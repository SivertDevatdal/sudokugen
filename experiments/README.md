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
