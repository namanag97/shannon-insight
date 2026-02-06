# Registry: Composite Scores

Composite scores fuse multiple signals (from `signals.md`) into single summary numbers. Each is defined here with its exact formula and weights.

**Calibration note**: Initial weights are hand-tuned. They will be replaced by logistic regression weights trained on the Technical Debt Dataset (33 Apache projects, 95K labeled issues) once validation infrastructure (see `validation/strategy.md`) is in place. Until then, use rank ordering ("this file is the #1 riskiest") rather than absolute score interpretation.

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

**Range**: [0, 1]. Higher = riskier.
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

**Range**: [0, 1]. Higher = better wired.
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

**Range**: [0, 1]. Higher = healthier.
**Inputs**: cohesion, coupling, main_seq_distance, boundary_alignment, role_consistency, stub_ratio.
**Polarity**: High is good.

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

**Range**: [0, 1]. Higher = better wired.
**Polarity**: High is good.

### ai_quality

Alias for `wiring_score`. Same formula.

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

**Range**: [0, 1]. Higher = healthier architecture.
**Polarity**: High is good.

### team_risk

Social/organizational risk score.

```
team_risk = 1 - (
    0.30 × (min_bus_factor_critical / 3.0)        # capped at 3
  + 0.25 × (1 - max(knowledge_gini across modules))
  + 0.25 × (1 - mean(coordination_cost) / 5.0)    # capped at 5
  + 0.20 × conway_correlation                      # higher = teams match architecture
)

where min_bus_factor_critical = min(bus_factor) across files with pctl(pagerank) > 0.75
```

**Range**: [0, 1]. Higher = more team risk (bad).
**Polarity**: High is bad.

### codebase_health

**Signal #62 in `signals.md`**. The one number.

```
codebase_health = 0.25 × architecture_health
               + 0.25 × wiring_score
               + 0.20 × (1 - finding_density)
               + 0.15 × (global_bus_factor / team_size)
               + 0.15 × modularity

where finding_density = |findings with severity > 0.5| / |total files|
      global_bus_factor = min_bus_factor_critical (capped at team_size)
      team_size = |distinct authors in recent window|
```

**Range**: [0, 1]. Higher = healthier.
**Polarity**: High is good.

---

## Normalization

All composite inputs that are percentile-based use:

```
pctl(x, values) = |{v ∈ values : v ≤ x}| / |values|
```

### Tiered normalization (for small codebases)

| Codebase size | Strategy |
|---|---|
| **< 15 files** | No percentiles. Use absolute thresholds from `signals.md` only. Composites not computed — show raw signal values. |
| **15-50 files** | Bayesian percentiles: `posterior_pctl = Beta(α + rank, β + n - rank)` where (α, β) are priors from PROMISE dataset. |
| **50+ files** | Standard percentile normalization. Full composites. |

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
