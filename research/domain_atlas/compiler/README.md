# Corpus-to-compiler closure contract

This folder defines how the research corpus becomes compiler input without pretending the compiler
already exists.

```text
declared enterprise intent
       |
       v
vertical language + analytical cases + authority
       |
       v
required practices/methods + data observations/shapes + source capabilities
       |
       v
canonical-reference adjudication + typed operation hypergraph + assurance laws
       |
       v
method/operation -> algorithm -> kernel + representation requirements
       |
       v
capability requirements --match/prove--> library/provider/target offers
       |                                      |
       +------------- binding ----------------+
                              |
                              v
physical/runtime plan -> artifacts -> runtime receipts -> acceptance evidence
```

The closed metamodel governs identity, editions, ownership, requirement/offer/binding/gap semantics,
compiler stages and proof results. Industries, practices, source classes, types, operations,
libraries, providers and targets are open registries. A new registry record must not require a new
compiler branch; an unrecognized semantic or missing capability produces a typed gap.

The compiler preserves non-collapsible chains discovered by the horizontal research:

```text
business question -> practice -> study design -> formal method -> algorithm -> kernel
                  -> reusable library -> execution environment -> product
                  -> reviewed decision handoff -> separate effect authority

semantic type -> carrier -> encoding -> framing -> layout/container -> codec
              -> implementation offer -> target occurrence

work contract -> resource demand -> admission/quota/budget -> resource offer
              -> reservation -> allocation -> lease/fence -> deployment occurrence
              -> observed usage -> rated/billed usage

monitored subject -> source occurrence -> collection attempt + observation window
                  -> candidate signal -> verified change event -> impact/invalidation
                  -> migration or requalification -> replacement receipt

expert identity -> exact contribution artifact -> scoped contribution claim
                -> independent evidence/counterevidence -> canonical mapping
                -> requirement or candidate library boundary

prediction target + information cutoff -> feature/label/study split contracts
                -> model family -> estimator + objective -> training algorithm
                -> fitted artifact -> calibration/evaluation -> decision rule
                -> deployment monitoring/retraining/retirement

vertical problem family -> closed formal subproblem -> typed feature facts
                -> multi-axis model-class adjudication or refusal
                -> transformation equivalence/loss receipts
                -> algorithm/kernel/provider requirements -> exact qualified offer
```

Each transition needs its own compatibility law and evidence. For example, a hash join algorithm is
not an inner-join semantic contract, and a Parquet file name is not proof of its logical types,
codec profile, corruption behavior or reader compatibility.
Likewise, a CPU request is not observed CPU use, quota is not physical capacity, reservation is not
allocation, and a lease without enforcement at the protected effect is not fencing.
Likewise, a failed feed is not evidence of no change, a release note is not canonical semantics, and
an author name is not a method. Expertise contributes scoped evidence through exact artifacts; it
does not acquire semantic ownership by reputation or citation count.

The formal-model step is executable in
[`model_class_adjudication/`](./model_class_adjudication/README.md). A pipeline nomination case,
for example, is not an LP merely because one screening view resembles a flow network. Nonlinear
hydraulics, integrality, uncertainty, information revelation, simulation coupling and authority must
either remain inside the adjudicated model or be proved outside the exact subproblem boundary. The
result is a conjunction of facets such as `MILP + two-stage stochastic`, not one vendor-oriented
enum. A matched facet creates provider requirements; it never selects or qualifies a provider.

## The compiler never selects a library by name

A requirement states exact contracts, operations, guarantees, applicability, cardinality, binding
phase and evidence threshold. An offer states what one library or provider actually supplies,
including limits, configuration decisions, exclusions and conformance receipts. A binding exists
only after structural, semantic, policy, resource and evidence checks pass.

```text
same name       != compatible semantics
same trait      != satisfied law
same source ID  != qualified deployed connector
same operation  != same guarantees or failure model
green test      != evidence outside that test's exact scope
```

## Library boundary

A library is a reusable contribution, not an app or a product. Pure semantic and algorithmic
libraries have no I/O. Runtime libraries may implement effects, but they must accept explicit effect
intents and expose receipts; domain logic cannot silently reach environment state. All decision
points are typed data with authority, binding phase, allowed values, consequences and default law.

Products and solution packs package libraries, contexts, adapters, operating obligations and user
outcome promises. They do not become semantic owners merely because they package them.

A vertical solution pack therefore carries two separate declarations: the products it composes and
the provider-neutral method contracts its analytical cases require. `forecasting_workbench` may be
a product while `time_series` remains a method contract; `process_mining_workbench` may be a product
while OCEL and PM4Py remain carrier and library identities. The compiler refuses a product or
industry name used as an implicit method/provider selector.

## Optional model and agent extension

Generative models, LLMs and tool-using agents may offer optional capabilities through the same
requirement/offer/binding system. They are not forbidden from the atlas, but the dependency is
one-way: the extension imports core types, policies, tools, budgets and effect contracts; core
semantics never import the extension.

```text
model invocation -> output claim/proposal -> deterministic validation
                 -> authority decision -> tool/effect intent -> runtime receipt
```

The steps do not collapse. A model can assist extraction, mapping, planning, code generation or
analysis, but it cannot replace canonical adjudication, proof execution, resource admission,
authorization or effect recording. This keeps the hard deterministic work valid with or without an
agent.

An agent being available does not mean the work has been performed. Parsing, typechecking,
constraint solving, numerical execution, provider qualification, authorization and receipt
verification are explicit deterministic obligations. Agent output may request those mechanisms or
explain their evidence; it cannot stand in for their outputs.

Every use site records one modality posture: `PROHIBITED`, `OPTIONAL`,
`REQUIRED_BY_INTENT`, or `UNDETERMINED`. The default product architecture is deterministic-core
first. Removing an optional model/LLM/agent binding must leave a conformant path or a typed
`capability_unavailable` gap; it may never silently weaken semantics, validation or authority.
