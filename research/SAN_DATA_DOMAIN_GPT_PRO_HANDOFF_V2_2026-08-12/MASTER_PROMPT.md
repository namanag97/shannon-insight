# Master prompt: discover and construct the declaration-to-data-solution domain

## Read this correction before doing anything else

Do **not** interpret this mission as building a KPI system, a metrics catalogue, an optimization
engine, or a solution for electricity per gigabyte. Those are narrow inhabitants of the domain.
They are not its organizing model.

The telecom electricity/GB document in this package is only an optional adversarial case with
which to test a sufficiently mature model. Do not organize the taxonomy, architecture, ontology,
compiler, examples, or research plan around it. Do not assume that every analytical request has a
known objective function, produces a metric, recommends an action, or can be “fixed.”

“Analytics” here includes the many disciplined ways in which people use data to describe,
inspect, explore, discover, explain, diagnose, compare, test, infer, estimate, predict, simulate,
optimize, investigate, audit, monitor, decide, and learn. Some analytical work is open-ended and
ends in evidence, findings, uncertainty, or a better question—not an automated decision.

## The mission

Discover, formalize, and implement a provider-neutral domain model of the entire horizontal
**data + data engineering + analytics** problem, together with extensible vertical domain packs.
The long-term system should let a person declare what data capability or analytical outcome they
need and compile that declaration, when it is sufficiently specified, into a valid solution made
from composable capabilities, configuration, contracts, and provider bindings. When it is not
sufficiently specified or cannot safely be compiled, the system must return precise questions,
refusals, assumptions, proof obligations, capability gaps, or a research/investigation plan.

The immediate job is not to pretend that this compiler already exists. The job is to create the
correct semantic foundation from which it can be built: bounded contexts, language, axes,
entities, value objects, laws, lifecycles, registries, contracts, intermediate representations,
linking rules, and a small executable neutral slice.

Treat this as a long-running research and engineering program. Do actual research and produce
actual artifacts. Do not stop after writing a roadmap, taxonomy essay, or architecture diagram.

## What success means

We want a compact, stable, constitutional metamodel and a set of open-world registries capable of
representing an indefinitely growing world:

```text
declarations of need
    + industry and organizational meaning
    + source-system and data semantics
    + analytical intent, method and evidence requirements
    + engineering, operational and governance constraints
    + available logical and physical capabilities
    + provider/environment bindings
              |
              v
   normalize -> validate -> resolve -> plan -> prove/refuse -> bind -> package
              |
              +--> executable solution where warranted
              +--> investigation/study design where the answer is not compilable
              +--> explicit questions, conflicts, assumptions and gaps otherwise
```

The system must be able to explain why a plan is admissible, what remains unproven, which facts
came from where, and which parts are reusable across industries.

## Do not collapse independent dimensions

At minimum, model these as orthogonal but linked axes. Determine whether further axes are needed.

1. **World and vertical semantics** — industries, subindustries, organizations, business
   capabilities, processes, assets, actors, products, places, resources, obligations and domain
   events.
2. **Questions and analytical intent** — what is being asked, why, for whom, at what decision or
   knowledge stage, with which acceptable uncertainty and consequence.
3. **Analytical practice** — modes of reasoning and analysis, their assumptions, inputs, methods,
   evidence, validity conditions, limitations, and possible outputs.
4. **Data reality** — source systems, observations, records, signals, content, relationships,
   events, files, streams, modalities, schemas, semantics, identity, time, space, quality,
   provenance, rights and change behavior.
5. **Data engineering lifecycle** — discover, connect, acquire, capture changes, transfer, parse,
   validate, clean, reconcile, integrate, transform, enrich, model, store, index, serve, observe,
   maintain, evolve, archive and dispose.
6. **Logical solution capabilities** — provider-neutral machines and libraries that can be
   composed into plans.
7. **Physical realization** — engines, products, protocols, formats, infrastructure, topology,
   deployment, performance, cost, energy, availability and operational constraints.
8. **Control and assurance** — security, privacy, governance, policy, contracts, quality,
   lineage, observability, reliability, audit, compliance, safety and human authorization.
9. **Lifecycle and time** — event time, observation time, valid time, transaction/recording time,
   processing time, publication time, version time, retention, expiry, freshness and correction.
10. **Evidence and epistemic status** — hypothesis, definition, observation, derived fact,
    estimate, assumption, model, claim, proof, validation, attestation and certification.
11. **Ownership and organizational boundaries** — bounded-context ownership, producer/consumer
    duties, data products, teams, jurisdictions and external authorities.
12. **Compilation status** — declared, admitted, normalized, linked, resolved, planned, proven,
    conditionally proven, refused, bound, deployed, observed and invalidated.

Never use one hierarchy where a faceted classification or typed hypergraph is required. A thing
may participate in several axes without becoming several incoherent copies.

## Analytics is not “metrics”

Research the full analytical landscape without assuming that a single traditional ladder such as
descriptive/diagnostic/predictive/prescriptive is exhaustive. It is one coarse projection only.
Build a faceted model that can distinguish, relate, and compose practices such as:

- profiling, summarization, measurement, reporting and semantic querying;
- visual, interactive, exploratory and discovery-oriented analysis;
- investigation, case analysis, root-cause analysis, fault isolation and forensic analysis;
- comparative, cohort, segmentation, pattern, association and sequence analysis;
- statistical estimation, uncertainty quantification, hypothesis testing and inference;
- experiments, quasi-experiments, causal discovery and causal effect estimation;
- forecasting, nowcasting, survival/reliability, risk and probabilistic analysis;
- anomaly, change, drift, fraud, abuse and rare-event analysis;
- process mining, process discovery, conformance checking and performance analysis;
- temporal, time-series, spatial, geospatial, graph, network and topology analysis;
- text, document, log, trace, image, audio, video, sensor and multimodal analysis using
  non-generative methods in the core;
- simulation, scenario, sensitivity, counterfactual, system-dynamics and digital-model analysis;
- optimization, scheduling, routing, allocation, planning, operations research and control;
- audit, reconciliation, lineage, compliance, quality and evidence analysis;
- monitoring, detection, alerting, observability and operational intelligence;
- decision analysis, decision support, recommendations and human-in-the-loop adjudication.

This list establishes breadth, not a closed enumeration and not a prescribed list of web search
queries. Derive the research program needed to discover missing schools, synonyms, distinctions,
assumptions, standards, expert communities, and boundary cases.

Do not model an analytics type as a name plus description. For every analytical practice, capture
at least:

```text
identity and aliases
purpose and questions answered
unit/subject of analysis
input data shapes and semantic prerequisites
observation and sampling model
method family and reusable operators
assumptions and identifiability conditions
required controls, baselines or comparators
time, space, population and granularity semantics
uncertainty and error model
validity threats and failure/refusal conditions
possible outputs and their epistemic status
interpretation and permitted/forbidden uses
evaluation/verification approach
operationalization requirements, if any
related, broader, narrower and commonly-confused practices
authoritative sources, seminal work, current experts and recent non-AI innovations
```

Analytical outputs are also a polymorphic family. They can include an admitted dataset, profile,
summary, statistic, metric, semantic result, table, report, visualization, dashboard, map, graph,
alert, anomaly, finding, explanation, evidence bundle, pattern, rule, segment, classification,
score, ranking, estimate, distribution, interval, test result, causal effect, forecast, scenario,
simulation trace, process model, conformance result, risk assessment, audit result, experiment
design, decision analysis, recommendation, optimization plan, operational plan, query service,
data product, workflow, or a well-formed unresolved question. Keep output kind separate from
method, intent, interface, and downstream action.

## Data and the preparation domain

Determine and name the bounded contexts that turn real-world source material into analytically
admissible data. Do not hide this behind the word “preprocessing.” Model the entire chain and its
contracts.

Create an extensible ontology of:

- source-system families and concrete source endpoints;
- systems of record, engagement, operation, observation, control and exchange;
- databases, APIs, applications, SaaS, files, content stores, devices, instruments, industrial
  systems, machines, networks, ledgers, external datasets, human collection and derived products;
- source objects such as tables, records, events, transactions, messages, logs, traces, metrics,
  documents, forms, images, audio, video, signals, samples, measurements, geographies, graphs,
  models and archives;
- representation, serialization, format, encoding, compression, protocol and transport;
- scalar/logical/physical types, structures, modality, dimensionality, cardinality, sparsity,
  order, hierarchy, relationships, topology and granularity;
- append, update, delete, correction, retraction, late arrival, duplication, reordering, replay,
  snapshot and slowly changing semantics;
- identity, keys, entity resolution, reference/master data and semantic alignment;
- missingness, censoring, truncation, noise, bias, error, lineage, provenance and quality;
- ownership, consent, purpose, sensitivity, residency, sovereignty, licensing, retention and
  deletion obligations.

Separate observed values from declared type, semantic role, physical representation, measurement
process and epistemic status. Distinguish a source claim from an admitted fact and a derived
analytical result. Preserve raw evidence where required; never silently convert uncertainty into
certainty.

## Horizontal capabilities and vertical packs

The horizontal layer contains reusable semantics and machines: contracts, connectors, change
capture, transport, parsing, quality, transformation, reconciliation, identity, temporal and
spatial handling, storage, indexing, query, computation, analytical operators, orchestration,
lineage, policy, observability, testing, packaging, deployment and maintenance.

The vertical layer contains domain meaning: industry vocabulary, entities, events, business
processes, questions, admissibility rules, source patterns, analytical recipes, constraints,
evidence requirements and policies. A sports pack and an oil-and-gas pack may bind the same
horizontal capabilities differently without copying their implementations.

Do not force every candidate into a Rust crate. For every proposed item, determine whether it is:

```text
constitutional law or invariant
bounded context
sovereign reusable library
module within a library
semantic type or value object
declarative definition or vocabulary term
catalog/registry entry
contract/schema
analytical method or operator
recipe/template/plan fragment
provider capability or binding
runtime mechanism or infrastructure concern
vertical-domain concept
documentation/evidence only
duplicate, composite, misplaced, or rejected
```

Reconcile the packaged 21-context model, 99-module proposal, analytics catalogue, data ontology,
composition model, and SSPEC proposal. Preserve disagreements and produce a disposition ledger;
do not merge by name or accept claimed counts as architectural truth.

## DDD is the discovery and ownership discipline

Use domain-driven design to decide meanings, boundaries, responsibilities and allowed
dependencies. For the whole domain and for every bounded context that survives the audit, cover
the applicable parts of this expanded contract:

### Strategic model

- domain vision, scope, non-goals and success questions;
- subdomain classification: core, supporting or generic, with build/buy/conform reasoning;
- bounded-context boundary: inside, outside, owner, authority and protected invariants;
- ubiquitous-language glossary with aliases, prohibited ambiguities and term provenance;
- context map with upstream/downstream and relationship patterns;
- anti-corruption layers and canonical translations at foreign boundaries;
- published languages, compatibility policy and semantic versioning;
- capability map, responsibility map and organizational ownership;
- external authorities, jurisdictions, standards and trust boundaries;
- assumptions, open questions, hotspots and decision records.

### Tactical model

- value objects, identifiers, quantities, units and admitted/validated constructors;
- entities, identity scopes and lifecycle;
- aggregates, roots, consistency boundaries and cross-aggregate references;
- invariants, preconditions, postconditions and impossible states;
- commands, queries and actors/authorities allowed to issue them;
- domain events, integration events, observations and corrections/retractions;
- exhaustive typed refusals and failure taxonomy;
- domain services, policies, specifications and rule composition;
- application use cases without domain rules leaking into orchestration;
- repositories/ports per aggregate root and adapters outside the domain core;
- factories/builders that enforce valid creation;
- state machines and legal/illegal transitions;
- policies/reactions, sagas/process managers, compensation and human checkpoints;
- read models/projections and their freshness/consistency contracts;
- concurrency, idempotency, deduplication, ordering and conflict semantics;
- time, provenance, evidence, uncertainty and correction models;
- non-functional domain laws: safety, privacy, security, reliability and auditability;
- event-storming flows and representative examples/counterexamples.

### Executable semantic model

- schemas and codecs for published languages;
- normalized identifiers and canonical ordering;
- dependency, compatibility and conflict rules;
- validation phases and typed diagnostic paths;
- linkable references and closure rules;
- source maps from authored declarations to normalized IR and plans;
- proof obligations and evidence categories;
- migration, deprecation, supersession and semantic-diff rules;
- testing laws, fixtures, counterexamples and conformance suites.

Not every DDD pattern must appear in every context. Record “not applicable” with a reason rather
than manufacturing aggregates, repositories, events, or sagas where they do not belong.

## Rust, YAML and intermediate representations

Rust is a strong implementation and verification substrate, not the domain model by itself. Use
its type system to make representable constraints explicit, while acknowledging which truths can
only be established by runtime checks, observation, human judgment, external authorities or
formal proof.

Use Rust where it materially helps:

- newtypes, enums and algebraic data types for vocabulary and closed local alternatives;
- generics, traits and associated types for lawful capability contracts;
- lifetimes and ownership where resource/borrowing semantics genuinely matter;
- visibility, modules, sealed traits and constructors for aggregate and invariant boundaries;
- typestates for real compile-time lifecycle transitions, without state explosion;
- `Result` and typed error/refusal enums for anticipated domain rejection;
- const generics or dimensional/unit types only where they improve correctness and ergonomics;
- serde codecs, schema generation, deterministic normalization and canonical serialization;
- property, model, fuzz, snapshot and conformance testing;
- feature flags only for legitimate optional extension boundaries, never semantic ambiguity.

Use human-authorable YAML for open-world definitions, registries, vertical packs, mappings,
contracts, policies, recipes, provider offers, examples and evidence references. Treat YAML as
untrusted input: parse into raw document types, resolve and validate into admitted semantic
values, and reject unknown, ambiguous, conflicting or unsupported meaning. Do not let stringly
typed YAML become the true domain.

Create a canonical versioned intermediate representation, preferably a normalized typed
hypergraph plus staged IRs, so that authored syntax, semantic meaning, logical planning, physical
binding and packaging remain separate:

```text
authoring documents
  -> parsed documents
  -> admitted semantic graph
  -> normalized declaration IR
  -> resolved logical capability plan
  -> proof/evidence obligations and refusals
  -> provider-bound physical plan
  -> deterministic deployable package
```

Every transformation must preserve source maps, diagnostics, provenance, versions and unresolved
obligations. No analytics result may directly mutate operational reality. Effects require an
explicit decision/control boundary, authorization, safety policy and auditable command.

## Research program

Design and execute the research needed to obtain broad horizontal and vertical coverage. Do not
wait for us to enumerate exact queries; discovering the right bodies of knowledge is part of the
work.

Prefer primary sources: standards, specifications, official technical documentation, scholarly
papers, seminal books, professional bodies, public reference models, authoritative taxonomies,
production engineering material and documented failures. Use secondary material for discovery
and triangulation. Record access date, source type, authority, claim supported, evidence strength,
scope and conflicts.

For every analytical subdomain, identify relevant experts and what can be learned from each—not
merely names or popularity. Capture their contribution, school/method, important work, operational
lesson, disputed boundary, applicable artifacts and sources. Likewise catalogue analytics-focused
companies only when their product or research supplies useful evidence about a capability or
market boundary. Do not treat broad cloud/platform vendors as “pure analytics companies,” and do
not use company marketing as ontology.

Research core innovations from the previous five years relative to the research date, excluding
Generative AI, LLMs, RAG, foundation-model agents and features whose essential mechanism depends
on them. Record the prior limitation, actual mechanism, evidence of novelty, maturity, tradeoffs,
affected bounded contexts, and whether the innovation changes semantics, algorithms, execution,
operations, governance or only packaging.

The core must remain non-AI/LLM-based. Classical statistics, causal methods, process mining,
operations research, rules, signal processing, simulation and deterministic/probabilistic
algorithms are first-class. Conventional machine learning may be represented only as an optional,
well-bounded extension if necessary for completeness. Generative AI/LLM/RAG/agent capabilities
must be quarantined and may not become a dependency of the core model or research method.

## Required machine-readable registries and artifacts

Produce versioned schemas and populated seed registries for at least:

- industry and subindustry hierarchy with external crosswalks;
- domain capabilities, processes, entities, events, resources and constraints;
- business/research/operational questions and analytical needs;
- analytical practices, method families, prerequisites, outputs and validity threats;
- source-system families, source objects, interfaces and change semantics;
- data types, structures, modalities, measurement/observation models and quality semantics;
- formats, protocols, representations and transports;
- connectors, pipeline stages, transformations, reconciliation and data-product definitions;
- storage, indexing, serving, compute, orchestration and operational capabilities;
- security, privacy, governance, lineage, reliability and lifecycle policies;
- horizontal library/module candidates with dispositions and dependency edges;
- provider capabilities and replaceable provider bindings;
- vertical packs and their mappings to the horizontal model;
- commands, events, refusals, states, invariants, laws and proof obligations;
- experts, organizations, companies, standards, sources and recent non-AI innovations;
- conflicts, unknowns, unsupported claims, rejected candidates and coverage gaps.

Represent relations explicitly. A normalized hypergraph or an equivalent typed relation model
must support n-ary facts such as “this method applied to this population and observation model,
under these assumptions, can produce this output for this intent with these validity threats.”

## Honest completeness

“All industries,” “all sources,” and “all analytics” cannot honestly be a frozen finite list.
Model bounded completeness:

```text
small closed constitutional kernel
  + versioned open-world registries
  + declared classification axes and external crosswalks
  + evidence and confidence per claim
  + known-unknown and gap registers
  + measurable coverage reports
  + deterministic recurring review and supersession process
```

Never claim “complete” because a target count was reached. Counts are inventory signals, not
semantic proof. State the universe or standard against which coverage was assessed, the date,
exclusions, unmapped items, depth, evidence threshold and validation status.

## Iteration and convergence

Maintain an append-only iteration ledger. Each iteration must record:

```text
question or suspected boundary failure
evidence examined
model change proposed
accepted/rejected/deferred decision and reason
artifacts changed
tests or validations run
coverage movement
new conflicts, unknowns and risks
next highest-information experiment
```

Use several deliberately different vertical slices to expose false abstractions. Include domains
with transactions, physical processes, regulated evidence, human cases, spatial/temporal signals,
networks and unstructured records. Reuse the same horizontal foundation and show exactly what is
vertical configuration versus a genuinely missing horizontal capability.

The telecom energy document may be used late as one optional stress test of physical semantics,
optimization and control boundaries. It must not be the first slice, the default example, or the
definition of success.

## Deliverable structure

Produce a deterministic, resumable repository/package with at least:

```text
README.md                         mission, status, navigation and exact commands
docs/                             context maps, vocabulary, laws, decisions and coverage reports
research/                         source ledger, expert/innovation records and conflict register
schemas/                          authoring and published-language schemas
registries/                       versioned horizontal open-world registries
verticals/                        industry/domain packs and examples
crates/                           Rust workspace for semantic kernel, IR, linker, compiler and CLI
tests/                            fixtures, counterexamples, conformance and determinism tests
tools/                            generators, validators, coverage and packaging tools
iterations/                       append-only convergence ledger and checkpoints
artifacts/                        generated manifests, hashes and deterministic release packages
```

Names may change if the architecture justifies it, but the responsibilities and generated-versus-
authored distinction must remain explicit.

## Acceptance gates

Do not report the foundation as buildable until all applicable gates pass:

1. The Rust workspace builds, formats, lints and tests with pinned toolchain/dependencies.
2. YAML/JSON schemas and Rust admitted types agree through explicit conformance tests.
3. Hostile inputs prove that invalid identifiers, units, time semantics, references, transitions,
   capabilities and unsafe effects are rejected with typed, located diagnostics.
4. Linking is closed: references resolve, dependencies are acyclic where required, versions are
   compatible, conflicts are explicit, and no undeclared capability is smuggled into a plan.
5. Canonical normalization and packaging are deterministic and hashes reproduce.
6. Each legacy 21-context and proposed 99-module item has a traceable disposition.
7. Multiple unlike verticals reuse horizontal capabilities without copied implementation or
   semantic leakage.
8. Representative declarations cover different analytical intents and output kinds—not merely
   metrics, dashboards or optimization.
9. Open-ended exploratory/investigative work compiles only to an admissible study or workspace,
   never to a fabricated answer.
10. Analytical outputs cannot directly cause operational effects without explicit authorization,
    policy, safety and evidence boundaries.
11. Coverage reports state their assessed universe, date, evidence bar, exclusions and gaps.
12. Every material claim has provenance and a trust status; unverified external claims remain
    labeled as such.
13. At least one end-to-end neutral slice demonstrates declaration, admission, linking, logical
    planning, proof/refusal, provider binding and deterministic package output.
14. A clean-machine reproduction command validates the package without relying on hidden state.

Passing the packaged legacy validators proves only that the existing drafts are structurally
consistent. It does not establish the acceptance gates above.

## How to begin

1. Read every packaged input and produce an evidence-aware discrepancy report. State explicitly
   where prior material confused analytics with metrics, optimization, control, infrastructure or
   provider products.
2. Inventory all claims and artifacts by provenance and validation status. Do not invent the
   missing archive referenced by the 99-module prose report.
3. Derive a research strategy and initial classification axes from the mission; do not merely
   repeat the lists in this prompt.
4. Propose and test the smallest constitutional metamodel that can represent the independent axes
   without encoding one industry, technology or analytical school.
5. Reconcile the existing decompositions through an explicit candidate-disposition ledger.
6. Implement the smallest neutral Rust + YAML + canonical-IR slice and its tests.
7. Exercise it with several unlike declarations and verticals. Use failures to drive the next
   iteration.
8. Continue research and implementation until the time/session boundary, then produce a resumable
   checkpoint, deterministic downloadable artifact package, hashes, exact commands, honest
   acceptance status, coverage frontier and next highest-information tasks.

Proceed autonomously through ordinary modelling and implementation decisions. Ask only when a
missing human policy or authority would materially change the domain contract. Never substitute a
confident narrative for executable artifacts, evidence, refusals, tests, or an honest gap.
