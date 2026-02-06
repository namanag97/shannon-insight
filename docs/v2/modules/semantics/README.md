# semantics/ -- Module Specification

## Status: DOES NOT EXIST (entirely new)

This module implements **IR2 (SemanticForm)** -- the first layer of "understanding" above raw syntax. It answers: *what does each file mean?*

## Responsibility

Classify every source file by its **role** in the system, extract the **concepts** it deals with, and measure its **completeness**. This is the bridge between syntactic structure (IR1) and relational structure (IR3): before we can build a meaningful graph, we need to know what each node *is* and what it's *about*.

Three concerns, in order of reliability:

1. **Role classification** -- deterministic decision tree, works on any file size.
2. **Concept extraction** -- TF-IDF + Louvain on identifier co-occurrence, requires 20+ unique identifiers.
3. **Completeness measurement** -- stub ratio, docstring coverage, TODO density (mostly forwarded from IR1).

## Exports

| Export | Kind | Description |
|--------|------|-------------|
| `SemanticAnalyzer` | class | Orchestrator. Takes `list[FileSyntax]` and produces `dict[str, FileSemantics]`. |
| `FileSemantics` | dataclass | Per-file semantic annotation (role, concepts, API surface, completeness). |
| `Role` | enum | 12-value classification: MODEL, SERVICE, UTILITY, CONFIG, TEST, CLI, INTERFACE, EXCEPTION, CONSTANT, ENTRY_POINT, MIGRATION, UNKNOWN. |
| `Concept` | dataclass | A topic cluster: dominant token, member tokens, weight. |
| `Symbol` | dataclass | A public API element: name, kind, parameter count. |
| `ConsumedSymbol` | dataclass | An imported symbol that is actually referenced in code. |
| `Completeness` | dataclass | Stub ratio, impl Gini, docstring coverage, TODO density. |

## Requires

| Module | What we consume | Why |
|--------|----------------|-----|
| `scanning/` | `FileSyntax`, `FunctionDef`, `ClassDef`, `ImportDecl` | All classification and extraction operates on parsed syntax trees. FileSyntax is our sole input. |

No other module dependencies. semantics/ sits directly after scanning/ in the structural spine.

## Feeds Into

| Module | What we provide | Why they need it |
|--------|----------------|------------------|
| `graph/` | `Role` (per file), `FileSemantics` (annotated nodes) | Orphan detection needs role (entry points and tests are not orphans). Graph nodes carry semantic annotations. |
| `signals/` | `concept_count`, `concept_entropy`, `naming_drift`, `todo_density`, `docstring_coverage`, `role` | These signals flow into the SignalField and are consumed by finders and composite scores. |
| `architecture/` | `Role` (per file) | Module-level `role_consistency` aggregates file roles. |

## Computed Signals

All signals belong to dimension **D3 NAMING** (see `registry/dimensions.md`). Formulas are defined in `registry/signals.md`; this module specifies HOW to compute them.

| # | Signal | How computed | Details |
|---|--------|-------------|---------|
| 8 | `role` | Deterministic decision tree on FileSyntax structural signals. | See `role-classification.md`. |
| 9 | `concept_count` | Count of Louvain communities from identifier co-occurrence graph. | See `concept-extraction.md`. Requires 20+ unique identifiers; below threshold returns 1. |
| 10 | `concept_entropy` | Shannon entropy of concept weights. | Computed after concept extraction. H = 0 when concept_count = 1. |
| 11 | `naming_drift` | Cosine distance between filename TF-IDF vector and content concept TF-IDF vector. | See `naming-drift.md`. Requires 20+ unique identifiers. |
| 12 | `todo_density` | Regex scan for TODO/FIXME/HACK tokens divided by line count. | Scans raw source from FileSyntax. |
| 13 | `docstring_coverage` | Ratio of documented public symbols to total public symbols. | Public symbols = functions/classes not prefixed with `_`. Documented = has a docstring (Python), JSDoc (JS/TS), or doc comment (Go, Rust, Java). |

## Interface

```python
class SemanticAnalyzer:
    def analyze(self, files: list[FileSyntax]) -> dict[str, FileSemantics]:
        """Produce FileSemantics for every file.

        Args:
            files: Parsed syntax from scanning/.

        Returns:
            Mapping from file path to FileSemantics.
            Every input file gets an entry -- no file is skipped entirely.
        """

    def analyze_file(self, file: FileSyntax, corpus_idf: dict[str, float]) -> FileSemantics:
        """Single-file analysis given pre-computed IDF weights.

        Two-pass design: first pass builds corpus IDF, second pass
        analyzes each file using those weights.
        """
```

## Internal Structure

```
semantics/
    __init__.py          # re-exports: SemanticAnalyzer, FileSemantics, Role, ...
    models.py            # FileSemantics, Role, Concept, Symbol, ConsumedSymbol, Completeness, SemanticDelta
    analyzer.py          # SemanticAnalyzer (orchestrator)
    role_classifier.py   # classify_role(FileSyntax) -> Role
    concept_extractor.py # extract_concepts(FileSyntax, idf) -> list[Concept]
    naming_drift.py      # compute_naming_drift(path, concepts, idf) -> float
    completeness.py      # compute_completeness(FileSyntax) -> Completeness
    tokenizer.py         # identifier splitting, normalization, stopword removal
```

## Two-Pass Design

Concept extraction requires corpus-wide IDF weights. The analyzer runs in two passes:

1. **Pass 1 -- Corpus construction**: Extract and normalize all identifiers from every file. Build a global IDF dictionary: `idf(token) = log(N / df(token))` where `df` = number of files containing the token.
2. **Pass 2 -- Per-file analysis**: For each file, classify role (no corpus needed), extract concepts (using corpus IDF), compute naming drift (using corpus IDF), measure completeness.

Role classification is independent of the corpus and can run in pass 1.

## Temporal Contract

As required by `registry/temporal-operators.md`, this module defines its temporal behavior:

### Output at time t

```
FileSemantics(f, t) -- the semantic annotation of file f at snapshot time t.
```

Every field is parameterized by time. A file's role, concepts, and completeness can all change between snapshots.

### Delta(t1, t2)

```
SemanticDelta:
    role_changed:       Optional[tuple[Role, Role]]   # (old, new) or None
    concepts_added:     list[Concept]
    concepts_removed:   list[Concept]
    concept_drift:      float                          # cosine distance between concept vectors
    api_surface_delta:  int                            # change in public symbol count
    completeness_delta: float                          # change in stub_ratio
```

### Key Time Series

| Metric | Formula | What it reveals |
|--------|---------|-----------------|
| `concept_count(f, t)` | len(concepts) | Scope creep (growing) or focusing (shrinking) |
| `concept_drift(f, t)` | Cumulative cosine distance from origin | Has the file wandered from its original purpose? |
| `naming_drift(f, t)` | Filename vs content distance | Did someone repurpose this file without renaming? |
| `api_surface(f, t)` | len(public_api) | Over-exposure growth |
| `stub_ratio(f, t)` | From IR1 | Are stubs being filled in? |

### Role Transition Matrix

Across all files and all time steps, count transitions from role A to role B:

```
          MODEL  SERVICE  UTILITY  CONFIG  ...
MODEL       45      3       1       0
SERVICE      1     38       2       0
UTILITY      0      5      29       1
...
```

Off-diagonal entries indicate role confusion events. A high off-diagonal count signals architectural instability.

### Reconstruction

To produce `FileSemantics(f, t_historical)`:

1. Retrieve historical FileSyntax via `git show <sha>:<path>` and re-parse.
2. Re-run `SemanticAnalyzer.analyze_file()` with corpus IDF from that snapshot.

This is Kind 3 temporal data (expensive, on-demand). See `registry/temporal-operators.md`.

## Error Handling

| Condition | Behavior |
|-----------|----------|
| File has < 20 unique identifiers | Skip concept extraction. Set `concept_count = 1`, `concept_entropy = 0.0`, `naming_drift = None`. Role classification still runs. |
| File has 0 functions and 0 classes | Role defaults to CONSTANT or UNKNOWN based on content. Completeness uses file-level metrics only. |
| File cannot be parsed by scanning/ | No FileSyntax produced, so no FileSemantics. This file is invisible to semantics/. |
| All identifiers are stopwords after filtering | Treat as < 20 unique identifiers. |
| Empty file | Role = UNKNOWN, all concept signals = None/0, completeness = trivial. |

## Performance Considerations

- Role classification: O(1) per file (pattern matching on pre-computed structural counts).
- Identifier extraction and tokenization: O(tokens) per file -- single pass over source.
- IDF computation: O(files x mean_tokens) -- one pass to build document-frequency map.
- Concept extraction (TF-IDF + Louvain): O(tokens^2) per file for co-occurrence graph construction. For files with > 500 unique identifiers, subsample to top-500 by TF-IDF weight.
- Naming drift: O(tokens) per file -- dot product of sparse vectors.

Total: dominated by concept extraction. Expected ~100ms for a 1000-line file on modern hardware.
