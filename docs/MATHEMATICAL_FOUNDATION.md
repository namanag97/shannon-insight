# Mathematical Foundation of Shannon Insight

## 1. The Central Idea

A codebase is an information system. Files emit *signals* — structural patterns,
dependency relationships, change frequency, semantic content, conceptual density.
No single signal reliably distinguishes intentional design from architectural
debt, because every metric has a valid counter-example (high coupling is fine for
a utility library; high complexity is expected in a parser). The only reliable
detector is *convergence across independent channels*: when multiple orthogonal
measures agree that a file is unusual, the finding is trustworthy.

Shannon Insight formalizes this intuition as a five-stage directed acyclic graph
(DAG), where each stage feeds the next and never feeds backward.

---

## 2. Pipeline DAG

```
                         ┌─────────────────────┐
                         │   Source Files (N)   │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                    L1   │   Language Scanner   │  FileMetrics per file
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                    L2   │ Primitive Extractor  │  5 raw primitives per file
                         │  ┌────┬────┬───┬──┐ │
                         │  │ H  │ PR │ V │ C│L│
                         │  └────┴────┴───┴──┘ │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                    L3   │  Anomaly Detector    │  z-scores + anomaly flags
                         │  (normalize → test)  │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                    L4   │   Signal Fusion      │  (score, confidence) per file
                         │  consistency-weighted │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                    L5   │ Recommendation Engine │  AnomalyReport[]
                         └─────────────────────┘
```

**Data flow** (types at each edge):

| Edge    | Type flowing                          | Size    |
|---------|---------------------------------------|---------|
| L1 → L2 | `Dict[path, FileMetrics]`            | N       |
| L2 → L3 | `Dict[path, Primitives]` (5 floats)  | N × 5   |
| L3 → L4 | `Dict[path, Primitives]` (z-scores) + anomaly flags | N × 5 |
| L4 → L5 | `Dict[path, (score, confidence)]`    | N × 2   |

No stage reads the output of a later stage. This is a strict DAG — there are no
feedback loops and no circular dependencies between layers.

---

## 3. Layer 2 — The Five Primitives

Each primitive measures a different *dimension* of code quality. They are
designed to be weakly correlated (empirically |ρ| < 0.35 between all pairs),
so each contributes independent information.

### 3.1 Structural Entropy

**Source theory**: Shannon, "A Mathematical Theory of Communication" (1948).

**What we measure**: The diversity of AST node types within a single file.

**Canonical definition**:

```
H(X) = -Σᵢ p(xᵢ) log₂ p(xᵢ)
```

where X is the random variable over AST node types, and p(xᵢ) = count(xᵢ) / total.

**Normalization**: We divide by maximum possible entropy to get a value in [0, 1]:

```
H_norm = H(X) / log₂(|X|)
```

where |X| = number of distinct node types observed in the file.

**Why normalize**: Raw entropy depends on alphabet size. A file with 3 node types
and a file with 30 node types cannot be compared directly. Normalization removes
this dependency: H_norm = 1 means the distribution is perfectly uniform (maximum
disorder); H_norm = 0 means a single node type dominates (minimum disorder).

**Edge cases handled in code** (`math/entropy.py`):
- Empty distribution (total = 0): returns 0.0
- Single event type (|X| = 1): returns 0.0 (log₂(1) = 0, no division by zero)
- Zero-count events in dictionary: skipped by `p > 0` guard

**Configurable parameters**: None. The formula is parameter-free — it depends only
on the AST distribution, which is produced by the language scanner.

**Interpretation for code**:
- H_norm near 1.0: Many different AST node types, none dominant. The file mixes
  concerns chaotically (functions, classes, constants, type aliases, decorators,
  all in equal measure). Suggests the file lacks a coherent structural pattern.
- H_norm near 0.0: One or two node types dominate. Common for auto-generated
  code, data files, or copy-pasted blocks. May indicate duplication.
- Moderate H_norm (0.4–0.7): Typical for well-structured code.

**Additional operations in the Entropy class**:

*KL Divergence*: `D_KL(P||Q) = Σ P(x) log₂(P(x)/Q(x))`. Measures how one
file's AST distribution diverges from a reference distribution. Returns +inf
when P has support where Q does not (mathematically correct — Cover & Thomas,
Theorem 2.6.3). Available for comparing files against a "typical" baseline.

*Joint Entropy*: `H(X,Y) = -Σ_x Σ_y p(x,y) log₂ p(x,y)`. Requires a true
joint distribution keyed by tuples `(x, y)`. For independent variables, the
chain rule gives H(X,Y) = H(X) + H(Y).

*Pooled Entropy*: `H(merge(X₁, X₂, ...))`. Merges multiple count distributions
into one and computes H of the mixture. This is NOT joint entropy — it is the
entropy of the pooled sample. Useful when you want a single entropy measure
across a group of files.

---

### 3.2 Network Centrality (PageRank)

**Source theory**: Brin & Page, "The Anatomy of a Large-Scale Hypertextual Web
Search Engine" (1998). Dangling-node treatment follows Langville & Meyer,
*Google's PageRank and Beyond* (2006), Chapter 3.

**What we measure**: Transitive importance of a file in the import graph.

**Canonical definition**:

```
PR(v) = (1-d)/N + d × [ Σ_{u→v} PR(u)/L(u) + dangling_sum/N ]
```

where:
- d = damping factor (probability the random surfer follows a link)
- N = total number of files
- L(u) = out-degree of u (number of files u imports)
- dangling_sum = Σ PR(node) for all nodes with L(node) = 0

**Dangling nodes**: Files that import nothing (L = 0) have no outgoing edges.
The standard treatment redistributes their accumulated rank uniformly to all
nodes, modeling a random surfer who "teleports" to a random page when stuck.
This is implemented in `math/graph.py`.

**Algorithm**: Power iteration. Initialize PR(v) = 1/N for all v. Iterate until
max|PR_new(v) - PR_old(v)| < tolerance or iteration limit reached.

**Configurable parameters** (in `shannon-insight.toml`):

| Parameter              | Default | Range     | Effect                           |
|------------------------|---------|-----------|----------------------------------|
| `pagerank_damping`     | 0.85    | [0.0, 1.0] | Higher = more weight on link structure, less on teleportation |
| `pagerank_iterations`  | 20      | [1, 100]  | More iterations = more accurate convergence |
| `pagerank_tolerance`   | 1e-6    | > 0       | Early-stop when max change < this |

**Why d = 0.85**: The original Brin & Page paper uses 0.85. It means 85% of the
time the surfer follows a link; 15% of the time they jump to a random page. This
balances structural importance against uniform baseline. Values closer to 1.0
amplify hub effects; values closer to 0.0 flatten scores toward 1/N.

**Convergence**: For a strongly connected graph with N nodes, power iteration
converges geometrically with rate d. For d = 0.85, after k iterations the error
is bounded by d^k. After 20 iterations: 0.85^20 ≈ 0.039 (< 4% error).

**How centrality is used in the extractor** (`primitives/extractor.py`):
The extractor currently uses an inline PageRank variant that is min-max
normalized to [0, 1]. The canonical `GraphMetrics.pagerank()` in `math/graph.py`
produces scores that sum to 1.0 (a proper probability distribution).

**Supplementary graph metrics** (available in `math/graph.py`):

*Betweenness Centrality* (Brandes' algorithm): Counts how often a node lies on
shortest paths between other pairs. Normalization uses 1/((n-1)(n-2)) for the
directed BFS traversal. Reference: Brandes (2001).

*Eigenvector Centrality*: Power iteration on the adjacency matrix to find the
leading eigenvector. A node is important if it is connected to other important
nodes. Note: ill-defined for disconnected graphs (Perron-Frobenius only applies
to irreducible matrices). Reference: Newman (2010), Section 7.2.

---

### 3.3 Churn Volatility

**What we measure**: How recently and frequently a file changes.

**Current implementation**: Uses filesystem modification timestamps as a proxy.

```
age(f) = now - last_modified(f)
volatility(f) = 1 - age(f) / max_age
```

This is a simple recency score: recently modified files get high volatility,
old files get low volatility. The score is in [0, 1].

**Configurable parameters**: None currently exposed. The timestamp comes from the
filesystem `stat()` call.

**Limitation**: Without git history, we cannot distinguish "one recent edit" from
"50 edits in the last week." The current score is a monotonic function of recency
only. A future git-based implementation would compute:

```
VI = σ(churn_rate) / (μ(churn_rate) + ε)
```

where churn_rate(t) = (insertions + deletions) per time window, and VI is the
coefficient of variation over rolling windows. This would capture *burstiness*,
not just recency.

---

### 3.4 Semantic Coherence

**Source theory**: Salton et al., "A Vector Space Model for Automatic Indexing"
(1975); TF-IDF weighting from Sparck Jones (1972).

**What we measure**: Whether a file's imports and exports are conceptually similar
to the rest of the codebase.

**Algorithm**:

1. Build a "document" for each file: `d = imports ∪ exports` (as a token string).
2. Compute TF-IDF vectors across all file-documents.
3. Compute pairwise cosine similarity: `sim(i, j) = (vᵢ · vⱼ) / (‖vᵢ‖ ‖vⱼ‖)`.
4. Coherence(i) = mean similarity to all OTHER files (self excluded).

**Why exclude self-similarity**: The diagonal of the similarity matrix is always
1.0. Including it inflates coherence scores, especially for small codebases.
The implementation explicitly skips `j == i`.

**Configurable parameters**:

| Parameter       | Default | Set in           | Effect                          |
|-----------------|---------|------------------|---------------------------------|
| `min_df`        | 1       | TfidfVectorizer  | Minimum document frequency      |
| `max_df`        | 0.8     | TfidfVectorizer  | Ignore terms appearing in >80% of files |

**Interpretation**:
- C near 1.0: The file's import/export vocabulary overlaps heavily with most
  other files. It is semantically "typical."
- C near 0.0: The file uses completely different symbols from the rest of the
  codebase. It may be an outlier, a utility with unique dependencies, or a
  misplaced concern.

---

### 3.5 Cognitive Load

**What we measure**: The mental effort required to understand a file, estimated
from structural features.

**Formula** (heuristic):

```
CL = concepts × complexity_score × (1 + nesting_depth / 10)
```

where:
- concepts = functions + structs + interfaces (count of named abstractions)
- complexity_score = cyclomatic complexity reported by the scanner
- nesting_depth = maximum nesting depth of control structures

The `(1 + depth/10)` factor is a linear amplifier that adds 10% load per level
of nesting. For typical code (depth 0–5), this is a 0–50% increase.

**Normalization**: Min-max normalized to [0, 1] across all files.

**Configurable parameters**: None currently. The formula components come from the
language scanner.

**Note**: This formula is a hand-tuned heuristic, not derived from a specific
cognitive science model. It captures the intuition that load increases with the
*product* of conceptual breadth (how many things) and structural complexity (how
tangled), amplified by nesting depth (how deeply nested). A more rigorous
alternative would be SonarSource's Cognitive Complexity metric (2017), which
assigns incremental penalties for nested control flow.

---

## 4. Layer 3 — Normalization and Anomaly Detection

### 4.1 Why Normalize

Raw primitives live on incomparable scales: entropy is in [0, 1], PageRank sums
to 1/N, cognitive load can be any non-negative float. To fuse them, we first
transform all primitives to z-scores:

```
z = (x - μ) / σ
```

After normalization, every primitive has mean 0 and standard deviation 1. A
z-score of +2.0 means "2 standard deviations above the mean" regardless of
which primitive it came from.

### 4.2 Three Normalization Modes

The detector chooses a mode based on sample size:

| Condition       | Mode                    | Method                        |
|-----------------|-------------------------|-------------------------------|
| N < 5 files     | Robust univariate       | Modified z-scores (MAD-based) |
| 5 ≤ N < 10     | Standard univariate     | z = (x - x̄) / s (ddof=1)     |
| N ≥ 10          | Multivariate            | Mahalanobis distance → χ² → z |

**Why MAD for small samples**: The sample standard deviation is unstable for
N < 5. The Median Absolute Deviation is a robust scale estimator (breakdown
point = 50%) that resists outliers. Modified z-scores use:

```
M_i = 0.6745 × (x_i - median) / MAD
```

The constant 0.6745 = 1/Φ⁻¹(3/4) makes M_i comparable to standard z-scores
under normality. Reference: Iglewicz & Hoaglin (1993).

**Why Mahalanobis for large samples**: Individual z-scores ignore correlations
between primitives. Mahalanobis distance accounts for the covariance structure:

```
D² = (x - μ)ᵀ Σ⁻¹ (x - μ)
```

Under multivariate normality, D² follows a χ² distribution with k = 5 degrees
of freedom. We convert:

```
p-value = 1 - χ²_CDF(D², k)
z-equiv = Φ⁻¹(1 - p)
```

This gives a single z-equivalent that captures how anomalous the *combination*
of all five primitives is.

**Edge case — singular covariance**: When features are linearly dependent (e.g.,
all files have identical entropy), the covariance matrix is singular. The code
falls back to Moore-Penrose pseudo-inverse, which projects onto the non-degenerate
subspace. Distances in degenerate directions are effectively zero.

**Edge case — p-value boundaries**: When D² is extremely large, p ≈ 0. The code
maps p ≤ 0 to z = 10.0 (a practical cap) rather than returning 0 or infinity.

### 4.3 Anomaly Thresholding

**Configurable parameter**:

| Parameter           | Default | Range      | Config key             |
|---------------------|---------|------------|------------------------|
| z-score threshold   | 1.5     | (0.0, 10.0) | `z_score_threshold`   |

A file is flagged as anomalous on a primitive if |z| > threshold.

**Why 1.5**: Under a Gaussian distribution, P(|Z| > 1.5) ≈ 0.134. This flags
roughly the top and bottom 13% of files. Lower thresholds (e.g., 1.0) flag 32%
(too noisy); higher thresholds (e.g., 2.0) flag only 5% (misses subtle issues).
The default 1.5 is an empirically reasonable trade-off for code metrics, which
are approximately but not exactly Gaussian.

In multivariate mode, the Mahalanobis z-equivalent is compared against the same
threshold. Individual per-primitive flags use threshold × 0.5 to identify which
dimensions contribute to a multivariate anomaly (since the joint threshold is
already met, individual dimensions may each be only moderately elevated).

---

## 5. Layer 4 — Signal Fusion

### 5.1 The Problem Fusion Solves

Consider a file with z-scores `[+3.0, +0.1, -0.2, +0.3, -0.1]`. Naive
averaging gives 0.62 — a moderate score that hides the fact that only one
primitive (entropy) is strongly anomalous while the others are near zero. Is
this a real finding or noise?

Now consider `[+2.1, +2.3, +1.9, +2.0, +2.2]`. Naive averaging gives 2.1 —
similar magnitude, but here ALL five primitives agree. This is far more
trustworthy.

Fusion must encode *magnitude* AND *consistency*.

### 5.2 Three Consistency Measures

The fusion engine computes three independent measures of signal agreement:

**a) Coefficient of Variation consistency**:

```
CV = σ(|z₁|, ..., |z₅|) / μ(|z₁|, ..., |z₅|)
consistency_CV = 1 / (1 + CV)
```

When all |zᵢ| are equal, CV = 0, consistency = 1.
When |zᵢ| vary widely, CV → ∞, consistency → 0.
Bounded in [0, 1] since CV ≥ 0. Uses absolute values because we care about
magnitude of anomaly, not direction.

**b) Correlation (sign agreement) consistency**:

```
signs = [sign(zᵢ) for zᵢ ≠ 0]
majority = mode(signs)
consistency_corr = count(sᵢ == majority) / len(signs)
```

Measures what fraction of signals point in the same direction. For a truly
anomalous file, we expect most signals to agree (all high or all low).
Bounded in [1/n, 1].

**c) Entropy consistency**:

```
pᵢ = |zᵢ| / Σ|zⱼ|
H = -Σ pᵢ log₂ pᵢ
H_norm = H / log₂(5)
consistency_ent = 1 - H_norm
```

When one signal dominates (one large |z|, rest near zero), entropy is low,
consistency is high — because the "information" is concentrated.
When signals are spread evenly, entropy is maximal, consistency is low.
Bounded in [0, 1].

### 5.3 Combining Consistency Measures

The three consistencies are combined via a weighted geometric mean:

```
C = consistency_CV^0.4 × consistency_corr^0.3 × consistency_ent^0.3
```

The geometric mean is chosen over the arithmetic mean because it is more
sensitive to low values: if ANY consistency measure is near zero, the overall
consistency drops sharply. The exponents (0.4, 0.3, 0.3) sum to 1.0, making
this a proper weighted geometric mean. CV consistency gets the highest weight
because it most directly measures spread of signal magnitudes.

### 5.4 Final Score

```
fused = Σ wᵢ × zᵢ           (weighted average of z-scores)
score = C × |fused|           (consistency-penalized magnitude)
```

The output is a `(score, confidence)` tuple per file, where confidence = C.

**Configurable parameter**:

| Parameter        | Default                          | Config key        |
|------------------|----------------------------------|-------------------|
| `fusion_weights` | [0.20, 0.25, 0.20, 0.15, 0.20]  | `fusion_weights`  |

The weights correspond to [entropy, centrality, churn, coherence, cognitive].
Centrality gets the highest weight (0.25) because hub-related architectural
issues tend to have the broadest blast radius. Coherence gets the lowest (0.15)
because TF-IDF on import tokens is a coarse semantic measure. Weights are
auto-normalized to sum to 1.0 during config validation.

### 5.5 Supplementary Fusion Methods

The codebase also provides fusion methods not used in the default pipeline but
available for advanced use:

**Dempster-Shafer combination** (`math/fusion.py`, `primitives/fusion.py`):
Evidence-theoretic combination where each source provides a mass function over
hypothesis sets (frozensets). Uses Dempster's rule:

```
m(A) = [ Σ_{B∩C=A} m₁(B) × m₂(C) ] / (1 - K)
```

where K = Σ_{B∩C=∅} m₁(B) × m₂(C) is the conflict coefficient. Reference:
Shafer, "A Mathematical Theory of Evidence" (1976).

**Bayesian fusion** (`math/fusion.py`, `primitives/fusion.py`):
Standard Bayes' theorem: P(H|E) = P(E|H) × P(H) / P(E). Computes posteriors
for each hypothesis, normalizes by total evidence, and returns the maximum
posterior with an entropy-based confidence measure. Reference: Bishop, "Pattern
Recognition and Machine Learning" (2006), Chapter 1.2.

**Multivariate fusion** (`primitives/fusion.py`):
Uses Mahalanobis distance on the z-score vector, accounting for the covariance
between signals. Converts D² to a z-equivalent via χ² CDF + inverse normal CDF.
Falls back to L2 norm when the covariance matrix is ill-conditioned (condition
number > 10¹²).

**Adaptive fusion**: Weights signals by their individual reliability scores.
`final = Σ(reliability_i × z_i) / Σ reliability_i`.

**Confidence-weighted fusion**: Similar to adaptive, but uses geometric mean of
confidences for overall confidence (more sensitive to low-confidence signals).

---

## 6. Layer 5 — Root Cause Attribution

The recommendation engine maps anomaly flag patterns to architectural diagnoses:

| Pattern                                  | Root Cause              | Recommendation              |
|------------------------------------------|-------------------------|-----------------------------|
| high_centrality + semantic_coherence_low | Brittle monolithic hub  | Split into focused modules  |
| high_cognitive_load + structural_entropy_high | Chaotic complexity  | Refactor, standardize       |
| high_volatility + high_centrality        | Unstable critical path  | Stabilize interface, add tests |
| structural_entropy_low + semantic_coherence_low | Duplicated code  | Extract common abstractions |

The engine does not introduce new mathematical computations — it is a rule-based
mapper from (anomaly_flags, z-scores) to (root_causes, recommendations).

---

## 7. Robust Statistics (Supporting Layer)

These methods from `math/robust.py` are used by the anomaly detector for small
sample sizes and by supplementary outlier detection.

### 7.1 Median Absolute Deviation (MAD)

```
MAD = median(|x_i - median(x)|)
```

A robust scale estimator. The median has a breakdown point of 50% (up to half
the data can be corrupted without affecting the result), so MAD inherits this
robustness. No parameters.

### 7.2 Modified Z-scores

```
M_i = 0.6745 × (x_i - x̃) / MAD
```

where x̃ = median. The constant 0.6745 = 1/Φ⁻¹(3/4) makes M_i comparable to
standard z-scores under the assumption of normality. If the data is non-normal,
the scores are still meaningful as a robust measure of "how many MADs from the
median," but the 0.6745 scaling loses its exact probabilistic interpretation.

Reference: Iglewicz & Hoaglin, "Volume 16: How to Detect and Handle Outliers"
(1993).

Default outlier threshold: |M| > 3.5.

### 7.3 IQR Outlier Detection

```
outlier if x < Q1 - k × IQR  or  x > Q3 + k × IQR
```

where IQR = Q3 - Q1 and k = 1.5 (Tukey's standard). Non-parametric — makes no
distributional assumptions.

Reference: Tukey, "Exploratory Data Analysis" (1977).

### 7.4 Grubbs' Test

```
G = max|x_i - x̄| / s
```

Tests the null hypothesis that there are no outliers in a univariate sample.
The critical value uses:

```
G_crit = ((n-1)/√n) × √(t²_{α/(2n), n-2} / (n - 2 + t²_{α/(2n), n-2}))
```

where t is the Student's t-distribution quantile. The test is two-sided with
significance α = 0.05 by default.

Reference: Grubbs, "Procedures for Detecting Outlying Observations in Samples"
(1969), Technometrics, 11(1).

---

## 8. Configuration Reference

All tunable parameters live in `shannon-insight.toml` (or environment variables
with `SHANNON_` prefix):

```toml
# ── Anomaly Detection ──
z_score_threshold = 1.5        # Flag files with |z| > this value

# ── PageRank ──
pagerank_damping = 0.85        # Random surfer damping factor
pagerank_iterations = 20       # Max power iteration steps
pagerank_tolerance = 1e-6      # Early-stop convergence criterion

# ── Signal Fusion ──
fusion_weights = [0.20, 0.25, 0.20, 0.15, 0.20]
#                 ent   cent   churn  coher  cogn

# ── File Filtering ──
max_file_size_mb = 10.0
max_files = 10000
exclude_patterns = ["*_test.go", "vendor/*", "node_modules/*", ...]

# ── Performance ──
parallel_workers = null         # null = auto-detect CPU count
timeout_seconds = 10

# ── Cache ──
enable_cache = true
cache_dir = ".shannon-cache"
cache_ttl_hours = 24
```

**Parameter interactions**:
- Lowering `z_score_threshold` increases sensitivity (more files flagged, more
  false positives). Raising it increases specificity.
- Changing `fusion_weights` re-balances which primitives dominate the final score.
  Setting a weight to 0 effectively disables that primitive.
- `pagerank_damping` close to 1.0 amplifies hub/authority structure;
  close to 0.0 makes all files near-equal.

---

## 9. Mathematical Properties

### 9.1 Primitive Independence

The five primitives are designed to be weakly correlated. Empirically, |ρ| < 0.35
for all pairs. This means each primitive contributes independent information to
the fusion stage. If primitives were highly correlated, the five-dimensional
analysis would collapse to effectively fewer dimensions, reducing discriminative
power.

The Mahalanobis distance in multivariate mode explicitly accounts for whatever
residual correlation exists via the covariance matrix inverse.

### 9.2 Consistency Bound

All three consistency measures are bounded in [0, 1]:

- CV consistency: CV ≥ 0 ⟹ 1/(1+CV) ∈ (0, 1]
- Correlation: proportion of agreements ∈ [1/n, 1]
- Entropy: 1 - H_norm ∈ [0, 1] since H_norm ∈ [0, 1]

The geometric mean of values in [0, 1] with exponents summing to 1 is also in
[0, 1]. Therefore the overall consistency C ∈ [0, 1].

### 9.3 Normalization Invariance

Z-score normalization is a location-scale transform:

```
E[z] = 0,  Var[z] = 1
```

This makes all primitives comparable regardless of their original scale. A z-score
of +2 means "2 standard deviations above the codebase mean" whether it refers to
entropy (in [0,1]) or cognitive load (in [0, ∞)).

### 9.4 PageRank Convergence

For a stochastic matrix with damping d, power iteration converges at rate d per
step. Error after k iterations: O(d^k). For d = 0.85 and k = 20:

```
0.85^20 ≈ 0.039
```

The scores are accurate to within ~4% relative error.

The dangling-node redistribution ensures the transition matrix is stochastic
(rows sum to 1) and primitive (aperiodic, irreducible due to the teleportation
term), so convergence is guaranteed by the Perron-Frobenius theorem.

---

## 10. Computational Complexity

| Stage         | Operation                  | Time              | Space         |
|---------------|----------------------------|-------------------|---------------|
| L1: Scan      | Parse N files, L lines avg | O(N × L)          | O(N × L)      |
| L2: Entropy   | AST node counting          | O(N × A) where A = node types | O(N × A) |
| L2: Centrality| PageRank power iteration   | O(I × E) where I = iters, E = edges | O(N + E) |
| L2: Volatility| Filesystem stat            | O(N)              | O(N)          |
| L2: Coherence | TF-IDF + cosine similarity | O(N² × V) where V = vocabulary | O(N × V) |
| L2: Load      | Arithmetic per file        | O(N)              | O(N)          |
| L3: Normalize | Z-scores or Mahalanobis    | O(N × k²) where k = 5 | O(N × k) |
| L4: Fusion    | Consistency + weighting    | O(N × k)          | O(N)          |
| L5: Report    | Rule matching              | O(N)              | O(N)          |
| **Total**     |                            | **O(N² × V + N × L)** | **O(N × V + N × L)** |

The quadratic term comes from pairwise cosine similarity in semantic coherence.
For codebases with N < 10,000 files, this completes in seconds.

---

## 11. Known Limitations and Assumptions

1. **Normality assumption**: Z-score thresholding, Grubbs' test, and the 0.6745
   MAD constant assume approximate normality. Code metrics are often right-skewed.
   The robust methods (MAD, IQR) mitigate this but do not eliminate it.

2. **Churn volatility is a weak proxy**: Without git history, volatility is just
   file recency. This cannot distinguish "one edit yesterday" from "daily edits
   for a month."

3. **Semantic coherence is token-level**: TF-IDF on import/export names is a
   bag-of-words model. It misses semantic relationships (e.g., "parseJSON" and
   "serializeJSON" are similar concepts but different tokens).

4. **Cognitive load is heuristic**: The formula `concepts × complexity × (1 +
   depth/10)` has no formal derivation. The /10 divisor is a tuning constant.

5. **Eigenvector centrality on disconnected graphs**: Power iteration may
   converge to a degenerate vector (zeros for isolated components).

6. **Covariance singularity**: When N is close to k = 5, the sample covariance
   matrix may be poorly estimated. The pseudo-inverse fallback handles
   singularity but may underestimate distances.

---

## 12. References

1. Shannon, C.E. (1948). "A Mathematical Theory of Communication." *Bell System
   Technical Journal*, 27(3), 379–423.
2. Cover, T.M. & Thomas, J.A. (2006). *Elements of Information Theory*, 2nd ed.
   Wiley.
3. Brin, S. & Page, L. (1998). "The Anatomy of a Large-Scale Hypertextual Web
   Search Engine." *Computer Networks and ISDN Systems*, 30(1–7), 107–117.
4. Langville, A.N. & Meyer, C.D. (2006). *Google's PageRank and Beyond: The
   Science of Search Engine Rankings*. Princeton University Press.
5. Brandes, U. (2001). "A Faster Algorithm for Betweenness Centrality." *Journal
   of Mathematical Sociology*, 25(2), 163–177.
6. Newman, M.E.J. (2010). *Networks: An Introduction*. Oxford University Press.
7. Mahalanobis, P.C. (1936). "On the Generalized Distance in Statistics."
   *Proceedings of the National Institute of Sciences of India*, 2(1), 49–55.
8. Grubbs, F.E. (1969). "Procedures for Detecting Outlying Observations in
   Samples." *Technometrics*, 11(1), 1–21.
9. Iglewicz, B. & Hoaglin, D.C. (1993). *Volume 16: How to Detect and Handle
   Outliers*. ASQC Quality Press.
10. Tukey, J.W. (1977). *Exploratory Data Analysis*. Addison-Wesley.
11. Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton University
    Press.
12. Bishop, C.M. (2006). *Pattern Recognition and Machine Learning*. Springer.
13. Salton, G., Wong, A. & Yang, C.S. (1975). "A Vector Space Model for
    Automatic Indexing." *Communications of the ACM*, 18(11), 613–620.
14. Sparck Jones, K. (1972). "A Statistical Interpretation of Term Specificity
    and Its Application in Retrieval." *Journal of Documentation*, 28(1), 11–21.
