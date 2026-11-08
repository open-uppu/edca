import datetime
from typing import Tuple, Set

# Key fixed & predictable US Market (NYSE) Holidays
US_HOLIDAYS_FIXED: Set[Tuple[int, int]] = {
    (1, 1),   # New Year's Day
    (6, 19),  # Juneteenth
    (7, 4),   # Independence Day
    (12, 25), # Christmas Day
}

# Key Thai SET Holidays
THAI_HOLIDAYS_FIXED: Set[Tuple[int, int]] = {
    (1, 1),   # New Year
    (4, 13),  # Songkran
    (4, 14),  # Songkran
    (4, 15),  # Songkran
    (5, 1),   # Labour Day
    (7, 28),  # King's Birthday
    (8, 12),  # Mother's Day
    (10, 13), # Memorial Day
    (10, 23), # Chulalongkorn Day
    (12, 5),  # Father's Day
    (12, 31), # New Year's Eve
}

def is_us_holiday(d: datetime.date) -> bool:
    if d.weekday() >= 5:  # Saturday or Sunday
        return True
    if (d.month, d.day) in US_HOLIDAYS_FIXED:
        return True
    # Thanksgiving: 4th Thursday of November
    if d.month == 11 and d.weekday() == 3:
        if 22 <= d.day <= 28:
            return True
    return False

def is_thai_holiday(d: datetime.date) -> bool:
    if d.weekday() >= 5:
        return True
    return (d.month, d.day) in THAI_HOLIDAYS_FIXED

def get_best_trading_day(monday_date: datetime.date) -> Tuple[datetime.date, str]:
    """Given Monday of the week, choose the optimal trading day (Wednesday or Tuesday fallback)."""
    wednesday = monday_date + datetime.timedelta(days=2)
    tuesday = monday_date + datetime.timedelta(days=1)
    thursday = monday_date + datetime.timedelta(days=3)
    
    if not is_us_holiday(wednesday) and not is_thai_holiday(wednesday):
        return wednesday, "วันพุธ (สภาวะตลาดและสภาพคล่องปกติ)"
    elif not is_us_holiday(tuesday) and not is_thai_holiday(tuesday):
        return tuesday, "วันอังคาร (ขยับขึ้นมาเนื่องจากวันพุธตรงกับวันหยุดตลาด)"
    elif not is_us_holiday(thursday) and not is_thai_holiday(thursday):
        return thursday, "วันพฤหัสบดี (ขยับถัดไปเนื่องจากต้นสัปดาห์มีวันหยุด)"
    return tuesday, "วันอังคาร (วันทำการปกติ)"
