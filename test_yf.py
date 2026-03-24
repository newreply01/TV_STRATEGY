import yfinance as yf
import pandas as pd
try:
    print("Testing yfinance download for AAPL...")
    df = yf.download("AAPL", period="5d", interval="5m", progress=False)
    if df is None or df.empty:
        print("Result: FAILED - DataFrame is empty or None")
    else:
        print(f"Result: SUCCESS - Shape: {df.shape}")
        if isinstance(df.columns, pd.MultiIndex):
            print("Detected MultiIndex columns, flattening...")
            df.columns = df.columns.get_level_values(0)
        print(df.head())
except Exception as e:
    print(f"Result: EXCEPTION - {e}")
