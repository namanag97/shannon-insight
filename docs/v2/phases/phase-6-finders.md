# Phase 6: New Finders

## Goal

Implement the 15 new finding types from `registry/finders.md`. All finders read from `SignalField` (Phase 5). Finders are grouped into three batches by signal dependency — each batch is independently shippable.

## Packages Touched

- `insights/finders/` — 15 new finder files
- `insights/finders/__init__.py` — register new finders in `get_default_finders()`
- `insights/models.py` — add `confidence` field to `Finding`

## Prerequisites

- Phase 5 complete (SignalField with percentiles and composites)
- Phase 3 complete (clone pairs, orphan detection, depth, G5 distances)
- Phase 4 complete (architecture signals, layer violations)

## Changes

### Modified: `insights/models.py`

Add confidence to Finding:

```python
@dataclass
class Finding:
    finding_type: str
    severity: float
    title: str
    files: List[str]
    evidence: List[Evidence]
    suggestion: str
    confidence: float = 1.0    # NEW: 0.0-1.0, how sure we are
    effort: str = "MEDIUM"     # NEW: LOW | MEDIUM | HIGH
    scope: str = "FILE"        # NEW: FILE | FILE_PAIR | MODULE | MODULE_PAIR | CODEBASE
```

### Hotspot Filter

For FILE-scope findings that use temporal signals, apply a hotspot filter before emitting:

```python
def passes_hotspot_filter(fs: FileSignals, finding_type: str, field: SignalField) -> bool:
    """Only flag files that are actively being worked on.

    Per registry/finders.md: temporal-aware findings require total_changes > median.
    """
    STRUCTURAL_ONLY = {"orphan_code", "hollow_code", "phantom_imports",
                       "copy_paste_clone", "flat_architecture", "naming_drift"}
    if finding_type in STRUCTURAL_ONLY:
        return True  # structural problems regardless of change frequency

    # Compute median total_changes across all files
    all_changes = [f.total_changes for f in field.per_file.values()]
    median_changes = sorted(all_changes)[len(all_changes) // 2] if all_changes else 0
    return fs.total_changes > median_changes
```

Rationale (from CodeScene research): flagging complex-but-stable files wastes developer attention. Only flag code that is both problematic AND actively changing. The median threshold ensures we only flag the more active half of the codebase.

### Batch 1: Structural Finders (need Phase 3 signals)

These finders have simple predicates on signals already available.

#### `finders/orphan_code.py` — ORPHAN_CODE

```python
class OrphanCodeFinder:
    name = "orphan_code"
    requires = {"signal_field"}

    def find(self, store):
        for f, fs in store.signal_field.per_file.items():
            if fs.is_orphan:
                yield Finding(
                    finding_type="orphan_code",
                    severity=0.55,
                    files=[f],
                    evidence=[
                        Evidence("in_degree", fs.in_degree, 0.0, "No files import this"),
                        Evidence("role", fs.role, 0.0, f"Classified as {fs.role}"),
                        Evidence("depth", fs.depth, 0.0, "Unreachable from entry points"),
                    ],
                    suggestion="Wire into dependency graph or remove if unused.",
                    effort="LOW",
                    scope="FILE",
                )
```

#### `finders/hollow_code.py` — HOLLOW_CODE

```
Condition: stub_ratio > 0.5 AND impl_gini > 0.6
Severity: 0.71
Evidence: stub_ratio, impl_gini, function list with body sizes
```

#### `finders/phantom_imports.py` — PHANTOM_IMPORTS

```
Condition: phantom_import_count > 0
Severity: 0.65
Evidence: unresolved import names, phantom_import_count
```

#### `finders/copy_paste_clone.py` — COPY_PASTE_CLONE

```
Condition: NCD(A, B) < 0.3 (from store.clone_pairs)
Severity: 0.50
Scope: FILE_PAIR
Evidence: NCD score, file sizes
```

#### `finders/flat_architecture.py` — FLAT_ARCHITECTURE

```
Condition: max(depth) <= 1 AND glue_deficit > 0.5
Severity: 0.60
Scope: CODEBASE (only one finding per run)
Evidence: max depth, glue_deficit, orphan_ratio
```

#### `finders/naming_drift.py` — NAMING_DRIFT

```
Condition: naming_drift > 0.7
Severity: 0.45
Evidence: naming_drift score, filename vs content concepts
```

**Batch 1 total: 6 finders, ~300 lines**

### Batch 2: Architecture Finders (need Phase 4 signals)

#### `finders/layer_violation.py` — LAYER_VIOLATION

```python
class LayerViolationFinder:
    name = "layer_violation"
    requires = {"signal_field", "architecture"}

    def find(self, store):
        if not store.architecture:
            return
        for v in store.architecture.violations:
            yield Finding(
                finding_type="layer_violation",
                severity=0.52,
                files=[],  # module-level, not file-level
                scope="MODULE_PAIR",
                evidence=[
                    Evidence("source_layer", v.source_layer, 0, f"{v.source_module} at layer {v.source_layer}"),
                    Evidence("target_layer", v.target_layer, 0, f"{v.target_module} at layer {v.target_layer}"),
                    Evidence("violation_type", 0, 0, v.violation_type.value),
                ],
                suggestion="Inject dependency or restructure to respect layer ordering.",
                effort="MEDIUM",
            )
```

#### `finders/zone_of_pain.py` — ZONE_OF_PAIN

```
Condition: instability is not None AND abstractness < 0.3 AND instability < 0.3
Scope: MODULE
Severity: 0.60
Evidence: abstractness, instability, main_seq_distance, dependent count
```

**Important**: `instability` is `Optional[float]` — it's `None` for isolated modules (Ca=Ce=0). Without the `is not None` guard, isolated modules would incorrectly trigger this finder (since `None < 0.3` raises TypeError, or if defaulted to 0.0 would be a false positive).

#### `finders/boundary_mismatch.py` — BOUNDARY_MISMATCH (upgrade)

Existing finder. Upgrade to use `role_consistency` as additional evidence and read from `signal_field` instead of directly from `store.structural`.

```
Condition: boundary_alignment < 0.7 AND file_count >= 3 (unchanged)
New evidence: role_consistency score
```

**Batch 2 total: 3 finders (2 new + 1 upgrade), ~200 lines**

### Batch 3: Cross-Dimensional Finders (need Phase 5 composites + temporal)

#### `finders/knowledge_silo.py` — KNOWLEDGE_SILO

```
Condition: bus_factor <= 1.5 AND percentile(pagerank) > 0.75
Severity: 0.70
Evidence: bus_factor, author list, pagerank percentile
```

#### `finders/conway_violation.py` — CONWAY_VIOLATION

```
Condition: d_author(M1, M2) > 0.8 AND structural_coupling(M1, M2) > 0.3
Scope: MODULE_PAIR
Severity: 0.55
Requires: author_distances from Phase 3
Evidence: author distance, structural coupling, module names
```

Note: This operates on module pairs. Requires aggregating G5 author distance to module level (mean author distance between files in M1 and files in M2).

#### `finders/review_blindspot.py` — REVIEW_BLINDSPOT

```
Condition: percentile(pagerank) > 0.75 AND bus_factor <= 1.5 AND no test file associated
Severity: 0.80
Evidence: pagerank percentile, bus_factor, test file presence
```

Test file detection (language-aware):
- Python: test_bar.py, bar_test.py, tests/test_bar.py, tests/bar/test_bar.py
- Go: bar_test.go (same directory)
- Java: BarTest.java, BarTests.java (in test source tree)
- TypeScript/JS: bar.test.ts, bar.spec.ts, __tests__/bar.test.ts
- Rust: skip (tests are inline via #[cfg(test)])
- Ruby: bar_test.rb, test_bar.rb, spec/bar_spec.rb
If language not supported for test detection, skip this finder for that file.

#### `finders/weak_link.py` — WEAK_LINK

```
Condition: delta_h(f) > 0.4 (from health Laplacian, Phase 5)
Severity: 0.75
Evidence: delta_h value, risk_score, mean neighbor risk_score
```

#### `finders/bug_attractor.py` — BUG_ATTRACTOR

```
Condition: fix_ratio > 0.4 AND percentile(pagerank) > 0.75
Severity: 0.70
Evidence: fix_ratio, pagerank percentile, total_changes, blast_radius_size
```

#### `finders/accidental_coupling.py` — ACCIDENTAL_COUPLING

```
Condition: structural edge exists AND concept_overlap(A, B) < 0.2
    where concept_overlap = |concepts(A) ∩ concepts(B)| / |concepts(A) ∪ concepts(B)|
    Read concepts from store.semantics[path].concepts (List[Concept] with .topic attribute).
    Compute Jaccard on concept.topic sets. If concepts unavailable for either file, skip this pair.
Scope: FILE_PAIR
Severity: 0.50
Evidence: import edge, concept_overlap score, concept lists for each file
```

**Batch 3 total: 6 finders, ~400 lines**

### Finder Tier Awareness

Every finder must handle ABSOLUTE tier (< 15 files). In ABSOLUTE tier, percentile-based conditions are replaced with absolute thresholds:

| Finder | FULL/BAYESIAN condition | ABSOLUTE fallback |
|--------|------------------------|-------------------|
| HIGH_RISK_HUB | pctl(pagerank) > 0.90 | pagerank > 0.01 AND blast_radius > 20 |
| GOD_FILE | pctl(cognitive_load) > 0.90 | cognitive_load > 15 |
| KNOWLEDGE_SILO | pctl(pagerank) > 0.75 | pagerank > 0.005 |
| BUG_ATTRACTOR | pctl(pagerank) > 0.75 | pagerank > 0.005 |
| REVIEW_BLINDSPOT | pctl(pagerank) > 0.75 | pagerank > 0.005 |
| WEAK_LINK | delta_h > 0.4 | same (already absolute) |

Finders without percentile conditions (ORPHAN_CODE, PHANTOM_IMPORTS, etc.) work identically in all tiers.

### Deferred Finders

These require cross-snapshot temporal data (Phase 7 persistence):

| Finder | Why deferred |
|--------|-------------|
| CHRONIC_PROBLEM (upgrade) | Needs finding persistence across 3+ snapshots |
| ARCHITECTURE_EROSION | Needs violation_rate time series across 3+ snapshots |

They will be added after Phase 7 as a small follow-up.

### Registration

```python
# insights/finders/__init__.py
def get_default_finders():
    return [
        # Existing (Phase 0)
        HighRiskHubFinder(),
        HiddenCouplingFinder(),
        GodFileFinder(),
        UnstableFileFinder(),
        BoundaryMismatchFinder(),  # upgraded in Batch 2
        DeadDependencyFinder(),

        # Batch 1: Structural
        OrphanCodeFinder(),
        HollowCodeFinder(),
        PhantomImportsFinder(),
        CopyPasteCloneFinder(),
        FlatArchitectureFinder(),
        NamingDriftFinder(),

        # Batch 2: Architecture
        LayerViolationFinder(),
        ZoneOfPainFinder(),

        # Batch 3: Cross-dimensional
        KnowledgeSiloFinder(),
        ConwayViolationFinder(),
        ReviewBlindspotFinder(),
        WeakLinkFinder(),
        BugAttractorFinder(),
        AccidentalCouplingFinder(),
    ]
```

All finders use graceful degradation: if `store.signal_field` is None or required signals are missing, the finder returns an empty list.

## Acceptance Criteria

### Batch 1
1. ORPHAN_CODE fires for a file with in_degree=0 and role=UTILITY
2. ORPHAN_CODE does NOT fire for files with role=ENTRY_POINT or TEST
3. HOLLOW_CODE fires for a file with 60% stubs and high Gini
4. PHANTOM_IMPORTS fires for a file importing a non-existent module
5. COPY_PASTE_CLONE fires for two near-identical test fixtures
6. FLAT_ARCHITECTURE fires for a project with max_depth=1 and glue_deficit > 0.5
7. NAMING_DRIFT fires for a file named `utils.py` containing only auth logic

### Batch 2
8. LAYER_VIOLATION fires for a known backward dependency in test fixture
9. ZONE_OF_PAIN fires for a concrete, stable module (low A, low I)
10. BOUNDARY_MISMATCH upgrade shows role_consistency in evidence

### Batch 3
11. KNOWLEDGE_SILO fires for a high-pagerank file with bus_factor = 1
12. REVIEW_BLINDSPOT fires for high-centrality, single-author, untested file
13. WEAK_LINK fires for a file with delta_h > 0.4
14. BUG_ATTRACTOR fires for a file with fix_ratio > 0.4 and high centrality
15. All existing tests pass — existing finders unaffected

### Global
16. Finding count is reasonable: running on Shannon Insight's own codebase should produce 5-20 findings, not 0 or 100+
17. No finder crashes on edge cases (empty codebase, single file, no git)

### Finding Grouping

To prevent output dominated by one finder type:
- Group FILE-scope findings of same type: if ORPHAN_CODE fires for 20 files, emit ONE finding with `files=[all 20]`
- Cap: max 3 grouped findings per type before filling with other types
- Ranking: sort grouped findings by max(severity across instances)
- Implement in `insights/ranking.py`, not in individual finders

## Estimated Scope

- 15 new finder files + registration changes
- 1 modified model file
- ~900 lines of new code
- ~2.5 weeks (batch 1: 1 week, batch 2: 0.5 weeks, batch 3: 1 week)
