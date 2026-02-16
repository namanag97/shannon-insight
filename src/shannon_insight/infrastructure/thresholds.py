"""ThresholdStrategy — tier-aware threshold checking for finders.

Pattern 6 from infrastructure.md. Eliminates duplicated tier logic across finders.

Every finder that checks percentiles currently has its own tier branching:
    if tier == "ABSOLUTE": use absolute threshold
    else: use percentile

This pattern centralizes that logic into ThresholdCheck, injected into finders.

Three tiers:
    ABSOLUTE (<15 files): No percentiles, use absolute_threshold from SignalMeta registry.
    BAYESIAN (15-50 files): Percentiles available but noisier.
    FULL (50+ files): Full percentile normalization.

Usage in finders:
    check = ThresholdCheck(store.signal_field.value)
    for path, fs in field.per_file.items():
        if check.above(fs, Signal.PAGERANK, 0.80):
            ...  # Works for ALL tiers without branching
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from shannon_insight.signals.registry import REGISTRY, Signal

if TYPE_CHECKING:
    from shannon_insight.signals.models import FileSignals, SignalField


class ThresholdCheck:
    """Tier-aware signal threshold checking. Injected into every finder.

    For FULL/BAYESIAN tiers, uses percentile-based thresholds.
    For ABSOLUTE tier, uses absolute thresholds from the signal registry.

    This eliminates 6+ finders reimplementing the same tier branching logic.
    """

    def __init__(self, field: SignalField) -> None:
        self.tier = field.tier

    def above(self, fs: FileSignals, signal: Signal, pctl_threshold: float) -> bool:
        """Is this file's signal value above the threshold?

        For high-is-bad signals (e.g., pagerank, cognitive_load, fix_ratio):
            FULL/BAYESIAN: percentile > pctl_threshold
            ABSOLUTE: raw value > absolute_threshold from registry

        Args:
            fs: FileSignals for the file being checked
            signal: Signal enum member to check
            pctl_threshold: Percentile threshold for FULL/BAYESIAN tiers
                           (e.g., 0.90 = top 10%, 0.80 = top 20%)

        Returns:
            True if the signal exceeds the threshold for the current tier.
            False if ABSOLUTE tier and no absolute_threshold is defined.
        """
        meta = REGISTRY.get(signal)
        if meta is None:
            return False
        if self.tier == "ABSOLUTE":
            if meta.absolute_threshold is None:
                return False  # No absolute threshold defined -- cannot evaluate
            raw = getattr(fs, signal.value, 0)
            return raw > meta.absolute_threshold
        # BAYESIAN or FULL: use percentile
        return fs.percentiles.get(signal.value, 0) > pctl_threshold

    def below(self, fs: FileSignals, signal: Signal, pctl_threshold: float) -> bool:
        """Is this file's signal value below the threshold?

        For high-is-good signals (e.g., bus_factor, semantic_coherence):
            FULL/BAYESIAN: percentile < pctl_threshold
            ABSOLUTE: raw value < absolute_threshold from registry

        Args:
            fs: FileSignals for the file being checked
            signal: Signal enum member to check
            pctl_threshold: Percentile threshold for FULL/BAYESIAN tiers
                           (e.g., 0.20 = bottom 20%, 0.30 = bottom 30%)

        Returns:
            True if the signal is below the threshold for the current tier.
            False if ABSOLUTE tier and no absolute_threshold is defined.
        """
        meta = REGISTRY.get(signal)
        if meta is None:
            return False
        if self.tier == "ABSOLUTE":
            if meta.absolute_threshold is None:
                return False
            raw = getattr(fs, signal.value, 0)
            return raw < meta.absolute_threshold
        # BAYESIAN or FULL: use percentile
        # Default to 1.0 so that signals without percentiles don't false-trigger
        return fs.percentiles.get(signal.value, 1.0) < pctl_threshold

    def above_raw(self, fs: FileSignals, signal: Signal, threshold: float) -> bool:
        """Check raw signal value against a fixed threshold (tier-independent).

        Some checks use absolute values regardless of tier (e.g., fix_ratio > 0.4).
        This method provides that without requiring registry metadata.

        Args:
            fs: FileSignals for the file being checked
            signal: Signal enum member to check
            threshold: Absolute value threshold

        Returns:
            True if raw value > threshold.
        """
        raw = getattr(fs, signal.value, 0)
        return raw > threshold

    def below_raw(self, fs: FileSignals, signal: Signal, threshold: float) -> bool:
        """Check raw signal value below a fixed threshold (tier-independent).

        Some checks use absolute values regardless of tier (e.g., bus_factor <= 1.5).
        This method provides that without requiring registry metadata.

        Args:
            fs: FileSignals for the file being checked
            signal: Signal enum member to check
            threshold: Absolute value threshold

        Returns:
            True if raw value < threshold.
        """
        raw = getattr(fs, signal.value, 0)
        return raw < threshold


def compute_hotspot_median(field: SignalField) -> int:
    """Compute median of total_changes across non-test files.

    Excludes TEST role files to avoid skewing by test churn.
    Used by hotspot-filtered finders to gate dormant files.

    Args:
        field: SignalField with per_file signals populated

    Returns:
        Median total_changes value (int). Returns 0 if no active non-test files.
    """
    changes = [
        fs.total_changes
        for fs in field.per_file.values()
        if fs.role != "TEST" and fs.total_changes > 0
    ]
    if not changes:
        return 0
    changes_sorted = sorted(changes)
    n = len(changes_sorted)
    # Use lower median for even-length lists (conservative: harder to trigger)
    return changes_sorted[n // 2] if n % 2 == 1 else changes_sorted[n // 2 - 1]


def is_hotspot(fs: FileSignals, median_changes: int) -> bool:
    """Check if a file passes the hotspot filter.

    Hotspot-filtered finders only fire on files with change activity
    above the median. This prevents flagging dormant code.

    Args:
        fs: FileSignals for the file
        median_changes: Precomputed median from compute_hotspot_median()

    Returns:
        True if the file has enough change activity.
    """
    return fs.total_changes > median_changes
