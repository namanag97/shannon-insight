# Existing Patterns (v1)

7 patterns from v1, upgraded with multi-IR evidence.

---

## 1. HIGH_RISK_HUB

Central file with high complexity and volatility.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 1.00 |
| **Phase** | 0 |
| **Hotspot** | Yes |
| **Requires** | pagerank, blast_radius_size, cognitive_load, churn_trajectory, total_changes |

### Condition

```python
pctl(pagerank) > 0.90 AND
pctl(blast_radius_size) > 0.90 AND
(pctl(cognitive_load) > 0.90 OR churn_trajectory ∈ {CHURNING, SPIKING})
```

### Evidence

- **IR3**: pagerank value, blast radius
- **IR5t**: churn trajectory, fix_ratio
- **IR2**: concept_count
- **IR5t**: bus_factor
- **IR5s**: Δh (health Laplacian)

### Remediation

"Split responsibilities. Pair-program to spread knowledge."

### Effort

HIGH

---

## 2. HIDDEN_COUPLING

Files that change together but have no explicit dependency.

| Property | Value |
|----------|-------|
| **Scope** | FILE_PAIR |
| **Severity** | 0.90 |
| **Phase** | 3 |
| **Hotspot** | No |
| **Requires** | COCHANGES_WITH, IMPORTS |

### Condition

```python
lift(A, B) ≥ 2.0 AND
confidence(A, B) ≥ 0.5 AND
NOT imports(A, B) AND NOT imports(B, A)
```

Where:
- `lift = P(A ∩ B) / (P(A) × P(B))`
- `confidence = P(A ∩ B) / P(A)`

### Evidence

- **G1**: no import edge
- **G4**: co-change count, lift, confidence
- **G6**: semantic similarity (if available)

### Remediation

"Extract shared concept or make dependency explicit."

### Effort

MEDIUM

---

## 3. GOD_FILE

Large file with too many concepts.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.80 |
| **Phase** | 2 |
| **Hotspot** | No |
| **Requires** | cognitive_load, semantic_coherence |

### Condition

```python
pctl(cognitive_load) > 0.90 AND
pctl(semantic_coherence) < 0.20
```

Note: semantic_coherence is HIGH_IS_GOOD, so we check for LOW percentile.

### Evidence

- **IR1**: function_count
- **IR2**: concept_count, concept_entropy
- **IR5**: cognitive_load percentile, coherence percentile

### Remediation

"Split by concept clusters. Each concept = a candidate file."

### Effort

HIGH

---

## 4. UNSTABLE_FILE

File with erratic change patterns.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.70 |
| **Phase** | 3 |
| **Hotspot** | Yes |
| **Requires** | churn_trajectory, total_changes |

### Condition

```python
churn_trajectory ∈ {CHURNING, SPIKING} AND
total_changes > median(total_changes)
```

### Evidence

- **IR5t**: trajectory, total changes, churn_slope, churn_cv

### Remediation

"Investigate why this file isn't stabilizing. Check fix_ratio."

### Effort

MEDIUM

---

## 5. BOUNDARY_MISMATCH

Directory boundary doesn't match dependency structure.

| Property | Value |
|----------|-------|
| **Scope** | MODULE |
| **Severity** | 0.60 |
| **Phase** | 4 |
| **Hotspot** | No |
| **Requires** | boundary_alignment, community, file_count |

### Condition

```python
boundary_alignment < 0.7 AND
file_count >= 3
```

### Evidence

- **IR3**: community assignments for each file
- **IR4**: boundary_alignment value
- File list with community IDs

### Remediation

"Directory boundary doesn't match dependency structure. Consider reorganizing."

### Effort

HIGH

---

## 6. DEAD_DEPENDENCY

Import edge with no co-change history.

| Property | Value |
|----------|-------|
| **Scope** | FILE_PAIR |
| **Severity** | 0.40 |
| **Phase** | 3 |
| **Hotspot** | No |
| **Requires** | IMPORTS, COCHANGES_WITH, total_changes |

### Condition

```python
imports(A, B) AND
cochange_count(A, B) = 0 AND
total_changes(A) >= 50 AND
total_changes(B) >= 50
```

Both files must have significant history (50+ commits) to rule out new files.

### Evidence

- **G1**: structural edge with imported symbols
- **G4**: zero co-changes over N commits

### Remediation

"This import may be dead. Verify the imported symbols are actually used."

### Effort

LOW

---

## 7. CHRONIC_PROBLEM

Finding that persists across 3+ snapshots.

| Property | Value |
|----------|-------|
| **Scope** | (wraps another finding) |
| **Severity** | base_severity × 1.25 |
| **Phase** | 7 |
| **Hotspot** | No |
| **Requires** | finding_lifecycle (persistence) |

### Condition

```python
same finding (by stable ID) persists across 3+ snapshots
```

### Evidence

- **IR6**: first_seen, persistence_count, trend

### Remediation

"This issue has persisted for N snapshots. Prioritize resolution."

### Effort

(inherits from base finding)

### Implementation

```python
def amplify_chronic_findings(
    findings: list[Finding],
    persistence: dict[str, int],  # finding_id → snapshot_count
) -> list[Finding]:
    result = []
    for f in findings:
        count = persistence.get(f.id, 1)
        if count >= 3:
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
            result.append(chronic)
        else:
            result.append(f)
    return result
```
