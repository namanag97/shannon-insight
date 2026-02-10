"""SQL-based finder implementations.

Each finder is a .sql file that queries the Parquet snapshot tables
via DuckDB to detect code quality issues.

Available SQL finders (22 total):

Existing (v1 upgraded):
- high_risk_hub.sql: Central + complex + churning files
- orphan_code.sql: Files with no imports and not entry points
- hidden_coupling.sql: Co-change without structural dependency
- god_file.sql: Complex files with low coherence
- unstable_file.sql: Churning/spiking trajectory files
- boundary_mismatch.sql: Module boundary doesn't match dependencies
- dead_dependency.sql: Structural edge with zero co-change
- chronic_problem.sql: Findings persisting 3+ snapshots

AI Code Quality:
- phantom_imports.sql: Unresolved phantom imports
- hollow_code.sql: Mostly stub/empty implementations
- copy_paste_clone.sql: NCD-detected file clones
- flat_architecture.sql: No composition layer
- naming_drift.sql: Filename doesn't match content

Social / Team:
- knowledge_silo.sql: Central files with single contributor
- conway_violation.sql: Coupled modules with separate teams
- review_blindspot.sql: Central, single-owner, untested files

Architecture:
- zone_of_pain.sql: Concrete + stable modules (hard to change)
- layer_violation.sql: Backward/skip edges in layer ordering
- architecture_erosion.sql: Increasing violation rate over snapshots

Cross-Dimensional:
- weak_link.sql: Health Laplacian outlier (worse than neighbors)
- bug_attractor.sql: High fix_ratio + high centrality
- accidental_coupling.sql: Structural edge between unrelated concepts
"""

from .runner import SQLFinderRunner

__all__ = ["SQLFinderRunner"]
