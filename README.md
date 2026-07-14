# sudokugen

Newspaper-quality sudoku generator. Produces one JSON file per day with a
MIDDELS (medium) and VANSKELIG (hard) puzzle pair, which the InDesign script
lays out on the page.

## Generating the next batch

Run kukoku and press **Enter twice** — that's it:

```
python kukoku.py        (or double-click kukoku.exe)
```

It finds the newest file in `puzzles/`, starts the day after, and generates
exactly two months. Existing files are never overwritten, so running it twice
by accident is harmless. To use a different start date or length, type them
at the prompts instead of pressing Enter.

Puzzles currently on file run through the date of the newest
`puzzles/YYYY-MM-DD.json`.

## Laying out a page in InDesign

1. Open the sudoku document in InDesign.
2. Window → Utilities → Scripts → run `indesign/fill_sudoku.jsx`.
3. Enter the date; the script loads `puzzles/<date>.json` and fills the grids.

If the repo moves to a new folder or machine, update `CONFIG.puzzleFolder`
at the top of `indesign/fill_sudoku.jsx`.

## Rebuilding kukoku.exe (Windows)

Run `build_exe.bat` — it installs PyInstaller and builds `dist\kukoku.exe`.
Rebuild whenever `kukoku.py` or the generator library changes. Put the exe
next to the `puzzles/` folder (it writes to `puzzles/` beside itself).

## Library CLI

The underlying generator also has a CLI (`pip install -e .` then `sudokugen
generate|rate|show|newspaper`), but the monthly batches only need `kukoku.py`.
