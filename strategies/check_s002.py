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
    cur.execute("SELECT serial_id, description_full_zh FROM tradingview_scripts WHERE serial_id = '002'")
    row = cur.fetchone()
    if row:
        print(f"ID: {row[0]}")
        print(f"Content:\n{row[1]}")
    else:
        print("s002 not found")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
