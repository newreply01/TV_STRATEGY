import sys
import os
from pathlib import Path

# Add python_modules to path to find strategy logic
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "python_modules"))

import json
import pandas as pd
import numpy as np
import yfinance as yf
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# Import strategy modules from logic folder
try:
    from s001_omni_flow.web.indicator import get_omni_flow_data
    from s002_clusters_volume_profile.web.indicator import calculate_clusters_volume_profile
except ImportError:
    # Fallback to local structure if needed
    from python_modules.s001_omni_flow.web.indicator import get_omni_flow_data
    from python_modules.s002_clusters_volume_profile.web.indicator import calculate_clusters_volume_profile

from strategy_003 import process_strategy_003

# Configure logging for Vercel (standard output)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Vercel handles CORS but we can keep it for safety during testing
CORS(app)

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
            actual_period = "60d"
            
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=actual_period, interval=interval)
        
        if df is None or df.empty:
            df = yf.download(symbol, period=actual_period, interval=interval, progress=False, auto_adjust=True)
            
        if df is None or df.empty:
            return None
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        logger.error(f"Engine Exception during yf fetch for {symbol}: {str(e)}")
        return None

@app.route('/health')
def health_check():
    return jsonify({"status": "UP", "message": "Vercel Python Engine is running", "python_version": sys.version})

@app.route('/charts/<slug>')
def get_chart_data(slug):
    symbol = request.args.get('symbol', 'AAPL')
    is_tw = ".TW" in symbol.upper() or symbol.isdigit()
    default_period = '7d' if is_tw else '5d'

    interval = request.args.get('interval', '5m')
    period = request.args.get('period', default_period)
    source_param = request.args.get('source', 'yahoo')
    
    yf_symbol = f"{symbol}.TW" if symbol.isdigit() else symbol
    df = fetch_yfinance_data(symbol=yf_symbol, period=period, interval=interval)
    source = "yfinance"

    if df is not None and not df.empty:
        # Branching logic based on slug
        if slug == SLUG_S002:
            df_s002 = df.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
            })
            profile, pocs = calculate_clusters_volume_profile(df_s002, n_clusters=6)
            
            ohlc = []
            for idx, row in df.iterrows():
                ohlc.append({
                    "time": int(idx.timestamp()),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close'])
                })
            
            if ohlc:
                try:
                    import re
                    match = re.match(r"(\d+)([a-zA-Z]+)", interval)
                    if match:
                        val, unit = int(match.group(1)), match.group(2).lower()
                        if unit == 'm': sec = val * 60
                        elif unit == 'h': sec = val * 3600
                        elif unit == 'd': sec = val * 86400
                        else: sec = 300
                    else:
                        sec = 300
                    bars_to_add = min(int((48 * 3600) / sec), 50)
                    last_time = ohlc[-1]["time"]
                    for i in range(1, bars_to_add + 1):
                        ohlc.append({"time": last_time + i * sec})
                except Exception as e:
                    pass
            
            data = {
                "ohlc": ohlc, "volume_profile": profile, "pocs": pocs,
                "indicator": [], "signal": [], "markers": []
            }
        elif slug == SLUG_S003:
            data = process_strategy_003(df)
        else:
            data = get_omni_flow_data(df)
            
        data['metadata'] = {
            "source": source, "symbol": symbol, "interval": interval,
            "period": period, "slug": slug
        }
        return jsonify(data)
    else:
        return jsonify({"error": f"No data found from {source} for {symbol}"}), 404

# Vercel entry point
# No app.run() needed, but we can wrap it for local dev
if __name__ == "__main__":
    app.run(port=26001)
