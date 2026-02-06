# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Shannon Insight is a multi-level codebase analysis tool using information theory, graph algorithms, and git history. PyPI package: `shannon-codebase-insight`. CLI entry point: `shannon-insight`.

## Common Commands

```bash
# Setup
pip install -e ".[dev]"          # or: make install

# Testing
make test                        # Full suite with coverage
make test-quick                  # Without coverage
pytest tests/test_foo.py -v      # Single test file
pytest tests/ -k "test_name" -v  # Single test by name

# Code quality
make format                      # ruff format + auto-fix
make lint                        # ruff check
make type-check                  # mypy src/
make check                       # lint + type-check
make all                         # format + check + test

# Run
shannon-insight -C test_codebase
```

## Architecture

All analysis flows through a single engine: `InsightKernel` (blackboard architecture).

### Data Flow

```
ScannerFactory → FileMetrics[] → AnalysisStore (blackboard)
                                   ↑ Analyzers write signals
                                   ↓ Finders read signals
                               Finding[] → InsightResult + Snapshot
```

Key types: `FileMetrics` (scanner output), `AnalysisStore` (blackboard), `Finding` (finder output), `InsightResult` (final result), `Snapshot` (serializable state for history/diff), `ChangeScopedReport` (scoped analysis for `--changed`/`--since`).

### Scanning Layer (`scanning/`)
`scanning/factory.py` creates language-specific scanners (Python, Go, TypeScript, JavaScript, Java, Rust, Ruby, C/C++) defined in `scanning/languages.py`. Scanners produce `FileMetrics` (in `scanning/models.py`). `UniversalScanner` auto-detects language.

### InsightKernel (`insights/kernel.py`)
Orchestrates a **blackboard architecture**:

1. **Analyzers** fill an `AnalysisStore` (blackboard) with signals. Each declares `requires`/`provides` and runs in topological order:
   - `StructuralAnalyzer` -> dependency graph, PageRank, SCC, Louvain communities
   - `PerFileAnalyzer` -> the 5 primitives (compression, centrality, volatility, coherence, cognitive load)
   - `TemporalAnalyzer` -> git co-change matrix, churn trajectories
   - `SpectralAnalyzer` -> Laplacian eigendecomposition

2. **Finders** read the store and produce evidence-backed `Finding` objects. Each declares required signals and is skipped if unavailable (graceful degradation when git is absent):
   - HighRiskHub, HiddenCoupling, GodFile, UnstableFile, BoundaryMismatch, DeadDependency

### CLI Layer
Built on **Typer** (wraps Click). The main callback in `cli/analyze.py` handles `-C/--path` and stores it in `ctx.obj["path"]` for subcommands. Uses `click.Choice` via `click_type=` for `--fail-on` validation.

```
shannon-insight                        # Main analysis (InsightKernel)
shannon-insight explain <file>         # Deep-dive on a specific file
shannon-insight diff                   # Compare snapshots
shannon-insight history                # List past snapshots
shannon-insight health                 # Codebase health trends
shannon-insight report                 # HTML treemap report
```

Key flags: `--changed` (auto-detect branch base), `--since <ref>` (scope to changed files), `--json`, `--verbose`, `--save`, `--fail-on any|high`.

### Structural Analysis (`graph/`)
Dependency graph construction (`builder.py`), graph algorithms (`algorithms.py` — centrality, SCC, blast radius, Louvain), and per-file/module measurements (`engine.py`).

### Signal Computation (`signals/`)
Per-file quality primitives (compression, centrality, volatility, coherence, cognitive load). Plugin-based: each primitive in `signals/plugins/`. `Primitives` dataclass in `signals/models.py`.

### Persistence (`persistence/`)
SQLite-backed history (`database.py`), snapshot capture/models (`capture.py`, `models.py`), reading/writing (`reader.py`, `writer.py`), snapshot diffing (`diff_engine.py`, `diff_models.py`), and change-scoped analysis (`scope.py`).

### Supporting Modules
- **`math/`**: Core algorithms (entropy, compression, Gini, graph algorithms, robust statistics, signal fusion)
- **`temporal/`**: Git log parsing (`git_extractor.py`), co-change matrix, churn trajectory classification
- **`cli/formatters/`**: Output formatting base classes (legacy formatters)
- **`config.py`**: Pydantic-based settings, overridable via `shannon-insight.toml` or `SHANNON_*` env vars

## Code Conventions

- Python 3.9+ target, type hints on functions
- Ruff for linting/formatting (line length 100)
- Mypy for type checking (ignores sklearn, diskcache, typer, rich)
- `snake_case` for functions/variables, `PascalCase` for classes
- Protocol classes for plugin interfaces (`Analyzer`, `Finder`, `Scanner`)
- `--save` is opt-in (off by default) — bare `shannon-insight` produces no `.shannon/` side effects
- Default log level is WARNING — scanner/analyzer noise suppressed unless `--verbose`

## Adding a New Language Scanner

1. Create scanner class in `src/shannon_insight/scanning/`
2. Register in `scanning/__init__.py`
3. Add auto-detection in `scanning/factory.py`
4. Add entry point in `pyproject.toml` under `[project.entry-points."shannon_insight.languages"]`

## Adding a New Primitive

1. Create plugin in `src/shannon_insight/signals/plugins/`
2. Add field to `Primitives` dataclass in `signals/models.py`
3. Register in `signals/registry.py`

## Adding a New Insight Finder

1. Create finder in `src/shannon_insight/insights/finders/`
2. Implement the `Finder` protocol: declare `requires` (store signals needed) and `find(store) -> list[Finding]`
3. Register in `InsightKernel`
