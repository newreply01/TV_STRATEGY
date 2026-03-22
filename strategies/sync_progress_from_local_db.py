import psycopg2
from datetime import datetime

# Database configurations
CONFIG_SRC = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "postgres123",
    "dbname": "stock_screener"
}

CONFIG_DEST = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "postgres123",
    "dbname": "tradeview_strategy"
}

def sync():
    try:
        # Connect to source
        conn_src = psycopg2.connect(**CONFIG_SRC)
        cur_src = conn_src.cursor()
        
        # Fetch data
        cur_src.execute("SELECT dataset, last_sync_date, status, check_at FROM fm_sync_progress")
        rows = cur_src.fetchall()
        print(f"Fetched {len(rows)} rows from stock_screener.fm_sync_progress")
        
        # Connect to destination
        conn_dest = psycopg2.connect(**CONFIG_DEST)
        cur_dest = conn_dest.cursor()
        
        # Insert or Update
        for row in rows:
            dataset, last_sync_date, status, check_at = row
            cur_dest.execute("""
                INSERT INTO fm_sync_progress (dataset, last_sync_date, status, check_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (dataset) DO UPDATE 
                SET last_sync_date = EXCLUDED.last_sync_date,
                    status = EXCLUDED.status,
                    check_at = EXCLUDED.check_at;
            """, (dataset, last_sync_date, status, check_at))
            
        conn_dest.commit()
        print(f"Successfully synced {len(rows)} rows to tradeview_strategy.fm_sync_progress")
        
        cur_src.close()
        conn_src.close()
        cur_dest.close()
        conn_dest.close()
    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    sync()
