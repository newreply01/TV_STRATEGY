import psycopg2
import json
import os
from datetime import datetime

# Local DB connection
LOCAL_DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "postgres123",
    "dbname": "tradeview_strategy"
}

def sync():
    # 本專案特定的策略同步進度
    data_to_sync = [
        {"dataset": "TradingView_Scripts", "last_sync_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": "done"},
        {"dataset": "Strategy_001_Data", "last_sync_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": "done"},
        {"dataset": "Strategy_002_Data", "last_sync_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": "done"},
    ]
    
    try:
        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        cur = conn.cursor()
        
        print("Connected to local database.")
        
        for row in data_to_sync:
            cur.execute("""
                INSERT INTO fm_sync_progress (dataset, last_sync_date, status, check_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (dataset) DO UPDATE 
                SET last_sync_date = EXCLUDED.last_sync_date,
                    status = EXCLUDED.status,
                    check_at = NOW();
            """, (row['dataset'], row['last_sync_date'], row['status']))
            
        conn.commit()
        print(f"Successfully synced {len(data_to_sync)} rows to fm_sync_progress.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    sync()
