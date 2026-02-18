# Shannon Insight: Accurate Signal Reference (from code)

## Count: 67 signals in Signal enum
The docstring says "62 signals" — STALE. 5 added after with #Xa/b numbering.

## Per-File: IR1 Syntactic (7) — produced by scanning
| # | Signal | Type | Polarity | Phase | Producer |
|---|--------|------|----------|-------|----------|
| 1 | LINES | int | high_is_bad | 0 | scanning |
| 2 | FUNCTION_COUNT | int | high_is_bad | 0 | scanning |
| 3 | CLASS_COUNT | int | neutral | 0 | scanning |
| 4 | MAX_NESTING | int | high_is_bad | 1 | scanning |
| 5 | IMPL_GINI | float | high_is_bad | 1 | scanning |
| 6 | STUB_RATIO | float | high_is_bad | 1 | scanning |
| 7 | IMPORT_COUNT | int | neutral | 0 | scanning |

## Per-File: IR2 Semantic (6) — produced by SemanticAnalyzer
| # | Signal | Type | Polarity | Phase | Producer |
|---|--------|------|----------|-------|----------|
| 8 | ROLE | str | neutral | 2 | semantics/roles |
| 9 | CONCEPT_COUNT | int | high_is_bad | 2 | semantics |
| 10 | CONCEPT_ENTROPY | float | high_is_bad | 2 | semantics |
| 11 | NAMING_DRIFT | float | high_is_bad | 2 | semantics |
| 12 | TODO_DENSITY | float | high_is_bad | 1 | scanning |
| 13 | DOCSTRING_COVERAGE | float | high_is_good | 2 | semantics |

## Per-File: IR3 Graph (15) — produced by StructuralAnalyzer + fusion
| # | Signal | Type | Polarity | Phase | Producer |
|---|--------|------|----------|-------|----------|
| 14 | PAGERANK | float | high_is_bad | 0 | graph/algorithms |
| 15 | BETWEENNESS | float | high_is_bad | 0 | graph/algorithms |
| 16 | IN_DEGREE | int | neutral | 0 | graph/algorithms |
| 17 | OUT_DEGREE | int | neutral | 0 | graph/algorithms |
| 18 | BLAST_RADIUS_SIZE | int | high_is_bad | 0 | graph/algorithms |
| 19 | DEPTH | int | neutral | 3 | graph/algorithms |
| 20 | IS_ORPHAN | bool | high_is_bad | 3 | graph/algorithms |
| 20a | CYCLE_MEMBER | bool | high_is_bad | 3 | graph/algorithms |
| 20b | CYCLE_SIZE | int | high_is_bad | 3 | graph/algorithms |
| 21 | PHANTOM_IMPORT_COUNT | int | high_is_bad | 3 | graph/algorithms |
| 22 | BROKEN_CALL_COUNT | int | high_is_bad | 4 | graph/algorithms [ALWAYS 0] |
| 23 | COMMUNITY | int | neutral | 0 | graph/algorithms |
| 24 | COMPRESSION_RATIO | float | neutral | 5 | signals/fusion |
| 25 | SEMANTIC_COHERENCE | float | high_is_good | 5 | signals/fusion |
| 26 | COGNITIVE_LOAD | float | high_is_bad | 5 | signals/fusion |

## Per-File: IR5t Temporal (9) — produced by TemporalAnalyzer
| # | Signal | Type | Polarity | Phase | Producer |
|---|--------|------|----------|-------|----------|
| 27 | TOTAL_CHANGES | int | high_is_bad | 3 | temporal/churn |
| 28 | CHURN_TRAJECTORY | str | neutral | 3 | temporal/churn |
| 29 | CHURN_SLOPE | float | high_is_bad | 3 | temporal/churn |
| 30 | CHURN_CV | float | high_is_bad | 3 | temporal/churn |
| 31 | BUS_FACTOR | float | high_is_good | 3 | temporal/churn |
| 32 | AUTHOR_ENTROPY | float | high_is_good | 3 | temporal/churn |
| 33 | FIX_RATIO | float | high_is_bad | 3 | temporal/churn |
| 34 | REFACTOR_RATIO | float | high_is_good | 3 | temporal/churn |
| 34a | CHANGE_ENTROPY | float | high_is_bad | 3 | temporal/churn |

## Per-File: IR5s Composites (4) — produced by SignalFusionAnalyzer
| # | Signal | Type | Polarity | Phase | Formula |
|---|--------|------|----------|-------|---------|
| 35 | RISK_SCORE | float | high_is_bad | 5 | 0.25×pctl(pr)+0.20×pctl(blast)+0.20×pctl(cog)+0.20×instability_factor+0.15×bf_term |
| 36 | WIRING_QUALITY | float | high_is_good | 5 | 1-(0.375×orphan+0.3125×stub_ratio+0.3125×phantom_ratio) |
| 36a | FILE_HEALTH_SCORE | float | high_is_good | 5 | 1-(0.25×risk+0.25×(1-wiring)+0.20×pctl(cog)+0.15×stub+0.15×orphan) |
| 36b | DELTA_H | float | high_is_bad | 5 | raw_risk[f] - mean(raw_risk[neighbours]) |

## Per-Module: IR4 (15) — produced by ArchitectureAnalyzer + fusion
| # | Signal | Type | Polarity | Phase | Producer |
|---|--------|------|----------|-------|----------|
| 37 | COHESION | float | high_is_good | 4 | architecture |
| 38 | COUPLING | float | high_is_bad | 4 | architecture |
| 39 | INSTABILITY | float | neutral | 4 | architecture [Optional, None if isolated] |
| 40 | ABSTRACTNESS | float | neutral | 4 | architecture |
| 41 | MAIN_SEQ_DISTANCE | float | high_is_bad | 4 | architecture |
| 42 | BOUNDARY_ALIGNMENT | float | high_is_good | 4 | architecture |
| 43 | LAYER_VIOLATION_COUNT | int | high_is_bad | 4 | architecture |
| 44 | ROLE_CONSISTENCY | float | high_is_good | 4 | architecture |
| 45 | VELOCITY | float | neutral | 5 | signals/fusion |
| 46 | COORDINATION_COST | float | high_is_bad | 5 | signals/fusion |
| 47 | KNOWLEDGE_GINI | float | high_is_bad | 5 | signals/fusion |
| 48 | MODULE_BUS_FACTOR | float | high_is_good | 5 | signals/fusion |
| 49 | MEAN_COGNITIVE_LOAD | float | high_is_bad | 5 | signals/fusion |
| 50 | FILE_COUNT | int | neutral | 4 | architecture |
| 51 | HEALTH_SCORE | float | high_is_good | 5 | signals/fusion |

## Global: S6 (11) — produced by various analyzers + fusion
| # | Signal | Type | Polarity | Phase | Producer |
|---|--------|------|----------|-------|----------|
| 52 | MODULARITY | float | high_is_good | 0 | graph/algorithms |
| 53 | FIEDLER_VALUE | float | high_is_good | 0 | graph/algorithms |
| 54 | SPECTRAL_GAP | float | high_is_good | 0 | graph/algorithms |
| 55 | CYCLE_COUNT | int | high_is_bad | 0 | graph/algorithms |
| 56 | CENTRALITY_GINI | float | high_is_bad | 3 | graph/algorithms |
| 57 | ORPHAN_RATIO | float | high_is_bad | 3 | graph/algorithms |
| 58 | PHANTOM_RATIO | float | high_is_bad | 3 | graph/algorithms |
| 59 | GLUE_DEFICIT | float | high_is_bad | 3 | graph/algorithms |
| 60 | WIRING_SCORE | float | high_is_good | 5 | signals/fusion |
| 61 | ARCHITECTURE_HEALTH | float | high_is_good | 5 | signals/fusion |
| 62 | CODEBASE_HEALTH | float | high_is_good | 5 | signals/fusion |

## Key Notes
- SEMANTIC_COHERENCE = 1 / (1 + concept_entropy) — derived, not independently computed
- COGNITIVE_LOAD = log2(lines+1) × (1+complexity/10) × (1+nesting/5) × (1+gini)
- INSTABILITY = None for isolated modules (Ca=Ce=0), not 0.0
- BROKEN_CALL_COUNT: always 0, placeholder until CALL edges implemented
- Signals 52-54 (MODULARITY, FIEDLER_VALUE, SPECTRAL_GAP) registered at phase 0 but
  FIEDLER_VALUE and SPECTRAL_GAP are actually computed by SpectralAnalyzer (phase 3 equivalent)
- Percentileable signals = all with percentileable=True in registry (~40 of 67)
- ABSOLUTE tier (<15 files) skips percentile normalization entirely
