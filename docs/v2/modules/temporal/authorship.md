# Authorship and Intent Analysis

Per-file, per-module, and codebase-level analysis of who changes code and why. Covers D7 (AUTHORSHIP) and D8 (INTENT) dimensions.

## Author Analysis (D7 AUTHORSHIP)

### Per-file author distribution

For each file, accumulate author commit counts from `FileHistory.commits`:

```
authors[email] += 1   for each commit touching the file
```

This produces a discrete probability distribution over authors:

```
p(a) = commits_by_author(a) / total_commits_for_file
```

### Author entropy

Shannon entropy of the author distribution. For the formula, see `registry/signals.md #32`.

```
H = -sum(p(a) * log2(p(a)) for a in authors)
```

- `H = 0`: single author (complete knowledge silo)
- `H = log2(k)`: k equally-contributing authors (perfectly distributed)

**Status**: The entropy computation exists in `math/entropy.py`. Currently applied to authors in the insights layer (`insights/analyzers/per_file.py`). v2 moves this computation into temporal/ where it belongs, since author data comes from git (the temporal source).

### Bus factor

Effective author count derived from entropy. For the formula, see `registry/signals.md #31`.

```
bus_factor = 2^H
```

This is the "equivalent number of equally-contributing authors." It is a continuous value (not rounded to an integer), reflecting fractional author contributions.

- `bus_factor = 1.0`: single author (maximum risk)
- `bus_factor = 3.0`: equivalent to 3 equally-contributing authors

**Status**: Currently computed in insights layer. v2 moves to temporal/.

### Primary author

The mode of the author distribution:

```
primary_author     = argmax(commits_by_author)
primary_author_pct = max(commits_by_author.values()) / total_commits
```

- `primary_author_pct > 0.8`: this file is essentially single-owner
- `primary_author_pct < 0.5`: no single dominant author

**Status**: v2 NEW.

## Per-Module Author Analysis (D7 at Scale S5)

Module-level authorship aggregates computed in `ModuleDynamics`:

### Knowledge Gini

For the formula, see `registry/signals.md #47`.

```
For each module:
    contributions = [commit_count for each author who touched any file in module]
    knowledge_gini = gini_coefficient(contributions)
```

- `Gini > 0.7`: one author dominates the module (knowledge silo)
- `Gini < 0.3`: knowledge is well-distributed

The Gini computation uses the existing `math/statistics.py::gini_coefficient()`.

**Status**: v2 NEW.

### Coordination cost

For the formula, see `registry/signals.md #46`.

```
For each commit touching a file in module M:
    count distinct authors in that commit
coordination_cost(M) = mean(distinct_authors_per_commit)
```

High coordination cost means multiple people must coordinate to make changes to a module. This is a Conway's Law signal: high coordination cost suggests the module spans team boundaries.

**Note**: "distinct authors in that commit" means across the commit's file list, not just within the module. A commit by one author has coordination_cost = 1 regardless of how many module files it touches. This measures commit-level team involvement.

**Status**: v2 NEW.

### Module bus factor

For the formula, see `registry/signals.md #48`.

```
module_bus_factor = min(bus_factor(f) for f in high_centrality_files_in_module)
```

Where "high centrality" means top quartile by pagerank within the module. The module's bus factor is limited by its most critical knowledge silo.

When centrality data is unavailable (temporal/ running before graph/), falls back to `min(bus_factor(f) for f in module.files)`.

**Status**: v2 NEW.

### Author overlap (Jaccard)

For Conway's Law correlation, compute pairwise author overlap between modules:

```
authors(M) = {a : a committed to any file in M}

jaccard(M1, M2) = |authors(M1) AND authors(M2)| / |authors(M1) OR authors(M2)|
```

Weighted variant (accounts for commit volume):

```
For each author a:
    w(a, M) = commits_by(a, M) / total_commits(M)

weighted_jaccard(M1, M2) = sum(min(w(a, M1), w(a, M2))) / sum(max(w(a, M1), w(a, M2)))
```

**Status**: v2 NEW.

### Conway's Law correlation

Correlation between structural coupling and author overlap across module pairs:

```
For each pair of modules (M1, M2):
    structural_coupling = edge_count(M1, M2) / max_possible_edges(M1, M2)
    author_overlap      = weighted_jaccard(M1, M2)

conway_correlation = pearson(structural_coupling_vector, author_overlap_vector)
```

- High positive correlation: teams match module boundaries (Conway alignment)
- Low or negative correlation: teams do not match modules (Conway violation -- potential coordination problems)

This is computed in `CodebaseDynamics` and requires both temporal data (author overlap) and graph data (structural coupling). When graph data is unavailable, this field is `None`.

**Status**: v2 NEW.

## Intent Classification (D8 INTENT)

### Approach: keyword matching + diff shape

Each commit is classified by its **intent** -- why the change was made. v2 uses a two-signal approach:

1. **Keyword matching** on commit messages (primary signal)
2. **Diff shape** heuristics (secondary signal, for disambiguation)

### Fix ratio

For the formula, see `registry/signals.md #33`.

```
fix_keywords = {"fix", "bug", "patch", "hotfix", "resolve", "repair"}

is_fix(commit) = any(keyword in commit.message.lower() for keyword in fix_keywords)

fix_ratio(file) = count(is_fix(c) for c in file.commits) / total_commits(file)
```

- `fix_ratio > 0.4`: this file attracts bugs (40%+ of its changes are fixes)
- `fix_ratio < 0.1`: rarely needs fixing

**Status**: v2 NEW. Requires commit messages (added in v2 git log format).

### Refactor ratio

For the formula, see `registry/signals.md #34`.

```
refactor_keywords = {"refactor", "restructure", "reorganize", "clean", "simplify"}

is_refactor(commit) = any(keyword in commit.message.lower() for keyword in refactor_keywords)

refactor_ratio(file) = count(is_refactor(c) for c in file.commits) / total_commits(file)
```

- High refactor_ratio: file receives proactive maintenance (good signal)
- Zero refactor_ratio + high fix_ratio: reactive-only maintenance (risk signal)

**Status**: v2 NEW.

### Keyword matching details

Matching is case-insensitive substring matching on the commit subject line. The keyword sets are intentionally small and conservative to minimize false positives.

Additional intent categories (not currently surfaced as signals but tracked internally for future use):

| Intent | Keywords |
|--------|----------|
| Feature | `feat`, `feature`, `add`, `implement`, `introduce` |
| Test | `test`, `spec`, `coverage` |
| Docs | `doc`, `readme`, `comment` |
| Dependency | `bump`, `upgrade`, `dependency`, `deps` |
| CI | `ci`, `pipeline`, `workflow`, `deploy` |

A commit may match multiple categories. For `fix_ratio` and `refactor_ratio` computation, only the fix and refactor categories matter. The categories are not mutually exclusive: "fix test for auth" matches both fix and test.

### Diff shape (secondary signal)

When keyword matching is ambiguous, diff shape provides additional signal:

| Shape | Indicator |
|-------|-----------|
| Mostly deletions | Likely refactor or cleanup |
| Small, localized change | Likely bug fix |
| Large additions | Likely feature |
| Balanced add/delete | Likely refactor |

Diff shape analysis requires `git diff --stat` output, which is more expensive than `git log`. In v2, diff shape is **optional** and off by default. It can be enabled for higher-fidelity intent classification at the cost of additional subprocess calls.

**Status**: v2 NEW (planned, not in initial implementation).

## v2 Additions Summary

| Component | Dimension | Scale | Status |
|-----------|-----------|-------|--------|
| `author_entropy` per file | D7 | S4 | Moved from insights/ to temporal/ |
| `bus_factor` per file | D7 | S4 | Moved from insights/ to temporal/ |
| `primary_author` per file | D7 | S4 | NEW |
| `knowledge_gini` per module | D7 | S5 | NEW |
| `coordination_cost` per module | D7 | S5 | NEW |
| `module_bus_factor` per module | D7 | S5 | NEW |
| Author overlap (Jaccard) | D7 | S5 | NEW |
| Conway correlation | D7 | S6 | NEW |
| `fix_ratio` per file | D8 | S4 | NEW |
| `refactor_ratio` per file | D8 | S4 | NEW |
| Intent keyword matching | D8 | -- | NEW |
| Diff shape analysis | D8 | -- | NEW (optional, deferred) |
