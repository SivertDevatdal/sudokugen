"""Solve path quality analysis and "soul" filter."""

from __future__ import annotations

from .types import SolvePath


def compute_se_rating(path: SolvePath) -> float:
    """SE-style rating: maximum technique difficulty in the solve path."""
    if not path:
        return 0.0
    return max(step.difficulty for step in path)


def analyze_solve_path(path: SolvePath) -> dict:
    """Compute all quality metrics for a solve path."""
    if not path:
        return {
            'total_steps': 0,
            'se_rating': 0.0,
            'crux_count': 0,
            'spike_ratio': 0.0,
            'avg_opportunity': 0.0,
            'technique_variety': 0,
            'techniques_used': [],
            'crux_position': 0.0,
        }

    difficulties = [step.difficulty for step in path]
    max_diff = max(difficulties)
    mean_diff = sum(difficulties) / len(difficulties)

    crux_positions = [i / len(path) for i, d in enumerate(difficulties) if d == max_diff]

    return {
        'total_steps': len(path),
        'se_rating': max_diff,
        'crux_count': sum(1 for d in difficulties if d == max_diff),
        'spike_ratio': max_diff / mean_diff if mean_diff > 0 else float('inf'),
        'avg_opportunity': sum(s.opportunities for s in path) / len(path),
        'technique_variety': len({step.technique for step in path}),
        'techniques_used': sorted({step.technique for step in path}),
        'crux_position': min(crux_positions) if crux_positions else 0.0,
    }


def has_soul(path: SolvePath, se_rating: float | None = None) -> bool:
    """Check if a solve path has the qualities of a satisfying puzzle.

    For hard/expert puzzles (SE > 3.0), applies strict criteria:
    1. Crux count: 1–3 applications of the hardest technique
    2. Spike ratio: max_difficulty / mean_difficulty < 5.0
    3. Average opportunity: > 1.5 (solver has choices, not a forced march)
    4. Technique variety: >= 3 distinct technique types
    5. Crux positioning: first crux appears after 30% of the solve path

    For easy/medium puzzles (SE <= 3.0), relaxed criteria:
    - Average opportunity > 1.2
    - Technique variety >= 1 (singles-only is fine for easy)
    """
    if len(path) < 5:
        return True

    metrics = analyze_solve_path(path)
    se = se_rating if se_rating is not None else metrics['se_rating']

    avg_opportunity = metrics['avg_opportunity']
    technique_variety = metrics['technique_variety']

    if se <= 3.0:
        # Easy/medium: just check it's not a forced march
        return avg_opportunity > 1.2 and technique_variety >= 1

    # Hard/expert: full soul check
    crux_count = metrics['crux_count']
    spike_ratio = metrics['spike_ratio']
    crux_position = metrics['crux_position']

    return (
        1 <= crux_count <= 3
        and spike_ratio < 5.0
        and avg_opportunity > 1.5
        and technique_variety >= 3
        and crux_position > 0.3
    )
