"""Tests for solving techniques."""

import sys
sys.path.insert(0, 'src')

from sudokugen.grid import SolverGrid
from sudokugen.techniques.singles import hidden_single_box, hidden_single_line, naked_single
from sudokugen.techniques.intersections import pointing_pair, claiming
from sudokugen.techniques.subsets import naked_pair
from sudokugen.types import has_candidate, candidate_count


# Puzzle that requires only hidden singles (box)
HIDDEN_SINGLE_PUZZLE = [
    0,0,0, 2,6,0, 7,0,1,
    6,8,0, 0,7,0, 0,9,0,
    1,9,0, 0,0,4, 5,0,0,
    8,2,0, 1,0,0, 0,4,0,
    0,0,4, 6,0,2, 9,0,0,
    0,5,0, 0,0,3, 0,2,8,
    0,0,9, 3,0,0, 0,7,4,
    0,4,0, 0,5,0, 0,3,6,
    7,0,3, 0,1,8, 0,0,0,
]


def test_hidden_single_box_finds():
    """Hidden single in box should find at least one application."""
    grid = SolverGrid(HIDDEN_SINGLE_PUZZLE)
    result = hidden_single_box(grid)
    assert result is not None
    assert result.technique == 'hidden_single_box'
    assert result.difficulty == 1.2
    assert len(result.assignments) == 1
    assert result.opportunities >= 1


def test_naked_single_on_forced_cell():
    """If a cell has only one candidate, naked single should find it."""
    # Create a grid where cell 0 is forced to a single value
    givens = [0] * 81
    # Fill row 0 except cell 0
    for c in range(1, 9):
        givens[c] = c + 1  # digits 2-9
    grid = SolverGrid(givens)
    # Cell 0 should have only candidate 1
    assert candidate_count(grid.candidates[0]) == 1
    result = naked_single(grid)
    assert result is not None
    assert result.assignments[0] == (0, 1)


def test_technique_does_not_mutate():
    """Techniques should not modify the grid."""
    grid = SolverGrid(HIDDEN_SINGLE_PUZZLE)
    cands_before = grid.candidates[:]
    vals_before = grid.values[:]
    hidden_single_box(grid)
    assert grid.candidates == cands_before
    assert grid.values == vals_before


if __name__ == '__main__':
    test_hidden_single_box_finds()
    test_naked_single_on_forced_cell()
    test_technique_does_not_mutate()
    print("All technique tests passed!")
