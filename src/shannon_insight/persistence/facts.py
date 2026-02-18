"""Fact storage database for Phase 1 data.

Stores complete parsed facts about source files with session tracking.
Separate from history.db (which stores signals/snapshots).

Schema:
- analysis_sessions: tracks each analysis run
- file_facts: one row per file per session
- function_facts: one row per function
- class_facts: one row per class
- import_facts: one row per import

Usage:
    db = FactDatabase(".shannon/facts.db")
    db.create_session(session)
    db.store_file_fact(fact)
    db.complete_session(session_id)
"""

from __future__ import annotations

import json
import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .fact_models import (
    AnalysisSession,
    ClassFact,
    FileFact,
    FunctionFact,
    ImportFact,
)

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

# Schema SQL
SCHEMA = """
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_info (
    version INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL
);

-- Session tracking
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    commit_sha TEXT,
    analyzed_path TEXT NOT NULL,
    tool_version TEXT NOT NULL,
    config_hash TEXT,
    status TEXT DEFAULT 'running',
    file_count INTEGER DEFAULT 0,
    error_message TEXT
);

-- File facts (one row per file per session)
CREATE TABLE IF NOT EXISTS file_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES analysis_sessions(id),
    path TEXT NOT NULL,
    absolute_path TEXT,
    content_hash TEXT NOT NULL,
    language TEXT NOT NULL,
    lines INTEGER NOT NULL,
    tokens INTEGER NOT NULL,
    complexity REAL NOT NULL,
    has_main_guard INTEGER NOT NULL,
    mtime REAL NOT NULL,
    function_count INTEGER NOT NULL,
    class_count INTEGER NOT NULL,
    import_count INTEGER NOT NULL,
    max_nesting INTEGER NOT NULL,
    stub_ratio REAL NOT NULL,
    impl_gini REAL NOT NULL,
    parsed_at TEXT NOT NULL,
    parser_type TEXT NOT NULL,
    tool_version TEXT NOT NULL,
    UNIQUE(session_id, path)
);

-- Function facts (one row per function)
CREATE TABLE IF NOT EXISTS function_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_fact_id INTEGER NOT NULL REFERENCES file_facts(id),
    name TEXT NOT NULL,
    qualified_name TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    params TEXT NOT NULL,
    signature_tokens INTEGER NOT NULL,
    decorators TEXT NOT NULL,
    body_tokens INTEGER NOT NULL,
    nesting_depth INTEGER NOT NULL,
    call_targets TEXT NOT NULL,
    class_name TEXT,
    is_stub INTEGER NOT NULL,
    stub_score REAL NOT NULL
);

-- Class facts (one row per class)
CREATE TABLE IF NOT EXISTS class_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_fact_id INTEGER NOT NULL REFERENCES file_facts(id),
    name TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    bases TEXT NOT NULL,
    method_names TEXT NOT NULL,
    field_names TEXT NOT NULL,
    is_abstract INTEGER NOT NULL,
    method_count INTEGER NOT NULL
);

-- Import facts (one row per import)
CREATE TABLE IF NOT EXISTS import_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_fact_id INTEGER NOT NULL REFERENCES file_facts(id),
    source TEXT NOT NULL,
    names TEXT NOT NULL,
    resolved_path TEXT,
    is_relative INTEGER NOT NULL,
    is_phantom INTEGER NOT NULL,
    is_stdlib INTEGER NOT NULL
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_file_facts_session ON file_facts(session_id);
CREATE INDEX IF NOT EXISTS idx_file_facts_path ON file_facts(path);
CREATE INDEX IF NOT EXISTS idx_file_facts_content_hash ON file_facts(content_hash);
CREATE INDEX IF NOT EXISTS idx_function_facts_file ON function_facts(file_fact_id);
CREATE INDEX IF NOT EXISTS idx_function_facts_qualified ON function_facts(qualified_name);
CREATE INDEX IF NOT EXISTS idx_class_facts_file ON class_facts(file_fact_id);
CREATE INDEX IF NOT EXISTS idx_import_facts_file ON import_facts(file_fact_id);
CREATE INDEX IF NOT EXISTS idx_import_facts_resolved ON import_facts(resolved_path);
"""


class FactDatabase:
    """SQLite database for storing parsed file facts.

    Thread-safe for concurrent reads, single writer.
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
            cursor = conn.execute("SELECT version FROM schema_info ORDER BY version DESC LIMIT 1")
            row = cursor.fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO schema_info (version, created_at) VALUES (?, ?)",
                    (SCHEMA_VERSION, datetime.now(timezone.utc).isoformat()),
                )
            elif row[0] < SCHEMA_VERSION:
                # Future: run migrations
                logger.warning(
                    f"Database schema version {row[0]} < {SCHEMA_VERSION}, migrations needed"
                )

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connection."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── Session Management ─────────────────────────────────────────────

    def create_session(self, session: AnalysisSession) -> None:
        """Create a new analysis session."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO analysis_sessions
                (id, started_at, completed_at, commit_sha, analyzed_path,
                 tool_version, config_hash, status, file_count, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.started_at.isoformat(),
                    session.completed_at.isoformat() if session.completed_at else None,
                    session.commit_sha,
                    session.analyzed_path,
                    session.tool_version,
                    session.config_hash,
                    session.status,
                    session.file_count,
                    session.error_message,
                ),
            )

    def complete_session(
        self, session_id: str, file_count: int, error_message: str | None = None
    ) -> None:
        """Mark a session as completed."""
        status = "failed" if error_message else "completed"
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE analysis_sessions
                SET completed_at = ?, status = ?, file_count = ?, error_message = ?
                WHERE id = ?
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    status,
                    file_count,
                    error_message,
                    session_id,
                ),
            )

    def get_session(self, session_id: str) -> AnalysisSession | None:
        """Get a session by ID."""
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM analysis_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_session(row)

    def _row_to_session(self, row: sqlite3.Row) -> AnalysisSession:
        """Convert a database row to AnalysisSession."""
        return AnalysisSession(
            id=row["id"],
            started_at=datetime.fromisoformat(row["started_at"]),
            completed_at=(
                datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
            ),
            commit_sha=row["commit_sha"],
            analyzed_path=row["analyzed_path"],
            tool_version=row["tool_version"],
            config_hash=row["config_hash"],
            status=row["status"],
            file_count=row["file_count"],
            error_message=row["error_message"],
        )

    # ── File Fact Storage ──────────────────────────────────────────────

    def store_file_fact(self, fact: FileFact) -> int:
        """Store a file fact and its entities.

        Args:
            fact: The FileFact to store

        Returns:
            The database ID of the stored file fact
        """
        with self._connect() as conn:
            # Insert file fact
            cursor = conn.execute(
                """
                INSERT INTO file_facts
                (session_id, path, absolute_path, content_hash, language,
                 lines, tokens, complexity, has_main_guard, mtime,
                 function_count, class_count, import_count, max_nesting,
                 stub_ratio, impl_gini, parsed_at, parser_type, tool_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fact.session_id,
                    fact.path,
                    fact.absolute_path,
                    fact.content_hash,
                    fact.language,
                    fact.lines,
                    fact.tokens,
                    fact.complexity,
                    1 if fact.has_main_guard else 0,
                    fact.mtime,
                    fact.function_count,
                    fact.class_count,
                    fact.import_count,
                    fact.max_nesting,
                    fact.stub_ratio,
                    fact.impl_gini,
                    fact.parsed_at.isoformat(),
                    fact.parser_type,
                    fact.tool_version,
                ),
            )
            file_fact_id = cursor.lastrowid
            assert file_fact_id is not None

            # Insert function facts
            for fn in fact.functions:
                self._store_function_fact(conn, file_fact_id, fn)

            # Insert class facts
            for cls in fact.classes:
                self._store_class_fact(conn, file_fact_id, cls)

            # Insert import facts
            for imp in fact.imports:
                self._store_import_fact(conn, file_fact_id, imp)

            return file_fact_id

    def _store_function_fact(
        self, conn: sqlite3.Connection, file_fact_id: int, fn: FunctionFact
    ) -> None:
        """Store a function fact."""
        conn.execute(
            """
            INSERT INTO function_facts
            (file_fact_id, name, qualified_name, start_line, end_line,
             params, signature_tokens, decorators, body_tokens, nesting_depth,
             call_targets, class_name, is_stub, stub_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                file_fact_id,
                fn.name,
                fn.qualified_name,
                fn.start_line,
                fn.end_line,
                json.dumps(fn.params),
                fn.signature_tokens,
                json.dumps(fn.decorators),
                fn.body_tokens,
                fn.nesting_depth,
                json.dumps(fn.call_targets),
                fn.class_name,
                1 if fn.is_stub else 0,
                fn.stub_score,
            ),
        )

    def _store_class_fact(
        self, conn: sqlite3.Connection, file_fact_id: int, cls: ClassFact
    ) -> None:
        """Store a class fact."""
        conn.execute(
            """
            INSERT INTO class_facts
            (file_fact_id, name, start_line, end_line, bases,
             method_names, field_names, is_abstract, method_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                file_fact_id,
                cls.name,
                cls.start_line,
                cls.end_line,
                json.dumps(cls.bases),
                json.dumps(cls.method_names),
                json.dumps(cls.field_names),
                1 if cls.is_abstract else 0,
                cls.method_count,
            ),
        )

    def _store_import_fact(
        self, conn: sqlite3.Connection, file_fact_id: int, imp: ImportFact
    ) -> None:
        """Store an import fact."""
        conn.execute(
            """
            INSERT INTO import_facts
            (file_fact_id, source, names, resolved_path,
             is_relative, is_phantom, is_stdlib)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                file_fact_id,
                imp.source,
                json.dumps(imp.names),
                imp.resolved_path,
                1 if imp.is_relative else 0,
                1 if imp.is_phantom else 0,
                1 if imp.is_stdlib else 0,
            ),
        )

    # ── Queries ────────────────────────────────────────────────────────

    def get_file_facts_for_session(self, session_id: str) -> list[FileFact]:
        """Get all file facts for a session."""
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM file_facts WHERE session_id = ?", (session_id,))
            return [self._load_file_fact(conn, row) for row in cursor.fetchall()]

    def get_file_fact_by_path(self, session_id: str, path: str) -> FileFact | None:
        """Get a file fact by session and path."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM file_facts WHERE session_id = ? AND path = ?",
                (session_id, path),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._load_file_fact(conn, row)

    def get_call_targets_for_session(self, session_id: str) -> dict[str, list[str]]:
        """Get all call targets indexed by qualified function name.

        Returns:
            Dict mapping qualified_name -> list of call targets
        """
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT f.qualified_name, f.call_targets
                FROM function_facts f
                JOIN file_facts ff ON f.file_fact_id = ff.id
                WHERE ff.session_id = ?
                """,
                (session_id,),
            )
            result = {}
            for row in cursor.fetchall():
                result[row["qualified_name"]] = json.loads(row["call_targets"])
            return result

    def get_class_bases_for_session(self, session_id: str) -> dict[str, list[str]]:
        """Get all class bases indexed by class name.

        Returns:
            Dict mapping "file:ClassName" -> list of base class names
        """
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT ff.path, c.name, c.bases
                FROM class_facts c
                JOIN file_facts ff ON c.file_fact_id = ff.id
                WHERE ff.session_id = ?
                """,
                (session_id,),
            )
            result = {}
            for row in cursor.fetchall():
                key = f"{row['path']}:{row['name']}"
                result[key] = json.loads(row["bases"])
            return result

    def get_imports_for_session(self, session_id: str) -> list[ImportFact]:
        """Get all imports for a session."""
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT ff.path as file_path, i.*
                FROM import_facts i
                JOIN file_facts ff ON i.file_fact_id = ff.id
                WHERE ff.session_id = ?
                """,
                (session_id,),
            )
            return [self._row_to_import_fact(row) for row in cursor.fetchall()]

    def _load_file_fact(self, conn: sqlite3.Connection, row: sqlite3.Row) -> FileFact:
        """Load a complete FileFact including entities."""
        file_fact_id = row["id"]

        # Load functions
        cursor = conn.execute(
            "SELECT * FROM function_facts WHERE file_fact_id = ?", (file_fact_id,)
        )
        functions = [self._row_to_function_fact(r, row["path"]) for r in cursor.fetchall()]

        # Load classes
        cursor = conn.execute("SELECT * FROM class_facts WHERE file_fact_id = ?", (file_fact_id,))
        classes = [self._row_to_class_fact(r, row["path"]) for r in cursor.fetchall()]

        # Load imports
        cursor = conn.execute("SELECT * FROM import_facts WHERE file_fact_id = ?", (file_fact_id,))
        imports = [self._row_to_import_fact(r, row["path"]) for r in cursor.fetchall()]

        return FileFact(
            path=row["path"],
            absolute_path=row["absolute_path"] or "",
            content_hash=row["content_hash"],
            session_id=row["session_id"],
            parsed_at=datetime.fromisoformat(row["parsed_at"]),
            parser_type=row["parser_type"],
            tool_version=row["tool_version"],
            language=row["language"],
            lines=row["lines"],
            tokens=row["tokens"],
            complexity=row["complexity"],
            has_main_guard=bool(row["has_main_guard"]),
            mtime=row["mtime"],
            functions=functions,
            classes=classes,
            imports=imports,
            function_count=row["function_count"],
            class_count=row["class_count"],
            import_count=row["import_count"],
            max_nesting=row["max_nesting"],
            stub_ratio=row["stub_ratio"],
            impl_gini=row["impl_gini"],
        )

    def _row_to_function_fact(self, row: sqlite3.Row, file_path: str) -> FunctionFact:
        """Convert a database row to FunctionFact."""
        return FunctionFact(
            name=row["name"],
            qualified_name=row["qualified_name"],
            file_path=file_path,
            start_line=row["start_line"],
            end_line=row["end_line"],
            params=json.loads(row["params"]),
            signature_tokens=row["signature_tokens"],
            decorators=json.loads(row["decorators"]),
            body_tokens=row["body_tokens"],
            nesting_depth=row["nesting_depth"],
            call_targets=json.loads(row["call_targets"]),
            class_name=row["class_name"],
            is_stub=bool(row["is_stub"]),
            stub_score=row["stub_score"],
        )

    def _row_to_class_fact(self, row: sqlite3.Row, file_path: str) -> ClassFact:
        """Convert a database row to ClassFact."""
        return ClassFact(
            name=row["name"],
            file_path=file_path,
            start_line=row["start_line"],
            end_line=row["end_line"],
            bases=json.loads(row["bases"]),
            method_names=json.loads(row["method_names"]),
            field_names=json.loads(row["field_names"]),
            is_abstract=bool(row["is_abstract"]),
            method_count=row["method_count"],
        )

    def _row_to_import_fact(self, row: sqlite3.Row, file_path: str | None = None) -> ImportFact:
        """Convert a database row to ImportFact."""
        # file_path may come from param or from join query result
        effective_path = file_path
        if effective_path is None:
            try:
                effective_path = row["file_path"]
            except (IndexError, KeyError):
                effective_path = ""
        return ImportFact(
            file_path=effective_path,
            source=row["source"],
            names=json.loads(row["names"]),
            resolved_path=row["resolved_path"],
            is_relative=bool(row["is_relative"]),
            is_phantom=bool(row["is_phantom"]),
            is_stdlib=bool(row["is_stdlib"]),
        )

    # ── Statistics ─────────────────────────────────────────────────────

    def get_session_stats(self, session_id: str) -> dict[str, int]:
        """Get statistics for a session."""
        with self._connect() as conn:
            stats = {}

            cursor = conn.execute(
                "SELECT COUNT(*) FROM file_facts WHERE session_id = ?", (session_id,)
            )
            stats["file_count"] = cursor.fetchone()[0]

            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM function_facts f
                JOIN file_facts ff ON f.file_fact_id = ff.id
                WHERE ff.session_id = ?
                """,
                (session_id,),
            )
            stats["function_count"] = cursor.fetchone()[0]

            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM class_facts c
                JOIN file_facts ff ON c.file_fact_id = ff.id
                WHERE ff.session_id = ?
                """,
                (session_id,),
            )
            stats["class_count"] = cursor.fetchone()[0]

            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM import_facts i
                JOIN file_facts ff ON i.file_fact_id = ff.id
                WHERE ff.session_id = ?
                """,
                (session_id,),
            )
            stats["import_count"] = cursor.fetchone()[0]

            return stats
