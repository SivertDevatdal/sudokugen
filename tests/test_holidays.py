"""Tests for the Norwegian printing calendar."""

import sys
from datetime import date

sys.path.insert(0, 'src')

from sudokugen.holidays import (
    easter_sunday, is_publishing_day, is_red_day, norwegian_red_days,
)


def test_easter_dates():
    assert easter_sunday(2024) == date(2024, 3, 31)
    assert easter_sunday(2025) == date(2025, 4, 20)
    assert easter_sunday(2026) == date(2026, 4, 5)
    assert easter_sunday(2027) == date(2027, 3, 28)


def test_2026_red_days():
    reds = norwegian_red_days(2026)
    assert len(reds) == 12
    for d in (date(2026, 1, 1), date(2026, 4, 2), date(2026, 4, 3),
              date(2026, 4, 5), date(2026, 4, 6), date(2026, 5, 1),
              date(2026, 5, 17), date(2026, 5, 14), date(2026, 5, 24),
              date(2026, 5, 25), date(2026, 12, 25), date(2026, 12, 26)):
        assert is_red_day(d), d


def test_publishing_day_rules():
    assert is_publishing_day(date(2026, 7, 25))       # Saturday, normal
    assert not is_publishing_day(date(2026, 7, 26))   # Sunday
    assert not is_publishing_day(date(2026, 5, 1))    # red day (Fri)
    assert not is_publishing_day(date(2026, 5, 17))   # red day on a Sunday
    assert is_publishing_day(date(2026, 5, 2))        # Saturday, normal


def test_no_red_days_in_current_batch():
    # The Jul 25 – Sep 25 2026 window has no red days (only Sundays).
    d = date(2026, 7, 25)
    while d <= date(2026, 9, 25):
        assert not is_red_day(d), d
        d = date.fromordinal(d.toordinal() + 1)
