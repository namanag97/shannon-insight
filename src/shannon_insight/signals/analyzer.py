"""SignalFusionAnalyzer — Wave 2 analyzer for signal fusion.

This analyzer runs AFTER all Wave 1 analyzers complete. It unifies
all signals from various store slots into a single SignalField.

Wave 1 analyzers (topo-sorted by requires/provides):
- StructuralAnalyzer
- TemporalAnalyzer
- SemanticAnalyzer
- ArchitectureAnalyzer
- SpectralAnalyzer

Wave 2 (always last):
- SignalFusionAnalyzer

The fusion analyzer has no requires/provides because the kernel
explicitly runs it after all Wave 1 analyzers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shannon_insight.insights.store_v2 import AnalysisStore


class SignalFusionAnalyzer:
    """Runs in Wave 2 — AFTER all Wave 1 analyzers complete.

    Collects signals from all store slots into a unified SignalField,
    computes percentiles, composites, and health Laplacian.
    """

    name = "signal_fusion"

    # Wave 2 analyzer: kernel runs this explicitly after Wave 1
    # No requires/provides needed
    requires: set[str] = set()
    provides: set[str] = {"signal_field"}

    # Critical: must run after all other analyzers
    run_last = True

    def analyze(self, store: AnalysisStore) -> None:
        """Build SignalField from store slots.

        The fusion pipeline runs 6 steps in order:
        1. collect - gather raw signals
        2. raw_risk - pre-percentile risk computation
        3. normalize - percentile computation
        4. module_temporal - module-level temporal aggregation
        5. composites - composite score computation
        6. laplacian - health Laplacian computation
        """
        from shannon_insight.signals.fusion import build

        signal_field = build(store)
        store.signal_field.set(signal_field, produced_by=self.name)
