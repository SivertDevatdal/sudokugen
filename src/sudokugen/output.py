"""JSON serialization and display formatting."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .types import PuzzleResult, GRID_SIZE, cell_from_rc


def puzzle_to_string(values: list[int]) -> str:
    """Convert 81-element list to compact string (0 = '.')."""
    return ''.join('.' if v == 0 else str(v) for v in values)


def string_to_puzzle(s: str) -> list[int]:
    """Convert 81-char string (. or 0 for empty) to list."""
    result = []
    for ch in s:
        if ch in '.0':
            result.append(0)
        elif ch.isdigit():
            result.append(int(ch))
    if len(result) != 81:
        raise ValueError(f"Expected 81 cells, got {len(result)}")
    return result


def puzzle_to_grid_display(values: list[int]) -> str:
    """Pretty-print a 9x9 grid with box separators."""
    lines = []
    lines.append('+-------+-------+-------+')
    for r in range(GRID_SIZE):
        parts = []
        for c in range(GRID_SIZE):
            v = values[cell_from_rc(r, c)]
            parts.append('.' if v == 0 else str(v))
        row = '| {} {} {} | {} {} {} | {} {} {} |'.format(*parts)
        lines.append(row)
        if r % 3 == 2:
            lines.append('+-------+-------+-------+')
    return '\n'.join(lines)


def puzzle_to_json(result: PuzzleResult) -> dict[str, Any]:
    """Convert a PuzzleResult to a JSON-serializable dict."""
    return {
        'puzzle': puzzle_to_string(result.grid),
        'solution': puzzle_to_string(result.solution),
        'difficulty': result.difficulty_tier,
        'se_rating': result.se_rating,
        'clue_count': result.clue_count,
        'has_soul': result.has_soul,
        'techniques_required': sorted({s.technique for s in result.solve_path}),
        'max_technique': max(result.solve_path, key=lambda s: s.difficulty).technique if result.solve_path else '',
        'solve_path_summary': result.metadata,
    }


def batch_to_json(results: list[PuzzleResult]) -> dict[str, Any]:
    """Wrap a list of puzzle results with batch metadata."""
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'count': len(results),
        'puzzles': [puzzle_to_json(r) for r in results],
    }


def _grid_to_2d(flat: list[int]) -> list[list[int]]:
    """Convert 81-element flat list to 9×9 nested array."""
    return [flat[r * 9:(r + 1) * 9] for r in range(9)]


def puzzle_pair_to_dated_json(
    date_str: str,
    middels: PuzzleResult,
    vanskelig: PuzzleResult,
) -> dict[str, Any]:
    """Create a dated puzzle pair for InDesign consumption.

    Grids are 9×9 nested arrays (easy for ExtendScript to parse).
    """
    return {
        'date': date_str,
        'middels': {
            'grid': _grid_to_2d(middels.grid),
            'solution': _grid_to_2d(middels.solution),
            'se_rating': middels.se_rating,
            'clue_count': middels.clue_count,
        },
        'vanskelig': {
            'grid': _grid_to_2d(vanskelig.grid),
            'solution': _grid_to_2d(vanskelig.solution),
            'se_rating': vanskelig.se_rating,
            'clue_count': vanskelig.clue_count,
        },
    }
