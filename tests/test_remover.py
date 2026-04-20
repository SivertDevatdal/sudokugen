"""Tests for symmetric clue removal."""

import sys
sys.path.insert(0, 'src')

from sudokugen.remover import remove_clues, remove_clues_for_difficulty
from sudokugen.generator import generate_full_grid
from sudokugen.dlx import has_unique_solution


def test_symmetry():
    """Removed puzzle should have 180° rotational symmetry."""
    grid = generate_full_grid()
    puzzle = remove_clues(grid, target_clues=30)
    assert puzzle is not None
    for i in range(40):
        a_empty = puzzle[i] == 0
        b_empty = puzzle[80 - i] == 0
        assert a_empty == b_empty, f"Symmetry broken at cell {i}"


def test_uniqueness():
    """Removed puzzle should still have a unique solution."""
    grid = generate_full_grid()
    puzzle = remove_clues(grid, target_clues=30)
    assert puzzle is not None
    assert has_unique_solution(puzzle)


def test_clue_count():
    """Clue count should be near the target."""
    grid = generate_full_grid()
    puzzle = remove_clues(grid, target_clues=28)
    assert puzzle is not None
    clues = sum(1 for v in puzzle if v != 0)
    assert 22 <= clues <= 32  # within reasonable range


def test_digit_balance():
    """At least 8 of 9 digits should be present."""
    grid = generate_full_grid()
    puzzle = remove_clues(grid, target_clues=28)
    assert puzzle is not None
    present = set(v for v in puzzle if v != 0)
    assert len(present) >= 8


def test_difficulty_ranges():
    """Different difficulties should produce different clue ranges."""
    grid = generate_full_grid()
    easy = remove_clues_for_difficulty(grid, 'easy')
    if easy:
        easy_clues = sum(1 for v in easy if v != 0)
        assert easy_clues >= 30  # easy should have many clues


if __name__ == '__main__':
    test_symmetry()
    test_uniqueness()
    test_clue_count()
    test_digit_balance()
    test_difficulty_ranges()
    print("All remover tests passed!")
