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
            margin: 0; padding: 0;
            background-color: #000000; color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex; flex-direction: column; height: 100vh; overflow: hidden;
        }
        header {
            padding: 15px 30px; background: rgba(255, 255, 255, 0.02);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex; justify-content: space-between; align-items: center; z-index: 100;
        }
        main { flex: 1; display: flex; position: relative; padding: 0; overflow: hidden; }
        #chart-container { flex: 1; height: 100%; background: #000000; position: relative; }
        #profile-overlay {
            position: absolute; top: 40px; right: 80px; bottom: 60px; width: 300px;
            z-index: 20; display: flex; flex-direction: column; pointer-events: none; padding-right: 0px;
        }
        .v-row { flex: 1; display: flex; align-items: center; position: relative; }
        .v-bar { height: 2px; border-radius: 4px 0 0 4px; margin-left: auto; }
        .v-marker { position: absolute; left: 0; right: 0; display: flex; align-items: center; gap: 10px; transform: translateY(-50%); }
        .v-line { flex: 1; height: 1px; background-image: linear-gradient(to right, currentColor 50%, transparent 50%); background-size: 3px 1px; background-repeat: repeat-x; }
        .v-label {
            font-size: 9px; font-weight: 900; background: rgba(0, 0, 0, 0.6);
            padding: 2px 4px; border-radius: 3px; white-space: nowrap;
        }
    </style>
</head>
<body>
    <header>
        <div class="title"><span class="symbol">{{symbol}}</span> Clusters Volume Profile [K-Means]</div>
        <div style="font-size: 11px; opacity: 0.4;">Exported: <script>document.write(new Date().toLocaleString())</script></div>
    </header>
    <main>
        <div id="chart-container">
            <div id="chart" style="width: 100%; height: 100%;"></div>
            <div id="profile-overlay"></div>
            <div id="markers-container" style="position: absolute; inset: 0; pointer-events: none; z-index: 21; margin: 40px 80px 60px 10px;"></div>
        </div>
    </main>

    <script>
        const data = {{json_data}};
        
        const profileOverlay = document.getElementById('profile-overlay');
        const markersContainer = document.getElementById('markers-container');

        const maxVol = Math.max(...data.volume_profile.map(p => p.volume));
        const maxPrice = Math.max(...data.volume_profile.map(p => p.price));
        const minPrice = Math.min(...data.volume_profile.map(p => p.price));
        const priceRange = maxPrice - minPrice || 1;
        
        // Render Volume Bins
        [...data.volume_profile].sort((a, b) => b.price - a.price).forEach(p => {
            const row = document.createElement('div');
            row.className = 'v-row';
            const bar = document.createElement('div');
            bar.className = 'v-bar';
            bar.style.width = (p.volume / maxVol * 100) + '%';
            bar.style.backgroundColor = p.color;
            bar.style.opacity = '0.6';
            row.appendChild(bar);
            profileOverlay.appendChild(row);
        });

        // Render K-Means POC Lines
        (data.pocs || []).forEach(poc => {
            const marker = document.createElement('div');
            marker.className = 'v-marker';
            const topPos = ((maxPrice - poc.price) / priceRange) * 100;
            marker.style.top = topPos + '%';
            marker.style.color = poc.color;
            
            marker.innerHTML = `
                <div class="v-label" style="background: transparent;">${(poc.total_volume/1000).toFixed(1)}K</div>
                <div class="v-line" style="color: ${poc.color}; opacity: 0.9;"></div>
                <div class="v-label" style="border: 1px solid ${poc.color}33;">Total: ${(poc.total_volume/1000).toFixed(1)}K</div>
            `;
            markersContainer.appendChild(marker);
        });

        // Main Chart Setup
        const chart = LightweightCharts.createChart(document.getElementById('chart'), {
            layout: { background: { type: 'solid', color: '#000000' }, textColor: '#d1d4dc' },
            grid: { vertLines: { color: 'rgba(255, 255, 255, 0.05)' }, horzLines: { color: 'rgba(255, 255, 255, 0.05)' } },
            timeScale: { borderColor: 'rgba(255, 255, 255, 0.1)', timeVisible: true, rightOffset: 30 },
            rightPriceScale: { borderColor: 'rgba(255, 255, 255, 0.1)' }
        });

        const candleSeries = chart.addCandlestickSeries({
            upColor: '#089981', downColor: '#f23645', borderVisible: false,
            wickUpColor: '#089981', wickDownColor: '#f23645'
        });
        candleSeries.setData(data.ohlc);

        // Zoom to show 150 bars
        if (data.ohlc.length > 150) {
            const last = data.ohlc[data.ohlc.length-1].time;
            const first = data.ohlc[data.ohlc.length-150].time;
            chart.timeScale().setVisibleRange({ from: first, to: last });
        } else {
            chart.timeScale().fitContent();
        }

        window.addEventListener('resize', () => {
            chart.applyOptions({ width: document.getElementById('chart-container').offsetWidth });
        });
    </script>
</body>
</html>
"""
    return html_template.replace("{{symbol}}", symbol).replace("{{json_data}}", json.dumps(data))

def main():
    if len(sys.argv) < 2:
        symbol = "2330.TW"
    else:
        symbol = sys.argv[1]
        
    print(f"Exporting {symbol} with K-Means Clusters...")
    
    # Download 1 month of 5m data
    df = yf.download(symbol, period="1mo", interval="5m", progress=False)
    if df.empty:
        print("No data found.")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [col.lower() for col in df.columns]

    # Calculate Profile (returns profile, pocs)
    profile, pocs = calculate_clusters_volume_profile(df)
    
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
        "volume_profile": profile,
        "pocs": pocs
    }
    
    html = generate_html(symbol, data)
    filename = f"{symbol.replace('.', '_')}_kmeans_vp.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Exported to {filename}")

if __name__ == "__main__":
    main()
