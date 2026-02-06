# Failure Modes: What Breaks If You Vibe Code This

> **Reality check**: These are the exact ways implementation fails if you don't follow specs precisely.
> Each has burned real projects. Don't be clever. Follow the spec.

---

## Category 1: Silent Data Corruption

### FM-1: Signal Name Typos

**What happens**: You write `"pageRank"` or `"page_rank"` instead of `"pagerank"`. Code runs. Signal is never found. Finder silently skips.

**Why it's bad**: No error. Finder just returns `[]`. You think there are no findings. Actually the finder never ran.

**Prevention**: Use `Signal.PAGERANK` enum, never strings. Registry pattern catches this at import time.

```python
# WRONG - silent failure
if fs.get("pageRank", 0) > 0.9:  # typo, always uses default 0

# RIGHT - caught at import
if fs.percentiles.get(Signal.PAGERANK.value, 0) > 0.9:
```

---

### FM-2: Instability = None Not Guarded

**What happens**: You compute `main_seq_distance = abs(A + I - 1)` but instability is `None` (isolated module). Python does `abs(0.3 + None - 1)` → TypeError... or worse, some edge case where it silently produces garbage.

**Why it's bad**: Crashes in production on real codebases with isolated modules. Or produces `NaN` that propagates.

**Prevention**: Always guard:

```python
# WRONG - crashes or NaN
D = abs(mod.abstractness + mod.instability - 1)

# RIGHT
if mod.instability is None:
    D = None  # or skip
else:
    D = abs(mod.abstractness + mod.instability - 1)
```

**Finders affected**: ZONE_OF_PAIN, health_score composite

---

### FM-3: Wrong Computation Order in Fusion

**What happens**: You compute percentiles BEFORE raw_risk. Health Laplacian uses percentile-normalized values. Laplacian becomes meaningless (all values ~uniform after percentile).

**Why it's bad**: WEAK_LINK finder produces random results. Looks like it works but findings are nonsense.

**Prevention**: FusionPipeline enforces order via typestate. Follow the 6-step order exactly:

```
1. collect
2. raw_risk     ← BEFORE percentiles
3. normalize    ← percentiles here
4. module_temporal
5. composites
6. laplacian    ← uses raw_risk, not percentiles
```

---

### FM-4: Percentile Formula Off-By-One

**What happens**: You use `<` instead of `≤` in percentile formula. Or you use 0-indexed rank instead of count.

**Why it's bad**: Percentiles are slightly wrong. Thresholds don't trigger when expected. Hard to debug.

**Prevention**: Use EXACT formula:

```python
# CORRECT formula
pctl = len([v for v in all_values if v <= this_value]) / len(all_values)

# WRONG - strict less than
pctl = len([v for v in all_values if v < this_value]) / len(all_values)
```

---

### FM-5: Polarity Confusion

**What happens**: You treat `semantic_coherence` as "high is bad" (like most signals). But it's "high is GOOD". Your finder fires on well-structured files.

**Why it's bad**: GOD_FILE finder flags the BEST files in codebase. User loses trust.

**Prevention**: Check `registry/signals.md` polarity table. Use inverted condition:

```python
# semantic_coherence: high is GOOD
# GOD_FILE wants LOW coherence (unfocused)

# WRONG - fires on good files
if pctl_coherence > 0.80:

# RIGHT - fires on bad files
if pctl_coherence < 0.20:
```

**Signals with high=GOOD**: semantic_coherence, bus_factor, author_entropy, docstring_coverage, refactor_ratio, cohesion, boundary_alignment, role_consistency, modularity, wiring_quality, health_score, etc.

---

## Category 2: Finders That Don't Fire

### FM-6: Forgot Tier Check

**What happens**: Your finder uses `pctl(pagerank) > 0.90`. Codebase has 10 files (ABSOLUTE tier). Percentiles don't exist. Finder silently returns `[]`.

**Why it's bad**: User with small codebase sees no findings. Thinks code is perfect.

**Prevention**: Check tier and use absolute thresholds:

```python
def find(self, store):
    field = store.signal_field.value

    if field.tier == "ABSOLUTE":
        # Use absolute threshold
        threshold = REGISTRY[Signal.PAGERANK].absolute_threshold
        if threshold is None:
            return []  # Can't evaluate
        condition = lambda fs: fs.pagerank > threshold
    else:
        # Use percentile
        condition = lambda fs: fs.percentiles.get("pagerank", 0) > 0.90
```

---

### FM-7: Forgot Hotspot Filter

**What happens**: Your finder (KNOWLEDGE_SILO) fires on a file that hasn't been touched in 2 years. User is confused why ancient stable code is flagged.

**Why it's bad**: Noise. User ignores all findings because they include irrelevant old files.

**Prevention**: Check `hotspot_filtered` flag, apply filter:

```python
def find(self, store):
    if self.hotspot_filtered:
        median = compute_hotspot_median(store)

    for path, fs in store.signal_field.value.per_file.items():
        # Hotspot check
        if self.hotspot_filtered:
            if fs.total_changes <= median:
                continue  # Skip dormant files

        # Actual condition
        if fs.bus_factor <= 1.5 and fs.percentiles.get("pagerank", 0) > 0.75:
            yield Finding(...)
```

---

### FM-8: Requires Not Declared

**What happens**: Finder needs `architecture` slot but doesn't declare it in `requires`. Topo-sort doesn't know. Finder runs before ArchitectureAnalyzer. Slot is empty. Finder returns `[]`.

**Why it's bad**: Silent. No error. Finder just doesn't work.

**Prevention**: Declare ALL requirements:

```python
class ZoneOfPainFinder:
    requires = {"architecture", "signal_field"}  # Both needed

    def find(self, store):
        if not store.architecture.available:  # Defensive check too
            return []
```

---

### FM-9: Wrong Store Slot

**What happens**: You read from `store.structural.analysis.pagerank` but v2 moved pagerank to `store.signal_field.per_file[path].pagerank`. You get old/stale data or None.

**Why it's bad**: Data mismatch. Finder uses outdated values.

**Prevention**: Use `signal_field` as the single source for all signals:

```python
# WRONG - old v1 pattern
pr = store.structural.analysis.pagerank.get(path, 0)

# RIGHT - v2 pattern
pr = store.signal_field.value.per_file[path].pagerank
```

---

## Category 3: Crashes in Production

### FM-10: Division by Zero

**What happens**: You compute `phantom_import_count / import_count` but file has 0 imports. Crash.

**Why it's bad**: Crashes on real codebase with import-free files (scripts, configs).

**Prevention**: Guard divisions:

```python
# WRONG
ratio = phantoms / imports

# RIGHT
ratio = phantoms / max(imports, 1)
# or
ratio = phantoms / imports if imports > 0 else 0.0
```

---

### FM-11: Empty Collection Operations

**What happens**: You compute `max(bus_factors)` but list is empty. `ValueError: max() arg is an empty sequence`.

**Why it's bad**: Crashes on single-file codebase or when temporal data missing.

**Prevention**: Guard aggregations:

```python
# WRONG
max_bf = max(fs.bus_factor for fs in files)

# RIGHT
bus_factors = [fs.bus_factor for fs in files if fs.bus_factor is not None]
max_bf = max(bus_factors) if bus_factors else 1.0
```

---

### FM-12: Slot Not Populated

**What happens**: You access `store.architecture.value` but ArchitectureAnalyzer failed or was skipped. Raises `LookupError`.

**Why it's bad**: Crashes when optional analyzer didn't run.

**Prevention**: Always check `.available`:

```python
# WRONG - crashes if not populated
modules = store.architecture.value.modules

# RIGHT
if not store.architecture.available:
    return []
modules = store.architecture.value.modules
```

---

## Category 4: Wrong Results

### FM-13: Gini Formula Wrong

**What happens**: You implement Gini but forget to sort values ascending first. Or use wrong index (0-indexed vs 1-indexed).

**Why it's bad**: impl_gini, centrality_gini, knowledge_gini all wrong. HOLLOW_CODE misfires.

**Prevention**: Use EXACT formula:

```python
def gini(values: List[float]) -> float:
    if not values or sum(values) == 0:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)

    # i is 1-indexed in formula
    numerator = sum((i + 1) * v for i, v in enumerate(sorted_values))
    denominator = n * sum(sorted_values)

    return (2 * numerator / denominator) - (n + 1) / n
```

---

### FM-14: BFS vs DFS for Depth

**What happens**: You use DFS instead of BFS for computing depth. Get longest path instead of shortest.

**Why it's bad**: depth values are wrong. Entry points don't have depth=0.

**Prevention**: Use BFS:

```python
# WRONG - DFS gives longest path
def dfs_depth(node, graph, visited):
    ...

# RIGHT - BFS gives shortest path
def bfs_depths(entry_points, graph):
    depths = {ep: 0 for ep in entry_points}
    queue = deque(entry_points)
    while queue:
        node = queue.popleft()
        for neighbor in graph.adjacency.get(node, []):
            if neighbor not in depths:
                depths[neighbor] = depths[node] + 1
                queue.append(neighbor)
    return depths
```

---

### FM-15: Confidence Always 0 or 1

**What happens**: You compute confidence as binary (condition met = 1, not met = 0). All findings have confidence 1.0.

**Why it's bad**: No way to rank findings by severity. All look equally bad.

**Prevention**: Use margin formula:

```python
# WRONG - binary
confidence = 1.0 if condition_met else 0.0

# RIGHT - margin-based
margin = (actual_pctl - threshold) / (1.0 - threshold)
confidence = max(0, min(1, margin))
```

---

### FM-16: Weight Sums ≠ 1.0

**What happens**: You add a term to risk_score but forget to adjust other weights. Weights sum to 1.15.

**Why it's bad**: Composites exceed [0,1] range. Display shows 11.5/10. User confused.

**Prevention**: Verify weight sums:

```python
# In composite function
weights = [0.25, 0.20, 0.20, 0.20, 0.15]
assert abs(sum(weights) - 1.0) < 0.001, f"Weights sum to {sum(weights)}"
```

---

## Category 5: Performance Disasters

### FM-17: O(n²) Clone Detection on Large Codebase

**What happens**: You do pairwise NCD comparison for all file pairs. 10,000 files = 50 million comparisons. Analysis takes hours.

**Why it's bad**: Unusable on real codebases.

**Prevention**: Use LSH for large codebases:

```python
if len(files) < 1000:
    # Direct pairwise OK
    pairs = [(a, b) for a, b in itertools.combinations(files, 2)]
else:
    # Use MinHash + LSH
    pairs = lsh_candidate_pairs(files)
```

---

### FM-18: Loading Entire Git History in Memory

**What happens**: You load all commits for all files into memory. Large repo with 100k commits = OOM.

**Why it's bad**: Crashes on real projects with long history.

**Prevention**: Stream git log, limit commits:

```python
# WRONG - load all
commits = list(repo.iter_commits())

# RIGHT - stream with limit
for commit in itertools.islice(repo.iter_commits(), MAX_COMMITS):
    process(commit)
```

---

### FM-19: Recomputing Signals Multiple Times

**What happens**: You compute pagerank in StructuralAnalyzer. Then compute it again in a plugin. Then again in a finder.

**Why it's bad**: Wastes CPU. May get inconsistent values if implementations differ.

**Prevention**: Single-owner rule. Signal computed ONCE, stored in SignalField, read everywhere:

```python
# WRONG - multiple computations
class StructuralAnalyzer:
    def analyze(self):
        pagerank = compute_pagerank(graph)  # First time

class CentralityPlugin:
    def compute(self):
        pagerank = compute_pagerank(graph)  # Second time, maybe different

# RIGHT - compute once, store, read
# StructuralAnalyzer computes and stores
# Everyone else reads from store.signal_field
```

---

## Category 6: Integration Failures

### FM-20: Analyzer Cycle

**What happens**: AnalyzerA requires slot X, provides Y. AnalyzerB requires Y, provides X. Topo-sort fails.

**Why it's bad**: Startup crash. Nothing runs.

**Prevention**: DAG must be acyclic. If you need circular data, split into phases:

```python
# WRONG - cycle
AnalyzerA: requires={"semantics"}, provides={"structural"}
AnalyzerB: requires={"structural"}, provides={"semantics"}

# RIGHT - no cycle, or use two-phase
AnalyzerA: requires={}, provides={"structural_basic"}
AnalyzerB: requires={"structural_basic"}, provides={"semantics"}
AnalyzerA_Enrichment: requires={"semantics"}, provides={"structural_enriched"}
```

---

### FM-21: Wave 2 Runs Too Early

**What happens**: SignalFusionAnalyzer doesn't have `run_last=True`. Topo-sort puts it in the middle. It runs before temporal data is ready.

**Why it's bad**: SignalField has empty temporal signals. All temporal finders produce wrong results.

**Prevention**: Mark SignalFusionAnalyzer as `run_last=True`:

```python
class SignalFusionAnalyzer:
    run_last = True  # CRITICAL - must run after all Wave 1 analyzers
```

---

### FM-22: Test Passes Locally, Fails in CI

**What happens**: Your finder iterates over `dict.keys()`. Order is insertion-order in Python 3.7+ but your test assumes alphabetical. CI has different insertion order.

**Why it's bad**: Flaky tests. CI randomly fails.

**Prevention**: Sort when order matters:

```python
# WRONG - order-dependent
for path in store.signal_field.value.per_file.keys():

# RIGHT - deterministic
for path in sorted(store.signal_field.value.per_file.keys()):
```

---

## Quick Reference: The 22 Ways to Fail

| # | Failure Mode | Category | Symptom |
|---|--------------|----------|---------|
| 1 | Signal name typos | Silent corruption | Finder never runs |
| 2 | Instability None not guarded | Silent corruption | Crash or NaN |
| 3 | Wrong fusion order | Silent corruption | WEAK_LINK random |
| 4 | Percentile formula wrong | Silent corruption | Thresholds off |
| 5 | Polarity confusion | Silent corruption | Best files flagged |
| 6 | Forgot tier check | No findings | ABSOLUTE tier silent |
| 7 | Forgot hotspot filter | Wrong findings | Ancient files flagged |
| 8 | Requires not declared | No findings | Finder runs too early |
| 9 | Wrong store slot | Wrong results | Stale data used |
| 10 | Division by zero | Crash | Import-free file |
| 11 | Empty collection | Crash | No temporal data |
| 12 | Slot not populated | Crash | Analyzer skipped |
| 13 | Gini formula wrong | Wrong results | HOLLOW_CODE misfires |
| 14 | BFS vs DFS | Wrong results | Depth values wrong |
| 15 | Binary confidence | Poor UX | All findings equal |
| 16 | Weights ≠ 1.0 | Wrong results | Scores > 10 |
| 17 | O(n²) clones | Performance | Hours on large repo |
| 18 | All git in memory | Performance | OOM crash |
| 19 | Signal recomputation | Performance | Slow + inconsistent |
| 20 | Analyzer cycle | Crash | Startup fails |
| 21 | Wave 2 too early | Wrong results | Empty temporal |
| 22 | Non-deterministic order | Flaky tests | CI fails randomly |

---

## How to Not Fail

1. **Use the Signal enum** - Never use string signal names
2. **Check `.available` before `.value`** - Always
3. **Guard None and division** - Every time
4. **Follow fusion order exactly** - 6 steps, that order
5. **Check polarity in signals.md** - Before writing finder condition
6. **Declare all requires** - Everything the finder reads
7. **Test on edge cases** - Empty, single file, no git, flat project
8. **Sort when iterating dicts** - If order matters to output
9. **Run `make all` constantly** - After every change

The spec is designed to prevent these. If you follow it exactly, you won't hit them. If you improvise, you will.
