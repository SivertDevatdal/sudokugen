# sudokugen

Newspaper-quality sudoku generator. Produces one JSON file per day with a
MIDDELS (medium) and VANSKELIG (hard) puzzle pair, which the InDesign script
lays out on the page.

## Where the sudokus are

In the [`puzzles/`](puzzles/) folder — one `YYYY-MM-DD.json` file per day.

**You normally don't have to generate anything.** A GitHub Actions workflow
runs on the 1st of every month and tops up `puzzles/` so it always covers at
least two months ahead. To get the newest files onto the work computer, just
download the repo like before: green **Code** button → **Download ZIP** →
extract into Downloads.

If you ever want more puzzles right now: repo page → **Actions** tab →
**Generate puzzles** → **Run workflow** button. A minute later the new files
are on main.

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
