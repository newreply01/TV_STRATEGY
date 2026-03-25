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

def demote_strategies():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Demote S003 and any s006-s048 items back to is_web_done = false
        # Note: 001 and 002 stay as is_web_done = true
        cur.execute("""
            UPDATE tradingview_scripts 
            SET is_web_done = false 
            WHERE serial_id NOT IN ('001', '002')
              AND serial_id IS NOT NULL 
              AND serial_id != ''
        """)
        
        count = cur.rowcount
        conn.commit()
        print(f"Successfully demoted {count} strategies back to 'Development Center' (is_web_done = false)")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    demote_strategies()
