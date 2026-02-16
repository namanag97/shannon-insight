"""Shared helper functions for pattern predicates and evidence builders.

These utilities are used across all pattern definitions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from shannon_insight.infrastructure.signals import Signal

if TYPE_CHECKING:
    from shannon_insight.infrastructure.entities import EntityId
    from shannon_insight.infrastructure.store import FactStore


def compute_percentile(store: FactStore, entity: EntityId, signal: Signal) -> float:
    """Compute percentile rank for a signal value across all files.

    Uses canonical percentile formula: pctl(S,f) = |{v: S(v)≤S(f)}| / |all_files|
    Returns 0.0 if signal not available.
    """
    value = store.get_signal(entity, signal)
    if value is None:
        return 0.0

    files = store.files()
    values = [store.get_signal(f, signal, default=0) for f in files]
    count_below_or_equal = sum(1 for v in values if v <= value)
    return count_below_or_equal / max(len(values), 1)


def compute_median(store: FactStore, signal: Signal) -> float:
    """Compute median value for a signal across all files."""
    files = store.files()
    values = sorted([store.get_signal(f, signal, default=0) for f in files])
    if not values:
        return 0.0
    n = len(values)
    if n % 2 == 0:
        return (values[n // 2 - 1] + values[n // 2]) / 2
    return values[n // 2]


def compute_confidence_from_margins(triggered: list[tuple[str, float, float, str]]) -> float:
    """Compute confidence from margins above/below thresholds.

    Args:
        triggered: List of (signal_name, actual, threshold, polarity)
                   where polarity is "high_is_bad" or "high_is_good"

    Returns:
        Confidence in [0, 1]
    """
    if not triggered:
        return 0.0

    margins = []
    for _signal, actual, threshold, polarity in triggered:
        if polarity == "high_is_bad":
            margin = (actual - threshold) / (1.0 - threshold) if threshold < 1 else 0
        else:  # high_is_good
            margin = (threshold - actual) / threshold if threshold > 0 else 0
        margins.append(max(0.0, min(1.0, margin)))

    return sum(margins) / len(margins)
