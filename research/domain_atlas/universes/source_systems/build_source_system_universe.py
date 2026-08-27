#!/usr/bin/env python3
"""Build the provider-neutral source-system universe.

The terse seed table in this file is an editorial convenience.  The emitted JSONL
contains the fully expanded capability contract for every class.  A compiler consumes
the emitted records, never this seed table and never a vendor-name switch statement.
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
AS_OF = "2026-08-25"


AXES = {
    "family_id": [
        "operational_database", "analytical_repository", "file_object_content",
        "api_remote_service", "event_messaging_cdc", "enterprise_application",
        "collaboration_productivity", "code_devops", "security_identity",
        "telemetry_digital_experience", "iot_edge", "industrial_ot",
        "scientific_research", "geospatial_media", "public_reference",
        "regulated_vertical", "legacy_offline",
    ],
    "authority_role": [
        "system_of_record", "authoritative_publication", "operational_projection",
        "derived_replica", "transport_channel", "observation_recorder",
        "human_workflow_record", "device_state", "composite_requires_field_authority",
    ],
    "logical_model": [
        "relational", "document", "key_value", "wide_column", "property_graph",
        "rdf_graph", "search_index", "vector_index", "time_series", "spatial_feature",
        "raster_grid", "multidimensional_array", "multidimensional_cube", "ledger",
        "append_log", "work_queue", "object_blob", "hierarchical_message",
        "binary_message", "tabular_record", "fixed_record", "content_tree",
        "activity_graph", "signal", "trace_graph", "image", "audio", "video",
        "point_cloud", "mesh_bim", "version_graph", "registry", "workflow_case",
        "digital_twin", "tensor", "simulation_state",
    ],
    "payload_shape": [
        "rows", "nested_records", "keyed_values", "edges_nodes", "triples_quads",
        "documents_terms", "vectors_metadata", "series_samples", "arrays_chunks",
        "events", "messages", "commands", "files", "objects", "pages_cells_formulas",
        "content_versions", "signals_waveforms", "images_frames", "audio_samples",
        "video_frames", "geometries_tiles", "points", "meshes", "facts_dimensions",
        "cases_tasks", "packages_artifacts", "identity_entitlements", "opaque_records",
    ],
    "discovery_mode": [
        "catalog", "namespace_list", "schema_introspection", "capability_document",
        "topic_list", "directory_walk", "manifest", "service_description",
        "device_browse", "manual_inventory", "none",
    ],
    "read_mode": [
        "point_get", "query", "scan", "snapshot", "range_read", "page_cursor",
        "incremental_cursor", "change_data_capture", "subscription", "stream", "poll", "file_arrival",
        "manual_export", "federated_query", "device_read", "media_playback",
    ],
    "write_mode": [
        "none", "append", "insert", "upsert", "replace", "delete", "transaction",
        "bulk_load", "publish", "command", "acknowledge", "file_put", "human_edit",
    ],
    "change_mode": [
        "none", "transaction_log", "change_stream", "revision_feed", "webhook",
        "subscription", "poll_diff", "file_arrival", "queue_delivery", "event_log",
        "device_notification", "manual_reexport",
    ],
    "schema_mode": [
        "fixed", "declared", "declared_evolving", "inferred", "schema_on_read",
        "registry_governed", "taxonomy_governed", "profile_governed", "opaque",
        "mixed_per_object",
    ],
    "compatibility_policy": [
        "exact_version", "backward", "forward", "full", "reader_writer_resolution",
        "profile_negotiated", "provider_defined", "none",
    ],
    "clock_model": [
        "transaction_clock", "server_clock", "event_producer_clock", "device_clock",
        "human_entered", "file_metadata_clock", "market_clock", "simulation_clock",
        "multiple_unreconciled", "none",
    ],
    "time_axis": [
        "event_time", "observation_time", "effective_valid_time", "recorded_system_time",
        "transaction_commit_time", "revision_publication_time", "ingestion_time",
        "schedule_service_time", "processing_time", "none",
    ],
    "ordering_scope": [
        "none", "per_key", "per_partition", "per_session", "per_transaction",
        "global_log", "source_sequence", "document_revision", "file_byte_order",
        "service_defined",
    ],
    "finality_model": [
        "commit_final", "majority_or_quorum_final", "append_final", "mutable_current_state",
        "workflow_approved", "settlement_final", "publication_revision", "windowed_late",
        "provisional_then_corrected", "device_best_effort", "never_intrinsically_final",
    ],
    "deletion_semantics": [
        "hard_delete", "soft_delete", "tombstone", "expiry_ttl", "compaction_loss",
        "redaction", "legal_hold", "superseded_revision", "not_exposed", "not_applicable",
    ],
    "transaction_boundary": [
        "single_record", "multi_record", "single_partition", "database_transaction",
        "message_delivery", "file_replace", "object_put", "document_revision",
        "business_workflow", "device_command", "none", "provider_defined",
    ],
    "consistency_model": [
        "serializable", "snapshot_isolation", "read_committed", "strong",
        "causal_session", "monotonic_session", "quorum_tunable", "eventual",
        "immutable_snapshot", "human_workflow", "transport_defined", "device_best_effort",
        "provider_defined",
    ],
    "access_topology": [
        "local_process", "local_network", "private_network", "public_internet",
        "partner_network", "managed_file_exchange", "device_gateway", "field_bus",
        "air_gapped", "human_mediated", "federated",
    ],
    "sensitivity_default": [
        "ordinary_enterprise", "credentials_secrets", "personal", "highly_sensitive_personal",
        "financial_regulated", "health_regulated", "safety_critical", "export_controlled",
        "licensed_restricted", "public", "deployment_specific",
    ],
}


VERIFICATION_TESTS = [
    ("verify.identity.authority", "Prove stable occurrence, namespace, object identity and field-level authority."),
    ("verify.discovery.capability_probe", "Compare advertised and empirically observed objects, schemas and operations."),
    ("verify.read.repeatable_snapshot", "Demonstrate a documented repeatable cut or explicitly reject snapshot semantics."),
    ("verify.read.pagination_mutation", "Mutate data during paging and detect omissions, repeats and cursor invalidation."),
    ("verify.change.snapshot_handoff", "Prove no gap or overlap loss between initial snapshot and change capture."),
    ("verify.change.resume_expiry", "Resume from checkpoints across disconnects and exercise cursor/retention expiry."),
    ("verify.delivery.duplicates", "Inject retries and redelivery; prove declared deduplication and idempotency behavior."),
    ("verify.delivery.order_gaps", "Reorder, omit and duplicate inputs; prove order scope and gap detection."),
    ("verify.delivery.replay_retention", "Replay within and beyond retention and verify an explicit terminal failure."),
    ("verify.delete.all_forms", "Exercise hard, soft, tombstone, TTL, redaction and not-exposed deletion paths."),
    ("verify.schema.compatibility", "Exercise additive, subtractive, rename, type, constraint and unknown-field changes."),
    ("verify.schema.identity_drift", "Detect key reuse, namespace moves, hierarchy drift and identity crosswalk changes."),
    ("verify.time.clock_and_lateness", "Measure clock source, skew, timezone, DST, lateness and revision-time behavior."),
    ("verify.finality.correction_retraction", "Exercise provisional, approved, corrected, reversed and retracted states."),
    ("verify.transaction.atomicity", "Observe commits and aborts at the declared transaction boundary."),
    ("verify.security.least_privilege", "Prove minimum read/discovery scopes and reject unauthorized objects and fields."),
    ("verify.security.tenant_boundary", "Prove tenant, row, field, object and inherited-ACL isolation."),
    ("verify.security.audit_rotation", "Rotate credentials/keys and reconcile access with immutable audit evidence."),
    ("verify.limit.envelope", "Probe rate, quota, page, payload, concurrency, retention and cost envelopes safely."),
    ("verify.reconcile.count_hash", "Reconcile counts, sums, hashes and domain control totals by stable cut."),
    ("verify.write.destructive_guard", "Prove writes/commands are disabled by default and require explicit policy."),
    ("verify.offline.reconnect", "Exercise long disconnection, buffered writes, conflict resolution and clock discontinuity."),
    ("verify.content.version_acl", "Verify content bytes, renditions, version identity, ACL inheritance, holds and redaction."),
    ("verify.media.codec_metadata", "Verify codec/container, orientation, frame/sample timing, checksums and metadata loss."),
    ("verify.vertical.conformance", "Validate profiles, code systems, identifiers and conformance artifacts for the domain."),
]


EVIDENCE = [
    ("ev.postgresql.mvcc", "PostgreSQL MVCC and transaction isolation", "PostgreSQL Global Development Group", "https://www.postgresql.org/docs/current/mvcc.html", ["transactions", "consistency", "snapshots"], "official_implementation_documentation"),
    ("ev.mongodb.change", "MongoDB Change Streams", "MongoDB", "https://www.mongodb.com/docs/manual/changeStreams/", ["change", "resume", "finality", "security"], "official_implementation_documentation"),
    ("ev.cassandra.architecture", "Apache Cassandra architecture and guarantees", "Apache Software Foundation", "https://cassandra.apache.org/doc/latest/cassandra/architecture/overview.html", ["consistency", "partitioning", "schema"], "official_implementation_documentation"),
    ("ev.neo4j.transactions", "Neo4j database internals and transactional behavior", "Neo4j", "https://neo4j.com/docs/operations-manual/current/database-internals/", ["transactions", "consistency", "limits"], "official_implementation_documentation"),
    ("ev.sqlite.isolation", "Isolation in SQLite", "SQLite", "https://www.sqlite.org/isolation.html", ["transactions", "snapshots", "offline"], "official_implementation_documentation"),
    ("ev.s3.multipart", "Amazon S3 multipart upload limits", "Amazon Web Services", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html", ["objects", "limits", "partial_upload"], "official_provider_contract"),
    ("ev.posix.files", "POSIX file and directory interfaces", "The Open Group", "https://pubs.opengroup.org/onlinepubs/9799919799/", ["files", "identity", "atomicity"], "normative_standard"),
    ("ev.rfc4180.csv", "RFC 4180 Common Format and MIME Type for CSV Files", "IETF", "https://www.rfc-editor.org/rfc/rfc4180.html", ["tabular_files", "schema"], "normative_standard"),
    ("ev.parquet.format", "Apache Parquet format specification", "Apache Software Foundation", "https://github.com/apache/parquet-format", ["columnar_files", "schema", "statistics", "encryption"], "official_specification"),
    ("ev.avro.spec", "Apache Avro specification", "Apache Software Foundation", "https://avro.apache.org/docs/1.12.0/specification/", ["binary_records", "schema", "compatibility"], "official_specification"),
    ("ev.opendocument", "OpenDocument 1.3 and OpenFormula", "OASIS Open", "https://docs.oasis-open.org/office/OpenDocument/v1.3/os/", ["spreadsheets", "formulas", "content"], "normative_standard"),
    ("ev.cmis", "Content Management Interoperability Services 1.1", "OASIS Open", "https://docs.oasis-open.org/cmis/CMIS/v1.1/CMIS-v1.1.html", ["content", "versions", "acl", "change", "paging"], "normative_standard"),
    ("ev.http9110", "RFC 9110 HTTP Semantics", "IETF", "https://www.rfc-editor.org/rfc/rfc9110.html", ["api", "methods", "retries", "security"], "normative_standard"),
    ("ev.openapi", "OpenAPI Specification", "OpenAPI Initiative", "https://spec.openapis.org/oas/latest.html", ["api", "discovery", "schema", "security"], "official_specification"),
    ("ev.graphql", "GraphQL Specification", "GraphQL Foundation", "https://spec.graphql.org/September2025/", ["api", "schema", "partial_results"], "official_specification"),
    ("ev.odata", "OData Version 4.01", "OASIS Open", "https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html", ["api", "paging", "delta", "schema"], "normative_standard"),
    ("ev.grpc", "gRPC protocol documentation", "Cloud Native Computing Foundation", "https://grpc.io/docs/what-is-grpc/core-concepts/", ["rpc", "streaming", "deadlines"], "official_specification"),
    ("ev.webdav", "RFC 4918 WebDAV", "IETF", "https://www.rfc-editor.org/rfc/rfc4918.html", ["content", "locking", "properties", "security"], "normative_standard"),
    ("ev.amqp", "AMQP Version 1.0", "OASIS Open", "https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-complete-v1.0-os.html", ["messaging", "settlement", "ordering", "security"], "normative_standard"),
    ("ev.mqtt", "MQTT Version 5.0", "OASIS Open", "https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html", ["messaging", "qos", "retention", "limits"], "normative_standard"),
    ("ev.kafka.design", "Apache Kafka design documentation", "Apache Software Foundation", "https://kafka.apache.org/documentation/#design", ["append_log", "ordering", "transactions", "retention"], "official_implementation_documentation"),
    ("ev.cloudevents", "CloudEvents Specification", "Cloud Native Computing Foundation", "https://github.com/cloudevents/spec/blob/ce@v1.0.2/cloudevents/spec.md", ["events", "identity", "schema", "security"], "official_specification"),
    ("ev.debezium", "Debezium connector development and change-event documentation", "Debezium Project", "https://debezium.io/documentation/reference/stable/connectors/index.html", ["cdc", "snapshot_handoff", "schema", "deletes"], "official_implementation_documentation"),
    ("ev.epcis", "EPCIS and Core Business Vocabulary 2.0", "GS1", "https://ref.gs1.org/standards/epcis/2.0.1/", ["supply_chain", "events", "time", "identity"], "normative_standard"),
    ("ev.isa95", "ISA-95 enterprise-control system integration", "International Society of Automation", "https://www.isa.org/standards-and-publications/isa-standards/isa-95-standard", ["erp", "mes", "manufacturing", "authority"], "standards_body_primary_overview"),
    ("ev.opcua", "OPC Unified Architecture specifications", "OPC Foundation", "https://reference.opcfoundation.org/specifications", ["industrial", "browse", "subscription", "security", "limits"], "normative_standard"),
    ("ev.coap", "RFC 7252 Constrained Application Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc7252.html", ["iot", "discovery", "delivery", "security", "limits"], "normative_standard"),
    ("ev.sensorthings", "OGC SensorThings API Part 1 Sensing 1.1", "Open Geospatial Consortium", "https://docs.ogc.org/is/18-088/18-088.html", ["sensors", "observations", "geospatial", "api"], "normative_standard"),
    ("ev.netcdf", "NetCDF file format specifications", "Unidata", "https://docs.unidata.ucar.edu/netcdf-c/current/file_format_specifications.html", ["scientific", "arrays", "schema", "limits"], "official_specification"),
    ("ev.hdf5", "HDF5 File Format Specification", "The HDF Group", "https://support.hdfgroup.org/documentation/hdf5/latest/_f_m_t3.html", ["scientific", "arrays", "hierarchy"], "official_specification"),
    ("ev.geopackage", "OGC GeoPackage Encoding Standard", "Open Geospatial Consortium", "https://docs.ogc.org/is/12-128r19/12-128r19.html", ["geospatial", "offline", "features", "tiles"], "normative_standard"),
    ("ev.stac", "SpatioTemporal Asset Catalog specification", "STAC Project", "https://github.com/radiantearth/stac-spec/tree/v1.1.0", ["geospatial", "catalog", "assets", "time"], "official_specification"),
    ("ev.dicom", "DICOM current standard", "DICOM Standards Committee / NEMA", "https://dicom.nema.org/medical/dicom/current/output/html/part01.html", ["medical_imaging", "media", "conformance"], "normative_standard"),
    ("ev.fhir", "HL7 FHIR R5", "HL7 International", "https://hl7.org/fhir/R5/", ["health", "api", "versioning", "security", "provenance"], "normative_standard"),
    ("ev.iso20022", "ISO 20022 catalogue of messages", "ISO 20022 Registration Authority", "https://www.iso20022.org/catalogue-messages", ["finance", "messages", "versions", "codes"], "standards_body_primary_catalogue"),
    ("ev.fix", "FIX technical standards", "FIX Trading Community", "https://www.fixtrading.org/standards/", ["trading", "messages", "sessions", "ordering"], "standards_body_primary_catalogue"),
    ("ev.xbrl", "XBRL 2.1 and conformance suite", "XBRL International", "https://specifications.xbrl.org/work-product-index-group-base-spec-base-spec.html", ["regulatory_reporting", "facts", "units", "taxonomy", "validation"], "normative_standard"),
    ("ev.gtfs", "General Transit Feed Specification", "MobilityData / GTFS community", "https://gtfs.org/documentation/overview/", ["transit", "schedule", "realtime", "identity"], "official_specification"),
    ("ev.dcat", "Data Catalog Vocabulary 3", "W3C", "https://www.w3.org/TR/vocab-dcat-3/", ["public_data", "catalog", "versions", "distributions"], "normative_standard"),
    ("ev.sdmx", "SDMX 3.1 specifications", "SDMX Sponsors", "https://docs.sdmx.org/en/3.1.0/", ["statistics", "multidimensional", "structure", "versions"], "normative_standard"),
    ("ev.activitystreams", "Activity Streams 2.0", "W3C", "https://www.w3.org/TR/activitystreams-core/", ["collaboration", "activities", "paging", "schema"], "normative_standard"),
    ("ev.imap", "RFC 9051 IMAP4rev2", "IETF", "https://www.rfc-editor.org/rfc/rfc9051.html", ["email", "identity", "flags", "ordering"], "normative_standard"),
    ("ev.caldav", "RFC 4791 CalDAV", "IETF", "https://www.rfc-editor.org/rfc/rfc4791.html", ["calendar", "sync", "time", "security"], "normative_standard"),
    ("ev.git", "Git protocol and pack-format documentation", "Git Project", "https://git-scm.com/docs/protocol-v2", ["source_code", "version_graph", "transport", "integrity"], "official_specification"),
    ("ev.spdx", "SPDX Specification 3.0.1", "Linux Foundation SPDX Project", "https://spdx.github.io/spdx-spec/", ["software_supply_chain", "packages", "provenance"], "normative_standard"),
    ("ev.cyclonedx", "CycloneDX specification 1.7", "OWASP Foundation / Ecma International", "https://cyclonedx.org/specification/overview/", ["software_supply_chain", "bom", "schema", "signatures"], "normative_standard"),
    ("ev.otel", "OpenTelemetry Specification", "Cloud Native Computing Foundation", "https://opentelemetry.io/docs/specs/otel/", ["logs", "metrics", "traces", "schema", "time"], "official_specification"),
    ("ev.tracecontext", "Trace Context", "W3C", "https://www.w3.org/TR/trace-context/", ["traces", "identity", "security"], "normative_standard"),
    ("ev.scim", "RFC 7644 SCIM Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc7644.html", ["identity", "api", "paging", "security"], "normative_standard"),
    ("ev.stix_taxii", "STIX and TAXII 2.1", "OASIS Open", "https://docs.oasis-open.org/cti/taxii/v2.1/os/taxii-v2.1-os.html", ["threat_intelligence", "versions", "paging", "security"], "normative_standard"),
    ("ev.webauthn", "Web Authentication Level 3", "W3C", "https://www.w3.org/TR/webauthn-3/", ["identity", "credentials", "security"], "normative_standard"),
    ("ev.openid_connect", "OpenID Connect Core 1.0", "OpenID Foundation", "https://openid.net/specs/openid-connect-core-1_0.html", ["identity", "tokens", "security"], "normative_standard"),
    ("ev.buildingsmart", "Industry Foundation Classes 4.3", "buildingSMART International", "https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/", ["bim", "assets", "geometry", "versions"], "normative_standard"),
    ("ev.edifact", "UN/EDIFACT standards directory", "UNECE", "https://unece.org/trade/uncefact/unedifact", ["edi", "messages", "versions"], "standards_body_primary_catalogue"),
]


BASE = {
    "authority": {"role": "composite_requires_field_authority", "field_level_override_required": True, "replica_may_lag": True},
    "object_model": {"object_kinds": ["records"], "logical_models": ["document"], "payload_shapes": ["nested_records"], "identity_scope": "occurrence_namespace", "identity_reuse_must_be_probed": True},
    "interfaces": {"discovery_modes": ["manual_inventory"], "read_modes": ["snapshot"], "write_modes": ["none"], "change_modes": ["none"], "access_topologies": ["private_network"]},
    "schema": {"mode": "mixed_per_object", "compatibility_policy": "provider_defined", "registry_or_contract": "deployment_required", "unknown_field_policy": "fail_closed", "key_and_constraint_discovery_required": True, "drift_observable": "must_probe"},
    "temporality": {"time_axes": ["recorded_system_time"], "clock_model": "server_clock", "timezone_and_calendar_required": True, "watermark_or_cursor": "none", "late_data": "not_intrinsic", "retention": "deployment_specific"},
    "order_finality": {"ordering_scope": "service_defined", "ordering_key": "must_probe", "gap_signal": "must_probe", "duplicate_semantics": "must_probe", "finality_model": "mutable_current_state", "corrections": "overwrite_or_revision_must_probe", "deletion_semantics": ["not_exposed"]},
    "transactions": {"boundary": "provider_defined", "consistency_model": "provider_defined", "snapshot_cut": "must_probe", "cross_object_atomicity": "must_probe"},
    "security": {"authentication": ["deployment_specific"], "authorization": ["object_or_field_scope_must_probe"], "encryption": ["in_transit_required", "at_rest_must_probe"], "tenant_boundary": "must_probe", "auditability": "must_probe", "sensitivity_default": "deployment_specific", "write_or_command_default": "deny"},
    "limits": {"class_values_are_portable": False, "must_probe": ["rate", "quota", "page_size", "payload_size", "object_size", "concurrency", "retention", "cursor_ttl", "query_timeout", "extract_cost", "egress", "license"], "hard_limit_behavior": "typed_failure_required"},
    "hazards": ["authority ambiguity", "silent schema drift", "partial extraction", "undocumented retention", "least-privilege mismatch"],
    "verification": ["verify.identity.authority", "verify.discovery.capability_probe", "verify.schema.compatibility", "verify.security.least_privilege", "verify.limit.envelope", "verify.reconcile.count_hash"],
}


PROFILES = {}


def profile(name: str, **patches: dict) -> None:
    value = copy.deepcopy(BASE)
    for section, patch in patches.items():
        value[section].update(patch)
    PROFILES[name] = value


profile("transactional_store",
    authority={"role": "system_of_record", "field_level_override_required": False, "replica_may_lag": True},
    object_model={"object_kinds": ["namespaces", "tables_or_collections", "records"], "logical_models": ["relational"], "payload_shapes": ["rows"]},
    interfaces={"discovery_modes": ["namespace_list", "schema_introspection"], "read_modes": ["point_get", "query", "scan", "snapshot", "incremental_cursor"], "write_modes": ["insert", "upsert", "delete", "transaction", "bulk_load"], "change_modes": ["transaction_log", "change_stream"], "access_topologies": ["private_network"]},
    schema={"mode": "declared_evolving", "compatibility_policy": "provider_defined"},
    temporality={"time_axes": ["transaction_commit_time", "recorded_system_time"], "clock_model": "transaction_clock", "watermark_or_cursor": "log_position_or_commit_token"},
    order_finality={"ordering_scope": "per_transaction", "ordering_key": "commit_position", "gap_signal": "position_discontinuity", "duplicate_semantics": "resume_overlap_possible", "finality_model": "commit_final", "deletion_semantics": ["hard_delete", "soft_delete", "tombstone"]},
    transactions={"boundary": "database_transaction", "consistency_model": "strong", "snapshot_cut": "transaction_snapshot_or_exported_snapshot", "cross_object_atomicity": "within_transaction"})
PROFILES["transactional_store"]["verification"] = BASE["verification"] + ["verify.read.repeatable_snapshot", "verify.change.snapshot_handoff", "verify.change.resume_expiry", "verify.delete.all_forms", "verify.transaction.atomicity"]

profile("distributed_mutable_store",
    authority={"role": "system_of_record", "field_level_override_required": False, "replica_may_lag": True},
    object_model={"object_kinds": ["namespaces", "collections", "records"], "logical_models": ["document"], "payload_shapes": ["nested_records"]},
    interfaces={"discovery_modes": ["namespace_list", "schema_introspection"], "read_modes": ["point_get", "query", "scan", "snapshot", "incremental_cursor"], "write_modes": ["insert", "upsert", "delete"], "change_modes": ["change_stream", "poll_diff"], "access_topologies": ["private_network", "public_internet"]},
    schema={"mode": "declared_evolving", "compatibility_policy": "provider_defined"},
    temporality={"time_axes": ["recorded_system_time", "transaction_commit_time"], "clock_model": "multiple_unreconciled", "watermark_or_cursor": "opaque_resume_token"},
    order_finality={"ordering_scope": "per_partition", "ordering_key": "partition_and_token", "gap_signal": "token_expiry_or_invalidation", "duplicate_semantics": "at_least_once_change_delivery", "finality_model": "majority_or_quorum_final", "deletion_semantics": ["hard_delete", "soft_delete", "tombstone", "expiry_ttl"]},
    transactions={"boundary": "single_partition", "consistency_model": "quorum_tunable", "snapshot_cut": "capability_dependent", "cross_object_atomicity": "not_portable"})
PROFILES["distributed_mutable_store"]["verification"] = BASE["verification"] + ["verify.change.snapshot_handoff", "verify.change.resume_expiry", "verify.delivery.duplicates", "verify.delivery.order_gaps", "verify.delete.all_forms", "verify.transaction.atomicity"]

profile("snapshot_repository",
    authority={"role": "derived_replica", "field_level_override_required": True, "replica_may_lag": True},
    object_model={"object_kinds": ["catalogs", "datasets", "tables", "snapshots"], "logical_models": ["relational", "multidimensional_cube"], "payload_shapes": ["rows", "facts_dimensions"]},
    interfaces={"discovery_modes": ["catalog", "schema_introspection"], "read_modes": ["query", "scan", "snapshot", "incremental_cursor", "federated_query"], "write_modes": ["append", "upsert", "replace", "delete", "bulk_load"], "change_modes": ["poll_diff", "revision_feed", "change_stream"], "access_topologies": ["private_network", "public_internet", "federated"]},
    schema={"mode": "declared_evolving", "compatibility_policy": "provider_defined"},
    temporality={"time_axes": ["recorded_system_time", "revision_publication_time", "ingestion_time"], "clock_model": "server_clock", "watermark_or_cursor": "snapshot_or_job_watermark"},
    order_finality={"ordering_scope": "none", "ordering_key": "not_intrinsic", "gap_signal": "reconciliation", "duplicate_semantics": "load_defined", "finality_model": "publication_revision", "deletion_semantics": ["hard_delete", "soft_delete", "superseded_revision"]},
    transactions={"boundary": "provider_defined", "consistency_model": "immutable_snapshot", "snapshot_cut": "named_snapshot_or_query_snapshot", "cross_object_atomicity": "capability_dependent"})
PROFILES["snapshot_repository"]["verification"] = BASE["verification"] + ["verify.read.repeatable_snapshot", "verify.change.resume_expiry", "verify.finality.correction_retraction", "verify.delete.all_forms"]

profile("file_or_object",
    authority={"role": "authoritative_publication", "field_level_override_required": True, "replica_may_lag": False},
    object_model={"object_kinds": ["directories_or_buckets", "files_or_objects", "versions"], "logical_models": ["object_blob"], "payload_shapes": ["files", "objects"]},
    interfaces={"discovery_modes": ["directory_walk", "manifest"], "read_modes": ["range_read", "snapshot", "file_arrival"], "write_modes": ["file_put", "replace", "delete"], "change_modes": ["file_arrival", "poll_diff"], "access_topologies": ["local_network", "public_internet", "managed_file_exchange"]},
    schema={"mode": "schema_on_read", "compatibility_policy": "none"},
    temporality={"time_axes": ["revision_publication_time", "recorded_system_time"], "clock_model": "file_metadata_clock", "watermark_or_cursor": "object_version_or_manifest"},
    order_finality={"ordering_scope": "file_byte_order", "ordering_key": "path_key_version", "gap_signal": "manifest_or_listing_reconciliation", "duplicate_semantics": "same_name_or_digest", "finality_model": "publication_revision", "deletion_semantics": ["hard_delete", "superseded_revision", "expiry_ttl"]},
    transactions={"boundary": "object_put", "consistency_model": "immutable_snapshot", "snapshot_cut": "versioned_manifest_or_inventory", "cross_object_atomicity": "not_portable"})
PROFILES["file_or_object"]["verification"] = BASE["verification"] + ["verify.read.repeatable_snapshot", "verify.change.resume_expiry", "verify.delivery.duplicates", "verify.schema.compatibility", "verify.delete.all_forms"]

profile("versioned_content",
    authority={"role": "human_workflow_record", "field_level_override_required": True, "replica_may_lag": True},
    object_model={"object_kinds": ["spaces", "folders", "documents", "versions", "renditions", "acl_entries"], "logical_models": ["content_tree", "activity_graph", "object_blob"], "payload_shapes": ["content_versions", "files", "events"]},
    interfaces={"discovery_modes": ["catalog", "directory_walk", "schema_introspection"], "read_modes": ["query", "snapshot", "incremental_cursor", "range_read"], "write_modes": ["human_edit", "file_put", "replace", "delete"], "change_modes": ["revision_feed", "webhook", "poll_diff"], "access_topologies": ["private_network", "public_internet"]},
    schema={"mode": "mixed_per_object", "compatibility_policy": "provider_defined"},
    temporality={"time_axes": ["effective_valid_time", "recorded_system_time", "revision_publication_time"], "clock_model": "human_entered", "watermark_or_cursor": "revision_or_delta_token"},
    order_finality={"ordering_scope": "document_revision", "ordering_key": "document_id_revision", "gap_signal": "revision_gap_or_deleted_history", "duplicate_semantics": "same_revision_or_delivery_retry", "finality_model": "workflow_approved", "deletion_semantics": ["soft_delete", "redaction", "legal_hold", "superseded_revision"]},
    transactions={"boundary": "document_revision", "consistency_model": "human_workflow", "snapshot_cut": "revision_cut_must_probe", "cross_object_atomicity": "not_portable"},
    security={"sensitivity_default": "highly_sensitive_personal"})
PROFILES["versioned_content"]["verification"] = BASE["verification"] + ["verify.change.resume_expiry", "verify.delete.all_forms", "verify.finality.correction_retraction", "verify.security.tenant_boundary", "verify.content.version_acl"]

profile("remote_api",
    authority={"role": "operational_projection", "field_level_override_required": True, "replica_may_lag": True},
    object_model={"object_kinds": ["resources", "operations", "representations"], "logical_models": ["hierarchical_message"], "payload_shapes": ["nested_records"]},
    interfaces={"discovery_modes": ["capability_document", "service_description", "manual_inventory"], "read_modes": ["point_get", "query", "page_cursor", "poll"], "write_modes": ["insert", "upsert", "replace", "delete", "command"], "change_modes": ["poll_diff", "webhook", "revision_feed"], "access_topologies": ["public_internet", "private_network"]},
    schema={"mode": "declared_evolving", "compatibility_policy": "profile_negotiated"},
    temporality={"time_axes": ["recorded_system_time", "effective_valid_time"], "clock_model": "server_clock", "watermark_or_cursor": "opaque_page_or_delta_token"},
    order_finality={"ordering_scope": "service_defined", "ordering_key": "server_sort_plus_tie_breaker_required", "gap_signal": "cursor_expiry_or_reconciliation", "duplicate_semantics": "retry_and_pagination_overlap", "finality_model": "mutable_current_state", "deletion_semantics": ["hard_delete", "soft_delete", "not_exposed"]},
    transactions={"boundary": "single_record", "consistency_model": "provider_defined", "snapshot_cut": "conditional_request_or_server_token", "cross_object_atomicity": "not_portable"})
PROFILES["remote_api"]["verification"] = BASE["verification"] + ["verify.read.pagination_mutation", "verify.change.resume_expiry", "verify.delivery.duplicates", "verify.delete.all_forms", "verify.security.audit_rotation"]

profile("event_channel",
    authority={"role": "transport_channel", "field_level_override_required": True, "replica_may_lag": False},
    object_model={"object_kinds": ["brokers", "topics_or_queues", "partitions", "messages"], "logical_models": ["append_log", "work_queue"], "payload_shapes": ["events", "messages"]},
    interfaces={"discovery_modes": ["topic_list", "schema_introspection"], "read_modes": ["subscription", "stream"], "write_modes": ["publish", "acknowledge"], "change_modes": ["queue_delivery", "event_log"], "access_topologies": ["private_network", "public_internet", "device_gateway"]},
    schema={"mode": "registry_governed", "compatibility_policy": "provider_defined"},
    temporality={"time_axes": ["event_time", "recorded_system_time", "ingestion_time"], "clock_model": "event_producer_clock", "watermark_or_cursor": "offset_sequence_or_delivery_tag"},
    order_finality={"ordering_scope": "per_partition", "ordering_key": "partition_offset_or_delivery_sequence", "gap_signal": "offset_discontinuity_or_retention", "duplicate_semantics": "delivery_contract_must_be_declared", "finality_model": "never_intrinsically_final", "deletion_semantics": ["expiry_ttl", "compaction_loss", "tombstone"]},
    transactions={"boundary": "message_delivery", "consistency_model": "transport_defined", "snapshot_cut": "not_intrinsic", "cross_object_atomicity": "not_portable"})
PROFILES["event_channel"]["verification"] = BASE["verification"] + ["verify.change.resume_expiry", "verify.delivery.duplicates", "verify.delivery.order_gaps", "verify.delivery.replay_retention", "verify.schema.compatibility", "verify.time.clock_and_lateness"]

profile("business_workflow",
    authority={"role": "human_workflow_record", "field_level_override_required": True, "replica_may_lag": True},
    object_model={"object_kinds": ["tenants", "business_objects", "documents", "workflow_states", "audit_entries"], "logical_models": ["relational", "document", "workflow_case"], "payload_shapes": ["rows", "nested_records", "cases_tasks", "events"]},
    interfaces={"discovery_modes": ["catalog", "schema_introspection", "capability_document"], "read_modes": ["query", "snapshot", "page_cursor", "incremental_cursor", "manual_export"], "write_modes": ["upsert", "command", "bulk_load", "human_edit"], "change_modes": ["webhook", "poll_diff", "revision_feed"], "access_topologies": ["public_internet", "private_network", "human_mediated"]},
    schema={"mode": "declared_evolving", "compatibility_policy": "provider_defined"},
    temporality={"time_axes": ["event_time", "effective_valid_time", "recorded_system_time", "revision_publication_time"], "clock_model": "human_entered", "watermark_or_cursor": "modified_time_plus_tie_breaker_or_delta_token"},
    order_finality={"ordering_scope": "service_defined", "ordering_key": "business_key_and_revision", "gap_signal": "audit_or_reconciliation", "duplicate_semantics": "workflow_retry_or_reopen", "finality_model": "workflow_approved", "deletion_semantics": ["soft_delete", "redaction", "legal_hold", "not_exposed"]},
    transactions={"boundary": "business_workflow", "consistency_model": "human_workflow", "snapshot_cut": "export_or_api_capability_dependent", "cross_object_atomicity": "business_transaction_not_storage_transaction"},
    security={"sensitivity_default": "personal"})
PROFILES["business_workflow"]["verification"] = BASE["verification"] + ["verify.read.pagination_mutation", "verify.change.resume_expiry", "verify.finality.correction_retraction", "verify.delete.all_forms", "verify.security.tenant_boundary", "verify.security.audit_rotation", "verify.vertical.conformance"]

profile("telemetry_stream",
    authority={"role": "observation_recorder", "field_level_override_required": False, "replica_may_lag": True},
    object_model={"object_kinds": ["resources", "instruments_or_emitters", "streams", "observations"], "logical_models": ["time_series", "append_log", "trace_graph"], "payload_shapes": ["series_samples", "events"]},
    interfaces={"discovery_modes": ["catalog", "schema_introspection"], "read_modes": ["query", "range_read", "stream", "subscription"], "write_modes": ["append", "publish"], "change_modes": ["event_log", "subscription"], "access_topologies": ["private_network", "public_internet"]},
    schema={"mode": "declared_evolving", "compatibility_policy": "backward"},
    temporality={"time_axes": ["event_time", "observation_time", "recorded_system_time", "ingestion_time"], "clock_model": "event_producer_clock", "watermark_or_cursor": "time_plus_stream_cursor"},
    order_finality={"ordering_scope": "per_key", "ordering_key": "resource_stream_sequence_or_time", "gap_signal": "sequence_gap_or_expected_interval", "duplicate_semantics": "retransmit_or_export_overlap", "finality_model": "windowed_late", "deletion_semantics": ["expiry_ttl", "compaction_loss"]},
    transactions={"boundary": "single_record", "consistency_model": "eventual", "snapshot_cut": "query_time_range_not_global_cut", "cross_object_atomicity": "none"})
PROFILES["telemetry_stream"]["verification"] = BASE["verification"] + ["verify.delivery.duplicates", "verify.delivery.order_gaps", "verify.delivery.replay_retention", "verify.time.clock_and_lateness", "verify.schema.compatibility"]

profile("device_or_control",
    authority={"role": "device_state", "field_level_override_required": True, "replica_may_lag": True},
    object_model={"object_kinds": ["sites", "devices", "tags_or_points", "alarms", "commands"], "logical_models": ["digital_twin", "signal", "time_series"], "payload_shapes": ["signals_waveforms", "series_samples", "events", "commands"]},
    interfaces={"discovery_modes": ["device_browse", "manual_inventory"], "read_modes": ["device_read", "poll", "subscription", "stream"], "write_modes": ["command"], "change_modes": ["device_notification", "subscription"], "access_topologies": ["device_gateway", "field_bus", "air_gapped"]},
    schema={"mode": "profile_governed", "compatibility_policy": "exact_version"},
    temporality={"time_axes": ["event_time", "observation_time", "recorded_system_time"], "clock_model": "device_clock", "watermark_or_cursor": "device_sequence_or_none"},
    order_finality={"ordering_scope": "per_key", "ordering_key": "device_tag_sequence", "gap_signal": "quality_code_sequence_or_heartbeat", "duplicate_semantics": "network_and_qos_dependent", "finality_model": "device_best_effort", "deletion_semantics": ["not_exposed", "expiry_ttl"]},
    transactions={"boundary": "device_command", "consistency_model": "device_best_effort", "snapshot_cut": "not_intrinsic", "cross_object_atomicity": "none"},
    security={"sensitivity_default": "safety_critical", "write_or_command_default": "deny_and_separate_control_plane"})
PROFILES["device_or_control"]["verification"] = BASE["verification"] + ["verify.delivery.duplicates", "verify.delivery.order_gaps", "verify.time.clock_and_lateness", "verify.write.destructive_guard", "verify.offline.reconnect", "verify.security.audit_rotation"]

profile("scientific_asset",
    authority={"role": "observation_recorder", "field_level_override_required": True, "replica_may_lag": False},
    object_model={"object_kinds": ["projects", "experiments", "samples", "runs", "instruments", "datasets", "artifacts"], "logical_models": ["multidimensional_array", "signal", "tensor"], "payload_shapes": ["arrays_chunks", "signals_waveforms", "files"]},
    interfaces={"discovery_modes": ["catalog", "manifest", "directory_walk"], "read_modes": ["snapshot", "range_read", "file_arrival", "query"], "write_modes": ["file_put", "append", "command"], "change_modes": ["file_arrival", "revision_feed"], "access_topologies": ["local_network", "private_network", "air_gapped"]},
    schema={"mode": "declared", "compatibility_policy": "exact_version"},
    temporality={"time_axes": ["event_time", "observation_time", "recorded_system_time", "revision_publication_time"], "clock_model": "device_clock", "watermark_or_cursor": "run_id_and_artifact_digest"},
    order_finality={"ordering_scope": "source_sequence", "ordering_key": "run_sample_index", "gap_signal": "run_manifest_or_sequence", "duplicate_semantics": "rerun_or_export_copy", "finality_model": "publication_revision", "deletion_semantics": ["superseded_revision", "redaction", "legal_hold"]},
    transactions={"boundary": "file_replace", "consistency_model": "immutable_snapshot", "snapshot_cut": "run_or_dataset_version", "cross_object_atomicity": "manifest_defined"},
    security={"sensitivity_default": "deployment_specific"})
PROFILES["scientific_asset"]["verification"] = BASE["verification"] + ["verify.read.repeatable_snapshot", "verify.schema.compatibility", "verify.time.clock_and_lateness", "verify.finality.correction_retraction", "verify.media.codec_metadata", "verify.vertical.conformance"]

profile("regulated_record",
    authority={"role": "system_of_record", "field_level_override_required": True, "replica_may_lag": True},
    object_model={"object_kinds": ["regulated_entities", "cases_or_accounts", "transactions_or_events", "documents", "audit_entries"], "logical_models": ["workflow_case", "ledger", "document"], "payload_shapes": ["nested_records", "facts_dimensions", "events", "content_versions"]},
    interfaces={"discovery_modes": ["capability_document", "schema_introspection", "manual_inventory"], "read_modes": ["query", "snapshot", "incremental_cursor", "manual_export"], "write_modes": ["command", "bulk_load", "human_edit"], "change_modes": ["revision_feed", "poll_diff", "webhook"], "access_topologies": ["private_network", "partner_network", "managed_file_exchange", "human_mediated"]},
    schema={"mode": "profile_governed", "compatibility_policy": "exact_version"},
    temporality={"time_axes": ["event_time", "effective_valid_time", "recorded_system_time", "revision_publication_time"], "clock_model": "multiple_unreconciled", "watermark_or_cursor": "filing_case_transaction_or_revision_token"},
    order_finality={"ordering_scope": "per_transaction", "ordering_key": "regulated_identifier_and_revision", "gap_signal": "control_total_or_sequence", "duplicate_semantics": "resubmission_or_amendment", "finality_model": "provisional_then_corrected", "deletion_semantics": ["redaction", "legal_hold", "superseded_revision", "not_exposed"]},
    transactions={"boundary": "business_workflow", "consistency_model": "human_workflow", "snapshot_cut": "regulated_reporting_cut_or_export", "cross_object_atomicity": "domain_defined"},
    security={"sensitivity_default": "highly_sensitive_personal"})
PROFILES["regulated_record"]["verification"] = BASE["verification"] + ["verify.read.repeatable_snapshot", "verify.finality.correction_retraction", "verify.delete.all_forms", "verify.security.tenant_boundary", "verify.security.audit_rotation", "verify.reconcile.count_hash", "verify.vertical.conformance"]

profile("legacy_batch",
    authority={"role": "system_of_record", "field_level_override_required": True, "replica_may_lag": False},
    object_model={"object_kinds": ["datasets", "members", "records", "reports", "jobs"], "logical_models": ["fixed_record", "object_blob"], "payload_shapes": ["opaque_records", "files"]},
    interfaces={"discovery_modes": ["manual_inventory", "manifest"], "read_modes": ["snapshot", "file_arrival", "manual_export"], "write_modes": ["bulk_load", "file_put", "command"], "change_modes": ["file_arrival", "manual_reexport"], "access_topologies": ["managed_file_exchange", "air_gapped", "human_mediated"]},
    schema={"mode": "fixed", "compatibility_policy": "exact_version"},
    temporality={"time_axes": ["recorded_system_time", "processing_time"], "clock_model": "file_metadata_clock", "watermark_or_cursor": "job_cycle_and_record_position"},
    order_finality={"ordering_scope": "file_byte_order", "ordering_key": "dataset_generation_record_position", "gap_signal": "record_count_control_total", "duplicate_semantics": "rerun_or_retransmit", "finality_model": "publication_revision", "deletion_semantics": ["not_exposed", "superseded_revision"]},
    transactions={"boundary": "file_replace", "consistency_model": "immutable_snapshot", "snapshot_cut": "batch_generation", "cross_object_atomicity": "job_defined"},
    security={"sensitivity_default": "deployment_specific"})
PROFILES["legacy_batch"]["verification"] = BASE["verification"] + ["verify.delivery.duplicates", "verify.delivery.order_gaps", "verify.schema.compatibility", "verify.reconcile.count_hash", "verify.offline.reconnect"]


# family, id suffix, name, profile, logical models, payload shapes, evidence refs, hazards, inherited refs
SEEDS = []


def seed(family: str, suffix: str, name: str, profile_id: str, models: list[str], shapes: list[str], evidence: list[str], hazards: list[str], inherited: list[str] | None = None) -> None:
    SEEDS.append((family, suffix, name, profile_id, models, shapes, evidence, hazards, inherited or []))


def many(family: str, profile_id: str, rows: list[tuple]) -> None:
    for row in rows:
        seed(family, row[0], row[1], profile_id, *row[2:])


# Operational databases: data model and guarantees distinguish classes; vendors are occurrences.
many("operational_database", "transactional_store", [
    ("relational_transactional", "Transactional relational database", ["relational"], ["rows"], ["ev.postgresql.mvcc"], ["replica lag", "long-running snapshot pressure", "DDL during capture", "transaction-log retention"], ["source.relational_oltp"]),
    ("distributed_relational", "Distributed relational database", ["relational"], ["rows"], ["ev.postgresql.mvcc", "ev.cassandra.architecture"], ["cross-shard transaction variance", "follower lag", "clock uncertainty", "topology movement"]),
    ("embedded_relational", "Embedded relational database", ["relational"], ["rows"], ["ev.sqlite.isolation"], ["single-writer contention", "WAL sidecar omission", "file-copy inconsistency", "device loss"]),
    ("spatial_relational", "Spatial relational database", ["relational", "spatial_feature"], ["rows", "geometries_tiles"], ["ev.postgresql.mvcc", "ev.geopackage"], ["CRS mismatch", "invalid geometry", "topology loss", "spatial-index assumptions"], ["source.spatial_database"]),
])
many("operational_database", "distributed_mutable_store", [
    ("document", "Document database", ["document"], ["nested_records"], ["ev.mongodb.change"], ["shape drift", "nested fanout", "resume-token expiry", "majority-vs-local visibility"], ["source.document_database"]),
    ("key_value", "Key-value database", ["key_value"], ["keyed_values"], ["ev.cassandra.architecture"], ["opaque values", "TTL deletion", "hot keys", "scan limitations"], ["source.key_value_store"]),
    ("wide_column", "Wide-column database", ["wide_column"], ["rows", "keyed_values"], ["ev.cassandra.architecture"], ["partition-key dependence", "tombstones", "compaction", "tunable-consistency mismatch"], ["source.wide_column_store"]),
    ("property_graph", "Property-graph database", ["property_graph"], ["edges_nodes"], ["ev.neo4j.transactions"], ["node identity mismatch", "edge multiplicity", "traversal explosion", "causal bookmark loss"], ["source.graph_database"]),
    ("rdf_triplestore", "RDF triple/quad store", ["rdf_graph"], ["triples_quads"], ["ev.dcat"], ["blank-node instability", "named-graph authority", "entailment variance", "federation partiality"]),
    ("search_index", "Search and inverted-index store", ["search_index", "document"], ["documents_terms", "nested_records"], ["ev.otel"], ["index is projection not authority", "refresh lag", "unstable deep paging", "mapping conflict"], ["source.search_index"]),
    ("time_series", "Time-series database", ["time_series"], ["series_samples"], ["ev.otel"], ["late samples", "downsampling loss", "retention expiry", "tag cardinality"], ["source.time_series_database"]),
    ("vector_similarity_index", "Vector similarity index", ["vector_index"], ["vectors_metadata"], ["ev.parquet.format"], ["embedding/version mismatch", "approximate-recall variance", "metadata filter drift", "index rebuild lag"]),
    ("multi_model", "Multi-model operational database", ["relational", "document", "property_graph", "key_value"], ["rows", "nested_records", "edges_nodes", "keyed_values"], ["ev.postgresql.mvcc", "ev.neo4j.transactions"], ["model-specific guarantees", "cross-model atomicity variance", "identity collision", "query-language mismatch"]),
    ("in_memory_cache", "Mutable in-memory cache", ["key_value"], ["keyed_values"], ["ev.cassandra.architecture"], ["eviction", "TTL expiry", "cache is not authority", "restart loss"]),
])

many("analytical_repository", "snapshot_repository", [
    ("cloud_data_warehouse", "Analytical data warehouse", ["relational", "multidimensional_cube"], ["rows", "facts_dimensions"], ["ev.postgresql.mvcc", "ev.sdmx"], ["mixed grain", "materialization staleness", "query concurrency", "compute cost"], ["source.data_warehouse"]),
    ("lake_table", "Transactional lake table", ["relational", "object_blob"], ["rows", "files"], ["ev.parquet.format", "ev.avro.spec"], ["snapshot expiry", "small files", "partition drift", "reader compatibility"], ["source.lake_table"]),
    ("raw_data_lake", "Raw data lake zone", ["object_blob"], ["files", "objects"], ["ev.s3.multipart", "ev.dcat"], ["unknown semantics", "duplicate landing", "mutable keys", "lifecycle deletion"]),
    ("olap_cube", "Multidimensional OLAP cube", ["multidimensional_cube"], ["facts_dimensions"], ["ev.sdmx"], ["preaggregation loss", "dimension processing lag", "calculation semantics", "member-key drift"], ["source.olap_cube"]),
    ("semantic_metric_store", "Published semantic and metric store", ["multidimensional_cube", "registry"], ["facts_dimensions"], ["ev.sdmx", "ev.xbrl"], ["definition version mismatch", "grain ambiguity", "cache staleness", "security context changes"], ["source.metrics_store"]),
    ("federated_query_catalog", "Federated query and external-table catalog", ["relational", "registry"], ["rows"], ["ev.dcat", "ev.openapi"], ["partial results", "source pushdown variance", "cross-source cut impossibility", "credential fanout"]),
    ("feature_repository", "Governed statistical feature repository", ["relational", "time_series"], ["rows", "series_samples"], ["ev.parquet.format"], ["online/offline skew", "point-in-time leakage", "feature definition drift", "TTL expiry"]),
    ("array_database", "Multidimensional array database", ["multidimensional_array"], ["arrays_chunks"], ["ev.netcdf", "ev.hdf5"], ["chunk-layout cost", "dimension convention mismatch", "fill-value ambiguity", "coordinate drift"]),
    ("query_result_cache", "Analytical query-result cache", ["relational", "key_value"], ["rows", "keyed_values"], ["ev.postgresql.mvcc"], ["stale result", "security-context leakage", "parameter collision", "eviction"]),
])

many("file_object_content", "file_or_object", [
    ("local_or_network_filesystem", "Local or network filesystem", ["object_blob"], ["files"], ["ev.posix.files"], ["partial write", "rename semantics", "path identity", "permission inheritance"], ["source.local_filesystem"]),
    ("object_storage", "Object storage", ["object_blob"], ["objects"], ["ev.s3.multipart"], ["incomplete multipart upload", "versioning disabled", "listing pagination", "lifecycle expiry"], ["source.object_storage"]),
    ("delimited_text_file", "Delimited text file", ["tabular_record"], ["rows", "files"], ["ev.rfc4180.csv"], ["delimiter/quote ambiguity", "locale parsing", "header drift", "duplicate delivery"], ["source.tabular_file"]),
    ("fixed_width_record_file", "Fixed-width record file", ["fixed_record"], ["opaque_records", "files"], ["ev.edifact"], ["copybook mismatch", "encoding", "record-version mixing", "truncation"]),
    ("self_describing_row_file", "Self-describing row-oriented record file", ["object_blob", "document"], ["files", "nested_records"], ["ev.avro.spec"], ["reader/writer schema mismatch", "union ambiguity", "codec support", "block corruption"]),
    ("columnar_analytical_file", "Columnar analytical file", ["object_blob", "relational"], ["files", "rows"], ["ev.parquet.format"], ["logical-type mismatch", "statistics leakage/staleness", "nested reconstruction", "encryption-key availability"], ["source.columnar_file"]),
    ("spreadsheet_workbook", "Spreadsheet workbook", ["tabular_record"], ["pages_cells_formulas"], ["ev.opendocument"], ["formula recalculation", "hidden ranges", "merged cells", "mixed types", "human overwrite"], ["source.spreadsheet"]),
    ("xml_json_document_file", "Structured XML or JSON document file", ["document"], ["nested_records", "files"], ["ev.openapi", "ev.avro.spec"], ["namespace/context drift", "number precision", "duplicate keys", "entity expansion"]),
    ("archive_or_package", "Archive or package container", ["object_blob", "content_tree"], ["files", "packages_artifacts"], ["ev.spdx", "ev.cyclonedx"], ["path traversal", "nested compression bomb", "missing manifest", "signature scope"]),
    ("binary_proprietary_file", "Opaque or proprietary binary file", ["object_blob"], ["opaque_records", "files"], ["ev.hdf5"], ["format/version opacity", "decoder availability", "endianness", "silent truncation"]),
    ("managed_file_transfer", "Managed file-transfer landing area", ["object_blob"], ["files"], ["ev.edifact", "ev.posix.files"], ["partial arrival", "duplicate retransmit", "late/missing batch", "encryption-key rotation"]),
])
many("file_object_content", "versioned_content", [
    ("enterprise_content_repository", "Enterprise content-management repository", ["content_tree", "object_blob"], ["content_versions", "files"], ["ev.cmis"], ["ACL inheritance", "rendition vs original", "legal hold", "version-series identity"], ["source.document_content"]),
    ("records_archive", "Records-management and legal archive", ["content_tree", "registry"], ["content_versions"], ["ev.cmis"], ["retention schedule", "legal hold", "disposition authority", "redacted revisions"]),
    ("shared_document_workspace", "Shared document workspace", ["content_tree", "activity_graph"], ["content_versions", "events"], ["ev.cmis", "ev.webdav"], ["concurrent edits", "link sharing", "deleted history", "guest access"]),
])

many("api_remote_service", "remote_api", [
    ("http_resource_api", "HTTP resource API", ["document"], ["nested_records"], ["ev.http9110", "ev.openapi"], ["retry safety", "rate limits", "pagination race", "partial response"], ["source.rest_api"]),
    ("graphql_query_api", "GraphQL query API", ["property_graph", "document"], ["nested_records", "edges_nodes"], ["ev.graphql"], ["partial data with errors", "nested fanout", "query cost", "field deprecation"], ["source.graphql_api"]),
    ("odata_data_service", "OData data service", ["relational", "document"], ["rows", "nested_records"], ["ev.odata"], ["delta-token expiry", "server paging", "capability variance", "metadata version"], ["source.odata_service"]),
    ("soap_web_service", "SOAP web service", ["hierarchical_message"], ["nested_records"], ["ev.http9110", "ev.openapi"], ["WSDL/XSD versioning", "namespace complexity", "fault mapping", "WS-Security profile variance"], ["source.soap_api"]),
    ("binary_rpc_service", "Binary RPC service", ["binary_message"], ["messages"], ["ev.grpc"], ["deadline expiry", "partial stream", "schema compatibility", "retry non-idempotence"], ["source.rpc_service"]),
    ("webdav_content_api", "WebDAV content service", ["content_tree", "object_blob"], ["content_versions", "files"], ["ev.webdav"], ["lock timeout", "property namespace", "conditional write failure", "depth traversal"]),
    ("bulk_export_api", "Asynchronous bulk-export API", ["object_blob", "document"], ["files", "nested_records"], ["ev.http9110", "ev.fhir"], ["job expiration", "partial export", "cut ambiguity", "signed URL expiry"]),
    ("screen_or_report_export", "Human-mediated report/export surface", ["tabular_record", "object_blob"], ["files", "rows"], ["ev.opendocument"], ["undocumented filters", "locale/formatting", "manual truncation", "no stable cursor"]),
    ("remote_query_endpoint", "Remote query endpoint", ["relational", "rdf_graph"], ["rows", "triples_quads"], ["ev.dcat", "ev.http9110"], ["query timeout", "partial federation", "result limits", "inference variance"]),
])

many("event_messaging_cdc", "event_channel", [
    ("partitioned_append_log", "Partitioned durable append log", ["append_log"], ["events", "messages"], ["ev.kafka.design"], ["partition-local order only", "retention expiry", "rebalance duplicates", "transaction marker handling"], ["source.event_broker"]),
    ("publish_subscribe_topic", "Publish/subscribe topic service", ["append_log"], ["events", "messages"], ["ev.amqp", "ev.cloudevents"], ["delivery retry", "subscription filtering", "retention variance", "unordered fanout"]),
    ("work_message_queue", "Work message queue", ["work_queue"], ["messages"], ["ev.amqp"], ["redelivery", "visibility/lock timeout", "poison message", "dead-letter divergence"], ["source.message_queue"]),
    ("transaction_log_cdc", "Transactional change-data-capture log", ["append_log", "relational"], ["events", "rows"], ["ev.debezium", "ev.mongodb.change"], ["snapshot/log gap", "transaction fragmentation", "DDL change", "log-position expiry"], ["source.cdc_log"]),
    ("event_sourced_journal", "Event-sourced aggregate journal", ["append_log"], ["events"], ["ev.cloudevents"], ["event-version evolution", "projection lag", "incorrect replay order", "redaction tension"]),
    ("mqtt_broker", "MQTT telemetry broker", ["append_log", "signal"], ["messages", "series_samples"], ["ev.mqtt"], ["QoS duplicates", "retained-state confusion", "session expiry", "topic wildcard leakage"], ["source.mqtt_telemetry"]),
    ("webhook_delivery", "Webhook delivery channel", ["append_log", "document"], ["events", "nested_records"], ["ev.http9110", "ev.cloudevents"], ["duplicate delivery", "out-of-order event", "signature replay", "missing replay"], ["source.webhook"]),
    ("cloud_event_bus", "Cloud event-routing bus", ["append_log"], ["events"], ["ev.cloudevents"], ["context metadata leakage", "schema externality", "batch has no order semantics", "routing retries"]),
    ("edi_mailbox_gateway", "EDI mailbox or B2B gateway", ["work_queue", "hierarchical_message"], ["messages", "files"], ["ev.edifact"], ["functional acknowledgements", "partner version mismatch", "duplicate interchange", "control-number rollover"]),
    ("streaming_media_bus", "Streaming media frame bus", ["append_log"], ["video_frames", "audio_samples"], ["ev.cloudevents"], ["frame loss", "timestamp discontinuity", "codec renegotiation", "backpressure"]),
])

many("enterprise_application", "business_workflow", [
    ("enterprise_resource_planning", "Enterprise resource planning", ["relational", "ledger", "workflow_case"], ["rows", "facts_dimensions", "cases_tasks"], ["ev.isa95", "ev.iso20022"], ["customization", "posting periods", "master-data mismatch", "extract authorization"], ["source.erp"]),
    ("general_ledger_accounting", "General ledger and accounting", ["ledger", "relational"], ["facts_dimensions", "rows"], ["ev.iso20022", "ev.xbrl"], ["posting vs effective date", "period close", "reversal", "currency/precision"]),
    ("procure_to_pay", "Procurement and accounts payable", ["workflow_case", "ledger"], ["cases_tasks", "facts_dimensions"], ["ev.iso20022", "ev.edifact"], ["three-way-match state", "invoice version", "supplier identity", "approval delegation"]),
    ("order_to_cash_billing", "Order-to-cash and billing", ["workflow_case", "ledger"], ["cases_tasks", "facts_dimensions"], ["ev.iso20022", "ev.edifact"], ["order amendment", "invoice correction", "tax jurisdiction", "allocation/settlement"]),
    ("customer_relationship_management", "Customer relationship management", ["relational", "document", "activity_graph"], ["rows", "nested_records", "events"], ["ev.openapi", "ev.activitystreams"], ["custom fields", "owner reassignment", "soft deletion", "merged identities"], ["source.crm"]),
    ("human_resources_payroll", "Human resources, payroll and workforce", ["relational", "document", "ledger"], ["rows", "nested_records", "facts_dimensions"], ["ev.scim", "ev.iso20022"], ["effective dating", "retroactive payroll", "regional rules", "extreme sensitivity"], ["source.hris_payroll"]),
    ("supply_chain_planning", "Supply-chain planning", ["relational", "property_graph"], ["rows", "edges_nodes"], ["ev.epcis", "ev.isa95"], ["scenario vs committed plan", "unit conversion", "multi-echelon identity", "forecast version"], ["source.scm_wms_tms"]),
    ("warehouse_management", "Warehouse management", ["workflow_case", "spatial_feature"], ["cases_tasks", "events"], ["ev.epcis", "ev.isa95"], ["inventory status", "lot/serial genealogy", "late scans", "location hierarchy"], ["source.scm_wms_tms"]),
    ("transportation_management", "Transportation management", ["workflow_case", "property_graph"], ["cases_tasks", "edges_nodes", "events"], ["ev.epcis"], ["shipment/load identity", "multi-leg updates", "partner codes", "planned vs actual"], ["source.scm_wms_tms"]),
    ("manufacturing_execution", "Manufacturing execution", ["workflow_case", "time_series"], ["cases_tasks", "events", "series_samples"], ["ev.isa95", "ev.opcua"], ["lot genealogy", "rework", "equipment identity", "plant customization"], ["source.mes"]),
    ("asset_maintenance", "Asset maintenance and EAM/CMMS", ["workflow_case", "document"], ["cases_tasks", "nested_records"], ["ev.isa95"], ["asset hierarchy drift", "manual work-order closure", "meter rollover", "planned vs actual"], ["source.cmms_eam"]),
    ("project_professional_services", "Project and professional-services automation", ["workflow_case", "relational"], ["cases_tasks", "rows"], ["ev.activitystreams"], ["status customization", "time-entry correction", "billing linkage", "deleted history"], ["source.project_service_management"]),
    ("it_service_management", "IT service management", ["workflow_case", "activity_graph"], ["cases_tasks", "events"], ["ev.otel", "ev.activitystreams"], ["workflow customization", "reopen semantics", "configuration-item drift", "manual severity"], ["source.project_service_management"]),
    ("marketing_automation", "Marketing automation", ["activity_graph", "document"], ["events", "nested_records"], ["ev.activitystreams", "ev.http9110"], ["consent", "identity stitching", "attribution windows", "suppression-list handling"]),
    ("customer_support_contact_center", "Customer support and contact center", ["workflow_case", "activity_graph"], ["cases_tasks", "events", "audio_samples"], ["ev.activitystreams", "ev.cmis"], ["channel identity", "PII in transcript", "reopen/merge", "recording retention"]),
    ("commerce_order_pos", "Commerce, order-management and point of sale", ["ledger", "workflow_case"], ["events", "rows", "facts_dimensions"], ["ev.epcis", "ev.iso20022"], ["returns/cancellations", "basket identity", "tax/currency", "offline terminal"], ["source.pos_ecommerce"]),
    ("enterprise_planning_performance", "Enterprise planning and performance management", ["multidimensional_cube", "workflow_case"], ["facts_dimensions", "cases_tasks"], ["ev.xbrl", "ev.sdmx"], ["scenario/version", "allocation rules", "spread behavior", "approval locks"]),
    ("master_data_management", "Master and reference-data management", ["registry", "property_graph"], ["nested_records", "edges_nodes"], ["ev.dcat", "ev.epcis"], ["survivorship rules", "effective dating", "code retirement", "crosswalk ambiguity"]),
])

many("collaboration_productivity", "versioned_content", [
    ("email_mailbox", "Email mailbox and archive", ["content_tree", "activity_graph"], ["content_versions", "events"], ["ev.imap"], ["thread reconstruction", "mutable flags", "legal hold", "message-id collision"], ["source.email_collaboration"]),
    ("calendar_scheduling", "Calendar and scheduling service", ["activity_graph"], ["events"], ["ev.caldav"], ["recurrence expansion", "timezone changes", "invitation state", "resource booking"]),
    ("team_chat", "Team chat and channel messaging", ["activity_graph"], ["events", "content_versions"], ["ev.activitystreams"], ["edits/deletes", "threads/replies", "guest channels", "ephemeral retention"]),
    ("meeting_conferencing", "Meeting and conferencing system", ["activity_graph", "object_blob"], ["events", "audio_samples", "video_frames", "content_versions"], ["ev.activitystreams", "ev.cmis"], ["participant identity", "recording/transcript alignment", "consent", "retention"]),
    ("wiki_knowledge_base", "Wiki and knowledge-base system", ["content_tree", "activity_graph"], ["content_versions", "events"], ["ev.cmis", "ev.activitystreams"], ["page rename", "version lineage", "embedded ACLs", "transclusion"]),
    ("forms_surveys", "Forms, surveys and manual data capture", ["document", "tabular_record"], ["nested_records", "rows"], ["ev.openapi"], ["questionnaire version", "response bias", "partial submission", "consent"], ["source.form_survey_manual"]),
    ("task_work_management", "Task and work-management system", ["workflow_case", "activity_graph"], ["cases_tasks", "events"], ["ev.activitystreams"], ["custom workflow", "reopened tasks", "assignee history", "deleted activity"]),
    ("whiteboard_design_workspace", "Collaborative design or whiteboard workspace", ["content_tree", "activity_graph"], ["content_versions", "events"], ["ev.cmis", "ev.activitystreams"], ["eventual merge", "object ID reuse", "export fidelity", "link sharing"]),
])

many("code_devops", "versioned_content", [
    ("distributed_version_control", "Distributed version-control repository", ["version_graph", "content_tree"], ["packages_artifacts", "content_versions"], ["ev.git"], ["force push", "history rewrite", "submodule identity", "large-file indirection"]),
    ("issue_change_tracker", "Issue and change-tracking system", ["workflow_case", "activity_graph"], ["cases_tasks", "events"], ["ev.activitystreams"], ["workflow customization", "issue merge/move", "deleted comments", "cross-project identity"]),
    ("ci_cd_orchestrator", "CI/CD execution and deployment system", ["workflow_case", "append_log"], ["cases_tasks", "events", "packages_artifacts"], ["ev.otel", "ev.spdx"], ["rerun identity", "secret leakage", "ephemeral logs", "environment promotion"]),
    ("artifact_package_registry", "Artifact and package registry", ["registry", "object_blob", "version_graph"], ["packages_artifacts", "files"], ["ev.spdx", "ev.cyclonedx"], ["mutable tags", "package deletion", "signature/provenance", "dependency confusion"]),
    ("software_bill_of_materials", "Software/hardware bill-of-materials repository", ["property_graph", "registry"], ["packages_artifacts", "edges_nodes"], ["ev.spdx", "ev.cyclonedx"], ["component identity", "incomplete transitive closure", "version-range ambiguity", "attestation trust"]),
    ("runtime_control_plane", "Runtime and orchestration control plane", ["digital_twin", "activity_graph"], ["nested_records", "events"], ["ev.otel", "ev.openapi"], ["eventual status", "ephemeral objects", "desired-vs-observed state", "watch compaction"]),
    ("configuration_infrastructure_state", "Configuration and infrastructure-state repository", ["version_graph", "document"], ["content_versions", "nested_records"], ["ev.git", "ev.spdx"], ["secret inclusion", "drift from deployed state", "workspace/state locking", "provider schema version"]),
])

many("security_identity", "remote_api", [
    ("identity_directory", "Identity directory and provisioning service", ["registry", "property_graph"], ["identity_entitlements", "edges_nodes"], ["ev.scim"], ["rename/merge", "deprovision lag", "group nesting", "sensitive attributes"]),
    ("identity_provider_authentication", "Identity provider and authentication event source", ["registry", "append_log"], ["identity_entitlements", "events"], ["ev.openid_connect", "ev.webauthn"], ["token vs session identity", "clock skew", "credential rotation", "privacy"]),
    ("privileged_access_secrets", "Privileged-access and secrets system", ["registry", "append_log"], ["identity_entitlements", "events"], ["ev.webauthn"], ["secret exfiltration", "lease expiry", "rotation races", "break-glass access"]),
    ("security_audit_log", "Security audit-log source", ["append_log"], ["events"], ["ev.otel", "ev.tracecontext"], ["tamper evidence", "clock skew", "administrator exclusions", "retention/legal hold"]),
    ("siem_detection_case", "SIEM detection and investigation case system", ["search_index", "workflow_case"], ["events", "cases_tasks"], ["ev.stix_taxii", "ev.otel"], ["alert deduplication", "rule-version drift", "case closure", "evidence retention"]),
    ("threat_intelligence_exchange", "Cyber-threat-intelligence exchange", ["property_graph", "document"], ["edges_nodes", "nested_records"], ["ev.stix_taxii"], ["object versioning", "confidence/provenance", "marking restrictions", "revoked indicators"]),
    ("vulnerability_exposure_management", "Vulnerability and exposure-management system", ["property_graph", "workflow_case"], ["edges_nodes", "cases_tasks"], ["ev.cyclonedx", "ev.stix_taxii"], ["asset identity", "scanner recency", "suppression/acceptance", "CVSS/version changes"]),
    ("network_security_telemetry", "Network-flow and security telemetry", ["append_log", "time_series"], ["events", "series_samples"], ["ev.otel", "ev.stix_taxii"], ["sampling", "NAT identity", "encrypted payload opacity", "high volume"]),
])

many("telemetry_digital_experience", "telemetry_stream", [
    ("application_logs", "Application and infrastructure logs", ["append_log", "search_index"], ["events"], ["ev.otel"], ["unstructured payload", "sensitive data", "sampling", "clock skew"], ["source.application_logs_traces"]),
    ("application_metrics", "Application and infrastructure metrics", ["time_series", "multidimensional_cube"], ["series_samples", "facts_dimensions"], ["ev.otel"], ["temporality mismatch", "reset/wrap", "cardinality explosion", "aggregation loss"]),
    ("distributed_traces", "Distributed traces and spans", ["trace_graph", "append_log"], ["events", "edges_nodes"], ["ev.otel", "ev.tracecontext"], ["head/tail sampling", "orphan spans", "clock skew", "context spoofing"], ["source.application_logs_traces"]),
    ("web_product_analytics", "Web interaction telemetry", ["append_log", "activity_graph"], ["events"], ["ev.activitystreams", "ev.cloudevents"], ["identity stitching", "consent/ad blockers", "client clock", "SDK schema drift"], ["source.web_mobile_telemetry"]),
    ("mobile_product_analytics", "Mobile application telemetry", ["append_log", "activity_graph"], ["events"], ["ev.activitystreams", "ev.cloudevents"], ["offline buffering", "app-version drift", "device resets", "consent"], ["source.web_mobile_telemetry"]),
    ("ad_media_measurement", "Advertising and media measurement platform", ["append_log", "multidimensional_cube"], ["events", "facts_dimensions"], ["ev.activitystreams"], ["attribution windows", "privacy thresholds", "restatements", "account timezone"], ["source.ad_media_platform"]),
])

many("iot_edge", "device_or_control", [
    ("constrained_device_api", "Constrained-device resource API", ["digital_twin", "key_value"], ["keyed_values", "nested_records"], ["ev.coap"], ["message loss/duplication", "sleep cycles", "small payload", "DTLS/OSCORE constraints"]),
    ("iot_sensor_gateway", "IoT sensor gateway", ["time_series", "digital_twin"], ["series_samples", "events"], ["ev.sensorthings", "ev.mqtt"], ["device identity", "clock drift", "buffer overflow", "firmware/schema drift"]),
    ("device_twin_registry", "Device-twin and fleet registry", ["digital_twin", "registry"], ["nested_records", "events"], ["ev.sensorthings", "ev.opcua"], ["desired-vs-reported state", "device reassignment", "stale shadow", "command conflict"]),
    ("edge_buffer_store_forward", "Edge buffer and store-forward source", ["append_log", "time_series"], ["events", "series_samples"], ["ev.coap", "ev.mqtt"], ["intermittent connection", "buffer overwrite", "clock discontinuity", "duplicate replay"]),
    ("smart_meter_gateway", "Smart-meter or interval-meter gateway", ["time_series", "digital_twin"], ["series_samples", "events"], ["ev.sensorthings"], ["interval correction", "meter rollover", "estimated reads", "device replacement"]),
    ("vehicle_telematics", "Vehicle and fleet telematics", ["time_series", "spatial_feature"], ["series_samples", "geometries_tiles", "events"], ["ev.sensorthings", "ev.gtfs"], ["GPS drift", "trip segmentation", "offline upload", "driver/vehicle identity"]),
    ("mobile_offline_store", "Mobile offline application store", ["relational", "document"], ["rows", "nested_records"], ["ev.sqlite.isolation", "ev.geopackage"], ["conflict resolution", "device loss", "partial sync", "local clock"]),
])

many("industrial_ot", "device_or_control", [
    ("scada_dcs", "SCADA or distributed-control system", ["digital_twin", "signal", "time_series"], ["signals_waveforms", "series_samples", "events"], ["ev.opcua", "ev.isa95"], ["safety boundary", "tag rename", "deadband/sampling", "control risk"], ["source.scada_dcs"]),
    ("opcua_information_server", "OPC UA information server", ["digital_twin", "property_graph", "signal"], ["edges_nodes", "series_samples", "events"], ["ev.opcua"], ["namespace changes", "certificate lifecycle", "subscription queue overflow", "profile variance"], ["source.opcua_gateway"]),
    ("plc_controller", "Programmable logic controller", ["key_value", "signal"], ["keyed_values", "signals_waveforms"], ["ev.opcua", "ev.isa95"], ["unsafe writes", "register mapping", "no trusted clock", "scan-cycle aliasing"], ["source.plc_device"]),
    ("industrial_historian", "Industrial process historian", ["time_series", "signal"], ["series_samples", "signals_waveforms"], ["ev.opcua", "ev.isa95"], ["compression/interpolation", "quality codes", "tag hierarchy", "retention"], ["source.industrial_historian"]),
    ("building_automation", "Building-automation management system", ["digital_twin", "time_series"], ["series_samples", "events"], ["ev.opcua", "ev.buildingsmart"], ["point naming", "occupancy privacy", "schedule overrides", "unit mismatch"]),
    ("robotics_machine_controller", "Robotics and machine controller", ["digital_twin", "signal"], ["signals_waveforms", "events", "commands"], ["ev.opcua", "ev.isa95"], ["real-time control boundary", "program version", "safety interlocks", "high-rate data"]),
    ("quality_inspection_system", "Industrial quality-inspection system", ["workflow_case", "image", "signal"], ["cases_tasks", "images_frames", "series_samples"], ["ev.isa95"], ["calibration", "false accept/reject labels", "sample traceability", "recipe version"]),
    ("batch_process_control", "Batch process-control system", ["workflow_case", "time_series"], ["cases_tasks", "series_samples", "events"], ["ev.isa95", "ev.opcua"], ["batch phase semantics", "recipe version", "hold/release", "equipment allocation"]),
    ("energy_grid_control", "Energy grid and utility control system", ["digital_twin", "time_series", "property_graph"], ["series_samples", "edges_nodes", "events"], ["ev.opcua", "ev.sensorthings"], ["critical infrastructure", "topology state", "estimated telemetry", "clock synchronization"]),
])

many("scientific_research", "scientific_asset", [
    ("laboratory_information_management", "Laboratory information-management system", ["workflow_case", "document"], ["cases_tasks", "nested_records"], ["ev.fhir", "ev.hdf5"], ["specimen/sample identity", "chain of custody", "amended results", "method version"], ["source.lims_instrument"]),
    ("scientific_instrument", "Scientific instrument data source", ["signal", "multidimensional_array"], ["signals_waveforms", "arrays_chunks", "files"], ["ev.netcdf", "ev.hdf5"], ["calibration", "proprietary format", "sampling", "instrument clock"], ["source.scientific_instrument"]),
    ("multidimensional_scientific_file", "Multidimensional scientific-data repository", ["multidimensional_array"], ["arrays_chunks", "files"], ["ev.netcdf", "ev.hdf5"], ["dimension conventions", "fill values", "chunking", "metadata vocabulary"]),
    ("genomics_sequence_repository", "Genomics sequence and variant repository", ["object_blob", "relational"], ["files", "rows"], ["ev.fhir", "ev.hdf5"], ["reference assembly", "sample identity", "consent", "pipeline/version"]),
    ("clinical_research_edc", "Clinical-research electronic data capture", ["workflow_case", "document"], ["cases_tasks", "nested_records"], ["ev.fhir"], ["protocol version", "query resolution", "subject pseudonym", "source-data verification"]),
    ("simulation_model_output", "Simulation and model-output repository", ["simulation_state", "multidimensional_array"], ["arrays_chunks", "files"], ["ev.netcdf", "ev.hdf5"], ["model/configuration version", "ensemble member", "restart state", "floating-point reproducibility"]),
    ("research_data_repository", "Research-data and publication repository", ["registry", "object_blob"], ["files", "nested_records"], ["ev.dcat"], ["DOI/version identity", "embargo", "license", "retraction"]),
    ("high_performance_job_scheduler", "High-performance computing job scheduler", ["workflow_case", "append_log"], ["cases_tasks", "events"], ["ev.otel"], ["job retry identity", "ephemeral nodes", "resource accounting", "queue state"]),
])

many("geospatial_media", "scientific_asset", [
    ("gis_feature_service", "Geospatial feature service", ["spatial_feature", "relational"], ["geometries_tiles", "rows"], ["ev.geopackage", "ev.sensorthings"], ["CRS mismatch", "geometry validity", "paging", "topology/version"], ["source.gis_service"]),
    ("raster_remote_sensing_catalog", "Raster and remote-sensing catalog", ["raster_grid", "registry"], ["images_frames", "geometries_tiles", "files"], ["ev.stac", "ev.netcdf"], ["cloud cover", "sensor calibration", "resolution", "reprocessing collection"], ["source.remote_sensing"]),
    ("point_cloud_repository", "Point-cloud repository", ["point_cloud"], ["points", "files"], ["ev.stac"], ["coordinate reference", "density/decimation", "classification version", "tiling"]),
    ("cad_bim_repository", "CAD/BIM and digital-building repository", ["mesh_bim", "property_graph"], ["meshes", "edges_nodes", "content_versions"], ["ev.buildingsmart"], ["model federation", "element identity", "coordinate systems", "version/approval"]),
    ("image_asset_library", "Image and digital-asset library", ["image", "content_tree"], ["images_frames", "content_versions"], ["ev.cmis", "ev.dicom"], ["EXIF/privacy", "orientation", "derivative vs original", "rights/license"]),
    ("audio_recording_repository", "Audio recording repository", ["audio", "content_tree"], ["audio_samples", "content_versions"], ["ev.cmis"], ["codec/container", "sample rate", "channel layout", "consent/retention"]),
    ("video_surveillance_media", "Video and surveillance-media repository", ["video", "content_tree"], ["video_frames", "content_versions"], ["ev.cmis", "ev.dicom"], ["frame timestamps", "codec changes", "privacy/redaction", "retention overwrite"]),
    ("mobility_location_stream", "Mobility and location stream", ["spatial_feature", "time_series"], ["geometries_tiles", "series_samples"], ["ev.gtfs", "ev.sensorthings"], ["map matching", "location privacy", "clock/GPS drift", "trip identity"]),
    ("weather_environmental_observation", "Weather and environmental observation source", ["spatial_feature", "time_series", "raster_grid"], ["series_samples", "geometries_tiles", "arrays_chunks"], ["ev.sensorthings", "ev.netcdf"], ["station relocation", "sensor drift", "forecast-vs-observation", "late quality control"], ["source.weather_environmental_sensor"]),
])

many("public_reference", "snapshot_repository", [
    ("open_data_catalog", "Public/open-data catalog", ["registry", "object_blob"], ["nested_records", "files"], ["ev.dcat"], ["silent revision", "license", "publication delay", "distribution link rot"], ["source.public_open_data"]),
    ("official_statistics_exchange", "Official-statistics exchange", ["multidimensional_cube", "registry"], ["facts_dimensions"], ["ev.sdmx"], ["seasonal adjustment revision", "confidentiality suppression", "code-list version", "vintage"]),
    ("reference_code_registry", "Reference and code-system registry", ["registry", "property_graph"], ["nested_records", "edges_nodes"], ["ev.dcat", "ev.fhir"], ["code retirement", "hierarchy change", "effective date", "crosswalk ambiguity"], ["source.reference_master_data"]),
    ("government_administrative_register", "Government administrative register", ["registry", "workflow_case"], ["nested_records", "cases_tasks"], ["ev.dcat"], ["legal authority", "historical correction", "personal data", "jurisdiction"]),
    ("web_feed_and_syndication", "Web feed and syndication source", ["activity_graph", "document"], ["events", "nested_records"], ["ev.activitystreams", "ev.http9110"], ["entry update/delete", "feed truncation", "link rot", "publication time"]),
    ("web_crawl_snapshot", "Web crawl or website snapshot", ["content_tree", "property_graph"], ["content_versions", "edges_nodes"], ["ev.http9110", "ev.dcat"], ["robots/license", "dynamic content", "canonical URL", "crawl incompleteness"]),
    ("published_report_filing_portal", "Published report or filing portal", ["registry", "object_blob"], ["files", "facts_dimensions"], ["ev.xbrl", "ev.dcat"], ["amendment/retraction", "taxonomy version", "human-readable vs machine-readable", "publication lag"]),
])

many("regulated_vertical", "regulated_record", [
    ("electronic_health_record", "Electronic health record", ["document", "workflow_case"], ["nested_records", "cases_tasks"], ["ev.fhir"], ["patient/encounter identity", "code systems", "amendments", "consent"], ["source.ehr_emr"]),
    ("health_claims_adjudication", "Health claims and adjudication", ["workflow_case", "ledger"], ["cases_tasks", "facts_dimensions"], ["ev.fhir", "ev.iso20022"], ["adjudication lag", "resubmission", "coding drift", "eligibility intervals"], ["source.claims_billing"]),
    ("medical_imaging_pacs", "Medical-imaging PACS/VNA", ["image", "content_tree"], ["images_frames", "content_versions"], ["ev.dicom"], ["patient/study identity", "transfer syntax", "de-identification", "instance replacement"]),
    ("pharmacy_medication_management", "Pharmacy and medication-management system", ["workflow_case", "registry"], ["cases_tasks", "nested_records"], ["ev.fhir"], ["order/dispense/admin distinction", "dose/unit", "formulary version", "controlled substance"]),
    ("core_banking", "Core banking deposits and lending", ["ledger", "workflow_case"], ["facts_dimensions", "cases_tasks"], ["ev.iso20022"], ["value date vs booking date", "reversal", "interest accrual", "end-of-day cut"]),
    ("payments_ledger", "Payments authorization, clearing and settlement", ["ledger", "append_log"], ["facts_dimensions", "events"], ["ev.iso20022"], ["authorization vs settlement", "chargeback", "currency precision", "idempotency"], ["source.payments_ledger"]),
    ("trading_order_execution", "Trading order and execution system", ["append_log", "ledger"], ["events", "facts_dimensions"], ["ev.fix"], ["venue sequence", "cancel/correct", "session reset", "market-clock precision"]),
    ("market_data_feed", "Financial market-data feed", ["time_series", "append_log"], ["series_samples", "events"], ["ev.fix"], ["corporate actions", "venue sequence", "late corrections", "licensing"], ["source.market_data"]),
    ("insurance_policy_claims", "Insurance policy and claims administration", ["workflow_case", "ledger"], ["cases_tasks", "facts_dimensions"], ["ev.iso20022"], ["policy version", "coverage effective time", "reserve development", "claim reopen"]),
    ("regulatory_xbrl_filing", "Regulatory XBRL filing repository", ["multidimensional_cube", "registry"], ["facts_dimensions", "files"], ["ev.xbrl"], ["taxonomy extensions", "duplicate facts", "units/decimals", "amended filings"]),
    ("telecom_oss_bss", "Telecommunications OSS/BSS", ["property_graph", "time_series", "ledger"], ["edges_nodes", "series_samples", "facts_dimensions"], ["ev.otel", "ev.iso20022"], ["network/service/customer identity", "mediation loss", "usage late arrival", "rating version"]),
    ("utility_meter_billing", "Utility metering and billing", ["time_series", "ledger"], ["series_samples", "facts_dimensions"], ["ev.sensorthings", "ev.iso20022"], ["estimated reads", "interval correction", "tariff version", "meter exchange"]),
    ("aviation_operations_maintenance", "Aviation operations and maintenance", ["workflow_case", "time_series"], ["cases_tasks", "series_samples", "events"], ["ev.opcua", "ev.isa95"], ["tail/component identity", "flight leg", "airworthiness records", "safety boundary"]),
    ("rail_transit_operations", "Rail and public-transit operations", ["spatial_feature", "activity_graph"], ["geometries_tiles", "events"], ["ev.gtfs"], ["schedule vs realtime", "service day", "trip replacement", "vehicle identity"]),
    ("maritime_logistics_tracking", "Maritime logistics and vessel tracking", ["spatial_feature", "activity_graph"], ["geometries_tiles", "events"], ["ev.epcis", "ev.sensorthings"], ["vessel/container identity", "AIS gaps/spoofing", "port event corrections", "partner visibility"]),
    ("pharmaceutical_quality_manufacturing", "Pharmaceutical quality and regulated manufacturing", ["workflow_case", "time_series"], ["cases_tasks", "series_samples", "content_versions"], ["ev.isa95", "ev.fhir"], ["electronic signatures", "batch genealogy", "deviation/CAPA", "validated-system change"]),
    ("government_case_justice", "Government case, benefits or justice system", ["workflow_case", "content_tree"], ["cases_tasks", "content_versions"], ["ev.dcat", "ev.cmis"], ["sealed records", "legal authority", "appeal/reopen", "retention"]),
    ("education_student_learning", "Student information and learning system", ["workflow_case", "activity_graph"], ["cases_tasks", "events"], ["ev.activitystreams"], ["learner identity", "term/version", "grade changes", "minor privacy"]),
    ("property_land_cadastral", "Property, land and cadastral registry", ["spatial_feature", "registry"], ["geometries_tiles", "nested_records"], ["ev.geopackage", "ev.dcat"], ["parcel topology", "legal effective date", "superseded title", "jurisdiction"]),
])

many("legacy_offline", "legacy_batch", [
    ("mainframe_relational_or_hierarchical", "Mainframe database or hierarchical store", ["relational", "document"], ["rows", "opaque_records"], ["ev.edifact"], ["EBCDIC/encoding", "copybook/catalog mismatch", "log access", "batch/online cut"]),
    ("indexed_sequential_dataset", "Indexed or sequential legacy dataset", ["fixed_record"], ["opaque_records"], ["ev.posix.files"], ["record layout", "key reuse", "generation data groups", "blocked records"]),
    ("fixed_record_batch_exchange", "Fixed-record batch exchange", ["fixed_record"], ["opaque_records", "files"], ["ev.edifact"], ["control totals", "record-version mixing", "late/missing file", "retransmission"]),
    ("tape_or_cold_archive", "Tape or cold archival source", ["object_blob"], ["files"], ["ev.posix.files"], ["restore latency", "media degradation", "catalog mismatch", "retention/destruction"]),
    ("print_spool_report", "Print-spool or rendered-report source", ["object_blob", "tabular_record"], ["files", "opaque_records"], ["ev.opendocument"], ["presentation not semantics", "page breaks", "OCR error", "rerun identity"]),
    ("transaction_monitor", "Legacy transaction-monitor journal", ["append_log", "workflow_case"], ["events", "opaque_records"], ["ev.amqp"], ["unit-of-work mapping", "restart/recovery", "copybook version", "partial log access"]),
    ("air_gapped_media_transfer", "Air-gapped removable-media transfer", ["object_blob"], ["files"], ["ev.posix.files", "ev.spdx"], ["malware", "chain of custody", "stale snapshot", "media loss"]),
    ("paper_form_ocr", "Paper form, scan and OCR capture", ["image", "document"], ["images_frames", "nested_records"], ["ev.cmis"], ["recognition error", "handwriting", "page association", "human verification"]),
    ("manual_offline_register", "Manual or offline operational register", ["tabular_record", "workflow_case"], ["rows", "cases_tasks"], ["ev.opendocument"], ["human error", "delayed entry", "overwrite", "no stable identifier"]),
])


# Class-level refinements where a shared profile would otherwise erase a material semantic
# distinction.  These are still provider-neutral; they name domain objects and observable
# capabilities rather than products.
CLASS_OVERRIDES = {
    "source.operational_database.search_index": {
        "authority": {"role": "operational_projection", "field_level_override_required": True},
        "object_model": {"object_kinds": ["indexes", "aliases", "documents", "segments", "mappings"]},
    },
    "source.operational_database.vector_similarity_index": {
        "authority": {"role": "operational_projection", "field_level_override_required": True},
        "object_model": {"object_kinds": ["indexes", "namespaces", "vectors", "metadata", "index_builds"]},
    },
    "source.operational_database.in_memory_cache": {
        "authority": {"role": "derived_replica", "field_level_override_required": True},
        "object_model": {"object_kinds": ["namespaces", "keys", "values", "expiry_metadata", "eviction_state"]},
        "order_finality": {"finality_model": "never_intrinsically_final", "deletion_semantics": ["expiry_ttl", "hard_delete", "compaction_loss"]},
    },
    "source.analytical_repository.query_result_cache": {
        "object_model": {"object_kinds": ["query_fingerprints", "parameter_sets", "security_contexts", "result_snapshots", "expiry_metadata"]},
        "order_finality": {"finality_model": "never_intrinsically_final", "deletion_semantics": ["expiry_ttl", "hard_delete"]},
    },
    "source.analytical_repository.feature_repository": {
        "object_model": {"object_kinds": ["entities", "feature_definitions", "feature_values", "event_timestamps", "materializations"]},
    },
    "source.file_object_content.spreadsheet_workbook": {
        "object_model": {"object_kinds": ["workbooks", "sheets", "named_ranges", "cells", "formulas", "styles", "external_links"]},
        "transactions": {"boundary": "file_replace", "snapshot_cut": "workbook_version_or_digest"},
    },
    "source.api_remote_service.bulk_export_api": {
        "object_model": {"object_kinds": ["export_jobs", "job_statuses", "result_manifests", "result_parts", "download_tokens"]},
        "order_finality": {"finality_model": "publication_revision", "ordering_scope": "file_byte_order"},
    },
    "source.event_messaging_cdc.transaction_log_cdc": {
        "object_model": {"object_kinds": ["databases", "schemas", "tables", "transactions", "row_changes", "log_positions"]},
        "interfaces": {"read_modes": ["snapshot", "change_data_capture", "stream"], "write_modes": ["none"], "change_modes": ["transaction_log"]},
        "order_finality": {"ordering_scope": "per_transaction", "ordering_key": "commit_log_position", "finality_model": "commit_final"},
        "transactions": {"boundary": "database_transaction", "snapshot_cut": "consistent_snapshot_plus_log_position", "cross_object_atomicity": "preserve_source_transaction_when_exposed"},
    },
    "source.event_messaging_cdc.webhook_delivery": {
        "object_model": {"object_kinds": ["subscriptions", "event_types", "deliveries", "attempts", "signatures"]},
        "interfaces": {"discovery_modes": ["capability_document", "manual_inventory"], "read_modes": ["subscription"], "write_modes": ["acknowledge"], "change_modes": ["webhook"]},
        "order_finality": {"ordering_scope": "service_defined", "ordering_key": "event_id_or_delivery_id", "gap_signal": "provider_replay_or_reconciliation"},
    },
    "source.enterprise_application.general_ledger_accounting": {
        "authority": {"role": "system_of_record", "field_level_override_required": True},
        "object_model": {"object_kinds": ["legal_entities", "ledgers", "accounts", "journals", "journal_lines", "periods", "balances", "reversals"]},
        "order_finality": {"finality_model": "workflow_approved", "ordering_scope": "per_transaction", "ordering_key": "ledger_journal_posting_sequence"},
    },
    "source.enterprise_application.procure_to_pay": {"object_model": {"object_kinds": ["suppliers", "requisitions", "purchase_orders", "receipts", "invoices", "matches", "approvals", "payments"]}},
    "source.enterprise_application.order_to_cash_billing": {"object_model": {"object_kinds": ["customers", "quotes", "orders", "fulfilments", "invoices", "credits", "receipts", "allocations"]}},
    "source.enterprise_application.customer_relationship_management": {"object_model": {"object_kinds": ["accounts", "contacts", "leads", "opportunities", "activities", "owners", "campaign_members"]}},
    "source.enterprise_application.human_resources_payroll": {"object_model": {"object_kinds": ["workers", "positions", "assignments", "organizations", "time_entries", "pay_runs", "earnings", "deductions"]}},
    "source.enterprise_application.supply_chain_planning": {"object_model": {"object_kinds": ["items", "locations", "bills_of_material", "supply", "demand", "forecasts", "plans", "scenarios"]}},
    "source.enterprise_application.warehouse_management": {"object_model": {"object_kinds": ["facilities", "locations", "inventory_units", "lots", "serials", "waves", "tasks", "movements"]}},
    "source.enterprise_application.transportation_management": {"object_model": {"object_kinds": ["orders", "shipments", "loads", "legs", "stops", "carriers", "tenders", "status_events"]}},
    "source.enterprise_application.manufacturing_execution": {"object_model": {"object_kinds": ["sites", "work_centers", "equipment", "materials", "work_orders", "operations", "lots", "genealogy", "production_events"]}},
    "source.enterprise_application.asset_maintenance": {"object_model": {"object_kinds": ["assets", "asset_hierarchies", "meters", "maintenance_plans", "work_orders", "failures", "parts", "labor"]}},
    "source.enterprise_application.enterprise_planning_performance": {"object_model": {"object_kinds": ["models", "dimensions", "members", "scenarios", "versions", "facts", "allocations", "approvals"]}},
    "source.security_identity.identity_directory": {"object_model": {"object_kinds": ["users", "groups", "service_principals", "memberships", "attributes", "provisioning_events"]}},
    "source.security_identity.identity_provider_authentication": {"object_model": {"object_kinds": ["subjects", "clients", "sessions", "authentication_events", "factors", "tokens", "consents"]}},
    "source.telemetry_digital_experience.application_logs": {"object_model": {"object_kinds": ["resources", "log_streams", "log_records", "severity_mappings", "retention_tiers"]}},
    "source.telemetry_digital_experience.application_metrics": {"object_model": {"object_kinds": ["resources", "metric_descriptors", "data_points", "attributes", "exemplars", "temporality_resets"]}},
    "source.telemetry_digital_experience.distributed_traces": {"object_model": {"object_kinds": ["resources", "traces", "spans", "span_events", "links", "sampling_decisions"]}},
    "source.industrial_ot.industrial_historian": {
        "authority": {"role": "observation_recorder", "field_level_override_required": False},
        "object_model": {"object_kinds": ["sites", "tag_namespaces", "tags", "samples", "quality_codes", "annotations", "compression_rules"]},
        "interfaces": {"write_modes": ["append"], "change_modes": ["subscription", "poll_diff"]},
    },
    "source.scientific_research.laboratory_information_management": {
        "authority": {"role": "human_workflow_record", "field_level_override_required": True},
        "object_model": {"object_kinds": ["studies", "subjects", "samples", "aliquots", "tests", "methods", "instruments", "results", "amendments"]},
    },
    "source.scientific_research.scientific_instrument": {"object_model": {"object_kinds": ["instruments", "configurations", "calibrations", "runs", "channels", "samples", "raw_signals", "derived_results"]}},
    "source.geospatial_media.gis_feature_service": {"object_model": {"object_kinds": ["collections", "features", "geometries", "attributes", "coordinate_reference_systems", "versions"]}},
    "source.geospatial_media.raster_remote_sensing_catalog": {"object_model": {"object_kinds": ["collections", "items", "assets", "bands", "footprints", "acquisition_times", "processing_levels"]}},
    "source.geospatial_media.point_cloud_repository": {"object_model": {"object_kinds": ["collections", "tiles", "points", "dimensions", "classifications", "coordinate_reference_systems"]}},
    "source.geospatial_media.cad_bim_repository": {"object_model": {"object_kinds": ["projects", "models", "sites", "buildings", "storeys", "elements", "relationships", "geometries", "revisions"]}},
    "source.public_reference.open_data_catalog": {
        "authority": {"role": "authoritative_publication", "field_level_override_required": True},
        "object_model": {"object_kinds": ["catalogs", "datasets", "dataset_series", "distributions", "data_services", "catalog_records", "publishers"]},
    },
    "source.public_reference.official_statistics_exchange": {
        "authority": {"role": "authoritative_publication", "field_level_override_required": False},
        "object_model": {"object_kinds": ["dataflows", "data_structures", "concepts", "code_lists", "datasets", "series", "observations", "constraints"]},
    },
    "source.regulated_vertical.electronic_health_record": {"object_model": {"object_kinds": ["patients", "encounters", "conditions", "observations", "orders", "procedures", "medications", "documents", "provenance", "audit_events"]}},
    "source.regulated_vertical.health_claims_adjudication": {"object_model": {"object_kinds": ["members", "coverage", "providers", "claims", "lines", "authorizations", "adjudications", "payments", "adjustments"]}},
    "source.regulated_vertical.medical_imaging_pacs": {"object_model": {"object_kinds": ["patients", "studies", "series", "instances", "frames", "transfer_syntaxes", "structured_reports", "audit_events"]}},
    "source.regulated_vertical.core_banking": {"object_model": {"object_kinds": ["customers", "accounts", "products", "contracts", "transactions", "balances", "accruals", "holds", "statements"]}},
    "source.regulated_vertical.payments_ledger": {
        "object_model": {"object_kinds": ["payment_instructions", "authorizations", "captures", "clearing_records", "settlements", "refunds", "chargebacks", "fees"]},
        "order_finality": {"finality_model": "settlement_final", "ordering_scope": "per_transaction", "ordering_key": "payment_lifecycle_sequence"},
    },
    "source.regulated_vertical.trading_order_execution": {"object_model": {"object_kinds": ["sessions", "instruments", "orders", "cancel_replace_requests", "executions", "allocations", "positions", "sequence_resets"]}},
    "source.regulated_vertical.market_data_feed": {"object_model": {"object_kinds": ["venues", "instruments", "books", "quotes", "trades", "statistics", "corporate_actions", "corrections"]}},
    "source.regulated_vertical.insurance_policy_claims": {"object_model": {"object_kinds": ["parties", "risks", "policies", "coverages", "endorsements", "claims", "exposures", "reserves", "payments"]}},
    "source.regulated_vertical.regulatory_xbrl_filing": {"object_model": {"object_kinds": ["filers", "reports", "facts", "contexts", "units", "taxonomies", "dimensions", "footnotes", "amendments"]}},
    "source.regulated_vertical.rail_transit_operations": {"object_model": {"object_kinds": ["agencies", "routes", "stops", "trips", "service_calendars", "stop_times", "vehicles", "trip_updates", "alerts"]}},
    "source.regulated_vertical.property_land_cadastral": {"object_model": {"object_kinds": ["jurisdictions", "parcels", "boundaries", "titles", "rights", "parties", "transactions", "valuations", "supersessions"]}},
}


def build_record(row: tuple) -> dict:
    family, suffix, name, profile_id, models, shapes, evidence, hazards, inherited = row
    record = copy.deepcopy(PROFILES[profile_id])
    record.update({
        "record_kind": "source_system_capability_class",
        "class_id": f"source.{family}.{suffix}",
        "edition": 1,
        "status": "researched_candidate",
        "name": name,
        "family_id": family,
        "profile_id": profile_id,
        "definition": f"Provider-neutral source capability class for {name.lower()}; concrete products, tenants, deployments and connectors are occurrences or adapters.",
        "not_a_vendor_type": True,
        "classification_rule": "Classify by observable authority, object/payload model, interface, change, time/order/finality and assurance semantics; a family label alone is insufficient.",
        "evidence_refs": evidence,
        "inherited_seed_refs": inherited,
    })
    record["object_model"]["logical_models"] = models
    record["object_model"]["payload_shapes"] = shapes
    for section, patch in CLASS_OVERRIDES.get(record["class_id"], {}).items():
        record[section].update(copy.deepcopy(patch))
    record["hazards"] = list(dict.fromkeys(record["hazards"] + hazards))
    record["verification"] = list(dict.fromkeys(record["verification"]))
    return record


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: list[dict]) -> None:
    path.write_text("".join(json.dumps(value, sort_keys=True) + "\n" for value in values), encoding="utf-8")


def main() -> int:
    records = [build_record(row) for row in SEEDS]
    evidence_records = [
        {
            "evidence_id": evidence_id,
            "title": title,
            "issuer": issuer,
            "url": url,
            "authority": "primary",
            "source_kind": source_kind,
            "supports_surfaces": surfaces,
            "retrieved_on": AS_OF,
            "use_limit": "Supports only the named surfaces; does not prove every deployment or connector capability.",
        }
        for evidence_id, title, issuer, url, surfaces, source_kind in EVIDENCE
    ]
    write_json(HERE / "classification-axes.json", {"universe_id": "source_system", "edition": 1, "as_of": AS_OF, "axes": AXES})
    write_jsonl(HERE / "source-classes.jsonl", records)
    write_jsonl(HERE / "evidence-sources.jsonl", evidence_records)
    write_json(HERE / "verification-tests.json", {
        "registry_id": "san.domain-atlas.source-system-verification",
        "edition": 1,
        "tests": [{"test_id": test_id, "purpose": purpose, "result_contract": ["pass", "fail", "not_supported", "not_authorized", "inconclusive"], "evidence_required": True} for test_id, purpose in VERIFICATION_TESTS],
    })

    by_family = Counter(record["family_id"] for record in records)
    by_profile = Counter(record["profile_id"] for record in records)
    evidence_usage = Counter(ref for record in records for ref in record["evidence_refs"])
    uncovered_evidence = sorted(item["evidence_id"] for item in evidence_records if not evidence_usage[item["evidence_id"]])
    write_json(HERE / "coverage-report.json", {
        "report_id": "san.domain-atlas.source-system-universe-coverage",
        "edition": 1,
        "as_of": AS_OF,
        "standing": "researched_open_world_candidate_universe",
        "class_records": len(records),
        "families": dict(sorted(by_family.items())),
        "capability_profiles": dict(sorted(by_profile.items())),
        "classification_axes": len(AXES),
        "axis_values": sum(len(values) for values in AXES.values()),
        "primary_evidence_records": len(evidence_records),
        "primary_evidence_issuers": len({item["issuer"] for item in evidence_records}),
        "evidence_records_unused_by_classes": uncovered_evidence,
        "classes_without_evidence": [record["class_id"] for record in records if not record["evidence_refs"]],
        "classes_without_hazards": [record["class_id"] for record in records if not record["hazards"]],
        "classes_without_verification": [record["class_id"] for record in records if not record["verification"]],
        "inherited_seed_refs_mapped": len({ref for record in records for ref in record["inherited_seed_refs"]}),
        "completion_claim": False,
        "completeness_semantics": "Open-world saturation: every encountered occurrence must classify or emit a typed extension gap; no finite class count proves future completeness.",
    })
    print(f"WROTE {len(records)} source classes, {len(evidence_records)} primary evidence records, {len(AXES)} axes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
