# Patterns (Finders)

Patterns are declarative rules that detect findings. There are **22 patterns**.

---

## Pattern Model

```python
class PatternScope(Enum):
    FILE = "file"
    FILE_PAIR = "file_pair"
    MODULE = "module"
    MODULE_PAIR = "module_pair"
    CODEBASE = "codebase"

@dataclass
class Pattern:
    name: str
    scope: PatternScope
    severity: float                              # [0, 1]
    requires: set[Signal | RelationType]         # Must be available
    condition: str                               # Human-readable
    predicate: Callable[[FactStore, Any], bool]  # Actual check
    severity_fn: Callable[[FactStore, Any], float]
    evidence_fn: Callable[[FactStore, Any], dict]
    description: str
    remediation: str
    category: str                                # structural, coupling, architecture, team
    hotspot_filtered: bool                       # Requires total_changes > median
    phase: int                                   # When available
```

---

## Pattern Categories

| Category | Count | Patterns |
|----------|-------|----------|
| **Existing (v1)** | 7 | HIGH_RISK_HUB, HIDDEN_COUPLING, GOD_FILE, UNSTABLE_FILE, BOUNDARY_MISMATCH, DEAD_DEPENDENCY, CHRONIC_PROBLEM |
| **AI Code Quality** | 6 | ORPHAN_CODE, HOLLOW_CODE, PHANTOM_IMPORTS, COPY_PASTE_CLONE, FLAT_ARCHITECTURE, NAMING_DRIFT |
| **Social/Team** | 3 | KNOWLEDGE_SILO, CONWAY_VIOLATION, REVIEW_BLINDSPOT |
| **Architecture** | 3 | LAYER_VIOLATION, ZONE_OF_PAIN, ARCHITECTURE_EROSION |
| **Cross-Dimensional** | 3 | WEAK_LINK, BUG_ATTRACTOR, ACCIDENTAL_COUPLING |
| **Total** | **22** | |

---

## Severity Reference

| Pattern | Severity | Category |
|---------|----------|----------|
| HIGH_RISK_HUB | 1.00 | Critical |
| HIDDEN_COUPLING | 0.90 | Critical |
| REVIEW_BLINDSPOT | 0.80 | High |
| GOD_FILE | 0.80 | High |
| WEAK_LINK | 0.75 | High |
| HOLLOW_CODE | 0.71 | High |
| KNOWLEDGE_SILO | 0.70 | High |
| BUG_ATTRACTOR | 0.70 | High |
| UNSTABLE_FILE | 0.70 | High |
| ARCHITECTURE_EROSION | 0.65 | Medium |
| PHANTOM_IMPORTS | 0.65 | Medium |
| FLAT_ARCHITECTURE | 0.60 | Medium |
| ZONE_OF_PAIN | 0.60 | Medium |
| BOUNDARY_MISMATCH | 0.60 | Medium |
| CONWAY_VIOLATION | 0.55 | Medium |
| ORPHAN_CODE | 0.55 | Medium |
| LAYER_VIOLATION | 0.52 | Medium |
| COPY_PASTE_CLONE | 0.50 | Low |
| ACCIDENTAL_COUPLING | 0.50 | Low |
| NAMING_DRIFT | 0.45 | Low |
| DEAD_DEPENDENCY | 0.40 | Low |
| CHRONIC_PROBLEM | base × 1.25 | Amplifier |

---

## Hotspot Filter

Patterns involving temporal signals only fire on "hot" files:

```python
def compute_hotspot_median(store: FactStore) -> float:
    """Median of total_changes across non-test files."""
    changes = [
        store.signals.get(f, Signal.TOTAL_CHANGES, 0)
        for f in store.files()
        if store.signals.get(f, Signal.ROLE) != Role.TEST
    ]
    return statistics.median(changes) if changes else 0.0
```

| Pattern | Hotspot Filtered | Rationale |
|---------|------------------|-----------|
| HIGH_RISK_HUB | Yes | Uses churn_trajectory |
| UNSTABLE_FILE | Yes | Temporal by definition |
| KNOWLEDGE_SILO | Yes | Uses bus_factor |
| REVIEW_BLINDSPOT | Yes | Uses bus_factor |
| WEAK_LINK | Yes | Cross-dimensional |
| BUG_ATTRACTOR | Yes | Uses fix_ratio |
| All others | No | Structural or semantic |

---

## Tier Behavior

| Pattern | ABSOLUTE (<15) | BAYESIAN (15-50) | FULL (50+) |
|---------|---------------|-----------------|------------|
| HIGH_RISK_HUB | Skip | Fire | Fire |
| HIDDEN_COUPLING | Fire | Fire | Fire |
| GOD_FILE | Skip | Fire | Fire |
| UNSTABLE_FILE | Fire | Fire | Fire |
| BOUNDARY_MISMATCH | Skip | Fire | Fire |
| DEAD_DEPENDENCY | Fire | Fire | Fire |
| CHRONIC_PROBLEM | Fire | Fire | Fire |
| ORPHAN_CODE | Fire | Fire | Fire |
| HOLLOW_CODE | Fire | Fire | Fire |
| PHANTOM_IMPORTS | Fire | Fire | Fire |
| COPY_PASTE_CLONE | Fire | Fire | Fire |
| FLAT_ARCHITECTURE | Fire | Fire | Fire |
| NAMING_DRIFT | Fire | Fire | Fire |
| KNOWLEDGE_SILO | Skip | Fire | Fire |
| CONWAY_VIOLATION | Skip | Fire | Fire |
| REVIEW_BLINDSPOT | Skip | Fire | Fire |
| LAYER_VIOLATION | Skip | Fire | Fire |
| ZONE_OF_PAIN | Skip | Fire | Fire |
| ARCHITECTURE_EROSION | Skip | Fire | Fire |
| WEAK_LINK | Skip | Fire | Fire |
| BUG_ATTRACTOR | Skip | Fire | Fire |
| ACCIDENTAL_COUPLING | Skip | Fire | Fire |

**ABSOLUTE tier**: Only 8 patterns fire (boolean, enum, count, or absolute thresholds).

---

## Confidence Scoring

```python
def compute_confidence(
    triggered_conditions: list[tuple[str, float, float, str]]
) -> float:
    """
    Confidence = mean of normalized margins.

    For each condition (signal, actual, threshold, polarity):
    - high_is_bad: margin = (actual - threshold) / (1.0 - threshold)
    - high_is_good: margin = (threshold - actual) / threshold

    Returns [0, 1].
    """
    if not triggered_conditions:
        return 0.0

    margins = []
    for signal, actual, threshold, polarity in triggered_conditions:
        if polarity == "high_is_bad":
            margin = (actual - threshold) / (1.0 - threshold) if threshold < 1 else 0
        else:
            margin = (threshold - actual) / threshold if threshold > 0 else 0
        margins.append(max(0.0, min(1.0, margin)))

    return sum(margins) / len(margins)
```

---

## Finding Identity

Each finding has a stable identity key for tracking across snapshots:

```
FILE scope:       (pattern, file_path)
FILE_PAIR scope:  (pattern, sorted(file_a, file_b))
MODULE scope:     (pattern, module_name)
MODULE_PAIR:      (pattern, sorted(mod_a, mod_b))
CODEBASE scope:   (pattern,)
```

**Rename awareness**: When persistence detects a file rename (via git), identity key is updated.

---

## Finding Model

```python
@dataclass
class Finding:
    id: str                      # Stable identity
    pattern: str                 # Pattern name
    scope: PatternScope
    target: EntityId | tuple[EntityId, EntityId]
    severity: float              # [0, 1]
    confidence: float            # [0, 1]
    evidence: dict               # What triggered it
    description: str
    remediation: str

    # For ranking
    impact: float                # Centrality-weighted

    # For lifecycle
    first_seen: datetime | None
    snapshot_count: int = 1
```

---

## Pattern Documentation

Detailed specifications for each pattern:

- **[01-existing.md](01-existing.md)** — 7 v1 patterns
- **[02-ai-quality.md](02-ai-quality.md)** — 6 AI code quality patterns
- **[03-social-team.md](03-social-team.md)** — 3 social/team patterns
- **[04-architecture.md](04-architecture.md)** — 3 architecture patterns
- **[05-cross-dimensional.md](05-cross-dimensional.md)** — 3 cross-dimensional patterns
