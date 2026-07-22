"""Tests for the holiday-shift rescheduler."""

import sys
from datetime import date, timedelta

sys.path.insert(0, 'src')

from sudokugen.reschedule import next_publishing_day, plan_holiday_shift


def batch(start: date, n: int) -> list[date]:
    """A clean Mon–Sat batch: n printing days from `start`, no Sundays."""
    days, d = [], start
    while len(days) < n:
        if d.weekday() != 6:
            days.append(d)
        d += timedelta(days=1)
    return days


def test_next_publishing_day_skips_sundays():
    # 2026-08-01 is a Saturday; the next printing day is Monday the 3rd.
    assert next_publishing_day(date(2026, 8, 1)) == date(2026, 8, 3)
    # a plain weekday just advances by one
    assert next_publishing_day(date(2026, 8, 3)) == date(2026, 8, 4)


def test_next_publishing_day_skips_extra_holidays():
    assert next_publishing_day(
        date(2026, 8, 3), skip={date(2026, 8, 4)}) == date(2026, 8, 5)


def test_skip_date_with_no_file_is_noop():
    dates = batch(date(2026, 7, 27), 10)
    # a Sunday never has a file
    assert plan_holiday_shift(dates, date(2026, 8, 2)) == []
    # a date past the end has no file
    assert plan_holiday_shift(dates, date(2027, 1, 1)) == []


def test_skip_weekday_cascades_forward():
    dates = batch(date(2026, 7, 27), 6)  # Mon..Sat 27–1 Aug
    plan = plan_holiday_shift(dates, date(2026, 7, 29))  # skip Wed
    old = [o for o, _ in plan]
    new = [n for _, n in plan]
    # everything from Wednesday onward moves
    assert old == [date(2026, 7, 29), date(2026, 7, 30),
                   date(2026, 7, 31), date(2026, 8, 1)]
    # each slides into the next printing slot; the tail lands Monday
    assert new == [date(2026, 7, 30), date(2026, 7, 31),
                   date(2026, 8, 1), date(2026, 8, 3)]
    # the skipped date is now empty, no date is a Sunday
    remaining = (set(dates) - set(old)) | set(new)
    assert date(2026, 7, 29) not in remaining
    assert all(d.weekday() != 6 for d in remaining)


def test_no_collisions_and_count_preserved():
    dates = batch(date(2026, 7, 27), 30)
    plan = plan_holiday_shift(dates, date(2026, 8, 10))
    remaining = (set(dates) - {o for o, _ in plan}) | {n for _, n in plan}
    assert len(remaining) == len(dates)          # no file lost or doubled
    assert date(2026, 8, 10) not in remaining     # holiday cleared
    assert all(d.weekday() != 6 for d in remaining)


def test_earlier_holiday_gap_is_preserved():
    # Skip a first holiday, then a second one that lands *before* it.
    dates = batch(date(2026, 7, 27), 20)
    first = plan_holiday_shift(dates, date(2026, 8, 5))
    after_first = sorted((set(dates) - {o for o, _ in first})
                         | {n for _, n in first})
    assert date(2026, 8, 5) not in after_first

    second = plan_holiday_shift(after_first, date(2026, 7, 31))
    after_second = (set(after_first) - {o for o, _ in second}) \
        | {n for _, n in second}
    # both holiday dates stay empty; the earlier gap wasn't back-filled
    assert date(2026, 7, 31) not in after_second
    assert date(2026, 8, 5) not in after_second
    assert all(d.weekday() != 6 for d in after_second)
