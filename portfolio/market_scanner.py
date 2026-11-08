from dataclasses import dataclass
from typing import List, Optional
from data.price_feed import get_live_market_metrics
from core.edca_engine import compute_edca_multiplier

# Curated High-Moat Leaders available on Dime! (US + Global ETFs + Thai SET Leaders)
WATCHLIST_LEADERS: List[str] = [
    # US Mega-Cap & Growth Leaders
    "NVDA", "META", "MSFT", "AAPL", "GOOGL", "AMZN", "TSLA", "AMD", "ADBE", "AVGO",
    # Global & Index ETFs
    "VOO", "QQQ", "SCHD",
    # Thai Blue-Chips
    "DELTA.BK", "BDMS.BK", "CPALL.BK", "ADVANC.BK", "AOT.BK", "PTT.BK", "GULF.BK"
]

@dataclass
class Opportunity:
    ticker: str
    symbol: str
    current_price: float
    drawdown_pct: float
    rsi14: float
    ema200: float
    multiplier: float
    grade: str
    signal: str

def assign_grade(multiplier: float, rsi: float, dd_pct: float) -> tuple[str, str]:
    """Assign an opportunity grade and Thai actionable signal."""
    if multiplier >= 1.70:
        return "A+", "ช้อนซื้อของลดราคาด่วน (Deep Discount & Oversold)"
    elif multiplier >= 1.30:
        return "A", "เริ่มทยอยสะสมได้ดี (Attractive Dip)"
    elif multiplier >= 0.90:
        return "B", "ราคาปกติ/โซนสมดุล (Normal Range)"
    else:
        return "C", "ชะลอการซื้อ/ราคาสูงใกล้ ATH (Overpriced / Wait)"

def scan_market_opportunities(watchlist: Optional[List[str]] = None) -> List[Opportunity]:
    """Scan watchlist symbols and return opportunities sorted by EDCA discount score."""
    tickers = watchlist if watchlist is not None else WATCHLIST_LEADERS
    opportunities: List[Opportunity] = []
    
    for ticker in tickers:
        metrics = get_live_market_metrics(ticker)
        multiplier = compute_edca_multiplier(
            price=metrics.current_price,
            ema200=metrics.ema200,
            dd_pct=metrics.drawdown_pct,
            rsi=metrics.rsi14
        )
        grade, signal = assign_grade(multiplier, metrics.rsi14, metrics.drawdown_pct)
        
        opportunities.append(Opportunity(
            ticker=ticker,
            symbol=metrics.symbol,
            current_price=metrics.current_price,
            drawdown_pct=metrics.drawdown_pct,
            rsi14=metrics.rsi14,
            ema200=metrics.ema200,
            multiplier=multiplier,
            grade=grade,
            signal=signal
        ))
        
    # Sort descending by multiplier (best discounts first)
    opportunities.sort(key=lambda x: (x.multiplier, -x.rsi14), reverse=True)
    return opportunities
