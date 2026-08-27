# Non-LLM change and innovation intelligence

This directory is the recurring evidence and invalidation layer for the domain
atlas.  It monitors primary standards, specifications, advisories, releases,
documentation and deployment receipts, then routes bounded change claims to
coverage-plane owners and compiler proof obligations.  It does not let a vendor
release, product name, or market category define canonical semantics.

The generated corpus is a candidate registry, not a news summary.  It preserves
the source observation, review decision, downstream invalidation and missing
evidence as separately identified records.

## Lifecycle

```text
 recurring schedule
        |
        v
 source occurrence ---- collection attempt
        |                       |
        |                 +-----+------------------+
        |                 |                        |
        |              success                  failure
        |                 |                        |
        |                 v                        v
        |          candidate signal        observability gap
        |                 |                 (never "no news")
        |                 v
        |          evidence/claim split
        |                 |
        |                 v
        |          reviewer decision
        |          /      |       \
        |       admit   watch    route to optional extension
        |          |      |          |
        |          v      +----------+-- retain generic substrate only
        |    verified change event
        |          |
        |          v
        +--> plane + compiler-proof impact mapping
                   |
                   v
          invalidate cached offer/decision/receipt
                   |
                   v
        migrate / requalify / refuse / retain gap
                   |
                   v
             supersession record
          (prior identity/evidence retained)
```

Successful collection with no qualifying item may produce a bounded `no_news`
observation for the exact source set and time window.  DNS, authentication,
timeout, parsing, rate-limit, or schema failures produce observability gaps.
They are never evidence that no change occurred.

## Evidence distinctions

- A release note is not a deployed rollout. `verified-change-events.jsonl`
  verifies the primary publisher claim and keeps `deployed_rollout_status` at
  `not_observed` until an occurrence receipt exists.
- A documentation diff is not proof of behavior. Conformance or deployed
  observation must close that gap.
- A security advisory is not exploit evidence. CISA KEV, incident evidence, or
  equivalent scoped evidence has a separate change type.
- A feature is not a qualified offer. `offer-observations.jsonl` deliberately
  keeps qualification false and requires exact artifact, target and test
  receipts.
- A vendor synthetic benchmark is not an independent result. The Snowflake
  throughput item is admitted only as a vendor claim.
- Preview and GA are different maturity states, and GA still does not prove
  regional rollout or deployed use.
- LLM and agent-specific wrappers live only in `extensions/llm_agent/`. Reusable
  sandbox, caller identity, package policy, stage mount, finite limit, cost and
  scheduling evidence can be retained as separately bounded non-LLM substrate.

## Registries

| File | Purpose |
| --- | --- |
| `monitored-subjects.jsonl` | Versioned monitored units and non-LLM scope |
| `sources.jsonl` | Primary source authority and limitations |
| `source-occurrences.jsonl` | Concrete feed/document endpoints and collection SLOs |
| `recurring-schedules.jsonl` | Daily, six-hourly, weekly and monthly collection/review jobs |
| `collection-runs.jsonl` | Run-level accounting for supplied monitoring briefs |
| `collection-attempts.jsonl` | Successes and failures, including 80 DNS gaps |
| `change-types.jsonl` | Non-conflating change/evidence classifications |
| `candidate-signals.jsonl` | Non-LLM and generic-substrate candidate/watch/admission signals |
| `verified-change-events.jsonl` | Primary-source-verified bounded claims |
| `claims-evidence.jsonl` | Positive claims and explicit scope boundaries |
| `coverage-proof-mappings.jsonl` | One routing record for every current atlas plane |
| `impact-mappings.jsonl` | Affected capabilities, contracts, providers and targets |
| `review-decisions.jsonl` | Admission, deferral, quarantine and policy decisions |
| `migration-invalidation-triggers.jsonl` | Proof reopening and migration/refusal actions |
| `security-availability-tradeoffs.jsonl` | Controls with availability/cost consequences |
| `offer-observations.jsonl` | Feature claims that remain unqualified offers |
| `watchlist.jsonl` | Missing evidence and exit criteria |
| `supersession.jsonl` | Edition replacement without erasing history |
| `innovations.jsonl` | Non-LLM 2021-2026 innovation candidates |
| `gaps.jsonl` | Typed unknowns that block overclaiming |

Every JSONL kind has a matching Draft 2020-12 schema in `schemas/`.
`metamodel.json` states the invariants, and `manifest.json` pins record counts
and SHA-256 digests.

## Optional LLM/agent extension

`extensions/llm_agent/` records the exact supplied model/agent capabilities and
changes. It imports deterministic core substrate mappings one-way; no core
record may depend on an extension identity. Its effect-state registry enforces:

```text
model output != agent plan != validated claim
             != authorized tool intent != effect receipt
```

This prevents generated content, an accepted plan, or even an authorized call
from being represented as a validated fact or observed external effect.

## Supplied briefs

The corpus represents the two supplied 2026-08-25 runs and their Google Managed
Spark, OpenMetadata, Snowflake, dbt and Dagster signals.  It also includes the
requested Redpanda, Cube and TypeORM release/advisory surfaces.  The Snowflake,
Cube and OpenMetadata LLM wrappers are held in the optional extension while their generic execution,
pagination, identity, package, stage, cost and orchestration substrates remain
available for bounded review.

Both supplied runs attempted 40 feeds and recorded 40 DNS failures.  Each also
recorded 30 manual primary-page opens.  The attempt corpus does not reconstruct
which manual page yielded which candidate when the briefs did not provide that
receipt; it says so explicitly rather than inventing lineage.

## Deterministic rebuild and validation

Run from the repository root:

```sh
python3 research/domain_atlas/ecosystem/change_intelligence/build_corpus.py
python3 research/domain_atlas/ecosystem/change_intelligence/validate_corpus.py
```

The builder performs no network access.  It emits stable key ordering, schemas,
manifests and hashes from the compact reviewed constants in `build_corpus.py`.
The validator checks identities, local schemas, references to the live coverage
plane and proof registries, full plane routing, supplied-signal presence,
anti-conflation laws, extension isolation, collection accounting and quality gates.

## False-completeness posture

Passing validation proves only that this finite candidate seed is internally
referentially sound and that every currently registered plane has a monitoring
route.  It does **not** prove that all vendors, standards, advisories, releases,
regions, deployed occurrences, innovations, exploits, behaviors, provider
offers, targets, vertical consequences or counterexamples have been found.  It
does not qualify a provider offer, establish canonical semantics, or close any
compiler proof.  Missing, inaccessible, stale or unreviewed evidence remains an
explicit gap, and all downstream selection must still demand occurrence-scoped
qualification and acceptance receipts.
