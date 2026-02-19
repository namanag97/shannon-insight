# Level 1: Temporal Signals

## Overview

Level 1 computes temporal signals from git history:
1. **Per-file signals** - churn, authorship, trajectory
2. **Per-pair signals** - co-change frequency, author overlap

## Per-File Signals

| Signal | Type | Formula | Meaning |
|--------|------|---------|---------|
| `churn_mean` | float | mean(changes per window) | Average activity |
| `churn_std` | float | std(changes per window) | Variability |
| `churn_cv` | float | σ/μ | Volatility |
| `churn_trend` | float | linear regression slope | Direction |
| `trajectory` | str | classification | DORMANT/STABILIZING/STABLE/CHURNING/SPIKING |
| `author_entropy` | float | -Σp log₂ p | Knowledge distribution |
| `bus_factor` | float | 2^H | Equivalent authors |
| `fix_ratio` | float | fix_commits / total | Bug-prone indicator |
| `total_changes` | int | commit count | Activity level |

## Per-Pair Signals

| Signal | Type | Formula | Meaning |
|--------|------|---------|---------|
| `lift` | float | P(a,b) / (P(a) × P(b)) | Co-change strength |
| `confidence_a_b` | float | P(B\|A changed) | Conditional probability |
| `author_jaccard` | float | \|A∩B\| / \|A∪B\| | Team overlap |

## Key Formulas

### Shannon Entropy
```
H = -Σ p(a) log₂ p(a)
where p(a) = commits_by_author / total_commits

bus_factor = 2^H
```

### Lift (Co-change)
```
lift(a,b) = P(a,b) / (P(a) × P(b))
          = (commits_both × total) / (commits_a × commits_b)

lift > 1 → stronger than random
lift = 1 → independent
lift < 1 → anti-correlated
```

### Trajectory Classification
```
if total_changes ≤ 1: DORMANT
elif slope < -0.1 and cv < 0.5: STABILIZING
elif slope > 0.1 and cv > 0.5: SPIKING
elif cv > 0.5: CHURNING
else: STABLE
```

## Data Models

```python
@dataclass
class ChurnSeries:
    file_path: str
    window_counts: list[int]
    total_changes: int
    trajectory: str
    slope: float
    cv: float
    bus_factor: float
    author_entropy: float
    fix_ratio: float
    refactor_ratio: float

@dataclass
class CoChangeMatrix:
    pairs: dict[tuple[str, str], CoChangePair]
    total_commits: int
    file_change_counts: dict[str, int]
```

## Current Implementation

**Files:**
- `src/shannon_insight/temporal/churn.py` - ChurnSeries builder
- `src/shannon_insight/temporal/cochange.py` - CoChangeMatrix builder
- `src/shannon_insight/temporal/git_raw_extractor.py` - Git extraction

## Dependencies

- **Requires:** Level 0 facts (commits, file changes)
- **Produces:** Signals for Level 2 (graph construction)
