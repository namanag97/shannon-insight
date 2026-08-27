# Source occurrence catalog

Status: researched candidate, open world, and intentionally not complete. No live customer
endpoint was probed, no credential was collected, and no occurrence in this package is compiler
bindable yet.

This package answers the concrete layer beneath the provider-neutral source-system universe:
which real organizations, products, release/artifact targets, offers, deployments, endpoints, and
connectors could satisfy a declared source requirement—and what must be proved before the compiler
may use one.

## The identities that must not collapse

```text
provider-neutral source capability class
  e.g. transactional CDC, EHR, mailbox, historian, market-data feed
                    |
                    | candidate_instance_of
                    v
provider org -> product -> implementation artifact -> documented/managed offer
                                  |                         |
                                  | exact build             | region/tier/contract
                                  +------------+------------+
                                               v
                                deployment / endpoint occurrence
                          tenant + site + config + objects + authority
                                               |
                    +--------------------------+--------------------------+
                    |                                                     |
                    v                                                     v
            protocol/profile                               connector class
       framing and access contract                 provider-neutral adapter role
                    |                                                     |
                    +--------------------------+--------------------------+
                                               v
                              connector implementation artifact
                         version + digest + lock + SBOM + license
                                               |
                                               v
                              deployed connector occurrence
                    config + network + secret refs + checkpoint store
                                               |
                                               v
                                  qualification receipts
                          exact scope + time + outcome + evidence
                                               |
                                               v
                         compiler binding OR typed refusal/gap
```

The constitutional identity chain is:

```text
source class != provider != product != artifact != offer != deployment != endpoint
protocol != data model != business authority
connector class != connector artifact != deployed connector
official documentation != conformance receipt != observed behavior
rolling "current" != exact reproducible version
```

These separations are why the compiler never branches on `if vendor == "SAP"` or
`if product == "PostgreSQL"`. It matches provider-neutral requirements to typed offers and then
requires occurrence-scoped proofs.

## Current corpus

The deterministic generated corpus contains:

| Record plane | Count |
|---|---:|
| provider organizations | 104 |
| product identities | 149 |
| implementation/qualification artifacts | 298 |
| combined provider + product + artifact records | 551 |
| documented offers | 149 |
| product/source-class surface candidates | 171 |
| documented occurrence templates | 171 |
| provider-neutral compiler requirements | 171 |
| requirement/offer mappings | 171 |
| protocol/class crosswalks | 107 |
| official primary-source records / distinct URLs | 300 / 299 |
| adapter/library boundaries | 54 |
| exact provider-neutral semantic library contracts | 1 |
| qualification probes | 44 |
| non-LLM innovations, 2021–2026 | 32 |
| negative twins | 30 |
| explicit open gaps | 32 |
| live probes / credentials / bindable occurrences | 0 / 0 / 0 |

All 171 upstream source-system classes have at least one real product or standards-backed
research target. All 107 upstream protocol profiles have a loss-aware crosswalk. Coverage is not
conformance: every product/source mapping says `candidate_not_conformance`, and every occurrence
is a `documented_template_not_observed`.

Families include databases and analytical repositories; ERP, finance, CRM, HR, SCM, WMS, TMS,
MES, EAM and service systems; files, object stores, content, email, calendar and collaboration;
APIs, webhooks, messaging and CDC; identity, security and telemetry; IoT, SCADA, PLC, historian,
building, robot, inspection, batch and grid systems; scientific instruments, arrays, genomics,
clinical research and HPC; GIS, Earth observation, point clouds, CAD/BIM, media and weather;
banking, payments, trading, market data, insurance, healthcare, telecom, utility, aviation,
transit, maritime, pharma, government, education and cadastral systems; and mainframe, VSAM,
fixed-record, tape, spool, CICS, air-gap, OCR and offline-register sources.

## What is documented versus what is proved

```text
official standard/product/API page
        |
        +-- may establish identity, vocabulary, protocol edition, documented feature
        |
        x-- does NOT establish tenant entitlement, exact build, region rollout,
            object/field authority, numerical limits, cost, runtime behavior,
            connector correctness, or end-to-end delivery guarantee

exact occurrence + connector + configuration
        |
        +-- execute scoped qualification probes
        |
        v
pass | fail | not_supported | not_authorized | inconclusive
        |
        +-- only fresh `pass` receipts may satisfy proof obligations
```

Marketing pages are retained only when they are the official identity/research entry point for a
closed commercial product. They never produce conformance. Normative standards and official API
documentation constrain only the named surface. Runtime claims require executed probes.

## Compiler binding path

```text
declared analytical/application intent
    -> source capability requirements
    -> candidate products/offers (research lookup only)
    -> exact deployment occurrence resolution
       - tenant/account, region/site, endpoint
       - exact product/API/schema build
       - object and field authority scope
       - entitlement and security boundary
    -> connector class requirement
    -> exact connector artifact + config + deployment
    -> qualification plan
       - snapshot/cursor/change handoff
       - schema/type/time/order/finality
       - deletes/corrections/retractions
       - limits/cost/backpressure/recovery
       - authn/authz/network/encryption/audit
       - export/exit and destructive guards
    -> receipts valid for exact scope and interval
    -> requirement/offer solving
    -> bound acquisition/write plan OR typed refusal
```

Material unknowns fail closed. `not_supported`, `not_authorized`, and `inconclusive` are not empty
datasets. Writes, deletes, and OT control commands remain disabled until separately authorized and
qualified. “Exactly once” is never inherited from a vendor label; it requires a composition proof
over source replay, connector checkpointing, pipeline recovery, and sink effect.

## Three different version cases

```text
Pinned software release
  PostgreSQL 18.x docs -> resolve exact server patch + extensions + config -> qualify

Rolling SaaS
  Microsoft Graph v1.0 -> resolve tenant/cloud/rollout + entitlement + behavior date -> qualify

Industrial deployment
  SIMATIC S7-1500 -> resolve hardware catalog + firmware + project + safety/network zone
                    -> read-only qualification; commands remain independently disabled
```

The phrase “current version” is not a reproducible artifact identity. The catalog records the
documented version family and refuses binding until the occurrence supplies an exact build or an
equivalent provider-issued behavior/rollout identity.

## Decision surfaces

`decision-axes.json` enumerates 17 independent axes: identity, version, authority, objects,
access, change, schema/type, time, ordering/finality, transactions, limits, security, topology,
availability/recovery, cost/resources, lifecycle, and evidence. A numerical fact is not usable
without value, unit, scope, provenance, observation time, validity and failure behavior.

Important source-specific distinctions include:

- email message/MIME/attachment/thread identity, delta paging, mailbox ACLs and retention;
- geospatial feature/raster/point-cloud assets, CRS edition/epoch/axis order and processing baseline;
- healthcare base FHIR version versus implementation guide, terminology and authorized resource set;
- banking authorization, clearing, settlement, posting, reversal and correction finality;
- OT read telemetry versus safety-critical command authority;
- scientific units, calendars, fill values, chunking, instrument calibration and accession revision;
- mainframe CCSID, copybook, RECFM/LRECL, packed decimal, generation data and spool lifecycle.

## Library boundaries

The 54 candidates in `adapter-library-boundaries.jsonl` are composable roles, not product
connectors. Each owns provider-neutral operations, typed configuration, cursor/checkpoint types,
typed refusals, receipt emission, and a dependency-removal seam. It does not own business
authority, credentials, deployment lifecycle, orchestration, or sink commit.

```text
pure contracts                              runtime adapters
----------------------------                -----------------------------
source requirement type                     network/protocol execution
object/authority descriptor                 paging/snapshot/change loops
cursor/checkpoint algebra                    retry/backoff/backpressure
type/loss mapping                            checkpoint persistence port
refusal and receipt types                    observability/receipt emission
qualification specification                 provider artifact integration
```

Provider quirks belong in adapters or anti-corruption profiles selected through registry data.
They do not create vendor-name branches in compiler semantics.

## Files

- `metamodel.json` — node/edge identities, binding key and invariants.
- `decision-axes.json` — complete occurrence decision surfaces.
- `official-sources.jsonl` — official primary evidence and strict use limits.
- `providers.jsonl`, `products.jsonl`, `implementation-artifacts.jsonl` — separate identities.
- `documented-offers.jsonl`, `product-source-surfaces.jsonl` — non-conformant research candidates.
- `occurrence-templates.jsonl` — all 171 class instances, explicitly not observed.
- `protocol-class-crosswalks.jsonl` — all 107 profiles with non-established semantics and loss rules.
- `compiler-requirements.jsonl`, `requirement-offer-mappings.jsonl` — fail-closed compiler inputs.
- `adapter-library-boundaries.jsonl` — 54 composable library seams.
- `library-semantic-contracts.jsonl` — the exact pure Source Cursor Algebra contract: typed
  identity and partial order, eight no-default decisions, operations, invariants, refusals,
  negative collapses and conformance oracles. It does not acquire tokens or persist checkpoints.
- `qualification-probes.jsonl` — 44 scoped, evidence-producing probes; none executed here.
- `innovations-2021-2026.jsonl` — changes that alter compiler evidence or invalidation needs.
- `negative-twins.jsonl` and `gaps.jsonl` — invalid inferences and unresolved work.
- `schemas/record.schema.json` — Draft 2020-12 record schema.
- `build_catalog.py` and `validate_catalog.py` — deterministic generator and validator.

## Rebuild and validate

```bash
python3 research/domain_atlas/universes/source_occurrence_catalog/build_catalog.py
python3 research/domain_atlas/universes/source_occurrence_catalog/validate_catalog.py
uv run --offline --with jsonschema \
  python research/domain_atlas/universes/source_occurrence_catalog/validate_catalog.py --schemas
```

The validator checks all source/protocol references, every identity edge, minimum research depth,
official-source posture, the absence of credential material, non-bindability without receipts,
global record-ID uniqueness, and per-file digests.

## Remaining work

The package is deliberately a research layer, not an environment inventory. The next closure step
is to ingest customer-authorized deployment descriptors and execute qualification probes inside
their controlled environments. Exact connector artifacts, dependency locks, SBOMs, licenses,
support matrices, supply-chain advisories, live limits, regional rollout, cost, object authority,
schema/change behavior and supplier-exit fidelity remain occurrence work. `gaps.jsonl` preserves
those unknowns instead of silently projecting public documentation onto a real enterprise.
