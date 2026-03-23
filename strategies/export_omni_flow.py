import sys
import json
import yfinance as yf
import pandas as pd
from s001_omni_flow.web.indicator import get_omni_flow_data

def generate_html(symbol, data):
    html_template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omni-Flow Strategy: {{symbol}}</title>
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
            color: #00e5ff;
            margin-right: 12px;
            background: rgba(0, 229, 255, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
        }
        main {
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        #price-container {
            flex: 2;
            width: 100%;
        }
        #indicator-container {
            flex: 1;
            width: 100%;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
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
    </style>
</head>
<body>
    <header>
        <div class="title"><span class="symbol">{{symbol}}</span> Omni-Flow Snapshot</div>
        <div style="font-size: 11px; opacity: 0.4;">Exported: <script>document.write(new Date().toLocaleString())</script></div>
    </header>
    <main>
        <div class="hud">
            <div class="hud-header">Omni-Flow Consensus</div>
            <div class="hud-row"><span class="hud-label">Asset</span><span class="hud-value">{{symbol}}</span></div>
            <div class="hud-row"><span class="hud-label">Status</span><span class="hud-value" style="color: #00e5ff;">SMART FLOW</span></div>
            <div class="hud-row"><span class="hud-label">Intensity</span><span class="hud-value">Dual Panes</span></div>
            <div class="hud-row"><span class="hud-label">Sync</span><span class="hud-value status-active">ACTIVE</span></div>
        </div>
        <div id="price-container"></div>
        <div id="indicator-container"></div>
    </main>

    <script>
        const chartData = {{json_data}};
        
        const chartOptions = {
            layout: { background: { type: 'solid', color: '#000000' }, textColor: '#d1d4dc' },
            grid: {
                vertLines: { color: 'rgba(42, 46, 57, 0.05)' },
                horzLines: { color: 'rgba(42, 46, 57, 0.05)' }
            },
            timeScale: { borderColor: 'rgba(197, 203, 206, 0.1)', timeVisible: true, rightOffset: 20 },
        };

        const priceChart = LightweightCharts.createChart(document.getElementById('price-container'), {
            ...chartOptions,
            handleScroll: true,
            handleScale: true,
        });

        const indicatorChart = LightweightCharts.createChart(document.getElementById('indicator-container'), {
            ...chartOptions,
            timeScale: {
                ...chartOptions.timeScale,
                visible: true, // Show time scale on bottom chart
            },
        });

        // Price Series
        const candlestickSeries = priceChart.addCandlestickSeries({
            upColor: '#00ffcc', downColor: '#ff2e2e', borderVisible: false,
            wickUpColor: '#00ffcc', wickDownColor: '#ff2e2e',
        });
        candlestickSeries.setData(chartData.ohlc);

        // Indicator Series (Baseline for automatic color switching)
        const flowSeries = indicatorChart.addBaselineSeries({
            baseValue: { type: 'price', price: 0 },
            topFillColor1: 'rgba(0, 255, 255, 0.4)', topFillColor2: 'rgba(0, 255, 255, 0.05)', topLineColor: '#00ffff',
            bottomFillColor1: 'rgba(255, 46, 46, 0.05)', bottomFillColor2: 'rgba(255, 46, 46, 0.4)', bottomLineColor: '#ff2e2e',
            lineWidth: 3,
            lastValueVisible: false,
            priceLineVisible: false,
        });
        flowSeries.setData(chartData.indicator);

        const signalSeries = indicatorChart.addLineSeries({
            color: 'rgba(200, 200, 200, 0.3)',
            lineWidth: 1,
            lastValueVisible: false,
            priceLineVisible: false,
        });
        signalSeries.setData(chartData.signal);

        // Markers on Indicator Pane (matching user screenshot)
        flowSeries.setMarkers(chartData.markers);

        // Horizontal Lines for Indicator
        [90, 70, 0, -70, -90].forEach(p => {
            flowSeries.createPriceLine({
                price: p,
                color: p === 0 ? 'rgba(255, 255, 255, 0.4)' : (Math.abs(p) === 90 ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)'),
                lineWidth: 1,
                lineStyle: p === 0 ? 0 : 1, // Solid for zero, dashed for others
                axisLabelVisible: true,
                title: p === 0 ? 'ZERO' : `${p > 0 ? '+' : ''}${p}`,
            });
        });

        // Sync Time Scales
        let isSyncing = false;
        priceChart.timeScale().subscribeVisibleTimeRangeChange(range => {
            if (isSyncing) return;
            isSyncing = true;
            indicatorChart.timeScale().setVisibleTimeRange(range);
            isSyncing = false;
        });

        indicatorChart.timeScale().subscribeVisibleTimeRangeChange(range => {
            if (isSyncing) return;
            isSyncing = true;
            priceChart.timeScale().setVisibleTimeRange(range);
            isSyncing = false;
        });

        // Fit Content
        priceChart.timeScale().fitContent();
        
        // Handle Resize
        window.addEventListener('resize', () => {
            const width = document.body.clientWidth;
            priceChart.applyOptions({ width });
            indicatorChart.applyOptions({ width });
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

    # Flatten MultiIndex if necessary
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    data = get_omni_flow_data(df)
    html_content = generate_html(symbol, data)
    
    filename = f"{symbol.replace('.', '_')}_omni_flow.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Successfully exported to {filename}")

if __name__ == "__main__":
    main()
