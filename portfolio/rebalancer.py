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
    min_order_thb: float = MIN_ORDER_THB,
    max_assets: Optional[int] = None
) -> List[AssetAllocation]:
    """
    Dynamically ranks and allocates budget across high-probability discounted assets
    while strictly protecting against concentration risk and enforcing Dime!'s 50 THB rule.
    Scales the number of assets dynamically based on available budget (up to 5 assets).
    """
    results: List[AssetAllocation] = []
    eligible_pool: List[dict] = []
    existing_tickers = set()

    # 1. Stage 1: Concentration Risk Filtering (Overweight Guard)
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
            discount = abs(min(0.0, h.return_pct))
            eligible_pool.append({
                "ticker": h.ticker,
                "return_pct": h.return_pct,
                "discount_score": discount,
                "is_new": False,
                "tag": f"หุ้นเดิมโซนลดราคา (Drawdown {h.return_pct:+.1f}%)"
            })

    # 2. Stage 2: Ingest High-Moat New Stock Opportunities from Market Scanner (Grade A+ or A)
    if opportunities:
        for opp in opportunities:
            ticker = getattr(opp, "ticker", None) or (opp.get("ticker") if isinstance(opp, dict) else "")
            grade = getattr(opp, "grade", None) or (opp.get("grade") if isinstance(opp, dict) else "")
            mult = getattr(opp, "multiplier", 1.0) or (opp.get("multiplier", 1.0) if isinstance(opp, dict) else 1.0)
            dd = getattr(opp, "drawdown_pct", 0.0) or (opp.get("drawdown_pct", 0.0) if isinstance(opp, dict) else 0.0)
            clean_ticker = ticker.replace(".BK", "")

            if clean_ticker not in existing_tickers and ticker not in existing_tickers:
                if grade in ("A+", "A") or mult >= 1.30:
                    discount = abs(min(0.0, dd))
                    eligible_pool.append({
                        "ticker": clean_ticker,
                        "return_pct": dd,
                        "discount_score": discount,
                        "is_new": True,
                        "tag": f"หุ้นใหม่เรดาร์ A ({grade}) (Drawdown {dd:+.1f}%, Mt {mult:.2f}x)"
                    })

    if not eligible_pool:
        return results

    # 3. Stage 3: Unified Leaderboard Ranking (Sorted by Discount Depth)
    # Higher discount score = Higher priority rank
    eligible_pool.sort(key=lambda x: x["discount_score"], reverse=True)

    # 4. Stage 4: Check Minimum Order Threshold (50 THB)
    if available_budget < min_order_thb:
        for rank_idx, item in enumerate(eligible_pool, start=1):
            results.append(AssetAllocation(
                ticker=item["ticker"],
                allocated_thb=0.0,
                percentage=0.0,
                action="SKIP (UNDER MIN ORDER)",
                reason=f"อันดับ #{rank_idx}: {item['tag']} (งบรวมสัปดาห์นี้ {available_budget:.2f} บ. ต่ำกว่าเกณฑ์ขั้นต่ำ {min_order_thb:.0f} บ. ของ Dime!)"
            ))
        return results

    # 5. Stage 5: Dynamic Slots (K) Determination based on Budget Size
    # Automatically chooses how many stocks to allocate to maximize diversification without over-fragmentation
    if max_assets is not None:
        k = max(1, min(max_assets, len(eligible_pool)))
    elif available_budget < (2 * min_order_thb):  # < 100 THB -> 1 slot
        k = 1
    elif available_budget < 600.0:                # 100 - 599 THB -> 2 slots
        k = 2
    elif available_budget < 1500.0:               # 600 - 1,499 THB -> 3 slots
        k = 3
    elif available_budget < 3000.0:               # 1,500 - 2,999 THB -> 4 slots
        k = 4
    else:                                         # >= 3,000 THB -> 5 slots
        k = 5

    k = min(k, len(eligible_pool))

    # Guard: Ensure budget can cover at least (k * min_order_thb)
    while k > 1 and (available_budget / k) < min_order_thb:
        k -= 1

    # 6. Stage 6: Weight Profiles
    weight_profiles = {
        1: [1.0],
        2: [0.60, 0.40],
        3: [0.45, 0.35, 0.20],
        4: [0.35, 0.25, 0.22, 0.18],
        5: [0.30, 0.24, 0.18, 0.15, 0.13]
    }
    weights = weight_profiles.get(k, [1.0 / k] * k)

    # 7. Stage 7: Exact Allocation & Dime! 50 THB Minimum Enforcement
    allocated_candidates = eligible_pool[:k]
    alloc_amts = [round(available_budget * w, 2) for w in weights]

    # Enforce minimum order threshold for all slots
    for i in range(k):
        if alloc_amts[i] < min_order_thb:
            alloc_amts[i] = min_order_thb

    # Ensure sum matches available_budget exactly without violating min_order_thb
    diff = round(available_budget - sum(alloc_amts), 2)
    if diff != 0:
        if alloc_amts[0] + diff >= min_order_thb:
            alloc_amts[0] = round(alloc_amts[0] + diff, 2)
        else:
            alloc_amts[0] = round(available_budget - sum(alloc_amts[1:]), 2)

    for i, item in enumerate(allocated_candidates):
        rank = i + 1
        order_amt = alloc_amts[i]
        pct = round((order_amt / available_budget) * 100.0, 1)
        action_name = "NEW ENTRY (BUY)" if item["is_new"] else "ACCUMULATE (BUY)"

        results.append(AssetAllocation(
            ticker=item["ticker"],
            allocated_thb=order_amt,
            percentage=pct,
            action=action_name,
            reason=f"อันดับ #{rank}: {item['tag']}"
        ))

    # 8. Stage 8: Remaining Queue / Watchlist Items (Unallocated this week)
    queue_candidates = eligible_pool[k:]
    for i, item in enumerate(queue_candidates, start=k + 1):
        results.append(AssetAllocation(
            ticker=item["ticker"],
            allocated_thb=0.0,
            percentage=0.0,
            action="QUEUE (NEXT WEEK)",
            reason=f"อันดับ #{i}: {item['tag']} (รอคิวจัดสรรในสัปดาห์ถัดไป)"
        ))

    return results
