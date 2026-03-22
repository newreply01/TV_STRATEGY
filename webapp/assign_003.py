import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433')
    cur = conn.cursor()
    cur.execute("UPDATE tradingview_scripts SET serial_id = '003' WHERE slug = 'vXui7vrm-Market-Structure-Dashboard-Flux-Charts'")
    conn.commit()
    print("SUCCESS: Serial ID 003 assigned.")
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
