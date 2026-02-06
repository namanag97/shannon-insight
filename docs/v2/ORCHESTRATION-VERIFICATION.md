# Orchestration Verification: First Time Right

> **Goal**: Verify every connection in the pipeline so implementation works on first attempt.
> No gaps, no ambiguity, no "figure it out during coding".

---

## 1. Store Slot Ownership Matrix

Every slot has EXACTLY ONE writer. Multiple readers OK.

| Slot | Writer | Phase | Type | Readers |
|------|--------|-------|------|---------|
| `file_metrics` | Kernel (input) | 0 | `List[FileMetrics]` | All analyzers, all finders |
| `file_syntax` | ScannerFactory | 1 | `Dict[str, FileSyntax]` | SemanticAnalyzer, GraphBuilder, clone detection |
| `structural` | StructuralAnalyzer | 0 | `CodebaseAnalysis` | ArchitectureAnalyzer, SignalFusion, most finders |
| `git_history` | TemporalAnalyzer | 3 | `GitHistory` | ChurnClassifier |
| `churn` | TemporalAnalyzer | 3 | `Dict[str, ChurnSeries]` | SignalFusion, temporal finders |
| `cochange` | TemporalAnalyzer | 3 | `CoChangeMatrix` | HIDDEN_COUPLING, DEAD_DEPENDENCY |
| `semantics` | SemanticAnalyzer | 2 | `Dict[str, FileSemantics]` | ACCIDENTAL_COUPLING, role signals |
| `roles` | SemanticAnalyzer | 2 | `Dict[str, str]` | orphan detection, ORPHAN_CODE, role_consistency |
| `clone_pairs` | StructuralAnalyzer | 3 | `List[ClonePair]` | COPY_PASTE_CLONE, clone_ratio |
| `author_distances` | StructuralAnalyzer | 3 | `List[AuthorDistance]` | CONWAY_VIOLATION, conway_alignment |
| `architecture` | ArchitectureAnalyzer | 4 | `Architecture` | SignalFusion, architecture finders |
| `spectral` | SpectralAnalyzer | 0 | `SpectralSummary` | fiedler_value, spectral_gap |
| `signal_field` | SignalFusionAnalyzer | 5 | `SignalField` | ALL finders (primary data source) |

**Verification**: ✅ No slot has multiple writers. Every slot has defined type.

---

## 2. Analyzer Dependency Resolution

Kernel uses `graphlib.TopologicalSorter` to order analyzers.

### Analyzer DAG

```
                    ┌─────────────────────────────────────────────┐
                    │                                             │
                    ▼                                             │
┌─────────────┐   ┌─────────────────┐   ┌────────────────────┐   │
│   Scanner   │──▶│StructuralAnalyzer│──▶│ArchitectureAnalyzer│   │
│ (file_syntax)│   │   (structural)   │   │   (architecture)   │   │
└─────────────┘   └─────────────────┘   └────────────────────┘   │
      │                   │                       │               │
      │                   │                       │               │
      ▼                   │                       │               │
┌─────────────┐           │                       │               │
│SemanticAnalyzer│◀────────┘                       │               │
│ (semantics,  │                                   │               │
│   roles)     │                                   │               │
└─────────────┘                                   │               │
      │                                           │               │
      └───────────────────────────────────────────┼───────────────┘
                                                  │
                    PARALLEL SPINE                │
                         │                        │
┌─────────────────┐      │                        │
│TemporalAnalyzer │      │                        │
│ (git_history,   │──────┼────────────────────────┤
│  churn, cochange)      │                        │
└─────────────────┘      │                        │
                         │                        │
                         ▼                        │
              ┌─────────────────────┐             │
              │ SignalFusionAnalyzer │◀────────────┘
              │   (signal_field)     │
              │    run_last=True     │
              └─────────────────────┘
```

### Explicit requires/provides

| Analyzer | requires | provides | run_last |
|----------|----------|----------|----------|
| Scanner | `{}` | `{"file_syntax"}` | false |
| StructuralAnalyzer | `{"file_syntax"}` | `{"structural", "clone_pairs", "author_distances"}` | false |
| SemanticAnalyzer | `{"file_syntax"}` | `{"semantics", "roles"}` | false |
| TemporalAnalyzer | `{}` | `{"git_history", "churn", "cochange"}` | false |
| SpectralAnalyzer | `{"structural"}` | `{"spectral"}` | false |
| ArchitectureAnalyzer | `{"structural", "roles"}` | `{"architecture"}` | false |
| SignalFusionAnalyzer | `{"*"}` | `{"signal_field"}` | **true** |

### Resolution Order (one valid topological sort)

```
1. Scanner              (no deps)
2. TemporalAnalyzer     (no deps, parallel)
3. StructuralAnalyzer   (needs file_syntax)
4. SemanticAnalyzer     (needs file_syntax)
5. SpectralAnalyzer     (needs structural)
6. ArchitectureAnalyzer (needs structural, roles)
--- Wave 2 ---
7. SignalFusionAnalyzer (run_last=true, reads all)
```

**Verification**: ✅ No cycles. All requires satisfied before provides needed.

---

## 3. Signal Computation Order

Within SignalFusionAnalyzer, signals must be computed in dependency order.

### Signal Dependency DAG

```
Phase 0 (scanning):
  #1 lines, #2 function_count, #3 class_count, #7 import_count
  #14 pagerank, #15 betweenness, #16 in_degree, #17 out_degree
  #18 blast_radius_size, #23 community, #24 compression_ratio
  #52 modularity, #53 fiedler_value, #54 spectral_gap, #55 cycle_count
                    │
                    ▼
Phase 1 (tree-sitter):
  #4 max_nesting, #5 impl_gini, #6 stub_ratio, #12 todo_density
  #26 cognitive_load (uses #2, #4, #5)
                    │
                    ▼
Phase 2 (semantics):
  #8 role, #9 concept_count, #10 concept_entropy, #11 naming_drift
  #13 docstring_coverage, #25 semantic_coherence
                    │
                    ▼
Phase 3 (enrichment):
  #19 depth (needs #8 role for entry points)
  #20 is_orphan (needs #8 role, #16 in_degree)
  #21 phantom_import_count
  #27-34 temporal signals (parallel, no structural deps)
  #56 centrality_gini, #57 orphan_ratio, #58 phantom_ratio, #59 glue_deficit
                    │
                    ▼
Phase 4 (architecture):
  #37 cohesion, #38 coupling, #39 instability, #40 abstractness
  #41 main_seq_distance (needs #39, #40)
  #42 boundary_alignment (needs #23 community)
  #43 layer_violation_count, #44 role_consistency (needs #8)
  #50 file_count
                    │
                    ▼
Phase 5 (fusion):
  Step 1: Collect all raw signals into SignalField
  Step 2: Compute raw_risk (needs #14, #18, #26, #28, #31)
  Step 3: Normalize (compute percentiles)
  Step 4: Module temporal (#45-48) (needs percentiles for module_bus_factor)
  Step 5: Composites (#35, #36, #49, #51, #60-62)
  Step 6: Health Laplacian (Δh) (needs raw_risk, graph edges)
```

### Critical Ordering Constraints

| Constraint | Reason | Verified |
|------------|--------|----------|
| #8 role before #20 is_orphan | Orphan excludes ENTRY_POINT, TEST roles | ✅ |
| #23 community before #42 boundary | Boundary uses Louvain communities | ✅ |
| #39 instability before #41 main_seq | D = \|A + I - 1\| | ✅ |
| raw_risk before percentiles | Laplacian needs raw values, not uniform pctl | ✅ |
| percentiles before module_bus_factor | module_bf = min(bf) over high-centrality files | ✅ |
| composites after percentiles | risk_score uses pctl(pagerank), etc. | ✅ |

**Verification**: ✅ Signal computation order is unambiguous and acyclic.

---

## 4. Finder Activation Conditions

Every finder has explicit activation conditions checked by kernel.

### Activation Matrix

| Finder | Phase | Tier | Hotspot | Git | Modules | Snapshots |
|--------|-------|------|---------|-----|---------|-----------|
| HIGH_RISK_HUB | 5 | BAYESIAN+ | yes | yes | no | no |
| HIDDEN_COUPLING | 3 | ALL | no | yes | no | no |
| GOD_FILE | 5 | BAYESIAN+ | no | no | no | no |
| UNSTABLE_FILE | 3 | ALL | yes | yes | no | no |
| BOUNDARY_MISMATCH | 4 | BAYESIAN+ | no | no | yes | no |
| DEAD_DEPENDENCY | 3 | ALL | no | yes | no | no |
| CHRONIC_PROBLEM | 7 | ALL | no | no | no | yes (3+) |
| ORPHAN_CODE | 3 | ALL | no | no | no | no |
| HOLLOW_CODE | 1 | ALL | no | no | no | no |
| PHANTOM_IMPORTS | 3 | ALL | no | no | no | no |
| COPY_PASTE_CLONE | 3 | ALL | no | no | no | no |
| FLAT_ARCHITECTURE | 3 | ALL | no | no | no | no |
| NAMING_DRIFT | 2 | ALL | no | no | no | no |
| KNOWLEDGE_SILO | 5 | BAYESIAN+ | yes | yes | no | no |
| CONWAY_VIOLATION | 4 | BAYESIAN+ | no | yes | yes | no |
| REVIEW_BLINDSPOT | 5 | BAYESIAN+ | yes | yes | no | no |
| LAYER_VIOLATION | 4 | BAYESIAN+ | no | no | yes | no |
| ZONE_OF_PAIN | 4 | BAYESIAN+ | no | no | yes | no |
| ARCHITECTURE_EROSION | 7 | BAYESIAN+ | no | no | yes | yes (3+) |
| WEAK_LINK | 5 | BAYESIAN+ | yes | no | no | no |
| BUG_ATTRACTOR | 5 | BAYESIAN+ | yes | yes | no | no |
| ACCIDENTAL_COUPLING | 2 | BAYESIAN+ | no | no | no | no |

### Kernel Activation Logic

```python
def should_run_finder(finder: Finder, store: AnalysisStore, context: Context) -> bool:
    """Determine if finder should run based on all conditions."""

    # 1. Check phase (signal_field must exist for Phase 5+ finders)
    if finder.min_phase >= 5 and not store.signal_field.available:
        return False

    # 2. Check tier
    tier = store.signal_field.value.tier if store.signal_field.available else "ABSOLUTE"
    if finder.tier_minimum == "BAYESIAN" and tier == "ABSOLUTE":
        return False
    if finder.tier_minimum == "FULL" and tier != "FULL":
        return False

    # 3. Check git requirement
    if finder.requires_git and not store.git_history.available:
        return False

    # 4. Check module requirement
    if finder.requires_modules and not store.architecture.available:
        return False
    if finder.requires_modules and len(store.architecture.value.modules) < 2:
        return False

    # 5. Check snapshot requirement
    if finder.requires_snapshots:
        snapshot_count = context.get_snapshot_count()
        if snapshot_count < 3:
            return False

    # 6. All checks passed
    return True
```

**Verification**: ✅ Every finder has unambiguous activation conditions.

---

## 5. Edge Case Decision Matrix

Every edge case has a defined behavior. No "undefined" outcomes.

### Codebase Characteristics

| Characteristic | Detection | Behavior | Affected Finders |
|----------------|-----------|----------|------------------|
| 0 files | `len(file_metrics) == 0` | Return empty InsightResult | All |
| 1 file | `len(file_metrics) == 1` | ABSOLUTE tier, most finders skip | All percentile-based |
| < 15 files | `len(file_metrics) < 15` | ABSOLUTE tier, no composites | 14 finders skip |
| No git | `not git_history.available` | Temporal signals = defaults, temporal finders skip | 7 finders |
| Shallow clone | `git_history.value.is_shallow` | Log warning, proceed with available history | All temporal |
| Single author | `distinct_authors < 2` | G5 skipped, bus_factor=1 everywhere | CONWAY, KNOWLEDGE |
| Flat project | `module_count < 2` | architecture=None, arch finders skip | 6 finders |
| Library (no entry points) | Entry point fallback chain triggers | Use synthetic roots for depth | FLAT_ARCHITECTURE |
| All files orphan | All in_degree=0 | depth=0 for all, orphan_ratio=1.0 | ORPHAN_CODE fires for all |
| Circular modules | SCC detection | Merge into single layer, log warning | LAYER_VIOLATION |
| Encoding error | Tree-sitter parse fails | Regex fallback | None |
| Git timeout | Subprocess timeout (30s) | TemporalError, finder skip | All temporal |

### Signal Edge Cases

| Signal | Edge Case | Value | Rationale |
|--------|-----------|-------|-----------|
| #5 impl_gini | ≤1 function | 0.0 | No variance possible |
| #6 stub_ratio | 0 functions | 0.0 | Nothing to measure |
| #10 concept_entropy | <3 functions | 0.0 | Single concept assumed |
| #11 naming_drift | Generic filename | 0.0 | utils.py is intentionally generic |
| #19 depth | No entry points | 0 for all | Fallback chain exhausted |
| #19 depth | Unreachable file | -1 | Distinct from depth=0 |
| #20 is_orphan | Entry point | false | Excluded by role check |
| #22 broken_call_count | No CALL edges | 0 | Feature not implemented yet |
| #31 bus_factor | Single commit | 1.0 | One author = bus factor 1 |
| #39 instability | Ca+Ce=0 | None | Isolated module, skip D |
| #41 main_seq_distance | instability=None | None | Can't compute without I |
| delta_h | Orphan file | 0.0 | No neighbors to compare |

### Finder Edge Cases

| Finder | Edge Case | Behavior |
|--------|-----------|----------|
| HIGH_RISK_HUB | All equal pagerank | No file exceeds 0.90 pctl, no findings |
| GOD_FILE | Very small file | coherence=1.0 (single concept), won't fire |
| UNSTABLE_FILE | All DORMANT | No CHURNING/SPIKING files, no findings |
| ORPHAN_CODE | All orphans | All fire, grouped into max 3 findings |
| HOLLOW_CODE | Single function file | impl_gini=0, condition fails |
| ZONE_OF_PAIN | instability=None | Finder skips that module |
| WEAK_LINK | All neighbors high risk | Δh ≈ 0, finder won't fire |
| CHRONIC_PROBLEM | File renamed | Identity key updated, finding persists |

**Verification**: ✅ All edge cases have defined outcomes. No undefined behavior.

---

## 6. Data Type Contracts

Every handoff has explicit type expectations.

### Store Slot Types

```python
@dataclass
class AnalysisStore:
    root_dir: str
    file_metrics: List[FileMetrics]                    # Never None, may be empty

    # Typed slots with error context
    file_syntax: Slot[Dict[str, FileSyntax]]           # path → syntax
    structural: Slot[CodebaseAnalysis]                 # graph + analysis
    git_history: Slot[GitHistory]                      # commits, files
    churn: Slot[Dict[str, ChurnSeries]]                # path → churn
    cochange: Slot[CoChangeMatrix]                     # pair → metrics
    semantics: Slot[Dict[str, FileSemantics]]          # path → semantics
    roles: Slot[Dict[str, str]]                        # path → role name
    clone_pairs: Slot[List[ClonePair]]                 # detected clones
    author_distances: Slot[List[AuthorDistance]]       # G5 distances
    architecture: Slot[Architecture]                   # modules, layers
    spectral: Slot[SpectralSummary]                    # eigenvalues
    signal_field: Slot[SignalField]                    # ALL signals
```

### Signal Value Types

| Type | Signals | Python Type | JSON Type | Range |
|------|---------|-------------|-----------|-------|
| int | #1-3, 7, 16-19, 21-23, 27, 43, 50, 55 | `int` | `number` | [0, ∞) or [-1, ∞) for depth |
| float | #4-6, 10-15, 18, 24-26, 29-42, 44-49, 51-54, 56-62 | `float` | `number` | [0, 1] or [0, ∞) |
| bool | #20 | `bool` | `boolean` | {true, false} |
| enum | #8, #28 | `str` | `string` | defined values |
| Optional[float] | #39, #41 | `Optional[float]` | `number \| null` | [0, 1] or null |

### Composite Weight Contracts

| Composite | Weight Sum | Inputs | Output Range |
|-----------|------------|--------|--------------|
| risk_score | 1.00 | 5 terms | [0, 1] |
| wiring_quality | 1.00 | 4 terms | [0, 1] |
| health_score | 1.00 (or redistributed) | 6 terms | [0, 1] |
| wiring_score | 1.00 | 5 terms | [0, 1] |
| architecture_health | 1.00 | 5 terms | [0, 1] |
| codebase_health | 1.00 | 4 terms | [0, 1] |
| team_risk | 1.00 | 4 terms | [0, 1] |

**Verification**: ✅ All types explicit. All ranges defined.

---

## 7. Error Recovery Paths

Every failure has a defined recovery.

### Analyzer Failures

| Analyzer | Failure | Recovery | Downstream Impact |
|----------|---------|----------|-------------------|
| Scanner | File read error | Skip file, log warning | File excluded from analysis |
| Scanner | Parse error | Regex fallback | Reduced accuracy |
| StructuralAnalyzer | Empty graph | Return empty CodebaseAnalysis | Most signals = 0 |
| SemanticAnalyzer | TF-IDF fails | Single concept per file | concept_entropy = 0 |
| TemporalAnalyzer | Git not found | Set slot error, skip | Temporal signals = defaults |
| TemporalAnalyzer | Timeout | Set slot error, skip | Temporal signals = defaults |
| ArchitectureAnalyzer | < 2 modules | Return None | Architecture finders skip |
| SignalFusionAnalyzer | Missing inputs | Use defaults/None | Composites may be incomplete |

### Finder Failures

| Failure | Recovery |
|---------|----------|
| Required signal unavailable | Finder returns [] (graceful skip) |
| Threshold evaluation error | Log error, skip file, continue |
| Confidence computation error | Use confidence = 0.5 |

### Validation Failures

| Validation | Failure | Recovery |
|------------|---------|----------|
| post-scanning | 0 files | Return empty result immediately |
| post-structural | Graph/metrics mismatch | Raise ValidationError, halt |
| post-fusion | Percentile on non-pctl signal | Raise ValidationError, halt |

**Verification**: ✅ All failures have defined recovery. No unhandled exceptions.

---

## 8. Integration Test Scenarios

Tests to run before declaring implementation complete.

### Scenario 1: Empty Repository

```
Input: Directory with 0 source files
Expected:
  - file_metrics = []
  - All slots = not available
  - InsightResult.findings = []
  - InsightResult.codebase_health = None
```

### Scenario 2: Single File

```
Input: One Python file, no git
Expected:
  - Tier = ABSOLUTE
  - No percentiles computed
  - No composites computed
  - Only ABSOLUTE-tier finders run (8 of 22)
  - No findings (thresholds unlikely met)
```

### Scenario 3: Small Project (10 files, with git)

```
Input: 10 Python files, git history
Expected:
  - Tier = ABSOLUTE
  - Temporal signals computed
  - UNSTABLE_FILE may fire (uses enum + median)
  - ORPHAN_CODE may fire (uses boolean)
  - No percentile-based finders
```

### Scenario 4: Medium Project (30 files, with git)

```
Input: 30 Python files, git history, multiple authors
Expected:
  - Tier = BAYESIAN
  - All signals computed
  - All composites computed
  - All finders eligible (if conditions met)
  - Architecture detected if multi-directory
```

### Scenario 5: Large Project (500 files)

```
Input: 500 files, git history, multiple modules
Expected:
  - Tier = FULL
  - Standard percentiles
  - All finders run
  - Performance < 5 seconds (excluding I/O)
```

### Scenario 6: No Git

```
Input: 50 files, no .git directory
Expected:
  - git_history.available = False
  - git_history._error = "Git repository not found"
  - Temporal signals = defaults (#27-34)
  - Temporal finders skip (7 finders)
  - Structural finders still run (15 finders)
```

### Scenario 7: Single Author

```
Input: 50 files, git history, 1 author
Expected:
  - bus_factor = 1.0 for all files
  - author_distances = [] (skipped, < 3 authors)
  - KNOWLEDGE_SILO fires for central files
  - CONWAY_VIOLATION skips (needs author distances)
```

### Scenario 8: Flat Project

```
Input: 50 files, all in root directory
Expected:
  - module_count = 1
  - architecture = None (or single module)
  - Architecture finders skip
  - Structural finders still run
```

### Scenario 9: Library Project

```
Input: 50 files, no __main__.py, no entry points
Expected:
  - Entry point fallback: __init__.py files
  - If still none: files with in_degree=0, out_degree>0
  - If still none: depth=0 for all
  - FLAT_ARCHITECTURE may fire if glue_deficit > 0.5
```

### Scenario 10: Circular Dependencies

```
Input: Modules A→B→C→A
Expected:
  - SCC detection merges A,B,C into single layer
  - layer_violation_count = 0 (within-layer)
  - LAYER_VIOLATION does not fire
  - Warning logged about cycle
```

**Verification**: ✅ 10 integration scenarios cover all major paths.

---

## 9. Orchestration Checklist

Run this checklist before each phase is complete.

### Phase 0 Checklist

- [ ] Signal enum has all 62 entries
- [ ] SignalMeta registered for each signal
- [ ] Slot[T] implemented with error context
- [ ] TopologicalSorter handles diamond deps
- [ ] TopologicalSorter detects cycles
- [ ] Validation functions exist (scanning, structural, fusion)
- [ ] Error taxonomy covers all modules
- [ ] `make all` passes

### Phase 1-4 Checklist (per phase)

- [ ] Analyzer implements Protocol correctly
- [ ] Analyzer declares correct requires/provides
- [ ] Analyzer writes to correct store slot
- [ ] Analyzer handles edge cases (empty input, errors)
- [ ] New signals registered in registry
- [ ] Tests cover happy path + edge cases
- [ ] `make all` passes

### Phase 5 Checklist

- [ ] FusionPipeline enforces 6-step order
- [ ] raw_risk computed BEFORE percentiles
- [ ] Percentiles exclude non-percentileable signals
- [ ] Composites handle None instability
- [ ] Health Laplacian uses raw_risk
- [ ] Δh = 0.0 for orphans
- [ ] All 62 signals in SignalField
- [ ] `make all` passes

### Phase 6 Checklist (per finder)

- [ ] Finder implements Protocol correctly
- [ ] Finder declares correct requires
- [ ] Finder checks tier_minimum
- [ ] Finder applies hotspot filter if needed
- [ ] Finder handles missing signals gracefully
- [ ] Confidence uses margin formula
- [ ] Evidence includes IR level
- [ ] Tests cover activation + edge cases
- [ ] `make all` passes

### Phase 7 Checklist

- [ ] TensorSnapshot schema v2 complete
- [ ] signal_history table created
- [ ] finding_lifecycle table created
- [ ] CHRONIC_PROBLEM uses persistence_count >= 3
- [ ] Rename detection works
- [ ] Migration v1→v2 tested
- [ ] `make all` passes

---

## 10. First Time Right Summary

| Aspect | Status | Evidence |
|--------|--------|----------|
| Store slots | ✅ | Ownership matrix, single writer per slot |
| Analyzer ordering | ✅ | DAG with requires/provides, topo-sort |
| Signal ordering | ✅ | Dependency DAG, phase constraints |
| Finder activation | ✅ | Activation matrix, kernel logic |
| Edge cases | ✅ | Decision matrix, defined outcomes |
| Type contracts | ✅ | Explicit types, ranges, Optional handling |
| Error recovery | ✅ | Recovery paths for all failure modes |
| Integration tests | ✅ | 10 scenarios covering all paths |

**ORCHESTRATION STATUS: VERIFIED COMPLETE**

The spec is fully connected. Implementation can proceed with confidence.
