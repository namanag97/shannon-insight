# Stage 5: Detect

Run patterns against the FactStore to produce findings.

---

## Pattern Execution

```python
def run_patterns(store: FactStore, patterns: list[Pattern]) -> list[Finding]:
    """
    Execute all patterns that can run given available signals.
    """
    findings = []

    # Compute hotspot median (for hotspot-filtered patterns)
    hotspot_median = compute_hotspot_median(store)

    for pattern in patterns:
        # Check if pattern can run in this tier
        if not pattern_can_run(pattern, store.tier):
            continue

        # Check if required signals are available
        if not all(store.signals.has_any(s) for s in pattern.requires):
            continue

        # Run pattern based on scope
        if pattern.scope == PatternScope.FILE:
            findings.extend(run_file_pattern(pattern, store, hotspot_median))
        elif pattern.scope == PatternScope.FILE_PAIR:
            findings.extend(run_pair_pattern(pattern, store))
        elif pattern.scope == PatternScope.MODULE:
            findings.extend(run_module_pattern(pattern, store))
        elif pattern.scope == PatternScope.CODEBASE:
            findings.extend(run_codebase_pattern(pattern, store))

    return findings
```

---

## Hotspot Filter

Patterns involving temporal signals only fire on "hot" files:

```python
def compute_hotspot_median(store: FactStore) -> float:
    """
    Median of total_changes across non-test files.
    """
    changes = []
    for f in store.files():
        role = store.signals.get(f, Signal.ROLE)
        if role != Role.TEST:
            total = store.signals.get(f, Signal.TOTAL_CHANGES, 0)
            changes.append(total)

    return statistics.median(changes) if changes else 0.0

def passes_hotspot_filter(
    entity: EntityId,
    store: FactStore,
    hotspot_median: float,
    pattern: Pattern,
) -> bool:
    """
    Returns True if file passes hotspot filter.
    Structural-only patterns always pass.
    """
    if not pattern.hotspot_filtered:
        return True

    total_changes = store.signals.get(entity, Signal.TOTAL_CHANGES, 0)
    return total_changes > hotspot_median
```

### Hotspot-Filtered vs Structural-Only

| Pattern | Hotspot | Rationale |
|---------|---------|-----------|
| HIGH_RISK_HUB | Yes | Temporal signals in condition |
| UNSTABLE_FILE | Yes | Temporal by definition |
| KNOWLEDGE_SILO | Yes | Uses bus_factor (temporal) |
| REVIEW_BLINDSPOT | Yes | Uses bus_factor (temporal) |
| WEAK_LINK | Yes | Cross-dimensional |
| BUG_ATTRACTOR | Yes | Uses fix_ratio (temporal) |
| GOD_FILE | No | Structural complexity |
| ORPHAN_CODE | No | Structural-only |
| HOLLOW_CODE | No | Structural-only |
| PHANTOM_IMPORTS | No | Structural-only |
| COPY_PASTE_CLONE | No | Structural-only |
| FLAT_ARCHITECTURE | No | Structural-only |
| NAMING_DRIFT | No | Structural-only |
| HIDDEN_COUPLING | No | Co-change is inherently temporal |
| DEAD_DEPENDENCY | No | Structural with history |
| LAYER_VIOLATION | No | Structural (architecture) |
| ZONE_OF_PAIN | No | Structural (Martin metrics) |
| ACCIDENTAL_COUPLING | No | Structural + semantic |

---

## File Pattern Execution

```python
def run_file_pattern(
    pattern: Pattern,
    store: FactStore,
    hotspot_median: float,
) -> list[Finding]:
    """
    Run pattern on each file.
    """
    findings = []

    for f in store.files():
        # Hotspot filter
        if not passes_hotspot_filter(f, store, hotspot_median, pattern):
            continue

        # Check predicate
        if pattern.predicate(store, f):
            # Compute severity
            severity = pattern.severity(store, f)

            # Compute confidence
            evidence = pattern.evidence(store, f)
            confidence = compute_confidence(evidence.get("triggered_conditions", []))

            findings.append(Finding(
                id=f"{pattern.name}:{f.key}",
                pattern=pattern.name,
                scope=PatternScope.FILE,
                target=f,
                severity=severity,
                confidence=confidence,
                evidence=evidence,
                description=pattern.description,
                remediation=pattern.remediation,
            ))

    return findings
```

---

## Pair Pattern Execution

```python
def run_pair_pattern(pattern: Pattern, store: FactStore) -> list[Finding]:
    """
    Run pattern on file pairs.

    Optimization: Only check pairs with relevant relationships.
    """
    findings = []
    files = list(store.files())

    # Determine which pairs to check based on pattern
    if pattern.name == "hidden_coupling":
        # Check pairs with high co-change but no import
        pairs = get_high_cochange_pairs(store)
    elif pattern.name == "dead_dependency":
        # Check pairs with import but low co-change
        pairs = get_import_pairs(store)
    elif pattern.name == "copy_paste_clone":
        # Check NCD clone pairs
        pairs = get_clone_pairs(store)
    elif pattern.name == "accidental_coupling":
        # Check import pairs with low concept overlap
        pairs = get_import_pairs(store)
    else:
        # Default: all pairs (expensive)
        pairs = list(combinations(files, 2))

    for a, b in pairs:
        if pattern.predicate(store, (a, b)):
            severity = pattern.severity(store, (a, b))
            evidence = pattern.evidence(store, (a, b))
            confidence = compute_confidence(evidence.get("triggered_conditions", []))

            # Stable identity key: sorted paths
            key = ":".join(sorted([a.key, b.key]))

            findings.append(Finding(
                id=f"{pattern.name}:{key}",
                pattern=pattern.name,
                scope=PatternScope.FILE_PAIR,
                target=(a, b),
                severity=severity,
                confidence=confidence,
                evidence=evidence,
                description=pattern.description,
                remediation=pattern.remediation,
            ))

    return findings
```

---

## Confidence Scoring

```python
def compute_confidence(
    triggered_conditions: list[tuple[str, float, float, str]]
) -> float:
    """
    Confidence = mean of normalized margins.

    Args:
        triggered_conditions: [(signal_name, actual, threshold, polarity), ...]
        polarity: "high_is_bad" or "high_is_good"

    Returns:
        Confidence in [0, 1]
    """
    if not triggered_conditions:
        return 0.0

    margins = []
    for signal, actual, threshold, polarity in triggered_conditions:
        if polarity == "high_is_bad":
            # Higher = worse. Margin = how much above threshold.
            if threshold >= 1.0:
                margin = 0.0
            else:
                margin = (actual - threshold) / (1.0 - threshold)
        else:  # high_is_good
            # Lower = worse. Margin = how much below threshold.
            if threshold <= 0.0:
                margin = 0.0
            else:
                margin = (threshold - actual) / threshold

        margins.append(max(0.0, min(1.0, margin)))

    return sum(margins) / len(margins)
```

**Example**:
```
HIGH_RISK_HUB:
  pctl(pagerank) = 0.95, threshold = 0.90, polarity = high_is_bad
  margin = (0.95 - 0.90) / (1.0 - 0.90) = 0.50

  pctl(blast_radius) = 0.98, threshold = 0.90, polarity = high_is_bad
  margin = (0.98 - 0.90) / (1.0 - 0.90) = 0.80

  confidence = mean([0.50, 0.80]) = 0.65
```

---

## Tier Behavior

Which patterns fire in each tier:

| Pattern | ABSOLUTE (<15) | BAYESIAN (15-50) | FULL (50+) |
|---------|---------------|-----------------|------------|
| HIGH_RISK_HUB | Skip | Fire | Fire |
| HIDDEN_COUPLING | Fire | Fire | Fire |
| GOD_FILE | Skip | Fire | Fire |
| UNSTABLE_FILE | Fire | Fire | Fire |
| BOUNDARY_MISMATCH | Skip | Fire | Fire |
| DEAD_DEPENDENCY | Fire | Fire | Fire |
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
| CHRONIC_PROBLEM | Fire | Fire | Fire |

**ABSOLUTE tier**: Only 8 patterns fire (those using boolean, enum, count, or absolute thresholds).

---

## Pattern Validation

Before running patterns, validate signal polarity usage:

```python
def validate_pattern(pattern: Pattern) -> list[str]:
    """
    Validate pattern respects signal polarities.
    """
    errors = []

    for signal, operator, threshold in pattern.conditions:
        meta = SIGNAL_REGISTRY[signal]

        if operator == ">" and meta.polarity == "high_is_good":
            errors.append(
                f"{pattern.name}: Signal {signal} is high=GOOD but condition uses > (expecting bad)"
            )

        if operator == "<" and meta.polarity == "high_is_bad":
            errors.append(
                f"{pattern.name}: Signal {signal} is high=BAD but condition uses < (expecting good)"
            )

    return errors
```
