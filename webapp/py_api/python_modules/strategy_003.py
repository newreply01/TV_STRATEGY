import numpy as np
import pandas as pd

class MarketStructure:
    def __init__(self, lb=50):
        self.lb = lb

    def get_swings(self, df):
        df = df.copy()
        df['high_roll'] = df['High'].rolling(window=self.lb*2+1, center=True).max()
        df['low_roll'] = df['Low'].rolling(window=self.lb*2+1, center=True).min()
        
        df['is_high'] = df['High'] == df['high_roll']
        df['is_low'] = df['Low'] == df['low_roll']
        
        return df

    def find_structure(self, df):
        df = self.get_swings(df)
        
        bos = []
        choch = []
        
        last_high = None
        last_low = None
        trend = 0 # 1: bull, -1: bear
        
        for i in range(len(df)):
            row = df.iloc[i]
            price = row['Close']
            
            # Update Swings
            if row['is_high']: last_high = row['High']
            if row['is_low']: last_low = row['Low']
            
            # Detect Structure
            if last_high and price > last_high:
                if trend == 1:
                    bos.append({'time': row.name, 'price': last_high, 'type': 'Bullish BOS'})
                elif trend == -1:
                    choch.append({'time': row.name, 'price': last_high, 'type': 'Bullish CHoCH'})
                    trend = 1
                else:
                    trend = 1
                last_high = None # Reset after break
                
            elif last_low and price < last_low:
                if trend == -1:
                    bos.append({'time': row.name, 'price': last_low, 'type': 'Bearish BOS'})
                elif trend == 1:
                    choch.append({'time': row.name, 'price': last_low, 'type': 'Bearish CHoCH'})
                    trend = -1
                else:
                    trend = -1
                last_low = None # Reset after break
                
        return bos, choch

def process_strategy_003(df):
    # Ensure index is datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
        
    ms = MarketStructure(lb=5) # Smaller lb for demo responsiveness
    bos, choch = ms.find_structure(df)
    
    # Map to Chart Markers
    markers = []
    for b in bos:
        markers.append({
            'time': int(b['time'].timestamp()), # b['time'] is now Timestamp
            'position': 'aboveBar',
            'color': '#00ffcc',
            'shape': 'arrowUp',
            'text': 'BOS'
        })
    for c in choch:
        markers.append({
            'time': int(c['time'].timestamp()),
            'position': 'belowBar',
            'color': '#ff2e2e',
            'shape': 'arrowDown',
            'text': 'CHoCH'
        })
        
    ohlc = []
    for t, row in df.iterrows():
        ohlc.append({
            'time': int(t.timestamp()),
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close'])
        })
        
    return {
        'ohlc': ohlc,
        'markers': markers,
        'metadata': {'source': 'yfinance', 'interval': 'H'}
    }
