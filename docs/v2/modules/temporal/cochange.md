# Co-Change Analysis

Co-change (temporal coupling) detection from git commit history. Two files are temporally coupled if they change together more often than chance predicts.

## Core Concepts

### Co-change count

The number of commits in which both file A and file B appear:

```
cochange_count(A, B) = |{commit c : A in c.files AND B in c.files}|
```

### Lift

Lift measures how much more frequently A and B co-change than expected under independence. For the formula definition, see `registry/signals.md` (via the co-change enrichment described in `ir-spec.md`):

```
P(A) = commits_touching(A) / total_commits
P(B) = commits_touching(B) / total_commits
P(A AND B) = cochange_count(A, B) / total_commits

lift(A, B) = P(A AND B) / (P(A) * P(B))
```

Interpretation:
- `lift = 1.0`: A and B change together exactly as often as chance predicts (independent)
- `lift > 2.0`: A and B change together much more than chance -- temporal coupling signal
- `lift < 0.5`: A and B actively avoid changing together (anti-correlation)

**Status**: EXISTS. No formula change in v2.

### Confidence

Confidence measures the conditional probability that one file changes given the other changed:

```
confidence(A -> B) = cochange_count(A, B) / total_changes(A)    # P(B | A)
confidence(B -> A) = cochange_count(A, B) / total_changes(B)    # P(A | B)
```

The current implementation stores both directional confidences (`confidence_a_b`, `confidence_b_a`). v2 `PairDynamics` takes the max:

```
confidence = max(P(B|A), P(A|B))
```

Rationale: for coupling detection, we care about the stronger direction. If changing A always requires changing B (but B often changes alone), the coupling is real from A's perspective.

**Status**: EXISTS (directional). v2 simplifies to max.

### Temporal coupling score

The fused coupling score used for edge enrichment:

```
temporal_coupling(A, B) = lift(A, B) * confidence(A, B)
```

This combines "how surprising is their co-occurrence" (lift) with "how reliable is the coupling" (confidence). High lift + high confidence = strong temporal coupling.

**Status**: v2 NEW (as an explicit score). The components exist today; the product is new.

## Filtering

### Bulk commit filtering

Commits touching more than `max_files_per_commit` files (default: 50) are excluded from co-change computation:

```python
relevant = [f for f in commit.files if f in analyzed_files]
if not relevant or len(relevant) > max_files_per_commit:
    continue
```

Rationale: a single commit touching 200 files (mass reformat, dependency update, initial commit) would generate 200*199/2 = 19,900 spurious co-change pairs. These pairs reflect the commit's bulk nature, not any semantic relationship.

**Status**: EXISTS. No change in v2.

### Analyzed files filtering

Only files present in `analyzed_files` (the current codebase scan) are included in co-change pairs. This prevents ghost pairs between deleted files or files outside the analysis scope.

**Status**: EXISTS. No change in v2.

### Minimum co-change threshold

Pairs with `cochange_count < min_cochanges` (default: 2) are excluded from the result matrix:

```python
if count < min_cochanges:
    continue
```

A single co-occurrence is noise. Two or more establishes a pattern.

**Status**: EXISTS. No change in v2.

## Co-Change Matrix Construction

The algorithm:

```
1. For each commit in history:
   a. Filter files to analyzed_files
   b. Skip if empty or > max_files_per_commit
   c. Increment file_change_counts[f] for each file f
   d. For each pair (a, b) in sorted(relevant) x sorted(relevant) where a < b:
      Increment pair_counts[(a, b)]

2. For each pair with count >= min_cochanges:
   Compute lift and confidence
   Create CoChangePair / PairDynamics entry

3. Return sparse matrix (only pairs above threshold)
```

**Complexity**: O(C x F^2) where C = number of commits and F = max files per commit (capped at 50). With 5000 commits and 50 max files: 5000 x 1225 = ~6M pair increment operations. In practice, most commits touch 2-5 files, so the actual cost is much lower.

**Status**: EXISTS. The algorithm does not change in v2.

## v2: PairDynamics Extension

In v2, the co-change matrix produces `PairDynamics` instead of `CoChangePair`. The key addition:

### `has_structural_edge`

This field indicates whether the co-changing pair also has a structural (import) edge in the code graph. It enables a critical cross-spine join:

- **High temporal coupling + structural edge**: expected coupling (they import each other, so they change together)
- **High temporal coupling + NO structural edge**: hidden coupling (they change together but have no visible dependency -- possible shared concept, shared resource, or missing abstraction)
- **Structural edge + LOW temporal coupling**: potentially dead dependency (one imports the other but they rarely change together)

temporal/ sets `has_structural_edge = False` for all pairs. The graph/ module updates it after the two spines merge. This is the co-change enrichment join point described in `01-contracts.md`.

### `temporal_coupling`

The derived score `lift * confidence`, stored for direct use by finders without recomputation.

## Downstream Use

### graph/ enrichment

graph/ reads the co-change matrix and:
1. Annotates structural edges with their temporal coupling score
2. Creates virtual edges for high-coupling pairs without structural edges (hidden coupling candidates)
3. Flags structural edges with zero temporal coupling (dead dependency candidates)

### insights/ finders

- **HiddenCoupling finder**: pairs with `lift > 2.0` and `has_structural_edge = False`
- **DeadDependency finder**: pairs with structural edge and `lift < 0.5` (or zero co-changes)
- **UnstableFile finder**: files appearing in many high-coupling pairs

## What Exists Today

The entire co-change pipeline exists and works:

| Component | File | Status |
|-----------|------|--------|
| `build_cochange_matrix()` | `cochange.py` | EXISTS, no v2 changes |
| `CoChangePair` | `models.py` | EXISTS, superseded by `PairDynamics` |
| `CoChangeMatrix` | `models.py` | EXISTS, retained |
| Bulk commit filtering | `cochange.py` | EXISTS |
| Lift computation | `cochange.py` | EXISTS |
| Confidence computation | `cochange.py` | EXISTS (directional, v2 takes max) |
| `PairDynamics` model | `models.py` | v2 NEW |
| `temporal_coupling` score | -- | v2 NEW |
| `has_structural_edge` flag | -- | v2 NEW (set by graph/) |
