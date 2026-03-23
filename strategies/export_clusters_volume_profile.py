import sys
import json
import yfinance as yf
import pandas as pd
import numpy as np
from s002_clusters_volume_profile.web.indicator import calculate_clusters_volume_profile

def generate_html(symbol, data):
    html_template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clusters Volume Profile: {{symbol}}</title>
    <script src="https://unpkg.com/lightweight-charts@4.2.1/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #000000;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }
        header {
            padding: 15px 30px;
            background: rgba(255, 255, 255, 0.02);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .title {
            font-size: 20px;
            font-weight: 900;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
        }
        .symbol {
            color: #ff9800;
            margin-right: 12px;
            background: rgba(255, 152, 0, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
        }
        main {
            flex: 1;
            display: flex;
            flex-direction: row;
            position: relative;
            gap: 4px;
            padding: 10px;
        }
        #profile-container {
            width: 120px;
            height: 100%;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            flex-direction: column;
            padding: 20px 0;
            position: relative;
        }
        .profile-label {
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 8px;
            font-weight: 900;
            color: #444;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            white-space: nowrap;
        }
        #chart-container {
            flex: 1;
            height: 100%;
            background: #000000;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            overflow: hidden;
        }
        /* HUD Overlay */
        .hud {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(20, 20, 22, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 16px;
            border-radius: 12px;
            width: 200px;
            z-index: 50;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            pointer-events: none;
        }
        .hud-header {
            font-size: 10px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #888;
            margin-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 4px;
        }
        .hud-row {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            margin-bottom: 8px;
        }
        .hud-label { color: #666; }
        .hud-value { font-weight: bold; }
        .status-active { color: #ffff00; animation: pulse 2s infinite; }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        /* Volume Bar */
        .v-bar {
            height: 100%;
            transition: width 0.3s;
            border-radius: 0 2px 2px 0;
        }
        .v-row {
            flex: 1;
            display: flex;
            align-items: center;
            padding-right: 5px;
            position: relative;
        }
    </style>
</head>
<body>
    <header>
        <div class="title"><span class="symbol">{{symbol}}</span> Clusters Volume Profile</div>
        <div style="font-size: 11px; opacity: 0.4;">Exported: <script>document.write(new Date().toLocaleString())</script></div>
    </header>
    <main>
        <div class="hud">
            <div class="hud-header">Clusters Volume Profile</div>
            <div class="hud-row"><span class="hud-label">Asset</span><span class="hud-value">{{symbol}}</span></div>
            <div class="hud-row"><span class="hud-label">Status</span><span class="hud-value" style="color: #ff9800;">FIXED PROFILE</span></div>
            <div class="hud-row"><span class="hud-label">Intensity</span><span class="hud-value">Lateral HUD</span></div>
            <div class="hud-row"><span class="hud-label">Sync</span><span class="hud-value status-active">ACTIVE</span></div>
        </div>
        <div id="profile-container">
            <div class="profile-label">Volume Profile</div>
            <!-- Bars will be injected here -->
        </div>
        <div id="chart-container"></div>
    </main>

    <script>
        const chartData = {{json_data}};
        
        // Render Volume Profile
        const profileContainer = document.getElementById('profile-container');
        const maxVol = Math.max(...chartData.volume_profile.map(p => p.volume));
        
        // We need to reverse because higher prices are at the top
        const sortedProfile = [...chartData.volume_profile].sort((a, b) => b.price - a.price);
        
        sortedProfile.forEach(p => {
            const row = document.createElement('div');
            row.className = 'v-row';
            const bar = document.createElement('div');
            bar.className = 'v-bar';
            bar.style.width = (p.volume / maxVol * 100) + '%';
            bar.style.backgroundColor = p.color;
            row.appendChild(bar);
            profileContainer.appendChild(row);
        });

        // Main Chart
        const chart = LightweightCharts.createChart(document.getElementById('chart-container'), {
            layout: { background: { type: 'solid', color: '#000000' }, textColor: '#d1d4dc' },
            grid: {
                vertLines: { color: 'rgba(42, 46, 57, 0.05)' },
                horzLines: { color: 'rgba(42, 46, 57, 0.05)' }
            },
            timeScale: { borderColor: 'rgba(197, 203, 206, 0.1)', timeVisible: true, rightOffset: 50 },
        });

        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#00ffcc', downColor: '#ff2e2e', borderVisible: false,
            wickUpColor: '#00ffcc', wickDownColor: '#ff2e2e',
        });
        candlestickSeries.setData(chartData.ohlc);

        chart.timeScale().fitContent();
        
        window.addEventListener('resize', () => {
            chart.applyOptions({ width: document.getElementById('chart-container').offsetWidth });
        });
    </script>
</body>
</html>
"""
    return html_template.replace("{{symbol}}", symbol).replace("{{json_data}}", json.dumps(data))

def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else "2330.TW"
    period = "60d"
    interval = "15m"
    
    print(f"Exporting {symbol} (Period: {period}, Interval: {interval})...")
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    if df.empty:
        print("Error: No data found.")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Ensure column names are lowercase for the indicator function
    df.columns = [col.lower() for col in df.columns]

    # Process Data
    profile = calculate_clusters_volume_profile(df)
    
    ohlc = []
    for index, row in df.iterrows():
        ohlc.append({
            "time": index.timestamp(),
            "open": float(row['open']),
            "high": float(row['high']),
            "low": float(row['low']),
            "close": float(row['close'])
        })
    
    data = {
        "ohlc": ohlc,
        "volume_profile": profile
    }
    
    html_content = generate_html(symbol, data)
    
    filename = f"{symbol.replace('.', '_')}_clusters_volume_profile.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Successfully exported to {filename}")

if __name__ == "__main__":
    main()
