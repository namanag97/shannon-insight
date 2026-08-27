"""Git facts database for raw commit/file-change storage.

Stores raw git data enabling:
1. Incremental updates (fetch only new commits)
2. Rich temporal queries (churn, authorship, co-change)
3. Line-level statistics (additions/deletions per file)
4. Rename tracking across history

Usage:
    db = GitFactDatabase(".shannon/git_facts.db")
    session = GitExtractionSession(...)
    db.create_session(session)
    db.store_commits_batch(commits, session.id)
    db.store_file_changes_batch(changes)
    db.complete_session(session.id, commit_count, change_count)

Query examples:
    db.get_file_churn("src/main.py", since_days=90)
    db.get_file_authors("src/main.py")
    db.get_cochange_pairs(min_cochanges=3)
"""

from __future__ import annotations

import json
import logging
import sqlite3
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .git_models import (
    ChangeType,
    GitCommit,
    GitExtractionSession,
    GitFileChange,
)

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

# Schema SQL - designed for fast temporal queries
SCHEMA = """
-- Schema version tracking
CREATE TABLE IF NOT EXISTS git_schema_info (
    version INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL
);

-- Extraction session tracking (enables incremental updates)
CREATE TABLE IF NOT EXISTS git_extraction_sessions (
    id TEXT PRIMARY KEY,
    repo_path TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    head_sha TEXT NOT NULL,
    oldest_sha TEXT,
    commit_count INTEGER DEFAULT 0,
    file_change_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',
    error_message TEXT
);

-- Raw commits (one row per commit)
CREATE TABLE IF NOT EXISTS git_commits (
    hash TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    author_email TEXT NOT NULL,
    author_name TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT DEFAULT '',
    parent_hashes TEXT NOT NULL,
    is_merge INTEGER NOT NULL,
    extraction_session_id TEXT NOT NULL
);

-- File changes (one row per file per commit)
-- This is the workhorse table for churn/co-change queries
CREATE TABLE IF NOT EXISTS git_file_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_hash TEXT NOT NULL,
    file_path TEXT NOT NULL,
    additions INTEGER,
    deletions INTEGER,
    change_type TEXT NOT NULL,
    old_path TEXT,
    UNIQUE(commit_hash, file_path)
);

-- === INDEXES FOR BLAZING SPEED ===

-- Commit queries by time range
CREATE INDEX IF NOT EXISTS idx_commits_timestamp ON git_commits(timestamp);

-- Author queries
CREATE INDEX IF NOT EXISTS idx_commits_author ON git_commits(author_email);

-- Session linkage
CREATE INDEX IF NOT EXISTS idx_commits_session ON git_commits(extraction_session_id);

-- File change lookups by commit
CREATE INDEX IF NOT EXISTS idx_file_changes_commit ON git_file_changes(commit_hash);

-- File history (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_file_changes_path ON git_file_changes(file_path);

-- Change type filtering (e.g., find all renames)
CREATE INDEX IF NOT EXISTS idx_file_changes_type ON git_file_changes(change_type);

-- Covering index for churn queries: get timestamp + changes for a file
-- This allows churn computation without touching git_commits table
CREATE INDEX IF NOT EXISTS idx_file_changes_path_commit
    ON git_file_changes(file_path, commit_hash);

-- Covering index for co-change: files in same commit
CREATE INDEX IF NOT EXISTS idx_file_changes_commit_path
    ON git_file_changes(commit_hash, file_path);
"""


class GitFactDatabase:
    """SQLite database for storing raw git facts.

    Thread-safe for concurrent reads, single writer.
    Uses WAL mode for good read/write concurrency.
    """

    def __init__(self, db_path: str | Path) -> None:
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema if needed."""
        with self._connect() as conn:
            conn.executescript(SCHEMA)

            # Check/set schema version
            cursor = conn.execute(
                "SELECT version FROM git_schema_info ORDER BY version DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO git_schema_info (version, created_at) VALUES (?, ?)",
                    (SCHEMA_VERSION, datetime.now(timezone.utc).isoformat()),
                )
            elif row[0] < SCHEMA_VERSION:
                logger.warning(
                    f"Git database schema version {row[0]} < {SCHEMA_VERSION}, migrations needed"
                )

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connection."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")  # Faster, still safe with WAL
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── Session Management ─────────────────────────────────────────────

    def create_session(self, session: GitExtractionSession) -> None:
        """Create a new extraction session."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO git_extraction_sessions
                (id, repo_path, started_at, completed_at, head_sha, oldest_sha,
                 commit_count, file_change_count, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.repo_path,
                    session.started_at.isoformat(),
                    session.completed_at.isoformat() if session.completed_at else None,
                    session.head_sha,
                    session.oldest_sha,
                    session.commit_count,
                    session.file_change_count,
                    session.status,
                    session.error_message,
                ),
            )

    def complete_session(
        self,
        session_id: str,
        commit_count: int,
        file_change_count: int,
        error_message: str | None = None,
    ) -> None:
        """Mark a session as completed."""
        status = "failed" if error_message else "completed"
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE git_extraction_sessions
                SET completed_at = ?, status = ?, commit_count = ?,
                    file_change_count = ?, error_message = ?
                WHERE id = ?
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    status,
                    commit_count,
                    file_change_count,
                    error_message,
                    session_id,
                ),
            )

    def get_latest_session(self, repo_path: str) -> GitExtractionSession | None:
        """Get the most recent successful session for a repo.

        Used for incremental updates: start from last head_sha.
        """
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM git_extraction_sessions
                WHERE repo_path = ? AND status = 'completed'
                ORDER BY completed_at DESC
                LIMIT 1
                """,
                (repo_path,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_session(row)

    def _row_to_session(self, row: sqlite3.Row) -> GitExtractionSession:
        """Convert a database row to GitExtractionSession."""
        return GitExtractionSession(
            id=row["id"],
            repo_path=row["repo_path"],
            started_at=datetime.fromisoformat(row["started_at"]),
            completed_at=(
                datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
            ),
            head_sha=row["head_sha"],
            oldest_sha=row["oldest_sha"],
            commit_count=row["commit_count"],
            file_change_count=row["file_change_count"],
            status=row["status"],
            error_message=row["error_message"],
        )

    # ── Batch Storage (FAST) ───────────────────────────────────────────

    def store_commits_batch(self, commits: list[GitCommit], session_id: str) -> int:
        """Store commits in batch using executemany.

        Returns number of commits stored.
        """
        if not commits:
            return 0

        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO git_commits
                (hash, timestamp, author_email, author_name, subject, body,
                 parent_hashes, is_merge, extraction_session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        c.hash,
                        c.timestamp,
                        c.author_email,
                        c.author_name,
                        c.subject,
                        c.body,
                        json.dumps(list(c.parent_hashes)),
                        1 if c.is_merge else 0,
                        session_id,
                    )
                    for c in commits
                ],
            )
            return conn.total_changes

    def store_file_changes_batch(self, changes: list[GitFileChange]) -> int:
        """Store file changes in batch using executemany.

        Returns number of changes stored.
        """
        if not changes:
            return 0

        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO git_file_changes
                (commit_hash, file_path, additions, deletions, change_type, old_path)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        c.commit_hash,
                        c.file_path,
                        c.additions,
                        c.deletions,
                        c.change_type.value,
                        c.old_path,
                    )
                    for c in changes
                ],
            )
            return conn.total_changes

    # ── Query Methods (BLAZING FAST) ───────────────────────────────────

    def get_file_churn(
        self,
        file_path: str,
        since_timestamp: int | None = None,
    ) -> dict[str, int | float]:
        """Get churn statistics for a file.

        Args:
            file_path: Relative file path
            since_timestamp: Unix timestamp to filter from (optional)

        Returns:
            Dict with: change_count, additions, deletions, churn
        """
        with self._connect() as conn:
            if since_timestamp:
                cursor = conn.execute(
                    """
                    SELECT
                        COUNT(*) as change_count,
                        COALESCE(SUM(fc.additions), 0) as additions,
                        COALESCE(SUM(fc.deletions), 0) as deletions
                    FROM git_file_changes fc
                    JOIN git_commits c ON fc.commit_hash = c.hash
                    WHERE fc.file_path = ? AND c.timestamp >= ?
                    """,
                    (file_path, since_timestamp),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT
                        COUNT(*) as change_count,
                        COALESCE(SUM(additions), 0) as additions,
                        COALESCE(SUM(deletions), 0) as deletions
                    FROM git_file_changes
                    WHERE file_path = ?
                    """,
                    (file_path,),
                )
            row = cursor.fetchone()
            return {
                "change_count": row["change_count"],
                "additions": row["additions"],
                "deletions": row["deletions"],
                "churn": row["additions"] + row["deletions"],
            }

    def get_file_authors(
        self,
        file_path: str,
        since_timestamp: int | None = None,
    ) -> list[tuple[str, str, int]]:
        """Get authors who changed a file, ordered by commit count.

        Returns:
            List of (email, name, commit_count) tuples
        """
        with self._connect() as conn:
            if since_timestamp:
                cursor = conn.execute(
                    """
                    SELECT c.author_email, c.author_name, COUNT(*) as commits
                    FROM git_commits c
                    JOIN git_file_changes fc ON c.hash = fc.commit_hash
                    WHERE fc.file_path = ? AND c.timestamp >= ?
                    GROUP BY c.author_email, c.author_name
                    ORDER BY commits DESC
                    """,
                    (file_path, since_timestamp),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT c.author_email, c.author_name, COUNT(*) as commits
                    FROM git_commits c
                    JOIN git_file_changes fc ON c.hash = fc.commit_hash
                    WHERE fc.file_path = ?
                    GROUP BY c.author_email, c.author_name
                    ORDER BY commits DESC
                    """,
                    (file_path,),
                )
            return [(r["author_email"], r["author_name"], r["commits"]) for r in cursor]

    def get_file_changes_in_range(
        self,
        file_paths: set[str],
        since_timestamp: int,
        until_timestamp: int | None = None,
    ) -> Iterator[tuple[str, int, str]]:
        """Get (file_path, timestamp, author_email) for files in time range.

        Streaming iterator for memory efficiency on large histories.
        """
        with self._connect() as conn:
            if until_timestamp:
                cursor = conn.execute(
                    """
                    SELECT fc.file_path, c.timestamp, c.author_email
                    FROM git_file_changes fc
                    JOIN git_commits c ON fc.commit_hash = c.hash
                    WHERE c.timestamp >= ? AND c.timestamp <= ?
                    ORDER BY c.timestamp
                    """,
                    (since_timestamp, until_timestamp),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT fc.file_path, c.timestamp, c.author_email
                    FROM git_file_changes fc
                    JOIN git_commits c ON fc.commit_hash = c.hash
                    WHERE c.timestamp >= ?
                    ORDER BY c.timestamp
                    """,
                    (since_timestamp,),
                )
            for row in cursor:
                if row["file_path"] in file_paths:
                    yield (row["file_path"], row["timestamp"], row["author_email"])

    def get_cochange_pairs(
        self,
        min_cochanges: int = 3,
        max_files_per_commit: int = 30,
        since_timestamp: int | None = None,
    ) -> list[tuple[str, str, int]]:
        """Get file pairs that changed together.

        Uses self-join on git_file_changes for efficiency.

        Args:
            min_cochanges: Minimum co-change count to include
            max_files_per_commit: Skip commits with more files (bulk reformats)
            since_timestamp: Only consider commits after this time

        Returns:
            List of (file_a, file_b, cochange_count) sorted by count desc
        """
        with self._connect() as conn:
            # First, get commits with <= max_files_per_commit files
            if since_timestamp:
                cursor = conn.execute(
                    """
                    WITH valid_commits AS (
                        SELECT commit_hash
                        FROM git_file_changes
                        GROUP BY commit_hash
                        HAVING COUNT(*) <= ?
                    ),
                    filtered_changes AS (
                        SELECT fc.commit_hash, fc.file_path
                        FROM git_file_changes fc
                        JOIN git_commits c ON fc.commit_hash = c.hash
                        JOIN valid_commits vc ON fc.commit_hash = vc.commit_hash
                        WHERE c.timestamp >= ?
                    )
                    SELECT a.file_path as file_a, b.file_path as file_b, COUNT(*) as cochanges
                    FROM filtered_changes a
                    JOIN filtered_changes b ON a.commit_hash = b.commit_hash
                        AND a.file_path < b.file_path
                    GROUP BY a.file_path, b.file_path
                    HAVING cochanges >= ?
                    ORDER BY cochanges DESC
                    """,
                    (max_files_per_commit, since_timestamp, min_cochanges),
                )
            else:
                cursor = conn.execute(
                    """
                    WITH valid_commits AS (
                        SELECT commit_hash
                        FROM git_file_changes
                        GROUP BY commit_hash
                        HAVING COUNT(*) <= ?
                    )
                    SELECT a.file_path as file_a, b.file_path as file_b, COUNT(*) as cochanges
                    FROM git_file_changes a
                    JOIN git_file_changes b ON a.commit_hash = b.commit_hash
                        AND a.file_path < b.file_path
                    JOIN valid_commits vc ON a.commit_hash = vc.commit_hash
                    GROUP BY a.file_path, b.file_path
                    HAVING cochanges >= ?
                    ORDER BY cochanges DESC
                    """,
                    (max_files_per_commit, min_cochanges),
                )
            return [(r["file_a"], r["file_b"], r["cochanges"]) for r in cursor]

    def get_file_age_and_recency(self, file_paths: set[str]) -> dict[str, tuple[int, int, int]]:
        """Get age/recency stats for files.

        Returns:
            Dict mapping file_path -> (first_change_ts, last_change_ts, age_days)
        """
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT
                    fc.file_path,
                    MIN(c.timestamp) as first_change,
                    MAX(c.timestamp) as last_change
                FROM git_file_changes fc
                JOIN git_commits c ON fc.commit_hash = c.hash
                GROUP BY fc.file_path
                """,
            )
            result = {}
            for row in cursor:
                path = row["file_path"]
                if path in file_paths:
                    first_ts = row["first_change"]
                    last_ts = row["last_change"]
                    age_days = (last_ts - first_ts) // 86400
                    result[path] = (first_ts, last_ts, age_days)
            return result

    def get_commits_touching_files(
        self,
        file_paths: set[str],
        since_timestamp: int | None = None,
    ) -> list[GitCommit]:
        """Get all commits that touched any of the given files.

        Returns commits in timestamp descending order (newest first).
        """
        with self._connect() as conn:
            placeholders = ",".join("?" * len(file_paths))
            if since_timestamp:
                cursor = conn.execute(
                    f"""
                    SELECT DISTINCT c.*
                    FROM git_commits c
                    JOIN git_file_changes fc ON c.hash = fc.commit_hash
                    WHERE fc.file_path IN ({placeholders}) AND c.timestamp >= ?
                    ORDER BY c.timestamp DESC
                    """,
                    (*file_paths, since_timestamp),
                )
            else:
                cursor = conn.execute(
                    f"""
                    SELECT DISTINCT c.*
                    FROM git_commits c
                    JOIN git_file_changes fc ON c.hash = fc.commit_hash
                    WHERE fc.file_path IN ({placeholders})
                    ORDER BY c.timestamp DESC
                    """,
                    tuple(file_paths),
                )
            return [self._row_to_commit(r) for r in cursor]

    def get_all_file_changes(self, since_timestamp: int | None = None) -> Iterator[GitFileChange]:
        """Stream all file changes for bulk processing.

        Memory-efficient iterator for building churn series.
        """
        with self._connect() as conn:
            if since_timestamp:
                cursor = conn.execute(
                    """
                    SELECT fc.*, c.timestamp
                    FROM git_file_changes fc
                    JOIN git_commits c ON fc.commit_hash = c.hash
                    WHERE c.timestamp >= ?
                    ORDER BY c.timestamp
                    """,
                    (since_timestamp,),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT fc.*, c.timestamp
                    FROM git_file_changes fc
                    JOIN git_commits c ON fc.commit_hash = c.hash
                    ORDER BY c.timestamp
                    """,
                )
            for row in cursor:
                yield self._row_to_file_change(row)

    def get_renames(self, since_timestamp: int | None = None) -> list[tuple[str, str, int]]:
        """Get all rename operations.

        Returns:
            List of (old_path, new_path, timestamp) sorted by time
        """
        with self._connect() as conn:
            if since_timestamp:
                cursor = conn.execute(
                    """
                    SELECT fc.old_path, fc.file_path as new_path, c.timestamp
                    FROM git_file_changes fc
                    JOIN git_commits c ON fc.commit_hash = c.hash
                    WHERE fc.change_type = 'R' AND fc.old_path IS NOT NULL
                        AND c.timestamp >= ?
                    ORDER BY c.timestamp
                    """,
                    (since_timestamp,),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT fc.old_path, fc.file_path as new_path, c.timestamp
                    FROM git_file_changes fc
                    JOIN git_commits c ON fc.commit_hash = c.hash
                    WHERE fc.change_type = 'R' AND fc.old_path IS NOT NULL
                    ORDER BY c.timestamp
                    """,
                )
            return [(r["old_path"], r["new_path"], r["timestamp"]) for r in cursor]

    def _row_to_commit(self, row: sqlite3.Row) -> GitCommit:
        """Convert database row to GitCommit."""
        parent_hashes = json.loads(row["parent_hashes"]) if row["parent_hashes"] else []
        return GitCommit(
            hash=row["hash"],
            timestamp=row["timestamp"],
            author_email=row["author_email"],
            author_name=row["author_name"],
            subject=row["subject"],
            body=row["body"] or "",
            parent_hashes=tuple(parent_hashes),
        )

    def _row_to_file_change(self, row: sqlite3.Row) -> GitFileChange:
        """Convert database row to GitFileChange."""
        return GitFileChange(
            commit_hash=row["commit_hash"],
            file_path=row["file_path"],
            additions=row["additions"],
            deletions=row["deletions"],
            change_type=ChangeType(row["change_type"]),
            old_path=row["old_path"],
        )

    # ── Statistics ─────────────────────────────────────────────────────

    def get_stats(self) -> dict[str, int]:
        """Get database statistics."""
        with self._connect() as conn:
            stats = {}

            cursor = conn.execute("SELECT COUNT(*) FROM git_commits")
            stats["commit_count"] = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM git_file_changes")
            stats["file_change_count"] = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(DISTINCT file_path) FROM git_file_changes")
            stats["unique_files"] = cursor.fetchone()[0]

            cursor = conn.execute(
                "SELECT COUNT(*) FROM git_extraction_sessions WHERE status = 'completed'"
            )
            stats["completed_sessions"] = cursor.fetchone()[0]

            return stats

    def get_timestamp_range(self) -> tuple[int, int] | None:
        """Get (oldest_timestamp, newest_timestamp) from commits."""
        with self._connect() as conn:
            cursor = conn.execute("SELECT MIN(timestamp), MAX(timestamp) FROM git_commits")
            row = cursor.fetchone()
            if row[0] is None:
                return None
            return (row[0], row[1])


__all__ = ["GitFactDatabase", "SCHEMA_VERSION"]
