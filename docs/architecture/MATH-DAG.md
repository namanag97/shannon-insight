# Mathematical Computation DAG

This document specifies every computation in Shannon Insight as a node in a directed acyclic graph. Each node declares:
- **REQUIRES**: Inputs that must exist
- **PRODUCES**: Outputs created
- **FORMULA**: The exact mathematical transformation

---

## Notation

| Symbol | Meaning |
|--------|---------|
| N | Number of files |
| K | Number of time windows |
| R | Number of relationship types (5) |
| T | The core tensor ∈ ℝ^(N×N×K×R) |
| G_r | Graph slice T[:,:,now,r] |
| A | Adjacency matrix |
| D | Degree matrix (diagonal) |
| L | Laplacian matrix (D - A) |

---

## Level 0: Raw Data

### 0.1 Filesystem Scan

```
REQUIRES:
  - repo_path: str
  - exclude_patterns: List[str]

PRODUCES:
  - file_list: Set[str]
  - file_content: Dict[str, bytes]
  - file_size: Dict[str, int]

METHOD: os.walk with pattern filtering
```

### 0.2 Git Log Extraction

```
REQUIRES:
  - repo_path: str
  - max_commits: int (default 10000)

PRODUCES:
  - commits: List[Commit]
      Commit = {hash, timestamp, author_email, subject, parent_hashes}
  - file_changes: List[FileChange]
      FileChange = {commit_hash, path, change_type, additions, deletions}

METHOD: git log --format='%H|%at|%ae|%s' --numstat
```

### 0.3 Rename Detection

```
REQUIRES:
  - file_changes from 0.2

PRODUCES:
  - renames: Dict[old_path, new_path]
  - file_id: Dict[current_path, stable_uuid]

METHOD:
  For change_type = 'R':
    file_id[new_path] = file_id[old_path]
    renames[old_path] = new_path
```

### 0.4 Author Normalization

```
REQUIRES:
  - commits from 0.2
  - .mailmap file (optional)

PRODUCES:
  - author_canonical: Dict[email, canonical_id]

METHOD: Parse .mailmap, group by email domain + name similarity
```

---

## Level 1: Syntax Extraction

### 1.1 Language Detection

```
REQUIRES:
  - file_list from 0.1
  - file_content from 0.1

PRODUCES:
  - language: Dict[path, str]

METHOD:
  1. Check file extension (.py → 'python', .go → 'go', etc.)
  2. Check shebang line for scripts
  3. Fallback to 'unknown'
```

### 1.2 AST Parsing

```
REQUIRES:
  - file_content from 0.1
  - language from 1.1

PRODUCES:
  - content_hash: Dict[path, sha256]
  - parsed_syntax: Dict[content_hash, ParsedSyntax]
      ParsedSyntax = {
        language, lines, tokens, complexity,
        functions: List[Function],
        classes: List[Class],
        imports: List[Import],
        identifiers: Set[str],
        max_nesting: int,
        has_main_guard: bool
      }

CACHING: If content_hash exists in cache, skip parsing
```

### 1.3 Import Extraction

```
REQUIRES:
  - parsed_syntax from 1.2

PRODUCES:
  - import_names: Dict[path, List[ImportInfo]]
      ImportInfo = {module, names, level, lineno}

FORMULA:
  Python: from X import Y → ImportInfo(module=X, names=[Y], level=0)
  Python: from .X import Y → ImportInfo(module=X, names=[Y], level=1)
  Go: import "pkg/path" → ImportInfo(module="pkg/path", names=[], level=0)
```

### 1.4 Identifier Extraction

```
REQUIRES:
  - parsed_syntax from 1.2

PRODUCES:
  - identifiers: Dict[path, Set[str]]
  - function_calls: Dict[path, List[str]]

METHOD:
  1. Extract all Name nodes from AST
  2. Split camelCase/snake_case: getUserData → [get, user, data]
  3. Lowercase and remove stopwords
```

### 1.5 Complexity Metrics

```
REQUIRES:
  - parsed_syntax from 1.2

PRODUCES:
  - lines: Dict[path, int]
  - complexity: Dict[path, int]
  - max_nesting: Dict[path, int]
  - function_count: Dict[path, int]
  - class_count: Dict[path, int]

FORMULA:
  complexity = 1 + count(if, for, while, case, &&, ||, try, except)
  max_nesting = max depth of nested control structures
```

### 1.6 Stub Detection

```
REQUIRES:
  - parsed_syntax from 1.2

PRODUCES:
  - stub_ratio: Dict[path, float]
  - impl_gini: Dict[path, float]

FORMULA:
  is_stub(fn) = body_tokens < 5 OR body matches (pass | ... | return None)
  stub_ratio = count(is_stub) / count(functions)

  impl_gini (function size distribution):
    sizes = sorted([fn.body_tokens for fn in functions])
    G = (2 × Σᵢ i × sizes[i]) / (n × Σ sizes) - (n+1)/n
```

---

## Level 2: Resolution & Concepts

### 2.1 Import Resolution

```
REQUIRES:
  - import_names from 1.3
  - file_list from 0.1

PRODUCES:
  - resolved_imports: Dict[path, Dict[import_name, resolved_path | None]]
  - unresolved_imports: Dict[path, Set[str]]

METHOD:
  For each import in file:
    1. Handle relative imports (level > 0 means go up directories)
    2. Try: module_name + ".py"
    3. Try: module_name + "/__init__.py"
    4. If not found in file_list → unresolved (third-party or phantom)
```

### 2.2 Concept Extraction (TF-IDF)

```
REQUIRES:
  - identifiers from 1.4
  - file_list from 0.1

PRODUCES:
  - concept_vectors: Dict[path, np.ndarray]  # TF-IDF vectors
  - concepts: Dict[path, List[(term, weight)]]

FORMULA:
  TF(term, file) = count(term, file) / total_terms(file)
  IDF(term) = log(N / |{files containing term}|)
  TF-IDF(term, file) = TF × IDF

  concepts[file] = top-k terms by TF-IDF score
```

### 2.3 Concept Entropy

```
REQUIRES:
  - concepts from 2.2

PRODUCES:
  - concept_entropy: Dict[path, float]
  - concept_count: Dict[path, int]

FORMULA:
  weights = [w for (term, w) in concepts[file]]
  total = sum(weights)
  p = [w / total for w in weights]

  H = -Σ p_i × log₂(p_i)

  concept_count = len(concepts[file])
```

### 2.4 Role Classification

```
REQUIRES:
  - parsed_syntax from 1.2
  - concepts from 2.2
  - resolved_imports from 2.1

PRODUCES:
  - role: Dict[path, Role]
      Role ∈ {ENTRY_POINT, TEST, MODEL, SERVICE, CONFIG, UTILITY, UNKNOWN}

METHOD (first match wins):
  1. has_main_guard AND out_degree > 0 → ENTRY_POINT
  2. filename matches test_*.py or *_test.py → TEST
  3. all functions are stubs or abstract → INTERFACE
  4. only dataclass/namedtuple definitions → MODEL
  5. has @app.route or @celery.task → SERVICE
  6. all caps identifiers > 80% → CONSTANT
  7. else → UTILITY
```

### 2.5 Semantic Coherence

```
REQUIRES:
  - concept_entropy from 2.3

PRODUCES:
  - semantic_coherence: Dict[path, float]  # [0, 1]

FORMULA:
  semantic_coherence = 1 / (1 + concept_entropy)

  Interpretation:
    High entropy = many diverse concepts = low coherence
    Low entropy = focused on few concepts = high coherence
```

---

## Level 3: Temporal Signals

### 3.1 Time Window Partitioning

```
REQUIRES:
  - commits from 0.2
  - window_size: int (default 30 days = 2592000 seconds)

PRODUCES:
  - windows: List[TimeWindow]
      TimeWindow = {index, start_ts, end_ts, commits}

METHOD:
  min_ts = min(commit.timestamp)
  max_ts = max(commit.timestamp)

  For i in range(K):
    windows[i] = {
      start_ts: min_ts + i * window_size,
      end_ts: min_ts + (i+1) * window_size,
      commits: [c for c in commits if c.timestamp in range]
    }
```

### 3.2 Churn Series

```
REQUIRES:
  - windows from 3.1
  - file_changes from 0.2

PRODUCES:
  - churn: Dict[path, ChurnSeries]
      ChurnSeries = {
        window_counts: List[int],
        total_changes: int,
        cv: float,
        slope: float,
        trajectory: str
      }

FORMULA:
  window_counts[t] = count(changes to file in window t)
  total_changes = sum(window_counts)

  μ = mean(window_counts)
  σ = std(window_counts)
  cv = σ / max(μ, 1)  # coefficient of variation

  slope = linear_regression_slope(window_counts vs time)

  Trajectory classification:
    DORMANT: total_changes ≤ 1 OR cv = 0
    STABILIZING: slope < -0.1 AND cv < 0.5
    SPIKING: slope > 0.1 AND cv > 0.5
    CHURNING: cv > 0.5
    STABLE: cv ≤ 0.5 AND |slope| < 0.1
```

### 3.3 Author Statistics

```
REQUIRES:
  - commits from 0.2
  - file_changes from 0.2
  - author_canonical from 0.4

PRODUCES:
  - authors_per_file: Dict[path, Dict[author, int]]
  - author_entropy: Dict[path, float]
  - bus_factor: Dict[path, float]

FORMULA:
  For each file:
    author_commits[author] = count(commits by author touching file)
    total = sum(author_commits.values())

    p[author] = author_commits[author] / total
    H = -Σ p × log₂(p)

    author_entropy = H
    bus_factor = 2^H

  Interpretation:
    bus_factor = 1 → single author
    bus_factor = k → k "equivalent" authors
```

### 3.4 Commit Classification

```
REQUIRES:
  - commits from 0.2

PRODUCES:
  - fix_commits: Dict[path, int]
  - refactor_commits: Dict[path, int]
  - fix_ratio: Dict[path, float]
  - refactor_ratio: Dict[path, float]

METHOD:
  fix_keywords = ["fix", "bug", "patch", "issue", "error", "crash"]
  refactor_keywords = ["refactor", "clean", "restructure", "rename", "move"]

  For each commit touching file:
    subject_lower = commit.subject.lower()
    if any(kw in subject_lower for kw in fix_keywords):
      fix_commits[file] += 1
    if any(kw in subject_lower for kw in refactor_keywords):
      refactor_commits[file] += 1

  fix_ratio = fix_commits / max(total_commits, 1)
  refactor_ratio = refactor_commits / max(total_commits, 1)
```

### 3.5 Co-Change Counts

```
REQUIRES:
  - commits from 0.2
  - file_changes from 0.2

PRODUCES:
  - cochange_counts: Dict[(path_a, path_b), int]
  - file_counts: Dict[path, int]

METHOD:
  decay_lambda = ln(2) / 90  # 90-day half-life

  For each commit:
    Skip if |commit.files| > 50 (bulk changes)

    days_ago = (now - commit.timestamp) / 86400
    weight = exp(-decay_lambda × days_ago)

    For each file in commit:
      file_counts[file] += weight

    For each pair (a, b) in commit.files where a < b:
      cochange_counts[(a, b)] += weight
```

### 3.6 Co-Change Metrics

```
REQUIRES:
  - cochange_counts from 3.5
  - file_counts from 3.5
  - total_commits from 0.2

PRODUCES:
  - cochange_lift: Dict[(path_a, path_b), float]
  - cochange_confidence: Dict[(path_a, path_b), (float, float)]

FORMULA:
  For (a, b) with cochange_counts[(a, b)] >= 3:

    P_ab = cochange_counts[(a, b)] / total_commits
    P_a = file_counts[a] / total_commits
    P_b = file_counts[b] / total_commits

    lift = P_ab / (P_a × P_b)

    confidence_a_b = cochange_counts[(a, b)] / file_counts[a]
    confidence_b_a = cochange_counts[(a, b)] / file_counts[b]

  Interpretation:
    lift > 1 → more co-change than random
    lift = 2 → 2× more likely to change together
```

---

## Level 4: Tensor Population

### 4.1 Node Index

```
REQUIRES:
  - file_list from 0.1

PRODUCES:
  - node_index: Dict[path, int]
  - index_node: Dict[int, path]

METHOD:
  Sort file_list alphabetically
  node_index = {path: i for i, path in enumerate(sorted(file_list))}
  index_node = {i: path for path, i in node_index.items()}
```

### 4.2 IMPORT Layer (R=0)

```
REQUIRES:
  - resolved_imports from 2.1
  - node_index from 4.1

PRODUCES:
  - T[:,:,t,0] for all time windows t

FORMULA:
  For each (source, target) in resolved_imports:
    i = node_index[source]
    j = node_index[target]
    T[i, j, :, 0] = 1.0  # Static across time (current state)
```

### 4.3 COCHANGE Layer (R=1)

```
REQUIRES:
  - cochange_lift from 3.6
  - windows from 3.1
  - node_index from 4.1

PRODUCES:
  - T[:,:,t,1] for all time windows t

FORMULA:
  For each window t:
    For each (a, b) with lift > 1.0:
      i, j = node_index[a], node_index[b]
      T[i, j, t, 1] = lift_in_window_t
      T[j, i, t, 1] = lift_in_window_t  # Symmetric
```

### 4.4 AUTHOR Layer (R=2)

```
REQUIRES:
  - authors_per_file from 3.3
  - windows from 3.1
  - node_index from 4.1

PRODUCES:
  - T[:,:,t,2] for all time windows t

FORMULA:
  For each pair (a, b):
    authors_a = set(authors_per_file[a].keys())
    authors_b = set(authors_per_file[b].keys())

    jaccard = |authors_a ∩ authors_b| / |authors_a ∪ authors_b|

    if jaccard > 0.1:
      i, j = node_index[a], node_index[b]
      T[i, j, :, 2] = jaccard
      T[j, i, :, 2] = jaccard  # Symmetric
```

### 4.5 SEMANTIC Layer (R=3)

```
REQUIRES:
  - concept_vectors from 2.2
  - node_index from 4.1

PRODUCES:
  - T[:,:,t,3] for all time windows t

FORMULA:
  For each pair (a, b):
    v_a = concept_vectors[a]
    v_b = concept_vectors[b]

    cosine = (v_a · v_b) / (‖v_a‖ × ‖v_b‖)

    if cosine > 0.3:
      i, j = node_index[a], node_index[b]
      T[i, j, :, 3] = cosine
      T[j, i, :, 3] = cosine  # Symmetric
```

### 4.6 COMBINED Layer (R=4)

```
REQUIRES:
  - T[:,:,:,0:4] from 4.2-4.5

PRODUCES:
  - T[:,:,t,4] for all time windows t

FORMULA:
  weights = [0.4, 0.3, 0.2, 0.1]  # import, cochange, author, semantic

  For each (i, j, t):
    T[i, j, t, 4] = Σᵣ weights[r] × T[i, j, t, r]
```

---

## Level 5: Graph Algorithms

### 5.1 PageRank

```
REQUIRES:
  - T[:,:,t,r] (any slice)
  - damping: float = 0.85
  - max_iterations: int = 50
  - tolerance: float = 1e-6

PRODUCES:
  - pagerank: Dict[node, float]

FORMULA:
  A = T[:,:,t,r]
  N = number of nodes

  Initialize: PR = [1/N, 1/N, ..., 1/N]

  Iterate until convergence:
    out_degree = A.sum(axis=1)
    out_degree[out_degree == 0] = 1  # Handle dangling nodes
    M = A / out_degree[:, None]  # Row-normalize

    dangling_mass = sum(PR[dangling_nodes]) / N

    PR_new = (1 - d)/N + d × (M.T @ PR + dangling_mass)

    if max(|PR_new - PR|) < tolerance:
      break
    PR = PR_new
```

### 5.2 Louvain Community Detection

```
REQUIRES:
  - T[:,:,t,r] (any slice)
  - resolution: float = 1.0

PRODUCES:
  - community: Dict[node, int]
  - modularity: float

FORMULA:
  Q = (1/2m) × Σᵢⱼ [Aᵢⱼ - (kᵢkⱼ/2m)] × δ(cᵢ, cⱼ)

  where:
    m = total edge weight
    kᵢ = degree of node i
    δ(cᵢ, cⱼ) = 1 if same community, else 0

  Algorithm:
    Phase 1 (Local Moving):
      For each node (sorted for determinism):
        Move to community maximizing ΔQ
    Phase 2 (Aggregation):
      Collapse communities into super-nodes
    Repeat until Q stops improving
```

### 5.3 Spectral Analysis

```
REQUIRES:
  - T[:,:,t,r] (any slice)

PRODUCES:
  - fiedler_value: float  # λ₂
  - spectral_gap: float  # λ₃ - λ₂
  - eigenvalues: List[float]

FORMULA:
  A = T[:,:,t,r]
  D = diag(A.sum(axis=1))  # Degree matrix
  L = D - A  # Unnormalized Laplacian

  Compute k smallest eigenvalues of L:
    λ₁ = 0 (always, for connected graph)
    λ₂ = algebraic connectivity (Fiedler value)
    λ₃, λ₄, ...

  spectral_gap = λ₃ - λ₂

  Interpretation:
    λ₂ small → graph nearly disconnected
    λ₂ large → strong global connectivity
    Large spectral_gap → clear cluster structure
```

### 5.4 Strongly Connected Components

```
REQUIRES:
  - T[:,:,t,0] (IMPORT layer, directed)

PRODUCES:
  - sccs: List[Set[node]]
  - cycle_member: Dict[node, bool]
  - cycle_count: int

ALGORITHM: Tarjan's SCC (iterative, O(V+E))

  cycle_member[node] = |SCC containing node| > 1
  cycle_count = count(SCCs with size > 1)
```

### 5.5 BFS Depth

```
REQUIRES:
  - T[:,:,t,0] (IMPORT layer)
  - role from 2.4

PRODUCES:
  - depth: Dict[node, int]

METHOD:
  entry_points = {n for n in nodes if role[n] == ENTRY_POINT}

  If no entry points:
    entry_points = {n for n in nodes if in_degree[n] == 0 and out_degree[n] > 0}

  If still empty:
    entry_points = all nodes with depth = 0

  BFS from all entry points:
    depth[entry] = 0
    For each node at depth d:
      For each successor s:
        If depth[s] undefined:
          depth[s] = d + 1

  depth[unreachable] = -1
```

### 5.6 Blast Radius

```
REQUIRES:
  - T[:,:,t,0] (IMPORT layer)

PRODUCES:
  - blast_radius: Dict[node, Set[node]]
  - blast_radius_size: Dict[node, int]

METHOD:
  A_reverse = T[:,:,t,0].T  # Transpose for reverse dependencies

  For each node v:
    blast_radius[v] = BFS(v, A_reverse) \ {v}
    blast_radius_size[v] = |blast_radius[v]|

  Interpretation: If v changes, all nodes in blast_radius[v] may be affected
```

### 5.7 Orphan Detection

```
REQUIRES:
  - T[:,:,t,0] (IMPORT layer)
  - role from 2.4

PRODUCES:
  - is_orphan: Dict[node, bool]

FORMULA:
  in_degree = T[:,:,t,0].sum(axis=0)

  is_orphan[node] = (in_degree[node] == 0)
                    AND role[node] NOT IN {ENTRY_POINT, TEST, CONFIG}
```

### 5.8 Centrality Gini

```
REQUIRES:
  - pagerank from 5.1

PRODUCES:
  - centrality_gini: float

FORMULA:
  x = sorted(pagerank.values())
  n = len(x)

  G = (2 × Σᵢ₌₁ⁿ i × xᵢ) / (n × Σ xᵢ) - (n+1)/n

  Interpretation:
    G < 0.3 → healthy distribution
    G > 0.7 → severe hub dominance
```

### 5.9 Betweenness Centrality

```
REQUIRES:
  - T[:,:,t,r] (any slice)

PRODUCES:
  - betweenness: Dict[node, float]

FORMULA (Brandes algorithm):
  CB(v) = Σ_{s≠v≠t} σ_st(v) / σ_st

  where:
    σ_st = # shortest paths from s to t
    σ_st(v) = # shortest paths through v

  Normalize: CB[v] / ((N-1)(N-2))
```

---

## Level 6: Cross-Layer Analysis

### 6.1 Hidden Coupling

```
REQUIRES:
  - T[:,:,t,0] (IMPORT)
  - T[:,:,t,1] (COCHANGE)

PRODUCES:
  - hidden_coupling_edges: List[(node, node, float)]
  - hidden_coupling_count: Dict[node, int]

FORMULA:
  For each (i, j):
    IF T[i,j,t,1] > threshold AND T[i,j,t,0] == 0:
      hidden_coupling_edges.append((i, j, T[i,j,t,1]))

  hidden_coupling_count[v] = count(hidden edges involving v)
```

### 6.2 Dead Imports

```
REQUIRES:
  - T[:,:,t,0] (IMPORT)
  - T[:,:,t,1] (COCHANGE)

PRODUCES:
  - dead_import_edges: List[(node, node)]

FORMULA:
  For each (i, j):
    IF T[i,j,t,0] > 0 AND T[i,j,t,1] == 0:
      dead_import_edges.append((i, j))

  Interpretation: Static import with no temporal coupling evidence
```

### 6.3 Conway Violations

```
REQUIRES:
  - T[:,:,t,0] (IMPORT)
  - T[:,:,t,2] (AUTHOR)

PRODUCES:
  - conway_violations: List[(node, node)]
  - conway_alignment: float

FORMULA:
  For each (i, j) with T[i,j,t,0] > 0:
    IF T[i,j,t,2] < 0.3:  # Low author overlap
      conway_violations.append((i, j))

  conway_alignment = 1 - |conway_violations| / |import_edges|
```

### 6.4 Mutual Information

```
REQUIRES:
  - T[:,:,t,r1] (any layer)
  - T[:,:,t,r2] (any layer)

PRODUCES:
  - mutual_info: float

FORMULA:
  Discretize edge weights into bins

  I(G1; G2) = Σₐ Σᵦ p(a,b) × log₂[p(a,b) / (p(a) × p(b))]

  where:
    p(a,b) = joint probability of edge being in bin a for G1 and bin b for G2
    p(a), p(b) = marginal probabilities
```

### 6.5 PageRank Velocity

```
REQUIRES:
  - T[:,:,t,r] for t = now, t-1

PRODUCES:
  - pagerank_velocity: Dict[node, float]

FORMULA:
  pr_now = PageRank(T[:,:,now,r])
  pr_prev = PageRank(T[:,:,now-1,r])

  pagerank_velocity[v] = (pr_now[v] - pr_prev[v]) / Δt

  Interpretation:
    > 0 → file becoming more central (risk increasing)
    < 0 → file becoming less central
```

### 6.6 Community Stability

```
REQUIRES:
  - T[:,:,t,r] for all t

PRODUCES:
  - community_changes: Dict[node, int]
  - community_stability: Dict[node, float]

FORMULA:
  For each time t:
    community[t] = Louvain(T[:,:,t,r])

  community_changes[v] = count(t where community[t][v] ≠ community[t-1][v])
  community_stability[v] = 1 - community_changes[v] / (K - 1)
```

### 6.7 Graph Velocity

```
REQUIRES:
  - T[:,:,t,r] for all t

PRODUCES:
  - graph_velocity: float

FORMULA:
  For each consecutive pair (t, t+1):
    edges_t = nonzero(T[:,:,t,r])
    edges_t1 = nonzero(T[:,:,t+1,r])

    edge_diff = |edges_t △ edges_t1|  # Symmetric difference
    edge_union = |edges_t ∪ edges_t1|

    velocity[t] = edge_diff / edge_union

  graph_velocity = mean(velocity)

  Interpretation: Fraction of edges changing per time window
```

---

## Level 7: Signal Fusion

### 7.1 Percentile Normalization

```
REQUIRES:
  - All per-file signals
  - N = file count

PRODUCES:
  - percentiles: Dict[signal_name, Dict[node, float]]

FORMULA:
  Tier selection:
    ABSOLUTE: N < 15 → use raw values only
    BAYESIAN: 15 ≤ N < 50 → smoothed percentiles
    FULL: N ≥ 50 → standard percentiles

  For FULL tier:
    pctl(signal, v) = |{u: signal[u] ≤ signal[v]}| / N
```

### 7.2 Raw Risk

```
REQUIRES:
  - pagerank from 5.1
  - blast_radius_size from 5.6
  - complexity from 1.5
  - churn_cv from 3.2
  - bus_factor from 3.3

PRODUCES:
  - raw_risk: Dict[node, float]

FORMULA:
  For each file v:
    raw_risk[v] = 0.25 × norm(pagerank[v])
                + 0.20 × norm(blast_radius_size[v])
                + 0.20 × norm(complexity[v])
                + 0.20 × min(churn_cv[v] / 2, 1)
                + 0.15 × max(0, 1 - bus_factor[v] / 5)

  where norm(x) = x / max(all values of x)
```

### 7.3 Risk Score

```
REQUIRES:
  - percentiles from 7.1
  - raw signals

PRODUCES:
  - risk_score: Dict[node, float]

FORMULA:
  For each file v:
    instability_factor = 1.0 if trajectory[v] ∈ {CHURNING, SPIKING} else 0.3

    risk_score[v] = 0.25 × pctl(pagerank, v)
                  + 0.20 × pctl(blast_radius_size, v)
                  + 0.20 × pctl(cognitive_load, v)
                  + 0.20 × instability_factor
                  + 0.15 × (1 - min(bus_factor[v], 5) / 5)
```

### 7.4 Wiring Quality

```
REQUIRES:
  - is_orphan from 5.7
  - stub_ratio from 1.6
  - unresolved_imports from 2.1

PRODUCES:
  - wiring_quality: Dict[node, float]

FORMULA:
  phantom_ratio[v] = |unresolved_imports[v]| / max(|all_imports[v]|, 1)

  wiring_quality[v] = 1 - (
      0.30 × is_orphan[v]
    + 0.25 × stub_ratio[v]
    + 0.25 × phantom_ratio[v]
    + 0.20 × (hidden_coupling_count[v] / max(degree[v], 1))
  )
```

### 7.5 Health Score

```
REQUIRES:
  - risk_score from 7.3
  - wiring_quality from 7.4
  - percentiles from 7.1
  - is_orphan from 5.7

PRODUCES:
  - health_score: Dict[node, float]  # [1, 10] scale

FORMULA:
  raw_health[v] = 1 - (
      0.25 × risk_score[v]
    + 0.20 × (1 - wiring_quality[v])
    + 0.20 × pctl(cognitive_load, v)
    + 0.15 × is_orphan[v]
    + 0.20 × (1 - neighborhood_coherence[v])
  )

  health_score[v] = 1 + 9 × raw_health[v]  # Scale to [1, 10]
```

### 7.6 Health Laplacian (Delta-H)

```
REQUIRES:
  - health_score from 7.5
  - T[:,:,now,0] (IMPORT layer)

PRODUCES:
  - delta_h: Dict[node, float]

FORMULA:
  For each node v:
    neighbors = {u: T[v,u,now,0] > 0 OR T[u,v,now,0] > 0}

    IF |neighbors| == 0:
      delta_h[v] = 0.0  # Orphan, no neighborhood
    ELSE:
      mean_neighbor_health = mean(health_score[u] for u in neighbors)
      delta_h[v] = health_score[v] - mean_neighbor_health

  Interpretation:
    delta_h > 0 → healthier than neighbors
    delta_h < 0 → sicker than neighbors (hotspot)
```

---

## Level 8: Module Aggregation

### 8.1 Module Detection

```
REQUIRES:
  - community from 5.2
  OR
  - file_list from 0.1 (directory-based)

PRODUCES:
  - modules: Dict[module_id, Set[node]]
  - module_membership: Dict[node, module_id]

METHOD:
  Option 1: Use Louvain communities
  Option 2: Use directory structure (parent_dir as module_id)
```

### 8.2 Module Cohesion

```
REQUIRES:
  - T[:,:,t,0] (IMPORT layer)
  - modules from 8.1

PRODUCES:
  - cohesion: Dict[module_id, float]

FORMULA:
  For module m:
    internal_edges = |{(a,b): a,b ∈ m AND T[a,b,t,0] > 0}|
    possible_edges = |m| × (|m| - 1)

    cohesion[m] = internal_edges / max(possible_edges, 1)
```

### 8.3 Module Coupling

```
REQUIRES:
  - T[:,:,t,0] (IMPORT layer)
  - modules from 8.1

PRODUCES:
  - coupling: Dict[module_id, float]
  - Ce: Dict[module_id, int]  # Efferent
  - Ca: Dict[module_id, int]  # Afferent

FORMULA:
  Ce[m] = |{(a,b): a ∈ m AND b ∉ m AND T[a,b,t,0] > 0}|
  Ca[m] = |{(a,b): a ∉ m AND b ∈ m AND T[a,b,t,0] > 0}|

  coupling[m] = Ce[m] / max(Ce[m] + Ca[m], 1)
```

### 8.4 Martin's Instability

```
REQUIRES:
  - Ce, Ca from 8.3

PRODUCES:
  - instability: Dict[module_id, float | None]

FORMULA:
  IF Ce[m] + Ca[m] == 0:
    instability[m] = None  # Isolated module
  ELSE:
    instability[m] = Ce[m] / (Ce[m] + Ca[m])

  Range: [0, 1]
    0 = completely stable (only incoming)
    1 = completely unstable (only outgoing)
```

### 8.5 Abstractness

```
REQUIRES:
  - role from 2.4
  - modules from 8.1

PRODUCES:
  - abstractness: Dict[module_id, float]

FORMULA:
  abstract_roles = {INTERFACE, CONSTANT, CONFIG}

  For module m:
    abstract_count = count(v ∈ m where role[v] in abstract_roles)
    abstractness[m] = abstract_count / |m|
```

### 8.6 Main Sequence Distance

```
REQUIRES:
  - instability from 8.4
  - abstractness from 8.5

PRODUCES:
  - main_seq_distance: Dict[module_id, float]

FORMULA:
  IF instability[m] is None:
    main_seq_distance[m] = abstractness[m]  # Treat as fully stable
  ELSE:
    main_seq_distance[m] = |abstractness[m] + instability[m] - 1|

  Zones:
    Zone of Pain: A < 0.3 AND I < 0.3 (concrete + stable)
    Zone of Uselessness: A > 0.7 AND I > 0.7 (abstract + unstable)
    Main Sequence: D ≈ 0 (ideal)
```

---

## Level 9: Global Signals

### 9.1 Global Ratios

```
REQUIRES:
  - is_orphan from 5.7
  - unresolved_imports from 2.1
  - file_list from 0.1

PRODUCES:
  - orphan_ratio: float
  - phantom_ratio: float

FORMULA:
  orphan_ratio = count(is_orphan) / N
  phantom_ratio = sum(|unresolved_imports[v]|) / sum(|all_imports[v]|)
```

### 9.2 Wiring Score

```
REQUIRES:
  - orphan_ratio from 9.1
  - phantom_ratio from 9.1
  - stub_ratio from 1.6
  - clone_pairs (if available)

PRODUCES:
  - wiring_score: float

FORMULA:
  glue_nodes = count(v where in_degree[v] > 0 AND out_degree[v] > 0)
  glue_deficit = 1 - glue_nodes / N

  clone_ratio = |files in clone pairs| / N

  wiring_score = 1 - (
      0.25 × orphan_ratio
    + 0.25 × phantom_ratio
    + 0.20 × glue_deficit
    + 0.15 × mean(stub_ratio)
    + 0.15 × clone_ratio
  )
```

### 9.3 Architecture Health

```
REQUIRES:
  - cohesion, coupling, main_seq_distance from Level 8
  - conway_violations from 6.3

PRODUCES:
  - architecture_health: float

FORMULA:
  violation_rate = |conway_violations| / max(|import_edges|, 1)

  architecture_health = 0.30 × (1 - violation_rate)
                      + 0.20 × mean(cohesion)
                      + 0.20 × (1 - mean(coupling))
                      + 0.15 × (1 - mean(main_seq_distance))
                      + 0.15 × mean(boundary_alignment)
```

### 9.4 Codebase Health

```
REQUIRES:
  - architecture_health from 9.3
  - wiring_score from 9.2
  - bus_factor from 3.3
  - modularity from 5.2

PRODUCES:
  - codebase_health: float  # [1, 10] scale

FORMULA:
  team_size = |unique authors|
  min_bus = min(bus_factor[v] for v in top 10% by pagerank)

  raw_health = 0.30 × architecture_health
             + 0.30 × wiring_score
             + 0.20 × min(min_bus / team_size, 1)
             + 0.20 × modularity

  codebase_health = 1 + 9 × raw_health  # Scale to [1, 10]
```

---

## Level 10: Finders

Each finder is a predicate over signals that produces findings when true.

### Finder Template

```
REQUIRES:
  - List of signals

CONDITION:
  Boolean expression over signals

PRODUCES:
  - Finding if condition is true
      Finding = {
        type: str,
        severity: float [0, 1],
        files: List[path],
        evidence: List[{signal, value, percentile}],
        description: str,
        suggestion: str
      }
```

### Finder Catalog

| Finder | Condition | Severity |
|--------|-----------|----------|
| HIGH_RISK_HUB | pagerank > p85 AND blast_radius > p75 | CRITICAL |
| GOD_FILE | lines > 500 AND (cognitive_load > p90 OR in_degree > p90) | HIGH |
| HIDDEN_COUPLING | lift > 2.0 AND no import edge | MEDIUM |
| ORPHAN_CODE | is_orphan AND role not in {ENTRY, TEST, CONFIG} | LOW |
| UNSTABLE_FILE | cv > 1.0 AND trajectory = CHURNING | MEDIUM |
| CYCLE | cycle_member = true | HIGH |
| ZONE_OF_PAIN | instability < 0.3 AND abstractness < 0.3 | MEDIUM |
| BOUNDARY_MISMATCH | boundary_alignment < 0.5 | MEDIUM |
| DEAD_IMPORT | import edge with no co-change evidence | LOW |
| CONWAY_VIOLATION | import across teams (author_jaccard < 0.2) | MEDIUM |
| VOLATILE_CORE | pagerank > p75 AND cv > 0.8 | HIGH |
| HOLLOW_CODE | stub_ratio > 0.5 | LOW |

---

## Appendix: Complexity Analysis

| Operation | Time | Space |
|-----------|------|-------|
| Filesystem scan | O(N) | O(N) |
| AST parsing | O(N × avg_file_size) | O(N) |
| Import resolution | O(N × avg_imports) | O(N²) worst |
| Tensor population | O(N² × K × R) | O(nnz) sparse |
| PageRank | O(E × iters) | O(N) |
| Louvain | O(N log N) | O(N) |
| Spectral | O(N² k) | O(N²) |
| SCC (Tarjan) | O(V + E) | O(V) |
| Percentiles | O(N log N) | O(N) |
| Finders | O(N) | O(findings) |

**Total for N=10,000 files**: ~50-70 seconds
