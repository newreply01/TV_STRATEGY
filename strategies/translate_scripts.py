import os
import psycopg2
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# 使用說明：
# 此腳本使用 deep-translator (Google Translate Web API) 進行自動翻譯
# 不需要 API Key，適合自動化轉譯流程。

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "dbname": "tradeview_strategy",
    "password": "postgres123",
    "port": "5433",
}

def get_free_translation(text_en):
    """
    使用 GoogleTranslator 進行免費翻譯。
    """
    try:
        # 使用 Google 翻譯，目標語言為繁體中文 (zh-TW)
        translated = GoogleTranslator(source='auto', target='zh-TW').translate(text_en)
        return translated
    except Exception as e:
        print(f"翻譯失敗: {e}")
        return None

def translate_all_pending():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 找出尚未轉譯且有英文描述的腳本
        cur.execute("SELECT slug, title, description_en FROM tradingview_scripts WHERE (description_zh IS NULL OR description_zh = '') AND description_en IS NOT NULL LIMIT 10")
        rows = cur.fetchall()
        
        if not rows:
            print("目前沒有待轉譯的項目。")
            return

        print(f"發現 {len(rows)} 個待轉譯項目 (使用免費轉譯引擎)...")
        
        for slug, title, desc_en in rows:
            print(f"正在自動轉譯: {title}...")
            # 由於描述可能很長，deep-translator 建議分段或限制長度，或者是直接嘗試
            # 我們這裡直接嘗試，如果太長可能需要處理
            zh_text = get_free_translation(desc_en)
            
            if zh_text:
                cur.execute("UPDATE tradingview_scripts SET description_zh = %s WHERE slug = %s", (zh_text, slug))
                print(f"成功完成自動轉譯: {title}")
                conn.commit()
            else:
                print(f"轉譯跳過: {title}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"轉譯過程發生資料庫錯誤: {e}")

if __name__ == "__main__":
    translate_all_pending()
