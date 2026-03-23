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
            background-color: #0a0a0b;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        header {
            padding: 20px 40px;
            background: rgba(255, 255, 255, 0.03);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .title {
            font-size: 24px;
            font-weight: 900;
            letter-spacing: -0.02em;
        }
        .symbol {
            color: #00e5ff; /* 更改為更亮眼的 Cyan */
            margin-right: 10px;
        }
        #chart-container {
            flex: 1;
            width: 100%;
        }
    </style>
</head>
<body>
    <header>
        <div class="title"><span class="symbol">{{symbol}}</span> Omni-Flow Snapshot</div>
        <div style="font-size: 12px; opacity: 0.5;">Exported on: <script>document.write(new Date().toLocaleString())</script></div>
    </header>
    <div id="chart-container"></div>

    <script>
        try {
            const chartData = {{json_data}};
            console.log("Chart Data Loaded:", chartData.ohlc.length, "bars");
            
            if (chartData.ohlc.length === 0) {
                document.getElementById('chart-container').innerHTML = '<div style="padding: 20px; color: #ef5350;">Error: No data in export.</div>';
            } else {
                const chart = LightweightCharts.createChart(document.getElementById('chart-container'), {
                    layout: {
                        background: { type: 'solid', color: '#0a0a0b' },
                        textColor: '#d1d4dc',
                    },
                    grid: {
                        vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
                        horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
                    },
                    crosshair: {
                        mode: LightweightCharts.CrosshairMode.Normal,
                    },
                    rightPriceScale: {
                        borderColor: 'rgba(197, 203, 206, 0.8)',
                    },
                    timeScale: {
                        borderColor: 'rgba(197, 203, 206, 0.8)',
                        timeVisible: true,
                    },
                });

                const candlestickSeries = chart.addCandlestickSeries({
                    upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
                    wickUpColor: '#26a69a', wickDownColor: '#ef5350',
                });
                candlestickSeries.setData(chartData.ohlc);

                const flowSeries = chart.addLineSeries({
                    color: '#00e5ff',
                    lineWidth: 2,
                    priceScaleId: 'left',
                });
                flowSeries.setData(chartData.indicator);

                const flowSignalSeries = chart.addLineSeries({
                    color: '#ff1744',
                    lineWidth: 1,
                    lineStyle: 2,
                    priceScaleId: 'left',
                });
                flowSignalSeries.setData(chartData.signal);

                chart.priceScale('left').applyOptions({
                    autoScale: true,
                    visible: true,
                    borderColor: 'rgba(197, 203, 206, 0.1)',
                });

                candlestickSeries.setMarkers(chartData.markers);
                
                // Force fit content after a short delay to ensure scales are ready
                setTimeout(() => {
                    chart.timeScale().fitContent();
                }, 100);

                window.addEventListener('resize', () => {
                    chart.applyOptions({ 
                        width: document.getElementById('chart-container').offsetWidth,
                        height: document.getElementById('chart-container').offsetHeight
                    });
                });
            }
        } catch (e) {
            console.error("Chart Init Error:", e);
            document.getElementById('chart-container').innerHTML = '<div style="padding: 20px; color: #ef5350;">JS Error: ' + e.message + '</div>';
        }
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
