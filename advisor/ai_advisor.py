import json
import requests
from config import Settings
from core.edca_engine import ExecutionPlan
from portfolio.rebalancer import AssetAllocation
from typing import List

def fallback_heuristic_advisory(plan: ExecutionPlan, allocations: List[AssetAllocation], trading_day_info: str) -> str:
    """Deterministic Thai advisory fallback when offline."""
    lines = [
        f"📊 **สรุปคำแนะนำการลงทุนประจำสัปดาห์ (EDCA System)**",
        f"• **วันและเวลาที่แนะนำให้ส่งคำสั่ง:** {trading_day_info}",
        f"• **งบลงทุนจริงสัปดาห์นี้:** {plan.invest_amount:,.2f} บาท (ตัวคูณ {plan.multiplier:.2f}x จากงบปกติ {plan.base_budget:,.2f} บาท)",
        f"• **สถานะกองเงินสดสำรอง (Cash Buffer):** {plan.new_buffer:,.2f} บาท (การเปลี่ยนแปลงงวดนี้: {plan.buffer_delta:+,.2f} บาท)",
        f"\n🎯 **การจัดสรรสินทรัพย์เป้าหมาย:**"
    ]
    for a in allocations:
        if a.allocated_thb > 0:
            lines.append(f"  - **{a.ticker}**: ซื้อ {a.allocated_thb:,.2f} บาท ({a.percentage:.0f}%) ➔ {a.reason}")
        else:
            lines.append(f"  - **{a.ticker}**: {a.action} ➔ {a.reason}")
    return "\n".join(lines)

def generate_weekly_advisory(plan: ExecutionPlan, allocations: List[AssetAllocation], trading_day_info: str) -> str:
    """Call LLM Gateway at 100.105.249.12:4000 to generate AI narrative, with fallback."""
    settings = Settings()
    prompt = (
        f"คุณคือ AI Quantitative Portfolio Advisor สำหรับระบบ EDCA\n"
        f"ข้อมูลประจำสัปดาห์:\n"
        f"- วันเทรดที่เหมาะสม: {trading_day_info}\n"
        f"- งบฐาน: {plan.base_budget} บาท, ตัวคูณ Mt: {plan.multiplier}x, งบที่ต้องใช้จริง: {plan.invest_amount} บาท\n"
        f"- Cash Buffer คงเหลือ: {plan.new_buffer} บาท\n"
        f"- รายการสินทรัพย์:\n" +
        "\n".join([f"  * {a.ticker}: {a.action} {a.allocated_thb} บาท ({a.reason})" for a in allocations]) +
        f"\nจงเขียนคำแนะนำการลงทุนประจำสัปดาห์เป็นภาษาไทยแบบกระชับ ชัดเจน น่าเชื่อถือ สไตล์มืออาชีพ มี bullet point ครบถ้วน"
    )
    
    try:
        resp = requests.post(
            f"{settings.llm_gateway_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1200,
                "temperature": 0.3
            },
            timeout=8.0
        )
        if resp.status_code == 200:
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if content and isinstance(content, str):
                return content.strip()
    except Exception:
        pass
        
    return fallback_heuristic_advisory(plan, allocations, trading_day_info)

def generate_scanner_advisory(opportunities: list) -> str:
    """Call LLM Gateway to generate an executive market discovery briefing for top discounted stocks."""
    settings = Settings()
    top_3 = opportunities[:3]
    opp_text = "\n".join([
        f"- {o.ticker}: ราคา ${o.current_price:,.2f}, ส่วนลดจาก ATH {o.drawdown_pct:.1f}%, RSI {o.rsi14:.1f}, เกรด {o.grade} ({o.signal})"
        for o in top_3
    ])
    prompt = (
        f"คุณคือ Senior Investment Strategist ด้าน EDCA Value Averaging\n"
        f"จากผลการสแกนตลาดวันนี้ พบหุ้นชั้นนำระดับโลก 3 ตัวที่กำลังลดราคาแรงและติดสัญญาณน่าซื้อที่สุด:\n"
        f"{opp_text}\n"
        f"จงวิเคราะห์สรุปคำแนะนำในรูปแบบ Bullet Point ภาษาไทยว่า ทำไมหุ้นเหล่านี้จึงเป็นโอกาสทองในการทยอยช้อนซื้อ (Buy on Dip) ในสัปดาห์นี้ ชี้จุดแข็งพื้นฐานและเหตุผลทางเทคนิค สั้นกระชับ ตรงประเด็น"
    )
    try:
        resp = requests.post(
            f"{settings.llm_gateway_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.3
            },
            timeout=8.0
        )
        if resp.status_code == 200:
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if content and isinstance(content, str):
                return content.strip()
    except Exception:
        pass
        
    return (
        f"🌟 **สรุปหุ้นเด่นในตลาดที่น่าสนใจช้อนซื้อสัปดาห์นี้ (EDCA Market Pick):**\n" +
        "\n".join([f"• **{o.ticker}** (เกรด {o.grade}): ย่อตัว {o.drawdown_pct:.1f}% จากจุดสูงสุดเดิม พร้อม RSI {o.rsi14:.1f} ➔ {o.signal}" for o in top_3])
    )
