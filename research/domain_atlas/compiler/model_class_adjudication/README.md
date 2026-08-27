# Deterministic model-class adjudication

Status: evidence-backed **candidate compiler contract**. It is not a solver, provider catalogue,
vertical solution, production qualifier, or completeness claim.

This package closes a specific compiler gap: before matching any solver, simulator, numerical
runtime, or library, the compiler must prove what kind of formal problem the declared subproblem
actually is—or refuse to classify it.

```text
vertical business problem
  pipeline nomination | bed flow | tender allocation | scheduling | ...
                         |
                         v
                closed subproblem boundary
                         |
        +----------------+----------------+
        | domain/units   | expressions    | uncertainty/time
        | objectives     | constraints    | composition/effects
        +----------------+----------------+
                         |
                         v
                 typed feature facts
                         |
                         v
          deterministic sound predicates + proofs
                         |
            +------------+-------------+
            |                          |
            v                          v
      class facets                 typed refusal
 LP + stochastic + two-stage      open scope / unknown domain /
 MISOCP + robust                  unproved linearization / ...
 simulation + optimization
            |
            v
 provider capability requirements (never a provider selection)
            |
            v
 exact offer + target + qualification + vertical acceptance
```

## Why this is not a flat enum

A model has several orthogonal classifications. “Two-stage stochastic MILP” is not one magical
vendor category: it is a conjunction of linear algebraic structure, integer domains, a probability
law, before/after-information decisions, recourse, and nonanticipativity. “Robust SOCP” similarly
combines a conic base formulation with governed uncertainty-set semantics.

The candidate therefore contains nine axes, 93 typed feature atoms, and 43 class facets spanning:

- continuous LP, MILP/binary LP, QP/MIQP, QCQP/MIQCQP, SOCP/MISOCP, SDP, exponential/power cone,
  convex/general NLP, and MINLP;
- finite-domain CP, exact CP-SAT-interface models, SAT, SMT, and pseudo-Boolean problems;
- certified network-flow specialization, bilevel, complementarity/equilibrium, planning, dynamic
  programming, MDP/POMDP, and optimal control;
- two-stage/multistage stochastic, robust, distributionally robust, and chance-constrained facets;
- discrete-event, continuous, system-dynamics, agent-based, Monte Carlo, co-simulation,
  simulation-optimization, and hybrid-composition facets.

This list is open-world. An unknown formalism extends the registry; it is never coerced to the
nearest name.

## Transformations are typed relations, not compiler tricks

Twenty-three transformation contracts distinguish exact equivalence, equisatisfiability with a
decoder, outer relaxation, bound production, candidate generation, bounded numerical approximation,
statistical approximation, and composition-relative equivalence. This prevents a target solver
class from overwriting the source problem's meaning.

```text
MILP --continuous relaxation--> LP
          allowed: relaxation bound
          forbidden: original-model feasibility or optimality

optimal control --discretization--> NLP
          allowed: discretized-model result + proved error envelope
          forbidden: continuous-time feasibility by default

stochastic program --finite scenario expansion--> LP/MILP
          allowed: result relative to exact scenario/revelation law
          forbidden: true-population guarantee or erased scenario lineage
```

An LLM or tool agent may propose a reformulation; it cannot supply its equivalence, error, decoding,
or loss receipt. A dedicated negative trace enforces this refusal.

## The agent and LLM boundary

Agents and generative models are permitted where intent requests them, but they are **not** model
classes and they are not ambient dependencies:

```text
optional model / tool-agent extension
  propose declaration | propose alternative | propose plan | explain trace
                             |
                             v
deterministic core
  parse -> type -> extract facts -> adjudicate -> solve/simulate -> validate
       -> qualify -> authorize -> execute -> verify receipt
```

The trace `trace.mca.fixture.lp_with_llm_proposal` adds both a generative proposal and tool-agent
fact to the canonical LP fixture. Its deterministic class remains exactly `continuous_lp`. The
validator fails if that changes.

Predictive/statistical ML is also kept separate. A fitted demand forecast may enter a stochastic
or robust model through a versioned prediction and uncertainty contract; it does not become an
agent. Conversely, an “agent” in agent-based simulation is a modeled entity with state and behavior
rules, not an LLM or tool-using software agent by name.

## Pipeline nomination falsification

The broad oil-and-gas nomination problem is intentionally refused as LP. Its current boundary still
contains unresolved nonlinear hydraulics, mixed commitment domains, uncertainty, and composition
edges. A narrower finite-coefficient continuous nomination-capacity **screening subproblem** can be
classified as LP after those concerns are proved outside its boundary. Even then it remains blocked
by provider qualification and vertical acceptance. Classification does not authorize curtailment or
any other operational effect.

```text
broad nomination problem
  contracts + priorities + integer commitments + uncertainty + hydraulics
                |
                +-- LP? --> REFUSE: open / mixed / nonlinear / uncertain
                |
                v
adjudicated screening cut
  continuous variables + affine objective/constraints + finite coefficients
                |
                +-- LP --> CLASSIFIED
                              |
                              +-- provider qualified? no
                              +-- vertical accepted? no
                              +-- effect authority? separate
```

## Artifacts

- `metamodel.json` — inputs, outputs, multi-axis semantics, constitutional laws, upstream digests.
- `classification-axes.jsonl` and `feature-atoms.jsonl` — orthogonal facts rather than product names.
- `model-classes.jsonl` — sound sufficient predicates and non-equivalence warnings.
- `classification-rules.jsonl` — executable class predicates plus non-collapse laws.
- `transformation-kinds.jsonl` and `transformation-traces.jsonl` — 23 semantic relations and seven
  falsification fixtures; none has an executed proof receipt.
- `provider-requirements.jsonl` — one unbound exact-subject/result/qualification requirement for
  each of the 43 class facets; no provider is selected or qualified.
- `proof-obligations.jsonl` and `refusal-rules.jsonl` — evidence needed and fail-closed outcomes.
- `decision-points.jsonl` — owner- and compiler-phase-bound choices; no silent defaults.
- `automation-boundaries.jsonl` — deterministic, predictive, generative, tool-agent, modeled-agent,
  and human roles kept separate.
- `bounded-contexts.jsonl` and `library-boundaries.jsonl` — candidate semantic ownership seams.
- `classification-traces.jsonl` and `adjudication-results.jsonl` — ten deterministic positive,
  negative-twin, cross-industry, hybrid, and extension-invariance fixtures.
- `gaps.jsonl` — blocking implementation, proof, provider, vertical, and independent-review gaps.

## Deterministic rebuild and validation

```bash
python3 research/domain_atlas/compiler/model_class_adjudication/build_bundle.py
python3 research/domain_atlas/compiler/model_class_adjudication/validate_bundle.py
```

The validator checks identity/reference closure, upstream digests, predicate feature closure, stored
results against the executable adjudicator, extension-removal invariance, ABM/LLM separation,
pipeline fail-closure, and the absence of fabricated provider qualification or vertical acceptance.
Passing means the research bundle is internally consistent—not that the taxonomy is complete or a
solution is deployable.
