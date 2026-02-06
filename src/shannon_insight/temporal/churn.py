"""Build per-file churn time series from git history."""

from collections import defaultdict

from .models import ChurnSeries, GitHistory


def build_churn_series(
    history: GitHistory,
    analyzed_files: set[str],
    window_weeks: int = 4,
) -> dict[str, ChurnSeries]:
    """Build per-file churn time series with trajectory classification.

    Trajectory classification via linear regression slope + coefficient of variation:
    - dormant: total_changes <= 1
    - stabilizing: negative slope (decreasing over time)
    - spiking: positive slope AND high coefficient of variation
    - churning: high coefficient of variation, no clear trend
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

    # Count changes per file per window
    file_windows: dict[str, list[int]] = defaultdict(lambda: [0] * num_windows)

    for commit in history.commits:
        window_idx = min((commit.timestamp - min_ts) // window_secs, num_windows - 1)
        for f in commit.files:
            if f in analyzed_files:
                file_windows[f][window_idx] += 1

    # Build ChurnSeries for each file
    results: dict[str, ChurnSeries] = {}

    for file_path, counts in file_windows.items():
        total = sum(counts)
        slope = _linear_slope(counts)
        trajectory = _classify_trajectory(counts, total, slope)

        results[file_path] = ChurnSeries(
            file_path=file_path,
            window_counts=counts,
            total_changes=total,
            trajectory=trajectory,
            slope=slope,
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


def _classify_trajectory(counts: list[int], total: int, slope: float) -> str:
    """Classify churn trajectory."""
    if total <= 1:
        return "dormant"

    # Coefficient of variation
    n = len(counts)
    mean = total / n if n > 0 else 0
    if mean == 0:
        return "dormant"

    variance = sum((c - mean) ** 2 for c in counts) / n
    std = variance**0.5
    cv = std / mean

    if slope < -0.1:
        return "stabilizing"
    elif slope > 0.1 and cv > 1.0:
        return "spiking"
    elif cv > 0.8:
        return "churning"
    else:
        return "stabilizing"
