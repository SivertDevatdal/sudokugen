"""Integration tests for the full pipeline."""

import sys
sys.path.insert(0, 'src')

from sudokugen.pipeline import generate_one
from sudokugen.dlx import has_unique_solution
from sudokugen.grid import ALL_UNITS


def test_generate_easy():
    """Should generate a valid easy puzzle."""
    result = generate_one('easy', max_attempts=200, require_soul=True)
    assert result is not None
    _validate_result(result, 'easy')


def test_generate_medium():
    """Should generate a valid medium puzzle."""
    result = generate_one('medium', max_attempts=300, require_soul=True)
    assert result is not None
    _validate_result(result, 'medium')


def test_generate_hard():
    """Should generate a valid hard puzzle."""
    result = generate_one('hard', max_attempts=500, require_soul=False)
    assert result is not None
    _validate_result(result, 'hard')


def _validate_result(result, expected_tier):
    """Validate all invariants of a generated puzzle."""
    # Correct difficulty tier
    assert result.difficulty_tier == expected_tier

    # Valid solution
    assert len(result.solution) == 81
    assert all(1 <= v <= 9 for v in result.solution)
    for unit in ALL_UNITS:
        vals = [result.solution[c] for c in unit]
        assert len(set(vals)) == 9

    # Puzzle is subset of solution
    for i in range(81):
        if result.grid[i] != 0:
            assert result.grid[i] == result.solution[i]

    # Unique solution
    assert has_unique_solution(result.grid)

    # Clue count matches
    assert result.clue_count == sum(1 for v in result.grid if v != 0)

    # 180° rotational symmetry
    for i in range(40):
        assert (result.grid[i] == 0) == (result.grid[80 - i] == 0)

    # At least 8 digits present
    present = set(v for v in result.grid if v != 0)
    assert len(present) >= 8

    # Solve path non-empty
    assert len(result.solve_path) > 0

    # SE rating positive
    assert result.se_rating > 0


if __name__ == '__main__':
    test_generate_easy()
    print("Easy: PASS")
    test_generate_medium()
    print("Medium: PASS")
    test_generate_hard()
    print("Hard: PASS")
    print("All pipeline tests passed!")
