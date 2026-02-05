# Shannon Insight

[![CI](https://github.com/namanag97/shannon-insight/actions/workflows/ci.yml/badge.svg)](https://github.com/namanag97/shannon-insight/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/shannon-insight)](https://pypi.org/project/shannon-insight/)
[![Python](https://img.shields.io/pypi/pyversions/shannon-insight)](https://pypi.org/project/shannon-insight/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Multi-level codebase analysis using information theory, graph algorithms, and git history. Produces actionable insights — not scores — by cross-referencing structural dependencies, temporal co-change patterns, per-file complexity signals, and spectral graph analysis.

Named after Claude Shannon, father of information theory.

## Quick Start

```bash
pip install shannon-codebase-insight

# Analyze your codebase
shannon-insight

# Analyze a specific directory
shannon-insight -C /path/to/project

# Focus on changed files (PR review)
shannon-insight --changed

# JSON output for CI
shannon-insight --json --fail-on high

# Deep-dive on a file
shannon-insight explain engine.py

# Health trends
shannon-insight health
```

## Commands

```
shannon-insight                    # Analyze codebase (grouped findings)
shannon-insight explain <file>     # Deep-dive: signals, findings, trends
shannon-insight diff               # Compare against last snapshot
shannon-insight history            # List past analysis snapshots
shannon-insight health             # Codebase health trends
shannon-insight report             # Interactive HTML treemap
```

## Options

```
-C, --path PATH     Project root (default: current directory)
--changed           Scope to changed files (auto-detects branch)
--since REF         Scope to files changed since a git ref
--json              Machine-readable JSON output
--verbose           Show detailed evidence per finding
--save              Save snapshot for history tracking
--fail-on LEVEL     Exit 1 if findings at level: any | high
```

## How It Works

Shannon Insight cross-references **four signal categories** to find problems no single metric can catch:

```bash
shannon-insight
```

```
SHANNON INSIGHT — 41 files, 14 modules, 688 commits analyzed

HIGH RISK HUBS — 2 files
  These files have many dependents. A bug ripples widely.

  src/click/core.py
    harder to understand than 98% of files in this codebase
  src/click/decorators.py
    changed 91 times in recent history

  → Split into smaller modules or add interfaces to reduce coupling.

HIDDEN COUPLING — 1 file
  These file pairs always change together but share no import.

  src/click/_termui_impl.py ↔ src/click/_winconsole.py
    when _winconsole.py changed, _termui_impl.py also changed 9 of 11 times (82%)

  → Make the dependency explicit or extract shared logic.
```

Works **with or without git**. Without git, temporal findings (hidden coupling, unstable files) are skipped; structural and per-file findings still work.

### Finding Types

| Finding | What it detects | Signals used |
|---------|----------------|--------------|
| **High Risk Hub** | Files that are both critical and fragile — heavily imported, complex, or frequently changed | PageRank, blast radius, cognitive load, churn |
| **Hidden Coupling** | Files that always change together but have no import relationship | Git co-change lift + confidence, dependency graph |
| **God File** | Files that are complex and unfocused — too many responsibilities | Cognitive load, semantic coherence |
| **Unstable File** | Files that keep getting modified without stabilizing | Churn trajectory (regression slope + coefficient of variation) |
| **Boundary Mismatch** | Directories whose files are more connected to other directories | Louvain communities vs directory structure |
| **Dead Dependency** | Import relationships where the files never actually change together | Dependency graph + co-change absence |

### How It Works

The insight engine uses a **blackboard architecture**:

```
Scanner → AnalysisStore ← Analyzers fill it → Finders read it → Ranked Findings
```

1. **Scan** — language-aware file parsing (Python, Go, TypeScript, Java, Rust, Ruby, C/C++)
2. **Analyze** — four analyzers populate a shared store:
   - *Structural*: dependency graph, PageRank, blast radius, communities, cycles
   - *Per-file*: cognitive load, semantic coherence, compression complexity, centrality, volatility
   - *Temporal*: git history → co-change matrix (lift + confidence) + churn trajectories
   - *Spectral*: Laplacian eigenvalues, Fiedler value (algebraic connectivity)
3. **Find** — six finders read from the store and produce evidence-backed findings
4. **Rank** — findings sorted by severity, grouped by type

Analyzers and finders declare `requires` and `provides` sets. The kernel topologically sorts analyzers and skips finders whose required signals are unavailable (graceful degradation).

## CI Integration

```bash
# Fail if any high-severity finding exists
shannon-insight --fail-on high

# Fail if any finding exists
shannon-insight --fail-on any
```

```yaml
# GitHub Actions
- name: Code quality gate
  run: shannon-insight --fail-on high
```

## Snapshot History

Use `--save` to record analysis snapshots for tracking over time.

```bash
shannon-insight --save              # Analyze and save snapshot
shannon-insight history             # List past snapshots
shannon-insight diff                # Compare current vs last snapshot
shannon-insight diff --pin          # Pin current as baseline
shannon-insight diff --baseline     # Compare against baseline
shannon-insight health              # Health trends over time
shannon-insight report              # Interactive HTML treemap
```

## Configuration

Create `shannon-insight.toml` in your project root:

```toml
exclude_patterns = ["*_test.go", "vendor/*", "node_modules/*"]
max_file_size_mb = 10.0
enable_cache = true

# Insight engine settings
git_max_commits = 5000          # max git commits to analyze (0 = no limit)
git_min_commits = 10            # min commits for temporal analysis
insights_max_findings = 50      # max findings
```

Or use environment variables with `SHANNON_` prefix:

```bash
export SHANNON_GIT_MAX_COMMITS=10000
```

## Supported Languages

- **Python** — `.py` files
- **Go** — `.go` files
- **TypeScript/React** — `.ts`, `.tsx` files
- **JavaScript** — `.js`, `.jsx` files
- **Java** — `.java` files
- **Rust** — `.rs` files
- **Ruby** — `.rb` files
- **C/C++** — `.c`, `.cpp`, `.cc`, `.h` files

Language is auto-detected.

## Architecture

```
shannon_insight/
├── cli/               # CLI commands (analyze, explain, diff, health, history, report)
├── core/              # Scanner factory
├── analysis/          # Multi-level structural analysis engine
├── analyzers/         # Language-specific scanners
├── primitives/        # Plugin-based per-file quality primitives
├── insights/          # Insight engine (blackboard architecture)
│   ├── analyzers/     # Signal producers (structural, per-file, temporal, spectral)
│   └── finders/       # Finding producers (6 finding types)
├── temporal/          # Git history extraction, co-change, churn analysis
├── math/              # Entropy, compression, graph algorithms, Gini, coherence
├── snapshot/          # Immutable analysis snapshots
├── storage/           # SQLite-backed snapshot history
├── diff/              # Snapshot comparison and change-scoped analysis
├── formatters/        # Output formatting
└── exceptions/        # Exception hierarchy
```

See [docs/INSIGHT_ENGINE.md](docs/INSIGHT_ENGINE.md) for the full insight engine design.

## Development

```bash
git clone https://github.com/namanag97/shannon-insight.git
cd shannon-insight
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

make test          # Run tests with coverage
make lint          # Run ruff linter
make format        # Format with ruff
make type-check    # Run mypy
make all           # Format + lint + type-check + test
```

## License

MIT License — see [LICENSE](LICENSE)

## Credits

Created by Naman Agarwal. Built on Claude Shannon's information theory, PageRank (Page & Brin), Louvain community detection (Blondel et al.), Tarjan's SCC algorithm, Kolmogorov complexity, and Laplacian spectral analysis (Fiedler).
