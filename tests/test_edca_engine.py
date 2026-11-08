from core.edca_engine import compute_edca_multiplier, calculate_weekly_execution, ExecutionPlan

def test_edca_multiplier_bull_overbought():
    # Bull market (price > EMA), ATH (dd = 0), RSI = 75
    # M = 1.0 - 0.15 - 0.15 - 0.20 = 0.50
    m = compute_edca_multiplier(price=150.0, ema200=100.0, dd_pct=0.0, rsi=75.0)
    assert m == 0.5

def test_edca_multiplier_panic_crash():
    # Bear market (price < EMA), DD = -40%, RSI = 20
    # M = 1.0 + 0.20 + 0.75 + 0.35 = 2.30 -> Clamped to 2.0
    m = compute_edca_multiplier(price=60.0, ema200=100.0, dd_pct=-40.0, rsi=20.0)
    assert m == 2.0

def test_cash_buffer_accumulate_on_low_multiplier():
    # Base 1000, M = 0.5 -> Invest 500, +500 to buffer
    plan = calculate_weekly_execution(base_budget=1000.0, multiplier=0.5, current_buffer=200.0)
    assert plan.invest_amount == 500.0
    assert plan.buffer_delta == 500.0
    assert plan.new_buffer == 700.0

def test_cash_buffer_draw_on_high_multiplier():
    # Base 1000, M = 1.6 -> Desired 1600, draw 600 from buffer
    plan = calculate_weekly_execution(base_budget=1000.0, multiplier=1.6, current_buffer=1000.0)
    assert plan.invest_amount == 1600.0
    assert plan.buffer_delta == -600.0
    assert plan.new_buffer == 400.0
