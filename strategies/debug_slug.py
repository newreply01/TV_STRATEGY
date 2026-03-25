import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "postgres"),
    "dbname": os.getenv("DB_NAME", "tradeview_strategy"),
    "password": os.getenv("DB_PASSWORD", "postgres123"),
    "port": os.getenv("DB_PORT", "5533"),
}

def debug_slug(slug):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print(f"--- Checking by slug '{slug}' ---")
        cur.execute("SELECT serial_id, description_full_zh, image_url, slug, description_zh, is_web_done, description_full FROM tradingview_scripts WHERE slug = %s", (slug,))
        row = cur.fetchone()
        if row:
            print(f"Serial ID: {row[0]}")
            print(f"ZH Full Content:\n{row[1]}")
            print(f"EN Full Length: {len(row[6]) if row[6] else 0}")
        else:
            print(f"Slug '{slug}' not found")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_slug('AA13FB1d-IB-Front-Run-Dashboard')
