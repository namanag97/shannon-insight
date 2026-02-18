"""StructuralExecutor — Build dependency graph and compute structural signals.

This phase builds the dependency graph from imports, then computes:
- PageRank (centrality)
- Betweenness centrality
- Strongly connected components
- Blast radius
- Louvain communities

Populates:
- store.structural: CodebaseAnalysis
- store.spectral: SpectralSummary (via SpectralAnalyzer)
- store.architecture: Architecture (via ArchitectureAnalyzer)
- store.semantics: FileSemantics (via SemanticAnalyzer)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...infrastructure.runtime import Phase
from ...logging_config import get_logger
from ..executor import BaseExecutor
from ..result import PhaseResult

if TYPE_CHECKING:
    from ...infrastructure.runtime import RuntimeContext
    from ...insights.store import AnalysisStore
    from ...session import AnalysisSession

logger = get_logger(__name__)


class StructuralExecutor(BaseExecutor):
    """Build dependency graph and run structural analyzers.

    Runs Wave 1 analyzers in topological order:
    1. StructuralAnalyzer - graph, PageRank, SCC, Louvain
    2. SpectralAnalyzer - Fiedler value, spectral gap
    3. SemanticAnalyzer - concepts, coherence, roles
    4. ArchitectureAnalyzer - modules, layers, Martin metrics
    """

    phase = Phase.STRUCTURAL
    timeout_seconds = 300  # 5 minutes
    name = "structural"

    def _execute(
        self,
        ctx: "RuntimeContext",
        store: "AnalysisStore",
        session: "AnalysisSession",
    ) -> PhaseResult:
        """Run structural analyzers."""
        from ...insights.analyzers import get_default_analyzers
        from ...insights.kernel_toposort import resolve_analyzer_order

        if store.file_count == 0:
            logger.warning("No files in store, skipping structural analysis")
            return PhaseResult.ok(items_processed=0)

        # Get Wave 1 analyzers in topological order
        analyzers = get_default_analyzers(session.config)
        ordered = resolve_analyzer_order(analyzers)

        ctx.set_phase_total(len(ordered))
        items_processed = 0
        items_failed = 0

        for analyzer in ordered:
            # Check cancellation
            if not ctx.should_continue:
                logger.warning("Structural analysis cancelled")
                break

            # Check requirements
            if not analyzer.requires.issubset(store.available):
                logger.debug(f"Skipping {analyzer.name}: requirements not met")
                ctx.advance(failed=True)
                items_failed += 1
                continue

            try:
                logger.debug(f"Running {analyzer.name}...")
                analyzer.analyze(store)
                items_processed += 1
                ctx.advance()
            except Exception as e:
                logger.warning(f"Analyzer {analyzer.name} failed: {e}")
                ctx.advance(failed=True)
                items_failed += 1
                # Continue with other analyzers (graceful degradation)

        logger.info(
            f"Structural analysis complete: {items_processed} analyzers succeeded, "
            f"{items_failed} failed"
        )

        return PhaseResult.ok(items_processed=items_processed)
