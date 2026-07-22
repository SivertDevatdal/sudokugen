"""Skipday — skip a date in the sudoku batch.

A tiny pop-up tool that lives in the same folder as the rendered
sudoku-YYYY-MM-DD.pdf files. Double-click it, type the date that needs
to be skipped (an unforeseen bank holiday, say), and it slides that day's
puzzle and every one after it forward by one printing slot — still
skipping Sundays, and leaving any earlier holiday gaps alone.

Only the filenames change; the PDF contents are never touched.
"""

import os
import re
import sys
from datetime import date

PDF_RE = re.compile(r'^sudoku-(\d{4}-\d{2}-\d{2})\.pdf$')

TITLE = 'Hopp over dato'


def base_dir() -> str:
    """The folder the tool is running from (next to the PDFs)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def ensure_package(base: str) -> None:
    """Make src/sudokugen importable when running from a source checkout."""
    if not getattr(sys, 'frozen', False):
        try:
            import sudokugen  # noqa: F401
        except ImportError:
            sys.path.insert(0, os.path.join(base, 'src'))


def scan_pdfs(folder: str) -> dict[date, str]:
    """Map each puzzle date to its sudoku-*.pdf filename in `folder`."""
    found: dict[date, str] = {}
    for name in os.listdir(folder):
        m = PDF_RE.match(name)
        if m:
            found[date.fromisoformat(m.group(1))] = name
    return found


def apply_shift(folder: str, files: dict[date, str],
                plan: list[tuple[date, date]]) -> None:
    """Rename files per `plan`, via temp names so nothing is overwritten."""
    temps: list[tuple[str, str]] = []
    for old, _new in plan:
        src = os.path.join(folder, files[old])
        tmp = src + '.moving'
        os.rename(src, tmp)
        temps.append((tmp, f'sudoku-{_new.isoformat()}.pdf'))
    for tmp, final in temps:
        os.rename(tmp, os.path.join(folder, final))


def _preview(skip: date, plan: list[tuple[date, date]]) -> str:
    lines = [f'{o.isoformat()}  →  {n.isoformat()}' for o, n in plan]
    if len(lines) > 6:
        lines = lines[:3] + ['…'] + lines[-2:]
    return (
        f'{skip.isoformat()} hoppes over.\n'
        f'Dette flytter {len(plan)} fil(er):\n\n'
        + '\n'.join(lines)
        + f'\n\nNy sluttdato: {plan[-1][1].isoformat()}\n\nFortsett?'
    )


def main() -> None:
    import tkinter as tk
    from tkinter import messagebox, simpledialog

    from sudokugen.reschedule import plan_holiday_shift

    base = base_dir()
    ensure_package(base)

    root = tk.Tk()
    root.withdraw()

    files = scan_pdfs(base)
    if not files:
        messagebox.showerror(
            TITLE, 'Fant ingen sudoku-PDF-filer i denne mappen.')
        return

    answer = simpledialog.askstring(
        TITLE,
        'Skriv inn datoen som skal hoppes over (ÅÅÅÅ-MM-DD).\n'
        'Alle etterfølgende datoer flyttes fram, søndager hoppes over.')
    if not answer:
        return
    try:
        skip = date.fromisoformat(answer.strip())
    except ValueError:
        messagebox.showerror(
            TITLE, 'Ugyldig dato. Bruk formatet ÅÅÅÅ-MM-DD.')
        return

    plan = plan_holiday_shift(list(files), skip)
    if not plan:
        messagebox.showinfo(
            TITLE,
            f'Ingen fil på {skip.isoformat()} – ingenting å flytte.')
        return

    if not messagebox.askokcancel(TITLE, _preview(skip, plan)):
        return

    apply_shift(base, files, plan)
    messagebox.showinfo(
        TITLE,
        f'Ferdig! {len(plan)} fil(er) ble flyttet.\n'
        f'{skip.isoformat()} er nå tom.')


if __name__ == '__main__':
    main()
