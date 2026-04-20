"""Tests for quality analysis and soul filter."""

import sys
sys.path.insert(0, 'src')

from sudokugen.types import TechniqueStep
from sudokugen.quality import compute_se_rating, has_soul, analyze_solve_path


def _make_path(steps: list[tuple[str, float, int]]) -> list[TechniqueStep]:
    """Helper: create a solve path from (technique, difficulty, opportunities)."""
    return [
        TechniqueStep(technique=t, difficulty=d, cell=0, digit=1, opportunities=o)
        for t, d, o in steps
    ]


def test_se_rating():
    path = _make_path([
        ('hidden_single_box', 1.2, 3),
        ('naked_single', 2.3, 1),
        ('x_wing', 3.2, 1),
    ])
    assert compute_se_rating(path) == 3.2


def test_has_soul_good_puzzle():
    """A well-balanced hard puzzle should have soul."""
    path = _make_path([
        ('hidden_single_box', 1.2, 5),
        ('hidden_single_box', 1.2, 4),
        ('naked_single', 2.3, 3),
        ('hidden_single_line', 1.5, 2),
        ('pointing_pair', 2.6, 2),
        ('hidden_single_box', 1.2, 3),
        ('x_wing', 3.2, 1),  # crux at position 6/9 = 67%
        ('hidden_single_box', 1.2, 4),
        ('hidden_single_box', 1.2, 3),
    ])
    assert has_soul(path, se_rating=3.2)


def test_has_soul_too_many_cruxes():
    """Too many applications of hardest technique = grinding."""
    path = _make_path([
        ('hidden_single_box', 1.2, 2),
        ('x_wing', 3.2, 1),
        ('x_wing', 3.2, 1),
        ('x_wing', 3.2, 1),
        ('x_wing', 3.2, 1),  # 4 cruxes > 3
        ('hidden_single_box', 1.2, 2),
    ])
    assert not has_soul(path, se_rating=3.2)


def test_has_soul_easy_relaxed():
    """Easy puzzles should pass with relaxed criteria."""
    path = _make_path([
        ('hidden_single_box', 1.2, 5),
        ('hidden_single_box', 1.2, 4),
        ('hidden_single_box', 1.2, 3),
        ('hidden_single_box', 1.2, 3),
        ('hidden_single_box', 1.2, 2),
        ('hidden_single_box', 1.2, 2),
    ])
    assert has_soul(path, se_rating=1.2)


if __name__ == '__main__':
    test_se_rating()
    test_has_soul_good_puzzle()
    test_has_soul_too_many_cruxes()
    test_has_soul_easy_relaxed()
    print("All quality tests passed!")
