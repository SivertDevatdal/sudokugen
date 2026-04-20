"""Technique solver orchestrator — applies techniques in strict difficulty order."""

from __future__ import annotations

from .types import TechniqueStep, SolvePath, NUM_CELLS, candidate_count
from .grid import SolverGrid
from .techniques import get_technique_order


def solve_with_techniques(
    givens: list[int],
    max_difficulty: float = 5.0,
) -> SolvePath | None:
    """Solve a puzzle using human techniques in ascending difficulty order.

    Returns the solve path if solvable without bifurcation and within
    max_difficulty. Returns None if the puzzle requires guessing or
    techniques harder than max_difficulty.

    Uses SolverGrid (non-propagating) so that every logical step is
    explicitly discovered and recorded by the technique functions.
    The solver always restarts from the easiest technique after each
    successful application, ensuring a canonical solve path.
    """
    grid = SolverGrid(givens)
    path: SolvePath = []
    techniques = get_technique_order()

    while not grid.is_complete():
        progress = False

        for name, difficulty, func in techniques:
            if difficulty > max_difficulty:
                continue

            result = func(grid)
            if result is None:
                continue

            # Apply assignments
            for cell, digit in result.assignments:
                grid.place(cell, digit)

            # Apply eliminations
            for cell, digit in result.eliminations:
                grid.eliminate(cell, digit)

            # Record step
            primary_cell = result.assignments[0][0] if result.assignments else -1
            primary_digit = result.assignments[0][1] if result.assignments else 0
            path.append(TechniqueStep(
                technique=result.technique,
                difficulty=result.difficulty,
                cell=primary_cell,
                digit=primary_digit,
                opportunities=result.opportunities,
            ))

            progress = True
            break  # restart from easiest technique

        if not progress:
            return None  # stuck — requires bifurcation

    return path
