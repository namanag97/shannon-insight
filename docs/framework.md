# Shannon Insight — Theoretical Framework

## 1. Core Thesis

A codebase is a measurable object. Like a physical system described by mass, charge, and spin, a codebase is fully described by a small set of **irreducible dimensions** measured at multiple **scales** across **time**.

Every code quality insight — every finding, every smell, every risk — is a derived quantity computed from these fundamentals. By identifying the fundamentals, we can:

1. **Systematically discover** new findings by exploring untested dimension combinations
2. **Unify** existing tools (linters, complexity analyzers, dependency checkers) under one theory
3. **Guarantee coverage** — if we measure all fundamentals, no category of insight is invisible
4. **Prioritize** by measuring information yield per compute cost

---

## 2. The Eight Irreducible Dimensions

These are orthogonal. None can be derived from the others.

### D1: SIZE — "How much?"

The quantity of code at any level. Lines, tokens, parameters, functions, files, modules.

Size is the simplest dimension but underpins almost every derived metric. Complexity without size is just shape. Risk without size has no blast radius.

**Measurements**: token count, line count, parameter count, field count, function count, file count, module count, total LOC.

### D2: SHAPE — "What structure?"

How code is organized internally. Depth of nesting, branching factor, distribution of sizes, symmetry of structure.

Shape captures the *geometry* of code independent of its content. A function with 10 sequential statements and a function with 10 nested conditions have the same SIZE but different SHAPE.

**Measurements**: nesting depth, cyclomatic complexity, inheritance depth, Gini coefficient of function sizes (distribution shape), branching factor, class hierarchy depth/width, architectural pattern (layered, hub-spoke, flat).

### D3: NAMING — "What concepts?"

The semantic content carried by identifiers. What a piece of code is *about*, as revealed by the words programmers chose.

Naming is the only dimension that captures **human intent at the token level**. Variable names, function names, class names — these are compressed natural language embedded in code.

**Measurements**: identifier vocabulary, concept clusters (via TF-IDF + clustering), filename-to-content alignment, naming convention consistency, vocabulary overlap between files.

### D4: REFERENCE — "What points to what?"

Every relationship where one entity depends on, uses, calls, inherits from, or refers to another.

Reference is the dimension that creates **structure between entities** (as opposed to D2 which is structure *within* entities). It's what makes a codebase a graph rather than a bag of files.

**Sub-types** (each creates a distinct graph):
- **Import**: file A imports file B
- **Call**: function in A calls function in B
- **Type**: A uses a type defined in B
- **Inheritance**: class in A extends class in B
- **Data**: A reads/writes state that B also reads/writes

**Measurements**: in-degree, out-degree, edge count, edge weight (symbol count), direction, transitivity (reachability).

### D5: INFORMATION — "How dense? How ordered?"

The information-theoretic properties of code. How much novelty, how much redundancy, how compressible.

This dimension is **language-agnostic**. Compression ratio doesn't care about syntax. Entropy doesn't care about language. It measures the pure information content independent of how it's expressed.

**Measurements**: Shannon entropy (byte-level, token-level), compression ratio (Kolmogorov approximation), Normalized Compression Distance between pairs, repetition index (duplicate lines), token entropy, surprise (information per token).

### D6: CHANGE — "How does it evolve?"

The temporal behavior of any entity. How often it changes, in what direction, at what rate, with what acceleration.

Change is the dimension that turns a snapshot into a movie. It's orthogonal to all spatial dimensions — a file can be any size, any shape, any information density, and independently change at any rate.

**Measurements**: edit frequency, churn trajectory (dormant/stabilizing/churning/spiking), velocity (changes per time unit), acceleration (d(velocity)/dt), time since last change, age, time-to-stabilize.

### D7: AUTHORSHIP — "Who touches it?"

The human/social properties. Who creates, modifies, reviews, and owns code.

Authorship is irreducible because no amount of static or temporal analysis can tell you that only one person understands a critical system. It requires a separate data source (git author data) and answers fundamentally different questions.

**Measurements**: author count, author entropy (H of contribution distribution), bus factor (2^H — effective author count), ownership concentration (max author percentage), author turnover rate, contributor overlap between entities.

### D8: INTENT — "Why was it changed?"

The purpose behind changes. Feature work, bug fix, refactoring, test, documentation, dependency update.

Intent is irreducible because the same SIZE change with the same SHAPE can be a feature or a bug fix, and these have completely different implications. A file attracting bug fixes is fundamentally different from a file attracting features.

**Measurements**: fix ratio (fraction of commits with fix/bug in message), refactor ratio, feature ratio, test ratio. Derived from commit message classification + diff shape analysis.

---

## 3. The Seven Scales

Every dimension exists at multiple levels of granularity. The scales form a containment hierarchy:

```
Scale 0: TOKEN       →  the atom
Scale 1: STATEMENT   →  a single instruction
Scale 2: FUNCTION    →  a named computation
Scale 3: CLASS       →  functions + shared state
Scale 4: FILE        →  a compilation unit
Scale 5: MODULE      →  a directory / package of files
Scale 6: CODEBASE    →  the entire system
```

**Each scale inherits from the one below.** A file's SIZE is the sum of its functions' SIZE. A module's SHAPE is the arrangement of its files' SHAPE. But each scale also has **emergent properties** not present below:

- FUNCTION has cyclomatic complexity (SHAPE) — a STATEMENT does not
- FILE has import graph position (REFERENCE) — a FUNCTION within a file does not
- MODULE has cohesion/coupling (derived from REFERENCE) — a single FILE does not
- CODEBASE has architectural pattern (SHAPE at Scale 6) — no single MODULE has this

---

## 4. The Measurement Tensor

The complete description of a codebase at one point in time is an **8 × 7 matrix** where each cell is either a scalar, a vector, or "not applicable":

```
                 S0:Token  S1:Stmt  S2:Func   S3:Class  S4:File    S5:Module    S6:Codebase
                 ────────  ───────  ────────  ────────  ─────────  ──────────   ───────────
D1:SIZE          chars     tokens   params,   methods,  functions, file count,  module count,
                                    body_tok  fields    LOC,       total LOC    total files
                                                        classes

D2:SHAPE           —         —      nesting,  inherit   fn_size    internal     architectural
                                    cyclo,    depth,    Gini,      dep struct,  pattern,
                                    branches  method    class      layer depth  layer count
                                              dist      hierarchy

D3:NAMING        kw/ident    —      fn name,  cls name, filename,  dir name,    global
                 /literal           param     method    concept    shared       conventions
                                    names     names     vocab      vocab

D4:REFERENCE       —         —      calls,    bases,    imports,   inter-mod    external
                                    reads,    composed  exports    edges,       dep graph
                                    writes    types               cohesion,
                                                                  coupling

D5:INFORMATION   surprise    —      body H,   method    file C,    internal     global
                 (context)          compress  H dist    token H,   redundancy   info density,
                                                        coherence  (mean NCD)   modularity

D6:CHANGE          —         —      edit      —         churn,     velocity,    growth rate,
                                    count,              trajectory growth       commit freq
                                    last mod

D7:AUTHORSHIP      —         —        —       —         bus factor,team size,   org contrib,
                                                        author H,  knowledge    turnover
                                                        ownership  Gini

D8:INTENT          —         —        —       —         fix ratio, module       project
                                                        refactor   purpose      phase
                                                        ratio

[ — = dimension not meaningfully measurable at this scale ]
```

**Active cells: ~40.** These are every measurement that Shannon Insight can compute. Each cell is a signal. Signals have values at every time point, creating the third axis.

---

## 5. Time as the Orthogonal Axis

Time is not a dimension like the other eight — it is the axis along which all dimensions are measured repeatedly. The full model is:

```
Measurement(dimension, scale, time) → value
```

This is a **3D tensor**. At each time point `t`, we have the full 8×7 matrix. Across time, each cell becomes a time series.

### Temporal Operators

For any signal `S(t)` (a single cell tracked over time):

| Operator | Formula | What it reveals |
|----------|---------|-----------------|
| **Delta** | `S(t) - S(t-1)` | What changed in one step |
| **Velocity** | `dS/dt` (linear regression slope) | Rate of change |
| **Acceleration** | `d²S/dt²` | Is change speeding up or slowing down? |
| **Trajectory** | classify(slope, cv) | Qualitative pattern: dormant, stabilizing, churning, spiking |
| **Volatility** | `std(S) / mean(S)` (coefficient of variation) | How erratic is this signal? |
| **Trend** | rolling mean direction | Long-term direction ignoring noise |
| **Seasonality** | autocorrelation at period `p` | Does this signal have rhythmic patterns? |
| **Stationarity** | Augmented Dickey-Fuller test | Is this process stable or drifting? |

Every signal in the 8×7 matrix can have these operators applied. This produces **second-order signals** — "the rate of change of complexity" or "the acceleration of coupling growth."

### Temporal at Each Scale

| Scale | Key temporal question |
|-------|---------------------|
| Function | When was this function last modified? Is it stable? |
| File | What's the churn trajectory? Is complexity growing? |
| Module | What's the development velocity? Is architecture eroding? |
| Codebase | Is overall health improving or declining? |

---

## 6. The Six Distance Spaces

Between any two entities, "closeness" can be measured in **six independent ways**. Each is defined by a different graph over the same set of nodes:

### Graph Definitions

| # | Graph | Nodes | Edges | Distance meaning |
|---|-------|-------|-------|-----------------|
| G1 | **Dependency** | files | import A→B | structural proximity |
| G2 | **Call** | functions | fn A calls fn B | behavioral proximity |
| G3 | **Type** | files | A uses type from B | contract proximity |
| G4 | **Co-change** | files | A,B changed in same commit | evolutionary proximity |
| G5 | **Author** | files | A,B share authors | social proximity |
| G6 | **Semantic** | files | A,B share concepts | meaning proximity |

### Distance Functions

```
d₁(A, B) = shortest_path(A, B, dependency_graph)
            ∞ if unreachable

d₂(A, B) = min call chain length between any fn in A and any fn in B
            ∞ if no call path exists

d₃(A, B) = 1 - |types_used_by_A ∩ types_defined_in_B| / |types_used_by_A|
            1 if no type relationship

d₄(A, B) = 1 / (cochange_lift(A, B) + ε)
            large if they never co-change

d₅(A, B) = 1 - |authors(A) ∩ authors(B)| / |authors(A) ∪ authors(B)|
            1 if completely different authors

d₆(A, B) = 1 - cosine(concept_vector(A), concept_vector(B))
            1 if no shared concepts
```

### The Disagreement Principle

**Findings are disagreements between distance spaces.**

When two distance spaces tell contradictory stories about the same pair of entities, something interesting is happening:

| d_space₁ says CLOSE | d_space₂ says FAR | Finding |
|---------------------|-------------------|---------|
| G4 Co-change | G1 Dependency | **Hidden coupling** — change together but no import |
| G1 Dependency | G4 Co-change | **Dead dependency** — import exists, never co-change |
| G6 Semantic | G1 Dependency | **Missed abstraction** — same concepts, not connected |
| G1 Dependency | G6 Semantic | **Accidental coupling** — connected but unrelated concepts |
| G5 Author | G1 Dependency | **Conway violation** — same team, different modules |
| G1 Dependency | G5 Author | **Coordination risk** — coupled code, different teams |
| G2 Call | G3 Type | **Weak contract** — calling through untyped interfaces |
| G1 Dependency | G2 Call | **Dead import** — import but no actual function calls |
| G6 Semantic | G5 Author | **Knowledge misalignment** — similar code, different owners |
| G4 Co-change | G6 Semantic | **Coincidental coupling** — co-evolve but unrelated concepts |

**Systematic finding discovery**: for each of the C(6,2) = 15 pairs of distance spaces, ask "what entities are close in one but far in the other?" Each pair potentially defines a new class of finding.

### Disagreement Score

```
For pair of files (A, B):

  rank_k(A, B) = percentile rank of d_k(A, B) among all file pairs
                 in distance space k

  disagreement(A, B, k₁, k₂) = |rank_k₁(A, B) - rank_k₂(A, B)|
```

High disagreement = the two spaces tell contradictory stories. Worth investigating.

**Aggregate disagreement** for a file:

```
  anomaly(A) = max over all B, all space pairs (k₁, k₂):
               disagreement(A, B, k₁, k₂)
```

Files with high aggregate anomaly are "structurally surprising" — they sit in unusual positions in the multi-space landscape.

---

## 7. Derived Dimensions

All higher-level concepts are **products of fundamentals**:

### First-Order Derivations (two fundamentals combined)

| Derived | = | Dim₁ | × | Dim₂ | Intuition |
|---------|---|------|---|------|-----------|
| **Complexity** | | SIZE | × | SHAPE | Big AND deep = hard to understand |
| **Coupling** | | REFERENCE | between | two entities | How entangled |
| **Cohesion** | | REFERENCE | + | NAMING within entity | Parts belong together |
| **Density** | | SIZE | / | INFORMATION | Big but low entropy = boilerplate |
| **Volatility** | | CHANGE | × | CHANGE.variance | Frequent AND erratic changes |
| **Ownership** | | AUTHORSHIP | × | concentration | How monopolized is knowledge |
| **Purposefulness** | | INTENT | × | consistency | Are changes deliberate or reactive |

### Second-Order Derivations (three+ fundamentals)

| Derived | = | Components | Intuition |
|---------|---|------------|-----------|
| **Risk** | | REFERENCE × CHANGE × SIZE | Central, changing, big = dangerous |
| **Knowledge risk** | | REFERENCE × (1/AUTHORSHIP) × SIZE | Central, big, single owner |
| **Debt** | | accumulated INTENT("fix") × SIZE × CHANGE | Bug-prone, big, still changing |
| **Staleness** | | SIZE × (1/CHANGE) × AUTHORSHIP.turnover | Big, untouched, original authors gone |
| **Drift** | | ΔNAMING / ΔTIME with low ΔREFERENCE | Concepts changing but structure not adapting |
| **Erosion** | | ΔSHAPE(worsening) × ΔCHANGE(accelerating) | Structure degrading faster over time |
| **Fragility** | | REFERENCE.blast_radius × (1/INFORMATION.coherence) | Wide impact + low internal focus |
| **Wiring quality** | | REFERENCE.connectivity × SIZE.completeness × INFORMATION.density | How well-connected and implemented (AI detection) |

### Finding Decomposition

Every finding is a threshold condition on derived dimensions:

```
FINDING                CONDITION (in fundamental dimensions)
───────                ──────────────────────────────────────
God file               SIZE(file).functions HIGH
                       × SHAPE(file).gini HIGH
                       × NAMING(file).concept_count HIGH
                       × INFORMATION(file).coherence LOW

High risk hub          REFERENCE(file).pagerank HIGH
                       × REFERENCE(file).blast_radius HIGH
                       × CHANGE(file).velocity HIGH
                       × SIZE(file).loc HIGH

Hidden coupling        REFERENCE(pair).dependency_distance FAR
                       × CHANGE(pair).cochange_distance CLOSE

Dead dependency        REFERENCE(pair).dependency_distance CLOSE
                       × CHANGE(pair).cochange_distance FAR

Unstable file          CHANGE(file).trajectory = CHURNING
                       × CHANGE(file).total HIGH

Boundary mismatch      REFERENCE(module).community ≠ SHAPE(module).directory
                       × REFERENCE(module).alignment LOW

Knowledge silo         AUTHORSHIP(file).bus_factor = 1
                       × REFERENCE(file).pagerank HIGH

Orphan code            REFERENCE(file).in_degree = 0
                       × NAMING(file).role ≠ ENTRY_POINT

Stub/hollow code       SIZE(file).function_count HIGH
                       × INFORMATION(file).density LOW
                       × SHAPE(file).impl_gini HIGH

Architecture erosion   ΔSHAPE(module).violations INCREASING
                       × ΔREFERENCE(module).coupling INCREASING
                       × ΔCHANGE(module).velocity INCREASING

Conway violation       AUTHORSHIP(pair).distance FAR
                       × REFERENCE(pair).dependency_distance CLOSE
```

This decomposition means: **to add a new finding, express it as a condition on fundamental dimensions.** If the fundamentals are measured, the finding falls out automatically.

---

## 8. The Computation Architecture

The measurement tensor is computed through a series of **Intermediate Representations**, each corresponding to a band of the tensor:

```
IR    WHAT IT COMPUTES                   TENSOR REGION
──    ──────────────────                 ─────────────
IR0   Raw file content                   D1(S0-S4), D3(S0) — raw size and identifiers
IR1   Syntactic structure                D1(S2-S4), D2(S2-S4), D4(S2-S3) — parsed structure
IR2   Semantic meaning                   D3(S2-S5), D5(S4) — concepts, roles, coherence
IR3   Relationship graph                 D4(S4-S6), D5(S4-S5 pairs) — all reference types + NCD
IR4   Architectural model                D2(S5-S6), D4(S5-S6) — layers, modules, patterns
IR5t  Temporal model                     D6(all), D7(all), D8(all) — change, authors, intent
IR5s  Signal field                       All derived dimensions — fusion + composites
IR6   Insights                           Finding conditions on derived dimensions
```

### Computation DAG

```
DATA SOURCES (roots — no dependencies)
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Source      │  │ Git        │  │ Project    │
│ Files      │  │ History    │  │ Config     │
│            │  │            │  │            │
│ (bytes,    │  │ (commits,  │  │ (entries,  │
│  paths)    │  │  authors,  │  │  deps,     │
│            │  │  messages) │  │  settings) │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │
      ▼               │               │
┌───────────┐         │               │
│ IR0       │         │               │
│           │         │               │
│ FileEntry │         │               │
│ per file: │         │               │
│  path     │         │               │
│  bytes    │         │               │
│  size     │         │               │
│  hash     │         │               │
│  language │         │               │
└─────┬─────┘         │               │
      │               │               │
      ▼               │               │
┌───────────┐         │               │
│ IR1       │         │               │
│           │         │               │
│ per file: │         │               │
│  functions│         │               │
│   .name   │         │               │
│   .params │         │               │
│   .body   │         │               │
│   .calls  │         │               │
│  classes  │         │               │
│  imports  │         │               │
│   .resolved_path    │               │
│   (null=phantom)    │               │
└─────┬─────┘         │               │
      │               │               │
      ▼               │               │
┌───────────┐         │               │
│ IR2       │         │               │
│           │         │               │
│ per file: │         │               │
│  role     │         │               │
│  concepts │         │               │
│  public_api         │               │
│  consumed_api       │               │
│  completeness       │               │
└─────┬─────┘         │               │
      │               │               │
      │               ▼               │
      │        ┌─────────────┐        │
      │        │ IR5t        │        │
      │        │             │        │
      │        │ per file:   │        │
      │        │  churn      │        │
      │        │  authors    │        │
      │        │  bus_factor │        │
      │        │  fix_ratio  │        │
      │        │             │        │
      │        │ per pair:   │        │
      │        │  cochange   │        │
      │        │  lift       │        │
      │        │             │        │
      │        │ per module: │        │
      │        │  velocity   │        │
      │        │  coord_cost │        │
      │        └──────┬──────┘        │
      │               │               │
      ▼               │               │
┌───────────┐         │               │
│ IR3       │◄────────┘               │
│           │   (temporal enriches    │
│ graph:    │    edges with cochange  │
│  nodes    │    data)                │
│  edges    │                         │
│   import  │◄────────────────────────┘
│   call    │   (config provides entry points
│   type    │    and declared deps for
│  phantoms │    phantom detection)
│           │
│ derived:  │
│  pagerank │
│  scc      │
│  blast    │
│  louvain  │
│  depth    │
│  spectral │
│  orphans  │
│  NCD pairs│
└─────┬─────┘
      │
      ▼
┌───────────┐
│ IR4       │
│           │
│ modules[] │
│  cohesion │
│  coupling │
│  I, A, D  │
│ layers[]  │
│ violations│
│ patterns  │
└─────┬─────┘
      │
      ▼
┌───────────┐
│ IR5s      │
│ (signals) │
│           │
│ per file: │
│  ~25 signals from IR1-IR5t
│  + composites (risk, wiring)
│           │
│ per module:│
│  ~15 signals from IR4+aggregated
│  + health_score
│           │
│ global:   │
│  ~10 signals
│  + codebase_health
└─────┬─────┘
      │
      ▼
┌───────────┐
│ IR6       │
│ (insights)│
│           │
│ findings[]│
│  evidence chains across IRs
│  severity, confidence
│  temporal context
│  suggestions with effort/impact
│           │
│ composites│
│  ai_quality_score
│  architecture_health
│  team_risk
│  codebase_health
└───────────┘
```

### Parallel Execution

The DAG has three independent spines that merge at IR3:

```
STRUCTURAL SPINE          TEMPORAL SPINE         CONFIG
IR0 → IR1 → IR2 ──┐      Git → IR5t ──┐        pyproject → entry_points ──┐
                   ├──→ IR3 ◄──────────┘                                   │
                   │         ◄─────────────────────────────────────────────┘
                   │
                   ├──→ IR4
                   │
                   └──→ IR5s → IR6
```

The structural spine (IR0→IR1→IR2) and temporal spine (Git→IR5t) run **fully in parallel** with zero data dependencies. They merge at IR3 where temporal data enriches graph edges.

### Demand-Driven Evaluation

Not all cells of the tensor need computation for every query. The kernel traces **backward from the requested findings** to determine which IRs (and which cells within each IR) are needed.

```
User requests: "AI code quality check"

Required findings: OrphanCode, StubCode, PhantomImport, FlatArchitecture
  → needs: orphan_ratio, stub_ratio, phantom_ratio, glue_deficit, impl_gini
    → needs IR3: graph (for orphans, phantoms, depth)
      → needs IR1: imports, functions (for graph building + stub detection)
        → needs IR0: file content
    → needs IR2: NO (not needed for these specific findings)
    → needs IR4: NO
    → needs IR5t: NO (no temporal signals required)

Execution plan: IR0 → IR1 → IR3 (partial: graph + orphans + phantoms + depth)
Skipped: IR2, IR4, IR5t, spectral, NCD, PageRank, Louvain
```

Versus full analysis: IR0 → IR1 → IR2 → IR5t → IR3 → IR4 → IR5s → IR6.

This is implemented via a **signal registry**:

```
Signal:
  name:          str                    # "orphan_ratio"
  ir_level:      int                    # 3
  depends_on:    [str]                  # ["graph", "entry_points"]
  compute:       Callable               # function that computes this signal
  dimension:     Dimension              # D4 (REFERENCE)
  scale:         Scale                  # S4 (FILE)

# Kernel resolution:
def execution_plan(required_signals: set[str]) -> list[Signal]:
    needed = transitive_closure(required_signals, depends_on)
    return topological_sort(needed)
```

### Persistence Strategy

| IR | Persist? | Reason |
|----|----------|--------|
| IR0 | Hash only | Git stores the content; we just need change detection |
| IR1 | Summary only | Recompute from source is fast; store function_count, stub_ratio |
| IR2 | Roles + concepts | Concept drift detection needs historical concept vectors |
| IR3 | Edges + key metrics | Graph diffing needs edge lists; store pagerank, cycles, modularity |
| IR4 | Full | Small (module-level); architecture drift needs full history |
| IR5t | Full | This IS the temporal data; it accumulates |
| IR5s | Key signals per file | Sparklines need historical signal values |
| IR6 | Full | Findings are the product; chronic detection needs history |

Storage format: SQLite (existing `.shannon/history.db`), one snapshot row per analysis run, with per-file signal columns and serialized graph/architecture data.

---

## 9. Cross-Dimensional Queries

The power of the framework is in queries that span multiple dimensions and scales simultaneously. These are organized by the **question pattern**:

### Pattern: "X but not Y" (Disagreement)

Two dimensions tell contradictory stories about the same entity.

| Query | Dimensions | Finding |
|-------|-----------|---------|
| High REFERENCE but low AUTHORSHIP | D4 × D7 | Knowledge risk — critical code, single owner |
| High CHANGE but low INTENT("feature") | D6 × D8 | Constant fixes — code is buggy, not evolving |
| High SIZE but low INFORMATION | D1 × D5 | Boilerplate / copy-paste — big but low entropy |
| High REFERENCE.in but low REFERENCE.call | D4 × D4 | Dead imports — imported but never called |
| High NAMING.concepts but low SHAPE.distribution | D3 × D2 | God file — many concepts, flat structure |
| Close CHANGE but far REFERENCE | D6 × D4 | Hidden coupling — co-evolve without dependency |
| Close REFERENCE but far NAMING | D4 × D3 | Accidental coupling — connected, unrelated |
| Close AUTHORSHIP but far REFERENCE | D7 × D4 | Conway violation — same team, separate code |

### Pattern: "X and Y and Z" (Compound risk)

Multiple dimensions align to amplify a problem.

| Query | Dimensions | Finding |
|-------|-----------|---------|
| High SIZE + High REFERENCE + High CHANGE | D1 × D4 × D6 | High risk hub |
| Low INFORMATION + High SIZE.fn_count + High SHAPE.gini | D5 × D1 × D2 | AI stub code |
| High CHANGE + High INTENT("fix") + High REFERENCE | D6 × D8 × D4 | Bug attractor in critical path |
| Low AUTHORSHIP + High CHANGE + High REFERENCE | D7 × D6 × D4 | Bus factor crisis — one person changing central code |
| Increasing REFERENCE.coupling + Increasing CHANGE.velocity | ΔD4 × ΔD6 | Architecture erosion (temporal compound) |

### Pattern: Scale bridging

Same dimension, different scales, inconsistent values.

| Query | Scales | Finding |
|-------|--------|---------|
| File NAMING ≠ Module NAMING | S4 vs S5 | Misplaced file — file concepts don't match module theme |
| File SHAPE(high) but Module SHAPE(uniform) | S4 vs S5 | God file hiding in a healthy module |
| Function AUTHORSHIP concentrated but File AUTHORSHIP distributed | S2 vs S4 | Partial knowledge — many authors but each knows only their functions |
| Module REFERENCE.cohesion high but Codebase REFERENCE.modularity low | S5 vs S6 | Good modules, bad boundaries |

---

## 10. The AI Code Quality Special Case

AI-generated code has a distinctive signature in the measurement tensor:

| Dimension | Healthy codebase | AI-generated codebase |
|-----------|-----------------|----------------------|
| D1 SIZE | Varies naturally | Suspiciously uniform file sizes |
| D2 SHAPE | Gini of fn sizes moderate (0.3-0.5) | Bimodal Gini (>0.6) — some complete, some stubs |
| D3 NAMING | Concepts match filenames | Naming drift — generic names, copy-paste identifiers |
| D4 REFERENCE | Connected graph, moderate depth | Sparse graph, many orphans, flat (depth ≤ 1) |
| D5 INFORMATION | Moderate compression (0.3-0.6) | Low function-level entropy (stubs) + high NCD (clones) |
| D6 CHANGE | Organic commit history | Burst creation, then silence |
| D7 AUTHORSHIP | Multiple authors | Single author (or single AI session) |
| D8 INTENT | Mix of feature/fix/refactor | All "initial commit" or "add feature" |

**AI wiring score** — a composite that captures the distinctive multi-dimensional signature:

```
wiring = 1 - (
    w₁ × D4.orphan_ratio                          # disconnected files
  + w₂ × D5.mean_stub_body_ratio                  # hollow implementations
  + w₃ × D4.phantom_ratio                         # hallucinated references
  + w₄ × D4.glue_deficit                          # no composition layer
  + w₅ × D2.impl_gini_above_threshold_ratio       # bimodal implementation
  + w₆ × max(0, uniform_size_score - 0.8)         # suspiciously uniform file sizes
)
```

Where each weight reflects the signal's discriminative power (tuned on labeled data if available, else equal weights as starting point).

---

## 11. Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    THE COMPLETE MODEL                        │
│                                                             │
│   8 Dimensions  ×  7 Scales  ×  Time  =  Measurement Tensor│
│                                                             │
│   6 Distance Spaces between entities                        │
│                                                             │
│   Derived dimensions = products of fundamentals             │
│   Findings = threshold conditions on derived dimensions     │
│            = disagreements between distance spaces           │
│                                                             │
│   Computed via IR pipeline:                                 │
│     IR0 (files) → IR1 (syntax) → IR2 (semantics)           │
│       → IR3 (graph) → IR4 (architecture)                    │
│     IR5t (temporal) runs in parallel                        │
│     IR5s (signals) fuses all → IR6 (insights)               │
│                                                             │
│   Demand-driven: only compute cells needed for              │
│   the requested findings                                    │
│                                                             │
│   Persistent: key signals stored for temporal               │
│   analysis across snapshots                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

The framework gives us:
1. **Completeness** — every possible code measurement maps to a cell in the tensor
2. **Composability** — new findings = new conditions on existing signals
3. **Discoverability** — unexplored dimension pairs = potential new findings
4. **Efficiency** — demand-driven evaluation skips unneeded computation
5. **Unification** — all existing tools (linters, complexity, deps, git analysis) are subsets of this tensor
