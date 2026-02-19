# Level 0: Fact Extraction Architecture

## Overview

Level 0 is the **foundation layer** for Shannon Insight's data pipeline. It extracts raw, immutable facts from two primary sources:

1. **Disk facts**: File content, syntax structure (functions, classes, imports)
2. **Git history facts**: Commits, file changes, renames, authorship

These facts are:
- **Immutable**: Once extracted, never modified
- **Content-addressed**: Syntax facts indexed by SHA-256 content hash
- **Identity-stable**: File identity persists across renames
- **Session-tracked**: Every extraction is audit-traced

## Ontology

### Core Primitives (6 fundamental entities)

```
FILE_ID ────→ immutable identity across renames
     ├────→ PATH (changes across renames)
     ├────→ CONTENT_HASH (immutable)
     └────→ COMMIT_ID (point in time)

COMMIT_ID ──→ point in history
     ├────→ HASH (40-char SHA)
     ├────→ TIMESTAMP
     ├────→ AUTHOR_ID (stable identity)
     └────→ MESSAGE

AUTHOR_ID ──→ stable identity across email changes
     ├────→ EMAILS (canonical + aliases)
     └────→ AUTHOR_NAME

CONTENT_HASH → immutable: maps 1:1 to FileSyntax
     └────→ SYNTAX_TREE (functions, classes, imports)
```

---

## Primitive Facts (Observed & Immutable)

### 1. FileObservation

```python
@dataclass(frozen=True)
class FileObservation:
    """Immutable fact: a file state at a point in time."""
    file_id: str                    # Stable identity (UUID)
    path: str                       # Current path (may change via renames)
    commit_hash: str                # Point in git history
    timestamp: int                  # unix seconds
    content_hash: str               # SHA-256 of content
    file_size_bytes: int
    is_binary: bool
    session_id: str                 # Analysis session
```

### 2. CommitFact

```python
@dataclass(frozen=True)
class CommitFact:
    """Immutable fact: a commit in git history."""
    hash: str                       # 40-char SHA
    timestamp: int                  # unix seconds
    author_id: str                  # Canonical author identity
    author_name: str
    author_email: str               # Email at time of commit
    subject: str                    # First line of message
    body: str                       # Full commit message
    parent_hashes: tuple[str, ...]  # For merge detection
    session_id: str

    @property
    def is_merge(self) -> bool:
        return len(self.parent_hashes) > 1
```

### 3. FileChangeFact

```python
@dataclass(frozen=True)
class FileChangeFact:
    """Immutable fact: one file's change in one commit."""
    file_id: str                    # Stable identity
    commit_hash: str
    change_type: Literal['A', 'M', 'D', 'R', 'C']
    old_path: str | None            # For renames
    new_path: str
    additions: int | None           # None for binary
    deletions: int | None
    session_id: str

    @property
    def churn(self) -> int:
        if self.additions is None:
            return 0
        return self.additions + self.deletions
```

### 4. RenameFact

```python
@dataclass(frozen=True)
class RenameFact:
    """Immutable fact: a file was renamed."""
    file_id: str                    # Same before & after
    commit_hash: str
    old_path: str
    new_path: str
    similarity: float               # 0.0-1.0 from git diff -M
    session_id: str
```

---

## Derived Facts (Cached by Content Hash)

### ParsedSyntax

```python
@dataclass(frozen=True)
class ParsedSyntax:
    """Cached syntax for a content hash. Same content → same parse."""
    content_hash: str               # PRIMARY KEY
    language: str
    functions: list[FunctionFact]
    classes: list[ClassFact]
    imports: list[ImportFact]
    lines: int
    tokens: int
    complexity: float
    has_main_guard: bool
    stub_ratio: float
    impl_gini: float
    max_nesting: int
    parser_type: Literal['tree-sitter', 'regex']
    parser_version: str
    session_id: str
```

---

## Identity Resolution

### FileIdentityResolver

```python
class FileIdentityResolver:
    """Assign stable file_id values that survive renames."""

    def resolve_file_id(self, path: str, renames: dict[str, str]) -> str:
        """
        Algorithm:
        1. Trace back through rename chain to find original path
        2. Combine: hash(original_path + first_appearance_timestamp)
        3. Same original → same file_id forever

        Example:
            Path: auth/models.py
            History: config/auth.py → auth/core.py → auth/models.py
            Returns: hash(config/auth.py + 2020-01-15) = "f1c3a9e2..."
        """
```

### AuthorIdentityResolver

```python
class AuthorIdentityResolver:
    """Unify author identities across email aliases."""

    def resolve_author(self, email: str, name: str) -> str:
        """
        Strategy:
        1. Check .mailmap file (git standard)
        2. Check shannon-insight.toml author_aliases
        3. Use email as canonical_id if no mapping
        """
```

---

## Storage Schema (SQLite)

```sql
-- Extraction sessions (audit trail)
CREATE TABLE extraction_sessions (
    id TEXT PRIMARY KEY,
    repo_path TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    head_sha TEXT,
    status TEXT DEFAULT 'running'
);

-- Commits
CREATE TABLE commits (
    hash TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    author_id TEXT NOT NULL,
    author_email TEXT,
    subject TEXT NOT NULL,
    body TEXT,
    parent_hashes TEXT,  -- JSON array
    session_id TEXT REFERENCES extraction_sessions(id)
);

-- File observations (file state at commit)
CREATE TABLE file_observations (
    id INTEGER PRIMARY KEY,
    file_id TEXT NOT NULL,
    path TEXT NOT NULL,
    commit_hash TEXT REFERENCES commits(hash),
    content_hash TEXT NOT NULL,
    is_binary INTEGER DEFAULT 0,
    session_id TEXT REFERENCES extraction_sessions(id),
    UNIQUE(session_id, file_id, commit_hash)
);

-- File changes (churn per commit)
CREATE TABLE file_changes (
    id INTEGER PRIMARY KEY,
    file_id TEXT NOT NULL,
    commit_hash TEXT REFERENCES commits(hash),
    change_type TEXT NOT NULL,  -- A|M|D|R|C
    old_path TEXT,
    new_path TEXT NOT NULL,
    additions INTEGER,
    deletions INTEGER,
    session_id TEXT REFERENCES extraction_sessions(id)
);

-- Renames (identity bridges)
CREATE TABLE renames (
    id INTEGER PRIMARY KEY,
    file_id TEXT NOT NULL,
    commit_hash TEXT REFERENCES commits(hash),
    old_path TEXT NOT NULL,
    new_path TEXT NOT NULL,
    similarity REAL,
    session_id TEXT REFERENCES extraction_sessions(id)
);

-- Parsed syntax (content-addressed, deduped)
CREATE TABLE parsed_syntax (
    content_hash TEXT PRIMARY KEY,
    language TEXT NOT NULL,
    functions TEXT NOT NULL,  -- JSON
    classes TEXT NOT NULL,    -- JSON
    imports TEXT NOT NULL,    -- JSON
    lines INTEGER NOT NULL,
    complexity REAL NOT NULL,
    parser_type TEXT NOT NULL,
    session_id TEXT REFERENCES extraction_sessions(id)
);

-- Indexes
CREATE INDEX idx_commits_timestamp ON commits(timestamp);
CREATE INDEX idx_commits_author ON commits(author_id);
CREATE INDEX idx_file_obs_file_id ON file_observations(file_id);
CREATE INDEX idx_file_obs_content ON file_observations(content_hash);
CREATE INDEX idx_file_changes_file ON file_changes(file_id);
CREATE INDEX idx_renames_file ON renames(file_id);
```

---

## FactStore API

```python
class FactStore:
    """High-level API for storing and querying facts."""

    # Session management
    def start_session(self, repo_path: str, head_sha: str) -> str: ...
    def complete_session(self, session_id: str) -> None: ...

    # Commit storage
    def store_commits(self, session_id: str, commits: list[CommitFact]) -> None: ...
    def get_commit(self, hash: str) -> CommitFact | None: ...
    def get_commits_since(self, timestamp: int) -> list[CommitFact]: ...

    # File observations
    def store_file_observations(self, session_id: str, obs: list[FileObservation]) -> None: ...
    def get_file_at_commit(self, file_id: str, commit: str) -> FileObservation | None: ...
    def get_file_lineage(self, file_id: str) -> list[FileObservation]: ...

    # File changes
    def store_file_changes(self, session_id: str, changes: list[FileChangeFact]) -> None: ...
    def get_total_churn(self, file_id: str) -> int: ...

    # Renames
    def store_renames(self, session_id: str, renames: list[RenameFact]) -> None: ...
    def get_renames_for_file(self, file_id: str) -> list[RenameFact]: ...

    # Parsed syntax (content-addressed)
    def store_syntax(self, session_id: str, syntax: list[ParsedSyntax]) -> None: ...
    def get_syntax_by_hash(self, content_hash: str) -> ParsedSyntax | None: ...
```

---

## Key Design Decisions

| Decision | Pro | Con | Rationale |
|----------|-----|-----|-----------|
| Content-addressed syntax | Zero-copy dedup | Query by file_id needs join | ~80% syntax repeats |
| File ID from original path | Rename-invariant | Need reverse-map | Stability > current names |
| Session-tracked facts | Full audit trail | More storage | Compliance + debugging |
| Immutable facts | Simple reasoning | Can't fix errors | Correctness > flexibility |

---

## Integration Points

**Reads from:**
- Files on disk (content)
- Git repository (commits, changes)

**Writes to:**
- SQLite fact store

**Consumed by:**
- Level 1: Temporal Signals (reads commits, changes)
- Level 2: Graph Construction (reads parsed imports)
- All higher levels (read via FactStore API)
