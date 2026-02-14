# Shannon Insight

**Multi-signal codebase analysis using information theory, graph algorithms, and spectral analysis.**

Shannon Insight treats source code as a measurable physical system. It computes 62 quantitative signals across 8 dimensions for every file, module, and codebase -- then surfaces actionable findings backed by mathematical evidence, not heuristics.

```
pip install shannon-codebase-insight
shannon-insight /path/to/your/project
```

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [How It Works](#how-it-works)
4. [The Math Behind It](#the-math-behind-it)
5. [Signals Reference](#signals-reference)
6. [Finders Reference](#finders-reference)
7. [Use Cases](#use-cases)
8. [CLI Reference](#cli-reference)
9. [Dashboard Guide](#dashboard-guide)
10. [FAQ](#faq)

---

## Introduction

### The Problem: Why Traditional Code Analysis Falls Short

Traditional static analysis tools operate in a single dimension. Linters catch style violations. Complexity analyzers count cyclomatic paths. Coverage tools measure test reach. Each tool sees one facet of code health while missing the systemic picture.

Consider a file that passes every lint rule and has moderate complexity -- but is imported by 47 other files, has been modified 200 times in 6 months, and is maintained by a single developer. No single-dimension tool flags this. Shannon Insight does.

Real codebase problems are **multi-dimensional**:

- A file can be well-formatted yet architecturally dangerous (high centrality + low bus factor).
- A module can have clean code yet eroded boundaries (high coupling + misaligned community structure).
- A pair of files can have no structural dependency yet always change together (hidden coupling via co-change).

### Our Approach: Information Theory Meets Software Engineering

Shannon Insight is named after Claude Shannon, the father of information theory. The core insight is that **code is a signal** -- it carries information in its structure, its dependencies, its history, and its authorship patterns. By measuring code the same way we measure signals in communication systems, we reveal properties invisible to rule-based tools.

The analysis operates across **8 irreducible dimensions**:

| Dimension | Question | Example Signals |
|-----------|----------|-----------------|
| **D1: Size** | How much code? | Lines, function count, class count |
| **D2: Shape** | How is it structured? | Max nesting, implementation Gini coefficient |
| **D3: Naming** | What concepts does it contain? | Concept entropy, naming drift, role classification |
| **D4: Reference** | What depends on what? | PageRank, betweenness, blast radius, community |
| **D5: Information** | How dense and ordered? | Compression ratio, semantic coherence, cognitive load |
| **D6: Change** | How does it evolve? | Churn trajectory, churn slope, coefficient of variation |
| **D7: Authorship** | Who touches it? | Bus factor, author entropy, knowledge Gini |
| **D8: Intent** | Why was it changed? | Fix ratio, refactor ratio |

These 8 dimensions are irreducible -- none can be derived from the others. Size tells you nothing about authorship. Change frequency tells you nothing about dependency structure. Each requires a separate data source and a separate mathematical treatment.

### Key Benefits

**Find issues missed by other tools.** Shannon Insight detects 22 distinct finding types, including hidden coupling (files that co-change but have no structural dependency), knowledge silos (critical files maintained by a single developer), weak links (files that drag down their healthy neighborhood), and Conway violations (team boundaries misaligned with architectural boundaries).

**Mathematical rigor, not heuristics.** Every finding is backed by quantitative signals with defined formulas, explicit thresholds, and computed confidence scores. When Shannon Insight says a file is a "high risk hub," it provides the PageRank percentile, blast radius, cognitive load score, and churn trajectory that triggered the finding.

**Scales from 5 files to 10,000+.** A three-tier degradation system adapts analysis to codebase size. Small codebases (under 15 files) get absolute thresholds. Medium codebases (15-50 files) get Bayesian-regularized percentiles. Large codebases (50+ files) get full percentile normalization with composite scores.

**8 languages supported.** Python, Go, TypeScript, JavaScript, Java, Rust, Ruby, and C/C++. Language-specific scanners extract syntax trees while a universal normalizer produces language-agnostic analysis.

**No server required.** `pip install` and run. All analysis happens locally. Results output as rich terminal display or JSON for CI integration.

---

## Quick Start

### Installation

```bash
pip install shannon-codebase-insight
```

For enhanced parsing with tree-sitter (recommended):

```bash
pip install shannon-codebase-insight[parsing]
```

### First Analysis

```bash
# Analyze the current directory
shannon-insight .

# Analyze a specific project
shannon-insight /path/to/project

# Analyze with full detail
shannon-insight /path/to/project --verbose
```

### Example Output

```
Shannon Insight v1.x - Multi-Signal Codebase Quality Analyzer

Scanned 127 files across 8 modules in 2.3s

Codebase Health: 6.4/10

Top Findings:
  CRITICAL  HIGH_RISK_HUB      src/core/engine.py
            PageRank p99, blast radius 43, cognitive load p95
            Suggestion: Split responsibilities. Pair-program to spread knowledge.

  HIGH      KNOWLEDGE_SILO     src/auth/session.py
            Bus factor: 1.0, PageRank p82
            Suggestion: Pair-program or rotate ownership.

  HIGH      HIDDEN_COUPLING    src/api/routes.py <-> src/db/queries.py
            Co-change lift: 4.2, no structural dependency
            Suggestion: Extract shared concept or make dependency explicit.

  MEDIUM    HOLLOW_CODE        src/utils/helpers.py
            Stub ratio: 0.67, impl Gini: 0.71
            Suggestion: Implement the stub functions.

  MEDIUM    ZONE_OF_PAIN       src/models/
            Abstractness: 0.12, Instability: 0.08
            Suggestion: Extract interfaces or reduce dependents.

5 findings (1 critical, 2 high, 2 medium)
```

### Save History and Track Trends

```bash
# Save a snapshot for trend tracking
shannon-insight /path/to/project --save

# Compare with previous snapshot
shannon-insight diff /path/to/project

# View health trends over time
shannon-insight health /path/to/project
```

### CI Integration

```bash
# Fail the build if any high-severity findings exist
shannon-insight /path/to/project --json --fail-on high

# Output JSON for programmatic consumption
shannon-insight /path/to/project --json
```

---

## How It Works

Shannon Insight processes a codebase through a six-stage pipeline. Each stage produces intermediate representations (IRs) that feed the next, building progressively richer understanding.

```
STAGE 0: TRIAGE
    Detect file count -> tier (ABSOLUTE / BAYESIAN / FULL)
    Detect languages -> load appropriate parsers
    Detect .git -> temporal analysis ON/OFF
    Count authors -> social analysis ON/OFF

STAGE 1: PARSE (per-language, parallel)
    tree-sitter (if installed) -> FileSyntax
    regex fallback             -> FileSyntax (basic)

STAGE 2: ANALYZE (two parallel spines)
    STRUCTURAL SPINE              TEMPORAL SPINE
    scanning/ (IR0->IR1)          temporal/ (git -> IR5t)
        |                              |
    semantics/ (IR2)                   |
        |                              |
    graph/ (IR3) <---------------------+  (co-change enrichment)
        |
    architecture/ (IR4)

STAGE 3: FUSE (always runs last)
    signals/ (IR5s): collect -> normalize -> composites -> health Laplacian

STAGE 4: FIND
    22 finders read from the unified SignalField
    Hotspot filter: suppress findings on stable code
    Group by scope, rank by severity x confidence

STAGE 5: OUTPUT
    JSON (primary), CLI rich terminal, --save -> SQLite persistence
```

### Phase 0: Triage and Baseline Scanning

The pipeline begins by scanning the source tree. Shannon Insight identifies source files across 8 supported languages, excluding binary files, vendored dependencies, and build artifacts (95 built-in exclude patterns).

**Triage** determines the analysis tier based on file count:
- **ABSOLUTE** (fewer than 15 files): No percentile normalization. Use absolute thresholds only. Composite scores are not computed.
- **BAYESIAN** (15-50 files): Bayesian-regularized percentiles with priors from industry datasets. Composites computed with confidence qualifiers.
- **FULL** (50+ files): Standard percentile normalization. Full composite scores.

The triage tier ensures meaningful analysis at any scale -- a 10-file project gets direct threshold comparisons, not statistically meaningless percentile rankings.

### Phase 1: Deep Parsing

Each source file is parsed into a language-agnostic `FileSyntax` representation. If tree-sitter grammars are installed, parsing uses full AST analysis. Otherwise, regex-based scanners provide a basic fallback.

The `FileSyntax` model captures:
- **Functions**: Name, parameters, body token count, nesting depth, call targets, decorators
- **Classes**: Name, base classes, methods, fields, abstractness markers
- **Imports**: Source module, imported names, resolved file path (or `null` for phantom imports)

This phase produces the first signals: `lines`, `function_count`, `class_count`, `max_nesting`, `impl_gini`, `stub_ratio`, and `import_count`.

### Phase 2: Semantic Analysis

The semantic layer classifies each file's **role** and extracts **concept clusters**.

**Role classification** uses a deterministic decision tree evaluated top-to-bottom (first match wins):

```
TEST        <- path matches test_*, *_test, tests/
ENTRY_POINT <- has __main__ guard or CLI decorators
INTERFACE   <- has ABC, Protocol, or @abstractmethod
CONSTANT    <- all identifiers are UPPER_SNAKE_CASE
EXCEPTION   <- majority of classes raise custom exceptions
MODEL       <- classes are field-heavy (>3 fields, few methods)
CLI         <- has CLI decorators (@app.route, typer, argparse)
SERVICE     <- has HTTP decorators or stateful classes with methods
MIGRATION   <- has migration patterns (alembic, django)
UTILITY     <- all top-level definitions are functions (no classes)
CONFIG      <- has only re-exports or __all__
UNKNOWN     <- default
```

**Concept extraction** operates in three tiers based on file complexity:
- **Tier 1** (fewer than 3 functions): Single concept based on role.
- **Tier 2** (3-9 functions): Keyword frequency extraction.
- **Tier 3** (10+ functions, 20+ unique identifiers): Full TF-IDF on identifiers with Louvain community detection on the token co-occurrence graph.

This phase produces: `role`, `concept_count`, `concept_entropy`, `naming_drift`, `todo_density`, and `docstring_coverage`.

### Phase 3: Graph Construction and Enrichment

Import declarations from Phase 1 are resolved into a directed dependency graph. Each edge represents "file A imports file B." Unresolved imports (phantom imports) are tracked separately.

On this graph, Shannon Insight computes:

- **PageRank**: Importance in the dependency network (damping factor d=0.85, power iteration convergence at 1e-6)
- **Betweenness centrality**: Bridge detection via Brandes' algorithm
- **Blast radius**: Transitive reverse closure via BFS -- how many files are affected if this file changes
- **Tarjan SCC**: Cycle detection (strongly connected components with more than one node)
- **Louvain communities**: Natural clustering of files by dependency structure
- **DAG depth**: Shortest path from entry points via BFS (depth=-1 means unreachable/orphan)
- **Spectral analysis**: Graph Laplacian eigenvalues via Lanczos algorithm
- **NCD clone detection**: Normalized Compression Distance between file pairs to find copy-paste clones (threshold: NCD < 0.3)
- **Author distance (G5)**: Weighted Jaccard distance between author distributions for each file pair

This phase produces signals including `pagerank`, `betweenness`, `in_degree`, `out_degree`, `blast_radius_size`, `depth`, `is_orphan`, `phantom_import_count`, `community`, `compression_ratio`, `cognitive_load`, and global signals like `modularity`, `fiedler_value`, `cycle_count`, `centrality_gini`, `orphan_ratio`, `phantom_ratio`, and `glue_deficit`.

### Phase 4: Architecture Detection

Shannon Insight infers module boundaries and architectural layers without configuration.

**Module detection**: Each directory containing source files is a candidate module. The algorithm selects the directory depth where most directories contain 3-15 files. For flat projects (all files in one directory), Louvain communities from Phase 3 serve as synthetic modules.

**Martin metrics** are computed per module:
- **Instability**: I = Ce / (Ca + Ce), where Ca = afferent (incoming) coupling and Ce = efferent (outgoing) coupling. `None` if the module is isolated (Ca=Ce=0).
- **Abstractness**: A = abstract_symbols / total_symbols (abstract classes, Protocol classes, @abstractmethod decorators).
- **Main sequence distance**: D = |A + I - 1|. D=0 is the ideal balance. Low A + low I = "zone of pain" (concrete and hard to change). High A + high I = "zone of uselessness."

**Layer inference**: The module-level dependency graph is topologically sorted. Modules with no dependencies become the foundation layer (depth 0). Entry-point modules become the top layer. Backward edges (lower layer importing upper layer) and skip edges (skipping intermediate layers) are flagged as violations.

### Phase 5: Signal Fusion

All raw signals from Phases 0-4 are collected into a unified `SignalField` -- one data structure containing every signal for every file, module, and the codebase as a whole.

The fusion pipeline executes in strict order:

1. **Collect** raw signals from all analysis store slots
2. **Compute `raw_risk`** per file (pre-percentile weighted sum, used by health Laplacian)
3. **Normalize** to percentiles (tiered: ABSOLUTE skips this, BAYESIAN uses Beta-posterior, FULL uses standard percentile)
4. **Aggregate module temporal signals** (velocity, coordination cost, knowledge Gini, module bus factor)
5. **Compute composite scores** (risk_score, wiring_quality, health_score, wiring_score, architecture_health, team_risk, codebase_health)
6. **Compute health Laplacian** (delta_h per file: how much worse is this file than its graph neighbors?)

**Composite scores** are computed on a [0, 1] internal scale and displayed on a **1-10 scale** (multiplied by 10). A codebase_health of 6.4/10 means the internal value is 0.64.

### Phase 6: Finding Detection

22 finders evaluate conditions against the `SignalField`. Each finder declares which signals it requires and gracefully skips if those signals are unavailable.

**Hotspot filtering**: For temporal-aware findings (HIGH_RISK_HUB, UNSTABLE_FILE, KNOWLEDGE_SILO, BUG_ATTRACTOR, REVIEW_BLINDSPOT, WEAK_LINK), the finder only fires if the file's `total_changes` exceeds the median across the codebase. This prevents flagging complex-but-stable files that nobody is working on.

**Confidence scoring**: Each finder computes confidence in [0, 1] using the margin formula -- how far above (or below) the threshold each triggering condition is. Higher margins mean higher confidence.

Findings are grouped by scope (FILE, FILE_PAIR, MODULE, MODULE_PAIR, CODEBASE) and ranked by severity multiplied by confidence.

### Phase 7: Persistence and Trends

When run with `--save`, Shannon Insight stores the full `SignalField` in a SQLite database (`.shannon/history.db`). Subsequent runs can compare snapshots to detect trends:

- **Signal time series**: Track any signal over time (delta, velocity, acceleration, trajectory, trend)
- **Finding lifecycle**: Track whether findings are new, persisting, resolved, or regression
- **Debt velocity**: Net change in findings between snapshots (|new| - |resolved|)

This enables the CHRONIC_PROBLEM finder (same finding persists across 3+ snapshots) and ARCHITECTURE_EROSION finder (violation rate increasing over time).

---

## The Math Behind It

Shannon Insight's mathematical foundation draws from four domains: information theory, graph theory, spectral analysis, and temporal statistics. This section explains each formula with intuitive meaning and worked examples.

### Information Theory

#### Shannon Entropy

The foundational measure of uncertainty in a probability distribution.

```
H = -SUM p(x) * log2(p(x))
```

Where p(x) is the probability of each outcome x, and the sum is over all possible outcomes.

**Intuition**: Entropy measures surprise. If a file is written by one author, there is no surprise in who wrote any given line -- entropy is 0. If a file has 4 equally-contributing authors, every line could be by anyone -- entropy is log2(4) = 2.0 bits.

**Application in Shannon Insight**:

*Author entropy* (signal #32): H is computed over the distribution of commits per author for each file. If author A wrote 80% of commits and author B wrote 20%:

```
H = -(0.8 * log2(0.8) + 0.2 * log2(0.2))
  = -(0.8 * (-0.322) + 0.2 * (-2.322))
  = -((-0.258) + (-0.464))
  = 0.722 bits
```

*Bus factor* (signal #31): Derived from author entropy as `2^H`. This converts entropy into an "effective author count":

```
bus_factor = 2^0.722 = 1.65
```

Meaning: this file effectively has 1.65 authors. If the primary contributor left, there is partial (but not full) knowledge coverage by the secondary contributor.

*Concept entropy* (signal #10): H is computed over concept cluster weights. If a file has three concept clusters with weights 0.4, 0.3, 0.3:

```
H = -(0.4 * log2(0.4) + 0.3 * log2(0.3) + 0.3 * log2(0.3))
  = -(0.4 * (-1.322) + 0.3 * (-1.737) + 0.3 * (-1.737))
  = -(-0.529 + (-0.521) + (-0.521))
  = 1.571 bits
```

A concept entropy above 1.5 suggests the file handles too many unrelated responsibilities -- a "god file" risk.

#### Compression Ratio (Kolmogorov Complexity Proxy)

```
compression_ratio = len(zlib.compress(content)) / len(content)
```

**Intuition**: Kolmogorov complexity -- the length of the shortest program that produces a given string -- is uncomputable. But compression provides a practical upper bound. Highly repetitive code (boilerplate, copy-paste) compresses well (low ratio). Dense, information-rich code resists compression (high ratio).

**Typical ranges**:
- Below 0.15: Highly repetitive (generated code, boilerplate)
- 0.3 to 0.6: Normal source code
- Above 0.7: Very dense (minified, data-heavy)

#### Normalized Compression Distance (NCD)

```
NCD(A, B) = (C(AB) - min(C(A), C(B))) / max(C(A), C(B))
```

Where C(x) = len(zlib.compress(x)).

**Intuition**: NCD measures how much new information B adds beyond A (and vice versa). If two files are nearly identical, compressing their concatenation adds almost nothing beyond the larger file -- NCD approaches 0. If they share nothing, NCD approaches 1.

**Application**: Clone detection. File pairs with NCD < 0.3 are flagged as copy-paste clones.

#### Semantic Coherence

```
semantic_coherence = mean(cosine(v_i, v_j)) for all function pairs i < j
```

Where v_i is the TF-IDF vector of function i's body tokens.

**Intuition**: If all functions in a file use similar vocabulary (all about "database," "query," "connection"), the file is semantically coherent -- it does one thing. If functions use unrelated vocabulary ("render," "template" mixed with "migrate," "schema"), the file lacks focus.

**Polarity**: High is good. A coherence of 0.85 means the file's functions are tightly themed. Below 0.20 (percentile) triggers the GOD_FILE finder.

### Graph Metrics

#### PageRank

```
PR(v) = (1 - d) / N + d * SUM PR(u) / out_degree(u)  for all u -> v
```

Where d = 0.85 (damping factor), N = total number of files, and the sum is over all files u that import file v.

**Intuition**: Originally developed by Google to rank web pages, PageRank measures "importance by endorsement." A file is important if important files depend on it. The damping factor d = 0.85 means there is a 15% chance of "teleporting" to a random file, preventing importance from accumulating in cycles.

**Iteration**: Starting from PR(v) = 1/N for all v, repeatedly apply the formula until the maximum change across all files is below 1e-6 (typically 15-25 iterations).

**Why it matters for code**: Files with high PageRank are structural hubs. A change to a high-PageRank file ripples through many transitive dependents. Combined with high cognitive load or low bus factor, high PageRank signals a high-risk hub.

#### Betweenness Centrality

```
B(v) = SUM sigma(s,t|v) / sigma(s,t)   for all s != v != t
```

Where sigma(s,t) is the number of shortest paths from s to t, and sigma(s,t|v) is the number of those paths passing through v. Computed via Brandes' algorithm in O(|V| * |E|).

**Intuition**: Betweenness measures "bridge-ness." A file with high betweenness sits on many shortest paths between other files. Removing or changing it disrupts communication across the dependency graph. High betweenness files are fragile choke points.

**Normalization**: Divided by (n-1)(n-2) for directed graphs, producing values in [0, 1].

#### Blast Radius

```
blast_radius_size(v) = |BFS(v, reverse(G))| - 1
```

**Intuition**: If file v changes, how many other files are (transitively) affected? BFS on the reversed dependency graph finds every file that directly or indirectly depends on v.

**Example**: If A imports B, and B imports C, and C imports D, then blast_radius_size(D) = 3 (A, B, and C are all affected by changes to D).

#### Louvain Community Detection

```
Modularity: Q = (1 / 2m) * SUM [A_ij - k_i * k_j / (2m)] * delta(c_i, c_j)
```

Where m = total edge count, A_ij = adjacency matrix, k_i = degree of node i, and delta(c_i, c_j) = 1 if nodes i and j are in the same community.

**Intuition**: Louvain greedily optimizes modularity Q by moving nodes between communities. High Q (above 0.3) means the codebase has a natural cluster structure -- files that depend heavily on each other form distinct groups. Low Q means dependencies are spread uniformly, suggesting poor modularization.

**Application**: Community assignments feed boundary alignment detection. If a directory's files are split across multiple communities, the directory boundary does not match the actual dependency structure (BOUNDARY_MISMATCH finding).

### Spectral Analysis

#### Graph Laplacian

```
L = D - A
```

Where D is the diagonal degree matrix (D_ii = degree of node i) and A is the adjacency matrix (symmetrized from directed edges).

**Intuition**: The Laplacian encodes the diffusion behavior of the graph. Its eigenvalues reveal structural properties that are invisible in the raw adjacency matrix.

#### Fiedler Value (Algebraic Connectivity)

```
fiedler_value = lambda_2  (second-smallest eigenvalue of L)
```

**Intuition**: The smallest eigenvalue of L is always 0 (corresponding to the constant eigenvector). The second-smallest eigenvalue, lambda_2, measures algebraic connectivity:

- lambda_2 = 0: The graph is disconnected (at least two components with no edges between them).
- Small lambda_2: The graph has a bottleneck -- a narrow bridge connecting two halves. Removing a few edges disconnects it.
- Large lambda_2: The graph is well-connected. No single edge removal causes disconnection.

**Application**: Low fiedler_value warns of fragile connectivity. Combined with high centrality_gini, it indicates a hub-and-spoke architecture where removing the hub disconnects the system.

#### Spectral Gap

```
spectral_gap = lambda_2 / lambda_3
```

**Intuition**: The ratio of the second to third eigenvalue measures how clear the "best cut" is. A large spectral gap means there is one dominant partition of the graph into two clusters. A small gap means the community structure is ambiguous -- multiple similar partitions exist.

#### Health Laplacian

```
delta_h(f) = raw_risk(f) - mean(raw_risk(n) for n in neighbors(f))
```

Where neighbors(f) = files that import f OR that f imports (undirected neighborhood), and raw_risk is a pre-percentile weighted sum.

**Intuition**: This is the discrete Laplacian operator applied to the "health" scalar field over the dependency graph. Delta_h > 0 means a file is worse than its neighborhood -- a local weak point. Delta_h > 0.4 triggers the WEAK_LINK finder.

**Why raw_risk, not percentile-based risk_score**: Percentile normalization produces a near-uniform distribution, making the Laplacian meaningless (every node has approximately the same value). The raw weighted sum preserves natural variation.

### Temporal Patterns

#### Churn Coefficient of Variation

```
CV = std(changes_per_window) / mean(changes_per_window)
```

Where changes_per_window is the number of commits per 4-week window.

**Intuition**: CV measures erraticism. A file with 10 changes every month has low CV (steady). A file with 0, 30, 0, 25, 0, 40 changes has high CV (spiky). High CV files are unpredictable and hard to plan around.

**Threshold**: CV > 1.0 flags a file as having erratic changes.

#### Churn Trajectory Classification

```
if total_changes <= 1:                          DORMANT
elif velocity < -threshold AND CV < 0.5:        STABILIZING
elif velocity > threshold AND CV > 0.5:         SPIKING
elif CV > 0.5:                                  CHURNING
else:                                           STABLE
```

Where velocity is the linear regression slope of the changes-per-window time series.

**Intuition**: Trajectory classifies the overall trend of a file's change history:
- **DORMANT**: Barely touched (0-1 total changes)
- **STABILIZING**: Was changing a lot but is calming down
- **STABLE**: Consistent, moderate change rate
- **CHURNING**: Erratic, unpredictable changes
- **SPIKING**: Change rate is increasing and erratic

CHURNING and SPIKING trajectories contribute to the instability_factor in risk_score computation.

#### Bus Factor

```
bus_factor = 2^H
```

Where H is the Shannon entropy of the per-file author distribution (commit counts per author).

**Intuition**: If a file has k equally-contributing authors, H = log2(k), so bus_factor = k. One author gives bus_factor = 1 (single point of failure). Three equal authors give bus_factor = 3. The exponential conversion makes bus_factor directly interpretable as "effective author count."

**Threshold**: bus_factor <= 1.5 with high PageRank triggers the KNOWLEDGE_SILO finder.

#### Co-change Detection

```
lift(A, B) = P(A and B) / (P(A) * P(B))
```

Where P(A) = fraction of commits touching file A, P(A and B) = fraction of commits touching both.

**Intuition**: Lift measures whether two files change together more often than chance predicts. Lift = 1 means independence. Lift > 2 means the files co-change at twice the expected rate. If lift >= 2 and confidence >= 0.5 but no structural dependency exists between the files, they have hidden coupling.

#### Gini Coefficient

```
G = (2 * SUM i * x_i) / (n * SUM x_i) - (n + 1) / n
```

Where x_i are values sorted ascending and i is 1-indexed rank.

**Intuition**: Gini measures inequality of a distribution. G = 0 means perfect equality (all values identical). G = 1 means maximum inequality (one value holds everything).

**Applications**:
- `impl_gini` (signal #5): Gini of function body token counts. High Gini (> 0.6) means some functions are complete while others are stubs -- a signature of AI-generated code.
- `centrality_gini` (signal #56): Gini of PageRank values. High Gini (> 0.7) means a few files dominate the dependency structure (fragile hub-and-spoke).
- `knowledge_gini` (signal #47): Gini of per-author commit counts within a module. High Gini (> 0.7) means knowledge is siloed.

---

## Signals Reference

Shannon Insight computes 62 base signals organized by scope and source.

### Per-File Signals (36 signals)

#### Syntactic Signals (from scanning)

| # | Signal | Type | Range | Polarity | Description |
|---|--------|------|-------|----------|-------------|
| 1 | `lines` | int | [0, inf) | high=BAD | Line count. Absolute threshold: > 500. |
| 2 | `function_count` | int | [0, inf) | high=BAD | Count of function/method definitions. Absolute threshold: > 30. |
| 3 | `class_count` | int | [0, inf) | neutral | Count of class definitions. |
| 4 | `max_nesting` | int | [0, inf) | high=BAD | Maximum nesting depth across all functions. Absolute threshold: > 4. |
| 5 | `impl_gini` | float | [0, 1] | high=BAD | Gini coefficient of function body token counts. 0 = uniform. > 0.6 = bimodal (AI signature). |
| 6 | `stub_ratio` | float | [0, 1] | high=BAD | Mean stub score across functions. Absolute threshold: > 0.5. |
| 7 | `import_count` | int | [0, inf) | neutral | Count of import declarations. |

#### Semantic Signals (from semantics)

| # | Signal | Type | Range | Polarity | Description |
|---|--------|------|-------|----------|-------------|
| 8 | `role` | enum | 12 values | -- | File role: MODEL, SERVICE, UTILITY, CONFIG, TEST, CLI, INTERFACE, EXCEPTION, CONSTANT, ENTRY_POINT, MIGRATION, UNKNOWN. |
| 9 | `concept_count` | int | [0, inf) | high=BAD | Number of concept clusters. Higher = less focused. |
| 10 | `concept_entropy` | float | [0, inf) | high=BAD | Shannon entropy of concept weights. Absolute threshold: > 1.5. |
| 11 | `naming_drift` | float | [0, 1] | high=BAD | 1 - cosine(filename tokens, content concept tokens). Absolute threshold: > 0.7. |
| 12 | `todo_density` | float | [0, inf) | high=BAD | (TODO + FIXME + HACK count) / lines. Absolute threshold: > 0.05. |
| 13 | `docstring_coverage` | float | [0, 1] | high=GOOD | documented_public_symbols / total_public_symbols. None for unsupported languages. |

#### Graph Signals (from graph analysis)

| # | Signal | Type | Range | Polarity | Description |
|---|--------|------|-------|----------|-------------|
| 14 | `pagerank` | float | [0, 1] | high=BAD | Importance via random walk. d=0.85, convergence at 1e-6. |
| 15 | `betweenness` | float | [0, 1] | high=BAD | Fraction of shortest paths passing through this file. |
| 16 | `in_degree` | int | [0, inf) | neutral | Files that import this file. |
| 17 | `out_degree` | int | [0, inf) | neutral | Files this file imports. |
| 18 | `blast_radius_size` | int | [0, n-1] | high=BAD | Transitive reverse closure size (BFS on reversed graph). |
| 19 | `depth` | int | [0, inf) or -1 | neutral | Shortest path from nearest entry point. -1 = unreachable (orphan). |
| 20 | `is_orphan` | bool | {0, 1} | high=BAD | in_degree=0 AND role is not ENTRY_POINT or TEST. |
| 21 | `phantom_import_count` | int | [0, inf) | high=BAD | Unresolved imports (missing modules). Absolute threshold: > 0. |
| 22 | `broken_call_count` | int | [0, inf) | high=BAD | Unresolved call targets. Defaults to 0 (future: CALL edges). |
| 23 | `community` | int | [0, k) | -- | Louvain community assignment ID. |
| 24 | `compression_ratio` | float | [0, 1] | neutral | zlib compressed size / raw size. |
| 25 | `semantic_coherence` | float | [0, 1] | high=GOOD | Mean pairwise cosine similarity of function TF-IDF vectors. |
| 26 | `cognitive_load` | float | [0, inf) | high=BAD | (concepts x complexity x e^(nesting/5)) x (1 + Gini). |

#### Temporal Signals (from git history)

| # | Signal | Type | Range | Polarity | Description |
|---|--------|------|-------|----------|-------------|
| 27 | `total_changes` | int | [0, inf) | high=BAD | Total commits touching this file. |
| 28 | `churn_trajectory` | enum | 5 values | -- | DORMANT, STABILIZING, STABLE, CHURNING, SPIKING. |
| 29 | `churn_slope` | float | (-inf, inf) | high=BAD | Linear regression slope of changes per 4-week window. |
| 30 | `churn_cv` | float | [0, inf) | high=BAD | Coefficient of variation of changes per window. Absolute threshold: > 1.0. |
| 31 | `bus_factor` | float | [1, inf) | high=GOOD | 2^H where H = author entropy. Effective author count. |
| 32 | `author_entropy` | float | [0, inf) | high=GOOD | Shannon entropy of author distribution. |
| 33 | `fix_ratio` | float | [0, 1] | high=BAD | Fraction of commits with fix/bug/patch keywords. Absolute threshold: > 0.4. |
| 34 | `refactor_ratio` | float | [0, 1] | high=GOOD | Fraction of commits with refactor/restructure keywords. |

#### Per-File Composites

| # | Signal | Type | Range | Polarity | Formula |
|---|--------|------|-------|----------|---------|
| 35 | `risk_score` | float | [0, 1] | high=BAD | 0.25 x pctl(pagerank) + 0.20 x pctl(blast_radius_size) + 0.20 x pctl(cognitive_load) + 0.20 x instability_factor + 0.15 x (1 - bus_factor/max_bus_factor) |
| 36 | `wiring_quality` | float | [0, 1] | high=GOOD | 1 - (0.30 x is_orphan + 0.25 x stub_ratio + 0.25 x phantom_import_count/max(import_count,1) + 0.20 x broken_call_count/max(total_calls,1)) |

### Per-Module Signals (15 signals)

| # | Signal | Type | Range | Polarity | Description |
|---|--------|------|-------|----------|-------------|
| 37 | `cohesion` | float | [0, 1] | high=GOOD | internal_edges / (file_count x (file_count - 1)). |
| 38 | `coupling` | float | [0, 1] | high=BAD | external_edges / (internal_edges + external_edges). |
| 39 | `instability` | float or None | [0, 1] | neutral | Ce / (Ca + Ce). None if isolated module (Ca=Ce=0). |
| 40 | `abstractness` | float | [0, 1] | neutral | abstract_symbols / total_symbols. |
| 41 | `main_seq_distance` | float | [0, 1] | high=BAD | |A + I - 1|. 0 = ideal balance. |
| 42 | `boundary_alignment` | float | [0, 1] | high=GOOD | Files in dominant Louvain community / total files. |
| 43 | `layer_violation_count` | int | [0, inf) | high=BAD | Backward or skip edges into this module. |
| 44 | `role_consistency` | float | [0, 1] | high=GOOD | max(role_count) / total_files in module. |
| 45 | `velocity` | float | [0, inf) | neutral | Commits per week touching any file in module. |
| 46 | `coordination_cost` | float | [0, inf) | high=BAD | Mean distinct authors per commit touching module. |
| 47 | `knowledge_gini` | float | [0, 1] | high=BAD | Gini coefficient of per-author commit counts. > 0.7 = silo. |
| 48 | `module_bus_factor` | float | [1, inf) | high=GOOD | min(bus_factor) across high-centrality files in module. |
| 49 | `mean_cognitive_load` | float | [0, inf) | high=BAD | Mean cognitive_load across files in module. |
| 50 | `file_count` | int | [0, inf) | neutral | Number of source files in module. |
| 51 | `health_score` | float | [0, 1] | high=GOOD | Composite: cohesion, coupling, main_seq_distance, boundary_alignment, role_consistency, stub_ratio. |

### Global Signals (11 signals)

| # | Signal | Type | Range | Polarity | Description |
|---|--------|------|-------|----------|-------------|
| 52 | `modularity` | float | [0, 1] | high=GOOD | Louvain Q score. > 0.3 = well-modularized. |
| 53 | `fiedler_value` | float | [0, inf) | high=GOOD | Lambda_2 of graph Laplacian. Algebraic connectivity. 0 = disconnected. |
| 54 | `spectral_gap` | float | [0, inf) | high=GOOD | Lambda_2 / lambda_3. Large = clear community structure. |
| 55 | `cycle_count` | int | [0, inf) | high=BAD | Count of SCCs with more than 1 node. |
| 56 | `centrality_gini` | float | [0, 1] | high=BAD | Gini of PageRank distribution. > 0.7 = hub-dominated. |
| 57 | `orphan_ratio` | float | [0, 1] | high=BAD | count(is_orphan) / total_files. |
| 58 | `phantom_ratio` | float | [0, 1] | high=BAD | unresolved_edges / total_edges. |
| 59 | `glue_deficit` | float | [0, 1] | high=BAD | 1 - |glue nodes| / |V|. Fraction that are NOT internal connectors. |
| 60 | `wiring_score` | float | [0, 1] | high=GOOD | 1 - (0.25 x orphan_ratio + 0.25 x phantom_ratio + 0.20 x glue_deficit + 0.15 x mean(stub_ratio) + 0.15 x clone_ratio). |
| 61 | `architecture_health` | float | [0, 1] | high=GOOD | Weighted: violation_rate, mean cohesion, mean coupling, mean D, boundary alignment. |
| 62 | `codebase_health` | float | [0, 1] | high=GOOD | 0.30 x architecture_health + 0.30 x wiring_score + 0.20 x (global_bus_factor/team_size) + 0.20 x modularity. |

### Temporal Operators

Every numeric signal can have temporal operators applied when historical snapshots exist:

| Operator | Formula | Meaning |
|----------|---------|---------|
| **Delta** | S(t) - S(t-1) | One-step change |
| **Velocity** | Slope of linear regression on S(t_0..t_n) | Rate of change |
| **Acceleration** | v(recent) - v(older) | Is change speeding up? |
| **Trajectory** | Classification (DORMANT/STABILIZING/STABLE/CHURNING/SPIKING) | Qualitative trend |
| **Volatility** | std(S) / mean(S) (coefficient of variation) | How erratic? |
| **Trend** | Direction of rolling mean | IMPROVING / STABLE / WORSENING |

With 62 base signals and 6 temporal operators, Shannon Insight can measure approximately 360 quantities per snapshot.

---

## Finders Reference

Shannon Insight has 22 finding types organized into 5 categories. Each finding is backed by specific signal conditions, not heuristics.

### Structural Findings (from v1)

#### HIGH_RISK_HUB
- **Severity**: 1.0 (highest)
- **Scope**: FILE
- **What it detects**: Files that are central to the dependency graph, complex, and actively changing. A change to this file has maximum ripple effect.
- **Condition**: pctl(pagerank) > 0.90 AND pctl(blast_radius_size) > 0.90 AND (pctl(cognitive_load) > 0.90 OR churn_trajectory in {CHURNING, SPIKING})
- **Hotspot filtered**: Yes -- only fires if total_changes > median.
- **How to fix**: Split responsibilities into focused modules. Pair-program to spread knowledge. Add integration tests at the boundary.

#### HIDDEN_COUPLING
- **Severity**: 0.9
- **Scope**: FILE_PAIR
- **What it detects**: Two files that always change together but have no structural dependency. This indicates an implicit contract that should be made explicit.
- **Condition**: co-change lift >= 2.0 AND confidence >= 0.5 AND no import edge between the pair.
- **How to fix**: Extract the shared concept into a common module, or add an explicit dependency.

#### GOD_FILE
- **Severity**: 0.8
- **Scope**: FILE
- **What it detects**: Files that are both highly complex and semantically unfocused -- they do too many things.
- **Condition**: pctl(cognitive_load) > 0.90 AND pctl(semantic_coherence) < 0.20
- **How to fix**: Split by concept clusters. Each concept identified by the semantic analyzer is a candidate for extraction into its own file.

#### UNSTABLE_FILE
- **Severity**: 0.7
- **Scope**: FILE
- **What it detects**: Files with erratic or spiking change patterns that have not stabilized.
- **Condition**: churn_trajectory in {CHURNING, SPIKING} AND total_changes > median
- **How to fix**: Investigate why the file keeps changing. Check fix_ratio -- if high, there may be a fundamental design issue.

#### BOUNDARY_MISMATCH
- **Severity**: 0.6
- **Scope**: MODULE
- **What it detects**: A directory whose files do not form a natural dependency cluster. The organizational boundary does not match the actual dependency structure.
- **Condition**: boundary_alignment < 0.7 AND file_count >= 3
- **How to fix**: Reorganize files to align directory boundaries with dependency clusters (Louvain communities).

#### DEAD_DEPENDENCY
- **Severity**: 0.4
- **Scope**: FILE_PAIR
- **What it detects**: An import edge exists between two files, but they never change together despite both having significant commit history. The dependency may be unused.
- **Condition**: structural edge exists AND co-change count = 0 AND both files have 50+ commits
- **How to fix**: Verify the imported symbols are actually used. Remove dead imports.

#### CHRONIC_PROBLEM
- **Severity**: base_severity x 1.25
- **Scope**: Wraps another finding
- **What it detects**: A finding that has persisted across 3 or more analysis snapshots. The issue is known but not addressed.
- **Condition**: Same finding identity key persists across 3+ snapshots.
- **How to fix**: Prioritize resolution. The persistence itself indicates organizational resistance to fixing the underlying issue.

### AI Code Quality Findings

#### ORPHAN_CODE
- **Severity**: 0.55
- **Scope**: FILE
- **What it detects**: Files with zero incoming dependencies that are not entry points or tests. Nothing imports them -- they may be dead code or incorrectly wired.
- **Condition**: is_orphan = true (in_degree = 0 AND role not in {ENTRY_POINT, TEST})
- **How to fix**: Wire into the dependency graph by importing from an appropriate module, or remove if truly unused.

#### HOLLOW_CODE
- **Severity**: 0.71
- **Scope**: FILE
- **What it detects**: Files where most functions are stubs (empty bodies, `pass`, `...`, `return None`) with a bimodal distribution (some complete, some hollow). A signature of AI-generated scaffolding.
- **Condition**: stub_ratio > 0.5 AND impl_gini > 0.6
- **How to fix**: Implement the stub functions. Prioritize functions called by other files.

#### PHANTOM_IMPORTS
- **Severity**: 0.65
- **Scope**: FILE
- **What it detects**: Import statements that cannot be resolved to any file in the codebase (and are not recognized as installed packages). The imported module does not exist.
- **Condition**: phantom_import_count > 0
- **How to fix**: Create the missing module or replace with an existing library.

#### COPY_PASTE_CLONE
- **Severity**: 0.50
- **Scope**: FILE_PAIR
- **What it detects**: Two files with near-identical content, detected via Normalized Compression Distance.
- **Condition**: NCD(A, B) < 0.3
- **How to fix**: Extract shared logic into a common module.

#### FLAT_ARCHITECTURE
- **Severity**: 0.60
- **Scope**: CODEBASE
- **What it detects**: A codebase where the dependency graph has no depth (max_depth <= 1) and most files are leaves with no orchestration layer.
- **Condition**: max(depth) <= 1 AND glue_deficit > 0.5
- **How to fix**: Add a composition/orchestration layer that connects leaf modules.

#### NAMING_DRIFT
- **Severity**: 0.45
- **Scope**: FILE
- **What it detects**: Files whose content does not match their filename. The name suggests one responsibility, but the content implements something different.
- **Condition**: naming_drift > 0.7
- **How to fix**: Rename the file to match its actual content, or extract the mismatched logic.

### Social / Team Findings

#### KNOWLEDGE_SILO
- **Severity**: 0.70
- **Scope**: FILE
- **What it detects**: Central files maintained by a single author. If that person leaves, critical knowledge is lost.
- **Condition**: bus_factor <= 1.5 AND pctl(pagerank) > 0.75
- **Hotspot filtered**: Yes.
- **How to fix**: Pair-program or rotate ownership. Ensure at least 2 people understand critical files.

#### CONWAY_VIOLATION
- **Severity**: 0.55
- **Scope**: MODULE_PAIR
- **What it detects**: Two modules with strong structural coupling but maintained by completely different teams. Conway's Law predicts friction.
- **Condition**: author_distance(M1, M2) > 0.8 AND structural_coupling(M1, M2) > 0.3
- **How to fix**: Align team boundaries with architectural boundaries, or reduce coupling between the modules.

#### REVIEW_BLINDSPOT
- **Severity**: 0.80
- **Scope**: FILE
- **What it detects**: High-centrality code with a single owner and no associated test file. Maximum risk: important, untested, single-author code.
- **Condition**: pctl(pagerank) > 0.75 AND bus_factor <= 1.5 AND no test file associated
- **Hotspot filtered**: Yes.
- **How to fix**: Add tests and a second reviewer/maintainer.

### Architecture Findings

#### LAYER_VIOLATION
- **Severity**: 0.52
- **Scope**: MODULE_PAIR
- **What it detects**: A dependency that goes backward in the inferred architectural layering (e.g., foundation layer importing presentation layer) or skips intermediate layers.
- **Condition**: Backward or skip edge in inferred layer ordering.
- **How to fix**: Inject a dependency inversion or restructure to respect layer ordering.

#### ZONE_OF_PAIN
- **Severity**: 0.60
- **Scope**: MODULE
- **What it detects**: Modules that are both concrete (low abstractness) and stable (low instability). They are hard to change because many things depend on them and they expose implementation details.
- **Condition**: instability is not None AND abstractness < 0.3 AND instability < 0.3
- **How to fix**: Extract interfaces or reduce the number of dependents.

#### ARCHITECTURE_EROSION
- **Severity**: 0.65
- **Scope**: CODEBASE
- **What it detects**: The architectural violation rate is increasing over time, indicating the architecture is actively eroding.
- **Condition**: violation_rate increasing over 3+ snapshots.
- **How to fix**: Schedule dedicated structural refactoring time.

### Cross-Dimensional Findings

#### WEAK_LINK
- **Severity**: 0.75
- **Scope**: FILE
- **What it detects**: Files that are significantly worse than their graph neighbors, detected via the health Laplacian. A local weak point that drags down an otherwise healthy neighborhood.
- **Condition**: delta_h(f) > 0.4
- **Hotspot filtered**: Yes.
- **How to fix**: Prioritize improvement of this specific file -- it has the highest marginal health impact.

#### BUG_ATTRACTOR
- **Severity**: 0.70
- **Scope**: FILE
- **What it detects**: Central files where 40%+ of changes are bug fixes. Something fundamental is wrong with the design.
- **Condition**: fix_ratio > 0.4 AND pctl(pagerank) > 0.75
- **Hotspot filtered**: Yes.
- **How to fix**: Root-cause analysis. The high fix ratio in a central file suggests a design flaw, not just bugs.

#### ACCIDENTAL_COUPLING
- **Severity**: 0.50
- **Scope**: FILE_PAIR
- **What it detects**: Two files that have a structural dependency (import edge) but share almost no concepts. The dependency may be accidental or poorly motivated.
- **Condition**: structural edge exists AND concept_overlap(A, B) < 0.2 (Jaccard on concept sets)
- **How to fix**: Consider removing or abstracting the dependency.

---

## Use Cases

### Code Review Automation

Integrate Shannon Insight into pull request workflows. When a PR modifies high-risk files, automatically flag the signals:

```bash
# Analyze only changed files
shannon-insight /path/to/project --changed

# Or changes since a specific ref
shannon-insight /path/to/project --since origin/main
```

The `--changed` flag produces a `ChangeScopedReport` showing only findings that affect modified files, making code review focused and actionable.

### Technical Debt Tracking

Run Shannon Insight with `--save` on each release (or weekly) to build a historical signal database:

```bash
# After each release
shannon-insight /path/to/project --save

# View trends
shannon-insight health /path/to/project
```

The health command shows:
- Codebase health score trend (sparkline)
- Debt velocity: are you creating or resolving findings faster?
- Files with worsening signals (increasing risk_score, decreasing bus_factor)
- Chronic problems: findings that have persisted across 3+ snapshots

### Onboarding New Developers

Run `explain` on a specific file to give a new developer an instant understanding of its role and risk profile:

```bash
shannon-insight explain src/core/engine.py
```

The output shows the file's role, concept clusters, dependency position (what it imports and what imports it), risk score breakdown, and any active findings. This is faster and more objective than reading scattered documentation.

### Architectural Governance

Use the architecture detection and layer inference to enforce architectural rules:

```bash
# Full analysis with architecture details
shannon-insight /path/to/project --verbose

# Check for layer violations in CI
shannon-insight /path/to/project --json --fail-on any
```

LAYER_VIOLATION and ZONE_OF_PAIN findings appear when the architecture drifts from its inferred layering. ARCHITECTURE_EROSION catches gradual degradation over time.

### CI/CD Quality Gates

```bash
# Fail if any finding has HIGH or CRITICAL severity
shannon-insight /path/to/project --fail-on high
# Exit code 0 = pass, 1 = findings found, 2 = error

# Fail on any finding
shannon-insight /path/to/project --fail-on any

# JSON output for parsing in CI scripts
shannon-insight /path/to/project --json --fail-on high
```

### HTML Report Generation

```bash
shannon-insight report /path/to/project
```

Generates an interactive HTML treemap report showing file risk as area (proportional to lines) and color (proportional to risk_score). Useful for presentations and architecture review meetings.

---

## CLI Reference

### Main Command

```bash
shannon-insight [OPTIONS] [PATH]
```

Runs the full analysis pipeline on the specified path (default: current directory).

| Flag | Description |
|------|-------------|
| `-C`, `--path PATH` | Path to analyze (alternative to positional argument) |
| `--changed` | Only analyze files changed since the auto-detected base ref |
| `--since REF` | Only analyze files changed since the given git ref |
| `--json` | Output results as JSON instead of rich terminal display |
| `--verbose` | Enable debug-level logging and show additional details |
| `--save` | Save analysis snapshot to `.shannon/history.db` for trend tracking |
| `--fail-on LEVEL` | Exit with code 1 if findings at or above this severity exist. Values: `any`, `high` |

### Subcommands

#### `explain`

```bash
shannon-insight explain FILE [OPTIONS]
```

Deep-dive analysis of a single file. Shows role, signals, dependency context, concept clusters, and active findings.

#### `diff`

```bash
shannon-insight diff [PATH] [OPTIONS]
```

Compare the current analysis with the most recent saved snapshot. Shows signal deltas, finding lifecycle (new/resolved/persisting/regression), and debt velocity.

#### `health`

```bash
shannon-insight health [PATH] [OPTIONS]
```

Show health trends over time. Requires 2+ saved snapshots. Displays codebase_health trend, worsening files, and improving files.

#### `history`

```bash
shannon-insight history [PATH] [OPTIONS]
```

List all saved analysis snapshots with metadata (timestamp, commit SHA, file count, finding count).

#### `report`

```bash
shannon-insight report [PATH] [OPTIONS]
```

Generate an interactive HTML treemap report. Files are sized by lines and colored by risk_score. Saved to `.shannon/report.html` by default.

#### `serve`

```bash
shannon-insight serve [PATH] [OPTIONS]
```

Start a local web server with an interactive dashboard (requires the `serve` optional dependency: `pip install shannon-codebase-insight[serve]`).

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Analysis completed successfully, no findings above the `--fail-on` threshold |
| 1 | Findings found above the `--fail-on` threshold |
| 2 | Analysis error (invalid path, configuration error, etc.) |

### Configuration

Shannon Insight can be configured via a `shannon-insight.toml` file in the project root or via environment variables with the `SHANNON_` prefix.

```toml
# shannon-insight.toml

# File scanning
max_file_size_mb = 10
follow_symlinks = false
exclude_patterns = ["vendor/", "node_modules/", ".git/"]

# Architecture
[architecture]
module_depth = "auto"  # or explicit integer

# Temporal
[temporal]
velocity_window_days = 90
```

All settings can be overridden with environment variables:

```bash
SHANNON_MAX_FILE_SIZE_MB=20 shannon-insight /path/to/project
```

---

## Dashboard Guide

The dashboard (via `shannon-insight serve`) provides an interactive web interface for exploring analysis results.

### Overview Screen

The landing page shows the codebase health score (1-10), finding summary by category, and key composite scores (architecture_health, wiring_score, team_risk). A dependency graph visualization shows the file-level import structure colored by risk_score.

### Issues Screen

Findings grouped by category (Structural, AI Code Quality, Social/Team, Architecture, Cross-Dimensional) and sorted by severity. Each finding shows:
- Severity badge and confidence score
- Affected files with signal values
- Evidence chain (which signals triggered the finding)
- Suggestion for resolution
- Estimated effort (LOW/MEDIUM/HIGH)

### Files Screen

Risk-ranked list of all analyzed files. Each file shows:
- Risk score (1-10 display scale)
- Wiring quality
- Key signals (PageRank percentile, cognitive load, bus factor)
- Active finding count
- Churn trajectory indicator

Click any file for the full explain view.

### Modules Screen

Architecture overview showing detected modules with Martin metrics:
- Instability-Abstractness scatter plot (main sequence visualization)
- Layer diagram with violation edges highlighted in red
- Module health scores
- Boundary alignment indicators

### Health Screen

Time series charts (requires 2+ saved snapshots):
- Codebase health over time
- Debt velocity (new vs. resolved findings per snapshot)
- Signal trends for selected files
- Finding lifecycle timeline

---

## FAQ

### How is this different from SonarQube?

SonarQube uses rule-based static analysis -- it checks code against predefined patterns (null pointer risks, code smells, style violations). Shannon Insight operates at a higher level of abstraction: it measures the mathematical properties of your codebase as a system (entropy, centrality, spectral connectivity, temporal patterns) and finds issues through cross-dimensional anomaly detection. SonarQube tells you "this function is too complex." Shannon Insight tells you "this function is too complex AND is a dependency hub AND has a single maintainer AND is actively churning -- it is a high-risk hub."

### How is this different from CodeClimate?

CodeClimate computes a maintainability index based on code metrics (complexity, duplication, size). Shannon Insight goes further with graph analysis (PageRank, Louvain communities, spectral decomposition), temporal analysis (churn trajectories, bus factor, co-change detection), and architecture analysis (Martin metrics, layer inference, violation detection). The health Laplacian and distance space disagreement framework are unique to Shannon Insight.

### Does it support my language?

Shannon Insight supports 8 languages: **Python**, **Go**, **TypeScript**, **JavaScript**, **Java**, **Rust**, **Ruby**, and **C/C++**. Graph analysis, temporal analysis, and most signals work across all languages. Some signals (like `docstring_coverage`) are language-specific.

Adding a new language requires implementing a scanner in `scanning/` and registering it in the factory -- see the extension point documentation.

### How long does analysis take?

Analysis time depends on codebase size and available data:
- 100 files: approximately 1-2 seconds
- 500 files: approximately 3-5 seconds
- 2,000 files: approximately 10-15 seconds
- 10,000 files: approximately 30-60 seconds (betweenness centrality dominates for large graphs)

Git history parsing adds 1-3 seconds depending on repository age.

### Can I use it in CI/CD?

Yes. Use `--json --fail-on high` for CI integration:

```yaml
# GitHub Actions example
- name: Shannon Insight Quality Gate
  run: |
    pip install shannon-codebase-insight
    shannon-insight . --json --fail-on high
```

Exit code 0 means no findings above the threshold. Exit code 1 means the build should fail.

### How to interpret health scores?

Health scores are displayed on a **1-10 scale** (internally computed as 0-1, multiplied by 10):

| Score | Interpretation |
|-------|---------------|
| 8-10 | Healthy. Well-structured, well-maintained, good bus factor. |
| 6-8 | Moderate. Some issues but manageable. Address findings proactively. |
| 4-6 | Concerning. Multiple systemic issues. Prioritize technical debt reduction. |
| 1-4 | Critical. Significant architectural problems or team risks. |

Use rank ordering ("this file is the #1 riskiest") rather than absolute interpretation of score values. The weights are hand-tuned and will be calibrated against industry datasets in future versions.

### What is the "wiring score" / "AI quality score"?

The wiring score (also called AI quality score) detects signatures common in AI-generated codebases: orphan files (unreachable code), phantom imports (missing modules), hollow code (stub functions), flat architecture (no depth), and copy-paste clones. It combines orphan_ratio, phantom_ratio, glue_deficit, mean stub_ratio, and clone_ratio into a single 1-10 score. High is good.

### What does "hotspot filtered" mean?

Temporal-aware findings (like HIGH_RISK_HUB, KNOWLEDGE_SILO, BUG_ATTRACTOR) only fire for files where `total_changes > median(total_changes)`. This prevents flagging complex-but-stable code that nobody is actively working on. The rationale: if a file is complicated but dormant, fixing it has low urgency. Only flag problems in code people are actually touching.

### Can I extend Shannon Insight?

Yes. Three extension points:

1. **New language scanner**: Implement a scanner class in `scanning/`, register in `factory.py`, add entry point in `pyproject.toml`.
2. **New signal primitive**: Add a plugin in `signals/plugins/`, add the field to the signal model, register in the registry.
3. **New finder**: Implement the `Finder` protocol (`name`, `requires`, `find(store)`) in `insights/finders/`, register in `InsightKernel`.
