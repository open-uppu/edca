from dataclasses import dataclass
from typing import List

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

def filter_and_allocate(holdings: List[Holding], available_budget: float) -> List[AssetAllocation]:
    """Allocate available budget prioritizing discounted quality assets while protecting against overconcentration."""
    results: List[AssetAllocation] = []
    eligible_candidates = []
    
    for h in holdings:
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
            eligible_candidates.append(h)
            
    if not eligible_candidates:
        return results
        
    # Sort eligible by discount (most negative return first)
    eligible_candidates.sort(key=lambda x: x.return_pct)
    
    # Take top 2 candidates
    top_candidates = eligible_candidates[:2]
    weights = [0.60, 0.40] if len(top_candidates) == 2 else [1.0]
    
    for i, candidate in enumerate(top_candidates):
        allocated = round(available_budget * weights[i], 2)
        results.append(AssetAllocation(
            ticker=candidate.ticker,
            allocated_thb=allocated,
            percentage=weights[i] * 100.0,
            action="ACCUMULATE (BUY)",
            reason=f"โซนของลดราคา (ผลตอบแทนติดลบ {candidate.return_pct:.1f}% เข้าเกณฑ์ EDCA Discount)"
        ))
        
    return results
