# Shannon Insight

[![PyPI](https://img.shields.io/pypi/v/shannon-codebase-insight)](https://pypi.org/project/shannon-codebase-insight/)
[![Python 3.9+](https://img.shields.io/pypi/pyversions/shannon-codebase-insight)](https://pypi.org/project/shannon-codebase-insight/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Multi-signal codebase analysis using information theory, graph algorithms, and git history. Cross-references dependency graphs, temporal co-change patterns, per-file complexity signals, and spectral analysis to surface structural problems that no single metric can catch.

Shannon Insight is for teams that want evidence-backed findings about where their codebase is fragile, tangled, or siloed -- not arbitrary quality scores.

## Quick Start

```bash
pip install shannon-codebase-insight
cd your-project
shannon-insight .
```

```
✓ Analyzed 234 files in 2.1s

Moderate structural issues — 1 file needs attention

START HERE
  src/core/engine.py
  Why: Central file (blast=47) with high churn (cv=2.1) and single owner
  Data: blast=47, changes=89, cv=2.1, lines=412
  Issues: high risk hub, knowledge silo

ALSO CONSIDER
  #2  src/api/handlers.py          High coupling, 3 issues
  #3  src/models/user.py           God file, low coherence
  #4  src/utils/helpers.py         Orphan code

Patterns: 5 structural, 3 coupling, 2 churn, 1 team
```

Launch the interactive dashboard:

```bash
pip install shannon-codebase-insight[serve]
shannon-insight serve
```

## What It Finds

### Structural

| Finding | What It Detects | Severity | Example |
|---------|----------------|----------|---------|
| `god_file` | Files with too many responsibilities -- high complexity, low coherence | HIGH | `core.py` has 45 functions across 6 unrelated concerns |
| `high_risk_hub` | Central files that are also complex or churning -- a bug here ripples widely | CRITICAL | `engine.py` imported by 47 files, changed 89 times |
| `orphan_code` | Files with zero importers that may be dead code | MEDIUM | `old_handler.py` imported by nothing |
| `hollow_code` | Files with >60% stub/empty functions -- started but never finished | HIGH | `api_v2.py` has 8 of 12 functions as `pass` |
| `phantom_imports` | Imports that resolve to no file in the codebase | MEDIUM | `from .missing_module import X` |
| `dead_dependency` | Import relationships where files never co-change in git history | LOW | `A` imports `B` but they haven't changed together in 688 commits |

### Architecture

| Finding | What It Detects | Severity | Example |
|---------|----------------|----------|---------|
| `hidden_coupling` | Files that co-change together but share no import | HIGH | `cache.py` and `db.py` change together 82% of the time with no import |
| `boundary_mismatch` | Directories whose files are more connected to other directories | MEDIUM | Files in `src/api/` are more tightly coupled to `src/models/` |
| `layer_violation` | Dependencies that flow backward through architectural layers | MEDIUM | `models/` imports from `controllers/` |
| `zone_of_pain` | Modules that are both concrete and stable -- painful to change | MEDIUM | `core/` has 0.1 abstractness and 0.2 instability |
| `flat_architecture` | Codebase lacks composition layer between leaf modules | MEDIUM | All modules at depth 1 with high glue deficit |

### Stability

| Finding | What It Detects | Severity | Example |
|---------|----------------|----------|---------|
| `unstable_file` | Files with increasing churn that aren't stabilizing | HIGH | `handlers.py` trajectory: CHURNING, cv=2.3 |
| `chronic_problem` | Findings that persist across 3+ analysis snapshots | HIGH | `god_file` on `engine.py` persisting 5 snapshots |
| `thrashing_code` | Files with erratic, spiking change patterns | HIGH | `config.py` has SPIKING trajectory with cv=3.1 |
| `bug_magnet` | Files where >40% of commits mention "fix" | HIGH | `parser.py` fix_ratio=0.62, 45 changes |

### Team

| Finding | What It Detects | Severity | Example |
|---------|----------------|----------|---------|
| `knowledge_silo` | Central files owned by a single contributor | HIGH | `auth.py` bus_factor=1.0, PageRank top 5% |
| `review_blindspot` | High-centrality files with single owner and no tests | HIGH | `billing.py` imported by 30 files, 1 author, no test file |
| `truck_factor` | Files where only one person has ever committed | HIGH | `scheduler.py` sole author, blast_radius=12 |
| `conway_violation` | Structurally-coupled modules maintained by different teams | MEDIUM | `api/` and `models/` tightly coupled but 0% author overlap |

### Code Quality

| Finding | What It Detects | Severity | Example |
|---------|----------------|----------|---------|
| `copy_paste_clone` | File pairs with high content similarity (NCD < 0.3) | MEDIUM | `handler_v1.py` and `handler_v2.py` are 85% similar |
| `incomplete_implementation` | Files with multiple incomplete signals (stubs + phantom imports) | HIGH | `service.py` has 4 stubs and 2 missing imports |
| `naming_drift` | Files whose names don't match their actual content | LOW | `utils.py` contains only database connection logic |
| `directory_hotspot` | Directories where most files are high-risk or churning | HIGH | `src/api/` has 5 of 7 files in top risk quartile |

Also: `weak_link` (file worse than its graph neighborhood), `bug_attractor` (central file with high fix ratio), `accidental_coupling` (imports between unrelated files), `architecture_erosion` (violation rate increasing over time), `duplicate_incomplete` (cloned files that are both incomplete).

## How It Works

Shannon Insight scans source files for structural metrics (LOC, function count, nesting depth, imports), builds a dependency graph, and runs PageRank, strongly connected components, and Louvain community detection. If git history is available, it extracts co-change patterns, churn trajectories, author entropy, and fix ratios.

These raw signals are fused through percentile normalization and weighted combination into per-file risk scores. A health Laplacian identifies files that are worse than their graph neighbors. 28 finders read from the unified signal field and produce evidence-backed findings ranked by severity.

The system works with or without git. Without git, temporal findings (hidden coupling, unstable files, team finders) are skipped; structural and per-file findings still work. See [docs/SIGNALS.md](docs/SIGNALS.md) for the full signal reference.

## Supported Languages

| Language | Extensions | Import Detection | Full Support |
|----------|-----------|-----------------|--------------|
| Python | `.py` | `import`, `from...import` | Yes |
| Go | `.go` | `import "..."` | Yes |
| TypeScript | `.ts`, `.tsx` | `import`, `require` | Yes |
| JavaScript | `.js`, `.jsx` | `import`, `require` | Yes |
| Java | `.java` | `import` | Yes |
| Rust | `.rs` | `use`, `mod` | Yes |
| Ruby | `.rb` | `require`, `require_relative` | Yes |
| C/C++ | `.c`, `.cpp`, `.cc`, `.h`, `.hpp` | `#include` | Yes |

Language is auto-detected. Use `--language <name>` to force a specific scanner.

## CLI Reference

### `shannon-insight [PATH]` -- Analyze

Analyze codebase quality. Default command when no subcommand is given.

```bash
shannon-insight .
shannon-insight --changed
shannon-insight --json --fail-on high
shannon-insight --verbose --concerns
shannon-insight --hotspots
shannon-insight --signals src/engine.py
shannon-insight --preview
```

| Flag | Default | Description |
|------|---------|-------------|
| `PATH` | `.` | Project root to analyze |
| `--changed` | off | Scope to files changed on current branch (auto-detects base) |
| `--since REF` | none | Scope to files changed since a git ref (e.g. `HEAD~3`) |
| `--json` | off | Machine-readable JSON output |
| `--verbose`, `-v` | off | Show detailed evidence and patterns |
| `--save/--no-save` | `--save` | Save snapshot to `.shannon/` history |
| `--fail-on LEVEL` | none | Exit 1 if findings at level: `any` or `high` |
| `--hotspots` | off | Show files ranked by combined risk signals |
| `--signals [FILE]` | none | Show raw signals table (optionally for a specific file) |
| `--concerns` | off | Show findings grouped by concern category |
| `--journey` | off | Developer journey view: health score, progress, next steps |
| `--preview` | off | Show what would be analyzed without running |
| `--output-format` | auto | Output format: `default`, `github`, `compact` |
| `--no-tui` | off | Disable interactive TUI, use classic output |
| `--version` | off | Show version and exit |
| `-c`, `--config` | none | TOML configuration file |
| `-w`, `--workers` | auto | Parallel worker count (1-32) |

### `shannon-insight explain <FILE>` -- File Deep-Dive

Deep-dive on a specific file: signals, findings, and trends.

```bash
shannon-insight explain engine.py
shannon-insight explain src/core/engine.py --verbose
shannon-insight explain engine.py --json
```

| Flag | Default | Description |
|------|---------|-------------|
| `FILE` | required | File to explain (substring match) |
| `--json` | off | JSON output |
| `--verbose`, `-v` | off | Show all signals (default shows top 8) |

### `shannon-insight diff` -- Compare Snapshots

Show what changed since a previous analysis run.

```bash
shannon-insight diff
shannon-insight diff --baseline
shannon-insight diff --ref 5
shannon-insight diff --pin
shannon-insight diff --unpin
```

| Flag | Default | Description |
|------|---------|-------------|
| `--ref`, `-r` | none | Compare against a specific snapshot ID or commit SHA |
| `--baseline`, `-b` | off | Compare against pinned baseline |
| `--pin` | off | Pin current snapshot as baseline |
| `--unpin` | off | Clear pinned baseline |
| `--json` | off | JSON output |
| `--verbose`, `-v` | off | Show full per-file metric details |

### `shannon-insight health` -- Health Trends

Show codebase health trends over time. Requires saved snapshots in `.shannon/`.

```bash
shannon-insight health
shannon-insight health --last 10
shannon-insight health --json
```

| Flag | Default | Description |
|------|---------|-------------|
| `--last`, `-n` | 20 | Number of recent snapshots to include (2-200) |
| `--json` | off | JSON output |

### `shannon-insight history` -- List Snapshots

List past analysis runs stored in `.shannon/history.db`.

```bash
shannon-insight history
shannon-insight history --limit 5
shannon-insight history --json
```

| Flag | Default | Description |
|------|---------|-------------|
| `--limit`, `-n` | 20 | Maximum snapshots to list (1-1000) |
| `--json` | off | JSON output |

### `shannon-insight report` -- HTML Report

Generate an interactive HTML report with treemap visualization.

```bash
shannon-insight report
shannon-insight report -o my-report.html -m entropy
shannon-insight report --no-trends
```

| Flag | Default | Description |
|------|---------|-------------|
| `--output`, `-o` | `shannon-report.html` | Output file path |
| `--metric`, `-m` | `cognitive_load` | Default metric for treemap coloring |
| `--trends/--no-trends` | `--trends` | Include file trend sparklines |
| `--verbose`, `-v` | off | Verbose logging |

### `shannon-insight serve` -- Live Dashboard

Start a live dashboard with file watching and WebSocket updates.

```bash
pip install shannon-codebase-insight[serve]
shannon-insight serve
shannon-insight serve --port 9000 --no-browser
```

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | 8765 | Port to listen on |
| `--host` | `127.0.0.1` | Host to bind to |
| `--no-browser` | off | Don't open browser automatically |
| `--verbose`, `-v` | off | Verbose logging |

## Dashboard

![Dashboard](docs/dashboard.png)

The live dashboard (`shannon-insight serve`) provides 5 screens with real-time updates via WebSocket:

- **Overview** -- Health score (1-10), verdict, issue summary by category, risk histogram, focus point
- **Issues** -- Category tabs (Incomplete, Fragile, Tangled, Team), severity filters, finding cards with evidence
- **Files** -- Searchable table with sortable columns, treemap view, file detail with all signals
- **Modules** -- Module table with Martin metrics (instability, abstractness), module detail
- **Health** -- Health trend chart, top movers, chronic findings, concern radar chart, global signals

Keyboard shortcuts: `1-5` switch tabs, `/` search files, `j/k` navigate, `Enter` drill down, `Esc` go back, `?` show help.

Export: JSON (full state) or CSV (file table). API: `GET /api/state`, `GET /api/gate`, `GET /api/export/json`, `GET /api/export/csv`, `WS /ws`.

See [docs/DASHBOARD.md](docs/DASHBOARD.md) for the full dashboard guide.

## Configuration

Create `shannon-insight.toml` in your project root:

```toml
# ── File Filtering ──
exclude_patterns = ["*_test.go", "vendor/*", "node_modules/*", "dist/*"]
max_file_size_mb = 10.0            # Skip files larger than this (default: 10)
max_files = 10000                  # Max files to analyze (default: 10000)

# ── Git / Temporal ──
git_max_commits = 5000             # Max commits to analyze (default: 5000, 0 = no limit)
git_min_commits = 10               # Min commits for temporal analysis (default: 10)

# ── Insights ──
insights_max_findings = 50         # Max findings to return (default: 50)

# ── History ──
enable_history = true              # Auto-save snapshots to .shannon/ (default: true)
history_max_snapshots = 100        # Max snapshots to retain (default: 100)

# ── Performance ──
parallel_workers = 4               # Parallel workers (default: auto-detect)
enable_cache = true                # Enable disk cache (default: true)
cache_ttl_hours = 24               # Cache lifetime (default: 24)
timeout_seconds = 10               # File operation timeout (default: 10)

# ── PageRank ──
pagerank_damping = 0.85            # Damping factor (default: 0.85)
pagerank_iterations = 20           # Max iterations (default: 20)

# ── Security ──
allow_hidden_files = false         # Analyze dotfiles (default: false)
follow_symlinks = false            # Follow symlinks (default: false)
```

**Precedence**: CLI flags > `SHANNON_*` environment variables > `shannon-insight.toml` > defaults.

Environment variables use the `SHANNON_` prefix: `SHANNON_GIT_MAX_COMMITS=10000`, `SHANNON_INSIGHTS_MAX_FINDINGS=100`, etc.

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for the full configuration reference.

## CI Integration

### GitHub Actions

```yaml
name: Code Quality
on: [pull_request]
jobs:
  shannon:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for temporal analysis
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install shannon-codebase-insight
      - run: shannon-insight --changed --fail-on high
```

The `--fail-on high` flag exits with code 1 if any finding has severity >= 0.8. Use `--fail-on any` to fail on any finding.

On GitHub Actions, output format is auto-detected to produce `::warning` and `::error` annotations on PR diffs. Force it with `--output-format github`.

### Quality Gate API

When running the dashboard (`shannon-insight serve`), the `/api/gate` endpoint returns pass/fail status:

```bash
curl http://localhost:8765/api/gate
```

```json
{
  "status": "PASS",
  "health": 7.2,
  "critical_count": 0,
  "finding_count": 12,
  "reason": "Health 7.2, no critical issues"
}
```

Fails when health < 4.0 or any finding has severity >= 0.9.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clean -- no findings above threshold |
| 1 | Findings above threshold detected |
| 130 | Interrupted (Ctrl+C) |

## Signals Reference

Shannon Insight computes 62 signals across 6 categories:

| Category | Signals | Examples |
|----------|---------|---------|
| **Size & Complexity** | 7 | `lines`, `function_count`, `cognitive_load`, `max_nesting` |
| **Graph Position** | 13 | `pagerank`, `blast_radius_size`, `in_degree`, `community` |
| **Code Health** | 6 | `compression_ratio`, `semantic_coherence`, `stub_ratio` |
| **Change History** | 8 | `total_changes`, `churn_cv`, `bus_factor`, `fix_ratio` |
| **Team Context** | 2 | `author_entropy`, `bus_factor` |
| **Computed Risk** | 4 | `risk_score`, `wiring_quality`, `file_health_score`, `raw_risk` |

Plus 15 per-module signals (Martin metrics, velocity, knowledge Gini) and 13 global signals (modularity, Fiedler value, codebase health).

See [docs/SIGNALS.md](docs/SIGNALS.md) for the full signal reference.

### How Scoring Works

**Per-file**: Raw signals are percentile-normalized across all files, then combined into `risk_score` via multiplicative fusion: `structural_risk * complexity * churn * bus_factor_penalty`. Dormant files (zero changes) get risk_score = 0.

**Codebase**: File scores and global metrics (modularity, wiring quality, architecture health) produce `codebase_health` (internal 0-1, displayed as 1-10).

**Focus point**: The "START HERE" recommendation ranks files by `risk * impact * tractability * confidence` to identify the single most actionable file.

## Optional Dependencies

```bash
pip install shannon-codebase-insight[serve]      # Dashboard (starlette, uvicorn, watchfiles)
pip install shannon-codebase-insight[tensordb]    # Parquet export + SQL finders (pyarrow, duckdb)
pip install shannon-codebase-insight[parsing]     # Tree-sitter parsing (more accurate AST)
```

## Development

```bash
git clone https://github.com/namanagarwal/shannon-insight.git
cd shannon-insight
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

make test          # Run tests with coverage
make all           # Format + lint + type-check + test
```

## License

MIT License -- see [LICENSE](LICENSE)

## Credits

Created by Naman Agarwal. Built on Claude Shannon's information theory, PageRank (Page & Brin), Louvain community detection (Blondel et al.), Tarjan's SCC algorithm, Kolmogorov complexity approximation, Martin's package metrics, and Fiedler spectral analysis.
