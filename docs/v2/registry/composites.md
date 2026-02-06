# Registry: Composite Scores

Composite scores fuse multiple signals (from `signals.md`) into single summary numbers. Each is defined here with its exact formula and weights.

**Calibration note**: Initial weights are hand-tuned. They will be replaced by logistic regression weights trained on the Technical Debt Dataset (33 Apache projects, 95K labeled issues) once validation infrastructure (see `validation/strategy.md`) is in place. Until then, use rank ordering ("this file is the #1 riskiest") rather than absolute score interpretation.

**Display scale**: All composites are computed as [0,1] internally but displayed on a **1-10 scale** (multiply by 10). Users see 6.4/10, not 0.64. This matches CodeScene's Code Health scale and is more intuitive.

### Display Scale Contract

```python
def to_display_scale(value: float) -> float:
    """
    Convert internal [0,1] composite to user-facing [1,10] scale.

    Rules:
    1. Multiply by 10
    2. Round to 1 decimal place using HALF_UP rounding
    3. Clamp to [1.0, 10.0] (floor at 1.0, not 0.0)
    4. If input > 1.0, log warning and clamp

    JSON output: both internal and display values provided:
      "risk_score": 0.64,
      "risk_score_display": 6.4
    """
    if value > 1.0:
        log.warning(f"Composite value {value} exceeds 1.0, clamping")
        value = 1.0
    if value < 0.0:
        log.warning(f"Composite value {value} below 0.0, clamping")
        value = 0.0

    display = round(value * 10, 1)
    return max(1.0, display)  # Floor at 1.0 for display

# Centralized in signals/display.py — all consumers call this function
```

### Division-by-Zero Guards

All composite formulas use guarded division:

```python
def safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Division with zero guard. Returns default if denominator is 0."""
    return numerator / denominator if denominator != 0 else default

# Examples in composites:
# wiring_quality: phantom_import_count / max(import_count, 1)  ← max() guard
# risk_score: bus_factor / max_bus_factor  ← requires max_bf > 0 (always true: bf >= 1)
# raw_risk: pagerank / max_pagerank  ← if max_pr = 0, term = 0.0
```

| Composite | Potential zero | Guard |
|-----------|---------------|-------|
| risk_score | max_bus_factor | Always >= 1.0 (minimum is 1 author) |
| wiring_quality | import_count, total_calls | Use `max(x, 1)` |
| raw_risk | max_pagerank, max_blast, max_cognitive | If 0, term contributes 0.0 |
| health_score | (no division) | N/A |
| wiring_score | (no division) | N/A |
| architecture_health | total_cross_module_edges | If 0, violation_rate = 0.0 |
| team_risk | team_size (for bf cap) | If 0, skip team_risk entirely |
| codebase_health | team_size | If 0, use bf_cap = 1 |

**Intermediate terms**: Some composite formulas use computed intermediates that are NOT numbered signals in `signals.md`:
- `clone_ratio` = `|files in NCD clone pairs| / |total files|` (from graph/ clone detection)
- `violation_rate` = `violating_cross_module_edges / total_cross_module_edges` (from architecture/)
- `raw_risk` = pre-percentile weighted sum (see Health Laplacian below)
- `conway_alignment` = `1 - mean(author_distance)` across structurally-coupled module pairs

These are computed inline during composite evaluation, not standalone signals.

---

## Per-File Composites

### risk_score

**Signal #35 in `signals.md`**. How dangerous is this file?

```
risk_score(f) = 0.25 × pctl(pagerank, f)
              + 0.20 × pctl(blast_radius_size, f)
              + 0.20 × pctl(cognitive_load, f)
              + 0.20 × instability_factor(f)
              + 0.15 × (1 - bus_factor(f) / max_bus_factor)

where instability_factor = 1.0 if churn_trajectory ∈ {CHURNING, SPIKING}
                           0.3 otherwise

pctl(signal, f) = |{v ∈ all_files : signal(v) ≤ signal(f)}| / |all_files|
```

**Range**: [0, 1]. Display as 1-10 scale: multiply by 10, round to 1 decimal. Higher = riskier.
**Inputs**: pagerank, blast_radius_size, cognitive_load, churn_trajectory, bus_factor.
**Polarity**: High is bad.

### wiring_quality

**Signal #36 in `signals.md`**. How well-connected and implemented is this file?

```
wiring_quality(f) = 1 - (
    0.30 × is_orphan(f)
  + 0.25 × stub_ratio(f)
  + 0.25 × (phantom_import_count(f) / max(import_count(f), 1))
  + 0.20 × (broken_call_count(f) / max(total_calls(f), 1))
)
```

**Range**: [0, 1]. Display as 1-10 scale: multiply by 10, round to 1 decimal. Higher = better wired.
**Inputs**: is_orphan, stub_ratio, phantom_import_count, import_count, broken_call_count.
**Polarity**: High is good.

---

## Per-Module Composites

### health_score

**Signal #51 in `signals.md`**. Overall module health.

```
health_score(m) = 0.20 × cohesion(m)
               + 0.15 × (1 - coupling(m))
               + 0.20 × (1 - main_seq_distance(m))
               + 0.15 × boundary_alignment(m)
               + 0.15 × role_consistency(m)
               + 0.15 × (1 - mean(stub_ratio across files in m))
```

**Range**: [0, 1]. Display as 1-10 scale: multiply by 10, round to 1 decimal. Higher = healthier.
**Inputs**: cohesion, coupling, main_seq_distance, boundary_alignment, role_consistency, stub_ratio.
**Polarity**: High is good.

**None guard**: If `instability = None` (isolated module, Ca+Ce=0), skip the `main_seq_distance` term and redistribute its 0.20 weight:

```
# Original weights (sum = 1.0):
cohesion:           0.20
(1-coupling):       0.15
(1-main_seq_dist):  0.20  ← SKIP if instability=None
boundary:           0.15
role_consistency:   0.15
(1-stub_ratio):     0.15

# Redistributed weights when instability=None (sum = 1.0):
cohesion:           0.25  (+0.05)
(1-coupling):       0.1875 (+0.0375)
boundary:           0.1875 (+0.0375)
role_consistency:   0.1875 (+0.0375)
(1-stub_ratio):     0.1875 (+0.0375)

# Implementation:
if instability is None:
    # Redistribute 0.20 proportionally to remaining 5 terms
    scale = 1.0 / 0.80  # = 1.25
    return (0.20 * scale * cohesion +
            0.15 * scale * (1 - coupling) +
            0.15 * scale * boundary +
            0.15 * scale * role_consistency +
            0.15 * scale * (1 - mean_stub_ratio))
```

---

## Global Composites

### wiring_score

**Signal #60 in `signals.md`**. Codebase-level AI code quality.

```
wiring_score = 1 - (
    0.25 × orphan_ratio
  + 0.25 × phantom_ratio
  + 0.20 × glue_deficit
  + 0.15 × mean(stub_ratio across all files)
  + 0.15 × clone_ratio
)

where clone_ratio = |files involved in NCD clone pairs| / |total files|
```

**Range**: [0, 1]. Display as 1-10 scale: multiply by 10, round to 1 decimal. Higher = better wired.
**Polarity**: High is good.

### ai_quality (deprecated alias)

Alias for `wiring_score`. Same formula. **Note**: Not a separate signal in `signals.md`. Use `wiring_score` (#60) in code. The alias exists only for user-facing display ("AI Quality Score").

### architecture_health

**Signal #61 in `signals.md`**. How well the system is structured.

```
architecture_health = 0.25 × (1 - violation_rate)
                    + 0.20 × mean(cohesion across modules)
                    + 0.20 × (1 - mean(coupling across modules))
                    + 0.20 × (1 - mean(main_seq_distance across modules))
                    + 0.15 × mean(boundary_alignment across modules)

where violation_rate = violating_cross_module_edges / total_cross_module_edges
```

**Range**: [0, 1]. Display as 1-10 scale: multiply by 10, round to 1 decimal. Higher = healthier architecture.
**Polarity**: High is good.

### team_risk (unnumbered — not in `signals.md`)

Social/organizational risk score. Not a numbered signal because it is display-only — no finder or composite consumes it.

```
team_risk = 1 - (
    0.30 × (min_bus_factor_critical / 3.0)        # capped at 3; bus_factor ∈ [1, ∞) where 1 = single author, 2^H where H is author entropy. The /3.0 caps the contribution at bus_factor=3.
  + 0.25 × (1 - max(knowledge_gini across modules))
  + 0.25 × (1 - mean(coordination_cost) / 5.0)    # capped at 5
  + 0.20 × conway_alignment                        # higher = teams match architecture (good)
)

where min_bus_factor_critical = min(bus_factor) across files with pctl(pagerank) > 0.75
      conway_alignment = 1 - mean(author_distance) across structurally-coupled module pairs
        (module pairs with ≥1 cross-module import edge)
        If author_distances unavailable (solo project): conway_alignment = 1.0 (no team risk)
        If no structurally-coupled module pairs: conway_alignment = 1.0
```

**Range**: [0, 1]. Display as 1-10 scale: multiply by 10, round to 1 decimal. Higher = more team risk (bad).
**Polarity**: High is bad.

### codebase_health

**Signal #62 in `signals.md`**. The one number.

```
codebase_health = 0.30 × architecture_health
               + 0.30 × wiring_score
               + 0.20 × (global_bus_factor / team_size)
               + 0.20 × modularity

where global_bus_factor = min_bus_factor_critical (capped at team_size)
      team_size = |distinct authors in recent window|
```

**Finding density removed**: The original formula included `0.20 × (1 - finding_density)` but this creates a **circular dependency** — finders need SignalField → SignalField includes codebase_health → codebase_health needs finding count → findings computed by finders. Weights redistributed to remaining terms. Finding density can be displayed alongside codebase_health but must NOT be part of its computation.

**Range**: [0, 1]. Display as 1-10 scale: multiply by 10, round to 1 decimal. Higher = healthier.
**Polarity**: High is good.

---

## Normalization

All composite inputs that are percentile-based use:

```
pctl(signal, f) = |{v ∈ all_files : signal(v) ≤ signal(f)}| / |all_files|
```

This is the canonical percentile formula. All documents use this form.

### Tiered normalization (for small codebases)

| Codebase size | Strategy |
|---|---|
| **< 15 files** | No percentiles. Use absolute thresholds from `signals.md` only. Composites not computed — show raw signal values. |
| **15-50 files** | Bayesian percentiles: `posterior_pctl = Beta(α + rank, β + n - rank)` where (α, β) are priors from PROMISE dataset. |
| **50+ files** | Standard percentile normalization. Full composites. |

---

## Tier Behavior

| Composite | ABSOLUTE (<15) | BAYESIAN (15-50) | FULL (50+) |
|-----------|---------------|-----------------|------------|
| `risk_score` | Not computed (needs pctl) | Computed (Bayesian pctl) | Computed |
| `wiring_quality` | Not computed | Computed | Computed |
| `health_score` | Not computed (needs module metrics) | Computed | Computed |
| `wiring_score` | Not computed | Computed | Computed |
| `architecture_health` | Not computed (needs modules) | Computed | Computed |
| `team_risk` | Not computed | Computed | Computed |
| `codebase_health` | Not computed | Computed | Computed |

**ABSOLUTE tier**: Show raw signal values instead of composites. Users see individual metrics (pagerank=0.12, cognitive_load=45, bus_factor=1) rather than fused scores. This avoids misleading composites from tiny sample sizes.

---

## Weight Calibration Plan

**Phase 1 (v2.0)**: Hand-tuned weights as specified above. Display rank ordering, not absolute scores.

**Phase 2 (post-validation)**:
1. Run Shannon Insight on Technical Debt Dataset (33 Apache Java projects).
2. Extract per-file signal vectors.
3. Label files: y = 1 if file has known bug in Jira, 0 otherwise.
4. Fit logistic regression: `P(bug | x) = σ(w · x)`.
5. Learned weights replace hand-tuned weights.
6. Cross-validate: train on 25 projects, test on 8. Report AUC.
7. Acceptance: AUC > 0.70, per-finder precision > 0.50.

**Literature guidance** (from W3 research): process metrics (churn, authors, age) outperform code metrics (complexity, coupling) for defect prediction. Temporal signals (D6, D7, D8) should likely carry MORE weight than structural signals (D1, D2, D4).

---

## Health Laplacian

Not a composite score but computed by `signals/`. Uses `raw_risk` (the pre-percentile weighted sum), NOT percentile-based `risk_score`.

```
raw_risk(f) = 0.25 × pagerank(f)/max_pagerank
            + 0.20 × blast_radius_size(f)/max_blast
            + 0.20 × cognitive_load(f)/max_cognitive
            + 0.20 × instability_factor(f)
            + 0.15 × (1 - bus_factor(f)/max_bus_factor)

Δh(f) = raw_risk(f) - mean(raw_risk(n) for n in neighbors(f))

where neighbors(f) = files that import f OR that f imports (undirected neighborhood)
```

**Why raw_risk, not risk_score**: Percentile normalization produces a near-uniform distribution, which makes the Laplacian meaningless (every node ≈ same value). The raw weighted sum preserves natural variation.

**Division by zero guards**: If `max_pagerank`, `max_blast`, `max_cognitive`, or `max_bus_factor` is 0, the corresponding term contributes 0 (not NaN). In practice: pagerank always > 0 due to damping factor; bus_factor always >= 1; blast/cognitive can be 0 for disconnected graphs or empty files.

**Interpretation**: Δh > 0 means file is worse than its neighborhood. Δh > 0.4 triggers WEAK_LINK finder.

**Edge case**: If a file has no neighbors (orphan), Δh = 0.0 (no neighborhood to compare against). Orphan files are handled by ORPHAN_CODE finder instead, so WEAK_LINK (which triggers at Δh > 0.4) will not fire for orphans.
