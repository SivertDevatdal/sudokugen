"""Uniqueness techniques: Unique Rectangle (Type 1).

These techniques exploit the fact that the puzzle is known to have a unique solution.
Only valid when uniqueness has been verified by DLX beforehand.
"""

from __future__ import annotations

from itertools import combinations

from ..types import (
    GRID_SIZE, candidate_count, candidates_iter, has_candidate, digit_bit,
    cell_from_rc, cell_row, cell_col, cell_box,
)
from ..grid import SolverGrid, CELL_ROW, CELL_COL, CELL_BOX
from . import TechniqueApplication


def unique_rectangle(grid: SolverGrid) -> TechniqueApplication | None:
    """Detect Type 1 Unique Rectangle.

    Four cells forming a rectangle in 2 rows × 2 columns spanning exactly 2 boxes,
    where 3 cells contain only digits {a, b} and the 4th has {a, b, ...}.
    Eliminate {a, b} from the 4th cell (otherwise the puzzle would have 2 solutions).

    Difficulty: 4.5 (SE rating)
    """
    first_elims: list[tuple[int, int]] = []
    opportunities = 0

    # Find all bivalue cells and group by candidate pair
    from collections import defaultdict
    pair_cells: dict[int, list[int]] = defaultdict(list)

    for cell in range(81):
        if grid.values[cell] == 0 and candidate_count(grid.candidates[cell]) == 2:
            pair_cells[grid.candidates[cell]].append(cell)

    for cand_bits, cells in pair_cells.items():
        if len(cells) < 3:
            continue

        digits = candidates_iter(cand_bits)
        a, b = digits[0], digits[1]

        # Try all triples of bivalue cells with same candidates
        for triple in combinations(cells, 3):
            rows = {CELL_ROW[c] for c in triple}
            cols = {CELL_COL[c] for c in triple}

            # Need exactly 2 rows and 2 columns
            if len(rows) != 2 or len(cols) != 2:
                continue

            r1, r2 = sorted(rows)
            c1, c2 = sorted(cols)

            # The 4 corners of the rectangle
            corners = [
                cell_from_rc(r1, c1), cell_from_rc(r1, c2),
                cell_from_rc(r2, c1), cell_from_rc(r2, c2),
            ]

            # Must span exactly 2 boxes
            boxes = {CELL_BOX[c] for c in corners}
            if len(boxes) != 2:
                continue

            # Find the 4th cell (the one not in our triple)
            triple_set = set(triple)
            fourth = [c for c in corners if c not in triple_set]
            if len(fourth) != 1:
                continue
            fourth_cell = fourth[0]

            # The 4th cell must be unsolved and have candidates {a, b, ...}
            if grid.values[fourth_cell] != 0:
                continue
            fc = grid.candidates[fourth_cell]
            if not (has_candidate(fc, a) and has_candidate(fc, b)):
                continue
            if candidate_count(fc) <= 2:
                continue  # already bivalue, no elimination possible

            elims = [(fourth_cell, a), (fourth_cell, b)]
            opportunities += 1
            if not first_elims:
                first_elims = elims

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='unique_rectangle',
        difficulty=4.5,
        eliminations=first_elims,
        opportunities=opportunities,
    )
