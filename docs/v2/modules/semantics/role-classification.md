# semantics/ -- Role Classification

## Overview

Every source file is assigned exactly one `Role` from a 12-value enum. Classification is **deterministic** -- a pure decision tree on structural signals from `FileSyntax` (IR1). No ML, no minimum data, no corpus dependency. Works on files of any size, including empty files.

Expected accuracy: **~80%** on real codebases. The remaining ~20% land in UNKNOWN or are misclassified -- which is itself useful signal (role confusion = architectural smell).

## Input

The classifier receives a single `FileSyntax` object and produces a `Role`. Relevant fields from FileSyntax:

```
FileSyntax:
    path:       str              # file path (for pattern matching)
    functions:  list[FunctionDef]
    classes:    list[ClassDef]
    imports:    list[ImportDecl]
    top_level:  int              # non-function, non-class top-level statements
```

From `ClassDef`:
- `bases: list[str]` -- parent classes
- `methods: list[FunctionDef]` -- class methods
- `fields: list[str]` -- instance attributes
- `is_abstract: bool` -- has ABC base or all methods abstract

From `FunctionDef`:
- `decorators: list[str]` -- decorator names
- `body_tokens: int` -- token count in function body

## Decision Tree

Rules are evaluated **top to bottom**. First match wins.

```
classify_role(file: FileSyntax) -> Role:

    # ---- Path-based rules (highest priority, cheapest) ----

    1. TEST
       path matches any of:
         - contains "/test_" or "/tests/" or "/_test" or "/test/"
         - ends with "_test.py", "_test.go", ".test.ts", ".test.js",
           ".spec.ts", ".spec.js", "Test.java", "_test.rb"
         - starts with "test_"
       -> return TEST

    2. MIGRATION
       path matches any of:
         - contains "/migrations/" or "/migrate/" or "/alembic/"
         - matches pattern: **/versions/*.py (Alembic)
         - matches pattern: **/migrations/???_*.py (Django)
         - ends with ".sql" inside a migrations directory
       -> return MIGRATION

    # ---- Structural rules (from FileSyntax content) ----

    3. ENTRY_POINT
       any of:
         - path ends with "__main__.py"
         - file contains `if __name__ == "__main__":` guard (Python)
         - file contains `func main()` at top level (Go)
         - path matches "cmd/*/main.go" or "cmd/*.go"
         - path matches "main.rs", "main.ts", "main.js"
         - file contains WSGI/ASGI app assignment (e.g., `app = FastAPI()`)
       -> return ENTRY_POINT

    4. INTERFACE
       any of:
         - any class inherits from ABC, ABCMeta, Protocol (Python)
         - any class has @abstractmethod decorators on all methods
         - file defines only `interface` types (Go)
         - file defines only `interface` or `abstract class` (TypeScript/Java)
         - file defines only trait definitions (Rust)
       -> return INTERFACE

    5. CONSTANT
       all of:
         - class_count == 0
         - function_count == 0 OR all functions have body_tokens < 5
         - all_caps_ratio > 0.8
       where:
         all_caps_ratio = (ALL_CAPS top-level assignments) / (total top-level assignments)
         Requires at least 2 top-level assignments.
       -> return CONSTANT

    6. EXCEPTION
       all of:
         - class_count >= 1
         - every class inherits from Exception, BaseException, Error,
           RuntimeError, ValueError, or another exception class in the file
         - function_count <= class_count (no significant standalone logic)
       -> return EXCEPTION

    7. MODEL
       any of:
         - any class is "field-heavy": len(fields) > len(methods)
         - any class inherits from known ORM bases:
           BaseModel (Pydantic), Model (Django), Base (SQLAlchemy),
           TypedDict, NamedTuple, dataclass-decorated
         - any class has @dataclass or @attrs decorator
         - file defines only struct types (Go, Rust, C)
       -> return MODEL

    8. CLI
       any of:
         - imports click, typer, argparse, fire, or equivalent
         - has @click.command, @app.command, or similar decorators
         - imports cobra (Go), clap (Rust), commander (JS)
       -> return CLI

    9. CONFIG
       any of:
         - path matches common config patterns:
           "config.py", "settings.py", "conf.py", "*.config.ts",
           "*.config.js", ".env*" handler
         - file loads environment variables (os.environ, dotenv, Viper)
         - class inherits from BaseSettings (Pydantic)
         - majority of assignments are from env/config sources
       -> return CONFIG

    10. SERVICE
        all of:
          - class_count >= 1
          - at least one class has both fields AND methods (has state + behavior)
          - function_count > 2 (non-trivial logic)
          - does not match MODEL (fields do NOT outnumber methods)
        -> return SERVICE

    11. UTILITY
        all of:
          - class_count == 0
          - function_count > 0
        -> return UTILITY

    12. UNKNOWN
        -> return UNKNOWN (fallback)
```

## Per-Language Considerations

The decision tree is language-agnostic in structure but the **pattern matchers** are language-aware:

### Python
- ABC/Protocol detection via `bases` containing "ABC", "Protocol", "ABCMeta".
- `@abstractmethod`, `@dataclass`, `@click.command` detected via `decorators`.
- `__main__.py` and `if __name__` guard for ENTRY_POINT.
- `_` prefix for private symbols (used in docstring_coverage, not role classification).

### Go
- `func main()` at top level for ENTRY_POINT.
- `cmd/*/main.go` path pattern for ENTRY_POINT.
- `interface` type declarations for INTERFACE.
- `struct` type declarations for MODEL.
- No class concept -- SERVICE requires struct with receiver methods.

### TypeScript / JavaScript
- `.test.ts`, `.spec.ts` suffixes for TEST.
- `interface` and `abstract class` for INTERFACE.
- `export default class` with methods and constructor state for SERVICE.
- Pure `export function` files for UTILITY.
- `*.config.ts`, `*.config.js` for CONFIG.

### Java
- `Test` suffix and JUnit imports for TEST.
- `interface` and `abstract class` keywords for INTERFACE.
- `@Entity`, `@Table` annotations for MODEL.
- `main(String[])` for ENTRY_POINT.

### Rust
- `trait` definitions for INTERFACE.
- `struct` definitions for MODEL.
- `fn main()` for ENTRY_POINT.
- `_test.rs` and `#[cfg(test)]` for TEST.

### Ruby
- `_test.rb`, `_spec.rb` for TEST.
- Modules with only method definitions for UTILITY.
- Classes inheriting `ActiveRecord::Base` for MODEL.

### C/C++
- Files with only struct/typedef definitions for MODEL.
- Files with `int main(` for ENTRY_POINT.
- Header files with only declarations for INTERFACE.

## Ambiguity Resolution

When a file matches multiple roles, the tree ordering resolves it:

| Ambiguity | Resolution | Rationale |
|-----------|-----------|-----------|
| Test file that is also an entry point | TEST wins | Tests are always tests, regardless of how they are invoked. |
| Config file with constants | CONFIG wins | Config with constants is still config; constants without config are CONSTANT. |
| CLI with service logic | CLI wins | The CLI nature dominates the file's architectural purpose. |
| Model with methods | MODEL if fields > methods, else SERVICE | Field-heavy = data container, method-heavy = service. |
| Utility imported as interface | UTILITY | We classify by structure, not by usage. If it has no classes and only functions, it is UTILITY even if used as an interface. |

## Role Consistency Score (Per Directory)

After classifying all files, compute a **role consistency score** for each directory (potential module):

```
files_in_dir = [f for f in files if dirname(f.path) == dir]
roles = [f.role for f in files_in_dir]
consistency = max(Counter(roles).values()) / len(roles)
```

- `1.0`: All files in the directory share the same role (well-focused module).
- `< 0.5`: Roles are scattered (confused module boundary).

This score is consumed by `architecture/` as signal #44 (`role_consistency`, per-module, D3 NAMING) -- see registry/signals.md.

## Accuracy Expectations

| Role | Expected precision | Expected recall | Notes |
|------|-------------------|-----------------|-------|
| TEST | ~99% | ~99% | Path patterns are highly reliable. |
| ENTRY_POINT | ~95% | ~90% | `__main__` and `func main()` are unambiguous. WSGI/ASGI detection is heuristic. |
| MIGRATION | ~98% | ~95% | Path patterns for Django/Alembic are well-defined. |
| INTERFACE | ~90% | ~75% | ABC/Protocol reliable in Python. Go interfaces clear. Other languages vary. |
| MODEL | ~85% | ~80% | Field-heavy heuristic works well but misses some models with logic. |
| CONSTANT | ~95% | ~80% | ALL_CAPS ratio is reliable when present. Misses mixed files. |
| EXCEPTION | ~95% | ~90% | Exception inheritance is unambiguous. |
| SERVICE | ~70% | ~70% | Hardest to distinguish from UTILITY with classes. |
| UTILITY | ~80% | ~85% | Clear when class_count == 0, but misses utility classes. |
| CLI | ~90% | ~85% | Import-based detection is reliable. |
| CONFIG | ~85% | ~75% | Path patterns help. Content detection is heuristic. |
| UNKNOWN | N/A | N/A | Catch-all. A high UNKNOWN rate is itself diagnostic. |

**Overall weighted accuracy: ~80%**. This is sufficient because the role signal is one input among many -- misclassification is softened by concept extraction and graph structure.
