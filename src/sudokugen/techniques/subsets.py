"""Subset techniques: naked pair, hidden pair, naked triple."""

from __future__ import annotations

from itertools import combinations

from ..types import DIGITS, digit_bit, candidate_count, candidates_iter, has_candidate
from ..grid import SolverGrid, ALL_UNITS
from . import TechniqueApplication


def naked_pair(grid: SolverGrid) -> TechniqueApplication | None:
    """Find two cells in a unit whose candidates are a subset of two digits.
    Eliminate those digits from other cells in the unit.

    Difficulty: 3.0 (SE rating)
    """
    first_elims: list[tuple[int, int]] = []
    opportunities = 0

    for unit in ALL_UNITS:
        unsolved = [c for c in unit if grid.values[c] == 0]
        # Find cells with exactly 2 candidates
        bivalue = [c for c in unsolved if candidate_count(grid.candidates[c]) == 2]

        for c1, c2 in combinations(bivalue, 2):
            if grid.candidates[c1] != grid.candidates[c2]:
                continue
            pair_cands = grid.candidates[c1]
            digits = candidates_iter(pair_cands)

            elims = []
            for c in unsolved:
                if c == c1 or c == c2:
                    continue
                for d in digits:
                    if has_candidate(grid.candidates[c], d):
                        elims.append((c, d))

            if elims:
                opportunities += 1
                if not first_elims:
                    first_elims = elims

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='naked_pair',
        difficulty=3.0,
        eliminations=first_elims,
        opportunities=opportunities,
    )


def hidden_pair(grid: SolverGrid) -> TechniqueApplication | None:
    """Find two digits that only appear in two cells within a unit.
    Restrict those cells to only those two digits.

    Difficulty: 3.4 (SE rating)
    """
    first_elims: list[tuple[int, int]] = []
    opportunities = 0

    for unit in ALL_UNITS:
        unsolved = [c for c in unit if grid.values[c] == 0]
        if len(unsolved) < 3:
            continue

        # For each digit, which unsolved cells contain it
        digit_cells: dict[int, list[int]] = {}
        for d in DIGITS:
            bit = digit_bit(d)
            cells = [c for c in unsolved if grid.candidates[c] & bit]
            if len(cells) == 2:
                digit_cells[d] = cells

        # Find pairs of digits that share exactly the same two cells
        digits_with_2 = list(digit_cells.keys())
        for d1, d2 in combinations(digits_with_2, 2):
            if digit_cells[d1] != digit_cells[d2]:
                continue

            c1, c2 = digit_cells[d1]
            pair_bits = digit_bit(d1) | digit_bit(d2)

            elims = []
            for c in (c1, c2):
                for d in candidates_iter(grid.candidates[c]):
                    if d != d1 and d != d2:
                        elims.append((c, d))

            if elims:
                opportunities += 1
                if not first_elims:
                    first_elims = elims

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='hidden_pair',
        difficulty=3.4,
        eliminations=first_elims,
        opportunities=opportunities,
    )


def naked_triple(grid: SolverGrid) -> TechniqueApplication | None:
    """Find three cells in a unit whose combined candidates span at most three digits.
    Eliminate those digits from other cells in the unit.

    Difficulty: 3.6 (SE rating)
    """
    first_elims: list[tuple[int, int]] = []
    opportunities = 0

    for unit in ALL_UNITS:
        unsolved = [c for c in unit if grid.values[c] == 0]
        # Only consider cells with 2 or 3 candidates
        small = [c for c in unsolved if 2 <= candidate_count(grid.candidates[c]) <= 3]

        for combo in combinations(small, 3):
            union = 0
            for c in combo:
                union |= grid.candidates[c]
            if candidate_count(union) != 3:
                continue

            digits = candidates_iter(union)
            combo_set = set(combo)
            elims = []
            for c in unsolved:
                if c in combo_set:
                    continue
                for d in digits:
                    if has_candidate(grid.candidates[c], d):
                        elims.append((c, d))

            if elims:
                opportunities += 1
                if not first_elims:
                    first_elims = elims

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='naked_triple',
        difficulty=3.6,
        eliminations=first_elims,
        opportunities=opportunities,
    )
