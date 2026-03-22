import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433')
    cur = conn.cursor()
    cur.execute("UPDATE tradingview_scripts SET title = 'Clusters Volume Profile' WHERE serial_id = '002'")
    conn.commit()
    print('SUCCESS: Updated Strategy 002 title.')
    conn.close()
except Exception as e:
    print(f'ERROR: {e}')
