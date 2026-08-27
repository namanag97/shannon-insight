#!/usr/bin/env python3
"""Build the provider-neutral connector, adapter, and protocol research universe.

The seed tables are editorial conveniences.  Emitted records are candidates, never
credentials, live probes, vendor connector endorsements, or completeness claims.
"""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCHEMAS = HERE / "schemas"
EXAMPLES = HERE / "examples"
EDITION = 1
AS_OF = "2026-08-26"


def dump_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_jsonl(path: Path, values: list[dict]) -> None:
    path.write_text("".join(json.dumps(value, sort_keys=True) + "\n" for value in values), encoding="utf-8")


def slug(value: str) -> str:
    return value.lower().replace("/", "_").replace("-", "_").replace(" ", "_").replace(".", "_")


def ref_schema() -> dict:
    return {"type": "string", "pattern": "^[a-z][a-z0-9_.:-]+$"}


def refs_schema(min_items: int = 0) -> dict:
    return {"type": "array", "minItems": min_items, "uniqueItems": True, "items": ref_schema()}


def strings_schema(min_items: int = 0) -> dict:
    return {"type": "array", "minItems": min_items, "uniqueItems": True, "items": {"type": "string", "minLength": 1}}


def record_schema(title: str, id_field: str, required: list[str], properties: dict) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://san.example/domain-atlas/connectors-protocols/{id_field}.schema.json",
        "title": title,
        "type": "object",
        "additionalProperties": False,
        "required": [id_field, "edition", "status", *required],
        "properties": {
            id_field: ref_schema(),
            "edition": {"type": "integer", "minimum": 1},
            "status": {"enum": ["candidate", "hypothesis", "test_fixture", "deprecated_candidate", "open"]},
            **properties,
        },
    }


def build_schemas() -> None:
    SCHEMAS.mkdir(exist_ok=True)
    obj = {"type": "object"}
    schemas = {
        "bounded-context": record_schema("Connector/protocol bounded-context candidate", "context_id", ["name", "definition", "owns", "does_not_own", "aggregates", "invariants", "commands", "events", "refusals", "decision_refs", "evidence_refs", "gaps"], {
            "name": {"type": "string", "minLength": 3}, "definition": {"type": "string", "minLength": 20},
            "owns": strings_schema(1), "does_not_own": strings_schema(1), "aggregates": strings_schema(1),
            "invariants": strings_schema(2), "commands": strings_schema(1), "events": strings_schema(1),
            "refusals": strings_schema(1), "decision_refs": refs_schema(1), "evidence_refs": refs_schema(1), "gaps": strings_schema(),
        }),
        "protocol": record_schema("Protocol or access contract candidate", "protocol_id", ["name", "family", "layer", "not_data_model", "edition_profile", "transport_and_framing", "session_and_discovery", "operation_surface", "security", "schema_type_time", "change_and_resume", "delivery_semantics", "limits_and_errors", "versioning", "source_class_refs", "context_refs", "evidence_refs"], {
            "name": {"type": "string", "minLength": 2}, "family": {"type": "string"}, "layer": {"type": "string"}, "not_data_model": {"const": True},
            "edition_profile": obj, "transport_and_framing": obj, "session_and_discovery": obj,
            "operation_surface": obj, "security": obj, "schema_type_time": obj, "change_and_resume": obj,
            "delivery_semantics": obj, "limits_and_errors": obj, "versioning": obj,
            "source_class_refs": refs_schema(1), "context_refs": refs_schema(1), "evidence_refs": refs_schema(1),
        }),
        "capability": record_schema("Connector capability candidate", "capability_id", ["name", "owner_context_ref", "definition", "preconditions", "postconditions", "guarantees", "limitations", "operation_refs", "decision_refs", "evidence_refs"], {
            "name": {"type": "string"}, "owner_context_ref": ref_schema(), "definition": {"type": "string", "minLength": 20},
            "preconditions": strings_schema(1), "postconditions": strings_schema(1), "guarantees": strings_schema(1),
            "limitations": strings_schema(1), "operation_refs": refs_schema(1), "decision_refs": refs_schema(1), "evidence_refs": refs_schema(1),
        }),
        "operation": record_schema("Typed connector operation candidate", "operation_id", ["name", "owner_context_ref", "effect_kind", "input_contract", "output_contract", "preconditions", "postconditions", "failure_modes", "idempotency", "cancellation", "receipts", "evidence_refs"], {
            "name": {"type": "string"}, "owner_context_ref": ref_schema(),
            "effect_kind": {"enum": ["pure", "read", "write", "command", "subscription", "control", "probe"]},
            "input_contract": obj, "output_contract": obj, "preconditions": strings_schema(1), "postconditions": strings_schema(1),
            "failure_modes": strings_schema(2), "idempotency": {"type": "string"}, "cancellation": {"type": "string"},
            "receipts": strings_schema(1), "evidence_refs": refs_schema(1),
        }),
        "decision": record_schema("Connector decision point candidate", "decision_id", ["question", "owner_context_ref", "allowed_values", "default_law", "binding_phase", "required_evidence", "negative_twin"], {
            "question": {"type": "string", "minLength": 10}, "owner_context_ref": ref_schema(), "allowed_values": strings_schema(2),
            "default_law": {"enum": ["forbidden", "explicit_safe_constant", "probe_with_receipt"]},
            "binding_phase": {"enum": ["logical_planning", "physical_binding", "deployment_binding", "runtime_reconciliation", "evidence_verification"]},
            "required_evidence": strings_schema(1), "negative_twin": {"type": "string", "minLength": 10},
        }),
        "lifecycle": record_schema("Connector lifecycle candidate", "lifecycle_id", ["subject_kind", "states", "transitions", "terminal_states", "invalidation_triggers", "receipts"], {
            "subject_kind": {"type": "string"}, "states": strings_schema(3),
            "transitions": {"type": "array", "minItems": 2, "items": {"type": "object", "required": ["from", "command", "to", "guard"], "additionalProperties": False, "properties": {"from": {"type": "string"}, "command": {"type": "string"}, "to": {"type": "string"}, "guard": {"type": "string"}}}},
            "terminal_states": strings_schema(1), "invalidation_triggers": strings_schema(1), "receipts": strings_schema(1),
        }),
        "connector-class": record_schema("Provider-neutral connector class", "connector_class_id", ["name", "definition", "source_class_refs", "protocol_refs", "required_capability_refs", "operation_refs", "semantic_boundaries", "selection_requirements", "assurance_claims_forbidden", "evidence_refs"], {
            "name": {"type": "string"}, "definition": {"type": "string", "minLength": 20}, "source_class_refs": refs_schema(1),
            "protocol_refs": refs_schema(1), "required_capability_refs": refs_schema(1), "operation_refs": refs_schema(1),
            "semantic_boundaries": obj, "selection_requirements": strings_schema(2), "assurance_claims_forbidden": strings_schema(2), "evidence_refs": refs_schema(1),
        }),
        "implementation-artifact": record_schema("Connector implementation artifact", "artifact_id", ["name", "artifact_kind", "build_identity", "connector_class_refs", "protocol_profiles", "declared_capability_refs", "qualified_capability_refs", "dependency_lock", "license_supply_chain", "security_posture", "version_lifecycle", "conformance_receipt_refs", "binding_eligible"], {
            "name": {"type": "string"}, "artifact_kind": {"enum": ["reference_fixture", "library", "sidecar", "service", "runtime_plugin", "generated_adapter"]},
            "build_identity": obj, "connector_class_refs": refs_schema(1), "protocol_profiles": refs_schema(1),
            "declared_capability_refs": refs_schema(1), "qualified_capability_refs": refs_schema(), "dependency_lock": obj,
            "license_supply_chain": obj, "security_posture": obj, "version_lifecycle": obj,
            "conformance_receipt_refs": refs_schema(), "binding_eligible": {"type": "boolean"},
        }),
        "deployed-connector-occurrence": record_schema("Deployed connector occurrence or hostile fixture", "occurrence_id", ["occurrence_kind", "source_occurrence_ref", "connector_class_ref", "artifact_ref", "deployment_identity", "configuration_fingerprint", "credential_references_only", "enabled_operations", "documented_capabilities", "probed_behavior", "snapshot_cut_cursor_change", "schema_type_time_order_finality", "limits_rate_quota_cost", "retry_idempotency_cancellation", "partition_recovery", "observability_receipts", "qualification", "binding_eligible"], {
            "occurrence_kind": {"enum": ["registered_deployment_candidate", "hostile_test_fixture", "legacy_test_fixture"]},
            "source_occurrence_ref": {"type": ["string", "null"]}, "connector_class_ref": ref_schema(), "artifact_ref": ref_schema(),
            "deployment_identity": obj, "configuration_fingerprint": {"type": "string"}, "credential_references_only": {"const": True},
            "enabled_operations": refs_schema(1), "documented_capabilities": obj, "probed_behavior": obj,
            "snapshot_cut_cursor_change": obj, "schema_type_time_order_finality": obj, "limits_rate_quota_cost": obj,
            "retry_idempotency_cancellation": obj, "partition_recovery": obj, "observability_receipts": obj,
            "qualification": obj, "binding_eligible": {"type": "boolean"},
        }),
        "evidence": record_schema("Primary or official protocol evidence", "evidence_id", ["title", "issuer", "url", "authority", "source_kind", "supports_surfaces", "retrieved_on", "use_limit"], {
            "title": {"type": "string", "minLength": 4}, "issuer": {"type": "string", "minLength": 2},
            "url": {"type": "string", "pattern": "^https://"}, "authority": {"const": "primary"},
            "source_kind": {"enum": ["normative_standard", "official_specification", "official_implementation_documentation", "official_provider_contract", "standards_body_primary_overview", "standards_body_primary_catalogue"]},
            "supports_surfaces": strings_schema(1), "retrieved_on": {"type": "string", "format": "date"}, "use_limit": {"type": "string", "minLength": 30},
        }),
        "innovation": record_schema("Recent non-LLM connector/protocol innovation", "innovation_id", ["name", "year", "change", "why_material", "non_llm", "protocol_refs", "evidence_refs", "limitations"], {
            "name": {"type": "string"}, "year": {"type": "integer", "minimum": 2021, "maximum": 2026},
            "change": {"type": "string", "minLength": 15}, "why_material": {"type": "string", "minLength": 15}, "non_llm": {"const": True},
            "protocol_refs": refs_schema(1), "evidence_refs": refs_schema(1), "limitations": strings_schema(1),
        }),
        "compiler-contract": record_schema("Connector compiler requirement, offer, or mapping", "compiler_record_id", ["record_kind", "subject_ref", "capability_refs", "operation_refs", "guarantees", "prohibited_traits", "evidence_gates", "binding_phase", "fallback_law"], {
            "record_kind": {"enum": ["requirement", "offer_template", "mapping"]}, "subject_ref": ref_schema(),
            "capability_refs": refs_schema(1), "operation_refs": refs_schema(1), "guarantees": strings_schema(1),
            "prohibited_traits": strings_schema(1), "evidence_gates": strings_schema(1),
            "binding_phase": {"enum": ["logical_planning", "physical_binding", "deployment_binding", "runtime_reconciliation", "evidence_verification"]},
            "fallback_law": {"enum": ["refuse", "typed_degradation_only_if_declared"]},
        }),
        "library-boundary": record_schema("Connector library boundary", "library_id", ["name", "owner_context_ref", "library_kind", "effect_boundary", "owns", "must_not_own", "public_contracts", "dependencies", "receipts", "removal_seams", "evidence_refs"], {
            "name": {"type": "string"}, "owner_context_ref": ref_schema(),
            "library_kind": {"enum": ["semantic_pure", "policy_pure", "protocol_codec", "runtime_mechanism", "provider_adapter", "test_oracle"]},
            "effect_boundary": {"enum": ["pure_no_io", "pure_effect_intents", "effectful_runtime", "provider_boundary"]},
            "owns": strings_schema(1), "must_not_own": strings_schema(2), "public_contracts": strings_schema(1),
            "public_traits": strings_schema(), "operation_refs": refs_schema(), "decision_refs": refs_schema(),
            "input_types": strings_schema(), "output_types": strings_schema(), "configuration_contracts": strings_schema(),
            "error_contracts": strings_schema(), "laws": strings_schema(), "oracles": strings_schema(),
            "resource_contracts": strings_schema(), "concurrency": strings_schema(), "cancellation": strings_schema(),
            "dependencies": strings_schema(), "receipts": strings_schema(1), "removal_seams": strings_schema(1), "evidence_refs": refs_schema(1),
        }),
        "conformance-test": record_schema("Connector conformance test", "test_id", ["name", "scope", "preconditions", "stimulus", "oracle", "expected_receipts", "allowed_outcomes", "distinguishes", "destructive", "evidence_refs"], {
            "name": {"type": "string"}, "scope": {"type": "string"}, "preconditions": strings_schema(1), "stimulus": strings_schema(1),
            "oracle": strings_schema(1), "expected_receipts": strings_schema(1),
            "allowed_outcomes": {"type": "array", "uniqueItems": True, "items": {"enum": ["pass", "fail", "not_supported", "not_authorized", "inconclusive"]}},
            "distinguishes": strings_schema(1), "destructive": {"type": "boolean"}, "evidence_refs": refs_schema(1),
        }),
        "crosswalk": record_schema("Read-only cross-universe mapping", "crosswalk_id", ["local_refs", "external_universe", "external_path", "external_refs", "reference_status", "relationship", "ownership_law"], {
            "local_refs": refs_schema(1), "external_universe": {"type": "string"}, "external_path": {"type": "string"},
            "external_refs": refs_schema(1), "reference_status": {"enum": ["materialized_validated", "generator_contract_surface"]},
            "relationship": {"type": "string"}, "ownership_law": {"type": "string"},
        }),
        "gap": record_schema("Open connector/protocol research gap", "gap_id", ["subject_ref", "gap_kind", "blocking", "known", "unknown", "resolution_condition", "prohibited_assumption", "evidence_refs"], {
            "subject_ref": ref_schema(), "gap_kind": {"type": "string"}, "blocking": {"type": "boolean"},
            "known": {"type": "string"}, "unknown": {"type": "string"}, "resolution_condition": {"type": "string"},
            "prohibited_assumption": {"type": "string"}, "evidence_refs": refs_schema(1),
        }),
        "negative-twin": record_schema("Semantic negative twin", "twin_id", ["left", "right", "unsafe_collapse", "compiler_response", "test_refs"], {
            "left": {"type": "string"}, "right": {"type": "string"}, "unsafe_collapse": {"type": "string"},
            "compiler_response": {"type": "string"}, "test_refs": refs_schema(1),
        }),
    }
    for name, schema in schemas.items():
        dump_json(SCHEMAS / f"{name}.schema.json", schema)


# id, name, sovereign subject, first capability, second capability, first operation, second operation, decision question
CONTEXT_ROWS = [
    ("source_connector_identity", "Source–connector identity", "classifies source class, connector class, artifact and occurrence separately", "classify connector role", "bind source occurrence", "classify connector", "bind occurrence", "Which identity layer is being asserted?"),
    ("protocol_profile", "Protocol profile", "owns edition and negotiated feature subsets", "declare profile", "negotiate profile", "declare protocol profile", "negotiate protocol profile", "Which protocol edition and extensions are admissible?"),
    ("endpoint_addressing", "Endpoint and addressing", "owns endpoint identity, authority, routes and address scopes", "resolve endpoint", "canonicalize address", "resolve endpoint", "canonicalize endpoint", "Which authority and route identify the remote surface?"),
    ("connection_contract", "Connection contract", "owns editioned provider-neutral connection declarations and occurrence bindings without opening a transport", "validate connection declaration", "bind connection occurrence", "validate connection declaration", "bind connection occurrence", "Which declaration, occurrence and binding edition identify the requested connection?"),
    ("session_connection", "Session and connection", "owns connection establishment, pooling, affinity and teardown", "open session", "pool sessions", "open session", "close session", "What state is bound to a connection or session?"),
    ("capability_discovery", "Capability discovery", "owns advertised features and probeable operations", "discover capabilities", "compare advertised observed", "fetch capability document", "probe capability", "Is a capability documented, probed, or both?"),
    ("namespace_discovery", "Namespace discovery", "owns discoverable catalogs, schemas, folders, topics and devices", "list namespaces", "discover objects", "list namespaces", "describe object", "What discovery breadth is authorized and complete?"),
    ("schema_introspection", "Schema introspection", "owns remote declarations, constraints and compatibility metadata", "read schema", "diff schema", "introspect schema", "diff source schema", "Is the schema declared, inferred, sampled, or opaque?"),
    ("type_mapping", "Protocol type mapping", "owns loss-aware mapping between remote and semantic types", "map type", "preserve unknown type", "map remote type", "emit type gap", "Which conversions are lossless under qualifiers?"),
    ("serialization_framing", "Serialization and framing", "owns bytes, frames, envelopes, compression and integrity checks", "encode frame", "decode frame", "encode request frame", "decode response frame", "Which framing and compression profile is active?"),
    ("authentication", "Connector authentication", "owns authentication mechanism use without owning secret material", "authenticate workload", "refresh credential", "authenticate session", "refresh credential reference", "Which authentication proof and channel binding are required?"),
    ("authorization_scope", "Authorization scope", "owns requested scopes, object privileges and least-privilege checks", "derive minimum scope", "verify access denial", "request authorization", "probe authorization boundary", "Which permissions are necessary for each operation?"),
    ("secret_reference", "Secret reference and rotation", "owns opaque secret references, refresh and rotation behavior", "resolve secret reference", "rotate connection", "resolve secret reference", "rotate authenticated session", "How does rotation invalidate sessions and checkpoints?"),
    ("network_security", "Network and channel security", "owns TLS, peer identity, proxies, tunnels and network policy", "establish secure channel", "verify peer", "open protected transport", "verify channel policy", "Which network trust boundary and peer identity are valid?"),
    ("query_request", "Query request", "owns remote query preparation, parameters, deadlines and result identity", "prepare query", "execute query", "prepare query", "execute query", "Is query identity stable across retries and pagination?"),
    ("point_range_read", "Point and range read", "owns keyed reads, byte ranges and conditional requests", "read point", "read range", "read point", "read range", "What consistency and conditional-read preconditions apply?"),
    ("pagination", "Pagination", "owns page traversal, continuation identity and mutation hazards", "start page walk", "continue page walk", "read first page", "resume page token", "Is continuation positional, snapshot-bound, or mutable?"),
    ("snapshot_cut", "Snapshot cut", "owns the source-consistent boundary selected for extraction", "select cut", "verify cut", "begin snapshot", "verify snapshot cut", "What commits and objects are included in the cut?"),
    ("bulk_job", "Bulk export/import job", "owns asynchronous job submission, progress, completion and artifacts", "submit bulk job", "collect bulk result", "submit bulk export", "collect completed export", "Does job acceptance differ from export completion?"),
    ("file_transfer", "File and object transfer", "owns resumable byte movement, integrity and atomic publication", "start transfer", "resume transfer", "transfer object", "verify transferred object", "What makes a partial transfer visible or complete?"),
    ("read_cursor", "Read cursor", "owns traversal position for a read operation", "issue read cursor", "resume read cursor", "issue read cursor", "resume read cursor", "Is the token only a read position or also a change checkpoint?"),
    ("change_capture", "Change capture", "owns change envelopes, before/after images and delete exposure", "start change capture", "decode change", "subscribe changes", "decode change record", "Which source commit boundary is exposed?"),
    ("cdc_resume", "CDC resume", "owns durable change-log position, retention and gap detection", "checkpoint change token", "resume change token", "persist resume token", "resume change feed", "Can the resume token expire or cross topology changes?"),
    ("snapshot_change_handoff", "Snapshot/change handoff", "owns common cuts, overlap, deduplication and reconciliation", "plan handoff", "verify no loss", "capture handoff token", "reconcile handoff", "Is there a verified common cut between snapshot and changes?"),
    ("subscription", "Subscription", "owns durable or ephemeral subscription identity and filters", "create subscription", "renew subscription", "create subscription", "renew subscription", "Who owns subscription state and expiry?"),
    ("webhook_delivery", "Webhook delivery", "owns callback registration, verification, delivery and redelivery", "register callback", "acknowledge delivery", "register webhook", "acknowledge webhook", "Does transport acknowledgement prove source acceptance?"),
    ("event_message_settlement", "Event/message settlement", "owns delivery, acknowledgement, rejection and settlement state", "receive message", "settle message", "receive message", "settle delivery", "At what scope is delivery settled?"),
    ("partition_assignment", "Partition assignment", "owns shard discovery, leasing, rebalance and ownership epochs", "discover partitions", "claim partition", "list partitions", "renew partition lease", "How are ownership epochs fenced during rebalance?"),
    ("ordering", "Ordering", "owns order scope, sequence identifiers, gaps and reorder tolerance", "observe sequence", "detect gap", "read sequence", "report order gap", "Is ordering global, partitioned, transactional, or absent?"),
    ("time_watermark", "Time and watermark", "owns source clocks, event/commit time, skew and progress frontiers", "map source time", "observe watermark", "read time metadata", "advance watermark", "Which clock and time axis governs progress?"),
    ("finality_correction", "Finality, correction and retraction", "owns provisional/final states and later corrections", "classify finality", "apply correction", "observe finality", "process retraction", "Can an accepted record later be corrected or retracted?"),
    ("transaction_boundary", "Remote transaction boundary", "owns begin/commit/abort scope and observed atomicity", "begin transaction", "commit transaction", "begin remote transaction", "commit remote transaction", "What objects and writes share an atomic boundary?"),
    ("write_mutation", "Write and mutation", "owns create/update/delete/upsert preconditions and effects", "prepare mutation", "apply mutation", "prepare mutation", "apply mutation", "Which mutation semantics and conditional guards apply?"),
    ("command_acceptance", "Command and source acceptance", "owns command submission, source acknowledgement and terminal outcome", "submit command", "observe command result", "submit source command", "poll command result", "Does transport success mean accepted, committed, or merely queued?"),
    ("idempotency", "Idempotency and deduplication", "owns request keys, effect identity and deduplication windows", "derive idempotency key", "verify duplicate effect", "submit idempotent request", "probe duplicate request", "At what scope and duration are duplicate effects suppressed?"),
    ("retry", "Retry", "owns retry eligibility, classification, delay and budget", "classify retry", "schedule retry", "classify remote failure", "retry request", "Which failures are safe and useful to retry?"),
    ("cancellation", "Cancellation", "owns propagation, remote cancellation and in-flight effect disposition", "request cancellation", "reconcile cancellation", "cancel remote work", "observe cancellation outcome", "Can work be stopped, or only observation abandoned?"),
    ("backpressure_flow", "Backpressure and flow control", "owns credits, windows, demand, buffering and overload behavior", "grant demand", "throttle ingress", "request demand", "apply backpressure", "Which layer can slow the producer without loss?"),
    ("rate_limit", "Rate limiting", "owns rate envelopes, reset signals and throttling receipts", "observe rate limit", "pace requests", "read rate headers", "throttle requests", "Are limits per identity, tenant, endpoint, or resource?"),
    ("quota_cost", "Quota and cost", "owns quotas, billable units, egress and preflight budget", "estimate cost", "reserve quota", "estimate request cost", "observe quota consumption", "Which finite budgets can refuse a plan before execution?"),
    ("recovery_replay", "Recovery and replay", "owns checkpoint restore, replay ranges and terminal loss", "plan recovery", "execute replay", "restore connector state", "replay source interval", "What state and retention are required for recovery?"),
    ("observability", "Connector observability", "owns health, metrics, logs, traces and lag without owning truth", "emit telemetry", "observe health", "emit connector telemetry", "measure connector lag", "Which signal is observation rather than correctness proof?"),
    ("receipt_evidence", "Receipts and evidence", "owns scoped execution, acceptance and conformance receipts", "issue receipt", "verify receipt", "record transport receipt", "record source receipt", "Which authority issued the receipt and what does it prove?"),
    ("version_negotiation", "Version negotiation", "owns protocol/server/client compatibility and downgrade", "negotiate version", "refuse incompatible version", "negotiate protocol", "record negotiated version", "Which downgrade changes semantics or security?"),
    ("deprecation_exit", "Deprecation and exit", "owns announced withdrawal, migration, overlap and removal", "announce deprecation", "migrate profile", "observe deprecation", "retire connector profile", "What evidence permits removal of an old profile?"),
    ("license_supply_chain", "License and supply chain", "owns license, redistribution, dependencies, provenance and attestations", "evaluate license", "verify artifact provenance", "inspect dependency lock", "verify artifact attestation", "Is the implementation legally and operationally deployable?"),
    ("implementation_qualification", "Implementation qualification", "owns declared versus tested support and invalidation", "qualify artifact", "invalidate qualification", "run conformance suite", "issue qualification receipt", "Which artifact/version/configuration was actually tested?"),
    ("deployment_binding", "Connector deployment binding", "owns occurrence configuration, placement and credential references", "bind deployment", "invalidate deployment", "register occurrence", "revalidate occurrence", "Which mutable deployment facts affect eligibility?"),
    ("connector_lifecycle", "Connector lifecycle", "owns desired and observed connector states, legal transitions, configuration editions, task divergence and disposition planning", "plan connector transition", "classify connector health", "plan connector transition", "classify connector health", "Which connector, task, configuration, run and observation editions govern the transition?"),
    ("industrial_command_safety", "Industrial command safety", "owns read-only default, interlocks and command authorization evidence", "authorize industrial command", "verify interlock", "submit guarded command", "observe device acknowledgement", "What safety authority permits a physical command?"),
    ("legacy_record_transport", "Legacy record transport", "owns blocking, code pages, record lengths, tapes and checkpoints", "decode legacy records", "checkpoint legacy transfer", "read blocked records", "translate code page", "Which record and character conventions are proven?"),
    ("browser_client_telemetry", "Browser/client telemetry", "owns client event collection, batching, unload delivery and privacy signals", "collect client telemetry", "flush telemetry", "enqueue client beacon", "observe telemetry delivery", "Does browser enqueue success prove collector acceptance?"),
    ("domain_profile_conformance", "Domain protocol profile conformance", "owns healthcare, finance, EDI, geospatial and OT profile constraints", "select domain profile", "validate conformance", "validate domain message", "emit conformance gap", "Which profile, code system and implementation guide applies?"),
    ("gap_refusal", "Connector gap and refusal", "owns unknown-capability gaps and typed compilation refusal", "emit connector gap", "resolve connector gap", "classify missing evidence", "refuse unsafe binding", "Which missing fact blocks binding rather than degrading?"),
]


CONTEXT_EVIDENCE = {
    "connection_contract": "evidence.cp.kafka_connect_api42", "connector_lifecycle": "evidence.cp.kafka_connect_user42",
    "authentication": "evidence.cp.rfc6749", "authorization_scope": "evidence.cp.rfc6749", "secret_reference": "evidence.cp.rfc8705",
    "network_security": "evidence.cp.rfc8446", "query_request": "evidence.cp.http_semantics", "pagination": "evidence.cp.odata401",
    "snapshot_cut": "evidence.cp.postgresql_mvcc", "bulk_job": "evidence.cp.fhir_bulk", "file_transfer": "evidence.cp.nfs41",
    "change_capture": "evidence.cp.postgresql_logical", "cdc_resume": "evidence.cp.mongodb_change", "snapshot_change_handoff": "evidence.cp.debezium",
    "webhook_delivery": "evidence.cp.websub", "event_message_settlement": "evidence.cp.amqp10", "partition_assignment": "evidence.cp.kafka_protocol",
    "ordering": "evidence.cp.kafka_protocol", "time_watermark": "evidence.cp.cloudevents", "transaction_boundary": "evidence.cp.postgresql_mvcc",
    "write_mutation": "evidence.cp.http_semantics", "command_acceptance": "evidence.cp.http_semantics", "idempotency": "evidence.cp.http_semantics",
    "retry": "evidence.cp.http_semantics", "cancellation": "evidence.cp.grpc", "backpressure_flow": "evidence.cp.http2",
    "rate_limit": "evidence.cp.http_semantics", "observability": "evidence.cp.opentelemetry", "receipt_evidence": "evidence.cp.tracecontext",
    "version_negotiation": "evidence.cp.http_semantics", "license_supply_chain": "evidence.cp.spdx3", "industrial_command_safety": "evidence.cp.opcua",
    "legacy_record_transport": "evidence.cp.tn3270e", "browser_client_telemetry": "evidence.cp.beacon", "domain_profile_conformance": "evidence.cp.fhir_r5",
}


EXTRA_EVIDENCE = [
    # id, title, issuer, URL, kind, supported surfaces
    ("rfc9110", "RFC 9110 HTTP Semantics", "IETF", "https://www.rfc-editor.org/rfc/rfc9110.html", "normative_standard", ["methods", "status", "idempotency", "retry"]),
    ("rfc9112", "RFC 9112 HTTP/1.1", "IETF", "https://www.rfc-editor.org/rfc/rfc9112.html", "normative_standard", ["framing", "connections"]),
    ("rfc9113", "RFC 9113 HTTP/2", "IETF", "https://www.rfc-editor.org/rfc/rfc9113.html", "normative_standard", ["multiplexing", "flow_control", "cancellation"]),
    ("rfc9114", "RFC 9114 HTTP/3", "IETF", "https://www.rfc-editor.org/rfc/rfc9114.html", "normative_standard", ["quic", "streams", "cancellation"]),
    ("rfc9000", "RFC 9000 QUIC", "IETF", "https://www.rfc-editor.org/rfc/rfc9000.html", "normative_standard", ["transport", "streams", "recovery"]),
    ("rfc9297", "RFC 9297 HTTP Datagrams and Capsule Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc9297.html", "normative_standard", ["http_datagrams", "capsules", "extensions"]),
    ("rfc9293", "RFC 9293 TCP", "IETF", "https://www.rfc-editor.org/rfc/rfc9293.html", "normative_standard", ["transport", "ordering"]),
    ("rfc8446", "RFC 8446 TLS 1.3", "IETF", "https://www.rfc-editor.org/rfc/rfc8446.html", "normative_standard", ["encryption", "peer_authentication"]),
    ("rfc6455", "RFC 6455 WebSocket Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc6455.html", "normative_standard", ["duplex", "framing"]),
    ("rfc9457", "RFC 9457 Problem Details for HTTP APIs", "IETF", "https://www.rfc-editor.org/rfc/rfc9457.html", "normative_standard", ["errors", "retry_classification"]),
    ("rfc8259", "RFC 8259 JSON", "IETF", "https://www.rfc-editor.org/rfc/rfc8259.html", "normative_standard", ["serialization", "numbers"]),
    ("rfc8949", "RFC 8949 CBOR", "IETF", "https://www.rfc-editor.org/rfc/rfc8949.html", "normative_standard", ["serialization", "canonicalization"]),
    ("rfc6749", "RFC 6749 OAuth 2.0", "IETF", "https://www.rfc-editor.org/rfc/rfc6749.html", "normative_standard", ["authorization", "tokens"]),
    ("rfc6750", "RFC 6750 OAuth Bearer Token Usage", "IETF", "https://www.rfc-editor.org/rfc/rfc6750.html", "normative_standard", ["authentication", "errors"]),
    ("rfc7636", "RFC 7636 PKCE", "IETF", "https://www.rfc-editor.org/rfc/rfc7636.html", "normative_standard", ["authorization", "client_security"]),
    ("rfc8705", "RFC 8705 OAuth Mutual TLS", "IETF", "https://www.rfc-editor.org/rfc/rfc8705.html", "normative_standard", ["channel_binding", "authentication"]),
    ("rfc8693", "RFC 8693 OAuth Token Exchange", "IETF", "https://www.rfc-editor.org/rfc/rfc8693.html", "normative_standard", ["delegation", "tokens"]),
    ("rfc9449", "RFC 9449 OAuth DPoP", "IETF", "https://www.rfc-editor.org/rfc/rfc9449.html", "normative_standard", ["sender_constrained_token", "replay"]),
    ("openid", "OpenID Connect Core 1.0", "OpenID Foundation", "https://openid.net/specs/openid-connect-core-1_0.html", "normative_standard", ["identity", "tokens"]),
    ("openapi32", "OpenAPI Specification 3.2.0", "OpenAPI Initiative", "https://spec.openapis.org/oas/v3.2.0.html", "official_specification", ["api_description", "schema", "security"]),
    ("openapi31", "OpenAPI Specification 3.1.0", "OpenAPI Initiative", "https://spec.openapis.org/oas/v3.1.0.html", "official_specification", ["api_description", "json_schema", "webhooks"]),
    ("graphql2025", "GraphQL Specification September 2025", "GraphQL Foundation", "https://spec.graphql.org/September2025/", "official_specification", ["query", "schema", "partial_results"]),
    ("graphql_http", "GraphQL over HTTP", "GraphQL Foundation", "https://graphql.github.io/graphql-over-http/draft/", "official_specification", ["http_binding", "media_types", "status"]),
    ("grpc", "gRPC Core Concepts", "Cloud Native Computing Foundation", "https://grpc.io/docs/what-is-grpc/core-concepts/", "official_specification", ["rpc", "streaming", "deadlines", "cancellation"]),
    ("protobuf", "Protocol Buffers Language Specification", "Google", "https://protobuf.dev/reference/protobuf/proto3-spec/", "official_specification", ["schema", "serialization", "compatibility"]),
    ("soap12", "SOAP Version 1.2", "W3C", "https://www.w3.org/TR/soap12-part1/", "normative_standard", ["envelope", "faults", "bindings"]),
    ("wsdl20", "Web Services Description Language 2.0", "W3C", "https://www.w3.org/TR/wsdl20/", "normative_standard", ["service_description", "operations"]),
    ("odata401", "OData Version 4.01 Protocol", "OASIS Open", "https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html", "normative_standard", ["query", "pagination", "delta", "batch"]),
    ("webdav", "RFC 4918 WebDAV", "IETF", "https://www.rfc-editor.org/rfc/rfc4918.html", "normative_standard", ["content", "locking", "properties"]),
    ("scim", "RFC 7644 SCIM Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc7644.html", "normative_standard", ["identity", "pagination", "bulk"]),
    ("websub", "WebSub Recommendation", "W3C", "https://www.w3.org/TR/websub/", "normative_standard", ["webhook", "subscription", "verification"]),
    ("sse", "Server-sent events", "WHATWG", "https://html.spec.whatwg.org/multipage/server-sent-events.html", "normative_standard", ["event_stream", "reconnect"]),
    ("cloudevents", "CloudEvents Specification 1.0.2", "Cloud Native Computing Foundation", "https://github.com/cloudevents/spec/blob/ce@v1.0.2/cloudevents/spec.md", "official_specification", ["event_envelope", "identity", "time"]),
    ("asyncapi3", "AsyncAPI Specification 3.0", "AsyncAPI Initiative", "https://www.asyncapi.com/docs/reference/specification/v3.0.0", "official_specification", ["event_api_description", "channels", "operations"]),
    ("amqp10", "AMQP Version 1.0", "OASIS Open", "https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-complete-v1.0-os.html", "normative_standard", ["messaging", "settlement", "flow_control"]),
    ("mqtt5", "MQTT Version 5.0", "OASIS Open", "https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html", "normative_standard", ["messaging", "qos", "session", "retained"]),
    ("kafka_protocol", "Apache Kafka Protocol", "Apache Software Foundation", "https://kafka.apache.org/protocol.html", "official_implementation_documentation", ["messaging", "partitions", "offsets", "transactions"]),
    ("kafka_connect", "Kafka Connect", "Apache Software Foundation", "https://kafka.apache.org/documentation/#connect", "official_implementation_documentation", ["connectors", "offsets", "tasks"]),
    ("kafka_connect_api42", "Apache Kafka 4.2 Connector API", "Apache Software Foundation", "https://kafka.apache.org/42/javadoc/org/apache/kafka/connect/connector/Connector.html", "official_implementation_documentation", ["configuration", "validation", "start", "stop", "reconfiguration", "tasks"]),
    ("kafka_connect_user42", "Apache Kafka 4.2 Connect User Guide", "Apache Software Foundation", "https://kafka.apache.org/42/kafka-connect/user-guide/", "official_implementation_documentation", ["connector_lifecycle", "task_status", "pause", "stop", "resume", "restart", "deletion", "offset_management"]),
    ("kafka_kraft", "Kafka KRaft Metadata Quorum", "Apache Software Foundation", "https://kafka.apache.org/documentation/#kraft", "official_implementation_documentation", ["metadata_quorum", "discovery", "failover"]),
    ("kafka_kip848", "KIP-848 Next Generation Consumer Rebalance Protocol", "Apache Software Foundation", "https://cwiki.apache.org/confluence/display/KAFKA/KIP-848%3A+The+Next+Generation+of+the+Consumer+Rebalance+Protocol", "official_specification", ["consumer_groups", "rebalance", "assignment_epoch"]),
    ("stomp12", "STOMP Protocol 1.2", "STOMP Project", "https://stomp.github.io/stomp-specification-1.2.html", "official_specification", ["messaging", "acknowledgement", "transactions"]),
    ("nats_protocol", "NATS Client Protocol", "NATS Authors", "https://docs.nats.io/reference/reference-protocols/nats-protocol", "official_implementation_documentation", ["messaging", "subjects", "flow"]),
    ("jms3", "Jakarta Messaging 3.1", "Eclipse Foundation", "https://jakarta.ee/specifications/messaging/3.1/", "normative_standard", ["messaging_api", "delivery", "transactions"]),
    ("coap", "RFC 7252 CoAP", "IETF", "https://www.rfc-editor.org/rfc/rfc7252.html", "normative_standard", ["iot", "requests", "retransmission"]),
    ("dds", "DDS 1.4", "Object Management Group", "https://www.omg.org/spec/DDS/1.4/", "normative_standard", ["industrial_pubsub", "qos", "discovery"]),
    ("postgres_wire", "PostgreSQL Frontend/Backend Protocol", "PostgreSQL Global Development Group", "https://www.postgresql.org/docs/current/protocol.html", "official_implementation_documentation", ["database_wire", "authentication", "query"]),
    ("postgres_logical", "PostgreSQL Logical Decoding", "PostgreSQL Global Development Group", "https://www.postgresql.org/docs/current/logicaldecoding.html", "official_implementation_documentation", ["cdc", "slots", "lsn"]),
    ("mysql_protocol", "MySQL Client/Server Protocol", "Oracle", "https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_PROTOCOL.html", "official_implementation_documentation", ["database_wire", "authentication", "query"]),
    ("mysql_binlog", "MySQL Binary Log", "Oracle", "https://dev.mysql.com/doc/refman/8.4/en/binary-log.html", "official_implementation_documentation", ["cdc", "position", "transactions"]),
    ("tds", "Tabular Data Stream Protocol", "Microsoft", "https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tds/", "official_specification", ["database_wire", "query", "transactions"]),
    ("mongo_wire", "MongoDB Wire Protocol", "MongoDB", "https://www.mongodb.com/docs/manual/reference/mongodb-wire-protocol/", "official_implementation_documentation", ["database_wire", "commands", "compression"]),
    ("cql", "Cassandra Native Protocol v5", "Apache Software Foundation", "https://cassandra.apache.org/doc/latest/cassandra/reference/native-protocol.html", "official_implementation_documentation", ["database_wire", "query", "paging"]),
    ("resp3", "Redis Serialization Protocol", "Redis", "https://redis.io/docs/latest/develop/reference/protocol-spec/", "official_implementation_documentation", ["database_wire", "commands", "push"]),
    ("bolt", "Bolt Protocol", "Neo4j", "https://neo4j.com/docs/bolt/current/", "official_implementation_documentation", ["database_wire", "query", "transactions"]),
    ("flight_sql", "Arrow Flight SQL", "Apache Software Foundation", "https://arrow.apache.org/docs/format/FlightSql.html", "official_specification", ["query", "bulk", "grpc"]),
    ("odbc", "ODBC Specification", "Microsoft", "https://learn.microsoft.com/en-us/sql/odbc/reference/odbc-programmer-s-reference", "official_specification", ["database_api", "types", "transactions"]),
    ("jdbc", "JDBC 4.3 Specification", "Oracle", "https://download.oracle.com/otndocs/jcp/jdbc-4_3-mrel3-spec/index.html", "official_specification", ["database_api", "types", "transactions"]),
    ("sparql", "SPARQL 1.1 Protocol", "W3C", "https://www.w3.org/TR/sparql11-protocol/", "normative_standard", ["graph_query", "http_binding", "results"]),
    ("ldap", "RFC 4511 LDAP Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc4511.html", "normative_standard", ["directory", "operations", "controls"]),
    ("posix", "POSIX.1-2024 System Interfaces", "The Open Group", "https://pubs.opengroup.org/onlinepubs/9799919799/", "normative_standard", ["filesystem", "files", "atomicity"]),
    ("nfs41", "RFC 8881 NFSv4.1", "IETF", "https://www.rfc-editor.org/rfc/rfc8881.html", "normative_standard", ["network_filesystem", "state", "recovery"]),
    ("smb3", "MS-SMB2 SMB Protocol", "Microsoft", "https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/", "official_specification", ["network_filesystem", "sessions", "durability"]),
    ("ftp", "RFC 959 FTP", "IETF", "https://www.rfc-editor.org/rfc/rfc959.html", "normative_standard", ["file_transfer", "restart", "representations"]),
    ("ftps", "RFC 4217 Securing FTP with TLS", "IETF", "https://www.rfc-editor.org/rfc/rfc4217.html", "normative_standard", ["file_transfer", "tls"]),
    ("sftp", "OpenSSH sftp Manual", "OpenBSD Project", "https://man.openbsd.org/sftp", "official_implementation_documentation", ["file_transfer", "resume", "authentication"]),
    ("rsync", "rsync Technical Report", "Samba Project", "https://rsync.samba.org/tech_report/", "official_specification", ["file_transfer", "delta", "integrity"]),
    ("s3_api", "Amazon S3 API Reference", "Amazon Web Services", "https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html", "official_provider_contract", ["object_api", "pagination", "multipart"]),
    ("oci_distribution", "OCI Distribution Specification", "Open Container Initiative", "https://github.com/opencontainers/distribution-spec/blob/main/spec.md", "official_specification", ["artifact_transfer", "content_identity", "pagination"]),
    ("cmis", "CMIS 1.1", "OASIS Open", "https://docs.oasis-open.org/cmis/CMIS/v1.1/CMIS-v1.1.html", "normative_standard", ["content", "versions", "acl"]),
    ("tus", "tus Resumable Upload Protocol 1.0", "tus Project", "https://tus.io/protocols/resumable-upload", "official_specification", ["upload", "resume", "offset"]),
    ("opcua", "OPC UA Specifications", "OPC Foundation", "https://reference.opcfoundation.org/specifications", "normative_standard", ["industrial", "browse", "subscription", "security"]),
    ("modbus", "Modbus Application Protocol V1.1b3", "Modbus Organization", "https://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf", "normative_standard", ["industrial", "registers", "commands"]),
    ("bacnet", "BACnet Standard", "ASHRAE", "https://www.ashrae.org/technical-resources/bookstore/bacnet", "standards_body_primary_overview", ["building_automation", "objects", "services"]),
    ("iec61850", "IEC 61850 Overview", "International Electrotechnical Commission", "https://iec61850.dvl.iec.ch/", "standards_body_primary_overview", ["power_system", "substation", "messages"]),
    ("dnp3", "DNP3 Specifications", "DNP Users Group", "https://www.dnp.org/Resources/Standards", "standards_body_primary_catalogue", ["industrial", "telecontrol", "time"]),
    ("mtconnect", "MTConnect Standard", "MTConnect Institute", "https://docs.mtconnect.org/", "normative_standard", ["industrial", "devices", "observations"]),
    ("sparkplug3", "Sparkplug Specification 3.0", "Eclipse Foundation", "https://sparkplug.eclipse.org/specification/", "official_specification", ["industrial", "mqtt", "state"]),
    ("onem2m", "oneM2M Specifications", "oneM2M", "https://www.onem2m.org/technical/published-specifications", "standards_body_primary_catalogue", ["iot", "resources", "subscriptions"]),
    ("matter", "Matter Specification", "Connectivity Standards Alliance", "https://csa-iot.org/developer-resource/specifications-download-request/", "standards_body_primary_catalogue", ["iot", "commissioning", "interaction"]),
    ("fhir_r5", "HL7 FHIR R5", "HL7 International", "https://hl7.org/fhir/R5/", "normative_standard", ["healthcare", "rest", "resources", "profiles"]),
    ("fhir_bulk", "FHIR Bulk Data Access 2.0", "HL7 International", "https://hl7.org/fhir/uv/bulkdata/STU2/", "normative_standard", ["healthcare", "bulk_export", "jobs"]),
    ("dicom", "DICOM Current Standard", "DICOM Standards Committee", "https://www.dicomstandard.org/current", "normative_standard", ["medical_imaging", "dimse", "dicomweb"]),
    ("hl7v2", "HL7 Version 2.9", "HL7 International", "https://www.hl7.org/implement/standards/product_brief.cfm?product_id=516", "standards_body_primary_overview", ["healthcare", "messages", "acknowledgement"]),
    ("ihe", "IHE Technical Frameworks", "Integrating the Healthcare Enterprise", "https://www.ihe.net/resources/technical_frameworks/", "standards_body_primary_catalogue", ["healthcare", "profiles", "transactions"]),
    ("fix", "FIX Technical Standards", "FIX Trading Community", "https://www.fixtrading.org/standards/", "standards_body_primary_catalogue", ["finance", "sessions", "orders", "market_data"]),
    ("fixp", "FIX Performance Session Layer", "FIX Trading Community", "https://www.fixtrading.org/standards/fixp/", "normative_standard", ["finance", "session", "sequencing"]),
    ("iso20022", "ISO 20022 Message Catalogue", "ISO 20022 Registration Authority", "https://www.iso20022.org/catalogue-messages", "standards_body_primary_catalogue", ["finance", "messages", "versions"]),
    ("xbrl", "XBRL Specifications", "XBRL International", "https://specifications.xbrl.org/", "standards_body_primary_catalogue", ["finance", "filings", "taxonomy"]),
    ("ofx", "Open Financial Exchange 2.3", "Financial Data Exchange", "https://financialdataexchange.org/FDX/FDX/About/OFX-Work-Group.aspx", "standards_body_primary_overview", ["finance", "exchange", "messages"]),
    ("edifact", "UN/EDIFACT", "UNECE", "https://unece.org/trade/uncefact/unedifact", "standards_body_primary_catalogue", ["edi", "directories", "messages"]),
    ("x12", "X12 Standards", "X12", "https://x12.org/products/standards", "standards_body_primary_catalogue", ["edi", "transactions", "versions"]),
    ("as2", "RFC 4130 AS2", "IETF", "https://www.rfc-editor.org/rfc/rfc4130.html", "normative_standard", ["edi", "receipts", "security"]),
    ("as4", "AS4 Profile of ebMS 3.0", "OASIS Open", "https://docs.oasis-open.org/ebxml-msg/ebms/v3.0/profiles/200707/as4-profile.html", "normative_standard", ["edi", "receipts", "reliability"]),
    ("ebms3", "ebXML Messaging Services 3.0", "OASIS Open", "https://docs.oasis-open.org/ebxml-msg/ebms/v3.0/core/os/ebms_core-3.0-spec-os.html", "normative_standard", ["edi", "messaging", "reliability"]),
    ("epcis", "EPCIS 2.0.1", "GS1", "https://ref.gs1.org/standards/epcis/2.0.1/", "normative_standard", ["supply_chain", "events", "query"]),
    ("ogc_features", "OGC API Features Part 1", "Open Geospatial Consortium", "https://docs.ogc.org/is/17-069r4/17-069r4.html", "normative_standard", ["geospatial", "features", "pagination"]),
    ("wfs", "OGC Web Feature Service 2.0", "Open Geospatial Consortium", "https://docs.ogc.org/is/09-025r2/09-025r2.html", "normative_standard", ["geospatial", "features", "transactions"]),
    ("stac", "STAC Specification 1.1", "STAC Project", "https://github.com/radiantearth/stac-spec/tree/v1.1.0", "official_specification", ["geospatial", "catalog", "assets"]),
    ("sensorthings", "OGC SensorThings API 1.1", "Open Geospatial Consortium", "https://docs.ogc.org/is/18-088/18-088.html", "normative_standard", ["iot", "observations", "pagination"]),
    ("zarr3", "Zarr Storage Specification 3", "Zarr Developers", "https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html", "official_specification", ["scientific", "arrays", "chunks"]),
    ("netcdf", "NetCDF Format Specifications", "Unidata", "https://docs.unidata.ucar.edu/netcdf-c/current/file_format_specifications.html", "official_specification", ["scientific", "arrays", "types"]),
    ("hdf5", "HDF5 File Format Specification", "The HDF Group", "https://support.hdfgroup.org/documentation/hdf5/latest/_f_m_t3.html", "official_specification", ["scientific", "arrays", "hierarchy"]),
    ("imap", "RFC 9051 IMAP4rev2", "IETF", "https://www.rfc-editor.org/rfc/rfc9051.html", "normative_standard", ["email", "mailbox", "sequence"]),
    ("smtp", "RFC 5321 SMTP", "IETF", "https://www.rfc-editor.org/rfc/rfc5321.html", "normative_standard", ["email", "delivery", "reply"]),
    ("jmap", "RFC 8620 JMAP", "IETF", "https://www.rfc-editor.org/rfc/rfc8620.html", "normative_standard", ["collaboration", "state", "changes"]),
    ("caldav", "RFC 4791 CalDAV", "IETF", "https://www.rfc-editor.org/rfc/rfc4791.html", "normative_standard", ["calendar", "webdav", "time"]),
    ("carddav", "RFC 6352 CardDAV", "IETF", "https://www.rfc-editor.org/rfc/rfc6352.html", "normative_standard", ["contacts", "webdav", "sync"]),
    ("activitystreams", "Activity Streams 2.0", "W3C", "https://www.w3.org/TR/activitystreams-core/", "normative_standard", ["collaboration", "activities", "collections"]),
    ("tn3270e", "RFC 2355 TN3270E", "IETF", "https://www.rfc-editor.org/rfc/rfc2355.html", "normative_standard", ["mainframe", "terminal", "records"]),
    ("drda", "IBM Distributed Relational Database Architecture", "IBM", "https://www.ibm.com/docs/en/db2/11.5.x?topic=standards-distributed-relational-database-architecture-drda", "official_implementation_documentation", ["mainframe", "database_wire", "distributed_unit_of_work"]),
    ("iscsi", "RFC 7143 iSCSI", "IETF", "https://www.rfc-editor.org/rfc/rfc7143.html", "normative_standard", ["block_storage", "sessions", "recovery"]),
    ("nvmeof", "NVMe over Fabrics", "NVM Express", "https://nvmexpress.org/specifications/", "standards_body_primary_catalogue", ["block_storage", "transport", "queues"]),
    ("opentelemetry", "OpenTelemetry Specification", "Cloud Native Computing Foundation", "https://opentelemetry.io/docs/specs/otel/", "official_specification", ["telemetry", "logs", "metrics", "traces"]),
    ("otlp", "OpenTelemetry Protocol", "Cloud Native Computing Foundation", "https://opentelemetry.io/docs/specs/otlp/", "official_specification", ["telemetry_transport", "retry", "partial_success"]),
    ("tracecontext", "Trace Context", "W3C", "https://www.w3.org/TR/trace-context/", "normative_standard", ["trace_identity", "propagation", "security"]),
    ("beacon", "Beacon", "W3C", "https://www.w3.org/TR/beacon/", "normative_standard", ["browser", "telemetry", "enqueue"]),
    ("reporting", "Reporting API", "W3C", "https://www.w3.org/TR/reporting-1/", "normative_standard", ["browser", "reports", "delivery"]),
    ("navigation_timing", "Navigation Timing Level 2", "W3C", "https://www.w3.org/TR/navigation-timing-2/", "normative_standard", ["browser", "timing", "privacy"]),
    ("spdx3", "SPDX Specification 3.0", "Linux Foundation", "https://spdx.github.io/spdx-spec/v3.0/", "normative_standard", ["license", "provenance", "supply_chain"]),
    ("cyclonedx16", "CycloneDX 1.6", "OWASP Foundation", "https://cyclonedx.org/docs/1.6/json/", "normative_standard", ["sbom", "dependencies", "attestation"]),
    ("slsa1", "SLSA Version 1.0", "OpenSSF", "https://slsa.dev/spec/v1.0/", "normative_standard", ["build_provenance", "supply_chain"]),
    ("debezium", "Debezium Connector Documentation", "Debezium Project", "https://debezium.io/documentation/reference/stable/connectors/index.html", "official_implementation_documentation", ["cdc", "snapshot", "resume", "schema"]),
    ("debezium_signaling", "Debezium Signaling and Incremental Snapshots", "Debezium Project", "https://debezium.io/documentation/reference/stable/configuration/signalling.html", "official_implementation_documentation", ["incremental_snapshot", "signaling", "watermarks"]),
    ("postgres_logical_protocol", "PostgreSQL Logical Replication Protocol", "PostgreSQL Global Development Group", "https://www.postgresql.org/docs/current/protocol-logical-replication.html", "official_implementation_documentation", ["logical_replication", "streaming_transactions", "two_phase"]),
]


SOURCE_DEFAULTS = {
    "db": ["source.operational_database.relational_transactional"],
    "file": ["source.file_object_content.local_or_network_filesystem"],
    "object": ["source.file_object_content.object_storage"],
    "api": ["source.api_remote_service.http_resource_api"],
    "event": ["source.event_messaging_cdc.publish_subscribe_topic"],
    "cdc": ["source.event_messaging_cdc.transaction_log_cdc"],
    "bulk": ["source.api_remote_service.bulk_export_api"],
    "iot": ["source.iot_edge.constrained_device_api"],
    "ot": ["source.industrial_ot.opcua_information_server"],
    "health": ["source.regulated_vertical.electronic_health_record"],
    "finance": ["source.regulated_vertical.trading_order_execution"],
    "edi": ["source.event_messaging_cdc.edi_mailbox_gateway"],
    "geo": ["source.geospatial_media.gis_feature_service"],
    "science": ["source.scientific_research.multidimensional_scientific_file"],
    "collab": ["source.collaboration_productivity.email_mailbox"],
    "legacy": ["source.legacy_offline.mainframe_relational_or_hierarchical"],
    "block": ["source.file_object_content.binary_proprietary_file"],
    "telemetry": ["source.telemetry_digital_experience.application_logs"],
}


SOURCE_OVERRIDES = {
    "sparql11_protocol": ["source.operational_database.rdf_triplestore"],
    "ldapv3": ["source.security_identity.identity_directory"],
    "postgresql_logical_replication": ["source.event_messaging_cdc.transaction_log_cdc"],
    "mysql_binary_log": ["source.event_messaging_cdc.transaction_log_cdc"],
    "webhook_http": ["source.event_messaging_cdc.webhook_delivery"],
    "websub": ["source.event_messaging_cdc.webhook_delivery"],
    "kafka_wire": ["source.event_messaging_cdc.partitioned_append_log"],
    "nats_jetstream": ["source.event_messaging_cdc.partitioned_append_log"],
    "mqtt5": ["source.event_messaging_cdc.mqtt_broker"],
    "fhir_r5_rest": ["source.regulated_vertical.electronic_health_record"],
    "dicomweb": ["source.regulated_vertical.medical_imaging_pacs"],
    "dicom_dimse": ["source.regulated_vertical.medical_imaging_pacs"],
    "fix_session": ["source.regulated_vertical.trading_order_execution", "source.regulated_vertical.market_data_feed"],
    "fixp": ["source.regulated_vertical.market_data_feed"],
    "iso20022_messages": ["source.regulated_vertical.payments_ledger"],
    "xbrl_reporting": ["source.regulated_vertical.regulatory_xbrl_filing"],
    "stac11": ["source.geospatial_media.raster_remote_sensing_catalog"],
    "sensorthings11": ["source.geospatial_media.weather_environmental_observation"],
    "caldav": ["source.collaboration_productivity.calendar_scheduling"],
    "activitystreams20": ["source.collaboration_productivity.team_chat"],
    "trace_context": ["source.telemetry_digital_experience.distributed_traces"],
    "beacon": ["source.telemetry_digital_experience.web_product_analytics"],
    "reporting_api": ["source.telemetry_digital_experience.web_product_analytics"],
    "navigation_timing2": ["source.telemetry_digital_experience.web_product_analytics"],
}


# id|name|family|layer|edition|evidence key|context key
PROTOCOL_TEXT = """
postgresql_wire|PostgreSQL frontend/backend protocol|db|database_wire|current|postgres_wire|query_request
postgresql_logical_replication|PostgreSQL logical replication protocol|cdc|change_protocol|current|postgres_logical|cdc_resume
mysql_client_server|MySQL client/server protocol|db|database_wire|8.4|mysql_protocol|query_request
mysql_binary_log|MySQL binary-log replication stream|cdc|change_protocol|8.4|mysql_binlog|cdc_resume
tds|Tabular Data Stream|db|database_wire|open-specification|tds|query_request
mongodb_wire|MongoDB wire protocol|db|database_wire|current|mongo_wire|query_request
cassandra_native_v5|Cassandra native protocol v5|db|database_wire|v5|cql|pagination
redis_resp3|Redis serialization protocol 3|db|database_wire|RESP3|resp3|serialization_framing
neo4j_bolt|Bolt protocol|db|database_wire|current|bolt|query_request
arrow_flight_sql|Arrow Flight SQL|db|query_rpc|current|flight_sql|bulk_job
odbc43|ODBC API contract|db|client_api|4.x|odbc|type_mapping
jdbc43|JDBC API contract|db|client_api|4.3|jdbc|transaction_boundary
sparql11_protocol|SPARQL 1.1 protocol|db|query_http|1.1|sparql|query_request
ldapv3|LDAPv3|db|directory_wire|v3|ldap|namespace_discovery
drda|Distributed Relational Database Architecture|legacy|database_wire|current|drda|query_request
posix_file_io|POSIX file interfaces|file|filesystem_api|2024|posix|file_transfer
nfs41|Network File System v4.1|file|network_filesystem|4.1|nfs41|recovery_replay
smb3|Server Message Block 3|file|network_filesystem|3.x|smb3|file_transfer
ftp|File Transfer Protocol|file|file_transfer|RFC959|ftp|file_transfer
ftps|FTP over TLS|file|file_transfer|RFC4217|ftps|network_security
sftp|SSH File Transfer|file|file_transfer|implementation-profile|sftp|file_transfer
rsync|rsync delta-transfer protocol|file|file_transfer|technical-report|rsync|file_transfer
webdav|WebDAV|file|content_http|RFC4918|webdav|file_transfer
s3_rest|S3-compatible object REST profile|object|object_http|provider-profile|s3_api|file_transfer
oci_distribution|OCI Distribution|object|artifact_http|1.x|oci_distribution|file_transfer
cmis_browser|CMIS Browser Binding|file|content_http|1.1|cmis|namespace_discovery
tus10|tus resumable upload|file|upload_http|1.0|tus|file_transfer
http11|HTTP/1.1|api|application_transport|RFC9112|rfc9112|session_connection
http2|HTTP/2|api|application_transport|RFC9113|rfc9113|backpressure_flow
http3|HTTP/3|api|application_transport|RFC9114|rfc9114|session_connection
openapi32|OpenAPI-described HTTP API|api|interface_description|3.2.0|openapi32|capability_discovery
graphql2025|GraphQL|api|query_language_protocol|September2025|graphql2025|query_request
graphql_over_http|GraphQL over HTTP|api|http_binding|draft-profile|graphql_http|query_request
grpc|gRPC|api|binary_rpc|current|grpc|cancellation
soap12|SOAP 1.2|api|message_envelope|1.2|soap12|serialization_framing
wsdl20|WSDL 2.0|api|service_description|2.0|wsdl20|capability_discovery
odata401|OData 4.01|api|data_api|4.01|odata401|pagination
scim2|SCIM 2.0|api|identity_api|RFC7644|scim|pagination
websocket|WebSocket|event|duplex_transport|RFC6455|rfc6455|session_connection
webhook_http|HTTP webhook profile|event|callback_delivery|HTTP-profile|rfc9110|webhook_delivery
websub|WebSub|event|subscription_delivery|Recommendation|websub|subscription
server_sent_events|Server-sent events|event|event_stream|living-standard|sse|subscription
cloudevents10|CloudEvents|event|event_envelope|1.0.2|cloudevents|serialization_framing
asyncapi30|AsyncAPI-described event interface|event|interface_description|3.0.0|asyncapi3|capability_discovery
amqp10|AMQP 1.0|event|message_protocol|1.0|amqp10|event_message_settlement
mqtt5|MQTT 5.0|event|message_protocol|5.0|mqtt5|event_message_settlement
kafka_wire|Kafka protocol|event|partitioned_log_protocol|current|kafka_protocol|partition_assignment
kafka_connect|Kafka Connect runtime contract|event|connector_runtime|current|kafka_connect|implementation_qualification
stomp12|STOMP 1.2|event|message_protocol|1.2|stomp12|event_message_settlement
nats_core|NATS client protocol|event|message_protocol|current|nats_protocol|event_message_settlement
nats_jetstream|NATS JetStream consumer protocol|event|durable_stream_protocol|current|nats_protocol|cdc_resume
jakarta_messaging31|Jakarta Messaging API|event|messaging_api|3.1|jms3|transaction_boundary
coap|Constrained Application Protocol|iot|constrained_resource|RFC7252|coap|retry
dds14|Data Distribution Service|ot|industrial_pubsub|1.4|dds|subscription
odata_batch|OData batch requests|bulk|bulk_http|4.01|odata401|bulk_job
scim_bulk|SCIM bulk operation|bulk|bulk_http|RFC7644|scim|bulk_job
s3_multipart|S3 multipart upload|bulk|bulk_object|provider-profile|s3_api|bulk_job
fhir_bulk20|FHIR Bulk Data Access|bulk|bulk_export|STU2|fhir_bulk|bulk_job
grpc_streaming|gRPC streaming|bulk|streaming_rpc|current|grpc|backpressure_flow
opcua|OPC Unified Architecture|ot|industrial_information|current|opcua|industrial_command_safety
modbus_tcp|Modbus TCP|ot|industrial_register|1.1b3|modbus|industrial_command_safety
bacnet|BACnet|ot|building_automation|current|bacnet|domain_profile_conformance
iec61850|IEC 61850 communication profile|ot|power_automation|current|iec61850|industrial_command_safety
dnp3|DNP3|ot|telecontrol|current|dnp3|industrial_command_safety
mtconnect|MTConnect|ot|machine_observation|current|mtconnect|domain_profile_conformance
sparkplug30|Sparkplug 3.0|ot|industrial_mqtt_profile|3.0|sparkplug3|change_capture
onem2m|oneM2M service layer|iot|iot_resource_protocol|current|onem2m|subscription
matter|Matter interaction model|iot|iot_interaction|current|matter|industrial_command_safety
fhir_r5_rest|FHIR RESTful API|health|health_resource_api|R5|fhir_r5|domain_profile_conformance
dicomweb|DICOMweb|health|medical_imaging_http|current|dicom|file_transfer
dicom_dimse|DICOM DIMSE|health|medical_imaging_message|current|dicom|event_message_settlement
hl7v2_mllp|HL7 v2 over MLLP profile|health|health_message|2.9-profile|hl7v2|domain_profile_conformance
ihe_xds|IHE document-sharing transactions|health|health_profile|current|ihe|domain_profile_conformance
fix_session|FIX session protocol|finance|market_message|current|fix|ordering
fixp|FIX Performance Session Layer|finance|market_session|current|fixp|ordering
iso20022_messages|ISO 20022 message exchange|finance|financial_message|catalogue|iso20022|domain_profile_conformance
xbrl_reporting|XBRL filing exchange|finance|financial_reporting|current|xbrl|schema_introspection
ofx23|Open Financial Exchange|finance|financial_message|2.3|ofx|domain_profile_conformance
un_edifact|UN/EDIFACT interchange|edi|edi_message|directories|edifact|legacy_record_transport
x12_edi|X12 interchange|edi|edi_message|release-specific|x12|legacy_record_transport
as2|Applicability Statement 2|edi|secure_edi_transport|RFC4130|as2|receipt_evidence
as4|Applicability Statement 4|edi|secure_edi_transport|profile|as4|receipt_evidence
ebms3|ebXML Messaging 3.0|edi|reliable_b2b_message|3.0|ebms3|event_message_settlement
epcis20|EPCIS 2.0|edi|supply_chain_event_api|2.0.1|epcis|change_capture
ogc_api_features|OGC API Features|geo|geospatial_http|Part1|ogc_features|pagination
wfs20|Web Feature Service|geo|geospatial_xml|2.0|wfs|query_request
stac11|SpatioTemporal Asset Catalog|geo|geospatial_catalog|1.1|stac|namespace_discovery
sensorthings11|SensorThings API|geo|observation_api|1.1|sensorthings|pagination
zarr3|Zarr storage protocol|science|chunked_array|3.0|zarr3|file_transfer
netcdf|NetCDF file contract|science|scientific_file|current|netcdf|type_mapping
hdf5|HDF5 file contract|science|scientific_file|current|hdf5|schema_introspection
imap4rev2|IMAP4rev2|collab|mailbox_protocol|RFC9051|imap|read_cursor
smtp|SMTP|collab|mail_transfer|RFC5321|smtp|command_acceptance
jmap|JMAP core|collab|collaboration_api|RFC8620|jmap|cdc_resume
caldav|CalDAV|collab|calendar_http|RFC4791|caldav|time_watermark
carddav|CardDAV|collab|contact_http|RFC6352|carddav|change_capture
activitystreams20|Activity Streams|collab|activity_model_protocol|2.0|activitystreams|pagination
tn3270e|TN3270E|legacy|terminal_record|RFC2355|tn3270e|legacy_record_transport
fixed_record_ftp|Fixed-record FTP profile|legacy|batch_file_transfer|site-profile|ftp|legacy_record_transport
ebcdic_blocked_file|EBCDIC blocked-record file profile|legacy|record_file|site-profile|posix|legacy_record_transport
iscsi|iSCSI|block|block_transport|RFC7143|iscsi|recovery_replay
nvme_over_fabrics|NVMe over Fabrics|block|block_transport|current|nvmeof|recovery_replay
otlp|OpenTelemetry Protocol|telemetry|telemetry_transport|current|otlp|observability
trace_context|W3C Trace Context|telemetry|context_propagation|Recommendation|tracecontext|receipt_evidence
beacon|Beacon API|telemetry|browser_delivery|Recommendation|beacon|browser_client_telemetry
reporting_api|Reporting API|telemetry|browser_reporting|working-draft|reporting|browser_client_telemetry
navigation_timing2|Navigation Timing Level 2|telemetry|browser_measurement|Recommendation|navigation_timing|browser_client_telemetry
"""


def evidence_records() -> list[dict]:
    records: list[dict] = []
    upstream = ROOT / "domain_atlas/universes/source_systems/evidence-sources.jsonl"
    for line in upstream.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        source = json.loads(line)
        records.append({
            **source,
            "evidence_id": "evidence.cp.upstream." + source["evidence_id"].removeprefix("ev."),
            "status": "candidate",
            "edition": EDITION,
            "use_limit": "Read-only crosswalk to source-system evidence. " + source["use_limit"],
        })
    for key, title, issuer, url, kind, surfaces in EXTRA_EVIDENCE:
        records.append({
            "evidence_id": f"evidence.cp.{key}", "edition": EDITION, "status": "candidate",
            "title": title, "issuer": issuer, "url": url, "authority": "primary", "source_kind": kind,
            "supports_surfaces": surfaces, "retrieved_on": AS_OF,
            "use_limit": "Supports the named protocol surfaces only; it does not prove a connector implementation, deployment configuration, entitlement, limit, or observed behavior.",
        })
    # Prefer the connector-specific record when a URL is also present upstream.
    by_url: dict[str, dict] = {}
    for record in records:
        if record["url"] not in by_url or ".upstream." not in record["evidence_id"]:
            by_url[record["url"]] = record
    return sorted(by_url.values(), key=lambda item: item["evidence_id"])


def context_records(evidence_ids: set[str]) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    contexts: list[dict] = []
    capabilities: list[dict] = []
    operations: list[dict] = []
    decisions: list[dict] = []
    fallback_evidence = "evidence.cp.rfc9110"
    if fallback_evidence not in evidence_ids:
        fallback_evidence = sorted(evidence_ids)[0]
    for key, name, subject, cap_a, cap_b, op_a, op_b, question in CONTEXT_ROWS:
        context_id = f"context.cp.{key}"
        decision_id = f"decision.cp.{key}"
        operation_ids = [f"operation.cp.{slug(op_a)}", f"operation.cp.{slug(op_b)}"]
        capability_ids = [f"capability.cp.{slug(cap_a)}", f"capability.cp.{slug(cap_b)}"]
        evidence_ref = CONTEXT_EVIDENCE.get(key, fallback_evidence)
        if evidence_ref not in evidence_ids:
            evidence_ref = fallback_evidence
        contexts.append({
            "context_id": context_id, "edition": EDITION, "status": "candidate", "name": name,
            "definition": f"Provider-neutral bounded context that {subject}; it does not classify a vendor product or own source semantics.",
            "owns": [subject, "explicit unknowns and scoped evidence for this subject"],
            "does_not_own": ["source-system business authority", "pipeline orchestration", "provider marketing identity"],
            "aggregates": [name + " contract", name + " receipt"],
            "invariants": ["Documented capability and probed behavior remain distinct.", "Unknown or unverified semantics produce a typed gap rather than an inferred guarantee."],
            "commands": [op_a, op_b], "events": [f"{key}.declared", f"{key}.observed", f"{key}.invalidated"],
            "refusals": [f"Refuse binding when {question.lower()} is unanswered and material to correctness or safety."],
            "decision_refs": [decision_id], "evidence_refs": [evidence_ref], "gaps": [],
        })
        decisions.append({
            "decision_id": decision_id, "edition": EDITION, "status": "candidate", "question": question,
            "owner_context_ref": context_id, "allowed_values": ["explicitly_declared", "observed_with_receipt", "unsupported", "unknown"],
            "default_law": "forbidden", "binding_phase": "physical_binding",
            "required_evidence": ["versioned protocol or implementation declaration", "scope-bound conformance or observation receipt"],
            "negative_twin": "A similar name, transport success, or neighboring capability is not evidence for this decision.",
        })
        for index, (cap_name, op_id) in enumerate(zip((cap_a, cap_b), operation_ids)):
            capability_id = capability_ids[index]
            capabilities.append({
                "capability_id": capability_id, "edition": EDITION, "status": "candidate", "name": cap_name.title(),
                "owner_context_ref": context_id,
                "definition": f"Capability to {cap_name} under the explicit {name.lower()} contract and evidence scope.",
                "preconditions": ["source occurrence and connector artifact identities are distinct", "protocol profile and authorization are explicit"],
                "postconditions": [f"A scoped {cap_name} result or typed refusal is emitted."],
                "guarantees": ["No guarantee exceeds the narrower of protocol law, implementation qualification, deployment configuration, and source behavior."],
                "limitations": ["Candidate definition; no live occurrence or credential is asserted."],
                "operation_refs": [op_id], "decision_refs": [decision_id], "evidence_refs": [evidence_ref],
            })
            effect = "probe" if any(word in op_id for word in ("probe", "verify", "observe", "inspect", "measure", "classify")) else "read"
            if any(word in op_id for word in ("apply", "submit", "commit", "create", "register", "acknowledge", "settle")):
                effect = "command"
            if any(word in op_id for word in ("encode", "decode", "map", "canonicalize", "derive")):
                effect = "pure"
            operations.append({
                "operation_id": op_id, "edition": EDITION, "status": "candidate", "name": op_id.rsplit(".", 1)[-1].replace("_", " ").title(),
                "owner_context_ref": context_id, "effect_kind": effect,
                "input_contract": {"requires": ["connector_class", "protocol_profile", "source_occurrence_or_fixture"], "authority": "caller_declaration"},
                "output_contract": {"returns": ["typed_result_or_refusal", "scoped_receipt"], "authority": "source_or_connector_as_labeled"},
                "preconditions": ["required decisions are bound", "credentials are opaque references and operation-specific authorization is present"],
                "postconditions": ["documented assertions and observations remain separately labeled", "all continuation state is typed by purpose"],
                "failure_modes": ["unsupported", "not_authorized", "invalid_profile", "remote_failure", "inconclusive"],
                "idempotency": "Declared per effect boundary; read safety does not prove write-effect idempotency.",
                "cancellation": "Reports whether remote work stopped, continued, or became unknown; local abandonment is not remote cancellation.",
                "receipts": ["transport_outcome", "source_acceptance_if_available", "continuation_or_terminal_state"], "evidence_refs": [evidence_ref],
            })

    # The two product-facing pure contracts each need a third operation that is
    # intentionally a plan, not an ambient effect.  Keep these operations in
    # their semantic owners while runtime execution remains behind a port.
    context_by_id = {item["context_id"]: item for item in contexts}
    for context_key, operation_name, evidence_ref in [
        ("connection_contract", "plan connection revocation", "evidence.cp.kafka_connect_api42"),
        ("connector_lifecycle", "plan connector revocation", "evidence.cp.kafka_connect_user42"),
    ]:
        context_id = f"context.cp.{context_key}"
        operation_id = f"operation.cp.{slug(operation_name)}"
        context_by_id[context_id]["commands"].append(operation_name)
        operations.append({
            "operation_id": operation_id, "edition": EDITION, "status": "candidate",
            "name": operation_name.title(), "owner_context_ref": context_id, "effect_kind": "pure",
            "input_contract": {"requires": ["connector_identity", "current_edition", "requested_disposition"], "authority": "caller_declaration"},
            "output_contract": {"returns": ["typed_effect_intent_or_refusal", "deterministic_decision_trace"], "authority": "semantic_contract_only"},
            "preconditions": ["current identity and edition are explicit", "the requested transition is named"],
            "postconditions": ["no network, process, secret-store, offset-store, or provider effect has occurred", "the plan records required authority and evidence"],
            "failure_modes": ["unknown_identity", "stale_edition", "illegal_transition", "authority_missing", "disposition_ambiguous"],
            "idempotency": "Equal canonical inputs produce the same plan digest; executing the plan is a separate operation.",
            "cancellation": "Not applicable to the bounded pure calculation.",
            "receipts": ["deterministic_plan_trace", "typed_refusal_if_any"], "evidence_refs": [evidence_ref],
        })
    return contexts, capabilities, operations, decisions


def protocol_records(evidence_ids: set[str]) -> list[dict]:
    records = []
    for raw in PROTOCOL_TEXT.strip().splitlines():
        key, name, family, layer, edition, evidence_key, context_key = raw.split("|")
        evidence_ref = f"evidence.cp.{evidence_key}"
        if evidence_ref not in evidence_ids:
            # Crosswalked evidence may carry the same official source under an upstream ID.
            candidates = sorted(e for e in evidence_ids if e.endswith("." + evidence_key))
            evidence_ref = candidates[0] if candidates else "evidence.cp.rfc9110"
        records.append({
            "protocol_id": f"protocol.cp.{key}", "edition": EDITION, "status": "candidate", "name": name,
            "family": family, "layer": layer, "not_data_model": True,
            "edition_profile": {"profile": edition, "negotiation_required": True, "extensions_must_be_enumerated": True},
            "transport_and_framing": {"binding": "profile_specific", "framing": "must_be_declared", "compression": "must_be_declared", "integrity": "must_be_verified_or_unknown"},
            "session_and_discovery": {"session_scope": "protocol_specific", "discovery": "documented_or_probed", "affinity": "must_be_observed"},
            "operation_surface": {"read": "profile_specific", "write": "disabled_until_separately_authorized", "change": "only_when_explicit", "command": "fail_closed"},
            "security": {"authentication": "profile_and_occurrence_specific", "authorization": "operation_and_object_specific", "secret_material": "reference_only", "channel": "explicit"},
            "schema_type_time": {"schema": "declared_inferred_or_opaque", "type_mapping": "loss_annotated", "time_axes": "source_profile_specific", "timezone": "never_inferred"},
            "change_and_resume": {"read_cursor": "not_interchangeable_with_cdc_resume", "cdc_resume": "protocol_specific", "retention_expiry": "terminal_gap_unless_rebootstrap"},
            "delivery_semantics": {"ordering": "scoped", "finality": "source_owned", "exactly_once": "not_claimed_end_to_end", "transport_success": "not_source_acceptance"},
            "limits_and_errors": {"numerical_defaults": "forbidden", "rate_quota_cost": "occurrence_observed", "retry": "classified", "cancellation": "disposition_required"},
            "versioning": {"compatibility": "profile_specific", "deprecation": "tracked", "invalidation_triggers": ["protocol edition", "server version", "artifact version", "configuration", "security policy"]},
            "source_class_refs": SOURCE_OVERRIDES.get(key, SOURCE_DEFAULTS[family]), "context_refs": [f"context.cp.{context_key}"], "evidence_refs": [evidence_ref],
        })
    return records


CONNECTOR_CLASS_ROWS = [
    # key, name, protocol keys, source class refs
    ("relational_query_reader", "Relational query reader", ["postgresql_wire", "mysql_client_server", "tds", "odbc43", "jdbc43"], ["source.operational_database.relational_transactional"]),
    ("distributed_sql_reader", "Distributed SQL query reader", ["postgresql_wire", "arrow_flight_sql", "jdbc43"], ["source.operational_database.distributed_relational"]),
    ("document_query_reader", "Document query reader", ["mongodb_wire", "http11"], ["source.operational_database.document"]),
    ("key_value_command_reader", "Key/value command reader", ["redis_resp3"], ["source.operational_database.key_value"]),
    ("wide_column_reader", "Wide-column query reader", ["cassandra_native_v5"], ["source.operational_database.wide_column"]),
    ("graph_query_reader", "Graph query reader", ["neo4j_bolt", "sparql11_protocol"], ["source.operational_database.property_graph", "source.operational_database.rdf_triplestore"]),
    ("database_cdc_reader", "Database change-log reader", ["postgresql_logical_replication", "mysql_binary_log", "mongodb_wire"], ["source.event_messaging_cdc.transaction_log_cdc"]),
    ("remote_query_reader", "Remote analytical query reader", ["arrow_flight_sql", "odbc43", "jdbc43"], ["source.api_remote_service.remote_query_endpoint"]),
    ("filesystem_scanner", "Filesystem scanner", ["posix_file_io", "nfs41", "smb3"], ["source.file_object_content.local_or_network_filesystem"]),
    ("managed_file_receiver", "Managed file-transfer receiver", ["ftp", "ftps", "sftp", "rsync"], ["source.file_object_content.managed_file_transfer"]),
    ("object_store_reader", "Object-store reader", ["s3_rest"], ["source.file_object_content.object_storage"]),
    ("resumable_object_writer", "Resumable object writer", ["tus10", "s3_multipart"], ["source.file_object_content.object_storage"]),
    ("artifact_registry_reader", "Content-addressed artifact reader", ["oci_distribution"], ["source.code_devops.artifact_package_registry"]),
    ("content_repository_reader", "Versioned content repository reader", ["cmis_browser", "webdav"], ["source.file_object_content.enterprise_content_repository"]),
    ("http_resource_reader", "HTTP resource reader", ["http11", "http2", "http3", "openapi32"], ["source.api_remote_service.http_resource_api"]),
    ("enterprise_saas_resource_reader", "Enterprise SaaS resource reader", ["http11", "openapi32", "graphql2025"], ["source.enterprise_application.enterprise_resource_planning", "source.enterprise_application.customer_relationship_management", "source.enterprise_application.human_resources_payroll"]),
    ("collaboration_saas_reader", "Collaboration SaaS resource reader", ["http11", "openapi32", "graphql2025"], ["source.collaboration_productivity.team_chat", "source.collaboration_productivity.task_work_management", "source.file_object_content.shared_document_workspace"]),
    ("devops_saas_reader", "DevOps SaaS resource reader", ["http11", "openapi32", "graphql2025"], ["source.code_devops.distributed_version_control", "source.code_devops.issue_change_tracker", "source.code_devops.ci_cd_orchestrator"]),
    ("security_saas_reader", "Security SaaS resource reader", ["http11", "openapi32", "scim2"], ["source.security_identity.siem_detection_case", "source.security_identity.vulnerability_exposure_management", "source.security_identity.security_audit_log"]),
    ("analytical_saas_reader", "Analytical SaaS query reader", ["http11", "openapi32", "arrow_flight_sql"], ["source.analytical_repository.cloud_data_warehouse", "source.analytical_repository.semantic_metric_store"]),
    ("graphql_reader", "GraphQL query reader", ["graphql2025", "graphql_over_http"], ["source.api_remote_service.graphql_query_api"]),
    ("rpc_reader", "Binary RPC reader", ["grpc", "grpc_streaming"], ["source.api_remote_service.binary_rpc_service"]),
    ("soap_service_adapter", "SOAP service adapter", ["soap12", "wsdl20"], ["source.api_remote_service.soap_web_service"]),
    ("odata_delta_reader", "OData query and delta reader", ["odata401", "odata_batch"], ["source.api_remote_service.odata_data_service"]),
    ("identity_provisioning_adapter", "Identity provisioning adapter", ["scim2", "scim_bulk"], ["source.security_identity.identity_directory"]),
    ("webhook_receiver", "Webhook receiver", ["webhook_http", "websub"], ["source.event_messaging_cdc.webhook_delivery"]),
    ("event_stream_reader", "Server event-stream reader", ["server_sent_events", "websocket"], ["source.event_messaging_cdc.publish_subscribe_topic"]),
    ("cloud_event_adapter", "Cloud event envelope adapter", ["cloudevents10", "asyncapi30"], ["source.event_messaging_cdc.cloud_event_bus"]),
    ("amqp_consumer", "AMQP message consumer", ["amqp10"], ["source.event_messaging_cdc.work_message_queue"]),
    ("mqtt_consumer", "MQTT telemetry consumer", ["mqtt5"], ["source.event_messaging_cdc.mqtt_broker"]),
    ("partitioned_log_consumer", "Partitioned append-log consumer", ["kafka_wire", "kafka_connect"], ["source.event_messaging_cdc.partitioned_append_log"]),
    ("stomp_consumer", "STOMP message consumer", ["stomp12"], ["source.event_messaging_cdc.work_message_queue"]),
    ("nats_consumer", "NATS subject consumer", ["nats_core", "nats_jetstream"], ["source.event_messaging_cdc.publish_subscribe_topic"]),
    ("messaging_api_adapter", "Messaging API adapter", ["jakarta_messaging31"], ["source.event_messaging_cdc.work_message_queue"]),
    ("coap_device_reader", "Constrained-device reader", ["coap"], ["source.iot_edge.constrained_device_api"]),
    ("dds_subscriber", "Industrial DDS subscriber", ["dds14"], ["source.industrial_ot.scada_dcs"]),
    ("bulk_export_job_reader", "Asynchronous bulk-export reader", ["fhir_bulk20", "odata_batch", "scim_bulk"], ["source.api_remote_service.bulk_export_api"]),
    ("bulk_import_writer", "Asynchronous bulk-import writer", ["odata_batch", "scim_bulk", "s3_multipart"], ["source.api_remote_service.http_resource_api", "source.file_object_content.object_storage"]),
    ("opcua_reader", "OPC UA browse/subscription reader", ["opcua"], ["source.industrial_ot.opcua_information_server"]),
    ("modbus_reader", "Modbus register reader", ["modbus_tcp"], ["source.industrial_ot.plc_controller"]),
    ("building_automation_reader", "Building-automation reader", ["bacnet"], ["source.industrial_ot.building_automation"]),
    ("power_telecontrol_reader", "Power-system telecontrol reader", ["iec61850", "dnp3"], ["source.industrial_ot.energy_grid_control"]),
    ("machine_observation_reader", "Machine observation reader", ["mtconnect", "sparkplug30"], ["source.industrial_ot.robotics_machine_controller"]),
    ("iot_resource_reader", "IoT resource reader", ["onem2m", "matter"], ["source.iot_edge.iot_sensor_gateway"]),
    ("fhir_reader", "FHIR clinical resource reader", ["fhir_r5_rest", "fhir_bulk20"], ["source.regulated_vertical.electronic_health_record"]),
    ("dicom_reader", "DICOM image reader", ["dicomweb", "dicom_dimse"], ["source.regulated_vertical.medical_imaging_pacs"]),
    ("hl7_message_receiver", "HL7 clinical message receiver", ["hl7v2_mllp", "ihe_xds"], ["source.regulated_vertical.electronic_health_record"]),
    ("fix_market_reader", "FIX market/order reader", ["fix_session", "fixp"], ["source.regulated_vertical.market_data_feed", "source.regulated_vertical.trading_order_execution"]),
    ("financial_message_adapter", "Financial message adapter", ["iso20022_messages", "ofx23"], ["source.regulated_vertical.payments_ledger"]),
    ("regulatory_filing_reader", "Regulatory filing reader", ["xbrl_reporting"], ["source.regulated_vertical.regulatory_xbrl_filing"]),
    ("edi_interchange_receiver", "EDI interchange receiver", ["un_edifact", "x12_edi", "as2", "as4", "ebms3"], ["source.event_messaging_cdc.edi_mailbox_gateway"]),
    ("supply_chain_event_reader", "Supply-chain event reader", ["epcis20"], ["source.enterprise_application.supply_chain_planning"]),
    ("geospatial_feature_reader", "Geospatial feature reader", ["ogc_api_features", "wfs20"], ["source.geospatial_media.gis_feature_service"]),
    ("geospatial_catalog_reader", "Spatiotemporal catalog reader", ["stac11"], ["source.geospatial_media.raster_remote_sensing_catalog"]),
    ("sensor_observation_reader", "Sensor observation reader", ["sensorthings11"], ["source.geospatial_media.weather_environmental_observation"]),
    ("chunked_array_reader", "Chunked scientific-array reader", ["zarr3", "netcdf", "hdf5"], ["source.scientific_research.multidimensional_scientific_file"]),
    ("mailbox_reader", "Mailbox reader", ["imap4rev2", "jmap"], ["source.collaboration_productivity.email_mailbox"]),
    ("mail_sender", "Mail submission adapter", ["smtp"], ["source.collaboration_productivity.email_mailbox"]),
    ("calendar_reader", "Calendar reader", ["caldav", "jmap"], ["source.collaboration_productivity.calendar_scheduling"]),
    ("contact_activity_reader", "Contact/activity reader", ["carddav", "activitystreams20"], ["source.collaboration_productivity.team_chat"]),
    ("mainframe_terminal_adapter", "Mainframe terminal adapter", ["tn3270e"], ["source.legacy_offline.transaction_monitor"]),
    ("legacy_batch_reader", "Legacy fixed-record batch reader", ["fixed_record_ftp", "ebcdic_blocked_file"], ["source.legacy_offline.fixed_record_batch_exchange"]),
    ("block_replication_adapter", "Block replication adapter", ["iscsi", "nvme_over_fabrics"], ["source.file_object_content.binary_proprietary_file"]),
    ("telemetry_exporter", "Telemetry exporter", ["otlp", "trace_context"], ["source.telemetry_digital_experience.distributed_traces"]),
    ("browser_telemetry_collector", "Browser telemetry collector", ["beacon", "reporting_api", "navigation_timing2"], ["source.telemetry_digital_experience.web_product_analytics"]),
    ("guarded_resource_writer", "Guarded HTTP resource writer", ["http11", "openapi32"], ["source.api_remote_service.http_resource_api"]),
    ("saas_writeback_adapter", "Guarded SaaS writeback adapter", ["http11", "openapi32", "odata401"], ["source.enterprise_application.customer_relationship_management", "source.collaboration_productivity.task_work_management", "source.enterprise_application.it_service_management"]),
    ("guarded_industrial_commander", "Guarded industrial commander", ["opcua", "modbus_tcp", "matter"], ["source.industrial_ot.plc_controller"]),
]


def connector_classes(protocol_ids: set[str], evidence_by_protocol: dict[str, list[str]]) -> list[dict]:
    records = []
    common_caps = ["capability.cp.classify_connector_role", "capability.cp.discover_capabilities", "capability.cp.bind_source_occurrence"]
    common_ops = ["operation.cp.classify_connector", "operation.cp.fetch_capability_document", "operation.cp.bind_occurrence"]
    for key, name, protocol_keys, sources in CONNECTOR_CLASS_ROWS:
        protocol_refs = [f"protocol.cp.{item}" for item in protocol_keys]
        assert set(protocol_refs) <= protocol_ids
        evidence_refs = sorted({ref for protocol in protocol_refs for ref in evidence_by_protocol[protocol]})
        records.append({
            "connector_class_id": f"connector.class.cp.{key}", "edition": EDITION, "status": "candidate", "name": name,
            "definition": f"Provider-neutral connector class for {name.lower()}, selected by required behavior and evidence rather than vendor or package name.",
            "source_class_refs": sources, "protocol_refs": protocol_refs,
            "required_capability_refs": common_caps, "operation_refs": common_ops,
            "semantic_boundaries": {"source_class": "owns source meaning and authority", "connector_class": "owns required access behavior", "implementation": "owns executable code and dependency identity", "occurrence": "owns deployment configuration and observations"},
            "selection_requirements": ["every required operation has a compatible protocol profile", "artifact and occurrence receipts satisfy requested assurance and are unexpired"],
            "assurance_claims_forbidden": ["protocol support implies source semantics", "connector-local exactly-once implies end-to-end effect", "documented capability implies probed behavior"],
            "evidence_refs": evidence_refs,
        })
    return records


def lifecycles() -> list[dict]:
    subjects = [
        ("connector_class", ["proposed", "reviewed", "candidate", "deprecated", "retired"]),
        ("implementation_artifact", ["declared", "built", "scanned", "qualified", "deprecated", "revoked"]),
        ("deployed_occurrence", ["registered", "configured", "probed", "eligible", "invalidated", "retired"]),
        ("protocol_profile", ["declared", "negotiated", "active", "deprecated", "unsupported"]),
        ("credential_reference", ["registered", "active", "rotating", "revoked", "expired"]),
        ("session", ["disconnected", "connecting", "authenticated", "active", "draining", "closed", "failed"]),
        ("snapshot", ["planned", "cut_selected", "reading", "read_complete", "reconciled", "published", "failed"]),
        ("bulk_job", ["prepared", "submitted", "accepted", "running", "export_complete", "collected", "expired", "failed"]),
        ("read_cursor", ["issued", "active", "exhausted", "expired", "invalidated"]),
        ("cdc_checkpoint", ["captured", "persisted", "active", "expired", "superseded", "gap_detected"]),
        ("subscription", ["requested", "verified", "active", "renewing", "expired", "revoked"]),
        ("message_delivery", ["available", "acquired", "accepted", "released", "rejected", "dead_lettered"]),
        ("remote_command", ["prepared", "submitted", "transport_accepted", "source_accepted", "committed", "rejected", "outcome_unknown"]),
        ("retry_budget", ["available", "consuming", "exhausted", "reset", "cancelled"]),
        ("qualification_receipt", ["planned", "executed", "issued", "valid", "invalidated", "expired"]),
        ("deprecation", ["announced", "migration_available", "overlap", "removal_eligible", "removed"]),
    ]
    records = []
    for subject, states in subjects:
        transitions = []
        for before, after in zip(states, states[1:]):
            transitions.append({"from": before, "command": f"advance_{slug(subject)}", "to": after, "guard": "required evidence and authority are present"})
        records.append({
            "lifecycle_id": f"lifecycle.cp.{subject}", "edition": EDITION, "status": "candidate", "subject_kind": subject,
            "states": states, "transitions": transitions, "terminal_states": [states[-1]],
            "invalidation_triggers": ["version change", "configuration change", "credential or authorization change", "source topology or retention change"],
            "receipts": [f"{subject}_transition_receipt", f"{subject}_invalidation_receipt"],
        })
    records.append({
        "lifecycle_id": "lifecycle.cp.connector_runtime", "edition": EDITION, "status": "candidate",
        "subject_kind": "connector_runtime",
        "states": ["draft", "configured", "validated", "qualified", "active", "pausing", "paused", "draining", "stopped", "upgrading", "failed", "retired"],
        "transitions": [
            {"from": "draft", "command": "configure", "to": "configured", "guard": "a new immutable configuration edition is supplied"},
            {"from": "configured", "command": "validate", "to": "validated", "guard": "configuration and referenced secret shapes pass deterministic validation"},
            {"from": "validated", "command": "qualify", "to": "qualified", "guard": "scoped artifact and occurrence qualification receipts are current"},
            {"from": "qualified", "command": "activate", "to": "active", "guard": "deployment authority and resource budgets are bound"},
            {"from": "active", "command": "request_pause", "to": "pausing", "guard": "the in-flight work disposition is explicit"},
            {"from": "pausing", "command": "observe_paused", "to": "paused", "guard": "connector and task observations satisfy the pause predicate"},
            {"from": "paused", "command": "resume", "to": "active", "guard": "qualification, authority and configuration edition remain valid"},
            {"from": "active", "command": "request_stop", "to": "draining", "guard": "checkpoint, task and external-resource disposition is explicit"},
            {"from": "draining", "command": "observe_stopped", "to": "stopped", "guard": "all required stop receipts or typed unknowns are recorded"},
            {"from": "stopped", "command": "resume", "to": "active", "guard": "recovery inputs and qualification are valid"},
            {"from": "stopped", "command": "begin_upgrade", "to": "upgrading", "guard": "old and new artifact/configuration editions and rollback law are bound"},
            {"from": "upgrading", "command": "complete_upgrade", "to": "active", "guard": "new occurrence observations and compatibility receipts pass"},
            {"from": "active", "command": "observe_failure", "to": "failed", "guard": "failure observation is scoped to connector and task occurrences"},
            {"from": "failed", "command": "restart", "to": "active", "guard": "failure class permits restart and retry budget remains"},
            {"from": "stopped", "command": "retire", "to": "retired", "guard": "configuration, offset, schema-history, credential, artifact and external-state dispositions are recorded"},
            {"from": "failed", "command": "retire", "to": "retired", "guard": "unknown completion and retained state are explicitly disposed"},
        ],
        "terminal_states": ["retired"],
        "invalidation_triggers": ["artifact edition", "configuration edition", "protocol profile", "credential or authorization", "source topology", "offset or schema-history loss", "qualification expiry"],
        "receipts": ["connector_transition_plan", "connector_observation_receipt", "task_observation_set", "retirement_disposition_receipt"],
    })
    return records


def implementation_records(connector_class_ids: list[str], protocol_ids: list[str], capability_ids: list[str]) -> list[dict]:
    rows = [
        ("reference_http_reader", "Reference HTTP reader fixture", "reference_fixture", ["http_resource_reader"], ["http11", "http2"]),
        ("reference_cdc_reader", "Reference CDC reader fixture", "reference_fixture", ["database_cdc_reader"], ["postgresql_logical_replication"]),
        ("reference_file_reader", "Reference legacy file reader fixture", "reference_fixture", ["legacy_batch_reader"], ["fixed_record_ftp", "ebcdic_blocked_file"]),
        ("reference_webhook_receiver", "Reference webhook receiver fixture", "reference_fixture", ["webhook_receiver"], ["webhook_http"]),
        ("reference_message_consumer", "Reference message consumer fixture", "reference_fixture", ["amqp_consumer"], ["amqp10"]),
        ("reference_bulk_reader", "Reference bulk-export fixture", "reference_fixture", ["bulk_export_job_reader"], ["fhir_bulk20"]),
        ("reference_ot_reader", "Reference read-only OT fixture", "reference_fixture", ["opcua_reader"], ["opcua"]),
        ("reference_browser_collector", "Reference browser telemetry fixture", "reference_fixture", ["browser_telemetry_collector"], ["beacon"]),
    ]
    records = []
    for key, name, kind, class_keys, protocol_keys in rows:
        records.append({
            "artifact_id": f"artifact.cp.{key}", "edition": EDITION, "status": "test_fixture", "name": name, "artifact_kind": kind,
            "build_identity": {"coordinate": f"unpublished:test-fixture:{key}", "version": "0.0.0-candidate", "digest": None, "reproducible": False},
            "connector_class_refs": [f"connector.class.cp.{item}" for item in class_keys],
            "protocol_profiles": [f"protocol.cp.{item}" for item in protocol_keys],
            "declared_capability_refs": capability_ids[:4], "qualified_capability_refs": [],
            "dependency_lock": {"present": False, "reason": "No executable artifact is published by this research candidate."},
            "license_supply_chain": {"license": "UNLICENSED research fixture metadata", "redistribution": "not_applicable", "sbom_ref": None, "provenance_ref": None},
            "security_posture": {"credentials": "references_only", "network": "not_deployed", "write_default": "disabled"},
            "version_lifecycle": {"support": "none", "deprecation": "fixture may change", "invalidation": ["any implementation materialization"]},
            "conformance_receipt_refs": [], "binding_eligible": False,
        })
    return records


def conformance_tests(evidence_ids: set[str]) -> list[dict]:
    rows = [
        ("identity_layers", "Identity layers remain distinct", "identity", ["register similarly named class, artifact and occurrence"], ["IDs and authority remain distinct"], ["source class is not connector class"]),
        ("advertised_vs_probed", "Advertised capability does not become observed behavior", "discovery", ["advertise an unimplemented operation"], ["probe result is fail or inconclusive"], ["documented capability", "probed behavior"]),
        ("read_cursor_vs_cdc", "Read cursor cannot resume CDC", "cursor", ["supply a page token to change resume"], ["typed token-purpose refusal"], ["read cursor", "CDC resume token"]),
        ("snapshot_cut_vs_completion", "Snapshot cut differs from completion", "snapshot", ["advance source after cut while export runs"], ["cut identity remains fixed; completion is separate"], ["snapshot consistency", "export completion"]),
        ("transport_vs_acceptance", "Transport success differs from source acceptance", "write", ["return HTTP 202 then reject job"], ["transport and terminal source receipts disagree visibly"], ["transport success", "source acceptance"]),
        ("connector_vs_end_to_end_exactly_once", "Connector exactly-once does not prove end-to-end effect", "delivery", ["commit source offset before sink effect"], ["end-to-end claim refused"], ["connector guarantee", "end-to-end effect"]),
        ("pagination_under_mutation", "Pagination under mutation", "pagination", ["insert and delete between pages"], ["omission/duplication classified by cursor law"], ["offset pagination", "snapshot pagination"]),
        ("cursor_expiry", "Continuation expiry", "cursor", ["resume beyond documented TTL"], ["terminal expired-token outcome"], ["empty result", "expired cursor"]),
        ("cdc_retention_gap", "CDC retention gap", "cdc", ["resume before retained boundary"], ["gap detected and rebootstrap required"], ["no changes", "unavailable changes"]),
        ("snapshot_cdc_handoff", "Snapshot-to-change handoff", "cdc", ["commit around handoff boundary"], ["every commit reconciles exactly once by identity"], ["overlap", "loss"]),
        ("transaction_atomicity", "Transaction atomicity", "transaction", ["disconnect during multi-record transaction"], ["partial visibility matches declared boundary"], ["protocol transaction", "source transaction"]),
        ("write_idempotency", "Write retry idempotency", "write", ["lose response after source commit then retry"], ["one effect or explicit duplicate outcome"], ["idempotent request", "idempotent effect"]),
        ("cancel_disposition", "Cancellation disposition", "cancellation", ["cancel after remote admission"], ["stopped/continued/unknown outcome recorded"], ["local cancellation", "remote cancellation"]),
        ("rate_scope", "Rate-limit scope", "limits", ["use two identities and endpoints"], ["scope and reset behavior observed"], ["per-client", "per-tenant"]),
        ("quota_exhaustion", "Quota exhaustion", "limits", ["consume a safe fixture quota"], ["typed terminal or resettable outcome"], ["rate limit", "quota"]),
        ("retry_after", "Retry-after semantics", "retry", ["inject 429/503 with and without retry metadata"], ["delay respects applicable law and budget"], ["retryable", "safe to retry"]),
        ("authn_vs_authz", "Authentication is not authorization", "security", ["authenticate without object privilege"], ["not-authorized, never empty data"], ["authenticated", "authorized"]),
        ("secret_rotation", "Secret rotation", "security", ["rotate referenced credential"], ["sessions renew without logging secret material"], ["secret reference", "secret value"]),
        ("tenant_boundary", "Tenant boundary", "security", ["request a sibling tenant object"], ["denial receipt without leaked metadata"], ["namespace absence", "authorization denial"]),
        ("tls_peer", "TLS peer identity", "security", ["present mismatched peer identity"], ["channel establishment fails closed"], ["encryption", "authenticated peer"]),
        ("schema_add", "Additive schema drift", "schema", ["add optional and required fields"], ["compatibility classified per profile"], ["parse success", "semantic compatibility"]),
        ("schema_type_change", "Type-change drift", "schema", ["widen, narrow and reinterpret a field"], ["loss and semantic changes reported"], ["carrier conversion", "semantic preservation"]),
        ("timezone_dst", "Timezone and DST", "time", ["cross DST overlap and gap"], ["source zone/offset/fold semantics preserved"], ["wall time", "instant"]),
        ("ordering_gap", "Ordering gap", "order", ["omit, duplicate and reorder sequences"], ["scope-specific gap receipt"], ["arrival order", "source order"]),
        ("finality_correction", "Finality and correction", "finality", ["emit provisional, corrected and retracted records"], ["each state remains distinguishable"], ["latest value", "final fact"]),
        ("webhook_redelivery", "Webhook redelivery", "webhook", ["drop acknowledgement after acceptance"], ["duplicate delivery observed and safely handled"], ["delivery", "unique event"]),
        ("message_settlement", "Message settlement", "messaging", ["release, reject and accept deliveries"], ["broker and application state remain distinct"], ["acknowledged transport", "business processed"]),
        ("partition_rebalance", "Partition rebalance fencing", "messaging", ["revoke during in-flight work"], ["old owner cannot commit after new epoch"], ["assignment", "exclusive authority"]),
        ("bulk_accept_complete", "Bulk job acceptance and completion", "bulk", ["accept then fail asynchronous job"], ["completion never inferred from submission"], ["accepted job", "completed export"]),
        ("partial_transfer", "Partial file/object transfer", "transfer", ["interrupt transfer before final byte"], ["partial object is hidden or explicitly partial"], ["bytes sent", "published object"]),
        ("legacy_blocking", "Legacy blocked-record parsing", "legacy", ["mix fixed/variable blocking and truncated record"], ["record boundary error not silent row shift"], ["block length", "record length"]),
        ("legacy_codepage", "Legacy code-page translation", "legacy", ["decode ambiguous EBCDIC bytes"], ["selected code page and losses receipted"], ["byte decode", "text meaning"]),
        ("ot_readonly", "OT command read-only default", "industrial", ["request write without control authority"], ["not-authorized before network effect"], ["read capability", "command capability"]),
        ("ot_interlock", "OT interlock", "industrial", ["request authorized command with unsafe interlock"], ["command refused with safety receipt"], ["authorized", "safe"]),
        ("fhir_profile", "FHIR profile conformance", "healthcare", ["supply base-valid resource violating profile"], ["profile violation reported"], ["base syntax", "profile conformance"]),
        ("edi_receipt", "EDI transport and business receipts", "edi", ["receive signed transport receipt and negative business acknowledgement"], ["receipts remain separate"], ["message disposition", "business acceptance"]),
        ("geo_axis_order", "Geospatial axis order", "geospatial", ["swap latitude/longitude under conflicting CRS conventions"], ["CRS and axis order explicit"], ["numeric pair", "geometry"]),
        ("scientific_fill", "Scientific fill and missing values", "scientific", ["read fill value, NaN and absent chunk"], ["missingness kinds remain distinct"], ["fill value", "measurement"]),
        ("browser_beacon", "Browser beacon enqueue", "browser", ["enqueue during unload then lose network"], ["enqueue receipt does not claim collector acceptance"], ["queued", "delivered"]),
        ("license_invalidation", "License and dependency invalidation", "supply_chain", ["change license or vulnerable dependency"], ["artifact qualification invalidated"], ["same API", "same deployability"]),
        ("version_downgrade", "Protocol downgrade", "versioning", ["negotiate older version missing required feature"], ["binding refused or typed degradation"], ["wire compatible", "capability compatible"]),
        ("telemetry_partial_success", "Telemetry partial success", "observability", ["collector rejects part of batch"], ["accepted and rejected counts receipted"], ["transport success", "all telemetry accepted"]),
    ]
    default_evidence = "evidence.cp.rfc9110"
    records = []
    for key, name, scope, stimulus, oracle, distinguishes in rows:
        evidence = "evidence.cp.opcua" if scope == "industrial" else default_evidence
        if scope == "healthcare": evidence = "evidence.cp.fhir_r5"
        if scope == "edi": evidence = "evidence.cp.as2"
        if scope == "browser": evidence = "evidence.cp.beacon"
        if scope == "messaging": evidence = "evidence.cp.amqp10"
        if evidence not in evidence_ids: evidence = sorted(evidence_ids)[0]
        records.append({
            "test_id": f"test.cp.{key}", "edition": EDITION, "status": "candidate", "name": name, "scope": scope,
            "preconditions": ["synthetic fixture or explicitly authorized sandbox", "no production credentials", "bounded non-destructive envelope"],
            "stimulus": stimulus, "oracle": oracle,
            "expected_receipts": ["artifact version and configuration fingerprint", "documented assertion snapshot", "observation outcome and timestamp"],
            "allowed_outcomes": ["pass", "fail", "not_supported", "not_authorized", "inconclusive"],
            "distinguishes": distinguishes, "destructive": scope in {"write", "industrial"}, "evidence_refs": [evidence],
        })
    return records


def compiler_records(capabilities: list[dict], operations: list[dict]) -> list[dict]:
    records = []
    for index, context in enumerate(CONTEXT_ROWS[:24]):
        key = context[0]
        caps = [capabilities[index * 2]["capability_id"], capabilities[index * 2 + 1]["capability_id"]]
        ops = [operations[index * 2]["operation_id"], operations[index * 2 + 1]["operation_id"]]
        requirement_id = f"compiler.cp.requirement.{key}"
        offer_id = f"compiler.cp.offer_template.{key}"
        mapping_id = f"compiler.cp.mapping.{key}"
        common = {
            "edition": EDITION, "status": "candidate", "capability_refs": caps, "operation_refs": ops,
            "guarantees": ["selected offer is no stronger than qualified artifact and occurrence evidence"],
            "prohibited_traits": ["vendor-name dispatch", "undocumented capability inference", "expired or configuration-mismatched receipt"],
            "evidence_gates": ["protocol profile evidence", "artifact qualification receipt", "occurrence observation or explicit unknown"],
            "binding_phase": "physical_binding", "fallback_law": "refuse",
        }
        records.append({"compiler_record_id": requirement_id, "record_kind": "requirement", "subject_ref": f"context.cp.{key}", **common})
        records.append({"compiler_record_id": offer_id, "record_kind": "offer_template", "subject_ref": f"context.cp.{key}", **common})
        records.append({"compiler_record_id": mapping_id, "record_kind": "mapping", "subject_ref": requirement_id, **common})
    return records


def library_records() -> list[dict]:
    return [
        {
            "library_id": "library.cp.contract_core", "edition": EDITION, "status": "candidate",
            "name": "Pure connector contract core", "owner_context_ref": "context.cp.source_connector_identity",
            "library_kind": "semantic_pure", "effect_boundary": "pure_effect_intents",
            "owns": ["identity distinctions", "requirements", "offers", "typed gaps", "effect intents"],
            "must_not_own": ["network I/O", "protocol bytes", "provider mappings", "credentials"],
            "public_contracts": ["ConnectorClass", "ProtocolProfile", "CapabilityRequirement", "EffectIntent", "ReceiptClaim"],
            "dependencies": [], "receipts": ["deterministic decision trace"],
            "removal_seams": ["effect intents are interpreted outside the pure core"], "evidence_refs": ["evidence.cp.rfc9110"],
        },
        {
            "library_id": "library.cp.connection_contract", "edition": EDITION, "status": "candidate",
            "name": "Connection contract kernel", "owner_context_ref": "context.cp.connection_contract",
            "library_kind": "semantic_pure", "effect_boundary": "pure_effect_intents",
            "owns": ["provider-neutral connection declarations", "occurrence bindings", "binding editions", "revocation plans", "connection effect intents"],
            "must_not_own": ["network I/O", "DNS or route execution", "secret values", "session pooling runtime", "provider selection", "source semantics"],
            "public_contracts": ["ConnectionDeclaration", "CredentialReference", "SourceOccurrence", "ConnectionBinding", "ConnectionBindingEdition", "ConnectionEffectIntent", "ConnectionContractOutcome"],
            "public_traits": ["ConnectionDeclarationValidator", "ConnectionOccurrenceBinder", "ConnectionRevocationPlanner"],
            "operation_refs": ["operation.cp.validate_connection_declaration", "operation.cp.bind_connection_occurrence", "operation.cp.plan_connection_revocation"],
            "decision_refs": ["decision.cp.connection_contract", "decision.cp.endpoint_addressing", "decision.cp.protocol_profile", "decision.cp.authentication", "decision.cp.authorization_scope", "decision.cp.secret_reference", "decision.cp.network_security"],
            "input_types": ["ConnectionContractCommand"], "output_types": ["ConnectionContractOutcome"],
            "configuration_contracts": ["ConnectionContractPolicy"],
            "error_contracts": ["SourceOccurrenceUnknown", "AuthorityMissing", "ProtocolProfileUnsupported", "CredentialReferenceInvalid", "StaleBindingEdition", "ConnectionContractRefusal"],
            "laws": [
                "endpoint identity, route, transport connection, authenticated session and pool lease are distinct",
                "connection binding success is not session readiness, source reachability, authorization, or source acceptance",
                "protocol, transport, channel-security, authentication and authorization profiles are separately editioned",
                "credential material is never carried by the declaration; only a scoped opaque reference may cross the boundary",
                "pool reuse cannot cross source occurrence, tenant, principal, authorization scope, transaction affinity, session affinity, or contract edition",
                "connect, handshake, authentication, request, idle and total budgets are distinct and have no hidden semantic defaults",
                "equal canonical declarations and decisions produce an equal binding digest",
                "unknown material compatibility or authority fails closed",
                "the pure kernel emits an effect intent and performs no network, filesystem, process, environment, clock, randomness or secret-store access",
            ],
            "oracles": ["canonical declaration digest is stable under field-order permutations", "secret values are rejected at the DTO boundary", "cross-occurrence pool reuse is refused", "revoked or stale bindings cannot produce an executable intent"],
            "resource_contracts": ["validation is linear in declared fields and bounded by explicit field and extension limits", "canonicalization refuses unbounded recursive extension graphs"],
            "concurrency": ["binding editions use optimistic comparison; a stale edition cannot overwrite a newer binding", "connection intent identity is independent of execution attempt identity"],
            "cancellation": ["pure validation and planning are bounded; cancellation is not remote connection cancellation"],
            "dependencies": [], "receipts": ["canonical connection-contract decision trace", "binding or revocation intent digest"],
            "removal_seams": ["transport, authentication, secret resolution and provider adapters consume typed intents through replaceable ports"],
            "evidence_refs": ["evidence.cp.kafka_connect_api42", "evidence.cp.rfc9110", "evidence.cp.rfc8446"],
        },
        {
            "library_id": "library.cp.connector_lifecycle", "edition": EDITION, "status": "candidate",
            "name": "Connector lifecycle state machine", "owner_context_ref": "context.cp.connector_lifecycle",
            "library_kind": "policy_pure", "effect_boundary": "pure_effect_intents",
            "owns": ["desired and observed connector states", "total legal transition relation", "configuration editions", "connector/task divergence", "restart and upgrade plans", "retirement disposition requirements"],
            "must_not_own": ["connector or task process execution", "offset or schema-history storage", "network I/O", "qualification authority", "business approval", "external-state deletion"],
            "public_contracts": ["ConnectorDesiredState", "ConnectorObservedState", "TaskObservedState", "ConnectorConfigurationEdition", "ConnectorTransition", "ConnectorTransitionIntent", "ConnectorLifecycleOutcome"],
            "public_traits": ["ConnectorTransitionPlanner", "ConnectorHealthClassifier", "ConnectorRevocationPlanner"],
            "operation_refs": ["operation.cp.plan_connector_transition", "operation.cp.classify_connector_health", "operation.cp.plan_connector_revocation"],
            "decision_refs": ["decision.cp.connector_lifecycle", "decision.cp.deployment_binding", "decision.cp.implementation_qualification", "decision.cp.deprecation_exit", "decision.cp.retry", "decision.cp.cancellation", "decision.cp.recovery_replay"],
            "input_types": ["ConnectorLifecycleCommand"], "output_types": ["ConnectorLifecycleOutcome"],
            "configuration_contracts": ["ConnectorLifecyclePolicy", "RestartBudget", "UpgradeCoexistencePolicy", "RetirementDispositionPolicy"],
            "error_contracts": ["IllegalTransition", "IncompatibleEdition", "QualificationMissing", "RevocationPending", "TaskStateDiverged", "UnknownCompletion", "RetirementDispositionIncomplete"],
            "laws": [
                "connector definition, implementation artifact, deployed occurrence, configuration edition, task assignment, run and attempt are distinct identities",
                "desired state is not observed connector state and observed connector state is not the set of observed task states",
                "configuration validation is not source reachability, implementation qualification, deployment eligibility or active execution",
                "pause, drain, stop, failure, deletion and retirement are non-interchangeable dispositions",
                "an accepted asynchronous transition request is not evidence that connector and tasks reached the requested state",
                "every reconfiguration creates or selects an immutable configuration edition and declares the disposition of in-flight work",
                "upgrade pins old and new artifact, configuration, protocol, offset and schema-history editions plus rollback compatibility",
                "unknown transition completion blocks blind retry until reconciled",
                "retirement records configuration, offsets, schema history, credentials, artifact and external-state disposition; deleting a control record proves none of those effects",
                "the transition function is total over state, command and policy and returns either a typed plan or a typed refusal",
                "the pure policy emits intents only; runtime controllers execute them and return scoped observations",
            ],
            "oracles": ["all state-command pairs produce a transition plan or named refusal", "pause and stop yield different resource dispositions", "stale configuration editions are fenced", "connector/task state divergence remains visible", "unknown completion forbids restart until reconciliation"],
            "resource_contracts": ["transition planning is bounded by the connector plus an explicitly bounded task observation set", "restart, retry and upgrade coexistence consume finite declared budgets"],
            "concurrency": ["configuration and desired-state editions are compared atomically", "task observations carry assignment epochs and cannot be merged across epochs without reconciliation"],
            "cancellation": ["cancelling transition planning has no remote effect; cancelling an issued intent yields an explicit in-flight disposition"],
            "dependencies": ["library.cp.connection_contract"],
            "receipts": ["deterministic transition decision trace", "connector/task observation classification", "retirement disposition requirement set"],
            "removal_seams": ["runtime controller, provider adapter, state store and qualification authority remain replaceable ports"],
            "evidence_refs": ["evidence.cp.kafka_connect_api42", "evidence.cp.kafka_connect_user42"],
        },
        {
            "library_id": "library.cp.protocol_codec", "edition": EDITION, "status": "candidate",
            "name": "Pure protocol codec", "owner_context_ref": "context.cp.serialization_framing",
            "library_kind": "protocol_codec", "effect_boundary": "pure_no_io",
            "owns": ["framing", "encoding", "decoding", "versioned grammar", "parse errors"],
            "must_not_own": ["sockets", "retries", "authentication policy", "source semantics"],
            "public_contracts": ["Frame", "DecodeResult", "EncodeResult", "ProtocolEdition"],
            "dependencies": [], "allowed_dependency_kinds": ["qualified representation codec"],
            "receipts": ["codec conformance vector result"],
            "removal_seams": ["byte transport is an injected runtime port"], "evidence_refs": ["evidence.cp.rfc8259"],
        },
        {
            "library_id": "library.cp.transport_runtime", "edition": EDITION, "status": "candidate",
            "name": "Protocol transport runtime", "owner_context_ref": "context.cp.session_connection",
            "library_kind": "runtime_mechanism", "effect_boundary": "effectful_runtime",
            "owns": ["connections", "timeouts", "flow control", "cancellation", "retry scheduling"],
            "must_not_own": ["business authority", "source classification", "provider object mapping", "end-to-end exactly-once claims"],
            "public_contracts": ["TransportRequest", "TransportOutcome", "CancellationDisposition", "RetryBudget"],
            "dependencies": ["library.cp.protocol_codec"],
            "capability_dependencies": ["capability.transport.tls", "capability.telemetry.port"],
            "receipts": ["transport attempt receipt", "remote cancellation disposition"],
            "removal_seams": ["transport trait permits replacement per protocol profile"], "evidence_refs": ["evidence.cp.rfc9113"],
        },
        {
            "library_id": "library.cp.provider_adapter", "edition": EDITION, "status": "candidate",
            "name": "Provider/source adapter", "owner_context_ref": "context.cp.deployment_binding",
            "library_kind": "provider_adapter", "effect_boundary": "effectful_runtime",
            "owns": ["remote object mapping", "provider-specific pagination", "documented limits", "source acceptance interpretation"],
            "must_not_own": ["semantic source authority", "pipeline scheduling", "secrets storage", "global retry policy"],
            "public_contracts": ["SourceOccurrenceBinding", "ProviderRequestMapping", "ObservedCapability", "SourceReceipt"],
            "dependencies": ["library.cp.contract_core", "library.cp.transport_runtime", "library.cp.protocol_codec"],
            "receipts": ["documented assertion", "probed behavior", "source acceptance receipt"],
            "removal_seams": ["adapter selected through connector-class offer instead of vendor switch"], "evidence_refs": ["evidence.cp.openapi32"],
        },
        {
            "library_id": "library.cp.conformance_oracle", "edition": EDITION, "status": "candidate",
            "name": "Connector conformance oracle", "owner_context_ref": "context.cp.implementation_qualification",
            "library_kind": "test_oracle", "effect_boundary": "pure_effect_intents",
            "owns": ["hostile scenarios", "negative twins", "receipt evaluation", "qualification invalidation"],
            "must_not_own": ["production probing", "credentials", "provider marketing assertions", "test subject implementation"],
            "public_contracts": ["ConformanceCase", "AllowedOutcome", "QualificationReceipt", "InvalidationTrigger"],
            "dependencies": ["library.cp.contract_core"], "receipts": ["conformance result", "qualification receipt"],
            "removal_seams": ["fixtures and runners are separate from semantic oracle"], "evidence_refs": ["evidence.cp.slsa1"],
        },
    ]


def innovation_records() -> list[dict]:
    rows = [
        ("http3", "HTTP/3", 2022, "HTTP semantics over QUIC with independent streams", "Changes pooling, head-of-line behavior, cancellation and network diagnostics", ["http3"], "rfc9114"),
        ("problem_details", "HTTP Problem Details revision", 2023, "RFC 9457 revised machine-readable HTTP errors", "Improves typed retry/refusal classification without treating every error body as equivalent", ["http11"], "rfc9457"),
        ("oauth_dpop", "OAuth DPoP", 2023, "Sender-constrains access and refresh tokens", "Reduces replay risk but adds proof keys, nonces and clock-sensitive failure modes", ["http11"], "rfc9449"),
        ("openapi31", "OpenAPI 3.1 JSON Schema alignment", 2021, "Aligned schema dialect behavior with JSON Schema 2020-12", "Makes schema tooling more expressive while requiring dialect-aware validators", ["openapi32"], "openapi31"),
        ("openapi32", "OpenAPI 3.2", 2025, "Added current interface-description features and clarified protocol metadata", "Requires edition-aware discovery and generated-client qualification", ["openapi32"], "openapi32"),
        ("graphql2025", "GraphQL September 2025 edition", 2025, "Published a new GraphQL specification edition", "Requires clients to pin schema and execution semantics rather than claiming generic GraphQL support", ["graphql2025"], "graphql2025"),
        ("asyncapi3", "AsyncAPI 3.0", 2024, "Separated channels, operations and messages more explicitly", "Improves event-interface compilation but does not prove broker runtime behavior", ["asyncapi30"], "asyncapi3"),
        ("flight_sql", "Arrow Flight SQL standardization", 2022, "Combined Arrow columnar transfer with SQL metadata and commands", "Enables high-throughput query exchange with explicit tickets, endpoints and streaming", ["arrow_flight_sql"], "flight_sql"),
        ("fhir_bulk2", "FHIR Bulk Data Access STU2", 2021, "Advanced asynchronous bulk export with manifest and polling contracts", "Separates job acceptance, export completion and expiring artifact collection", ["fhir_bulk20"], "fhir_bulk"),
        ("fhir_r5", "FHIR R5", 2023, "Published the fifth major FHIR specification release", "Creates explicit version/profile compatibility obligations for healthcare adapters", ["fhir_r5_rest"], "fhir_r5"),
        ("stac11", "STAC 1.1", 2024, "Advanced spatiotemporal catalog item and asset conventions", "Improves catalog interoperability while leaving asset retrieval and consistency separate", ["stac11"], "stac"),
        ("zarr3", "Zarr 3.0", 2024, "Introduced the version-3 chunked-array storage specification", "Changes metadata, codecs and store interaction profiles for scientific adapters", ["zarr3"], "zarr3"),
        ("sparkplug3", "Sparkplug 3.0", 2022, "Updated the industrial MQTT state-management profile", "Adds profile-specific birth/death and metric-state semantics beyond generic MQTT delivery", ["sparkplug30"], "sparkplug3"),
        ("matter10", "Matter 1.0", 2022, "Standardized an IP-based connected-device interaction model", "Introduces commissioning, fabrics and interaction semantics requiring safety-aware adapters", ["matter"], "matter"),
        ("epcis20", "EPCIS 2.0", 2022, "Added JSON/JSON-LD bindings and REST query/subscription surfaces", "Expands supply-chain event integration beyond legacy XML while preserving business-step semantics", ["epcis20"], "epcis"),
        ("spdx3", "SPDX 3.0", 2024, "Published a modular software supply-chain information model", "Allows connector artifacts and dependencies to carry stronger license/provenance evidence", ["oci_distribution"], "spdx3"),
        ("cyclonedx16", "CycloneDX 1.6", 2024, "Expanded BOM and attestation representation", "Improves dependency and service inventory used to invalidate connector qualification", ["oci_distribution"], "cyclonedx16"),
        ("slsa10", "SLSA 1.0", 2023, "Stabilized build provenance requirements", "Provides a scoped basis for artifact provenance gates without proving runtime correctness", ["oci_distribution"], "slsa1"),
        ("otel_logs", "OpenTelemetry logs stabilization", 2023, "Matured a common logs data model beside metrics and traces", "Improves connector observability correlation while telemetry remains evidence, not truth", ["otlp"], "opentelemetry"),
        ("otlp_partial", "OTLP partial-success semantics", 2022, "Standardized reporting of partially rejected telemetry batches", "Prevents transport success from being misread as total collector acceptance", ["otlp"], "otlp"),
        ("kafka_kraft", "Kafka KRaft metadata mode", 2022, "Moved cluster metadata management into Kafka's quorum architecture", "Changes discovery, failover and operational compatibility assumptions for consumers", ["kafka_wire"], "kafka_kraft"),
        ("kafka_rebalance", "Kafka next-generation consumer rebalance protocol", 2024, "Introduced a broker-driven consumer group rebalance design", "Changes assignment epochs, recovery and compatibility testing for partition consumers", ["kafka_wire"], "kafka_kip848"),
        ("debezium_incremental", "Debezium incremental snapshots", 2021, "Added chunked snapshotting coordinated through signaling and change streams", "Enables online backfills but requires watermark, overlap and deduplication proofs", ["postgresql_logical_replication"], "debezium_signaling"),
        ("postgres_streaming", "PostgreSQL logical replication streaming in-progress transactions", 2021, "Allowed large in-progress transactions to stream before commit under negotiated capability", "Changes buffering, transaction finality and restart behavior for CDC clients", ["postgresql_logical_replication"], "postgres_logical_protocol"),
        ("graphql_incremental", "GraphQL incremental delivery directives", 2025, "Standardized incremental response concepts in the current GraphQL edition", "Requires clients to distinguish partial transport completion from full operation completion", ["graphql2025"], "graphql2025"),
        ("http_datagrams", "HTTP Datagrams and Capsule Protocol", 2022, "Standardized unreliable datagrams and capsule extensions alongside HTTP semantics", "Creates explicit reliability and ordering distinctions for tunnel, telemetry and event transports", ["http3"], "rfc9297"),
    ]
    return [{
        "innovation_id": f"innovation.cp.{key}", "edition": EDITION, "status": "candidate", "name": name, "year": year,
        "change": change, "why_material": why, "non_llm": True,
        "protocol_refs": [f"protocol.cp.{protocol}"], "evidence_refs": [f"evidence.cp.{evidence}"],
        "limitations": ["Year records the relevant release/publication milestone; verify mutable project documentation before production binding.", "Innovation evidence does not qualify any implementation or deployed occurrence."],
    } for key, name, year, change, why, protocols, evidence in rows for protocol in protocols]


def crosswalk_records() -> list[dict]:
    rows = [
        ("source_classes", ["connector.class.cp.relational_query_reader", "connector.class.cp.database_cdc_reader"], "source_systems", "research/domain_atlas/universes/source_systems/source-classes.jsonl", ["source.operational_database.relational_transactional", "source.event_messaging_cdc.transaction_log_cdc"], "materialized_validated", "connector classes offer access to source classes"),
        ("pipeline_ingestion", ["context.cp.snapshot_change_handoff", "context.cp.recovery_replay"], "pipeline_dataflow", "research/domain_atlas/universes/pipeline_dataflow/context-candidates.jsonl", ["ppl.ingestion_contract", "ppl.snapshot_change_handoff", "ppl.retry", "ppl.cancellation"], "materialized_validated", "connector receipts satisfy pipeline acquisition requirements"),
        ("messaging", ["context.cp.event_message_settlement", "context.cp.partition_assignment"], "source_systems_and_pipeline_messaging", "research/domain_atlas/universes/source_systems/source-classes.jsonl", ["source.event_messaging_cdc.partitioned_append_log", "source.event_messaging_cdc.work_message_queue", "ppl.channel_contract", "ppl.delivery_guarantee"], "materialized_validated", "protocol transport realizes but does not own messaging delivery semantics"),
        ("types_shapes", ["context.cp.type_mapping", "context.cp.serialization_framing"], "data_shapes", "research/domain_atlas/universes/data_shapes/bounded-context-candidates.jsonl", ["bc.carrier_representation", "bc.schema_compatibility", "bc.event_change_stream", "bc.time_calendar"], "materialized_validated", "connector mapping preserves type/shape qualifiers and emits gaps"),
        ("security", ["context.cp.authentication", "context.cp.authorization_scope", "context.cp.secret_reference"], "security_privacy_trust", "research/domain_atlas/universes/security_privacy_trust/bounded-context-candidates.jsonl", ["spt.authentication", "spt.authorization_policy", "spt.secrets_management", "spt.supply_chain_attestation"], "materialized_validated", "security universe owns policy; connector enforces and receipts decisions"),
        ("quality", ["context.cp.implementation_qualification", "context.cp.receipt_evidence"], "quality_observability_reconciliation", "research/domain_atlas/universes/quality_observability_reconciliation/bounded-context-candidates.jsonl", ["qor.context.contract_observation", "qor.context.validation_execution", "qor.context.evidence_receipt", "qor.context.reconciliation_execution"], "materialized_validated", "connector observations feed quality and reconciliation without self-certifying correctness"),
        ("lineage", ["context.cp.receipt_evidence", "context.cp.observability"], "lineage_provenance_evidence", "research/domain_atlas/universes/lineage_provenance_evidence/build_corpus.py", ["context.lpe.runtime-receipts", "context.lpe.audit-event", "context.lpe.source-lineage"], "generator_contract_surface", "connector receipts are evidence inputs; lineage owns derivation claims"),
        ("provider_target", ["context.cp.implementation_qualification", "context.cp.deployment_binding"], "provider_target_registry", "research/domain_atlas/compiler/provider_target_registry/build_registry.py", ["context.ptr.identity", "context.ptr.offer", "context.ptr.target.occurrence"], "generator_contract_surface", "provider/target registry owns concrete offers and targets; this universe owns connector semantics"),
    ]
    return [{
        "crosswalk_id": f"crosswalk.cp.{key}", "edition": EDITION, "status": "candidate", "local_refs": local,
        "external_universe": universe, "external_path": path, "external_refs": external, "reference_status": status,
        "relationship": relation, "ownership_law": "The external universe retains semantic ownership; this mapping is read-only and cannot strengthen its claims.",
    } for key, local, universe, path, external, status, relation in rows]


def gap_records() -> list[dict]:
    rows = [
        ("primary_clause_pinning", "context.cp.receipt_evidence", "evidence_depth", True, "Official sources and edition labels are recorded.", "Normative clause anchors and content digests are incomplete.", "Pin clauses/digests and complete independent review.", "A mutable landing page cannot prove an immutable protocol clause.", "rfc9110"),
        ("independent_saturation", "context.cp.gap_refusal", "coverage", True, "More than seventy primary/official specifications span requested families.", "Independent reviewers and recurring saturation searches are absent.", "Two independent reviews and scheduled evidence refresh complete without material new families.", "Record count is not completeness.", "openapi32"),
        ("live_occurrence_absent", "context.cp.deployment_binding", "deployment", True, "Schemas and hostile fixtures model occurrences.", "No real connector deployment, credentials, entitlements, or live probes are asserted.", "Register an authorized occurrence and execute scoped conformance probes.", "Fixture behavior cannot qualify production.", "slsa1"),
        ("provider_limits", "context.cp.rate_limit", "limits", True, "Limit surfaces and receipts are typed.", "Numerical values vary by tenant, region, edition, contract, and time.", "Observe every binding-critical limit on the target occurrence.", "Never copy a class-level default.", "rfc9110"),
        ("end_to_end_effect", "context.cp.idempotency", "delivery", True, "Protocol and connector delivery states are explicit.", "End-to-end effect requires source, pipeline state, and sink proofs.", "Compose and verify an end-to-end effect protocol.", "Connector exactly-once is not end-to-end exactly-once.", "kafka_protocol"),
        ("snapshot_consistency", "context.cp.snapshot_cut", "consistency", True, "Snapshot cut and export completion are separate states.", "Many APIs do not expose a stable cross-object cut.", "Provide a source-supported cut or declare reconciliation/limitations.", "Export completion cannot be treated as snapshot consistency.", "postgres_logical"),
        ("cdc_topology_change", "context.cp.cdc_resume", "recovery", True, "Resume-token purpose and expiry are modeled.", "Topology/version changes may invalidate tokens differently per source.", "Qualify restart across supported topology and version transitions.", "A readable token is not proof of resumability.", "debezium"),
        ("webhook_acceptance", "context.cp.webhook_delivery", "acceptance", False, "Transport and application receipts are distinct.", "Many webhook producers expose no durable business-acceptance receipt.", "Declare at-least-once plus application deduplication or a stronger verified profile.", "HTTP 2xx cannot prove downstream business processing.", "websub"),
        ("legacy_encodings", "context.cp.legacy_record_transport", "legacy", True, "Blocking and code-page decisions are explicit.", "Site copybooks, control totals, code pages, and truncation behavior are occurrence-owned.", "Acquire authoritative layouts and validate hostile byte fixtures.", "Do not infer record layout from file suffix.", "tn3270e"),
        ("ot_write_safety", "context.cp.industrial_command_safety", "safety", True, "Industrial commands compile read-only by default.", "Safety authority, interlocks, and physical outcome receipts are site-specific.", "Obtain control authority and pass destructive-guard tests in an approved environment.", "Authentication alone never authorizes a physical command.", "opcua"),
        ("paid_standards", "context.cp.domain_profile_conformance", "evidence_access", False, "Primary publisher catalogues identify several standards.", "Some full normative texts require licensed access.", "Record licensed clause-level evidence under permitted redistribution terms.", "A public overview is not the full conformance specification.", "x12"),
        ("browser_delivery", "context.cp.browser_client_telemetry", "delivery", False, "Browser enqueue and collector acceptance are separate.", "User agent lifecycle and privacy policies can drop or reduce telemetry.", "Qualify each browser/profile and reconcile server receipts.", "API call success does not prove network delivery.", "beacon"),
        ("saas_semantics", "connector.class.cp.http_resource_reader", "provider_mapping", True, "Generic SaaS API protocol classes are represented.", "Object authority, rate policies, bulk jobs, deletions, and change semantics are provider-specific.", "Bind a provider adapter offer with current official docs and occurrence probes.", "Do not create a connector class from a SaaS vendor name.", "openapi32"),
        ("license_compatibility", "context.cp.license_supply_chain", "licensing", True, "License and SBOM surfaces are required.", "No implementation artifact has been selected or legally reviewed.", "Complete artifact-specific license, export, vulnerability, provenance and support review.", "Protocol openness does not make every client library redistributable.", "spdx3"),
        ("cost_forecast", "context.cp.quota_cost", "cost", False, "Cost is an occurrence-level finite budget.", "Pricing tiers, egress, minimums and request classification are mutable.", "Snapshot official pricing/contract evidence and reconcile actual bills.", "A protocol request count is not a monetary cost.", "rfc9110"),
    ]
    return [{
        "gap_id": f"gap.cp.{key}", "edition": EDITION, "status": "open", "subject_ref": subject, "gap_kind": kind,
        "blocking": blocking, "known": known, "unknown": unknown, "resolution_condition": resolution,
        "prohibited_assumption": prohibited, "evidence_refs": [f"evidence.cp.{evidence}"],
    } for key, subject, kind, blocking, known, unknown, resolution, prohibited, evidence in rows]


def negative_twins() -> list[dict]:
    rows = [
        ("source_vs_connector_class", "source-system capability class", "connector access class", "Makes protocol/package names own business authority.", "Preserve both IDs and require an explicit binding.", "identity_layers"),
        ("class_vs_artifact", "connector class", "implementation artifact", "Treats required behavior as executable/qualified code.", "Require build identity and qualification separately.", "identity_layers"),
        ("artifact_vs_occurrence", "implementation artifact", "deployed connector occurrence", "Hides configuration, credentials, network, limits and observations.", "Bind an occurrence with a configuration fingerprint.", "identity_layers"),
        ("protocol_vs_data_model", "protocol framing/operations", "payload data model and semantics", "Wire compatibility becomes semantic compatibility.", "Validate carrier, schema, profile and semantic mapping separately.", "schema_type_change"),
        ("documented_vs_probed", "documented capability", "probed behavior", "Turns mutable documentation into deployment evidence.", "Store both assertions with independent provenance and time.", "advertised_vs_probed"),
        ("read_cursor_vs_cdc_token", "pagination/read cursor", "CDC resume token", "Can silently skip changes or resume the wrong operation.", "Type tokens by issuer, operation, scope and expiry.", "read_cursor_vs_cdc"),
        ("transport_vs_acceptance", "transport success", "source acceptance/commit", "Publishes or acknowledges effects that the source later rejects.", "Require distinct receipts and terminal outcome polling where needed.", "transport_vs_acceptance"),
        ("cut_vs_completion", "snapshot consistency cut", "export job completion", "A completed export may combine different source moments.", "Record cut proof separately from job lifecycle.", "snapshot_cut_vs_completion"),
        ("connector_vs_end_to_end", "connector exactly-once claim", "end-to-end effect exactly once", "Ignores source replay, pipeline recovery and sink commit boundaries.", "Require a composed effect proof or refuse the claim.", "connector_vs_end_to_end_exactly_once"),
        ("authn_vs_authz", "authenticated principal", "authorized operation/object scope", "May expose forbidden data or mislabel denial as emptiness.", "Verify least privilege for each operation and object.", "authn_vs_authz"),
        ("retryable_vs_safe", "temporarily retryable failure", "safe-to-repeat effect", "Retries can duplicate non-idempotent writes.", "Prove effect identity/deduplication before retrying.", "write_idempotency"),
        ("cancelled_vs_stopped", "local task cancelled", "remote work stopped", "Leaves unobserved external effects in flight.", "Reconcile remote disposition and emit outcome_unknown when necessary.", "cancel_disposition"),
        ("ordered_vs_final", "ordered observation", "final business fact", "A correctly sequenced item may later be reversed or corrected.", "Track ordering and finality independently.", "finality_correction"),
        ("encrypted_vs_authenticated", "encrypted channel", "authenticated intended peer", "Allows secure communication with the wrong endpoint.", "Verify peer identity and policy, not encryption alone.", "tls_peer"),
        ("fixture_vs_live_probe", "synthetic conformance fixture", "authorized live occurrence probe", "Fabricates qualification and production claims.", "Keep fixtures binding-ineligible until scoped live evidence exists.", "advertised_vs_probed"),
    ]
    return [{"twin_id": f"negative.cp.{key}", "edition": EDITION, "status": "candidate", "left": left, "right": right, "unsafe_collapse": danger, "compiler_response": response, "test_refs": [f"test.cp.{test}"]} for key, left, right, danger, response, test in rows]


def occurrence_fixtures(artifacts: list[dict]) -> list[dict]:
    rows = [
        ("hostile_http_202", "hostile_test_fixture", "http_resource_reader", "reference_http_reader", "operation.cp.submit_source_command", {"transport": "HTTP 202", "source": "later rejected"}),
        ("hostile_expired_cdc", "hostile_test_fixture", "database_cdc_reader", "reference_cdc_reader", "operation.cp.resume_change_feed", {"token": "syntactically valid", "source": "expired before retained boundary"}),
        ("hostile_partial_bulk", "hostile_test_fixture", "bulk_export_job_reader", "reference_bulk_reader", "operation.cp.collect_completed_export", {"job": "accepted", "source": "failed after partial artifact"}),
        ("legacy_ebcdic_blocked", "legacy_test_fixture", "legacy_batch_reader", "reference_file_reader", "operation.cp.read_blocked_records", {"encoding": "EBCDIC variant unknown", "record_blocking": "mixed and truncated"}),
        ("hostile_webhook_duplicate", "hostile_test_fixture", "webhook_receiver", "reference_webhook_receiver", "operation.cp.acknowledge_webhook", {"delivery": "duplicated after lost acknowledgement", "application": "deduplication required"}),
        ("hostile_ot_command", "hostile_test_fixture", "guarded_industrial_commander", "reference_ot_reader", "operation.cp.submit_guarded_command", {"authentication": "present", "authorization": "absent", "interlock": "unsafe"}),
        ("browser_unload_drop", "hostile_test_fixture", "browser_telemetry_collector", "reference_browser_collector", "operation.cp.enqueue_client_beacon", {"enqueue": "true", "collector": "no receipt"}),
    ]
    return [{
        "occurrence_id": f"occurrence.cp.{key}", "edition": EDITION, "status": "test_fixture", "occurrence_kind": kind,
        "source_occurrence_ref": None, "connector_class_ref": f"connector.class.cp.{class_key}", "artifact_ref": f"artifact.cp.{artifact_key}",
        "deployment_identity": {"environment": "synthetic-only", "site": "none", "tenant": "none", "region": "none", "version": "fixture"},
        "configuration_fingerprint": f"fixture:{key}:no-secret", "credential_references_only": True, "enabled_operations": [operation],
        "documented_capabilities": {"status": "fixture assertion", "source_refs": []},
        "probed_behavior": {"probe_kind": "synthetic hostile scenario; not live", "observations": observed, "observed_at": None},
        "snapshot_cut_cursor_change": {"snapshot_cut": "unknown", "read_cursor": "typed separately", "cdc_resume_token": "typed separately", "handoff": "unqualified"},
        "schema_type_time_order_finality": {"schema": "fixture", "type_mapping": "explicit gaps", "time": "fixture clock", "ordering": "unknown", "finality": "unknown"},
        "limits_rate_quota_cost": {"values": "unknown", "portable_defaults": False, "cost": "not_applicable"},
        "retry_idempotency_cancellation": {"retry": "disabled unless scenario declares", "idempotency": "unproven", "cancellation": "outcome must be recorded"},
        "partition_recovery": {"partition": "fixture-specific", "checkpoint": "ephemeral", "recovery": "test reset only"},
        "observability_receipts": {"transport": "separate", "source_acceptance": "separate", "test": "synthetic result only"},
        "qualification": {"live_probe": False, "qualified": False, "reason": "negative/hostile fixture"}, "binding_eligible": False,
    } for key, kind, class_key, artifact_key, operation, observed in rows]


def conformance_harness(tests: list[dict]) -> dict:
    return {
        "harness_id": "harness.cp.connector_conformance", "edition": EDITION, "status": "candidate",
        "candidate_only": True, "live_probe_default": "forbidden", "credential_policy": "opaque references only; never stored in corpus or receipts",
        "phases": [
            {"phase": "static_declaration", "inputs": ["connector class", "artifact manifest", "protocol profiles"], "outputs": ["structural findings"]},
            {"phase": "synthetic_hostile", "inputs": ["negative twins", "fixture occurrence"], "outputs": ["deterministic conformance receipts"]},
            {"phase": "authorized_occurrence", "inputs": ["separately approved sandbox", "credential references", "finite budgets"], "outputs": ["scoped observations"], "default": "disabled"},
            {"phase": "qualification", "inputs": ["receipts", "artifact/configuration fingerprint", "invalidation triggers"], "outputs": ["qualified, rejected, or inconclusive"]},
        ],
        "test_refs": [item["test_id"] for item in tests],
        "laws": [
            "unsupported, not-authorized and inconclusive are never treated as empty success",
            "destructive tests require separate control authority and safe target",
            "a test receipt is scoped to artifact version, configuration, occurrence and observation time",
            "any material version, topology, authorization or configuration change invalidates affected receipts",
        ],
    }


def coverage_matrix() -> dict:
    rows = [
        ("database_wire_query_change", ["postgresql_wire", "mysql_client_server", "tds", "mongodb_wire", "postgresql_logical_replication"], ["relational_query_reader", "database_cdc_reader"], ["query_request", "change_capture", "cdc_resume"]),
        ("file_object_transfer", ["ftp", "sftp", "rsync", "s3_rest", "tus10"], ["managed_file_receiver", "object_store_reader", "resumable_object_writer"], ["file_transfer", "recovery_replay"]),
        ("rest_graphql_grpc_soap_odata", ["http11", "openapi32", "graphql2025", "grpc", "soap12", "odata401"], ["http_resource_reader", "graphql_reader", "rpc_reader", "soap_service_adapter", "odata_delta_reader"], ["query_request", "pagination", "serialization_framing"]),
        ("webhooks", ["webhook_http", "websub"], ["webhook_receiver"], ["webhook_delivery", "subscription"]),
        ("event_messaging", ["amqp10", "mqtt5", "kafka_wire", "stomp12", "nats_jetstream"], ["amqp_consumer", "mqtt_consumer", "partitioned_log_consumer"], ["event_message_settlement", "partition_assignment"]),
        ("bulk_export_import", ["fhir_bulk20", "odata_batch", "scim_bulk", "s3_multipart"], ["bulk_export_job_reader", "bulk_import_writer"], ["bulk_job", "file_transfer"]),
        ("saas_apis", ["http11", "openapi32", "graphql2025", "odata401"], ["enterprise_saas_resource_reader", "collaboration_saas_reader", "devops_saas_reader", "security_saas_reader", "analytical_saas_reader", "saas_writeback_adapter"], ["capability_discovery", "pagination", "rate_limit", "quota_cost"]),
        ("industrial_ot_iot", ["opcua", "modbus_tcp", "bacnet", "iec61850", "dnp3", "sparkplug30", "onem2m", "matter"], ["opcua_reader", "modbus_reader", "power_telecontrol_reader", "iot_resource_reader", "guarded_industrial_commander"], ["industrial_command_safety", "subscription"]),
        ("healthcare", ["fhir_r5_rest", "fhir_bulk20", "dicomweb", "dicom_dimse", "hl7v2_mllp", "ihe_xds"], ["fhir_reader", "dicom_reader", "hl7_message_receiver"], ["domain_profile_conformance", "bulk_job"]),
        ("finance_market_messaging", ["fix_session", "fixp", "iso20022_messages", "xbrl_reporting", "ofx23"], ["fix_market_reader", "financial_message_adapter", "regulatory_filing_reader"], ["ordering", "finality_correction", "domain_profile_conformance"]),
        ("geospatial_scientific", ["ogc_api_features", "wfs20", "stac11", "sensorthings11", "zarr3", "netcdf", "hdf5"], ["geospatial_feature_reader", "geospatial_catalog_reader", "sensor_observation_reader", "chunked_array_reader"], ["schema_introspection", "type_mapping", "pagination"]),
        ("edi", ["un_edifact", "x12_edi", "as2", "as4", "ebms3", "epcis20"], ["edi_interchange_receiver", "supply_chain_event_reader"], ["receipt_evidence", "legacy_record_transport", "domain_profile_conformance"]),
        ("email_collaboration", ["imap4rev2", "smtp", "jmap", "caldav", "carddav", "activitystreams20"], ["mailbox_reader", "mail_sender", "calendar_reader", "contact_activity_reader"], ["read_cursor", "change_capture", "time_watermark"]),
        ("mainframe_legacy", ["drda", "tn3270e", "fixed_record_ftp", "ebcdic_blocked_file"], ["mainframe_terminal_adapter", "legacy_batch_reader"], ["legacy_record_transport"]),
        ("filesystem_object_block", ["posix_file_io", "nfs41", "smb3", "s3_rest", "iscsi", "nvme_over_fabrics"], ["filesystem_scanner", "object_store_reader", "block_replication_adapter"], ["file_transfer", "recovery_replay"]),
        ("browser_client_telemetry", ["otlp", "trace_context", "beacon", "reporting_api", "navigation_timing2"], ["telemetry_exporter", "browser_telemetry_collector"], ["browser_client_telemetry", "observability", "receipt_evidence"]),
        ("command_writeback", ["http11", "openapi32", "odata401", "opcua", "modbus_tcp", "matter"], ["guarded_resource_writer", "saas_writeback_adapter", "guarded_industrial_commander"], ["write_mutation", "command_acceptance", "idempotency", "industrial_command_safety"]),
        ("discovery_introspection", ["openapi32", "wsdl20", "opcua", "stac11"], ["http_resource_reader", "opcua_reader", "geospatial_catalog_reader"], ["capability_discovery", "namespace_discovery", "schema_introspection"]),
        ("authentication_authorization_secrets", ["http11", "grpc", "sftp", "mqtt5"], ["http_resource_reader", "rpc_reader", "managed_file_receiver", "mqtt_consumer"], ["authentication", "authorization_scope", "secret_reference", "network_security"]),
        ("snapshot_cut_cursor_resume_change", ["postgresql_logical_replication", "mysql_binary_log", "mongodb_wire", "odata401", "jmap"], ["database_cdc_reader", "odata_delta_reader", "mailbox_reader"], ["snapshot_cut", "read_cursor", "change_capture", "cdc_resume", "snapshot_change_handoff"]),
        ("schema_type_time_order_finality", ["graphql2025", "grpc", "cloudevents10", "fix_session", "zarr3"], ["graphql_reader", "rpc_reader", "cloud_event_adapter", "fix_market_reader", "chunked_array_reader"], ["schema_introspection", "type_mapping", "time_watermark", "ordering", "finality_correction"]),
        ("limits_rate_quota_cost", ["http11", "odata401", "kafka_wire"], ["http_resource_reader", "partitioned_log_consumer"], ["rate_limit", "quota_cost"]),
        ("retry_idempotency_cancellation", ["http11", "grpc", "amqp10", "coap"], ["http_resource_reader", "rpc_reader", "amqp_consumer", "coap_device_reader"], ["retry", "idempotency", "cancellation"]),
        ("partition_recovery", ["kafka_wire", "nats_jetstream", "nfs41", "iscsi"], ["partitioned_log_consumer", "nats_consumer", "filesystem_scanner", "block_replication_adapter"], ["partition_assignment", "recovery_replay"]),
        ("observability_receipts", ["otlp", "trace_context", "as2", "amqp10"], ["telemetry_exporter", "edi_interchange_receiver", "amqp_consumer"], ["observability", "receipt_evidence"]),
        ("versioning_deprecation", ["openapi32", "graphql2025", "fhir_r5_rest", "zarr3"], ["http_resource_reader", "graphql_reader", "fhir_reader", "chunked_array_reader"], ["version_negotiation", "deprecation_exit"]),
        ("licensing_supply_chain", ["oci_distribution"], ["artifact_registry_reader"], ["license_supply_chain", "implementation_qualification"]),
    ]
    return {
        "matrix_id": "coverage.cp.requested_surfaces", "edition": EDITION, "status": "candidate", "completion_claim": False,
        "dimensions": [{
            "dimension": name,
            "protocol_refs": [f"protocol.cp.{item}" for item in protocol_keys],
            "connector_class_refs": [f"connector.class.cp.{item}" for item in class_keys],
            "context_refs": [f"context.cp.{item}" for item in context_keys],
            "coverage_law": "Presence demonstrates modeled coverage only; binding still requires artifact qualification and occurrence evidence.",
        } for name, protocol_keys, class_keys, context_keys in rows],
    }


def main() -> int:
    build_schemas()
    evidence = evidence_records()
    evidence_ids = {item["evidence_id"] for item in evidence}
    contexts, capabilities, operations, decisions = context_records(evidence_ids)
    protocols = protocol_records(evidence_ids)
    protocol_ids = {item["protocol_id"] for item in protocols}
    evidence_by_protocol = {item["protocol_id"]: item["evidence_refs"] for item in protocols}
    classes = connector_classes(protocol_ids, evidence_by_protocol)
    lifecycle_records = lifecycles()
    tests = conformance_tests(evidence_ids)
    compiler = compiler_records(capabilities, operations)
    libraries = library_records()
    innovations = innovation_records()
    crosswalks = crosswalk_records()
    gaps = gap_records()
    twins = negative_twins()
    artifacts = implementation_records([item["connector_class_id"] for item in classes], sorted(protocol_ids), [item["capability_id"] for item in capabilities])
    occurrences = occurrence_fixtures(artifacts)

    outputs = {
        "bounded-context-candidates.jsonl": contexts,
        "protocols.jsonl": protocols,
        "capabilities.jsonl": capabilities,
        "operations.jsonl": operations,
        "decisions.jsonl": decisions,
        "lifecycles.jsonl": lifecycle_records,
        "connector-classes.jsonl": classes,
        "implementation-artifacts.jsonl": artifacts,
        "deployed-connector-occurrences.jsonl": occurrences,
        "evidence.jsonl": evidence,
        "innovations-2021-2026.jsonl": innovations,
        "compiler-requirements.jsonl": [item for item in compiler if item["record_kind"] == "requirement"],
        "capability-offer-templates.jsonl": [item for item in compiler if item["record_kind"] == "offer_template"],
        "compiler-mappings.jsonl": [item for item in compiler if item["record_kind"] == "mapping"],
        "library-boundaries.jsonl": libraries,
        "conformance-tests.jsonl": tests,
        "cross-universe-mappings.jsonl": crosswalks,
        "gaps.jsonl": gaps,
        "negative-twins.jsonl": twins,
    }
    for filename, records in outputs.items():
        dump_jsonl(HERE / filename, records)
    dump_json(EXAMPLES / "conformance-harness.json", conformance_harness(tests))
    dump_json(EXAMPLES / "hostile-scenarios.json", {"status": "test_fixture", "candidate_only": True, "occurrence_refs": [item["occurrence_id"] for item in occurrences], "negative_twin_refs": [item["twin_id"] for item in twins], "no_credentials": True, "no_live_probes": True})
    dump_json(HERE / "coverage-matrix.json", coverage_matrix())

    core_count = sum(len(outputs[name]) for name in ["protocols.jsonl", "capabilities.jsonl", "operations.jsonl", "decisions.jsonl", "lifecycles.jsonl"])
    report = {
        "report_id": "coverage.cp.connectors_protocols", "edition": EDITION, "as_of": AS_OF,
        "status": "candidate_research_corpus", "completion_claim": False,
        "counts": {filename.removesuffix(".jsonl").replace("-", "_"): len(records) for filename, records in sorted(outputs.items())},
        "core_protocol_capability_operation_decision_lifecycle_records": core_count,
        "protocol_families": sorted({item["family"] for item in protocols}),
        "primary_official_evidence_sources": len(evidence), "distinct_evidence_issuers": len({item["issuer"] for item in evidence}),
        "bounded_context_threshold_met": len(contexts) >= 45, "core_record_threshold_met": core_count >= 220,
        "evidence_threshold_met": len(evidence) >= 70, "innovation_threshold_met": len(innovations) >= 20,
        "real_deployed_occurrences": 0, "fixture_occurrences": len(occurrences), "live_probes": 0, "credentials": 0,
        "standing": "broad_candidate_taxonomy_with_primary_evidence_and_unresolved_independent_review",
    }
    dump_json(HERE / "coverage-report.json", report)
    manifest = {
        "universe_id": "connectors_protocols", "edition": EDITION, "status": "candidate_research_contract", "as_of": AS_OF,
        "completion_claim": False, "core_scope": "Provider-neutral connector, adapter and protocol contracts between source-system needs/classes and deployed source occurrences.",
        "excludes": ["vendor connector catalog", "LLM or generative core semantics", "credentials", "fabricated live probes", "provider selection by name"],
        "identity_law": ["source class != source occurrence", "connector class != implementation artifact", "implementation artifact != deployed connector occurrence", "protocol != data model"],
        "files": sorted([*outputs, "coverage-report.json", "coverage-matrix.json", "examples/conformance-harness.json", "examples/hostile-scenarios.json"]),
    }
    dump_json(HERE / "manifest.json", manifest)
    print(f"WROTE connectors/protocols: {len(contexts)} contexts, {core_count} core records, {len(classes)} connector classes, {len(evidence)} evidence sources, {len(innovations)} innovations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
