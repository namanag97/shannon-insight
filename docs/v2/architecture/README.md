# Shannon Insight v2 Architecture

> **The definitive reference for Shannon Insight's data model and architecture.**
> Self-contained. Every entity, signal, relation, pattern, and formula is fully specified here.

---

## What is Shannon Insight?

Shannon Insight is a **multi-dimensional codebase analysis engine**. It views code through 8 independent lenses (dimensions), computes 62 signals, builds 6 distance spaces, and detects 22 types of findings where signals disagree.

**The Core Insight**: Bugs hide where different views of the codebase tell contradictory stories.
- Files that change together but have no import? **Hidden coupling.**
- Files that import each other but share no concepts? **Accidental coupling.**
- Files that are central in the graph but owned by one person? **Knowledge silo.**

---

## Document Structure

```
architecture/
├── README.md                    ← You are here
├── 01-pipeline/                 ← How data flows through the system
│   ├── README.md
│   ├── 01-initialize.md         ← Runtime context, config
│   ├── 02-collect.md            ← Collectors (5)
│   ├── 03-model.md              ← Build fact store
│   ├── 04-derive.md             ← Signal derivation (topo-sorted)
│   ├── 05-detect.md             ← Pattern matching
│   ├── 06-rank.md               ← Prioritization
│   └── 07-output.md             ← Formatting, persistence
├── 02-entities/                 ← What we analyze
│   └── README.md                ← 6 entity types
├── 03-signals/                  ← What we measure (62 signals)
│   ├── README.md                ← Signal model, registry
│   ├── 01-per-file.md           ← Signals 1-36
│   ├── 02-per-module.md         ← Signals 37-51
│   └── 03-global.md             ← Signals 52-62
├── 04-relations/                ← How entities connect (8 types)
│   └── README.md
├── 05-distance-spaces/          ← 6 notions of "closeness"
│   └── README.md
├── 06-patterns/                 ← What we detect (22 finders)
│   ├── README.md
│   ├── 01-existing.md           ← 7 v1 finders
│   ├── 02-ai-quality.md         ← 6 AI code quality finders
│   ├── 03-social-team.md        ← 3 team/social finders
│   ├── 04-architecture.md       ← 3 architecture finders
│   └── 05-cross-dimensional.md  ← 3 cross-dimensional finders
├── 07-composites/               ← Fused scores (formulas)
│   └── README.md
├── 08-store/                    ← Blackboard (13 slots)
│   └── README.md
└── 09-runtime/                  ← Meta concerns
    └── README.md
```

---

## Quick Reference

| Concept | Count | Location |
|---------|-------|----------|
| **Entity Types** | 6 | `02-entities/` |
| **Signals** | 62 | `03-signals/` |
| **Relation Types** | 8 | `04-relations/` |
| **Distance Spaces** | 6 | `05-distance-spaces/` |
| **Patterns (Finders)** | 22 | `06-patterns/` |
| **Composite Formulas** | 7 | `07-composites/` |
| **Store Slots** | 13 | `08-store/` |
| **Dimensions** | 8 | Below |
| **Phases** | 8 | Below |

---

## The 8 Dimensions

Every signal belongs to exactly one dimension. Dimensions are irreducible — none can be derived from the others.

| # | Dimension | Question | Examples |
|---|-----------|----------|----------|
| D1 | **SIZE** | How much? | lines, function_count, file_count |
| D2 | **SHAPE** | What structure? | max_nesting, impl_gini, stub_ratio |
| D3 | **NAMING** | What concepts? | role, concept_count, naming_drift |
| D4 | **REFERENCE** | What points to what? | pagerank, in_degree, is_orphan |
| D5 | **INFORMATION** | How dense? | compression_ratio, semantic_coherence |
| D6 | **CHANGE** | How does it evolve? | total_changes, churn_cv, churn_trajectory |
| D7 | **AUTHORSHIP** | Who touches it? | bus_factor, author_entropy, knowledge_gini |
| D8 | **INTENT** | Why was it changed? | fix_ratio, refactor_ratio |

---

## The 8 Phases

Implementation is split into 8 phases. Each phase unlocks specific signals.

| Phase | Name | Signals Unlocked | Cumulative |
|-------|------|------------------|------------|
| 0 | Baseline | 1-3, 7, 14-18, 23-24, 52-55 | 15 |
| 1 | Deep Parsing | 4-6, 12, 26 | 20 |
| 2 | Semantics | 8-11, 13, 25 | 26 |
| 3 | Graph Enrichment | 19-21, 27-34, 56-59 | 40 |
| 4 | Architecture | 37-44, 50 | 49 |
| 5 | Signal Fusion | 35-36, 45-49, 51, 60-62 | 62 |
| 6 | Finders | — (all 22 finders) | 62 |
| 7 | Persistence v2 | — (TensorSnapshot, history) | 62 |

---

## Data Flow (One Run)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INITIALIZE                                    │
│  Discover root, load config, detect language, build RuntimeContext      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            COLLECT                                      │
│                                                                         │
│   CodeCollector ──→ FileMetrics[], FileSyntax[]                        │
│   GitCollector ──→ GitHistory, ChurnSeries[]                           │
│   DependencyCollector ──→ IMPORTS relations                            │
│   CoChangeCollector ──→ COCHANGES_WITH relations                       │
│   SemanticCollector ──→ FileSemantics[], SIMILAR_TO relations          │
│                                                                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             MODEL                                       │
│                                                                         │
│   Build FactStore:                                                      │
│   ├── entities: Dict[EntityId, Entity]                                 │
│   ├── signals: SignalStore (Entity × Signal × Time → Value)            │
│   └── relations: RelationGraph (typed edges)                           │
│                                                                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            DERIVE                                       │
│                                                                         │
│   Topo-sorted by requires/provides:                                    │
│   1. PageRankDeriver ──→ pagerank                                      │
│   2. OrphanDeriver ──→ is_orphan, depth                                │
│   3. ModuleDeriver ──→ cohesion, coupling, instability                 │
│   4. PercentileDeriver ──→ *_pctl (normalized)                         │
│   5. CompositeDeriver ──→ risk_score, health_score, etc.               │
│   6. LaplacianDeriver ──→ raw_risk, delta_h                            │
│                                                                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            DETECT                                       │
│                                                                         │
│   For each Pattern in registry:                                        │
│     If pattern.requires satisfied in store:                            │
│       For each target in pattern.scope:                                │
│         If pattern.predicate(store, target):                           │
│           findings.append(Finding(...))                                │
│                                                                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             RANK                                        │
│                                                                         │
│   score(f) = severity × confidence × impact                            │
│   where impact = pagerank(target) if FILE scope else 1.0               │
│   Sort by score descending, take top N                                 │
│                                                                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            OUTPUT                                       │
│                                                                         │
│   Format: terminal (rich), JSON, HTML report                           │
│   Persist: TensorSnapshot → SQLite (.shannon/history.db)               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Abstractions

| Abstraction | Definition | Example |
|-------------|------------|---------|
| **Entity** | Something we analyze | File, Module, Codebase |
| **Signal** | A measurement on an entity | `pagerank=0.95`, `bus_factor=1` |
| **Relation** | A typed edge between entities | `auth.py IMPORTS db.py` |
| **DistanceSpace** | A metric on entity pairs | G1: dependency distance |
| **Pattern** | A declarative rule | `pctl(pagerank) > 0.90 AND ...` |
| **Finding** | A detected issue | `HIGH_RISK_HUB on auth.py` |

---

## Mathematical Foundations

### Gini Coefficient
```
G = (2 × Σᵢ i × xᵢ) / (n × Σ xᵢ) - (n + 1) / n

where xᵢ sorted ascending, i is 1-indexed, n = count
G = 0: perfect equality
G = 1: maximum inequality
```

### Shannon Entropy
```
H = -Σ p(x) × log₂(p(x))

H = 0: single value (no uncertainty)
H = log₂(n): uniform distribution (max uncertainty)
```

### Percentile (Canonical)
```
pctl(signal, f) = |{v ∈ all_files : signal(v) ≤ signal(f)}| / |all_files|

Uses ≤ (not <) for consistent ordering
```

### Bus Factor
```
bus_factor = 2^H

where H = author_entropy
bus_factor = 1: single author
bus_factor = k: k equally-contributing authors
```

---

## Navigation

Start with:
1. **[Pipeline](01-pipeline/README.md)** — understand the flow
2. **[Entities](02-entities/README.md)** — what we analyze
3. **[Signals](03-signals/README.md)** — what we measure
4. **[Patterns](06-patterns/README.md)** — what we detect

For implementation:
- **[Store](08-store/README.md)** — the blackboard
- **[Runtime](09-runtime/README.md)** — config, tiers, graceful degradation
