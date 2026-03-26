import pandas as pd
import numpy as np
import pandas_ta as ta

def get_color_for_strength(val):
    """
    Return a hex color based on the flow_main value (-100 to 100)
    Author's Regimes:
    - Cyan (> 10, bullish)
    - Red (< -10, bearish)
    - Gray (-10 to 10, neutral/accumulation)
    """
    if val > 70: return "#00e5ff" # Strong Bullish (Cyan Bright)
    if val > 10: return "#00acc1"  # Bullish (Cyan)
    if val < -70: return "#ff1744" # Strong Bearish (Red Bright)
    if val < -10: return "#c62828" # Bearish (Red)
    return "#787b86" # Neutral (Gray)

def asf(src, high, low, close, length):
    """
    Adaptive Spectral Filter from original Pine Script
    """
    atr = ta.atr(high=high, low=low, close=close, length=length)
    alpha = 2.0 / (length + 1)
    
    src_diff = src.diff().abs()
    mintick = 0.01
    
    # adaptive_alpha = math.min(1.0, alpha * (math.abs(src - src[1]) / (diff + syminfo.mintick)))
    adaptive_alpha = (alpha * (src_diff / (atr + mintick))).clip(upper=1.0)
    
    out = np.zeros(len(src))
    src_np = src.to_numpy()
    aa_np = adaptive_alpha.to_numpy()
    
    # Initialize first valid data
    first_valid = src.first_valid_index()
    if first_valid is not None:
        idx = src.index.get_loc(first_valid)
        out[idx] = src_np[idx]
        for i in range(idx + 1, len(src)):
            aa = aa_np[i] if not pd.isna(aa_np[i]) else alpha
            out[i] = out[i-1] + aa * (src_np[i] - out[i-1])
            
    return pd.Series(out, index=src.index)

def calculate_omni_flow(df, flow_len=24, spectral_len=10, boost=1.5):
    """
    df: OHLCV DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
    """
    # 1. Volume Pressure
    smart_vol = df['Volume'].fillna(ta.true_range(df['High'], df['Low'], df['Close']))
    vol_pressure = (df['Close'] - df['Open']) / (np.maximum(df['High'] - df['Low'], 0.01)) * smart_vol
    
    # 2. Raw Flow (SMA)
    fpi_raw = ta.sma(vol_pressure, length=flow_len)
    
    # 3. Normalization
    fpi_highest = fpi_raw.rolling(window=flow_len * 2).max()
    fpi_lowest = fpi_raw.rolling(window=flow_len * 2).min()
    fpi_range = np.maximum(fpi_highest - fpi_lowest, 0.01)
    fpi_norm = ((fpi_raw - fpi_lowest) / fpi_range * 200) - 100
    
    # 4. Boosting
    boosted_flow = np.sign(fpi_norm) * np.power(np.abs(fpi_norm) / 100, 1 / boost) * 100
    
    # 5. Smoothing using Pine's Adaptive Spectral Filter
    flow_main = asf(boosted_flow, df['High'], df['Low'], df['Close'], spectral_len)
    flow_signal = ta.ema(flow_main, length=5) # Fixed to 5 as per Pine Source
    
    # Crosses for Signals
    cross_up = ta.cross(flow_main, flow_signal, above=True)
    cross_dn = ta.cross(flow_main, flow_signal, above=False)
    
    # Combine results
    df['is_bullish'] = flow_main > 0
    df['flow_main'] = flow_main
    df['flow_signal'] = flow_signal
    df['cross_up'] = cross_up
    df['cross_dn'] = cross_dn
    
    return df

def get_omni_flow_data(df, interval="15m"):
    """
    Format for Lightweight Charts with Professional Features
    """
    # Ensure DataFrame has a DatetimeIndex for the time filter logic
    if 'datetime' in df.columns:
        df = df.copy()
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
    elif not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df_calc = calculate_omni_flow(df)
    df_calc = df_calc.dropna()
    print(f"OMNI-Pro: Processing {len(df_calc)} bars.")
    
    ohlc = []
    indicator_main = []
    indicator_sig = []
    markers = []
    
    total_cross_up = int(df_calc['cross_up'].sum())
    total_cross_dn = int(df_calc['cross_dn'].sum())
    print(f"OMNI-Pro: Found {total_cross_up} Cross-Up, {total_cross_dn} Cross-Dn potential points.")
    
    # State tracking like Pine ta.barssince
    bars_since_cross_up = 999
    bars_since_cross_dn = 999
    
    # Tracks how many consecutive bars 'confirm' has been true
    bull_confirm_series = []
    bear_confirm_series = []
    
    # 1.0 month display filter (30 days)
    cutoff_time = df_calc.index.max() - pd.Timedelta(days=30)
    for idx, row in df_calc.iterrows():
        t = int(idx.timestamp())
        flow_v = float(row['flow_main'])
        sig_v = float(row['flow_signal'])
        
        # State tracking (Computed for ALL bars to ensure accuracy)
        if row['cross_up']: bars_since_cross_up = 0
        else: bars_since_cross_up += 1
        
        if row['cross_dn']: bars_since_cross_dn = 0
        else: bars_since_cross_dn += 1
        
        bull_confirm = (bars_since_cross_up < 3) and (flow_v > sig_v)
        bear_confirm = (bars_since_cross_dn < 3) and (flow_v < sig_v)
        
        bull_confirm_series.append(bull_confirm)
        bear_confirm_series.append(bear_confirm)
        
        is_impulse_bull = False
        is_impulse_bear = False
        
        if len(bull_confirm_series) >= 2:
            def bars_since_not(series):
                count = 0
                for v in reversed(series):
                    if not v: break
                    count += 1
                return count
            
            # Use same threshold logic (>15.0) and crossover detection
            bs_not_bull_prev = bars_since_not(bull_confirm_series[:-1])
            bs_not_bull_curr = bars_since_not(bull_confirm_series)
            if bs_not_bull_prev <= 2 and bs_not_bull_curr > 2 and flow_v > 15.0:
                is_impulse_bull = True
                
            bs_not_bear_prev = bars_since_not(bear_confirm_series[:-1])
            bs_not_bear_curr = bars_since_not(bear_confirm_series)
            if bs_not_bear_prev <= 2 and bs_not_bear_curr > 2 and flow_v < -15.0:
                is_impulse_bear = True

        # DISPLAY FILTER: Only append to JSON output if within last 1.5 months
        if idx >= cutoff_time:
            ohlc.append({
                "time": t,
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close'])
            })
            indicator_main.append({"time": t, "value": flow_v})
            indicator_sig.append({"time": t, "value": sig_v})
            
            if is_impulse_bull:
                markers.append({"time": t, "position": "inBar", "color": "#ffff00", "shape": "arrowUp", "size": 1})
            elif is_impulse_bear:
                markers.append({"time": t, "position": "inBar", "color": "#ffff00", "shape": "arrowDown", "size": 1})

            
    # Debug: Log for inspection
    if markers:
        from datetime import datetime
        print(f"\n[SIGNAL-REPORT] Symbol: 2330.TW | Total: {len(markers)} (UTC)")
        print("-" * 60)
        # Print last 20 for user check (Show TPE time for debugging)
        for m in markers[-20:]:
            # Display localized for console logs (assuming TPE is target)
            dt = datetime.fromtimestamp(m['time'] + 28800).strftime('%Y-%m-%d %H:%M')
            shape = m.get('shape', 'circle')
            print(f"{dt:<20} | {shape:<12} | {m['position']:<10} | {m['color']}")
        print("-" * 60)
            
    # Inject Future Empty Bars (0.5 Day = 43200 seconds)
    if ohlc:
        last_t = ohlc[-1]['time']
        # Dynamically determine step from interval (e.g. '15m' -> 900)
        step = 900 if '15' in interval else (300 if '5' in interval else 3600)
        num_bars_05d = 43200 // step if step > 0 else 1
        for i in range(1, num_bars_05d + 1):
            future_t = last_t + (i * step)
            ohlc.append({"time": future_t}) 

    return {
        "ohlc": ohlc,
        "indicator": indicator_main,
        "signal": indicator_sig,
        "markers": markers
    }
