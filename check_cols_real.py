import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5533')
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'tradingview_scripts'")
    rows = cur.fetchall()
    with open('webapp/db_columns_real.txt', 'w') as f:
        for r in rows:
            f.write(r[0] + '\n')
    conn.close()
    print("Columns exported successfully.")
except Exception as e:
    print(f"ERROR: {e}")
