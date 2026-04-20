"""Fish techniques: X-Wing and Swordfish."""

from __future__ import annotations

from itertools import combinations

from ..types import DIGITS, GRID_SIZE, digit_bit, has_candidate
from ..grid import SolverGrid, ROW_CELLS, COL_CELLS
from . import TechniqueApplication


def x_wing(grid: SolverGrid) -> TechniqueApplication | None:
    """Find two rows where a digit appears in exactly the same two columns.
    Eliminate that digit from those columns in all other rows.
    Also checks column-based X-Wings (two cols, same two rows).

    Difficulty: 3.2 (SE rating)
    """
    first_elims: list[tuple[int, int]] = []
    opportunities = 0

    for d in DIGITS:
        bit = digit_bit(d)

        # Row-based X-Wing: find rows where d appears in exactly 2 columns
        row_positions: list[tuple[int, list[int]]] = []
        for ri, row in enumerate(ROW_CELLS):
            cols = [ci for ci, c in enumerate(row) if grid.values[c] == 0 and grid.candidates[c] & bit]
            if len(cols) == 2:
                row_positions.append((ri, cols))

        for (r1, cols1), (r2, cols2) in combinations(row_positions, 2):
            if cols1 != cols2:
                continue
            c1, c2 = cols1
            elims = []
            for ri in range(GRID_SIZE):
                if ri == r1 or ri == r2:
                    continue
                for ci in (c1, c2):
                    cell = ROW_CELLS[ri][ci]
                    if grid.values[cell] == 0 and grid.candidates[cell] & bit:
                        elims.append((cell, d))
            if elims:
                opportunities += 1
                if not first_elims:
                    first_elims = elims

        # Column-based X-Wing: find cols where d appears in exactly 2 rows
        col_positions: list[tuple[int, list[int]]] = []
        for ci, col in enumerate(COL_CELLS):
            rows = [ri for ri, c in enumerate(col) if grid.values[c] == 0 and grid.candidates[c] & bit]
            if len(rows) == 2:
                col_positions.append((ci, rows))

        for (c1, rows1), (c2, rows2) in combinations(col_positions, 2):
            if rows1 != rows2:
                continue
            r1, r2 = rows1
            elims = []
            for ci in range(GRID_SIZE):
                if ci == c1 or ci == c2:
                    continue
                for ri in (r1, r2):
                    cell = ROW_CELLS[ri][ci]
                    if grid.values[cell] == 0 and grid.candidates[cell] & bit:
                        elims.append((cell, d))
            if elims:
                opportunities += 1
                if not first_elims:
                    first_elims = elims

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='x_wing',
        difficulty=3.2,
        eliminations=first_elims,
        opportunities=opportunities,
    )


def swordfish(grid: SolverGrid) -> TechniqueApplication | None:
    """Find three rows where a digit appears in at most 3 columns total,
    and those columns contain the digit in exactly those 3 rows.
    Eliminate from those columns in other rows. Also checks column-based.

    Difficulty: 3.8 (SE rating)
    """
    first_elims: list[tuple[int, int]] = []
    opportunities = 0

    for d in DIGITS:
        bit = digit_bit(d)

        # Row-based Swordfish
        row_positions: list[tuple[int, list[int]]] = []
        for ri, row in enumerate(ROW_CELLS):
            cols = [ci for ci, c in enumerate(row) if grid.values[c] == 0 and grid.candidates[c] & bit]
            if 2 <= len(cols) <= 3:
                row_positions.append((ri, cols))

        for combo in combinations(row_positions, 3):
            rows = [r for r, _ in combo]
            col_union = set()
            for _, cols in combo:
                col_union.update(cols)
            if len(col_union) != 3:
                continue

            row_set = set(rows)
            elims = []
            for ci in col_union:
                for ri in range(GRID_SIZE):
                    if ri in row_set:
                        continue
                    cell = ROW_CELLS[ri][ci]
                    if grid.values[cell] == 0 and grid.candidates[cell] & bit:
                        elims.append((cell, d))

            if elims:
                opportunities += 1
                if not first_elims:
                    first_elims = elims

        # Column-based Swordfish
        col_positions: list[tuple[int, list[int]]] = []
        for ci, col in enumerate(COL_CELLS):
            rows = [ri for ri, c in enumerate(col) if grid.values[c] == 0 and grid.candidates[c] & bit]
            if 2 <= len(rows) <= 3:
                col_positions.append((ci, rows))

        for combo in combinations(col_positions, 3):
            cols = [c for c, _ in combo]
            row_union = set()
            for _, rows in combo:
                row_union.update(rows)
            if len(row_union) != 3:
                continue

            col_set = set(cols)
            elims = []
            for ri in row_union:
                for ci in range(GRID_SIZE):
                    if ci in col_set:
                        continue
                    cell = ROW_CELLS[ri][ci]
                    if grid.values[cell] == 0 and grid.candidates[cell] & bit:
                        elims.append((cell, d))

            if elims:
                opportunities += 1
                if not first_elims:
                    first_elims = elims

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='swordfish',
        difficulty=3.8,
        eliminations=first_elims,
        opportunities=opportunities,
    )
