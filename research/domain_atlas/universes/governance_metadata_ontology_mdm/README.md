# Governance, metadata, ontology, and MDM universe

This directory is a provider-neutral, open-world candidate registry for a deterministic intent
compiler and composable libraries. It models independently owned meanings, authority decisions,
operations, refusals, and integration contracts. It is not a feature checklist for one data
catalog or MDM product.

Every emitted record has status `candidate_pending_review`. Counts demonstrate research depth,
not acceptance or universal completeness.

## The separations that define the universe

```text
real or digital asset
        |
        +-- asset identity ---------------- stable key, version, aliases, namespace
        |
        +-- metadata record --------------- assertions *about* the asset + provenance
        |        |
        |        +-- catalog listing ------ discoverability; never endorsement by itself
        |        +-- certification -------- criteria + evidence snapshot + issuer + expiry
        |
        +-- technical/runtime schema ------ fields, carriers, keys, compatibility
        |        |
        |        +-- semantic model ------- entities, dimensions, joins, query grain
        |                 |
        |                 +-- metric ------ formula, unit, time spine, filters, additivity
        |
        +-- domain language
                 |
                 +-- glossary ------------ scoped terms and definitions
                 +-- taxonomy ------------ navigable concept scheme
                 +-- ontology ------------ formal axioms and declared inference semantics

shared business entity
        |
        +-- identity assertion ------------ who/what the entity is in a scope
        +-- entity resolution ------------- candidate, comparison, match/non-match/review
        +-- authoritative master ---------- governed field authority and effective version
        +-- golden record ----------------- reproducible survivorship projection
        +-- reference data ---------------- values that classify/constrain other data
        +-- code set ---------------------- maintenance-agency codes and lifecycle

governance authority
        |
        +-- owner/accountability ---------- decision right and outcome accountability
        +-- stewardship ------------------- delegated operational governance work
        +-- custody ----------------------- possession, safekeeping, availability
        +-- policy statement -------------- permission/prohibition/duty under an issuer
                 |
                 +-- decision/enforcement - evaluated input + action + immutable receipt
```

The compiler never collapses these boundaries:

- metadata about an asset is not the asset, a domain ontology, a runtime schema, or a semantic
  metric;
- an identity assertion is not a similarity score, a match decision, or a merge;
- authoritative master data is not a survivorship-generated golden record, a publisher's Golden
  Copy file, or a reference code set;
- catalog listing is not certification, access grant, or evidence of correctness;
- a policy statement is not a runtime decision or enforcement receipt; and
- accountability, delegation, stewardship, custody, approval, and entitlement are qualified
  roles, never one generic `owner` field.

## Deterministic compilation

```text
intent
  -> resolve governed object kind
  -> resolve identity namespace + artifact versions + effective time
  -> select exactly one owner context
  -> match typed requirement to capability/operation offer
  -> resolve source-system, type/shape, formula, quality, lineage,
     privacy/security, operation, and vertical bindings
  -> check ACL, authority, evidence, invariants, hold and policy
  -> emit executable plan + proof obligations + receipts
     OR typed gap/refusal (never a label- or vendor-name guess)
```

All governed writes are deny-by-default. Unsupported semantics, unresolved identity, missing
authority, ambiguous version, insufficient evidence, incompatible schemas, active holds, and
indeterminate authorization produce typed failures.

## Current generated depth

`coverage-report.json` is authoritative for generated counts and SHA-256 digests. Edition 1
currently contains:

- 80 evidence sources: 20 W3C-issued records, 11 ISO/ISO-IEC records, 4 OMG records, 13 industry
  standards, 14 major OSS documentation records, and 4 research articles;
- 50 bounded-context candidates;
- 50 capability candidates and 200 typed-operation candidates;
- 40 explicit compiler decision points (290 capability/operation/decision candidates total);
- 74 ubiquitous-language candidates with homonym groups and negative distinctions;
- 39 hard invariants and compiler refusals;
- 49 context relations with deny-by-default ACL boundaries;
- 50 requirement/offer/compiler mappings;
- 25 live library-boundary candidates with explicit semantic class/effect posture, one candidate
  owner each, and an acyclic dependency graph;
- twelve coarse library candidates retired in favor of exact existing compositions, with no
  compatibility aliases and explicit replacement records;
- 32 external-universe mappings to source systems, types/shapes, semantic/formula contexts,
  quality, pipeline lineage, privacy/security, operations, and vertical profiles;
- 12 vertical cases across finance, healthcare, retail, official statistics, public records,
  manufacturing, software delivery, research, utilities, telecom, insurance, and logistics;
- 28 source-backed 2021-2026 developments, with working drafts marked as drafts; and
- 17 explicit gaps.

## Files

- `bounded-context-candidates.jsonl` — candidate semantic ownership boundaries.
- `ubiquitous-language-candidates.jsonl` — terms, scoped definitions, homonyms, and forbidden
  conflations.
- `capability-operation-candidates.jsonl` — capability offers and typed operations with
  signatures, pre/postconditions, effects, determinism, idempotency, and refusals.
- `decision-point-candidates.jsonl` — material compiler branches and fail-closed defaults.
- `invariants-refusals.jsonl` — hard laws and refusal behavior.
- `context-relations-acls.jsonl` — cross-context relations and permitted access.
- `compiler-mappings.jsonl` — requirement-to-offer selection and compiler proof obligations.
- `library-boundaries.jsonl` — candidate composable-library ownership and dependencies.
- `retired-compositions.jsonl` — coarse candidates retired in favor of exact library compositions.
- `external-universe-mappings.jsonl` — bridges to neighboring horizontal universes and verticals.
- `vertical-cases.jsonl` — portability and distinction tests in unrelated industries.
- `evidence-sources.jsonl` — primary evidence index with bounded claims.
- `innovations-2021-2026.jsonl` — recent standards/specification/OSS developments and maturity.
- `coverage-gaps.jsonl` — known research, evidence, implementation, and freshness gaps.
- `schemas/` — Draft 2020-12 JSON Schemas for every JSONL record kind.
- `coverage-report.json` — generated counts, minimum checks, status counts, and digests.
- `build_corpus.py` — deterministic generator.
- `validate_corpus.py` — dependency-free reference/depth/determinism audit plus optional JSON Schema
  validation.

Ten libraries created by the final coarse-boundary decomposition publish exact public types,
traits, operation signatures, typed refusals, laws and conformance-oracle classes: certification
lifecycle, assurance appraisal plan, governance issue workflow, change review policy, catalog
listing, discovery query, classification assignment, privacy-purpose binding, match policy and
golden-record edition. The validator prevents these source contracts from regressing to generated
placeholders.

## Evidence posture

The source registry uses primary standards pages, normative specifications, official project
documentation, and original research. A source supports only the surfaces named in its record; it
does not prove that any deployed product conforms. W3C working drafts are not treated as stable
Recommendations. ISO catalog abstracts and freely available pages do not replace licensed
clause-level review where the full normative text is restricted.

No evidence record is a legal opinion. Privacy-purpose compatibility, retention schedules,
regulated code-system use, and policy precedence still require the named organizational or legal
authority.

## Completeness limits

This is deliberately an open universe. It is not complete merely because minimum counts pass.
Before acceptance, candidates still need clause-level source pinning and digests, independent
review, split/merge adjudication, two unrelated implementations per critical contract, negative
tests, source-occurrence and connector receipts, population-specific entity-resolution evaluation,
multi-catalog federation tests, jurisdiction packs, and recurring freshness review.

Some bridges use explicit selectors such as `shape.*` because neighboring universe records remain
candidates. A compiler must resolve a selector to one exact accepted registry edition and ID or
emit a typed gap. It must never treat the selector as a wildcard execution permission.

Prompt, RAG, agent-memory, generative-model, and LLM-specific semantics are excluded from the core.
A future extension may depend one-way on this universe but may not redefine its identity,
authority, policy, provenance, privacy, quality, or retention laws.

The repository asks research agents to record work through `td`; the executable was unavailable in
this environment, so `gmo.gap.td_tooling` records that missing workflow evidence.

## Rebuild and validate

```bash
python3 research/domain_atlas/universes/governance_metadata_ontology_mdm/build_corpus.py
python3 research/domain_atlas/universes/governance_metadata_ontology_mdm/validate_corpus.py
uv run --with jsonschema python research/domain_atlas/universes/governance_metadata_ontology_mdm/validate_corpus.py
```

The validator rebuilds twice and compares every generated registry, schema, and coverage report
byte-for-byte. With `jsonschema` installed it also checks every record against its Draft 2020-12
schema.
