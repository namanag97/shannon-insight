#!/usr/bin/env python3
"""Build the adversarial data-modality coverage audit deterministically.

This is deliberately an audit of ``../data_shapes`` rather than a second registry.
Every mapping is declared in ``FAMILY_SPECS``; the builder never matches names.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CANONICAL = ROOT.parent / "data_shapes"
AS_OF = "2026-08-25"
RELATIONS = {"equivalent", "narrower", "broader", "overlap", "disjoint", "missing"}


def dump_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def dump_jsonl(path: Path, values: list[dict]) -> None:
    path.write_text("".join(json.dumps(v, sort_keys=True, ensure_ascii=False) + "\n" for v in values))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


AXES = [
    ("abstraction_layer", "layer", ["semantic_meaning", "observation_record_shape", "modality", "logical_topology", "carrier", "encoding", "container_file_format", "physical_layout", "compression_protection"], "A lower representation layer never proves a higher semantic layer."),
    ("schema_posture", "interpretation", ["strongly_schema_bound", "externally_profiled", "self_describing", "schema_on_read", "weakly_declared", "mixed", "opaque"], "'Unstructured' means a weak or deferred schema/interpretation posture, never absence of structure."),
    ("modality", "logical", ["scalar", "categorical", "text", "binary", "record", "document", "table", "graph", "event", "temporal", "signal", "image", "audio", "video", "spatial", "array", "scientific", "engineering_3d", "genomic", "clinical", "financial", "code", "metadata_evidence", "mixed"], "Modality is independent of source, carrier, codec, and file extension."),
    ("logical_shape", "logical", ["scalar", "optional", "union", "tuple", "record", "sequence", "set", "map", "table", "cube", "tree", "document", "message", "bundle", "graph", "stream", "series", "tensor", "raster", "coverage", "point_set", "mesh", "solid", "scene", "archive", "model", "code_tree", "provenance", "mixed"], "Logical shape does not determine physical layout."),
    ("dimensionality", "structural", ["zero", "one", "two", "three", "four", "n_dimensional", "ragged", "mixed_or_variable", "not_applicable"], "Dimension count does not establish axis meaning."),
    ("logical_topology", "structural", ["none", "linear", "tree", "forest", "directed_graph", "undirected_graph", "multigraph", "dag", "hypergraph", "grid", "mesh", "manifold", "point_set", "coverage_function", "scene_graph", "mixed"], "Topology is distinct from order, geometry, and storage adjacency."),
    ("grain", "semantic", ["value", "field", "record", "row", "cell", "observation", "event", "sample", "pixel", "voxel", "feature", "relationship", "document", "message", "file_member", "model_object", "variant", "transaction", "evidence_item", "mixed"], "Rows, files, and messages do not reveal business grain without a declaration."),
    ("identity_model", "semantic", ["none", "positional", "natural_key", "surrogate_key", "content_address", "uri", "composite", "versioned", "contextual", "standard_defined", "mixed"], "Identity is independent of label, equality, and storage address."),
    ("key_model", "structural", ["none", "candidate", "primary", "foreign", "compound", "partition", "sort", "temporal", "coordinate", "membership", "standard_defined", "mixed"], "A physical index or field number is not automatically a semantic key."),
    ("ordering", "structural", ["none", "incidental", "total_semantic", "partial_semantic", "sequence_number", "event_time", "topological", "spatial_traversal", "document_order", "standard_defined", "mixed"], "Serialized byte order is not semantic order."),
    ("time_role", "temporal", ["none", "event_time", "observation_time", "valid_time", "transaction_time", "recorded_time", "ingestion_time", "processing_time", "publication_time", "media_time", "simulation_time", "mixed"], "Multiple time roles remain named and cannot be collapsed to one timestamp."),
    ("change_model", "temporal", ["immutable", "mutable_in_place", "snapshot", "append_only", "delta", "cdc", "upsert", "retraction", "versioned", "bitemporal", "schema_evolution", "mixed", "unknown"], "Change representation does not prove event semantics or finality."),
    ("missingness", "semantic", ["forbidden", "nullable_unspecified", "typed_absence", "mask", "sentinel", "structural_absence", "censored", "not_applicable", "mixed", "unknown"], "Null, omission, mask, censoring, and structural absence are not interchangeable."),
    ("uncertainty", "semantic", ["none_declared", "quality_flag", "interval", "distribution", "ensemble", "measurement_uncertainty", "censoring", "mixed", "unknown"], "Precision and compression error do not establish epistemic uncertainty."),
    ("coordinate_reference", "semantic", ["none", "pixel", "index", "projected_crs", "geographic_crs", "vertical_crs", "engineering_crs", "temporal_reference", "genomic_reference", "mixed", "required_external"], "Coordinate tuples are uninterpretable without axis order, CRS/reference, and epoch where applicable."),
    ("unit_semantics", "semantic", ["none", "dimensionless", "physical_unit", "currency", "calendar_unit", "sample_rate", "pixel_scale", "mixed", "required_external", "unknown"], "Numeric carrier and scale never establish a quantity kind or unit."),
    ("carrier", "representation", ["boolean", "integer", "float", "decimal", "text", "bytes", "record", "list", "map", "union", "array_buffer", "mixed", "opaque", "standard_defined"], "Carrier representability is weaker than semantic equivalence."),
    ("encoding", "representation", ["none", "utf8", "json", "xml", "yaml", "cbor", "protobuf_wire", "avro_binary", "columnar_binary", "image_codec", "audio_codec", "video_codec", "domain_binary", "mixed", "standard_defined"], "Encoding is not a semantic data type or collection shape."),
    ("container_file_format", "representation", ["none", "single_object", "multipart", "archive", "compound_package", "row_file", "columnar_file", "media_container", "scientific_container", "domain_container", "mixed", "standard_defined"], "A container may carry multiple modalities and does not identify their meaning."),
    ("physical_layout", "physical", ["unspecified", "row_major", "column_major", "columnar", "chunked", "tiled", "scanline", "csr", "csc", "coo", "blocked", "interleaved", "planar", "indexed_offsets", "linked_objects", "mixed", "standard_defined"], "Layout affects access and kernels, not logical identity."),
    ("compression_protection", "representation", ["none", "lossless", "lossy", "encrypted", "signed", "checksummed", "content_addressed", "compressed_and_encrypted", "mixed", "external"], "Compression, encryption, signatures, and checksums are independent contracts."),
    ("access_locality", "physical", ["sequential", "random", "row", "column", "chunk", "tile", "range", "streaming", "graph_traversal", "content_addressed", "mixed", "provider_dependent"], "Access affordance is not semantic ordering."),
    ("evolution", "compatibility", ["none", "append_fields", "field_identity", "versioned_schema", "reader_writer_resolution", "open_world", "closed_world", "profile_defined", "mixed", "unknown"], "Syntactic schema compatibility does not prove semantic compatibility."),
    ("provenance", "evidence", ["absent", "source_reference", "record_level", "field_level", "activity_graph", "custody_chain", "embedded_manifest", "external", "mixed", "required"], "Provenance records a claim and authority; it does not make the claim true."),
    ("integrity", "evidence", ["none", "checksum", "cryptographic_digest", "signature", "merkle", "sequence_gap_detection", "container_validation", "schema_validation", "mixed", "external"], "Integrity proves only its declared byte/object scope."),
    ("authority", "semantic", ["unknown", "source_asserted", "domain_owner", "standards_body", "custodian", "derived", "consensus", "mixed", "not_applicable"], "Authority must be explicit and is not conferred by format conformance."),
]


def source(sid: str, title: str, publisher: str, url: str, year: int | None, category: str, edition: str = "") -> dict:
    return {
        "source_id": sid,
        "title": title,
        "publisher": publisher,
        "url": url,
        "publication_year": year,
        "standard_family": category,
        "edition_or_version": edition or None,
        "authority": "normative_or_primary_official",
        "source_kind": "official_specification",
        "accessed_at": AS_OF,
        "supports": [category, "layer-boundary evidence"],
        "limitations": ["Conformance to this representation does not by itself establish enterprise semantic meaning."],
    }


EXTRA_SOURCES = [
    source("A-SRC-071", "Internet Message Format", "IETF", "https://www.rfc-editor.org/rfc/rfc5322.html", 2008, "email", "RFC 5322"),
    source("A-SRC-072", "MIME Part One: Format of Internet Message Bodies", "IETF", "https://www.rfc-editor.org/rfc/rfc2045.html", 1996, "email_mime", "RFC 2045"),
    source("A-SRC-073", "MIME Part Two: Media Types", "IETF", "https://www.rfc-editor.org/rfc/rfc2046.html", 1996, "email_mime", "RFC 2046"),
    source("A-SRC-074", "The application/mbox Media Type", "IETF", "https://www.rfc-editor.org/rfc/rfc4155.html", 2005, "email_archive", "RFC 4155"),
    source("A-SRC-075", "HTTP Semantics", "IETF", "https://www.rfc-editor.org/rfc/rfc9110.html", 2022, "web", "RFC 9110"),
    source("A-SRC-076", "HTML Living Standard", "WHATWG", "https://html.spec.whatwg.org/", 2026, "web_document", "Living Standard"),
    source("A-SRC-077", "Document Object Model Standard", "WHATWG", "https://dom.spec.whatwg.org/", 2026, "document_tree", "Living Standard"),
    source("A-SRC-078", "Portable Document Format — PDF 2.0", "ISO / PDF Association", "https://pdfa.org/resource/iso-32000-2/", 2020, "fixed_layout_document", "ISO 32000-2:2020"),
    source("A-SRC-079", "PDF/UA-2", "ISO / PDF Association", "https://pdfa.org/resource/iso-14289-2-pdf-ua-2/", 2024, "accessible_document", "ISO 14289-2:2024"),
    source("A-SRC-080", "Office Open XML File Formats", "Ecma International", "https://ecma-international.org/publications-and-standards/standards/ecma-376/", 2021, "office_document", "ECMA-376 5th edition"),
    source("A-SRC-081", "OpenDocument Version 1.3", "OASIS", "https://www.oasis-open.org/standard/open-document-format-for-office-applications-opendocument-version-1-3/", 2021, "office_document", "ODF 1.3"),
    source("A-SRC-082", "EPUB 3.3", "W3C", "https://www.w3.org/TR/epub-33/", 2023, "publication_document", "3.3"),
    source("A-SRC-083", "Portable Network Graphics", "W3C", "https://www.w3.org/TR/png-3/", 2025, "image", "Third Edition"),
    source("A-SRC-084", "TIFF Revision 6.0", "Adobe", "https://developer.adobe.com/content/dam/udp/en/open/standards/tiff/TIFF6.pdf", 1992, "image", "6.0"),
    source("A-SRC-085", "JPEG XL", "ISO/IEC JPEG", "https://jpeg.org/jpegxl/", 2022, "image_codec", "ISO/IEC 18181"),
    source("A-SRC-086", "OpenEXR Technical Introduction", "Academy Software Foundation", "https://openexr.com/en/latest/TechnicalIntroduction.html", 2026, "image_container", "3.x"),
    source("A-SRC-087", "WAVE and AVI Codec Registries", "IETF", "https://www.rfc-editor.org/rfc/rfc2361.html", 1998, "audio_container", "RFC 2361"),
    source("A-SRC-088", "FLAC Format", "Xiph.Org Foundation", "https://xiph.org/flac/format.html", 2025, "audio_codec", "1.5"),
    source("A-SRC-089", "Opus Codec", "IETF", "https://www.rfc-editor.org/rfc/rfc6716.html", 2012, "audio_codec", "RFC 6716"),
    source("A-SRC-090", "AV1 Bitstream and Decoding Process Specification", "Alliance for Open Media", "https://aomediacodec.github.io/av1-spec/av1-spec.pdf", 2023, "video_codec", "1.0.0 with errata"),
    source("A-SRC-091", "WebVTT: The Web Video Text Tracks Format", "W3C", "https://www.w3.org/TR/webvtt1/", 2019, "timed_text", "1"),
    source("A-SRC-092", "WebCodecs", "W3C", "https://www.w3.org/TR/webcodecs/", 2026, "media_api", "Working Draft"),
    source("A-SRC-093", "FITS Standard", "IAU FITS Working Group / NASA", "https://fits.gsfc.nasa.gov/fits_standard.html", 2018, "scientific", "4.0"),
    source("A-SRC-094", "ASAM MDF", "ASAM", "https://www.asam.net/standards/detail/mdf/", 2024, "measurement_signal", "4.3.0"),
    source("A-SRC-095", "OPC Unified Architecture Part 14: PubSub", "OPC Foundation", "https://reference.opcfoundation.org/Core/Part14/", 2025, "industrial_telemetry", "1.05"),
    source("A-SRC-096", "OGC 3D Tiles", "Open Geospatial Consortium", "https://www.ogc.org/standards/3DTiles/", 2022, "geospatial_3d", "1.1"),
    source("A-SRC-097", "CityGML 3.0 Conceptual Model", "Open Geospatial Consortium", "https://docs.ogc.org/is/20-010/20-010.html", 2021, "geospatial_3d", "3.0"),
    source("A-SRC-098", "GeoPackage Encoding Standard", "Open Geospatial Consortium", "https://www.geopackage.org/spec/", 2024, "geospatial_container", "1.4.0"),
    source("A-SRC-099", "SpatioTemporal Asset Catalog Specification", "STAC Project", "https://github.com/radiantearth/stac-spec/tree/master", 2021, "geospatial_catalog", "1.0.0"),
    source("A-SRC-100", "GeoParquet Specification", "GeoParquet / OGC", "https://geoparquet.org/releases/v1.1.0/", 2024, "geospatial_columnar", "1.1.0"),
    source("A-SRC-101", "GeoArrow Specification", "GeoArrow Project", "https://github.com/geoarrow/geoarrow", 2024, "geospatial_memory_layout", "0.2"),
    source("A-SRC-102", "glTF 2.0 Specification", "Khronos Group", "https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html", 2021, "scene_asset", "2.0.1"),
    source("A-SRC-103", "Industry Foundation Classes 4.3", "buildingSMART International", "https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/index.html", 2024, "bim", "4.3.2.0"),
    source("A-SRC-104", "Managed Model-based 3D Engineering", "ISO", "https://www.iso.org/standard/84300.html", 2025, "cad_product_model", "ISO 10303-242:2025"),
    source("A-SRC-105", "LAS Specification", "ASPRS", "https://www.asprs.org/divisions-committees/lidar-division/laser-las-file-format-exchange-activities", 2019, "point_cloud", "1.4 R15"),
    source("A-SRC-106", "ASTM E57 3D Imaging Data Exchange", "ASTM International", "https://www.astm.org/e2807-11r19.html", 2019, "point_cloud", "E2807-11(2019)"),
    source("A-SRC-107", "Sparse Arrays", "SciPy Project", "https://docs.scipy.org/doc/scipy/tutorial/sparse.html", 2026, "sparse_array", "1.18"),
    source("A-SRC-108", "DLPack Specification", "DLPack Project", "https://dmlc.github.io/dlpack/latest/", 2025, "tensor_interchange", "1.2"),
    source("A-SRC-109", "Matrix Market Exchange Formats", "NIST", "https://math.nist.gov/MatrixMarket/formats.html", 1997, "sparse_matrix", "coordinate/array"),
    source("A-SRC-110", "NumPy NPY Format", "NumPy Project", "https://numpy.org/devdocs/reference/generated/numpy.lib.format.html", 2026, "array_file", "3.0"),
    source("A-SRC-111", "SAM/BAM and Related Specifications", "GA4GH / samtools", "https://samtools.github.io/hts-specs/", 2026, "genomics", "SAM 1.6 / VCF 4.5 / CRAM 3.1"),
    source("A-SRC-112", "Variation Representation Specification", "GA4GH", "https://vrs.ga4gh.org/", 2024, "genomics", "2.x"),
    source("A-SRC-113", "Phenopackets", "GA4GH", "https://www.ga4gh.org/product/phenopackets/", 2022, "clinical_genomics", "2.0"),
    source("A-SRC-114", "FHIR R5", "HL7 International", "https://hl7.org/fhir/R5/", 2023, "healthcare", "5.0.0"),
    source("A-SRC-115", "Genomics Reporting Implementation Guide", "HL7 International", "https://www.hl7.org/fhir/uv/genomics-reporting/STU3/", 2024, "clinical_genomics", "3.0.0"),
    source("A-SRC-116", "Clinical Document Architecture R2.0", "HL7 International", "https://www.hl7.org/implement/standards/product_brief.cfm?product_id=7", 2005, "clinical_document", "R2"),
    source("A-SRC-117", "Catalogue of ISO 20022 Messages", "ISO 20022 Registration Authority", "https://www.iso20022.org/catalogue-messages", 2026, "financial_message", "current"),
    source("A-SRC-118", "FIX Latest Online Specification", "FIX Trading Community", "https://www.fixtrading.org/standards/", 2026, "financial_message", "FIX Latest"),
    source("A-SRC-119", "FpML Specifications", "FpML / ISDA", "https://www.fpml.org/spec/", 2025, "financial_trade_document", "5.13"),
    source("A-SRC-120", "XBRL 2.1 Specification", "XBRL International", "https://specifications.xbrl.org/work-product-index-group-base-spec-base-spec.html", 2003, "financial_reporting", "2.1"),
    source("A-SRC-121", "APPNOTE ZIP File Format Specification", "PKWARE", "https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT", 2026, "archive", "6.3.10"),
    source("A-SRC-122", "PAX Archive Format", "The Open Group", "https://pubs.opengroup.org/onlinepubs/9699919799/utilities/pax.html", 2018, "archive", "POSIX.1-2017"),
    source("A-SRC-123", "GZIP File Format", "IETF", "https://www.rfc-editor.org/rfc/rfc1952.html", 1996, "compression", "RFC 1952"),
    source("A-SRC-124", "Zstandard Compression", "IETF", "https://www.rfc-editor.org/rfc/rfc8878.html", 2021, "compression", "RFC 8878"),
    source("A-SRC-125", "Brotli Compressed Data Format", "IETF", "https://www.rfc-editor.org/rfc/rfc7932.html", 2016, "compression", "RFC 7932"),
    source("A-SRC-126", "Cryptographic Message Syntax", "IETF", "https://www.rfc-editor.org/rfc/rfc5652.html", 2009, "protection", "RFC 5652"),
    source("A-SRC-127", "CBOR Object Signing and Encryption", "IETF", "https://www.rfc-editor.org/rfc/rfc9052.html", 2022, "protection", "RFC 9052"),
    source("A-SRC-128", "YAML 1.2.2", "YAML Language Development Team", "https://yaml.org/spec/1.2.2/", 2021, "configuration", "1.2.2"),
    source("A-SRC-129", "TOML", "TOML Project", "https://toml.io/en/v1.0.0", 2021, "configuration", "1.0.0"),
    source("A-SRC-130", "OCI Image Layout", "Open Container Initiative", "https://github.com/opencontainers/image-spec/blob/main/image-layout.md", 2025, "artifact_package", "1.1"),
    source("A-SRC-131", "CycloneDX Specification", "OWASP Foundation", "https://cyclonedx.org/specification/overview/", 2025, "metadata_evidence", "1.7"),
    source("A-SRC-132", "C2PA Technical Specification", "Coalition for Content Provenance and Authenticity", "https://spec.c2pa.org/specifications/", 2026, "provenance_evidence", "2.4"),
    source("A-SRC-133", "Data Catalog Vocabulary Version 3", "W3C", "https://www.w3.org/TR/vocab-dcat-3/", 2024, "metadata_catalog", "3"),
    source("A-SRC-134", "Dublin Core Metadata Element Set", "DCMI", "https://www.dublincore.org/specifications/dublin-core/dces/", 2020, "metadata", "1.1"),
    source("A-SRC-135", "WARC File Format", "IETF", "https://www.rfc-editor.org/rfc/rfc9585.html", 2024, "web_archive", "RFC 9585"),
    source("A-SRC-136", "ELF gABI", "System V ABI Project", "https://gabi.xinuos.com/elf/", 2013, "executable_binary", "4.1"),
    source("A-SRC-137", "WebAssembly Core Specification", "W3C", "https://www.w3.org/TR/wasm-core-2/", 2025, "bytecode", "2.0"),
    source("A-SRC-138", "LLVM Bitcode File Format", "LLVM Project", "https://llvm.org/docs/BitCodeFormat.html", 2026, "intermediate_representation", "current"),
    source("A-SRC-139", "AsyncAPI Specification", "AsyncAPI Initiative", "https://www.asyncapi.com/docs/reference/specification/v3.0.0", 2024, "event_schema", "3.0.0"),
    source("A-SRC-140", "Protocol Buffers Editions", "Google", "https://protobuf.dev/programming-guides/editions/", 2024, "schema_bound_message", "2023/2024"),
    source("A-SRC-141", "Apache Arrow Format Version History", "Apache Software Foundation", "https://arrow.apache.org/docs/format/Versioning.html", 2025, "columnar_memory", "current"),
    source("A-SRC-142", "SDMX 3.0 Standards", "SDMX Sponsors", "https://docs.sdmx.org/en/latest/", 2021, "statistical_data", "3.0"),
    source("A-SRC-143", "OpenTelemetry Semantic Conventions", "Cloud Native Computing Foundation", "https://opentelemetry.io/docs/specs/semconv/", 2023, "telemetry", "1.x"),
    source("A-SRC-144", "CloudEvents SQL", "Cloud Native Computing Foundation", "https://github.com/cloudevents/spec/blob/main/cesql/spec.md", 2024, "event_query", "1.0"),
    source("A-SRC-145", "OpenAPI Specification 3.1.0", "OpenAPI Initiative", "https://spec.openapis.org/oas/v3.1.0.html", 2021, "api_schema", "3.1.0"),
    source("A-SRC-146", "OGC SensorThings API Part 1", "Open Geospatial Consortium", "https://docs.ogc.org/is/18-088/18-088.html", 2021, "sensor_observation", "1.1"),
    source("A-SRC-147", "OpenSCENARIO XML", "ASAM", "https://www.asam.net/standards/detail/openscenario-xml/", 2024, "simulation_scenario", "1.3.1"),
    source("A-SRC-148", "RO-Crate Specification", "RO-Crate Community", "https://www.researchobject.org/ro-crate/specification/1.2/", 2025, "research_package", "1.2"),
    source("A-SRC-149", "Simple Mail Transfer Protocol", "IETF", "https://www.rfc-editor.org/rfc/rfc5321.html", 2008, "email_transport_envelope", "RFC 5321"),
    source("A-SRC-150", "iCalendar", "IETF", "https://www.rfc-editor.org/rfc/rfc5545.html", 2009, "calendar_object", "RFC 5545"),
    source("A-SRC-151", "MIDI 1.0 Detailed Specification", "MIDI Association", "https://midi.org/midi-1-0-detailed-specification", 1996, "musical_event", "1.0"),
    source("A-SRC-152", "ECMAScript Language Specification", "Ecma International", "https://tc39.es/ecma262/", 2026, "program_source", "ECMA-262"),
]


def F(fid: str, label: str, cluster: str, layer: str, modality: str, shape: str, target: str | None,
      relation: str, refs: list[str], invalid: str, target_kind: str = "shape_record", **overrides: str) -> dict:
    assert relation in RELATIONS
    return {
        "family_id": fid,
        "label": label,
        "domain_cluster": cluster,
        "expected_registry_layer": layer,
        "modality": modality,
        "logical_shape": shape,
        "target_id": target,
        "target_kind": target_kind if target else "none",
        "relation": relation,
        "evidence_refs": refs,
        "invalid_inference": invalid,
        "overrides": overrides,
    }


FAMILY_SPECS = [
    F("fam.scalar_value", "typed scalar value", "core", "observation_record_shape", "scalar", "scalar", "shape.scalar", "equivalent", ["A-DSS-001", "A-DSS-002"], "A scalar carrier does not reveal business meaning."),
    F("fam.optional_value", "optional typed value", "core", "observation_record_shape", "record", "optional", "shape.optional_value", "equivalent", ["A-DSS-001", "A-DSS-007"], "Null or omission does not identify the reason for absence."),
    F("fam.tagged_union", "tagged union", "core", "observation_record_shape", "record", "union", "shape.tagged_union", "equivalent", ["A-DSS-002", "A-DSS-005"], "A union tag does not establish semantic substitutability."),
    F("fam.tuple", "heterogeneous tuple", "core", "observation_record_shape", "record", "tuple", "shape.tuple", "equivalent", ["A-DSS-001", "A-DSS-002"], "Position does not imply a field name or business role."),
    F("fam.named_record", "named record or struct", "core", "observation_record_shape", "record", "record", "shape.struct", "equivalent", ["A-DSS-002", "A-DSS-005"], "Field names do not prove semantic ownership."),
    F("fam.homogeneous_list", "homogeneous list", "core", "observation_record_shape", "record", "sequence", "shape.homogeneous_list", "equivalent", ["A-DSS-001", "A-DSS-002"], "Serialization order is not necessarily semantic order."),
    F("fam.set", "set", "core", "observation_record_shape", "record", "set", "shape.set", "equivalent", ["A-DSS-001"], "Deduplication is invalid without declared equality."),
    F("fam.multiset", "multiset", "core", "observation_record_shape", "record", "set", "shape.multiset", "equivalent", ["A-DSS-001"], "Multiplicity is not an accidental duplicate count."),
    F("fam.key_value_map", "key-value map", "core", "observation_record_shape", "record", "map", "shape.map", "equivalent", ["A-DSS-001", "A-DSS-007"], "Map keys are not automatically entity identifiers."),
    F("fam.opaque_blob", "opaque binary blob", "core", "observation_record_shape", "binary", "document", "shape.binary_blob", "equivalent", ["A-DSS-007"], "Opaque bytes cannot be queried as decoded content."),

    F("fam.relational_relation", "mathematical relation", "tables", "observation_record_shape", "table", "table", "shape.relation", "equivalent", ["A-DSS-010"], "Row position and physical order are non-semantic."),
    F("fam.keyed_relation", "key-constrained relation", "tables", "observation_record_shape", "table", "table", "shape.keyed_relation", "equivalent", ["A-DSS-010", "A-DSS-064"], "A file row number is not a primary key."),
    F("fam.data_frame", "labeled data frame", "tables", "observation_record_shape", "table", "table", "shape.data_frame", "equivalent", ["A-DSS-002", "A-DSS-064"], "Column labels do not establish measures, dimensions, or units."),
    F("fam.wide_table", "wide record table", "tables", "observation_record_shape", "table", "table", "shape.wide_record_table", "equivalent", ["A-DSS-010"], "A wide layout does not prove one-row-per-entity grain."),
    F("fam.fact_table", "dimensional fact table", "tables", "observation_record_shape", "table", "table", "shape.fact_table", "equivalent", ["A-DSS-027"], "Numeric columns are not measures without semantic declarations."),
    F("fam.dimension_table", "dimension table", "tables", "observation_record_shape", "table", "table", "shape.dimension_table", "equivalent", ["A-DSS-027"], "Text columns are not automatically dimensions."),
    F("fam.star_schema", "star schema", "tables", "observation_record_shape", "table", "model", "shape.star_schema", "equivalent", ["A-DSS-027"], "Join topology does not prove conformed dimensions."),
    F("fam.snowflake_schema", "snowflake schema", "tables", "observation_record_shape", "table", "model", "shape.snowflake_schema", "equivalent", ["A-DSS-027"], "Normalization shape does not establish analytical grain."),
    F("fam.spreadsheet_workbook", "spreadsheet workbook", "tables", "observation_record_shape", "mixed", "bundle", "shape.spreadsheet_workbook", "equivalent", ["A-SRC-080", "A-SRC-081"], "A rectangular cell region is not automatically a typed table."),
    F("fam.csv_dialect", "CSV dialect-bound table representation", "tables", "encoding", "table", "table", "shape.table", "disjoint", ["A-DSS-010", "A-DSS-064"], "CSV syntax does not prove column types, null semantics, or grain."),
    F("fam.fixed_width_rows", "fixed-width row representation", "tables", "physical_layout", "table", "table", "shape.table", "disjoint", ["A-DSS-010"], "Byte offsets do not establish field semantics."),
    F("fam.statistical_cube", "statistical observation cube", "tables", "observation_record_shape", "table", "cube", "shape.statistical_observation_cube", "equivalent", ["A-DSS-026", "A-DSS-027"], "Cube coordinates do not establish aggregation law."),
    F("fam.sparse_cube", "sparse multidimensional cube", "tables", "observation_record_shape", "array", "cube", "shape.sparse_cube", "equivalent", ["A-DSS-026"], "An absent cube cell is not necessarily zero or missing."),
    F("fam.contingency_table", "contingency table", "tables", "observation_record_shape", "table", "cube", "shape.contingency_table", "equivalent", ["A-DSS-027"], "Cell counts do not justify independence inference."),

    F("fam.plain_text_document", "plain-text document", "documents", "observation_record_shape", "text", "document", "shape.text_document", "equivalent", ["A-DSS-062"], "Text decoding does not establish language, structure, or meaning."),
    F("fam.tree_document", "generic tree document", "documents", "observation_record_shape", "document", "tree", "shape.tree_document", "equivalent", ["A-DSS-001", "A-DSS-009"], "Tree shape does not imply XML, JSON, or domain semantics."),
    F("fam.markup_document", "markup document", "documents", "observation_record_shape", "document", "document", "shape.markup_document", "equivalent", ["A-DSS-009", "A-SRC-076"], "Markup syntax does not prove rendered or textual equivalence."),
    F("fam.rich_text_document", "editable rich-text document", "documents", "observation_record_shape", "document", "document", "shape.markup_document", "narrower", ["A-SRC-080", "A-SRC-081"], "Rendered appearance does not prove editable structure preservation."),
    F("fam.fixed_layout_document", "paginated fixed-layout document", "documents", "observation_record_shape", "document", "document", "shape.paginated_document", "equivalent", ["A-SRC-078", "A-SRC-079"], "A PDF page image is not equivalent to its logical reading order."),
    F("fam.compound_document", "compound document bundle", "documents", "observation_record_shape", "mixed", "bundle", "shape.document_bundle", "equivalent", ["A-SRC-080", "A-SRC-081"], "Package membership does not establish document-part semantics."),
    F("fam.pdf_program", "PDF document object graph", "documents", "container_file_format", "document", "document", "shape.pdf_document", "overlap", ["A-SRC-078"], "PDF conformance does not prove reading order, extraction fidelity, or semantic structure."),
    F("fam.ooxml_wordprocessing", "OOXML word-processing package", "documents", "container_file_format", "document", "bundle", "shape.word_processing_document", "overlap", ["A-SRC-080"], "DOCX packaging is not the identity of a rich-text semantic document."),
    F("fam.ooxml_spreadsheet", "OOXML spreadsheet package", "documents", "container_file_format", "mixed", "bundle", "shape.spreadsheet_workbook", "overlap", ["A-SRC-080"], "XLSX cells may contain formulas, presentation, tables, and weakly typed regions."),
    F("fam.ooxml_presentation", "OOXML presentation package", "documents", "container_file_format", "mixed", "bundle", "shape.presentation_document", "overlap", ["A-SRC-080"], "Slide order and visual placement do not establish a tabular or prose model."),
    F("fam.odf_text", "OpenDocument text package", "documents", "container_file_format", "document", "bundle", "shape.word_processing_document", "overlap", ["A-SRC-081"], "ODF packaging is separate from editable document semantics."),
    F("fam.odf_spreadsheet", "OpenDocument spreadsheet package", "documents", "container_file_format", "mixed", "bundle", "shape.spreadsheet_workbook", "overlap", ["A-SRC-081"], "ODS sheets cannot be assumed to be relations."),
    F("fam.epub_publication", "EPUB publication", "documents", "observation_record_shape", "document", "bundle", "shape.epub_publication", "equivalent", ["A-SRC-082"], "Reading order and resource graph are not reducible to one markup tree."),
    F("fam.html_dom", "HTML DOM document", "documents", "observation_record_shape", "document", "tree", "shape.html_document", "equivalent", ["A-SRC-076", "A-SRC-077"], "HTML source bytes, parsed DOM, and rendered accessibility tree are distinct."),
    F("fam.web_archive", "web crawl archive", "documents", "observation_record_shape", "mixed", "archive", "shape.web_archive", "equivalent", ["A-SRC-135"], "A WARC record sequence does not establish page-level semantic equivalence."),

    F("fam.internet_email", "Internet email message", "email", "observation_record_shape", "mixed", "message", "shape.internet_message", "equivalent", ["A-SRC-071"], "Header From is not the transport envelope sender or verified identity."),
    F("fam.mime_multipart", "MIME multipart body tree", "email", "observation_record_shape", "mixed", "tree", "shape.mime_multipart", "equivalent", ["A-SRC-072", "A-SRC-073"], "A MIME media type does not prove decoded payload semantics."),
    F("fam.stored_email_message", "stored account-scoped email message", "email", "observation_record_shape", "mixed", "message", "shape.email_message", "equivalent", ["A-SRC-071", "A-SRC-072"], "Mailbox state and delivery metadata are not part of Internet message content identity."),
    F("fam.conversation_thread", "profile-defined conversation thread", "email", "observation_record_shape", "mixed", "graph", "shape.conversation_thread", "equivalent", ["A-SRC-071"], "Subject or References fields alone do not prove conversation membership."),
    F("fam.mailbox_archive", "mailbox message sequence", "email", "container_file_format", "mixed", "archive", "shape.record_stream_file", "overlap", ["A-SRC-074"], "mbox separators and file order do not prove thread or event-time order."),
    F("fam.email_transport_envelope", "email transport envelope", "email", "observation_record_shape", "record", "message", None, "missing", ["A-SRC-149"], "SMTP reverse-path and forward-path are distinct from message header fields."),
    F("fam.calendar_object", "calendar and scheduling object", "documents", "observation_record_shape", "record", "message", None, "missing", ["A-SRC-150", "A-DSS-035"], "A local date-time without zone/calendar policy is not a globally ordered instant."),

    F("fam.json_document", "JSON document instance", "messages", "encoding", "record", "tree", "shape.tree_document", "disjoint", ["A-DSS-008", "A-DSS-001"], "JSON number and object syntax do not establish precision or duplicate-name policy."),
    F("fam.xml_infoset", "XML information set", "messages", "encoding", "document", "tree", "shape.tree_document", "disjoint", ["A-DSS-009"], "XML lexical equality is not infoset or domain equality."),
    F("fam.yaml_representation", "YAML representation graph", "messages", "encoding", "record", "graph", "shape.tree_document", "overlap", ["A-SRC-128"], "YAML aliases can form a graph; treating every YAML value as a tree loses identity."),
    F("fam.cbor_tagged_value", "CBOR tagged data item", "messages", "encoding", "record", "union", "shape.tagged_union", "overlap", ["A-DSS-007"], "A CBOR tag is uninterpretable without its registered or private contract."),
    F("fam.protobuf_message", "Protocol Buffers message", "messages", "encoding", "record", "message", "shape.schema_bound_message", "overlap", ["A-DSS-006", "A-SRC-140"], "Wire compatibility does not prove semantic compatibility."),
    F("fam.avro_record", "Avro schema-bound record", "messages", "encoding", "record", "message", "shape.schema_bound_message", "overlap", ["A-DSS-005"], "Avro reader-writer resolution does not prove domain-safe evolution."),
    F("fam.arrow_record_batch", "Arrow record batch", "messages", "physical_layout", "table", "table", "shape.table", "disjoint", ["A-DSS-002", "A-SRC-141"], "Arrow buffers do not prove a relational key, grain, or semantic column order."),
    F("fam.parquet_column_chunk", "Parquet column-chunk layout", "messages", "physical_layout", "table", "table", "shape.table", "disjoint", ["A-DSS-004"], "Parquet physical statistics do not establish semantic constraints."),
    F("fam.api_exchange_message", "API request or response message", "messages", "observation_record_shape", "record", "message", "shape.schema_bound_message", "overlap", ["A-DSS-070", "A-SRC-145"], "API schema conformance does not establish business command or event semantics."),
    F("fam.asyncapi_message", "asynchronous API message", "messages", "observation_record_shape", "event", "message", "shape.event_envelope", "overlap", ["A-SRC-139", "A-DSS-029"], "A channel binding does not establish event time, idempotency, or finality."),

    F("fam.general_graph", "general graph", "graphs", "observation_record_shape", "graph", "graph", "shape.graph", "equivalent", ["A-DSS-011"], "Adjacency does not establish causal or semantic relationship."),
    F("fam.directed_graph", "directed graph", "graphs", "observation_record_shape", "graph", "graph", "shape.directed_graph", "equivalent", ["A-DSS-011"], "Edge direction does not prove causal direction."),
    F("fam.multigraph", "multigraph", "graphs", "observation_record_shape", "graph", "graph", "shape.multigraph", "equivalent", ["A-DSS-011"], "Parallel edges must not be silently deduplicated."),
    F("fam.dag", "directed acyclic graph", "graphs", "observation_record_shape", "graph", "graph", "shape.directed_acyclic_graph", "equivalent", ["A-DSS-011"], "A DAG does not automatically define one topological order."),
    F("fam.tree", "rooted tree", "graphs", "observation_record_shape", "graph", "tree", "shape.tree", "equivalent", ["A-DSS-011"], "Document order and tree ancestry are distinct."),
    F("fam.hypergraph", "hypergraph", "graphs", "observation_record_shape", "graph", "graph", "shape.hypergraph", "equivalent", ["A-DSS-011"], "A hyperedge cannot always be losslessly reduced to pairwise edges."),
    F("fam.bipartite_graph", "bipartite graph", "graphs", "observation_record_shape", "graph", "graph", "shape.bipartite_graph", "equivalent", ["A-DSS-011"], "Partition membership must be explicit."),
    F("fam.property_graph", "property graph", "graphs", "observation_record_shape", "graph", "graph", "shape.property_graph", "equivalent", ["A-DSS-011"], "Property-graph labels and RDF classes are not aliases."),
    F("fam.rdf_graph", "RDF graph", "graphs", "observation_record_shape", "graph", "graph", "shape.rdf_graph", "equivalent", ["A-DSS-011", "A-DSS-012"], "Lexical JSON-LD equality is not RDF graph equality."),
    F("fam.rdf_dataset", "RDF dataset with named graphs", "graphs", "observation_record_shape", "graph", "graph", "shape.rdf_graph", "broader", ["A-DSS-011"], "An RDF graph record cannot represent dataset graph names without extension."),
    F("fam.temporal_graph", "temporal graph", "graphs", "observation_record_shape", "graph", "graph", "shape.temporal_graph", "equivalent", ["A-DSS-011", "A-DSS-036"], "Edge validity time and event recording time must remain distinct."),
    F("fam.provenance_graph", "provenance activity graph", "metadata", "observation_record_shape", "metadata_evidence", "provenance", "shape.provenance_graph", "equivalent", ["A-DSS-028"], "Derivation links do not prove correctness or authority."),
    F("fam.lineage_run_graph", "runtime lineage graph", "metadata", "observation_record_shape", "metadata_evidence", "provenance", "shape.lineage_run_graph", "equivalent", ["A-DSS-039"], "Recorded lineage does not prove complete dependency capture."),

    F("fam.event_envelope", "event envelope", "events", "observation_record_shape", "event", "message", "shape.event_envelope", "equivalent", ["A-DSS-029"], "Envelope time and payload event time are not necessarily equal."),
    F("fam.domain_event", "domain event record", "events", "observation_record_shape", "event", "record", "shape.domain_event_record", "equivalent", ["A-DSS-029"], "A message named event is not proof that a domain fact occurred."),
    F("fam.log_record", "log record", "events", "observation_record_shape", "event", "record", "shape.log_record", "equivalent", ["A-DSS-030"], "Log severity and message text do not establish audit evidence."),
    F("fam.row_changelog", "row changelog", "events", "observation_record_shape", "event", "stream", "shape.row_changelog", "equivalent", ["A-DSS-038"], "Update-before/update-after cannot be collapsed without loss."),
    F("fam.cdc_stream", "change-data-capture stream", "events", "observation_record_shape", "event", "stream", "shape.change_data_capture_stream", "equivalent", ["A-DSS-038"], "Commit order does not necessarily equal business event order."),
    F("fam.upsert_stream", "upsert stream", "events", "observation_record_shape", "event", "stream", "shape.upsert_stream", "equivalent", ["A-DSS-038"], "An upsert without key and delete semantics is under-specified."),
    F("fam.retraction_stream", "retraction stream", "events", "observation_record_shape", "event", "stream", "shape.retraction_stream", "equivalent", ["A-DSS-038"], "Retraction does not mean source fact deletion."),
    F("fam.watermarked_stream", "watermarked event stream", "events", "observation_record_shape", "event", "stream", "shape.watermarked_event_stream", "equivalent", ["A-DSS-037"], "A watermark is a progress assertion, not proof of completeness."),
    F("fam.case_event_log", "case-centric event log", "events", "observation_record_shape", "event", "stream", "shape.case_event_log", "equivalent", ["A-DSS-033"], "Case identifiers cannot be inferred from correlation fields."),
    F("fam.object_centric_event_log", "object-centric event log", "events", "observation_record_shape", "event", "graph", "shape.object_centric_event_log", "equivalent", ["A-DSS-034"], "Object-event relations must not be projected to one case without declared loss."),
    F("fam.activity_lifecycle_log", "activity lifecycle log", "events", "observation_record_shape", "event", "stream", "shape.activity_lifecycle_log", "equivalent", ["A-DSS-033"], "Lifecycle transitions require correlation and ordering semantics."),
    F("fam.audit_trail", "audit trail", "events", "observation_record_shape", "metadata_evidence", "stream", "shape.audit_trail", "equivalent", ["A-DSS-028"], "Append-only storage does not prove completeness, custody, or non-repudiation."),

    F("fam.trace_span_graph", "distributed trace span graph", "telemetry", "observation_record_shape", "metadata_evidence", "graph", "shape.trace_span_graph", "equivalent", ["A-DSS-032"], "Parent and link edges do not prove causality."),
    F("fam.metric_stream", "telemetry metric stream", "telemetry", "observation_record_shape", "temporal", "stream", "shape.metric_stream", "equivalent", ["A-DSS-031", "A-DSS-063"], "Metric names and labels do not establish business metric semantics."),
    F("fam.histogram_stream", "histogram metric stream", "telemetry", "observation_record_shape", "temporal", "stream", "shape.histogram_stream", "equivalent", ["A-DSS-031"], "Histograms with different bucket boundaries cannot be added naively."),
    F("fam.exponential_histogram", "exponential histogram stream", "telemetry", "observation_record_shape", "temporal", "stream", "shape.histogram_stream", "narrower", ["A-DSS-031", "A-SRC-143"], "Scale changes require defined downscaling before aggregation."),
    F("fam.telemetry_log_stream", "telemetry log stream", "telemetry", "observation_record_shape", "event", "stream", "shape.log_record", "broader", ["A-DSS-030"], "A log-record shape does not define collection ordering, gaps, or retention."),

    F("fam.ordered_series", "ordered series", "time_series", "observation_record_shape", "temporal", "series", "shape.ordered_series", "equivalent", ["A-DSS-035"], "Physical order is not a semantic series index."),
    F("fam.regular_time_series", "regular time series", "time_series", "observation_record_shape", "temporal", "series", "shape.regular_time_series", "equivalent", ["A-DSS-035"], "Nominal cadence does not prove absence of gaps or clock drift."),
    F("fam.irregular_time_series", "irregular time series", "time_series", "observation_record_shape", "temporal", "series", "shape.irregular_time_series", "equivalent", ["A-DSS-035"], "Interpolation is invalid without a declared signal or process model."),
    F("fam.multivariate_time_series", "multivariate time series", "time_series", "observation_record_shape", "temporal", "series", "shape.multivariate_time_series", "equivalent", ["A-DSS-035"], "Timestamp equality does not prove synchronized observation."),
    F("fam.panel_series", "panel series", "time_series", "observation_record_shape", "temporal", "series", "shape.panel_series", "equivalent", ["A-DSS-026"], "Entity membership and balancedness must be declared."),
    F("fam.longitudinal_cohort", "longitudinal cohort", "time_series", "observation_record_shape", "clinical", "series", "shape.longitudinal_cohort", "equivalent", ["A-DSS-057"], "Repeated records do not prove a stable cohort population."),
    F("fam.interval_series", "interval series", "time_series", "observation_record_shape", "temporal", "series", "shape.interval_series", "equivalent", ["A-DSS-036"], "Interval endpoint closure cannot be guessed."),

    F("fam.sampled_signal", "sampled signal", "signals", "observation_record_shape", "signal", "series", "shape.sampled_signal", "equivalent", ["A-DSS-044"], "Sample index does not establish time without rate and clock metadata."),
    F("fam.multichannel_signal", "multichannel sampled signal", "signals", "observation_record_shape", "signal", "series", "shape.multichannel_signal", "equivalent", ["A-DSS-045"], "Channel alignment cannot be inferred from equal array lengths."),
    F("fam.spectrum", "frequency-domain spectrum", "signals", "observation_record_shape", "signal", "series", None, "missing", ["A-DSS-045"], "A spectrum is not interchangeable with a time-domain waveform."),
    F("fam.spectrogram", "time-frequency spectrogram", "signals", "observation_record_shape", "signal", "raster", "shape.spectrogram", "equivalent", ["A-DSS-045"], "Spectrogram magnitudes do not permit exact waveform reconstruction without phase/profile."),
    F("fam.mdf_measurement", "ASAM MDF measurement data", "signals", "container_file_format", "signal", "bundle", "shape.multichannel_signal", "overlap", ["A-SRC-094"], "MDF container conformance does not establish sensor calibration or unit authority."),
    F("fam.sensor_observation", "sensor observation", "signals", "observation_record_shape", "signal", "record", "shape.measurement_observation", "overlap", ["A-DSS-022", "A-DSS-023", "A-SRC-146"], "A sensor result without feature, property, procedure, unit, and time is incomplete."),

    F("fam.raster_image", "raster image", "media", "observation_record_shape", "image", "raster", "shape.image", "equivalent", ["A-SRC-083", "A-SRC-084"], "Pixel values do not establish color space or scene/display encoding."),
    F("fam.multichannel_image", "multichannel image", "media", "observation_record_shape", "image", "raster", "shape.multichannel_image", "equivalent", ["A-SRC-086"], "Channel names alone may not establish spectral response."),
    F("fam.label_image", "label image", "media", "observation_record_shape", "image", "raster", "shape.label_image", "equivalent", ["A-DSS-042"], "Interpolation of categorical labels is invalid."),
    F("fam.image_pyramid", "multiresolution image pyramid", "media", "observation_record_shape", "image", "raster", "shape.multiresolution_image_pyramid", "equivalent", ["A-DSS-042", "A-DSS-047"], "Pyramid levels are not independent observations."),
    F("fam.voxel_volume", "voxel volume", "media", "observation_record_shape", "image", "tensor", "shape.voxel_volume", "equivalent", ["A-DSS-041", "A-DSS-043"], "Voxel index is not a physical coordinate without an affine/reference frame."),
    F("fam.deep_image", "deep image with variable samples per pixel", "media", "observation_record_shape", "image", "raster", None, "missing", ["A-SRC-086"], "Deep samples cannot be flattened to one pixel value without an explicit compositing loss."),
    F("fam.audio_track", "audio track", "media", "observation_record_shape", "audio", "series", "shape.audio_track", "equivalent", ["A-DSS-045", "A-SRC-088", "A-SRC-089"], "Codec sample rate does not establish measurement clock accuracy."),
    F("fam.musical_event_sequence", "musical event sequence", "media", "observation_record_shape", "audio", "stream", None, "missing", ["A-SRC-151"], "Symbolic note events are not an audio waveform."),
    F("fam.video_track", "video track", "media", "observation_record_shape", "video", "series", "shape.video_track", "equivalent", ["A-DSS-046", "A-SRC-090"], "Decode order and presentation order are distinct."),
    F("fam.timed_media_container", "timed-media container", "media", "container_file_format", "mixed", "bundle", "shape.timed_media_container", "overlap", ["A-DSS-046"], "A media container is not a codec, track modality, or semantic timeline."),
    F("fam.caption_track", "timed text caption track", "media", "observation_record_shape", "text", "series", None, "missing", ["A-SRC-091"], "Cue order does not prove linguistic or accessibility completeness."),
    F("fam.openexr_container", "OpenEXR multipart/deep image container", "media", "container_file_format", "image", "bundle", "shape.multichannel_image", "overlap", ["A-SRC-086"], "EXR parts, views, channels, and deep samples are different axes."),

    F("fam.geometry", "spatial geometry", "geospatial", "observation_record_shape", "spatial", "model", "shape.geometry", "equivalent", ["A-DSS-018"], "Coordinate numbers do not define a CRS or axis order."),
    F("fam.spatial_feature", "spatial feature", "geospatial", "observation_record_shape", "spatial", "record", "shape.spatial_feature", "equivalent", ["A-DSS-018"], "Geometry equality is not feature identity."),
    F("fam.feature_collection", "spatial feature collection", "geospatial", "observation_record_shape", "spatial", "sequence", "shape.feature_collection", "equivalent", ["A-DSS-020"], "Collection order is not spatial or semantic order."),
    F("fam.spatial_raster", "georeferenced raster", "geospatial", "observation_record_shape", "spatial", "raster", "shape.raster", "equivalent", ["A-DSS-019"], "Raster cells require CRS, grid geometry, and range semantics."),
    F("fam.coverage", "spatiotemporal coverage", "geospatial", "observation_record_shape", "spatial", "coverage", "shape.coverage", "equivalent", ["A-DSS-019"], "A coverage is a function, not merely an image or array."),
    F("fam.grid_coverage", "grid coverage", "geospatial", "observation_record_shape", "spatial", "coverage", "shape.grid_coverage", "equivalent", ["A-DSS-019"], "Grid index is not a geographic position without domain-set mapping."),
    F("fam.point_cloud", "point cloud", "geospatial", "observation_record_shape", "spatial", "point_set", "shape.point_cloud", "equivalent", ["A-DSS-019", "A-SRC-105", "A-SRC-106"], "Point order and density do not establish a surface."),
    F("fam.trajectory", "trajectory", "geospatial", "observation_record_shape", "spatial", "series", "shape.trajectory", "equivalent", ["A-DSS-021"], "A sequence of positions is not a trajectory without object identity and time."),
    F("fam.moving_feature", "moving feature", "geospatial", "observation_record_shape", "spatial", "record", "shape.moving_feature", "equivalent", ["A-DSS-021"], "Trajectory samples do not fully define continuous moving geometry."),
    F("fam.spatial_network", "spatially embedded network", "geospatial", "observation_record_shape", "spatial", "graph", "shape.spatial_network", "equivalent", ["A-DSS-018"], "Geometric crossings do not automatically imply network connectivity."),
    F("fam.vector_tile", "vector tile", "geospatial", "container_file_format", "spatial", "bundle", "shape.spatial_tile", "narrower", ["A-SRC-096"], "Tile clipping and quantization can change topology and identifiers."),
    F("fam.three_d_tiles", "3D tiles hierarchy", "geospatial", "observation_record_shape", "engineering_3d", "scene", "shape.spatial_tile_set", "overlap", ["A-SRC-096"], "Level-of-detail nodes are not independent semantic objects."),
    F("fam.city_model", "semantic 3D city model", "geospatial", "observation_record_shape", "engineering_3d", "model", None, "missing", ["A-SRC-097"], "Rendered mesh geometry does not preserve city-object semantics."),
    F("fam.stac_catalog", "spatiotemporal asset catalog", "geospatial", "observation_record_shape", "metadata_evidence", "tree", None, "missing", ["A-SRC-099"], "Catalog metadata does not prove asset validity or semantic comparability."),
    F("fam.geoparquet_binding", "GeoParquet table binding", "geospatial", "physical_layout", "spatial", "table", "shape.feature_collection", "disjoint", ["A-SRC-100", "A-SRC-101"], "GeoParquet metadata and memory layout are not the identity of a feature collection."),

    F("fam.vector", "vector", "arrays", "observation_record_shape", "array", "tensor", "shape.vector", "equivalent", ["A-DSS-002"], "Vector position has no meaning without an axis/index contract."),
    F("fam.matrix", "matrix", "arrays", "observation_record_shape", "array", "tensor", "shape.matrix", "equivalent", ["A-DSS-002"], "A two-dimensional array is not necessarily a linear operator."),
    F("fam.dense_tensor", "dense tensor", "arrays", "observation_record_shape", "array", "tensor", "shape.dense_tensor", "equivalent", ["A-DSS-002", "A-SRC-108"], "Shape compatibility alone does not establish axis semantic compatibility."),
    F("fam.coo_sparse_tensor", "coordinate sparse tensor", "arrays", "observation_record_shape", "array", "tensor", "shape.coordinate_sparse_tensor", "equivalent", ["A-SRC-107", "A-SRC-109"], "Missing coordinates, stored zeros, and duplicate coordinates require explicit laws."),
    F("fam.csr_matrix", "CSR sparse matrix", "arrays", "physical_layout", "array", "tensor", "shape.compressed_sparse_matrix", "narrower", ["A-SRC-107", "A-SRC-109"], "CSR storage is not semantic row order or missingness."),
    F("fam.csc_matrix", "CSC sparse matrix", "arrays", "physical_layout", "array", "tensor", "shape.compressed_sparse_matrix", "narrower", ["A-SRC-107", "A-SRC-109"], "CSC storage is not semantic column order."),
    F("fam.block_sparse_tensor", "block-sparse tensor", "arrays", "physical_layout", "array", "tensor", "shape.coordinate_sparse_tensor", "overlap", ["A-SRC-107"], "Block absence and element zero are different."),
    F("fam.ragged_array", "ragged array", "arrays", "observation_record_shape", "array", "tensor", "shape.ragged_array", "equivalent", ["A-DSS-002", "A-DSS-017"], "Padding a ragged axis invents values unless masked explicitly."),
    F("fam.masked_array", "masked array", "arrays", "observation_record_shape", "array", "tensor", "shape.masked_array", "equivalent", ["A-DSS-017"], "A mask is not a missingness reason."),
    F("fam.labeled_array", "labeled multidimensional array", "arrays", "observation_record_shape", "array", "tensor", "shape.labeled_array", "equivalent", ["A-DSS-015", "A-DSS-017"], "Coordinate labels do not automatically carry unit or CRS semantics."),
    F("fam.chunked_array", "chunked array", "arrays", "physical_layout", "array", "tensor", "shape.chunked_array", "overlap", ["A-DSS-016"], "Chunk boundaries are physical and must not affect logical equality."),

    F("fam.hdf5_dataset_graph", "HDF5 group/dataset graph", "scientific", "container_file_format", "scientific", "graph", None, "missing", ["A-DSS-014"], "HDF5 groups, links, dataspaces, and datasets cannot be collapsed to one tensor."),
    F("fam.netcdf_dataset", "netCDF named-dimension dataset", "scientific", "observation_record_shape", "scientific", "bundle", None, "missing", ["A-DSS-015", "A-DSS-017"], "Coordinate variables and conventions carry semantics beyond array shape."),
    F("fam.zarr_hierarchy", "Zarr v3 group/array hierarchy", "scientific", "container_file_format", "scientific", "tree", "shape.chunked_array", "broader", ["A-DSS-016"], "A Zarr hierarchy is broader than one chunked array and codecs are separate."),
    F("fam.fits_hdu_list", "FITS header-data-unit list", "scientific", "container_file_format", "scientific", "bundle", None, "missing", ["A-SRC-093"], "FITS can carry images and tables; the file format is not one modality."),
    F("fam.dicom_study_series", "DICOM study/series/instance graph", "scientific", "observation_record_shape", "clinical", "graph", None, "missing", ["A-DSS-041"], "DICOM pixel data alone is not the study, series, patient, or acquisition context."),
    F("fam.ome_microscopy", "OME multidimensional microscopy dataset", "scientific", "observation_record_shape", "scientific", "bundle", "shape.multiresolution_image_pyramid", "broader", ["A-DSS-042"], "OME axes, transforms, labels, and acquisition metadata exceed an image pyramid."),
    F("fam.nifti_neurovolume", "NIfTI neuroimaging volume", "scientific", "container_file_format", "scientific", "tensor", "shape.voxel_volume", "overlap", ["A-DSS-043"], "NIfTI header transforms are not optional decoration on a voxel tensor."),
    F("fam.seismic_waveform", "seismic waveform archive", "scientific", "observation_record_shape", "signal", "series", "shape.sampled_signal", "narrower", ["A-DSS-044"], "Sample quality and timing corrections cannot be discarded."),

    F("fam.surface_mesh", "surface mesh", "engineering", "observation_record_shape", "engineering_3d", "mesh", "shape.mesh", "equivalent", ["A-DSS-019", "A-SRC-102"], "A mesh does not prove a watertight manifold or engineering solid."),
    F("fam.boundary_representation", "boundary-representation solid", "engineering", "observation_record_shape", "engineering_3d", "solid", None, "missing", ["A-SRC-104"], "A triangle mesh is not equivalent to an exact topological B-rep solid."),
    F("fam.scene_graph", "3D scene graph", "engineering", "observation_record_shape", "engineering_3d", "scene", None, "missing", ["A-SRC-102"], "Render hierarchy and transforms do not establish product structure."),
    F("fam.gltf_asset", "glTF runtime asset", "engineering", "container_file_format", "engineering_3d", "scene", None, "missing", ["A-SRC-102"], "glTF is a runtime asset representation, not a CAD authoring model."),
    F("fam.cad_product_model", "managed CAD product model", "engineering", "observation_record_shape", "engineering_3d", "model", None, "missing", ["A-SRC-104"], "Geometry alone does not preserve product configuration or design intent."),
    F("fam.bim_facility_model", "BIM facility and infrastructure model", "engineering", "observation_record_shape", "engineering_3d", "model", None, "missing", ["A-SRC-103"], "BIM objects, spatial structure, systems, geometry, and property sets are distinct facets."),
    F("fam.digital_twin_snapshot", "digital-twin state snapshot", "engineering", "observation_record_shape", "mixed", "model", "shape.entity_snapshot", "overlap", ["A-SRC-095", "A-SRC-103"], "A state snapshot is not the physical asset or a causal simulator."),
    F("fam.simulation_scenario", "executable simulation scenario", "engineering", "observation_record_shape", "mixed", "model", "shape.simulation_experiment", "overlap", ["A-DSS-051", "A-SRC-147"], "Scenario syntax does not prove model validity or deterministic execution."),

    F("fam.biological_sequence", "biological sequence", "genomics", "observation_record_shape", "genomic", "sequence", None, "missing", ["A-SRC-111"], "A character string is not a sequence without alphabet, strand, and reference context."),
    F("fam.read_collection", "sequencing read collection", "genomics", "observation_record_shape", "genomic", "sequence", None, "missing", ["A-SRC-111"], "Read order does not imply genomic order."),
    F("fam.sequence_alignment", "sequence alignment records", "genomics", "observation_record_shape", "genomic", "table", None, "missing", ["A-SRC-111"], "Alignment position is meaningless without reference assembly and coordinate convention."),
    F("fam.variant_set", "genomic variant set", "genomics", "observation_record_shape", "genomic", "set", None, "missing", ["A-SRC-111", "A-SRC-112"], "Two variant strings are not equivalent without normalization and reference context."),
    F("fam.genotype_haplotype", "genotype or haplotype assertion", "genomics", "observation_record_shape", "genomic", "record", None, "missing", ["A-SRC-112"], "Allele set, phase, ploidy, and sample identity must remain explicit."),
    F("fam.phenopacket", "computable phenotype packet", "genomics", "observation_record_shape", "clinical", "bundle", None, "missing", ["A-SRC-113"], "Phenotype ontology codes do not prove diagnosis or causal variant."),
    F("fam.fhir_resource", "FHIR resource", "health", "observation_record_shape", "clinical", "record", "shape.schema_bound_message", "overlap", ["A-SRC-114"], "Base-resource conformance does not prove profile, terminology, or workflow conformance."),
    F("fam.fhir_bundle", "FHIR bundle", "health", "observation_record_shape", "clinical", "bundle", "shape.document_bundle", "overlap", ["A-SRC-114"], "FHIR bundle type changes processing and identity semantics."),
    F("fam.clinical_document", "clinical document", "health", "observation_record_shape", "clinical", "document", "shape.document_bundle", "overlap", ["A-SRC-116"], "A rendered clinical note is not equivalent to structured entries."),
    F("fam.genomic_report", "structured genomic report", "health", "observation_record_shape", "clinical", "bundle", None, "missing", ["A-SRC-115"], "Variant findings, study metadata, interpretations, and recommendations have separate authority."),

    F("fam.iso20022_message", "ISO 20022 financial message", "finance", "observation_record_shape", "financial", "message", "shape.schema_bound_message", "narrower", ["A-SRC-117"], "Schema-valid amount and date fields do not prove business-rule or market-practice conformance."),
    F("fam.fix_message", "FIX session/application message", "finance", "observation_record_shape", "financial", "message", "shape.schema_bound_message", "narrower", ["A-SRC-118"], "Tag presence does not establish session state or application semantics."),
    F("fam.fpml_trade", "FpML trade document", "finance", "observation_record_shape", "financial", "document", "shape.tree_document", "narrower", ["A-SRC-119"], "Trade economics cannot be inferred from XML structure alone."),
    F("fam.xbrl_instance", "XBRL fact instance", "finance", "observation_record_shape", "financial", "cube", "shape.statistical_observation_cube", "overlap", ["A-SRC-120"], "Facts require taxonomy concepts, units, periods, entities, and dimensions."),
    F("fam.order_book", "limit order book state", "finance", "observation_record_shape", "financial", "model", None, "missing", ["A-SRC-118"], "A price-level snapshot does not prove order-level queue priority."),
    F("fam.market_tick_stream", "market tick stream", "finance", "observation_record_shape", "financial", "stream", "shape.irregular_time_series", "narrower", ["A-SRC-118"], "Arrival order, exchange sequence, and event time are distinct."),
    F("fam.ledger_journal", "double-entry journal", "finance", "observation_record_shape", "financial", "table", "shape.transaction_record", "broader", ["A-SRC-117"], "A transaction record alone does not enforce balanced postings or account authority."),

    F("fam.archive_package", "generic archive member set", "packaging", "container_file_format", "binary", "archive", "shape.archive", "overlap", ["A-SRC-121", "A-SRC-122"], "Archive membership and path names do not establish document semantics."),
    F("fam.zip_container", "ZIP container", "packaging", "container_file_format", "binary", "archive", "shape.document_bundle", "disjoint", ["A-SRC-121"], "ZIP is a container, not a document bundle semantic type."),
    F("fam.tar_container", "PAX/TAR container", "packaging", "container_file_format", "binary", "archive", "shape.document_bundle", "disjoint", ["A-SRC-122"], "Archive order and paths are carrier details unless profiled."),
    F("fam.compressed_stream", "compressed byte stream", "packaging", "compression_protection", "binary", "archive", "shape.binary_blob", "disjoint", ["A-SRC-123", "A-SRC-124", "A-SRC-125"], "Compression does not change the decoded logical value when lossless."),
    F("fam.encrypted_envelope", "encrypted or signed envelope", "packaging", "compression_protection", "binary", "message", "shape.binary_blob", "disjoint", ["A-SRC-126", "A-SRC-127"], "Encryption and signatures do not grant authorization or prove payload truth."),
    F("fam.bagit_package", "BagIt manifested package", "packaging", "container_file_format", "metadata_evidence", "bundle", "shape.evidence_bundle", "overlap", ["A-DSS-067"], "Payload checksums prove byte integrity, not semantic completeness."),
    F("fam.oci_image_layout", "OCI image layout", "packaging", "container_file_format", "metadata_evidence", "bundle", "shape.container_image", "overlap", ["A-SRC-130"], "Content-addressed layers do not establish software behavior or provenance completeness."),

    F("fam.yaml_config", "YAML configuration graph", "code_config", "observation_record_shape", "code", "graph", "shape.configuration_document", "narrower", ["A-SRC-128"], "Implicit scalar resolution must not be guessed across YAML profiles."),
    F("fam.toml_config", "TOML configuration tables", "code_config", "observation_record_shape", "code", "tree", "shape.configuration_document", "narrower", ["A-SRC-129"], "Configuration keys do not establish domain ownership."),
    F("fam.source_code", "source code document", "code_config", "observation_record_shape", "code", "document", "shape.source_code_file", "equivalent", ["A-SRC-152"], "Source text equality is not program semantic equivalence."),
    F("fam.general_ast", "general abstract syntax tree", "code_config", "observation_record_shape", "code", "code_tree", "shape.abstract_syntax_tree", "equivalent", ["A-SRC-138"], "A formula AST is narrower than a language AST and trivia may be lost."),
    F("fam.compiler_ir", "compiler intermediate representation", "code_config", "observation_record_shape", "code", "graph", "shape.expression_dag", "broader", ["A-SRC-138"], "IR graph equality does not prove source-level behavioral equivalence."),
    F("fam.bytecode_module", "portable bytecode module", "code_config", "observation_record_shape", "code", "bundle", "shape.bytecode_module", "equivalent", ["A-SRC-137", "A-SRC-138"], "A binary module is not an opaque blob once its executable structure is interpreted."),
    F("fam.executable_object", "executable/object file", "code_config", "observation_record_shape", "code", "bundle", "shape.compiled_object", "overlap", ["A-SRC-136"], "Sections, symbols, relocations, and machine code cannot be reduced to uninterpreted bytes for analysis."),

    F("fam.dataset_manifest", "dataset manifest", "metadata", "observation_record_shape", "metadata_evidence", "record", "shape.dataset_manifest", "equivalent", ["A-DSS-060", "A-DSS-067"], "Manifest inclusion does not prove fitness or authority."),
    F("fam.annotation", "targeted annotation", "metadata", "observation_record_shape", "metadata_evidence", "record", "shape.annotation", "equivalent", ["A-DSS-068"], "Annotation target selection does not prove claim truth."),
    F("fam.evidence_bundle", "evidence bundle", "metadata", "observation_record_shape", "metadata_evidence", "bundle", "shape.evidence_bundle", "equivalent", ["A-DSS-060"], "Bundling evidence does not establish a valid inference."),
    F("fam.claim_evidence_graph", "claim-evidence graph", "metadata", "observation_record_shape", "metadata_evidence", "provenance", "shape.claim_evidence_graph", "equivalent", ["A-DSS-028"], "Graph connectivity does not establish evidential support strength."),
    F("fam.sbom", "software bill of materials", "metadata", "observation_record_shape", "metadata_evidence", "graph", "shape.evidence_bundle", "narrower", ["A-DSS-059", "A-SRC-131"], "SBOM completeness cannot be inferred from schema validation."),
    F("fam.c2pa_manifest", "content provenance manifest", "metadata", "observation_record_shape", "metadata_evidence", "provenance", "shape.evidence_bundle", "narrower", ["A-SRC-132"], "A valid signature authenticates the signer and bytes, not the depicted event."),
    F("fam.catalog_record", "dataset catalog record", "metadata", "observation_record_shape", "metadata_evidence", "record", None, "missing", ["A-SRC-133", "A-SRC-134"], "Catalog discoverability metadata does not prove dataset quality or access."),
    F("fam.data_contract", "data contract artifact", "metadata", "observation_record_shape", "metadata_evidence", "document", "shape.schema_contract", "overlap", ["A-DSS-040"], "A contract document is not an executable proof of conformance."),
    F("fam.immutable_ledger", "append-only immutable ledger", "metadata", "observation_record_shape", "metadata_evidence", "stream", "shape.immutable_ledger", "equivalent", ["A-DSS-028"], "Append-only integrity does not establish correctness of entries."),
]


PROFILE_DEFAULTS = {
    "core": ("strongly_schema_bound", "zero", "none", "value", "none", "none", "none", "immutable", "typed_absence", "none_declared", "none", "none"),
    "tables": ("strongly_schema_bound", "two", "none", "row", "composite", "primary", "none", "snapshot", "typed_absence", "unknown", "none", "required_external"),
    "documents": ("mixed", "mixed_or_variable", "tree", "document", "standard_defined", "none", "document_order", "versioned", "structural_absence", "unknown", "none", "none"),
    "email": ("externally_profiled", "mixed_or_variable", "tree", "message", "standard_defined", "standard_defined", "document_order", "append_only", "structural_absence", "unknown", "none", "none"),
    "messages": ("strongly_schema_bound", "mixed_or_variable", "tree", "message", "standard_defined", "standard_defined", "standard_defined", "schema_evolution", "structural_absence", "unknown", "none", "none"),
    "graphs": ("strongly_schema_bound", "mixed_or_variable", "directed_graph", "relationship", "standard_defined", "membership", "none", "versioned", "structural_absence", "unknown", "none", "none"),
    "events": ("externally_profiled", "one", "linear", "event", "standard_defined", "temporal", "event_time", "append_only", "typed_absence", "unknown", "none", "none"),
    "telemetry": ("externally_profiled", "one", "mixed", "observation", "contextual", "standard_defined", "event_time", "append_only", "typed_absence", "quality_flag", "none", "physical_unit"),
    "time_series": ("externally_profiled", "one", "linear", "observation", "composite", "temporal", "event_time", "append_only", "typed_absence", "unknown", "temporal_reference", "required_external"),
    "signals": ("externally_profiled", "one", "linear", "sample", "positional", "coordinate", "event_time", "append_only", "typed_absence", "quality_flag", "temporal_reference", "sample_rate"),
    "media": ("externally_profiled", "mixed_or_variable", "grid", "sample", "positional", "coordinate", "standard_defined", "immutable", "mask", "unknown", "pixel", "pixel_scale"),
    "geospatial": ("externally_profiled", "mixed_or_variable", "mixed", "feature", "standard_defined", "standard_defined", "none", "versioned", "typed_absence", "measurement_uncertainty", "required_external", "required_external"),
    "arrays": ("strongly_schema_bound", "n_dimensional", "grid", "cell", "positional", "coordinate", "standard_defined", "mutable_in_place", "mask", "unknown", "index", "required_external"),
    "scientific": ("externally_profiled", "n_dimensional", "mixed", "observation", "standard_defined", "coordinate", "standard_defined", "versioned", "mixed", "measurement_uncertainty", "required_external", "required_external"),
    "engineering": ("strongly_schema_bound", "three", "mixed", "model_object", "versioned", "standard_defined", "standard_defined", "versioned", "structural_absence", "measurement_uncertainty", "engineering_crs", "physical_unit"),
    "genomics": ("externally_profiled", "one", "linear", "variant", "standard_defined", "coordinate", "standard_defined", "versioned", "typed_absence", "quality_flag", "genomic_reference", "none"),
    "health": ("strongly_schema_bound", "mixed_or_variable", "mixed", "record", "standard_defined", "standard_defined", "standard_defined", "versioned", "typed_absence", "quality_flag", "none", "physical_unit"),
    "finance": ("strongly_schema_bound", "mixed_or_variable", "mixed", "transaction", "standard_defined", "standard_defined", "event_time", "versioned", "typed_absence", "unknown", "none", "currency"),
    "packaging": ("opaque", "mixed_or_variable", "tree", "file_member", "standard_defined", "standard_defined", "incidental", "immutable", "structural_absence", "none_declared", "none", "none"),
    "code_config": ("strongly_schema_bound", "mixed_or_variable", "tree", "record", "versioned", "standard_defined", "document_order", "versioned", "structural_absence", "none_declared", "none", "none"),
    "metadata": ("externally_profiled", "mixed_or_variable", "directed_graph", "evidence_item", "standard_defined", "standard_defined", "standard_defined", "versioned", "typed_absence", "quality_flag", "none", "none"),
}


PROFILE_FIELDS = ["schema_posture", "dimensionality", "logical_topology", "grain", "identity_model", "key_model", "ordering", "change_model", "missingness", "uncertainty", "coordinate_reference", "unit_semantics"]


OPS = {
    "core": [("validate", "valid", "op.validate"), ("canonicalize", "partial", "op.canonicalize"), ("compare", "partial", "op.compare")],
    "tables": [("project", "valid", "op.project"), ("filter", "partial", "op.filter"), ("join", "partial", "op.join"), ("aggregate", "partial", "op.aggregate")],
    "documents": [("parse", "partial", "op.parse"), ("render", "partial", "op.render"), ("extract_structure", "partial", None), ("redact", "partial", "op.redact")],
    "email": [("parse_message", "partial", "op.parse"), ("decode_mime", "partial", "op.decode"), ("thread", "partial", None), ("verify_sender", "invalid_without_external_evidence", None)],
    "messages": [("parse", "partial", "op.parse"), ("validate", "partial", "op.validate"), ("migrate_schema", "partial", "op.migrate_schema"), ("semantic_compare", "invalid_without_profile", "op.semantic_diff")],
    "graphs": [("traverse", "partial", "op.traverse"), ("subgraph", "partial", "op.subgraph"), ("canonicalize", "partial", "op.canonicalize_graph"), ("join", "partial", None)],
    "events": [("watermark", "partial", "op.watermark"), ("replay", "partial", "op.replay"), ("deduplicate", "partial", "op.deduplicate"), ("infer_event_time", "invalid", None)],
    "telemetry": [("aggregate", "partial", "op.aggregate"), ("correlate", "partial", "op.correlate"), ("downscale_histogram", "partial", "op.downscale_histogram"), ("infer_causality", "invalid", None)],
    "time_series": [("window", "partial", "op.window"), ("resample", "partial", "op.resample"), ("align", "partial", "op.align"), ("interpolate", "partial", "op.interpolate")],
    "signals": [("filter", "partial", "op.filter_signal"), ("fft", "partial", "op.fft"), ("resample", "partial", "op.resample"), ("infer_clock", "invalid", None)],
    "media": [("decode", "partial", "op.decode"), ("transcode", "lossy_or_partial", "op.transcode"), ("select_channel", "partial", "op.select_channel"), ("render", "partial", "op.render")],
    "geospatial": [("reproject", "partial", "op.reproject"), ("spatial_join", "partial", "op.spatial_join"), ("simplify", "lossy_or_partial", "op.simplify"), ("infer_crs", "invalid", None)],
    "arrays": [("slice", "partial", "op.slice"), ("reshape", "partial", "op.reshape"), ("transpose", "partial", "op.transpose"), ("sparse_convert", "partial", "op.sparse_convert")],
    "scientific": [("slice", "partial", "op.slice"), ("rechunk", "partial", "op.rechunk"), ("unit_convert", "partial", "op.convert_unit"), ("infer_axis_semantics", "invalid", None)],
    "engineering": [("tessellate", "lossy_or_partial", None), ("validate_topology", "partial", "op.validate"), ("transform", "partial", None), ("infer_design_intent", "invalid", None)],
    "genomics": [("normalize_variant", "partial", None), ("align", "partial", "op.align"), ("project_reference", "partial", None), ("infer_reference_assembly", "invalid", None)],
    "health": [("validate_profile", "partial", "op.validate"), ("terminology_validate", "partial", None), ("reconcile", "partial", "op.reconcile"), ("infer_diagnosis", "invalid", None)],
    "finance": [("validate_market_practice", "partial", "op.validate"), ("reconcile", "partial", "op.reconcile"), ("aggregate", "partial", "op.aggregate"), ("infer_legal_finality", "invalid", None)],
    "packaging": [("unpack", "partial", "op.unpack"), ("verify_digest", "partial", "op.verify_digest"), ("decode", "partial", "op.decode"), ("infer_payload_semantics", "invalid", None)],
    "code_config": [("parse", "partial", "op.parse"), ("typecheck", "partial", "op.typecheck"), ("semantic_diff", "partial", "op.semantic_diff"), ("infer_behavioral_equivalence", "invalid", None)],
    "metadata": [("validate", "partial", "op.validate"), ("provenance_trace", "partial", "op.provenance_trace"), ("verify_digest", "partial", "op.verify_digest"), ("infer_truth", "invalid", None)],
}


def axis_profile(fam: dict) -> dict[str, str]:
    values = dict(zip(PROFILE_FIELDS, PROFILE_DEFAULTS[fam["domain_cluster"]]))
    values.update({
        "abstraction_layer": fam["expected_registry_layer"],
        "modality": fam["modality"],
        "logical_shape": fam["logical_shape"],
        "time_role": "event_time" if fam["domain_cluster"] in {"events", "telemetry", "finance"} else ("media_time" if fam["domain_cluster"] == "media" else ("observation_time" if fam["domain_cluster"] in {"time_series", "signals", "scientific"} else "none")),
        "carrier": "mixed",
        "encoding": "standard_defined" if fam["expected_registry_layer"] in {"encoding", "container_file_format", "physical_layout", "compression_protection"} else "none",
        "container_file_format": "standard_defined" if fam["expected_registry_layer"] == "container_file_format" else "none",
        "physical_layout": "standard_defined" if fam["expected_registry_layer"] == "physical_layout" else "unspecified",
        "compression_protection": "external" if fam["expected_registry_layer"] != "compression_protection" else "mixed",
        "access_locality": "provider_dependent",
        "evolution": "profile_defined",
        "provenance": "external",
        "integrity": "external",
        "authority": "unknown",
    })
    values.update(fam.get("overrides", {}))
    return values


def canonical_coverage(axis_id: str, fam: dict, target: dict | None) -> tuple[str, str]:
    if fam["relation"] == "missing":
        return "missing", "No exact canonical record is declared by this audit."
    if fam["relation"] == "disjoint":
        return "out_of_scope_by_layer", "Closest canonical record is deliberately disjoint at another abstraction layer."
    if target is None:
        return "missing", "Declared target is unresolved."
    if fam["target_kind"] == "type_record":
        explicit = {"missingness", "uncertainty", "time_role", "provenance", "carrier"}
    else:
        explicit = {"logical_shape", "logical_topology", "key_model", "ordering", "time_role", "change_model"}
    if axis_id in explicit:
        return "explicit", "Canonical record has a dedicated contract surface for this axis."
    if axis_id in {"abstraction_layer", "modality", "dimensionality", "grain", "identity_model"}:
        return "partial", "Canonical definition/family may constrain this axis but has no normalized per-record axis cell."
    return "not_explicit", "Canonical record lacks a normalized explicit field for this independent axis."


def build() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "schemas").mkdir(exist_ok=True)

    canonical_sources = load_jsonl(CANONICAL / "sources.jsonl")
    sources = []
    for rec in canonical_sources:
        copied = dict(rec)
        copied["canonical_source_id"] = rec["source_id"]
        copied["source_id"] = "A-" + rec["source_id"]
        copied["standard_family"] = "canonical_baseline"
        copied["publication_year"] = None
        sources.append(copied)
    sources.extend(EXTRA_SOURCES)
    sources.sort(key=lambda r: r["source_id"])

    axes_doc = {
        "audit_id": "san.domain-atlas.data-modality-gap-audit.axes",
        "edition": 1,
        "status": "candidate_audit",
        "non_cartesian_law": "Cells record independently observed expectations; their combinations are not manufactured named types.",
        "unstructured_law": "Unstructured is only a weak/deferred schema and interpretation posture, never absence of structure; all data has physical and logical structure.",
        "axes": [
            {"axis_id": aid, "layer": layer, "values": vals, "independence_rule": rule}
            for aid, layer, vals, rule in AXES
        ],
    }
    dump_json(ROOT / "classification-axes.json", axes_doc)

    schema_postures = [
        {
            "posture_id": "POSTURE-001", "input_label": "structured", "normalized_postures": ["strongly_schema_bound"],
            "is_modality": False, "structure_absent": False,
            "audit_rule": "Count coverage only when schema edition, constraints, grain, identity, and semantic owner are explicit; syntax validity alone is insufficient.",
            "examples": ["relational schema", "Protocol Buffers message", "FHIR profile"],
            "evidence_refs": ["A-DSS-001", "A-DSS-006", "A-SRC-114"],
        },
        {
            "posture_id": "POSTURE-002", "input_label": "semi-structured", "normalized_postures": ["self_describing", "schema_on_read", "mixed"],
            "is_modality": False, "structure_absent": False,
            "audit_rule": "Decompose this umbrella label into explicit syntax, recursive structure, schema availability, evolution, and interpretation authority.",
            "examples": ["JSON document", "XML infoset", "YAML representation graph"],
            "evidence_refs": ["A-DSS-008", "A-DSS-009", "A-SRC-128"],
        },
        {
            "posture_id": "POSTURE-003", "input_label": "so-called unstructured", "normalized_postures": ["weakly_declared", "opaque"],
            "is_modality": False, "structure_absent": False,
            "audit_rule": "Treat the label only as absent/weak enterprise interpretation; preserve document, media, signal, code, container, and byte structure and require a typed interpreter before operations.",
            "examples": ["free-form document", "email body", "image", "audio", "opaque binary"],
            "evidence_refs": ["A-SRC-071", "A-SRC-078", "A-SRC-083", "A-DSS-045"],
        },
    ]
    dump_jsonl(ROOT / "schema-posture-audit.jsonl", schema_postures)

    shape_records = {r["shape_id"]: r for r in load_jsonl(CANONICAL / "shape-records.jsonl")}
    type_records = {r["type_id"]: r for r in load_jsonl(CANONICAL / "type-records.jsonl")}
    op_records = {r["operation_id"]: r for r in load_jsonl(CANONICAL / "operation-totality-matrix.jsonl")}
    source_ids = {r["source_id"] for r in sources}

    families, tensor, crosswalks, op_gaps, assertions = [], [], [], [], []
    relation_counter = Counter()
    cell_counter = Counter()
    for index, fam in enumerate(FAMILY_SPECS, 1):
        target = (shape_records if fam["target_kind"] == "shape_record" else type_records).get(fam["target_id"])
        family_record = {
            "family_id": fam["family_id"],
            "label": fam["label"],
            "domain_cluster": fam["domain_cluster"],
            "candidate_kind": "coverage_expectation_not_registry_entry",
            "expected_registry_layer": fam["expected_registry_layer"],
            "description": f"Audit expectation for {fam['label']} with layer boundaries and refusal rules.",
            "required_distinctions": ["semantic meaning", "logical/observation shape", "representation binding"],
            "invalid_inferences": [fam["invalid_inference"]],
            "evidence_refs": fam["evidence_refs"],
            "status": "candidate_audit_expectation",
        }
        families.append(family_record)

        profile = axis_profile(fam)
        cells = []
        for axis_id, _, allowed, _ in AXES:
            expected = profile[axis_id]
            assert expected in allowed, (fam["family_id"], axis_id, expected)
            coverage, note = canonical_coverage(axis_id, fam, target)
            cells.append({
                "axis_id": axis_id,
                "expected_values": [expected],
                "canonical_coverage": coverage,
                "canonical_refs": [fam["target_id"]] if fam["target_id"] else [],
                "note": note,
            })
            cell_counter[coverage] += 1
        tensor.append({
            "tensor_id": "tensor." + fam["family_id"].split(".", 1)[1],
            "family_id": fam["family_id"],
            "axis_cells": cells,
            "cell_count": len(cells),
            "non_cartesian": True,
        })

        cw = {
            "crosswalk_id": f"cw.{index:03d}",
            "family_id": fam["family_id"],
            "target_registry": "san.domain-atlas.data-shapes",
            "target_kind": fam["target_kind"],
            "target_id": fam["target_id"],
            "relation": fam["relation"],
            "comparison_basis": ["abstraction layer", "element/grain contract", "topology", "order/time/change laws", "operation/refusal surface"],
            "law_comparison": {
                "abstraction_layer": "match" if fam["relation"] == "equivalent" else ("unresolved" if fam["relation"] == "missing" else "mismatch_or_refinement"),
                "grain_identity": "manual_match" if fam["relation"] == "equivalent" else fam["relation"],
                "topology": "manual_match" if fam["relation"] == "equivalent" else fam["relation"],
                "order_time_change": "manual_match" if fam["relation"] == "equivalent" else fam["relation"],
                "operation_refusals": "manual_match_with_audit_extensions" if fam["relation"] == "equivalent" else fam["relation"],
                "conclusion": fam["relation"],
            },
            "equivalence_justification": (f"The audit expectation for {fam['label']} and {fam['target_id']} occupy the same logical shape layer and have manually compared grain, topology, order/time/change, and refusal surfaces; the label was not used as evidence." if fam["relation"] == "equivalent" else None),
            "name_equivalence_used": False,
            "rationale": fam["invalid_inference"],
            "evidence_refs": fam["evidence_refs"],
            "status": "candidate_manual_law_comparison",
        }
        crosswalks.append(cw)
        relation_counter[fam["relation"]] += 1

        assertions.append({
            "assertion_id": f"ASSERT-FAMILY-{index:03d}",
            "assertion_kind": "invalid_inference" if "not" in fam["invalid_inference"].lower() or "cannot" in fam["invalid_inference"].lower() else "coverage_boundary",
            "subject_family_id": fam["family_id"],
            "claim": fam["invalid_inference"],
            "disposition": "compiler_must_refuse_or_require_profile",
            "canonical_refs": [fam["target_id"]] if fam["target_id"] else [],
            "evidence_refs": fam["evidence_refs"],
            "falsifier_or_closure": "An editioned law and conformance fixture may narrow this refusal for its declared scope.",
            "priority": "high" if fam["relation"] in {"missing", "disjoint"} else "medium",
        })

        for op_index, (op_name, validity, canonical_op) in enumerate(OPS[fam["domain_cluster"]], 1):
            op_gaps.append({
                "operation_gap_id": f"OPG-{index:03d}-{op_index}",
                "family_id": fam["family_id"],
                "operation": op_name,
                "expected_validity": validity,
                "canonical_operation_id": canonical_op,
                "canonical_operation_exists": canonical_op in op_records if canonical_op else False,
                "gap_kind": "missing_operation" if not canonical_op else ("precondition_profile_required" if validity != "valid" else "mapped_review_required"),
                "invalid_inference": fam["invalid_inference"] if validity.startswith("invalid") else None,
                "comparison_method": "explicit declared mapping; no name-based equivalence",
                "evidence_refs": fam["evidence_refs"],
            })

    for record in families:
        assert set(record["evidence_refs"]) <= source_ids

    dump_jsonl(ROOT / "modality-family-expectations.jsonl", families)
    dump_jsonl(ROOT / "coverage-tensor.jsonl", tensor)
    dump_jsonl(ROOT / "canonical-crosswalk.jsonl", crosswalks)
    dump_jsonl(ROOT / "operation-type-gaps.jsonl", op_gaps)

    representation_findings = [
        ("PDF", "container_file_format", "fixed-layout document object graph", "PDF bytes/pages do not prove reading order or editable text structure", ["fam.pdf_program", "fam.fixed_layout_document"]),
        ("DOCX", "container_file_format", "rich-text logical document", "ZIP/OOXML packaging is distinct from the document's semantic structure", ["fam.ooxml_wordprocessing"]),
        ("XLSX/ODS", "container_file_format", "workbook plus weakly typed cell regions", "A workbook is neither one table nor one cube", ["fam.ooxml_spreadsheet", "fam.odf_spreadsheet", "fam.spreadsheet_workbook"]),
        ("CSV", "encoding", "table candidate", "Dialect, header, type, null, key, and grain profiles are external", ["fam.csv_dialect"]),
        ("JSON", "encoding", "tree/graph carrier", "JSON syntax is not the category 'semi-structured' and does not supply domain meaning", ["fam.json_document"]),
        ("XML", "encoding", "infoset/tree carrier", "XML serialization is distinct from the infoset and schema-bound domain object", ["fam.xml_infoset"]),
        ("YAML", "encoding", "representation graph", "Aliases make graph identity possible and presentation comments are not representation nodes", ["fam.yaml_representation", "fam.yaml_config"]),
        ("Protobuf", "encoding", "schema-bound message", "Wire field compatibility is not semantic compatibility", ["fam.protobuf_message"]),
        ("Avro", "encoding", "schema-bound record", "Reader/writer resolution is not domain-safe evolution", ["fam.avro_record"]),
        ("Arrow", "physical_layout", "record batch/table carrier", "Columnar buffers are not a semantic relation", ["fam.arrow_record_batch"]),
        ("Parquet", "physical_layout", "columnar file binding", "Row groups, pages, and statistics are representation contracts", ["fam.parquet_column_chunk"]),
        ("GeoParquet", "physical_layout", "feature-table binding", "CRS/geometry metadata binds but does not replace feature semantics", ["fam.geoparquet_binding"]),
        ("email", "observation_record_shape", "IMF headers/body plus separate transport envelope", "Header sender is not SMTP envelope sender or verified actor", ["fam.internet_email"]),
        ("MIME", "container_file_format", "multipart body tree", "Media-type labels require decoding and semantic profiles", ["fam.mime_multipart"]),
        ("HDF5", "container_file_format", "linked group/dataset graph", "Dataset, dataspace, datatype, link, attribute, and chunk layout remain separate", ["fam.hdf5_dataset_graph"]),
        ("netCDF", "observation_record_shape", "named-dimension scientific dataset", "Its data model and CF meaning exceed a raw N-D array", ["fam.netcdf_dataset"]),
        ("Zarr", "container_file_format", "chunked arrays and groups", "Chunks/codecs/store keys are not array semantic axes", ["fam.zarr_hierarchy"]),
        ("FITS", "container_file_format", "ordered heterogeneous HDUs", "One FITS file may contain images and tables", ["fam.fits_hdu_list"]),
        ("DICOM", "container_file_format", "clinical imaging information model", "Pixel data, instances, series, studies, and patient context cannot be collapsed", ["fam.dicom_study_series"]),
        ("OpenEXR", "container_file_format", "multipart multichannel/deep image", "Part, view, channel, sample, tile, and compression are independent axes", ["fam.openexr_container", "fam.deep_image"]),
        ("ISO BMFF", "container_file_format", "timed tracks", "Container timing and codec decode semantics are distinct", ["fam.timed_media_container", "fam.video_track", "fam.audio_track"]),
        ("glTF", "container_file_format", "runtime scene asset", "A runtime asset is not a CAD/BIM authoring or product model", ["fam.gltf_asset", "fam.scene_graph"]),
        ("IFC", "observation_record_shape", "BIM facility model", "Schema, exchange serialization, object graph, geometry, and properties are distinct", ["fam.bim_facility_model"]),
        ("STEP AP242", "observation_record_shape", "managed product model", "The physical file syntax is not the product lifecycle semantics", ["fam.cad_product_model"]),
        ("ZIP/TAR", "container_file_format", "archive members", "Archive packaging is not document semantics", ["fam.zip_container", "fam.tar_container"]),
        ("gzip/zstd/brotli", "compression_protection", "compressed bytes", "Lossless compression must not create a new logical data type", ["fam.compressed_stream"]),
        ("CMS/COSE", "compression_protection", "protected envelope", "Cryptographic validity is not authorization, provenance completeness, or truth", ["fam.encrypted_envelope"]),
        ("VCF", "encoding", "variant assertions", "Lexical records require reference and normalization laws", ["fam.variant_set"]),
        ("FHIR", "observation_record_shape", "profiled clinical resources/bundles", "JSON/XML carrier choice is not clinical conformance", ["fam.fhir_resource", "fam.fhir_bundle"]),
        ("ISO 20022/FIX", "observation_record_shape", "financial business messages", "Schema-valid fields do not establish market practice or settlement finality", ["fam.iso20022_message", "fam.fix_message"]),
    ]
    rep_records = []
    for i, (term, mistaken, actual, risk, fams) in enumerate(representation_findings, 1):
        refs = sorted({ref for fam in FAMILY_SPECS if fam["family_id"] in fams for ref in fam["evidence_refs"]})
        rep_records.append({
            "finding_id": f"RLF-{i:03d}", "term": term, "commonly_confused_as": mistaken,
            "required_separation": actual, "risk": risk, "family_ids": fams, "evidence_refs": refs,
            "compiler_action": "preserve layers and require an explicit representation binding",
        })
        assertions.append({
            "assertion_id": f"ASSERT-LAYER-{i:03d}", "assertion_kind": "representation_layer_confusion",
            "subject_family_id": fams[0], "claim": risk, "disposition": "preserve_layer_boundary",
            "canonical_refs": [], "evidence_refs": refs,
            "falsifier_or_closure": "Only an editioned binding may prove a scoped reversible mapping; it cannot erase the layers.",
            "priority": "high",
        })
    dump_jsonl(ROOT / "representation-layer-findings.jsonl", rep_records)

    # Explicit audit of the canonical registry's representation crosswalks.  The keys are
    # finding IDs, not fuzzy representation names; additions require a reviewed source edit.
    canonical_rep_links = {
        "RLF-001": ["xwalk.048"], "RLF-002": ["xwalk.050"], "RLF-003": ["xwalk.049", "xwalk.050"],
        "RLF-004": ["xwalk.011"], "RLF-005": ["xwalk.001", "xwalk.002", "xwalk.003"],
        "RLF-006": ["xwalk.010"], "RLF-007": ["xwalk.054"], "RLF-008": ["xwalk.009"],
        "RLF-009": ["xwalk.008"], "RLF-010": ["xwalk.005", "xwalk.006"], "RLF-011": ["xwalk.007"],
        "RLF-012": [], "RLF-013": ["xwalk.045", "xwalk.047"], "RLF-014": ["xwalk.046"],
        "RLF-015": ["xwalk.014"], "RLF-016": ["xwalk.015"], "RLF-017": ["xwalk.016"],
        "RLF-018": [], "RLF-019": ["xwalk.023"], "RLF-020": [], "RLF-021": ["xwalk.028"],
        "RLF-022": [], "RLF-023": [], "RLF-024": [], "RLF-025": ["xwalk.056"],
        "RLF-026": ["xwalk.057"], "RLF-027": [], "RLF-028": [], "RLF-029": [], "RLF-030": [],
    }
    partial_rep_findings = {"RLF-003", "RLF-013", "RLF-025", "RLF-026"}
    canonical_rep_audit = []
    for rec in rep_records:
        links = canonical_rep_links[rec["finding_id"]]
        canonical_rep_audit.append({
            "representation_audit_id": "CRA-" + rec["finding_id"].split("-")[-1],
            "finding_id": rec["finding_id"],
            "canonical_crosswalk_ids": links,
            "coverage": "missing" if not links else ("partial" if rec["finding_id"] in partial_rep_findings else "explicit"),
            "comparison_basis": ["source and target layers", "preserved semantics", "loss-at-risk", "direction", "test obligations"],
            "name_equivalence_used": False,
            "gap": "No exact canonical representation crosswalk." if not links else ("Only a subset of the grouped representations has an exact canonical crosswalk." if rec["finding_id"] in partial_rep_findings else None),
        })
    dump_jsonl(ROOT / "canonical-representation-audit.jsonl", canonical_rep_audit)

    finding_specs = [
        ("overlap", "document logical/format boundary", ["fam.fixed_layout_document", "fam.pdf_program", "fam.spreadsheet_workbook", "fam.ooxml_spreadsheet"], "Canonical logical shapes now exist; adjudicate whether format-specific records are bindings or true logical specializations."),
        ("missing", "email transport envelope", ["fam.email_transport_envelope", "fam.mailbox_archive"], "Keep SMTP envelope distinct from message headers and add an explicit mbox/framed-message binding profile."),
        ("missing", "scientific compound datasets", ["fam.hdf5_dataset_graph", "fam.netcdf_dataset", "fam.fits_hdu_list"], "Add linked dataset/group and heterogeneous-HDU constructors."),
        ("missing", "engineering geometry", ["fam.boundary_representation", "fam.scene_graph", "fam.cad_product_model", "fam.bim_facility_model"], "Add exact solid, scene, product, and facility model shapes separately."),
        ("missing", "genomics", ["fam.biological_sequence", "fam.sequence_alignment", "fam.variant_set", "fam.genotype_haplotype"], "Add reference-aware genomic observation/collection shapes in a vertical extension."),
        ("missing", "financial state", ["fam.order_book", "fam.ledger_journal"], "Add order-book and balanced-journal shapes in a finance extension."),
        ("missing", "timed text and symbolic media", ["fam.caption_track", "fam.musical_event_sequence"], "Add symbolic/timed-text shapes distinct from waveforms."),
        ("missing", "deep image", ["fam.deep_image"], "Add variable-sample-per-pixel image shape."),
        ("split", "generic document", ["fam.rich_text_document", "fam.fixed_layout_document", "fam.html_dom"], "Split editable rich text, fixed-layout page object graph, and live DOM semantics."),
        ("split", "schema-bound message", ["fam.protobuf_message", "fam.avro_record", "fam.api_exchange_message", "fam.fhir_resource"], "Keep a common constructor but split field identity/evolution/profile laws."),
        ("split", "binary blob interpretation", ["fam.bytecode_module", "fam.executable_object", "fam.encrypted_envelope"], "Decoded executable/protected structures need typed interpretation rather than opaque fallback."),
        ("split", "image family", ["fam.raster_image", "fam.label_image", "fam.deep_image", "fam.voxel_volume"], "Distinguish continuous color, categorical labels, deep samples, and volumetric coordinates."),
        ("split", "point/mesh/solid", ["fam.point_cloud", "fam.surface_mesh", "fam.boundary_representation"], "Do not treat sampling, tessellation, and exact solid topology as interchangeable."),
        ("merge", "CSV table specialization", ["fam.csv_dialect", "fam.relational_relation"], "Do not mint CSV as a logical type; merge only the logical table expectation and retain the encoding binding."),
        ("merge", "GeoParquet feature table specialization", ["fam.geoparquet_binding", "fam.feature_collection"], "Do not mint a GeoParquet semantic type; bind its layout to an explicit feature-table shape."),
        ("merge", "NIfTI voxel specialization", ["fam.nifti_neurovolume", "fam.voxel_volume"], "Keep NIfTI as a representation/vertical profile over voxel volume rather than a horizontal core shape."),
        ("merge", "seismic sampled-signal specialization", ["fam.seismic_waveform", "fam.sampled_signal"], "Use vertical qualifiers on sampled signal unless new laws demand a separate core constructor."),
        ("overlap", "table versus data frame", ["fam.relational_relation", "fam.data_frame"], "Adjudicate equality, labels, row identity, and missingness before any alias claim."),
        ("overlap", "raster image versus spatial raster", ["fam.raster_image", "fam.spatial_raster"], "Same grid topology can carry incompatible color and geospatial coverage semantics."),
        ("overlap", "tree document versus YAML graph", ["fam.tree_document", "fam.yaml_representation"], "Aliases/references can make YAML broader than a tree."),
        ("overlap", "document bundle versus archive", ["fam.compound_document", "fam.archive_package"], "Logical part roles and generic archive membership are not equivalent."),
        ("overlap", "event log versus telemetry log", ["fam.log_record", "fam.telemetry_log_stream", "fam.audit_trail"], "Operational log, business event, and audit evidence have different authorities and completeness laws."),
        ("overlap", "RDF graph versus dataset", ["fam.rdf_graph", "fam.rdf_dataset"], "Named graph identity and dataset scope must not be erased."),
        ("overlap", "tensor versus coverage", ["fam.dense_tensor", "fam.coverage"], "Coverage domain/range semantics are not implied by N-D indexing."),
    ]
    findings = []
    for i, (kind, area, fams, action) in enumerate(finding_specs, 1):
        refs = sorted({ref for fam in FAMILY_SPECS if fam["family_id"] in fams for ref in fam["evidence_refs"]})
        findings.append({"finding_id": f"GAP-{i:03d}", "finding_type": kind, "area": area, "family_ids": fams,
                         "finding": action, "recommended_action": action, "evidence_refs": refs, "status": "open_review"})
    dump_jsonl(ROOT / "gap-findings.jsonl", findings)

    vertical_specs = [
        ("retail", "customer order fact table", ["fam.fact_table", "fam.dimension_table"], "order-line grain and currency remain explicit"),
        ("banking", "ISO 20022 payment and ledger reconciliation", ["fam.iso20022_message", "fam.ledger_journal"], "message validity is weaker than posting finality"),
        ("capital_markets", "order-book reconstruction", ["fam.fix_message", "fam.order_book", "fam.market_tick_stream"], "exchange sequence and event time remain distinct"),
        ("healthcare", "diagnostic report with images", ["fam.fhir_bundle", "fam.clinical_document", "fam.dicom_study_series"], "narrative, atomic observations, and pixel data remain linked but distinct"),
        ("clinical_genomics", "genomic diagnostic report", ["fam.genomic_report", "fam.variant_set", "fam.genotype_haplotype"], "reference assembly and interpretation authority are mandatory"),
        ("life_sciences", "microscopy screen", ["fam.ome_microscopy", "fam.image_pyramid", "fam.label_image"], "axis, transform, and label ontologies are preserved"),
        ("astronomy", "FITS observation product", ["fam.fits_hdu_list", "fam.raster_image", "fam.keyed_relation"], "heterogeneous HDUs remain typed"),
        ("earth_science", "climate reanalysis cube", ["fam.netcdf_dataset", "fam.grid_coverage", "fam.labeled_array"], "CF coordinates, units, calendars, and cell methods are required"),
        ("geospatial", "mobility trajectory analytics", ["fam.trajectory", "fam.moving_feature", "fam.spatial_network"], "object identity, time, CRS, and network map matching are declared"),
        ("smart_city", "3D city asset catalog", ["fam.city_model", "fam.three_d_tiles", "fam.stac_catalog"], "semantic city objects are not reduced to render LODs"),
        ("manufacturing", "CAD/BIM digital thread", ["fam.cad_product_model", "fam.bim_facility_model", "fam.digital_twin_snapshot"], "configuration, design intent, state, and geometry remain separate"),
        ("automotive", "vehicle measurement and scenario", ["fam.mdf_measurement", "fam.simulation_scenario", "fam.multichannel_signal"], "clock, channel calibration, and scenario model version are explicit"),
        ("energy", "grid sensor telemetry", ["fam.sensor_observation", "fam.metric_stream", "fam.regular_time_series"], "unit, feature of interest, clock, and aggregation temporality are explicit"),
        ("telecom", "distributed service observability", ["fam.trace_span_graph", "fam.telemetry_log_stream", "fam.exponential_histogram"], "correlation does not imply causality"),
        ("media", "broadcast master", ["fam.timed_media_container", "fam.video_track", "fam.audio_track", "fam.caption_track"], "track timelines, codecs, language, and accessibility roles remain explicit"),
        ("publishing", "accessible digital publication", ["fam.epub_publication", "fam.html_dom", "fam.rich_text_document"], "reading order and accessibility semantics are tested"),
        ("legal", "signed evidence package", ["fam.pdf_program", "fam.encrypted_envelope", "fam.evidence_bundle"], "signature scope, custody, rendering, and claim authority remain separate"),
        ("cybersecurity", "software supply-chain evidence", ["fam.sbom", "fam.c2pa_manifest", "fam.oci_image_layout"], "digest identity does not prove runtime behavior or completeness"),
        ("research", "reproducible scientific package", ["fam.bagit_package", "fam.dataset_manifest", "fam.provenance_graph"], "payload integrity and derivation claims remain explicit"),
        ("software_engineering", "source-to-binary analysis", ["fam.source_code", "fam.general_ast", "fam.compiler_ir", "fam.executable_object"], "text, syntax, IR, and executable layouts are not equivalent"),
    ]
    verticals = []
    fam_by_id = {f["family_id"]: f for f in families}
    for i, (vertical, case, fams, law) in enumerate(vertical_specs, 1):
        refs = sorted({ref for fid in fams for ref in fam_by_id[fid]["evidence_refs"]})
        verticals.append({"sample_id": f"VERT-{i:03d}", "vertical": vertical, "case": case, "family_ids": fams,
                          "coverage_law": law, "evidence_refs": refs, "status": "sample_not_universal_proof"})
    dump_jsonl(ROOT / "vertical-case-samples.jsonl", verticals)

    innovation_specs = [
        (2021, "YAML 1.2.2 clarification and renewed specification process", "A-SRC-128", ["fam.yaml_representation"]),
        (2021, "OpenAPI 3.1 aligns its schema vocabulary with JSON Schema 2020-12", "A-SRC-145", ["fam.api_exchange_message"]),
        (2023, "Protocol Buffers Editions introduces edition-scoped language evolution", "A-SRC-140", ["fam.protobuf_message"]),
        (2021, "SDMX 3.0 expands the statistical information model", "A-SRC-142", ["fam.statistical_cube"]),
        (2021, "OGC SensorThings API 1.1 profiles observations and sensing entities", "A-SRC-146", ["fam.sensor_observation"]),
        (2021, "STAC 1.0 stabilizes spatiotemporal asset catalog structures", "A-SRC-099", ["fam.stac_catalog"]),
        (2021, "glTF 2.0.1 consolidates runtime 3D scene asset representation", "A-SRC-102", ["fam.gltf_asset"]),
        (2021, "OpenEXR 3 generation separates core file processing and modernizes multipart/deep workflows", "A-SRC-086", ["fam.openexr_container", "fam.deep_image"]),
        (2022, "OGC 3D Tiles 1.1 adds interoperable hierarchical 3D geospatial content", "A-SRC-096", ["fam.three_d_tiles"]),
        (2022, "GA4GH Phenopackets 2.0 broadens computable phenotype packets", "A-SRC-113", ["fam.phenopacket"]),
        (2022, "COSE standardizes protected CBOR envelopes", "A-SRC-127", ["fam.encrypted_envelope"]),
        (2022, "JPEG XL standardizes modern still-image coding", "A-SRC-085", ["fam.raster_image"]),
        (2023, "FHIR R5 adds and stabilizes richer diagnostic/genomic resources", "A-SRC-114", ["fam.fhir_resource", "fam.genomic_report"]),
        (2023, "OpenTelemetry semantic conventions reach stable versioned contracts", "A-SRC-143", ["fam.metric_stream", "fam.trace_span_graph"]),
        (2023, "OCEL 2.0 adds qualified object-event relations and object changes", "A-DSS-034", ["fam.object_centric_event_log"]),
        (2023, "HDF5 1.14 generation advances the scientific container implementation surface", "A-DSS-014", ["fam.hdf5_dataset_graph"]),
        (2023, "CloudEvents ecosystem adds SQL-like event filtering semantics", "A-SRC-144", ["fam.event_envelope"]),
        (2024, "GeoParquet 1.1 adds native GeoArrow-derived geometry encodings", "A-SRC-100", ["fam.geoparquet_binding"]),
        (2024, "GeoArrow 0.2 distinguishes field metadata from memory layout", "A-SRC-101", ["fam.geoparquet_binding"]),
        (2024, "SPDX 3.0 adopts a modular graph/profile model", "A-DSS-059", ["fam.sbom"]),
        (2024, "DCAT 3 standardizes dataset series, version, checksum, and catalog refinements", "A-SRC-133", ["fam.catalog_record"]),
        (2024, "HL7 Genomics Reporting IG 3.0 expands structured clinical genomics reporting", "A-SRC-115", ["fam.genomic_report"]),
        (2024, "VCF 4.5 advances variant representation conventions", "A-SRC-111", ["fam.variant_set"]),
        (2024, "WARC RFC 9585 refreshes web archive interchange", "A-SRC-135", ["fam.web_archive"]),
        (2024, "AsyncAPI 3.0 restructures asynchronous message and operation descriptions", "A-SRC-139", ["fam.asyncapi_message"]),
        (2024, "ASAM OpenSCENARIO 1.3 extends scenario description", "A-SRC-147", ["fam.simulation_scenario"]),
        (2024, "C2PA 2.x advances signed content-provenance manifests", "A-SRC-132", ["fam.c2pa_manifest"]),
        (2025, "Zarr v3 standardizes codecs and storage-transformer-aware chunked arrays", "A-DSS-016", ["fam.zarr_hierarchy"]),
        (2025, "STEP AP242 edition 4 expands managed model-based 3D engineering", "A-SRC-104", ["fam.cad_product_model"]),
        (2025, "WebAssembly Core 2.0 advances portable structured bytecode", "A-SRC-137", ["fam.bytecode_module"]),
        (2025, "RO-Crate 1.2 advances research-object packaging", "A-SRC-148", ["fam.evidence_bundle", "fam.dataset_manifest"]),
        (2025, "PNG Third Edition modernizes portable raster-image representation", "A-SRC-083", ["fam.raster_image"]),
        (2026, "WebCodecs continues explicit separation of codec APIs from codec specifications", "A-SRC-092", ["fam.video_track", "fam.audio_track"]),
    ]
    innovations = [
        {"innovation_id": f"INNOV-{i:03d}", "year": year, "innovation": title, "evidence_refs": [src],
         "family_ids": fams, "non_llm": True, "audit_significance": "Requires a versioned shape or representation distinction; does not create semantic equivalence."}
        for i, (year, title, src, fams) in enumerate(innovation_specs, 1)
    ]
    dump_jsonl(ROOT / "innovations-2021-2026.jsonl", innovations)
    dump_jsonl(ROOT / "audit-assertions.jsonl", assertions)
    dump_jsonl(ROOT / "standards-sources.jsonl", sources)

    cluster_counts = Counter(f["domain_cluster"] for f in FAMILY_SPECS)
    missing_by_cluster = Counter(f["domain_cluster"] for f in FAMILY_SPECS if f["relation"] == "missing")
    strata = []
    cumulative = 0
    for i, cluster in enumerate(sorted(cluster_counts), 1):
        cumulative += cluster_counts[cluster]
        strata.append({"stratum": cluster, "candidate_families_reviewed": cluster_counts[cluster],
                       "canonical_missing": missing_by_cluster[cluster], "cumulative_families": cumulative,
                       "independent_reviewer": False})
    saturation = {
        "audit_id": "san.domain-atlas.data-modality-gap-audit.saturation",
        "as_of": AS_OF,
        "claim": "not_saturated",
        "honest_limit": "This is one adversarial standards sweep, not an exhaustive census. Source count and cell count are evidence of breadth, not proof of closure.",
        "search_strata": strata,
        "novelty_curve": [{"strata_reviewed": i, "cumulative_families": row["cumulative_families"]} for i, row in enumerate(strata, 1)],
        "absence_of_new_category_cycles": 0,
        "required_cycles_for_saturation_claim": 2,
        "independent_review_complete": False,
        "unseen_mass_estimate": None,
        "why_no_unseen_mass_estimate": "Standards strata were purposively sampled rather than independent identically distributed discoveries.",
        "closure_rule": "Two independent disjoint-domain sweeps add no new constructor/layer distinction, all missing mappings are adjudicated, and every family has two unrelated vertical fixtures.",
        "known_blind_spots": ["proprietary industry formats", "jurisdiction-specific records", "long-tail scientific instruments", "legacy mainframe encodings", "implementation conformance behavior"],
    }
    dump_json(ROOT / "saturation-report.json", saturation)

    canonical_files = ["classification-axes.json", "type-records.jsonl", "shape-records.jsonl", "operation-totality-matrix.jsonl", "representation-crosswalks.jsonl", "invalid-inference-matrix.jsonl", "sources.jsonl"]
    canonical_representation_records = load_jsonl(CANONICAL / "representation-crosswalks.jsonl")
    canonical_invalid_inferences = load_jsonl(CANONICAL / "invalid-inference-matrix.jsonl")
    snapshot = {
        "registry": "san.domain-atlas.data-shapes",
        "as_of": AS_OF,
        "files": {name: {"sha256": sha256(CANONICAL / name), "bytes": (CANONICAL / name).stat().st_size} for name in canonical_files},
        "counts": {"types": len(type_records), "shapes": len(shape_records), "operations": len(op_records), "representation_crosswalks": len(canonical_representation_records), "invalid_inferences": len(canonical_invalid_inferences), "sources": len(canonical_sources)},
        "crosswalk_policy": "All target IDs are explicit declarations; no names were used to infer equivalence.",
    }
    dump_json(ROOT / "canonical-snapshot.json", snapshot)

    summary = {
        "audit_id": "san.domain-atlas.data-modality-gap-audit",
        "edition": 1,
        "status": "candidate_adversarial_audit",
        "as_of": AS_OF,
        "scope": "Non-generative enterprise data modalities, logical shapes, carriers, representations, and layer boundaries.",
        "is_competing_registry": False,
        "counts": {
            "axes": len(AXES), "candidate_families": len(families), "coverage_cells": sum(r["cell_count"] for r in tensor),
            "sources": len(sources), "unique_source_urls": len({record["url"] for record in sources}), "canonical_crosswalks": len(crosswalks), "audit_assertions": len(assertions),
            "operation_type_cells": len(op_gaps), "schema_posture_records": len(schema_postures), "representation_findings": len(rep_records), "canonical_representation_audits": len(canonical_rep_audit), "gap_findings": len(findings),
            "vertical_samples": len(verticals), "innovations_2021_2026": len(innovations),
        },
        "crosswalk_relations": dict(sorted(relation_counter.items())),
        "coverage_cell_states": dict(sorted(cell_counter.items())),
        "canonical_snapshot": snapshot["counts"],
        "saturation_claim": "not_saturated",
        "forbidden_shortcuts": ["name-based equivalence", "file extension as semantic type", "unstructured as structure-free", "null as absence reason", "format conformance as truth", "axis Cartesian product as enumeration"],
    }
    dump_json(ROOT / "audit-summary.json", summary)

    generated = [
        "classification-axes.json", "schema-posture-audit.jsonl", "modality-family-expectations.jsonl", "coverage-tensor.jsonl", "canonical-crosswalk.jsonl",
        "operation-type-gaps.jsonl", "representation-layer-findings.jsonl", "canonical-representation-audit.jsonl", "gap-findings.jsonl", "vertical-case-samples.jsonl",
        "innovations-2021-2026.jsonl", "audit-assertions.jsonl", "standards-sources.jsonl", "saturation-report.json",
        "canonical-snapshot.json", "audit-summary.json",
    ]
    manifest = {"builder": "build_audit.py", "as_of": AS_OF, "files": {name: sha256(ROOT / name) for name in generated}}
    dump_json(ROOT / "manifest.json", manifest)


if __name__ == "__main__":
    build()
