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
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from .fact_models import (
    AnalysisSession,
    ClassFact,
    FileFact,
    FunctionFact,
    ImportFact,
)
from ..graph.models import CodeGraph, GraphAnalysis

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 2

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

-- ═══════════════════════════════════════════════════════════════════
-- PHASE 2: Graph Storage (CodeGraph output persistence)
-- ═══════════════════════════════════════════════════════════════════

-- Graph edges (all edge types in one table)
-- Edge types: IMPORTS, CALLS, INHERITS, CONTAINS, TYPE_FLOW
CREATE TABLE IF NOT EXISTS graph_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES analysis_sessions(id),
    edge_type TEXT NOT NULL,
    source_node TEXT NOT NULL,
    source_node_type TEXT NOT NULL,
    target_node TEXT NOT NULL,
    target_node_type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    metadata TEXT,
    UNIQUE(session_id, edge_type, source_node, target_node)
);

-- Node metrics (computed values per node)
-- Metric names: pagerank, betweenness, in_degree, out_degree, depth,
--               inheritance_depth, is_dead, is_orphan, blast_radius_size
CREATE TABLE IF NOT EXISTS node_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES analysis_sessions(id),
    node_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    UNIQUE(session_id, node_id, metric_name)
);

-- Graph summary (session-level aggregate stats)
CREATE TABLE IF NOT EXISTS graph_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES analysis_sessions(id) UNIQUE,
    file_node_count INTEGER NOT NULL,
    function_node_count INTEGER NOT NULL,
    class_node_count INTEGER NOT NULL,
    import_edge_count INTEGER NOT NULL,
    call_edge_count INTEGER NOT NULL,
    inherit_edge_count INTEGER NOT NULL,
    contains_edge_count INTEGER NOT NULL,
    cycle_count INTEGER NOT NULL,
    function_cycle_count INTEGER NOT NULL,
    dead_function_count INTEGER NOT NULL,
    diamond_class_count INTEGER NOT NULL,
    modularity_score REAL NOT NULL,
    centrality_gini REAL NOT NULL,
    computed_at TEXT NOT NULL
);

-- Cycle membership (which nodes are in which cycles)
CREATE TABLE IF NOT EXISTS cycle_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES analysis_sessions(id),
    cycle_id INTEGER NOT NULL,
    cycle_type TEXT NOT NULL,
    node_id TEXT NOT NULL,
    UNIQUE(session_id, cycle_type, cycle_id, node_id)
);

-- Community membership (Louvain communities)
CREATE TABLE IF NOT EXISTS community_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES analysis_sessions(id),
    community_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    UNIQUE(session_id, node_id)
);

-- Graph indexes
CREATE INDEX IF NOT EXISTS idx_graph_edges_session ON graph_edges(session_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_source ON graph_edges(source_node);
CREATE INDEX IF NOT EXISTS idx_graph_edges_target ON graph_edges(target_node);
CREATE INDEX IF NOT EXISTS idx_graph_edges_type ON graph_edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_node_metrics_session ON node_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_node_metrics_node ON node_metrics(node_id);
CREATE INDEX IF NOT EXISTS idx_node_metrics_metric ON node_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_cycle_members_session ON cycle_members(session_id);
CREATE INDEX IF NOT EXISTS idx_community_members_session ON community_members(session_id);
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
                logger.warning(f"Database schema version {row[0]} < {SCHEMA_VERSION}, migrations needed")

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
            cursor = conn.execute(
                "SELECT * FROM analysis_sessions WHERE id = ?", (session_id,)
            )
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
                datetime.fromisoformat(row["completed_at"])
                if row["completed_at"]
                else None
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
            cursor = conn.execute(
                "SELECT * FROM file_facts WHERE session_id = ?", (session_id,)
            )
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
        cursor = conn.execute(
            "SELECT * FROM class_facts WHERE file_fact_id = ?", (file_fact_id,)
        )
        classes = [self._row_to_class_fact(r, row["path"]) for r in cursor.fetchall()]

        # Load imports
        cursor = conn.execute(
            "SELECT * FROM import_facts WHERE file_fact_id = ?", (file_fact_id,)
        )
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

    def _row_to_function_fact(
        self, row: sqlite3.Row, file_path: str
    ) -> FunctionFact:
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

    def _row_to_import_fact(
        self, row: sqlite3.Row, file_path: str | None = None
    ) -> ImportFact:
        """Convert a database row to ImportFact."""
        return ImportFact(
            file_path=file_path or row.get("file_path", ""),
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

    # ── Graph Storage (Phase 2) ─────────────────────────────────────────

    def store_graph_edges(
        self,
        session_id: str,
        edge_type: str,
        edges: dict[str, list[str]],
        source_node_type: str,
        target_node_type: str,
    ) -> int:
        """Store graph edges of a specific type.

        Args:
            session_id: Analysis session ID
            edge_type: IMPORTS, CALLS, INHERITS, CONTAINS, TYPE_FLOW
            edges: Adjacency dict {source: [targets]}
            source_node_type: FILE, FUNCTION, CLASS, TYPE
            target_node_type: FILE, FUNCTION, CLASS, TYPE

        Returns:
            Number of edges stored
        """
        count = 0
        with self._connect() as conn:
            for source, targets in edges.items():
                for target in targets:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO graph_edges
                        (session_id, edge_type, source_node, source_node_type,
                         target_node, target_node_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (session_id, edge_type, source, source_node_type,
                         target, target_node_type),
                    )
                    count += 1
        return count

    def store_node_metric(
        self,
        session_id: str,
        node_id: str,
        node_type: str,
        metric_name: str,
        value: float,
    ) -> None:
        """Store a single metric for a node."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO node_metrics
                (session_id, node_id, node_type, metric_name, value)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, node_id, node_type, metric_name, value),
            )

    def store_node_metrics_batch(
        self,
        session_id: str,
        node_type: str,
        metric_name: str,
        values: dict[str, float],
    ) -> int:
        """Store metrics for multiple nodes in batch.

        Args:
            session_id: Analysis session ID
            node_type: FILE, FUNCTION, CLASS
            metric_name: pagerank, betweenness, depth, etc.
            values: {node_id: value}

        Returns:
            Number of metrics stored
        """
        with self._connect() as conn:
            for node_id, value in values.items():
                conn.execute(
                    """
                    INSERT OR REPLACE INTO node_metrics
                    (session_id, node_id, node_type, metric_name, value)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (session_id, node_id, node_type, metric_name, value),
                )
        return len(values)

    def store_graph_summary(
        self,
        session_id: str,
        summary: dict,
    ) -> None:
        """Store graph-level summary statistics."""
        from datetime import datetime, timezone

        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO graph_summary
                (session_id, file_node_count, function_node_count, class_node_count,
                 import_edge_count, call_edge_count, inherit_edge_count, contains_edge_count,
                 cycle_count, function_cycle_count, dead_function_count, diamond_class_count,
                 modularity_score, centrality_gini, computed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    summary.get("file_node_count", 0),
                    summary.get("function_node_count", 0),
                    summary.get("class_node_count", 0),
                    summary.get("import_edge_count", 0),
                    summary.get("call_edge_count", 0),
                    summary.get("inherit_edge_count", 0),
                    summary.get("contains_edge_count", 0),
                    summary.get("cycle_count", 0),
                    summary.get("function_cycle_count", 0),
                    summary.get("dead_function_count", 0),
                    summary.get("diamond_class_count", 0),
                    summary.get("modularity_score", 0.0),
                    summary.get("centrality_gini", 0.0),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def store_cycle_members(
        self,
        session_id: str,
        cycle_type: str,
        cycles: list[set[str]],
    ) -> None:
        """Store cycle membership information.

        Args:
            session_id: Analysis session ID
            cycle_type: FILE or FUNCTION
            cycles: List of sets, each set is a cycle's member nodes
        """
        with self._connect() as conn:
            for cycle_id, members in enumerate(cycles):
                for node_id in members:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO cycle_members
                        (session_id, cycle_id, cycle_type, node_id)
                        VALUES (?, ?, ?, ?)
                        """,
                        (session_id, cycle_id, cycle_type, node_id),
                    )

    def store_community_members(
        self,
        session_id: str,
        node_community: dict[str, int],
    ) -> None:
        """Store community membership from Louvain.

        Args:
            session_id: Analysis session ID
            node_community: {node_id: community_id}
        """
        with self._connect() as conn:
            for node_id, community_id in node_community.items():
                conn.execute(
                    """
                    INSERT OR REPLACE INTO community_members
                    (session_id, community_id, node_id)
                    VALUES (?, ?, ?)
                    """,
                    (session_id, community_id, node_id),
                )

    # ── Graph Retrieval (Phase 2) ───────────────────────────────────────

    def get_graph_edges(
        self,
        session_id: str,
        edge_type: str | None = None,
    ) -> dict[str, list[str]]:
        """Get graph edges, optionally filtered by type.

        Args:
            session_id: Analysis session ID
            edge_type: Optional filter (IMPORTS, CALLS, etc.)

        Returns:
            Adjacency dict {source: [targets]}
        """
        with self._connect() as conn:
            if edge_type:
                cursor = conn.execute(
                    """
                    SELECT source_node, target_node FROM graph_edges
                    WHERE session_id = ? AND edge_type = ?
                    """,
                    (session_id, edge_type),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT source_node, target_node FROM graph_edges
                    WHERE session_id = ?
                    """,
                    (session_id,),
                )

            edges: dict[str, list[str]] = {}
            for row in cursor.fetchall():
                source = row["source_node"]
                target = row["target_node"]
                edges.setdefault(source, []).append(target)
            return edges

    def get_node_metrics(
        self,
        session_id: str,
        metric_name: str | None = None,
        node_type: str | None = None,
    ) -> dict[str, dict[str, float]]:
        """Get node metrics, optionally filtered.

        Args:
            session_id: Analysis session ID
            metric_name: Optional filter by metric (pagerank, etc.)
            node_type: Optional filter by node type (FILE, FUNCTION, etc.)

        Returns:
            Nested dict {node_id: {metric_name: value}}
        """
        with self._connect() as conn:
            query = "SELECT node_id, metric_name, value FROM node_metrics WHERE session_id = ?"
            params: list = [session_id]

            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            if node_type:
                query += " AND node_type = ?"
                params.append(node_type)

            cursor = conn.execute(query, params)

            result: dict[str, dict[str, float]] = {}
            for row in cursor.fetchall():
                node_id = row["node_id"]
                if node_id not in result:
                    result[node_id] = {}
                result[node_id][row["metric_name"]] = row["value"]
            return result

    def get_graph_summary(self, session_id: str) -> dict | None:
        """Get graph-level summary for a session."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM graph_summary WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return dict(row)

    def get_cycle_members(
        self,
        session_id: str,
        cycle_type: str | None = None,
    ) -> list[set[str]]:
        """Get cycles as list of node sets.

        Args:
            session_id: Analysis session ID
            cycle_type: Optional filter (FILE or FUNCTION)

        Returns:
            List of sets, each set is a cycle's members
        """
        with self._connect() as conn:
            if cycle_type:
                cursor = conn.execute(
                    """
                    SELECT cycle_id, node_id FROM cycle_members
                    WHERE session_id = ? AND cycle_type = ?
                    ORDER BY cycle_id
                    """,
                    (session_id, cycle_type),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT cycle_id, node_id FROM cycle_members
                    WHERE session_id = ?
                    ORDER BY cycle_id
                    """,
                    (session_id,),
                )

            cycles_dict: dict[int, set[str]] = {}
            for row in cursor.fetchall():
                cycle_id = row["cycle_id"]
                if cycle_id not in cycles_dict:
                    cycles_dict[cycle_id] = set()
                cycles_dict[cycle_id].add(row["node_id"])

            return list(cycles_dict.values())

    def get_community_members(self, session_id: str) -> dict[str, int]:
        """Get community membership for all nodes.

        Returns:
            {node_id: community_id}
        """
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT node_id, community_id FROM community_members
                WHERE session_id = ?
                """,
                (session_id,),
            )
            return {row["node_id"]: row["community_id"] for row in cursor.fetchall()}
