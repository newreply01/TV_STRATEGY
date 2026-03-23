import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "dbname": "tradeview_strategy",
    "password": "postgres123",
    "port": "5533",
}

def check_swing_profile():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT slug, title, description_full FROM tradingview_scripts WHERE slug = 'gFlv7t7R-Swing-Profile-BigBeluga'")
        row = cur.fetchone()
        if row:
            print(f"Slug: {row[0]}")
            print(f"Title: {row[1]}")
            print("\n--- Description Full ---")
            print(row[2])
        else:
            print("Script not found.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_swing_profile()
