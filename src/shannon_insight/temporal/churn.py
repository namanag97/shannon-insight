"""Build per-file churn time series from git history."""

from __future__ import annotations

from collections import Counter, defaultdict
from math import log2

from .models import ChurnSeries, GitHistory, Trajectory

# Keywords for fix_ratio and refactor_ratio computation
FIX_KEYWORDS = frozenset({"fix", "bug", "patch", "hotfix", "bugfix", "repair", "issue"})
REFACTOR_KEYWORDS = frozenset(
    {"refactor", "cleanup", "clean up", "reorganize", "restructure", "rename"}
)


def build_churn_series(
    history: GitHistory,
    analyzed_files: set[str],
    window_weeks: int = 4,
    slope_threshold: float = 0.1,
    cv_threshold: float = 0.5,
) -> dict[str, ChurnSeries]:
    """Build per-file churn time series with trajectory classification.

    Trajectory classification (per v2 spec temporal-operators.md):
    - DORMANT: total_changes <= 1 or cv = 0
    - STABILIZING: negative slope AND cv < 0.5 (decreasing, steady)
    - SPIKING: positive slope AND cv > 0.5 (increasing, erratic)
    - CHURNING: cv > 0.5 (erratic, no clear trend)
    - STABLE: cv <= 0.5 (steady, no strong trend)
    """
    if not history.commits:
        return {}

    # Determine time boundaries
    timestamps = [c.timestamp for c in history.commits]
    min_ts = min(timestamps)
    max_ts = max(timestamps)
    window_secs = window_weeks * 7 * 86400

    if window_secs == 0:
        return {}

    num_windows = max(1, (max_ts - min_ts) // window_secs + 1)

    # Count changes per file per window, track authors and commit types
    file_windows: dict[str, list[int]] = defaultdict(lambda: [0] * num_windows)
    file_authors: dict[str, Counter[str]] = defaultdict(Counter)
    file_fix_count: dict[str, int] = defaultdict(int)
    file_refactor_count: dict[str, int] = defaultdict(int)
    file_commit_count: dict[str, int] = defaultdict(int)

    for commit in history.commits:
        window_idx = min((commit.timestamp - min_ts) // window_secs, num_windows - 1)
        subject_lower = commit.subject.lower()
        is_fix = any(kw in subject_lower for kw in FIX_KEYWORDS)
        is_refactor = any(kw in subject_lower for kw in REFACTOR_KEYWORDS)

        for f in commit.files:
            if f in analyzed_files:
                file_windows[f][window_idx] += 1
                file_authors[f][commit.author] += 1
                file_commit_count[f] += 1
                if is_fix:
                    file_fix_count[f] += 1
                if is_refactor:
                    file_refactor_count[f] += 1

    # Build ChurnSeries for each file
    results: dict[str, ChurnSeries] = {}

    for file_path, counts in file_windows.items():
        total = sum(counts)
        slope = _linear_slope(counts)
        cv = _compute_cv(counts, total)
        trajectory = _classify_trajectory(
            counts, total, slope, cv,
            slope_threshold=slope_threshold,
            cv_threshold=cv_threshold,
        )
        change_entropy = compute_change_entropy(counts)

        # Compute author entropy and bus_factor
        author_counts = file_authors[file_path]
        author_entropy = _compute_author_entropy(author_counts)
        bus_factor = 2**author_entropy  # Number of equivalent authors

        # Compute fix and refactor ratios
        commit_count = file_commit_count[file_path]
        fix_ratio = file_fix_count[file_path] / commit_count if commit_count > 0 else 0.0
        refactor_ratio = file_refactor_count[file_path] / commit_count if commit_count > 0 else 0.0

        results[file_path] = ChurnSeries(
            file_path=file_path,
            window_counts=counts,
            total_changes=total,
            trajectory=trajectory,
            slope=slope,
            cv=cv,
            bus_factor=bus_factor,
            author_entropy=author_entropy,
            fix_ratio=fix_ratio,
            refactor_ratio=refactor_ratio,
            change_entropy=change_entropy,
        )

    return results


def _linear_slope(values: list[int]) -> float:
    """Simple linear regression slope."""
    n = len(values)
    if n < 2:
        return 0.0

    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n

    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return 0.0
    return numerator / denominator


def _compute_cv(counts: list[int], total: int) -> float:
    """Compute coefficient of variation for change counts.

    Returns 0.0 if:
    - No changes (total=0)
    - Only 1 time window (CV undefined for single data point)
    - Mean is 0
    """
    n = len(counts)
    if n < 2 or total == 0:
        return 0.0

    mean = total / n
    if mean == 0:
        return 0.0

    variance = sum((c - mean) ** 2 for c in counts) / n
    std = variance**0.5
    return float(std / mean)


def _classify_trajectory(
    counts: list[int], total: int, slope: float, cv: float | None = None
) -> str:
    """Classify churn trajectory per v2 spec (temporal-operators.md).

    Classification rules:
    - DORMANT: total_changes <= 1 OR cv = 0
    - STABILIZING: slope < -threshold AND cv < 0.5 (decreasing, steady)
    - SPIKING: slope > threshold AND cv > 0.5 (increasing, erratic)
    - CHURNING: cv > 0.5 (erratic, no clear trend)
    - STABLE: cv <= 0.5 (steady, no strong trend)

    The CV threshold of 0.5 distinguishes erratic (CHURNING/SPIKING) from
    steady (STABLE/STABILIZING). See temporal-operators.md for rationale.

    Args:
        counts: Changes per time window
        total: Total change count
        slope: Linear regression slope
        cv: Coefficient of variation (computed if None for backward compat)

    Returns:
        Trajectory enum value (str-compatible for JSON serialization)
    """
    # Threshold for "significant" slope
    SLOPE_THRESHOLD = 0.1
    # CV threshold per spec: 0.5 distinguishes erratic from steady
    CV_THRESHOLD = 0.5

    if total <= 1:
        return Trajectory.DORMANT

    # Compute CV if not provided (backward compat)
    if cv is None:
        cv = _compute_cv(counts, total)

    if cv == 0:
        return Trajectory.DORMANT

    # Classification per v2 spec
    if slope < -SLOPE_THRESHOLD and cv < CV_THRESHOLD:
        return Trajectory.STABILIZING
    elif slope > SLOPE_THRESHOLD and cv > CV_THRESHOLD:
        return Trajectory.SPIKING
    elif cv > CV_THRESHOLD:
        return Trajectory.CHURNING
    else:
        return Trajectory.STABLE


def _compute_author_entropy(author_counts: Counter[str]) -> float:
    """Compute Shannon entropy of author commit distribution.

    Higher entropy = more diverse authorship = better bus factor.
    Single author = 0 entropy = bus_factor of 1.

    Returns:
        Entropy in bits.
    """
    total = sum(author_counts.values())
    if total == 0:
        return 0.0
    probs = [count / total for count in author_counts.values() if count > 0]
    return -sum(p * log2(p) for p in probs)


def compute_change_entropy(commits_per_window: list[int]) -> float:
    """Compute Shannon entropy of change distribution across time windows.

    High entropy = changes scattered evenly across all windows = BAD
    (constant churn with no focused burst pattern).
    Low entropy = changes concentrated in few windows = more predictable.

    Returns:
        Entropy in bits. 0.0 if no changes.
    """
    total = sum(commits_per_window)
    if total == 0:
        return 0.0
    probs = [c / total for c in commits_per_window if c > 0]
    return -sum(p * log2(p) for p in probs)
