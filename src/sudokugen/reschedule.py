"""Rescheduling helpers for the dated puzzle batch.

The newspaper prints Monday–Saturday, never on Sundays. When an
unforeseen bank holiday (red day) turns up, the puzzle for that date and
every date after it has to slide forward by one printing slot, still
skipping Sundays and without disturbing any earlier holiday gaps that are
already baked into the batch.

`plan_holiday_shift` computes exactly which files move where. It is pure
(dates in, date pairs out) so it can be unit-tested and reused by the
`skipday` pop-up tool without pulling in any GUI code.
"""

from __future__ import annotations

from datetime import date, timedelta

SUNDAY = 6


def next_publishing_day(d: date, skip: frozenset[date] = frozenset()) -> date:
    """Return the first day strictly after `d` that is a printing day.

    Printing days are every day except Sundays and any date in `skip`.
    """
    d += timedelta(days=1)
    while d.weekday() == SUNDAY or d in skip:
        d += timedelta(days=1)
    return d


def plan_holiday_shift(
    dates: list[date], skip_date: date
) -> list[tuple[date, date]]:
    """Plan the file moves for skipping `skip_date`.

    `dates` is the set of dates that currently have a puzzle file (order
    doesn't matter; it is sorted internally). If `skip_date` has a file,
    that file and every later file shift up into the next occupied slot,
    and one brand-new date is appended at the end (skipping Sundays), so
    `skip_date` ends up empty. Files before `skip_date` — and any gaps
    already present (Sundays, earlier holidays) — are left untouched.

    Returns a list of (old_date, new_date) pairs to rename, ordered from
    the earliest mover to the latest. Returns an empty list when
    `skip_date` has no file (nothing to do).
    """
    dates = sorted(dates)
    if skip_date not in dates:
        return []
    idx = dates.index(skip_date)
    movers = dates[idx:]
    targets = dates[idx + 1:] + [next_publishing_day(dates[-1])]
    return list(zip(movers, targets))
