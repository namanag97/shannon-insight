# Connector, adapter, and protocol universe

Status: evidence-backed candidate research corpus; not a completeness or deployment claim.

This package models the provider-neutral access layer between a source-system need/class and a
deployed source occurrence. It is deliberately **not** a catalog of vendor connectors. Protocols,
connector classes, implementation artifacts, and deployed occurrences remain separate identities
because each owns different facts and evidence.

```text
source-system need / capability class
          |  owns business authority, objects, change and finality meaning
          v
connector capability requirement ---- protocol/profile contract
          |                                      |
          v                                      v
provider-neutral connector class ---- implementation artifact
          |                            code/version/license/SBOM
          |                                      |
          +-------------------+------------------+
                              v
                 deployed connector occurrence
            config/network/credential refs/limits/probes
                              |
                              v
                  acquisition or write plan
              + receipts, gaps, and invalidation
```

## Identity and semantic laws

The compiler must preserve these non-substitutability rules:

- **Source class ≠ source occurrence.** A class describes portable source behavior; an occurrence
  owns product/version/tenant/site authority and mutable numerical limits.
- **Connector class ≠ implementation artifact.** A class states required access behavior; an
  artifact is code with a build identity, dependencies, license, provenance, and support lifecycle.
- **Implementation artifact ≠ deployed connector occurrence.** Deployment configuration,
  entitlement, network location, credentials, observed behavior, quotas, and qualification are
  occurrence facts.
- **Protocol ≠ data model.** Successful framing or parsing does not establish payload meaning,
  type preservation, authority, schema compatibility, time, order, or finality.
- **Documented capability ≠ probed behavior.** Both are retained with different provenance.
- **Read cursor ≠ CDC resume token.** Tokens are typed by issuer, purpose, object/partition scope,
  cut, version, retention boundary, and expiry.
- **Transport success ≠ source acceptance.** `2xx`, broker settlement, socket completion, or bytes
  sent may precede source validation, commit, business acknowledgement, or asynchronous failure.
- **Snapshot consistency ≠ export completion.** A completed job proves lifecycle progress, not a
  common source cut across its objects.
- **Connector exactly-once ≠ end-to-end effect.** End-to-end claims require a composed proof over
  source replay, connector checkpoint, pipeline recovery, and sink effect/commit.

Material unknowns fail closed. Unsupported, unauthorized, expired, and inconclusive outcomes are
not interpreted as empty data. Writes and industrial commands remain disabled unless a separate
authorization and destructive-guard receipt exists.

## Coverage

The generated `coverage-report.json` currently records:

| Surface | Count |
|---|---:|
| bounded-context candidates | 52 |
| protocol profiles | 107 |
| connector capabilities | 104 |
| typed operations | 104 |
| decision points | 52 |
| lifecycle records | 16 |
| protocol/capability/operation/decision/lifecycle records | 383 |
| connector classes | 68 |
| primary/official evidence sources | 149 |
| distinct evidence issuers | 65 |
| non-LLM innovations, 2021–2026 | 26 |
| conformance tests | 42 |
| real deployed occurrences / live probes / credentials | 0 / 0 / 0 |

Families cover database wire/query/change protocols; local, network, managed-file, object and block
transfer; REST/OpenAPI, GraphQL, gRPC, SOAP, OData, WebDAV and SCIM; webhooks and event streams;
AMQP, MQTT, Kafka, STOMP, NATS, JMS, CoAP and DDS; bulk jobs; OPC UA, Modbus, BACnet, IEC 61850,
DNP3, MTConnect, Sparkplug, oneM2M and Matter; FHIR, FHIR Bulk Data, DICOM, HL7 v2 and IHE; FIX,
FIXP, ISO 20022, XBRL and OFX; EDIFACT, X12, AS2, AS4, ebMS and EPCIS; OGC APIs, WFS, STAC,
SensorThings, Zarr, NetCDF and HDF5; IMAP, SMTP, JMAP, CalDAV, CardDAV and ActivityStreams;
TN3270E, DRDA and hostile fixed/EBCDIC records; iSCSI and NVMe-oF; OTLP, Trace Context and browser
telemetry delivery.

The count is a researched coverage position, not enumeration saturation. Evidence records point to
official specification owners and state their use limits. Several standards have licensed normative
texts; public publisher catalogues are identified as overviews rather than silently treated as full
clause-level evidence. `gaps.jsonl` keeps clause pinning, mutable documentation, paid standards,
occurrence limits, live qualification, safety authority, and independent review open.

## Contract surfaces

Every protocol candidate declares its edition/profile; layer; transport and framing; session and
discovery behavior; read/write/change/command surface; authentication, authorization, secret and
channel posture; schema/type/time mapping; cursor/change/resume semantics; ordering, finality and
delivery limits; retry, error and cancellation behavior; version/deprecation triggers; source-class
crosswalk; contexts; and evidence.

Connector classes compose required capabilities and compatible protocol profiles without naming a
vendor. Artifact records add build identity, dependency lock, licensing, SBOM/provenance posture,
declared versus qualified capabilities, support lifecycle and receipts. Occurrences add deployment
identity/configuration, credential **references**, documented assertions, separately labeled probe
observations, snapshot/cursor/change state, schema/time/order/finality, mutable limits/quota/cost,
retry/cancellation, partition/recovery, observability, and qualification.

The only occurrence records in this corpus are binding-ineligible hostile or legacy fixtures. They
exercise asynchronous rejection after transport acceptance, expired CDC checkpoints, partial bulk
exports, duplicate webhooks, EBCDIC/blocked-record ambiguity, unsafe industrial commands, and
browser enqueue without collector receipt. `negative-twins.jsonl` gives the paired semantic
confusions each fixture is meant to catch.

## Library boundaries

```text
pure contract core -> pure protocol codec -> effectful transport runtime
         |                                             |
         +---------------- provider adapter ------------+
                               |
                     source occurrence boundary

conformance oracle observes declarations/receipts; it owns no production I/O
```

- `library.cp.contract_core` owns identities, requirements/offers, decisions, typed gaps, and pure
  effect intents; it owns no I/O or protocol bytes.
- `library.cp.protocol_codec` owns versioned framing and parse/encode errors; it owns no sockets,
  retries, authentication policy, or source semantics.
- `library.cp.transport_runtime` owns connections, timeouts, flow control, retry scheduling, and
  cancellation disposition; it owns no provider object mapping or end-to-end guarantee.
- `library.cp.provider_adapter` maps a concrete remote surface and its source acknowledgements; it
  owns no business authority, scheduling policy, or secret storage.
- `library.cp.conformance_oracle` owns hostile scenarios, negative twins, receipt evaluation, and
  qualification invalidation; it performs no unapproved live probe.

## Compiler mappings and cross-universe integration

`compiler-requirements.jsonl`, `capability-offer-templates.jsonl`, and
`compiler-mappings.jsonl` provide fail-closed physical-binding candidates. Every mapping requires a
protocol profile, artifact qualification receipt, occurrence observation (or explicit unknown), and
invalidation triggers. Vendor names, undocumented inference, expired receipts, and configuration
mismatch are prohibited dispatch inputs.

`cross-universe-mappings.jsonl` is read-only. It maps to materialized source-system, pipeline,
data-shape, security, and quality IDs and validates those references. The lineage and provider/target
packages currently expose generators rather than materialized registries, so those records are
explicitly marked `generator_contract_surface`; no nonexistent qualification is inferred.

Ownership remains one-way:

- source systems own source meaning, authority, consistency, changes, and finality;
- pipeline/dataflow owns composed cuts, state, recovery, orchestration, and sink effects;
- messaging contracts own channel delivery meaning beyond protocol bytes;
- data types/shapes own semantic types, carrier compatibility, and loss;
- security owns policy decisions, secret/key custody, trust, privacy, and authorization;
- quality/reconciliation owns fitness, comparison, adjudication, and correction;
- lineage/provenance owns derivation and evidence claims;
- provider/target owns concrete organizations, offers, targets, limits, cost, qualification, and exit.

## Files

- `bounded-context-candidates.jsonl`, `capabilities.jsonl`, `operations.jsonl`, `decisions.jsonl`,
  and `lifecycles.jsonl` — domain model and typed behavior.
- `protocols.jsonl` — version/profile-aware protocol candidates; not a data-model or vendor list.
- `connector-classes.jsonl` — provider-neutral connector classes crosswalked to source classes.
- `implementation-artifacts.jsonl` and `deployed-connector-occurrences.jsonl` — deliberately
  unqualified test fixtures demonstrating the identity boundary.
- `evidence.jsonl` — primary/official protocol and source specifications with scoped use limits.
- `innovations-2021-2026.jsonl` — 26 recent non-generative protocol/access changes.
- `compiler-requirements.jsonl`, `capability-offer-templates.jsonl`, and
  `compiler-mappings.jsonl` — requirement/offer/binding candidates.
- `library-boundaries.jsonl` — pure, codec, runtime, provider-adapter and oracle seams.
- `conformance-tests.jsonl`, `negative-twins.jsonl`, and `examples/` — hostile, legacy and
  fail-closed qualification vocabulary.
- `cross-universe-mappings.jsonl`, `gaps.jsonl`, `coverage-report.json`, and `manifest.json` —
  integration, uncertainty, exact counts and package identity.
- `coverage-matrix.json` — validated crosswalk from every requested protocol and contract surface
  to protocol, connector-class, and bounded-context records.
- `schemas/` — Draft 2020-12 schemas, including connector class, implementation artifact, and
  deployed connector occurrence.
- `build_corpus.py` and `validate_corpus.py` — deterministic generator and validator.

## Rebuild and validate

```bash
python3 research/domain_atlas/universes/connectors_protocols/build_corpus.py
python3 research/domain_atlas/universes/connectors_protocols/validate_corpus.py
uv run --with jsonschema python research/domain_atlas/universes/connectors_protocols/validate_corpus.py
```

The validator checks schemas when `jsonschema` is available, otherwise retaining dependency-free
identity, reference, threshold, semantic-distinction, evidence, fixture-safety, crosswalk, count,
and deterministic-regeneration checks.
