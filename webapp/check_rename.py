import psycopg2
conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433')
cur = conn.cursor()
cur.execute(" SELECT serial_id title FROM tradingview_scripts WHERE serial_id = 002 )
