# Store (Blackboard)

The AnalysisStore is the blackboard that all analyzers write to and finders read from.

---

## Store Slots (13 total)

| Slot | Type | Written By | Phase |
|------|------|------------|-------|
| file_metrics | list[FileMetrics] | Kernel (input) | 0 |
| file_syntax | dict[str, FileSyntax] | CodeCollector | 1 |
| structural | CodebaseAnalysis | StructuralAnalyzer | 0 |
| git_history | GitHistory | TemporalAnalyzer | 3 |
| cochange | CoChangeMatrix | TemporalAnalyzer | 3 |
| churn | dict[str, ChurnSeries] | TemporalAnalyzer | 3 |
| spectral | SpectralSummary | SpectralAnalyzer | 0 |
| semantics | dict[str, FileSemantics] | SemanticAnalyzer | 2 |
| roles | dict[str, str] | SemanticAnalyzer | 2 |
| clone_pairs | list[ClonePair] | StructuralAnalyzer | 3 |
| author_distances | list[AuthorDistance] | StructuralAnalyzer | 3 |
| architecture | Architecture | ArchitectureAnalyzer | 4 |
| signal_field | SignalField | SignalFusionAnalyzer | 5 |

---

## Current Store (v1)

```python
@dataclass
class AnalysisStore:
    # Inputs (set by kernel before analyzers run)
    root_dir: str = ""
    file_metrics: list[FileMetrics] = field(default_factory=list)

    # Structural signals (set by StructuralAnalyzer)
    structural: Optional[CodebaseAnalysis] = None

    # Temporal signals (set by TemporalAnalyzer)
    git_history: Optional[GitHistory] = None
    cochange: Optional[CoChangeMatrix] = None
    churn: Optional[dict[str, ChurnSeries]] = None

    # Per-file signals (set by PerFileAnalyzer)
    file_signals: Optional[dict[str, dict[str, float]]] = None

    # Spectral signals (set by SpectralAnalyzer)
    spectral: Optional[SpectralSummary] = None

    @property
    def available(self) -> set[str]:
        """Track what signal categories have been populated."""
        avail: set[str] = {"files"}
        if self.structural:
            avail.add("structural")
        if self.cochange or self.churn:
            avail.add("temporal")
        if self.file_signals:
            avail.add("file_signals")
        if self.spectral:
            avail.add("spectral")
        return avail
```

---

## Target Store (v2)

```python
@dataclass
class AnalysisStore:
    # Identity
    root_dir: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tier: Tier = Tier.FULL

    # Inputs
    file_metrics: list[FileMetrics] = field(default_factory=list)

    # Phase 1: Deep parsing
    file_syntax: dict[str, FileSyntax] = field(default_factory=dict)

    # Phase 0: Structural
    structural: Optional[CodebaseAnalysis] = None
    spectral: Optional[SpectralSummary] = None

    # Phase 2: Semantics
    semantics: dict[str, FileSemantics] = field(default_factory=dict)
    roles: dict[str, str] = field(default_factory=dict)

    # Phase 3: Temporal + Graph enrichment
    git_history: Optional[GitHistory] = None
    cochange: Optional[CoChangeMatrix] = None
    churn: dict[str, ChurnSeries] = field(default_factory=dict)
    clone_pairs: list[ClonePair] = field(default_factory=list)
    author_distances: list[AuthorDistance] = field(default_factory=list)

    # Phase 4: Architecture
    architecture: Optional[Architecture] = None

    # Phase 5: Signal fusion
    signal_field: Optional[SignalField] = None

    @property
    def available(self) -> set[str]:
        """Track what signal categories have been populated."""
        avail: set[str] = {"files"}
        if self.file_syntax:
            avail.add("syntax")
        if self.structural:
            avail.add("structural")
        if self.semantics:
            avail.add("semantics")
        if self.git_history or self.churn:
            avail.add("temporal")
        if self.spectral:
            avail.add("spectral")
        if self.architecture:
            avail.add("architecture")
        if self.signal_field:
            avail.add("signals")
        return avail
```

---

## Slot Types

### FileMetrics

```python
@dataclass
class FileMetrics:
    path: str
    language: str
    lines: int
    function_count: int
    class_count: int
    import_count: int
    imports: list[str]
```

### FileSyntax (Phase 1+)

```python
@dataclass
class FileSyntax:
    path: str
    functions: list[FunctionDef]
    classes: list[ClassDef]
    max_nesting: int
    has_main_guard: bool

@dataclass
class FunctionDef:
    name: str
    line: int
    signature_tokens: int
    body_tokens: int
    is_stub: bool

@dataclass
class ClassDef:
    name: str
    line: int
    bases: list[str]
    is_abstract: bool
```

### FileSemantics (Phase 2+)

```python
@dataclass
class FileSemantics:
    path: str
    role: Role
    concepts: list[str]
    concept_weights: dict[str, float]
    concept_count: int
    concept_entropy: float
    naming_drift: float
    docstring_coverage: float
    semantic_coherence: float
```

### ChurnSeries

```python
@dataclass
class ChurnSeries:
    path: str
    total_changes: int
    changes_per_window: list[int]
    churn_trajectory: Trajectory
    churn_slope: float
    churn_cv: float
    authors: dict[str, int]
    bus_factor: float
    author_entropy: float
    fix_ratio: float
    refactor_ratio: float
```

### Architecture (Phase 4+)

```python
@dataclass
class Architecture:
    modules: list[Module]
    layers: dict[str, int]
    violations: list[Violation]

@dataclass
class Module:
    name: str
    files: list[str]
    cohesion: float
    coupling: float
    instability: Optional[float]
    abstractness: float
    main_seq_distance: Optional[float]
    boundary_alignment: float
```

### SignalField (Phase 5+)

```python
@dataclass
class SignalField:
    """Unified signal storage."""

    # Per-file signals
    file_signals: dict[str, dict[Signal, float]]

    # Per-module signals
    module_signals: dict[str, dict[Signal, float]]

    # Global signals
    global_signals: dict[Signal, float]

    # Percentiles
    percentiles: dict[str, dict[Signal, float]]

    # Health Laplacian
    delta_h: dict[str, float]

    def get(self, entity: str, signal: Signal) -> Optional[float]:
        if entity in self.file_signals:
            return self.file_signals[entity].get(signal)
        if entity in self.module_signals:
            return self.module_signals[entity].get(signal)
        return self.global_signals.get(signal)

    def get_pctl(self, path: str, signal: Signal) -> Optional[float]:
        return self.percentiles.get(path, {}).get(signal)
```

---

## Read/Write Protocol

### Analyzers Write

```python
class Analyzer(Protocol):
    name: str
    requires: set[str]    # Slot names
    provides: set[str]    # Slot names

    def analyze(self, store: AnalysisStore) -> None:
        """Write to store. Never read from slots you don't require."""
        ...
```

### Finders Read

```python
class Finder(Protocol):
    name: str
    requires: set[str]    # Slot names

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Read from store. Never write."""
        ...
```

---

## Analyzer Execution Order

Analyzers are topologically sorted by requires/provides:

```python
def resolve_analyzer_order(analyzers: list[Analyzer]) -> list[Analyzer]:
    """
    Topo-sort analyzers by dependencies.
    """
    graph = {}
    for a in analyzers:
        graph[a.name] = set()
        for other in analyzers:
            if a.requires & other.provides:
                graph[a.name].add(other.name)

    sorted_names = list(graphlib.TopologicalSorter(graph).static_order())

    name_to_analyzer = {a.name: a for a in analyzers}
    return [name_to_analyzer[n] for n in sorted_names]
```

### Current Order

1. StructuralAnalyzer (provides: structural)
2. TemporalAnalyzer (provides: git_history, cochange, churn)
3. SpectralAnalyzer (requires: structural, provides: spectral)
4. SemanticAnalyzer (requires: file_syntax, provides: semantics, roles)
5. ArchitectureAnalyzer (requires: structural, provides: architecture)
6. **SignalFusionAnalyzer** (requires: ALL, provides: signal_field) — always last

---

## Graceful Degradation

Finders skip gracefully if required signals unavailable:

```python
def run_finders(store: AnalysisStore, finders: list[Finder]) -> list[Finding]:
    findings = []

    for finder in finders:
        # Check if all required slots are available
        if not finder.requires.issubset(store.available):
            logger.info(f"Skipping {finder.name}: missing {finder.requires - store.available}")
            continue

        try:
            findings.extend(finder.find(store))
        except Exception as e:
            logger.warning(f"{finder.name} failed: {e}")

    return findings
```

---

## Validation

After each analyzer, validate store integrity:

```python
def validate_after_structural(store: AnalysisStore) -> None:
    """Validate after StructuralAnalyzer."""
    assert store.structural is not None
    assert len(store.structural.files) == len(store.file_metrics)

def validate_after_temporal(store: AnalysisStore) -> None:
    """Validate after TemporalAnalyzer."""
    if store.git_history:
        assert store.churn is not None
        assert store.cochange is not None

def validate_signal_field(store: AnalysisStore) -> None:
    """Validate SignalField completeness."""
    sf = store.signal_field
    assert sf is not None

    # Every file should have all required signals
    for path in store.file_metrics:
        assert path.path in sf.file_signals
        signals = sf.file_signals[path.path]
        assert Signal.LINES in signals
        assert Signal.PAGERANK in signals
```
