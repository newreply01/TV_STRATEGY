import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "dbname": "tradeview_strategy",
    "password": "postgres123",
    "port": "5433",
}

translations = {
    "lpnsjMbH-Clusters-Volume-Profile-LuxAlgo": "Clusters Volume Profile (分簇成交量分佈) 是由 LuxAlgo 開發的高級工具，利用 K-Means 聚類算法將歷史價格行為分類為不同的組，並為每個組生成獨立的成交量分佈圖。這有助於交易者識別特定價格區間內的成交量密集區，從而精確判斷支撐與壓力位。",
    "xZFb6Isb-Smart-Trader-Concentric-Candles-Aristot": "Smart Trader | 同心蠟燭與亞里斯多德擺線系列第 5 集，介紹了一種全新的圖表分析方法。此腳本結合了幾何 DNA 分析與市場結構識別，旨在揭露價格波動背後的數學規律，引導交易者發現隱藏的趨勢轉折點。",
    "WAsO68K0-MovingAverages": "MovingAverages (移動平均線庫) 是一個高效的算法集合，提供了 O(1) 複雜度的數值穩定移動平均線運算。它支援錨定點與分數長度（最高達 100k 根 K 線），是開發複雜策略時處理平滑數據的基礎工具庫。"
}

def update_translations():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        for slug, zh_text in translations.items():
            cur.execute(
                "UPDATE tradingview_scripts SET description_zh = %s WHERE slug = %s",
                (zh_text, slug)
            )
        
        conn.commit()
        cur.close()
        conn.close()
        print("Batch 2 translations (Screenshot items) updated successfully.")
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    update_translations()
