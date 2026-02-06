# signals/normalization.md -- Percentile Normalization and Tiered Analysis

## Purpose

Raw signals have incompatible units and ranges: `lines` is [0, infinity), `compression_ratio` is [0, 1], `pagerank` sums to 1 across all files. Normalization maps every numeric signal to a common [0, 1] scale so they can be combined in composite scores.

The core formula is percentile ranking. The challenge is that percentile ranking degrades for small samples. This module implements a three-tier approach to handle codebases of any size.

## Percentile Formula

For signal S and file f within a set of all files:

```
pctl(S, f) = |{v in all_files : S(v) <= S(f)}| / |all_files|
```

Range: [0, 1]. A value of 0.95 means this file's signal is higher than 95% of all files. Ties share the same percentile. This is a rank-order statistic -- robust to outliers, distribution-free.

## Three Tiers

The tier is determined once per analysis run based on `|all_files|`. It applies to all normalization within that run.

### Tier 1: ABSOLUTE (< 15 files)

**Problem**: With 10 files, each percentile increment is 10 percentage points. Ranking is noise -- the difference between "50th percentile" and "60th percentile" is exactly one file.

**Strategy**: Do not compute percentiles. Do not compute composite scores. Use absolute thresholds only.

Absolute thresholds are defined per signal in `registry/signals.md`. These are universal bounds derived from industry standards (McCabe 1976 for complexity, NIST for nesting, etc.) and apply regardless of codebase size.

| Signal | Absolute threshold | Interpretation |
|--------|-------------------|----------------|
| `lines` | > 500 | File is large |
| `function_count` | > 30 | Too many functions |
| `max_nesting` | > 4 | Deep nesting |
| `impl_gini` | > 0.6 | Bimodal implementation |
| `stub_ratio` | > 0.5 | Mostly stubs |
| `concept_entropy` | > 1.5 | Unfocused |
| `naming_drift` | > 0.7 | Filename misleads |
| `todo_density` | > 0.05 | Many incomplete markers |
| `phantom_import_count` | > 0 | Broken references |
| `broken_call_count` | > 0 | Broken call targets |
| `churn_cv` | > 1.0 | Erratic changes |
| `fix_ratio` | > 0.4 | Bug attractor |

Structural facts (is_orphan, phantom imports, broken calls) are valid at any size -- they are binary, not statistical.

**Output**: `FileSignals` with raw values. `percentiles` field is `None`. `risk_score` and other composites are `None`. Finders that require percentiles are skipped with a message explaining why.

### Tier 2: BAYESIAN (15-50 files)

**Problem**: Percentiles are computable but noisy. With 30 files, each rank step is ~3.3 percentile points. Extreme percentiles (95th, 99th) are not meaningful.

**Strategy**: Bayesian-regularized percentiles using priors from industry datasets.

```
posterior_pctl(S, f) = E[Beta(alpha + rank, beta + n - rank)]
                     = (alpha + rank) / (alpha + beta + n)

where:
  rank   = |{v : S(v) <= S(f)}|
  n      = |all_files|
  alpha, beta = prior parameters from PROMISE/TechDebt datasets
```

The Beta distribution prior pulls extreme percentiles toward the center when sample size is small. With n = 30 and flat prior (alpha = beta = 1), the 30th file has posterior pctl = 31/32 = 0.97 instead of 1.0 -- a small but meaningful regularization.

**Prior calibration**: For each signal, fit a Beta distribution to the signal values across the Technical Debt Dataset (33 Apache projects, thousands of files). This produces signal-specific (alpha, beta) pairs that encode "what typical codebases look like." These priors are stored as constants.

**Output**: `FileSignals` with Bayesian percentiles. Composites are computed but displayed with a confidence qualifier: "Based on a small sample (N files). Rankings may shift as codebase grows."

### Tier 3: FULL (50+ files)

Standard percentile normalization as defined above. Full composite scores with no qualifiers.

At 50+ files, each rank step is <= 2 percentile points. The 95th percentile captures at least 2-3 files. Gini, PCA, and clustering are statistically meaningful.

## Signal Independence and Covariance Analysis (W5)

Composite scores assume signals contribute independent information. If two signals are highly correlated (e.g., `lines` and `function_count`), weighting both is double-counting the same information.

### Correlation check

At analysis time (tier FULL only), compute the Pearson correlation matrix across all per-file numeric signals:

```
R[i, j] = corr(S_i across all files, S_j across all files)
```

Flag pairs where |R[i, j]| > 0.8 as redundant. Report these in verbose output.

### Recommended action

When redundant pairs are detected:

1. Keep the signal that is more interpretable (prefer `pagerank` over `betweenness` if they correlate).
2. In composite score computation, halve the weight of the subordinate signal.
3. Log a warning: "Signals X and Y are highly correlated (r=0.87). Composite weights adjusted."

### PCA-based alternative

For advanced users or validation:

```
1. Standardize all per-file numeric signals (zero mean, unit variance)
2. Compute PCA eigenvalue spectrum
3. Report effective dimensionality k where sum(lambda_1..lambda_k) / sum(all lambda) > 0.90
4. If k << d (e.g., 4 dimensions explain 90% of variance):
   - PC scores can replace raw signals in composites
   - Each PC is interpretable: "PC1 = structural risk, PC2 = social risk, ..."
```

This is a validation step. If run on 5-10 open-source projects pre-launch, it answers the question: "Are our 8 dimensions genuinely independent, or actually 3-4 latent factors?"

## Implementation Notes

- Percentiles are computed once per `SignalFusion.fuse()` call, then cached on `FileSignals.percentiles`.
- Tier determination is a single comparison at the start of `fuse()`.
- Bayesian priors are compile-time constants (a dict of `{signal_name: (alpha, beta)}`) loaded from a data file.
- Correlation check runs only in verbose mode (it requires O(d^2 * n) computation).
- Normalization is idempotent -- calling it twice produces the same result.
