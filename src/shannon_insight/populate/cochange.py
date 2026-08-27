"""Populate COCHANGE layer (R=1) from git history using lift-based association rules.

Rules:
  - Skip commits touching >50 files (bulk commits).
  - Apply exponential decay: weight = exp(-lambda * days_ago),
    lambda = ln(2)/90 (90-day half-life).
  - Compute lift: P(A inter B) / (P(A) * P(B)).
  - Only add edges where lift > 1.0.
  - Symmetric: both (a,b) and (b,a) are stored.
"""

from __future__ import annotations

import math
from collections import Counter
from itertools import combinations
from typing import Any

from ..tensor.core import COCHANGE

# 90-day half-life for exponential decay
_DECAY_LAMBDA = math.log(2) / 90


def populate_cochange(
    tensor: Any,
    git_history: Any,
    now_timestamp: int,
    window_days: int = 30,
) -> None:
    """Fill T[:,:,t,COCHANGE] with lift scores.

    Args:
        tensor: A ``RelationTensor`` instance.
        git_history: Object with a ``.commits`` list.  Each commit has
            ``.files`` (iterable of paths) and ``.timestamp`` (unix seconds).
        now_timestamp: Reference unix timestamp (typically ``time.time()``).
        window_days: Size of the time window in days (used for future
            multi-window support; currently all edges go to the latest
            window).
    """
    # Accumulate weighted co-occurrence and marginal counts
    cochange_counts: Counter[tuple[str, str]] = Counter()
    file_counts: Counter[str] = Counter()
    total_weight = 0.0

    for commit in git_history.commits:
        # Skip bulk / mass-reformatting commits
        if len(commit.files) > 50:
            continue

        commit_files = list(commit.files)

        days_ago = max((now_timestamp - commit.timestamp) / 86400, 0)
        weight = math.exp(-_DECAY_LAMBDA * days_ago)

        # Marginals
        for f in commit_files:
            file_counts[f] += weight

        # Pairwise co-occurrence (sorted key for canonical pair ordering)
        if len(commit_files) >= 2:
            for a, b in combinations(sorted(commit_files), 2):
                cochange_counts[(a, b)] += weight

        total_weight += weight

    if total_weight == 0:
        return

    # Compute lift and populate the tensor
    t = tensor.n_windows - 1  # current window

    for (a, b), count in cochange_counts.items():
        p_ab = count / total_weight
        p_a = file_counts[a] / total_weight
        p_b = file_counts[b] / total_weight

        if p_a == 0 or p_b == 0:
            continue

        lift = p_ab / (p_a * p_b)

        if lift > 1.0:
            tensor.add_edge(a, b, t, COCHANGE, weight=lift)
            tensor.add_edge(b, a, t, COCHANGE, weight=lift)  # symmetric
