# Shannon Insight V4 — Canonical System Specification

**Status**: SINGLE SOURCE OF TRUTH. Supersedes all v1/v2/v3 docs in this repo and all
documents in `~/Projects/shannon-v2/` (specs/, trial-run-v1, v3-reactive, hybrid event-log
experiment). Where any other document contradicts this one, **this one wins**.
**Cutover policy**: hard cutover, no backward compatibility, zero users, free to break APIs.
**Date**: 2026-08-23

---

## PART 0 — MANDATE & DOCTRINE

### 0.1 Ambition

> A codebase is a measurable system: an **8-dimension x 7-scale x T-time measurement field**.
> Findings are *derived quantities* computed from that field — never hand-crufted rules.
> The engine is the product: offline-first, `pip install`, deterministic, self-validating.
> End state: **Time Machine for Code Health** — a verdict in 5 seconds, one focus point,
> diff any two moments, forecast decay ("health < 6.0 in ~24 days"), every finding carrying
> evidence chains, calibrated confidence, and predicted post-fix values.

Positioning (validated across both repos' product briefs): existing tools are one-dimensional,
snapshot-based, rule-based. Shannon is multi-dimensional, temporal, derivation-based, and the
first to treat **AI-generated code quality as a first-class detection domain**.

### 0.2 Design Principles (binding)

| # | Principle | Origin / rationale |
|---|-----------|--------------------|
| P1 | **Facts are immutable, content-addressed, append-only.** Everything downstream is a derived view. | Hybrid event-log experiment (shannon-v2) + v3 fact architecture; kills snapshot JSON bloat, makes Kind-3 reconstruction feasible |
| P2 | **Identity before analytics.** Stable `file_id` across renames; canonical authors; bot filtering. | Every bus-factor/silo/co-change number is a lie after renames without this |
| P3 | **One store.** `ShannonDB` (SQLite). Facts + signals + findings + history in one schema. Parquet/DuckDB export is an extra, not a second truth. | Three-DB split and AnalysisStore/FactStore bridge are dead |
| P4 | **Registries are law.** Signals, patterns, thresholds, dimensions live in declarative registries compiled at startup into an executable DAG. Code reads the registry; the registry is not documentation of code. | "Specs say X, code does Y" killed shannon-v2 twice |
| P5 | **Precision over recall.** A missing finding is acceptable; a false positive burns trust permanently. Every finding carries confidence; uncalibrated numbers are labeled as such. | shannon-v2 doctrine, empirically relearned: NO_TEST_FILE noise 202→30 findings |
| P6 | **Deterministic core, optional intelligence.** Zero-network default (`--offline` is a tested contract). Embeddings/LLM are opt-in tiers with graceful degradation. | Product brief; privacy positioning |
| P7 | **Contracts are runtime artifacts.** The signal-dependency DAG, slot single-writer rules, polarity sanity, percentileable flags: compiled into a `ContractBundle` asserted by tests on every run of CI. | trial-run-v1's best invention; prevents the 22 documented failure modes structurally |
| P8 | **Batch pipeline with incremental invalidation**, not reactive streams. | v3-reactive evidence: RxPython complexity produced 24 failing tests / 20% coverage for gains achievable via content-hash invalidation |
| P9 | **Golden masters.** Deterministic fixture corpus with manifest hashes; property tests assert incremental==full equivalence. | Only reliable defense for a math-heavy pipeline |
| P10 | **Tiered execution is mandatory UX.** `check` (<5s, Tier 1 only), `analyze` (full), `--focus` (pruned DAG). Findings volume without tiers was rejected by users twice. | shannon-v2 lesson relearned; ABSOLUTE/BAYESIAN/FULL normalization tiers |

### 0.3 Evidence Base

1. **This repo's corpus**: 184 docs digested (v2 spec+registry+phases, v3-architecture,
   audits REAL_GAPS_2026-02-14 / PRODUCT_AUDIT / AUDIT-REPORT, design waves A–G, research
   folder, MATH-DAG, TENSOR-ARCHITECTURE).
2. **shannon-v2 corpus**: ARCHITECTURE_PROPOSAL, COMPREHENSIVE_ARCHITECTURE_AUDIT (7.2/10),
   DEVELOPMENT_PLAN (28-week plan), TECHNICAL_DEEP_DIVE, V2_V3_COMPARISON, V3_FINAL_STATUS,
   specs/ (78 docs incl. core-types.md 1627 lines), three implementation trees.
3. **External SOTA research** (2025–2026, ~120 sources across four domains): graph
   intelligence, information-theoretic metrics/clones/embeddings, repository mining/defect
   prediction, LLM-powered analysis. Key citations inline throughout; consolidated in
   Appendix C.

---

## PART I — THE COMPUTATION DAG

The entire system is one static DAG, declared in registries, topo-sorted at startup.
Nodes are *pure functions over typed inputs*. Two spines (structural ∥ temporal) join at L4.

```
                        ┌─────────────────────────────────────────────────────────┐
                        │                    L0 FACTS                             │
  filesystem ────────► scan ─► FileObservation{path, sha256, lang, size}           │
                        │        BlobStore(content-addressed)                      │
                        │   FileIdentityResolver (rename-proof file_id)            │
                        │   AuthorResolver (canonical authors, bots filtered)      │
  git log ───────────► git_extract ─► CommitFact[], FileChangeFact[], RenameEvent[]│
                        └────────┬───────────────────────┬────────────────────────┘
                                 │                       │
                 ┌───────────────▼──────────┐   ┌────────▼─────────────────────┐
                 │ L1 SYNTAX (structural    │   │ L3 TEMPORAL (temporal spine) │
                 │ spine)                   │   │                              │
                 │ tree-sitter parse        │   │ ChurnSeries per file_id      │
                 │  → FileSyntax            │   │ TrajectoryClassifier         │
                 │ FunctionDef/ClassDef/    │   │ IntentClassifier (fix/refact)│
                 │ ImportDecl               │   │ CoChangeMatrix (lift)        │
                 │ stub_ratio, impl_gini,   │   │ SZAnalyzer (bug-inducing)    │
                 │ nesting                  │   │ ChangeEntropy                │
                 └───────┬──────────────────┘   └────────┬─────────────────────┘
                         │                               │
                 ┌───────▼──────────────┐                │
                 │ L2 SEMANTICS         │                │
                 │ RoleClassifier(12)   │                │
                 │ ConceptExtractor     │                │
                 │ naming_drift         │                │
                 │ NL facts extraction  │                │
                 └───────┬──────────────┘                │
                         │                               │
                 ┌───────▼───────────────────────────────▼─────────────────────┐
                 │ L4 GRAPHS (join point)                                       │
                 │ CodeGraph: nodes FILE/FUNCTION/CLASS/AUTHOR/PKG              │
                 │ Layers: G_import G_call G_type G_cochange G_author           │
                 │         G_semantic* G_clone        (*optional embedder)       │
                 │ Set algebra: hidden=coch∖imp, dead=imp∖coch, conway=imp×¬aut │
                 └───────┬─────────────────────────────────────────────────────┘
                         │
                 ┌───────▼─────────────────────────────────────────────────────┐
                 │ L5 GRAPH ALGORITHMS                                          │
                 │ PageRank · Brandes betweenness · SCC+cycle diagnosis ·       │
                 │ Leiden communities · k-core/articulation · blast radius ·    │
                 │ Fiedler λ₂ · spectral gap λ₃−λ₂ · modularity Q · Gini        │
                 └───────┬─────────────────────────────────────────────────────┘
                         │
                 ┌───────▼─────────────────────────────────────────────────────┐
                 │ L6 CROSS-LAYER                                               │
                 │ NMI(layer_i; layer_j) → behavioral/conway/semantic coherence │
                 │ Temporal operators on any signal (delta@ velocity@ ...)      │
                 │ Semantic divergence quadrants (NCD × embedding cosine)*      │
                 └───────┬─────────────────────────────────────────────────────┘
                         │
                 ┌───────▼─────────────────────────────────────────────────────┐
                 │ L7 COMPOSITES                                                │
                 │ tier normalize (ABSOLUTE/BAYESIAN/FULL) → raw_risk →         │
                 │ Laplacian Δh → risk_score/wiring/health/codebase_health      │
                 │ calibration layer (isotonic when labels exist)               │
                 └───────┬─────────────────────────────────────────────────────┘
                         │
                 ┌───────▼─────────────────────────────────────────────────────┐
                 │ L8 PATTERNS                                                  │
                 │ PatternSpec registry (28 finders) + MotifCompiler            │
                 │ severity×confidence scoring · lifecycle hashing · ranking    │
                 └───────┬─────────────────────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐   ┌──────────────┐   ┌────────────────────┐
              │ DELIVERY            │   │ INTEL (opt)   │   │ EVAL HARNESS       │
              │ CLI/server/CI/SARIF │◄──│ embedder/LLM/ │   │ golden masters,    │
              │ report/MCP/repo-map │   │ MCP/adjudicate│   │ P/R telemetry, SZZ │
              └─────────────────────┘   └──────────────┘   │ ground truth loop  │
                                                           └────────────────────┘
```

### DAG node contract

Every node declares:
```python
Node(id="signals.pagerank",
     requires=[S("graphs.edges", layer="import")],   # typed requirements
     provides=S("pagerank"),                          # single-writer enforced
     phase="E", cost="O(k·|V|·|E|)", tier=Tier.ANALYZE)
```
Executor = `graphlib.TopologicalSorter`; structural and temporal spines run in parallel
until L4; `--focus <domain>` prunes the DAG transitively from required outputs;
`check` mode runs Tier-1 subgraph only.

---

## PART II — PHASED BUILD PLAN WITH MATHEMATICAL DERIVATIONS

Phases are ordered by dependency: **A(parse anything) → B(relate) → C(measure per-file)
→ D(temporal spine) → E(graph algorithms) → F(fusion) → G(patterns) → H(persist/time-travel)
→ I(intelligence tier) → J(delivery + eval)**. Each phase lists: goal, DAG nodes added,
the math (with derivations and why-it-is-correct arguments), external grounding, reuse
from existing trees, acceptance gates.

---

### PHASE A — PARSE ANY CODEBASE (L0 + L1)

**Goal**: turn any repo into immutable facts + syntax IRs, rename-proof, author-clean,
language-complete. Nothing else exists until this works on arbitrary input.

#### A.1 Content addressing & change detection

Every file becomes `FileObservation(path, sha256, language, size)`; content bytes stored
once in `BlobStore`. Parse results cached under `(sha256, parser_version)`.

*Math.* Hash-addressing gives change detection for free: file changed ⟺ hash differs —
no mtime heuristics, no content diffs. Parse cache hit rate after warm run approaches
1 − (changed_files / total_files); combined with incremental invalidation this yields the
70–90% recompute-avoidance claimed by the reactive rewrite, without its complexity.

#### A.2 Identity resolution (the foundation everything stands on)

Three-tier resolver produces stable `file_id` (UUID minted on Add, threaded through Rename,
popped on Delete):

1. **Exact**: blob SHA carried across a commit's rename entry.
2. **Git heuristic**: `git log -M` similarity ≥ 50% (configurable).
3. **Content fallback**: MinHash-Jaccard or NCD ≥ 0.7 on normalized token streams — covers
   splits/merges where git gives nothing. (This is Wave-B's NCD-rename idea, now grounded:
   CLSA 2026 showed identity errors injected **8.3M false line-deaths out of 32.5M births**
   — identity quality bounds every downstream statistic.)

Rename events logged as first-class facts `(old_path, new_path, method, confidence)`.
All per-file time series follow `file_id`, never paths.

**Author resolution**: `.mailmap` → email-domain heuristics → name-token fuzzy match
(Indel similarity; ESEM 2026 registered-report methodology) → canonical author registry.
Bot filter (BoDeGHa-style rules: `[bot]` suffixes, dependabot/renovate/greenkeeper,
cadence regularity) excludes bots from bus factor / silo / Conway math.

#### A.3 Syntax extraction (tree-sitter only)

Delete the regex scanner path entirely. Regex fallback caused silent finder degradation
(call_targets None) — a documented audit failure mode. Per-language query modules emit:

```
FileSyntax{parse_mode, has_errors, top_level_statements}
FunctionDef{name, params, return_type, body_tokens, signature_tokens, span,
            call_targets[], nesting_depth, decorators[]}
ClassDef{name, bases[], methods[], fields[], is_abstract}
ImportDecl{module, names[], resolved_path|null}
```

Derived primitives (formulas fixed here):

- **stub_score(fn)** = `1 − min(1, body_tokens / (signature_tokens × 3))`;
  `stub_ratio(file) = mean(stub_score)`. Rationale: a function whose body is tiny relative
  to its interface is declarative scaffolding; the ratio saturates at 1/3 body-to-signature
  balance. Hard stub patterns (pass/…/NotImplementedError/todo!/unimplemented!/
  panic!/empty) pin score to 1.0.
- **impl_gini** over function body sizes (sorted ascending x₁..xₙ):
  `G = Σᵢ (2i − n − 1)·xᵢ / (n²·x̄)`. G ∈ [0,1]; G > 0.6 = bimodal "few real bodies among
  many stubs" — the AI-generated signature. Gini chosen over entropy because it measures
  *concentration* (scale-free, insensitive to unit count), which is exactly the bimodality
  signal; entropy conflates many-uniform-small with many-mixed-large.
- **max_nesting**: AST depth of control-flow nesting (tree-sitter exact vs regex approximate
  was a known PARTIAL in baseline audits).
- **cyclomatic proxy** (for later phases): `CC ≈ 1 + count(if, elif, for, while, case,
  except, &&, ||, ?:)` — McCabe E−N+2P computed syntactically; validated adequate for
  ranking use, not for certification use.

**Grounding**: tree-sitter error-recovering grammars are the industry standard for
multi-language static tooling (GitHub semantic, Aider repo maps, Semgrep). Python 3.11+
floor (3.12 target) matches shannon-v2 decision and buys interpreter perf for free.

**Reuse**: current repo's `scanning/` tree-sitter modules + grammar installer (~80%);
shannon-v2 trial-run LanguageAgnosticAST normalization concept for cross-language metrics.

**Acceptance gates**
- All 8 languages parse fixtures; Python function counts match manual counts exactly.
- Rename/split/squash synthetic repos: identity-chain recovery ≥ 95% exact-tier, ≥ 85% overall.
- Golden manifests frozen for 5-fixture corpus (small/multi_lang/messy/clean/git_history).
- Throughput ≥ 20k LOC/s/core cold parse; empty files, latin-1, symlinks handled per
  degradation matrix (Part V).

---

### PHASE B — RELATE (L4 construction: imports, edges, set algebra)

**Goal**: build the multilayer graph skeleton. Algorithms come in Phase E; here we get
edges *right*, because every coupling finding is only as good as edge resolution.

#### B.1 Import resolution (deterministic, confidence-tagged)

Algorithm (ported from v3-reactive where it reached parity and was battle-tested on Flask):
1. Classify each ImportDecl relative/absolute.
2. Candidate generation: direct path, package `__init__`/`index`/`mod`, same-directory.
3. Priority order: exact > init/index > same-dir > ancestor walk with **progressive prefix
   stripping** (`flask.helpers` → strip leading segments until a match).
4. No match → classify external via ecosystem manifests (pyproject/go.mod/package.json+
   tsconfig paths/pom/Cargo.toml/Gemfile/#include) → else `PHANTOM_IMPORT`.

Edge record: `Edge(src, dst, type=IMPORT, symbols[], weight=1.0, confidence=HIGH)`.

#### B.2 Edge type ladder

| Type | Source | Confidence | Phase available |
|------|--------|-----------|-----------------|
| IMPORT | B.1 | HIGH | B |
| CALL | same-file free; imported-symbol via symbol index; `self.x` method resolution; chained attribute best-effort | HIGH/MEDIUM/LOW | W4 |
| TYPE_FLOW | annotation/type usage | LOW | backlogged |
| INHERIT | ClassDef.bases resolved | HIGH | W4 |
| CONTAINS | structural | HIGH | B |

Rule (confidence-gated consumption, adopted from design corpus): consumers declare minimum
edge confidence; `broken_call_count` stays 0 until CALL edges exist and finders consuming it
degrade explicitly (no silent zeros).

#### B.3 Layer schema & set algebra (the finding factory)

Seven named layers over the same vertex set V (files):

| Layer | Edge weight | Meaning |
|-------|------------|---------|
| G_import | 1.0 | static dependency |
| G_call | conf | dynamic dependency |
| G_type | conf | contract coupling |
| G_cochange | lift | behavioral coupling |
| G_author | jaccard | social coupling |
| G_clone | 1−similarity | duplication coupling |
| G_semantic | cosine* | conceptual proximity (*opt-in embedder, Phase I) |

Findings-as-disagreements (the design corpus' best idea, formalized):

```
hidden_coupling : E_cochange \ E_import          (changes together, no structure)
dead_dependency : E_import \ E_cochange          (structure, no shared behavior)
conway_violation: E_import × ¬overlap(E_author)  (structure, separate owners)
semantic_twin*   : high cos ∧ low syntactic sim  (duplication invisible to NCD)
```

*Grounding*: disagreement between proximity spaces as anomaly source traces to
socio-technical congruence literature (Cataldo et al. 2006) and is the systematic engine
behind what competitors hand-code as rules. SARIF (2023) proved fusing heterogeneous
proximity sources beats any single source for structure recovery.

**Acceptance gates**: import resolution ≥ 98% precision on fixture corpus; phantom rate on
clean fixtures ≈ 0; ContractBundle asserts every layer's edge schema.

---

### PHASE C — MEASURE (L1-derived + L2 per-file primitives)

**Goal**: the per-file measurement vector. Each metric below states its formula and the
mathematical reason it is the right functional.

#### C.1 Information dimension

- **compression_ratio** r(x) = `len(zlib.compress(x)) / len(x)`.
  *Math*: zlib output length upper-bounds an approximation of Kolmogorov complexity K_U(x);
  low r ⇒ highly compressible ⇒ redundant/boilerplate; high r ⇒ dense/novel tokens.
  Known failure modes (researched 2024–2025): gzip's 32KB sliding window truncates large
  files; concatenation artifacts inflate similarity; raw-byte compression is blind to token
  structure. **Mitigations baked in**: compress *normalized token streams* (identifiers →
  placeholders, literals → type markers — NiCad-style blind renaming), segment-wise on
  function spans for large files, compressor swappable behind `Compressor` protocol.
- **NCD** (clone distance, Phase G consumer):
  `NCD(x,y) = (C(xy) − min(Cx,Cy)) / max(Cx,Cy)` (Cilibrasi–Vitányí 2005). Approximates
  normalized information distance; metric up to O(1) error; values < 0.3 = clone candidate.
  Significance testing added (permutation null within size buckets) because a bare point
  estimate is uncalibrated — P5.
- **token_entropy** H = −Σₖ pₖ log₂ pₖ over token-type distribution; normalized H/log₂ k.
  Diagnostic-only (v0.x lesson: AST-vocab entropy ≠ complexity).

#### C.2 Naming/concept dimension (semantics)

- **Roles**: 12-value enum (MODEL SERVICE UTILITY CONFIG TEST CLI INTERFACE EXCEPTION
  CONSTANT ENTRY_POINT MIGRATION UNKNOWN) via deterministic first-match decision tree
  (path rules first: TEST/MIGRATION). Expected accuracy ~80%; value is that *misclassification
  is itself a smell*. Roles gate orphan logic and test-pair whitelists downstream.
- **Concepts**: identifier splitting (snake/camel/acronym) → stopword removal → corpus IDF
  (two-pass) → within-file co-occurrence graph → Leiden clusters → ≤10 concepts.
  Files < 20 unique tokens: concepts = ∅, concept_count = 1, entropy = 0 (documented floor).
- **concept_entropy** H_concepts; > 1.5 = unfocused file.
- **naming_drift** = `1 − cos(tfidf(filename_tokens), tfidf(content_concepts))`;
  generic filenames (`utils`, `helpers`, `common`) forced to drift 0 (they carry no claim).
  *Math*: filename is a compressed human assertion about content; cosine distance in the
  TF-IDF space measures violation of that assertion. LING lexical-smell lineage
  (ISOMORPH/HOMOGRAPH) operationalized.

#### C.3 Cognitive load

`cognitive_load = concept_count_norm × complexity_norm × (1 + max_nesting/10)`,
percentile-normalized upstream of composites. Deliberately simple; the baseline-analysis
post-mortem showed exotic load proxies produced false positives. Complexity factor uses
the CC proxy from A.3.

#### C.4 Completeness signals

`phantom_import_count` (B.1), `broken_call_count` (gated), `todo_density`
(TODO/FIXME/HACK occurrences per KLOC), `docstring_coverage` (Python first).

**Grounding**: compression-as-complexity has empirical standing (Hindle/Godfrey/Holt line;
v0.x worked examples hand-verified: simple.go 0.21 vs complex.go 0.38). TF-IDF coherence
replaced import-TF-IDF coherence after BASELINE_ANALYSIS proved the latter measured
libraries, not responsibilities (false positives on demo files).

**Acceptance gates**: cross-language universality test (same logic in py/go/ts ⇒
compression ratios within ±0.03, identical token streams post-normalization); role
precision/recall table published for fixture corpus; golden masters updated.

---

### PHASE D — TEMPORAL SPINE (L3)

**Goal**: everything derivable from git, computed once per `file_id`, with honest labels.

#### D.1 Churn dynamics

Fixed 4-week windows over full history (configurable depth). For window series w₁..w_T:
- mean μ, std σ, **CV = σ / max(μ, ε)** (volatility operator).
- **slope** b via OLS: `b = Σ(t−t̄)(w−w̄) / Σ(t−t̄)²` (velocity operator).
- **Trajectory classifier** (canonical decision tree — one definition, everywhere):

```
DORMANT      total_changes ≤ 1
STABILIZING  slope < −0.1  ∧ CV < 0.5
SPIKING      slope > 0.1   ∧ CV > 0.5
CHURNING     CV > 0.5
STABLE       otherwise
```

*Why these thresholds*: CV = 0.5 separates coefficient-of-variation regimes where the
std is half the mean — below it, variation is dominated by work cadence; above it, by
instability. Slope gate ±0.1 changes/window is the smallest OLS-detectable trend given
window granularity. (Phase I adds BOCPD regime posteriors as an upgrade; the deterministic
tree remains the offline default — see I.1.)

#### D.2 Change entropy

`H_change = −Σⱼ pⱼ log₂ pⱼ` over pⱼ = fraction of changes landing in window j.
Near-uniform scatter (H → log₂ T) = shotgun-surgery profile; focused (H → 0) = hotspot.
Empirical grounding: co-change graph entropy correlates with defect count (r ≈ 0.54,
2025 study) and improves defect AUROC in ~82% of settings. Finder threshold:
HIGH_SCATTER iff `H_change > 0.8·log₂(T)`.

#### D.3 Intent mining

Keyword classes on commit subjects (+ optional diff-shape secondary):
fix = {fix, bug, patch, hotfix, resolve, repair}; refactor = {refactor, restructure,
reorganize, clean, simplify}. `fix_ratio`, `refactor_ratio` per file_id. Bulk commits
(> 50 files) excluded from co-change but counted for churn (documented asymmetry).

#### D.4 Co-change with lift

For pair (A,B) co-occurring in c_AB commits with marginals c_A, c_B over C commits:

```
P(A) = c_A/C   P(B) = c_B/C   P(A∧B) = c_AB/C
lift(A,B) = P(A∧B) / (P(A)·P(B))
confidence_{A→B} = c_AB / c_A        (directional)
pair_confidence = min(confidence_{A→B}, confidence_{B→A})
temporal_coupling = lift × pair_confidence
```

*Math*: lift is the association ratio; lift > 1 means positive dependence; lift = PMI
exponentiated. Threshold lift ≥ 2.0 ∧ pair_confidence ≥ 0.5 for candidate hidden coupling
(restored from v2 spec; v3 dropped the confidence term and thereby admitted noise pairs).
Squash-merge awareness: probable squashes detected (mega-overlap vs previous tip,
"Merge pull request" subjects) and down-weighted pending PR connectors (W7).

#### D.5 SZZ ground-truth suite (the self-validation unlock)

Implement B-SZZ → AG-SZZ admissible-line filtering → RA-SZZ relevancy filter, plus:
ghost-commit flagging (~17% of fixes have unreachable inducers — Lyu et al. TSE 2024),
and refactoring-aware label hygiene (RefactoringMiner-class detection where available;
CAT/ISSRE-2025 showed refactoring tangles bias labels up to 37% F1 degradation if ignored).
Output: `bug_inducing_commit_ids` as facts. This converts every finder from a heuristic
into a *measurable instrument* (retrospective precision per finder per repo — nobody ships
this; see Part VII Eval).

#### D.6 Authorship

Per file_id: author share vector p_a over owned lines (recency-weighted, LOCC-style).
- **author_entropy** H_auth = −Σ p_a log₂ p_a.
- **bus_factor = 2^{H_auth}** — the perplexity/effective-number-of-equal-authors
  (Hill number q=1). *Math*: exponentiated entropy is the unique additive measure whose
  value equals the support size under uniformity; commit-count truck factors are provably
  loose heuristics (bus-factor estimation is NP-hard; Piccolo 2025 peeling heuristics beat
  degree counting). W3 upgrade: bipartite-peeling TRUCK_FACTOR.
- knowledge_gini per module; coordination_cost = mean distinct authors per commit;
  module_bus_factor = min bus_factor over top-quartile-PageRank files.

**Reuse**: current `temporal/` extractor (~85%, fix trajectory fallback bug + %s subject),
churn module with corrected thresholds.

**Acceptance gates**: trajectory determinism across runs; uniform/focused/bimodal change
entropy unit pins (bounds [0, log₂T]); SZZ smoke test on a repo with known `Fixes:` tags;
squash synthetic repo handled.

---

### PHASE E — GRAPH ALGORITHMS (L5)

All implemented in-house on sparse CSR matrices (numpy/scipy become core deps — they are
already transitive today); optional `[accel]` extra enables the backend ladder
(graph-tool > igraph > scipy > pure-python) proven in trial-run-v1 benchmarks
(100 files: 45s → 1.1s).

#### E.1 PageRank

```
PR(v) = (1−d)/N + d·[ Σ_{u→v} PR(u)/out(u) + dangling_mass/N ]     d = 0.85
```
Power iteration to L1 tolerance 1e-6, ≤ 20 iters. *Convergence bound*: error after k
iterations ≤ d^k (Google matrix contracts by d; 0.85²⁰ ≈ 3.9%). Dangling mass
redistributed uniformly (else rank leaks on DAG-ish graphs — import graphs are near-DAG).
Computed per weakly-connected component then renormalized.

#### E.2 Betweenness — Brandes 2001, O(V·E)

Accumulator formulation with predecessor stacks; normalized by 1/((n−1)(n−2)).
Sampling (≥ 256 pivot sources, error-bounded approximation) above 5k nodes.

#### E.3 SCC + cycle diagnosis

Iterative Tarjan (explicit stack — recursion depth killed v1 on deep graphs).
**Beyond membership** (the SOTA upgrade): per non-trivial SCC compute candidate
break-edges ranked by inverse temporal_coupling ("breaking A→B costs little behaviorally:
they haven't co-changed in 8 months"), rank cycles by size × churn × coupling. Minimum
feedback arc set approximated greedily — exact is NP-hard, greedy suffices for diagnosis.

#### E.4 Communities — Leiden (upgrade from Louvain)

Local-move on modularity ΔQ:
```
ΔQ(i→C) = [ (Σ_in + k_{i,in})/(2m) − ((Σ_tot + k_i)/(2m))² ]
        − [  Σ_in/(2m)        − (Σ_tot/(2m))²   − (k_i/(2m))² ]
```
then **Leiden refinement** (ensure well-connected communities via sub-eigraph partitioning;
guarantees non-degenerate partitions and fixes Louvain's internally-disconnected-community
defect). Determinism: sorted node iteration + fixed tie-breaks; consensus stability across
runs reported (run 3× at FULL tier on small graphs, Jaccard of partitions = stability
signal). *Why Leiden*: Louvain's resolution limit (Fortunato–Barthélemy 2007) misses
communities smaller than scale ξ; Leiden's refinement mitigates the worst cases and its
connectedness guarantee matters because we contract modules on these partitions later.

#### E.5 Spectral

Laplacian L = D − A (symmetric, largest component). Lanczos (scipy `eigsh`) for k lowest
eigenpairs, k = min(10, |V|−1); skip graphs < 3 nodes.
- **fiedler_value = λ₂** (algebraic connectivity; Cheeger: h(G)²/2 ≤ λ₂ ≤ 2h(G) — λ₂
  certifies bottleneck width; near-zero ⇒ nearly disconnected architecture).
- **spectral_gap = λ₃ − λ₂** (FINAL definition; large gap ⇒ clean bipartite-ish community
  separation; λ₂/λ₃ ratio rejected — conflates two distinct quantities).
- Fiedler vector sign-split = spectral bipartition, cross-checked against Leiden
  (disagreement = boundary ambiguity signal).

#### E.6 Robustness kit (new, cheap, high-leverage)

- **k-core decomposition** (peeling) → `core_number` per file.
- **Articulation points** (Tarjan low-link) → bridges whose removal disconnects modules.
- **blast_radius(v)** = |descendants(v)| via reverse reachability closure (per-component BFS).
- **depth** = shortest-path hops from nearest entry point (entry = role ENTRY_POINT /
  in_degree-0 roots), −1 unreachable; orphans = `in_degree = 0 ∧ role ∉ {ENTRY_POINT,
  TEST}` (role-gated — the NO_TEST_FILE lesson).

#### E.7 Global topology

modularity Q of Leiden partition; centrality_gini over PageRank (> 0.7 hub dominance);
orphan_ratio, phantom_ratio, glue_deficit = 1 − internal-node ratio.

**Acceptance gates**: algorithm parity suite against networkx on fixtures (PageRank L1
diff < 1e-9, identical SCC/partitions mod rotation); determinism (byte-identical JSON
across runs); perf budgets (Part V).

---

### PHASE F — CROSS-LAYER FUSION (L6/L7)

#### F.1 Normalization tiers (statistics honesty)

Software metrics are power-law/lognormally distributed (defect counts Pareto α≈2–3;
complexity/churn/size lognormal — Nagappan & Ball line). z-scores on such data are
meaningless; percentiles are robust. Tiers:

| Tier | n files | Method |
|------|---------|--------|
| ABSOLUTE | < 15 | Registry absolute thresholds; no percentiles, no composites |
| BAYESIAN | 15–50 | Beta-posterior smoothed percentile `(α + r)/(α + β + n)` (flat α=β=1 initially; informative priors after calibration corpora exist) |
| FULL | ≥ 50 | Inclusive percentile `#{v ≤ x}/n`; zero-variance → 0.5 |

Non-percentileable set declared in registry (enums, bools, composites, singletons).

#### F.2 The two-risk duality (resolves the raw_risk war)

Two different questions demand two different functionals:

**raw_risk** — a smooth scalar field for the Laplacian (needs continuity; percentiles are
near-uniform ⇒ discrete Laplacian ≡ 0, a degenerate field):

```
raw_risk(f) = 0.25·minmax(pagerank) + 0.20·minmax(blast_radius_size)
            + 0.20·minmax(cognitive_load) + 0.20·min(churn_cv/2, 1)
            + 0.15·max(0, 1 − bus_factor/5)
```
Continuous instability term `min(cv/2,1)` (saturates at cv = 2). Missing inputs →
drop-and-renormalize weights. Dormant files: churn term contributes 0 (undefined), others stand.

**risk_score** — a ranking composite for attention ordering (contrast is good):

```
risk_score(f) = 0.25·pctl(pagerank) + 0.20·pctl(blast) + 0.20·pctl(cognitive_load)
              + 0.20·instability_factor + 0.15·max(0, 1 − min(bus_factor,5)/5)
instability_factor = 1.0 if trajectory ∈ {CHURNING, SPIKING} else 0.3
```

The binary-vs-continuous "contradiction" in prior specs was two answers to two questions;
now it is documented as intentional.

#### F.3 Health Laplacian

Neighbor set N(f) = adjacency of `G_import ∪ G_cochange` (union graph, undirected view):

```
Δh(f) = raw_risk(f) − mean_{g∈N(f)} raw_risk(g)        (orphans: Δh = 0)
```
Δh > 0.4 ⇒ WEAK_LINK candidate (file worse than its neighborhood); strongly negative ⇒
hidden strength (protective hub — surfaced in explain mode, not as a finding).

#### F.4 Composites (final formulas, one each)

```
wiring_quality(f) = 1 − (0.30·orphan + 0.25·stub_ratio + 0.25·phantom_file_ratio
                         + 0.20·broken_call_ratio)          # drop-renormalize w/o CALL edges
file_health(f)    = 1 + 9·(1 − (0.25·risk_score + 0.20·(1−wiring_quality)
                     + 0.20·pctl(cognitive_load) + 0.15·orphan_flag
                     + 0.20·(1−neighborhood_coherence)))    # displayed as 1–10, HALF_UP
wiring_score(G)   = 1 − (0.25·orphan_ratio + 0.25·phantom_ratio + 0.20·glue_deficit
                         + 0.15·mean_stub_ratio + 0.15·clone_ratio)
architecture_health(G) = 0.30·(1−violation_rate) + 0.20·mean(cohesion)
                     + 0.20·(1−norm(coupling)) + 0.15·mean(1−main_seq_distance)
                     + 0.15·mean(boundary_alignment)
codebase_health(G) = 1 + 9·(0.30·architecture_health + 0.30·wiring_score
                     + 0.20·team_factor + 0.20·norm(modularity))
# finding_density deliberately EXCLUDED (circularity: it fed on its own outputs)
```

Module Martin metrics (guards binding): cohesion = internal_directed_edges / k(k−1)
(None if k<2); instability = Ce/(Ca+Ce) (**None if Ca+Ce = 0** — every consumer must
None-guard; the missing guard crashed five call sites historically); abstractness =
abstract types/total types; main_seq_distance = |A + I − 1|.

#### F.5 Cross-layer mutual information (NMI)

For layers U,V: classify each unordered vertex pair into {in both, U-only, V-only, neither}
→ contingency table → `NMI(U,V) = 2·I(U;V)/(H(U)+H(V))`.

```
behavioral_coherence = NMI(G_import, G_cochange)   # structure predicts behavior?
conway_alignment     = NMI(G_import, G_author)     # org mirrors architecture?
semantic_alignment   = NMI(G_import, G_semantic)   # concepts mirror dependencies? (I-tier)
topology_stability   = 1/(1 + graph_velocity),  graph_velocity = |ΔE|/|E∪E'| per snapshot
```
Interpretation table shipped with each (high/medium/low readings), citing the STMC null
result (TSE 2021: congruence↔bugs link failed replication in 25 OSS projects) so claims
stay calibrated.

**Acceptance gates**: tier selection correct at 14/15/51 files; Laplacian nonzero on
fixture with known weak-link (hand-verifiable); composites reproduce golden values;
correlation redundancy check (|ρ|>0.8 halves subordinate weight) exercised in tests.

---

### PHASE G — PATTERNS (L8)

#### G.1 Declarative PatternSpec

```python
PatternSpec(
  id="HIDDEN_COUPLING", scope=FILE_PAIR, base_severity=0.90,
  requires=["cochange.lift", "cochange.pair_confidence", "graph.layers"],
  conditions=[
    Gate("lift >= 2.0"),
    Gate("pair_confidence >= 0.5"),
    Not(AnyEdge("import", both_directions=True)),
    Not(ExpectedPair()),          # whitelist: test↔src basename, __init__, same-module
  ],
  hotspot=True, tier_minimum=FULL, effort=MEDIUM)
```

Compiled at startup; executed by the pattern executor; evidence auto-generated from
condition margins (which condition fired how hard). Motif compiler: graph anti-pattern
catalogue (hub-like, cyclic-with-exit, god-module, unstable-interface) declared as node/edge
constraint patterns — ARC/HUSACCT vocabularies as data.

#### G.2 Canonical catalog — 28 finders

Categories: Structural 7 · Coupling/Duplication 6 · Architecture 6 · Team 4 · Intent 2 · Meta 3.
Severities are **rank separators, calibration pending** (Eval harness owns promotion to
probabilities).

| # | ID | Scope | Sev | Condition (canonical) | Hotspot |
|---|----|-------|-----|----------------------|---------|
| 1 | HIGH_RISK_HUB | FILE | 1.00 | pctl(PR)>0.90 ∧ pctl(blast)>0.90 ∧ (pctl(cog)>0.90 ∨ traj∈{CHURN,SPIKE}) | ✓ |
| 2 | GOD_FILE | FILE | 0.80 | pctl(cog_load)>0.90 ∧ semantic_coherence<0.20 | |
| 3 | UNSTABLE_FILE | FILE | 0.70 | traj∈{CHURNING,SPIKING} ∧ changes>median(non-test) | ✓ |
| 4 | THRASHING_CODE | FILE | 0.66 | traj=SPIKING ∧ churn_cv>1.0 | ✓ |
| 5 | ORPHAN_CODE | FILE | 0.55 | is_orphan ∧ role∉{ENTRY_POINT,TEST} | exempt |
| 6 | PHANTOM_IMPORTS | FILE | 0.65 | phantom_import_count>0 | exempt |
| 7 | HOLLOW_CODE | FILE | 0.71 | stub_ratio>0.5 ∧ impl_gini>0.6 | exempt |
| 8 | HIDDEN_COUPLING | PAIR | 0.90 | lift≥2.0 ∧ conf≥0.5 ∧ no import edge ∧ ¬expected | |
| 9 | DEAD_DEPENDENCY | PAIR | 0.40 | import edge ∧ cochange=0 ∧ both ≥50 commits | |
| 10 | ACCIDENTAL_COUPLING | PAIR | 0.50 | import edge ∧ concept_jaccard<0.2 ∧ different communities | |
| 11 | COPY_PASTE_CLONE | PAIR | 0.50 | NCD<0.3 (function-unit post-W4) | exempt |
| 12 | DUPLICATE_INCOMPLETE | PAIR | 0.68 | clone pair ∧ mean(stub_ratio)≥0.3 | exempt |
| 13 | INCOMPLETE_IMPLEMENTATION | FILE | 0.72 | stub_count≥2 ∧ phantom_import_count≥1 | |
| 14 | BOUNDARY_MISMATCH | MODULE | 0.60 | boundary_alignment<0.7 ∧ files≥3 | |
| 15 | LAYER_VIOLATION | MOD_PAIR | 0.52 | BACKWARD/SKIP edge vs inferred∨declared layers | |
| 16 | ZONE_OF_PAIN | MODULE | 0.60 | abstractness<0.3 ∧ instability<0.3 (instability≠None) | |
| 17 | ARCHITECTURE_EROSION | CODEBASE | 0.65 | violation_rate strictly increasing ≥3 snapshots | |
| 18 | FLAT_ARCHITECTURE | CODEBASE | 0.60 | max(depth)≤1 ∧ glue_deficit>0.5 ∧ files≥10 | exempt |
| 19 | DIRECTORY_HOTSPOT | MODULE | 0.70 | ≥60% files in top risk quartile ∧ files≥3 | |
| 20 | KNOWLEDGE_SILO | FILE | 0.70 | bus_factor≤1.5 ∧ pctl(PR)>0.75 | ✓ |
| 21 | REVIEW_BLINDSPOT | FILE | 0.80 | pctl(PR)>0.75 ∧ bus_factor≤1.5 ∧ no test twin | ✓ |
| 22 | TRUCK_FACTOR | FILE | 0.85 | bus_factor≤1.0 ∧ PR top-quartile | ✓ |
| 23 | CONWAY_VIOLATION | MOD_PAIR | 0.55 | author_jaccard<0.3 ∧ structural_coupling>0.3 | |
| 24 | BUG_MAGNET | FILE | 0.70 | fix_ratio>0.4 ∧ total_changes≥5 | ✓ |
| 25 | BUG_ATTRACTOR | FILE | 0.75 | fix_ratio>0.4 ∧ pctl(PR)>0.75 | ✓ |
| 26 | WEAK_LINK | FILE | 0.75 | Δh>0.4 | ✓ |
| 27 | NAMING_DRIFT | FILE | 0.45 | naming_drift>0.7 ∧ ¬generic_filename | exempt |
| 28 | CHRONIC_PROBLEM | meta | ×1.25 cap 1.0 | same stable id persists ≥3 snapshots | |

ABSOLUTE-tier firing set (absolute-threshold fallbacks defined in registry): #5,6,7,9,11,12,
13,18,27,16 → **10 finders** (resolves the historical 8-vs-10 discrepancy by declaration).

#### G.3 Scoring model

Condition margin (polarity-aware): for threshold τ on signal s,
high-is-bad: `m = clamp((v−τ)/(1−τ), 0, 1)`; low-is-bad: `m = clamp((τ−v)/τ, 0, 1)`;
boolean gates contribute 1.0. Then:

```
confidence = mean(margins)
severity   = base_severity × clamp(mean_margins, 0.5, 1.0)
rank_key   = 0.7·severity + 0.3·confidence      (ties: scope breadth → evidence count → id)
```

Stable finding identity: `sha256(pattern_id ‖ sorted(entity_ids))[:16]` — lifecycle
(new/persisting/resolved/regression) tracked across snapshots; debt_velocity =
|new| − |resolved|. Grouping: same-type FILE findings grouped ≤ 3 per group.
Focus point (delivery): `actionability = risk × impact × tractability × confidence`
with impact=(pctl(PR)+min(blast/50,1))/2, tractability penalties (orphan ×0.5,
>1000 LOC ×0.8), confidence ×0.7 without git.

**Acceptance gates**: per-finder fire/no-fire fixtures (both directions); self-analysis
produces 5–20 findings; zero crashes on empty/single-file/no-git/<2-modules corpora.

---

### PHASE H — PERSIST & TIME MACHINE

ShannonDB (SQLite, WAL). Schema v4 sketch:

```sql
blobs(sha256 PK, size, lang)
parsed_syntax(sha256 PK, json, parser_version)             -- content-keyed cache
file_identities(file_id PK, created_at, deleted_at)
file_paths(file_id FK, path, valid_from_snapshot, valid_to_snapshot)
renames(old_path,new_path,method,confidence,commit)
authors(canonical_id PK, aliases_json, is_bot)
commits(sha PK, ts, author_fk, subject, intent_class)
file_changes(commit_fk, file_id FK, add, del)
bug_inducers(fix_commit_fk, inducer_commit_fk, method, confidence)   -- SZZ facts
snapshots(id PK, ts, commit, config_hash, tier)
signal_history(snapshot_fk, entity_key, signal, value, pctl)
findings(snapshot_fk, identity_key, pattern_id, severity, confidence,
         status new|persisting|resolved|regression, evidence_json)
nl_facts(file_id FK, kind comment|docstring|readme, span, text_hash)
```

Diff engine consumes snapshots → SignalDelta/FindingDelta/debt_velocity/regressions.
**Kind-3 reconstruction becomes tractable**: historical re-analysis reuses parsed_syntax by
content hash — only genuinely-new blobs get parsed. Queries: time series per entity×signal,
finding history, chronic sets. Export extras: Parquet/DuckDB (absorbing the hybrid
event-log experiment's SQL-finder idea: `patterns/*.sql` over wide tables as an optional
query surface).

---

### PHASE I — INTELLIGENCE TIER (all optional, `--offline` safe)

1. **BOCPD regime upgrade**: Adams–MacKay Bayesian online changepoint over weekly churn
   (Normal conjugate, hazard ≈ 1/250); outputs P(changepoint) + regime posterior per file.
   Alert thresholds tied to an explicit alert budget (Youssef 2025 SRE-style calibration:
   missed-vs-false-alarm cost ratio → probability threshold; Brier score reported).
   Deterministic tree stays default until BOCPD passes eval parity.
2. **Embedder protocol** (`none | onnx-local | voyage/openai`): local ONNX default model
   class 33–137M params (CodeRankEmbed-class), int8/binary quantized vectors cached in
   ShannonDB keyed by sha256. Unlocks: G_semantic layer, semantic twins (quadrant model —
   high-cosine ∧ high-NCD = renamed logic; low-NCD ∧ high-cosine = Type-4 candidate;
   divergence quadrants are the differentiated artifact), DocDrift (docstring-vs-body
   cosine), concept-drift trajectories (module centroid displacement across snapshots).
3. **LLM adapters** (cloud or Ollama endpoint): adjudication of ambiguous findings
   (rubric-judge: CONFIRMED/REFUTED/UNVERIFIABLE + cited evidence; judge may never raise
   severity without new evidence); adversarial verify (isolated advocate/skeptic sessions —
   naive verifier chains collapse into sycophancy per CCV 2026); remediation simulation
   (cut proposed edges → recompute modularity/coupling → predicted deltas in the suggestion);
   KNighter-style synthesis: confirmed findings → mined checker candidates → deterministic
   PatternSpecs (ML on the training side, never the runtime side).
4. **Context supplier**: `repo-map` emitter (tree-sitter symbols × PageRank × token budget —
   aider-proven recipe; we already own the ranking inputs) and context packs
   (`pack --for file --budget 4k`); MCP server exposing signals/findings/graph to coding
   agents. Distribution win at near-zero ML risk.
5. **PR connectors** (GitHub/GitLab): true changeset reconstruction under squashes, issue↔commit
   link recovery (regex → time-proximity → dense-retrieval + classical reranker; LinkRank
   one-to-many awareness), review-latency/depth metrics feeding REVIEW_BLINDSPOT with real data.

**Grounding**: Tencent FP study (hybrid LLM refinement removes 94–98% of static-analysis
FPs at $0.001–0.12/alarm); BugLens precision 0.10→0.72 via structured reasoning; CodeRabbit
field rejection 56.3% ⇒ adjudication must be evidence-chained, not generative.

---

### PHASE J — DELIVERY + EVAL HARNESS

Delivery surfaces (parity of insight quality across channels): CLI (verdict → focus point →
also-consider → patterns; `check` Tier-1 <5s), server dashboard (existing React SPA ported
to new API), CI gate (`--fail-on`; FAIL iff display_health < 4.0 ∨ severity ≥ 0.9;
SARIF export; GitHub annotations), HTML report, IDE gutter path (W7), MCP.

**Eval harness (a product, not a test dir)**:
- Golden-master corpus + manifests; hypothesis property tests (incremental == full;
  percentile monotonicity; entropy bounds).
- Injected-fault repos (introduce cycle / split cohesive module / plant god file / clone
  families) → per-finder detection @ fixed budget = regression tests for thresholds.
- Labeled corpora: ApacheJIT adapter; repos with `Fixes:` tags; TechDebt dataset for
  composite calibration. Acceptance: composite AUC > 0.70, per-finder precision > 0.50
  before any severity claim is labeled "calibrated"; isotonic mapping score→P(real issue).
- FP telemetry: `shannon-insight feedback dismiss|confirm <finding-id>` persisted;
  per-finder empirical precision published in `health --json`; chronic low-yield patterns
  auto-suppressed per repo.
- Real-world validation protocol (trial-run-v1 style): requests/flask/django runs with
  recorded findings + timing, kept green in CI.

---

## PART III — CANONICAL REGISTRIES

### III.1 Dimensions (8) × scales (7)

Dimensions: SIZE SHAPE NAMING REFERENCE INFORMATION CHANGE AUTHORSHIP INTENT.
Scales: TOKEN STATEMENT FUNCTION CLASS FILE MODULE CODEBASE (FILE primary).
Aggregation operators: sum mean max min gini entropy. Derived dimensions (first-order):
Complexity Coupling Cohesion Density Volatility Ownership Purposefulness; (second-order):
Risk KnowledgeRisk Debt Staleness Drift Erosion Fragility WiringQuality.
Every PatternSpec must decompose into conditions on derived dimensions (enforced by lint).

### III.2 Signal registry (primary, numbered)

76 primary signals (legacy bookkeeping bug — "+18 yet still 62" — resolved: operator
derivatives are views `sig@delta|velocity|acceleration|volatility|trend|trajectory`,
not registrations):

- **F01–F45 per-file** (45): lines, function_count, class_count, max_nesting, impl_gini,
  stub_ratio, import_count | role, concept_count, concept_entropy, naming_drift,
  todo_density, docstring_coverage | pagerank, betweenness, in_degree, out_degree,
  blast_radius_size, depth, is_orphan, phantom_import_count, broken_call_count, community,
  compression_ratio, semantic_coherence, cognitive_load, core_number | total_changes,
  churn_trajectory, churn_slope, churn_cv, bus_factor, author_entropy, fix_ratio,
  refactor_ratio, change_entropy | hidden_coupling_count, dead_import_count,
  conway_violation_count, neighborhood_coherence | raw_risk, delta_h, risk_score,
  wiring_quality, file_health.
- **M01–M15 per-module** (15): cohesion, coupling, instability, abstractness,
  main_seq_distance, boundary_alignment, layer_violation_count, role_consistency, velocity,
  coordination_cost, knowledge_gini, module_bus_factor, mean_cognitive_load, file_count,
  module_health.
- **G01–G16 global** (16): modularity, fiedler_value, spectral_gap, cycle_count,
  centrality_gini, orphan_ratio, phantom_ratio, glue_deficit, wiring_score,
  architecture_health, codebase_health, behavioral_coherence, conway_alignment,
  semantic_alignment, topology_stability, violation_rate.

Each registration carries: `{dimension, scale, polarity(HIGH_IS_BAD|GOOD|NEUTRAL),
percentileable, tier_min, producer_node, absolute_threshold?, formula_ref}`.

### III.3 Temporal operators (universal)

delta · velocity(OLS slope) · acceleration · volatility(CV) · trend(rolling-3,
polarity-aware) · trajectory(canonical tree). Applicability matrix: numeric+composites →
all six; ratios[0,1] → no volatility; enums/bools → delta only. Seasonality/stationarity
backlogged (needs ≥20 points).

---

## PART IV — RESOLVED CONTRADICTIONS LEDGER

| # | Topic | Conflicting versions | V4 DECISION |
|---|-------|----------------------|-------------|
| 1 | Finder count | 22 (v2 registry) vs 28 (v3/code/README) vs 38 (v3-reactive) | **28 canonical catalog** (III/G.2); extras from reactive tree are candidates, not members |
| 2 | spectral_gap | λ₂/λ₃ (v2) vs λ₃−λ₂ (v3, MATH-DAG) | **λ₃ − λ₂**; fiedler_value = λ₂ separately named |
| 3 | raw_risk instability | binary factor vs continuous min(cv/2,1) | **Both, intentional**: continuous in raw_risk (Laplacian smoothness), binary factor in risk_score (ranking contrast) |
| 4 | wiring_quality | 3-term (v3) vs 4-term w/ broken_calls (v2) | **4-term with drop-renormalize** when CALL edges absent |
| 5 | Hidden coupling | confidence gate dropped in v3 | **Restored** conf ≥ 0.5 + ExpectedPair whitelist |
| 6 | Finding model | scopes dropped, lifecycle dropped (v3) | **Superset**: FILE/FILE_PAIR/MODULE/MODULE_PAIR/CODEBASE + effort + lifecycle + evidence chains + sha256[:16] key + `probability` (null until calibrated) |
| 7 | Trajectory CV boundary | 0.5 vs 1.0 across docs | **Canonical tree @ 0.5** (D.1); churn_cv>1.0 survives only as THRASHING_CODE gate |
| 8 | Cohesion denominator | n(n−1) vs m(m−1)/2 | **Directed: k(k−1)**; k<2 → None |
| 9 | Graph taxonomy | 6 distance-spaces vs 5 graphs | **7 named layers** incl. G_clone; G_semantic optional |
| 10 | Identity | path-keyed (v2) vs UUID (v3) | **UUID file_id + rename events mandatory at L0** |
| 11 | Storage | TensorSnapshot JSON vs 3 DBs vs Parquet events | **Single ShannonDB**; Parquet/DuckDB = export/query extra |
| 12 | Signal bookkeeping | "+18 yet 62" | **76 primary**; operators are views |
| 13 | MATH-DAG divergent finders/thresholds | parallel universe spec | Archived; registry wins |
| 14 | Percentile inclusivity | ≤ vs < | **Inclusive ≤**; zero-variance → 0.5 |
| 15 | Orchestration | mutable blackboard vs forward-only stages vs RxPython reactive | **Forward-only typed stages**; Slot[T] provenance inside executor; **reactive rejected** (evidence: 24 failing tests, 20% cov) |
| 16 | team_risk | weighted composite vs display-only | **Display-only derived** (unnumbered) |
| 17 | Regex scanner fallback | mandatory (shannon-v2) vs delete (v2 phases) | **Deleted**; tree-sitter required `[parsing]` extra, hard error without it |
| 18 | Python floor | 3.9 vs 3.12 | **3.11+** (3.12 target) |

---

## PART V — EXECUTION ARCHITECTURE

- **Kernel**: startup compiles registries → ContractBundle validation (single-writer slots,
  requirement satisfiability, polarity sanity) → TopologicalSorter execution plan.
  Parallel: structural ∥ temporal spines; process pool for L1 parse fan-out; thread pool IO.
- **Modes**: `check` (Tier-1 subgraph, <5s small repos) · `analyze` (default full) ·
  `--focus <domain>` (transitive pruning; ai-quality focus skips IR4/temporal ≈40% saving) ·
  `--changed/--since` (scope) · incremental by content hash (skip unchanged through L1–L2;
  delta-update L3–L8).
- **Degradation matrix** (each row tested):

| Condition | Behavior |
|-----------|----------|
| no git | skip L3; temporal finders skipped; structural intact |
| no tree-sitter | hard error with install hint |
| n < 15 | ABSOLUTE tier; 10 finders fire; no composites |
| < 2 modules | architecture=None; arch finders skip |
| single-author repo | G_author-dependent finders skip |
| empty/single-line files | defined floors (lines=0 ok, cognitive_load=0) |
| disconnected graph | per-component algorithms; Δh orphan=0 |
| instability undefined | None-guard everywhere; ZONE_OF_PAIN skips |

- **Error taxonomy**: ShannonError{message, code SC1xx–SC9xx, recoverable, recovery_hint};
  per-item isolation (one bad file never kills the run — ERR-02 pattern); exit codes
  0/1/130/2 preserved.
- **Performance budgets**: cold 1k files < 30s; 10k files < 60s; `--changed` <100 files < 10s
  warm; memory < 1GB @ 10k files; algorithms ≤ 15% of wall (sparse CSR + optional accel
  ladder).
- **Config**: `shannon-insight.toml` sections `[files] [git] [insights] [history]
  [performance] [architecture] [intel] [eval]` — precedence CLI > env(SHANNON_) > TOML >
  defaults; unknown keys = warning (not silent). Declared architecture example:

```toml
[architecture.rules]
layers = ["cli", "server", "services", "models", "core"]
allow_skip_layers = false
forbid = [{ from = "models", to = "services" }]   # turns LAYER_VIOLATION deterministic
```

---

## PART VI — REPO TOPOLOGY & MIGRATION MAPPING

```
src/shannon_insight/
  core/       ← insights/kernel.py (rewritten), infrastructure/Slot,exceptions,runtime
  registry/   ← infrastructure/signals + docs/v2/registry/* (compiled)
  facts/      ← facts/, extract/, scanning/file discovery, populate/*
  syntax/     ← scanning/tree-sitter modules, grammar_installer
  semantics/  ← semantics/ (as-is)
  temporal/   ← temporal/ (fixed), + szz.py, + bocpd.py (I.1)
  graphs/     ← graph/ + algorithms/ merged; + motifs.py, + layers.py
  signals/    ← signals/ rewritten around SignalField; fusion typestate builder
  patterns/   ← insights/finders/* → declarative specs; registry.py; ranking.py
  persist/    ← persistence/ + storage/ merged; schema v4
  intel/      ← NEW: embedders.py llm.py repomap.py packs.py mcp_server.py connectors/
  delivery/   ← cli/ server/ visualization/ exports
  eval/       ← NEW: goldens/ injected/ corpora/ telemetry
```

Reused assets: main-repo scanners/git-extractor/algorithms/dashboard/CLI shell;
trial-run-v1 ContractBundle concept, accelerated backend ladder, fixture corpus + goldens,
real-world validation reports; v3-reactive import resolver (progressive stripping),
diagnostics module, output formatting conventions; hybrid-experiment SQL-finders idea
(optional DuckDB surface). Deleted: AnalysisStore blackboard, dual stores + `_sync_entities`,
regex scanners, TensorSnapshot JSON dumps, all superseding docs (archived under
`docs/archive/pre-v4/`).

---

## PART VII — ROADMAP (waves map onto phases)

| Wave | Phases | Ships | Exit criteria |
|------|--------|-------|---------------|
| W1 Foundation | A,B,C | facts+identity+syntax+imports+per-file measures; ContractBundle; goldens | gates of A/B/C green; self-analysis sane; 62→76 signals registered |
| W2 Correctness | D,E | temporal spine+SZZ; Leiden+spectral+k-core+cycle diagnosis; declared-architecture compliance | SZZ smoke pass; parity vs networkx; determinism byte-identical |
| W3 Fusion+Patterns | F,G | tiers, composites, Laplacian, 28 patterns, lifecycle | F/G gates; injected-fault detection table v1 |
| W4 Time machine | H | ShannonDB, diff/lifecycle, Kind-3 fast path | 3-snapshot history e2e; regression detection works |
| W5 Function-level | B.2(CALL)+G clones | symbol spans, CALL edges, function-unit clone bands | call_edges>0 on fixtures; BigCloneEval-style band report |
| W6 Intelligence | I | BOCPD, embedder quadrant model, adjudication, repo-map/MCP, PR connectors | offline-contract test; adjudication precision ≥ deterministic baseline |
| W7 Delivery | J | PR review surface, forecast widget, IDE gutter, calibration release | AUC>0.70 composite; per-finder precision>0.50 labeled; FP telemetry live |

Sequencing principle: **identity → edges → measures → time → algorithms → fusion →
patterns → memory → intelligence → delivery**. Nothing in wave N+1 may depend on an
uncalibrated artifact of wave N (P5).

---

## APPENDIX C — KEY EXTERNAL GROUNDING (selected)

Graph: Fortunato–Barthélemy 2007 (resolution limit) · Leiden (Traag et al.) · Brandes 2001 ·
Cheeger inequality · k-core (Kitsak et al.) · SARIF 2023 (multi-source architecture
recovery) · HUSACCT (compliance rule vocabulary) · PairSmell ICSE 2025 (63% FP economics of
smell detection) · SmellBench 2026.
Information/clones: Cilibrasi–Vitányí 2005 (NCD) · Benavides 2025 (gzip pathology fixes) ·
BigCloneBench/Eval (band methodology) · Auto-SPT 2025 (transform robustness) · CoIR 2025 /
MTEB (embedding evaluation) · CodeRankEmbed/nomic-embed-code (local retrievers).
Temporal/process: Nagappan & Ball 2005 · Hassan 2009 (change entropy) · Kamei et al. 2013
(JIT, effort-aware) · SZZ lineage + Lyu TSE 2024 (ghost commits) · CAT ISSRE 2025
(refactoring label hygiene) · Piccolo 2025 (NP-hard bus factor, peeling) · Cataldo 2006 +
STMC TSE 2021 (congruence evidence/null) · SofiaWL 2023 (review routing spreads knowledge) ·
CLSA 2026 (line lifespan; identity dominance) · Adams–MacKay 2007 + Youssef 2025 (BOCPD,
alert budgets) · Constantinou & Mens 2017 (attrition hazards).
AI: aider repo-map · Greptile/TREX · CCV 2026 (sycophancy/isolation) · KNighter (checker
synthesis) · Tencent FP study arXiv:2601.18844 · BugLens · CodeRabbit field study
(arXiv:2607.03316, 56.3% rejection) · SWE-rebench (contamination discipline).

*Full source list lives with the research agents' reports (session records, 2026-08-23).*

— END OF SPEC —
