"""Difficulty test sheet — nine puzzles, one per technique rung, on one A4 page.

The sheet exists to calibrate the generator against a human: every puzzle on
it is picked so that its *hardest required step* is a different technique from
all the others, in ascending order of difficulty. Rate them 1–5 on paper and
the ratings map straight back onto the solver's SE scale, which is what
`classifier.py` uses to label puzzles MIDDELS or VANSKELIG.

Rendered output (`render_testsheet_pdf`) is three A4 pages:

1. the test sheet itself — nine grids with a 1–5 rating row under each,
2. the characteristics table — what makes each puzzle what it is,
3. the answer key.

`build_testsheet()` does the generation; it is slow (minutes), because the
rare rungs — a puzzle whose hardest step is a naked triple, say — only turn
up in about one generated puzzle in two hundred.
"""

from __future__ import annotations

import json
import os
import random
from collections import Counter
from dataclasses import dataclass, field
from multiprocessing import Pool
from typing import Any

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from .column import PUZZLE_FONT_PT, PUZZLE_STROKES, _DigitFont
from .output import puzzle_to_string
from .pipeline import generate_one
from .quality import analyze_solve_path
from .types import PuzzleResult, cell_from_rc


@dataclass(frozen=True)
class Rung:
    """One step of the difficulty ladder: the technique that tops the puzzle."""
    technique: str      # solver name of the hardest required technique
    se: float           # its SE difficulty, i.e. the puzzle's SE rating
    name: str           # Norwegian name for the sheet
    what: str           # what the solver has to spot, in one line


# The ladder, easiest first. Every rung is a distinct hardest-technique, so
# the nine puzzles differ in kind and not just in how long they take.
# swordfish (SE 3.8) is missing on purpose — see swordfish_note() below.
LADDER: tuple[Rung, ...] = (
    Rung('naked_single', 2.3, 'Nakent enkelttall',
         'en rute der åtte tall er utelukket, så bare ett blir igjen'),
    Rung('pointing_pair', 2.6, 'Pekende par',
         'et tall som i en boks bare kan stå i én rad/kolonne, og strykes videre ut'),
    Rung('claiming', 2.8, 'Blokkrav',
         'et tall som i en rad/kolonne bare kan stå i én boks, og strykes ut av resten av boksen'),
    Rung('naked_pair', 3.0, 'Nakent par',
         'to ruter i samme enhet med samme to tall — begge tallene strykes hos naboene'),
    Rung('x_wing', 3.2, 'X-Wing',
         'et tall låst i to rader på de samme to kolonnene (eller omvendt)'),
    Rung('hidden_pair', 3.4, 'Skjult par',
         'to tall som bare får plass i de samme to rutene — alt annet i de rutene ryker'),
    Rung('naked_triple', 3.6, 'Nakent trippel',
         'tre ruter som til sammen bare rommer tre tall'),
    Rung('xy_wing', 4.2, 'XY-Wing',
         'tre toerruter i kjede: XY–XZ–YZ, som stryker Z der de to endene ser samme rute'),
    Rung('unique_rectangle', 4.5, 'Unikt rektangel',
         'et mønster som måtte gitt to løsninger — og derfor ikke kan stå'),
)


def swordfish_note(meta: dict[str, Any]) -> str:
    """Why the ladder skips SE 3,8 — stated as what the generation run saw."""
    seen = meta['crux_census'].get('swordfish', 0)
    total = meta['puzzles_generated']
    return (
        f'Swordfish (SE 3,8) står ikke på arket. Løseren tar alltid det '
        f'billigste steget først, og et rutenett som er åpent nok til å by på '
        f'en swordfish har nesten alltid et nakent trippel eller en enklere '
        f'teknikk å ta i stedet — den var vanskeligste steg i {seen} av '
        f'{total} genererte puslespill.'
    )


# Norwegian names for every technique the solver knows, for the technique
# lists in the characteristics table.
TECHNIQUE_NAMES: dict[str, str] = {
    'hidden_single_box': 'skjult enkelttall (boks)',
    'hidden_single_line': 'skjult enkelttall (linje)',
    'naked_single': 'nakent enkelttall',
    'pointing_pair': 'pekende par',
    'claiming': 'blokkrav',
    'naked_pair': 'nakent par',
    'x_wing': 'X-Wing',
    'hidden_pair': 'skjult par',
    'naked_triple': 'nakent trippel',
    'swordfish': 'swordfish',
    'xy_wing': 'XY-Wing',
    'unique_rectangle': 'unikt rektangel',
}

TIER_NAMES = {'easy': 'LETT', 'medium': 'MIDDELS', 'hard': 'VANSKELIG',
              'expert': 'EKSPERT'}


def _no(value: float) -> str:
    """One decimal, Norwegian style: 3,4 rather than 3.4."""
    return f'{value:.1f}'.replace('.', ',')


def _ganger(count: int) -> str:
    return '1 gang' if count == 1 else f'{count} ganger'


# --- Characteristics -------------------------------------------------------

def characteristics(result: PuzzleResult, rung: Rung) -> dict[str, Any]:
    """Everything worth documenting about one puzzle on the sheet."""
    metrics = analyze_solve_path(result.solve_path)
    techniques = sorted({s.technique for s in result.solve_path})
    return {
        'puzzle': puzzle_to_string(result.grid),
        'solution': puzzle_to_string(result.solution),
        'se_rating': result.se_rating,
        'tier': result.difficulty_tier,
        'tier_name': TIER_NAMES.get(result.difficulty_tier, result.difficulty_tier),
        'clue_count': result.clue_count,
        'key_technique': rung.technique,
        'key_technique_name': rung.name,
        'key_technique_what': rung.what,
        'techniques': techniques,
        'technique_names': [TECHNIQUE_NAMES.get(t, t) for t in techniques],
        'technique_variety': metrics['technique_variety'],
        'total_steps': metrics['total_steps'],
        'crux_count': metrics['crux_count'],
        'crux_position': round(metrics['crux_position'], 3),
        'avg_opportunity': round(metrics['avg_opportunity'], 2),
        'spike_ratio': round(metrics['spike_ratio'], 2),
        'has_soul': result.has_soul,
    }


def _selection_key(result: PuzzleResult) -> tuple[float, float, int]:
    """Rank candidates for a rung: hardest first.

    Fewer givens is the strongest lever, then a solve path with fewer
    simultaneous openings (less to stumble over), then a longer path.
    """
    metrics = analyze_solve_path(result.solve_path)
    return (result.clue_count, metrics['avg_opportunity'], -metrics['total_steps'])


# --- Generation ------------------------------------------------------------

def _task(args: tuple[int, str]) -> PuzzleResult | None:
    """Worker: one seeded generation attempt."""
    seed, tier = args
    random.seed(seed)
    return generate_one(tier, max_attempts=40)


@dataclass
class Collection:
    """Candidates found so far, bucketed by their hardest technique."""
    buckets: dict[str, list[PuzzleResult]] = field(default_factory=dict)
    census: Counter = field(default_factory=Counter)
    generated: int = 0

    def add(self, result: PuzzleResult) -> None:
        crux = max(result.solve_path, key=lambda s: s.difficulty).technique
        self.generated += 1
        self.census[crux] += 1
        self.buckets.setdefault(crux, []).append(result)

    def missing(self) -> list[Rung]:
        return [r for r in LADDER if not self.buckets.get(r.technique)]


def build_testsheet(
    base_seed: int = 20260814,
    workers: int = 4,
    batch: int = 200,
    max_batches: int = 40,
    progress: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Generate the nine-puzzle set, one puzzle per rung of LADDER.

    Runs seeded batches until every rung is filled or `max_batches` is spent,
    then keeps the hardest candidate found for each rung. Returns
    (entries, meta) where entries are `characteristics()` dicts in ladder
    order, and meta records how the set was found.

    Raises RuntimeError if a rung could not be filled within the budget.
    """
    collection = Collection()
    seed = base_seed

    for _ in range(max_batches):
        # Alternate the requested tier so both clue ranges (hard 24–30,
        # expert 22–28) are sampled.
        tasks = [(seed + i, 'expert' if i % 2 else 'hard') for i in range(batch)]
        seed += batch

        if workers <= 1:
            results = [_task(t) for t in tasks]
        else:
            with Pool(processes=workers) as pool:
                results = pool.map(_task, tasks)

        for result in results:
            if result is not None:
                collection.add(result)

        missing = collection.missing()
        if progress:
            print(f'  {collection.generated} puslespill, mangler: '
                  f'{[r.technique for r in missing] or "ingenting"}', flush=True)
        if not missing:
            break

    missing = collection.missing()
    if missing:
        raise RuntimeError(
            'Fant ikke kandidat for: ' + ', '.join(r.technique for r in missing))

    entries = []
    for number, rung in enumerate(LADDER, start=1):
        best = min(collection.buckets[rung.technique], key=_selection_key)
        entry = characteristics(best, rung)
        entry['number'] = number
        entry['candidates_seen'] = collection.census[rung.technique]
        entries.append(entry)

    meta = {
        'base_seed': base_seed,
        'puzzles_generated': collection.generated,
        'crux_census': dict(sorted(collection.census.items(),
                                   key=lambda kv: -kv[1])),
    }
    meta['note_swordfish'] = swordfish_note(meta)
    return entries, meta


# --- PDF rendering ---------------------------------------------------------

PAGE_W, PAGE_H = 210 * mm, 297 * mm
MARGIN = 12.0          # mm
GRID_MM = 56.0         # puzzle grid edge on the sheet
COL_GAP = 9.0          # mm between columns
GRAY = (0.42, 0.42, 0.42)

# Reference cell size of the newspaper column, used to scale font and strokes
# so the sheet's digits sit in the cell the way the printed paper's do.
REF_CELL_MM = 8.8


def _y(top_mm: float) -> float:
    """Canvas y for a distance measured down from the top of the page."""
    return PAGE_H - top_mm * mm


def _bold_font(cell_mm: float) -> _DigitFont:
    return _DigitFont('tg_bold_digits.ttf', PUZZLE_FONT_PT * cell_mm / REF_CELL_MM)


def _regular_font(cell_mm: float) -> _DigitFont:
    return _DigitFont('tg_regular_digits.ttf',
                      PUZZLE_FONT_PT * cell_mm / REF_CELL_MM)


def _draw_grid(c: Canvas, values: list[int], left: float, top: float,
               size: float, font: _DigitFont) -> None:
    """Draw an 81-cell grid with its top-left corner at (left, top) in mm."""
    cell = size / 9
    scale = size / (9 * REF_CELL_MM)
    outer, box, thin = (w * scale for w in PUZZLE_STROKES)

    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineCap(2)  # projecting square cap, so corners close
    for i in range(10):
        c.setLineWidth(outer if i in (0, 9) else box if i in (3, 6) else thin)
        x = (left + i * cell) * mm
        y = _y(top + i * cell)
        c.line(x, _y(top), x, _y(top + size))
        c.line(left * mm, y, (left + size) * mm, y)

    for row in range(9):
        for col in range(9):
            value = values[cell_from_rc(row, col)]
            if value:
                font.draw(c, value,
                          (left + (col + 0.5) * cell) * mm,
                          _y(top + (row + 0.5) * cell))


def _draw_rating_row(c: Canvas, left: float, top: float, width: float) -> None:
    """Draw the 'Vurdering: [1][2][3][4][5]' row under a puzzle."""
    box_w, box_h, gap = 7.0, 7.0, 1.6
    label = 'Vurdering:'
    c.setFillColorRGB(0, 0, 0)
    c.setFont('Helvetica', 7)
    c.drawString(left * mm, _y(top + 4.8), label)

    boxes_w = 5 * box_w + 4 * gap
    x = left + width - boxes_w
    for digit in range(1, 6):
        c.setLineWidth(0.4)
        c.setStrokeColorRGB(*GRAY)
        c.rect(x * mm, _y(top + box_h), box_w * mm, box_h * mm, stroke=1, fill=0)
        c.setFillColorRGB(*GRAY)
        c.setFont('Helvetica', 7.5)
        text = str(digit)
        c.drawString(x * mm + (box_w * mm - c.stringWidth(text, 'Helvetica', 7.5)) / 2,
                     _y(top + box_h / 2 + 1.0), text)
        x += box_w + gap


def _draw_puzzle_cell(c: Canvas, entry: dict[str, Any], left: float, top: float,
                      width: float, font: _DigitFont) -> None:
    """One puzzle on the sheet: heading, grid, rating row."""
    c.setFillColorRGB(0, 0, 0)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(left * mm, _y(top + 3), f"NR. {entry['number']}")

    facts = f"SE {_no(entry['se_rating'])} · {entry['clue_count']} tall"
    c.setFont('Helvetica', 7)
    c.drawString((left + width) * mm - c.stringWidth(facts, 'Helvetica', 7),
                 _y(top + 3), facts)

    c.setFillColorRGB(*GRAY)
    c.setFont('Helvetica', 6.5)
    c.drawString(left * mm, _y(top + 7.4), entry['key_technique_name'])

    _draw_grid(c, [int(ch) if ch != '.' else 0 for ch in entry['puzzle']],
               left + (width - GRID_MM) / 2, top + 9.5, GRID_MM, font)
    _draw_rating_row(c, left, top + 9.5 + GRID_MM + 3.5, width)


def _page_sheet(c: Canvas, entries: list[dict[str, Any]], title: str,
                scale_note: str) -> None:
    """Page 1 — the sheet you print and hand out."""
    col_w = (PAGE_W / mm - 2 * MARGIN - 2 * COL_GAP) / 3
    row_h = 9.5 + GRID_MM + 3.5 + 7.0 + 7.0  # heading + grid + rating + gap

    c.setFillColorRGB(0, 0, 0)
    c.setFont('Helvetica-Bold', 15)
    c.drawString(MARGIN * mm, _y(MARGIN + 5), title)

    c.setFont('Helvetica', 8)
    c.setFillColorRGB(*GRAY)
    c.drawString(MARGIN * mm, _y(MARGIN + 10.5),
                 'Ni oppgaver med stigende vanskegrad — hver av dem krever '
                 'sin egen vanskeligste teknikk.')
    c.drawString(MARGIN * mm, _y(MARGIN + 14.5), scale_note)

    top0 = MARGIN + 21
    font = _bold_font(GRID_MM / 9)
    for index, entry in enumerate(entries):
        left = MARGIN + (index % 3) * (col_w + COL_GAP)
        top = top0 + (index // 3) * row_h
        _draw_puzzle_cell(c, entry, left, top, col_w, font)

    c.setFillColorRGB(*GRAY)
    c.setFont('Helvetica', 6.5)
    c.drawString(MARGIN * mm, _y(PAGE_H / mm - MARGIN),
                 'SE = teknisk vanskegrad (2,3 = enkelttall, 4,5 = unikt '
                 'rektangel). «tall» = antall oppgitte tall i rutenettet.')


def _wrap(c: Canvas, text: str, font: str, size: float,
          width_mm: float) -> list[str]:
    """Break `text` into lines no wider than `width_mm`."""
    lines: list[str] = []
    words = text.split()
    line = ''
    for word in words:
        trial = f'{line} {word}'.strip()
        if line and c.stringWidth(trial, font, size) > width_mm * mm:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def _paragraph(c: Canvas, text: str, left: float, top: float, width: float,
               font: str, size: float, leading: float) -> float:
    """Draw wrapped text, returning the top of the line after it."""
    for line in _wrap(c, text, font, size, width):
        c.setFont(font, size)
        c.drawString(left * mm, _y(top), line)
        top += leading
    return top


def _table_row(c: Canvas, cells: list[str], xs: list[float], top: float,
               font: str, size: float) -> None:
    c.setFont(font, size)
    for text, x in zip(cells, xs):
        c.drawString(x * mm, _y(top), text)


def _page_characteristics(c: Canvas, entries: list[dict[str, Any]],
                          meta: dict[str, Any]) -> None:
    """Page 2 — what each puzzle is made of."""
    width = PAGE_W / mm - 2 * MARGIN
    c.setFillColorRGB(0, 0, 0)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(MARGIN * mm, _y(MARGIN + 4), 'Kjennetegn')

    headers = ['Nr', 'SE', 'Nivå', 'Tall', 'Nøkkelteknikk',
               'Steg', 'Krux', 'Plass', 'Valg', 'Teknikker']
    xs = [MARGIN, MARGIN + 9, MARGIN + 20, MARGIN + 40, MARGIN + 52,
          MARGIN + 102, MARGIN + 115, MARGIN + 128, MARGIN + 145,
          MARGIN + 160]

    top = MARGIN + 14
    c.setFillColorRGB(*GRAY)
    _table_row(c, headers, xs, top, 'Helvetica-Bold', 6.5)
    c.setStrokeColorRGB(*GRAY)
    c.setLineWidth(0.4)
    c.line(MARGIN * mm, _y(top + 1.8), (PAGE_W / mm - MARGIN) * mm, _y(top + 1.8))

    top += 6
    for entry in entries:
        c.setFillColorRGB(0, 0, 0)
        _table_row(c, [
            str(entry['number']),
            _no(entry['se_rating']),
            entry['tier_name'],
            str(entry['clue_count']),
            entry['key_technique_name'],
            str(entry['total_steps']),
            str(entry['crux_count']),
            f"{entry['crux_position'] * 100:.0f} %",
            _no(entry['avg_opportunity']),
            str(entry['technique_variety']),
        ], xs, top, 'Helvetica', 6.5)
        top += 5.4

    top += 4
    c.setFillColorRGB(*GRAY)
    for line in [
        'Nøkkelteknikk = det vanskeligste steget oppgaven krever; det er dette '
        'steget SE-tallet måler. Krux = hvor mange ganger den teknikken må '
        'brukes, Plass = hvor langt ut i løsningen den dukker opp første gang.',
        'Valg = hvor mange steg som i snitt er mulige samtidig — lavt tall '
        'betyr smal sti og mer leting. Teknikker = hvor mange ulike teknikker '
        'løsningen bruker i alt.',
        'Rekkefølgen på arket følger teknikken, ikke følelsen: en oppgave '
        'lenger ned kan ha flere oppgitte tall og dermed kjennes lettere enn '
        'den over. Det er nettopp det ratingen skal fange opp.',
    ]:
        top = _paragraph(c, line, MARGIN, top, width, 'Helvetica', 6.5, 3.8)
        top += 1

    top += 5
    c.setFillColorRGB(0, 0, 0)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(MARGIN * mm, _y(top), 'Hva hver oppgave krever')
    top += 6
    for entry in entries:
        c.setFillColorRGB(0, 0, 0)
        c.setFont('Helvetica-Bold', 7)
        c.drawString(MARGIN * mm, _y(top),
                     f"{entry['number']}. {entry['key_technique_name']}")
        c.setFillColorRGB(*GRAY)
        c.setFont('Helvetica', 7)
        c.drawString((MARGIN + 38) * mm, _y(top), entry['key_technique_what'])
        c.setFont('Helvetica', 6.5)
        top = _paragraph(c, 'Teknikker: ' + ', '.join(entry['technique_names']),
                         MARGIN + 38, top + 3.6, width - 38, 'Helvetica', 6.5, 3.6)
        top += 2.6

    top += 3
    c.setFillColorRGB(*GRAY)
    top = _paragraph(c, meta['note_swordfish'], MARGIN, top, width,
                     'Helvetica', 6.5, 3.8)
    _paragraph(c, f"Settet er plukket ut fra {meta['puzzles_generated']} "
                  f'genererte puslespill (seed {meta["base_seed"]}); for hvert '
                  'trinn er kandidaten med færrest oppgitte tall valgt.',
               MARGIN, top + 2, width, 'Helvetica', 6.5, 3.8)


def _page_key(c: Canvas, entries: list[dict[str, Any]]) -> None:
    """Page 3 — the answer key."""
    c.setFillColorRGB(0, 0, 0)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(MARGIN * mm, _y(MARGIN + 4), 'Fasit')

    size = 52.0
    col_w = (PAGE_W / mm - 2 * MARGIN - 2 * COL_GAP) / 3
    font = _regular_font(size / 9)
    top0 = MARGIN + 14
    for index, entry in enumerate(entries):
        left = MARGIN + (index % 3) * (col_w + COL_GAP)
        top = top0 + (index // 3) * (size + 12)
        c.setFillColorRGB(0, 0, 0)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(left * mm, _y(top), f"NR. {entry['number']}")
        c.setFillColorRGB(*GRAY)
        c.setFont('Helvetica', 6.5)
        facts = f"SE {_no(entry['se_rating'])} · {entry['key_technique_name']}"
        c.drawString((left + col_w) * mm - c.stringWidth(facts, 'Helvetica', 6.5),
                     _y(top), facts)
        _draw_grid(c, [int(ch) for ch in entry['solution']],
                   left + (col_w - size) / 2, top + 2.5, size, font)


def render_testsheet_pdf(path: str, entries: list[dict[str, Any]],
                         meta: dict[str, Any], *,
                         title: str = 'SUDOKU — TESTARK',
                         scale_note: str = 'Sett kryss i ruten som passer: '
                                           '1 = for lett, 5 = for vanskelig.') -> str:
    """Render the three-page test sheet. Returns `path`."""
    if len(entries) != 9:
        raise ValueError(f'test sheet takes 9 puzzles, got {len(entries)}')

    c = Canvas(path, pagesize=(PAGE_W, PAGE_H))
    _page_sheet(c, entries, title, scale_note)
    c.showPage()
    _page_characteristics(c, entries, meta)
    c.showPage()
    _page_key(c, entries)
    c.save()
    return path


# --- Documentation ---------------------------------------------------------

def testsheet_markdown(entries: list[dict[str, Any]],
                       meta: dict[str, Any]) -> str:
    """The same characteristics as a README, for reading on GitHub."""
    lines = [
        '# Sudoku-testark',
        '',
        'Ni oppgaver med stigende vanskegrad, én per teknikk-trinn. Skriv ut',
        '`sudoku-testark.pdf` (side 1) og sett kryss i 1–5 under hver oppgave.',
        'Side 2 er kjennetegnene, side 3 er fasit.',
        '',
        '| Nr | SE | Nivå | Tall | Nøkkelteknikk | Steg | Krux | Plass | Valg |',
        '| --: | --: | :-- | --: | :-- | --: | --: | --: | --: |',
    ]
    for e in entries:
        lines.append(
            f"| {e['number']} | {_no(e['se_rating'])} | {e['tier_name']} | "
            f"{e['clue_count']} | {e['key_technique_name']} | {e['total_steps']} | "
            f"{e['crux_count']} | {e['crux_position'] * 100:.0f} % | "
            f"{_no(e['avg_opportunity'])} |")

    lines += [
        '',
        '- **SE** — vanskegraden til det vanskeligste steget oppgaven krever.',
        '- **Nøkkelteknikk** — hvilket steg det er. Hver oppgave på arket har sitt eget.',
        '- **Krux** — hvor mange ganger den teknikken må brukes.',
        '- **Plass** — hvor langt ut i løsningen kruxet dukker opp første gang.',
        '- **Valg** — hvor mange steg som i snitt er mulige samtidig; lavt tall = smalere sti.',
        '',
        'Rekkefølgen følger teknikken, ikke følelsen: en oppgave lenger ned på',
        'arket kan ha flere oppgitte tall og dermed kjennes lettere enn den over.',
        'Det er nettopp det ratingen skal fange opp.',
        '',
        '## Oppgavene',
        '',
    ]
    for e in entries:
        what = e['key_technique_what']
        seen = e['candidates_seen']
        lines += [
            f"### {e['number']}. {e['key_technique_name']} (SE {_no(e['se_rating'])})",
            '',
            f"{what[0].upper()}{what[1:]}.",
            '',
            f"- Nivå: {e['tier_name']} · {e['clue_count']} oppgitte tall",
            f"- Teknikker i løsningen: {', '.join(e['technique_names'])}",
            f"- Løsningssti: {e['total_steps']} steg, kruxet "
            f"{_ganger(e['crux_count'])} fra {e['crux_position'] * 100:.0f} % "
            'ut i stien',
            f"- Valgt blant {seen} kandidat{'' if seen == 1 else 'er'} med "
            'denne nøkkelteknikken',
            f"- Oppgave: `{e['puzzle']}`",
            f"- Fasit: `{e['solution']}`",
            '',
        ]

    census = ', '.join(f'{TECHNIQUE_NAMES.get(k, k)} {v}'
                       for k, v in meta['crux_census'].items())
    lines += [
        '## Slik ble settet plukket',
        '',
        f"Generatoren laget {meta['puzzles_generated']} puslespill "
        f"(seed {meta['base_seed']}). Fordelt på vanskeligste teknikk: {census}.",
        'For hvert trinn er kandidaten med færrest oppgitte tall valgt.',
        '',
        meta['note_swordfish'],
        '',
        'Regenerer med `sudokugen testsheet -o testsheet`.',
        '',
    ]
    return '\n'.join(lines)


def write_testsheet(out_dir: str, entries: list[dict[str, Any]],
                    meta: dict[str, Any]) -> dict[str, str]:
    """Write the PDF, the JSON data and the README into `out_dir`."""
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'sudoku-testark.pdf')
    json_path = os.path.join(out_dir, 'testsheet.json')
    md_path = os.path.join(out_dir, 'README.md')

    render_testsheet_pdf(pdf_path, entries, meta)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'puzzles': entries}, f,
                  indent=2, ensure_ascii=False)
        f.write('\n')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(testsheet_markdown(entries, meta))

    return {'pdf': pdf_path, 'json': json_path, 'readme': md_path}
