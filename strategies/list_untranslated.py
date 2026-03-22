import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "dbname": "tradeview_strategy",
    "password": "postgres123",
    "port": "5433",
}

def list_untranslated():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT slug, title, description_en FROM tradingview_scripts WHERE title LIKE '%Clusters Volume Profile%' OR title LIKE '%MovingAverages%' OR title LIKE '%Smart Trader%'")
        rows = cur.fetchall()
        for row in rows:
            print(f"Slug: {row[0]}")
            print(f"Title: {row[1]}")
            print(f"Desc: {row[2][:100]}...")
            print("-" * 20)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_untranslated()
