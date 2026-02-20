"""Populate COCHANGE layer (R=1)."""
from __future__ import annotations

import math
from collections import Counter
from itertools import combinations

from ..tensor.core import RelationTensor, COCHANGE
from ..extract.models import GitHistory


# 90-day half-life
DECAY_LAMBDA = math.log(2) / 90


def populate_cochange(
    tensor: RelationTensor,
    git_history: GitHistory,
    now_timestamp: int,
    window_days: int = 30,
):
    """Fill T[:,:,t,COCHANGE] with lift scores."""
    # Group commits by time window
    window_seconds = window_days * 86400

    # Count co-occurrences with decay
    cochange_counts: Counter[tuple[str, str]] = Counter()
    file_counts: Counter[str] = Counter()
    total_weight = 0.0

    for commit in git_history.commits:
        # Skip bulk commits
        if len(commit.files) > 50:
            continue

        days_ago = (now_timestamp - commit.timestamp) / 86400
        weight = math.exp(-DECAY_LAMBDA * days_ago)

        for f in commit.files:
            file_counts[f] += weight

        for a, b in combinations(sorted(commit.files), 2):
            cochange_counts[(a, b)] += weight

        total_weight += weight

    if total_weight == 0:
        return

    # Compute lift and populate tensor
    min_count = 3

    for (a, b), count in cochange_counts.items():
        if count < min_count:
            continue

        p_ab = count / total_weight
        p_a = file_counts[a] / total_weight
        p_b = file_counts[b] / total_weight

        if p_a == 0 or p_b == 0:
            continue

        lift = p_ab / (p_a * p_b)

        if lift > 1.0:
            # Determine time window
            t = tensor.n_windows - 1  # Current window

            tensor.add_edge(a, b, t, COCHANGE, weight=lift)
            tensor.add_edge(b, a, t, COCHANGE, weight=lift)  # Symmetric
