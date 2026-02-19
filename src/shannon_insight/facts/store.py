"""Unified Fact Store.

Central API for storing and querying all codebase facts.
Integrates content-addressable storage, file identity resolution,
and structured fact storage in a single SQLite database.

Usage:
    store = FactStore.open("/path/to/facts.db")

    # Store facts
    content_hash = store.store_content(b"file content")
    store.store_commit(commit_hash="abc123", timestamp=1700000000,
                       author_email="dev@example.com", author_name="Dev")
    store.store_file_change(commit_hash="abc123", file_id="f1",
                            change_type="M", new_path="src/main.py")

    # Query
    syntax = store.get_parsed_syntax(content_hash)
    commits = list(store.get_commits_in_range(since=1690000000))

    # Context manager
    with FactStore.open("/path/to/facts.db") as store:
        store.store_commit(...)
        # auto-commits on clean exit, rolls back on exception
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import time
import zlib
from pathlib import Path
from collections.abc import Iterator
from typing import Any

from .models import (
    CommitFact,
    ExtractedClass,
    ExtractedFunction,
    ExtractedImport,
    FileChangeFact,
    ParsedSyntaxFact,
)

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

# =========================================================================
# Schema DDL
# =========================================================================

_SCHEMA_SQL = """
-- Schema version tracking
CREATE TABLE IF NOT EXISTS fact_schema_info (
    version     INTEGER PRIMARY KEY,
    created_at  TEXT NOT NULL
);

-- =====================================================================
-- Content-Addressable Blob Storage
-- =====================================================================
CREATE TABLE IF NOT EXISTS blobs (
    content_hash TEXT PRIMARY KEY,
    data         BLOB NOT NULL,
    size_bytes   INTEGER NOT NULL
);

-- =====================================================================
-- File Identity (stable across renames)
-- =====================================================================
CREATE TABLE IF NOT EXISTS file_identities (
    file_id      TEXT PRIMARY KEY,
    birth_commit TEXT NOT NULL,
    birth_path   TEXT NOT NULL,
    current_path TEXT,
    is_alive     INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_file_identities_current_path
    ON file_identities(current_path);

-- Path-to-ID mapping at historical points (for resolve_file_id_at)
CREATE TABLE IF NOT EXISTS file_path_history (
    file_id   TEXT    NOT NULL REFERENCES file_identities(file_id),
    path      TEXT    NOT NULL,
    timestamp INTEGER NOT NULL,
    PRIMARY KEY (file_id, path, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_file_path_history_path
    ON file_path_history(path, timestamp);

-- =====================================================================
-- Commits
-- =====================================================================
CREATE TABLE IF NOT EXISTS commits (
    commit_hash    TEXT PRIMARY KEY,
    timestamp      INTEGER NOT NULL,
    author_email   TEXT    NOT NULL,
    author_name    TEXT    NOT NULL,
    message_subject TEXT   NOT NULL,
    message_body   TEXT,
    parent_hashes  TEXT    NOT NULL DEFAULT '[]',
    is_merge       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_commits_timestamp
    ON commits(timestamp);

CREATE INDEX IF NOT EXISTS idx_commits_author
    ON commits(author_email);

-- =====================================================================
-- File Changes (one per file per commit)
-- =====================================================================
CREATE TABLE IF NOT EXISTS file_changes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_hash TEXT    NOT NULL,
    file_id     TEXT    NOT NULL,
    change_type TEXT    NOT NULL,
    old_path    TEXT,
    new_path    TEXT,
    additions   INTEGER,
    deletions   INTEGER,
    UNIQUE(commit_hash, file_id)
);

CREATE INDEX IF NOT EXISTS idx_file_changes_commit
    ON file_changes(commit_hash);

CREATE INDEX IF NOT EXISTS idx_file_changes_file_id
    ON file_changes(file_id);

-- =====================================================================
-- File Observations (file state at a commit)
-- =====================================================================
CREATE TABLE IF NOT EXISTS file_observations (
    file_id      TEXT    NOT NULL,
    commit_hash  TEXT    NOT NULL,
    path         TEXT    NOT NULL,
    content_hash TEXT    NOT NULL,
    timestamp    INTEGER NOT NULL,
    PRIMARY KEY (file_id, commit_hash)
);

CREATE INDEX IF NOT EXISTS idx_file_observations_content
    ON file_observations(content_hash);

CREATE INDEX IF NOT EXISTS idx_file_observations_timestamp
    ON file_observations(timestamp);

-- =====================================================================
-- Parsed Syntax Cache (keyed by content_hash -- pure function of bytes)
-- =====================================================================
CREATE TABLE IF NOT EXISTS parsed_syntax (
    content_hash   TEXT PRIMARY KEY,
    language       TEXT    NOT NULL,
    lines          INTEGER NOT NULL,
    tokens         INTEGER,
    complexity     INTEGER,
    max_nesting    INTEGER,
    has_main_guard INTEGER NOT NULL DEFAULT 0,
    stub_ratio     REAL,
    parser_type    TEXT    NOT NULL DEFAULT 'regex',
    tool_version   TEXT    NOT NULL DEFAULT 'unknown'
);

-- =====================================================================
-- Extracted Functions
-- =====================================================================
CREATE TABLE IF NOT EXISTS extracted_functions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash   TEXT    NOT NULL,
    name           TEXT    NOT NULL,
    qualified_name TEXT    NOT NULL,
    start_line     INTEGER NOT NULL,
    end_line       INTEGER NOT NULL,
    params         TEXT    NOT NULL DEFAULT '[]',
    decorators     TEXT    NOT NULL DEFAULT '[]',
    body_tokens    INTEGER NOT NULL DEFAULT 0,
    nesting_depth  INTEGER NOT NULL DEFAULT 0,
    is_stub        INTEGER NOT NULL DEFAULT 0,
    class_name     TEXT
);

CREATE INDEX IF NOT EXISTS idx_extracted_functions_content
    ON extracted_functions(content_hash);

-- =====================================================================
-- Extracted Classes
-- =====================================================================
CREATE TABLE IF NOT EXISTS extracted_classes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT    NOT NULL,
    name         TEXT    NOT NULL,
    start_line   INTEGER NOT NULL DEFAULT 0,
    end_line     INTEGER NOT NULL DEFAULT 0,
    bases        TEXT    NOT NULL DEFAULT '[]',
    method_names TEXT    NOT NULL DEFAULT '[]',
    field_names  TEXT    NOT NULL DEFAULT '[]',
    is_abstract  INTEGER NOT NULL DEFAULT 0,
    method_count INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_extracted_classes_content
    ON extracted_classes(content_hash);

-- =====================================================================
-- Extracted Imports
-- =====================================================================
CREATE TABLE IF NOT EXISTS extracted_imports (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash  TEXT NOT NULL,
    raw_statement TEXT NOT NULL,
    source_module TEXT NOT NULL,
    names         TEXT NOT NULL DEFAULT '[]',
    is_relative   INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_extracted_imports_content
    ON extracted_imports(content_hash);

-- =====================================================================
-- Resolved Imports (edges in the dependency graph)
-- =====================================================================
CREATE TABLE IF NOT EXISTS resolved_imports (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    source_content_hash TEXT NOT NULL,
    source_file_id      TEXT NOT NULL,
    target_file_id      TEXT,
    target_module       TEXT NOT NULL,
    is_stdlib           INTEGER NOT NULL DEFAULT 0,
    is_phantom          INTEGER NOT NULL DEFAULT 0,
    UNIQUE(source_content_hash, source_file_id, target_module)
);

CREATE INDEX IF NOT EXISTS idx_resolved_imports_source
    ON resolved_imports(source_file_id);

CREATE INDEX IF NOT EXISTS idx_resolved_imports_target
    ON resolved_imports(target_file_id);

-- =====================================================================
-- Extraction Sessions
-- =====================================================================
CREATE TABLE IF NOT EXISTS extraction_sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at    REAL    NOT NULL,
    completed_at  REAL,
    head_commit   TEXT,
    file_count    INTEGER DEFAULT 0,
    commit_count  INTEGER DEFAULT 0,
    status        TEXT    NOT NULL DEFAULT 'running'
);
"""


def _create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes idempotently."""
    conn.executescript(_SCHEMA_SQL)

    # Check / set schema version
    cursor = conn.execute(
        "SELECT version FROM fact_schema_info ORDER BY version DESC LIMIT 1"
    )
    row = cursor.fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO fact_schema_info (version, created_at) VALUES (?, datetime('now'))",
            (SCHEMA_VERSION,),
        )
    elif row[0] < SCHEMA_VERSION:
        logger.warning(
            "FactStore schema version %d < %d, migrations needed",
            row[0],
            SCHEMA_VERSION,
        )
    conn.commit()


# =========================================================================
# FactStore
# =========================================================================


class FactStore:
    """Unified storage for all codebase facts.

    Integrates:
    - Content-addressable blob storage (SHA-256 keyed, zlib compressed)
    - File identity resolution (stable IDs across renames)
    - Structured fact storage (commits, changes, syntax, entities)

    Usage::

        store = FactStore.open("/path/to/facts.db")

        # Store content
        content_hash = store.store_content(b"hello world")

        # Store commit
        store.store_commit(
            commit_hash="abc123",
            timestamp=1700000000,
            author_email="dev@example.com",
            author_name="Dev",
            message_subject="Initial commit",
        )

        # Context manager
        with FactStore.open("/path/to/facts.db") as s:
            s.store_commit(...)
            # auto-commits on clean exit
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        _create_schema(self.conn)

    @classmethod
    def open(cls, path: str | Path) -> FactStore:
        """Open or create a fact store at the given path.

        Args:
            path: Filesystem path for the SQLite database.

        Returns:
            A connected FactStore instance.
        """
        db_path = Path(path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        return cls(conn)

    @classmethod
    def in_memory(cls) -> FactStore:
        """Create an in-memory fact store (for testing).

        Returns:
            A connected FactStore backed by ``:memory:``.
        """
        conn = sqlite3.connect(":memory:")
        conn.execute("PRAGMA foreign_keys = ON")
        return cls(conn)

    # =====================================================================
    # Content Storage (content-addressable blobs)
    # =====================================================================

    def store_content(self, content: bytes) -> str:
        """Store file content, return its SHA-256 hash.

        Content is compressed with zlib before storage. Duplicate
        content (same hash) is silently ignored.

        Args:
            content: Raw file bytes.

        Returns:
            Hex-encoded SHA-256 hash of the content.
        """
        content_hash = hashlib.sha256(content).hexdigest()
        compressed = zlib.compress(content, level=6)
        self.conn.execute(
            "INSERT OR IGNORE INTO blobs (content_hash, data, size_bytes) VALUES (?, ?, ?)",
            (content_hash, compressed, len(content)),
        )
        return content_hash

    def get_content(self, content_hash: str) -> bytes | None:
        """Retrieve content by its SHA-256 hash.

        Args:
            content_hash: Hex-encoded SHA-256 hash.

        Returns:
            The original uncompressed bytes, or None if not found.
        """
        row = self.conn.execute(
            "SELECT data FROM blobs WHERE content_hash = ?",
            (content_hash,),
        ).fetchone()
        if row is None:
            return None
        return zlib.decompress(row["data"])

    def has_content(self, content_hash: str) -> bool:
        """Check if content exists in the blob store.

        Args:
            content_hash: Hex-encoded SHA-256 hash.

        Returns:
            True if the content is stored.
        """
        row = self.conn.execute(
            "SELECT 1 FROM blobs WHERE content_hash = ?",
            (content_hash,),
        ).fetchone()
        return row is not None

    # =====================================================================
    # Identity Resolution
    # =====================================================================

    def register_file_identity(
        self,
        file_id: str,
        birth_commit: str,
        birth_path: str,
        current_path: str | None = None,
        is_alive: bool = True,
    ) -> None:
        """Register a file identity.

        Args:
            file_id: Stable UUID for the file.
            birth_commit: Commit hash where the file was first seen.
            birth_path: Path at creation time.
            current_path: Current path (None if deleted).
            is_alive: Whether the file still exists.
        """
        self.conn.execute(
            """INSERT OR IGNORE INTO file_identities
               (file_id, birth_commit, birth_path, current_path, is_alive)
               VALUES (?, ?, ?, ?, ?)""",
            (file_id, birth_commit, birth_path, current_path or birth_path, int(is_alive)),
        )

    def update_file_path(
        self,
        file_id: str,
        new_path: str | None,
        timestamp: int,
        is_alive: bool = True,
    ) -> None:
        """Update the current path for a file (e.g., after rename or delete).

        Also records the path change in history for temporal queries.

        Args:
            file_id: Stable file UUID.
            new_path: New path, or None if the file is deleted.
            timestamp: Unix epoch seconds when the change happened.
            is_alive: Whether the file is still alive.
        """
        self.conn.execute(
            "UPDATE file_identities SET current_path = ?, is_alive = ? WHERE file_id = ?",
            (new_path, int(is_alive), file_id),
        )
        if new_path is not None:
            self.conn.execute(
                "INSERT OR IGNORE INTO file_path_history (file_id, path, timestamp) VALUES (?, ?, ?)",
                (file_id, new_path, timestamp),
            )

    def resolve_file_id(self, path: str) -> str | None:
        """Get the stable FileID for a current path.

        Args:
            path: Current file path.

        Returns:
            The file_id string, or None if no file is known at this path.
        """
        row = self.conn.execute(
            "SELECT file_id FROM file_identities WHERE current_path = ? AND is_alive = 1",
            (path,),
        ).fetchone()
        return row["file_id"] if row else None

    def resolve_file_id_at(self, path: str, timestamp: int) -> str | None:
        """Get the FileID for a path at a historical point in time.

        Finds the most recent path record at or before the given timestamp.

        Args:
            path: Historical file path.
            timestamp: Unix epoch seconds.

        Returns:
            The file_id string, or None.
        """
        row = self.conn.execute(
            """SELECT file_id FROM file_path_history
               WHERE path = ? AND timestamp <= ?
               ORDER BY timestamp DESC LIMIT 1""",
            (path, timestamp),
        ).fetchone()
        return row["file_id"] if row else None

    def get_file_identity(self, file_id: str) -> dict[str, Any] | None:
        """Get the full identity record for a file.

        Args:
            file_id: Stable file UUID.

        Returns:
            Dict with file_id, birth_commit, birth_path, current_path,
            is_alive keys, or None if not found.
        """
        row = self.conn.execute(
            "SELECT * FROM file_identities WHERE file_id = ?",
            (file_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "file_id": row["file_id"],
            "birth_commit": row["birth_commit"],
            "birth_path": row["birth_path"],
            "current_path": row["current_path"],
            "is_alive": bool(row["is_alive"]),
        }

    # =====================================================================
    # Commit Facts
    # =====================================================================

    def store_commit(
        self,
        commit_hash: str,
        timestamp: int,
        author_email: str,
        author_name: str,
        message_subject: str,
        message_body: str | None = None,
        parent_hashes: list[str] | None = None,
        is_merge: bool = False,
    ) -> None:
        """Store a commit fact.

        Duplicate commits (same hash) are silently ignored.

        Args:
            commit_hash: Git commit SHA.
            timestamp: Unix epoch seconds.
            author_email: Author email.
            author_name: Author display name.
            message_subject: First line of commit message.
            message_body: Remaining commit message lines.
            parent_hashes: List of parent commit SHAs.
            is_merge: Whether this is a merge commit.
        """
        self.conn.execute(
            """INSERT OR IGNORE INTO commits
               (commit_hash, timestamp, author_email, author_name,
                message_subject, message_body, parent_hashes, is_merge)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                commit_hash,
                timestamp,
                author_email,
                author_name,
                message_subject,
                message_body,
                json.dumps(parent_hashes or []),
                int(is_merge),
            ),
        )

    def store_commit_fact(self, fact: CommitFact) -> None:
        """Store a CommitFact dataclass.

        Convenience wrapper around :meth:`store_commit`.

        Args:
            fact: The CommitFact to store.
        """
        self.store_commit(
            commit_hash=fact.commit_hash,
            timestamp=fact.timestamp,
            author_email=fact.author_email_raw,
            author_name=fact.author_name_raw,
            message_subject=fact.message_subject,
            message_body=fact.message_body,
            parent_hashes=list(fact.parent_hashes),
            is_merge=fact.is_merge,
        )

    def store_commits_batch(self, commits: list[CommitFact]) -> int:
        """Store multiple commits in a single batch operation.

        Args:
            commits: List of CommitFact dataclasses to store.

        Returns:
            Number of commits inserted (duplicates silently skipped).
        """
        if not commits:
            return 0
        self.conn.executemany(
            """INSERT OR IGNORE INTO commits
               (commit_hash, timestamp, author_email, author_name,
                message_subject, message_body, parent_hashes, is_merge)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    c.commit_hash,
                    c.timestamp,
                    c.author_email_raw,
                    c.author_name_raw,
                    c.message_subject,
                    c.message_body,
                    json.dumps(list(c.parent_hashes)),
                    int(c.is_merge),
                )
                for c in commits
            ],
        )
        return self.conn.total_changes

    def get_commit(self, commit_hash: str) -> dict[str, Any] | None:
        """Get a commit by its hash.

        Args:
            commit_hash: Git commit SHA.

        Returns:
            Dict with commit fields, or None if not found.
        """
        row = self.conn.execute(
            "SELECT * FROM commits WHERE commit_hash = ?",
            (commit_hash,),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_commit_dict(row)

    def get_commits_in_range(
        self,
        since: int | None = None,
        until: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Iterate commits in a time range, ordered by timestamp.

        Args:
            since: Minimum timestamp (inclusive). None means no lower bound.
            until: Maximum timestamp (inclusive). None means no upper bound.

        Yields:
            Dicts with commit fields.
        """
        if since is not None and until is not None:
            cursor = self.conn.execute(
                "SELECT * FROM commits WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp",
                (since, until),
            )
        elif since is not None:
            cursor = self.conn.execute(
                "SELECT * FROM commits WHERE timestamp >= ? ORDER BY timestamp",
                (since,),
            )
        elif until is not None:
            cursor = self.conn.execute(
                "SELECT * FROM commits WHERE timestamp <= ? ORDER BY timestamp",
                (until,),
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM commits ORDER BY timestamp",
            )
        for row in cursor:
            yield self._row_to_commit_dict(row)

    def _row_to_commit_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a commits row to a dict."""
        return {
            "commit_hash": row["commit_hash"],
            "timestamp": row["timestamp"],
            "author_email": row["author_email"],
            "author_name": row["author_name"],
            "message_subject": row["message_subject"],
            "message_body": row["message_body"],
            "parent_hashes": json.loads(row["parent_hashes"]),
            "is_merge": bool(row["is_merge"]),
        }

    # =====================================================================
    # File Change Facts
    # =====================================================================

    def store_file_change(
        self,
        commit_hash: str,
        file_id: str,
        change_type: str,
        old_path: str | None = None,
        new_path: str | None = None,
        additions: int | None = None,
        deletions: int | None = None,
    ) -> None:
        """Store a file change fact.

        Duplicate changes (same commit + file_id) are silently ignored.

        Args:
            commit_hash: Git commit SHA.
            file_id: Stable file UUID.
            change_type: One of A, M, D, R, C (git status codes).
            old_path: Previous path (for renames).
            new_path: New path.
            additions: Line additions (None for binary files).
            deletions: Line deletions (None for binary files).
        """
        self.conn.execute(
            """INSERT OR IGNORE INTO file_changes
               (commit_hash, file_id, change_type, old_path, new_path,
                additions, deletions)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (commit_hash, file_id, change_type, old_path, new_path, additions, deletions),
        )

    def store_file_change_fact(self, fact: FileChangeFact) -> None:
        """Store a FileChangeFact dataclass.

        Args:
            fact: The FileChangeFact to store.
        """
        self.store_file_change(
            commit_hash=fact.commit_hash,
            file_id=fact.file_id,
            change_type=fact.change_type.value,
            old_path=fact.old_path,
            new_path=fact.new_path,
            additions=fact.additions,
            deletions=fact.deletions,
        )

    def store_file_changes_batch(self, changes: list[FileChangeFact]) -> int:
        """Store multiple file changes in a single batch operation.

        Args:
            changes: List of FileChangeFact dataclasses.

        Returns:
            Number of changes inserted.
        """
        if not changes:
            return 0
        self.conn.executemany(
            """INSERT OR IGNORE INTO file_changes
               (commit_hash, file_id, change_type, old_path, new_path,
                additions, deletions)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    c.commit_hash,
                    c.file_id,
                    c.change_type.value,
                    c.old_path,
                    c.new_path,
                    c.additions,
                    c.deletions,
                )
                for c in changes
            ],
        )
        return self.conn.total_changes

    def get_changes_for_commit(self, commit_hash: str) -> list[dict[str, Any]]:
        """Get all file changes in a commit.

        Args:
            commit_hash: Git commit SHA.

        Returns:
            List of dicts with change fields.
        """
        cursor = self.conn.execute(
            "SELECT * FROM file_changes WHERE commit_hash = ?",
            (commit_hash,),
        )
        return [self._row_to_change_dict(row) for row in cursor]

    def get_changes_for_file(self, file_id: str) -> list[dict[str, Any]]:
        """Get all changes to a file across history.

        Args:
            file_id: Stable file UUID.

        Returns:
            List of dicts with change fields.
        """
        cursor = self.conn.execute(
            "SELECT * FROM file_changes WHERE file_id = ?",
            (file_id,),
        )
        return [self._row_to_change_dict(row) for row in cursor]

    def _row_to_change_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a file_changes row to a dict."""
        return {
            "commit_hash": row["commit_hash"],
            "file_id": row["file_id"],
            "change_type": row["change_type"],
            "old_path": row["old_path"],
            "new_path": row["new_path"],
            "additions": row["additions"],
            "deletions": row["deletions"],
        }

    # =====================================================================
    # File Observations
    # =====================================================================

    def store_file_observation(
        self,
        file_id: str,
        commit_hash: str,
        path: str,
        content_hash: str,
        timestamp: int,
    ) -> None:
        """Record that a file had certain content at a commit.

        Args:
            file_id: Stable file UUID.
            commit_hash: Git commit SHA.
            path: Path of the file at this commit.
            content_hash: SHA-256 of the file content.
            timestamp: Unix epoch seconds.
        """
        self.conn.execute(
            """INSERT OR IGNORE INTO file_observations
               (file_id, commit_hash, path, content_hash, timestamp)
               VALUES (?, ?, ?, ?, ?)""",
            (file_id, commit_hash, path, content_hash, timestamp),
        )

    def get_file_at_commit(self, file_id: str, commit_hash: str) -> dict[str, Any] | None:
        """Get file state at a specific commit.

        Args:
            file_id: Stable file UUID.
            commit_hash: Git commit SHA.

        Returns:
            Dict with file_id, commit_hash, path, content_hash,
            timestamp keys, or None.
        """
        row = self.conn.execute(
            "SELECT * FROM file_observations WHERE file_id = ? AND commit_hash = ?",
            (file_id, commit_hash),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_observation_dict(row)

    def get_current_files(self) -> Iterator[dict[str, Any]]:
        """Iterate all currently existing files.

        Returns the most recent observation for each living file identity.

        Yields:
            Dicts with file observation fields.
        """
        cursor = self.conn.execute(
            """SELECT fo.*
               FROM file_observations fo
               INNER JOIN (
                   SELECT file_id, MAX(timestamp) AS max_ts
                   FROM file_observations
                   GROUP BY file_id
               ) latest ON fo.file_id = latest.file_id AND fo.timestamp = latest.max_ts
               INNER JOIN file_identities fi ON fo.file_id = fi.file_id
               WHERE fi.is_alive = 1"""
        )
        for row in cursor:
            yield self._row_to_observation_dict(row)

    def _row_to_observation_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a file_observations row to a dict."""
        return {
            "file_id": row["file_id"],
            "commit_hash": row["commit_hash"],
            "path": row["path"],
            "content_hash": row["content_hash"],
            "timestamp": row["timestamp"],
        }

    # =====================================================================
    # Parsed Syntax Cache
    # =====================================================================

    def store_parsed_syntax(
        self,
        content_hash: str,
        language: str,
        lines: int,
        tokens: int | None = None,
        complexity: int | None = None,
        max_nesting: int | None = None,
        has_main_guard: bool = False,
        stub_ratio: float | None = None,
        parser_type: str = "regex",
        tool_version: str = "unknown",
    ) -> None:
        """Cache parsed syntax for a content hash.

        Since parsed syntax is a pure function of content, the same
        content_hash always produces the same result. Duplicates are
        silently ignored.

        Args:
            content_hash: SHA-256 of the file content.
            language: Detected programming language.
            lines: Line count.
            tokens: Token count (may be None).
            complexity: Cyclomatic complexity (may be None).
            max_nesting: Maximum nesting depth (may be None).
            has_main_guard: Whether file has ``if __name__ == "__main__"`` guard.
            stub_ratio: Ratio of stub functions (may be None).
            parser_type: ``"tree-sitter"`` or ``"regex"``.
            tool_version: Shannon version string.
        """
        self.conn.execute(
            """INSERT OR IGNORE INTO parsed_syntax
               (content_hash, language, lines, tokens, complexity,
                max_nesting, has_main_guard, stub_ratio,
                parser_type, tool_version)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                content_hash,
                language,
                lines,
                tokens,
                complexity,
                max_nesting,
                int(has_main_guard),
                stub_ratio,
                parser_type,
                tool_version,
            ),
        )

    def store_parsed_syntax_fact(self, fact: ParsedSyntaxFact) -> None:
        """Store a ParsedSyntaxFact dataclass.

        Args:
            fact: The ParsedSyntaxFact to store.
        """
        self.store_parsed_syntax(
            content_hash=fact.content_hash,
            language=fact.language,
            lines=fact.lines,
            tokens=fact.tokens,
            complexity=fact.complexity,
            max_nesting=fact.max_nesting,
            has_main_guard=fact.has_main_guard,
            stub_ratio=fact.stub_ratio,
            parser_type=fact.parser_type,
        )

    def get_parsed_syntax(self, content_hash: str) -> dict[str, Any] | None:
        """Get cached parsed syntax for a content hash.

        Args:
            content_hash: SHA-256 of the file content.

        Returns:
            Dict with syntax fields, or None if not cached.
        """
        row = self.conn.execute(
            "SELECT * FROM parsed_syntax WHERE content_hash = ?",
            (content_hash,),
        ).fetchone()
        if row is None:
            return None
        return {
            "content_hash": row["content_hash"],
            "language": row["language"],
            "lines": row["lines"],
            "tokens": row["tokens"],
            "complexity": row["complexity"],
            "max_nesting": row["max_nesting"],
            "has_main_guard": bool(row["has_main_guard"]),
            "stub_ratio": row["stub_ratio"],
            "parser_type": row["parser_type"],
            "tool_version": row["tool_version"],
        }

    def has_parsed_syntax(self, content_hash: str) -> bool:
        """Check if syntax is cached for this content hash.

        Args:
            content_hash: SHA-256 of the file content.

        Returns:
            True if a cached parse exists.
        """
        row = self.conn.execute(
            "SELECT 1 FROM parsed_syntax WHERE content_hash = ?",
            (content_hash,),
        ).fetchone()
        return row is not None

    # =====================================================================
    # Extracted Entities (functions, classes, imports)
    # =====================================================================

    def store_extracted_function(
        self,
        content_hash: str,
        name: str,
        qualified_name: str,
        start_line: int,
        end_line: int,
        **kwargs: Any,
    ) -> None:
        """Store an extracted function.

        Args:
            content_hash: SHA-256 of the source file content.
            name: Function name.
            qualified_name: Fully qualified name (e.g., ``ClassName.method``).
            start_line: Starting line number.
            end_line: Ending line number.
            **kwargs: Optional fields: params, decorators, body_tokens,
                      nesting_depth, is_stub, class_name.
        """
        self.conn.execute(
            """INSERT INTO extracted_functions
               (content_hash, name, qualified_name, start_line, end_line,
                params, decorators, body_tokens, nesting_depth, is_stub, class_name)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                content_hash,
                name,
                qualified_name,
                start_line,
                end_line,
                json.dumps(kwargs.get("params", [])),
                json.dumps(kwargs.get("decorators", [])),
                kwargs.get("body_tokens", 0),
                kwargs.get("nesting_depth", 0),
                int(kwargs.get("is_stub", False)),
                kwargs.get("class_name"),
            ),
        )

    def store_extracted_function_fact(self, fact: ExtractedFunction) -> None:
        """Store an ExtractedFunction dataclass.

        Args:
            fact: The ExtractedFunction to store.
        """
        self.store_extracted_function(
            content_hash=fact.content_hash,
            name=fact.name,
            qualified_name=fact.qualified_name,
            start_line=fact.start_line,
            end_line=fact.end_line,
            params=list(fact.params),
            decorators=list(fact.decorators),
            body_tokens=fact.body_tokens,
            nesting_depth=fact.nesting_depth,
            is_stub=fact.is_stub,
            class_name=fact.class_name,
        )

    def get_functions_for_content(self, content_hash: str) -> list[dict[str, Any]]:
        """Get all functions extracted from content.

        Args:
            content_hash: SHA-256 of the source file content.

        Returns:
            List of dicts with function fields.
        """
        cursor = self.conn.execute(
            "SELECT * FROM extracted_functions WHERE content_hash = ?",
            (content_hash,),
        )
        return [
            {
                "content_hash": row["content_hash"],
                "name": row["name"],
                "qualified_name": row["qualified_name"],
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "params": json.loads(row["params"]),
                "decorators": json.loads(row["decorators"]),
                "body_tokens": row["body_tokens"],
                "nesting_depth": row["nesting_depth"],
                "is_stub": bool(row["is_stub"]),
                "class_name": row["class_name"],
            }
            for row in cursor
        ]

    def store_extracted_class(
        self,
        content_hash: str,
        name: str,
        **kwargs: Any,
    ) -> None:
        """Store an extracted class.

        Args:
            content_hash: SHA-256 of the source file content.
            name: Class name.
            **kwargs: Optional fields: start_line, end_line, bases,
                      method_names, field_names, is_abstract, method_count.
        """
        self.conn.execute(
            """INSERT INTO extracted_classes
               (content_hash, name, start_line, end_line, bases,
                method_names, field_names, is_abstract, method_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                content_hash,
                name,
                kwargs.get("start_line", 0),
                kwargs.get("end_line", 0),
                json.dumps(kwargs.get("bases", [])),
                json.dumps(kwargs.get("method_names", [])),
                json.dumps(kwargs.get("field_names", [])),
                int(kwargs.get("is_abstract", False)),
                kwargs.get("method_count", 0),
            ),
        )

    def store_extracted_class_fact(self, fact: ExtractedClass) -> None:
        """Store an ExtractedClass dataclass.

        Args:
            fact: The ExtractedClass to store.
        """
        self.store_extracted_class(
            content_hash=fact.content_hash,
            name=fact.name,
            start_line=fact.start_line,
            end_line=fact.end_line,
            bases=list(fact.bases),
            method_names=list(fact.method_names),
            field_names=list(fact.field_names),
            is_abstract=fact.is_abstract,
            method_count=fact.method_count,
        )

    def get_classes_for_content(self, content_hash: str) -> list[dict[str, Any]]:
        """Get all classes extracted from content.

        Args:
            content_hash: SHA-256 of the source file content.

        Returns:
            List of dicts with class fields.
        """
        cursor = self.conn.execute(
            "SELECT * FROM extracted_classes WHERE content_hash = ?",
            (content_hash,),
        )
        return [
            {
                "content_hash": row["content_hash"],
                "name": row["name"],
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "bases": json.loads(row["bases"]),
                "method_names": json.loads(row["method_names"]),
                "field_names": json.loads(row["field_names"]),
                "is_abstract": bool(row["is_abstract"]),
                "method_count": row["method_count"],
            }
            for row in cursor
        ]

    def store_extracted_import(
        self,
        content_hash: str,
        raw_statement: str,
        source_module: str,
        **kwargs: Any,
    ) -> None:
        """Store an extracted import.

        Args:
            content_hash: SHA-256 of the source file content.
            raw_statement: The raw import statement text.
            source_module: Resolved module source (e.g., ``os.path``).
            **kwargs: Optional fields: names, is_relative.
        """
        self.conn.execute(
            """INSERT INTO extracted_imports
               (content_hash, raw_statement, source_module, names, is_relative)
               VALUES (?, ?, ?, ?, ?)""",
            (
                content_hash,
                raw_statement,
                source_module,
                json.dumps(kwargs.get("names", [])),
                int(kwargs.get("is_relative", False)),
            ),
        )

    def store_extracted_import_fact(self, fact: ExtractedImport) -> None:
        """Store an ExtractedImport dataclass.

        Args:
            fact: The ExtractedImport to store.
        """
        self.store_extracted_import(
            content_hash=fact.content_hash,
            raw_statement=f"from {fact.source} import {', '.join(fact.names)}"
            if fact.names
            else f"import {fact.source}",
            source_module=fact.source,
            names=list(fact.names),
            is_relative=fact.is_relative,
        )

    def get_imports_for_content(self, content_hash: str) -> list[dict[str, Any]]:
        """Get all imports extracted from content.

        Args:
            content_hash: SHA-256 of the source file content.

        Returns:
            List of dicts with import fields.
        """
        cursor = self.conn.execute(
            "SELECT * FROM extracted_imports WHERE content_hash = ?",
            (content_hash,),
        )
        return [
            {
                "content_hash": row["content_hash"],
                "raw_statement": row["raw_statement"],
                "source_module": row["source_module"],
                "names": json.loads(row["names"]),
                "is_relative": bool(row["is_relative"]),
            }
            for row in cursor
        ]

    # =====================================================================
    # Resolved Imports
    # =====================================================================

    def store_resolved_import(
        self,
        source_content_hash: str,
        source_file_id: str,
        target_file_id: str | None,
        target_module: str,
        is_stdlib: bool = False,
        is_phantom: bool = False,
    ) -> None:
        """Store a resolved import edge.

        Args:
            source_content_hash: SHA-256 of the importing file's content.
            source_file_id: Stable file UUID of the importing file.
            target_file_id: Stable file UUID of the target file (None for external).
            target_module: Module path being imported.
            is_stdlib: Whether the target is standard library.
            is_phantom: Whether the target is an unresolved internal reference.
        """
        self.conn.execute(
            """INSERT OR IGNORE INTO resolved_imports
               (source_content_hash, source_file_id, target_file_id,
                target_module, is_stdlib, is_phantom)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                source_content_hash,
                source_file_id,
                target_file_id,
                target_module,
                int(is_stdlib),
                int(is_phantom),
            ),
        )

    def get_resolved_imports_from(self, source_file_id: str) -> list[dict[str, Any]]:
        """Get all resolved imports from a file.

        Args:
            source_file_id: Stable file UUID of the importing file.

        Returns:
            List of dicts with resolved import fields.
        """
        cursor = self.conn.execute(
            "SELECT * FROM resolved_imports WHERE source_file_id = ?",
            (source_file_id,),
        )
        return [self._row_to_resolved_import_dict(row) for row in cursor]

    def get_resolved_imports_to(self, target_file_id: str) -> list[dict[str, Any]]:
        """Get all resolved imports pointing to a file.

        Args:
            target_file_id: Stable file UUID of the target file.

        Returns:
            List of dicts with resolved import fields.
        """
        cursor = self.conn.execute(
            "SELECT * FROM resolved_imports WHERE target_file_id = ?",
            (target_file_id,),
        )
        return [self._row_to_resolved_import_dict(row) for row in cursor]

    def _row_to_resolved_import_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a resolved_imports row to a dict."""
        return {
            "source_content_hash": row["source_content_hash"],
            "source_file_id": row["source_file_id"],
            "target_file_id": row["target_file_id"],
            "target_module": row["target_module"],
            "is_stdlib": bool(row["is_stdlib"]),
            "is_phantom": bool(row["is_phantom"]),
        }

    # =====================================================================
    # Session Management
    # =====================================================================

    def start_session(self, head_commit: str | None = None) -> int:
        """Start an extraction session.

        Args:
            head_commit: Current HEAD commit SHA (optional).

        Returns:
            The auto-generated session ID.
        """
        cursor = self.conn.execute(
            """INSERT INTO extraction_sessions
               (started_at, head_commit, status)
               VALUES (?, ?, 'running')""",
            (time.time(), head_commit),
        )
        session_id = cursor.lastrowid
        assert session_id is not None
        return session_id

    def complete_session(
        self,
        session_id: int,
        file_count: int,
        commit_count: int,
    ) -> None:
        """Mark a session as complete.

        Args:
            session_id: The session ID returned by :meth:`start_session`.
            file_count: Number of files processed.
            commit_count: Number of commits processed.
        """
        self.conn.execute(
            """UPDATE extraction_sessions
               SET completed_at = ?, file_count = ?, commit_count = ?, status = 'completed'
               WHERE id = ?""",
            (time.time(), file_count, commit_count, session_id),
        )

    def fail_session(self, session_id: int) -> None:
        """Mark a session as failed.

        Args:
            session_id: The session ID returned by :meth:`start_session`.
        """
        self.conn.execute(
            """UPDATE extraction_sessions
               SET completed_at = ?, status = 'failed'
               WHERE id = ?""",
            (time.time(), session_id),
        )

    def get_last_session(self) -> dict[str, Any] | None:
        """Get the most recent completed session.

        Returns:
            Dict with session fields, or None if no completed sessions.
        """
        row = self.conn.execute(
            """SELECT * FROM extraction_sessions
               WHERE status = 'completed'
               ORDER BY completed_at DESC LIMIT 1"""
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "head_commit": row["head_commit"],
            "file_count": row["file_count"],
            "commit_count": row["commit_count"],
            "status": row["status"],
        }

    # =====================================================================
    # Statistics
    # =====================================================================

    def get_stats(self) -> dict[str, int]:
        """Get overall database statistics.

        Returns:
            Dict with counts for blobs, commits, file_changes,
            file_identities, parsed_syntax, and sessions.
        """
        stats: dict[str, int] = {}
        for table in [
            "blobs",
            "commits",
            "file_changes",
            "file_identities",
            "file_observations",
            "parsed_syntax",
            "extracted_functions",
            "extracted_classes",
            "extracted_imports",
            "resolved_imports",
            "extraction_sessions",
        ]:
            row = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()  # noqa: S608
            stats[table] = row[0]
        return stats

    # =====================================================================
    # Transaction Management
    # =====================================================================

    def commit(self) -> None:
        """Commit pending changes."""
        self.conn.commit()

    def rollback(self) -> None:
        """Rollback pending changes."""
        self.conn.rollback()

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def __enter__(self) -> FactStore:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
