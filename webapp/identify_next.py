import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5533')
    cur = conn.cursor()
    cur.execute("SELECT serial_id, title, slug, url, boosts_count FROM tradingview_scripts WHERE is_implemented = false ORDER BY boosts_count DESC LIMIT 1")
    row = cur.fetchone()
    if row:
        print(f"NEXT_STRATEGY|{row[0]}|{row[1]}|{row[2]}|{row[3]}|{row[4]}")
    else:
        print("NO_PENDING_STRATEGY")
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
