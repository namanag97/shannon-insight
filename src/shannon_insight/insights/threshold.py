"""ThresholdStrategy for tier-aware finder thresholds.

Finders use this to check signal thresholds without implementing tier logic themselves.
The signal registry provides absolute thresholds; this strategy handles branching.

Tier behavior:
    ABSOLUTE (<15 files): Uses absolute threshold from registry
    BAYESIAN (15-50 files): Uses percentile threshold
    FULL (50+ files): Uses percentile threshold

Example usage in finder:
    check = ThresholdCheck(store.signal_field.value)
    for path, fs in store.signal_field.value.per_file.items():
        if check.above(fs, Signal.PAGERANK, 0.90):  # pctl > 0.90
            yield Finding(...)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shannon_insight.signals.registry import REGISTRY, Signal

if TYPE_CHECKING:
    pass


class ThresholdCheck:
    """Tier-aware signal threshold checking. Injected into every finder.

    Attributes:
        tier: Current normalization tier ("ABSOLUTE", "BAYESIAN", or "FULL")
    """

    def __init__(self, field: Any) -> None:
        """Initialize with signal field.

        Args:
            field: SignalField containing tier and signal data
        """
        self.tier = field.tier

    def above(self, fs: Any, signal: Signal, pctl_threshold: float) -> bool:
        """Is this file above the threshold for this signal?

        For "high is bad" signals (pagerank, stub_ratio, etc.):
            FULL/BAYESIAN: uses percentile
            ABSOLUTE: uses absolute threshold from registry

        Args:
            fs: FileSignals object with raw values and percentiles
            signal: Signal enum value to check
            pctl_threshold: Percentile threshold (0.0 to 1.0) for FULL/BAYESIAN tiers

        Returns:
            True if signal exceeds threshold, False otherwise
        """
        meta = REGISTRY[signal]

        if self.tier == "ABSOLUTE":
            if meta.absolute_threshold is None:
                return False  # No absolute threshold defined → can't evaluate
            raw = getattr(fs, signal.value, 0)
            return raw > meta.absolute_threshold

        # FULL or BAYESIAN tier: use percentile
        pctl_value: float = fs.percentiles.get(signal.value, 0)
        return pctl_value > pctl_threshold

    def above_adaptive(self, fs: Any, signal: Signal, all_values: list[float]) -> bool:
        """Is this file above the natural breakpoint for this signal?

        Uses Otsu's method to find the natural threshold in the distribution.
        Falls back to percentile if Otsu produces degenerate result.

        Args:
            fs: FileSignals object
            signal: Signal enum value
            all_values: All values of this signal across the codebase

        Returns:
            True if signal exceeds Otsu threshold
        """
        from ..math.statistics import Statistics

        if len(all_values) < 4:
            return self.above(fs, signal, 0.75)  # Fall back to fixed percentile

        threshold = Statistics.otsu_threshold(all_values)
        raw = getattr(fs, signal.value, 0)
        return raw > threshold

    def mad_outlier(
        self, fs: Any, signal: Signal, all_values: list[float], z_cutoff: float = 3.0
    ) -> bool:
        """Is this file a MAD-based outlier for this signal?

        Uses robust z-scores (MAD) to detect genuine outliers.

        Args:
            fs: FileSignals object
            signal: Signal enum value
            all_values: All values of this signal across the codebase
            z_cutoff: MAD z-score cutoff (default 3.0)

        Returns:
            True if file is a statistical outlier
        """
        from ..math.statistics import Statistics

        if len(all_values) < 4:
            return False

        raw = getattr(fs, signal.value, 0)
        z_scores = Statistics.mad_z_score(all_values)

        # Find index of this file's value
        try:
            idx = all_values.index(raw)
            return abs(z_scores[idx]) > z_cutoff
        except (ValueError, IndexError):
            return False

    def below(self, fs: Any, signal: Signal, pctl_threshold: float) -> bool:
        """Is this file below the threshold for this signal?

        Inverse of above(). For "high is good" signals (bus_factor, coherence, etc.):
            FULL/BAYESIAN: uses percentile
            ABSOLUTE: uses absolute threshold from registry

        Args:
            fs: FileSignals object with raw values and percentiles
            signal: Signal enum value to check
            pctl_threshold: Percentile threshold (0.0 to 1.0) for FULL/BAYESIAN tiers

        Returns:
            True if signal is below threshold, False otherwise
        """
        meta = REGISTRY[signal]

        if self.tier == "ABSOLUTE":
            if meta.absolute_threshold is None:
                return False  # No absolute threshold defined → can't evaluate
            raw = getattr(fs, signal.value, 0)
            return raw < meta.absolute_threshold

        # FULL or BAYESIAN tier: use percentile
        pctl_value: float = fs.percentiles.get(signal.value, 1.0)
        return pctl_value < pctl_threshold
