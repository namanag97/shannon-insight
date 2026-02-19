# Shannon Insight Codebase Audit

## Module Map

```
src/shannon_insight/
├── api.py                    # Main entry: analyze() function
├── config.py                 # Pydantic settings, TOML loading
├── environment.py            # Environment discovery
├── session.py                # AnalysisSession: config + tier
│
├── scanning/                 # Phase 0-1: Syntax extraction
│   ├── syntax.py             # FileSyntax, FunctionDef, ClassDef, ImportDecl
│   ├── syntax_extractor.py   # Orchestrates parsers
│   ├── treesitter_parser.py  # Tree-sitter integration
│   ├── fallback.py           # Regex fallback
│   └── normalizer.py         # Cross-language normalization
│
├── graph/                    # Phase 2-3: Graph algorithms
│   ├── models.py             # DependencyGraph, GraphAnalysis
│   ├── engine.py             # Graph building from imports
│   └── clone_detection.py    # NCD-based clones
│
├── architecture/             # Phase 4: Architecture analysis
│   ├── models.py             # Module, Layer, Violation
│   ├── modules.py            # Module detection
│   ├── layers.py             # Layer inference
│   └── metrics.py            # Martin metrics
│
├── semantics/                # Phase 2: Semantic analysis
│   ├── concepts.py           # TF-IDF concept extraction
│   ├── roles.py              # Role classification
│   └── analyzer.py           # SemanticAnalyzer
│
├── temporal/                 # Phase 3: Git temporal analysis
│   ├── models.py             # GitHistory, ChurnSeries, CoChangeMatrix
│   └── git_extractor.py      # Raw git extraction
│
├── signals/                  # Phase 5: Signal fusion
│   ├── models.py             # FileSignals, ModuleSignals, GlobalSignals
│   └── normalization.py      # Percentile normalization
│
├── infrastructure/           # v2 foundation patterns
│   ├── signals.py            # Signal enum, REGISTRY
│   ├── store.py              # FactStore (unified)
│   ├── entities.py           # EntityId types
│   └── validation.py         # Phase contracts
│
├── insights/                 # Analysis orchestration
│   ├── kernel.py             # InsightKernel (legacy)
│   ├── store.py              # AnalysisStore (blackboard)
│   ├── analyzers/            # Structural, Temporal, Spectral
│   └── finders/              # 22+ pattern detectors
│
├── kernel/                   # v2 orchestrator
│   ├── runtime_kernel.py     # RuntimeKernel
│   └── phases/               # Phase executors
│
├── persistence/              # Storage
│   ├── facts.py              # FactDatabase (SQLite)
│   ├── git_facts.py          # GitFactDatabase
│   ├── database.py           # SnapshotDatabase
│   └── models.py             # TensorSnapshot
│
└── cli/                      # Typer CLI
```

---

## Data Flow

```
CLI Entry (shannon-insight)
    ↓
analyze() [api.py]
    ↓
RuntimeKernel.run()
    │
    ├── Phase 0: Discovery → find source files
    ├── Phase 1: Scanning → FileSyntax (tree-sitter/regex)
    ├── Phase 2: Structural → DependencyGraph, PageRank, SCC, Louvain
    ├── Phase 3: Temporal → GitHistory, ChurnSeries, CoChangeMatrix
    ├── Phase 4: Fusion → FileSignals, ModuleSignals, GlobalSignals
    ├── Phase 5: Patterns → Finding[] (22 finders)
    └── Phase 6: Reporting → TensorSnapshot
```

---

## Key Data Models

### FileSyntax (scanning/syntax.py)
```python
FileSyntax:
    path, language, content_hash
    functions: FunctionDef[]
    classes: ClassDef[]
    imports: ImportDecl[]
    max_nesting, stub_ratio, impl_gini
```

### FileSignals (signals/models.py)
```python
FileSignals (36 signals):
    # Scanning
    lines, function_count, class_count, max_nesting, stub_ratio
    # Graph
    pagerank, betweenness, blast_radius_size, depth, is_orphan
    # Temporal
    total_changes, churn_cv, bus_factor, author_entropy
    # Composites
    risk_score, wiring_quality, health_score, delta_h
```

### DependencyGraph (graph/models.py)
```python
DependencyGraph:
    adjacency: dict[str, set[str]]  # A → {B, C}
    reverse: dict[str, set[str]]    # B ← {A}
    unresolved_imports: set[str]
```

### ChurnSeries (temporal/models.py)
```python
ChurnSeries:
    file_path, total_changes
    trajectory: DORMANT | STABILIZING | STABLE | CHURNING | SPIKING
    cv, bus_factor, author_entropy
```

---

## Storage (3 SQLite DBs)

1. **facts.db** - Parsed syntax facts
   - `file_facts`, `function_facts`, `class_facts`, `import_facts`

2. **git_facts.db** - Git history
   - `git_commits`, `git_file_changes`

3. **history.db** - Snapshots
   - `snapshots` (TensorSnapshot JSON)

---

## Technical Debt

### High Priority
- **Instability=None guards**: 5+ places need guard for isolated modules
- **Percentile NaN**: ABSOLUTE tier (<15 files) has no percentiles
- **Dual Store**: AnalysisStore + FactStore not consolidated

### Medium Priority
- **Legacy InsightKernel**: Still used alongside RuntimeKernel
- **No content-hash caching**: Re-parses unchanged files
- **O(n²) co-change**: No LSH for large codebases

### Missing Features
- CALL/TYPE_FLOW edges (deferred)
- Adaptive LSH for clone detection
- Symbol-level analysis scaffolding

---

## Statistics

| Metric | Count |
|--------|-------|
| Modules | 21 packages |
| Data models | 40+ dataclasses |
| Analyzers | 4 (Structural, Temporal, Spectral, Fusion) |
| Finders | 22 patterns |
| Signals | 62 (36 file + 15 module + 11 global) |
| Phases | 7 |
| Tests | 200+ files |
