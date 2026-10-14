"""Tests for the newspaper publishing calendar and the website manifest."""

import json
import sys
from datetime import date

sys.path.insert(0, 'src')

from sudokugen.manifest import write_manifest
from sudokugen.publishing import (
    easter_sunday, is_publishing_day, no_paper_reason, norwegian_holidays,
    previous_publishing_day,
)


def test_easter_sunday():
    assert easter_sunday(2026) == date(2026, 4, 5)
    assert easter_sunday(2027) == date(2027, 3, 28)
    assert easter_sunday(2024) == date(2024, 3, 31)


def test_norwegian_holidays_2027():
    assert set(norwegian_holidays(2027)) == {
        date(2027, 1, 1), date(2027, 3, 25), date(2027, 3, 26),
        date(2027, 3, 28), date(2027, 3, 29), date(2027, 5, 1),
        date(2027, 5, 6), date(2027, 5, 16), date(2027, 5, 17),
        date(2027, 12, 25), date(2027, 12, 26),
    }  # 2. pinsedag coincides with 17. mai in 2027


def test_no_paper_days():
    assert no_paper_reason(date(2026, 10, 11)) == 'Søndag'
    assert no_paper_reason(date(2026, 12, 25)) == '1. juledag'
    assert no_paper_reason(date(2026, 10, 14)) is None
    assert not is_publishing_day(date(2027, 3, 25))   # skjærtorsdag
    assert is_publishing_day(date(2026, 12, 24))      # julaften: not red


def test_previous_publishing_day_skips_holidays():
    # Christmas 2026: Fri 25th, Sat 26th, Sun 27th -> Monday follows Thursday
    assert previous_publishing_day(date(2026, 12, 28)) == date(2026, 12, 24)
    # Easter 2027: påskeaften (Sat) is not red -> Tuesday follows Saturday,
    # Saturday follows Wednesday
    assert previous_publishing_day(date(2027, 3, 30)) == date(2027, 3, 27)
    assert previous_publishing_day(date(2027, 3, 27)) == date(2027, 3, 24)


def test_manifest(tmp_path):
    for day in ('2026-12-23', '2026-12-24', '2026-12-28'):
        (tmp_path / f'sudoku-{day}.pdf').write_bytes(b'%PDF')
    (tmp_path / 'other.pdf').write_bytes(b'%PDF')
    data = json.loads(open(write_manifest(str(tmp_path)), encoding='utf-8').read())
    assert data['available'] == ['2026-12-23', '2026-12-24', '2026-12-28']
    assert data['noPaper']['2026-12-25'] == '1. juledag'
    assert data['noPaper']['2026-12-27'] == 'Søndag'
    assert '2026-12-24' not in data['noPaper']
