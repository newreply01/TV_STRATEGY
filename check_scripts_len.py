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

def check_scripts():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT slug, title, length(description_en) as len_en, length(description_full) as len_full FROM tradingview_scripts ORDER BY len_full ASC LIMIT 20")
        rows = cur.fetchall()
        print("--- Shortest Full Descriptions ---")
        for row in rows:
            print(f"Slug: {row[0]}, Len EN: {row[2]}, Len FULL: {row[3]}, Title: {row[1]}")
            
        print("\n--- 'Swing Profile' Scripts ---")
        cur.execute("SELECT slug, title, length(description_full) FROM tradingview_scripts WHERE title ILIKE '%Swing Profile%'")
        rows = cur.fetchall()
        for row in rows:
            print(f"Slug: {row[0]}, Len FULL: {row[2]}, Title: {row[1]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_scripts()
