# Phase 2: IR2 Semantic Layer

## Goal

Create the `semantics/` package to classify file roles, extract concept clusters, detect naming drift, and measure documentation coverage -- producing `FileSemantics` for every source file.

## Packages Touched

- **NEW** `semantics/` -- new package (IR2)
- `insights/analyzers/` -- minor: wire semantic signals into `AnalysisStore`
- `insights/kernel.py` -- register semantic analyzer in the pipeline

## Prerequisites

- Phase 1 complete (tree-sitter `FileSyntax` with functions, classes, decorators, calls)

## Changes

### New Files

| File | Purpose |
|---|---|
| `semantics/__init__.py` | Exports: `SemanticAnalyzer`, `FileSemantics`, `Role` |
| `semantics/models.py` | `FileSemantics`, `Role` enum, `Concept`, `Symbol`, `Completeness` dataclasses |
| `semantics/analyzer.py` | `SemanticAnalyzer` -- orchestrates role classification + concept extraction per file |
| `semantics/roles.py` | Deterministic role classifier (decision tree on structural signals, see W6) |
| `semantics/concepts.py` | TF-IDF + Louvain concept extraction for files with 20+ unique identifiers |
| `semantics/naming.py` | Naming drift: `1 - cosine(tfidf(filename_tokens), tfidf(content_concept_tokens))` |
| `semantics/completeness.py` | `todo_density`, `docstring_coverage` computation |
| `tests/test_semantics.py` | Tests for role classification, concept extraction, naming drift |
| `tests/test_role_classification.py` | Focused tests for the role decision tree across file archetypes |

### Modified Files

| File | Change |
|---|---|
| `insights/analyzers/__init__.py` | Add semantic analyzer import |
| `insights/kernel.py` | Register `SemanticAnalyzer` in the analyzer pipeline (runs after scanning, before graph) |
| `insights/store.py` | Add `semantics: Optional[Dict[str, FileSemantics]] = None` slot (full semantic objects) and `roles: Optional[Dict[str, str]] = None` convenience slot. Individual signals are read from `FileSemantics` objects, not scattered into `file_signals`. |

### Role Classification Decision Tree

**Priority rule**: The decision tree is evaluated top-to-bottom. First matching rule wins. No multi-classification.

```
classify_role(file: FileSyntax) -> Role:
    if path matches test patterns (test_*, *_test, tests/)     -> TEST
    if has __main__ guard or @click.command / @app.command      -> ENTRY_POINT
    if has ABC, Protocol, or @abstractmethod                    -> INTERFACE
    if all identifiers are UPPER_SNAKE_CASE                     -> CONSTANT
    if majority of classes raise custom exceptions               -> EXCEPTION
    if classes are field-heavy (>3 fields, few methods)          -> MODEL
    if has CLI decorators (@app.route, typer, argparse)          -> CLI
    if has @app.get/@app.post or inherits BaseHTTPHandler        -> SERVICE
    if has migration patterns (alembic, django migrations)       -> MIGRATION
    if has stateful classes with methods                         -> SERVICE
    if all top-level definitions are functions (no classes)       -> UTILITY
    if has only re-exports or __all__                            -> CONFIG
    else                                                         -> UNKNOWN
```

### Concept Extraction (tiered by file complexity)

**Tier 1 (< 3 functions)**: Single concept based on role.
```concepts = [Concept(topic=role.name, weight=1.0)]```
concept_entropy = 0.0, concept_count = 1

**Tier 2 (3-9 functions)**: Keyword frequency. Extract identifiers, split camelCase/snake_case, count token frequency, top-k tokens (k=3) become concept labels. No Louvain -- graph too small.

**Tier 3 (10+ functions, 20+ unique identifiers)**: Full TF-IDF + Louvain pipeline (unchanged from current spec).

Files below Tier 3 get naming_drift = 0.0 (not enough data to compare filename vs content meaningfully).

### Implementation Note: Two-Pass Architecture

TF-IDF requires corpus-wide IDF values (computed across ALL files). The `SemanticAnalyzer` **cannot** process files lazily — it needs all files upfront.

```
Pass 1: Extract identifiers from every file → build corpus-wide IDF dictionary
Pass 2: Compute per-file TF-IDF vectors → run Louvain on co-occurrence graph for Tier 3 files
```

The `SemanticAnalyzer.analyze(store)` interface has access to all files via `store.file_syntax`, so this works. But the implementation must be explicitly two-pass. Do NOT attempt streaming or per-file processing for Tier 3 concept extraction.

### Store Changes

```python
@dataclass
class AnalysisStore:
    # ... existing ...

    # Phase 2 additions:
    semantics: Optional[Dict[str, FileSemantics]] = None  # path -> full FileSemantics
    roles: Optional[Dict[str, str]] = None                 # path -> role string (convenience alias)
```

`SemanticAnalyzer` writes both slots. `roles` is a convenience alias so downstream consumers (Phase 3 `compute_orphans`, Phase 4 `ArchitectureAnalyzer`) don't need to unpack `FileSemantics` objects just to get the role.

## New Signals Available After This Phase

| # | Signal | Type | Range | Computed by |
|---|--------|------|-------|-------------|
| 8 | `role` | enum(Role) | 12 values | `semantics/roles.py` |
| 9 | `concept_count` | int | [0, inf) | `semantics/concepts.py` |
| 10 | `concept_entropy` | float | [0, inf) | `semantics/concepts.py` |
| 11 | `naming_drift` | float | [0, 1] | `semantics/naming.py` |
| 12 | `todo_density` | float | [0, inf) | `semantics/completeness.py` |
| 13 | `docstring_coverage` | float | [0, 1] | `semantics/completeness.py` | Python only. For other languages: `None` (not 0.0 -- that would mean 'no docs' which is a different claim than 'cannot measure'). |

## New Finders Available After This Phase

No new finders yet (finders are Phase 6). However, signals 8-13 are prerequisites for:

- ORPHAN_CODE (needs `role` for entry point / test exclusion)
- NAMING_DRIFT (needs `naming_drift`)
- GOD_FILE upgrade (can now use `concept_count` + `concept_entropy` as evidence)

## New Temporal Capabilities

- `SemanticDelta`: role_changed (bool), concepts_added/removed, concept_drift (cosine distance from origin over time)
- `concept_drift(f, t)` becomes a trackable time series after persistence is updated (Phase 7)

## Acceptance Criteria

1. Role classification produces correct roles for `test_codebase/` Go files
2. Role classification produces correct roles for Shannon Insight's own Python source
3. Python test files classified as TEST, `__init__.py` as CONFIG, CLI files as CLI
4. Concept extraction produces 2+ concepts for files with diverse content (e.g., `kernel.py`)
5. `naming_drift` > 0.5 for intentionally misnamed test fixture
6. `todo_density` correctly counts TODO/FIXME/HACK markers
7. `docstring_coverage` = 1.0 for fully documented file, 0.0 for undocumented file
8. Graceful degradation: files with < 20 identifiers get single-concept fallback
9. All existing tests pass
10. Files with < 3 functions get single-concept fallback (Tier 1)

**Generic filename handling**: Files named `utils.py`, `helpers.py`, `common.py`, `misc.py`, `shared.py`, `base.py`, `core.py`, `__init__.py` get `naming_drift = 0.0` (they are intentionally generic, not drifted).

## Estimated Scope

- ~9 new files (package + models + 4 computation modules + 2 test files)
- ~3 modified files
- ~2 weeks of implementation
