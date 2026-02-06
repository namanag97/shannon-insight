# Registry: Signal Catalog

The single source of truth for every measurable signal in Shannon Insight.

**Rules**:
- Every signal is defined exactly ONCE in this file.
- No other document may define a signal's formula. Module specs describe HOW to compute; this file defines WHAT the signal is.
- Every signal belongs to exactly one dimension (from `dimensions.md`) and one scale (from `scales.md`).
- Every signal specifies which IR produces it and which module computes it.
- Every signal specifies its polarity: "high is bad" or "high is good" — this determines how `trend` is classified (IMPROVING vs WORSENING).

---

## Per-File Signals (Scale S4)

### From IR1 (Syntactic) — computed by `scanning/`

| # | Signal | Dimension | Type | Range | High means | Absolute threshold | Formula |
|---|--------|-----------|------|-------|------------|-------------------|---------|
| 1 | `lines` | D1 SIZE | int | [0, ∞) | larger file (risk factor) | > 500 | Line count |
| 2 | `function_count` | D1 SIZE | int | [0, ∞) | more functions (complexity) | > 30 | Count of function/method definitions |
| 3 | `class_count` | D1 SIZE | int | [0, ∞) | more classes | — | Count of class definitions |
| 4 | `max_nesting` | D2 SHAPE | int | [0, ∞) | deeper nesting (harder to read) | > 4 | Max nesting depth across all functions in file |
| 5 | `impl_gini` | D2 SHAPE | float | [0, 1] | uneven implementation (AI signature) | > 0.6 | Gini coefficient of function body_token counts. G ≈ 0 = uniform. G > 0.6 = bimodal (some complete, some stubs). |
| 6 | `stub_ratio` | D2 SHAPE | float | [0, 1] | more stubs (incomplete) | > 0.5 | `mean(stub_score(f) for f in functions)` where `stub_score(f) = 1 - min(1, body_tokens / (signature_tokens × 3))`. Hard classify: `body_tokens < 5` OR body matches `^\s*(pass\|\\.\\.\\.\|return\s+None?)\s*$`. |
| 7 | `import_count` | D4 REFERENCE | int | [0, ∞) | more dependencies | — | Count of import declarations |

### From IR2 (Semantic) — computed by `semantics/`

| # | Signal | Dimension | Type | Range | High means | Absolute threshold | Formula |
|---|--------|-----------|------|-------|------------|-------------------|---------|
| 8 | `role` | D3 NAMING | enum | Role | — | — | Deterministic decision tree on structural signals. Values: MODEL, SERVICE, UTILITY, CONFIG, TEST, CLI, INTERFACE, EXCEPTION, CONSTANT, ENTRY_POINT, MIGRATION, UNKNOWN. See `modules/semantics/role-classification.md`. |
| 9 | `concept_count` | D3 NAMING | int | [0, ∞) | more concepts (less focused) | — | Count of concept clusters from TF-IDF + Louvain on token co-occurrence graph. Requires 20+ unique identifiers; below threshold = 1 (role-based). |
| 10 | `concept_entropy` | D3 NAMING | float | [0, ∞) | less focused (god file risk) | > 1.5 | `H = -Σ w(c) × log₂(w(c))` where w(c) = weight of concept c. H = 0 = single concept. H > 1.5 = many competing concepts. |
| 11 | `naming_drift` | D3 NAMING | float | [0, 1] | filename misleads (smell) | > 0.7 | `1 - cosine(tfidf(filename_tokens), tfidf(content_concept_tokens))`. Requires 20+ unique identifiers. |
| 12 | `todo_density` | D3 NAMING | float | [0, ∞) | more incomplete markers | > 0.05 | `(TODO + FIXME + HACK count) / lines` |
| 13 | `docstring_coverage` | D3 NAMING | float | [0, 1] | better documented (good) | — | `documented_public_symbols / total_public_symbols`. Polarity: high is GOOD. |

### From IR3 (Graph) — computed by `graph/`

| # | Signal | Dimension | Type | Range | High means | Absolute threshold | Formula |
|---|--------|-----------|------|-------|------------|-------------------|---------|
| 14 | `pagerank` | D4 REFERENCE | float | [0, 1] | more central (risk factor) | — | `PR(v) = (1-d)/N + d × Σ PR(u)/out_degree(u)` for u→v. d = 0.85, iterate until `max(\|PR_new - PR_old\|) < 10⁻⁶` or 50 iterations. |
| 15 | `betweenness` | D4 REFERENCE | float | [0, 1] | more bridge-like (fragility) | — | `B(v) = Σ_{s≠v≠t} σ(s,t\|v) / σ(s,t)`. Brandes' algorithm O(\|V\| × \|E\|). |
| 16 | `in_degree` | D4 REFERENCE | int | [0, ∞) | more dependents | — | Count of files that import this file. |
| 17 | `out_degree` | D4 REFERENCE | int | [0, ∞) | more dependencies | — | Count of files this file imports. |
| 18 | `blast_radius_size` | D4 REFERENCE | int | [0, n-1] | wider impact | — | `\|BFS(v, reverse(G))\| - 1`. Transitive reverse closure size. |
| 19 | `depth` | D4 REFERENCE | int | [0, ∞) or -1 | deeper in call chain | — | Longest path from nearest entry point via BFS. `-1` = unreachable (orphan). |
| 20 | `is_orphan` | D4 REFERENCE | bool | {0,1} | disconnected (unused code) | = 1 | `in_degree = 0 AND role ≠ ENTRY_POINT AND role ≠ TEST`. Structural fact. |
| 21 | `phantom_import_count` | D4 REFERENCE | int | [0, ∞) | broken references | > 0 | Count of import declarations where `resolved_path = null` and not external-installed. |
| 22 | `broken_call_count` | D4 REFERENCE | int | [0, ∞) | broken call targets | > 0 | Count of CALL edge targets that cannot be resolved. Requires CALL edges (Phase 3+). |
| 23 | `community` | D4 REFERENCE | int | [0, k) | — | — | Louvain community assignment ID. Not a quality signal; used for boundary alignment. |
| 24 | `compression_ratio` | D5 INFORMATION | float | [0, 1] | more repetitive / boilerplate | — | `len(zlib.compress(content)) / len(content)`. < 0.15 = highly repetitive. 0.3-0.6 = normal. > 0.7 = very dense. |
| 25 | `semantic_coherence` | D5 INFORMATION | float | [0, 1] | more focused (good) | — | `mean(cosine(vᵢ, vⱼ))` for all function-level TF-IDF vector pairs i < j. Polarity: high is GOOD. |
| 26 | `cognitive_load` | D5 INFORMATION | float | [0, ∞) | harder to understand (risk factor) | — | `(concepts × complexity × nesting_factor) × (1 + G)` where `concepts = function_count + class_count`, `complexity = mean cyclomatic complexity`, `nesting_factor = e^(max_nesting / 5)`, `G = gini(function_body_token_counts)`. The exponential nesting penalty reflects nonlinear comprehension cost. |

### From IR5t (Temporal) — computed by `temporal/`

| # | Signal | Dimension | Type | Range | High means | Absolute threshold | Formula |
|---|--------|-----------|------|-------|------------|-------------------|---------|
| 27 | `total_changes` | D6 CHANGE | int | [0, ∞) | more volatile | — | Count of commits touching this file. |
| 28 | `churn_trajectory` | D6 CHANGE | enum | Trajectory | — | — | Classification of churn time series. Values: DORMANT, STABILIZING, STABLE, CHURNING, SPIKING. See `temporal-operators.md` for classification rules. |
| 29 | `churn_slope` | D6 CHANGE | float | (-∞, ∞) | increasing churn (risk) | — | Linear regression slope of changes-per-4-week-window series. |
| 30 | `churn_cv` | D6 CHANGE | float | [0, ∞) | erratic changes | > 1.0 | Coefficient of variation of changes-per-window series. |
| 31 | `bus_factor` | D7 AUTHORSHIP | float | [1, ∞) | more authors (good) | = 1 | `2^H` where `H = -Σ p(a) × log₂(p(a))` and `p(a) = commits_by_author(a) / total_commits`. Effective author count. Polarity: high is GOOD; low (= 1) is risk. |
| 32 | `author_entropy` | D7 AUTHORSHIP | float | [0, ∞) | more distributed (good) | — | `H = -Σ p(a) × log₂(p(a))`. H = 0 = single author. H = log₂(k) = k equally-contributing authors. Polarity: high is GOOD. |
| 33 | `fix_ratio` | D8 INTENT | float | [0, 1] | attracts more bugs (risk) | > 0.4 | `\|commits matching fix/bug/patch/hotfix/resolve/repair\| / total_commits`. |
| 34 | `refactor_ratio` | D8 INTENT | float | [0, 1] | more proactive maintenance (good) | — | `\|commits matching refactor/restructure/reorganize/clean/simplify\| / total_commits`. Polarity: high is GOOD. |

### Composites (from IR5s) — computed by `signals/`

| # | Signal | Type | Range | High means | Formula |
|---|--------|------|-------|------------|---------|
| 35 | `risk_score` | float | [0, 1] | riskier | `0.25 × pctl(pagerank) + 0.20 × pctl(blast_radius_size) + 0.20 × pctl(cognitive_load) + 0.20 × instability_factor + 0.15 × (1 - bus_factor/max_bus_factor)` where `instability_factor = 1.0 if trajectory ∈ {CHURNING, SPIKING} else 0.3`. |
| 36 | `wiring_quality` | float | [0, 1] | better connected (good) | `1 - (0.30 × is_orphan + 0.25 × stub_ratio + 0.25 × (phantom_import_count / max(import_count, 1)) + 0.20 × (broken_call_count / max(total_calls, 1)))`. Polarity: high is GOOD. |

---

## Per-Module Signals (Scale S5)

All computed by `architecture/` (IR4) or aggregated from per-file signals by `signals/` (IR5s).

| # | Signal | Dimension | Source | Formula |
|---|--------|-----------|--------|---------|
| 37 | `cohesion` | D4 REFERENCE | IR4 | `internal_edges / (file_count × (file_count - 1))`. 0 if file_count ≤ 1. |
| 38 | `coupling` | D4 REFERENCE | IR4 | `external_edges / (internal_edges + external_edges)`. 0 if no edges. |
| 39 | `instability` | D4 REFERENCE | IR4 | `Ce / (Ca + Ce)` where Ca = afferent (incoming), Ce = efferent (outgoing). Martin's I metric. |
| 40 | `abstractness` | D4 REFERENCE | IR4 | `abstract_symbols / total_symbols`. Expanded for Python: ABC, Protocol, NotImplementedError, never-instantiated. See `modules/architecture/martin-metrics.md`. |
| 41 | `main_seq_distance` | D4 REFERENCE | IR4 | `\|abstractness + instability - 1\|`. D = 0 = ideal. Zone of pain: A < 0.3 AND I < 0.3. Zone of uselessness: A > 0.7 AND I > 0.7. |
| 42 | `boundary_alignment` | D4 REFERENCE | IR4 | `files_in_dominant_louvain_community / total_files_in_module`. |
| 43 | `layer_violation_count` | D4 REFERENCE | IR4 | Count of backward/skip edges into this module. |
| 44 | `role_consistency` | D3 NAMING | IR4 | `max(role_count) / total_files` in module. 1.0 = all files same role. |
| 45 | `velocity` | D6 CHANGE | IR5t | Commits per week touching any file in module. |
| 46 | `coordination_cost` | D7 AUTHORSHIP | IR5t | `mean(distinct_authors_per_commit)` for commits touching module. |
| 47 | `knowledge_gini` | D7 AUTHORSHIP | IR5t | Gini coefficient of per-author commit counts within module. > 0.7 = silo. |
| 48 | `module_bus_factor` | D7 AUTHORSHIP | IR5t | `min(bus_factor)` across high-centrality files in module. |
| 49 | `mean_cognitive_load` | D5 INFORMATION | IR5s | `mean(cognitive_load)` across files in module. |
| 50 | `file_count` | D1 SIZE | IR0 | Number of source files in module. |
| 51 | `health_score` | composite | IR5s | `0.20 × cohesion + 0.15 × (1-coupling) + 0.20 × (1-main_seq_distance) + 0.15 × boundary_alignment + 0.15 × role_consistency + 0.15 × (1-mean_stub_ratio)`. Polarity: high is GOOD. |

---

## Global Signals (Scale S6)

All computed by `graph/` (IR3), `architecture/` (IR4), or `signals/` (IR5s).

| # | Signal | Dimension | Source | Formula |
|---|--------|-----------|--------|---------|
| 52 | `modularity` | D4 REFERENCE | IR3 | Louvain Q score. `Q = (1/2m) Σ [A_ij - k_ik_j/(2m)] δ(c_i, c_j)`. Q > 0.3 = good. |
| 53 | `fiedler_value` | D4 REFERENCE | IR3 | λ₂ of graph Laplacian L = D - A. Algebraic connectivity. Via Lanczos for top-k. λ₂ = 0 = disconnected. Small = bottleneck. Large = well-connected. |
| 54 | `spectral_gap` | D4 REFERENCE | IR3 | `λ₂ / λ₃`. Large = clear best cut. Small = ambiguous. |
| 55 | `cycle_count` | D4 REFERENCE | IR3 | Count of SCCs with \|nodes\| > 1. Tarjan's algorithm. |
| 56 | `centrality_gini` | D4 REFERENCE | IR3 | Gini coefficient of pagerank distribution. > 0.7 = hub-dominated. |
| 57 | `orphan_ratio` | D4 REFERENCE | IR3 | `count(is_orphan) / total_files`. |
| 58 | `phantom_ratio` | D4 REFERENCE | IR3 | `unresolved_edges / total_edges`. |
| 59 | `glue_deficit` | D4 REFERENCE | IR3 | `1 - \|{v: in_degree(v) > 0 AND out_degree(v) > 0}\| / \|V\|`. Fraction of nodes that are NOT internal (glue). |
| 60 | `wiring_score` | composite | IR5s | `1 - (0.25 × orphan_ratio + 0.25 × phantom_ratio + 0.20 × glue_deficit + 0.15 × mean(stub_ratio) + 0.15 × clone_ratio)`. AI quality composite. Polarity: high is GOOD. |
| 61 | `architecture_health` | composite | IR5s | Weighted combination of violation_rate, mean cohesion, mean coupling, mean D, boundary_alignment. See `composites.md`. Polarity: high is GOOD. |
| 62 | `codebase_health` | composite | IR5s | `0.25 × architecture_health + 0.25 × wiring_score + 0.20 × (1 - finding_density) + 0.15 × (global_bus_factor / team_size) + 0.15 × modularity`. The one number. Polarity: high is GOOD. |

---

## Signal Applicability by Temporal Operator

| Signal type | delta | velocity | trend | trajectory | volatility | seasonality | stationarity |
|---|---|---|---|---|---|---|---|
| Numeric (pagerank, lines, etc.) | x | x | x | x | x | x | x |
| Float ratio [0,1] (stub_ratio) | x | x | x | x | — | — | — |
| Boolean (is_orphan) | x | — | — | — | — | — | — |
| Enum (role, churn_trajectory) | x | — | — | — | — | — | — |
| Composite (risk_score, health) | x | x | x | x | x | — | — |

---

## Signal Count Summary

| Scope | Count | Notes |
|---|---|---|
| Per-file numeric | 28 | Signals 1-34 minus enums/bools |
| Per-file enum/bool | 4 | role, churn_trajectory, is_orphan, community |
| Per-file composite | 2 | risk_score, wiring_quality |
| Per-module | 15 | Signals 37-51 |
| Global | 11 | Signals 52-62 |
| **Total** | **62** | Excluding second-order temporal signals |

With 8 temporal operators per numeric signal: ~62 base + ~300 temporal derivatives ≈ **~360 total measurable quantities** per snapshot.
