# Phase 0: Document and Stabilize Current State

## Goal

Establish a verified, documented baseline of every existing module, signal, finder, and test so that subsequent phases can be measured against a known starting point.

## Packages Touched

None modified. All packages inventoried:

- `scanning/` (6 files) -- language-aware file parsing, `ScannerFactory`, `UniversalScanner`
- `graph/` (5 files) -- dependency graph construction, algorithms (PageRank, SCC, Louvain, blast radius), engine
- `signals/` (9 files) -- per-file quality primitives (compression, centrality, volatility, coherence, cognitive load)
- `temporal/` (5 files) -- git log parsing, co-change matrix, churn trajectory classification
- `persistence/` (11 files) -- SQLite history, snapshot capture, diffing, rename detection, scoped analysis
- `insights/` (12 files) -- InsightKernel blackboard, 4 analyzers, 7 finders, ranking, store
- `cli/` (9 files) -- Typer app, 6 commands (main, explain, diff, health, history, report)
- `math/` (8 files) -- entropy, compression, Gini, graph algorithms, robust statistics, signal fusion
- `visualization/` (3 files) -- HTML treemap report
- Root modules: `models.py`, `config.py`, `logging_config.py`, `cache.py`, `file_ops.py`, `security.py`, `exceptions/`

## Prerequisites

None. This is the starting phase.

## Changes

No code changes. Documentation-only deliverables:

| Deliverable | Description |
|---|---|
| `CLAUDE.md` audit | Verify every section matches actual code (package names, commands, conventions) |
| Existing signal inventory | Catalog which signals from `registry/signals.md` already exist in v1 and where they are computed |
| Existing finder inventory | Catalog which finders from `registry/finders.md` already exist and their current `requires` declarations |
| Test coverage report | Run `make test` with coverage, document per-module coverage percentages |
| Dependency map | Document actual import relationships between packages (verify against `01-contracts.md`) |
| Gap analysis | For each signal/finder in the v2 registry, mark as EXISTS, PARTIAL, or MISSING |

## Existing Signals (v1 baseline)

Signals currently computed by the v1 codebase:

| # | Signal | Status | Computed by |
|---|--------|--------|-------------|
| 1 | `lines` | EXISTS | `scanning/` |
| 2 | `function_count` | EXISTS | `scanning/` |
| 3 | `class_count` | EXISTS | `scanning/` |
| 4 | `max_nesting` | PARTIAL | `scanning/` (regex-based, inaccurate for nested constructs) |
| 5 | `impl_gini` | EXISTS | `signals/plugins/` |
| 6 | `stub_ratio` | EXISTS | `signals/plugins/` |
| 7 | `import_count` | EXISTS | `scanning/` |
| 14 | `pagerank` | EXISTS | `graph/algorithms.py` |
| 16 | `in_degree` | EXISTS | `graph/algorithms.py` |
| 17 | `out_degree` | EXISTS | `graph/algorithms.py` |
| 18 | `blast_radius_size` | EXISTS | `graph/algorithms.py` |
| 23 | `community` | EXISTS | `graph/algorithms.py` (Louvain) |
| 24 | `compression_ratio` | EXISTS | `signals/plugins/compression.py` |
| 25 | `semantic_coherence` | EXISTS | `signals/plugins/coherence.py` |
| 26 | `cognitive_load` | EXISTS | `signals/plugins/cognitive_load.py` |
| 27 | `total_changes` | EXISTS | `temporal/` |
| 28 | `churn_trajectory` | EXISTS | `temporal/churn.py` |
| 29-30 | `churn_slope`, `churn_cv` | EXISTS | `temporal/churn.py` |
| 31-32 | `bus_factor`, `author_entropy` | EXISTS | `temporal/` |
| 33-34 | `fix_ratio`, `refactor_ratio` | EXISTS | `temporal/` |
| 52 | `modularity` | EXISTS | `graph/algorithms.py` |
| 53 | `fiedler_value` | EXISTS | `insights/analyzers/spectral.py` |

## Existing Finders (v1 baseline)

| Finder | Status |
|--------|--------|
| HIGH_RISK_HUB | EXISTS |
| HIDDEN_COUPLING | EXISTS |
| GOD_FILE | EXISTS |
| UNSTABLE_FILE | EXISTS |
| BOUNDARY_MISMATCH | EXISTS |
| DEAD_DEPENDENCY | EXISTS |
| CHRONIC_PROBLEM | EXISTS |

## New Signals Available After This Phase

None. Documentation-only phase.

## New Finders Available After This Phase

None. Documentation-only phase.

## New Temporal Capabilities

None. Documentation-only phase.

## Acceptance Criteria

1. `make test` passes with 247 tests green
2. `make check` (lint + type-check) passes or known errors are documented
3. Gap analysis spreadsheet complete: every signal 1-62 and every finder 1-22 marked EXISTS/PARTIAL/MISSING
4. Import dependency map matches `01-contracts.md` or discrepancies are documented
5. CLAUDE.md is verified accurate against actual codebase

## Estimated Scope

- 0 files created/modified in `src/`
- 1 gap analysis document
- 1 dependency map document
- ~2-3 hours of audit work
