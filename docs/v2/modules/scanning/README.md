# Module: scanning/

The scanning module is the pipeline root. It reads source files from disk, parses them into structured syntax representations, and produces the IR0 (FileEntry) and IR1 (FileSyntax) intermediate representations. Every downstream module depends on scanning/ output; scanning/ depends on nothing. In v2, scanning/ replaces its regex-based extraction engine with tree-sitter for accurate, language-aware AST parsing while preserving the same output contract.

---

## Contract Summary

| | |
|---|---|
| **Exports** | `ScannerFactory`, `UniversalScanner`, `FileEntry`, `FileSyntax`, `FunctionDef`, `ClassDef`, `ImportDecl`, `SyntaxDelta` |
| **Requires** | Nothing (pipeline root) |
| **Feeds** | semantics/ (FileSyntax for role classification, concept extraction), graph/ (ImportDecl for edges, FunctionDef.calls for CALL edges, ClassDef.bases for inheritance edges) |
| **Computes signals** | #1 `lines`, #2 `function_count`, #3 `class_count`, #4 `max_nesting`, #5 `impl_gini`, #6 `stub_ratio`, #7 `import_count` (see `registry/signals.md`) |

---

## Signals Computed

All seven signals are per-file (Scale S4), from IR1 (Syntactic). Formulas are defined in `registry/signals.md`. This module computes them as follows:

| # | Signal | How computed | Dimension |
|---|--------|-------------|-----------|
| 1 | `lines` | `len(content.splitlines())` on raw file content | D1 SIZE |
| 2 | `function_count` | `len(file_syntax.functions)` | D1 SIZE |
| 3 | `class_count` | `len(file_syntax.classes)` | D1 SIZE |
| 4 | `max_nesting` | `max(f.nesting_depth for f in file_syntax.functions)`, computed from AST tree depth within each function body; see `tree-sitter.md` | D2 SHAPE |
| 5 | `impl_gini` | Gini coefficient over `[f.body_tokens for f in file_syntax.functions]`; see `stub-detection.md` | D2 SHAPE |
| 6 | `stub_ratio` | `mean(stub_score(f) for f in functions)` with hard classification fallback; see `stub-detection.md` | D2 SHAPE |
| 7 | `import_count` | `len(file_syntax.imports)` | D4 REFERENCE |

---

## Current State vs v2 Changes

### EXISTS TODAY (v1)

- `ScannerFactory` auto-detects languages from file extensions, creates `ConfigurableScanner` instances.
- `ConfigurableScanner` uses regex patterns (`LanguageConfig`) to count functions, extract imports/exports, estimate complexity, and measure nesting depth.
- Output model is `FileMetrics` -- a flat dataclass with `lines`, `tokens`, `imports` (list of strings), `exports`, `functions` (int count), `function_sizes` (list of int line counts), `nesting_depth`, `complexity_score`.
- Supports 8 languages (Python, Go, TypeScript/JS, Java, Rust, Ruby, C/C++) plus a universal fallback.
- Regex-based: no per-function detail, no call extraction, no class field extraction, no per-function nesting, no body source capture.

### NEW IN v2

- **tree-sitter replaces regex** for all 8 languages. The universal fallback retains regex for unsupported languages. See `tree-sitter.md`.
- **Output model changes**: `FileMetrics` is replaced by `FileEntry` (IR0) + `FileSyntax` (IR1). See `models.md`.
- **Per-function detail**: `FunctionDef` captures name, params, return type, body source, body token count, signature token count, start/end lines, call targets, nesting depth, decorators.
- **Class detail**: `ClassDef` captures name, bases, methods, fields, `is_abstract`.
- **Import detail**: `ImportDecl` captures source, names, `is_relative`, `resolved_path`, `is_external`. See `import-resolution.md`.
- **Stub detection**: `stub_ratio` and `impl_gini` computed from per-function body/signature token counts. See `stub-detection.md`.
- **SyntaxDelta**: Structured diff for temporal analysis -- functions/imports added, removed, modified.
- **Backward compatibility**: A thin `FileMetrics` adapter is provided that converts `FileSyntax` to the v1 `FileMetrics` shape, so existing tests and downstream consumers continue to work during migration.

---

## Temporal Contract

### Output at time t

```
FileEntry(f, t)    -- the file's existence and metadata at commit/snapshot t
FileSyntax(f, t)   -- the parsed syntax of file f at time t
```

### Delta(t1, t2)

```
SyntaxDelta:
  functions_added:    [FunctionDef]
  functions_removed:  [FunctionDef]
  functions_modified: [(FunctionDef_old, FunctionDef_new)]
  imports_added:      [ImportDecl]
  imports_removed:    [ImportDecl]
```

Function matching across versions: match by name (exact), then by signature similarity for renames:
```
match(f1, f2) = (f1.name == f2.name) OR
                (jaccard(f1.params, f2.params) > 0.8 AND levenshtein(f1.name, f2.name) < 3)
```

### Time series

| Metric | How derived | Reveals |
|--------|------------|---------|
| function_count(t) | `len(functions)` per snapshot | Scope creep vs decomposition |
| stub_ratio(t) | Per-snapshot stub computation | Are stubs being filled in over time? |
| import_count(t) | `len(imports)` per snapshot | Dependency growth |
| impl_gini(t) | Per-snapshot Gini computation | Is implementation becoming more even? |

### Reconstruction

To produce scanning/ output at a historical commit:
```
git show <sha>:<path> | tree-sitter parse → FileSyntax
```
This is Kind 3 temporal data (see `registry/temporal-operators.md`). Requires re-parsing every file at the target commit.

---

## Error Handling Contract

| Condition | Behavior | Output |
|-----------|----------|--------|
| File cannot be read (permissions, encoding) | Log warning, skip file | No FileEntry emitted |
| File too large (> `max_file_size_bytes`) | Log debug, skip file | No FileEntry emitted |
| tree-sitter parse fails | Degrade to regex fallback, set `parse_mode = REGEX` flag on FileSyntax | Partial FileSyntax with reduced detail |
| tree-sitter parse partially fails (error nodes in AST) | Extract what is parseable, flag `has_errors = True` | FileSyntax with best-effort data |
| Binary file detected | Skip silently | No FileEntry emitted |
| Empty file | Emit FileEntry with `size = 0` | FileSyntax with empty lists |
| Unsupported language (no tree-sitter grammar) | Use universal regex scanner | FileSyntax with `parse_mode = REGEX` |

Errors never propagate as exceptions to callers. The scanning/ module returns a list of successfully parsed files. Callers check list length and `parse_mode` flags to assess coverage.

---

## Internal File Organization

```
scanning/
  __init__.py              # Public API: ScannerFactory, UniversalScanner, model re-exports
  models.py                # FileEntry, FileSyntax, FunctionDef, ClassDef, ImportDecl, SyntaxDelta
  factory.py               # ScannerFactory: language detection, scanner instantiation
  parser.py                # NEW: TreeSitterParser — wraps tree-sitter, one instance per language
  queries/                 # NEW: Per-language .py query modules
    python.py              #   tree-sitter query strings + capture normalization
    go.py
    typescript.py
    java.py
    rust.py
    ruby.py
    c.py
  normalizer.py            # NEW: Converts tree-sitter captures → FileSyntax (language-agnostic)
  imports.py               # NEW: Import resolution algorithm (relative → absolute → external)
  stubs.py                 # NEW: Stub detection (stub_score, impl_gini computation)
  scanner.py               # ConfigurableScanner (LEGACY: retained for universal/regex fallback)
  languages.py             # LanguageConfig regex definitions (LEGACY: retained for fallback)
  base.py                  # BaseScanner ABC (LEGACY: retained for backward compat)
```

### Migration path

1. `parser.py` + `queries/` + `normalizer.py` are pure additions.
2. `factory.py` is updated to prefer tree-sitter, falling back to `ConfigurableScanner` when no grammar exists.
3. `models.py` replaces `FileMetrics` with the new model hierarchy. A `to_file_metrics()` adapter method is provided.
4. `scanner.py`, `languages.py`, `base.py` are retained but marked as legacy. They serve the universal fallback and backward compatibility.
