# Shannon Insight Pipeline Specification

## Document Information

| Field        | Value                |
| ------------ | -------------------- |
| Version      | 2.0                  |
| Status       | Draft Specification  |
| Last Updated | 2026-02-19           |
| Authors      | Shannon Insight Team |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Mathematical Foundation](#2-mathematical-foundation)
3. [Pipeline Overview](#3-pipeline-overview)
4. [Stage Specifications](#4-stage-specifications)
5. [Database Schema](#5-database-schema)
6. [Runtime Analysis](#6-runtime-analysis)
7. [Consistency Model](#7-consistency-model)
8. [Failure Modes & Recovery](#8-failure-modes--recovery)
9. [Incremental Computation](#9-incremental-computation)
10. [Observability](#10-observability)
11. [Constraints & Limitations](#11-constraints--limitations)

---

## 1. Executive Summary

### 1.1 Purpose

This document specifies a staged mathematical pipeline for codebase analysis that:

- Extracts structural and temporal data from source code and git history
- Constructs a **multi-layer relationship tensor** T ∈ ℝ^(N×N×K×R)
- Computes **79 signals** across 7 layers of abstraction
- Detects **22 patterns** indicating code health issues
- Persists all intermediate results for auditability and incremental updates

### 1.2 Mathematical Foundation

The pipeline implements a **tensor-based multi-layer graph analysis** system:

```
Core Tensor: T ∈ ℝ^(N × N × K × R)
  N = maximum number of files across all time
  K = number of time points
  R = number of relationship types

T[i, j, t, r] = weight of relationship r between files i and j at time t
```

Key operations:
- **Tensor slicing**: Extract G_r(t) = T[:,:,t,r] for each layer/time
- **Tensor reduction**: Aggregate across time or relationships
- **Tensor decomposition**: Low-rank approximation for efficient analysis
- **Temporal derivatives**: d/dt of graph signals for trajectory analysis

### 1.3 Design Principles

| Principle          | Description                                            |
| ------------------ | ------------------------------------------------------ |
| Persistence-First  | Every stage writes to DB before the next stage reads   |
| Incremental        | Only recompute what changed since last run             |
| Auditable          | Any signal value traceable to source data              |
| Recoverable        | Failed runs resume from last successful stage          |
| Deterministic      | Same inputs produce same outputs                       |
| Mathematically Rigorous | All operations have formal definitions             |

### 1.4 Pipeline Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SHANNON INSIGHT PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ Stage 0  │──▶│ Stage 1  │──▶│ Stage 2  │──▶│ Stage 3  │──▶│ Stage 4  │ │
│  │ Extract  │   │  Index   │   │  Graph   │   │ Signals  │   │ Patterns │ │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘ │
│       │              │              │              │              │       │
│       ▼              ▼              ▼              ▼              ▼       │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ facts.db │   │temporal.db│  │ graph.db │   │signals.db│   │finds.db │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mathematical Foundation

### 2.1 The Fundamental Tensor

The core data structure is a 4-dimensional tensor representing all relationships over time:

```
T ∈ ℝ^(N × N × K × R)

Dimension meanings:
  dim[0] = source node (files, indexed 0 to N-1)
  dim[1] = target node (files, indexed 0 to N-1)
  dim[2] = time (snapshots, indexed 0 to K-1)
  dim[3] = relationship type (indexed 0 to R-1)

Relationship types R:
  0: IMPORT      (syntax-level dependencies)
  1: COCHANGE    (behavioral coupling from git)
  2: AUTHOR      (social coupling from authors)
  3: SEMANTIC    (concept similarity)
  4: CLONE       (code duplication)
  5: COMBINED    (weighted fusion of all)
```

### 2.2 Tensor Slicing Operations

| Slice                    | Notation      | Result      | Meaning                              |
| ------------------------ | ------------- | ----------- | ------------------------------------ |
| Fix time, fix relation   | T[:,:,t,r]    | N×N matrix  | Graph Gᵣ at time t                   |
| Fix relation             | T[:,:,:,r]    | N×N×K tensor| Evolution of Gᵣ over time            |
| Fix time                 | T[:,:,t,:]    | N×N×R tensor| Multi-layer graph at time t          |
| Fix node pair            | T[i,j,:,:]    | K×R matrix  | All relationships between i,j over time |
| Fix source node          | T[i,:,t,r]    | N vector    | Neighbors of i in Gᵣ(t)              |

### 2.3 Tensor Reduction Operations

| Operation           | Notation               | Definition                   | Use Case          |
| ------------------- | ---------------------- | ---------------------------- | ----------------- |
| Sum over time       | Σₜ T[:,:,t,r]          | Cumulative relationship      | Total co-change   |
| Mean over time      | (1/K) Σₜ T[:,:,t,r]    | Average relationship         | Stable coupling   |
| Max over time       | maxₜ T[i,j,t,r]        | Peak relationship            | Maximum coupling  |
| Sum over relations  | Σᵣ αᵣ T[:,:,t,r]       | Combined graph               | Multi-layer fusion|

### 2.4 Graph-Theoretic Derivations

For any graph G_r(t) = T[:,:,t,r]:

```
Adjacency matrix:      A[r,t] = T[:,:,t,r]
Degree matrix:         D[r,t][i,i] = Σⱼ A[r,t][i,j]
Laplacian:             L[r,t] = D[r,t] - A[r,t]
Normalized Laplacian:  L_norm[r,t] = I - D[r,t]^(-1/2) A[r,t] D[r,t]^(-1/2)
Transition matrix:     P[r,t] = D[r,t]^(-1) A[r,t]
```

### 2.5 Temporal Operators

**Point Operators:**
```
s(v)           = s(v, t_now)           Current value
s(v, t)        = Value at time t       Historical lookup
s₀(v)          = s(v, birth(v))        Value at birth
s_end(v)       = s(v, death(v))        Value at death
```

**Window Operators** (window w = [t-Δ, t]):
```
μ_w(s, v)      = (1/|w|) Σ_{τ∈w} s(v, τ)           Mean
σ_w(s, v)      = √(Var_{τ∈w}(s(v, τ)))              Std deviation
min_w(s, v)    = min_{τ∈w} s(v, τ)                  Minimum
max_w(s, v)    = max_{τ∈w} s(v, τ)                  Maximum
β_w(s, v)      = Linear regression slope in w      Trend
```

**Derivative Operators:**
```
Ds(v, t)       = (s(v,t) - s(v,t-Δ)) / Δ           Velocity
D²s(v, t)      = (Ds(v,t) - Ds(v,t-Δ)) / Δ         Acceleration
D̄s(v, t)       = β_w(s, v)                         Smoothed velocity
```

**Stability Operators:**
```
cv(s, v)       = σ(s,v) / μ(s,v)                   Coefficient of variation
stability(s,v) = 1 / (1 + cv(s,v))                 Stability ∈ (0, 1]
H(s, v)        = -Σ p(s) log p(s)                  Entropy
```

### 2.6 Information-Theoretic Measures

**Shannon Entropy:**
```
H(X) = -Σᵢ p(xᵢ) log₂ p(xᵢ)
```

**Mutual Information between Graphs:**
```
I(G₁; G₂) = Σₐ Σᵦ (nₐᵦ/n) log₂[(nₐᵦ × n) / (nₐ• × n•ᵦ)]

where:
  n₁₁ = |{(i,j) : A₁[i,j]=1 ∧ A₂[i,j]=1}|  (both have edge)
  n₁₀ = |{(i,j) : A₁[i,j]=1 ∧ A₂[i,j]=0}|  (only G₁)
  n₀₁ = |{(i,j) : A₁[i,j]=0 ∧ A₂[i,j]=1}|  (only G₂)
  n₀₀ = |{(i,j) : A₁[i,j]=0 ∧ A₂[i,j]=0}|  (neither)
  n = n₁₁ + n₁₀ + n₀₁ + n₀₀
```

**Normalized Mutual Information:**
```
NMI(X,Y) = 2 I(X;Y) / (H(X) + H(Y))
Range: [0, 1]
```

**Transfer Entropy (Causality):**
```
T(X→Y) = I(Y_{t+1}; X_t | Y_t)
       = H(Y_{t+1}|Y_t) - H(Y_{t+1}|Y_t,X_t)
```

---

## 3. Pipeline Overview

### 3.1 Stage Dependency Graph

```
                    ┌──────────────────┐
                    │   Source Code    │
                    │   + Git Repo     │
                    └────────┬─────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 0: Raw Extraction     │
              │  ─────────────────────────   │
              │  • Parse files → FileSyntax  │
              │  • Extract git → Commits     │
              │  • Extract diffs → Changes   │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 1: Temporal Index     │
              │  ─────────────────────────   │
              │  • Build event log           │
              │  • Compute node lifecycle    │
              │  • Compute edge lifecycle    │
              │  • Build time windows        │
              └──────────────┬───────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  STAGE 2a   │   │  STAGE 2b   │   │  STAGE 2c   │
    │  ─────────  │   │  ─────────  │   │  ─────────  │
    │  G_import   │   │  G_cochange │   │  G_semantic │
    │  G_clone    │   │  G_author   │   │             │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 2d: Graph Fusion      │
              │  ─────────────────────────   │
              │  • Build G_combined          │
              │  • Sample historical graphs  │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 3a: Graph Algorithms  │
              │  ─────────────────────────   │
              │  • PageRank per layer        │
              │  • Louvain per layer         │
              │  • Spectral per layer        │
              │  • SCC, depth, blast radius  │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 3b: Trajectory        │
              │  ─────────────────────────   │
              │  • Compute derivatives       │
              │  • Stability measures        │
              │  • Trend analysis            │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 3c: Cross-Layer       │
              │  ─────────────────────────   │
              │  • Mutual information        │
              │  • Hidden coupling           │
              │  • Coherence measures        │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 3d: Composites        │
              │  ─────────────────────────   │
              │  • Normalization             │
              │  • Risk scores               │
              │  • Health scores             │
              │  • Aggregation               │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 4: Pattern Detection  │
              │  ─────────────────────────   │
              │  • Evaluate 22 finders       │
              │  • Score and rank            │
              │  • Link to evidence          │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  STAGE 5: Snapshot Seal      │
              │  ─────────────────────────   │
              │  • Link all artifacts        │
              │  • Compute diff from prior   │
              │  • Archive snapshot          │
              └──────────────────────────────┘
```

### 3.2 Stage Summary Table

| Stage | Name                | Inputs      | Outputs                        | DB Tables                         | Parallelizable |
| ----- | ------------------- | ----------- | ------------------------------ | --------------------------------- | -------------- |
| 0     | Raw Extraction      | Files, Git  | FileSyntax, Commits, Diffs     | file_facts, git_commits, ...      | Yes (per file) |
| 1     | Temporal Index      | Stage 0     | Events, Lifecycles, Windows    | events, node_lifecycle, ...       | Partial        |
| 2a    | Import Graph        | Stage 0, 1  | G_import(t)                    | graph_edges[IMPORT]               | Yes            |
| 2b    | Temporal Graphs     | Stage 1     | G_cochange, G_author           | graph_edges[COCHANGE/AUTHOR]      | Yes            |
| 2c    | Semantic Graph      | Stage 0     | G_semantic, G_clone            | graph_edges[SEMANTIC/CLONE]       | Yes            |
| 2d    | Graph Fusion        | Stage 2a-c  | G_combined, Historical samples | graph_edges[COMBINED], graph_hist | No             |
| 3a    | Graph Algorithms    | Stage 2     | Node signals, Global signals   | node_signals, global_signals      | Yes (per graph)|
| 3b    | Trajectory          | Stage 3a+   | Derivatives, Stability         | trajectory_signals                | No             |
| 3c    | Cross-Layer         | Stage 2, 3a | MI, Coherence, Hidden coupling | cross_layer_signals               | Partial        |
| 3d    | Composites          | Stage 3a-c  | Risk, Health, Aggregates       | composite_signals                 | Yes (per entity)|
| 4     | Patterns            | Stage 3     | Findings                       | findings, finding_evidence        | Yes (per pattern)|
| 5     | Snapshot            | All         | Sealed snapshot                | snapshots, snapshot_artifacts     | No             |

---

## 4. Stage Specifications

### 4.0 Stage 0: Raw Extraction

#### Purpose

Extract raw facts from source files and git repository. This is the only stage that touches the filesystem and git directly.

#### Inputs

| Input        | Source                | Description                        |
| ------------ | --------------------- | ---------------------------------- |
| Source files | Filesystem            | All files matching language extensions |
| Git repo     | .git/                 | Full git history                   |
| Config       | shannon-insight.toml  | Exclusion patterns, limits         |

#### Processing Steps

```
0.1 Discover files
    ├── Walk directory tree
    ├── Apply exclusion patterns (95 default patterns)
    ├── Filter by extension (8 supported languages)
    └── Respect max_files limit

0.2 Parse each file (parallelizable)
    ├── Detect language from extension
    ├── Parse with tree-sitter (if available) or regex fallback
    ├── Extract: functions, classes, imports, complexity, nesting
    ├── Compute content_hash = SHA256(content)
    └── Store FileSyntax record

0.3 Extract git commits
    ├── git log --all --format="%H|%at|%ae|%s"
    ├── Parse into Commit records
    ├── Limit to max_commits (default 5000)
    └── Store GitCommit records

0.4 Extract file changes
    ├── git log --all --name-status --numstat
    ├── For each commit: files added, modified, deleted, renamed
    ├── For modified files: additions, deletions counts
    └── Store GitFileChange records

0.5 Extract import changes from diffs (optional, for edge lifecycle)
    ├── git log --all -p --diff-filter=M -- "*.py" "*.ts" ...
    ├── Parse diffs for import statement changes
    ├── Detect: import added, import removed
    └── Store ImportChange records
```

#### Outputs

| Output        | Table             | Description                  |
| ------------- | ----------------- | ---------------------------- |
| FileSyntax    | file_facts        | Parsed syntax per file       |
| GitCommit     | git_commits       | Commit metadata              |
| GitFileChange | git_file_changes  | Per-file changes per commit  |
| ImportChange  | import_changes    | Import add/remove events     |

#### Database Schema

```sql
-- File facts from parsing
CREATE TABLE file_facts (
    id              INTEGER PRIMARY KEY,
    session_id      TEXT NOT NULL,
    path            TEXT NOT NULL,
    content_hash    TEXT NOT NULL,
    language        TEXT NOT NULL,
    lines           INTEGER NOT NULL,
    functions       INTEGER NOT NULL,
    classes         INTEGER NOT NULL,
    imports         INTEGER NOT NULL,
    complexity      INTEGER NOT NULL,
    max_nesting     INTEGER NOT NULL,
    stub_count      INTEGER NOT NULL,
    created_at      INTEGER NOT NULL,

    UNIQUE(session_id, path)
);

CREATE INDEX idx_file_facts_session ON file_facts(session_id);
CREATE INDEX idx_file_facts_hash ON file_facts(content_hash);

-- Git commits
CREATE TABLE git_commits (
    hash            TEXT PRIMARY KEY,
    timestamp       INTEGER NOT NULL,
    author_email    TEXT NOT NULL,
    subject         TEXT NOT NULL,
    session_id      TEXT NOT NULL
);

CREATE INDEX idx_git_commits_ts ON git_commits(timestamp);
CREATE INDEX idx_git_commits_author ON git_commits(author_email);

-- File changes per commit
CREATE TABLE git_file_changes (
    id              INTEGER PRIMARY KEY,
    commit_hash     TEXT NOT NULL REFERENCES git_commits(hash),
    file_path       TEXT NOT NULL,
    change_type     TEXT NOT NULL,  -- 'A', 'M', 'D', 'R'
    old_path        TEXT,           -- for renames
    additions       INTEGER,
    deletions       INTEGER,

    UNIQUE(commit_hash, file_path)
);

CREATE INDEX idx_git_changes_file ON git_file_changes(file_path);
CREATE INDEX idx_git_changes_commit ON git_file_changes(commit_hash);

-- Import changes from diffs (optional)
CREATE TABLE import_changes (
    id              INTEGER PRIMARY KEY,
    commit_hash     TEXT NOT NULL REFERENCES git_commits(hash),
    file_path       TEXT NOT NULL,
    change_type     TEXT NOT NULL,  -- 'add', 'remove'
    import_target   TEXT NOT NULL,  -- resolved import path
    timestamp       INTEGER NOT NULL
);
```

#### Runtime Characteristics

| Metric          | Value                                 | Notes                    |
| --------------- | ------------------------------------- | ------------------------ |
| Time complexity | O(files × avg_file_size + commits)    | Dominated by parsing     |
| Space complexity| O(files + commits + changes)          | Linear storage           |
| Parallelism     | High                                  | Files parsed independently|
| I/O pattern     | Read-heavy                            | Filesystem + git         |
| Typical runtime | 1-5 min for 1000 files, 5000 commits  | Depends on git depth     |

#### Incremental Strategy

On subsequent runs:
1. Load existing file_facts for session
2. For each file:
   a. Compute content_hash
   b. If hash matches existing record → skip parsing
   c. If hash differs or new file → parse and upsert
3. For git:
   a. Find last processed commit hash
   b. Extract only commits since then
   c. Append new commits and file changes

---

### 4.1 Stage 1: Temporal Index

#### Purpose

Build a temporal index that enables efficient reconstruction of any graph at any historical time point.

#### Mathematical Definition

The temporal index materializes the tensor dimension K (time) through an event-sourced architecture:

```
Event Log: E = {e₁, e₂, ..., e_m}
  where e_i = (timestamp, event_type, source, target, metadata)

Node Lifecycle: L_node = {(path, birth_ts, death_ts, canonical_path)}
Edge Lifecycle: L_edge = {(relation, source, target, birth_ts, death_ts)}
```

Graph reconstruction at time t:
```
G(t) = {e ∈ E : e.birth_ts ≤ t < e.death_ts}
```

#### Inputs

| Input           | Source  | Description             |
| --------------- | ------- | ----------------------- |
| file_facts      | Stage 0 | Current file state      |
| git_commits     | Stage 0 | Commit history          |
| git_file_changes| Stage 0 | File changes per commit |
| import_changes  | Stage 0 | Import add/remove events|

#### Processing Steps

```
1.1 Build event log (append-only)
    ├── For each file change:
    │   ├── change_type='A' → emit NODE_ADD event
    │   ├── change_type='D' → emit NODE_REMOVE event
    │   └── change_type='R' → emit NODE_RENAME event
    ├── For each import change:
    │   ├── change_type='add' → emit EDGE_ADD(IMPORT) event
    │   └── change_type='remove' → emit EDGE_REMOVE(IMPORT) event
    └── Sort events by timestamp

1.2 Compute node lifecycle
    ├── For each unique file path:
    │   ├── birth_ts = min(timestamp where NODE_ADD)
    │   ├── death_ts = max(timestamp where NODE_REMOVE) or NULL
    │   └── canonical_path = resolve rename chains
    └── Handle renames: old_path → canonical_path mapping

1.3 Compute edge lifecycle (for IMPORT edges)
    ├── For each (source, target) pair:
    │   ├── birth_ts = timestamp of EDGE_ADD
    │   └── death_ts = timestamp of EDGE_REMOVE or NULL
    └── Store lifecycle records

1.4 Build time windows
    ├── Define window_size (default: 4 weeks = 28 days)
    ├── Partition commits into windows
    ├── For each window:
    │   ├── Compute cochange counts: {(a,b): count}
    │   ├── Compute author counts: {file: {author: count}}
    │   └── Compute churn counts: {file: changes}
    └── Store window aggregates
```

#### Outputs

| Output         | Table            | Description                |
| -------------- | ---------------- | -------------------------- |
| Events         | events           | Append-only event log      |
| Node lifecycle | node_lifecycle   | Birth/death per file       |
| Edge lifecycle | edge_lifecycle   | Birth/death per edge       |
| Time windows   | time_windows     | Pre-aggregated window data |
| Window cochange| window_cochange  | Co-change counts per window|
| Window authors | window_authors   | Author counts per window   |

#### Database Schema

```sql
-- Append-only event log
CREATE TABLE events (
    id              INTEGER PRIMARY KEY,
    timestamp       INTEGER NOT NULL,
    commit_hash     TEXT NOT NULL,
    event_type      TEXT NOT NULL,  -- NODE_ADD, NODE_REMOVE, NODE_RENAME, EDGE_ADD, EDGE_REMOVE
    relation_type   TEXT,           -- NULL for node events, 'IMPORT' etc for edge events
    source_path     TEXT NOT NULL,
    target_path     TEXT,           -- for edges and renames
    author          TEXT NOT NULL,
    metadata        TEXT            -- JSON for additional data
);

CREATE INDEX idx_events_ts ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_source ON events(source_path);

-- Node lifecycle
CREATE TABLE node_lifecycle (
    path            TEXT PRIMARY KEY,
    canonical_path  TEXT NOT NULL,
    birth_ts        INTEGER NOT NULL,
    death_ts        INTEGER,        -- NULL if still alive
    birth_commit    TEXT NOT NULL,
    death_commit    TEXT
);

CREATE INDEX idx_node_lifecycle_birth ON node_lifecycle(birth_ts);
CREATE INDEX idx_node_lifecycle_death ON node_lifecycle(death_ts);

-- Edge lifecycle (per relationship type)
CREATE TABLE edge_lifecycle (
    id              INTEGER PRIMARY KEY,
    relation_type   TEXT NOT NULL,
    source_path     TEXT NOT NULL,
    target_path     TEXT NOT NULL,
    birth_ts        INTEGER NOT NULL,
    death_ts        INTEGER,        -- NULL if still exists
    birth_commit    TEXT NOT NULL,
    death_commit    TEXT,

    UNIQUE(relation_type, source_path, target_path, birth_ts)
);

CREATE INDEX idx_edge_lifecycle_rel ON edge_lifecycle(relation_type);
CREATE INDEX idx_edge_lifecycle_source ON edge_lifecycle(source_path);

-- Time windows
CREATE TABLE time_windows (
    id              INTEGER PRIMARY KEY,
    window_start    INTEGER NOT NULL,
    window_end      INTEGER NOT NULL,
    commit_count    INTEGER NOT NULL,
    file_count      INTEGER NOT NULL,
    author_count    INTEGER NOT NULL,

    UNIQUE(window_start)
);

-- Cochange counts per window
CREATE TABLE window_cochange (
    window_id       INTEGER NOT NULL REFERENCES time_windows(id),
    file_a          TEXT NOT NULL,
    file_b          TEXT NOT NULL,
    cochange_count  INTEGER NOT NULL,

    PRIMARY KEY(window_id, file_a, file_b)
);

-- Author counts per window
CREATE TABLE window_authors (
    window_id       INTEGER NOT NULL REFERENCES time_windows(id),
    file_path       TEXT NOT NULL,
    author          TEXT NOT NULL,
    commit_count    INTEGER NOT NULL,

    PRIMARY KEY(window_id, file_path, author)
);
```

#### Key Operations

**Reconstruct graph at time t:**
```sql
-- Get nodes alive at time t
SELECT canonical_path
FROM node_lifecycle
WHERE birth_ts <= :t AND (death_ts IS NULL OR death_ts > :t);

-- Get edges alive at time t
SELECT source_path, target_path, relation_type
FROM edge_lifecycle
WHERE relation_type = :rel_type
  AND birth_ts <= :t
  AND (death_ts IS NULL OR death_ts > :t);
```

**Compute cochange for window:**
```sql
SELECT file_a, file_b, SUM(cochange_count) as total
FROM window_cochange wc
JOIN time_windows tw ON wc.window_id = tw.id
WHERE tw.window_start >= :start AND tw.window_end <= :end
GROUP BY file_a, file_b;
```

#### Runtime Characteristics

| Metric          | Value                                      | Notes                      |
| --------------- | ------------------------------------------ | -------------------------- |
| Time complexity | O(events + commits × files_per_commit)     | Event building dominates   |
| Space complexity| O(events + nodes + edges × history_depth)  | Can be large for long history |
| Parallelism     | Limited                                    | Event ordering must be preserved |
| Typical runtime | 30s - 2 min                                | Depends on history depth   |

---

### 4.2 Stage 2: Graph Construction

#### Purpose

Build the multi-layer relationship graphs T[:,:,t,r] from indexed data.

#### 4.2a Stage 2a: Import Graph (G_import)

**Mathematical Definition:**
```
G_import(t) = (V(t), E_import(t))

E_import(t) = {(a, b) : a imports b at time t}
            = {(a, b) : edge_lifecycle[IMPORT, a, b].birth_ts ≤ t < death_ts}
```

**Processing:**
```
2a.1 For current time (now):
     ├── Read file_facts.imports for each file
     ├── Resolve import targets to file paths
     ├── Create edges: source → target
     └── Store in graph_edges[IMPORT]

2a.2 For historical time points (sampled):
     ├── Use edge_lifecycle to reconstruct G_import(t)
     ├── Store snapshot in graph_history
     └── Sample at: t - 1mo, t - 3mo, t - 6mo, t - 12mo
```

**Runtime:** O(files × avg_imports), ~5-10s

#### 4.2b Stage 2b: Temporal Graphs (G_cochange, G_author)

**Mathematical Definition:**
```
G_cochange = (V, E_cochange, W_cochange)

W_cochange(a, b) = lift(a, b) = P(a,b) / (P(a) × P(b))
                 = (commits containing both a,b) × (total commits) /
                   (commits containing a) × (commits containing b)

Edge condition: lift(a,b) > 1.0 (more than random co-occurrence)

G_author = (V, E_author, W_author)

W_author(a, b) = Jaccard(authors(a), authors(b))
               = |authors(a) ∩ authors(b)| / |authors(a) ∪ authors(b)|

Edge condition: Jaccard(a,b) > 0.1 (non-trivial overlap)
```

**Processing:**
```
2b.1 Build G_cochange:
     ├── Read window_cochange for recent windows
     ├── Compute lift: lift(a,b) = P(a,b) / (P(a) × P(b))
     ├── Filter edges with lift > 1.0
     └── Store in graph_edges[COCHANGE]

2b.2 Build G_author:
     ├── Read window_authors for recent windows
     ├── Compute Jaccard: |A∩B| / |A∪B|
     ├── Filter edges with Jaccard > 0.1
     └── Store in graph_edges[AUTHOR]
```

**Runtime:** O(windows × pairs), ~10-30s

#### 4.2c Stage 2c: Semantic Graph (G_semantic, G_clone)

**Mathematical Definition:**
```
G_semantic = (V, E_semantic, W_semantic)

For each file, extract concept vector: c(v) ∈ ℝ^d (TF-IDF weighted)
W_semantic(a, b) = cosine(c(a), c(b)) = c(a) · c(b) / (||c(a)|| × ||c(b)||)

Edge condition: cosine(a,b) > 0.3

G_clone = (V, E_clone, W_clone)

W_clone(a, b) = 1 - NCD(a, b)
NCD(a,b) = (C(a+b) - min(C(a), C(b))) / max(C(a), C(b))
where C(x) = compressed size of x

Edge condition: NCD(a,b) < 0.3
```

**Processing:**
```
2c.1 Extract concepts per file:
     ├── Tokenize identifiers
     ├── Apply TF-IDF weighting
     ├── Extract top-k concepts per file
     └── Store in file_concepts

2c.2 Build G_semantic:
     ├── Compute cosine similarity between concept vectors
     ├── Filter edges with similarity > 0.3
     └── Store in graph_edges[SEMANTIC]

2c.3 Build G_clone:
     ├── Compute NCD for file pairs (with LSH for large codebases)
     ├── Filter edges with NCD < 0.3
     └── Store in graph_edges[CLONE]
```

**Runtime:** O(files² × concepts) or O(files × log files) with LSH, ~20-60s

#### 4.2d Stage 2d: Graph Fusion (G_combined)

**Mathematical Definition:**
```
G_combined = (V, E_combined, W_combined)

W_combined(a, b) = Σᵣ αᵣ × Wᵣ(a, b)
                = α_import × W_import(a,b)
                + α_cochange × W_cochange(a,b)
                + α_author × W_author(a,b)
                + α_semantic × W_semantic(a,b)

Default weights: α = [0.4, 0.3, 0.2, 0.1] (IMPORT, COCHANGE, AUTHOR, SEMANTIC)
Constraint: Σᵣ αᵣ = 1

Edge condition: W_combined(a,b) > θ (default θ = 0.1)
```

**Processing:**
```
2d.1 Build G_combined (weighted union):
     ├── Normalize edge weights per graph to [0,1]
     ├── Combine: w_combined = α×w_import + β×w_cochange + γ×w_author + δ×w_semantic
     ├── Default weights: α=0.4, β=0.3, γ=0.2, δ=0.1
     └── Store in graph_edges[COMBINED]

2d.2 Sample historical combined graphs:
     ├── For each historical time point t:
     │   ├── Reconstruct G_import(t)
     │   ├── Compute G_cochange(t) from window data up to t
     │   ├── Combine into G_combined(t)
     │   └── Store in graph_history
     └── Store graph_history records
```

**Runtime:** O(edges), ~5-10s

#### Database Schema

```sql
-- Graph edges (all relationship types)
CREATE TABLE graph_edges (
    id              INTEGER PRIMARY KEY,
    snapshot_id     TEXT NOT NULL,
    relation_type   TEXT NOT NULL,  -- IMPORT, COCHANGE, AUTHOR, SEMANTIC, CLONE, COMBINED
    source_path     TEXT NOT NULL,
    target_path     TEXT NOT NULL,
    weight          REAL NOT NULL DEFAULT 1.0,
    metadata        TEXT,           -- JSON with additional attributes

    UNIQUE(snapshot_id, relation_type, source_path, target_path)
);

CREATE INDEX idx_graph_edges_snapshot ON graph_edges(snapshot_id, relation_type);
CREATE INDEX idx_graph_edges_source ON graph_edges(source_path);
CREATE INDEX idx_graph_edges_target ON graph_edges(target_path);

-- Historical graph snapshots
CREATE TABLE graph_history (
    id              INTEGER PRIMARY KEY,
    snapshot_id     TEXT NOT NULL,
    relation_type   TEXT NOT NULL,
    timestamp       INTEGER NOT NULL,
    node_count      INTEGER NOT NULL,
    edge_count      INTEGER NOT NULL,

    UNIQUE(snapshot_id, relation_type, timestamp)
);

-- File concepts for semantic graph
CREATE TABLE file_concepts (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    concept         TEXT NOT NULL,
    weight          REAL NOT NULL,

    PRIMARY KEY(snapshot_id, file_path, concept)
);
```

---

### 4.3 Stage 3: Signal Computation

#### Purpose

Compute 79 signals across 7 layers from the multi-layer graphs.

#### 4.3a Stage 3a: Graph Algorithms

**Mathematical Definitions:**

**PageRank:**
```
π = α(I - (1-α)P)⁻¹v

Pipeline:
1. Build transition matrix: P = D⁻¹A
2. Power iteration: π^{(k+1)} = (1-α)Pπ^{(k)} + αv
3. Convergence: ||π^{(k+1)} - π^{(k)}||₁ < ε

Complexity: O(k|E|) for k iterations
```

**Louvain Community Detection:**
```
Modularity: Q = (1/2m) Σᵢⱼ [Aᵢⱼ - (kᵢkⱼ/2m)] δ(cᵢ,cⱼ)

Pipeline:
Phase 1 (Local Moving):
  for each node i:
    move i to community C maximizing ΔQ

Phase 2 (Aggregation):
  build supernetwork from communities

Repeat until convergence

Complexity: O(n log n) typical, O(n²) worst case
```

**Spectral Analysis:**
```
1. Build Laplacian: L = D - A or L_sym = D^{-1/2}LD^{-1/2}
2. Eigendecomposition: L = UΛUᵀ
3. Fiedler value: λ₂(L) (algebraic connectivity)
4. Spectral gap: λ₃ - λ₂

Complexity: O(n³) for exact, O(n²) for Lanczos
```

**SCC Detection:**
```
Pipeline: Kosaraju's algorithm
1. DFS on G → finish times
2. Transpose: Gᵀ
3. DFS on Gᵀ in finish-time order

Complexity: O(|V| + |E|)
```

**Processing per relationship type r:**
```
3a.1 Centrality metrics:
     ├── PageRank(G_r) → pagerank[r] per node
     ├── Betweenness(G_r) → betweenness[r] per node
     └── Store in node_signals

3a.2 Community detection:
     ├── Louvain(G_r) → community[r] per node, modularity[r] global
     └── Store in node_signals, global_signals

3a.3 Structural metrics:
     ├── In/out degree per node
     ├── SCC detection → cycle_member, cycle_size per node
     ├── BFS from entry points → depth per node
     ├── Transitive closure → blast_radius per node
     └── Store in node_signals

3a.4 Spectral metrics:
     ├── Laplacian eigenvalues → fiedler[r], spectral_gap[r] global
     └── Store in global_signals

3a.5 Distribution metrics:
     ├── Gini(pagerank) → centrality_gini[r] global
     └── Store in global_signals
```

**Runtime:** O(V + E) per algorithm, ~10-30s

#### 4.3b Stage 3b: Trajectory Signals

**Mathematical Definitions:**
```
Velocity:      Ds(v, t) = (s(v,t) - s(v,t-Δ)) / Δ
Acceleration:  D²s(v, t) = (Ds(v,t) - Ds(v,t-Δ)) / Δ
Trend:         β_w(s, v) = linear regression slope over window w

Community stability:
  community_changes(v) = Σ_t 1(community[t] ≠ community[t-1])
  community_stability(v) = 1 - community_changes / observations

Graph velocity (global):
  graph_velocity = mean(|E(t) △ E(t-1)| / |E(t) ∪ E(t-1)|)

Topology stability:
  topology_stability = 1 / (1 + graph_velocity)
```

**Processing:**
```
3b.1 Load historical snapshots:
     ├── For each historical time t in graph_history:
     │   └── Load node_signals computed at t (or compute now)
     └── Build time series per node per signal

3b.2 Compute derivatives:
     ├── For each node, for each signal s:
     │   ├── velocity = (s(now) - s(t-1)) / Δt
     │   ├── acceleration = (velocity(now) - velocity(t-1)) / Δt
     │   └── trend = linear_regression_slope(s over all t)
     └── Store in trajectory_signals

3b.3 Compute stability metrics:
     ├── community_changes = count(community[t] ≠ community[t-1])
     ├── community_stability = 1 - community_changes / observations
     └── Store in trajectory_signals

3b.4 Compute global trajectory:
     ├── graph_velocity = mean(edge_jaccard(G(t), G(t-1)))
     ├── fiedler_trend = slope(fiedler over time)
     ├── modularity_trend = slope(modularity over time)
     └── Store in global_trajectory_signals
```

**Runtime:** O(history_depth × V), ~5-15s

#### 4.3c Stage 3c: Cross-Layer Signals

**Mathematical Definitions:**
```
Mutual Information:
  I(G₁; G₂) = H(G₁) + H(G₂) - H(G₁, G₂)
            = Σₐ Σᵦ (nₐᵦ/n) log₂[(nₐᵦ × n) / (nₐ• × n•ᵦ)]

Behavioral coherence:  I(G_import; G_cochange)
Conway alignment:      I(G_import; G_author)
Semantic alignment:    I(G_import; G_semantic)

Per-node cross-layer:
  hidden_coupling_count(v) = |N_cochange(v) \ N_import(v)|
  dead_import_count(v) = |N_import(v) \ N_cochange(v)|
  neighborhood_coherence(v) = |N_imp ∩ N_coc| / |N_imp ∪ N_coc|

Per-pair cross-layer:
  hidden_coupling(a,b) = cochange(a,b) × (1 - import(a,b))
  conway_violation(a,b) = import(a,b) × (1 - author_overlap(a,b))
```

**Processing:**
```
3c.1 Compute mutual information:
     ├── behavioral_coherence = I(G_import; G_cochange)
     ├── conway_alignment = I(G_import; G_author)
     ├── semantic_alignment = I(G_import; G_semantic)
     └── Store in global_signals

3c.2 Compute per-node cross-layer:
     ├── For each node v:
     │   ├── N_import = neighbors in G_import
     │   ├── N_cochange = neighbors in G_cochange
     │   ├── hidden_coupling_count = |N_cochange \ N_import|
     │   ├── neighborhood_coherence = |N_import ∩ N_cochange| / |N_import ∪ N_cochange|
     │   └── Store in node_cross_signals
     └──

3c.3 Compute per-pair cross-layer:
     ├── For pairs with any relationship:
     │   ├── hidden_coupling = cochange(a,b) × (1 - import(a,b))
     │   ├── conway_violation = import(a,b) × (1 - author(a,b))
     │   └── Store in pair_signals (sparse, only non-zero)
     └──
```

**Runtime:** O(V × avg_degree) + O(E) for MI, ~10-20s

#### 4.3d Stage 3d: Composite Signals

**Mathematical Definitions:**

**Percentile Normalization:**
```
pctl(x) = |{v : s(v) ≤ x}| / |{v}|
```

**Risk Score (per file):**
```
risk_score(v) =
    w₁ × pctl(pagerank[IMPORT](v))           # structural importance
  + w₂ × pctl(|pagerank_velocity(v)|)        # changing importance
  + w₃ × pctl(blast_radius[IMPORT](v))       # impact of change
  + w₄ × min(churn_cv(v) / 2, 1)             # change volatility
  + w₅ × max(0, 1 - bus_factor(v) / 5)       # knowledge concentration
  + w₆ × pctl(hidden_coupling_count(v))      # undeclared dependencies
  + w₇ × (1 - community_stability(v))        # structural instability

Default weights: w = [0.15, 0.10, 0.15, 0.15, 0.15, 0.15, 0.15]
```

**Wiring Quality (per file):**
```
wiring_quality(v) = 1 - (
    w₁ × is_orphan[IMPORT](v)
  + w₂ × stub_ratio(v)
  + w₃ × phantom_import_ratio(v)
  + w₄ × (hidden_coupling_count(v) / max(degree(v), 1))
)

Default weights: w = [0.25, 0.25, 0.25, 0.25]
```

**Health Score (per file):**
```
health_score(v) = 1 - (
    w₁ × risk_score(v)
  + w₂ × (1 - wiring_quality(v))
  + w₃ × pctl(cognitive_load(v))
  + w₄ × is_orphan[IMPORT](v)
  + w₅ × (1 - neighborhood_coherence(v))
)

Default weights: w = [0.25, 0.20, 0.20, 0.15, 0.20]
```

**Health Laplacian (delta_h):**
```
delta_h(v) = health_score(v) - mean(health_score(n) for n in neighbors(v))

Conservation property: Σ_v delta_h(v) ≈ 0
```

**Codebase Health (The One Number):**
```
codebase_health =
    w₁ × architecture_health
  + w₂ × wiring_score
  + w₃ × (global_bus_factor / team_size)
  + w₄ × modularity[IMPORT]
  + w₅ × behavioral_coherence
  + w₆ × topology_stability

Default weights: w = [0.20, 0.20, 0.15, 0.15, 0.15, 0.15]
```

**Processing:**
```
3d.1 Percentile normalization:
     ├── For each normalizable signal:
     │   ├── Collect all values across files
     │   ├── Compute pctl(v) = rank(v) / count
     │   └── Store percentiles in node_signals
     └── Skip for ABSOLUTE tier (<15 files)

3d.2 File composites:
     ├── raw_risk = weighted_sum(pagerank, blast_radius, cognitive_load, churn_cv, bus_factor)
     ├── risk_score = weighted_sum(percentiles) + trajectory_terms + cross_layer_terms
     ├── wiring_quality = 1 - penalties(orphan, stub, phantom, hidden_coupling)
     ├── file_health_score = composite(risk, wiring, cognitive, coherence)
     └── Store in composite_signals

3d.3 Health Laplacian:
     ├── For each node v:
     │   ├── neighbors = import_neighbors ∪ imported_by
     │   ├── mean_neighbor_risk = mean(raw_risk(n) for n in neighbors)
     │   ├── delta_h = raw_risk(v) - mean_neighbor_risk
     │   └── Store delta_h in composite_signals
     └──

3d.4 Module composites:
     ├── Aggregate file signals per module
     ├── Compute Martin metrics (cohesion, coupling, instability, abstractness)
     ├── Compute health_score per module
     └── Store in module_signals

3d.5 Codebase composites:
     ├── wiring_score = 1 - penalties(orphan_ratio, phantom_ratio, glue_deficit, ...)
     ├── architecture_health = composite(violation_rate, cohesion, coupling, ...)
     ├── team_risk = composite(bus_factor, knowledge_gini, coordination_cost, conway)
     ├── codebase_health = composite(architecture, wiring, bus_factor, modularity, coherence, stability)
     └── Store in global_signals
```

**Runtime:** O(V), ~5-10s

#### Database Schema

```sql
-- Node signals (per file, per relationship type where applicable)
CREATE TABLE node_signals (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    relation_type   TEXT,           -- NULL for non-graph signals
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,
    percentile      REAL,           -- NULL for non-normalizable

    PRIMARY KEY(snapshot_id, file_path, relation_type, signal_name)
);

CREATE INDEX idx_node_signals_snapshot ON node_signals(snapshot_id);
CREATE INDEX idx_node_signals_signal ON node_signals(signal_name);

-- Trajectory signals (per file)
CREATE TABLE trajectory_signals (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    signal_name     TEXT NOT NULL,  -- e.g., 'pagerank_velocity', 'community_stability'
    value           REAL NOT NULL,

    PRIMARY KEY(snapshot_id, file_path, signal_name)
);

-- Cross-layer signals (per file)
CREATE TABLE cross_layer_signals (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,

    PRIMARY KEY(snapshot_id, file_path, signal_name)
);

-- Pair signals (sparse, only significant pairs)
CREATE TABLE pair_signals (
    snapshot_id     TEXT NOT NULL,
    file_a          TEXT NOT NULL,
    file_b          TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,

    PRIMARY KEY(snapshot_id, file_a, file_b, signal_name)
);

-- Module signals
CREATE TABLE module_signals (
    snapshot_id     TEXT NOT NULL,
    module_path     TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,

    PRIMARY KEY(snapshot_id, module_path, signal_name)
);

-- Global signals
CREATE TABLE global_signals (
    snapshot_id     TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,

    PRIMARY KEY(snapshot_id, signal_name)
);

-- Composite signals (file-level, separated for clarity)
CREATE TABLE composite_signals (
    snapshot_id     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    raw_risk        REAL NOT NULL,
    risk_score      REAL NOT NULL,
    wiring_quality  REAL NOT NULL,
    health_score    REAL NOT NULL,
    delta_h         REAL NOT NULL,

    PRIMARY KEY(snapshot_id, file_path)
);
```

---

### 4.4 Stage 4: Pattern Detection

#### Purpose

Evaluate all 22 finders against computed signals to detect patterns.

#### Mathematical Framework

Each finder f defines a condition on signals:
```
f: Entity × Signals → {0, 1}

Finding = {
  pattern: PatternName,
  target: Entity,
  severity: [0, 1],
  confidence: [0, 1],
  evidence: {signal_name: value}
}
```

#### Processing

```
4.1 Load signal data:
     ├── Load node_signals, trajectory_signals, cross_layer_signals
     ├── Load module_signals, global_signals
     ├── Load pair_signals (for pair-scope patterns)
     └── Load graph_edges (for relation-based patterns)

4.2 For each finder (parallelizable per finder):
     ├── Determine scope: FILE, PAIR, MODULE, CODEBASE
     ├── Determine required signals
     ├── Evaluate condition for each entity in scope
     ├── For matches:
     │   ├── Compute severity (from formula)
     │   ├── Compute confidence
     │   ├── Collect evidence (signal values that triggered)
     │   └── Create Finding record
     └── Apply hotspot filter for FILE scope (unless structural-only)

4.3 Rank findings:
     ├── Sort by severity × confidence
     ├── Apply max_findings limit
     └── Store ranked findings

4.4 Link evidence:
     ├── For each finding:
     │   ├── Store signal values as evidence
     │   └── Store related entities (for PAIR scope)
     └── Store in finding_evidence
```

#### Finder Execution Order

```
Wave 1: Structural (no cross-dependencies)
├── GOD_FILE
├── ORPHAN_CODE
├── PHANTOM_DEPENDENCY
├── CIRCULAR_DEPENDENCY
├── COPY_PASTE_CLONE
└── FLAT_ARCHITECTURE

Wave 2: Architecture (needs module signals)
├── ZONE_OF_PAIN
├── ZONE_OF_USELESSNESS
├── LAYER_VIOLATION
├── BOUNDARY_MISMATCH
├── UNSTABLE_INTERFACE
└── RIGID_CORE

Wave 3: Cross-dimensional (needs all signals)
├── HIGH_RISK_HUB
├── HIDDEN_COUPLING
├── CONWAY_VIOLATION
├── WEAK_LINK
├── ACCIDENTAL_COUPLING
└── KNOWLEDGE_SILO

Wave 4: Temporal/Quality
├── UNSTABLE_FILE
├── BUS_FACTOR_RISK
├── HOLLOW_CODE
└── CHRONIC_PROBLEM
```

#### Database Schema

```sql
-- Findings
CREATE TABLE findings (
    id              TEXT PRIMARY KEY,
    snapshot_id     TEXT NOT NULL,
    pattern         TEXT NOT NULL,  -- e.g., 'HIDDEN_COUPLING'
    scope           TEXT NOT NULL,  -- FILE, PAIR, MODULE, CODEBASE
    target          TEXT NOT NULL,  -- file path, or "file_a|file_b" for pairs
    severity        REAL NOT NULL,
    confidence      REAL NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT,
    remediation     TEXT,
    rank            INTEGER,

    UNIQUE(snapshot_id, pattern, target)
);

CREATE INDEX idx_findings_snapshot ON findings(snapshot_id);
CREATE INDEX idx_findings_pattern ON findings(pattern);
CREATE INDEX idx_findings_severity ON findings(severity DESC);

-- Finding evidence
CREATE TABLE finding_evidence (
    finding_id      TEXT NOT NULL REFERENCES findings(id),
    signal_name     TEXT NOT NULL,
    signal_value    REAL NOT NULL,
    percentile      REAL,
    description     TEXT,

    PRIMARY KEY(finding_id, signal_name)
);

-- Finding lifecycle (for CHRONIC_PROBLEM detection)
CREATE TABLE finding_lifecycle (
    pattern         TEXT NOT NULL,
    target          TEXT NOT NULL,
    first_seen      TEXT NOT NULL,  -- snapshot_id
    last_seen       TEXT NOT NULL,  -- snapshot_id
    persistence_count INTEGER NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'active',

    PRIMARY KEY(pattern, target)
);
```

**Runtime:** O(finders × entities), typically 22 × files, ~5-15s

---

### 4.5 Stage 5: Snapshot Seal

#### Purpose

Seal all artifacts under a single snapshot ID for atomic retrieval and historical comparison.

#### Processing

```
5.1 Generate snapshot_id:
     └── snapshot_id = f"{commit_sha}_{timestamp}_{random_suffix}"

5.2 Link all artifacts:
     ├── All tables reference snapshot_id
     └── Create snapshot metadata record

5.3 Compute diff from prior snapshot:
     ├── Load prior snapshot signals
     ├── Compute signal deltas per file
     ├── Identify new/resolved findings
     └── Store in snapshot_diff

5.4 Archive (optional):
     ├── Export snapshot to Parquet files
     └── Compress and store
```

#### Database Schema

```sql
-- Snapshot metadata
CREATE TABLE snapshots (
    id              TEXT PRIMARY KEY,
    commit_sha      TEXT NOT NULL,
    timestamp       INTEGER NOT NULL,
    root_path       TEXT NOT NULL,
    file_count      INTEGER NOT NULL,
    finding_count   INTEGER NOT NULL,
    codebase_health REAL,
    status          TEXT NOT NULL DEFAULT 'complete',
    created_at      INTEGER NOT NULL,
    config_hash     TEXT,
    tool_version    TEXT
);

CREATE INDEX idx_snapshots_commit ON snapshots(commit_sha);
CREATE INDEX idx_snapshots_ts ON snapshots(timestamp);

-- Snapshot artifact manifest
CREATE TABLE snapshot_artifacts (
    snapshot_id     TEXT NOT NULL REFERENCES snapshots(id),
    artifact_type   TEXT NOT NULL,  -- 'file_facts', 'graph_edges', 'findings', etc.
    record_count    INTEGER NOT NULL,
    checksum        TEXT,

    PRIMARY KEY(snapshot_id, artifact_type)
);

-- Snapshot diff (changes from prior)
CREATE TABLE snapshot_diff (
    snapshot_id     TEXT NOT NULL REFERENCES snapshots(id),
    prior_snapshot  TEXT REFERENCES snapshots(id),
    files_added     INTEGER NOT NULL,
    files_removed   INTEGER NOT NULL,
    files_changed   INTEGER NOT NULL,
    findings_new    INTEGER NOT NULL,
    findings_resolved INTEGER NOT NULL,
    health_delta    REAL,

    PRIMARY KEY(snapshot_id)
);
```

**Runtime:** ~5-10s

---

## 5. Database Schema Summary

### 5.1 Database Files

| Database    | Tables                                                    | Purpose          | Typical Size |
| ----------- | --------------------------------------------------------- | ---------------- | ------------ |
| facts.db    | file_facts, git_commits, git_file_changes, import_changes | Stage 0 outputs  | 10-50 MB     |
| temporal.db | events, node_lifecycle, edge_lifecycle, time_windows, ... | Stage 1 outputs  | 20-100 MB    |
| graph.db    | graph_edges, graph_history, file_concepts                 | Stage 2 outputs  | 10-50 MB     |
| signals.db  | node_signals, trajectory_signals, cross_layer_signals, ...| Stage 3 outputs  | 20-100 MB    |
| findings.db | findings, finding_evidence, finding_lifecycle             | Stage 4 outputs  | 1-10 MB      |
| snapshots.db| snapshots, snapshot_artifacts, snapshot_diff              | Stage 5 outputs  | 1-5 MB       |

### 5.2 Total Storage Estimate

| Codebase Size | Files   | History         | Total DB Size   |
| ------------- | ------- | --------------- | --------------- |
| Small         | <100    | <1000 commits   | <50 MB          |
| Medium        | 100-1000| 1000-5000 commits| 50-200 MB      |
| Large         | 1000-10000 | 5000+ commits | 200 MB - 1 GB   |
| Monorepo      | 10000+  | 10000+ commits  | 1-10 GB         |

---

## 6. Runtime Analysis

### 6.1 Overall Pipeline Timing

| Stage                  | Small (<100) | Medium (100-1000) | Large (1000-10000) |
| ---------------------- | ------------ | ----------------- | ------------------ |
| 0: Extraction          | 5-10s        | 30-60s            | 2-5 min            |
| 1: Temporal Index      | 2-5s         | 10-30s            | 1-2 min            |
| 2: Graph Construction  | 5-10s        | 30-60s            | 2-5 min            |
| 3: Signal Computation  | 5-10s        | 30-60s            | 2-5 min            |
| 4: Pattern Detection   | 1-2s         | 5-10s             | 30-60s             |
| 5: Snapshot Seal       | 1-2s         | 2-5s              | 5-10s              |
| **Total (cold)**       | 20-40s       | 2-4 min           | 8-20 min           |
| **Total (incremental)**| 5-10s        | 20-60s            | 2-5 min            |

### 6.2 Complexity Analysis

| Operation        | Time Complexity                         | Space Complexity           |
| ---------------- | --------------------------------------- | -------------------------- |
| File parsing     | O(files × avg_lines)                    | O(files × syntax_size)     |
| Git extraction   | O(commits + changes)                    | O(commits + changes)       |
| Event building   | O(changes)                              | O(events)                  |
| Graph construction| O(files × avg_imports + pairs)         | O(edges)                   |
| PageRank         | O(iterations × edges)                   | O(nodes)                   |
| Louvain          | O(passes × edges)                       | O(nodes + edges)           |
| Spectral         | O(nodes³) or O(nodes × eigenvalues)     | O(nodes²) or O(nodes)      |
| Trajectory       | O(history_depth × nodes × signals)      | O(history × nodes)         |
| Cross-layer MI   | O(edges₁ + edges₂)                      | O(1)                       |
| Composites       | O(nodes)                                | O(nodes)                   |
| Pattern detection| O(patterns × entities)                  | O(findings)                |

### 6.3 Memory Footprint

| Stage                  | Peak Memory            | Notes                              |
| ---------------------- | ---------------------- | ---------------------------------- |
| 0: Extraction          | O(largest_file)        | Files parsed one at a time         |
| 1: Temporal Index      | O(events)              | Event log in memory during build   |
| 2: Graph Construction  | O(nodes + edges)       | Graphs in memory                   |
| 3a: Graph Algorithms   | O(nodes²) worst case   | Spectral is memory-heavy           |
| 3b-d: Other Signals    | O(nodes × signals)     | Signal vectors                     |
| 4: Pattern Detection   | O(nodes × signals)     | Loaded signals                     |
| **Peak Overall**       | O(nodes² + edges)      | During spectral computation        |

### 6.4 Bottleneck Analysis

| Bottleneck                    | Impact                  | Mitigation                                  |
| ----------------------------- | ----------------------- | ------------------------------------------- |
| Spectral computation          | O(n³) for dense Laplacian| Use sparse solver, approximate for n>5000  |
| Clone detection (NCD)         | O(n²) pairwise          | LSH for n>1000, skip for n>5000            |
| Historical graph reconstruction| O(history × work)      | Sample history, don't compute all points   |
| Git extraction                | I/O bound               | Incremental extraction                      |
| Large file parsing            | Memory for AST          | Stream parsing, skip >10MB files           |

---

## 7. Consistency Model

### 7.1 Invariants

| Invariant            | Description                                        | Enforcement                          |
| -------------------- | -------------------------------------------------- | ------------------------------------ |
| Snapshot atomicity   | All artifacts for a snapshot are complete or none  | Transaction per stage, rollback on failure |
| Signal derivability  | Any signal value can be recomputed from inputs     | Store all intermediate data          |
| Temporal monotonicity| Events ordered by timestamp                        | Sort events, reject out-of-order     |
| Graph consistency    | Edge endpoints exist as nodes                      | Validate on insert                   |
| Referential integrity| Foreign keys valid                                 | DB constraints                       |

### 7.2 Consistency Checks

**After Stage 0:**
- ✓ All file_facts have valid content_hash
- ✓ All git_file_changes reference valid commits
- ✓ No duplicate (session_id, path) in file_facts

**After Stage 1:**
- ✓ Every node in edge_lifecycle exists in node_lifecycle
- ✓ Events are sorted by timestamp
- ✓ No gaps in time_windows coverage

**After Stage 2:**
- ✓ All graph edge endpoints exist as nodes
- ✓ Edge weights are positive
- ✓ Historical snapshots have consistent node counts

**After Stage 3:**
- ✓ All percentiles in [0, 1]
- ✓ All composite scores in [0, 1]
- ✓ delta_h sums to ~0 across codebase (conservation)

**After Stage 4:**
- ✓ All findings reference valid targets
- ✓ All evidence signals exist in signal tables
- ✓ Severity and confidence in [0, 1]

**After Stage 5:**
- ✓ All artifact tables reference the snapshot_id
- ✓ Record counts match snapshot_artifacts
- ✓ Checksums validate

### 7.3 Idempotency

Each stage is idempotent: running it twice with same inputs produces same outputs.

| Stage | Enforcement                                            |
| ----- | ------------------------------------------------------ |
| 0     | UPSERT on (session_id, path) with content_hash check   |
| 1     | DELETE + INSERT for session (rebuild index)            |
| 2-3   | DELETE + INSERT for snapshot_id                        |
| 4     | DELETE + INSERT for snapshot_id                        |
| 5     | Snapshot ID includes randomness, always unique         |

---

## 8. Failure Modes & Recovery

### 8.1 Failure Scenarios

| Scenario            | Detection         | Impact                    | Recovery                              |
| ------------------- | ----------------- | ------------------------- | ------------------------------------- |
| Parse error         | Exception         | Single file missing       | Log, skip file, continue              |
| Git unavailable     | Command fails     | No temporal data          | Run structural-only mode              |
| OOM during spectral | MemoryError       | Stage 3a fails            | Reduce to approximate method          |
| DB write fails      | SQLException      | Stage incomplete          | Rollback, retry                       |
| Timeout             | Watchdog          | Stage incomplete          | Kill, rollback, retry with limits     |
| Corrupt input       | Validation fails  | Stage fails               | Report error, abort                   |

### 8.2 Recovery Procedures

**Partial stage failure:**
1. Identify failed stage from run_log
2. Check last successful checkpoint
3. Rollback incomplete data:
   ```sql
   DELETE FROM {table} WHERE snapshot_id = :failed_snapshot
   ```
4. Retry from failed stage

**Full recovery:**
1. Identify last complete snapshot
2. Delete all data for incomplete snapshots
3. Re-run pipeline from Stage 0 (or from Stage 1 if facts intact)

### 8.3 Checkpointing

Checkpoint after each stage:
1. Validate stage outputs
2. Write checkpoint record:
   ```sql
   INSERT INTO run_checkpoints (run_id, stage, status, timestamp)
   ```
3. Commit transaction

On startup:
1. Find last run
2. Find last successful checkpoint
3. Resume from next stage

---

## 9. Incremental Computation

### 9.1 Change Detection

| Data    | Change Detection           | Granularity   |
| ------- | -------------------------- | ------------- |
| Files   | content_hash comparison    | Per-file      |
| Git     | HEAD commit comparison     | Per-commit    |
| Imports | diff of import statements  | Per-file      |
| Graphs  | edge set difference        | Per-graph     |
| Signals | value comparison           | Per-signal    |

### 9.2 Incremental Update Strategy

**Stage 0 (Extraction):**
```
For files:
  changed_files = {f : content_hash(f) ≠ stored_hash(f)}
  new_files = {f : f not in stored}
  deleted_files = {f : f in stored but not on disk}

  Parse only: changed_files ∪ new_files
  Mark deleted: deleted_files

For git:
  last_commit = get_last_processed_commit()
  new_commits = git log {last_commit}..HEAD

  Extract only: new_commits
```

**Stage 1 (Temporal Index):**
- Append new events to event log
- Update node_lifecycle for affected nodes
- Update edge_lifecycle for affected edges
- Rebuild affected time_windows only

**Stage 2 (Graphs):**
- G_import: Rebuild only for changed_files (local update)
- G_cochange, G_author: Update incrementally from new window data
- G_combined: Rebuild (fast, O(edges))

**Stage 3 (Signals):**
- Graph signals: Recompute PageRank, Louvain (global algorithms)
- But: can warm-start from previous values
- Trajectory: Append new data point, recompute derivatives
- Composites: Recompute only for files with changed inputs

**Stage 4 (Patterns):**
- Re-evaluate all patterns (fast)
- Compare to previous findings for lifecycle update

### 9.3 Incremental Runtime Savings

| Scenario          | Full Run  | Incremental    |
| ----------------- | --------- | -------------- |
| No changes        | 2-5 min   | <5s            |
| 1 file changed    | 2-5 min   | 10-30s         |
| 10 files changed  | 2-5 min   | 30-60s         |
| 100 files changed | 2-5 min   | 1-2 min        |
| Git-only changes  | 2-5 min   | 20-60s         |

---

## 10. Observability

### 10.1 Logging

| Level  | Content                  | Example                                   |
| ------ | ------------------------ | ----------------------------------------- |
| INFO   | Stage transitions, counts| "Stage 2 complete: 1500 edges in G_import"|
| DEBUG  | Per-entity operations    | "Computed pagerank for file.py: 0.0234"   |
| WARNING| Recoverable issues       | "Failed to parse malformed.py, skipping"  |
| ERROR  | Stage failures           | "OOM during spectral computation"         |

### 10.2 Metrics

```python
@dataclass
class PipelineMetrics:
    # Timing
    stage_durations: dict[str, float]      # seconds per stage
    total_duration: float

    # Throughput
    files_processed: int
    files_per_second: float
    commits_processed: int
    edges_computed: int
    signals_computed: int

    # Quality
    parse_failures: int
    validation_failures: int

    # Resources
    peak_memory_mb: float
    db_size_mb: float
```

### 10.3 Run Log

```sql
CREATE TABLE run_log (
    run_id          TEXT PRIMARY KEY,
    started_at      INTEGER NOT NULL,
    completed_at    INTEGER,
    status          TEXT NOT NULL,  -- 'running', 'complete', 'failed'
    commit_sha      TEXT,
    config_hash     TEXT,
    metrics         TEXT            -- JSON PipelineMetrics
);

CREATE TABLE run_checkpoints (
    run_id          TEXT NOT NULL REFERENCES run_log(run_id),
    stage           TEXT NOT NULL,
    status          TEXT NOT NULL,
    started_at      INTEGER NOT NULL,
    completed_at    INTEGER,
    record_count    INTEGER,
    error_message   TEXT,

    PRIMARY KEY(run_id, stage)
);
```

### 10.4 Tracing (Optional)

For debugging signal provenance:
```sql
CREATE TABLE signal_provenance (
    snapshot_id     TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    signal_name     TEXT NOT NULL,
    value           REAL NOT NULL,
    producer        TEXT NOT NULL,      -- stage/function that produced
    inputs          TEXT,               -- JSON list of input signals
    computed_at     INTEGER NOT NULL,

    PRIMARY KEY(snapshot_id, entity_id, signal_name)
);
```

---

## 11. Constraints & Limitations

### 11.1 Hard Limits

| Constraint        | Limit     | Rationale                |
| ----------------- | --------- | ------------------------ |
| Max files         | 100,000   | Memory for graphs        |
| Max commits       | 50,000    | Git extraction time      |
| Max file size     | 10 MB     | Parse memory             |
| Max edge count    | 10M       | Memory for algorithms    |
| Max history depth | 20 snapshots | Storage               |

### 11.2 Graceful Degradation

| Condition        | Degradation                | Impact                                  |
| ---------------- | -------------------------- | --------------------------------------- |
| No git           | Skip temporal stages       | No churn, cochange, trajectory signals  |
| >5000 files      | Skip NCD clone detection   | No CLONE graph                          |
| >10000 files     | Approximate spectral       | Lower accuracy fiedler                  |
| No tree-sitter   | Regex fallback             | Less accurate parsing                   |
| <15 files        | ABSOLUTE tier              | No percentiles, threshold-based         |

### 11.3 Unsupported Scenarios

| Scenario        | Reason             | Workaround              |
| --------------- | ------------------ | ----------------------- |
| Binary files    | Can't parse        | Excluded by default     |
| Encrypted repos | Can't read git     | Decrypt first           |
| Shallow clones  | Incomplete history | Full clone required     |
| Submodules      | Separate repos     | Analyze separately      |
| Generated code  | Noise              | Add to exclusions       |

### 11.4 Assumptions

| Assumption                | Impact if Violated               |
| ------------------------- | -------------------------------- |
| Files are UTF-8           | Parse errors                     |
| Git history is linear-ish | Merge commit handling imprecise  |
| Import syntax is standard | Unresolved imports               |
| Single language per file  | Wrong parser selected            |
| Stable file paths         | Rename detection fails           |

---

## Appendix A: Signal Quick Reference

### A.1 Signal Count by Layer

| Layer | Name        | Count | Examples                                    |
| ----- | ----------- | ----- | ------------------------------------------- |
| L0    | Syntax      | 8     | lines, function_count, complexity           |
| L2-T  | Temporal    | 9     | total_changes, churn_cv, bus_factor         |
| L2-S  | Semantic    | 7     | role, concept_count, semantic_coherence     |
| L3    | Graph-Node  | 14    | pagerank, community, blast_radius_size      |
| L3    | Graph-Global| 5     | modularity, fiedler_value, centrality_gini  |
| L4    | Trajectory  | 8     | pagerank_velocity, community_stability      |
| L5    | Cross-Layer | 7     | hidden_coupling_count, behavioral_coherence |
| L6    | Composite   | 21    | risk_score, health_score, codebase_health   |
|       | **Total**   | **79**|                                             |

### A.2 Signal Formulas

**L6 Composite Signals:**

```
risk_score(v) =
    0.15 × pctl(pagerank)
  + 0.10 × pctl(|pagerank_velocity|)
  + 0.15 × pctl(blast_radius)
  + 0.15 × min(churn_cv/2, 1)
  + 0.15 × max(0, 1 - bus_factor/5)
  + 0.15 × pctl(hidden_coupling_count)
  + 0.15 × (1 - community_stability)

wiring_quality(v) = 1 - (
    0.25 × is_orphan
  + 0.25 × stub_ratio
  + 0.25 × phantom_import_ratio
  + 0.25 × (hidden_coupling_count / max(degree, 1))
)

file_health_score(v) = 1 - (
    0.25 × risk_score
  + 0.20 × (1 - wiring_quality)
  + 0.20 × pctl(cognitive_load)
  + 0.15 × is_orphan
  + 0.20 × (1 - neighborhood_coherence)
)

codebase_health =
    0.20 × architecture_health
  + 0.20 × wiring_score
  + 0.15 × (global_bus_factor / team_size)
  + 0.15 × modularity[IMPORT]
  + 0.15 × behavioral_coherence
  + 0.15 × topology_stability
```

---

## Appendix B: Finder Quick Reference

| # | Pattern              | Scope   | Key Signals                       | Layer   |
| - | -------------------- | ------- | --------------------------------- | ------- |
| 1 | GOD_FILE             | FILE    | lines, cognitive_load, in_degree  | L0+L3   |
| 2 | ORPHAN_CODE          | FILE    | is_orphan, role                   | L3+L2   |
| 3 | PHANTOM_DEPENDENCY   | FILE    | phantom_import_count              | L3      |
| 4 | CIRCULAR_DEPENDENCY  | FILE    | cycle_member, cycle_size          | L3      |
| 5 | COPY_PASTE_CLONE     | PAIR    | NCD weight                        | L2      |
| 6 | FLAT_ARCHITECTURE    | CODEBASE| modularity, centrality_gini       | L3      |
| 7 | ZONE_OF_PAIN         | MODULE  | instability, main_seq_distance    | L6      |
| 8 | ZONE_OF_USELESSNESS  | MODULE  | instability, abstractness         | L6      |
| 9 | LAYER_VIOLATION      | PAIR    | layer assignments                 | L6      |
|10 | BOUNDARY_MISMATCH    | MODULE  | boundary_alignment                | L6      |
|11 | UNSTABLE_INTERFACE   | MODULE  | instability, velocity             | L6      |
|12 | RIGID_CORE           | MODULE  | instability, coupling             | L6      |
|13 | HIGH_RISK_HUB        | FILE    | pagerank, churn_cv, bus_factor    | L3+L2+L6|
|14 | HIDDEN_COUPLING      | PAIR    | cochange, import                  | L5      |
|15 | CONWAY_VIOLATION     | PAIR    | import, author_overlap            | L5      |
|16 | WEAK_LINK            | FILE    | delta_h                           | L6      |
|17 | ACCIDENTAL_COUPLING  | PAIR    | concept_overlap, import           | L5      |
|18 | KNOWLEDGE_SILO       | MODULE  | knowledge_gini, module_bus_factor | L6      |
|19 | UNSTABLE_FILE        | FILE    | churn_cv, trajectory              | L2      |
|20 | BUS_FACTOR_RISK      | FILE    | bus_factor, pagerank              | L2+L3   |
|21 | HOLLOW_CODE          | FILE    | stub_ratio                        | L0      |
|22 | CHRONIC_PROBLEM      | FILE    | finding_lifecycle                 | L7      |

---

## Appendix C: Relationship Types

| ID | Type            | Edge (a→b) exists if            | Weight W(a,b) | Directed | Source    |
| -- | --------------- | ------------------------------- | ------------- | -------- | --------- |
| R₁ | IMPORT          | a has import statement for b    | 1.0           | Yes      | Parsing   |
| R₂ | CALLS           | function in a calls function in b| call_count   | Yes      | Deep parsing |
| R₃ | COCHANGES       | a,b in same commit              | lift(a,b)     | No       | Git       |
| R₄ | AUTHOR_OVERLAP  | authors(a) ∩ authors(b) ≠ ∅     | Jaccard       | No       | Git       |
| R₅ | CONCEPT_SIMILAR | concepts(a) · concepts(b) > θ   | cosine_sim    | No       | Semantics |
| R₆ | CLONE           | NCD(a,b) < θ                    | 1 - NCD       | No       | Content   |
| R₇ | COMBINED        | Weighted fusion of all          | Σᵣ αᵣ Wᵣ      | Mixed    | Derived   |

---

## Appendix D: Derived Relationship Types

| Derived Type        | Definition                     | Formula                | Interpretation           |
| ------------------- | ------------------------------ | ---------------------- | ------------------------ |
| HIDDEN_COUPLING     | Cochange without import        | G₃ \ (G₁ ∪ G₁ᵀ)       | Undeclared dependency    |
| CONFIRMED_COUPLING  | Import and cochange            | G₁ ∩ G₃                | Validated dependency     |
| DEAD_IMPORT         | Import without cochange        | G₁ \ G₃                | Possibly unused          |
| CONWAY_VIOLATION    | Import without author overlap  | G₁ \ G₄                | Cross-team dependency    |
| CONWAY_ALIGNED      | Import with author overlap     | G₁ ∩ G₄                | Same-team dependency     |
| SEMANTIC_MISMATCH   | Import without concept similar | G₁ \ G₅                | Conceptual disconnect    |

---

## Appendix E: Normalization Rules

### E.1 Percentile Normalization

```
pctl(x) = |{v : s(v) ≤ x}| / |{v}|
```

### E.2 Effective Percentile (with floor)

```
eff_pctl(signal, value) =
    0.0 if value < FLOOR[signal]
    pctl(value) otherwise

FLOORS = {
    'pagerank': 0.001,
    'blast_radius': 2,
    'cognitive_load': 3,
}
```

### E.3 Signal Polarity

| Polarity  | Meaning               | Normalization for "badness" |
| --------- | --------------------- | --------------------------- |
| HIGH_BAD  | High value = problem  | pctl(x)                     |
| HIGH_GOOD | High value = healthy  | 1 - pctl(x)                 |
| NEUTRAL   | Structural, not quality| Use as-is                  |

---

## Appendix F: Aggregation Rules

### F.1 File → Module Aggregation

| Signal Type  | Aggregation  | Formula                                |
| ------------ | ------------ | -------------------------------------- |
| Counts       | sum          | Σ s(v)                                 |
| Rates/ratios | mean         | (1/n) Σ s(v)                           |
| Worst case   | max          | max s(v)                               |
| Best case    | min          | min s(v)                               |
| Risk signals | weighted_mean| Σ importance(v) × s(v) / Σ importance(v)|
| Distributions| gini         | Gini({s(v)})                           |

### F.2 Importance Weighting

```
importance(v) = pagerank[COMBINED](v)

weighted_mean(s) = Σ importance(v) × s(v) / Σ importance(v)
```

---

## Document Revision History

| Version | Date       | Author  | Changes                    |
| ------- | ---------- | ------- | -------------------------- |
| 1.0     | 2026-02-01 | Team    | Initial draft              |
| 2.0     | 2026-02-19 | Team    | Added mathematical foundation, tensor model, cross-layer analysis |

---

*End of Document*
