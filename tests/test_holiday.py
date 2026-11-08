import datetime
from market_calendar.holiday_engine import is_us_holiday, is_thai_holiday, get_best_trading_day

def test_known_us_holiday():
    # Christmas 2026-12-25
    assert is_us_holiday(datetime.date(2026, 12, 25)) is True
    # Normal day (Tuesday 2026-11-10)
    assert is_us_holiday(datetime.date(2026, 11, 10)) is False

def test_known_thai_holiday():
    # Songkran 2026-04-13
    assert is_thai_holiday(datetime.date(2026, 4, 13)) is True
    # Normal day
    assert is_thai_holiday(datetime.date(2026, 11, 10)) is False

def test_holiday_shift_to_tuesday():
    # Monday 2026-11-09, Wed 2026-11-11 is normal
    best_day, reason = get_best_trading_day(datetime.date(2026, 11, 9))
    assert best_day.weekday() in [1, 2]  # Tuesday (1) or Wednesday (2)
