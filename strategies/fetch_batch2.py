import psycopg2
from psycopg2.extras import RealDictCursor
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

ids = ['s041', 's042', 's043', 's044', 's045', 's046', 's047', 's048']
OUTPUT_FILE = "batch5_descriptions.txt"

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for serial_id in ids:
            cur.execute("SELECT serial_id, title, description_full FROM tradingview_scripts WHERE serial_id = %s", (serial_id,))
            r = cur.fetchone()
            if r:
                f.write(f"--- {r['serial_id']}: {r['title']} ---\n")
                f.write(r['description_full'] or "")
                f.write("\n\n" + "="*50 + "\n\n")
    print(f"Saved {len(ids)} descriptions to {OUTPUT_FILE}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
