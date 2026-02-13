# Configuration Reference

Shannon Insight is configured through a combination of CLI flags, environment variables, and a TOML configuration file. All settings have sensible defaults -- configuration is optional.

## Configuration Precedence

Settings are resolved in this order (highest priority first):

1. **CLI arguments** -- Flags like `--verbose`, `--workers 4`, `--fail-on high`
2. **Environment variables** -- Prefixed with `SHANNON_` (e.g., `SHANNON_GIT_MAX_COMMITS=10000`)
3. **TOML config file** -- `./shannon-insight.toml` or specified via `--config path.toml`
4. **Defaults** -- Built-in values defined in `AnalysisSettings`

A CLI flag always wins. An environment variable overrides the config file. The config file overrides defaults.

## Full Example Config

```toml
# shannon-insight.toml
# Place in your project root. All values shown are defaults.

# ── File Filtering ──────────────────────────────────────
exclude_patterns = [
    "*_test.go",
    "*_test.ts",
    "*.test.ts",
    "*.spec.ts",
    "vendor/*",
    "node_modules/*",
    "dist/*",
    "build/*",
    ".git/*",
    "venv/*",
    ".venv/*",
    "__pycache__/*",
    ".tox/*",
    ".mypy_cache/*",
    "htmlcov/*",
    ".coverage",
    "coverage/*",
    "*.egg-info/*",
    ".eggs/*",
    ".pytest_cache/*",
    ".ruff_cache/*",
    "*.min.js",
    "*.bundle.js",
    "*.generated.*",
]
max_file_size_mb = 10.0
max_files = 10000

# ── Git / Temporal ──────────────────────────────────────
git_max_commits = 5000
git_min_commits = 10

# ── Insights ────────────────────────────────────────────
insights_max_findings = 50

# ── History ─────────────────────────────────────────────
enable_history = true
history_max_snapshots = 100

# ── Performance ─────────────────────────────────────────
# parallel_workers = 4           # Uncomment to override auto-detect
enable_cache = true
cache_dir = ".shannon-cache"
cache_ttl_hours = 24
timeout_seconds = 10

# ── PageRank ────────────────────────────────────────────
pagerank_damping = 0.85
pagerank_iterations = 20
pagerank_tolerance = 1e-6

# ── Logging ─────────────────────────────────────────────
verbose = false
quiet = false
# log_file = "shannon.log"       # Uncomment to log to file

# ── Security ────────────────────────────────────────────
allow_hidden_files = false
block_system_dirs = true
follow_symlinks = false
```

## Configuration Options

### File Filtering

| Key | Type | Default | Valid Range | Env Var | Description |
|-----|------|---------|-------------|---------|-------------|
| `exclude_patterns` | list[str] | (see above) | glob patterns | `SHANNON_EXCLUDE_PATTERNS` | File patterns to exclude from analysis. Uses glob syntax (`*` matches within path segment, `**` matches across segments). |
| `max_file_size_mb` | float | `10.0` | 0.0-100.0 | `SHANNON_MAX_FILE_SIZE_MB` | Skip files larger than this. Large files slow analysis and are typically generated/vendored. |
| `max_files` | int | `10000` | 1-100000 | `SHANNON_MAX_FILES` | Maximum files to analyze. Safety limit for very large monorepos. |

**Notes**:
- Exclude patterns are matched against the path relative to the project root.
- Default excludes cover common build artifacts, caches, and vendored code.
- Add project-specific patterns (e.g., `"generated/**"`, `"proto/*.go"`) to reduce noise.

### Git / Temporal

| Key | Type | Default | Valid Range | Env Var | Description |
|-----|------|---------|-------------|---------|-------------|
| `git_max_commits` | int | `5000` | 0-100000 | `SHANNON_GIT_MAX_COMMITS` | Maximum number of git commits to analyze. Set to 0 for no limit. Higher values give more accurate temporal signals but take longer. |
| `git_min_commits` | int | `10` | 0+ | `SHANNON_GIT_MIN_COMMITS` | Minimum commits required to enable temporal analysis. Below this threshold, churn, co-change, and team signals are skipped. |

**Notes**:
- Without git history, Shannon Insight still produces structural and per-file findings.
- For CI on feature branches, ensure `fetch-depth: 0` in checkout to get full history.
- Setting `git_max_commits = 500` is sufficient for most PR-level analysis.

### Insights

| Key | Type | Default | Valid Range | Env Var | Description |
|-----|------|---------|-------------|---------|-------------|
| `insights_max_findings` | int | `50` | 1-500 | `SHANNON_INSIGHTS_MAX_FINDINGS` | Maximum findings to return. Findings are sorted by severity; lower-severity findings are dropped when the limit is reached. |

### History

| Key | Type | Default | Valid Range | Env Var | Description |
|-----|------|---------|-------------|---------|-------------|
| `enable_history` | bool | `true` | true/false | `SHANNON_ENABLE_HISTORY` | Auto-save analysis snapshots to `.shannon/history.db`. Required for `diff`, `health`, `history` commands and the `chronic_problem`/`architecture_erosion` finders. |
| `history_max_snapshots` | int | `100` | 1-10000 | `SHANNON_HISTORY_MAX_SNAPSHOTS` | Maximum snapshots to retain. When exceeded, oldest snapshots are pruned. |

**Notes**:
- The `.shannon/` directory is created in the project root.
- Add `.shannon/` to `.gitignore` -- it contains local analysis history.
- Snapshots are SQLite-backed and typically 50-200 KB each.

### Performance

| Key | Type | Default | Valid Range | Env Var | Description |
|-----|------|---------|-------------|---------|-------------|
| `parallel_workers` | int or null | `null` (auto) | 1-32 | `SHANNON_PARALLEL_WORKERS` | Number of parallel workers for file scanning. Auto-detect uses `os.cpu_count()`. Set to 1 for debugging. |
| `timeout_seconds` | int | `10` | 1-300 | `SHANNON_TIMEOUT_SECONDS` | Timeout for individual file operations (parsing, compression). Prevents hangs on malformed files. |
| `enable_cache` | bool | `true` | true/false | `SHANNON_ENABLE_CACHE` | Enable disk cache for repeated analysis. Caches file metrics to skip unchanged files. |
| `cache_dir` | str | `".shannon-cache"` | any path | `SHANNON_CACHE_DIR` | Cache directory path. Relative paths are resolved from the current working directory. |
| `cache_ttl_hours` | int | `24` | 0-720 | `SHANNON_CACHE_TTL_HOURS` | Cache entry lifetime in hours. Set to 0 to disable cache expiry. Maximum 30 days (720 hours). |

**Notes**:
- The cache stores file metrics keyed by file hash. A code change invalidates the cache for that file.
- Add `.shannon-cache/` to `.gitignore`.
- In CI, caching is useful with GitHub Actions cache for repeated runs.

### PageRank

| Key | Type | Default | Valid Range | Env Var | Description |
|-----|------|---------|-------------|---------|-------------|
| `pagerank_damping` | float | `0.85` | 0.0-1.0 | `SHANNON_PAGERANK_DAMPING` | PageRank damping factor. 0.85 is the standard value from the original paper. Lower values spread importance more evenly. |
| `pagerank_iterations` | int | `20` | 1-100 | `SHANNON_PAGERANK_ITERATIONS` | Maximum PageRank iterations. Convergence usually occurs within 10-15 iterations. |
| `pagerank_tolerance` | float | `1e-6` | >0 | `SHANNON_PAGERANK_TOLERANCE` | PageRank convergence tolerance. Iteration stops when the change between iterations falls below this threshold. |

**Notes**:
- These rarely need adjustment. The defaults match standard graph analysis practice.
- Lower damping (e.g., 0.70) reduces the influence of deep dependency chains.

### Logging

| Key | Type | Default | Valid Range | Env Var | Description |
|-----|------|---------|-------------|---------|-------------|
| `verbose` | bool | `false` | true/false | `SHANNON_VERBOSE` | Enable DEBUG-level logging. Shows analyzer progress, signal values, finder decisions. |
| `quiet` | bool | `false` | true/false | `SHANNON_QUIET` | Suppress all output except ERRORs. Useful for CI pipelines where only exit code matters. |
| `log_file` | str or null | `null` | any path | `SHANNON_LOG_FILE` | Write logs to a file instead of stderr. |

### Security

| Key | Type | Default | Valid Range | Env Var | Description |
|-----|------|---------|-------------|---------|-------------|
| `allow_hidden_files` | bool | `false` | true/false | `SHANNON_ALLOW_HIDDEN_FILES` | Include dotfiles (files starting with `.`) in analysis. Off by default because dotfiles are typically configuration, not source code. |
| `block_system_dirs` | bool | `true` | true/false | `SHANNON_BLOCK_SYSTEM_DIRS` | Refuse to analyze system directories (`/usr`, `/etc`, etc.). Safety measure against accidental misuse. |
| `follow_symlinks` | bool | `false` | true/false | `SHANNON_FOLLOW_SYMLINKS` | Follow symbolic links during file discovery. Off by default to prevent infinite loops and duplicate analysis. |

## Environment Variables

All settings can be overridden via environment variables with the `SHANNON_` prefix. The variable name is the uppercase version of the config key:

```bash
# Examples
export SHANNON_GIT_MAX_COMMITS=10000
export SHANNON_INSIGHTS_MAX_FINDINGS=100
export SHANNON_PARALLEL_WORKERS=4
export SHANNON_VERBOSE=true
export SHANNON_ENABLE_CACHE=false
export SHANNON_EXCLUDE_PATTERNS='["vendor/*","generated/*"]'
```

For list values (like `exclude_patterns`), use JSON array syntax in the environment variable.

Boolean values accept: `true`, `false`, `1`, `0`, `yes`, `no`.

## CLI Flags

CLI flags override both environment variables and config file settings:

```bash
# These override any config file or env var
shannon-insight --verbose              # overrides verbose=false
shannon-insight -w 8                   # overrides parallel_workers
shannon-insight -c custom.toml         # use specific config file
shannon-insight --save                 # overrides enable_history for this run
```

## Config File Discovery

Shannon Insight looks for `shannon-insight.toml` in:

1. The path specified by `--config` / `-c`
2. The project root (the `PATH` argument or current directory)

The file must be valid TOML. Unknown keys are silently ignored (allows forward compatibility).

## Computed Properties

These are derived from the config values at runtime:

| Property | Derived From | Description |
|----------|-------------|-------------|
| `max_file_size_bytes` | `max_file_size_mb * 1024 * 1024` | Max file size in bytes for internal comparisons |
| `cache_ttl_seconds` | `cache_ttl_hours * 3600` | Cache TTL in seconds for internal comparisons |

## Recipes

### Minimal CI Config

```toml
# Fast CI analysis -- skip history, limit commits
enable_history = false
git_max_commits = 500
insights_max_findings = 20
enable_cache = false
```

### Monorepo Config

```toml
# Large repo -- increase limits, add excludes
max_files = 50000
git_max_commits = 10000
parallel_workers = 8
exclude_patterns = [
    "vendor/*",
    "node_modules/*",
    "third_party/*",
    "generated/*",
    "proto/*.go",
]
```

### Deep Analysis Config

```toml
# Maximum detail -- for quarterly reviews
git_max_commits = 0              # No limit
insights_max_findings = 200
history_max_snapshots = 500
verbose = true
```
