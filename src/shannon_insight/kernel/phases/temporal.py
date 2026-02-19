"""TemporalExecutor — Extract git history and compute temporal signals.

This phase extracts git history and computes:
- Commit history per file
- Churn series (change frequency, trajectory)
- Co-change matrix (files that change together)
- Author statistics (bus factor, entropy)

Populates:
- store.git_history: GitHistory
- store.churn: Dict[path, ChurnSeries]
- store.cochange: CoChangeMatrix
- store.author_distances: List[AuthorDistance]

Note: This phase is skipped if git is not available.
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


class TemporalExecutor(BaseExecutor):
    """Extract git history and compute temporal signals.

    Uses TemporalAnalyzer to extract git history if available.
    Gracefully skips if not a git repository.
    """

    phase = Phase.TEMPORAL
    timeout_seconds = 300  # 5 minutes for git log
    name = "temporal"

    def _execute(
        self,
        ctx: RuntimeContext,
        store: AnalysisStore,
        session: AnalysisSession,
    ) -> PhaseResult:
        """Extract git history."""
        # Check if git is available
        if not session.env.is_git_repo:
            logger.info("Not a git repository, skipping temporal analysis")
            return PhaseResult.ok(items_processed=0)

        # Import here to avoid circular dependency
        from ...insights.analyzers.temporal import TemporalAnalyzer

        analyzer = TemporalAnalyzer(
            max_commits=session.config.git_max_commits,
            min_commits=session.config.git_min_commits,
            facts_db=store.facts_db,
        )

        try:
            # Check requirements
            if not analyzer.requires.issubset(store.available):
                logger.debug("Skipping temporal: requirements not met")
                return PhaseResult.ok(items_processed=0)

            analyzer.analyze(store)

            # Count items processed
            items_processed = 0
            if store.git_history.available:
                items_processed = store.git_history.value.total_commits

            logger.info(f"Temporal analysis complete: {items_processed} commits analyzed")
            return PhaseResult.ok(items_processed=items_processed)

        except Exception as e:
            logger.warning(f"Temporal analysis failed: {e}")
            # Return partial success (we can continue without temporal data)
            return PhaseResult.ok(items_processed=0)
