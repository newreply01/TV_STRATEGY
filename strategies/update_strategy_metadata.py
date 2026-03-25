import os
import re
import json
import argparse
import psycopg2
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from psycopg2.extras import RealDictCursor

# Load environment variables
# Try to load from current dir or webapp dir
load_dotenv()
if not os.getenv("DATABASE_URL"):
    load_dotenv("../webapp/.env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "postgres"),
    "dbname": os.getenv("DB_NAME", "tradeview_strategy"),
    "password": os.getenv("DB_PASSWORD", "postgres123"),
    "port": os.getenv("DB_PORT", "5433"),
}

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

GEMINI_PROMPT = """
你是一位專業的金融量化交易專家與語文專家。請將以下 TradingView 指標/策略的英文語法與描述，翻譯成高品質、具學術專業感且通順的繁體中文。

要求：
1. 使用專業術語（例如：回測、支撐壓力、成交量分佈、聚類算法等）。
2. 保持原文的邏輯結構，但語氣要像專業的財經專欄或學術論文。
3. 如果原文包含 Pine Script 變數名，請保留英文或在括號中註記。
4. 輸出必須為純繁體中文描述，不要包含 Markdown 以外的標記。
5. 確保翻譯後的內容適合放置在產品的「繁體中文」介紹頁面中。

原文：
{text}
"""

def get_high_quality_translation(text):
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY not found. Skipping AI translation.")
        return None
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(GEMINI_PROMPT.format(text=text))
        return response.text.strip()
    except Exception as e:
        print(f"Error during Gemini translation: {e}")
        return None

def fetch_tv_description(url):
    try:
        # Using subprocess to call curl as it seems more reliable for TradingView
        import subprocess
        cmd = ["curl", "-s", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            print(f"  Curl failed for {url}, code: {result.returncode}")
            return None
        
        html_content = result.stdout
        print(f"  HTML fetched ({len(html_content)} bytes). First 200 chars: {html_content[:200]}")
        
        # Find all script tags that might contain JSON
        script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.S)
        print(f"  Scanned {len(script_tags)} script tags")
        
        fetched_content = None
        for script_body in script_tags:
            script_body = script_body.strip()
            if not (script_body.startswith('{') or script_body.startswith('[')):
                continue
            
            try:
                data = json.loads(script_body)
                
                # Recursive search for 'description' and 'docs'
                def find_key(obj, key):
                    if isinstance(obj, dict):
                        if key in obj: return obj[key]
                        for v in obj.values():
                            item = find_key(v, key)
                            if item: return item
                    elif isinstance(obj, list):
                        for item in obj:
                            res = find_key(item, key)
                            if res: return res
                    return None
                
                desc = find_key(data, "description")
                docs = find_key(data, "docs")
                
                if desc or docs:
                    current_desc = docs if docs and len(docs) > len(desc or "") else desc
                    if current_desc and len(current_desc) > 50: # Avoid short snippets
                        fetched_content = current_desc
                        print(f"  Extracted content from JSON ({len(fetched_content)} chars)")
                        break
            except:
                continue
        
        if fetched_content:
            return fetched_content
        else:
            print("  Warning: No suitable description JSON found in any script tag.")
            return None
    except Exception as e:
        print(f"Error fetching TV description: {e}")
        return None

def update_thumbnail(slug):
    # Hardcoded logic similar to update_thumbnails.ts for now, 
    # but can be expanded to download real images.
    prefix = slug.split('-')[0]
    return prefix

def process_script(conn, script_row, force=False):
    slug = script_row['slug']
    serial_id = script_row['serial_id']
    url = script_row['url']
    
    print(f"Processing {serial_id}: {slug}...")
    
    updates = {}
    
    # 1. Sync Full Description (ORIGIN)
    full_desc = script_row.get('description_full')
    if not full_desc or force:
        print(f"  Fetching latest description from TradingView...")
        fetched_desc = fetch_tv_description(url)
        if fetched_desc:
            full_desc = fetched_desc
            updates['description_full'] = full_desc
            print(f"  Synced ORIGIN description ({len(full_desc)} chars)")
    
    # 2. High Quality Translation (繁體中文)
    if full_desc and (not script_row.get('description_full_zh') or force):
        print(f"  Generating High Quality translation via Gemini...")
        zh_desc = get_high_quality_translation(full_desc)
        if zh_desc:
            updates['description_full_zh'] = zh_desc
            # Also update the short description if it's missing
            if not script_row.get('description_zh'):
                updates['description_zh'] = zh_desc[:200] + "..."
            print(f"  Generated zh-TW translation ({len(zh_desc)} chars)")
    
    # 3. Thumbnail Update
    if not script_row.get('image_url') or script_row['image_url'] == 'placeholder':
        new_img = update_thumbnail(slug)
        if new_img:
            updates['image_url'] = new_img
            print(f"  Updated image_url to {new_img}")

    if updates:
        cur = conn.cursor()
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        params = list(updates.values()) + [slug]
        cur.execute(f"UPDATE tradingview_scripts SET {set_clause} WHERE slug = %s", params)
        conn.commit()
        print(f"  Successfully updated {len(updates)} fields.")
    else:
        print("  No updates needed.")

def main():
    parser = argparse.ArgumentParser(description="Update strategy metadata (Content, Translation, Thumbnails)")
    parser.add_argument("--serial", help="Serial ID to update (e.g. S002)")
    parser.add_argument("--all", action="store_true", help="Update all scripts with a serial_id")
    parser.add_argument("--force", action="store_true", help="Force refresh even if content exists")
    args = parser.parse_args()
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if args.serial:
            # Flexible matching for serial_id (e.g. S002, s002, 002)
            search_id = args.serial.lower()
            if search_id.startswith('s'):
                search_id_alt = search_id[1:]
            else:
                search_id_alt = 's' + search_id
            
            cur.execute("SELECT * FROM tradingview_scripts WHERE LOWER(serial_id) IN (%s, %s)", (search_id, search_id_alt))
            scripts = cur.fetchall()
        elif args.all:
            cur.execute("SELECT * FROM tradingview_scripts WHERE serial_id IS NOT NULL ORDER BY serial_id")
            scripts = cur.fetchall()
        else:
            parser.print_help()
            return

        print(f"Found {len(scripts)} scripts to process.")
        for s in scripts:
            process_script(conn, s, force=args.force)
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    main()
