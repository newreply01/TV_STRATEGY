import os
import json
import psycopg2
import pandas as pd
import numpy as np
import yfinance as yf
from flask import Flask, jsonify, request
from flask_cors import CORS
from s001_omni_flow.web.indicator import get_omni_flow_data
from s002_clusters_volume_profile.web.indicator import calculate_clusters_volume_profile
from strategy_003 import process_strategy_003

app = Flask(__name__)
# Keep CORS relaxed for localhost
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Strategy Slug Constants
SLUG_S001 = "3ONFG3bJ-Omni-Flow-Consensus-LuxAlgo"
SLUG_S002 = "lpnsjMbH-Clusters-Volume-Profile-LuxAlgo"
SLUG_S003 = "vXui7vrm-Market-Structure-Dashboard-Flux-Charts"

def fetch_yfinance_data(symbol="2330.TW", period="1mo", interval="15m"):
    """
    Fetch historical data from yfinance for backtesting or simulation.
    Note: 15m interval is only available for the last 60 days.
    """
    try:
        # Optimization: 15m interval is extremely sensitive to period
        actual_period = "1mo" 
        print(f"Engine: Downloading {symbol} from yf (period={actual_period}, interval={interval})")
        df = yf.download(symbol, period=actual_period, interval=interval, progress=False)
        
        if df is None or df.empty:
            print(f"Engine Error: yf returned EMPTY df for {symbol}")
            return None
            
        print(f"Engine: Download success for {symbol}. Shape: {df.shape}")
        
        # Standardize MultiIndex columns (yf 0.2.x+ behavior)
        if isinstance(df.columns, pd.MultiIndex):
            print(f"Engine: Flattening MultiIndex columns: {df.columns.tolist()[:2]}...")
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        print(f"Engine Exception during yf fetch: {e}")
        return None

def fetch_stock_screener_data(symbol="2330", limit=500):
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres123",
            dbname="stock_screener",
            port="5433"
        )
        # 修正: PostgreSQL 的 array_agg 語法與資料型態轉換
        query = f"""
            SELECT 
                date_trunc('minute', trade_time) as "Date",
                (array_agg(price ORDER BY trade_time ASC))[1] as "Open",
                MAX(price) as "High",
                MIN(price) as "Low",
                (array_agg(price ORDER BY trade_time DESC))[1] as "Close",
                SUM(volume) as "Volume"
            FROM realtime_ticks 
            WHERE symbol = '{symbol}' 
            GROUP BY 1
            ORDER BY 1 ASC
            LIMIT {limit}
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty:
            return None
            
        # Set index to Date and sort ascending
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date').sort_index()
        
        return df
    except Exception as e:
        print(f"Error fetching from stock_screener: {e}")
        return None

@app.route('/api/health')
def health_check():
    return jsonify({"status": "UP", "message": "Chart Engine is running"})

@app.route('/api/charts/<slug>')
def get_chart_data(slug):
    # Parameters from query string
    interval = request.args.get('interval', '1m')
    period = request.args.get('period', '1d')
    symbol = request.args.get('symbol', 'AAPL')
    
    # Logic: Use yfinance for longer periods or 15m interval
    if period != '1d' or interval == '15m':
        # Map 2330 -> 2330.TW for yfinance
        yf_symbol = f"{symbol}.TW" if symbol.isdigit() else symbol
        df = fetch_yfinance_data(symbol=yf_symbol, period=period, interval=interval)
        source = "yfinance"
    else:
        # Use local DB for real-time 1m data
        df = fetch_stock_screener_data(symbol=symbol)
        source = "local_db"
    
    if df is not None and not df.empty:
        print(f"Engine: Using {source} for {symbol} ({interval}/{period}), Count: {len(df)}")
        
        # Branching logic based on slug
        if slug == SLUG_S002:
            # S002: Volume Profile
            # Rename columns to lowercase for S002's indicator function
            df_s002 = df.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
            })
            profile = calculate_clusters_volume_profile(df_s002)
            
            # Create OHLC for frontend
            ohlc = []
            for idx, row in df.iterrows():
                ohlc.append({
                    "time": int(idx.timestamp()),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close'])
                })
            
            data = {
                "ohlc": ohlc,
                "volume_profile": profile,
                "indicator": [], # Placeholder to avoid errors
                "signal": [],
                "markers": []
            }
        elif slug == SLUG_S003:
            # S003: Market Structure Dashboard
            # Set a default 1h interval if not specified for S003
            data = process_strategy_003(df)
        else:
            # Default to S001: Omni-Flow
            data = get_omni_flow_data(df)
            
        data['metadata'] = {
            "source": source,
            "symbol": symbol,
            "interval": interval,
            "period": period,
            "slug": slug
        }
        return jsonify(data)
    else:
        return jsonify({"error": f"No data found from {source} for {symbol}"}), 404

if __name__ == "__main__":
    # Start on 26001 with debug
    app.run(host='0.0.0.0', port=26001, debug=True)

