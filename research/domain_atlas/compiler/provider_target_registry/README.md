# Provider and target physical-binding registry

Status: **candidate research corpus**. Evidence retrieval date: **2026-08-25**. This is an
open-world seed, not a provider ranking, recommendation, certification, availability promise, or
claim of universal support.

This registry supplies the physical-binding stage with provider-neutral capability classes,
versioned implementation and offer identities, target constraints, evidence scopes, qualification
receipts and refusal laws. It has no LLM, generative or agentic runtime dependency. Provider names
are data attached to offers; they never own canonical semantics and never determine dispatch.
Optional model/LLM/agent assistance may propose typed inputs, explanations or plans, but removing
that entire extension must leave parsing, typing, constraint solving, execution, authorization and
receipt verification intact. Proposals acquire neither semantic nor effect authority.

```text
upstream semantic + assurance contract
                 |
                 v
       capability requirement
        (guarantees + finite budgets)
                 |
                 v
       provider-neutral class -------------------------------+
                 |                                           |
                 v                                           |
 provider organization --maintains/offers--> artifact        |
                 |                         + exact version     |
                 |                         + offer snapshot    |
                 v                                           |
        versioned concrete offer                             |
                 |                                           |
                 +---------- matches target profile <--------+
                                      |
                                      v
                              target occurrence
                           + config fingerprint
                           + location/control evidence
                           + finite resource vector
                                      |
                         compatibility matrix cell
                                      |
                         qualification receipt
                         /                    \
            semantic conformance       performance result
                    |                         |
                    +-----------+-------------+
                                v
             resource + limit + cost feasibility
              /          |          |          \
     documented     probed       list       measured
       limit         limit       price        cost
                                |
                                v
               binding, declared typed degradation,
                         or typed refusal
```

## Identities that remain separate

```text
provider class != provider organization
provider organization != implementation artifact
implementation artifact != edition/version
edition/version != versioned concrete offer
concrete offer != deployed target occurrence

capability class != observed offer
target profile/class != target occurrence
documented limit != probed limit
list price != measured workload cost
semantic conformance != performance qualification
library != engine != managed service
availability region != residency guarantee
```

A target occurrence is bindable only after its immutable artifact versions, relevant configuration,
location, finite budgets and evidence are fixed. The seed's public-service occurrences are explicitly
`documented_offer_snapshot` records, not claims that a deployment exists. They are intentionally
`binding_eligible: false`; their qualification receipts are `inconclusive` because no occurrence was
available for probes.

The retained continuous-LP pilot is the first exception to the documentation-only evidence class:
it records exact OR-Tools 9.15.6755 GLOP/MPSolver-Python and highspy 1.15.1 interfaces, two isolated
macOS Arm64/Python 3.14.7 probe occurrences and four executed-test assessments. Three scoped
profiles passed; the precise infeasible-versus-unbounded profile for GLOP/MPSolver failed. These
executions remain `binding_eligible: false`: they have no independent appraisal, portability proof,
production/SLO/security/license qualification or vertical acceptance. A retained negative twin also
shows that these exact native extensions collided when imported into one Python process; the result
is target-scoped and causes process isolation, not a claim of universal incompatibility.

The bounded-integer CP-SAT pilot adds a second falsification path. Its first retained adapter
configuration passed core, global-constraint, scheduling and limit profiles but failed complete
enumeration because observing a callback was incorrectly treated as requesting exhaustive search.
The corrected adapter propagated enumeration intent into the exact provider parameter and all five
profiles passed. Both configurations remain as distinct target occurrences and receipts. This is
executed evidence that adapter configuration changes semantics; neither run is independently
appraised, provider-qualified, portable or accepted for a manufacturing schedule.

## Coverage

The taxonomy spans:

- native/POSIX, WebAssembly/WASI/components, JVM/JNI and CPython/native extensions;
- local process, OCI container, Kubernetes pod/job/device allocation, serverless function/container;
- bounded batch, microbatch, continuous stream, event-driven and distributed DAG engines;
- relational, embedded/vectorized, distributed/federated, warehouse and lakehouse engines;
- object, block, local/shared file storage and table-format coordination primitives;
- partitioned logs, durable subscriptions and work queues;
- scalar CPU, SIMD/vector extensions, GPU and low-level accelerator APIs;
- developer-local, edge, on-premises, public-cloud, hybrid, sovereign and air-gapped targets;
- TCP/QUIC, async I/O, user-space packet/storage I/O, bandwidth and egress;
- OS/local-DAG/Kubernetes/batch/fair-share/preemptive/topology/device schedulers; and
- managed Kubernetes, batch, function, container, database, warehouse and storage services.

Concrete vendor and project records exist only to describe dated offers and artifacts. They are
not comparative rankings. Every concrete offer says that it is non-universal, identifies an exact
version or an explicit documentation snapshot, carries observed/retrieved dates, enumerates
exclusions and declares invalidation triggers.

## Compiler binding law

1. Resolve the upstream semantic owner, exact contract edition and capability requirements.
2. Require finite resource, state, time, network and cost budgets for every blocking dimension.
3. Enumerate offers by capability structure, never by provider or artifact name.
4. Reject prohibited traits, stale evidence, unversioned artifacts and incompatible targets.
5. Resolve an exact target occurrence and configuration fingerprint.
6. Evaluate compatibility cells and run the declared semantic and performance oracles separately.
7. Distinguish documented limits from occurrence probes and rate cards from measured workload cost.
8. Bind only when all structural, semantic, policy, resource, cost and evidence gates pass.
9. Carry a degradation only when intent declared its type and authority approved it; otherwise refuse.
10. Invalidate the binding on relevant version, configuration, target, region, quota, capacity, rate,
    oracle, evidence-age, health or location-control changes.

## Artifacts

- `metamodel.json` — identity split, binding chain, laws and reconciled upstream contracts.
- `sources.jsonl` — current primary standards, official specifications, implementation docs,
  releases and price pages. Mutable pages are scoped to the retrieval date.
- `context-candidates.jsonl` — ownership-boundary candidates; none are adjudicated as complete.
- `capability-classes.jsonl` — provider-neutral taxonomy.
- `provider-classes.jsonl` and `provider-organizations.jsonl` — roles and concrete organization
  identities, separate from artifacts and offers.
- `implementation-artifacts.jsonl` — library, engine, runtime, orchestrator, protocol, service,
  hardware-ISA and storage-system identities with version schemes.
- `concrete-offers.jsonl` — versioned/datestamped candidate offers and exclusions.
- `target-profiles.jsonl` and `target-occurrences.jsonl` — abstract constraints versus concrete or
  documentary occurrences.
- `resource-limit-cost-evidence.jsonl` — separately typed documented/probed limits, list prices,
  measured costs, usage and quota observations.
- `qualification-receipts.jsonl` — semantic and performance results kept separate and scoped.
- `compatibility-matrix.jsonl` — conditional/incompatible/unknown matrix cells, never global flags.
- `decisions.jsonl` — explicit authority-bound decisions with forbidden defaults.
- `refusal-invalidation-rules.jsonl` — fail-closed and requalification laws.
- `compiler-requirement-offer-mappings.jsonl` — provider-neutral requirement-to-offer candidate sets.
- `library-adapter-boundaries.jsonl` — pure/runtime library, provider-adapter and engine-integration
  ownership/effect/receipt boundaries.
- `innovations.jsonl` — dated, non-generative advances from 2021–2026.
- `gaps.jsonl` — honest unknowns and the evidence required to close them.
- `schema/*.schema.json` — one Draft 2020-12 schema per JSONL record kind.
- `build_registry.py` and `validate_registry.py` — deterministic generator and validator.
- `manifest.json` — generated counts and threshold declaration.

## Evidence posture

The source catalog contains 110 primary/official sources retrieved on 2026-08-25. A standard is
authoritative only for its normative interface; implementation documentation only for that
implementation; service documentation and pricing only for the named surface at the retrieval
date. None proves cross-provider equivalence, current account quota, capacity, residency, semantic
conformance, or workload performance.

Mutable claims must be refreshed under an authority-declared maximum age. Price evidence requires
currency, meter, region/account terms and effective time. Measured cost additionally requires a
versioned workload and reconciliation with provider meters. Availability lists remain separate
from contractual, legal and operational residency evidence.

## Exact generated counts

```text
113 primary/official sources
 40 context candidates
149 capability classes
 15 provider classes
 30 provider organizations
 59 implementation artifacts
 59 versioned concrete offers
 36 target profiles
 20 target occurrences/evidence snapshots
 30 resource/limit/cost evidence records
 25 qualification assessments (15 documentary, 10 executed-test; 0 qualified)
 23 compatibility cells
 34 decisions
 26 refusal/invalidation rules
 34 compiler requirement/offer mappings
 22 library/adapter boundaries
 26 non-generative innovations (2021-2026)
 25 open gaps
298 capability/offer/target/decision records
```

## Build and validate

From the repository root:

```bash
python3 research/domain_atlas/compiler/provider_target_registry/build_registry.py
python3 research/domain_atlas/compiler/provider_target_registry/validate_registry.py
```

The validator applies every record schema, checks identities and references, enforces count floors,
finite budgets, dated mutable evidence, fail-closed qualification, cost/limit distinctions,
invalidation coverage and deterministic regeneration. It rebuilds the corpus and compares hashes to
prove byte-for-byte deterministic output.

## Honest gaps

The corpus does not claim provider completeness, current capacity, account entitlements, negotiated
prices, deployed occurrence qualification, cross-provider SQL equivalence, accelerator compatibility,
end-to-end delivery, legal residency, air-gap assurance, measured energy/carbon, or workload cost.
Each missing proof is represented as a typed gap with a concrete resolution condition and a
prohibited assumption.
