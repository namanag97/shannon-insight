-- Parquet table schema definitions for the tensor DB migration.
--
-- These CREATE TABLE statements define the logical schema that DuckDB
-- uses when reading/writing Parquet files.  Each table maps 1:1 to an
-- event dataclass in events/schema.py.
--
-- Notes:
-- - No partitioning (optimize later when data volume justifies it)
-- - Percentiles computed on read via DuckDB window functions
-- - VARCHAR for JSON blobs (evidence, data)
-- - All signal columns are nullable (missing = not computed)

-- ─────────────────────────────────────────────────────────────────
-- Snapshot metadata
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id       VARCHAR PRIMARY KEY,
    timestamp         VARCHAR NOT NULL,
    commit_sha        VARCHAR,
    analyzed_path     VARCHAR NOT NULL,
    tool_version      VARCHAR NOT NULL,
    schema_version    INTEGER NOT NULL DEFAULT 2,
    file_count        INTEGER NOT NULL DEFAULT 0,
    module_count      INTEGER NOT NULL DEFAULT 0,
    commits_analyzed  INTEGER NOT NULL DEFAULT 0,
    analyzers_ran     VARCHAR NOT NULL DEFAULT '[]',  -- JSON array
    config_hash       VARCHAR NOT NULL DEFAULT ''
);

-- ─────────────────────────────────────────────────────────────────
-- Per-file signals (wide table: 1 row per file per snapshot)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS file_signals (
    snapshot_id           VARCHAR NOT NULL,
    file_path             VARCHAR NOT NULL,

    -- IR1 (scanning) - signals #1-7
    lines                 INTEGER,
    function_count        INTEGER,
    class_count           INTEGER,
    max_nesting           INTEGER,
    impl_gini             DOUBLE,
    stub_ratio            DOUBLE,
    import_count          INTEGER,

    -- IR2 (semantics) - signals #8-13
    role                  VARCHAR,
    concept_count         INTEGER,
    concept_entropy       DOUBLE,
    naming_drift          DOUBLE,
    todo_density          DOUBLE,
    docstring_coverage    DOUBLE,

    -- IR3 (graph) - signals #14-26
    pagerank              DOUBLE,
    betweenness           DOUBLE,
    in_degree             INTEGER,
    out_degree            INTEGER,
    blast_radius_size     INTEGER,
    depth                 INTEGER,
    is_orphan             BOOLEAN,
    phantom_import_count  INTEGER,
    broken_call_count     INTEGER,
    community             INTEGER,
    compression_ratio     DOUBLE,
    semantic_coherence    DOUBLE,
    cognitive_load        DOUBLE,

    -- IR5t (temporal) - signals #27-34
    total_changes         INTEGER,
    churn_trajectory      VARCHAR,
    churn_slope           DOUBLE,
    churn_cv              DOUBLE,
    bus_factor            DOUBLE,
    author_entropy        DOUBLE,
    fix_ratio             DOUBLE,
    refactor_ratio        DOUBLE,

    -- Pre-percentile risk
    raw_risk              DOUBLE,

    -- Composites
    risk_score            DOUBLE,
    wiring_quality        DOUBLE,
    file_health_score     DOUBLE,

    -- Health Laplacian delta
    delta_h               DOUBLE,

    PRIMARY KEY (snapshot_id, file_path)
);

-- ─────────────────────────────────────────────────────────────────
-- Per-module signals
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS module_signals (
    snapshot_id           VARCHAR NOT NULL,
    module_path           VARCHAR NOT NULL,

    -- Martin metrics - signals #37-41
    cohesion              DOUBLE,
    coupling              DOUBLE,
    instability           DOUBLE,
    abstractness          DOUBLE,
    main_seq_distance     DOUBLE,

    -- Boundary analysis - signals #42-44
    boundary_alignment    DOUBLE,
    layer_violation_count INTEGER,
    role_consistency      DOUBLE,

    -- Module temporal - signals #45-48
    velocity              DOUBLE,
    coordination_cost     DOUBLE,
    knowledge_gini        DOUBLE,
    module_bus_factor     DOUBLE,

    -- Aggregated - signals #49-50
    mean_cognitive_load   DOUBLE,
    file_count            INTEGER,

    -- Composite - signal #51
    health_score          DOUBLE,

    PRIMARY KEY (snapshot_id, module_path)
);

-- ─────────────────────────────────────────────────────────────────
-- Global signals (1 row per snapshot)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS global_signals (
    snapshot_id           VARCHAR PRIMARY KEY,

    -- Graph structure - signals #52-56
    modularity            DOUBLE,
    fiedler_value         DOUBLE,
    spectral_gap          DOUBLE,
    cycle_count           INTEGER,
    centrality_gini       DOUBLE,

    -- Wiring quality - signals #57-59
    orphan_ratio          DOUBLE,
    phantom_ratio         DOUBLE,
    glue_deficit          DOUBLE,

    -- Phase 3/4 derived
    clone_ratio           DOUBLE,
    violation_rate        DOUBLE,
    conway_alignment      DOUBLE,
    team_size             INTEGER,

    -- Composites - signals #60-62
    wiring_score          DOUBLE,
    architecture_health   DOUBLE,
    team_risk             DOUBLE,
    codebase_health       DOUBLE
);

-- ─────────────────────────────────────────────────────────────────
-- Unified edges (G1/G4/G5/G6)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS edges (
    snapshot_id  VARCHAR NOT NULL,
    source       VARCHAR NOT NULL,
    target       VARCHAR NOT NULL,
    space        VARCHAR NOT NULL,  -- 'G1' | 'G4' | 'G5' | 'G6'
    weight       DOUBLE NOT NULL DEFAULT 1.0,
    data         VARCHAR           -- JSON blob for extra metadata
);

-- ─────────────────────────────────────────────────────────────────
-- Findings
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS findings (
    snapshot_id    VARCHAR NOT NULL,
    finding_type   VARCHAR NOT NULL,
    identity_key   VARCHAR NOT NULL,
    severity       DOUBLE NOT NULL,
    title          VARCHAR NOT NULL,
    files          VARCHAR NOT NULL DEFAULT '[]',  -- JSON array
    evidence       VARCHAR NOT NULL DEFAULT '[]',  -- JSON array
    suggestion     VARCHAR NOT NULL DEFAULT '',
    confidence     DOUBLE NOT NULL DEFAULT 1.0,
    effort         VARCHAR NOT NULL DEFAULT 'MEDIUM',
    scope          VARCHAR NOT NULL DEFAULT 'FILE'
);
