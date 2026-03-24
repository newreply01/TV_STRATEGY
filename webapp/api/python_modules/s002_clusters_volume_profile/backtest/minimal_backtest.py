import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime

# DB Config
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "postgres123",
    "dbname": "tradeview_strategy"
}

def backtest(symbol="2330"):
    print(f"Starting backtest for {symbol} - Clusters Volume Profile")
    # 這裡實作簡單的回測邏輯：當價格向上突破高交易量區域時買入，反之賣出。
    # 目前僅作範例框架。
    
    # 獲取數據
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = f"SELECT datetime, open, high, low, close, volume FROM daily_prices WHERE stock_id = '{symbol}' ORDER BY datetime ASC"
        df = pd.read_sql(query, conn)
        conn.close()
    except Exception as e:
        print(f"Error fetching data: {e}. Backtest aborted.")
        return
        
    if df.empty:
        print("No data found for backtest.")
        return

    # 計算簡單信號（範例：靠近近期高量區則標示）
    # 在實際實作中，這會與 indicator.py 共享邏輯
    
    initial_capital = 1000000
    capital = initial_capital
    position = 0
    
    for i in range(1, len(df)):
        price = df.loc[i, 'close']
        # 買入邏輯範例：價格 > 前一日收盤且量大
        if df.loc[i, 'volume'] > df.loc[i-1, 'volume'] * 1.5 and position == 0:
            position = capital // price
            capital -= position * price
            print(f"BUY at {price} on {df.loc[i, 'datetime']}")
        # 賣出邏輯範例：賺 5% 就跑
        elif position > 0 and price > (initial_capital / position) * 1.05:
            capital += position * price
            position = 0
            print(f"SELL at {price} on {df.loc[i, 'datetime']} (Profit Take)")

    final_portfolio = capital + (position * df.iloc[-1]['close'])
    profit = final_portfolio - initial_capital
    print(f"Backtest Finished. Total Profit: {profit:.2f}")

if __name__ == "__main__":
    backtest()
