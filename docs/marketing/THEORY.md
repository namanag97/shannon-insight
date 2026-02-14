# Shannon Insight: Mathematical Foundations

This document provides rigorous mathematical definitions for the techniques underlying Shannon Insight. It is intended for researchers, advanced practitioners, and contributors who want to understand the theoretical basis of each computation.

---

## Table of Contents

1. [Information Theory](#information-theory)
2. [Graph Theory](#graph-theory)
3. [Spectral Graph Theory](#spectral-graph-theory)
4. [Temporal Analysis](#temporal-analysis)
5. [Signal Fusion and Normalization](#signal-fusion-and-normalization)
6. [Statistical Methods](#statistical-methods)
7. [References](#references)

---

## Information Theory

### Shannon Entropy

**Formal definition**: For a discrete random variable X with probability mass function p(x) over a finite alphabet A:

```
H(X) = -SUM_{x in A} p(x) * log_2(p(x))
```

with the convention that 0 * log_2(0) = 0 (justified by the limit as p -> 0+).

**Properties**:
- H(X) >= 0, with equality iff X is deterministic (one outcome has probability 1).
- H(X) <= log_2(|A|), with equality iff X is uniformly distributed.
- H is concave in p.

**Intuitive explanation**: Entropy measures the average number of bits needed to encode a message from the source X. Low entropy means the source is predictable (few bits needed). High entropy means the source is surprising (many bits needed).

**Application in Shannon Insight**:

*Author entropy*: Let a_1, ..., a_k be the authors of a file, with p(a_i) = commits_by_a_i / total_commits. Then:

```
H_author = -SUM_{i=1}^{k} p(a_i) * log_2(p(a_i))
```

This measures how "spread out" the authorship is. H_author = 0 means one person wrote everything. H_author = log_2(k) means k authors contributed equally.

*Concept entropy*: Let c_1, ..., c_m be concept clusters extracted from a file, with weights w(c_j). Then:

```
H_concept = -SUM_{j=1}^{m} w(c_j) * log_2(w(c_j))
```

High concept entropy indicates the file handles many unrelated responsibilities.

### Source Coding Theorem

**Formal statement** (Shannon 1948): For a stationary ergodic source X, the minimum achievable compression rate is H(X). Any lossless code must use at least H(X) bits per symbol on average.

**Relevance**: Shannon Insight uses compression as a proxy for Kolmogorov complexity. The source coding theorem guarantees that zlib compression provides an upper bound on the true information content of a file.

### Kolmogorov Complexity and Compression

**Formal definition**: The Kolmogorov complexity K(x) of a string x is the length of the shortest program that produces x on a universal Turing machine.

K(x) is uncomputable (by reduction from the halting problem), but compression algorithms provide a computable upper bound:

```
K(x) <= C(x) + O(1)
```

where C(x) = length of x after compression and O(1) is the length of the decompressor program.

**Application**: Shannon Insight computes:

```
compression_ratio(f) = |zlib(content(f))| / |content(f)|
```

Low compression ratio indicates high redundancy (boilerplate, copy-paste patterns). The ratio is not true Kolmogorov complexity, but it is a consistent, language-agnostic proxy.

### Normalized Compression Distance (NCD)

**Formal definition** (Cilibrasi and Vitanyi 2005): For strings x and y, the Normalized Information Distance (NID) is:

```
NID(x, y) = max(K(x|y), K(y|x)) / max(K(x), K(y))
```

Since K is uncomputable, NCD approximates NID using a compressor C:

```
NCD(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
```

where C(xy) is the compressed length of the concatenation of x and y.

**Properties**:
- NCD is a metric (non-negative, symmetric, satisfies triangle inequality up to approximation error).
- NCD in [0, 1+epsilon] (for real compressors, can slightly exceed 1 due to overhead).
- NCD = 0: x and y are identical (or nearly so).
- NCD = 1: x and y share no compressible patterns.

**Application**: Clone detection. Shannon Insight uses zlib level 6 and flags file pairs with NCD < 0.3 as clones. The adaptive strategy uses direct pairwise comparison for fewer than 1000 files and MinHash+LSH pre-filtering for larger codebases.

### TF-IDF and Cosine Similarity

**Formal definition**: For a term t in document d within corpus D:

```
tf(t, d) = count(t in d) / |d|                 (term frequency)
idf(t, D) = log(|D| / |{d in D : t in d}|)    (inverse document frequency)
tfidf(t, d, D) = tf(t, d) * idf(t, D)
```

The TF-IDF vector of document d is the vector of tfidf values for all terms in the vocabulary.

**Cosine similarity** between documents d_i and d_j:

```
cos(d_i, d_j) = (v_i . v_j) / (||v_i|| * ||v_j||)
```

where v_i, v_j are TF-IDF vectors.

**Application in Shannon Insight**:

*Semantic coherence*: For a file f with functions f_1, ..., f_n, treat each function body as a "document" and compute:

```
semantic_coherence(f) = mean(cos(v_i, v_j)) for all i < j
```

High coherence means all functions share vocabulary (focused file). Low coherence means functions are about different things (god file candidate).

*Naming drift*: Compute cosine similarity between the TF-IDF vector of the filename tokens and the TF-IDF vector of the file's content tokens:

```
naming_drift(f) = 1 - cos(tfidf(filename_tokens), tfidf(content_tokens))
```

High drift means the filename is misleading.

*Concept extraction* (Tier 3): Build a TF-IDF matrix across all files, then construct a token co-occurrence graph where edges connect tokens that appear in the same function. Apply Louvain community detection to find concept clusters.

---

## Graph Theory

### Dependency Graph Model

**Formal definition**: The dependency graph is a directed graph G = (V, E) where:
- V = set of source files
- E = {(u, v) : file u imports file v}

Additional graph types (currently IMPORT only; CALL and TYPE_FLOW are planned):
- G1: Dependency (IMPORT edges)
- G4: Co-change (temporal edges)
- G5: Author (social edges)
- G6: Semantic (concept similarity edges)

### PageRank

**Formal definition** (Brin and Page 1998): For a directed graph G = (V, E), the PageRank of node v is the stationary distribution of a random walk with restart:

```
PR(v) = (1 - d) / |V| + d * SUM_{u: (u,v) in E} PR(u) / out_degree(u)
```

where d = 0.85 is the damping factor. This can be written in matrix form:

```
PR = (1 - d) / |V| * 1 + d * M^T * PR
```

where M is the column-stochastic transition matrix (M_ij = 1/out_degree(i) if (i,j) in E, else 0).

**Convergence**: Power iteration starting from PR_0 = 1/|V| converges geometrically at rate d. Shannon Insight iterates until max|PR_new - PR_old| < 1e-6 or 50 iterations.

**Intuitive explanation**: PageRank models a random surfer who follows links with probability d and jumps to a random page with probability (1-d). The stationary probability of visiting each page is its PageRank. In a dependency graph, files that are imported by many important files accumulate high PageRank.

**Why not just in-degree?** In-degree counts direct dependents. PageRank captures transitive importance. A file imported by one very important hub has high PageRank despite in_degree = 1.

### Betweenness Centrality

**Formal definition** (Freeman 1977): For a node v in graph G:

```
B(v) = SUM_{s != v != t} sigma(s,t|v) / sigma(s,t)
```

where sigma(s,t) is the number of shortest paths from s to t, and sigma(s,t|v) is the number of those paths passing through v.

**Brandes' algorithm** (2001): Computes betweenness for all nodes in O(|V| * |E|) by:
1. Running BFS from each source s to compute shortest path counts sigma and distances.
2. Accumulating "dependency scores" delta in reverse BFS order.

**Normalization**: For directed graphs, divide by (|V|-1)(|V|-2) to produce values in [0, 1].

**Intuitive explanation**: Betweenness measures how often a node appears on shortest paths between other nodes. High betweenness = structural bridge. Removing a high-betweenness node disrupts many communication paths. In code, these are files that mediate between otherwise-disconnected parts of the system.

### Strongly Connected Components (Tarjan's Algorithm)

**Formal definition**: A strongly connected component (SCC) of a directed graph is a maximal set of vertices S such that for every pair u, v in S, there exists a path from u to v and from v to u.

**Tarjan's algorithm** (1972): Linear-time algorithm using DFS with a stack. Each node gets an index (discovery order) and a lowlink (smallest index reachable from the subtree). When lowlink[v] == index[v], v is the root of an SCC.

Shannon Insight uses an iterative (non-recursive) implementation to avoid Python's recursion limit.

**Application**: cycle_count = |{S : |S| > 1}|. SCCs with more than one node represent circular dependencies.

### Community Detection (Louvain Method)

**Formal definition** (Blondel et al. 2008): The Louvain method greedily optimizes Newman-Girvan modularity:

```
Q = (1 / 2m) * SUM_{i,j} [A_ij - k_i * k_j / (2m)] * delta(c_i, c_j)
```

where m = |E|, A_ij is the adjacency matrix entry, k_i = degree of i, and delta(c_i, c_j) = 1 if nodes i and j are assigned to the same community.

**Algorithm**:
1. Each node starts in its own community.
2. For each node, compute the modularity gain of moving it to each neighbor's community.
3. Move the node to the community with maximum positive gain.
4. Repeat until no move improves modularity.
5. Contract the graph (communities become nodes).
6. Repeat from step 2 on the contracted graph.

**Modularity gain formula** (move node i to community C):

```
delta_Q = [Sigma_in + k_i_in) / 2m - ((Sigma_tot + k_i) / 2m)^2]
        - [Sigma_in / 2m - (Sigma_tot / 2m)^2 - (k_i / 2m)^2]
```

where Sigma_in = sum of edge weights inside C, Sigma_tot = sum of degrees of nodes in C, k_i_in = sum of edges from i to nodes in C.

**Note**: The squared term uses (2m)^2 = 4m^2. This is the standard formula.

**Determinism**: Shannon Insight sorts nodes before iteration to ensure reproducible community assignments.

**Interpretation**: Q > 0.3 indicates meaningful community structure. Q < 0.3 suggests weak modularization.

### Blast Radius (Transitive Reverse Closure)

**Formal definition**: For node v in directed graph G:

```
blast_radius(v) = {u in V : v is reachable from u in G}
blast_radius_size(v) = |blast_radius(v)|
```

Equivalently, BFS from v on the reversed graph.

**Intuitive explanation**: If file v changes, every file in its blast radius may need to recompile, retest, or adapt. Large blast radius means high change impact.

### DAG Depth

**Formal definition**: Given a set of entry points E (files with role=ENTRY_POINT, or in_degree=0 with out_degree>0 as fallback):

```
depth(v) = min_{e in E} shortest_path_length(e, v, G)
depth(v) = -1 if no entry point can reach v
```

Computed via multi-source BFS from all entry points simultaneously.

**Intuitive explanation**: Depth measures how "deep" a file is in the architectural layering. Depth 0 = entry point. Depth 1 = directly used by entry points. Large depth = foundational utility. Depth -1 = orphan (unreachable from any entry point).

---

## Spectral Graph Theory

### Graph Laplacian

**Formal definition**: For an undirected graph G = (V, E) with adjacency matrix A and degree matrix D:

```
L = D - A
```

The combinatorial Laplacian L is symmetric positive semi-definite.

**Properties**:
- L has n = |V| real non-negative eigenvalues: 0 = lambda_1 <= lambda_2 <= ... <= lambda_n.
- The multiplicity of eigenvalue 0 equals the number of connected components.
- For a connected graph, lambda_1 = 0 with eigenvector proportional to 1 (constant vector), and lambda_2 > 0.

**Symmetric normalized Laplacian** (alternative):

```
L_sym = D^{-1/2} L D^{-1/2} = I - D^{-1/2} A D^{-1/2}
```

Shannon Insight uses the combinatorial Laplacian for spectral analysis and the discrete Laplacian operator for the health Laplacian.

### Fiedler Value and Algebraic Connectivity

**Formal definition** (Fiedler 1973): The algebraic connectivity of a connected graph is:

```
a(G) = lambda_2(L)
```

The corresponding eigenvector v_2 (the Fiedler vector) provides the optimal 2-partition of the graph (spectral bisection).

**Properties**:
- a(G) = 0 iff the graph is disconnected.
- a(G) >= 2 * (1 - cos(pi/n)) for any graph on n vertices (lower bound from path graph).
- For a complete graph K_n: a(G) = n.
- Cheeger inequality: h(G)/2 <= a(G) <= 2*h(G), where h(G) is the edge expansion (isoperimetric number).

**Intuitive explanation**: Algebraic connectivity measures the "bottleneck" of the graph. A low Fiedler value means there exists a small set of edges whose removal would disconnect or nearly disconnect the graph. In code, this means fragile connectivity.

**Computation**: Shannon Insight uses the Lanczos algorithm (scipy.sparse.linalg.eigsh with which='SM') to compute the k smallest eigenvalues efficiently without forming the full matrix.

### Spectral Gap

**Formal definition**:

```
spectral_gap = lambda_2 / lambda_3
```

**Intuitive explanation**: A large spectral gap means the graph has a clear "best cut" into two communities. A small gap means multiple similar-quality partitions exist, indicating ambiguous community structure.

### Diffusion and the Health Laplacian

The graph Laplacian governs diffusion processes. For a scalar field h: V -> R (e.g., risk values on files):

```
(Lh)(v) = SUM_{u ~ v} [h(v) - h(u)]
```

where the sum is over neighbors u of v. This is the discrete Laplacian operator.

Shannon Insight uses a simplified form:

```
delta_h(v) = h(v) - mean(h(u) for u ~ v)
```

This measures how much a node deviates from its neighborhood average. Positive delta_h means the node is a local maximum (worse than neighbors). The interpretation is analogous to the Laplacian in physics: heat flows from hot to cold, and a local hot spot (positive Laplacian) will lose heat to its cooler neighbors.

**Mathematical connection to eigendecomposition**: If h is an eigenvector of L with eigenvalue lambda, then (Lh)(v) = lambda * h(v). Low-frequency eigenvectors (small lambda) vary smoothly across the graph. High-frequency eigenvectors (large lambda) oscillate rapidly. The health Laplacian delta_h captures local high-frequency deviation without full eigendecomposition.

---

## Temporal Analysis

### Time Series Model

For each file f and signal S, the temporal spine produces a time series:

```
{S(f, t_0), S(f, t_1), ..., S(f, t_n)}
```

where t_i are time points derived from git history (commit timestamps, bucketed into 4-week windows).

### Linear Regression (Velocity)

**Formal definition**: Fit S(t) = a + b*t via ordinary least squares:

```
b = (n * SUM(t_i * S_i) - SUM(t_i) * SUM(S_i)) / (n * SUM(t_i^2) - (SUM(t_i))^2)
```

The slope b is the "velocity" of the signal.

**Interpretation**: b > 0 means the signal is increasing (e.g., file is getting more complex over time). b < 0 means decreasing (e.g., file is stabilizing).

### Coefficient of Variation (Volatility)

**Formal definition**: For a time series {x_1, ..., x_n} with mean mu and standard deviation sigma:

```
CV = sigma / mu
```

**Properties**:
- CV is dimensionless (unit-free).
- CV = 0 means constant time series.
- CV > 1 means the standard deviation exceeds the mean (high variability).

**Application**: churn_cv measures the erraticism of a file's change rate. Trajectory classification uses CV thresholds:
- CV < 0.5 combined with negative velocity: STABILIZING
- CV > 0.5 combined with positive velocity: SPIKING
- CV > 0.5 without strong velocity: CHURNING

### Trajectory Classification

The trajectory classifier combines velocity and volatility into qualitative categories:

```
classify(total_changes, velocity, cv):
    if total_changes <= 1:          return DORMANT
    if velocity < -eps and cv < 0.5: return STABILIZING
    if velocity > eps and cv > 0.5:  return SPIKING
    if cv > 0.5:                     return CHURNING
    else:                            return STABLE
```

where eps is a velocity threshold.

This is a deterministic decision boundary in the (velocity, CV) space.

### Co-change Analysis (Temporal Association)

**Formal definition**: For files A and B across N commits:

```
support(A) = |{c : A in c}| / N          (frequency of A)
support(B) = |{c : B in c}| / N          (frequency of B)
support(A, B) = |{c : A in c and B in c}| / N  (co-frequency)

confidence(A -> B) = support(A, B) / support(A)
lift(A, B) = support(A, B) / (support(A) * support(B))
```

**Interpretation**:
- Lift = 1: A and B are independent (co-change at the expected rate).
- Lift > 1: Positive association (co-change more than expected).
- Lift >> 2 with no structural edge: HIDDEN_COUPLING.
- Lift near 0 despite structural edge: DEAD_DEPENDENCY (if both have significant history).

This is the same association rule mining framework used in market basket analysis, applied to commit baskets.

### Author Distance (G5 Space)

**Formal definition**: For files A and B with author weight distributions w_A and w_B:

```
d_5(A, B) = 1 - SUM_a min(w_a(A), w_a(B)) / SUM_a max(w_a(A), w_a(B))
```

where w_a(f) = commits_by_author_a_on_f / total_commits_on_f.

This is 1 minus the weighted Jaccard similarity of author distributions.

**Properties**:
- d_5 = 0: Identical author distributions.
- d_5 = 1: Completely different authors.
- d_5 is symmetric and satisfies the triangle inequality.

---

## Signal Fusion and Normalization

### Percentile Normalization

**Formal definition**: For signal S and file f:

```
pctl(S, f) = |{v in all_files : S(v) <= S(f)}| / |all_files|
```

This maps any signal to a [0, 1] scale based on rank order.

**Properties**:
- Distribution-free: works regardless of the underlying signal distribution.
- Robust to outliers: a single extreme value does not distort the scale.
- Percentiles are not meaningful for small samples (resolved via tiered normalization).

### Bayesian Percentile (Small Sample Regularization)

**Formal definition**: For a file at rank r among n files, with Beta prior (alpha, beta):

```
posterior_pctl(r, n) = (alpha + r) / (alpha + beta + n)
```

This is the posterior mean of a Beta(alpha + r, beta + n - r) distribution.

**Properties**:
- With flat prior (alpha = beta = 1): posterior pulls extreme values toward 0.5.
- For the highest-ranked file (r = n): posterior = (1 + n) / (2 + n), which is less than 1.
- As n -> infinity: posterior -> r/n (standard percentile).

**Intuition**: In a small codebase, the "worst" file might not be truly extreme -- it is just the worst among a small sample. Bayesian regularization hedges against overconfidence in small samples.

### Composite Score Formulas

All composites are weighted sums of normalized signals. The general form:

```
composite(f) = SUM_i w_i * transformed_signal_i(f)
```

where SUM w_i = 1 and transformed_signal is either pctl(S, f), 1-pctl(S, f), S(f) directly, or another transformation.

**Weight sum verification** (all composite weights sum to 1.0):

| Composite | Weights | Sum |
|-----------|---------|-----|
| risk_score | 0.25 + 0.20 + 0.20 + 0.20 + 0.15 | 1.00 |
| wiring_quality | 0.30 + 0.25 + 0.25 + 0.20 | 1.00 |
| health_score | 0.20 + 0.15 + 0.20 + 0.15 + 0.15 + 0.15 | 1.00 |
| wiring_score | 0.25 + 0.25 + 0.20 + 0.15 + 0.15 | 1.00 |
| architecture_health | 0.25 + 0.20 + 0.20 + 0.20 + 0.15 | 1.00 |
| codebase_health | 0.30 + 0.30 + 0.20 + 0.20 | 1.00 |
| team_risk | 0.30 + 0.25 + 0.25 + 0.20 | 1.00 |

### Health Laplacian

The health Laplacian applies the discrete Laplacian operator to the raw_risk scalar field:

```
raw_risk(f) = 0.25 * pagerank(f)/max_pagerank
            + 0.20 * blast_radius_size(f)/max_blast
            + 0.20 * cognitive_load(f)/max_cognitive
            + 0.20 * instability_factor(f)
            + 0.15 * (1 - bus_factor(f)/max_bus_factor)

delta_h(f) = raw_risk(f) - mean(raw_risk(n) for n in neighbors(f))
```

**Why raw values, not percentiles**: Percentile normalization produces a near-uniform distribution where every file has approximately the same value. The Laplacian of a constant field is zero everywhere -- making it useless. Raw values preserve the natural variation needed for meaningful local comparisons.

**Division-by-zero guards**: If max_pagerank, max_blast, or max_cognitive is 0, the corresponding term contributes 0 (not NaN). In practice, PageRank is always positive due to the damping factor; bus_factor is always >= 1; blast and cognitive can be 0 for disconnected or empty files.

---

## Statistical Methods

### Gini Coefficient

**Formal definition**: For values x_1 <= x_2 <= ... <= x_n (sorted ascending):

```
G = (2 * SUM_{i=1}^{n} i * x_i) / (n * SUM_{i=1}^{n} x_i) - (n + 1) / n
```

**Equivalent definitions**:
- Relative mean absolute difference: G = SUM_{i,j} |x_i - x_j| / (2 * n * SUM x_i)
- Area between Lorenz curve and equality line: G = 2 * integral(y - L(y), 0, 1) where L is the Lorenz curve

**Properties**:
- G in [0, 1] (for non-negative values).
- G = 0: Perfect equality (all values identical).
- G = 1: Maximum inequality (one value holds everything, rest are zero).

**Verification**: For values [1, 1, 1, 1] (equal):
```
G = (2 * (1*1 + 2*1 + 3*1 + 4*1)) / (4 * 4) - 5/4
  = (2 * 10) / 16 - 1.25
  = 1.25 - 1.25
  = 0.0
```

For values [0, 0, 0, 4] (maximum inequality, n=4):
```
G = (2 * (1*0 + 2*0 + 3*0 + 4*4)) / (4 * 4) - 5/4
  = (2 * 16) / 16 - 1.25
  = 2.0 - 1.25
  = 0.75
```

Note: With n=4, the maximum Gini is 0.75 (not 1.0), because (n-1)/n = 3/4. G = 1 only in the continuous limit.

### Martin's Distance from Main Sequence

**Formal definition** (Robert C. Martin 1994): For a module M:

```
Ca = afferent coupling (number of external classes that depend on classes in M)
Ce = efferent coupling (number of external classes that classes in M depend on)

I = Ce / (Ca + Ce)         (Instability, [0, 1])
A = abstract / total       (Abstractness, [0, 1])

D = |A + I - 1|            (Distance from main sequence, [0, 1])
```

The "main sequence" is the line A + I = 1 in the (A, I) plane. Modules near this line balance abstractness and stability.

**Zones**:
- A < 0.3 AND I < 0.3: Zone of Pain. Concrete and stable. Many dependents, hard to change.
- A > 0.7 AND I > 0.7: Zone of Uselessness. Abstract and unstable. Over-engineered, potentially unused.

**Edge case**: I = None if Ca + Ce = 0 (isolated module with no cross-module dependencies). In this case, D is undefined and Shannon Insight sets main_seq_distance = 0.0.

### Confidence Scoring (Margin Formula)

**Formal definition**: For a finding with triggered conditions {(signal_i, value_i, threshold_i, polarity_i)}:

```
For each condition:
  if polarity = "high_is_bad":
    margin_i = (value_i - threshold_i) / (1.0 - threshold_i)
  if polarity = "high_is_good":
    margin_i = (threshold_i - value_i) / threshold_i

  margin_i = clamp(margin_i, 0, 1)

confidence = mean(margin_1, ..., margin_k)
```

**Intuitive explanation**: The margin measures how far beyond the threshold the actual value falls, normalized to the available range. A value just barely above the threshold gives margin near 0. A value at the extreme gives margin near 1.

**Example**: For HIGH_RISK_HUB with pctl(pagerank) = 0.95, threshold = 0.90:
```
margin = (0.95 - 0.90) / (1.0 - 0.90) = 0.05 / 0.10 = 0.50
```

### Correlation and Redundancy Detection

**Formal definition**: Pearson correlation between signals S_i and S_j:

```
r(S_i, S_j) = Cov(S_i, S_j) / (sigma_i * sigma_j)
```

Computed across all files for each pair of numeric per-file signals.

**Application**: If |r| > 0.8, the signals carry redundant information. Shannon Insight halves the weight of the subordinate signal in composite computation and logs a warning.

**PCA validation** (optional): Standardize all signals, compute eigenvalue spectrum. The effective dimensionality k (where the first k principal components explain 90% of variance) reveals whether the 8 declared dimensions are genuinely independent or collapse into fewer latent factors.

---

## References

1. Shannon, C.E. (1948). "A Mathematical Theory of Communication." *Bell System Technical Journal*, 27(3), 379-423.

2. Cilibrasi, R. and Vitanyi, P. (2005). "Clustering by Compression." *IEEE Transactions on Information Theory*, 51(4), 1523-1545.

3. Brin, S. and Page, L. (1998). "The Anatomy of a Large-Scale Hypertextual Web Search Engine." *Computer Networks*, 30(1-7), 107-117.

4. Freeman, L.C. (1977). "A Set of Measures of Centrality Based on Betweenness." *Sociometry*, 40(1), 35-41.

5. Brandes, U. (2001). "A Faster Algorithm for Betweenness Centrality." *Journal of Mathematical Sociology*, 25(2), 163-177.

6. Tarjan, R.E. (1972). "Depth-First Search and Linear Graph Algorithms." *SIAM Journal on Computing*, 1(2), 146-160.

7. Blondel, V.D., Guillaume, J.L., Lambiotte, R., and Lefebvre, E. (2008). "Fast Unfolding of Communities in Large Networks." *Journal of Statistical Mechanics*, P10008.

8. Fiedler, M. (1973). "Algebraic Connectivity of Graphs." *Czechoslovak Mathematical Journal*, 23(2), 298-305.

9. Martin, R.C. (1994). "OO Design Quality Metrics." In *Object Mentor*.

10. McCabe, T.J. (1976). "A Complexity Measure." *IEEE Transactions on Software Engineering*, SE-2(4), 308-320.

11. Tornhill, A. (2015). *Your Code as a Crime Scene: Use Forensic Techniques to Arrest Defects, Bottlenecks, and Bad Design in Your Programs.* Pragmatic Bookshelf.

12. Gini, C. (1912). "Variabilita e mutabilita." *Reprinted in Memorie di metodologica statistica*.
