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

def debug_s043():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check by serial_id
        print("--- Checking by serial_id 's043' ---")
        cur.execute("SELECT serial_id, description_full_zh, image_url, slug, url FROM tradingview_scripts WHERE serial_id = 's043'")
        row = cur.fetchone()
        if row:
            print(f"Serial ID: {row[0]}")
            print(f"ZH Length: {len(row[1]) if row[1] else 0}")
            print(f"Image URL: {row[2]}")
            print(f"Slug: {row[3]}")
            print(f"URL: {row[4]}")
        else:
            print("s043 not found by serial_id")
            
        # Check by slug
        print("\n--- Checking by slug 'cUIRGJ41-Effort-Anchored-VWAP' ---")
        cur.execute("SELECT serial_id, description_full_zh, image_url FROM tradingview_scripts WHERE tradingview_url LIKE '%cUIRGJ41-Effort-Anchored-VWAP%'")
        row = cur.fetchone()
        if row:
            print(f"Serial ID: {row[0]}")
            print(f"ZH Length: {len(row[1]) if row[1] else 0}")
            print(f"Image URL: {row[2]}")
        else:
            print("Slug not found in tradingview_url")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_s043()
