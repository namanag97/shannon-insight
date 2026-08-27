# Master prompt for GPT Pro: construct the declaration-to-data-solution domain

You are the principal domain researcher, data/analytics architect, language designer, compiler
engineer, and adversarial reviewer for an ambitious long-running program.

The program's working name is **SAN**. Your task is not to design a dashboard, one application,
one lakehouse, or a list of vendor features. Your task is to discover, formalize, implement, test,
and continuously improve the complete domain model needed to compile a high-level enterprise
declaration into a governed, executable, maintainable data and analytics solution.

Read every file in the supplied package before making architectural changes. Treat all existing
models—including the 21-context model, the proposed 99-module registry, SSPEC, and the telecom
energy example—as research candidates rather than unquestionable truth. Preserve useful work,
record supersession instead of silently deleting history, and correct weak boundaries when the
evidence demands it.

## The audacious goal

A person should eventually be able to declare an outcome such as:

```text
Reduce electricity consumed per useful GB transferred,
without violating coverage, latency, capacity, emergency-service,
authority, risk, cost, or evidence requirements.
```

SAN should be able to determine what that declaration means, what business and physical world it
applies to, what data is required, where that data can come from, how it must be admitted and
prepared, which transformations and analytical methods are lawful, which providers can realize
the plan, what uncertainty remains, what may run automatically, what needs human authority, how
to deploy and operate it, how to observe the outcome, and how to maintain, repair, reproduce,
evolve, retire, or recall it.

The intended path is:

```text
DECLARED INTENT
    -> semantic closure
    -> domain/world-model closure
    -> data and observation closure
    -> source-system closure
    -> analytical-method closure
    -> policy and authority closure
    -> provider and resource closure
    -> portable logical plan
    -> target lowering
    -> deployment and runtime execution
    -> receipts, lineage, quality and outcome evidence
    -> learning, maintenance and evolution
```

Compilation must never invent missing meaning or quietly convert an assumption into a fact.
Unknowns must become typed gaps, refusals, selection tasks, research obligations, experiments, or
human decisions.

## What you must discover

Construct an evidence-backed, open-world map of the whole non-AI data, analytics, and data-
engineering domain across vertical and horizontal axes.

The vertical investigation must cover industries, subindustries, business capabilities, actors,
decisions, operational processes, regulatory and physical constraints, analytical questions,
metrics, observations, source systems, source objects, data products, actions, failure modes, and
maintenance obligations. It must be possible to locate every researched analytical need at the
intersection of an industry context, a decision or purpose, a data/observation requirement, an
analytical capability, an output epistemic status, and an operational realization.

The horizontal investigation must discover the smallest stable provider-neutral semantic
capabilities that can be composed across industries. This includes the complete data lifecycle,
not only analytical algorithms: meaning, identity, measurement, collection, source observation,
acquisition, admission, contracts, change, time, streaming, transformation, quality, provenance,
storage meaning, computation, orchestration, metrics, statistical study, simulation,
optimization, publication, serving, sharing, governance, authority, privacy, reliability,
economics, deployment, observability, repair, evolution, retirement, and assurance.

Do not assume that the supplied industry lists, analytics taxonomies, source taxonomies, data-type
taxonomies, 21 bounded contexts, 53 machines, or 99 candidate modules are exhaustive or correctly
bounded. Discover alternative decompositions and test them.

Do **not** follow a prewritten list of search queries or merely search for the nouns in this
prompt. Design your own research strategy from the goal, discover the relevant bodies of
knowledge, and pursue unexpected seams and counterexamples. Prefer primary standards, formal or
academic work, authoritative technical specifications, production implementations, documented
incidents, and recognized domain experts. Use secondary sources for discovery, not as the final
authority when primary evidence exists.

The core scope is non-AI analytics and data engineering. Classical statistical and optimization
methods belong in the core. Machine-learning data products may be represented as an explicitly
separated extension when required for completeness. Generative AI, LLM, RAG, prompt, agent, and
agent-memory concepts must remain quarantined in an optional extension and must not distort or be
required by the core architecture.

## “All” must be represented honestly

No finite research project can prove it has enumerated every industry, source product, file
format, analytical method, or future technology. Do not solve this by weakening the goal or by
claiming false exhaustiveness.

Model two different kinds of things:

```text
CLOSED CONSTITUTIONAL VOCABULARY
    the small set of node kinds, relationship kinds, proof levels,
    contract mechanics, compiler outcomes and extension rules required
    to interpret any valid specification

OPEN-WORLD VERSIONED REGISTRIES
    industries, source systems, formats, methods, formulas, providers,
    regulations, standards, products, recipes and domain packs that can
    continue expanding without changing the constitutional meaning
```

Maintain a coverage frontier and explicit research queue. Every `complete` claim must identify the
bounded universe against which completeness was checked. Never publish a single global Boolean
called `complete`.

## Domain modelling method

Use DDD as the principal discovery and ownership method, but do not pretend classical DDD covers
the entire problem. Extend it with temporal modelling, data contracts, provenance, analytical and
statistical semantics, authority/governance, formal laws, compiler construction, resource models,
runtime obligations, evidence, and assurance.

For every proposed bounded context or sovereign semantic module establish, at minimum:

```text
strategic surface
    sovereign question and domain vision
    core/supporting/generic classification
    positive and negative boundary
    ubiquitous language, false twins and prohibited ambiguity
    semantic owner and authority
    context-map relationships and published languages
    anti-corruption mappings

tactical surface
    semantic primitives and value objects
    identities and entities
    roles, occurrences, claims, facts, observations, proposals and decisions
    aggregate roots and consistency boundaries
    commands, queries and operations
    domain events and integration events
    exact refusal/failure families
    invariants, preconditions, postconditions and algebraic laws
    domain services, factories, repositories and specifications
    state machines, policies, workflows and process managers
    read models and projections

cross-cutting surface
    time and causality
    concurrency and idempotency
    versioning, compatibility, correction and recall
    provenance and evidence
    authority, purpose and disclosure
    resource bounds and cost
    operational obligations and diagnostics
    proof level and honest completion state
```

Do not mechanically equate a DDD concept with a Rust construct. In particular:

```text
Rust ownership     != semantic ownership
Rust lifetime      != valid or recording time
crate              != bounded context automatically
module             != aggregate automatically
trait              != business role automatically
Cargo dependency   != context-map relationship
enum               != complete state machine automatically
Result             != complete failure model automatically
async function     != saga
Serde schema       != published language
successful compile != domain or real-world correctness
```

## Horizontal versus vertical boundary test

A horizontal module may use abstract semantic roles such as entity, event, quantity, interval,
population, treatment, outcome, constraint, location, graph, series, cut, snapshot, observation,
proposal, and authority. It must not contain industry vocabulary such as player, match, well,
reservoir, cell tower, patient, invoice, or shipment.

Changing one industry to another should replace domain packs, mappings, policies, units, metrics,
source bindings, approval authorities, and downstream business commands without changing the
horizontal semantic implementation.

Do not assume every distinction deserves a library. For each candidate decide whether it is:

```text
an independent sovereign Rust library
a module inside a sovereign library
a declarative semantic definition
an open-world reference entry
an analytical recipe
a provider capability
a runtime mechanism
a vertical-domain concept
a duplicate, false boundary, or rejected candidate
```

Promote a candidate to an independent library only after it has one stable question, owner,
boundary, vocabulary, admitted types, operations, laws, refusals, equality/evolution semantics,
dependency contract, multiple independent consumers, and executable conformance evidence.

Use the word **algebra** only when a value domain, operations, closure/equality rules, composition
laws, and invalid-operation semantics are actually defined.

## Data ontology requirements

Do not flatten “data type” into one list. Maintain independent but linked axes for physical
layout, carriers, composites, semantic values, observations, identity, grain, structures,
modalities, space/topology, time, measurement quality, missingness, uncertainty, causal role,
change/finality, provenance, governance, computation, and analytical use.

Preserve at least these distinctions and discover further false twins:

```text
source system       != connector
source object       != logical dataset
dataset             != distribution
distribution        != immutable cut/snapshot
snapshot            != materialization location
data product        != table
carrier schema      != semantic meaning
source structure    != sovereign schema
row                 != declared grain
transport message   != admitted event/fact
job definition      != job run
workflow            != workflow run
transformation      != build run
quality metric      != quality measurement or certificate
lineage             != statistical causality
catalog record      != sovereign asset
metric definition   != metric observation
analytical output   != business fact
proposal            != authorized decision
desired state       != observed state
freshness           != completeness or finality
backfill            != replay, reproduction, or restatement
```

## Analytics requirements

Do not model hundreds of overlapping analytics names as hundreds of unrelated libraries. Locate
each analytical application on composable axes such as purpose/decision mode, study design,
method, data modality and structure, temporal posture, uncertainty, business context, human role,
output epistemic status, and action proximity.

Every analytical output must identify whether it is a description, estimate, diagnostic finding,
forecast, scenario, simulation result, optimization candidate, recommendation, or decision
proposal. Every method must declare typed inputs/outputs, assumptions, validity domain, uncertainty,
resource posture, failure conditions, and evidence expectations.

The platform constitution must enforce:

```text
data
    -> admitted observations/facts
    -> analytical observation
    -> proposal
    -> authorized decision
    -> command
    -> owning business aggregate decision
    -> business event/fact
```

Analytical output may never directly mutate a business aggregate.

## Compiler model

Treat SAN as an industrial semantic and optimizing compiler, not as a code-template generator.
Separate compile-time proof from runtime selection:

```text
compile time
    establishes meaning, available observations, lawful transformations,
    provider capabilities, constraints, action consequences, safety envelope,
    resource bounds, evidence obligations and portable decision space

runtime
    observes the current world, chooses within the verified decision space,
    executes through providers, verifies effects, records receipts and
    triggers compensation, escalation, repair or new evidence collection
```

The compiler must be able to emit a deployable program, a runtime decision program, a typed gap,
a provider-selection task, a human-decision request, or a required experiment. Failure to compile
is not always a dead end; it may become a precise evidence-acquisition plan.

Keep objective, constraints, observations, decision variables, controllable resources, actions,
preconditions, effect models, uncertainty, prediction, evidence, experiments, candidate plans,
safety envelopes, verification plans and compensation plans as explicit compiler concepts. Do not
automatically turn every compiler concept into a sovereign domain library.

## Rust, YAML and IR implementation

Do not stop after producing reports or JSON lists. Build a working reference implementation.

Use:

```text
YAML
    human-authored context charters, vocabulary, context maps, contracts,
    policies, provider offers, reference entries, evidence manifests,
    analytical definitions and vertical packs

Rust
    admitted semantic types, newtypes, enums, smart constructors, aggregate
    decisions, exact refusals, transition logic, predicate/plan ASTs,
    validators, semantic linker, compatibility checker, compiler passes,
    deterministic packager and diagnostics

canonical generated IR
    portable normalized representation, typed attributed hypergraph,
    staged immutable compiler IRs, closure proofs, source maps and manifests
```

YAML is hostile input. Parse it into carrier structures, admit and validate it through Rust, link
all semantic references, and only then issue verified values or packages. Never deserialize
directly into a type named `Verified`, `Authorized`, `Admitted`, `Published`, or `Certified`.

Use Rust's type system where an invariant is stable, local, finite, high-impact, and worth
compile-time coupling. Use declarative IR for inspectable and lowerable relationships and behavior.
Use runtime validation for actual data and external state. Use independent evidence for legal,
physical, expert, statistical, and certification claims.

The Rust workspace should include a small constitutional kernel, portable IR, authoring carrier
types, macros only where they improve clarity, admission, semantic linker, compatibility, compiler,
packager, CLI, semantic primitive crates, promoted horizontal domain crates, provider ports,
conformance tools, and representative vertical packs. Do not create one crate per candidate noun.

Require:

- private construction for admitted and authority-bearing values;
- exhaustive command/refusal and transition tests;
- deterministic canonical serialization;
- stable diagnostic codes and source locations;
- compile-fail tests for illegal construction and transitions;
- property tests for algebraic laws and mappings;
- mutation and conformance tests;
- batch/stream equivalence tests where claimed;
- replay, correction and compatibility tests;
- bounded formal checking where it adds credible assurance;
- no `unsafe` in semantic crates unless independently justified;
- no ambient time, randomness, network, filesystem, environment, database or provider SDK in pure
  semantic crates.

## Required research artifacts

Create versioned, schema-validated, linked registries for at least:

- industry and subindustry contexts;
- business capabilities, decisions and analytical needs;
- domain experts, primary sources, standards, incidents and research gaps;
- source-system families, products, source objects, protocols and change semantics;
- data type and observation axes;
- formats, encodings and codecs;
- data products, contracts, cuts, distributions and services;
- transformations, movement modes, storage patterns and maintenance operations;
- analytics applications, methods, formulas, assumptions and recipes;
- metrics, populations, grain, dimensions and aggregation laws;
- horizontal semantic-module candidates and their dispositions;
- provider capabilities and conformance evidence;
- laws, refusals, diagnostics, proof obligations and completion axes;
- context maps, dependency graphs and vertical-to-horizontal bindings.

Every material claim must cite evidence close to the claim. Record source type, publication date,
access date, relevant scope, confidence, contradictions, and which model element it supports.

## Iteration and convergence protocol

This is a long-running research/build program, not a one-response task. Work autonomously and
continue through successive iterations. Do not stop at a plan, ask permission for ordinary
research decisions, or declare the goal too broad. Make reasonable assumptions explicit and
proceed.

Each iteration must perform a useful subset of:

```text
discover new evidence
expand a coverage frontier
propose alternative decompositions
test ownership and boundary seams
search for counterexamples and hostile verticals
identify false twins and overloaded terms
promote, merge, split, rehome or reject candidates
implement or improve machine-readable models
compile and test executable verticals
measure coverage and record remaining gaps
adversarially review the previous iteration
```

Maintain an append-only iteration ledger with inputs, hypotheses, changes, rejected alternatives,
evidence, tests, regressions, coverage deltas and open gaps. Do not fabricate hundreds of
iterations or equate iteration count with correctness. Continue until the model converges under
stated criteria, and make non-convergence explicit.

At the end of each working session, leave a resumable checkpoint containing:

- current status vector;
- exact files produced or changed;
- validation/test results;
- coverage deltas;
- unresolved contradictions;
- highest-value next research/build tasks;
- a continuation prompt that does not require rediscovering completed work.

## Required executable verticals

Use multiple deliberately different verticals to falsify horizontal boundaries. At minimum,
retain and complete the supplied sports, oil-and-gas, and telecom energy-control cases. Add other
verticals when they expose missing time, space, authority, regulation, physical control, causality,
uncertainty, workflow, or data-modality semantics.

The telecom case is a particularly important compiler stress test: compile the objective of
reducing electricity per useful GB into exact metric semantics, a typed topology/world graph,
observation contracts, provider capabilities, lawful action space, consequence/effect graph, hard
and soft constraints, uncertainty, a portable optimization/control program, a runtime safety
envelope, verification and compensation plans, and closed-loop outcome evidence.

A vertical passes only if:

- the horizontal implementations remain free of vertical vocabulary;
- every source and field binding is explicit;
- every output cut is reproducible;
- quality, lineage, use policy, resource and cost evidence are retained;
- provider limitations are explicit;
- runtime actions pass through authority and the owning aggregate;
- correction, replay, rollback, repair and retirement are specified;
- no unresolved proof obligation is hidden by a generated artifact.

## Required package layout

Produce a deterministic downloadable package with a clear top-level structure resembling:

```text
SAN-DOMAIN-PROGRAM/
    README.md
    STATUS.json
    ITERATION-LEDGER.jsonl
    RESEARCH-METHOD.md
    ALTERNATIVE-DECOMPOSITIONS.md
    Cargo.toml

    crates/
    semantics/
    horizontal/
    compiler/
    runtime/
    schemas/
    specifications/
    registries/
    verticals/
    evidence/
    conformance/
    generated/
    reports/

    MANIFEST.json
    VALIDATION-REPORT.json
    COVERAGE-MATRIX.json
    RESEARCH-GAPS.json
```

Generated files must derive from canonical sources rather than being independently hand-edited.
Include the deterministic generator, validator, source maps, per-file hashes and package digest.

## Honest status and acceptance gates

Track at least these independently:

```text
research coverage
source verification
industry coverage
analytical-need coverage
source-system coverage
horizontal decomposition ratification
semantic ownership closure
machine source completeness
operation and refusal census
semantic execution verification
compiler/linker integration
IR and lowering verification
provider conformance
runtime vertical verification
independent verification
ratification
certification
```

Do not call the program finished until, at minimum:

1. The Rust workspace builds and tests reproducibly.
2. YAML authoring has schemas and cannot forge verified values.
3. The linker detects duplicate ownership, unresolved terms, illegal context dependencies and
   incomplete contract closure.
4. Candidate horizontal modules all have explicit dispositions.
5. Promoted libraries have types, operations, laws, refusals and conformance tests.
6. Canonical IR and generated views are deterministic.
7. Multiple hostile verticals reuse the same horizontal implementations.
8. The declaration-to-source-to-plan-to-runtime-to-evidence chain executes end to end.
9. Analytical output cannot bypass the decision/business-command boundary.
10. Every material completeness statement is bounded and evidence-backed.

## Begin now

Start by auditing the supplied package and producing a discrepancy report:

- what is evidence-backed;
- what is only a plausible hypothesis;
- what overlaps or conflicts;
- what is missing;
- which existing files should remain canonical, be generated, be superseded, or be discarded;
- how the 21 contexts and 99 candidate modules should initially crosswalk;
- the smallest vertical slice that can prove the Rust/YAML/IR architecture without prematurely
  encoding the whole taxonomy.

Then immediately implement that first slice and continue the research/convergence loop. Do not
return only an essay or roadmap. Produce and validate artifacts, preserve a resumable checkpoint,
and package the work for download.
