"""Candidate grid, peer maps, and constraint propagation."""

from __future__ import annotations

from .types import (
    GRID_SIZE, BOX_SIZE, NUM_CELLS, DIGITS, ALL_CANDIDATES,
    digit_bit, candidate_count, has_candidate, single_candidate, candidates_iter,
    cell_row, cell_col, cell_box, cell_from_rc,
)

# ---------------------------------------------------------------------------
# Precomputed tables (built once at import time)
# ---------------------------------------------------------------------------

ROW_CELLS: list[list[int]] = [
    [cell_from_rc(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)
]

COL_CELLS: list[list[int]] = [
    [cell_from_rc(r, c) for r in range(GRID_SIZE)] for c in range(GRID_SIZE)
]

BOX_CELLS: list[list[int]] = []
for br in range(BOX_SIZE):
    for bc in range(BOX_SIZE):
        cells = []
        for dr in range(BOX_SIZE):
            for dc in range(BOX_SIZE):
                cells.append(cell_from_rc(br * BOX_SIZE + dr, bc * BOX_SIZE + dc))
        BOX_CELLS.append(cells)

# All 27 units (9 rows + 9 cols + 9 boxes)
ALL_UNITS: list[list[int]] = ROW_CELLS + COL_CELLS + BOX_CELLS

# For each cell, which 3 units it belongs to (indices into ALL_UNITS)
CELL_UNITS: list[list[int]] = [[] for _ in range(NUM_CELLS)]
for ui, unit in enumerate(ALL_UNITS):
    for cell in unit:
        CELL_UNITS[cell].append(ui)

# For each cell, its 20 peers (cells sharing a row, column, or box)
PEERS: list[list[int]] = []
for cell in range(NUM_CELLS):
    peer_set: set[int] = set()
    for ui in CELL_UNITS[cell]:
        for c in ALL_UNITS[ui]:
            if c != cell:
                peer_set.add(c)
    PEERS.append(sorted(peer_set))

# Peer sets for fast lookup
PEER_SETS: list[set[int]] = [set(p) for p in PEERS]

# Box index for each cell
CELL_BOX: list[int] = [cell_box(c) for c in range(NUM_CELLS)]

# Row/col indices for each cell
CELL_ROW: list[int] = [cell_row(c) for c in range(NUM_CELLS)]
CELL_COL: list[int] = [cell_col(c) for c in range(NUM_CELLS)]


# ---------------------------------------------------------------------------
# CandidateGrid — the shared substrate for solving and generation
# ---------------------------------------------------------------------------

class CandidateGrid:
    """A sudoku grid with bitfield candidate tracking and constraint propagation."""

    __slots__ = ('values', 'candidates')

    def __init__(self, givens: list[int]) -> None:
        """Initialize from 81-element list (0 = empty)."""
        self.values: list[int] = [0] * NUM_CELLS
        self.candidates: list[int] = [ALL_CANDIDATES] * NUM_CELLS

        for cell in range(NUM_CELLS):
            if givens[cell] != 0:
                if not self.assign(cell, givens[cell]):
                    raise ValueError(f"Contradiction assigning {givens[cell]} to cell {cell}")

    def assign(self, cell: int, digit: int) -> bool:
        """Place digit in cell and propagate constraints. Returns False on contradiction."""
        # Remove all other candidates from this cell
        other = self.candidates[cell] & ~digit_bit(digit)
        for d in candidates_iter(other):
            if not self.eliminate(cell, d):
                return False
        return True

    def eliminate(self, cell: int, digit: int) -> bool:
        """Remove digit from cell's candidates. Returns False on contradiction."""
        bit = digit_bit(digit)
        if not (self.candidates[cell] & bit):
            return True  # already eliminated

        self.candidates[cell] &= ~bit
        c = self.candidates[cell]

        # If no candidates left, contradiction
        if c == 0:
            return False

        # If exactly one candidate, assign it and propagate to peers
        d = single_candidate(c)
        if d:
            self.values[cell] = d
            for peer in PEERS[cell]:
                if not self.eliminate(peer, d):
                    return False

        # For each unit containing this cell, check if digit now has
        # exactly one possible location → assign it there
        for ui in CELL_UNITS[cell]:
            places = 0
            place_cell = -1
            for uc in ALL_UNITS[ui]:
                if self.candidates[uc] & bit:
                    places += 1
                    place_cell = uc
                    if places > 1:
                        break
            if places == 0:
                return False  # digit has no home in this unit
            if places == 1:
                if not self.assign(place_cell, digit):
                    return False

        return True

    def copy(self) -> CandidateGrid:
        """Deep copy for backtracking."""
        new = object.__new__(CandidateGrid)
        new.values = self.values[:]
        new.candidates = self.candidates[:]
        return new

    def is_complete(self) -> bool:
        """All cells assigned."""
        return all(v != 0 for v in self.values)

    def unsolved_cells(self) -> list[int]:
        """Cells not yet assigned, sorted by fewest candidates (MRV)."""
        cells = [c for c in range(NUM_CELLS) if self.values[c] == 0]
        cells.sort(key=lambda c: candidate_count(self.candidates[c]))
        return cells


class SolverGrid:
    """A passive candidate grid for the technique solver.

    Unlike CandidateGrid, this does NOT auto-propagate constraints.
    The technique solver is responsible for discovering and applying
    each logical step explicitly. This ensures the solve path accurately
    records which techniques were needed.
    """

    __slots__ = ('values', 'candidates')

    def __init__(self, givens: list[int]) -> None:
        self.values: list[int] = [0] * NUM_CELLS
        self.candidates: list[int] = [ALL_CANDIDATES] * NUM_CELLS

        for cell in range(NUM_CELLS):
            if givens[cell] != 0:
                d = givens[cell]
                self.values[cell] = d
                self.candidates[cell] = digit_bit(d)
                # Remove digit from all peers' candidates
                for peer in PEERS[cell]:
                    self.candidates[peer] &= ~digit_bit(d)

    def place(self, cell: int, digit: int) -> None:
        """Place a digit in a cell and eliminate from peers. No cascading."""
        self.values[cell] = digit
        self.candidates[cell] = digit_bit(digit)
        bit = digit_bit(digit)
        for peer in PEERS[cell]:
            self.candidates[peer] &= ~bit

    def eliminate(self, cell: int, digit: int) -> None:
        """Remove a candidate from a cell. No cascading."""
        self.candidates[cell] &= ~digit_bit(digit)

    def is_complete(self) -> bool:
        return all(v != 0 for v in self.values)

    def copy(self) -> SolverGrid:
        new = object.__new__(SolverGrid)
        new.values = self.values[:]
        new.candidates = self.candidates[:]
        return new
