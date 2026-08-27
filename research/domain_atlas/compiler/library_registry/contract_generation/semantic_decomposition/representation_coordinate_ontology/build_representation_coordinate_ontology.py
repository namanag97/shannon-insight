#!/usr/bin/env python3
"""Build a representation-layer coordinate ontology and lossless all-member rebase."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
PRECLASSIFICATIONS = SEM / "applicability_matrices/member-preclassifications.jsonl"
sys.path.insert(0, str(SEM))

from structural_coordinate_package import build_package, render_outputs  # noqa: E402


SOURCES = [
    {
        "source_id": "source.representation.json-schema-2020-12",
        "title": "JSON Schema: A Media Type for Describing JSON Documents — Core 2020-12",
        "publisher": "JSON Schema Project",
        "url": "https://json-schema.org/draft/2020-12/json-schema-core",
        "bounded_implication": "Schema resources, dialects, vocabularies, identifiers, references, assertions and annotations are distinct representation concerns.",
        "authority_limit": "JSON Schema validation does not establish bounded-context meaning, aggregate invariants, identity, authorization, effect safety or business acceptance.",
    },
    {
        "source_id": "source.representation.arrow-columnar",
        "title": "Apache Arrow Columnar Format",
        "publisher": "Apache Arrow",
        "url": "https://arrow.apache.org/docs/format/Columnar.html",
        "bounded_implication": "Logical data types, physical memory layouts, buffers, validity bitmaps, nesting, dictionary encoding and extension types are separately specified.",
        "authority_limit": "An Arrow layout or extension name does not own domain meaning, row identity, business constraints, causal order or application compatibility.",
    },
    {
        "source_id": "source.representation.protobuf-proto3",
        "title": "Protocol Buffers Language Guide (proto3)",
        "publisher": "Protocol Buffers Project",
        "url": "https://protobuf.dev/programming-guides/proto3/",
        "bounded_implication": "Field numbers, presence, unknown fields and binary/JSON wire-safe change rules are distinct from generated-language APIs.",
        "authority_limit": "Wire compatibility and unknown-field retention do not prove semantic preservation, validation, authorization or safe application behavior.",
    },
    {
        "source_id": "source.representation.avro-spec",
        "title": "Apache Avro Specification",
        "publisher": "Apache Avro",
        "url": "https://avro.apache.org/docs/current/specification/",
        "bounded_implication": "Data is written under a writer schema and interpreted under a reader schema through directional schema resolution with named types, aliases and promotion rules.",
        "authority_limit": "Successful schema resolution is not bidirectional round-trip meaning, domain validity, historical truth or migration acceptance.",
    },
    {
        "source_id": "source.representation.cbor-rfc8949",
        "title": "RFC 8949: Concise Binary Object Representation (CBOR)",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc8949.html",
        "bounded_implication": "A data model, binary encoding, tags, preferred serialization and deterministic encoding requirements occupy distinct interoperability layers.",
        "authority_limit": "Deterministic CBOR bytes do not create domain identity, semantic equivalence, trust, correctness or application acceptance.",
    },
    {
        "source_id": "source.representation.jcs-rfc8785",
        "title": "RFC 8785: JSON Canonicalization Scheme (JCS)",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc8785.html",
        "bounded_implication": "A scoped canonicalization profile can produce invariant JSON representations for cryptographic operations under explicit input restrictions.",
        "authority_limit": "Canonical JSON bytes do not prove domain equality, source authenticity, claim truth, schema validity or fitness for use.",
    },
    {
        "source_id": "source.representation.iceberg-spec",
        "title": "Apache Iceberg Table Specification",
        "publisher": "Apache Iceberg",
        "url": "https://iceberg.apache.org/spec/",
        "bounded_implication": "Schemas, stable non-reused field IDs, partition specs, sort orders, manifests, snapshots and table metadata have distinct identities and evolution rules.",
        "authority_limit": "Table-format identity and evolution do not establish upstream semantic identity, business correctness, row uniqueness or arbitrary migration reversibility.",
    },
    {
        "source_id": "source.representation.parquet-format",
        "title": "Apache Parquet File Format",
        "publisher": "Apache Parquet",
        "url": "https://parquet.apache.org/docs/file-format/",
        "bounded_implication": "Column chunks, pages, encodings, compression, metadata, logical types and statistics form separable physical and logical representation concerns.",
        "authority_limit": "Parquet metadata or statistics do not own domain semantics, prove complete pruning safety outside their contract, or establish application-level compatibility.",
    },
    {
        "source_id": "source.representation.unicode-normalization",
        "title": "Unicode Standard Annex #15: Unicode Normalization Forms",
        "publisher": "Unicode Consortium",
        "url": "https://unicode.org/reports/tr15/",
        "bounded_implication": "Normalization forms define scoped equivalence-preserving transformations over Unicode sequences with stability and composition rules.",
        "authority_limit": "Unicode normalization does not define locale collation, identifier policy, domain equality, confusable safety or arbitrary text canonicalization.",
    },
    {
        "source_id": "source.representation.wit",
        "title": "WebAssembly Interface Type (WIT) Language",
        "publisher": "Bytecode Alliance / WebAssembly Component Model",
        "url": "https://component-model.bytecodealliance.org/design/wit.html",
        "bounded_implication": "Packages, worlds, interfaces, resources, imports, exports and canonical type bindings describe component boundaries separately from implementations.",
        "authority_limit": "WIT types and canonical ABI adaptation do not prove domain meaning, behavior, effect safety, resource guarantees or provider qualification.",
    },
    {
        "source_id": "source.representation.openapi-3-2",
        "title": "OpenAPI Specification 3.2.0",
        "publisher": "OpenAPI Initiative",
        "url": "https://spec.openapis.org/oas/v3.2.0.html",
        "bounded_implication": "A language-neutral HTTP description separates operations, parameters, messages, media types, schemas, callbacks and external documentation.",
        "authority_limit": "An OpenAPI document does not prove server conformance, domain invariants, authorization, behavioral compatibility or operational fitness.",
    },
    {
        "source_id": "source.representation.media-types-rfc6838",
        "title": "RFC 6838: Media Type Specifications and Registration Procedures",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc6838.html",
        "bounded_implication": "Media types identify representation formats and registration trees with explicit interoperability, fragment and security considerations.",
        "authority_limit": "A media-type label does not prove payload conformance, semantic identity, safe processing, authenticity or negotiated application support.",
    },
    {
        "source_id": "source.representation.zstd-rfc8878",
        "title": "RFC 8878: Zstandard Compression and the application/zstd Media Type",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc8878.html",
        "bounded_implication": "Frames, blocks, dictionaries, checksums and decompression limits are explicit parts of a compression representation contract.",
        "authority_limit": "Lossless decompression preserves the encoded byte sequence, not domain meaning, authenticity, safety, bounded resource use or semantic validity.",
    },
    {
        "source_id": "source.representation.rfc4648",
        "title": "RFC 4648: Base-N Encodings",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc4648.html",
        "bounded_implication": "Base encodings define alphabets, padding and canonical encoding rules for transporting octets in restricted textual carriers.",
        "authority_limit": "Base encoding is a carrier transform; it supplies neither compression, encryption, integrity, semantic type nor domain identity.",
    },
]


ARCHETYPES = [
    ("owned_domain_meaning", "Bounded-context meaning and invariants represented elsewhere but never owned by a carrier."),
    ("published_language_or_profile", "Editioned semantic contract intentionally exposed across a context boundary."),
    ("vocabulary_ontology_or_term", "Named concept/relation vocabulary with explicit namespace, edition and interpretation."),
    ("logical_schema", "Logical field/type/relationship shape independent of one physical layout."),
    ("constraint_schema", "Dialect/profile expressing structural assertions, annotations or validation constraints."),
    ("api_contract", "Operation and message description at an integration boundary."),
    ("ir_ast_or_plan", "Structured intermediate representation for syntax, semantics, plans or lowering."),
    ("dto_or_message", "Boundary transfer object or message representation, not the domain entity itself."),
    ("scalar_carrier", "Primitive carrier with width, signedness, range, precision, scale or lexical rules."),
    ("record_or_object", "Named or structural collection of fields/properties."),
    ("collection_or_sequence", "Repeated values with explicit multiplicity, order and boundedness."),
    ("map_or_dictionary", "Key/value representation with key equality, ordering and duplicate-key policy."),
    ("table_row_or_relation", "Tabular logical representation with rows, columns, nullability and constraints."),
    ("graph", "Node/edge/property representation with identifiers, incidence and direction."),
    ("document", "Tree, mixed-content or document-oriented representation."),
    ("event_envelope", "Occurrence payload plus transport/context metadata and edition."),
    ("time_series", "Time-indexed observation representation with sampling and time-basis metadata."),
    ("spatial_representation", "Geometry, topology or raster carrier with reference-system metadata."),
    ("tensor_or_array", "Ranked multidimensional representation with shape, element type, strides and layout."),
    ("media_representation", "Image, audio, video or compound-media representation and profile."),
    ("opaque_blob", "Bytes intentionally uninterpreted at the current boundary."),
    ("in_memory_layout", "Runtime memory organization, alignment, offsets, ownership and validity."),
    ("row_layout", "Physical record-contiguous organization."),
    ("columnar_layout", "Physical column-contiguous organization with buffers and validity metadata."),
    ("buffer", "Contiguous or segmented byte region with ownership, lifetime, alignment and bounds."),
    ("page_block_or_chunk", "Finite subdivision for encoding, transfer, access, recovery or scheduling."),
    ("file_or_object", "Persisted object representation with identity, length, metadata and edition."),
    ("container", "Compound format packaging payloads, indexes, metadata or nested representations."),
    ("frame_or_envelope", "Self-delimiting transport/stream unit with boundaries and control metadata."),
    ("header_or_metadata", "Representation-describing fields distinct from the represented payload meaning."),
    ("wire_protocol", "On-the-wire grammar, message sequencing and negotiation contract."),
    ("abi_or_calling_convention", "Binary calling, layout, ownership and linkage boundary."),
    ("language_binding", "Generated or hand-written language view over an external interface."),
    ("provider_or_legacy_adapter", "Replaceable translation at a provider or foreign-model boundary."),
    ("codec", "Typed bidirectional or directional transformation between representation domains."),
    ("charset_or_text_encoding", "Mapping between abstract text/code points and code-unit/octet sequences."),
    ("canonicalization_profile", "Scoped rules selecting a deterministic representative encoding."),
    ("compression_envelope", "Compressed representation with algorithm, parameters, dictionary and limits."),
    ("protection_envelope", "Encrypted, authenticated or otherwise protected representation with key/context metadata."),
    ("checksum_or_digest", "Scoped integrity/content-address witness over exact bytes and algorithm profile."),
    ("content_or_media_type", "Negotiated label for representation syntax/profile and processing expectations."),
    ("extension_or_unknown_field", "Unrecognized or separately governed representation element and preservation behavior."),
    ("schema_identifier_or_reference", "Identifier/reference resolving an exact schema resource, dialect or edition."),
    ("dictionary_encoding", "Value-to-index physical encoding with dictionary identity and ordering rules."),
    ("index_or_pruning_metadata", "Auxiliary access/statistics representation with validity and false-positive/negative contract."),
    ("opaque_handle", "Capability/reference token whose internal representation and lifecycle are hidden."),
    ("zero_copy_view", "Borrowed/shared physical view with declared ownership, lifetime, aliasing and mutation constraints."),
    ("versioned_representation_artifact", "Immutable identified representation edition with provenance and compatibility relations."),
]


KERNELS = [
    "bind_owned_meaning", "publish_semantic_profile", "define_vocabulary", "resolve_term",
    "define_logical_schema", "resolve_schema", "validate_schema_dialect", "validate_instance",
    "validate_domain_invariants", "parse", "format", "encode", "decode", "serialize",
    "deserialize", "transcode", "frame", "unframe", "pack_container", "unpack_container",
    "compress", "decompress", "encrypt", "decrypt", "canonicalize", "verify_canonical_form",
    "calculate_checksum", "verify_checksum", "negotiate_content", "probe_format", "sniff_format",
    "project", "coerce", "apply_default", "normalize", "preserve_unknown_fields",
    "drop_unknown_with_residual", "apply_extension_profile", "map_stable_identifiers", "map_names",
    "row_to_column", "column_to_row", "pack_buffer", "unpack_buffer", "chunk",
    "reassemble_chunks", "stream", "random_access_read", "memory_map", "copy",
    "create_zero_copy_view", "marshal_ffi", "unmarshal_ffi", "generate_language_binding",
    "invoke_provider_adapter", "dictionary_encode", "dictionary_decode", "convert_endianness",
    "convert_numeric_carrier", "refuse_lossy_conversion",
]


def archetypes() -> list[dict]:
    return [
        {
            "record_kind": "representation_bearer_archetype",
            "archetype_id": f"archetype.representation.{name.replace('_', '-')}.v1",
            "meaning": meaning,
            "applicability": "UNRESOLVED_PER_MEANING_BINDING_DIRECTION_PROFILE_AND_USE_SITE",
            "completion_claim": False,
        }
        for name, meaning in ARCHETYPES
    ]


def kernels() -> list[dict]:
    return [
        {
            "record_kind": "representation_operation_kernel",
            "kernel_id": f"kernel.representation.{name.replace('_', '-')}.v1",
            "operation": name,
            "required_input": "EXACT_SOURCE_MEANING_SOURCE_REPRESENTATION_TARGET_REPRESENTATION_DIRECTION_PROFILE_AND_RESOURCE_LIMITS",
            "required_output": "TYPED_PRESERVATION_OUTCOME_WITH_LOSS_RESIDUAL_UNKNOWN_FIELDS_AND_CONFORMANCE_EVIDENCE",
            "effect_classification": "PURE_TRANSFORM_OR_EFFECTFUL_IO_ADAPTER_BOUNDARY_MUST_BE_DECLARED",
            "completion_claim": False,
        }
        for name in KERNELS
    ]


ONTOLOGY = {
    "ontology_id": "ontology.semantic-axis.representation-coordinate.v1",
    "edition": 1,
    "as_of": AS_OF,
    "axis": "representation",
    "domain_question": "Which exact bounded-context meaning is carried by which published profile, schema, carrier, physical layout, container, codec, wire/ABI binding or adapter, in which direction and under what preservation, loss, residual, resource and conformance contract?",
    "coordinate_key": [
        "bounded_context_ref", "owned_meaning_ref", "source_representation_ref",
        "target_representation_ref", "direction", "representation_profile_ref",
        "binding_or_adapter_ref", "use_site_ref",
    ],
    "representation_layers": [
        "owned_domain_meaning_and_invariants", "published_language_or_semantic_profile",
        "logical_schema_and_constraints", "representation_binding", "carrier_and_physical_layout",
        "container_framing_and_metadata", "codec_and_canonicalization_profile",
        "wire_dto_or_api_contract", "language_or_abi_binding", "provider_or_legacy_adapter",
    ],
    "required_coordinate_fields": [
        "source_meaning_identity_and_edition", "source_and_target_representation_identity_and_edition",
        "direction_and_supported_shape_profile_subset", "carrier_type_width_range_precision_scale_and_lexical_space",
        "logical_schema_dialect_constraints_and_reference_resolution", "physical_layout_buffers_offsets_alignment_endianness_and_ownership",
        "container_frame_header_metadata_and_content_type", "codec_algorithm_parameters_dictionary_and_canonicalization_profile",
        "identity_equality_grain_and_cardinality_preservation", "state_time_order_and_topology_preservation",
        "partiality_uncertainty_null_presence_default_and_unknown_field_behavior", "authority_privacy_security_and_safety_preservation",
        "units_reference_system_locale_collation_and_normalization", "coercion_truncation_rounding_imputation_and_overflow_behavior",
        "extension_negotiation_passthrough_understanding_and_enforcement", "loss_classification_typed_residual_and_accepting_owner",
        "size_depth_allocation_expansion_ratio_and_streaming_limits", "determinism_canonical_bytes_and_digest_scope",
        "roundtrip_semantic_and_representation_conformance_oracles", "schema_binding_provider_and_generated_code_removal_seams",
        "error_precedence_corruption_recovery_and_ambiguous_format_behavior", "evidence_edition_environment_and_invalidation_conditions",
    ],
    "required_outcomes": [
        "exactly_preserved", "preserved_under_declared_profile", "projected_with_residual",
        "lossy_with_explicit_acceptance", "opaque_passthrough", "unsupported", "ambiguous",
        "indeterminate", "corrupt", "resource_exhausted", "refused",
    ],
    "non_collapse_laws": [
        "domain_meaning_is_not_schema_dto_field_name_or_storage_type",
        "published_language_is_not_provider_wire_format",
        "logical_schema_is_not_constraint_schema_or_physical_layout",
        "carrier_equality_is_not_value_equality_or_domain_equivalence",
        "schema_syntax_validity_instance_validity_and_aggregate_validity_are_distinct",
        "successful_decode_is_not_semantic_preservation",
        "roundtrip_bytes_are_not_roundtrip_meaning_without_a_preservation_profile",
        "canonicalization_is_profile_scoped_and_does_not_create_domain_identity",
        "defaulting_coercion_truncation_rounding_normalization_and_imputation_are_transforms",
        "unknown_field_preservation_is_not_understanding_validation_or_enforcement",
        "extension_passthrough_does_not_confer_extension_semantics",
        "field_column_serialization_event_temporal_and_causal_order_are_distinct",
        "zero_copy_is_a_physical_property_not_a_semantic_guarantee",
        "compression_encryption_base_encoding_checksums_and_canonicalization_are_distinct",
        "content_type_label_negotiation_parse_success_and_payload_conformance_are_distinct",
        "generated_language_ffi_and_provider_bindings_are_adapters_not_semantic_owners",
        "stable_field_identity_is_not_field_name_position_or_domain_entity_identity",
        "lossless_byte_transform_is_not_meaning_preservation",
        "every_lossy_or_partial_conversion_emits_a_typed_residual_or_refuses",
        "format_codec_provider_and_legacy_adapters_remain_replaceable_at_the_boundary",
    ],
    "compiler_refusals": [
        "REFUSE_UNBOUND_OWNED_MEANING_OR_REPRESENTATION_EDITION",
        "REFUSE_AMBIGUOUS_DIRECTION_PROFILE_DIALECT_OR_CONTENT_TYPE",
        "REFUSE_SCHEMA_SUCCESS_AS_DOMAIN_INVARIANT_PROOF",
        "REFUSE_DECODE_OR_ROUNDTRIP_AS_SEMANTIC_PRESERVATION",
        "REFUSE_UNDECLARED_COERCION_DEFAULT_NORMALIZATION_OR_UNKNOWN_FIELD_POLICY",
        "REFUSE_LOSS_WITHOUT_TYPED_RESIDUAL_AND_ACCEPTING_OWNER",
        "REFUSE_CANONICAL_BYTES_AS_DOMAIN_IDENTITY",
        "REFUSE_UNBOUNDED_ALLOCATION_DEPTH_OR_DECOMPRESSION",
        "REFUSE_GENERATED_BINDING_OR_PROVIDER_ADAPTER_AS_MEANING_OWNER",
    ],
    "status": "STRUCTURAL_COORDINATE_ONTOLOGY_DECISIONS_OPEN",
    "completion_claim": False,
}


def route(facets: tuple[str, ...]) -> str:
    if not facets:
        return "NO_DISCOVERY_SIGNAL_REQUIRES_FULL_REPRESENTATION_LAYER_AND_BINDING_INVENTORY"
    facet_set = set(facets)
    if "physical_layout" in facet_set:
        return "LAYOUT_SIGNAL_REQUIRES_LOGICAL_PHYSICAL_BUFFER_CODEC_AND_PRESERVATION_RESEARCH"
    if "wire_protocol_or_dto" in facet_set:
        return "WIRE_OR_DTO_SIGNAL_REQUIRES_MEANING_SCHEMA_CARRIER_UNKNOWN_FIELD_AND_ADAPTER_RESEARCH"
    if "encoded_bytes_or_container" in facet_set:
        return "ENCODED_OR_CONTAINER_SIGNAL_REQUIRES_FRAMING_CODEC_LIMITS_CANONICALIZATION_AND_LOSS_RESEARCH"
    if "logical_schema" in facet_set:
        return "LOGICAL_SCHEMA_SIGNAL_REQUIRES_DIALECT_CONSTRAINT_MEANING_AND_PHYSICAL_BINDING_RESEARCH"
    if "published_language_or_profile" in facet_set:
        return "PUBLISHED_PROFILE_SIGNAL_REQUIRES_MEANING_EDITION_SUBSET_BINDING_AND_CONFORMANCE_RESEARCH"
    if "semantic_native" in facet_set:
        return "SEMANTIC_NATIVE_SIGNAL_REQUIRES_EXPLICIT_EXTERNAL_REPRESENTATION_AND_PRESERVATION_RESEARCH"
    return "LEXICAL_REPRESENTATION_SIGNAL_REQUIRES_COMPLETE_LAYER_AND_BINDING_RESEARCH"


def build() -> dict:
    return build_package(
        axis="representation",
        preclassifications_path=PRECLASSIFICATIONS,
        docket_prefix="docket.representation-coordinate",
        docket_record_kind="representation_structural_rebase_docket",
        cluster_prefix="cluster.representation-coordinate-rebase",
        cluster_record_kind="representation_member_research_cluster",
        member_record_kind="representation_member_research_route",
        member_route_prefix="route.representation-coordinate",
        extension_record_kind="representation_exact_contract_extension_candidate",
        extension_prefix="extension.representation-coordinate",
        route_for_facets=route,
        cluster_next_evidence=[
            "authoritative per-use-site owned-meaning and representation-layer inventory",
            "source/target editions direction profile and complete preservation obligations",
            "coercion default normalization unknown-field extension and typed-loss behavior",
            "resource corruption recovery adapter-removal and conformance oracles",
        ],
        member_open_fields={
            "required_representation_layer_inventory": "NOT_YET_SUPPLIED",
            "required_directional_preservation_profile": "NOT_YET_SUPPLIED",
            "required_loss_resource_adapter_and_conformance_contract": "NOT_YET_SUPPLIED",
        },
        extension_record_kinds=[
            "representation_layer_inventory", "meaning_to_representation_binding",
            "carrier_layout_container_and_codec_profile", "directional_preservation_obligation_set",
            "coercion_default_unknown_field_and_extension_policy", "typed_loss_and_residual_contract",
            "resource_corruption_and_recovery_contract", "adapter_removal_and_conformance_oracle",
        ],
        ontology=ONTOLOGY,
        sources=SOURCES,
        archetypes=archetypes(),
        kernels=kernels(),
        summary_base={
            "program_id": "program.representation-coordinate-ontology-and-rebase.v1",
            "as_of": AS_OF,
            "axis": "representation",
            "representation_bearer_archetypes": len(ARCHETYPES),
            "representation_operation_kernels": len(KERNELS),
            "representation_layer_inventories_supplied": 0,
            "directional_preservation_profiles_supplied": 0,
        },
        lexical_summary_key="routes_with_lexical_representation_projection",
        vacancy_summary_key="routes_with_no_representation_projection",
    )


def outputs() -> dict[str, str]:
    return render_outputs(
        built=build(),
        ontology_filename="representation-coordinate-ontology.json",
        archetypes_filename="representation-bearer-archetypes.jsonl",
        kernels_filename="representation-operation-kernels.jsonl",
        members_filename="member-representation-routes.jsonl",
        manifest_id="manifest.representation-coordinate-ontology-and-rebase.v1",
        as_of=AS_OF,
    )


def main() -> int:
    for name, payload in outputs().items():
        (HERE / name).write_text(payload)
    summary = build()["summary"]
    print(
        "BUILD PASS representation coordinate ontology: "
        f"{summary['representation_bearer_archetypes']} bearers, "
        f"{summary['representation_operation_kernels']} kernels, "
        f"{summary['research_clusters']} clusters and "
        f"{summary['target_member_routes']} exact routes; decisions remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
