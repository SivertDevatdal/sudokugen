"""Tests for the newspaper column PDF renderer."""

import json
import sys
from datetime import date

import pytest

sys.path.insert(0, 'src')

from sudokugen.column import (
    COLS, ROWS_VANSKELIG, SOL_ROWS, SOL1_COLS, SOL2_COLS,
    render_column_pdf, render_day,
)

SAMPLE_GRID = [[(r * 3 + r // 3 + c) % 9 + 1 if (r + c) % 3 == 0 else 0
                for c in range(9)] for r in range(9)]
SAMPLE_SOLUTION = [[(r * 3 + r // 3 + c) % 9 + 1 for c in range(9)]
                   for r in range(9)]


def test_geometry_constants():
    """Line position tables are 10 monotonically increasing entries."""
    for lines in (COLS, ROWS_VANSKELIG, SOL_ROWS, SOL1_COLS, SOL2_COLS):
        assert len(lines) == 10
        assert all(a < b for a, b in zip(lines, lines[1:]))
    # solution grids sit side by side without overlapping
    assert SOL1_COLS[9] < SOL2_COLS[0]


def test_render_column_pdf(tmp_path):
    """Renders a non-empty single-page PDF."""
    out = tmp_path / 'out.pdf'
    grids = {'middels': SAMPLE_GRID, 'vanskelig': SAMPLE_GRID}
    sols = {'middels': SAMPLE_SOLUTION, 'vanskelig': SAMPLE_SOLUTION}
    render_column_pdf(str(out), grids, sols)
    data = out.read_bytes()
    assert data.startswith(b'%PDF')
    assert len(data) > 5000


def test_render_day_uses_previous_solutions(tmp_path):
    """render_day requires the previous day's JSON for its solutions."""
    def day_json(day, grid, solution):
        payload = {'date': day.isoformat()}
        for key in ('middels', 'vanskelig'):
            payload[key] = {'grid': grid, 'solution': solution,
                            'se_rating': 2.3, 'clue_count': 28}
        (tmp_path / f'{day.isoformat()}.json').write_text(
            json.dumps(payload), encoding='utf-8')

    day_json(date(2026, 1, 2), SAMPLE_GRID, SAMPLE_SOLUTION)

    # previous day missing -> refuses to render
    with pytest.raises(FileNotFoundError):
        render_day(date(2026, 1, 2), str(tmp_path), str(tmp_path))

    day_json(date(2026, 1, 1), SAMPLE_GRID, SAMPLE_SOLUTION)
    out = render_day(date(2026, 1, 2), str(tmp_path), str(tmp_path))
    assert out.endswith('sudoku-2026-01-02.pdf')
    assert (tmp_path / 'sudoku-2026-01-02.pdf').read_bytes().startswith(b'%PDF')
