"""Dancing Links (Algorithm X) exact cover solver for sudoku uniqueness checking."""

from __future__ import annotations

from .types import GRID_SIZE, NUM_CELLS, DIGITS, cell_row, cell_col, cell_box


class _Node:
    """Doubly-linked node in the DLX matrix."""
    __slots__ = ('left', 'right', 'up', 'down', 'column', 'row_id')

    def __init__(self) -> None:
        self.left: _Node = self
        self.right: _Node = self
        self.up: _Node = self
        self.down: _Node = self
        self.column: _ColumnNode = None  # type: ignore[assignment]
        self.row_id: int = -1


class _ColumnNode(_Node):
    """Column header with size tracking."""
    __slots__ = ('size', 'col_id')

    def __init__(self, col_id: int) -> None:
        super().__init__()
        self.size: int = 0
        self.col_id: int = col_id
        self.column = self


class DLXMatrix:
    """Exact cover matrix using Dancing Links."""

    def __init__(self, num_cols: int) -> None:
        self.header = _ColumnNode(-1)
        self.columns: list[_ColumnNode] = []

        prev = self.header
        for i in range(num_cols):
            col = _ColumnNode(i)
            col.left = prev
            col.right = self.header
            prev.right = col
            self.header.left = col
            prev = col
            self.columns.append(col)

    def add_row(self, row_id: int, col_indices: list[int]) -> None:
        """Add a row covering the specified columns."""
        first: _Node | None = None
        for ci in col_indices:
            col = self.columns[ci]
            node = _Node()
            node.row_id = row_id
            node.column = col

            # Insert at bottom of column
            node.up = col.up
            node.down = col
            col.up.down = node
            col.up = node
            col.size += 1

            # Link horizontally
            if first is None:
                first = node
                node.left = node
                node.right = node
            else:
                node.left = first.left
                node.right = first
                first.left.right = node
                first.left = node

    def _cover(self, col: _ColumnNode) -> None:
        col.right.left = col.left
        col.left.right = col.right
        row = col.down
        while row is not col:
            j = row.right
            while j is not row:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1
                j = j.right
            row = row.down

    def _uncover(self, col: _ColumnNode) -> None:
        row = col.up
        while row is not col:
            j = row.left
            while j is not row:
                j.column.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            row = row.up
        col.right.left = col
        col.left.right = col

    def solve(self, max_solutions: int = 2) -> list[list[int]]:
        """Find up to max_solutions solutions. Returns list of row-id lists."""
        solutions: list[list[int]] = []
        partial: list[int] = []
        self._search(partial, solutions, max_solutions)
        return solutions

    def _search(self, partial: list[int], solutions: list[list[int]],
                max_solutions: int) -> None:
        if self.header.right is self.header:
            solutions.append(partial[:])
            return

        if len(solutions) >= max_solutions:
            return

        # Choose column with minimum size (S heuristic)
        min_size = float('inf')
        chosen: _ColumnNode = None  # type: ignore[assignment]
        col = self.header.right
        while col is not self.header:
            assert isinstance(col, _ColumnNode)
            if col.size < min_size:
                min_size = col.size
                chosen = col
                if min_size <= 1:
                    break
            col = col.right

        if chosen.size == 0:
            return

        self._cover(chosen)
        row = chosen.down
        while row is not chosen:
            partial.append(row.row_id)

            j = row.right
            while j is not row:
                self._cover(j.column)
                j = j.right

            self._search(partial, solutions, max_solutions)
            if len(solutions) >= max_solutions:
                # Unwind and return early
                j = row.left
                while j is not row:
                    self._uncover(j.column)
                    j = j.left
                partial.pop()
                self._uncover(chosen)
                return

            j = row.left
            while j is not row:
                self._uncover(j.column)
                j = j.left

            partial.pop()
            row = row.down

        self._uncover(chosen)


# ---------------------------------------------------------------------------
# Sudoku-specific interface
# ---------------------------------------------------------------------------

def _sudoku_to_dlx(givens: list[int]) -> DLXMatrix:
    """Convert a sudoku puzzle to an exact cover matrix.

    324 columns:
      0–80:   cell constraints (each cell filled exactly once)
      81–161: row-digit constraints (each digit in each row exactly once)
      162–242: col-digit constraints (each digit in each column exactly once)
      243–323: box-digit constraints (each digit in each box exactly once)

    Up to 729 rows (81 cells × 9 digits), reduced by givens.
    """
    matrix = DLXMatrix(324)

    for cell in range(NUM_CELLS):
        r, c, b = cell_row(cell), cell_col(cell), cell_box(cell)
        if givens[cell] != 0:
            d = givens[cell]
            row_id = cell * 9 + (d - 1)
            cols = [
                cell,
                81 + r * 9 + (d - 1),
                162 + c * 9 + (d - 1),
                243 + b * 9 + (d - 1),
            ]
            matrix.add_row(row_id, cols)
        else:
            for d in range(1, 10):
                row_id = cell * 9 + (d - 1)
                cols = [
                    cell,
                    81 + r * 9 + (d - 1),
                    162 + c * 9 + (d - 1),
                    243 + b * 9 + (d - 1),
                ]
                matrix.add_row(row_id, cols)

    return matrix


def count_solutions(givens: list[int], limit: int = 2) -> int:
    """Count solutions up to limit. Returns 0, 1, or limit."""
    matrix = _sudoku_to_dlx(givens)
    solutions = matrix.solve(max_solutions=limit)
    return len(solutions)


def has_unique_solution(givens: list[int]) -> bool:
    """Check if the puzzle has exactly one solution."""
    return count_solutions(givens, limit=2) == 1


def solve_dlx(givens: list[int]) -> list[int] | None:
    """Solve and return the solution as 81-element list, or None."""
    matrix = _sudoku_to_dlx(givens)
    solutions = matrix.solve(max_solutions=1)
    if not solutions:
        return None
    result = givens[:]
    for row_id in solutions[0]:
        cell = row_id // 9
        digit = (row_id % 9) + 1
        result[cell] = digit
    return result
