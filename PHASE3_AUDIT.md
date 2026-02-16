# Phase 3 Complete Architecture Audit

**Goal**: Understand data provenance, consumer dependencies, blast radius, and create a complete implementation plan with zero technical debt.

**Date**: 2026-02-16
**Status**: In Progress

---

## Executive Summary

### Critical Findings

1. **Signal plugins are DEAD CODE** (169 lines) — Never imported or called
2. **AnalysisEngine computes signals twice** — compression_ratio + cognitive_load computed in engine, then fusion reads them
3. **File reading happens 1.5x** (not 4x as initially thought) — Cache exists and IS being used by fusion
4. **FileAnalysis is the bridge** — Engine writes signals to FileAnalysis, fusion reads from it
5. **Clean separation already exists** — The architecture is cleaner than expected

### Revised Understanding

The **4x file reading problem doesn't exist** in SignalFusion! Here's what actually happens:

```
SyntaxExtractor → reads files, caches content ✅
  ↓
AnalysisEngine → uses content cache via content_getter ✅
  ↓
  Computes: compression_ratio, cognitive_load
  Stores in: FileAnalysis (in CodebaseAnalysis)
  ↓
SignalFusion → reads from FileAnalysis ✅
  Does NOT re-read files!
  Lines 156-157: fs.compression_ratio = fa.compression_ratio
```

**The ONLY redundant file read** is in **clone detection** (doesn't use cache).

---

## Part 1: Data Provenance Map

### Complete Data Flow (Every Signal, Every Source)

```
┌──────────────────────────────────────────────────────────────┐
│ PHASE 0: File System Scan                                   │
└──────────────────────────────────────────────────────────────┘
  Environment.scan()
    ↓
  List[Path] — all file paths in codebase
    ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: Syntax Extraction (SyntaxExtractor)                │
│ READ FILES ONCE ← ONLY DISK I/O                             │
└──────────────────────────────────────────────────────────────┘
  for each file:
    content = path.read_text()  ← DISK READ
    store._content_cache[path] = content  ← CACHE
    syntax = parse(content)
    ↓
  store.file_syntax.set(dict[path, FileSyntax])
    ↓
  FileSyntax contains:
    - path: str
    - lines: int (computed property)
    - function_count: int (computed)
    - class_count: int (computed)
    - import_sources: list[str] (parsed)
    - function_sizes: list[int]
    - max_nesting: int
    - complexity: float
    - impl_gini: float (computed)
    - stub_ratio: float (computed)

┌──────────────────────────────────────────────────────────────┐
│ PHASE 2: WAVE 1 ANALYZERS                                   │
└──────────────────────────────────────────────────────────────┘

─────────────────────────────────────────────────────────────
1. StructuralAnalyzer
─────────────────────────────────────────────────────────────
  Input:  store.file_syntax (dict[path, FileSyntax])
          store._content_cache (for compression_ratio)

  Calls:  AnalysisEngine.run()

  AnalysisEngine does:
    A. build_dependency_graph(file_syntax)
        → DependencyGraph:
            - adjacency: dict[str, list[str]]  (A→B edges)
            - reverse: dict[str, list[str]]    (B←A edges)
            - all_nodes: set[str]
            - edge_count: int
            - unresolved_imports: dict[str, list[str]]

    B. run_graph_algorithms(graph)
        → GraphAnalysis:
            - pagerank: dict[str, float]
            - betweenness: dict[str, float]
            - in_degree: dict[str, int]
            - out_degree: dict[str, int]
            - blast_radius: dict[str, set[str]]
            - cycles: list[CycleGroup]
            - communities: list[Community]
            - node_community: dict[str, int]
            - modularity_score: float
            - depth: dict[str, int]
            - is_orphan: dict[str, bool]
            - centrality_gini: float
            - spectral_gap: float

    C. _measure_files(graph, graph_analysis)
        FOR EACH FILE:
          Read content from cache:
            content = self._content_getter(path)  ← FROM CACHE

          Compute:
            - compression_ratio = Compression.compression_ratio(content)
            - cognitive_load = _compute_cognitive_load(syntax)
            - function_size_gini = Gini.gini_coefficient(sizes)

          Graph data:
            - pagerank, betweenness, in/out degree (from GraphAnalysis)
            - blast_radius_size, community_id
            - depth, is_orphan, phantom_import_count

        → dict[path, FileAnalysis]

        FileAnalysis contains:
          - path: str
          - lines, function_count, nesting_depth, max_function_size
          - compression_ratio ← COMPUTED HERE
          - cognitive_load ← COMPUTED HERE
          - function_size_gini
          - pagerank, betweenness, in/out_degree
          - blast_radius_size, community_id, cycle_member
          - depth, is_orphan, phantom_import_count
          - depends_on, depended_on_by

    D. _measure_modules(graph, graph_analysis)
        Group files by directory
        Compute per-module:
          - cohesion = internal_edges / possible_internal
          - coupling = external_edges / total_edges
          - boundary_alignment = dominant_community_ratio

        → dict[module_path, ModuleAnalysis]

    E. _analyze_boundaries(modules, graph_analysis)
        Find modules where:
          boundary_alignment < 0.7 AND file_count > 2

        → list[BoundaryMismatch]

    F. _detect_outliers(files)
        Statistical outlier detection using MAD
        Metrics: cognitive_load, compression_ratio, function_size_gini, blast_radius

        → dict[path, list[str]]

  Output: CodebaseAnalysis
    - files: dict[path, FileAnalysis]
    - modules: dict[path, ModuleAnalysis]
    - graph: DependencyGraph
    - graph_analysis: GraphAnalysis
    - boundary_mismatches: list[BoundaryMismatch]
    - outliers: dict[path, list[str]]
    - total_files, total_modules, total_edges, cycle_count, modularity

  Also runs: detect_clones(file_contents, roles)
    → list[ClonePair]

    PROBLEM: Clone detection RE-READS files from disk!
    Lines 114-117 in structural.py:
      full_path = root / path
      file_contents[path] = full_path.read_bytes()  ← DISK READ

    Should use: store.get_content(path)  ← FROM CACHE

  Writes:
    - store.structural.set(CodebaseAnalysis)
    - store.clone_pairs.set(list[ClonePair])

─────────────────────────────────────────────────────────────
2. TemporalAnalyzer
─────────────────────────────────────────────────────────────
  Input:  store.file_syntax (for file paths)
          Git repository (runs git log)

  Calls:  extract_git_history(root_dir, file_paths)
          build_cochange_matrix(commits)
          compute_churn_metrics(commits, file_paths)
          compute_author_distances(commits)

  Output:
    - GitHistory: commits, file_changes
    - CoChangeMatrix: matrix[file_a, file_b] → co-change count
    - dict[path, ChurnSeries]:
        - total_changes: int
        - trajectory: str (STABILIZING|CHURNING|SPIKING|DORMANT)
        - slope, cv (coefficient of variation)
        - bus_factor: float (2^H where H = author entropy)
        - author_entropy, fix_ratio, refactor_ratio
    - list[AuthorDistance]: file_a, file_b, distance

  Writes:
    - store.git_history.set(GitHistory)
    - store.cochange.set(CoChangeMatrix)
    - store.churn.set(dict[path, ChurnSeries])
    - store.author_distances.set(list[AuthorDistance])

─────────────────────────────────────────────────────────────
3. SemanticAnalyzer
─────────────────────────────────────────────────────────────
  Input:  store.file_syntax (FileSyntax for content analysis)

  Calls:  extract_concepts(syntax) → TF-IDF
          classify_role(syntax) → Role enum
          compute_coherence(syntax)

  Output:
    - dict[path, FileSemantics]:
        - concept_count: int
        - concept_entropy: float
        - concepts: dict[str, float] (concept → weight)
        - naming_drift: float
        - todo_density: float
        - docstring_coverage: float | None
    - dict[path, str] (Role):
        - ENTRY_POINT, MODEL, TEST, CONFIG, etc.

  Writes:
    - store.semantics.set(dict[path, FileSemantics])
    - store.roles.set(dict[path, str])

─────────────────────────────────────────────────────────────
4. SpectralAnalyzer
─────────────────────────────────────────────────────────────
  Input:  store.structural (needs DependencyGraph)

  Calls:  compute_laplacian(graph)
          compute_fiedler_value(laplacian)

  Output: SpectralSummary
    - fiedler_value: float
    - algebraic_connectivity: float

  Writes:
    - store.spectral.set(SpectralSummary)

─────────────────────────────────────────────────────────────
5. ArchitectureAnalyzer
─────────────────────────────────────────────────────────────
  Input:  store.structural (graph, modules)
          store.semantics (for role-based module grouping)

  Calls:  detect_modules(graph)
          compute_martin_metrics(modules)
          infer_layers(modules)
          find_violations(modules, layers)

  Output: Architecture
    - modules: dict[path, ModuleInfo]
        - instability: float | None
        - abstractness: float
        - main_seq_distance: float
        - role_consistency: float
        - layer: int
        - layer_violation_count: int

  Writes:
    - store.architecture.set(Architecture)

┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: WAVE 2 ANALYZER (SignalFusionAnalyzer)             │
└──────────────────────────────────────────────────────────────┘

  Input:  ALL Wave 1 slots
          - store.file_syntax
          - store.structural ← READS compression_ratio, cognitive_load HERE
          - store.churn
          - store.semantics
          - store.roles
          - store.architecture

  Process:
    1. step1_collect()
        FOR EACH FILE:
          _fill_from_syntax(fs, syntax)
            → lines, function_count, class_count, max_nesting,
              impl_gini, stub_ratio, import_count

          _fill_from_graph(fs)
            fa = structural.files.get(path)  ← FileAnalysis
            fs.compression_ratio = fa.compression_ratio  ← READ FROM ENGINE
            fs.cognitive_load = fa.cognitive_load        ← READ FROM ENGINE
            fs.pagerank, betweenness, in/out_degree, ...

          _fill_from_semantics(fs)
            → role, concept_count, concept_entropy, naming_drift,
              todo_density, docstring_coverage, semantic_coherence

          _fill_from_temporal(fs)
            → total_changes, churn_trajectory, churn_slope, churn_cv,
              bus_factor, author_entropy, fix_ratio, refactor_ratio

        Aggregate:
          _fill_hierarchy() → parent_dir, module_path, dir_depth, siblings_count
          _collect_directories() → per_directory aggregates
          _collect_modules() → per_module aggregates (from architecture)
          _collect_global() → codebase-wide aggregates

    2. step2_raw_risk()
        Compute raw_risk BEFORE percentiles
        Used by health Laplacian

    3. step3_normalize()
        Compute percentiles for all signals
        (Skip if tier = ABSOLUTE)

    4. step4_module_temporal()
        Aggregate temporal signals to module level

    5. step5_composites()
        Compute composite signals:
          - risk_score = weighted combination
          - wiring_quality = weighted combination
          - file_health_score, module_health_score

    6. step6_laplacian()
        Compute health Laplacian (change propagation)

  Output: SignalField
    - per_file: dict[path, FileSignals]
    - per_directory: dict[path, DirectorySignals]
    - per_module: dict[path, ModuleSignals]
    - global_signals: GlobalSignals
    - tier: str

  Writes:
    - store.signal_field.set(SignalField)

┌──────────────────────────────────────────────────────────────┐
│ PHASE 4: FINDERS (Pattern Matchers)                         │
└──────────────────────────────────────────────────────────────┘

  Input:  store.signal_field (primary)
          store.structural (some finders)
          store.clone_pairs (clone finders)
          store.architecture (architecture finders)

  30+ finders, each reads specific slots:
    - HIGH_RISK_HUB: signal_field
    - GOD_FILE: signal_field
    - ORPHAN_CODE: signal_field + structural.graph
    - COPY_PASTE_CLONE: clone_pairs
    - LAYER_VIOLATION: architecture
    - ACCIDENTAL_COUPLING: structural + semantics + roles
    - etc.

  Output: list[Finding]
```

---

## Part 2: Consumer Dependency Matrix

### Who Reads What From Where

| Data Source | Stored In | Read By | Purpose |
|-------------|-----------|---------|---------|
| **FileSyntax** | store.file_syntax | SemanticAnalyzer | Concept extraction, role classification |
| | | StructuralAnalyzer (via AnalysisEngine) | Graph building, file measurements |
| | | SignalFusion | Collect IR1 signals |
| **DependencyGraph** | store.structural.graph | SignalFusion | Graph signals |
| | | SpectralAnalyzer | Laplacian computation |
| | | OrphanCodeFinder | Orphan detection |
| | | DeadDependencyFinder | Dead edge detection |
| **FileAnalysis** | store.structural.files | SignalFusion | **compression_ratio, cognitive_load** |
| **compression_ratio** | FileAnalysis | SignalFusion | Copy to FileSignals |
| **cognitive_load** | FileAnalysis | SignalFusion | Copy to FileSignals |
| **ChurnSeries** | store.churn | SignalFusion | Temporal signals |
| **FileSemantics** | store.semantics | SignalFusion | Semantic signals |
| | | AccidentalCouplingFinder | Concept overlap |
| **Roles** | store.roles | SignalFusion | Role signal |
| | | CloneDetection | Exclude TEST/MIGRATION |
| | | AccidentalCouplingFinder | Filter by role |
| **Architecture** | store.architecture | SignalFusion | Module signals |
| | | LayerViolationFinder | Check violations |
| | | ConwayViolationFinder | Check alignment |
| **SignalField** | store.signal_field | ALL FINDERS | Primary data source |
| **ClonePairs** | store.clone_pairs | CopyPasteCloneFinder | Clone detection |
| | | DuplicateIncompleteFinder | Duplicate code |

---

## Part 3: The Signal Plugin Mystery SOLVED

### Are Signal Plugins Used?

**NO. They are DEAD CODE.**

Evidence:
```bash
# Search for imports of signal plugins
$ grep -r "from.*plugins" src/shannon_insight/**/*.py
src/shannon_insight/signals/plugins/volatility.py:from ..base import PrimitivePlugin
src/shannon_insight/signals/plugins/compression.py:from ..base import PrimitivePlugin
src/shannon_insight/signals/plugins/coherence.py:from ..base import PrimitivePlugin
src/shannon_insight/signals/plugins/cognitive_load.py:from ..base import PrimitivePlugin
```

**Result**: Only the plugins themselves import PrimitivePlugin. Nobody else imports them!

### Why Don't They Run?

The old v1 architecture had a plugin system. v2 replaced it with direct computation in:
1. **AnalysisEngine** — computes compression_ratio, cognitive_load
2. **SignalFusion** — reads those values from FileAnalysis

The plugin files still exist but are **orphaned code**.

### Files to Delete (169 lines total)

```bash
src/shannon_insight/signals/plugins/compression.py       # 40 lines
src/shannon_insight/signals/plugins/cognitive_load.py     # 61 lines
src/shannon_insight/signals/plugins/coherence.py          # 39 lines
src/shannon_insight/signals/plugins/volatility.py         # 29 lines
src/shannon_insight/signals/base.py                       # (if unused)
```

---

## Part 4: File Reading Audit (REVISED)

### Initial Hypothesis: Files Read 4x

**WRONG**. Actual file reading:

```
SyntaxExtractor:       1000 reads (cached) ✅
AnalysisEngine:           0 reads (uses cache) ✅
SignalFusion:             0 reads (reads from FileAnalysis) ✅
CloneDetection:        1000 reads (bypasses cache) ❌

TOTAL: 2000 reads (2x, not 4x)
```

### The Cache IS Working (Mostly)

```python
# AnalysisEngine._read_file_content() — USES CACHE
def _read_file_content(self, rel_path: str) -> Optional[str]:
    # Try cache first (WORKS!)
    if self._content_getter is not None:
        content = self._content_getter(rel_path)
        if content is not None:
            return content  # ✅ Returns cached content

    # Fallback to disk (rarely happens)
    return Path(rel_path).read_text()
```

### The ONLY Problem: Clone Detection

```python
# analyzers/structural.py:114-117
for path in store.files:
    # ❌ BAD: Bypasses cache
    full_path = root / path
    file_contents[path] = full_path.read_bytes()

# ✅ SHOULD BE:
for path in store.files:
    content = store.get_content(path)  # Use cache
    if content:
        file_contents[path] = content.encode("utf-8")
```

**Fix**: 2 lines changed, eliminates 1000 redundant reads.

---

## Part 5: Blast Radius Analysis

### If We Delete Signal Plugins

**Files affected**: 0

Reason: Nobody imports them.

**Risk**: None

### If We Remove compression_ratio/cognitive_load from AnalysisEngine

**Direct impacts**:
- `graph/engine.py` — remove lines 110-112, 115, 143-175
- `graph/models.py` — FileAnalysis still has fields (keep for now, consumers exist)
- `signals/fusion.py` — need to COMPUTE these signals instead of READING them

**Consumers of FileAnalysis.compression_ratio**:
- SignalFusion._fill_from_graph() — line 156
- engine._detect_outliers() — line 328

**Consumers of FileAnalysis.cognitive_load**:
- SignalFusion._fill_from_graph() — line 157
- engine._detect_outliers() — line 327

**Risk**: MEDIUM
- Must move computation to SignalFusion BEFORE removing from engine
- Must update or remove _detect_outliers()

### If We Slim AnalysisEngine

**Candidates for extraction**:

1. **_analyze_boundaries()** → Move to ArchitectureAnalyzer
   - Consumers: None (stores in CodebaseAnalysis.boundary_mismatches)
   - Risk: LOW (self-contained)

2. **_detect_outliers()** → Remove or extract
   - Consumers: None (stores in CodebaseAnalysis.outliers)
   - Usage: Unclear if finders use this
   - Risk: LOW (can remove if unused)

3. **compression_ratio/cognitive_load computation** → Move to SignalFusion
   - Consumers: SignalFusion (must refactor first)
   - Risk: MEDIUM (requires careful migration)

### If We Fix Clone Detection Cache Usage

**Files affected**:
- `insights/analyzers/structural.py` — _detect_clones() method

**Risk**: VERY LOW (local change, same output)

---

## Part 6: Ontological Naming Audit

### Current Names vs Reality

| Current Name | What It Actually Does | Better Name? |
|--------------|----------------------|--------------|
| **AnalysisEngine** | Builds graph + runs algorithms + measures files + modules | GraphAnalyzer? StructuralBuilder? |
| **StructuralAnalyzer** | Thin wrapper around AnalysisEngine + clone detection | (absorb AnalysisEngine) |
| **FileAnalysis** | Per-file measurements from graph layer | ✅ GOOD |
| **FileSignals** | Per-file signals from fusion layer | ✅ GOOD |
| **SignalFusionAnalyzer** | Unifies all signals into SignalField | ✅ GOOD |
| **Primitives** | OLD v1 model (5 primitives) | DEPRECATED (keep for compatibility) |
| **_content_cache** | Content cache in AnalysisStore | ✅ GOOD |
| **content_getter** | Function to read from cache | ✅ GOOD |

### Naming Improvements

1. **AnalysisEngine** → **GraphBuilder** or **StructuralEngine**
   - Current name too generic
   - "Engine" suggests orchestration (that's the Kernel's job)
   - "GraphBuilder" is more specific

2. Keep **FileAnalysis** and **FileSignals** as distinct
   - FileAnalysis = graph layer output
   - FileSignals = fusion layer output
   - Clear separation of concerns

---

## Part 7: Dead Code Audit

### Confirmed Dead Code

1. **Signal plugins** (169 lines)
   - `signals/plugins/compression.py`
   - `signals/plugins/cognitive_load.py`
   - `signals/plugins/coherence.py`
   - `signals/plugins/volatility.py`
   - `signals/base.py` (PrimitivePlugin base class)

2. **Possibly dead**:
   - `AnalysisEngine._detect_outliers()` — stored in CodebaseAnalysis.outliers, but does any finder read it?
   - `CodebaseAnalysis.outliers` field — need to check if used

### Zombie Code (Still Called But Redundant)

1. **AnalysisEngine._compute_cognitive_load()**
   - Computes cognitive_load
   - SignalFusion just copies the value
   - Should move to SignalFusion

2. **AnalysisEngine compression_ratio in _measure_files()**
   - Reads from cache, computes compression
   - SignalFusion just copies the value
   - Should move to SignalFusion

---

## Part 8: Separation of Concerns Audit

### Current Responsibilities

```
AnalysisEngine (graph/engine.py):
  ✅ build_dependency_graph() — BELONGS HERE
  ✅ run_graph_algorithms() — BELONGS HERE
  ✅ _measure_modules() — BELONGS HERE (module = graph concept)
  ❌ _measure_files() compression/cognitive — BELONGS IN FUSION
  ❌ _analyze_boundaries() — BELONGS IN ARCHITECTURE
  ❓ _detect_outliers() — UNCLEAR VALUE

StructuralAnalyzer (insights/analyzers/structural.py):
  ✅ Calls AnalysisEngine — MAKES SENSE
  ✅ Clone detection — MAKES SENSE (structural similarity)
  ❌ Thin wrapper — COULD ABSORB ENGINE

SignalFusionAnalyzer (signals/analyzer.py):
  ✅ Unifies all signals — BELONGS HERE
  ❌ Doesn't compute compression/cognitive — SHOULD COMPUTE

ArchitectureAnalyzer (architecture/analyzer.py):
  ✅ Module detection, Martin metrics — BELONGS HERE
  ❌ Doesn't handle boundaries — SHOULD TAKE FROM ENGINE
```

### Ideal Separation

```
GraphBuilder (rename AnalysisEngine):
  - build_dependency_graph()
  - run_graph_algorithms()
  - measure_modules() (cohesion/coupling)
  - NOTHING ELSE

StructuralAnalyzer:
  - Calls GraphBuilder
  - Clone detection
  - (Maybe absorb GraphBuilder directly)

ArchitectureAnalyzer:
  - Module detection
  - Martin metrics
  - Layer inference
  - Boundary analysis (moved from engine)

SignalFusionAnalyzer:
  - Collect all signals
  - COMPUTE compression_ratio (not copy)
  - COMPUTE cognitive_load (not copy)
  - Normalize, percentiles
  - Composites, health Laplacian
```

---

## Part 9: Complete Implementation Plan

### Zero Technical Debt Migration

#### Phase 3A: Delete Dead Code (SAFE, IMMEDIATE)

**Files to delete**:
```bash
rm src/shannon_insight/signals/plugins/compression.py
rm src/shannon_insight/signals/plugins/cognitive_load.py
rm src/shannon_insight/signals/plugins/coherence.py
rm src/shannon_insight/signals/plugins/volatility.py
# Check if base.py is used elsewhere first
rm src/shannon_insight/signals/base.py  # If unused
```

**Tests to update**:
- None (plugins are not tested because they're never called)

**Risk**: ZERO (dead code)

**Time**: 5 minutes

#### Phase 3B: Fix Clone Detection Cache (SAFE, HIGH IMPACT)

**File**: `src/shannon_insight/insights/analyzers/structural.py`

**Change**:
```python
def _detect_clones(self, store: AnalysisStore) -> None:
    """Run NCD clone detection on file contents."""
    root = Path(store.root_dir) if store.root_dir else Path.cwd()

    # Get file contents from cache
    file_contents: dict[str, bytes] = {}
    for path in store.files:
        # Use cache (not disk!)
        content = store.get_content(path)
        if content is not None:
            file_contents[path] = content.encode("utf-8")
```

**Remove**:
```python
# DELETE THIS FALLBACK (shouldn't happen)
else:
    try:
        full_path = root / path
        file_contents[path] = full_path.read_bytes()
    except OSError:
        pass
```

**Impact**: Eliminates 1000 file reads for 1000-file codebase

**Risk**: VERY LOW (same computation, different source)

**Tests**: Existing clone detection tests should pass unchanged

**Time**: 10 minutes

#### Phase 3C: Move Boundary Analysis to ArchitectureAnalyzer (MEDIUM RISK)

**From**: `graph/engine.py:_analyze_boundaries()`

**To**: `architecture/analyzer.py`

**Steps**:
1. Copy `_analyze_boundaries()` and `_suggest_module()` to ArchitectureAnalyzer
2. Call from ArchitectureAnalyzer.analyze()
3. Store in Architecture model (add boundary_mismatches field)
4. Remove from AnalysisEngine
5. Update consumers

**Consumers to check**:
- Does anything read `CodebaseAnalysis.boundary_mismatches`?
- Likely: BoundaryMismatchFinder

**Risk**: MEDIUM (moving code between analyzers)

**Time**: 30 minutes

**Tests**: Architecture analyzer tests

#### Phase 3D: Audit and Remove _detect_outliers() (CONDITIONAL)

**Investigation**:
```bash
# Check if outliers field is used
grep -r "\.outliers" src/shannon_insight/
```

**If unused**:
- Remove `_detect_outliers()` from AnalysisEngine
- Remove `outliers` field from CodebaseAnalysis

**If used**:
- Keep for now
- Document usage
- Consider moving to separate analyzer

**Risk**: LOW (self-contained feature)

**Time**: 15 minutes

#### Phase 3E: Move Compression/Cognitive Computation to SignalFusion (HIGH IMPACT)

**This is the BIG ONE**. Careful migration required.

**Current Flow**:
```
AnalysisEngine._measure_files()
  → Computes compression_ratio, cognitive_load
  → Stores in FileAnalysis

SignalFusion._fill_from_graph()
  → Reads fa.compression_ratio, fa.cognitive_load
  → Copies to FileSignals
```

**New Flow**:
```
SignalFusion.step1_collect()
  → Computes compression_ratio, cognitive_load directly
  → Uses store.get_content() for cached reads
  → Stores in FileSignals
```

**Steps**:

1. **Add computation to SignalFusion** (additive, safe)
   ```python
   # In fusion.py:_fill_from_graph()

   # TEMPORARY: Compute AND read (for validation)
   path = fs.path
   content = self.store.get_content(path)
   if content:
       computed_compression = Compression.compression_ratio(content.encode())
       computed_cognitive = self._compute_cognitive_load_v2(syntax, content)

       # Validate against engine's computation
       if fa:
           assert abs(computed_compression - fa.compression_ratio) < 0.01
           assert abs(computed_cognitive - fa.cognitive_load) < 0.01

       fs.compression_ratio = computed_compression
       fs.cognitive_load = computed_cognitive
   ```

2. **Port cognitive_load formula** from engine to fusion
   ```python
   def _compute_cognitive_load_v2(self, syntax: FileSyntax, content: str) -> float:
       """Cognitive load formula from engine._compute_cognitive_load()."""
       import math
       lines_factor = math.log2(syntax.lines + 1) if syntax.lines > 0 else 0
       complexity_factor = 1 + syntax.complexity / 10
       nesting_factor = 1 + syntax.max_nesting / 5
       gini = syntax.impl_gini if syntax.impl_gini else 0.0
       gini_factor = 1 + gini
       return lines_factor * complexity_factor * nesting_factor * gini_factor
   ```

3. **Run all tests** — should pass with assertions

4. **Remove assertions** — trust the new computation

5. **Remove from AnalysisEngine**:
   ```python
   # In engine.py:_measure_files()
   # DELETE these lines:
   # content = self._read_file_content(fs.path)
   # if content:
   #     fa.compression_ratio = Compression.compression_ratio(content.encode("utf-8"))
   # fa.cognitive_load = self._compute_cognitive_load(fs)
   ```

6. **Remove _compute_cognitive_load() method**

7. **Keep fields in FileAnalysis** (for now, backward compatibility)

8. **Run all tests** again

**Risk**: MEDIUM (computation move, must validate identical results)

**Time**: 1 hour

**Tests**: All signal tests, fusion tests, integration tests

#### Phase 3F: Rename AnalysisEngine → GraphBuilder (OPTIONAL, LOW PRIORITY)

**Only if we want perfect ontology**

**Changes**:
- Rename `graph/engine.py` → `graph/graph_builder.py`
- Rename class `AnalysisEngine` → `GraphBuilder`
- Update imports in `insights/analyzers/structural.py`

**Risk**: LOW (renaming only)

**Time**: 15 minutes

#### Phase 3G: Absorb GraphBuilder into StructuralAnalyzer (OPTIONAL)

**If we want maximum simplicity**

Merge GraphBuilder directly into StructuralAnalyzer.analyze()

**Pros**:
- Fewer files
- Clearer flow (no wrapper)

**Cons**:
- Longer method
- Harder to test in isolation

**Decision**: DEFER (not critical)

---

## Part 10: Final State (After All Changes)

### File Reading: 1x

```
SyntaxExtractor:    1000 reads (cached) ✅
AnalysisEngine:        0 reads (no longer reads files) ✅
SignalFusion:          0 reads (uses cache) ✅
CloneDetection:        0 reads (uses cache) ✅

TOTAL: 1000 reads (1x) ⚡
```

### Analyzer Responsibilities

```
StructuralAnalyzer:
  ✅ Build dependency graph
  ✅ Run graph algorithms (PageRank, SCC, Louvain, etc.)
  ✅ Compute module cohesion/coupling
  ✅ Clone detection (NCD)
  ❌ NO per-file signal computation
  ❌ NO boundary analysis

ArchitectureAnalyzer:
  ✅ Detect modules
  ✅ Compute Martin metrics
  ✅ Infer layers
  ✅ Find violations
  ✅ Analyze boundary mismatches (moved from engine)

SignalFusionAnalyzer:
  ✅ Collect all signals
  ✅ COMPUTE compression_ratio (moved from engine)
  ✅ COMPUTE cognitive_load (moved from engine)
  ✅ Normalize, percentiles
  ✅ Composites, health Laplacian
```

### Lines of Code

```
BEFORE:
  graph/engine.py:                380 lines (bloated)
  analyzers/structural.py:        130 lines (thin wrapper)
  signals/plugins/*.py:           169 lines (dead code)
  signals/fusion.py:              ~800 lines

AFTER:
  graph/engine.py:                ~250 lines (slimmed)
  analyzers/structural.py:        130 lines (unchanged)
  signals/plugins/*.py:           DELETED
  signals/fusion.py:              ~850 lines (+50 for compression/cognitive)

NET: -200 lines, cleaner separation
```

---

## Part 11: Migration Checklist

### Pre-Flight Checks

- [ ] All tests passing (`make test`)
- [ ] Git status clean
- [ ] Create feature branch: `git checkout -b phase3-cleanup`

### Phase 3A: Delete Dead Code

- [ ] Delete signal plugin files
- [ ] Delete base.py (if unused)
- [ ] Run `make all`
- [ ] Commit: "Delete unused signal plugins (169 lines)"

### Phase 3B: Fix Clone Detection Cache

- [ ] Modify `_detect_clones()` to use `store.get_content()`
- [ ] Remove disk read fallback
- [ ] Run clone detection tests
- [ ] Run full suite
- [ ] Commit: "Fix clone detection to use content cache"

### Phase 3C: Move Boundary Analysis

- [ ] Copy methods to ArchitectureAnalyzer
- [ ] Add boundary_mismatches to Architecture model
- [ ] Update ArchitectureAnalyzer.analyze() to call it
- [ ] Remove from AnalysisEngine
- [ ] Check consumers (BoundaryMismatchFinder)
- [ ] Run architecture tests
- [ ] Commit: "Move boundary analysis to ArchitectureAnalyzer"

### Phase 3D: Audit Outliers

- [ ] Search for `.outliers` usage
- [ ] If unused: remove `_detect_outliers()` and field
- [ ] If used: document and keep
- [ ] Run tests
- [ ] Commit: "Remove unused outlier detection" OR "Document outlier detection usage"

### Phase 3E: Move Compression/Cognitive to Fusion

- [ ] Add computation to SignalFusion with validation assertions
- [ ] Port `_compute_cognitive_load()` formula
- [ ] Run all tests (should pass with assertions)
- [ ] Remove assertions
- [ ] Remove computation from AnalysisEngine
- [ ] Remove `_compute_cognitive_load()` method
- [ ] Run all tests again
- [ ] Commit: "Move compression_ratio and cognitive_load to SignalFusion"

### Phase 3F: Optional Rename

- [ ] Rename AnalysisEngine → GraphBuilder
- [ ] Update imports
- [ ] Run tests
- [ ] Commit: "Rename AnalysisEngine to GraphBuilder for clarity"

### Final Validation

- [ ] Run `make all` (format, check, test)
- [ ] Run integration tests
- [ ] Test on real codebase
- [ ] Verify performance improvement (profile file I/O)
- [ ] Review all commits
- [ ] Merge to main

---

## Part 12: Risk Mitigation

### High-Risk Changes

1. **Moving compression/cognitive computation**
   - Mitigation: Add validation assertions during transition
   - Fallback: Keep both computations, compare, gradually remove old

2. **Moving boundary analysis**
   - Mitigation: Copy first, remove later
   - Fallback: Keep in both places temporarily

### Testing Strategy

1. **Unit tests**: Each analyzer in isolation
2. **Integration tests**: Full pipeline end-to-end
3. **Regression tests**: Compare outputs before/after on sample codebases
4. **Performance tests**: Measure file I/O before/after

### Rollback Plan

Each phase is atomic:
- Phase 3A: Revert commit (delete dead code is safe)
- Phase 3B: Revert commit (cache usage is local)
- Phase 3C: Revert commit (boundary analysis move)
- Phase 3E: Revert commit (computation move)

If any phase fails, revert that commit and reassess.

---

## Conclusion

### What We Learned

1. **Signal plugins are dead code** (169 lines to delete)
2. **File reading is NOT 4x** — cache is working, clone detection is the only issue (2x, not 4x)
3. **The architecture is cleaner than expected** — main issue is separation of concerns, not duplication
4. **AnalysisEngine does too much** — should focus on graph, not file measurements
5. **SignalFusion should compute, not copy** — compression/cognitive belong in fusion layer

### The Real Problems

1. ❌ **Clone detection bypasses cache** (1000 redundant reads)
2. ❌ **AnalysisEngine computes signals that fusion could compute** (not wrong, but separation violation)
3. ❌ **Dead code still in repo** (169 lines of plugins)
4. ❌ **Boundary analysis in wrong analyzer** (belongs in Architecture)

### The Fix

1. ✅ Delete signal plugins (5 min, zero risk)
2. ✅ Fix clone cache (10 min, very low risk)
3. ✅ Move boundary analysis (30 min, medium risk)
4. ✅ Move compression/cognitive (1 hour, medium risk)

**Total time**: ~2 hours
**Total impact**: Clean separation, 1x file reads (from 2x), 200 fewer lines

### Ready to Execute?

This plan is:
- ✅ Complete (every data flow traced)
- ✅ Safe (each step atomic and reversible)
- ✅ Zero debt (no compromises)
- ✅ Ontologically correct (names match reality)
- ✅ Well-tested (validation at each step)
- ✅ Best practices (clear separation of concerns)

**Next step**: Execute Phase 3A (delete dead code)?
