# Stage 2: Collect

Run collectors to gather raw measurements from source files and git history.

---

## Collectors

| # | Collector | Input | Output | Signals Produced | Relations Produced |
|---|-----------|-------|--------|------------------|-------------------|
| 1 | CodeCollector | Source files | FileMetrics[], FileSyntax[] | 1-7, 12 | — |
| 2 | GitCollector | Git log | GitHistory, ChurnSeries[] | 27-34 | AUTHORED_BY |
| 3 | DependencyCollector | FileMetrics | DependencyGraph | 14-18, 52-55 | IMPORTS, DEPENDS_ON |
| 4 | CoChangeCollector | GitHistory | CoChangeMatrix | — | COCHANGES_WITH |
| 5 | SemanticCollector | FileSyntax | FileSemantics[] | 8-13, 25 | SIMILAR_TO |

---

## Collector Protocol

```python
class Collector(Protocol):
    name: str
    provides_signals: set[Signal]
    provides_relations: set[RelationType]

    def available(self, ctx: RuntimeContext) -> bool:
        """Can this collector run in this context?"""
        ...

    def collect(self, ctx: RuntimeContext, store: FactStore) -> None:
        """
        Populate store with entities, raw signals, and relations.
        May raise CollectorError on fatal failure.
        """
        ...
```

---

## 1. CodeCollector

Parses source files to extract structural metrics.

### Availability
```python
def available(self, ctx: RuntimeContext) -> bool:
    return ctx.file_count > 0
```

### Output

**FileMetrics** (one per file):
```python
@dataclass
class FileMetrics:
    path: str                     # Relative to root
    language: str
    lines: int                    # Signal #1
    function_count: int           # Signal #2
    class_count: int              # Signal #3
    import_count: int             # Signal #7
    imports: list[str]            # Raw import strings
```

**FileSyntax** (Phase 1+, one per file):
```python
@dataclass
class FileSyntax:
    path: str
    functions: list[FunctionDef]
    classes: list[ClassDef]
    max_nesting: int              # Signal #4
    has_main_guard: bool          # For role detection

@dataclass
class FunctionDef:
    name: str
    line: int
    signature_tokens: int
    body_tokens: int
    is_stub: bool                 # body_tokens < 5 or matches stub pattern

@dataclass
class ClassDef:
    name: str
    line: int
    bases: list[str]
    is_abstract: bool             # Has ABC, Protocol, or NotImplementedError
```

### Signals Computed

| Signal | Formula |
|--------|---------|
| #1 lines | Line count |
| #2 function_count | len(functions) |
| #3 class_count | len(classes) |
| #4 max_nesting | Max depth in AST |
| #5 impl_gini | Gini of function body_tokens |
| #6 stub_ratio | mean(f.is_stub for f in functions) |
| #7 import_count | len(imports) |
| #12 todo_density | (TODO + FIXME + HACK count) / lines |

---

## 2. GitCollector

Extracts git history and authorship.

### Availability
```python
def available(self, ctx: RuntimeContext) -> bool:
    return ctx.has_git
```

### Git Commands Used

```bash
# File history with authors
git log --pretty=format:"%H|%an|%ae|%at|%s" --name-only --no-merges -- <file>

# Format: commit_hash|author_name|author_email|timestamp|subject
# Followed by blank-line-separated file list
```

### Output

**GitHistory**:
```python
@dataclass
class GitHistory:
    commits: list[Commit]
    file_to_commits: dict[str, list[str]]  # path → commit hashes
    author_to_commits: dict[str, list[str]]  # email → commit hashes
```

**ChurnSeries** (one per file):
```python
@dataclass
class ChurnSeries:
    path: str
    total_changes: int            # Signal #27
    changes_per_window: list[int]  # 4-week windows
    churn_trajectory: Trajectory  # Signal #28
    churn_slope: float            # Signal #29
    churn_cv: float               # Signal #30
    authors: dict[str, int]       # email → commit count
    bus_factor: float             # Signal #31
    author_entropy: float         # Signal #32
    fix_ratio: float              # Signal #33
    refactor_ratio: float         # Signal #34
```

### Trajectory Classification

```python
class Trajectory(Enum):
    DORMANT = "dormant"           # ≤1 change ever
    STABILIZING = "stabilizing"   # CV < 0.5 and slope < 0
    STABLE = "stable"             # CV < 1.0 and |slope| < 0.1
    CHURNING = "churning"         # CV > 1.0
    SPIKING = "spiking"           # Recent spike > 3σ above mean
```

### Relations Produced

**AUTHORED_BY**: File → Author
```python
Relation(
    type=RelationType.AUTHORED_BY,
    source=EntityId(FILE, path),
    target=EntityId(AUTHOR, email),
    weight=1.0,
    metadata={"commits": count, "first_commit": date, "last_commit": date}
)
```

---

## 3. DependencyCollector

Resolves imports to build dependency graph.

### Availability
```python
def available(self, ctx: RuntimeContext) -> bool:
    return ctx.file_count > 0
```

### Output

**DependencyGraph**:
```python
@dataclass
class DependencyGraph:
    nodes: set[str]               # File paths
    edges: dict[str, set[str]]    # source → targets
    reverse: dict[str, set[str]]  # target → sources (for blast radius)
    unresolved: dict[str, list[str]]  # path → unresolved import strings
```

### Import Resolution

```python
def resolve_import(import_str: str, importer_path: str, root: Path) -> str | None:
    """
    Resolve import string to file path.
    Returns None if external (installed package) or truly unresolved.

    Examples:
      "from auth.login import User" → "src/auth/login.py"
      "import numpy" → None (external)
      "from ..utils import helper" → "src/utils.py" (relative)
    """
```

### Signals Computed

| Signal | Formula |
|--------|---------|
| #14 pagerank | PageRank algorithm (d=0.85, 50 iterations) |
| #15 betweenness | Brandes' algorithm |
| #16 in_degree | len(reverse[path]) |
| #17 out_degree | len(edges[path]) |
| #18 blast_radius_size | len(BFS(path, reverse)) - 1 |
| #52 modularity | Louvain Q score |
| #53 fiedler_value | λ₂ of Laplacian |
| #54 spectral_gap | λ₂ / λ₃ |
| #55 cycle_count | Count of SCCs with |nodes| > 1 |

### Relations Produced

**IMPORTS**: File → File
```python
Relation(
    type=RelationType.IMPORTS,
    source=EntityId(FILE, importer),
    target=EntityId(FILE, imported),
    weight=1.0,
)
```

**DEPENDS_ON**: Module → Module (aggregated)
```python
Relation(
    type=RelationType.DEPENDS_ON,
    source=EntityId(MODULE, module_a),
    target=EntityId(MODULE, module_b),
    weight=edge_count,
)
```

---

## 4. CoChangeCollector

Builds co-change matrix from git history.

### Availability
```python
def available(self, ctx: RuntimeContext) -> bool:
    return ctx.has_git
```

### Algorithm

```python
def build_cochange_matrix(history: GitHistory) -> CoChangeMatrix:
    """
    For each commit, all files in that commit are co-changed.
    Weight = lift(A, B) = P(A ∩ B) / (P(A) × P(B))
    """
    pair_counts: Counter[tuple[str, str]] = Counter()
    file_counts: Counter[str] = Counter()
    total_commits = len(history.commits)

    for commit in history.commits:
        files = commit.files
        for f in files:
            file_counts[f] += 1
        for a, b in combinations(sorted(files), 2):
            pair_counts[(a, b)] += 1

    # Compute lift
    cochange: dict[tuple[str, str], float] = {}
    for (a, b), count in pair_counts.items():
        p_a = file_counts[a] / total_commits
        p_b = file_counts[b] / total_commits
        p_ab = count / total_commits
        lift = p_ab / (p_a * p_b) if p_a > 0 and p_b > 0 else 0
        cochange[(a, b)] = lift

    return CoChangeMatrix(cochange)
```

### Relations Produced

**COCHANGES_WITH**: File → File (symmetric)
```python
Relation(
    type=RelationType.COCHANGES_WITH,
    source=EntityId(FILE, a),
    target=EntityId(FILE, b),
    weight=lift,
    metadata={"count": pair_count, "confidence": confidence}
)
```

---

## 5. SemanticCollector

Extracts concepts and computes semantic similarity.

### Availability
```python
def available(self, ctx: RuntimeContext) -> bool:
    return ctx.file_count >= 3  # Need enough files for meaningful TF-IDF
```

### Output

**FileSemantics** (one per file):
```python
@dataclass
class FileSemantics:
    path: str
    role: Role                    # Signal #8
    concepts: list[str]           # Top concept tokens
    concept_weights: dict[str, float]  # concept → TF-IDF weight
    concept_count: int            # Signal #9
    concept_entropy: float        # Signal #10
    naming_drift: float           # Signal #11
    docstring_coverage: float     # Signal #13
    semantic_coherence: float     # Signal #25
```

### Role Classification

```python
class Role(Enum):
    MODEL = "model"
    SERVICE = "service"
    UTILITY = "utility"
    CONFIG = "config"
    TEST = "test"
    CLI = "cli"
    INTERFACE = "interface"
    EXCEPTION = "exception"
    CONSTANT = "constant"
    ENTRY_POINT = "entry_point"
    MIGRATION = "migration"
    UNKNOWN = "unknown"
```

**Classification rules** (first match wins):
```python
def classify_role(path: str, syntax: FileSyntax, metrics: FileMetrics) -> Role:
    filename = Path(path).stem.lower()

    # Test detection
    if filename.startswith("test_") or filename.endswith("_test"):
        return Role.TEST
    if "/tests/" in path or "/test/" in path:
        return Role.TEST

    # Entry point detection
    if syntax.has_main_guard:
        return Role.ENTRY_POINT
    if filename in ("main", "cli", "app", "__main__"):
        return Role.ENTRY_POINT

    # Config detection
    if filename in ("config", "settings", "constants", "env"):
        return Role.CONFIG

    # Model detection (dataclasses, no logic)
    if all_classes_are_dataclasses(syntax):
        return Role.MODEL

    # Interface detection
    if all_classes_are_abstract(syntax):
        return Role.INTERFACE

    # Exception detection
    if all_classes_are_exceptions(syntax):
        return Role.EXCEPTION

    # Utility detection (all functions, no classes)
    if syntax.class_count == 0 and syntax.function_count > 0:
        return Role.UTILITY

    # Service detection (classes with methods)
    if syntax.class_count > 0:
        return Role.SERVICE

    return Role.UNKNOWN
```

### Signals Computed

| Signal | Formula |
|--------|---------|
| #8 role | Decision tree above |
| #9 concept_count | len(concepts) via Louvain on token co-occurrence |
| #10 concept_entropy | -Σ w(c) × log₂(w(c)) |
| #11 naming_drift | 1 - cosine(tfidf(filename), tfidf(content)) |
| #13 docstring_coverage | documented_public / total_public |
| #25 semantic_coherence | mean(cosine(vᵢ, vⱼ)) for function TF-IDF vectors |

### Relations Produced

**SIMILAR_TO**: File → File (top-k most similar)
```python
Relation(
    type=RelationType.SIMILAR_TO,
    source=EntityId(FILE, a),
    target=EntityId(FILE, b),
    weight=cosine_similarity,
)
```

---

## Parallel Execution

```python
def run_collectors(ctx: RuntimeContext, store: FactStore) -> None:
    """
    Run collectors in optimal order with parallelism.
    """
    # Phase 1: Parallel (no dependencies)
    with ThreadPoolExecutor(max_workers=2) as executor:
        structural_future = executor.submit(run_structural_spine, ctx, store)
        temporal_future = executor.submit(run_temporal_spine, ctx, store)

        structural_future.result()  # Wait for completion
        temporal_future.result()

    # Phase 2: Sequential (depends on both spines)
    CoChangeCollector().collect(ctx, store)  # Needs GitHistory + file list
    SemanticCollector().collect(ctx, store)  # Needs FileSyntax

def run_structural_spine(ctx: RuntimeContext, store: FactStore) -> None:
    CodeCollector().collect(ctx, store)
    DependencyCollector().collect(ctx, store)

def run_temporal_spine(ctx: RuntimeContext, store: FactStore) -> None:
    if ctx.has_git:
        GitCollector().collect(ctx, store)
```

---

## Error Handling

```python
class CollectorError(Exception):
    """Fatal collector failure."""
    pass

def collect_with_graceful_degradation(
    collector: Collector,
    ctx: RuntimeContext,
    store: FactStore
) -> None:
    """
    Run collector, handle failures gracefully.
    """
    if not collector.available(ctx):
        logger.info(f"Skipping {collector.name}: not available")
        return

    try:
        collector.collect(ctx, store)
    except CollectorError:
        raise  # Fatal, propagate
    except Exception as e:
        logger.warning(f"{collector.name} failed: {e}. Continuing without.")
        # Mark signals as unavailable
        for signal in collector.provides_signals:
            store.mark_unavailable(signal)
```
