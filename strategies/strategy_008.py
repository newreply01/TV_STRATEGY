import pandas as pd
import numpy as np
import math

def rma(series, length):
    """Running Moving Average (used in TradingView ta.rma)"""
    alpha = 1.0 / length
    return series.ewm(alpha=alpha, adjust=False).mean()

def calculate_adx(df, length=14):
    """Calculate ADX (Average Directional Index)"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    up_move = high.diff()
    down_move = -low.diff()
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    
    plus_dm = pd.Series(plus_dm, index=df.index)
    minus_dm = pd.Series(minus_dm, index=df.index)
    
    atr_rma = rma(tr, length)
    plus_rma = rma(plus_dm, length)
    minus_rma = rma(minus_dm, length)
    
    # Avoid division by zero
    plus_di = 100.0 * (plus_rma / atr_rma.replace(0, np.nan)).fillna(0)
    minus_di = 100.0 * (minus_rma / atr_rma.replace(0, np.nan)).fillna(0)
    
    sum_di = (plus_di + minus_di).replace(0, np.nan)
    dx = 100.0 * (abs(plus_di - minus_di) / sum_di).fillna(0)
    adx_val = rma(dx, length)
    
    return adx_val

def ma_dyn(src, length, ma_type="EMA"):
    """Dynamic MA calculation (EMA or RMA)"""
    length = max(1, int(length))
    if ma_type == "EMA":
        return src.ewm(span=length, adjust=False).mean()
    else: # RMA
        return rma(src, length)

def process_strategy_008(df, interval="15m"):
    """
    S008: Smart NR2-NR20 and Inside Bar (Zeiierman)
    Optimized Python implementation for chart engine.
    """
    if df is None or df.empty:
        return {"ohlc":[], "indicators":[], "markers":[], "signal":[]}

    # Ensure columns are lowercase
    df = df.rename(columns={
        'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
    })
    
    # --- Strategy Parameters (Pine Defaults) ---
    useInsideBar = True
    lookBack = 20
    lbMode = "Static" # "ADX Adaptive" supported
    b_adxLen = 14
    b_adxLo = 10.0
    b_adxHi = 35.0
    lbMin = 20
    lbMax = 120
    
    useTrendFilter = True
    trendMode = "Static"
    trendMaType = "EMA"
    trendMul = 2.0
    trendMaLen = 200
    # -------------------------------------------

    high = df['high']
    low = df['low']
    close = df['close']

    # 1. Adaptive Look Back Calculation
    if lbMode == "ADX Adaptive":
        adx_val = calculate_adx(df, b_adxLen)
        tB = ((adx_val - b_adxLo) / (b_adxHi - b_adxLo)).clip(0, 1)
        lb_series = (lbMax - tB * (lbMax - lbMin)).round().astype(int)
    else:
        lb_series = pd.Series(lookBack, index=df.index)
    lb_series = lb_series.clip(2, 500)
    
    # 2. Trend Filter MA
    # For performance in vectorized context, we use the average effective length
    # Pine script's ma_dyn with variable length is complex in Pandas.
    # We use a static 200 EMA as the default Trend Filter for reliability.
    eff_ma_len = trendMaLen
    if trendMode == "NR-Adaptive":
        eff_ma_len = int(lb_series.iloc[-1] * trendMul)
        eff_ma_len = max(20, min(200, eff_ma_len))
        
    trendMA = ma_dyn(close, eff_ma_len, trendMaType)
    allowLong = ~useTrendFilter | (close > trendMA)
    allowShort = ~useTrendFilter | (close < trendMA)

    # 3. NR Detection (Vectorized)
    # Scan n from 2 to 20
    nr_found = pd.Series(False, index=df.index)
    nr_len = pd.Series(np.nan, index=df.index)
    nr_rank = pd.Series(np.inf, index=df.index)
    
    # Use a fixed lookback for ranking efficiency (matching lb_series last value)
    L = int(lb_series.iloc[-1])
    
    for n in range(2, 21):
        # r = ta.highest(high, n) - ta.lowest(low, n)
        r = high.rolling(n).max() - low.rolling(n).min()
        
        # isNR: r < lowest(r[1], L)
        mn_prev = r.shift(1).rolling(L).min()
        is_nr = (r < mn_prev) & mn_prev.notna()
        
        # rankTightness (estimate): Percentage of past ranges smaller than current
        # Note: True rankTightness in Pine is math.sum(Range[1] <= current, L) / L
        # In vectorized: using rolling rank of current against past
        def calc_rank_vector(x):
            curr = x[-1]
            past = x[:-1]
            return (past <= curr).sum() / len(past) if len(past) > 0 else 1.0
            
        # Optimization: only calculate rank where is_nr is True
        if is_nr.any():
            # Approximate rank or use slow apply only for candidates
            candidates = is_nr[is_nr].index
            for idx in candidates:
                # get window [idx-L : idx]
                loc = df.index.get_loc(idx)
                if loc < L: continue
                window = r.iloc[loc-L : loc+1]
                rk = (window.iloc[:-1] <= window.iloc[-1]).sum() / L
                
                # Smart NR Selection
                if rk < nr_rank.loc[idx]:
                    nr_rank.loc[idx] = rk
                    nr_len.loc[idx] = n
                    nr_found.loc[idx] = True

    # 4. Inside Bar Detection
    isInsideBar = (high < high.shift(1)) & (low > low.shift(1))
    
    setupNow = nr_found.copy()
    setupLen = nr_len.copy()
    
    if useInsideBar:
        # Inside Bar is secondary to Smart NR
        mask_ib = (~setupNow) & isInsideBar
        setupNow.loc[mask_ib] = True
        setupLen.loc[mask_ib] = 1
        
    newSetup = setupNow & (~setupNow.shift(1).fillna(False))

    # 5. Signal Processing (State Machine for Breakouts)
    # We iterate through the data to find triggers
    markers = []
    
    pending = False
    p_hi = 0.0
    p_lo = 0.0
    p_name = ""
    p_rank = 1.0
    
    # Throttling logic
    last_signal_idx = -100
    min_dist = 5 # Minimum bars between any two signals
    
    # Prepare OHLC for frontend
    ohlc_data = []
    ma_data = []
    
    for i in range(len(df)):
        bar_idx = df.index[i]
        t = int(bar_idx.timestamp())
        
        ohlc_data.append({
            "time": t,
            "open": float(df['open'].iloc[i]),
            "high": float(df['high'].iloc[i]),
            "low": float(df['low'].iloc[i]),
            "close": float(df['close'].iloc[i])
        })
        
        ma_val = float(trendMA.iloc[i])
        if not math.isnan(ma_val):
            ma_data.append({"time": t, "value": ma_val})
            
        # If new setup occurs, replace or start pending
        # Stricter rank check for SNR (rank < 0.1) for high-quality signals
        if newSetup.iloc[i]:
            curr_rank = nr_rank.iloc[i] if not math.isnan(nr_rank.iloc[i]) else 1.0
            if setupLen.iloc[i] == 1 or curr_rank < 0.10:
                pending = True
                curr_len = int(setupLen.iloc[i])
                p_hi = float(df['high'].iloc[i-curr_len+1 : i+1].max())
                p_lo = float(df['low'].iloc[i-curr_len+1 : i+1].min())
                p_name = "SNR" if curr_len > 1 else "IB"
                p_rank = curr_rank

        # Check for trigger if pending and cooled down
        if pending and (i - last_signal_idx >= min_dist):
            can_long = allowLong.iloc[i]
            can_short = allowShort.iloc[i]
            
            is_bull = df['high'].iloc[i] >= p_hi
            is_bear = df['low'].iloc[i] <= p_lo
            
            if (is_bull and can_long) or (is_bear and can_short):
                # Trigger!
                is_long = is_bull and can_long
                if is_bull and is_bear:
                    is_long = abs(df['open'].iloc[i] - p_hi) <= abs(df['open'].iloc[i] - p_lo)
                
                # Double-check time to prevent vertical stacking even if data has dups
                if not markers or markers[-1]['time'] != t:
                    markers.append({
                        "time": t,
                        "position": "belowBar" if is_long else "aboveBar",
                        "color": "#2196F3" if is_long else "#FF5252",
                        "shape": "arrowUp" if is_long else "arrowDown"
                        # Fixed: Removed 'text' to declutter chart totally
                    })
                    last_signal_idx = i
                    pending = False
            elif i - last_signal_idx > 50: # Timeout pending if no breakout
                pending = False

    return {
        "ohlc": ohlc_data,
        "indicators": [
            {
                "name": "Trend MA",
                "type": "line",
                "data": ma_data,
                "color": "#FFC107",
                "lineWidth": 1,
                "pane": 0 # Main pane
            }
        ],
        "markers": markers,
        "signal": [] # Detailed signal list if needed
    }
