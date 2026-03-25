import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "postgres"),
    "dbname": os.getenv("DB_NAME", "tradeview_strategy"),
    "password": os.getenv("DB_PASSWORD", "postgres123"),
    "port": os.getenv("DB_PORT", "5533"),
}

UPDATES = {
    "s041": """# Adaptive Ichimoku Nexus 自適應一目均衡表系統

這款指標是對經典「一目均衡表」(Ichimoku Kinko Hyo) 的現代升級。傳統系統使用固定週期 (9/26/52)，而本指標引入了「波動率自適應引擎」，根據市場壓力動態縮放轉頭線 (Tenkan)、基準線 (Kijun) 與先行帶 B (Span B)。

🔶 **核心增強 (ENHANCEMENTS)**
🔹 **自適應週期**：在波動率大時縮短週期（反應敏捷），在波動率小時拉長週期（過濾噪音）。
🔹 **8 因子匯流評分 (0-100)**：量化所有一目均衡維度（價格 vs 雲帶、TK 交叉、遲行帶確認等）加上成交量與動能。 score ≥ 80 為強訊號。
🔹 **動能脈衝引擎**：衡量 TK 擴散速度與未來雲帶旋轉方向，捕捉趨勢加速度。
🔹 **結構性止損**：支持以 Kumo 雲帶邊緣或基準線作為止損錨點，提供符合結構意義的風控。

🔶 **輔助工具**：包含雲帶突破 (Kumo Breakout) 檢測、雲帶回測 (Retest) 訊號，以及多時區 (MTF) 對齊面版。
""",
    "s042": """# Camarilla Pivot Levels [QuantumFlow] 卡瑪利拉樞紐位階

卡瑪利拉樞紐由 Nick Scott 於 1989 年開發，基於「均值回歸」原則。它利用前一天的數據計算出 8 個關鍵位階，對於開盤後的反轉或突破具有極高的參考價值。

🔶 **關鍵位階 (KEY LEVELS)**
- **S3 / R3**：主要反轉區（價格傾向在此反彈）。
- **S4 / R4**：突破區（若價格強勢穿透，預期趨勢將延續）。
- **S6 / R6**：極端位階（罕見，通常意味著強力的趨勢延伸或極度超買/超賣反轉）。
- **CP**：中心樞紐（前日收盤價）。

🔶 **特色功能**：支持 RTH (常規交易時段) 與 ETH (延長交易時段) 模式，內建價格標籤與警報，適合與成交量分布或訂單流結合成交。
""",
    "s043": """# Effort-Anchored VWAP 努力錨定成交量加權平均價

這款脚本根據「成交量激增」(Volume Spikes) 自動選擇 VWAP 的起始點。

🔶 **核心概念 (CONCEPTS)**
🔹 **努力錨定 (Effort-Anchoring)**：自動識別超過標準差的「努力 K 線」（代表市場有巨大分歧或共識），並將 VWAP 錨點重置於該位置。
🔹 **統計標準差帶**：相對於活動中的「努力錨點」繪製統計偏離路徑。
🔹 **視覺反饋**：在高成交量觸發重置的 K 線上進行高亮標註。

🔶 **交易建議**：當價格觸及 VWAP 帶時，通常代表回探了「大資金進場」的平均成本區，是潛在的買賣機會。
""",
    "s044": """# RTH Time based Gap Fill Statistic 交易時段缺口回補統計

這是一款量化分析工具，旨在追踪「開盤缺口」（前日 16:00 到今日 09:30 的價差）的回補行為。

🔶 **核心功能 (KEY FEATURES)**
- **滾動 126 天回溯**：動態捕捉近 6 個月的市場慣性。
- **細分時間桶 (Time Buckets)**：將回補時間分類為「開盤波動期」(09:30-09:59)、「第一小時」及「盤後回補」，幫助交易者判斷最高機率的時間窗口。
- **機率熱力圖**：表格以綠色/紅色展示回補機率與「未回補」(Runaway Gaps) 風險。

🔶 **數據洞察**：如果缺口在開盤前 30 分鐘未回補，隨後每個 15 分鐘段的回補機率將顯著下降。
""",
    "s045": """# IB Front Run Dashboard 初始餘額領先指標儀表板

本指標分析紐約常規交易時段 (RTH) 的前 45 分鐘（09:30–10:15），以在 10:15 收盤時識別高勝率的方向性設置。

🔶 **判斷標準**
在 10:15 分，指標會檢查價格與以下三個關鍵價位的關係：
1. **IB45 中點**：前 45 分鐘初始餘額的中點。
2. **OR 中點**：開盤區間的中心。
3. **10:00 開盤價**。

如果價格同時位於這三個水平之上或之下，則確認方向性偏差。儀表板會顯示近 20 天的勝率（Hit Rate），幫助交易者在 NQ 或 ES1! 等期貨市場中捕捉日內趨勢。
""",
    "s046": """# TTrades Currency Strength & Pair Ranker 貨幣強度與貨幣對排名器

這款指標靈感來自 TTrades 的貨幣配對方法，旨在幫助外匯交易者在市場開盤時快速識別最強與最弱的貨幣，而無需切換圖表。

🔶 **分析邏輯**
- **期貨與 DXY 整合**：利用外匯期貨數據與美元指數 (DXY) 判斷相對強弱。
- **最強 vs 最弱**：解釋 EUR/USD、USD/JPY 等貨幣對背後的聯動概念，找出最容易產生「擴張走勢」的組合，實現「買強賣弱」的結構化交易。
""",
    "s047": """# Pine Editor 字體更改指南 (非指標)

這不是一個指標，而是一份針對 Windows 環境下更改 TradingView Desktop 編輯器字體的圖文指南。

🔶 **為什麼需要？**
Windows 上的 Pine 編輯器默認使用 Consolas 字體，其粗體 (Bold) 效果在某些顯示器上過於纖細，且「1」與「l」等字符辨識度不足。

🔶 **操作步驟 (摘要)**
1. 下載並安裝 `opentype-feature-freezer`。
2. 將您喜歡的等寬字體（如 Source Code Pro）重命名為 `Menlo`（TradingView 識別的字體名）。
3. 安裝字體並重啟 TradingView。
這將顯著提升代碼的可讀性與視覺美感。
""",
    "s048": """# Breakout Volume Delta 突破成交量 Delta 指標

Breakout Volume Delta 利用低時區 (LTF) 的成交量數據來衡量突破的「強度」。它不僅看價格是否突破，還精確計算突破 K 線內部買方與賣方的參與程度。

🔶 **核心原理**
- **分拆式 K 線視覺化**：將突破 K 線的實體拆分為買方主導與賣方主導的比例，一眼看出參與度。
- **低時區 Delta 累加**：在當前 K 線內細分更小的時間週期，將收盤大於開盤的子 K 線計為買盤，反之計為賣盤。
- **突破過濾器**：可選設置，僅當突破方向的 Delta 佔比超過設定閾值（如 60%）時，才確認該突破有效。

🔶 **獨特性**：這不僅是價格行為，更是訂單流數據的視覺化，幫助交易者過濾那些「虛假」或「無力」的突破。
"""
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for serial_id, content in UPDATES.items():
        cur.execute("UPDATE tradingview_scripts SET description_full_zh = %s WHERE serial_id = %s", (content, serial_id))
    conn.commit()
    print(f"Updated {len(UPDATES)} scripts successfully")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
