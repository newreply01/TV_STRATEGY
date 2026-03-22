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
    "Ax8kwFhb-FLOOP-Pro": "FLOOP Pro (固定回顧期同比) 是一個先進的技術指標，旨在透過比較當前價格行為與歷史同期表現來識別趨勢強度與反轉點。它利用固定窗口分析來消除季節性噪音，並提供清楚的進出場視覺化訊號。",
    "3ONFG3bJ-Omni-Flow-Consensus-LuxAlgo": "Omni-Flow Consensus (全方位流量共識) 是由 LuxAlgo 開發的高級指標，結合了多種成交量與價格流動演算法，以提供市場共識的單一視覺化呈現。它能自動過濾市場噪音並標註關鍵的流動性區域，協助交易者把握大資金流向。",
    "TY43MHZi-NY15m-ORB-with-a-fixed-SL-TP-Nasdaq": "NY15m ORB (紐約 15 分鐘開盤區間突破) 策略專為 Nasdaq 交易設計。它自動標註紐約市場開盤後前 15 分鐘的高低點，並在突破發生時提供具備固定止損與止盈目標的交易訊號，適合追求開盤波動性的交易者。",
    "kJ0nOczA-Inversion-Fair-Value-Gaps-IFVG-ChartPrime": "Inversion Fair Value Gaps (反向公允價值缺口, IFVG) 指標由 ChartPrime 提供，致力於識別市場失衡區域及其後續的反向支撐/壓力效應。此指標能精確標註 IFVG 區域，幫助交易者在區間回測時尋找高品質的進場機會。",
    "2ZouHl3Q-RSI-BUY-SELL-Pro-KN": "RSI BUY SELL Pro KN 是一個強化的相對強弱指數工具，優化了傳統 RSI 的超買/超賣訊號。它引入了動態門檻與過濾邏輯，旨在捕捉趨勢重啟時的買賣點，並有效減少震盪行情中的假訊號。"
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
        print("Batch 1 translations updated successfully.")
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    update_translations()
