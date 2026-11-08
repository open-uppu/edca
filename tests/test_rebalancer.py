from portfolio.rebalancer import Holding, filter_and_allocate

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
    
    assert tsm_alloc.allocated_thb == 0.0
    assert arm_alloc.allocated_thb == 0.0
    assert googl_alloc.allocated_thb > 0.0
