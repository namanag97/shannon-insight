# signals/composites.md -- Composite Score Computation

## Purpose

Composite scores fuse multiple normalized signals into single summary numbers at each scale (file, module, global). They answer high-level questions: "How risky is this file?", "How healthy is this module?", "What is the overall codebase quality?"

All composite formulas and weights are defined in `registry/composites.md`. This document describes the **computation pipeline** -- how the formulas are evaluated, how missing inputs are handled, and how weights will be calibrated.

## Computation Pipeline

### Step 1: Collect upstream signals

For each entity (file, module, or codebase), gather the raw signal values from `FileSignals`, `ModuleSignals`, and `GlobalSignals`. These are already populated by `SignalFusion` from upstream modules.

### Step 2: Normalize

Apply percentile normalization (see `normalization.md`) to all numeric inputs. Composites that use `pctl()` in their formulas operate on percentile-ranked values. Composites that use raw values (e.g., `is_orphan`, `stub_ratio`) use them directly.

### Step 3: Handle missing inputs

If a signal required by a composite is `None` (upstream module did not run):

1. Drop the term from the weighted sum.
2. Renormalize remaining weights to sum to 1.0.
3. Mark the composite as `partial` (metadata flag, not exposed in the value).

Example: `risk_score` needs `bus_factor` (from temporal/). If temporal/ did not run:

```
Original: 0.25*pctl(pagerank) + 0.20*pctl(blast_radius) + 0.20*pctl(cognitive_load)
        + 0.20*instability_factor + 0.15*(1 - bus_factor/max_bus_factor)

Without bus_factor: drop the 0.15 term, renormalize:
  0.25/0.85 * pctl(pagerank) + 0.20/0.85 * pctl(blast_radius)
  + 0.20/0.85 * pctl(cognitive_load) + 0.20/0.85 * instability_factor

  = 0.294*pctl(pagerank) + 0.235*pctl(blast_radius)
  + 0.235*pctl(cognitive_load) + 0.235*instability_factor
```

This ensures composites are always in [0, 1] and always computable (as long as at least one input exists).

### Step 4: Compute weighted sum

Apply the formula from `registry/composites.md` with (potentially renormalized) weights.

### Step 5: Clamp to [0, 1]

All composites have range [0, 1]. Clamp the result. In practice the weighted sum of [0, 1] values stays in [0, 1], but edge cases (floating point, renormalization) may produce values slightly outside bounds.

## Composite Catalog

All formulas are defined in `registry/composites.md`. Summary of what is computed at each level:

### Per-file composites

| Signal | # | Inputs | What it answers |
|--------|---|--------|-----------------|
| `risk_score` | 35 | pagerank, blast_radius_size, cognitive_load, churn_trajectory, bus_factor | How dangerous is this file? |
| `wiring_quality` | 36 | is_orphan, stub_ratio, phantom_import_count, import_count, broken_call_count | How well-connected and implemented is this file? |

### Per-module composites

| Signal | # | Inputs | What it answers |
|--------|---|--------|-----------------|
| `health_score` | 51 | cohesion, coupling, main_seq_distance, boundary_alignment, role_consistency, stub_ratio | Overall module health? |

### Global composites

| Signal | # | Inputs | What it answers |
|--------|---|--------|-----------------|
| `wiring_score` | 60 | orphan_ratio, phantom_ratio, glue_deficit, stub_ratio, clone_ratio | Codebase-level AI code quality? |
| `architecture_health` | 61 | violation_rate, cohesion, coupling, main_seq_distance, boundary_alignment | How well is the system structured? |
| `team_risk` | - | bus_factor, knowledge_gini, coordination_cost, conway_correlation | Social/organizational risk? |
| `codebase_health` | 62 | architecture_health, wiring_score, global_bus_factor, modularity | The one number (finding_density removed to avoid circular dep). |

## Calibration Strategy (W3)

### Phase 1: Hand-tuned weights (v2.0)

Initial weights as specified in `registry/composites.md` are hand-tuned based on domain knowledge and literature guidance. Key principle from research: process metrics (churn, authors) outperform code metrics (complexity, coupling) for defect prediction, so temporal signals should carry more weight.

**Display strategy**: Use **rank ordering** rather than absolute score interpretation. Show "This file is the #1 riskiest in your codebase" rather than "risk = 0.87". Rank ordering is robust to weight misspecification -- even with wrong weights, the top-5 riskiest files are likely correct if the input signals are meaningful.

### Phase 2: Logistic regression calibration (post-validation)

Once the validation infrastructure is in place:

1. Run Shannon Insight on the Technical Debt Dataset (33 Apache Java projects).
2. Extract per-file signal vectors: `x(f) = [pctl(pagerank), pctl(blast_radius), pctl(cognitive_load), ...]`
3. Label files from ground truth: `y(f) = 1` if file has known bug in Jira, `0` otherwise.
4. Fit logistic regression: `P(bug | x) = sigmoid(w * x)`.
5. Learned weights `w` replace hand-tuned weights in composite formulas.
6. Cross-validate: train on 25 projects, test on 8. Report AUC.
7. **Acceptance criteria**: AUC > 0.70, per-finder precision > 0.50.

Per-signal predictive power is ranked by |coefficient| in the logistic model. Signals with near-zero coefficients may be dropped or downweighted.

### Literature guidance

| Rank | Most predictive signal | Source |
|------|----------------------|--------|
| 1 | Relative code churn | Nagappan & Ball 2005, 89% accuracy |
| 2 | Number of distinct committers | Rahman & Devanbu 2013 |
| 3 | File age / recency | Multiple studies |
| 4 | Coupling (PageRank proxy) | Basili CK metrics validation |
| 5 | Lack of cohesion | CK metrics suite |
| 6 | Cyclomatic complexity | McCabe -- correlated but weaker than process metrics |

This confirms: temporal signals (D6, D7, D8) should likely carry MORE weight than structural signals (D1, D2, D4) in the final calibrated model.

## PCA-Based Alternative (W5)

If the dimension correlation analysis (see `normalization.md`) reveals that effective dimensionality is low (3-4 PCs explain 90%+ variance):

1. Use PC scores as composite inputs instead of raw (percentiled) signals.
2. Each PC becomes an interpretable factor: "PC1 = structural risk", "PC2 = social risk", etc.
3. Composite = weighted sum of PC scores, avoiding double-counting correlated signals.
4. Weights on PCs can still be calibrated via logistic regression.

This is not the default approach. It requires validation on real codebases first. If PCA shows that the 8 dimensions are genuinely independent (effective dimensionality >= 7), the current weighted-sum approach with raw signals is correct and this alternative is unnecessary.

## Fallback Behavior by Tier

| Tier | Composite behavior |
|------|-------------------|
| ABSOLUTE (< 15 files) | Composites not computed. Show raw values with absolute threshold violations. |
| BAYESIAN (15-50 files) | Composites computed with Bayesian percentiles. Displayed with confidence qualifier. |
| FULL (50+ files) | Full composite computation. No qualifiers. |

## Implementation Notes

- Composite computation is a single pass after normalization. No iteration or convergence needed.
- Missing-input weight renormalization is per-composite, per-entity. Different files may have different sets of available signals (e.g., new files with no git history have no temporal signals).
- `codebase_health` depends on `architecture_health` and `wiring_score`, which must be computed first. The computation order is: per-file composites -> per-module composites -> global composites.
- All composite values are stored on `FileSignals.risk_score`, `ModuleSignals.health_score`, `GlobalSignals.codebase_health`, etc.
