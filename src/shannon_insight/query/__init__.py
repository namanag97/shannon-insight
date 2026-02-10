"""DuckDB query layer for reading Parquet snapshots.

Provides SQL-based access to analysis data stored in Parquet files,
replacing the in-memory blackboard pattern for reads.
"""

from .engine import QueryEngine

__all__ = ["QueryEngine"]
