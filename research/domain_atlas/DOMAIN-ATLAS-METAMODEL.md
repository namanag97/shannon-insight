# Bounded-context atlas metamodel

## 1. Why the context atlas comes first

A product can combine several bounded contexts, and one bounded context can contribute semantics
to several products. Product packaging therefore cannot decide who owns terms, invariants,
authority or state. That ownership must be established first.

```text
bounded context = language + semantic owner + laws + state/behavior + published contracts
product         = user + job + outcome + adoption/lifecycle/SLO/exit promise
```

## 2. Candidate bounded-context identity

Every context candidate must declare:

1. Stable suffix-free identity and separate edition.
2. One sovereign question.
3. Positive and negative charter.
4. Core/supporting/generic classification.
5. Ubiquitous language, homonyms, false twins and prohibited terms.
6. Imported concepts and their semantic owners.
7. Values, entities, aggregates, roles and identities where applicable.
8. Commands, queries, events, policies and external-effect intents.
9. Total state machines and refusal precedence.
10. Time, ordering, concurrency and idempotency semantics.
11. Laws, invariants, algebraic properties and executable oracles.
12. Published language and anti-corruption translations.
13. Requirements, offers, cardinalities and binding phases.
14. Authority, purpose, tenancy, jurisdiction and disclosure posture.
15. Resource bounds and failure model.
16. Compatibility, migration, replay, correction, recall and exit.
17. Compiler queries, IR representation and lowering obligations where applicable.
18. Runtime receipts, evidence, diagnostics and completion axes.

The 110-point product truth contract is not copied blindly into each context. A context uses the
universal sovereign-specification contract plus a typed applicability profile.

## 3. Context split test

Split a candidate when one or more of these cannot be reconciled under one language and owner:

- the same word has incompatible meanings or equality laws;
- commands require different authorities or transactional boundaries;
- state machines have independent lifecycles or correction semantics;
- time/order/finality meanings differ;
- failure or refusal precedence differs materially;
- one part must remain pure while another owns I/O or runtime state;
- implementations must be replaceable behind a published language; or
- the context would otherwise own both a claim and its independent appraisal.

## 4. Context merge test

Merge candidates when their split is only a vendor feature, team, crate, UI, deployment process,
storage table, configuration option or synonym and they share the same language, owner, laws and
lifecycle.

Individual formulas, connector brands, file formats, statistical methods and industry metrics
normally belong to open registries governed by a context. They become contexts only when they
introduce a distinct semantic algebra, authority or lifecycle.

## 5. Candidate record shape

```yaml
context_id: dat.metric
edition: 1
status: hypothesis
family: analytical-semantics
sovereign_question: >
  What measure over what population, grain, filters, dimensions and time does this metric mean?
positive_charter: []
negative_charter: []
ubiquitous_language: []
imports: []
exports: []
aggregates: []
operations: []
events: []
states: []
invariants: []
refusals: []
time_model: []
authority_model: []
resource_model: []
compatibility: []
compiler_surface: []
evidence: []
coverage: {}
```

## 6. Context-map relationship vocabulary

```text
upstream_downstream
customer_supplier
conformist
anti_corruption_layer
open_host_service
published_language
shared_kernel              exceptional and explicitly governed
separate_ways
independent_appraisal
authority_delegation
evidence_submission
compiler_requirement
provider_offer
runtime_receipt
```

## 7. Closed versus open registries

Closed, compiler-owned metamodels include identity, editions, ownership, requirement/offer
relations, applicability, evidence status, gaps and compilation outcomes.

Open registries include industries, source products, connectors, formula definitions, statistical
methods, storage engines, query providers, codecs, visualizations and deployment targets. An open
registry is still versioned and governed; “open” means extensible without changing the compiler's
closed vocabulary.

