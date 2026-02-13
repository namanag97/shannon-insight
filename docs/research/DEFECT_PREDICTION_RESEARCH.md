# Defect Prediction Research (Feb 2026)

**Research Question**: What mathematical properties ACTUALLY indicate bugs or problems in codebases?

**Goal**: Move beyond heuristics to empirically validated mathematical foundations for Shannon Insight v2.

---

## Document Overview

### 1. [Mathematical Foundations of Defects](./mathematical-foundations-of-defects.md) (25KB)

**Comprehensive research synthesis** covering:
- Information theory perspective (entropy, compression, Kolmogorov complexity)
- Graph theory perspective (centrality, cycles, spectral analysis, modularity)
- Statistical perspective (distributions, outlier detection, thresholds)
- Temporal perspective (churn, co-change, bus factor)
- Cross-dimensional signals (socio-technical congruence, structural-temporal disagreement)

**Key Findings**:
- **Power Law**: 80% of defects in 20% of files (universal)
- **Relative Churn**: 89% accuracy predicting defects (Nagappan & Ball 2005)
- **Change Entropy**: r=0.54 correlation with defect counts
- **Lognormal Distribution**: Software metrics DON'T follow normal distributions
- **Socio-Technical Congruence**: Gaps between team structure and code structure predict failures

**Audience**: Deep dive, full citations, mathematical proofs.

---

### 2. [Quick Reference Guide](./defect-prediction-quick-reference.md) (12KB)

**Practical implementation guide** with:
- Statistical reality check (which distributions to use)
- Proven defect predictors (Tier 1 vs Tier 2)
- Threshold decision trees (complexity, churn, ownership, centrality)
- Outlier detection methods (IQR recommended, z-score discouraged)
- Composite scoring formulas (hotspot, risk score)
- Cross-dimensional detection (mismatch, hidden coupling, congruence)
- Formula cheat sheet (entropy, bus factor, Gini, CV, modularity, IQR)
- Common pitfalls (what NOT to do)

**Audience**: Developers implementing finders, quick lookup.

---

### 3. [Implementation Priorities](./implementation-priorities.md) (15KB)

**Actionable roadmap** for Shannon Insight v2:
- Priority matrix (P0/P1/P2 features)
- Validation of existing spec (what we got right ✅)
- Missing features (change entropy ⚠️)
- Future enhancements (socio-technical congruence, cognitive complexity)
- Detailed addition spec for change entropy
- Testing strategy (unit + integration tests)
- Research-backed thresholds for finders

**Audience**: Shannon Insight development team, sprint planning.

---

## Executive Summary

### What We Learned

#### 1. Distribution Reality

Software metrics DO NOT follow normal distributions:
- **Defect concentration**: Power law (Pareto 80/20)
- **Complexity, churn, file size**: Lognormal
- **Fault distribution**: Double Pareto (context-dependent)

**Implication**: z-score and mean-based approaches FAIL. Use percentiles and IQR.

#### 2. Proven Predictors

| Metric | Correlation | Threshold | Source |
|--------|-------------|-----------|--------|
| Relative churn | 89% accuracy | > 75th percentile | Nagappan & Ball 2005 |
| Change entropy | r = 0.54 | High scatter | Co-Change 2024 |
| Cyclomatic complexity | Positive | > 10 | McCabe 1976 |
| Bus factor | Post-release failures | < 3 | Git Bus Factor |
| Socio-tech congruence | Increased failures | Low overlap | Cataldo 2013 |

#### 3. Complexity Thresholds (Validated)

```
Cyclomatic Complexity:
  1-10  → Low risk (no action)
  11-15 → Moderate (review)
  16-30 → High (refactor recommended)
  31+   → Critical (must refactor)
```

McCabe's original threshold of 10 has strongest empirical support.

#### 4. Entropy Interpretations

**Change Entropy** (process metric):
- **HIGH**: Changes scattered across files → BAD (lack of focus, hidden coupling)
- **LOW**: Changes concentrated → GOOD (modular, focused)

**Code Entropy** (structural):
- **HIGH**: Complex/unique logic OR chaos (context-dependent)
- **LOW**: Repetitive/simple (could be clones)

**Alone, entropy is neutral**. Context (churn, test coverage, ownership) determines risk.

#### 5. Temporal Coupling

**NOT all co-change is bad**:
- Interface + implementation → EXPECTED
- Test + code → GOOD PRACTICE
- Files in same feature → NORMAL

**Flag as hidden coupling only when**:
- Support > 0.3 (frequent co-change)
- No structural dependency
- Different architectural modules
- High graph distance (> 3 hops)

#### 6. Composite Scoring

**Multiplicative, not additive**:
```python
hotspot_score = change_frequency × (1 - code_health)
```

**Rationale**: Zero frequency → score = 0 (doesn't matter how bad the code is if never touched).

---

## Validation of Shannon Insight v2 Spec

### What We Got Right ✅

1. **Percentile-based normalization** (Phase 5) → Correct for lognormal distributions
2. **Tier-based thresholds** (Phase 6) → Handles small sample problem
3. **Hotspot filtering** (Phase 6) → `change_freq > median` matches CodeScene
4. **Bus factor formula** (Phase 3) → `2^H` matches empirical studies
5. **Temporal coupling filter** (Phase 6) → Checks structural edge + module boundary
6. **CV-based classification** (Phase 3) → STABILIZING < 0.5, CHURNING ≥ 0.5

### What We Should Add ⚠️

1. **Change entropy** (file-level scatter of changes) → Add to Phase 3
   - Empirical support: r=0.54 with defect counts
   - Easy to compute: existing git history
   - High value: detects unstable files

### What We Can Defer ❌

1. **Socio-technical congruence** → Post-v2 (requires team metadata)
2. **Cognitive complexity** → Post-v2 (marginal over cyclomatic)
3. **Spectral clustering** → Not needed (Louvain sufficient)

---

## Key Implementation Changes

### Immediate (Phase 3 Addition)

**Add to `temporal/churn.md`**:
```python
@dataclass
class ChurnSeries:
    # ... existing fields ...
    change_entropy: Optional[float]  # NEW: H = -Σ(p×log₂(p))
```

**Computation**:
```python
def compute_change_entropy(commits, months=12):
    windows = partition_commits_by_month(commits, months)
    changes_per_window = [len(w) for w in windows]
    total = sum(changes_per_window)
    probs = [c/total for c in changes_per_window if c > 0]
    return -sum(p * log2(p) for p in probs)
```

**Use in Finder** (Phase 6):
```python
if churn.change_entropy > log2(12) * 0.8:
    yield Finding(
        kind=FindingKind.UNSTABLE_FILE,
        severity=Severity.MODERATE,
        message="Changes scattered across 12 months"
    )
```

---

## Common Pitfalls (Avoid These)

### ❌ Don't Do This

1. **Assume normal distribution**:
   ```python
   outliers = [v for v in values if v > mean + 2*std]  # WRONG
   ```

2. **Simple weighted sum**:
   ```python
   risk = 0.25*complexity + 0.25*churn + 0.25*coupling + 0.25*centrality  # WRONG
   ```

3. **Flag all temporal coupling**:
   ```python
   if cochange_support(A, B) > 0.3:
       flag_as_problem(A, B)  # WRONG (might be expected)
   ```

4. **Use z-score on skewed data**:
   ```python
   z_score = (value - mean) / std  # WRONG for lognormal/power law
   ```

### ✅ Do This Instead

1. **Use percentiles and IQR**:
   ```python
   Q1, Q3 = percentile(values, [25, 75])
   IQR = Q3 - Q1
   outliers = [v for v in values if v > Q3 + 1.5*IQR]  # CORRECT
   ```

2. **Multiplicative scoring with filtering**:
   ```python
   if churn > median:
       risk = change_frequency * (1 - code_health)  # CORRECT
   else:
       risk = 0  # Not a hotspot
   ```

3. **Check structural coupling**:
   ```python
   if cochange_support(A, B) > 0.3 and not has_structural_edge(A, B):
       flag_as_hidden_coupling(A, B)  # CORRECT
   ```

4. **Use percentile ranking**:
   ```python
   percentile_rank = sum(v <= value for v in values) / len(values)  # CORRECT
   ```

---

## Research Sources

### Core Papers

1. **[Nagappan & Ball (2005)](https://www.microsoft.com/en-us/research/publication/use-of-relative-code-churn-measures-to-predict-system-defect-density/)**: Relative code churn (89% accuracy)
2. **[Co-Change Graph Entropy (2024)](https://arxiv.org/html/2504.18511v1)**: Process metrics (r=0.54)
3. **[Cataldo (2013)](https://herbsleb.org/web-pubs/pdfs/Cataldo-Coordination-2013.pdf)**: Coordination breakdowns and failures
4. **[Pareto Distribution of Defects](https://www.researchgate.net/publication/221232158_The_Vital_Few_and_Trivial_Many_An_Empirical_Analysis_of_the_Pareto_Distribution_of_Defects)**: Power law validation
5. **[Power Laws in Software](https://www.spinellis.gr/pubs/jrnl/2008-TOSEM-PowerLaws/html/LSV08.html)**: Distribution models
6. **[Lognormal Distribution](https://link.springer.com/chapter/10.1007/978-1-84800-131-2_73)**: Software reliability
7. **[Evolutionary Coupling and Defects](https://dl.acm.org/doi/10.1002/smr.1842)**: Temporal coupling correlation

### Industry Tools

1. **[CodeScene](https://docs.enterprise.codescene.io/)**: Behavioral code analysis, hotspot methodology
2. **[SonarQube](https://docs.sonarsource.com/sonarqube-server/2025.1/)**: Technical debt, cognitive complexity
3. **McCabe Cyclomatic Complexity**: Thresholds (1976)

### Foundational Theory

1. **[Kolmogorov Complexity](https://en.wikipedia.org/wiki/Kolmogorov_complexity)**: Information theory
2. **[Modularity and Community Structure](https://www.pnas.org/doi/10.1073/pnas.0601602103)**: Graph theory
3. **[Conway's Law](https://en.wikipedia.org/wiki/Conway's_law)**: Socio-technical alignment

**Full bibliography**: See `mathematical-foundations-of-defects.md` (50+ references).

---

## Next Steps

### For Development Team

1. **Read**: Start with `defect-prediction-quick-reference.md` (12KB, practical)
2. **Implement**: Add change entropy to Phase 3 (see `implementation-priorities.md`)
3. **Test**: Unit tests for entropy computation, integration tests for Phase 3
4. **Validate**: Run on real codebases, compare with known defect data

### For Research

1. **Validate empirically**: Collect Shannon Insight findings + actual bug data
2. **Publish**: "Shannon Insight: Multi-Dimensional Defect Prediction" paper
3. **Extend**: Socio-technical congruence (Phase 8), cognitive complexity (optional)

### For Users

1. **Trust percentiles**: Top 10% centrality = hubs (no universal threshold)
2. **Focus hotspots**: High frequency + bad health = prioritize
3. **Context matters**: High entropy alone ≠ bad, combine with churn/ownership
4. **Bus factor < 3**: Knowledge transfer risk (empirically validated)

---

## FAQ

### Q: Why not use z-score for outlier detection?

**A**: Software metrics follow lognormal/power law distributions, NOT normal. Z-score assumes normality and fails on skewed data. Use IQR (percentile-based, robust).

### Q: What's a "good" cyclomatic complexity?

**A**: ≤ 10 (McCabe original, strongest empirical support). 11-15 acceptable with experienced team and comprehensive tests. > 30 = critical.

### Q: Is ALL temporal coupling bad?

**A**: No. Interface+implementation, test+code, same-feature files co-change normally. Flag only when: support > 0.3 AND no structural edge AND different modules.

### Q: How do I combine multiple metrics?

**A**: Multiplicatively with filtering, not simple weighted sums. Example: `hotspot = frequency × (1 - health)`. Zero frequency → zero score (inactive code doesn't matter).

### Q: What's the difference between change entropy and code entropy?

**A**: **Change entropy** (process): Scatter of changes over time (HIGH = bad). **Code entropy** (structural): Information content (context-dependent, neutral alone).

### Q: Why percentiles for small codebases?

**A**: Percentiles unreliable for < 15 files. Use absolute thresholds (CC > 15, etc.) instead. Shannon v2 has tier-based strategy (ABSOLUTE/BAYESIAN/FULL).

---

## Document Metadata

- **Date**: 2026-02-10
- **Version**: 1.0
- **Research Duration**: 4 hours
- **Papers Reviewed**: 50+
- **Total Content**: 52KB across 3 documents
- **Primary Researcher**: Claude Opus 4.5 (Shannon Insight context)
- **Target**: Shannon Insight v2 implementation

---

**Start Here**: Read `defect-prediction-quick-reference.md` for practical thresholds and formulas.

**Deep Dive**: Read `mathematical-foundations-of-defects.md` for full citations and theory.

**Implementation**: Follow `implementation-priorities.md` for Phase 3 addition (change entropy).
