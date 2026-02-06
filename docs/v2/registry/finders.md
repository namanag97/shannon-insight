# Registry: Finding Catalog

Every finding type in Shannon Insight. Each finder declares which signals it requires (from `signals.md`), its condition, severity, evidence template, and suggestion template.

**Rules**:
- A finder only runs if ALL its required signals are available in the AnalysisStore.
- If a signal is missing (e.g., no git = no bus_factor), the finder is gracefully skipped.
- This enables demand-driven evaluation: trace from active finders → required signals → compute only those.

**Severity values**: All severity numbers are hand-tuned initial values, not calibrated. They define relative ordering (HIGH_RISK_HUB at 1.0 is worse than NAMING_DRIFT at 0.45). Exact values will be adjusted based on real-world usage. The seemingly precise values (0.71, 0.55) are intentional rank separators, not claims of measurement precision.

**Intermediate terms**: Some finders reference computed intermediates that are NOT numbered signals in `signals.md`:
- `cochange_lift`, `cochange_confidence` — derived from the co-change matrix (AnalysisStore.cochange)
- `clone_ratio` — `|files in NCD clone pairs| / |total files|`, computed during wiring_score
- `violation_rate` — `violating_cross_module_edges / total_cross_module_edges`, computed during architecture_health
- `raw_risk` — pre-percentile weighted sum used by health Laplacian (see `composites.md`)
- `graph edges` — structural dependency edges from the DependencyGraph

These are data-structure reads, not standalone signal computations. They don't need signal IDs.

**Hotspot filter**: For FILE-scope findings that involve temporal signals (HIGH_RISK_HUB, UNSTABLE_FILE, KNOWLEDGE_SILO, BUG_ATTRACTOR, REVIEW_BLINDSPOT, WEAK_LINK), the finder MUST also check: `total_changes > median(total_changes)`. This ensures we only flag files that are actively being worked on. Structural-only findings (ORPHAN_CODE, HOLLOW_CODE, PHANTOM_IMPORTS, COPY_PASTE_CLONE, FLAT_ARCHITECTURE, NAMING_DRIFT) are exempt — they're problems regardless of change frequency.

**Hotspot median definition**:
```python
def compute_hotspot_median(store: AnalysisStore) -> float:
    """
    Compute median of total_changes across non-test files.
    Excludes TEST role files to avoid skewing by test churn.
    """
    changes = [
        store.churn[path].total_changes
        for path in store.file_metrics
        if store.roles.get(path) != "TEST"
        and path in store.churn
    ]
    return statistics.median(changes) if changes else 0.0
```

---

## Confidence Scoring Formula

Every finder computes a confidence score in [0, 1] using the **margin formula**:

```python
def compute_confidence(
    triggered_conditions: List[Tuple[str, float, float, str]]
    # (signal_name, actual_value, threshold, polarity)
) -> float:
    """
    Confidence = mean of normalized margins across all triggered conditions.

    For each condition that fired:
    - If polarity == "high_is_bad" (e.g., pagerank): margin = (actual - threshold) / (1.0 - threshold)
    - If polarity == "high_is_good" (e.g., bus_factor): margin = (threshold - actual) / threshold

    margin is clamped to [0, 1].
    """
    if not triggered_conditions:
        return 0.0

    margins = []
    for signal, actual, threshold, polarity in triggered_conditions:
        if polarity == "high_is_bad":
            # Higher value = worse. Margin = how much above threshold.
            margin = (actual - threshold) / (1.0 - threshold) if threshold < 1.0 else 0.0
        else:  # high_is_good
            # Lower value = worse. Margin = how much below threshold.
            margin = (threshold - actual) / threshold if threshold > 0.0 else 0.0
        margins.append(max(0.0, min(1.0, margin)))

    return sum(margins) / len(margins)

# Example: HIGH_RISK_HUB
# pctl(pagerank) = 0.95, threshold = 0.90, polarity = "high_is_bad"
# margin = (0.95 - 0.90) / (1.0 - 0.90) = 0.05 / 0.10 = 0.50
#
# pctl(blast_radius) = 0.98, threshold = 0.90, polarity = "high_is_bad"
# margin = (0.98 - 0.90) / (1.0 - 0.90) = 0.08 / 0.10 = 0.80
#
# confidence = mean([0.50, 0.80]) = 0.65
```

---

## Signal Polarity in Finder Conditions

Every finder condition MUST respect signal polarity. This table shows how each finder interprets its signals:

| Finder | Signal | Polarity | Condition interpretation |
|--------|--------|----------|--------------------------|
| HIGH_RISK_HUB | pagerank | high=BAD | `pctl > 0.90` → "too central" |
| HIGH_RISK_HUB | blast_radius_size | high=BAD | `pctl > 0.90` → "too impactful" |
| HIGH_RISK_HUB | cognitive_load | high=BAD | `pctl > 0.90` → "too complex" |
| GOD_FILE | cognitive_load | high=BAD | `pctl > 0.90` → "too complex" |
| GOD_FILE | semantic_coherence | high=GOOD | `pctl < 0.20` → "too unfocused" |
| KNOWLEDGE_SILO | bus_factor | high=GOOD | `≤ 1.5` → "too few authors" |
| KNOWLEDGE_SILO | pagerank | high=BAD | `pctl > 0.75` → "too central" |
| BUG_ATTRACTOR | fix_ratio | high=BAD | `> 0.4` → "too many bug fixes" |
| BUG_ATTRACTOR | pagerank | high=BAD | `pctl > 0.75` → "too central" |
| REVIEW_BLINDSPOT | pagerank | high=BAD | `pctl > 0.75` → "too central" |
| REVIEW_BLINDSPOT | bus_factor | high=GOOD | `≤ 1.5` → "too few authors" |
| HOLLOW_CODE | stub_ratio | high=BAD | `> 0.5` → "too incomplete" |
| HOLLOW_CODE | impl_gini | high=BAD | `> 0.6` → "too uneven" |
| NAMING_DRIFT | naming_drift | high=BAD | `> 0.7` → "filename misleads" |
| ZONE_OF_PAIN | abstractness | neutral | `< 0.3` → "too concrete" |
| ZONE_OF_PAIN | instability | neutral | `< 0.3` → "too stable" (hard to change) |

**Validation rule**: Before using a signal in a finder condition, assert its polarity matches the condition direction:

```python
def validate_finder_condition(signal: Signal, operator: str, threshold: float):
    """Validate that finder condition respects signal polarity."""
    meta = REGISTRY[signal]

    if operator == ">" and meta.polarity == "high_is_good":
        raise ValueError(f"Signal {signal} is high=GOOD but condition uses > (expecting bad)")

    if operator == "<" and meta.polarity == "high_is_bad":
        raise ValueError(f"Signal {signal} is high=BAD but condition uses < (expecting good)")

    # neutral polarity: both directions are valid
```

---

## Existing Findings (upgraded with multi-IR evidence)

### HIGH_RISK_HUB

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 1.0 |
| **Requires** | `pagerank`, `blast_radius_size`, `cognitive_load`, `churn_trajectory`, `total_changes` |
| **Condition** | `pctl(pagerank) > 0.90 AND pctl(blast_radius_size) > 0.90 AND (pctl(cognitive_load) > 0.90 OR churn_trajectory ∈ {CHURNING, SPIKING})` |
| **Confidence** | `mean(margin_above_threshold(signal, threshold) for each condition)` |
| **Evidence** | [IR3] pagerank + blast radius, [IR5t] churn + fix_ratio, [IR2] concept_count, [IR5t] bus_factor, [IR5s] Δh (health Laplacian) |
| **Suggestion** | "Split responsibilities. Pair-program to spread knowledge." |
| **Effort** | HIGH |
| **Status** | Exists in v1. v2 adds multi-IR evidence. |

### HIDDEN_COUPLING

| Field | Value |
|---|---|
| **Scope** | FILE_PAIR |
| **Severity** | 0.9 |
| **Requires** | `cochange_lift`, `cochange_confidence`, graph edges |
| **Condition** | `lift ≥ 2.0 AND confidence ≥ 0.5 AND no structural edge between pair` |
| **Evidence** | [G1] no import edge, [G4] co-change count + lift + confidence, [G6] semantic similarity (if available) |
| **Suggestion** | "Extract shared concept or make dependency explicit." |
| **Effort** | MEDIUM |
| **Status** | Exists in v1. v2 adds distance space evidence. |

### GOD_FILE

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.8 |
| **Requires** | `cognitive_load`, `semantic_coherence` |
| **Condition** | `pctl(cognitive_load) > 0.90 AND pctl(semantic_coherence) < 0.20` |
| **Evidence** | [IR1] function_count, [IR2] concept_count + concept_entropy, [IR5] cognitive_load percentile, coherence percentile |
| **Suggestion** | "Split by concept clusters. Each concept = a candidate file." |
| **Effort** | HIGH |
| **Status** | Exists in v1. |

### UNSTABLE_FILE

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.7 |
| **Requires** | `churn_trajectory`, `total_changes` |
| **Condition** | `churn_trajectory ∈ {CHURNING, SPIKING} AND total_changes > median(total_changes)` |
| **Evidence** | [IR5t] trajectory, total changes, churn_slope, churn_cv |
| **Suggestion** | "Investigate why this file isn't stabilizing. Check fix_ratio." |
| **Effort** | MEDIUM |
| **Status** | Exists in v1. |

### BOUNDARY_MISMATCH

| Field | Value |
|---|---|
| **Scope** | MODULE |
| **Severity** | 0.6 |
| **Requires** | `boundary_alignment`, `community`, `file_count` |
| **Condition** | `boundary_alignment < 0.7 AND file_count ≥ 3` |
| **Evidence** | [IR3] community assignments, [IR4] boundary_alignment, file list with community IDs |
| **Suggestion** | "Directory boundary doesn't match dependency structure. Consider reorganizing." |
| **Effort** | HIGH |
| **Status** | Exists in v1. |

### DEAD_DEPENDENCY

| Field | Value |
|---|---|
| **Scope** | FILE_PAIR |
| **Severity** | 0.4 |
| **Requires** | graph edges, `cochange_lift`, `total_changes` |
| **Condition** | `structural_edge_exists AND cochange_count = 0 AND both files have 50+ commits` |
| **Evidence** | [G1] structural edge with symbols, [G4] zero co-changes over N commits |
| **Suggestion** | "This import may be dead. Verify the imported symbols are actually used." |
| **Effort** | LOW |
| **Status** | Exists in v1. |

### CHRONIC_PROBLEM

| Field | Value |
|---|---|
| **Scope** | (wraps another finding) |
| **Severity** | `base_severity × 1.25` (scales up) |
| **Requires** | finding persistence history |
| **Condition** | `same finding (by stable ID) persists across 3+ snapshots` |
| **Evidence** | [IR6] first_seen, persistence_count, trend |
| **Suggestion** | "This issue has persisted for N snapshots. Prioritize resolution." |
| **Effort** | (inherits from base finding) |
| **Status** | Exists in v1. |

---

## New Findings — AI Code Quality

### ORPHAN_CODE

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.55 |
| **Requires** | `is_orphan`, `role` |
| **Condition** | `is_orphan = true` (equivalent: `in_degree = 0 AND role ∉ {ENTRY_POINT, TEST}`) |
| **Evidence** | [IR3] in_degree = 0, depth = -1, [IR2] role, [G6] nearest semantic neighbor (if available) |
| **Suggestion** | "This file is unreachable. Wire it into [semantic neighbor] or remove it." |
| **Effort** | LOW |
| **Phase** | 6 |

### HOLLOW_CODE

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.71 |
| **Requires** | `stub_ratio`, `impl_gini` |
| **Condition** | `stub_ratio > 0.5 AND impl_gini > 0.6` |
| **Evidence** | [IR1] stub functions listed with body, [IR2] stub_ratio + impl_gini, [IR5t] author (bot/AI indicator) |
| **Suggestion** | "Implement the stub functions. Priority: functions called by other files." |
| **Effort** | MEDIUM |
| **Phase** | 6 |

### PHANTOM_IMPORTS

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.65 |
| **Requires** | `phantom_import_count` |
| **Condition** | `phantom_import_count > 0` |
| **Evidence** | [IR1] unresolved import statements with source references, [IR3] phantom_ratio for file |
| **Suggestion** | "Create missing module or replace with existing library." |
| **Effort** | MEDIUM |
| **Phase** | 6 |

### COPY_PASTE_CLONE

| Field | Value |
|---|---|
| **Scope** | FILE_PAIR |
| **Severity** | 0.50 |
| **Requires** | NCD clone pairs (from `graph/`) |
| **Condition** | `NCD(A, B) < 0.3` (after MinHash pre-filtering) |
| **Evidence** | [IR3] NCD score, file sizes, shared content estimate |
| **Suggestion** | "Extract shared logic into a common module." |
| **Effort** | MEDIUM |
| **Phase** | 6 |

### FLAT_ARCHITECTURE

| Field | Value |
|---|---|
| **Scope** | CODEBASE |
| **Severity** | 0.60 |
| **Requires** | `depth` (max), `glue_deficit` |
| **Condition** | `max_depth ≤ 1 AND glue_deficit > 0.5` |
| **Evidence** | [IR3] max depth, glue_deficit, internal_ratio |
| **Suggestion** | "Add composition layer. Many leaf modules exist but nothing orchestrates them." |
| **Effort** | HIGH |
| **Phase** | 6 |

### NAMING_DRIFT

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.45 |
| **Requires** | `naming_drift` |
| **Condition** | `naming_drift > 0.7` |
| **Evidence** | [IR2] filename tokens vs content concept tokens, cosine similarity |
| **Suggestion** | "Rename file to match its actual content, or extract mismatched logic." |
| **Effort** | LOW |
| **Phase** | 6 |

---

## New Findings — Social / Team

### KNOWLEDGE_SILO

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.70 |
| **Requires** | `bus_factor`, `pagerank` |
| **Condition** | `bus_factor ≤ 1.5 AND pctl(pagerank) > 0.75` |
| **Evidence** | [IR5t] bus_factor, author list, [IR3] pagerank percentile |
| **Suggestion** | "Pair-program or rotate ownership. Single point of knowledge failure." |
| **Effort** | LOW |
| **Phase** | 6 |

### CONWAY_VIOLATION

| Field | Value |
|---|---|
| **Scope** | MODULE_PAIR |
| **Severity** | 0.55 |
| **Requires** | author overlap (G5), structural coupling |
| **Condition** | `d_author(M₁, M₂) > 0.8 AND structural_coupling(M₁, M₂) > 0.3` |
| **Evidence** | [G5] author distance, [G1] structural coupling, module names |
| **Suggestion** | "Coupled modules maintained by different teams. Align team boundaries." |
| **Effort** | HIGH |
| **Phase** | 6 |

### REVIEW_BLINDSPOT

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.80 |
| **Requires** | `pagerank`, `bus_factor`, test mapping |
| **Condition** | `pctl(pagerank) > 0.75 AND bus_factor ≤ 1.5 AND no_test_file` |
| **Evidence** | [IR3] centrality, [IR5t] author distribution, test file presence |
| **Suggestion** | "High-centrality code with single owner and no tests. Add tests and reviewer." |
| **Effort** | MEDIUM |
| **Phase** | 6 |

---

## New Findings — Architecture

### LAYER_VIOLATION

| Field | Value |
|---|---|
| **Scope** | MODULE_PAIR |
| **Severity** | 0.52 |
| **Requires** | `layer_violation_count`, layer assignments |
| **Condition** | Backward or skip edge in inferred layer ordering |
| **Evidence** | [IR4] source/target layers, violating import symbols |
| **Suggestion** | "Inject dependency or restructure to respect layer ordering." |
| **Effort** | MEDIUM |
| **Phase** | 6 |

### ZONE_OF_PAIN

| Field | Value |
|---|---|
| **Scope** | MODULE |
| **Severity** | 0.60 |
| **Requires** | `abstractness`, `instability` |
| **Condition** | `instability is not None AND abstractness < 0.3 AND instability < 0.3` |
| **Evidence** | [IR4] A, I, D values, dependents count |
| **Suggestion** | "Concrete and stable — hard to change. Extract interfaces or reduce dependents." |
| **Effort** | HIGH |
| **Phase** | 6 |

### ARCHITECTURE_EROSION

| Field | Value |
|---|---|
| **Scope** | CODEBASE |
| **Severity** | 0.65 |
| **Requires** | `layer_violation_count` over 3+ snapshots |
| **Condition** | `violation_rate increasing over 3+ snapshots` |
| **Evidence** | [IR4] violation_rate time series, [IR6] persistence |
| **Suggestion** | "Architecture is actively eroding. Schedule structural refactoring." |
| **Effort** | HIGH |
| **Phase** | 6 |

---

## New Findings — Cross-Dimensional

### WEAK_LINK

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.75 |
| **Requires** | `raw_risk`, graph edges (for health Laplacian Δh computation) |
| **Condition** | `Δh(f) > 0.4` (health Laplacian: file much worse than all neighbors) |
| **Evidence** | [IR5s] Δh value, neighbor raw_risk values, risk_score for display |
| **Suggestion** | "This file drags down its healthy neighborhood. Prioritize improvement." |
| **Effort** | MEDIUM |
| **Phase** | 6 |

### BUG_ATTRACTOR

| Field | Value |
|---|---|
| **Scope** | FILE |
| **Severity** | 0.70 |
| **Requires** | `fix_ratio`, `pagerank` |
| **Condition** | `fix_ratio > 0.4 AND pctl(pagerank) > 0.75` |
| **Evidence** | [IR5t] fix_ratio, fix commit list, [IR3] pagerank, blast radius |
| **Suggestion** | "40%+ of changes are bug fixes in a central file. Root-cause analysis needed." |
| **Effort** | MEDIUM |
| **Phase** | 6 |

### ACCIDENTAL_COUPLING

| Field | Value |
|---|---|
| **Scope** | FILE_PAIR |
| **Severity** | 0.50 |
| **Requires** | structural edges, concept clusters (from Phase 2 semantics) |
| **Condition** | `structural edge exists AND concept_overlap(A, B) < 0.2` where `concept_overlap = |concepts(A) ∩ concepts(B)| / |concepts(A) ∪ concepts(B)|` (Jaccard) |
| **Evidence** | [G1] structural edge, [IR2] concept lists, Jaccard overlap score |
| **Suggestion** | "Connected but unrelated concepts. Consider removing or abstracting the dependency." |
| **Effort** | MEDIUM |
| **Phase** | 6 |

---

## Hotspot and Tier Behavior

### Hotspot Classification

Each finder is either **hotspot-filtered** (requires `total_changes > median`) or **structural-only** (fires regardless of change frequency).

| Finder | Hotspot | Rationale |
|--------|---------|-----------|
| HIGH_RISK_HUB | yes | Temporal signals in condition |
| HIDDEN_COUPLING | no | Co-change is inherently temporal |
| GOD_FILE | no | Structural complexity, not change-driven |
| UNSTABLE_FILE | yes | Temporal by definition |
| BOUNDARY_MISMATCH | no | Structural (module scope) |
| DEAD_DEPENDENCY | no | Requires history but condition is structural |
| CHRONIC_PROBLEM | no | Meta-finder (wraps others) |
| ORPHAN_CODE | no | Structural-only |
| HOLLOW_CODE | no | Structural-only |
| PHANTOM_IMPORTS | no | Structural-only |
| COPY_PASTE_CLONE | no | Structural-only |
| FLAT_ARCHITECTURE | no | Structural-only (codebase scope) |
| NAMING_DRIFT | no | Structural-only |
| KNOWLEDGE_SILO | yes | Temporal (bus_factor) + structural |
| CONWAY_VIOLATION | no | Module scope, social signal |
| REVIEW_BLINDSPOT | yes | Temporal (bus_factor) + structural |
| LAYER_VIOLATION | no | Structural (architecture) |
| ZONE_OF_PAIN | no | Structural (Martin metrics) |
| ARCHITECTURE_EROSION | no | Requires snapshots, not hotspot |
| WEAK_LINK | yes | Cross-dimensional, health Laplacian |
| BUG_ATTRACTOR | yes | Temporal (fix_ratio) |
| ACCIDENTAL_COUPLING | no | Structural + semantic |

### Tier Behavior

Which finders fire in which normalization tier.

| Finder | ABSOLUTE (<15) | BAYESIAN (15-50) | FULL (50+) | Notes |
|--------|---------------|-----------------|------------|-------|
| HIGH_RISK_HUB | skip | fire | fire | Requires percentile conditions |
| HIDDEN_COUPLING | fire | fire | fire | Uses lift threshold (absolute) |
| GOD_FILE | skip | fire | fire | Requires percentile conditions |
| UNSTABLE_FILE | fire | fire | fire | Uses enum + median (relative) |
| BOUNDARY_MISMATCH | skip | fire | fire | Needs ≥2 modules |
| DEAD_DEPENDENCY | fire | fire | fire | Uses absolute commit count |
| CHRONIC_PROBLEM | fire | fire | fire | Meta-finder, depends on base |
| ORPHAN_CODE | fire | fire | fire | Boolean condition |
| HOLLOW_CODE | fire | fire | fire | Absolute thresholds |
| PHANTOM_IMPORTS | fire | fire | fire | Count > 0 |
| COPY_PASTE_CLONE | fire | fire | fire | NCD threshold (absolute) |
| FLAT_ARCHITECTURE | fire | fire | fire | Absolute thresholds |
| NAMING_DRIFT | fire | fire | fire | Absolute threshold |
| KNOWLEDGE_SILO | skip | fire | fire | Requires percentile (pagerank) |
| CONWAY_VIOLATION | skip | fire | fire | Needs ≥2 modules + ≥3 authors |
| REVIEW_BLINDSPOT | skip | fire | fire | Requires percentile (pagerank) |
| LAYER_VIOLATION | skip | fire | fire | Needs ≥2 modules |
| ZONE_OF_PAIN | skip | fire | fire | Needs module Martin metrics |
| ARCHITECTURE_EROSION | skip | fire | fire | Needs ≥3 snapshots + modules |
| WEAK_LINK | skip | fire | fire | Needs raw_risk computation |
| BUG_ATTRACTOR | skip | fire | fire | Requires percentile (pagerank) |
| ACCIDENTAL_COUPLING | skip | fire | fire | Needs concept clusters (Phase 2) |

**ABSOLUTE tier**: Only 8 of 22 finders fire. These use boolean, enum, count, or absolute threshold conditions that don't require percentile normalization.

---

## Finding Identity Keys

Each finding has a **stable identity key** for tracking across snapshots (CHRONIC_PROBLEM detection, finding lifecycle in persistence).

```
identity_key = (finder_name, scope, *scope_specific_key)

FILE scope:       (finder, file_path)
FILE_PAIR scope:  (finder, sorted(file_a, file_b))
MODULE scope:     (finder, module_name)
MODULE_PAIR:      (finder, sorted(mod_a, mod_b))
CODEBASE scope:   (finder,)
```

**Rename awareness**: When persistence detects a file rename (via git rename tracking), the identity key is updated to use the new path. This prevents rename → finding disappears → finding reappears as new.

---

## Finding Summary

| Category | Count | Exists | New |
|---|---|---|---|
| Structural (v1) | 7 | 7 | 0 |
| AI Code Quality | 6 | 0 | 6 |
| Social / Team | 3 | 0 | 3 |
| Architecture | 3 | 0 | 3 |
| Cross-Dimensional | 3 | 0 | 3 |
| **Total** | **22** | **7** | **15** |
