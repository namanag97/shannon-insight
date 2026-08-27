# Shannon Insight Architecture

This directory contains the definitive implementation architecture documentation for the
**Software / Codebase Intelligence and Engineering Analytics** product in this repository.

## Scope boundary

The executable `src/shannon_insight` package is one application-domain analytical product. It is
not the universal enterprise data-and-analytics platform modeled under `research/`. Its complete
machine-readable product, library, component and Python-workbench boundary is maintained at:

- [`research/domain_atlas/universes/application_behavior/bindings/codebase_intelligence/`](../../research/domain_atlas/universes/application_behavior/bindings/codebase_intelligence/)

```text
provider-neutral data / method / runtime / evidence contracts
                              │
                              ▼
      Software / Codebase Intelligence application product
                              │
                              ▼
                 src/shannon_insight (Python)

research/**/*.py = corpus authoring, validation, migration or execution workbench
                   != production platform or semantic authority
```

The relationship tensor is an important product implementation model, not the boundary of all
analytics. A parser is not a product, a graph is not a sovereign domain, an engineering signal is
not a universal business metric, and a finding cannot authorize remediation.

## Core Documents

| Document | Description |
|----------|-------------|
| [TENSOR-ARCHITECTURE.md](./TENSOR-ARCHITECTURE.md) | **Start here.** The 4D tensor model, computation pipeline, and system overview. |
| [MATH-DAG.md](./MATH-DAG.md) | Complete mathematical specification. Every computation with REQUIRES/PRODUCES/FORMULA. |

## The Core Idea

Shannon Insight builds a **4D relationship tensor** that captures how files relate to each other:

```
T ∈ ℝ^(N × N × K × R)

N = files
K = time windows
R = 5 relationship types (IMPORT, COCHANGE, AUTHOR, SEMANTIC, COMBINED)
```

**Everything in this product implementation flows through this tensor:**
- Levels 0-2: Extract data and **populate** the tensor
- Levels 3+: **Slice** the tensor and compute signals

## Related Documentation

### Signal Registry

The complete list of 62 computed signals:

- [v2/registry/signals.md](../v2/registry/signals.md) — Signal names, types, polarities
- [v2/registry/composites.md](../v2/registry/composites.md) — Composite score formulas
- [v2/registry/finders.md](../v2/registry/finders.md) — 22 finder patterns

### Implementation Guides

- [v2/SPEC-REFERENCE.md](../v2/SPEC-REFERENCE.md) — Quick reference for store slots, signals, phases
- [v2/FAILURE-MODES.md](../v2/FAILURE-MODES.md) — Common implementation bugs and how to avoid them
- [v2/infrastructure.md](../v2/infrastructure.md) — Infrastructure patterns (Signal enum, Slot[T], etc.)

### Phase Specifications

Detailed specs for each implementation phase:

| Phase | Document | Description |
|-------|----------|-------------|
| 0 | [phases/phase-0-baseline.md](../v2/phases/phase-0-baseline.md) | Parsing, git extraction, basic signals |
| 1 | [phases/phase-1-deep-parsing.md](../v2/phases/phase-1-deep-parsing.md) | tree-sitter, function analysis |
| 2 | [phases/phase-2-semantics.md](../v2/phases/phase-2-semantics.md) | Concepts, roles, coherence |
| 3 | [phases/phase-3-graph-enrichment.md](../v2/phases/phase-3-graph-enrichment.md) | Graph algorithms, clones |
| 4 | [phases/phase-4-architecture.md](../v2/phases/phase-4-architecture.md) | Modules, Martin metrics |
| 5 | [phases/phase-5-signal-fusion.md](../v2/phases/phase-5-signal-fusion.md) | Normalization, composites |
| 6 | [phases/phase-6-finders.md](../v2/phases/phase-6-finders.md) | Pattern detection |
| 7 | [phases/phase-7-persistence-v2.md](../v2/phases/phase-7-persistence-v2.md) | Storage, snapshots |

## Key Concepts

### The Five Relationship Types

| R | Name | Edge Weight | Meaning |
|---|------|-------------|---------|
| 0 | IMPORT | 1.0 | Static code dependency |
| 1 | COCHANGE | lift | Temporal coupling (files change together) |
| 2 | AUTHOR | Jaccard | Team ownership overlap |
| 3 | SEMANTIC | cosine | Concept similarity |
| 4 | COMBINED | weighted | Fusion of all relationships |

### Slicing Operations

```python
T[:,:,t,r]     # Adjacency matrix at time t, relation r
T[:,:,:,r]     # Temporal evolution of relation r
T[:,:,t,:]     # All relations at time t
```

### Health Score Scale

All health scores use a **1-10 scale**:
- 10 = Excellent health
- 7-9 = Good
- 4-6 = Moderate issues
- 1-3 = Critical problems

### Normalization Tiers

| Tier | File Count | Strategy |
|------|------------|----------|
| ABSOLUTE | < 15 | Raw thresholds only |
| BAYESIAN | 15-50 | Smoothed percentiles |
| FULL | 50+ | Standard percentiles |

## Quick Reference

### Running Analysis

```bash
# Basic analysis
shannon-insight -C /path/to/repo

# With persistence
shannon-insight -C /path/to/repo --save

# JSON output
shannon-insight -C /path/to/repo --json

# Changed files only (fast)
shannon-insight -C /path/to/repo --changed
```

### Key Files

| Path | Purpose |
|------|---------|
| `src/shannon_insight/kernel/` | Pipeline orchestration |
| `src/shannon_insight/graph/` | Graph construction & algorithms |
| `src/shannon_insight/signals/` | Signal computation & fusion |
| `src/shannon_insight/temporal/` | Git analysis, churn, co-change |
| `src/shannon_insight/insights/` | Analyzers, finders, store |
| `src/shannon_insight/persistence/` | SQLite storage, snapshots |

## References

### Academic

- Kolda & Bader, "Tensor Decompositions and Applications", SIAM Review 2009
- Blondel et al., "Fast unfolding of communities in large networks" (Louvain), 2008
- Martin, "Agile Software Development: Principles, Patterns, and Practices", 2002

### Industry

- [CodeScene Code Health](https://codescene.io/docs/guides/technical/code-health.html)
- [SonarQube Metrics](https://docs.sonarsource.com/sonarqube-server/user-guide/code-metrics/)
- [Martin Package Metrics](https://en.wikipedia.org/wiki/Software_package_metrics)

### Libraries

- [TensorLy](http://tensorly.org/) — Tensor decomposition
- [PyData Sparse](https://sparse.pydata.org/) — Sparse n-D arrays
- [NetworkX](https://networkx.org/) — Graph algorithms
