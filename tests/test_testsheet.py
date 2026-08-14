"""Tests for the nine-puzzle difficulty test sheet."""

import sys

import pytest

sys.path.insert(0, 'src')

from sudokugen.output import string_to_puzzle
from sudokugen.solver import solve_with_techniques
from sudokugen.techniques import get_technique_order
from sudokugen.testsheet import (
    LADDER, TECHNIQUE_NAMES, _selection_key, characteristics,
    render_testsheet_pdf, swordfish_note, write_testsheet,
)
# aliased: pytest would collect a name starting with "test" as a test case
from sudokugen.testsheet import testsheet_markdown as build_markdown
from sudokugen.types import PuzzleResult

# A real VANSKELIG puzzle whose hardest required step is an XY-Wing (SE 4.2).
SAMPLE_PUZZLE = ('6.5.7.....14...2.5....591.6...79..2...9...4...4..38...'
                 '4.698....1.3...54.....4.6.2')
SAMPLE_SOLUTION = ('695172834714863295832459176568794321379216458241538967'
                   '426985713183627549957341682')


def make_result(puzzle: str = SAMPLE_PUZZLE,
                solution: str = SAMPLE_SOLUTION) -> PuzzleResult:
    """Solve a puzzle string into a PuzzleResult, the way the pipeline does."""
    grid = string_to_puzzle(puzzle)
    path = solve_with_techniques(grid)
    assert path is not None
    return PuzzleResult(
        grid=grid,
        solution=string_to_puzzle(solution),
        solve_path=path,
        se_rating=max(step.difficulty for step in path),
        difficulty_tier='hard',
        clue_count=sum(1 for v in grid if v != 0),
        has_soul=True,
    )


def sample_entries() -> list[dict]:
    """Nine entries sharing one puzzle — enough to exercise the renderer."""
    result = make_result()
    entries = []
    for number, rung in enumerate(LADDER, start=1):
        entry = characteristics(result, rung)
        entry['number'] = number
        entry['candidates_seen'] = 1
        entries.append(entry)
    return entries


SAMPLE_META = {
    'base_seed': 1,
    'puzzles_generated': 500,
    'crux_census': {'xy_wing': 120, 'naked_triple': 2},
    'note_swordfish': swordfish_note(
        {'puzzles_generated': 500, 'crux_census': {'xy_wing': 120}}),
}


def test_ladder_is_nine_ascending_distinct_rungs():
    """Nine rungs, strictly ascending, each with its own hardest technique."""
    assert len(LADDER) == 9
    assert all(a.se < b.se for a, b in zip(LADDER, LADDER[1:]))
    assert len({rung.technique for rung in LADDER}) == 9


def test_ladder_matches_the_solver():
    """Every rung names a real technique at the difficulty the solver gives it."""
    known = {name: difficulty for name, difficulty, _ in get_technique_order()}
    for rung in LADDER:
        assert known[rung.technique] == rung.se
        assert rung.technique in TECHNIQUE_NAMES


def test_characteristics_describe_the_solve_path():
    result = make_result()
    rung = next(r for r in LADDER if r.technique == 'xy_wing')
    entry = characteristics(result, rung)

    assert entry['puzzle'] == SAMPLE_PUZZLE
    assert entry['solution'] == SAMPLE_SOLUTION
    assert entry['se_rating'] == 4.2
    assert entry['clue_count'] == 30
    assert entry['key_technique'] == 'xy_wing'
    assert entry['tier_name'] == 'VANSKELIG'
    assert 'xy_wing' in entry['techniques']
    assert entry['technique_variety'] == len(entry['techniques'])
    assert entry['total_steps'] > 0
    assert 0.0 <= entry['crux_position'] <= 1.0


def test_selection_prefers_fewer_clues():
    """Between two candidates for a rung, the sparser grid wins."""
    fat = make_result()
    lean = make_result()
    lean.clue_count = 24
    assert _selection_key(lean) < _selection_key(fat)


def test_render_testsheet_pdf(tmp_path):
    out = tmp_path / 'ark.pdf'
    render_testsheet_pdf(str(out), sample_entries(), SAMPLE_META)
    data = out.read_bytes()
    assert data.startswith(b'%PDF')
    assert data.count(b'/Type /Page\n') == 3  # sheet, characteristics, key


def test_render_requires_nine_puzzles(tmp_path):
    with pytest.raises(ValueError):
        render_testsheet_pdf(str(tmp_path / 'x.pdf'), sample_entries()[:4],
                             SAMPLE_META)


def test_markdown_documents_every_puzzle():
    text = build_markdown(sample_entries(), SAMPLE_META)
    for rung in LADDER:
        assert rung.name in text
    assert SAMPLE_PUZZLE in text
    assert 'Swordfish' in text


def test_write_testsheet_writes_all_three_files(tmp_path):
    paths = write_testsheet(str(tmp_path), sample_entries(), SAMPLE_META)
    assert set(paths) == {'pdf', 'json', 'readme'}
    for path in paths.values():
        assert (tmp_path / path.rsplit('/', 1)[-1]).stat().st_size > 0


def test_swordfish_note_reports_the_census():
    note = swordfish_note({'puzzles_generated': 500,
                           'crux_census': {'swordfish': 0}})
    assert '0 av 500' in note
