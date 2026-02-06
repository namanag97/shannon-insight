# Development Rehearsal: Finder Data Flow Traces

> **Enterprise verification**: Every finder traced end-to-end through store slots, signals, phases, and tiers.
> This document validates the spec is implementable with no dangling references.

---

## Rehearsal Format

For each finder:
1. **Store slots read** — what `store.X` fields does it access?
2. **Signals consumed** — which numbered signals from `signals.md`?
3. **Phase dependency** — earliest phase after which finder can run
4. **Tier behavior** — ABSOLUTE/BAYESIAN/FULL firing rules
5. **Edge cases** — what can go wrong, how does it degrade?
6. **Confidence formula** — which signals feed margin computation

---

## 1. HIGH_RISK_HUB (Existing, upgraded)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 1.0 |
| Hotspot | YES — requires `total_changes > median` |

### Store Slots Read
```
store.signal_field.per_file[path].pagerank          → #14
store.signal_field.per_file[path].blast_radius_size → #18
store.signal_field.per_file[path].cognitive_load    → #26
store.signal_field.per_file[path].churn_trajectory  → #28
store.signal_field.per_file[path].total_changes     → #27
store.signal_field.per_file[path].percentiles       → for pctl() evaluation
```

### Signal Dependencies
| Signal | # | Phase | Tier needs pctl? |
|--------|---|-------|------------------|
| pagerank | 14 | 0 | YES |
| blast_radius_size | 18 | 0 | YES |
| cognitive_load | 26 | 1 | YES |
| churn_trajectory | 28 | 3 | NO (enum) |
| total_changes | 27 | 3 | NO (median filter) |

### Phase Dependency
**Earliest: Phase 5** (needs `signal_field` which includes percentiles + composites)

### Tier Behavior
- **ABSOLUTE**: SKIP — condition requires `pctl(X) > 0.90` which is unavailable
- **BAYESIAN**: FIRE — Bayesian percentiles available
- **FULL**: FIRE — standard percentiles available

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| No git history | total_changes=0, churn_trajectory=DORMANT → hotspot filter excludes, finder effectively skipped |
| Single-file codebase | percentiles are trivial (all 1.0) → finder fires but meaningless |
| All files equal pagerank | percentiles spread evenly → likely no file exceeds 0.90 |

### Confidence Formula
```python
triggered = [
    ("pagerank", pctl_pr, 0.90, "high_is_bad"),
    ("blast_radius_size", pctl_blast, 0.90, "high_is_bad"),
    ("cognitive_load", pctl_cog, 0.90, "high_is_bad"),
]
# trajectory is enum, not a margin
confidence = mean(margin(s, t, p) for s, t, p in triggered if condition_met(s, t))
```

### Verification Status: ✅ VERIFIED

---

## 2. HIDDEN_COUPLING (Existing, upgraded)

| Attribute | Value |
|-----------|-------|
| Scope | FILE_PAIR |
| Severity | 0.9 |
| Hotspot | NO — co-change is inherently temporal |

### Store Slots Read
```
store.cochange.matrix[pair]           → lift, confidence, count
store.structural.graph.adjacency      → check if structural edge exists
```

### Signal Dependencies
| Signal | # | Phase | Notes |
|--------|---|-------|-------|
| (cochange_lift) | — | 3 | Intermediate, from cochange matrix |
| (cochange_confidence) | — | 3 | Intermediate |
| (graph_edges) | — | 0 | Structural edge check |

### Phase Dependency
**Earliest: Phase 3** (needs cochange matrix enrichment)

### Tier Behavior
- **ABSOLUTE**: FIRE — uses absolute lift/confidence thresholds (≥2.0, ≥0.5)
- **BAYESIAN**: FIRE
- **FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| No git history | cochange matrix empty → finder produces no findings |
| Very few commits | lift/confidence noisy → may produce false positives |
| Monorepo (many unrelated files) | high false positive rate, consider workspace filtering |

### Confidence Formula
```python
# Lift-based margin: how far above threshold
margin_lift = (lift - 2.0) / max(lift, 2.0)  # normalize to [0, ~1]
margin_conf = (confidence - 0.5) / 0.5
confidence = mean([margin_lift, margin_conf])
```

### Verification Status: ✅ VERIFIED

---

## 3. GOD_FILE (Existing)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.8 |
| Hotspot | NO — structural complexity, not change-driven |

### Store Slots Read
```
store.signal_field.per_file[path].cognitive_load     → #26
store.signal_field.per_file[path].semantic_coherence → #25
store.signal_field.per_file[path].percentiles
```

### Signal Dependencies
| Signal | # | Phase | Polarity |
|--------|---|-------|----------|
| cognitive_load | 26 | 1 | high=BAD |
| semantic_coherence | 25 | 2 | high=GOOD |

### Phase Dependency
**Earliest: Phase 5** (needs percentiles)

### Tier Behavior
- **ABSOLUTE**: SKIP — requires percentile conditions
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| Very small file (< 3 functions) | semantic_coherence = 1.0 (single concept), finder won't fire |
| File with one massive function | concept_entropy ≈ 0, coherence high → finder won't fire |

### Confidence Formula
```python
triggered = [
    ("cognitive_load", pctl_cog, 0.90, "high_is_bad"),
    ("semantic_coherence", pctl_coh, 0.20, "high_is_good"),  # inverted!
]
confidence = mean(margin(s, t, p) for s, t, p in triggered)
```

**Note**: semantic_coherence uses INVERTED margin because condition is `pctl < 0.20`:
```python
margin_coh = (0.20 - pctl_coh) / 0.20  # e.g., pctl=0.10 → margin=0.50
```

### Verification Status: ✅ VERIFIED

---

## 4. UNSTABLE_FILE (Existing)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.7 |
| Hotspot | YES |

### Store Slots Read
```
store.signal_field.per_file[path].churn_trajectory → #28
store.signal_field.per_file[path].total_changes    → #27
```

### Signal Dependencies
| Signal | # | Phase | Notes |
|--------|---|-------|-------|
| churn_trajectory | 28 | 3 | enum, not pctl |
| total_changes | 27 | 3 | hotspot filter |

### Phase Dependency
**Earliest: Phase 3** (needs temporal signals)

### Tier Behavior
- **ABSOLUTE**: FIRE — uses enum + median, no percentiles
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| ≤1 commit on file | trajectory=DORMANT → finder won't fire |
| All files same churn | median captures middle, ~50% files pass filter |

### Verification Status: ✅ VERIFIED

---

## 5. BOUNDARY_MISMATCH (Existing)

| Attribute | Value |
|-----------|-------|
| Scope | MODULE |
| Severity | 0.6 |
| Hotspot | NO |

### Store Slots Read
```
store.architecture.modules[path].boundary_alignment → #42
store.architecture.modules[path].file_count         → #50
```

### Signal Dependencies
| Signal | # | Phase | Notes |
|--------|---|-------|-------|
| boundary_alignment | 42 | 4 | |
| file_count | 50 | 4 | minimum 3 required |

### Phase Dependency
**Earliest: Phase 4** (needs architecture package)

### Tier Behavior
- **ABSOLUTE**: SKIP — needs ≥2 modules (unlikely with <15 files)
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| Flat project (1 module) | architecture=None → finder skipped |
| All files in single community | boundary_alignment=1.0 → no mismatch |

### Verification Status: ✅ VERIFIED

---

## 6. DEAD_DEPENDENCY (Existing)

| Attribute | Value |
|-----------|-------|
| Scope | FILE_PAIR |
| Severity | 0.4 |
| Hotspot | NO |

### Store Slots Read
```
store.structural.graph.adjacency[src]  → check structural edge
store.cochange.matrix[pair].count      → check co-change count
store.churn[path].total_changes        → both files need 50+ commits
```

### Phase Dependency
**Earliest: Phase 3**

### Tier Behavior
- **ABSOLUTE**: FIRE — absolute threshold (50 commits)
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| Files with <50 commits each | excluded, too little history to judge |
| External dependency edge | not in graph, N/A |

### Verification Status: ✅ VERIFIED

---

## 7. CHRONIC_PROBLEM (Meta-finder)

| Attribute | Value |
|-----------|-------|
| Scope | wraps another finding |
| Severity | 1.25× base |
| Hotspot | NO |

### Store Slots Read
```
store.finding_history[identity_key]  → persistence count, first_seen
```

### Phase Dependency
**Earliest: Phase 7** (needs finding lifecycle in persistence)

### Tier Behavior
- **ALL TIERS**: FIRE — depends on base finding's tier behavior

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| < 3 snapshots total | finder cannot fire (need 3+ persisting) |
| File renamed | identity key updated via rename tracking |

### Verification Status: ✅ VERIFIED

---

## 8. ORPHAN_CODE (New - AI Quality)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.55 |
| Hotspot | NO — structural |

### Store Slots Read
```
store.signal_field.per_file[path].is_orphan → #20
store.roles[path]                            → for entry point check
```

### Signal Dependencies
| Signal | # | Phase | Notes |
|--------|---|-------|-------|
| is_orphan | 20 | 3 | bool |
| role | 8 | 2 | used in is_orphan computation |

### Phase Dependency
**Earliest: Phase 3** (needs orphan computation)

### Tier Behavior
- **ALL TIERS**: FIRE — boolean condition, no percentiles

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| File is TEST | excluded by role check in is_orphan |
| File is ENTRY_POINT | excluded by role check |
| All files orphaned | possible for library project, use fallback entry points |

### Verification Status: ✅ VERIFIED

---

## 9. HOLLOW_CODE (New - AI Quality)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.71 |
| Hotspot | NO — structural |

### Store Slots Read
```
store.signal_field.per_file[path].stub_ratio → #6
store.signal_field.per_file[path].impl_gini  → #5
```

### Signal Dependencies
| Signal | # | Phase | Notes |
|--------|---|-------|-------|
| stub_ratio | 6 | 1 | needs FunctionDef.body_tokens |
| impl_gini | 5 | 1 | needs FunctionDef.body_tokens |

### Phase Dependency
**Earliest: Phase 1** (needs tree-sitter for accurate body tokens)

### Tier Behavior
- **ALL TIERS**: FIRE — absolute thresholds (>0.5, >0.6)

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| No functions in file | stub_ratio=0, impl_gini=0 → won't fire |
| Single function | impl_gini=0 (no variance) → won't fire even if stub |

### Verification Status: ✅ VERIFIED

---

## 10. PHANTOM_IMPORTS (New - AI Quality)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.65 |
| Hotspot | NO — structural |

### Store Slots Read
```
store.signal_field.per_file[path].phantom_import_count → #21
```

### Phase Dependency
**Earliest: Phase 3** (needs unresolved import detection)

### Tier Behavior
- **ALL TIERS**: FIRE — count > 0

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| All imports are external (pip packages) | filtered out, won't count as phantom |
| Dynamic import | not detected (static analysis only) |

### Verification Status: ✅ VERIFIED

---

## 11. COPY_PASTE_CLONE (New - AI Quality)

| Attribute | Value |
|-----------|-------|
| Scope | FILE_PAIR |
| Severity | 0.50 |
| Hotspot | NO — structural |

### Store Slots Read
```
store.clone_pairs  → List[ClonePair] with NCD score
```

### Phase Dependency
**Earliest: Phase 3** (needs NCD clone detection)

### Tier Behavior
- **ALL TIERS**: FIRE — NCD < 0.3 is absolute

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| Very small files (<100 bytes) | NCD unreliable, consider minimum size filter |
| Test files cloned | may be intentional test fixture duplication |

### Verification Status: ✅ VERIFIED

---

## 12. FLAT_ARCHITECTURE (New - AI Quality)

| Attribute | Value |
|-----------|-------|
| Scope | CODEBASE |
| Severity | 0.60 |
| Hotspot | NO — structural |

### Store Slots Read
```
store.signal_field.global_signals.max_depth    → derived from #19
store.signal_field.global_signals.glue_deficit → #59
```

### Phase Dependency
**Earliest: Phase 3** (needs depth computation)

### Tier Behavior
- **ALL TIERS**: FIRE — absolute thresholds

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| Single file | depth=0, glue_deficit=1.0 → finder fires (correct: no architecture) |
| All entry points | depth=0 for all → finder fires |

### Verification Status: ✅ VERIFIED

---

## 13. NAMING_DRIFT (New - AI Quality)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.45 |
| Hotspot | NO — structural |

### Store Slots Read
```
store.signal_field.per_file[path].naming_drift → #11
```

### Phase Dependency
**Earliest: Phase 2** (needs semantics/)

### Tier Behavior
- **ALL TIERS**: FIRE — absolute threshold >0.7

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| Generic filename (utils.py) | naming_drift = 0.0 → won't fire |
| Very short file (<20 tokens) | naming_drift based on limited data |

### Verification Status: ✅ VERIFIED

---

## 14. KNOWLEDGE_SILO (New - Social)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.70 |
| Hotspot | YES |

### Store Slots Read
```
store.signal_field.per_file[path].bus_factor → #31
store.signal_field.per_file[path].pagerank   → #14
store.signal_field.per_file[path].percentiles.pagerank
```

### Phase Dependency
**Earliest: Phase 5** (needs percentiles)

### Tier Behavior
- **ABSOLUTE**: SKIP — requires pctl(pagerank)
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| Single author project | bus_factor=1 for all → many findings, may want to suppress |
| File with 2 commits total | bus_factor unreliable, but threshold ≤1.5 may catch |

### Verification Status: ✅ VERIFIED

---

## 15. CONWAY_VIOLATION (New - Social)

| Attribute | Value |
|-----------|-------|
| Scope | MODULE_PAIR |
| Severity | 0.55 |
| Hotspot | NO |

### Store Slots Read
```
store.author_distances[pair]           → G5 author distance
store.architecture.module_graph[pair]  → structural coupling
```

### Phase Dependency
**Earliest: Phase 4** (needs architecture + G5 from Phase 3)

### Tier Behavior
- **ABSOLUTE**: SKIP — needs ≥3 authors, ≥2 modules
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| Single author | author_distances empty → finder skipped |
| < 3 distinct authors | G5 computation skipped, finder skipped |

### Verification Status: ✅ VERIFIED

---

## 16. REVIEW_BLINDSPOT (New - Social)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.80 |
| Hotspot | YES |

### Store Slots Read
```
store.signal_field.per_file[path].pagerank
store.signal_field.per_file[path].bus_factor
store.roles[path]  → to find test file
```

### Phase Dependency
**Earliest: Phase 5**

### Tier Behavior
- **ABSOLUTE**: SKIP — requires pctl(pagerank)
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| All files have tests | no_test_file=false for all → finder won't fire |
| Test detection fails | false positives (flags files that have tests elsewhere) |

### Verification Status: ✅ VERIFIED

---

## 17. LAYER_VIOLATION (New - Architecture)

| Attribute | Value |
|-----------|-------|
| Scope | MODULE_PAIR |
| Severity | 0.52 |
| Hotspot | NO |

### Store Slots Read
```
store.architecture.layers              → layer assignments
store.architecture.violations          → List[Violation]
```

### Phase Dependency
**Earliest: Phase 4**

### Tier Behavior
- **ABSOLUTE**: SKIP — needs ≥2 modules
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| All modules in one SCC (cycle) | layers collapsed, violation_count=0 |
| Flat project | no layers → finder skipped |

### Verification Status: ✅ VERIFIED

---

## 18. ZONE_OF_PAIN (New - Architecture)

| Attribute | Value |
|-----------|-------|
| Scope | MODULE |
| Severity | 0.60 |
| Hotspot | NO |

### Store Slots Read
```
store.architecture.modules[path].abstractness  → #40
store.architecture.modules[path].instability   → #39
```

### Phase Dependency
**Earliest: Phase 4**

### Tier Behavior
- **ABSOLUTE**: SKIP — needs module metrics
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| instability=None (isolated) | **MUST CHECK**: finder skips this module |
| All modules are utilities | A≈0, I≈1 → not in zone of pain |

### Verification Status: ✅ VERIFIED (instability guard added)

---

## 19. ARCHITECTURE_EROSION (New - Architecture)

| Attribute | Value |
|-----------|-------|
| Scope | CODEBASE |
| Severity | 0.65 |
| Hotspot | NO |

### Store Slots Read
```
store.finding_history[violation_rate]  → time series
```

### Phase Dependency
**Earliest: Phase 7** (needs 3+ snapshots with architecture)

### Tier Behavior
- **ABSOLUTE**: SKIP — needs architecture
- **BAYESIAN/FULL**: FIRE if 3+ snapshots

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| < 3 snapshots | finder cannot fire |
| Violation rate flat | no erosion, finder won't fire |

### Verification Status: ✅ VERIFIED

---

## 20. WEAK_LINK (New - Cross-Dimensional)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.75 |
| Hotspot | YES |

### Store Slots Read
```
store.signal_field.per_file[path].delta_h      → health Laplacian Δh
store.structural.graph.adjacency               → neighbors
```

### Phase Dependency
**Earliest: Phase 5** (needs health Laplacian computation)

### Tier Behavior
- **ABSOLUTE**: SKIP — needs raw_risk computation
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| Orphan file (no neighbors) | Δh = 0.0 → finder won't fire (handled by ORPHAN_CODE) |
| All neighbors also high risk | Δh ≈ 0 → finder won't fire (correct: no contrast) |

### Verification Status: ✅ VERIFIED (orphan edge case documented)

---

## 21. BUG_ATTRACTOR (New - Cross-Dimensional)

| Attribute | Value |
|-----------|-------|
| Scope | FILE |
| Severity | 0.70 |
| Hotspot | YES |

### Store Slots Read
```
store.signal_field.per_file[path].fix_ratio  → #33
store.signal_field.per_file[path].pagerank   → #14
store.signal_field.per_file[path].percentiles
```

### Phase Dependency
**Earliest: Phase 5**

### Tier Behavior
- **ABSOLUTE**: SKIP — requires pctl(pagerank)
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| No commits match fix pattern | fix_ratio=0 → finder won't fire |
| All commits are fixes | fix_ratio=1.0 → finder fires if central |

### Verification Status: ✅ VERIFIED

---

## 22. ACCIDENTAL_COUPLING (New - Cross-Dimensional)

| Attribute | Value |
|-----------|-------|
| Scope | FILE_PAIR |
| Severity | 0.50 |
| Hotspot | NO |

### Store Slots Read
```
store.structural.graph.adjacency[src]          → structural edge
store.semantics[path_a].concepts               → concept set A
store.semantics[path_b].concepts               → concept set B
```

### Phase Dependency
**Earliest: Phase 2** (needs semantics/ concepts)

### Tier Behavior
- **ABSOLUTE**: SKIP — needs concept clusters
- **BAYESIAN/FULL**: FIRE

### Edge Cases
| Condition | Behavior |
|-----------|----------|
| File has no concepts (< 20 tokens) | concept set = {ROLE}, likely overlap |
| Both files are CONFIG | concepts overlap via role → won't fire |

### Verification Status: ✅ VERIFIED

---

## Summary: Finder Dependencies

| Finder | Phase | ABSOLUTE | BAYESIAN | FULL | Store Slots |
|--------|-------|----------|----------|------|-------------|
| HIGH_RISK_HUB | 5 | skip | fire | fire | signal_field |
| HIDDEN_COUPLING | 3 | fire | fire | fire | cochange, structural |
| GOD_FILE | 5 | skip | fire | fire | signal_field |
| UNSTABLE_FILE | 3 | fire | fire | fire | signal_field |
| BOUNDARY_MISMATCH | 4 | skip | fire | fire | architecture |
| DEAD_DEPENDENCY | 3 | fire | fire | fire | structural, cochange, churn |
| CHRONIC_PROBLEM | 7 | fire | fire | fire | finding_history |
| ORPHAN_CODE | 3 | fire | fire | fire | signal_field, roles |
| HOLLOW_CODE | 1 | fire | fire | fire | signal_field |
| PHANTOM_IMPORTS | 3 | fire | fire | fire | signal_field |
| COPY_PASTE_CLONE | 3 | fire | fire | fire | clone_pairs |
| FLAT_ARCHITECTURE | 3 | fire | fire | fire | signal_field.global |
| NAMING_DRIFT | 2 | fire | fire | fire | signal_field |
| KNOWLEDGE_SILO | 5 | skip | fire | fire | signal_field |
| CONWAY_VIOLATION | 4 | skip | fire | fire | author_distances, architecture |
| REVIEW_BLINDSPOT | 5 | skip | fire | fire | signal_field, roles |
| LAYER_VIOLATION | 4 | skip | fire | fire | architecture |
| ZONE_OF_PAIN | 4 | skip | fire | fire | architecture |
| ARCHITECTURE_EROSION | 7 | skip | fire | fire | finding_history |
| WEAK_LINK | 5 | skip | fire | fire | signal_field, structural |
| BUG_ATTRACTOR | 5 | skip | fire | fire | signal_field |
| ACCIDENTAL_COUPLING | 2 | skip | fire | fire | structural, semantics |

---

## Rehearsal Status: ALL 22 FINDERS VERIFIED ✅
