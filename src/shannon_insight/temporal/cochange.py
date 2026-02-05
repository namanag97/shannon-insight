"""Build co-change matrix from git history."""

from collections import defaultdict
from itertools import combinations
from typing import Dict, Set, Tuple

from .models import CoChangeMatrix, CoChangePair, GitHistory


def build_cochange_matrix(
    history: GitHistory,
    analyzed_files: Set[str],
    min_cochanges: int = 2,
    max_files_per_commit: int = 50,
) -> CoChangeMatrix:
    """Build sparse co-change matrix from git history.

    Only includes:
    - Files that exist in analyzed_files (current codebase)
    - Pairs with cochange_count >= min_cochanges (filter noise)
    - Commits that touch <= max_files_per_commit files (filter bulk reformats)
    """
    file_change_counts: Dict[str, int] = defaultdict(int)
    pair_counts: Dict[Tuple[str, str], int] = defaultdict(int)

    for commit in history.commits:
        # Filter to analyzed files only
        relevant = [f for f in commit.files if f in analyzed_files]
        if not relevant or len(relevant) > max_files_per_commit:
            continue

        for f in relevant:
            file_change_counts[f] += 1

        # Count co-changes for all pairs
        for a, b in combinations(sorted(relevant), 2):
            pair_counts[(a, b)] += 1

    # Build CoChangePair objects for pairs above threshold
    pairs: Dict[Tuple[str, str], CoChangePair] = {}
    total_commits = history.total_commits

    for (a, b), count in pair_counts.items():
        if count < min_cochanges:
            continue

        total_a = file_change_counts[a]
        total_b = file_change_counts[b]

        # Confidence: P(B changed | A changed)
        conf_a_b = count / total_a if total_a > 0 else 0.0
        conf_b_a = count / total_b if total_b > 0 else 0.0

        # Lift: observed / expected under independence
        expected = (total_a * total_b) / total_commits if total_commits > 0 else 0
        lift = count / expected if expected > 0 else 0.0

        pairs[(a, b)] = CoChangePair(
            file_a=a,
            file_b=b,
            cochange_count=count,
            total_a=total_a,
            total_b=total_b,
            confidence_a_b=conf_a_b,
            confidence_b_a=conf_b_a,
            lift=lift,
        )

    return CoChangeMatrix(
        pairs=pairs,
        total_commits=total_commits,
        file_change_counts=dict(file_change_counts),
    )
