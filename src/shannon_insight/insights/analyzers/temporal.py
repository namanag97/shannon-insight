"""TemporalAnalyzer — orchestrates git extraction, co-change, churn, and author distances.

This analyzer uses the new DB-backed git storage for:
1. Persistent raw git data (commits, file changes with line counts)
2. Incremental updates (only fetch new commits)
3. Efficient temporal queries

The flow:
    GitRawExtractor → GitFactDatabase → build_churn_series_from_db
                                      → build_cochange_matrix_from_db
                                      → compute_author_distances

A GitHistory is still populated for backward compatibility with finders.
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ...graph.distance import compute_author_distances
from ...infrastructure.entities import EntityId, EntityType
from ...infrastructure.relations import Relation, RelationType
from ...infrastructure.signals import Signal
from ...logging_config import get_logger
from ...persistence.git_facts import GitFactDatabase
from ...persistence.git_models import GitExtractionSession
from ...temporal import (
    GitRawExtractor,
    build_churn_series_from_db,
    build_cochange_matrix_from_db,
)
from ...temporal.compat import raw_data_to_history
from ...temporal.models import GitHistory
from ..store import AnalysisStore

logger = get_logger(__name__)

# Minimum commits required for meaningful temporal analysis
_MIN_COMMITS = 10

# Default git_facts.db location
_GIT_FACTS_DB = ".shannon/git_facts.db"


class TemporalAnalyzer:
    """Analyze git history for churn, co-change, and authorship patterns.

    Uses persistent SQLite storage for raw git data, enabling:
    - Incremental updates (only fetch new commits since last run)
    - Rich queries (line-level churn, authorship, rename tracking)
    - Multiple analyses without re-parsing git log
    """

    name = "temporal"
    requires: set[str] = set()  # No deps - git extraction is independent
    provides: set[str] = {"git_history", "cochange", "churn", "author_distances"}

    def __init__(self, max_commits: int = 5000, min_commits: int = _MIN_COMMITS):
        self.max_commits = max_commits
        self.min_commits = min_commits

    def analyze(self, store: AnalysisStore) -> None:
        """Run temporal analysis using DB-backed git storage."""
        # Determine git_facts.db path
        db_path = Path(store.root_dir) / _GIT_FACTS_DB

        # Check for incremental update
        since_sha = None
        if db_path.exists():
            try:
                db = GitFactDatabase(db_path)
                last_session = db.get_latest_session(store.root_dir)
                if last_session:
                    since_sha = last_session.head_sha
                    logger.debug(f"Incremental update from {since_sha[:8]}...")
            except Exception as e:
                logger.warning(f"Failed to read existing git_facts.db: {e}")

        # Extract raw git data
        extractor = GitRawExtractor(store.root_dir, max_commits=self.max_commits)
        raw_data = extractor.extract(since_sha=since_sha)

        if raw_data is None:
            logger.info("No git history available — temporal analysis skipped")
            store.git_history.set_error("No git history available", self.name)
            return

        # For incremental updates with no new commits, use existing DB data
        if raw_data.commit_count == 0 and since_sha:
            logger.debug("No new commits since last extraction")
            # Still need to run analysis from existing DB data
            db = GitFactDatabase(db_path)
        else:
            # Store new data to database
            db = GitFactDatabase(db_path)
            session = GitExtractionSession(
                id=str(uuid4()),
                repo_path=store.root_dir,
                started_at=datetime.now(timezone.utc),
                completed_at=None,
                head_sha=raw_data.head_sha,
                oldest_sha=raw_data.oldest_sha,
                commit_count=0,
                file_change_count=0,
                status="running",
            )
            db.create_session(session)

            try:
                db.store_commits_batch(raw_data.commits, session.id)
                db.store_file_changes_batch(raw_data.file_changes)
                db.complete_session(
                    session.id,
                    raw_data.commit_count,
                    raw_data.file_change_count,
                )
                logger.debug(
                    f"Stored {raw_data.commit_count} commits, "
                    f"{raw_data.file_change_count} file changes"
                )
            except Exception as e:
                db.complete_session(session.id, 0, 0, error_message=str(e))
                raise

        # Check minimum commits (from DB)
        stats = db.get_stats()
        total_commits = stats.get("commit_count", 0)
        if total_commits < self.min_commits:
            logger.info(
                f"Only {total_commits} commits "
                f"(need {self.min_commits}) — temporal analysis skipped"
            )
            store.git_history.set_error(
                f"Only {total_commits} commits (need {self.min_commits})",
                self.name,
            )
            return

        # Get analyzed files
        analyzed_files = set(store.files.keys())

        # Normalize paths: git paths are repo-relative, file paths may be subdir-relative
        analyzed_files = self._normalize_file_paths(store.root_dir, analyzed_files)

        # Get churn thresholds from config
        window_weeks = 4
        slope_threshold = 0.1
        cv_threshold = 0.5
        if store.session is not None and store.session.config is not None:
            thresholds = store.session.config.thresholds
            window_weeks = thresholds.churn_window_weeks
            slope_threshold = thresholds.churn_slope_threshold
            cv_threshold = thresholds.churn_cv_threshold

        # Build churn and cochange from database
        churn = build_churn_series_from_db(
            db,
            analyzed_files,
            window_weeks=window_weeks,
            slope_threshold=slope_threshold,
            cv_threshold=cv_threshold,
        )
        cochange = build_cochange_matrix_from_db(db, analyzed_files)

        # Build GitHistory for backward compatibility
        # We need to reconstruct it from the new data or fetch from DB
        if raw_data.commit_count > 0:
            history = raw_data_to_history(raw_data)
        else:
            # Fetch commits from DB to build history
            history = self._build_history_from_db(db, analyzed_files)

        # Normalize git paths in history to match file paths
        self._normalize_git_paths(history, store.root_dir)

        # Set store slots
        store.git_history.set(history, produced_by=self.name)
        store.cochange.set(cochange, produced_by=self.name)
        store.churn.set(churn, produced_by=self.name)

        # Phase 3: G5 author distance space
        author_dists = compute_author_distances(history, analyzed_files)
        store.author_distances.set(author_dists, produced_by=self.name)

        # Sync temporal signals to FactStore
        self._sync_to_fact_store(store, churn, cochange)

        logger.debug(
            f"Temporal analysis: {total_commits} commits (DB), "
            f"{len(cochange.pairs)} co-change pairs, "
            f"{len(churn)} churn series, "
            f"{len(author_dists)} author distance pairs"
        )

    def _build_history_from_db(
        self, db: GitFactDatabase, analyzed_files: set[str]
    ) -> GitHistory:
        """Build GitHistory from database for backward compatibility."""
        from ...temporal.models import Commit

        commits = db.get_commits_touching_files(analyzed_files)

        # Convert to old Commit format
        old_commits = []
        for gc in commits:
            # Get files for this commit
            with db._connect() as conn:
                cursor = conn.execute(
                    "SELECT file_path FROM git_file_changes WHERE commit_hash = ?",
                    (gc.hash,),
                )
                files = [row["file_path"] for row in cursor]

            old_commits.append(
                Commit(
                    hash=gc.hash,
                    timestamp=gc.timestamp,
                    author=gc.author_email,
                    files=files,
                    subject=gc.subject,
                )
            )

        file_set = {fc for c in old_commits for fc in c.files}
        span_days = 0
        if len(old_commits) >= 2:
            newest = old_commits[0].timestamp
            oldest = old_commits[-1].timestamp
            span_days = max(1, (newest - oldest) // 86400)

        return GitHistory(
            commits=old_commits,
            file_set=file_set,
            span_days=span_days,
        )

    def _normalize_file_paths(self, root_dir: str, file_paths: set[str]) -> set[str]:
        """Convert file paths to repo-relative paths for git matching."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=root_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return file_paths
            repo_root = Path(result.stdout.strip()).resolve()
        except Exception:
            return file_paths

        root_path = Path(root_dir).resolve()
        try:
            prefix = str(root_path.relative_to(repo_root))
        except ValueError:
            return file_paths

        if prefix == ".":
            return file_paths

        # Add prefix to convert subdir-relative to repo-relative
        prefix_slash = prefix + "/"
        return {prefix_slash + f for f in file_paths}

    def _sync_to_fact_store(self, store: AnalysisStore, churn, cochange) -> None:
        """Sync temporal analysis results to FactStore.

        Writes per-file churn signals (TOTAL_CHANGES, CHURN_CV, BUS_FACTOR,
        AUTHOR_ENTROPY, FIX_RATIO, REFACTOR_RATIO) and COCHANGES_WITH
        relations for significant co-change pairs.
        """
        if not hasattr(store, "fact_store"):
            return

        fs = store.fact_store

        # Per-file churn signals
        for path, cs in churn.items():
            entity_id = EntityId(EntityType.FILE, path)
            fs.set_signal(entity_id, Signal.TOTAL_CHANGES, cs.total_changes)
            fs.set_signal(entity_id, Signal.CHURN_CV, cs.cv)
            fs.set_signal(entity_id, Signal.BUS_FACTOR, cs.bus_factor)
            fs.set_signal(entity_id, Signal.AUTHOR_ENTROPY, cs.author_entropy)
            fs.set_signal(entity_id, Signal.FIX_RATIO, cs.fix_ratio)
            fs.set_signal(entity_id, Signal.REFACTOR_RATIO, cs.refactor_ratio)
            fs.set_signal(entity_id, Signal.CHURN_TRAJECTORY, cs.trajectory)
            fs.set_signal(entity_id, Signal.CHURN_SLOPE, cs.slope)

        # COCHANGES_WITH relations (weighted by lift, with full metadata)
        for (file_a, file_b), pair in cochange.pairs.items():
            src_id = EntityId(EntityType.FILE, file_a)
            tgt_id = EntityId(EntityType.FILE, file_b)
            metadata = {
                "lift": pair.lift,
                "confidence_a_b": pair.confidence_a_b,
                "confidence_b_a": pair.confidence_b_a,
                "cochange_count": pair.cochange_count,
            }
            fs.add_relation(
                Relation(
                    type=RelationType.COCHANGES_WITH,
                    source=src_id,
                    target=tgt_id,
                    weight=pair.lift,
                    metadata=metadata,
                )
            )
            # Reverse direction (symmetric)
            reverse_metadata = {
                "lift": pair.lift,
                "confidence_a_b": pair.confidence_b_a,
                "confidence_b_a": pair.confidence_a_b,
                "cochange_count": pair.cochange_count,
            }
            fs.add_relation(
                Relation(
                    type=RelationType.COCHANGES_WITH,
                    source=tgt_id,
                    target=src_id,
                    weight=pair.lift,
                    metadata=reverse_metadata,
                )
            )

        logger.debug(
            f"FactStore sync: {len(churn)} churn signals, "
            f"{len(cochange.pairs)} COCHANGES_WITH relations"
        )

    @staticmethod
    def _normalize_git_paths(history: GitHistory, root_dir: str) -> None:
        """Strip repo-root prefix from git paths to match file paths.

        Git log returns paths relative to the repo root (e.g. src/pkg/foo.py),
        but file paths are relative to root_dir (e.g. foo.py when
        root_dir is <repo>/src/pkg). This strips the root_dir prefix.
        """
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
            return

        if prefix == ".":
            return

        prefix_slash = prefix + "/"

        for commit in history.commits:
            commit.files = [
                f[len(prefix_slash) :] if f.startswith(prefix_slash) else f
                for f in commit.files
            ]
