"""Which days the newspaper is published (and so gets a sudoku).

There is no paper on Sundays or on Norwegian public holidays (red days),
so no puzzles are generated for those days and the next page carries the
solutions from the last day that was printed.

Extra one-off days without a paper (a strike, a special issue, ...) go in
no-paper-days.txt at the repo root, one YYYY-MM-DD per line.
"""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from functools import lru_cache

SUNDAY = 6  # date.weekday()

# no-paper-days.txt sits at the repo root (next to kukoku.exe when frozen).
if getattr(sys, 'frozen', False):
    _ROOT = os.path.dirname(sys.executable)
else:
    _ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         os.pardir, os.pardir)
EXTRA_DAYS_FILE = os.path.join(_ROOT, 'no-paper-days.txt')


def easter_sunday(year: int) -> date:
    """Western Easter Sunday (anonymous Gregorian algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


@lru_cache(maxsize=None)
def norwegian_holidays(year: int) -> dict[date, str]:
    """The Norwegian public holidays (red days) of `year`, date -> name."""
    easter = easter_sunday(year)
    return {
        date(year, 1, 1): '1. nyttårsdag',
        easter - timedelta(days=3): 'Skjærtorsdag',
        easter - timedelta(days=2): 'Langfredag',
        easter: '1. påskedag',
        easter + timedelta(days=1): '2. påskedag',
        date(year, 5, 1): 'Arbeidernes dag',
        date(year, 5, 17): 'Grunnlovsdag',
        easter + timedelta(days=39): 'Kristi himmelfartsdag',
        easter + timedelta(days=49): '1. pinsedag',
        easter + timedelta(days=50): '2. pinsedag',
        date(year, 12, 25): '1. juledag',
        date(year, 12, 26): '2. juledag',
    }


def _load_extra_days(path: str) -> frozenset[date]:
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.read().splitlines()
    except OSError:
        return frozenset()
    days = set()
    for line in lines:
        line = line.split('#', 1)[0].strip()
        if line:
            days.add(date.fromisoformat(line))
    return frozenset(days)


EXTRA_NO_PAPER_DAYS = _load_extra_days(EXTRA_DAYS_FILE)


def no_paper_reason(day: date) -> str | None:
    """Why there is no paper on `day`, or None if it is a publishing day."""
    holiday = norwegian_holidays(day.year).get(day)
    if holiday:
        return holiday
    if day.weekday() == SUNDAY:
        return 'Søndag'
    if day in EXTRA_NO_PAPER_DAYS:
        return 'Ingen avis'
    return None


def is_publishing_day(day: date) -> bool:
    """True for every day the paper prints a sudoku."""
    return no_paper_reason(day) is None


def previous_publishing_day(day: date) -> date:
    """The publishing day before `day` (e.g. Saturday for a Monday)."""
    prev = day - timedelta(days=1)
    while not is_publishing_day(prev):
        prev -= timedelta(days=1)
    return prev
