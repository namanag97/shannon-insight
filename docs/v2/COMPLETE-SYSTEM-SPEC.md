# Shannon Insight: Complete System Specification

## Document Purpose

This document is a complete specification for building Shannon Insight from scratch. It is designed to be consumed by AI agents or developers who need to implement the full system without prior context.

**Read this document in order. Each section builds on previous sections.**

---

# Part I: Foundation

## 1. What This System Does

Shannon Insight analyzes codebases to detect structural, temporal, and social patterns that indicate technical debt, risk, and architectural issues.

**Inputs:**
- Source code files (Python, TypeScript, JavaScript, Go, Java, Rust, Ruby, C/C++)
- Git repository history

**Outputs:**
- 79+ quantitative signals measuring code health
- 22 pattern detections (findings) with severity and evidence
- A single "codebase health" score (1-10)

**Key Insight:** A codebase is a dynamical system on a multi-layer network. Files are nodes. Relationships (imports, co-changes, authorship) are edges. The system evolves over time. Health is measured by analyzing the network structure, its evolution, and cross-layer coherence.

---

## 2. Core Concepts

### 2.1 The Multi-Layer Graph

At any time t, a codebase is represented as multiple overlapping graphs:

```
M(t) = {
    G_import(t)    : file A imports file B
    G_cochange(t)  : file A and B change together in commits
    G_author(t)    : file A and B share authors
    G_semantic(t)  : file A and B have similar concepts
    G_clone(t)     : file A and B have duplicated content
    G_combined(t)  : weighted union of all above
}
```

Each graph has the same nodes (files) but different edges (relationships).

### 2.2 The Temporal Dimension

The system tracks how graphs evolve:
- **Events**: node additions, deletions, renames; edge additions, deletions
- **Trajectories**: how signals change over time (velocity, acceleration)
- **Windows**: time-bucketed aggregations (e.g., 4-week windows for churn)

### 2.3 The Signal Hierarchy

Signals are computed in layers, each depending only on layers below:

```
Layer 0: Syntax       → Parse files → lines, functions, complexity
Layer 1: Temporal     → Process git → events, lifecycles, windows
Layer 2: Graphs       → Build edges → G_import, G_cochange, G_author, G_semantic, G_clone
Layer 3: Graph Algos  → Run algorithms → PageRank, Louvain, spectral, SCC
Layer 4: Trajectory   → Compute derivatives → velocity, stability, trends
Layer 5: Cross-Layer  → Compare graphs → coherence, hidden coupling, MI
Layer 6: Composites   → Weighted sums → risk_score, health_score
Layer 7: Findings     → Pattern matching → GOD_FILE, HIDDEN_COUPLING, etc.
```

### 2.4 Entity Scopes

Signals and findings have different scopes:

| Scope | Description | Example |
|-------|-------------|---------|
| FILE | Single file | risk_score for `api/users.py` |
| PAIR | Two files | hidden_coupling between `a.py` and `b.py` |
| MODULE | Directory/package | cohesion for `src/api/` |
| CODEBASE | Entire system | codebase_health |

---

## 3. Technology Stack

### 3.1 Required

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.9+ | Implementation |
| Database | SQLite | Persistence |
| CLI | Typer | Command-line interface |
| Parsing | tree-sitter (optional) + regex | Syntax extraction |
| Git | subprocess to `git` | History extraction |

### 3.2 Optional

| Component | Technology | Purpose |
|-----------|------------|---------|
| Deep parsing | tree-sitter bindings | Better syntax extraction |
| Fast queries | DuckDB | Analytics over Parquet |
| Visualization | Rich | Terminal output |

### 3.3 No External Dependencies For

- Graph algorithms (implement from scratch)
- Statistical computations (implement from scratch)
- Signal computations (implement from scratch)

---

# Part II: Data Models

## 4. Core Data Structures

### 4.1 File Syntax (Layer 0 Output)

```python
@dataclass
class FunctionDef:
    name: str
    start_line: int
    end_line: int
    parameters: int
    complexity: int          # cyclomatic complexity
    is_stub: bool            # body is pass/... or single return

@dataclass
class ClassDef:
    name: str
    start_line: int
    end_line: int
    methods: list[str]
    bases: list[str]         # parent classes
    is_abstract: bool        # has abstract methods

@dataclass
class Import:
    module: str              # what is imported
    alias: str | None        # import X as alias
    line: int
    is_relative: bool        # from . import X

@dataclass
class FileSyntax:
    path: str                # relative to repo root
    language: str            # python, typescript, go, etc.
    content_hash: str        # SHA256 of content
    lines: int
    functions: list[FunctionDef]
    classes: list[ClassDef]
    imports: list[Import]

    # Computed properties
    @property
    def function_count(self) -> int:
        return len(self.functions)

    @property
    def class_count(self) -> int:
        return len(self.classes)

    @property
    def import_count(self) -> int:
        return len(self.imports)

    @property
    def complexity(self) -> int:
        return sum(f.complexity for f in self.functions)

    @property
    def max_nesting(self) -> int:
        # Computed during parsing
        ...

    @property
    def stub_ratio(self) -> float:
        if not self.functions:
            return 0.0
        return sum(1 for f in self.functions if f.is_stub) / len(self.functions)

    @property
    def impl_gini(self) -> float:
        # Gini coefficient of function sizes
        sizes = [f.end_line - f.start_line for f in self.functions]
        return gini_coefficient(sizes) if len(sizes) > 1 else 0.0
```

### 4.2 Git Data (Layer 0 Output)

```python
@dataclass
class GitCommit:
    hash: str                # full SHA
    timestamp: int           # unix timestamp
    author_email: str
    subject: str             # first line of message

@dataclass
class GitFileChange:
    commit_hash: str
    file_path: str
    change_type: str         # 'A' (add), 'M' (modify), 'D' (delete), 'R' (rename)
    old_path: str | None     # for renames
    additions: int           # lines added
    deletions: int           # lines deleted
```

### 4.3 Temporal Index (Layer 1 Output)

```python
@dataclass
class GraphEvent:
    timestamp: int
    commit_hash: str
    event_type: str          # NODE_ADD, NODE_REMOVE, EDGE_ADD, EDGE_REMOVE
    relation_type: str | None  # IMPORT, COCHANGE, etc. (None for node events)
    source_path: str
    target_path: str | None  # for edges
    author: str

@dataclass
class NodeLifecycle:
    path: str
    canonical_path: str      # resolved through renames
    birth_ts: int
    death_ts: int | None     # None if still alive

@dataclass
class EdgeLifecycle:
    relation_type: str
    source_path: str
    target_path: str
    birth_ts: int
    death_ts: int | None

@dataclass
class TimeWindow:
    start_ts: int
    end_ts: int
    commit_count: int

@dataclass
class WindowCochange:
    window_id: int
    file_a: str
    file_b: str
    count: int               # times changed together

@dataclass
class WindowAuthors:
    window_id: int
    file_path: str
    author: str
    commit_count: int
```

### 4.4 Relationship Graph (Layer 2 Output)

```python
@dataclass
class RelationshipGraph:
    relation_type: str       # IMPORT, COCHANGE, AUTHOR, SEMANTIC, CLONE, COMBINED
    timestamp: int           # when this snapshot was taken
    nodes: set[str]          # file paths
    adjacency: dict[str, list[str]]   # forward edges
    reverse: dict[str, list[str]]     # backward edges
    weights: dict[tuple[str, str], float]  # edge weights

    @property
    def edge_count(self) -> int:
        return sum(len(targets) for targets in self.adjacency.values())

    def neighbors(self, node: str, direction: str = 'both') -> set[str]:
        result = set()
        if direction in ('out', 'both'):
            result.update(self.adjacency.get(node, []))
        if direction in ('in', 'both'):
            result.update(self.reverse.get(node, []))
        return result
```

### 4.5 Signals (Layer 3-6 Output)

```python
@dataclass
class FileSignals:
    path: str

    # Layer 0: Syntax
    lines: int = 0
    function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    max_nesting: int = 0
    complexity: int = 0
    stub_ratio: float = 0.0
    impl_gini: float = 0.0

    # Layer 2: Temporal
    total_changes: int = 0
    churn_cv: float = 0.0
    churn_slope: float = 0.0
    churn_trajectory: str = "DORMANT"
    bus_factor: float = 1.0
    author_entropy: float = 0.0
    fix_ratio: float = 0.0
    refactor_ratio: float = 0.0
    change_entropy: float = 0.0

    # Layer 2: Semantic
    role: str = "UNKNOWN"
    concept_count: int = 1
    concept_entropy: float = 0.0
    naming_drift: float = 0.0
    todo_density: float = 0.0
    docstring_coverage: float | None = None
    semantic_coherence: float = 0.5

    # Layer 3: Graph (per relationship type, here showing IMPORT)
    pagerank: float = 0.0
    betweenness: float = 0.0
    in_degree: int = 0
    out_degree: int = 0
    blast_radius_size: int = 0
    depth: int = -1
    is_orphan: bool = False
    cycle_member: bool = False
    cycle_size: int = 0
    phantom_import_count: int = 0
    community: int = -1
    compression_ratio: float = 0.0
    cognitive_load: float = 0.0

    # Layer 3: Graph (additional relationship types)
    pagerank_cochange: float = 0.0
    pagerank_combined: float = 0.0
    community_cochange: int = -1

    # Layer 4: Trajectory
    pagerank_velocity: float = 0.0
    pagerank_acceleration: float = 0.0
    community_stability: float = 1.0
    centrality_trend: float = 0.0

    # Layer 5: Cross-Layer
    hidden_coupling_count: int = 0
    neighborhood_coherence: float = 1.0

    # Layer 6: Composites
    raw_risk: float = 0.0
    risk_score: float = 0.0
    wiring_quality: float = 1.0
    file_health_score: float = 1.0
    delta_h: float = 0.0

    # Percentiles (filled during normalization)
    percentiles: dict[str, float] = field(default_factory=dict)

@dataclass
class ModuleSignals:
    path: str
    file_count: int = 0

    # Martin Metrics
    cohesion: float = 0.0
    coupling: float = 0.0
    instability: float | None = None  # None if isolated
    abstractness: float = 0.0
    main_seq_distance: float = 0.0

    # Boundary
    boundary_alignment: float = 0.0
    layer_violation_count: int = 0
    role_consistency: float = 0.0

    # Temporal
    velocity: float = 0.0
    coordination_cost: float = 0.0
    knowledge_gini: float = 0.0
    module_bus_factor: float = 1.0

    # Aggregate
    mean_cognitive_load: float = 0.0
    health_score: float = 0.0

@dataclass
class GlobalSignals:
    # Graph Structure
    modularity: float = 0.0
    fiedler_value: float = 0.0
    spectral_gap: float = 0.0
    cycle_count: int = 0
    centrality_gini: float = 0.0

    # Multi-layer
    modularity_cochange: float = 0.0
    fiedler_cochange: float = 0.0

    # Wiring
    orphan_ratio: float = 0.0
    phantom_ratio: float = 0.0
    glue_deficit: float = 0.0
    clone_ratio: float = 0.0
    violation_rate: float = 0.0

    # Trajectory
    graph_velocity: float = 0.0
    fiedler_trend: float = 0.0
    modularity_trend: float = 0.0
    topology_stability: float = 1.0

    # Cross-Layer
    behavioral_coherence: float = 0.0
    conway_alignment: float = 1.0
    semantic_alignment: float = 0.0

    # Social
    team_size: int = 1

    # Composites
    wiring_score: float = 0.0
    architecture_health: float = 0.0
    team_risk: float = 0.0
    codebase_health: float = 0.0
```

### 4.6 Findings (Layer 7 Output)

```python
@dataclass
class Finding:
    id: str                  # unique identifier
    pattern: str             # e.g., "HIDDEN_COUPLING"
    scope: str               # FILE, PAIR, MODULE, CODEBASE
    target: str              # file path or "file_a|file_b" for pairs
    severity: float          # 0.0 to 1.0
    confidence: float        # 0.0 to 1.0
    title: str               # human-readable title
    description: str         # detailed description
    remediation: str         # suggested fix
    evidence: dict[str, float]  # signal values that triggered

@dataclass
class FindingLifecycle:
    pattern: str
    target: str
    first_seen_snapshot: str
    last_seen_snapshot: str
    persistence_count: int
    status: str              # 'active', 'resolved'
```

---

# Part III: Pipeline Specification

## 5. Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Stage 0          Stage 1         Stage 2         Stage 3              │
│  ┌────────┐      ┌────────┐      ┌────────┐      ┌────────┐            │
│  │Extract │─────▶│ Index  │─────▶│ Graph  │─────▶│Signals │            │
│  └───┬────┘      └───┬────┘      └───┬────┘      └───┬────┘            │
│      │               │               │               │                  │
│      ▼               ▼               ▼               ▼                  │
│  facts.db       temporal.db      graph.db       signals.db              │
│                                                                         │
│                                                     │                   │
│                                                     ▼                   │
│                                   Stage 4         Stage 5               │
│                                  ┌────────┐      ┌────────┐            │
│                                  │Pattern │─────▶│Snapshot│            │
│                                  └───┬────┘      └───┬────┘            │
│                                      │               │                  │
│                                      ▼               ▼                  │
│                                 findings.db     snapshots.db            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

Each stage:
1. Reads from database tables written by previous stages
2. Performs computation
3. Writes results to database tables
4. Validates outputs before proceeding

---

## 6. Stage 0: Raw Extraction

### 6.1 Purpose
Extract raw facts from source files and git repository.

### 6.2 Inputs
- File system (source files)
- Git repository

### 6.3 Outputs
- `file_facts` table
- `git_commits` table
- `git_file_changes` table

### 6.4 Algorithm

```
STAGE_0_EXTRACT(repo_path, config):
    session_id = generate_uuid()

    # 6.4.1 Discover files
    files = []
    for path in walk(repo_path):
        if should_exclude(path, config.exclude_patterns):
            continue
        if get_extension(path) not in SUPPORTED_EXTENSIONS:
            continue
        if file_size(path) > config.max_file_size:
            continue
        files.append(path)
        if len(files) >= config.max_files:
            break

    # 6.4.2 Parse each file
    for path in files:
        content = read_file(path)
        content_hash = sha256(content)

        # Check if already parsed with same hash
        existing = db.query("SELECT * FROM file_facts WHERE path=? AND content_hash=?", path, content_hash)
        if existing:
            continue

        # Parse
        language = detect_language(path)
        syntax = parse_file(content, language)

        # Store
        db.insert("file_facts", {
            session_id: session_id,
            path: path,
            content_hash: content_hash,
            language: language,
            lines: syntax.lines,
            functions: len(syntax.functions),
            classes: len(syntax.classes),
            imports: len(syntax.imports),
            complexity: syntax.complexity,
            max_nesting: syntax.max_nesting,
            stub_count: count(f for f in syntax.functions if f.is_stub),
            function_data: json(syntax.functions),
            class_data: json(syntax.classes),
            import_data: json(syntax.imports),
        })

    # 6.4.3 Extract git commits
    last_commit = db.query("SELECT MAX(hash) FROM git_commits")

    git_log = run("git log --format='%H|%at|%ae|%s' {last_commit}..HEAD")
    for line in git_log:
        hash, timestamp, author, subject = line.split('|', 3)
        db.insert("git_commits", {
            hash: hash,
            timestamp: int(timestamp),
            author_email: author,
            subject: subject,
            session_id: session_id,
        })

    # 6.4.4 Extract file changes
    git_log = run("git log --name-status --numstat --format='COMMIT:%H' {last_commit}..HEAD")
    current_commit = None
    for line in git_log:
        if line.startswith("COMMIT:"):
            current_commit = line[7:]
        elif line:
            # Parse file change
            change_type, path, old_path, additions, deletions = parse_change_line(line)
            db.insert("git_file_changes", {
                commit_hash: current_commit,
                file_path: path,
                change_type: change_type,
                old_path: old_path,
                additions: additions,
                deletions: deletions,
            })

    return session_id
```

### 6.5 File Parsing by Language

```
PARSE_FILE(content, language):
    if treesitter_available(language):
        return parse_with_treesitter(content, language)
    else:
        return parse_with_regex(content, language)

# Python regex patterns
PYTHON_PATTERNS = {
    function: r'^(\s*)def\s+(\w+)\s*\(',
    class: r'^(\s*)class\s+(\w+)',
    import: r'^(?:from\s+([\w.]+)\s+)?import\s+([\w.]+)',
}

# TypeScript/JavaScript regex patterns
TYPESCRIPT_PATTERNS = {
    function: r'(?:function\s+(\w+)|(\w+)\s*[=:]\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
    class: r'class\s+(\w+)',
    import: r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
}

# Go regex patterns
GO_PATTERNS = {
    function: r'^func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(',
    struct: r'^type\s+(\w+)\s+struct\s*\{',
    import: r'import\s+(?:\w+\s+)?[\'"]([^\'"]+)[\'"]',
}
```

### 6.6 Database Schema

```sql
-- facts.db

CREATE TABLE file_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    language TEXT NOT NULL,
    lines INTEGER NOT NULL,
    functions INTEGER NOT NULL,
    classes INTEGER NOT NULL,
    imports INTEGER NOT NULL,
    complexity INTEGER NOT NULL,
    max_nesting INTEGER NOT NULL,
    stub_count INTEGER NOT NULL,
    function_data TEXT,  -- JSON
    class_data TEXT,     -- JSON
    import_data TEXT,    -- JSON
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),

    UNIQUE(session_id, path)
);

CREATE INDEX idx_file_facts_session ON file_facts(session_id);
CREATE INDEX idx_file_facts_path ON file_facts(path);
CREATE INDEX idx_file_facts_hash ON file_facts(content_hash);

CREATE TABLE git_commits (
    hash TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    author_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    session_id TEXT NOT NULL
);

CREATE INDEX idx_git_commits_timestamp ON git_commits(timestamp DESC);
CREATE INDEX idx_git_commits_author ON git_commits(author_email);

CREATE TABLE git_file_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_hash TEXT NOT NULL,
    file_path TEXT NOT NULL,
    change_type TEXT NOT NULL,
    old_path TEXT,
    additions INTEGER,
    deletions INTEGER,

    FOREIGN KEY (commit_hash) REFERENCES git_commits(hash)
);

CREATE INDEX idx_file_changes_commit ON git_file_changes(commit_hash);
CREATE INDEX idx_file_changes_path ON git_file_changes(file_path);
```

---

## 7. Stage 1: Temporal Index

### 7.1 Purpose
Build temporal indexes that enable reconstruction of any graph at any historical time point.

### 7.2 Inputs
- `file_facts` table
- `git_commits` table
- `git_file_changes` table

### 7.3 Outputs
- `events` table
- `node_lifecycle` table
- `edge_lifecycle` table
- `time_windows` table
- `window_cochange` table
- `window_authors` table

### 7.4 Algorithm

```
STAGE_1_INDEX(session_id):
    # 7.4.1 Build event log
    events = []

    # Node events from file changes
    for change in db.query("SELECT * FROM git_file_changes ORDER BY commit_hash"):
        commit = db.query("SELECT * FROM git_commits WHERE hash=?", change.commit_hash)

        if change.change_type == 'A':  # Add
            events.append(GraphEvent(
                timestamp=commit.timestamp,
                commit_hash=commit.hash,
                event_type='NODE_ADD',
                relation_type=None,
                source_path=change.file_path,
                target_path=None,
                author=commit.author_email,
            ))
        elif change.change_type == 'D':  # Delete
            events.append(GraphEvent(
                timestamp=commit.timestamp,
                commit_hash=commit.hash,
                event_type='NODE_REMOVE',
                relation_type=None,
                source_path=change.file_path,
                target_path=None,
                author=commit.author_email,
            ))
        elif change.change_type == 'R':  # Rename
            events.append(GraphEvent(
                timestamp=commit.timestamp,
                commit_hash=commit.hash,
                event_type='NODE_RENAME',
                relation_type=None,
                source_path=change.old_path,
                target_path=change.file_path,
                author=commit.author_email,
            ))

    # Sort by timestamp
    events.sort(key=lambda e: e.timestamp)

    # Store events
    for event in events:
        db.insert("events", event)

    # 7.4.2 Compute node lifecycle
    node_births = {}  # path -> (timestamp, commit)
    node_deaths = {}  # path -> (timestamp, commit)
    renames = {}      # old_path -> new_path

    for event in events:
        if event.event_type == 'NODE_ADD':
            if event.source_path not in node_births:
                node_births[event.source_path] = (event.timestamp, event.commit_hash)
        elif event.event_type == 'NODE_REMOVE':
            node_deaths[event.source_path] = (event.timestamp, event.commit_hash)
        elif event.event_type == 'NODE_RENAME':
            renames[event.source_path] = event.target_path

    # Resolve rename chains
    def canonical(path):
        visited = set()
        while path in renames and path not in visited:
            visited.add(path)
            path = renames[path]
        return path

    # Store node lifecycle
    all_paths = set(node_births.keys()) | set(node_deaths.keys())
    for path in all_paths:
        birth_ts, birth_commit = node_births.get(path, (0, None))
        death_ts, death_commit = node_deaths.get(path, (None, None))

        db.insert("node_lifecycle", {
            path: path,
            canonical_path: canonical(path),
            birth_ts: birth_ts,
            death_ts: death_ts,
            birth_commit: birth_commit,
            death_commit: death_commit,
        })

    # 7.4.3 Build time windows
    commits = db.query("SELECT * FROM git_commits ORDER BY timestamp")
    if not commits:
        return

    min_ts = commits[0].timestamp
    max_ts = commits[-1].timestamp
    window_size = 28 * 24 * 60 * 60  # 4 weeks in seconds

    windows = []
    current_start = min_ts
    while current_start < max_ts:
        current_end = current_start + window_size
        windows.append((current_start, current_end))
        current_start = current_end

    for i, (start, end) in enumerate(windows):
        window_commits = [c for c in commits if start <= c.timestamp < end]
        db.insert("time_windows", {
            id: i,
            window_start: start,
            window_end: end,
            commit_count: len(window_commits),
        })

    # 7.4.4 Compute cochange per window
    for window_id, (start, end) in enumerate(windows):
        # Get commits in window
        window_commits = db.query(
            "SELECT hash FROM git_commits WHERE timestamp >= ? AND timestamp < ?",
            start, end
        )

        # Get files changed per commit
        for commit in window_commits:
            files = db.query(
                "SELECT file_path FROM git_file_changes WHERE commit_hash = ?",
                commit.hash
            )
            file_paths = [f.file_path for f in files]

            # Count cochange pairs
            for i, a in enumerate(file_paths):
                for b in file_paths[i+1:]:
                    key = (min(a, b), max(a, b))
                    db.upsert("window_cochange", {
                        window_id: window_id,
                        file_a: key[0],
                        file_b: key[1],
                        cochange_count: "cochange_count + 1",
                    })

        # Get author counts per file
        for commit in window_commits:
            author = db.query("SELECT author_email FROM git_commits WHERE hash=?", commit.hash)
            files = db.query("SELECT file_path FROM git_file_changes WHERE commit_hash=?", commit.hash)

            for f in files:
                db.upsert("window_authors", {
                    window_id: window_id,
                    file_path: f.file_path,
                    author: author.author_email,
                    commit_count: "commit_count + 1",
                })
```

### 7.5 Database Schema

```sql
-- temporal.db

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    commit_hash TEXT NOT NULL,
    event_type TEXT NOT NULL,
    relation_type TEXT,
    source_path TEXT NOT NULL,
    target_path TEXT,
    author TEXT NOT NULL
);

CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_source ON events(source_path);

CREATE TABLE node_lifecycle (
    path TEXT PRIMARY KEY,
    canonical_path TEXT NOT NULL,
    birth_ts INTEGER NOT NULL,
    death_ts INTEGER,
    birth_commit TEXT,
    death_commit TEXT
);

CREATE INDEX idx_node_lifecycle_canonical ON node_lifecycle(canonical_path);
CREATE INDEX idx_node_lifecycle_birth ON node_lifecycle(birth_ts);

CREATE TABLE edge_lifecycle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relation_type TEXT NOT NULL,
    source_path TEXT NOT NULL,
    target_path TEXT NOT NULL,
    birth_ts INTEGER NOT NULL,
    death_ts INTEGER,
    birth_commit TEXT,
    death_commit TEXT,

    UNIQUE(relation_type, source_path, target_path, birth_ts)
);

CREATE INDEX idx_edge_lifecycle_relation ON edge_lifecycle(relation_type);

CREATE TABLE time_windows (
    id INTEGER PRIMARY KEY,
    window_start INTEGER NOT NULL,
    window_end INTEGER NOT NULL,
    commit_count INTEGER NOT NULL
);

CREATE TABLE window_cochange (
    window_id INTEGER NOT NULL,
    file_a TEXT NOT NULL,
    file_b TEXT NOT NULL,
    cochange_count INTEGER NOT NULL DEFAULT 1,

    PRIMARY KEY(window_id, file_a, file_b),
    FOREIGN KEY(window_id) REFERENCES time_windows(id)
);

CREATE TABLE window_authors (
    window_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    author TEXT NOT NULL,
    commit_count INTEGER NOT NULL DEFAULT 1,

    PRIMARY KEY(window_id, file_path, author),
    FOREIGN KEY(window_id) REFERENCES time_windows(id)
);
```

---

## 8. Stage 2: Graph Construction

### 8.1 Purpose
Build all relationship graphs from indexed data.

### 8.2 Sub-stages

| Sub-stage | Graph | Source |
|-----------|-------|--------|
| 2a | G_import | file_facts.import_data |
| 2b | G_cochange | window_cochange |
| 2c | G_author | window_authors |
| 2d | G_semantic | file_facts (TF-IDF) |
| 2e | G_clone | file content (NCD) |
| 2f | G_combined | all above |

### 8.3 Algorithm

```
STAGE_2_GRAPHS(snapshot_id):
    # Get current files
    files = db.query("SELECT path FROM file_facts WHERE session_id = ?", session_id)
    file_set = {f.path for f in files}

    # 8.3.1 Build G_import
    for file in files:
        imports = json.loads(file.import_data)
        for imp in imports:
            target = resolve_import(imp.module, file.path, file_set)
            if target and target in file_set:
                db.insert("graph_edges", {
                    snapshot_id: snapshot_id,
                    relation_type: 'IMPORT',
                    source_path: file.path,
                    target_path: target,
                    weight: 1.0,
                })

    # 8.3.2 Build G_cochange
    # Use recent windows (e.g., last 6 months)
    recent_windows = db.query(
        "SELECT id FROM time_windows ORDER BY window_end DESC LIMIT 26"
    )

    cochange_totals = {}  # (a, b) -> total count
    file_counts = {}      # file -> commit count
    total_commits = 0

    for window in recent_windows:
        total_commits += window.commit_count

        pairs = db.query("SELECT * FROM window_cochange WHERE window_id = ?", window.id)
        for pair in pairs:
            if pair.file_a in file_set and pair.file_b in file_set:
                key = (pair.file_a, pair.file_b)
                cochange_totals[key] = cochange_totals.get(key, 0) + pair.cochange_count

        authors = db.query("SELECT file_path, SUM(commit_count) as total FROM window_authors WHERE window_id = ? GROUP BY file_path", window.id)
        for a in authors:
            file_counts[a.file_path] = file_counts.get(a.file_path, 0) + a.total

    # Compute lift and store edges
    for (a, b), count in cochange_totals.items():
        p_a = file_counts.get(a, 0) / total_commits
        p_b = file_counts.get(b, 0) / total_commits
        p_ab = count / total_commits

        if p_a > 0 and p_b > 0:
            lift = p_ab / (p_a * p_b)
            if lift > 1.0:  # More than random
                db.insert("graph_edges", {
                    snapshot_id: snapshot_id,
                    relation_type: 'COCHANGE',
                    source_path: a,
                    target_path: b,
                    weight: lift,
                })

    # 8.3.3 Build G_author
    author_sets = {}  # file -> set of authors
    for window in recent_windows:
        authors = db.query("SELECT file_path, author FROM window_authors WHERE window_id = ?", window.id)
        for a in authors:
            if a.file_path not in author_sets:
                author_sets[a.file_path] = set()
            author_sets[a.file_path].add(a.author)

    # Compute Jaccard and store edges
    file_list = list(file_set)
    for i, a in enumerate(file_list):
        for b in file_list[i+1:]:
            if a in author_sets and b in author_sets:
                set_a = author_sets[a]
                set_b = author_sets[b]
                intersection = len(set_a & set_b)
                union = len(set_a | set_b)
                if union > 0:
                    jaccard = intersection / union
                    if jaccard > 0.1:  # Non-trivial overlap
                        db.insert("graph_edges", {
                            snapshot_id: snapshot_id,
                            relation_type: 'AUTHOR',
                            source_path: a,
                            target_path: b,
                            weight: jaccard,
                        })

    # 8.3.4 Build G_semantic
    # Extract concepts via TF-IDF
    concepts = {}  # file -> {concept: weight}
    for file in files:
        functions = json.loads(file.function_data)
        classes = json.loads(file.class_data)

        # Tokenize identifiers
        tokens = []
        for f in functions:
            tokens.extend(split_camel_snake(f.name))
        for c in classes:
            tokens.extend(split_camel_snake(c.name))

        # Count term frequency
        tf = Counter(tokens)
        concepts[file.path] = tf

    # Compute IDF
    doc_count = len(files)
    idf = {}
    for file_concepts in concepts.values():
        for term in file_concepts:
            idf[term] = idf.get(term, 0) + 1
    for term in idf:
        idf[term] = log(doc_count / idf[term])

    # Compute TF-IDF vectors and cosine similarity
    vectors = {}
    for path, tf in concepts.items():
        vector = {term: freq * idf.get(term, 0) for term, freq in tf.items()}
        norm = sqrt(sum(v*v for v in vector.values()))
        if norm > 0:
            vectors[path] = {k: v/norm for k, v in vector.items()}

    # Store semantic edges
    for i, a in enumerate(file_list):
        for b in file_list[i+1:]:
            if a in vectors and b in vectors:
                # Cosine similarity
                dot = sum(vectors[a].get(k, 0) * vectors[b].get(k, 0) for k in vectors[a])
                if dot > 0.3:
                    db.insert("graph_edges", {
                        snapshot_id: snapshot_id,
                        relation_type: 'SEMANTIC',
                        source_path: a,
                        target_path: b,
                        weight: dot,
                    })

    # Store concepts for later use
    for path, tf in concepts.items():
        for concept, weight in tf.items():
            db.insert("file_concepts", {
                snapshot_id: snapshot_id,
                file_path: path,
                concept: concept,
                weight: weight * idf.get(concept, 0),
            })

    # 8.3.5 Build G_clone (if not too many files)
    if len(file_list) <= 5000:
        contents = {}
        for file in files:
            content = read_file(file.path)
            contents[file.path] = content

        for i, a in enumerate(file_list):
            for b in file_list[i+1:]:
                ncd = normalized_compression_distance(contents[a], contents[b])
                if ncd < 0.3:
                    db.insert("graph_edges", {
                        snapshot_id: snapshot_id,
                        relation_type: 'CLONE',
                        source_path: a,
                        target_path: b,
                        weight: 1.0 - ncd,
                    })

    # 8.3.6 Build G_combined
    # Collect all edges
    all_edges = {}  # (a, b) -> {relation_type: weight}
    edges = db.query("SELECT * FROM graph_edges WHERE snapshot_id = ?", snapshot_id)
    for e in edges:
        key = (min(e.source_path, e.target_path), max(e.source_path, e.target_path))
        if key not in all_edges:
            all_edges[key] = {}
        all_edges[key][e.relation_type] = e.weight

    # Combine with weights
    weights = {
        'IMPORT': 0.35,
        'COCHANGE': 0.30,
        'AUTHOR': 0.15,
        'SEMANTIC': 0.15,
        'CLONE': 0.05,
    }

    for (a, b), relations in all_edges.items():
        combined_weight = sum(
            weights.get(r, 0) * w
            for r, w in relations.items()
        )
        if combined_weight > 0:
            db.insert("graph_edges", {
                snapshot_id: snapshot_id,
                relation_type: 'COMBINED',
                source_path: a,
                target_path: b,
                weight: combined_weight,
            })
```

### 8.4 Helper Functions

```
RESOLVE_IMPORT(module, source_file, file_set):
    """Resolve import module string to file path."""

    # Handle relative imports (Python)
    if module.startswith('.'):
        base_dir = dirname(source_file)
        dots = len(module) - len(module.lstrip('.'))
        for _ in range(dots - 1):
            base_dir = dirname(base_dir)
        rest = module.lstrip('.')
        candidates = [
            join(base_dir, rest.replace('.', '/') + '.py'),
            join(base_dir, rest.replace('.', '/'), '__init__.py'),
        ]
    else:
        # Absolute import
        candidates = [
            module.replace('.', '/') + '.py',
            join(module.replace('.', '/'), '__init__.py'),
        ]

    for candidate in candidates:
        if candidate in file_set:
            return candidate

    return None  # External or unresolved

NORMALIZED_COMPRESSION_DISTANCE(a: bytes, b: bytes) -> float:
    """NCD = (C(ab) - min(C(a), C(b))) / max(C(a), C(b))"""
    import zlib

    c_a = len(zlib.compress(a))
    c_b = len(zlib.compress(b))
    c_ab = len(zlib.compress(a + b))

    return (c_ab - min(c_a, c_b)) / max(c_a, c_b)
```

### 8.5 Database Schema

```sql
-- graph.db

CREATE TABLE graph_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    source_path TEXT NOT NULL,
    target_path TEXT NOT NULL,
    weight REAL NOT NULL DEFAULT 1.0,
    metadata TEXT,

    UNIQUE(snapshot_id, relation_type, source_path, target_path)
);

CREATE INDEX idx_graph_edges_snapshot ON graph_edges(snapshot_id, relation_type);
CREATE INDEX idx_graph_edges_source ON graph_edges(source_path);
CREATE INDEX idx_graph_edges_target ON graph_edges(target_path);

CREATE TABLE file_concepts (
    snapshot_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    concept TEXT NOT NULL,
    weight REAL NOT NULL,

    PRIMARY KEY(snapshot_id, file_path, concept)
);

CREATE TABLE graph_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    node_count INTEGER NOT NULL,
    edge_count INTEGER NOT NULL,

    UNIQUE(snapshot_id, relation_type, timestamp)
);
```

---

## 9. Stage 3: Signal Computation

### 9.1 Purpose
Compute all signals from graphs and temporal data.

### 9.2 Sub-stages

| Sub-stage | Signals | Dependencies |
|-----------|---------|--------------|
| 3a | Graph algorithms | Stage 2 graphs |
| 3b | Temporal signals | Stage 1 windows |
| 3c | Semantic signals | Stage 0 facts |
| 3d | Trajectory signals | Historical snapshots |
| 3e | Cross-layer signals | Multiple graphs |
| 3f | Composite signals | All above |

### 9.3 Stage 3a: Graph Algorithms

```
STAGE_3A_GRAPH_ALGORITHMS(snapshot_id):
    relation_types = ['IMPORT', 'COCHANGE', 'AUTHOR', 'SEMANTIC', 'COMBINED']

    for rel_type in relation_types:
        # Load graph
        edges = db.query(
            "SELECT source_path, target_path, weight FROM graph_edges WHERE snapshot_id=? AND relation_type=?",
            snapshot_id, rel_type
        )

        graph = build_graph(edges)

        # 9.3.1 PageRank
        pagerank = compute_pagerank(graph, damping=0.85, iterations=100)
        for node, value in pagerank.items():
            store_signal(snapshot_id, node, f'pagerank_{rel_type}', value)

        # 9.3.2 Betweenness
        betweenness = compute_betweenness(graph)
        for node, value in betweenness.items():
            store_signal(snapshot_id, node, f'betweenness_{rel_type}', value)

        # 9.3.3 Degree
        for node in graph.nodes:
            in_deg = len(graph.reverse.get(node, []))
            out_deg = len(graph.adjacency.get(node, []))
            store_signal(snapshot_id, node, f'in_degree_{rel_type}', in_deg)
            store_signal(snapshot_id, node, f'out_degree_{rel_type}', out_deg)

        # 9.3.4 Community detection (Louvain)
        communities, modularity = compute_louvain(graph)
        for node, comm_id in communities.items():
            store_signal(snapshot_id, node, f'community_{rel_type}', comm_id)
        store_global_signal(snapshot_id, f'modularity_{rel_type}', modularity)

        # 9.3.5 Spectral (Fiedler value)
        fiedler, spectral_gap = compute_spectral(graph)
        store_global_signal(snapshot_id, f'fiedler_{rel_type}', fiedler)
        store_global_signal(snapshot_id, f'spectral_gap_{rel_type}', spectral_gap)

        # For IMPORT graph only:
        if rel_type == 'IMPORT':
            # 9.3.6 SCC (cycles)
            sccs = compute_scc(graph)
            cycle_count = 0
            for scc in sccs:
                if len(scc) > 1:
                    cycle_count += 1
                    for node in scc:
                        store_signal(snapshot_id, node, 'cycle_member', 1)
                        store_signal(snapshot_id, node, 'cycle_size', len(scc))
            store_global_signal(snapshot_id, 'cycle_count', cycle_count)

            # 9.3.7 Depth (BFS from entry points)
            entry_points = find_entry_points(graph)
            depths = compute_bfs_depth(graph, entry_points)
            for node, depth in depths.items():
                store_signal(snapshot_id, node, 'depth', depth)

            # 9.3.8 Blast radius
            for node in graph.nodes:
                blast = compute_transitive_closure(graph.reverse, node)
                store_signal(snapshot_id, node, 'blast_radius_size', len(blast))

            # 9.3.9 Orphan detection
            for node in graph.nodes:
                is_orphan = len(graph.reverse.get(node, [])) == 0
                store_signal(snapshot_id, node, 'is_orphan', 1 if is_orphan else 0)

            # 9.3.10 Phantom imports
            for node in graph.nodes:
                imports = db.query("SELECT import_data FROM file_facts WHERE path=?", node)
                if imports:
                    import_list = json.loads(imports.import_data)
                    resolved = graph.adjacency.get(node, [])
                    phantom_count = len(import_list) - len(resolved)
                    store_signal(snapshot_id, node, 'phantom_import_count', max(0, phantom_count))

        # 9.3.11 Centrality Gini
        pr_values = list(pagerank.values())
        gini = compute_gini(pr_values)
        store_global_signal(snapshot_id, f'centrality_gini_{rel_type}', gini)
```

### 9.4 Graph Algorithm Implementations

```
COMPUTE_PAGERANK(graph, damping=0.85, iterations=100, tolerance=1e-6):
    """PageRank centrality."""
    n = len(graph.nodes)
    if n == 0:
        return {}

    # Initialize
    pr = {node: 1.0 / n for node in graph.nodes}

    for _ in range(iterations):
        new_pr = {}
        diff = 0.0

        for node in graph.nodes:
            # Sum of PR from incoming edges
            incoming_sum = 0.0
            for source in graph.reverse.get(node, []):
                out_degree = len(graph.adjacency.get(source, []))
                if out_degree > 0:
                    incoming_sum += pr[source] / out_degree

            new_pr[node] = (1 - damping) / n + damping * incoming_sum
            diff += abs(new_pr[node] - pr[node])

        pr = new_pr
        if diff < tolerance:
            break

    return pr

COMPUTE_BETWEENNESS(graph):
    """Betweenness centrality using Brandes' algorithm."""
    betweenness = {node: 0.0 for node in graph.nodes}

    for source in graph.nodes:
        # BFS from source
        stack = []
        predecessors = {node: [] for node in graph.nodes}
        sigma = {node: 0.0 for node in graph.nodes}
        sigma[source] = 1.0
        distance = {node: -1 for node in graph.nodes}
        distance[source] = 0

        queue = [source]
        while queue:
            v = queue.pop(0)
            stack.append(v)
            for w in graph.adjacency.get(v, []):
                if distance[w] < 0:
                    distance[w] = distance[v] + 1
                    queue.append(w)
                if distance[w] == distance[v] + 1:
                    sigma[w] += sigma[v]
                    predecessors[w].append(v)

        # Accumulation
        delta = {node: 0.0 for node in graph.nodes}
        while stack:
            w = stack.pop()
            for v in predecessors[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != source:
                betweenness[w] += delta[w]

    # Normalize
    n = len(graph.nodes)
    if n > 2:
        scale = 1.0 / ((n - 1) * (n - 2))
        for node in betweenness:
            betweenness[node] *= scale

    return betweenness

COMPUTE_LOUVAIN(graph):
    """Louvain community detection."""
    # Initialize each node in its own community
    node_to_comm = {node: i for i, node in enumerate(sorted(graph.nodes))}

    # Build undirected weighted adjacency
    weights = {}
    degree = {node: 0.0 for node in graph.nodes}
    for src, targets in graph.adjacency.items():
        for tgt in targets:
            w = graph.weights.get((src, tgt), 1.0)
            key = (min(src, tgt), max(src, tgt))
            weights[key] = weights.get(key, 0) + w
            degree[src] += w
            degree[tgt] += w

    m = sum(weights.values())
    if m == 0:
        return node_to_comm, 0.0

    improved = True
    while improved:
        improved = False
        for node in sorted(graph.nodes):
            current_comm = node_to_comm[node]
            best_comm = current_comm
            best_gain = 0.0

            # Calculate gain for moving to each neighbor's community
            neighbor_comms = {}
            for neighbor in graph.neighbors(node, 'both'):
                comm = node_to_comm[neighbor]
                key = (min(node, neighbor), max(node, neighbor))
                w = weights.get(key, 0)
                neighbor_comms[comm] = neighbor_comms.get(comm, 0) + w

            for comm, ki_in in neighbor_comms.items():
                if comm == current_comm:
                    continue
                # Modularity gain formula
                sigma_tot = sum(degree[n] for n in graph.nodes if node_to_comm[n] == comm)
                ki = degree[node]
                gain = ki_in / m - (sigma_tot * ki) / (2 * m * m)
                if gain > best_gain:
                    best_gain = gain
                    best_comm = comm

            if best_comm != current_comm:
                node_to_comm[node] = best_comm
                improved = True

    # Compute final modularity
    modularity = 0.0
    for (a, b), w in weights.items():
        if node_to_comm[a] == node_to_comm[b]:
            modularity += w / m - (degree[a] * degree[b]) / (4 * m * m)

    return node_to_comm, modularity

COMPUTE_SPECTRAL(graph):
    """Compute Fiedler value (algebraic connectivity) and spectral gap."""
    n = len(graph.nodes)
    if n < 2:
        return 0.0, 0.0

    # Build Laplacian matrix
    nodes = sorted(graph.nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}

    L = [[0.0] * n for _ in range(n)]

    for src, targets in graph.adjacency.items():
        i = node_idx[src]
        for tgt in targets:
            j = node_idx[tgt]
            w = graph.weights.get((src, tgt), 1.0)
            L[i][i] += w
            L[i][j] -= w
            L[j][j] += w
            L[j][i] -= w

    # Compute eigenvalues (using power iteration for simplicity)
    # In production, use numpy.linalg.eigvalsh
    eigenvalues = compute_eigenvalues(L)
    eigenvalues.sort()

    fiedler = eigenvalues[1] if len(eigenvalues) > 1 else 0.0
    spectral_gap = eigenvalues[2] - eigenvalues[1] if len(eigenvalues) > 2 else 0.0

    return fiedler, spectral_gap

COMPUTE_SCC(graph):
    """Tarjan's algorithm for strongly connected components."""
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = set()
    sccs = []

    def strongconnect(node):
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)

        for successor in graph.adjacency.get(node, []):
            if successor not in index:
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif successor in on_stack:
                lowlinks[node] = min(lowlinks[node], index[successor])

        if lowlinks[node] == index[node]:
            scc = set()
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.add(w)
                if w == node:
                    break
            sccs.append(scc)

    for node in graph.nodes:
        if node not in index:
            strongconnect(node)

    return sccs

COMPUTE_BFS_DEPTH(graph, entry_points):
    """BFS from entry points to compute depth."""
    depths = {node: -1 for node in graph.nodes}

    queue = []
    for ep in entry_points:
        if ep in graph.nodes:
            depths[ep] = 0
            queue.append((ep, 0))

    while queue:
        node, depth = queue.pop(0)
        for neighbor in graph.adjacency.get(node, []):
            if depths[neighbor] == -1:
                depths[neighbor] = depth + 1
                queue.append((neighbor, depth + 1))

    return depths

COMPUTE_TRANSITIVE_CLOSURE(reverse_adj, start):
    """BFS to find all nodes reachable from start in reverse graph."""
    visited = set()
    queue = list(reverse_adj.get(start, []))

    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        queue.extend(reverse_adj.get(node, []))

    return visited

COMPUTE_GINI(values):
    """Gini coefficient for inequality measurement."""
    if not values or len(values) < 2:
        return 0.0

    values = sorted(values)
    n = len(values)
    total = sum(values)

    if total == 0:
        return 0.0

    weighted_sum = sum((i + 1) * v for i, v in enumerate(values))
    gini = (2 * weighted_sum) / (n * total) - (n + 1) / n

    # Bias correction
    gini *= n / (n - 1)

    return max(0.0, min(1.0, gini))
```

### 9.5 Stage 3b: Temporal Signals

```
STAGE_3B_TEMPORAL_SIGNALS(snapshot_id):
    files = db.query("SELECT DISTINCT path FROM file_facts WHERE session_id=?", session_id)
    windows = db.query("SELECT * FROM time_windows ORDER BY window_start")

    for file in files:
        # Get churn per window
        churn_series = []
        for window in windows:
            churn = db.query(
                """SELECT SUM(additions + deletions) as churn
                   FROM git_file_changes fc
                   JOIN git_commits c ON fc.commit_hash = c.hash
                   WHERE fc.file_path = ? AND c.timestamp >= ? AND c.timestamp < ?""",
                file.path, window.window_start, window.window_end
            )
            churn_series.append(churn.churn or 0)

        total_changes = sum(churn_series)
        store_signal(snapshot_id, file.path, 'total_changes', total_changes)

        # Coefficient of variation
        if len(churn_series) >= 3 and total_changes > 0:
            mean_churn = total_changes / len(churn_series)
            variance = sum((c - mean_churn)**2 for c in churn_series) / (len(churn_series) - 1)
            std_churn = sqrt(variance)
            cv = std_churn / mean_churn if mean_churn > 0 else 0
            store_signal(snapshot_id, file.path, 'churn_cv', cv)
        else:
            store_signal(snapshot_id, file.path, 'churn_cv', 0.0)

        # Churn slope (linear regression)
        if len(churn_series) >= 2:
            n = len(churn_series)
            x_mean = (n - 1) / 2
            y_mean = total_changes / n
            numerator = sum((i - x_mean) * (churn_series[i] - y_mean) for i in range(n))
            denominator = sum((i - x_mean)**2 for i in range(n))
            slope = numerator / denominator if denominator > 0 else 0
            store_signal(snapshot_id, file.path, 'churn_slope', slope)
        else:
            store_signal(snapshot_id, file.path, 'churn_slope', 0.0)

        # Trajectory classification
        cv = get_signal(snapshot_id, file.path, 'churn_cv')
        slope = get_signal(snapshot_id, file.path, 'churn_slope')

        if total_changes <= 1 or cv == 0:
            trajectory = 'DORMANT'
        elif slope < -0.1 and cv < 0.5:
            trajectory = 'STABILIZING'
        elif slope > 0.1 and cv > 0.5:
            trajectory = 'SPIKING'
        elif cv > 0.5:
            trajectory = 'CHURNING'
        else:
            trajectory = 'STABLE'
        store_signal(snapshot_id, file.path, 'churn_trajectory', trajectory)

        # Author entropy and bus factor
        authors = db.query(
            """SELECT author_email, COUNT(*) as commits
               FROM git_commits c
               JOIN git_file_changes fc ON c.hash = fc.commit_hash
               WHERE fc.file_path = ?
               GROUP BY author_email""",
            file.path
        )

        total_author_commits = sum(a.commits for a in authors)
        if total_author_commits > 0:
            entropy = 0.0
            for a in authors:
                p = a.commits / total_author_commits
                if p > 0:
                    entropy -= p * log2(p)
            store_signal(snapshot_id, file.path, 'author_entropy', entropy)
            store_signal(snapshot_id, file.path, 'bus_factor', 2 ** entropy)
        else:
            store_signal(snapshot_id, file.path, 'author_entropy', 0.0)
            store_signal(snapshot_id, file.path, 'bus_factor', 1.0)

        # Fix ratio and refactor ratio
        fix_keywords = ['fix', 'bug', 'patch', 'hotfix', 'repair', 'issue']
        refactor_keywords = ['refactor', 'cleanup', 'clean up', 'reorganize', 'restructure']

        commits = db.query(
            """SELECT c.subject
               FROM git_commits c
               JOIN git_file_changes fc ON c.hash = fc.commit_hash
               WHERE fc.file_path = ?""",
            file.path
        )

        fix_count = sum(1 for c in commits if any(kw in c.subject.lower() for kw in fix_keywords))
        refactor_count = sum(1 for c in commits if any(kw in c.subject.lower() for kw in refactor_keywords))
        total_commits = len(commits)

        store_signal(snapshot_id, file.path, 'fix_ratio', fix_count / total_commits if total_commits > 0 else 0)
        store_signal(snapshot_id, file.path, 'refactor_ratio', refactor_count / total_commits if total_commits > 0 else 0)
```

### 9.6 Stage 3c: Semantic Signals

```
STAGE_3C_SEMANTIC_SIGNALS(snapshot_id):
    files = db.query("SELECT * FROM file_facts WHERE session_id=?", session_id)

    for file in files:
        # Role classification
        role = classify_role(file)
        store_signal(snapshot_id, file.path, 'role', role)

        # Concept count and entropy
        concepts = db.query(
            "SELECT concept, weight FROM file_concepts WHERE snapshot_id=? AND file_path=?",
            snapshot_id, file.path
        )

        concept_count = len(concepts)
        store_signal(snapshot_id, file.path, 'concept_count', concept_count)

        if concepts:
            total_weight = sum(c.weight for c in concepts)
            entropy = 0.0
            for c in concepts:
                p = c.weight / total_weight if total_weight > 0 else 0
                if p > 0:
                    entropy -= p * log2(p)
            store_signal(snapshot_id, file.path, 'concept_entropy', entropy)
            store_signal(snapshot_id, file.path, 'semantic_coherence', 1.0 / (1.0 + entropy))
        else:
            store_signal(snapshot_id, file.path, 'concept_entropy', 0.0)
            store_signal(snapshot_id, file.path, 'semantic_coherence', 1.0)

        # Naming drift (consistency of naming conventions)
        functions = json.loads(file.function_data)
        snake_count = sum(1 for f in functions if '_' in f.name)
        camel_count = sum(1 for f in functions if f.name[0].islower() and any(c.isupper() for c in f.name))
        total = len(functions)

        if total > 1:
            dominant = max(snake_count, camel_count)
            naming_drift = 1 - (dominant / total)
        else:
            naming_drift = 0.0
        store_signal(snapshot_id, file.path, 'naming_drift', naming_drift)

        # TODO density
        content = read_file(file.path)
        todo_count = content.lower().count('todo') + content.lower().count('fixme')
        todo_density = todo_count / file.lines if file.lines > 0 else 0
        store_signal(snapshot_id, file.path, 'todo_density', todo_density)

        # Docstring coverage (Python only)
        if file.language == 'python':
            functions = json.loads(file.function_data)
            documented = sum(1 for f in functions if has_docstring(f))
            coverage = documented / len(functions) if functions else None
            store_signal(snapshot_id, file.path, 'docstring_coverage', coverage)

CLASSIFY_ROLE(file):
    """Classify file role based on patterns."""
    path = file.path.lower()

    # Test files
    if 'test' in path or path.endswith('_test.py') or path.endswith('.test.ts'):
        return 'TEST'

    # Entry points
    if '__main__' in file.content or 'if __name__' in file.content:
        return 'ENTRY_POINT'
    if path.endswith('main.py') or path.endswith('main.go') or path.endswith('index.ts'):
        return 'ENTRY_POINT'

    # Config files
    if 'config' in path or 'settings' in path:
        return 'CONFIG'

    # Models
    classes = json.loads(file.class_data)
    if classes and all(is_data_class(c) for c in classes):
        return 'MODEL'

    # Interfaces
    if file.stub_ratio > 0.8:
        return 'INTERFACE'

    # Services (high function count, low class count)
    if file.functions > 5 and file.classes <= 1:
        return 'SERVICE'

    return 'UNKNOWN'
```

### 9.7 Stage 3d: Trajectory Signals

```
STAGE_3D_TRAJECTORY_SIGNALS(snapshot_id):
    # Load historical snapshots
    history = db.query(
        "SELECT DISTINCT snapshot_id, timestamp FROM graph_snapshots ORDER BY timestamp"
    )

    if len(history) < 2:
        # No history, set defaults
        files = db.query("SELECT DISTINCT file_path FROM node_signals WHERE snapshot_id=?", snapshot_id)
        for file in files:
            store_trajectory_signal(snapshot_id, file.file_path, 'pagerank_velocity', 0.0)
            store_trajectory_signal(snapshot_id, file.file_path, 'pagerank_acceleration', 0.0)
            store_trajectory_signal(snapshot_id, file.file_path, 'community_stability', 1.0)
            store_trajectory_signal(snapshot_id, file.file_path, 'centrality_trend', 0.0)
        return

    # Get current and previous snapshots
    current = history[-1]
    previous = history[-2] if len(history) >= 2 else None
    older = history[-3] if len(history) >= 3 else None

    # Time deltas (in days)
    dt1 = (current.timestamp - previous.timestamp) / 86400 if previous else 1
    dt2 = (previous.timestamp - older.timestamp) / 86400 if older else 1

    files = db.query("SELECT DISTINCT file_path FROM node_signals WHERE snapshot_id=?", snapshot_id)

    for file in files:
        # PageRank velocity
        pr_current = get_signal(current.snapshot_id, file.file_path, 'pagerank_IMPORT')
        pr_previous = get_signal(previous.snapshot_id, file.file_path, 'pagerank_IMPORT') if previous else pr_current

        velocity = (pr_current - pr_previous) / dt1 if dt1 > 0 else 0
        store_trajectory_signal(snapshot_id, file.file_path, 'pagerank_velocity', velocity)

        # PageRank acceleration
        if older:
            pr_older = get_signal(older.snapshot_id, file.file_path, 'pagerank_IMPORT')
            velocity_prev = (pr_previous - pr_older) / dt2 if dt2 > 0 else 0
            acceleration = (velocity - velocity_prev) / dt1 if dt1 > 0 else 0
            store_trajectory_signal(snapshot_id, file.file_path, 'pagerank_acceleration', acceleration)
        else:
            store_trajectory_signal(snapshot_id, file.file_path, 'pagerank_acceleration', 0.0)

        # Community stability
        community_changes = 0
        observations = 0
        prev_comm = None
        for h in history:
            comm = get_signal(h.snapshot_id, file.file_path, 'community_IMPORT')
            if comm is not None:
                observations += 1
                if prev_comm is not None and comm != prev_comm:
                    community_changes += 1
                prev_comm = comm

        stability = 1.0 - (community_changes / max(observations - 1, 1)) if observations > 1 else 1.0
        store_trajectory_signal(snapshot_id, file.file_path, 'community_stability', stability)

        # Centrality trend (linear regression over all history)
        pr_values = []
        for h in history:
            pr = get_signal(h.snapshot_id, file.file_path, 'pagerank_IMPORT')
            if pr is not None:
                pr_values.append(pr)

        if len(pr_values) >= 2:
            trend = linear_regression_slope(pr_values)
            store_trajectory_signal(snapshot_id, file.file_path, 'centrality_trend', trend)
        else:
            store_trajectory_signal(snapshot_id, file.file_path, 'centrality_trend', 0.0)

    # Global trajectory signals
    # Graph velocity
    edges_current = set(db.query(
        "SELECT source_path || '→' || target_path FROM graph_edges WHERE snapshot_id=? AND relation_type='IMPORT'",
        current.snapshot_id
    ))
    edges_previous = set(db.query(
        "SELECT source_path || '→' || target_path FROM graph_edges WHERE snapshot_id=? AND relation_type='IMPORT'",
        previous.snapshot_id
    )) if previous else edges_current

    intersection = len(edges_current & edges_previous)
    union = len(edges_current | edges_previous)
    jaccard = intersection / union if union > 0 else 1.0
    graph_velocity = 1.0 - jaccard
    store_global_signal(snapshot_id, 'graph_velocity', graph_velocity)
    store_global_signal(snapshot_id, 'topology_stability', 1.0 / (1.0 + graph_velocity))

    # Fiedler trend
    fiedler_values = [get_global_signal(h.snapshot_id, 'fiedler_IMPORT') for h in history]
    fiedler_values = [f for f in fiedler_values if f is not None]
    if len(fiedler_values) >= 2:
        store_global_signal(snapshot_id, 'fiedler_trend', linear_regression_slope(fiedler_values))
    else:
        store_global_signal(snapshot_id, 'fiedler_trend', 0.0)

    # Modularity trend
    mod_values = [get_global_signal(h.snapshot_id, 'modularity_IMPORT') for h in history]
    mod_values = [m for m in mod_values if m is not None]
    if len(mod_values) >= 2:
        store_global_signal(snapshot_id, 'modularity_trend', linear_regression_slope(mod_values))
    else:
        store_global_signal(snapshot_id, 'modularity_trend', 0.0)
```

### 9.8 Stage 3e: Cross-Layer Signals

```
STAGE_3E_CROSS_LAYER_SIGNALS(snapshot_id):
    # Load graphs
    G_import = load_graph(snapshot_id, 'IMPORT')
    G_cochange = load_graph(snapshot_id, 'COCHANGE')
    G_author = load_graph(snapshot_id, 'AUTHOR')
    G_semantic = load_graph(snapshot_id, 'SEMANTIC')

    # 9.8.1 Per-file cross-layer signals
    for node in G_import.nodes:
        N_import = G_import.neighbors(node, 'both')
        N_cochange = G_cochange.neighbors(node, 'both')
        N_author = G_author.neighbors(node, 'both')

        # Hidden coupling count
        hidden = N_cochange - N_import
        store_cross_signal(snapshot_id, node, 'hidden_coupling_count', len(hidden))

        # Neighborhood coherence
        intersection = len(N_import & N_cochange)
        union = len(N_import | N_cochange)
        coherence = intersection / union if union > 0 else 1.0
        store_cross_signal(snapshot_id, node, 'neighborhood_coherence', coherence)

    # 9.8.2 Global cross-layer signals

    # Behavioral coherence: I(G_import; G_cochange)
    behavioral_coherence = compute_graph_mutual_information(G_import, G_cochange)
    store_global_signal(snapshot_id, 'behavioral_coherence', behavioral_coherence)

    # Conway alignment: I(G_import; G_author)
    conway_alignment = compute_graph_mutual_information(G_import, G_author)
    store_global_signal(snapshot_id, 'conway_alignment', conway_alignment)

    # Semantic alignment: I(G_import; G_semantic)
    semantic_alignment = compute_graph_mutual_information(G_import, G_semantic)
    store_global_signal(snapshot_id, 'semantic_alignment', semantic_alignment)

    # 9.8.3 Pair-level cross-layer signals (sparse, only significant)
    all_pairs = set()
    for e in G_import.edges():
        all_pairs.add((min(e[0], e[1]), max(e[0], e[1])))
    for e in G_cochange.edges():
        all_pairs.add((min(e[0], e[1]), max(e[0], e[1])))

    for a, b in all_pairs:
        has_import = (a, b) in G_import.edges() or (b, a) in G_import.edges()
        cochange_weight = G_cochange.weights.get((a, b), 0) + G_cochange.weights.get((b, a), 0)
        author_overlap = G_author.weights.get((a, b), 0) + G_author.weights.get((b, a), 0)
        semantic_sim = G_semantic.weights.get((a, b), 0) + G_semantic.weights.get((b, a), 0)

        # Hidden coupling
        hidden_coupling = cochange_weight * (1 if not has_import else 0)
        if hidden_coupling > 0:
            store_pair_signal(snapshot_id, a, b, 'hidden_coupling', hidden_coupling)

        # Conway violation
        conway_violation = (1 if has_import else 0) * (1 - author_overlap)
        if has_import and author_overlap < 0.2:
            store_pair_signal(snapshot_id, a, b, 'conway_violation', conway_violation)

        # Semantic mismatch
        semantic_mismatch = (1 if has_import else 0) * (1 - semantic_sim)
        if has_import and semantic_sim < 0.3:
            store_pair_signal(snapshot_id, a, b, 'semantic_mismatch', semantic_mismatch)

COMPUTE_GRAPH_MUTUAL_INFORMATION(G1, G2):
    """Compute mutual information between two graphs."""
    nodes = G1.nodes | G2.nodes
    n = len(nodes)
    if n < 2:
        return 0.0

    # Count edge co-occurrences
    node_list = sorted(nodes)
    n11 = n10 = n01 = n00 = 0

    for i, a in enumerate(node_list):
        for b in node_list[i+1:]:
            in_g1 = (a in G1.adjacency and b in G1.adjacency[a]) or \
                    (b in G1.adjacency and a in G1.adjacency[b])
            in_g2 = (a in G2.adjacency and b in G2.adjacency[a]) or \
                    (b in G2.adjacency and a in G2.adjacency[b])

            if in_g1 and in_g2:
                n11 += 1
            elif in_g1 and not in_g2:
                n10 += 1
            elif not in_g1 and in_g2:
                n01 += 1
            else:
                n00 += 1

    total = n11 + n10 + n01 + n00
    if total == 0:
        return 0.0

    # Compute MI
    mi = 0.0
    for nij, ni, nj in [
        (n11, n11 + n10, n11 + n01),
        (n10, n11 + n10, n10 + n00),
        (n01, n01 + n00, n11 + n01),
        (n00, n01 + n00, n10 + n00),
    ]:
        if nij > 0 and ni > 0 and nj > 0:
            pij = nij / total
            pi = ni / total
            pj = nj / total
            mi += pij * log2(pij / (pi * pj))

    # Normalize to [0, 1]
    h1 = entropy([n11 + n10, n01 + n00], total)
    h2 = entropy([n11 + n01, n10 + n00], total)
    max_mi = min(h1, h2)

    return mi / max_mi if max_mi > 0 else 0.0
```

### 9.9 Stage 3f: Composite Signals

```
STAGE_3F_COMPOSITE_SIGNALS(snapshot_id):
    files = db.query("SELECT DISTINCT file_path FROM node_signals WHERE snapshot_id=?", snapshot_id)

    # 9.9.1 Compute percentiles (skip for small codebases)
    file_count = len(files)
    tier = 'ABSOLUTE' if file_count < 15 else 'BAYESIAN' if file_count < 50 else 'FULL'

    if tier != 'ABSOLUTE':
        NORMALIZABLE = [
            'lines', 'function_count', 'complexity', 'max_nesting',
            'pagerank_IMPORT', 'betweenness_IMPORT', 'blast_radius_size',
            'total_changes', 'churn_cv', 'cognitive_load',
            'hidden_coupling_count',
        ]

        for signal in NORMALIZABLE:
            values = []
            for file in files:
                v = get_signal(snapshot_id, file.file_path, signal)
                if v is not None:
                    values.append((file.file_path, v))

            values.sort(key=lambda x: x[1])
            n = len(values)
            for rank, (path, _) in enumerate(values):
                pctl = (rank + 1) / n
                store_percentile(snapshot_id, path, signal, pctl)

    # 9.9.2 File composites
    for file in files:
        # Raw risk (pre-percentile, for Laplacian)
        pagerank = get_signal(snapshot_id, file.file_path, 'pagerank_IMPORT') or 0
        blast = get_signal(snapshot_id, file.file_path, 'blast_radius_size') or 0
        cognitive = get_signal(snapshot_id, file.file_path, 'cognitive_load') or 0
        churn_cv = get_signal(snapshot_id, file.file_path, 'churn_cv') or 0
        bus_factor = get_signal(snapshot_id, file.file_path, 'bus_factor') or 1

        # Normalize by max
        max_pr = db.query("SELECT MAX(value) FROM node_signals WHERE snapshot_id=? AND signal_name='pagerank_IMPORT'", snapshot_id).value or 1
        max_blast = db.query("SELECT MAX(value) FROM node_signals WHERE snapshot_id=? AND signal_name='blast_radius_size'", snapshot_id).value or 1
        max_cog = db.query("SELECT MAX(value) FROM node_signals WHERE snapshot_id=? AND signal_name='cognitive_load'", snapshot_id).value or 1

        raw_risk = (
            0.25 * (pagerank / max_pr) +
            0.20 * (blast / max_blast) +
            0.20 * (cognitive / max_cog) +
            0.20 * min(churn_cv / 2.0, 1.0) +
            0.15 * max(0, 1 - bus_factor / 5.0)
        )
        store_composite_signal(snapshot_id, file.file_path, 'raw_risk', raw_risk)

        # Risk score (percentile-based)
        if tier != 'ABSOLUTE':
            pctl_pr = get_percentile(snapshot_id, file.file_path, 'pagerank_IMPORT') or 0
            pctl_blast = get_percentile(snapshot_id, file.file_path, 'blast_radius_size') or 0
            pctl_cog = get_percentile(snapshot_id, file.file_path, 'cognitive_load') or 0
            pctl_hidden = get_percentile(snapshot_id, file.file_path, 'hidden_coupling_count') or 0
            community_stability = get_trajectory_signal(snapshot_id, file.file_path, 'community_stability') or 1.0
            pagerank_velocity = abs(get_trajectory_signal(snapshot_id, file.file_path, 'pagerank_velocity') or 0)

            # Normalize velocity to percentile
            all_velocities = [abs(get_trajectory_signal(snapshot_id, f.file_path, 'pagerank_velocity') or 0) for f in files]
            all_velocities.sort()
            vel_pctl = (all_velocities.index(pagerank_velocity) + 1) / len(all_velocities) if pagerank_velocity in all_velocities else 0

            risk_score = (
                0.15 * pctl_pr +
                0.10 * vel_pctl +
                0.15 * pctl_blast +
                0.15 * pctl_cog +
                0.15 * min(churn_cv / 2.0, 1.0) +
                0.15 * max(0, 1 - bus_factor / 5.0) +
                0.10 * pctl_hidden +
                0.05 * (1 - community_stability)
            )
        else:
            # Absolute tier: threshold-based
            thresholds = {
                'lines': 500, 'function_count': 30, 'max_nesting': 4,
                'complexity': 50, 'churn_cv': 1.0, 'fix_ratio': 0.4,
            }
            violations = sum(1 for k, v in thresholds.items()
                           if (get_signal(snapshot_id, file.file_path, k) or 0) > v)
            risk_score = violations / len(thresholds)

        store_composite_signal(snapshot_id, file.file_path, 'risk_score', min(1.0, max(0.0, risk_score)))

        # Wiring quality
        is_orphan = get_signal(snapshot_id, file.file_path, 'is_orphan') or 0
        stub_ratio = get_signal(snapshot_id, file.file_path, 'stub_ratio') or 0
        phantom_count = get_signal(snapshot_id, file.file_path, 'phantom_import_count') or 0
        import_count = get_signal(snapshot_id, file.file_path, 'import_count') or 1
        hidden_count = get_cross_signal(snapshot_id, file.file_path, 'hidden_coupling_count') or 0
        degree = (get_signal(snapshot_id, file.file_path, 'in_degree_IMPORT') or 0) + \
                 (get_signal(snapshot_id, file.file_path, 'out_degree_IMPORT') or 0)

        wiring_quality = 1.0 - (
            0.25 * is_orphan +
            0.25 * stub_ratio +
            0.25 * (phantom_count / max(import_count, 1)) +
            0.25 * (hidden_count / max(degree, 1))
        )
        store_composite_signal(snapshot_id, file.file_path, 'wiring_quality', max(0.0, wiring_quality))

        # File health score
        coherence = get_cross_signal(snapshot_id, file.file_path, 'neighborhood_coherence') or 1.0
        pctl_cog = get_percentile(snapshot_id, file.file_path, 'cognitive_load') or 0

        file_health = 1.0 - (
            0.25 * risk_score +
            0.20 * (1 - wiring_quality) +
            0.20 * pctl_cog +
            0.15 * is_orphan +
            0.20 * (1 - coherence)
        )
        store_composite_signal(snapshot_id, file.file_path, 'file_health_score', max(0.0, file_health))

    # 9.9.3 Health Laplacian (delta_h)
    G_import = load_graph(snapshot_id, 'IMPORT')

    for file in files:
        neighbors = G_import.neighbors(file.file_path, 'both')

        if not neighbors:
            delta_h = 0.0
        else:
            my_risk = get_composite_signal(snapshot_id, file.file_path, 'raw_risk') or 0
            neighbor_risks = [get_composite_signal(snapshot_id, n, 'raw_risk') or 0 for n in neighbors]
            mean_neighbor_risk = sum(neighbor_risks) / len(neighbor_risks)
            delta_h = my_risk - mean_neighbor_risk

        store_composite_signal(snapshot_id, file.file_path, 'delta_h', delta_h)

    # 9.9.4 Module composites
    modules = detect_modules(files)

    for module_path, module_files in modules.items():
        # Cohesion and coupling
        internal_edges = 0
        external_edges_out = 0
        external_edges_in = 0

        module_file_set = set(module_files)
        for f in module_files:
            for target in G_import.adjacency.get(f, []):
                if target in module_file_set:
                    internal_edges += 1
                else:
                    external_edges_out += 1
            for source in G_import.reverse.get(f, []):
                if source not in module_file_set:
                    external_edges_in += 1

        n = len(module_files)
        possible_internal = n * (n - 1) if n > 1 else 1
        cohesion = internal_edges / possible_internal

        total_edges = internal_edges + external_edges_out + external_edges_in
