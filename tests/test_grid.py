"""Tests for grid module — peer maps, CandidateGrid, SolverGrid."""

import sys
sys.path.insert(0, 'src')

from sudokugen.types import (
    GRID_SIZE, NUM_CELLS, DIGITS, ALL_CANDIDATES,
    candidate_count, has_candidate, single_candidate, candidates_from_set,
    candidates_to_set, candidates_iter, digit_bit,
    cell_row, cell_col, cell_box, cell_from_rc,
)
from sudokugen.grid import (
    PEERS, PEER_SETS, ROW_CELLS, COL_CELLS, BOX_CELLS, ALL_UNITS, CELL_UNITS,
    CandidateGrid, SolverGrid,
)


def test_peer_count():
    """Every cell has exactly 20 peers."""
    for cell in range(NUM_CELLS):
        assert len(PEERS[cell]) == 20, f"Cell {cell} has {len(PEERS[cell])} peers"
        assert len(PEER_SETS[cell]) == 20


def test_no_self_peer():
    """No cell is its own peer."""
    for cell in range(NUM_CELLS):
        assert cell not in PEER_SETS[cell]


def test_peer_symmetry():
    """If A is a peer of B, then B is a peer of A."""
    for cell in range(NUM_CELLS):
        for peer in PEERS[cell]:
            assert cell in PEER_SETS[peer]


def test_units_coverage():
    """27 units, each with 9 cells."""
    assert len(ALL_UNITS) == 27
    for unit in ALL_UNITS:
        assert len(unit) == 9


def test_cell_units():
    """Every cell belongs to exactly 3 units."""
    for cell in range(NUM_CELLS):
        assert len(CELL_UNITS[cell]) == 3


def test_bitfield_helpers():
    assert candidate_count(ALL_CANDIDATES) == 9
    assert candidate_count(0) == 0
    assert candidate_count(digit_bit(5)) == 1
    assert has_candidate(ALL_CANDIDATES, 1)
    assert has_candidate(ALL_CANDIDATES, 9)
    assert not has_candidate(0, 5)
    assert single_candidate(digit_bit(7)) == 7
    assert single_candidate(digit_bit(3) | digit_bit(5)) == 0
    assert candidates_to_set(ALL_CANDIDATES) == set(DIGITS)
    assert candidates_from_set({1, 5, 9}) == digit_bit(1) | digit_bit(5) | digit_bit(9)
    assert sorted(candidates_iter(digit_bit(2) | digit_bit(7))) == [2, 7]


def test_cell_helpers():
    assert cell_from_rc(0, 0) == 0
    assert cell_from_rc(8, 8) == 80
    assert cell_row(0) == 0
    assert cell_col(0) == 0
    assert cell_row(80) == 8
    assert cell_col(80) == 8
    assert cell_box(0) == 0
    assert cell_box(80) == 8
    assert cell_box(cell_from_rc(4, 4)) == 4  # center


def test_candidate_grid_propagation():
    """CandidateGrid should propagate constraints on initialization."""
    # A simple puzzle that CandidateGrid can solve via propagation
    givens = [0] * 81
    # Fill first row partially
    givens[0] = 1
    grid = CandidateGrid(givens)
    assert grid.values[0] == 1
    # 1 should be eliminated from all peers of cell 0
    for peer in PEERS[0]:
        assert not has_candidate(grid.candidates[peer], 1)


def test_solver_grid_no_propagation():
    """SolverGrid should NOT auto-propagate beyond initial setup."""
    givens = [0] * 81
    givens[0] = 1
    grid = SolverGrid(givens)
    assert grid.values[0] == 1
    # Peers should have 1 eliminated
    for peer in PEERS[0]:
        assert not has_candidate(grid.candidates[peer], 1)
    # But placing a value should only eliminate from peers, not cascade
    grid.place(1, 2)  # cell 1, digit 2
    assert grid.values[1] == 2


if __name__ == '__main__':
    test_peer_count()
    test_no_self_peer()
    test_peer_symmetry()
    test_units_coverage()
    test_cell_units()
    test_bitfield_helpers()
    test_cell_helpers()
    test_candidate_grid_propagation()
    test_solver_grid_no_propagation()
    print("All grid tests passed!")
