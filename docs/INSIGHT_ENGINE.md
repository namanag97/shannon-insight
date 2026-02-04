# Insight Engine

The insight engine is the `shannon-insight . insights` command. It cross-references structural dependencies, git history, per-file quality signals, and spectral graph properties to produce prioritized, evidence-backed findings.

## Architecture

The engine uses a **blackboard pattern**. All analyzers write to a shared `AnalysisStore`. All finders read from it. The kernel orchestrates execution order.

```
Scanner + GitExtractor → AnalysisStore → Analyzers fill it → Finders read it → Findings
```

### Why Blackboard?

- Analyzers are independent — structural analysis doesn't need to know about git
- Finders can combine signals freely — a "high risk hub" finder reads PageRank from structural + churn from temporal
- Graceful degradation — if git isn't available, temporal stays `None` and finders requiring it are skipped

### Execution Flow

```
1. Kernel scans files (ScannerFactory)
2. Kernel creates AnalysisStore
3. Kernel topologically sorts analyzers by requires/provides
4. For each analyzer:
   - If analyzer.requires ⊆ store.available → run it
   - Otherwise → skip
5. For each finder:
   - If finder.requires ⊆ store.available → collect findings
   - Otherwise → skip
6. Sort findings by severity, cap at max_findings
```

## Signal Categories

### Structural (from existing AnalysisEngine)

- Dependency graph (import resolution)
- PageRank (importance via random walk)
- Betweenness centrality (bridge nodes)
- Blast radius (transitive closure on reverse graph)
- Strongly connected components (Tarjan)
- Louvain community detection (modularity optimization)
- Boundary alignment (declared directories vs discovered communities)

### Per-File (from existing primitive plugins)

- Compression complexity (Kolmogorov via zlib)
- Network centrality (PageRank on dependency graph)
- Churn volatility (modification timestamp)
- Semantic coherence (identifier clustering entropy)
- Cognitive load (concepts × complexity × nesting × Gini)

### Temporal (git history)

- **Co-change matrix**: for every pair of files, how often they appear in the same commit. Metrics:
  - **Confidence**: P(B changed | A changed) — directional
  - **Lift**: observed co-change / expected under independence — higher means stronger signal
  - Filters: commits with >50 files excluded (bulk reformats), minimum 2 co-changes required
- **Churn trajectories**: per-file time series of changes per window (default 4 weeks). Classified as:
  - `dormant` — ≤1 total change
  - `stabilizing` — negative linear regression slope
  - `spiking` — positive slope + high coefficient of variation
  - `churning` — high variance, no trend

### Spectral (Laplacian eigenvalues)

- Build undirected adjacency from the dependency graph
- Compute graph Laplacian: L = D - A
- Eigendecomposition via `numpy.linalg.eigvalsh`
- **Fiedler value** (2nd smallest eigenvalue): measures algebraic connectivity. Low = codebase has bottleneck connections. High = well-connected.
- **Number of components**: from zero eigenvalue count
- **Spectral gap**: ratio of 2nd to 3rd eigenvalue — measures separation strength

For disconnected graphs, Fiedler value is computed on the largest connected component.

## Finding Types

### 1. High Risk Hub (severity base: 1.0)

**Trigger**: file is in the top 10% on 2+ of: PageRank, blast radius, cognitive load, churn.

**Why it matters**: these files are where bugs are most expensive. A change here affects the most code, and the file itself is hard to reason about.

**Contextual suggestions**:
- Hub by connectivity → "N files depend on this, blast radius M. Split into focused modules or introduce interfaces."
- Hub by complexity + churn → "Complex and frequently modified. Extract the parts that change most into separate modules."

### 2. Hidden Coupling (severity base: 0.9)

**Trigger**: co-change lift > 2.0 AND confidence > 50% AND no structural dependency between the pair.

**Why it matters**: these files have an invisible contract. When someone changes one, they need to know to change the other — but nothing in the code tells them that.

**Filters**: `__init__.py` pairs excluded (noise from package-level changes).

### 3. God File (severity base: 0.8)

**Trigger**: cognitive load top 10% AND semantic coherence bottom 20%.

**Why it matters**: a file that's both complex and unfocused is the hardest to maintain. Low coherence means the names suggest multiple unrelated concerns — it's doing too many jobs.

### 4. Unstable File (severity base: 0.7)

**Trigger**: churn trajectory is "churning" or "spiking" AND total changes above median.

**Why it matters**: a file that keeps changing without stabilizing usually has a root cause — unclear requirements, leaky abstraction, or missing tests.

### 5. Boundary Mismatch (severity base: 0.6)

**Trigger**: boundary alignment < 0.7 AND module has > 2 files AND there are actionable relocation suggestions.

**Why it matters**: when a directory's files are more connected to other directories than to each other, the package structure doesn't match reality. Developers look in the wrong place for related code.

### 6. Dead Dependency (severity base: 0.4)

**Trigger**: structural dependency exists (import) but co-change count = 0 AND both files have been changed ≥1 time AND history has ≥50 commits.

**Why it matters**: an import that never causes correlated changes might be unused or vestigial. Removing it simplifies the dependency graph.

## Severity Formula

```
final_severity = finder.BASE_SEVERITY × individual_strength
```

Where `individual_strength` depends on the finder:
- Percentile-based finders (high_risk_hub, god_file, unstable_file): average triggering percentile / 100
- Co-change finders (hidden_coupling): (lift/10 + max_confidence) / 2
- Boundary mismatch: 1.0 - alignment score
- Dead dependency: fixed at 0.7

All values clamped to [0.1, 1.0].

## Percentile Computation

All percentile-based thresholds use `compute_percentiles()` from `insights/ranking.py`:

```python
def compute_percentiles(values: Dict[str, float]) -> Dict[str, float]:
    """Given {file: value}, return {file: percentile 0-100}."""
    sorted_vals = sorted(values.values())
    rank = bisect_left(sorted_vals, val)
    percentile = (rank / n) * 100
```

This means percentiles are relative to *this codebase*, not absolute. A file in the 95th percentile for cognitive load is more complex than 95% of the *other files in the same project*.

## Temporal Extraction

Git history is extracted via subprocess (`git log --format='%H|%at|%ae' --name-only`). The parser handles:

- Merge commits (no files, header immediately followed by next commit header)
- Monorepo paths (files filtered to analyzed directory)
- Missing git (returns `None`, temporal analysis skipped)

Co-change matrix uses association rule mining concepts:
- **Support**: how often a pair appears together
- **Confidence**: P(B|A) — directional probability
- **Lift**: observed / expected — >1 means positive association

## File Structure

```
temporal/
├── models.py          # GitHistory, Commit, CoChangeMatrix, ChurnSeries, SpectralSummary
├── git_extractor.py   # subprocess git log → GitHistory
├── cochange.py        # GitHistory → CoChangeMatrix
└── churn.py           # GitHistory → Dict[str, ChurnSeries]

insights/
├── models.py          # Finding, Evidence, InsightResult
├── store.py           # AnalysisStore (the blackboard)
├── protocols.py       # Analyzer and Finder protocol classes
├── kernel.py          # InsightKernel orchestrator
├── ranking.py         # percentile computation
├── analyzers/
│   ├── structural.py  # wraps AnalysisEngine
│   ├── per_file.py    # wraps PrimitiveExtractor
│   ├── temporal.py    # wraps GitExtractor + co-change + churn
│   └── spectral.py    # Laplacian eigendecomposition
└── finders/
    ├── high_risk_hub.py
    ├── hidden_coupling.py
    ├── god_file.py
    ├── unstable_file.py
    ├── boundary_mismatch.py
    └── dead_dependency.py
```

## Edge Cases

1. **No git** — GitExtractor returns `None`, temporal signals stay `None`, finders requiring "temporal" are skipped
2. **Young repo (<10 commits)** — TemporalAnalyzer skips, warning in output
3. **Tiny codebase (<5 files)** — finders require minimum 5 files to produce findings
4. **Bulk commits (>50 files)** — filtered from co-change analysis
5. **`__init__.py` co-change** — HiddenCouplingFinder explicitly filters these pairs
6. **Disconnected graph** — SpectralAnalyzer computes Fiedler on largest connected component
7. **No numpy** — SpectralAnalyzer catches ImportError and skips
