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
shannon-insight test_codebase/complexity_demo --language python --top 10
```

## Architecture

The codebase has three analysis pipelines, all starting from a shared scanning layer:

### Scanning Layer
`core/scanner_factory.py` creates language-specific scanners (Python, Go, TypeScript, JavaScript, Java, Rust, Ruby, C/C++) defined in `analyzers/languages.py`. Scanners produce `FileMetrics` (lines, tokens, imports, complexity). `UniversalScanner` auto-detects language.

### Pipeline 1: Per-File Primitives (`shannon-insight .`)
`core/analyzer.py` → `core/pipeline.py` → `primitives/extractor.py`

Computes 5 orthogonal quality metrics per file via a plugin system (`primitives/plugins/`):
- Compression complexity (Kolmogorov via zlib)
- Network centrality (PageRank)
- Churn volatility
- Semantic coherence (identifier clustering entropy)
- Cognitive load (complexity x nesting x Gini)

Signals are fused with configurable weights, anomalies flagged via z-score.

### Pipeline 2: Insight Engine (`shannon-insight . insights`)
`insights/kernel.py` orchestrates a **blackboard architecture**:

1. **Analyzers** fill an `AnalysisStore` (blackboard) with signals. Each declares `requires`/`provides` and runs in topological order:
   - `StructuralAnalyzer` → dependency graph, PageRank, SCC, Louvain communities
   - `PerFileAnalyzer` → the 5 primitives above
   - `TemporalAnalyzer` → git co-change matrix, churn trajectories
   - `SpectralAnalyzer` → Laplacian eigendecomposition

2. **Finders** read the store and produce evidence-backed `Finding` objects. Each declares required signals and is skipped if unavailable (graceful degradation when git is absent):
   - HighRiskHub, HiddenCoupling, GodFile, UnstableFile, BoundaryMismatch, DeadDependency

### Pipeline 3: Structural Analysis (`shannon-insight . structure`)
`analysis/engine.py` runs a DAG of graph algorithms: dependency graph construction, PageRank, betweenness centrality, Tarjan's SCC, Louvain modularity, module cohesion/coupling measurement.

### Supporting Modules
- **`math/`**: Core algorithms (entropy, compression, Gini, graph algorithms, robust statistics, signal fusion)
- **`temporal/`**: Git log parsing (`git_extractor.py`), co-change matrix, churn trajectory classification
- **`formatters/`**: Output backends (Rich, JSON, CSV, quiet, GitHub Actions annotations)
- **`storage/`**: SQLite-backed history for snapshot persistence
- **`snapshot/`**: Capture/compare analysis state over time
- **`config.py`**: Pydantic-based settings, overridable via `shannon-insight.toml` or `SHANNON_*` env vars

## Code Conventions

- Python 3.9+ target, type hints on functions
- Ruff for linting/formatting (line length 100)
- Mypy for type checking (ignores sklearn, diskcache, typer, rich)
- `snake_case` for functions/variables, `PascalCase` for classes
- Protocol classes for plugin interfaces (`Analyzer`, `Finder`, `Scanner`)

## Adding a New Language Scanner

1. Create scanner class in `src/shannon_insight/analyzers/`
2. Register in `analyzers/__init__.py`
3. Add auto-detection in `core/scanner_factory.py`
4. Add entry point in `pyproject.toml` under `[project.entry-points."shannon_insight.languages"]`

## Adding a New Primitive

1. Create plugin in `src/shannon_insight/primitives/plugins/`
2. Add field to `Primitives` dataclass in `models.py`
3. Register in `primitives/registry.py`
4. Update fusion weights in `config.py`
5. Add recommendations in `primitives/recommendations.py`

## Adding a New Insight Finder

1. Create finder in `src/shannon_insight/insights/finders/`
2. Implement the `Finder` protocol: declare `requires` (store signals needed) and `find(store) -> list[Finding]`
3. Register in `InsightKernel`
