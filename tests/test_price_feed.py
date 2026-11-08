import pytest
from data.price_feed import fetch_asset_history, get_live_market_metrics, normalize_ticker

def test_normalize_ticker():
    assert normalize_ticker("GOOGL") == "GOOGL"
    assert normalize_ticker("DELTA") == "DELTA.BK"
    assert normalize_ticker("BDMS") == "BDMS.BK"
    assert normalize_ticker("SCB") == "SCB.BK"
    assert normalize_ticker("TSLA") == "TSLA"

def test_get_live_market_metrics():
    # Fetch live metrics for GOOGL
    metrics = get_live_market_metrics("GOOGL")
    assert metrics is not None
    assert metrics.current_price > 0.0
    assert metrics.ema200 > 0.0
    assert 0.0 <= metrics.rsi14 <= 100.0
    assert metrics.ath_price >= metrics.current_price
    assert metrics.drawdown_pct <= 0.0
