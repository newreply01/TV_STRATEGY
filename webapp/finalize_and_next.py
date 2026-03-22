import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433')
    cur = conn.cursor()
    
    # 1. Finalize S003 (Marked as 100% done)
    # Note: Using single quotes for the query string to allow double quotes for camelCase columns
    cur.execute('UPDATE tradingview_scripts SET is_implemented = true, "isWebDone" = true, "isScriptDone" = true WHERE serial_id = \'003\'')
    
    # 2. Identify S004 (Highest Boosts, not implemented)
    cur.execute("SELECT serial_id, title, slug, url, boosts_count FROM tradingview_scripts WHERE is_implemented = false ORDER BY boosts_count DESC LIMIT 1")
    row = cur.fetchone()
    
    conn.commit()
    
    print("SUCCESS: Strategy 003 marked as DONE.")
    if row:
        print(f"NEXT_STRATEGY|{row[0]}|{row[1]}|{row[2]}|{row[3]}|{row[4]}")
    else:
        print("NO_PENDING_STRATEGY")
        
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
