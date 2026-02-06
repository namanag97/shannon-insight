# Churn Analysis

Per-file churn time series construction and trajectory classification. This is the D6 (CHANGE) dimension of temporal analysis.

## Time Window Partitioning

Commit timestamps are partitioned into fixed-width windows:

```
window_secs = window_weeks * 7 * 86400    # default: 4 weeks = 2,419,200 seconds
num_windows = max(1, (max_ts - min_ts) // window_secs + 1)
window_idx(commit) = min((commit.timestamp - min_ts) // window_secs, num_windows - 1)
```

For each file, a `window_counts: list[int]` array of length `num_windows` is populated, where `window_counts[i]` is the number of commits touching that file in window `i`.

**Status**: EXISTS. No change in v2.

### Edge cases

- Single commit: `num_windows = 1`, slope is 0, trajectory is DORMANT (total_changes = 1)
- All commits in same window: `num_windows = 1` because `max_ts - min_ts < window_secs`
- File not in `analyzed_files`: skipped entirely

### Window size rationale

4 weeks balances granularity vs noise. Shorter windows (1 week) create spiky data for infrequently-changed files. Longer windows (8+ weeks) smooth out real spikes. The 4-week default is not configurable in the current API but could be parameterized if needed.

## Linear Regression for Slope

The slope of changes over time is computed via ordinary least squares on the `window_counts` series:

```python
def _linear_slope(values: list[int]) -> float:
    n = len(values)
    if n < 2:
        return 0.0

    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n

    numerator   = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return 0.0
    return numerator / denominator
```

This is the closed-form OLS solution: `b = Cov(x, y) / Var(x)` where `x = [0, 1, ..., n-1]`.

For the formula definition, see `registry/signals.md #29` (`churn_slope`).

**Status**: EXISTS. No change in v2.

### Interpretation

- `slope > 0`: churn is increasing over time (accelerating)
- `slope < 0`: churn is decreasing over time (decelerating / stabilizing)
- `slope ~ 0`: churn is steady or flat

Slope is in units of "changes per window per window" (i.e., the rate of change of the change rate). A slope of 0.5 means each successive 4-week window has on average 0.5 more changes than the previous one.

## Coefficient of Variation

CV measures how erratic the churn pattern is, independent of the overall level:

```
mean = sum(window_counts) / len(window_counts)
variance = sum((c - mean)^2 for c in window_counts) / len(window_counts)
cv = sqrt(variance) / mean
```

For the formula definition, see `registry/signals.md #30` (`churn_cv`).

**Status**: The computation EXISTS in `_classify_trajectory()` but the CV value is not stored as a field on `ChurnSeries`. v2 surfaces it as `FileHistory.churn_cv` and as signal #30.

### Interpretation

- `CV < 0.5`: relatively steady change rate
- `0.5 <= CV <= 1.0`: moderate variability
- `CV > 1.0`: highly erratic (changes come in bursts)

## Trajectory Classification

The canonical classification rules are defined in `registry/temporal-operators.md` (Trajectory operator). This module implements them for churn:

```
if total_changes <= 1:                                  DORMANT
elif slope < -threshold AND CV < 1:                     STABILIZING
elif slope > threshold AND CV > 0.5:                    SPIKING
elif CV > 0.5:                                          CHURNING
else:                                                   STABLE
```

For the full specification, see `registry/temporal-operators.md`.

### Current implementation vs v2

The current code in `churn.py` has two differences from the canonical rules:

| Aspect | Current code | v2 canonical |
|--------|-------------|-------------|
| STABLE case | Falls through to `return "stabilizing"` | Explicit STABLE branch |
| CV thresholds | SPIKING uses `cv > 1.0`, CHURNING uses `cv > 0.8` | SPIKING uses `cv > 0.5`, CHURNING uses `cv > 0.5` |
| Slope threshold | Hardcoded `-0.1` / `0.1` | Parameterized `threshold` (default 0.1) |

v2 fixes both:
1. The STABLE trajectory is added as the `else` branch -- files that are not dormant, not clearly trending, and not erratic are stable.
2. CV thresholds are aligned with the registry specification.

### Decision tree (v2)

```
total_changes <= 1?
  YES -> DORMANT
  NO  -> slope < -0.1 AND CV < 1.0?
           YES -> STABILIZING
           NO  -> slope > 0.1 AND CV > 0.5?
                    YES -> SPIKING
                    NO  -> CV > 0.5?
                             YES -> CHURNING
                             NO  -> STABLE
```

### Examples

| File | Windows | Slope | CV | Trajectory |
|------|---------|-------|----|-----------|
| config.py | [0, 0, 1, 0, 0] | ~0 | high | DORMANT (total=1) |
| utils.py | [5, 4, 3, 2, 1] | -1.0 | 0.47 | STABILIZING |
| auth.py | [1, 1, 2, 8, 12] | +2.8 | 0.97 | SPIKING |
| db.py | [0, 5, 0, 6, 0, 7] | +0.3 | 1.1 | SPIKING |
| models.py | [3, 2, 4, 3, 2] | ~0 | 0.28 | STABLE |
| handler.py | [0, 4, 0, 5, 1, 0, 6] | ~0 | 1.0 | CHURNING |

## Integration with FileHistory

In v2, churn analysis populates the churn fields of `FileHistory`:

```python
file_history.churn_series     = window_counts
file_history.churn_slope      = slope
file_history.churn_cv         = cv
file_history.churn_trajectory = trajectory
file_history.total_changes    = sum(window_counts)
```

The standalone `build_churn_series()` function and `ChurnSeries` model remain available for backward compatibility.
