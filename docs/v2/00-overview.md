# Shannon Insight v2 — Overview

## Vision

Shannon Insight treats source code as a measurable physical system. It computes a multi-dimensional measurement tensor over every file, module, and codebase — across time — and surfaces actionable insights by detecting anomalies, disagreements, and threshold violations.

v2 expands from a CLI reporting tool to an interactive exploration platform with a web UI, while keeping the analysis engine as a standalone open-source library.

## The Complete Model

```
8 Dimensions × 7 Scales × Time = Measurement Tensor

6 Distance Spaces between entities

Derived dimensions = products of fundamentals
Findings = threshold conditions on derived dimensions
         = disagreements between distance spaces

~62 base signals + ~300 temporal derivatives = ~360 measurable quantities
22 finding types across 5 categories
6 composite scores
```

See the `registry/` directory for canonical definitions of every dimension, scale, signal, distance space, finder, and composite.

## Architecture Decision: Pipeline + Blackboard Hybrid

**The pipeline** defines computation order:

```
IR0 (files) → IR1 (syntax) → IR2 (semantics) → IR3 (graph) → IR4 (architecture)
                                                      ↑
IR5t (temporal: git) ─────────────────────────────────┘ (parallel, merges at IR3)

All IRs → IR5s (signal fusion) → IR6 (insights)
```

**The blackboard** defines data sharing within the insights engine:

- Analyzers write signals to a shared `AnalysisStore`
- Finders read signals from the store and produce findings
- Each declares `requires` (signals needed) and `provides` (signals produced)
- The kernel topologically sorts them and runs only what's needed

These aren't contradictory: the pipeline is the macro architecture (which IR feeds which), the blackboard is the micro pattern (how InsightKernel orchestrates analyzers and finders within a stage).

## Key Principle

**The engine is the product.** Everything else (CLI, web UI, CI runner) is a view into its output. The engine works without any server, UI, or network — `pip install` and run.

## What Makes This Different

| Existing tools | Shannon Insight v2 |
|---|---|
| Measure one dimension | 8 dimensions simultaneously, cross-dimensional anomalies |
| File-level metrics | 7 scales from token to codebase |
| Snapshot analysis | Full temporal dimension — every metric is a time series |
| Hand-crafted rules | Systematic finding discovery via distance space disagreements |
| Terminal output | Interactive multi-view web exploration |
| No AI code awareness | First-class AI code quality detection |

## Novel Innovations

1. **Health Laplacian** — treat health as scalar field over dependency graph, find weak links via Laplacian diffusion
2. **Distance space disagreements** — 15 pairs of 6 spaces, each pair a potential finding class
3. **AI wiring score** — systematic detection of orphans, stubs, phantoms, flat architecture, clones
4. **Temporal tensor decomposition** — CP decomposition reveals evolution archetypes
5. **MDL architecture fit** — single number for "does our architecture still match reality"
6. **Mutual information between structure and change** — do changes respect module boundaries?
7. **Zipf deviation** — power-law file size distribution distinguishes human from AI code
8. **Interactive distance space switching** — switch graph layout between 6 proximity types

## Deployment Models

| Model | Audience | What |
|---|---|---|
| **Local server** | Individual developer | `shannon-insight serve` — engine + API + frontend in one process, SQLite, no network |
| **CI integration** | Development teams | GitHub Action, PR risk scores, merge gates |
| **Hosted platform** | Engineering orgs | OAuth repo connect, persistent dashboard, cross-repo insights |

## Document Structure

```
docs/v2/
├── 00-overview.md              ← you are here
├── 01-contracts.md             ← inter-module wiring diagram
├── registry/                   ← SINGLE SOURCE OF TRUTH for all cross-cutting concerns
│   ├── dimensions.md           ← 8 dimensions
│   ├── scales.md               ← 7 scales
│   ├── signals.md              ← ~62 signals (THE catalog)
│   ├── temporal-operators.md   ← operators that apply to all signals
│   ├── distance-spaces.md      ← 6 distance spaces
│   ├── derived-dimensions.md   ← products of fundamentals
│   ├── finders.md              ← 22 finding types
│   └── composites.md           ← 6 composite scores
├── modules/                    ← HOW things are computed (one dir per package)
│   ├── scanning/               ← IR0 + IR1
│   ├── semantics/              ← IR2 (NEW)
│   ├── graph/                  ← IR3
│   ├── architecture/           ← IR4 (NEW)
│   ├── temporal/               ← IR5t
│   ├── signals/                ← IR5s
│   ├── insights/               ← IR6
│   ├── persistence/            ← storage + snapshots
│   ├── cli/                    ← terminal UI
│   └── web/                    ← web UI (NEW, future)
├── phases/                     ← implementation phases (cross-cutting)
└── validation/                 ← testing and validation strategy
```

**Registry** = WHAT exists (cross-cutting, canonical definitions).
**Modules** = HOW things are computed (per-package, references registry).
**Phases** = WHEN things are built (cross-cutting, references modules).
