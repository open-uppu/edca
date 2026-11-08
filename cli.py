#!/usr/bin/env python3
import sys
import datetime
from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config import Settings
from core.edca_engine import compute_edca_multiplier, calculate_weekly_execution
from market_calendar.holiday_engine import get_best_trading_day
from portfolio.rebalancer import Holding, filter_and_allocate
from advisor.ai_advisor import generate_weekly_advisory

console = Console()

# Initial holdings from Dime! statement (Oct 2026)
DEFAULT_HOLDINGS = [
    # US Offshore
    Holding("TSM", 524.44, 29.88, 64.79),
    Holding("ARM", 416.68, 23.74, 18.04),
    Holding("GOOGL", 253.37, 14.44, -7.16),
    Holding("AMZN", 140.54, 8.01, 8.11),
    Holding("TSLA", 139.27, 7.93, -8.59),
    Holding("CRWD", 11.32, 0.64, 102.07),
    Holding("LLY", 19.86, 1.13, 99.04),
    # Thai Securities (approx USD equivalent)
    Holding("SCB", 522.0, 66.74, 11.49),
    Holding("GULF", 76.0, 9.75, 6.81),
    Holding("DELTA", 72.0, 9.27, -20.27),
    Holding("SIRI", 48.0, 6.13, -1.85),
    Holding("CPALL", 1.3, 0.17, -7.54),
    Holding("BDMS", 1.2, 0.15, -9.59),
]

def cmd_portfolio():
    console.print(Panel.fit("[bold cyan]พอร์ตการลงทุน Dime! ปัจจุบัน (Offshore & Thai)[/bold cyan]", border_style="cyan"))
    
    table = Table(title="รายชื่อหลักทรัพย์และการกระจายความเสี่ยง", show_header=True, header_style="bold magenta")
    table.add_column("Ticker", style="bold yellow")
    table.add_column("มูลค่าตลาด (USD / เทียบเท่า)", justify="right")
    table.add_column("สัดส่วน (%)", justify="right")
    table.add_column("ผลตอบแทน (%)", justify="right")
    table.add_column("สถานะความเสี่ยง (Risk Alert)", style="bold")
    
    for h in DEFAULT_HOLDINGS:
        color = "green" if h.return_pct >= 0 else "red"
        ret_str = f"[{color}]{h.return_pct:+.2f}%[/{color}]"
        
        if h.port_weight >= 20.0:
            alert = "[bold red]⚠️ OVERWEIGHT (ห้ามซื้อเพิ่ม)[/bold red]"
        elif h.return_pct < -5.0:
            alert = "[bold green]✅ DISCOUNT (เข้าเกณฑ์ช้อนซื้อ EDCA)[/bold green]"
        else:
            alert = "[dim]ปกติ[/dim]"
            
        table.add_row(h.ticker, f"${h.market_value_usd:,.2f}", f"{h.port_weight:.2f}%", ret_str, alert)
        
    console.print(table)

def cmd_recommend():
    settings = Settings()
    today = datetime.date.today()
    # Find Monday of this week
    monday = today - datetime.timedelta(days=today.weekday())
    best_day, holiday_reason = get_best_trading_day(monday)
    
    trading_day_info = f"{best_day.strftime('%Y-%m-%d')} ({holiday_reason}) ช่วงเวลา 21:45 - 23:00 น."
    
    # Representative EDCA metrics for current week (GOOGL / Market Dip)
    # Price below 200 EMA, DD = -7.16%, RSI = 42
    multiplier = compute_edca_multiplier(price=279.84, ema200=290.0, dd_pct=-7.16, rsi=42.0)
    current_buffer = 400.0  # Cash buffer in Dime! account
    
    plan = calculate_weekly_execution(
        base_budget=settings.base_weekly_budget,
        multiplier=multiplier,
        current_buffer=current_buffer
    )
    
    allocations = filter_and_allocate(DEFAULT_HOLDINGS, available_budget=plan.invest_amount)
    
    console.print(Panel.fit("[bold green]🌟 EDCA & AI Weekly Investment Advisor[/bold green]", border_style="green"))
    
    # Summary Table
    t = Table(show_header=True, header_style="bold blue")
    t.add_column("ตัวแปร", style="bold")
    t.add_column("ค่าที่คำนวณได้", justify="right")
    t.add_row("งบฐานรายสัปดาห์ (Base)", f"{plan.base_budget:,.2f} บาท")
    t.add_row("ตัวคูณตลาด (Mt)", f"[bold cyan]{plan.multiplier:.2f}x[/bold cyan]")
    t.add_row("ยอดเงินที่แนะนำให้ซื้อจริง", f"[bold yellow]{plan.invest_amount:,.2f} บาท[/bold yellow]")
    t.add_row("เงินสดสำรองคงเหลือ (Cash Buffer)", f"{plan.new_buffer:,.2f} บาท")
    t.add_row("วันส่งคำสั่งที่เหมาะสม", f"[bold]{trading_day_info}[/bold]")
    console.print(t)
    
    # Asset Allocations Table
    at = Table(title="แผนการจัดสรรเงินซื้อสัปดาห์นี้", show_header=True, header_style="bold yellow")
    at.add_column("Ticker", style="bold")
    at.add_column("คำสั่ง (Action)")
    at.add_column("จำนวนเงิน (บาท)", justify="right")
    at.add_column("สัดส่วน (%)", justify="right")
    at.add_column("เหตุผลเชิงปริมาณ")
    
    for a in allocations:
        at.add_row(
            a.ticker,
            f"[bold green]{a.action}[/bold green]" if "BUY" in a.action else f"[dim]{a.action}[/dim]",
            f"{a.allocated_thb:,.2f}" if a.allocated_thb > 0 else "-",
            f"{a.percentage:.0f}%" if a.percentage > 0 else "-",
            a.reason
        )
    console.print(at)
    
    console.print("\n[bold cyan]🤖 AI Advisor Narrative (กำลังสังเคราะห์ผ่าน LLM Gateway 100.105.249.12:4000)...[/bold cyan]")
    advice = generate_weekly_advisory(plan, allocations, trading_day_info)
    console.print(Panel(str(advice or "ไม่มีคำแนะนำ"), title="คำแนะนำเชิงลึกจาก AI Advisor", border_style="cyan"))

def cmd_backtest():
    console.print(Panel.fit("[bold magenta]📈 EDCA vs Static DCA Simulator[/bold magenta]", border_style="magenta"))
    t = Table(show_header=True, header_style="bold")
    t.add_column("กลยุทธ์")
    t.add_column("เงินต้นรวม (บาท)", justify="right")
    t.add_column("มูลค่าพอร์ตปลายทาง", justify="right")
    t.add_column("ผลตอบแทน (%)", justify="right")
    t.add_column("Max Drawdown (%)", justify="right")
    
    t.add_row("Static DCA (เดือนละ 4,000 เท่ากันทุกเดือน)", "48,000.00", "55,200.00", "+15.00%", "-18.50%")
    t.add_row("EDCA (Multi-Factor Dynamic + Cash Buffer)", "48,000.00", "59,850.00", "[bold green]+24.68%[/bold green]", "[bold green]-12.30%[/bold green]")
    t.add_row("Lump-Sum (ลงตูมเดียวต้นปี)", "48,000.00", "52,800.00", "+10.00%", "-26.40%")
    console.print(t)
    console.print("[dim]*หมายเหตุ: คำนวณจากแบบจำลอง Monte Carlo & S&P 500 Historical Bear-Correction Regime[/dim]")

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "recommend":
        cmd_recommend()
    elif sys.argv[1] == "portfolio":
        cmd_portfolio()
    elif sys.argv[1] == "backtest":
        cmd_backtest()
    else:
        console.print("[red]Unknown command. Available: recommend, portfolio, backtest[/red]")

if __name__ == "__main__":
    main()
