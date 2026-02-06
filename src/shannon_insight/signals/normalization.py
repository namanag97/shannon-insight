"""Percentile normalization for signal fusion.

Three tiers based on codebase size:
- ABSOLUTE (<15 files): No percentiles, use absolute thresholds only
- BAYESIAN (15-50): Bayesian percentiles with flat priors (v2.0: same as standard)
- FULL (50+): Standard percentile normalization

Percentile formula (FM-4 prevention): pctl(x) = |{v: v <= x}| / |values|
Uses <= (not <) to avoid off-by-one errors.
"""

from __future__ import annotations

from bisect import bisect_right
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shannon_insight.signals.models import SignalField

# Signals to normalize (numeric, per-file)
NORMALIZABLE_SIGNALS = [
    "lines",
    "function_count",
    "class_count",
    "max_nesting",
    "impl_gini",
    "stub_ratio",
    "import_count",
    "concept_count",
    "concept_entropy",
    "naming_drift",
    "todo_density",
    "pagerank",
    "betweenness",
    "in_degree",
    "out_degree",
    "blast_radius_size",
    "depth",
    "phantom_import_count",
    "compression_ratio",
    "semantic_coherence",
    "cognitive_load",
    "total_changes",
    "churn_slope",
    "churn_cv",
    "bus_factor",
    "author_entropy",
    "fix_ratio",
    "refactor_ratio",
]

# Absolute floors for percentile effectiveness
# If raw value is below floor, percentile is forced to 0.0
# This prevents 450 files with pagerank=0.001 from showing as "90th percentile"
ABSOLUTE_FLOORS: dict[str, float] = {
    "pagerank": 0.005,
    "blast_radius_size": 5.0,
    "cognitive_load": 10.0,
    "lines": 100.0,
}


def normalize(field: SignalField) -> None:
    """Compute percentiles for all numeric signals.

    Modifies field.per_file[*].percentiles in place.
    ABSOLUTE tier: returns immediately, no percentiles computed.
    BAYESIAN/FULL tier: computes standard percentiles (Bayesian uses flat priors = same).
    """
    if field.tier == "ABSOLUTE":
        # < 15 files: no percentiles, use absolute thresholds only
        return

    # Collect all values per signal across all files
    signal_values = _collect_signal_values(field)

    # Compute percentiles for each file
    for fs in field.per_file.values():
        for signal_name in NORMALIZABLE_SIGNALS:
            values = signal_values.get(signal_name, [])
            if not values:
                continue

            raw = getattr(fs, signal_name, None)
            if raw is None or not isinstance(raw, (int, float)):
                continue

            # Compute percentile
            pctl = _standard_percentile(float(raw), values)

            # Apply effective percentile (floor check)
            pctl = effective_percentile(signal_name, float(raw), pctl)

            fs.percentiles[signal_name] = pctl


def _collect_signal_values(field: SignalField) -> dict[str, list[float]]:
    """Collect all numeric signal values across files."""
    signal_values: dict[str, list[float]] = {}

    for fs in field.per_file.values():
        for signal_name in NORMALIZABLE_SIGNALS:
            raw = getattr(fs, signal_name, None)
            if raw is not None and isinstance(raw, (int, float)):
                if signal_name not in signal_values:
                    signal_values[signal_name] = []
                signal_values[signal_name].append(float(raw))

    # Sort for efficient percentile computation
    for values in signal_values.values():
        values.sort()

    return signal_values


def _standard_percentile(value: float, sorted_values: list[float]) -> float:
    """Compute percentile using <= formula.

    pctl(x) = |{v : v <= x}| / |values|

    Uses bisect_right which gives count of values <= x.
    """
    if not sorted_values:
        return 0.0
    idx = bisect_right(sorted_values, value)
    return idx / len(sorted_values)


def effective_percentile(signal_name: str, raw_value: float, pctl: float) -> float:
    """Apply absolute floor to percentile.

    If raw value is below the minimum threshold, force percentile to 0.0.
    This prevents misleading high percentiles on low absolute values.

    Example: pagerank=0.002 might be 90th percentile in a clustered distribution,
    but it's still a trivially low value. Force to 0.0 percentile.
    """
    if signal_name in ABSOLUTE_FLOORS:
        floor = ABSOLUTE_FLOORS[signal_name]
        if raw_value < floor:
            return 0.0
    return pctl
