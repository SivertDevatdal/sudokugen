"""Full grid generation via backtracking with randomized digit ordering."""

from __future__ import annotations

import random

from .types import NUM_CELLS, candidates_iter
from .grid import CandidateGrid


def generate_full_grid() -> list[int]:
    """Generate a complete valid 9x9 sudoku grid.

    Uses constraint propagation + backtracking with MRV heuristic
    and randomized candidate ordering for variety.
    Returns a 81-element list of digits 1–9.
    """
    grid = CandidateGrid([0] * NUM_CELLS)
    result = _fill(grid)
    if result is None:
        raise RuntimeError("Failed to generate grid (should not happen)")
    return result


def _fill(grid: CandidateGrid) -> list[int] | None:
    """Recursive backtracking fill with MRV heuristic."""
    if grid.is_complete():
        return grid.values[:]

    unsolved = grid.unsolved_cells()
    if not unsolved:
        return None

    # MRV: pick cell with fewest candidates (already sorted)
    cell = unsolved[0]
    digits = candidates_iter(grid.candidates[cell])
    random.shuffle(digits)

    for digit in digits:
        snapshot = grid.copy()
        if snapshot.assign(cell, digit):
            result = _fill(snapshot)
            if result is not None:
                return result

    return None
