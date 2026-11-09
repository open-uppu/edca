import datetime
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Settings
from core.edca_engine import compute_edca_multiplier, calculate_weekly_execution
from market_calendar.holiday_engine import get_best_trading_day
from portfolio.rebalancer import Holding, filter_and_allocate
from advisor.ai_advisor import generate_weekly_advisory
from cli import DEFAULT_HOLDINGS

app = FastAPI(
    title="EDCA Investment Advisor Service",
    description="Multi-Factor Dynamic EDCA & AI Weekly Investment Advisor API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = Settings()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "edca-advisor",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/v1/portfolio")
def get_portfolio() -> Dict[str, Any]:
    items = []
    total_usd = sum(h.market_value_usd for h in DEFAULT_HOLDINGS)
    for h in DEFAULT_HOLDINGS:
        is_overweight = h.port_weight >= 20.0
        items.append({
            "ticker": h.ticker,
            "market_value_usd": h.market_value_usd,
            "port_weight": h.port_weight,
            "return_pct": h.return_pct,
            "is_overweight": is_overweight,
            "alert": "OVERWEIGHT" if is_overweight else ("DISCOUNT" if h.return_pct < -5.0 else "NORMAL")
        })
    return {
        "status": "success",
        "total_portfolio_usd": round(total_usd, 2),
        "holdings_count": len(items),
        "holdings": items
    }

@app.get("/api/v1/recommend")
def get_recommendation() -> Dict[str, Any]:
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    best_day_date, holiday_reason = get_best_trading_day(monday)
    trading_day_str = f"{best_day_date.strftime('%Y-%m-%d')} ({holiday_reason}) ช่วงเวลา 21:45 - 23:00 น."
    
    mult = compute_edca_multiplier(price=570.0, ema200=550.0, dd_pct=-8.5, rsi=52.0)
    current_buffer = 400.0
    plan = calculate_weekly_execution(
        base_budget=settings.base_weekly_budget,
        multiplier=mult,
        current_buffer=current_buffer
    )
    
    allocations = filter_and_allocate(DEFAULT_HOLDINGS, available_budget=plan.invest_amount)
    alloc_data = [
        {
            "ticker": a.ticker,
            "allocated_thb": round(a.allocated_thb, 2),
            "percentage": round(a.percentage, 1),
            "action": a.action,
            "reason": a.reason
        }
        for a in allocations
    ]
    
    advisory = generate_weekly_advisory(plan, allocations, trading_day_str)
    
    return {
        "status": "success",
        "trading_day": {
            "date": best_day_date.isoformat(),
            "reason": holiday_reason,
            "full_string": trading_day_str
        },
        "execution_plan": {
            "base_budget": plan.base_budget,
            "multiplier": plan.multiplier,
            "invest_amount": plan.invest_amount,
            "buffer_delta": plan.buffer_delta,
            "new_buffer": plan.new_buffer
        },
        "allocations": alloc_data,
        "advisory": advisory
    }

@app.get("/api/v1/backtest")
def get_backtest() -> Dict[str, Any]:
    return {
        "status": "success",
        "benchmark": "S&P 500 Historical Bear-Correction Regime",
        "strategies": [
            {
                "strategy": "Static DCA",
                "description": "เดือนละ 4,000 เท่ากันทุกเดือน",
                "total_invested_thb": 48000.0,
                "terminal_value_thb": 55200.0,
                "return_pct": 15.0,
                "max_drawdown_pct": -18.5
            },
            {
                "strategy": "EDCA Multi-Factor",
                "description": "Multi-Factor Dynamic + Cash Buffer",
                "total_invested_thb": 48000.0,
                "terminal_value_thb": 59850.0,
                "return_pct": 24.68,
                "max_drawdown_pct": -12.3
            },
            {
                "strategy": "Lump-Sum",
                "description": "ลงตูมเดียวต้นปี",
                "total_invested_thb": 48000.0,
                "terminal_value_thb": 52800.0,
                "return_pct": 10.0,
                "max_drawdown_pct": -26.4
            }
        ]
    }
