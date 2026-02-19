# Level 1: Temporal Signals

## Overview

Computes time-based signals from git history. Measures how files *evolve* — change patterns, authorship, maintenance intent, and co-change coupling.

**Depends on:** Level 0 (CommitFact, FileChangeFact)
**Produces:** ChurnSeries per file, CoChangeMatrix (pairwise)

---

## Per-File Signals (8 signals)

### 1. total_changes
```
total_changes(file) = |{commits touching file}|
```
Polarity: High is bad (indicates risk, complexity)

### 2. churn_trajectory
```
DORMANT | STABILIZING | STABLE | CHURNING | SPIKING

Classification:
- DORMANT: total_changes ≤ 1 OR cv = 0
- STABILIZING: early burst + recent silence, OR slope < -0.1 AND cv < 0.5
- SPIKING: slope > 0.1 AND cv > 0.5
- CHURNING: cv > 0.5 (erratic, no trend)
- STABLE: cv ≤ 0.5, |slope| < 0.1
```

### 3. churn_slope
```
Linear regression slope of changes per window.
slope = Σ(tᵢ - t̄)(countᵢ - c̄) / Σ(tᵢ - t̄)²
```
Positive = accelerating, Negative = stabilizing

### 4. churn_cv
```
Coefficient of variation (volatility):
cv = σ(window_counts) / μ(window_counts)

With Bessel's correction: σ² = Σ(x-μ)² / (n-1)
```
- cv < 0.5: steady
- cv ≥ 1.0: highly erratic

### 5. author_entropy
```
H = -Σ p(author) × log₂(p(author))

where p(author) = commits_by_author / total_commits
```
- H = 0: single author
- H = log₂(k): k equal authors

### 6. bus_factor
```
bus_factor = 2^author_entropy
```
- 1 = single author (high risk)
- k = k equal authors (distributed)

### 7. fix_ratio
```
fix_ratio = (commits with fix keywords) / total_commits

Keywords: fix, bug, patch, hotfix, bugfix, repair, issue
```

### 8. refactor_ratio
```
refactor_ratio = (commits with refactor keywords) / total_commits

Keywords: refactor, cleanup, reorganize, restructure, rename
```

---

## Time Windows

```
window_width = window_weeks × 7 × 86400 seconds  (default: 4 weeks)
num_windows = (max_ts - min_ts) / window_width + 1
window_index(commit) = (commit.timestamp - min_ts) / window_width
```

---

## Pairwise Signals: Co-Change

### CoChangePair
```python
@dataclass
class CoChangePair:
    file_a: str
    file_b: str
    cochange_count: int          # commits touching both
    confidence_a_b: float        # P(B|A) = count_ab / total_a
    confidence_b_a: float        # P(A|B) = count_ab / total_b
    lift: float                   # observed / expected
```

### Lift Formula
```
lift(a,b) = (count_ab × total_weight) / (total_a × total_b)

lift = 1.0: independent
lift > 2.0: significant coupling
lift > 5.0: strong coupling
```

### Temporal Decay
```
weight = exp(-λ × days_since)
λ = ln(2) / 90  (90-day half-life)

0 days:   weight = 1.0
90 days:  weight = 0.5
180 days: weight = 0.25
```

---

## Data Models

```python
@dataclass
class ChurnSeries:
    file_path: str
    window_counts: list[int]
    total_changes: int
    trajectory: str              # enum value
    slope: float
    cv: float
    bus_factor: float
    author_entropy: float
    fix_ratio: float
    refactor_ratio: float

@dataclass
class CoChangeMatrix:
    pairs: dict[tuple[str,str], CoChangePair]  # sparse
    total_commits: int
    file_change_counts: dict[str, int]
```

---

## Algorithm: build_churn_series

```
1. Extract time bounds (min_ts, max_ts)
2. Initialize per-file accumulators:
   - window_counts[file][window_idx]
   - author_counts[file][author]
   - fix_count[file], refactor_count[file]

3. For each commit:
   - window_idx = (timestamp - min_ts) / window_width
   - For each file in commit:
     - Increment window_counts, author_counts
     - Check fix/refactor keywords

4. For each file:
   - Compute slope, cv, trajectory
   - Compute author_entropy, bus_factor
   - Compute fix_ratio, refactor_ratio
```

## Algorithm: build_cochange_matrix

```
1. For each commit:
   - Skip if > 30 files (bulk reformat)
   - weight = exp(-λ × days_since)
   - For each file: file_counts[file] += weight
   - For each pair: pair_counts[(a,b)] += weight

2. For pairs with raw_count >= 3:
   - confidence_a_b = weighted_count / total_a
   - lift = (count_ab × total_weight) / (total_a × total_b)
```

---

## Graceful Degradation

**No git history:**
- total_changes = 0
- trajectory = DORMANT
- bus_factor = 1.0
- All ratios = 0.0

**Single commit:**
- trajectory = DORMANT
- cv = 0.0

---

## Store Integration

```python
class AnalysisStore:
    git_history: GitHistory
    cochange: CoChangeMatrix
    churn: dict[str, ChurnSeries]
```

Populated by `TemporalAnalyzer` in Wave 1.

---

## Mathematical Summary

| Formula | Purpose |
|---------|---------|
| `cv = σ/μ` | Volatility |
| `H = -Σp log₂p` | Author entropy |
| `bf = 2^H` | Bus factor |
| `lift = obs/exp` | Co-change strength |
| `w = e^(-λt)` | Temporal decay |
