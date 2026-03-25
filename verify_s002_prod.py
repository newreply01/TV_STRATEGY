import psycopg2

SUPABASE_URL = "postgresql://postgres.cktbfzaudujxgjmmwfcl:R88ItLq7cVREvofJ@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres"

def verify_s002():
    try:
        conn = psycopg2.connect(SUPABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT serial_id, slug, description_full_zh, description_zh FROM tradingview_scripts WHERE serial_id = '002'")
        row = cur.fetchone()
        if row:
            print(f"Serial: {row[0]}")
            print(f"Slug: {row[1]}")
            desc_full_zh = row[2] or ""
            desc_zh = row[3] or ""
            print(f"description_full_zh Len: {len(desc_full_zh)}")
            print(f"description_zh Len: {len(desc_zh)}")
            if len(desc_full_zh) > 0:
                print("First 100 chars of full_zh:")
                print(desc_full_zh[:100])
        else:
            print("S002 not found!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_s002()
