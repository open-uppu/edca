import pandas as pd
import numpy as np
from core.indicators import calculate_ema, calculate_rsi, calculate_drawdown

def test_calculate_drawdown():
    # ATH = 100, Current = 80 -> -20.0%
    dd = calculate_drawdown(current_price=80.0, ath_price=100.0)
    assert round(dd, 2) == -20.0
    
    # At ATH -> 0.0%
    assert calculate_drawdown(100.0, 100.0) == 0.0

def test_calculate_rsi_flat():
    prices = pd.Series([100.0] * 30)
    rsi = calculate_rsi(prices, period=14)
    assert 45.0 <= rsi <= 55.0  # neutral

def test_calculate_rsi_strong_uptrend():
    prices = pd.Series([100.0 + i * 2.0 for i in range(30)])
    rsi = calculate_rsi(prices, period=14)
    assert rsi > 70.0  # overbought

def test_calculate_ema():
    prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    ema = calculate_ema(prices, period=3)
    assert len(ema) == len(prices)
    assert ema.iloc[-1] > ema.iloc[0]
