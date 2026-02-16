# Stage 6: Rank

Prioritize findings by importance.

---

## Ranking Formula

```python
def compute_finding_score(finding: Finding, store: FactStore) -> float:
    """
    Score = severity × confidence × impact

    Higher score = more important finding.
    """
    severity = finding.severity      # [0, 1]
    confidence = finding.confidence  # [0, 1]
    impact = compute_impact(finding, store)  # [0, 1]

    return severity * confidence * impact
```

---

## Impact Calculation

Impact reflects how important the target entity is to the codebase.

```python
def compute_impact(finding: Finding, store: FactStore) -> float:
    """
    Impact based on target's centrality.
    """
    if finding.scope == PatternScope.FILE:
        # PageRank percentile
        pctl = store.signals.get(finding.target, "pagerank_pctl", 0.5)
        return pctl

    elif finding.scope == PatternScope.FILE_PAIR:
        # Max of both files' pagerank
        a, b = finding.target
        pctl_a = store.signals.get(a, "pagerank_pctl", 0.5)
        pctl_b = store.signals.get(b, "pagerank_pctl", 0.5)
        return max(pctl_a, pctl_b)

    elif finding.scope == PatternScope.MODULE:
        # Module's mean file pagerank
        files = store.relations.incoming(finding.target, RelationType.IN_MODULE)
        if not files:
            return 0.5
        pctls = [store.signals.get(f.source, "pagerank_pctl", 0.5) for f in files]
        return sum(pctls) / len(pctls)

    elif finding.scope == PatternScope.CODEBASE:
        # Codebase findings always high impact
        return 1.0

    return 0.5  # Default
```

---

## Sorting

```python
def rank_findings(
    findings: list[Finding],
    store: FactStore,
    max_findings: int,
) -> list[Finding]:
    """
    Sort findings by score descending, take top N.
    """
    # Compute scores
    scored = [(f, compute_finding_score(f, store)) for f in findings]

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Take top N
    ranked = [f for f, _ in scored[:max_findings]]

    # Attach rank for display
    for i, finding in enumerate(ranked):
        finding.rank = i + 1

    return ranked
```

---

## Grouping

For output, findings are grouped by scope:

```python
def group_findings(findings: list[Finding]) -> dict[str, list[Finding]]:
    """
    Group findings for structured output.
    """
    groups = {
        "codebase": [],
        "module": [],
        "file": [],
        "file_pair": [],
    }

    for f in findings:
        if f.scope == PatternScope.CODEBASE:
            groups["codebase"].append(f)
        elif f.scope == PatternScope.MODULE:
            groups["module"].append(f)
        elif f.scope == PatternScope.FILE:
            groups["file"].append(f)
        elif f.scope in (PatternScope.FILE_PAIR, PatternScope.MODULE_PAIR):
            groups["file_pair"].append(f)

    return groups
```

---

## Severity Reference

Pre-defined severity values for each pattern:

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

## Deduplication

Findings can be deduplicated by identity key:

```python
def deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    """
    Remove duplicate findings (same pattern + target).
    Keep highest severity.
    """
    seen: dict[str, Finding] = {}

    for f in findings:
        if f.id not in seen or f.severity > seen[f.id].severity:
            seen[f.id] = f

    return list(seen.values())
```

---

## Chronic Problem Amplification

For findings that persist across snapshots:

```python
def amplify_chronic_findings(
    findings: list[Finding],
    persistence_counts: dict[str, int],
) -> list[Finding]:
    """
    Amplify severity of chronic findings.

    Chronic = persists 3+ snapshots.
    Amplification = severity × 1.25 (capped at 1.0)
    """
    amplified = []

    for f in findings:
        count = persistence_counts.get(f.id, 1)

        if count >= 3:
            # Create wrapper finding
            chronic = Finding(
                id=f"chronic_problem:{f.id}",
                pattern="chronic_problem",
                scope=f.scope,
                target=f.target,
                severity=min(1.0, f.severity * 1.25),
                confidence=f.confidence,
                evidence={
                    "base_finding": f.pattern,
                    "persistence_count": count,
                    "first_seen": f.first_seen,
                },
                description=f"This issue has persisted for {count} snapshots.",
                remediation=f.remediation,
            )
            amplified.append(chronic)
        else:
            amplified.append(f)

    return amplified
```
