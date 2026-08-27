# Candidate global bounded-context map and ACL corpus

This folder is a deterministic, machine-readable **candidate** map of language boundaries across
the researched data and analytics universes. It is neither a global-completeness claim nor a list
of products. It answers a narrower compiler question:

> When one independently owned language must cross into another, which exact contract, authority,
> translation, loss, refusal, version and evidence obligations make the crossing admissible?

The corpus samples 144 context candidates across 24 planes and binds 308 typed context-map
relations one-to-one to 308 anti-corruption/boundary decisions. A name never proves synonymy, identity,
ownership, authority or compatibility. Every record remains `candidate_open_world`.

`input-alignments.jsonl` consumes the inherited context-candidate inventory conservatively: only
38 exact seed tokens align after the declared underscore/hyphen ID encoding. These records inherit
neither synonymy, identity, ownership nor adjudication.

## The map is not a stack

The same context can be upstream for one contract, downstream for another, and an independent
appraiser for a third. Products and providers sit outside semantic ownership.

```text
                         candidate authority roles
                                   |
                         own language + laws
                                   v
  +----------------+     published language      +----------------+
  | source context | ---------------------------> | local context  |
  | id + edition   |                              | id + edition   |
  +----------------+                              +----------------+
          |                                                ^
          | submits claim/evidence                         | appraises / admits
          v                                                |
  +----------------+      independent appraisal    +----------------+
  | evidence issuer| ----------------------------> | decision owner |
  +----------------+                               +----------------+
          |
          | foreign contract
          v
  +-----------------------------------------------------------------+
  | anti-corruption decision                                        |
  | exact input edition -> mapping -> local import contract          |
  | totality | residual | loss | identity | time | grain | refusal   |
  +-----------------------------------------------------------------+
          |
          | requirement (not vendor name)
          v
  +----------------+   proofed binding   +--------------------------+
  | pure libraries | <-----------------> | target/provider offers   |
  +----------------+                     +--------------------------+
          ^                                          |
          | packaged, never semantically owned       | occurrence receipt
          |                                          v
  +----------------+                     +--------------------------+
  | product / suite|                     | deployed occurrence      |
  +----------------+                     +--------------------------+
```

The graph is therefore a hypergraph over several independent directions:

```text
meaning:      semantic owner -> published language -> local admitted meaning
authority:    accountable authority -> delegation -> decision -> enforcement
evidence:     issuer -> claim/evidence -> independent appraiser -> verdict
dependency:   requirement -> offer -> qualification -> binding -> occurrence
time:         source validity -> observation/recording -> decision -> replay
identity:     foreign identifier -> match candidate -> authorized decision
grain:        source grain -> mapping cardinality -> analytical grain -> result
version:      source edition -> ACL edition -> local edition -> migration/recall
```

## What one relation records

`relations.jsonl` does not contain an unqualified `A -> B`. Each edge fixes:

- context identity and edition on both ends;
- upstream/downstream roles and one DDD relationship type;
- semantic-owner context, published-language edition, import and export contracts;
- dependency, authority and evidence direction;
- the exact ACL decision;
- total/partial/conditional translation;
- information preservation, residuals and declared losses;
- identity, time and grain changes;
- version coexistence and migration requirements;
- deterministic failures/refusals, proof obligations and forbidden-cycle class.

The paired `acl-decisions.jsonl` says how the foreign contract is admitted locally. Unknown foreign
values are refused or retained as typed residuals; they are never guessed.

## DDD relationship vocabulary

```text
upstream_downstream     meaning constrains downstream use
customer_supplier       downstream needs influence an upstream contract
conformist              downstream deliberately accepts upstream coupling
anti_corruption_layer   downstream translates into its own language
open_host_service       upstream exposes a stable multi-consumer protocol
published_language      an editioned external-dependency contract
shared_kernel           exceptional joint ownership with joint tests/changes
separate_ways           deliberate non-integration
independent_appraisal   issuer and appraiser remain different authorities
authority_delegation    scoped, expiring, revocable authority transfer
evidence_submission     issuer submits; target decides relevance/sufficiency
compiler_requirement    semantic context requests provider-neutral capability
provider_offer          implementation offers capability but not semantics
runtime_receipt         occurrence says what happened in one execution
```

`shared_kernel` is not a convenient common crate. It is exceptional because it requires an exact
shared model, named joint owners, a change protocol, compatibility law and conformance tests.

## Non-collapsible distinctions

```text
bounded context != product != suite != provider != deployment occurrence
semantic owner != accountable role != steward != custodian != maintainer
published language != transport protocol != carrier schema != provider API
import != export != requirement != offer != binding != runtime receipt
parse success != schema conformance != semantic admission
identifier map != match candidate != identity decision != merge
valid time != observation time != event time != recording time != processing time
grain change != cardinality change != representation change != information loss
delegation != data flow != dependency != evidence submission
claim issuer != evidence source != independent appraiser != decision authority
```

A catalog may describe a context. A product may package it. A provider may implement or host it.
None becomes the semantic owner merely through cataloging, packaging, implementation or hosting.

## Three unrelated vertical paths and their negative twins

### Counterparty credit risk

```text
counterparty identity
  -> legal agreement + jurisdiction
  -> exposure measurement
  -> collateral/netting
  -> default/wrong-way-risk simulation
  -> qualified CCR decision

negative twin:
  agreement code without jurisdiction/edition
  -X-> REFUSE legal-agreement equivalence
```

This path prevents trade aggregation, identity matching, legal netting, simulation and limit
decisions from collapsing into a single "CCR analytics" context.

### Clinical outcomes

```text
authorized patient identity
  -> coded clinical observation + status + unit
  -> time-indexed episode/cohort
  -> study design + estimand + outcome estimate
  -> independent safety adjudication
  -> evidence-informed care decision

negative twin:
  detection signal self-certified by its issuer
  -X-> REFUSE unadjudicated safety signal as care order
```

### Industrial maintenance

```text
asset identity/configuration
  -> calibrated sensor observation
  -> process event and operating state
  -> degradation/failure-mode model
  -> constrained maintenance optimization
  -> authorized work order + completion evidence

negative twin:
  uncalibrated signal treated as failure evidence
  -X-> REFUSE at sensor-observation admission
```

These paths are intentionally unrelated. Passing one cannot stand in for passing another.

## Compiler use

The compiler must first resolve a context and published-language edition, then build an ACL plan.
Provider selection comes later.

```text
declared term
    |
    v
resolve context identity + edition --unknown--> typed compiler gap
    |
    v
resolve semantic owner + published language --ambiguous--> refuse
    |
    v
select explicit ACL/mapping edition
    |
    +--> prove totality / residual handling / information loss
    +--> prove identity / time / grain transformations
    +--> prove authority / evidence direction / version coexistence
    |
    v
emit language IR requirement
    |
    v
bind library offer + qualification + exact target
    |
    v
execute through effect adapter -> occurrence-scoped receipt
```

`requirements.jsonl`, `offers.jsonl`, and `compiler-mappings.jsonl` show the separation. Mappings
remain `candidate_unbound`; an entry is not proof that an implementation has qualified.

## Library boundaries

The 30 candidate libraries split pure semantics from effectful gateways. Examples include context
identity, relationship vocabulary, translation-totality algebra, loss ledger, identity/time/grain
bridges, authority graph, compatibility, cycle checking, refusal catalog, context IR, binder,
runtime gateway and conformance kit. Every library declares:

- pure or effect-adapter posture;
- one responsibility and explicit non-ownership;
- all decision points that callers may configure;
- ports, dependencies and evidence surfaces.

No library dispatches by provider/product name. A provider adapter implements a later offer against
an exact target and cannot redefine the domain language.

## Source and innovation posture

`sources.jsonl` snapshots 199 distinct primary or authoritative standards, specifications, official
project documents and original research records drawn from already researched universes. Every
source includes authority scope and limitations. A citation can constrain one surface; it cannot
settle global semantic ownership.

`innovations-2021-2026.jsonl` records 20 non-LLM changes such as OpenAPI 3.1/3.2, incremental CDC
snapshots, DID Core, EPCIS 2.0, SLSA 1.0, FHIR R5, OpenTelemetry metrics stability, DCAT 3, RDF
Dataset Canonicalization, AsyncAPI 3.0, Iceberg REST catalog/v3 and Verifiable Credentials 2.0.
These are evidence of changed contracts or boundaries, never replacements for the ontology.

## Files

```text
metamodel.json                    closed axes and constitutional distinctions
contexts.jsonl                    144 sampled candidate contexts
relations.jsonl                   308 typed context-map relations
acl-decisions.jsonl               308 exact anti-corruption/boundary decisions
loss-refusal-rules.jsonl           60 non-silent-loss laws
proof-obligations.jsonl            32 compiler/release proofs
requirements.jsonl                 30 provider-neutral needs
offers.jsonl                       30 candidate library offers
compiler-mappings.jsonl            30 unbound mappings
library-boundaries.jsonl           30 composable boundaries
vertical-paths.jsonl                6 positive/negative paths
input-alignments.jsonl             38 exact-token inventory alignments
innovations-2021-2026.jsonl        20 non-LLM changes
sources.jsonl                     199 evidence records
gaps.jsonl                         28 explicit open gaps
schemas/*.schema.json              per-record schemas
manifest.json                       counts, inputs and artifact hashes
build_corpus.py                     deterministic generator
validate_corpus.py                  references, laws, scale and hash validator
```

## Rebuild and validate

```bash
python3 research/domain_atlas/context_map/build_corpus.py
python3 research/domain_atlas/context_map/validate_corpus.py --determinism
```

The validator checks useful-scale gates, exact internal references, context/import/export/ACL
closure, source and innovation citations, totality/loss/refusal consistency, product/provider
non-ownership, authority/compiler forbidden cycles, library dependency cycles, positive and
negative vertical paths, manifest hashes and deterministic regeneration.

HTTP reachability is intentionally not part of deterministic validation. A network outage must not
make a semantic build nondeterministic; source occurrence monitoring belongs to change intelligence.

## Open-world warning

The corpus has 28 typed gaps. It does not claim that 144 candidates are the final bounded contexts,
that every relationship has been independently adjudicated, or that any offer is production-ready.
Splits, merges and owner decisions remain evidence-driven. New contexts extend the open registry;
they do not loosen the closed identity, relation, loss, authority and proof vocabulary.
