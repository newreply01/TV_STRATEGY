import psycopg2
import sys

def update_db():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5533/tradeview_db")
        cur = conn.cursor()
        
        # Update S001
        cur.execute("UPDATE \"Script\" SET \"imageUrl\" = '3ONFG3bJ' WHERE slug LIKE '%Omni-Flow%';")
        print(f"S001 updated: {cur.rowcount} rows")
        
        # Update S002
        cur.execute("UPDATE \"Script\" SET \"imageUrl\" = 'lpnsjMbH' WHERE slug LIKE '%Clusters%';")
        print(f"S002 updated: {cur.rowcount} rows")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Local DB Update Success!")
    except Exception as e:
        print(f"Error updating local DB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_db()
