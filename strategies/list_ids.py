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

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT serial_id FROM tradingview_scripts ORDER BY serial_id LIMIT 50")
    rows = cur.fetchall()
    for row in rows:
        print(row[0])
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
