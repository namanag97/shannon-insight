# Shannon Insight

[![CI](https://github.com/namanag97/shannon-insight/actions/workflows/ci.yml/badge.svg)](https://github.com/namanag97/shannon-insight/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/shannon-insight)](https://pypi.org/project/shannon-insight/)
[![Python](https://img.shields.io/pypi/pyversions/shannon-insight)](https://pypi.org/project/shannon-insight/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Multi-level codebase analysis using information theory, graph algorithms, and git history. Produces actionable insights — not scores — by cross-referencing structural dependencies, temporal co-change patterns, per-file complexity signals, and spectral graph analysis.

Named after Claude Shannon, father of information theory.

## Quick Start

```bash
pip install shannon-insight

# Actionable insights: what to fix and why
shannon-insight . insights

# Structural analysis: dependencies, communities, cycles
shannon-insight . structure

# Per-file quality primitives
shannon-insight .
```

## Insight Engine (`insights` command)

The `insights` command cross-references **four signal categories** to find problems no single metric can catch:

```bash
shannon-insight . insights
```

```
SHANNON INSIGHT — 41 files, 14 modules, 688 commits analyzed

1. HIGH RISK HUB
   src/click/core.py
   • harder to understand than 98% of files in this codebase
   • changed 136 times in recent history
   → This file is both complex and frequently modified. Each change carries
     higher risk of introducing bugs. Extract the parts that change most
     often into a separate, well-tested module.

2. HIDDEN COUPLING
   src/click/_termui_impl.py ↔ src/click/_winconsole.py
   • when _winconsole.py changed, _termui_impl.py also changed 9 of 11 times (82%)
   • 17.6x more often than expected by chance
   • neither file imports the other
   → These files always change together but share no import. They likely share
     an implicit contract. Make this explicit: either add an import, or extract
     the shared concept into a common module.
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
   - *Structural*: dependency graph, PageRank, blast radius, communities, cycles (existing engine)
   - *Per-file*: cognitive load, semantic coherence, compression complexity, centrality, volatility
   - *Temporal*: git history → co-change matrix (lift + confidence) + churn trajectories
   - *Spectral*: Laplacian eigenvalues, Fiedler value (algebraic connectivity)
3. **Find** — six finders read from the store and produce evidence-backed findings
4. **Rank** — findings sorted by severity (base priority × signal strength), capped at `--max-findings`

Analyzers and finders declare `requires` and `provides` sets. The kernel topologically sorts analyzers and skips finders whose required signals are unavailable (graceful degradation).

### Options

```bash
shannon-insight . insights                    # default: rich output, top 10 findings
shannon-insight . insights --format json      # machine-readable JSON
shannon-insight . insights --verbose          # show raw signal values
shannon-insight . insights --max-findings 20  # show more findings
shannon-insight . insights --language python  # analyze only Python files
```

## Structural Analysis (`structure` command)

Builds a multi-level model of your codebase using graph theory:

```bash
shannon-insight . structure
```

| Level | What | Math |
|-------|------|------|
| Dependency graph | Which files depend on which | Import resolution, directed graph |
| Centrality | Which files are critical hubs | PageRank, betweenness centrality |
| Blast radius | What breaks if you change a file | Transitive closure on reverse graph |
| Cycles | Circular dependencies | Tarjan's SCC algorithm |
| Communities | Natural clusters in the codebase | Louvain modularity optimization |
| Module analysis | Cohesion/coupling per directory | Internal vs external edge density |
| Boundary alignment | Do directories match actual structure? | Declared vs discovered communities |
| Complexity outliers | Files with extreme measurements | Median Absolute Deviation (robust) |

Output shows only issues — circular dependencies, high-impact files, boundary mismatches, complexity outliers. Use `--format json` for full structured data.

## Per-File Quality Primitives

The default `shannon-insight .` command computes **5 orthogonal quality primitives** per file:

| Primitive | What it measures | High means |
|-----------|-----------------|------------|
| **Compression Complexity** | Kolmogorov complexity (via zlib) | Dense/unique code |
| **Network Centrality** | PageRank on dependency graph | Critical hub |
| **Churn Volatility** | File modification recency | Recently changed / unstable |
| **Semantic Coherence** | Identifier-based responsibility focus | Low: mixed concerns |
| **Cognitive Load** | Concepts × complexity × Gini inequality | Overloaded file |

## Output Formats

```bash
# Rich terminal output (default)
shannon-insight .

# Machine-readable JSON
shannon-insight . --format json

# Pipe-friendly CSV
shannon-insight . --format csv

# Just file paths (one per line)
shannon-insight . --format quiet

# Deep-dive on a specific file
shannon-insight . --explain complex.go

# Export to file
shannon-insight . --output report.json
```

## CI Integration

```bash
# Fail if any file scores above 2.0
shannon-insight . --format quiet --fail-above 2.0
```

```yaml
# GitHub Actions
- name: Code quality gate
  run: shannon-insight . --fail-above 2.0 --format quiet
```

## Configuration

Create `shannon-insight.toml` in your project root:

```toml
z_score_threshold = 1.5
fusion_weights = [0.2, 0.25, 0.2, 0.15, 0.2]
exclude_patterns = ["*_test.go", "vendor/*", "node_modules/*"]
max_file_size_mb = 10.0
enable_cache = true

# Insight engine settings
git_max_commits = 5000          # max git commits to analyze (0 = no limit)
git_min_commits = 10            # min commits for temporal analysis
insights_max_findings = 10      # max findings in insights command
```

Or use environment variables with `SHANNON_` prefix:

```bash
export SHANNON_Z_SCORE_THRESHOLD=2.0
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

Language is auto-detected by default. Override with `--language`.

## Architecture

```
shannon_insight/
├── cli/               # CLI commands (analyze, structure, insights, baseline, cache)
├── core/              # Orchestration, pipeline, scanner factory
├── analysis/          # Multi-level structural analysis engine
├── analyzers/         # Language-specific scanners
├── primitives/        # Plugin-based per-file quality primitives
├── insights/          # Insight engine (blackboard architecture)
│   ├── analyzers/     # Signal producers (structural, per-file, temporal, spectral)
│   └── finders/       # Finding producers (6 finding types)
├── temporal/          # Git history extraction, co-change, churn analysis
├── math/              # Entropy, compression, graph algorithms, Gini, coherence
├── formatters/        # Output formatting (rich, json, csv, quiet, github)
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
