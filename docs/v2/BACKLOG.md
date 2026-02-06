# Feature Backlog

Features deferred from the v2 core spec. Each has been evaluated and intentionally postponed — not forgotten. Revisit when the core pipeline (Phases 0-7) is complete and validated on real codebases.

---

## B1: CP/Tucker Tensor Decomposition

**What**: Arrange all signals (d dimensions) for all files (n entities) across all time points (t snapshots) into a 3D tensor T(n,d,t). Factorize via CP decomposition to find "evolution archetypes" — groups of files that change the same signals the same way over time.

**Why deferred**: Requires Kind 3 temporal data (B2). Academic technique with no proven track record on source code analysis. Needs tensorly dependency. Minimum ~20 time points to produce meaningful factorizations.

**Prerequisite**: B2 (Kind 3 temporal), Phase 7 (persistence with signal history).

**Revisit when**: 10+ real projects have 20+ saved snapshots each, and there's a concrete question that cross-signal temporal patterns would answer.

**Estimated effort**: 2-3 weeks research + implementation.

---

## B2: Kind 3 Temporal Reconstruction

**What**: Re-run the full analysis pipeline at historical commits. `git show <sha>:<path>` to reconstruct every file at a past commit, then parse, build graph, compute signals. Fills the entire temporal tensor retroactively.

**Why deferred**: Expensive. For 500 files × 50 commits = 25,000 file parses + 50 graph constructions + 50 signal fusion runs. Minutes of computation for marginal insight beyond what `git log` (Kind 1) and cross-snapshot comparison (Kind 2) already provide.

**Prerequisite**: Phase 7 (persistence v2).

**Revisit when**: A user needs historical signal values (not just churn/authorship) for a specific analysis. Could be useful for "when did architecture start eroding?" questions.

**Estimated effort**: 1-2 weeks. The pipeline already exists — this is "run it N times at different commits" plus storage.

---

## B3: Seasonality and Stationarity Operators

**What**:
- **Seasonality**: Autocorrelation `r(lag)` on signal time series. Detects release-cycle rhythms (e.g., complexity spikes every 2 weeks before release).
- **Stationarity**: Augmented Dickey-Fuller test. Answers "is this signal drifting or fluctuating around a mean?"

**Why deferred**: Requires 20+ data points (snapshots) to be statistically meaningful. No current finder uses either operator. The simpler operators (delta, velocity, trend) cover 90% of temporal questions.

**Prerequisite**: Phase 7 (signal_history with 20+ snapshots).

**Revisit when**: A finder needs to distinguish "this metric is drifting upward" (non-stationary) from "this metric fluctuates but returns to baseline" (stationary). Could power a "SEASONAL_HOTSPOT" finder.

**Estimated effort**: 1 week. scipy.stats has ADF test, numpy has autocorrelation.

---

## B4: G3 TYPE_FLOW Distance Space

**What**: Edges where file A uses a type defined in file B. Distance: `1 - |types_used_by_A ∩ types_defined_in_B| / |types_used_by_A|`. Creates a "contract proximity" graph between files.

**Why deferred**: Requires resolving type identifiers to their defining files. In Python (dynamic typing), `User` could be defined in `models/user.py`, re-exported from `models/__init__.py`, or imported from a third-party package. This is essentially type inference — half a compiler. Feasible for typed languages (TypeScript, Java, Rust) but not for Python without deep analysis.

**Prerequisite**: Phase 1 (tree-sitter with class/type extraction), plus a type resolution engine.

**Revisit when**: CALL edge resolution (G2) is working. TYPE_FLOW uses similar cross-file resolution infrastructure.

**Estimated effort**: 3-4 weeks. Hard problem.

---

## B5: Combined Multi-Graph Laplacian

**What**: Weighted sum of Laplacians from all distance spaces: `L_combined = Σ αᵢ Lᵢ`. Eigenvectors define "multi-relational communities" — groups of files that are close in ALL spaces simultaneously.

**Why deferred**: Over-engineering. Individual distance space disagreements (G1 vs G4, G1 vs G6, etc.) already produce concrete findings. The combined operator produces "multi-relational communities" but there's no finder that consumes them. Adding weighted Laplacian combination introduces tuning parameters (α weights) with no ground truth to calibrate against.

**Prerequisite**: At least 4 of 6 distance spaces operational (G1, G4, G5, G6).

**Revisit when**: Someone asks "show me groups of files that are related in EVERY dimension simultaneously." Until then, Louvain communities on the import graph suffice.

**Estimated effort**: 1 week. Math is straightforward (scipy sparse LA). Value is uncertain.

---

## B6: G2 CALL Edge Resolution

**What**: Resolve syntactic call targets (`foo()`) to the file that defines `foo`. Creates behavioral proximity graph — files whose functions actually call each other, not just import each other.

**Why deferred**: Cross-file function resolution is hard. `foo()` could be: a local variable, a builtin, a method on `self`, an imported function, or a dynamically dispatched call. Phase 1 provides `call_targets[]` (unresolved syntactic targets) which enables heuristic matching, but reliable resolution requires scope analysis.

**Prerequisite**: Phase 1 (call_targets from tree-sitter).

**Revisit when**: Phase 3 is complete and there's appetite for a heuristic call graph. Start with Python (most structured imports) as a pilot.

**Estimated effort**: 2-3 weeks for heuristic resolution (Python-first), 6+ weeks for multi-language.

---

## B7: Web UI

**What**: Interactive exploration platform. `shannon-insight serve` launches a local FastAPI server with views: Map (graph visualization with distance space switching), Timeline (signal sparklines over time), File (deep-dive), Architecture (layer diagram), PR Risk (change-scoped analysis).

**Why deferred**: The engine is the product. CLI + JSON output covers CI integration and developer workflows. Building a web UI before the analysis engine is validated is premature optimization of the presentation layer.

**Prerequisite**: All phases 0-7 complete. JSON output format stabilized.

**Revisit when**: The analysis produces consistent, useful results on 10+ real codebases and the JSON output format is stable. Then build the UI as a consumer of the JSON API.

**Estimated effort**: 4-8 weeks. Separate project. React + D3 for graph visualization.

---

## Priority Order for Revisiting

| Priority | Feature | Value if it works | Risk |
|----------|---------|-------------------|------|
| 1 | B6: CALL edges | Enables G2, TYPE_FLOW, better architecture | Hard resolution problem |
| 2 | B7: Web UI | Massive UX improvement | Large scope, separate project |
| 3 | B3: Seasonality/Stationarity | New finder class | Needs lots of data points |
| 4 | B2: Kind 3 reconstruction | Historical signal analysis | Expensive computation |
| 5 | B4: G3 TYPE_FLOW | Contract proximity graph | Needs B6 first |
| 6 | B1: CP/Tucker | Evolution archetypes | Research, unproven |
| 7 | B5: Combined Laplacian | Multi-relational communities | No finder consumes it |
