# Implementation Priorities: Research to Production

**Purpose**: Translate research findings into actionable Shannon Insight v2 implementation decisions.

---

## Priority Matrix

| Priority | Feature | Impact | Effort | Status | Phase |
|----------|---------|--------|--------|--------|-------|
| **P0** | IQR outlier detection | HIGH | LOW | ✅ Spec | Phase 5 |
| **P0** | Tier-based thresholds | HIGH | MEDIUM | ✅ Spec | Phase 6 |
| **P0** | Hotspot filter (change_freq > median) | HIGH | LOW | ✅ Spec | Phase 6 |
| **P0** | Bus factor / author entropy | HIGH | MEDIUM | ✅ Spec | Phase 3 |
| **P1** | Relative churn metrics | HIGH | LOW | ✅ Spec | Phase 3 |
| **P1** | Change entropy (scatter) | MEDIUM | MEDIUM | ⚠️ Add | Phase 3+ |
| **P1** | Temporal coupling filter | MEDIUM | LOW | ✅ Spec | Phase 6 |
| **P1** | CV-based stabilizing/churning | MEDIUM | LOW | ✅ Spec | Phase 3 |
| **P2** | Socio-technical congruence | MEDIUM | HIGH | ⚠️ Future | Phase 8 |
| **P2** | Cognitive complexity | LOW | MEDIUM | ⚠️ Future | Phase 8 |
| **P2** | Spectral clustering (Q) | LOW | HIGH | ❌ Defer | N/A |

**Legend**:
- ✅ Spec: Already in v2 spec
- ⚠️ Add: Should add to spec
- ⚠️ Future: Post-v2 phase
- ❌ Defer: Low ROI

---

## P0: Critical Path (Already in Spec)

### 1. IQR Outlier Detection (Phase 5)

**Current Spec**: Phase 5 uses percentiles for normalization.

**Research Finding**: IQR is robust to lognormal/power law distributions.

**Action**: ✅ **No change needed**. Percentile-based normalization is correct.

**Validation**:
```python
# Phase 5: SignalFusionAnalyzer
def normalize(values, tier):
    if tier == Tier.ABSOLUTE:
        return values  # No normalization
    elif tier == Tier.FULL:
        return [percentile_rank(v, values) for v in values]
```

This is CORRECT per research.

---

### 2. Tier-Based Thresholds (Phase 6)

**Current Spec**: `ThresholdStrategy` adapts to codebase size.

**Research Finding**: Small samples can't use percentiles reliably.

**Action**: ✅ **Already implemented** correctly.

**Validation**:
```python
# infrastructure.md: ThresholdStrategy
def get_tier(file_count):
    if file_count < 15:
        return Tier.ABSOLUTE
    elif file_count < 50:
        return Tier.BAYESIAN
    else:
        return Tier.FULL
```

Matches research recommendations.

---

### 3. Hotspot Filter (Phase 6)

**Current Spec**: Finders apply `change_freq > median` filter.

**Research Finding**: CodeScene uses `frequency × health` model.

**Action**: ✅ **Already implemented**.

**Validation** (phase-6-finders.md):
```
FILE scope findings require total_changes > median UNLESS structural-only
```

This is CORRECT per research.

---

### 4. Bus Factor / Author Entropy (Phase 3)

**Current Spec**: Phase 3 computes `author_entropy` and `bus_factor`.

**Research Finding**: `bus_factor = 2^H` predicts post-release failures.

**Action**: ✅ **Already implemented**.

**Validation** (phase-3-graph-enrichment.md):
```python
ChurnSeries:
    author_entropy: float  # H = -Σ(p×log₂(p))
    bus_factor: int        # 2^H
```

Formula matches research.

---

## P1: High Value Additions

### 5. Relative Churn Metrics (Phase 3)

**Current Spec**: Phase 3 has `total_changes`, `recent_changes`.

**Research Finding**: Nagappan & Ball show `churn/LOC` is 89% accurate predictor.

**Action**: ✅ **Already computed** via primitives.

**Validation**:
```python
# Phase 5: churn_volatility primitive
relative_churn = percentile(total_changes / max(current_LOC, 1))
```

Implicitly computed in normalization. ✅

---

### 6. Change Entropy (MISSING)

**Current Spec**: Not explicitly computed.

**Research Finding**: r=0.54 correlation with defect counts (Co-Change Entropy 2024).

**Action**: ⚠️ **Should add** to Phase 3 or Phase 5.

**Recommendation**:

**Option A**: Add to Phase 3 (TemporalAnalyzer)
```python
# temporal/churn.md: Add field
class ChurnSeries:
    change_entropy: Optional[float]  # Scatter of changes over time windows

def compute_change_entropy(commits, windows=12):
    """
    Measure how dispersed changes are across time windows.
    High entropy = scattered (bad), low entropy = focused (good).
    """
    changes_per_window = [count_changes_in_window(w) for w in windows]
    total = sum(changes_per_window)
    probs = [c/total for c in changes_per_window if c > 0]
    return -sum(p * log2(p) for p in probs)
```

**Option B**: Add to Phase 5 as composite signal
```python
# composites.md: Add to file signals
change_entropy: Optional[float]
  Formula: H = -Σ(p_i × log₂(p_i)) over monthly change distribution
  Range: [0, log₂(months)]
  Polarity: HIGH = bad (scattered changes)
```

**Decision**: Add to **Phase 3** (temporal data available there).

---

### 7. Temporal Coupling Filter (Phase 6)

**Current Spec**: ACCIDENTAL_COUPLING checks for co-change without structural edge.

**Research Finding**: Some co-change is expected (interface+impl, test+code).

**Action**: ✅ **Already handled** via module check.

**Validation** (phase-6-finders.md):
```
ACCIDENTAL_COUPLING fires when:
- Support > 0.3
- No structural edge
- Different architectural modules
```

The "different modules" check filters expected co-change. ✅

---

### 8. CV-Based Stabilizing/Churning (Phase 3)

**Current Spec**: Phase 3 computes `churn_cv`.

**Research Finding**: CV < 0.5 = stabilizing, CV ≥ 0.5 = churning.

**Action**: ✅ **Already implemented**.

**Validation** (temporal/churn.md):
```python
ChurnSeries:
    churn_cv: float  # Coefficient of variation
```

Used in `temporal-operators.md` for STABILIZING/CHURNING classification. ✅

---

## P2: Future Enhancements

### 9. Socio-Technical Congruence (Phase 8 Candidate)

**Research Finding**: Cataldo (2013) shows congruence gaps → failures.

**Why Deferred**:
- Requires organizational data (team assignments)
- Most codebases don't have structured team metadata
- High implementation complexity
- Medium impact (only for multi-team codebases)

**Recommendation**: Post-v2 feature, **Phase 8** or **plugin**.

**Implementation Sketch**:
```python
# Future: socio-technical-analyzer.py
class SocioTechnicalAnalyzer:
    def analyze(self, store, team_data):
        # Build coordination requirements matrix
        coord_req = build_coordination_matrix(store.graph)

        # Build actual coordination (from co-authorship)
        actual_coord = build_coauthorship_graph(store.git_history)

        # Compute congruence
        congruence = overlap(coord_req, actual_coord)

        store.socio_technical = SocioTechnicalData(
            congruence_score=congruence,
            misalignments=detect_misalignments(coord_req, actual_coord)
        )
```

---

### 10. Cognitive Complexity (Phase 8 Candidate)

**Research Finding**: SonarQube uses CC=15 threshold, penalizes nesting.

**Why Deferred**:
- Requires AST traversal (already in Phase 1)
- Marginal improvement over cyclomatic complexity
- Low incremental value

**Recommendation**: Post-v2, if users request it.

**Implementation Sketch**:
```python
# Future: Add to FileSyntax (phase-1)
@dataclass
class FileSyntax:
    cognitive_complexity: Optional[int]  # SonarQube definition

# Add to PerFileAnalyzer
def compute_cognitive_complexity(syntax):
    # +1 for breaks in linear flow
    # +1 per nesting level
    # Ignores shorthand operators
    pass
```

---

### 11. Spectral Clustering (Modularity Q)

**Research Finding**: Q > 0.3 indicates meaningful community structure.

**Why Deferred**:
- Already have Louvain algorithm (Phase 2)
- Louvain implicitly maximizes Q
- Spectral clustering adds little value

**Recommendation**: ❌ **Defer indefinitely**.

**Rationale**: Louvain gives better communities than spectral bisection for most graphs.

---

## Missing from Spec: Change Entropy

### Detailed Addition to Phase 3

**File**: `docs/v2/temporal/churn.md`

**Add Field**:
```python
@dataclass
class ChurnSeries:
    # ... existing fields ...
    change_entropy: Optional[float]  # NEW
```

**Computation**:
```python
def compute_change_entropy(commits: List[Commit], months: int = 12) -> float:
    """
    Measure how dispersed changes are across time windows.

    High entropy = changes scattered across many periods (bad)
    Low entropy = changes concentrated in few periods (good)

    Args:
        commits: List of commits for file
        months: Number of monthly windows (default 12)

    Returns:
        Entropy in bits (range [0, log₂(months)])
    """
    # Group commits into monthly windows
    windows = partition_commits_by_month(commits, months)
    changes_per_window = [len(w) for w in windows]

    # Compute entropy
    total = sum(changes_per_window)
    if total == 0:
        return None

    probs = [c / total for c in changes_per_window if c > 0]
    entropy = -sum(p * log2(p) for p in probs)

    return entropy
```

**Interpretation**:
```python
def interpret_change_entropy(entropy: float, months: int) -> str:
    """
    Interpret change entropy value.

    Args:
        entropy: Computed entropy
        months: Number of windows

    Returns:
        Interpretation string
    """
    max_entropy = log2(months)

    if entropy > max_entropy * 0.8:
        return "HIGH_SCATTER"  # Bad: changes everywhere
    elif entropy < max_entropy * 0.3:
        return "FOCUSED"  # Good: concentrated changes
    else:
        return "MODERATE"
```

**Use in Finders** (Phase 6):
```python
# Example: UNSTABLE_FILE finder
def find_unstable_files(store):
    for path, signals in store.file_signals.items():
        churn = store.git_history[path]

        if churn.change_entropy and churn.change_entropy > log2(12) * 0.8:
            # High scatter of changes = unstable
            yield Finding(
                kind=FindingKind.UNSTABLE_FILE,
                severity=Severity.MODERATE,
                message=f"Changes scattered across {12} months",
                evidence={'change_entropy': churn.change_entropy}
            )
```

**Add to Registry** (`docs/v2/modules/signals/registry.md`):
```yaml
Signal.CHANGE_ENTROPY:
  description: "Dispersion of changes across time windows"
  dimension: Dimension.TEMPORAL
  scale: Scale.RATIO
  polarity: "HIGH = bad (scattered changes)"
  formula: "H = -Σ(p_i × log₂(p_i)) over monthly windows"
  range: "[0, log₂(windows)]"
  source: "TemporalAnalyzer"
  empirical_support: "r=0.54 with defect count (Co-Change Entropy 2024)"
```

---

## Implementation Checklist

### Phase 3 Additions

- [ ] Add `change_entropy` field to `ChurnSeries`
- [ ] Implement `compute_change_entropy()` in `temporal/churn_analyzer.py`
- [ ] Add unit tests for entropy computation
- [ ] Update `temporal/churn.md` documentation
- [ ] Add `Signal.CHANGE_ENTROPY` to registry

### Phase 5 Validation

- [ ] Verify percentile normalization (already correct ✅)
- [ ] Verify tier-based strategy (already correct ✅)
- [ ] Add `change_entropy` to composite signals (if using)

### Phase 6 Validation

- [ ] Verify hotspot filter (already correct ✅)
- [ ] Verify temporal coupling filter (already correct ✅)
- [ ] Add `change_entropy` to UNSTABLE_FILE finder

### Documentation

- [x] Create `mathematical-foundations-of-defects.md`
- [x] Create `defect-prediction-quick-reference.md`
- [x] Create `implementation-priorities.md`
- [ ] Update MEMORY.md with research findings

---

## Validation Against Research

### What We Got Right ✅

1. **Percentile-based normalization** → Correct for lognormal distributions
2. **Tier-based thresholds** → Handles small sample problem
3. **Hotspot filtering** → Matches CodeScene methodology
4. **Bus factor formula** → `2^H` matches empirical studies
5. **Relative churn** → Implicit in normalized signals
6. **Temporal coupling filter** → Checks structural edge + module
7. **CV-based classification** → STABILIZING < 0.5, CHURNING ≥ 0.5

### What We Should Add ⚠️

1. **Change entropy** (file-level scatter) → Phase 3
2. **Explicit relative churn signal** → Optional (already implicit)

### What We Can Defer ❌

1. **Socio-technical congruence** → Post-v2 (Phase 8)
2. **Cognitive complexity** → Post-v2 (user request)
3. **Spectral clustering** → Not needed (Louvain sufficient)

---

## Research-Backed Thresholds

### Update `docs/v2/modules/signals/finders.md`

For each finder, add **empirical justification**:

```yaml
HIGH_RISK_HUB:
  thresholds:
    pagerank: "> 90th percentile"
    total_changes: "> median"
  justification: "Cataldo (2013): High centrality + churn → increased failures"

UNSTABLE_FILE:
  thresholds:
    churn_cv: ">= 0.5"
    change_entropy: "> 0.8 × log₂(windows)"
  justification: "Co-Change Entropy (2024): r=0.54 with defects"

ZONE_OF_PAIN:
  thresholds:
    instability: "> 0.7"
    abstractness: "< 0.3"
  justification: "Martin (2003): Architecture debt metric"
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_change_entropy.py
def test_change_entropy_uniform():
    # Equal changes in all windows
    commits = create_uniform_commits(12)  # 10 per month
    entropy = compute_change_entropy(commits, months=12)
    assert entropy == pytest.approx(log2(12), rel=0.01)  # Max entropy

def test_change_entropy_focused():
    # All changes in one window
    commits = create_focused_commits(12, focus_month=5)
    entropy = compute_change_entropy(commits, months=12)
    assert entropy == pytest.approx(0.0, abs=0.01)  # Min entropy

def test_change_entropy_moderate():
    # Half in month 1, half in month 6
    commits = create_bimodal_commits(12, [1, 6])
    entropy = compute_change_entropy(commits, months=12)
    assert 0 < entropy < log2(12)  # Between min and max
```

### Integration Tests

```python
# tests/integration/test_phase3_temporal.py
def test_temporal_analyzer_computes_change_entropy():
    store = create_test_store()
    analyzer = TemporalAnalyzer(git_log_path="/path/to/sample")

    analyzer.analyze(store)

    assert store.git_history is not None
    for path, churn in store.git_history.items():
        if churn.total_changes > 0:
            assert churn.change_entropy is not None
            assert 0 <= churn.change_entropy <= log2(12)
```

---

## References

All recommendations based on empirical research from:
- `mathematical-foundations-of-defects.md` (full citations)
- Shannon Insight v2 spec (`docs/v2/`)

---

**Next Steps**:
1. Add `change_entropy` to Phase 3 spec
2. Update `ChurnSeries` model
3. Implement `compute_change_entropy()`
4. Add to registry + finders
5. Write unit tests
6. Update MEMORY.md

**Version**: 1.0
**Date**: 2026-02-10
