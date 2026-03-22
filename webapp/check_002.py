import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433')
    cur = conn.cursor()
    cur.execute("SELECT serial_id, title, slug, url, is_web_done, is_script_done FROM tradingview_scripts WHERE serial_id = '002'")
    row = cur.fetchone()
    if row:
        print(f"Serial ID: {row[0]}")
        print(f"Title: {row[1]}")
        print(f"Slug: {row[2]}")
        print(f"URL: {row[3]}")
        print(f"Web Done: {row[4]}")
        print(f"Script Done: {row[5]}")
    else:
        print("Strategy 002 not found!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
