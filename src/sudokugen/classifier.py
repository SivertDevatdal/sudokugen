"""Difficulty classification based on SE rating and clue count."""

from __future__ import annotations


def classify_difficulty(se_rating: float, clue_count: int) -> str | None:
    """Map SE rating to a difficulty tier.

    Returns 'easy', 'medium', 'hard', 'expert', or None if no tier fits.
    Primary classification is by technique difficulty (SE rating).
    Clue count is a secondary sanity check.
    """
    if se_rating <= 1.5:
        return 'easy'
    if se_rating <= 2.5:
        return 'medium' if clue_count >= 26 else 'hard'
    if se_rating <= 3.4:
        return 'medium' if clue_count >= 30 else 'hard'
    if se_rating <= 5.0:
        return 'hard' if clue_count >= 26 else 'expert'
    return None  # beyond our technique range


def max_difficulty_for_tier(tier: str) -> float:
    """Maximum SE difficulty allowed for a given tier."""
    return {
        'easy': 1.5,
        'medium': 3.4,
        'hard': 5.0,
        'expert': 5.0,
    }.get(tier, 5.0)


def difficulty_clue_range(difficulty: str) -> tuple[int, int]:
    """Target (min, max) clue counts for each difficulty tier."""
    return {
        'easy': (32, 38),
        'medium': (28, 34),
        'hard': (24, 30),
        'expert': (22, 28),
    }.get(difficulty, (26, 32))
