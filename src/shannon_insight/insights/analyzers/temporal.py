"""TemporalAnalyzer — orchestrates git extraction, co-change, churn, and author distances."""

import subprocess
from pathlib import Path

from ...graph.distance import compute_author_distances
from ...logging_config import get_logger
from ...temporal import GitExtractor, build_churn_series, build_cochange_matrix
from ...temporal.models import GitHistory
from ..store_v2 import AnalysisStore

logger = get_logger(__name__)

# Minimum commits required for meaningful temporal analysis
_MIN_COMMITS = 10


class TemporalAnalyzer:
    name = "temporal"
    requires: set[str] = {"files"}
    provides: set[str] = {"git_history", "cochange", "churn", "author_distances"}

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

        # Git log returns paths relative to repo root, but file_metrics paths
        # are relative to root_dir. Normalize git paths so they match.
        self._normalize_git_paths(history, store.root_dir)

        cochange = build_cochange_matrix(history, analyzed_files)
        churn = build_churn_series(history, analyzed_files)

        store.git_history.set(history, produced_by=self.name)
        store.cochange.set(cochange, produced_by=self.name)
        store.churn.set(churn, produced_by=self.name)

        # Phase 3: G5 author distance space
        author_dists = compute_author_distances(history, analyzed_files)
        store.author_distances.set(author_dists, produced_by=self.name)

        logger.debug(
            f"Temporal analysis: {history.total_commits} commits, "
            f"{len(cochange.pairs)} co-change pairs, "
            f"{len(churn)} churn series, "
            f"{len(author_dists)} author distance pairs"
        )

    @staticmethod
    def _normalize_git_paths(history: GitHistory, root_dir: str) -> None:
        """Strip repo-root prefix from git paths to match file_metrics paths.

        Git log returns paths relative to the repo root (e.g. src/pkg/foo.py),
        but file_metrics paths are relative to root_dir (e.g. foo.py when
        root_dir is <repo>/src/pkg). This strips the root_dir prefix.
        """
        # Find the git repo root
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=root_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return
            repo_root = Path(result.stdout.strip()).resolve()
        except Exception:
            return

        root_path = Path(root_dir).resolve()
        try:
            prefix = str(root_path.relative_to(repo_root))
        except ValueError:
            return  # root_dir is not inside the repo

        if prefix == ".":
            return  # Already at repo root, no stripping needed

        prefix_slash = prefix + "/"

        for commit in history.commits:
            commit.files = [
                f[len(prefix_slash) :] if f.startswith(prefix_slash) else f for f in commit.files
            ]
