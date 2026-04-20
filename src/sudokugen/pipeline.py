"""Batch generation pipeline with multiprocessing."""

from __future__ import annotations

import random
from multiprocessing import Pool
from typing import Any

from .types import PuzzleResult, NUM_CELLS
from .generator import generate_full_grid
from .remover import remove_clues_for_difficulty
from .solver import solve_with_techniques
from .quality import compute_se_rating, has_soul, analyze_solve_path
from .classifier import classify_difficulty, max_difficulty_for_tier


def generate_one(
    difficulty: str = 'medium',
    max_attempts: int = 200,
    require_soul: bool = True,
) -> PuzzleResult | None:
    """Generate a single puzzle of the requested difficulty.

    Runs the full pipeline: generate → remove → solve → classify → filter.
    Returns None if unable to produce a matching puzzle within max_attempts.
    """
    max_diff = max_difficulty_for_tier(difficulty)

    for _ in range(max_attempts):
        # 1. Generate full grid
        solution = generate_full_grid()

        # 2. Remove clues with symmetry
        puzzle = remove_clues_for_difficulty(solution, difficulty)
        if puzzle is None:
            continue

        # 3. Solve with techniques
        path = solve_with_techniques(puzzle, max_difficulty=max_diff)
        if path is None:
            continue

        # 4. Compute metrics
        se = compute_se_rating(path)
        clue_count = sum(1 for v in puzzle if v != 0)
        tier = classify_difficulty(se, clue_count)

        # 5. Check tier match
        if tier != difficulty:
            continue

        # 6. Quality filter
        soul = has_soul(path, se_rating=se)
        if require_soul and not soul:
            continue

        # 7. Build result
        metrics = analyze_solve_path(path)
        return PuzzleResult(
            grid=puzzle,
            solution=solution,
            solve_path=path,
            se_rating=se,
            difficulty_tier=difficulty,
            clue_count=clue_count,
            has_soul=soul,
            metadata=metrics,
        )

    return None


def _worker(args: tuple[str, int, bool]) -> PuzzleResult | None:
    """Worker function for multiprocessing."""
    difficulty, max_attempts, require_soul = args
    return generate_one(difficulty, max_attempts, require_soul)


def generate_batch(
    difficulty: str = 'medium',
    count: int = 10,
    workers: int = 4,
    max_attempts_per_puzzle: int = 200,
    require_soul: bool = True,
) -> list[PuzzleResult]:
    """Generate multiple puzzles using multiprocessing.

    Launches more tasks than needed to account for failures,
    collecting results until count puzzles are obtained.
    """
    results: list[PuzzleResult] = []
    # Launch extra tasks to account for generation failures
    tasks_to_launch = count * 3
    args = [(difficulty, max_attempts_per_puzzle, require_soul)] * tasks_to_launch

    if workers <= 1:
        for a in args:
            if len(results) >= count:
                break
            r = _worker(a)
            if r is not None:
                results.append(r)
    else:
        with Pool(processes=workers) as pool:
            for r in pool.imap_unordered(_worker, args):
                if r is not None:
                    results.append(r)
                if len(results) >= count:
                    pool.terminate()
                    break

    return results[:count]
