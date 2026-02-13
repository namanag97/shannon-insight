"""DuckDB query engine that loads Parquet files for SQL-based analysis.

This is the read-side of the tensor DB migration. It provides a DuckDB
connection with all Parquet tables registered as views, enabling:
- SQL-based finder implementations
- Ad-hoc queries against analysis data
- Percentile computation via window functions (not stored, computed on read)

Requires: pip install shannon-codebase-insight[tensordb]
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _import_duckdb():
    """Lazy import duckdb."""
    try:
        import duckdb

        return duckdb
    except ImportError:
        raise ImportError(
            "duckdb is required for the query engine. "
            "Install with: pip install shannon-codebase-insight[tensordb]"
        ) from None


class QueryEngine:
    """DuckDB-based query engine over Parquet snapshot files.

    Usage::

        engine = QueryEngine("/path/to/project")
        engine.load()  # registers Parquet files as views

        # Run arbitrary SQL
        results = engine.execute("SELECT * FROM file_signals WHERE pagerank > 0.01")

        # Get the latest snapshot ID
        sid = engine.latest_snapshot_id()

        # Query with percentiles (computed on-the-fly)
        results = engine.execute('''
            SELECT file_path, pagerank,
                   PERCENT_RANK() OVER (ORDER BY pagerank) as pagerank_pctl
            FROM file_signals
            WHERE snapshot_id = ?
        ''', [sid])
    """

    def __init__(self, project_root: str) -> None:
        self.parquet_dir = Path(project_root) / ".shannon" / "parquet"
        self._con: Any | None = None  # duckdb.DuckDBPyConnection (lazy import)
        self._loaded = False

    @property
    def available(self) -> bool:
        """Return True if Parquet data exists and can be loaded."""
        if not self.parquet_dir.exists():
            return False
        return any(self.parquet_dir.glob("*.parquet"))

    def load(self) -> None:
        """Create DuckDB connection and register all Parquet files as views.

        Each .parquet file becomes a view named after its stem:
        - file_signals.parquet -> file_signals
        - edges.parquet -> edges
        - etc.
        """
        if self._loaded and self._con is not None:
            return

        duckdb = _import_duckdb()
        self._con = duckdb.connect(database=":memory:")

        table_files = {
            "snapshots": "snapshots.parquet",
            "file_signals": "file_signals.parquet",
            "module_signals": "module_signals.parquet",
            "global_signals": "global_signals.parquet",
            "edges": "edges.parquet",
            "findings": "findings.parquet",
        }

        registered = []
        for view_name, filename in table_files.items():
            parquet_path = self.parquet_dir / filename
            if parquet_path.exists():
                # Use CREATE VIEW so data is always read fresh from Parquet
                self._con.execute(
                    f"CREATE VIEW {view_name} AS SELECT * FROM read_parquet('{parquet_path}')"
                )
                registered.append(view_name)
            else:
                # Create empty view so SQL queries don't fail on missing tables
                self._create_empty_view(view_name)

        self._loaded = True
        logger.info("QueryEngine loaded %d views from %s", len(registered), self.parquet_dir)

    def _create_empty_view(self, view_name: str) -> None:
        """Create an empty view for a missing table to avoid SQL errors."""
        # Define minimal schemas for empty tables
        schemas = {
            "snapshots": "snapshot_id VARCHAR, timestamp VARCHAR",
            "file_signals": "snapshot_id VARCHAR, file_path VARCHAR",
            "module_signals": "snapshot_id VARCHAR, module_path VARCHAR",
            "global_signals": "snapshot_id VARCHAR",
            "edges": "snapshot_id VARCHAR, source VARCHAR, target VARCHAR, space VARCHAR, weight DOUBLE",
            "findings": (
                "snapshot_id VARCHAR, finding_type VARCHAR, identity_key VARCHAR, "
                "severity DOUBLE, title VARCHAR, files VARCHAR, evidence VARCHAR, "
                "suggestion VARCHAR, confidence DOUBLE, effort VARCHAR, scope VARCHAR"
            ),
        }
        schema = schemas.get(view_name, "dummy INTEGER")
        assert self._con is not None
        self._con.execute(f"CREATE VIEW {view_name} AS SELECT * FROM (SELECT {schema}) WHERE 1=0")

    @property
    def con(self):
        """Get the DuckDB connection, loading if needed."""
        if not self._loaded:
            self.load()
        return self._con

    def execute(self, sql: str, params: list | dict | None = None) -> list[tuple]:
        """Execute SQL and return results as list of tuples.

        Parameters
        ----------
        sql:
            SQL query. Can reference views: file_signals, edges, findings, etc.
            Use ``?`` for positional params (list) or ``$name`` for named params (dict).
        params:
            Positional (list) or named (dict) parameters for parameterized queries.

        Returns
        -------
        list[tuple]
            Query results.
        """
        if not self._loaded:
            self.load()
        assert self._con is not None

        if params:
            result = self._con.execute(sql, params)
        else:
            result = self._con.execute(sql)
        return list(result.fetchall())

    def execute_dict(self, sql: str, params: list | dict | None = None) -> list[dict[str, Any]]:
        """Execute SQL and return results as list of dicts.

        Parameters
        ----------
        sql:
            SQL query. Use ``?`` for positional params or ``$name`` for named params.
        params:
            Positional (list) or named (dict) parameters.

        Returns
        -------
        list[dict]
            Each dict maps column name -> value.
        """
        if not self._loaded:
            self.load()
        assert self._con is not None

        if params:
            result = self._con.execute(sql, params)
        else:
            result = self._con.execute(sql)

        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def latest_snapshot_id(self) -> str | None:
        """Return the most recent snapshot_id, or None if no snapshots exist."""
        rows = self.execute("SELECT snapshot_id FROM snapshots ORDER BY timestamp DESC LIMIT 1")
        if rows:
            return str(rows[0][0])
        return None

    def close(self) -> None:
        """Close the DuckDB connection."""
        if self._con is not None:
            self._con.close()
            self._con = None
            self._loaded = False

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, *args):
        self.close()
