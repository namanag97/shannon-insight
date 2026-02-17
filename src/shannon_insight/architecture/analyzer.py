"""ArchitectureAnalyzer for Phase 4.

Orchestrates:
1. Module detection (directories → Module objects)
2. Martin metrics computation
3. Layer inference
4. Violation detection
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..graph.models import CodebaseAnalysis
from ..infrastructure.entities import Entity, EntityId, EntityType
from ..infrastructure.relations import Relation, RelationType
from ..infrastructure.signals import Signal
from ..logging_config import get_logger
from .layers import build_module_graph, infer_layers
from .metrics import compute_module_metrics
from .models import Architecture
from .modules import detect_modules

if TYPE_CHECKING:
    from ..insights.store import AnalysisStore

logger = get_logger(__name__)


class ArchitectureAnalyzer:
    """Analyzer protocol implementation for architecture detection."""

    name = "architecture"
    requires: set[str] = {"structural", "roles"}
    provides: set[str] = {"architecture"}

    def analyze(self, store: AnalysisStore) -> None:
        """Run architecture analysis and populate store.architecture.

        Args:
            store: AnalysisStore with structural analysis completed
        """
        # Check prerequisites
        if not store.structural.available:
            logger.warning("Structural analysis not available - skipping architecture")
            store.architecture.set_error("structural not available", self.name)
            return

        structural: CodebaseAnalysis = store.structural.value

        # Get file paths from structural analysis
        file_paths = list(structural.files.keys())
        if not file_paths:
            logger.info("No files to analyze - skipping architecture")
            return

        # 1. Detect modules
        modules = detect_modules(file_paths, root_dir=store.root_dir)
        logger.debug(f"Detected {len(modules)} modules")

        if len(modules) < 2:
            logger.info("Single module detected - minimal architecture analysis")

        # 2. Compute Martin metrics per module
        roles_dict: dict[str, str] = {}
        if store.roles.available:
            roles_dict = store.roles.value

        for mod in modules.values():
            compute_module_metrics(
                mod,
                modules,
                structural.graph,
                roles_dict,
            )

        # 3. Build module graph (needed by fusion for Conway alignment)
        module_graph = build_module_graph(modules, structural.graph)

        # 4. Infer layers
        layers, violations = infer_layers(modules, structural.graph)
        logger.debug(f"Inferred {len(layers)} layers, {len(violations)} violations")

        # 5. Compute architecture-level metrics
        total_cross_edges = sum(mod.external_edges for mod in modules.values())
        violation_edge_count = sum(v.edge_count for v in violations)
        violation_rate = violation_edge_count / total_cross_edges if total_cross_edges > 0 else 0.0

        # 6. Assemble result
        architecture = Architecture(
            modules=modules,
            layers=layers,
            violations=violations,
            violation_rate=violation_rate,
            module_graph=module_graph,
            has_layering=len(layers) >= 2,
            max_depth=max((m.layer for m in modules.values()), default=0),
            module_count=len(modules),
        )

        # Store result
        store.architecture.set(architecture, produced_by=self.name)
        logger.debug(
            f"Architecture analysis complete: {architecture.module_count} modules, "
            f"{architecture.max_depth + 1} layers, {len(violations)} violations"
        )

        # Sync to FactStore
        self._sync_to_fact_store(store, architecture)

    def _sync_to_fact_store(self, store: AnalysisStore, architecture: Architecture) -> None:
        """Sync architecture analysis results to FactStore.

        Writes per-module signals (COHESION, COUPLING, INSTABILITY,
        ABSTRACTNESS, MAIN_SEQ_DISTANCE, BOUNDARY_ALIGNMENT, FILE_COUNT)
        and relations (IN_MODULE, DEPENDS_ON).

        Note: violation_rate is an intermediate term (not a standalone signal)
        stored in Architecture.violation_rate for use in architecture_health composite.
        """
        if not hasattr(store, "fact_store"):
            return

        fs = store.fact_store

        # Per-module signals
        for module_name, module in architecture.modules.items():
            mod_id = EntityId(EntityType.MODULE, module_name)

            # Ensure module entity exists before setting signals
            if fs.get_entity(mod_id) is None:
                fs.add_entity(Entity(id=mod_id, metadata={}))

            fs.set_signal(mod_id, Signal.COHESION, module.cohesion)
            fs.set_signal(mod_id, Signal.COUPLING, module.coupling)
            if module.instability is not None:
                fs.set_signal(mod_id, Signal.INSTABILITY, module.instability)
            fs.set_signal(mod_id, Signal.ABSTRACTNESS, module.abstractness)
            fs.set_signal(mod_id, Signal.MAIN_SEQ_DISTANCE, module.main_seq_distance)
            fs.set_signal(mod_id, Signal.BOUNDARY_ALIGNMENT, module.boundary_alignment)
            fs.set_signal(mod_id, Signal.FILE_COUNT, float(module.file_count))

        # Note: violation_rate is stored in Architecture object and used by
        # SignalFusionAnalyzer to compute architecture_health composite.
        # It is NOT a standalone signal in the Signal enum.

        # IN_MODULE relations (File -> Module)
        for module_name, module in architecture.modules.items():
            mod_id = EntityId(EntityType.MODULE, module_name)
            for file_path in module.files:
                file_id = EntityId(EntityType.FILE, file_path)
                fs.add_relation(
                    Relation(
                        type=RelationType.IN_MODULE,
                        source=file_id,
                        target=mod_id,
                    )
                )

        # DEPENDS_ON relations (Module -> Module)
        for src_module, targets in architecture.module_graph.items():
            src_id = EntityId(EntityType.MODULE, src_module)
            for tgt_module, edge_count in targets.items():
                tgt_id = EntityId(EntityType.MODULE, tgt_module)
                fs.add_relation(
                    Relation(
                        type=RelationType.DEPENDS_ON,
                        source=src_id,
                        target=tgt_id,
                        weight=float(edge_count),
                    )
                )

        logger.debug(
            f"FactStore sync: {len(architecture.modules)} modules, "
            f"{sum(len(module.files) for module in architecture.modules.values())} IN_MODULE relations, "
            f"{sum(len(targets) for targets in architecture.module_graph.values())} DEPENDS_ON relations"
        )
