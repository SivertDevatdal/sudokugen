"""Sudoku solving techniques for difficulty grading.

Each technique is a pure inspector: it receives a SolverGrid (read-only),
finds one application of the technique, counts total opportunities, and returns
a TechniqueApplication describing what to do — or None if the technique doesn't apply.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..grid import SolverGrid


@dataclass
class TechniqueApplication:
    """Result from a technique detection function."""
    technique: str
    difficulty: float
    eliminations: list[tuple[int, int]] = field(default_factory=list)  # (cell, digit) pairs
    assignments: list[tuple[int, int]] = field(default_factory=list)   # (cell, digit) pairs
    opportunities: int = 1  # how many independent applications exist


TechniqueFunc = Callable[[SolverGrid], TechniqueApplication | None]

# Lazy-populated by _build_technique_order() on first access
_TECHNIQUE_ORDER: list[tuple[str, float, TechniqueFunc]] | None = None


def get_technique_order() -> list[tuple[str, float, TechniqueFunc]]:
    """Return the authoritative technique ordering (lazy-loaded to avoid circular imports)."""
    global _TECHNIQUE_ORDER
    if _TECHNIQUE_ORDER is None:
        from .singles import hidden_single_box, hidden_single_line, naked_single
        from .intersections import pointing_pair, claiming
        from .subsets import naked_pair, hidden_pair, naked_triple
        from .fish import x_wing, swordfish
        from .wings import xy_wing
        from .uniqueness import unique_rectangle

        _TECHNIQUE_ORDER = [
            ('hidden_single_box', 1.2, hidden_single_box),
            ('hidden_single_line', 1.5, hidden_single_line),
            ('naked_single', 2.3, naked_single),
            ('pointing_pair', 2.6, pointing_pair),
            ('claiming', 2.8, claiming),
            ('naked_pair', 3.0, naked_pair),
            ('x_wing', 3.2, x_wing),
            ('hidden_pair', 3.4, hidden_pair),
            ('naked_triple', 3.6, naked_triple),
            ('swordfish', 3.8, swordfish),
            ('xy_wing', 4.2, xy_wing),
            ('unique_rectangle', 4.5, unique_rectangle),
        ]
    return _TECHNIQUE_ORDER
