# Phase 1: Complete File Parsing Data Model

## Current State Analysis

**Date:** 2026-02-18
**Status:** Gap analysis complete

---

## 1. Data We CAN Extract (Current FileSyntax)

### 1.1 File Metadata
| Field | Type | Example | Currently Stored? |
|-------|------|---------|-------------------|
| `path` | str | "insights/kernel.py" | ✅ Yes |
| `language` | str | "python" | ✅ Yes |
| `mtime` | float | 1771345006.71 | ✅ Yes |
| `has_main_guard` | bool | False | ✅ Yes |
| `_lines` | int | 520 | ✅ Yes |
| `_tokens` | int | 2413 | ✅ Yes |
| `_complexity` | float | 2.91 | ✅ Yes |

### 1.2 Function Data (FunctionDef)
| Field | Type | Example | Currently Stored? | Used in Graph? |
|-------|------|---------|-------------------|----------------|
| `name` | str | "run" | ✅ Yes | ❌ NO |
| `params` | list[str] | ["self", "max_findings"] | ✅ Yes | ❌ NO |
| `body_tokens` | int | 727 | ✅ Yes | ❌ NO |
| `signature_tokens` | int | 15 | ✅ Yes | ❌ NO |
| `nesting_depth` | int | 4 | ✅ Yes | ❌ NO |
| `start_line` | int | 86 | ✅ Yes | ❌ NO |
| `end_line` | int | 332 | ✅ Yes | ❌ NO |
| `call_targets` | list[str] | ["AnalysisStore", "logger"] | ✅ Yes (tree-sitter) | ❌ **NO - LOST** |
| `decorators` | list[str] | ["property", "staticmethod"] | ✅ Yes | ❌ NO |
| `is_stub` | bool | False | ✅ Computed | ❌ NO |
| `stub_score` | float | 0.0 | ✅ Computed | ❌ NO |

### 1.3 Class Data (ClassDef)
| Field | Type | Example | Currently Stored? | Used in Graph? |
|-------|------|---------|-------------------|----------------|
| `name` | str | "InsightKernel" | ✅ Yes | ❌ NO |
| `bases` | list[str] | ["Protocol", "ABC"] | ✅ Yes | ❌ **NO - LOST** |
| `methods` | list[FunctionDef] | [...] | ✅ Yes | ❌ NO |
| `fields` | list[str] | ["session", "analyzers"] | ✅ Yes | ❌ NO |
| `is_abstract` | bool | True | ✅ Yes | ❌ NO |

### 1.4 Import Data (ImportDecl)
| Field | Type | Example | Currently Stored? | Used in Graph? |
|-------|------|---------|-------------------|----------------|
| `source` | str | "..persistence.models" | ✅ Yes | ✅ Yes (only this!) |
| `names` | list[str] | ["TensorSnapshot", "Finding"] | ✅ Yes | ❌ **NO - LOST** |
| `resolved_path` | str\|None | "persistence/models.py" | ✅ Yes | ❌ **NO - LOST** |
| `is_phantom` | bool | True (if unresolved) | ✅ Computed | Partial |

---

## 2. Data Currently LOST in Pipeline

### 2.1 Lost in Graph Building
| Data | What it enables | Impact |
|------|-----------------|--------|
| `call_targets` | Function → Function call graph | Can't detect: which functions are hotspots, call depth, dead functions |
| `bases` | Class → Class inheritance | Can't detect: deep inheritance, diamond problems, interface compliance |
| `names` (imports) | Symbol-level dependencies | Can't detect: which specific symbols used, unused imports |
| `resolved_path` | Pre-computed resolution | Re-computing in graph builder, wasting work |
| `methods` | Class contains Method | Can't detect: god classes by method count, method coupling |
| `decorators` | Decorator patterns | Can't detect: over-decorated code, decorator chains |

### 2.2 Lost in Persistence
| Data | Currently in Snapshot? | Should be? |
|------|------------------------|------------|
| Full FileSyntax | ❌ NO (only aggregates) | ✅ YES |
| FunctionDef details | ❌ NO | ✅ YES |
| ClassDef details | ❌ NO | ✅ YES |
| ImportDecl details | ❌ NO | ✅ YES |
| call_targets | ❌ NO | ✅ YES |

---

## 3. Proposed Data Model for Storage

### 3.1 FileFact (what we store per file)

```python
@dataclass
class FileFact:
    """Complete parsed facts about a single file.

    This is the source of truth for Phase 1 data.
    Immutable once created for a given (path, commit_sha, mtime).
    """

    # Identity
    path: str                      # Relative path
    absolute_path: str             # For debugging
    commit_sha: str                # Git commit when parsed
    mtime: float                   # File modification time
    content_hash: str              # SHA-256 of content (for dedup)

    # Session metadata
    session_id: str                # Analysis session
    parsed_at: datetime            # When this was parsed
    parser_version: str            # "tree-sitter" or "regex"
    tool_version: str              # Shannon version

    # File metadata
    language: str
    lines: int
    tokens: int
    complexity: float
    has_main_guard: bool

    # Entities (full details, not summaries)
    functions: list[FunctionFact]
    classes: list[ClassFact]
    imports: list[ImportFact]

    # Computed aggregates (for quick queries)
    function_count: int
    class_count: int
    import_count: int
    max_nesting: int
    stub_ratio: float
    impl_gini: float


@dataclass
class FunctionFact:
    """Complete facts about a function."""

    # Identity
    name: str
    qualified_name: str            # "ClassName.method_name" or "function_name"
    file_path: str                 # Back-reference

    # Location
    start_line: int
    end_line: int

    # Signature
    params: list[str]
    signature_tokens: int
    decorators: list[str]

    # Body
    body_tokens: int
    nesting_depth: int

    # Relationships (THE KEY DATA)
    call_targets: list[str]        # What this function calls

    # Computed
    is_stub: bool
    stub_score: float


@dataclass
class ClassFact:
    """Complete facts about a class."""

    # Identity
    name: str
    file_path: str

    # Location
    start_line: int
    end_line: int

    # Relationships (THE KEY DATA)
    bases: list[str]               # Inheritance

    # Contents
    methods: list[str]             # Method names (details in FunctionFact)
    fields: list[str]

    # Computed
    is_abstract: bool
    method_count: int


@dataclass
class ImportFact:
    """Complete facts about an import."""

    # Identity
    file_path: str                 # Which file has this import

    # Import details
    source: str                    # "os.path" or "..models"
    names: list[str]               # ["join", "dirname"] from "from X import Y"
    is_relative: bool              # Starts with "."

    # Resolution (THE KEY DATA - don't recompute!)
    resolved_path: str | None      # Target file in codebase
    is_phantom: bool               # True if unresolved internal
    is_stdlib: bool                # True if stdlib/third-party
```

### 3.2 Storage Schema (SQLite)

```sql
-- Session tracking
CREATE TABLE analysis_sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    commit_sha TEXT,
    analyzed_path TEXT NOT NULL,
    tool_version TEXT NOT NULL,
    config_hash TEXT,
    status TEXT DEFAULT 'running'  -- running, completed, failed
);

-- File facts (one row per file per session)
CREATE TABLE file_facts (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES analysis_sessions(id),
    path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    language TEXT NOT NULL,
    lines INTEGER NOT NULL,
    tokens INTEGER NOT NULL,
    complexity REAL NOT NULL,
    has_main_guard INTEGER NOT NULL,
    function_count INTEGER NOT NULL,
    class_count INTEGER NOT NULL,
    import_count INTEGER NOT NULL,
    max_nesting INTEGER NOT NULL,
    stub_ratio REAL NOT NULL,
    impl_gini REAL NOT NULL,
    parsed_at TEXT NOT NULL,
    parser_version TEXT NOT NULL,

    UNIQUE(session_id, path)
);

-- Function facts (one row per function)
CREATE TABLE function_facts (
    id INTEGER PRIMARY KEY,
    file_fact_id INTEGER NOT NULL REFERENCES file_facts(id),
    name TEXT NOT NULL,
    qualified_name TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    params TEXT NOT NULL,          -- JSON array
    signature_tokens INTEGER NOT NULL,
    decorators TEXT NOT NULL,      -- JSON array
    body_tokens INTEGER NOT NULL,
    nesting_depth INTEGER NOT NULL,
    call_targets TEXT NOT NULL,    -- JSON array (THE KEY!)
    is_stub INTEGER NOT NULL,
    stub_score REAL NOT NULL
);

-- Class facts (one row per class)
CREATE TABLE class_facts (
    id INTEGER PRIMARY KEY,
    file_fact_id INTEGER NOT NULL REFERENCES file_facts(id),
    name TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    bases TEXT NOT NULL,           -- JSON array (THE KEY!)
    methods TEXT NOT NULL,         -- JSON array of method names
    fields TEXT NOT NULL,          -- JSON array
    is_abstract INTEGER NOT NULL
);

-- Import facts (one row per import)
CREATE TABLE import_facts (
    id INTEGER PRIMARY KEY,
    file_fact_id INTEGER NOT NULL REFERENCES file_facts(id),
    source TEXT NOT NULL,
    names TEXT NOT NULL,           -- JSON array (THE KEY!)
    is_relative INTEGER NOT NULL,
    resolved_path TEXT,            -- NULL if phantom/stdlib
    is_phantom INTEGER NOT NULL,
    is_stdlib INTEGER NOT NULL
);

-- Indexes for graph building
CREATE INDEX idx_function_calls ON function_facts(file_fact_id);
CREATE INDEX idx_class_bases ON class_facts(file_fact_id);
CREATE INDEX idx_imports ON import_facts(file_fact_id, resolved_path);
```

---

## 4. What Needs to Change

### 4.1 Phase 1: Scanning Changes

| Change | File | Description |
|--------|------|-------------|
| Add `content_hash` | `scanning/syntax.py` | SHA-256 of file content |
| Add `absolute_path` | `scanning/syntax.py` | For debugging |
| Add `qualified_name` | `scanning/syntax.py` | "Class.method" format |
| Mark stdlib imports | `scanning/syntax.py` | New `is_stdlib` field |
| Store start/end for classes | `treesitter_parser.py` | Currently missing |

### 4.2 Phase 1: Persistence Changes

| Change | File | Description |
|--------|------|-------------|
| Create `FactDatabase` | `persistence/facts.py` | New module for fact storage |
| Store FileFact | `persistence/facts.py` | Full syntax data to DB |
| Store FunctionFact | `persistence/facts.py` | All function details |
| Store ClassFact | `persistence/facts.py` | All class details |
| Store ImportFact | `persistence/facts.py` | All import details with resolution |
| Session tracking | `persistence/facts.py` | analysis_sessions table |

### 4.3 Phase 2: Graph Changes

| Change | File | Description |
|--------|------|-------------|
| Multi-node-type graph | `graph/models.py` | FILE, FUNCTION, CLASS nodes |
| Multi-edge-type graph | `graph/models.py` | IMPORT, CALL, INHERIT, CONTAINS edges |
| Use `call_targets` | `graph/builder.py` | Build CALL edges |
| Use `bases` | `graph/builder.py` | Build INHERIT edges |
| Use `names` | `graph/builder.py` | Track symbol-level deps |
| Read from FactDatabase | `graph/builder.py` | Don't re-parse, read stored facts |

---

## 5. New Graph Model

### 5.1 Node Types

```python
class NodeType(Enum):
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    # Future: MODULE, SYMBOL
```

### 5.2 Edge Types

```python
class EdgeType(Enum):
    IMPORTS = "imports"           # FILE -> FILE
    IMPORTS_SYMBOL = "imports_symbol"  # FILE -> SYMBOL (future)
    CALLS = "calls"               # FUNCTION -> FUNCTION
    INHERITS = "inherits"         # CLASS -> CLASS
    CONTAINS = "contains"         # FILE -> FUNCTION, FILE -> CLASS, CLASS -> METHOD
```

### 5.3 Multi-Graph Structure

```python
@dataclass
class CodeGraph:
    """Multi-type dependency graph."""

    # Nodes by type
    file_nodes: set[str]          # file paths
    function_nodes: set[str]      # "file:func_name" or "file:Class.method"
    class_nodes: set[str]         # "file:ClassName"

    # Edges by type
    import_edges: dict[str, list[str]]      # file -> [files]
    call_edges: dict[str, list[str]]        # func -> [funcs]
    inherit_edges: dict[str, list[str]]     # class -> [classes]
    contains_edges: dict[str, list[str]]    # file -> [funcs, classes]

    # Reverse indexes
    imported_by: dict[str, list[str]]
    called_by: dict[str, list[str]]
    inherited_by: dict[str, list[str]]
    contained_in: dict[str, str]
```

---

## 6. Verification Queries

After implementation, these queries should work:

```sql
-- Which functions call the most other functions?
SELECT f.qualified_name, json_array_length(f.call_targets) as call_count
FROM function_facts f
ORDER BY call_count DESC
LIMIT 10;

-- Which classes have deep inheritance?
SELECT c.name, json_array_length(c.bases) as base_count
FROM class_facts c
WHERE json_array_length(c.bases) > 2;

-- Which files import the most symbols?
SELECT ff.path, COUNT(*) as import_count,
       SUM(json_array_length(i.names)) as symbol_count
FROM file_facts ff
JOIN import_facts i ON i.file_fact_id = ff.id
GROUP BY ff.path
ORDER BY symbol_count DESC;

-- Dead functions (defined but never called)
SELECT f.qualified_name
FROM function_facts f
WHERE f.qualified_name NOT IN (
    SELECT json_each.value
    FROM function_facts f2, json_each(f2.call_targets)
);
```
