"""TemporalAnalyzer — orchestrates git extraction, co-change, and churn."""

from ...logging_config import get_logger
from ...temporal import GitExtractor, build_churn_series, build_cochange_matrix
from ..store_v2 import AnalysisStore

logger = get_logger(__name__)

# Minimum commits required for meaningful temporal analysis
_MIN_COMMITS = 10


class TemporalAnalyzer:
    name = "temporal"
    requires: set[str] = {"files"}
    provides: set[str] = {"git_history", "cochange", "churn"}

    def __init__(self, max_commits: int = 5000, min_commits: int = _MIN_COMMITS):
        self.max_commits = max_commits
        self.min_commits = min_commits

    def analyze(self, store: AnalysisStore) -> None:
        extractor = GitExtractor(store.root_dir, max_commits=self.max_commits)
        history = extractor.extract()

        if history is None:
            logger.info("No git history available — temporal analysis skipped")
            store.git_history.set_error("No git history available", self.name)
            return

        if history.total_commits < self.min_commits:
            logger.info(
                f"Only {history.total_commits} commits "
                f"(need {self.min_commits}) — temporal analysis skipped"
            )
            store.git_history.set_error(
                f"Only {history.total_commits} commits (need {self.min_commits})",
                self.name,
            )
            return

        analyzed_files = {fm.path for fm in store.file_metrics}

        cochange = build_cochange_matrix(history, analyzed_files)
        churn = build_churn_series(history, analyzed_files)

        store.git_history.set(history, produced_by=self.name)
        store.cochange.set(cochange, produced_by=self.name)
        store.churn.set(churn, produced_by=self.name)

        logger.debug(
            f"Temporal analysis: {history.total_commits} commits, "
            f"{len(cochange.pairs)} co-change pairs, "
            f"{len(churn)} churn series"
        )
