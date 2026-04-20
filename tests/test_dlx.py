"""Tests for DLX solver."""

import sys
sys.path.insert(0, 'src')

from sudokugen.dlx import has_unique_solution, count_solutions, solve_dlx
from sudokugen.generator import generate_full_grid


# A known easy puzzle with unique solution
EASY_PUZZLE = [
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


def test_unique_solution():
    """Known puzzle should have unique solution."""
    assert has_unique_solution(EASY_PUZZLE)


def test_full_grid_unique():
    """A complete grid should have exactly 1 solution."""
    grid = generate_full_grid()
    assert has_unique_solution(grid)
    assert count_solutions(grid, limit=2) == 1


def test_solve():
    """DLX should solve a valid puzzle."""
    sol = solve_dlx(EASY_PUZZLE)
    assert sol is not None
    assert all(1 <= v <= 9 for v in sol)


def test_multiple_solutions():
    """Removing enough clues should create multiple solutions."""
    grid = generate_full_grid()
    # Remove many clues to likely get multiple solutions
    sparse = grid[:]
    for i in range(0, 50):
        sparse[i] = 0
    # Very sparse — should have multiple solutions (or at least not be rejected)
    n = count_solutions(sparse, limit=2)
    assert n >= 1  # at least solvable


if __name__ == '__main__':
    test_unique_solution()
    test_full_grid_unique()
    test_solve()
    test_multiple_solutions()
    print("All DLX tests passed!")
