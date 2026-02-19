"""SQL schema for the unified fact store.

All tables live in a single SQLite database (``facts.db``).
The schema is versioned; ``create_schema`` is idempotent and checks
the version on every call.

Table groups:
    Content:     blobs
    Identity:    file_identities, file_renames, author_identities, author_emails
    Git:         commits, file_observations, file_changes
    Parsing:     parsed_syntax, extracted_functions, extracted_classes,
                 extracted_imports, resolved_imports
    Snapshots:   current_snapshot, path_lookup
    Meta:        schema_version, extraction_sessions
"""

from __future__ import annotations

import logging
import sqlite3

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

# ── DDL ───────────────────────────────────────────────────────────────

_SCHEMA_SQL = """\
-- =====================================================================
-- Meta
-- =====================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    created_at  TEXT    NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS extraction_sessions (
    session_id      TEXT    PRIMARY KEY,
    started_at      TEXT    NOT NULL,
    completed_at    TEXT,
    commit_sha      TEXT,
    analyzed_path   TEXT    NOT NULL,
    tool_version    TEXT    NOT NULL,
    config_hash     TEXT,
    status          TEXT    NOT NULL DEFAULT 'running',
    file_count      INTEGER DEFAULT 0,
    error_message   TEXT
);

-- =====================================================================
-- Content-addressable blob storage
-- =====================================================================

CREATE TABLE IF NOT EXISTS blobs (
    content_hash     TEXT    PRIMARY KEY,
    data             BLOB   NOT NULL,
    original_size    INTEGER NOT NULL,
    compressed_size  INTEGER NOT NULL
);

-- =====================================================================
-- Identity
-- =====================================================================

CREATE TABLE IF NOT EXISTS file_identities (
    file_id       TEXT    PRIMARY KEY,
    birth_commit  TEXT    NOT NULL,
    birth_path    TEXT    NOT NULL,
    current_path  TEXT,
    is_alive      INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS file_renames (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id       TEXT    NOT NULL REFERENCES file_identities(file_id),
    commit_hash   TEXT    NOT NULL,
    old_path      TEXT    NOT NULL,
    new_path      TEXT    NOT NULL,
    timestamp     INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS author_identities (
    author_id     TEXT    PRIMARY KEY,
    canonical_name TEXT   NOT NULL,
    canonical_email TEXT  NOT NULL
);

CREATE TABLE IF NOT EXISTS author_emails (
    email         TEXT    PRIMARY KEY,
    author_id     TEXT    NOT NULL REFERENCES author_identities(author_id),
    name_raw      TEXT    NOT NULL
);

-- =====================================================================
-- Git facts
-- =====================================================================

CREATE TABLE IF NOT EXISTS commits (
    commit_hash     TEXT    PRIMARY KEY,
    timestamp       INTEGER NOT NULL,
    author_id       TEXT    NOT NULL,
    author_email_raw TEXT   NOT NULL,
    author_name_raw TEXT    NOT NULL,
    message_subject TEXT    NOT NULL,
    message_body    TEXT,
    parent_hashes   TEXT    NOT NULL,
    is_merge        INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS file_observations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id       TEXT    NOT NULL REFERENCES file_identities(file_id),
    commit_hash   TEXT    NOT NULL REFERENCES commits(commit_hash),
    path          TEXT    NOT NULL,
    content_hash  TEXT    NOT NULL,
    timestamp     INTEGER NOT NULL,
    UNIQUE(file_id, commit_hash)
);

CREATE TABLE IF NOT EXISTS file_changes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_hash   TEXT    NOT NULL REFERENCES commits(commit_hash),
    file_id       TEXT    NOT NULL REFERENCES file_identities(file_id),
    change_type   TEXT    NOT NULL,
    old_path      TEXT,
    new_path      TEXT,
    additions     INTEGER,
    deletions     INTEGER
);

-- =====================================================================
-- Parsed facts (keyed by content_hash -- pure function of content)
-- =====================================================================

CREATE TABLE IF NOT EXISTS parsed_syntax (
    content_hash   TEXT    PRIMARY KEY,
    language       TEXT    NOT NULL,
    lines          INTEGER NOT NULL,
    tokens         INTEGER,
    complexity     INTEGER,
    max_nesting    INTEGER,
    has_main_guard INTEGER NOT NULL DEFAULT 0,
    stub_ratio     REAL,
    parser_type    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS extracted_functions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash    TEXT    NOT NULL REFERENCES parsed_syntax(content_hash),
    name            TEXT    NOT NULL,
    qualified_name  TEXT    NOT NULL,
    start_line      INTEGER NOT NULL,
    end_line        INTEGER NOT NULL,
    params          TEXT    NOT NULL,
    decorators      TEXT    NOT NULL,
    body_tokens     INTEGER NOT NULL,
    nesting_depth   INTEGER NOT NULL,
    is_stub         INTEGER NOT NULL DEFAULT 0,
    class_name      TEXT
);

CREATE TABLE IF NOT EXISTS extracted_classes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash    TEXT    NOT NULL REFERENCES parsed_syntax(content_hash),
    name            TEXT    NOT NULL,
    start_line      INTEGER NOT NULL,
    end_line        INTEGER NOT NULL,
    bases           TEXT    NOT NULL,
    method_names    TEXT    NOT NULL,
    field_names     TEXT    NOT NULL,
    is_abstract     INTEGER NOT NULL DEFAULT 0,
    method_count    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS extracted_imports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash    TEXT    NOT NULL REFERENCES parsed_syntax(content_hash),
    source          TEXT    NOT NULL,
    names           TEXT    NOT NULL,
    is_relative     INTEGER NOT NULL DEFAULT 0,
    resolved_path   TEXT
);

CREATE TABLE IF NOT EXISTS resolved_imports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash    TEXT    NOT NULL,
    source          TEXT    NOT NULL,
    resolved_path   TEXT    NOT NULL,
    resolution_type TEXT    NOT NULL,
    UNIQUE(content_hash, source, resolved_path)
);

-- =====================================================================
-- Snapshot (current working-tree state)
-- =====================================================================

CREATE TABLE IF NOT EXISTS current_snapshot (
    file_id       TEXT    PRIMARY KEY REFERENCES file_identities(file_id),
    path          TEXT    NOT NULL,
    content_hash  TEXT    NOT NULL,
    mtime         REAL,
    snapshot_at   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS path_lookup (
    path          TEXT    PRIMARY KEY,
    file_id       TEXT    NOT NULL REFERENCES file_identities(file_id),
    content_hash  TEXT    NOT NULL
);

-- =====================================================================
-- Indexes
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_file_renames_file_id
    ON file_renames(file_id);
CREATE INDEX IF NOT EXISTS idx_file_renames_commit
    ON file_renames(commit_hash);

CREATE INDEX IF NOT EXISTS idx_author_emails_author_id
    ON author_emails(author_id);

CREATE INDEX IF NOT EXISTS idx_commits_timestamp
    ON commits(timestamp);
CREATE INDEX IF NOT EXISTS idx_commits_author
    ON commits(author_id);

CREATE INDEX IF NOT EXISTS idx_file_observations_file_id
    ON file_observations(file_id);
CREATE INDEX IF NOT EXISTS idx_file_observations_commit
    ON file_observations(commit_hash);
CREATE INDEX IF NOT EXISTS idx_file_observations_content
    ON file_observations(content_hash);

CREATE INDEX IF NOT EXISTS idx_file_changes_commit
    ON file_changes(commit_hash);
CREATE INDEX IF NOT EXISTS idx_file_changes_file_id
    ON file_changes(file_id);

CREATE INDEX IF NOT EXISTS idx_extracted_functions_content
    ON extracted_functions(content_hash);
CREATE INDEX IF NOT EXISTS idx_extracted_classes_content
    ON extracted_classes(content_hash);
CREATE INDEX IF NOT EXISTS idx_extracted_imports_content
    ON extracted_imports(content_hash);
CREATE INDEX IF NOT EXISTS idx_resolved_imports_content
    ON resolved_imports(content_hash);

CREATE INDEX IF NOT EXISTS idx_current_snapshot_path
    ON current_snapshot(path);
CREATE INDEX IF NOT EXISTS idx_current_snapshot_content
    ON current_snapshot(content_hash);

CREATE INDEX IF NOT EXISTS idx_extraction_sessions_status
    ON extraction_sessions(status);
"""


def create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes if they do not exist.

    Idempotent: safe to call on every startup.  Checks the schema version
    and logs a warning if the database was created by a newer version.

    Args:
        conn: An open SQLite connection.  The caller is responsible for
              committing the transaction.
    """
    conn.executescript(_SCHEMA_SQL)

    cursor = conn.execute(
        "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
    )
    row = cursor.fetchone()

    if row is None:
        # First time -- stamp the version
        from datetime import datetime, timezone

        conn.execute(
            "INSERT INTO schema_version (version, created_at, description) VALUES (?, ?, ?)",
            (
                SCHEMA_VERSION,
                datetime.now(timezone.utc).isoformat(),
                "Initial schema for unified fact store",
            ),
        )
    elif row[0] > SCHEMA_VERSION:
        logger.warning(
            "Database schema version %d is newer than code version %d. "
            "You may need to upgrade shannon-insight.",
            row[0],
            SCHEMA_VERSION,
        )
    elif row[0] < SCHEMA_VERSION:
        logger.warning(
            "Database schema version %d < %d, migrations needed.",
            row[0],
            SCHEMA_VERSION,
        )
