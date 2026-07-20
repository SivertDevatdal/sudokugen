"""Newspaper sudoku column PDF rendering — the standard output format.

Renders one dated PDF per day (sudoku-YYYY-MM-DD.pdf) on an 80 x 234 mm
page: MIDDELS puzzle grid on top, VANSKELIG below, and two small
solution grids bottom-aligned. Following newspaper convention, the
solution grids show the PREVIOUS day's solutions.

All geometry (line positions, stroke widths, digit sizes) was measured
from the production reference sudoku20260725.pdf, and digits are drawn
as vector outlines using Trade Gothic digit glyphs (subset in
data/tg_*.ttf), so the output is pixel-faithful to the InDesign
original with no font installation required.
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta
from importlib.resources import files

from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

PAGE_W = 80 * mm
PAGE_H = 234 * mm

# Line-center positions in mm from the page's top-left corner, as
# measured from the reference PDF (the original InDesign table has
# slightly non-uniform cells — these are the real positions).
COLS = [0.35, 9.52, 18.17, 26.81, 35.63, 44.27, 52.92, 61.56, 70.38, 79.55]
ROWS_MIDDELS = COLS
ROWS_VANSKELIG = [86.43, 95.43, 104.25, 112.89, 121.53, 130.17,
                  138.99, 147.64, 156.28, 165.45]
SOL_ROWS = [196.14, 200.55, 204.61, 208.76, 212.90, 216.96,
            221.10, 225.25, 229.31, 233.72]
SOL1_COLS = [0.35, 4.59, 8.64, 12.88, 16.93, 20.99, 25.05, 29.28, 33.34, 37.57]
SOL2_COLS = [42.16, 46.57, 50.62, 54.77, 58.91, 62.97, 67.12, 71.26, 75.14, 79.55]

# Stroke widths in pt: (outer border, 3x3 box lines, cell lines)
PUZZLE_STROKES = (2.5, 1.5, 0.5)
SOLUTION_STROKES = (1.5, 1.0, 0.3)

# Reference digit heights: 3.88 mm (puzzles), 1.94 mm (solutions),
# calibrated against the '5' glyph's bbox.
PUZZLE_DIGIT_MM = 3.88
SOLUTION_DIGIT_MM = 1.94


class _GlyphPathPen(BasePen):
    """Draws a fontTools glyph into a reportlab path."""

    def __init__(self, glyph_set, path, scale, dx, dy):
        super().__init__(glyph_set)
        self.p, self.s, self.dx, self.dy = path, scale, dx, dy

    def _pt(self, p):
        return (p[0] * self.s + self.dx, p[1] * self.s + self.dy)

    def _moveTo(self, p):
        self.p.moveTo(*self._pt(p))

    def _lineTo(self, p):
        self.p.lineTo(*self._pt(p))

    def _qCurveToOne(self, p1, p2):
        x0, y0 = self._pt(self._getCurrentPoint())
        x1, y1 = self._pt(p1)
        x2, y2 = self._pt(p2)
        self.p.curveTo(x0 + 2 / 3 * (x1 - x0), y0 + 2 / 3 * (y1 - y0),
                       x2 + 2 / 3 * (x1 - x2), y2 + 2 / 3 * (y1 - y2), x2, y2)

    def _closePath(self):
        self.p.close()


class _DigitFont:
    """A digit-only font subset: glyph d is named glyph{d+1:05d}."""

    def __init__(self, resource_name: str, digit_mm: float):
        data = files('sudokugen').joinpath('data', resource_name)
        with data.open('rb') as f:
            self.font = TTFont(f)
        self.glyph_set = self.font.getGlyphSet()
        self.metrics = {}
        for d in range(10):
            g = f'glyph{d + 1:05d}'
            bp = BoundsPen(self.glyph_set)
            self.glyph_set[g].draw(bp)
            self.metrics[d] = (bp.bounds, self.font['hmtx'][g][0])
        # scale so the '5' glyph is digit_mm tall (matches reference)
        b5 = self.metrics[5][0]
        self.scale = (digit_mm * mm) / (b5[3] - b5[1])

    def draw(self, canvas: Canvas, digit: int, cx: float, cy: float) -> None:
        """Draw digit centered (advance-horizontal, bbox-vertical) at cx, cy."""
        (x0, y0, x1, y1), adv = self.metrics[digit]
        p = canvas.beginPath()
        pen = _GlyphPathPen(self.glyph_set, p, self.scale,
                            cx - adv * self.scale / 2,
                            cy - (y0 + y1) * self.scale / 2)
        self.glyph_set[f'glyph{digit + 1:05d}'].draw(pen)
        canvas.drawPath(p, stroke=0, fill=1)


_fonts: dict[str, _DigitFont] = {}


def _digit_font(kind: str) -> _DigitFont:
    if kind not in _fonts:
        if kind == 'bold':
            _fonts[kind] = _DigitFont('tg_bold_digits.ttf', PUZZLE_DIGIT_MM)
        else:
            _fonts[kind] = _DigitFont('tg_regular_digits.ttf', SOLUTION_DIGIT_MM)
    return _fonts[kind]


def _y(y_mm: float) -> float:
    return PAGE_H - y_mm * mm


def _draw_grid(c: Canvas, grid2d, xs, ys, font: _DigitFont, strokes) -> None:
    outer, box, thin = strokes
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineCap(2)  # projecting square cap: corners join without gaps
    for i in range(10):
        c.setLineWidth(outer if i in (0, 9) else box if i in (3, 6) else thin)
        c.line(xs[i] * mm, _y(ys[0]), xs[i] * mm, _y(ys[9]))
        c.line(xs[0] * mm, _y(ys[i]), xs[9] * mm, _y(ys[i]))
    for r in range(9):
        for col in range(9):
            v = grid2d[r][col]
            if v:
                font.draw(c, v,
                          (xs[col] + xs[col + 1]) / 2 * mm,
                          (_y(ys[r]) + _y(ys[r + 1])) / 2)


def render_column_pdf(out_path: str, puzzles: dict, prev_solutions: dict) -> None:
    """Render one day's column.

    puzzles: {'middels': 9x9 grid, 'vanskelig': 9x9 grid} (0 = empty)
    prev_solutions: {'middels': 9x9, 'vanskelig': 9x9} — the PREVIOUS
    day's solutions, printed at the bottom.
    """
    bold, reg = _digit_font('bold'), _digit_font('regular')
    c = Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    _draw_grid(c, puzzles['middels'], COLS, ROWS_MIDDELS, bold, PUZZLE_STROKES)
    _draw_grid(c, puzzles['vanskelig'], COLS, ROWS_VANSKELIG, bold, PUZZLE_STROKES)
    _draw_grid(c, prev_solutions['middels'], SOL1_COLS, SOL_ROWS, reg, SOLUTION_STROKES)
    _draw_grid(c, prev_solutions['vanskelig'], SOL2_COLS, SOL_ROWS, reg, SOLUTION_STROKES)
    c.save()


def render_day(day: date, puzzles_dir: str, out_dir: str) -> str:
    """Render sudoku-YYYY-MM-DD.pdf for `day` from the dated JSON files.

    Requires puzzles/<day>.json and puzzles/<day - 1>.json (for the
    printed solutions). Returns the output path.
    """
    with open(os.path.join(puzzles_dir, f'{day.isoformat()}.json'),
              encoding='utf-8') as f:
        today = json.load(f)
    prev_day = day - timedelta(days=1)
    prev_path = os.path.join(puzzles_dir, f'{prev_day.isoformat()}.json')
    if not os.path.exists(prev_path):
        raise FileNotFoundError(
            f'{prev_path} missing — need the previous day for its solutions')
    with open(prev_path, encoding='utf-8') as f:
        prev = json.load(f)

    out_path = os.path.join(out_dir, f'sudoku-{day.isoformat()}.pdf')
    render_column_pdf(
        out_path,
        {'middels': today['middels']['grid'],
         'vanskelig': today['vanskelig']['grid']},
        {'middels': prev['middels']['solution'],
         'vanskelig': prev['vanskelig']['solution']},
    )
    return out_path
