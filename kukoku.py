"""Kukoku — Newspaper Sudoku Generator

Generates dated sudoku puzzle pairs (MIDDELS + VANSKELIG).
Each day gets its own JSON file named by date (e.g. 2026-04-17.json),
ready for the InDesign fill_sudoku.jsx script to consume.

Just run it and press Enter twice: it finds the newest puzzle file in
the puzzles/ folder and generates the next two months from there.

With --auto it runs without any prompts and simply tops up the puzzles/
folder so that it always covers at least two months ahead of today
(used by the scheduled GitHub Actions workflow).
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta

DATED_FILE = re.compile(r'^(\d{4}-\d{2}-\d{2})\.json$')


def find_latest_puzzle_date(output_dir: str) -> date | None:
    """Return the most recent date among existing YYYY-MM-DD.json files."""
    latest = None
    try:
        names = os.listdir(output_dir)
    except OSError:
        return None
    for name in names:
        m = DATED_FILE.match(name)
        if not m:
            continue
        try:
            d = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if latest is None or d > latest:
            latest = d
    return latest


def add_months(d: date, months: int) -> date:
    """Return the same day-of-month `months` later (clamped to month end)."""
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    # Clamp day to the target month's length (e.g. Jan 31 + 1 month -> Feb 28)
    for day in range(d.day, d.day - 4, -1):
        try:
            return date(year, month, day)
        except ValueError:
            continue
    raise ValueError(f"Cannot add {months} months to {d}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--auto', action='store_true',
        help='No prompts: top up puzzles/ to cover two months ahead of today.')
    args = parser.parse_args()

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, 'puzzles')

    # When running from a plain source checkout without the package
    # installed, make src/sudokugen importable.
    if not getattr(sys, 'frozen', False):
        try:
            import sudokugen  # noqa: F401
        except ImportError:
            sys.path.insert(0, os.path.join(base_dir, 'src'))

    print("Kukoku — Newspaper Sudoku Generator")
    print("=" * 40)
    print()

    # Default start date: the day after the newest existing puzzle file,
    # so consecutive runs continue the sequence with no gap.
    latest = find_latest_puzzle_date(output_dir)
    if latest is not None:
        default_start = latest + timedelta(days=1)
        print(f"Newest puzzle on file: {latest.isoformat()}")
    else:
        default_start = date.today() + timedelta(days=1)

    if args.auto:
        # Unattended mode: extend coverage through two months from today.
        start_date = default_start
        target_end = add_months(date.today(), 2)
        num_days = (target_end - start_date).days + 1
        if num_days < 1:
            print(f"Already covered through {latest.isoformat()} "
                  f"(target: {target_end.isoformat()}). Nothing to do.")
            return
    else:
        date_input = input(f"Start date [{default_start.isoformat()}]: ").strip()
        if date_input == '':
            start_date = default_start
        else:
            try:
                start_date = date.fromisoformat(date_input)
            except ValueError:
                print(f"  Invalid date format. Use YYYY-MM-DD.")
                input("Press Enter to exit...")
                sys.exit(1)

        # Default length: exactly two calendar months from the start date.
        default_days = (add_months(start_date, 2) - start_date).days
        days_input = input(f"Number of days [{default_days} = 2 months]: ").strip()
        num_days = default_days
        if days_input:
            try:
                num_days = int(days_input)
                if num_days < 1:
                    raise ValueError
            except ValueError:
                print(f"  Invalid number, using {default_days}.")
                num_days = default_days

    end_date = start_date + timedelta(days=num_days - 1)
    print()
    print(f"Generating {num_days} days: "
          f"{start_date.isoformat()} through {end_date.isoformat()}")
    print()
    os.makedirs(output_dir, exist_ok=True)

    from sudokugen.pipeline import generate_one
    from sudokugen.output import puzzle_pair_to_dated_json

    t0 = time.perf_counter()
    generated = 0
    skipped = 0

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.isoformat()
        filename = f"{date_str}.json"
        filepath = os.path.join(output_dir, filename)

        # Never overwrite a puzzle that may already have been published.
        if os.path.exists(filepath):
            print(f"  {filename}  already exists, skipping")
            skipped += 1
            continue

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
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        generated += 1

        print(f"  {filename}  (MIDDELS SE {middels.se_rating:.1f}, "
              f"VANSKELIG SE {vanskelig.se_rating:.1f})")

    elapsed = time.perf_counter() - t0
    print()
    print(f"Done — {generated} files saved to {output_dir}"
          + (f" ({skipped} already existed)" if skipped else ""))
    print(f"Time: {elapsed:.1f}s")
    if not args.auto:
        print()
        input("Press Enter to exit...")


if __name__ == '__main__':
    main()
