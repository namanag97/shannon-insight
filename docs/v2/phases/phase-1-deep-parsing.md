# Phase 1: Deep Parsing with tree-sitter

## Goal

Replace regex-based scanning with tree-sitter AST parsing to produce `FileSyntax` with per-function bodies, call sites, nesting depth, and decorators across all 8 supported languages.

## Packages Touched

- `scanning/` -- **major rewrite**: new tree-sitter parser, per-language query files, normalizer
- `pyproject.toml` -- add `tree-sitter` and `tree-sitter-languages` dependencies

## Prerequisites

- Phase 0 complete (baseline documented, all existing tests passing)

## Changes

### New Files

| File | Purpose |
|---|---|
| `scanning/treesitter_parser.py` | Core tree-sitter wrapper: load grammar, run queries, return raw captures |
| `scanning/queries/python.py` | Python S-expression queries for functions, classes, calls, imports |
| `scanning/queries/go.py` | Go queries |
| `scanning/queries/typescript.py` | TypeScript queries (shared with JavaScript where applicable) |
| `scanning/queries/javascript.py` | JavaScript queries |
| `scanning/queries/java.py` | Java queries |
| `scanning/queries/rust.py` | Rust queries |
| `scanning/queries/ruby.py` | Ruby queries |
| `scanning/queries/c_cpp.py` | C/C++ queries |
| `scanning/queries/__init__.py` | Query registry: language -> query module mapping |
| `scanning/normalizer.py` | Convert raw tree-sitter captures into language-agnostic `FileSyntax` |
| `tests/test_treesitter_parsing.py` | Tests for tree-sitter extraction across all 8 languages |
| `tests/fixtures/` | Sample files for each language (small, focused test fixtures) |

### Modified Files

| File | Change |
|---|---|
| `scanning/models.py` | Add `FileSyntax`, `FunctionDef`, `ClassDef`, `ImportDecl` data models (or expand existing `FileMetrics`) |
| `scanning/factory.py` | Route to tree-sitter parser instead of regex scanners |
| `scanning/scanner.py` | Adapt `UniversalScanner` to use tree-sitter pipeline |
| `scanning/languages.py` | Retain for language detection; parsing logic moves to tree-sitter |
| `scanning/base.py` | Update `Scanner` protocol to return `FileSyntax` |
| `pyproject.toml` | Add optional dependency group: `[project.optional-dependencies] parsing = ["tree-sitter>=0.23", "tree-sitter-python>=0.23", "tree-sitter-go>=0.23", "tree-sitter-typescript>=0.23", "tree-sitter-javascript>=0.23", "tree-sitter-java>=0.23", "tree-sitter-rust>=0.23", "tree-sitter-ruby>=0.23", "tree-sitter-c>=0.23", "tree-sitter-cpp>=0.23"]`. Install via `pip install shannon-codebase-insight[parsing]`. |

### Data Model: FileSyntax

```python
@dataclass
class FunctionDef:
    name: str
    params: list[str]
    body_tokens: int
    signature_tokens: int
    call_targets: list[str] | None = None  # Unresolved syntactic targets. None if regex-parsed.
    nesting_depth: int        # NEW: accurate from AST
    start_line: int
    end_line: int
    decorators: list[str]     # NEW: @app.route, @abstractmethod, etc.

@dataclass
class ClassDef:
    name: str
    bases: list[str]
    methods: list[FunctionDef]
    fields: list[str]
    is_abstract: bool         # NEW: has ABC/Protocol/abstractmethod

@dataclass
class ImportDecl:
    source: str
    names: list[str]
    resolved_path: str | None  # None = phantom

@dataclass
class FileSyntax:
    path: str
    functions: list[FunctionDef]
    classes: list[ClassDef]
    imports: list[ImportDecl]
    language: str
    has_main_guard: bool = False  # True if `if __name__ == "__main__":` or equivalent detected
```

**`has_main_guard` detection**:
- **tree-sitter**: Query for `if_statement` containing `__name__` and `"__main__"` comparisons
- **regex fallback**: Simple text search for `if __name__` in raw content during scanning
- **Non-Python**: `False` (language-specific entry point patterns handled by role classification instead)

### Store Slot: `file_syntax`

Phase 1 adds a new slot to `AnalysisStore`:

```python
@dataclass
class AnalysisStore:
    # ... existing ...

    # Phase 1 addition:
    file_syntax: Optional[Dict[str, FileSyntax]] = None  # path -> FileSyntax
```

The scanner writes `store.file_syntax` after parsing all files. Downstream consumers:
- **SemanticAnalyzer** (Phase 2): reads functions, classes, decorators for role classification
- **ArchitectureAnalyzer** (Phase 4): reads classes with `is_abstract` for abstractness
- **SignalFusion** (Phase 5): reads functions for `impl_gini`, `stub_ratio` recomputation
- **Clone detection** (Phase 3): reads identifiers for MinHash shingles

### Fallback Strategy

tree-sitter is optional. The scanning pipeline:

1. Check if tree-sitter grammar is installed for the detected language
2. If YES: parse with tree-sitter → FileSyntax (full: call_targets, decorators populated)
3. If parse FAILS (encoding error, syntax error): fall back to regex → FileSyntax (basic: call_targets=None)
4. If NO grammar installed: regex scanner → FileSyntax (basic)

Both paths produce FileSyntax. Downstream code checks `if fn.call_targets is not None` to handle the difference.

Track fallback rate: log how many files used regex fallback. If > 20%, warn the user.

## New Signals Available After This Phase

More accurate versions of existing signals (same IDs, better data):

| # | Signal | Improvement |
|---|--------|-------------|
| 1-3 | `lines`, `function_count`, `class_count` | Accurate AST-based counts |
| 4 | `max_nesting` | Real AST depth, not regex approximation |
| 5 | `impl_gini` | Per-function `body_tokens` from AST |
| 6 | `stub_ratio` | Precise stub detection using body AST |
| 7 | `import_count` | All import forms captured |

New raw data (not yet signals, but available for downstream phases):

- Per-function `calls[]` -- syntactic call targets (feeds Phase 3 CALL edges)
- Per-function `decorators[]` -- feeds Phase 2 role classification
- Per-class `is_abstract` -- feeds Phase 4 abstractness

## New Finders Available After This Phase

No new finders. Existing finders benefit from improved accuracy.

## New Temporal Capabilities

None directly. But `FileSyntax` enables future `SyntaxDelta` (functions added/removed/modified between commits).

## Acceptance Criteria

1. All 8 languages parse without errors on representative test files (1 fixture per language)
2. Python function extraction matches manual count on `test_codebase/` files
3. `calls[]` populated for Python functions (syntactic targets)
4. `nesting_depth` matches hand-counted values for nested test cases
5. `decorators[]` captures `@abstractmethod`, `@property`, `@app.route` patterns
6. All 247 existing tests pass (backward compatibility)
7. New tests cover: function extraction, class extraction, import extraction, nesting depth, stub detection per language
8. Performance: parsing 500 files completes in under 2 seconds
9. Regex fallback activates for files with encoding errors (test with a Latin-1 encoded fixture)

## Estimated Scope

- ~15 new files (parser, 8 query modules, normalizer, tests, fixtures)
- ~6 modified files
- ~2-3 weeks of implementation
