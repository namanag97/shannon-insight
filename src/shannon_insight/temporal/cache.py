"""SQLite-based commit cache for incremental temporal analysis.

The cache stores parsed git commits to avoid re-parsing the entire history
on every run. On subsequent runs, only new commits (since last_sha) are
parsed and merged with the cached data.

Cache location: .shannon/commit_cache.db (created alongside analysis root)
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ..logging_config import get_logger
from .models import Commit

logger = get_logger(__name__)

# Schema version for migrations
_SCHEMA_VERSION = 1


class CommitCache:
    """SQLite-based commit cache for incremental temporal analysis.

    The cache stores:
    - Parsed commits with metadata (sha, timestamp, author, subject)
    - File associations for each commit
    - last_sha for incremental updates

    Usage:
        cache = CommitCache("/path/to/.shannon")
        if cache.last_sha:
            # Incremental: only fetch commits since last_sha
            new_commits = extractor.extract_since(cache.last_sha)
            cache.store_commits(new_commits)
        else:
            # Cold start: fetch all and store
            commits = extractor.extract()
            cache.store_commits(commits)
            cache.set_last_sha(commits[0].hash if commits else None)
    """

    def __init__(self, shannon_dir: str | Path):
        """Initialize cache with .shannon directory path.

        Args:
            shannon_dir: Path to .shannon directory (created if needed)
        """
        self._shannon_dir = Path(shannon_dir)
        self._shannon_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._shannon_dir / "commit_cache.db"
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.row_factory = sqlite3.Row

        # Create tables if not exists
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS cache_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS commits (
                sha TEXT PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                author TEXT NOT NULL,
                subject TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS commit_files (
                sha TEXT NOT NULL,
                file_path TEXT NOT NULL,
                PRIMARY KEY (sha, file_path),
                FOREIGN KEY (sha) REFERENCES commits(sha)
            );

            CREATE INDEX IF NOT EXISTS idx_commit_files_sha ON commit_files(sha);
            CREATE INDEX IF NOT EXISTS idx_commits_timestamp ON commits(timestamp);
            """
        )

        # Check/set schema version
        version = self._get_meta("schema_version")
        if version is None:
            self._set_meta("schema_version", str(_SCHEMA_VERSION))
        elif int(version) != _SCHEMA_VERSION:
            logger.warning(
                f"Cache schema version mismatch: {version} vs {_SCHEMA_VERSION}. Clearing cache."
            )
            self.clear()

        self._conn.commit()

    def _get_meta(self, key: str) -> str | None:
        """Get metadata value."""
        if self._conn is None:
            return None
        row = self._conn.execute("SELECT value FROM cache_meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def _set_meta(self, key: str, value: str | None) -> None:
        """Set metadata value."""
        if self._conn is None:
            return
        if value is None:
            self._conn.execute("DELETE FROM cache_meta WHERE key = ?", (key,))
        else:
            self._conn.execute(
                "INSERT OR REPLACE INTO cache_meta (key, value) VALUES (?, ?)",
                (key, value),
            )
        self._conn.commit()

    @property
    def last_sha(self) -> str | None:
        """Get SHA of last cached commit (most recent)."""
        return self._get_meta("last_sha")

    def set_last_sha(self, sha: str | None) -> None:
        """Set SHA of last cached commit."""
        self._set_meta("last_sha", sha)

    def store_commits(self, commits: list[Commit]) -> int:
        """Store commits in cache.

        Args:
            commits: List of Commit objects to store

        Returns:
            Number of new commits added (excludes duplicates)
        """
        if self._conn is None or not commits:
            return 0

        added = 0
        for commit in commits:
            # Skip if already cached
            existing = self._conn.execute(
                "SELECT sha FROM commits WHERE sha = ?", (commit.hash,)
            ).fetchone()
            if existing:
                continue

            # Insert commit
            self._conn.execute(
                "INSERT INTO commits (sha, timestamp, author, subject) VALUES (?, ?, ?, ?)",
                (commit.hash, commit.timestamp, commit.author, commit.subject),
            )

            # Insert file associations
            for file_path in commit.files:
                self._conn.execute(
                    "INSERT INTO commit_files (sha, file_path) VALUES (?, ?)",
                    (commit.hash, file_path),
                )

            added += 1

        self._conn.commit()

        if added > 0:
            logger.debug(f"Cached {added} new commits")

        return added

    def get_all_commits(self) -> list[Commit]:
        """Get all cached commits, newest first.

        Returns:
            List of Commit objects sorted by timestamp descending
        """
        if self._conn is None:
            return []

        commits = []
        rows = self._conn.execute(
            "SELECT sha, timestamp, author, subject FROM commits ORDER BY timestamp DESC"
        ).fetchall()

        for row in rows:
            # Get files for this commit
            files = [
                f["file_path"]
                for f in self._conn.execute(
                    "SELECT file_path FROM commit_files WHERE sha = ?", (row["sha"],)
                ).fetchall()
            ]
            commits.append(
                Commit(
                    hash=row["sha"],
                    timestamp=row["timestamp"],
                    author=row["author"],
                    subject=row["subject"],
                    files=files,
                )
            )

        return commits

    def get_commits_since(self, sha: str) -> list[Commit]:
        """Get commits newer than the given SHA.

        Args:
            sha: SHA to start from (exclusive)

        Returns:
            List of commits newer than sha, newest first
        """
        if self._conn is None:
            return []

        # Get timestamp of the reference commit
        ref = self._conn.execute("SELECT timestamp FROM commits WHERE sha = ?", (sha,)).fetchone()
        if not ref:
            return []

        return [c for c in self.get_all_commits() if c.timestamp > ref["timestamp"]]

    def is_cached(self, sha: str) -> bool:
        """Check if a commit SHA is already cached."""
        if self._conn is None:
            return False
        row = self._conn.execute("SELECT sha FROM commits WHERE sha = ?", (sha,)).fetchone()
        return row is not None

    def commit_count(self) -> int:
        """Get number of cached commits."""
        if self._conn is None:
            return 0
        row = self._conn.execute("SELECT COUNT(*) as cnt FROM commits").fetchone()
        return row["cnt"] if row else 0

    def clear(self) -> None:
        """Clear all cached data."""
        if self._conn is None:
            return
        self._conn.executescript(
            """
            DELETE FROM commit_files;
            DELETE FROM commits;
            DELETE FROM cache_meta;
            """
        )
        self._conn.commit()
        self._set_meta("schema_version", str(_SCHEMA_VERSION))
        logger.debug("Cleared commit cache")

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> CommitCache:
        return self

    def __exit__(self, *args) -> None:
        self.close()
