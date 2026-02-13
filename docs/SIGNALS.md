# Signals Reference

Shannon Insight computes 62 signals organized into per-file, per-module, and global tiers. Signals are the raw measurements that finders use to detect structural problems.

## Per-File Signals

### Size & Complexity (#1-7)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 1 | `lines` | Lines of code | int | 0-infinity | neutral | Total lines in the file. Raw size metric. | Scanning (IR1) |
| 2 | `function_count` | Functions | int | 0-infinity | neutral | Number of functions/methods defined. | Scanning (IR1) |
| 3 | `class_count` | Classes/Structs | int | 0-infinity | neutral | Number of classes, structs, or type definitions. | Scanning (IR1) |
| 4 | `max_nesting` | Max nesting depth | int | 0-infinity | higher_is_worse | Deepest nesting level of control flow. Higher nesting correlates with defect density. | Scanning (IR1) |
| 5 | `impl_gini` | Function size inequality | float | 0.0-1.0 | higher_is_worse | Gini coefficient of function body sizes. High values mean uneven implementation -- some functions are much larger than others. | Scanning (IR1) |
| 6 | `stub_ratio` | Stub/empty functions | float | 0.0-1.0 | higher_is_worse | Fraction of functions with trivial bodies (pass, return None, etc.). High values indicate incomplete implementation. | Scanning (IR1) |
| 7 | `import_count` | Import count | int | 0-infinity | neutral | Number of import statements. Proxy for external dependency surface. | Scanning (IR1) |

### Semantics (#8-13)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 8 | `role` | File role | str | UNKNOWN, MODEL, SERVICE, ENTRY_POINT, TEST, CONFIG, UTILITY, INTERFACE | neutral | Detected architectural role based on naming, imports, and content patterns. | SemanticAnalyzer (IR2) |
| 9 | `concept_count` | Concept count | int | 1-infinity | neutral | Number of distinct semantic concepts detected in the file. | SemanticAnalyzer (IR2) |
| 10 | `concept_entropy` | Concept entropy | float | 0.0-infinity | neutral | Shannon entropy of concept distribution. Higher means more evenly spread concepts. | SemanticAnalyzer (IR2) |
| 11 | `naming_drift` | Naming drift | float | 0.0-1.0 | higher_is_worse | How much the filename tokens diverge from the content's actual concepts. High values mean the file is misnamed. | SemanticAnalyzer (IR2) |
| 12 | `todo_density` | TODO density | float | 0.0-1.0 | higher_is_worse | Fraction of lines containing TODO/FIXME/HACK markers. | SemanticAnalyzer (IR2) |
| 13 | `docstring_coverage` | Docstring coverage | float | 0.0-1.0 | higher_is_better | Fraction of functions with documentation. None if not applicable. | SemanticAnalyzer (IR2) |

### Graph Position (#14-26)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 14 | `pagerank` | PageRank centrality | float | 0.0-1.0 | neutral | PageRank score in the dependency graph. Measures structural importance -- high-PageRank files are depended on by many other important files. | StructuralAnalyzer (IR3) |
| 15 | `betweenness` | Betweenness centrality | float | 0.0-1.0 | neutral | Fraction of shortest paths passing through this file. High betweenness means the file is a bridge between communities. | StructuralAnalyzer (IR3) |
| 16 | `in_degree` | Files that import this | int | 0-infinity | neutral | Number of files that directly import this file. | StructuralAnalyzer (IR3) |
| 17 | `out_degree` | Files this imports | int | 0-infinity | neutral | Number of files this file directly imports. | StructuralAnalyzer (IR3) |
| 18 | `blast_radius_size` | Blast radius | int | 0-infinity | higher_is_worse | Number of files transitively reachable from this file via reverse dependency edges. If this file breaks, this many files may be affected. | StructuralAnalyzer (IR3) |
| 19 | `depth` | DAG depth | int | -1-infinity | neutral | BFS distance from entry points in the dependency DAG. -1 means unreachable. | StructuralAnalyzer (IR3) |
| 20 | `is_orphan` | Is orphan | bool | true/false | higher_is_worse | True if no other file imports this file (in_degree=0) and it isn't an entry point, test, or known dynamic-load target. | StructuralAnalyzer (IR3) |
| 21 | `phantom_import_count` | Missing imports | int | 0-infinity | higher_is_worse | Number of imports that resolve to no file in the codebase. Indicates broken or external dependencies. | StructuralAnalyzer (IR3) |
| 22 | `broken_call_count` | Broken calls | int | 0-infinity | higher_is_worse | Number of function calls to non-existent targets. Currently 0 until CALL edges are implemented. | StructuralAnalyzer (IR3) |
| 23 | `community` | Louvain community | int | -1-infinity | neutral | Community assignment from Louvain modularity detection. -1 means unassigned. | StructuralAnalyzer (IR3) |
| 24 | `compression_ratio` | Compression ratio | float | 0.0-1.0 | higher_is_better | `compressed_size / raw_size` using zlib. Lower values mean more repetitive (compressible) content -- an approximation of Kolmogorov complexity. | StructuralAnalyzer (IR3) |
| 25 | `semantic_coherence` | Semantic coherence | float | 0.0-1.0 | higher_is_better | How focused the file's imports are. Measured as intra-community import fraction. Higher means the file imports within its own cluster. | StructuralAnalyzer (IR3) |
| 26 | `cognitive_load` | Cognitive load | float | 0.0-infinity | higher_is_worse | Weighted complexity combining nesting depth, function count, cyclomatic proxies, and parameter counts. Estimates how hard the file is to understand. | StructuralAnalyzer (IR3) |

### Change History (#27-34)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 27 | `total_changes` | Total commits | int | 0-infinity | neutral | Number of git commits that modified this file. | TemporalAnalyzer (IR5t) |
| 28 | `churn_trajectory` | Churn trend | str | STABILIZING, CHURNING, SPIKING, DORMANT | neutral | Classification based on regression slope and coefficient of variation. CHURNING = steady high activity; SPIKING = erratic bursts; STABILIZING = decreasing; DORMANT = inactive. | TemporalAnalyzer (IR5t) |
| 29 | `churn_slope` | Churn slope | float | -infinity-infinity | higher_is_worse | Linear regression slope of change frequency over time windows. Positive = accelerating churn. | TemporalAnalyzer (IR5t) |
| 30 | `churn_cv` | Churn volatility | float | 0.0-infinity | higher_is_worse | Coefficient of variation of change counts across time windows. Higher means more irregular change patterns. | TemporalAnalyzer (IR5t) |
| 31 | `bus_factor` | Bus factor | float | 1.0-infinity | higher_is_better | 2^H where H is Shannon entropy of author contribution distribution. 1.0 = single author; higher = knowledge spread across more people. | TemporalAnalyzer (IR5t) |
| 32 | `author_entropy` | Author diversity | float | 0.0-infinity | neutral | Shannon entropy of per-author commit counts. 0.0 = single author. | TemporalAnalyzer (IR5t) |
| 33 | `fix_ratio` | Bugfix ratio | float | 0.0-1.0 | higher_is_worse | Fraction of commits whose messages contain "fix", "bug", "patch", "hotfix", etc. High values mean the file attracts bugs. | TemporalAnalyzer (IR5t) |
| 34 | `refactor_ratio` | Refactor ratio | float | 0.0-1.0 | neutral | Fraction of commits whose messages contain "refactor", "cleanup", "restructure", etc. | TemporalAnalyzer (IR5t) |

### Computed (#35-36 + extras)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| - | `change_entropy` | Change distribution | float | 0.0-infinity | neutral | Shannon entropy of change distribution across time windows. Uniform distribution = high entropy. | TemporalAnalyzer (IR5t) |
| - | `raw_risk` | Raw risk | float | 0.0-1.0 | higher_is_worse | Pre-percentile weighted risk used by the health Laplacian. Computed from pagerank, blast_radius, cognitive_load, churn, and bus_factor with absolute normalization (divide by max). | SignalFusion (step 2) |
| 35 | `risk_score` | Risk score | float | 0.0-1.0 | higher_is_worse | Percentile-based composite: `structural_risk * complexity * churn_factor * bus_factor_penalty`. Dormant files (total_changes=0) get 0. The primary ranking signal. | SignalFusion (step 5) |
| 36 | `wiring_quality` | Wiring quality | float | 0.0-1.0 | higher_is_better | How well-connected and implemented: `1 - (orphan + stubs + phantoms + broken_calls)`. 1.0 = perfectly wired. | SignalFusion (step 5) |
| - | `file_health_score` | File health | float | 0.0-1.0 | higher_is_better | Composite of risk, wiring, complexity, stubs, and orphan status. The per-file equivalent of codebase_health. | SignalFusion (step 5) |

### Hierarchy Context

| Signal | Type | Description |
|--------|------|-------------|
| `parent_dir` | str | Immediate parent directory (e.g., `src/api`) |
| `module_path` | str | Logical module this file belongs to |
| `dir_depth` | int | Nesting level from root (0 = root) |
| `siblings_count` | int | Other files in the same directory |

### Percentiles

Every numeric per-file signal has a corresponding percentile in `percentiles[signal_name]` (0.0-1.0). Percentiles are computed across all files in the codebase using bisect-based ranking.

**Tier system** (based on file count):
- **ABSOLUTE** (<15 files): No percentiles computed; finders use absolute thresholds only
- **BAYESIAN** (15-50 files): Standard percentile normalization
- **FULL** (50+ files): Standard percentile normalization

**Absolute floors**: To prevent misleading high percentiles on trivial values, certain signals have minimum thresholds below which the percentile is forced to 0:

| Signal | Floor | Rationale |
|--------|-------|-----------|
| `pagerank` | 0.001 | Filter near-zero values |
| `blast_radius_size` | 2 | At least 2 files affected |
| `cognitive_load` | 3.0 | Trivial files only |
| `lines` | 20 | Tiny files only |

## Per-Module Signals

### Martin Metrics (#37-41)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 37 | `cohesion` | Cohesion | float | 0.0-1.0 | higher_is_better | How tightly connected files within the module are. Measured as ratio of intra-module edges to possible edges. | ArchitectureAnalyzer |
| 38 | `coupling` | Coupling | float | 0.0-1.0 | higher_is_worse | Fraction of a module's dependencies that cross module boundaries. | ArchitectureAnalyzer |
| 39 | `instability` | Instability | float | 0.0-1.0 or None | neutral | Martin's I = Ce / (Ca + Ce). 0.0 = maximally stable (many dependents), 1.0 = maximally unstable (depends on many). None if isolated (Ca=Ce=0). | ArchitectureAnalyzer |
| 40 | `abstractness` | Abstractness | float | 0.0-1.0 | neutral | Ratio of abstract/interface files in the module. | ArchitectureAnalyzer |
| 41 | `main_seq_distance` | Main sequence distance | float | 0.0-1.0 | higher_is_worse | Distance from the Martin main sequence line (A + I = 1). High distance means the module is in the "zone of pain" (concrete + stable) or "zone of uselessness" (abstract + unstable). | ArchitectureAnalyzer |

### Boundary Analysis (#42-44)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 42 | `boundary_alignment` | Boundary alignment | float | 0.0-1.0 | higher_is_better | How well the module's directory boundary matches its actual dependency community. 1.0 = directory perfectly matches Louvain community. | ArchitectureAnalyzer |
| 43 | `layer_violation_count` | Layer violations | int | 0-infinity | higher_is_worse | Number of import edges within this module that violate the detected layer order. | ArchitectureAnalyzer |
| 44 | `role_consistency` | Role consistency | float | 0.0-1.0 | higher_is_better | How uniform the file roles are within this module. 1.0 = all files have the same role. | ArchitectureAnalyzer |

### Module Temporal (#45-48)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 45 | `velocity` | Velocity | float | 0.0-infinity | neutral | Commits per week touching any file in this module. Measures development activity. | SignalFusion (step 4) |
| 46 | `coordination_cost` | Coordination cost | float | 0.0-infinity | higher_is_worse | Mean distinct authors per commit touching this module. Higher means more people need to coordinate. | SignalFusion (step 4) |
| 47 | `knowledge_gini` | Knowledge Gini | float | 0.0-1.0 | higher_is_worse | Gini coefficient of per-author commit counts in this module. High values mean knowledge is concentrated in few people. | SignalFusion (step 4) |
| 48 | `module_bus_factor` | Module bus factor | float | 1.0-infinity | higher_is_better | Minimum bus_factor among high-centrality files (top 25% by PageRank) in this module. Falls back to mean if no high-centrality files. | SignalFusion (step 4) |

### Aggregated (#49-51)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 49 | `mean_cognitive_load` | Mean cognitive load | float | 0.0-infinity | higher_is_worse | Average cognitive_load across files in this module. | SignalFusion (step 1) |
| 50 | `file_count` | File count | int | 0-infinity | neutral | Number of files in this module. | SignalFusion (step 1) |
| 51 | `health_score` | Module health | float | 0.0-1.0 | higher_is_better | Composite: cohesion, coupling, main_seq_distance, boundary_alignment, role_consistency, stub_ratio. | SignalFusion (step 5) |

## Global Signals

### Graph Structure (#52-56)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 52 | `modularity` | Modularity | float | -0.5-1.0 | higher_is_better | Louvain modularity score of the dependency graph. Higher means well-separated communities. | StructuralAnalyzer |
| 53 | `fiedler_value` | Fiedler value | float | 0.0-infinity | higher_is_better | Second-smallest eigenvalue of the graph Laplacian. Measures algebraic connectivity -- 0 means disconnected components, higher means tightly connected. | SpectralAnalyzer |
| 54 | `spectral_gap` | Spectral gap | float | 0.0-infinity | higher_is_better | Difference between the first and second eigenvalues of the Laplacian. Larger gap means clearer community structure. | SpectralAnalyzer |
| 55 | `cycle_count` | Cycle count | int | 0-infinity | higher_is_worse | Number of strongly connected components with 2+ nodes (dependency cycles). | StructuralAnalyzer |
| 56 | `centrality_gini` | Centrality Gini | float | 0.0-1.0 | higher_is_worse | Gini coefficient of PageRank distribution. High values mean a few files dominate the dependency graph. | StructuralAnalyzer |

### Wiring Quality (#57-59)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 57 | `orphan_ratio` | Orphan ratio | float | 0.0-1.0 | higher_is_worse | Fraction of files with zero importers (excluding entry points and tests). | SignalFusion (step 1) |
| 58 | `phantom_ratio` | Phantom ratio | float | 0.0-1.0 | higher_is_worse | Fraction of import statements that resolve to no file. | SignalFusion (step 1) |
| 59 | `glue_deficit` | Glue deficit | float | 0.0-1.0 | higher_is_worse | Whether the codebase has enough bridge/orchestration files. `1 - glue_files / expected_glue` where expected_glue = sqrt(num_modules). | SignalFusion (step 1) |

### Derived Signals

| Signal | Type | Range | Polarity | Description | Source |
|--------|------|-------|----------|-------------|--------|
| `clone_ratio` | float | 0.0-1.0 | higher_is_worse | Fraction of files that have a detected clone pair (NCD < 0.3). | Phase 3 clone detection |
| `violation_rate` | float | 0.0-1.0 | higher_is_worse | Fraction of cross-module dependency edges that violate the detected layer order. | Phase 4 architecture |
| `conway_alignment` | float | 0.0-1.0 | higher_is_better | How well team boundaries match module boundaries. 1.0 = perfect alignment. Computed from author overlap between structurally-coupled modules. | Phase 3 author distances |
| `team_size` | int | 1-infinity | neutral | Number of distinct git authors across the codebase. | Phase 3 git history |

### Composites (#60-62)

| # | Signal | Label | Type | Range | Polarity | Description | Source |
|---|--------|-------|------|-------|----------|-------------|--------|
| 60 | `wiring_score` | Wiring score | float | 0.0-1.0 | higher_is_better | `1 - (0.25*orphan_ratio + 0.25*phantom_ratio + 0.20*glue_deficit + 0.15*mean_stub_ratio + 0.15*clone_ratio)`. Codebase-level code completeness. | SignalFusion (step 5) |
| 61 | `architecture_health` | Architecture health | float | 0.0-1.0 | higher_is_better | `0.25*(1-violation_rate) + 0.20*mean(cohesion) + 0.20*(1-mean(coupling)) + 0.20*(1-mean(main_seq_distance)) + 0.15*mean(boundary_alignment)`. | SignalFusion (step 5) |
| - | `team_risk` | Team risk | float | 0.0-1.0 | higher_is_worse | `1 - (0.30*min_bus/3 + 0.25*(1-max_gini) + 0.25*(1-mean_coord/5) + 0.20*conway)`. Organizational risk composite. | SignalFusion (step 5) |
| 62 | `codebase_health` | Codebase health | float | 0.0-1.0 | higher_is_better | `0.30*architecture_health + 0.30*wiring_score + 0.20*(bus_factor/team_size) + 0.20*modularity`. The master metric displayed as 1-10. | SignalFusion (step 5) |

### Health Laplacian

| Signal | Type | Range | Polarity | Description |
|--------|------|-------|----------|-------------|
| `delta_h` (per-file) | float | -1.0-1.0 | higher_is_worse | `raw_risk(file) - mean(raw_risk(neighbors))`. Positive means the file is worse than its graph neighborhood. Values > 0.4 trigger the `weak_link` finder. Orphans get delta_h = 0. |

## Signal Fusion Pipeline

The 6-step fusion pipeline transforms raw measurements into composite scores:

### Step 1: Collect

Gathers signals from all store slots (scanning, graph, temporal, semantics, architecture) into a unified `SignalField` with per-file, per-directory, per-module, and global tiers.

### Step 2: Raw Risk

Computes pre-percentile `raw_risk` for each file using absolute normalization (divide by max value across codebase):

```
raw_risk = 0.25 * (pagerank/max) + 0.20 * (blast_radius/max)
         + 0.20 * (cognitive_load/max) + 0.20 * instability_factor
         + 0.15 * (1 - bus_factor/max)
```

Where `instability_factor` = 1.0 if churn trajectory is CHURNING or SPIKING, else 0.3.

### Step 3: Normalize

Computes percentile rank for each numeric signal across all files. Applies absolute floors to prevent misleading percentiles on trivial values. Skipped for codebases with fewer than 15 files (ABSOLUTE tier).

### Step 4: Module Temporal

Aggregates temporal signals to module level: velocity, coordination cost, knowledge Gini, and module bus factor. Requires percentiles from step 3 to identify high-centrality files.

### Step 5: Composites

Computes `risk_score`, `wiring_quality`, `file_health_score` (per-file), `health_score` (per-module), and `wiring_score`, `architecture_health`, `team_risk`, `codebase_health` (global).

`risk_score` uses multiplicative fusion -- all factors must be present for high risk. Dormant files (zero changes) automatically get risk_score = 0.

### Step 6: Health Laplacian

Computes `delta_h` for each file: the difference between the file's raw_risk and the mean raw_risk of its graph neighbors. Identifies files that are worse than their surroundings -- structural weak links.

Uses `raw_risk` (step 2) rather than `risk_score` (step 5) to avoid circularity: percentile-normalized values would compress the range and hide relative differences.

## Display Scale

All composite scores are stored internally as 0-1 floats but displayed on a 1-10 scale for user readability:

```
display_value = round(internal_value * 9 + 1, 1)
```

| Internal | Display | Label |
|----------|---------|-------|
| 0.78-1.0 | 8.0-10.0 | Healthy |
| 0.56-0.77 | 6.0-7.9 | Moderate |
| 0.33-0.55 | 4.0-5.9 | At Risk |
| 0.0-0.32 | 1.0-3.9 | Critical |
