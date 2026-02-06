# insights/models -- Data Models

**Status**: EXISTS -- expanding for v2

## Current Models (v1)

The current implementation in `src/shannon_insight/insights/models.py` defines four dataclasses:

```python
@dataclass
class Evidence:
    signal: str           # "pagerank", "blast_radius_pct", etc.
    value: float          # the raw value
    percentile: float     # 0-100
    description: str      # "top 3% by PageRank"

@dataclass
class Finding:
    finding_type: str     # "high_risk_hub", etc.
    severity: float       # 0.0 to 1.0
    title: str
    files: List[str]
    evidence: List[Evidence]
    suggestion: str

@dataclass
class StoreSummary:
    total_files: int = 0
    total_modules: int = 0
    commits_analyzed: int = 0
    git_available: bool = False
    fiedler_value: Optional[float] = None
    signals_available: List[str] = field(default_factory=list)

@dataclass
class InsightResult:
    findings: List[Finding]
    store_summary: StoreSummary
```

## v2 Models

### Evidence

Gains `ir_source` to identify which IR level produced this evidence item, enabling multi-IR evidence chains.

```python
@dataclass
class Evidence:
    ir_source: str              # "IR1", "IR2", "IR3", "IR4", "IR5t", "IR5s"
    signal: str                 # signal name from registry/signals.md
    value: Any                  # the raw value (float, str, bool, int)
    percentile: Optional[float] # where it ranks (0-100), None for non-numeric
    description: str            # human-readable explanation
```

### Finding

Gains confidence scoring, scope classification, effort estimate, and temporal lifecycle fields.

```python
@dataclass
class Finding:
    # Identity
    id: str                     # stable hash: hash(type + sorted(targets))
    type: str                   # "HIGH_RISK_HUB", "ORPHAN_CODE", etc.

    # Scoring
    severity: float             # [0, 1] -- from registry/finders.md base severity
    confidence: float           # [0, 1] -- margin above threshold (see scoring.md)

    # Scope
    scope: Scope                # FILE | FILE_PAIR | MODULE | MODULE_PAIR | CODEBASE
    targets: List[str]          # affected file/module paths

    # Evidence
    evidence: List[Evidence]    # ordered chain from multiple IRs
    suggestion: str             # actionable recommendation text
    effort: Effort              # LOW | MEDIUM | HIGH

    # Temporal lifecycle (populated when history is available)
    first_seen: Optional[datetime] = None
    persistence_count: int = 0  # snapshots this has existed
    trend: Trend = Trend.STABLE # WORSENING | STABLE | IMPROVING
    regression: bool = False    # was resolved, came back
```

#### Scope enum

```python
class Scope(str, Enum):
    FILE = "FILE"
    FILE_PAIR = "FILE_PAIR"
    MODULE = "MODULE"
    MODULE_PAIR = "MODULE_PAIR"
    CODEBASE = "CODEBASE"
```

#### Effort enum

```python
class Effort(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
```

#### Trend enum

```python
class Trend(str, Enum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    WORSENING = "WORSENING"
```

#### Stable ID computation

```python
def finding_id(finding_type: str, targets: List[str]) -> str:
    """Deterministic hash for cross-snapshot tracking."""
    key = finding_type + "|" + "|".join(sorted(targets))
    return hashlib.sha256(key.encode()).hexdigest()[:16]
```

The ID is stable across runs as long as the finding type and target set are the same. This enables:
- Tracking persistence across snapshots
- Detecting regressions (resolved then reappeared)
- Computing debt velocity

### Finding lifecycle

A finding progresses through states based on its presence across snapshots:

```
NEW ──> PERSISTING ──> RESOLVED
                          │
                          └──> REGRESSION (if same ID reappears)
```

Fields supporting lifecycle:

| Field | Source | Meaning |
|---|---|---|
| `first_seen` | First snapshot containing this finding ID | When the issue was first detected |
| `persistence_count` | Count of consecutive snapshots | How long it has persisted |
| `trend` | Comparing severity/evidence across snapshots | Getting better or worse? |
| `regression` | ID was absent in prior snapshot, present now | Issue returned after being fixed |

Lifecycle data is populated by the kernel when a history database is available. Without `--save`, these fields remain at their defaults.

### InsightResult

```python
@dataclass
class InsightResult:
    findings: List[Finding]
    composites: CompositeScores
    suggestions: List[Suggestion]
    execution_plan: Optional[ExecutionPlan] = None  # for debugging/transparency
```

### CompositeScores

Summary-level composite scores from `registry/composites.md`.

```python
@dataclass
class CompositeScores:
    ai_quality: float           # wiring_score from signals/
    architecture_health: float  # from signals/
    team_risk: float            # from signals/
    codebase_health: float      # the one number
```

### Suggestion

Actionable recommendations that may address multiple findings.

```python
@dataclass
class Suggestion:
    action: str                 # "Split auth_service.py into auth.py and cache.py"
    priority: int               # 1 = do first
    effort: Effort              # LOW | MEDIUM | HIGH
    impact: float               # estimated health improvement [0, 1]
    targets: List[str]          # files/modules to change
    evidence_refs: List[str]    # finding IDs this suggestion addresses
```

### InsightDelta

Structured diff between two `InsightResult` snapshots.

```python
@dataclass
class InsightDelta:
    new_findings: List[Finding]
    resolved_findings: List[Finding]
    persisting: List[Finding]           # with updated persistence_count
    regressions: List[Finding]          # was resolved, came back
    worsening: List[Finding]            # severity or evidence increased
    improving: List[Finding]            # severity or evidence decreased

    @property
    def debt_velocity(self) -> int:
        """Positive = accumulating debt. Negative = paying down."""
        return len(self.new_findings) - len(self.resolved_findings)
```

## Migration Path

The v1 `Finding` dataclass is a strict subset of the v2 model. Migration:

1. Rename `finding_type` to `type`, `files` to `targets`
2. Add `id` (computed from type + targets)
3. Add `confidence` (initially set to severity as a fallback)
4. Add `scope` (inferred from finding type -- FILE_PAIR for HIDDEN_COUPLING/DEAD_DEPENDENCY, MODULE for BOUNDARY_MISMATCH, FILE for all others)
5. Add `effort` (from `registry/finders.md` per finding type)
6. `StoreSummary` is subsumed by `CompositeScores` + `ExecutionPlan`
