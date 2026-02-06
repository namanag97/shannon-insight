# scanning/ Tree-Sitter Parsing Architecture

v2 replaces the regex-based `ConfigurableScanner` with tree-sitter for all 8 supported languages. This document specifies the parsing architecture, per-language query approach, error handling, and performance targets.

---

## Why tree-sitter

The v1 scanner uses regex patterns (`LanguageConfig` in `languages.py`) to count functions, extract imports, and estimate complexity. This approach cannot:

- Extract per-function body source text
- Identify call targets within function bodies
- Distinguish methods from top-level functions
- Extract class fields and inheritance
- Compute per-function nesting depth accurately
- Handle nested/multiline constructs reliably

tree-sitter is the standard solution. It is used by GitHub (Semantic/CodeQL), Sourcegraph, Neovim, and Helix. It provides error-tolerant, incremental parsing with pre-built grammars for all target languages.

### Dependencies

```
tree-sitter >= 0.25.2
tree-sitter-languages       # 165+ pre-built grammars, no compilation needed
```

---

## Architecture

```
FileEntry.content (bytes)
       |
  [ Parser ]              one tree-sitter Parser instance per language, reused
       |
   tree-sitter AST        S-expression tree with typed nodes
       |
  [ Query Engine ]         per-language query strings extract captures
       |
   raw captures            list of (capture_name, node) tuples
       |
  [ Normalizer ]           language-agnostic: captures -> FileSyntax
       |
   FileSyntax              uniform output model for all languages
```

### Parser (`scanning/parser.py`)

```python
class TreeSitterParser:
    """Wraps tree-sitter. One instance per language, thread-safe for read-only use."""

    def __init__(self, language: Language):
        self._parser = tree_sitter.Parser()
        self._language = tree_sitter_languages.get_language(language.value)
        self._parser.set_language(self._language)
        self._queries = load_queries(language)  # from scanning/queries/<lang>.py

    def parse(self, content: bytes) -> ParseResult:
        """Parse file content, return AST + captures."""
        tree = self._parser.parse(content)
        has_errors = self._check_errors(tree.root_node)
        captures = self._run_queries(tree.root_node, content)
        return ParseResult(tree=tree, captures=captures, has_errors=has_errors)

    def _check_errors(self, root) -> bool:
        """Walk tree looking for ERROR or MISSING nodes."""
        ...

    def _run_queries(self, root, content) -> dict[str, list[CaptureNode]]:
        """Execute all query patterns, return grouped captures."""
        ...
```

Parser instances are cached per language (one per process). They are reused across files of the same language.

### Query Engine (`scanning/queries/`)

Each language has a query module containing tree-sitter S-expression queries for extracting:

1. **Function definitions** -- name, parameters, body, decorators
2. **Class definitions** -- name, bases, body
3. **Import declarations** -- source path, imported names
4. **Call expressions** -- within function bodies, direct and qualified

Queries use tree-sitter's query syntax with `@capture` names. Example captures:

| Capture | What it binds |
|---------|---------------|
| `@fn.name` | Function name identifier node |
| `@fn.params` | Parameters node (entire parameter list) |
| `@fn.body` | Function body block node |
| `@fn.decorator` | Decorator node above function |
| `@class.name` | Class name identifier node |
| `@class.bases` | Base class list node |
| `@class.body` | Class body block node |
| `@import.source` | Import module/path string node |
| `@import.names` | Imported name nodes |
| `@call.direct` | Direct function call identifier |
| `@call.object` | Object in `obj.method()` |
| `@call.method` | Method name in `obj.method()` |

### Per-Language Queries

Each language module in `scanning/queries/` exports a `QUERIES: dict[str, str]` mapping query names to S-expression strings. Approximate complexity per language:

| Language | Query complexity | Key differences |
|----------|-----------------|-----------------|
| Python | ~60 lines | Indent-based body, `self.x` field extraction, decorator syntax, relative imports with dots |
| Go | ~50 lines | `func` vs method declaration (receiver), grouped imports `import (...)`, exported = capitalized |
| TypeScript | ~70 lines | Arrow functions, `interface`, `type` aliases, `export default`, JSX |
| JavaScript | ~65 lines | Same AST as TypeScript minus type annotations |
| Java | ~60 lines | Annotations (`@Override`), access modifiers, generic types, package imports |
| Rust | ~55 lines | `fn`, `impl` blocks, `trait`, `use` with nested paths, `pub` visibility |
| Ruby | ~50 lines | `def`/`end` blocks, `module`, `require`/`require_relative`, block syntax |
| C/C++ | ~65 lines | `#include`, function pointer syntax, `class`/`struct`, templates, preprocessor |

#### Python query excerpt

```python
QUERIES = {
    "functions": """
        (function_definition
          name: (identifier) @fn.name
          parameters: (parameters) @fn.params
          body: (block) @fn.body)
    """,
    "methods": """
        (class_definition
          body: (block
            (function_definition
              name: (identifier) @fn.name
              parameters: (parameters) @fn.params
              body: (block) @fn.body)))
    """,
    "classes": """
        (class_definition
          name: (identifier) @class.name
          superclasses: (argument_list)? @class.bases
          body: (block) @class.body)
    """,
    "imports": """
        (import_statement
          name: (dotted_name) @import.source)
        (import_from_statement
          module_name: (dotted_name) @import.source
          name: (dotted_name) @import.names)
        (import_from_statement
          module_name: (relative_import) @import.source
          name: (dotted_name) @import.names)
    """,
    "calls": """
        (call
          function: (identifier) @call.direct)
        (call
          function: (attribute
            object: (_) @call.object
            attribute: (identifier) @call.method))
    """,
}
```

#### Go query excerpt

```python
QUERIES = {
    "functions": """
        (function_declaration
          name: (identifier) @fn.name
          parameters: (parameter_list) @fn.params
          body: (block) @fn.body)
    """,
    "methods": """
        (method_declaration
          receiver: (parameter_list) @fn.receiver
          name: (field_identifier) @fn.name
          parameters: (parameter_list) @fn.params
          body: (block) @fn.body)
    """,
    "imports": """
        (import_declaration
          (import_spec
            path: (interpreted_string_literal) @import.source))
        (import_declaration
          (import_spec_list
            (import_spec
              path: (interpreted_string_literal) @import.source)))
    """,
    "calls": """
        (call_expression
          function: (identifier) @call.direct)
        (call_expression
          function: (selector_expression
            operand: (identifier) @call.object
            field: (field_identifier) @call.method))
    """,
}
```

### Normalizer (`scanning/normalizer.py`)

The normalizer converts raw tree-sitter captures into the language-agnostic `FileSyntax` model. It handles:

1. **Capture grouping**: Associates `@fn.name`, `@fn.params`, `@fn.body` captures from the same function definition node into a single `FunctionDef`.

2. **Token counting**: For each function body, strips comments and string literals (using the tree-sitter AST node types, not regex), then counts tokens. This gives `body_tokens` and `signature_tokens`.

3. **Nesting depth**: For each function body node, walks the AST subtree counting nested block-inducing nodes (`if_statement`, `for_statement`, `while_statement`, `try_statement`, `match_statement`, etc.). The max depth across all paths is `nesting_depth`.

4. **Call extraction**: Formats call captures as strings: direct calls become `"foo"`, qualified calls become `"obj.method"`.

5. **Field extraction**: Language-specific logic:
   - Python: find `self.x = ...` assignments in `__init__` body + class-level annotated assignments
   - Go: struct field declarations
   - Java/TS: field declarations with access modifiers
   - Rust: struct fields
   - Ruby: `attr_accessor`, `attr_reader`, `@instance_var` assignments

6. **Decorator extraction**: Captures decorator/annotation nodes above function/class definitions, formats as strings.

The normalizer is the **only** place where language-specific post-processing logic exists outside the query files. It uses a dispatch table keyed on `Language`.

---

## What tree-sitter Gives vs Does Not Give

### tree-sitter provides

- Function/method names, parameters, body source text, start/end positions
- Call site identification (syntactic -- what identifier is called)
- Class definitions with inheritance, fields
- Import statements with full paths and imported names
- Nesting depth computed from real AST structure (not brace/indent counting)
- Decorator/annotation extraction
- Error-tolerant parsing (partial results from broken files)
- Consistent node types across language versions

### tree-sitter does NOT provide

| Missing capability | Why | Who handles it |
|-------------------|-----|----------------|
| Type inference | `self.db` -- what type is `db`? | graph/ with heuristics, or JARVIS for Python |
| Cross-file symbol resolution | Where does `db.query` actually point? | `import-resolution.md` resolves import paths; graph/ resolves call targets |
| Virtual dispatch resolution | Which override of `process()` gets called? | Not resolved in v2; CALL edges get confidence tags |
| Control flow analysis | Is this code reachable? | Out of scope for scanning/ |
| Macro expansion | C/C++ `#define`, Rust `macro_rules!` | Macros treated as opaque; body tokens counted as-is |

---

## Error Handling

### Unparseable file

When tree-sitter fails to parse a file entirely (returns a root ERROR node):

1. Log a warning: `"tree-sitter parse failed for {path}, falling back to regex"`
2. Run the legacy `ConfigurableScanner._analyze_file()` on the same content
3. Convert the resulting `FileMetrics` to a `FileSyntax` with `parse_mode = REGEX`
4. The `REGEX` FileSyntax has: line count, function count (int, no FunctionDef objects), import strings (no ImportDecl resolution), nesting depth (approximate)

### Partial parse errors

When tree-sitter parses most of the file but some nodes are ERROR:

1. Set `has_errors = True` on the FileSyntax
2. Extract all non-error subtrees normally
3. For function bodies containing ERROR nodes: set `body_tokens` from the raw text (best effort), set `calls = []` (unreliable in error regions)

### Encoding issues

1. Try UTF-8 first
2. On `UnicodeDecodeError`, try `latin-1`
3. On failure, skip file (log warning, no FileEntry emitted)

tree-sitter operates on `bytes`, so encoding affects only the normalizer's string conversion.

---

## Performance Targets

| Metric | Target | Basis |
|--------|--------|-------|
| Parse throughput | >= 100,000 lines/sec | tree-sitter benchmarks: ~166K lines/sec single-threaded |
| Single file (20K lines) | < 200ms | tree-sitter: ~120ms for 20K lines |
| Full scan (1000 files) | < 30 seconds | With query execution and normalization overhead |
| Memory per file | < 50MB peak | tree-sitter AST is compact; body_source strings are the main cost |
| Parser initialization | < 100ms per language | One-time cost, amortized across all files |

### Optimization strategies

1. **Parser reuse**: One `TreeSitterParser` instance per language, reused across all files of that language.
2. **Lazy body_source**: Store `(start_byte, end_byte)` references into the original content instead of copying strings. Materialize only when needed (stub detection, compression ratio).
3. **Parallel scanning**: Files can be parsed independently. Use `concurrent.futures.ProcessPoolExecutor` with one parser per worker. tree-sitter parsers are not thread-safe but are process-safe.
4. **Skip unchanged files**: When doing incremental scans, use `FileEntry.hash` to skip files that haven't changed since the last scan.
