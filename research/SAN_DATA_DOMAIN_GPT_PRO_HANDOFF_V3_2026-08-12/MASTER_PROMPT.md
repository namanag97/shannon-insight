# Research and implementation brief: universal data and analytics domain specification

## Assignment

Research, model, and implement a machine-readable specification of the data, data-engineering,
and analytics domain.

The specification will be the semantic foundation of a future compiler. A user will declare a
data or analytical requirement. The compiler will determine the meaning of the declaration,
validate it, identify missing information, select compatible capabilities, construct a logical
plan, bind the plan to an execution environment, and produce a reproducible solution package.

This assignment covers the domain foundation and a working compiler kernel. It does not require a
complete production data platform. It requires a model that can grow to that scope without
changing its fundamental semantics.

Use the supplied files as research inputs. Audit them before reuse. The prompt is authoritative
where an input uses a narrower scope or a conflicting model.

## Result

Produce a versioned repository containing:

1. a strategic and tactical domain model;
2. a stable semantic kernel;
3. open-world registries covering horizontal capabilities and vertical domains;
4. a canonical intermediate representation;
5. a Rust implementation of admission, validation, linking, diagnostics, and a minimal planning
   pipeline;
6. YAML authoring formats with schemas and examples;
7. researched catalogues of industries, analytical practices, data sources, data types, experts,
   specialist companies, and recent innovations;
8. coverage, provenance, conflict, decision, and gap records;
9. conformance tests and reproducible release artifacts;
10. a recurring review process that supports continued expansion without breaking existing
    meaning.

The result must contain usable artifacts and executable code. A report, plan, or taxonomy by
itself is not sufficient.

## Domain scope

The domain includes the complete path from a statement of need to an operated data or analytical
solution:

```text
domain need
  -> analytical or data intent
  -> source and evidence requirements
  -> acquisition and data engineering
  -> data products and semantic models
  -> analytical execution
  -> results and interpretation
  -> optional decision or operational use
  -> observation, maintenance, evolution, and retirement
```

The domain covers data sources, data contracts, movement, transformation, storage, computation,
analytics, orchestration, serving, governance, security, privacy, quality, lineage,
observability, reliability, cost, deployment, maintenance, and lifecycle management.

Analytics is not defined as metric computation. It is the set of practices used to examine data,
establish evidence, answer questions, discover structure, test claims, estimate uncertainty,
explain outcomes, anticipate possible futures, evaluate alternatives, and support decisions.
Analytical work may be confirmatory or exploratory. Its result may be a dataset, finding,
estimate, model, explanation, test, forecast, scenario, plan, visualization, evidence package,
decision input, or a refined question. An analytical result has no authority to create an
operational effect unless a separate control contract grants that authority.

The core scope excludes Generative AI, LLMs, RAG, foundation models, and agent-based systems.
Conventional machine learning may be represented as an optional bounded extension when required
for coverage. The core must remain usable without that extension.

## Required separation of concerns

Model the following concerns independently and connect them through typed relations:

| Concern | Meaning |
|---|---|
| Vertical domain | Industry, subindustry, organization, process, actor, asset, product, event, obligation, and domain vocabulary |
| Need | Business, scientific, regulatory, investigative, or operational purpose |
| Analytical intent | Question, subject, population, decision context, evidence threshold, uncertainty tolerance, and permitted use |
| Analytical practice | Method family, assumptions, prerequisites, operators, validity conditions, and interpretation rules |
| Data | Observation, record, signal, content, relationship, representation, semantics, quality, provenance, and rights |
| Engineering capability | Provider-neutral function used to acquire, move, transform, manage, compute, analyze, serve, or operate data |
| Logical plan | Composition of capabilities satisfying semantic and non-functional constraints |
| Physical binding | Products, engines, protocols, infrastructure, deployment topology, and environment configuration |
| Assurance | Security, privacy, governance, safety, quality, reliability, audit, and compliance obligations |
| Evidence | Source, claim, assumption, derivation, observation, validation, proof obligation, and confidence |
| Lifecycle | State, version, time semantics, change, correction, retention, supersession, and retirement |
| Ownership | Bounded-context authority, producer and consumer duties, team, jurisdiction, and external authority |

Do not collapse these concerns into a single hierarchy. Use faceted classification and typed
n-ary relations where a binary tree would lose meaning. Distinguish intent from method, method
from implementation, result from action, logical capability from provider product, and declared
data from observed data.

## Core semantic objects

Define precise, versioned contracts for at least the following objects.

### Declaration

A declaration states a desired data or analytical outcome and its constraints. It records the
requesting authority, purpose, subject, scope, expected result contract, available inputs,
required evidence, permitted uses, quality and timeliness requirements, governance constraints,
operating constraints, and unresolved choices.

A declaration can be incomplete. The compiler must represent missing information explicitly. It
must not invent domain meaning, causality, source semantics, acceptable risk, or authorization.

### Analytical practice

An analytical practice records its identity and aliases, questions it can address, input and
observation requirements, unit and population semantics, assumptions, method family, reusable
operators, uncertainty model, validity threats, refusal conditions, possible result contracts,
evaluation procedures, interpretation rules, and prohibited uses.

The classification must be faceted. A practice may be classified by purpose, reasoning mode,
evidence mode, mathematical structure, data shape, temporal mode, spatial mode, execution mode,
interaction mode, result kind, decision relationship, and domain applicability. These axes must
not be treated as mutually exclusive taxonomic levels.

### Analytical result

An analytical result records the question addressed, input versions, method and configuration,
assumptions, provenance, population and granularity, time and space semantics, uncertainty,
validity limits, evaluation evidence, result payload, interpretation, and permitted downstream
uses. Results that have different epistemic status must use different types.

### Source and data contract

A source contract records the system and object being observed, access interface, ownership,
change behavior, identity, schema, representation, time semantics, delivery guarantees, quality,
provenance, sensitivity, rights, retention, and operational characteristics.

A data contract records the semantic and operational conditions under which data is admissible
for a specified use. Raw source claims, admitted observations, reconciled facts, derived values,
and analytical results are distinct states.

### Capability

A capability is a provider-neutral function with typed inputs, outputs, preconditions,
postconditions, invariants, semantic effects, operational properties, evidence requirements,
compatibility rules, and failure modes. A capability is not a vendor, product, deployment, or
configuration file.

### Vertical pack

A vertical pack contains domain vocabulary, entities, events, processes, source patterns,
questions, analytical needs, constraints, policies, mappings, and reusable recipes for an
industry or subindustry. It binds domain meaning to horizontal capabilities without copying their
implementation.

### Solution plan

A solution plan is a typed composition of capabilities that satisfies a declaration. It records
unresolved obligations, assumptions, proofs, provider requirements, operational policies,
lineage, costs, risks, and expected result contracts. Logical planning and physical provider
binding are separate stages.

## Domain-driven design requirements

Use domain-driven design as the method for discovering meaning, authority, consistency, and
boundaries. Apply each item where it is semantically warranted and record a reason where it is not
applicable.

### Strategic model

- domain vision, scope, non-goals, and success criteria;
- subdomain classification as core, supporting, or generic;
- bounded contexts with explicit inside, outside, owner, authority, and invariants;
- ubiquitous language with definitions, aliases, ambiguity rules, and provenance;
- context map with upstream/downstream direction and relationship type;
- anti-corruption layers and boundary translations;
- published languages, compatibility policy, and semantic versioning;
- capability and responsibility maps;
- external authorities, standards, jurisdictions, and trust boundaries;
- assumptions, hotspots, open questions, and architecture decisions.

### Tactical model

- value objects, entities, identifiers, quantities, and units;
- aggregates, roots, consistency boundaries, and invariants;
- commands, queries, actors, and authorization;
- domain events, observations, corrections, and integration events;
- typed refusals and failure taxonomy;
- domain services, application services, policies, and specifications;
- repositories, ports, adapters, and factories;
- state machines and lifecycle transitions;
- reactions, sagas, process managers, compensation, and human checkpoints;
- projections and read models with consistency and freshness contracts;
- concurrency, idempotency, ordering, replay, and conflict semantics;
- time, provenance, evidence, uncertainty, and correction models;
- domain laws, examples, counterexamples, and event-storming flows.

### Executable model

- schemas and codecs for authored and published languages;
- normalized identifiers and canonical ordering;
- reference resolution, dependency, compatibility, and conflict rules;
- validation stages and typed diagnostic paths;
- proof and evidence obligations;
- source maps across compiler stages;
- migration, deprecation, supersession, and semantic diff;
- fixtures, property tests, hostile inputs, and conformance suites.

## Horizontal and vertical research coverage

Build a versioned, source-supported inventory of industries and subindustries. For each vertical,
model its principal capabilities, processes, entities, events, source-system families, analytical
needs, result uses, constraints, and assurance obligations. Cross-reference established external
classifications rather than creating an isolated industry hierarchy.

Build a granular analytical-practice registry. The initial research target is approximately 300
distinct practices, provided that each entry has a defensible boundary and evidence. Do not split
synonyms to reach a count. Record broader, narrower, related, composable, and commonly confused
practices. Report coverage by classification facet and source authority.

Build a source-system and data ontology covering source families, source objects, observation
processes, change semantics, interfaces, representations, structures, modalities, measurement
semantics, identity, time, space, quality, provenance, rights, and lifecycle. The ontology must
support new source types through registry extension without changing the semantic kernel.

Build a horizontal capability map for the complete data-engineering and analytical lifecycle.
For every proposed component, decide whether it belongs in the constitutional kernel, a Rust
library, a library module, a semantic type, a declarative registry, a schema, an operator, a
recipe, a provider binding, a runtime mechanism, a vertical pack, documentation, or a rejected or
duplicate category. Record the decision and reason.

Reconcile every item in the supplied context model and module proposals through this disposition
process. Preserve disagreements and unresolved questions. Do not accept supplied names, counts,
checksums, or validation claims without the corresponding evidence.

## People, organizations, and innovation research

Create an expert registry linked to analytical practices and domain problems. Each record must
state the person's relevant contribution, school or method, significant work, practical lesson,
scope, disputed claims where material, and supporting sources. Coverage is based on substantive
contribution rather than prominence.

Create a landscape of approximately 100 specialist analytics companies. Include companies whose
primary identity is an analytical product, method, or domain-specific analytical service. General
cloud, database, consulting, and enterprise-platform vendors may appear as provider or ecosystem
records but do not qualify as specialist analytics companies solely because they offer analytics
features. State the selection and ranking method; do not present an arbitrary list as a factual
“top 100.”

Research material innovations introduced or substantially advanced during the five years before
the research date. Exclude innovations whose essential mechanism depends on Generative AI, LLMs,
RAG, foundation models, or agents. For each innovation, record the previous limitation, mechanism,
novelty evidence, maturity, trade-offs, affected bounded contexts, and implementation relevance.

Derive the research strategy, terminology, queries, and source selection required to satisfy
these objectives. The lists in this brief define deliverables and boundaries, not a prescribed
search script.

## Evidence and completeness

Prefer primary sources and use secondary sources for discovery and triangulation. Store sources
separately from claims. Every material claim must identify its source, access date, source type,
authority, scope, evidence strength, and conflicts.

Use the following trust states consistently:

```text
hypothesis
research candidate
source-supported claim
structurally validated artifact
executable law
runtime-observed claim
independently attested claim
certified claim
```

The domain is open-ended. Completeness therefore consists of a closed constitutional kernel, an
extensible registry model, declared classification axes, external crosswalks, measurable coverage,
known gaps, and a recurring review process. Do not claim universal completeness from an item
count. Every coverage statement must name its assessed universe, date, exclusions, depth,
evidence threshold, and unmapped items.

## Rust, YAML, and intermediate representation

Use Rust for the admitted semantic model and compiler kernel. Evaluate the applicable stable Rust
language and standard-library features against the domain requirements. Record which features are
used, what invariant or boundary each supports, and why plausible alternatives were not used.
Separate compile-time guarantees from runtime validation, external evidence, and human policy.

Use YAML as a human authoring format for open-world definitions, mappings, contracts, policies,
recipes, provider capabilities, vertical packs, examples, and evidence references. YAML is
untrusted input. Parse it into raw document types and admit it into semantic types only after
schema, reference, compatibility, policy, and invariant validation. Strings are not substitutes
for domain types.

Implement a versioned canonical intermediate representation. A normalized typed hypergraph is the
default representation unless research establishes a better model. Maintain distinct stages:

```text
authored documents
  -> parsed documents
  -> admitted semantic graph
  -> normalized declaration IR
  -> resolved logical plan
  -> proof, evidence, and refusal state
  -> provider-bound physical plan
  -> deterministic solution package
```

Preserve source locations, provenance, versions, diagnostics, assumptions, and unresolved
obligations through every stage. Canonical serialization and package generation must be
deterministic.

## Required repository structure

Use or improve the following responsibility layout:

```text
README.md          mission, status, navigation, and commands
docs/              domain maps, vocabulary, laws, decisions, and coverage reports
research/          source, expert, company, innovation, conflict, and gap records
schemas/           authoring and published-language schemas
registries/        versioned horizontal registries
verticals/         industry and subindustry packs
crates/            Rust workspace for kernel, IR, linker, compiler, and CLI
tests/             fixtures, counterexamples, property, conformance, and determinism tests
tools/             validation, generation, coverage, migration, and packaging tools
iterations/        append-only iteration and decision ledger
artifacts/         manifests, hashes, and deterministic release packages
```

Generated and authored files must be distinguishable. The repository must state the source of
truth for every artifact.

## Execution method

Work in evidence-driven iterations. Each iteration must record:

- the question, gap, or suspected boundary failure;
- evidence examined;
- model or implementation change;
- accepted, rejected, or deferred decision and reason;
- artifacts changed;
- validation performed;
- coverage change;
- remaining conflicts and risks;
- next highest-information task.

Use substantially different vertical slices to test horizontal reuse and expose false
abstractions. Include differences in data shape, time behavior, physical versus digital process,
regulation, human investigation, uncertainty, and operational consequences. Treat supplied sports,
oil-and-gas, and telecom material as candidate tests, not as the organizing ontology.

Continue research and implementation through the available session. Do not stop after proposing a
plan. At a session boundary, leave a resumable checkpoint containing current status, exact
commands, completed and failed acceptance gates, unresolved decisions, coverage frontier, and the
next work queue.

## Acceptance criteria

The first foundation release is acceptable when:

1. the strategic, tactical, and executable models agree on boundaries and terminology;
2. every supplied context and proposed module has a traceable disposition;
3. the Rust workspace builds, formats, lints, and passes tests with pinned dependencies;
4. authored schemas, admitted Rust types, and canonical IR agree through conformance tests;
5. hostile and incomplete declarations produce typed, source-located diagnostics or refusals;
6. references, versions, dependencies, and conflicts are resolved explicitly;
7. canonical normalization and packaging reproduce identical hashes from identical inputs;
8. multiple unrelated verticals reuse horizontal capabilities without semantic leakage;
9. representative declarations cover several analytical intents and result contracts;
10. exploratory work produces an admissible investigation or study design rather than a
    fabricated answer;
11. analytical results cannot directly produce operational effects without an explicit,
    authorized, auditable control boundary;
12. every material claim and generated artifact has provenance and validation status;
13. coverage reports identify the assessed universe, evidence threshold, exclusions, and gaps;
14. at least one end-to-end example performs admission, normalization, linking, logical planning,
    refusal or proof handling, provider binding, and deterministic packaging;
15. a clean environment can reproduce the validation and release process from documented
    commands.

## Initial work sequence

1. Read and inventory every supplied file.
2. Produce a discrepancy report covering scope, terminology, boundaries, duplication, unsupported
   claims, missing artifacts, and validation status.
3. Establish the first version of the classification axes, bounded contexts, ubiquitous language,
   constitutional laws, and candidate-disposition rules.
4. Define the schemas for sources, claims, semantic objects, relations, and registries.
5. Implement the minimal Rust semantic kernel, YAML admission path, canonical IR, linker, typed
   diagnostics, and tests.
6. Exercise the kernel with unrelated declarations and vertical packs.
7. Expand the research registries and domain model, using failures and coverage gaps to select
   subsequent iterations.
8. Produce a deterministic release package and a resumable checkpoint.

Proceed without requesting routine implementation choices. Request human input only when a
policy, authority, risk tolerance, or domain definition cannot be derived and would materially
change the contract. Report uncertainty and gaps directly. Do not replace missing evidence or
implementation with narrative confidence.
