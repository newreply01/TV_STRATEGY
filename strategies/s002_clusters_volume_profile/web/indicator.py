import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime

# DB Configs
DB_CONFIG_STRATEGY = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "postgres123",
    "dbname": "tradeview_strategy"
}

DB_CONFIG_SCREENER = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "postgres123",
    "dbname": "stock_screener"
}

def get_data(symbol="2330", limit=300, source="yahoo"):
    """
    獲取數據核心函數
    source="local": 從 PostgreSQL 資料庫獲取 (適合精確回測)
    source="yahoo": 從 Yahoo Finance 獲取 (適合快速網頁展示)
    """
    if source == "yahoo":
        try:
            import yfinance as yf
            # 對於台股，確保有 .TW 後綴
            if symbol.isdigit() and len(symbol) == 4:
                fetch_symbol = f"{symbol}.TW"
            else:
                fetch_symbol = symbol
                
            df = yf.download(fetch_symbol, period="1mo", interval="15m", progress=False)
            if df.empty: raise ValueError("No data from yfinance")
            
            # 統一欄位名稱
            df = df.reset_index()
            # yfinance v0.2.40+ returns MultiIndex columns sometimes
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.rename(columns={
                'Date': 'datetime', 'Datetime': 'datetime', 
                'Open': 'open', 'High': 'high', 'Low': 'low', 
                'Close': 'close', 'Volume': 'volume'
            }, inplace=True)
            return df.tail(limit)
        except Exception as e:
            print(f"Yahoo Finance fetch failed: {e}. Falling back to dummy.")

    # Local DB Logic (Backtest mode)
    try:
        conn = psycopg2.connect(**DB_CONFIG_SCREENER)
        query = f"SELECT trade_time as datetime, open_price as open, high_price as high, low_price as low, price as close, volume FROM realtime_ticks WHERE symbol = '{symbol}' ORDER BY trade_time DESC LIMIT {limit}"
        df = pd.read_sql(query, conn)
        conn.close()
        df = df.iloc[::-1].reset_index(drop=True)
        if not df.empty: return df
    except Exception as e:
        print(f"Local DB fetch failed: {e}")

    # Fallback to Dummy
    print("Using dummy data as final fallback.")
    dates = pd.date_range(end=datetime.now(), periods=limit, freq='min')
    df = pd.DataFrame({
        'datetime': dates,
        'open': np.random.uniform(500, 600, limit),
        'high': np.random.uniform(505, 605, limit),
        'low': np.random.uniform(495, 595, limit),
        'close': np.random.uniform(500, 600, limit),
        'volume': np.random.uniform(100, 1000, limit)
    })
    return df

def calculate_clusters_volume_profile(df, n_bins=50, window=100):
    if df.empty: return []
    latest_window = df.tail(window)
    price_min, price_max = latest_window['low'].min(), latest_window['high'].max()
    if price_max == price_min: price_max += 0.1
    
    bins = np.linspace(price_min, price_max, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    vap = np.zeros(n_bins)
    
    for _, row in latest_window.iterrows():
        bar_bins = (bins[:-1] >= row['low']) & (bins[1:] <= row['high'])
        if bar_bins.any():
            vap[bar_bins] += row['volume'] / bar_bins.sum()
        else:
            idx = np.digitize(row['close'], bins) - 1
            if 0 <= idx < n_bins: vap[idx] += row['volume']

    # Define color palette matching the reference image
    palette = [
        "rgba(171, 71, 188, 0.7)",  # Purple
        "rgba(255, 167, 38, 0.7)",  # Orange
        "rgba(102, 187, 106, 0.7)", # Green
        "rgba(239, 83, 80, 0.7)",   # Red
        "rgba(66, 165, 245, 0.7)"   # Blue
    ]
    
    profile_data = []
    for i in range(len(vap)):
        # Assign color based on price percentile/index to create cluster effect
        color_idx = int((i / len(vap)) * len(palette))
        color_idx = min(color_idx, len(palette) - 1)
        
        profile_data.append({
            "price": float(round(bin_centers[i], 2)),
            "volume": float(round(vap[i], 2)),
            "color": palette[color_idx]
        })
    
    return profile_data

def main(symbol="2330"):
    df = get_data(symbol)
    profile = calculate_clusters_volume_profile(df)
    
    ohlc = []
    for _, row in df.iterrows():
        ohlc.append({
            "time": row['datetime'].timestamp() if hasattr(row['datetime'], 'timestamp') else str(row['datetime']),
            "open": float(row['open']),
            "high": float(row['high']),
            "low": float(row['low']),
            "close": float(row['close'])
        })
    
    return {
        "ohlc": ohlc,
        "volume_profile": profile,
        "symbol": symbol,
        "title": "Clusters Volume Profile [LuxAlgo]"
    }

if __name__ == "__main__":
    res = main()
    print(f"Computed Volume Profile for {res['symbol']} with {len(res['volume_profile'])} bins.")
