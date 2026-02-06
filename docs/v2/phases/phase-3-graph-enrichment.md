# Phase 3: Graph Enrichment

## Goal

Extend the dependency graph with new signal computations, clone detection, and the author distance space — turning the graph from import-only into a multi-signal analysis layer.

This phase does NOT add CALL or TYPE_FLOW edges (those require cross-function resolution that is Phase 3b/future work). It focuses on signals computable from existing IMPORT edges + Phase 1/2 outputs.

## Packages Touched

- `graph/models.py` — add fields to `GraphAnalysis` and `FileAnalysis`
- `graph/algorithms.py` — add DAG depth, centrality Gini, orphan detection
- `graph/engine.py` — wire new computations into `AnalysisEngine`
- `graph/clone_detection.py` — **new file**: NCD-based clone pair detection
- `graph/distance.py` — **new file**: G5 author distance computation
- `insights/store.py` — expose new signals
- `insights/analyzers/structural.py` — pass new data to store

## Prerequisites

- Phase 1 complete (tree-sitter `FileSyntax` with accurate function counts, nesting)
- Phase 2 complete (`role` classification for orphan exclusion of ENTRY_POINT/TEST)

## Changes

### Modified: `graph/models.py`

Add to `GraphAnalysis`:

```python
@dataclass
class GraphAnalysis:
    # ... existing fields ...

    # Phase 3 additions:
    depth: Dict[str, int] = field(default_factory=dict)            # BFS depth from entry points, -1 = unreachable
    is_orphan: Dict[str, bool] = field(default_factory=dict)       # in_degree=0 AND not entry_point/test
    centrality_gini: float = 0.0                                    # Gini of pagerank distribution
    spectral_gap: float = 0.0                                       # λ₂/λ₃ (move from SpectralSummary)
```

Add to `FileAnalysis`:

```python
@dataclass
class FileAnalysis:
    # ... existing fields ...

    # Phase 3 additions:
    depth: int = -1
    is_orphan: bool = False
    phantom_import_count: int = 0
```

Add new models:

```python
@dataclass
class ClonePair:
    file_a: str
    file_b: str
    ncd: float              # Normalized Compression Distance, lower = more similar
    size_a: int             # bytes
    size_b: int

@dataclass
class AuthorDistance:
    """G5 distance space entry."""
    file_a: str
    file_b: str
    distance: float         # 1 - weighted Jaccard overlap of author distributions
```

### Modified: `graph/builder.py` — Track Unresolved Imports

Currently, `build_dependency_graph` silently discards unresolved imports (returns `None` → skipped). Signal #21 `phantom_import_count` requires counting these.

```python
def build_dependency_graph(file_metrics, ...) -> DependencyGraph:
    adjacency = defaultdict(list)
    unresolved: Dict[str, List[str]] = defaultdict(list)  # NEW

    for fm in file_metrics:
        for imp in fm.imports:
            resolved = _resolve_import(imp, fm.path, path_index, all_paths)
            if resolved and resolved != fm.path:
                adjacency[fm.path].append(resolved)
            elif resolved is None:
                unresolved[fm.path].append(imp)  # NEW: track what failed

    return DependencyGraph(
        adjacency=adjacency,
        unresolved_imports=unresolved,  # NEW field
        ...
    )
```

Add to `DependencyGraph`:
```python
@dataclass
class DependencyGraph:
    # ... existing ...
    unresolved_imports: Dict[str, List[str]] = field(default_factory=dict)
```

This feeds `phantom_import_count` (per-file) and `phantom_ratio` (global).

### Modified: `temporal/git_extractor.py` — Add Commit Subject

The git log format is currently `%H|%at|%ae` (hash, timestamp, author email). Signals #33 `fix_ratio` and #34 `refactor_ratio` require matching keywords in commit messages ("fix", "bug", "refactor", etc.).

**Change**: Add `%s` (subject) to the git log format:
```
# Before:
format = "%H|%at|%ae"

# After:
format = "%H|%at|%ae|%s"
```

Add `subject: str = ""` field to `Commit` model.

**Parsing rule**: Commit subjects can contain `|` characters (e.g., `"fix auth | update deps"`). Parse with `line.split("|", maxsplit=3)` — everything after the third `|` is the subject. Do NOT use unbounded `split("|")`.

**Keyword classification** (used by Phase 5 SignalFusion to compute fix_ratio/refactor_ratio):
- **fix keywords**: `fix`, `bug`, `patch`, `hotfix`, `issue`, `resolve`, `correct`
- **refactor keywords**: `refactor`, `restructure`, `reorganize`, `clean up`, `simplify`, `extract`
- Match is case-insensitive substring on the commit subject.

### Modified: `temporal/churn.py` — Store Computed Values

`churn_cv` is currently computed in `_classify_trajectory()` but discarded (used as local variable for classification logic only). Additional per-file temporal signals need to be stored.

Add to `ChurnSeries`:
```python
@dataclass
class ChurnSeries:
    # ... existing fields ...

    # Phase 3 additions:
    cv: float = 0.0              # Coefficient of variation (was computed but discarded)
    bus_factor: float = 1.0      # 2^H where H = Shannon entropy of author distribution
    author_entropy: float = 0.0  # Shannon entropy of per-file author commit distribution
    fix_ratio: float = 0.0       # fraction of commits with fix keywords in subject
    refactor_ratio: float = 0.0  # fraction of commits with refactor keywords in subject
```

**bus_factor computation**: For each file, count commits per author → compute Shannon entropy H → bus_factor = 2^H. If single author, H=0, bus_factor=1.

**Requires**: `git_history.commits` with per-commit file lists AND the new `subject` field for fix/refactor classification.

### New: `graph/clone_detection.py`

NCD-based clone detection with adaptive strategy:

```
Algorithm (adaptive by codebase size):

IF file_count < 1000:
  # Direct pairwise — 125K zlib compressions for 500 files ≈ 1-2s. No LSH overhead.
  1. For all (i,j) pairs where i < j:
     NCD(i,j) = (C(ij) - min(C(i), C(j))) / max(C(i), C(j))
     where C(z) = len(zlib.compress(z, level=6))
  2. Return pairs where NCD < 0.3

ELSE (file_count >= 1000):
  # MinHash+LSH pre-filter to avoid O(n²) blowup
  1. For each file, compute MinHash signature (128 permutations) from 4-gram shingles
  2. Use LSH (b=32 bands, r=4 rows) to find candidate pairs
     # b=32, r=4 gives P(candidate | Jaccard=0.5) ≈ 0.87
     # Previous b=8, r=16 was WRONG — gave threshold ~0.88, missing most clones
  3. For candidate pairs only, compute exact NCD (same formula as above)
  4. Return pairs where NCD < 0.3
```

**Clone threshold: NCD < 0.3** — stores all pairs below this. Finders can tighten further. Severity scales inversely with NCD (lower = more severe).

**Exclusion rules**: Skip file pairs where BOTH files have role=TEST or role=MIGRATION. These share structural patterns (setup/teardown, migration boilerplate) that trigger false positives.

**Performance target**: < 2 seconds for 500 files (direct pairwise), < 5 seconds for 2000 files (LSH).

**Signals produced**: `clone_ratio` (global) = `|files in any clone pair| / |total files|`

### New: `graph/distance.py`

G5 author distance space:

```python
def compute_author_distances(
    git_history: GitHistory,
    analyzed_files: Set[str],
) -> List[AuthorDistance]:
    """Weighted Jaccard distance between author distributions.

    Only compute for file pairs that share at least one author
    (sparse — skip pairs with distance = 1.0).
    """
    # Step 1: Build per-file author distribution
    # author_weights[file][author] = commits_by_author / total_commits_on_file

    # Step 2: For each pair sharing an author:
    # d(A,B) = 1 - Σ_a min(w_a(A), w_a(B)) / Σ_a max(w_a(A), w_a(B))

    # Step 3: Return sparse list (only pairs with distance < 1.0)
```

**Input**: `GitHistory` from temporal/ (already available).
**Performance**: Sparse computation — only pairs sharing authors. Typically < 5% of all pairs.

**Solo project handling**: If `distinct_authors < 2`, skip G5 computation entirely. Set `author_distances = None`. Finders requiring G5 (CONWAY_VIOLATION) gracefully skip.

### Modified: `graph/algorithms.py`

Add three functions:

```python
def compute_dag_depth(
    adjacency: Dict[str, List[str]],
    entry_points: Set[str],
) -> Dict[str, int]:
    """BFS from entry points on the forward (import) graph.

    Entry point fallback chain (if entry_points is empty):
    1. Files with role=ENTRY_POINT (from Phase 2)
    2. __init__.py files that re-export (have both imports and are imported)
    3. Root importers: in_degree=0 AND out_degree>0
    4. If still empty: depth=0 for ALL files (flat project, skip depth-based finders)

    Depth = shortest path (BFS hop count) from nearest entry point.
    Files unreachable from any entry point get depth = -1.
    """

def compute_orphans(
    in_degree: Dict[str, int],
    roles: Dict[str, str],       # file -> role from Phase 2
) -> Dict[str, bool]:
    """is_orphan = in_degree == 0 AND role not in {ENTRY_POINT, TEST}"""

def compute_centrality_gini(pagerank: Dict[str, float]) -> float:
    """Gini coefficient of pagerank distribution.

    > 0.7 = hub-dominated topology
    < 0.3 = relatively flat
    Uses existing math/gini.py
    """
```

**Determinism**: Sort nodes before Louvain iteration to ensure deterministic community assignments across runs. Current implementation uses `list(all_nodes)` which depends on set ordering. Fix: `nodes = sorted(all_nodes)`.

### Modified: `graph/engine.py`

Wire new computations after existing graph algorithms:

```python
# After run_graph_algorithms():
analysis.depth = compute_dag_depth(graph.adjacency, entry_points)
analysis.is_orphan = compute_orphans(analysis.in_degree, roles)
analysis.centrality_gini = compute_centrality_gini(analysis.pagerank)
```

### Modified: `insights/store.py`

Add fields:

```python
@dataclass
class AnalysisStore:
    # ... existing ...

    # Phase 3 additions:
    clone_pairs: Optional[List[ClonePair]] = None
    author_distances: Optional[List[AuthorDistance]] = None
    roles: Optional[Dict[str, str]] = None  # file -> Role (from Phase 2 semantics)
```

Update `available` property:

```python
@property
def available(self) -> Set[str]:
    avail = {"files"}
    # ... existing checks ...
    if self.clone_pairs is not None:
        avail.add("clones")
    if self.author_distances is not None:
        avail.add("author_distances")
    if self.roles is not None:
        avail.add("roles")
    return avail
```

### Modified: `insights/analyzers/structural.py`

After graph algorithms, run:
1. `compute_dag_depth` using entry points from `store.roles`
2. `compute_orphans` using `store.roles`
3. `compute_centrality_gini`
4. Clone detection (if > 5 files, skip for tiny codebases)
5. Author distance (if `store.git_history` available)

### Moved: `SpectralSummary.spectral_gap` → `GraphAnalysis.spectral_gap`

Move `spectral_gap` from `temporal/models.py:SpectralSummary` into `GraphAnalysis`. The `SpectralAnalyzer` already writes to `store.spectral` — update it to also write `store.structural.graph_analysis.spectral_gap`. Eventually remove `SpectralSummary` as a standalone model (fiedler_value and eigenvalues move to `GraphAnalysis` too).

## New Signals Available After This Phase

| # | Signal | Status before | Status after | Computed by |
|---|--------|--------------|--------------|-------------|
| 15 | `betweenness` | EXISTS | EXISTS (unchanged) | `graph/algorithms.py` |
| 19 | `depth` | MISSING | **NEW** | `graph/algorithms.py:compute_dag_depth` |
| 20 | `is_orphan` | MISSING | **NEW** | `graph/algorithms.py:compute_orphans` |
| 21 | `phantom_import_count` | PARTIAL | **UPGRADED** | `graph/builder.py` (count unresolved) |
| 54 | `spectral_gap` | EXISTS (in SpectralSummary) | MOVED to GraphAnalysis | `insights/analyzers/spectral.py` |
| 56 | `centrality_gini` | MISSING | **NEW** | `graph/algorithms.py:compute_centrality_gini` |
| 57 | `orphan_ratio` | MISSING | **NEW** (global) | `count(is_orphan) / total_files` |
| 58 | `phantom_ratio` | MISSING | **NEW** (global) | `unresolved / total_edges` |
| 59 | `glue_deficit` | MISSING | **NEW** (global) | `1 - |glue_nodes| / |V|` |
| — | `clone_ratio` | MISSING | **NEW** (global) | `graph/clone_detection.py` |
| — | G5 distances | MISSING | **NEW** | `graph/distance.py` |

**Signal #22 (`broken_call_count`) is NOT available** — requires CALL edges which are future work.

## New Finders Available After This Phase

No new finders yet. But these signals unlock finders in Phase 6:
- `is_orphan` → ORPHAN_CODE finder
- `phantom_import_count` → PHANTOM_IMPORTS finder
- `depth` + `glue_deficit` → FLAT_ARCHITECTURE finder
- Clone pairs → COPY_PASTE_CLONE finder
- G5 distances → CONWAY_VIOLATION finder

## Acceptance Criteria

1. `depth` correctly computed: entry points get depth=0, their imports get depth=1, etc.
2. Unreachable files (no path from any entry point) get depth=-1
3. `is_orphan` correctly excludes ENTRY_POINT and TEST files
4. `centrality_gini` matches hand-computed value on test fixture
5. Clone detection finds known duplicates in test fixtures (two files with NCD < 0.3)
6. Clone detection does NOT flag files that are merely similar (NCD > 0.5)
7. Author distance = 0 for files with identical author distributions
8. Author distance = 1 for files with completely different authors
9. All 247+ existing tests pass
10. Performance: clone detection < 1s for 500 files, author distance < 500ms
11. Louvain produces identical communities on two consecutive runs with same input

## What This Phase Does NOT Do

- **No CALL edges** — resolving `foo()` to the file defining `foo` across languages is a hard cross-reference problem. Deferred to future work (Phase 3b). The spec's G2 (call distance space) is not built here.
- **No TYPE_FLOW edges** — same reason. G3 deferred.
- **No G6 semantic distance** — needs concept vectors from Phase 2 to be wired into a distance computation. Could be added here but keeping scope tight.

## Estimated Scope

- 2 new files (`clone_detection.py`, `distance.py`)
- 5 modified files
- ~600 lines of new code
- ~1.5 weeks
