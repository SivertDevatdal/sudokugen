"""Why is Set B (SE 1.5) the preferred medium? — solve-experience analysis.

Reads the solver's step-by-step path for puzzles at each of the three test
levels and measures what the solve actually *feels* like:

  * technique mix — what kind of deduction each placement needs
      1.2 hidden single (box)   — scan one box
      1.5 hidden single (line)  — scan a row/column
      2.3 naked single          — track a cell's remaining candidates
  * naked-single reliance — how often the pleasant "where does X go?"
      scanning runs dry and you must switch to candidate bookkeeping
  * flow — how many moves are available at each step (opportunities);
      steps with exactly one available move are "bottlenecks" (you must
      find that one specific move to progress)

Run: python experiments/analyze_difficulty.py
"""

from __future__ import annotations

import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sudokugen.solver import solve_with_techniques

from gen_easier_middels_test import SETS, make_puzzle

LEVEL_NAME = {'A': 'A  SE 2.3', 'B': 'B  SE 1.5', 'C': 'C  SE 1.2'}
SAMPLES_PER_LEVEL = 40


def solve_metrics(grid: list[int]) -> dict:
    """Characterise the human solve of `grid`."""
    path = solve_with_techniques(grid, max_difficulty=5.0)
    assert path is not None
    diffs = [round(s.difficulty, 1) for s in path]
    opps = [s.opportunities for s in path]
    n = len(path)
    counts = Counter(diffs)
    return {
        'clues': sum(1 for v in grid if v),
        'steps': n,
        'pct_box': 100 * counts.get(1.2, 0) / n,       # 1.2 hidden single box
        'pct_line': 100 * counts.get(1.5, 0) / n,      # 1.5 hidden single line
        'pct_naked': 100 * counts.get(2.3, 0) / n,     # 2.3 naked single
        'n_naked': counts.get(2.3, 0),
        'mean_opp': sum(opps) / n,
        'min_opp': min(opps),
        'bottlenecks': sum(1 for o in opps if o == 1),
    }


def summarise(rows: list[dict]) -> dict:
    keys = ['clues', 'steps', 'pct_box', 'pct_line', 'pct_naked',
            'n_naked', 'mean_opp', 'bottlenecks']
    return {k: sum(r[k] for r in rows) / len(rows) for k in keys}


def main() -> None:
    # --- the exact 9 puzzles that were rated (fixed seed) ---
    random.seed(20260722)
    seen: set[tuple[int, ...]] = set()
    print('The nine rated puzzles')
    print(f"{'':4} {'clues':>5} {'steps':>5} {'box%':>5} {'line%':>6} "
          f"{'naked%':>7} {'#naked':>7} {'meanOpp':>8} {'botl':>5}")
    for prefix, target, clue_range in SETS:
        for n in range(1, 4):
            grid, _sol, _se, _cl = make_puzzle(target, clue_range, seen)
            m = solve_metrics(grid)
            print(f'{prefix}{n:<3} {m["clues"]:>5} {m["steps"]:>5} '
                  f'{m["pct_box"]:>5.0f} {m["pct_line"]:>6.0f} '
                  f'{m["pct_naked"]:>7.0f} {m["n_naked"]:>7} '
                  f'{m["mean_opp"]:>8.2f} {m["bottlenecks"]:>5}')

    # --- larger fresh sample per level to see if it generalises ---
    random.seed(4242)
    seen = set()
    print(f'\nAveraged over {SAMPLES_PER_LEVEL} fresh puzzles per level')
    print(f"{'level':10} {'clues':>5} {'steps':>5} {'box%':>5} {'line%':>6} "
          f"{'naked%':>7} {'#naked':>7} {'meanOpp':>8} {'botl':>5}")
    for prefix, target, clue_range in SETS:
        rows = []
        for _ in range(SAMPLES_PER_LEVEL):
            grid, _s, _se, _c = make_puzzle(target, clue_range, seen)
            rows.append(solve_metrics(grid))
        s = summarise(rows)
        print(f'{LEVEL_NAME[prefix]:10} {s["clues"]:>5.0f} {s["steps"]:>5.0f} '
              f'{s["pct_box"]:>5.0f} {s["pct_line"]:>6.0f} '
              f'{s["pct_naked"]:>7.0f} {s["n_naked"]:>7.1f} '
              f'{s["mean_opp"]:>8.2f} {s["bottlenecks"]:>5.1f}')


if __name__ == '__main__':
    main()
