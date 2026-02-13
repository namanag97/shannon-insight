# Finders Reference

Shannon Insight ships 28 finders that read from the unified signal field to detect structural problems. Each finder declares the signals it requires and degrades gracefully when those signals are unavailable (e.g., temporal finders are skipped when there's no git history).

## Structural Finders

### `high_risk_hub`

| Property | Value |
|----------|-------|
| **Name** | High Risk Hub |
| **Category** | Structural |
| **Severity** | 1.0 (CRITICAL) |
| **Effort** | MEDIUM |
| **Scope** | FILE |

**What It Detects**: Files that are both structurally central and problematic -- they have many dependents (high PageRank or blast radius) AND are complex or churning. A bug in these files ripples widely across the codebase.

**Signals Used**:
- `pagerank` >= 80th percentile OR `blast_radius_size` >= 80th percentile (centrality gate)
- `cognitive_load` >= 80th percentile OR `churn_trajectory` in {CHURNING, SPIKING} (problem gate)

**Example**:
```
HIGH RISK HUB — src/core/engine.py
  pagerank: 0.084 (92nd pctl)  blast_radius: 47  cognitive_load: 18.4 (89th pctl)
  → Split into smaller modules to reduce coupling; extract frequently-changing parts
```

**Why It Matters**: These are the files where a single defect can cascade through a large fraction of the codebase. They're the highest-leverage refactoring targets.

---

### `god_file`

| Property | Value |
|----------|-------|
| **Name** | God File |
| **Category** | Structural |
| **Severity** | 0.8 (HIGH) |
| **Effort** | HIGH |
| **Scope** | FILE |

**What It Detects**: Files with too many responsibilities. Identified by high cognitive load or many functions combined with low semantic coherence -- the file does many unrelated things.

**Signals Used**:
- `cognitive_load` >= 80th percentile OR `function_count` > 10
- `semantic_coherence` <= 30th percentile
- `function_count` >= 3

**Example**:
```
GOD FILE — src/utils/helpers.py
  cognitive_load: 22.1 (95th pctl)  semantic_coherence: 0.12 (8th pctl)  functions: 34
  → Identify clusters of related functions and extract each group into a focused module
```

**Why It Matters**: God files accumulate merge conflicts, are hard to understand, and resist refactoring because every change risks unrelated side effects.

---

### `orphan_code`

| Property | Value |
|----------|-------|
| **Name** | Orphan Code |
| **Category** | Structural |
| **Severity** | 0.55 (MEDIUM) |
| **Effort** | LOW |
| **Scope** | FILE |

**What It Detects**: Files with zero importers (in_degree=0) that aren't entry points, tests, or known dynamic-load targets. Excludes `__init__.py` files and files in plugin/scanner/finder directories.

**Signals Used**:
- `in_degree` = 0
- Not `__init__.py`, not entry point, not test file
- Not re-exported via parent `__init__` or sibling imports

**Example**:
```
ORPHAN CODE — src/legacy/old_processor.py
  in_degree: 0  is_orphan: true
  → Wire into dependency graph or remove if unused
```

**Why It Matters**: Orphan files may be dead code that wastes developer attention and increases cognitive load when navigating the codebase.

---

### `hollow_code`

| Property | Value |
|----------|-------|
| **Name** | Hollow Code |
| **Category** | Structural |
| **Severity** | 0.71 (HIGH) |
| **Effort** | MEDIUM |
| **Scope** | FILE |

**What It Detects**: Files where >60% of functions are stubs or empty implementations, combined with uneven function sizes (impl_gini > 0.6). Started but never finished.

**Signals Used**:
- `stub_ratio` > 0.6
- `impl_gini` > 0.6
- `function_count` >= 3

**Example**:
```
HOLLOW CODE — src/api/v2_handlers.py
  stub_ratio: 0.75  impl_gini: 0.82  functions: 12
  → Implement stub functions; prioritize those called by other files
```

**Why It Matters**: Hollow files create a false sense of architecture -- the structure exists but the behavior doesn't. Callers may hit runtime errors.

---

### `phantom_imports`

| Property | Value |
|----------|-------|
| **Name** | Phantom Imports |
| **Category** | Structural |
| **Severity** | 0.65-0.80 (scales with count) |
| **Effort** | MEDIUM |
| **Scope** | FILE |

**What It Detects**: Import statements that resolve to no file in the codebase. May indicate deleted modules, typos, or missing dependencies.

**Signals Used**:
- `phantom_import_count` > 0
- Severity: min(0.80, 0.65 + 0.03 * (count - 1))

**Example**:
```
PHANTOM IMPORTS — src/services/auth.py
  phantom_import_count: 3  out_degree: 8
  → Create missing modules or replace with existing library
```

**Why It Matters**: Phantom imports can cause runtime ImportErrors and indicate incomplete refactoring or missing package dependencies.

---

### `dead_dependency`

| Property | Value |
|----------|-------|
| **Name** | Dead Dependency |
| **Category** | Structural |
| **Severity** | 0.4 (LOW) |
| **Effort** | LOW |
| **Scope** | FILE_PAIR |

**What It Detects**: Import relationships where the two files have never co-changed in git history despite both being actively modified. The import may be vestigial.

**Signals Used**:
- Structural edge exists (import)
- Zero co-change evidence across 50+ commits
- Both files changed >= 3 times individually

**Example**:
```
DEAD DEPENDENCY — src/api/router.py → src/legacy/compat.py
  co-changes: 0 over 688 commits  individual changes: 45, 12
  → Check if import is unused or vestigial; remove if not needed
```

**Why It Matters**: Dead dependencies clutter the dependency graph and may indicate unused code paths.

## Architecture Finders

### `hidden_coupling`

| Property | Value |
|----------|-------|
| **Name** | Hidden Coupling |
| **Category** | Architecture |
| **Severity** | 0.9 (HIGH) |
| **Effort** | LOW |
| **Scope** | FILE_PAIR |

**What It Detects**: File pairs that co-change together frequently (min 3 co-occurrences) but share no import relationship. The coupling is implicit -- possibly through shared database tables, config files, or undocumented conventions.

**Signals Used**:
- Co-change lift >= 2.0
- Co-change confidence >= 0.5
- Mutual information >= 0.05 bits
- No structural dependency between pair

**Example**:
```
HIDDEN COUPLING — src/api/cache.py ↔ src/db/queries.py
  co-changes: 9/11 (82%)  lift: 4.2  confidence: 0.82  MI: 0.34 bits
  → Add import or extract shared logic to make implicit contract explicit
```

**Why It Matters**: Hidden coupling means changes to one file silently require changes to the other. This is a maintenance trap that no linter can catch.

---

### `boundary_mismatch`

| Property | Value |
|----------|-------|
| **Name** | Boundary Mismatch |
| **Category** | Architecture |
| **Severity** | 0.6 (MEDIUM) |
| **Effort** | HIGH |
| **Scope** | MODULE |

**What It Detects**: Modules (directories) where files are more connected to other directories than to their siblings. The directory boundary doesn't match the actual dependency community.

**Signals Used**:
- `boundary_alignment` < 0.7
- Module has > 2 files

**Example**:
```
BOUNDARY MISMATCH — src/api/
  boundary_alignment: 0.42  files: 8
  → Relocate misplaced files to their actual dependency communities
```

**Why It Matters**: Mismatched boundaries mean the directory structure is misleading -- developers look in the wrong place for related code.

---

### `layer_violation`

| Property | Value |
|----------|-------|
| **Name** | Layer Violation |
| **Category** | Architecture |
| **Severity** | 0.52 (MEDIUM) |
| **Effort** | MEDIUM |
| **Scope** | MODULE_PAIR |

**What It Detects**: Dependencies that flow backward through the detected architectural layer order (e.g., models importing from controllers).

**Signals Used**:
- Detected layer ordering from architecture analysis
- Backward or skip-layer dependency edges

**Example**:
```
LAYER VIOLATION — src/models/ → src/controllers/
  direction: backward  layer_depth_diff: -2
  → Inject dependency or restructure to respect layer order
```

**Why It Matters**: Layer violations erode the intended architecture, creating cycles and making it harder to reason about the system's structure.

---

### `zone_of_pain`

| Property | Value |
|----------|-------|
| **Name** | Zone of Pain |
| **Category** | Architecture |
| **Severity** | 0.60-0.70 (scales with distance from main sequence) |
| **Effort** | HIGH |
| **Scope** | MODULE |

**What It Detects**: Modules with low abstractness (<0.3) and low instability (<0.3) -- they're concrete and stable, meaning many modules depend on them but they expose no interfaces. Changes to these modules are painful because they ripple to all dependents.

**Signals Used**:
- `abstractness` < 0.3
- `instability` < 0.3

**Example**:
```
ZONE OF PAIN — src/core/
  abstractness: 0.08  instability: 0.15  main_seq_distance: 0.77
  → Extract interfaces or reduce dependents
```

**Why It Matters**: Modules in the zone of pain resist change. They should either expose interfaces (raise abstractness) or have fewer dependents (raise instability).

---

### `flat_architecture`

| Property | Value |
|----------|-------|
| **Name** | Flat Architecture |
| **Category** | Architecture |
| **Severity** | 0.60 (MEDIUM) |
| **Effort** | HIGH |
| **Scope** | CODEBASE |

**What It Detects**: Codebases where all files are at the same depth (max_depth <= 1) and there are no orchestration/coordination files (glue_deficit > 0.5). The system is flat with no composition layer.

**Signals Used**:
- `depth` <= 1 for all files
- `glue_deficit` > 0.5

**Example**:
```
FLAT ARCHITECTURE
  max_depth: 1  glue_deficit: 0.72  modules: 12
  → Add a composition layer to orchestrate leaf modules
```

**Why It Matters**: Flat architectures lack the glue code that coordinates between modules, leading to implicit coordination through conventions or global state.

---

### `architecture_erosion`

| Property | Value |
|----------|-------|
| **Name** | Architecture Erosion |
| **Category** | Architecture |
| **Severity** | 0.65-1.0 (scales with erosion rate) |
| **Effort** | HIGH |
| **Scope** | CODEBASE |

**What It Detects**: Progressive degradation of architectural rules. Queries snapshot history for increasing `violation_rate` across 3+ snapshots.

**Signals Used**:
- `violation_rate` trend over 3+ snapshots
- >= 2 consecutive increasing transitions
- Total increase >= 5%

**Example**:
```
ARCHITECTURE EROSION
  violation_rate: 0.08 → 0.11 → 0.15 (3 snapshots)  erosion: +7%
  → Add pre-commit hooks to block new violations; dedicate sprint time to fix existing ones
```

**Why It Matters**: Architecture erosion is insidious -- each small violation seems harmless but the cumulative effect degrades the system.

---

### `accidental_coupling`

| Property | Value |
|----------|-------|
| **Name** | Accidental Coupling |
| **Category** | Architecture |
| **Severity** | 0.50 (MEDIUM) |
| **Effort** | MEDIUM |
| **Scope** | FILE_PAIR |

**What It Detects**: Import relationships between files that have almost nothing in common semantically. The dependency exists but the files don't share concepts.

**Signals Used**:
- Structural edge exists (import)
- Combined similarity < 0.15 (0.6 * import_fingerprint + 0.4 * concept_overlap)
- Neither file is infrastructure (models, config, utils)

**Example**:
```
ACCIDENTAL COUPLING — src/billing/invoice.py → src/auth/tokens.py
  concept_overlap: 0.03  import_similarity: 0.08
  → Remove or abstract the dependency; files are unrelated
```

**Why It Matters**: Accidental coupling creates unnecessary dependency chains that increase blast radius and complicate testing.

## Stability Finders

### `unstable_file`

| Property | Value |
|----------|-------|
| **Name** | Unstable File |
| **Category** | Stability |
| **Severity** | 0.7 (HIGH) |
| **Effort** | MEDIUM |
| **Scope** | FILE |

**What It Detects**: Files with active churn that isn't stabilizing. The file keeps getting modified without converging.

**Signals Used**:
- `churn_trajectory` in {CHURNING, SPIKING}
- `total_changes` > median

**Example**:
```
UNSTABLE FILE — src/api/handlers.py
  churn_trajectory: CHURNING  total_changes: 67  churn_cv: 2.3
  → Split file or add tests to reduce churn; investigate unclear requirements
```

**Why It Matters**: Files that don't stabilize suggest unclear requirements, poor abstractions, or conflicting stakeholders.

---

### `chronic_problem`

| Property | Value |
|----------|-------|
| **Name** | Chronic Problem |
| **Category** | Stability |
| **Severity** | Base severity * 1.25 |
| **Effort** | HIGH |
| **Scope** | Inherits from wrapped finding |

**What It Detects**: Findings that persist across 3+ consecutive snapshots. The wrapped finding's severity is amplified by 1.25x because persistence indicates the problem is being ignored or is too costly to fix with current approach.

**Signals Used**:
- Queries `.shannon/history.db` for finding persistence
- Requires 3+ snapshots with the same finding

**Example**:
```
CHRONIC PROBLEM — god_file on src/core/engine.py (persisting 5 snapshots)
  original_severity: 0.80 → chronic_severity: 1.00
  → Schedule dedicated refactoring; create tech debt ticket
```

**Why It Matters**: Chronic problems are the technical debt that compounds -- the longer they persist, the harder they are to fix.

---

### `thrashing_code`

| Property | Value |
|----------|-------|
| **Name** | Thrashing Code |
| **Category** | Stability |
| **Severity** | 0.75-0.90 |
| **Effort** | MEDIUM |
| **Scope** | FILE |

**What It Detects**: Files with erratic, spiking change patterns -- they don't have steady churn but rather unpredictable bursts of modification.

**Signals Used**:
- `churn_trajectory` = SPIKING OR `churn_cv` > 1.5
- `total_changes` >= 3
- `lines` > 30
- Severity 0.90 if both SPIKING and churn_cv > 1.5

**Example**:
```
THRASHING CODE — src/config/settings.py
  churn_trajectory: SPIKING  churn_cv: 3.1  total_changes: 28
  → Review recent changes for conflicting requirements; consider design review
```

**Why It Matters**: Thrashing indicates conflicting requirements, bikeshedding, or a component that nobody owns.

---

### `bug_magnet`

| Property | Value |
|----------|-------|
| **Name** | Bug Magnet |
| **Category** | Stability |
| **Severity** | 0.80-0.95 |
| **Effort** | HIGH |
| **Scope** | FILE |

**What It Detects**: Files where >40% of commits mention bug-fix keywords (fix, bug, patch, hotfix). Combined with minimum 5 changes to avoid false positives on low-activity files.

**Signals Used**:
- `fix_ratio` > 0.4
- `total_changes` >= 5
- Severity scales with fix_ratio and cognitive_load

**Example**:
```
BUG MAGNET — src/parser/tokenizer.py
  fix_ratio: 0.62  total_changes: 45  cognitive_load: 14.2
  → Refactor or add more tests; analyze git history for root causes
```

**Why It Matters**: A high fix ratio means the file is a recurring source of defects. Adding tests or refactoring has outsized ROI.

## Team Finders

### `knowledge_silo`

| Property | Value |
|----------|-------|
| **Name** | Knowledge Silo |
| **Category** | Team |
| **Severity** | 0.70 (HIGH) |
| **Effort** | LOW |
| **Scope** | FILE |

**What It Detects**: Central files (top 20% by PageRank) owned by a single contributor (bus_factor <= 1.5). Requires team_size > 1 to avoid flagging solo projects.

**Signals Used**:
- `bus_factor` <= 1.5
- `pagerank` >= 80th percentile
- `team_size` > 1

**Example**:
```
KNOWLEDGE SILO — src/core/scheduler.py
  bus_factor: 1.0  pagerank: 0.072 (88th pctl)  author_entropy: 0.0
  → Pair-program or rotate ownership; single point of knowledge failure
```

**Why It Matters**: If the sole contributor leaves, understanding and maintaining this central file becomes extremely difficult.

---

### `review_blindspot`

| Property | Value |
|----------|-------|
| **Name** | Review Blindspot |
| **Category** | Team |
| **Severity** | 0.80 (HIGH) |
| **Effort** | MEDIUM |
| **Scope** | FILE |

**What It Detects**: High-centrality files with single ownership AND no test file. These have no safety net -- no second pair of eyes and no automated verification.

**Signals Used**:
- `pagerank` >= 80th percentile
- `bus_factor` <= 1.5
- No corresponding test file detected
- `team_size` > 1

**Example**:
```
REVIEW BLINDSPOT — src/billing/calculator.py
  pagerank: 0.065 (85th pctl)  bus_factor: 1.0  test_file: none
  → Add tests and add a reviewer; high-centrality with no safety net
```

**Why It Matters**: Central files without tests or review diversity are the most likely source of undetected regressions.

---

### `truck_factor`

| Property | Value |
|----------|-------|
| **Name** | Truck Factor |
| **Category** | Team |
| **Severity** | 0.85-0.95 |
| **Effort** | LOW |
| **Scope** | FILE |

**What It Detects**: Files where exactly one person has ever committed, combined with structural importance (high PageRank or blast radius >= 3) and non-trivial size (> 50 lines).

**Signals Used**:
- `bus_factor` = 1.0
- `pagerank` >= 70th percentile OR `blast_radius_size` >= 3
- `lines` > 50
- `team_size` > 1
- Severity boosts to 0.95 if both high PageRank and high blast radius

**Example**:
```
TRUCK FACTOR — src/infra/deploy.py
  bus_factor: 1.0  blast_radius: 12  pagerank: 0.045 (78th pctl)  lines: 234
  → Document and have another person review; consider pair programming
```

**Why It Matters**: Named after the "bus factor" thought experiment. If this one contributor is unavailable, this critical file becomes a black box.

---

### `conway_violation`

| Property | Value |
|----------|-------|
| **Name** | Conway Violation |
| **Category** | Team |
| **Severity** | 0.55 (MEDIUM) |
| **Effort** | HIGH |
| **Scope** | MODULE_PAIR |

**What It Detects**: Structurally-coupled modules maintained by very different teams. Conway's Law predicts that the software structure mirrors the team structure -- violations mean the code coupling doesn't match team ownership.

**Signals Used**:
- Module pair structural coupling weight > 0.3
- Author distance > 0.8 (very different contributor sets)

**Example**:
```
CONWAY VIOLATION — src/api/ ↔ src/models/
  coupling_weight: 0.65  author_distance: 0.92
  → Align team boundaries with module structure
```

**Why It Matters**: When tightly-coupled code is maintained by different teams, coordination overhead increases and integration bugs are common.

## Code Quality Finders

### `copy_paste_clone`

| Property | Value |
|----------|-------|
| **Name** | Copy-Paste Clone |
| **Category** | Code Quality |
| **Severity** | 0.50-0.60 |
| **Effort** | MEDIUM |
| **Scope** | FILE_PAIR |

**What It Detects**: File pairs with high content similarity measured by Normalized Compression Distance (NCD < 0.3). Severity scales inversely with NCD.

**Signals Used**:
- NCD < 0.3 (Normalized Compression Distance)
- Severity: 0.50 + (0.3 - NCD) * 0.33

**Example**:
```
COPY-PASTE CLONE — src/handlers/v1.py ↔ src/handlers/v2.py
  NCD: 0.12  lines_a: 180  lines_b: 195
  → Extract shared logic into a common module
```

**Why It Matters**: Cloned code means bug fixes need to be applied in multiple places, which is error-prone and wasteful.

---

### `incomplete_implementation`

| Property | Value |
|----------|-------|
| **Name** | Incomplete Implementation |
| **Category** | Code Quality |
| **Severity** | 0.80-0.95 |
| **Effort** | HIGH |
| **Scope** | FILE |

**What It Detects**: Files with multiple signals of incompleteness: phantom imports (runtime errors), broken calls, high stub ratio, or low implementation uniformity. Requires 2+ signals OR 1 runtime-error signal.

**Signals Used**:
- `phantom_import_count` > 0 (runtime error)
- `broken_call_count` > 0 (runtime error)
- `stub_ratio` > 0.6
- `impl_gini` < 0.15 AND `function_count` > 5 AND `stub_ratio` > 0.3
- Severity += 0.05 per issue + 0.10 for runtime errors

**Example**:
```
INCOMPLETE IMPLEMENTATION — src/services/payment.py
  phantom_imports: 2  stub_ratio: 0.64  issues: 3
  → Fix imports, implement stubs, or remove dead code
```

**Why It Matters**: Incomplete files are ticking time bombs -- they may pass static analysis but fail at runtime.

---

### `naming_drift`

| Property | Value |
|----------|-------|
| **Name** | Naming Drift |
| **Category** | Code Quality |
| **Severity** | 0.45 (LOW) |
| **Effort** | LOW |
| **Scope** | FILE |

**What It Detects**: Files whose filename tokens don't match the concepts actually found in the code. The name suggests one thing, the content does another.

**Signals Used**:
- `naming_drift` > 0.7

**Example**:
```
NAMING DRIFT — src/utils.py
  naming_drift: 0.84
  → Rename file to match actual content, or extract mismatched logic
```

**Why It Matters**: Misleading filenames waste developer time during navigation and make the codebase harder to learn.

---

### `directory_hotspot`

| Property | Value |
|----------|-------|
| **Name** | Directory Hotspot |
| **Category** | Code Quality |
| **Severity** | 0.80-0.90 |
| **Effort** | HIGH |
| **Scope** | MODULE |

**What It Detects**: Directories where most files are high-risk or churning. Indicates systemic issues rather than isolated file problems.

**Signals Used**:
- `file_count` >= 3
- Not a test directory
- `high_risk_file_count` >= 2 OR `hotspot_file_count` > 50% of files
- Severity 0.90 if both conditions, 0.88 if >50% high-risk

**Example**:
```
DIRECTORY HOTSPOT — src/api/
  files: 7  high_risk: 5 (71%)  hotspot: 4 (57%)
  → Systemic issues; refactor entire directory rather than individual files
```

**Why It Matters**: When most files in a directory are problematic, fixing them one by one won't help -- the directory needs structural redesign.

---

### `duplicate_incomplete`

| Property | Value |
|----------|-------|
| **Name** | Duplicate Incomplete |
| **Category** | Code Quality |
| **Severity** | 0.75-0.90 |
| **Effort** | HIGH |
| **Scope** | FILE_PAIR |

**What It Detects**: Clone pairs where both files are also incomplete (high stub ratio or phantom imports). Worse than regular clones because neither copy works fully.

**Signals Used**:
- Clone pair (NCD < 0.3)
- Both files: `stub_ratio` > 0.3 OR `phantom_import_count` > 0
- Severity += 0.10 if both have stub_ratio > 0.5
- Severity += 0.10 if both have phantom imports

**Example**:
```
DUPLICATE INCOMPLETE — src/api/v2.py ↔ src/api/v3.py
  NCD: 0.18  stub_ratio_a: 0.55  stub_ratio_b: 0.60
  → Complete one implementation and delete the duplicate
```

**Why It Matters**: Two incomplete copies of the same code are worse than one -- effort is split and neither version works.

---

### `weak_link`

| Property | Value |
|----------|-------|
| **Name** | Weak Link |
| **Category** | Code Quality |
| **Severity** | 0.75-0.85 |
| **Effort** | MEDIUM |
| **Scope** | FILE |

**What It Detects**: Files that are significantly worse than their graph neighborhood. Uses the health Laplacian: `delta_h = raw_risk(file) - mean(raw_risk(neighbors))`.

**Signals Used**:
- `delta_h` > 0.4 (absolute threshold)
- Not an orphan file
- Severity: 0.75 + (delta_h - 0.4) * 0.25 (capped at 0.85)

**Example**:
```
WEAK LINK — src/core/validator.py
  delta_h: 0.52  raw_risk: 0.71  neighborhood_mean: 0.19
  → File drags down its healthy neighborhood; prioritize improvement
```

**Why It Matters**: A weak link in an otherwise healthy neighborhood has outsized negative impact on the surrounding code's quality.

---

### `bug_attractor`

| Property | Value |
|----------|-------|
| **Name** | Bug Attractor |
| **Category** | Code Quality |
| **Severity** | 0.70 (HIGH) |
| **Effort** | MEDIUM |
| **Scope** | FILE |

**What It Detects**: Central files (top 20% by PageRank) with high fix ratio (>40%). The combination of importance and bug-prone history makes these high-priority targets.

**Signals Used**:
- `fix_ratio` > 0.4
- `pagerank` >= 80th percentile
- `team_size` > 1

**Example**:
```
BUG ATTRACTOR — src/core/parser.py
  fix_ratio: 0.48  pagerank: 0.061 (83rd pctl)  total_changes: 56
  → 40%+ bug fixes in central file; root-cause analysis needed
```

**Why It Matters**: A central file that keeps attracting bugs means defects propagate widely and recur frequently.

## Finder Behavior Notes

### Hotspot Filtering

18 of 28 finders use hotspot filtering -- they only fire on files that are above the median change activity threshold. This prevents flagging dormant files that aren't actively causing problems.

### Tier Minimum

Finders declare a minimum normalization tier:
- **ABSOLUTE** (13 finders): Works on any codebase, uses absolute thresholds
- **BAYESIAN** (14 finders): Requires 15+ files for percentile-based detection

### Graceful Degradation

Finders declare `requires` sets. If the required analysis phase didn't complete (e.g., no git history for `cochange`), the finder is silently skipped. The kernel logs a debug message.

### Max Findings

Most finders cap their output (typically 10-20 findings) to keep results actionable. The highest-severity findings are kept.
