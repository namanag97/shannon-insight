# Shannon Insight v2 — Developer Implementation Guide

> **ENTERPRISE-GRADE PRODUCTION SOFTWARE**
>
> This guide provides step-by-step implementation instructions for each phase.
> Read SPEC-REFERENCE.md first for architecture overview, then use this for daily development.

---

## Quick Start Checklist

Before writing any code, verify:

- [ ] Read `SPEC-REFERENCE.md` (architecture, signals, finders)
- [ ] Read `infrastructure.md` (8 patterns to build first)
- [ ] Read `FINDER-REHEARSAL.md` (22 finder data flows)
- [ ] Read `SIGNAL-REHEARSAL.md` (62 signal data flows)
- [ ] Run `make all` to verify tests pass

---

## Phase 0: Infrastructure Patterns (~1 week)

### Deliverables

| Pattern | File | Lines | Test File |
|---------|------|-------|-----------|
| Protocol contracts | `insights/protocols.py` | ~50 | `tests/test_protocols.py` |
| Signal enum + registry | `signals/registry.py` | ~120 | `tests/signals/test_registry.py` |
| Typed Slot[T] store | `insights/store.py` | ~40 | `tests/test_store.py` |
| graphlib topo-sort | `insights/kernel.py` | ~30 | `tests/test_kernel_ordering.py` |
| Phase validation | `insights/validation.py` | ~80 | `tests/test_validation.py` |
| Fusion pipeline builder | `signals/fusion.py` | ~60 | `tests/signals/test_fusion.py` |
| ThresholdStrategy | `insights/threshold.py` | ~25 | `tests/test_threshold.py` |
| Error taxonomy | `exceptions/taxonomy.py` | ~90 | `tests/test_exceptions.py` |

### Test-First Development

For each pattern:

1. **Write test file first**
```python
# tests/signals/test_registry.py
def test_signal_enum_has_all_62_signals():
    """Signal enum must define all 62 signals."""
    assert len(Signal) == 62

def test_duplicate_producer_raises():
    """Same signal registered by two producers must raise."""
    register(SignalMeta(Signal.PAGERANK, float, "file", True, "high_is_bad", None, "graph/algorithms", 0))
    with pytest.raises(ValueError, match="already registered"):
        register(SignalMeta(Signal.PAGERANK, float, "file", True, "high_is_bad", None, "other/module", 0))

def test_percentileable_signals_excludes_enums():
    """Enum signals must not be in percentileable set."""
    pctl = percentileable_signals()
    assert Signal.ROLE not in pctl
    assert Signal.CHURN_TRAJECTORY not in pctl
    assert Signal.COMMUNITY not in pctl
```

2. **Implement until tests pass**
3. **Run `make all`**

### Acceptance Criteria

- [ ] All 62 signals registered with correct metadata
- [ ] Analyzer topo-sort handles diamond dependencies
- [ ] Analyzer topo-sort detects cycles with clear error
- [ ] Slot[T] wrapper provides error context
- [ ] Validation catches mismatched adjacency/reverse
- [ ] Fusion pipeline enforces step ordering (type errors if wrong)
- [ ] ThresholdStrategy handles all 3 tiers
- [ ] Error codes match `taxonomy.py` definitions

---

## Phase 1: Tree-sitter Parsing (~3 weeks)

### New Files

| File | Purpose | Lines |
|------|---------|-------|
| `scanning/treesitter_parser.py` | Core parser wrapper | ~150 |
| `scanning/queries/python.py` | Python tree-sitter queries | ~60 |
| `scanning/queries/javascript.py` | JS/TS queries | ~60 |
| `scanning/queries/go.py` | Go queries | ~60 |
| `scanning/queries/java.py` | Java queries | ~60 |
| `scanning/queries/rust.py` | Rust queries | ~60 |
| `scanning/queries/ruby.py` | Ruby queries | ~60 |
| `scanning/queries/c.py` | C/C++ queries | ~60 |
| `scanning/normalizer.py` | Captures → FileSyntax | ~100 |
| `scanning/fallback.py` | Regex fallback | ~80 |

### Modified Files

| File | Changes |
|------|---------|
| `scanning/models.py` | Add `FunctionDef.body_tokens`, `FunctionDef.calls[]`, `FileSyntax.has_main_guard` |
| `scanning/factory.py` | Route to tree-sitter or regex based on config |

### Key Implementation Notes

```python
# scanning/treesitter_parser.py
import tree_sitter_languages

def parse(content: str, language: str) -> tree_sitter.Tree:
    """Parse source code using tree-sitter."""
    parser = tree_sitter_languages.get_parser(language)
    return parser.parse(content.encode())

def extract_functions(tree: tree_sitter.Tree, language: str) -> List[FunctionDef]:
    """Extract function definitions using language-specific queries."""
    query = QUERIES[language]["function"]
    captures = query.captures(tree.root_node)
    return [_capture_to_function_def(c) for c in captures]
```

### Acceptance Criteria

- [ ] Python function extraction matches manual count on test_codebase/
- [ ] Function body_tokens count excludes comments and docstrings
- [ ] max_nesting computed correctly for nested if/for/try blocks
- [ ] stub_ratio formula: `1 - min(1, body_tokens / (signature_tokens × 3))`
- [ ] impl_gini uses Gini formula from signals.md
- [ ] Regex fallback activates when tree-sitter fails
- [ ] Track fallback rate: warn if > 20%

---

## Phase 2: Semantics Package (~2 weeks)

### New Files

| File | Purpose | Lines |
|------|---------|-------|
| `semantics/models.py` | FileSemantics, Role, Concept | ~80 |
| `semantics/analyzer.py` | SemanticAnalyzer | ~60 |
| `semantics/roles.py` | Role decision tree | ~100 |
| `semantics/concepts.py` | TF-IDF + Louvain | ~150 |
| `semantics/naming.py` | Naming drift | ~50 |
| `semantics/completeness.py` | TODO density, docstring coverage | ~50 |

### Role Classification Decision Tree

```python
# semantics/roles.py
def classify_role(syntax: FileSyntax) -> Role:
    """First-match-wins priority classification."""
    path = syntax.path.lower()

    # Priority 1: Explicit patterns
    if path.endswith("_test.py") or "/test_" in path or "/tests/" in path:
        return Role.TEST
    if path.endswith("__main__.py") or syntax.has_main_guard:
        return Role.ENTRY_POINT
    if path.endswith("conftest.py"):
        return Role.CONFIG
    if "exception" in path or _all_classes_inherit_exception(syntax):
        return Role.EXCEPTION

    # Priority 2: Structural patterns
    if syntax.class_count > 0 and syntax.function_count == 0:
        return Role.MODEL
    if syntax.function_count > 0 and syntax.class_count == 0:
        if "service" in path or "handler" in path:
            return Role.SERVICE
        return Role.UTILITY

    # Priority 3: Content patterns
    if _is_interface(syntax):
        return Role.INTERFACE
    if _is_config(syntax):
        return Role.CONFIG

    return Role.UNKNOWN
```

### Acceptance Criteria

- [ ] Role classification covers all 12 roles
- [ ] Concept extraction uses 3-tier strategy (10+, 3-9, <3 functions)
- [ ] Louvain on token co-occurrence produces stable clusters (sort nodes)
- [ ] naming_drift = 0.0 for generic filenames
- [ ] todo_density counts TODO, FIXME, HACK patterns
- [ ] docstring_coverage = documented / total public symbols

---

## Phase 3: Graph Enrichment (~1.5 weeks)

### Modified Files

| File | Changes |
|------|---------|
| `graph/models.py` | Add `depth`, `is_orphan`, `ClonePair`, `AuthorDistance` |
| `graph/algorithms.py` | Add `compute_dag_depth()`, `compute_orphans()`, `centrality_gini()` |

### New Files

| File | Purpose | Lines |
|------|---------|-------|
| `graph/clone_detection.py` | MinHash + NCD | ~120 |
| `graph/distance.py` | G5 author distance | ~80 |

### Key Implementation Notes

```python
# graph/algorithms.py
def compute_dag_depth(graph: DependencyGraph, roles: Dict[str, str]) -> Dict[str, int]:
    """
    BFS from entry points. Returns shortest path distance.
    Fallback chain if no entry points:
    1. Files with role=ENTRY_POINT
    2. __init__.py files
    3. Files with in_degree=0 and out_degree>0
    4. All files get depth=0
    """
    entry_points = [p for p, r in roles.items() if r == "ENTRY_POINT"]
    if not entry_points:
        entry_points = [p for p in graph.nodes if p.endswith("__init__.py")]
    if not entry_points:
        entry_points = [p for p in graph.nodes
                        if graph.in_degree(p) == 0 and graph.out_degree(p) > 0]
    if not entry_points:
        return {p: 0 for p in graph.nodes}

    return _bfs_depths(graph, entry_points)

def compute_orphans(graph: DependencyGraph, roles: Dict[str, str]) -> Set[str]:
    """Orphan = in_degree=0 AND role ∉ {ENTRY_POINT, TEST}."""
    return {
        p for p in graph.nodes
        if graph.in_degree(p) == 0
        and roles.get(p) not in {"ENTRY_POINT", "TEST"}
    }
```

### Acceptance Criteria

- [ ] depth correctly computed: entry points get depth=0, imports get depth=1
- [ ] depth=-1 for unreachable files (or use orphan detection)
- [ ] NCD clone detection threshold = 0.3
- [ ] NCD uses adaptive strategy: pairwise < 1000 files, LSH ≥ 1000
- [ ] G5 author distance computed for pairs sharing ≥1 author
- [ ] centrality_gini uses correct Gini formula

---

## Phase 4: Architecture Package (~2 weeks)

### New Files

| File | Purpose | Lines |
|------|---------|-------|
| `architecture/models.py` | Architecture, Module, Layer, Violation | ~100 |
| `architecture/analyzer.py` | ArchitectureAnalyzer | ~60 |
| `architecture/modules.py` | Module detection | ~100 |
| `architecture/metrics.py` | Martin metrics | ~80 |
| `architecture/layers.py` | Topological layer inference | ~80 |

### Key Implementation Notes

```python
# architecture/metrics.py
def compute_instability(ca: int, ce: int) -> Optional[float]:
    """
    Martin's Instability = Ce / (Ca + Ce).
    Returns None if Ca + Ce = 0 (isolated module).
    """
    total = ca + ce
    if total == 0:
        return None  # CRITICAL: not 0.0, not 0.5, but None
    return ce / total

def compute_main_seq_distance(abstractness: float, instability: Optional[float]) -> Optional[float]:
    """
    D = |A + I - 1|.
    Returns None if instability is None.
    """
    if instability is None:
        return None
    return abs(abstractness + instability - 1)
```

### Acceptance Criteria

- [ ] Module detection uses directory boundaries (fallback to Louvain)
- [ ] instability = None when Ca+Ce = 0
- [ ] main_seq_distance guards instability=None
- [ ] Layer inference uses topological sort
- [ ] Cyclic modules merged into single layer
- [ ] ZONE_OF_PAIN finder checks `instability is not None`

---

## Phase 5: Signal Fusion (~2 weeks)

### New/Modified Files

| File | Purpose | Lines |
|------|---------|-------|
| `signals/models.py` | FileSignals, ModuleSignals, GlobalSignals, SignalField | ~150 |
| `signals/fusion.py` | SignalFusionAnalyzer (8-step pipeline) | ~200 |
| `signals/normalization.py` | Tiered percentile computation | ~80 |
| `signals/composites.py` | All composite formulas | ~150 |
| `signals/health_laplacian.py` | Δh computation | ~60 |
| `signals/analyzer.py` | SignalFusionAnalyzer (run_last=True) | ~40 |

### 8-Step Pipeline

```python
# signals/fusion.py
def build(store: AnalysisStore) -> SignalField:
    """The ONLY valid call order. Enforced by typestate pattern."""
    return (FusionPipeline(store)
        .step1_collect()       # Gather raw signals from all store slots
        .step2_raw_risk()      # Compute raw_risk for Laplacian (before percentiles)
        .step3_normalize()     # Compute percentiles (skip in ABSOLUTE tier)
        .step4_module_temporal() # Fill module temporal signals (needs percentiles)
        .step5_composites()    # Compute risk_score, health_score, etc.
        .step6_laplacian())    # Compute Δh using raw_risk
```

### Acceptance Criteria

- [ ] All 62 signals collected into SignalField
- [ ] Tier detection: < 15 → ABSOLUTE, 15-50 → BAYESIAN, 50+ → FULL
- [ ] ABSOLUTE tier: no percentiles, no composites
- [ ] Percentile formula: `|{v: S(v) ≤ S(f)}| / |all_files|`
- [ ] Composite weights sum to 1.0
- [ ] Weight redistribution when instability=None
- [ ] Health Laplacian uses raw_risk, not risk_score
- [ ] Δh = 0.0 for orphan files

---

## Phase 6: New Finders (~2.5 weeks)

### Batch 1: AI Code Quality (6 finders)

| Finder | File | Key Signals |
|--------|------|-------------|
| ORPHAN_CODE | `finders/orphan.py` | #20 is_orphan |
| HOLLOW_CODE | `finders/hollow.py` | #5 impl_gini, #6 stub_ratio |
| PHANTOM_IMPORTS | `finders/phantom.py` | #21 phantom_import_count |
| COPY_PASTE_CLONE | `finders/clone.py` | clone_pairs |
| FLAT_ARCHITECTURE | `finders/flat.py` | #19 depth, #59 glue_deficit |
| NAMING_DRIFT | `finders/naming.py` | #11 naming_drift |

### Batch 2: Social/Team (3 finders)

| Finder | File | Key Signals |
|--------|------|-------------|
| KNOWLEDGE_SILO | `finders/silo.py` | #31 bus_factor, #14 pagerank |
| CONWAY_VIOLATION | `finders/conway.py` | author_distances, architecture |
| REVIEW_BLINDSPOT | `finders/blindspot.py` | #14 pagerank, #31 bus_factor |

### Batch 3: Architecture (3 finders)

| Finder | File | Key Signals |
|--------|------|-------------|
| LAYER_VIOLATION | `finders/layer.py` | architecture.violations |
| ZONE_OF_PAIN | `finders/zone.py` | #39 instability, #40 abstractness |
| ARCHITECTURE_EROSION | `finders/erosion.py` | finding_history |

### Batch 4: Cross-Dimensional (3 finders)

| Finder | File | Key Signals |
|--------|------|-------------|
| WEAK_LINK | `finders/weak.py` | delta_h, #35 raw_risk |
| BUG_ATTRACTOR | `finders/bug.py` | #33 fix_ratio, #14 pagerank |
| ACCIDENTAL_COUPLING | `finders/accidental.py` | semantics.concepts, structural edges |

### Finder Template

```python
# finders/zone.py
from insights.protocols import Finder
from insights.threshold import ThresholdCheck
from signals.registry import Signal, REGISTRY

class ZoneOfPainFinder:
    name = "zone_of_pain"
    api_version = "2.0"
    requires = {"architecture", "signal_field"}
    error_mode = "skip"
    hotspot_filtered = False
    tier_minimum = "BAYESIAN"

    def find(self, store):
        if not store.architecture.available:
            return []

        findings = []
        for mod_path, mod in store.architecture.value.modules.items():
            # CRITICAL: guard for None instability
            if mod.instability is None:
                continue

            if mod.abstractness < 0.3 and mod.instability < 0.3:
                findings.append(Finding(
                    type="ZONE_OF_PAIN",
                    scope="MODULE",
                    targets=[mod_path],
                    severity=0.60,
                    confidence=self._compute_confidence(mod),
                    evidence=self._build_evidence(mod),
                    suggestion="Concrete and stable — hard to change. Extract interfaces.",
                ))
        return findings

    def _compute_confidence(self, mod) -> float:
        # Margin formula for A < 0.3 and I < 0.3
        margin_a = (0.3 - mod.abstractness) / 0.3
        margin_i = (0.3 - mod.instability) / 0.3
        return (margin_a + margin_i) / 2
```

### Acceptance Criteria

- [ ] All 15 new finders implemented
- [ ] Each finder respects tier_minimum
- [ ] Hotspot-filtered finders check `total_changes > median`
- [ ] Confidence uses margin formula
- [ ] Evidence includes IR level and signal values
- [ ] Finding grouping: max 3 per type for FILE scope

---

## Phase 7: Persistence V2 (~2 weeks)

### Modified Files

| File | Changes |
|------|---------|
| `persistence/models.py` | TensorSnapshot (schema v2) |
| `persistence/database.py` | signal_history, finding_lifecycle tables |

### Key Implementation Notes

```python
# persistence/models.py
@dataclass
class TensorSnapshot:
    version: str = "2.0"
    timestamp: str  # ISO 8601
    config_hash: str  # Hash of AnalysisSettings
    file_data: Dict[str, FileData]
    module_data: Dict[str, ModuleData]
    global_data: GlobalData
    graph_data: GraphData
    arch_data: Optional[ArchData]
    temporal_data: Optional[TemporalData]
    findings: List[Finding]
    timing: Dict[str, float]  # Per-IR timing breakdown
```

### Acceptance Criteria

- [ ] TensorSnapshot schema v2 includes all signals
- [ ] signal_history enables time-series queries
- [ ] finding_lifecycle tracks first_seen, persistence_count
- [ ] CHRONIC_PROBLEM fires for 3+ consecutive snapshots
- [ ] Rename detection via git tracking
- [ ] Migration v1 → v2 preserves existing data

---

## Development Workflow

### Daily Rhythm

1. **Morning**: Pick next item from phase checklist
2. **Write test first**: Create test file before implementation
3. **Implement**: Write minimal code to pass tests
4. **Validate**: Run `make all`
5. **Commit**: Small, focused commits with phase prefix

### Commit Message Format

```
[Phase N] Description

- What changed
- Why it changed

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### PR Checklist

- [ ] Tests pass: `make test`
- [ ] Types check: `make check` (mypy)
- [ ] Format clean: `make format` (ruff)
- [ ] No new warnings
- [ ] Acceptance criteria met
- [ ] SPEC-REFERENCE.md matches implementation

---

## Troubleshooting

### "Signal not found in registry"

```python
# Ensure signal is registered in signals/registry.py
register(SignalMeta(Signal.YOUR_SIGNAL, float, "file", True, "high_is_bad", None, "your/module", 3))
```

### "Analyzer dependency cycle detected"

```python
# Check requires/provides don't form a cycle
# Use graphlib.TopologicalSorter error message to identify cycle
```

### "Slot not populated"

```python
# Check analyzer that should populate it ran before consumer
# Check analyzer didn't fail (look for error in slot._error)
```

### "Finder skipped but expected to fire"

```python
# Check tier: finder may need BAYESIAN but you're in ABSOLUTE
# Check hotspot filter: total_changes may be below median
# Check required signals: store.signal_field may be missing data
```

---

## Reference Links

| Document | Purpose |
|----------|---------|
| `SPEC-REFERENCE.md` | Architecture, all signals, all finders |
| `infrastructure.md` | 8 hardening patterns |
| `FINDER-REHEARSAL.md` | 22 finder data flows |
| `SIGNAL-REHEARSAL.md` | 62 signal data flows |
| `registry/signals.md` | Signal definitions, formulas, edge cases |
| `registry/finders.md` | Finder conditions, tiers, confidence |
| `registry/composites.md` | Composite formulas, weight redistribution |
| `01-contracts.md` | Module dependencies, data flow |
| `phases/phase-N-*.md` | Detailed phase specs |
