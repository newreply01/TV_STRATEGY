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

def check_all():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("SELECT serial_id, title, image_url, is_web_done, slug FROM tradingview_scripts WHERE serial_id IS NOT NULL ORDER BY serial_id")
        rows = cur.fetchall()
        
        print(f"{'ID':<6} | {'Title':<30} | {'Image':<8} | {'Done':<5} | {'Slug'}")
        print("-" * 100)
        for r in rows:
            serial_id = r[0]
            title = r[1][:30]
            image = "OK" if r[2] else "MISSING"
            done = "YES" if r[3] else "NO"
            slug = r[4]
            print(f"{serial_id:<6} | {title:<30} | {image:<8} | {done:<5} | {slug}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_all()
