# Experiments Directory - ARCHIVED

**Status:** These experiments are archived and no longer maintained.

## Background

These 7 experimental scripts were written during early research phases to validate theoretical foundations of the shannon-insight analysis engine. They explored:

1. **Measurement Theory Audit** - Scale classifications (nominal/ordinal/interval/ratio) and fusion strategies
2. **Co-Change Analysis** - Process mining, hidden coupling detection, association rules
3. **Churn Trajectory Analysis** - Dynamical systems classification of file change patterns
4. **Spectral Graph Summary** - Laplacian eigenanalysis, Fiedler partitioning
5. **Category Projection** - File→module functor preservation properties
6. **Algebraic Validation** - Monoid/semiring properties of metric aggregations
7. **Persistent Homology** - Topological data analysis of dependency neighborhoods

## Why Archived?

These experiments import from **obsolete v1 API paths** that no longer exist:
- `shannon_insight.core.scanner_factory` → now `shannon_insight.scanning.factory`
- `shannon_insight.analysis.engine` → now `shannon_insight.insights.kernel`
- `shannon_insight.analysis.models` → scattered across `graph/`, `architecture/`, etc.

The codebase has undergone significant refactoring (v2 migration in progress), and these scripts are no longer compatible.

## Preservation Value

**Do NOT delete.** These experiments:
- Validated mathematical foundations that inform current design decisions
- Contain examples of external research techniques (persistent homology, spectral methods)
- Document historical exploration of rejected approaches
- May be valuable for academic papers or future research

See memory/MEMORY.md for key learnings extracted from these experiments.

## Running Experiments

If you need to run these for research purposes:

### Option 1: Pin to old version
```bash
git checkout <commit-before-v2-migration>
python experiments/01_measurement_audit.py /path/to/codebase
```

### Option 2: Rewrite against current API
Each experiment would need:
- Replace `_bootstrap.load_analysis()` with direct `InsightKernel` usage
- Copy minimal dataclass models locally (FileMetrics, DependencyGraph, etc.)
- Update to new store/blackboard architecture

This is NOT recommended unless absolutely necessary.

## Excluding from Analysis

To prevent these experiments from polluting dependency analysis results, they are excluded via `.shannon-ignore` or config `exclude_patterns`.

If you see experiment files showing up in analysis output, verify your exclusion patterns include `experiments/**`.
