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
    "s031": """# Market Microstructure Analytics 市場微觀結構分析指標

這款指標將機構級別的市場微觀結構分析帶入一般交易者的圖表。它不依賴佣金或費用，而是精確衡量「買賣價差」(Bid-Ask Spread) 與「流動性」(Liquidity)，這些是每筆交易中隱形的性能損耗來源。

🔶 **學術模型基礎 (SCIENTIFIC MODELS)**
🔹 **Roll (1984) 公式**：利用價格變化的負自相關性，在沒有報價數據的情況下逆推價差大小。
🔹 **Corwin-Schultz (2012)**：基於一週期與二週期的最高/最低價比例，分離出純粹的價差成分。
🔹 **Abdi-Ranaldo (2017)**：最新且最穩定的估算模型，將收盤價與區間中點的偏差進行對數化處理。
🔹 **Kyle (1985) Lambda**：衡量價格對淨成交流的敏感度。Lambda 飆升通常意味著市場中存在「知情交易者」。

---

**核心指標 (LIQUIDITY METRICS)**
- **Amihud (2002) 非流動性比率**：計算每單位成交金額引起的價格變動，展現市場深度。
- **流動性壓力指數 (LSI)**：綜合價差、深度與資訊不對稱，提供從 0 到 100 的壓力評分。
- **價差與波動率比**：區分「活躍且健康」的波動與「寬價差且低效」的波動。
""",
    "s032": """# Volume Flow Analysis [UAlgo] 成交量流向分析指標

成交量流向分析將歷史成交量映射到具體的價格位階上，並將其拆解為方向性壓力、潛在流動性、失衡區、吸收區、控制點 (POC) 及價值區 (Value Area)。

🔶 **主要功能 (FEATURES)**
🔹 **多維分布圖**：將每一根 K 線的成交量根據收盤位置拆分為買方與賣方壓力，展示在水平分布圖上。
🔹 **隱形流 (Stealth Flow)**：根據單位成交量的價格移動範圍，追踪移動效率。
🔹 **失衡檢測**：自動標註買賣壓力比例超過預設值的失衡區域。
🔹 **吸收檢測**：識別高成交量但低移動效率的區塊，提示潛在的籌碼吸收行為。
🔹 **適應性衰減**：可設置衰減因子，讓最近的成交量對分布圖形狀產生更大的影響。
""",
    "s033": """# Price Memory Heatmap 價格記憶熱力圖

「價位記憶熱力圖」視覺化了市場在哪裡產生記憶。它識別重複發生反應的價格水平，通過專有的熱力系統衡量其強度，並將其顯示為動態區域。這些區域會隨每次反應而加強，並隨著時間推移自然淡化。

🔶 **運作機制 (CORE MECHANISM)**
🔹 **熱量累加**：當價格在特定位階發生轉折 (Pivots) 或影線拒絕 (Wick Rejections) 時，該級別會獲得熱量。
🔹 **指數衰減**：若位階長時間未受測試，熱量會隨時間指數級流失，實現視覺上的「自動清理」。
🔹 **即時行為分類**：自動將當前與位階的交互分類為「拒絕」(Rejection)、「掃進」(Sweep)、「突破」(Break) 或「回測」(Retest)。
🔹 **層級劃分**：將位階分為「發展中」(Developing)、「活躍」(Active)、「強勁」(Strong) 與「主導」(Dominant)。

🔶 **使用效益**
幫助交易者區分一個水平是被測試過 1 次還是 10 次，以及當時是否有成交量支持。資深級別 (Veteran) 且高熱量的區域通常具有極深的結構意義。
""",
    "s034": """# RiiZA v14 專業機構交易套件

RiiZA v14 是一款全功能專業交易工具，旨在將技術指標與機構交易概念 (SMC/ICT) 相結合。此版本優化了空頭 (Sell) 訊號邏輯，並以簡潔的格式呈現所有數據。

🔶 **核心功能 (KEY FUNCTIONALITIES)**
- **自適應 ATR 訊號**：高精度趨勢追蹤，具備可調靈敏度以過濾市場噪音。
- **智能殺戮區 (Killzone)**：自動追踪亞洲、倫敦與紐約時段，進行即時流動性映射。
- **機構級工具**：自動檢測公允價值缺口 (FVG) 與訂單塊 (Order Blocks)。
- **位移追蹤器**：識別高動能 K 線，預示市場反轉或延續。
""",
    "s035": """# Intuitive Trade Regime [TraderZen] 直覺式交易體系

這款指標將價格變動的結構轉化為熟悉的直覺形狀——「樓梯」(Staircase)，讓交易者能以視覺感知趨勢的 character，而不是解讀抽象的數據。

🔶 **核心概念：樓梯 (THE STAIRCASE)**
- **踏面 (Tread)**：水平長度顯示當前體系維持的時間。
- **踢面 (Riser)**：垂直高度顯示趨勢切換的震級。
- **平台 (Landing)**：顯示市場在決定下一個動作前的盤整區域。
- **3D 深度信息**：利用 3D 透視強化視覺感知，多頭向上看（從下方觀察結構），空頭向下看（從上方俯瞰跌勢）。

🔶 **視覺效果**
- **瀑布 (Waterfall)**：在狹窄的跌勢中顯示瀑布流狀，代表快速清算。
- **碎石 (Cliff)**：在強勁的漲勢中顯示險峻懸崖，傳達高動能的能量。
""",
    "s036": """# PineScript Notepad++ 整合工具 (非指標)

這不是一個指標，而是一個為 Notepad++ (NPP) 編輯器設計的 PineScript 整合包。它支持 2026 年最新版的 PineScript v6，提供自動補全、函數列表與語法高亮功能。

🔶 **為什麼需要這個？**
- TradingView 自帶編輯器尚未提供完整的函數列表。
- NPP 允許高度自定義字體、顏色方案與暗黑模式，讓標準語法與用戶自定義函數在視覺上產生清晰區隔，提升編碼效率。
""",
    "s037": """# Gold Priceaction V2.00 黃金價格行為指標

這是一款專門為黃金 (XAUUSD) 市場設計的強大全能指標。黃金市場以高波動與機構「流動性獵取」(Liquidity Grabs) 著稱，本指標旨在透過數學計算追蹤機構足跡。

🔶 **核心功能**
- **動態趨勢線**：算法自動尋找最準確的上升與下降趨勢線。
- **智能樞紐 (Pivots)**：精確區分「強高低點」（硬支撐壓力）與「弱高低點」（目標吸引位）。
- **機構區域**：自動高亮訂單塊 (Order Blocks) 與公允價值缺口 (FVG)。
- **多時區背景**：直接在低時區圖表顯示 PDH/PDL（前日高低點）等宏觀價位。

🔶 **互動式儀表板**
包含即時獲利概率評分、趨勢偏差分析與自適應止損建議，幫助交易者與「聰明錢」站在同一邊。
""",
    "s038": """# SMT Divergences & BOS Detector 市場相關性與結構突破檢測器

本開源指標將聰明錢技術 (SMT) 離散與市場結構突破 (BOS) 相結合，幫助交易者透過對比相關資產（如黃金 vs 美元指數）來識別潛在的反轉與確認。

🔶 **分析邏輯 (LOGIC)**
- **SMT 離散**：當一個市場創出新高而另一個相關市場未能創出新高時，顯示趨勢轉弱。支持多品種對比與反向相關性（反轉）處理。
- **BOS 檢測**：動態追踪波段高低點，過濾內部結構，標註趨勢的延續或反演。
- **綜合流程**：尋找 SMT 離散後的 BOS 確認，這被視為勝率極高的交易設置。
""",
    "s039": """# Ready, Aim, Fire! 階段式動能震盪指標

Ready, Aim, Fire! 是一款動能態勢震盪指標，通過「準備」(Ready)、「瞄準」(Aim) 與「開火」(Fire) 三個階段來識別交易轉折點。

🔶 **運作原則 (HOW IT WORKS)**
1. **隨機狀態引擎 (READY/AIM)**：使用三組隨機指標追蹤交叉。一次交叉為 READY（動能蓄勢），連續同向交叉為 AIM（動能飽滿）。
2. **Fisher 轉換 (MOMENTUM)**：將動能壓縮進有界區域，視覺化展現超買/超賣極限。
3. **開火訊號 (FIRE!)**：當動能發生轉折拐點時，發出綠色 (多) 或紅色 (空) 的執行標籤。

這是一套基於 David H. Starr 經典概念的專業級下層窗口視覺化系統。
""",
    "s040": """# Footprint Delta Trap PRO 足跡成交流陷阱指標

Footprint Delta Trap PRO 是一款基於訂單流 (Order Flow) 的反轉策略指標，專門用於偵測流動性陷阱，識別那些強大的買盤或賣盤被吸收並拒絕的時刻。

🔶 **檢測核心 (CORE LOGIC)**
- **Delta 異常尖峰**：識別激進的買方/賣方。
- **影線拒絕**：當強大的 Delta 伴隨著長影線且價格無法突破時，標註為陷阱。
- **POC 驗證**：利用控制點位置（Point of Control）確認流動性區。

🔶 **交易訊號**
- **BUY**：看漲陷阱檢測（賣壓被吸收）。
- **SELL**：看跌陷阱檢測（買壓被吸收）。
指標專注於偵測那些「失敗的突破」與「動能耗竭」動作，而非傳統的趨勢追隨。
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
