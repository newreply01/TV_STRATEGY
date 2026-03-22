import psycopg2

def fix_translation():
    conn = psycopg2.connect(
        host='localhost', 
        port=5433, 
        user='postgres', 
        password='postgres123', 
        dbname='tradeview_strategy'
    )
    cur = conn.cursor()
    
    zh_content = """Omni-Flow Consensus (全方位流向共識) 是一個綜合技術指標，旨在透過捕捉市場的多層次趨勢、波動性與成交量動能，提供精準的入場與出場信號。

核心特點：
1. **趨勢共識引擎**：結合了多種移動平均線與過濾算法，確保信號不被短期噪音干擾。
2. **動能波形分析**：即時分析成交量流向，識別機構大戶的進場跡象。
3. **多時間框架過濾**：內建跨週期確認機制，提升交易勝率。

使用說明：
- **看多信號**：當背景轉為綠色且出現向上箭頭時，代表趨勢向上共識達成。
- **看空信號**：當背景轉為紅色且出現向下箭頭時，代表趨勢向下共識達成。
- **過度擴展警示**：圖表上方或下方的點狀標示代表價格可能進入超買或超賣區間，建議適度減碼。"""

    en_content = """The Omni-Flow Consensus is a comprehensive technical indicator designed to provide precise entry and exit signals by capturing multi-layered market trends, volatility, and volume momentum.

Core Features:
1. **Trend Consensus Engine**: Combines multiple moving averages and filtering algorithms to ensure signals are not disturbed by short-term noise.
2. **Momentum Wave Analysis**: Real-time analysis of volume flow to identify signs of institutional entry.
3. **Multi-Timeframe Filtering**: Built-in cross-cycle confirmation mechanism to increase trading win rate.

Instructions:
- **Bullish Signal**: When the background turns green and an up arrow appears, it represents an upward trend consensus.
- **Bearish Signal**: When the background turns red and a down arrow appears, it represents a downward trend consensus.
- **Overextension Warning**: Dotted markings above or below the chart indicate that price may have entered overbought or oversold zones, suggesting moderate reduction."""

    cur.execute("""
        UPDATE tradingview_scripts 
        SET description_zh = %s, description_en = %s 
        WHERE slug = '3ONFG3bJ-Omni-Flow-Consensus-LuxAlgo'
    """, (zh_content, en_content))
    
    conn.commit()
    cur.close()
    conn.close()
    print("Successfully updated S001 translation.")

if __name__ == "__main__":
    fix_translation()
