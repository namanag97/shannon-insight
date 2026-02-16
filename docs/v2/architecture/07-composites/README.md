# Composite Scores

Composite scores fuse multiple signals into single summary numbers. There are **7 composites**.

---

## Display Scale

All composites are computed as [0, 1] internally but displayed on a **1-10 scale**.

```python
def to_display_scale(value: float) -> float:
    """
    Convert internal [0,1] to user-facing [1,10] scale.

    Rules:
    1. Multiply by 10
    2. Round to 1 decimal place (HALF_UP)
    3. Clamp to [1.0, 10.0] (floor at 1.0, not 0.0)
    """
    if value > 1.0:
        log.warning(f"Composite {value} exceeds 1.0, clamping")
        value = 1.0
    if value < 0.0:
        value = 0.0

    display = round(value * 10, 1)
    return max(1.0, display)  # Floor at 1.0
```

---

## Division Guards

All formulas use guarded division:

```python
def safe_div(num: float, denom: float, default: float = 0.0) -> float:
    return num / denom if denom != 0 else default
```

| Composite | Potential Zero | Guard |
|-----------|---------------|-------|
| risk_score | max_bus_factor | Always >= 1.0 |
| wiring_quality | import_count, total_calls | Use `max(x, 1)` |
| raw_risk | max_pagerank, max_blast, max_cognitive | If 0, term = 0.0 |
| health_score | (no division) | N/A |
| wiring_score | (no division) | N/A |
| architecture_health | total_cross_module_edges | If 0, violation_rate = 0.0 |
| codebase_health | team_size | If 0, use 1 |

---

## Per-File Composites

### #35 risk_score

How dangerous is this file?

```
risk_score(f) = 0.25 × pctl(pagerank, f)
              + 0.20 × pctl(blast_radius_size, f)
              + 0.20 × pctl(cognitive_load, f)
              + 0.20 × instability_factor(f)
              + 0.15 × (1 - bus_factor(f) / max_bus_factor)

where instability_factor = 1.0 if churn_trajectory ∈ {CHURNING, SPIKING}
                           0.3 otherwise
```

| Input | Weight | Polarity |
|-------|--------|----------|
| pctl(pagerank) | 0.25 | HIGH_IS_BAD |
| pctl(blast_radius_size) | 0.20 | HIGH_IS_BAD |
| pctl(cognitive_load) | 0.20 | HIGH_IS_BAD |
| instability_factor | 0.20 | — |
| 1 - bus_factor/max | 0.15 | HIGH_IS_GOOD → inverted |
| **Total** | **1.00** | |

**Polarity**: HIGH_IS_BAD

---

### #36 wiring_quality

How well-connected and implemented is this file?

```
wiring_quality(f) = 1 - (
    0.30 × is_orphan(f)
  + 0.25 × stub_ratio(f)
  + 0.25 × (phantom_import_count(f) / max(import_count(f), 1))
  + 0.20 × (broken_call_count(f) / max(total_calls(f), 1))
)
```

| Input | Weight | Notes |
|-------|--------|-------|
| is_orphan | 0.30 | Boolean (0 or 1) |
| stub_ratio | 0.25 | Already [0, 1] |
| phantom_import_ratio | 0.25 | Normalized by import_count |
| broken_call_ratio | 0.20 | = 0 until CALL edges exist |
| **Total** | **1.00** | |

**Polarity**: HIGH_IS_GOOD (note: formula is `1 - (bad things)`)

---

## Per-Module Composite

### #51 health_score

Overall module health.

```
health_score(m) = 0.20 × cohesion(m)
               + 0.15 × (1 - coupling(m))
               + 0.20 × (1 - main_seq_distance(m))
               + 0.15 × boundary_alignment(m)
               + 0.15 × role_consistency(m)
               + 0.15 × (1 - mean(stub_ratio across files in m))
```

| Input | Weight | Notes |
|-------|--------|-------|
| cohesion | 0.20 | HIGH_IS_GOOD |
| 1 - coupling | 0.15 | Invert HIGH_IS_BAD |
| 1 - main_seq_distance | 0.20 | Invert HIGH_IS_BAD |
| boundary_alignment | 0.15 | HIGH_IS_GOOD |
| role_consistency | 0.15 | HIGH_IS_GOOD |
| 1 - mean(stub_ratio) | 0.15 | Invert HIGH_IS_BAD |
| **Total** | **1.00** | |

**instability = None guard**:

```python
if instability is None:
    # Redistribute 0.20 weight proportionally
    scale = 1.0 / 0.80  # = 1.25
    return (0.20 * scale * cohesion +
            0.15 * scale * (1 - coupling) +
            0.15 * scale * boundary_alignment +
            0.15 * scale * role_consistency +
            0.15 * scale * (1 - mean_stub_ratio))
```

**Polarity**: HIGH_IS_GOOD

---

## Global Composites

### #60 wiring_score

Codebase-level AI code quality.

```
wiring_score = 1 - (
    0.25 × orphan_ratio
  + 0.25 × phantom_ratio
  + 0.20 × glue_deficit
  + 0.15 × mean(stub_ratio across all files)
  + 0.15 × clone_ratio
)

where clone_ratio = |files in NCD clone pairs| / |total files|
```

| Input | Weight | Notes |
|-------|--------|-------|
| orphan_ratio | 0.25 | Already [0, 1] |
| phantom_ratio | 0.25 | Already [0, 1] |
| glue_deficit | 0.20 | Already [0, 1] |
| mean(stub_ratio) | 0.15 | Already [0, 1] |
| clone_ratio | 0.15 | Computed |
| **Total** | **1.00** | |

**Polarity**: HIGH_IS_GOOD

**Alias**: `ai_quality` (deprecated, use `wiring_score` in code)

---

### #61 architecture_health

How well the system is structured.

```
architecture_health = 0.25 × (1 - violation_rate)
                    + 0.20 × mean(cohesion across modules)
                    + 0.20 × (1 - mean(coupling across modules))
                    + 0.20 × (1 - mean(main_seq_distance across modules))
                    + 0.15 × mean(boundary_alignment across modules)

where violation_rate = violating_cross_module_edges / total_cross_module_edges
```

| Input | Weight | Notes |
|-------|--------|-------|
| 1 - violation_rate | 0.25 | Invert |
| mean(cohesion) | 0.20 | HIGH_IS_GOOD |
| 1 - mean(coupling) | 0.20 | Invert |
| 1 - mean(main_seq_distance) | 0.20 | Invert, skip None |
| mean(boundary_alignment) | 0.15 | HIGH_IS_GOOD |
| **Total** | **1.00** | |

**Polarity**: HIGH_IS_GOOD

---

### #62 codebase_health

The one number.

```
codebase_health = 0.30 × architecture_health
               + 0.30 × wiring_score
               + 0.20 × (global_bus_factor / team_size)
               + 0.20 × modularity

where:
  global_bus_factor = min_bus_factor_critical (capped at team_size)
  min_bus_factor_critical = min(bus_factor) across files with pctl(pagerank) > 0.75
  team_size = |distinct authors in recent window|
```

| Input | Weight | Notes |
|-------|--------|-------|
| architecture_health | 0.30 | Already composite |
| wiring_score | 0.30 | Already composite |
| global_bus_factor / team_size | 0.20 | Normalized |
| modularity | 0.20 | Already [0, 1] |
| **Total** | **1.00** | |

**Polarity**: HIGH_IS_GOOD

**Note**: Finding density is NOT included (circular dependency with finders). It can be displayed alongside but not in formula.

---

## Intermediate Terms

These are computed inline during composite evaluation, not standalone signals:

| Term | Formula | Used In |
|------|---------|---------|
| clone_ratio | `\|files in NCD clone pairs\| / \|total files\|` | wiring_score |
| violation_rate | `violating_edges / total_cross_module_edges` | architecture_health |
| raw_risk | Pre-percentile weighted sum | Health Laplacian |
| conway_alignment | `1 - mean(author_distance)` | team_risk |

---

## Tier Behavior

| Composite | ABSOLUTE (<15) | BAYESIAN (15-50) | FULL (50+) |
|-----------|---------------|-----------------|------------|
| risk_score | Not computed | Computed | Computed |
| wiring_quality | Not computed | Computed | Computed |
| health_score | Not computed | Computed | Computed |
| wiring_score | Not computed | Computed | Computed |
| architecture_health | Not computed | Computed | Computed |
| codebase_health | Not computed | Computed | Computed |

**ABSOLUTE tier**: Show raw signal values instead. Users see individual metrics rather than fused scores.

---

## Weight Calibration

Current weights are hand-tuned. Future calibration plan:

1. Run on Technical Debt Dataset (33 Apache projects)
2. Extract per-file signal vectors
3. Label files: y = 1 if file has known bug in Jira
4. Fit logistic regression: `P(bug | x) = σ(w · x)`
5. Replace hand-tuned weights with learned weights
6. Acceptance: AUC > 0.70, per-finder precision > 0.50

**Literature insight**: Process metrics (churn, authors, age) outperform code metrics for defect prediction. Temporal signals may deserve higher weights.
