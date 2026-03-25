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

def promote_all():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Set is_web_done = true and is_implemented = true for all strategies with a serial_id
        cur.execute("""
            UPDATE tradingview_scripts 
            SET is_web_done = true, 
                is_implemented = true 
            WHERE serial_id IS NOT NULL 
              AND serial_id != ''
        """)
        
        count = cur.rowcount
        conn.commit()
        print(f"Successfully promoted {count} strategies to 'Completed' (is_web_done = true)")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    promote_all()
