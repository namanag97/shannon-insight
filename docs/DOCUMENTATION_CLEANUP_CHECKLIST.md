# Documentation Cleanup Checklist

**Goal:** Organize documentation for clarity, remove outdated content, fix inconsistencies
**Timeline:** 1 week (17-23 hours total)
**Status:** Not Started

---

## Phase 1: Archive Outdated Docs (1 hour)

### Create Archive Directory
- [ ] Create `/docs/archived/` directory
- [ ] Create `/docs/archived/README.md` with explanation:
  ```markdown
  # Archived Documentation

  This directory contains historical documentation that is no longer current but preserved for reference.

  ## Why These Were Archived
  - Replaced by v2 specifications in `/docs/v2/`
  - Historical implementation prompts no longer relevant
  - Superseded by more complete research documents in `/research/`

  ## What to Reference Instead
  - For v1 documentation: See `/docs/` root files (SIGNALS.md, FINDERS.md, CONFIGURATION.md)
  - For v2 specifications: See `/docs/v2/phases/` and `/docs/v2/registry/`
  - For research: See `/research/`
  - For getting started: See `/docs/GETTING_STARTED.md`
  ```

### Move Files to Archive

**From Root:**
- [ ] Move `AGENT_PROMPT.md` → `/docs/archived/AGENT_PROMPT.md`
- [ ] Move `PRIMITIVE_REDESIGN.md` → `/docs/archived/PRIMITIVE_REDESIGN.md`

**From docs/:**
- [ ] Move `docs/INSIGHT_DELIVERY_PIPELINE.md` → `/docs/archived/`
- [ ] Move `docs/REARCHITECTURE_PLAN.md` → `/docs/archived/`
- [ ] Move `docs/IMPLEMENTATION_AGENT_PROMPT.md` → `/docs/archived/`
- [ ] Move `docs/MATHEMATICAL_FOUNDATION.md` → `/docs/archived/` (duplicate of research/ version)
- [ ] Move `docs/DOCUMENTATION_PROMPT.md` → `/docs/archived/`
- [ ] Move `docs/QA-AGENT-PROMPT.md` → `/docs/archived/`
- [ ] Move `docs/DASHBOARD_PROMPTS.md` → `/docs/archived/`
- [ ] Move `docs/BASELINE_ANALYSIS.md` → `/docs/archived/`
- [ ] Move `docs/brainstorm-v2.md` → `/docs/archived/`
- [ ] Move `docs/framework.md` → `/docs/archived/` (replaced by v2/phases/)
- [ ] Move `docs/ir-spec.md` → `/docs/archived/` (replaced by v2/modules/)
- [ ] Move `docs/spec-v2.md` → `/docs/archived/` (replaced by v2/phases/)
- [ ] Move `docs/mathematics.md` → `/docs/archived/` (duplicate of research/ version)
- [ ] Move `docs/solutions.md` → `/docs/archived/`
- [ ] Move `docs/walkthrough.md` → `/docs/archived/`

**Total Files Archived:** 16

---

## Phase 2: Fix Inconsistencies (2-3 hours)

### Fix CONTRIBUTING.md
- [ ] Line 131: Change "analyzers/" → "scanning/"
- [ ] Line 139: Change "primitives/" → "signals/plugins/"
- [ ] Add section: "Documentation Updates" with checklist:
  - When adding signal: Update `docs/SIGNALS.md` + `docs/v2/registry/signals.md`
  - When adding finder: Update `docs/FINDERS.md` + `docs/v2/registry/finders.md`
  - When adding language: Update `README.md` language table
  - When changing CLI: Update `README.md` CLI reference

### Fix CHANGELOG.md
- [ ] Check current version in `src/shannon_insight/__init__.py`
- [ ] If version is 0.7.0, update CHANGELOG.md:
  ```markdown
  ## [0.7.0] - 2026-02-XX (Unreleased)

  ### Added
  - ...

  ## [0.4.0] - 2025-02-03
  ```
- [ ] If version is 0.4.0, no change needed (just note discrepancy)

### Fix examples/README.md
- [ ] Remove `--pr` flag (not implemented)
- [ ] Remove `--language go` syntax (auto-detect only)
- [ ] Change `--format json` → `--json`
- [ ] Verify all flags match `shannon-insight --help` output
- [ ] Add note: "See `shannon-insight --help` for all options"

### Fix DASHBOARD.md
- [ ] Add status tags to each feature:
  - "Status: ✅ Implemented" (e.g., Overview screen)
  - "Status: ⚠️ Partial" (e.g., Module violations - data exists but not shown)
  - "Status: ❌ Planned" (e.g., Dependency graph visualization)
- [ ] Add link to `/docs/AUDIT_EXECUTIVE_SUMMARY.md` for gap analysis

---

## Phase 3: Consolidate Duplication (1-2 hours)

### Merge STATUS.md into README.md
- [ ] Copy "Current State" section from STATUS.md to README.md
- [ ] Add "Version History" table to README.md:
  ```markdown
  ## Version History

  | Version | Date | Status | Key Features |
  |---------|------|--------|--------------|
  | 0.7.0 | TBD | In Development | ... |
  | 0.4.0 | 2025-02-03 | Production | 247 tests, 28 finders, 8 languages |
  ```
- [ ] Delete `STATUS.md`

### Move DASHBOARD_ROADMAP.md to v2/BACKLOG.md
- [ ] Copy features from DASHBOARD_ROADMAP.md to `docs/v2/BACKLOG.md` as B8-B15
- [ ] Delete `docs/DASHBOARD_ROADMAP.md`

---

## Phase 4: Create v2 Organization (2-3 hours)

### Create /docs/v2/README.md
```markdown
# Shannon Insight v2 Specification

**Status:** DESIGN (not implemented yet)
**Timeline:** 6-12 months
**Current Phase:** Phase 0 (Infrastructure Hardening)

## Overview

Shannon Insight v2 represents a major architectural evolution with enhanced parsing,
semantic analysis, and architectural metrics. The v2 design is organized into:

- **8 Implementation Phases** (`phases/`) — Step-by-step implementation plan
- **Registry Files** (`registry/`) — Canonical definitions of signals, finders, dimensions
- **Module Specifications** (`modules/`) — Deep-dive into each subsystem

## Implementation Phases

| Phase | Name | Status | Timeline | Description |
|-------|------|--------|----------|-------------|
| 0 | Baseline | ✅ Complete | - | v1 inventory |
| 1 | Deep Parsing | 📋 Design | 3 weeks | Tree-sitter integration |
| 2 | Semantics | 📋 Design | 3 weeks | TF-IDF concepts, role classification |
| 3 | Graph Enrichment | 📋 Design | 4 weeks | DAG depth, NCD clones, author distance |
| 4 | Architecture | 📋 Design | 4 weeks | Modules, Martin metrics, layers |
| 5 | Signal Fusion | 📋 Design | 3 weeks | 6-step fusion pipeline |
| 6 | Enhanced Finders | 📋 Design | 2 weeks | 15 new finders |
| 7 | Persistence v2 | 📋 Design | 2 weeks | TensorSnapshot, signal_history |

**Total Estimated Effort:** ~21 weeks (~5 months)

## Registry Files

- `dimensions.md` — 10 analysis dimensions
- `scales.md` — 4 measurement scales
- `signals.md` — 62 signals (canonical definitions)
- `temporal-operators.md` — 6 temporal operators
- `distance-spaces.md` — 6 graph distance spaces
- `derived-dimensions.md` — Composite metrics
- `finders.md` — 22 finders (registry metadata)
- `composites.md` — Signal fusion formulas

## Module Specifications

- `scanning.md` — Language scanners, tree-sitter integration
- `graph.md` — Dependency graph, algorithms
- `signals.md` — Signal fusion, normalization
- `temporal.md` — Git extraction, churn, cochange
- `semantics.md` — Role classification, concepts
- `architecture.md` — Module detection, Martin metrics
- `persistence.md` — TensorSnapshot, SQLite schema
- `insights.md` — Finders, kernel orchestration

## Migration Roadmap

### v1 → v2 (Breaking Changes)

1. **Signals:** Primitives dataclass → SignalField (typed)
2. **Analyzers:** Hand-rolled topo-sort → graphlib.TopologicalSorter
3. **Store:** Optional fields → Typed Slot[T] with provenance
4. **Finders:** String signal names → Signal enum
5. **Persistence:** Snapshot v1 → TensorSnapshot v2

### Compatibility

- v1 snapshots can be read by v2 (conversion function exists)
- v2 will maintain CLI compatibility (same commands)
- Configuration file format unchanged

## Development Strategy

- One module per session (test-first)
- `make all` after every change
- Phase order strict (acceptance criteria before next phase)
- ~17 sessions estimated for phases 0-7

## See Also

- `/docs/PRODUCT_AUDIT_2026.md` — Complete feature inventory
- `/docs/AUDIT_EXECUTIVE_SUMMARY.md` — Action plan
- `/research/` — Mathematical foundations
```

- [ ] Create `/docs/v2/README.md` with content above
- [ ] Verify all phase links work
- [ ] Verify all registry links work

### Create /docs/v2/modules/ Directory

- [ ] Create `/docs/v2/modules/` directory
- [ ] Create `/docs/v2/modules/README.md`:
  ```markdown
  # Module Specifications

  Deep-dive into each subsystem of Shannon Insight v2.

  - `scanning.md` — Language scanners, tree-sitter integration
  - `graph.md` — Dependency graph, algorithms
  - `signals.md` — Signal fusion, normalization
  - `temporal.md` — Git extraction, churn, cochange
  - `semantics.md` — Role classification, concepts
  - `architecture.md` — Module detection, Martin metrics
  - `persistence.md` — TensorSnapshot, SQLite schema
  - `insights.md` — Finders, kernel orchestration
  ```

**Note:** Actual module files (scanning.md, graph.md, etc.) will be created in Phase 4 (not in this cleanup)

---

## Phase 5: Create New Documentation (12-16 hours)

### Create docs/GETTING_STARTED.md (2-3 hours)
```markdown
# Getting Started with Shannon Insight

**Installation:**
```bash
pip install shannon-codebase-insight
```

**First Analysis:**
```bash
shannon-insight /path/to/your/project
```

**Understanding Output:**

1. Health Score (1-10)
2. Five Mental Models
3. Finding Categories
4. Signal Categories
5. FAQ (10 common questions)

...
```

- [ ] Write full GETTING_STARTED.md (2000+ words)
- [ ] Include screenshots/examples
- [ ] Link from README.md

### Create docs/ARCHITECTURE.md (3-4 hours)
```markdown
# Architecture Overview

**Pipeline Stages:**
1. SCAN
2. PARSE
3. ANALYZE WAVE 1
4. CLEAR CACHE
5. ANALYZE WAVE 2
6. FIND
7. DIAGNOSE
8. DEDUPLICATE & RANK
9. SNAPSHOT

**Analyzer DAG:**
- Diagram showing dependencies
- Store slots
- Signal flow

**Signal Fusion Pipeline:**
- 6-step process
- Tier system
- Normalization

**Persistence:**
- SQLite schema
- TensorSnapshot v2
- Finding lifecycle

...
```

- [ ] Write full ARCHITECTURE.md (3000+ words)
- [ ] Add flowcharts/diagrams
- [ ] Link from README.md

### Create docs/EXTENDING.md (3-4 hours)
```markdown
# Extending Shannon Insight

## Adding a Language Scanner

Step-by-step tutorial with code examples

## Adding a Finder

Step-by-step tutorial with code examples

## Adding a Signal Plugin

Step-by-step tutorial with code examples

## Testing Guide

Unit tests, integration tests, fixtures

## Publishing to PyPI

Release checklist

...
```

- [ ] Write full EXTENDING.md (2500+ words)
- [ ] Include code examples
- [ ] Link from README.md and CONTRIBUTING.md

### Create docs/GLOSSARY.md (1-2 hours)
```markdown
# Glossary

**A**
- **Abstractness:** Ratio of abstract symbols to total symbols in a module
- **Analyzer:** Component that reads from store, produces signals
- **Author Entropy:** Shannon entropy of author contribution distribution

**B**
- **Betweenness Centrality:** Graph metric measuring node's role in shortest paths
- **Blast Radius:** Count of files transitively dependent on a file
- **Bus Factor:** 2^H where H is author entropy (number of critical contributors)

...

**P**
- **PageRank:** Centrality metric from Google's original algorithm
- **Percentile:** Position in distribution (0-1), e.g., "top 5% by PageRank"

...
```

- [ ] Write full GLOSSARY.md (50+ terms)
- [ ] Alphabetize
- [ ] Cross-reference other docs
- [ ] Link from README.md

### Create docs/API.md (2-3 hours)
```markdown
# API Reference

## HTTP Endpoints

### GET /api/state
Returns current analysis state

**Response:**
```json
{
  "health": 7.5,
  "files": { ... },
  ...
}
```

### WebSocket /ws
Real-time updates

**Message Types:**
- `{ type: "complete", state: {...} }`
- `{ type: "progress", message, phase, percent }`
- `{ type: "ping" }`

## Python API

### InsightKernel
Main analysis orchestrator

```python
from shannon_insight.insights.kernel import InsightKernel

kernel = InsightKernel(settings)
result, snapshot = kernel.run(file_metrics, store)
```

### AnalysisStore
Blackboard pattern store

```python
from shannon_insight.insights.store import AnalysisStore

store = AnalysisStore()
store.structural = ...
```

## Stability Matrix

| Component | Status | Notes |
|-----------|--------|-------|
| Signals | STABLE | 62 signals, v1 API locked |
| Finders | STABLE | 22 finders, protocol stable |
| Analyzers | BETA | Protocol stable, implementations may change |
| Dashboard | BETA | API stable, UI evolving |
| v2 Specs | DESIGN | Not implemented yet |

...
```

- [ ] Write full API.md (2000+ words)
- [ ] Document all endpoints
- [ ] Document Python classes
- [ ] Add stability matrix
- [ ] Link from README.md

### Update docs/SIGNALS.md (1 hour)
- [ ] Add header: "This is v1 documentation. For v2 design, see `/docs/v2/registry/signals.md`"
- [ ] Verify all 62 signals documented (currently 28)
- [ ] Add missing signals:
  - `max_nesting`, `impl_gini`, `stub_ratio`, `import_count`
  - `concept_count`, `concept_entropy`, `naming_drift`, `todo_density`, `docstring_coverage`
  - `betweenness`, `in_degree`, `out_degree`, `depth`, `community`
  - `compression_ratio`, `churn_trajectory`, `churn_slope`
  - `author_entropy`, `fix_ratio`, `refactor_ratio`, `wiring_quality`
  - `cohesion`, `coupling`, `main_seq_distance`, `boundary_alignment`, `role_consistency`
  - `coordination_cost`, `knowledge_gini`, `module_bus_factor`, `mean_cognitive_load`

### Update docs/FINDERS.md (30 mins)
- [ ] Add header: "This is v1 documentation. For v2 design, see `/docs/v2/registry/finders.md`"
- [ ] Verify count matches implementation (28 in doc, ~22 in code?)
- [ ] If mismatch, update to actual implementation

---

## Phase 6: Documentation Governance (2-3 hours)

### Create docs/DOCUMENTATION_GUIDE.md
```markdown
# Documentation Guide

## Principles

1. **Single Source of Truth:** Each piece of information documented in exactly one place
2. **DRY (Don't Repeat Yourself):** Link to existing docs rather than duplicating
3. **Version Markers:** Clearly mark v1 vs. v2 vs. research
4. **Update Checklist:** When adding feature, update X, Y, Z

## Where to Document What

| Type | Location | Example |
|------|----------|---------|
| User-facing features | README.md | CLI commands, finding types |
| Configuration | CONFIGURATION.md | All settings, precedence rules |
| Signals/Finders | SIGNALS.md, FINDERS.md | Canonical list (v1) |
| Architecture | ARCHITECTURE.md | Pipeline stages, analyzer DAG |
| Developer setup | CONTRIBUTING.md | Installation, workflow, coding standards |
| Extension guides | EXTENDING.md | Adding scanner, finder, signal |
| v2 design | /docs/v2/ | Phases, registry, modules |
| Research | /research/ | Mathematical foundations, empirical validation |
| Archived | /docs/archived/ | Historical documents |

## When to Archive vs. Delete

**Archive** if:
- Document has historical value
- May be referenced for context
- Represents significant past work

**Delete** if:
- Duplicate of existing doc
- Temporary notes/scratchpad
- No future reference value

## Version Markers

- v1 docs: Add header "This is v1 documentation. For v2 design, see..."
- v2 docs: Add header "This is v2 design specification (not implemented yet)"
- Research docs: Add header "This is research documentation. See /docs/v2/ for implementation spec"

## Update Checklist

When adding a **signal**:
- [ ] Add to `src/shannon_insight/signals/` (implementation)
- [ ] Add to `docs/SIGNALS.md` (v1 reference)
- [ ] Add to `docs/v2/registry/signals.md` (v2 design)
- [ ] Add to README.md signal count

When adding a **finder**:
- [ ] Add to `src/shannon_insight/insights/finders/` (implementation)
- [ ] Add to `docs/FINDERS.md` (v1 reference)
- [ ] Add to `docs/v2/registry/finders.md` (v2 design)
- [ ] Add to README.md finder count

When adding a **language scanner**:
- [ ] Add to `src/shannon_insight/scanning/` (implementation)
- [ ] Add to README.md language table
- [ ] Add to EXTENDING.md example

When changing **CLI**:
- [ ] Update README.md CLI reference table
- [ ] Update examples/README.md if affected
- [ ] Update GETTING_STARTED.md if affected
- [ ] Update `--help` text in CLI code

## Link Checking

- Run `make check-docs` to verify no broken links
- Add new docs to check list
```

- [ ] Create DOCUMENTATION_GUIDE.md
- [ ] Add to CONTRIBUTING.md (link)

### Add Documentation CI Checks (2-3 hours)

Create `.github/workflows/docs-check.yml`:
```yaml
name: Documentation Check

on:
  pull_request:
    paths:
      - 'docs/**'
      - 'README.md'
      - 'CONTRIBUTING.md'
      - 'CHANGELOG.md'

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check for broken internal links
        run: |
          # Script to check markdown links
          python scripts/check_docs_links.py
      - name: Check for orphaned files
        run: |
          # Script to find files not linked anywhere
          python scripts/check_orphaned_docs.py
      - name: Check version consistency
        run: |
          # Compare CHANGELOG.md vs __init__.py
          python scripts/check_version_consistency.py
```

Create scripts:
- [ ] `scripts/check_docs_links.py` — Check markdown links
- [ ] `scripts/check_orphaned_docs.py` — Find unlinked files
- [ ] `scripts/check_version_consistency.py` — Version number check
- [ ] Add to `.github/workflows/docs-check.yml`
- [ ] Test locally before committing

---

## Verification Checklist

### Phase 1: Archive
- [ ] All 16 files moved to `/docs/archived/`
- [ ] `/docs/archived/README.md` exists
- [ ] No broken links after move

### Phase 2: Fix
- [ ] CONTRIBUTING.md module paths corrected
- [ ] CHANGELOG.md version matches `__init__.py`
- [ ] examples/README.md flags match `--help`
- [ ] DASHBOARD.md has status tags

### Phase 3: Consolidate
- [ ] STATUS.md content in README.md
- [ ] STATUS.md deleted
- [ ] DASHBOARD_ROADMAP.md content in v2/BACKLOG.md
- [ ] DASHBOARD_ROADMAP.md deleted

### Phase 4: v2 Organization
- [ ] `/docs/v2/README.md` exists
- [ ] `/docs/v2/modules/` directory exists
- [ ] `/docs/v2/modules/README.md` exists
- [ ] All links in v2/README.md work

### Phase 5: New Docs
- [ ] GETTING_STARTED.md created (2000+ words)
- [ ] ARCHITECTURE.md created (3000+ words)
- [ ] EXTENDING.md created (2500+ words)
- [ ] GLOSSARY.md created (50+ terms)
- [ ] API.md created (2000+ words)
- [ ] SIGNALS.md updated (all 62 signals)
- [ ] FINDERS.md updated (verified count)

### Phase 6: Governance
- [ ] DOCUMENTATION_GUIDE.md created
- [ ] Documentation CI scripts created
- [ ] `.github/workflows/docs-check.yml` created
- [ ] CI passing locally

### Final Checks
- [ ] Run `make check-docs` (if added to Makefile)
- [ ] No broken internal links
- [ ] No orphaned files (all linked from somewhere)
- [ ] Version numbers consistent
- [ ] README.md links to all major docs
- [ ] All new docs linked from README.md or CONTRIBUTING.md

---

## Time Tracking

| Phase | Estimated | Actual | Notes |
|-------|-----------|--------|-------|
| Phase 1: Archive | 1 hour | | |
| Phase 2: Fix | 2-3 hours | | |
| Phase 3: Consolidate | 1-2 hours | | |
| Phase 4: v2 Organization | 2-3 hours | | |
| Phase 5: New Docs | 12-16 hours | | |
| Phase 6: Governance | 2-3 hours | | |
| **TOTAL** | **17-23 hours** | | |

---

## Sign-off

- [ ] All tasks completed
- [ ] All verification checks passed
- [ ] Documentation CI passing
- [ ] Ready for v1.0 release

**Completed by:** _______________
**Date:** _______________
