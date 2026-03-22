import asyncio
import os
import sys
import re
import requests
from datetime import datetime
from playwright.async_api import async_playwright
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "postgres"),
    "dbname": os.getenv("DB_NAME", "tradeview_strategy"),
    "password": os.getenv("DB_PASSWORD", "postgres123"),
    "port": os.getenv("DB_PORT", "5433"),
}

URLS = {
    "popular": "https://tw.tradingview.com/scripts/",
    "editors_picks": "https://tw.tradingview.com/scripts/editors-picks/"
}

PUBLIC_DIR = "/home/xg/tradeview-strategy/webapp/public/scripts"

async def auto_scroll(page):
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 100;
                let timer = setInterval(() => {
                    let scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= scrollHeight || totalHeight > 3000){
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    """)

async def scrape_detail(browser, url, slug):
    print(f"  -> Scraping detail: {url}")
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(4)
        
        # Extract full description, Pine Script and Stats
        detail_data = await page.evaluate("""
            () => {
                const descEl = document.querySelector('div.js-script-description') || document.querySelector('div[class*="description"]');
                const images = descEl ? Array.from(descEl.querySelectorAll('img')).map(img => img.src) : [];
                
                // Extract metrics (Boosts and Comments)
                const boostEl = document.querySelector('span[class*="boosts-count"], button[class*="boost"] span');
                const commentEl = document.querySelector('span[class*="comments-count"], button[class*="comment"] span');
                
                const parseCount = (txt) => {
                   if (!txt) return 0;
                   txt = txt.trim().toLowerCase();
                   if (txt.includes('k')) return parseFloat(txt.replace('k', '')) * 1000;
                   return parseInt(txt.replace(/[^0-9]/g, '')) || 0;
                };

                return {
                    description_full: descEl ? descEl.innerText.trim() : '',
                    images: images,
                    boosts_count: boostEl ? parseCount(boostEl.innerText) : 0,
                    comments_count: commentEl ? parseCount(commentEl.innerText) : 0
                };
            }
        """)
        
        # Extract code tab
        pine_script = ""
        try:
            code_tab = page.get_by_text(re.compile(r"原始碼|Source Code")).first
            if await code_tab.count() > 0:
                await code_tab.click()
                await asyncio.sleep(3)
                pine_script = await page.evaluate("""
                    () => {
                        const codeEl = document.querySelector('div[class*="codeContainer"]');
                        return codeEl ? codeEl.innerText.trim() : '';
                    }
                """)
        except Exception as e:
            print(f"    Error clicking code tab for {slug}: {e}")

        # Download images
        local_images = []
        script_dir = os.path.join(PUBLIC_DIR, slug)
        if not os.path.exists(script_dir):
            os.makedirs(script_dir)
            
        for i, img_url in enumerate(detail_data['images']):
            try:
                # Sanitize extension
                ext_match = re.search(r'\.(png|jpg|jpeg|gif|webp|svg)(\?|$)', img_url, re.I)
                ext = ext_match.group(1) if ext_match else 'png'
                
                response = requests.get(img_url, timeout=15)
                if response.status_code == 200:
                    filename = f"img_{i}.{ext}"
                    filepath = os.path.join(script_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    local_images.append(f"/scripts/{slug}/{filename}")
                else:
                    print(f"    Failed to download image {img_url}: Status {response.status_code}")
            except Exception as e:
                print(f"    Failed to download image {img_url}: {e}")

        detail_data['pine_script'] = pine_script
        detail_data['local_images'] = local_images
        return detail_data
    except Exception as e:
        print(f"    Error scraping {url}: {e}")
        return None
    finally:
        await page.close()

async def scrape_scripts(browser, url, source_type):
    print(f"[{source_type}] Navigating to {url}...")
    page = await browser.new_page()
    await page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    })
    
    try:
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await auto_scroll(page)
        await asyncio.sleep(2)
        
        scripts = await page.evaluate(f"""
            () => {{
                const items = Array.from(document.querySelectorAll('article'));
                return items.map(item => {{
                    const titleEl = item.querySelector('a[class*="title"]');
                    const authorEl = item.querySelector('a[aria-label*="profile"], a[class*="user-link"], span[class*="author"]');
                    const imgEl = item.querySelector('img');
                    const descEl = item.querySelector('div[class*="description"] p, a[class*="paragraph"]');
                    
                    const link = titleEl ? titleEl.getAttribute('href') : '';
                    
                    return {{
                        title: titleEl ? titleEl.innerText.trim() : '',
                        author: authorEl ? authorEl.innerText.trim() : 'Unknown',
                        url: link ? (link.startsWith('http') ? link : `https://tw.tradingview.com${{link}}`) : '',
                        slug: link ? link.split('/').filter(Boolean).pop() : '',
                        image_url: imgEl ? imgEl.src : '',
                        description_en: descEl ? descEl.innerText.trim() : '',
                        source_type: '{source_type}'
                    }};
                }}).filter(s => s.title && s.slug);
            }}
        """)
        
        print(f"[{source_type}] Found {len(scripts)} scripts. Fetching details & saving incrementally...")
        
        # Fetch details and save each script (Phase 2)
        detailed_scripts = []
        count = 0
        for s in scripts:
            detail = await scrape_detail(browser, s['url'], s['slug'])
            if detail:
                s.update(detail)
            save_to_db([s]) # Save individual script
            detailed_scripts.append(s)
            count += 1
            print(f"[{source_type}] ({count}/{len(scripts)}) Saved: {s['slug']}")
            
        return detailed_scripts
    except Exception as e:
        print(f"[{source_type}] Error: {e}")
        return []
    finally:
        await page.close()

def save_to_db(scripts):
    if not scripts:
        return
        
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    query = """
        INSERT INTO tradingview_scripts (
            title, author, url, slug, image_url, description_en, source_type, 
            description_full, pine_script, local_images, boosts_count, comments_count, 
            last_synced_at, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (slug) DO UPDATE SET
            title = EXCLUDED.title,
            author = EXCLUDED.author,
            url = EXCLUDED.url,
            image_url = EXCLUDED.image_url,
            description_en = EXCLUDED.description_en,
            description_full = EXCLUDED.description_full,
            pine_script = EXCLUDED.pine_script,
            local_images = EXCLUDED.local_images,
            boosts_count = EXCLUDED.boosts_count,
            comments_count = EXCLUDED.comments_count,
            last_synced_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
    """
    
    for s in scripts:
        try:
            cur.execute(query, (
                s['title'], s['author'], s['url'], s['slug'], 
                s.get('image_url'), s.get('description_en'), s.get('source_type'),
                s.get('description_full'), s.get('pine_script'), s.get('local_images'),
                s.get('boosts_count', 0), s.get('comments_count', 0)
            ))
        except Exception as e:
            print(f"Error saving {s['slug']}: {e}")
            conn.rollback()
            
    # Update sync progress
    cur.execute("""
        INSERT INTO fm_sync_progress (dataset, last_sync_date)
        VALUES ('TradingView_Scripts', CURRENT_TIMESTAMP)
        ON CONFLICT (dataset) DO UPDATE SET last_sync_date = EXCLUDED.last_sync_date
    """)
    
    conn.commit() # Commit everything at once
    cur.close()
    conn.close()
    
    # Trigger Automated AI Translation
    try:
        from translate_scripts import translate_all_pending
        translate_all_pending()
    except Exception as e:
        print(f"Translation trigger failed: {e}")

def log_status(service_name, status, message=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO system_status (service_name, status, message, check_time)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """, (service_name, status, message))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to log status: {e}")

async def main():
    log_status("tradingview_crawler", "RUNNING", "Started scraping popular and editors picks")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            
            popular = await scrape_scripts(browser, URLS["popular"], "popular")
            editors = await scrape_scripts(browser, URLS["editors_picks"], "editors_picks")
            
            save_to_db(popular)
            save_to_db(editors)
            
            await browser.close()
            log_status("tradingview_crawler", "SUCCESS", f"Successfully scraped {len(popular) + len(editors)} scripts")
        except Exception as e:
            log_status("tradingview_crawler", "FAILED", str(e))
            raise e

if __name__ == "__main__":
    asyncio.run(main())
