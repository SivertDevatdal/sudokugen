"""Vector PDF rendering of sudoku grids for newspaper/InDesign import."""

from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from .types import cell_from_rc

# --- Defaults matching the newspaper template ---

RED = (0.75, 0.12, 0.12)  # dark red matching template
BLACK = (0, 0, 0)
SOLUTION_GRAY = (0.35, 0.35, 0.35)

THICK_LINE = 1.5  # pt — box borders + outer border
THIN_LINE = 0.5   # pt — cell borders


def _draw_grid(
    c: Canvas,
    grid: list[int],
    origin_x: float,
    origin_y: float,
    grid_size: float,
    *,
    line_color: tuple[float, float, float] = RED,
    font_name: str = 'Helvetica',
    font_size: float = 16,
    font_color: tuple[float, float, float] = BLACK,
    thick: float = THICK_LINE,
    thin: float = THIN_LINE,
) -> None:
    """Draw a sudoku grid at the given position on a canvas."""
    cell = grid_size / 9

    # Thin cell lines
    c.setStrokeColorRGB(*line_color)
    c.setLineWidth(thin)
    for i in range(10):
        if i % 3 == 0:
            continue
        x = origin_x + i * cell
        c.line(x, origin_y, x, origin_y + grid_size)
    for j in range(10):
        if j % 3 == 0:
            continue
        y = origin_y + j * cell
        c.line(origin_x, y, origin_x + grid_size, y)

    # Thick box borders
    c.setLineWidth(thick)
    for i in range(4):
        x = origin_x + i * 3 * cell
        c.line(x, origin_y, x, origin_y + grid_size)
    for j in range(4):
        y = origin_y + j * 3 * cell
        c.line(origin_x, y, origin_x + grid_size, y)

    # Digits
    c.setFillColorRGB(*font_color)
    c.setFont(font_name, font_size)
    for row in range(9):
        for col in range(9):
            val = grid[cell_from_rc(row, col)]
            if val == 0:
                continue
            digit = str(val)
            cx = origin_x + col * cell
            cy = origin_y + (8 - row) * cell
            tw = c.stringWidth(digit, font_name, font_size)
            x = cx + (cell - tw) / 2
            y = cy + (cell - font_size * 0.7) / 2
            c.drawString(x, y, digit)


def render_grid_pdf(
    path: str,
    grid: list[int],
    *,
    is_solution: bool = False,
    label: str = '',
    line_color: tuple[float, float, float] = BLACK,
    font_name: str = 'Helvetica',
) -> None:
    """Render a single sudoku grid to a 92x92mm vector PDF."""
    page = 92 * mm
    margin = 2 * mm
    gs = page - 2 * margin

    c = Canvas(path, pagesize=(page, page))

    oy = margin
    if label:
        oy += 3.5 * mm

    _draw_grid(
        c, grid, margin, oy, gs,
        line_color=line_color,
        font_name=font_name,
        font_size=10 if is_solution else 16,
        font_color=SOLUTION_GRAY if is_solution else BLACK,
    )

    if label:
        c.setFillColorRGB(*BLACK)
        c.setFont(font_name, 7)
        tw = c.stringWidth(label, font_name, 7)
        c.drawString(margin + (gs - tw) / 2, margin + 0.5 * mm, label)

    c.save()


def render_newspaper_pdf(
    path: str,
    middels_puzzle: list[int],
    vanskelig_puzzle: list[int],
    middels_solution: list[int],
    vanskelig_solution: list[int],
    *,
    line_color: tuple[float, float, float] = RED,
    font_name: str = 'Helvetica',
) -> None:
    """Render the full newspaper layout as a single PDF.

    Matches the template: "DAGENS SUDOKU" header, two puzzles stacked
    with vertical labels (MIDDELS / VANSKELIG), and LØSNINGER section
    with two small solution grids at the bottom.
    """
    # Page dimensions — sized to content
    grid_size = 55 * mm       # main puzzle grids
    sol_grid_size = 22 * mm   # small solution grids
    label_margin = 12 * mm    # space for vertical label on left
    h_margin = 6 * mm         # left/right page margin
    top_margin = 5 * mm
    header_height = 7 * mm
    gap = 6 * mm              # vertical gap between puzzles
    sol_gap = 4 * mm          # gap between solution grids
    sol_header = 5 * mm       # "LØSNINGER" header height
    bottom_margin = 4 * mm

    content_width = label_margin + grid_size
    page_width = 2 * h_margin + content_width

    page_height = (top_margin + header_height + gap
                   + grid_size + gap
                   + grid_size + gap
                   + sol_header + sol_grid_size + bottom_margin)

    c = Canvas(path, pagesize=(page_width, page_height))

    # X position where grids start (after label margin)
    grid_x = h_margin + label_margin

    # --- "DAGENS SUDOKU" header ---
    cursor_y = page_height - top_margin
    c.setFillColorRGB(*BLACK)
    header_font_size = 9
    c.setFont(font_name, header_font_size)
    header_text = "D A G E N S   S U D O K U"
    tw = c.stringWidth(header_text, font_name, header_font_size)
    c.drawString(grid_x + (grid_size - tw) / 2, cursor_y - header_font_size, header_text)

    cursor_y -= header_height + gap

    # --- MIDDELS puzzle ---
    middels_y = cursor_y - grid_size
    _draw_grid(
        c, middels_puzzle, grid_x, middels_y, grid_size,
        line_color=line_color, font_name=font_name, font_size=11,
    )
    # Vertical label "MIDDELS" on the left
    c.saveState()
    label_font_size = 7
    c.setFillColorRGB(*BLACK)
    c.setFont(font_name, label_font_size)
    label_text = "M I D D E L S"
    lt = c.stringWidth(label_text, font_name, label_font_size)
    lx = h_margin + 3 * mm
    ly = middels_y + (grid_size - lt) / 2
    c.translate(lx, ly)
    c.rotate(90)
    c.drawString(0, 0, label_text)
    c.restoreState()

    cursor_y = middels_y - gap

    # --- VANSKELIG puzzle ---
    vansk_y = cursor_y - grid_size
    _draw_grid(
        c, vanskelig_puzzle, grid_x, vansk_y, grid_size,
        line_color=line_color, font_name=font_name, font_size=11,
    )
    # Vertical label "VANSKELIG"
    c.saveState()
    c.setFillColorRGB(*BLACK)
    c.setFont(font_name, label_font_size)
    label_text = "V A N S K E L I G"
    lt = c.stringWidth(label_text, font_name, label_font_size)
    lx = h_margin + 3 * mm
    ly = vansk_y + (grid_size - lt) / 2
    c.translate(lx, ly)
    c.rotate(90)
    c.drawString(0, 0, label_text)
    c.restoreState()

    cursor_y = vansk_y - gap

    # --- "LØSNINGER" header ---
    c.setFillColorRGB(*BLACK)
    sol_header_size = 7
    c.setFont(font_name, sol_header_size)
    sol_text = "L Ø S N I N G E R"
    tw = c.stringWidth(sol_text, font_name, sol_header_size)
    c.drawString(grid_x + (grid_size - tw) / 2, cursor_y - sol_header_size, sol_text)

    cursor_y -= sol_header

    # --- Two small solution grids side by side ---
    sol_y = cursor_y - sol_grid_size
    # Center the two solution grids under the puzzle grid
    total_sol_width = 2 * sol_grid_size + sol_gap
    sol_start_x = grid_x + (grid_size - total_sol_width) / 2

    _draw_grid(
        c, middels_solution, sol_start_x, sol_y, sol_grid_size,
        line_color=line_color, font_name=font_name, font_size=4,
        thick=0.8, thin=0.25,
    )
    _draw_grid(
        c, vanskelig_solution, sol_start_x + sol_grid_size + sol_gap, sol_y, sol_grid_size,
        line_color=line_color, font_name=font_name, font_size=4,
        thick=0.8, thin=0.25,
    )

    c.save()
