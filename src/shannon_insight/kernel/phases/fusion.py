"""FusionExecutor — Compute signals and composites.

This phase runs Wave 2 analyzers (after all Wave 1 complete):
- SignalFusionAnalyzer unifies all signals into SignalField
- Computes percentiles (tier-dependent)
- Computes composite signals (risk_score, health_score, etc.)
- Builds health Laplacian delta_h

Populates:
- store.signal_field: SignalField with FileSignals, ModuleSignals, GlobalSignals

After this phase, store._content_cache is cleared to free memory.
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


class FusionExecutor(BaseExecutor):
    """Compute signals and composites.

    Runs Wave 2 analyzers which require all Wave 1 signals.
    """

    phase = Phase.FUSION
    timeout_seconds = 180  # 3 minutes
    name = "fusion"

    def _execute(
        self,
        ctx: RuntimeContext,
        store: AnalysisStore,
        session: AnalysisSession,
    ) -> PhaseResult:
        """Run signal fusion."""
        from ...insights.analyzers import get_wave2_analyzers

        if store.file_count == 0:
            logger.warning("No files in store, skipping fusion")
            return PhaseResult.ok(items_processed=0)

        wave2_analyzers = get_wave2_analyzers()
        ctx.set_phase_total(len(wave2_analyzers))

        items_processed = 0
        for analyzer in wave2_analyzers:
            if not ctx.should_continue:
                logger.warning("Fusion cancelled")
                break

            try:
                logger.debug(f"Running {analyzer.name}...")
                analyzer.analyze(store)
                items_processed += 1
                ctx.advance()
            except Exception as e:
                logger.warning(f"Wave 2 analyzer {analyzer.name} failed: {e}")
                ctx.advance(failed=True)

        # Clear content cache to free memory (no longer needed after fusion)
        store.clear_content_cache()

        logger.info(f"Fusion complete: signal_field available={store.signal_field.available}")
        return PhaseResult.ok(items_processed=items_processed)
