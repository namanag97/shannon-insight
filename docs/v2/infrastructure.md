# Infrastructure: 6 Hardening Patterns + Enterprise Contracts

> **ENTERPRISE-GRADE PRODUCTION SOFTWARE**
>
> This is NOT an MVP. These patterns are Phase 0 blockers — implementation CANNOT proceed without them.
> Total: ~500 lines of infrastructure code + ~100 lines of contracts.

Build these BEFORE Phase 1 code. They are Phase 0 deliverables alongside documentation.

Each pattern maps to a proven production system.

---

## Protocol Contracts (Enterprise Extensions)

### Enhanced Analyzer Protocol

```python
from typing import Protocol, Set, Optional

class Analyzer(Protocol):
    """Analyzer protocol with enterprise metadata for orchestration."""

    # Identity
    name: str
    api_version: str = "2.0"  # Semantic version for compatibility checks

    # Dependencies
    requires: Set[str]        # Slots that must be in store.available
    provides: Set[str]        # Slots this analyzer adds to store.available

    # Orchestration
    run_last: bool = False    # If True, runs in Wave 2 (after all Wave 1 analyzers)

    # Error handling
    error_mode: str = "fail"  # "fail" | "skip" | "degrade"
                              # fail: raise exception, halt pipeline
                              # skip: log warning, continue without this analyzer
                              # degrade: partial results OK, continue

    # Deprecation
    deprecated: bool = False
    deprecation_note: Optional[str] = None

    def analyze(self, store: "AnalysisStore") -> None:
        """Mutate store by populating slots declared in `provides`."""
        ...
```

### Enhanced Finder Protocol

```python
class Finder(Protocol):
    """Finder protocol with enterprise metadata for graceful degradation."""

    # Identity
    name: str
    api_version: str = "2.0"

    # Dependencies
    requires: Set[str]        # Signals/slots that must be available

    # Behavior
    error_mode: str = "skip"  # "fail" | "skip" | "degrade"
                              # skip: if requirements missing, silently return []
                              # degrade: partial evaluation with reduced confidence
                              # fail: raise if requirements missing

    # Classification
    hotspot_filtered: bool = False  # If True, must also check total_changes > median
    tier_minimum: str = "ABSOLUTE"  # Minimum tier: "ABSOLUTE" | "BAYESIAN" | "FULL"

    # Deprecation
    deprecated: bool = False
    deprecation_note: Optional[str] = None

    def find(self, store: "AnalysisStore") -> List["Finding"]:
        """Return findings based on store contents. Never mutate store."""
        ...

    def compute_confidence(
        self,
        signals: Dict[str, float],
        thresholds: Dict[str, float]
    ) -> float:
        """
        Compute confidence score using margin formula.

        confidence = mean(margin(signal, threshold) for each triggered condition)
        margin(s, t) = max(0, (percentile(s) - t) / (1.0 - t))  # normalized to [0,1]

        Example: pctl(pagerank)=0.95, threshold=0.90
                 margin = (0.95 - 0.90) / (1.0 - 0.90) = 0.50
        """
        ...
```

### Evidence Builder Protocol

```python
class EvidenceBuilder(Protocol):
    """Standard interface for building evidence chains."""

    def build_evidence(
        self,
        finding: "Finding",
        store: "AnalysisStore"
    ) -> List["Evidence"]:
        """
        Build structured evidence for a finding.

        Each Evidence includes:
        - signal: Signal enum value
        - raw_value: actual value
        - percentile: if applicable
        - threshold: what was exceeded
        - ir_level: which IR produced this signal
        """
        ...
```

---

## Pattern 1: Signal Enum + Registry

**Inspired by**: Prometheus `CollectorRegistry` (auto-registration, collision detection via `describe()`), SonarQube `MeasureComputer` (declared input/output metrics with DAG validation).

**Kills**: C3 (name mismatches), C4 (duplicate computation), C12 (percentiling wrong signals), C17 (all-zero columns), C47 (single source of truth).

**File**: `signals/registry.py` (~120 lines)

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Set

class Signal(Enum):
    """Every signal defined ONCE. The enum IS the name — no string typos possible."""
    # IR1 scanning
    LINES = "lines"
    FUNCTION_COUNT = "function_count"
    CLASS_COUNT = "class_count"
    MAX_NESTING = "max_nesting"
    IMPL_GINI = "impl_gini"
    STUB_RATIO = "stub_ratio"
    IMPORT_COUNT = "import_count"
    # IR2 semantics
    ROLE = "role"
    CONCEPT_COUNT = "concept_count"
    CONCEPT_ENTROPY = "concept_entropy"
    NAMING_DRIFT = "naming_drift"
    TODO_DENSITY = "todo_density"
    DOCSTRING_COVERAGE = "docstring_coverage"
    # IR3 graph
    PAGERANK = "pagerank"
    BETWEENNESS = "betweenness"
    IN_DEGREE = "in_degree"
    OUT_DEGREE = "out_degree"
    BLAST_RADIUS_SIZE = "blast_radius_size"
    DEPTH = "depth"
    IS_ORPHAN = "is_orphan"
    PHANTOM_IMPORT_COUNT = "phantom_import_count"
    BROKEN_CALL_COUNT = "broken_call_count"
    COMMUNITY = "community"
    COMPRESSION_RATIO = "compression_ratio"
    SEMANTIC_COHERENCE = "semantic_coherence"
    COGNITIVE_LOAD = "cognitive_load"
    # IR5t temporal
    TOTAL_CHANGES = "total_changes"
    CHURN_TRAJECTORY = "churn_trajectory"
    CHURN_SLOPE = "churn_slope"
    CHURN_CV = "churn_cv"
    BUS_FACTOR = "bus_factor"
    AUTHOR_ENTROPY = "author_entropy"
    FIX_RATIO = "fix_ratio"
    REFACTOR_RATIO = "refactor_ratio"
    # Composites
    RAW_RISK = "raw_risk"
    RISK_SCORE = "risk_score"
    WIRING_QUALITY = "wiring_quality"
    # ... module and global signals follow same pattern

@dataclass(frozen=True)
class SignalMeta:
    signal: Signal
    dtype: type                          # int, float, str, bool
    scope: str                           # "file" | "module" | "global"
    percentileable: bool                 # False for community, role, is_orphan, trajectory
    polarity: str                        # "high_is_bad" | "high_is_good" | "neutral"
    absolute_threshold: Optional[float]  # For ABSOLUTE tier finders. None = no threshold.
    produced_by: str                     # Single owner: "graph/algorithms", "temporal/churn"
    phase: int                           # First available: 0, 1, 2, 3, 4, 5

# THE registry — populated at import time, validated immediately
REGISTRY: Dict[Signal, SignalMeta] = {}

def register(meta: SignalMeta) -> None:
    """Register a signal. Raises on duplicate with different producer (single-owner rule)."""
    if meta.signal in REGISTRY:
        existing = REGISTRY[meta.signal]
        if existing.produced_by != meta.produced_by:
            raise ValueError(
                f"Signal {meta.signal.value} already registered by {existing.produced_by}, "
                f"cannot register again from {meta.produced_by}"
            )
        return  # Idempotent for same producer
    REGISTRY[meta.signal] = meta

def percentileable_signals() -> Set[Signal]:
    """Signals safe for percentile normalization. Auto-derived, never hand-maintained."""
    return {s for s, m in REGISTRY.items() if m.percentileable}

def signals_by_phase(phase: int) -> Set[Signal]:
    """Signals available after a given phase completes."""
    return {s for s, m in REGISTRY.items() if m.phase <= phase}

# Register all signals at module load — catches collisions immediately
register(SignalMeta(Signal.PAGERANK, float, "file", True, "high_is_bad", 0.005, "graph/algorithms", 0))
register(SignalMeta(Signal.COMMUNITY, int, "file", False, "neutral", None, "graph/algorithms", 0))
register(SignalMeta(Signal.IS_ORPHAN, bool, "file", False, "high_is_bad", None, "graph/algorithms", 3))
register(SignalMeta(Signal.ROLE, str, "file", False, "neutral", None, "semantics/roles", 2))
register(SignalMeta(Signal.DEPTH, int, "file", True, "neutral", None, "graph/algorithms", 3))
register(SignalMeta(Signal.BUS_FACTOR, float, "file", True, "high_is_good", 1.0, "temporal/churn", 3))
# ... all 62 signals registered here
```

**Why this works**: You can't typo a signal name (it's an enum, not a string). You can't percentile `community` or `role` (the registry says `percentileable=False`). You can't have two modules computing the same signal (single-owner registration rejects duplicates). The AI coder adds a new signal by adding an enum member + one `register()` call. Forget either → immediate error.

---

## Pattern 2: `graphlib.TopologicalSorter` for Analyzer Ordering

**Inspired by**: SonarQube's `DirectAcyclicGraph.sort()` for MeasureComputers. Python stdlib since 3.9.

**Kills**: C1 (undeclared dependencies), ordering bugs, cycle detection.

**File**: Modify `insights/kernel.py` (~30 lines replacing existing `_resolve_order`)

```python
from graphlib import TopologicalSorter, CycleError

def _resolve_order(self) -> list:
    """Topologically sort analyzers. Catches cycles at startup, not at runtime."""
    ts = TopologicalSorter()

    # Build DAG from requires/provides declarations
    provides_map: Dict[str, str] = {}  # slot -> analyzer_name
    for analyzer in self._analyzers:
        ts.add(analyzer.name)
        for req in analyzer.requires:
            if req in provides_map:
                ts.add(analyzer.name, provides_map[req])  # depends on provider
        for prov in analyzer.provides:
            if prov in provides_map:
                raise ValueError(
                    f"Slot '{prov}' provided by both {provides_map[prov]} and {analyzer.name}"
                )
            provides_map[prov] = analyzer.name

    try:
        order = list(ts.static_order())
    except CycleError as e:
        raise ValueError(f"Analyzer dependency cycle: {e}")

    name_to_analyzer = {a.name: a for a in self._analyzers}
    return [name_to_analyzer[name] for name in order if name in name_to_analyzer]
```

**Bonus**: `TopologicalSorter` supports `prepare()`/`get_ready()`/`done()` for parallel execution within levels. When we want to parallelize structural + temporal (they're independent), the stdlib already supports it. No library needed.

---

## Pattern 3: Typed `Slot[T]` Store with Error Context

**Inspired by**: Dagster's `AssetIn(is_required=False)` for optional dependencies. Railway-oriented programming's Result type adapted to blackboard slots.

**Kills**: C34 (no-git finders fire everywhere), C5/C8 (unclear who computed what), scattered `if X is None` checks.

**File**: `insights/store.py` (~40 lines, replacing raw Optional fields)

```python
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

@dataclass
class Slot(Generic[T]):
    """A typed blackboard slot. Wraps Optional with provenance and error context."""
    _value: Optional[T] = None
    _error: Optional[str] = None
    _produced_by: str = ""

    @property
    def available(self) -> bool:
        return self._value is not None

    @property
    def value(self) -> T:
        if self._value is None:
            raise LookupError(
                f"Slot not populated{f': {self._error}' if self._error else ''}"
            )
        return self._value

    def get(self, default: T = None) -> Optional[T]:
        return self._value if self._value is not None else default

    def set(self, value: T, produced_by: str) -> None:
        self._value = value
        self._produced_by = produced_by

    def set_error(self, error: str, produced_by: str) -> None:
        self._error = error
        self._produced_by = produced_by

@dataclass
class AnalysisStore:
    root_dir: str = ""
    file_metrics: list = field(default_factory=list)             # Always populated by scanner

    # Typed slots — each knows if it's populated, why not, and who wrote it
    file_syntax: Slot[Dict[str, FileSyntax]] = field(default_factory=Slot)
    structural: Slot[CodebaseAnalysis] = field(default_factory=Slot)
    git_history: Slot[GitHistory] = field(default_factory=Slot)
    churn: Slot[Dict[str, ChurnSeries]] = field(default_factory=Slot)
    cochange: Slot[CoChangeMatrix] = field(default_factory=Slot)
    semantics: Slot[Dict[str, FileSemantics]] = field(default_factory=Slot)
    roles: Slot[Dict[str, str]] = field(default_factory=Slot)
    spectral: Slot[SpectralSummary] = field(default_factory=Slot)
    clone_pairs: Slot[List[ClonePair]] = field(default_factory=Slot)
    author_distances: Slot[List[AuthorDistance]] = field(default_factory=Slot)
    architecture: Slot[Architecture] = field(default_factory=Slot)
    signal_field: Slot[SignalField] = field(default_factory=Slot)

    @property
    def available(self) -> set[str]:
        avail = {"files"}
        for name in ["structural", "git_history", "churn", "cochange", "semantics",
                      "roles", "spectral", "clone_pairs", "author_distances",
                      "architecture", "signal_field", "file_syntax"]:
            slot = getattr(self, name)
            if isinstance(slot, Slot) and slot.available:
                avail.add(name)
        return avail
```

**Why this works**:
- Finders can't crash on None — `slot.value` raises a clear error with provenance.
- `slot.available` replaces scattered `if store.X is not None` checks.
- `slot._error` captures WHY something is missing ("git not installed", "temporal analyzer failed") — displayed to user.
- `slot._produced_by` answers "who wrote this?" — debugging aid.
- The kernel checks `slot.available` for requires/provides. Finders never see missing data.

---

## Pattern 4: Phase Validation Contracts

**Inspired by**: Dagster `@asset_check` (validation between pipeline stages, can block downstream execution).

**Kills**: C9 (wrong field names), C5 (missing fields), data integrity bugs that cascade across phases.

**File**: `insights/validation.py` (~80 lines, one function per phase boundary)

```python
"""Run after each analyzer phase. Catches data integrity issues before they propagate."""

from signals.registry import REGISTRY, Signal, signals_by_phase

class ValidationError(Exception):
    """Raised when phase contract is violated. Stops pipeline with clear message."""
    pass

def validate_after_scanning(store):
    """After scanner, before analyzers."""
    if not store.file_metrics:
        raise ValidationError("Scanner produced 0 files")
    paths = {fm.path for fm in store.file_metrics}
    if store.file_syntax.available:
        extra = set(store.file_syntax.value.keys()) - paths
        missing = paths - set(store.file_syntax.value.keys())
        if extra:
            raise ValidationError(f"file_syntax has paths not in file_metrics: {extra}")
        # missing is OK — some files may fail to parse

def validate_after_structural(store):
    """After StructuralAnalyzer."""
    if not store.structural.available:
        return  # Structural might have failed — that's OK, finders will skip
    graph = store.structural.value.graph
    # Every graph node must be a scanned file
    metric_paths = {fm.path for fm in store.file_metrics}
    orphan_nodes = graph.all_nodes - metric_paths
    if orphan_nodes:
        raise ValidationError(f"Graph has {len(orphan_nodes)} nodes not in scanned files")
    # Reverse adjacency must be consistent with forward
    for src, targets in graph.adjacency.items():
        for tgt in targets:
            if src not in graph.reverse.get(tgt, []):
                raise ValidationError(f"Adjacency has {src}→{tgt} but reverse is inconsistent")

def validate_signal_field(store):
    """After SignalFusion. The most critical validation."""
    if not store.signal_field.available:
        return
    field = store.signal_field.value
    metric_paths = {fm.path for fm in store.file_metrics}
    signal_paths = set(field.per_file.keys())
    if signal_paths != metric_paths:
        raise ValidationError(
            f"SignalField covers {len(signal_paths)} files but {len(metric_paths)} were scanned"
        )
    # No percentiles on non-percentileable signals
    allowed = {s.value for s in percentileable_signals()}
    for fs in field.per_file.values():
        bad = set(fs.percentiles.keys()) - allowed
        if bad:
            raise ValidationError(f"Percentiles computed for non-percentileable signals: {bad}")
```

**Wired into kernel**: Validation runs in dev/test (controlled by config flag). Catches wiring errors immediately. In production, can be disabled for speed (these are O(n) checks, trivial vs graph algorithms).

---

## Pattern 5: Fusion Pipeline Builder

**Inspired by**: Typestate pattern (separate classes per state). Research conclusion: full typestate is impractical in Python, but separate-class chaining is lightweight and effective for a fixed 8-step pipeline.

**Kills**: The module_bus_factor ordering bug (steps can't be reordered), future ordering bugs.

**File**: `signals/fusion.py` (~60 lines of structure around existing logic)

```python
class FusionPipeline:
    """Each step returns the next stage type. Enforces ordering via types."""

    def __init__(self, store: AnalysisStore):
        self.store = store
        self.field = SignalField()

    def step1_collect(self) -> "_Collected":
        """Gather raw signals from all store slots into SignalField."""
        # ... fill per-file from scanning, graph, semantics, temporal ...
        # ... fill per-module from architecture ...
        # ... fill global signals ...
        return _Collected(self.field, self.store)

class _Collected:
    def __init__(self, field, store):
        self.field, self.store = field, store

    def step2_raw_risk(self) -> "_RawRisked":
        """Compute raw_risk per file (pre-percentile). Used by health Laplacian."""
        for fs in self.field.per_file.values():
            fs.raw_risk = _compute_raw_risk(fs)
        return _RawRisked(self.field, self.store)

class _RawRisked:
    def step3_normalize(self) -> "_Normalized":
        """Compute percentiles. ABSOLUTE tier skips this."""
        normalize(self.field)
        return _Normalized(self.field, self.store)

class _Normalized:
    def step4_module_temporal(self) -> "_ModuleTemporal":
        """Fill module temporal signals. Safe to read percentiles now."""
        if self.store.architecture.available:
            for mod in self.store.architecture.value.modules.values():
                ms = self.field.per_module.get(mod.path)
                if ms:
                    fill_module_temporal(ms, mod, self.store, self.field)
        return _ModuleTemporal(self.field, self.store)

class _ModuleTemporal:
    def step5_composites(self) -> "_Composited":
        """Compute all composite scores. Requires percentiles + module temporal."""
        compute_composites(self.field)
        return _Composited(self.field, self.store)

class _Composited:
    def step6_laplacian(self) -> SignalField:
        """Health Laplacian. Uses raw_risk, not composites. Final step."""
        if self.store.structural.available:
            self.field.delta_h = compute_health_laplacian(
                self.field, self.store.structural.value.graph
            )
        return self.field

# Usage — the ONLY valid call order:
def build(store: AnalysisStore) -> SignalField:
    return (FusionPipeline(store)
        .step1_collect()
        .step2_raw_risk()
        .step3_normalize()
        .step4_module_temporal()
        .step5_composites()
        .step6_laplacian())
```

**Why this works**: You literally cannot call `step5_composites()` on a `_Collected` object — the method doesn't exist on that class. Mypy catches reordering at type-check time. The AI coder can't get the ordering wrong.

---

## Pattern 6: ThresholdStrategy for Finders

**Inspired by**: Strategy pattern. The signal registry provides absolute thresholds; the strategy handles tier-aware branching.

**Kills**: C16 (6+ finders reimplementing tier logic), C13 (depth sentinel handling).

**File**: `insights/threshold.py` (~25 lines)

```python
from signals.registry import REGISTRY, Signal

class ThresholdCheck:
    """Tier-aware signal threshold checking. Injected into every finder."""

    def __init__(self, field: SignalField):
        self.tier = field.tier

    def above(self, fs: FileSignals, signal: Signal, pctl_threshold: float) -> bool:
        """Is this file above the threshold for this signal?

        FULL/BAYESIAN: uses percentile.
        ABSOLUTE: uses absolute threshold from registry.
        """
        meta = REGISTRY[signal]
        if self.tier == "ABSOLUTE":
            if meta.absolute_threshold is None:
                return False  # No absolute threshold defined → can't evaluate
            raw = getattr(fs, signal.value, 0)
            return raw > meta.absolute_threshold
        return fs.percentiles.get(signal.value, 0) > pctl_threshold

    def below(self, fs: FileSignals, signal: Signal, pctl_threshold: float) -> bool:
        """Inverse of above. For 'high is good' signals."""
        meta = REGISTRY[signal]
        if self.tier == "ABSOLUTE":
            if meta.absolute_threshold is None:
                return False
            raw = getattr(fs, signal.value, 0)
            return raw < meta.absolute_threshold
        return fs.percentiles.get(signal.value, 1.0) < pctl_threshold

# In finders — zero tier logic:
class BugAttractorFinder:
    name = "bug_attractor"
    requires = {"signal_field", "temporal"}

    def find(self, store):
        check = ThresholdCheck(store.signal_field.value)
        for f, fs in store.signal_field.value.per_file.items():
            if fs.fix_ratio > 0.4 and check.above(fs, Signal.PAGERANK, 0.75):
                yield Finding(...)
```

**Why this works**: Finders never touch tier logic. The absolute threshold comes from the signal registry (Pattern 1). One place to get tier handling right, used by all 6+ percentile finders.

---

---

## Pattern 7: Error Taxonomy + Recovery Strategies

**File**: `exceptions/taxonomy.py` (~60 lines)

```python
"""Enterprise error taxonomy with error codes and recovery strategies."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

class ErrorCode(Enum):
    """Structured error codes for observability and debugging."""
    # Scanning errors (SC1xx)
    SC100 = "SC100"  # File read error
    SC101 = "SC101"  # Encoding detection failed
    SC102 = "SC102"  # Tree-sitter parse failed
    SC103 = "SC103"  # Regex fallback failed

    # Semantic errors (SC2xx)
    SC200 = "SC200"  # Concept extraction failed (too few tokens)
    SC201 = "SC201"  # Role classification ambiguous
    SC202 = "SC202"  # TF-IDF computation failed

    # Graph errors (SC3xx)
    SC300 = "SC300"  # Import resolution failed
    SC301 = "SC301"  # Call resolution failed
    SC302 = "SC302"  # Clone detection timeout
    SC303 = "SC303"  # Graph has unreachable nodes

    # Temporal errors (SC4xx)
    SC400 = "SC400"  # Git not found
    SC401 = "SC401"  # Git log parse failed
    SC402 = "SC402"  # Git subprocess timeout
    SC403 = "SC403"  # Shallow clone detected

    # Architecture errors (SC5xx)
    SC500 = "SC500"  # Module detection failed
    SC501 = "SC501"  # Layer inference cycle detected
    SC502 = "SC502"  # Martin metrics undefined (isolated module)

    # Signal errors (SC6xx)
    SC600 = "SC600"  # Percentile on non-percentileable signal
    SC601 = "SC601"  # Composite input missing
    SC602 = "SC602"  # Normalization tier mismatch

    # Finder errors (SC7xx)
    SC700 = "SC700"  # Required signal unavailable
    SC701 = "SC701"  # Threshold evaluation failed
    SC702 = "SC702"  # Confidence computation failed

    # Validation errors (SC8xx)
    SC800 = "SC800"  # Phase contract violated
    SC801 = "SC801"  # Store slot type mismatch
    SC802 = "SC802"  # Adjacency/reverse inconsistent

    # Persistence errors (SC9xx)
    SC900 = "SC900"  # SQLite write failed
    SC901 = "SC901"  # Schema migration failed
    SC902 = "SC902"  # Snapshot corruption detected


@dataclass
class ShannonError(Exception):
    """Base exception with structured context for enterprise logging."""
    message: str
    code: ErrorCode
    context: Dict[str, Any] = field(default_factory=dict)
    recoverable: bool = True
    recovery_hint: Optional[str] = None

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message}"

    def to_json(self) -> Dict[str, Any]:
        """Structured logging format."""
        return {
            "error_code": self.code.value,
            "message": self.message,
            "context": self.context,
            "recoverable": self.recoverable,
            "recovery_hint": self.recovery_hint,
        }


# Domain-specific exceptions
class ScanningError(ShannonError): pass
class SemanticError(ShannonError): pass
class GraphError(ShannonError): pass
class TemporalError(ShannonError): pass
class ArchitectureError(ShannonError): pass
class SignalError(ShannonError): pass
class FinderError(ShannonError): pass
class ValidationError(ShannonError): pass
class PersistenceError(ShannonError): pass
```

**Recovery strategy per error_mode**:

| error_mode | Behavior | Use case |
|------------|----------|----------|
| `"fail"` | Raise exception, halt pipeline | Critical analyzers (StructuralAnalyzer) |
| `"skip"` | Log warning, return empty/None, continue | Optional analyzers (TemporalAnalyzer when git unavailable) |
| `"degrade"` | Partial results, reduced confidence, continue | Finders that can work with subset of signals |

---

## Pattern 8: Structured Logging Format

**File**: `logging_config.py` enhancement (~30 lines)

```python
import json
import logging
from datetime import datetime
from typing import Any, Dict

class StructuredFormatter(logging.Formatter):
    """JSON structured logging for enterprise observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add component context if available
        if hasattr(record, "component"):
            log_entry["component"] = record.component
        if hasattr(record, "error_code"):
            log_entry["error_code"] = record.error_code
        if hasattr(record, "context"):
            log_entry["context"] = record.context

        # Add exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def get_structured_logger(name: str, component: str) -> logging.Logger:
    """Get a logger with structured context."""
    logger = logging.getLogger(name)
    logger = logging.LoggerAdapter(logger, {"component": component})
    return logger


# Usage in analyzers:
# logger = get_structured_logger(__name__, "TemporalAnalyzer")
# logger.warning("Git extraction failed", extra={
#     "error_code": "SC400",
#     "context": {"root_dir": "/path/to/repo", "cause": "git binary not found"}
# })
```

---

## What We Chose NOT to Use (and why)

| Pattern | Why not |
|---------|---------|
| **Dagster as dependency** | Massive dep tree (grpcio, sqlalchemy, alembic). We already have the pattern in 50 lines of kernel.py. |
| **Full typestate (Literal types + cast)** | Python culture clash, requires `cast()` which is unsafe, mypy `--allow-redefinition`. Separate classes (Pattern 5) is simpler. |
| **attrs** | Already depend on Pydantic + dataclasses. Third data library = cognitive overhead. |
| **`dry-python/returns`** | Requires Python 3.10+, we target 3.9+. Roll our own if needed (50 lines). |
| **CodeClimate-style isolated engines** | We NEED cross-signal analysis. Isolation prevents exactly what makes Shannon Insight valuable. |
| **Semgrep's OCaml core** | Single-language tool, different constraints. Their generic AST validates our FileSyntax but the architecture doesn't transfer. |
| **Opportunistic blackboard control** | Non-deterministic. We use deterministic topo-sort (SonarQube pattern). Already the right choice. |
| **Prometheus-style pull-based collection** | We're not a monitoring system. But their registry pattern (collision detection, typed metrics) maps directly to Pattern 1. |

---

## Implementation Order

All 8 patterns are Phase 0 deliverables. Build them BEFORE any feature code.

| Order | Pattern | Lines | Depends on | Blocks |
|:---:|---------|:---:|---|---|
| 1 | Protocol contracts (enhanced) | ~50 | Nothing | Everything |
| 2 | Signal enum + registry | ~120 | Nothing | Patterns 4, 5, 6 |
| 3 | Typed Slot[T] store | ~40 | Nothing | Patterns 4, 5 |
| 4 | graphlib topo-sort | ~30 | Patterns 1, 3 | Kernel |
| 5 | Phase validation | ~80 | Patterns 1, 2, 3 | All phases |
| 6 | Fusion pipeline builder | ~60 | Patterns 1, 2, 3 | Phase 5 |
| 7 | ThresholdStrategy | ~25 | Pattern 2 | Phase 6 finders |
| 8 | Error taxonomy + logging | ~90 | Nothing | All error handling |
| **Total** | | **~495** | | |

**Critical path**: 1 → 2 → 3 → 4 → 5 (must be sequential). Patterns 6, 7, 8 can parallel after 2+3.

After these ~500 lines exist, the remaining ~5000 lines of feature code can't have:
- Signal name typos (enum)
- Duplicate signal computation (single-owner)
- Wrong percentile targets (registry metadata)
- Ordering bugs in fusion (typestate builder)
- Tier-handling bugs in finders (ThresholdStrategy)
- Silent None crashes (typed Slot)
- Data integrity propagation (phase validation)
- Undeclared dependencies (graphlib cycle detection)

---

## Validation: How Production Tools Solve the Same Problems

| Our Pattern | SonarQube | CodeScene | Semgrep | Prometheus |
|-------------|-----------|-----------|---------|------------|
| Signal enum + registry | MeasureComputer declares input/output metrics, DAG validates | Proprietary signal definitions | Rule schema validation | `CollectorRegistry` with `describe()` collision detection |
| Typed Slot store | Sensor output → typed measures in component tree | N/A (monolith) | `Core_result.t` typed output | N/A |
| graphlib topo-sort | `DirectAcyclicGraph.sort()` in LoadMeasureComputersStep | Implicit fixed pipeline | Independent rules (no ordering needed) | N/A |
| Phase validation | `PostMeasuresComputationChecksStep` between phases | N/A | Per-file error isolation + partial AST recovery | N/A |
| Fusion builder | Fixed 65-step sequence in ReportComputationSteps.java | Fixed pipeline stages | 5-stage sequential pipeline | N/A |
| ThresholdStrategy | Quality Gate conditions (ratio-based, not percentile) | Relative ranking + fixed 1-10 scale | Severity set by rule author | N/A |
