"""Kukoku — Newspaper Sudoku Generator

Generates 30 days of dated sudoku puzzle pairs (MIDDELS + VANSKELIG).
Each day gets its own JSON file named by date (e.g. 2026-04-17.json),
ready for the InDesign fill_sudoku.jsx script to consume.
"""

import json
import os
import sys
import time
from datetime import date, datetime, timedelta


def main() -> None:
    if getattr(sys, 'frozen', False):
        output_dir = os.path.join(os.path.dirname(sys.executable), 'puzzles')
    else:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'puzzles')

    print("Kukoku — Newspaper Sudoku Generator")
    print("=" * 40)
    print()

    # Ask for start date
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    date_input = input(f"Start date [{tomorrow}]: ").strip()
    if date_input == '':
        start_date = date.today() + timedelta(days=1)
    else:
        try:
            start_date = date.fromisoformat(date_input)
        except ValueError:
            print(f"  Invalid date format. Use YYYY-MM-DD.")
            input("Press Enter to exit...")
            sys.exit(1)

    # Ask for number of days
    days_input = input("Number of days [30]: ").strip()
    num_days = 30
    if days_input:
        try:
            num_days = int(days_input)
            if num_days < 1:
                raise ValueError
        except ValueError:
            print("  Invalid number, using 30.")
            num_days = 30

    print()
    os.makedirs(output_dir, exist_ok=True)

    from sudokugen.pipeline import generate_one
    from sudokugen.output import puzzle_pair_to_dated_json

    t0 = time.perf_counter()
    print(f"Generating {num_days} days of puzzles...")
    print()

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.isoformat()

        # Generate MIDDELS (medium)
        middels = generate_one('medium', require_soul=True)
        if middels is None:
            middels = generate_one('medium', require_soul=False)
        if middels is None:
            print(f"  {date_str}  FAILED (middels)")
            continue

        # Generate VANSKELIG (hard)
        vanskelig = generate_one('hard', max_attempts=500, require_soul=True)
        if vanskelig is None:
            vanskelig = generate_one('hard', max_attempts=500, require_soul=False)
        if vanskelig is None:
            print(f"  {date_str}  FAILED (vanskelig)")
            continue

        # Save JSON
        data = puzzle_pair_to_dated_json(date_str, middels, vanskelig)
        filename = f"{date_str}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"  {filename}  (MIDDELS SE {middels.se_rating:.1f}, "
              f"VANSKELIG SE {vanskelig.se_rating:.1f})")

    elapsed = time.perf_counter() - t0
    print()
    print(f"Done — {num_days} files saved to {output_dir}")
    print(f"Time: {elapsed:.1f}s")
    print()
    input("Press Enter to exit...")


if __name__ == '__main__':
    main()
