# Provider-neutral source-system universe

This corpus defines what an enterprise source can truthfully provide before products,
connectors or industry solution packs are chosen. It expands the inherited 56-class seed into
171 stable, machine-readable capability classes across 17 families. Every class has explicit
authority, payload, interface, schema, time, order/finality, transaction, security, limit,
hazard and verification surfaces.

The registry is deliberately open-world. `171` is a researched coverage position, not a claim
that no future source behavior exists. An occurrence that does not match must produce a typed
`source-gap.*`; the compiler must not guess from a vendor name, file extension or industry
label.

## The boundary that prevents connector-driven products

```text
Capability class          Deployed occurrence            Connector/adapter
--------------------      ---------------------------    -------------------------
provider-neutral law  +   product/version/tenant/site +  implementation/protocol
payload semantics         field-level authority          executable operations
time/order/finality       observed numerical limits      conformance receipts
hazards/tests             security/network boundary      support/license/version
          \                         |                         /
           \---------------- compiler requirement match ---/
                              |
                    plan or typed refusal gap
```

- A **capability class** is a stable semantic and operational kind. Examples are
  `source.event_messaging_cdc.transaction_log_cdc` and
  `source.regulated_vertical.electronic_health_record`.
- A **source occurrence** is a concrete deployment. Vendor, product, tenant, region, version,
  numerical limits and exact permissions live here.
- A **connector** is an implementation with tested operations. A matching class label is not
  sufficient; its receipts must satisfy the requested assurance.
- An **acquisition plan** composes an occurrence and connector with snapshot/change handoff,
  reconciliation, budgets and security policy. It is not a source type.

One commercial deployment may map to several classes. For example, an enterprise suite can
expose ledger authority, workflow state, a content repository, an HTTP API and a change stream
with different guarantees. Those surfaces remain separate; the registry does not create one
vendor-shaped mega-class.

## Coverage

| Family | Classes | Representative semantics |
|---|---:|---|
| Operational database | 14 | relational, document, key-value, wide-column, graphs, search, time-series, spatial, vector, cache |
| Analytical repository | 9 | warehouse, lake table, raw lake, cube, semantic metrics, federation, features, arrays, caches |
| File, object and content | 14 | filesystem, object storage, text/fixed/row/columnar files, spreadsheets, archives, CMIS/content |
| API and remote service | 9 | HTTP, GraphQL, OData, SOAP, RPC, WebDAV, bulk export, report export, query endpoint |
| Event, messaging and CDC | 10 | append log, pub/sub, work queue, CDC, event journal, MQTT, webhook, EDI, media bus |
| Enterprise application | 18 | ERP/accounting, P2P, O2C, CRM, HR, SCM, WMS, TMS, MES, EAM, ITSM, commerce, EPM, MDM |
| Collaboration/productivity | 8 | email, calendar, chat, meetings, wiki, forms, tasks, design workspaces |
| Code and DevOps | 7 | Git, issue tracking, CI/CD, registries, BOMs, control plane, infrastructure state |
| Security and identity | 8 | directory, IdP, PAM/secrets, audit, SIEM, threat intel, vulnerability, network telemetry |
| Telemetry/digital experience | 6 | logs, metrics, traces, web, mobile, advertising/media measurement |
| IoT and edge | 7 | constrained APIs, gateways, twins, store-forward, meters, vehicles, mobile offline |
| Industrial/OT | 9 | SCADA/DCS, OPC UA, PLC, historian, building, robotics, inspection, batch, grid |
| Scientific/research | 8 | LIMS, instruments, scientific arrays, genomics, EDC, simulation, repository, HPC |
| Geospatial/media | 9 | features, raster/STAC, point cloud, CAD/BIM, image/audio/video, mobility, weather |
| Public/reference | 7 | data catalogs, SDMX, code registries, government registers, feeds, crawl, filings |
| Regulated vertical | 19 | health, finance, insurance, telecom, utilities, aviation, transit, maritime, pharma, government, education, land |
| Legacy/offline | 9 | mainframe, sequential/indexed, fixed batch, tape, spool, monitor, air gap, OCR, manual register |

`classification-axes.json` contains 19 controlled axes and 258 values. The class records use
those values, while deployment-specific details remain mandatory in an occurrence record.

## Exact contract surfaces

Every line in `source-classes.jsonl` expands the complete class contract:

1. stable identity, family and semantic profile;
2. authority role and field-level override requirement;
3. objects, logical models, payload shapes and identity scope;
4. discovery, read, write, change and access topologies;
5. schema mode, compatibility, registry, keys and unknown-field policy;
6. time axes, clock, calendar/timezone, cursor/watermark, lateness and retention;
7. ordering scope/key, gaps, duplicates, finality, corrections and deletes;
8. transaction boundary, consistency, snapshot cut and cross-object atomicity;
9. authentication, authorization, encryption, tenancy, audit and sensitivity;
10. rate/quota/page/payload/object/concurrency/retention/cursor/cost probes;
11. class-specific hazards; and
12. required verification tests and primary evidence references.

Numerical limits are intentionally **not** copied into a class. Limits change by product,
edition, tenant, contract, region and time. `source-occurrence.schema.json` requires a value,
unit, scope, provenance, observation time and failure behavior for every quantitative limit.
This is more exact than a stale universal number.

## Time, order and finality are independent

The registry does not collapse these concerns:

```text
event/effective time   when the business or physical fact applies
recorded/commit time   when a source accepted it
ingestion time         when a consumer observed it
ordering scope         global, transaction, partition, session, key, revision, or none
finality               commit, quorum, workflow approval, settlement, publication revision,
                       late-data window, provisional/corrected, device best effort, or never
deletion               hard, soft, tombstone, TTL, compaction, redaction, hold, supersession
```

This is why a queue, CDC log, webhook, human workflow and market feed cannot share a generic
“streaming source” contract.

## Verification and failure behavior

`verification-tests.json` defines 25 evidence-producing tests. They cover identity/authority,
capability discovery, repeatable cuts, paging under mutation, snapshot-to-change handoff,
checkpoint expiry, duplicates, order/gaps, replay/retention, every deletion form, schema/key
drift, clocks/lateness, correction/retraction, atomicity, security/tenancy, limit envelopes,
reconciliation, destructive writes, offline reconnection, content ACL/version behavior,
media fidelity and vertical conformance.

Allowed outcomes are `pass`, `fail`, `not_supported`, `not_authorized` and `inconclusive`.
Unsupported and unauthorized are not silently treated as empty data. Writes and industrial
commands compile read-only unless separately authorized and verified.

## Evidence posture

`evidence-sources.jsonl` records 54 primary sources from 34 issuers. They include IETF, W3C,
OASIS, Apache projects, HL7, DICOM/NEMA, OGC, ISO 20022, GS1, ISA, OPC Foundation, XBRL,
FIX, SDMX, GTFS/MobilityData, OpenID Foundation, Git, SQLite, PostgreSQL and other official
specification owners. Each record states only the surfaces it supports and explicitly refuses
to generalize that evidence to every deployment.

The primary sources establish real distinctions such as HTTP retry semantics, GraphQL partial
results, OData delta tokens, MQTT QoS and retained messages, log retention and partition order,
OPC UA subscriptions/security, FHIR version/profile conformance, DICOM transfer/media rules,
Parquet logical types/encryption, Avro reader-writer schema resolution, XBRL facts/units/taxonomy,
SDMX structures and GeoPackage offline integrity.

Evidence remains incomplete until clauses and content digests are pinned and independently
reviewed; this is recorded in `coverage-gaps.json`.

## Inherited 56-class audit

`inherited-audit.json` gives every inherited ID a stable replacement crosswalk. The inherited
seed used values outside its own declared axes (`event_stream`, `transaction_table`,
`clinical_record`, `metric_cube` and `source_defined`) and omitted authority, object discovery,
security, limits, cost, verification and evidence surfaces. It remains useful as migration
input, but is superseded for new mappings.

Some inherited composites split lawfully. For example:

- `source.scm_wms_tms` maps to supply-chain planning, warehouse management and transportation
  management;
- `source.application_logs_traces` maps to logs and distributed traces; and
- `source.project_service_management` maps to project/professional services and ITSM.

## Industry-pack integration

Industry records should reference stable `source.*` class IDs in `source_system_need` and add
the industry-specific objects, authority, code systems, time/finality and verification needs.
They should not place a vendor or connector name in that field. A later occurrence binding can
select concrete deployments.

Examples:

```text
retail return reconciliation
  -> source.enterprise_application.commerce_order_pos
  -> source.regulated_vertical.payments_ledger
  -> source.event_messaging_cdc.webhook_delivery

industrial bottleneck / downtime RCA
  -> source.enterprise_application.manufacturing_execution
  -> source.industrial_ot.industrial_historian
  -> source.industrial_ot.asset_maintenance (invalid: no such ID)
  -> source.enterprise_application.asset_maintenance (correct stable ID)
```

The invalid line illustrates fail-closed behavior: similar words are not enough to invent an ID.

## LLM and generative-system boundary

Generic model artifacts, feature repositories, vector indexes, experiment files and serving
telemetry are classifiable through existing core classes. An LLM provider is normally an HTTP,
RPC, event or artifact occurrence. Prompt, RAG, model-specific token, agent-memory and
generative semantics are not embedded in this core. A future extension must use a separate
namespace, depend one-way on these core contracts, and publish its own privacy/security and
evaluation profile.

## Files

- `source-classes.jsonl` — 171 fully expanded stable class records.
- `classification-axes.json` — controlled classification values.
- `source-system-class.schema.json` — class JSON Schema.
- `source-occurrence.schema.json` — concrete deployment and observed-limit schema.
- `connector-capability.schema.json` — adapter declaration and conformance-receipt schema.
- `unknown-source-gap.schema.json` — fail-closed extension-gap schema.
- `evidence-sources.jsonl` and `evidence-source.schema.json` — primary evidence corpus.
- `verification-tests.json` — executable verification vocabulary.
- `compiler-contract.json` — deterministic selection and refusal laws.
- `coverage-report.json` — generated quantitative coverage.
- `coverage-gaps.json` — explicit remaining research and assurance gaps.
- `inherited-audit.json` — inherited 56-class defects and complete crosswalk.
- `build_source_system_universe.py` — deterministic corpus generator.
- `validate_source_systems.py` — dependency-free audit plus optional JSON Schema validation.

## Rebuild and validate

```bash
python3 research/domain_atlas/universes/source_systems/build_source_system_universe.py
python3 research/domain_atlas/universes/source_systems/validate_source_systems.py
uv run --with jsonschema python research/domain_atlas/universes/source_systems/validate_source_systems.py
```

The last command performs Draft 2020-12 validation in addition to the dependency-free axis,
reference, crosswalk, evidence, minimum-depth and open-world checks.
