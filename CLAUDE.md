# CLAUDE.md

**Shannon Insight**: Codebase analysis tool using information theory, graph algorithms, and git history.
PyPI: `shannon-codebase-insight` | CLI: `shannon-insight`

## Quick Reference

```bash
# Setup & Quality
make install                     # pip install -e ".[dev]"
make all                         # format + check + test

# Testing
make test                        # Full suite with coverage
pytest tests/test_foo.py -v      # Single file
pytest tests/ -k "test_name" -v  # Single test

# CLI
shannon-insight -C <path>        # Main analysis
shannon-insight explain <file>   # File deep-dive
shannon-insight diff/history     # Snapshot operations
shannon-insight health/report    # Health trends / HTML report
```

Key flags: `--changed`, `--since <ref>`, `--json`, `--verbose`, `--save`, `--fail-on any|high`

## Architecture

**Core**: `InsightKernel` orchestrates blackboard pattern:
```
ScannerFactory → FileMetrics[] → AnalysisStore (blackboard)
                                   ↑ Analyzers write signals
                                   ↓ Finders read signals
                               Finding[] → InsightResult + Snapshot
```

**Key Types**: `FileMetrics`, `AnalysisStore`, `Finding`, `InsightResult`, `Snapshot`, `ChangeScopedReport`

### Core Modules

**`scanning/`**: `ScannerFactory` (factory.py) creates language scanners (Python, Go, TS, JS, Java, Rust, Ruby, C/C++) → `FileMetrics`. `UniversalScanner` auto-detects.

**`insights/kernel.py`**: Blackboard orchestrator
- **Analyzers** (topo-sorted): `StructuralAnalyzer` (graph, PageRank, SCC, Louvain), `PerFileAnalyzer` (5 primitives), `TemporalAnalyzer` (co-change), `SpectralAnalyzer` (Laplacian)
- **Finders** (graceful degradation): HighRiskHub, HiddenCoupling, GodFile, UnstableFile, BoundaryMismatch, DeadDependency

**`graph/`**: Dependency graph (builder.py), algorithms (centrality, SCC, Louvain), measurements (engine.py)

**`signals/`**: Plugin-based primitives (compression, centrality, volatility, coherence, cognitive load). Plugins in `signals/plugins/`, dataclass in models.py

**`persistence/`**: SQLite history (database.py), snapshots (capture.py, models.py), diff (diff_engine.py), scoping (scope.py)

**`temporal/`**: Git extraction (git_extractor.py), co-change matrix, churn classification

**`config.py`**: Pydantic settings, overridable via `shannon-insight.toml` or `SHANNON_*` env vars

**`cli/`**: Typer-based. Main callback (analyze.py) handles `-C/--path` → `ctx.obj["path"]`

## Conventions

- Python 3.9+, type hints, `snake_case`/`PascalCase`
- Ruff (line 100), mypy (ignores: sklearn, diskcache, typer, rich)
- Protocol interfaces: `Analyzer`, `Finder`, `Scanner`
- `--save` opt-in (default: no `.shannon/` side effects)
- Log level WARNING (use `--verbose` for debug)

## Extension Points

**Language Scanner**: Class in `scanning/` → register in `__init__.py`, `factory.py` → add entry point in `pyproject.toml`

**Primitive**: Plugin in `signals/plugins/` → add field to `Primitives` (models.py) → register in `registry.py`

**Finder**: Class in `insights/finders/` → implement `Finder` protocol (`requires`, `find(store)`) → register in `InsightKernel`
