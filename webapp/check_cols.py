import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433')
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'tradingview_scripts'")
    cols = [r[0] for r in cur.fetchall()]
    print(f"COLUMNS|{','.join(cols)}")
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
