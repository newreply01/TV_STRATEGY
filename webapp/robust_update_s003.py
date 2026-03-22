import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433', connect_timeout=5)
    cur = conn.cursor()
    
    # Try both naming conventions
    try:
        cur.execute("UPDATE tradingview_scripts SET is_implemented = true, \"isWebDone\" = true, \"isScriptDone\" = true WHERE serial_id = '003'")
        print("SUCCESS: Updated using \"isWebDone\" (camelCase)")
    except Exception:
        conn.rollback()
        cur.execute("UPDATE tradingview_scripts SET is_implemented = true, is_web_done = true, is_script_done = true WHERE serial_id = '003'")
        print("SUCCESS: Updated using is_web_done (snake_case)")
        
    conn.commit()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
