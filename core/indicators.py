import pandas as pd
import numpy as np

def calculate_ema(prices: pd.Series, period: int = 200) -> pd.Series:
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return prices.ewm(span=max(len(prices), 1), adjust=False).mean()
    return prices.ewm(span=period, adjust=False).mean()

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate Relative Strength Index (RSI)."""
    if len(prices) < 2:
        return 50.0
    
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    
    last_gain = avg_gain.iloc[-1]
    last_loss = avg_loss.iloc[-1]
    
    if last_loss == 0:
        return 100.0 if last_gain > 0 else 50.0
    if last_gain == 0:
        return 0.0
        
    rs = last_gain / last_loss
    return float(100.0 - (100.0 / (1.0 + rs)))

def calculate_drawdown(current_price: float, ath_price: float) -> float:
    """Calculate percentage drawdown from All-Time High."""
    if ath_price <= 0:
        return 0.0
    return float(((current_price - ath_price) / ath_price) * 100.0)
