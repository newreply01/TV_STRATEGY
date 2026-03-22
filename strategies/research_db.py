import psycopg2

def research():
    configs = [
        {"dbname": "tradeview_strategy", "port": "5433"},
        {"dbname": "stock_screener", "port": "5433"}
    ]
    
    for config in configs:
        print(f"--- Researching DB: {config['dbname']} ---")
        try:
            conn = psycopg2.connect(
                host="localhost",
                user="postgres",
                password="postgres123",
                dbname=config['dbname'],
                port=config['port']
            )
            cur = conn.cursor()
            
            if config['dbname'] == "tradeview_strategy":
                # Fetch full script
                cur.execute("SELECT pine_script FROM tradingview_scripts WHERE title LIKE '%Omni-Flow Consensus%' LIMIT 1")
                res = cur.fetchone()
                if res:
                    print("--- OMNI-FLOW PINE SCRIPT (First 500 chars) ---")
                    print(res[0][:500])
                    # Save full script to a file for analysis
                    with open("omni_flow_logic.pine", "w", encoding="utf-8") as f:
                        f.write(res[0])
            
            if config['dbname'] == "stock_screener":
                # Check for realtime_ticks
                cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'realtime_ticks' AND table_schema = 'public'")
                if cur.fetchone()[0] > 0:
                    print("--- realtime_ticks FOUND ---")
                    cur.execute("SELECT count(*) FROM realtime_ticks WHERE symbol = '2330'")
                    count = cur.fetchone()[0]
                    print(f"Records for 2330 in realtime_ticks: {count}")
                    if count > 0:
                        cur.execute("SELECT trade_time, open_price, high_price, low_price, price, volume FROM realtime_ticks WHERE symbol = '2330' ORDER BY trade_time DESC LIMIT 5")
                        rows = cur.fetchall()
                        for row in rows:
                            print(f"Sample 2330 1m Data: {row}")
                else:
                    print("!!! realtime_ticks NOT FOUND !!! Search all schemas again...")
                    cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = 'realtime_ticks'")
                    matches = cur.fetchall()
                    print(f"Found in schemas: {matches}")
                
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error connecting to {config['dbname']}: {e}")

if __name__ == "__main__":
    research()
