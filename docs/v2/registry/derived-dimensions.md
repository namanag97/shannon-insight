# Registry: Derived Dimensions

All higher-level concepts are products of fundamental dimensions (from `dimensions.md`). Every finding (in `finders.md`) decomposes into a condition on derived dimensions.

## First-Order Derivations (two fundamentals)

| Derived | Components | Intuition | Example signal expression |
|---------|-----------|-----------|--------------------------|
| **Complexity** | SIZE × SHAPE | Big AND deep = hard to understand | `lines × max_nesting` |
| **Coupling** | REFERENCE between entities | How entangled | `external_edges / total_edges` |
| **Cohesion** | REFERENCE + NAMING within entity | Parts belong together | `internal_edges × concept_focus` |
| **Density** | SIZE / INFORMATION | Big but low entropy = boilerplate | `lines / compression_ratio` |
| **Volatility** | CHANGE × CHANGE.variance | Frequent AND erratic | `total_changes × churn_cv` |
| **Ownership** | AUTHORSHIP × concentration | Knowledge monopolized | `1 / bus_factor` |
| **Purposefulness** | INTENT × consistency | Changes deliberate or reactive | `1 - fix_ratio` |

## Second-Order Derivations (three+ fundamentals)

| Derived | Components | Intuition |
|---------|-----------|-----------|
| **Risk** | REFERENCE × CHANGE × SIZE | Central, changing, big = dangerous |
| **Knowledge risk** | REFERENCE × (1/AUTHORSHIP) × SIZE | Central, big, single owner |
| **Debt** | accumulated INTENT("fix") × SIZE × CHANGE | Bug-prone, big, still changing |
| **Staleness** | SIZE × (1/CHANGE) × AUTHORSHIP.turnover | Big, untouched, original authors gone |
| **Drift** | ΔNAMING / ΔTIME with low ΔREFERENCE | Concepts changing but structure not adapting |
| **Erosion** | ΔSHAPE(worsening) × ΔCHANGE(accelerating) | Structure degrading faster over time |
| **Fragility** | REFERENCE.blast_radius × (1/INFORMATION.coherence) | Wide impact + low internal focus |
| **Wiring quality** | REFERENCE.connectivity × SIZE.completeness × INFORMATION.density | How well-connected and implemented |

## Finding Decomposition

Every finding is a threshold condition on derived dimensions:

```
FINDING                    = CONDITION ON DERIVED DIMENSIONS
─────────────────────      ───────────────────────────────────
High risk hub              Risk HIGH (REFERENCE.pagerank × CHANGE.velocity × SIZE)
Hidden coupling            d(CHANGE) CLOSE × d(REFERENCE) FAR between pair
Dead dependency            d(REFERENCE) CLOSE × d(CHANGE) FAR between pair
God file                   Complexity HIGH × Cohesion LOW (SIZE × SHAPE × 1/NAMING.coherence)
Unstable file              Volatility HIGH (CHANGE × CHANGE.variance)
Knowledge silo             Ownership HIGH × Risk HIGH (1/AUTHORSHIP × REFERENCE)
Orphan code                REFERENCE.connectivity = 0 × NAMING.role ≠ ENTRY_POINT
Hollow code                Density LOW × SHAPE.gini HIGH (stubs + uneven implementation)
Architecture erosion       ΔSHAPE.violations INCREASING × ΔCHANGE.velocity INCREASING
Conway violation           d(AUTHORSHIP) FAR × d(REFERENCE) CLOSE between modules
Bug attractor              INTENT.fix_ratio HIGH × REFERENCE.pagerank HIGH
Weak link                  Δh(health Laplacian) >> 0 (much worse than neighbors)
```

**To add a new finding**: express it as a condition on fundamental dimensions. If the fundamentals are measured, the finding falls out automatically.

## AI Code Quality Signature

AI-generated code has a distinctive multi-dimensional signature:

| Dimension | Healthy codebase | AI-generated |
|-----------|-----------------|-------------|
| D1 SIZE | Varies naturally | Suspiciously uniform file sizes |
| D2 SHAPE | Gini 0.3-0.5 | Bimodal Gini > 0.6 (complete + stubs) |
| D3 NAMING | Concepts match filenames | Naming drift, generic identifiers |
| D4 REFERENCE | Connected, moderate depth | Sparse, many orphans, flat (depth ≤ 1) |
| D5 INFORMATION | Moderate compression | Low function-level entropy (stubs) + high NCD (clones) |
| D6 CHANGE | Organic commit history | Burst creation, then silence |
| D7 AUTHORSHIP | Multiple authors | Single author / AI session |
| D8 INTENT | Mix of feature/fix/refactor | All "initial commit" or "add feature" |

The `wiring_score` composite (see `signals.md` #60) captures this multi-dimensional signature.
