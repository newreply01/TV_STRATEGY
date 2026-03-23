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

def check_one_script():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Fetch one script that has both en and full
        cur.execute("SELECT slug, title, description_en, description_full FROM tradingview_scripts WHERE description_full IS NOT NULL AND description_full != '' LIMIT 1")
        row = cur.fetchone()
        if row:
            slug, title, desc_en, desc_full = row
            print(f"Slug: {slug}")
            print(f"Title: {title}")
            print(f"Desc EN length: {len(desc_en) if desc_en else 0}")
            print(f"Desc FULL length: {len(desc_full) if desc_full else 0}")
            print("\n--- Desc EN ---")
            print(desc_en[:500] + "..." if desc_en else "None")
            print("\n--- Desc FULL ---")
            print(desc_full[:500] + "..." if desc_full else "None")
        else:
            # Try to find any record
            cur.execute("SELECT slug, title, description_en, description_full FROM tradingview_scripts LIMIT 1")
            row = cur.fetchone()
            if row:
                slug, title, desc_en, desc_full = row
                print(f"No FULL description found. Sample record: {slug}")
                print(f"Desc EN length: {len(desc_en) if desc_en else 0}")
                print(f"Desc FULL is: {desc_full}")
            else:
                print("Table is empty.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_one_script()
