# Session Recovery: f5e79ff3-d368-43ec-b498-24107c0fdd71

## Math Discussion & COMPLETE-SYSTEM-SPEC Work

---


### [Thinking]

The user is asking me to check the actual code to see:
1. What data flows between analyzers
2. Specifically: does the graph/structural analyzer need temporal data? How does that work?
3. Is the math correct in each analyzer?

Let me investigate the actual code to understand the real dependencies and check if the math is correct.

I need to:
1. Read the StructuralAnalyzer to see what it actually computes and what inputs it needs
2. Read the TemporalAnalyzer to see what it computes
3. Check if there are cross-dependencies that aren't properly handled
4. Verify the math formulas

Let me start by reading the key analyzer files.


## ASSISTANT

Let me dig into the actual code to check the dependencies and math.


### [Thinking]

Now I need to check the actual analysis engine and signal computations. The user is asking about:
1. Does graph analyzer need temporal data for any function? If so, is it properly wired?
2. Is the math correct?

Let me read the graph engine, signals code, and the fusion analyzer to understand the data flow.


## ASSISTANT

Let me check the graph engine and signal fusion to see the actual dependencies and math.


### [Thinking]

The fusion.py doesn't exist. Let me search for the signal fusion analyzer and also look at the store to understand the slots.


## ASSISTANT

Let me find the signal fusion analyzer and check the store structure.


### [Thinking]

Now let me read the SignalFusionAnalyzer and the signals/fusion.py to understand how signals are computed and if temporal data is needed.


## ASSISTANT

Let me check the signal fusion analyzer and the models to trace the actual computations.


### [Thinking]

Now let me look at the actual math - the composites, normalization, and health Laplacian - to verify if they're correct.


## ASSISTANT

Now let me check the composite calculations and health Laplacian math.


### [Thinking]

Now I have a much clearer picture of the data flow. Let me trace through it to understand the dependencies and potential issues.

The user asked specifically about the graph analyzer needing temporal data. Let me check the actual data flow:

1. **StructuralAnalyzer** (requires: `file_syntax`)
   - Runs `AnalysisEngine.run()` which builds the dependency graph
   - Computes: PageRank, betweenness, SCC, Louvain, depth, orphans
   - Does NOT need temporal data

2. **TemporalAnalyzer** (requires: nothing)
   - Extracts git history
   - Computes: ChurnSeries, CoChangeMatrix, AuthorDistances
   - Does NOT need structural data

3. **SemanticAnalyzer** (requires: `file_syntax`)
   - Computes: concepts, roles, semantic coherence
   - Does NOT need structural or temporal data

4. **SpectralAnalyzer** (requires: `structural`)
   - Computes: Fiedler value, spectral gap
   - Needs structural (graph Laplacian)

5. **ArchitectureAnalyzer** (requires: `structural`, `roles`)
   - Computes: module detection, Martin metrics
   - Needs structural + roles

6. **SignalFusionAnalyzer** (Wave 2, requires everything)
   - Collects all signals from all slots
   - Computes composites, health Laplacian

Now let me check the cross-dependencies more carefully. The user is asking if the graph analyzer needs temporal data for some function. Let me look at the actual dependencies:

In `fusion.py._compute_cognitive_load()` and other computations in the SignalFusionAnalyzer, temporal data is read from `store.churn` slot which is filled by TemporalAnalyzer.

In `engine.py._measure_files()` - the graph engine does NOT read temporal data. 

The graph engine only reads from FileSyntax and GraphAnalysis. However, the health Laplacian computation in `health_laplacian.py` depends on temporal signals like churn_cv and bus_factor alongside structural metrics like pagerank and blast_radius_size. This dependency is satisfied because TemporalAnalyzer completes in Wave 1, allowing SignalFusionAnalyzer to access all required signals when it runs in Wave 2.

Now examining the mathematical implementations: the percentile calculation correctly uses `bisect_right` to count values ≤ x, the Gini formula needs verification in the math module, Shannon entropy feeds into bus_factor as 2^H, and the health Laplacian delta_h depends on raw_risk differences between a node and its neighbors.


## ASSISTANT

Let me check the Gini calculation and the temporal/churn computations to verify the math.


### [Thinking]

Now I have a comprehensive view of the actual code. Let me summarize the findings:

## Architecture Summary

### Data Dependencies (What Actually Happens)

```
Files on disk
    │
    ▼
SyntaxExtractor (file_syntax slot)
    │
    ├──────────────────────────────────────────────────────────────┐
    │                                                              │
    ▼                                                              ▼
StructuralAnalyzer                                     SemanticAnalyzer
reads: file_syntax                                     reads: file_syntax
writes: structural, clone_pairs                        writes: semantics, roles
    │
    │                  TemporalAnalyzer
    │                  reads: git (subprocess)
    │                  writes: git_history, churn, cochange, author_distances
    │
    ▼                              │
SpectralAnalyzer                   │
reads: structural                  │
writes: spectral                   │
    │                              │
    ├──────────────────────────────┤
    ▼                              ▼
ArchitectureAnalyzer               │
reads: structural + roles          │
writes: architecture               │
    │                              │
    └──────────────────────────────┘
                 │
                 ▼
       SignalFusionAnalyzer (Wave 2)
       reads: ALL slots
       writes: signal_field
                 │
                 ▼
       execute_patterns(FactStore)
```

### Cross-Dependencies That Matter

1. **SignalFusion needs temporal for:**
   - `_fill_from_temporal()` → reads `store.churn` for `churn_cv`, `bus_factor`, `total_changes`
   - `raw_risk` computation → uses `churn_cv`, `bus_factor`
   - `risk_score` composite → uses `churn_cv`, `bus_factor`
   - `_fill_module_temporal()` → reads `store.git_history` for velocity, coordination_cost, knowledge_gini

2. **SignalFusion needs structural for:**
   - `_fill_from_graph()` → reads `store.structural` for graph metrics
   - `compute_health_laplacian()` → uses graph.adjacency/reverse for neighbor lookup

3. **SignalFusion needs architecture for:**
   - `_collect_modules()` → reads `store.architecture` for module metrics
   - `_fill_hierarchy()` → uses architecture for file→module mapping

4. **ArchitectureAnalyzer needs:** roles from semantic analysis to determine module responsibilities, and structural graph data to compute architectural patterns and layering relationships.

The mathematical foundations check out. The Gini coefficient properly sorts values in ascending order and applies 1-indexed positioning through enumeration, with bias correction via `n/(n-1)`. Shannon entropy for author distribution correctly computes `H = -Σp×log₂(p)`, yielding bus_factor as `2^H` to represent equivalent contributors. Percentile calculations accurately count values at or below a threshold divided by total count.

Coefficient of Variation applies Bessel's correction in the variance denominator. The Health Laplacian delta_h subtracts mean neighbor risk from a file's raw risk, treating isolated modules as neutral (0.0). Raw risk itself combines three weighted components: 0.25 for normalized PageRank, 0.20 for blast radius, and 0.20 for additional factors.

The raw_risk formula continues with cognitive load (0.20 weight), churn coefficient of variation capped at 2.0 (0.20 weight), and bus factor contribution (0.15 weight, maxing out at 5 people). All inputs use raw normalized values rather than percentile rankings.

Regarding temporal dependency: the graph analyzer doesn't require temporal data at all—it only consumes file syntax information. Temporal analysis happens downstream in the signal fusion phase, so the ordering concern doesn't apply. The pipeline correctly sequences structural analysis first, followed by temporal and semantic passes, with signal fusion occurring after all initial analyses complete.

There's a subtle dependency where structural clone detection attempts to access roles populated by semantic analysis, but the topological sort doesn't guarantee this ordering. The code handles this gracefully by falling back to empty roles if unavailable. The fusion phase also performs role-aware orphan filtering, which depends on semantic results being available.


## ASSISTANT

Now I have the full picture. Let me summarize the findings:

---

## The Architecture Is Actually Correct

### What You Asked: "Does graph analyzer need temporal data?"

**No, it doesn't.** The `StructuralAnalyzer` only reads from `file_syntax`. The cross-dependency you were worried about is handled by SignalFusion (Wave 2), which runs AFTER both structural and temporal complete.

### The Real Dependency Chain

```
Wave 1 (can run in parallel, topo-sorted):
├── StructuralAnalyzer:  file_syntax → structural, clone_pairs
├── TemporalAnalyzer:    git subprocess → git_history, churn, cochange
├── SemanticAnalyzer:    file_syntax → semantics, roles
├── SpectralAnalyzer:    structural → spectral
└── ArchitectureAnalyzer: structural + roles → architecture

Wave 2 (runs AFTER all Wave 1):
└── SignalFusionAnalyzer: ALL slots → signal_field
    ├─ step1_collect: reads structural, temporal, semantics, architecture
    ├─ step2_raw_risk: computes raw_risk (needs churn_cv, bus_factor from temporal)
    ├─ step3_normalize: percentiles
    ├─ step4_module_temporal: reads git_history (needs temporal)
    ├─ step5_composites: risk_score, wiring_quality, health_score
    └─ step6_laplacian: delta_h (needs graph adjacency)
```

### The Math Is Correct

| Formula | Code Location | Status |
|---------|--------------|--------|
| Gini: `G = (2×Σi×xᵢ)/(n×Σxᵢ) - (n+1)/n` | `math/gini.py:62-63` | ✓ Sorts ascending, 1-indexed |
| Shannon: `H = -Σp×log₂(p)` | `temporal/churn.py:241` | ✓ |
| bus_factor: `2^H` | `temporal/churn.py:105` | ✓ |
| Percentile: `bisect_right(sorted, x)/n` | `normalization.py:133` | ✓ Uses ≤ |
| CV: `σ/μ` (Bessel corrected) | `temporal/churn.py:162` | ✓ |
| raw_risk: weighted sum with max-normalization | `health_laplacian.py:100-102` | ✓ |
| delta_h: `raw_risk(f) - mean(raw_risk(neighbors))` | `health_laplacian.py:64` | ✓ |

### One Subtle Issue (But Not a Bug)

In `StructuralAnalyzer._detect_clones()` (line 187):
```python
if store.roles.available:
    roles = store.roles.value  # SemanticAnalyzer provides this
```

This looks like a cross-dependency (Structural reading from Semantic), but:
1. It's guarded by `.available` check
2. Falls back to empty `{}` if unavailable
3. Only affects TEST/MIGRATION file exclusion from clone detection

**Graceful degradation, not a bug.**

### Where Temporal Data Actually Gets Used

In `SignalFusionAnalyzer` (Wave 2), temporal signals flow into:

1. **FileSignals** (`fusion.py:191-208`):
   - `churn_cv`, `bus_factor`, `total_changes`, `fix_ratio`, etc.

2. **raw_risk** (`health_laplacian.py:97-98`):
   - `instab_factor = min(churn_cv / 2.0, 1.0)`
   - `bf_term = max(0, 1 - bus_factor / 5.0)`

3. **risk_score** (`composites.py:92-93`):
   - Same formula but using percentiles instead of raw values

4. **module temporal** (`fusion.py:531-588`):
   - `velocity`, `coordination_cost`, `knowledge_gini`, `module_bus_factor`

**All of this happens in Wave 2, after temporal is complete.** The ordering is correct.

---

**Bottom line:** The pipeline is wired correctly. Structural doesn't need temporal. Temporal doesn't need structural. Both feed into SignalFusion which needs everything. The math implementations match the spec formulas.


### [Thinking]

The user is making a fundamental architectural point. Let me think about this carefully.

They're saying:

1. There are TWO fundamental data sources:
   - Files (structural/static) 
   - Git (temporal/dynamic)

2. These should be the FOUNDATION (Wave 0), and everything else builds on TOP of both.

3. The current design treats them as independent parallel tracks, but theoretically many signals SHOULD use both:
   - Spectral analysis: Currently only uses the static import graph. But shouldn't spectral properties change over time? Or shouldn't we weight edges by co-change frequency?
   - Semantic analysis: Currently only uses file content. But shouldn't concept drift be measured over time?
   - Risk scores: Should combine structural importance (PageRank) with temporal instability (churn)

Let me think about what SHOULD theoretically depend on BOTH structural AND temporal:

1. **Spectral Analysis** - Currently computes Fiedler value on the static import graph. But:
   - Could weight edges by co-change frequency (files that change together have stronger coupling)
   - Could compute spectral properties on the co-change graph, not just import graph
   - Could track spectral evolution over time

2. **Semantic Analysis** - Currently extracts concepts from current file content. But:
   - Concept drift should measure how concepts CHANGED over time
   - Naming drift could compare current names to historical names

3. **Architecture Analysis** - Currently detects modules from static structure. But:
   - Conway's Law alignment needs author overlap (temporal)
   - Module stability needs churn data
   - Module boundaries might be better detected from co-change patterns than imports

4. **Clone Detection** - Currently NCD on current content. But:
   - Clones that co-evolve vs clones that diverge (temporal dimension)

5. **Risk Score** - This one DOES combine structural (pagerank, blast_radius) with temporal (churn_cv, bus_factor) in SignalFusion. But it's done AFTER the fact, not at the foundation level.
   
The theoretical architecture should layer differently: raw data extraction (files and git history) feeds into foundational analyses that build both static and temporal graphs, then derived analyses read from those combined sources rather than operating independently. Spectral analysis would work on a graph weighted by co-change frequency, semantic analysis would track concept evolution, architecture detection would incorporate author patterns and stability metrics, and all downstream signals would naturally integrate both dimensions from the start.

The current implementation bypasses this—it runs structural, temporal, semantic, and spectral analyses in parallel, each mostly isolated, then attempts to reconcile them in a final fusion step. This works pragmatically because SignalFusion patches the gaps afterward, but it means analyses that should be reading from both sources (like spectral on a temporally-weighted graph, or architecture detection informed by churn patterns) are instead operating on incomplete inputs. For instance, spectral clustering ignores co-change frequency entirely, semantic drift detection doesn't account for structural stability, and module detection doesn't weight edges by how often they actually change together. The Spectral Analyzer currently relies solely on the static import graph's Laplacian, but files that frequently co-change might indicate stronger coupling than imports alone reveal. Weighting edges by both import relationships and co-change frequency could better capture actual dependencies.

The Semantic Analyzer's naming_drift metric only measures consistency within a single file rather than tracking how naming conventions evolve over time. It should compare current naming patterns against historical versions to detect actual drift.

The Architecture Analyzer identifies modules through import structure and boundary alignment, but misses temporal signals. Co-change patterns—files modified together—could refine module detection since files changing in tandem likely belong together.

Orphan Detection currently flags files with zero incoming imports, but this ignores files that participate heavily in co-change patterns. A file with no imports but frequent coordinated changes isn't truly orphan and shouldn't be treated as such.

For the mathematical foundation, instead of separate graphs for imports and co-changes, a unified representation could weight edges by both signals: G_combined = (V, E) where each edge weight combines import strength with co-change frequency using a blended coefficient. ued together at the end in SignalFusion.

The current approach treats structure and time as separate pipelines—computing metrics independently on each, then combining them additively. But they should inform each other from the start. Building a unified graph that merges both dimensions lets me compute metrics once on this richer representation, where structural and temporal relationships reinforce each other rather than getting bolted together afterward.


## ASSISTANT

You're making a fundamental architectural point. Let me think through the math properly.

## The Two Primitive Data Sources

```
SOURCE 1: Files (static)              SOURCE 2: Git (temporal)
├── content → syntax                  ├── commits → timestamps
├── imports → edges                   ├── file_changes → churn
└── structure → metrics               └── co-occurrence → coupling
```

## What SHOULD Happen (Theoretically)

These two sources should **fuse at the graph level**, not at the signal level:

```
G_combined(u,v) = α × import(u,v) + β × cochange(u,v)
```

Then ALL downstream analysis runs on this combined graph.

## What ACTUALLY Happens (Current Code)

```
G_import  ──────► PageRank, Louvain, Spectral  ──┐
                                                  ├──► SignalFusion (additive)
G_cochange ────► lift, confidence ───────────────┘
```

The temporal and structural are **never combined into a unified graph**. They're glued together AFTER with weighted sums in composites.

## Specific Examples Where This Matters

### 1. Spectral Analysis

**Current**: Fiedler value on import graph Laplacian
```python
L = D - A  # where A is import adjacency only
```

**Should be**: Fiedler on combined graph
```python
A_combined[i,j] = w_import × has_import(i,j) + w_cochange × lift(i,j)
L = D - A_combined
```

The Fiedler value would then capture **both** structural connectivity AND temporal coupling.

### 2. Orphan Detection

**Current**: `is_orphan = (in_degree == 0)`

**Should be**: A file with zero imports but **high co-change lift** with other files isn't orphan — it's coupled through behavior, not declaration.

```python
is_orphan = (import_in_degree == 0) AND (cochange_degree == 0)
```

### 3. PageRank / Centrality

**Current**: PageRank on static import graph

**Should be**: PageRank on combined graph, or time-decayed PageRank where recent edges matter more:
```python
weight(u,v,t) = import(u,v) × decay(now - t) × cochange(u,v,t)
```

### 4. Community Detection (Louvain)

**Current**: Louvain on import graph only

**Should be**: Files that change together but don't import each other might belong to the same "behavioral module":
```python
modularity = Σ [A_combined(i,j) - k_i×k_j/(2m)] × δ(c_i, c_j)
```

### 5. Semantic Coherence

**Current**: Measures concept entropy from current content

**Should be**: Track concept drift **over time** — how much did this file's purpose change?
```
concept_stability = 1 - divergence(concepts_now, concepts_6mo_ago)
```

## The Correct Architecture

```
Wave 0: Extract raw data
├── SyntaxExtractor → FileSyntax (imports, functions, classes)
└── GitExtractor → commits, file_changes

Wave 1: Build unified graphs
├── G_import = build_from_imports(FileSyntax)
├── G_cochange = build_from_git(commits)
├── G_author = build_author_overlap(commits)
└── G_combined = fuse(G_import, G_cochange, weights)

Wave 2: Graph algorithms on combined
├── PageRank(G_combined)
├── Louvain(G_combined)
├── Spectral(L_combined)
├── Depth/Orphans(G_combined)
└── etc.

Wave 3: Higher-order analysis
├── Architecture (modules from G_combined communities)
├── Semantics (concepts + temporal drift)
└── Finders (read unified signals)
```

## The Math Problem You're Pointing At

The current code computes:
```
risk = 0.25×pctl(pagerank_static) + 0.20×pctl(blast_static) + 0.20×instability_temporal + ...
```

This is **additive fusion** of separately-computed metrics.

But the **correct math** would be:
```
pagerank = PageRank(G_combined)  # already incorporates temporal
blast = BFS(G_combined)          # already incorporates temporal
```

Then risk is just a function of the unified centrality, no additive temporal term needed.

## Summary

| Aspect | Current | Should Be |
|--------|---------|-----------|
| Graph | Two separate graphs | One combined graph |
| Fusion point | End (composites) | Beginning (graph construction) |
| Spectral | Static imports only | Combined import + cochange |
| Orphan | import in_degree=0 | combined degree=0 |
| PageRank | Static import graph | Combined weighted graph |
| Louvain | Import communities | Behavioral communities |

**You're right.** The architecture is wired to "work" but it's not mathematically correct. Structural and temporal should merge at the graph level, not the signal level.


### [Thinking]

The user wants me to think even deeper. Let me consider what's really fundamental here.

If we have two data sources - files and git - what are we really trying to measure?

We're trying to understand the **state** and **evolution** of a codebase. 

Let me think about this from first principles:

1. **What is a codebase?**
   - A set of files at a point in time (snapshot)
   - A history of changes over time (trajectory)

2. **What are we measuring?**
   - Structure (how things are connected)
   - Behavior (how things change together)
   - Risk (what might break)

But wait - the user is pushing me to think deeper. What's the fundamental mathematical object here?

A codebase is not just a graph. It's a **dynamical system**. The files are the state, and the changes are the dynamics.

Let me think about this more carefully:

**The Fundamental Object**

At any time t, we have:
- S(t) = set of files with their content
- G(t) = dependency graph at time t
- C(t→t+1) = changes between t and t+1

The codebase is really a **time-varying graph** or a **temporal network**.

**What we're computing now:**
- G(now) - the current snapshot
- Statistics over {C(t→t+1)} - churn, cochange

But we're NOT computing:
- How G evolved: G(t-n) → G(t-n+1) → ... → G(now)
- The dynamics of the graph itself

**The deeper insight:**

The import graph changes over time. Files get added, removed, refactored. The topology evolves.

Current approach: We look at G(now) and separately at change statistics.

Correct approach: We should look at the **trajectory** of G through graph space.

**Even deeper:**

What does "risk" really mean? 


Risk = P(future_problem | current_state, historical_dynamics)

To estimate this, we need the current structural state, how the system arrived there through its evolution, and patterns from history showing how problems emerge. My current approach captures features of G(now) and change distributions, but misses the trajectory itself—how the graph's topological properties shifted over time. For instance, instead of just computing the Fiedler eigenvalue now, I should track how it evolved, whether the graph is becoming more or less modular.

Similarly with centrality: a file's PageRank trajectory matters more than its snapshot value. Rising centrality signals growing importance and higher risk; declining centrality suggests obsolescence. The real mathematical structure here is a 3-tensor T[file_i, file_j, time_t] encoding relationships across time—imports, co-changes, author overlaps at each moment. This demands tensor decomposition rather than static graph operations.

The implications shift the analysis fundamentally. Spectral methods move from eigenvectors of the current graph to Tucker or CP decomposition, revealing stable patterns versus evolving ones. Community detection becomes temporal tracking: files that shift communities frequently indicate architectural instability, and fragmenting communities signal structural stress. The user's insight is that these temporal and structural dimensions shouldn't be analyzed separately—they're aspects of a single spatio-temporal object.

This reframes the workflow entirely. Rather than independently constructing import graphs and change statistics then combining them, the approach should reconstruct G(t) across relevant time points, then analyze the resulting trajectory as a unified object. This enables direct measurement of structural stability over periods like six months, or computing centrality derivatives to identify nodes gaining or losing influence.

The information-theoretic lens sharpens what we're actually measuring. Structural entropy captures current complexity, temporal entropy captures change unpredictability, and mutual information between structure and behavior reveals alignment—high values indicate structure predicts changes well, while low values expose accidental coupling or Conway's law violations. Rather than shallow proxies for semantic coherence, the deeper approach builds a generative model P(changes | structure) to directly assess how well the architecture explains observed modifications, with deviations flagging anomalies.

The real insight is treating the codebase as a dynamical system evolving through graph space rather than a static snapshot with separate change metrics. This requires temporal networks, tensor decomposition, and dynamical systems frameworks—not the current approach of computing graph features and change statistics independently then combining them additively. The trajectory through graph space itself becomes the object of study.


## ASSISTANT

You're right. Let me go deeper.

## The Real Mathematical Object

A codebase isn't two separate things (structure + history). It's **one dynamical system**:

```
G(t) = the dependency graph at time t
```

The current structure G(now) **is** the result of all historical changes. They're not independent — they're the same thing viewed differently.

## What We're Actually Measuring

We want: **P(future_problem | current_state, dynamics)**

This requires understanding the **trajectory** through graph space:

```
G(t-n) → G(t-n+1) → ... → G(now) → G(future)?
```

## What Current Code Does vs Should Do

| Current | Should Be |
|---------|-----------|
| Features of G(now) | Features of trajectory {G(t)} |
| Statistics of changes | Dynamics of graph evolution |
| Additive fusion | Unified temporal object |

## The Tensor Formulation

The proper object is a **3-tensor**:

```
T[i, j, t] = relationship between file_i and file_j at time t
```

This encodes:
- Import edges at each commit
- Co-change at each window
- Author overlap at each period

Current code: matrix ops on G(now) + scalar stats from Σ changes
Correct: **tensor decomposition** on the full spatiotemporal structure

## Specific Examples

### 1. Centrality Should Have Velocity

Current:
```python
risk = f(PageRank(G_now), churn_cv)
```

Should be:
```python
pagerank_t = [PageRank(G(t)) for t in timeline]
pagerank_velocity = d(pagerank)/dt  # derivative

# File with HIGH centrality AND INCREASING velocity = critical AND growing = HIGH RISK
# File with HIGH centrality AND DECREASING velocity = legacy, maybe becoming obsolete
```

### 2. Spectral Evolution, Not Snapshot

Current:
```python
fiedler = second_eigenvalue(Laplacian(G_now))
```

Should be:
```python
fiedler_t = [fiedler(G(t)) for t in timeline]

# Is the graph becoming MORE or LESS connected?
# Are communities stabilizing or fragmenting?
spectral_trend = slope(fiedler_t)
```

### 3. Community Membership Over Time

Current:
```python
communities = Louvain(G_now)
```

Should be:
```python
communities_t = [Louvain(G(t)) for t in timeline]

# How often does file change community?
community_stability[file] = entropy(communities_t[file])

# Files that frequently change communities = unstable role = architectural smell
```

### 4. Information-Theoretic View

The deepest formulation:

```
I(Structure; Behavior) = mutual information
```

- **High I(G; changes)** = structure predicts behavior = healthy architecture
- **Low I(G; changes)** = changes don't follow structure = hidden coupling

```python
# P(file_j changes | file_i changed AND imports(i,j))
# vs
# P(file_j changes | file_i changed AND NOT imports(i,j))

# If these are similar → imports don't predict co-change → accidental coupling
```

This is what "semantic coherence" and "Conway alignment" are **trying** to capture, but superficially.

## The Reconstruction Problem

To do this properly, we need to **reconstruct G(t)** at historical points:

```python
def reconstruct_graph_at_commit(commit_sha):
    """What was the import graph at this commit?"""
    # git checkout commit_sha
    # parse all files
    # build import graph
    # return G(t)
```

Then:
```python
trajectory = [reconstruct_graph_at_commit(sha) for sha in sample_commits]
# Now analyze the TRAJECTORY, not just the endpoint
```

## The Three Levels

| Level | What It Computes | Current Code |
|-------|------------------|--------------|
| **Shallow** | Features of G(now) + stats of changes | ✓ This is what we have |
| **Medium** | Combined graph G_import ∪ G_cochange | ✗ Missing |
| **Deep** | Trajectory analysis on {G(t)} | ✗ Missing |

## Why This Changes Everything

At the deep level:

- **"Churn"** isn't a separate signal — it's `‖dG/dt‖` (rate of graph change)
- **"Risk"** isn't additive features — it's `P(instability | trajectory)`
- **"Coupling"** isn't edge count — it's `I(Δfile_i; Δfile_j)` (mutual information of change patterns)
- **"Health"** isn't a weighted sum — it's a measure of trajectory smoothness through graph space

## The Fundamental Insight

The codebase is a **dynamical system on a network**. Structure and time aren't two inputs — they're one unified evolution.

Current architecture: snapshot + statistics → additive fusion
Correct architecture: trajectory → dynamical features → unified risk model

Does this level resonate with what you're thinking?


### [Thinking]

The user wants to go even deeper and define this more rigorously. Let me think about the mathematical foundations properly.

We're dealing with a dynamical system on a graph. Let me formalize this:

**State Space**
- At any time t, the codebase has a state S(t)
- S(t) consists of:
  - A set of files V(t) (nodes can appear/disappear)
  - Content of each file c_v(t) for v ∈ V(t)
  - Relationships between files (imports, calls, etc.)

**The Graph at Time t**
- G(t) = (V(t), E(t), W(t))
- V(t) = set of files that exist at time t
- E(t) = edges (imports, dependencies)
- W(t) = edge weights (could be binary or weighted)

**The Change Operator**
- Δ(t₁, t₂) represents the change from t₁ to t₂
- This includes:
  - Files added: V(t₂) \ V(t₁)
  - Files removed: V(t₁) \ V(t₂)
  - Files modified: {v : c_v(t₁) ≠ c_v(t₂)}
  - Edges added/removed

**The Fundamental Quantities**

1. **Graph Laplacian at time t**
   L(t) = D(t) - A(t)
   where A(t) is adjacency, D(t) is degree matrix

2. **Spectral properties at time t**
   - λ₂(t) = Fiedler value (algebraic connectivity)
   - Eigenvectors define community structure

3. **Centrality at time t**
   - π(t) = PageRank vector
   - b(t) = betweenness vector
   
Now I need to think about how to measure change over time. The graph velocity would be (G(t+Δt) - G(t)) / Δt, but this requires defining what subtraction means for graphs. I could measure this as edit distance, spectral distance using ‖L(t+Δt) - L(t)‖, or structural similarity like Jaccard distance on edges. Each captures different aspects of how the dependency structure evolves.

For individual files, I should track centrality velocity dπ/dt to see whether each file's importance is growing or shrinking. Similarly, spectral velocity dλ₂/dt would reveal whether the codebase is becoming more or less modular over time.

To formalize this, I can represent the evolution as a tensor T ∈ ℝ^(n × n × k × m) where n is the maximum number of files, k is the number of time windows, and m is the number of relationship types. Each entry T[i, j, t, r] captures the strength of relationship r between files i and j at time t, with relationship types including IMPORTS, COCHANGES_WITH, SHARES_AUTHOR, and SHARES_CONCEPT.

Decomposing this tensor via CP or Tucker methods reveals latent structure: CP decomposition isolates file clusters, temporal activation patterns, and which relationship types drive the dynamics, while Tucker decomposition exposes how file groups, time periods, and relationship types interact through the core tensor.

Rather than computing signals from static snapshots, I should define them as functions of the tensor structure itself, capturing how relationships evolve across time and relationship types.

Risk emerges from trajectory properties—specifically, instability measured by the rate of change in the core tensor, and sensitivity indicating whether perturbations here cascade elsewhere in the system.

The information-theoretic lens clarifies what we're measuring. Define X as structural features and Y as future modifications. The conditional entropy H(Y|X) captures whether the current structure constrains upcoming changes—low values mean behavior is predictable from architecture, while high values signal unpredictability. Mutual information I(X; Y) quantifies how much structure reveals about evolution. Transfer entropy distinguishes causal direction: does the graph architecture govern how it transforms, or vice versa? In healthy systems, structure should drive behavior rather than follow it.

This framework yields concrete metrics: trajectory_stability measures how rapidly the graph shifts, centrality_momentum tracks whether files gain or lose importance, and spectral_acceleration detects accelerating modularity changes. Structural_predictability tests whether graph properties forecast future modifications, behavioral_coherence examines whether tightly coupled files coevolve, and attractor_distance gauges proximity to stable configurations.

Computing these requires G(t) across multiple commits—expensive since it demands repeated checkouts and parsing. Instead, I can approximate using git metadata alone: track which edges existed at each commit through file presence, and infer edge changes from renames, additions, and deletions. A hierarchy of approximations exists: Level 0 uses current G plus aggregated changes; Level 1 weights by temporal patterns and cochange data; Level 2 samples G(t) at critical commits to compute trajectory features; Level 3 builds a full tensor decomposition for maximum precision but highest cost.


## ASSISTANT

Let me formalize this properly.

## The State Space

At time t, the codebase has state:

```
S(t) = {
    V(t): set of files that exist
    c_v(t): content of file v
    E(t): edges (imports, calls, etc.)
}
```

The graph G(t) = (V(t), E(t)) evolves over time. **This is the fundamental object.**

## The Dynamical System

```
G(t₀) → G(t₁) → G(t₂) → ... → G(now)
        ↑        ↑        ↑
       Δ₁       Δ₂       Δ₃      (changes/commits)
```

Each Δ is a transformation: files added, removed, modified, edges changed.

## What We Should Compute

### 1. Position (current state)
```
G(now), L(now), π(now), λ₂(now)
```
This is what current code computes.

### 2. Velocity (rate of change)
```
dG/dt ≈ distance(G(t), G(t-Δ)) / Δt
```

For graphs, "distance" could be:
- Edge Jaccard: |E(t) △ E(t-Δ)| / |E(t) ∪ E(t-Δ)|
- Spectral distance: ‖L(t) - L(t-Δ)‖_F
- Node churn: |V(t) △ V(t-Δ)|

### 3. Per-node velocity
```
dπ_i/dt = (PageRank_i(now) - PageRank_i(then)) / Δt
```

File whose centrality is **increasing** = growing importance = watch closely.

### 4. Acceleration (is change speeding up?)
```
d²G/dt² = (dG/dt)|_now - (dG/dt)|_then
```

Positive acceleration = instability is increasing = warning sign.

### 5. Direction (what kind of change?)
```
Δ = Δ_structural + Δ_authorship + Δ_semantic
```

Decompose changes into orthogonal components.

## The Tensor Formulation

Define:
```
T[i, j, t, r] = strength of relationship r between files i,j at time t
```

Where r ∈ {IMPORTS, COCHANGES, SHARES_AUTHOR, SHARES_CONCEPT, ...}

This is a 4-tensor. Current code flattens this:
- Collapse t dimension → snapshot
- Collapse r dimension → separate matrices per relationship type
- Fuse at the end with weighted sums

**Proper approach**: Tensor decomposition (CP or Tucker)

```
T ≈ Σᵣ aᵣ ⊗ bᵣ ⊗ cᵣ ⊗ dᵣ
```

This discovers:
- **aᵣ, bᵣ**: File clusters that move together
- **cᵣ**: When these patterns are active
- **dᵣ**: Which relationship types matter

## Information-Theoretic Foundation

Let:
- X = structural features (graph topology)
- Y = behavioral features (change patterns)

### Key Quantities

| Quantity | Meaning | Healthy Value |
|----------|---------|---------------|
| H(Y\|X) | Uncertainty of changes given structure | Low |
| I(X; Y) | Mutual information: structure ↔ behavior | High |
| T(X→Y) | Transfer entropy: structure drives behavior | High |
| T(Y→X) | Transfer entropy: behavior drives structure | Low |

**Interpretation**:
- High I(X;Y): Imports predict co-changes. Structure reflects reality.
- Low I(X;Y): Files change together without import relationships. Hidden coupling.

```python
# Behavioral coherence
coherence = I(imports_graph; cochange_graph)

# Conway alignment  
conway = I(module_structure; author_teams)

# Architectural integrity
integrity = T(design→implementation) - T(implementation→design)
```

## Concrete Signals from Trajectory

| Signal | Definition | Meaning |
|--------|------------|---------|
| `graph_velocity` | ‖dG/dt‖ | How fast is topology changing? |
| `centrality_momentum[i]` | dπᵢ/dt | Is file i becoming more central? |
| `spectral_trend` | dλ₂/dt | Is graph getting more/less modular? |
| `structural_predictability` | I(G; ΔG) | Do graph properties predict changes? |
| `behavioral_coherence` | I(imports; cochanges) | Do imports predict co-change? |
| `trajectory_curvature` | ‖d²G/dt²‖ | Is change accelerating? |

## Risk Redefined

Risk isn't a weighted sum of features. It's a **trajectory property**:

```
risk(file) = f(
    position: where is file in graph now?
    velocity: how fast is its neighborhood changing?
    sensitivity: small changes here → large changes elsewhere?
    predictability: do changes follow structure?
    momentum: trending toward trouble?
)
```

Mathematically:
```
risk ∝ centrality × velocity × (1 - predictability) × sensitivity
```

Where sensitivity is like a local Lyapunov exponent: if I perturb this file, how much does the rest of the system change?

## The Hierarchy of Approximations

| Level | What It Computes | Cost | Accuracy |
|-------|------------------|------|----------|
| 0 | G(now) + Σ(change stats) | Low | Low |
| 1 | G(now) with edges weighted by cochange | Medium | Medium |
| 2 | Sample G(t) at N commits, trajectory features | High | High |
| 3 | Full tensor T[i,j,t,r], decomposition | Very High | Highest |

Current code is Level 0. 

Level 1 is achievable without reconstruction — just weight the current graph edges by temporal signal.

Level 2 requires reconstructing G at historical points (expensive but doable).

Level 3 is research-grade.

## The Practical Middle Ground

For Level 1 (achievable now):

```python
# Combined adjacency matrix
A_combined[i,j] = (
    α × has_import(i,j) +           # structural
    β × cochange_lift(i,j) +         # temporal
    γ × author_overlap(i,j) +        # social
    δ × concept_similarity(i,j)      # semantic
)

# Then ALL graph algorithms run on A_combined:
pagerank = PageRank(A_combined)
communities = Louvain(A_combined)
fiedler = Spectral(Laplacian(A_combined))
```

For Level 2 (future):

```python
# Sample graph at key commits
commits = sample_commits(history, n=20)
trajectory = [reconstruct_graph(c) for c in commits]

# Compute trajectory features
velocity = [graph_distance(trajectory[i], trajectory[i+1]) for i in range(n-1)]
centrality_history = [[pagerank(g)[file] for g in trajectory] for file in files]
```

## Summary: The Mathematical Framework

```
Codebase = Dynamical system on evolving graph G(t)

Signals = Features of trajectory {G(t)}
        = Position + Velocity + Acceleration + Curvature + Predictability

Risk = Trajectory instability measure
     = How likely is the system to move toward problematic states?

Health = Trajectory smoothness + Structure-behavior alignment
       = I(structure; behavior) + 1/‖dG/dt‖
```

Does this framework capture what you're thinking? Where should we go deeper?


### [Thinking]

The user loves the theoretical framework but is concerned about implementation. They want to go one layer deeper into how we'd actually build this.

Let me think about the practical implementation challenges:

1. **Reconstructing G(t)** - This is expensive. For each historical point, we'd need to:
   - Checkout the code at that commit
   - Parse all files
   - Build the import graph
   - This is O(commits × files × parse_time)

2. **Storage** - The full tensor T[i,j,t,r] could be huge:
   - n files × n files × k time windows × m relationship types
   - For n=1000, k=100, m=5 → 500 billion entries (sparse, but still)

3. **Incremental computation** - We don't want to recompute everything on each run

4. **Approximations** - What can we compute WITHOUT full reconstruction?

Let me think about what we CAN extract from git without reconstruction:

From git log alone:
- Which files existed at each commit (git ls-tree)
- Which files changed together (co-change)
- Who changed what (authorship)
- File renames (git log --follow or diff --find-renames)

What we CANNOT get without checkout+parse:
- Import relationships at historical points
- Function/class structure at historical points
- Semantic content at historical points

So the key insight is: we have FULL temporal data for:
- File existence: V(t)
- Co-change: which files changed together
- Authorship: who touched what

But we only have CURRENT snapshot for:
- Import graph: E_import(now)
- Semantic content: concepts(now)
- Syntax structure: functions, classes(now)

**The Hybrid Approach**

We can compute:
1. V(t) - file existence over time (cheap, from git)
2. Cochange(t) - co-change matrix over time (cheap, from git)


3. Authors(t) - authorship over time (cheap, from git)
4. E_import(now) - current import graph (we have this)

We CANNOT easily compute:
- E_import(t) for historical t

**The Approximation**

Key insight: Import relationships are relatively STABLE compared to file content. If file A imports file B today, it probably imported B for most of its history unless there was a major refactor. So we approximate the historical import graph by filtering the current one to only include files that existed at each point in time.

This breaks down when imports were added or removed, or when files underwent significant refactoring, but it's a reasonable starting point. We could refine this by parsing git diffs to detect when import statements were actually added or removed, extracting those changes without needing to reconstruct the entire historical graph.

The approach would involve analyzing diff output to identify import line additions and removals, then using those deltas to compute the import graph at any point in time by subtracting future additions and adding back future removals from the current state. This is far more efficient than full reconstruction.

For implementation, I'd structure this around a temporal graph data model that tracks both the current snapshot of nodes and edges alongside historical metadata from git—like when files were first created and when they were last modified. in self.node_birth.items() if birth <= t and self.node_death.get(n, float('inf')) > t}
        edges_t = {(a,b) for (a,b), birth in self.edge_birth.items()
                   if birth <= t and self.edge_death.get((a,b), float('inf')) > t
                   and a in nodes_t and b in nodes_t}

The reconstruction method filters nodes and edges based on their birth and death timestamps, keeping only those active at time t. The pipeline then extracts temporal primitives from git history without requiring checkouts—file timelines, import changes from diffs, co-change matrices per window, and authorship data. Phase 1 builds the temporal graph by reconstructing node and edge states.

Phase 2 computes trajectories across multiple dimensions: graph velocity measures structural change between windows, centrality trajectories track PageRank evolution, spectral analysis follows the second eigenvalue, and community detection applies Louvain clustering at each time point. Phase 3 derives features from these trajectories—velocity, acceleration, curvature, stability metrics, and information-theoretic measures like predictability and coherence between imports and co-changes. Finally, Phase 4 combines position, velocity, and sensitivity to estimate risk.

For storage, rather than maintaining a full tensor, I'm using sparse event representation. Each GraphEvent captures a timestamp, type (node/edge addition or removal), source/target nodes, and metadata like author or commit hash. The timeline is simply a list of these events, and I can reconstruct G(t) by replaying events up to any given timestamp.

This approach is efficient because commits rarely modify graph structure, so events are naturally sparse. Replay complexity scales with the number of events up to time t rather than all files, and overall storage is O(events) instead of O(files² × time).

For incremental updates, I check if a cached timeline exists, extract only new events since the last run, append them, and then recompute or incrementally update trajectory features. The extraction process queries for changes since a given commit hash.

I'm considering an approximation hierarchy with three levels. Level 0 uses the current approach—reconstructing G(now) from files and cochange from git logs. Level 1 approximates E_import(t) by intersecting current imports with files that existed at time t, which is cheaper but misses import changes. Level 2 parses diffs to track edge births and deaths, providing more accurate historical import edges.

For practical implementation, I need to extend git extraction to capture file renames and diff content, then build a language-specific import change extractor that works from diffs rather than full file checkouts. I'll implement a TemporalGraph structure to store the event timeline and enable efficient graph_at(t) queries, followed by trajectory analysis that samples time points and computes graph metrics and their derivatives at each point.

The information-theoretic measures should quantify imports and cochanges, then calculate H(changes | structure). Finally, I'll integrate these trajectory-based signals into the fusion layer to replace the current additive approach.


## ASSISTANT

Let me think through the implementation constraints and design a practical path.

## The Core Problem

**Full reconstruction is expensive:**
```
For each historical time t:
    git checkout commit_t        # O(files)
    parse all files              # O(files × parse_time)
    build import graph           # O(edges)
```

For 1000 commits × 500 files = millions of parse operations. Not practical.

## What We Can Get Cheaply from Git

| Data | Source | Cost |
|------|--------|------|
| File existence V(t) | `git ls-tree` | O(commits × files) - cheap |
| File co-change | `git log --name-only` | O(commits) - cheap |
| Authorship | `git log --format` | O(commits) - cheap |
| File renames | `git log --follow` | O(commits × files) - medium |
| Import changes | Parse diffs | O(commits × diff_size) - medium |

**What we CANNOT get cheaply:**
- Full import graph E(t) at historical points
- Semantic content at historical points
- Function/class structure at historical points

## The Key Insight

**Import relationships are stable.** If A imports B today, it probably did for most of its history.

Approximation:
```
E_import(t) ≈ E_import(now) ∩ {(a,b) : a ∈ V(t) ∧ b ∈ V(t)}
```

Current imports, filtered to files that existed at time t.

## Better: Diff-Based Edge Tracking

We CAN extract import changes from diffs without full checkout:

```python
def extract_import_changes(diff_text: str, language: str) -> tuple[list, list]:
    """Parse import additions/removals from a diff."""
    added, removed = [], []
    
    for line in diff_text.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            imp = parse_import_line(line[1:], language)
            if imp:
                added.append(imp)
        elif line.startswith('-') and not line.startswith('---'):
            imp = parse_import_line(line[1:], language)
            if imp:
                removed.append(imp)
    
    return added, removed
```

Then reconstruct edge history:
```
E(t) = E(now) - Σ{edges added after t} + Σ{edges removed after t}
```

## The Event-Sourced Data Model

Instead of storing snapshots, store **events**:

```python
@dataclass
class GraphEvent:
    timestamp: int          # unix timestamp
    commit_sha: str
    event_type: str         # 'node_add' | 'node_remove' | 'edge_add' | 'edge_remove'
    source: str             # file path (or source file for edges)
    target: str | None      # target file for edges
    author: str
    
@dataclass 
class TemporalGraphStore:
    events: list[GraphEvent]          # append-only log
    
    # Indexes for fast lookup
    node_birth: dict[str, int]        # file -> first_seen_timestamp
    node_death: dict[str, int]        # file -> removed_timestamp
    edge_birth: dict[tuple, int]      # (src, tgt) -> first_seen
    edge_death: dict[tuple, int]      # (src, tgt) -> removed
    
    def graph_at(self, t: int) -> Graph:
        """Reconstruct graph at time t by replaying events."""
        nodes = {n for n, birth in self.node_birth.items()
                 if birth <= t and self.node_death.get(n, INF) > t}
        edges = {e for e, birth in self.edge_birth.items()
                 if birth <= t and self.edge_death.get(e, INF) > t
                 and e[0] in nodes and e[1] in nodes}
        return Graph(nodes, edges)
```

**Storage cost**: O(events), not O(nodes² × time)
**Reconstruction cost**: O(events up to t)

## The Extraction Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: Raw Git Extraction (run once, cache result)       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  git log --all --name-status --follow --diff-filter=ADRM   │
│      ↓                                                      │
│  For each commit:                                           │
│    - files added (A) → node_add events                      │
│    - files deleted (D) → node_remove events                 │
│    - files renamed (R) → node identity mapping              │
│    - files modified (M) → parse diff for import changes     │
│                                                             │
│  Output: events.db (append-only event log)                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Build Temporal Indexes                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  From events.db:                                            │
│    - node_birth[file] = min(timestamp where file appears)   │
│    - node_death[file] = timestamp where file deleted        │
│    - edge_birth[(a,b)] = timestamp of import addition       │
│    - edge_death[(a,b)] = timestamp of import removal        │
│    - cochange_windows[t] = {(a,b): count} per time window   │
│    - author_windows[t][file] = Counter of authors           │
│                                                             │
│  Output: temporal_index.db                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Sample & Compute Trajectory                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Sample N time points: t₁, t₂, ..., tₙ                      │
│                                                             │
│  For each tᵢ:                                               │
│    G(tᵢ) = graph_at(tᵢ)           # reconstruct from index │
│    π(tᵢ) = PageRank(G(tᵢ))        # centrality             │
│    λ₂(tᵢ) = Fiedler(G(tᵢ))        # spectral               │
│    C(tᵢ) = Louvain(G(tᵢ))         # communities            │
│                                                             │
│  Output: trajectory.db                                      │
│    - graph_metrics[t] = {nodes, edges, density, ...}        │
│    - centrality[t][file] = pagerank                         │
│    - spectral[t] = {fiedler, gap, ...}                      │
│    - communities[t][file] = community_id                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Trajectory Features (Derivatives)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  graph_velocity[t] = distance(G(t), G(t-1))                 │
│  centrality_velocity[file] = d(pagerank)/dt                 │
│  spectral_velocity = d(fiedler)/dt                          │
│  community_stability[file] = entropy(community assignments) │
│                                                             │
│  Graph distance options:                                    │
│    - Edge Jaccard: |E₁ △ E₂| / |E₁ ∪ E₂|                    │
│    - Spectral: ‖L₁ - L₂‖_F                                  │
│    - Node Jaccard: |V₁ △ V₂| / |V₁ ∪ V₂|                    │
│                                                             │
│  Output: trajectory_features.db                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: Information-Theoretic Measures                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  behavioral_coherence = I(E_import; E_cochange)             │
│    - Do files that import each other change together?       │
│    - High = structure reflects behavior                     │
│    - Low = hidden coupling                                  │
│                                                             │
│  structural_predictability = I(G(t); ΔG(t+1))               │
│    - Does current structure predict future changes?         │
│                                                             │
│  conway_alignment = I(E_import; E_author_overlap)           │
│    - Does team structure match code structure?              │
│                                                             │
│  Output: information_metrics.db                             │
└─────────────────────────────────────────────────────────────┘
```

## Concrete Data Structures

```python
# ══════════════════════════════════════════════════════════════
# Layer 1: Event Storage (append-only, immutable)
# ══════════════════════════════════════════════════════════════

@dataclass
class GraphEvent:
    timestamp: int
    commit_sha: str
    event_type: Literal['node_add', 'node_remove', 'edge_add', 'edge_remove', 'rename']
    path: str                    # primary file
    target_path: str | None      # for edges: import target; for rename: new name
    author: str
    
# Storage: SQLite table or Parquet file
# events(timestamp, commit_sha, event_type, path, target_path, author)


# ══════════════════════════════════════════════════════════════
# Layer 2: Temporal Index (derived, rebuildable from events)
# ══════════════════════════════════════════════════════════════

@dataclass
class TemporalIndex:
    # Node lifecycle
    node_birth: dict[str, int]           # file -> first timestamp
    node_death: dict[str, int]           # file -> death timestamp (INF if alive)
    node_renames: dict[str, str]         # old_path -> canonical_path
    
    # Edge lifecycle  
    edge_birth: dict[tuple[str,str], int]
    edge_death: dict[tuple[str,str], int]
    
    # Windowed aggregates (e.g., 4-week windows)
    windows: list[TimeWindow]

@dataclass
class TimeWindow:
    start: int
    end: int
    cochange: dict[tuple[str,str], int]   # (a,b) -> count changed together
    author_counts: dict[str, Counter]      # file -> {author: count}
    churn: dict[str, int]                  # file -> change count


# ══════════════════════════════════════════════════════════════
# Layer 3: Trajectory (sampled graph states)
# ══════════════════════════════════════════════════════════════

@dataclass
class GraphSnapshot:
    timestamp: int
    node_count: int
    edge_count: int
    density: float
    
    # Centrality (sparse, only store non-trivial)
    pagerank: dict[str, float]
    betweenness: dict[str, float]
    
    # Spectral
    fiedler_value: float
    spectral_gap: float
    
    # Communities
    community_map: dict[str, int]     # file -> community_id
    modularity: float

@dataclass
class Trajectory:
    snapshots: list[GraphSnapshot]    # ordered by time
    sample_timestamps: list[int]
    
    def velocity_at(self, t: int) -> float:
        """Graph change rate at time t."""
        i = self._find_window(t)
        if i == 0:
            return 0.0
        return graph_distance(self.snapshots[i], self.snapshots[i-1])
    
    def centrality_velocity(self, file: str) -> list[float]:
        """d(pagerank)/dt for a file."""
        pr = [s.pagerank.get(file, 0.0) for s in self.snapshots]
        return np.diff(pr) / np.diff(self.sample_timestamps)


# ══════════════════════════════════════════════════════════════
# Layer 4: Trajectory Features (final signals)
# ══════════════════════════════════════════════════════════════

@dataclass  
class TrajectoryFeatures:
    # Global trajectory features
    mean_velocity: float              # average ‖dG/dt‖
    velocity_trend: float             # is velocity increasing?
    spectral_trend: float             # d(fiedler)/dt
    
    # Per-file trajectory features
    centrality_momentum: dict[str, float]    # d(pagerank)/dt per file
    community_stability: dict[str, float]    # how often file changes community
    existence_fraction: dict[str, float]     # what % of history did file exist?
    
    # Information-theoretic
    behavioral_coherence: float       # I(imports; cochanges)
    structural_predictability: float  # I(G(t); ΔG(t+1))
    conway_alignment: float           # I(modules; teams)
```

## The Incremental Update Strategy

```python
class TemporalAnalyzer:
    def __init__(self, cache_dir: Path):
        self.events_db = cache_dir / "events.db"
        self.index_db = cache_dir / "temporal_index.db"
        self.trajectory_db = cache_dir / "trajectory.db"
    
    def update(self, repo_path: Path) -> TrajectoryFeatures:
        # 1. Check what we have cached
        last_commit = self._get_last_processed_commit()
        current_head = get_head_sha(repo_path)
        
        if last_commit == current_head:
            # Nothing new, return cached features
            return self._load_cached_features()
        
        # 2. Extract only NEW events since last commit
        new_events = extract_events_since(repo_path, last_commit)
        self._append_events(new_events)
        
        # 3. Update indexes (incremental)
        self._update_temporal_index(new_events)
        
        # 4. Recompute affected trajectory windows
        affected_windows = {e.timestamp // WINDOW_SIZE for e in new_events}
        for w in affected_windows:
            self._recompute_snapshot(w)
        
        # 5. Recompute trajectory features
        return self._compute_trajectory_features()
```

## The Import Change Extractor

```python
# Language-specific import patterns
IMPORT_PATTERNS = {
    'python': [
        r'^import\s+([\w.]+)',
        r'^from\s+([\w.]+)\s+import',
    ],
    'javascript': [
        r"^import\s+.*from\s+['\"]([^'\"]+)['\"]",
        r"^const\s+\w+\s*=\s*require\(['\"]([^'\"]+)['\"]\)",
    ],
    'go': [
        r'^import\s+"([^"]+)"',
        r'^\s+"([^"]+)"',  # inside import block
    ],
    # ... other languages
}

def extract_import_events_from_diff(
    diff: str, 
    file_path: str,
    commit_sha: str,
    timestamp: int,
    author: str,
) -> list[GraphEvent]:
    """Parse a diff to extract import add/remove events."""
    
    language = detect_language(file_path)
    patterns = IMPORT_PATTERNS.get(language, [])
    events = []
    
    for line in diff.split('\n'):
        if not line.startswith(('+', '-')) or line.startswith(('+++', '---')):
            continue
            
        is_add = line.startswith('+')
        content = line[1:]
        
        for pattern in patterns:
            match = re.match(pattern, content.strip())
            if match:
                imported = match.group(1)
                resolved = resolve_import(imported, file_path)
                if resolved:
                    events.append(GraphEvent(
                        timestamp=timestamp,
                        commit_sha=commit_sha,
                        event_type='edge_add' if is_add else 'edge_remove',
                        path=file_path,
                        target_path=resolved,
                        author=author,
                    ))
    
    return events
```

## Summary: The Implementation Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Trajectory Features                               │
│  (what finders/fusion consume)                              │
│  centrality_momentum, behavioral_coherence, etc.            │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Trajectory                                        │
│  (sampled graph snapshots + derivatives)                    │
│  G(t₁), G(t₂), ..., velocity, acceleration                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Temporal Index                                    │
│  (efficient reconstruction support)                         │
│  node_birth, edge_birth, windowed cochange                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Event Log                                         │
│  (append-only, immutable source of truth)                   │
│  GraphEvent stream from git                                 │
├─────────────────────────────────────────────────────────────┤
│  Layer 0: Git Repository                                    │
│  (external, read-only)                                      │
└─────────────────────────────────────────────────────────────┘
```

Does this implementation architecture make sense? Should we go deeper on any specific layer?


### [Thinking]

The user wants me to forget about computational cost and focus on getting the theoretical framework correct, comprehensive, and logically consistent.

Let me think from first principles about what a codebase really is and how we should model it.

## First Principles

A codebase is a system that:
1. Has state (files, their content, their relationships)
2. Evolves over time (commits change the state)
3. Has multiple types of relationships (imports, co-change, authorship, semantic similarity)
4. Exists at multiple scales (functions, files, modules, codebase)

## The Fundamental Objects

### 1. The State at Time t

At any moment t, the codebase has:
- V(t) = set of files
- For each file v: content(v, t), syntax(v, t), semantics(v, t)
- Relationships between files

### 2. The Relationship Types

Between any two files, there can be multiple relationship types:
- IMPORTS: static dependency (A imports B)
- CALLS: dynamic dependency (function in A calls function in B)
- COCHANGES: behavioral coupling (A and B change together)
- SHARES_AUTHOR: social coupling (same people work on A and B)
- SHARES_CONCEPT: semantic coupling (A and B have similar concepts)
- CLONED_FROM: copy-paste relationship

Each relationship type forms its own graph.

### 3. The Multi-Layer Graph

At time t, we have a multi-layer graph:
```
M(t) = {
    G_import(t),
    G_call(t),
    G_cochange(t),
    G_author(t),
    G_semantic(t),
    G_clone(t),
}
```

### 4. The Temporal Evolution

The system evolves:
```
M(t₀) → M(t₁) → M(t₂) → ... → M(now)


```

Each transition is caused by commits (changes).

### 5. The Full Mathematical Object

The complete representation is a tensor:
```
T[i, j, t, r] = weight of relationship r between files i and j at time t
```

Or in event-sourced form:
```
Events = [(timestamp, relationship_type, source, target, weight, metadata), ...]
```

## The Signal Hierarchy

Now let's think about what signals we want to compute.

### Level 0: Raw Observations
These come directly from parsing files and git:
- File content, syntax trees
- Import statements
- Git commits, diffs, authors

### Level 1: Per-file and per-relationship metrics

I can compute basic properties from the raw observations—things like import counts, change frequency, authorship patterns, and semantic similarity scores. These form the foundation for higher-level analysis.

### Level 2: Structural properties from the dependency graph

The graph structure at any point in time reveals how files relate to each other: which ones are central hubs versus peripheral, which serve as bridges between clusters, and how they're organized into communities. I can measure these through pagerank, betweenness centrality, degree distributions, and clustering assignments.

### Level 3: Temporal evolution patterns

Files have lifecycles—they're born, grow, stabilize, or decay. I can track age, volatility through churn rates, and how their role in the system changes over time.

```
) = changes in window
- stability(v) = 1 / variance(changes)
- centrality_velocity(v) = d(pagerank)/dt
- community_stability(v) = how often changes community

### Level 4: Per-File Cross-Layer Signals
Computed from multiple relationship types:
- behavioral_coherence(v) = correlation between import neighbors and cochange neighbors
- conway_alignment(v) = correlation between import neighbors and author-overlap neighbors

### Level 5: Pairwise Signals
For pairs of files:
- coupling(a, b) = combined strength across all relationship types
- hidden_coupling(a, b) = cochange without import (behavioral but not declared)
- conway_violation(a, b) = strong import but different teams

### Level 6: Module/Cluster Signals
For groups of files:
- coh
```
esion(module) = internal edge density
- coupling(module) = external edge density
- instability(module) = Ce / (Ca + Ce)
- velocity(module) = aggregate change rate

At the global level, I'm tracking system-wide properties: modularity quality, overall health, and how stable the architecture remains over time. Then there are trajectory signals that capture meta-level patterns—whether the codebase is structurally changing, if modularity is improving or degrading, and whether risk is accumulating.

## The Computation DAG

Now let's think about dependencies between computations.

```
Raw Git Data ─────────────────────────────────────────┐
    │                                                 │
    ▼                                                 ▼
File Events                                      Change Events
(add, remove, rename)                            (modify, with diff)
    │                                                 │
    ├─────────────────┬───────────────────────────────┤
    │                 │                               │
    ▼                 ▼                               ▼
V(t)              Import Changes              Cochange Matrix
(files at t)      (from diffs)                (from commits)
    │                 │                               │
    └────────┬────────┘                               │
             │                                        │
             ▼                                        │
         G_import(t)                                  │
         (import graph at t)                          │
             │                                        │
             │                                        ▼
             │                                   G_cochange(t)
             │                                        │
             ├────────────────────────────────────────┤
             │                                        │
             ▼                                        ▼
      Graph Algorithms                         Temporal Algorithms
      (PageRank, Louvain,                      (churn, bus_factor,
       SCC, Spectral)                           trajectories)
             │                                        │
             └────────────────┬───────────────────────┘
                              │
                              ▼
                    Multi-Layer Fusion
                    (combine all relationship types)
                              │
                              ▼
                    Trajectory Analysis
                    (derivatives, trends)
                              │
                              ▼
                    Information-Theoretic
                    (mutual information, coherence)
                              │
                              ▼
                    Risk & Health Signals
                              │
                              ▼
                    Pattern Detection

Each relationship type r has distinct properties: a temporal graph G_r(t), edge semantics defining what connections represent, polarity indicating whether high values signal health or risk, and temporal characteristics showing stability or volatility patterns.

For imports, edges represent declared dependencies where module a depends on b's interface—structurally neutral but relatively stable across time. Calls capture runtime dependencies with edge weights as invocation counts, reflecting actual usage of b's implementation.

Cochanges measure behavioral coupling through lift statistics, identifying when modules change together beyond random chance. Author overlap quantifies social coupling by comparing developer sets across modules. Semantic coupling uses concept similarity to detect modules sharing vocabulary or domain concepts, all computed over sliding windows to capture evolving relationships.

Copy-paste detection identifies cloned content through normalized compression distance, flagged as negative since duplication typically indicates technical debt. Comparing these relationship types reveals hidden dependencies—high cochange without explicit imports suggests undeclared coupling—and Conway violations where import patterns misalign with organizational structure.

Semantic mismatches occur when modules import unrelated concepts, pointing to potential abstraction problems. At the file level, coherence measures whether declared dependencies align with actual behavioral dependencies through correlation. Globally, mutual information between the import and cochange graphs captures overall structural-behavioral alignment.

For temporal analysis, I can apply operators to any signal: instantaneous values at the current moment, windowed statistics like means and trends over time periods, derivatives showing rates of change and acceleration, and historical metrics including birth values and percentile distributions. The framework then organizes all signals across three dimensions—scope (file, pair, module), type (structural, behavioral, temporal), and temporal operator (instant, windowed, derivative, historical). rank | FILE | GRAPH | INSTANT | IMPORT |
| pagerank | FILE | GRAPH | INSTANT | COCHANGE |
| pagerank | FILE | GRAPH | INSTANT | COMBINED |
| churn | FILE | TEMPORAL | WINDOWED | - |
| centrality_velocity | FILE | GRAPH | TRAJECTORY | IMPORT |
| hidden_coupling | PAIR | CROSS | WINDOWED | IMPORT×COCHANGE |
| modularity | GLOBAL | GRAPH | INSTANT | IMPORT |
| modularity_trend | GLOBAL | GRAPH | TRAJECTORY | IMPORT |
| behavioral_coherence | GLOBAL | CROSS | WINDOWED | IMPORT×COCHANGE |

## The Computation Model

Now let's define how computations are structured:

### Primitive Extractors (from raw data)
```
extract_syntax(file

I can map out concrete signals using this framework—pagerank variants capture different relationship types at the file level, while churn tracks temporal patterns. Velocity metrics show how centrality evolves, and cross-source signals like hidden coupling combine multiple relationship dimensions. At the global scope, modularity and behavioral coherence reveal structural patterns and their changes over time.

The extraction layer pulls syntax, imports, commits, and diffs from source material. Graph builders then construct domain-specific networks—import graphs at specific timestamps, cochange graphs from commit windows, semantic and clone graphs from code analysis. Generic algorithms like pagerank, betweenness, and Louvain clustering operate across these different graph types.

Temporal analysis tracks how signals evolve through derivatives and windowed aggregation, computing velocity and acceleration on graph snapshots. Cross-layer operations reveal hidden couplings between import and cochange patterns, identify Conway's Law violations between architecture and team structure, and synthesize multiple graphs into unified representations.

Composite signals combine lower-level measurements—risk scores aggregate position and velocity signals weighted by sensitivity, while health scores integrate quality and coherence metrics to assess overall system state.

The architecture stratifies analysis across seven layers: foundational relationship graphs (imports, co-changes, authorship, semantic links) feed into graph-specific signals like pagerank and community detection, which then flow into trajectory analysis tracking how centrality and community structure evolve. Cross-layer signals like behavioral coherence and Conway alignment emerge from comparing patterns across relationship types, composite signals synthesize these into actionable scores, and finally detected patterns surface as findings like GOD_FILE or hidden coupling violations.

At the base, raw extraction pulls syntax trees, commits, and diffs from source files and version control. The temporal index layers these events into node and edge lifecycles with sliding windows. Each successive layer depends only on those beneath it, creating a clean dependency hierarchy that enables incremental computation and validation.

To compute `risk_score` for a file, the pipeline starts by extracting syntax information—lines, functions, complexity metrics—then identifies imports from that syntax. These imports feed into building an import graph at the current timestamp, which then gets analyzed through pagerank to determine centrality scores and blast radius calculations.

In parallel, commit history is extracted to build a cochange graph showing which files are modified together, while churn metrics and bus factor (authorship concentration) are computed from the same commit data. All these signals—structural complexity, dependency centrality, co-modification patterns, and team knowledge distribution—converge to produce the final risk assessment. ence,      │
                    │    ...          │
                    │  )              │
                    └─────────────────┘
```

The key insight is computing pagerank across multiple time points to capture how centrality evolves. From those snapshots, I can derive the velocity—the rate of change in centrality—which becomes a critical signal. This velocity component feeds into the fusion function alongside the static measures, allowing the risk model to account for whether a node's importance is rising, falling, or stable. Behavioral coherence and other temporal patterns then refine the final assessment.


## ASSISTANT

Let me rebuild this from first principles, comprehensive and logically consistent.

---

# The Complete Framework

## Part 1: The Fundamental Object

A codebase is a **dynamical system on a multi-layer network**.

### 1.1 State at Time t

```
S(t) = {
    V(t)           : set of files that exist at time t
    content(v, t)  : raw content of file v at time t
    syntax(v, t)   : parsed syntax tree of file v at time t
}
```

### 1.2 Relationship Types

Between any two files, there are **multiple relationship types**:

| Type | Notation | Definition | Source |
|------|----------|------------|--------|
| IMPORTS | R₁ | a statically depends on b | Parsing |
| CALLS | R₂ | function in a calls function in b | Parsing (deep) |
| COCHANGES | R₃ | a and b change together | Git |
| SHARES_AUTHOR | R₄ | same authors work on a and b | Git |
| SHARES_CONCEPT | R₅ | a and b have similar concepts | Semantics |
| CLONED_FROM | R₆ | a and b have duplicated content | NCD |

### 1.3 The Multi-Layer Graph

At time t, we have a **multi-layer graph**:

```
M(t) = ( V(t), {G_r(t) : r ∈ RelationshipTypes} )

where:
    G_r(t) = (V(t), E_r(t), W_r(t))
    E_r(t) ⊆ V(t) × V(t)           edges of type r
    W_r(t) : E_r(t) → ℝ⁺           edge weights
```

### 1.4 The Complete Mathematical Object

The full representation is a **4-tensor**:

```
T[i, j, t, r] = weight of relationship r between files i and j at time t

Dimensions:
    i, j ∈ [1, n_max]     files (including historical)
    t ∈ [1, T]            time points
    r ∈ [1, R]            relationship types
```

---

## Part 2: The Signal Taxonomy

Every signal is classified along **4 dimensions**:

### Dimension 1: Scope
```
FILE      : signal for a single file
PAIR      : signal for a pair of files  
MODULE    : signal for a group of files
CODEBASE  : signal for the entire system
```

### Dimension 2: Source Layer
```
SYNTAX    : from parsing file content
GRAPH     : from network structure
TEMPORAL  : from change history
SEMANTIC  : from concept extraction
CROSS     : from combining multiple sources
```

### Dimension 3: Time Reference
```
INSTANT   : value at current time t
WINDOWED  : aggregated over time window [t-w, t]
TRAJECTORY: derived from sequence of values over time
LIFECYCLE : about birth, death, age of entity
```

### Dimension 4: Relationship Type (for graph signals)
```
IMPORT    : from G_import
CALL      : from G_call
COCHANGE  : from G_cochange
AUTHOR    : from G_author
SEMANTIC  : from G_semantic
CLONE     : from G_clone
COMBINED  : from weighted combination of multiple graphs
```

### The Signal Space

A signal is fully specified by: `(scope, source, time_ref, rel_type)`

Examples:
```
pagerank         : (FILE, GRAPH, INSTANT, IMPORT)
pagerank_cochange: (FILE, GRAPH, INSTANT, COCHANGE)
pagerank_velocity: (FILE, GRAPH, TRAJECTORY, IMPORT)
churn_cv         : (FILE, TEMPORAL, WINDOWED, -)
hidden_coupling  : (PAIR, CROSS, WINDOWED, IMPORT×COCHANGE)
modularity       : (CODEBASE, GRAPH, INSTANT, IMPORT)
modularity_trend : (CODEBASE, GRAPH, TRAJECTORY, IMPORT)
coherence        : (CODEBASE, CROSS, WINDOWED, IMPORT×COCHANGE)
```

---

## Part 3: The Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 7: FINDINGS                                                  │
│  Pattern instances detected from signals                            │
│  (GOD_FILE, HIDDEN_COUPLING, CONWAY_VIOLATION, ...)                 │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 6: COMPOSITE SIGNALS                                         │
│  Weighted combinations of lower signals                             │
│  (risk_score, health_score, wiring_quality)                         │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 5: CROSS-LAYER SIGNALS                                       │
│  Computed from multiple relationship types                          │
│  (behavioral_coherence, conway_alignment, hidden_coupling)          │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 4: TRAJECTORY SIGNALS                                        │
│  Derivatives and trends over time                                   │
│  (centrality_velocity, spectral_trend, stability)                   │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 3: GRAPH SIGNALS                                             │
│  Computed from single-layer graphs                                  │
│  (pagerank[r], betweenness[r], community[r], depth[r])              │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 2: RELATIONSHIP GRAPHS                                       │
│  One graph per relationship type per time point                     │
│  (G_import(t), G_cochange(t), G_author(t), G_semantic(t), ...)      │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 1: TEMPORAL INDEX                                            │
│  Event log and lifecycle tracking                                   │
│  (events, node_birth, node_death, edge_birth, edge_death)           │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 0: RAW EXTRACTION                                            │
│  Primitives from files and git                                      │
│  (FileSyntax, Commits, Diffs, Authors)                              │
├─────────────────────────────────────────────────────────────────────┤
│  SOURCE: Files on disk + Git repository                             │
└─────────────────────────────────────────────────────────────────────┘
```

**Invariant**: Each layer only depends on layers below it.

---

## Part 4: Layer Specifications

### Layer 0: Raw Extraction

**Inputs**: Files on disk, Git repository

**Outputs**:

```python
@dataclass
class FileSyntax:
    path: str
    language: str
    content_hash: str
    lines: int
    functions: list[FunctionDef]
    classes: list[ClassDef]
    imports: list[Import]
    complexity: int
    
@dataclass
class GitCommit:
    sha: str
    timestamp: int
    author: str
    message: str
    
@dataclass
class GitFileChange:
    commit_sha: str
    file_path: str
    change_type: Literal['A', 'M', 'D', 'R']
    old_path: str | None        # for renames
    additions: int
    deletions: int
    diff_content: str | None    # for import extraction
```

**Extractors**:
```
extract_syntax(file_path, content) → FileSyntax
extract_commits(git_repo, since) → list[GitCommit]
extract_file_changes(git_repo, since) → list[GitFileChange]
```

---

### Layer 1: Temporal Index

**Inputs**: Layer 0 outputs

**Outputs**:

```python
@dataclass
class GraphEvent:
    timestamp: int
    event_type: Literal['node_add', 'node_remove', 'edge_add', 'edge_remove']
    relation_type: str          # 'IMPORT', 'COCHANGE', etc.
    source: str                 # file path
    target: str | None          # file path (for edges)
    weight: float
    metadata: dict              # commit_sha, author, etc.

@dataclass
class TemporalIndex:
    # Event log (append-only source of truth)
    events: list[GraphEvent]
    
    # Node lifecycle
    node_birth: dict[str, int]          # file → first_seen_timestamp
    node_death: dict[str, int]          # file → removed_timestamp
    node_canonical: dict[str, str]      # old_path → canonical_path (for renames)
    
    # Edge lifecycle (per relationship type)
    edge_birth: dict[str, dict[tuple, int]]   # rel_type → {(a,b) → timestamp}
    edge_death: dict[str, dict[tuple, int]]   # rel_type → {(a,b) → timestamp}
    
    # Time windows (for efficient queries)
    windows: list[TimeWindow]

@dataclass  
class TimeWindow:
    start_ts: int
    end_ts: int
    commits: list[str]                          # commit SHAs in window
    cochange_counts: dict[tuple[str,str], int]  # (a,b) → co-occurrence count
    author_counts: dict[str, Counter[str]]      # file → {author → commit_count}
    churn_counts: dict[str, int]                # file → change_count
```

**Builders**:
```
build_temporal_index(commits, file_changes, syntax_history) → TemporalIndex
```

---

### Layer 2: Relationship Graphs

**Inputs**: Layer 1 Temporal Index, Layer 0 FileSyntax

**Outputs**: One graph per relationship type, reconstructable at any time t

```python
@dataclass
class RelationshipGraph:
    relation_type: str
    timestamp: int                              # -1 for "current"
    nodes: set[str]
    edges: dict[str, list[str]]                 # adjacency list
    weights: dict[tuple[str, str], float]       # edge weights
    reverse: dict[str, list[str]]               # reverse adjacency

@dataclass
class MultiLayerGraph:
    timestamp: int
    nodes: set[str]
    layers: dict[str, RelationshipGraph]        # rel_type → graph
    
    def graph(self, rel_type: str) -> RelationshipGraph:
        return self.layers[rel_type]
    
    def combined(self, weights: dict[str, float]) -> RelationshipGraph:
        """Weighted combination of layers."""
        ...
```

**Graph Definitions**:

| Graph | Edge (a,b) exists if | Weight |
|-------|---------------------|--------|
| G_import | a imports b | 1.0 |
| G_call | function in a calls function in b | call_count |
| G_cochange | a,b co-occur in same commit | lift(a,b) |
| G_author | authors(a) ∩ authors(b) ≠ ∅ | Jaccard(authors) |
| G_semantic | concept_similarity(a,b) > θ | cosine_similarity |
| G_clone | NCD(a,b) < θ | 1 - NCD(a,b) |

**Builders**:
```
build_import_graph(index, t) → RelationshipGraph
build_cochange_graph(index, window) → RelationshipGraph
build_author_graph(index, window) → RelationshipGraph
build_semantic_graph(syntax_map, concepts) → RelationshipGraph
build_clone_graph(syntax_map, threshold) → RelationshipGraph
build_multi_layer_graph(index, t, window) → MultiLayerGraph
```

**Key Function**: Reconstruct any graph at any time

```python
def graph_at(index: TemporalIndex, rel_type: str, t: int) -> RelationshipGraph:
    """Reconstruct relationship graph at time t."""
    nodes = {n for n, birth in index.node_birth.items()
             if birth <= t and index.node_death.get(n, INF) > t}
    
    edge_births = index.edge_birth.get(rel_type, {})
    edge_deaths = index.edge_death.get(rel_type, {})
    
    edges = {(a,b) for (a,b), birth in edge_births.items()
             if birth <= t and edge_deaths.get((a,b), INF) > t
             and a in nodes and b in nodes}
    
    return RelationshipGraph(rel_type, t, nodes, to_adjacency(edges), ...)
```

---

### Layer 3: Graph Signals

**Inputs**: Layer 2 Relationship Graphs

**Outputs**: Per-node and global metrics for each graph

```python
@dataclass
class NodeGraphSignals:
    """Graph signals for a single node in a single relationship graph."""
    path: str
    relation_type: str
    timestamp: int
    
    # Centrality
    pagerank: float
    betweenness: float
    eigenvector: float
    
    # Degree
    in_degree: int
    out_degree: int
    
    # Position
    depth: int                  # BFS distance from entry points
    is_orphan: bool             # in_degree == 0 (context-dependent)
    
    # Community
    community_id: int
    
    # Reach
    blast_radius: int           # transitive closure size

@dataclass
class GlobalGraphSignals:
    """Graph signals for entire graph."""
    relation_type: str
    timestamp: int
    
    node_count: int
    edge_count: int
    density: float
    
    # Spectral
    fiedler_value: float        # algebraic connectivity
    spectral_gap: float
    
    # Community structure
    modularity: float
    community_count: int
    
    # Cycles
    cycle_count: int
    largest_scc_size: int
    
    # Inequality
    centrality_gini: float
```

**Algorithms** (generic, work on any RelationshipGraph):
```
pagerank(G, damping, iterations) → dict[node, float]
betweenness(G) → dict[node, float]
louvain(G) → (communities, modularity)
tarjan_scc(G) → list[set[node]]
spectral(G) → (fiedler, gap, eigenvectors)
bfs_depth(G, roots) → dict[node, int]
blast_radius(G) → dict[node, set[node]]
gini(values) → float
```

**Key Insight**: These algorithms are **parameterized by relationship type**:
```
pagerank_import = pagerank(G_import)
pagerank_cochange = pagerank(G_cochange)
pagerank_combined = pagerank(G_combined)
```

---

### Layer 4: Trajectory Signals

**Inputs**: Layer 3 signals at multiple time points

**Outputs**: Derivatives and temporal features

```python
@dataclass
class TrajectoryPoint:
    timestamp: int
    graph_signals: GlobalGraphSignals
    node_signals: dict[str, NodeGraphSignals]

@dataclass
class Trajectory:
    relation_type: str
    points: list[TrajectoryPoint]       # ordered by time
    
    def signal_over_time(self, node: str, signal: str) -> list[float]:
        """Get signal values for a node over time."""
        return [p.node_signals[node].__dict__[signal] 
                for p in self.points if node in p.node_signals]

@dataclass
class NodeTrajectorySignals:
    """Trajectory-derived signals for a node."""
    path: str
    relation_type: str
    
    # Derivatives
    centrality_velocity: float          # d(pagerank)/dt
    centrality_acceleration: float      # d²(pagerank)/dt²
    
    # Stability
    community_stability: float          # 1 - entropy(community assignments)
    degree_stability: float             # 1 - cv(degree over time)
    
    # Lifecycle
    age: int                            # now - birth
    existence_fraction: float           # time_existed / total_history

@dataclass
class GlobalTrajectorySignals:
    """Trajectory-derived signals for entire codebase."""
    relation_type: str
    
    # Graph velocity
    graph_velocity: float               # mean(‖G(t) - G(t-1)‖)
    graph_acceleration: float           # d(velocity)/dt
    
    # Spectral trends
    fiedler_trend: float                # d(fiedler)/dt
    modularity_trend: float             # d(modularity)/dt
    
    # Stability
    topology_stability: float           # 1 - graph_velocity
```

**Operators**:
```
derivative(values, timestamps) → velocities
second_derivative(values, timestamps) → accelerations  
window_mean(values, window_size) → smoothed
window_std(values, window_size) → volatility
trend(values, timestamps) → slope
```

**Graph Distance Functions**:
```
edge_jaccard(G1, G2) = |E1 △ E2| / |E1 ∪ E2|
spectral_distance(G1, G2) = ‖L1 - L2‖_F
node_jaccard(G1, G2) = |V1 △ V2| / |V1 ∪ V2|
```

---

### Layer 5: Cross-Layer Signals

**Inputs**: Multiple Layer 2 graphs, Layer 3 signals

**Outputs**: Signals derived from comparing relationship types

```python
@dataclass
class CrossLayerSignals:
    """Signals from comparing relationship types."""
    
    # Information-theoretic (global)
    behavioral_coherence: float         # I(G_import; G_cochange)
    conway_alignment: float             # I(G_import; G_author)
    semantic_structural_alignment: float # I(G_import; G_semantic)
    
    # Correlation-based (global)
    import_cochange_correlation: float  # corr(A_import, A_cochange)
    
    # Structural predictability
    structural_predictability: float    # I(G(t); ΔG(t+1))

@dataclass
class NodeCrossLayerSignals:
    """Cross-layer signals for a single node."""
    path: str
    
    # Neighborhood coherence
    neighborhood_coherence: float       # overlap of neighbors across layers
    
    # Hidden coupling exposure
    hidden_coupling_count: int          # cochange neighbors not in import neighbors
    
    # Conway violation exposure
    conway_violation_count: int         # import neighbors with no author overlap

@dataclass  
class PairCrossLayerSignals:
    """Cross-layer signals for a pair of files."""
    source: str
    target: str
    
    # Coupling types
    declared_coupling: bool             # exists in G_import
    behavioral_coupling: float          # weight in G_cochange
    social_coupling: float              # weight in G_author
    semantic_coupling: float            # weight in G_semantic
    
    # Derived
    hidden_coupling: float              # behavioral × (1 - declared)
    conway_violation: float             # declared × (1 - social)
    semantic_mismatch: float            # declared × (1 - semantic)
```

**Algorithms**:
```
mutual_information(G1, G2) → float
    # I(X;Y) where X,Y are adjacency matrix entries
    
neighborhood_overlap(v, G1, G2) → float
    # |N_G1(v) ∩ N_G2(v)| / |N_G1(v) ∪ N_G2(v)|

hidden_coupling_pairs(G_import, G_cochange, threshold) → list[(a, b, strength)]
    # pairs with high cochange but no import

conway_violation_pairs(G_import, G_author, threshold) → list[(a, b, strength)]
    # pairs with import but low author overlap
```

---

### Layer 6: Composite Signals

**Inputs**: All lower layer signals

**Outputs**: Weighted combinations for decision-making

```python
@dataclass
class FileCompositeSignals:
    path: str
    
    # Risk (higher = more dangerous to change)
    risk_score: float
    
    # Quality (higher = better)
    wiring_quality: float
    health_score: float
    
    # Laplacian (relative to neighbors)
    delta_h: float              # health - mean(neighbor health)

@dataclass
class ModuleCompositeSignals:
    path: str
    
    health_score: float
    architecture_quality: float

@dataclass
class CodebaseCompositeSignals:
    wiring_score: float
    architecture_health: float
    team_risk: float
    codebase_health: float
```

**Formulas** (now including trajectory signals):

```python
def compute_risk_score(
    node: str,
    graph_signals: NodeGraphSignals,           # Layer 3
    trajectory_signals: NodeTrajectorySignals, # Layer 4
    cross_signals: NodeCrossLayerSignals,      # Layer 5
    temporal_signals: ChurnSignals,            # From temporal
) -> float:
    """
    Risk combines:
    - Position: how important is this file? (centrality)
    - Velocity: how fast is importance changing? (trajectory)
    - Impact: what breaks if this changes? (blast radius)
    - Instability: how unpredictable are changes? (churn)
    - Knowledge: who knows this code? (bus factor)
    - Coupling: hidden dependencies? (cross-layer)
    """
    return (
        0.15 * normalize(graph_signals.pagerank)
      + 0.10 * normalize(abs(trajectory_signals.centrality_velocity))  # NEW
      + 0.15 * normalize(graph_signals.blast_radius)
      + 0.15 * normalize(temporal_signals.churn_cv)
      + 0.15 * (1 - temporal_signals.bus_factor / 5.0)
      + 0.15 * normalize(cross_signals.hidden_coupling_count)          # NEW
      + 0.15 * (1 - trajectory_signals.community_stability)            # NEW
    )
```

```python
def compute_behavioral_coherence(
    G_import: RelationshipGraph,
    G_cochange: RelationshipGraph,
) -> float:
    """
    Mutual information between import structure and change behavior.
    High = imports predict co-changes (good architecture)
    Low = hidden coupling (bad architecture)
    """
    return mutual_information(G_import.adjacency_matrix, G_cochange.adjacency_matrix)
```

---

### Layer 7: Findings (Patterns)

**Inputs**: All signals from Layers 3-6

**Outputs**: Detected pattern instances

```python
@dataclass
class Finding:
    pattern: str                # e.g., "HIDDEN_COUPLING"
    scope: str                  # FILE, PAIR, MODULE, CODEBASE
    target: str | tuple         # file path or (file_a, file_b)
    severity: float             # 0-1
    confidence: float           # 0-1
    evidence: dict[str, Any]    # signal values that triggered
    
# Pattern definitions
PATTERNS = {
    "HIDDEN_COUPLING": {
        "scope": "PAIR",
        "condition": lambda cross: cross.hidden_coupling > 0.5,
        "severity": lambda cross: cross.hidden_coupling,
    },
    "CONWAY_VIOLATION": {
        "scope": "PAIR",
        "condition": lambda cross: cross.conway_violation > 0.5,
        "severity": lambda cross: cross.conway_violation,
    },
    "RISING_RISK": {                                            # NEW
        "scope": "FILE",
        "condition": lambda traj: traj.centrality_velocity > 0.1 
                               and traj.community_stability < 0.5,
        "severity": lambda traj: traj.centrality_velocity,
    },
    "ARCHITECTURAL_DECAY": {                                    # NEW
        "scope": "CODEBASE",
        "condition": lambda global_traj: global_traj.modularity_trend < -0.05,
        "severity": lambda global_traj: abs(global_traj.modularity_trend),
    },
}
```

---

## Part 5: The Computation DAG

```
                    ┌─────────────────────────────────────┐
                    │          FILES + GIT                │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │          LAYER 0                    │
                    │       Raw Extraction                │
                    ├─────────────────────────────────────┤
                    │  FileSyntax    Commits    Diffs     │
                    └──────┬──────────┬──────────┬────────┘
                           │          │          │
                    ┌──────┴──────────┴──────────┴────────┐
                    │          LAYER 1                    │
                    │      Temporal Index                 │
                    ├─────────────────────────────────────┤
                    │  events, node_lifecycle,            │
                    │  edge_lifecycle, windows            │
                    └──────────────┬──────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │ G_import  │           │ G_cochange│           │ G_author  │  ... (other layers)
    │   (t)     │           │   (t)     │           │   (t)     │
    └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
          │          LAYER 2      │                       │
          │    Relationship       │                       │
          │       Graphs          │                       │
          └───────────┬───────────┴───────────────────────┘
                      │
                      ▼
          ┌───────────────────────────────────────────────┐
          │                  LAYER 3                      │
          │              Graph Signals                    │
          ├───────────────────────────────────────────────┤
          │  Per-graph: pagerank[r], betweenness[r],      │
          │             communities[r], spectral[r]       │
          └───────────────────────┬───────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌─────────────────┐         ┌─────────────────┐
          │    LAYER 4      │         │    LAYER 5      │
          │   Trajectory    │         │   Cross-Layer   │
          │    Signals      │         │    Signals      │
          ├─────────────────┤         ├─────────────────┤
          │ velocity,       │         │ coherence,      │
          │ acceleration,   │         │ hidden_coupling,│
          │ stability       │         │ conway_violation│
          └────────┬────────┘         └────────┬────────┘
                   │                           │
                   └─────────────┬─────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────────────┐
                    │           LAYER 6                   │
                    │      Composite Signals              │
                    ├─────────────────────────────────────┤
                    │  risk_score, health_score,          │
                    │  wiring_quality, delta_h            │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │           LAYER 7                   │
                    │          Findings                   │
                    ├─────────────────────────────────────┤
                    │  Pattern instances detected         │
                    └─────────────────────────────────────┘
```

---

## Part 6: Summary of Key Principles

### 1. The Tensor View
The codebase is a 4-tensor T[file, file, time, relation_type]. All analysis is operations on this tensor.

### 2. Multi-Layer Graphs  
There are R relationship types, each forming its own graph. Signals can be computed on any layer or combinations.

### 3. Trajectory First
Every instantaneous signal has a trajectory counterpart. Velocity and acceleration are first-class citizens.

### 4. Cross-Layer Coherence
The most important signals come from **comparing** relationship types:
- Import structure vs behavioral coupling → hidden dependencies
- Import structure vs social structure → Conway violations
- Structure vs trajectory → architectural decay

### 5. Layered Computation
Each layer only depends on layers below. This enables:
- Clear reasoning about dependencies
- Incremental computation
- Caching at each layer

### 6. Principled Risk
Risk is not a heuristic weighted sum. It's:
```
Risk = f(position, velocity, impact, predictability, coupling)
```
Where each term has a clear mathematical definition.

---

Does this framework feel comprehensive and consistent? Should we refine any part?


### [Thinking]

The user wants to continue refining and defining this framework further. Let me think about what aspects we should flesh out more:

1. **The tensor operations** - we defined T[i,j,t,r] but haven't specified the actual operations
2. **The relationship type algebra** - how do we combine graphs? What are the valid operations?
3. **The temporal operators** - we mentioned derivatives but need to formalize them
4. **The information-theoretic measures** - mutual information, entropy, etc. need precise definitions
5. **The signal dependencies** - which signals depend on which others?
6. **The normalization/scaling** - how do we make signals comparable?
7. **The aggregation rules** - how do file signals become module signals become codebase signals?
8. **The complete signal catalog** - enumerate ALL signals with their exact definitions

Let me build this out systematically.

## 1. Tensor Operations

The fundamental tensor T[i,j,t,r] supports these operations:

### Slicing
- T[:,:,t,:] = multi-layer graph at time t
- T[:,:,:,r] = temporal evolution of relationship r
- T[i,:,t,r] = neighbors of i in layer r at time t
- T[i,j,:,r] = time series of relationship r between i and j

### Reduction
- sum over t = cumulative relationship strength
- mean over r = combined relationship strength
- max over t = peak relationship strength

### Transformation
- Normalize along dimensions
- Threshold (binarize)
- Symmetrize (for undirected)

## 2. Relationship Type Algebra

### Graph Combination Operations

**Union**: G₁ ∪ G₂
- Edges from either graph
- Weight = max(w₁, w₂) or sum(w₁, w₂)

**Intersection**: G₁ ∩ G₂  


- Edges present in both graphs
- Weight = min(w₁, w₂) or product(w₁, w₂)

**Difference**: G₁ \ G₂
- Edges in G₁ but not G₂
- This gives "hidden coupling" when G₁=cochange, G₂=import

**Weighted Combination**: Σᵣ αᵣ Gᵣ
- Combined adjacency matrix
- A_combined = Σᵣ αᵣ Aᵣ

**Product**: G₁ ⊗ G₂
- Edge weight = product of weights
- This gives "confirmed coupling" (strong in both)

### Derived Relationship Types

From the 6 primitive types, we can derive:

| Derived Type | Definition | Meaning |
|--------------|------------|---------|
| HIDDEN_COUPLING | G_cochange \ G_import | Behavioral but undeclared |
| CONFIRMED_COUPLING | G_import ∩ G_cochange | Declared and behavioral |
| DEAD_IMPORT | G_import \ G_cochange | Declared but unused |
| CONWAY_VIOLATION | G_import \ G_author | Dependency across team boundaries |
| CONWAY_ALIGNED | G_import ∩ G_author | Dependency within team |
| SEMANTIC_MISMATCH | G_import \ G_semantic | Import unrelated concepts |
| COMBINED | Σᵣ αᵣ Gᵣ | Weighted combination |

## 3. Temporal Operators

For signals tracked over time, I can extract values at specific moments or analyze patterns within windows. Point operators give me snapshots—either the current state or a value at some past time. Window-based operators let me compute statistics like averages, variability, and trends across a time range. Derivative operators capture how signals change, measuring both first-order rates of change and acceleration.

Beyond these basic measurements, lifecycle operators track when signals emerge and disappear, calculating their age or total duration. Stability operators quantify how consistent a signal remains relative to its typical magnitude. Information-theoretic measures then let me compare how much two signals share in common or diverge from each other. I(G₁; G₂) = H(G₁) + H(G₂) - H(G₁, G₂) for binary adjacency matrices, where H represents the entropy of the edge distribution.

The normalized version scales this by dividing by the sum of individual entropies: NMI(G₁, G₂) = 2 I(G₁; G₂) / (H(G₁) + H(G₂)).

Conditional entropy H(G₁ | G₂) = H(G₁, G₂) - H(G₂) captures the remaining uncertainty about one graph given knowledge of the other.

For signal analysis, transfer entropy T(X→Y) = I(Y(t+1); X(t) | Y(t)) quantifies causal influence by measuring how much past values of X improve predictions of Y's future beyond Y's own history. The entropy of a distribution itself is H(s) = -Σᵢ p(sᵢ) log p(sᵢ), providing the baseline uncertainty measure.

The catalog begins with raw file metrics: line counts, function and class definitions, import statements, cyclomatic complexity, maximum nesting depth, and content hashing. Temporal signals from git history include birth and death timestamps, age calculations, and total modifications tracked across commits.

Windowed temporal metrics capture activity within a specific time window—commits, distinct authors, additions, deletions, and churn rates. Derived temporal signals build on these foundations to compute higher-level patterns.

Churn statistics measure volatility: mean and standard deviation of changes per window, with coefficient of variation normalizing across files. A linear trend captures whether churn is accelerating or stabilizing. Author entropy quantifies distribution diversity among contributors, with bus factor indicating how concentrated knowledge is (higher values mean more distributed). Commit classification ratios distinguish fix-oriented versus refactor-oriented work. Graph signals then extend analysis to relationships between files.

| in_degree[r] | FILE | int | Number of incoming edges in Gᵣ |
| out_degree[r] | FILE | int | Number of outgoing edges in Gᵣ |
| degree[r] | FILE | int | in_degree + out_degree |
| pagerank[r] | FILE | float | PageRank centrality in Gᵣ |
| betweenness[r] | FILE | float | Betweenness centrality in Gᵣ |
| eigenvector[r] | FILE | float | Eigenvector centrality in Gᵣ |
| clustering[r] | FILE | float | Local clustering coefficient |
| depth[r] | FILE | int | BFS distance from entry points |
| blast_radius[r] | FILE | int | Size of transitive closure |
| community

[r] | FILE | int | Community ID from Louvain |
| is_orphan[r] | FILE | bool | in_degree[r] == 0 |

### Layer 3: Global Graph Signals (per relationship type r)

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| node_count[r] | CODEBASE | int | Number of nodes in Gᵣ |
| edge_count[r] | CODEBASE | int | Number of edges in Gᵣ |
| density[r] | CODEBASE | float | edge_count / (node_count × (node_count-1)) |
| fiedler[r] | CODEBASE | float | Second smallest eigenvalue of Laplacian |
| spectral_gap[r] | CODEBASE | float | λ₃ - λ₂ |
| modularity[r] | CODEBASE | float | Modularity score from Louvain |
| community_count[r] | CODEBASE | int | Number of communities |
| scc_count[r] | CODEBASE | int | Number of non-trivial SCCs |
| largest_scc[r] | CODEBASE | int | Size of largest SCC |
| centrality_gini[r] | CODEBASE | float | Gini of pagerank distribution |

### Layer 4: Trajectory Signals

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| pagerank_velocity | FILE | float | d(pagerank)/dt |
| pagerank_acceleration | FILE | float | d²(pagerank)/dt² |
| degree_velocity | FILE | float | d(degree)/dt |
| community_changes | FILE | int | Number of community changes |
| community_stability | FILE | float | 1 - community_changes/observations |
| existence_fraction | FILE | float | (time alive) / (total history) |
| graph_velocity | CODEBASE | float | mean(‖G(t) - G(t-1)‖) |
| fiedler_trend | CODEBASE | float | d(fiedler)/dt |
| modularity_trend | CODEBASE | float | d(modularity)/dt |
| topology_stability | CODEBASE | float | 1 / (1 + graph_velocity) |

### Layer 5: Cross-Layer Signals

|
| hidden_coupling_count | FILE | int | |N_cochange(v) \ N_import(v)| |
| dead_import_count | FILE | int | |N_import(v) \ N_cochange(v)| |
| conway_violation_count | FILE | int | |N_import(v) \ N_author(v)| |
| neighborhood_coherence | FILE | float | |N_import ∩ N_cochange| / |N_import ∪ N_cochange| |
| hidden_coupling | PAIR | float | cochange(a,b) × (1 - import(a,b)) |
| dead_import | PAIR | float |
import(a,b) × (1 - cochange(a,b)) |
| conway_violation | PAIR | float | import(a,b) × (1 - author_overlap(a,b)) |
| semantic_mismatch | PAIR | float | import(a,b) × (1 - semantic_sim(a,b)) |

At the codebase level, I'm measuring mutual information between different graph structures. Behavioral coherence captures how well import dependencies align with actual change patterns, while conway alignment checks whether the dependency graph matches team structure. Semantic alignment and structural predictability extend this to semantic relationships and temporal evolution.

For individual files, I calculate a risk score and wiring quality by combining orphan, stub, and phantom penalties. Health scores aggregate multiple factors, and delta_h measures how a file's health compares to its neighbors. At the module level, I'm tracking cohesion through internal edge density, coupling via external connections, instability as the ratio of efferent to total coupling, and abstractness based on the proportion of abstract files.

The main sequence distance captures deviation from the ideal A + I = 1 relationship, while module health combines these architectural metrics. For the entire codebase, wiring score penalizes orphaned and phantom modules, architecture health reflects overall structural quality, team risk incorporates bus factor and knowledge distribution, and codebase health serves as the aggregate health indicator.

Signals aggregate differently depending on scope. From file to module level, sum captures totals like lines and commits, mean averages complexity and churn metrics, max identifies peak risk values, min finds minimum thresholds, and standard deviation plus Gini and entropy coefficients measure variability and inequality. Weighted means account for importance factors. The same approach applies when rolling module signals up to codebase level. Graph-based signals follow a different path—they're computed on the induced subgraph rather than through simple aggregation.

Normalization depends on the signal type and comparison context. Min-max scaling works for bounded metrics, z-scores for unbounded distributions, percentile ranking for outlier robustness, and log transformation for heavy-tailed data. Cross-codebase comparisons benefit from percentile-based or research-backed absolute thresholds. Polarity matters too—some signals improve when higher, others when lower.

The complete data model organizes analysis results hierarchically: metadata (timestamp, commit, path), raw syntax data, temporal indexing, and graph structures.

Graphs store relationship types across time periods. Graph signals are computed at both node and global levels for each relationship type. Trajectory signals track how node and global metrics evolve. Cross-layer signals integrate information across nodes and node pairs.

The structure culminates in composite signals aggregated at file, module, and codebase levels, with findings extracted as the final output layer.


## ASSISTANT

Let me define and refine each component precisely.

---

# Complete Framework Definition

## Part 1: The Tensor and Its Operations

### 1.1 The Fundamental Tensor

```
T ∈ ℝ^(N × N × K × R)

where:
    N = maximum number of files across all time
    K = number of time points
    R = number of relationship types
    
    T[i, j, t, r] = weight of relationship r between files i and j at time t
                   = 0 if either file doesn't exist at time t
```

### 1.2 Tensor Slicing Operations

| Slice | Notation | Result | Meaning |
|-------|----------|--------|---------|
| Fix time, fix relation | T[:,:,t,r] | N×N matrix | Graph Gᵣ at time t |
| Fix relation | T[:,:,:,r] | N×N×K tensor | Evolution of Gᵣ |
| Fix time | T[:,:,t,:] | N×N×R tensor | Multi-layer graph at t |
| Fix node pair | T[i,j,:,:] | K×R matrix | All relationships between i,j over time |
| Fix source node | T[i,:,t,r] | N vector | Neighbors of i in Gᵣ(t) |

### 1.3 Tensor Reduction Operations

| Operation | Notation | Definition | Use Case |
|-----------|----------|------------|----------|
| Sum over time | Σₜ T[:,:,t,r] | Cumulative relationship | Total co-change |
| Mean over time | (1/K) Σₜ T[:,:,t,r] | Average relationship | Stable coupling |
| Max over time | maxₜ T[i,j,t,r] | Peak relationship | Maximum coupling |
| Sum over relations | Σᵣ αᵣ T[:,:,t,r] | Combined graph | Multi-layer fusion |

### 1.4 Tensor-Derived Matrices

```python
# Adjacency matrix for relation r at time t
A[r,t] = T[:,:,t,r]

# Degree matrix  
D[r,t][i,i] = Σⱼ A[r,t][i,j]

# Laplacian
L[r,t] = D[r,t] - A[r,t]

# Normalized Laplacian
L_norm[r,t] = I - D[r,t]^(-1/2) A[r,t] D[r,t]^(-1/2)

# Transition matrix (for PageRank)
P[r,t] = D[r,t]^(-1) A[r,t]
```

---

## Part 2: Relationship Type Algebra

### 2.1 Primitive Relationship Types

| ID | Type | Edge (a→b) exists if | Weight W(a,b) | Directed | Source |
|----|------|---------------------|---------------|----------|--------|
| R₁ | IMPORTS | a has import statement for b | 1.0 | Yes | Parsing |
| R₂ | CALLS | function in a calls function in b | call_count | Yes | Deep parsing |
| R₃ | COCHANGES | a,b in same commit | lift(a,b) | No | Git |
| R₄ | AUTHOR_OVERLAP | authors(a) ∩ authors(b) ≠ ∅ | Jaccard | No | Git |
| R₅ | CONCEPT_SIMILAR | concepts(a) · concepts(b) > θ | cosine_sim | No | Semantics |
| R₆ | CLONE | NCD(a,b) < θ | 1 - NCD | No | Content |

### 2.2 Edge Weight Definitions

**COCHANGES weight (lift)**:
```
lift(a,b) = P(a,b) / (P(a) × P(b))
         = (commits containing both a,b) × (total commits) / 
           (commits containing a) × (commits containing b)

lift > 1 → co-change more than random
lift = 1 → independent
lift < 1 → anti-correlated
```

**AUTHOR_OVERLAP weight (Jaccard)**:
```
jaccard(a,b) = |authors(a) ∩ authors(b)| / |authors(a) ∪ authors(b)|
```

**CONCEPT_SIMILAR weight (cosine)**:
```
cosine(a,b) = concepts(a) · concepts(b) / (‖concepts(a)‖ × ‖concepts(b)‖)
```

**CLONE weight (1 - NCD)**:
```
NCD(a,b) = (C(a+b) - min(C(a), C(b))) / max(C(a), C(b))
where C(x) = compressed size of x
```

### 2.3 Graph Combination Operations

**Binary Operations on Graphs**:

| Operation | Notation | Edge Set | Weight | Meaning |
|-----------|----------|----------|--------|---------|
| Union | G₁ ∪ G₂ | E₁ ∪ E₂ | max(w₁,w₂) | Either relationship |
| Intersection | G₁ ∩ G₂ | E₁ ∩ E₂ | min(w₁,w₂) | Both relationships |
| Difference | G₁ \ G₂ | E₁ \ E₂ | w₁ | Only in G₁ |
| Product | G₁ ⊗ G₂ | E₁ ∩ E₂ | w₁ × w₂ | Confirmed by both |

**Linear Combination**:
```
G_combined = Σᵣ αᵣ Gᵣ

A_combined[i,j] = Σᵣ αᵣ Aᵣ[i,j]

Constraint: Σᵣ αᵣ = 1 for normalized combination
```

### 2.4 Derived Relationship Types

| Derived Type | Definition | Formula | Interpretation |
|--------------|------------|---------|----------------|
| HIDDEN_COUPLING | Cochange without import | G₃ \ (G₁ ∪ G₁ᵀ) | Undeclared dependency |
| CONFIRMED_COUPLING | Import and cochange | G₁ ∩ G₃ | Validated dependency |
| DEAD_IMPORT | Import without cochange | G₁ \ G₃ | Possibly unused |
| CONWAY_VIOLATION | Import without author overlap | G₁ \ G₄ | Cross-team dependency |
| CONWAY_ALIGNED | Import with author overlap | G₁ ∩ G₄ | Same-team dependency |
| SEMANTIC_MISMATCH | Import without concept similarity | G₁ \ G₅ | Conceptual disconnect |

---

## Part 3: Temporal Operators

### 3.1 Signal Notation

For a signal s defined over entities and time:
```
s: Entity × Time → ℝ
s(v, t) = value of signal s for entity v at time t
s(v) = s(v, now)  [shorthand for current value]
```

### 3.2 Point Operators

| Operator | Notation | Definition |
|----------|----------|------------|
| Current | s(v) | s(v, t_now) |
| At time | s(v, t) | Value at specific time |
| At birth | s₀(v) | s(v, birth(v)) |
| At death | s_end(v) | s(v, death(v)) |

### 3.3 Window Operators

For window w = [t-Δ, t]:

| Operator | Notation | Definition |
|----------|----------|------------|
| Window mean | μ_w(s, v) | (1/\|w\|) Σ_{τ∈w} s(v, τ) |
| Window std | σ_w(s, v) | √(Var_{τ∈w}(s(v, τ))) |
| Window min | min_w(s, v) | min_{τ∈w} s(v, τ) |
| Window max | max_w(s, v) | max_{τ∈w} s(v, τ) |
| Window sum | Σ_w(s, v) | Σ_{τ∈w} s(v, τ) |
| Window trend | β_w(s, v) | Linear regression slope in w |

### 3.4 Derivative Operators

| Operator | Notation | Definition | Interpretation |
|----------|----------|------------|----------------|
| Velocity | Ds(v, t) | (s(v,t) - s(v,t-Δ)) / Δ | Rate of change |
| Acceleration | D²s(v, t) | (Ds(v,t) - Ds(v,t-Δ)) / Δ | Change of rate |
| Smoothed velocity | D̄s(v, t) | β_w(s, v) | Trend (robust) |

### 3.5 Lifecycle Operators

| Operator | Notation | Definition |
|----------|----------|------------|
| Birth time | birth(v) | min{t : v ∈ V(t)} |
| Death time | death(v) | max{t : v ∈ V(t)} or ∞ |
| Age | age(v) | t_now - birth(v) |
| Lifespan | lifespan(v) | death(v) - birth(v) |
| Alive fraction | alive(v) | lifespan(v) / (t_now - t_0) |

### 3.6 Stability Operators

| Operator | Notation | Definition | Range |
|----------|----------|------------|-------|
| Coefficient of variation | cv(s, v) | σ(s,v) / μ(s,v) | [0, ∞) |
| Stability | stability(s, v) | 1 / (1 + cv(s,v)) | (0, 1] |
| Entropy | H(s, v) | -Σ p(s) log p(s) | [0, log n] |

---

## Part 4: Information-Theoretic Measures

### 4.1 Entropy Definitions

**Shannon Entropy of a distribution**:
```
H(X) = -Σᵢ p(xᵢ) log₂ p(xᵢ)
```

**Joint Entropy**:
```
H(X,Y) = -Σᵢⱼ p(xᵢ,yⱼ) log₂ p(xᵢ,yⱼ)
```

**Conditional Entropy**:
```
H(X|Y) = H(X,Y) - H(Y)
       = -Σᵢⱼ p(xᵢ,yⱼ) log₂ p(xᵢ|yⱼ)
```

### 4.2 Mutual Information

**Definition**:
```
I(X;Y) = H(X) + H(Y) - H(X,Y)
       = H(X) - H(X|Y)
       = Σᵢⱼ p(xᵢ,yⱼ) log₂ [p(xᵢ,yⱼ) / (p(xᵢ)p(yⱼ))]
```

**Normalized Mutual Information**:
```
NMI(X,Y) = 2 I(X;Y) / (H(X) + H(Y))
```
Range: [0, 1]

### 4.3 Graph Mutual Information

For two graphs G₁, G₂ over same nodes:

**Edge-based MI**:
```
Treat edges as binary random variables.
X = {A₁[i,j] : i < j}  (flattened upper triangle)
Y = {A₂[i,j] : i < j}

I(G₁; G₂) = I(X; Y)
```

**Computation**:
```
Let:
    n₁₁ = |{(i,j) : A₁[i,j]=1 ∧ A₂[i,j]=1}|  (both have edge)
    n₁₀ = |{(i,j) : A₁[i,j]=1 ∧ A₂[i,j]=0}|  (only G₁)
    n₀₁ = |{(i,j) : A₁[i,j]=0 ∧ A₂[i,j]=1}|  (only G₂)
    n₀₀ = |{(i,j) : A₁[i,j]=0 ∧ A₂[i,j]=0}|  (neither)
    n = n₁₁ + n₁₀ + n₀₁ + n₀₀

I(G₁;G₂) = Σₐ∈{0,1} Σᵦ∈{0,1} (nₐᵦ/n) log₂[(nₐᵦ × n) / (nₐ• × n•ᵦ)]
```

### 4.4 Transfer Entropy (Causality)

**Definition**:
```
T(X→Y) = I(Y_{t+1}; X_t | Y_t)
       = H(Y_{t+1}|Y_t) - H(Y_{t+1}|Y_t,X_t)
```

"How much does knowing X reduce uncertainty about future Y, beyond what Y's past tells us?"

**For graphs**:
```
T(G₁→G₂) = I(G₂(t+1); G₁(t) | G₂(t))
```

"Does structure G₁ help predict changes in G₂?"

### 4.5 Specific Information Measures

| Measure | Definition | Interpretation |
|---------|------------|----------------|
| Behavioral Coherence | I(G_import; G_cochange) | Do imports predict co-change? |
| Conway Alignment | I(G_import; G_author) | Do imports align with teams? |
| Semantic Alignment | I(G_import; G_semantic) | Do imports align with concepts? |
| Structural Predictability | I(G(t); ΔG(t+1)) | Does structure predict change? |
| Causal Structure | T(G_import→G_cochange) | Does structure drive behavior? |
| Causal Behavior | T(G_cochange→G_import) | Does behavior drive structure? |

---

## Part 5: Complete Signal Catalog

### 5.1 Syntax Signals (Layer 0)

| Signal | Scope | Type | Definition | Source |
|--------|-------|------|------------|--------|
| `lines` | FILE | int | Line count | Parsing |
| `functions` | FILE | int | Function definition count | Parsing |
| `classes` | FILE | int | Class/struct definition count | Parsing |
| `imports` | FILE | int | Import statement count | Parsing |
| `complexity` | FILE | int | Cyclomatic complexity (Σ over functions) | Parsing |
| `max_nesting` | FILE | int | Maximum nesting depth | Parsing |
| `max_function_lines` | FILE | int | Lines in largest function | Parsing |
| `stub_count` | FILE | int | Functions with trivial body | Parsing |
| `stub_ratio` | FILE | float | stub_count / functions | Derived |
| `impl_gini` | FILE | float | Gini(function_sizes) | Derived |

### 5.2 Temporal Primitive Signals (Layer 1)

| Signal | Scope | Type | Definition | Source |
|--------|-------|------|------------|--------|
| `birth_ts` | FILE | int | First commit timestamp | Git |
| `death_ts` | FILE | int | Removal timestamp (∞ if alive) | Git |
| `age_days` | FILE | int | (now - birth_ts) / 86400 | Derived |
| `total_commits` | FILE | int | Commits touching file | Git |
| `total_authors` | FILE | int | Distinct authors | Git |
| `total_additions` | FILE | int | Σ lines added | Git |
| `total_deletions` | FILE | int | Σ lines deleted | Git |

### 5.3 Windowed Temporal Signals (Layer 2)

Window w defaults to 4 weeks.

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| `commits_w` | FILE | int | Commits in window |
| `authors_w` | FILE | int | Distinct authors in window |
| `churn_w` | FILE | int | additions + deletions in window |
| `fix_commits_w` | FILE | int | Fix-related commits in window |
| `refactor_commits_w` | FILE | int | Refactor-related commits in window |

### 5.4 Derived Temporal Signals (Layer 2)

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| `churn_mean` | FILE | float | μ_windows(churn) |
| `churn_std` | FILE | float | σ_windows(churn) |
| `churn_cv` | FILE | float | churn_std / max(churn_mean, 1) |
| `churn_trend` | FILE | float | β_windows(churn) [slope] |
| `author_entropy` | FILE | float | H(author distribution) |
| `bus_factor` | FILE | float | 2^(author_entropy) |
| `fix_ratio` | FILE | float | fix_commits / total_commits |
| `refactor_ratio` | FILE | float | refactor_commits / total_commits |
| `change_entropy` | FILE | float | H(churn distribution over windows) |

**Trajectory Classification**:
```
trajectory = 
    DORMANT     if total_commits ≤ 1 or churn_cv = 0
    STABILIZING if churn_trend < -θ and churn_cv < 0.5
    SPIKING     if churn_trend > θ and churn_cv > 0.5
    CHURNING    if churn_cv > 0.5
    STABLE      otherwise
```

### 5.5 Graph Signals - Per Node (Layer 3)

For each relationship type r ∈ {IMPORT, COCHANGE, AUTHOR, SEMANTIC, CLONE, COMBINED}:

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| `in_degree[r]` | FILE | int | \|{u : (u,v) ∈ E_r}\| |
| `out_degree[r]` | FILE | int | \|{u : (v,u) ∈ E_r}\| |
| `degree[r]` | FILE | int | in_degree + out_degree |
| `pagerank[r]` | FILE | float | PageRank centrality |
| `betweenness[r]` | FILE | float | Betweenness centrality |
| `clustering[r]` | FILE | float | Local clustering coefficient |
| `depth[r]` | FILE | int | BFS distance from entry points |
| `blast_radius[r]` | FILE | int | \|transitive_closure(v)\| |
| `community[r]` | FILE | int | Community ID |
| `is_orphan[r]` | FILE | bool | in_degree[r] = 0 |
| `is_hub[r]` | FILE | bool | in_degree[r] > μ + 2σ |

### 5.6 Graph Signals - Global (Layer 3)

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| `node_count[r]` | CODEBASE | int | \|V\| |
| `edge_count[r]` | CODEBASE | int | \|E_r\| |
| `density[r]` | CODEBASE | float | \|E_r\| / (\|V\|×(\|V\|-1)) |
| `fiedler[r]` | CODEBASE | float | λ₂(L_r) |
| `spectral_gap[r]` | CODEBASE | float | λ₃ - λ₂ |
| `modularity[r]` | CODEBASE | float | Louvain modularity |
| `community_count[r]` | CODEBASE | int | Number of communities |
| `scc_count[r]` | CODEBASE | int | Non-trivial SCCs |
| `largest_scc_size[r]` | CODEBASE | int | Max SCC size |
| `centrality_gini[r]` | CODEBASE | float | Gini(pagerank) |
| `orphan_count[r]` | CODEBASE | int | Files with in_degree=0 |
| `orphan_ratio[r]` | CODEBASE | float | orphan_count / node_count |

### 5.7 Trajectory Signals - Per Node (Layer 4)

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| `pagerank_velocity` | FILE | float | D(pagerank[IMPORT]) |
| `pagerank_acceleration` | FILE | float | D²(pagerank[IMPORT]) |
| `degree_velocity` | FILE | float | D(degree[IMPORT]) |
| `community_changes` | FILE | int | Times community changed |
| `community_stability` | FILE | float | 1 - changes/observations |
| `centrality_trend` | FILE | float | β(pagerank over time) |

### 5.8 Trajectory Signals - Global (Layer 4)

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| `graph_velocity` | CODEBASE | float | mean(\|E(t) △ E(t-1)\| / \|E(t) ∪ E(t-1)\|) |
| `node_churn` | CODEBASE | float | mean(\|V(t) △ V(t-1)\| / \|V(t) ∪ V(t-1)\|) |
| `fiedler_trend` | CODEBASE | float | β(fiedler over time) |
| `modularity_trend` | CODEBASE | float | β(modularity over time) |
| `density_trend` | CODEBASE | float | β(density over time) |
| `topology_stability` | CODEBASE | float | 1 / (1 + graph_velocity) |

### 5.9 Cross-Layer Signals - Per Node (Layer 5)

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| `hidden_coupling_count` | FILE | int | \|N_cochange(v) \ N_import(v)\| |
| `dead_import_count` | FILE | int | \|N_import(v) \ N_cochange(v)\| |
| `conway_violation_count` | FILE | int | \|N_import(v) \ N_author(v)\| |
| `neighborhood_coherence` | FILE | float | \|N_imp ∩ N_coc\| / \|N_imp ∪ N_coc\| |
| `import_cochange_overlap` | FILE | float | Jaccard(N_import, N_cochange) |

### 5.10 Cross-Layer Signals - Per Pair (Layer 5)

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| `has_import` | PAIR | bool | (a,b) ∈ E_import or (b,a) ∈ E_import |
| `cochange_strength` | PAIR | float | W_cochange(a,b) |
| `author_overlap` | PAIR | float | W_author(a,b) |
| `semantic_similarity` | PAIR | float | W_semantic(a,b) |
| `hidden_coupling` | PAIR | float | cochange × (1 - has_import) |
| `dead_import` | PAIR | float | has_import × (1 - cochange) |
| `conway_violation` | PAIR | float | has_import × (1 - author_overlap) |
| `semantic_mismatch` | PAIR | float | has_import × (1 - semantic_similarity) |

### 5.11 Cross-Layer Signals - Global (Layer 5)

| Signal | Scope | Type | Definition |
|--------|-------|------|------------|
| `behavioral_coherence` | CODEBASE | float | I(G_import; G_cochange) |
| `conway_alignment` | CODEBASE | float | I(G_import; G_author) |
| `semantic_alignment` | CODEBASE | float | I(G_import; G_semantic) |
| `structural_predictability` | CODEBASE | float | I(G(t); ΔG(t+1)) |
| `hidden_coupling_ratio` | CODEBASE | float | \|E_hidden\| / \|E_cochange\| |
| `conway_violation_ratio` | CODEBASE | float | \|E_conway_viol\| / \|E_import\| |

### 5.12 Composite Signals - Per File (Layer 6)

| Signal | Scope | Type | Formula |
|--------|-------|------|---------|
| `risk_score` | FILE | float | See §6.1 |
| `wiring_quality` | FILE | float | See §6.2 |
| `health_score` | FILE | float | See §6.3 |
| `delta_h` | FILE | float | health - mean(neighbor_health) |

### 5.13 Composite Signals - Per Module (Layer 6)

| Signal | Scope | Type | Formula |
|--------|-------|------|---------|
| `cohesion` | MODULE | float | internal_edges / possible_internal |
| `coupling` | MODULE | float | external_edges / total_edges |
| `instability` | MODULE | float | Ce / (Ca + Ce) |
| `abstractness` | MODULE | float | abstract_count / file_count |
| `main_seq_distance` | MODULE | float | \|A + I - 1\| |
| `health_score` | MODULE | float | See §6.4 |

### 5.14 Composite Signals - Codebase (Layer 6)

| Signal | Scope | Type | Formula |
|--------|-------|------|---------|
| `wiring_score` | CODEBASE | float | See §6.5 |
| `architecture_health` | CODEBASE | float | See §6.6 |
| `team_risk` | CODEBASE | float | See §6.7 |
| `codebase_health` | CODEBASE | float | See §6.8 |

---

## Part 6: Composite Signal Formulas

### 6.1 File Risk Score

```
risk_score(v) = 
    w₁ × pctl(pagerank[IMPORT](v))           # structural importance
  + w₂ × pctl(|pagerank_velocity(v)|)        # changing importance [NEW]
  + w₃ × pctl(blast_radius[IMPORT](v))       # impact of change
  + w₄ × min(churn_cv(v) / 2, 1)             # change volatility
  + w₅ × max(0, 1 - bus_factor(v) / 5)       # knowledge concentration
  + w₆ × pctl(hidden_coupling_count(v))      # undeclared dependencies [NEW]
  + w₇ × (1 - community_stability(v))        # structural instability [NEW]

Default weights: w = [0.15, 0.10, 0.15, 0.15, 0.15, 0.15, 0.15]
Sum = 1.0
```

### 6.2 File Wiring Quality

```
wiring_quality(v) = 1 - (
    w₁ × is_orphan[IMPORT](v)
  + w₂ × stub_ratio(v)  
  + w₃ × phantom_import_ratio(v)
  + w₄ × (hidden_coupling_count(v) / max(degree(v), 1))  # [NEW]
)

Default weights: w = [0.25, 0.25, 0.25, 0.25]
```

### 6.3 File Health Score

```
health_score(v) = 1 - (
    w₁ × risk_score(v)
  + w₂ × (1 - wiring_quality(v))
  + w₃ × pctl(cognitive_load(v))
  + w₄ × is_orphan[IMPORT](v)
  + w₅ × (1 - neighborhood_coherence(v))    # [NEW]
)

Default weights: w = [0.25, 0.20, 0.20, 0.15, 0.20]
```

### 6.4 Module Health Score

```
health_score(m) = 
    w₁ × cohesion(m)
  + w₂ × (1 - coupling(m))
  + w₃ × (1 - main_seq_distance(m))     # skip if instability=None
  + w₄ × boundary_alignment(m)
  + w₅ × role_consistency(m)
  + w₆ × (1 - mean(stub_ratio(v) for v in m))

Default weights: w = [0.20, 0.15, 0.20, 0.15, 0.15, 0.15]
If instability=None: redistribute w₃ proportionally
```

### 6.5 Codebase Wiring Score

```
wiring_score = 1 - (
    w₁ × orphan_ratio[IMPORT]
  + w₂ × phantom_ratio
  + w₃ × glue_deficit
  + w₄ × mean(stub_ratio)
  + w₅ × clone_ratio
  + w₆ × hidden_coupling_ratio              # [NEW]
)

Default weights: w = [0.20, 0.20, 0.15, 0.15, 0.15, 0.15]
```

### 6.6 Architecture Health

```
architecture_health = 
    w₁ × (1 - violation_rate)
  + w₂ × mean(cohesion)
  + w₃ × (1 - mean(coupling))
  + w₄ × (1 - mean(main_seq_distance))
  + w₅ × mean(boundary_alignment)
  + w₆ × behavioral_coherence               # [NEW]
  + w₇ × (1 - |modularity_trend|)           # [NEW] penalize rapid change

Default weights: w = [0.15, 0.15, 0.15, 0.15, 0.10, 0.15, 0.15]
```

### 6.7 Team Risk

```
team_risk = 1 - (
    w₁ × min(min_critical_bus_factor, 3) / 3
  + w₂ × (1 - max(knowledge_gini))
  + w₃ × (1 - mean(coordination_cost))
  + w₄ × conway_alignment                   # [NEW]
)

Default weights: w = [0.30, 0.25, 0.25, 0.20]
```

### 6.8 Codebase Health (The One Number)

```
codebase_health = 
    w₁ × architecture_health
  + w₂ × wiring_score
  + w₃ × (global_bus_factor / team_size)
  + w₄ × modularity[IMPORT]
  + w₅ × behavioral_coherence               # [NEW]
  + w₆ × topology_stability                 # [NEW]

Default weights: w = [0.20, 0.20, 0.15, 0.15, 0.15, 0.15]
```

---

## Part 7: Aggregation Rules

### 7.1 File → Module Aggregation

| Signal Type | Aggregation | Formula |
|-------------|-------------|---------|
| Counts | sum | Σ s(v) |
| Rates/ratios | mean | (1/n) Σ s(v) |
| Worst case | max | max s(v) |
| Best case | min | min s(v) |
| Risk signals | weighted_mean | Σ importance(v) × s(v) / Σ importance(v) |
| Distributions | gini | Gini({s(v)}) |

### 7.2 Module → Codebase Aggregation

Same rules, applied to module signals.

### 7.3 Importance Weighting

```
importance(v) = pagerank[COMBINED](v)

weighted_mean(s) = Σ importance(v) × s(v) / Σ importance(v)
```

---

## Part 8: Normalization

### 8.1 Percentile Normalization

```
pctl(x) = |{v : s(v) ≤ x}| / |{v}|
```

### 8.2 Min-Max Normalization

```
norm(x) = (x - min) / (max - min)
```

### 8.3 Effective Percentile (with floor)

```
eff_pctl(signal, value) = 
    0.0 if value < FLOOR[signal]
    pctl(value) otherwise
    
FLOORS = {
    'pagerank': 0.001,
    'blast_radius': 2,
    'cognitive_load': 3,
}
```

### 8.4 Signal Polarity

| Polarity | Meaning | Normalization for "badness" |
|----------|---------|----------------------------|
| HIGH_BAD | High value = problem | pctl(x) |
| HIGH_GOOD | High value = healthy | 1 - pctl(x) |
| NEUTRAL | Structural, not quality | Use as-is |

---

## Summary

This framework provides:

1. **Mathematical foundation**: Tensor T[i,j,t,r] with formal operations
2. **Relationship algebra**: 6 primitive types + derived types + combination operations
3. **Temporal operators**: Derivatives, windows, stability measures
4. **Information theory**: MI, entropy, transfer entropy for coherence
5. **Complete signal catalog**: 100+ signals across 7 layers
6. **Composite formulas**: Risk, health, wiring with trajectory terms
7. **Aggregation rules**: File → Module → Codebase
8. **Normalization**: Percentile, floors, polarity

Shall we continue refining any specific part?


### [Thinking]

The user wants me to map the existing 22 finders, 6 analyzers, and 69 signals onto the framework I've defined. Let me think through this systematically.

First, let me recall what we have in the current codebase:

**Analyzers (from memory and code):**
1. StructuralAnalyzer - graph, PageRank, SCC, Louvain
2. TemporalAnalyzer - git history, churn, cochange
3. SemanticAnalyzer - concepts, roles
4. SpectralAnalyzer - Fiedler, spectral gap
5. ArchitectureAnalyzer - modules, Martin metrics
6. SignalFusionAnalyzer - combines everything

**Signals (62-69 based on memory):**
The memory says 62 signals (36 file + 15 module + 11 global), but user says 69. Let me enumerate them.

**Finders (22 from memory):**
From the v2 spec, there are finders for various patterns.

Let me now map everything onto the framework I defined. I need to:
1. List all 22 finders and show which signals/layers they read from
2. List all 6 analyzers and show what they produce
3. List all signals and categorize them in my framework

Let me be systematic about this.

## Signals Mapping

From my framework, I defined signals at each layer. Let me map the actual signals:

### Layer 0: Syntax (from parsing)
1. lines
2. function_count (functions)
3. class_count (classes/structs)
4. import_count
5. complexity
6. max_nesting
7. stub_ratio
8. impl_gini

### Layer 1-2: Temporal (from git)
9. total_changes
10. churn_cv
11. churn_slope


12. churn_trajectory
13. bus_factor
14. author_entropy
15. fix_ratio
16. refactor_ratio
17. change_entropy

### Layer 3: Graph Signals - Per File
For IMPORT graph:
18. pagerank
19. betweenness
20. in_degree
21. out_degree
22. blast_radius_size
23. depth
24. is_orphan
25. cycle_member
26. cycle_size
27. phantom_import_count
28. community
29. compression_ratio
30. cognitive_load

### Layer 3: Graph Signals - Global
31. modularity
32. cycle

_count
33. centrality_gini
34. fiedler_value
35. spectral_gap

### Layer 2-3: Semantic Signals
36. role
37. concept_count
38. concept_entropy
39. naming_drift
40. todo_density
41. docstring_coverage
42. semantic_coherence

### Layer 4: Trajectory Signals
(These might be new or implicit in current code)

### Layer 5: Cross-Layer Signals
These would be new in the framework

### Layer 6: Composite Signals - Per File
43. risk_score
44. wiring_quality
45. file_health_score
46. delta_h
47. raw_risk

### Layer 6: Composite Signals - Per Module
48. cohesion
49. coupling
50. instability
51. abstractness
52. main_seq_distance
53. boundary_alignment
54. layer_violation_count
55. role_consistency
56. velocity
57. coordination_cost
58. knowledge_gini
59. module_bus_factor
60. mean_cognitive_load
61. file_count
62. health_score (module)

### Layer 6: Composite Signals - Global
63. orphan_ratio
64. phantom_ratio
65. glue_deficit
66. clone_ratio
67. violation_rate
68. conway_alignment
69. team_size
70. wiring_score
71. architecture_health
72. team_risk
73. codebase_health

I'm getting more than 69 total. Need to verify against the actual registry in signals.md from the v2 spec, which lists file-level signals as items 1-36.

Checking the code directly, the module signals span #37-51 and global signals cover #52-62, giving 62 total. The user mentioned 69, so there might be additional signals beyond what's documented. Looking at the FileSignals class in signals/models.py, I can identify: lines, function_count, class_count, max_nesting, impl_gini, stub_ratio, import_count, role, concept_count, concept_entropy, naming_drift, todo_density, docstring_coverage, pagerank, betweenness, in_degree, out_degree, blast_radius_size, depth, is_orphan, cycle_member, phantom_import_count, and broken.

Continuing through the file signals: _call_count serves as a placeholder, followed by community, compression_ratio, semantic_coherence, cognitive_load, total_changes, churn_trajectory, churn_slope, churn_cv, bus_factor, author_entropy, fix_ratio, refactor_ratio, change_entropy, raw_risk, risk_score, wiring_quality, file_health_score, and delta_h. The ModuleSignals class then defines cohesion, coupling, instability, abstractness, main_seq_distance, boundary_alignment, layer_violation_count, role_consistency, velocity, coordination_cost, knowledge_gini, and module_bus_.

Completing the module-level metrics with mean_cognitive_load, file_count, and health_score. GlobalSignals encompasses the remaining dimensions: modularity, fiedler_value, spectral_gap, cycle_count, centrality_gini, orphan_ratio, phantom_ratio, glue_deficit, clone_ratio, violation_rate, conway_alignment, team_size, wiring_score, architecture_health, team_risk, and codebase_health. This brings the total to approximately 72 distinct signals across the system.

Rather than enumerate every possible metric, I'll focus on what's actually implemented and documented. The structural analysis identifies specific patterns like GOD_FILE for detecting oversized modules.

The finders capture distinct anti-patterns: structural issues (HIGH_RISK_HUB with high centrality and churn, ORPHAN_CODE with no incoming dependencies, PHANTOM_DEPENDENCY for unresolved imports, CIRCULAR_DEPENDENCY for files in strongly connected components, COPY_PASTE_CLONE for duplicated code), temporal concerns (UNSTABLE_FILE tracking high churn volatility, BUS_FACTOR_RISK for knowledge concentration, CHRONIC_PROBLEM for recurring issues), semantic problems (HOLLOW_CODE with excessive stubs, UNFOCUSED_FILE with scattered concepts, NAMING_INCONSISTENCY across the codebase), and architectural violations like ZONE_OF_PAIN (high instability and abstractness distance), LAYER_VIOLATION (cross-layer imports), and BOUNDARY_MISMATCH (module structure misaligned with communities). Cross-dimensional patterns include HIDDEN_COUPLING (cochange without explicit imports), CONWAY_VIOLATION (imports crossing team boundaries), WEAK_LINK (high delta_h), and ACCIDENTAL_COUPLING (concept overlap without dependencies). Social dimensions capture KNOWLEDGE_SILO (uneven knowledge distribution) and COORDINATION_BOTTLENECK (high coordination costs), while CHRONIC_PROBLEM tracks persistence across snapshots.

Looking at the actual implementation, the v1 baseline includes HighRiskHub, HiddenCoupling, GodFile, UnstableFile, BoundaryMismatch, and DeadDependency. The v2 specification expands this significantly with three waves of finders. Wave 1 covers structural issues: GOD_FILE, ORPHAN_CODE, PHANTOM_DEPENDENCY, CIRCULAR_DEPENDENCY, COPY_PASTE_CLONE, and FLAT_ARCHITECTURE. Wave 2 addresses architectural concerns including ZONE_OF_PAIN, ZONE_OF_USELESSNESS, and LAYER_VIOLATION among others.

The cross-dimensional wave introduces HIGH_RISK_HUB, HIDDEN_COUPLING, CONWAY_VIOLATION, WEAK_LINK, ACCIDENTAL_COUPLING, and KNOWLEDGE_SILO. Temporal and social dimensions add UNSTABLE_FILE, BUS_FACTOR_RISK, HOLLOW_CODE, and CHRONIC_PROBLEM. These 22 finders map to four core analyzers: StructuralAnalyzer, TemporalAnalyzer, SemanticAnalyzer, and Spectral.

I need to add ArchitectureAnalyzer and SignalFusionAnalyzer to complete the framework, then present everything systematically.


## ASSISTANT

Let me systematically map all components to the framework.

---

# Complete Component Mapping

## Part 1: The 6 Analyzers

### Analyzer 1: StructuralAnalyzer

**Framework Position**: Layer 0 → Layer 2 → Layer 3

**Inputs**:
- Layer 0: `FileSyntax` (imports, content)

**Outputs**:
| Signal | Layer | Relationship Type | Formula |
|--------|-------|-------------------|---------|
| `pagerank` | L3-Node | IMPORT | PageRank(G_import) |
| `betweenness` | L3-Node | IMPORT | Betweenness(G_import) |
| `in_degree` | L3-Node | IMPORT | \|{u: (u,v) ∈ E}\| |
| `out_degree` | L3-Node | IMPORT | \|{u: (v,u) ∈ E}\| |
| `blast_radius_size` | L3-Node | IMPORT | \|transitive_closure(v)\| |
| `depth` | L3-Node | IMPORT | BFS from entry points |
| `is_orphan` | L3-Node | IMPORT | in_degree = 0 |
| `cycle_member` | L3-Node | IMPORT | v ∈ any SCC |
| `cycle_size` | L3-Node | IMPORT | \|SCC containing v\| |
| `phantom_import_count` | L3-Node | IMPORT | unresolved imports |
| `community` | L3-Node | IMPORT | Louvain cluster ID |
| `compression_ratio` | L3-Node | - | C(content)/len(content) |
| `cognitive_load` | L3-Node | - | f(lines, complexity, nesting, gini) |
| `modularity` | L3-Global | IMPORT | Louvain Q score |
| `cycle_count` | L3-Global | IMPORT | \|{SCC: \|SCC\|>1}\| |
| `centrality_gini` | L3-Global | IMPORT | Gini(pagerank) |

**Also Produces**:
- `G_import(now)` - the import graph at current time
- `clone_pairs` - NCD clone detection results
- `CLONED_FROM` relations

**Framework Assessment**: 
- ✅ Correctly produces Layer 3 graph signals for IMPORT relationship
- ❌ Missing: Should also store edge lifecycle (edge_birth/edge_death) for trajectory
- ❌ Missing: Should produce G_import, not just signals derived from it

---

### Analyzer 2: TemporalAnalyzer

**Framework Position**: Layer 0 → Layer 1 → Layer 2

**Inputs**:
- Git repository (commits, diffs)

**Outputs**:
| Signal | Layer | Type | Formula |
|--------|-------|------|---------|
| `total_changes` | L2-Temporal | int | Σ commits touching file |
| `churn_cv` | L2-Temporal | float | σ(churn)/μ(churn) |
| `churn_slope` | L2-Temporal | float | β(churn over windows) |
| `churn_trajectory` | L2-Temporal | enum | Classification from cv+slope |
| `bus_factor` | L2-Temporal | float | 2^(author_entropy) |
| `author_entropy` | L2-Temporal | float | H(author distribution) |
| `fix_ratio` | L2-Temporal | float | fix_commits/total_commits |
| `refactor_ratio` | L2-Temporal | float | refactor_commits/total_commits |
| `change_entropy` | L2-Temporal | float | H(churn distribution) |

**Also Produces**:
- `G_cochange` - co-change graph with lift weights
- `G_author` - author overlap graph (via author_distances)
- `COCHANGES_WITH` relations
- `git_history` - raw commit data

**Framework Assessment**:
- ✅ Correctly produces Layer 1-2 temporal signals
- ✅ Produces G_cochange relationship graph
- ✅ Produces G_author relationship graph
- ❌ Missing: Should store to Layer 1 temporal index (event log)
- ❌ Missing: Import edge changes from diffs (for trajectory)

---

### Analyzer 3: SemanticAnalyzer

**Framework Position**: Layer 0 → Layer 2 (Semantic)

**Inputs**:
- Layer 0: `FileSyntax` (content, identifiers)

**Outputs**:
| Signal | Layer | Type | Formula |
|--------|-------|------|---------|
| `role` | L2-Semantic | enum | First-match classification |
| `concept_count` | L2-Semantic | int | \|extracted concepts\| |
| `concept_entropy` | L2-Semantic | float | H(concept weights) |
| `naming_drift` | L2-Semantic | float | Inconsistency score |
| `todo_density` | L2-Semantic | float | TODO count / lines |
| `docstring_coverage` | L2-Semantic | float | Documented / total |
| `semantic_coherence` | L2-Semantic | float | 1/(1 + concept_entropy) |

**Also Produces**:
- `G_semantic` - concept similarity graph (via SIMILAR_TO relations)
- `concepts` per file - for cross-layer analysis

**Framework Assessment**:
- ✅ Correctly produces semantic signals
- ✅ Produces G_semantic relationship graph
- ⚠️ `semantic_coherence` is derived from entropy, not from comparing to neighbors
- ❌ Missing: Should track concept evolution over time

---

### Analyzer 4: SpectralAnalyzer

**Framework Position**: Layer 2 → Layer 3

**Inputs**:
- `G_import` from StructuralAnalyzer

**Outputs**:
| Signal | Layer | Relationship Type | Formula |
|--------|-------|-------------------|---------|
| `fiedler_value` | L3-Global | IMPORT | λ₂(Laplacian) |
| `spectral_gap` | L3-Global | IMPORT | λ₃ - λ₂ |

**Framework Assessment**:
- ✅ Correctly produces spectral signals
- ❌ Missing: Should compute on G_cochange too (spectral[COCHANGE])
- ❌ Missing: Should compute on G_combined
- ❌ Missing: Spectral trajectory (fiedler over time)

---

### Analyzer 5: ArchitectureAnalyzer

**Framework Position**: Layer 2 + Layer 3 → Layer 3 (Module)

**Inputs**:
- `G_import` from StructuralAnalyzer
- `roles` from SemanticAnalyzer

**Outputs**:
| Signal | Layer | Scope | Formula |
|--------|-------|-------|---------|
| `cohesion` | L3-Module | MODULE | internal_edges / possible |
| `coupling` | L3-Module | MODULE | external_edges / total |
| `instability` | L3-Module | MODULE | Ce / (Ca + Ce) |
| `abstractness` | L3-Module | MODULE | abstract_files / total |
| `main_seq_distance` | L3-Module | MODULE | \|A + I - 1\| |
| `boundary_alignment` | L3-Module | MODULE | dominant_community / files |
| `layer_violation_count` | L3-Module | MODULE | cross-layer imports |
| `role_consistency` | L3-Module | MODULE | dominant_role / files |

**Also Produces**:
- Module membership mapping
- Layer assignments
- `DEPENDS_ON` relations between modules

**Framework Assessment**:
- ✅ Correctly produces module-level signals
- ❌ Missing: Module signals for G_cochange (behavioral modules)
- ❌ Missing: Module trajectory signals

---

### Analyzer 6: SignalFusionAnalyzer

**Framework Position**: All Layers → Layer 4 + Layer 5 + Layer 6

**Inputs**:
- All signals from Analyzers 1-5
- All relationship graphs

**Outputs**:

**Layer 4 Trajectory (Currently Missing/Implicit)**:
| Signal | Should Compute | Currently |
|--------|----------------|-----------|
| `pagerank_velocity` | d(pagerank)/dt | ❌ Not computed |
| `community_stability` | 1 - changes/obs | ❌ Not computed |
| `fiedler_trend` | d(fiedler)/dt | ❌ Not computed |
| `graph_velocity` | edge churn rate | ❌ Not computed |

**Layer 5 Cross-Layer (Partially Present)**:
| Signal | Should Compute | Currently |
|--------|----------------|-----------|
| `hidden_coupling_count` | \|N_coc \ N_imp\| | ⚠️ Via pattern, not signal |
| `behavioral_coherence` | I(G_imp; G_coc) | ❌ Not computed |
| `conway_alignment` | 1 - mean(author_dist) | ✅ Computed |

**Layer 6 Composites (Present)**:
| Signal | Scope | Status |
|--------|-------|--------|
| `raw_risk` | FILE | ✅ |
| `risk_score` | FILE | ✅ |
| `wiring_quality` | FILE | ✅ |
| `file_health_score` | FILE | ✅ |
| `delta_h` | FILE | ✅ |
| `velocity` | MODULE | ✅ |
| `coordination_cost` | MODULE | ✅ |
| `knowledge_gini` | MODULE | ✅ |
| `module_bus_factor` | MODULE | ✅ |
| `health_score` | MODULE | ✅ |
| `wiring_score` | CODEBASE | ✅ |
| `architecture_health` | CODEBASE | ✅ |
| `team_risk` | CODEBASE | ✅ |
| `codebase_health` | CODEBASE | ✅ |

**Framework Assessment**:
- ✅ Correctly produces Layer 6 composites
- ⚠️ Layer 5 cross-layer signals are partial
- ❌ Missing: Layer 4 trajectory signals entirely
- ❌ Missing: Information-theoretic measures (MI, coherence)

---

## Part 2: The 69 Signals

Let me categorize all signals by the framework layers:

### Layer 0: Syntax Signals (8 signals)

| # | Signal | Scope | Type | Definition | Producer |
|---|--------|-------|------|------------|----------|
| 1 | `lines` | FILE | int | Line count | Scanning |
| 2 | `function_count` | FILE | int | Function definitions | Scanning |
| 3 | `class_count` | FILE | int | Class/struct definitions | Scanning |
| 4 | `import_count` | FILE | int | Import statements | Scanning |
| 5 | `max_nesting` | FILE | int | Max nesting depth | Scanning |
| 6 | `complexity` | FILE | int | Cyclomatic complexity | Scanning |
| 7 | `stub_ratio` | FILE | float | stub_count / functions | Scanning |
| 8 | `impl_gini` | FILE | float | Gini(function_sizes) | Scanning |

**Framework Mapping**: ✅ All correctly in Layer 0

---

### Layer 2: Temporal Signals (9 signals)

| # | Signal | Scope | Type | Definition | Producer |
|---|--------|-------|------|------------|----------|
| 9 | `total_changes` | FILE | int | Commits touching file | Temporal |
| 10 | `churn_cv` | FILE | float | σ(churn)/μ(churn) | Temporal |
| 11 | `churn_slope` | FILE | float | Linear trend of churn | Temporal |
| 12 | `churn_trajectory` | FILE | enum | DORMANT/STABLE/CHURNING/... | Temporal |
| 13 | `bus_factor` | FILE | float | 2^(author_entropy) | Temporal |
| 14 | `author_entropy` | FILE | float | H(author distribution) | Temporal |
| 15 | `fix_ratio` | FILE | float | fix_commits / total | Temporal |
| 16 | `refactor_ratio` | FILE | float | refactor_commits / total | Temporal |
| 17 | `change_entropy` | FILE | float | H(churn over windows) | Temporal |

**Framework Mapping**: ✅ All correctly in Layer 2 (windowed temporal)

---

### Layer 2: Semantic Signals (7 signals)

| # | Signal | Scope | Type | Definition | Producer |
|---|--------|-------|------|------------|----------|
| 18 | `role` | FILE | enum | ENTRY/MODEL/SERVICE/... | Semantic |
| 19 | `concept_count` | FILE | int | Extracted concepts | Semantic |
| 20 | `concept_entropy` | FILE | float | H(concept weights) | Semantic |
| 21 | `naming_drift` | FILE | float | Naming inconsistency | Semantic |
| 22 | `todo_density` | FILE | float | TODOs / lines | Semantic |
| 23 | `docstring_coverage` | FILE | float | Documented / total | Semantic |
| 24 | `semantic_coherence` | FILE | float | 1/(1 + concept_entropy) | Fusion |

**Framework Mapping**: ✅ All correctly in Layer 2 (semantic)

---

### Layer 3: Graph Signals - Per Node (14 signals)

| # | Signal | Scope | Rel Type | Definition | Producer |
|---|--------|-------|----------|------------|----------|
| 25 | `pagerank` | FILE | IMPORT | PageRank centrality | Structural |
| 26 | `betweenness` | FILE | IMPORT | Betweenness centrality | Structural |
| 27 | `in_degree` | FILE | IMPORT | Incoming edges | Structural |
| 28 | `out_degree` | FILE | IMPORT | Outgoing edges | Structural |
| 29 | `blast_radius_size` | FILE | IMPORT | Transitive closure size | Structural |
| 30 | `depth` | FILE | IMPORT | BFS from entry points | Structural |
| 31 | `is_orphan` | FILE | IMPORT | in_degree = 0 | Structural |
| 32 | `cycle_member` | FILE | IMPORT | In SCC | Structural |
| 33 | `cycle_size` | FILE | IMPORT | SCC size | Structural |
| 34 | `phantom_import_count` | FILE | IMPORT | Unresolved imports | Structural |
| 35 | `community` | FILE | IMPORT | Louvain cluster ID | Structural |
| 36 | `compression_ratio` | FILE | - | Kolmogorov proxy | Fusion |
| 37 | `cognitive_load` | FILE | - | Comprehension difficulty | Fusion |
| 38 | `broken_call_count` | FILE | CALL | Unresolved calls | (Deferred) |

**Framework Mapping**: 
- ✅ Signals 25-35 correctly in Layer 3 for IMPORT relationship
- ⚠️ Signal 38 is placeholder (CALL edges not implemented)
- ❌ Missing: These signals for COCHANGE, AUTHOR relationships

**Gap Analysis**:
```
SHOULD HAVE (per framework):
- pagerank[COCHANGE]     ❌ Not computed
- pagerank[AUTHOR]       ❌ Not computed  
- pagerank[COMBINED]     ❌ Not computed
- community[COCHANGE]    ❌ Not computed (behavioral communities)
- depth[COCHANGE]        ❌ Not computed
```

---

### Layer 3: Graph Signals - Global (5 signals)

| # | Signal | Scope | Rel Type | Definition | Producer |
|---|--------|-------|----------|------------|----------|
| 39 | `modularity` | CODEBASE | IMPORT | Louvain Q | Structural |
| 40 | `cycle_count` | CODEBASE | IMPORT | Non-trivial SCCs | Structural |
| 41 | `centrality_gini` | CODEBASE | IMPORT | Gini(pagerank) | Structural |
| 42 | `fiedler_value` | CODEBASE | IMPORT | λ₂(Laplacian) | Spectral |
| 43 | `spectral_gap` | CODEBASE | IMPORT | λ₃ - λ₂ | Spectral |

**Framework Mapping**: ✅ All correctly in Layer 3 Global for IMPORT

**Gap Analysis**:
```
SHOULD HAVE (per framework):
- modularity[COCHANGE]   ❌ Not computed
- fiedler[COCHANGE]      ❌ Not computed
- fiedler[COMBINED]      ❌ Not computed
```

---

### Layer 4: Trajectory Signals (0 signals currently)

| # | Signal | Scope | Should Exist | Currently |
|---|--------|-------|--------------|-----------|
| - | `pagerank_velocity` | FILE | d(pagerank)/dt | ❌ |
| - | `pagerank_acceleration` | FILE | d²(pagerank)/dt² | ❌ |
| - | `community_stability` | FILE | 1 - changes/observations | ❌ |
| - | `centrality_trend` | FILE | β(pagerank over time) | ❌ |
| - | `graph_velocity` | CODEBASE | edge Jaccard over time | ❌ |
| - | `fiedler_trend` | CODEBASE | d(fiedler)/dt | ❌ |
| - | `modularity_trend` | CODEBASE | d(modularity)/dt | ❌ |
| - | `topology_stability` | CODEBASE | 1/(1 + graph_velocity) | ❌ |

**Framework Mapping**: ❌ **Entire Layer 4 is missing**

---

### Layer 5: Cross-Layer Signals (4 signals, partially implemented)

| # | Signal | Scope | Definition | Currently |
|---|--------|-------|------------|-----------|
| 44 | `conway_alignment` | CODEBASE | 1 - mean(author_distance) | ✅ |
| - | `behavioral_coherence` | CODEBASE | I(G_import; G_cochange) | ❌ |
| - | `hidden_coupling_count` | FILE | \|N_coc \ N_imp\| | ❌ (via pattern only) |
| - | `neighborhood_coherence` | FILE | Jaccard(N_imp, N_coc) | ❌ |

**Framework Mapping**: ⚠️ Layer 5 is minimal

---

### Layer 6: Composite Signals - Per File (5 signals)

| # | Signal | Scope | Formula | Producer |
|---|--------|-------|---------|----------|
| 45 | `raw_risk` | FILE | Pre-percentile risk | Fusion |
| 46 | `risk_score` | FILE | Percentile-based composite | Fusion |
| 47 | `wiring_quality` | FILE | 1 - (orphan + stub + phantom) | Fusion |
| 48 | `file_health_score` | FILE | Composite health | Fusion |
| 49 | `delta_h` | FILE | health - mean(neighbor_health) | Fusion |

**Framework Mapping**: ✅ All correctly in Layer 6

**Gap Analysis**:
```
Current risk_score formula:
  0.25 × pctl(pagerank)
+ 0.20 × pctl(blast_radius)
+ 0.20 × pctl(cognitive_load)
+ 0.20 × instability_factor
+ 0.15 × bus_factor_term

SHOULD INCLUDE (per framework):
+ w × pctl(|pagerank_velocity|)      ❌ Missing (trajectory)
+ w × pctl(hidden_coupling_count)    ❌ Missing (cross-layer)
+ w × (1 - community_stability)      ❌ Missing (trajectory)
```

---

### Layer 6: Composite Signals - Per Module (15 signals)

| # | Signal | Scope | Formula | Producer |
|---|--------|-------|---------|----------|
| 50 | `cohesion` | MODULE | internal_edges / possible | Architecture |
| 51 | `coupling` | MODULE | external_edges / total | Architecture |
| 52 | `instability` | MODULE | Ce / (Ca + Ce) | Architecture |
| 53 | `abstractness` | MODULE | abstract_files / total | Architecture |
| 54 | `main_seq_distance` | MODULE | \|A + I - 1\| | Architecture |
| 55 | `boundary_alignment` | MODULE | dominant_community / files | Architecture |
| 56 | `layer_violation_count` | MODULE | Cross-layer imports | Architecture |
| 57 | `role_consistency` | MODULE | dominant_role / files | Architecture |
| 58 | `velocity` | MODULE | commits/week | Fusion |
| 59 | `coordination_cost` | MODULE | cross-module commits / total | Fusion |
| 60 | `knowledge_gini` | MODULE | Gini(author commits) | Fusion |
| 61 | `module_bus_factor` | MODULE | min(bus_factor of critical files) | Fusion |
| 62 | `mean_cognitive_load` | MODULE | mean(cognitive_load) | Fusion |
| 63 | `file_count` | MODULE | \|files in module\| | Architecture |
| 64 | `health_score` | MODULE | Composite | Fusion |

**Framework Mapping**: ✅ All correctly in Layer 6

---

### Layer 6: Composite Signals - Global (11 signals)

| # | Signal | Scope | Formula | Producer |
|---|--------|-------|---------|----------|
| 65 | `orphan_ratio` | CODEBASE | orphan_count / total | Fusion |
| 66 | `phantom_ratio` | CODEBASE | files with phantoms / total | Fusion |
| 67 | `glue_deficit` | CODEBASE | 1 - glue_files / expected | Fusion |
| 68 | `clone_ratio` | CODEBASE | files in clones / total | Fusion |
| 69 | `violation_rate` | CODEBASE | violations / cross-module edges | Architecture |
| 70 | `team_size` | CODEBASE | Distinct authors | Fusion |
| 71 | `wiring_score` | CODEBASE | Composite | Fusion |
| 72 | `architecture_health` | CODEBASE | Composite | Fusion |
| 73 | `team_risk` | CODEBASE | Composite | Fusion |
| 74 | `codebase_health` | CODEBASE | The one number | Fusion |

**Framework Mapping**: ✅ All correctly in Layer 6

**Gap Analysis**:
```
Current codebase_health formula:
  0.30 × architecture_health
+ 0.30 × wiring_score
+ 0.20 × (global_bus_factor / team_size)
+ 0.20 × modularity

SHOULD INCLUDE (per framework):
+ w × behavioral_coherence           ❌ Missing (cross-layer)
+ w × topology_stability             ❌ Missing (trajectory)
```

---

### Signal Count Summary

| Layer | Expected | Current | Gap |
|-------|----------|---------|-----|
| L0: Syntax | 8 | 8 | 0 |
| L2: Temporal | 9 | 9 | 0 |
| L2: Semantic | 7 | 7 | 0 |
| L3: Graph-Node | 14 × R | 14 | **-28** (only IMPORT) |
| L3: Graph-Global | 5 × R | 5 | **-10** (only IMPORT) |
| L4: Trajectory | 8+ | 0 | **-8** |
| L5: Cross-Layer | 6+ | 1 | **-5** |
| L6: File | 5 | 5 | 0 |
| L6: Module | 15 | 15 | 0 |
| L6: Global | 11 | 11 | 0 |
| **Total** | **~100** | **~69** | **~31** |

---

## Part 3: The 22 Finders

Let me map each finder to the framework, showing which layers/signals it reads.

### Structural Finders (6)

#### 1. GOD_FILE
```
Scope: FILE
Layer: L0 + L3
Signals Read:
  - lines (L0)
  - function_count (L0)
  - cognitive_load (L3)
  - in_degree[IMPORT] (L3)
  
Condition: 
  lines > 500 AND (cognitive_load > pctl_90 OR in_degree > pctl_90)
  
Framework Assessment: ✅ Correct layer usage
```

#### 2. ORPHAN_CODE
```
Scope: FILE
Layer: L3 + L2-Semantic
Signals Read:
  - is_orphan[IMPORT] (L3)
  - role (L2-Semantic)
  
Condition:
  is_orphan = true AND role NOT IN (ENTRY_POINT, TEST, CONFIG)
  
Framework Assessment: ✅ Correct
Enhancement: Should also check is_orphan[COCHANGE] - behaviorally orphan
```

#### 3. PHANTOM_DEPENDENCY
```
Scope: FILE
Layer: L3
Signals Read:
  - phantom_import_count (L3)
  
Condition:
  phantom_import_count > 0
  
Framework Assessment: ✅ Correct
```

#### 4. CIRCULAR_DEPENDENCY
```
Scope: FILE (or PAIR)
Layer: L3
Signals Read:
  - cycle_member (L3)
  - cycle_size (L3)
  
Condition:
  cycle_member = true
  
Framework Assessment: ✅ Correct
```

#### 5. COPY_PASTE_CLONE
```
Scope: PAIR
Layer: L2 (Clone graph)
Signals Read:
  - CLONED_FROM relation
  - NCD weight
  
Condition:
  NCD(a, b) < 0.3
  
Framework Assessment: ✅ Correct
```

#### 6. FLAT_ARCHITECTURE
```
Scope: CODEBASE
Layer: L3-Global
Signals Read:
  - modularity[IMPORT] (L3)
  - community_count (L3)
  - centrality_gini (L3)
  
Condition:
  modularity < 0.3 AND centrality_gini < 0.3
  
Framework Assessment: ✅ Correct
Enhancement: Should check modularity[COCHANGE] too
```

---

### Architecture Finders (6)

#### 7. ZONE_OF_PAIN
```
Scope: MODULE
Layer: L6-Module
Signals Read:
  - instability (L6)
  - abstractness (L6)
  - main_seq_distance (L6)
  
Condition:
  instability IS NOT NULL AND main_seq_distance > 0.5
  AND (instability > 0.7 AND abstractness < 0.3)  # Painful zone
  
Framework Assessment: ✅ Correct
```

#### 8. ZONE_OF_USELESSNESS
```
Scope: MODULE
Layer: L6-Module
Signals Read:
  - instability (L6)
  - abstractness (L6)
  
Condition:
  instability < 0.3 AND abstractness > 0.7
  
Framework Assessment: ✅ Correct
```

#### 9. LAYER_VIOLATION
```
Scope: PAIR (modules)
Layer: L6-Module
Signals Read:
  - layer assignments
  - DEPENDS_ON relation
  
Condition:
  module_a.layer < module_b.layer AND imports(a, b)
  
Framework Assessment: ✅ Correct
```

#### 10. BOUNDARY_MISMATCH
```
Scope: MODULE
Layer: L6-Module
Signals Read:
  - boundary_alignment (L6)
  
Condition:
  boundary_alignment < 0.7
  
Framework Assessment: ✅ Correct
Enhancement: Should also check behavioral boundary alignment
```

#### 11. UNSTABLE_INTERFACE
```
Scope: MODULE
Layer: L6-Module + L2-Temporal
Signals Read:
  - instability (L6)
  - velocity (L6)
  - abstractness (L6)
  
Condition:
  instability > 0.7 AND velocity > pctl_75 AND abstractness > 0.5
  
Framework Assessment: ✅ Correct
```

#### 12. RIGID_CORE
```
Scope: MODULE
Layer: L6-Module
Signals Read:
  - instability (L6)
  - coupling (L6)
  - file_count (L6)
  
Condition:
  instability < 0.2 AND coupling > 0.5 AND file_count > 10
  
Framework Assessment: ✅ Correct
```

---

### Cross-Dimensional Finders (6)

#### 13. HIGH_RISK_HUB
```
Scope: FILE
Layer: L3 + L2 + L6
Signals Read:
  - pagerank[IMPORT] (L3)
  - churn_cv (L2)
  - bus_factor (L2)
  - risk_score (L6)
  
Condition:
  pagerank > pctl_90 AND (churn_cv > 1.0 OR bus_factor < 2)
  
Framework Assessment: ✅ Correct
Enhancement: Should include pagerank_velocity (L4)
```

#### 14. HIDDEN_COUPLING
```
Scope: PAIR
Layer: L5 (Cross-Layer)
Signals Read:
  - COCHANGES_WITH relation (G_cochange)
  - IMPORTS relation (G_import)
  - cochange lift
  
Condition:
  cochange_lift(a,b) > 2.0 AND NOT has_import(a,b) AND NOT has_import(b,a)
  
Formula (framework):
  hidden_coupling(a,b) = cochange(a,b) × (1 - import(a,b)) × (1 - import(b,a))
  
Framework Assessment: ✅ Correct - This IS a Layer 5 pattern
Gap: Should compute hidden_coupling_count as FILE signal
```

#### 15. CONWAY_VIOLATION
```
Scope: PAIR
Layer: L5 (Cross-Layer)
Signals Read:
  - IMPORTS relation (G_import)
  - author_overlap (G_author)
  
Condition:
  has_import(a,b) AND author_overlap(a,b) < 0.2
  
Formula (framework):
  conway_violation(a,b) = import(a,b) × (1 - author_overlap(a,b))
  
Framework Assessment: ✅ Correct - This IS a Layer 5 pattern
```

#### 16. WEAK_LINK
```
Scope: FILE
Layer: L6
Signals Read:
  - delta_h (L6)
  - file_health_score (L6)
  
Condition:
  delta_h > 0.4  # Much worse than neighbors
  
Framework Assessment: ✅ Correct
```

#### 17. ACCIDENTAL_COUPLING
```
Scope: PAIR
Layer: L5 (Cross-Layer)
Signals Read:
  - concepts (L2-Semantic)
  - IMPORTS relation (G_import)
  
Condition:
  concept_overlap(a,b) > 0.5 AND NOT has_import(a,b)
  
Formula (framework):
  accidental_coupling = semantic(a,b) × (1 - import(a,b))
  
Framework Assessment: ✅ Correct - Layer 5 (semantic × import)
Note: Different from HIDDEN_COUPLING (behavioral × import)
```

#### 18. KNOWLEDGE_SILO
```
Scope: MODULE
Layer: L6-Module
Signals Read:
  - knowledge_gini (L6)
  - module_bus_factor (L6)
  
Condition:
  knowledge_gini > 0.7 OR module_bus_factor < 1.5
  
Framework Assessment: ✅ Correct
```

---

### Temporal/Quality Finders (4)

#### 19. UNSTABLE_FILE
```
Scope: FILE
Layer: L2-Temporal
Signals Read:
  - churn_cv (L2)
  - churn_trajectory (L2)
  - total_changes (L2)
  
Condition:
  churn_trajectory IN (CHURNING, SPIKING) AND total_changes > median
  
Framework Assessment: ✅ Correct
Enhancement: Should include trajectory signals (L4)
```

#### 20. BUS_FACTOR_RISK
```
Scope: FILE
Layer: L2-Temporal + L3
Signals Read:
  - bus_factor (L2)
  - pagerank[IMPORT] (L3)
  
Condition:
  bus_factor < 1.5 AND pagerank > pctl_75
  
Framework Assessment: ✅ Correct
```

#### 21. HOLLOW_CODE
```
Scope: FILE
Layer: L0
Signals Read:
  - stub_ratio (L0)
  - function_count (L0)
  
Condition:
  stub_ratio > 0.5 AND function_count > 3
  
Framework Assessment: ✅ Correct
```

#### 22. CHRONIC_PROBLEM
```
Scope: FILE
Layer: L7 (Meta - persistence)
Signals Read:
  - finding history from snapshots
  - persistence_count
  
Condition:
  finding exists in >= 3 consecutive snapshots
  
Framework Assessment: ✅ Correct - Uses temporal persistence
```

---

### Finder Summary by Layer

| Layer | Finders Using It |
|-------|------------------|
| L0: Syntax | GOD_FILE, HOLLOW_CODE |
| L2: Temporal | HIGH_RISK_HUB, UNSTABLE_FILE, BUS_FACTOR_RISK |
| L2: Semantic | ORPHAN_CODE, ACCIDENTAL_COUPLING |
| L3: Graph-Node | GOD_FILE, ORPHAN_CODE, PHANTOM_DEPENDENCY, CIRCULAR_DEPENDENCY, HIGH_RISK_HUB, BUS_FACTOR_RISK |
| L3: Graph-Global | FLAT_ARCHITECTURE |
| L4: Trajectory | **None currently** ❌ |
| L5: Cross-Layer | HIDDEN_COUPLING, CONWAY_VIOLATION, ACCIDENTAL_COUPLING |
| L6: File | HIGH_RISK_HUB, WEAK_LINK |
| L6: Module | All architecture finders |
| L6: Global | FLAT_ARCHITECTURE |

---

## Part 4: Gap Analysis Summary

### Missing from Framework Implementation

#### Layer 4: Trajectory (Entirely Missing)
```
Signals needed:
- pagerank_velocity
- pagerank_acceleration
- community_stability
- centrality_trend
- graph_velocity
- fiedler_trend
- modularity_trend
- topology_stability

Finders that should use:
- HIGH_RISK_HUB (rising importance)
- UNSTABLE_FILE (trajectory context)
- ARCHITECTURAL_DECAY (new finder)
```

#### Layer 5: Cross-Layer (Mostly Missing)
```
Signals needed:
- behavioral_coherence = I(G_import; G_cochange)
- neighborhood_coherence per file
- hidden_coupling_count per file
- structural_predictability

Finders that should use:
- HIDDEN_COUPLING (already uses relation-level)
- Should aggregate to file-level signal
```

#### Multi-Relationship Graph Signals (Missing)
```
Currently only IMPORT relationship has graph signals.
Should also have for:
- COCHANGE: pagerank[COCHANGE], community[COCHANGE], etc.
- AUTHOR: pagerank[AUTHOR]
- COMBINED: pagerank[COMBINED]
```

#### New Finders Enabled by Framework
```
With trajectory signals:
- RISING_RISK: pagerank_velocity > 0 AND community_stability < 0.5
- ARCHITECTURAL_DECAY: modularity_trend < -0.05
- STABILIZING_CODE: churn_trend < 0 AND community_stability > 0.8

With multi-layer graphs:
- BEHAVIORAL_ORPHAN: is_orphan[COCHANGE] = true
- STRUCTURAL_BEHAVIORAL_MISMATCH: community[IMPORT] ≠ community[COCHANGE]
```

---

## Part 5: Recommended Additions

### New Signals (Priority Order)

| Priority | Signal | Layer | Enables |
|----------|--------|-------|---------|
| P0 | `behavioral_coherence` | L5 | Global health metric |
| P0 | `graph_velocity` | L4 | Stability tracking |
| P1 | `pagerank_velocity` | L4 | Rising risk detection |
| P1 | `community_stability` | L4 | Architectural stability |
| P1 | `hidden_coupling_count` | L5 | Per-file coupling metric |
| P2 | `pagerank[COCHANGE]` | L3 | Behavioral importance |
| P2 | `community[COCHANGE]` | L3 | Behavioral modules |
| P3 | `fiedler_trend` | L4 | Modularity trajectory |
| P3 | `neighborhood_coherence` | L5 | Per-file coherence |

### New Finders (Priority Order)

| Priority | Finder | Signals Needed |
|----------|--------|----------------|
| P1 | RISING_RISK | pagerank_velocity, community_stability |
| P1 | ARCHITECTURAL_DECAY | modularity_trend, fiedler_trend |
| P2 | BEHAVIORAL_ORPHAN | is_orphan[COCHANGE] |
| P2 | LOW_COHERENCE | behavioral_coherence (global) |
| P3 | STRUCTURAL_BEHAVIORAL_MISMATCH | community[IMPORT], community[COCHANGE] |

---

Does this complete mapping help clarify the gaps and opportunities?


### [Thinking]

The user wants me to create a comprehensive document that defines the complete pipeline with:
1. Step by step stages
2. DB storage at each stage
3. Runtime considerations
4. Other concerns

This should be a specification document, not an implementation plan. Let me create a thorough, well-structured document that covers:

1. Pipeline Overview
2. Each stage in detail:
   - Inputs
   - Outputs
   - DB schema
   - Runtime characteristics
   - Dependencies
3. Storage model
4. Runtime analysis
5. Failure modes
6. Incremental computation
7. Consistency guarantees

Let me write this as a proper specification document.


## ASSISTANT

# Shannon Insight Pipeline Specification

## Document Information

| Field | Value |
|-------|-------|
| Version | 2.0 |
| Status | Draft Specification |
| Last Updated | 2026-02-18 |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Pipeline Overview](#2-pipeline-overview)
3. [Stage Specifications](#3-stage-specifications)
4. [Database Schema](#4-database-schema)
5. [Runtime Analysis](#5-runtime-analysis)
6. [Consistency Model](#6-consistency-model)
7. [Failure Modes & Recovery](#7-failure-modes--recovery)
8. [Incremental Computation](#8-incremental-computation)
9. [Observability](#9-observability)
10. [Constraints & Limitations](#10-constraints--limitations)

---

## 1. Executive Summary

### 1.1 Purpose

This document specifies a staged pipeline for codebase analysis that:
- Extracts structural and temporal data from source code and git history
- Builds multi-layer relationship graphs
- Computes signals across 7 layers of abstraction
- Detects patterns indicating code health issues
- Persists all intermediate results for auditability and incremental updates

### 1.2 Design Principles

| Principle | Description |
|-----------|-------------|
| **Persistence-First** | Every stage writes to DB before the next stage reads |
| **Incremental** | Only recompute what changed since last run |
| **Auditable** | Any signal value traceable to source data |
| **Recoverable** | Failed runs resume from last successful stage |
| **Deterministic** | Same inputs produce same outputs |

### 1.3 Pipeline Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SHANNON INSIGHT PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌───────┐ │
│  │ Stage 0 │───▶│ Stage 1 │───▶│ Stage 2 │───▶│ Stage 3 │───▶│ St. 4 │ │
│  │ Extract │    │  Index  │    │  Graph  │    │ Signals │    │Pattern│ │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    └───┬───┘ │
│       │              │              │              │              │     │
│       ▼              ▼              ▼              ▼              ▼     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌───────┐ │
│  │ facts   │    │ temporal│    │  graph  │    │ signals │    │finding│ │
│  │   .db   │    │   .db   │    │   .db   │    │   .db   │    │  .db  │ │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └───────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline Overview

### 2.1 Stage Dependency Graph

```
                    ┌──────────────────┐
                    │   Source Code    │
                    │   + Git Repo     │
                    └────────┬─────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 0: Raw Extraction     │
              │  ─────────────────────────   │
              │  • Parse files → FileSyntax  │
              │  • Extract git → Commits     │
              │  • Extract diffs → Changes   │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 1: Temporal Index     │
              │  ─────────────────────────   │
              │  • Build event log           │
              │  • Compute node lifecycle    │
              │  • Compute edge lifecycle    │
              │  • Build time windows        │
              └──────────────┬───────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  STAGE 2a   │   │  STAGE 2b   │   │  STAGE 2c   │
    │  ─────────  │   │  ─────────  │   │  ─────────  │
    │  G_import   │   │  G_cochange │   │  G_semantic │
    │  G_clone    │   │  G_author   │   │             │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 2d: Graph Fusion      │
              │  ─────────────────────────   │
              │  • Build G_combined          │
              │  • Sample historical graphs  │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 3a: Graph Algorithms  │
              │  ─────────────────────────   │
              │  • PageRank per layer        │
              │  • Louvain per layer         │
              │  • Spectral per layer        │
              │  • SCC, depth, blast radius  │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 3b: Trajectory        │
              │  ─────────────────────────   │
              │  • Compute derivatives       │
              │  • Stability measures        │
              │  • Trend analysis            │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 3c: Cross-Layer       │
              │  ─────────────────────────   │
              │  • Mutual information        │
              │  • Hidden coupling           │
              │  • Coherence measures        │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 3d: Composites        │
              │  ─────────────────────────   │
              │  • Normalization             │
              │  • Risk scores               │
              │  • Health scores             │
              │  • Aggregation               │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 4: Pattern Detection  │
              │  ─────────────────────────   │
              │  • Evaluate 22 finders       │
              │  • Score and rank            │
              │  • Link to evidence          │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 5: Snapshot Seal      │
              │  ─────────────────────────   │
              │  • Link all artifacts        │
              │  • Compute diff from prior   │
              │  • Archive snapshot          │
              └──────────────────────────────┘
```

### 2.2 Stage Summary Table

| Stage | Name | Inputs | Outputs | DB Tables | Parallelizable |
|-------|------|--------|---------|-----------|----------------|
| 0 | Raw Extraction | Files, Git | FileSyntax, Commits, Diffs | `file_facts`, `git_commits`, `git_file_changes` | Yes (per file) |
| 1 | Temporal Index | Stage 0 | Events, Lifecycles, Windows | `events`, `node_lifecycle`, `edge_lifecycle`, `time_windows` | Partial |
| 2a | Import Graph | Stage 0, 1 | G_import(t) | `graph_edges[IMPORT]`, `graph_snapshots` | Yes |
| 2b | Temporal Graphs | Stage 1 | G_cochange, G_author | `graph_edges[COCHANGE]`, `graph_edges[AUTHOR]` | Yes |
| 2c | Semantic Graph | Stage 0 | G_semantic, G_clone | `graph_edges[SEMANTIC]`, `graph_edges[CLONE]` | Yes |
| 2d | Graph Fusion | Stage 2a-c | G_combined, Historical samples | `graph_edges[COMBINED]`, `graph_history` | No |
| 3a | Graph Algorithms | Stage 2 | Node signals, Global signals | `node_signals`, `global_signals` | Yes (per graph) |
| 3b | Trajectory | Stage 3a + history | Derivatives, Stability | `trajectory_signals` | No |
| 3c | Cross-Layer | Stage 2, 3a | MI, Coherence, Hidden coupling | `cross_layer_signals` | Partial |
| 3d | Composites | Stage 3a-c | Risk, Health, Aggregates | `composite_signals` | Yes (per entity) |
| 4 | Patterns | Stage 3 | Findings | `findings`, `finding_evidence` | Yes (per pattern) |
| 5 | Snapshot | All | Sealed snapshot | `snapshots`, `snapshot_artifacts` | No |

---

## 3. Stage Specifications

### Stage 0: Raw Extraction

#### 3.0.1 Purpose
Extract raw facts from source files and git repository. This is the only stage that touches the filesystem and git directly.

#### 3.0.2 Inputs

| Input | Source | Description |
|-------|--------|-------------|
| Source files | Filesystem | All files matching language extensions |
| Git repository | `.git/` | Full git history |
| Config | `shannon-insight.toml` | Exclusion patterns, limits |

#### 3.0.3 Processing Steps

```
0.1  Discover files
     ├── Walk directory tree
     ├── Apply exclusion patterns (95 default patterns)
     ├── Filter by extension (8 supported languages)
     └── Respect max_files limit

0.2  Parse each file (parallelizable)
     ├── Detect language from extension
     ├── Parse with tree-sitter (if available) or regex fallback
     ├── Extract: functions, classes, imports, complexity, nesting
     ├── Compute content_hash = SHA256(content)
     └── Store FileSyntax record

0.3  Extract git commits
     ├── git log --all --format="%H|%at|%ae|%s"
     ├── Parse into Commit records
     ├── Limit to max_commits (default 5000)
     └── Store GitCommit records

0.4  Extract file changes
     ├── git log --all --name-status --numstat
     ├── For each commit: files added, modified, deleted, renamed
     ├── For modified files: additions, deletions counts
     └── Store GitFileChange records

0.5  Extract import changes from diffs (optional, for edge lifecycle)
     ├── git log --all -p --diff-filter=M -- "*.py" "*.ts" ...
     ├── Parse diffs for import statement changes
     ├── Detect: import added, import removed
     └── Store ImportChange records
```

#### 3.0.4 Outputs

| Output | Table | Description |
|--------|-------|-------------|
| FileSyntax | `file_facts` | Parsed syntax per file |
| GitCommit | `git_commits` | Commit metadata |
| GitFileChange | `git_file_changes` | Per-file changes per commit |
| ImportChange | `import_changes` | Import add/remove events |

#### 3.0.5 Database Schema

```sql
-- File facts from parsing
CREATE TABLE file_facts (
    id              INTEGER PRIMARY KEY,
    session_id      TEXT NOT NULL,
    path            TEXT NOT NULL,
    content_hash    TEXT NOT NULL,
    language        TEXT NOT NULL,
    lines           INTEGER NOT NULL,
    functions       INTEGER NOT NULL,
    classes         INTEGER NOT NULL,
    imports         INTEGER NOT NULL,
    complexity      INTEGER NOT NULL,
    max_nesting     INTEGER NOT NULL,
    stub_count      INTEGER NOT NULL,
    created_at      INTEGER NOT NULL,
    
    UNIQUE(session_id, path)
);

CREATE INDEX idx_file_facts_session ON file_facts(session_id);
CREATE INDEX idx_file_facts_hash ON file_facts(content_hash);

-- Git commits
CREATE TABLE git_commits (
    hash            TEXT PRIMARY KEY,
    timestamp       INTEGER NOT NULL,
    author_email    TEXT NOT NULL,
    subject         TEXT NOT NULL,
    session_id      TEXT NOT NULL
);

CREATE INDEX idx_git_commits_ts ON git_commits(timestamp);
CREATE INDEX idx_git_commits_author ON git_commits(author_email);

-- File changes per commit
CREATE TABLE git_file_changes (
    id              INTEGER PRIMARY KEY,
    commit_hash     TEXT NOT NULL REFERENCES git_commits(hash),
    file_path       TEXT NOT NULL,
    change_type     TEXT NOT NULL,  -- 'A', 'M', 'D', 'R'
    old_path        TEXT,           -- for renames
    additions       INTEGER,
    deletions       INTEGER,
    
    UNIQUE(commit_hash, file_path)
);

CREATE INDEX idx_git_changes_file ON git_file_changes(file_path);
CREATE INDEX idx_git_changes_commit ON git_file_changes(commit_hash);

-- Import changes from diffs (optional)
CREATE TABLE import_changes (
    id              INTEGER PRIMARY KEY,
    commit_hash     TEXT NOT NULL REFERENCES git_commits(hash),
    file_path       TEXT NOT NULL,
    change_type     TEXT NOT NULL,  -- 'add', 'remove'
    import_target   TEXT NOT NULL,  -- resolved import path
    timestamp       INTEGER NOT NULL
);
```

#### 3.0.6 Runtime Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Time complexity | O(files × avg_file_size + commits) | Dominated by parsing |
| Space complexity | O(files + commits + changes) | Linear storage |
| Parallelism | High | Files parsed independently |
| I/O pattern | Read-heavy | Filesystem + git |
| Typical runtime | 1-5 min for 1000 files, 5000 commits | Depends on git history depth |

#### 3.0.7 Incremental Strategy

```
On subsequent runs:
1. Load existing file_facts for session
2. For each file:
   a. Compute content_hash
   b. If hash matches existing record → skip parsing
   c. If hash differs or new file → parse and upsert
3. For git:
   a. Find last processed commit hash
   b. Extract only commits since then
   c. Append new commits and file changes
```

#### 3.0.8 Failure Modes

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Parse error | Exception during parsing | Log warning, skip file, continue |
| Git not available | git command fails | Abort temporal analysis, continue structural |
| File unreadable | IOError | Log warning, skip file, continue |
| Encoding error | UnicodeDecodeError | Try latin-1 fallback, then skip |

---

### Stage 1: Temporal Index

#### 3.1.1 Purpose
Build a temporal index that enables efficient reconstruction of any graph at any historical time point.

#### 3.1.2 Inputs

| Input | Source | Description |
|-------|--------|-------------|
| `file_facts` | Stage 0 | Current file state |
| `git_commits` | Stage 0 | Commit history |
| `git_file_changes` | Stage 0 | File changes per commit |
| `import_changes` | Stage 0 | Import add/remove events |

#### 3.1.3 Processing Steps

```
1.1  Build event log (append-only)
     ├── For each file change:
     │   ├── change_type='A' → emit NODE_ADD event
     │   ├── change_type='D' → emit NODE_REMOVE event
     │   └── change_type='R' → emit NODE_RENAME event
     ├── For each import change:
     │   ├── change_type='add' → emit EDGE_ADD(IMPORT) event
     │   └── change_type='remove' → emit EDGE_REMOVE(IMPORT) event
     └── Sort events by timestamp

1.2  Compute node lifecycle
     ├── For each unique file path:
     │   ├── birth_ts = min(timestamp where NODE_ADD)
     │   ├── death_ts = max(timestamp where NODE_REMOVE) or NULL
     │   └── canonical_path = resolve rename chains
     └── Handle renames: old_path → canonical_path mapping

1.3  Compute edge lifecycle (for IMPORT edges)
     ├── For each (source, target) pair:
     │   ├── birth_ts = timestamp of EDGE_ADD
     │   └── death_ts = timestamp of EDGE_REMOVE or NULL
     └── Store lifecycle records

1.4  Build time windows
     ├── Define window_size (default: 4 weeks = 28 days)
     ├── Partition commits into windows
     ├── For each window:
     │   ├── Compute cochange counts: {(a,b): count}
     │   ├── Compute author counts: {file: {author: count}}
     │   └── Compute churn counts: {file: changes}
     └── Store window aggregates
```

#### 3.1.4 Outputs

| Output | Table | Description |
|--------|-------|-------------|
| Events | `events` | Append-only event log |
| Node lifecycle | `node_lifecycle` | Birth/death per file |
| Edge lifecycle | `edge_lifecycle` | Birth/death per edge |
| Time windows | `time_windows` | Pre-aggregated window data |
| Window cochange | `window_cochange` | Co-change counts per window |
| Window authors | `window_authors` | Author counts per window |

#### 3.1.5 Database Schema

```sql
-- Append-only event log
CREATE TABLE events (
    id              INTEGER PRIMARY KEY,
    timestamp       INTEGER NOT NULL,
    commit_hash     TEXT NOT NULL,
    event_type      TEXT NOT NULL,  -- NODE_ADD, NODE_REMOVE, NODE_RENAME, EDGE_ADD, EDGE_REMOVE
    relation_type   TEXT,           -- NULL for node events, 'IMPORT' etc for edge events
    source_path     TEXT NOT NULL,
    target_path     TEXT,           -- for edges and renames
    author          TEXT NOT NULL,
    metadata        TEXT            -- JSON for additional data
);

CREATE INDEX idx_events_ts ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_source ON events(source_path);

-- Node lifecycle
CREATE TABLE node_lifecycle (
    path            TEXT PRIMARY KEY,
    canonical_path  TEXT NOT NULL,
    birth_ts        INTEGER NOT NULL,
    death_ts        INTEGER,        -- NULL if still alive
    birth_commit    TEXT NOT NULL,
    death_commit    TEXT
);

CREATE INDEX idx_node_lifecycle_birth ON node_lifecycle(birth_ts);
CREATE INDEX idx_node_lifecycle_death ON node_lifecycle(death_ts);

-- Edge lifecycle (per relationship type)
CREATE TABLE edge_lifecycle (
    id              INTEGER PRIMARY KEY,
    relation_type   TEXT NOT NULL,
    source_path     TEXT NOT NULL,
    target_path     TEXT NOT NULL,
    birth_ts        INTEGER NOT NULL,
    death_ts        INTEGER,        -- NULL if still exists
    birth_commit    TEXT NOT NULL,
    death_commit    TEXT,
    
    UNIQUE(relation_type, source_path, target_path, birth_ts)
);

CREATE INDEX idx_edge_lifecycle_rel ON edge_lifecycle(relation_type);
CREATE INDEX idx_edge_lifecycle_source ON edge_lifecycle(source_path);

-- Time windows
CREATE TABLE time_windows (
    id              INTEGER PRIMARY KEY,
    window_start    INTEGER NOT NULL,
    window_end      INTEGER NOT NULL,
    commit_count    INTEGER NOT NULL,
    file_count      INTEGER NOT NULL,
    author_count    INTEGER NOT NULL,
    
    UNIQUE(window_start)
);

-- Cochange counts per window
CREATE TABLE window_cochange (
    window_id       INTEGER NOT NULL REFERENCES time_windows(id),
    file_a          TEXT NOT NULL,
    file_b          TEXT NOT NULL,
    cochange_count  INTEGER NOT NULL,
    
    PRIMARY KEY(window_id, file_a, file_b)
);

-- Author counts per window
CREATE TABLE window_authors (
    window_id       INTEGER NOT NULL REFERENCES time_windows(id),
    file_path       TEXT NOT NULL,
    author          TEXT NOT NULL,
    commit_count    INTEGER NOT NULL,
    
    PRIMARY KEY(window_id, file_path, author)
);
```

#### 3.1.6 Key Operations

**Reconstruct graph at time t**:
```sql
-- Get nodes alive at time t
SELECT canonical_path 
FROM node_lifecycle 
WHERE birth_ts <= :t AND (death_ts IS NULL OR death_ts > :t);

-- Get edges alive at time t
SELECT source_path, target_path, relation_type
FROM edge_lifecycle
WHERE relation_type = :rel_type
  AND birth_ts <= :t 
  AND (death_ts IS NULL OR death_ts > :t);
```

**Compute cochange for window**:
```sql
SELECT file_a, file_b, SUM(cochange_count) as total
FROM window_cochange wc
JOIN time_windows tw ON wc.window_id = tw.id
WHERE tw.window_start >= :start AND tw.window_end <= :end
GROUP BY file_a, file_b;
```

#### 3.1.7 Runtime Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Time complexity | O(events + commits × files_per_commit) | Event building dominates |
| Space complexity | O(events + nodes + edges × history_depth) | Can be large for long histories |
| Parallelism | Limited | Event ordering must be preserved |
| Typical runtime | 30s - 2 min | Depends on history depth |

---

### Stage 2: Graph Construction

#### 3.2.1 Purpose
Build the multi-layer relationship graphs from indexed data.

#### Stage 2a: Import Graph

**Processing**:
```
2a.1  For current time (now):
      ├── Read file_facts.imports for each file
      ├── Resolve import targets to file paths
      ├── Create edges: source → target
      └── Store in graph_edges[IMPORT]

2a.2  For historical time points (sampled):
      ├── Use edge_lifecycle to reconstruct G_import(t)
      ├── Store snapshot in graph_history
      └── Sample at: t - 1mo, t - 3mo, t - 6mo, t - 12mo
```

#### Stage 2b: Temporal Graphs

**Processing**:
```
2b.1  Build G_cochange:
      ├── Read window_cochange for recent windows
      ├── Compute lift: lift(a,b) = P(a,b) / (P(a) × P(b))
      ├── Filter edges with lift > 1.0 (more than random)
      └── Store in graph_edges[COCHANGE]

2b.2  Build G_author:
      ├── Read window_authors for recent windows
      ├── Compute Jaccard: |A∩B| / |A∪B| where A,B = author sets
      ├── Filter edges with Jaccard > 0.1 (non-trivial overlap)
      └── Store in graph_edges[AUTHOR]
```

#### Stage 2c: Semantic Graph

**Processing**:
```
2c.1  Extract concepts per file:
      ├── Tokenize identifiers
      ├── Apply TF-IDF weighting
      ├── Extract top-k concepts per file
      └── Store in file_concepts

2c.2  Build G_semantic:
      ├── Compute cosine similarity between concept vectors
      ├── Filter edges with similarity > 0.3
      └── Store in graph_edges[SEMANTIC]

2c.3  Build G_clone:
      ├── Compute NCD for file pairs (with LSH for large codebases)
      ├── Filter edges with NCD < 0.3
      └── Store in graph_edges[CLONE]
```

#### Stage 2d: Graph Fusion

**Processing**:
```
2d.1  Build G_combined (weighted union):
      ├── Normalize edge weights per graph to [0,1]
      ├── Combine: w_combined = α×w_import + β×w_cochange + γ×w_author + δ×w_semantic
      ├── Default weights: α=0.4, β=0.3, γ=0.2, δ=0.1
      └── Store in graph_edges[COMBINED]

2d.2  Sample historical combined graphs:
      ├── For each historical time point t:
      │   ├── Reconstruct G_import(t)
      │   ├── Compute G_cochange(t) from window data up to t
      │   ├── Combine into G_combined(t)
      │   └── Store in graph_history
      └── Store graph_history records
```

#### 3.2.2 Database Schema

```sql
-- Graph edges (all relationship types)
CREATE TABLE graph_edges (
    id              INTEGER PRIMARY KEY,
    snapshot_id     TEXT NOT NULL,
    relation_type   TEXT NOT NULL,  -- IMPORT, COCHANGE, AUTHOR, SEMANTIC, CLONE, COMBINED
    source_path     TEXT NOT NULL,
    target_path     TEXT NOT NULL,
    weight          REAL NOT NULL DEFAULT 1.0,
    metadata        TEXT,           -- JSON with additional attributes
    
    UNIQUE(snapshot_id, relation_type, source_path, target_path)
);

CREATE INDEX idx_graph_edges_snapshot ON graph_edges(snapshot_id, relation_type);
CREATE INDEX idx_graph_edges_source ON graph_edges(source_path);
CREATE INDEX idx_graph_edges_target ON graph_edges(target_path);

-- Historical graph snapshots
CREATE TABLE graph_history (
    id              INTEGER PRIMARY KEY,
    snapshot_id     TEXT NOT NULL,
    relation_type   TEXT NOT NULL,
    timestamp       INTEGER NOT NULL,
    node_count      INTEGER NOT NULL,
    edge_count      INTEGER NOT NULL,
    
    UNIQUE(snapshot_id, relation_type, timestamp)
);

-- File concepts for semantic graph
CREATE TABLE file_concepts (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    concept         TEXT NOT NULL,
    weight          REAL NOT NULL,
    
    PRIMARY KEY(snapshot_id, file_path, concept)
);
```

#### 3.2.3 Runtime Characteristics

| Sub-stage | Time Complexity | Parallelism | Typical Runtime |
|-----------|-----------------|-------------|-----------------|
| 2a: Import | O(files × imports) | High | 5-10s |
| 2b: Cochange | O(windows × pairs) | Medium | 10-30s |
| 2c: Semantic | O(files² × concepts) or O(files × log files) with LSH | Medium | 20-60s |
| 2d: Fusion | O(edges) | High | 5-10s |
| **Total** | | | 40s - 2 min |

---

### Stage 3: Signal Computation

#### Stage 3a: Graph Algorithms

**Processing per relationship type r**:
```
3a.1  Centrality metrics:
      ├── PageRank(G_r) → pagerank[r] per node
      ├── Betweenness(G_r) → betweenness[r] per node
      └── Store in node_signals

3a.2  Community detection:
      ├── Louvain(G_r) → community[r] per node, modularity[r] global
      └── Store in node_signals, global_signals

3a.3  Structural metrics:
      ├── In/out degree per node
      ├── SCC detection → cycle_member, cycle_size per node
      ├── BFS from entry points → depth per node
      ├── Transitive closure → blast_radius per node
      └── Store in node_signals

3a.4  Spectral metrics:
      ├── Laplacian eigenvalues → fiedler[r], spectral_gap[r] global
      └── Store in global_signals

3a.5  Distribution metrics:
      ├── Gini(pagerank) → centrality_gini[r] global
      └── Store in global_signals
```

#### Stage 3b: Trajectory Signals

**Processing**:
```
3b.1  Load historical snapshots:
      ├── For each historical time t in graph_history:
      │   └── Load node_signals computed at t (or compute now)
      └── Build time series per node per signal

3b.2  Compute derivatives:
      ├── For each node, for each signal s:
      │   ├── velocity = (s(now) - s(t-1)) / Δt
      │   ├── acceleration = (velocity(now) - velocity(t-1)) / Δt
      │   └── trend = linear_regression_slope(s over all t)
      └── Store in trajectory_signals

3b.3  Compute stability metrics:
      ├── community_changes = count(community[t] ≠ community[t-1])
      ├── community_stability = 1 - community_changes / observations
      └── Store in trajectory_signals

3b.4  Compute global trajectory:
      ├── graph_velocity = mean(edge_jaccard(G(t), G(t-1)))
      ├── fiedler_trend = slope(fiedler over time)
      ├── modularity_trend = slope(modularity over time)
      └── Store in global_trajectory_signals
```

#### Stage 3c: Cross-Layer Signals

**Processing**:
```
3c.1  Compute mutual information:
      ├── behavioral_coherence = I(G_import; G_cochange)
      ├── conway_alignment = I(G_import; G_author)
      ├── semantic_alignment = I(G_import; G_semantic)
      └── Store in global_signals

3c.2  Compute per-node cross-layer:
      ├── For each node v:
      │   ├── N_import = neighbors in G_import
      │   ├── N_cochange = neighbors in G_cochange
      │   ├── hidden_coupling_count = |N_cochange \ N_import|
      │   ├── neighborhood_coherence = |N_import ∩ N_cochange| / |N_import ∪ N_cochange|
      │   └── Store in node_cross_signals
      └── 

3c.3  Compute per-pair cross-layer:
      ├── For pairs with any relationship:
      │   ├── hidden_coupling = cochange(a,b) × (1 - import(a,b))
      │   ├── conway_violation = import(a,b) × (1 - author(a,b))
      │   └── Store in pair_signals (sparse, only non-zero)
      └──
```

#### Stage 3d: Composite Signals

**Processing**:
```
3d.1  Percentile normalization:
      ├── For each normalizable signal:
      │   ├── Collect all values across files
      │   ├── Compute pctl(v) = rank(v) / count
      │   └── Store percentiles in node_signals
      └── Skip for ABSOLUTE tier (<15 files)

3d.2  File composites:
      ├── raw_risk = weighted_sum(pagerank, blast_radius, cognitive_load, churn_cv, bus_factor)
      ├── risk_score = weighted_sum(percentiles) + trajectory_terms + cross_layer_terms
      ├── wiring_quality = 1 - penalties(orphan, stub, phantom, hidden_coupling)
      ├── file_health_score = composite(risk, wiring, cognitive, coherence)
      └── Store in composite_signals

3d.3  Health Laplacian:
      ├── For each node v:
      │   ├── neighbors = import_neighbors ∪ imported_by
      │   ├── mean_neighbor_risk = mean(raw_risk(n) for n in neighbors)
      │   ├── delta_h = raw_risk(v) - mean_neighbor_risk
      │   └── Store delta_h in composite_signals
      └──

3d.4  Module composites:
      ├── Aggregate file signals per module
      ├── Compute Martin metrics (cohesion, coupling, instability, abstractness)
      ├── Compute health_score per module
      └── Store in module_signals

3d.5  Codebase composites:
      ├── wiring_score = 1 - penalties(orphan_ratio, phantom_ratio, glue_deficit, ...)
      ├── architecture_health = composite(violation_rate, cohesion, coupling, ...)
      ├── team_risk = composite(bus_factor, knowledge_gini, coordination_cost, conway)
      ├── codebase_health = composite(architecture, wiring, bus_factor, modularity, coherence, stability)
      └── Store in global_signals
```

#### 3.3.2 Database Schema

```sql
-- Node signals (per file, per relationship type where applicable)
CREATE TABLE node_signals (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    relation_type   TEXT,           -- NULL for non-graph signals
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,
    percentile      REAL,           -- NULL for non-normalizable
    
    PRIMARY KEY(snapshot_id, file_path, relation_type, signal_name)
);

CREATE INDEX idx_node_signals_snapshot ON node_signals(snapshot_id);
CREATE INDEX idx_node_signals_signal ON node_signals(signal_name);

-- Trajectory signals (per file)
CREATE TABLE trajectory_signals (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    signal_name     TEXT NOT NULL,  -- e.g., 'pagerank_velocity', 'community_stability'
    value           REAL NOT NULL,
    
    PRIMARY KEY(snapshot_id, file_path, signal_name)
);

-- Cross-layer signals (per file)
CREATE TABLE cross_layer_signals (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,
    
    PRIMARY KEY(snapshot_id, file_path, signal_name)
);

-- Pair signals (sparse, only significant pairs)
CREATE TABLE pair_signals (
    snapshot_id     TEXT NOT NULL,
    file_a          TEXT NOT NULL,
    file_b          TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,
    
    PRIMARY KEY(snapshot_id, file_a, file_b, signal_name)
);

-- Module signals
CREATE TABLE module_signals (
    snapshot_id     TEXT NOT NULL,
    module_path     TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,
    
    PRIMARY KEY(snapshot_id, module_path, signal_name)
);

-- Global signals
CREATE TABLE global_signals (
    snapshot_id     TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,
    
    PRIMARY KEY(snapshot_id, signal_name)
);

-- Composite signals (file-level, separated for clarity)
CREATE TABLE composite_signals (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    raw_risk        REAL NOT NULL,
    risk_score      REAL NOT NULL,
    wiring_quality  REAL NOT NULL,
    health_score    REAL NOT NULL,
    delta_h         REAL NOT NULL,
    
    PRIMARY KEY(snapshot_id, file_path)
);
```

#### 3.3.3 Runtime Characteristics

| Sub-stage | Time Complexity | Parallelism | Typical Runtime |
|-----------|-----------------|-------------|-----------------|
| 3a: Graph algorithms | O(V + E) per algorithm | Per graph | 10-30s |
| 3b: Trajectory | O(history_depth × V) | Limited | 5-15s |
| 3c: Cross-layer | O(V × avg_degree) + O(E) for MI | Medium | 10-20s |
| 3d: Composites | O(V) | High | 5-10s |
| **Total** | | | 30s - 1.5 min |

---

### Stage 4: Pattern Detection

#### 3.4.1 Purpose
Evaluate all 22 finders against computed signals to detect patterns.

#### 3.4.2 Processing

```
4.1  Load signal data:
      ├── Load node_signals, trajectory_signals, cross_layer_signals
      ├── Load module_signals, global_signals
      ├── Load pair_signals (for pair-scope patterns)
      └── Load graph_edges (for relation-based patterns)

4.2  For each finder (parallelizable per finder):
      ├── Determine scope: FILE, PAIR, MODULE, CODEBASE
      ├── Determine required signals
      ├── Evaluate condition for each entity in scope
      ├── For matches:
      │   ├── Compute severity (from formula)
      │   ├── Compute confidence
      │   ├── Collect evidence (signal values that triggered)
      │   └── Create Finding record
      └── Apply hotspot filter for FILE scope (unless structural-only)

4.3  Rank findings:
      ├── Sort by severity × confidence
      ├── Apply max_findings limit
      └── Store ranked findings

4.4  Link evidence:
      ├── For each finding:
      │   ├── Store signal values as evidence
      │   └── Store related entities (for PAIR scope)
      └── Store in finding_evidence
```

#### 3.4.3 Finder Execution Order

```
Wave 1: Structural (no cross-dependencies)
├── GOD_FILE
├── ORPHAN_CODE
├── PHANTOM_DEPENDENCY
├── CIRCULAR_DEPENDENCY
├── COPY_PASTE_CLONE
└── FLAT_ARCHITECTURE

Wave 2: Architecture (needs module signals)
├── ZONE_OF_PAIN
├── ZONE_OF_USELESSNESS
├── LAYER_VIOLATION
├── BOUNDARY_MISMATCH
├── UNSTABLE_INTERFACE
└── RIGID_CORE

Wave 3: Cross-dimensional (needs all signals)
├── HIGH_RISK_HUB
├── HIDDEN_COUPLING
├── CONWAY_VIOLATION
├── WEAK_LINK
├── ACCIDENTAL_COUPLING
└── KNOWLEDGE_SILO

Wave 4: Temporal/Quality
├── UNSTABLE_FILE
├── BUS_FACTOR_RISK
├── HOLLOW_CODE
└── CHRONIC_PROBLEM
```

#### 3.4.4 Database Schema

```sql
-- Findings
CREATE TABLE findings (
    id              TEXT PRIMARY KEY,
    snapshot_id     TEXT NOT NULL,
    pattern         TEXT NOT NULL,  -- e.g., 'HIDDEN_COUPLING'
    scope           TEXT NOT NULL,  -- FILE, PAIR, MODULE, CODEBASE
    target          TEXT NOT NULL,  -- file path, or "file_a|file_b" for pairs
    severity        REAL NOT NULL,
    confidence      REAL NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT,
    remediation     TEXT,
    rank            INTEGER,
    
    UNIQUE(snapshot_id, pattern, target)
);

CREATE INDEX idx_findings_snapshot ON findings(snapshot_id);
CREATE INDEX idx_findings_pattern ON findings(pattern);
CREATE INDEX idx_findings_severity ON findings(severity DESC);

-- Finding evidence
CREATE TABLE finding_evidence (
    finding_id      TEXT NOT NULL REFERENCES findings(id),
    signal_name     TEXT NOT NULL,
    signal_value    REAL NOT NULL,
    percentile      REAL,
    description     TEXT,
    
    PRIMARY KEY(finding_id, signal_name)
);

-- Finding lifecycle (for CHRONIC_PROBLEM detection)
CREATE TABLE finding_lifecycle (
    pattern         TEXT NOT NULL,
    target          TEXT NOT NULL,
    first_seen      TEXT NOT NULL,  -- snapshot_id
    last_seen       TEXT NOT NULL,  -- snapshot_id
    persistence_count INTEGER NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'active',
    
    PRIMARY KEY(pattern, target)
);
```

#### 3.4.5 Runtime Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Time complexity | O(finders × entities) | Typically 22 × files |
| Parallelism | High | Finders independent within waves |
| Typical runtime | 5-15s | |

---

### Stage 5: Snapshot Seal

#### 3.5.1 Purpose
Seal all artifacts under a single snapshot ID for atomic retrieval and historical comparison.

#### 3.5.2 Processing

```
5.1  Generate snapshot_id:
      └── snapshot_id = f"{commit_sha}_{timestamp}_{random_suffix}"

5.2  Link all artifacts:
      ├── All tables reference snapshot_id
      └── Create snapshot metadata record

5.3  Compute diff from prior snapshot:
      ├── Load prior snapshot signals
      ├── Compute signal deltas per file
      ├── Identify new/resolved findings
      └── Store in snapshot_diff

5.4  Archive (optional):
      ├── Export snapshot to Parquet files
      └── Compress and store
```

#### 3.5.3 Database Schema

```sql
-- Snapshot metadata
CREATE TABLE snapshots (
    id              TEXT PRIMARY KEY,
    commit_sha      TEXT NOT NULL,
    timestamp       INTEGER NOT NULL,
    root_path       TEXT NOT NULL,
    file_count      INTEGER NOT NULL,
    finding_count   INTEGER NOT NULL,
    codebase_health REAL,
    status          TEXT NOT NULL DEFAULT 'complete',
    created_at      INTEGER NOT NULL,
    config_hash     TEXT,
    tool_version    TEXT
);

CREATE INDEX idx_snapshots_commit ON snapshots(commit_sha);
CREATE INDEX idx_snapshots_ts ON snapshots(timestamp);

-- Snapshot artifact manifest
CREATE TABLE snapshot_artifacts (
    snapshot_id     TEXT NOT NULL REFERENCES snapshots(id),
    artifact_type   TEXT NOT NULL,  -- 'file_facts', 'graph_edges', 'findings', etc.
    record_count    INTEGER NOT NULL,
    checksum        TEXT,
    
    PRIMARY KEY(snapshot_id, artifact_type)
);

-- Snapshot diff (changes from prior)
CREATE TABLE snapshot_diff (
    snapshot_id     TEXT NOT NULL REFERENCES snapshots(id),
    prior_snapshot  TEXT REFERENCES snapshots(id),
    files_added     INTEGER NOT NULL,
    files_removed   INTEGER NOT NULL,
    files_changed   INTEGER NOT NULL,
    findings_new    INTEGER NOT NULL,
    findings_resolved INTEGER NOT NULL,
    health_delta    REAL,
    
    PRIMARY KEY(snapshot_id)
);
```

---

## 4. Database Schema Summary

### 4.1 Database Files

| Database | Tables | Purpose | Typical Size |
|----------|--------|---------|--------------|
| `facts.db` | `file_facts`, `git_commits`, `git_file_changes`, `import_changes` | Stage 0 outputs | 10-50 MB |
| `temporal.db` | `events`, `node_lifecycle`, `edge_lifecycle`, `time_windows`, `window_cochange`, `window_authors` | Stage 1 outputs | 20-100 MB |
| `graph.db` | `graph_edges`, `graph_history`, `file_concepts` | Stage 2 outputs | 10-50 MB |
| `signals.db` | `node_signals`, `trajectory_signals`, `cross_layer_signals`, `pair_signals`, `module_signals`, `global_signals`, `composite_signals` | Stage 3 outputs | 20-100 MB |
| `findings.db` | `findings`, `finding_evidence`, `finding_lifecycle` | Stage 4 outputs | 1-10 MB |
| `snapshots.db` | `snapshots`, `snapshot_artifacts`, `snapshot_diff` | Stage 5 outputs | 1-5 MB |

### 4.2 Total Storage Estimate

| Codebase Size | Files | History | Total DB Size |
|---------------|-------|---------|---------------|
| Small | <100 | <1000 commits | <50 MB |
| Medium | 100-1000 | 1000-5000 commits | 50-200 MB |
| Large | 1000-10000 | 5000+ commits | 200 MB - 1 GB |
| Monorepo | 10000+ | 10000+ commits | 1-10 GB |

---

## 5. Runtime Analysis

### 5.1 Overall Pipeline Timing

| Stage | Small (<100 files) | Medium (100-1000) | Large (1000-10000) |
|-------|-------------------|-------------------|-------------------|
| 0: Extraction | 5-10s | 30-60s | 2-5 min |
| 1: Temporal Index | 2-5s | 10-30s | 1-2 min |
| 2: Graph Construction | 5-10s | 30-60s | 2-5 min |
| 3: Signal Computation | 5-10s | 30-60s | 2-5 min |
| 4: Pattern Detection | 1-2s | 5-10s | 30-60s |
| 5: Snapshot Seal | 1-2s | 2-5s | 5-10s |
| **Total (cold)** | **20-40s** | **2-4 min** | **8-20 min** |
| **Total (incremental)** | **5-10s** | **20-60s** | **2-5 min** |

### 5.2 Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| File parsing | O(files × avg_lines) | O(files × syntax_size) |
| Git extraction | O(commits + changes) | O(commits + changes) |
| Event building | O(changes) | O(events) |
| Graph construction | O(files × avg_imports + pairs) | O(edges) |
| PageRank | O(iterations × edges) | O(nodes) |
| Louvain | O(passes × edges) | O(nodes + edges) |
| Spectral | O(nodes³) or O(nodes × eigenvalues) | O(nodes²) or O(nodes) |
| Trajectory | O(history_depth × nodes × signals) | O(history × nodes) |
| Cross-layer MI | O(edges₁ + edges₂) | O(1) |
| Composites | O(nodes) | O(nodes) |
| Pattern detection | O(patterns × entities) | O(findings) |

### 5.3 Memory Footprint

| Stage | Peak Memory | Notes |
|-------|-------------|-------|
| 0: Extraction | O(largest_file) | Files parsed one at a time |
| 1: Temporal Index | O(events) | Event log in memory during build |
| 2: Graph Construction | O(nodes + edges) | Graphs in memory |
| 3a: Graph Algorithms | O(nodes²) worst case | Spectral is memory-heavy |
| 3b-d: Other Signals | O(nodes × signals) | Signal vectors |
| 4: Pattern Detection | O(nodes × signals) | Loaded signals |
| **Peak Overall** | **O(nodes² + edges)** | During spectral computation |

### 5.4 Bottleneck Analysis

| Bottleneck | Impact | Mitigation |
|------------|--------|------------|
| Spectral computation | O(n³) for dense Laplacian | Use sparse solver, approximate for n>5000 |
| Clone detection (NCD) | O(n²) pairwise | LSH for n>1000, skip for n>5000 |
| Historical graph reconstruction | O(history × work) | Sample history, don't compute all points |
| Git extraction | I/O bound | Incremental extraction |
| Large file parsing | Memory for AST | Stream parsing, skip >10MB files |

---

## 6. Consistency Model

### 6.1 Invariants

| Invariant | Description | Enforcement |
|-----------|-------------|-------------|
| **Snapshot atomicity** | All artifacts for a snapshot are complete or none | Transaction per stage, rollback on failure |
| **Signal derivability** | Any signal value can be recomputed from inputs | Store all intermediate data |
| **Temporal monotonicity** | Events ordered by timestamp | Sort events, reject out-of-order |
| **Graph consistency** | Edge endpoints exist as nodes | Validate on insert |
| **Referential integrity** | Foreign keys valid | DB constraints |

### 6.2 Consistency Checks

```
After Stage 0:
  ✓ All file_facts have valid content_hash
  ✓ All git_file_changes reference valid commits
  ✓ No duplicate (session_id, path) in file_facts

After Stage 1:
  ✓ Every node in edge_lifecycle exists in node_lifecycle
  ✓ Events are sorted by timestamp
  ✓ No gaps in time_windows coverage

After Stage 2:
  ✓ All graph edge endpoints exist as nodes
  ✓ Edge weights are positive
  ✓ Historical snapshots have consistent node counts

After Stage 3:
  ✓ All percentiles in [0, 1]
  ✓ All composite scores in [0, 1]
  ✓ delta_h sums to ~0 across codebase (conservation)

After Stage 4:
  ✓ All findings reference valid targets
  ✓ All evidence signals exist in signal tables
  ✓ Severity and confidence in [0, 1]

After Stage 5:
  ✓ All artifact tables reference the snapshot_id
  ✓ Record counts match snapshot_artifacts
  ✓ Checksums validate
```

### 6.3 Idempotency

Each stage is idempotent: running it twice with same inputs produces same outputs.

```
Enforcement:
- Stage 0: UPSERT on (session_id, path) with content_hash check
- Stage 1: DELETE + INSERT for session (rebuild index)
- Stage 2-3: DELETE + INSERT for snapshot_id
- Stage 4: DELETE + INSERT for snapshot_id
- Stage 5: Snapshot ID includes randomness, always unique
```

---

## 7. Failure Modes & Recovery

### 7.1 Failure Scenarios

| Scenario | Detection | Impact | Recovery |
|----------|-----------|--------|----------|
| Parse error | Exception | Single file missing | Log, skip file, continue |
| Git unavailable | Command fails | No temporal data | Run structural-only mode |
| OOM during spectral | MemoryError | Stage 3a fails | Reduce to approximate method |
| DB write fails | SQLException | Stage incomplete | Rollback, retry |
| Timeout | Watchdog | Stage incomplete | Kill, rollback, retry with limits |
| Corrupt input | Validation fails | Stage fails | Report error, abort |

### 7.2 Recovery Procedures

**Partial stage failure**:
```
1. Identify failed stage from run_log
2. Check last successful checkpoint
3. Rollback incomplete data:
   DELETE FROM {table} WHERE snapshot_id = :failed_snapshot
4. Retry from failed stage
```

**Full recovery**:
```
1. Identify last complete snapshot
2. Delete all data for incomplete snapshots
3. Re-run pipeline from Stage 0 (or from Stage 1 if facts intact)
```

### 7.3 Checkpointing

```
Checkpoint after each stage:
1. Validate stage outputs
2. Write checkpoint record:
   INSERT INTO run_checkpoints (run_id, stage, status, timestamp)
3. Commit transaction

On startup:
1. Find last run
2. Find last successful checkpoint
3. Resume from next stage
```

---

## 8. Incremental Computation

### 8.1 Change Detection

| Data | Change Detection | Granularity |
|------|------------------|-------------|
| Files | content_hash comparison | Per-file |
| Git | HEAD commit comparison | Per-commit |
| Imports | diff of import statements | Per-file |
| Graphs | edge set difference | Per-graph |
| Signals | value comparison | Per-signal |

### 8.2 Incremental Update Strategy

**Stage 0 (Extraction)**:
```
For files:
  changed_files = {f : content_hash(f) ≠ stored_hash(f)}
  new_files = {f : f not in stored}
  deleted_files = {f : f in stored but not on disk}
  
  Parse only: changed_files ∪ new_files
  Mark deleted: deleted_files

For git:
  last_commit = get_last_processed_commit()
  new_commits = git log {last_commit}..HEAD
  
  Extract only: new_commits
```

**Stage 1 (Temporal Index)**:
```
Append new events to event log
Update node_lifecycle for affected nodes
Update edge_lifecycle for affected edges
Rebuild affected time_windows only
```

**Stage 2 (Graphs)**:
```
For G_import:
  Rebuild only for changed_files (local update)
  
For G_cochange, G_author:
  Update incrementally from new window data
  
For G_combined:
  Rebuild (fast, O(edges))
```

**Stage 3 (Signals)**:
```
For graph signals:
  Recompute PageRank, Louvain (global algorithms, must rerun)
  But: can warm-start from previous values
  
For trajectory:
  Append new data point, recompute derivatives
  
For composites:
  Recompute only for files with changed inputs
```

**Stage 4 (Patterns)**:
```
Re-evaluate all patterns (fast)
Compare to previous findings for lifecycle update
```

### 8.3 Incremental Runtime Savings

| Scenario | Full Run | Incremental |
|----------|----------|-------------|
| No changes | 2-5 min | <5s (detect no changes) |
| 1 file changed | 2-5 min | 10-30s |
| 10 files changed | 2-5 min | 30-60s |
| 100 files changed | 2-5 min | 1-2 min |
| Git-only changes | 2-5 min | 20-60s |

---

## 9. Observability

### 9.1 Logging

| Level | Content | Example |
|-------|---------|---------|
| INFO | Stage transitions, counts | "Stage 2 complete: 1500 edges in G_import" |
| DEBUG | Per-entity operations | "Computed pagerank for file.py: 0.0234" |
| WARNING | Recoverable issues | "Failed to parse malformed.py, skipping" |
| ERROR | Stage failures | "OOM during spectral computation" |

### 9.2 Metrics

```python
@dataclass
class PipelineMetrics:
    # Timing
    stage_durations: dict[str, float]      # seconds per stage
    total_duration: float
    
    # Throughput
    files_processed: int
    files_per_second: float
    commits_processed: int
    edges_computed: int
    signals_computed: int
    
    # Quality
    parse_failures: int
    validation_failures: int
    
    # Resources
    peak_memory_mb: float
    db_size_mb: float
```

### 9.3 Run Log

```sql
CREATE TABLE run_log (
    run_id          TEXT PRIMARY KEY,
    started_at      INTEGER NOT NULL,
    completed_at    INTEGER,
    status          TEXT NOT NULL,  -- 'running', 'complete', 'failed'
    commit_sha      TEXT,
    config_hash     TEXT,
    metrics         TEXT            -- JSON PipelineMetrics
);

CREATE TABLE run_checkpoints (
    run_id          TEXT NOT NULL REFERENCES run_log(run_id),
    stage           TEXT NOT NULL,
    status          TEXT NOT NULL,
    started_at      INTEGER NOT NULL,
    completed_at    INTEGER,
    record_count    INTEGER,
    error_message   TEXT,
    
    PRIMARY KEY(run_id, stage)
);
```

### 9.4 Tracing (Optional)

For debugging signal provenance:
```sql
CREATE TABLE signal_provenance (
    snapshot_id     TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,
    producer        TEXT NOT NULL,      -- stage/function that produced
    inputs          TEXT,               -- JSON list of input signals
    computed_at     INTEGER NOT NULL,
    
    PRIMARY KEY(snapshot_id, entity_id, signal_name)
);
```

---

## 10. Constraints & Limitations

### 10.1 Hard Limits

| Constraint | Limit | Rationale |
|------------|-------|-----------|
| Max files | 100,000 | Memory for graphs |
| Max commits | 50,000 | Git extraction time |
| Max file size | 10 MB | Parse memory |
| Max edge count | 10M | Memory for algorithms |
| Max history depth | 20 snapshots | Storage |

### 10.2 Graceful Degradation

| Condition | Degradation | Impact |
|-----------|-------------|--------|
| No git | Skip temporal stages | No churn, cochange, trajectory signals |
| >5000 files | Skip NCD clone detection | No CLONE graph |
| >10000 files | Approximate spectral | Lower accuracy fiedler |
| No tree-sitter | Regex fallback | Less accurate parsing |
| <15 files | ABSOLUTE tier | No percentiles, threshold-based |

### 10.3 Unsupported Scenarios

| Scenario | Reason | Workaround |
|----------|--------|------------|
| Binary files | Can't parse | Excluded by default |
| Encrypted repos | Can't read git | Decrypt first |
| Shallow clones | Incomplete history | Full clone required |
| Submodules | Separate repos | Analyze separately |
| Generated code | Noise | Add to exclusions |

### 10.4 Assumptions

| Assumption | Impact if Violated |
|------------|-------------------|
| Files are UTF-8 | Parse errors |
| Git history is linear-ish | Merge commit handling may be imprecise |
| Import syntax is standard | Unresolved imports |
| Single language per file | Wrong parser selected |
| Stable file paths | Rename detection fails |

---

## Appendix A: Signal Quick Reference

### A.1 Layer 0-2: Base Signals (24)

| # | Signal | Scope | Type | Layer |
|---|--------|-------|------|-------|
| 1 | lines | FILE | int | L0 |
| 2 | function_count | FILE | int | L0 |
| 3 | class_count | FILE | int | L0 |
| 4 | import_count | FILE | int | L0 |
| 5 | max_nesting | FILE | int | L0 |
| 6 | complexity | FILE | int | L0 |
| 7 | stub_ratio | FILE | float | L0 |
| 8 | impl_gini | FILE | float | L0 |
| 9 | total_changes | FILE | int | L2-T |
| 10 | churn_cv | FILE | float | L2-T |
| 11 | churn_slope | FILE | float | L2-T |
| 12 | churn_trajectory | FILE | enum | L2-T |
| 13 | bus_factor | FILE | float | L2-T |
| 14 | author_entropy | FILE | float | L2-T |
| 15 | fix_ratio | FILE | float | L2-T |
| 16 | refactor_ratio | FILE | float | L2-T |
| 17 | change_entropy | FILE | float | L2-T |
| 18 | role | FILE | enum | L2-S |
| 19 | concept_count | FILE | int | L2-S |
| 20 | concept_entropy | FILE | float | L2-S |
| 21 | naming_drift | FILE | float | L2-S |
| 22 | todo_density | FILE | float | L2-S |
| 23 | docstring_coverage | FILE | float | L2-S |
| 24 | semantic_coherence | FILE | float | L2-S |

### A.2 Layer 3: Graph Signals (19 × R relationship types)

| # | Signal | Scope | Per Relation |
|---|--------|-------|--------------|
| 25 | pagerank | FILE | Yes |
| 26 | betweenness | FILE | Yes |
| 27 | in_degree | FILE | Yes |
| 28 | out_degree | FILE | Yes |
| 29 | blast_radius_size | FILE | Yes |
| 30 | depth | FILE | Yes |
| 31 | is_orphan | FILE | Yes |
| 32 | cycle_member | FILE | Yes |
| 33 | cycle_size | FILE | Yes |
| 34 | phantom_import_count | FILE | IMPORT only |
| 35 | community | FILE | Yes |
| 36 | compression_ratio | FILE | No |
| 37 | cognitive_load | FILE | No |
| 38 | modularity | CODEBASE | Yes |
| 39 | cycle_count | CODEBASE | Yes |
| 40 | centrality_gini | CODEBASE | Yes |
| 41 | fiedler_value | CODEBASE | Yes |
| 42 | spectral_gap | CODEBASE | Yes |
| 43 | density | CODEBASE | Yes |

### A.3 Layer 4: Trajectory Signals (8)

| # | Signal | Scope |
|---|--------|-------|
| 44 | pagerank_velocity | FILE |
| 45 | pagerank_acceleration | FILE |
| 46 | community_stability | FILE |
| 47 | centrality_trend | FILE |
| 48 | graph_velocity | CODEBASE |
| 49 | fiedler_trend | CODEBASE |
| 50 | modularity_trend | CODEBASE |
| 51 | topology_stability | CODEBASE |

### A.4 Layer 5: Cross-Layer Signals (7)

| # | Signal | Scope |
|---|--------|-------|
| 52 | hidden_coupling_count | FILE |
| 53 | neighborhood_coherence | FILE |
| 54 | hidden_coupling | PAIR |
| 55 | conway_violation | PAIR |
| 56 | behavioral_coherence | CODEBASE |
| 57 | conway_alignment | CODEBASE |
| 58 | semantic_alignment | CODEBASE |

### A.5 Layer 6: Composite Signals (21)

| # | Signal | Scope |
|---|--------|-------|
| 59 | raw_risk | FILE |
| 60 | risk_score | FILE |
| 61 | wiring_quality | FILE |
| 62 | file_health_score | FILE |
| 63 | delta_h | FILE |
| 64 | cohesion | MODULE |
| 65 | coupling | MODULE |
| 66 | instability | MODULE |
| 67 | abstractness | MODULE |
| 68 | main_seq_distance | MODULE |
| 69 | boundary_alignment | MODULE |
| 70 | role_consistency | MODULE |
| 71 | velocity | MODULE |
| 72 | coordination_cost | MODULE |
| 73 | knowledge_gini | MODULE |
| 74 | module_bus_factor | MODULE |
| 75 | health_score | MODULE |
| 76 | wiring_score | CODEBASE |
| 77 | architecture_health | CODEBASE |
| 78 | team_risk | CODEBASE |
| 79 | codebase_health | CODEBASE |

**Total: 79 signals** (plus R×19 for multi-relationship graph signals)

---

## Appendix B: Finder Quick Reference

| # | Pattern | Scope | Key Signals | Layer |
|---|---------|-------|-------------|-------|
| 1 | GOD_FILE | FILE | lines, cognitive_load, in_degree | L0+L3 |
| 2 | ORPHAN_CODE | FILE | is_orphan, role | L3+L2 |
| 3 | PHANTOM_DEPENDENCY | FILE | phantom_import_count | L3 |
| 4 | CIRCULAR_DEPENDENCY | FILE | cycle_member, cycle_size | L3 |
| 5 | COPY_PASTE_CLONE | PAIR | NCD weight | L2 |
| 6 | FLAT_ARCHITECTURE | CODEBASE | modularity, centrality_gini | L3 |
| 7 | ZONE_OF_PAIN | MODULE | instability, main_seq_distance | L6 |
| 8 | ZONE_OF_USELESSNESS | MODULE | instability, abstractness | L6 |
| 9 | LAYER_VIOLATION | PAIR | layer assignments | L6 |
| 10 | BOUNDARY_MISMATCH | MODULE | boundary_alignment | L6 |
| 11 | UNSTABLE_INTERFACE | MODULE | instability, velocity | L6 |
| 12 | RIGID_CORE | MODULE | instability, coupling | L6 |
| 13 | HIGH_RISK_HUB | FILE | pagerank, churn_cv, bus_factor | L3+L2+L6 |
| 14 | HIDDEN_COUPLING | PAIR | cochange, import | L5 |
| 15 | CONWAY_VIOLATION | PAIR | import, author_overlap | L5 |
| 16 | WEAK_LINK | FILE | delta_h | L6 |
| 17 | ACCIDENTAL_COUPLING | PAIR | concept_overlap, import | L5 |
| 18 | KNOWLEDGE_SILO | MODULE | knowledge_gini, module_bus_factor | L6 |
| 19 | UNSTABLE_FILE | FILE | churn_cv, trajectory | L2 |
| 20 | BUS_FACTOR_RISK | FILE | bus_factor, pagerank | L2+L3 |
| 21 | HOLLOW_CODE | FILE | stub_ratio | L0 |
| 22 | CHRONIC_PROBLEM | FILE | finding_lifecycle | L7 |

---

*End of Document*


### [Thinking]

The user is asking a very practical question - can this actually be built? They seem somewhat amused/overwhelmed by the scope of what I've defined.

Let me think honestly about this:

**What exists today (v1):**
- 6 analyzers working
- ~69 signals computed
- 22 finders defined
- Basic persistence (snapshots)
- Working CLI on PyPI

**What the spec adds:**
- Multi-layer graphs (currently only IMPORT)
- Trajectory signals (Layer 4) - entirely new
- Cross-layer signals with MI (Layer 5) - mostly new
- Historical graph reconstruction
- Event-sourced temporal index
- Full DB persistence at every stage

**The honest assessment:**

1. **Core framework is sound** - The math is correct, the layering makes sense, the dependencies are clear.

2. **Much already exists** - Maybe 60-70% of the signals are already computed in some form. The analyzers exist. The finders exist.

3. **The hard parts:**
   - Historical graph reconstruction (expensive, but can be approximated)
   - Trajectory signals (need historical data, but can bootstrap)
   - Mutual information computation (straightforward math, just needs implementation)
   - Multi-layer graph algorithms (PageRank on cochange graph, etc.)
   - Full persistence model (significant refactor from in-memory)

4. **What's actually new vs. refactoring:**
   - NEW: Layer 4 (trajectory) - ~8 signals
   - NEW: Layer 5 cross-layer MI signals - ~6 signals  
   - NEW: Multi-relationship graph signals - running same algorithms on different graphs
   - NEW: Persistence-first architecture
   - REFACTOR: Everything else is moving existing code around

5. **Realistic build estimate:**
   - If starting from scratch: 3-6 months for a team
   - Building on v1: 4-8 weeks for focused work
   - The hardest part isn't the code, it's the testing and validation

6. **Can it be simplified?**
   - Yes, significantly
   - Trajectory signals can start with just 2-3 (pagerank_velocity, graph_velocity)
   - Cross-layer can start with just behavioral_coherence
   - Historical reconstruction can be sampled (5 points, not continuous)
   - Multi-relationship can start with IMPORT + COCHANGE only

Let me give the user an honest, practical answer.


## ASSISTANT

Honest answer:

## What Already Exists (v1)

| Component | Status | LOC |
|-----------|--------|-----|
| 6 Analyzers | ✅ Working | ~2000 |
| ~69 Signals | ✅ Computed | ~1500 |
| 22 Finders | ✅ Defined | ~1000 |
| Basic persistence | ✅ Working | ~800 |
| CLI on PyPI | ✅ Shipped | ~500 |

**You already have ~60-70% of the signals.**

## What's Actually New

| Component | Effort | Why Hard |
|-----------|--------|----------|
| Layer 4: Trajectory (8 signals) | Medium | Need historical snapshots |
| Layer 5: Cross-layer MI (6 signals) | Low | Just math, data exists |
| Multi-relationship graphs | Medium | Same algorithms, different inputs |
| Persistence-first architecture | High | Refactor from in-memory |
| Historical graph reconstruction | Medium | Can approximate cheaply |

## The Practical Build Path

**Phase 1: Quick Wins (1-2 weeks)**
```
- Add pagerank[COCHANGE] (run PageRank on cochange graph) 
- Add behavioral_coherence (MI between import and cochange)
- Add hidden_coupling_count as a FILE signal (not just pattern)
- Store graphs to DB (you already have graph_store.db)
```

**Phase 2: Trajectory Foundation (2-3 weeks)**
```
- Store 5 historical snapshots (monthly)
- Compute pagerank_velocity = (now - last_month) / 30 days
- Compute graph_velocity = edge Jaccard between snapshots
- Add 2-3 trajectory-based finders
```

**Phase 3: Full Persistence (3-4 weeks)**
```
- Refactor to read from DB, not in-memory slots
- Event-sourced temporal index
- Incremental updates
```

**Phase 4: Polish (2-3 weeks)**
```
- Remaining trajectory signals
- Full multi-relationship support
- Performance optimization
```

## The Minimal Viable Enhancement

If you want 80% of the value with 20% of the work:

```python
# Add these 5 signals to existing fusion:

1. pagerank_cochange = PageRank(G_cochange)  # 10 lines
2. behavioral_coherence = edge_overlap(G_import, G_cochange) / union  # 15 lines  
3. hidden_coupling_count = len(cochange_neighbors - import_neighbors)  # 5 lines
4. pagerank_velocity = (current - cached_last_run) / days_elapsed  # 10 lines
5. graph_velocity = edge_jaccard(G_now, G_cached)  # 10 lines
```

**50 lines of code gets you the most important cross-layer and trajectory signals.**

## The Real Answer

| Question | Answer |
|----------|--------|
| Can the full spec be built? | Yes, 2-3 months focused work |
| Should you build all of it? | Probably not all at once |
| What's the MVP? | 5 new signals + persistence refactor |
| What's blocking you? | Nothing technical, just prioritization |

The spec is comprehensive so you know WHERE you're going. You don't have to build it all at once.

**Start with**: `behavioral_coherence` and `pagerank_velocity`. Those two signals alone would catch issues the current system misses.

Want me to write just those two?


### [Thinking]

The user wants me to write a comprehensive specification document that AI agents can use to build this system from scratch. This should be a fresh project spec, not building on v1.

Let me create a complete, self-contained specification document that covers:
1. Project overview
2. Architecture
3. Data models
4. Pipeline stages
5. All signals with exact formulas
6. All finders with exact conditions
7. Database schemas
8. API contracts
9. Testing requirements
10. Everything an AI agent would need to implement this

This should be written in a way that an AI agent can follow step by step to build the entire system.


## ASSISTANT

I'll write a comprehensive specification document for AI agents to build this from scratch.


## ASSISTANT

API Error: The model has reached its context window limit.


## ASSISTANT

Prompt is too long
