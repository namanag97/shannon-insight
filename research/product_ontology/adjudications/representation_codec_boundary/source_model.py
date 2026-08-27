#!/usr/bin/env python3
"""Adjudicate codec-as-a-service as representation libraries/runtime, not product."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"


def ev(ident: str, title: str, publisher: str, uri: str, claim: str, limit: str) -> dict[str, Any]:
    return {"source_id": f"evidence.rcb.{ident}", "source_class": "official_specification_or_documentation", "title": title, "publisher": publisher, "uri": uri, "retrieved_at": "2026-08-26", "claim": claim, "scope_limit": limit}


def refs(*idents: str) -> list[str]:
    return [f"evidence.rcb.{ident}" for ident in idents]


def art(ident: str, kind: str, name: str, definition: str, evidence: list[str], owner: str | None = None) -> dict[str, Any]:
    return {"artifact_id": ident, "kind": kind, "name": name, "status": "candidate", "semantic_owner_ref": owner, "adoption_unit": False, "operated": False, "definition": definition, "evidence_refs": evidence}


SOURCES = [
    ("arrow", "Apache Arrow Columnar Format", "Apache Arrow", "https://arrow.apache.org/docs/format/Columnar.html", "Defines physical layouts, buffers, dictionaries, IPC framing and named compression profiles.", "Arrow layout and codec support do not own business type or product lifecycle."),
    ("arrow_security", "Apache Arrow Format Security", "Apache Arrow", "https://arrow.apache.org/docs/format/Security.html", "Documents untrusted-input, validation and resource-exhaustion concerns.", "Guidance does not qualify a particular implementation or deployment."),
    ("zstd", "RFC 8878 Zstandard", "IETF", "https://www.rfc-editor.org/rfc/rfc8878.html", "Defines the Zstandard lossless compressed data format, frames, dictionaries and errors.", "It does not define random access, provider selection or a service product."),
    ("cbor", "RFC 8949 CBOR", "IETF", "https://www.rfc-editor.org/rfc/rfc8949.html", "Defines the CBOR data model, encodings and deterministic encoding requirements.", "Deterministic encoding is profile-scoped and not semantic identity by itself."),
    ("parquet", "Apache Parquet Format", "Apache Parquet", "https://parquet.apache.org/docs/file-format/", "Defines column chunks, pages, encodings, compression and file metadata.", "Parquet does not own table transaction or business semantics."),
    ("orc", "Apache ORC Specification", "Apache ORC", "https://orc.apache.org/specification/", "Defines stripes, streams, encodings, indexes and compression blocks.", "ORC format support does not establish provider qualification or optimality."),
    ("avro", "Apache Avro Specification", "Apache Avro", "https://avro.apache.org/docs/current/specification/", "Defines binary encoding, schema resolution, object containers and codecs.", "Schema resolution is not universal semantic compatibility."),
    ("protobuf", "Protocol Buffers Encoding", "Google", "https://protobuf.dev/programming-guides/encoding/", "Defines protobuf wire types and field encoding.", "Wire compatibility and deterministic serialization do not prove canonical semantic identity."),
    ("png", "Portable Network Graphics Specification Third Edition", "W3C", "https://www.w3.org/TR/png-3/", "Defines PNG image model, chunks, filters, compression and conformance.", "A bundled media format still contains separable representation contracts."),
    ("zarr", "Zarr Storage Specification 3", "Zarr", "https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html", "Defines chunked array metadata, codecs, storage transformers and nodes.", "Zarr profiles do not select a codec for every workload or prove loss acceptance."),
    ("jpeg", "JPEG 1", "JPEG", "https://jpeg.org/jpeg/", "Defines a family of still-image coding standards and conformance ecosystem.", "A codec family does not define a universal perceptual acceptance metric."),
    ("unicode", "Unicode Standard", "Unicode Consortium", "https://www.unicode.org/versions/latest/", "Defines characters, encoding forms and conformance requirements.", "Character encoding is not semantic text language or business meaning."),
]


# suffix, name, operation, decision, invariant, refusal, concrete library, evidence
LIBS = [
    ("carrier_contract", "Carrier and framing contract", "validate_carrier", "carrier_seek_stream_and_frame_profile", "carrier_capabilities_are_explicit_and_do_not_follow_from_file_suffix", "carrier_contract_unknown", "library.san_stream_codec", ["arrow", "zstd", "zarr"]),
    ("codec_kernel", "Codec kernel contract", "encode_or_decode", "codec_edition_profile_direction_and_target", "decode_is_bounded_total_over_the_declared_profile_or_refuses", "codec_profile_unsupported", "library.san_codec_kernel", ["zstd", "png", "jpeg"]),
    ("codec_provider", "Codec provider boundary", "qualify_codec_provider", "implementation_version_target_and_limits", "algorithm_or_format_identity_never_selects_a_provider_by_name", "codec_provider_unqualified", "library.san_codec_provider", ["arrow", "zstd"]),
    ("codec_runtime", "Codec runtime", "execute_codec_invocation", "budget_cancellation_memory_and_receipt", "runtime_effects_do_not_acquire_payload_semantics", "codec_runtime_failed", "library.san_codec_runtime", ["arrow_security", "zstd"]),
    ("compression_contract", "Compression contract", "compress_or_decompress", "losslessness_dictionary_frame_and_access_profile", "compression_algorithm_layout_column_encoding_and_codec_are_distinct", "compression_contract_incompatible", "library.san_compression_contract", ["zstd", "parquet", "orc"]),
    ("loss_contract", "Loss and fidelity contract", "verify_decoded_fidelity", "equality_error_metric_units_population_and_authority", "lossy_output_requires_an_explicit_finite_accepted_profile_and_oracle", "loss_profile_unbound", "library.san_loss_contract", ["jpeg", "png"]),
    ("transcode_plan", "Transcode plan", "compile_transcode", "source_target_intermediate_loss_and_metadata", "every_transcode_reports_semantic_and_representation_loss", "transcode_loss_unproved", "library.san_transcode_plan", ["avro", "protobuf", "zarr"]),
    ("canonical_representation", "Canonical representation profile", "canonicalize_representation", "profile_edition_and_equivalence_scope", "deterministic_bytes_are_not_business_identity_or_truth", "canonical_profile_missing", "library.san_canonical", ["cbor", "protobuf"]),
]


GAPS = [
    ("provider_conformance", "Exact profile/target/resource conformance is missing for many codec providers."),
    ("resource_bounds", "Worst-case memory, CPU, expansion and cancellation behavior are often undocumented or input-dependent."),
    ("dictionary_lifecycle", "Dictionary identity, distribution, revocation and cache coherence lack one portable contract."),
    ("random_access", "Streaming, restartability, splittability and random access are frequently conflated."),
    ("loss_interchange", "Loss/error/perceptual/task acceptance profiles lack a universal interchange model."),
    ("transcode_loss", "Cross-format transcodes rarely emit complete semantic and representation loss receipts."),
    ("canonicalization", "Deterministic provider output is often mistaken for stable cross-version canonicalization."),
    ("hardware_equivalence", "CPU, SIMD, GPU and accelerator implementations need bitwise or bounded-result equivalence evidence."),
    ("security_bombs", "Expansion bombs, malformed nesting and crafted metadata require format-specific bounded validation."),
    ("two_implementations", "Critical codec/library contracts still need two independent qualified implementations and shared law oracles."),
]


def source() -> dict[str, Any]:
    sources = [ev(*row) for row in SOURCES]
    kinds = [
        {"kind": "architecture_pattern", "definition": "Recurring packaging or deployment shape; not a product or semantic owner."},
        {"kind": "control_component", "definition": "Runtime or policy component inside a consuming product."},
        {"kind": "semantic_contract", "definition": "Owner of representation identity, laws, decisions and refusals."},
        {"kind": "capability", "definition": "Typed operation provided under a semantic contract."},
        {"kind": "standard", "definition": "Editioned external representation specification."},
        {"kind": "implementation", "definition": "Observed unqualified implementation or provider."},
        {"kind": "neighbor", "definition": "Adjacent owner imported through a typed boundary."},
    ]
    artifacts = [
        art("pattern.codec_as_service", "architecture_pattern", "Codec-as-a-Service", "An operational wrapper around reusable representation libraries and qualified runtime offers; no independent enterprise outcome or semantic authority is proven.", refs("arrow", "zstd", "zarr")),
        art("component.codec_runtime", "control_component", "Codec runtime component", "Bounded encode, decode or transcode execution with budgets, cancellation and receipts inside a consuming product.", refs("arrow_security", "zstd")),
        art("component.optional_codec_assistance", "control_component", "Optional codec configuration assistance", "Removable model/agent proposal surface for configuration search; it cannot select providers, authorize loss, bypass validation or execute effects.", refs("cbor", "zstd")),
        art("standard.arrow", "standard", "Apache Arrow format", "Columnar representation and IPC specification.", refs("arrow")),
        art("standard.zstd", "standard", "Zstandard format", "Lossless compression format and algorithm profile.", refs("zstd")),
        art("standard.cbor", "standard", "CBOR", "Binary data model and encoding with deterministic profiles.", refs("cbor")),
        art("implementation.arrow_libraries", "implementation", "Apache Arrow implementations", "Observed multi-language format and codec implementations; unqualified here.", refs("arrow", "arrow_security")),
        art("implementation.zstd_reference", "implementation", "Zstandard reference implementation", "Observed codec implementation; unqualified here.", refs("zstd")),
        art("neighbor.semantic_type", "neighbor", "Semantic type system", "Owns value meaning, equality, units, missingness and domain constraints.", refs("arrow", "unicode")),
        art("neighbor.storage_layout", "neighbor", "Storage and layout", "Owns object/page/stripe/chunk placement and persistence lifecycle.", refs("parquet", "orc", "zarr")),
        art("neighbor.runtime_resource", "neighbor", "Runtime and resource control", "Owns scheduling, memory, CPU/GPU, cancellation and isolation guarantees.", refs("arrow_security", "zstd")),
        art("neighbor.security_policy", "neighbor", "Security and authorization", "Owns permission, key use, trust and effect authorization.", refs("arrow_security")),
    ]
    ownership = []
    libraries = []
    requirements = []
    maps = []
    for suffix, name, operation, decision, invariant, refusal, concrete, evidence_ids in LIBS:
        owner = f"semantic.rcb.{suffix}"
        capability = f"capability.rcb.{suffix}"
        evidence = refs(*evidence_ids)
        artifacts.append(art(owner, "semantic_contract", name, f"Owns {name.lower()} decisions, laws and refusals.", evidence))
        artifacts.append(art(capability, "capability", operation.replace("_", " ").title(), f"Typed capability to {operation.replace('_', ' ')}.", evidence, owner=owner))
        ownership.append({"meaning_id": f"meaning.rcb.{suffix}", "term": name, "owner_ref": owner, "invariant": invariant, "must_not_be_owned_by": ["pattern.codec_as_service", "component.codec_runtime", "neighbor.semantic_type"]})
        abstract = f"library.adjudicated.rcb.{suffix}"
        libraries.append({"library_id": abstract, "class": "runtime_boundary" if suffix == "codec_runtime" else "semantic_pure", "owner_ref": owner, "provides": [capability], "types": [f"{suffix.title().replace('_', '')}Request", f"{suffix.title().replace('_', '')}Result", f"{suffix.title().replace('_', '')}Refusal"], "operations": [operation], "decisions": [decision], "invariants": [invariant, "provider_name_never_changes_representation_semantics", "model_or_agent_output_cannot_select_loss_authority_or_bypass_validation"], "refusals": [refusal, "resource_exhausted", "unsupported_profile"], "dependencies": [], "effect_boundary": "effect_intents_and_receipts" if suffix == "codec_runtime" else "pure_no_io", "evidence_refs": evidence})
        requirements.append({"requirement_id": f"requirement.rcb.{suffix}", "consumer_ref": "component.codec_runtime", "capability_ref": capability, "minimum_qualified_offers": 2, "binding_phase": "deployment_time" if suffix in {"codec_provider", "codec_runtime"} else "compile_time", "status": "unbound", "refusal": "refuse when no exact qualified profile/target offer exists"})
        maps.append({"binding_map_id": f"binding.rcb.{suffix}", "abstract_library_ref": abstract, "compiler_disposition": "structurally_projected_unqualified", "concrete_library_refs": [concrete], "gap_ref": None, "portable_offer": False})

    decisions = [
        {"decision_id": "decision.rcb.codec_service", "subject_ref": "pattern.codec_as_service", "disposition": "reclassify_as_library_runtime_component", "rationale": "Encoding/decoding is normally a reusable library/kernel contract; an optional operated wrapper owns availability and budgets but lacks an independently adopted enterprise outcome, semantic authority and exit boundary.", "evidence_refs": refs("arrow", "zstd", "zarr")},
        {"decision_id": "decision.rcb.runtime", "subject_ref": "component.codec_runtime", "disposition": "retain_as_control_component", "rationale": "Runtime execution is useful and effect-bounded but remains inside storage, movement, query, media or other consuming products.", "evidence_refs": refs("arrow_security", "zstd")},
        {"decision_id": "decision.rcb.agent", "subject_ref": "component.optional_codec_assistance", "disposition": "optional_non_authoritative_extension", "rationale": "Models may propose configuration only when requested; exact profile validation, provider qualification, loss authority, execution and verification remain deterministic.", "evidence_refs": refs("cbor", "zstd")},
    ]
    offers = [
        {"offer_id": "offer.rcb.arrow", "provider_ref": "implementation.arrow_libraries", "capability_refs": ["capability.rcb.carrier_contract", "capability.rcb.codec_kernel", "capability.rcb.codec_runtime"], "status": "observed_unqualified", "qualified_implementation_count": 0, "portable": False, "evidence_refs": refs("arrow", "arrow_security")},
        {"offer_id": "offer.rcb.zstd", "provider_ref": "implementation.zstd_reference", "capability_refs": ["capability.rcb.codec_kernel", "capability.rcb.codec_provider", "capability.rcb.compression_contract"], "status": "observed_unqualified", "qualified_implementation_count": 0, "portable": False, "evidence_refs": refs("zstd")},
    ]
    relations = [
        {"relation_id": "relation.rcb.pattern_packages_runtime", "from_ref": "pattern.codec_as_service", "predicate": "packages", "to_ref": "component.codec_runtime", "binding_phase": "deployment_time"},
        {"relation_id": "relation.rcb.runtime_requires_resources", "from_ref": "component.codec_runtime", "predicate": "requires", "to_ref": "neighbor.runtime_resource", "binding_phase": "runtime"},
        {"relation_id": "relation.rcb.runtime_imports_semantics", "from_ref": "component.codec_runtime", "predicate": "requires", "to_ref": "neighbor.semantic_type", "binding_phase": "compile_time"},
        {"relation_id": "relation.rcb.runtime_imports_layout", "from_ref": "component.codec_runtime", "predicate": "requires", "to_ref": "neighbor.storage_layout", "binding_phase": "compile_time"},
    ]
    crosswalks = [
        {"legacy_ref": "candidate.product.codec_service", "canonical_refs": ["pattern.codec_as_service", "component.codec_runtime"], "disposition": "reclassify_as_library_runtime_component"},
        {"legacy_ref": "term.codec", "canonical_refs": ["semantic.rcb.codec_kernel", "semantic.rcb.compression_contract", "semantic.rcb.loss_contract"], "disposition": "split_codec_compression_and_loss"},
    ]
    negatives = [
        ("codec_product", "every encode/decode operation is an enterprise product", "retain library/kernel semantics and optional runtime component"),
        ("algorithm_provider", "algorithm name selects a provider", "bind an exact qualified version/profile/target offer"),
        ("format_semantics", "file format owns business meaning", "import semantic type and domain contracts"),
        ("suffix_type", "file suffix proves type or codec", "validate exact carrier and format evidence"),
        ("deterministic_canonical", "deterministic serialization is universally canonical", "bind a canonical profile and equivalence scope"),
        ("digest_identity", "digest of bytes is business identity", "keep content identity and domain identity distinct"),
        ("checksum_signature", "checksum is a signature", "retain integrity-detection and authenticated-issuer contracts separately"),
        ("compression_layout", "compression algorithm is physical layout", "type compression and layout independently"),
        ("column_codec", "column encoding is a general compressor", "preserve the transform pipeline stages"),
        ("stream_random", "streamable means splittable or random access", "declare each access trait and prerequisites"),
        ("range_random", "range-readable carrier makes compressed content random access", "prove independent decode units and dependencies"),
        ("dictionary_inline", "dictionary ID guarantees dictionary availability or identity", "bind exact dictionary artifact and lifecycle"),
        ("lossy_default", "lossy mode can be selected by cost optimization alone", "require finite loss profile, authority and decoded-output oracle"),
        ("lossless_name", "provider lossless label proves equality", "run the declared equality oracle over qualified profiles"),
        ("transcode_silent", "transcode may drop unsupported semantics silently", "emit typed loss or refuse"),
        ("gpu_name", "GPU codec is compatible because the algorithm name matches", "qualify profile, memory space, limits, cancellation and result equivalence"),
        ("double_compress", "more compression layers always improve cost", "model expansion, CPU, access and latency trade-offs"),
        ("provider_docs", "official docs qualify provider behavior", "require executable conformance and resource evidence"),
        ("agent_select", "agent may choose lossy settings or provider from prose", "compile typed intent and require authority/qualification"),
        ("ai_codec", "AI codec creates a new representation product", "model exact codec/loss method without changing product boundaries"),
    ]
    return {
        "contract_id": "contract.product_adjudication.representation_codec_boundary.v0_1_0",
        "edition": 1,
        "status": "evidence_backed_adjudicated_candidate_not_ratified",
        "scope": "Carrier, encoding, codec, compression, loss, canonicalization, transcode, provider and runtime boundaries for data representation.",
        "negative_scope": "Does not own semantic data meaning, storage/product lifecycle, security authority, runtime scheduling or independent enterprise product outcomes.",
        "artifact_kinds": kinds,
        "sources": sources,
        "artifacts": artifacts,
        "boundary_decisions": decisions,
        "ownership": ownership,
        "libraries": libraries,
        "requirements": requirements,
        "offers": offers,
        "relations": relations,
        "crosswalks": crosswalks,
        "negative_tests": [{"test_id": f"negative.rcb.{ident}", "prohibited_claim": claim, "expected_result": result} for ident, claim, result in negatives],
        "binding_maps": maps,
        "binding_gaps": [],
        "semantic_gaps": [{"gap_id": f"gap.rcb.{ident}", "gap_class": "semantic_or_conformance", "statement": statement, "blocking": True, "closure_evidence": "Exact edition/profile contract, executable law oracle and two independent qualified implementations."} for ident, statement in GAPS],
        "non_collapse_laws": [
            "semantic type != carrier != serialization != framing != layout != column encoding != compression != codec != container",
            "algorithm/format identity != provider identity != qualified offer != runtime occurrence",
            "lossless claim != proved equality; lossy configuration != accepted loss authority",
            "deterministic serialization != universal canonicalization != business identity",
            "codec library/runtime component != independently adopted enterprise product",
            "optional models or agents cannot select providers, authorize loss, bypass validation or own execution receipts",
        ],
    }


def source_bytes() -> bytes:
    return (json.dumps(source(), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


if __name__ == "__main__":
    SOURCE.write_bytes(source_bytes())
