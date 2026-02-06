"""Percentile computation and severity ranking utilities."""

from bisect import bisect_left


def compute_percentiles(values: dict[str, float]) -> dict[str, float]:
    """Given {file: value}, return {file: percentile 0-100}.

    Uses bisect for efficient rank lookup. Ties get the same percentile
    (left-side rank).
    """
    if not values:
        return {}

    sorted_vals = sorted(values.values())
    n = len(sorted_vals)
    if n == 0:
        return {}

    rank_map: dict[str, float] = {}
    for path, val in values.items():
        rank = bisect_left(sorted_vals, val)
        rank_map[path] = (rank / n) * 100

    return rank_map
