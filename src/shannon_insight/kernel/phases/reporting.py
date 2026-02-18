"""ReportingExecutor — Rank findings and capture snapshot.

This phase performs final processing:
1. Run persistence finders (if historical data available)
2. Deduplicate findings (subsumption rules)
3. Rank findings by severity x impact
4. Capture TensorSnapshot for persistence
5. Build InsightResult

Produces:
- ctx._insight_result: InsightResult
- ctx._snapshot: TensorSnapshot
"""

from __future__ import annotations

from pathlib import Path
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


class ReportingExecutor(BaseExecutor):
    """Rank findings and capture snapshot.

    Final phase that:
    1. Optionally runs persistence finders
    2. Deduplicates and ranks findings
    3. Captures TensorSnapshot
    4. Builds InsightResult
    """

    phase = Phase.REPORTING
    timeout_seconds = 60  # 1 minute
    name = "reporting"

    def _execute(
        self,
        ctx: "RuntimeContext",
        store: "AnalysisStore",
        session: "AnalysisSession",
    ) -> PhaseResult:
        """Build final result and snapshot."""
        from ...insights.models import InsightResult, StoreSummary
        from ...insights.ranking import deduplicate_findings, rank_findings
        from ...persistence.capture import capture_tensor_snapshot

        # Get findings from patterns phase
        findings: list = getattr(ctx, "_findings", [])
        pattern_findings: list = getattr(ctx, "_pattern_findings", [])

        # Run persistence finders if historical data available
        if self._has_historical_data(store.root_dir):
            self._run_persistence_finders(store, findings, pattern_findings)

        # Deduplicate and rank
        findings = deduplicate_findings(findings)

        # Get file signals for impact-based ranking
        file_signals = None
        if store.signal_field.available:
            file_signals = store.signal_field.value.per_file

        findings = rank_findings(findings, file_signals)

        # Cap findings
        max_findings = session.config.max_findings
        capped = findings[:max_findings]

        # Build result
        result = InsightResult(
            findings=capped,
            store_summary=self._summarize(store),
        )

        # Capture snapshot
        snapshot = capture_tensor_snapshot(store, result, session)

        # Store for kernel to extract
        ctx._insight_result = result  # type: ignore
        ctx._snapshot = snapshot  # type: ignore

        logger.info(f"Reporting complete: {len(capped)} findings, {snapshot.file_count} files")
        return PhaseResult.ok(items_processed=len(capped))

    def _has_historical_data(self, root_dir: str, min_snapshots: int = 3) -> bool:
        """Check if historical data is available for persistence finders."""
        db_path = Path(root_dir) / ".shannon" / "history.db"
        if not db_path.exists():
            return False

        try:
            import sqlite3

            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM snapshots")
                count: int = cursor.fetchone()[0]
                return count >= min_snapshots
        except Exception:
            return False

    def _run_persistence_finders(
        self, store: "AnalysisStore", findings: list, current_findings: list
    ) -> None:
        """Run persistence-based finders with DB connection."""
        from ...insights.finders import get_persistence_finders
        from ...persistence import HistoryDB

        try:
            with HistoryDB(store.root_dir) as db:
                for finder in get_persistence_finders():
                    try:
                        if finder.name == "chronic_problem":
                            new_findings = finder.find(
                                store=store,
                                db_conn=db.conn,
                                current_findings=current_findings,
                            )
                        else:
                            new_findings = finder.find(store=store, db_conn=db.conn)
                        findings.extend(new_findings)
                    except Exception as e:
                        logger.warning(f"Persistence finder {finder.name} failed: {e}")
        except Exception as e:
            logger.debug(f"No history DB available: {e}")

    def _summarize(self, store: "AnalysisStore") -> "StoreSummary":
        """Build summary from store state."""
        from ...insights.models import StoreSummary

        summary = StoreSummary(
            total_files=store.file_count,
            signals_available=sorted(store.available),
        )

        if store.structural.available:
            summary.total_modules = store.structural.value.total_modules

        if store.git_history.available:
            summary.commits_analyzed = store.git_history.value.total_commits
            summary.git_available = True

        if store.spectral.available:
            summary.fiedler_value = store.spectral.value.fiedler_value

        return summary
