"""SQL-based finder implementations.

Each finder is a .sql file that queries the Parquet snapshot tables
via DuckDB to detect code quality issues.

Available SQL finders:
- high_risk_hub.sql: Central + complex + churning files
- orphan_code.sql: Files with no imports and not entry points
- hidden_coupling.sql: Co-change without structural dependency
"""

from .runner import SQLFinderRunner

__all__ = ["SQLFinderRunner"]
