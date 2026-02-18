"""Build co-change matrix from git history."""

from __future__ import annotations

import math
import time
from collections import defaultdict
from itertools import combinations
from typing import TYPE_CHECKING

from .models import CoChangeMatrix, CoChangePair, GitHistory

if TYPE_CHECKING:
    from ..persistence.git_facts import GitFactDatabase

# Temporal decay: 90-day half-life
_DECAY_LAMBDA = math.log(2) / 90


def build_cochange_matrix(
    history: GitHistory,
    analyzed_files: set[str],
    min_cochanges: int = 3,
    max_files_per_commit: int = 30,
) -> CoChangeMatrix:
    """Build sparse co-change matrix from git history.

    Only includes:
    - Files that exist in analyzed_files (current codebase)
    - Pairs with cochange_count >= min_cochanges (filter noise)
    - Commits that touch <= max_files_per_commit files (filter bulk reformats)

    Applies temporal decay: each commit weighted by exp(-lambda * days_since)
    where lambda = ln(2)/90 (90-day half-life). Recent co-changes matter more.
    """
    file_change_counts: dict[str, float] = defaultdict(float)
    pair_counts: dict[tuple[str, str], float] = defaultdict(float)
    pair_raw_counts: dict[tuple[str, str], int] = defaultdict(int)

    now = int(time.time())

    for commit in history.commits:
        # Filter to analyzed files only
        relevant = [f for f in commit.files if f in analyzed_files]
        if not relevant or len(relevant) > max_files_per_commit:
            continue

        # Temporal decay weight
        days_since = max(0, (now - commit.timestamp) / 86400)
        weight = math.exp(-_DECAY_LAMBDA * days_since)

        for f in relevant:
            file_change_counts[f] += weight

        # Count co-changes for all pairs (weighted)
        for a, b in combinations(sorted(relevant), 2):
            pair_counts[(a, b)] += weight
            pair_raw_counts[(a, b)] += 1

    # Build CoChangePair objects for pairs above threshold
    pairs: dict[tuple[str, str], CoChangePair] = {}
    total_commits = history.total_commits

    # Pre-compute total weight once (sum of decay weights for all commits)
    total_weight = sum(
        math.exp(-_DECAY_LAMBDA * max(0, (now - c.timestamp) / 86400)) for c in history.commits
    )

    for (a, b), weighted_count in pair_counts.items():
        raw_count = pair_raw_counts[(a, b)]
        if raw_count < min_cochanges:
            continue

        total_a = file_change_counts[a]
        total_b = file_change_counts[b]

        # Confidence: P(B changed | A changed) — using weighted counts
        conf_a_b = weighted_count / total_a if total_a > 0 else 0.0
        conf_b_a = weighted_count / total_b if total_b > 0 else 0.0

        # Lift: observed / expected under independence (weighted)
        if total_weight > 0:
            expected = (total_a * total_b) / total_weight
            lift = weighted_count / expected if expected > 0 else 0.0
        else:
            lift = 0.0

        # Store weighted totals consistently — confidence was computed from these,
        # so consumers can recompute if needed. Round to int if very close to avoid
        # float precision artifacts (e.g., 12.000000001 → 12).
        stored_total_a = round(total_a) if abs(total_a - round(total_a)) < 1e-9 else total_a
        stored_total_b = round(total_b) if abs(total_b - round(total_b)) < 1e-9 else total_b

        pairs[(a, b)] = CoChangePair(
            file_a=a,
            file_b=b,
            cochange_count=raw_count,
            total_a=stored_total_a,
            total_b=stored_total_b,
            confidence_a_b=conf_a_b,
            confidence_b_a=conf_b_a,
            lift=lift,
            weight=weighted_count,
        )

    return CoChangeMatrix(
        pairs=pairs,
        total_commits=total_commits,
        file_change_counts={k: int(v) for k, v in file_change_counts.items()},
    )


def build_cochange_matrix_from_db(
    db: GitFactDatabase,
    analyzed_files: set[str],
    min_cochanges: int = 3,
    max_files_per_commit: int = 30,
    since_timestamp: int | None = None,
) -> CoChangeMatrix:
    """Build sparse co-change matrix from git database.

    Database-backed equivalent of build_cochange_matrix().
    Much faster for repeated analyses on same repo.

    Args:
        db: GitFactDatabase with extracted git data
        analyzed_files: Set of files to include (current codebase)
        min_cochanges: Minimum raw co-change count to include
        max_files_per_commit: Skip commits with more files (bulk reformats)
        since_timestamp: Only consider commits after this time

    Returns:
        CoChangeMatrix with sparse pair data
    """
    # Get commit timestamp range
    ts_range = db.get_timestamp_range()
    if ts_range is None:
        return CoChangeMatrix(pairs={}, total_commits=0, file_change_counts={})

    now = int(time.time())

    # Get all commits in range with their files
    with db._connect() as conn:
        # Query for commits with file count filtering
        if since_timestamp:
            cursor = conn.execute(
                """
                SELECT c.hash, c.timestamp, GROUP_CONCAT(fc.file_path) as files
                FROM git_commits c
                JOIN git_file_changes fc ON c.hash = fc.commit_hash
                WHERE c.timestamp >= ?
                GROUP BY c.hash
                HAVING COUNT(*) <= ?
                """,
                (since_timestamp, max_files_per_commit),
            )
        else:
            cursor = conn.execute(
                """
                SELECT c.hash, c.timestamp, GROUP_CONCAT(fc.file_path) as files
                FROM git_commits c
                JOIN git_file_changes fc ON c.hash = fc.commit_hash
                GROUP BY c.hash
                HAVING COUNT(*) <= ?
                """,
                (max_files_per_commit,),
            )

        file_change_counts: dict[str, float] = defaultdict(float)
        pair_counts: dict[tuple[str, str], float] = defaultdict(float)
        pair_raw_counts: dict[tuple[str, str], int] = defaultdict(int)
        total_commits = 0

        for row in cursor:
            total_commits += 1
            files_str = row["files"]
            if not files_str:
                continue

            all_files = files_str.split(",")
            # Filter to analyzed files only
            relevant = [f for f in all_files if f in analyzed_files]
            if not relevant:
                continue

            # Temporal decay weight
            days_since = max(0, (now - row["timestamp"]) / 86400)
            weight = math.exp(-_DECAY_LAMBDA * days_since)

            for f in relevant:
                file_change_counts[f] += weight

            # Count co-changes for all pairs (weighted)
            for a, b in combinations(sorted(relevant), 2):
                pair_counts[(a, b)] += weight
                pair_raw_counts[(a, b)] += 1

    # Calculate total weight for lift calculation
    if since_timestamp:
        with db._connect() as conn:
            cursor = conn.execute(
                "SELECT timestamp FROM git_commits WHERE timestamp >= ?",
                (since_timestamp,),
            )
            total_weight = sum(
                math.exp(-_DECAY_LAMBDA * max(0, (now - row["timestamp"]) / 86400))
                for row in cursor
            )
    else:
        with db._connect() as conn:
            cursor = conn.execute("SELECT timestamp FROM git_commits")
            total_weight = sum(
                math.exp(-_DECAY_LAMBDA * max(0, (now - row["timestamp"]) / 86400))
                for row in cursor
            )

    # Build CoChangePair objects for pairs above threshold
    pairs: dict[tuple[str, str], CoChangePair] = {}

    for (a, b), weighted_count in pair_counts.items():
        raw_count = pair_raw_counts[(a, b)]
        if raw_count < min_cochanges:
            continue

        total_a = file_change_counts[a]
        total_b = file_change_counts[b]

        # Confidence: P(B changed | A changed)
        conf_a_b = weighted_count / total_a if total_a > 0 else 0.0
        conf_b_a = weighted_count / total_b if total_b > 0 else 0.0

        # Lift: observed / expected under independence
        if total_weight > 0:
            expected = (total_a * total_b) / total_weight
            lift = weighted_count / expected if expected > 0 else 0.0
        else:
            lift = 0.0

        # Round totals if very close to int
        stored_total_a = round(total_a) if abs(total_a - round(total_a)) < 1e-9 else total_a
        stored_total_b = round(total_b) if abs(total_b - round(total_b)) < 1e-9 else total_b

        pairs[(a, b)] = CoChangePair(
            file_a=a,
            file_b=b,
            cochange_count=raw_count,
            total_a=stored_total_a,
            total_b=stored_total_b,
            confidence_a_b=conf_a_b,
            confidence_b_a=conf_b_a,
            lift=lift,
            weight=weighted_count,
        )

    return CoChangeMatrix(
        pairs=pairs,
        total_commits=total_commits,
        file_change_counts={k: int(v) for k, v in file_change_counts.items()},
    )
