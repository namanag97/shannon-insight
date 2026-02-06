"""TemporalAnalyzer — orchestrates git extraction, co-change, and churn."""

from ...logging_config import get_logger
from ...temporal import GitExtractor, build_churn_series, build_cochange_matrix
from ..store import AnalysisStore

logger = get_logger(__name__)

# Minimum commits required for meaningful temporal analysis
_MIN_COMMITS = 10


class TemporalAnalyzer:
    name = "temporal"
    requires: set[str] = {"files"}
    provides: set[str] = {"temporal"}

    def __init__(self, max_commits: int = 5000, min_commits: int = _MIN_COMMITS):
        self.max_commits = max_commits
        self.min_commits = min_commits

    def analyze(self, store: AnalysisStore) -> None:
        extractor = GitExtractor(store.root_dir, max_commits=self.max_commits)
        history = extractor.extract()

        if history is None:
            logger.info("No git history available — temporal analysis skipped")
            return

        if history.total_commits < self.min_commits:
            logger.info(
                f"Only {history.total_commits} commits "
                f"(need {self.min_commits}) — temporal analysis skipped"
            )
            return

        analyzed_files = {fm.path for fm in store.file_metrics}

        store.git_history = history
        store.cochange = build_cochange_matrix(history, analyzed_files)
        store.churn = build_churn_series(history, analyzed_files)

        logger.debug(
            f"Temporal analysis: {history.total_commits} commits, "
            f"{len(store.cochange.pairs)} co-change pairs, "
            f"{len(store.churn)} churn series"
        )
