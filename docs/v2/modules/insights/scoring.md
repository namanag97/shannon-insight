# insights/scoring -- Severity and Confidence Computation

**Status**: NEW (v1 has severity only; v2 adds confidence and evidence amplifiers)

## Overview

Every finding has two numeric scores:

- **Severity** [0, 1]: How bad is this problem? Defined per finding type in `registry/finders.md` as a base value, then adjusted by evidence strength.
- **Confidence** [0, 1]: How sure are we that this IS a problem? Computed from margin above threshold.

These are independent axes. A finding can have high severity but low confidence (e.g., a file barely crosses the GOD_FILE thresholds) or low severity but high confidence (e.g., NAMING_DRIFT with a clear 0.95 drift score).

## Confidence Computation

### Margin above threshold

Each finder condition involves one or more threshold comparisons (e.g., `pctl(pagerank) > 0.90`). Confidence measures how far above the threshold the actual values are.

For a single threshold condition:

```
margin(value, threshold) = (value - threshold) / (1 - threshold)
                         = clamp to [0, 1]
```

For a multi-condition finder, confidence is the mean margin across all conditions:

```
confidence = mean(margin(v_i, t_i) for each condition i)
```

### Example: HIGH_RISK_HUB

Conditions:
- `pctl(pagerank) > 0.90`
- `pctl(blast_radius_size) > 0.90`
- `pctl(cognitive_load) > 0.90 OR churn_trajectory in {CHURNING, SPIKING}`

For a file with pagerank pctl=0.97, blast_radius pctl=0.95, cognitive_load pctl=0.88, trajectory=CHURNING:

```
margin_pagerank  = (0.97 - 0.90) / (1.0 - 0.90) = 0.70
margin_blast     = (0.95 - 0.90) / (1.0 - 0.90) = 0.50
margin_cognitive = 0.0  (below threshold; but trajectory fires)
margin_trajectory = 1.0 (boolean condition met)

# The OR means we take max of the two sub-conditions
margin_third = max(0.0, 1.0) = 1.0

confidence = mean(0.70, 0.50, 1.0) = 0.73
```

### Special cases

**Boolean conditions** (e.g., `is_orphan = true`): margin is 1.0 if true, 0.0 if false.

**Enum conditions** (e.g., `churn_trajectory in {CHURNING, SPIKING}`): margin is 1.0 if the value matches, 0.0 otherwise. No partial credit.

**Percentile inversions** (e.g., `pctl(semantic_coherence) < 0.20` for GOD_FILE): invert the margin formula:

```
margin(value, threshold, inverted=True) = (threshold - value) / threshold
```

## Severity Computation

### Base severity

Each finding type has a base severity defined in `registry/finders.md`:

| Finding | Base Severity |
|---|---|
| HIGH_RISK_HUB | 1.0 |
| HIDDEN_COUPLING | 0.9 |
| REVIEW_BLINDSPOT | 0.8 |
| GOD_FILE | 0.8 |
| WEAK_LINK | 0.75 |
| HOLLOW_CODE | 0.71 |
| UNSTABLE_FILE | 0.7 |
| KNOWLEDGE_SILO | 0.7 |
| BUG_ATTRACTOR | 0.7 |
| PHANTOM_IMPORTS | 0.65 |
| ARCHITECTURE_EROSION | 0.65 |
| FLAT_ARCHITECTURE | 0.6 |
| BOUNDARY_MISMATCH | 0.6 |
| ZONE_OF_PAIN | 0.6 |
| ORPHAN_CODE | 0.55 |
| CONWAY_VIOLATION | 0.55 |
| LAYER_VIOLATION | 0.52 |
| COPY_PASTE_CLONE | 0.5 |
| ACCIDENTAL_COUPLING | 0.5 |
| NAMING_DRIFT | 0.45 |
| DEAD_DEPENDENCY | 0.4 |
| CHRONIC_PROBLEM | base x 1.25 |

### Evidence amplifier

The base severity is modulated by the strength of evidence:

```
adjusted_severity = base_severity * evidence_amplifier

evidence_amplifier = clamp(mean(evidence_strengths), 0.5, 1.0)
```

Where `evidence_strengths` is the list of margin values from each evidence item. This means:
- A finding that barely crosses thresholds gets severity reduced by up to 50%
- A finding that massively exceeds thresholds keeps its full base severity

### Chronic problem escalation

CHRONIC_PROBLEM wraps another finding and scales its severity:

```
chronic_severity = base_finding.severity * 1.25 * clamp(persistence_count / 10, 0.3, 1.0)
```

Capped at 1.0. A finding that has persisted for 10+ snapshots reaches maximum chronic severity.

## Evidence Chain Construction

Each finder builds an evidence chain by collecting items from multiple IR levels. The evidence chain is ordered from most concrete (structural facts) to most interpretive (composites and trends).

### Evidence ordering convention

```
1. IR1 (Syntactic)  -- raw structural facts (function count, stub ratio)
2. IR2 (Semantic)   -- role, concepts, naming
3. IR3 (Graph)      -- centrality, connectivity, cycles
4. IR4 (Architecture) -- layer assignments, Martin metrics
5. IR5t (Temporal)  -- churn, authors, fix ratio
6. IR5s (Signals)   -- composites, health Laplacian
```

### Constructing evidence items

Each evidence item is built by the finder from data in the signal field:

```python
Evidence(
    ir_source="IR3",
    signal="pagerank",
    value=0.087,
    percentile=95.0,
    description="Top 5% most central file"
)
```

The `description` field is a human-readable explanation that avoids jargon. It should answer "so what?" rather than just restating the number.

### Evidence from distance spaces (v2)

For cross-dimensional finders (WEAK_LINK, ACCIDENTAL_COUPLING), evidence includes distance space identifiers from the six distance spaces defined in `registry/signals.md`:

- G1: Dependency distance (structural edges)
- G2: Topological distance (shortest path)
- G3: Change distance (co-change lift)
- G4: Temporal distance (churn similarity)
- G5: Author distance (team overlap)
- G6: Semantic distance (concept similarity)

A disagreement between spaces IS the evidence:

```python
Evidence(
    ir_source="IR3",
    signal="d_dependency",
    value=0.1,          # close in dependency space
    percentile=None,
    description="Directly connected via import"
),
Evidence(
    ir_source="IR2",
    signal="d_semantic",
    value=0.85,          # far in semantic space
    percentile=None,
    description="Unrelated concepts (cosine similarity 0.15)"
)
```

## Ranking

After scoring, findings are sorted by a composite ranking key:

```
rank_key = severity * 0.7 + confidence * 0.3
```

This prioritizes high-severity findings but uses confidence as a tiebreaker. A high-severity/low-confidence finding ranks below a slightly-lower-severity/high-confidence one.

Within equal rank, secondary sort by:
1. Scope breadth (CODEBASE > MODULE > FILE)
2. Number of evidence items (more evidence = more actionable)
3. Finding type alphabetically (for stability)
