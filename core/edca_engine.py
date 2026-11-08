from dataclasses import dataclass

@dataclass
class ExecutionPlan:
    base_budget: float
    multiplier: float
    invest_amount: float
    buffer_delta: float
    new_buffer: float

def compute_edca_multiplier(price: float, ema200: float, dd_pct: float, rsi: float) -> float:
    """
    Compute dynamic EDCA multiplier Mt in range [0.5, 2.0].
    Mt = 1.0 + Delta_Trend + Delta_Drawdown + Delta_RSI
    """
    # Factor 1: Trend
    delta_trend = -0.15 if price >= ema200 else 0.20
    
    # Factor 2: Drawdown from ATH
    if dd_pct >= -5.0:
        delta_dd = -0.15
    elif -15.0 <= dd_pct < -5.0:
        delta_dd = 0.00
    elif -25.0 <= dd_pct < -15.0:
        delta_dd = 0.25
    elif -35.0 <= dd_pct < -25.0:
        delta_dd = 0.50
    else:
        delta_dd = 0.75
        
    # Factor 3: RSI
    if rsi > 70.0:
        delta_rsi = -0.20
    elif 45.0 <= rsi <= 70.0:
        delta_rsi = 0.00
    elif 30.0 <= rsi < 45.0:
        delta_rsi = 0.15
    else:
        delta_rsi = 0.35
        
    raw_m = 1.0 + delta_trend + delta_dd + delta_rsi
    return round(max(0.5, min(2.0, raw_m)), 2)

def calculate_weekly_execution(base_budget: float, multiplier: float, current_buffer: float) -> ExecutionPlan:
    """Calculate actual investment amount and new cash buffer balance."""
    target_invest = base_budget * multiplier
    
    if target_invest <= base_budget:
        surplus = base_budget - target_invest
        return ExecutionPlan(
            base_budget=base_budget,
            multiplier=multiplier,
            invest_amount=target_invest,
            buffer_delta=surplus,
            new_buffer=current_buffer + surplus
        )
    else:
        needed = target_invest - base_budget
        draw = min(needed, current_buffer)
        actual_invest = base_budget + draw
        return ExecutionPlan(
            base_budget=base_budget,
            multiplier=multiplier,
            invest_amount=actual_invest,
            buffer_delta=-draw,
            new_buffer=current_buffer - draw
        )
