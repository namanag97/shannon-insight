# Shannon Insight Memory

## Important Workflow Rules
- **NEVER read background agent output files** — they blow up the context window.
- Use `TaskOutput` with `block=false` only for status checks, or wait for completion notification.

## Project State
- Current version: 0.8.0 (pyproject.toml)
- Working CLI on PyPI: `shannon-codebase-insight`
- 6 analyzers, 28 patterns, 67 signals (enum has 67, docstring says 62 — stale)
- Zero users — can break APIs freely

## Key Architecture (VERIFIED FROM CODE)

See `memory/architecture.md` for full detail. Summary:

### Pipeline (InsightKernel.run())
```
SyntaxExtractor → store.file_syntax
Wave 1 analyzers (topo-sorted) → store slots
Wave 2 SignalFusionAnalyzer → store.signal_field
execute_patterns(store.fact_store) → pattern_findings
persistence finders (if history.db has 3+ snapshots)
rank + cap → InsightResult
capture_tensor_snapshot → TensorSnapshot → history.db
```

### Store Slots (AnalysisStore)
- `file_syntax`: dict[path, FileSyntax] — produced by scanning
- `structural`: CodebaseAnalysis — produced by StructuralAnalyzer
- `clone_pairs`: list[ClonePair] — produced by StructuralAnalyzer
- `git_history`: GitHistory — produced by TemporalAnalyzer
- `cochange`: CoChangeMatrix — produced by TemporalAnalyzer
- `churn`: dict[path, ChurnSeries] — produced by TemporalAnalyzer
- `author_distances`: list[AuthorDistance] — produced by TemporalAnalyzer
- `spectral`: SpectralSummary — produced by SpectralAnalyzer
- `semantics`: dict[path, FileSemantics] — produced by SemanticAnalyzer
- `roles`: dict[path, str] — produced by SemanticAnalyzer
- `architecture`: Architecture — produced by ArchitectureAnalyzer
- `signal_field`: SignalField — produced by SignalFusionAnalyzer

### Analyzers (VERIFIED FROM CODE)
1. `StructuralAnalyzer` — requires: {file_syntax}, provides: {structural, clone_pairs}
2. `TemporalAnalyzer` — requires: {}, provides: {git_history, cochange, churn, author_distances}
3. `SpectralAnalyzer` — requires: {structural}, provides: {spectral}
4. `SemanticAnalyzer` — requires: {file_syntax}, provides: {semantics, roles}
5. `ArchitectureAnalyzer` — requires: {structural, roles}, provides: {architecture}
6. `SignalFusionAnalyzer` (Wave 2) — provides: {signal_field}

### Patterns (28, VERIFIED FROM registry.py)
Core(7): HIGH_RISK_HUB, HIDDEN_COUPLING, GOD_FILE, UNSTABLE_FILE, BOUNDARY_MISMATCH, DEAD_DEPENDENCY, CHRONIC_PROBLEM
AI Quality(8): ORPHAN_CODE, HOLLOW_CODE, PHANTOM_IMPORTS, COPY_PASTE_CLONE, FLAT_ARCHITECTURE, NAMING_DRIFT, INCOMPLETE_IMPLEMENTATION, DUPLICATE_INCOMPLETE
Team(3): KNOWLEDGE_SILO, REVIEW_BLINDSPOT, TRUCK_FACTOR
Architecture(5): LAYER_VIOLATION, ZONE_OF_PAIN, ARCHITECTURE_EROSION, CIRCULAR_DEPENDENCY, ZONE_OF_USELESSNESS
Cross-Dim(3): WEAK_LINK, BUG_ATTRACTOR, ACCIDENTAL_COUPLING
Temporal(2): THRASHING_CODE, DIRECTORY_HOTSPOT

### Signal Count: 67 (NOT 62 or 69)
5 signals added after initial 62 with #Xa/b numbering: CYCLE_MEMBER, CYCLE_SIZE, CHANGE_ENTROPY, FILE_HEALTH_SCORE, DELTA_H
BROKEN_CALL_COUNT is registered but always 0 (CALL edges not implemented)

## Persistence Databases (VERIFIED FROM CODE)
- `facts.db`: FileFact, FunctionFact, ClassFact, ImportFact (Phase 1 parsed facts)
- `git_facts.db`: git_commits, git_file_changes (raw git data for temporal)
- `graph_store.db`: graph_edges, node_metrics, cycle_members, community_members
- `history.db`: 16 tables V1+V2 — snapshots, signal_history, finding_lifecycle, etc.
- `Parquet` (optional): snapshots, file_signals, module_signals, global_signals, edges, findings

## Relations (10 types, VERIFIED FROM relations.py)
IMPORTS, COCHANGES_WITH, SIMILAR_TO, AUTHORED_BY, IN_MODULE, CONTAINS, DEPENDS_ON, CLONED_FROM, CYCLE_WITH, AUTHOR_DISTANCE

## Key Stale Documentation (mark as ⚠️ STALE)
- `docs/v2/` phases 0-7: These are SPEC documents; implementation already exists
- Signal count in infrastructure/signals.py docstring says "62 signals" — actual is 67
- MEMORY.md had wrong ChurnSeries fields (recency_days, dominant_author don't exist)
- "22 analyzers" mentioned anywhere is wrong — there are 6 analyzers, 28 patterns
- v1/v2 distinction is stale — this IS the implementation

## Development Rules
- `make all` after every file change
- Tests are in tests/ (run with `make test`)
- Architecture: see `memory/architecture.md`
- Signals: see `memory/signals-accurate.md`
