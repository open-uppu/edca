from core.edca_engine import ExecutionPlan
from portfolio.rebalancer import AssetAllocation
from advisor.ai_advisor import generate_weekly_advisory, fallback_heuristic_advisory

def test_fallback_heuristic_advisory():
    plan = ExecutionPlan(
        base_budget=1000.0,
        multiplier=1.2,
        invest_amount=1200.0,
        buffer_delta=-200.0,
        new_buffer=800.0
    )
    allocations = [
        AssetAllocation("GOOGL", 720.0, 60.0, "BUY", "Discount -7%"),
        AssetAllocation("TSLA", 480.0, 40.0, "BUY", "Discount -8%"),
    ]
    advice = fallback_heuristic_advisory(plan, allocations, "วันพุธ 21:45 น.")
    assert "1,200" in advice
    assert "GOOGL" in advice
    assert "TSLA" in advice
