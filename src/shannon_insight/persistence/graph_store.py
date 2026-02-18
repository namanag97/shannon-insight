"""Graph storage for Phase 2 CodeGraph persistence.

Stores graph structure and computed metrics separately from raw facts.
Uses the same SQLite database but manages graph-specific tables.

Usage:
    store = GraphStore(".shannon/facts.db")
    store.store_code_graph(session_id, graph)
    store.store_graph_analysis(session_id, analysis, graph)

    # Later retrieval:
    graph = store.load_code_graph(session_id)
    analysis = store.load_graph_analysis(session_id)
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from ..graph.models import CodeGraph, Community, CycleGroup, GraphAnalysis

logger = logging.getLogger(__name__)

# Graph-specific schema (extends facts.db)
GRAPH_SCHEMA = """
-- ═══════════════════════════════════════════════════════════════════
-- PHASE 2: Graph Storage (CodeGraph output persistence)
-- ═══════════════════════════════════════════════════════════════════

-- Graph edges (all edge types in one table)
CREATE TABLE IF NOT EXISTS graph_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
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
CREATE TABLE IF NOT EXISTS node_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    UNIQUE(session_id, node_id, metric_name)
);

-- Graph summary (session-level aggregate stats)
CREATE TABLE IF NOT EXISTS graph_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
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

-- Cycle membership
CREATE TABLE IF NOT EXISTS cycle_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    cycle_id INTEGER NOT NULL,
    cycle_type TEXT NOT NULL,
    node_id TEXT NOT NULL,
    UNIQUE(session_id, cycle_type, cycle_id, node_id)
);

-- Community membership
CREATE TABLE IF NOT EXISTS community_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    community_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    UNIQUE(session_id, node_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_graph_edges_session ON graph_edges(session_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_type ON graph_edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_node_metrics_session ON node_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_node_metrics_metric ON node_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_cycle_members_session ON cycle_members(session_id);
CREATE INDEX IF NOT EXISTS idx_community_members_session ON community_members(session_id);
"""


class GraphStore:
    """SQLite storage for CodeGraph and GraphAnalysis.

    Separate from FactDatabase to keep concerns isolated.
    Can share the same database file or use a separate one.
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(GRAPH_SCHEMA)

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
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

    # ── Store Operations ────────────────────────────────────────────────

    def store_code_graph(self, session_id: str, graph: CodeGraph) -> dict[str, int]:
        """Store a complete CodeGraph."""
        counts = {}
        with self._connect() as conn:
            # Import edges
            counts["imports"] = self._store_edges(
                conn, session_id, "IMPORTS", graph.import_edges, "FILE", "FILE"
            )
            # Call edges
            counts["calls"] = self._store_edges(
                conn, session_id, "CALLS", graph.call_edges, "FUNCTION", "FUNCTION"
            )
            # Inherit edges
            counts["inherits"] = self._store_edges(
                conn, session_id, "INHERITS", graph.inherit_edges, "CLASS", "CLASS"
            )
            # Contains edges (split by target type)
            for file_path, contained in graph.contains_edges.items():
                for node in contained:
                    target_type = "FUNCTION" if node in graph.function_nodes else "CLASS"
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO graph_edges
                        (session_id, edge_type, source_node, source_node_type,
                         target_node, target_node_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (session_id, "CONTAINS", file_path, "FILE", node, target_type),
                    )
                    counts["contains"] = counts.get("contains", 0) + 1
        return counts

    def _store_edges(
        self,
        conn: sqlite3.Connection,
        session_id: str,
        edge_type: str,
        edges: dict[str, list[str]],
        src_type: str,
        tgt_type: str,
    ) -> int:
        count = 0
        for source, targets in edges.items():
            for target in targets:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO graph_edges
                    (session_id, edge_type, source_node, source_node_type,
                     target_node, target_node_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (session_id, edge_type, source, src_type, target, tgt_type),
                )
                count += 1
        return count

    def store_graph_analysis(
        self, session_id: str, analysis: GraphAnalysis, graph: CodeGraph
    ) -> None:
        """Store GraphAnalysis metrics."""
        with self._connect() as conn:
            # File metrics
            self._store_metrics(conn, session_id, "FILE", "pagerank", analysis.pagerank)
            self._store_metrics(conn, session_id, "FILE", "betweenness", analysis.betweenness)
            self._store_metrics(
                conn,
                session_id,
                "FILE",
                "in_degree",
                {k: float(v) for k, v in analysis.in_degree.items()},
            )
            self._store_metrics(
                conn,
                session_id,
                "FILE",
                "out_degree",
                {k: float(v) for k, v in analysis.out_degree.items()},
            )
            self._store_metrics(
                conn, session_id, "FILE", "depth", {k: float(v) for k, v in analysis.depth.items()}
            )
            self._store_metrics(
                conn,
                session_id,
                "FILE",
                "is_orphan",
                {k: 1.0 if v else 0.0 for k, v in analysis.is_orphan.items()},
            )

            # Function metrics
            self._store_metrics(
                conn, session_id, "FUNCTION", "pagerank", analysis.function_pagerank
            )
            self._store_metrics(
                conn, session_id, "FUNCTION", "betweenness", analysis.function_betweenness
            )
            self._store_metrics(
                conn, session_id, "FUNCTION", "is_dead", dict.fromkeys(analysis.dead_functions, 1.0)
            )

            # Class metrics
            self._store_metrics(
                conn,
                session_id,
                "CLASS",
                "inheritance_depth",
                {k: float(v) for k, v in analysis.inheritance_depth.items()},
            )
            self._store_metrics(
                conn,
                session_id,
                "CLASS",
                "has_diamond",
                dict.fromkeys(analysis.diamond_classes, 1.0),
            )

            # Cycles
            for i, cycle in enumerate(analysis.cycles):
                for node in cycle.nodes:
                    conn.execute(
                        "INSERT OR REPLACE INTO cycle_members VALUES (NULL,?,?,?,?)",
                        (session_id, i, "FILE", node),
                    )
            for i, cycle in enumerate(analysis.function_cycles):
                for node in cycle:
                    conn.execute(
                        "INSERT OR REPLACE INTO cycle_members VALUES (NULL,?,?,?,?)",
                        (session_id, i, "FUNCTION", node),
                    )

            # Communities
            for node, comm_id in analysis.node_community.items():
                conn.execute(
                    "INSERT OR REPLACE INTO community_members VALUES (NULL,?,?,?)",
                    (session_id, comm_id, node),
                )

            # Summary
            conn.execute(
                """
                INSERT OR REPLACE INTO graph_summary VALUES
                (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    session_id,
                    len(graph.file_nodes),
                    len(graph.function_nodes),
                    len(graph.class_nodes),
                    sum(len(v) for v in graph.import_edges.values()),
                    sum(len(v) for v in graph.call_edges.values()),
                    sum(len(v) for v in graph.inherit_edges.values()),
                    sum(len(v) for v in graph.contains_edges.values()),
                    len(analysis.cycles),
                    len(analysis.function_cycles),
                    len(analysis.dead_functions),
                    len(analysis.diamond_classes),
                    analysis.modularity_score,
                    analysis.centrality_gini,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def _store_metrics(
        self,
        conn: sqlite3.Connection,
        session_id: str,
        node_type: str,
        metric_name: str,
        values: dict[str, float],
    ) -> None:
        for node_id, value in values.items():
            conn.execute(
                """
                INSERT OR REPLACE INTO node_metrics VALUES (NULL,?,?,?,?,?)
                """,
                (session_id, node_id, node_type, metric_name, value),
            )

    # ── Load Operations ─────────────────────────────────────────────────

    def load_code_graph(self, session_id: str) -> CodeGraph:
        """Load CodeGraph from database."""
        graph = CodeGraph()
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM graph_edges WHERE session_id = ?", (session_id,))
            for row in cursor:
                edge_type = row["edge_type"]
                src, tgt = row["source_node"], row["target_node"]
                tgt_type = row["target_node_type"]

                if edge_type == "IMPORTS":
                    graph.import_edges.setdefault(src, []).append(tgt)
                    graph.imported_by.setdefault(tgt, []).append(src)
                    graph.file_nodes.add(src)
                    graph.file_nodes.add(tgt)
                elif edge_type == "CALLS":
                    graph.call_edges.setdefault(src, []).append(tgt)
                    graph.called_by.setdefault(tgt, []).append(src)
                    graph.function_nodes.add(src)
                    graph.function_nodes.add(tgt)
                elif edge_type == "INHERITS":
                    graph.inherit_edges.setdefault(src, []).append(tgt)
                    graph.inherited_by.setdefault(tgt, []).append(src)
                    graph.class_nodes.add(src)
                    graph.class_nodes.add(tgt)
                elif edge_type == "CONTAINS":
                    graph.contains_edges.setdefault(src, []).append(tgt)
                    graph.contained_in[tgt] = src
                    graph.file_nodes.add(src)
                    if tgt_type == "FUNCTION":
                        graph.function_nodes.add(tgt)
                    else:
                        graph.class_nodes.add(tgt)
        return graph

    def load_graph_analysis(self, session_id: str) -> GraphAnalysis:
        """Load GraphAnalysis from database."""
        analysis = GraphAnalysis()
        with self._connect() as conn:
            # Metrics
            cursor = conn.execute("SELECT * FROM node_metrics WHERE session_id = ?", (session_id,))
            for row in cursor:
                node, ntype, metric, val = (
                    row["node_id"],
                    row["node_type"],
                    row["metric_name"],
                    row["value"],
                )
                if ntype == "FILE":
                    if metric == "pagerank":
                        analysis.pagerank[node] = val
                    elif metric == "betweenness":
                        analysis.betweenness[node] = val
                    elif metric == "in_degree":
                        analysis.in_degree[node] = int(val)
                    elif metric == "out_degree":
                        analysis.out_degree[node] = int(val)
                    elif metric == "depth":
                        analysis.depth[node] = int(val)
                    elif metric == "is_orphan":
                        analysis.is_orphan[node] = val > 0.5
                elif ntype == "FUNCTION":
                    if metric == "pagerank":
                        analysis.function_pagerank[node] = val
                    elif metric == "betweenness":
                        analysis.function_betweenness[node] = val
                    elif metric == "is_dead" and val > 0.5:
                        analysis.dead_functions.add(node)
                elif ntype == "CLASS":
                    if metric == "inheritance_depth":
                        analysis.inheritance_depth[node] = int(val)
                    elif metric == "has_diamond" and val > 0.5:
                        analysis.diamond_classes.append(node)

            # Cycles
            cursor = conn.execute(
                "SELECT * FROM cycle_members WHERE session_id = ? ORDER BY cycle_id",
                (session_id,),
            )
            file_cycles: dict[int, set[str]] = {}
            func_cycles: dict[int, set[str]] = {}
            for row in cursor:
                cid, ctype, node = row["cycle_id"], row["cycle_type"], row["node_id"]
                if ctype == "FILE":
                    file_cycles.setdefault(cid, set()).add(node)
                else:
                    func_cycles.setdefault(cid, set()).add(node)
            analysis.cycles = [CycleGroup(nodes=s) for s in file_cycles.values()]
            analysis.function_cycles = list(func_cycles.values())

            # Communities
            cursor = conn.execute(
                "SELECT * FROM community_members WHERE session_id = ?", (session_id,)
            )
            comm_map: dict[int, set[str]] = {}
            for row in cursor:
                cid, node = row["community_id"], row["node_id"]
                analysis.node_community[node] = cid
                comm_map.setdefault(cid, set()).add(node)
            analysis.communities = [Community(id=i, members=m) for i, m in sorted(comm_map.items())]

            # Summary
            cursor = conn.execute("SELECT * FROM graph_summary WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                analysis.modularity_score = row["modularity_score"]
                analysis.centrality_gini = row["centrality_gini"]

        return analysis

    def has_graph(self, session_id: str) -> bool:
        """Check if a graph exists for this session."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM graph_summary WHERE session_id = ? LIMIT 1",
                (session_id,),
            )
            return cursor.fetchone() is not None

    def get_summary(self, session_id: str) -> dict | None:
        """Get graph summary stats."""
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM graph_summary WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
