"""Shared types, constants, and bitfield helpers for sudoku generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Grid constants
GRID_SIZE = 9
BOX_SIZE = 3
NUM_CELLS = 81
DIGITS = range(1, 10)

# Bitfield candidate helpers — candidates stored as int with bits 1–9
ALL_CANDIDATES = 0x3FE  # bits 1..9 set = 0b1111111110


def digit_bit(d: int) -> int:
    """Bitmask for a single digit (1–9)."""
    return 1 << d


def candidates_from_set(digits: set[int]) -> int:
    """Convert a set of digits to a candidate bitfield."""
    c = 0
    for d in digits:
        c |= 1 << d
    return c


def candidates_to_set(c: int) -> set[int]:
    """Convert a candidate bitfield to a set of digits."""
    return {d for d in DIGITS if c & (1 << d)}


def candidate_count(c: int) -> int:
    """Number of candidates in a bitfield."""
    return (c >> 1).bit_count()  # only bits 1–9 matter


def has_candidate(c: int, d: int) -> bool:
    """Check if digit d is a candidate."""
    return bool(c & (1 << d))


def single_candidate(c: int) -> int:
    """Return the only digit in a single-candidate bitfield, or 0."""
    shifted = c >> 1
    if shifted.bit_count() != 1:
        return 0
    return shifted.bit_length()


def candidates_iter(c: int) -> list[int]:
    """Return list of digits in a candidate bitfield."""
    return [d for d in DIGITS if c & (1 << d)]


# Cell index helpers — cells numbered 0–80, row-major
def cell_row(cell: int) -> int:
    return cell // GRID_SIZE


def cell_col(cell: int) -> int:
    return cell % GRID_SIZE


def cell_box(cell: int) -> int:
    return (cell_row(cell) // BOX_SIZE) * BOX_SIZE + cell_col(cell) // BOX_SIZE


def cell_from_rc(row: int, col: int) -> int:
    return row * GRID_SIZE + col


# Dataclasses for solve path tracking

@dataclass
class TechniqueStep:
    """A single step in a solve path."""
    technique: str
    difficulty: float
    cell: int  # primary cell affected (-1 if elimination-only)
    digit: int  # primary digit placed (0 if elimination-only)
    opportunities: int  # how many independent applications exist at this state


SolvePath = list[TechniqueStep]


@dataclass
class PuzzleResult:
    """Complete result from the generation pipeline."""
    grid: list[int]  # 81 givens (0 = empty)
    solution: list[int]  # 81 solution digits
    solve_path: SolvePath
    se_rating: float
    difficulty_tier: str
    clue_count: int
    has_soul: bool
    metadata: dict[str, Any] = field(default_factory=dict)
