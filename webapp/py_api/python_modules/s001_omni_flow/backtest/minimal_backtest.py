import pandas as pd
import yfinance as yf
from web.indicator import get_omni_flow_data

def run_simple_backtest(symbol='AAPL', period='2mo'):
    print(f"--- 啟動 {symbol} 策略回測範本 ---")
    
    # 模擬後端數據調用
    # 注意：這裡直接調用 web 目錄下的邏輯，確保回測與展示代碼一致
    data = get_omni_flow_data(symbol, interval='15m', period=period)
    
    if not data or 'indicator' not in data:
        print("數據獲取失敗。")
        return

    indicator_df = pd.DataFrame(data['indicator'])
    ohlc_df = pd.DataFrame(data['ohlc'])
    
    # 合併數據進行分析
    signals = indicator_df[indicator_df['marker'].notnull()]
    
    print(f"分析區間: {period}")
    print(f"總共偵測到信號數: {len(signals)}")
    print("\n最近 5 筆信號詳情:")
    print(signals.tail(5)[['time', 'marker', 'color']])
    
    # 簡單模擬交易邏輯
    # (此處可擴充為完整的 Backtrader 邏輯)
    print("\n--- 回測完成 ---")

if __name__ == "__main__":
    run_simple_backtest()
