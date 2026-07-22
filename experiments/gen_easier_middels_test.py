"""Difficulty experiment: three gentler 'middels' candidate sets on A4.

Standalone test harness — it does NOT touch the production generator or
its difficulty settings. It only *reads* the existing sudokugen
primitives to build 9 puzzles across three difficulty ceilings so the
feel of a slightly easier medium can be judged on paper.

Layout (both pages, same labels):
    A1 A2 A3   ← Set A: ceiling SE 2.3 (naked single), extra clues
    B1 B2 B3   ← Set B: ceiling SE 1.5 (hidden singles only)
    C1 C2 C3   ← Set C: ceiling SE 1.2 (box hidden singles), most clues

Outputs two A4 PDFs: the puzzles and the matching solutions.
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from sudokugen.generator import generate_full_grid
from sudokugen.remover import remove_clues
from sudokugen.solver import solve_with_techniques
from sudokugen.quality import compute_se_rating

# (label prefix, exact target SE, clue range) for each set. Pinning the
# SE to a specific rung keeps the three sets clearly distinct:
#   A 2.3 = today's level (needs naked singles) — reference point
#   B 1.5 = one notch easier (hidden singles are the hardest step)
#   C 1.2 = easiest (only box hidden singles), with the most clues
SETS = [
    ('A', 2.3, (30, 33)),
    ('B', 1.5, (32, 35)),
    ('C', 1.2, (34, 38)),
]
SEED = 20260722


def make_puzzle(target_se: float, clue_range: tuple[int, int],
                seen: set[tuple[int, ...]], tries: int = 8000):
    """Return (grid, solution, se, clues) whose hardest step is target_se."""
    lo, hi = clue_range
    for _ in range(tries):
        solution = generate_full_grid()
        target = random.randint(lo, hi)
        puzzle = remove_clues(solution, target_clues=target, min_clues=lo)
        if puzzle is None:
            continue
        clues = sum(1 for v in puzzle if v)
        if not (lo <= clues <= hi):
            continue
        path = solve_with_techniques(puzzle, max_difficulty=target_se)
        if path is None:            # needs a technique above the target
            continue
        se = compute_se_rating(path)
        if abs(se - target_se) > 0.05:   # must top out exactly at target
            continue
        key = tuple(puzzle)
        if key in seen:
            continue
        seen.add(key)
        return puzzle, solution, se, clues
    raise RuntimeError(f'could not build a puzzle at SE {target_se}')


def build() -> list[dict]:
    random.seed(SEED)
    seen: set[tuple[int, ...]] = set()
    out = []
    for prefix, target_se, clue_range in SETS:
        for n in range(1, 4):
            grid, sol, se, clues = make_puzzle(target_se, clue_range, seen)
            out.append({'label': f'{prefix}{n}', 'target_se': target_se,
                        'grid': grid, 'solution': sol,
                        'se': se, 'clues': clues})
            print(f'  {prefix}{n}: SE {se:.1f}, {clues} clues '
                  f'(target {target_se})')
    return out


# ---- A4 rendering -----------------------------------------------------

PAGE_W, PAGE_H = A4
MARGIN = 14 * mm
GRID = 49 * mm
CELL = GRID / 9
COL_W = (PAGE_W - 2 * MARGIN) / 3


def _draw_grid(c: Canvas, values, x0: float, y0: float) -> None:
    """Draw a 9x9 grid with top-left at (x0, y0); values 0 = blank."""
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineCap(2)
    for i in range(10):
        w = 1.4 if i % 3 == 0 else 0.4
        c.setLineWidth(w)
        c.line(x0 + i * CELL, y0, x0 + i * CELL, y0 - GRID)
        c.line(x0, y0 - i * CELL, x0 + GRID, y0 - i * CELL)
    fs = CELL * 0.62
    c.setFont('Helvetica', fs)
    # Helvetica cap height is 0.718 em; drop the baseline by half of that
    # so the digit is optically centred on the cell midpoint.
    baseline_drop = 0.718 * fs / 2
    for r in range(9):
        for col in range(9):
            v = values[r * 9 + col]
            if v:
                cx = x0 + col * CELL + CELL / 2
                cy = y0 - r * CELL - CELL / 2
                c.drawCentredString(cx, cy - baseline_drop, str(v))


def _render_page(path: str, puzzles: list[dict], title: str,
                 key: str) -> None:
    c = Canvas(path, pagesize=A4)
    c.setFont('Helvetica-Bold', 15)
    c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN, title)

    top = PAGE_H - MARGIN - 12 * mm
    row_h = (top - MARGIN) / 3
    for idx, pz in enumerate(puzzles):
        row, col = divmod(idx, 3)
        gx = MARGIN + col * COL_W + (COL_W - GRID) / 2
        band_top = top - row * row_h
        c.setFont('Helvetica-Bold', 11)
        c.drawString(gx, band_top - 4 * mm, pz['label'])
        _draw_grid(c, pz[key], gx, band_top - 7 * mm)
    c.save()


def main() -> None:
    out_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(out_dir, exist_ok=True)
    print('Generating 9 test puzzles (3 sets x 3):')
    puzzles = build()

    puz_pdf = os.path.join(out_dir, 'middels-test-puzzles.pdf')
    sol_pdf = os.path.join(out_dir, 'middels-test-solutions.pdf')
    _render_page(puz_pdf, puzzles,
                 'MIDDELS — vanskelighetstest (A/B/C)', 'grid')
    _render_page(sol_pdf, puzzles,
                 'MIDDELS — vanskelighetstest — fasit (A/B/C)', 'solution')
    print(f'\nWrote:\n  {puz_pdf}\n  {sol_pdf}')


if __name__ == '__main__':
    main()
