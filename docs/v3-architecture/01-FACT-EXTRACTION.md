# Level 0: Fact Extraction

## Overview

Level 0 is the foundation. It extracts primitive facts from two sources:
1. **Files on disk** - content, syntax, metrics
2. **Git repository** - commits, changes, authors

Key innovations:
- Content-addressable storage (blobs by hash)
- Stable file identity across renames (FileIdentityResolver)
- Author identity normalization
- Append-only fact log

## Data Models

### Primitive Facts (Observed)

```python
@dataclass(frozen=True)
class FileObservation:
    file_id: str              # UUID, survives renames
    path: str                 # current path
    content_hash: str         # SHA-256
    commit_hash: str          # when observed
    timestamp: int

@dataclass(frozen=True)
class CommitFact:
    commit_hash: str
    timestamp: int
    author_id: str
    author_email_raw: str
    author_name_raw: str
    message_subject: str
    message_body: str
    parent_hashes: list[str]
    is_merge: bool

@dataclass(frozen=True)
class FileChangeFact:
    commit_hash: str
    file_id: str
    change_type: Literal["A", "M", "D", "R"]
    old_path: str | None
    additions: int | None
    deletions: int | None
```

### Derived Facts (Computed)

```python
@dataclass(frozen=True)
class ParsedSyntax:
    content_hash: str         # key - pure function of content
    language: str
    lines: int
    functions: list[FunctionDef]
    classes: list[ClassDef]
    imports: list[ImportDecl]
    identifiers: frozenset[str]
    complexity: int
    max_nesting: int
    parser_type: str          # "tree-sitter" or "regex"
```

## File Identity Resolution

Files are identified by UUID, not path. Renames are tracked as events.

```python
class FileIdentityResolver:
    def process_change(self, commit_hash, timestamp, change):
        if change.type == "A":
            file_id = uuid4()
            self.canonical[change.path] = file_id
        elif change.type == "R":
            file_id = self.canonical.pop(change.old_path)
            self.canonical[change.new_path] = file_id
            self.renames.append((change.old_path, change.new_path, file_id))
        elif change.type == "D":
            self.canonical.pop(change.path, None)
        return self.canonical.get(change.path)
```

## Content-Addressable Caching

Parse results cached by content hash. Unchanged files skip re-parsing.

```python
def extract_syntax(path: str, store: FactStore) -> FileSyntax:
    content = read_file(path)
    hash = sha256(content)

    cached = store.get_parsed_syntax(hash)
    if cached:
        return cached.to_file_syntax(path)

    syntax = parse(content)
    store.store_parsed_syntax(hash, syntax)
    return syntax
```

## SQL Schema

```sql
CREATE TABLE blobs (
    content_hash TEXT PRIMARY KEY,
    content BLOB NOT NULL,
    size_bytes INTEGER NOT NULL,
    compressed_size INTEGER
);

CREATE TABLE file_identities (
    file_id TEXT PRIMARY KEY,
    birth_commit TEXT NOT NULL,
    birth_path TEXT NOT NULL,
    current_path TEXT,
    is_alive INTEGER DEFAULT 1
);

CREATE TABLE file_renames (
    file_id TEXT NOT NULL,
    commit_hash TEXT NOT NULL,
    old_path TEXT NOT NULL,
    new_path TEXT NOT NULL,
    timestamp INTEGER NOT NULL
);

CREATE TABLE commits (
    commit_hash TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    author_id TEXT NOT NULL,
    author_email_raw TEXT NOT NULL,
    message_subject TEXT
);

CREATE TABLE file_changes (
    commit_hash TEXT NOT NULL,
    file_id TEXT NOT NULL,
    change_type TEXT NOT NULL,
    additions INTEGER,
    deletions INTEGER
);

CREATE TABLE parsed_syntax (
    content_hash TEXT PRIMARY KEY,
    language TEXT NOT NULL,
    lines INTEGER NOT NULL,
    complexity INTEGER,
    parser_type TEXT NOT NULL
);
```

## Current Implementation

**Files:**
- `src/shannon_insight/scanning/syntax.py` - FileSyntax model
- `src/shannon_insight/scanning/normalizer.py` - TreeSitterNormalizer
- `src/shannon_insight/temporal/git_raw_extractor.py` - Git extraction
- `src/shannon_insight/persistence/facts.py` - FactDatabase
- `src/shannon_insight/persistence/git_facts.py` - GitFactDatabase

**Status:** ~85% complete. Missing unified FactStore API.

## Dependencies

- **Requires:** Files on disk, Git repository
- **Produces:** Facts for all other levels
