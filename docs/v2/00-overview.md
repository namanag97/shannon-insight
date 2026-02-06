# Shannon Insight v2 — Overview

## Vision

Shannon Insight treats source code as a measurable physical system. It computes a multi-dimensional signal vector over every file, module, and codebase — across time — and surfaces actionable insights by detecting anomalies, disagreements, and threshold violations.

**The engine is the product.** CLI and JSON output are the primary interfaces. Web UI is backlogged (see `BACKLOG.md`). The engine works without any server, UI, or network — `pip install` and run.

## The Complete Model

```
8 Dimensions × 7 Scales × Time = Signal Field

4 Active Distance Spaces (G1 dependency, G4 co-change, G5 author, G6 semantic)
    + 2 backlogged (G2 call, G3 type)
    → Disagreements between spaces = systematic finding discovery

62 base signals + 6 temporal operators (delta, velocity, acceleration, trajectory, volatility, trend)
22 finding types across 5 categories
7 composite scores (1-10 scale)
```

See the `registry/` directory for canonical definitions of every dimension, scale, signal, distance space, finder, and composite.

## Pipeline Architecture

Six stages, not a flat pipeline. Triage determines what to compute. Two-wave analyzer execution ensures fusion always runs last.

```
STAGE 0: TRIAGE
    Detect: file count → tier (ABSOLUTE/BAYESIAN/FULL)
            languages → load parsers
            .git? → temporal ON/OFF
            authors → social ON/OFF

STAGE 1: PARSE (per-language, parallel)
    tree-sitter (if installed) → FileSyntax
    regex fallback             → FileSyntax (basic)

STAGE 2: ANALYZE (two parallel spines)
    STRUCTURAL SPINE              TEMPORAL SPINE
    scanning/ (IR0→IR1)           temporal/ (git → IR5t)
        ↓                              │
    semantics/ (IR2)                   │
        ↓                              │
    graph/ (IR3) ◄─────────────────────┘  (co-change enrichment)
        ↓
    architecture/ (IR4)

STAGE 3: FUSE (always runs last — Wave 2)
    signals/ (IR5s): collect → normalize → composites → health Laplacian

STAGE 4: FIND
    22 finders read SignalField, tier-aware (absolute thresholds or percentile+floor)
    Hotspot filter: suppress findings on stable code (unless structural-only)
    Group by scope (file/module/codebase), rank by severity × confidence

STAGE 5: OUTPUT
    JSON (primary), CLI rich terminal, --save → SQLite persistence
```

## Blackboard Pattern (within the kernel)

- Analyzers write signals to a shared `AnalysisStore`
- Finders read signals from `SignalField` (unified view)
- Each analyzer declares `requires` (signals needed) and `provides` (signals produced)
- Wave 1: kernel topologically sorts analyzers and runs what's needed
- Wave 2: `SignalFusionAnalyzer` always runs last, reads everything
- Finders gracefully skip if required signals are unavailable

## Three-Tier Degradation

The system adapts to codebase size:

| Tier | Files | Normalization | Composites | Finders use |
|------|-------|--------------|------------|-------------|
| ABSOLUTE | < 15 | none | skip | absolute thresholds |
| BAYESIAN | 15-50 | Beta-posterior pctl | compute | pctl + abs floor |
| FULL | 50+ | standard pctl | compute | pctl + abs floor |

## What Makes This Different

| Existing tools | Shannon Insight v2 |
|---|---|
| Measure one dimension | 8 dimensions simultaneously, cross-dimensional anomalies |
| File-level metrics | 7 scales from token to codebase |
| Snapshot analysis | Temporal dimension — Kind 1 (git) + Kind 2 (cross-snapshot) |
| Hand-crafted rules | Systematic finding discovery via distance space disagreements |
| Hotspot OR complexity | Hotspot filter: only flag complex code that people actually touch |
| No AI code awareness | First-class AI code quality detection (wiring score) |

## Novel Innovations

1. **Hotspot-filtered findings** — only flag code that is both problematic AND actively changing (CodeScene-validated approach)
2. **Health Laplacian** — treat health as scalar field over dependency graph, find local weak links
3. **Distance space disagreements** — pairs of 4 spaces, each pair a potential finding class
4. **AI wiring score** — systematic detection of orphans, stubs, phantoms, flat architecture, clones
5. **Three-tier degradation** — meaningful analysis from 5-file projects to 10K-file monorepos
6. **Automatic layer inference** — topological sort discovers FE→BE→DB architecture without configuration

## Deployment Models

| Model | Audience | What |
|---|---|---|
| **CLI + JSON** | Individual developer | `shannon-insight -C <path>` — full analysis, JSON output for tooling |
| **CI integration** | Development teams | GitHub Action, `--json --fail-on high`, merge gates |
| **Web UI** | Future (see `BACKLOG.md` B7) | Interactive exploration, backlogged until engine is validated |

## Document Structure

```
docs/v2/
├── 00-overview.md              ← you are here
├── 01-contracts.md             ← inter-module wiring diagram
├── BACKLOG.md                  ← deferred features (B1-B7)
├── registry/                   ← SINGLE SOURCE OF TRUTH for all cross-cutting concerns
│   ├── dimensions.md           ← 8 dimensions
│   ├── scales.md               ← 7 scales
│   ├── signals.md              ← 62 signals (THE catalog)
│   ├── temporal-operators.md   ← operators that apply to all signals
│   ├── distance-spaces.md      ← 4 active + 2 backlogged distance spaces
│   ├── derived-dimensions.md   ← products of fundamentals
│   ├── finders.md              ← 22 finding types
│   └── composites.md           ← 7 composite scores (1-10 scale)
├── modules/                    ← HOW things are computed (one dir per package)
│   ├── scanning/               ← IR0 + IR1
│   ├── semantics/              ← IR2 (NEW)
│   ├── graph/                  ← IR3
│   ├── architecture/           ← IR4 (NEW)
│   ├── temporal/               ← IR5t
│   ├── signals/                ← IR5s
│   ├── insights/               ← IR6
│   ├── persistence/            ← storage + snapshots
│   └── cli/                    ← terminal UI
├── phases/                     ← implementation phases (cross-cutting)
│   ├── phase-0-baseline.md     ← audit + gap analysis
│   ├── phase-1-deep-parsing.md ← tree-sitter (optional) + FileSyntax
│   ├── phase-2-semantics.md    ← IR2 semantic layer
│   ├── phase-3-graph-enrichment.md ← NCD clones, depth, orphans, G5
│   ├── phase-4-architecture.md ← IR4 module detection + layers
│   ├── phase-5-signal-fusion.md ← SignalField + composites + health Laplacian
│   ├── phase-6-finders.md      ← 15 new finders in 3 batches
│   └── phase-7-persistence-v2.md ← TensorSnapshot + finding lifecycle
└── validation/                 ← testing and validation strategy
```

**Registry** = WHAT exists (cross-cutting, canonical definitions).
**Modules** = HOW things are computed (per-package, references registry).
**Phases** = WHEN things are built (cross-cutting, references modules).
**Backlog** = WHAT'S deferred (with rationale and prerequisites).
