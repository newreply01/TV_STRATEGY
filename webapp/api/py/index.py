from flask import Flask, jsonify, request
import sys
import pandas as pd
import yfinance as yf
import importlib.util
import os

import os

app = Flask(__name__)

# Ensure current directory is in path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fetch_data(symbol, period="1mo", interval="1h"):
    if symbol.isdigit() and len(symbol) == 4:
        fetch_symbol = f"{symbol}.TW"
    else:
        fetch_symbol = symbol
    
    df = yf.download(fetch_symbol, period=period, interval=interval, progress=False)
    if df.empty:
        return None
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df.reset_index()
    # Standardize column names for the indicators
    df.rename(columns={
        'Date': 'datetime', 'Datetime': 'datetime',
        'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume',
        'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
    }, inplace=True)
    return df

@app.route('/api/py/health')
def health():
    return jsonify({
        "status": "OK",
        "message": "Python Engine is operational",
        "python": sys.version
    })

@app.route('/api/py/charts/<slug>')
def get_chart_data(slug):
    symbol = request.args.get('symbol', 'AAPL')
    interval = request.args.get('interval', '5m')
    period = request.args.get('period', '7d')
    
    # Map the frontend slug to strategy ID
    strategy_id = "s001_omni_flow"
    if "Volume-Profile" in slug:
        strategy_id = "s002_clusters_volume_profile"
    
    # Support strategy override via query param
    strategy_id = request.args.get('strategy', strategy_id)
    
    try:
        if strategy_id == "s001_omni_flow":
            df = fetch_data(symbol, period=period, interval=interval)
            if df is None: return jsonify({"error": "No data found"}), 404
            from python_modules.s001_omni_flow.web.indicator import get_omni_flow_data
            result = get_omni_flow_data(df)
            return jsonify(result)
            
        elif strategy_id == "s002_clusters_volume_profile":
            from python_modules.s002_clusters_volume_profile.web.indicator import main as get_s002_data
            result = get_s002_data(symbol)
            return jsonify(result)
            
        return jsonify({"error": "Strategy implementation not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/py/indicator')
def get_indicator():
# ... (existing content)
    strategy_id = request.args.get('strategy', 's001_omni_flow')
    symbol = request.args.get('symbol', '2330')
    
    # Map strategy IDs to their module paths
    strategy_map = {
        "s001_omni_flow": "python_modules.s001_omni_flow.web.indicator",
        "s002_clusters_volume_profile": "python_modules.s002_clusters_volume_profile.web.indicator"
    }
    
    if strategy_id not in strategy_map:
        return jsonify({"error": f"Strategy {strategy_id} not found"}), 404

    try:
        # Determine data requirements based on strategy
        if strategy_id == "s001_omni_flow":
            df = fetch_data(symbol, period="3mo", interval="1d") # Daily for omni flow usually
            if df is None: return jsonify({"error": "No data found"}), 404
            
            from python_modules.s001_omni_flow.web.indicator import get_omni_flow_data
            result = get_omni_flow_data(df)
            return jsonify(result)
            
        elif strategy_id == "s002_clusters_volume_profile":
            # S002 implementation in indicator.py already has get_data(symbol) which uses yfinance
            from python_modules.s002_clusters_volume_profile.web.indicator import main as get_s002_data
            result = get_s002_data(symbol)
            return jsonify(result)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fallback route
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({"message": f"Python engine root. Path accessed: {path}"})

if __name__ == "__main__":
    app.run(port=5000)
