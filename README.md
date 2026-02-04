# Shannon Insight

[![CI](https://github.com/namanagarwal/shannon-insight/actions/workflows/ci.yml/badge.svg)](https://github.com/namanagarwal/shannon-insight/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/shannon-insight)](https://pypi.org/project/shannon-insight/)
[![Python](https://img.shields.io/pypi/pyversions/shannon-insight)](https://pypi.org/project/shannon-insight/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Multi-level codebase analysis using information theory and graph algorithms. Produces structural intelligence — dependency graphs, community detection, blast radius, cycle detection — not arbitrary scores. Named after Claude Shannon, father of information theory.

## Quick Start

```bash
pip install shannon-insight

# Structural analysis: dependencies, communities, cycles, blast radius
shannon-insight . structure

# Structural analysis as JSON (for AI agent consumption)
shannon-insight . structure --format json

# Per-file quality primitives (original analysis)
shannon-insight /path/to/codebase
```

## Structural Analysis (new)

The `structure` command builds a multi-level model of your codebase using graph theory and information theory:

```bash
shannon-insight . structure
```

**What it computes:**

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

**Output shows only issues** — no noise, no scores, just structural facts:

- Circular dependencies (real cycles, not Python package init patterns)
- High-impact files (blast radius > 30% of codebase)
- Boundary mismatches (directories that don't match coupling structure)
- Top complexity outliers

Use `--format json` to get the full structured data for piping to an AI agent.

## Per-File Quality Primitives

The default `shannon-insight .` command computes **5 orthogonal quality primitives** per file:

| Primitive | What it measures | High means |
|-----------|-----------------|------------|
| **Compression Complexity** | Kolmogorov complexity (via zlib) | Dense/unique code |
| **Network Centrality** | PageRank on dependency graph | Critical hub |
| **Churn Volatility** | File modification recency | Recently changed / unstable |
| **Semantic Coherence** | Identifier-based responsibility focus | Low: mixed concerns |
| **Cognitive Load** | Concepts x complexity x Gini inequality | Overloaded file |

## Output Formats

```bash
# Rich terminal output (default) with summary dashboard
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

Use `--fail-above` to gate CI pipelines on code quality:

```bash
# Fail if any file scores above 2.0
shannon-insight . --format quiet --fail-above 2.0
```

Example GitHub Actions step:

```yaml
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
```

Or use environment variables with `SHANNON_` prefix:

```bash
export SHANNON_Z_SCORE_THRESHOLD=2.0
export SHANNON_ENABLE_CACHE=false
```

## CLI Options

```
Options:
  PATH                      Path to codebase directory [default: .]
  -l, --language TEXT       Language (auto, python, go, typescript, react, javascript)
  -t, --top INTEGER         Number of top files to display [1-1000]
  -o, --output FILE         Export JSON report to file
  -f, --format TEXT         Output format: rich, json, csv, quiet
  -e, --explain TEXT        Deep-dive on matching file(s)
  --fail-above FLOAT        CI gate: exit 1 if max score exceeds threshold
  --threshold FLOAT         Z-score threshold for anomaly detection
  -c, --config FILE         TOML configuration file
  -v, --verbose             Enable DEBUG logging
  -q, --quiet               Suppress all but ERROR logging
  --no-cache                Disable caching
  --clear-cache             Clear cache before running
  -w, --workers INTEGER     Parallel workers [1-32]
  --version                 Show version and exit

Commands:
  structure     Structural analysis: dependencies, communities, cycles
  baseline      Save/show analysis baseline
  cache-info    Show cache statistics
  cache-clear   Clear analysis cache
```

## Supported Languages

- **Python** - `.py` files
- **Go** - `.go` files
- **TypeScript/React** - `.ts`, `.tsx` files
- **JavaScript** - `.js`, `.jsx` files (uses TypeScript scanner)

Language is auto-detected by default. Override with `--language`.

## How It Works

### Structural Analysis (`structure` command)

```
Parse → Constructs + Relationships
     → Build Dependency Graph
     → Graph Algorithms (PageRank, Tarjan SCC, Louvain, transitive closure)
     → Measure Constructs (compression ratio, cognitive load, Gini)
     → Measure Modules (cohesion, coupling, boundary alignment)
     → Statistical Layer (MAD-based outlier detection)
     → Structured Result Store (queryable, not scored)
```

### Per-File Analysis (default command)

```
Scanner → FileMetrics → 5 Primitives → Z-score → Fusion → Recommendations
```

See [docs/MATHEMATICAL_FOUNDATION.md](docs/MATHEMATICAL_FOUNDATION.md) for the full mathematical framework.

## Development

```bash
git clone https://github.com/namanagarwal/shannon-insight.git
cd shannon-insight
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

make test          # Run tests with coverage
make lint          # Run ruff linter
make format        # Format with ruff
make type-check    # Run mypy
make all           # Format + lint + type-check + test
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE)

## Credits

Created by Naman Agarwal. Inspired by Claude Shannon's information theory, PageRank (Page & Brin), Louvain community detection (Blondel et al.), Tarjan's SCC algorithm, and Kolmogorov complexity.
