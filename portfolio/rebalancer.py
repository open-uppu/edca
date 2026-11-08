from dataclasses import dataclass
from typing import List, Optional, Any

MIN_ORDER_THB: float = 50.0

@dataclass
class Holding:
    ticker: str
    market_value_usd: float
    port_weight: float
    return_pct: float

@dataclass
class AssetAllocation:
    ticker: str
    allocated_thb: float
    percentage: float
    action: str
    reason: str


def filter_and_allocate(
    holdings: List[Holding],
    available_budget: float,
    opportunities: Optional[List[Any]] = None,
    min_order_thb: float = MIN_ORDER_THB
) -> List[AssetAllocation]:
    """
    Allocate available budget prioritizing discounted quality assets while protecting
    against overconcentration and enforcing Dime! minimum order threshold (50 THB).
    Also supports introducing high-grade new stock opportunities from Market Scanner.
    """
    results: List[AssetAllocation] = []
    eligible_candidates: List[dict] = []
    existing_tickers = set()

    for h in holdings:
        existing_tickers.add(h.ticker)
        # Concentration rule: >=20% single US asset or >=40% single Thai asset is OVERWEIGHT
        if h.port_weight >= 20.0:
            results.append(AssetAllocation(
                ticker=h.ticker,
                allocated_thb=0.0,
                percentage=0.0,
                action="HOLD / RUN PROFIT",
                reason=f"สัดส่วนในพอร์ตล้นเกินเกณฑ์ปลอดภัย ({h.port_weight:.1f}%)"
            ))
        else:
            eligible_candidates.append({
                "ticker": h.ticker,
                "return_pct": h.return_pct,
                "is_new": False,
                "reason_tag": f"โซนของลดราคา (ผลตอบแทนติดลบ {h.return_pct:.1f}% เข้าเกณฑ์ EDCA Discount)"
            })

    # Sort existing eligible candidates by discount (most negative return first)
    eligible_candidates.sort(key=lambda x: x["return_pct"])

    # Check for top-tier new stock opportunities from Market Scanner (Grade A+ or A)
    new_candidates: List[dict] = []
    if opportunities:
        for opp in opportunities:
            ticker = getattr(opp, "ticker", None) or (opp.get("ticker") if isinstance(opp, dict) else "")
            grade = getattr(opp, "grade", None) or (opp.get("grade") if isinstance(opp, dict) else "")
            mult = getattr(opp, "multiplier", 1.0) or (opp.get("multiplier", 1.0) if isinstance(opp, dict) else 1.0)
            dd = getattr(opp, "drawdown_pct", 0.0) or (opp.get("drawdown_pct", 0.0) if isinstance(opp, dict) else 0.0)
            clean_ticker = ticker.replace(".BK", "")

            if clean_ticker not in existing_tickers and ticker not in existing_tickers:
                if grade in ("A+", "A") or mult >= 1.30:
                    new_candidates.append({
                        "ticker": clean_ticker,
                        "return_pct": dd,  # Use drawdown as discount metric
                        "is_new": True,
                        "reason_tag": f"เปิดพอร์ตหุ้นใหม่เรดาร์ A ({grade}): Drawdown {dd:+.1f}%, ตัวคูณ Mt {mult:.2f}x"
                    })

        new_candidates.sort(key=lambda x: x["return_pct"])

    # Combine selection: prioritize top existing discounted holding + top new opportunity (or 2 existing)
    selected_pool: List[dict] = []
    if eligible_candidates:
        selected_pool.append(eligible_candidates[0])

    if new_candidates:
        # If there is a high-grade new opportunity, grant it the 2nd slot
        selected_pool.append(new_candidates[0])
    elif len(eligible_candidates) > 1:
        selected_pool.append(eligible_candidates[1])

    if not selected_pool:
        return results

    # Check Dime! minimum order threshold: 50 THB
    if available_budget < min_order_thb:
        for item in selected_pool:
            results.append(AssetAllocation(
                ticker=item["ticker"],
                allocated_thb=0.0,
                percentage=0.0,
                action="SKIP (UNDER MIN ORDER)",
                reason=f"งบลงทุนสัปดาห์นี้ ({available_budget:.2f} บาท) ต่ำกว่าขั้นต่ำ {min_order_thb:.0f} บาทของ Dime! แนะนำทบเข้า Cash Buffer"
            ))
        return results

    # Budget Allocation with Minimum Order Size Guard
    # If budget cannot cover 2 orders of min_order_thb (e.g. budget < 100 THB), allocate 100% to top candidate
    if len(selected_pool) == 1 or available_budget < (2 * min_order_thb):
        top = selected_pool[0]
        action_prefix = "NEW ENTRY (BUY)" if top.get("is_new") else "ACCUMULATE (BUY)"
        results.append(AssetAllocation(
            ticker=top["ticker"],
            allocated_thb=round(available_budget, 2),
            percentage=100.0,
            action=action_prefix,
            reason=f"{top['reason_tag']} (รวมงบเป็น 1 ไม้ตามเกณฑ์ขั้นต่ำ Dime! {min_order_thb:.0f} บาท)" if len(selected_pool) > 1 else top['reason_tag']
        ))
        if len(selected_pool) > 1:
            second = selected_pool[1]
            results.append(AssetAllocation(
                ticker=second["ticker"],
                allocated_thb=0.0,
                percentage=0.0,
                action="SKIP (BUDGET CONSOLIDATION)",
                reason=f"งบไม่พอแบ่ง 2 ไม้ให้ถึงขั้นต่ำ {min_order_thb:.0f} บาทต่อไม้ (ยกยอดไปให้ {top['ticker']})"
            ))
    else:
        # Both can receive at least min_order_thb
        first = selected_pool[0]
        second = selected_pool[1]

        # Ideal split: 60% / 40%
        first_amt = round(available_budget * 0.60, 2)
        second_amt = round(available_budget * 0.40, 2)

        # Enforce that second_amt is at least min_order_thb
        if second_amt < min_order_thb:
            second_amt = min_order_thb
            first_amt = round(available_budget - second_amt, 2)

        first_pct = round((first_amt / available_budget) * 100.0, 1)
        second_pct = round((second_amt / available_budget) * 100.0, 1)

        first_act = "NEW ENTRY (BUY)" if first.get("is_new") else "ACCUMULATE (BUY)"
        second_act = "NEW ENTRY (BUY)" if second.get("is_new") else "ACCUMULATE (BUY)"

        results.append(AssetAllocation(
            ticker=first["ticker"],
            allocated_thb=first_amt,
            percentage=first_pct,
            action=first_act,
            reason=first["reason_tag"]
        ))
        results.append(AssetAllocation(
            ticker=second["ticker"],
            allocated_thb=second_amt,
            percentage=second_pct,
            action=second_act,
            reason=second["reason_tag"]
        ))

    return results
