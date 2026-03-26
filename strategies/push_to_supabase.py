import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# DATABASE URLS
LOCAL_DB_URL = "postgresql://postgres:postgres123@localhost:5533/tradeview_strategy"
SUPABASE_DB_URL = "postgresql://postgres.cktbfzaudujxgjmmwfcl:R88ItLq7cVREvofJ@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require"

def sync_to_supabase():
    try:
        # 1. Connect to Local DB
        print("Connecting to Local DB...")
        conn_local = psycopg2.connect(LOCAL_DB_URL)
        cur_local = conn_local.cursor(cursor_factory=RealDictCursor)
        
        # 2. Fetch all scripts
        cur_local.execute("SELECT * FROM tradingview_scripts")
        scripts = cur_local.fetchall()
        print(f"Found {len(scripts)} scripts in local DB.")
        
        # 3. Connect to Supabase
        print("Connecting to Supabase...")
        conn_supabase = psycopg2.connect(SUPABASE_DB_URL)
        cur_supabase = conn_supabase.cursor()
        
        # 4. Sync each script
        count = 0
        for script in scripts:
            # Fields: serial_id, description_zh, description_full_zh, local_images, is_implemented, is_web_done, image_url, last_synced_at
            # We use slug as the unique qualifier
            query = """
                UPDATE tradingview_scripts
                SET 
                    serial_id = %s,
                    description_zh = %s,
                    description_full_zh = %s,
                    local_images = %s,
                    is_implemented = %s,
                    is_web_done = %s,
                    image_url = %s,
                    last_synced_at = %s,
                    title = %s,
                    author = %s
                WHERE slug = %s
            """
            
            cur_supabase.execute(query, (
                script['serial_id'],
                script['description_zh'],
                script['description_full_zh'],
                script['local_images'],
                script['is_implemented'],
                script['is_web_done'],
                script['image_url'],
                script['last_synced_at'],
                script['title'],
                script['author'],
                script['slug']
            ))
            count += 1
            if count % 10 == 0:
                print(f"Synced {count}/{len(scripts)}...")
                
        conn_supabase.commit()
        print(f"SUCCESS: Successfully synced {count} scripts to Supabase.")
        
        cur_local.close()
        conn_local.close()
        cur_supabase.close()
        conn_supabase.close()
        
    except Exception as e:
        print(f"CRITICAL ERROR during sync: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_to_supabase()
