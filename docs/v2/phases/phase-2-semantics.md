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
| `insights/store.py` | Add semantic signal slots: `role`, `concept_count`, `concept_entropy`, `naming_drift`, `todo_density`, `docstring_coverage` |

### Role Classification Decision Tree

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

### Concept Extraction (Tier 2: files with 20+ unique identifiers)

```
1. Extract all identifiers from FileSyntax
2. Split camelCase/snake_case into tokens
3. Build TF-IDF vectors (within-file corpus)
4. Build token co-occurrence graph (tokens appearing in same function)
5. Run Louvain community detection on co-occurrence graph
6. Each community = a concept, with weight = sum of TF-IDF scores
7. concept_entropy = H(concept_weights)
```

For files with fewer than 20 identifiers: `concepts = [Concept(topic=role.name, weight=1.0)]`, `concept_entropy = 0.0`.

## New Signals Available After This Phase

| # | Signal | Type | Range | Computed by |
|---|--------|------|-------|-------------|
| 8 | `role` | enum(Role) | 12 values | `semantics/roles.py` |
| 9 | `concept_count` | int | [0, inf) | `semantics/concepts.py` |
| 10 | `concept_entropy` | float | [0, inf) | `semantics/concepts.py` |
| 11 | `naming_drift` | float | [0, 1] | `semantics/naming.py` |
| 12 | `todo_density` | float | [0, inf) | `semantics/completeness.py` |
| 13 | `docstring_coverage` | float | [0, 1] | `semantics/completeness.py` |

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

## Estimated Scope

- ~9 new files (package + models + 4 computation modules + 2 test files)
- ~3 modified files
- ~2 weeks of implementation
