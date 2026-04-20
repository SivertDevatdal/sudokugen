"""Wing techniques: XY-Wing."""

from __future__ import annotations

from ..types import candidate_count, candidates_iter, has_candidate, digit_bit
from ..grid import SolverGrid, PEERS, PEER_SETS, NUM_CELLS
from . import TechniqueApplication


def xy_wing(grid: SolverGrid) -> TechniqueApplication | None:
    """Find an XY-Wing pattern: a pivot cell {a,b} with two pincer cells
    {a,c} and {b,c} that are peers of the pivot. Eliminate c from cells
    that see both pincers.

    Difficulty: 4.2 (SE rating)
    """
    first_elims: list[tuple[int, int]] = []
    opportunities = 0

    # Collect all bivalue cells
    bivalue: list[int] = []
    for cell in range(NUM_CELLS):
        if grid.values[cell] == 0 and candidate_count(grid.candidates[cell]) == 2:
            bivalue.append(cell)

    bivalue_set = set(bivalue)

    for pivot in bivalue:
        a, b = candidates_iter(grid.candidates[pivot])
        pivot_peers = PEER_SETS[pivot]

        # Find pincers among bivalue peers of pivot
        pincers_a: list[int] = []  # peers with candidates {a, c} for some c != b
        pincers_b: list[int] = []  # peers with candidates {b, c} for some c != a

        for peer in PEERS[pivot]:
            if peer not in bivalue_set:
                continue
            pc = grid.candidates[peer]
            if has_candidate(pc, a) and not has_candidate(pc, b):
                pincers_a.append(peer)
            elif has_candidate(pc, b) and not has_candidate(pc, a):
                pincers_b.append(peer)

        for pa in pincers_a:
            # pa has candidates {a, c} — find c
            pa_digits = candidates_iter(grid.candidates[pa])
            c_from_a = pa_digits[0] if pa_digits[1] == a else pa_digits[1]

            for pb in pincers_b:
                # pb must have candidates {b, c_from_a}
                pb_digits = candidates_iter(grid.candidates[pb])
                c_from_b = pb_digits[0] if pb_digits[1] == b else pb_digits[1]

                if c_from_a != c_from_b:
                    continue

                c = c_from_a
                c_bit = digit_bit(c)

                # Eliminate c from cells that see both pa and pb
                common_peers = PEER_SETS[pa] & PEER_SETS[pb]
                elims = [
                    (cell, c) for cell in common_peers
                    if grid.values[cell] == 0 and grid.candidates[cell] & c_bit
                    and cell != pivot
                ]

                if elims:
                    opportunities += 1
                    if not first_elims:
                        first_elims = elims

    if opportunities == 0:
        return None

    return TechniqueApplication(
        technique='xy_wing',
        difficulty=4.2,
        eliminations=first_elims,
        opportunities=opportunities,
    )
