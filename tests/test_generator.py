"""Tests for grid generation."""

import sys
sys.path.insert(0, 'src')

from sudokugen.generator import generate_full_grid
from sudokugen.grid import ALL_UNITS


def test_valid_grid():
    """Generated grid should be a valid sudoku solution."""
    for _ in range(10):
        grid = generate_full_grid()
        assert len(grid) == 81
        assert all(1 <= v <= 9 for v in grid)
        for unit in ALL_UNITS:
            vals = [grid[c] for c in unit]
            assert len(set(vals)) == 9, f"Duplicate in unit: {vals}"


def test_randomness():
    """Two consecutive grids should (almost certainly) be different."""
    g1 = generate_full_grid()
    g2 = generate_full_grid()
    assert g1 != g2


if __name__ == '__main__':
    test_valid_grid()
    test_randomness()
    print("All generator tests passed!")
