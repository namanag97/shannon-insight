# TensorSnapshot Data Model

The universal output format for Shannon Insight. Every consumer (CLI, web UI, CI runner) reads this structure. Defined once here; referenced everywhere else.

## Full Schema

```python
@dataclass
class TensorSnapshot:
    # ── Metadata ──────────────────────────────────────────────
    version: str                          # "2.0" — schema version
    timestamp: str                        # ISO-8601 UTC
    commit_sha: Optional[str]             # HEAD at analysis time
    project: str                          # project root path
    tool_version: str                     # shannon-insight version
    config_hash: str                      # hash of AnalysisSettings

    # ── Per-file data (IR1 through IR5s) ─────────────────────
    files: Dict[str, FileData]            # path -> all file-level data

    # ── Per-module data (IR4 + IR5s) ─────────────────────────
    modules: Dict[str, ModuleData]        # module path -> module-level data

    # ── Graph data (IR3) ─────────────────────────────────────
    graph: GraphData                      # edges, communities, spectral

    # ── Architecture data (IR4) ──────────────────────────────
    architecture: ArchData                # layers, violations, patterns

    # ── Temporal data (IR5t) ─────────────────────────────────
    temporal: TemporalData                # co-change pairs, module dynamics

    # ── Global signals (IR3 + IR4 + IR5s) ────────────────────
    global_signals: GlobalData            # codebase-level signals

    # ── Insights (IR6) ───────────────────────────────────────
    findings: List[Finding]               # all findings with evidence chains
    composites: CompositeScores           # risk, health, wiring, team risk
    suggestions: List[Suggestion]         # prioritized action items

    # ── Run metadata ─────────────────────────────────────────
    config: AnalysisConfig                # which finders ran, thresholds
    timing: Dict[str, float]              # {ir_name: duration_ms}
    file_count: int
    module_count: int
    commits_analyzed: int
    analyzers_ran: List[str]
```

### FileData

All per-file signals from `registry/signals.md` (signals 1-36), grouped by source IR.

```python
@dataclass
class FileData:
    # From IR1 (scanning/)
    lines: int
    function_count: int
    class_count: int
    max_nesting: int
    impl_gini: float
    stub_ratio: float
    import_count: int

    # From IR2 (semantics/) -- NEW
    role: str                             # Role enum value
    concept_count: int
    concept_entropy: float
    naming_drift: float
    todo_density: float
    docstring_coverage: float

    # From IR3 (graph/)
    pagerank: float
    betweenness: float
    in_degree: int
    out_degree: int
    blast_radius_size: int
    depth: int
    is_orphan: bool
    phantom_import_count: int
    broken_call_count: int
    community: int
    compression_ratio: float
    semantic_coherence: float
    cognitive_load: float

    # From IR5t (temporal/)
    total_changes: int
    churn_trajectory: str                 # Trajectory enum value
    churn_slope: float
    churn_cv: float
    bus_factor: float
    author_entropy: float
    fix_ratio: float
    refactor_ratio: float

    # Composites (from IR5s)
    risk_score: float
    wiring_quality: float
```

### ModuleData

Per-module signals from `registry/signals.md` (signals 37-51).

```python
@dataclass
class ModuleData:
    path: str
    files: List[str]
    cohesion: float
    coupling: float
    instability: float
    abstractness: float
    main_seq_distance: float
    boundary_alignment: float
    layer_violation_count: int
    role_consistency: float
    velocity: float
    coordination_cost: float
    knowledge_gini: float
    module_bus_factor: float
    mean_cognitive_load: float
    file_count: int
    health_score: float
```

### GraphData

Serialized graph structure from IR3.

```python
@dataclass
class GraphData:
    edges: List[EdgeRecord]               # (src, dst, type, symbols, weight)
    unresolved_edges: List[UnresolvedRecord]
    communities: Dict[str, int]           # file -> community ID
    sccs: List[List[str]]                 # strongly connected components
    clone_pairs: List[ClonePair]          # (file_a, file_b, ncd_score)
```

### ArchData

Architecture model from IR4.

```python
@dataclass
class ArchData:
    layers: List[LayerRecord]             # (depth, module_paths)
    violations: List[ViolationRecord]     # (src_module, dst_module, type, count)
    patterns: ArchPatterns                # is_layered, is_modular, etc.
```

### TemporalData

Summary of temporal analysis from IR5t.

```python
@dataclass
class TemporalData:
    cochange_pairs: List[CochangeRecord]  # (file_a, file_b, lift, confidence)
    codebase_dynamics: CodebaseDynamicsRecord
```

### GlobalData

Codebase-level signals from `registry/signals.md` (signals 52-62).

```python
@dataclass
class GlobalData:
    modularity: float
    fiedler_value: float
    spectral_gap: float
    cycle_count: int
    centrality_gini: float
    orphan_ratio: float
    phantom_ratio: float
    glue_deficit: float
    wiring_score: float
    architecture_health: float
    codebase_health: float
```

### Finding (v2)

Extended from v1 with multi-IR evidence and temporal context.

```python
@dataclass
class Finding:
    id: str                               # stable hash (type + sorted targets)
    type: str                             # e.g. "HIGH_RISK_HUB"
    severity: float                       # [0, 1]
    confidence: float                     # [0, 1] -- NEW
    scope: str                            # FILE | MODULE | CODEBASE
    targets: List[str]                    # affected file/module paths
    evidence: List[Evidence]              # multi-IR evidence chain
    suggestion: str
    effort: str                           # LOW | MEDIUM | HIGH

    # Temporal context (populated from history)
    first_seen: Optional[str]             # ISO-8601
    persistence_count: int                # snapshots this has existed
    trend: str                            # WORSENING | STABLE | IMPROVING
    regression: bool                      # was resolved, came back

@dataclass
class Evidence:
    ir_source: str                        # "IR1", "IR2", etc. -- NEW
    signal: str
    value: Any
    percentile: Optional[float]
    description: str
```

## Serialization

### JSON

Human-readable export for debugging and CI integration. The full TensorSnapshot serializes to JSON with `json.dumps()`. All nested dataclasses implement `to_dict()`.

### SQLite

Primary local storage. See `storage-strategy.md` for the full schema. Key design: signals are stored as key-value rows (not columns) so new signals can be added without schema migration.

### PostgreSQL (hosted mode)

Same logical schema as SQLite, adapted for multi-tenant hosted deployment. Adds `project_id` and `team_id` foreign keys. Connection pool via asyncpg.

## Backward Compatibility

The v2 `TensorSnapshot` is a superset of the v1 `Snapshot`. The v1 fields map directly:

| v1 field | v2 location |
|----------|-------------|
| `file_signals` | `files[path].{signal_name}` |
| `codebase_signals` | `global_signals.{signal_name}` |
| `findings` | `findings` (extended with `confidence`, `ir_source`) |
| `dependency_edges` | `graph.edges` (extended with type, symbols, weight) |

See `migration.md` for the v1 to v2 migration procedure.
