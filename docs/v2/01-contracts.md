# Inter-Module Contracts

The wiring diagram of Shannon Insight. What each module exports, what it requires, and how data flows between them.

## Data Flow

```
  SOURCE FILES ────→ scanning/ ────→ semantics/ ──┐
                      (IR0+IR1)       (IR2)        │
                                                   ├──→ graph/ ──→ architecture/
  GIT HISTORY ─────→ temporal/ ───────────────────┘     (IR3)       (IR4)
                      (IR5t)           (parallel)       │            │
                                                        ├────────────┤
                                                        ▼            │
                                                   signals/ ◄───────┘
                                                    (IR5s)
                                                        │
                                                        ▼
                                                   insights/
                                                    (IR6)
                                                        │
                              ┌──────────────┤
                              ▼              ▼
                          persistence/   cli/ + JSON
```

## Module Contracts

### scanning/ (IR0 + IR1)

| | |
|---|---|
| **Exports** | `ScannerFactory`, `UniversalScanner`, `FileEntry`, `FileSyntax`, `FunctionDef`, `ClassDef`, `ImportDecl` |
| **Requires** | Nothing (pipeline root) |
| **Feeds** | semantics/ (FileSyntax), graph/ (imports, calls, classes) |
| **Computes signals** | `lines`, `function_count`, `class_count`, `max_nesting`, `impl_gini`, `stub_ratio`, `import_count` |
| **Temporal contract** | Output at time t: FileSyntax(f, t). Delta: SyntaxDelta (functions/imports added/removed/modified). Reconstruct: `git show <sha>:<path>` → re-parse. |

### semantics/ (IR2) — NEW

| | |
|---|---|
| **Exports** | `SemanticAnalyzer`, `FileSemantics`, `Role`, `Concept`, `Symbol`, `Completeness` |
| **Requires** | scanning/ (FileSyntax) |
| **Feeds** | graph/ (annotated nodes, roles for orphan detection), signals/ (concept signals) |
| **Computes signals** | `role`, `concept_count`, `concept_entropy`, `naming_drift`, `todo_density`, `docstring_coverage` |
| **Temporal contract** | Output at time t: FileSemantics(f, t). Delta: SemanticDelta (role_changed, concepts_added/removed, concept_drift). Key time series: concept_drift(f, t) = cumulative cosine distance from origin. Reconstruct: re-run on historical FileSyntax. |

### graph/ (IR3)

| | |
|---|---|
| **Exports** | `GraphBuilder`, `CodeGraph`, `GraphMetrics`, `Edge`, `FileNode`, `UnresolvedEdge` |
| **Requires** | scanning/ (imports, calls for edge construction), semantics/ (roles for orphan classification), temporal/ (co-change for edge enrichment, optional) |
| **Feeds** | architecture/ (file graph for module contraction), signals/ (centrality, connectivity), insights/ (graph data for finders) |
| **Computes signals** | `pagerank`, `betweenness`, `in_degree`, `out_degree`, `blast_radius_size`, `depth`, `is_orphan`, `phantom_import_count`, `broken_call_count`, `community`, `compression_ratio`, `semantic_coherence`, `cognitive_load` |
| **Also produces** | `modularity`, `fiedler_value`, `spectral_gap`, `cycle_count`, `centrality_gini`, `orphan_ratio`, `phantom_ratio`, `glue_deficit` (global signals), NCD clone pairs, 6 distance spaces |
| **Temporal contract** | Output at time t: CodeGraph(t), GraphMetrics(t). Delta: GraphDelta (edges added/removed, new/broken cycles, community migration, pagerank delta). Reconstruct: rebuild graph from historical FileSyntax + ImportDecl. |

### architecture/ (IR4) — NEW

| | |
|---|---|
| **Exports** | `ArchitectureAnalyzer`, `Architecture`, `Module`, `Layer`, `Violation`, `ArchPatterns`, `ArchHealth` |
| **Requires** | graph/ (file graph, communities), semantics/ (file roles) |
| **Feeds** | signals/ (module-level metrics), insights/ (architecture finders) |
| **Computes signals** | `cohesion`, `coupling`, `instability`, `abstractness`, `main_seq_distance`, `boundary_alignment`, `layer_violation_count`, `role_consistency`, `file_count` |
| **Also produces** | `architecture_health` (global composite), layer assignments, violation list, architectural patterns |
| **Temporal contract** | Output at time t: Architecture(t). Delta: ArchDelta (modules split/merged, layer changes, new/resolved violations). Key time series: violation_rate(t), architecture drift velocity. Reconstruct: rebuild from historical CodeGraph. |

### temporal/ (IR5t)

| | |
|---|---|
| **Exports** | `TemporalExtractor`, `TemporalModel`, `FileHistory`, `PairDynamics`, `ModuleDynamics`, `CodebaseDynamics` |
| **Requires** | Nothing (parallel spine — reads git directly) |
| **Feeds** | graph/ (co-change enrichment), signals/ (churn/author signals), insights/ (temporal finders) |
| **Computes signals** | `total_changes`, `churn_trajectory`, `churn_slope`, `churn_cv`, `bus_factor`, `author_entropy`, `fix_ratio`, `refactor_ratio`, `velocity`, `coordination_cost`, `knowledge_gini`, `module_bus_factor` |
| **Also produces** | Co-change pairs (lift, confidence), codebase dynamics |
| **Temporal contract** | This module IS temporal data (Kind 1). Not parameterized by snapshot time — it reads the full git history each run. Module dynamics and codebase dynamics are intrinsically temporal. |

### signals/ (IR5s)

| | |
|---|---|
| **Exports** | `SignalFusion`, `SignalField`, `FileSignals`, `ModuleSignals`, `GlobalSignals` |
| **Requires** | ALL other modules (scanning, semantics, graph, architecture, temporal) |
| **Feeds** | insights/ (the signal field that finders evaluate against) |
| **Computes signals** | `risk_score`, `wiring_quality`, `health_score`, `wiring_score`, `architecture_health`, `team_risk`, `codebase_health` (all composites) |
| **Responsibilities** | Percentile normalization, tiered analysis (small codebases), composite score computation, health Laplacian computation. Two-wave execution: SignalFusion runs in Wave 2 (after all Wave 1 analyzers complete) |
| **Temporal contract** | Output at time t: SignalField(t). Every signal becomes a time series S(f, t₀..tₙ). Applies temporal operators (delta, velocity, trend) to all numeric signals. Stores historical signal values for sparklines. |

### insights/ (IR6)

| | |
|---|---|
| **Exports** | `InsightKernel`, `InsightResult`, `Finding`, `Evidence`, `Suggestion`, `CompositeScores` |
| **Requires** | signals/ (SignalField) |
| **Feeds** | persistence/ (results to store), cli/ (results to display) |
| **Responsibilities** | Signal registry for demand-driven evaluation, topological sort of analyzer/finder dependencies, finding predicate evaluation, evidence chain construction, severity/confidence scoring |
| **Computes** | All 22 finding types (see `registry/finders.md`) |
| **Temporal contract** | Output at time t: InsightResult(t). Delta: InsightDelta (new/resolved/persisting/regression findings). Debt velocity = \|new\| - \|resolved\|. Finding IDs are stable hashes for cross-snapshot tracking. |

### persistence/

| | |
|---|---|
| **Exports** | `SnapshotWriter`, `SnapshotReader`, `DiffEngine`, `TensorSnapshot` |
| **Requires** | insights/ (InsightResult to serialize), signals/ (SignalField to store) |
| **Feeds** | cli/ (historical data for diff/health/history commands), web/ (data for all views) |
| **Responsibilities** | TensorSnapshot serialization, SQLite storage, per-IR persistence strategy, snapshot diffing, rename detection, change-scoped analysis |

### cli/

| | |
|---|---|
| **Exports** | `app` (Typer application) |
| **Requires** | insights/ (InsightKernel), persistence/ (history), config |
| **Commands** | main, explain, diff, health, history, report, serve (new) |

### web/ — BACKLOGGED (see BACKLOG.md B7)

## Parallelism

The structural spine and temporal spine run fully in parallel:

```
STRUCTURAL SPINE              TEMPORAL SPINE
scanning/ (IR0→IR1)           temporal/ (git → IR5t)
    ↓                              │
semantics/ (IR2)                   │
    ↓                              │
graph/ (IR3) ◄─────────────────────┘  (co-change enrichment)
    ↓
architecture/ (IR4)
    ↓
signals/ (IR5s) ◄── reads ALL
    ↓
insights/ (IR6)
```

Zero data dependencies between spines until graph/ merges them.

## Temporal Architecture

See `registry/temporal-operators.md` for full specification. Summary:

- **Kind 1** (git-derived): `temporal/` computes from git log. Always available.
- **Kind 2** (cross-snapshot): `persistence/` stores and compares analysis runs. Requires `--save`.
- **Kind 3** (reconstruction): BACKLOGGED (see `BACKLOG.md` B2). Re-run pipeline at historical commits.

Every module has a temporal contract (defined in its README.md) specifying: output at time t, structured delta, time series, and reconstruction method.
