Temporal Module Architecture

  1. High-Level Data Flow

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                           TemporalAnalyzer                                  │
  │                         (orchestrator entry point)                          │
  └─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                            GitExtractor                                     │
  │                                                                             │
  │   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
  │   │ _is_git_repo │ ───▶ │ _run_git_log │ ───▶ │ _parse_log   │             │
  │   │  (rev-parse) │      │  (subprocess)│      │   (regex)    │             │
  │   └──────────────┘      └──────────────┘      └──────────────┘             │
  │                                                       │                     │
  │                                                       ▼                     │
  │                                              ┌──────────────┐               │
  │                                              │  GitHistory  │               │
  │                                              │  + Commit[]  │               │
  │                                              └──────────────┘               │
  └─────────────────────────────────────────────────────────────────────────────┘
                                      │
                      ┌───────────────┼───────────────┐
                      ▼               ▼               ▼
              ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
              │ build_churn │ │build_cochange│ │compute_author│
              │  _series    │ │   _matrix   │ │  _distances │
              └─────────────┘ └─────────────┘ └─────────────┘
                      │               │               │
                      ▼               ▼               ▼
              ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
              │Dict[path,   │ │CoChangeMatrix│ │List[Author │
              │ChurnSeries] │ │             │ │  Distance] │
              └─────────────┘ └─────────────┘ └─────────────┘
                      │               │               │
                      └───────────────┼───────────────┘
                                      ▼
                            ┌─────────────────┐
                            │  AnalysisStore  │
                            │                 │
                            │ ├─ git_history  │
                            │ ├─ churn        │
                            │ ├─ cochange     │
                            │ └─ author_dists │
                            └─────────────────┘

  2. Git Log Parsing

  ┌─────────────────────────────────────────────────────────────────┐
  │                         Git Command                             │
  │                                                                 │
  │  git log --format=%H|%at|%ae|%s --name-only -n5000             │
  │           ───┬── ──┬─ ──┬─ ─┬─                                 │
  │              │     │    │   └─ subject (for fix/refactor ratio)│
  │              │     │    └───── author email                    │
  │              │     └────────── unix timestamp                  │
  │              └──────────────── 40-char SHA                     │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                       Raw Output                                │
  │                                                                 │
  │  abc123...|1700000000|alice@example.com|fix auth bug           │
  │  foo.py                                                        │
  │  bar.py                                                        │
  │                                                                 │
  │  def456...|1699900000|bob@example.com|refactor module          │
  │  foo.py                                                        │
  │  baz.py                                                        │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ _parse_log() with regex
  ┌─────────────────────────────────────────────────────────────────┐
  │                     Parsing Algorithm                           │
  │                                                                 │
  │  FOR each line:                                                 │
  │    IF line matches ^[0-9a-f]{40}\|...$  (header pattern)       │
  │      → Flush previous commit (if has files)                    │
  │      → Split line with maxsplit=3 (subject can have |)         │
  │      → Start new commit                                        │
  │    ELSE IF current_hash exists                                 │
  │      → Append line as file path                                │
  │                                                                 │
  │  Key: Only commits WITH files are kept (merge commits dropped) │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                      Data Objects                               │
  │                                                                 │
  │  Commit                      GitHistory                         │
  │  ┌────────────────────┐      ┌─────────────────────────┐       │
  │  │ hash: str (40 hex) │      │ commits: List[Commit]   │       │
  │  │ timestamp: int     │      │   (newest first)        │       │
  │  │ author: str        │      │ file_set: Set[str]      │       │
  │  │ files: List[str]   │      │   (all files ever seen) │       │
  │  │ subject: str       │      │ span_days: int          │       │
  │  └────────────────────┘      │   (newest - oldest)     │       │
  │                              └─────────────────────────┘       │
  └─────────────────────────────────────────────────────────────────┘

  3. Churn Series Computation

  ┌─────────────────────────────────────────────────────────────────┐
  │                    build_churn_series()                         │
  │                                                                 │
  │  Input: GitHistory, analyzed_files, window_weeks=4             │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │               Step 1: Time Window Bucketing                     │
  │                                                                 │
  │  window_secs = window_weeks × 7 × 86400                        │
  │  num_windows = (max_ts - min_ts) / window_secs + 1             │
  │                                                                 │
  │  Timeline:                                                      │
  │  ├────────┼────────┼────────┼────────┤                         │
  │  │ week 0 │ week 1 │ week 2 │ week 3 │                         │
  │  └────────┴────────┴────────┴────────┘                         │
  │      ▲        ▲▲       ▲                                       │
  │      │        ││       └─ commit C                             │
  │      │        │└───────── commit B                             │
  │      │        └────────── commit B (same file)                 │
  │      └─────────────────── commit A                             │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │              Step 2: Per-File Aggregation                       │
  │                                                                 │
  │  FOR each commit:                                               │
  │    window_idx = (timestamp - min_ts) / window_secs             │
  │    is_fix = any(fix_kw in subject.lower())                     │
  │    is_refactor = any(refactor_kw in subject.lower())           │
  │                                                                 │
  │    FOR each file in commit.files ∩ analyzed_files:             │
  │      file_windows[file][window_idx] += 1                       │
  │      file_authors[file][author] += 1                           │
  │      file_fix_count[file] += is_fix                            │
  │      file_refactor_count[file] += is_refactor                  │
  │                                                                 │
  │  fix_keywords: fix, bug, patch, hotfix, bugfix, repair, issue  │
  │  refactor_kw:  refactor, cleanup, reorganize, restructure...   │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │              Step 3: Signal Computation                         │
  │                                                                 │
  │  FOR each file:                                                 │
  │    counts = [3, 1, 5, 2]  (changes per window)                 │
  │                                                                 │
  │    ┌─────────────────────────────────────────────────────────┐ │
  │    │ slope = linear_regression(counts)                       │ │
  │    │                                                         │ │
  │    │   y                                                     │ │
  │    │   5│       *                                            │ │
  │    │   4│                                                    │ │
  │    │   3│ *                   slope = Σ(i-x̄)(v-ȳ)           │ │
  │    │   2│               *            ─────────────           │ │
  │    │   1│     *                       Σ(i-x̄)²               │ │
  │    │   0└─────────────────▶ window                           │ │
  │    │     0   1   2   3                                       │ │
  │    └─────────────────────────────────────────────────────────┘ │
  │                                                                 │
  │    ┌─────────────────────────────────────────────────────────┐ │
  │    │ cv = std(counts) / mean(counts)                         │ │
  │    │     = σ / μ  (coefficient of variation)                 │ │
  │    │                                                         │ │
  │    │     cv = 0    → perfectly steady                        │ │
  │    │     cv < 0.5  → relatively stable                       │ │
  │    │     cv > 1.0  → highly erratic                          │ │
  │    └─────────────────────────────────────────────────────────┘ │
  │                                                                 │
  │    ┌─────────────────────────────────────────────────────────┐ │
  │    │ author_entropy = -Σ p(a) × log₂(p(a))                   │ │
  │    │                                                         │ │
  │    │   p(a) = commits_by_author_a / total_commits_on_file   │ │
  │    │                                                         │ │
  │    │   1 author  → H = 0                                     │ │
  │    │   2 authors (50/50) → H = 1.0                           │ │
  │    │   4 authors (25% each) → H = 2.0                        │ │
  │    └─────────────────────────────────────────────────────────┘ │
  │                                                                 │
  │    bus_factor = 2^author_entropy                               │
  │    fix_ratio = fix_commits / total_commits                     │
  │    refactor_ratio = refactor_commits / total_commits           │
  │    change_entropy = -Σ p(w) × log₂(p(w))  (window dist)       │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │              Step 4: Trajectory Classification                  │
  │                                                                 │
  │                    ┌──────────────────┐                        │
  │                    │ total_changes ≤ 1│                        │
  │                    └────────┬─────────┘                        │
  │                         YES │ NO                               │
  │                      ┌──────┴──────┐                           │
  │                      ▼             ▼                           │
  │                  DORMANT    ┌──────────────┐                   │
  │                             │ slope < -0.1 │                   │
  │                             └──────┬───────┘                   │
  │                                YES │ NO                        │
  │                         ┌─────────┴─────────┐                  │
  │                         ▼                   ▼                  │
  │                   STABILIZING    ┌────────────────────┐        │
  │                                  │slope > 0.1 & cv>1.0│        │
  │                                  └─────────┬──────────┘        │
  │                                        YES │ NO                │
  │                                  ┌─────────┴─────────┐         │
  │                                  ▼                   ▼         │
  │                               SPIKING      ┌───────────┐       │
  │                                            │ cv > 0.8  │       │
  │                                            └─────┬─────┘       │
  │                                              YES │ NO          │
  │                                            ┌─────┴─────┐       │
  │                                            ▼           ▼       │
  │                                        CHURNING   STABILIZING  │
  │                                                                │
  │  ⚠️  NOTE: Thresholds differ from v2 spec (spec uses cv > 0.5) │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                       ChurnSeries                               │
  │  ┌────────────────────────────────────────────────────────────┐│
  │  │ file_path: str                                             ││
  │  │ window_counts: [3, 1, 5, 2]                                ││
  │  │ total_changes: 11                                          ││
  │  │ trajectory: "churning"                                     ││
  │  │ slope: 0.1                                                 ││
  │  │ cv: 0.65                                                   ││
  │  │ bus_factor: 1.75                                           ││
  │  │ author_entropy: 0.81                                       ││
  │  │ fix_ratio: 0.30                                            ││
  │  │ refactor_ratio: 0.10                                       ││
  │  │ change_entropy: 1.92                                       ││
  │  └────────────────────────────────────────────────────────────┘│
  └─────────────────────────────────────────────────────────────────┘

  4. Co-Change Matrix

  ┌─────────────────────────────────────────────────────────────────┐
  │                  build_cochange_matrix()                        │
  │                                                                 │
  │  Input: GitHistory, analyzed_files, min_cochanges=2            │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │              Temporal Decay Weighting                           │
  │                                                                 │
  │  weight(commit) = e^(-λ × days_since_commit)                   │
  │                                                                 │
  │  λ = ln(2) / 90  (90-day half-life)                            │
  │                                                                 │
  │  ┌─────────────────────────────────────────────────────────┐   │
  │  │ weight                                                  │   │
  │  │   1.0 ┤ ****                                            │   │
  │  │   0.5 ┤      ****                                       │   │
  │  │   0.25┤           ****                                  │   │
  │  │   0.0 ┼────────────────────────▶ days                   │   │
  │  │         0   90   180   270                              │   │
  │  └─────────────────────────────────────────────────────────┘   │
  │                                                                 │
  │  Recent co-changes matter MORE than old ones                   │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │              Pair Counting (Sparse)                             │
  │                                                                 │
  │  FOR each commit:                                               │
  │    relevant = commit.files ∩ analyzed_files                    │
  │    IF len(relevant) > 30: skip (bulk reformat filter)          │
  │                                                                 │
  │    weight = e^(-λ × days_since)                                │
  │                                                                 │
  │    FOR each file in relevant:                                  │
  │      file_change_counts[file] += weight                        │
  │                                                                 │
  │    FOR each pair (a, b) in combinations(relevant, 2):          │
  │      pair_counts[(a,b)] += weight                              │
  │      pair_raw_counts[(a,b)] += 1                               │
  │                                                                 │
  │  Example commit: {foo.py, bar.py, baz.py}                      │
  │  Creates pairs: (bar.py, foo.py), (bar.py, baz.py),            │
  │                 (baz.py, foo.py)                                │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │              Lift Computation                                   │
  │                                                                 │
  │  FOR each pair (a, b) with raw_count >= min_cochanges:         │
  │                                                                 │
  │    ┌───────────────────────────────────────────────────────┐   │
  │    │ Confidence (conditional probability):                 │   │
  │    │                                                       │   │
  │    │   P(B | A) = weighted_cochange / weighted_changes_A   │   │
  │    │   P(A | B) = weighted_cochange / weighted_changes_B   │   │
  │    │                                                       │   │
  │    │   "If A changed, how often did B also change?"       │   │
  │    └───────────────────────────────────────────────────────┘   │
  │                                                                 │
  │    ┌───────────────────────────────────────────────────────┐   │
  │    │ Lift (association strength):                          │   │
  │    │                                                       │   │
  │    │            observed co-occurrence                     │   │
  │    │   lift = ─────────────────────────                    │   │
  │    │            expected under independence                │   │
  │    │                                                       │   │
  │    │         weighted_cochange                             │   │
  │    │       = ─────────────────────────                     │   │
  │    │         (total_a × total_b) / total_weight            │   │
  │    │                                                       │   │
  │    │   lift > 1.0 → co-change MORE than expected           │   │
  │    │   lift = 1.0 → independent                            │   │
  │    │   lift < 1.0 → co-change LESS than expected           │   │
  │    └───────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                     CoChangeMatrix                              │
  │  ┌────────────────────────────────────────────────────────────┐│
  │  │ pairs: Dict[(str,str), CoChangePair]  (sparse, sorted keys)││
  │  │ total_commits: int                                         ││
  │  │ file_change_counts: Dict[str, int]                         ││
  │  └────────────────────────────────────────────────────────────┘│
  │                                                                 │
  │                      CoChangePair                               │
  │  ┌────────────────────────────────────────────────────────────┐│
  │  │ file_a, file_b: str                                        ││
  │  │ cochange_count: int  (raw count)                           ││
  │  │ total_a, total_b: float  (weighted)                        ││
  │  │ confidence_a_b, confidence_b_a: float                      ││
  │  │ lift: float                                                ││
  │  │ weight: float  (weighted co-change count)                  ││
  │  └────────────────────────────────────────────────────────────┘│
  └─────────────────────────────────────────────────────────────────┘

  5. Author Distance (G5 Space)

  ┌─────────────────────────────────────────────────────────────────┐
  │              compute_author_distances()                         │
  │                                                                 │
  │  Purpose: Measure team similarity between files                 │
  │  Used for: Conway's Law violation detection                     │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │         Step 1: Build Per-File Author Distributions            │
  │                                                                 │
  │  FOR each commit:                                               │
  │    FOR each file ∈ commit.files ∩ analyzed_files:             │
  │      file_author_counts[file][author] += 1                     │
  │                                                                 │
  │  Example:                                                       │
  │    foo.py: {alice: 5, bob: 3}                                  │
  │    bar.py: {alice: 2, carol: 6}                                │
  │    baz.py: {bob: 4, carol: 2}                                  │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │         Step 2: Normalize to Probability Distributions          │
  │                                                                 │
  │  weights[file][author] = count / total_commits_on_file         │
  │                                                                 │
  │  Example:                                                       │
  │    foo.py: {alice: 0.625, bob: 0.375}                          │
  │    bar.py: {alice: 0.25, carol: 0.75}                          │
  │    baz.py: {bob: 0.67, carol: 0.33}                            │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │         Step 3: Build Author → Files Index (Sparse)            │
  │                                                                 │
  │  author_files[author] = {files where author contributed}       │
  │                                                                 │
  │  Example:                                                       │
  │    alice → {foo.py, bar.py}                                    │
  │    bob   → {foo.py, baz.py}                                    │
  │    carol → {bar.py, baz.py}                                    │
  │                                                                 │
  │  Only compute distance for file pairs sharing ≥1 author        │
  │  (keeps representation sparse for large codebases)             │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │         Step 4: Weighted Jaccard Distance                       │
  │                                                                 │
  │  FOR each pair (A, B) sharing at least one author:             │
  │                                                                 │
  │    ┌───────────────────────────────────────────────────────┐   │
  │    │              Σ min(wₐ(A), wₐ(B))                      │   │
  │    │ Jaccard = ─────────────────────────                   │   │
  │    │              Σ max(wₐ(A), wₐ(B))                      │   │
  │    │                                                       │   │
  │    │ distance = 1 - Jaccard                                │   │
  │    └───────────────────────────────────────────────────────┘   │
  │                                                                 │
  │  Example: foo.py vs bar.py                                      │
  │                                                                 │
  │    author │ w(foo) │ w(bar) │ min  │ max                       │
  │    ───────┼────────┼────────┼──────┼─────                      │
  │    alice  │  0.625 │  0.25  │ 0.25 │ 0.625                     │
  │    bob    │  0.375 │  0.0   │ 0.0  │ 0.375                     │
  │    carol  │  0.0   │  0.75  │ 0.0  │ 0.75                      │
  │    ───────┴────────┴────────┴──────┴─────                      │
  │    Σ min = 0.25                                                │
  │    Σ max = 1.75                                                │
  │    Jaccard = 0.25 / 1.75 = 0.143                               │
  │    distance = 1 - 0.143 = 0.857  (different teams!)            │
  │                                                                 │
  │  distance = 0.0 → same author distribution (same team)         │
  │  distance = 1.0 → no overlap (completely different teams)      │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                     AuthorDistance                              │
  │  ┌────────────────────────────────────────────────────────────┐│
  │  │ file_a: str                                                ││
  │  │ file_b: str                                                ││
  │  │ distance: float  [0, 1)  (only pairs with d < 1.0 stored) ││
  │  └────────────────────────────────────────────────────────────┘│
  │                                                                 │
  │  Used by: CONWAY_VIOLATION finder                              │
  │  Condition: high structural coupling + high author distance    │
  │            = different teams maintaining tightly-coupled code  │
  └─────────────────────────────────────────────────────────────────┘

  6. Store Integration

  ┌─────────────────────────────────────────────────────────────────┐
  │                    TemporalAnalyzer.analyze()                   │
  └─────────────────────────────────────────────────────────────────┘
                                │
           ┌────────────────────┼────────────────────┐
           ▼                    ▼                    ▼
  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
  │  store.git_history│ │   store.churn   │ │  store.cochange  │
  │  .set(history)    │ │   .set(churn)   │ │   .set(matrix)   │
  └──────────────────┘ └──────────────────┘ └──────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                store.author_distances.set(ad)                   │
  └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                   _write_to_store()                             │
  │                                                                 │
  │  Writes to FactStore for downstream finders:                   │
  │                                                                 │
  │  Per-file signals:                                              │
  │  ┌─────────────────────────────────────────────────────────┐   │
  │  │ Signal.TOTAL_CHANGES      │ churn.total_changes         │   │
  │  │ Signal.CHURN_CV           │ churn.cv                    │   │
  │  │ Signal.BUS_FACTOR         │ churn.bus_factor            │   │
  │  │ Signal.AUTHOR_ENTROPY     │ churn.author_entropy        │   │
  │  │ Signal.FIX_RATIO          │ churn.fix_ratio             │   │
  │  │ Signal.REFACTOR_RATIO     │ churn.refactor_ratio        │   │
  │  │ Signal.CHURN_TRAJECTORY   │ churn.trajectory            │   │
  │  │ Signal.CHURN_SLOPE        │ churn.slope                 │   │
  │  └─────────────────────────────────────────────────────────┘   │
  │                                                                 │
  │  Relations:                                                     │
  │  ┌─────────────────────────────────────────────────────────┐   │
  │  │ RelationType.COCHANGES_WITH │ weight = lift             │   │
  │  └─────────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────┘

  7. Graceful Degradation

  ┌─────────────────────────────────────────────────────────────────┐
  │                    Error Handling Flow                          │
  │                                                                 │
  │  ┌─────────────────┐                                           │
  │  │ Not a git repo? │────YES────▶ store.git_history.set_error() │
  │  └────────┬────────┘             return early                   │
  │           │ NO                                                  │
  │           ▼                                                     │
  │  ┌─────────────────┐                                           │
  │  │ < 10 commits?   │────YES────▶ store.git_history.set_error() │
  │  │ (shallow clone) │             return early                   │
  │  └────────┬────────┘                                           │
  │           │ NO                                                  │
  │           ▼                                                     │
  │  ┌─────────────────┐                                           │
  │  │ Output > 50MB?  │────YES────▶ truncate, warn, continue      │
  │  └────────┬────────┘                                           │
  │           │ NO                                                  │
  │           ▼                                                     │
  │  ┌─────────────────┐                                           │
  │  │ Solo author?    │────YES────▶ author_distances = []         │
  │  │ (< 2 authors)   │             (G5 empty, but churn OK)      │
  │  └────────┬────────┘                                           │
  │           │ NO                                                  │
  │           ▼                                                     │
  │       Full analysis                                             │
  └─────────────────────────────────────────────────────────────────┘
