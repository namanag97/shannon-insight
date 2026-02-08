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
from ..logging_config import get_logger
from .layers import infer_layers
from .metrics import compute_module_metrics
from .models import Architecture
from .modules import detect_modules

if TYPE_CHECKING:
    from ..insights.store_v2 import AnalysisStore

logger = get_logger(__name__)


class ArchitectureAnalyzer:
    """Analyzer protocol implementation for architecture detection."""

    name = "architecture"
    requires: set[str] = {"structural"}
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

        # 3. Infer layers
        layers, violations = infer_layers(modules, structural.graph)
        logger.debug(f"Inferred {len(layers)} layers, {len(violations)} violations")

        # 4. Compute architecture-level metrics
        total_cross_edges = sum(mod.external_edges for mod in modules.values())
        violation_edge_count = sum(v.edge_count for v in violations)
        violation_rate = violation_edge_count / total_cross_edges if total_cross_edges > 0 else 0.0

        # 5. Assemble result
        architecture = Architecture(
            modules=modules,
            layers=layers,
            violations=violations,
            violation_rate=violation_rate,
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
