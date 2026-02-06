# Shannon Insight
**Stack:** Python + Graph Algorithms + Git + Typer (CLI)
**Status:** Implemented
**Priority:** P2

## What It Does
Multi-level codebase analysis tool using information theory, graph algorithms, and git history. Produces actionable findings -- not scores -- by cross-referencing structural dependencies, temporal co-change patterns, per-file complexity signals, and spectral graph analysis. Named after Claude Shannon.

Published on PyPI as `shannon-codebase-insight`.

## Current State
### Working Features
- **Scanning Layer:** Language-specific scanners for Python, Go, TypeScript, JavaScript, Java, Rust, Ruby, C/C++ with auto-detection
- **InsightKernel (Blackboard Architecture):**
  - Analyzers: StructuralAnalyzer (dependency graph, PageRank, SCC, Louvain), PerFileAnalyzer (5 primitives), TemporalAnalyzer (git co-change, churn), SpectralAnalyzer (Laplacian eigendecomposition)
  - Finders: HighRiskHub, HiddenCoupling, GodFile, UnstableFile, BoundaryMismatch, DeadDependency
- **CLI Commands:**
  - `shannon-insight` -- full codebase analysis with grouped findings
  - `shannon-insight explain <file>` -- deep-dive on signals, findings, trends
  - `shannon-insight diff` -- compare against last snapshot
  - `shannon-insight history` -- list past analysis snapshots
  - `shannon-insight health` -- codebase health trends
  - `shannon-insight report` -- interactive HTML treemap
- **Scoping:** `--changed` (auto-detect branch base), `--since <ref>` (scope to changed files)
- **CI Integration:** `--json` output, `--fail-on any|high` exit code control
- **Persistence:** SQLite-backed snapshot history with diffing
- **Graceful Degradation:** Works with or without git (temporal findings skipped without git)

### Finding Types
| Finding | What It Detects |
|---------|----------------|
| High Risk Hub | Files that are critical and fragile -- heavily imported, complex, or frequently changed |
| Hidden Coupling | Files that always change together but have no import relationship |
| God File | Complex and unfocused files with too many responsibilities |
| Unstable File | Files that keep getting modified without stabilizing |
| Boundary Mismatch | Directories whose files are more connected to other directories |
| Dead Dependency | Import relationships where files never actually change together |

### In Progress
- Nothing actively in progress

### Known Issues
- None documented

## Key Commands
```bash
# Install
pip install shannon-codebase-insight
# or dev install
pip install -e ".[dev]"

# Analyze codebase
shannon-insight
shannon-insight -C /path/to/project

# Focus on changed files (PR review)
shannon-insight --changed

# JSON output for CI
shannon-insight --json --fail-on high

# Deep-dive
shannon-insight explain engine.py

# Health trends
shannon-insight health

# Testing
make test           # Full suite with coverage
make test-quick     # Without coverage
make format         # ruff format + auto-fix
make lint           # ruff check
make type-check     # mypy src/
make all            # format + check + test
```

## Next Steps
- [ ] Add more language scanners as needed
- [ ] Explore ML-based anomaly detection for findings
- [ ] Add GitHub Actions integration example
- [ ] Performance optimization for very large codebases (10k+ files)

## History
- 2026-02-05: Fully implemented. Published on PyPI. All six finding types working. Supports 8 programming languages.
