# Runtime

How the tool sets up itself, understands its environment, and handles edge cases.

---

## RuntimeContext

```python
@dataclass
class RuntimeContext:
    """Everything the tool needs to know about its environment."""

    # Location
    root: Path                    # Resolved absolute path

    # Git state
    is_git_repo: bool
    branch: str | None            # Current branch name
    head_commit: str | None       # HEAD SHA (short)

    # Language detection
    languages: list[str]          # Detected languages, sorted by file count
    primary_language: str         # First in list

    # Scale
    file_count: int               # Source files matching filters
    tier: Tier                    # ABSOLUTE | BAYESIAN | FULL

    # Capabilities
    has_git: bool                 # Can run temporal analysis
    has_tests: bool               # Test files detected

    # Timing
    started_at: datetime
```

---

## Tier System

Behavior adapts based on codebase size.

### Tier Determination

```python
class Tier(Enum):
    ABSOLUTE = "absolute"    # < 15 files
    BAYESIAN = "bayesian"    # 15-50 files
    FULL = "full"            # 50+ files

def determine_tier(file_count: int) -> Tier:
    if file_count < 15:
        return Tier.ABSOLUTE
    elif file_count < 50:
        return Tier.BAYESIAN
    else:
        return Tier.FULL
```

### Tier Effects

| Feature | ABSOLUTE (<15) | BAYESIAN (15-50) | FULL (50+) |
|---------|---------------|-----------------|------------|
| Raw signals | All computed | All computed | All computed |
| Percentiles | Not computed | Bayesian posterior | Standard |
| Composites | Not computed | Computed | Computed |
| Finders | 8 of 22 | 22 of 22 | 22 of 22 |

### ABSOLUTE Tier Behavior

```python
def analyze_absolute_tier(store: AnalysisStore) -> AnalysisResult:
    """
    For tiny codebases:
    - Show raw signal values, not composites
    - Only run finders with absolute thresholds
    """
    # Skip percentile computation
    # Skip composite computation
    # Run only: HIDDEN_COUPLING, UNSTABLE_FILE, DEAD_DEPENDENCY,
    #           ORPHAN_CODE, HOLLOW_CODE, PHANTOM_IMPORTS,
    #           COPY_PASTE_CLONE, FLAT_ARCHITECTURE
```

### BAYESIAN Tier Normalization

```python
def bayesian_percentile(
    value: float,
    values: list[float],
    alpha: float = 1.0,
    beta: float = 1.0,
) -> float:
    """
    Bayesian posterior percentile for small samples.

    Uses Beta prior to shrink estimates toward 0.5.
    """
    rank = sum(1 for v in values if v <= value)
    n = len(values)

    # Posterior mean of Beta(alpha + rank, beta + n - rank)
    posterior = (alpha + rank) / (alpha + beta + n)
    return posterior
```

---

## Configuration

### Config Resolution Order

```
Priority (highest wins):
1. CLI flags              --exclude="*.test.py" --max-findings=10
2. Environment variables  SHANNON_MAX_FINDINGS=10
3. Project config         ./shannon-insight.toml
4. User config            ~/.config/shannon-insight/config.toml
5. Built-in defaults
```

### Config Model

```python
@dataclass
class Config:
    # Scope
    include: list[str] = field(default_factory=lambda: ["**/*"])
    exclude: list[str] = field(default_factory=list)

    # Thresholds (override registry defaults)
    thresholds: dict[Signal, float] = field(default_factory=dict)

    # Feature toggles
    enable_git: bool = True
    enable_semantic: bool = True
    enable_team: bool = True

    # Output
    max_findings: int = 20
    format: OutputFormat = OutputFormat.TERMINAL

    # Persistence
    save_snapshot: bool = False
    db_path: Path | None = None
```

### TOML Config Example

```toml
# shannon-insight.toml

[scope]
include = ["src/**/*.py", "lib/**/*.py"]
exclude = ["**/test_*.py", "**/migrations/**"]

[thresholds]
god_file_lines = 800           # Override default 1000
stub_ratio_max = 0.3           # Stricter than default 0.5

[features]
enable_git = true
enable_semantic = true

[output]
max_findings = 30
format = "json"

[persistence]
save_snapshot = true
db_path = ".shannon/history.db"
```

### Environment Variables

```bash
SHANNON_ROOT=/path/to/project
SHANNON_MAX_FINDINGS=50
SHANNON_FORMAT=json
SHANNON_ENABLE_GIT=false
SHANNON_SAVE_SNAPSHOT=true
```

---

## Graceful Degradation

### Missing Git

```python
def handle_no_git(ctx: RuntimeContext, store: AnalysisStore) -> None:
    """
    When git is unavailable:
    - Skip GitCollector, CoChangeCollector
    - Skip temporal signals (#27-34)
    - Skip finders requiring temporal signals
    """
    if not ctx.has_git:
        logger.warning("Not a git repository. Temporal analysis disabled.")
        store.git_history = None
        store.cochange = None
        store.churn = {}
```

### Finder Degradation Table

| Missing Data | Finders Skipped |
|--------------|-----------------|
| No git | HIGH_RISK_HUB, UNSTABLE_FILE, DEAD_DEPENDENCY, HIDDEN_COUPLING, KNOWLEDGE_SILO, REVIEW_BLINDSPOT, CONWAY_VIOLATION, BUG_ATTRACTOR |
| No semantics | GOD_FILE, NAMING_DRIFT, ACCIDENTAL_COUPLING |
| No modules (< 2) | BOUNDARY_MISMATCH, LAYER_VIOLATION, ZONE_OF_PAIN, CONWAY_VIOLATION, ARCHITECTURE_EROSION |
| No snapshots (< 3) | CHRONIC_PROBLEM, ARCHITECTURE_EROSION |

### Parse Error Handling

```python
def collect_with_error_handling(collector: Collector, ctx: RuntimeContext, store: FactStore) -> None:
    """
    Handle individual file parse errors gracefully.
    """
    try:
        collector.collect(ctx, store)
    except FileParseError as e:
        logger.warning(f"Failed to parse {e.path}: {e.message}")
        # Continue with other files
    except CollectorError:
        raise  # Fatal, propagate
```

---

## Error Handling

### Error Types

```python
class AnalysisError(Exception):
    """Base class for analysis errors."""
    pass

class ConfigError(AnalysisError):
    """Invalid configuration."""
    pass

class CollectorError(AnalysisError):
    """Fatal collector failure."""
    pass

class FileParseError(AnalysisError):
    """Single file parse failure (non-fatal)."""
    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
```

### Timeout Handling

```python
TIMEOUTS = {
    "collector_code": 120,    # 2 min
    "collector_git": 60,      # 1 min
    "analyzer": 300,          # 5 min per analyzer
    "finder": 30,             # 30 sec per finder
}

def run_with_timeout(func: Callable, timeout: float, name: str) -> Any:
    """Run function with timeout. Raises AnalyzerTimeoutError if exceeded."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise AnalyzerTimeoutError(f"{name} exceeded {timeout}s timeout")
```

---

## Caching

### Disk Cache

```python
from diskcache import Cache

CACHE_DIR = Path.home() / ".cache" / "shannon-insight"

def get_cache() -> Cache:
    return Cache(str(CACHE_DIR), size_limit=500 * 1024 * 1024)  # 500 MB

def cache_key(root: Path, file_path: str, mtime: float) -> str:
    """Cache key based on file path and modification time."""
    return f"{root}:{file_path}:{mtime}"
```

### Cached Operations

- File metrics (by mtime)
- Git history (by HEAD commit)
- Dependency graph (by file mtimes hash)

---

## Logging

```python
import logging

def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("git").setLevel(logging.WARNING)
```

### Log Levels

| Level | Use |
|-------|-----|
| DEBUG | Detailed trace (--verbose) |
| INFO | Progress messages |
| WARNING | Non-fatal issues, skipped operations |
| ERROR | Fatal issues |

---

## Exit Codes

```python
class ExitCode(IntEnum):
    SUCCESS = 0
    FINDINGS_EXIST = 1
    HIGH_SEVERITY_FINDINGS = 2
    ERROR = 3

def determine_exit_code(findings: list[Finding], fail_on: str) -> ExitCode:
    """
    Determine exit code based on --fail-on setting.

    --fail-on=none: Always 0
    --fail-on=any: 1 if any findings
    --fail-on=high: 2 if severity >= 0.8
    """
    if fail_on == "none":
        return ExitCode.SUCCESS

    if not findings:
        return ExitCode.SUCCESS

    if fail_on == "any":
        return ExitCode.FINDINGS_EXIST

    if fail_on == "high":
        if any(f.severity >= 0.8 for f in findings):
            return ExitCode.HIGH_SEVERITY_FINDINGS

    return ExitCode.SUCCESS
```

---

## Performance Characteristics

| Codebase Size | Expected Time | Memory |
|---------------|---------------|--------|
| < 100 files | < 5s | < 100 MB |
| 100-1000 files | 5-30s | 100-500 MB |
| 1000-10000 files | 30s-5m | 500 MB - 2 GB |
| 10000+ files | 5-30m | 2-8 GB |

### Bottlenecks

1. **Git log parsing** — scales with commit count
2. **NCD clone detection** — O(n²) but with MinHash pre-filter
3. **Co-change matrix** — O(n² × commits)
4. **TF-IDF vectorization** — scales with total tokens

### Optimization Strategies

- Incremental analysis (--changed flag)
- MinHash pre-filtering for clones
- Sparse co-change matrix
- Parallel collector execution
