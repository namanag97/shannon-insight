# Registry: Finding Catalog

Every finding type in Shannon Insight. Each finder declares which signals it requires (from `signals.md`), its condition, severity, evidence template, and suggestion template.

**Rules**:
- A finder only runs if ALL its required signals are available in the AnalysisStore.
- If a signal is missing (e.g., no git = no bus_factor), the finder is gracefully skipped.
- This enables demand-driven evaluation: trace from active finders → required signals → compute only those.

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
| **Condition** | `abstractness < 0.3 AND instability < 0.3` |
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
| **Requires** | `risk_score`, graph edges (for health Laplacian) |
| **Condition** | `Δh(f) > 0.4` (health Laplacian: file much worse than all neighbors) |
| **Evidence** | [IR5s] Δh value, neighbor health values, risk_score |
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
| **Requires** | structural edges, `naming_drift` or semantic distance (G6) |
| **Condition** | `d_dependency CLOSE (edge exists) AND d_semantic FAR (cosine < 0.3)` |
| **Evidence** | [G1] structural edge, [G6] semantic distance, concept lists |
| **Suggestion** | "Connected but unrelated concepts. Consider removing or abstracting the dependency." |
| **Effort** | MEDIUM |
| **Phase** | 6 |

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
