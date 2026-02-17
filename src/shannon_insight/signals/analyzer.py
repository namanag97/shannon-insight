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

CRITICAL: After fusion, signals are synced to FactStore so that
pattern predicates can read them. Without this sync, patterns
that read fusion-computed signals (STUB_RATIO, SEMANTIC_COHERENCE,
RISK_SCORE, etc.) would fail or produce incorrect results.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from shannon_insight.infrastructure.entities import Entity, EntityId, EntityType
from shannon_insight.infrastructure.signals import Signal

if TYPE_CHECKING:
    from shannon_insight.insights.store import AnalysisStore
    from shannon_insight.signals.models import SignalField

logger = logging.getLogger(__name__)


class SignalFusionAnalyzer:
    """Runs in Wave 2 — AFTER all Wave 1 analyzers complete.

    Collects signals from all store slots into a unified SignalField,
    computes percentiles, composites, and health Laplacian.

    After fusion, syncs all computed signals to FactStore so patterns
    can read them via store.get_signal().
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

        After fusion, syncs all signals to FactStore for pattern execution.
        """
        from shannon_insight.signals.fusion import build

        # Session is required for tier information
        if store.session is None:
            raise ValueError("AnalysisStore.session must be set before signal fusion")

        signal_field = build(store, store.session)
        store.signal_field.set(signal_field, produced_by=self.name)

        # CRITICAL: Sync fusion-computed signals to FactStore
        # Without this, patterns cannot read signals like STUB_RATIO,
        # SEMANTIC_COHERENCE, RISK_SCORE, module signals, etc.
        self._sync_to_fact_store(store, signal_field)

    def _sync_to_fact_store(self, store: AnalysisStore, field: SignalField) -> None:
        """Sync all fusion-computed signals to FactStore.

        This enables pattern predicates to read signals via store.get_signal().
        Without this sync, patterns that depend on fusion signals would fail.

        Syncs:
        - Per-file signals (FileSignals) - 36 signals
        - Per-module signals (ModuleSignals) - 15 signals
        - Global signals (GlobalSignals) - 11 signals
        """
        if not hasattr(store, "fact_store"):
            return

        fs = store.fact_store
        producer = self.name

        # Per-file signals
        file_count = 0
        for path, file_signals in field.per_file.items():
            entity_id = EntityId(EntityType.FILE, path)
            self._sync_file_signals(fs, entity_id, file_signals, producer)
            file_count += 1

        # Per-module signals
        module_count = 0
        for path, module_signals in field.per_module.items():
            entity_id = EntityId(EntityType.MODULE, path)
            # Ensure module entity exists
            if fs.get_entity(entity_id) is None:
                fs.add_entity(Entity(id=entity_id, metadata={}))
            self._sync_module_signals(fs, entity_id, module_signals, producer)
            module_count += 1

        # Global signals
        codebase_id = EntityId(EntityType.CODEBASE, store.root_dir)
        if fs.get_entity(codebase_id) is None:
            fs.add_entity(Entity(id=codebase_id, metadata={}))
        self._sync_global_signals(fs, codebase_id, field.global_signals, producer)

        logger.debug(
            f"FactStore sync: {file_count} files, {module_count} modules, global signals synced"
        )

    def _sync_file_signals(self, fs, entity_id: EntityId, signals, producer: str) -> None:
        """Sync FileSignals to FactStore.

        Only syncs signals that are computed during fusion and NOT already
        synced by Wave 1 analyzers. Signals like PAGERANK, BUS_FACTOR are
        already in FactStore from StructuralAnalyzer and TemporalAnalyzer.
        """
        # IR1 signals from FileSyntax (not synced by scanning)
        fs.set_signal(entity_id, Signal.STUB_RATIO, signals.stub_ratio, producer=producer)
        fs.set_signal(entity_id, Signal.IMPL_GINI, signals.impl_gini, producer=producer)
        fs.set_signal(entity_id, Signal.MAX_NESTING, signals.max_nesting, producer=producer)

        # IR2 semantic signals (SEMANTIC_COHERENCE computed in fusion)
        fs.set_signal(
            entity_id, Signal.SEMANTIC_COHERENCE, signals.semantic_coherence, producer=producer
        )

        # IR3 graph signals computed in fusion (overwrites 0.0 from StructuralAnalyzer)
        fs.set_signal(entity_id, Signal.COGNITIVE_LOAD, signals.cognitive_load, producer=producer)
        fs.set_signal(
            entity_id, Signal.COMPRESSION_RATIO, signals.compression_ratio, producer=producer
        )

        # Composites (computed in fusion step 5)
        fs.set_signal(entity_id, Signal.RISK_SCORE, signals.risk_score, producer=producer)
        fs.set_signal(entity_id, Signal.WIRING_QUALITY, signals.wiring_quality, producer=producer)

    def _sync_module_signals(self, fs, entity_id: EntityId, signals, producer: str) -> None:
        """Sync ModuleSignals to FactStore."""
        # Martin metrics
        fs.set_signal(entity_id, Signal.COHESION, signals.cohesion, producer=producer)
        fs.set_signal(entity_id, Signal.COUPLING, signals.coupling, producer=producer)
        if signals.instability is not None:
            fs.set_signal(entity_id, Signal.INSTABILITY, signals.instability, producer=producer)
        fs.set_signal(entity_id, Signal.ABSTRACTNESS, signals.abstractness, producer=producer)
        fs.set_signal(
            entity_id, Signal.MAIN_SEQ_DISTANCE, signals.main_seq_distance, producer=producer
        )

        # Boundary analysis
        fs.set_signal(
            entity_id, Signal.BOUNDARY_ALIGNMENT, signals.boundary_alignment, producer=producer
        )
        fs.set_signal(
            entity_id,
            Signal.LAYER_VIOLATION_COUNT,
            signals.layer_violation_count,
            producer=producer,
        )
        fs.set_signal(
            entity_id, Signal.ROLE_CONSISTENCY, signals.role_consistency, producer=producer
        )

        # Module temporal
        fs.set_signal(entity_id, Signal.VELOCITY, signals.velocity, producer=producer)
        fs.set_signal(
            entity_id, Signal.COORDINATION_COST, signals.coordination_cost, producer=producer
        )
        fs.set_signal(entity_id, Signal.KNOWLEDGE_GINI, signals.knowledge_gini, producer=producer)
        fs.set_signal(
            entity_id, Signal.MODULE_BUS_FACTOR, signals.module_bus_factor, producer=producer
        )

        # Aggregates
        fs.set_signal(
            entity_id, Signal.MEAN_COGNITIVE_LOAD, signals.mean_cognitive_load, producer=producer
        )
        fs.set_signal(entity_id, Signal.FILE_COUNT, signals.file_count, producer=producer)
        fs.set_signal(entity_id, Signal.HEALTH_SCORE, signals.health_score, producer=producer)

    def _sync_global_signals(self, fs, entity_id: EntityId, signals, producer: str) -> None:
        """Sync GlobalSignals to FactStore."""
        # Wiring quality signals
        fs.set_signal(entity_id, Signal.ORPHAN_RATIO, signals.orphan_ratio, producer=producer)
        fs.set_signal(entity_id, Signal.PHANTOM_RATIO, signals.phantom_ratio, producer=producer)
        fs.set_signal(entity_id, Signal.GLUE_DEFICIT, signals.glue_deficit, producer=producer)

        # Composites
        fs.set_signal(entity_id, Signal.WIRING_SCORE, signals.wiring_score, producer=producer)
        fs.set_signal(
            entity_id, Signal.ARCHITECTURE_HEALTH, signals.architecture_health, producer=producer
        )
        fs.set_signal(entity_id, Signal.CODEBASE_HEALTH, signals.codebase_health, producer=producer)
