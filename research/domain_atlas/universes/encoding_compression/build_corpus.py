#!/usr/bin/env python3
"""Build the provider-neutral representation, encoding, layout and compression corpus.

The Python file is the reviewable authoring source.  Generated JSON/JSONL is the
machine-readable surface consumed by validators and future compiler passes.  The
records are an open-world candidate atlas, not a claim that every future format,
codec, implementation, or target has been enumerated.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EDITION = 1
ACCESSED = "2026-08-25"


def write_json(name: str, value: object) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_jsonl(name: str, rows: list[dict]) -> None:
    (ROOT / name).write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )


# Primary standards, project specifications, official implementation contracts,
# and primary research artifacts.  A provider page is authoritative only for its
# own interface/claim; the authority_limit field deliberately prevents promotion
# into a universal law.
SOURCE_ROWS = [
    ("src.unicode.17", "The Unicode Standard 17.0", "Unicode Consortium", "consensus_standard", "https://www.unicode.org/versions/Unicode17.0.0/", "characters, code points, UTF encoding forms and schemes"),
    ("src.ietf.utf8", "UTF-8, a transformation format of ISO 10646", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc3629.html", "UTF-8 byte syntax, validity, and security considerations"),
    ("src.ietf.json", "The JavaScript Object Notation Data Interchange Format", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc8259.html", "JSON grammar and interoperability constraints"),
    ("src.ietf.cbor", "Concise Binary Object Representation", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc8949.html", "CBOR data model, serialization and deterministic-encoding basis"),
    ("src.ietf.jcs", "JSON Canonicalization Scheme", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc8785.html", "a specific canonical JSON profile"),
    ("src.protobuf.encoding", "Protocol Buffers Encoding", "Google Protocol Buffers", "official_specification", "https://protobuf.dev/programming-guides/encoding/", "Protocol Buffers wire types, tags, varints and field behavior"),
    ("src.protobuf.deterministic", "Proto Serialization Is Not Canonical", "Google Protocol Buffers", "official_documentation", "https://protobuf.dev/programming-guides/serialization-not-canonical/", "limits of deterministic Protocol Buffers serialization"),
    ("src.avro.spec", "Apache Avro Specification", "Apache Avro", "official_specification", "https://avro.apache.org/docs/current/specification/", "Avro schemas, binary encoding, resolution, OCF blocks and codecs"),
    ("src.flatbuffers.internals", "FlatBuffers Internals", "Google FlatBuffers", "official_specification", "https://flatbuffers.dev/flatbuffers_internals.html", "FlatBuffers wire layout, offsets, alignment and schema evolution"),
    ("src.capnproto.encoding", "Cap'n Proto Encoding", "Cap'n Proto", "official_specification", "https://capnproto.org/encoding.html", "Cap'n Proto segment, pointer and struct/list encoding"),
    ("src.msgpack.spec", "MessagePack Specification", "MessagePack", "official_specification", "https://github.com/msgpack/msgpack/blob/master/spec.md", "MessagePack byte-level format"),
    ("src.itu.x690", "X.690 ASN.1 encoding rules", "ITU-T", "consensus_standard", "https://www.itu.int/rec/T-REC-X.690", "BER, CER and DER encoding rules"),
    ("src.arrow.columnar", "Arrow Columnar Format", "Apache Arrow", "official_specification", "https://arrow.apache.org/docs/format/Columnar.html", "in-memory layouts, nulls, nesting, dictionaries, run ends and IPC"),
    ("src.arrow.security", "Arrow Format Security Considerations", "Apache Arrow", "official_specification", "https://arrow.apache.org/docs/format/Security.html", "validation and trust boundaries for Arrow formats and interfaces"),
    ("src.parquet.format", "Apache Parquet Format", "Apache Parquet", "official_specification", "https://github.com/apache/parquet-format", "Parquet physical/logical types, pages, row groups and encodings"),
    ("src.parquet.page_index", "Parquet Page Index", "Apache Parquet", "official_specification", "https://github.com/apache/parquet-format/blob/master/PageIndex.md", "page skipping metadata and its limitations"),
    ("src.parquet.bloom", "Parquet Bloom Filter", "Apache Parquet", "official_specification", "https://github.com/apache/parquet-format/blob/master/BloomFilter.md", "split-block Bloom filter representation and false-positive semantics"),
    ("src.parquet.encryption", "Parquet Modular Encryption", "Apache Parquet", "official_specification", "https://github.com/apache/parquet-format/blob/master/Encryption.md", "file and column encryption envelopes and metadata protection"),
    ("src.orc.spec", "ORC Specification", "Apache ORC", "official_specification", "https://orc.apache.org/specification/ORCv0/", "stripes, streams, RLE, indexes, compression and encryption variants"),
    ("src.hdf5.format", "HDF5 File Format Specification", "The HDF Group", "official_specification", "https://support.hdfgroup.org/documentation/hdf5/latest/_s_p_e_c.html", "HDF5 object mapping, chunk layouts and filter-pipeline metadata"),
    ("src.hdf5.chunking", "HDF5 Dataset Chunking Issues", "The HDF Group", "official_documentation", "https://support.hdfgroup.org/documentation/hdf5/latest/hdf5_chunk_issues.html", "chunk atomicity, access amplification and filter interaction"),
    ("src.netcdf.format", "netCDF Formats, Data Models, and Software Releases", "NSF Unidata", "official_documentation", "https://docs.unidata.ucar.edu/netcdf-c/current/faq.html", "netCDF physical variants, XDR, HDF5 mapping, chunking and compression"),
    ("src.netcdf.quantize", "Lossy Compression with Quantize", "NSF Unidata", "official_documentation", "https://docs.unidata.ucar.edu/netcdf-c/current/quantize.html", "netCDF significant-digit quantization and declared lossy behavior"),
    ("src.zarr.v3", "Zarr Storage Specification Version 3", "Zarr", "official_specification", "https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html", "chunked array metadata, keys, codec pipelines and extensions"),
    ("src.zarr.sharding", "Zarr Sharding Codec", "Zarr", "official_specification", "https://zarr-specs.readthedocs.io/en/latest/v3/codecs/sharding-indexed/v1.0.html", "indexed sharding of chunks and partial access"),
    ("src.ogc.cog", "Cloud Optimized GeoTIFF 1.0", "Open Geospatial Consortium", "consensus_standard", "https://docs.ogc.org/is/21-026/21-026.html", "range-readable tiled raster organization and HTTP requirements"),
    ("src.geoparquet.spec", "GeoParquet Specification", "Open Geospatial Consortium GeoParquet", "official_specification", "https://github.com/opengeospatial/geoparquet", "geospatial vector metadata and geometry encodings in Parquet"),
    ("src.pmtiles.v3", "PMTiles Version 3 Specification", "Protomaps", "official_specification", "https://github.com/protomaps/PMTiles/blob/main/spec/v3/spec.md", "single-file tile archive directories, offsets, compression and range reads"),
    ("src.ogc.geotiff", "OGC GeoTIFF Standard", "Open Geospatial Consortium", "consensus_standard", "https://www.ogc.org/standards/geotiff/", "georeferencing metadata in TIFF"),
    ("src.w3c.png3", "Portable Network Graphics Specification, Third Edition", "W3C", "consensus_standard", "https://www.w3.org/TR/png-3/", "lossless raster chunks, filters, integrity, animation and HDR metadata"),
    ("src.jpeg.jpeg1", "JPEG 1 Overview and Standards", "JPEG Committee", "standards_body_documentation", "https://jpeg.org/jpeg/", "JPEG family parts and baseline still-image coding"),
    ("src.jpeg.jpegxl", "JPEG XL Overview", "JPEG Committee", "standards_body_documentation", "https://jpeg.org/jpegxl/", "JPEG XL lossless/lossy coding, progressive delivery and JPEG reconstruction"),
    ("src.aom.avif", "AV1 Image File Format 1.2", "Alliance for Open Media", "official_specification", "https://aomedia.org/docs/AV1%20Image%20File%20Format%20%28AVIF%29%20v1.2.0.pdf", "AV1 image items inside HEIF"),
    ("src.aom.av1", "AV1 Bitstream and Decoding Process", "Alliance for Open Media", "official_specification", "https://aomedia.org/specifications/av1/", "AV1 bitstream and decoder process"),
    ("src.aom.av2", "AV2 Bitstream and Decoding Process 1.0", "Alliance for Open Media", "official_specification", "https://av2.aomedia.org/", "AV2 bitstream, decoder process and reference software"),
    ("src.openexr.spec", "OpenEXR Technical Introduction", "Academy Software Foundation OpenEXR", "official_specification", "https://openexr.com/en/latest/TechnicalIntroduction.html", "HDR image channels, tiles, parts and compression choices"),
    ("src.ietf.flac", "Free Lossless Audio Codec", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc9639.html", "FLAC lossless audio frames, metadata, checks and streamable subset"),
    ("src.ietf.opus", "Definition of the Opus Audio Codec", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc6716.html", "Opus lossy audio bitstream, rate, delay and decoder behavior"),
    ("src.ietf.matroska", "Matroska Media Container Format Specification", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc9559.html", "Matroska container elements and codec encapsulation"),
    ("src.dicom.transfer", "DICOM Transfer Syntax", "DICOM Standards Committee", "consensus_standard", "https://dicom.nema.org/medical/dicom/current/output/chtml/part05/chapter_10.html", "medical-data byte ordering, VR and encapsulated pixel-data transfer syntaxes"),
    ("src.hts.specs", "SAM/BAM and CRAM Specifications", "Global Alliance for Genomics and Health", "official_specification", "https://github.com/samtools/hts-specs", "genomics alignment containers, BGZF framing, CRAM references and codecs"),
    ("src.asprs.las", "LAS Specification", "American Society for Photogrammetry and Remote Sensing", "consensus_standard", "https://www.asprs.org/divisions-committees/lidar-division/laser-las-file-format-exchange-activities", "point-cloud LAS format and conformance scope"),
    ("src.ietf.deflate", "DEFLATE Compressed Data Format", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc1951.html", "DEFLATE LZ77/Huffman bitstream"),
    ("src.ietf.gzip", "GZIP File Format Specification", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc1952.html", "gzip framing, members and CRC"),
    ("src.ietf.zstd", "Zstandard Compression and Media Type", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc8878.html", "Zstandard frames, blocks, dictionaries, entropy coding and windows"),
    ("src.ietf.brotli", "Brotli Compressed Data Format", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc7932.html", "Brotli lossless bitstream and bounded-memory streaming properties"),
    ("src.lz4.frame", "LZ4 Frame Format", "LZ4 Project", "official_specification", "https://github.com/lz4/lz4/blob/dev/doc/lz4_Frame_format.md", "LZ4 framing, independent blocks, dictionaries and checksums"),
    ("src.snappy.frame", "Snappy Framing Format", "Google Snappy", "official_specification", "https://github.com/google/snappy/blob/main/framing_format.txt", "Snappy chunks, bounded buffers, concatenation and CRC32C"),
    ("src.xz.format", "The .xz File Format", "Tukaani Project", "official_specification", "https://tukaani.org/xz/xz-file-format.txt", "XZ streams, blocks, indexes, filters and checks"),
    ("src.roaring.format", "Roaring Bitmap Format Specification", "RoaringBitmap", "official_specification", "https://github.com/RoaringBitmap/RoaringFormatSpec", "portable array, bitmap and run containers"),
    ("src.vldb.alp", "ALP: Adaptive Lossless Floating-Point Compression", "CWI Database Architectures Group", "primary_research", "https://github.com/cwida/ALP", "lossless floating-point encoding, code and reproducibility artifacts"),
    ("src.sigmod.btrblocks", "BtrBlocks: Efficient Columnar Compression for Data Lakes", "Technical University of Munich", "primary_research", "https://github.com/maxi-k/btrblocks", "block-wise adaptive column encoding and implementation"),
    ("src.vldb.chimp", "Chimp: Efficient Lossless Floating Point Compression", "PVLDB authors", "primary_research", "https://pages.cs.aueb.gr/users/kotidis/Publications/chimp.pdf", "streaming lossless floating-point XOR encoding"),
    ("src.vldb.elf", "Elf: Erasing-based Lossless Floating-Point Compression", "PVLDB", "primary_research", "https://www.vldb.org/pvldb/vol16/p1763-li.pdf", "lossless erasing-based floating-point encoding and evaluation"),
    ("src.sz3", "SZ3 Modular Error-bounded Lossy Compression", "SZ Compressor Project", "primary_research_software", "https://github.com/szcompressor/SZ3", "scientific error-bound modes, modular predictors and quantizers"),
    ("src.zfp.modes", "zfp Compression Modes", "Lawrence Livermore National Laboratory", "official_documentation", "https://zfp.readthedocs.io/en/develop/modes.html", "fixed-rate, precision, accuracy and reversible modes"),
    ("src.blosc2.format", "C-Blosc2 Frame Format", "Blosc", "official_specification", "https://github.com/Blosc/c-blosc2/blob/main/README_CFRAME_FORMAT.rst", "chunked meta-compression frames, filters and random access"),
    ("src.nvidia.nvcomp", "nvCOMP", "NVIDIA", "official_implementation_contract", "https://developer.nvidia.com/nvcomp", "GPU compression/decompression APIs, algorithms and hardware constraints"),
    ("src.intel.iaa", "Intel In-Memory Analytics Accelerator Architecture", "Intel", "official_hardware_contract", "https://www.intel.com/content/www/us/en/content-details/721858/intel-in-memory-analytics-accelerator-architecture-specification.html", "hardware compression and analytic-operation offload"),
    ("src.microsoft.gdeflate", "GDeflate Reference Implementation and Stream Definition", "Microsoft", "official_specification", "https://github.com/microsoft/DirectStorage/blob/main/GDeflate/GDeflate/README.md", "parallel GPU-oriented DEFLATE-derived stream"),
    ("src.ietf.digest", "Digest Fields", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc9530.html", "content versus representation digest semantics"),
    ("src.nist.sha3", "FIPS 202 SHA-3 Standard", "NIST", "consensus_standard", "https://csrc.nist.gov/pubs/fips/202/final", "SHA-3 and SHAKE algorithms"),
    ("src.nist.shs", "FIPS 180-4 Secure Hash Standard", "NIST", "consensus_standard", "https://csrc.nist.gov/pubs/fips/180-4/upd1/final", "SHA-2 algorithms"),
    ("src.ietf.cose", "CBOR Object Signing and Encryption", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc9052.html", "COSE signing, MAC and encryption structures"),
    ("src.ietf.jws", "JSON Web Signature", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc7515.html", "JWS signature and integrity envelope"),
    ("src.ietf.aead", "Authenticated Encryption with Associated Data", "IETF", "internet_standard", "https://www.rfc-editor.org/rfc/rfc5116.html", "AEAD interface and nonce/tag semantics"),
    ("src.nist.gcm", "Recommendation for Block Cipher Modes: GCM and GMAC", "NIST", "consensus_standard", "https://csrc.nist.gov/pubs/sp/800/38/d/final", "AES-GCM authenticated-encryption parameters and limits"),
    ("src.oci.descriptor", "OCI Content Descriptors", "Open Container Initiative", "official_specification", "https://github.com/opencontainers/image-spec/blob/main/descriptor.md", "content address, media type, size and digest verification"),
    ("src.lance.format", "Lance File Format Specification", "Lance", "official_specification", "https://lance.org/format/file/", "cloud-oriented per-column pages and random access"),
    ("src.meta.nimble", "Nimble File Format", "Meta", "official_research_software", "https://github.com/facebookincubator/nimble", "extensible cascading column encodings and wide-table layout; explicitly unstable"),
    ("src.vortex.editions", "Vortex Editions", "LF AI & Data Vortex", "official_specification", "https://docs.vortex.dev/specs/editions", "independently versioned encoding/layout component editions"),
    ("src.vortex.project", "Vortex Project", "LF AI & Data Foundation", "official_project_record", "https://lfaidata.foundation/projects/vortex/", "compressed arrays across memory, disk and IPC and project maturity"),
    ("src.sigmod.f3", "F3: The Open-Source Data File Format for the Future", "Carnegie Mellon Database Group", "primary_research", "https://db.cs.cmu.edu/papers/2025/zeng-sigmod2025.pdf", "2025 columnar file-format design and comparative evaluation"),
]


SOURCES = [
    {
        "source_id": sid,
        "edition": EDITION,
        "title": title,
        "publisher": publisher,
        "kind": kind,
        "url": url,
        "primary_or_official": True,
        "supports": supports,
        "authority_limit": "Authoritative only for the named standard, implementation, interface, hardware, or experiment; it neither proves universal superiority nor closes the open-world registry.",
        "accessed_at": ACCESSED,
    }
    for sid, title, publisher, kind, url, supports in SOURCE_ROWS
]


AXES = {
    "atlas_id": "san.encoding-compression.axes",
    "edition": EDITION,
    "status": "candidate_open_world",
    "distinction_law": "A semantic type, carrier, encoding, framing, layout, container, codec, compression algorithm, protection envelope, implementation, and execution target are distinct nodes even when a product bundles them.",
    "axes": [
        {"axis_id": "representation_layer", "values": ["semantic_type", "carrier", "scalar_encoding", "character_encoding", "schema_serialization", "framing", "physical_layout", "container_file_format", "column_encoding", "compression_algorithm", "domain_codec", "canonicalization_profile", "integrity_algorithm", "cryptographic_envelope", "chunking_scheme", "implementation_offer", "execution_target"]},
        {"axis_id": "reversibility", "values": ["bitwise_lossless", "semantic_lossless", "conditionally_lossless", "error_bounded_lossy", "rate_bounded_lossy", "precision_bounded_lossy", "perceptual_lossy", "unknown_forbidden"]},
        {"axis_id": "identity_scope", "values": ["source_semantic_value", "canonical_semantic_value", "encoded_bytes", "compressed_bytes", "container_member", "whole_container", "selected_representation", "transmitted_content"]},
        {"axis_id": "access", "values": ["sequential_only", "restartable", "splittable", "block_random_access", "page_random_access", "row_random_access", "coordinate_random_access", "progressive", "range_readable"]},
        {"axis_id": "execution_mode", "values": ["whole_buffer", "incremental", "streaming", "microbatch", "block_parallel", "column_parallel", "pipeline_parallel", "device_resident"]},
        {"axis_id": "state_dependency", "values": ["stateless", "previous_symbol", "previous_value", "previous_block", "sliding_window", "external_dictionary", "schema_registry", "reference_data", "model_parameters"]},
        {"axis_id": "physical_grain", "values": ["bit", "byte", "code_unit", "scalar", "value", "record", "frame", "page", "column_chunk", "row_group", "stripe", "tile", "multidimensional_chunk", "shard", "file", "object"]},
        {"axis_id": "byte_bit_order", "values": ["little_endian", "big_endian", "network_order", "mixed_declared", "byte_invariant", "lsb_first", "msb_first", "native_only_non_interchange"]},
        {"axis_id": "shape", "values": ["scalar", "sequence", "record", "table", "nested_table", "sparse", "graph", "timeseries", "nd_array", "raster", "vector_geometry", "point_cloud", "audio", "image", "video", "genomics"]},
        {"axis_id": "compression_mechanism", "values": ["dictionary", "run_length", "delta", "frame_of_reference", "bit_packing", "prefix", "prediction_residual", "transform", "entropy", "lz_matching", "quantization", "decorrelation", "cascaded", "adaptive_selection"]},
        {"axis_id": "error_model", "values": ["none_exact", "absolute", "relative", "pointwise_relative", "significant_digits", "fixed_precision", "fixed_rate", "psnr", "perceptual_metric", "application_observable", "unbounded_forbidden"]},
        {"axis_id": "integrity_scope", "values": ["none", "header", "block", "frame", "page", "column", "chunk", "member", "file", "representation", "content", "merkle_node"]},
        {"axis_id": "security_property", "values": ["none", "error_detection", "collision_resistant_identity", "authenticity", "confidentiality", "integrity_authentication", "non_repudiation_not_implied"]},
        {"axis_id": "metadata_placement", "values": ["inline_per_value", "block_header", "page_header", "footer", "sidecar", "external_registry", "manifest", "implicit_forbidden"]},
        {"axis_id": "schema_binding", "values": ["self_describing", "schema_embedded", "schema_fingerprint", "schema_external", "schema_less_syntax", "fixed_profile", "unknown_forbidden"]},
        {"axis_id": "null_nesting", "values": ["not_applicable", "sentinel", "validity_bitmap", "tagged_union", "offsets", "definition_levels", "repetition_levels", "sparse_presence", "application_specific"]},
        {"axis_id": "statistics", "values": ["none", "count", "null_count", "min_max", "sum", "distinct_estimate", "dictionary_membership", "bloom_filter", "page_offsets", "zone_map", "domain_summary"]},
        {"axis_id": "target", "values": ["portable_scalar_cpu", "simd_cpu", "multicore_cpu", "gpu", "dedicated_accelerator", "browser_wasm", "embedded_bounded_memory", "object_store_range", "memory_mapped", "network_stream"]},
        {"axis_id": "resource", "values": ["encoded_size", "peak_memory", "working_set", "dictionary_size", "window_size", "encode_throughput", "decode_throughput", "latency", "parallelism", "energy", "io_amplification", "compute_amplification"]},
        {"axis_id": "compatibility", "values": ["exact_edition", "backward_read", "forward_skip", "profile_subset", "extension_registry", "transcode_required", "reference_required", "decoder_capability_required"]},
        {"axis_id": "corruption_behavior", "values": ["detect_and_stop", "detect_and_skip_block", "resynchronize", "recover_from_redundancy", "conceal_media_error", "best_effort_forbidden_without_policy"]},
        {"axis_id": "decision_phase", "values": ["semantic_closure", "logical_planning", "physical_binding", "write_time", "read_time", "runtime_adaptive", "migration", "recovery"]},
    ],
}


CONTEXT_ROWS = [
    ("bc.representation.carrier", "Which physical carrier holds an already-typed value without redefining its meaning?", ["carrier identity", "buffer/stream/seekability traits", "memory-space trait"], ["semantic business type", "compression choice"], ["Carrier capability is explicit; a byte slice alone does not imply format."], ["src.arrow.columnar"]),
    ("bc.representation.byte_order", "How are multi-byte units and bits ordered, aligned and padded for interchange?", ["endianness", "bit order", "alignment", "padding"], ["numeric meaning", "hardware selection"], ["Native order cannot cross an interchange boundary without an editioned target constraint."], ["src.arrow.columnar", "src.unicode.17"]),
    ("bc.representation.character_encoding", "How are abstract characters mapped to code units and bytes, and what constitutes malformed input?", ["character encoding", "BOM policy", "decoder error policy"], ["language semantics", "Unicode normalization"], ["Malformed sequences never silently acquire replacement semantics unless policy explicitly permits it."], ["src.unicode.17", "src.ietf.utf8"]),
    ("bc.representation.scalar_encoding", "How are scalar values mapped to finite bit patterns while preserving signedness, width and special values?", ["integer/floating encoding", "varint", "zigzag", "bit packing"], ["units", "business equality"], ["Width, overflow, NaN, signed zero and decimal-rounding behavior are explicit."], ["src.protobuf.encoding", "src.arrow.columnar"]),
    ("bc.representation.schema_serialization", "How does a schema bind field identities and values to a wire representation across editions?", ["wire grammar", "field tags", "schema resolution", "unknown-field behavior"], ["domain schema ownership", "transport retry"], ["Wire compatibility is not semantic compatibility; both must be proven."], ["src.protobuf.encoding", "src.avro.spec", "src.flatbuffers.internals"]),
    ("bc.representation.framing", "Where do independently consumable messages or blocks begin and end, and how can a reader resynchronize?", ["length/sentinel/TLV framing", "sync markers", "frame boundaries"], ["business transaction", "compression algorithm internals"], ["A decoder has a finite maximum frame and a typed truncation outcome."], ["src.avro.spec", "src.snappy.frame", "src.ietf.flac"]),
    ("bc.representation.canonicalization", "Which one of multiple semantically acceptable serializations is the governed canonical byte representation?", ["canonical profile", "ordering", "numeric normalization", "canonical receipt"], ["semantic equality", "digest algorithm"], ["Deterministic implementation output is not called canonical without a complete editioned profile."], ["src.ietf.jcs", "src.ietf.cbor", "src.protobuf.deterministic"]),
    ("bc.representation.content_identity", "Which exact byte scope is named by a digest and how is that identity recomputed after transforms?", ["digest scope", "content address", "identity receipt"], ["business identity", "signature authority"], ["Digest of compressed bytes is distinct from digest of decoded or canonical values."], ["src.oci.descriptor", "src.ietf.digest"]),
    ("bc.representation.chunking", "How is a logical byte/value domain partitioned into independently named, stored, transferred or decoded chunks?", ["chunk boundary law", "chunk identity", "reassembly order"], ["table partitioning", "business aggregation"], ["Reassembly is total only when coverage, order and integrity close without overlap ambiguity."], ["src.zarr.v3", "src.hdf5.chunking"]),
    ("bc.representation.physical_layout", "How are values placed into buffers, pages, tiles, stripes and files for declared access paths?", ["row/column/hybrid layout", "page/stripe/tile placement", "offset indexes"], ["logical table model", "query optimization policy"], ["Layout never changes value semantics; access guarantees require explicit metadata."], ["src.arrow.columnar", "src.parquet.format", "src.orc.spec"]),
    ("bc.representation.null_nested_layout", "How are absence, variable-length values and nesting represented without confusing null, empty and missing?", ["validity", "offsets", "definition/repetition levels", "nested reconstruction"], ["business missingness semantics", "schema authorship"], ["Null, empty, absent field and unknown are never conflated."], ["src.arrow.columnar", "src.parquet.format"]),
    ("bc.representation.column_encoding", "Which reversible physical encoding represents a typed value sequence within a column or block?", ["dictionary/RLE/delta/FOR/bit-pack encoding", "escape values", "encoding metadata"], ["general compression", "semantic type"], ["Decoding reconstructs the declared physical value sequence exactly unless a separate loss contract is attached."], ["src.parquet.format", "src.orc.spec", "src.arrow.columnar"]),
    ("bc.representation.dictionary_lifecycle", "How is an encoding dictionary trained, identified, distributed, versioned and retired?", ["dictionary identity", "training corpus", "scope", "availability"], ["master/reference data", "schema registry"], ["Decoder availability of the exact dictionary is a blocking requirement, not a cache hint."], ["src.ietf.zstd", "src.lz4.frame"]),
    ("bc.representation.compression_algorithm", "What reversible or declared-loss transform reduces a representation under finite resource bounds?", ["algorithm semantics", "parameters", "round-trip law", "error law"], ["container placement", "provider implementation"], ["Every lossy mode names its error contract and approval authority."], ["src.ietf.zstd", "src.sz3", "src.zfp.modes"]),
    ("bc.representation.codec", "How does a domain carrier such as image, audio, video or scientific array bind to a codestream and decoder contract?", ["codec profile", "domain sample mapping", "decode result", "loss surface"], ["container multiplexing", "media rights"], ["Profile, level, color/sample model and loss mode are explicit before encode."], ["src.w3c.png3", "src.ietf.flac", "src.aom.av1"]),
    ("bc.representation.container", "How are one or more coded payloads, schemas, indexes and metadata assembled into a versioned file or stream?", ["container members", "metadata placement", "indexes", "edition"], ["table transaction semantics", "codec internals"], ["A file extension or media type is evidence for dispatch only after magic/profile validation."], ["src.ietf.matroska", "src.parquet.format", "src.hdf5.format"]),
    ("bc.representation.codec_binding", "Which compression or media codec is valid at each container member or layout grain?", ["container-codec compatibility", "codec parameters", "member metadata"], ["algorithm implementation quality", "product packaging"], ["A codec name alone cannot prove framing, checksum, splittability or decoder availability."], ["src.avro.spec", "src.parquet.format", "src.hdf5.format"]),
    ("bc.representation.loss_contract", "What information may be discarded, how is error measured, and who may approve that loss?", ["loss class", "error metric/bound", "protected observables", "approval"], ["business harm policy", "codec implementation"], ["Unknown or unbounded loss fails closed; validation is on decoded outputs and protected observables."], ["src.sz3", "src.zfp.modes", "src.netcdf.quantize"]),
    ("bc.representation.compression_selection", "Which encoding pipeline satisfies access, fidelity, resource, compatibility and target constraints for an observed corpus?", ["selection requirement", "benchmark protocol", "selection receipt"], ["provider ranking", "business semantic policy"], ["Selection dispatches on capability and evidence, never vendor or library name."], ["src.sigmod.btrblocks", "src.vldb.alp", "src.vortex.editions"]),
    ("bc.representation.pipeline", "In which typed order may preprocessing, encoding, compression, integrity and protection transforms compose?", ["transform DAG", "ordering constraints", "inverse DAG", "pipeline edition"], ["data pipeline scheduling", "cryptographic key authority"], ["Every forward edge has typed input/output, inverse/refusal semantics and resource limits."], ["src.hdf5.format", "src.zarr.v3", "src.blosc2.format"]),
    ("bc.representation.random_access", "What independent decode unit and index prove bounded random or range access?", ["restart point", "offset index", "dependency window", "read amplification"], ["query predicate semantics", "object-store consistency"], ["Random-access claims include worst-case bytes fetched and prerequisite metadata."], ["src.parquet.page_index", "src.ogc.cog", "src.lance.format"]),
    ("bc.representation.splittability", "Where may work be partitioned for parallel decode without hidden dependency on preceding bytes or values?", ["split points", "independent-block proof", "reassembly"], ["distributed scheduler", "business partitioning"], ["A frame is splittable only when its dictionary/window/reference dependencies are available at each split."], ["src.avro.spec", "src.lz4.frame", "src.ietf.flac"]),
    ("bc.representation.pruning_metadata", "Which conservative summaries allow data blocks to be skipped without false negatives?", ["min/max/null statistics", "Bloom filters", "page offsets", "summary validity"], ["query predicate", "semantic measure definition"], ["Pruning may produce false positives but never false negatives within its declared type/order semantics."], ["src.parquet.page_index", "src.parquet.bloom", "src.orc.spec"]),
    ("bc.representation.integrity", "How are accidental corruption and truncation detected at the correct representation grain?", ["checksum", "coverage scope", "verification", "truncation detection"], ["cryptographic authenticity", "storage durability"], ["A checksum is not a signature and verification precedes unsafe decoding where possible."], ["src.snappy.frame", "src.w3c.png3", "src.ietf.digest"]),
    ("bc.representation.protection_envelope", "How are encoded bytes encrypted, authenticated or signed without losing scope and algorithm agility?", ["protection envelope", "associated data", "nonce/tag/signature placement"], ["key management", "authorization", "privacy purpose"], ["Nonce uniqueness, authenticated scope and algorithm edition are mandatory; encryption is not identity."], ["src.ietf.aead", "src.ietf.cose", "src.nist.gcm"]),
    ("bc.representation.transcode", "Can one representation be converted to another while preserving declared semantics, fidelity and identity scopes?", ["source/target profile", "loss ledger", "metadata mapping", "transcode receipt"], ["semantic model migration", "storage movement"], ["Transcode never claims lossless from container readability alone; each semantic and metadata component is reconciled."], ["src.jpeg.jpegxl", "src.ietf.flac", "src.ogc.cog"]),
    ("bc.representation.corruption_recovery", "What can be recovered after malformed, truncated or corrupt input and what evidence remains unavailable?", ["resynchronization", "block skip", "recovery boundary", "damage map"], ["backup/restore", "business correction"], ["Recovered output is marked partial with exact damaged ranges; best effort never masquerades as valid complete data."], ["src.avro.spec", "src.snappy.frame", "src.ietf.flac"]),
    ("bc.representation.streaming", "What finite-state encoder/decoder contract handles incremental input, backpressure, flush and finalization?", ["incremental states", "flush/end semantics", "bounded buffering", "cancellation"], ["transport protocol", "job scheduler"], ["End-of-input, need-more-input, need-more-output, cancelled and malformed are distinct results."], ["src.ietf.brotli", "src.lz4.frame", "src.ietf.flac"]),
    ("bc.representation.target_capability", "Which compute, memory and I/O target capabilities constrain legal representation and codec bindings?", ["target profile", "memory space", "SIMD/device/offload capability"], ["resource allocation", "provider implementation"], ["Target support is a versioned probed offer, never inferred from architecture name."], ["src.nvidia.nvcomp", "src.intel.iaa", "src.microsoft.gdeflate"]),
    ("bc.representation.kernel_contract", "What typed kernel transforms buffers on a target with bounded resources, alignment and cancellation semantics?", ["kernel ports", "memory spaces", "alignment", "async receipt"], ["algorithm semantics", "device scheduling"], ["A fast kernel is qualified against the algorithm oracle and never becomes the semantic owner."], ["src.nvidia.nvcomp", "src.intel.iaa", "src.arrow.columnar"]),
    ("bc.representation.provider_qualification", "How does an implementation prove conformance, interoperability, resource behavior and failure safety for a capability offer?", ["offer contract", "fixtures", "differential tests", "qualification evidence"], ["vendor procurement", "product branding"], ["Claims and benchmarks are scoped to exact versions, parameters, targets and corpora."], ["src.w3c.png3", "src.arrow.security", "src.oci.descriptor"]),
    ("bc.representation.edition_compatibility", "Which encoded component editions may coexist and what reader capability is required?", ["edition identity", "reader/writer matrix", "extension behavior", "upcast/transcode"], ["domain schema compatibility", "release deployment"], ["Unknown required component is a typed unsupported result; it is never silently skipped."], ["src.vortex.editions", "src.parquet.format", "src.ietf.flac"]),
    ("bc.representation.resource_model", "What finite size, memory, work, latency, energy and amplification budgets govern encode/decode?", ["resource estimates", "worst-case expansion", "budget refusal"], ["infrastructure quota", "business cost policy"], ["Every decode has output and work limits defending against decompression bombs and adversarial inputs."], ["src.ietf.brotli", "src.arrow.security", "src.ietf.zstd"]),
    ("bc.representation.detection", "How may an unknown byte source be inspected and classified without trusting extensions or ambiguous magic alone?", ["bounded probe", "candidate profile", "confidence/evidence", "ambiguity gap"], ["semantic inference", "malware analysis"], ["Detection never supplies missing semantic type, encryption key, schema or trust; ambiguity remains a gap."], ["src.avro.spec", "src.w3c.png3", "src.oci.descriptor"]),
]


CONTEXTS = [
    {
        "context_id": cid,
        "edition": EDITION,
        "status": "candidate_not_adjudicated",
        "sovereign_question": question,
        "owns": owns,
        "inside": owns,
        "outside": outside,
        "invariants": invariants,
        "neighbors": [],
        "compiler_surfaces": ["typed requirement", "capability offer", "decision point", "operation", "proof obligation", "runtime receipt"],
        "evidence_refs": evidence,
        "gaps": ["Ownership must be adjudicated against global data-shape, storage, security, runtime and compiler context maps."],
        "llm_dependency": "none",
    }
    for cid, question, owns, outside, invariants, evidence in CONTEXT_ROWS
]


# (id, kind, display name, loss class, evidence refs, capability traits)
REPRESENTATION_ROWS = [
    ("rep.carrier.bit_string", "carrier", "Bit string", "bitwise_lossless", ["src.ietf.deflate"], ["bit_addressable"]),
    ("rep.carrier.byte_string", "carrier", "Byte string", "bitwise_lossless", ["src.ietf.cbor"], ["byte_addressable"]),
    ("rep.carrier.contiguous_buffer", "carrier", "Contiguous host buffer", "bitwise_lossless", ["src.arrow.columnar"], ["random_access", "host_memory"]),
    ("rep.carrier.segmented_buffer", "carrier", "Segmented/scatter-gather buffers", "bitwise_lossless", ["src.arrow.columnar"], ["segmented", "zero_copy_possible"]),
    ("rep.carrier.byte_stream", "carrier", "Sequential byte stream", "bitwise_lossless", ["src.ietf.brotli"], ["streaming", "non_seekable"]),
    ("rep.carrier.seekable_byte_source", "carrier", "Seekable byte source", "bitwise_lossless", ["src.parquet.format"], ["seekable", "range_readable"]),
    ("rep.carrier.memory_mapped_region", "carrier", "Memory-mapped byte region", "bitwise_lossless", ["src.arrow.columnar"], ["random_access", "shared_memory"]),
    ("rep.carrier.device_buffer", "carrier", "Device-resident buffer", "bitwise_lossless", ["src.nvidia.nvcomp"], ["device_memory", "async_possible"]),
    ("rep.scalar.little_endian_fixed", "scalar_encoding", "Little-endian fixed-width scalar", "bitwise_lossless", ["src.arrow.columnar"], ["little_endian", "fixed_width"]),
    ("rep.scalar.big_endian_fixed", "scalar_encoding", "Big-endian fixed-width scalar", "bitwise_lossless", ["src.unicode.17"], ["big_endian", "fixed_width"]),
    ("rep.scalar.twos_complement", "scalar_encoding", "Two's-complement signed integer", "bitwise_lossless", ["src.arrow.columnar"], ["signed", "fixed_width"]),
    ("rep.scalar.ieee754_binary", "scalar_encoding", "IEEE-style binary floating-point carrier", "bitwise_lossless", ["src.arrow.columnar"], ["nan_payload_policy_required", "signed_zero"]),
    ("rep.scalar.unsigned_varint", "scalar_encoding", "Unsigned base-128 varint", "bitwise_lossless", ["src.protobuf.encoding"], ["variable_width", "unsigned"]),
    ("rep.scalar.zigzag_varint", "scalar_encoding", "Zigzag signed varint", "bitwise_lossless", ["src.protobuf.encoding"], ["variable_width", "signed"]),
    ("rep.scalar.bit_packed", "scalar_encoding", "Fixed-bit-width packed integers", "bitwise_lossless", ["src.parquet.format"], ["bit_packed", "range_bound_required"]),
    ("rep.character.utf8", "character_encoding", "UTF-8", "semantic_lossless", ["src.unicode.17", "src.ietf.utf8"], ["byte_order_invariant", "variable_width"]),
    ("rep.character.utf16", "character_encoding", "UTF-16 with declared byte order", "semantic_lossless", ["src.unicode.17"], ["bom_policy", "variable_width"]),
    ("rep.character.utf32", "character_encoding", "UTF-32 with declared byte order", "semantic_lossless", ["src.unicode.17"], ["bom_policy", "fixed_code_unit"]),
    ("rep.serialization.json", "schema_serialization", "JSON serialization", "semantic_lossless", ["src.ietf.json"], ["text", "schema_external_or_profile"]),
    ("rep.serialization.cbor", "schema_serialization", "CBOR serialization", "semantic_lossless", ["src.ietf.cbor"], ["self_delimiting", "tag_extensible"]),
    ("rep.serialization.protobuf", "schema_serialization", "Protocol Buffers wire format", "semantic_lossless", ["src.protobuf.encoding", "src.protobuf.deterministic"], ["schema_external", "unknown_fields"]),
    ("rep.serialization.avro_binary", "schema_serialization", "Avro binary encoding", "semantic_lossless", ["src.avro.spec"], ["writer_schema_required", "schema_resolution"]),
    ("rep.serialization.flatbuffers", "schema_serialization", "FlatBuffers wire format", "semantic_lossless", ["src.flatbuffers.internals"], ["random_access", "schema_external"]),
    ("rep.serialization.capnproto", "schema_serialization", "Cap'n Proto wire format", "semantic_lossless", ["src.capnproto.encoding"], ["segmented", "schema_external"]),
    ("rep.serialization.messagepack", "schema_serialization", "MessagePack wire format", "semantic_lossless", ["src.msgpack.spec"], ["self_describing_syntax", "extension_types"]),
    ("rep.serialization.asn1_ber", "schema_serialization", "ASN.1 Basic Encoding Rules", "semantic_lossless", ["src.itu.x690"], ["tag_length_value", "multiple_encodings"]),
    ("rep.serialization.asn1_der", "schema_serialization", "ASN.1 Distinguished Encoding Rules", "semantic_lossless", ["src.itu.x690"], ["canonical_profile", "tag_length_value"]),
    ("rep.framing.length_prefix", "framing", "Length-prefixed frame", "bitwise_lossless", ["src.protobuf.encoding"], ["bounded_length_required", "incremental"]),
    ("rep.framing.type_length_value", "framing", "Type-length-value frame", "bitwise_lossless", ["src.itu.x690"], ["typed", "skippability_profile"]),
    ("rep.framing.delimited_text", "framing", "Escaped delimiter framing", "semantic_lossless", ["src.ietf.json"], ["delimiter", "escaping_required"]),
    ("rep.framing.sync_marker", "framing", "Synchronization-marker blocks", "bitwise_lossless", ["src.avro.spec"], ["splittable", "resynchronizable"]),
    ("rep.framing.independent_blocks", "framing", "Independently decodable blocks", "bitwise_lossless", ["src.lz4.frame"], ["parallel_decode", "restartable"]),
    ("rep.layout.row", "physical_layout", "Row-major record layout", "bitwise_lossless", ["src.avro.spec"], ["row_locality"]),
    ("rep.layout.columnar", "physical_layout", "Column-major analytical layout", "bitwise_lossless", ["src.arrow.columnar"], ["column_locality", "vectorizable"]),
    ("rep.layout.hybrid_pax", "physical_layout", "Page-local hybrid row/column layout", "bitwise_lossless", ["src.parquet.format"], ["page_local", "hybrid"]),
    ("rep.layout.validity_offsets_values", "physical_layout", "Validity plus offsets plus values nested layout", "bitwise_lossless", ["src.arrow.columnar"], ["nested", "null_distinct_from_empty"]),
    ("rep.layout.definition_repetition", "physical_layout", "Definition and repetition level nested layout", "bitwise_lossless", ["src.parquet.format"], ["nested", "levels"]),
    ("rep.layout.page", "physical_layout", "Page layout", "bitwise_lossless", ["src.parquet.format"], ["page_grain", "metadata"]),
    ("rep.layout.row_group", "physical_layout", "Row-group layout", "bitwise_lossless", ["src.parquet.format"], ["row_partition", "column_chunks"]),
    ("rep.layout.stripe", "physical_layout", "Stripe layout", "bitwise_lossless", ["src.orc.spec"], ["stripe_grain", "stream_directory"]),
    ("rep.layout.multidimensional_chunk", "physical_layout", "N-dimensional chunk layout", "bitwise_lossless", ["src.hdf5.chunking", "src.zarr.v3"], ["coordinate_access", "chunk_atomic"]),
    ("rep.layout.tile_pyramid", "physical_layout", "Tiled multiresolution pyramid", "semantic_lossless", ["src.ogc.cog"], ["range_readable", "progressive_resolution"]),
    ("rep.layout.shard_index", "physical_layout", "Indexed shard of logical chunks", "bitwise_lossless", ["src.zarr.sharding"], ["range_readable", "small_object_reduction"]),
    ("rep.column.plain", "column_encoding", "Plain typed values", "bitwise_lossless", ["src.parquet.format"], ["baseline"]),
    ("rep.column.dictionary", "column_encoding", "Dictionary indices plus dictionary", "bitwise_lossless", ["src.arrow.columnar"], ["dictionary", "cardinality_sensitive"]),
    ("rep.column.run_length", "column_encoding", "Run-length encoding", "bitwise_lossless", ["src.orc.spec"], ["run_length", "order_sensitive"]),
    ("rep.column.run_end", "column_encoding", "Run-end encoded layout", "bitwise_lossless", ["src.arrow.columnar"], ["run_length", "log_random_access"]),
    ("rep.column.delta_binary_packed", "column_encoding", "Delta binary packed integers", "bitwise_lossless", ["src.parquet.format"], ["delta", "bit_packed"]),
    ("rep.column.delta_length_byte_array", "column_encoding", "Delta-length byte arrays", "bitwise_lossless", ["src.parquet.format"], ["delta_length", "variable_width"]),
    ("rep.column.delta_byte_array", "column_encoding", "Prefix/delta byte arrays", "bitwise_lossless", ["src.parquet.format"], ["prefix", "order_sensitive"]),
    ("rep.column.byte_stream_split", "column_encoding", "Byte-stream split", "bitwise_lossless", ["src.parquet.format"], ["byte_transpose", "compression_preconditioner"]),
    ("rep.column.frame_of_reference", "column_encoding", "Frame-of-reference integer encoding", "bitwise_lossless", ["src.vldb.alp"], ["frame_of_reference", "bit_packed"]),
    ("rep.column.patched_frame_of_reference", "column_encoding", "Patched frame-of-reference", "bitwise_lossless", ["src.sigmod.btrblocks"], ["frame_of_reference", "exception_patch"]),
    ("rep.column.alp_float", "column_encoding", "ALP adaptive lossless floating-point encoding", "bitwise_lossless", ["src.vldb.alp"], ["floating_point", "adaptive", "simd"]),
    ("rep.column.chimp_float", "column_encoding", "Chimp lossless floating-point stream encoding", "bitwise_lossless", ["src.vldb.chimp"], ["floating_point", "xor", "streaming"]),
    ("rep.column.elf_float", "column_encoding", "Elf lossless floating-point stream encoding", "bitwise_lossless", ["src.vldb.elf"], ["floating_point", "erasing_recoverable", "streaming"]),
    ("rep.column.roaring_bitmap", "column_encoding", "Roaring portable bitmap containers", "bitwise_lossless", ["src.roaring.format"], ["bitmap", "adaptive_container"]),
    ("rep.compression.none", "compression_algorithm", "Identity/no compression", "bitwise_lossless", ["src.avro.spec"], ["zero_transform"]),
    ("rep.compression.deflate", "compression_algorithm", "DEFLATE", "bitwise_lossless", ["src.ietf.deflate"], ["lz77", "huffman"]),
    ("rep.compression.zstandard", "compression_algorithm", "Zstandard", "bitwise_lossless", ["src.ietf.zstd"], ["lz_matching", "huffman", "fse", "dictionary_optional"]),
    ("rep.compression.brotli", "compression_algorithm", "Brotli", "bitwise_lossless", ["src.ietf.brotli"], ["lz77", "huffman", "static_dictionary"]),
    ("rep.compression.lz4", "compression_algorithm", "LZ4 block coding", "bitwise_lossless", ["src.lz4.frame"], ["lz_matching", "fast_decode"]),
    ("rep.compression.snappy", "compression_algorithm", "Snappy block coding", "bitwise_lossless", ["src.snappy.frame"], ["lz_matching", "fast_decode"]),
    ("rep.compression.lzma2", "compression_algorithm", "LZMA2", "bitwise_lossless", ["src.xz.format"], ["dictionary", "range_coding"]),
    ("rep.compression.huffman", "compression_algorithm", "Huffman prefix coding", "bitwise_lossless", ["src.ietf.deflate"], ["entropy", "prefix_code"]),
    ("rep.compression.fse_ans", "compression_algorithm", "Finite-state entropy / ANS coding", "bitwise_lossless", ["src.ietf.zstd"], ["entropy", "state_machine"]),
    ("rep.compression.rice_golomb", "compression_algorithm", "Rice/Golomb residual coding", "bitwise_lossless", ["src.ietf.flac"], ["residual", "variable_length"]),
    ("rep.compression.sz3", "compression_algorithm", "SZ3 error-bounded scientific compression", "error_bounded_lossy", ["src.sz3"], ["prediction", "quantization", "error_bound"]),
    ("rep.compression.zfp", "compression_algorithm", "zfp scientific array compression", "mixed_declared", ["src.zfp.modes"], ["transform", "fixed_rate", "fixed_precision", "fixed_accuracy", "reversible"]),
    ("rep.container.gzip", "container_file_format", "gzip member stream", "bitwise_lossless", ["src.ietf.gzip"], ["sequential", "crc", "concatenable"]),
    ("rep.container.zstd_frame", "container_file_format", "Zstandard frame", "bitwise_lossless", ["src.ietf.zstd"], ["frame", "checksum_optional", "dictionary_id"]),
    ("rep.container.lz4_frame", "container_file_format", "LZ4 frame", "bitwise_lossless", ["src.lz4.frame"], ["frame", "block_independence_selectable", "checksum_optional"]),
    ("rep.container.snappy_framed", "container_file_format", "Snappy framed stream", "bitwise_lossless", ["src.snappy.frame"], ["chunks", "crc32c", "concatenable"]),
    ("rep.container.xz", "container_file_format", "XZ container", "bitwise_lossless", ["src.xz.format"], ["blocks", "index", "checks"]),
    ("rep.container.avro_ocf", "container_file_format", "Avro Object Container File", "semantic_lossless", ["src.avro.spec"], ["schema_embedded", "sync_blocks", "splittable"]),
    ("rep.container.arrow_ipc", "container_file_format", "Arrow IPC stream/file", "semantic_lossless", ["src.arrow.columnar"], ["record_batches", "zero_copy_oriented", "random_access_file"]),
    ("rep.container.parquet", "container_file_format", "Apache Parquet file", "semantic_lossless", ["src.parquet.format"], ["columnar", "row_groups", "pages", "footer"]),
    ("rep.container.orc", "container_file_format", "Apache ORC file", "semantic_lossless", ["src.orc.spec"], ["columnar", "stripes", "streams", "footer"]),
    ("rep.container.hdf5", "container_file_format", "HDF5 file", "semantic_lossless", ["src.hdf5.format"], ["self_describing", "chunked_or_contiguous", "filter_pipeline"]),
    ("rep.container.netcdf", "container_file_format", "netCDF physical format family", "semantic_lossless", ["src.netcdf.format"], ["multiple_physical_variants", "nd_array"]),
    ("rep.container.zarr3", "container_file_format", "Zarr version 3 store", "semantic_lossless", ["src.zarr.v3"], ["nd_array", "chunked", "codec_pipeline", "key_value_store"]),
    ("rep.container.cog", "container_file_format", "Cloud Optimized GeoTIFF", "semantic_lossless", ["src.ogc.cog", "src.ogc.geotiff"], ["tiled", "overview", "http_range"]),
    ("rep.container.geoparquet", "container_file_format", "GeoParquet", "semantic_lossless", ["src.geoparquet.spec", "src.parquet.format"], ["geospatial_vector", "parquet_profile"]),
    ("rep.container.pmtiles3", "container_file_format", "PMTiles v3", "semantic_lossless", ["src.pmtiles.v3"], ["tile_archive", "range_readable", "directory_index"]),
    ("rep.container.matroska", "container_file_format", "Matroska", "semantic_lossless", ["src.ietf.matroska"], ["multitrack", "timecoded", "codec_container"]),
    ("rep.container.dicom_transfer", "container_file_format", "DICOM transfer syntax envelope", "mixed_declared", ["src.dicom.transfer"], ["medical", "explicit_or_implicit_vr", "encapsulated_pixel_data"]),
    ("rep.container.bam_bgzf", "container_file_format", "BAM in BGZF", "semantic_lossless", ["src.hts.specs"], ["genomics", "splittable_gzip_blocks", "indexed"]),
    ("rep.container.cram", "container_file_format", "CRAM", "mixed_declared", ["src.hts.specs"], ["genomics", "reference_dependent", "preservation_map"]),
    ("rep.container.lance_file", "container_file_format", "Lance file container", "semantic_lossless", ["src.lance.format"], ["column_pages", "cloud_random_access", "arrow_native"]),
    ("rep.container.nimble", "container_file_format", "Nimble research file format", "semantic_lossless", ["src.meta.nimble"], ["wide_table", "cascading_encoding", "unstable"]),
    ("rep.container.vortex", "container_file_format", "Vortex editioned format", "semantic_lossless", ["src.vortex.editions", "src.vortex.project"], ["compressed_array", "extensible_components", "editioned"]),
    ("rep.codec.png", "domain_codec", "PNG/APNG codec", "bitwise_lossless", ["src.w3c.png3"], ["image", "lossless", "progressive"]),
    ("rep.codec.jpeg", "domain_codec", "JPEG 1 codec family", "perceptual_lossy", ["src.jpeg.jpeg1"], ["image", "lossy", "profile_required"]),
    ("rep.codec.jpegxl", "domain_codec", "JPEG XL codec", "mixed_declared", ["src.jpeg.jpegxl"], ["image", "lossless", "lossy", "progressive", "jpeg_reconstruction"]),
    ("rep.codec.avif", "domain_codec", "AVIF image codec/container profile", "mixed_declared", ["src.aom.avif"], ["image", "av1_payload", "lossless", "lossy"]),
    ("rep.codec.openexr", "domain_codec", "OpenEXR image codec/container", "mixed_declared", ["src.openexr.spec"], ["hdr_image", "channels", "tiles", "lossless_and_lossy_modes"]),
    ("rep.codec.flac", "domain_codec", "FLAC audio codec", "bitwise_lossless", ["src.ietf.flac"], ["audio", "lossless", "streamable_subset"]),
    ("rep.codec.opus", "domain_codec", "Opus audio codec", "perceptual_lossy", ["src.ietf.opus"], ["audio", "lossy", "low_latency", "rate_control"]),
    ("rep.codec.av1", "domain_codec", "AV1 video codec", "mixed_declared", ["src.aom.av1"], ["video", "lossy", "lossless_profile", "hardware_profiles"]),
    ("rep.codec.av2", "domain_codec", "AV2 video codec", "mixed_declared", ["src.aom.av2"], ["video", "lossy", "lossless_profile", "new_2026"]),
    ("rep.codec.las", "domain_codec", "LAS point-cloud coding", "semantic_lossless", ["src.asprs.las"], ["point_cloud", "scaled_integer_coordinates"]),
    ("rep.canonical.jcs", "canonicalization_profile", "JSON Canonicalization Scheme", "semantic_lossless", ["src.ietf.jcs"], ["canonical", "json"]),
    ("rep.canonical.cbor_core_deterministic", "canonicalization_profile", "CBOR core deterministic profile", "semantic_lossless", ["src.ietf.cbor"], ["deterministic", "profile_not_universal_canonical"]),
    ("rep.canonical.asn1_der", "canonicalization_profile", "ASN.1 DER canonical profile", "semantic_lossless", ["src.itu.x690"], ["canonical", "asn1"]),
    ("rep.integrity.crc32", "integrity_algorithm", "CRC-32", "bitwise_lossless", ["src.w3c.png3"], ["error_detection", "not_cryptographic"]),
    ("rep.integrity.crc32c", "integrity_algorithm", "CRC-32C", "bitwise_lossless", ["src.snappy.frame"], ["error_detection", "not_cryptographic"]),
    ("rep.integrity.sha256", "integrity_algorithm", "SHA-256 digest", "bitwise_lossless", ["src.nist.shs", "src.oci.descriptor"], ["collision_resistant", "content_identity"]),
    ("rep.integrity.sha3_256", "integrity_algorithm", "SHA3-256 digest", "bitwise_lossless", ["src.nist.sha3"], ["collision_resistant", "content_identity"]),
    ("rep.protection.aead", "cryptographic_envelope", "AEAD envelope", "bitwise_lossless", ["src.ietf.aead", "src.nist.gcm"], ["confidentiality", "integrity_authentication", "nonce_required"]),
    ("rep.protection.cose", "cryptographic_envelope", "COSE signing/encryption envelope", "bitwise_lossless", ["src.ietf.cose"], ["cbor", "signature", "encryption", "mac"]),
    ("rep.protection.jws", "cryptographic_envelope", "JWS signature envelope", "bitwise_lossless", ["src.ietf.jws"], ["json", "signature", "protected_headers"]),
    ("rep.chunk.fixed_bytes", "chunking_scheme", "Fixed-size byte chunking", "bitwise_lossless", ["src.hdf5.chunking"], ["deterministic_boundaries", "size_configured"]),
    ("rep.chunk.semantic_records", "chunking_scheme", "Record-boundary chunking", "semantic_lossless", ["src.avro.spec"], ["record_aligned", "count_and_size"]),
    ("rep.chunk.nd_coordinates", "chunking_scheme", "N-dimensional coordinate chunking", "semantic_lossless", ["src.zarr.v3"], ["coordinate_key", "shape_configured"]),
    ("rep.chunk.content_defined", "chunking_scheme", "Content-defined byte chunking", "bitwise_lossless", ["src.oci.descriptor"], ["rolling_fingerprint_required", "dedup_oriented"]),
    ("rep.target.scalar_cpu", "execution_target", "Portable scalar CPU target", "bitwise_lossless", ["src.ietf.zstd"], ["host_memory", "portable"]),
    ("rep.target.simd_cpu", "execution_target", "SIMD CPU target", "bitwise_lossless", ["src.arrow.columnar", "src.vldb.alp"], ["alignment", "vector_width"]),
    ("rep.target.multicore_cpu", "execution_target", "Multicore CPU target", "bitwise_lossless", ["src.ietf.zstd"], ["threads", "chunk_parallel"]),
    ("rep.target.gpu", "execution_target", "GPU device target", "bitwise_lossless", ["src.nvidia.nvcomp", "src.microsoft.gdeflate"], ["device_memory", "batch_parallel", "async"]),
    ("rep.target.hardware_offload", "execution_target", "Dedicated compression accelerator target", "bitwise_lossless", ["src.intel.iaa"], ["queue", "offload", "capability_probe"]),
    ("rep.target.object_store_range", "execution_target", "Object-store HTTP range target", "bitwise_lossless", ["src.ogc.cog", "src.lance.format"], ["range_read", "request_cost", "latency"]),
    ("rep.target.embedded", "execution_target", "Bounded-memory embedded target", "bitwise_lossless", ["src.ietf.brotli", "src.ietf.flac"], ["bounded_memory", "streaming"]),
]


OWNER_BY_KIND = {
    "carrier": "bc.representation.carrier",
    "scalar_encoding": "bc.representation.scalar_encoding",
    "character_encoding": "bc.representation.character_encoding",
    "schema_serialization": "bc.representation.schema_serialization",
    "framing": "bc.representation.framing",
    "physical_layout": "bc.representation.physical_layout",
    "column_encoding": "bc.representation.column_encoding",
    "compression_algorithm": "bc.representation.compression_algorithm",
    "container_file_format": "bc.representation.container",
    "domain_codec": "bc.representation.codec",
    "canonicalization_profile": "bc.representation.canonicalization",
    "integrity_algorithm": "bc.representation.integrity",
    "cryptographic_envelope": "bc.representation.protection_envelope",
    "chunking_scheme": "bc.representation.chunking",
    "execution_target": "bc.representation.target_capability",
}


def loss_contract(loss_class: str) -> dict:
    if loss_class in {"bitwise_lossless", "semantic_lossless"}:
        return {
            "may_discard_information": False,
            "error_contract": "exact reconstruction under the declared semantic/bitwise equality and valid input profile",
            "metric": "bitwise identity" if loss_class == "bitwise_lossless" else "declared semantic equality",
            "bound": "zero",
            "approval_required": False,
            "verification": "round-trip oracle plus cross-implementation fixtures",
        }
    if loss_class == "error_bounded_lossy":
        return {
            "may_discard_information": True,
            "error_contract": "caller must select an absolute, relative, pointwise-relative, significant-digit, norm, or named application bound",
            "metric": "selected numeric and protected-observable metrics",
            "bound": "finite explicit value with units and scope",
            "approval_required": True,
            "verification": "decode and check every required bound plus downstream protected-observable tests",
        }
    if loss_class == "perceptual_lossy":
        return {
            "may_discard_information": True,
            "error_contract": "caller must declare quality/rate target, protected features, acceptable perceptual metrics and human-review policy",
            "metric": "domain metric plus task/human acceptance; no single universal perceptual metric",
            "bound": "explicit profile; unbounded defaults forbidden",
            "approval_required": True,
            "verification": "decoded-signal metrics, adversarial exemplars and declared human/task acceptance",
        }
    if loss_class == "mixed_declared":
        return {
            "may_discard_information": "mode_dependent",
            "error_contract": "mode must be explicitly lossless or carry a complete finite loss/error contract before binding",
            "metric": "bitwise/semantic identity for lossless mode; named numeric or perceptual metrics for lossy mode",
            "bound": "zero for lossless; finite explicit profile for lossy",
            "approval_required": True,
            "verification": "mode-specific round-trip or error/quality oracle",
        }
    raise ValueError(loss_class)


REPRESENTATIONS = [
    {
        "representation_id": rid,
        "edition": EDITION,
        "status": "sourced_candidate",
        "record_kind": kind,
        "name": name,
        "definition": f"Provider-neutral candidate for {name}; exact behavior is the cited edition/profile, not a product-name heuristic.",
        "semantic_owner_context_ref": OWNER_BY_KIND[kind],
        "input_layer": "typed value or preceding representation layer",
        "output_layer": kind,
        "loss_class": loss,
        "loss_contract": loss_contract(loss),
        "capability_traits": traits,
        "parameters": ["exact edition/profile", "resource limits", "compatibility policy", "target capability"] + (["loss/error profile"] if loss in {"error_bounded_lossy", "perceptual_lossy", "mixed_declared"} else []),
        "access_contract": ["streaming/restart/random-access/splittability are independent declared traits", "worst-case read and decode amplification must be qualified"],
        "integrity_contract": ["integrity scope is separate from codec/container identity", "untrusted input is bounded before allocation and decode"],
        "compatibility_contract": ["writer and reader component editions resolve", "unknown required feature produces unsupported_capability"],
        "target_requirements": ["memory space and alignment", "finite output/work bound", "qualified implementation offer"],
        "forbidden_inferences": ["file extension proves format", "format proves semantic type", "codec name proves splittability", "deterministic output proves canonicalization", "checksum proves authenticity"],
        "evidence_refs": evidence,
        "compiler_implications": ["match requirements to traits and evidence", "emit every selected parameter and rejected alternative", "retain exact source and target representation identities"],
        "gaps": ["Requires conformance fixtures and two unrelated vertical bindings before adjudication."],
        "dispatch_key": "capability_signature_only",
        "llm_dependency": "none",
    }
    for rid, kind, name, loss, evidence, traits in REPRESENTATION_ROWS
]


OPERATION_ROWS = [
    ("operation.representation.encode", "Encode", "bc.representation.schema_serialization", ["TypedValue<T>", "EncodingProfile"], ["EncodedBytes<Profile>", "EncodeReceipt"], "conditionally_lossless"),
    ("operation.representation.decode", "Decode", "bc.representation.schema_serialization", ["BoundedBytes", "EncodingProfile", "DecodeLimits"], ["TypedValue<T>", "DecodeReceipt"], "not_applicable"),
    ("operation.representation.byte_swap", "Byte swap", "bc.representation.byte_order", ["FixedWidthWords<W,FromEndian>"], ["FixedWidthWords<W,ToEndian>"], "lossless"),
    ("operation.representation.transcode_text", "Transcode character encoding", "bc.representation.character_encoding", ["ValidatedText<FromEncoding>", "MalformedPolicy"], ["ValidatedText<ToEncoding>", "TranscodeReceipt"], "conditionally_lossless"),
    ("operation.representation.canonicalize", "Canonicalize", "bc.representation.canonicalization", ["SemanticDocument<T>", "CanonicalProfile"], ["CanonicalBytes<Profile>", "CanonicalReceipt"], "conditionally_lossless"),
    ("operation.representation.frame", "Frame", "bc.representation.framing", ["PayloadBytes", "FramingProfile"], ["FramedBytes<Profile>"], "lossless"),
    ("operation.representation.deframe", "Deframe", "bc.representation.framing", ["BoundedFramedBytes", "FramingProfile", "DecodeLimits"], ["PayloadFrames", "DamageMap"], "not_applicable"),
    ("operation.representation.pack_bits", "Bit pack", "bc.representation.scalar_encoding", ["IntegerSequence", "VerifiedRange", "BitWidth"], ["PackedBits", "PackReceipt"], "lossless"),
    ("operation.representation.unpack_bits", "Bit unpack", "bc.representation.scalar_encoding", ["PackedBits", "Count", "BitWidth"], ["IntegerSequence"], "not_applicable"),
    ("operation.representation.dictionary_encode", "Dictionary encode", "bc.representation.column_encoding", ["ValueSequence<T>", "DictionaryPolicy"], ["Dictionary<T>", "IndexSequence", "EscapeSequence"], "lossless"),
    ("operation.representation.dictionary_decode", "Dictionary decode", "bc.representation.column_encoding", ["Dictionary<T>", "IndexSequence", "EscapeSequence"], ["ValueSequence<T>"], "not_applicable"),
    ("operation.representation.run_length_encode", "Run-length encode", "bc.representation.column_encoding", ["OrderedValueSequence<T>"], ["RunSequence<T>"], "lossless"),
    ("operation.representation.delta_encode", "Delta encode", "bc.representation.column_encoding", ["OrderedNumericSequence<T>", "OverflowPolicy"], ["BaseValue<T>", "DeltaSequence<D>"], "lossless"),
    ("operation.representation.frame_of_reference", "Frame-of-reference encode", "bc.representation.column_encoding", ["NumericBlock<T>", "ReferencePolicy"], ["Reference<T>", "ResidualBlock<D>"], "lossless"),
    ("operation.representation.encode_nested_levels", "Encode nested levels", "bc.representation.null_nested_layout", ["NestedValues<T>", "Schema"], ["LeafValues<T>", "DefinitionLevels", "RepetitionLevels"], "lossless"),
    ("operation.representation.decode_nested_levels", "Decode nested levels", "bc.representation.null_nested_layout", ["LeafValues<T>", "DefinitionLevels", "RepetitionLevels", "Schema"], ["NestedValues<T>"], "not_applicable"),
    ("operation.representation.compress", "Compress losslessly", "bc.representation.compression_algorithm", ["UncompressedBytes", "LosslessCompressionProfile", "Budget"], ["CompressedBytes<Profile>", "CompressionReceipt"], "lossless"),
    ("operation.representation.compress_lossy", "Compress with declared loss", "bc.representation.loss_contract", ["TypedSignal<T>", "LossProfile", "Budget", "Approval"], ["LossyCodestream<Profile>", "LossReceipt"], "lossy_declared"),
    ("operation.representation.decompress", "Decompress", "bc.representation.compression_algorithm", ["BoundedCompressedBytes<Profile>", "Dictionary?", "DecodeLimits"], ["DecodedBytes", "DecodeReceipt"], "not_applicable"),
    ("operation.representation.verify_loss", "Verify decoded loss/error", "bc.representation.loss_contract", ["Original<T>", "Decoded<T>", "LossProfile"], ["ErrorMeasurements", "PassOrRefusal"], "not_applicable"),
    ("operation.representation.chunk", "Partition into chunks", "bc.representation.chunking", ["LogicalInput<T>", "ChunkingProfile"], ["OrderedChunks<T>", "ChunkManifest"], "lossless"),
    ("operation.representation.reassemble", "Reassemble chunks", "bc.representation.chunking", ["ChunkManifest", "VerifiedChunks<T>"], ["LogicalInput<T>", "ReassemblyReceipt"], "not_applicable"),
    ("operation.representation.shard", "Shard chunks", "bc.representation.physical_layout", ["LogicalChunks", "ShardingProfile"], ["ShardBytes", "ShardIndex"], "lossless"),
    ("operation.representation.build_pruning_metadata", "Build pruning metadata", "bc.representation.pruning_metadata", ["TypedBlock<T>", "SummaryProfile"], ["ConservativeSummary<T>"], "lossless"),
    ("operation.representation.may_prune", "Evaluate pruning summary", "bc.representation.pruning_metadata", ["Predicate<T>", "ConservativeSummary<T>"], ["DefinitelyNoOrMaybe"], "not_applicable"),
    ("operation.representation.checksum", "Compute checksum", "bc.representation.integrity", ["ScopedBytes", "ChecksumProfile"], ["ChecksumValue", "ScopeReceipt"], "not_applicable"),
    ("operation.representation.verify_checksum", "Verify checksum", "bc.representation.integrity", ["ScopedBytes", "ExpectedChecksum"], ["VerifiedOrCorrupt"], "not_applicable"),
    ("operation.representation.digest", "Compute cryptographic digest", "bc.representation.content_identity", ["IdentityScopedBytes", "DigestProfile"], ["ContentDigest", "ScopeReceipt"], "not_applicable"),
    ("operation.representation.encrypt_aead", "AEAD encrypt", "bc.representation.protection_envelope", ["Plaintext", "AssociatedData", "Nonce", "KeyHandle", "AlgorithmProfile"], ["Ciphertext", "AuthenticationTag", "ProtectionReceipt"], "lossless"),
    ("operation.representation.decrypt_aead", "AEAD decrypt", "bc.representation.protection_envelope", ["Ciphertext", "AssociatedData", "Nonce", "Tag", "KeyHandle", "AlgorithmProfile"], ["AuthenticatedPlaintext"], "not_applicable"),
    ("operation.representation.sign", "Sign canonical scoped bytes", "bc.representation.protection_envelope", ["CanonicalScopedBytes", "KeyHandle", "SignatureProfile"], ["SignatureEnvelope", "SigningReceipt"], "not_applicable"),
    ("operation.representation.verify_signature", "Verify signature", "bc.representation.protection_envelope", ["CanonicalScopedBytes", "SignatureEnvelope", "TrustPolicy"], ["VerifiedSignerClaimOrRefusal"], "not_applicable"),
    ("operation.representation.transcode", "Transcode representation", "bc.representation.transcode", ["SourceRepresentation<S>", "TargetProfile", "LossPolicy", "MetadataPolicy"], ["TargetRepresentation<T>", "LossLedger", "TranscodeReceipt"], "conditionally_lossless"),
    ("operation.representation.inspect_bounded", "Inspect bounded header/metadata", "bc.representation.detection", ["BoundedPrefixSuffix", "ProbeBudget"], ["CandidateProfiles", "Evidence", "Ambiguities"], "not_applicable"),
    ("operation.representation.recover", "Recover independently valid regions", "bc.representation.corruption_recovery", ["DamagedRepresentation", "RecoveryProfile", "Budget"], ["RecoveredRegions", "DamageMap", "RecoveryReceipt"], "lossy_declared"),
    ("operation.representation.train_dictionary", "Train compression dictionary", "bc.representation.dictionary_lifecycle", ["VersionedTrainingCorpus", "TrainingPolicy", "Budget"], ["DictionaryArtifact", "TrainingReceipt"], "not_applicable"),
    ("operation.representation.plan_encoding", "Plan encoding pipeline", "bc.representation.compression_selection", ["RepresentationRequirements", "CorpusProfile", "ProviderOffers", "Budgets"], ["PhysicalEncodingPlan", "RejectedOffers", "PlanEvidence"], "not_applicable"),
    ("operation.representation.qualify_provider", "Qualify implementation offer", "bc.representation.provider_qualification", ["CapabilityOffer", "ConformanceFixtures", "Target", "Budgets"], ["QualificationEvidence", "ScopedVerdict"], "not_applicable"),
    ("operation.representation.stream_step", "Advance streaming codec", "bc.representation.streaming", ["CodecState", "InputWindow", "OutputWindow", "Directive", "Budget"], ["CodecState", "Progress", "NeedOrTerminalResult"], "conditionally_lossless"),
]


def operation_loss_contract(info_loss: str) -> dict:
    if info_loss == "lossy_declared":
        return {"class": info_loss, "required": True, "must_include": ["metric", "finite bound or explicit recovery damage range", "scope", "approval", "verification"]}
    if info_loss == "conditionally_lossless":
        return {"class": info_loss, "required": True, "must_include": ["equality relation", "malformed/unrepresentable policy", "any normalization or replacement"]}
    return {"class": info_loss, "required": False, "must_include": []}


OPERATIONS = [
    {
        "operation_id": oid,
        "edition": EDITION,
        "status": "sourced_candidate",
        "family_id": "operation.representation",
        "name": name,
        "operation_kind": "pure_transform" if oid not in {"operation.representation.qualify_provider", "operation.representation.plan_encoding", "operation.representation.stream_step"} else "planner",
        "semantic_owner_candidate": owner,
        "signature": {"type_parameters": ["T"], "inputs": inputs, "outputs": outputs, "error_type": "RepresentationError"},
        "effect_class": "pure",
        "determinism": "deterministic",
        "idempotency": "not_applicable",
        "totality": "partial_typed_refusal",
        "information_loss": info_loss,
        "loss_contract": operation_loss_contract(info_loss),
        "order_sensitivity": "order_required",
        "time_sensitivity": "none",
        "statefulness": "bounded_state" if oid.endswith(("stream_step", "train_dictionary")) else "stateless",
        "execution_modes": ["batch", "stream", "incremental", "embedded"],
        "preconditions": ["exact source and target profiles resolve", "finite input/output/work budgets", "required dictionary/schema/key/reference is available"],
        "postconditions": ["result carries exact representation identity", "receipt reports bytes, work, target and selected parameters", "no undeclared information loss"],
        "laws": ["no vendor-name dispatch", "failure cannot return apparently valid output", "unknown profile is unsupported_capability"],
        "refusals": ["unsupported_profile", "missing_schema", "missing_dictionary", "missing_reference", "loss_not_approved", "target_capability_absent", "budget_infeasible"],
        "failures": ["malformed_input", "truncated_input", "integrity_failure", "output_limit_exceeded", "work_limit_exceeded", "provider_fault", "cancelled"],
        "resource_model": ["input bytes", "maximum output bytes", "peak memory", "work units", "latency", "parallelism", "I/O amplification"],
        "provider_requirements": ["versioned capability offer", "conformance fixtures", "negative/adversarial tests", "resource evidence", "cancellation safety"],
        "evidence_refs": ["src.arrow.security", "src.ietf.zstd"],
        "llm_dependency": "none",
        "gaps": ["Exact Rust type and error algebra awaits global context ownership adjudication."],
    }
    for oid, name, owner, inputs, outputs, info_loss in OPERATION_ROWS
]


DECISION_ROWS = [
    ("decision.representation.equality", "Which equality must survive the round trip?", ["bitwise", "semantic_profile", "application_observable"], "semantic_closure"),
    ("decision.representation.loss_mode", "May the representation discard information?", ["lossless_only", "lossy_with_contract"], "semantic_closure"),
    ("decision.representation.error_metric", "Which error metric and finite bound govern loss?", ["absolute", "relative", "pointwise_relative", "significant_digits", "fixed_precision", "fixed_rate", "psnr", "perceptual_plus_task", "application_observable"], "semantic_closure"),
    ("decision.representation.original_retention", "Must the original representation be retained beside a lossy derivative?", ["required", "not_required_by_authority"], "assurance_insertion"),
    ("decision.representation.carrier", "Which carrier and memory space hold each boundary value?", ["contiguous_host", "segmented_host", "stream", "seekable", "mapped", "device"], "physical_binding"),
    ("decision.representation.byte_order", "Which byte and bit order crosses the boundary?", ["little", "big", "byte_invariant", "mixed_declared"], "logical_planning"),
    ("decision.representation.character_encoding", "Which character encoding and malformed-input policy apply?", ["utf8_strict", "utf16_declared_endian_strict", "utf32_declared_endian_strict", "explicit_legacy_acl"], "semantic_closure"),
    ("decision.representation.wire_profile", "Which exact schema serialization profile and edition apply?", ["registry_resolved_profile"], "logical_planning"),
    ("decision.representation.canonical_profile", "Is a canonical byte profile required, and which edition?", ["none", "registry_resolved_profile"], "logical_planning"),
    ("decision.representation.frame_grain", "What is the independently bounded frame grain?", ["message", "record_block", "page", "chunk", "media_frame", "container_member"], "logical_planning"),
    ("decision.representation.max_frame", "What maximum encoded and decoded frame sizes are accepted?", ["finite_declared"], "assurance_insertion"),
    ("decision.representation.layout", "Which physical layout satisfies declared access patterns?", ["row", "columnar", "hybrid", "nd_chunked", "tiled_pyramid", "sharded"], "physical_binding"),
    ("decision.representation.null_nested", "How are null, empty, missing and nesting represented?", ["validity_offsets", "definition_repetition", "tagged_profile", "not_applicable"], "logical_planning"),
    ("decision.representation.block_grain", "At what grain are encoding, compression, integrity and encryption independently applied?", ["frame", "page", "column_chunk", "row_group", "stripe", "tile", "nd_chunk", "shard", "file"], "physical_binding"),
    ("decision.representation.column_encoding", "Which column encoding plan is selected per typed block?", ["capability_and_evidence_selected"], "physical_binding"),
    ("decision.representation.dictionary", "Is a dictionary used and how is its identity/lifecycle resolved?", ["none", "embedded", "manifest_referenced", "registry_referenced"], "physical_binding"),
    ("decision.representation.compression", "Which compression requirement profile applies?", ["none", "lossless_ratio_oriented", "lossless_speed_oriented", "lossy_error_bounded", "lossy_perceptual"], "physical_binding"),
    ("decision.representation.codec_parameters", "Which complete algorithm parameters are fixed or runtime-adaptive?", ["compile_bound", "write_time_selected_with_receipt", "runtime_adaptive_with_receipt"], "physical_binding"),
    ("decision.representation.split", "Must encoded data be splittable for parallel work?", ["required", "not_required"], "logical_planning"),
    ("decision.representation.random_access", "Which random/range access guarantees and amplification bounds are required?", ["sequential", "block", "page", "row", "coordinate", "progressive"], "logical_planning"),
    ("decision.representation.statistics", "Which conservative pruning metadata may be emitted and trusted?", ["none", "min_max", "dictionary", "bloom", "page_index", "domain_summary"], "physical_binding"),
    ("decision.representation.checksum", "Which accidental-corruption check covers which grain?", ["none_by_policy", "crc32", "crc32c", "format_mandated"], "assurance_insertion"),
    ("decision.representation.digest_scope", "Which exact representation scope receives a collision-resistant digest?", ["canonical_semantic", "encoded", "compressed", "container_member", "whole_container", "transmitted_content"], "assurance_insertion"),
    ("decision.representation.encryption_scope", "Which members and metadata require authenticated encryption?", ["none_by_policy", "payload", "column", "footer", "member", "whole_container"], "assurance_insertion"),
    ("decision.representation.signature_scope", "Which canonical bytes and protected headers are signed?", ["none_by_policy", "manifest", "member", "whole_artifact"], "assurance_insertion"),
    ("decision.representation.chunking", "Which chunk boundary law and target size apply?", ["fixed", "record_aligned", "nd_coordinates", "content_defined"], "physical_binding"),
    ("decision.representation.target", "Which target capability profile executes each kernel?", ["portable_cpu", "simd_cpu", "multicore_cpu", "gpu", "hardware_offload", "embedded"], "physical_binding"),
    ("decision.representation.fallback", "What fallback is legal when an accelerated provider is unavailable?", ["portable_qualified", "alternate_qualified", "refuse"], "deployment_binding"),
    ("decision.representation.corruption", "What recovery behavior is authorized after corruption?", ["fail_whole", "skip_independent_block", "resynchronize_and_mark_partial", "conceal_media_with_damage_receipt"], "assurance_insertion"),
    ("decision.representation.transcode", "May existing artifacts be transcoded and under which loss/metadata policy?", ["exact_only", "semantic_lossless", "lossy_with_approval", "forbidden"], "logical_planning"),
    ("decision.representation.compatibility", "Which writer/reader editions and extension behavior are required?", ["exact", "backward_read", "forward_skip_optional", "transcode"], "physical_binding"),
    ("decision.representation.decode_limits", "Which output, nesting, allocation and work limits guard every decoder?", ["finite_declared"], "assurance_insertion"),
    ("decision.representation.benchmark_corpus", "Which representative and adversarial corpus qualifies selection?", ["versioned_domain_corpus_plus_adversarial"], "evidence_verification"),
    ("decision.representation.selection_objective", "How are size, latency, throughput, energy and amplification traded off?", ["lexicographic", "weighted_with_units", "pareto_then_authority"], "physical_binding"),
    ("decision.representation.recompression", "When does a changed pipeline require rewrite, dual-read or lazy migration?", ["rewrite", "dual_read", "lazy_on_access", "retain_old"], "deployment_binding"),
    ("decision.representation.probe_policy", "How much untrusted input may format detection inspect?", ["bounded_header_footer", "declared_profile_only", "quarantine_for_external_inspection"], "assurance_insertion"),
]


DECISIONS = [
    {
        "decision_id": did,
        "edition": EDITION,
        "status": "declared",
        "owner_context_ref": "bc.representation." + did.split(".")[2] if "bc.representation." + did.split(".")[2] in {c["context_id"] for c in CONTEXTS} else "bc.representation.compression_selection",
        "question": question,
        "value_contract": "Closed choice or registry reference with exact edition; values outside the contract produce a compiler gap.",
        "allowed_values": values,
        "binding_phase": phase,
        "authority_ref": "authority.intent_owner_or_governing_policy",
        "default_law": "forbidden",
        "default_value": None,
        "constraints": ["must not weaken declared fidelity, security, compatibility or resource requirements"],
        "conflicts": [],
        "implications": ["invalidates physical binding and downstream evidence when changed"],
        "affects_contracts": ["representation requirement", "provider offer", "kernel plan", "runtime receipt"],
        "evidence_required": ["standard/profile evidence", "provider qualification", "corpus benchmark where selection-dependent"],
        "change_semantics": ["semantic diff", "artifact migration disposition", "historical decoder retention"],
        "gaps": [],
    }
    for did, question, values, phase in DECISION_ROWS
]


MAPPING_ROWS = [
    ("mapping.text_interchange", "validated multilingual text interchange", ["semantic Unicode scalar sequence", "strict malformed-input policy"], ["operation.representation.transcode_text", "operation.representation.encode"], ["character_encoding", "byte_order_invariant"], ["decision.representation.character_encoding"]),
    ("mapping.signed_document", "stable signed structured document", ["semantic schema", "canonical bytes", "signature scope"], ["operation.representation.canonicalize", "operation.representation.digest", "operation.representation.sign"], ["canonicalization_profile", "collision_resistant", "signature"], ["decision.representation.canonical_profile", "decision.representation.digest_scope", "decision.representation.signature_scope"]),
    ("mapping.schema_message", "schema-evolving binary message", ["field identity", "writer/reader compatibility", "bounded frame"], ["operation.representation.encode", "operation.representation.frame"], ["schema_serialization", "unknown_fields", "bounded_length_required"], ["decision.representation.wire_profile", "decision.representation.max_frame"]),
    ("mapping.appendable_record_stream", "appendable and splittable record stream", ["schema binding", "restart marker", "block integrity"], ["operation.representation.frame", "operation.representation.compress", "operation.representation.checksum"], ["splittable", "schema_embedded", "restartable"], ["decision.representation.frame_grain", "decision.representation.split"]),
    ("mapping.column_scan", "selective analytical column scan", ["projection", "predicate pruning", "vector decode"], ["operation.representation.build_pruning_metadata", "operation.representation.may_prune", "operation.representation.decompress"], ["columnar", "page_random_access", "conservative_statistics"], ["decision.representation.layout", "decision.representation.statistics"]),
    ("mapping.nested_table", "nested analytical table round trip", ["null/empty distinction", "nested reconstruction", "schema evolution"], ["operation.representation.encode_nested_levels", "operation.representation.decode_nested_levels"], ["nested", "null_distinct_from_empty"], ["decision.representation.null_nested"]),
    ("mapping.random_row_lookup", "bounded random row lookup", ["row coordinate", "range-readable pages", "read amplification bound"], ["operation.representation.plan_encoding", "operation.representation.decompress"], ["row_random_access", "range_readable"], ["decision.representation.random_access", "decision.representation.block_grain"]),
    ("mapping.object_store_raster", "object-store range-readable raster", ["spatial window", "resolution level", "HTTP range behavior"], ["operation.representation.plan_encoding", "operation.representation.transcode"], ["tiled", "overview", "http_range"], ["decision.representation.layout", "decision.representation.random_access"]),
    ("mapping.scientific_array_lossless", "lossless chunked scientific array", ["dtype/shape/chunk coordinates", "exact round trip", "partial coordinate access"], ["operation.representation.chunk", "operation.representation.compress", "operation.representation.reassemble"], ["nd_array", "coordinate_access", "bitwise_lossless"], ["decision.representation.chunking", "decision.representation.loss_mode"]),
    ("mapping.scientific_array_lossy", "error-bounded scientific-array derivative", ["units", "finite error bound", "protected observables", "approval"], ["operation.representation.compress_lossy", "operation.representation.verify_loss"], ["error_bounded_lossy", "nd_array"], ["decision.representation.error_metric", "decision.representation.original_retention"]),
    ("mapping.media_stream", "low-latency coded media stream", ["sample/color profile", "rate/quality", "latency", "damage behavior"], ["operation.representation.compress_lossy", "operation.representation.frame", "operation.representation.stream_step"], ["streaming", "perceptual_lossy", "bounded_state"], ["decision.representation.codec_parameters", "decision.representation.corruption"]),
    ("mapping.lossless_archive", "long-lived lossless archive", ["exact decoder profile", "content identity", "integrity", "future reader"], ["operation.representation.compress", "operation.representation.digest"], ["bitwise_lossless", "editioned", "collision_resistant"], ["decision.representation.compatibility", "decision.representation.digest_scope"]),
    ("mapping.encrypted_columnar", "selectively accessible encrypted columnar artifact", ["column access authority", "metadata confidentiality", "pruning leakage policy"], ["operation.representation.encrypt_aead", "operation.representation.build_pruning_metadata"], ["columnar", "integrity_authentication"], ["decision.representation.encryption_scope", "decision.representation.statistics"]),
    ("mapping.content_addressed_artifact", "content-addressed immutable artifact", ["canonical identity scope", "digest algorithm", "size"], ["operation.representation.canonicalize", "operation.representation.digest"], ["canonicalization_profile", "content_identity"], ["decision.representation.canonical_profile", "decision.representation.digest_scope"]),
    ("mapping.gpu_decompression", "device-resident parallel decompression", ["supported codestream", "device buffers", "async/cancellation", "portable fallback"], ["operation.representation.decompress", "operation.representation.qualify_provider"], ["gpu", "device_memory", "batch_parallel"], ["decision.representation.target", "decision.representation.fallback"]),
    ("mapping.hardware_offload", "dedicated compression offload", ["queue capability", "algorithm subset", "fallback", "resource evidence"], ["operation.representation.compress", "operation.representation.qualify_provider"], ["hardware_offload", "capability_probe"], ["decision.representation.target", "decision.representation.fallback"]),
    ("mapping.corrupt_partial_recovery", "governed partial recovery from corrupt input", ["independent regions", "damage map", "partial-output authority"], ["operation.representation.inspect_bounded", "operation.representation.recover"], ["resynchronizable", "damage_receipt"], ["decision.representation.corruption", "decision.representation.probe_policy"]),
    ("mapping.cross_endian", "cross-endian fixed-width interchange", ["source/target byte order", "width", "alignment"], ["operation.representation.byte_swap"], ["fixed_width", "declared_endian"], ["decision.representation.byte_order"]),
    ("mapping.recompression_migration", "live recompression or format migration", ["old/new reader matrix", "identity changes", "rollback", "in-flight artifacts"], ["operation.representation.transcode", "operation.representation.verify_checksum"], ["transcode", "multi_version"], ["decision.representation.recompression", "decision.representation.transcode"]),
    ("mapping.unknown_bytes", "safe inspection of unknown bytes", ["finite probe", "trust boundary", "ambiguity result"], ["operation.representation.inspect_bounded"], ["bounded_probe", "ambiguous_gap"], ["decision.representation.probe_policy"]),
]


COMPILER_MAPPINGS = [
    {
        "mapping_id": mid,
        "edition": EDITION,
        "intent_pattern": intent,
        "required_semantic_inputs": requirements,
        "operation_refs": operations,
        "required_capability_traits": traits,
        "decision_refs": decisions,
        "binding_law": ["enumerate structurally compatible offers", "prove semantics, fidelity, access, resource, compatibility and target constraints", "select by declared objective without provider-name branches", "retain rejected offers and evidence"],
        "typed_refusals": ["unknown_semantics", "unsupported_profile", "unapproved_loss", "incompatible_reader", "target_unavailable", "resource_infeasible", "qualification_missing"],
        "output_ir": "PhysicalRepresentationPlan plus bindings, inverse plan, evidence, receipts and residual gaps",
    }
    for mid, intent, requirements, operations, traits, decisions in MAPPING_ROWS
]


LIBRARY_ROWS = [
    ("library.san_carrier", "semantic_pure", "bc.representation.carrier", ["Carrier", "MemorySpace", "Seekability"], ["decision.representation.carrier"]),
    ("library.san_byte_order", "algorithm_pure", "bc.representation.byte_order", ["Endian", "BitOrder", "Alignment"], ["decision.representation.byte_order"]),
    ("library.san_text_encoding", "algorithm_pure", "bc.representation.character_encoding", ["CharacterEncoding", "MalformedTextError"], ["decision.representation.character_encoding"]),
    ("library.san_scalar_encoding", "algorithm_pure", "bc.representation.scalar_encoding", ["ScalarEncoding", "Width", "Overflow"], ["decision.representation.byte_order"]),
    ("library.san_wire_schema", "semantic_pure", "bc.representation.schema_serialization", ["WireProfile", "FieldIdentity", "Compatibility"], ["decision.representation.wire_profile"]),
    ("library.san_framing", "algorithm_pure", "bc.representation.framing", ["Frame", "FrameBoundary", "FrameLimit"], ["decision.representation.frame_grain", "decision.representation.max_frame"]),
    ("library.san_canonical", "algorithm_pure", "bc.representation.canonicalization", ["CanonicalProfile", "CanonicalBytes"], ["decision.representation.canonical_profile"]),
    ("library.san_content_identity", "semantic_pure", "bc.representation.content_identity", ["IdentityScope", "ContentDigest"], ["decision.representation.digest_scope"]),
    ("library.san_chunking", "algorithm_pure", "bc.representation.chunking", ["ChunkBoundary", "ChunkManifest"], ["decision.representation.chunking"]),
    ("library.san_layout", "semantic_pure", "bc.representation.physical_layout", ["LayoutProfile", "AccessPath"], ["decision.representation.layout", "decision.representation.block_grain"]),
    ("library.san_nested_layout", "algorithm_pure", "bc.representation.null_nested_layout", ["Validity", "Offsets", "Levels"], ["decision.representation.null_nested"]),
    ("library.san_column_encoding", "algorithm_pure", "bc.representation.column_encoding", ["ColumnEncoding", "EncodedBlock"], ["decision.representation.column_encoding"]),
    ("library.san_dictionary", "semantic_pure", "bc.representation.dictionary_lifecycle", ["DictionaryId", "DictionaryArtifact", "TrainingReceipt"], ["decision.representation.dictionary"]),
    ("library.san_compression_contract", "semantic_pure", "bc.representation.compression_algorithm", ["CompressionProfile", "CompressedBytes"], ["decision.representation.compression", "decision.representation.codec_parameters"]),
    ("library.san_loss_contract", "policy_pure", "bc.representation.loss_contract", ["LossProfile", "ErrorMeasurement", "LossApproval"], ["decision.representation.loss_mode", "decision.representation.error_metric"]),
    ("library.san_integrity", "algorithm_pure", "bc.representation.integrity", ["ChecksumProfile", "VerifiedBytes"], ["decision.representation.checksum"]),
    ("library.san_protection_envelope", "semantic_pure", "bc.representation.protection_envelope", ["ProtectionProfile", "ProtectedBytes"], ["decision.representation.encryption_scope", "decision.representation.signature_scope"]),
    ("library.san_pruning_metadata", "algorithm_pure", "bc.representation.pruning_metadata", ["ConservativeSummary", "DefinitelyNoOrMaybe"], ["decision.representation.statistics"]),
    ("library.san_transcode_plan", "semantic_pure", "bc.representation.transcode", ["TranscodePlan", "LossLedger", "MetadataMapping"], ["decision.representation.transcode"]),
    ("library.san_codec_runtime", "runtime_mechanism", "bc.representation.compression_algorithm", ["CodecState", "CodecProgress", "CodecReceipt"], ["decision.representation.decode_limits"]),
    ("library.san_stream_codec", "runtime_mechanism", "bc.representation.streaming", ["StreamDirective", "NeedInput", "NeedOutput"], ["decision.representation.max_frame"]),
    ("library.san_random_access_reader", "runtime_mechanism", "bc.representation.random_access", ["RangePlan", "RestartPoint", "ReadReceipt"], ["decision.representation.random_access"]),
    ("library.san_representation_planner", "policy_pure", "bc.representation.compression_selection", ["RepresentationRequirements", "PhysicalRepresentationPlan"], ["decision.representation.selection_objective", "decision.representation.benchmark_corpus"]),
    ("library.san_codec_provider", "provider_adapter", "bc.representation.provider_qualification", ["CapabilityOffer", "ProviderHandle", "QualificationEvidence"], ["decision.representation.target", "decision.representation.fallback"]),
    ("library.san_codec_kernel", "target_backend", "bc.representation.kernel_contract", ["KernelOffer", "KernelInvocation", "KernelReceipt"], ["decision.representation.target"]),
    ("library.san_corruption_recovery", "runtime_mechanism", "bc.representation.corruption_recovery", ["DamageMap", "RecoveredRegion", "RecoveryReceipt"], ["decision.representation.corruption"]),
    ("library.san_format_probe", "runtime_mechanism", "bc.representation.detection", ["ProbeBudget", "CandidateProfile", "AmbiguityGap"], ["decision.representation.probe_policy"]),
]


LIBRARIES = [
    {
        "library_id": lid,
        "edition": EDITION,
        "status": "hypothesis",
        "library_kind": kind,
        "semantic_owner_refs": [owner] if kind in {"semantic_pure", "policy_pure"} else [],
        "contributes_to_context_refs": [owner],
        "effect_boundary": "pure_no_io" if kind in {"semantic_pure", "algorithm_pure", "policy_pure"} else "effectful_runtime",
        "public_types": public_types,
        "public_traits": ["CapabilityRequirement", "CapabilityOffer", "ConformanceOracle"],
        "operation_refs": [row[0] for row in OPERATION_ROWS if row[2] == owner],
        "error_contracts": ["typed refusal", "malformed/corrupt failure", "budget/cancellation", "unsupported capability"],
        "decision_refs": decisions,
        "requirement_refs": ["requirement.representation.capability"],
        "offer_refs": ["offer.representation.capability"],
        "configuration_contracts": ["editioned typed config; no stringly vendor switch"],
        "effect_intents": [] if kind in {"semantic_pure", "algorithm_pure", "policy_pure"} else ["allocate bounded buffers", "invoke qualified kernel", "read/write declared carrier"],
        "runtime_receipts": [] if kind in {"semantic_pure", "algorithm_pure", "policy_pure"} else ["bytes in/out", "work/time/memory", "provider/target/parameters", "loss/integrity result"],
        "laws": ["provider-name-independent public API", "unknown capabilities fail closed", "no undeclared information loss"],
        "oracles": ["round-trip", "cross-implementation", "malformed/adversarial", "resource bound"] + (["loss/error"] if lid == "library.san_loss_contract" else []),
        "resource_contracts": ["finite input", "finite output", "finite work", "peak memory", "cancellation"],
        "concurrency": ["Send/Sync posture explicit", "state is not shared unless contract permits"],
        "cancellation": ["cooperative safe point", "no apparently complete partial output"],
        "unsafe_ffi_generated_policy": ["unsafe/FFI confined to provider adapter", "safe wrapper validates lengths, alignment and lifetimes"],
        "dependencies": [],
        "targets": ["target-profile registry"],
        "compatibility": ["semantic edition independent from implementation version", "old decoders retained for governed historical artifacts"],
        "removal_seams": ["capability offer/requirement boundary", "differential conformance suite"],
        "forbidden_responsibilities": ["business semantic type ownership outside named context", "provider-name dispatch", "hidden defaults", "key management", "job scheduling"],
        "evidence_refs": ["src.arrow.security", "src.oci.descriptor"],
        "gaps": ["Crate split remains a candidate until ownership and cycle analysis across the global atlas."],
    }
    for lid, kind, owner, public_types, decisions in LIBRARY_ROWS
]


KERNEL_ROWS = [
    ("kernel.scalar.codec", "portable scalar encode/decode", ["rep.target.scalar_cpu"], ["operation.representation.encode", "operation.representation.decode"]),
    ("kernel.simd.bitpack", "SIMD bit pack/unpack", ["rep.target.simd_cpu"], ["operation.representation.pack_bits", "operation.representation.unpack_bits"]),
    ("kernel.simd.column_decode", "SIMD column decoding", ["rep.target.simd_cpu"], ["operation.representation.dictionary_decode", "operation.representation.delta_encode"]),
    ("kernel.cpu.chunk_compress", "multicore independent-chunk compression", ["rep.target.multicore_cpu"], ["operation.representation.compress"]),
    ("kernel.cpu.streaming_codec", "bounded-state streaming codec", ["rep.target.scalar_cpu", "rep.target.multicore_cpu"], ["operation.representation.stream_step"]),
    ("kernel.gpu.batch_decompress", "GPU batched decompression", ["rep.target.gpu"], ["operation.representation.decompress"]),
    ("kernel.gpu.device_decompress", "device-side fused copy/decompress", ["rep.target.gpu"], ["operation.representation.decompress"]),
    ("kernel.accelerator.deflate", "dedicated DEFLATE-compatible offload", ["rep.target.hardware_offload"], ["operation.representation.compress", "operation.representation.decompress"]),
    ("kernel.media.decode", "profile-qualified media decode", ["rep.target.scalar_cpu", "rep.target.gpu", "rep.target.hardware_offload"], ["operation.representation.decompress"]),
    ("kernel.integrity.checksum", "vectorized checksum", ["rep.target.scalar_cpu", "rep.target.simd_cpu", "rep.target.hardware_offload"], ["operation.representation.checksum", "operation.representation.verify_checksum"]),
    ("kernel.integrity.digest", "cryptographic digest", ["rep.target.scalar_cpu", "rep.target.simd_cpu", "rep.target.hardware_offload"], ["operation.representation.digest"]),
    ("kernel.protection.aead", "authenticated encryption/decryption", ["rep.target.scalar_cpu", "rep.target.hardware_offload"], ["operation.representation.encrypt_aead", "operation.representation.decrypt_aead"]),
    ("kernel.loss.verify", "decoded loss/error measurement", ["rep.target.scalar_cpu", "rep.target.simd_cpu", "rep.target.gpu"], ["operation.representation.verify_loss"]),
]


KERNELS = [
    {
        "kernel_id": kid,
        "edition": EDITION,
        "status": "candidate_contract",
        "name": name,
        "semantic_owner_ref": "bc.representation.kernel_contract",
        "target_profile_refs": targets,
        "operation_refs": operations,
        "ports": {"inputs": ["TypedBuffer<MemorySpace,Alignment,Representation>"], "outputs": ["TypedBuffer<MemorySpace,Alignment,Representation>", "KernelReceipt"], "errors": ["unsupported", "invalid_buffer", "budget", "cancelled", "device_fault"]},
        "required_capabilities": ["exact algorithm/profile", "input/output memory spaces", "alignment", "maximum sizes", "async and cancellation behavior"],
        "determinism": "same semantic/bit result required; byte determinism only when the profile requires canonical output",
        "fallback_contract": "fallback is a separately qualified offer selected by capability; silent target downgrade is forbidden",
        "qualification": ["reference oracle", "differential implementations", "boundary lengths", "unaligned/overlap cases", "malformed data", "resource exhaustion", "cancellation", "target-specific conformance"],
        "receipt_fields": ["kernel offer id/version", "target id", "parameters", "bytes in/out", "time/work", "fallback", "loss/integrity result"],
        "evidence_refs": ["src.nvidia.nvcomp", "src.intel.iaa", "src.arrow.security"],
        "llm_dependency": "none",
    }
    for kid, name, targets, operations in KERNEL_ROWS
]


QUALIFICATION = {
    "contract_id": "san.representation.library-provider-qualification",
    "edition": EDITION,
    "status": "active_research_contract",
    "separation": {
        "semantic_owner": "defines meaning, equality, loss and compatibility laws",
        "algorithm_library": "implements pure transformations and reference oracles",
        "runtime_mechanism": "manages bounded buffers, streams, cancellation and receipts",
        "provider_adapter": "maps a foreign API to canonical typed operations",
        "target_backend": "implements target-specific kernels without owning semantics",
        "provider_offer": "versioned observed capabilities and limits for one implementation/target/configuration",
    },
    "offer_required_fields": ["offer_id", "implementation_version", "algorithm_profile_editions", "encode_decode_modes", "loss_modes", "streaming", "splittability", "random_access", "dictionary", "integrity", "memory_spaces", "alignment", "thread_safety", "async", "cancellation", "maximum_input", "maximum_output", "worst_case_expansion", "targets", "licenses", "security_advisories", "evidence", "expiry"],
    "qualification_gates": [
        "parse and reject unsupported profiles without name heuristics",
        "golden vectors from the authoritative standard",
        "round-trip/property tests for every supported lossless profile",
        "loss/error oracle for every supported lossy profile and boundary",
        "cross-implementation encode/decode matrix with at least two independent implementations where available",
        "malformed, truncated, adversarial nesting, oversized declaration and decompression-bomb corpus",
        "stream fragmentation, flush, concatenation, restart and cancellation tests",
        "random-access/splittability/read-amplification proof when offered",
        "dictionary missing/wrong/version mismatch tests",
        "checksum/digest/protection scope and tamper tests",
        "thread, alias, alignment, overlap, FFI lifetime and memory-space tests",
        "finite CPU/GPU time, peak memory, output size and energy/throughput evidence on the exact target",
        "compatibility fixtures across claimed writer/reader editions",
        "license, patent posture, supply-chain provenance and current advisory review",
    ],
    "selection_law": ["filter by exact semantic and fidelity requirements", "filter by access and compatibility", "filter by security and resource constraints", "require unexpired qualification on target", "optimize declared objective", "retain rejected alternatives and emit binding receipt"],
    "forbidden": ["dispatch by crate/vendor/product name", "benchmark without corpus and target identity", "success boolean that erases partial/corrupt/unsupported states", "implicit lossy default", "fallback without receipt", "unsafe decoder before size/work guards"],
    "result_states": ["qualified", "qualified_with_scoped_limitations", "not_qualified", "evidence_expired", "unsupported_profile", "conformance_failure", "resource_failure", "security_blocked"],
}


INNOVATION_ROWS = [
    ("innovation.encoding.alp", 2024, "Adaptive lossless floating-point encoding combines decimal-to-integer and high-precision paths with SIMD-friendly encodings.", ["src.vldb.alp"], "Peer-reviewed artifact; superiority remains corpus and implementation dependent."),
    ("innovation.encoding.chimp", 2022, "Chimp improved streaming lossless floating-point coding over earlier XOR-window techniques.", ["src.vldb.chimp"], "Primary research evaluation; not a universal best codec."),
    ("innovation.encoding.elf", 2023, "Elf introduced provably reversible bit erasing to expose floating-point redundancy before XOR coding.", ["src.vldb.elf"], "Lossless under the paper's exact algorithm; production interoperability requires format governance."),
    ("innovation.encoding.btrblocks", 2023, "BtrBlocks demonstrated block-wise adaptive cascades for columnar data-lake compression.", ["src.sigmod.btrblocks"], "Research format and corpus; not an established interchange standard."),
    ("innovation.format.zarr3", 2024, "Zarr v3 separated array-to-bytes, bytes-to-bytes codecs and storage transformers with extension points.", ["src.zarr.v3", "src.zarr.sharding"], "Standard evolution; provider support and extension interoperability vary."),
    ("innovation.format.cog_standard", 2023, "OGC standardized Cloud Optimized GeoTIFF range-readable raster organization.", ["src.ogc.cog"], "Standardizes organization, not universal optimality for all raster workloads."),
    ("innovation.format.geoparquet", 2023, "GeoParquet stabilized interoperable geospatial vector metadata and geometry encodings over Parquet.", ["src.geoparquet.spec"], "Still evolving toward fuller OGC standardization; exact released version matters."),
    ("innovation.format.pmtiles3", 2023, "PMTiles v3 provided a compact range-readable single-file tile archive with hierarchical directories.", ["src.pmtiles.v3"], "Specialized for tiled geospatial delivery, not general table storage."),
    ("innovation.codec.flac_rfc", 2024, "FLAC gained an IETF standards-track bitstream specification and explicit streamable subset.", ["src.ietf.flac"], "Standardization of a mature codec rather than invention in 2024."),
    ("innovation.codec.png3", 2025, "PNG Third Edition integrated APNG, HDR/WCG metadata, updated integrity and security guidance.", ["src.w3c.png3"], "Evolution of an established lossless format."),
    ("innovation.codec.jpegxl", 2021, "JPEG XL standardized modern lossless/lossy/progressive image coding and reversible legacy-JPEG reconstruction.", ["src.jpeg.jpegxl"], "Deployment support and exact ISO edition must be separately qualified."),
    ("innovation.codec.av2", 2026, "AOMedia published AV2 1.0 and reference software as a new open video bitstream generation.", ["src.aom.av2"], "Very new; hardware, independent decoder and production maturity evidence remains limited."),
    ("innovation.hardware.gdeflate", 2022, "GDeflate reorganized DEFLATE-derived symbols into parallel substreams for GPU decompression.", ["src.microsoft.gdeflate"], "Different stream format; interoperability and target support must be probed."),
    ("innovation.hardware.intel_iaa", 2023, "Intel IAA productized integrated compression/decompression and analytic primitive offload.", ["src.intel.iaa"], "Hardware-specific availability and supported profile subsets require runtime qualification."),
    ("innovation.hardware.nvcomp", 2025, "nvCOMP expanded device-side and hardware-engine paths for standard and GPU-oriented codecs.", ["src.nvidia.nvcomp"], "Official capability claims; benchmark and portability claims need independent evidence."),
    ("innovation.format.lance", 2023, "Lance decoupled per-column large pages from row groups to target cloud random-access workloads.", ["src.lance.format"], "Format-specific trade-offs; table and search semantics live above the file layer."),
    ("innovation.format.nimble", 2024, "Nimble explored cascading encodings and lighter metadata for extremely wide tables.", ["src.meta.nimble"], "Project explicitly disclaims stability and encourages one library, so it is research evidence, not a neutral standard."),
    ("innovation.format.vortex", 2025, "Vortex introduced editioned extensible compressed-array components across memory, disk and IPC.", ["src.vortex.editions", "src.vortex.project"], "New ecosystem; claims require independent, workload-specific qualification."),
    ("innovation.format.f3", 2025, "F3 proposed an open next-generation columnar format and evaluated metadata/layout choices across wide data.", ["src.sigmod.f3"], "Primary research; adoption and independent implementation evidence are immature."),
    ("innovation.integrity.http_digest", 2024, "RFC 9530 separated digest of message content from digest of selected representation.", ["src.ietf.digest"], "Protocol semantics, not a new hash function."),
]


INNOVATIONS = [
    {
        "innovation_id": iid,
        "edition": EDITION,
        "year": year,
        "status": "evidence_backed_candidate",
        "non_llm": True,
        "problem_and_innovation": description,
        "evidence_refs": evidence,
        "evidence_posture": "primary standard, official implementation contract, or primary research as named in evidence",
        "limits": limits,
        "compiler_implications": ["register capability/edition rather than product-name branch", "require exact target and conformance evidence", "retain maturity limitation"],
    }
    for iid, year, description, evidence, limits in INNOVATION_ROWS
]


GAP_ROWS = [
    ("gap.representation.global_context_adjudication", "blocking", "Context ownership overlaps storage, data-shape, security, runtime and compiler domains and is not globally adjudicated."),
    ("gap.representation.semantic_type_bindings", "blocking", "Representation candidates are not yet bound to the full semantic data-type universe with equality and invalid-inference proofs."),
    ("gap.representation.format_conformance_vectors", "blocking", "Many standards lack normalized, locally executable cross-implementation conformance-vector manifests."),
    ("gap.representation.provider_offers", "blocking", "Concrete library/provider/version/target offers and evidence expiry are not yet populated."),
    ("gap.representation.two_implementations", "blocking", "Two independent implementation evidence is not established for every claimed format/profile."),
    ("gap.representation.vertical_bindings", "blocking", "Each capability needs at least two unrelated vertical analytical bindings."),
    ("gap.representation.loss_observables", "blocking", "Vertical packs must specify protected downstream observables for lossy media/scientific compression."),
    ("gap.representation.dictionary_registry", "major", "Dictionary artifact identity, distribution, retention and disaster-recovery contracts need integration with artifact registries."),
    ("gap.representation.content_defined_chunking", "major", "Rabin/FastCDC-style chunking algorithms need direct primary-source records and adversarial boundary qualification."),
    ("gap.representation.specialized_codecs", "major", "Coverage remains incomplete for seismic, astronomy, microscopy, CAD, telemetry, graph and domain-specific industrial codecs."),
    ("gap.representation.media_profiles", "major", "AVC/HEVC/VVC/AAC/WebP/JPEG 2000 profiles and patent/licensing postures need exact standard-edition records."),
    ("gap.representation.geospatial_pointcloud", "major", "LAZ/COPC, 3D Tiles and additional raster/vector formats need primary specification and access-contract records."),
    ("gap.representation.genomics", "major", "CRAM preservation maps, external references and controlled-loss fields need deep per-version modeling."),
    ("gap.representation.crypto_agility", "major", "Protection envelopes need binding to the global key-management, authority and cryptographic-agility contexts."),
    ("gap.representation.side_channels", "major", "Compressed-size, timing, pruning metadata and encrypted-footer leakage policies are not fully modeled."),
    ("gap.representation.bomb_corpus", "major", "A shared decompression-bomb, recursion, integer-overflow and pathological-input corpus is not yet assembled."),
    ("gap.representation.energy_model", "major", "Energy and carbon measurements are named but lack cross-target measurement protocols."),
    ("gap.representation.compatibility_matrix", "major", "Historical writer/reader matrices and upcasters are incomplete across all editions."),
    ("gap.representation.rust_types", "major", "Rust typestates, traits, error algebra and no_std/wasm/FFI surfaces await global ownership and crate-cycle adjudication."),
    ("gap.representation.product_boundaries", "deferred", "No product or suite boundary may be derived until contexts, capabilities, providers and cross-domain dependencies are adjudicated."),
]


GAPS = [
    {
        "gap_id": gid,
        "edition": EDITION,
        "severity": severity,
        "status": "open",
        "description": description,
        "owner_candidate": "bc.representation.provider_qualification" if "provider" in gid or "implementation" in gid else "bc.representation.compression_selection",
        "closure_evidence_required": ["machine-readable records", "authoritative evidence", "validator gate", "independent review"],
        "compiler_behavior_until_closed": "emit typed compiler gap and refuse any binding that depends on the missing proof",
    }
    for gid, severity, description in GAP_ROWS
]

GAP_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://san.example/spec/representation-gap-v1.schema.json",
    "type": "object", "additionalProperties": False,
    "required": ["gap_id", "edition", "severity", "status", "description", "owner_candidate", "closure_evidence_required", "compiler_behavior_until_closed"],
    "properties": {
        "gap_id": {"type": "string", "minLength": 1}, "edition": {"type": "integer", "minimum": 1},
        "severity": {"enum": ["blocking", "major", "deferred"]}, "status": {"const": "open"},
        "description": {"type": "string", "minLength": 1}, "owner_candidate": {"type": "string", "minLength": 1},
        "closure_evidence_required": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "compiler_behavior_until_closed": {"type": "string", "minLength": 1},
    },
}


MANIFEST = {
    "corpus_id": "san.domain-atlas.encoding-compression",
    "edition": EDITION,
    "status": "candidate_open_world",
    "generated_at": ACCESSED,
    "completion_claim": False,
    "forbidden_core_dependencies": ["llm", "large_language_model", "prompt", "rag", "agent_memory", "generative_model"],
    "counts": {
        "sources": len(SOURCES),
        "axes": len(AXES["axes"]),
        "contexts": len(CONTEXTS),
        "representations": len(REPRESENTATIONS),
        "operations": len(OPERATIONS),
        "decision_points": len(DECISIONS),
        "compiler_mappings": len(COMPILER_MAPPINGS),
        "library_candidates": len(LIBRARIES),
        "kernel_contracts": len(KERNELS),
        "innovations": len(INNOVATIONS),
        "gaps": len(GAPS),
    },
    "laws": [
        "layers remain distinct even when packaged together",
        "unknown meaning or capability is a typed gap",
        "every lossy method exposes error, bound, scope, approval and verification",
        "provider selection uses capabilities and evidence, never names",
        "a checksum is not authenticity; a digest is not business identity; encryption is not authorization",
        "format detection cannot infer semantic type",
        "all decoders execute under finite input, output, nesting, memory and work budgets",
        "historical decodability and evidence survive migrations",
    ],
}


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    write_json("manifest.json", MANIFEST)
    write_json("axes.json", AXES)
    write_jsonl("sources.jsonl", SOURCES)
    write_jsonl("bounded-context-candidates.jsonl", CONTEXTS)
    write_jsonl("format-layout-codec-records.jsonl", REPRESENTATIONS)
    write_jsonl("typed-operations.jsonl", OPERATIONS)
    write_jsonl("decision-points.jsonl", DECISIONS)
    write_jsonl("compiler-mappings.jsonl", COMPILER_MAPPINGS)
    write_jsonl("library-candidates.jsonl", LIBRARIES)
    write_jsonl("kernel-contracts.jsonl", KERNELS)
    write_json("library-provider-qualification.json", QUALIFICATION)
    write_jsonl("innovations.jsonl", INNOVATIONS)
    write_jsonl("gaps.jsonl", GAPS)
    write_json("gap.schema.json", GAP_SCHEMA)
    print(json.dumps(MANIFEST["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
