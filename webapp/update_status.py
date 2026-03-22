import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433')
    cur = conn.cursor()
    cur.execute(" UPDATE tradingview_scripts SET is_web_done = true is_script_done = true WHERE serial_id IN 001 002 )
