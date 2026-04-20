"""Single-digit techniques: hidden singles (box/line) and naked singles."""

from __future__ import annotations

from ..types import DIGITS, has_candidate, candidate_count, single_candidate, digit_bit
from ..grid import SolverGrid, BOX_CELLS, ROW_CELLS, COL_CELLS
from . import TechniqueApplication


def hidden_single_box(grid: SolverGrid) -> TechniqueApplication | None:
    """Find a digit that has only one possible cell within a box.

    Difficulty: 1.2 (SE rating)
    """
    first_cell = -1
    first_digit = 0
    opportunities = 0

    for box in BOX_CELLS:
        for d in DIGITS:
            bit = digit_bit(d)
            places = []
            for cell in box:
                if grid.values[cell] == 0 and grid.candidates[cell] & bit:
                    places.append(cell)
                    if len(places) > 1:
                        break
            if len(places) == 1:
                opportunities += 1
                if first_cell == -1:
                    first_cell = places[0]
                    first_digit = d

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='hidden_single_box',
        difficulty=1.2,
        assignments=[(first_cell, first_digit)],
        opportunities=opportunities,
    )


def hidden_single_line(grid: SolverGrid) -> TechniqueApplication | None:
    """Find a digit that has only one possible cell within a row or column.

    Difficulty: 1.5 (SE rating)
    """
    first_cell = -1
    first_digit = 0
    opportunities = 0

    for unit in ROW_CELLS + COL_CELLS:
        for d in DIGITS:
            bit = digit_bit(d)
            places = []
            for cell in unit:
                if grid.values[cell] == 0 and grid.candidates[cell] & bit:
                    places.append(cell)
                    if len(places) > 1:
                        break
            if len(places) == 1:
                opportunities += 1
                if first_cell == -1:
                    first_cell = places[0]
                    first_digit = d

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='hidden_single_line',
        difficulty=1.5,
        assignments=[(first_cell, first_digit)],
        opportunities=opportunities,
    )


def naked_single(grid: SolverGrid) -> TechniqueApplication | None:
    """Find a cell with exactly one candidate remaining.

    Difficulty: 2.3 (SE rating)
    """
    first_cell = -1
    first_digit = 0
    opportunities = 0

    for cell in range(81):
        if grid.values[cell] == 0 and candidate_count(grid.candidates[cell]) == 1:
            d = single_candidate(grid.candidates[cell])
            opportunities += 1
            if first_cell == -1:
                first_cell = cell
                first_digit = d

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='naked_single',
        difficulty=2.3,
        assignments=[(first_cell, first_digit)],
        opportunities=opportunities,
    )
