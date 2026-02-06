# scanning/ Data Models

The data models produced by scanning/. These define IR0 (FileEntry) and IR1 (FileSyntax) -- the foundational representations that every downstream module consumes.

---

## IR0: FileEntry

**Purpose**: What exists on disk. Raw file metadata without parsing.

```python
@dataclass
class FileEntry:
    path: str                   # relative to project root, forward-slash normalized
    content: bytes              # raw file bytes (not stored in persistence — read on demand)
    size: int                   # len(content)
    hash: str                   # SHA-256 hex digest of content (for change detection)
    language: Language           # detected language enum
    mtime: float                # last-modified timestamp (epoch seconds)
```

| Field | Source | Cost | Notes |
|-------|--------|------|-------|
| path | filesystem walk | O(n) | Always relative; normalized to forward slashes on Windows |
| content | `open(path, 'rb').read()` | O(n), I/O bound | Held in memory during parsing, then released |
| size | `len(content)` | trivial | Byte count, not line count |
| hash | `hashlib.sha256(content).hexdigest()` | O(n), CPU cheap | Used for cross-snapshot change detection and rename detection |
| language | Extension lookup + header heuristic | O(1) | Falls back to UNKNOWN for unrecognized extensions |
| mtime | `os.stat(path).st_mtime` | O(1) | Used only for display; hash is the authoritative change signal |

### Language Enum

```python
class Language(str, Enum):
    PYTHON = "python"
    GO = "go"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    RUST = "rust"
    RUBY = "ruby"
    C = "c"
    CPP = "cpp"
    UNKNOWN = "unknown"
```

### What exists today vs what's new

- **EXISTS TODAY**: `FileMetrics.path`, `FileMetrics.lines`, `FileMetrics.last_modified` capture some of this. No `hash`, no `content` bytes, no explicit `Language` enum.
- **NEW IN v2**: `FileEntry` is a separate model from syntax. The `hash` field enables efficient change detection without content diffing. The `content` field is transient (not persisted).

---

## IR1: FileSyntax

**Purpose**: The structural content of a file -- functions, classes, imports -- with enough per-function detail for stub detection, signal computation, and downstream semantic/graph analysis.

```python
@dataclass
class FileSyntax:
    path: str                     # same as FileEntry.path
    language: Language            # same as FileEntry.language
    parse_mode: ParseMode         # TREE_SITTER | REGEX (how this was parsed)
    has_errors: bool              # True if tree-sitter encountered error nodes
    lines: int                    # line count
    functions: list[FunctionDef]
    classes: list[ClassDef]
    imports: list[ImportDecl]
    top_level_statements: int     # non-function, non-class, non-import statement count
```

### ParseMode

```python
class ParseMode(str, Enum):
    TREE_SITTER = "tree_sitter"   # Full AST parse
    REGEX = "regex"               # Fallback: regex-based extraction (reduced detail)
```

When `parse_mode = REGEX`, downstream consumers know that `FunctionDef.calls`, `FunctionDef.body_source`, `ClassDef.fields`, and per-function `nesting_depth` may be absent or approximate.

### What exists today vs what's new

- **EXISTS TODAY**: `FileMetrics` has `lines`, `functions` (int count only), `imports` (list of raw strings), `function_sizes` (list of line counts). No per-function detail, no class detail, no parse mode flag.
- **NEW IN v2**: Per-function `FunctionDef` objects, per-class `ClassDef` objects, structured `ImportDecl` objects. `parse_mode` and `has_errors` flags for quality tracking.

---

## FunctionDef

**Purpose**: One function or method definition with enough detail for stub detection, call graph construction, and complexity measurement.

```python
@dataclass
class FunctionDef:
    name: str                       # function/method name
    params: list[str]               # parameter names (with type annotations if available)
    return_type: str | None         # return type annotation if present
    body_source: str                # raw source text of function body
    body_tokens: int                # token count in body (post-comment/string stripping)
    signature_tokens: int           # token count in the signature line
    start_line: int                 # 1-indexed
    end_line: int                   # 1-indexed, inclusive
    calls: list[str]                # syntactic call targets: ["db.query", "Token.create"]
    nesting_depth: int              # max nesting depth within this function's body
    decorators: list[str]           # decorator/annotation strings: ["staticmethod", "app.route(\"/login\")"]
    is_method: bool                 # True if defined inside a class body
    class_name: str | None          # enclosing class name, if is_method
```

| Field | Source | Notes |
|-------|--------|-------|
| name | tree-sitter `identifier` capture in function_definition node | |
| params | tree-sitter `parameters` capture, split into individual names | Type annotations preserved as `name: type` strings when available |
| return_type | tree-sitter return type annotation capture | None for languages/functions without type annotations |
| body_source | tree-sitter `body` capture, raw text | Used for stub detection, compression ratio |
| body_tokens | Tokenize `body_source`: strip comments/strings, count `\w+` and operators | Key input for stub_score and impl_gini |
| signature_tokens | Tokenize the signature line (everything before body) | Used in stub_score denominator |
| start_line, end_line | tree-sitter node start/end positions | 1-indexed to match editor conventions |
| calls | tree-sitter `call_expression` captures within body | Syntactic only: `foo()` -> `"foo"`, `obj.method()` -> `"obj.method"` |
| nesting_depth | Max tree depth from function body root to any descendant block/compound statement | Counts `if/for/while/match/try` nesting, not brace nesting |
| decorators | tree-sitter `decorator` captures above function node | Full decorator text including arguments |
| is_method | True if parent node is a class body | |
| class_name | Name of enclosing class | None for top-level functions |

### What exists today vs what's new

- **EXISTS TODAY**: `FileMetrics.function_sizes` gives a list of line counts per function, but no names, no params, no body access, no call extraction. Function count is an integer.
- **NEW IN v2**: Full `FunctionDef` objects with all fields above. This is the biggest data model expansion in v2.

---

## ClassDef

**Purpose**: One class definition with enough detail for role classification, abstractness computation, and inheritance graph construction.

```python
@dataclass
class ClassDef:
    name: str                       # class name
    bases: list[str]                # parent class names: ["ABC", "BaseModel"]
    methods: list[FunctionDef]      # method definitions (references to FunctionDef objects)
    fields: list[str]               # instance attributes from __init__ or class-level annotations
    decorators: list[str]           # class-level decorators
    is_abstract: bool               # has ABC/Protocol base, or all methods are abstract/stub
    start_line: int                 # 1-indexed
    end_line: int                   # 1-indexed, inclusive
```

| Field | Source | Notes |
|-------|--------|-------|
| name | tree-sitter `identifier` capture in class_definition node | |
| bases | tree-sitter `argument_list` / `superclass` captures | Raw names, not resolved to files |
| methods | Nested FunctionDef objects from tree-sitter method captures | Includes `__init__`, `__str__`, etc. |
| fields | Python: `self.x` assignments in `__init__` + class-level type annotations. Java/TS: field declarations. Go: struct fields. | Identifier names only, not types |
| decorators | tree-sitter `decorator` captures above class node | |
| is_abstract | `"ABC" in bases or "Protocol" in bases or has @abstractmethod methods` | Expanded check in architecture/ for never-instantiated heuristic |
| start_line, end_line | tree-sitter node positions | |

### What exists today vs what's new

- **EXISTS TODAY**: `FileMetrics.structs` and `FileMetrics.interfaces` are integer counts from regex matching. No class names, no bases, no fields, no method association.
- **NEW IN v2**: Full `ClassDef` objects. Methods are linked back to their `FunctionDef` objects. `is_abstract` enables architecture/ abstractness computation.

---

## ImportDecl

**Purpose**: One import declaration with resolution status. The key input for graph/ edge construction.

```python
@dataclass
class ImportDecl:
    source: str                     # raw import path: "..models", "bcrypt", "os.path"
    names: list[str]                # imported names: ["User", "Token"] or ["*"]
    is_relative: bool               # True for relative imports (Python "..", Go "./")
    resolved_path: str | None       # resolved to a project file path, or None
    is_external: bool               # True if package is not in the project tree
    start_line: int                 # 1-indexed
```

| Field | Source | Notes |
|-------|--------|-------|
| source | tree-sitter import statement capture | The module/package path as written |
| names | tree-sitter imported name captures | `["*"]` for wildcard imports |
| is_relative | Detected from leading dots (Python), `./` prefix (Go/TS), or `require_relative` (Ruby) | |
| resolved_path | Import resolution algorithm output; see `import-resolution.md` | None = unresolved (phantom candidate) |
| is_external | `resolved_path is None AND source matches known external package` | Standard library and installed packages are external |
| start_line | tree-sitter node position | |

### What exists today vs what's new

- **EXISTS TODAY**: `FileMetrics.imports` is a `list[str]` of raw import path strings. No resolution, no `is_relative`, no `is_external`, no imported names.
- **NEW IN v2**: Structured `ImportDecl` with resolution status. `resolved_path = None` feeds phantom import detection in graph/.

---

## SyntaxDelta

**Purpose**: Structured diff between two `FileSyntax` snapshots of the same file. Used for temporal analysis and cross-snapshot tracking.

```python
@dataclass
class SyntaxDelta:
    path: str
    functions_added: list[FunctionDef]
    functions_removed: list[FunctionDef]
    functions_modified: list[tuple[FunctionDef, FunctionDef]]  # (old, new)
    imports_added: list[ImportDecl]
    imports_removed: list[ImportDecl]
    classes_added: list[ClassDef]
    classes_removed: list[ClassDef]
    line_delta: int                 # lines(t2) - lines(t1)
    stub_ratio_delta: float         # stub_ratio(t2) - stub_ratio(t1)
```

### Function matching algorithm

Functions are matched between `FileSyntax(t1)` and `FileSyntax(t2)` for the same file:

1. **Exact name match**: `f1.name == f2.name` (handles ~95% of cases)
2. **Rename detection**: For unmatched functions, check `jaccard(f1.params, f2.params) > 0.8 AND levenshtein(f1.name, f2.name) < 3`
3. **Remaining unmatched in t1**: `functions_removed`
4. **Remaining unmatched in t2**: `functions_added`
5. **Matched pairs where `f1.body_source != f2.body_source`**: `functions_modified`

### What exists today vs what's new

- **NEW IN v2**: `SyntaxDelta` does not exist today. The current system stores `FileMetrics` snapshots and diffs only at the signal level (numeric deltas). v2 adds structured syntax-level diffing.

---

## Summary of Model Hierarchy

```
FileEntry (IR0)         -- existence + raw metadata
  |
  v
FileSyntax (IR1)        -- parsed structure
  ├── FunctionDef[]     -- per-function detail
  ├── ClassDef[]        -- per-class detail (contains FunctionDef[] for methods)
  └── ImportDecl[]      -- per-import detail with resolution status

SyntaxDelta             -- diff between two FileSyntax at different times
```

All models are immutable dataclasses. They carry no behavior beyond property accessors. Signal computation (`stub_ratio`, `impl_gini`, etc.) lives in `scanning/stubs.py`, not in the models.
