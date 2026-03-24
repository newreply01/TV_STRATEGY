import os
import json
import psycopg2
import pandas as pd
import numpy as np
import yfinance as yf
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from s001_omni_flow.web.indicator import get_omni_flow_data
from s002_clusters_volume_profile.web.indicator import calculate_clusters_volume_profile
from strategy_003 import process_strategy_003

# Configure logging to write to a file explicitly
logging.basicConfig(
    filename='/home/xg/tradeview-strategy/strategies/chart_engine.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("--- Chart Engine Starting ---")
logger.info(f"yfinance version: {yf.__version__}")

app = Flask(__name__)
# Keep CORS relaxed for localhost
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Strategy Slug Constants
SLUG_S001 = "3ONFG3bJ-Omni-Flow-Consensus-LuxAlgo"
SLUG_S002 = "lpnsjMbH-Clusters-Volume-Profile-LuxAlgo"
SLUG_S003 = "vXui7vrm-Market-Structure-Dashboard-Flux-Charts"

def fetch_yfinance_data(symbol="2330.TW", period="1mo", interval="15m"):
    try:
        actual_period = period
        if interval == '1m' and (period not in ['1d', '5d', '7d']):
            actual_period = "7d"
        elif interval in ['5m', '15m', '30m'] and period == '2mo':
            # Yahoo limit for intraday < 1h is 60 days. Standardize 2mo to 60d.
            actual_period = "60d"
            logger.info(f"Engine: Standardizing {interval} period 2mo to 60d for Yahoo compatibility")
            
        logger.info(f"Engine: Downloading {symbol} via Ticker (period={actual_period}, interval={interval})")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=actual_period, interval=interval)
        
        if df is None or df.empty:
            # Retry with download if history fails
            logger.warning(f"Engine Warning: Ticker.history empty for {symbol}, trying download...")
            df = yf.download(symbol, period=actual_period, interval=interval, progress=False, auto_adjust=True)
            
        if df is None or df.empty:
            logger.error(f"Engine Error: All yf methods returned EMPTY for {symbol}")
            return None
            
        logger.info(f"Engine: Download success for {symbol}. Shape: {df.shape}")
        
        # Flatten MultiIndex if necessary
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logger.error(f"Engine Exception during yf fetch for {symbol}: {error_msg}")
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
    symbol = request.args.get('symbol', 'AAPL')
    # Determine default period based on exchange (Taiwan vs others)
    is_tw = ".TW" in symbol.upper() or symbol.isdigit()
    default_period = '7d' if is_tw else '5d'

    interval = request.args.get('interval', '5m')
    period = request.args.get('period', default_period)
    print(f"Engine Request: symbol={symbol}, period={period}, is_tw={is_tw}")
    source_param = request.args.get('source', 'yahoo')
    df = None
    source = source_param

    # Use local DB if explicitly requested or if it's the old 1m/1d default
    if source == 'local' or (period == '1d' and interval == '1m'):
        df = fetch_stock_screener_data(symbol=symbol)
        source = "local_db"
    
    if df is None or df.empty:
        # Fallback to yfinance if local_db fails, or if default yahoo
        print(f"Engine: Attempting yfinance fetch for {symbol} (fallback or regular)")
        yf_symbol = f"{symbol}.TW" if symbol.isdigit() else symbol
        df = fetch_yfinance_data(symbol=yf_symbol, period=period, interval=interval)
        source = "yfinance"

    if df is not None and not df.empty:
        print(f"Engine: Using {source} for {symbol} ({interval}/{period}), Count: {len(df)}")
        
        # Branching logic based on slug
        if slug == SLUG_S002:
            # S002: Volume Profile
            # Rename columns to lowercase for S002's indicator function
            df_s002 = df.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
            })
            profile, pocs = calculate_clusters_volume_profile(df_s002, n_clusters=6)
            
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
            
            # Predict future times for 2 days buffer (48 hours)
            if ohlc:
                try:
                    import re
                    # parse interval string to seconds (e.g. '5m' -> 300)
                    match = re.match(r"(\d+)([a-zA-Z]+)", interval)
                    if match:
                        val, unit = int(match.group(1)), match.group(2).lower()
                        if unit == 'm': sec = val * 60
                        elif unit == 'h': sec = val * 3600
                        elif unit == 'd': sec = val * 86400
                        else: sec = 300
                    else:
                        sec = 300
                    
                    # 避免 24 小時市場的 5分K 塞入 500 多根導致縮放太過極端
                    # 預設 150~200 根即有視覺上兩天的留白效果，依照使用者需求再減半為 100 以下，現在再度減半為 50 根
                    bars_to_add = min(int((48 * 3600) / sec), 50)
                    last_time = ohlc[-1]["time"]
                    for i in range(1, bars_to_add + 1):
                        ohlc.append({"time": last_time + i * sec})
                except Exception as e:
                    print(f"Error appending future timescale: {e}")
            
            data = {
                "ohlc": ohlc,
                "volume_profile": profile,
                "pocs": pocs,
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

