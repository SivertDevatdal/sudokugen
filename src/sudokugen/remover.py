"""Symmetric clue removal with uniqueness verification."""

from __future__ import annotations

import random

from .types import NUM_CELLS, DIGITS
from .dlx import has_unique_solution


def remove_clues(
    solution: list[int],
    target_clues: int = 28,
    min_clues: int = 22,
) -> list[int] | None:
    """Remove clues from a complete grid while preserving uniqueness and 180° symmetry.

    Returns a puzzle (81-element list, 0 = empty) or None if target can't be reached.
    """
    puzzle = solution[:]
    clue_count = NUM_CELLS

    # Build symmetric pairs: (i, 80-i) for i < 40, plus center cell (40,)
    pairs: list[tuple[int, ...]] = []
    for i in range(40):
        pairs.append((i, 80 - i))
    pairs.append((40,))  # center cell is its own partner
    random.shuffle(pairs)

    for pair in pairs:
        if clue_count <= target_clues:
            break

        # Skip if any cell in pair already empty
        if any(puzzle[c] == 0 for c in pair):
            continue

        # Tentatively remove
        backups = [(c, puzzle[c]) for c in pair]
        for c in pair:
            puzzle[c] = 0
        new_count = clue_count - len(pair)

        # Don't go below minimum
        if new_count < min_clues:
            for c, v in backups:
                puzzle[c] = v
            continue

        if has_unique_solution(puzzle):
            clue_count = new_count
        else:
            for c, v in backups:
                puzzle[c] = v

    # Verify at least 8 of 9 digits present
    present = set(v for v in puzzle if v != 0)
    if len(present) < 8:
        return None

    if clue_count > target_clues + 4:
        return None  # couldn't get close enough to target

    return puzzle


def remove_clues_for_difficulty(
    solution: list[int],
    difficulty: str,
) -> list[int] | None:
    """Remove clues targeting a specific difficulty tier's clue range."""
    ranges = {
        'easy': (32, 38),
        'medium': (28, 34),
        'hard': (24, 30),
        'expert': (22, 28),
    }
    min_c, max_c = ranges.get(difficulty, (26, 32))
    target = random.randint(min_c, max_c)
    return remove_clues(solution, target_clues=target, min_clues=min_c)
