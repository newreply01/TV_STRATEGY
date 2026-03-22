import pandas as pd
import numpy as np
import pandas_ta as ta
import yfinance as yf
from sklearn.neighbors import KNeighborsClassifier

def calculate_knn_indicators(symbol="AAPL", period="1y", interval="1d"):
    """
    實作 Machine Learning Pivot Points (KNN) 的簡化版本作為 PoC。
    """
    # 1. 獲取數據
    data = yf.download(symbol, period=period, interval=interval)
    if data.empty:
        return None
    
    # 預處理：移除多重索引 (yfinance 可能返回)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 2. 特徵工程 (基於 Pine Script 常用指標)
    data['RSI'] = ta.rsi(data['Close'], length=14)
    data['CCI'] = ta.cci(data['High'], data['Low'], data['Close'], length=20)
    data['ADX'] = ta.adx(data['High'], data['Low'], data['Close'], length=14)['ADX_14']
    
    # 清理空值
    df = data.dropna().copy()
    
    # 3. 定義目標：預測下一個 Pivot High/Low (簡化為漲跌)
    # 本 PoC 目的是展示數據流，非精準策略復刻
    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    
    # 4. KNN 模型
    X = df[['RSI', 'CCI', 'ADX']].values
    y = df['Target'].values
    
    # 訓練與預測
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X[:-1], y[:-1]) # 留最後一個測試
    
    df['KNN_Signal'] = knn.predict(X)
    
    # 5. 格式化為 Lightweight Charts 格式
    # OHLC
    ohlc_data = []
    for idx, row in df.iterrows():
        ohlc_data.append({
            "time": int(idx.timestamp()),
            "open": float(row['Open']),
            "high": float(row['High']),
            "low": float(row['Low']),
            "close": float(row['Close'])
        })
    
    # Signals (例如在圖表上標註)
    signals = []
    for idx, row in df.iterrows():
        if row['KNN_Signal'] == 1:
            signals.append({
                "time": int(idx.timestamp()),
                "position": "belowBar",
                "color": "#22c55e",
                "shape": "arrowUp",
                "text": "Buy"
            })
        else:
            signals.append({
                "time": int(idx.timestamp()),
                "position": "aboveBar",
                "color": "#ef4444",
                "shape": "arrowDown",
                "text": "Sell"
            })
            
    return {
        "ohlc": ohlc_data,
        "markers": signals
    }

if __name__ == "__main__":
    result = calculate_knn_indicators()
    if result:
        print(f"Calculated {len(result['ohlc'])} bars.")
        print(f"Sample signal: {result['markers'][-1]}")
