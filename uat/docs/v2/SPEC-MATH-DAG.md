# Mathematical Computation DAG Specification

## Document Information

| Field        | Value               |
| ------------ | ------------------- |
| Version      | 1.0                 |
| Status       | Formal Specification|
| Last Updated | 2026-02-19          |

---

## 1. Purpose

This document specifies the **exact mathematical dependency graph (DAG)** for all computations in the Shannon Insight pipeline. Every node represents a computation, every edge represents a data dependency.

**Key Properties:**
- **Acyclic**: No computation can depend on itself (directly or transitively)
- **Explicit Dependencies**: Every input to every computation is listed
- **Parallelizable**: Nodes at same depth can run in parallel
- **Verifiable**: Each edge can be traced to a mathematical formula

---

## 2. DAG Notation

```
ComputationNode(deps=[list of required computations])
  → Output: signal_name (scope)
  → Formula: mathematical definition
```

**DAG Levels:**
- Level 0: Raw inputs (filesystem, git)
- Level 1-2: Parsed facts
- Level 3-5: Graphs
- Level 6-8: Graph algorithms
- Level 9-11: Derived signals
- Level 12-14: Composite signals
- Level 15+: Finders

---

## 3. Complete DAG

### Level 0: Raw Inputs (No dependencies)

```
FileSystem
  → Output: file_content(path) → bytes
  → Source: filesystem read

GitRepository  
  → Output: commit_history → List[Commit]
  → Source: git log
```

---

### Level 1: Parsing (Depends on Level 0)

```
FileParser(deps=[FileSystem])
  → Output: 
    - lines(path) → int
    - function_count(path) → int
    - class_count(path) → int
    - import_statements(path) → List[str]
    - function_bodies(path) → List[str]
    - nesting_depths(path) → List[int]
  → Formula: tree-sitter AST traversal

ContentHash(deps=[FileSystem])
  → Output: content_hash(path) → str
  → Formula: SHA256(file_content(path))

GitLogParser(deps=[GitRepository])
  → Output:
    - commit_hash(i) → str
    - commit_timestamp(i) → int
    - commit_author(i) → str
    - commit_subject(i) → str
  → Formula: git log parsing

GitDiffParser(deps=[GitRepository])
  → Output:
    - file_change(commit, path) → {A, M, D, R}
    - additions(commit, path) → int
    - deletions(commit, path) → int
  → Formula: git log --numstat parsing
```

---

### Level 2: Derived Parsing (Depends on Level 1)

```
ImportResolver(deps=[FileParser, FileSystem])
  → Output: 
    - resolved_imports(path) → List[path]
    - phantom_imports(path) → List[str]
  → Formula: 
    resolved = [resolve(imp) for imp in import_statements(path) if resolve(imp) exists]
    phantom = [imp for imp in import_statements(path) if resolve(imp) is None]

CyclomaticComplexity(deps=[FileParser])
  → Output: complexity(path) → int
  → Formula: complexity = Σ(decision_points in function) for each function

MaxNesting(deps=[FileParser])
  → Output: max_nesting(path) → int
  → Formula: max(nesting_depths(path))

FunctionSizeStats(deps=[FileParser])
  → Output:
    - max_function_lines(path) → int
    - function_sizes(path) → List[int]
    - stub_count(path) → int
  → Formula:
    sizes = [len(body.split('\n')) for body in function_bodies(path)]
    stubs = count(body for body in function_bodies(path) if is_trivial(body))

ImplGini(deps=[FunctionSizeStats])
  → Output: impl_gini(path) → float
  → Formula: Gini(function_sizes(path))

StubRatio(deps=[FunctionSizeStats, FileParser])
  → Output: stub_ratio(path) → float
  → Formula: stub_count(path) / max(function_count(path), 1)

EventBuilder(deps=[GitLogParser, GitDiffParser])
  → Output: events → List[Event]
  → Formula:
    for each commit c:
      for each file_change(c, path):
        emit Event(type=change_type, timestamp=c.timestamp, path=path)

NodeLifecycle(deps=[EventBuilder])
  → Output:
    - birth_ts(path) → int
    - death_ts(path) → int | None
    - canonical_path(path) → str
  → Formula:
    birth_ts(path) = min(e.timestamp for e in events if e.path == path and e.type in {A, M})
    death_ts(path) = max(e.timestamp for e in events if e.path == path and e.type == D) or None

TimeWindowBuilder(deps=[GitLogParser])
  → Output: time_windows → List[Window]
  → Formula:
    partition commits by (timestamp // window_size)
    window_w = {commits where w*window_size <= timestamp < (w+1)*window_size}
```

---

### Level 3: Graph Construction (Depends on Level 1-2)

```
G_Import(deps=[ImportResolver])
  → Output: 
    - E_import → Set[(source, target)]
    - W_import(source, target) → float (always 1.0)
  → Formula:
    E_import = {(a, b) : b in resolved_imports(a)}

G_Cochange(deps=[TimeWindowBuilder, GitDiffParser])
  → Output:
    - E_cochange → Set[(a, b)]
    - W_cochange(a, b) → float
  → Formula:
    cochange_count(a, b) = |{c : a ∈ files(c) and b ∈ files(c)}|
    P(a) = |{c : a ∈ files(c)}| / |commits|
    P(a, b) = cochange_count(a, b) / |commits|
    lift(a, b) = P(a, b) / (P(a) × P(b))
    E_cochange = {(a, b) : lift(a, b) > 1.0}
    W_cochange(a, b) = lift(a, b)

G_Author(deps=[GitLogParser, GitDiffParser])
  → Output:
    - E_author → Set[(a, b)]
    - W_author(a, b) → float
  → Formula:
    authors(path) = {c.author for c in commits where path ∈ files(c)}
    Jaccard(a, b) = |authors(a) ∩ authors(b)| / |authors(a) ∪ authors(b)|
    E_author = {(a, b) : Jaccard(a, b) > 0.1}
    W_author(a, b) = Jaccard(a, b)

ConceptExtractor(deps=[FileParser, FileSystem])
  → Output: concepts(path) → Dict[str, float]
  → Formula:
    tokens = tokenize(identifiers + comments + strings)
    tfidf(token, path) = tf(token, path) × idf(token)
    concepts(path) = {top-k tokens by tfidf}

G_Semantic(deps=[ConceptExtractor])
  → Output:
    - E_semantic → Set[(a, b)]
    - W_semantic(a, b) → float
  → Formula:
    cosine(a, b) = concepts(a) · concepts(b) / (||concepts(a)|| × ||concepts(b)||)
    E_semantic = {(a, b) : cosine(a, b) > 0.3}
    W_semantic(a, b) = cosine(a, b)

G_Clone(deps=[FileSystem, ContentHash])
  → Output:
    - E_clone → Set[(a, b)]
    - W_clone(a, b) → float
  → Formula:
    NCD(a, b) = (C(a+b) - min(C(a), C(b))) / max(C(a), C(b))
    where C(x) = compressed_size(x)
    E_clone = {(a, b) : NCD(a, b) < 0.3}
    W_clone(a, b) = 1 - NCD(a, b)
```

---

### Level 4: Graph Fusion (Depends on Level 3)

```
GraphNormalizer(deps=[G_Import, G_Cochange, G_Author, G_Semantic])
  → Output: 
    - W_norm_import(a, b) → float
    - W_norm_cochange(a, b) → float
    - W_norm_author(a, b) → float
    - W_norm_semantic(a, b) → float
  → Formula:
    W_norm_r(a, b) = (W_r(a, b) - min_r) / (max_r - min_r)

G_Combined(deps=[GraphNormalizer])
  → Output:
    - E_combined → Set[(a, b)]
    - W_combined(a, b) → float
  → Formula:
    W_combined(a, b) = α×W_norm_import(a,b) + β×W_norm_cochange(a,b) 
                     + γ×W_norm_author(a,b) + δ×W_norm_semantic(a,b)
    where α=0.4, β=0.3, γ=0.2, δ=0.1
    E_combined = {(a, b) : W_combined(a, b) > 0.1}
```

---

### Level 5: Historical Graph Sampling (Depends on Level 3, NodeLifecycle)

```
GraphHistorySampler(deps=[G_Import, G_Cochange, NodeLifecycle, EventBuilder])
  → Output: 
    - G_import(t) for t in sample_times
    - G_cochange(t) for t in sample_times
  → Formula:
    G_import(t) = {(a, b) : edge_lifecycle[IMPORT, a, b].birth_ts ≤ t < death_ts}
    G_cochange(t) = compute from windows ending at t
    sample_times = [now - 1mo, now - 3mo, now - 6mo, now - 12mo]
```

---

### Level 6: Graph Algorithms - Adjacency/Degree (Depends on Level 3-4)

```
AdjacencyMatrix(deps=[G_Import])
  → Output:
    - A_import → Matrix[N×N]
    - D_import → DiagonalMatrix[N×N]
  → Formula:
    A[i,j] = 1 if (i,j) ∈ E_import else 0
    D[i,i] = Σ_j A[i,j]

[Similar for G_Cochange, G_Author, G_Semantic, G_Combined]

Degree(deps=[AdjacencyMatrix])
  → Output:
    - in_degree(path, r) → int
    - out_degree(path, r) → int
    - degree(path, r) → int
  → Formula:
    in_degree(v, r) = |{u : (u, v) ∈ E_r}|
    out_degree(v, r) = |{u : (v, u) ∈ E_r}|
    degree(v, r) = in_degree + out_degree

IsOrphan(deps=[Degree])
  → Output: is_orphan(path, r) → bool
  → Formula: in_degree(path, r) == 0
```

---

### Level 7: Graph Algorithms - PageRank (Depends on Level 6)

```
TransitionMatrix(deps=[AdjacencyMatrix])
  → Output: P_import → Matrix[N×N]
  → Formula: P = D^{-1} A

PageRank(deps=[TransitionMatrix])
  → Output: pagerank(path, r) → float
  → Formula:
    π^{(k+1)} = (1-α)Pπ^{(k)} + αv
    where α = 0.15, v = (1/N, ..., 1/N)
    pagerank(v) = lim_{k→∞} π^{(k)}[v]

[Same for G_Cochange, G_Author, G_Semantic, G_Combined]
```

---

### Level 8: Graph Algorithms - Community (Depends on Level 6-7)

```
Louvain(deps=[AdjacencyMatrix])
  → Output:
    - community(path, r) → int
    - modularity(r) → float
  → Formula:
    Q = (1/2m) Σ_{i,j} [A_{ij} - (k_i k_j / 2m)] δ(c_i, c_j)
    Repeat:
      Phase 1: move each node to best community
      Phase 2: aggregate communities into supernodes
    Until Q stops improving

CommunitySizes(deps=[Louvain])
  → Output: community_size(community_id, r) → int
  → Formula: |{v : community(v, r) = community_id}|
```

---

### Level 9: Graph Algorithms - Spectral (Depends on Level 6)

```
Laplacian(deps=[AdjacencyMatrix])
  → Output: L_import → Matrix[N×N]
  → Formula: L = D - A

NormalizedLaplacian(deps=[Laplacian, AdjacencyMatrix])
  → Output: L_norm_import → Matrix[N×N]
  → Formula: L_norm = I - D^{-1/2} A D^{-1/2}

SpectralDecomposition(deps=[NormalizedLaplacian])
  → Output:
    - fiedler_value(r) → float
    - spectral_gap(r) → float
    - eigenvectors(r) → Matrix[N×k]
  → Formula:
    eigenvalues = sort(λ_1 ≤ λ_2 ≤ ... ≤ λ_N) from L_norm = UΛU^T
    fiedler_value = λ_2
    spectral_gap = λ_3 - λ_2
```

---

### Level 10: Graph Algorithms - Structural (Depends on Level 3, 6)

```
SCCDetection(deps=[G_Import])
  → Output:
    - cycle_member(path, r) → bool
    - cycle_size(path, r) → int
    - cycle_count(r) → int
  → Formula: Kosaraju's or Tarjan's algorithm
    SCCs = strongly_connected_components(G_r)
    cycle_member(v) = |SCC containing v| > 1
    cycle_size(v) = |SCC containing v|

BFS_Depth(deps=[G_Import, EntryPoints])
  → Output: depth(path, r) → int
  → Formula:
    depth(v) = min_{entry} BFS_distance(entry, v)
    where entry ∈ {v : role(v) == ENTRY_POINT}

TransitiveClosure(deps=[G_Import])
  → Output: reachable_from(path) → Set[path]
  → Formula: TC = closure of A under matrix multiplication

BlastRadius(deps=[TransitiveClosure])
  → Output: blast_radius_size(path, r) → int
  → Formula: |reachable_from(path)|
```

---

### Level 11: Graph Algorithms - Distribution (Depends on Level 7)

```
CentralityDistribution(deps=[PageRank])
  → Output: pagerank_values(r) → List[float]
  → Formula: [pagerank(v, r) for v in files]

GiniCoefficient(deps=[CentralityDistribution])
  → Output: centrality_gini(r) → float
  → Formula:
    x = sorted(pagerank_values(r))
    n = len(x)
    G = (2 Σ_{i} i×x_i) / (n Σ_{i} x_i) - (n+1)/n
```

---

### Level 12: Temporal Signals - Basic (Depends on Level 1-2, 5)

```
CommitCounts(deps=[GitDiffParser, NodeLifecycle])
  → Output:
    - total_changes(path) → int
    - total_additions(path) → int
    - total_deletions(path) → int
  → Formula:
    total_changes(path) = |{c : path ∈ files(c)}|
    total_additions(path) = Σ_c additions(c, path)
    total_deletions(path) = Σ_c deletions(c, path)

AuthorStats(deps=[GitLogParser, GitDiffParser])
  → Output:
    - total_authors(path) → int
    - author_commit_counts(path) → Dict[author, count]
  → Formula:
    authors(path) = {c.author : path ∈ files(c)}
    author_commit_counts(path)[a] = |{c : c.author = a and path ∈ files(c)}|
```

---

### Level 13: Temporal Signals - Windowed (Depends on Level 12, TimeWindowBuilder)

```
WindowedChurn(deps=[GitDiffParser, TimeWindowBuilder])
  → Output:
    - churn_w(path, window) → int
    - commits_w(path, window) → int
  → Formula:
    churn_w(path, w) = Σ_{c in w} (additions(c,path) + deletions(c,path))
    commits_w(path, w) = |{c in w : path ∈ files(c)}|

WindowedAuthors(deps=[AuthorStats, TimeWindowBuilder])
  → Output: authors_w(path, window) → int
  → Formula: |{a : author made commit in window touching path}|

ChurnStats(deps=[WindowedChurn])
  → Output:
    - churn_mean(path) → float
    - churn_std(path) → float
    - churn_cv(path) → float
  → Formula:
    churn_values = [churn_w(path, w) for w in windows]
    churn_mean = mean(churn_values)
    churn_std = std(churn_values)
    churn_cv = churn_std / max(churn_mean, 1)

ChurnTrend(deps=[WindowedChurn])
  → Output: churn_trend(path) → float
  → Formula:
    β = linear_regression_slope(churn_values over time)
    churn_trend = β

ChurnTrajectory(deps=[ChurnStats, ChurnTrend, CommitCounts])
  → Output: churn_trajectory(path) → enum
  → Formula:
    if total_changes ≤ 1 or churn_cv == 0: DORMANT
    elif churn_trend < -θ and churn_cv < 0.5: STABILIZING
    elif churn_trend > θ and churn_cv > 0.5: SPIKING
    elif churn_cv > 0.5: CHURNING
    else: STABLE

AuthorEntropy(deps=[AuthorStats])
  → Output: author_entropy(path) → float
  → Formula:
    p_a = author_commit_counts[path][a] / total_changes(path)
    H = -Σ_a p_a × log₂(p_a)

BusFactor(deps=[AuthorEntropy])
  → Output: bus_factor(path) → float
  → Formula: 2^(author_entropy(path))

CommitClassification(deps=[GitLogParser])
  → Output:
    - fix_commits(path) → int
    - refactor_commits(path) → int
  → Formula:
    fix_commits = |{c : path ∈ files(c) and is_fix(c.subject)}|
    refactor_commits = |{c : path ∈ files(c) and is_refactor(c.subject)}|

CommitRatios(deps=[CommitClassification, CommitCounts])
  → Output:
    - fix_ratio(path) → float
    - refactor_ratio(path) → float
  → Formula:
    fix_ratio = fix_commits / max(total_changes, 1)
    refactor_ratio = refactor_commits / max(total_changes, 1)

ChangeEntropy(deps=[WindowedChurn])
  → Output: change_entropy(path) → float
  → Formula:
    churn_values = [churn_w(path, w) for w in windows]
    total = sum(churn_values)
    p_w = churn_values[w] / total
    H = -Σ_w p_w × log₂(p_w)
```

---

### Level 14: Semantic Signals (Depends on Level 2, ConceptExtractor)

```
RoleClassifier(deps=[FileParser, ImportResolver, FunctionSizeStats])
  → Output: role(path) → enum
  → Formula:
    if has_main(path): ENTRY
    elif has_class_defs(path) and few_imports(path): MODEL
    elif has_test_patterns(path): TEST
    elif has_route_handlers(path): ROUTER
    elif has_db_access(path): DATASTORE
    elif many_imports(path) and many_exports(path): SERVICE
    elif few_functions(path) and many_imports(path): CONFIG
    else: UTILITY

ConceptStats(deps=[ConceptExtractor])
  → Output:
    - concept_count(path) → int
    - concept_entropy(path) → float
  → Formula:
    concept_count = |concepts(path)|
    weights = list(concepts(path).values())
    total = sum(weights)
    p_i = weights[i] / total
    H = -Σ_i p_i × log₂(p_i)

SemanticCoherence(deps=[ConceptStats])
  → Output: semantic_coherence(path) → float
  → Formula: 1 / (1 + concept_entropy(path))

NamingDrift(deps=[FileParser])
  → Output: naming_drift(path) → float
  → Formula:
    identifiers = extract_identifiers(path)
    inconsistency = measure_naming_style_variance(identifiers)
    naming_drift = inconsistency

TodoDensity(deps=[FileParser])
  → Output: todo_density(path) → float
  → Formula:
    todo_count = count_occurrences(path, ["TODO", "FIXME", "XXX"])
    todo_density = todo_count / max(lines(path), 1)

DocstringCoverage(deps=[FileParser])
  → Output: docstring_coverage(path) → float
  → Formula:
    documented = count(functions with docstrings)
    docstring_coverage = documented / max(function_count, 1)
```

---

### Level 15: Cognitive Load (Depends on Level 1-2, 6)

```
CognitiveLoad(deps=[FileParser, FunctionSizeStats, ImplGini, Degree])
  → Output: cognitive_load(path) → float
  → Formula:
    CL = α × log(lines) 
       + β × log(complexity + 1)
       + γ × max_nesting
       + δ × impl_gini
       + ε × log(degree(path, IMPORT) + 1)
    normalized = CL / (α + β + γ + δ + ε)
    where α=0.25, β=0.25, γ=0.20, δ=0.15, ε=0.15

CompressionRatio(deps=[FileSystem])
  → Output: compression_ratio(path) → float
  → Formula:
    raw_size = len(file_content(path))
    compressed_size = zlib.compress(file_content(path))
    compression_ratio = compressed_size / raw_size
```

---

### Level 16: Trajectory Signals (Depends on Level 5, 7, 8)

```
SignalHistory(deps=[GraphHistorySampler, PageRank, Louvain])
  → Output:
    - pagerank_history(path) → List[(t, value)]
    - community_history(path) → List[(t, value)]
  → Formula:
    For each t in sample_times:
      Compute pagerank(path, r) on G_import(t)
      Compute community(path, r) on G_import(t)

PagerankVelocity(deps=[SignalHistory])
  → Output: pagerank_velocity(path) → float
  → Formula:
    D(pagerank) = (pagerank(t_now) - pagerank(t_prev)) / (t_now - t_prev)

PagerankAcceleration(deps=[PagerankVelocity])
  → Output: pagerank_acceleration(path) → float
  → Formula:
    D²(pagerank) = (D(pagerank)_now - D(pagerank)_prev) / Δt

CommunityStability(deps=[SignalHistory])
  → Output:
    - community_changes(path) → int
    - community_stability(path) → float
  → Formula:
    community_changes = Σ_t 1(community(t) ≠ community(t-1))
    community_stability = 1 - community_changes / (num_transitions)

CentralityTrend(deps=[SignalHistory])
  → Output: centrality_trend(path) → float
  → Formula:
    values = [pagerank(t) for t in times]
    centrality_trend = linear_regression_slope(values)

GlobalTrajectory(deps=[GraphHistorySampler, SpectralDecomposition, Louvain])
  → Output:
    - graph_velocity(r) → float
    - fiedler_trend(r) → float
    - modularity_trend(r) → float
    - topology_stability(r) → float
  → Formula:
    graph_velocity = mean(|E(t) △ E(t-1)| / |E(t) ∪ E(t-1)|)
    fiedler_trend = slope([fiedler_value(t) for t in times])
    modularity_trend = slope([modularity(t) for t in times])
    topology_stability = 1 / (1 + graph_velocity)
```

---

### Level 17: Cross-Layer Signals - Global (Depends on Level 3)

```
MutualInformation(deps=[G_Import, G_Cochange, G_Author, G_Semantic])
  → Output:
    - behavioral_coherence → float
    - conway_alignment → float
    - semantic_alignment → float
  → Formula:
    I(G₁; G₂) = Σₐ Σᵦ (nₐᵦ/n) log₂[(nₐᵦ × n) / (nₐ• × n•ᵦ)]
    
    n₁₁ = |{(i,j) : A₁[i,j]=1 ∧ A₂[i,j]=1}|
    n₁₀ = |{(i,j) : A₁[i,j]=1 ∧ A₂[i,j]=0}|
    n₀₁ = |{(i,j) : A₁[i,j]=0 ∧ A₂[i,j]=1}|
    n₀₀ = |{(i,j) : A₁[i,j]=0 ∧ A₂[i,j]=0}|
    n = n₁₁ + n₁₀ + n₀₁ + n₀₀
    
    behavioral_coherence = I(G_import; G_cochange)
    conway_alignment = I(G_import; G_author)
    semantic_alignment = I(G_import; G_semantic)
```

---

### Level 18: Cross-Layer Signals - Per Node (Depends on Level 3, 6)

```
NeighborhoodSets(deps=[G_Import, G_Cochange, G_Author])
  → Output:
    - N_import(path) → Set[path]
    - N_cochange(path) → Set[path]
    - N_author(path) → Set[path]
  → Formula:
    N_r(v) = {u : (v, u) ∈ E_r or (u, v) ∈ E_r}

HiddenCouplingCount(deps=[NeighborhoodSets])
  → Output: hidden_coupling_count(path) → int
  → Formula: |N_cochange(path) \ N_import(path)|

DeadImportCount(deps=[NeighborhoodSets])
  → Output: dead_import_count(path) → int
  → Formula: |N_import(path) \ N_cochange(path)|

ConwayViolationCount(deps=[NeighborhoodSets])
  → Output: conway_violation_count(path) → int
  → Formula: |N_import(path) \ N_author(path)|

NeighborhoodCoherence(deps=[NeighborhoodSets])
  → Output: neighborhood_coherence(path) → float
  → Formula:
    Jaccard(N_import, N_cochange) = |N_import ∩ N_cochange| / |N_import ∪ N_cochange|
```

---

### Level 19: Cross-Layer Signals - Per Pair (Depends on Level 3)

```
PairSignals(deps=[G_Import, G_Cochange, G_Author, G_Semantic])
  → Output:
    - has_import(a, b) → bool
    - cochange_strength(a, b) → float
    - author_overlap(a, b) → float
    - semantic_similarity(a, b) → float
    - hidden_coupling(a, b) → float
    - conway_violation(a, b) → float
    - semantic_mismatch(a, b) → float
  → Formula:
    has_import(a, b) = (a, b) ∈ E_import or (b, a) ∈ E_import
    cochange_strength(a, b) = W_cochange(a, b) if (a, b) ∈ E_cochange else 0
    author_overlap(a, b) = W_author(a, b) if (a, b) ∈ E_author else 0
    semantic_similarity(a, b) = W_semantic(a, b) if (a, b) ∈ E_semantic else 0
    
    hidden_coupling(a, b) = cochange_strength(a, b) × (1 - has_import(a, b))
    conway_violation(a, b) = has_import(a, b) × (1 - author_overlap(a, b))
    semantic_mismatch(a, b) = has_import(a, b) × (1 - semantic_similarity(a, b))
```

---

### Level 20: Module Signals (Depends on Level 3, 6, 14)

```
ModuleMembership(deps=[FileSystem])
  → Output: module(path) → str
  → Formula: module = directory(path) or explicit config

ModuleEdges(deps=[G_Import, ModuleMembership])
  → Output:
    - internal_edges(module) → Set[(path, path)]
    - external_edges(module) → Set[(path, path)]
    - incoming_edges(module) → Set[(path, path)]
  → Formula:
    internal = {(a, b) ∈ E_import : module(a) == module(b) == m}
    external = {(a, b) ∈ E_import : module(a) == m and module(b) ≠ m}
    incoming = {(a, b) ∈ E_import : module(a) ≠ m and module(b) == m}

Cohesion(deps=[ModuleEdges, ModuleMembership])
  → Output: cohesion(module) → float
  → Formula:
    possible_internal = C(|files_in_module|, 2)
    cohesion = |internal_edges| / max(possible_internal, 1)

Coupling(deps=[ModuleEdges])
  → Output: coupling(module) → float
  → Formula:
    total = |internal_edges| + |external_edges|
    coupling = |external_edges| / max(total, 1)

Instability(deps=[ModuleEdges])
  → Output:
    - Ce(module) → int  # efferent (outgoing)
    - Ca(module) → int  # afferent (incoming)
    - instability(module) → float
  → Formula:
    Ce = |{(a, b) ∈ E_import : module(a) == m and module(b) ≠ m}|
    Ca = |{(a, b) ∈ E_import : module(a) ≠ m and module(b) == m}|
    instability = Ce / max(Ce + Ca, 1)

Abstractness(deps=[ModuleMembership, RoleClassifier])
  → Output: abstractness(module) → float
  → Formula:
    abstract_count = |{v in module : role(v) in {MODEL, INTERFACE}}|
    abstractness = abstract_count / |module|

MainSequenceDistance(deps=[Instability, Abstractness])
  → Output: main_seq_distance(module) → float
  → Formula: |abstractness + instability - 1|

BoundaryAlignment(deps=[ModuleMembership, Louvain])
  → Output: boundary_alignment(module) → float
  → Formula:
    dominant = mode(community(v) for v in module)
    boundary_alignment = |{v in module : community(v) == dominant}| / |module|

LayerViolationCount(deps=[G_Import, LayerAssignments])
  → Output: layer_violation_count(module) → int
  → Formula:
    |{(a, b) ∈ E_import : module(a) == m and layer(a) < layer(b)}|

RoleConsistency(deps=[ModuleMembership, RoleClassifier])
  → Output: role_consistency(module) → float
  → Formula:
    dominant = mode(role(v) for v in module)
    role_consistency = |{v in module : role(v) == dominant}| / |module|

ModuleVelocity(deps=[ModuleMembership, WindowedChurn])
  → Output: velocity(module) → float
  → Formula:
    commits_in_module = Σ_{v in module} commits_w(v, recent_window)
    velocity = commits_in_module / weeks_in_window

ModuleCoordinationCost(deps=[ModuleMembership, GitDiffParser])
  → Output: coordination_cost(module) → float
  → Formula:
    cross_module_commits = |{c : ∃v∈module, w∉module : v,w ∈ files(c)}|
    total_commits = |{c : ∃v∈module : v ∈ files(c)}|
    coordination_cost = cross_module_commits / max(total_commits, 1)

ModuleKnowledgeGini(deps=[ModuleMembership, AuthorStats])
  → Output: knowledge_gini(module) → float
  → Formula:
    author_counts = concat(author_commit_counts(v) for v in module)
    knowledge_gini = Gini(author_counts)

ModuleBusFactor(deps=[ModuleMembership, BusFactor])
  → Output: module_bus_factor(module) → float
  → Formula: min(bus_factor(v) for v in module if pagerank(v) > threshold)

ModuleMeanCognitiveLoad(deps=[ModuleMembership, CognitiveLoad])
  → Output: mean_cognitive_load(module) → float
  → Formula: mean(cognitive_load(v) for v in module)

ModuleHealthScore(deps=[Cohesion, Coupling, MainSequenceDistance, BoundaryAlignment, 
                        RoleConsistency, ModuleMeanCognitiveLoad])
  → Output: health_score(module) → float
  → Formula:
    health_score = 0.20 × cohesion
                 + 0.15 × (1 - coupling)
                 + 0.20 × (1 - main_seq_distance)  [if instability defined]
                 + 0.15 × boundary_alignment
                 + 0.15 × role_consistency
                 + 0.15 × (1 - mean_cognitive_load)
```

---

### Level 21: Percentile Normalization (Depends on Level 6-20)

```
PercentileComputer(deps=[All numeric signals])
  → Output: pctl(signal, value) → float
  → Formula:
    pctl(x) = |{v : signal(v) ≤ x}| / |{v}|
    
    Special case for ABSOLUTE tier (n < 15 files):
      pctl(x) = x / max_value  (linear normalization instead)

EffectivePercentile(deps=[PercentileComputer])
  → Output: eff_pctl(signal, value) → float
  → Formula:
    if value < FLOOR[signal]: return 0.0
    else: return pctl(signal, value)
    
    FLOORS = {
      'pagerank': 0.001,
      'blast_radius': 2,
      'cognitive_load': 3,
    }
```

---

### Level 22: Composite Signals - File (Depends on Level 6-21)

```
RawRisk(deps=[PageRank, BlastRadius, CognitiveLoad, ChurnStats, BusFactor])
  → Output: raw_risk(path) → float
  → Formula:
    raw_risk = 0.25 × pctl(pagerank[IMPORT])
             + 0.20 × pctl(blast_radius_size[IMPORT])
             + 0.20 × pctl(cognitive_load)
             + 0.20 × min(churn_cv / 2, 1)
             + 0.15 × max(0, 1 - bus_factor / 5)

RiskScore(deps=[RawRisk, PagerankVelocity, HiddenCouplingCount, CommunityStability])
  → Output: risk_score(path) → float
  → Formula:
    risk_score = 0.15 × pctl(pagerank[IMPORT])
               + 0.10 × pctl(|pagerank_velocity|)
               + 0.15 × pctl(blast_radius_size[IMPORT])
               + 0.15 × min(churn_cv / 2, 1)
               + 0.15 × max(0, 1 - bus_factor / 5)
               + 0.15 × pctl(hidden_coupling_count)
               + 0.15 × (1 - community_stability)

WiringQuality(deps=[IsOrphan, StubRatio, PhantomImports, HiddenCouplingCount, Degree])
  → Output: wiring_quality(path) → float
  → Formula:
    hidden_ratio = hidden_coupling_count / max(degree[IMPORT], 1)
    wiring_quality = 1 - (
        0.25 × is_orphan[IMPORT]
      + 0.25 × stub_ratio
      + 0.25 × (phantom_import_count / max(import_count, 1))
      + 0.25 × hidden_ratio
    )

FileHealthScore(deps=[RiskScore, WiringQuality, CognitiveLoad, IsOrphan, NeighborhoodCoherence])
  → Output: file_health_score(path) → float
  → Formula:
    file_health_score = 1 - (
        0.25 × risk_score
      + 0.20 × (1 - wiring_quality)
      + 0.20 × pctl(cognitive_load)
      + 0.15 × is_orphan[IMPORT]
      + 0.20 × (1 - neighborhood_coherence)
    )

HealthLaplacian(deps=[FileHealthScore, G_Import])
  → Output: delta_h(path) → float
  → Formula:
    neighbors = {u : (path, u) ∈ E_import or (u, path) ∈ E_import}
    mean_neighbor_health = mean(file_health_score(u) for u in neighbors)
    delta_h = file_health_score(path) - mean_neighbor_health
```

---

### Level 23: Composite Signals - Global (Depends on Level 6-22)

```
OrphanRatio(deps=[IsOrphan])
  → Output: orphan_ratio → float
  → Formula: |{v : is_orphan(v, IMPORT)}| / |files|

PhantomRatio(deps=[ImportResolver])
  → Output: phantom_ratio → float
  → Formula: |{v : phantom_imports(v) ≠ ∅}| / |files|

GlueDeficit(deps=[PageRank, ModuleMembership])
  → Output: glue_deficit → float
  → Formula:
    expected_glue = number_of_module_pairs
    actual_glue = |{(a,b) : module(a)≠module(b) and pagerank(a)+pagerank(b)>threshold}|
    glue_deficit = 1 - actual_glue / expected_glue

CloneRatio(deps=[G_Clone])
  → Output: clone_ratio → float
  → Formula: |{v : ∃u s.t. (v,u) ∈ E_clone}| / |files|

ViolationRate(deps=[LayerViolationCount, ModuleEdges])
  → Output: violation_rate → float
  → Formula: total_layer_violations / total_cross_module_edges

TeamSize(deps=[GitLogParser])
  → Output: team_size → int
  → Formula: |{c.author for c in commits}|

WiringScore(deps=[OrphanRatio, PhantomRatio, GlueDeficit, CloneRatio, 
                   StubRatio, HiddenCouplingCount])
  → Output: wiring_score → float
  → Formula:
    mean_stub = mean(stub_ratio(v) for v in files)
    hidden_ratio = Σ hidden_coupling_count(v) / |E_cochange|
    wiring_score = 1 - (
        0.20 × orphan_ratio
      + 0.20 × phantom_ratio
      + 0.15 × glue_deficit
      + 0.15 × mean_stub
      + 0.15 × clone_ratio
      + 0.15 × hidden_ratio
    )

ArchitectureHealth(deps=[ViolationRate, Cohesion, Coupling, MainSequenceDistance,
                          BoundaryAlignment, MutualInformation, GlobalTrajectory])
  → Output: architecture_health → float
  → Formula:
    architecture_health = 0.15 × (1 - violation_rate)
                        + 0.15 × mean(cohesion)
                        + 0.15 × (1 - mean(coupling))
                        + 0.15 × (1 - mean(main_seq_distance))
                        + 0.10 × mean(boundary_alignment)
                        + 0.15 × behavioral_coherence
                        + 0.15 × (1 - |modularity_trend|)

TeamRisk(deps=[BusFactor, ModuleKnowledgeGini, ModuleCoordinationCost, MutualInformation])
  → Output: team_risk → float
  → Formula:
    min_bus = min(bus_factor(v) for v in files if pagerank(v) > pctl_75)
    team_risk = 1 - (
        0.30 × min(min_bus, 3) / 3
      + 0.25 × (1 - max(knowledge_gini))
      + 0.25 × (1 - mean(coordination_cost))
      + 0.20 × conway_alignment
    )

CodebaseHealth(deps=[ArchitectureHealth, WiringScore, BusFactor, TeamSize,
                      Louvain, MutualInformation, GlobalTrajectory])
  → Output: codebase_health → float
  → Formula:
    codebase_health = 0.20 × architecture_health
                    + 0.20 × wiring_score
                    + 0.15 × (min_bus_factor / team_size)
                    + 0.15 × modularity[IMPORT]
                    + 0.15 × behavioral_coherence
                    + 0.15 × topology_stability
```

---

### Level 24+: Finder Dependencies

Each finder reads specific signals. Here are the exact dependencies:

```
GOD_FILE(deps=[lines, cognitive_load, in_degree[IMPORT]])
  → Condition: lines > 500 AND (cognitive_load > pctl_90 OR in_degree > pctl_90)

ORPHAN_CODE(deps=[is_orphan[IMPORT], role])
  → Condition: is_orphan = true AND role NOT IN (ENTRY, TEST, CONFIG)

PHANTOM_DEPENDENCY(deps=[phantom_import_count])
  → Condition: phantom_import_count > 0

CIRCULAR_DEPENDENCY(deps=[cycle_member])
  → Condition: cycle_member = true

COPY_PASTE_CLONE(deps=[G_Clone])
  → Condition: (a, b) ∈ E_clone

FLAT_ARCHITECTURE(deps=[modularity[IMPORT], centrality_gini[IMPORT]])
  → Condition: modularity < 0.3 AND centrality_gini < 0.3

ZONE_OF_PAIN(deps=[instability, abstractness, main_seq_distance])
  → Condition: main_seq_distance > 0.5 AND instability > 0.7 AND abstractness < 0.3

ZONE_OF_USELESSNESS(deps=[instability, abstractness])
  → Condition: instability < 0.3 AND abstractness > 0.7

LAYER_VIOLATION(deps=[G_Import, LayerAssignments])
  → Condition: (a, b) ∈ E_import AND layer(a) < layer(b)

BOUNDARY_MISMATCH(deps=[boundary_alignment])
  → Condition: boundary_alignment < 0.7

UNSTABLE_INTERFACE(deps=[instability, velocity, abstractness])
  → Condition: instability > 0.7 AND velocity > pctl_75 AND abstractness > 0.5

RIGID_CORE(deps=[instability, coupling, file_count])
  → Condition: instability < 0.2 AND coupling > 0.5 AND file_count > 10

HIGH_RISK_HUB(deps=[pagerank[IMPORT], churn_cv, bus_factor, risk_score])
  → Condition: pagerank > pctl_90 AND (churn_cv > 1.0 OR bus_factor < 2)

HIDDEN_COUPLING(deps=[PairSignals.hidden_coupling])
  → Condition: hidden_coupling(a, b) > threshold

CONWAY_VIOLATION(deps=[PairSignals.conway_violation])
  → Condition: conway_violation(a, b) > threshold

WEAK_LINK(deps=[delta_h, file_health_score])
  → Condition: delta_h > 0.4

ACCIDENTAL_COUPLING(deps=[PairSignals.semantic_mismatch])
  → Condition: semantic_mismatch(a, b) > threshold AND NOT has_import(a, b)

KNOWLEDGE_SILO(deps=[knowledge_gini, module_bus_factor])
  → Condition: knowledge_gini > 0.7 OR module_bus_factor < 1.5

UNSTABLE_FILE(deps=[churn_cv, churn_trajectory, total_changes])
  → Condition: churn_trajectory IN (CHURNING, SPIKING) AND total_changes > median

BUS_FACTOR_RISK(deps=[bus_factor, pagerank[IMPORT]])
  → Condition: bus_factor < 1.5 AND pagerank > pctl_75

HOLLOW_CODE(deps=[stub_ratio, function_count])
  → Condition: stub_ratio > 0.5 AND function_count > 3

CHRONIC_PROBLEM(deps=[finding_lifecycle])
  → Condition: finding exists in >= 3 consecutive snapshots
```

---

## 4. DAG Summary

### 4.1 Level Summary

| Level | Computation Type | Count | Dependencies |
|-------|------------------|-------|--------------|
| 0 | Raw inputs | 2 | None |
| 1 | Parsing | 4 | Level 0 |
| 2 | Derived parsing | 6 | Level 1 |
| 3 | Graph construction | 5 | Level 1-2 |
| 4 | Graph fusion | 2 | Level 3 |
| 5 | Historical sampling | 1 | Level 3 |
| 6 | Adjacency/Degree | 3 | Level 3-4 |
| 7 | PageRank | 2 | Level 6 |
| 8 | Community | 2 | Level 6-7 |
| 9 | Spectral | 3 | Level 6 |
| 10 | Structural | 4 | Level 3, 6 |
| 11 | Distribution | 2 | Level 7 |
| 12 | Temporal basic | 2 | Level 1-2 |
| 13 | Temporal windowed | 8 | Level 12 |
| 14 | Semantic | 6 | Level 2 |
| 15 | Cognitive load | 2 | Level 1-2, 6 |
| 16 | Trajectory | 6 | Level 5, 7, 8 |
| 17 | Cross-layer global | 1 | Level 3 |
| 18 | Cross-layer node | 5 | Level 3, 6 |
| 19 | Cross-layer pair | 1 | Level 3 |
| 20 | Module signals | 14 | Level 3, 6, 14 |
| 21 | Percentiles | 2 | Level 6-20 |
| 22 | File composites | 5 | Level 6-21 |
| 23 | Global composites | 9 | Level 6-22 |
| 24+ | Finders | 22 | Various |

### 4.2 Critical Path

The longest dependency chain (critical path) determines minimum pipeline time:

```
FileSystem → FileParser → ImportResolver → G_Import → AdjacencyMatrix 
  → TransitionMatrix → PageRank → CentralityDistribution → GiniCoefficient
  → PercentileComputer → RawRisk → RiskScore → FileHealthScore 
  → HealthLaplacian → CodebaseHealth → HIGH_RISK_HUB

Total depth: ~15 levels
```

### 4.3 Parallelization Opportunities

**Can run in parallel:**
- All file parsing (Level 1)
- All graph construction (Level 3) - G_Import, G_Cochange, G_Author, G_Semantic, G_Clone
- Graph algorithms per relationship type (Level 6-11)
- All per-file signal computation (Level 12-15, 18)
- All finders (Level 24+)

**Must be sequential:**
- Level 4 requires all Level 3 graphs
- Level 16 requires historical snapshots
- Level 21 requires all signals
- Level 22-23 require percentiles

### 4.4 Data Flow Diagram

```
                                    ┌─────────────────────────────────────────────┐
                                    │              Level 0: Inputs               │
                                    │  FileSystem │ GitRepository               │
                                    └──────┬──────────────┬─────────────────────┘
                                           │              │
                    ┌──────────────────────┴──────────────┴──────────────────────┐
                    │                  Level 1: Parsing                           │
                    │  FileParser │ ContentHash │ GitLogParser │ GitDiffParser   │
                    └──────┬─────────────┬─────────────┬───────────────┬─────────┘
                           │             │             │               │
          ┌────────────────┴─────────┐   │   ┌─────────┴───────────────┴────────┐
          │    Level 2: Derived      │   │   │     Level 1b: Temporal Events    │
          │  ImportResolver          │   │   │  EventBuilder │ NodeLifecycle    │
          │  CyclomaticComplexity    │   │   │  TimeWindowBuilder              │
          │  FunctionSizeStats       │   │   └──────────────┬──────────────────┘
          │  ImplGini │ StubRatio    │   │                  │
          └───────┬──────────────────┘   │                  │
                  │                      │                  │
                  └──────────────────────┼──────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │           Level 3: Graph Construction (Parallel)              │
         │                                                               │
         │  ┌────────────┐ ┌─────────────┐ ┌────────────┐ ┌───────────┐ │
         │  │ G_Import   │ │ G_Cochange  │ │ G_Author   │ │ G_Semantic│ │
         │  └─────┬──────┘ └──────┬──────┘ └─────┬──────┘ └─────┬─────┘ │
         │        │               │               │              │       │
         │        └───────────────┴───────────────┴──────────────┘       │
         │                                │                              │
         │                     ┌──────────┴──────────┐                   │
         │                     │ G_Combined (Level 4)│                   │
         │                     └──────────┬──────────┘                   │
         └────────────────────────────────┼──────────────────────────────┘
                                          │
         ┌────────────────────────────────┼────────────────────────────────┐
         │                 Level 6-11: Graph Algorithms (Per Graph)       │
         │                                                                │
         │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
         │  │AdjacencyMatrix│ │TransitionMat│ │   Laplacian   │           │
         │  └───────┬──────┘ └──────┬───────┘ └───────┬──────┘           │
         │          │               │                 │                   │
         │          ▼               ▼                 ▼                   │
         │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
         │  │   Degree     │ │  PageRank    │ │   Spectral   │           │
         │  │   IsOrphan   │ │              │ │ Decomposition│           │
         │  └───────┬──────┘ └──────┬───────┘ └───────┬──────┘           │
         │          │               │                 │                   │
         │          ▼               ▼                 ▼                   │
         │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
         │  │     SCC      │ │   Louvain    │ │    Fiedler   │           │
         │  │ BlastRadius  │ │  Community   │ │ SpectralGap  │           │
         │  │    Depth     │ │  Modularity  │ │              │           │
         │  └───────┬──────┘ └──────┬───────┘ └───────┬──────┘           │
         │          │               │                 │                   │
         │          └───────────────┴─────────────────┘                   │
         │                          │                                     │
         │                          ▼                                     │
         │                  ┌──────────────┐                              │
         │                  │GiniCoefficient│                             │
         │                  └───────┬──────┘                              │
         └──────────────────────────┼──────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────────────────┐
         │               Level 12-16: Temporal & Trajectory               │
         │                                                                  │
         │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
         │  │CommitCounts  │ │WindowedChurn │ │AuthorEntropy │            │
         │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
         │         │                │                │                     │
         │         ▼                ▼                ▼                     │
         │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
         │  │ChurnStats    │ │ChurnTrajectory│ │  BusFactor   │            │
         │  │ChurnTrend    │ └──────┬───────┘ └──────┬───────┘            │
         │  └──────┬───────┘        │                │                     │
         │         │                └────────────────┘                     │
         │         │                       │                               │
         │         └───────────────────────┼───────────────────────────────┤
         │                                 │                               │
         │                                 ▼                               │
         │                    ┌────────────────────────┐                   │
         │                    │ Level 16: Trajectory   │                   │
         │                    │ PagerankVelocity       │                   │
         │                    │ CommunityStability     │                   │
         │                    │ GlobalTrajectory       │                   │
         │                    └───────────┬────────────┘                   │
         └────────────────────────────────┼────────────────────────────────┘
                                          │
         ┌────────────────────────────────┼────────────────────────────────┐
         │            Level 17-19: Cross-Layer Analysis                    │
         │                                                                 │
         │  ┌──────────────────────┐    ┌──────────────────────┐          │
         │  │ MutualInformation    │    │ NeighborhoodSets     │          │
         │  │ behavioral_coherence │    │ HiddenCouplingCount  │          │
         │  │ conway_alignment     │    │ NeighborhoodCoherence│          │
         │  └──────────┬───────────┘    └──────────┬───────────┘          │
         │             │                           │                       │
         │             └───────────┬───────────────┘                       │
         │                         │                                       │
         │                         ▼                                       │
         │              ┌──────────────────────┐                          │
         │              │    PairSignals       │                          │
         │              │ hidden_coupling(pairs)│                          │
         │              │ conway_violation     │                          │
         │              └──────────┬───────────┘                          │
         └─────────────────────────┼───────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼───────────────────────────────────────┐
         │               Level 20: Module Signals                         │
         │                                                                  │
         │  Cohesion │ Coupling │ Instability │ Abstractness              │
         │  MainSeqDistance │ BoundaryAlignment │ RoleConsistency         │
         │  ModuleVelocity │ CoordinationCost │ KnowledgeGini            │
         │                         │                                       │
         │                         ▼                                       │
         │                 ModuleHealthScore                               │
         └─────────────────────────┬───────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼───────────────────────────────────────┐
         │             Level 21: Percentile Normalization                  │
         │                                                                  │
         │              PercentileComputer │ EffectivePercentile           │
         │                         │                                       │
         └─────────────────────────┼───────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼───────────────────────────────────────┐
         │            Level 22-23: Composite Signals                       │
         │                                                                  │
         │  ┌──────────────────────────────────────────────────────────┐  │
         │  │ Level 22: File Composites                                │  │
         │  │                                                          │  │
         │  │ RawRisk → RiskScore → WiringQuality → FileHealthScore   │  │
         │  │                              ↓                           │  │
         │  │                        HealthLaplacian                    │  │
         │  └──────────────────────────────┬───────────────────────────┘  │
         │                                 │                               │
         │                                 ▼                               │
         │  ┌──────────────────────────────────────────────────────────┐  │
         │  │ Level 23: Global Composites                              │  │
         │  │                                                          │  │
         │  │ OrphanRatio │ PhantomRatio │ GlueDeficit │ CloneRatio   │  │
         │  │ ViolationRate │ TeamSize                                  │  │
         │  │         ↓                                                │  │
         │  │ WiringScore → ArchitectureHealth → TeamRisk              │  │
         │  │         ↓                          ↓                      │  │
         │  │         └────────────────────────────┐                    │  │
         │  │                                      ▼                    │  │
         │  │                            CodebaseHealth                 │  │
         │  └──────────────────────────────────────────────────────────┘  │
         └─────────────────────────┬───────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼───────────────────────────────────────┐
         │                 Level 24+: Finders (22 patterns)               │
         │                                                                  │
         │  ┌─────────────────────────────────────────────────────────┐   │
         │  │ Wave 1: Structural (Parallel)                           │   │
         │  │ GOD_FILE │ ORPHAN_CODE │ PHANTOM_DEPENDENCY            │   │
         │  │ CIRCULAR_DEPENDENCY │ COPY_PASTE_CLONE │ FLAT_ARCHITECTURE│   │
         │  └─────────────────────────────────────────────────────────┘   │
         │                                                                  │
         │  ┌─────────────────────────────────────────────────────────┐   │
         │  │ Wave 2: Architecture (Parallel, depends on modules)     │   │
         │  │ ZONE_OF_PAIN │ ZONE_OF_USELESSNESS │ LAYER_VIOLATION    │   │
         │  │ BOUNDARY_MISMATCH │ UNSTABLE_INTERFACE │ RIGID_CORE     │   │
         │  └─────────────────────────────────────────────────────────┘   │
         │                                                                  │
         │  ┌─────────────────────────────────────────────────────────┐   │
         │  │ Wave 3: Cross-Dimensional (Parallel)                    │   │
         │  │ HIGH_RISK_HUB │ HIDDEN_COUPLING │ CONWAY_VIOLATION      │   │
         │  │ WEAK_LINK │ ACCIDENTAL_COUPLING │ KNOWLEDGE_SILO        │   │
         │  └─────────────────────────────────────────────────────────┘   │
         │                                                                  │
         │  ┌─────────────────────────────────────────────────────────┐   │
         │  │ Wave 4: Temporal/Quality (Parallel)                     │   │
         │  │ UNSTABLE_FILE │ BUS_FACTOR_RISK │ HOLLOW_CODE           │   │
         │  │ CHRONIC_PROBLEM                                          │   │
         │  └─────────────────────────────────────────────────────────┘   │
         └──────────────────────────────────────────────────────────────────┘
```

---

## 5. Verification Checklist

To verify this DAG is correct:

- [ ] **Acyclicity**: No computation depends on itself transitively
- [ ] **Completeness**: Every signal in the framework has a computation node
- [ ] **Correctness**: Each formula matches the framework definition
- [ ] **Minimality**: No unnecessary dependencies
- [ ] **Implementability**: Each node maps to code

---

## Appendix: Computation Node Index

| Node ID | Name | Level | Outputs | Dependencies |
|---------|------|-------|---------|--------------|
| 0.1 | FileSystem | 0 | file_content | - |
| 0.2 | GitRepository | 0 | commits | - |
| 1.1 | FileParser | 1 | syntax signals | 0.1 |
| 1.2 | ContentHash | 1 | content_hash | 0.1 |
| 1.3 | GitLogParser | 1 | commit metadata | 0.2 |
| 1.4 | GitDiffParser | 1 | file changes | 0.2 |
| 2.1 | ImportResolver | 2 | resolved_imports, phantom | 1.1, 0.1 |
| 2.2 | CyclomaticComplexity | 2 | complexity | 1.1 |
| 2.3 | FunctionSizeStats | 2 | function_sizes, stub_count | 1.1 |
| 2.4 | ImplGini | 2 | impl_gini | 2.3 |
| 2.5 | StubRatio | 2 | stub_ratio | 2.3, 1.1 |
| 2.6 | EventBuilder | 2 | events | 1.3, 1.4 |
| 2.7 | NodeLifecycle | 2 | birth_ts, death_ts | 2.6 |
| 2.8 | TimeWindowBuilder | 2 | time_windows | 1.3 |
| 3.1 | G_Import | 3 | E_import, W_import | 2.1 |
| 3.2 | G_Cochange | 3 | E_cochange, W_cochange | 2.8, 1.4 |
| 3.3 | G_Author | 3 | E_author, W_author | 1.3, 1.4 |
| 3.4 | G_Semantic | 3 | E_semantic, W_semantic | 4.1 |
| 3.5 | G_Clone | 3 | E_clone, W_clone | 0.1, 1.2 |
| 4.1 | ConceptExtractor | 3 | concepts | 1.1, 0.1 |
| 4.2 | GraphNormalizer | 4 | normalized weights | 3.1-3.4 |
| 4.3 | G_Combined | 4 | E_combined, W_combined | 4.2 |
| 5.1 | GraphHistorySampler | 5 | historical graphs | 3.1, 3.2, 2.7, 2.6 |
| 6.1 | AdjacencyMatrix | 6 | A, D | 3.1-4.3 |
| 6.2 | Degree | 6 | in_degree, out_degree | 6.1 |
| 6.3 | IsOrphan | 6 | is_orphan | 6.2 |
| 7.1 | TransitionMatrix | 7 | P | 6.1 |
| 7.2 | PageRank | 7 | pagerank | 7.1 |
| 8.1 | Louvain | 8 | community, modularity | 6.1 |
| 8.2 | CommunitySizes | 8 | community_size | 8.1 |
| 9.1 | Laplacian | 9 | L | 6.1 |
| 9.2 | NormalizedLaplacian | 9 | L_norm | 9.1, 6.1 |
| 9.3 | SpectralDecomposition | 9 | fiedler, spectral_gap | 9.2 |
| 10.1 | SCCDetection | 10 | cycle_member, cycle_size | 3.1 |
| 10.2 | BFS_Depth | 10 | depth | 3.1, 14.1 |
| 10.3 | TransitiveClosure | 10 | reachable_from | 3.1 |
| 10.4 | BlastRadius | 10 | blast_radius_size | 10.3 |
| 11.1 | CentralityDistribution | 11 | pagerank_values | 7.2 |
| 11.2 | GiniCoefficient | 11 | centrality_gini | 11.1 |
| 12.1 | CommitCounts | 12 | total_changes, additions, deletions | 1.4, 2.7 |
| 12.2 | AuthorStats | 12 | total_authors, author_counts | 1.3, 1.4 |
| 13.1 | WindowedChurn | 13 | churn_w, commits_w | 1.4, 2.8 |
| 13.2 | WindowedAuthors | 13 | authors_w | 12.2, 2.8 |
| 13.3 | ChurnStats | 13 | churn_mean, churn_std, churn_cv | 13.1 |
| 13.4 | ChurnTrend | 13 | churn_trend | 13.1 |
| 13.5 | ChurnTrajectory | 13 | churn_trajectory | 13.3, 13.4, 12.1 |
| 13.6 | AuthorEntropy | 13 | author_entropy | 12.2 |
| 13.7 | BusFactor | 13 | bus_factor | 13.6 |
| 13.8 | CommitClassification | 13 | fix_commits, refactor_commits | 1.3 |
| 13.9 | CommitRatios | 13 | fix_ratio, refactor_ratio | 13.8, 12.1 |
| 13.10 | ChangeEntropy | 13 | change_entropy | 13.1 |
| 14.1 | RoleClassifier | 14 | role | 1.1, 2.1, 2.3 |
| 14.2 | ConceptStats | 14 | concept_count, concept_entropy | 4.1 |
| 14.3 | SemanticCoherence | 14 | semantic_coherence | 14.2 |
| 14.4 | NamingDrift | 14 | naming_drift | 1.1 |
| 14.5 | TodoDensity | 14 | todo_density | 1.1 |
| 14.6 | DocstringCoverage | 14 | docstring_coverage | 1.1 |
| 15.1 | CognitiveLoad | 15 | cognitive_load | 1.1, 2.3, 2.4, 6.2 |
| 15.2 | CompressionRatio | 15 | compression_ratio | 0.1 |
| 16.1 | SignalHistory | 16 | pagerank_history, community_history | 5.1, 7.2, 8.1 |
| 16.2 | PagerankVelocity | 16 | pagerank_velocity | 16.1 |
| 16.3 | PagerankAcceleration | 16 | pagerank_acceleration | 16.2 |
| 16.4 | CommunityStability | 16 | community_changes, community_stability | 16.1 |
| 16.5 | CentralityTrend | 16 | centrality_trend | 16.1 |
| 16.6 | GlobalTrajectory | 16 | graph_velocity, fiedler_trend, etc. | 5.1, 9.3, 8.1 |
| 17.1 | MutualInformation | 17 | behavioral_coherence, conway_alignment | 3.1-3.4 |
| 18.1 | NeighborhoodSets | 18 | N_import, N_cochange, N_author | 3.1-3.3 |
| 18.2 | HiddenCouplingCount | 18 | hidden_coupling_count | 18.1 |
| 18.3 | DeadImportCount | 18 | dead_import_count | 18.1 |
| 18.4 | ConwayViolationCount | 18 | conway_violation_count | 18.1 |
| 18.5 | NeighborhoodCoherence | 18 | neighborhood_coherence | 18.1 |
| 19.1 | PairSignals | 19 | pair-level cross-layer signals | 3.1-3.4 |
| 20.1 | ModuleMembership | 20 | module | 0.1 |
| 20.2 | ModuleEdges | 20 | internal/external edges | 3.1, 20.1 |
| 20.3 | Cohesion | 20 | cohesion | 20.2, 20.1 |
| 20.4 | Coupling | 20 | coupling | 20.2 |
| 20.5 | Instability | 20 | instability, Ce, Ca | 20.2 |
| 20.6 | Abstractness | 20 | abstractness | 20.1, 14.1 |
| 20.7 | MainSequenceDistance | 20 | main_seq_distance | 20.5, 20.6 |
| 20.8 | BoundaryAlignment | 20 | boundary_alignment | 20.1, 8.1 |
| 20.9 | LayerViolationCount | 20 | layer_violation_count | 3.1, LayerAssignments |
| 20.10 | RoleConsistency | 20 | role_consistency | 20.1, 14.1 |
| 20.11 | ModuleVelocity | 20 | velocity | 20.1, 13.1 |
| 20.12 | ModuleCoordinationCost | 20 | coordination_cost | 20.1, 1.4 |
| 20.13 | ModuleKnowledgeGini | 20 | knowledge_gini | 20.1, 12.2 |
| 20.14 | ModuleBusFactor | 20 | module_bus_factor | 20.1, 13.7 |
| 20.15 | ModuleMeanCognitiveLoad | 20 | mean_cognitive_load | 20.1, 15.1 |
| 20.16 | ModuleHealthScore | 20 | module health_score | 20.3-20.8, 20.15 |
| 21.1 | PercentileComputer | 21 | pctl | 6.2-20.16 |
| 21.2 | EffectivePercentile | 21 | eff_pctl | 21.1 |
| 22.1 | RawRisk | 22 | raw_risk | 7.2, 10.4, 15.1, 13.3, 13.7 |
| 22.2 | RiskScore | 22 | risk_score | 22.1, 16.2, 18.2, 16.4 |
| 22.3 | WiringQuality | 22 | wiring_quality | 6.3, 2.5, 2.1, 18.2, 6.2 |
| 22.4 | FileHealthScore | 22 | file_health_score | 22.2, 22.3, 15.1, 6.3, 18.5 |
| 22.5 | HealthLaplacian | 22 | delta_h | 22.4, 3.1 |
| 23.1 | OrphanRatio | 23 | orphan_ratio | 6.3 |
| 23.2 | PhantomRatio | 23 | phantom_ratio | 2.1 |
| 23.3 | GlueDeficit | 23 | glue_deficit | 7.2, 20.1 |
| 23.4 | CloneRatio | 23 | clone_ratio | 3.5 |
| 23.5 | ViolationRate | 23 | violation_rate | 20.9, 20.2 |
| 23.6 | TeamSize | 23 | team_size | 1.3 |
| 23.7 | WiringScore | 23 | wiring_score | 23.1-23.4, 2.5, 18.2 |
| 23.8 | ArchitectureHealth | 23 | architecture_health | 23.5, 20.3-20.8, 17.1, 16.6 |
| 23.9 | TeamRisk | 23 | team_risk | 13.7, 20.13, 20.12, 17.1 |
| 23.10 | CodebaseHealth | 23 | codebase_health | 23.8, 23.7, 13.7, 23.6, 8.1, 17.1, 16.6 |
| 24.1-24.22 | Finders | 24+ | findings | Various |

---

*End of Document*
