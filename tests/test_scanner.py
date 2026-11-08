import pytest
from portfolio.market_scanner import scan_market_opportunities, Opportunity, WATCHLIST_LEADERS

def test_watchlist_has_core_assets():
    assert "NVDA" in WATCHLIST_LEADERS
    assert "META" in WATCHLIST_LEADERS
    assert "VOO" in WATCHLIST_LEADERS
    assert "CPALL.BK" in WATCHLIST_LEADERS

def test_scan_market_opportunities():
    # Test scanner on a mini subset
    mini_list = ["NVDA", "AAPL", "VOO"]
    opps = scan_market_opportunities(mini_list)
    assert len(opps) == 3
    # Check attributes
    for o in opps:
        assert isinstance(o, Opportunity)
        assert o.ticker in mini_list
        assert o.current_price > 0.0
        assert o.multiplier >= 0.5
        assert o.grade in ["A+", "A", "B", "C"]
    # Check sorted descending by multiplier
    assert opps[0].multiplier >= opps[-1].multiplier
