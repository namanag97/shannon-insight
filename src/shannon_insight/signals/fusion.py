"""FusionPipeline — typestate pattern for signal fusion ordering.

This is the Phase 0 SKELETON. Full implementation is Phase 5.

The typestate pattern enforces the correct 6-step ordering:
    1. collect: Gather raw signals from all store slots
    2. raw_risk: Compute raw_risk per file (pre-percentile)
    3. normalize: Compute percentiles (ABSOLUTE tier skips this)
    4. module_temporal: Fill module temporal signals
    5. composites: Compute all composite scores
    6. laplacian: Health Laplacian (uses raw_risk, not composites)

Each step returns the next stage type. You literally cannot call
step5_composites() on a _Collected object — the method doesn't exist.
Mypy catches reordering at type-check time.

Example usage:
    field = build(store)  # Chains all 6 steps
    # or manually:
    field = (FusionPipeline(store)
        .step1_collect()
        .step2_raw_risk()
        .step3_normalize()
        .step4_module_temporal()
        .step5_composites()
        .step6_laplacian())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shannon_insight.insights.store_v2 import AnalysisStore


@dataclass
class FileSignals:
    """Per-file signals container.

    Populated by fusion pipeline. Full fields added in Phase 5.
    """

    path: str = ""
    # Raw signals (populated in step1)
    pagerank: float = 0.0
    # ... more signals added in Phase 5

    # Percentiles (populated in step3)
    percentiles: dict[str, float] = field(default_factory=dict)

    # Composites (populated in step5)
    raw_risk: float = 0.0
    risk_score: float = 0.0


@dataclass
class ModuleSignals:
    """Per-module signals container.

    Populated by fusion pipeline. Full fields added in Phase 5.
    """

    path: str = ""
    # ... module signals added in Phase 5


@dataclass
class GlobalSignals:
    """Global (codebase-wide) signals container.

    Populated by fusion pipeline. Full fields added in Phase 5.
    """

    # ... global signals added in Phase 5
    modularity: float = 0.0
    codebase_health: float = 0.0


@dataclass
class SignalField:
    """The complete signal tensor.

    Contains all signals at all scales: per-file, per-module, global.
    This is what finders read from.
    """

    tier: str = "FULL"  # "ABSOLUTE" | "BAYESIAN" | "FULL"
    per_file: dict[str, FileSignals] = field(default_factory=dict)
    per_module: dict[str, ModuleSignals] = field(default_factory=dict)
    global_signals: GlobalSignals = field(default_factory=GlobalSignals)
    delta_h: dict[str, float] = field(default_factory=dict)  # Health Laplacian


class FusionPipeline:
    """Entry point for signal fusion. Each step returns the next stage type."""

    def __init__(self, store: AnalysisStore) -> None:
        self.store = store
        self.field = SignalField()
        self._determine_tier()

    def _determine_tier(self) -> None:
        """Set tier based on file count."""
        n = len(self.store.file_metrics)
        if n < 15:
            self.field.tier = "ABSOLUTE"
        elif n < 50:
            self.field.tier = "BAYESIAN"
        else:
            self.field.tier = "FULL"

    def step1_collect(self) -> _Collected:
        """Gather raw signals from all store slots into SignalField.

        Phase 0 skeleton: Just creates empty FileSignals per file.
        Phase 5: Full collection from scanning, graph, semantics, temporal.
        """
        for fm in self.store.file_metrics:
            self.field.per_file[fm.path] = FileSignals(path=fm.path)
        return _Collected(self.field, self.store)


class _Collected:
    """State after step1_collect. Can only proceed to step2_raw_risk."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step2_raw_risk(self) -> _RawRisked:
        """Compute raw_risk per file (pre-percentile). Used by health Laplacian.

        Phase 0 skeleton: No-op.
        Phase 5: Full raw_risk computation.
        """
        # Skeleton: raw_risk stays 0.0
        return _RawRisked(self.field, self.store)


class _RawRisked:
    """State after step2_raw_risk. Can only proceed to step3_normalize."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step3_normalize(self) -> _Normalized:
        """Compute percentiles. ABSOLUTE tier skips this.

        Phase 0 skeleton: No-op.
        Phase 5: Full percentile computation.
        """
        # Skeleton: percentiles dict stays empty
        return _Normalized(self.field, self.store)


class _Normalized:
    """State after step3_normalize. Can only proceed to step4_module_temporal."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step4_module_temporal(self) -> _ModuleTemporal:
        """Fill module temporal signals. Safe to read percentiles now.

        Phase 0 skeleton: No-op.
        Phase 5: Full module temporal computation.
        """
        return _ModuleTemporal(self.field, self.store)


class _ModuleTemporal:
    """State after step4_module_temporal. Can only proceed to step5_composites."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step5_composites(self) -> _Composited:
        """Compute all composite scores. Requires percentiles + module temporal.

        Phase 0 skeleton: No-op.
        Phase 5: Full composite computation (risk_score, health_score, etc.).
        """
        return _Composited(self.field, self.store)


class _Composited:
    """State after step5_composites. Can only proceed to step6_laplacian."""

    def __init__(self, field: SignalField, store: AnalysisStore) -> None:
        self.field = field
        self.store = store

    def step6_laplacian(self) -> SignalField:
        """Health Laplacian. Uses raw_risk, not composites. Final step.

        Phase 0 skeleton: No-op.
        Phase 5: Full delta_h computation.
        """
        return self.field


def build(store: AnalysisStore) -> SignalField:
    """Convenience function: run all 6 fusion steps.

    This is the ONLY valid call order for the pipeline.
    """
    return (
        FusionPipeline(store)
        .step1_collect()
        .step2_raw_risk()
        .step3_normalize()
        .step4_module_temporal()
        .step5_composites()
        .step6_laplacian()
    )
