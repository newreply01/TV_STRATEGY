import psycopg2
try:
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433')
    cur = conn.cursor()
    cur.execute("""
        UPDATE tradingview_scripts 
        SET title = 'Clusters Volume Profile',
            slug = 'lpnsjMbH-Clusters-Volume-Profile-LuxAlgo',
            url = 'https://www.tradingview.com/script/lpnsjMbH-Clusters-Volume-Profile-LuxAlgo/'
        WHERE serial_id = '002'
    """)
    cur.execute("""
        UPDATE tradingview_scripts 
        SET title = 'Omni-Flow Consensus'
        WHERE serial_id = '001' AND title IS NULL
    """)
    conn.commit()
    print("SUCCESS: Metadata updated.")
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
