"""Intersection techniques: pointing pairs and claiming (box-line reduction)."""

from __future__ import annotations

from ..types import DIGITS, GRID_SIZE, BOX_SIZE, digit_bit, cell_row, cell_col, cell_box
from ..grid import SolverGrid, BOX_CELLS, ROW_CELLS, COL_CELLS, CELL_ROW, CELL_COL, CELL_BOX
from . import TechniqueApplication


def pointing_pair(grid: SolverGrid) -> TechniqueApplication | None:
    """If all candidates for a digit in a box lie in one row/col,
    eliminate that digit from the rest of that row/col.

    Difficulty: 2.6 (SE rating)
    """
    first_elims: list[tuple[int, int]] = []
    opportunities = 0

    for bi, box in enumerate(BOX_CELLS):
        for d in DIGITS:
            bit = digit_bit(d)
            cells_with_d = [c for c in box if grid.values[c] == 0 and grid.candidates[c] & bit]
            if len(cells_with_d) < 2:
                continue

            # Check if all in same row
            rows = {CELL_ROW[c] for c in cells_with_d}
            if len(rows) == 1:
                row = rows.pop()
                elims = [
                    (c, d) for c in ROW_CELLS[row]
                    if CELL_BOX[c] != bi and grid.values[c] == 0 and grid.candidates[c] & bit
                ]
                if elims:
                    opportunities += 1
                    if not first_elims:
                        first_elims = elims

            # Check if all in same column
            cols = {CELL_COL[c] for c in cells_with_d}
            if len(cols) == 1:
                col = cols.pop()
                elims = [
                    (c, d) for c in COL_CELLS[col]
                    if CELL_BOX[c] != bi and grid.values[c] == 0 and grid.candidates[c] & bit
                ]
                if elims:
                    opportunities += 1
                    if not first_elims:
                        first_elims = elims

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='pointing_pair',
        difficulty=2.6,
        eliminations=first_elims,
        opportunities=opportunities,
    )


def claiming(grid: SolverGrid) -> TechniqueApplication | None:
    """If all candidates for a digit in a row/col lie within one box,
    eliminate that digit from the rest of that box.

    Difficulty: 2.8 (SE rating)
    """
    first_elims: list[tuple[int, int]] = []
    opportunities = 0

    for unit in ROW_CELLS + COL_CELLS:
        for d in DIGITS:
            bit = digit_bit(d)
            cells_with_d = [c for c in unit if grid.values[c] == 0 and grid.candidates[c] & bit]
            if len(cells_with_d) < 2:
                continue

            boxes = {CELL_BOX[c] for c in cells_with_d}
            if len(boxes) == 1:
                bi = boxes.pop()
                elims = [
                    (c, d) for c in BOX_CELLS[bi]
                    if c not in cells_with_d and grid.values[c] == 0 and grid.candidates[c] & bit
                ]
                if elims:
                    opportunities += 1
                    if not first_elims:
                        first_elims = elims

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='claiming',
        difficulty=2.8,
        eliminations=first_elims,
        opportunities=opportunities,
    )
