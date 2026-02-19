# Shannon Insight: Tensor-Based Architecture

## Overview

Shannon Insight analyzes codebases by building a **4D relationship tensor** that captures how files relate to each other across multiple dimensions and time. All analysis flows through this single data structure.

```
T ∈ ℝ^(N × N × K × R)

N = number of files (nodes)
K = number of time windows (monthly snapshots)
R = 5 relationship types
```

**The Core Insight**: Everything before tensor construction *populates* the tensor. Everything after *slices* from it.

---

## The Relationship Tensor

### Dimensions

| Dim | Symbol | Meaning | Example |
|-----|--------|---------|---------|
| 1 | i | Source file | `src/api/users.py` |
| 2 | j | Target file | `src/models/user.py` |
| 3 | t | Time window | `2024-01` (January 2024) |
| 4 | r | Relationship type | `IMPORT` |

### Relationship Types (R=5)

| Index | Name | Weight | Meaning |
|-------|------|--------|---------|
| 0 | **IMPORT** | 1.0 | File i imports file j |
| 1 | **COCHANGE** | lift score | Files changed together (temporal coupling) |
| 2 | **AUTHOR** | Jaccard | Same developers maintain both files |
| 3 | **SEMANTIC** | cosine | Similar concepts/vocabulary |
| 4 | **COMBINED** | weighted sum | Fusion of all relationships |

### Tensor Entry Semantics

```
T[i, j, t, r] = strength of relationship r between files i and j at time t
```

- `T[i, j, t, 0] = 1.0` → file i imports file j at time t
- `T[i, j, t, 1] = 2.5` → files co-change 2.5× more than random (lift)
- `T[i, j, t, 2] = 0.8` → 80% author overlap (Jaccard similarity)
- `T[i, j, t, 3] = 0.6` → 60% concept similarity (cosine)

---

## Computation DAG

The analysis pipeline is a directed acyclic graph with 6 levels:

```
┌─────────────────────────────────────────────────────────────────────┐
│ LEVEL 0: RAW DATA                                                   │
│   files on disk ───────────────────── git repository               │
└───────────────────────────┬─────────────────────┬───────────────────┘
                            │                     │
                            ▼                     ▼
┌───────────────────────────────────┐ ┌───────────────────────────────┐
│ LEVEL 1: EXTRACTION               │ │ LEVEL 1: EXTRACTION           │
│   file → AST → syntax             │ │   git log → commits           │
│   AST → imports                   │ │   commits → file_changes      │
│   AST → identifiers → concepts    │ │   commits → authors_per_file  │
└───────────────────────────┬───────┘ └───────────────┬───────────────┘
                            │                         │
                            └────────────┬────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LEVEL 2: TENSOR POPULATION                                          │
│                                                                     │
│   For each time window t ∈ [0, K):                                  │
│     resolved_imports ────────► T[:,:,t,0]  (IMPORT)                │
│     cochange_counts ─────────► T[:,:,t,1]  (COCHANGE)              │
│     author_overlap ──────────► T[:,:,t,2]  (AUTHOR)                │
│     concept_similarity ──────► T[:,:,t,3]  (SEMANTIC)              │
│     weighted_sum ────────────► T[:,:,t,4]  (COMBINED)              │
│                                                                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LEVEL 3: SLICE & COMPUTE                                            │
│                                                                     │
│   T[:,:,now,r] ──► Graph G_r ──► Algorithms ──► Signals            │
│                                                                     │
│   PageRank(G_import)      ──► pagerank[file]                       │
│   Louvain(G_import)       ──► community[file], modularity          │
│   Laplacian(G_import)     ──► fiedler_value, spectral_gap          │
│   SCC(G_import)           ──► cycle_member[file]                   │
│   BFS(G_import)           ──► depth[file], blast_radius[file]      │
│                                                                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LEVEL 4: CROSS-LAYER & TEMPORAL                                     │
│                                                                     │
│   T[:,:,now,IMPORT] vs T[:,:,now,COCHANGE]                         │
│     ──► hidden_coupling = edges in COCHANGE but not IMPORT         │
│     ──► behavioral_coherence = I(G_import; G_cochange)             │
│                                                                     │
│   T[:,:,:,IMPORT] over time                                         │
│     ──► pagerank_velocity = d(pagerank)/dt                         │
│     ──► community_stability                                         │
│     ──► graph_velocity (edge churn)                                │
│                                                                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LEVEL 5: COMPOSITES & FINDERS                                       │
│                                                                     │
│   All signals ──► percentiles ──► risk_score[file]                 │
│   risk + wiring + coherence  ──► health_score[file]                │
│   module aggregations        ──► architecture_health               │
│   global aggregations        ──► codebase_health                   │
│                                                                     │
│   Threshold conditions       ──► 22 Finding patterns               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Level 0: Raw Data

### Inputs

| Source | Data | Format |
|--------|------|--------|
| Filesystem | File contents | `Dict[path, bytes]` |
| Filesystem | File list | `Set[path]` |
| Git | Commits | `List[Commit]` |
| Git | File changes | `Dict[commit, List[FileChange]]` |

### Key Operations

```python
# Filesystem scan
file_list = walk(repo_path, exclude_patterns)
file_content = {path: read(path) for path in file_list}

# Git extraction
commits = parse_git_log(git_log_output)
file_changes = parse_git_numstat(git_numstat_output)
```

---

## Level 1: Extraction

### Syntax Extraction (per file)

| Output | Type | Source |
|--------|------|--------|
| `language` | str | Extension + shebang |
| `imports` | List[Import] | AST traversal |
| `functions` | List[Function] | AST traversal |
| `classes` | List[Class] | AST traversal |
| `identifiers` | Set[str] | AST traversal |
| `lines` | int | Line count |
| `complexity` | int | Decision points |
| `max_nesting` | int | Control flow depth |

**Content-addressed caching**: Parse results keyed by `SHA256(content)`. Unchanged files skip re-parsing.

### Git Extraction

| Output | Type | Source |
|--------|------|--------|
| `commits` | List[Commit] | `git log` |
| `file_changes` | Dict[commit, files] | `git log --numstat` |
| `renames` | Dict[old_path, new_path] | `git log --follow` |
| `authors_per_file` | Dict[file, Set[author]] | Aggregated from commits |

### Temporal Signals (per file)

| Signal | Formula | Meaning |
|--------|---------|---------|
| `churn_cv` | `σ(window_counts) / μ(window_counts)` | Volatility |
| `bus_factor` | `2^H` where H = author entropy | Knowledge distribution |
| `fix_ratio` | `fix_commits / total_commits` | Defect density proxy |

---

## Level 2: Tensor Population

### Building Each Relationship Layer

#### R=0: IMPORT

```python
for file in files:
    for imp in file.imports:
        resolved = resolve_import(imp, file_list)
        if resolved:
            T[file_idx, resolved_idx, t, 0] = 1.0
```

#### R=1: COCHANGE

```python
# Lift = observed co-occurrence / expected co-occurrence
for commit in commits:
    for (file_a, file_b) in pairs(commit.files):
        cochange_count[(a, b)] += decay_weight(commit.age)

for (a, b), count in cochange_counts.items():
    lift = (count / total_commits) / (P(a) * P(b))
    if lift > 1.0:
        T[a, b, t, 1] = lift
```

#### R=2: AUTHOR

```python
for (file_a, file_b) in all_pairs:
    authors_a = authors_per_file[file_a]
    authors_b = authors_per_file[file_b]
    jaccard = len(authors_a & authors_b) / len(authors_a | authors_b)
    if jaccard > 0.1:
        T[a, b, t, 2] = jaccard
```

#### R=3: SEMANTIC

```python
# TF-IDF concept vectors from identifiers
for file in files:
    concept_vector[file] = tfidf(file.identifiers)

for (file_a, file_b) in all_pairs:
    cosine = dot(concept_vector[a], concept_vector[b]) / (norm(a) * norm(b))
    if cosine > 0.3:
        T[a, b, t, 3] = cosine
```

#### R=4: COMBINED

```python
# Weighted fusion
weights = [0.4, 0.3, 0.2, 0.1]  # import, cochange, author, semantic
for (i, j) in all_edges:
    T[i, j, t, 4] = sum(w * T[i, j, t, r] for r, w in enumerate(weights))
```

### Sparse Storage

The tensor is extremely sparse (~1-5% density). Use COO format:

```python
import sparse

coords = []  # List of (i, j, t, r) tuples
values = []  # List of weights

# Build incrementally
for edge in edges:
    coords.append([edge.src, edge.dst, edge.time, edge.rel])
    values.append(edge.weight)

T = sparse.COO(np.array(coords).T, values, shape=(N, N, K, R))
```

**Memory**: For N=1000, K=12, R=5:
- Dense: 6.9 GB
- Sparse (5% density): ~11 MB

---

## Level 3: Slice & Compute

### Slicing Operations

| Operation | Result | Use |
|-----------|--------|-----|
| `T[:,:,t,r]` | N×N matrix | Graph at time t, relation r |
| `T[:,:,:,r]` | N×N×K tensor | Temporal evolution of relation r |
| `T[:,:,t,:]` | N×N×R tensor | All relations at time t |
| `T[i,:,t,:]` | N×R matrix | All edges from node i |

### Graph Algorithms

All algorithms operate on slices:

```python
# PageRank on import graph at current time
A_import = T[:,:, -1, 0].tocsr()  # Last time window, IMPORT relation
pagerank = power_iteration(A_import, damping=0.85)

# Louvain community detection
communities, modularity = louvain(A_import, resolution=1.0)

# Spectral analysis
L = degree_matrix(A_import) - A_import
eigenvalues = sparse_eigsh(L, k=10)
fiedler_value = eigenvalues[1]
spectral_gap = eigenvalues[2] - eigenvalues[1]
```

### Algorithm Reference

| Algorithm | Input | Output | Complexity |
|-----------|-------|--------|------------|
| PageRank | A (N×N) | scores (N,) | O(E × iters) |
| Louvain | A (N×N) | communities, Q | O(N log N) |
| Tarjan SCC | A (N×N) | components | O(V + E) |
| BFS Depth | A (N×N), entries | depths (N,) | O(V + E) |
| Spectral | L (N×N) | eigenvalues (k,) | O(N² k) |

---

## Level 4: Cross-Layer Analysis

### Graph Set Operations

```python
# Hidden coupling: files that co-change but don't import
hidden = T[:,:,t,COCHANGE] - T[:,:,t,IMPORT]
hidden_pairs = [(i, j) for (i, j) in hidden.nonzero() if hidden[i,j] > threshold]

# Dead imports: imports without co-change evidence
dead = T[:,:,t,IMPORT] - T[:,:,t,COCHANGE]

# Conway violations: imports across team boundaries
conway_violations = T[:,:,t,IMPORT] * (1 - T[:,:,t,AUTHOR])
```

### Mutual Information Between Layers

Measures alignment between relationship types:

```python
def edge_mutual_info(G1, G2):
    """I(G1; G2) - how much knowing G1 tells us about G2"""
    # Discretize edge weights into bins
    # Compute joint and marginal distributions
    # Return MI in bits
    n11 = count(edges in both G1 and G2)
    n10 = count(edges in G1 only)
    n01 = count(edges in G2 only)
    n00 = count(edges in neither)
    # Standard MI formula...
```

| MI Comparison | High MI Means | Low MI Means |
|---------------|---------------|--------------|
| I(IMPORT; COCHANGE) | Structure matches behavior | Decoupled evolution |
| I(IMPORT; AUTHOR) | Conway's law holds | Cross-team deps |
| I(COCHANGE; AUTHOR) | Same teams maintain coupled code | Coordination needed |

### Temporal Derivatives

```python
# PageRank velocity
pr_now = pagerank(T[:,:,-1,0])
pr_prev = pagerank(T[:,:,-2,0])
pr_velocity = (pr_now - pr_prev) / delta_t

# Community stability
comm_now = louvain(T[:,:,-1,0])
comm_prev = louvain(T[:,:,-2,0])
changes = count(files where comm_now != comm_prev)
stability = 1 - changes / N
```

---

## Level 5: Composites & Finders

### Normalization Tiers

| Tier | File Count | Strategy |
|------|------------|----------|
| ABSOLUTE | < 15 | Use raw thresholds |
| BAYESIAN | 15-50 | Smoothed percentiles |
| FULL | 50+ | Standard percentiles |

### Composite Formulas

**risk_score** (per file):
```
risk_score = 0.25 × pctl(pagerank)
           + 0.20 × pctl(blast_radius)
           + 0.20 × pctl(cognitive_load)
           + 0.20 × instability_factor
           + 0.15 × (1 - bus_factor/5)
```

**health_score** (per file, 1-10 scale):
```
health_score = 10 × (1 - weighted_penalties)

where penalties include:
  - risk_score
  - 1 - wiring_quality
  - cognitive_load percentile
  - is_orphan
  - 1 - neighborhood_coherence
```

**codebase_health** (global, 1-10 scale):
```
codebase_health = 0.30 × architecture_health
                + 0.30 × wiring_score
                + 0.20 × (bus_factor / team_size)
                + 0.20 × modularity
```

### Finders

Each finder reads signals and fires when threshold conditions are met:

| Finder | Condition | Severity |
|--------|-----------|----------|
| `HIGH_RISK_HUB` | pagerank > p85 AND blast_radius > p75 | CRITICAL |
| `HIDDEN_COUPLING` | high COCHANGE lift AND no IMPORT edge | MEDIUM |
| `GOD_FILE` | lines > 500 AND (cognitive_load > p90 OR in_degree > p90) | HIGH |
| `UNSTABLE_FILE` | churn_cv > 1.0 AND trajectory = CHURNING | MEDIUM |
| `ORPHAN_CODE` | in_degree = 0 AND role not in {ENTRY, TEST, CONFIG} | LOW |

---

## Storage & Persistence

### Tensor Storage (SQLite)

```sql
-- Sparse tensor entries
CREATE TABLE tensor_entries (
    src_id INTEGER,
    dst_id INTEGER,
    time_idx INTEGER,
    relation INTEGER,
    weight REAL,
    PRIMARY KEY (src_id, dst_id, time_idx, relation)
);

-- Node index
CREATE TABLE nodes (
    node_id INTEGER PRIMARY KEY,
    path TEXT UNIQUE,
    file_id TEXT  -- Stable identity across renames
);

-- Time windows
CREATE TABLE time_windows (
    time_idx INTEGER PRIMARY KEY,
    start_ts INTEGER,
    end_ts INTEGER,
    commit_range TEXT
);
```

### Content-Addressed Parsing Cache

```sql
CREATE TABLE parsed_syntax (
    content_hash TEXT PRIMARY KEY,
    language TEXT,
    syntax_json TEXT,  -- Compressed parsed AST
    parsed_at INTEGER
);
```

### Signal Snapshots

```sql
CREATE TABLE signal_snapshots (
    snapshot_id INTEGER PRIMARY KEY,
    timestamp INTEGER,
    commit_sha TEXT,
    signals_json TEXT,  -- Compressed SignalField
    findings_json TEXT
);
```

---

## Implementation Notes

### Python Libraries

| Library | Use |
|---------|-----|
| `sparse` (PyData) | COO tensor storage |
| `scipy.sparse` | CSR matrices for algorithms |
| `networkx` | Graph algorithms (PageRank, Louvain) |
| `tensorly` | Tensor decomposition (optional) |

### Performance Targets

For N=10,000 files:

| Phase | Target |
|-------|--------|
| Level 0 (I/O) | < 5s |
| Level 1 (Parsing) | < 10s |
| Level 2 (Tensor Build) | < 5s |
| Level 3 (Algorithms) | < 15s |
| Level 4 (Cross-layer) | < 10s |
| Level 5 (Composites) | < 5s |
| **Total** | **< 50s** |

### Incremental Updates

For subsequent runs:
1. Check content hashes → skip unchanged files
2. Only rebuild tensor entries for modified files
3. Recompute algorithms on updated slices
4. Delta-update signals

---

## References

### Academic

- Kolda & Bader, "Tensor Decompositions and Applications", SIAM Review 2009
- von Luxburg, "A Tutorial on Spectral Clustering", Statistics and Computing 2007
- Blondel et al., "Fast unfolding of communities in large networks" (Louvain), 2008

### Industry Tools

- [CodeScene Code Health](https://codescene.io/docs/guides/technical/code-health.html)
- [SonarQube Metrics](https://docs.sonarsource.com/sonarqube-server/2025.1/user-guide/code-metrics/)
- [Martin Package Metrics](https://en.wikipedia.org/wiki/Software_package_metrics)

### Libraries

- [TensorLy](http://tensorly.org/) - Tensor decomposition
- [PyData Sparse](https://sparse.pydata.org/) - Sparse n-D arrays
- [NetworkX](https://networkx.org/) - Graph algorithms

---

## Appendix: Signal Registry

See [signals.md](../v2/registry/signals.md) for the complete list of 62 signals with:
- Data types
- Polarities (HIGH_IS_BAD / HIGH_IS_GOOD)
- Percentile eligibility
- Phase availability
