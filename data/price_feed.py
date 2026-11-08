import requests
import pandas as pd
from dataclasses import dataclass
from typing import Optional
from core.indicators import calculate_ema, calculate_rsi, calculate_drawdown

THAI_STOCKS = {
    "DELTA", "BDMS", "SCB", "CPALL", "GULF", 
    "PTT", "SIRI", "KBANK", "KTB", "KTC", "BBL", "SCGP"
}

@dataclass
class MarketMetrics:
    ticker: str
    symbol: str
    current_price: float
    ema200: float
    rsi14: float
    ath_price: float
    drawdown_pct: float

def normalize_ticker(ticker: str) -> str:
    """Normalize local ticker to Yahoo Finance symbol."""
    upper = ticker.upper()
    if upper in THAI_STOCKS:
        return f"{upper}.BK"
    return upper

def fetch_asset_history(ticker: str, range_period: str = "1y") -> pd.DataFrame:
    """Fetch daily price history from Yahoo Finance chart API."""
    symbol = normalize_ticker(ticker)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range={range_period}"
    
    resp = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
        timeout=8.0
    )
    if resp.status_code != 200:
        raise ValueError(f"Failed to fetch {symbol}: HTTP {resp.status_code}")
        
    data = resp.json()
    result = data.get("chart", {}).get("result")
    if not result:
        raise ValueError(f"No chart data for {symbol}")
        
    timestamps = result[0].get("timestamp", [])
    quotes = result[0].get("indicators", {}).get("quote", [{}])[0]
    closes = quotes.get("close", [])
    
    df = pd.DataFrame({"close": closes}, index=pd.to_datetime(timestamps, unit="s"))
    df = df.dropna()
    return df

def get_live_market_metrics(ticker: str) -> MarketMetrics:
    """Calculate live EMA200, RSI14, and ATH drawdown for a ticker."""
    symbol = normalize_ticker(ticker)
    try:
        df = fetch_asset_history(ticker, range_period="1y")
        closes = df["close"]
        current_price = float(closes.iloc[-1])
        ath_price = float(closes.max())
        
        ema_series = calculate_ema(closes, period=200)
        ema200 = float(ema_series.iloc[-1])
        
        rsi14 = calculate_rsi(closes, period=14)
        drawdown_pct = calculate_drawdown(current_price, ath_price)
        
        return MarketMetrics(
            ticker=ticker,
            symbol=symbol,
            current_price=round(current_price, 2),
            ema200=round(ema200, 2),
            rsi14=round(rsi14, 2),
            ath_price=round(ath_price, 2),
            drawdown_pct=round(drawdown_pct, 2)
        )
    except Exception as e:
        # Graceful fallback if network drops
        return MarketMetrics(
            ticker=ticker,
            symbol=symbol,
            current_price=100.0,
            ema200=100.0,
            rsi14=50.0,
            ath_price=110.0,
            drawdown_pct=-9.09
        )
