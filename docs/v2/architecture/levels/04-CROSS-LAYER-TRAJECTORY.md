# Level 4: Cross-Layer & Trajectory Signals

## Overview

Level 4 computes signals that require **multiple graphs** (cross-layer comparisons) or **temporal sequences** (trajectory analysis). These signals reveal:

- **Hidden relationships**: Where behavior diverges from structure (e.g., files that change together but don't import)
- **Causal dependencies**: Whether structure drives behavior or vice versa
- **Temporal dynamics**: How centrality, community membership, and topology evolve
- **System health trends**: Whether modularity is improving or degrading

**Dependencies**: Levels 2-3 (all graphs, all graph signals computed)

**Outputs**: 10 new signals (4 trajectory, 11 cross-layer) → 21 total

---

## Part A: Trajectory Signals (Temporal Derivatives)

### A.1 Concept: Signal Series & Velocity

For any signal `s(v)` measured at multiple time points `t₁, t₂, ..., tₖ`, we compute:

```
Velocity (first derivative):
    v_s(v, t) = (s(v,t) - s(v,t-Δ)) / Δ

Acceleration (second derivative):
    a_s(v, t) = (v_s(v,t) - v_s(v,t-Δ)) / Δ

Trend (robust velocity):
    τ_s(v) = slope(s(v) vs time)   # linear regression
```

**Physical meaning**: 
- `v_s > 0`: signal is increasing (getting worse if risk-like, better if health-like)
- `a_s > 0`: signal is accelerating (trend is speeding up)
- `τ_s > 0`: overall trend over history is increasing

### A.2 Per-File Trajectory Signals

#### Signal: `pagerank_velocity`
```
Formula:
    v_pr(v, t) = (pagerank(v,t) - pagerank(v,t-Δ)) / Δ
    where Δ = time interval (e.g., 1 month)

Interpretation:
    > 0: file becoming more central (riskier)
    < 0: file becoming less central (healthier)

Null handling:
    If file didn't exist at t-Δ, use first valid measurement
    If only one snapshot available, return 0.0
```

#### Signal: `pagerank_acceleration`
```
Formula:
    a_pr(v, t) = (v_pr(v,t) - v_pr(v,t-Δ)) / Δ

Interpretation:
    > 0: centrality increases are accelerating (crisis trajectory)
    < 0: centrality increases are decelerating (stabilizing)
    ~ 0: steady velocity (linear growth or decline)
```

#### Signal: `degree_velocity`
```
Formula:
    v_d(v, t) = (degree(v,t) - degree(v,t-Δ)) / Δ

Interpretation:
    Tracks how quickly a file is acquiring/losing dependencies.
    > 0: file collecting dependencies (potential coupling growth)
    < 0: file decoupling from codebase
```

#### Signal: `community_changes`
```
Formula:
    cc(v) = count(times community(v,t) ≠ community(v,t-1))
            over all observed time points

Integer count of community reassignments.

Interpretation:
    > 0: file moves between communities over time (unstable boundaries)
    = 0: file stays in same community (stable architecture)
```

#### Signal: `community_stability`
```
Formula:
    cs(v) = 1 - (community_changes(v) / num_time_points)
            = (num_time_points - community_changes(v)) / num_time_points

Interpretation:
    1.0: file always in same community (stable)
    0.0: file changes community at every step (highly unstable)
    ~ 0.5: moderate churn in module assignment
```

#### Signal: `existence_fraction`
```
Formula:
    ef(v) = (time_alive) / (total_history)
          = (node_death(v) - node_birth(v)) / (max_timestamp - min_timestamp)

Interpretation:
    1.0: file existed for entire repository history
    ~ 0.5: file created halfway through history
    ~ 0.0: file is very recent
```

### A.3 Global Trajectory Signals

#### Signal: `graph_velocity`
```
Formula:
    v_G(t) = mean(‖G(t) - G(t-Δ)‖)

where ‖G(t) - G(t-1)‖ = symmetric_difference in edge sets:
    |edges(t) \ edges(t-1)| + |edges(t-1) \ edges(t)|
    divided by max(|edges(t)|, |edges(t-1)|)

Interpretation:
    ∈ [0, 1]: 0 = graph static, 1 = complete restructuring
    > 0.2: high architectural churn
    < 0.05: stable architecture

Notes:
    - Normalizes by max edge count to make 0-1 scale invariant
    - Computed over import graph only (most stable signal)
    - Exclude 1-off bulk commits (mass reformats) via sliding median filter
```

#### Signal: `fiedler_trend`
```
Formula:
    τ_λ₂ = slope(fiedler_values over time)

where fiedler_values = [λ₂(t₁), λ₂(t₂), ..., λ₂(tₖ)]

Interpretation:
    > 0: algebraic connectivity increasing (graph clustering tightening)
    < 0: algebraic connectivity decreasing (modularity breaking down)
    ~ 0: steady spectral properties (stable community structure)

Physical meaning (Fiedler = algebraic connectivity):
    λ₂ > threshold: multiple connected components (fragmented)
    λ₂ small: bottleneck structure (vulnerable to edge removals)
```

#### Signal: `modularity_trend`
```
Formula:
    τ_Q = slope(modularity_values over time)

where modularity_values = [Q(t₁), Q(t₂), ..., Q(tₖ)]

Interpretation:
    > 0: communities becoming more distinct (good architecture evolution)
    < 0: communities merging/eroding (architecture degradation)
    ~ 0: stable community structure
```

#### Signal: `topology_stability`
```
Formula:
    ts = 1 / (1 + graph_velocity)

Interpretation:
    ∈ (0, 1]: 1 = completely static graph
             0.5 ≈ 50% edge changes per interval
             → 0 = chaotic restructuring

Mapping:
    ts ≥ 0.8: stable topology (graph_velocity ≤ 0.25)
    ts ∈ [0.5, 0.8): moderate churn
    ts < 0.5: high architectural churn
```

### A.4 Historical Snapshot Collection

To compute trajectory signals, we need **time series of graph snapshots**:

```
Timeline Construction:
    1. Determine analysis window from git history span (min_commit...max_commit)
    2. Partition into T time intervals (default: monthly snapshots)
    3. For each interval t_i:
       a. Reconstruct import graph at end of t_i
          - Include only commits up to t_i timestamp
          - Filter out deleted files (use node_death dates)
       b. Run graph algorithms (PageRank, Louvain, Spectral)
       c. Store snapshot: {timestamp: t_i, pagerank: {...}, community: {...}, fiedler: ...}
    4. Sort snapshots chronologically
    5. Compute velocity/acceleration/trend by differencing adjacent snapshots

Snapshot Filtering:
    - Skip snapshots with < 5 files (too sparse for meaningful analysis)
    - If no valid snapshots, set all trajectory signals to 0.0
    - Edge case: single snapshot → all velocities = 0.0

Storage Model:
    For each snapshot:
        {
          timestamp: unix_seconds,
          file_count: int,
          edge_count: int,
          pagerank_per_file: {file: float, ...},
          community_per_file: {file: int, ...},
          fiedler: float,
          modularity: float,
          density: float
        }
```

### A.5 Edge Cases & Robustness

**Few commits (< 10 total)**:
```
- Set num_windows = 1 (single window = entire history)
- All per-file trajectory signals = 0.0
- Global trajectory signals computed but low confidence
```

**Single snapshot available**:
```
- Cannot compute velocity/acceleration (requires ≥2 points)
- Set all trajectory signals = 0.0
- Flag for manual review
```

**Dormant file (last changed > 6 months ago)**:
```
- Velocity = 0.0 by definition (unchanged)
- Use last observed snapshot for stability metrics
```

**High graph churn (> 50% edges change per month)**:
```
- Indicates tooling issues, mass refactors, or generation artifacts
- Flag and use robust statistics (median instead of mean)
```

---

## Part B: Cross-Layer Signals (Graph Comparisons)

### B.1 Concept: Comparing G₁ and G₂

Given two graphs over the same nodes:
- **G_import**: A → B means A imports B
- **G_cochange**: A — B means A and B change together (undirected)
- **G_author**: A — B means A and B share authors (undirected)
- **G_semantic**: A — B means A and B have similar concepts (undirected)

Cross-layer analysis asks: **Do these graphs agree?**

```
Perfect agreement (rare):
    All pairs that import also cochange, share authors, and have similar concepts

Mismatch (common):
    Pair (A,B):
    - imports: YES, cochanges: NO → dead import or hidden coupling
    - imports: YES, authors: NO → Conway's Law violation
    - imports: YES, semantics: NO → accidental coupling
```

### B.2 Per-Node Cross-Layer Signals

#### Signal: `hidden_coupling_count`
```
Formula:
    hcc(v) = |N_cochange(v) \ N_import(v)|
           = count of files that cochange with v but DON'T import from v

where:
    N_cochange(v) = {u : cochange(v,u) ≥ threshold}
    N_import(v) = neighbors of v in G_import (in + out)

Interpretation:
    > 0: v has hidden dependencies (runtime coupling, side effects)
    = 0: all cochange partners are in import graph (good structure)
    > 5: significant hidden complexity (refactoring needed)

Threshold notes:
    For G_cochange: use lift(v,u) > 1.5 (above random chance)
    For G_import: any presence counts (directed union in/out)
```

#### Signal: `dead_import_count`
```
Formula:
    dic(v) = |N_import(v) \ N_cochange(v)|
           = count of files that v imports from but DON'T cochange with

where:
    N_import(v) = neighbors in G_import
    N_cochange(v) = cochange neighbors above threshold

Interpretation:
    > 0: v has dead/vestigial imports (technical debt)
    = 0: all imports are actively used
    > 5: v is importing abandoned/frozen dependencies

Threshold notes:
    Cochange threshold: lift > 1.5 (significant association)
    If a dependency is used at all, it should show up in some commits
```

#### Signal: `conway_violation_count`
```
Formula:
    cvc(v) = |N_import(v) \ N_author(v)|
           = count of files that v imports from but share no authors

where:
    N_import(v) = neighbors in G_import
    N_author(v) = files sharing ≥1 author

Interpretation:
    > 0: v imports from code not maintained by v's team
    = 0: perfect Conway's Law alignment (unlikely in large orgs)
    > 3: significant team boundary violations (coordination issues)

Physical meaning (Conway's Law):
    If A and B have different maintainers, A→B creates coordination cost
    High violation_count suggests architectural misalignment
```

#### Signal: `neighborhood_coherence`
```
Formula:
    nc(v) = |N_import(v) ∩ N_cochange(v)| / |N_import(v) ∪ N_cochange(v)|
          = Jaccard similarity between import and cochange neighborhoods

where:
    Intersection: files that both import AND cochange
    Union: files that import OR cochange (or both)

Range: [0, 1]
    1.0: import graph perfectly predicts cochange (ideal)
    0.5: 50% overlap (moderate mismatch)
    0.0: no overlap (complete structural/behavioral mismatch)

Special cases:
    If |N_import ∪ N_cochange| = 0: set nc(v) = 1.0 (isolated node, coherent)
```

### B.3 Global Cross-Layer Signals (Mutual Information)

#### Theory: Mutual Information

For two graphs G₁ and G₂ over N nodes, mutual information measures how much knowing the edge structure of G₁ tells us about G₂.

```
Contingency table (all possible edge pairs):
    Each of N×N node pairs (i,j) can have:
    - Edge in both: n₁₁
    - Edge in G₁ only: n₁₀
    - Edge in G₂ only: n₀₁
    - Edge in neither: n₀₀
    
    Total pairs: n = n₁₁ + n₁₀ + n₀₁ + n₀₀ = N×(N-1)/2 for undirected

Mutual Information:
    I(G₁; G₂) = Σₐᵦ (nₐᵦ/n) × log₂[(nₐᵦ × n) / (nₐ• × n•ᵦ)]
    
where:
    nₐ• = n_{a0} + n_{a1} = marginal count for G₁ (a ∈ {0,1})
    n•ᵦ = n_{0b} + n_{1b} = marginal count for G₂ (b ∈ {0,1})

Normalized Mutual Information:
    NMI(G₁; G₂) = 2 × I(G₁; G₂) / (H(G₁) + H(G₂))
    
where:
    H(G) = -[p_e log₂(p_e) + (1-p_e) log₂(1-p_e)]
    p_e = |E| / (N×(N-1)/2) = edge density
```

**Interpretation**:
- `I = 0`: graphs are independent (no information transfer)
- `I > 0`: knowing one graph helps predict the other
- `NMI = 1`: perfect prediction (graphs identical)
- `NMI = 0`: no mutual information (independent)

#### Signal: `behavioral_coherence`
```
Formula:
    bc = NMI(G_import, G_cochange)

Interpretation:
    1.0: Files that import also cochange (structure = behavior)
    0.5: Moderate alignment (some imports have cochange)
    0.0: No relationship (imports don't predict changes)

Physical meaning:
    High bc: architecture accurately reflects actual dependencies
    Low bc: hidden dependencies, emergent coupling
    
Example:
    - Auth module imports database module
    - Auth and database change together in 80% of commits
    → high behavioral_coherence
    
    - Auth module imports database module
    - Auth and database never change together
    → low behavioral_coherence (dead import or side-effect dependency)
```

#### Signal: `conway_alignment`
```
Formula:
    ca = NMI(G_import, G_author)

Interpretation:
    1.0: Teams owning imported files are same (Conway perfect)
    0.5: Moderate author overlap
    0.0: No team alignment (strong cross-team dependencies)

Physical meaning:
    High ca: organizational structure matches code structure
    Low ca: files architected for teams that don't maintain them

Implementation:
    G_author: edge (A, B) iff they share ≥1 author
    Use Jaccard for author overlap: |A ∩ B| / |A ∪ B|
    
Alternative (phase 3 current):
    ca = 1.0 - mean(author_distance(N_import(v)))
    More granular (per-file) but doesn't capture global coherence
    v2 keeps both: NMI for global, distance for per-file tuning
```

#### Signal: `semantic_alignment`
```
Formula:
    sa = NMI(G_import, G_semantic)

Interpretation:
    1.0: Imported files have similar concepts (conceptually coherent)
    0.5: Some semantic overlap
    0.0: No semantic relationship (accidental coupling)

Physical meaning:
    High sa: imports are semantically meaningful
    Low sa: architectural boundaries don't match conceptual boundaries
    
Example:
    - api.py imports both database.py and logging.py
    - api.py and database.py share concepts {db, query, schema}
    - api.py and logging.py share no concepts
    → sa = ~0.66 (1 of 2 imports semantically aligned)
```

#### Signal: `structural_predictability`
```
Formula:
    sp = I(G(t); ΔG(t+Δ))
       = mutual information between graph structure at t and edge changes at t+Δ

where:
    G(t) = snapshot of import graph at time t
    ΔG(t+Δ) = binary matrix: edges added/removed in next interval

Interpretation:
    High sp: current structure determines what changes (predictable evolution)
    Low sp: changes are independent of structure (chaotic)
    
Example:
    If new imports are always between high-PageRank nodes:
    → sp = high (structure predicts growth)
    
    If imports change randomly:
    → sp = low (structure doesn't predict changes)
```

### B.4 Transfer Entropy (Causal Direction)

#### Concept: Does X cause Y?

```
Conditional mutual information:
    T(X→Y) = I(Y_{t+Δ}; X_t | Y_t)
           = how much X_t tells us about Y_{t+Δ}, given Y_t history

Interpretation:
    T(X→Y) > T(Y→X): X causes Y (structure drives behavior)
    T(Y→X) > T(X→Y): Y causes X (behavior shapes structure)
    T(X→Y) ≈ T(Y→X): bidirectional causality
    Both ~ 0: no causal relationship

Physical interpretation:
    - T(structure → behavior): "Does the import graph predict cochange patterns?"
    - T(behavior → structure): "Do change patterns drive refactoring?"
```

#### Causal Signals (Phase 5+)

```
causal_structure = T(G_import(t) → G_cochange(t+Δ))
    > 0.5: architecture shapes how code evolves
    
causal_behavior = T(G_cochange(t) → G_import(t+Δ))
    > 0.5: temporal coupling drives architectural changes (refactoring in response)
```

**Note**: Transfer entropy is computationally expensive (requires 3D tensors). Deferred to Phase 5+ if needed for causal analysis.

---

## Part C: Integration & Data Flow

### C.1 Input Requirements

**From Level 2 (Graphs)**:
- `G_import`: Full dependency graph with all edges
- `G_cochange`: Co-change matrix (not a direct graph, convert via lift threshold)
- `G_author`: Author overlap graph
- `G_semantic`: Semantic similarity graph
- `adjacency` & `reverse` indices for efficient neighborhood queries

**From Level 3 (Graph Signals)**:
- Per-file: `pagerank`, `depth`, `community`, `degree`, `blast_radius`
- Global: `fiedler_value`, `modularity`
- All for every time snapshot (if trajectory analysis enabled)

**From Temporal Module**:
- `ChurnSeries.window_counts` for trend fitting
- `CoChangeMatrix.pairs` with lift values
- Git commit history for snapshot timing
- File birth/death timestamps

**From File Metrics**:
- File paths (canonical names for graph nodes)
- Import lists (for N_import neighborhoods)

### C.2 Computation Pipeline

```
PHASE 4.1: Prepare Graphs
    Input: G_import, G_cochange, G_author, G_semantic
    For G_cochange (raw matrix):
        - Convert to undirected graph edges where lift(a,b) > 1.5
        - Compute adjacency list representation
        
    For G_author:
        - Build from author overlap: edge (a,b) if authors(a) ∩ authors(b) ≠ ∅
        - Weight by Jaccard: |A∩B| / |A∪B|
    
    Output: Normalized adjacency lists for all graphs

PHASE 4.2: Per-Node Cross-Layer Signals
    For each file v:
        hcc(v) ← compute_hidden_coupling_count(v, G_cochange, G_import)
        dic(v) ← compute_dead_import_count(v, G_import, G_cochange)
        cvc(v) ← compute_conway_violation_count(v, G_import, G_author)
        nc(v) ← compute_neighborhood_coherence(v, G_import, G_cochange)
    
    Store in FileSignals.hidden_coupling_count, etc.

PHASE 4.3: Global Cross-Layer Signals (Mutual Information)
    Compute contingency tables:
        - (G_import, G_cochange) → I() → bc = NMI()
        - (G_import, G_author) → I() → ca = NMI()
        - (G_import, G_semantic) → I() → sa = NMI()
    
    Store in GlobalSignals

PHASE 4.4: Trajectory Signals (requires historical snapshots)
    Condition: if num_snapshots >= 2 and span >= 3 months
    
    For each file v:
        Collect time series: [(t₁, pagerank(v,t₁)), (t₂, pagerank(v,t₂)), ...]
        v_pr(v) ← first_derivative(series)
        a_pr(v) ← second_derivative(series)
        cc(v) ← count_community_changes(v)
        cs(v) ← community_stability(v)
        ef(v) ← existence_fraction(v)
    
    For codebase:
        v_G ← graph_velocity()
        τ_λ₂ ← fiedler_trend()
        τ_Q ← modularity_trend()
        ts ← topology_stability()
    
    Store per-file in FileSignals, per-codebase in GlobalSignals

PHASE 4.5: Null Handling
    For each signal s:
        if insufficient data:
            s ← 0.0 with metadata flag {'requires': ['snapshots', 'history']}
```

### C.3 Graceful Degradation (Tier System)

**ABSOLUTE tier** (< 15 files):
```
- Cross-layer signals available (only need current snapshot)
- Trajectory signals unavailable (insufficient history)
- Set all trajectory = 0.0
```

**BAYESIAN tier** (15-50 files):
```
- Cross-layer signals available
- Trajectory signals available IF span >= 1 month
- Otherwise set trajectory = 0.0
```

**FULL tier** (50+ files):
```
- All signals available
- Require span >= 3 months for trajectory
- Require 5+ snapshots for fiedler_trend, modularity_trend
```

---

## Part D: Data Models

### D.1 FileSignals Extensions

```python
@dataclass
class FileSignals:
    # ... existing fields ...
    
    # Cross-layer signals (new in Level 4)
    hidden_coupling_count: int = 0          # |N_cochange \ N_import|
    dead_import_count: int = 0              # |N_import \ N_cochange|
    conway_violation_count: int = 0         # |N_import \ N_author|
    neighborhood_coherence: float = 0.0     # Jaccard(N_import, N_cochange)
    
    # Trajectory signals (new in Level 4)
    pagerank_velocity: float = 0.0          # d(pagerank)/dt
    pagerank_acceleration: float = 0.0      # d²(pagerank)/dt²
    degree_velocity: float = 0.0            # d(degree)/dt
    community_changes: int = 0              # count of community reassignments
    community_stability: float = 0.0        # 1 - (changes / observations)
    existence_fraction: float = 0.0         # time_alive / total_history
```

### D.2 GlobalSignals Extensions

```python
@dataclass
class GlobalSignals:
    # ... existing fields ...
    
    # Cross-layer signals (new in Level 4)
    behavioral_coherence: float = 0.0       # NMI(G_import; G_cochange)
    conway_alignment: float = 1.0           # NMI(G_import; G_author)
    semantic_alignment: float = 0.0         # NMI(G_import; G_semantic)
    structural_predictability: float = 0.0  # I(G(t); ΔG(t+Δ))
    
    # Trajectory signals (new in Level 4)
    graph_velocity: float = 0.0             # mean(‖G(t) - G(t-1)‖)
    fiedler_trend: float = 0.0              # slope(fiedler over time)
    modularity_trend: float = 0.0           # slope(modularity over time)
    topology_stability: float = 1.0         # 1 / (1 + graph_velocity)
    
    # Transfer entropy (Phase 5+)
    causal_structure: float | None = None   # T(G_import → G_cochange)
    causal_behavior: float | None = None    # T(G_cochange → G_import)
```

### D.3 TemporalSnapshot Model

```python
@dataclass
class TemporalSnapshot:
    """Historical snapshot of graph and node signals at a point in time."""
    
    timestamp: int                          # unix seconds
    graph_stats: GraphStats
    per_node_signals: dict[str, dict[str, float]]  # {file: {signal: value}}
    
    # Specific for trajectory computation
    pagerank_per_file: dict[str, float]
    community_per_file: dict[str, int]
    fiedler_value: float
    modularity: float
    graph_velocity: float

@dataclass
class GraphStats:
    file_count: int
    edge_count: int
    density: float
    cycle_count: int
    largest_scc: int
```

---

## Part E: Implementation Notes

### E.1 Mutual Information Computation

```python
def compute_mutual_information(
    adj1: dict[str, set[str]],  # G₁ adjacency
    adj2: dict[str, set[str]],  # G₂ adjacency
    nodes: set[str]
) -> float:
    """
    Compute I(G₁; G₂) efficiently.
    
    O(N²) but sparse adjacency makes it practical.
    """
    
    # Build contingency table
    n11 = n10 = n01 = n00 = 0
    
    for i, j in combinations(nodes, 2):
        edge1 = (i in adj1.get(j, set())) or (j in adj1.get(i, set()))
        edge2 = (i in adj2.get(j, set())) or (j in adj2.get(i, set()))
        
        if edge1 and edge2:
            n11 += 1
        elif edge1:
            n10 += 1
        elif edge2:
            n01 += 1
        else:
            n00 += 1
    
    n = n11 + n10 + n01 + n00
    
    # Compute mutual information
    I = 0.0
    for n_ab, n_a_dot, n_dot_b in [
        (n11, n11+n10, n11+n01),
        (n10, n11+n10, n10+n00),
        (n01, n01+n00, n11+n01),
        (n00, n01+n00, n10+n00),
    ]:
        if n_ab > 0 and n_a_dot > 0 and n_dot_b > 0:
            p_ab = n_ab / n
            I += p_ab * math.log2((n_ab * n) / (n_a_dot * n_dot_b))
    
    return I

def normalize_mutual_information(
    I: float,
    adj1: dict[str, set[str]],
    adj2: dict[str, set[str]],
    nodes: set[str]
) -> float:
    """NMI(G₁; G₂) ∈ [0, 1]"""
    
    H1 = _entropy_graph(adj1, nodes)
    H2 = _entropy_graph(adj2, nodes)
    
    if H1 + H2 == 0:
        return 0.0
    
    return 2 * I / (H1 + H2)

def _entropy_graph(adj: dict[str, set[str]], nodes: set[str]) -> float:
    """H(G) = Shannon entropy of edge distribution"""
    
    edge_count = sum(len(v) for v in adj.values()) / 2  # undirected
    possible_edges = len(nodes) * (len(nodes) - 1) / 2
    p_e = edge_count / possible_edges if possible_edges > 0 else 0.0
    
    if p_e == 0 or p_e == 1:
        return 0.0
    
    return -(p_e * math.log2(p_e) + (1-p_e) * math.log2(1-p_e))
```

### E.2 Trajectory Fitting

```python
def compute_velocity(
    series: list[tuple[int, float]],  # (timestamp, value) pairs
) -> float:
    """First derivative: linear regression slope."""
    
    if len(series) < 2:
        return 0.0
    
    times = [t for t, v in series]
    values = [v for t, v in series]
    
    # Normalize timestamps to interval [0, 1]
    t_min, t_max = min(times), max(times)
    t_span = t_max - t_min
    if t_span == 0:
        return 0.0
    
    t_norm = [(t - t_min) / t_span for t in times]
    
    # Ordinary least squares
    n = len(values)
    t_mean = sum(t_norm) / n
    v_mean = sum(values) / n
    
    numerator = sum((t - t_mean) * (v - v_mean) for t, v in zip(t_norm, values))
    denominator = sum((t - t_mean) ** 2 for t in t_norm)
    
    if denominator == 0:
        return 0.0
    
    slope = numerator / denominator
    # Denormalize to units per month
    return slope * (t_span / (30 * 86400))
```

### E.3 Graph Velocity

```python
def compute_graph_velocity(
    snapshots: list[TemporalSnapshot],
) -> float:
    """Mean relative edge change per interval."""
    
    if len(snapshots) < 2:
        return 0.0
    
    velocities = []
    for i in range(1, len(snapshots)):
        prev_snap, curr_snap = snapshots[i-1], snapshots[i]
        
        # Symmetric difference of edges
        prev_edges = _adjacency_to_edges(prev_snap.pagerank_per_file.keys(), ...)
        curr_edges = _adjacency_to_edges(curr_snap.pagerank_per_file.keys(), ...)
        
        added = len(curr_edges - prev_edges)
        removed = len(prev_edges - curr_edges)
        total_changes = added + removed
        
        max_edges = max(len(prev_edges), len(curr_edges))
        if max_edges == 0:
            v_t = 0.0
        else:
            v_t = total_changes / max_edges
        
        velocities.append(v_t)
    
    # Robust: use median instead of mean (outliers common)
    return sorted(velocities)[len(velocities) // 2]
```

---

## Part F: Testing Strategy

### F.1 Unit Test Cases

```python
def test_hidden_coupling_count():
    """Pair imports but doesn't cochange → hidden_coupling = 0
    Pair cochanges but doesn't import → hidden_coupling = 1
    """
    
def test_dead_import_count():
    """Import but no cochange → dead_import = 1
    Import and cochange → dead_import = 0
    """
    
def test_conway_violation_count():
    """Import from different author → violation = 1
    Import from same author → violation = 0
    """
    
def test_neighborhood_coherence():
    """100% overlap: coherence = 1.0
    0% overlap: coherence = 0.0
    50% overlap: coherence = 0.33 (Jaccard)
    """
    
def test_behavioral_coherence():
    """Identical import and cochange graphs → bc = 1.0
    Disjoint graphs → bc = 0.0
    """
    
def test_pagerank_velocity():
    """Increasing pagerank → velocity > 0
    Decreasing pagerank → velocity < 0
    Constant pagerank → velocity ≈ 0
    """
    
def test_topology_stability():
    """No edge changes → stability = 1.0
    100% edges change → stability ≈ 0.5
    50% edges change → stability ≈ 0.67
    """
```

### F.2 Integration Test Cases

```python
def test_level_4_with_sample_codebases():
    """End-to-end: inject graphs → compute all signals → validate ranges"""
    
def test_graceful_degradation():
    """ABSOLUTE tier: trajectory = all 0.0, cross-layer available
    BAYESIAN tier: trajectory available if span >= 1mo
    FULL tier: all signals available
    """
    
def test_null_handling():
    """No snapshots → trajectory = 0.0
    Single snapshot → trajectory = 0.0, cross-layer = computed
    """
```

---

## Part G: Dependencies & Load Order

**Produces signals**: 15 new per-file + global

**Requires inputs**:
1. FileMetrics (scanning output)
2. DependencyGraph (import analysis)
3. CoChangeMatrix (temporal analysis)
4. AuthorshipData (temporal analysis)
5. GraphAnalysis with snapshots (temporal snapshots)

**Called by**:
- Level 5 (Signal Fusion) — reads cross-layer & trajectory for composites
- Level 6 (Finders) — reads for pattern detection
- Level 7 (Persistence) — stores in TensorSnapshot

**Execution model**:
- Compute ALL cross-layer signals first (depends only on current snapshot)
- Compute trajectory signals IF snapshots available
- Skip trajectory in ABSOLUTE tier

---

## Summary: Level 4 Signal Count

| Category | Per-File | Global | Total |
|----------|----------|--------|-------|
| Cross-Layer | 4 | 4 | 8 |
| Trajectory | 6 | 4 | 10 |
| **Total** | **10** | **8** | **18** |

**Cumulative**: Levels 1-4 = 62 signals ✓
