# sudokugen

Newspaper-quality sudoku generator. For every day it produces:

- `puzzles/YYYY-MM-DD.json` — the MIDDELS and VANSKELIG puzzle pair with
  solutions and ratings (see [Difficulty](#difficulty)).
- `pdfs/sudoku-YYYY-MM-DD.pdf` — **the standard print-ready output**: an
  80 × 234 mm newspaper column with both puzzle grids and *the same day's*
  solutions at the bottom, printed upside down (turn the paper around and
  they read normally, MIDDELS on the left). There is no sudoku on Sundays:
  no Sunday files are generated. Rendered by
  `src/sudokugen/column.py` with geometry measured from the production
  InDesign original and Trade Gothic digit outlines (subset in
  `src/sudokugen/data/`), so it is pixel-faithful to the paper's layout
  with no fonts to install.

Pages up to and including 2026-10-27 printed the *previous* publishing
day's solutions instead (Saturday's on a Monday), right side up;
re-rendering one of those days still reproduces what was printed.

## Difficulty

Which generator level each puzzle uses is set at the top of `kukoku.py`:

| Setting | MIDDELS | VANSKELIG | Used |
|---|---|---|---|
| `original` | medium | hard | through 2026-10-27 |
| `easier` | easy | medium | from 2026-10-28 (current) |

To switch, change `ACTIVE_DIFFICULTY` in `kukoku.py`. Only newly generated
days are affected, since kukoku never overwrites existing files, so to change
days that already exist, move their JSON and PDF files out of `puzzles/` and
`pdfs/` and run kukoku again. Each day's JSON records the level used
(`"difficulty"`).

The `original`-difficulty puzzles that had already been generated for
2026-10-28 through 2026-12-08 when the switch was made are kept in
[`archive/original-difficulty/`](archive/original-difficulty/).

## Where the sudokus are

In the [`puzzles/`](puzzles/) (JSON) and [`pdfs/`](pdfs/) (print PDFs)
folders.

**You normally don't have to generate anything.** A GitHub Actions workflow
runs on the 1st of every month and tops up `puzzles/` so it always covers at
least two months ahead. To get the newest files onto the work computer, just
download the repo like before: green **Code** button → **Download ZIP** →
extract into Downloads.

If you ever want more puzzles right now: repo page → **Actions** tab →
**Generate puzzles** → **Run workflow** button. A minute later the new files
are on main.

## Using it from code (e.g. a website generator)

```python
from datetime import date
from sudokugen.column import render_day

render_day(date(2026, 9, 26), 'puzzles', 'pdfs')  # -> pdfs/sudoku-2026-09-26.pdf
```

`sudokugen.pipeline.generate_one('easy'|'medium'|'hard'|'expert')` makes new puzzles;
`sudokugen.output.puzzle_pair_to_dated_json` writes the daily JSON.
`kukoku.py --auto` does all of it non-interactively (top up JSON coverage
two months ahead, then render every missing PDF).

## Laying out a page in InDesign

1. Open the sudoku document in InDesign.
2. Window → Utilities → Scripts → run `indesign/fill_sudoku.jsx`.
3. Enter the date; the script loads `puzzles/<date>.json` and fills the grids.

If the repo folder moves to a new place or machine, update
`CONFIG.puzzleFolder` at the top of `indesign/fill_sudoku.jsx`.

## Generating on a computer instead (optional)

Download `kukoku.exe` from the
[kukoku-exe release](../../releases/tag/kukoku-exe) (built automatically by
the **Build kukoku.exe** workflow — no Python needed). Put it in the
sudokugen folder next to `puzzles/` and double-click it, then press **Enter
twice**: it continues from the newest puzzle on file and generates the next
two months. It never overwrites existing files.

With Python installed, `python kukoku.py` does the same thing, and
`python kukoku.py --auto` runs it without prompts (that's what the monthly
workflow uses).

## Library CLI

The underlying generator also has a CLI (`pip install -e .` then `sudokugen
generate|rate|show|newspaper`), but the daily batches only need `kukoku.py`.
