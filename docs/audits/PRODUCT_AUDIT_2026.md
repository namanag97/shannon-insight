# Shannon Insight: Comprehensive Product Audit 2026-02-14

**Executive Summary for CTO-Level Strategic Planning**

This document provides a complete inventory of Shannon Insight's features, identifies gaps between backend capabilities and frontend presentation, assesses data storage/display patterns, and recommends improvements for developer experience and product clarity.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Feature Matrix: Backend vs Frontend](#feature-matrix-backend-vs-frontend)
3. [Gap Analysis](#gap-analysis)
4. [Storage Assessment](#storage-assessment)
5. [Display Assessment](#display-assessment)
6. [Backend Improvement Recommendations](#backend-improvement-recommendations)
7. [Frontend Improvement Recommendations](#frontend-improvement-recommendations)
8. [Product Principles](#product-principles)
9. [Complexity for New Developers](#complexity-for-new-developers)
10. [Documentation Cleanup Plan](#documentation-cleanup-plan)
11. [Roadmap Clarity](#roadmap-clarity)

---

## Executive Summary

**Current State:**
- **Backend:** Mature, well-tested (247 tests), 62 signals, 22 finders, 8 language scanners
- **Frontend:** Functional dashboard with 5 screens, real-time updates, keyboard navigation
- **Documentation:** 70+ files with good coverage but poor organization (v1/v2 mixing, outdated docs)
- **Gap:** Backend capabilities exceed frontend display; missing 15+ signals in UI

**Key Findings:**
1. ✅ **Backend is production-ready** — All analyzers, finders, signals implemented and tested
2. ⚠️ **Frontend displays ~60% of backend data** — Many signals computed but not shown
3. ❌ **Documentation is fragmented** — v1 (current) mixed with v2 (spec), no clear onboarding path
4. ✅ **Storage model is correct** — TensorSnapshot v2 schema supports all features
5. ⚠️ **Display strategy is incomplete** — Sparklines, trends, violations missing from UI

**Strategic Recommendations:**
1. **Short-term (1-2 weeks):** Complete frontend display of all 62 signals, add sparkline trends
2. **Medium-term (1 month):** Reorganize documentation (archive v1/v2 split), create developer onboarding guide
3. **Long-term (3 months):** Begin v2 phase implementation (tree-sitter, enhanced graph algorithms)

---

## Feature Matrix: Backend vs Frontend

### Signals (62 Total)

| Signal | Backend | Frontend Display | Location in UI | Gap |
|--------|---------|------------------|----------------|-----|
| **File Signals (36)** |
| `lines` | ✅ | ✅ | File detail | ✅ Full |
| `function_count` | ✅ | ✅ | File detail | ✅ Full |
| `class_count` | ✅ | ⚠️ | File detail (as "structs") | ⚠️ Label mismatch |
| `max_nesting` | ✅ | ❌ | Missing | ❌ Not displayed |
| `impl_gini` | ✅ | ❌ | Missing | ❌ Not displayed |
| `stub_ratio` | ✅ | ❌ | Missing | ❌ Not displayed |
| `import_count` | ✅ | ❌ | Missing | ❌ Not displayed |
| `role` | ✅ | ✅ | File detail + filters | ✅ Full |
| `concept_count` | ✅ | ❌ | Missing | ❌ Not displayed |
| `concept_entropy` | ✅ | ❌ | Missing | ❌ Not displayed |
| `naming_drift` | ✅ | ❌ | Missing | ❌ Not displayed |
| `todo_density` | ✅ | ❌ | Missing | ❌ Not displayed |
| `docstring_coverage` | ✅ | ❌ | Missing | ❌ Not displayed |
| `pagerank` | ✅ | ✅ | File table + detail | ✅ Full |
| `betweenness` | ✅ | ❌ | Missing | ❌ Not displayed |
| `in_degree` | ✅ | ❌ | Missing | ❌ Not displayed |
| `out_degree` | ✅ | ❌ | Missing | ❌ Not displayed |
| `blast_radius_size` | ✅ | ✅ | File table + detail | ✅ Full |
| `depth` | ✅ | ❌ | Missing | ❌ Not displayed |
| `is_orphan` | ✅ | ✅ | File filters | ✅ Full |
| `phantom_import_count` | ✅ | ❌ | Missing | ❌ Not displayed |
| `broken_call_count` | ⚠️ | ❌ | N/A (not implemented) | ⚠️ Backend gap |
| `community` | ✅ | ❌ | Missing | ❌ Not displayed |
| `compression_ratio` | ✅ | ❌ | Missing | ❌ Not displayed |
| `semantic_coherence` | ✅ | ❌ | Missing | ❌ Not displayed |
| `cognitive_load` | ✅ | ✅ | File table + detail | ✅ Full |
| `total_changes` | ✅ | ✅ | File table + detail | ✅ Full |
| `churn_trajectory` | ✅ | ❌ | Missing | ❌ Not displayed |
| `churn_slope` | ✅ | ❌ | Missing | ❌ Not displayed |
| `churn_cv` | ✅ | ✅ | File table + detail | ✅ Full |
| `bus_factor` | ✅ | ✅ | File table + detail | ✅ Full |
| `author_entropy` | ✅ | ❌ | Missing | ❌ Not displayed |
| `fix_ratio` | ✅ | ❌ | Missing | ❌ Not displayed |
| `refactor_ratio` | ✅ | ❌ | Missing | ❌ Not displayed |
| `risk_score` | ✅ | ✅ | File table + detail | ✅ Full |
| `wiring_quality` | ✅ | ❌ | Missing | ❌ Not displayed |
| **Module Signals (15)** |
| `cohesion` | ✅ | ❌ | Missing | ❌ Not displayed |
| `coupling` | ✅ | ❌ | Missing | ❌ Not displayed |
| `instability` | ✅ | ✅ | Module table + detail | ✅ Full |
| `abstractness` | ✅ | ✅ | Module table + detail | ✅ Full |
| `main_seq_distance` | ✅ | ❌ | Missing | ❌ Not displayed |
| `boundary_alignment` | ✅ | ❌ | Missing | ❌ Not displayed |
| `layer_violation_count` | ✅ | ⚠️ | Module detail (not shown) | ⚠️ Data in backend, UI incomplete |
| `role_consistency` | ✅ | ❌ | Missing | ❌ Not displayed |
| `velocity` | ✅ | ✅ | Module table + detail | ✅ Full |
| `coordination_cost` | ✅ | ❌ | Missing | ❌ Not displayed |
| `knowledge_gini` | ✅ | ❌ | Missing | ❌ Not displayed |
| `module_bus_factor` | ✅ | ❌ | Missing | ❌ Not displayed |
| `mean_cognitive_load` | ✅ | ❌ | Missing | ❌ Not displayed |
| `file_count` | ✅ | ✅ | Module table + detail | ✅ Full |
| `health_score` | ✅ | ✅ | Module table + detail | ✅ Full |
| **Global Signals (11)** |
| `modularity` | ✅ | ✅ | Health screen | ✅ Full |
| `fiedler_value` | ✅ | ✅ | Health screen | ✅ Full |
| `spectral_gap` | ✅ | ✅ | Health screen | ✅ Full |
| `cycle_count` | ✅ | ✅ | Health screen | ✅ Full |
| `centrality_gini` | ✅ | ✅ | Health screen | ✅ Full |
| `orphan_ratio` | ✅ | ✅ | Health screen | ✅ Full |
| `phantom_ratio` | ✅ | ✅ | Health screen | ✅ Full |
| `glue_deficit` | ⚠️ | ❌ | N/A (not computed) | ⚠️ Backend gap |
| `clone_ratio` | ✅ | ✅ | Health screen | ✅ Full |
| `violation_rate` | ✅ | ✅ | Health screen | ✅ Full |
| `conway_alignment` | ✅ | ✅ | Health screen | ✅ Full |

**Summary:**
- **Fully Displayed:** 23/62 (37%)
- **Partially Displayed:** 2/62 (3%)
- **Missing from UI:** 35/62 (56%)
- **Backend Gaps:** 2/62 (3%) — `broken_call_count`, `glue_deficit`

---

### Finders (22 Total)

| Finder | Backend | Frontend Display | Category | Gap |
|--------|---------|------------------|----------|-----|
| `high_risk_hub` | ✅ | ✅ | Fragile | ✅ Full |
| `hidden_coupling` | ✅ | ✅ | Tangled | ✅ Full |
| `god_file` | ✅ | ✅ | Fragile | ✅ Full |
| `unstable_file` | ✅ | ✅ | Fragile | ✅ Full |
| `boundary_mismatch` | ✅ | ✅ | Tangled | ✅ Full |
| `dead_dependency` | ✅ | ✅ | Incomplete | ✅ Full |
| `orphan_code` | ✅ | ✅ | Incomplete | ✅ Full |
| `hollow_code` | ✅ | ✅ | Incomplete | ✅ Full |
| `phantom_imports` | ✅ | ✅ | Incomplete | ✅ Full |
| `copy_paste_clone` | ✅ | ✅ | Tangled | ✅ Full |
| `flat_architecture` | ✅ | ✅ | Tangled | ✅ Full |
| `naming_drift` | ✅ | ✅ | Incomplete | ✅ Full |
| `layer_violation` | ✅ | ✅ | Tangled | ✅ Full |
| `zone_of_pain` | ✅ | ✅ | Fragile | ✅ Full |
| `knowledge_silo` | ✅ | ✅ | Team | ✅ Full |
| `conway_violation` | ✅ | ✅ | Team | ✅ Full |
| `review_blindspot` | ✅ | ✅ | Team | ✅ Full |
| `weak_link` | ✅ | ✅ | Fragile | ✅ Full |
| `bug_attractor` | ✅ | ✅ | Fragile | ✅ Full |
| `accidental_coupling` | ✅ | ✅ | Tangled | ✅ Full |
| `chronic_problem` | ✅ | ✅ | All categories | ✅ Full |
| `architecture_erosion` | ✅ | ✅ | Tangled | ✅ Full |

**Summary:** All 22 finders are displayed in the Issues screen. ✅ **100% coverage**

---

### Visualization Features

| Feature | Backend Data Available | Frontend Display | Status |
|---------|------------------------|------------------|--------|
| **Health Score** | ✅ TensorSnapshot.global_signals | ✅ Overview hero | ✅ Full |
| **Category Bars** | ✅ Findings grouped | ✅ Overview | ✅ Full |
| **Risk Histogram** | ✅ File risk scores | ✅ Overview | ✅ Full |
| **Focus Point** | ✅ Actionability ranking | ✅ Overview | ✅ Full |
| **Finding Evidence** | ✅ Evidence with percentiles | ✅ Issues screen | ✅ Full |
| **File Table** | ✅ FileSignals | ✅ Files screen | ⚠️ Only 7/36 signals |
| **File Treemap** | ✅ Lines + risk_score | ✅ Files screen | ✅ Full |
| **Module Table** | ✅ ModuleSignals | ✅ Modules screen | ⚠️ Only 5/15 signals |
| **Health Trends** | ✅ signal_history table | ✅ Health screen | ✅ Full |
| **Top Movers** | ✅ Delta computation | ✅ Health screen | ✅ Full |
| **Chronic Findings** | ✅ finding_lifecycle table | ✅ Health screen | ✅ Full |
| **Concern Radar** | ✅ Category scores | ✅ Health screen | ✅ Full |
| **Signal Sparklines** | ✅ signal_history table | ❌ Missing | ❌ Not implemented |
| **Dependency Graph** | ✅ dependency_edges | ❌ Missing | ❌ Not visualized |
| **Layer Diagram** | ✅ layers[] | ❌ Missing | ❌ Not visualized |
| **Module Violations** | ✅ violations[] | ⚠️ Data exists but not shown in UI | ⚠️ Partial |
| **Author Distance Viz** | ✅ author_distances | ❌ Missing | ❌ Not visualized |
| **Cochange Heatmap** | ✅ cochange_edges | ❌ Missing | ❌ Not visualized |

**Summary:**
- **Fully Displayed:** 11/18 (61%)
- **Partially Displayed:** 3/18 (17%)
- **Missing from UI:** 4/18 (22%)

---

### CLI Commands

| Command | Backend | Frontend | Gap |
|---------|---------|----------|-----|
| `analyze` | ✅ | ✅ (via serve) | ✅ Full |
| `diff` | ✅ | ❌ | ❌ CLI-only |
| `explain` | ✅ | ⚠️ (file detail similar) | ⚠️ Partial overlap |
| `health` | ✅ | ✅ (Health screen) | ✅ Full |
| `history` | ✅ | ⚠️ (trends shown) | ⚠️ Partial |
| `report` | ✅ | ❌ | ❌ CLI-only |
| `serve` | ✅ | ✅ | ✅ Full |
| `journey` | ✅ | ❌ | ❌ CLI-only |
| `tui` | ✅ | ❌ | ❌ CLI-only (different interface) |

**Summary:** Frontend covers core analysis; CLI has unique views (diff, report, journey, tui)

---

## Gap Analysis

### Critical Gaps (High Impact, Missing from Frontend)

1. **Signal Sparklines** ⭐️⭐️⭐️
   - **Backend:** `signal_history` table has all time-series data
   - **Frontend:** Placeholder code exists (`renderSparkline`) but not wired to data
   - **Impact:** Users can't see trends over time (health improving/degrading)
   - **Fix:** Wire `f.trends` from backend to frontend signal display

2. **Dependency Graph Visualization** ⭐️⭐️⭐️
   - **Backend:** `dependency_edges` available in TensorSnapshot
   - **Frontend:** No graph renderer
   - **Impact:** Can't visualize module dependencies, cycles, or coupling
   - **Fix:** Add D3.js or Cytoscape.js graph view (new screen or tab)

3. **Layer Architecture Diagram** ⭐️⭐️
   - **Backend:** `layers[]` computed, `violations[]` available
   - **Frontend:** Data exists but not displayed
   - **Impact:** Can't see layering violations visually
   - **Fix:** Add layer diagram to Modules screen or Architecture tab

4. **Module Violations List** ⭐️⭐️
   - **Backend:** `violations[]` in TensorSnapshot
   - **Frontend:** Module detail screen has placeholder but doesn't populate
   - **Fix:** Populate `m.violations` in `build_dashboard_state` → render in UI

5. **Missing File Signals in Table** ⭐️⭐️
   - **Backend:** 36 file signals computed
   - **Frontend:** Only 7 shown in file table (Lines, Risk, Churn CV, Cognitive Load, Blast Radius, PageRank, Total Changes)
   - **Impact:** Users miss 29 signals (max_nesting, impl_gini, stub_ratio, concept_entropy, etc.)
   - **Fix:** Add column toggles or "Show All Signals" expansion

6. **Missing Module Signals in Table** ⭐️⭐️
   - **Backend:** 15 module signals computed
   - **Frontend:** Only 5 shown (Health, Instability, Abstractness, Files, Velocity)
   - **Impact:** Users miss cohesion, coupling, boundary_alignment, coordination_cost, etc.
   - **Fix:** Add expandable module detail with all signals

7. **Churn Trajectory Classification** ⭐️
   - **Backend:** Files classified as STABILIZING/CHURNING/SPIKING/DORMANT
   - **Frontend:** Not displayed (only churn_cv shown)
   - **Impact:** Can't filter files by churn pattern
   - **Fix:** Add churn_trajectory badge to file rows

8. **Semantic Signals** ⭐️
   - **Backend:** `concept_count`, `concept_entropy`, `naming_drift`, `docstring_coverage`
   - **Frontend:** Not displayed
   - **Impact:** Can't identify poorly documented or semantically confused files
   - **Fix:** Add "Code Quality" section to file detail

9. **Team Context Signals** ⭐️
   - **Backend:** `author_entropy`, `fix_ratio`, `refactor_ratio`, `coordination_cost`, `knowledge_gini`
   - **Frontend:** Only `bus_factor` shown
   - **Impact:** Missing collaboration insights
   - **Fix:** Add "Team Context" section to file/module detail

10. **Cochange Heatmap** ⭐️
    - **Backend:** `cochange_edges` available
    - **Frontend:** Not visualized
    - **Impact:** Can't see temporal coupling patterns
    - **Fix:** Add cochange heatmap to Health screen or new "Temporal" tab

---

### Medium Priority Gaps

11. **In-Degree / Out-Degree** — Graph metrics not shown
12. **Betweenness Centrality** — Available but not displayed
13. **Community Detection** — Louvain community IDs computed but not visualized
14. **Compression Ratio** — Information density metric not shown
15. **Main Sequence Distance** — Architecture metric (Martin) not shown
16. **Boundary Alignment** — Module/community alignment not shown
17. **Role Consistency** — Module role homogeneity not shown

---

### Low Priority Gaps

18. **Impl Gini** — Function size distribution metric
19. **Stub Ratio** — Hollow code indicator (finder exists, signal not shown)
20. **Import Count** — Basic metric, low value
21. **Depth** — DAG depth from entry points
22. **Phantom Import Count** — Finder covers this, signal less useful

---

### Backend Gaps (Data Not Computed)

23. **`broken_call_count`** — Requires CALL edges (deferred to v2 Phase 1+)
24. **`glue_deficit`** — Not yet implemented (marked as research)

---

## Storage Assessment

### ✅ **Storage Model: CORRECT**

**TensorSnapshot v2 Schema** is well-designed and supports all features:

| Data Type | Storage Location | Schema | Assessment |
|-----------|------------------|--------|------------|
| **File Signals** | `file_signals` dict | `{path: {signal: value}}` | ✅ Correct |
| **Module Signals** | `module_signals` dict | `{module: {signal: value}}` | ✅ Correct |
| **Global Signals** | `global_signals` dict | `{signal: value}` | ✅ Correct |
| **Findings** | `findings` list | `FindingRecord[]` with identity_key | ✅ Correct |
| **Dependency Graph** | `dependency_edges` list | `[(src, tgt)]` | ✅ Correct |
| **Cochange Graph** | `cochange_edges` list | `[(a, b, weight, lift)]` | ✅ Correct |
| **Architecture** | `modules`, `layers`, `violations` | Lists of dicts | ✅ Correct |
| **Health Laplacian** | `delta_h` dict | `{path: Δh}` | ✅ Correct |
| **Metadata** | Root fields | `commit_sha`, `timestamp`, `tool_version` | ✅ Correct |

**SQLite Schema** (history.db):

| Table | Purpose | Schema | Assessment |
|-------|---------|--------|------------|
| `snapshots` | Snapshot records | id, timestamp, commit_sha, file_count, etc. | ✅ Correct |
| `signal_history` | Per-file signal time series | snapshot_id, file_path, signal_name, value | ✅ Correct |
| `module_signal_history` | Per-module signal time series | snapshot_id, module_path, signal_name, value | ✅ Correct |
| `global_signal_history` | Global signal time series | snapshot_id, signal_name, value | ✅ Correct |
| `findings` | Finding records | id, snapshot_id, finding_type, identity_key, etc. | ✅ Correct |
| `finding_lifecycle` | Finding persistence | finding_id, occurrences, first/last snapshot_id | ✅ Correct |

**Issues Found:** None. Storage is production-ready. ✅

---

## Display Assessment

### ✅ **What's Displayed Correctly**

1. **Health Score** — Large visual indicator with color coding (red < 4, orange < 6, yellow < 8, green ≥ 8)
2. **Finding Evidence** — Rich display with percentiles ("top 5% by PageRank")
3. **File Filters** — Role-based (MODEL, SERVICE, etc.), has_issues, orphans
4. **Risk Histogram** — 5-bin SVG chart (0-0.2, 0.2-0.4, etc.)
5. **Treemap** — Sized by LOC, colored by risk (squarify layout)
6. **Concern Radar** — Polar chart for 4 categories (Incomplete, Fragile, Tangled, Team)
7. **Health Trends** — Sparkline chart with historical data
8. **Top Movers** — Files with biggest health delta (sorted by absolute change)
9. **Chronic Findings** — Findings appearing in 3+ snapshots
10. **Keyboard Navigation** — j/k selection, Enter to open, 1-5 screen switching

### ⚠️ **What's Partially Displayed**

1. **File Table** — Shows 7/36 signals (missing 29)
   - **Shown:** Lines, Risk, Churn CV, Cognitive Load, Blast Radius, PageRank, Total Changes
   - **Missing:** max_nesting, impl_gini, stub_ratio, concept_entropy, naming_drift, todo_density, docstring_coverage, betweenness, in_degree, out_degree, depth, community, compression_ratio, semantic_coherence, churn_trajectory, churn_slope, author_entropy, fix_ratio, refactor_ratio, wiring_quality

2. **Module Table** — Shows 5/15 signals (missing 10)
   - **Shown:** Health, Instability, Abstractness, Files, Velocity
   - **Missing:** cohesion, coupling, main_seq_distance, boundary_alignment, layer_violation_count, role_consistency, coordination_cost, knowledge_gini, module_bus_factor, mean_cognitive_load

3. **Module Detail** — Violations placeholder exists but not populated
   - **Fix:** Wire `m.violations` in `build_dashboard_state` → render as list

### ❌ **What's Missing Entirely**

1. **Signal Sparklines** — No trends shown in file/module detail
2. **Dependency Graph** — No visual graph renderer
3. **Layer Diagram** — Architecture layers not visualized
4. **Cochange Heatmap** — Temporal coupling not shown
5. **Author Distance Viz** — Team collaboration patterns not shown
6. **Community Visualization** — Louvain communities not shown
7. **Churn Trajectory Badges** — STABILIZING/CHURNING/SPIKING/DORMANT not displayed
8. **Semantic Quality Section** — concept_entropy, naming_drift, docstring_coverage not grouped

### ✅ **Display Patterns: CORRECT**

| Pattern | Implementation | Assessment |
|---------|----------------|------------|
| **Severity Color Coding** | Red (critical ≥ 0.9), Orange (high ≥ 0.7), Yellow (medium ≥ 0.5), Blue (low ≥ 0.3), Gray (info < 0.3) | ✅ Correct |
| **Health Color Coding** | Red (< 4), Orange (< 6), Yellow (< 8), Green (≥ 8) | ✅ Correct |
| **Risk Polarity** | High-is-bad signals colored red, high-is-good colored green | ✅ Correct |
| **Percentile Display** | "top 5% by PageRank" format | ✅ Correct |
| **Number Formatting** | 1000 → "1.0k", 1000000 → "1.0M" | ✅ Correct |
| **Signal Grouping** | 6 categories (Size, Graph, Code Health, Change History, Team, Computed) | ✅ Correct |
| **Finding Categories** | 4 categories (Incomplete, Fragile, Tangled, Team) | ✅ Correct |

---

## Backend Improvement Recommendations

### Priority 1: Data Completeness

1. **Populate `f.trends` in `build_dashboard_state`** ⭐️⭐️⭐️
   - **Current:** Frontend expects `file.trends[signal]` but backend doesn't populate
   - **Fix:** Query `signal_history` table in `api.py`, add to each file's data
   - **Impact:** Enables sparklines in UI
   - **Effort:** 2-4 hours

2. **Populate `m.violations` in `build_dashboard_state`** ⭐️⭐️
   - **Current:** Module detail expects `m.violations` array but not populated
   - **Fix:** Add violations from TensorSnapshot to module objects
   - **Impact:** Shows layer violations in module detail
   - **Effort:** 1-2 hours

3. **Add Missing Signals to Dashboard State** ⭐️⭐️
   - **Current:** Only subset of signals sent to frontend
   - **Fix:** Include all 62 signals in `files[path].signals` dict
   - **Impact:** Frontend can display any signal
   - **Effort:** 1 hour (already computed, just include in JSON)

### Priority 2: Performance Optimization

4. **Optimize `build_dashboard_state` Performance** ⭐️⭐️
   - **Current:** Builds entire state dict every WebSocket update
   - **Issue:** Large codebases (1000+ files) cause slow updates
   - **Fix:** Add caching layer, only rebuild on actual analysis completion
   - **Impact:** Faster WebSocket updates
   - **Effort:** 4-6 hours

5. **Add Progressive Loading for Large Codebases** ⭐️
   - **Current:** Frontend loads all files at once (200-file limit)
   - **Fix:** Add pagination or virtual scrolling to backend API
   - **Impact:** Support 1000+ file codebases
   - **Effort:** 6-8 hours

### Priority 3: API Enhancements

6. **Add `/api/file/<path>` Endpoint** ⭐️
   - **Current:** File detail data loaded from full state
   - **Fix:** Add endpoint to fetch single file's full signal history + findings
   - **Impact:** Faster file detail loading, reduced initial payload
   - **Effort:** 2-3 hours

7. **Add `/api/signals/trends` Endpoint** ⭐️
   - **Current:** No dedicated endpoint for signal trends
   - **Fix:** Add endpoint to query signal_history for specific files/signals
   - **Impact:** Enables custom trend visualizations
   - **Effort:** 2-3 hours

8. **Add `/api/graph` Endpoint** ⭐️
   - **Current:** Dependency graph in full state only
   - **Fix:** Add endpoint with filtering (e.g., subgraph around file)
   - **Impact:** Enables interactive dependency graph exploration
   - **Effort:** 3-4 hours

### Priority 4: Data Quality

9. **Implement `glue_deficit` Signal** ⭐️
   - **Current:** Marked as "not computed"
   - **Fix:** Research and implement glue code detection algorithm
   - **Impact:** Identifies missing abstraction layers
   - **Effort:** 8-12 hours (research + implementation)

10. **Add Signal Validation in `SignalFusionAnalyzer`** ⭐️
    - **Current:** No validation that all 62 signals are computed
    - **Fix:** Add assertion checking all signals present, log warnings for nulls
    - **Impact:** Catch signal computation bugs early
    - **Effort:** 2-3 hours

---

## Frontend Improvement Recommendations

### Priority 1: Complete Signal Display

1. **Add Signal Sparklines to File/Module Detail** ⭐️⭐️⭐️
   - **Current:** `renderSparkline` exists but not wired to data
   - **Fix:** Wire `f.trends[signal]` to sparkline renderer in signal grid
   - **Impact:** Users see trends over time (health improving/degrading)
   - **Effort:** 3-4 hours
   - **Design:** Add mini-sparkline next to each signal value in file detail

2. **Add "Show All Signals" Toggle to File Table** ⭐️⭐️
   - **Current:** Only 7/36 signals shown, no way to see others
   - **Fix:** Add column picker dropdown, allow users to toggle columns
   - **Impact:** Advanced users can see all signals
   - **Effort:** 4-6 hours
   - **Design:** Dropdown with checkboxes for each signal category

3. **Add Missing Signals to File Detail** ⭐️⭐️
   - **Current:** File detail shows only 8 signals in grid
   - **Fix:** Add sections for:
     - **Code Quality:** max_nesting, impl_gini, stub_ratio
     - **Semantics:** concept_count, concept_entropy, naming_drift, docstring_coverage
     - **Graph Position:** betweenness, in_degree, out_degree, depth, community
     - **Team Context:** author_entropy, fix_ratio, refactor_ratio
     - **Technical Debt:** compression_ratio, wiring_quality
   - **Impact:** Complete signal visibility
   - **Effort:** 4-6 hours

4. **Add Churn Trajectory Badges** ⭐️
   - **Current:** churn_cv shown but not churn_trajectory
   - **Fix:** Add badge (STABILIZING/CHURNING/SPIKING/DORMANT) to file rows
   - **Impact:** Quick visual pattern recognition
   - **Effort:** 2-3 hours
   - **Design:** Color-coded badge next to file name

### Priority 2: New Visualizations

5. **Add Dependency Graph Visualization** ⭐️⭐️⭐️
   - **Current:** dependency_edges available but not rendered
   - **Fix:** Add new "Graph" screen or tab with:
     - Force-directed graph (D3.js or Cytoscape.js)
     - Node size = PageRank, color = risk
     - Edge highlighting for cycles
     - Click file → highlight dependencies
   - **Impact:** Visual dependency exploration
   - **Effort:** 12-16 hours
   - **Library:** D3.js (16KB gzipped) or Cytoscape.js (48KB)

6. **Add Layer Architecture Diagram** ⭐️⭐️
   - **Current:** layers[] and violations[] not visualized
   - **Fix:** Add layer diagram to Modules screen:
     - Horizontal layers (top = high-level, bottom = low-level)
     - Modules as boxes
     - Violations as red arrows
   - **Impact:** Visualize architecture layering
   - **Effort:** 8-10 hours

7. **Add Cochange Heatmap** ⭐️⭐️
   - **Current:** cochange_edges not visualized
   - **Fix:** Add heatmap to Health screen:
     - Matrix: files × files
     - Color intensity = cochange weight
     - Highlight high lift (surprising coupling)
   - **Impact:** See temporal coupling patterns
   - **Effort:** 6-8 hours

8. **Add Module Violations List** ⭐️
   - **Current:** Module detail has placeholder but not populated
   - **Fix:** Render `m.violations` as list with:
     - Source module → Target module
     - Layer direction (e.g., "Application → Data")
     - Count of violating edges
   - **Impact:** Identify specific layer violations
   - **Effort:** 2-3 hours

### Priority 3: Interaction Enhancements

9. **Add Advanced File Search** ⭐️⭐️
   - **Current:** Substring search only
   - **Fix:** Add query syntax:
     - `role:MODEL` — Filter by role
     - `risk:>0.7` — Filter by signal threshold
     - `churn:CHURNING` — Filter by trajectory
     - `orphan:true` — Boolean filters
   - **Impact:** Power users can find files faster
   - **Effort:** 6-8 hours

10. **Add Signal Correlation Heatmap** ⭐️
    - **Current:** No way to see signal relationships
    - **Fix:** Add correlation matrix to Health screen:
      - Compute Pearson correlation between signals
      - Heatmap: signals × signals
      - Click cell → show scatterplot
    - **Impact:** Understand signal dependencies
    - **Effort:** 8-10 hours

11. **Add Concern Deep Dive** ⭐️
    - **Current:** Concern radar shows scores but no details
    - **Fix:** Click concern → filtered findings view
    - **Impact:** Understand what drives each concern score
    - **Effort:** 2-3 hours

12. **Add File Comparison View** ⭐️
    - **Current:** No way to compare two files
    - **Fix:** Add "Compare" button in file detail:
      - Select 2 files → side-by-side signal comparison
      - Highlight differences
    - **Impact:** Understand why one file is riskier
    - **Effort:** 6-8 hours

### Priority 4: Performance & UX

13. **Add Virtual Scrolling to File Table** ⭐️⭐️
    - **Current:** 200-file hard limit
    - **Fix:** Implement virtual scrolling (only render visible rows)
    - **Impact:** Support 1000+ file codebases
    - **Effort:** 6-8 hours
    - **Library:** Use native Intersection Observer or library like `react-window` (if migrating to React)

14. **Add Progressive State Loading** ⭐️
    - **Current:** Full state loaded on connect
    - **Fix:** Load overview first, then files/modules on demand
    - **Impact:** Faster initial page load
    - **Effort:** 8-10 hours

15. **Add Keyboard Shortcuts Everywhere** ⭐️
    - **Current:** Some shortcuts (1-5, j/k) but not comprehensive
    - **Fix:** Add shortcuts for:
      - `f` — Focus search
      - `c` — Toggle column picker
      - `g` — Go to file (fuzzy search)
      - `r` — Refresh analysis
    - **Impact:** Faster navigation for power users
    - **Effort:** 3-4 hours

16. **Add Dark/Light Theme Toggle** ⭐️
    - **Current:** Dark theme only
    - **Fix:** Add theme toggle, store in localStorage
    - **Impact:** Accessibility for light theme users
    - **Effort:** 4-6 hours

---

## Product Principles

### Core Design Principles (Current, Implicit)

1. **Information Density Over Simplicity**
   - Files table shows 7 signals, but 36 available
   - Trade-off: Dense data vs. overwhelm
   - **Principle:** Default to essential signals, progressive disclosure for advanced

2. **Real-Time Over Batch**
   - WebSocket live updates, file watcher auto-reanalysis
   - **Principle:** Developer sees impact of changes immediately

3. **Visual Over Textual**
   - Risk histogram, treemap, radar chart vs. tables
   - **Principle:** Graphical representation for pattern recognition

4. **Actionability Over Completeness**
   - Focus point shows "what to fix first" with actionability score
   - **Principle:** Guide user to highest-value actions

5. **Evidence-Based Over Opinionated**
   - Findings show evidence with percentiles, not just "this is bad"
   - **Principle:** Transparent reasoning, user can judge

6. **Keyboard-First Over Mouse-Only**
   - j/k navigation, Enter to open, 1-5 screen switching
   - **Principle:** Power users can navigate without mouse

7. **Unified View Over Scattered Reports**
   - Single dashboard with 5 screens vs. separate CLI commands
   - **Principle:** Cohesive experience, cross-reference easily

### Recommended Principles (Explicit, for Documentation)

8. **Progressive Disclosure**
   - Show essential data by default, expand on demand
   - **Example:** File table shows 7 signals, "Show All" reveals 36

9. **Contextual Relevance**
   - Different signals matter for different roles (entry points vs. models)
   - **Example:** Entry points care about blast_radius, models care about abstraction

10. **Trend Awareness**
    - Past context matters (is health improving or degrading?)
    - **Example:** Sparklines show trends, not just current value

---

## Complexity for New Developers

### What New Developers Need to Understand

#### Level 1: User Perspective (1-2 hours)

1. **What Shannon Insight Does**
   - Analyzes codebases using information theory + graph algorithms + git history
   - Outputs: Health score (1-10), findings (actionable issues), signals (62 metrics)

2. **Five Mental Models**
   - **Structural:** Code as a dependency graph (PageRank, cycles, communities)
   - **Temporal:** Code as a change history (churn, cochange, authorship)
   - **Semantic:** Code as a concept space (roles, naming, documentation)
   - **Architectural:** Code as layered modules (cohesion, coupling, violations)
   - **Risk:** Code as a risk surface (composite of all dimensions)

3. **Three Tier System**
   - **ABSOLUTE** (<15 files): Basic metrics, no percentiles
   - **BAYESIAN** (15-50 files): Empirical CDF percentiles, restricted finders
   - **FULL** (50+ files): Full percentile normalization, all finders

4. **Four Finding Categories**
   - **Incomplete:** Missing structure (orphans, dead code, hollow files)
   - **Fragile:** High change risk (unstable files, god files, bug attractors)
   - **Tangled:** Coupling issues (hidden coupling, layer violations, clones)
   - **Team:** Collaboration problems (knowledge silos, Conway violations)

#### Level 2: Developer Perspective (4-8 hours)

5. **Backend Pipeline (8 Stages)**
   - SCAN (FileMetrics) → PARSE (FileSyntax) → ANALYZE WAVE 1 (5 analyzers, topo-sorted) → CLEAR CACHE → ANALYZE WAVE 2 (SignalFusionAnalyzer) → FIND (22 finders) → DIAGNOSE → DEDUPLICATE & RANK → SNAPSHOT

6. **Analyzer DAG**
   - `StructuralAnalyzer` → provides structural (graph, cycles, communities)
   - `TemporalAnalyzer` → provides git_history, cochange, churn
   - `SpectralAnalyzer` → provides spectral (Fiedler, gap)
   - `SemanticAnalyzer` → requires structural, provides semantics, roles
   - `ArchitectureAnalyzer` → requires structural, provides architecture (modules, Martin metrics)
   - `SignalFusionAnalyzer` → requires ALL, provides signal_field (62 signals)

7. **Store Slots (10 Typed Slots)**
   - `file_metrics`, `file_syntax`, `structural`, `git_history`, `cochange`, `churn`, `author_distances`, `spectral`, `semantics`, `roles`, `architecture`, `signal_field`

8. **Signal Fusion Pipeline (6 Steps)**
   - Collect → Raw risk → Normalize (percentiles) → Module temporal → Composites → Laplacian (delta_h)

9. **Finder Protocol**
   - `name`, `requires` (frozenset of slots), `find(store) -> list[Finding]`
   - Graceful degradation: skip if required slots unavailable

10. **Snapshot Lifecycle**
    - Capture → Save to .shannon/history.db → Query for trends → Diff for deltas

#### Level 3: Architecture Perspective (8-16 hours)

11. **Six Infrastructure Patterns (v2)**
    - Signal enum + registry (Prometheus-inspired)
    - graphlib.TopologicalSorter (stdlib, DAG execution)
    - Typed Slot[T] store (replaces raw Optional)
    - Phase validation contracts (Dagster-inspired)
    - Fusion pipeline builder (lightweight typestate)
    - ThresholdStrategy (tier-aware finder thresholds)

12. **Language Scanner Abstraction**
    - `Scanner` protocol → `ConfigurableScanner` (regex-based) → `SyntaxExtractor` (tree-sitter optional)
    - Fallback chain: tree-sitter → regex → universal fallback

13. **Finding Identity Keys**
    - Rename-aware via persistence rename detection
    - Enables chronic finding tracking across snapshots

14. **Health Laplacian (delta_h)**
    - Graph Laplacian diffusion on health field
    - Propagates health influence from neighbors
    - High delta_h = file "pulls down" neighbors

15. **Composite Signal Weights**
    - risk_score = 0.3×structural + 0.25×temporal + 0.2×semantic + 0.15×graph + 0.1×team
    - All composites use percentile inputs (after normalization)

### Complexity Reduction Strategies

**For Onboarding:**
1. **Create "Start Here" Guide** — 30-minute tutorial covering 5 mental models
2. **Add Architecture Diagram** — Visual flowchart of pipeline stages
3. **Add Glossary** — Define 20 key terms (PageRank, churn, cohesion, etc.)
4. **Add Code Tour** — Annotated walkthrough of InsightKernel.run()

**For Development:**
5. **Standardize Module Structure** — All modules follow same pattern (models.py, analyzer.py, tests/)
6. **Add Type Stubs** — Complete mypy coverage, reduce "Any" types
7. **Document Invariants** — Preconditions/postconditions for analyzers
8. **Add Debug Mode** — `--debug-export` dumps pipeline state at each stage

**For Understanding:**
9. **Add Examples Repo** — Real-world examples for each finder (when it fires, why, how to fix)
10. **Add Video Walkthrough** — 10-minute screencast of dashboard usage
11. **Add FAQ** — 20 common questions (e.g., "Why is X file marked as orphan?")

---

## Documentation Cleanup Plan

### Phase 1: Archive Outdated Docs (2-3 hours)

**Create `/docs/archived/`** and move:
- `AGENT_PROMPT.md` (root)
- `PRIMITIVE_REDESIGN.md` (root)
- `docs/INSIGHT_DELIVERY_PIPELINE.md`
- `docs/REARCHITECTURE_PLAN.md`
- `docs/IMPLEMENTATION_AGENT_PROMPT.md`
- `docs/MATHEMATICAL_FOUNDATION.md` (use research/ version)
- `docs/DOCUMENTATION_PROMPT.md`
- `docs/QA-AGENT-PROMPT.md`
- `docs/DASHBOARD_PROMPTS.md`
- `docs/BASELINE_ANALYSIS.md`
- `docs/brainstorm-v2.md`
- `docs/framework.md`
- `docs/ir-spec.md`
- `docs/spec-v2.md` (replaced by v2/phases/)
- `docs/mathematics.md` (replaced by research/)
- `docs/solutions.md`
- `docs/walkthrough.md`

**Add `/docs/archived/README.md`** explaining what was archived and why.

### Phase 2: Fix Inconsistencies (2-3 hours)

1. **CONTRIBUTING.md** — Update module paths (analyzers → scanning, primitives → signals/plugins)
2. **CHANGELOG.md** — Update version (0.4.0 → 0.7.0 or clarify)
3. **examples/README.md** — Remove non-existent flags, update signatures
4. **DASHBOARD.md** — Add "Status: Implemented/Planned" tags to each feature

### Phase 3: Consolidate Duplication (1-2 hours)

5. **STATUS.md** — Consolidate into README "Current State" section, remove STATUS.md
6. **DASHBOARD_ROADMAP.md** — Move to `/docs/v2/BACKLOG.md` (append as B8-B15)

### Phase 4: Reorganize v2 Docs (2-3 hours)

7. **Create `/docs/v2/README.md`** with:
   - Overview of v2 vision
   - Link to all 8 phases
   - Link to registry files
   - Migration roadmap (v1 → v2 timeline)
   - Status: DESIGN (not implemented yet)

8. **Create `/docs/v2/modules/` with:**
   - `scanning.md` — Language scanners, tree-sitter integration
   - `graph.md` — Dependency graph, algorithms (PageRank, Louvain)
   - `signals.md` — Signal fusion, normalization, composites
   - `temporal.md` — Git extraction, churn, cochange
   - `semantics.md` — Role classification, concepts
   - `architecture.md` — Module detection, Martin metrics, layers
   - `persistence.md` — TensorSnapshot, SQLite schema
   - `insights.md` — Finders, kernel orchestration

### Phase 5: Add Missing Docs (4-6 hours)

9. **Create `docs/GETTING_STARTED.md`** with:
   - Installation
   - First analysis
   - Understanding output
   - Five mental models
   - FAQ (10 common questions)

10. **Create `docs/ARCHITECTURE.md`** with:
    - Pipeline flowchart
    - Analyzer DAG diagram
    - Store slot diagram
    - Signal fusion pipeline
    - Persistence flow

11. **Create `docs/EXTENDING.md`** with:
    - Adding a language scanner (tutorial)
    - Adding a finder (tutorial)
    - Adding a signal plugin (tutorial)
    - Testing guide
    - Publishing to PyPI

12. **Create `docs/GLOSSARY.md`** with:
    - 20 key terms (PageRank, churn, cohesion, instability, etc.)
    - Alphabetized, cross-referenced

13. **Create `docs/API.md`** with:
    - HTTP endpoints (`/api/state`, `/api/export/json`, etc.)
    - WebSocket protocol
    - Python API (`InsightKernel`, `AnalysisStore`)
    - Stability matrix (stable/beta/experimental)

14. **Update `docs/SIGNALS.md`** with:
    - Add header: "This is v1 documentation"
    - Add link to v2 spec: `docs/v2/registry/signals.md`
    - Add missing signals (62 total, currently 28 documented)

15. **Update `docs/FINDERS.md`** with:
    - Add header: "This is v1 documentation"
    - Add link to v2 spec: `docs/v2/registry/finders.md`
    - Verify count matches implementation (28 in doc, ~22 in code?)

### Phase 6: Documentation Governance (1-2 hours)

16. **Create `docs/DOCUMENTATION_GUIDE.md`** with:
    - Documentation principles (DRY, single source of truth)
    - Where to document what (README vs docs/ vs docstrings)
    - When to archive vs. delete
    - Version markers (v1, v2, v3)
    - Update checklist (when adding feature, update X, Y, Z)

17. **Add Documentation CI Check** with:
    - Check for broken internal links
    - Check for orphaned files (not linked anywhere)
    - Check for version mismatches (e.g., CHANGELOG vs __init__.py)

---

## Roadmap Clarity

### Current State (v1, Production)

**Features:**
- ✅ 62 signals (36 file, 15 module, 11 global)
- ✅ 22 finders (6 structural, 4 temporal, 4 team, 8 cross-dimensional)
- ✅ 8 language scanners (Python, Go, TS, Java, Rust, Ruby, C/C++, universal)
- ✅ CLI with 9 commands (analyze, diff, explain, health, history, report, serve, journey, tui)
- ✅ Live dashboard with 5 screens (overview, issues, files, modules, health)
- ✅ SQLite persistence with 6 tables (snapshots, signal_history, findings, lifecycle)
- ✅ WebSocket real-time updates
- ✅ File watcher auto-reanalysis
- ✅ 247 tests, production-ready

**Known Gaps:**
- ❌ `broken_call_count` signal (requires CALL edges)
- ❌ `glue_deficit` signal (research needed)
- ⚠️ Frontend displays 37% of backend signals

### Short-Term Roadmap (1-2 months)

**Goal:** Complete v1 frontend, stabilize documentation

**Milestones:**
1. **Frontend Signal Completion** (2 weeks)
   - Add sparklines to file/module detail
   - Add "Show All Signals" toggle to file table
   - Add missing signal sections to file detail (semantics, team context, graph position)
   - Add churn trajectory badges
   - Add module violations list

2. **Visualization Enhancements** (2 weeks)
   - Add dependency graph visualization (D3.js or Cytoscape.js)
   - Add layer architecture diagram
   - Add cochange heatmap

3. **Documentation Cleanup** (1 week)
   - Archive outdated docs (16 files → /archived/)
   - Fix inconsistencies (CONTRIBUTING.md, CHANGELOG.md, examples/README.md)
   - Create GETTING_STARTED.md, ARCHITECTURE.md, EXTENDING.md, GLOSSARY.md, API.md

4. **Performance Optimization** (1 week)
   - Optimize `build_dashboard_state` with caching
   - Add virtual scrolling to file table (support 1000+ files)
   - Add progressive state loading

**Deliverable:** v1.0 release (production-ready, complete frontend, clean docs)

### Medium-Term Roadmap (3-6 months)

**Goal:** Begin v2 implementation (phases 0-2)

**Milestones:**
1. **Phase 0: Infrastructure Hardening** (2 weeks)
   - Implement 6 infrastructure patterns (Signal enum, TopologicalSorter, Typed Slot, etc.)
   - Migrate from Primitives to SignalField
   - Add phase validation contracts

2. **Phase 1: Deep Parsing** (3 weeks)
   - Integrate tree-sitter for all 8 languages
   - Implement FileSyntax extractor
   - Add `has_main_guard`, `call_targets`, `decorators`
   - Optional install: `pip install shannon-codebase-insight[parsing]`

3. **Phase 2: Semantics** (3 weeks)
   - Implement 3-tier concept extraction (TF-IDF+Louvain, keyword freq, single concept)
   - Add naming drift analyzer
   - Add docstring coverage (Python AST, others comment-based)
   - Add role classification (7 roles)

**Deliverable:** v2.0-alpha release (enhanced parsing + semantics)

### Long-Term Roadmap (6-12 months)

**Goal:** Complete v2 implementation (phases 3-7)

**Milestones:**
1. **Phase 3: Graph Enrichment** (4 weeks)
   - DAG depth (BFS from entry points)
   - Orphan detection (in_degree=0, not entry/test)
   - Centrality Gini (inequality measure)
   - NCD clone detection (LSH + pairwise, threshold 0.3)
   - Author distance (G5 metric space)

2. **Phase 4: Architecture** (4 weeks)
   - Module detection (directory-based + role clustering)
   - Martin metrics (cohesion, coupling, instability, abstractness)
   - Layer inference (topological sort + role hints)
   - Violation detection

3. **Phase 5: Signal Fusion** (3 weeks)
   - Implement 6-step fusion pipeline (collect, raw_risk, normalize, module_temporal, composites, laplacian)
   - Add tier-aware normalization (ABSOLUTE/BAYESIAN/FULL)
   - Compute all 11 composite signals
   - Compute health Laplacian (delta_h)

4. **Phase 6: Enhanced Finders** (2 weeks)
   - Implement 15 new finders (9 structural, 2 architecture, 4 cross-dimensional)
   - Add tier-aware thresholds
   - Add hotspot filter (total_changes > median)

5. **Phase 7: Persistence v2** (2 weeks)
   - Migrate to TensorSnapshot v2 schema
   - Add signal_history, module_signal_history, global_signal_history tables
   - Add finding_lifecycle tracking
   - Add rename detection for identity keys

**Deliverable:** v2.0 release (full spec implementation)

### Research Backlog (Ongoing)

**Deferred Features** (from `docs/v2/BACKLOG.md`):
- B1: CALL edges (requires static analysis)
- B2: TYPE_FLOW edges (requires type system integration)
- B3: CP/Tucker decomposition (tensor methods)
- B4: Kind 3 temporal reconstruction (advanced time series)
- B5: Seasonality/stationarity operators (time series patterns)
- B6: G3 TYPE_FLOW distance space (deferred until CALL edges)
- B7: Combined Laplacian over 6 spaces (research)

**New Research Areas:**
- Code smells (25+ patterns from research/)
- Security findings (SAST integration from research/)
- Defect prediction (machine learning models from research/)

---

## Action Items Summary

### Critical (Do This Week)

1. ✅ **Create this audit document** (DONE)
2. **Wire sparkline data** — Populate `f.trends` in `build_dashboard_state` (2-4 hours)
3. **Fix CONTRIBUTING.md** — Update module paths (30 mins)
4. **Archive outdated docs** — Move 16 files to /archived/ (1 hour)
5. **Create /docs/v2/README.md** — Overview of v2 vision (1 hour)

### High Priority (Do This Month)

6. **Add "Show All Signals" toggle** to file table (4-6 hours)
7. **Add missing signal sections** to file detail (4-6 hours)
8. **Add dependency graph visualization** (12-16 hours)
9. **Create GETTING_STARTED.md** (2-3 hours)
10. **Create ARCHITECTURE.md** (3-4 hours)
11. **Optimize `build_dashboard_state` performance** (4-6 hours)

### Medium Priority (Do Next 3 Months)

12. **Implement Phase 0 infrastructure** (2 weeks)
13. **Implement Phase 1 deep parsing** (3 weeks)
14. **Implement Phase 2 semantics** (3 weeks)
15. **Add layer architecture diagram** (8-10 hours)
16. **Add cochange heatmap** (6-8 hours)

---

## Conclusion

Shannon Insight has a **solid v1 foundation** with comprehensive backend capabilities and a functional frontend. The main gaps are:

1. **Frontend displays only 37% of backend signals** — Many computed metrics not shown in UI
2. **Documentation is fragmented** — v1/v2 mixing, outdated docs clutter main docs/
3. **Missing visualizations** — Dependency graph, layer diagram, cochange heatmap not implemented

The recommended strategy is:

1. **Short-term:** Complete v1 frontend (2-3 weeks) → v1.0 release
2. **Medium-term:** Clean up documentation (1 week), begin v2 Phase 0-2 (2-3 months) → v2.0-alpha release
3. **Long-term:** Complete v2 Phases 3-7 (6 months) → v2.0 release

This audit provides a clear roadmap for strategic decision-making, developer onboarding, and product evolution.

---

**Document Version:** 1.0
**Date:** 2026-02-14
**Author:** CTO-level Product Audit
**Next Review:** 2026-03-14 (1 month)
