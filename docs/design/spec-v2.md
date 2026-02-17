# Shannon Insight v2 — Product & Engineering Specification

## 1. Vision

Shannon Insight is a codebase intelligence platform that treats source code as a measurable physical system. It computes a multi-dimensional measurement tensor over every file, module, and the codebase as a whole — across time — and surfaces actionable insights by detecting anomalies, disagreements, and threshold violations in that tensor.

v2 expands from a CLI reporting tool to an **interactive exploration platform** with a web UI, while keeping the analysis engine as a standalone open-source library.

### What Makes This Different

| Existing tools | Shannon Insight v2 |
|---|---|
| Measure one dimension (complexity OR dependencies OR churn) | Measure 8 dimensions simultaneously, find cross-dimensional anomalies |
| File-level metrics | 7 scales from token to codebase, with module and architecture levels |
| Snapshot analysis | Full temporal dimension — every metric is a time series |
| Hand-crafted rules | Systematic finding discovery via distance space disagreements |
| Terminal output | Interactive multi-view web exploration |
| No AI code awareness | First-class AI code quality detection (orphans, stubs, phantoms, wiring) |

---

## 2. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         CORE ENGINE                               │
│                    (Python library — open source)                  │
│                                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Scanner │→│  IR1    │→│  IR2    │→│  IR3    │→ ...→ IR6    │
│  │ (IR0)   │  │ Syntax  │  │ Semant  │  │ Graph   │             │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
│       ↑                                                          │
│  ┌─────────┐                    ┌──────────────┐                 │
│  │   Git   │───────────────────→│  IR5-temporal │                │
│  └─────────┘                    └──────────────┘                 │
│                                                                   │
│  Output: TensorSnapshot (the universal data contract)            │
└──────────────────────┬───────────────────────────────────────────┘
                       │
            TensorSnapshot (JSON / protobuf / SQLite)
                       │
         ┌─────────────┼──────────────┐
         │             │              │
    ┌────▼────┐  ┌─────▼─────┐  ┌────▼────────┐
    │   CLI   │  │ Local Web │  │ CI Runner   │
    │         │  │ Server    │  │ (GH Action) │
    │ Terminal│  │ FastAPI + │  │             │
    │ output  │  │ SPA       │  │ PR comments │
    │         │  │           │  │ + upload    │
    └─────────┘  └─────┬─────┘  └──────┬──────┘
                       │               │
                       └───────┬───────┘
                               │
                        ┌──────▼──────┐
                        │   Web UI    │
                        │  (5 views)  │
                        └─────────────┘
```

### Component Responsibilities

| Component | Responsibility | Runs where |
|---|---|---|
| Core Engine | Compute IR0→IR6, produce TensorSnapshot | Where the code is (local, CI, cloud) |
| CLI | Terminal output for quick checks | Developer machine |
| Local Web Server | Serve frontend + REST API over local data | Developer machine (localhost) |
| CI Runner | Analyze PRs, post comments, upload snapshots | CI environment |
| Web UI | Interactive exploration of tensor data | Browser |
| API Server (optional) | Store snapshots, serve historical data, team features | Cloud (for SaaS/team use) |

### Key Principle

The engine is the product. Everything else is a view into its output. The engine works without any server, UI, or network — `pip install` and run.

---

## 3. Theoretical Foundation

### 3.1 The Eight Irreducible Dimensions

Every property of code derives from combinations of these orthogonal dimensions:

| # | Dimension | Question | Mathematical object |
|---|-----------|----------|-------------------|
| D1 | **SIZE** | How much? | Positive integers, distributions (Gini), growth models |
| D2 | **SHAPE** | What structure? | Trees, nesting depth, cyclomatic complexity, Gini of function sizes |
| D3 | **NAMING** | What concepts? | Token vectors in TF-IDF space, cosine similarity, clustering |
| D4 | **REFERENCE** | What points where? | Directed multi-graphs, centrality, spectral decomposition |
| D5 | **INFORMATION** | How dense/ordered? | Shannon entropy, Kolmogorov complexity (compression), NCD |
| D6 | **CHANGE** | How does it evolve? | Time series, regression, trajectory classification |
| D7 | **AUTHORSHIP** | Who touches it? | Discrete distributions, entropy, Gini, overlap measures |
| D8 | **INTENT** | Why was it changed? | Commit classification, proportional analysis |

### 3.2 The Seven Scales

Each dimension is measured at every level of granularity:

| Scale | Entity | Example SIZE measurement | Example REFERENCE measurement |
|---|---|---|---|
| S0 | Token | Character count | — |
| S1 | Statement | Token count | Variables used |
| S2 | Function | Params, body tokens, lines | Calls made, vars read/written |
| S3 | Class | Methods, fields | Base classes, composed types |
| S4 | File | Functions, LOC, classes | Imports, exports |
| S5 | Module | File count, total LOC | Inter-module edges, cohesion/coupling |
| S6 | Codebase | Modules, total files | Dependency graph topology |

### 3.3 The Measurement Tensor

The complete description of a codebase is:

```
M(dimension, scale, time) → value
```

An 8 × 7 × T tensor. ~40 active cells (not all dimension×scale combinations are meaningful). Each cell is a signal that can be tracked over time.

### 3.4 The Six Distance Spaces

Between any two files, "closeness" has six independent meanings:

| Graph | Edges | Distance meaning |
|---|---|---|
| G1 Dependency | import A→B | Structural proximity |
| G2 Call | fn A calls fn B | Behavioral proximity |
| G3 Type | A uses type from B | Contract proximity |
| G4 Co-change | A,B in same commit | Evolutionary proximity |
| G5 Author | A,B share authors | Social proximity |
| G6 Semantic | A,B share concepts | Meaning proximity |

### 3.5 The Disagreement Principle

**Findings are disagreements between distance spaces.** When two spaces tell contradictory stories about the same file pair, there is an insight:

| Close in | Far in | Finding |
|---|---|---|
| G4 Co-change | G1 Dependency | Hidden coupling |
| G1 Dependency | G4 Co-change | Dead dependency |
| G6 Semantic | G1 Dependency | Missed abstraction |
| G1 Dependency | G6 Semantic | Accidental coupling |
| G5 Author | G1 Dependency | Conway violation |
| G1 Dependency | G5 Author | Coordination risk |
| G2 Call | G3 Type | Weak contract |
| G1 Dependency | G2 Call | Dead import |

15 pairs of 6 spaces = systematic finding discovery. Each unexplored pair is a potential new finding class.

### 3.6 Derived Dimensions

Higher-level concepts are products of fundamentals:

| Derived | Components | Intuition |
|---|---|---|
| Complexity | SIZE × SHAPE | Big AND deep |
| Coupling | REFERENCE between entities | How entangled |
| Cohesion | REFERENCE + NAMING within entity | Parts belong together |
| Risk | REFERENCE × CHANGE × SIZE | Central, volatile, big |
| Knowledge risk | REFERENCE × (1/AUTHORSHIP) | Central, single owner |
| Debt | accumulated INTENT("fix") × SIZE | Bug-prone and big |
| Drift | ΔNAMING / ΔTIME | Concepts changing, names not |
| Erosion | ΔSHAPE(worsening) × ΔCHANGE(accelerating) | Structure degrading faster |
| Wiring quality | REFERENCE.connectivity × INFORMATION.density | Connected and implemented |

Every finding decomposes into a condition on derived dimensions. To add a new finding: express it as a condition on fundamentals.

---

## 4. Data Pipeline — Intermediate Representations

### 4.1 Pipeline Overview

```
DATA SOURCES (parallel)
├── Source files ─→ IR0 (FileSystem)
├── Git history  ─→ IR5t (TemporalModel)    ← parallel with structural spine
└── Project config ─→ entry points, declared deps

STRUCTURAL SPINE (sequential)
IR0 → IR1 (SyntacticForm) → IR2 (SemanticForm) → IR3 (RelationshipGraph) → IR4 (ArchitecturalModel)

FUSION
IR1 + IR2 + IR3 + IR4 + IR5t → IR5s (SignalField)

OUTPUT
IR5s → IR6 (Insights) → TensorSnapshot
```

The structural spine and temporal spine run **fully in parallel** — zero data dependencies until they merge at IR3 (temporal data enriches graph edges with co-change).

### 4.2 IR0: FileSystem

**Input**: Directory path.
**Output**: File entries with path, bytes, size, content hash, detected language.
**Time**: O(n), I/O bound. ~50ms for 100 files.

Data model:
```
FileEntry:
  path:      str          # relative to project root
  content:   bytes
  size:      int
  hash:      str          # SHA-256 for change detection
  language:  Language      # auto-detected
```

### 4.3 IR1: SyntacticForm

**Input**: IR0.
**Output**: Per-file structural data — functions (with body tokens, calls, nesting), classes (with fields, methods), imports (with resolution status).
**Math**: AST parsing, token counting, import path resolution.
**Time**: O(n × avg_file_size). ~200ms for 100 files.

Data model:
```
FileSyntax:
  path:       str
  functions:  [FunctionDef]     # name, params, body_tokens, signature_tokens,
                                #   calls[], nesting_depth, start/end line
  classes:    [ClassDef]        # name, bases, methods[], fields[], is_abstract
  imports:    [ImportDecl]      # source, names, resolved_path (null = phantom)
```

Key computations:
- **Stub score per function**: `1 - min(1, body_tokens / (signature_tokens × 3))`
- **Implementation Gini per file**: Gini coefficient of function body_tokens — bimodal = AI signature (G > 0.6)

### 4.4 IR2: SemanticForm

**Input**: IR1.
**Output**: Per-file semantic data — role classification, concept clusters, public API, consumed API, completeness metrics.
**Math**: Decision tree classification (roles), TF-IDF + Louvain clustering (concepts), cosine similarity (naming drift).
**Time**: O(n × avg_tokens). ~100ms for 100 files.

Data model:
```
FileSemantics:
  path:          str
  role:          Role            # MODEL, SERVICE, UTILITY, CONFIG, TEST, CLI,
                                 #   INTERFACE, EXCEPTION, CONSTANT, ENTRY_POINT
  concepts:      [Concept]       # topic, tokens[], weight
  public_api:    [Symbol]        # name, kind, params
  consumed_api:  [ConsumedSymbol]# source_file, symbols_used[]
  completeness:  Completeness    # stub_ratio, implementation_gini, todo_density
```

Key computations:
- **Role classification**: Deterministic decision tree on structural signals (test patterns → TEST, has ABC → INTERFACE, field-heavy classes → MODEL, stateless functions → UTILITY, etc.)
- **Concept extraction**: Extract identifiers → split camelCase/snake_case → TF-IDF vectors → build within-file co-occurrence graph → Louvain community detection → each community = a concept
- **Concept entropy**: `H = -Σ w(c) × log₂(w(c))`. H = 0 = focused. H > 1.5 = god file.
- **Naming drift**: `1 - cosine(tfidf(filename_tokens), tfidf(content_concept_tokens))`
- **Completeness**: stub_ratio from IR1, implementation Gini from IR1, TODO/FIXME density

### 4.5 IR3: RelationshipGraph

**Input**: IR1 (imports, calls), IR2 (annotated nodes), IR5t (co-change data for edge enrichment), project config (entry points).
**Output**: Multi-edge dependency graph with centrality, cycles, blast radius, communities, depth, spectral metrics, orphans, phantoms, NCD clone pairs.
**Math**: PageRank, Tarjan SCC, BFS blast radius, Louvain, topological sort, Lanczos eigendecomposition, NCD with MinHash pre-filtering.
**Time**: O(|V|² + |E| × k) for most algorithms. Spectral via Lanczos: O(k × |E|). NCD with pruning: O(0.05n²). ~300ms for 100 files.

Data model:
```
CodeGraph:
  nodes:       {path: FileNode}   # with references to IR1/IR2
  edges:       [Edge]             # source, target, type (IMPORT|CALL|TYPE), symbols[], weight
  unresolved:  [UnresolvedEdge]   # phantom imports, broken calls

GraphMetrics:
  pagerank:         {path: float}
  betweenness:      {path: float}
  in_degree:        {path: int}
  out_degree:       {path: int}
  blast_radius:     {path: set[str]}
  sccs:             [set[str]]
  communities:      {path: int}
  modularity:       float
  depth:            {path: int}       # from entry points, ∞ = orphan
  fiedler_value:    float
  spectral_gap:     float
  orphans:          [str]
  orphan_ratio:     float
  phantom_ratio:    float
  glue_deficit:     float             # 1 - internal_node_ratio
  centrality_gini:  float
  clone_pairs:      [(path, path, ncd_score)]
```

Key computations:
- **PageRank**: `PR(v) = (1-d)/|V| + d × Σ PR(u)/out(u)` for u→v. d=0.85, 20 iterations.
- **Blast radius**: BFS on reverse graph from each node. `blast(v) = |reachable(v, reverse(G))| - 1`
- **DAG depth**: BFS from entry points. `depth(v) = max(depth(u)+1)` for u→v. Unreachable = orphan.
- **Fiedler value**: λ₂ of graph Laplacian L = D - A. Via Lanczos iteration for top-k eigenvalues.
- **NCD**: `NCD(x,y) = (C(x·y) - min(C(x),C(y))) / max(C(x),C(y))`. Pre-filtered by: same language AND similar size (±30%) AND MinHash Jaccard estimate > 0.3.
- **Centrality Gini**: Gini coefficient of PageRank distribution. High = hub-dominated.
- **Glue deficit**: `1 - |{v : in_degree(v) > 0 AND out_degree(v) > 0}| / |V|`

### 4.6 IR4: ArchitecturalModel

**Input**: IR3 (file graph), IR2 (file roles).
**Output**: Module-level metrics, inferred layers, violations, architectural patterns.
**Math**: Graph contraction, topological sort, Robert Martin's I/A/D metrics, boundary alignment.
**Time**: O(|modules|²). ~50ms.

Data model:
```
Architecture:
  modules:    [Module]        # path, files, role, cohesion, coupling,
                              #   instability (I), abstractness (A),
                              #   distance_from_main_sequence (D),
                              #   role_consistency, boundary_alignment
  layers:     [Layer]         # depth, modules[]
  violations: [Violation]     # source_module, target_module, type (BACKWARD|SKIP),
                              #   edge_count, symbols[]
  patterns:   ArchPatterns    # is_layered, is_modular, has_god_module,
                              #   hub_and_spoke, layer_count
  health:     ArchHealth      # violation_rate, mean_cohesion, mean_coupling,
                              #   mean_D, boundary_alignment
```

Key computations:
- **Layer inference**: Collapse file graph to module graph → remove back-edges via DFS → topological sort → `layer(m) = max(layer(dep) + 1)`. Back-edges = violations.
- **Module cohesion**: `internal_edges / (|files| × (|files| - 1))`
- **Module coupling**: `external_edges / total_edges`
- **Instability**: `I = Ce / (Ca + Ce)` (Robert Martin)
- **Abstractness**: `A = abstract_symbols / total_symbols`
- **Distance from main sequence**: `D = |A + I - 1|`. D = 0 = ideal balance. Zone of pain: A < 0.3 AND I < 0.3. Zone of uselessness: A > 0.7 AND I > 0.7.
- **Boundary alignment**: Fraction of files in dominant Louvain community per module.
- **Architecture entropy**: `H = -Σ p(module_size) × log₂(p(module_size))`. Low = god module dominates.

### 4.7 IR5t: TemporalModel (parallel with structural spine)

**Input**: Git history.
**Output**: Per-file change history + author data, per-pair co-change metrics, per-module dynamics, codebase dynamics.
**Math**: Time series regression, coefficient of variation, Shannon entropy, association rule mining (lift/confidence), Gini.
**Time**: O(commits × files_per_commit). ~400ms for 5000 commits.

Data model:
```
TemporalModel:
  file_histories:    {path: FileHistory}
    # total_changes, trajectory (dormant|stabilizing|churning|spiking),
    # churn_slope, churn_cv, authors {email: count}, author_entropy,
    # bus_factor (2^H), fix_ratio, refactor_ratio, age, last_modified

  coevolution:       {(path,path): PairDynamics}
    # cochange_count, lift, confidence, has_structural_edge, temporal_coupling

  module_dynamics:   {module: ModuleDynamics}
    # velocity, coordination_cost, knowledge_gini, stability, growth_rate

  codebase_dynamics: CodebaseDynamics
    # commit_frequency[], active_contributors[], growth_rate,
    # entropy_rate (H of commits across modules), global_bus_factor
```

Key computations:
- **Churn trajectory**: Partition history into 4-week windows, count changes per window. Fit linear regression (slope), compute CV. Classify: dormant (≤1 change), stabilizing (negative slope), spiking (positive slope + high CV), churning (high CV), stable.
- **Author entropy**: `H = -Σ p(author) × log₂(p(author))`. Bus factor = `2^H`.
- **Co-change lift**: `lift(A,B) = P(A∩B) / (P(A) × P(B))`. Filter commits > 50 files. Minimum 2 co-occurrences.
- **Fix ratio**: Fraction of commits matching fix/bug/patch/hotfix keywords.
- **Coordination cost**: Mean distinct authors per commit touching a module.
- **Knowledge Gini**: Gini coefficient of per-author commit counts within a module.
- **Entropy rate**: `H = -Σ p(module) × log₂(p(module))` where p = commit fraction. Low = bottleneck.

### 4.8 IR5s: SignalField (fusion layer)

**Input**: All previous IRs.
**Output**: Percentile-normalized signal vectors per file, per module, and global. Composite scores.
**Math**: Percentile normalization, weighted linear combination, signal covariance analysis, health Laplacian.
**Time**: O(n × signals). ~50ms.

Data model:
```
SignalField:
  per_file:   {path: FileSignals}
    # ~25 signals from IR1 through IR5t (see Section 5)
    # + composites: risk_score, wiring_quality

  per_module: {module: ModuleSignals}
    # ~15 signals from IR4 + aggregated file signals
    # + health_score

  global:     GlobalSignals
    # ~10 signals: modularity, fiedler, orphan_ratio, phantom_ratio,
    # glue_deficit, wiring_score, architecture_health, codebase_health
```

Key computations:
- **Percentile normalization**: `percentile(x, values) = |{v ≤ x}| / |values|`. All signals normalized to [0,1].
- **Risk score**: `Σ wᵢ × percentile(signalᵢ)` with weights [pagerank: 0.25, blast: 0.20, cognitive: 0.20, churn: 0.20, 1/bus_factor: 0.15].
- **Wiring quality**: `1 - (0.30 × orphan + 0.25 × stub_ratio + 0.25 × phantom_ratio + 0.20 × broken_call_ratio)`.
- **Module health**: `Σ wᵢ × signalᵢ` across cohesion, 1-coupling, 1-D, alignment, role_consistency, 1-stub_ratio.
- **Health Laplacian**: `Δh(f) = Σ_neighbors (h(neighbor) - h(f))`. Positive = weak link. Negative = hidden strength.
- **Codebase health**: `0.25 × arch_health + 0.25 × wiring + 0.20 × (1-finding_density) + 0.15 × (bus_factor/team_size) + 0.15 × modularity`.

### 4.9 IR6: Insights

**Input**: IR5s.
**Output**: Findings with multi-IR evidence chains, composite scores, prioritized suggestions.
**Math**: Multi-signal predicate evaluation, confidence scoring (margin above threshold), severity amplification.
**Time**: O(findings × signals). ~20ms.

Data model:
```
InsightResult:
  findings:    [Finding]
    # id (stable hash), type, severity, confidence, scope (FILE|MODULE|CODEBASE),
    # targets[], evidence[] (ir_source, signal, value, percentile, description),
    # suggestion, effort (LOW|MEDIUM|HIGH),
    # first_seen, persistence_count, trend, regression (bool)

  composites:  CompositeScores
    # ai_quality, architecture_health, team_risk, codebase_health

  suggestions: [Suggestion]
    # action, priority, effort, impact, targets[], evidence_refs[]
```

### 4.10 Demand-Driven Evaluation

Each signal declares its dependencies. The kernel only computes what the active finders need.

```
Signal Registry:
  "pagerank"      depends_on: ["graph"]           computed_by: compute_pagerank
  "graph"         depends_on: ["file_metrics"]     computed_by: build_graph
  "orphan_ratio"  depends_on: ["graph", "entries"] computed_by: detect_orphans
  "wiring_score"  depends_on: ["orphan_ratio", "stub_ratio", "phantom_ratio", "glue_deficit"]

Kernel resolution:
  1. Collect required signals from active finders
  2. Trace dependencies transitively
  3. Topological sort → execution plan
  4. Execute only the required subgraph
```

Example: `--focus ai-quality` activates OrphanCode + StubCode + PhantomImport + FlatArchitecture finders → needs only IR0, IR1, IR3 (partial) → skips IR2, IR4, IR5t, spectral, NCD, PageRank, Louvain. ~60% less compute.

---

## 5. Signal Catalog

### 5.1 Per-File Signals (~25 signals)

| Signal | Source IR | Dimension | Formula |
|---|---|---|---|
| lines | IR1 | D1 SIZE | Line count |
| function_count | IR1 | D1 SIZE | Function count |
| class_count | IR1 | D1 SIZE | Class count |
| max_nesting | IR1 | D2 SHAPE | Max nesting depth across functions |
| impl_gini | IR1 | D2 SHAPE | Gini coefficient of function body_tokens |
| role | IR2 | D3 NAMING | Classified role (SERVICE, MODEL, etc.) |
| concept_count | IR2 | D3 NAMING | Number of concept clusters |
| concept_entropy | IR2 | D3 NAMING | H of concept weights |
| naming_drift | IR2 | D3 NAMING | 1 - cosine(filename, content concepts) |
| stub_ratio | IR2 | D2 SHAPE | Fraction of functions that are stubs |
| pagerank | IR3 | D4 REFERENCE | PageRank centrality |
| betweenness | IR3 | D4 REFERENCE | Betweenness centrality |
| in_degree | IR3 | D4 REFERENCE | Files importing this |
| out_degree | IR3 | D4 REFERENCE | Files this imports |
| blast_radius_size | IR3 | D4 REFERENCE | Transitive reverse closure size |
| depth | IR3 | D4 REFERENCE | DAG depth from entry point |
| is_orphan | IR3 | D4 REFERENCE | depth = ∞ AND not entry point |
| phantom_import_count | IR3 | D4 REFERENCE | Unresolved imports |
| broken_call_count | IR3 | D4 REFERENCE | Calls to non-existent targets |
| compression_ratio | IR3 | D5 INFORMATION | C(file) / len(file) |
| semantic_coherence | IR3 | D5 INFORMATION | Mean cosine of function token vectors |
| cognitive_load | IR3 | D5 INFORMATION | (concepts × complexity × nesting) × (1+Gini) |
| total_changes | IR5t | D6 CHANGE | Total commits touching file |
| churn_trajectory | IR5t | D6 CHANGE | dormant/stabilizing/churning/spiking |
| bus_factor | IR5t | D7 AUTHORSHIP | 2^(author entropy) |
| author_entropy | IR5t | D7 AUTHORSHIP | H of author contribution distribution |
| fix_ratio | IR5t | D8 INTENT | Fraction of commits classified as fix |

### 5.2 Per-Module Signals (~15 signals)

| Signal | Source | Formula |
|---|---|---|
| cohesion | IR4 | internal_edges / possible_internal_edges |
| coupling | IR4 | external_edges / total_edges |
| instability | IR4 | Ce / (Ca + Ce) |
| abstractness | IR4 | abstract_symbols / total_symbols |
| main_seq_distance | IR4 | \|A + I - 1\| |
| boundary_alignment | IR4 | Files in dominant community / total files |
| layer_violation_count | IR4 | Back-edges into this module |
| role_consistency | IR4 | Max role fraction among files |
| velocity | IR5t | Commits per week touching module |
| coordination_cost | IR5t | Mean authors per commit |
| knowledge_gini | IR5t | Gini of author contributions |
| module_bus_factor | IR5t | Min bus factor of high-centrality files |
| mean_cognitive_load | IR5s | Mean cognitive load of files |
| file_count | IR0 | Number of files |
| health_score | IR5s | Weighted composite |

### 5.3 Global Signals (~10 signals)

| Signal | Source | Formula |
|---|---|---|
| modularity | IR3 | Louvain Q score |
| fiedler_value | IR3 | λ₂ of graph Laplacian |
| cycle_count | IR3 | Number of SCCs with size > 1 |
| centrality_gini | IR3 | Gini of PageRank distribution |
| orphan_ratio | IR3 | Orphan files / total files |
| phantom_ratio | IR3 | Unresolved edges / total edges |
| glue_deficit | IR3 | 1 - internal_node_ratio |
| wiring_score | IR5s | Composite AI quality score |
| architecture_health | IR5s | Composite from IR4 metrics |
| codebase_health | IR5s | Grand composite of all signals |

---

## 6. Finding Catalog

### 6.1 Existing Findings (upgraded with multi-IR evidence)

| Finding | Condition | Severity |
|---|---|---|
| **High Risk Hub** | pagerank P90+ AND blast_radius P90+ AND (cognitive P90+ OR churn P90+) | 1.0 |
| **Hidden Coupling** | cochange_lift ≥ 2.0 AND confidence ≥ 0.5 AND no structural edge | 0.9 |
| **God File** | cognitive_load P90+ AND coherence P20- | 0.8 |
| **Unstable File** | trajectory ∈ {churning, spiking} AND changes above median | 0.7 |
| **Boundary Mismatch** | boundary_alignment < 0.7 AND module has 3+ files | 0.6 |
| **Dead Dependency** | structural edge exists AND cochange = 0 AND 50+ commits | 0.4 |
| **Chronic Problem** | Same finding persists 3+ snapshots | 0.75 (scales) |

### 6.2 New Findings — AI Code Quality

| Finding | Condition | Severity |
|---|---|---|
| **Orphan Code** | in_degree = 0 AND role ≠ ENTRY_POINT AND role ≠ TEST | 0.55 |
| **Hollow Code** | stub_ratio > 0.5 AND impl_gini > 0.6 | 0.71 |
| **Phantom Imports** | phantom_import_count > 0 | 0.65 |
| **Copy-Paste Clone** | NCD(A, B) < 0.3 for file pair | 0.50 |
| **Flat Architecture** | max_depth ≤ 1 AND glue_deficit > 0.5 | 0.60 |
| **Naming Drift** | naming_drift > 0.7 | 0.45 |

### 6.3 New Findings — Social/Team

| Finding | Condition | Severity |
|---|---|---|
| **Knowledge Silo** | bus_factor = 1 AND pagerank P75+ | 0.70 |
| **Conway Violation** | d_author FAR AND d_dependency CLOSE between modules | 0.55 |
| **Review Blindspot** | high centrality AND bus_factor = 1 AND no test file | 0.80 |

### 6.4 New Findings — Architecture

| Finding | Condition | Severity |
|---|---|---|
| **Layer Violation** | backward or skip edge in inferred layer ordering | 0.52 |
| **Zone of Pain** | module A < 0.3 AND I < 0.3 | 0.60 |
| **Architecture Erosion** | violation_rate increasing over 3+ snapshots | 0.65 |

### 6.5 New Findings — Cross-Dimensional

| Finding | Condition | Severity |
|---|---|---|
| **Weak Link** | health Δh > 0.4 (much worse than all neighbors) | 0.75 |
| **Bug Attractor** | fix_ratio > 0.4 AND pagerank P75+ | 0.70 |
| **Accidental Coupling** | d_dependency CLOSE AND d_semantic FAR | 0.50 |

### 6.6 Composite Scores

| Score | Formula | Scale |
|---|---|---|
| **AI Quality** | 1 - (0.25×orphan + 0.25×hollow + 0.20×phantom + 0.15×glue_deficit + 0.15×clone_ratio) | 0-1 |
| **Architecture Health** | Weighted(violation_rate, cohesion, coupling, main_seq_dist, boundary_alignment) | 0-1 |
| **Team Risk** | f(min_bus_factor, knowledge_gini, coordination_cost, Conway correlation) | 0-1 |
| **Codebase Health** | 0.25×arch + 0.25×wiring + 0.20×(1-findings) + 0.15×team + 0.15×modularity | 0-1 |

---

## 7. TensorSnapshot — The Data Contract

The universal output format. Everything downstream (CLI, web UI, CI) consumes this.

```
TensorSnapshot:
  version:     str                  # schema version
  timestamp:   datetime
  commit_sha:  Optional[str]
  project:     str                  # project name/path

  # IR outputs (the tensor)
  files:       {path: FileData}     # all per-file data from IR1-IR5s
  modules:     {path: ModuleData}   # all per-module data from IR4-IR5s
  graph:       GraphData            # edges, centrality, communities, spectral
  architecture: ArchData            # layers, violations, patterns
  temporal:    TemporalData         # co-change pairs, module dynamics
  global:      GlobalData           # all global signals

  # Insights
  findings:    [Finding]
  composites:  CompositeScores
  suggestions: [Suggestion]

  # Metadata
  config:      AnalysisConfig       # which finders ran, thresholds used
  timing:      {ir: duration_ms}    # performance data
```

Serialization: JSON (human-readable, larger) or Protocol Buffers (compact, typed). SQLite for local history (one row per snapshot).

---

## 8. Web UI Specification

### 8.1 Five Views

| View | Purpose | Primary interaction |
|---|---|---|
| **Map** | Codebase topology | Navigate the graph, toggle overlays, switch distance spaces |
| **Timeline** | Temporal trends | Scrub through time, compare snapshots, annotate events |
| **File** | Single-entity deep dive | Read signals, evidence, neighborhood, history |
| **Architecture** | System structure | Explore layers, modules, violations, Martin metrics |
| **PR Risk** | Change impact | See risk per file, blast zone, complexity delta |

### 8.2 View: Map (Codebase Explorer)

**Layout**: Force-directed graph of files as nodes, edges as connections. Louvain communities pulled together.

**Node encoding**:
- Size → LOC (or any SIZE signal)
- Color → health (or any signal via dropdown)
- Border → findings (red ring = has findings)
- Shape → role (circle = service, square = model, diamond = utility, etc.)

**Edge encoding**:
- Thickness → weight (symbol count)
- Color → type (import = gray, call = blue, co-change = orange)
- Dashed → violation or phantom

**Interactions**:
- Hover node → tooltip with key signals + sparklines
- Click node → navigate to File view
- Drag to zoom/pan
- Select module → highlight + show module signals sidebar
- Toggle buttons: show/hide edge types, show/hide orphans, show blast radius of selected file
- **Distance space switcher**: dropdown changes graph layout to show G1/G2/G4/G5/G6 proximity. Switching from "dependency" to "co-change" layout rearranges nodes so co-changing files cluster together — visually reveals hidden coupling.

**Overlays** (toggle on/off):
- Health heatmap (node color gradient)
- Orphan highlight (dimmed or flagged)
- Phantom edges (dashed red)
- Blast radius (highlight all transitively affected nodes from selected file)
- Layer violation edges (red dashed)
- Clone pairs (thick orange between near-duplicates)

### 8.3 View: Timeline (Temporal Explorer)

**Layout**: Horizontal time axis. Stacked signal charts.

**Content**:
- Top: codebase-level signals (health, findings count, modularity, wiring score)
- Middle: selectable per-module signals (velocity, coordination cost, health)
- Bottom: selectable per-file signals (any signal from the catalog)

**Interactions**:
- Click any time point → load that snapshot
- Drag-select range → diff view (what changed between two points)
- Hover → value tooltips
- Annotations layer: mark releases, major PRs, incidents
- Finding lifecycle bars: horizontal bars showing when each finding appeared and resolved

**Key visualization**: **Finding river** — a stacked area chart where each band is a finding type. Width = count. Shows how debt accumulates and is paid down over time.

### 8.4 View: File Deep-Dive

**Layout**: Single file focus with four panels.

**Panel 1 — Signal card**: All ~25 per-file signals displayed as horizontal bars (percentile). Grouped by dimension (SIZE, SHAPE, NAMING, REFERENCE, INFORMATION, CHANGE, AUTHORSHIP, INTENT). Color-coded by severity.

**Panel 2 — Radar chart**: 8 dimensions plotted on a radar/spider chart. One axis per dimension, value = max percentile of signals in that dimension. Immediately shows the file's "shape" in dimension space.

**Panel 3 — Neighborhood**: Mini-graph showing this file's direct neighbors (imports + importers). Nodes colored by health. Edges labeled with symbols. Health Laplacian value shown (Δh = weak link / hidden strength).

**Panel 4 — History**: Time series of key signals for this file. Sparkline per signal. Highlight change points. Show trajectory classification.

**Panel 5 — Findings**: All findings involving this file. Full evidence chains with IR source labels. Suggestions with effort/impact.

### 8.5 View: Architecture

**Layout**: Layered diagram generated from IR4.

**Content**:
- Horizontal layers (Layer 0 at bottom, highest at top)
- Modules as boxes within layers, sized by file count
- Edges between modules (thickness = edge count)
- Violation edges as red dashed lines crossing layers
- Each module box shows: health bar, I/A/D values, role label

**Interactions**:
- Click module → expand to show files within
- Click violation → show which imports cause it
- Toggle: show Martin's main sequence plot (A vs I scatter, each point = module)
- Toggle: show boundary alignment (color modules by alignment score)

**Martin's Main Sequence Plot** (sub-view):
- Scatter plot: x = Instability, y = Abstractness
- Diagonal line = main sequence (A + I = 1)
- Distance from line = D value
- Green zone near the line, red zones in corners (pain / uselessness)
- Each point = a module, sized by file count

### 8.6 View: PR Risk

**Layout**: Triggered from CI or by selecting a branch diff.

**Content**:
- Top: aggregate PR risk score (1-10 scale with color)
- File table: changed files ranked by risk contribution, with signal breakdown
- Blast zone: mini-graph showing changed files + their transitive dependents, colored by affected/not
- Complexity delta: bar chart showing Δ cognitive_load per file
- Finding impact: new findings introduced, existing findings resolved, regressions
- Recommendation: text summary of highest-risk aspects

### 8.7 Data Flow: Web UI

```
Browser (SPA)
    │
    │ REST API calls
    ▼
┌──────────────┐
│ API Server   │
│ (FastAPI)    │
│              │
│ Endpoints:   │
│  GET /snapshots                  → list of snapshots
│  GET /snapshots/:id              → full TensorSnapshot
│  GET /snapshots/:id/file/:path   → single file data
│  GET /snapshots/:id/graph        → graph data (nodes + edges)
│  GET /snapshots/:id/findings     → findings list
│  GET /diff/:id1/:id2             → delta between snapshots
│  GET /history/:path              → time series for one file
│  GET /pr-risk                    → risk analysis for current diff
│              │
│ Reads from:  │
│  SQLite      │ (local mode)
│  PostgreSQL  │ (hosted mode)
└──────────────┘
```

The SPA is static (can be served from CDN, embedded in CLI, or hosted). All data comes from API endpoints. The API server can be the same process as `shannon-insight serve` (local mode) or a standalone deployment (hosted mode).

---

## 9. Deployment Models

### 9.1 Model A: Local Developer Server

```bash
$ pip install shannon-insight
$ shannon-insight serve -C ./my-project

  Shannon Insight running at http://localhost:8420
  Analyzing 342 files...
  Analysis complete. Open browser to explore.
```

- Engine + API server + frontend all in one process
- Data stored in `.shannon/history.db` (SQLite)
- No network, no accounts, no data leaves the machine
- Auto-reanalyzes on file changes (filesystem watcher)
- **Target audience**: individual developer exploring their own codebase

### 9.2 Model B: CI Integration

```yaml
# .github/workflows/shannon.yml
name: Shannon Insight
on: [pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - uses: shannon-insight/action@v2
        with:
          fail-on: high
          comment: true
          upload-to: https://insight.mycompany.com  # optional
```

- Runs full analysis on every PR
- Posts risk score + summary as PR comment
- Optionally uploads snapshot to team dashboard
- `fail-on: high` blocks merge if high-severity findings
- **Target audience**: development teams wanting quality gates

### 9.3 Model C: Hosted Platform (SaaS)

- Connect GitHub/GitLab repo via OAuth
- Automatic analysis on push/PR
- Persistent dashboard with full history
- Team management, notification settings
- Org-level cross-repo insights
- **Target audience**: engineering organizations, platform teams
- **Business model**: free for open source, paid for private repos

### 9.4 Migration Path

```
Phase 1: Local server
  - Add TensorSnapshot serialization to existing engine
  - Build minimal web UI (Map + File views)
  - Add `shannon-insight serve` command
  - Keep CLI working as-is

Phase 2: Full web UI
  - Add Timeline, Architecture, PR Risk views
  - Add all new finders (AI quality, social, architecture)
  - Add demand-driven evaluation
  - Add IR2 (semantic) and IR4 (architecture) layers

Phase 3: CI Integration
  - GitHub Action wrapper
  - PR comment bot
  - Snapshot upload endpoint

Phase 4: Hosted platform
  - API server with PostgreSQL
  - Auth + team management
  - Cross-repo dashboards
  - Billing
```

---

## 10. Novel Innovations

Capabilities not found in any existing tool:

### 10.1 Health Scalar Field with Laplacian Diffusion

Treat health as a field over the dependency graph. Compute its Laplacian: `Δh(f) = Σ_neighbors (h(neighbor) - h(f))`. Files with high Δh are **weak links** — unhealthy in a healthy neighborhood. Files with negative Δh are **hidden strengths**. Simulate health diffusion to find equilibrium — deviation from equilibrium = architectural mismatch.

### 10.2 Systematic Finding Discovery via Distance Space Disagreements

15 pairs of 6 distance spaces. For each pair, find entities where distances disagree. Each disagreement is a potential finding. This is a finding discovery engine, not a hand-crafted rule set. Unexplored pairs may contain findings nobody has named yet.

### 10.3 AI Code Quality Detection

First tool to systematically detect AI-generated code problems: orphans (written but never imported), stubs (signatures without bodies), phantoms (references to non-existent modules), flat architecture (no composition), copy-paste clones (NCD), naming drift. Combined into a single wiring score.

### 10.4 Temporal Tensor Decomposition

CP decomposition of the files × signals × time tensor reveals **evolution archetypes** — recurring patterns like "files becoming more complex AND more central AND less maintained." Archetypes are discovered, not predefined.

### 10.5 MDL Architecture Fit

Minimum Description Length measures how well declared architecture explains actual code: `fit = L(deviations|model) / L(code)`. Single number for "is our architecture still real?"

### 10.6 Mutual Information Between Structure and Change

`I(structure; change)` captures whether changes respect module boundaries. High = disciplined. Low = eroded architecture. Single-number architectural health metric.

### 10.7 Zipf Deviation for AI Detection

Natural codebases follow power-law file size distribution. AI-generated codebases don't. KL divergence from fitted power law distinguishes human from AI code at the codebase level.

### 10.8 Interactive Distance Space Switching

Web UI lets users switch the graph layout between 6 distance spaces. Switching from "dependency" to "co-change" visually rearranges files so co-changing clusters appear — hidden coupling becomes literally visible.

---

## 11. Document Index

| Document | Content | Location |
|---|---|---|
| This spec | Complete product and engineering specification | `docs/spec-v2.md` |
| Framework | Theoretical foundation — dimensions, scales, tensor, distances | `docs/framework.md` |
| Mathematics | Formulas and algorithms at every level | `docs/mathematics.md` |
| IR Specification | Data models for each IR, temporal operators, persistence | `docs/ir-spec.md` |
| Feature Brainstorm | All feature ideas with priority matrix | `docs/brainstorm-v2.md` |
| Walkthrough | Concrete example tracing through the entire pipeline | `docs/walkthrough.md` |
