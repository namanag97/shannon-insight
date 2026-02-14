# Shannon Insight: System Architecture

This document describes the internal architecture of Shannon Insight for contributors, integrators, and anyone who wants to understand how the system works at the code level.

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Module Structure](#module-structure)
3. [Data Flow](#data-flow)
4. [The Blackboard Pattern](#the-blackboard-pattern)
5. [Intermediate Representations](#intermediate-representations)
6. [Extension Points](#extension-points)
7. [Testing Strategy](#testing-strategy)
8. [Key Design Decisions](#key-design-decisions)

---

## High-Level Architecture

Shannon Insight follows a staged pipeline architecture with a shared blackboard (AnalysisStore) at its center. Two parallel spines -- structural and temporal -- feed into a fusion layer that produces composite signals, which finders then evaluate to produce actionable findings.

```
  SOURCE FILES -----> scanning/ -----> semantics/ ---+
                       (IR0+IR1)        (IR2)        |
                                                     +---> graph/ ---> architecture/
  GIT HISTORY ------> temporal/ ------------------------>   (IR3)        (IR4)
                       (IR5t)            (parallel)       |            |
                                                          +------------+
                                                          v            |
                                                     signals/ <--------+
                                                      (IR5s)
                                                          |
                                                          v
                                                     insights/
                                                      (IR6)
                                                          |
                                +-------------------------+
                                v                         v
                            persistence/              cli/ + JSON
```

The pipeline produces 6 intermediate representations (IR0 through IR6), each building on the previous. The structural spine (scanning -> semantics -> graph -> architecture) processes file content. The temporal spine (temporal) processes git history. Both feed into the signal fusion layer (signals), which normalizes, combines, and produces the final SignalField that finders read.

---

## Module Structure

The codebase is organized into these packages within `src/shannon_insight/`:

### `scanning/` -- IR0 + IR1: File Parsing

**Purpose**: Parse source files across 8 languages into language-agnostic `FileSyntax` representations.

**Key types**:
- `ScannerFactory` -- Factory that creates language-specific scanners based on file extension
- `UniversalScanner` -- Auto-detects language and dispatches to the appropriate scanner
- `FileMetrics` -- Basic file-level metrics (lines, functions, classes, imports)
- `FileSyntax` -- Rich syntax representation (functions with bodies, classes with inheritance, imports with resolution)
- `FunctionDef` -- Per-function data: name, parameters, body_tokens, nesting_depth, call_targets, decorators
- `ClassDef` -- Per-class data: name, bases, methods, fields, is_abstract
- `ImportDecl` -- Import declaration: source, names, resolved_path

**Language scanners**: Python, Go, TypeScript, JavaScript, Java, Rust, Ruby, C/C++. Each scanner implements the `Scanner` protocol.

**Fallback strategy**: If tree-sitter grammars are installed (`pip install shannon-codebase-insight[parsing]`), parsing uses full AST analysis. Otherwise, regex-based scanners provide basic extraction. Both paths produce `FileSyntax`, but tree-sitter populates additional fields (call_targets, decorators).

### `semantics/` -- IR2: Semantic Analysis

**Purpose**: Classify file roles, extract concept clusters, detect naming drift, and measure documentation coverage.

**Key types**:
- `SemanticAnalyzer` -- Orchestrator for all semantic computations
- `FileSemantics` -- Complete semantic profile: role, concepts, naming_drift, todo_density, docstring_coverage
- `Role` -- Enum: MODEL, SERVICE, UTILITY, CONFIG, TEST, CLI, INTERFACE, EXCEPTION, CONSTANT, ENTRY_POINT, MIGRATION, UNKNOWN
- `Concept` -- A concept cluster: topic name and weight

**Important implementation detail**: Concept extraction requires a two-pass architecture. Pass 1 extracts identifiers from all files to build corpus-wide IDF values. Pass 2 computes per-file TF-IDF vectors and runs Louvain community detection on the token co-occurrence graph.

### `graph/` -- IR3: Dependency Graph

**Purpose**: Build the dependency graph from import declarations, run graph algorithms, and compute per-file and global graph metrics.

**Key types**:
- `DependencyGraph` -- Directed graph with adjacency, reverse adjacency, and unresolved imports
- `CodebaseAnalysis` -- Container for all graph-derived analysis results
- `GraphAnalysis` -- Global graph metrics (modularity, Fiedler value, cycle count, centrality Gini)
- `FileAnalysis` -- Per-file graph metrics (PageRank, betweenness, blast radius, depth, is_orphan)
- `ClonePair` -- NCD-based clone detection result
- `AuthorDistance` -- G5 author distance space entry

**Algorithms** (in `algorithms.py`):
1. Degree computation -- O(|V| + |E|)
2. Tarjan SCC -- O(|V| + |E|)
3. PageRank -- O(|E| * iterations), power iteration with d=0.85
4. Betweenness centrality -- O(|V| * |E|), Brandes' algorithm
5. Blast radius BFS -- O(|V| * (|V| + |E|))
6. Louvain community detection -- O(|E| * passes)
7. DAG depth -- O(|V| + |E|), multi-source BFS from entry points
8. Spectral analysis -- O(|E| * k * iterations), Lanczos for top-k eigenvalues
9. Centrality Gini -- O(|V| log |V|)

### `architecture/` -- IR4: Architecture Detection

**Purpose**: Detect module boundaries, compute Martin metrics, infer layers, and detect violations.

**Key types**:
- `ArchitectureAnalyzer` -- Analyzer protocol implementation
- `Architecture` -- Top-level result: modules, layers, violations
- `Module` -- A directory-based module with Martin metrics (Ca, Ce, I, A, D)
- `Layer` -- A depth level in the inferred layering
- `Violation` -- A backward or skip edge in the layer ordering

**Module detection**: Selects the directory depth where most directories have 3-15 files. For flat projects, uses Louvain communities as synthetic modules.

**Layer inference**: Topological sort of the module-level dependency DAG. SCCs (circular module dependencies) are merged to the same layer.

### `temporal/` -- IR5t: Git History Analysis

**Purpose**: Parse git history, compute churn trajectories, co-change matrices, author distributions, and commit classification.

**Key types**:
- `GitExtractor` -- Parses `git log` output
- `ChurnSeries` -- Per-file temporal signals: total_changes, trajectory, slope, CV, bus_factor, author_entropy, fix_ratio, refactor_ratio
- `CoChangeMatrix` -- Pairwise co-change counts with lift and confidence

**Parallel spine**: The temporal spine runs independently of the structural spine (scanning -> semantics -> graph). Both spines merge at the signal fusion stage.

### `signals/` -- IR5s: Signal Fusion

**Purpose**: Collect all signals into a unified SignalField, normalize to percentiles, compute composite scores, and apply the health Laplacian.

**Key types**:
- `SignalField` -- Unified container: per_file (Dict[str, FileSignals]), per_module (Dict[str, ModuleSignals]), global_signals (GlobalSignals), delta_h (Dict[str, float])
- `FileSignals` -- All 36 per-file signals plus percentiles and composites
- `ModuleSignals` -- All 15 per-module signals
- `GlobalSignals` -- All 11 global signals including composites
- `SignalFusion` -- Builder that collects from all store slots and produces SignalField

**Fusion pipeline** (strict order):
1. Collect raw signals from all sources
2. Compute raw_risk per file (pre-percentile, for health Laplacian)
3. Normalize to percentiles (tiered: ABSOLUTE/BAYESIAN/FULL)
4. Aggregate module temporal signals (needs percentiles for module_bus_factor)
5. Compute composite scores (risk_score, wiring_quality, health_score, etc.)
6. Compute health Laplacian (uses raw_risk, not composites)

**Two-wave execution**: SignalFusion runs in Wave 2, after all Wave 1 analyzers (structural, semantic, temporal, architecture) have completed.

### `insights/` -- IR6: Finding Detection

**Purpose**: Orchestrate the analysis pipeline via the InsightKernel blackboard pattern, run finders, rank findings, and produce the final InsightResult.

**Key types**:
- `InsightKernel` -- The central orchestrator. Manages analyzers (Wave 1 + Wave 2), finders, and the AnalysisStore blackboard.
- `AnalysisStore` -- Shared blackboard with typed slots for each IR's output
- `Finding` -- A detected issue: type, severity, confidence, files, evidence, suggestion
- `Evidence` -- A signal value that contributed to a finding
- `InsightResult` -- Final analysis output: findings, composites, metadata

**Analyzer protocol**:
```python
class Analyzer(Protocol):
    name: str
    requires: Set[str]    # store slots needed
    provides: Set[str]    # store slots written

    def analyze(self, store: AnalysisStore) -> None: ...
```

**Finder protocol**:
```python
class Finder(Protocol):
    name: str
    requires: Set[str]    # store slots needed

    def find(self, store: AnalysisStore) -> List[Finding]: ...
```

### `persistence/` -- Snapshot Storage

**Purpose**: Serialize analysis results to SQLite, enable cross-snapshot comparison, and track finding lifecycle.

**Key types**:
- `TensorSnapshot` -- Serialized SignalField with all per-file, per-module, and global signals
- `HistoryDB` -- SQLite database with signal_history, finding_lifecycle tables
- `DiffEngine` -- Computes structured diffs between snapshots
- `SnapshotDiff` -- Signal deltas, finding deltas, debt velocity

### `cli/` -- Terminal Interface

**Purpose**: Typer-based CLI with rich terminal output.

**Commands**: main (analyze), explain, diff, health, history, report, serve

### `math/` -- Mathematical Primitives

**Purpose**: Reusable math functions used by multiple modules.

**Contents**: Shannon entropy, compression, Gini coefficient, graph algorithms (PageRank, betweenness), robust statistics, signal fusion helpers.

---

## Data Flow

### Input to Output

```
Input:
  1. Source file paths (from scanning the directory tree)
  2. Git history (from `git log`, if available)
  3. Configuration (shannon-insight.toml, env vars, CLI flags)

Processing:
  1. scanning/   -> FileMetrics[] + FileSyntax[]
  2. semantics/  -> FileSemantics[] (role, concepts, naming_drift)
  3. temporal/   -> ChurnSeries[], CoChangeMatrix  (parallel with 1-2)
  4. graph/      -> DependencyGraph, GraphAnalysis, FileAnalysis[]
  5. architecture/ -> Architecture (modules, layers, violations)
  6. signals/    -> SignalField (62 signals, percentiles, 7 composites, delta_h)
  7. insights/   -> Finding[] (22 finder types)

Output:
  - InsightResult (findings, composites, metadata)
  - Serialized to: rich terminal, JSON, HTML report, or SQLite snapshot
```

### Store Slot Dependencies

The AnalysisStore has typed slots. Each analyzer writes to specific slots and reads from others:

```
Slot                 Written by          Read by
----                 ----------          -------
file_metrics         scanning/           signals/, graph/, semantics/
file_syntax          scanning/           semantics/, graph/ (clones), architecture/
roles                semantics/          graph/ (orphan detection), architecture/
semantics            semantics/          signals/ (concepts), finders (ACCIDENTAL_COUPLING)
structural           graph/              architecture/, signals/, finders
git_history          temporal/           signals/ (module temporal)
cochange             temporal/           finders (HIDDEN_COUPLING, DEAD_DEPENDENCY)
churn                temporal/           signals/ (per-file temporal signals)
spectral             graph/ (spectral)   signals/ (fiedler, spectral_gap)
clone_pairs          graph/ (clones)     finders (COPY_PASTE_CLONE)
author_distances     graph/ (distance)   finders (CONWAY_VIOLATION)
architecture         architecture/       signals/ (module metrics), finders
signal_field         signals/            ALL finders (the main data source)
```

### Analyzer Execution Order

Wave 1 analyzers are topologically sorted by their `requires` and `provides` declarations:

```
1. StructuralAnalyzer  requires: {files}         provides: {structural, spectral}
2. TemporalAnalyzer    requires: {files}         provides: {git_history, cochange, churn}
   (can run in parallel with StructuralAnalyzer)
3. SemanticAnalyzer    requires: {file_syntax}   provides: {semantics, roles}
4. ArchitectureAnalyzer requires: {structural, roles}  provides: {architecture}

Wave 2 (always last):
5. SignalFusionAnalyzer requires: ALL             provides: {signal_field}
```

After all analyzers, finders run:
```
6. All finders (in registration order)
   Each finder checks if its required slots are available; skips if not.
```

---

## The Blackboard Pattern

Shannon Insight uses the blackboard pattern (also known as the shared workspace pattern) at its core. The `AnalysisStore` is the blackboard -- a shared data structure where analyzers write signals and finders read them.

### Why Blackboard?

1. **Decoupling**: Analyzers do not call each other directly. They read from and write to the store. Adding a new analyzer does not require modifying existing ones.

2. **Graceful degradation**: If an analyzer cannot run (e.g., no git history available), its store slots remain empty. Finders that require those slots gracefully skip. The system degrades without failing.

3. **Demand-driven evaluation**: The kernel can trace from a finder's `requires` through the dependency graph of analyzers to determine exactly which computations are needed. Unused analyzers can be skipped.

4. **Testability**: Each analyzer can be tested in isolation by providing a pre-populated store with only its required slots.

### Store Typed Slots

The AnalysisStore uses typed Optional fields (not a generic dictionary) to ensure type safety:

```python
@dataclass
class AnalysisStore:
    file_metrics: List[FileMetrics]                    # always populated
    file_syntax: Optional[Dict[str, FileSyntax]] = None
    roles: Optional[Dict[str, str]] = None
    semantics: Optional[Dict[str, FileSemantics]] = None
    structural: Optional[CodebaseAnalysis] = None
    git_history: Optional[GitHistory] = None
    cochange: Optional[CoChangeMatrix] = None
    churn: Optional[Dict[str, ChurnSeries]] = None
    spectral: Optional[SpectralSummary] = None
    clone_pairs: Optional[List[ClonePair]] = None
    author_distances: Optional[List[AuthorDistance]] = None
    architecture: Optional[Architecture] = None
    signal_field: Optional[SignalField] = None
```

Each slot is either populated (the analysis ran) or None (it did not). This is the mechanism for graceful degradation.

---

## Intermediate Representations

Each stage of the pipeline produces an intermediate representation that subsequent stages consume:

| IR | Name | Produced by | Contains |
|----|------|-------------|----------|
| IR0 | File entry | scanning/ | File path, language, raw content reference |
| IR1 | Syntax | scanning/ | FileSyntax with functions, classes, imports |
| IR2 | Semantics | semantics/ | Role, concepts, naming drift, documentation coverage |
| IR3 | Graph | graph/ | Dependency graph, PageRank, betweenness, blast radius, communities, clones |
| IR4 | Architecture | architecture/ | Modules, Martin metrics, layers, violations |
| IR5t | Temporal | temporal/ | Churn trajectories, co-change, authorship, intent |
| IR5s | Signals | signals/ | SignalField with 62 signals, percentiles, 7 composites, health Laplacian |
| IR6 | Insights | insights/ | 22 finding types with evidence, confidence, suggestions |

Each IR is a complete, self-contained representation. An IR can be serialized (for snapshots), diffed (for trend detection), and queried (for the CLI explain command).

---

## Extension Points

Shannon Insight has three primary extension points, each following a protocol-based registration pattern.

### Adding a New Language Scanner

1. Create a scanner class in `scanning/` that implements the `Scanner` protocol:

```python
class MyLanguageScanner:
    def scan(self, content: str, path: str) -> FileSyntax:
        # Parse the file content
        # Return FileSyntax with functions, classes, imports
        ...
```

2. Register in `scanning/__init__.py` and `scanning/factory.py`:

```python
# In factory.py
SCANNERS = {
    ".py": PythonScanner,
    ".go": GoScanner,
    ".mylang": MyLanguageScanner,  # Add here
}
```

3. Add an entry point in `pyproject.toml`:

```toml
[project.entry-points."shannon_insight.languages"]
mylang = "shannon_insight.scanning:MyLanguageScanner"
```

### Adding a New Signal Primitive

1. Create a plugin in `signals/plugins/`:

```python
class MySignalPlugin:
    name = "my_signal"

    def compute(self, file_metrics: FileMetrics) -> float:
        # Compute the signal value
        ...
```

2. Add the field to the signal model (`signals/models.py`):

```python
@dataclass
class FileSignals:
    # ... existing fields ...
    my_signal: float = 0.0
```

3. Register in `signals/registry.py` and document in `docs/v2/registry/signals.md`.

### Adding a New Finder

1. Create a finder class in `insights/finders/`:

```python
class MyFinder:
    name = "my_finding"
    requires = {"signal_field"}

    def find(self, store: AnalysisStore) -> List[Finding]:
        if not store.signal_field:
            return []

        findings = []
        for path, fs in store.signal_field.per_file.items():
            if self._check_condition(fs):
                findings.append(Finding(
                    finding_type="my_finding",
                    severity=0.6,
                    files=[path],
                    evidence=[...],
                    suggestion="...",
                ))
        return findings
```

2. Register in `insights/finders/__init__.py`:

```python
def get_default_finders():
    return [
        # ... existing finders ...
        MyFinder(),
    ]
```

The finder automatically participates in graceful degradation: if its required store slots are not populated, the kernel skips it.

---

## Testing Strategy

### Test Pyramid

```
         /  \
        / E2E \         End-to-end: CLI commands on test codebases
       /-------\
      / Integr. \       Integration: Kernel runs full pipeline on fixtures
     /-----------\
    /   Unit      \     Unit: Individual analyzers, finders, algorithms
   /_______________\

247+ tests in the test suite
```

### Test Fixtures

Located in `tests/fixtures/`, these sample files exercise specific analysis scenarios:

| Fixture | Purpose |
|---------|---------|
| `sample_simple.py` | Basic scanning: function/class counts, import extraction |
| `sample_stubs.py` | HOLLOW_CODE testing: stub_ratio > 0.5, high impl_gini |
| `sample_complex.py` | Cognitive load: max_nesting=5, deep function nesting |
| `sample_entry.py` | Entry point detection: has `__main__` guard |
| `sample_orphan.py` | ORPHAN_CODE testing: no incoming dependencies |
| `sample_model.py` | Role=MODEL: dataclass-only file with fields |
| `test_sample.py` | Role=TEST: test file pattern matching |

### Testing Approach by Module

- **scanning/**: Parse test fixtures, verify function counts, class counts, nesting depth match hand-counted values.
- **graph/**: Construct dependency graphs from known inputs, verify PageRank convergence, verify blast radius, verify Louvain communities.
- **temporal/**: Feed synthetic git history, verify trajectory classification, verify co-change lift computation.
- **signals/**: Construct SignalField from known inputs, verify percentile computation, verify composite scores.
- **insights/finders/**: Pre-populate store with specific signal values, verify each finder fires (or does not fire) as expected.

### Quality Commands

```bash
make all       # format + check + test
make test      # Full suite with coverage
make check     # Ruff lint + mypy type checking
```

---

## Key Design Decisions

### Why Blackboard, Not Pipeline?

A pure pipeline (A -> B -> C -> D) requires every stage to run and produces no output until the last stage completes. The blackboard pattern allows:
- Partial results when some analyzers cannot run (no git = no temporal signals)
- Demand-driven computation (only run what finders need)
- Easy addition of new analyzers without modifying the pipeline

### Why Not NetworkX?

Shannon Insight implements its own graph algorithms instead of using NetworkX. Reasons:
- Avoid a heavy dependency for a small set of well-defined algorithms
- Control over determinism (sorted iteration in Louvain)
- Iterative Tarjan implementation (avoids Python recursion limit)
- Tight integration with the signal pipeline

### Why Percentile Normalization?

Raw signals have incompatible units (lines: integers up to thousands; PageRank: floats summing to 1; compression ratio: float 0 to 1). Percentile normalization maps everything to [0, 1] based on rank, which:
- Is distribution-free (works regardless of signal distribution shape)
- Is robust to outliers
- Makes weighted combination meaningful

The tradeoff is that percentiles are noisy for small samples, addressed by the three-tier degradation.

### Why Two-Wave Analyzer Execution?

Signal fusion must run after all other analyzers because it reads from all store slots. If fusion were sorted alongside other analyzers, it would need to declare `requires = ALL`, which breaks topological sort (cyclic dependency with any analyzer that could read composites). The two-wave design is simple and eliminates ordering ambiguity.

### Why Display Scale 1-10?

Internal computation uses [0, 1]. Display uses 1-10 (multiply by 10, floor at 1.0). Reasons:
- 1-10 is more intuitive for non-technical audiences (CTO, product manager)
- Matches CodeScene's Code Health scale (industry precedent)
- Floor at 1.0 prevents confusing "0.0" scores (nothing is truly zero health)
- Decimal precision (6.4/10) provides useful granularity without false precision

### Why raw_risk for Health Laplacian?

The health Laplacian computes `delta_h = raw_risk(f) - mean(raw_risk(neighbors(f)))`. It uses `raw_risk` (pre-percentile weighted sum) instead of `risk_score` (percentile-based composite) because percentile normalization produces a near-uniform distribution. The Laplacian of a uniform field is zero everywhere, making it useless. Raw values preserve the natural variation needed for the Laplacian to detect local extrema.

### Why Hotspot Filtering?

Finding complex-but-stable code wastes developer attention. If a file has high cognitive load but has not been modified in a year, the complexity is a theoretical risk, not an active one. Hotspot filtering (requiring total_changes > median) ensures findings focus on code that people are actually working on. This approach is validated by CodeScene's research and the "Your Code as a Crime Scene" methodology.

### Why Signal Polarity Declarations?

Every signal declares whether "high" is good (bus_factor, semantic_coherence) or bad (cognitive_load, churn_cv). This enables:
- Automatic trend classification (increasing bus_factor = IMPROVING; increasing cognitive_load = WORSENING)
- Correct composite computation (invert good signals with `1 - pctl(signal)`)
- Confidence scoring (margin formula respects polarity direction)
- Finder condition validation (prevents logical errors like `pctl(bus_factor) > 0.90` meaning "too many authors")
