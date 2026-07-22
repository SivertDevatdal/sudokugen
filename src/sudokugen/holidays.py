"""Norwegian public holidays (røde dager) and the printing calendar.

The newspaper prints Monday–Saturday and never on a Sunday or a red day.
`is_publishing_day` is the single source of truth for that rule; the
generator uses it to decide which dates get a puzzle, and the rescheduler
uses it when sliding dates forward.

Red days are the twelve national holidays. The movable ones hang off
Easter Sunday, computed with the Anonymous Gregorian algorithm.
"""

from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache

SUNDAY = 6


def easter_sunday(year: int) -> date:
    """Easter Sunday (Western/Gregorian) for `year`."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    lg = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * lg) // 451
    month = (h + lg - 7 * m + 114) // 31
    day = (h + lg - 7 * m + 114) % 31 + 1
    return date(year, month, day)


@lru_cache(maxsize=None)
def norwegian_red_days(year: int) -> frozenset[date]:
    """The twelve Norwegian public holidays for `year`."""
    e = easter_sunday(year)
    return frozenset({
        date(year, 1, 1),              # Første nyttårsdag
        e - timedelta(days=3),         # Skjærtorsdag
        e - timedelta(days=2),         # Langfredag
        e,                             # Første påskedag
        e + timedelta(days=1),         # Andre påskedag
        date(year, 5, 1),              # Arbeidernes dag
        date(year, 5, 17),             # Grunnlovsdag
        e + timedelta(days=39),        # Kristi himmelfartsdag
        e + timedelta(days=49),        # Første pinsedag
        e + timedelta(days=50),        # Andre pinsedag
        date(year, 12, 25),            # Første juledag
        date(year, 12, 26),            # Andre juledag
    })


def is_red_day(d: date) -> bool:
    """True if `d` is a Norwegian public holiday."""
    return d in norwegian_red_days(d.year)


def is_publishing_day(d: date) -> bool:
    """True if the paper prints on `d` (not a Sunday, not a red day)."""
    return d.weekday() != SUNDAY and not is_red_day(d)
