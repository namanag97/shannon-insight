# Shannon Insight: Actual Architecture (from code)

## Data Flow (verified from InsightKernel.run())

```
Source Data
  Raw files (discovered via git ls-files or directory walk)
  Git repository (git log subprocess)

Phase 0: Discovery
  Environment.discover_environment() → file list, languages, git branch
  AnalysisSession(config, env) → tier (ABSOLUTE/BAYESIAN/FULL)

Phase 1: Scanning (SyntaxExtractor)
  TreeSitterNormalizer or RegexFallbackScanner → FileSyntax per file
  resolve_all_imports() → updates ImportDecl.resolved_path
  → store.file_syntax: dict[path, FileSyntax]
  → store._content_cache: dict[path, str] (file text, released after fusion)

  Side: _sync_entities() writes 4 basic signals to FactStore:
    LINES, FUNCTION_COUNT, CLASS_COUNT, IMPORT_COUNT

Wave 1 Analyzers (topologically sorted by requires/provides):

  StructuralAnalyzer (requires: file_syntax)
    AnalysisEngine.run() →
      build_dependency_graph() → DependencyGraph
      run_graph_algorithms() → PageRank, SCC, Louvain, blast_radius
      → per-file: pagerank, betweenness, in/out_degree, blast_radius, community
      → per-file: depth (BFS from entry points), is_orphan, phantom_import_count
      → per-file: compression_ratio, cognitive_load
      → global: modularity, cycle_count, centrality_gini
    detect_clones(file_contents, threshold=0.30, min_lines=20) → clone_pairs
    → store.structural: CodebaseAnalysis
    → store.clone_pairs: list[ClonePair]
    → FactStore signals: PAGERANK, BETWEENNESS, IN_DEGREE, OUT_DEGREE,
        BLAST_RADIUS_SIZE, COMMUNITY, DEPTH, IS_ORPHAN, CYCLE_MEMBER, CYCLE_SIZE,
        PHANTOM_IMPORT_COUNT, COMPRESSION_RATIO, COGNITIVE_LOAD
    → FactStore global: MODULARITY, CYCLE_COUNT, CENTRALITY_GINI
    → FactStore relations: IMPORTS, CYCLE_WITH (symmetric), CLONED_FROM (symmetric)

  TemporalAnalyzer (requires: nothing, skips if < 10 commits)
    GitExtractor.extract() → GitHistory (commits with author/timestamp/files/message)
    _normalize_git_paths() → strips repo-root prefix from git paths
    build_cochange_matrix() → CoChangeMatrix (lift, confidence_a_b, confidence_b_a)
    build_churn_series() → dict[path, ChurnSeries]
      ChurnSeries fields: total_changes, trajectory, slope, cv, bus_factor,
                          author_entropy, fix_ratio, refactor_ratio, change_entropy
    compute_author_distances() → list[AuthorDistance] (1 - weighted_jaccard per pair)
    → store.git_history, store.cochange, store.churn, store.author_distances
    → FactStore signals: TOTAL_CHANGES, CHURN_CV, BUS_FACTOR, AUTHOR_ENTROPY,
        FIX_RATIO, REFACTOR_RATIO, CHURN_TRAJECTORY, CHURN_SLOPE
    → FactStore relations: COCHANGES_WITH (symmetric, weighted by lift)

  SpectralAnalyzer (requires: structural, needs numpy)
    Build undirected adjacency matrix
    Compute Laplacian L = D - A
    np.linalg.eigvalsh(L) → eigenvalues (sorted)
    fiedler_value = λ₂ (on largest component if disconnected)
    spectral_gap = λ₂/λ₃
    → store.spectral: SpectralSummary(fiedler_value, num_components, eigenvalues[:20], spectral_gap)
    → FactStore global: FIEDLER_VALUE, SPECTRAL_GAP

  SemanticAnalyzer (requires: file_syntax)
    Pass 1: ConceptExtractor.add_file() for all files → compute_idf()
    Pass 2 per file:
      classify_role(syntax, root_dir) → role enum
      extractor.extract(syntax, role) → concepts, concept_entropy, tier
      compute_import_fingerprint() → dict[module → weight]
      compute_naming_drift(path, concepts, tier) → float [0,1]
      compute_completeness(syntax, content) → docstring_coverage, todo_density
    → store.semantics: dict[path, FileSemantics]
    → store.roles: dict[path, str]
    → FactStore signals: CONCEPT_COUNT, CONCEPT_ENTROPY, NAMING_DRIFT,
        TODO_DENSITY, DOCSTRING_COVERAGE, ROLE
    → FactStore relations: SIMILAR_TO (cosine similarity of import fingerprints >= 0.5)

  ArchitectureAnalyzer (requires: structural, roles)
    detect_modules(file_paths, root_dir) → dict[path, Module]
    compute_module_metrics(mod, all_modules, graph, roles, node_community):
      cohesion = internal_edges / max_possible
      coupling = external_edges_out / max_possible
      instability = Ce/(Ca+Ce), or None if isolated
      abstractness = abstract_classes / total_classes (0.0 if no classes)
      main_seq_distance = |instability + abstractness - 1| (skip if None)
      boundary_alignment = fraction of files in majority Louvain community
      role_consistency = fraction with dominant role
    build_module_graph() → module-level import graph
    infer_layers() → topological ordering + violations
    violation_rate = violating_edges / total_cross_edges
    → store.architecture: Architecture
    → FactStore signals: COHESION, COUPLING, INSTABILITY (if not None),
        ABSTRACTNESS, MAIN_SEQ_DISTANCE, BOUNDARY_ALIGNMENT, FILE_COUNT
    → FactStore relations: IN_MODULE, DEPENDS_ON (weighted by edge count)

Wave 2:

  SignalFusionAnalyzer (runs AFTER all Wave 1)
    6-step typestate pipeline (enforces order at class level):

    Step 1 COLLECT: Read all store slots → SignalField
      - FileSignals per file (IR1 from syntax, IR3 from structural,
                              IR2 from semantics, IR5t from churn)
      - cognitive_load = log2(lines+1) × (1+complexity/10) × (1+nesting/5) × (1+gini)
      - semantic_coherence = 1/(1 + concept_entropy)
      - is_orphan refined with role awareness (ENTRY_POINT/TEST/CONFIG not orphans)
      - DirectorySignals (aggregate per directory)
      - ModuleSignals (from architecture slot)
      - GlobalSignals (orphan_ratio, phantom_ratio, glue_deficit, conway_alignment, team_size)

    Step 2 RAW_RISK: Pre-percentile risk per file
      raw_risk = simple weighted sum (used by health Laplacian; must precede percentiles)

    Step 3 NORMALIZE: Percentile computation
      pctl(v) = |files with value ≤ v| / total_files
      ABSOLUTE tier (<15 files) skips this step entirely

    Step 4 MODULE_TEMPORAL: Module-level temporal aggregates (reads percentiles)
      velocity = commits/week touching module
      coordination_cost = cross-module commits / total module commits
      knowledge_gini = Gini of per-author commit counts
      module_bus_factor = min bus_factor of files where pctl(pagerank) > 0.75

    Step 5 COMPOSITES: All 7 composite scores
      risk_score    = 0.25×pctl(pr) + 0.20×pctl(blast) + 0.20×pctl(cog)
                    + 0.20×min(churn_cv/2, 1) + 0.15×(1 - bus_factor/5)
      wiring_quality = 1 - (0.375×orphan + 0.3125×stub_ratio + 0.3125×phantom_ratio)
                     [broken_call_count term REMOVED, CALL edges not impl]
      file_health   = 1 - (0.25×risk + 0.25×(1-wiring) + 0.20×pctl(cog)
                     + 0.15×stub_ratio + 0.15×orphan)
      health_score  = 0.20×cohesion + 0.15×(1-coupling) + 0.20×(1-D)
                    + 0.15×boundary + 0.15×role_consistency + 0.15×(1-mean_stub)
                    [D term redistributed 1.25× if instability=None]
      wiring_score  = 1 - (0.25×orphan_ratio + 0.25×phantom_ratio + 0.20×glue_deficit
                     + 0.15×mean_stub + 0.15×clone_ratio)
      arch_health   = 0.25×(1-violation_rate) + 0.20×mean(cohesion) + 0.20×(1-mean(coupling))
                    + 0.20×(1-mean(D)) + 0.15×mean(boundary)
      codebase_hlth = 0.30×arch_health + 0.30×wiring_score + 0.20×(bf/team_size) + 0.20×modularity

    Step 6 LAPLACIAN: Health Laplacian
      delta_h[f] = raw_risk[f] - mean(raw_risk[neighbours])
                   positive = file is riskier than its import neighbourhood

    → store.signal_field: SignalField
    → FactStore: syncs ALL 67 signals (including re-syncing IR1/IR2/IR3 for pattern access)

Pattern Execution:
  execute_patterns(store.fact_store, ALL_PATTERNS, tier, max_findings×2)
  Patterns query FactStore via EntityId + Signal lookups + Relation queries
  → list[PatternFinding]

Ranking + Output:
  deduplicate_findings() → rank_findings() → cap at max_findings
  capture_tensor_snapshot() → TensorSnapshot → history.db
```

## FactStore Data Model

```
EntityId(type=FILE|MODULE|CODEBASE, key=path_or_root)
Entity(id=EntityId, metadata={})
Signal enum (67 members) → float|int|str|bool value per entity
Relation(type=RelationType, source=EntityId, target=EntityId, weight=float, metadata={})
```

RelationTypes (10): IMPORTS, COCHANGES_WITH, SIMILAR_TO, AUTHORED_BY,
                     IN_MODULE, CONTAINS, DEPENDS_ON, CLONED_FROM, CYCLE_WITH, AUTHOR_DISTANCE

## Persistence Databases

```
.shannon/
  facts.db      - file_facts, function_facts, class_facts, import_facts (7 tables)
  git_facts.db  - git_commits, git_file_changes, git_extraction_sessions (3 tables)
  graph_store.db- graph_edges, node_metrics, cycle_members, community_members (5 tables)
  history.db    - 16 tables: snapshots, signal_history, finding_lifecycle, etc.
  parquet/      - optional tensordb: file_signals, module_signals, global_signals, edges, findings
```

## Tier Logic (session.py)
- ABSOLUTE: < 15 files — no percentiles, absolute thresholds only
- BAYESIAN: 15-49 files — percentiles available but small-sample aware
- FULL: 50+ files — full percentile normalization

## Scanning Details
- TreeSitterNormalizer OR RegexFallbackScanner → same FileSyntax output
- tree-sitter: populates call_targets, decorators, return_type, param_types
- regex: call_targets=None (check this to know parser type)
- Import resolution: language-aware, stdlib-aware, relative + absolute paths
- Content cache: file text cached after scanning, released after fusion step 5
- NCD clone detection: threshold=0.30, minimum 20 lines

## Notable Incomplete Features (from code)
- BROKEN_CALL_COUNT = always 0, CALL edges not implemented yet
- CONWAY_VIOLATION pattern disabled (author_distance computation not wired to pattern)
- ABSOLUTE tier skips architecture_health, team_risk, codebase_health composites
- SpectralAnalyzer skips if numpy unavailable
- TemporalAnalyzer skips if < 10 commits
