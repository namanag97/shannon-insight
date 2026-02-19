# Shannon Insight: Mathematical Computation DAG

This document defines the complete Directed Acyclic Graph of mathematical computations.
Each layer only depends on layers below it.

---

## Layer 0: Raw Extraction

**Inputs**: Files on disk, Git repository

```
FILES ──────────────────────────────────────────────────────────────┐
├── content: bytes                                                   │
├── path: str                                                        │
└── hash: sha256(content)                                            │
                                                                     │
GIT ────────────────────────────────────────────────────────────────┤
├── commits: [(hash, timestamp, author, message)]                    │
├── file_changes: [(commit, path, change_type, additions, deletions)]│
└── renames: [(commit, old_path, new_path)]                          │
                                                                     ▼
                                                              [LAYER 1]
```

**Outputs**:
| Signal | Scope | Type | Formula |
|--------|-------|------|---------|
| `lines` | FILE | int | `len(content.splitlines())` |
| `functions` | FILE | int | `count(parse(content).functions)` |
| `classes` | FILE | int | `count(parse(content).classes)` |
| `imports` | FILE | list[str] | `parse(content).import_targets` |
| `complexity` | FILE | int | `Σ(1 + branches per function)` |
| `max_nesting` | FILE | int | `max(nesting_depth per statement)` |
| `content_hash` | FILE | str | `sha256(content)` |

---

## Layer 1: Temporal Index

**Inputs**: Git commits, file_changes, renames

```
COMMITS + FILE_CHANGES + RENAMES
         │
         ▼
    ┌─────────────────────────────────────────────────────┐
    │  NODE LIFECYCLE                                     │
    │  ├── node_birth[path] = min(t where path appears)   │
    │  ├── node_death[path] = max(t where path removed)   │
    │  └── node_canonical[old] = new (for renames)        │
    │                                                     │
    │  EDGE LIFECYCLE                                     │
    │  ├── edge_birth[r][(a,b)] = first t with edge       │
    │  └── edge_death[r][(a,b)] = last t with edge        │
    │                                                     │
    │  WINDOW AGGREGATES                                  │
    │  ├── cochange_counts[(a,b)] = co-occurrence count   │
    │  ├── author_counts[path] = {author: commit_count}   │
    │  └── churn_counts[path] = total modifications       │
    └─────────────────────────────────────────────────────┘
         │
         ▼
    [LAYER 2]
```

**Formulas**:
```
age(v) = t_now - node_birth[v]

churn_per_window[v][w] = count(changes to v in window w)

churn_mean[v] = mean(churn_per_window[v])
churn_std[v] = std(churn_per_window[v])
churn_cv[v] = churn_std[v] / max(churn_mean[v], 1)

author_entropy[v] = -Σ p(a) log₂ p(a)  where p(a) = commits_by_a / total_commits
bus_factor[v] = 2^author_entropy[v]

fix_ratio[v] = commits_with_fix_keyword / total_commits
refactor_ratio[v] = commits_with_refactor_keyword / total_commits
```

---

## Layer 2: Relationship Graphs

**Inputs**: Layer 0 (imports, content), Layer 1 (cochange_counts, author_counts)

```
┌─────────────────────────────────────────────────────────────────────┐
│  G_IMPORT (R₁) - Directed                                           │
│  ├── Edge (a → b) if: a imports b                                   │
│  └── Weight: 1.0                                                    │
├─────────────────────────────────────────────────────────────────────┤
│  G_COCHANGE (R₃) - Undirected                                       │
│  ├── Edge (a — b) if: lift(a,b) > 1.0                               │
│  └── Weight: lift(a,b) = P(a,b) / (P(a) × P(b))                     │
│           = (commits_both × total_commits) / (commits_a × commits_b)│
├─────────────────────────────────────────────────────────────────────┤
│  G_AUTHOR (R₄) - Undirected                                         │
│  ├── Edge (a — b) if: authors(a) ∩ authors(b) ≠ ∅                   │
│  └── Weight: jaccard(a,b) = |A∩B| / |A∪B|                           │
├─────────────────────────────────────────────────────────────────────┤
│  G_SEMANTIC (R₅) - Undirected                                       │
│  ├── Edge (a — b) if: cosine(concepts_a, concepts_b) > θ            │
│  └── Weight: cosine_similarity                                      │
├─────────────────────────────────────────────────────────────────────┤
│  G_CLONE (R₆) - Undirected                                          │
│  ├── Edge (a — b) if: NCD(a,b) < 0.3                                │
│  └── Weight: 1 - NCD(a,b)                                           │
│       NCD(a,b) = (C(a+b) - min(C(a),C(b))) / max(C(a),C(b))          │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
    [LAYER 3]
```

**Derived Graphs**:
```
HIDDEN_COUPLING    = G_cochange \ (G_import ∪ G_importᵀ)
CONFIRMED_COUPLING = G_import ∩ G_cochange
DEAD_IMPORT        = G_import \ G_cochange
CONWAY_VIOLATION   = G_import \ G_author
CONWAY_ALIGNED     = G_import ∩ G_author
SEMANTIC_MISMATCH  = G_import \ G_semantic

G_COMBINED = Σᵣ αᵣ Gᵣ  where Σαᵣ = 1
```

---

## Layer 3: Graph Signals

**Inputs**: Layer 2 (all graphs)

### 3.1 Per-Node Signals (for each relationship type r)

```
GRAPH Gᵣ
    │
    ├──► DEGREE
    │    ├── in_degree[r](v) = |{u : (u,v) ∈ Eᵣ}|
    │    ├── out_degree[r](v) = |{u : (v,u) ∈ Eᵣ}|
    │    └── degree[r](v) = in_degree + out_degree
    │
    ├──► CENTRALITY
    │    ├── pagerank[r](v) = (1-d)/N + d × Σᵤ pagerank[r](u)/out_degree(u)
    │    │                    where d=0.85, iterate until convergence
    │    ├── betweenness[r](v) = Σₛ≠ᵥ≠ₜ σₛₜ(v)/σₛₜ
    │    │                       σₛₜ = shortest paths s→t
    │    │                       σₛₜ(v) = shortest paths through v
    │    └── eigenvector[r](v) = principal eigenvector of Aᵣ
    │
    ├──► STRUCTURE
    │    ├── depth[r](v) = BFS distance from entry points
    │    │                 entry_points = {v : in_degree[IMPORT](v) = 0}
    │    │                              OR {__init__.py files}
    │    │                              OR all nodes (fallback)
    │    ├── blast_radius[r](v) = |transitive_closure(v)|
    │    │                      = |{u : path v →* u exists}|
    │    └── is_orphan[r](v) = (in_degree[r](v) == 0)
    │
    ├──► COMMUNITY
    │    ├── community[r](v) = Louvain cluster assignment
    │    │                     maximize: Q = (1/2m) Σᵢⱼ [Aᵢⱼ - kᵢkⱼ/2m] δ(cᵢ,cⱼ)
    │    └── clustering[r](v) = triangles(v) / possible_triangles(v)
    │
    └──► CYCLE MEMBERSHIP
         ├── cycle_member(v) = v ∈ any SCC with |SCC| > 1
         └── cycle_size(v) = |SCC containing v|
```

### 3.2 Global Graph Signals

```
GRAPH Gᵣ
    │
    ├──► TOPOLOGY
    │    ├── node_count[r] = |V|
    │    ├── edge_count[r] = |E|
    │    └── density[r] = |E| / (|V| × (|V|-1))
    │
    ├──► SPECTRAL
    │    │   L = D - A (Laplacian)
    │    │   eigenvalues: 0 = λ₁ ≤ λ₂ ≤ λ₃ ≤ ...
    │    ├── fiedler[r] = λ₂ (algebraic connectivity)
    │    └── spectral_gap[r] = λ₃ - λ₂
    │
    ├──► COMMUNITY
    │    ├── modularity[r] = Q from Louvain
    │    └── community_count[r] = |unique communities|
    │
    ├──► CYCLES
    │    ├── scc_count[r] = |{SCC : |SCC| > 1}|
    │    └── largest_scc[r] = max(|SCC|)
    │
    └──► INEQUALITY
         └── centrality_gini[r] = Gini(pagerank values)
                                = (2×Σᵢ i×xᵢ)/(n×Σxᵢ) - (n+1)/n
                                  where xᵢ sorted ascending, i is 1-indexed
```

---

## Layer 4: Trajectory Signals

**Inputs**: Layer 3 computed at multiple time points

```
For signal s(v) measured at times t₁, t₂, ..., tₖ:

VELOCITY (first derivative):
    Ds(v, t) = (s(v,t) - s(v,t-Δ)) / Δ

ACCELERATION (second derivative):
    D²s(v, t) = (Ds(v,t) - Ds(v,t-Δ)) / Δ

TREND (robust velocity):
    trend(s, v) = linear_regression_slope(s(v) over time)
```

**Specific Trajectory Signals**:
| Signal | Scope | Formula |
|--------|-------|---------|
| `pagerank_velocity` | FILE | `D(pagerank)` |
| `pagerank_acceleration` | FILE | `D²(pagerank)` |
| `degree_velocity` | FILE | `D(degree)` |
| `community_changes` | FILE | `count(community(t) ≠ community(t-1))` |
| `community_stability` | FILE | `1 - community_changes/observations` |
| `existence_fraction` | FILE | `(time alive) / (total history)` |
| `graph_velocity` | CODEBASE | `mean(‖G(t) - G(t-1)‖)` |
| `fiedler_trend` | CODEBASE | `trend(fiedler)` |
| `modularity_trend` | CODEBASE | `trend(modularity)` |
| `topology_stability` | CODEBASE | `1 / (1 + graph_velocity)` |

---

## Layer 5: Cross-Layer Signals

**Inputs**: Layer 2 (multiple graphs), Layer 3 (graph signals)

### 5.1 Per-Node Cross-Layer

```
For node v, comparing two graphs G₁ and G₂:

N₁(v) = neighbors of v in G₁
N₂(v) = neighbors of v in G₂

hidden_coupling_count(v) = |N_cochange(v) \ N_import(v)|
dead_import_count(v) = |N_import(v) \ N_cochange(v)|
conway_violation_count(v) = |N_import(v) \ N_author(v)|
neighborhood_coherence(v) = |N_import ∩ N_cochange| / |N_import ∪ N_cochange|
```

### 5.2 Per-Pair Cross-Layer

```
For pair (a, b):

hidden_coupling(a,b) = cochange(a,b) × (1 - import(a,b))
dead_import(a,b) = import(a,b) × (1 - cochange(a,b))
conway_violation(a,b) = import(a,b) × (1 - author_overlap(a,b))
semantic_mismatch(a,b) = import(a,b) × (1 - semantic_sim(a,b))
```

### 5.3 Global Cross-Layer (Mutual Information)

```
For graphs G₁, G₂ over same nodes:

I(G₁; G₂) = edge-based mutual information
          = Σₐᵦ (nₐᵦ/n) log₂[(nₐᵦ × n) / (nₐ• × n•ᵦ)]

where:
    n₁₁ = edges in both
    n₁₀ = edges only in G₁
    n₀₁ = edges only in G₂
    n₀₀ = edges in neither
    n = n₁₁ + n₁₀ + n₀₁ + n₀₀

NMI(G₁, G₂) = 2 × I(G₁; G₂) / (H(G₁) + H(G₂))
```

**Specific Cross-Layer Signals**:
| Signal | Scope | Formula |
|--------|-------|---------|
| `behavioral_coherence` | CODEBASE | `I(G_import; G_cochange)` |
| `conway_alignment` | CODEBASE | `I(G_import; G_author)` |
| `semantic_alignment` | CODEBASE | `I(G_import; G_semantic)` |
| `structural_predictability` | CODEBASE | `I(G(t); ΔG(t+1))` |

### 5.4 Transfer Entropy (Causal)

```
T(X→Y) = I(Y_{t+1}; X_t | Y_t)
       = H(Y_{t+1}|Y_t) - H(Y_{t+1}|Y_t,X_t)

"Does knowing X improve prediction of Y beyond Y's own history?"

T(G_import → G_cochange): Does structure drive behavior?
T(G_cochange → G_import): Does behavior drive structure?
```

---

## Layer 6: Composite Signals

**Inputs**: Layers 0-5 (all signals)

### 6.1 Normalization (Required First)

```
For percentile-based normalization:
    pctl(S, v) = |{u : S(u) ≤ S(v)}| / |all_files|

Three-tier strategy:
    ABSOLUTE tier (<15 files): use raw values only
    BAYESIAN tier (15-50 files): blend raw + percentile
    FULL tier (50+ files): use percentiles
```

### 6.2 Per-File Composites

```
RAW_RISK (computed BEFORE percentiles):
    raw_risk(v) = 0.25 × norm(pagerank)
                + 0.20 × norm(blast_radius_size)
                + 0.20 × norm(cognitive_load)
                + 0.20 × min(churn_cv / 2.0, 1.0)
                + 0.15 × max(0, 1 - bus_factor / 5.0)

RISK_SCORE (uses percentiles):
    risk_score(v) = 0.25 × pctl(pagerank)
                  + 0.20 × pctl(blast_radius_size)
                  + 0.20 × pctl(cognitive_load)
                  + 0.20 × pctl(instability)
                  + 0.15 × (1 - pctl(bus_factor))

WIRING_QUALITY (penalties):
    wiring_quality(v) = 1.0
                      - 0.3 × is_orphan
                      - 0.2 × pctl(stub_ratio)
                      - 0.2 × (phantom_import_count > 0)
                      - 0.2 × pctl(hidden_coupling_count)
                      - 0.1 × (clone_count > 0)

HEALTH_SCORE:
    health_score(v) = 10.0 × (1.0
                    - 0.40 × risk_score
                    - 0.25 × (1 - wiring_quality)
                    - 0.20 × pctl(cognitive_load)
                    - 0.15 × (1 - neighborhood_coherence))
    Range: [1, 10]

DELTA_H (Health Laplacian):
    delta_h(v) = raw_risk(v) - mean(raw_risk(neighbors))
               = 0 if v is orphan (no neighbors)

    Interpretation:
        delta_h > 0: file is riskier than neighbors (hotspot)
        delta_h < 0: file is healthier than neighbors
        delta_h = 0: file matches neighborhood risk
```

### 6.3 Per-Module Composites

```
MODULE_HEALTH:
    module_health(m) = 10.0 × (1.0
                     - 0.25 × (1 - cohesion(m))
                     - 0.20 × coupling(m)
                     - 0.20 × main_seq_distance(m)   # if instability not None
                     - 0.15 × (1 - boundary_alignment(m))
                     - 0.10 × (1 - role_consistency(m))
                     - 0.10 × (layer_violation_count(m) > 0))

Where:
    cohesion(m) = internal_edges / (|m| × (|m|-1) / 2)
    coupling(m) = external_edges / total_possible_external
    Ce(m) = |{dependencies m has on others}|
    Ca(m) = |{others that depend on m}|
    instability(m) = Ce / (Ce + Ca)  if Ce+Ca > 0 else None
    abstractness(m) = abstract_files / total_files
    main_seq_distance(m) = |abstractness + instability - 1|
    boundary_alignment(m) = |module ∩ community| / |module ∪ community|
```

### 6.4 Global Composites

```
WIRING_SCORE:
    wiring_score = 1.0
                 - 0.20 × orphan_ratio
                 - 0.15 × phantom_ratio
                 - 0.15 × glue_deficit
                 - 0.20 × mean_stub_ratio
                 - 0.15 × clone_ratio
                 - 0.15 × hidden_coupling_ratio

ARCHITECTURE_HEALTH:
    architecture_health = 10.0 × (1.0
                        - 0.20 × violation_rate
                        - 0.15 × (1 - mean_cohesion)
                        - 0.15 × mean_coupling
                        - 0.15 × mean_main_seq_distance
                        - 0.15 × (1 - mean_boundary_alignment)
                        - 0.10 × (1 - behavioral_coherence)
                        - 0.10 × (modularity_trend < 0))

TEAM_RISK:
    team_risk = 0.30 × (1 - global_bus_factor / team_size)
              + 0.25 × knowledge_gini
              + 0.25 × coordination_cost
              + 0.20 × (1 - conway_alignment)

CODEBASE_HEALTH:
    codebase_health = 10.0 × (
        0.25 × architecture_health/10
      + 0.20 × wiring_score
      + 0.15 × global_bus_factor / team_size
      + 0.15 × modularity
      + 0.15 × behavioral_coherence
      + 0.10 × topology_stability
    )
```

---

## Layer 7: Finders (Patterns)

**Inputs**: Layer 6 (composite signals), all previous layers

Each finder reads specific signals and emits findings:

### 7.1 Structural Finders

| Finder | Reads | Condition |
|--------|-------|-----------|
| `ORPHAN_CODE` | `is_orphan[IMPORT]`, `roles` | `is_orphan AND role NOT IN {TEST, MIGRATION, CONFIG}` |
| `PHANTOM_IMPORT` | `unresolved_imports` | `|unresolved| > 0` |
| `CLONE_CODE` | `clone_pairs`, `NCD` | `NCD(a,b) < 0.3` |
| `GOD_FILE` | `functions`, `lines`, `complexity` | `functions > 50 OR lines > 1000` |
| `HOLLOW_CODE` | `stub_ratio`, `functions` | `stub_ratio > 0.5 AND functions > 3` |
| `FLAT_ARCHITECTURE` | `max(depth[IMPORT])` | `max_depth < 3 AND files > 20` |

### 7.2 Temporal Finders

| Finder | Reads | Condition |
|--------|-------|-----------|
| `VOLATILE_FILE` | `churn_cv`, `total_changes` | `churn_cv > 1.5 AND total_changes > median` |
| `BUS_FACTOR_RISK` | `bus_factor` | `bus_factor < 1.5 AND total_changes > 10` |
| `STABILIZING` | `churn_cv`, `churn_trend` | `churn_cv < 0.5 AND churn_trend < 0` |

### 7.3 Graph Finders

| Finder | Reads | Condition |
|--------|-------|-----------|
| `HIGH_RISK_HUB` | `pagerank`, `blast_radius` | `pctl(pagerank) > 0.9 AND blast_radius > 10` |
| `HIDDEN_COUPLING` | `hidden_coupling_count` | `hidden_coupling_count > 3` |
| `DEAD_DEPENDENCY` | `dead_import_count` | `dead_import_count > 2` |
| `CYCLE_MEMBER` | `cycle_member`, `cycle_size` | `cycle_member AND cycle_size > 2` |

### 7.4 Architecture Finders

| Finder | Reads | Condition |
|--------|-------|-----------|
| `ZONE_OF_PAIN` | `instability`, `abstractness` | `instability > 0.5 AND abstractness < 0.2` |
| `USELESS_ABSTRACTION` | `instability`, `abstractness` | `instability < 0.2 AND abstractness > 0.8` |
| `BOUNDARY_MISMATCH` | `boundary_alignment` | `boundary_alignment < 0.5` |
| `LAYER_VIOLATION` | `layer_violation_count` | `layer_violation_count > 0` |
| `CONWAY_VIOLATION` | `conway_violation_count` | `conway_violation_count > 2` |

### 7.5 Cross-Dimensional Finders

| Finder | Reads | Condition |
|--------|-------|-----------|
| `ACCIDENTAL_COUPLING` | `concept_overlap`, `cochange` | `low concept overlap BUT high cochange` |
| `ARCHITECTURAL_DEBT` | `health_score`, `delta_h` | `health_score < 4 AND delta_h > 0.2` |
| `HOTSPOT` | `raw_risk`, `total_changes` | `raw_risk > p90 AND total_changes > median` |

---

## Complete DAG Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 7: FINDINGS                                                   │
│   22 finders reading from all layers                                │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 6: COMPOSITES                                                 │
│   raw_risk → risk_score → health_score → delta_h                    │
│   cohesion + coupling + instability → module_health                 │
│   wiring_score + architecture_health + team_risk → codebase_health  │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 5: CROSS-LAYER                                                │
│   G₁ × G₂ → hidden_coupling, dead_import, conway_violation          │
│   I(G₁; G₂) → behavioral_coherence, conway_alignment                │
│   T(G₁ → G₂) → causal_structure, causal_behavior                    │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 4: TRAJECTORY                                                 │
│   s(t) → Ds(t) → D²s(t)                                             │
│   pagerank_velocity, community_stability, fiedler_trend             │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 3: GRAPH SIGNALS                                              │
│   Per-node: pagerank, betweenness, depth, blast_radius, community   │
│   Global: fiedler, modularity, centrality_gini, scc_count           │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 2: RELATIONSHIP GRAPHS                                        │
│   G_import, G_cochange, G_author, G_semantic, G_clone               │
│   Derived: HIDDEN_COUPLING, DEAD_IMPORT, CONWAY_VIOLATION           │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 1: TEMPORAL INDEX                                             │
│   node_birth, node_death, cochange_counts, author_counts            │
│   churn_cv, bus_factor, author_entropy, fix_ratio                   │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 0: RAW EXTRACTION                                             │
│   Files: lines, functions, classes, imports, complexity             │
│   Git: commits, file_changes, renames                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Signal Count by Layer

| Layer | Signals | Description |
|-------|---------|-------------|
| 0 | 8 | Syntax: lines, functions, classes, imports, complexity, max_nesting, max_function_lines, content_hash |
| 1 | 9 | Temporal: age, churn_mean/std/cv/trend, bus_factor, author_entropy, fix_ratio, refactor_ratio |
| 2 | 6 | Graphs: G_import, G_cochange, G_author, G_semantic, G_clone, G_combined |
| 3 | 19 | Per-node (14): degree, pagerank, betweenness, depth, blast_radius, community, is_orphan, cycle_member, ... + Global (5): fiedler, modularity, centrality_gini, scc_count, density |
| 4 | 10 | Trajectory: pagerank_velocity, degree_velocity, community_stability, fiedler_trend, topology_stability, ... |
| 5 | 11 | Cross-layer: hidden_coupling_count, dead_import_count, neighborhood_coherence, behavioral_coherence, conway_alignment, ... |
| 6 | 9 | Composites: raw_risk, risk_score, wiring_quality, health_score, delta_h, module_health, wiring_score, architecture_health, codebase_health |
| **Total** | **62** | |

---

## Key Formulas Reference

### Gini Coefficient
```
G = (2 × Σᵢ i × xᵢ) / (n × Σxᵢ) - (n+1)/n

where:
    xᵢ sorted in ascending order
    i is 1-indexed

Returns: 0 = perfect equality, 1 = maximum inequality
```

### Shannon Entropy
```
H(X) = -Σᵢ p(xᵢ) log₂ p(xᵢ)

For author distribution:
    p(a) = commits_by_author_a / total_commits
    bus_factor = 2^H
```

### PageRank
```
PR(v) = (1-d)/N + d × Σᵤ PR(u)/out_degree(u)

where:
    d = 0.85 (damping factor)
    N = total nodes
    iterate until convergence (Δ < 1e-6)
```

### Mutual Information
```
I(G₁; G₂) = Σₐᵦ (nₐᵦ/n) × log₂[(nₐᵦ × n) / (nₐ• × n•ᵦ)]

where nₐᵦ counts edges present (1) or absent (0) in each graph
```

### Health Laplacian
```
Δh(v) = raw_risk(v) - (1/|N(v)|) × Σᵤ∈N(v) raw_risk(u)

where N(v) = neighbors of v in G_import
      Δh(v) = 0 if v is orphan (|N(v)| = 0)
```
