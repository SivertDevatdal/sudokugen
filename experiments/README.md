# Easier-middels difficulty test

A one-off experiment to judge a slightly easier MIDDELS on paper. It does
not change the production generator — it only reads sudokugen's primitives.

`gen_easier_middels_test.py` builds 9 puzzles in three sets, each pinned to
a fixed Sudoku-Explainer rung so the levels are clearly distinct, and lays
them out on two A4 pages (puzzles + matching solutions), labelled A1–C3:

| Set | SE rung | Hardest technique needed | Clues | vs. today |
|-----|---------|--------------------------|-------|-----------|
| A   | 2.3     | naked single             | 30–33 | today's level (reference) |
| B   | 1.5     | hidden single (row/col)  | 32–35 | one notch easier |
| C   | 1.2     | hidden single (box only) | 34–38 | easiest |

Today's MIDDELS batch sits almost entirely at SE 2.3, so A is the control,
B and C are the candidates for a gentler medium.

Run: `python experiments/gen_easier_middels_test.py`
Output: `experiments/output/middels-test-{puzzles,solutions}.pdf`
The seed is fixed, so re-running reproduces the same nine puzzles.

## Findings: why Set B (SE 1.5) is preferred

`analyze_difficulty.py` reads the solver's step-by-step path and measures
what each level's solve *feels* like. Averaged over 40 puzzles per level:

| level    | clues | naked singles/puzzle | bottlenecks* | mean moves available |
|----------|-------|----------------------|--------------|----------------------|
| A SE 2.3 | 31    | 1.4                  | 12.9         | 2.78                 |
| B SE 1.5 | 33    | 0.0                  | 7.3          | 3.59                 |
| C SE 1.2 | 36    | 0.0                  | 1.5          | 6.36                 |

\* bottleneck = a step where only ONE move exists on the whole board.

Reading:
- **B is the hardest level that stays 100% "hidden single" logic** — every
  placement is a positive "this digit has exactly one home" deduction, and
  it still needs the wider row/column scans (line hidden singles).
- **A crosses into "naked single" territory** ~1–2 times per puzzle: the
  where-does-X-go scan runs dry and you must switch to tracking a cell's
  leftover candidates — a different, bookkeeping-heavy mode — while the
  board is much tighter (~13 forced single-move bottlenecks). That mode
  switch + tightness is the "too hard / tedious" feedback.
- **C** is box-scanning only and over-clued: 6+ moves available at all
  times, almost never a bottleneck → too easy.

Controlled check (clues fixed at 32, only the ceiling varies) confirms the
driver is the technique, not the clue count:

| ceiling @ 32 clues | naked/puzzle | bottlenecks | mean moves |
|--------------------|--------------|-------------|------------|
| 1.5                | 0.00         | 7.5         | 3.59       |
| 2.3                | 1.20         | 12.3        | 2.93       |
