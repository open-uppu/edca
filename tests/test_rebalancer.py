from portfolio.rebalancer import Holding, AssetAllocation, filter_and_allocate, MIN_ORDER_THB

def test_suppress_overweight_assets():
    holdings = [
        Holding(ticker="TSM", market_value_usd=524.0, port_weight=29.88, return_pct=64.79),
        Holding(ticker="ARM", market_value_usd=416.0, port_weight=23.74, return_pct=18.04),
        Holding(ticker="GOOGL", market_value_usd=253.0, port_weight=14.44, return_pct=-7.16),
        Holding(ticker="TSLA", market_value_usd=139.0, port_weight=7.93, return_pct=-8.59),
    ]
    allocations = filter_and_allocate(holdings, available_budget=1000.0)
    
    # TSM & ARM must have 0 allocation
    tsm_alloc = next(a for a in allocations if a.ticker == "TSM")
    arm_alloc = next(a for a in allocations if a.ticker == "ARM")
    googl_alloc = next(a for a in allocations if a.ticker == "GOOGL")
    tsla_alloc = next(a for a in allocations if a.ticker == "TSLA")
    
    assert tsm_alloc.allocated_thb == 0.0
    assert arm_alloc.allocated_thb == 0.0
    assert googl_alloc.allocated_thb >= MIN_ORDER_THB
    assert tsla_alloc.allocated_thb >= MIN_ORDER_THB


def test_min_order_threshold_under_50():
    holdings = [
        Holding(ticker="GOOGL", market_value_usd=253.0, port_weight=14.44, return_pct=-7.16),
        Holding(ticker="TSLA", market_value_usd=139.0, port_weight=7.93, return_pct=-8.59),
    ]
    # Budget 40 THB is below 50 THB Dime! minimum
    allocations = filter_and_allocate(holdings, available_budget=40.0)
    assert len(allocations) == 2
    for a in allocations:
        assert a.allocated_thb == 0.0
        assert "UNDER MIN ORDER" in a.action


def test_min_order_threshold_consolidation_under_100():
    holdings = [
        Holding(ticker="GOOGL", market_value_usd=253.0, port_weight=14.44, return_pct=-7.16),
        Holding(ticker="TSLA", market_value_usd=139.0, port_weight=7.93, return_pct=-8.59),
    ]
    # Budget 80 THB: cannot split 2 * 50 THB, so top candidate gets all 80 THB
    allocations = filter_and_allocate(holdings, available_budget=80.0)
    tsla_alloc = next(a for a in allocations if a.ticker == "TSLA")
    googl_alloc = next(a for a in allocations if a.ticker == "GOOGL")

    assert tsla_alloc.allocated_thb == 80.0
    assert tsla_alloc.percentage == 100.0
    assert googl_alloc.allocated_thb == 0.0


def test_min_order_threshold_split_above_100():
    holdings = [
        Holding(ticker="GOOGL", market_value_usd=253.0, port_weight=14.44, return_pct=-7.16),
        Holding(ticker="TSLA", market_value_usd=139.0, port_weight=7.93, return_pct=-8.59),
    ]
    # Budget 110 THB: 40% would be 44 (< 50), so it should clamp to minimum 50 THB
    allocations = filter_and_allocate(holdings, available_budget=110.0)
    tsla_alloc = next(a for a in allocations if a.ticker == "TSLA")
    googl_alloc = next(a for a in allocations if a.ticker == "GOOGL")

    assert googl_alloc.allocated_thb >= 50.0
    assert tsla_alloc.allocated_thb >= 50.0
    assert round(tsla_alloc.allocated_thb + googl_alloc.allocated_thb, 2) == 110.0


def test_new_stock_opportunity_allocation():
    holdings = [
        Holding(ticker="TSLA", market_value_usd=139.0, port_weight=7.93, return_pct=-8.59),
    ]
    opportunities = [
        {"ticker": "NVDA", "grade": "A+", "multiplier": 1.75, "drawdown_pct": -18.5},
        {"ticker": "AAPL", "grade": "B", "multiplier": 1.05, "drawdown_pct": -3.2},
    ]
    # NVDA is a new stock with Grade A+, should be allocated as NEW ENTRY
    allocations = filter_and_allocate(holdings, available_budget=1000.0, opportunities=opportunities)
    nvda_alloc = next((a for a in allocations if a.ticker == "NVDA"), None)
    assert nvda_alloc is not None
    assert nvda_alloc.action == "NEW ENTRY (BUY)"
    assert nvda_alloc.allocated_thb >= 50.0
