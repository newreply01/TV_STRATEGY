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

def get_data(symbol="2330", limit=300):
    """從 stock_screener.realtime_ticks 獲取 OHLCV 數據"""
    try:
        conn = psycopg2.connect(**DB_CONFIG_SCREENER)
        # 使用 research_db.py 中確認的欄位名稱
        query = f"""
            SELECT trade_time as datetime, open_price as open, high_price as high, 
                   low_price as low, price as close, volume 
            FROM realtime_ticks 
            WHERE symbol = '{symbol}' 
            ORDER BY trade_time DESC 
            LIMIT {limit}
        """
        df = pd.read_sql(query, conn)
        conn.close()
        df = df.iloc[::-1].reset_index(drop=True)
        return df
    except Exception as e:
        print(f"Error fetching data from local DB: {e}. Using dummy data instead.")
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

    profile_data = []
    mean_vap = vap.mean()
    for i in range(n_bins):
        if vap[i] > 0:
            profile_data.append({
                "price": float(round(bin_centers[i], 2)),
                "volume": float(round(vap[i], 2)),
                "color": "rgba(33, 150, 243, 0.5)" if vap[i] < mean_vap else "rgba(255, 82, 82, 0.7)"
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
