"""Command-line interface for sudokugen."""

from __future__ import annotations

import argparse
import json
import sys
import time

from .output import (
    puzzle_to_grid_display, puzzle_to_string, string_to_puzzle,
    puzzle_to_json, batch_to_json,
)
from .pipeline import generate_one, generate_batch
from .solver import solve_with_techniques
from .quality import compute_se_rating, has_soul, analyze_solve_path
from .classifier import classify_difficulty


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate one or more puzzles."""
    difficulty = args.difficulty
    count = args.count
    require_soul = not args.no_soul

    if count == 1:
        t0 = time.perf_counter()
        result = generate_one(difficulty, require_soul=require_soul)
        elapsed = time.perf_counter() - t0

        if result is None:
            print(f"Failed to generate a {difficulty} puzzle. Try again.", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(puzzle_to_json(result), indent=2))
        else:
            print(puzzle_to_grid_display(result.grid))
            print()
            print(f"Puzzle:     {puzzle_to_string(result.grid)}")
            print(f"Solution:   {puzzle_to_string(result.solution)}")
            print(f"Difficulty: {result.difficulty_tier} (SE {result.se_rating:.1f})")
            print(f"Clues:      {result.clue_count}")
            print(f"Techniques: {', '.join(sorted({s.technique for s in result.solve_path}))}")
            print(f"Has soul:   {result.has_soul}")
            print(f"Generated in {elapsed:.2f}s")
    else:
        t0 = time.perf_counter()
        results = generate_batch(
            difficulty, count,
            workers=args.workers,
            require_soul=require_soul,
        )
        elapsed = time.perf_counter() - t0

        if not results:
            print(f"Failed to generate any {difficulty} puzzles.", file=sys.stderr)
            sys.exit(1)

        if args.output:
            data = batch_to_json(results)
            with open(args.output, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Wrote {len(results)} puzzles to {args.output} in {elapsed:.2f}s")
        else:
            data = batch_to_json(results)
            print(json.dumps(data, indent=2))


def cmd_rate(args: argparse.Namespace) -> None:
    """Rate an existing puzzle."""
    puzzle = string_to_puzzle(args.puzzle)
    path = solve_with_techniques(puzzle)

    if path is None:
        print("Could not solve with available techniques (requires guessing).")
        sys.exit(1)

    se = compute_se_rating(path)
    clue_count = sum(1 for v in puzzle if v != 0)
    tier = classify_difficulty(se, clue_count)
    soul = has_soul(path)
    metrics = analyze_solve_path(path)

    if args.json:
        print(json.dumps({
            'difficulty': tier,
            'se_rating': se,
            'clue_count': clue_count,
            'has_soul': soul,
            'techniques': sorted({s.technique for s in path}),
            'metrics': metrics,
        }, indent=2))
    else:
        print(f"Difficulty: {tier} (SE {se:.1f})")
        print(f"Clues:      {clue_count}")
        print(f"Steps:      {len(path)}")
        print(f"Techniques: {', '.join(sorted({s.technique for s in path}))}")
        print(f"Has soul:   {soul}")
        print(f"Metrics:    {metrics}")


def cmd_newspaper(args: argparse.Namespace) -> None:
    """Generate two puzzles (easy + hard) as four vector PDFs for newspaper import."""
    import os
    from .pdf import render_grid_pdf

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    t0 = time.perf_counter()

    # Generate easy puzzle
    easy = generate_one('easy', require_soul=True)
    if easy is None:
        print("Failed to generate easy puzzle.", file=sys.stderr)
        sys.exit(1)

    # Generate hard puzzle
    hard = generate_one('hard', max_attempts=500, require_soul=True)
    if hard is None:
        # Fall back to medium if hard fails
        hard = generate_one('hard', max_attempts=500, require_soul=False)
    if hard is None:
        print("Failed to generate hard puzzle.", file=sys.stderr)
        sys.exit(1)

    elapsed = time.perf_counter() - t0

    # Render four PDFs
    easy_puzzle_path = os.path.join(output_dir, 'easy_puzzle.pdf')
    hard_puzzle_path = os.path.join(output_dir, 'hard_puzzle.pdf')
    easy_solution_path = os.path.join(output_dir, 'easy_solution.pdf')
    hard_solution_path = os.path.join(output_dir, 'hard_solution.pdf')

    render_grid_pdf(easy_puzzle_path, easy.grid, label='EASY')
    render_grid_pdf(hard_puzzle_path, hard.grid, label='HARD')
    render_grid_pdf(easy_solution_path, easy.solution, is_solution=True, label='EASY')
    render_grid_pdf(hard_solution_path, hard.solution, is_solution=True, label='HARD')

    print(f"Generated in {elapsed:.2f}s")
    print(f"  {easy_puzzle_path}")
    print(f"  {hard_puzzle_path}")
    print(f"  {easy_solution_path}")
    print(f"  {hard_solution_path}")
    print()
    print(f"Easy:  SE {easy.se_rating:.1f}, {easy.clue_count} clues, "
          f"techniques: {', '.join(sorted({s.technique for s in easy.solve_path}))}")
    print(f"Hard:  SE {hard.se_rating:.1f}, {hard.clue_count} clues, "
          f"techniques: {', '.join(sorted({s.technique for s in hard.solve_path}))}")


def cmd_show(args: argparse.Namespace) -> None:
    """Pretty-print a puzzle."""
    puzzle = string_to_puzzle(args.puzzle)
    print(puzzle_to_grid_display(puzzle))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='sudokugen',
        description='Newspaper-quality sudoku puzzle generator',
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # generate
    gen = sub.add_parser('generate', help='Generate sudoku puzzles')
    gen.add_argument('-d', '--difficulty', default='medium',
                     choices=['easy', 'medium', 'hard', 'expert'])
    gen.add_argument('-n', '--count', type=int, default=1)
    gen.add_argument('-w', '--workers', type=int, default=4)
    gen.add_argument('-o', '--output', help='Output JSON file (for batch)')
    gen.add_argument('--json', action='store_true', help='Output as JSON')
    gen.add_argument('--no-soul', action='store_true',
                     help='Skip soul quality filter')
    gen.set_defaults(func=cmd_generate)

    # newspaper
    news = sub.add_parser('newspaper',
                          help='Generate easy + hard puzzle PDFs for newspaper')
    news.add_argument('-o', '--output-dir', default='.',
                      help='Output directory for PDFs (default: current)')
    news.set_defaults(func=cmd_newspaper)

    # rate
    rate = sub.add_parser('rate', help='Rate an existing puzzle')
    rate.add_argument('puzzle', help='81-char puzzle string (. or 0 for empty)')
    rate.add_argument('--json', action='store_true')
    rate.set_defaults(func=cmd_rate)

    # show
    show = sub.add_parser('show', help='Pretty-print a puzzle')
    show.add_argument('puzzle', help='81-char puzzle string')
    show.set_defaults(func=cmd_show)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
