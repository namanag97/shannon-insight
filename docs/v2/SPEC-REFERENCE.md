# Shannon Insight v2 — Consolidated Spec Reference

> **This is the single reference document for implementing v2.**
> It consolidates architecture, signals, finders, composites, formulas, edge cases, and the phase plan.
> For deep-dive details on any module, see the corresponding `modules/` or `registry/` doc.

---

## 1. Architecture

### Data Flow (one run)

```
FILES ON DISK ──→ scanning/ (IR0+IR1) ──→ semantics/ (IR2) ──┐
                  FileMetrics[]            FileSemantics[]     │
                  signals #1-7             signals #8-13       │
                                                               ├──→ graph/ (IR3)
GIT HISTORY ───→ temporal/ (IR5t) ─────────────────────────────┘    CodeGraph + GraphMetrics
                  GitHistory, ChurnSeries                           signals #14-26, #52-59
                  signals #27-34                                    │
                                                                    ▼
                                                              architecture/ (IR4)
                                                              Architecture, Module, Layer
                                                              signals #37-44, #50
                                                                    │
                                                                    ▼
                                                              signals/ (IR5s) ← reads ALL
                                                              SignalField (unified)
                                                              composites #35-36, #45-51, #60-62
                                                              health Laplacian
                                                                    │
                                                                    ▼
                                                              insights/ (IR6)
                                                              22 finders → Finding[]
                                                                    │
                                                         ┌──────────┼──────────┐
                                                         ▼          ▼          ▼
                                                    persistence/  cli/      web/ (future)
```

### Parallelism

```
STRUCTURAL SPINE              TEMPORAL SPINE
scanning/ ──→ semantics/      temporal/ (reads git directly)
         ──→ graph/ ◄─────────── co-change enrichment (merges here)
         ──→ architecture/
         ──→ signals/ ◄──────── reads temporal signals
         ──→ insights/
```

Zero data dependency between spines until graph/ merges them.

### Blackboard Pattern

```
AnalysisStore (shared mutable state)
├── file_metrics: List[FileMetrics]       ← set by kernel (input)
├── file_syntax: Dict[str, FileSyntax]    ← written by Scanner (Phase 1)
├── structural: CodebaseAnalysis          ← written by StructuralAnalyzer
├── git_history: GitHistory               ← written by TemporalAnalyzer
├── cochange: CoChangeMatrix              ← written by TemporalAnalyzer
├── churn: Dict[str, ChurnSeries]         ← written by TemporalAnalyzer
├── spectral: SpectralSummary             ← written by SpectralAnalyzer
├── semantics: Dict[str, FileSemantics]   ← written by SemanticAnalyzer (Phase 2)
├── roles: Dict[str, str]                 ← written by SemanticAnalyzer (Phase 2, convenience alias)
├── clone_pairs: List[ClonePair]          ← written by StructuralAnalyzer (Phase 3)
├── author_distances: List[AuthorDistance] ← written by StructuralAnalyzer (Phase 3)
├── architecture: Architecture            ← written by ArchitectureAnalyzer (Phase 4)
└── signal_field: SignalField             ← written by SignalFusionAnalyzer (Phase 5, LAST)

Kernel: topo-sort analyzers by requires/provides, run in order.
        SignalFusionAnalyzer has run_last=True, bypasses topo sort.
Finders: read store (never write), return List[Finding].
         Skip gracefully if required signals unavailable.
```

---

## 2. Signal Catalog (62 signals)

### Mathematical Foundations

**Gini coefficient** (used for impl_gini, centrality_gini, knowledge_gini):
```
G = (2 × Σᵢ i × xᵢ) / (n × Σ xᵢ) - (n + 1) / n
where xᵢ sorted ascending, i is 1-indexed, n = count. G=0 equal, G=1 max inequality.
```

**Percentile** (canonical form, used everywhere):
```
pctl(signal, f) = |{v ∈ all_files : signal(v) ≤ signal(f)}| / |all_files|
```

**Shannon entropy**:
```
H = -Σ p(x) × log₂(p(x))
```

### Per-File Signals (S4 scale, 36 signals)

#### IR1 Scanning (#1-7)

| # | Signal | Dim | Type | Range | High = | Threshold | Source |
|---|--------|-----|------|-------|--------|-----------|--------|
| 1 | `lines` | D1 | int | [0,∞) | larger | >500 | line count |
| 2 | `function_count` | D1 | int | [0,∞) | complex | >30 | function/method count |
| 3 | `class_count` | D1 | int | [0,∞) | more classes | — | class count |
| 4 | `max_nesting` | D2 | int | [0,∞) | harder to read | >4 | max AST nesting depth |
| 5 | `impl_gini` | D2 | float | [0,1] | uneven (AI sign.) | >0.6 | Gini of function body_token counts |
| 6 | `stub_ratio` | D2 | float | [0,1] | incomplete | >0.5 | mean(stub_score) per function |
| 7 | `import_count` | D4 | int | [0,∞) | more deps | — | import declaration count |

**stub_score(f)** = `1 - min(1, body_tokens / (signature_tokens × 3))`. Hard classify: `body_tokens < 5` OR body matches `pass|...|return None`.

#### IR2 Semantics (#8-13)

| # | Signal | Dim | Type | Range | High = | Threshold | Source |
|---|--------|-----|------|-------|--------|-----------|--------|
| 8 | `role` | D3 | enum | Role(12) | — | — | decision tree on structure |
| 9 | `concept_count` | D3 | int | [0,∞) | less focused | — | TF-IDF + Louvain clusters |
| 10 | `concept_entropy` | D3 | float | [0,∞) | god file risk | >1.5 | H(concept weights) |
| 11 | `naming_drift` | D3 | float | [0,1] | filename misleads | >0.7 | 1 - cos(filename_tfidf, content_tfidf) |
| 12 | `todo_density` | D3 | float | [0,∞) | incomplete markers | >0.05 | (TODO+FIXME+HACK) / lines |
| 13 | `docstring_coverage` | D3 | float | [0,1] | better docs (GOOD) | — | documented / total public symbols |

**Role values**: MODEL, SERVICE, UTILITY, CONFIG, TEST, CLI, INTERFACE, EXCEPTION, CONSTANT, ENTRY_POINT, MIGRATION, UNKNOWN

**Concept extraction tiers**:
- 10+ functions AND 20+ identifiers: full TF-IDF + Louvain
- 3-9 functions: simplified keyword frequency clustering
- <3 functions: single concept, entropy = 0.0

**Generic filename handling**: `utils.py`, `helpers.py`, `common.py`, `misc.py`, `shared.py`, `base.py`, `core.py`, `__init__.py` → naming_drift = 0.0

#### IR3 Graph (#14-26)

| # | Signal | Dim | Type | Range | High = | Formula |
|---|--------|-----|------|-------|--------|---------|
| 14 | `pagerank` | D4 | float | [0,1] | central (risk) | PR(v) = (1-d)/N + d×Σ PR(u)/out(u), d=0.85 |
| 15 | `betweenness` | D4 | float | [0,1] | bridge (fragile) | Brandes' algorithm |
| 16 | `in_degree` | D4 | int | [0,∞) | more dependents | count of importers |
| 17 | `out_degree` | D4 | int | [0,∞) | more deps | count of imports |
| 18 | `blast_radius_size` | D4 | int | [0,n-1] | wider impact | BFS on reverse graph |
| 19 | `depth` | D4 | int | [0,∞)∪{-1} | deeper in chain | BFS from entry points, -1=unreachable |
| 20 | `is_orphan` | D4 | bool | {0,1} | unused | in_degree=0 AND role∉{ENTRY_POINT,TEST} |
| 21 | `phantom_import_count` | D4 | int | [0,∞) | broken refs | unresolved non-external imports |
| 22 | `broken_call_count` | D4 | int | [0,∞) | broken calls | **defaults to 0 until CALL edges exist** |
| 23 | `community` | D4 | int | [0,k) | — | Louvain assignment ID |
| 24 | `compression_ratio` | D5 | float | [0,1] | repetitive | len(zlib.compress(x))/len(x) |
| 25 | `semantic_coherence` | D5 | float | [0,1] | focused (GOOD) | mean pairwise cosine of function TF-IDF |
| 26 | `cognitive_load` | D5 | float | [0,∞) | hard to understand | (concepts×complexity×e^(nesting/5))×(1+G) |

**DAG depth: zero entry point handling**:
1. If no ENTRY_POINT files: use `__init__.py` files as synthetic roots
2. If still none: use files with in_degree=0 AND out_degree>0
3. If still none: set depth=0 for all, skip depth-based signals

#### IR5t Temporal (#27-34)

| # | Signal | Dim | Type | Range | High = | Formula |
|---|--------|-----|------|-------|--------|---------|
| 27 | `total_changes` | D6 | int | [0,∞) | volatile | commit count touching file |
| 28 | `churn_trajectory` | D6 | enum | Trajectory | — | DORMANT/STABILIZING/STABLE/CHURNING/SPIKING |
| 29 | `churn_slope` | D6 | float | (-∞,∞) | increasing churn | linear regression slope of 4-week windows |
| 30 | `churn_cv` | D6 | float | [0,∞) | erratic | coefficient of variation, threshold >1.0 |
| 31 | `bus_factor` | D7 | float | [1,∞) | more authors (GOOD) | 2^H where H = author entropy |
| 32 | `author_entropy` | D7 | float | [0,∞) | distributed (GOOD) | H = -Σ p(a)×log₂(p(a)) |
| 33 | `fix_ratio` | D8 | float | [0,1] | bug-prone | fix commits / total commits |
| 34 | `refactor_ratio` | D8 | float | [0,1] | maintained (GOOD) | refactor commits / total commits |

**Trajectory classification** (v2 canonical thresholds):
```
if Σ changes ≤ 1:                                    DORMANT
elif velocity < -threshold AND CV < 0.5:              STABILIZING
elif velocity > threshold AND CV > 0.5:               SPIKING
elif CV > 0.5:                                        CHURNING
else:                                                 STABLE
```

#### Per-File Composites (#35-36)

| # | Signal | Range | Polarity | Formula |
|---|--------|-------|----------|---------|
| 35 | `risk_score` | [0,1] | high=BAD | 0.25×pctl(pagerank) + 0.20×pctl(blast_radius_size) + 0.20×pctl(cognitive_load) + 0.20×instability_factor + 0.15×(1-bus_factor/max_bf) |
| 36 | `wiring_quality` | [0,1] | high=GOOD | 1-(0.30×is_orphan + 0.25×stub_ratio + 0.25×(phantoms/imports) + 0.20×(broken_calls/total_calls)) |

`instability_factor` = 1.0 if trajectory∈{CHURNING,SPIKING}, else 0.3

### Per-Module Signals (S5 scale, 15 signals)

| # | Signal | Dim | Formula |
|---|--------|-----|---------|
| 37 | `cohesion` | D4 | internal_edges / (file_count × (file_count-1)) |
| 38 | `coupling` | D4 | external_edges / (internal + external) |
| 39 | `instability` | D4 | Ce / (Ca+Ce). **None if Ca+Ce=0** |
| 40 | `abstractness` | D4 | abstract_symbols / total_symbols |
| 41 | `main_seq_distance` | D4 | \|A + I - 1\|. Skip if I=None |
| 42 | `boundary_alignment` | D4 | files_in_dominant_community / total_files |
| 43 | `layer_violation_count` | D4 | backward + skip edges into module |
| 44 | `role_consistency` | D3 | max(role_count) / total_files |
| 45 | `velocity` | D6 | commits/week in **last 90 days** (configurable) |
| 46 | `coordination_cost` | D7 | mean(distinct_authors_per_commit) |
| 47 | `knowledge_gini` | D7 | Gini of per-author commit counts. >0.7=silo |
| 48 | `module_bus_factor` | D7 | min(bus_factor) across high-centrality files |
| 49 | `mean_cognitive_load` | D5 | mean(cognitive_load) across files |
| 50 | `file_count` | D1 | source files in module |
| 51 | `health_score` | comp | 0.20×cohesion + 0.15×(1-coupling) + 0.20×(1-main_seq_dist) + 0.15×boundary + 0.15×role_consistency + 0.15×(1-mean_stub_ratio) |

**Instability edge case**: If Ca+Ce=0 (isolated module), set instability=None. Skip main_seq_distance. ZONE_OF_PAIN must check instability is not None.

### Global Signals (S6 scale, 11 signals)

| # | Signal | Formula |
|---|--------|---------|
| 52 | `modularity` | Louvain Q = (1/2m)Σ[A_ij - k_i×k_j/(2m)]δ(c_i,c_j). >0.3=good |
| 53 | `fiedler_value` | λ₂ of Laplacian L=D-A. 0=disconnected |
| 54 | `spectral_gap` | λ₂/λ₃. Large=clear cut |
| 55 | `cycle_count` | SCCs with >1 node |
| 56 | `centrality_gini` | Gini of pagerank distribution |
| 57 | `orphan_ratio` | count(is_orphan) / total_files |
| 58 | `phantom_ratio` | unresolved_edges / total_edges |
| 59 | `glue_deficit` | 1 - \|glue_nodes\| / \|V\| |
| 60 | `wiring_score` | 1-(0.25×orphan_ratio + 0.25×phantom_ratio + 0.20×glue_deficit + 0.15×mean(stub_ratio) + 0.15×clone_ratio) |
| 61 | `architecture_health` | 0.25×(1-violation_rate) + 0.20×mean(cohesion) + 0.20×(1-mean(coupling)) + 0.20×(1-mean(main_seq_dist)) + 0.15×mean(boundary) |
| 62 | `codebase_health` | 0.30×arch_health + 0.30×wiring_score + 0.20×(global_bf/team_size) + 0.20×modularity |

**team_risk** (unnumbered, display-only): 1-(0.30×(min_bf_critical/3.0) + 0.25×(1-max(knowledge_gini)) + 0.25×(1-mean(coord_cost)/5.0) + 0.20×conway_alignment). bus_factor∈[1,∞), /3.0 caps contribution. conway_alignment = 1 - mean(author_distance) across structurally-coupled module pairs.

### Health Laplacian

```
raw_risk(f) = 0.25×pagerank/max_pr + 0.20×blast/max_blast + 0.20×cognitive/max_cog
            + 0.20×instability_factor + 0.15×(1-bus_factor/max_bf)

Δh(f) = raw_risk(f) - mean(raw_risk(n) for n in neighbors(f))
```

Uses **raw weighted sum**, NOT percentile-based risk_score (avoids Laplacian-on-uniform circularity).
Δh > 0.4 triggers WEAK_LINK finder.

---

## 3. Finder Catalog (22 finders)

**Severity values are hand-tuned rank separators, not calibrated measurements.**

**Finding grouping**: FILE-scope findings of same type are grouped into one Finding with multiple files. Max 3 grouped findings per type. Implemented in ranking.py.

### Existing (7, upgraded in v2)

| Finder | Scope | Sev | Condition | Key signals |
|--------|-------|-----|-----------|-------------|
| HIGH_RISK_HUB | FILE | 1.0 | pctl(pagerank)>0.90 AND pctl(blast_radius_size)>0.90 AND (pctl(cognitive_load)>0.90 OR trajectory∈{CHURNING,SPIKING}) | #14,18,26,28 |
| HIDDEN_COUPLING | FILE_PAIR | 0.9 | lift≥2.0 AND confidence≥0.5 AND no structural edge | cochange, graph |
| GOD_FILE | FILE | 0.8 | pctl(cognitive_load)>0.90 AND pctl(semantic_coherence)<0.20 | #26,25 |
| UNSTABLE_FILE | FILE | 0.7 | trajectory∈{CHURNING,SPIKING} AND total_changes>median | #28,27 |
| BOUNDARY_MISMATCH | MODULE | 0.6 | boundary_alignment<0.7 AND file_count≥3 | #42,50 |
| DEAD_DEPENDENCY | FILE_PAIR | 0.4 | structural edge AND cochange_count=0 AND both have 50+ commits | graph, cochange |
| CHRONIC_PROBLEM | wraps | 1.25× | same finding persists 3+ snapshots | finding lifecycle |

### New: AI Code Quality (6)

| Finder | Scope | Sev | Condition |
|--------|-------|-----|-----------|
| ORPHAN_CODE | FILE | 0.55 | is_orphan=true |
| HOLLOW_CODE | FILE | 0.71 | stub_ratio>0.5 AND impl_gini>0.6 |
| PHANTOM_IMPORTS | FILE | 0.65 | phantom_import_count>0 |
| COPY_PASTE_CLONE | FILE_PAIR | 0.50 | NCD(A,B)<0.3 |
| FLAT_ARCHITECTURE | CODEBASE | 0.60 | max(depth)≤1 AND glue_deficit>0.5 |
| NAMING_DRIFT | FILE | 0.45 | naming_drift>0.7 |

### New: Social/Team (3)

| Finder | Scope | Sev | Condition |
|--------|-------|-----|-----------|
| KNOWLEDGE_SILO | FILE | 0.70 | bus_factor≤1.5 AND pctl(pagerank)>0.75 |
| CONWAY_VIOLATION | MOD_PAIR | 0.55 | d_author(M1,M2)>0.8 AND structural_coupling>0.3 |
| REVIEW_BLINDSPOT | FILE | 0.80 | pctl(pagerank)>0.75 AND bus_factor≤1.5 AND no_test_file |

**Test detection**: Use role=TEST classification, not filename patterns. If any TEST file shares base name → test exists.
**Single-author projects**: Skip G5 computation if distinct_authors < 3. CONWAY_VIOLATION, KNOWLEDGE_SILO gracefully degrade.

### New: Architecture (3)

| Finder | Scope | Sev | Condition |
|--------|-------|-----|-----------|
| LAYER_VIOLATION | MOD_PAIR | 0.52 | backward or skip edge in inferred layers |
| ZONE_OF_PAIN | MODULE | 0.60 | abstractness<0.3 AND instability<0.3 (both must be non-None) |
| ARCHITECTURE_EROSION | CODEBASE | 0.65 | violation_rate increasing over 3+ snapshots |

**Flat projects** (all files in one directory, module_count < 2): Skip architecture analysis entirely. Set architecture=None. All architecture finders gracefully skip.

**Module cycles**: If most modules are in one SCC, layer_violation_count=0 (false negative). Consider adding module_cycle_count to global signals as a separate check.

### New: Cross-Dimensional (3)

| Finder | Scope | Sev | Condition |
|--------|-------|-----|-----------|
| WEAK_LINK | FILE | 0.75 | Δh(f)>0.4 (health Laplacian, raw_risk) |
| BUG_ATTRACTOR | FILE | 0.70 | fix_ratio>0.4 AND pctl(pagerank)>0.75 |
| ACCIDENTAL_COUPLING | FILE_PAIR | 0.50 | structural edge AND concept_overlap(A,B) < 0.2 (Jaccard, NOT cosine) |

**ACCIDENTAL_COUPLING** uses `concept_overlap = |concepts(A)∩concepts(B)| / |concepts(A)∪concepts(B)|` from Phase 2 concept clusters. NOT the per-file semantic_coherence signal.

---

## 4. Distance Spaces (6)

| # | Space | Distance | Source | Status |
|---|-------|----------|--------|--------|
| G1 | Dependency | shortest path in import graph | IR3 | Exists |
| G2 | Call | min call chain length | IR3 CALL edges | Future |
| G3 | Type | 1 - type overlap ratio | IR3 TYPE_FLOW | Future |
| G4 | Co-change | 1 / (lift + ε) | IR5t | Exists |
| G5 | Author | 1 - weighted Jaccard of author dists | IR5t | Phase 3 |
| G6 | Semantic | 1 - cosine(tfidf_A, tfidf_B) | IR2 | Phase 2+ |

**Disagreement principle**: Finding = close in one space, far in another.

| Close in | Far in | Finding |
|----------|--------|---------|
| G4 | G1 | HIDDEN_COUPLING |
| G1 | G4 | DEAD_DEPENDENCY |
| G1 | G6 | ACCIDENTAL_COUPLING |
| G5 (author) | G1 (dep) | CONWAY_VIOLATION |

---

## 5. Normalization Tiers

| Files | Tier | Strategy |
|-------|------|----------|
| < 15 | ABSOLUTE | No percentiles. Use absolute thresholds only. Composites NOT computed. |
| 15-50 | BAYESIAN | Bayesian percentiles (initially flat priors = standard percentile) |
| 50+ | FULL | Standard percentile normalization. Full composites. |

---

## 6. Core Data Models

### Current → v2 Evolution

```
FileMetrics (v1)           →  FileMetrics + FunctionDef/ClassDef/ImportDecl fields (Phase 1)
Primitives (5 floats)      →  FileSignals (36 fields) via SignalField (Phase 5)
AnalysisStore (6 slots)    →  AnalysisStore (11 slots + signal_field) (Phase 5)
Snapshot (schema v1)       →  TensorSnapshot (schema v2) (Phase 7)
CodebaseAnalysis           →  CodebaseAnalysis + Architecture (Phase 4)
```

### SignalField (Phase 5, the unified container)

```python
@dataclass
class SignalField:
    per_file: Dict[str, FileSignals]       # ~36 signals per file
    per_module: Dict[str, ModuleSignals]   # ~15 signals per module
    global_signals: GlobalSignals           # ~11 codebase signals
    tier: str                               # ABSOLUTE | BAYESIAN | FULL
```

### Key Protocol Interfaces

```python
class Analyzer(Protocol):
    name: str
    requires: Set[str]      # what must be in store.available
    provides: Set[str]      # what this analyzer adds to store.available
    def analyze(self, store: AnalysisStore) -> None: ...

class Finder(Protocol):
    name: str
    requires: Set[str]
    def find(self, store: AnalysisStore) -> List[Finding]: ...
```

---

## 7. Phase Plan

```
Phase 0  Baseline audit         0 code changes    ~1 week
Phase 1  tree-sitter parsing    ~15 new files     ~3 weeks
Phase 2  semantics/ package     ~9 new files      ~2 weeks
Phase 3  Graph enrichment       ~2 new files      ~1.5 weeks
Phase 4  architecture/ package  ~5 new files      ~2 weeks
Phase 5  Signal fusion          ~5 new files      ~2 weeks
Phase 6  New finders            ~15 new files     ~2.5 weeks
Phase 7  Persistence v2         ~2 new files      ~2 weeks
                                                  ≈16 weeks total
```

### Phase Dependency Chain

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7
                                                                    ↑
                                                          batches can overlap
```

### What Each Phase Unlocks

| Phase | New signals | New finders | Key deliverable |
|-------|-------------|-------------|-----------------|
| 0 | — | — | Gap analysis, verified baseline |
| 1 | #1-7 upgraded (accurate AST) | — | tree-sitter parser, FunctionDef.calls[] |
| 2 | #8-13 (role, concepts, drift) | — | semantics/ package |
| 3 | #19-21, #54, #56-59, G5, clones | — | depth, orphans, clones, author distance |
| 4 | #37-44, #50 | — | architecture/ package, layers, Martin metrics |
| 5 | #35-36, #45-49, #51, #60-62, Δh | — | SignalField, composites, health Laplacian |
| 6 | — | 15 new (3 batches) | ORPHAN, HOLLOW, PHANTOM, CLONE, FLAT, NAMING, LAYER, ZONE, KNOWLEDGE, CONWAY, REVIEW, WEAK, BUG, ACCIDENTAL, + BOUNDARY upgrade |
| 7 | Kind 2 temporal | CHRONIC_PROBLEM upgrade, ARCHITECTURE_EROSION | TensorSnapshot, finding lifecycle |

### What v2 Explicitly Defers

| Feature | Reason | Status |
|---------|--------|--------|
| CALL edges (G2) | Cross-function resolution is hard, language-specific | Future Phase 3b |
| TYPE_FLOW edges (G3) | Requires type inference | Future |
| CP/Tucker tensor decomposition | Needs Kind 3 temporal (expensive reconstruction) | Research |
| Kind 3 temporal (historical reconstruction) | Re-run pipeline at past commits, O(commits×files) | Research |
| Web UI | Separate project | Future |
| Temporal operators on arbitrary signals | Infrastructure exists (signal_history), operators not implemented | Incremental |
| Calibrated weights (logistic regression) | Needs Technical Debt Dataset validation | Post-validation |

---

## 8. Edge Cases & Decisions

### Project Characteristics

| Characteristic | Handling |
|----------------|----------|
| **< 15 files** | ABSOLUTE tier. No percentiles, no composites. Show raw signals. |
| **No git history** | temporal/ skipped. Signals #27-34 = defaults. Finders requiring temporal skip. |
| **Single author** | Skip G5 author distance. CONWAY_VIOLATION, KNOWLEDGE_SILO degrade. |
| **Library (no entry points)** | Synthetic entry points: __init__.py → root importers → depth=0 fallback |
| **Flat project (1 directory)** | architecture=None if module_count<2. Architecture finders skip. |
| **Monorepo** | Detect workspaces. Each workspace = separate analysis root. |
| **Circular module deps** | Merge into single layer. layer_violation_count=0. Log warning. |

### Signal Edge Cases

| Signal | Edge case | Decision |
|--------|-----------|----------|
| `instability` | Ca+Ce=0 (isolated module) | Set to None, skip main_seq_distance |
| `broken_call_count` | No CALL edges yet | Defaults to 0 |
| `naming_drift` | Generic filename (utils.py) | Set to 0.0 |
| `concept_entropy` | < 3 functions in file | Set to 0.0, single concept |
| `bus_factor` | Single commit file | Set to 1.0 |
| `velocity` | No commits in 90-day window | Set to 0.0 |
| `depth` | No entry points found | Fallback chain (see §2 above) |

### Finder Edge Cases

| Finder | Edge case | Decision |
|--------|-----------|----------|
| ORPHAN_CODE | Entry points with in_degree=0 | Excluded by role check |
| FLAT_ARCHITECTURE | Tiny projects (< 10 files) | max_depth check still valid |
| ACCIDENTAL_COUPLING | No concept data | Finder skips (graceful degradation) |
| ZONE_OF_PAIN | instability=None | Finder skips |
| ARCHITECTURE_EROSION | < 3 snapshots | Finder skips |
| Finding explosion | 50+ orphans | Grouped into 1 finding with file list |

---

## 9. Louvain Gain Formula (Reference)

```
Standard Louvain modularity gain for moving node i to community C:

ΔQ = [k_{i,in} / 2m] - [Σ_tot × k_i / (2m)²]

where:
  k_{i,in}  = sum of edge weights from i to nodes in C
  Σ_tot     = sum of degrees of nodes in C (before adding i)
  k_i       = degree of node i
  2m        = sum of all edge weights in graph
  (2m)²     = 4m² (the square of 2m, NOT 2×m²)

Net gain = gain_of_adding_to_target - cost_of_removing_from_current
```

---

## 10. File Layout After v2

```
src/shannon_insight/
├── scanning/                  IR0+IR1 (Phase 1: tree-sitter)
│   ├── models.py              FileMetrics + FunctionDef/ClassDef/ImportDecl
│   ├── treesitter_parser.py   NEW: core parser
│   ├── queries/               NEW: per-language query modules
│   ├── normalizer.py          NEW: captures → FileSyntax
│   ├── factory.py             routes to tree-sitter or regex fallback
│   └── ...existing...
├── semantics/                 IR2 (Phase 2: NEW package)
│   ├── models.py              FileSemantics, Role, Concept
│   ├── analyzer.py            SemanticAnalyzer
│   ├── roles.py               role decision tree
│   ├── concepts.py            TF-IDF + Louvain
│   ├── naming.py              naming drift
│   └── completeness.py        todo_density, docstring_coverage
├── graph/                     IR3 (Phase 3: enriched)
│   ├── models.py              + ClonePair, AuthorDistance, depth, orphan fields
│   ├── algorithms.py          + compute_dag_depth, compute_orphans, centrality_gini
│   ├── clone_detection.py     NEW: MinHash + NCD
│   ├── distance.py            NEW: G5 author distance
│   └── ...existing...
├── architecture/              IR4 (Phase 4: NEW package)
│   ├── models.py              Architecture, Module, Layer, Violation
│   ├── analyzer.py            ArchitectureAnalyzer
│   ├── modules.py             module detection
│   ├── metrics.py             Martin metrics, abstractness
│   └── layers.py              topological sort, violations
├── signals/                   IR5s (Phase 5: rewritten)
│   ├── models.py              FileSignals, ModuleSignals, GlobalSignals, SignalField
│   ├── fusion.py              NEW: SignalFusion (collects all signals)
│   ├── normalization.py       NEW: tiered percentile
│   ├── composites.py          NEW: all composite formulas
│   ├── health_laplacian.py    NEW: Δh computation
│   ├── analyzer.py            NEW: SignalFusionAnalyzer (run_last=True)
│   └── ...existing plugins preserved...
├── insights/                  IR6 (Phase 6: 15 new finders)
│   ├── finders/               + orphan, hollow, phantom, clone, flat, naming,
│   │                            layer, zone, knowledge, conway, review,
│   │                            weak, bug, accidental
│   ├── ranking.py             + finding grouping logic
│   └── ...existing...
├── temporal/                  IR5t (minor changes)
├── persistence/               Phase 7: TensorSnapshot
│   ├── models.py              TensorSnapshot (schema v2)
│   └── ...enhanced...
├── cli/                       unchanged commands + serve (future)
└── math/                      unchanged
```

---

*This document is the consolidated reference. For implementation details on any module, see `modules/<package>/README.md`. For the full signal/finder definitions, see `registry/`. For phase-by-phase implementation plans with acceptance criteria, see `phases/`.*
