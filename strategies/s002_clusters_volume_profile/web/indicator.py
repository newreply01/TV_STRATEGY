import pandas as pd
import numpy as np
try:
    import psycopg2
except ImportError:
    psycopg2 = None
    print("Warning: psycopg2 not found. Local DB features will be disabled.")
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

def get_data(symbol="2330", limit=2000, source="yahoo"):
    """
    獲取數據核心函數
    source="local": 從 PostgreSQL 資料庫獲取 (適合精確回測)
    source="yahoo": 從 Yahoo Finance 獲取 (適合快速網頁展示)
    預設使用近三天資料
    """
    if source == "yahoo":
        try:
            import yfinance as yf
            # 對於台股，確保有 .TW 後綴
            if symbol.isdigit() and len(symbol) == 4:
                fetch_symbol = f"{symbol}.TW"
            else:
                fetch_symbol = symbol
                
            df = yf.download(fetch_symbol, period="3d", interval="5m", progress=False)
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

def calculate_clusters_volume_profile(df, n_clusters=5, iterations=10, n_bins=120, window=600):
    if df.empty: return [], []
    latest_window = df.tail(window).copy()
    
    # 1. K-Means clustering setup
    latest_window['hlc2'] = (latest_window['high'] + latest_window['low']) / 2
    prices = latest_window['hlc2'].values
    volumes = latest_window['volume'].values
    
    p_min, p_max = latest_window['low'].min(), latest_window['high'].max()
    if p_max <= p_min: p_max = p_min + 0.1
    # Initial centroids: evenly spaced (Pine script implementation)
    step = (p_max - p_min) / (n_clusters + 1)
    centroids = np.array([p_min + (i + 1) * step for i in range(n_clusters)])
    assignments = np.zeros(len(prices), dtype=int)
    
    # 2. Iterations (1D K-Means)
    for _ in range(iterations):
        # Assign to nearest centroid
        distances = np.abs(prices[:, np.newaxis] - centroids)
        assignments = np.argmin(distances, axis=1)
        
        # Update centroids (volume-weighted)
        for k in range(n_clusters):
            mask = (assignments == k)
            if mask.any():
                centroids[k] = np.sum(prices[mask] * volumes[mask]) / np.sum(volumes[mask])
    
    # 3. Colors
    palette = [
        "rgba(171, 71, 188, 0.75)", # Purple
        "rgba(255, 167, 38, 0.75)", # Orange
        "rgba(102, 187, 106, 0.75)",# Green
        "rgba(239, 83, 80, 0.75)",  # Red
        "rgba(66, 165, 245, 0.75)"  # Blue
    ]
    
    # 4. Generate Profiles per Cluster
    all_profile_bins = []
    pocs = []
    
    # Sort centroids to ensure consistent coloring from bottom to top
    sorted_indices = np.argsort(centroids)
    
    for i, k in enumerate(sorted_indices):
        mask = (assignments == k)
        if not mask.any(): continue
        
        cluster_df = latest_window[mask]
        c_min, c_max = cluster_df['low'].min(), cluster_df['high'].max()
        
        # Calculate profile for this cluster
        fixed_rows = 20
        bins = np.linspace(c_min, c_max, fixed_rows + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        bin_vap = np.zeros(fixed_rows)
        
        for _, row in cluster_df.iterrows():
            wick_range = max(row['high'] - row['low'], 0.01) # fallback mintick
            
            for b_idx in range(fixed_rows):
                bin_b = bins[b_idx]
                bin_t = bins[b_idx + 1]
                intersect_l = max(row['low'], bin_b)
                intersect_h = min(row['high'], bin_t)
                
                if intersect_h > intersect_l:
                    bin_vap[b_idx] += row['volume'] * (intersect_h - intersect_l) / wick_range
        
        # Total Volume and POC for the cluster
        total_vol = cluster_df['volume'].sum()
        poc_price = bin_centers[np.argmax(bin_vap)] if len(bin_vap) > 0 else centroids[k]
        
        color = palette[i % len(palette)]
        
        # Add POC info for dashed lines
        pocs.append({
            "price": float(round(poc_price, 2)),
            "color": color,
            "total_volume": float(total_vol)
        })
        
        for j in range(len(bin_vap)):
            all_profile_bins.append({
                "price": float(round(bin_centers[j], 2)),
                "volume": float(round(bin_vap[j], 2)),
                "color": color
            })
            
    # Sort profiles by price for frontend rendering
    all_profile_bins.sort(key=lambda x: x['price'])
    return all_profile_bins, pocs

def main(symbol="2330"):
    df = get_data(symbol)
    profile, pocs = calculate_clusters_volume_profile(df)
    
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
        "pocs": pocs,
        "symbol": symbol,
        "title": "Clusters Volume Profile [LuxAlgo]"
    }

if __name__ == "__main__":
    res = main()
    print(f"Computed {len(res['pocs'])} clusters for {res['symbol']}.")
