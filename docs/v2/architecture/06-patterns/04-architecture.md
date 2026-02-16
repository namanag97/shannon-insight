# Architecture Patterns

3 patterns for detecting architectural issues.

---

## 17. LAYER_VIOLATION

Dependency that violates layer ordering.

| Property | Value |
|----------|-------|
| **Scope** | MODULE_PAIR |
| **Severity** | 0.52 |
| **Phase** | 4 |
| **Hotspot** | No |
| **Requires** | DEPENDS_ON, layer assignments |

### Condition

```python
backward_edge(M₁, M₂) OR skip_edge(M₁, M₂)
```

Where:
- `backward_edge`: dependency from higher layer to lower layer
- `skip_edge`: dependency that skips intermediate layers

### Layer Detection

```python
def infer_layers(store: FactStore) -> dict[str, int]:
    """
    Infer layer ordering from dependency structure.

    1. Build module dependency DAG
    2. Topological sort
    3. Assign layers based on topological order

    Returns: module → layer (0 = bottom, higher = upper)
    """
    modules = list(store.modules())
    deps = {}  # module → set of modules it depends on

    for m in modules:
        deps[m.key] = set()
        for rel in store.relations.outgoing(m, RelationType.DEPENDS_ON):
            deps[m.key].add(rel.target.key)

    # Topological sort
    sorted_modules = topological_sort(deps)

    # Assign layers
    layers = {}
    for i, m in enumerate(sorted_modules):
        layers[m] = i

    return layers

def is_backward_edge(source_module: str, target_module: str, layers: dict[str, int]) -> bool:
    """
    Backward edge: source at higher layer depends on target at lower layer.
    This is actually EXPECTED in normal dependency flow.

    Violation: source at LOWER layer depends on target at HIGHER layer.
    """
    return layers.get(source_module, 0) < layers.get(target_module, 0)
```

### Evidence

- **IR4**: source/target layers
- Violating import symbols

### Remediation

"Inject dependency or restructure to respect layer ordering."

### Effort

MEDIUM

---

## 18. ZONE_OF_PAIN

Module that is concrete and stable (hard to change).

| Property | Value |
|----------|-------|
| **Scope** | MODULE |
| **Severity** | 0.60 |
| **Phase** | 4 |
| **Hotspot** | No |
| **Requires** | abstractness, instability |

### Condition

```python
instability IS NOT None AND  # Guard for isolated modules
abstractness < 0.3 AND
instability < 0.3
```

### Martin's Main Sequence

```
        1.0
         │
Abstract │  Zone of
         │  Uselessness
         │     ╲
    0.5  │      ╲
         │       ╲  Main
         │        ╲ Sequence
         │         ╲
    0.0  ├──────────╲───────
         0.0        0.5     1.0
                 Instability

Zone of Pain: A < 0.3, I < 0.3 (bottom-left)
Zone of Uselessness: A > 0.7, I > 0.7 (top-right)
Main Sequence: A + I ≈ 1 (diagonal)
```

### Evidence

- **IR4**: A (abstractness), I (instability), D (distance)
- Dependents count

### Remediation

"Concrete and stable — hard to change. Extract interfaces or reduce dependents."

### Effort

HIGH

### Edge Case

**instability = None**: Isolated modules (Ca + Ce = 0) have no meaningful instability. ZONE_OF_PAIN must NOT fire for these modules.

```python
def zone_of_pain_predicate(store: FactStore, module: EntityId) -> bool:
    instability = store.signals.get(module, Signal.INSTABILITY)

    # Guard: skip isolated modules
    if instability is None:
        return False

    abstractness = store.signals.get(module, Signal.ABSTRACTNESS, 0)

    return abstractness < 0.3 and instability < 0.3
```

---

## 19. ARCHITECTURE_EROSION

Violation rate increasing over time.

| Property | Value |
|----------|-------|
| **Scope** | CODEBASE |
| **Severity** | 0.65 |
| **Phase** | 7 |
| **Hotspot** | No |
| **Requires** | layer_violation_count over 3+ snapshots |

### Condition

```python
violation_rate increasing over 3+ consecutive snapshots
```

Where:
```
violation_rate = violating_cross_module_edges / total_cross_module_edges
```

### Evidence

- **IR4**: violation_rate time series
- **IR6**: persistence (snapshot history)

### Remediation

"Architecture is actively eroding. Schedule structural refactoring."

### Effort

HIGH

### Implementation

```python
def architecture_erosion_predicate(store: FactStore, history: SnapshotHistory) -> bool:
    """
    Check if violation_rate is increasing over 3+ snapshots.
    """
    snapshots = history.recent(count=3)
    if len(snapshots) < 3:
        return False

    rates = [s.signals.get(Signal.VIOLATION_RATE) for s in snapshots]

    # Check for strictly increasing
    return rates[0] < rates[1] < rates[2]

def violation_rate(store: FactStore) -> float:
    """
    Compute current violation rate.
    """
    modules = list(store.modules())

    total_edges = 0
    violating_edges = 0

    for rel in store.relations.by_type(RelationType.DEPENDS_ON):
        total_edges += 1
        if is_violation(rel, store):
            violating_edges += 1

    return violating_edges / total_edges if total_edges > 0 else 0.0
```
