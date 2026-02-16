# Signals

Signals are measurements on entities. There are **62 signals** in total.

---

## Signal Model

```python
class Signal(Enum):
    """All 62 signals as an enum. Use this for type-safe access."""

    # Per-file signals (1-36)
    LINES = "lines"
    FUNCTION_COUNT = "function_count"
    CLASS_COUNT = "class_count"
    MAX_NESTING = "max_nesting"
    IMPL_GINI = "impl_gini"
    STUB_RATIO = "stub_ratio"
    IMPORT_COUNT = "import_count"
    ROLE = "role"
    CONCEPT_COUNT = "concept_count"
    CONCEPT_ENTROPY = "concept_entropy"
    NAMING_DRIFT = "naming_drift"
    TODO_DENSITY = "todo_density"
    DOCSTRING_COVERAGE = "docstring_coverage"
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
    TOTAL_CHANGES = "total_changes"
    CHURN_TRAJECTORY = "churn_trajectory"
    CHURN_SLOPE = "churn_slope"
    CHURN_CV = "churn_cv"
    BUS_FACTOR = "bus_factor"
    AUTHOR_ENTROPY = "author_entropy"
    FIX_RATIO = "fix_ratio"
    REFACTOR_RATIO = "refactor_ratio"
    RISK_SCORE = "risk_score"
    WIRING_QUALITY = "wiring_quality"

    # Per-module signals (37-51)
    COHESION = "cohesion"
    COUPLING = "coupling"
    INSTABILITY = "instability"
    ABSTRACTNESS = "abstractness"
    MAIN_SEQ_DISTANCE = "main_seq_distance"
    BOUNDARY_ALIGNMENT = "boundary_alignment"
    LAYER_VIOLATION_COUNT = "layer_violation_count"
    ROLE_CONSISTENCY = "role_consistency"
    VELOCITY = "velocity"
    COORDINATION_COST = "coordination_cost"
    KNOWLEDGE_GINI = "knowledge_gini"
    MODULE_BUS_FACTOR = "module_bus_factor"
    MEAN_COGNITIVE_LOAD = "mean_cognitive_load"
    FILE_COUNT = "file_count"
    HEALTH_SCORE = "health_score"

    # Global signals (52-62)
    MODULARITY = "modularity"
    FIEDLER_VALUE = "fiedler_value"
    SPECTRAL_GAP = "spectral_gap"
    CYCLE_COUNT = "cycle_count"
    CENTRALITY_GINI = "centrality_gini"
    ORPHAN_RATIO = "orphan_ratio"
    PHANTOM_RATIO = "phantom_ratio"
    GLUE_DEFICIT = "glue_deficit"
    WIRING_SCORE = "wiring_score"
    ARCHITECTURE_HEALTH = "architecture_health"
    CODEBASE_HEALTH = "codebase_health"
```

---

## Signal Specification

```python
@dataclass
class SignalSpec:
    """Metadata for a signal."""

    signal: Signal
    number: int                   # 1-62
    scope: set[EntityType]        # Which entities have this signal
    dimension: str                # D1-D8
    dtype: type                   # int, float, bool, Enum
    range: str                    # "[0, 1]", "[0, ∞)", etc.
    polarity: Polarity            # HIGH_IS_BAD, HIGH_IS_GOOD, NEUTRAL
    phase: int                    # When it becomes available
    source: str                   # Which module computes it
    percentileable: bool          # Can compute percentile
    absolute_threshold: float | None  # For ABSOLUTE tier
    formula: str                  # How to compute

class Polarity(Enum):
    HIGH_IS_BAD = "high_is_bad"
    HIGH_IS_GOOD = "high_is_good"
    NEUTRAL = "neutral"
```

---

## Signal Counts

| Scope | Count | Signal Numbers |
|-------|-------|----------------|
| Per-file | 36 | #1-36 |
| Per-module | 15 | #37-51 |
| Global | 11 | #52-62 |
| **Total** | **62** | |

---

## Signals by Dimension

| Dimension | Signals |
|-----------|---------|
| D1 SIZE | lines, function_count, class_count, file_count |
| D2 SHAPE | max_nesting, impl_gini, stub_ratio |
| D3 NAMING | role, concept_count, concept_entropy, naming_drift, todo_density, docstring_coverage, role_consistency |
| D4 REFERENCE | import_count, pagerank, betweenness, in_degree, out_degree, blast_radius_size, depth, is_orphan, phantom_import_count, broken_call_count, community, cohesion, coupling, instability, abstractness, main_seq_distance, boundary_alignment, layer_violation_count, modularity, fiedler_value, spectral_gap, cycle_count, centrality_gini, orphan_ratio, phantom_ratio, glue_deficit |
| D5 INFORMATION | compression_ratio, semantic_coherence, cognitive_load, mean_cognitive_load |
| D6 CHANGE | total_changes, churn_trajectory, churn_slope, churn_cv, velocity |
| D7 AUTHORSHIP | bus_factor, author_entropy, knowledge_gini, module_bus_factor, coordination_cost |
| D8 INTENT | fix_ratio, refactor_ratio |
| Composite | risk_score, wiring_quality, health_score, wiring_score, architecture_health, codebase_health |

---

## Signals by Phase

| Phase | New Signals | Cumulative |
|-------|-------------|------------|
| 0 | #1-3, 7, 14-18, 23-24, 52-55 | 15 |
| 1 | #4-6, 12, 26 | 20 |
| 2 | #8-11, 13, 25 | 26 |
| 3 | #19-21, 27-34, 56-59 | 40 |
| 4 | #37-44, 50 | 49 |
| 5 | #35-36, 45-49, 51, 60-62 | 62 |

---

## Polarity Summary

| Polarity | Count | Examples |
|----------|-------|----------|
| HIGH_IS_BAD | 32 | pagerank, churn_cv, stub_ratio, fix_ratio |
| HIGH_IS_GOOD | 14 | bus_factor, semantic_coherence, health_score |
| NEUTRAL | 16 | class_count, in_degree, age_days, role |

---

## Signal Documentation

Detailed signal specifications are in:

- **[01-per-file.md](01-per-file.md)** — Signals #1-36 (36 signals)
- **[02-per-module.md](02-per-module.md)** — Signals #37-51 (15 signals)
- **[03-global.md](03-global.md)** — Signals #52-62 (11 signals)

---

## SignalStore

```python
class SignalStore:
    """Entity × Signal × Time → Value"""

    def __init__(self):
        self._data: dict[tuple[EntityId, Signal], SignalValue] = {}
        self._history: dict[tuple[EntityId, Signal], list[SignalValue]] = {}

    def set(
        self,
        entity: EntityId,
        signal: Signal,
        value: Any,
        timestamp: datetime | None = None,
    ) -> None:
        """Set a signal value."""
        timestamp = timestamp or datetime.now()
        sv = SignalValue(entity, signal, value, timestamp)
        self._data[(entity, signal)] = sv
        self._history.setdefault((entity, signal), []).append(sv)

    def get(
        self,
        entity: EntityId,
        signal: Signal,
        default: Any = None,
    ) -> Any:
        """Get latest signal value."""
        sv = self._data.get((entity, signal))
        return sv.value if sv else default

    def has(self, entity: EntityId, signal: Signal) -> bool:
        """Check if signal exists for entity."""
        return (entity, signal) in self._data

    def has_any(self, signal: Signal) -> bool:
        """Check if signal exists for any entity."""
        return any(k[1] == signal for k in self._data)

    def all_values(self, signal: Signal) -> list[tuple[EntityId, Any]]:
        """Get all values for a signal across entities."""
        return [
            (k[0], v.value)
            for k, v in self._data.items()
            if k[1] == signal
        ]

    def history(
        self,
        entity: EntityId,
        signal: Signal,
    ) -> list[SignalValue]:
        """Get historical values for a signal."""
        return self._history.get((entity, signal), [])

@dataclass
class SignalValue:
    entity: EntityId
    signal: Signal
    value: Any
    timestamp: datetime
    confidence: float = 1.0
```

---

## Percentile Computation

```python
def compute_percentile(
    store: SignalStore,
    entity: EntityId,
    signal: Signal,
) -> float | None:
    """
    Compute percentile for a signal value.

    pctl(signal, f) = |{v : signal(v) ≤ signal(f)}| / |all_files|

    Returns None if signal not available.
    """
    value = store.get(entity, signal)
    if value is None:
        return None

    all_values = [v for _, v in store.all_values(signal) if v is not None]
    if not all_values:
        return None

    count_le = sum(1 for v in all_values if v <= value)
    return count_le / len(all_values)
```

---

## Division-by-Zero Guards

Many signal formulas require guards:

```python
def safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Division with zero guard."""
    return numerator / denominator if denominator != 0 else default

# Examples:
# stub_ratio: stubs / max(functions, 1)
# instability: Ce / max(Ca + Ce, 1)
# normalized pagerank: pr / max(max_pr, 1e-10)
```

---

## Gini Coefficient Formula

Used for impl_gini, centrality_gini, knowledge_gini:

```python
def compute_gini(values: list[float]) -> float:
    """
    G = (2 × Σᵢ i × xᵢ) / (n × Σ xᵢ) - (n + 1) / n

    where xᵢ sorted ascending, i is 1-indexed.
    G = 0: perfect equality
    G = 1: maximum inequality
    """
    if not values or sum(values) == 0:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)
    total = sum(sorted_values)

    weighted_sum = sum((i + 1) * v for i, v in enumerate(sorted_values))

    return (2 * weighted_sum) / (n * total) - (n + 1) / n
```

---

## Shannon Entropy Formula

Used for author_entropy, concept_entropy:

```python
def compute_entropy(counts: dict[str, int]) -> float:
    """
    H = -Σ p(x) × log₂(p(x))

    H = 0: single value (certainty)
    H = log₂(n): uniform distribution (max uncertainty)
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy
```
