# Shannon Insight — Mathematical Foundations

## Overview

This document specifies the mathematics at three levels:

1. **Per-dimension** — each of the 8 dimensions is a distinct mathematical object
2. **Per-IR transition** — each IR→IR transform uses specific mathematical operations
3. **On the tensor** — operations on the full 8×7×T measurement tensor

---

## Part I: Mathematics of Each Dimension

### D1: SIZE — Counting and Distribution Theory

Size measurements are **positive integers** at every scale. The math is about distribution, not the values themselves.

**Within a file** — function size distribution:

Let `s₁, s₂, ..., sₖ` be body token counts for k functions in a file.

```
Mean function size:     μ = (1/k) Σ sᵢ
Variance:               σ² = (1/k) Σ (sᵢ - μ)²
Coefficient of var:     CV = σ / μ

Gini coefficient:       G = (Σᵢ Σⱼ |sᵢ - sⱼ|) / (2k² μ)
```

The **Gini** is the key metric. It measures inequality of implementation:

- G ≈ 0: all functions similar size (uniform, healthy)
- G = 0.3–0.5: natural variation (normal codebase)
- G > 0.6: extreme inequality (some functions huge, others empty — AI stub signature)

**Percentile function** for any size metric across the codebase:

```
percentile(x, values) = |{v ∈ values : v ≤ x}| / |values|
```

Percentiles are scale-free — they let us compare files regardless of codebase size or language norms.

**Growth modeling** across time:

```
file_count(t) modeled as:
  Linear:       f(t) = a + bt                (healthy, steady growth)
  Exponential:  f(t) = a × e^(bt)            (bloating)
  Logistic:     f(t) = K / (1 + e^(-b(t-t₀))) (saturating — mature project)

Fit via least squares, select model by AIC/BIC.
```

**Zipf's law test** — in natural codebases, file sizes follow a power law:

```
P(size > s) ∝ s^(-α)
```

If the codebase deviates from Zipf (e.g., all files suspiciously same size), it's a signal of artificial generation.

```
zipf_deviation = KL_divergence(actual_size_distribution || fitted_power_law)
```

---

### D2: SHAPE — Tree Metrics and Graph Geometry

Shape is about **structure**, not content. The mathematical objects are trees (AST, class hierarchy) and distributions of structural properties.

**Cyclomatic complexity** (per function):

```
M = E - N + 2P

where E = edges in control flow graph
      N = nodes in control flow graph
      P = connected components (usually 1)
```

Approximation without building CFG:
```
M ≈ 1 + |if| + |elif| + |for| + |while| + |except| + |and| + |or| + |case|
```

**Nesting depth distribution** (per file):

Let `nᵢ` = max nesting depth of function i. The distribution of {nᵢ} characterizes the file's shape.

```
Max nesting:            max(nᵢ)
Mean nesting:           μ_n = (1/k) Σ nᵢ
Nesting entropy:        H_n = -Σ p(d) log₂ p(d)    where p(d) = fraction of functions at depth d
```

High nesting entropy = functions at many different depths = inconsistent structure.

**Inheritance depth** (per class hierarchy):

```
DIT(class) = length of longest path from class to root of inheritance tree
```

**Method size distribution within a class** — same Gini analysis as file-level function sizes:

```
G_class = gini([method_size for method in class.methods])
```

**Structural symmetry** — do similar components have similar shapes?

For each pair of files in a module:
```
shape_similarity(A, B) = 1 - |fn_count(A) - fn_count(B)| / max(fn_count(A), fn_count(B))
                       × 1 - |max_nesting(A) - max_nesting(B)| / max(max_nesting(A), max_nesting(B))
                       × 1 - |class_count(A) - class_count(B)| / max(class_count(A), class_count(B))
```

High mean shape_similarity within a module = consistent patterns (healthy). Low = chaotic.

**Architectural shape** (codebase level):

Classify the dependency graph's shape:

```
Layered:      ∃ topological ordering with few back-edges
              Test: back_edge_ratio = |back_edges| / |total_edges| < 0.1

Hub-and-spoke: ∃ node v where degree(v) > 0.3 × |E|
               AND removing v disconnects > 50% of the graph

Modular:      modularity Q > 0.3 (from Louvain)
              AND mean(cohesion) > 0.5
              AND mean(coupling) < 0.3

Flat:         max(DAG_depth) ≤ 2
              AND |internal_nodes| / |total_nodes| < 0.2

Monolith:     largest_connected_component > 0.9 × |V|
              AND modularity Q < 0.2
```

---

### D3: NAMING — Information Theory on Natural Language Embedded in Code

Identifiers are the intersection of natural language and code. The math draws from NLP and information theory.

**Token extraction and normalization:**

```
split("getUserProfile") → ["get", "user", "profile"]
split("get_user_profile") → ["get", "user", "profile"]
split("HTTPSConnection") → ["https", "connection"]

Normalize: lowercase, stem optional (Porter stemmer), remove stopwords (the, a, is)
```

**TF-IDF per file:**

```
tf(token, file) = count(token in file) / total_tokens(file)

idf(token) = log(|files| / |{f : token ∈ f}|)

tfidf(token, file) = tf(token, file) × idf(token)
```

This gives each file a **vector in R^V** where V = vocabulary size. These vectors live in a high-dimensional space where distance = semantic dissimilarity.

**Concept extraction via token co-occurrence:**

Build a within-file co-occurrence graph:

```
For each file:
  nodes = unique tokens
  edge(tᵢ, tⱼ) exists if tᵢ and tⱼ appear in the same function
  weight(tᵢ, tⱼ) = number of functions where both appear

Apply Louvain community detection → each community = a concept
```

**Concept weight:**
```
w(concept_c) = |{tokens in concept_c}| / |{all tokens in file}|
```

**Concept entropy** (per file):
```
H_concepts = -Σ w(c) × log₂(w(c))
```

- H = 0: single concept (perfectly focused file)
- H = 1: two equal concepts (dual-purpose file)
- H > 2: many concepts (god file candidate)

**Naming drift** (filename vs content):

```
filename_vector = tfidf_vector(split(filename_stem))
content_vector  = Σ w(c) × centroid(tfidf vectors of tokens in concept c)

drift = 1 - cosine(filename_vector, content_vector)

where cosine(u, v) = (u · v) / (‖u‖ × ‖v‖)
```

**Vocabulary richness** (Yule's K):

```
For a file with N total identifier tokens and fᵢ = frequency of i-th unique token:

M₁ = N (total tokens)
M₂ = Σ i² × fᵢ (sum of squared frequencies × rank)

K = 10⁴ × (M₂ - M₁) / M₁²
```

Low K = rich vocabulary = many distinct concepts. High K = repetitive vocabulary = focused or formulaic.

**Cross-file semantic similarity:**

```
sim(A, B) = cosine(tfidf_vector(A), tfidf_vector(B))
```

This defines the semantic distance space (G6). Unlike NCD which measures information-theoretic similarity of raw bytes, this measures similarity of *meaning* as captured by identifier choice.

---

### D4: REFERENCE — Graph Theory and Spectral Methods

Reference is the richest mathematical dimension. It spans all of graph theory.

**Graph representation:**

```
G = (V, E, w, τ)

V = files (or functions for call graph)
E ⊆ V × V = directed edges
w: E → ℕ = weight (number of symbols crossing the edge)
τ: E → {IMPORT, CALL, TYPE, DATA} = edge type
```

**Centrality measures:**

PageRank (eigenvector centrality variant):
```
PR(v) = (1-d)/|V| + d × Σ_{u→v} PR(u) / out_degree(u)

d = 0.85 (damping factor)
Iterate until convergence: max(|PR_new - PR_old|) < ε = 10⁻⁶
Typically converges in 20-50 iterations.
```

In matrix form:
```
Let M be the column-stochastic adjacency matrix: M[i,j] = 1/out_degree(j) if j→i, else 0
Let e = [1/|V|, ..., 1/|V|]ᵀ

PR = (1-d) × e + d × M × PR    (fixed point equation)
```

PageRank is the stationary distribution of a random walk on the dependency graph. It answers: "if I follow random imports, where do I end up?" High PR = structural hub.

Betweenness centrality:
```
B(v) = Σ_{s≠v≠t} σ(s,t|v) / σ(s,t)

where σ(s,t) = number of shortest paths from s to t
      σ(s,t|v) = number of those paths passing through v

Computed via Brandes' algorithm: O(|V| × |E|)
```

B(v) answers: "how much of the communication flow passes through v?" High betweenness = bridge node, removing it disconnects communities.

**Strongly connected components (Tarjan's algorithm):**

```
Iterative DFS with a stack. Identifies maximal subgraphs where every node is reachable from every other.

SCC with |nodes| > 1 = circular dependency cycle.

Cycle density = Σ |edges within SCCs| / |E|
```

**Blast radius (transitive reverse closure):**

```
blast(v) = BFS(v, reverse(G))
blast_size(v) = |blast(v)| - 1

Interpretation: if v breaks, blast_size(v) files are potentially affected.
```

**DAG depth (longest path from entry points):**

```
For each entry point e, BFS forward:
  depth(e) = 0
  depth(v) = max(depth(u) + 1) for all u→v

file_depth(v) = min(depth(v) from each reachable entry point)
```

If file_depth(v) = ∞ (unreachable from any entry point), v is an orphan.

**Spectral graph theory:**

The graph Laplacian:
```
L = D - A

where D = diagonal degree matrix: D[i,i] = degree(i)
      A = adjacency matrix (undirected version)
```

Properties of L:
- L is positive semi-definite → all eigenvalues λᵢ ≥ 0
- λ₁ = 0 always (eigenvector = constant vector)
- Number of zero eigenvalues = number of connected components
- **λ₂ = Fiedler value = algebraic connectivity**

```
Eigendecomposition: L = U Λ Uᵀ

λ₁ = 0 ≤ λ₂ ≤ λ₃ ≤ ... ≤ λₙ

Fiedler value = λ₂
Fiedler vector = u₂ (eigenvector for λ₂)
```

**What the eigenvalues tell us:**

```
λ₂ (Fiedler value):
  - λ₂ = 0: graph is disconnected
  - λ₂ small: graph has a bottleneck (almost disconnectable)
  - λ₂ large: graph is well-connected, robust

λ₂/λ₃ (spectral gap):
  - Large gap: graph has a clear "best cut" into two communities
  - Small gap: multiple nearly-equivalent cuts exist

The Fiedler vector u₂ defines a spectral bipartition:
  Partition A = {v : u₂(v) < 0}
  Partition B = {v : u₂(v) ≥ 0}
  This is the min-cut approximation (Cheeger inequality).
```

**Cheeger inequality** (relates spectral gap to graph expansion):

```
h(G)² / 2 ≤ λ₂ ≤ 2h(G)

where h(G) = min over all cuts S: |edges(S, V\S)| / min(|S|, |V\S|)
```

This means: λ₂ is a proxy for how hard it is to break the graph into disconnected components. Higher = more resilient architecture.

**Normalized Laplacian** (better for graphs with varying degree):

```
L_norm = D^(-1/2) L D^(-1/2) = I - D^(-1/2) A D^(-1/2)

Eigenvalues of L_norm ∈ [0, 2]
λ₂(L_norm) is the normalized algebraic connectivity.
```

**Community detection — Louvain algorithm:**

Modularity:
```
Q = (1/2m) Σ_{ij} [A_{ij} - kᵢkⱼ/(2m)] δ(cᵢ, cⱼ)

where m = |E|
      kᵢ = degree of node i
      cᵢ = community of node i
      δ(cᵢ, cⱼ) = 1 if same community

Q ∈ [-0.5, 1]. Typical good values: Q > 0.3
```

Louvain greedily maximizes Q:
1. Start with each node in its own community
2. For each node, compute ΔQ of moving it to each neighbor's community
3. Move to community giving largest positive ΔQ
4. Repeat until no move improves Q
5. Contract communities into super-nodes, repeat from step 1

**Multi-graph centrality** (NEW):

When we have multiple edge types (import, call, type), we can compute centrality on the combined graph:

```
A_combined = α₁A_import + α₂A_call + α₃A_type

where αᵢ = weight for edge type i
Default: α = [0.5, 0.3, 0.2] (imports most important, then calls, then types)

PR_combined = PageRank(A_combined)
```

Or compute separate PageRank on each graph and fuse:
```
PR_fused(v) = Σᵢ αᵢ × PR_i(v) / Σᵢ αᵢ
```

The first approach captures cross-graph effects (a file that's imported AND called is more central than one that's only imported). The second is simpler and more interpretable.

---

### D5: INFORMATION — Information Theory and Kolmogorov Complexity

This is the most mathematically fundamental dimension. Shannon Insight is named after this.

**Shannon entropy** (byte-level):

```
H(X) = -Σ p(x) log₂ p(x)

where p(x) = frequency of byte value x in the file
      x ∈ {0, 1, ..., 255}

H ∈ [0, 8] bits per byte.
```

- H < 3: highly structured (mostly whitespace, repetitive)
- H ≈ 4-5: typical source code
- H > 6: compressed data, binary, or obfuscated code

**Token-level entropy** (more meaningful for code):

```
H_token = -Σ p(t) log₂ p(t)

where p(t) = frequency of token t / total tokens
      tokens = identifiers + keywords + operators
```

This is more informative than byte entropy because it measures the diversity of *programming constructs* rather than raw characters.

**Kolmogorov complexity approximation** (compression ratio):

```
K(x) ≈ C(x) = len(zlib.compress(x))

compression_ratio = C(x) / len(x)
```

- ratio < 0.15: highly repetitive (copy-paste, boilerplate)
- ratio 0.3-0.6: normal complexity
- ratio > 0.7: very dense (minified, obfuscated, or genuinely complex)

**Why compression approximates Kolmogorov complexity:**

Kolmogorov complexity K(x) = length of shortest program that outputs x. This is uncomputable (halting problem), but compression algorithms give an upper bound: `K(x) ≤ C(x) + O(1)`. The better the compressor, the tighter the bound. zlib is fast and practical.

**Normalized Compression Distance (NCD) — the universal similarity metric:**

```
NCD(x, y) = (C(x·y) - min(C(x), C(y))) / max(C(x), C(y))
```

Where `x·y` = concatenation of file contents.

Mathematical properties:
- NCD ∈ [0, 1+ε] (approximately)
- NCD is a metric (satisfies triangle inequality approximately)
- NCD is **universal**: it captures ALL computable similarities. If two files are similar in ANY computable sense, NCD will be low.
- NCD does not depend on language, encoding, or format

This is the deepest result we use: NCD is the computable approximation to the **normalized information distance**, which is the optimal similarity metric in an information-theoretic sense.

**Conditional entropy** (what A tells you about B):

```
H(B|A) = H(A·B) - H(A)

≈ C(A·B) - C(A)    (compression approximation)
```

If H(B|A) << H(B): knowing A tells you a lot about B → strong information relationship.
If H(B|A) ≈ H(B): A tells you nothing about B → independent.

This is an alternative to NCD for measuring file relationships.

**Mutual information** (shared information between files):

```
I(A; B) = H(A) + H(B) - H(A, B)

≈ C(A) + C(B) - C(A·B)
```

I(A; B) > 0 means they share information (similar code, shared patterns, copy-paste).
I(A; B) ≈ 0 means they're informationally independent.

**Semantic coherence** (within-file concept focus):

```
Extract identifier tokens, build TF vector, compute within-file clustering.

coherence = max_cluster_weight
          = |tokens in largest concept| / |all tokens|
```

Alternatively, coherence as cosine self-similarity:

```
Split file into function-level TF-IDF vectors: v₁, v₂, ..., vₖ

coherence = mean(cosine(vᵢ, vⱼ)) for all pairs i < j
```

High coherence = all functions in the file use similar vocabulary = single responsibility.
Low coherence = functions use different vocabularies = mixed concerns.

**Cognitive load** — Gini-enhanced complexity:

```
cognitive_load(file) = (concepts × complexity × nesting_factor) × (1 + G)

where:
  concepts = function_count + class_count
  complexity = mean cyclomatic complexity
  nesting_factor = e^(max_nesting / 5)   # exponential penalty for deep nesting
  G = gini(function_sizes)                # inequality amplifier
```

The `(1 + G)` term means: uneven function sizes make a file HARDER to understand, even if total complexity is the same. A file with 10 equally-complex functions is easier than one with 1 huge function and 9 tiny ones.

**Per-function information density:**

```
density(fn) = H_token(fn.body) × len(fn.body) / fn.body_tokens

           = total information content / token count
           = bits per token
```

Stubs: density ≈ 0 (pass, return None have near-zero information)
Real logic: density > 2 bits/token
Dense algorithms: density > 4 bits/token

---

### D6: CHANGE — Time Series Analysis

Change is measured as a time series. Each file's edit history is a signal over time.

**Churn time series:**

Partition time into windows of width w (default: 4 weeks):
```
churn(file, t) = |{commits in window t that touch file}|
```

This gives a time series `c₁, c₂, ..., cₜ` per file.

**Linear trend:**

```
Fit c(t) = a + bt via ordinary least squares:

b = (T Σtcₜ - ΣtΣcₜ) / (T Σt² - (Σt)²)
a = (Σcₜ - b Σt) / T
```

b > 0: increasing activity (spiking)
b < 0: decreasing activity (stabilizing)
b ≈ 0: flat (dormant or steady)

**Coefficient of variation:**

```
CV = σ(cₜ) / μ(cₜ)
```

CV > 1: highly erratic (bursts of activity then silence)
CV < 0.5: relatively steady

**Trajectory classification:**

```
if Σcₜ ≤ 1:                         DORMANT
elif b < -threshold AND CV < 1:       STABILIZING
elif b > threshold AND CV > 0.5:      SPIKING
elif CV > 0.5:                        CHURNING
else:                                 STABLE
```

**Change point detection** (PELT algorithm):

Find points in the time series where the statistical properties change:

```
Minimize: Σ_{segments} [cost(segment) + β]

where cost(segment) = -2 × log_likelihood(segment under Gaussian model)
      β = penalty for adding a change point (BIC: β = log(T))
```

Change points in a file's churn series indicate: "something happened here" — maybe a refactor, a new feature, a new maintainer.

**Survival analysis** — time to stabilize:

```
For each file, define "stabilized" as: churn_rate drops below median AND stays below for 3+ windows.

S(t) = P(not yet stabilized at time t after creation)

Fit Kaplan-Meier survival curve. Median survival time = typical time-to-stabilize.
```

Files that never stabilize (still changing after 6+ months) are chronic problems.

**Autocorrelation** (periodicity detection):

```
r(lag) = Corr(cₜ, cₜ₊ₗₐ₍ᵍ)

If r(lag = 2 weeks) is high: file has a fortnightly release cycle rhythm.
If r(lag = 1 quarter) is high: file has seasonal activity.
```

---

### D7: AUTHORSHIP — Entropy and Concentration on Discrete Distributions

Authorship is a distribution over a discrete set (authors). The math is about concentration, diversity, and overlap.

**Author entropy per file:**

```
Let n(a, f) = commits by author a on file f
    N(f) = total commits on file f
    p(a|f) = n(a, f) / N(f)

H(f) = -Σ_a p(a|f) × log₂ p(a|f)
```

H = 0: single author (bus factor crisis)
H = log₂(k): k authors with equal contributions

**Effective author count (bus factor):**

```
bus_factor(f) = 2^(H(f))
```

This is the "equivalent number of equally-contributing authors." It smoothly interpolates between extremes:
- 1 author with 100%: 2⁰ = 1
- 2 authors with 50/50: 2¹ = 2
- 1 author with 90%, 1 with 10%: 2^0.47 ≈ 1.4 (effectively 1.4 authors — the second barely counts)

**Knowledge Gini per module:**

```
contributions = [total_commits_by_author_a_in_module for each author a]
G = gini(contributions)
```

G > 0.7: one person dominates the module (knowledge silo)
G < 0.3: contributions well-distributed

**Author overlap between files** (Jaccard):

```
J(A, B) = |authors(A) ∩ authors(B)| / |authors(A) ∪ authors(B)|
```

This defines the social distance space (G5).

**Weighted author overlap** (accounts for contribution levels):

```
For each author a, let wₐ(f) = commits by a on file f / total commits on f

J_weighted(A, B) = Σ_a min(wₐ(A), wₐ(B)) / Σ_a max(wₐ(A), wₐ(B))
```

This distinguishes "both files have a drive-by commit from author X" (low weighted overlap) from "author X is the primary maintainer of both" (high weighted overlap).

**Conway's Law correlation:**

```
For each pair of modules (M₁, M₂):

  social_distance(M₁, M₂) = 1 - J_weighted(authors(M₁), authors(M₂))
  structural_coupling(M₁, M₂) = |edges between M₁ and M₂| / max_possible_edges

conway_correlation = pearson_correlation(
  [social_distance(i,j) for all module pairs],
  [1 - structural_coupling(i,j) for all module pairs]
)
```

conway_correlation > 0.5: architecture matches team structure (Conway holds — natural)
conway_correlation < 0: teams are coupled but code is separate (friction) or vice versa

**Author turnover rate:**

```
For each time window t:
  new_authors(t) = |authors_in_t \ authors_in_(t-1)|
  departed_authors(t) = |authors_in_(t-1) \ authors_in_t|

  turnover(t) = (new + departed) / (2 × |active_authors_in_t|)
```

High turnover on a high-centrality module = knowledge drainage risk.

---

### D8: INTENT — Classification and Proportional Analysis

Intent is derived from commit messages and diff characteristics. The math is simpler but the signal is unique.

**Commit classification** (keyword + pattern matching):

```
categories = {
  FIX:       {"fix", "bug", "patch", "hotfix", "resolve", "repair", "issue"},
  FEATURE:   {"add", "feat", "implement", "new", "introduce", "create"},
  REFACTOR:  {"refactor", "restructure", "reorganize", "clean", "simplify", "rename", "move"},
  TEST:      {"test", "spec", "coverage", "assert"},
  DOCS:      {"doc", "readme", "comment", "typo"},
  DEPS:      {"upgrade", "bump", "dependency", "update.*version"},
  CHORE:     {"chore", "ci", "build", "config"}
}

classify(message) = argmax_cat |{kw ∈ categories[cat] : kw ∈ message.lower()}|
```

**Enhanced classification using diff shape:**

```
if mostly additions, few deletions:        likely FEATURE
if balanced additions/deletions:           likely REFACTOR
if few additions, mostly to test files:    likely TEST
if touches only dependency files:          likely DEPS
```

Combine message keywords + diff shape for higher accuracy.

**Fix ratio per file:**

```
fix_ratio(f) = |{commits on f classified as FIX}| / |{all commits on f}|
```

fix_ratio > 0.4: file attracts bugs — 40%+ of all changes are fixes
fix_ratio < 0.1: file is stable, changes are features/refactors

**Intent entropy per file:**

```
p(cat|f) = |{commits on f with category cat}| / |{all commits on f}|
H_intent(f) = -Σ_cat p(cat|f) × log₂ p(cat|f))
```

Low intent entropy: file has a clear purpose (all features, or all fixes)
High intent entropy: file gets everything (features, fixes, refactors, tests) — possible god file

**Refactor-to-fix ratio** (per module, over time):

```
RFR(module, t) = refactor_commits(t) / (fix_commits(t) + 1)
```

RFR > 1: proactive maintenance (more refactoring than fixing)
RFR < 0.5: reactive maintenance (mostly firefighting)

Trend of RFR over time indicates whether the team is getting ahead of or falling behind on debt.

---

## Part II: Mathematics of IR Transitions

### IR0 → IR1: Parsing Transform

**Mathematical nature**: Deterministic transformation (bijection for well-formed code).

Source code → AST → simplified structural representation.

The key math is not in parsing itself but in **what we extract from the AST**:

```
For each function f in AST:
  body_tokens(f) = count(tokens in f.body)
  signature_tokens(f) = count(tokens in f.signature)
  calls(f) = {node.func.id for node in ast.walk(f) if isinstance(node, ast.Call)}
  nesting(f) = max_depth(f, counting If/For/While/Try/With)
```

**Import resolution** — graph edge construction:

```
resolve(import_statement, project_files) → Optional[file_path]

For relative imports: navigate from current file's directory
For absolute imports: search project source roots
For external imports: check against known package list

Success → graph edge
Failure → phantom (unresolved edge)
```

### IR1 → IR2: Semantic Classification

**Mathematical nature**: Lossy dimensionality reduction. Many syntactic forms map to the same semantic role.

**Role classification** — decision tree:

This is a deterministic classifier. No probabilistic math needed. The tree structure is:

```
                    is_test_file?
                   /              \
                 YES               NO
                 TEST         is_entry_point?
                              /              \
                            YES               NO
                         ENTRY_POINT    has_abstract_methods?
                                        /                   \
                                      YES                    NO
                                   INTERFACE           has_classes_with_fields > methods?
                                                      /                               \
                                                    YES                                NO
                                                   MODEL                         ... (continue)
```

**Concept extraction** — Louvain on token co-occurrence:

Step 1: Build co-occurrence matrix:
```
C[tᵢ, tⱼ] = |{functions where both tᵢ and tⱼ appear as identifiers}|
```

Step 2: Apply Louvain (modularity maximization) on graph with adjacency matrix C.

Step 3: Each community = a concept. Topic name = token with highest TF-IDF in that community.

**Public API detection:**

```
public(symbol) = NOT symbol.name.startswith("_")
               AND symbol appears at module level (not nested)
               AND (is_function OR is_class OR is_constant)
```

**Stub detection** (from IR1 function data):

```
stub_score(f) = {
  1.0   if body matches /^(pass|\.\.\.|\s*return\s*None?\s*)$/
  0.8   if body_tokens < 3
  max(0, 1 - body_tokens / (signature_tokens × 3))  otherwise
}

file_stub_ratio = mean(stub_score(f) for f in file.functions)
```

### IR1+IR2 → IR3: Graph Construction

**Mathematical nature**: Creating a multi-relational directed graph from per-file data.

**Edge construction:**

```
For each file A:
  For each import in A.ir1.imports:
    if import.resolved_path = B:
      add_edge(A, B, type=IMPORT, weight=|import.names|)

  For each function fn in A.ir1.functions:
    For each call in fn.calls:
      target = resolve_call(call, A.ir1.imports, all_files)
      if target.file = B ≠ A:
        add_edge(A, B, type=CALL, weight=1)
```

**Graph metrics computation order:**

```
1. PageRank:      O(|V| × iterations × |E|/|V|) ≈ O(20|E|)
2. Tarjan SCC:    O(|V| + |E|)
3. Blast radius:  O(|V| × (|V| + |E|))  — BFS from each node on reverse graph
4. Louvain:       O(|E| × log|V|)        — near-linear in practice
5. DAG depth:     O(|V| + |E|)           — BFS from entry points
6. Spectral:      O(|V|³)                — eigendecomposition (or O(k|E|) for top-k via Lanczos)
7. NCD pairs:     O(n² × avg_file_size)  — with pruning: O(0.05n² × avg_file_size)
```

Total for a 1000-file codebase: spectral dominates at O(10⁹). Use Lanczos iteration for top-k eigenvalues to reduce to O(k × |E|) ≈ O(10⁵).

### IR3 → IR4: Architecture Inference

**Mathematical nature**: Graph contraction (file graph → module graph) + topological analysis.

**Module graph construction:**

```
module(file) = parent_directory(file.path)

module_graph: V' = {unique modules}, E' = {(m₁, m₂) : ∃ edge (f₁, f₂) in file graph where module(f₁)=m₁, module(f₂)=m₂, m₁≠m₂}

edge_weight(m₁, m₂) = |{(f₁,f₂) ∈ E : module(f₁)=m₁, module(f₂)=m₂}|
```

**Layer assignment** (topological ordering on module DAG):

```
1. Identify back-edges via DFS on module_graph
2. Remove back-edges → DAG
3. layer(m) = 0 if in_degree(m) = 0 in DAG
             = max(layer(dep) + 1) for deps of m

Back-edges = layer violations.
```

**Robert Martin's metrics:**

```
Ca(m) = afferent coupling = |{edges INTO m from outside}|
Ce(m) = efferent coupling = |{edges OUT of m to outside}|

Instability:    I(m) = Ce / (Ca + Ce)     ∈ [0, 1]
Abstractness:   A(m) = abstract_types / total_types   ∈ [0, 1]

Distance from Main Sequence:  D(m) = |A + I - 1|     ∈ [0, 1]
```

The "main sequence" is the line A + I = 1. Modules should be:
- Abstract AND stable (A high, I low): interfaces, contracts
- Concrete AND unstable (A low, I high): implementations, leaf code

Being in the **zone of pain** (concrete + stable, A low, I low): hard to change, everyone depends on it.
Being in the **zone of uselessness** (abstract + unstable, A high, I high): abstract code nobody uses.

```
Zone of Pain:        A < 0.3 AND I < 0.3
Zone of Uselessness: A > 0.7 AND I > 0.7
Main Sequence:       |A + I - 1| < 0.2
```

**Boundary alignment:**

```
For each module m:
  file_communities = {f: community(f) for f in m.files}  (from Louvain on file graph)
  dominant_community = mode(file_communities.values())
  alignment(m) = |{f : community(f) == dominant_community}| / |m.files|
```

alignment = 1.0: all files belong to the same community (perfect boundary)
alignment < 0.5: files in this module actually belong to different communities (wrong boundary)

### All IRs → IR5s: Signal Fusion

**Mathematical nature**: Dimensionality reduction + weighted combination.

**Percentile normalization:**

All signals are first normalized to percentiles within the codebase:

```
for signal S:
  values = [S(f) for f in all_files]
  for each file f:
    S_percentile(f) = |{v ∈ values : v ≤ S(f)}| / |values|
```

This makes all signals commensurable — they're all in [0, 1] with uniform distribution.

**Weighted fusion for composite scores:**

```
risk(f) = Σᵢ wᵢ × Sᵢ_percentile(f)

where Sᵢ ∈ {pagerank, blast_radius, cognitive_load, churn_rate, fix_ratio, ...}
      wᵢ = learned or hand-tuned weights, Σwᵢ = 1
```

**Optimal weight learning (if labeled data available):**

Given files labeled as "problematic" or "healthy":

```
Minimize: -Σ [yⱼ log(σ(w·xⱼ)) + (1-yⱼ) log(1 - σ(w·xⱼ))]

where xⱼ = percentile signal vector for file j
      yⱼ = 1 if file is problematic, 0 if healthy
      σ = sigmoid function
      w = weight vector to learn
```

This is logistic regression. Gives optimal weights for combining signals into a risk score.

**Without labeled data** — use signal covariance:

```
Compute covariance matrix of signals across files:
  Σ = cov([S₁(f), S₂(f), ..., Sₖ(f)] for all f)

Highly correlated signals (Σᵢⱼ > 0.8): redundant — keep one, drop the other.
Uncorrelated signals: complementary — both contribute independent information.

Total information = Σᵢ log(1 + λᵢ)  where λᵢ = eigenvalues of Σ
```

**Signal independence test:**

```
For each pair of signals (Sᵢ, Sⱼ):
  ρ = pearson_correlation(Sᵢ, Sⱼ across files)

  If |ρ| > 0.8: signals are redundant. Keep the one more correlated with known bad outcomes.
  If |ρ| < 0.2: signals are independent. Both contribute unique information.
```

### IR5s → IR6: Finding Generation

**Mathematical nature**: Pattern matching on the signal field. Logical conditions on derived dimensions.

Each finding is a predicate over signals:

```
high_risk_hub(f) = (
    percentile(pagerank, f) > 0.90
    AND percentile(blast_radius, f) > 0.90
    AND (percentile(cognitive_load, f) > 0.90 OR percentile(churn_rate, f) > 0.90)
)
```

**Confidence scoring:**

```
confidence(finding) = mean(
  margin_above_threshold(signal, threshold)
  for each signal condition in the finding
)

where margin_above_threshold(S, τ) = min(1, (S - τ) / (1 - τ))
```

A finding where pagerank percentile = 0.91 (just barely above 0.90) has lower confidence than one where pagerank percentile = 0.99 (far above threshold). The margin tells us how robust the finding is.

**Severity scoring:**

```
severity(finding) = base_severity(finding.type) × evidence_amplifier

evidence_amplifier = 1 + 0.1 × (|evidence_items| - min_required)
```

More evidence = higher severity (the problem is visible from multiple angles).

---

## Part III: Mathematics on the Full Tensor

### The File Vector Space

Each file is a point in R^d where d ≈ 40 (number of active cells in the measurement tensor):

```
x(f) = [S₁(f), S₂(f), ..., S_d(f)]

where Sᵢ are all measured signals, percentile-normalized to [0, 1].
```

The entire codebase is a point cloud in R^d:

```
X = {x(f₁), x(f₂), ..., x(fₙ)}     n = number of files
```

### Principal Component Analysis (PCA)

Find the axes of maximum variation in the file population:

```
1. Center: X̄ = X - mean(X)
2. Covariance: Σ = (1/n) X̄ᵀ X̄       (d × d matrix)
3. Eigendecompose: Σ = U Λ Uᵀ
4. Principal components: columns of U, ordered by eigenvalue magnitude
```

**What PCA reveals:**

```
PC1 (first principal component):
  = the axis of greatest variation across files
  = usually a "general quality" axis (high on all bad signals OR low on all)
  = explains ~30-40% of variance typically

PC2:
  = the axis of second-greatest variation, orthogonal to PC1
  = usually distinguishes structural vs temporal problems
  = explains ~15-20% of variance

PC1 + PC2 together explain ~50-60% of total variance.
```

The loadings (eigenvector coefficients) tell you which signals define each PC:

```
If PC1 = 0.3×pagerank + 0.3×blast_radius + 0.25×cognitive_load + 0.15×churn...
Then PC1 = "structural risk" axis.

If PC2 = 0.4×bus_factor + 0.3×author_entropy - 0.2×churn...
Then PC2 = "social risk" axis.
```

**Dimensionality of quality:** How many PCs do you need to explain 90% of variance? If 3-4, then code quality is fundamentally a low-dimensional phenomenon (just a few independent factors). If 15+, it's genuinely high-dimensional (many independent concerns).

### Anomaly Detection

Files that are unusual across multiple dimensions simultaneously.

**Mahalanobis distance:**

```
d_M(f) = √((x(f) - μ)ᵀ Σ⁻¹ (x(f) - μ))

where μ = mean signal vector
      Σ = covariance matrix
```

Mahalanobis distance accounts for correlations between signals. A file with high pagerank AND high cognitive load is less anomalous than one with high pagerank AND high compression ratio (because the first pair is commonly correlated, the second isn't).

```
d_M > χ²_d(0.95)^(1/2):  file is statistically anomalous at 95% confidence
```

**Isolation Forest** (better for non-Gaussian distributions):

```
1. Randomly select a signal dimension
2. Randomly select a split point between min and max
3. Partition files by split
4. Repeat recursively until each file is isolated
5. Anomaly score = average depth to isolation across many trees

Short depth = easy to isolate = anomalous
Long depth = takes many splits to isolate = normal
```

**Local Outlier Factor (LOF):**

```
For each file f:
  k_distance(f) = distance to k-th nearest neighbor in signal space
  reach_density(f) = 1 / mean(max(k_distance(neighbor), dist(f, neighbor)) for k neighbors)
  LOF(f) = mean(reach_density(neighbor) / reach_density(f) for k neighbors)

LOF >> 1: file is in a sparser region than its neighbors = local outlier
LOF ≈ 1: file has similar density to its neighbors = normal
```

LOF is powerful because it detects anomalies relative to the local neighborhood. A complex utility file might be normal among utilities but anomalous among config files.

### Clustering

Group files by their multi-dimensional signal profiles.

**k-Means:**

```
Minimize: Σᵢ Σ_{f ∈ Cᵢ} ‖x(f) - μᵢ‖²

where Cᵢ = cluster i, μᵢ = centroid of cluster i
```

Choose k via silhouette score:
```
s(f) = (b(f) - a(f)) / max(a(f), b(f))

where a(f) = mean distance to same-cluster files
      b(f) = mean distance to nearest other cluster

mean(s) > 0.5: good clustering. < 0.25: weak structure.
```

**What clusters reveal:**

- Cluster of (high complexity, high centrality, high churn) = "fire zone" — the files that need the most attention
- Cluster of (low complexity, low centrality, low churn) = "stable foundation" — healthy infrastructure
- Cluster of (high stub ratio, low call depth, many orphans) = "AI scaffolding" — generated but not wired up

Naming clusters automatically:
```
For each cluster c:
  distinguishing_signals = signals where c's mean > 75th percentile OR < 25th percentile of population
  cluster_name = join(distinguishing_signals, " + ")

  Example: "High centrality + High cognitive load + Low bus factor" → "Knowledge-risk hubs"
```

### The Temporal Tensor

The full data is a 3D tensor:

```
T ∈ R^(n × d × t)

where n = files, d = signal dimensions, t = time points
```

**Tensor decomposition (CP decomposition):**

Approximate T as a sum of rank-1 tensors:

```
T ≈ Σᵣ₌₁ᴿ λᵣ (aᵣ ⊗ bᵣ ⊗ cᵣ)

where aᵣ ∈ R^n = file profile
      bᵣ ∈ R^d = signal profile
      cᵣ ∈ R^t = time profile
      λᵣ = weight
```

Each component r captures a "latent factor":
```
Component 1: aᵣ = [high on files A,B,C], bᵣ = [high on complexity, churn], cᵣ = [increasing over time]
Interpretation: "Files A, B, C are becoming more complex and churny over time"

Component 2: aᵣ = [high on files X,Y], bᵣ = [high on bus_factor, coherence], cᵣ = [stable]
Interpretation: "Files X, Y have consistently good health metrics"
```

CP decomposition reveals **archetypes** — the fundamental patterns of file evolution in the codebase.

**Tucker decomposition** (more general):

```
T ≈ G ×₁ A ×₂ B ×₃ C

where G ∈ R^(R₁ × R₂ × R₃) = core tensor (interactions between factors)
      A ∈ R^(n × R₁) = file factor matrix
      B ∈ R^(d × R₂) = signal factor matrix
      C ∈ R^(t × R₃) = time factor matrix
```

Tucker captures interactions: "the combination of this file group AND this signal group AND this time period is unusual." CP cannot capture such three-way interactions.

### Multi-Graph Spectral Analysis

We have 6 graphs over the same node set (files). This is a **multiplex network**.

**Combined Laplacian:**

```
L_combined = Σᵢ αᵢ Lᵢ

where Lᵢ = Laplacian of graph i (dependency, call, type, co-change, author, semantic)
      αᵢ = weight for graph i
```

The eigenvectors of L_combined define **multi-relational communities**: groups of files that are close across ALL relationship types simultaneously.

```
Fiedler vector of L_combined → bipartition that respects all graphs at once
```

This is more powerful than Louvain on any single graph because it finds communities that are structurally, temporally, AND socially coherent.

**Graph disagreement matrix:**

For each pair of graphs (Gᵢ, Gⱼ), compute how much they disagree:

```
D_ij = ‖L_i / ‖L_i‖_F  -  L_j / ‖L_j‖_F‖_F

where ‖·‖_F = Frobenius norm
```

D_ij ≈ 0: graphs i and j tell the same story
D_ij large: graphs disagree — there exist file pairs that are close in one but far in the other

This gives a 6×6 matrix of inter-graph disagreement. High values indicate fruitful finding opportunities.

**Random walk on the multiplex:**

```
At each step:
  1. Choose graph type i with probability proportional to αᵢ
  2. Follow a random edge in graph Gᵢ

Stationary distribution = multiplex PageRank
```

Multiplex PageRank captures "importance across all types of relationship." A file that is structurally central AND temporally coupled AND semantically related to many files gets the highest multiplex PageRank.

### Signal Manifold Geometry

The file vectors don't just live in R^d — they live on a **manifold** (a curved subspace).

**UMAP for visualization:**

```
1. Build k-nearest-neighbor graph in signal space
2. Compute fuzzy topological representation (simplicial complex)
3. Optimize 2D layout that preserves the topology

Result: 2D scatter plot where nearby points = similar files
```

UMAP preserves both local AND global structure (unlike t-SNE which only preserves local). This means clusters, outliers, and inter-cluster distances are all meaningful.

**Persistent homology** (topological data analysis):

```
1. Build Vietoris-Rips complex at increasing distance thresholds ε
2. Track when topological features (components, loops, voids) appear and disappear
3. Features that persist across many ε values = genuine structure
   Features that appear/disappear quickly = noise

Persistence diagram: plot (birth_ε, death_ε) for each feature
```

What this reveals for a codebase:
- **Long-lived connected components** at small ε: tight clusters of similar files
- **Loops (1-cycles)** that persist: groups of files that form boundaries without connecting to their interior (hollow abstractions)
- **Voids (2-cycles)** that persist: higher-order structural holes in the codebase

### Information-Theoretic Optimality

**Minimum Description Length (MDL):**

The "best model" of a codebase is the one that minimizes:

```
MDL = L(model) + L(data | model)

where L(model) = bits to describe the architectural model
      L(data | model) = bits to describe the deviations from the model
```

If the declared architecture (IR4) is a good model, L(data | model) is small. If the actual code deviates a lot, L(data | model) is large.

```
architecture_fit = L(data | model) / L(data)

architecture_fit ≈ 0: architecture explains the code perfectly
architecture_fit ≈ 1: architecture explains nothing (might as well have no architecture)
```

This gives a principled single number for "how well does the intended architecture match reality?"

**Mutual Information between dimension pairs:**

```
I(Dᵢ; Dⱼ) = Σ_{x,y} p(x,y) log₂(p(x,y) / (p(x)p(y)))

where x = binned values of dimension i
      y = binned values of dimension j
```

High I(Dᵢ; Dⱼ) = these dimensions are informationally coupled (knowing one tells you about the other).

Example findings:
```
I(REFERENCE; AUTHORSHIP) high → files that are structurally coupled tend to have the same authors (Conway's law holds)
I(CHANGE; INFORMATION) high → files that change often tend to be informationally dense (complex code attracts changes)
I(SIZE; INTENT) high → big files attract more bug fixes (size breeds bugs)
```

Low mutual information between dimensions that "should" be related is also interesting:
```
I(REFERENCE; NAMING) low → structurally coupled files use different vocabularies = accidental coupling
```

### Health as a Scalar Field

Define health as a scalar function over the codebase graph:

```
h: V → [0, 1]

h(f) = 1 - risk_score(f)
```

The **health gradient** between connected files:

```
∇h(f₁, f₂) = h(f₂) - h(f₁)   for edge f₁→f₂
```

Health should flow "upward" — leaf implementations can be messy, but the code they flow into should be healthier. If ∇h is consistently negative along dependency edges (depending on unhealthier code), the architecture is "health-inverting" — a structural anti-pattern.

**Health Laplacian:**

```
Define weight matrix W where W[i,j] = 1 if edge exists, 0 otherwise
Define health vector h = [h(f₁), ..., h(fₙ)]

Δh(f) = Σ_{neighbors g} W[f,g] × (h(g) - h(f))
       = (health of neighbors) - (health of f) × degree(f)
```

Δh(f) > 0: file f is surrounded by healthier files (it's a local minimum — the weakest link)
Δh(f) < 0: file f is healthier than its neighbors (it's doing well in a bad neighborhood)

Files with large negative Δh are **hidden strengths** — good code in a bad part of the graph.
Files with large positive Δh are **weak links** — the one bad file that drags down a healthy neighborhood.

This is analogous to heat diffusion: if we "diffuse" health through the graph, what would the equilibrium look like? Files far from equilibrium are the interesting ones.

### Codebase Entropy Rate

The codebase as a whole has an information-theoretic characterization:

**Structural entropy:**

```
H_struct = -Σ_m p(m) log₂ p(m)

where p(m) = |files in module m| / |total files|
```

How evenly distributed are files across modules?

**Change entropy:**

```
H_change = -Σ_f p(f) log₂ p(f)

where p(f) = |commits touching f| / |total file-commit pairs|
```

How evenly distributed are changes across files?

**Joint entropy:**

```
H(struct, change) = -Σ_{m,f} p(m,f) log₂ p(m,f)
```

**Mutual information between structure and change:**

```
I(struct; change) = H_struct + H_change - H(struct, change)
```

High I: changes cluster within modules (changes respect architecture — healthy)
Low I: changes spread across modules (changes ignore architecture — erosion)

### The Health Tensor Decomposition

Combining everything:

```
For snapshot at time t:

  1. Compute measurement tensor M(dimension, scale, file)
  2. Normalize to percentiles
  3. Compute derived dimensions (products of fundamentals)
  4. Evaluate finding predicates → insights

  5. PCA → principal quality factors
  6. Clustering → file archetypes
  7. Anomaly detection → outliers
  8. Multi-graph spectral → cross-relational communities

  9. Compare to previous snapshot:
     ΔM = M(t) - M(t-1)
     Velocity = dM/dt
     Acceleration = d²M/dt²

  10. CP decomposition of temporal tensor → evolution archetypes

  11. Scalar summaries:
      codebase_health = f(modularity, wiring_score, debt_velocity, ...)
      architecture_fit = MDL ratio
      knowledge_risk = f(min bus factor on critical paths, Conway correlation)
      ai_quality = f(orphan_ratio, stub_ratio, phantom_ratio, glue_deficit)
```

---

## Part IV: Mathematical Summary by IR

| IR | Input | Transform | Key Math | Output |
|----|-------|-----------|----------|--------|
| IR0→IR1 | bytes | parsing | AST traversal, token counting | FileSyntax |
| IR1→IR2 | syntax | classification + clustering | TF-IDF, Louvain on token co-occurrence, cosine similarity | FileSemantics |
| IR2→IR3 | semantics | graph construction | Edge resolution, path algorithms | CodeGraph |
| IR3 internal | graph | graph algorithms | PageRank (eigenvector), Tarjan (DFS), BFS (blast), Louvain (modularity max), Lanczos (spectral) | GraphMetrics |
| IR3 cross-file | bytes pairs | information distance | NCD (compression), mutual information, conditional entropy | PairMetrics |
| IR3→IR4 | file graph | graph contraction + topo sort | Module graph, topological ordering, Martin's I/A/D, Cheeger inequality | Architecture |
| Git→IR5t | commits | time series analysis | Linear regression, CV, PELT change points, survival analysis, association rules (lift/confidence) | TemporalModel |
| All→IR5s | all IRs | signal fusion | Percentile normalization, weighted combination, logistic regression (if labels), covariance analysis, PCA | SignalField |
| IR5s→IR6 | signals | pattern matching | Multi-signal predicates, confidence margins, severity scoring | Insights |
| Tensor-level | full tensor | tensor analysis | CP/Tucker decomposition, Mahalanobis anomaly detection, UMAP, persistent homology, MDL, multiplex spectral | Meta-insights |
