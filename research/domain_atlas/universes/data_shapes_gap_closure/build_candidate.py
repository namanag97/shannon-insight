#!/usr/bin/env python3
"""Build the non-canonical data-shape gap-closure candidate bundle.

The generator intentionally consumes the independent audit and canonical candidate as
read-only evidence.  It never edits either input and never upgrades a proposal into a
canonical fact.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
UNIVERSES = HERE.parent
AUDIT = UNIVERSES / "data_modality_gap_audit"
CANONICAL = UNIVERSES / "data_shapes"
ACCESSED = "2026-08-25"


def slug(value: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in value).split())


def dump_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def dump_jsonl(path: Path, records: list[dict]) -> None:
    records = sorted(records, key=lambda r: next((str(r[k]) for k in r if k.endswith("_id")), json.dumps(r, sort_keys=True)))
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


# id, label, cluster, canonical relation, canonical target, representation, evidence,
# identity law, time law, order law, topology law, change law, uncertainty law,
# security law, three domain operations, invalid inference
FAMILIES = [
    ("smtp_envelope", "SMTP transaction envelope", "mail_calendar", "proposed_new_shape", None, "RFC 5321/6531 command transaction", ["A-SRC-149", "GAP-SRC-001"], "transaction identity is session plus MAIL transaction boundary, not Message-ID", "command sequencing and retry time are transport time, not message authored time", "MAIL precedes RCPT set precedes DATA; recipient order is not delivery authority", "one reverse-path to a possibly empty ordered command history and recipient multiset", "each retry is a new delivery attempt linked to the same or revised message", "acceptance is not final delivery and enhanced status may remain unknown", "reverse-path/header From/verified author are distinct; recipient disclosure is sensitive", ["validate_command_sequence", "normalize_envelope_address", "correlate_delivery_attempt"], "SMTP reverse-path equals RFC 5322 From"),
    ("internet_message_graph", "Internet message and MIME entity graph", "mail_calendar", "proposed_specialization_of", "shape.internet_message", "RFC 5322 plus MIME entity tree", ["A-SRC-071", "A-SRC-072", "A-SRC-073"], "Message-ID is optional and not globally trustworthy; MIME Content-ID has part scope", "Date is an asserted header time, Received fields form transport observations", "header occurrence order and MIME child order may be significant", "header multimap plus recursive multipart/message body graph", "forwarding, resent fields and content transfer transformations create related editions", "missing headers and malformed MIME require explicit recovery profile", "active content, spoofed headers and attachment media types are untrusted", ["parse_message_graph", "decode_transfer_encoding", "extract_attachment_manifest"], "A parseable From header proves authenticated sender"),
    ("mailbox_archive", "Mailbox archive and message occurrence collection", "mail_calendar", "proposed_specialization_of", "shape.mailbox_collection", "mbox or provider export profile", ["A-SRC-074", "A-SRC-071"], "message occurrence identity is mailbox/provider scoped and differs from content digest", "internal date, received time and header date remain separate", "file order is not conversation order or delivery order", "framed message sequence with mailbox labels/folders external to mbox", "moves, label changes, deduplication and expunge are occurrence changes", "duplicate content may be distinct deliveries", "mailbox ACL, legal hold, deleted state and authentication evidence must be preserved", ["frame_mbox", "deduplicate_occurrences", "reconstruct_thread_candidates"], "Equal Message-ID or bytes proves one mailbox occurrence"),
    ("calendar_object", "Calendar object with recurrence and participants", "mail_calendar", "proposed_new_shape", None, "iCalendar/iTIP/jCal/JSCalendar profile", ["A-SRC-150", "GAP-SRC-002", "GAP-SRC-003"], "UID plus recurrence-id and sequence edition identify occurrences and revisions", "floating/local/zoned/date values, recurrence, duration and availability are distinct", "component property order is generally not event order; recurrence expansion uses calendar rules", "calendar contains components, properties, parameters and recurrence overrides", "SEQUENCE, DTSTAMP, recurrence exceptions and scheduling methods govern change", "future timezone rules and attendee state can be unresolved", "organizer authority, attendee privacy and scheduling injection require policy", ["expand_recurrence", "merge_calendar_revision", "resolve_local_time"], "A DTSTART lexical value always identifies one UTC instant"),
    ("frequency_spectrum", "Frequency-domain spectrum", "signal_media", "proposed_specialization_of", "shape.ordered_series", "complex or magnitude frequency-bin array", ["A-DSS-045", "GAP-SRC-004"], "spectrum identity includes source signal/segment and transform profile", "window/segment time is provenance; bins are frequency coordinates", "bin order follows signed/one-sided frequency convention", "frequency coordinate mapped to complex, magnitude, power or density values", "re-windowing, averaging and calibration create derived spectra", "noise floor, leakage, estimator variance and confidence are explicit", "sensitive signal content and calibration metadata inherit source controls", ["estimate_spectrum", "convert_spectral_density", "inverse_transform_if_complete"], "Magnitude spectrum alone permits exact waveform reconstruction"),
    ("deep_image", "Variable-sample deep image", "signal_media", "proposed_specialization_of", "shape.multichannel_image", "OpenEXR multipart deep-sample representation", ["A-SRC-086"], "part/view/channel/pixel/sample identity is explicit", "shutter and frame time are asset metadata, not per-sample unless declared", "samples at a pixel are depth ordered only under a declared profile", "2-D pixel grid with a variable-length sample list per pixel and named channels", "flattening/compositing creates a lossy derived image", "coverage/opacity and depth uncertainty may be per sample", "render layers and hidden object identifiers may be sensitive", ["validate_deep_samples", "composite_depth_samples", "flatten_to_raster"], "One color/depth value per pixel preserves a deep image"),
    ("caption_track", "Timed text caption/subtitle track", "signal_media", "proposed_new_shape", None, "WebVTT/TTML-like cue sequence", ["A-SRC-091", "GAP-SRC-005"], "track and cue identifiers have document/profile scope", "cue intervals use media timeline with explicit time base", "cue file order may resolve overlaps but does not prove spoken order", "timed cues with payload, regions, styling and metadata", "retiming, translation, correction and segmentation produce track editions", "speaker attribution, language and accessibility completeness may be unknown", "captions can reveal sensitive speech; style markup is untrusted input", ["validate_cue_timeline", "retime_track", "merge_caption_tracks"], "Cue presence proves transcription completeness or language correctness"),
    ("musical_event_sequence", "Symbolic musical-event sequence", "signal_media", "proposed_new_shape", None, "MIDI event stream/file profile", ["A-SRC-151", "GAP-SRC-006"], "track/channel/note occurrence identity differs from pitch equality", "ticks require tempo map and time division to map to elapsed time", "same-tick event order and running status are profile-sensitive", "tracks containing channel, meta and system events over musical time", "quantization, tempo edits and expressive controller edits are revisions", "velocity and controller values are performance instructions, not acoustic certainty", "SysEx and embedded metadata require trust and size controls", ["resolve_musical_time", "pair_note_events", "render_event_sequence"], "MIDI notes are interchangeable with decoded audio samples"),
    ("city_model", "Semantic 3D city model", "geo_catalog", "proposed_new_shape", None, "CityGML conceptual/encoding profile", ["A-SRC-097"], "city object identity is namespace/version scoped and separate from surface IDs", "validity, construction history and observation time are independently qualified", "feature/member order has no default spatial meaning", "typed city-object graph with geometry, topology, appearances and relations", "versions, dynamizers and lifecycle events must be explicit", "LoD and incomplete geometry are not measurement confidence", "addresses, interiors and infrastructure attributes can be sensitive", ["validate_city_topology", "select_level_of_detail", "derive_render_mesh"], "A rendered 3-D mesh preserves city-object classes and relations"),
    ("stac_catalog", "Spatiotemporal asset catalog graph", "geo_catalog", "proposed_specialization_of", "shape.dataset_manifest", "STAC Catalog/Collection/Item plus extensions", ["A-SRC-099"], "stable linkable IDs are scoped by catalog/collection and provider policy", "item datetime, interval, created/updated and asset observation times differ", "link-array order is not traversal or temporal order", "linked catalog/collection/item graph with asset and extension metadata", "catalog links, extension editions and asset versions evolve independently", "bbox/footprint/cloud-cover metadata may be approximate or absent", "links can expose signed URLs, locations and restricted asset metadata", ["traverse_catalog", "validate_extension_profile", "resolve_asset_occurrence"], "Catalog metadata proves referenced asset availability, quality or semantic comparability"),
    ("feature_table", "Geospatial feature table", "geo_catalog", "proposed_specialization_of", "shape.feature_collection", "GeoParquet/GeoArrow binding", ["A-SRC-100", "A-SRC-101"], "feature/row identity requires explicit key; geometry bytes are not feature identity", "feature valid/recorded/observation time roles are declared columns", "row order has no spatial or feature semantics by default", "relation of feature records with one or more CRS-qualified geometry columns", "upserts and geometry revisions require identity and edition policy", "empty/null/invalid geometry and coordinate precision are distinct states", "geometry can be sensitive; CRS and precision reduction do not anonymize", ["validate_geometry_column", "transform_crs", "spatial_filter"], "GeoParquet file identity or row number supplies stable feature identity"),
    ("hdf5_group_graph", "HDF5 linked group/dataset graph", "scientific_imaging", "proposed_new_shape", None, "HDF5 abstract data model and file representation", ["A-DSS-014"], "object tokens, links and paths have different identity and lifetime", "time is domain metadata unless a convention binds a dimension", "group member iteration order is profile dependent unless tracked", "directed link graph of groups, datasets, committed datatypes and attributes", "SWMR/versioning and link mutation are storage changes, not domain change by default", "fill values, missing chunks and domain uncertainty differ", "external links, filters, user blocks and object references cross trust boundaries", ["traverse_hdf5_graph", "resolve_links", "materialize_dataset_slice"], "An HDF5 file is one tensor or group path is permanent object identity"),
    ("netcdf_dataset", "netCDF named-dimension scientific dataset", "scientific_imaging", "proposed_specialization_of", "shape.labeled_array", "netCDF enhanced/classic model plus CF profile", ["A-DSS-015", "A-DSS-017"], "group/variable/dimension names are scoped and coordinate identity is convention-bound", "calendar, time units, bounds and climatological time require CF interpretation", "dimension order affects storage/API but coordinate order has semantic constraints", "groups, dimensions, variables, attributes and coordinate systems", "append/unlimited dimensions and revised metadata have separate change laws", "fill/missing/valid range, QC flags and measurement uncertainty differ", "locations and environmental variables may have access classifications", ["resolve_coordinate_system", "subset_named_dimensions", "decode_cf_time"], "N-D extents alone establish axes, units, calendar or cell methods"),
    ("fits_hdu_list", "FITS ordered heterogeneous HDU list", "scientific_imaging", "proposed_new_shape", None, "FITS 4.x header/data units", ["A-SRC-093"], "HDU index/name/version identity differs; card occurrences can repeat", "time keywords require specific conventions and time scales", "HDU and header-card order is representation-significant", "primary HDU followed by heterogeneous image/table extension HDUs", "append/update may rewrite checksums and header/data units", "undefined pixels, null table cells and measurement error use separate conventions", "checksums prove transport integrity, not authenticity or access authority", ["parse_hdu_sequence", "select_hdu", "verify_fits_checksum"], "A FITS file is one image or table"),
    ("dicom_study_graph", "DICOM patient-study-series-instance graph", "scientific_imaging", "proposed_new_shape", None, "DICOM information object and transfer-syntax profiles", ["A-DSS-041", "GAP-SRC-007"], "Patient/Study/Series/SOP Instance UIDs have distinct scopes and correction rules", "study, series, acquisition, content and instance creation times remain distinct", "instance number and file order do not establish acquisition order without profile", "clinical entity graph linked to instances, frames, segments, waveforms and reports", "correction, de-identification, derived instances and replacement require provenance", "pixel value, segmentation label, measurement and diagnostic confidence differ", "PHI, burned-in annotations, private tags and UID linkage require governed handling", ["assemble_study_graph", "decode_transfer_syntax", "deidentify_profiled"], "Pixel bytes or filename identify the clinical study and patient context"),
    ("boundary_representation", "Exact boundary-representation solid", "engineering_models", "proposed_specialization_of", "shape.mesh", "STEP geometric/topological representation", ["A-SRC-104", "GAP-SRC-008"], "solid/shell/face/edge/vertex and persistent design IDs are distinct", "design edition and validity differ from manufacturing observation time", "orientation of loops/shells is topological, not arbitrary list order", "oriented topology bounding exact or approximated geometric surfaces", "feature edits and topology naming changes require correspondence/provenance", "tolerances and geometric approximation error are explicit", "export may expose design IP, hidden layers and product identifiers", ["validate_watertight_solid", "classify_point_in_solid", "tessellate_with_tolerance"], "Triangle mesh equality proves exact B-rep or design-feature equality"),
    ("scene_graph", "Runtime 3-D scene graph", "engineering_models", "proposed_new_shape", None, "node hierarchy with transforms, meshes, materials and animation", ["A-SRC-102"], "node/mesh/material/accessor identity is asset-local unless externally named", "animation samplers use declared timeline; asset creation time is separate", "child order may affect traversal but not product assembly semantics", "directed node graph instancing geometry/material/camera/animation assets", "animation and extension edits create asset editions", "quantization, LOD and compressed geometry introduce declared approximation", "external URIs, scripts/extensions and embedded metadata require policy", ["resolve_world_transforms", "instantiate_scene", "evaluate_animation"], "Scene hierarchy proves engineering bill-of-materials or containment authority"),
    ("gltf_asset", "glTF runtime delivery asset", "engineering_models", "proposed_representation_binding_to", "candidate.shape.scene_graph", "glTF 2.0 JSON/GLB plus registered extensions", ["A-SRC-102"], "indices and URIs are representation-local; names are not stable IDs", "animation input accessors define asset-local time", "array index order is representation binding and extension dependent", "container joining scene graph, buffers, accessors, images and extensions", "extension/version changes can alter interpretation without domain revision", "quantization and mesh compression require error/profile declarations", "external resources, extensions and images cross origin/trust boundaries", ["validate_gltf_profile", "resolve_asset_references", "transcode_mesh_extension"], "glTF conformance implies CAD/BIM semantics or manufacturable geometry"),
    ("cad_product_model", "Managed model-based CAD product definition", "engineering_models", "proposed_new_shape", None, "STEP AP242 application protocol", ["A-SRC-104"], "product/version/definition/shape/PMI identities and effectivity scopes differ", "configuration effectivity and design release time are separate", "assembly occurrence order is not product structure authority", "product structure plus exact geometry, PMI, validation properties and configuration", "revisions, alternatives and change notices preserve configuration lineage", "geometric tolerances and validation properties bound fidelity", "export-control, proprietary design and supplier partitions are security qualifiers", ["resolve_product_configuration", "validate_shape_representation", "compare_product_editions"], "Geometry-only exchange preserves product structure, PMI and design intent"),
    ("bim_facility_model", "BIM facility and infrastructure information model", "engineering_models", "proposed_new_shape", None, "IFC schema/model-view/serialization profile", ["A-SRC-103"], "GlobalId and object occurrence/type identities have profile/lifecycle constraints", "construction phase, asset validity and model record time are distinct", "spatial containment and decomposition are relations, not file order", "typed object graph with spatial structure, systems, geometry, properties and documents", "model federation, issue resolution and asset handover create editions", "geometry placement, quantities and property values may carry tolerance/quality", "facility security, occupant data and sensitive system topology require filtering", ["validate_ifc_graph", "federate_models", "extract_model_view"], "IFC file parsing proves conformance to a model view or complete asset information"),
    ("biological_sequence", "Reference-qualified biological sequence", "genomics", "proposed_new_shape", None, "FASTA/GA4GH sequence representation", ["A-SRC-111", "A-SRC-112"], "sequence digest/accession/assembly/contig identity and version are distinct", "sample collection and reference release times are separate metadata", "base order and strand/orientation are semantic", "alphabet-qualified ordered residues with optional reference/region context", "correction, normalization and reference version changes create new assertions", "ambiguous bases and base quality are distinct", "genomic sequence may be identifying and access-controlled", ["validate_alphabet", "reverse_complement", "slice_reference_region"], "A text string of bases identifies reference assembly, strand and sample"),
    ("sequence_read_set", "Sequencing read collection", "genomics", "proposed_new_shape", None, "FASTQ/read group profile", ["A-SRC-111", "GAP-SRC-009"], "read name is run/tool scoped; read-pair and read-group identity are explicit", "run/cycle/sample collection times are distinct", "base and quality order are coupled; collection order is not genomic order", "reads with bases, per-base quality, pairing and run/sample metadata", "trimming, correction, deduplication and consensus derive new read sets", "quality scores are model/profile dependent, not probabilities without calibration", "raw reads are highly identifying and may contain contaminants", ["validate_read_quality", "pair_reads", "trim_with_provenance"], "Read name is globally unique or quality character has universal probability meaning"),
    ("sequence_alignment", "Reference-qualified sequence alignment set", "genomics", "proposed_new_shape", None, "SAM/BAM/CRAM alignment model", ["A-SRC-111"], "read/alignment/reference IDs and primary/secondary/supplementary status differ", "sample/run time is metadata; reference coordinate is not time", "coordinate sort, query-name sort and file order are declared separately", "alignment records relating query sequence to versioned reference coordinates", "realignment, duplicate marking and recalibration create derived editions", "mapping/base quality and alignment ambiguity are separate", "alignments retain identifying variants and reference access dependencies", ["validate_cigar", "sort_alignments", "project_reference_coordinates"], "Coordinate and CIGAR are meaningful without reference edition and coordinate convention"),
    ("variant_set", "Normalized genomic variant assertion set", "genomics", "proposed_new_shape", None, "VCF/BCF and GA4GH VRS profile", ["A-SRC-111", "A-SRC-112"], "variant identity depends on reference context and normalization; record ID is not identity", "observation, call, interpretation and database release times differ", "file coordinate order does not imply haplotype phase", "variant loci/alleles plus sample calls, annotations and filters", "normalization, left alignment, liftover and reinterpretation create derived assertions", "genotype likelihood, quality, filter and clinical significance are distinct", "variants and sample identifiers are sensitive genomic data", ["normalize_variant", "compare_vrs_identity", "liftover_variant"], "Equal CHROM/POS/REF/ALT strings across assemblies identify the same biological variation"),
    ("genotype_haplotype", "Genotype and phased haplotype assertion", "genomics", "proposed_new_shape", None, "VCF/VRS genotype-haplotype profile", ["A-SRC-111", "A-SRC-112"], "sample, allele, locus, ploidy and phase-set identities are explicit", "call time, specimen time and validity time differ", "allele order is meaningful only under phased/ploidy profile", "allele copies and phase relations over loci for one subject/specimen", "re-calling, phasing and reference changes produce revised assertions", "likelihood/posterior and no-call/partial-call states are explicit", "genotype is sensitive identity/health data", ["validate_ploidy", "phase_haplotype", "merge_call_sets"], "Unphased genotype supplies haplotype or phase"),
    ("phenopacket", "Computable phenotype packet", "genomics", "proposed_new_shape", None, "GA4GH Phenopackets schema/profile", ["A-SRC-113"], "subject/biosample/phenotypic feature/disease IDs and ontology editions differ", "onset, observation, procedure and packet record times remain typed", "feature list order does not imply chronology or importance", "subject-centered graph of phenotypes, diseases, measurements, biosamples and interpretations", "new observations and ontology mappings create packet editions", "excluded, unknown, onset-range and evidence confidence are explicit", "rare phenotype combinations are identifying health data", ["validate_ontology_terms", "merge_packet_editions", "derive_case_feature_set"], "Phenotype code proves diagnosis, causal variant or current presence"),
    ("genomic_report", "Structured clinical genomic report", "genomics", "proposed_new_shape", None, "FHIR Genomics Reporting profile", ["A-SRC-114", "A-SRC-115"], "report/observation/specimen/patient/test and variant identities are distinct", "issued, effective, specimen and interpretation times remain distinct", "result list order is not clinical priority unless profiled", "diagnostic report graph linking studies, findings, interpretations and recommendations", "amendment, correction, reclassification and withdrawal are lifecycle states", "analytical validity, pathogenicity, evidence and recommendation confidence differ", "clinical authority, consent, secondary findings and access are governed", ["validate_report_profile", "assemble_finding_graph", "apply_report_amendment"], "A variant observation itself is a diagnosis or authorized recommendation"),
    ("order_book", "Limit-order-book state and event history", "finance_metadata", "proposed_new_shape", None, "FIX market-data/order-entry profile", ["A-SRC-118", "GAP-SRC-010"], "venue/instrument/session/order/quote/price-level identities and replacement chains differ", "exchange event, sending, receive and processing times remain distinct", "sequence number and price-time priority are venue/profile governed", "order-level or price-level bid/ask state plus incremental event stream", "add/modify/cancel/execute/reset/correct transitions reconstruct state", "hidden liquidity, implied orders, packet loss and stale state are explicit uncertainty", "market data entitlements, participant IDs and trading controls are governed", ["reconstruct_book", "validate_sequence_gap", "compute_depth_snapshot"], "A price-level snapshot proves order-level queue priority or executable liquidity"),
    ("catalog_record", "Governed dataset catalog record", "finance_metadata", "proposed_specialization_of", "shape.dataset_manifest", "DCAT/Dublin Core/profiled metadata graph", ["A-SRC-133", "A-SRC-134"], "catalog/dataset/distribution/service/record identities and editions differ", "issued, modified, temporal coverage and source validity times differ", "catalog listing/link order has no ranking semantics by default", "metadata graph describing assets, distributions, services, provenance and access", "supersession, tombstone, deprecation and refresh are catalog lifecycle events", "completeness, freshness, quality and certification are separate claims", "discoverability, authorization, license and actual access are distinct", ["validate_catalog_profile", "resolve_distribution", "merge_metadata_assertions"], "Catalog presence proves access, freshness, fitness or certified quality"),
    ("protected_content_envelope", "Protected content envelope", "security_interchange", "proposed_new_shape", None, "CMS or COSE content-protection profile", ["A-SRC-126", "A-SRC-127"], "content, signer/key, recipient and envelope identities are separate", "signing, countersigning, certificate validity and receipt times differ", "signer/recipient list order is not authority precedence", "typed protected headers plus payload/reference, signatures/MAC/encryption recipients", "re-encryption, countersignature and algorithm migration create new envelopes", "cryptographic verification outcome is not semantic truth confidence", "critical headers, algorithm policy, key purpose and detached-content binding are mandatory", ["verify_protected_envelope", "decrypt_for_recipient", "transcode_protected_payload"], "CMS and COSE bytes or successful signature prove payload truth and authorization"),
    ("fhir_resource_graph", "Profiled FHIR resource graph", "clinical_interchange", "proposed_specialization_of", "shape.schema_bound_message", "FHIR R5 JSON/XML/RDF with implementation-guide profiles", ["A-SRC-114"], "logical id, version id, canonical URL, business identifier and reference identity differ", "resource meta time, clinical effective time and recorded time remain distinct", "array order is meaningful only for elements defined as ordered", "resources linked by typed references, contained resources and bundles", "create/update/history, amendment and clinical status follow resource/profile laws", "data absent reason, uncertainty extensions and clinical interpretation differ", "security labels, compartments, consent and purpose-of-use are external governance", ["validate_fhir_profile", "resolve_fhir_references", "compare_resource_versions"], "FHIR schema validity proves clinical validity, authorization or profile conformance"),
    ("financial_business_message", "Financial business message and transaction choreography", "finance_interchange", "proposed_specialization_of", "shape.schema_bound_message", "ISO 20022 message definition and market-practice profile", ["A-SRC-117"], "business message, instruction, transaction, account, party and UETR identities differ", "creation, settlement, value, acceptance and status times remain typed", "XML element order differs from business transaction sequence", "typed business message with header, parties, accounts, transactions and status", "replacement, cancellation, return, investigation and status transitions are explicit", "acceptance status does not prove settlement finality", "party/account data, signatures and market-practice authority require governance", ["validate_market_practice", "correlate_transaction_status", "apply_message_choreography"], "ISO 20022 schema-valid message is accepted, settled or semantically complete"),
    ("fix_message_stream", "FIX session and application message stream", "finance_interchange", "proposed_new_shape", None, "FIX tag-value/binary session profile", ["A-SRC-118"], "session, sequence, order, execution and trade IDs have distinct scopes", "SendingTime, transact time and venue event time differ", "MsgSeqNum orders a session but does not establish market causality across sessions", "session-control and application messages with repeating groups and dictionaries", "resend, gap fill, sequence reset, cancel/replace and correction alter interpretation", "poss dup, stale book and business reject states are explicit", "session credentials, entitlements and counterparty IDs are governed", ["parse_fix_dictionary", "reconcile_session_sequence", "correlate_order_lifecycle"], "FIX session order supplies total event order across venues or business finality"),
]


EXTRA_SOURCES = [
    ("GAP-SRC-001", "SMTP Extension for Internationalized Email", "IETF", "https://www.rfc-editor.org/rfc/rfc6531.html", "RFC 6531", "internationalized SMTP envelope"),
    ("GAP-SRC-002", "jCal: The JSON Format for iCalendar", "IETF", "https://www.rfc-editor.org/rfc/rfc7265.html", "RFC 7265", "calendar representation crosswalk"),
    ("GAP-SRC-003", "JSCalendar: A JSON Representation of Calendar Data", "IETF", "https://www.rfc-editor.org/rfc/rfc8984.html", "RFC 8984", "calendar semantic representation"),
    ("GAP-SRC-004", "IEEE Standard Definitions of Physical Quantities for Fundamental Frequency and Time Metadata", "IEEE", "https://standards.ieee.org/ieee/269/8209/", "official standard page", "frequency-domain qualifier evidence"),
    ("GAP-SRC-005", "Timed Text Markup Language 2", "W3C", "https://www.w3.org/TR/ttml2/", "W3C Recommendation", "timed text semantics"),
    ("GAP-SRC-006", "MIDI 2.0 Specifications", "MIDI Association", "https://midi.org/midi-2-0-specifications", "official specification portal", "symbolic musical events"),
    ("GAP-SRC-007", "DICOM Standard", "NEMA / Medical Imaging & Technology Alliance", "https://www.dicomstandard.org/current", "current edition portal", "DICOM information model and transfer syntaxes"),
    ("GAP-SRC-008", "STEPmod AP242 module repository", "ISO TC184/SC4", "https://www.mbx-if.org/home/mbx/ap242-scope/", "official ecosystem scope", "AP242 product model"),
    ("GAP-SRC-009", "FASTQ format", "NCBI", "https://www.ncbi.nlm.nih.gov/sra/docs/submitformats/", "official submission format documentation", "sequencing reads and qualities"),
    ("GAP-SRC-010", "FIX Simple Binary Encoding", "FIX Trading Community", "https://www.fixtrading.org/standards/sbe-online/", "official online specification", "market data message representation"),
]


CROSSWALKS = [
    ("smtp_rfc5321", "SMTP RFC 5321", "candidate.shape.smtp_envelope", "transport_protocol_binding", "conditional", ["envelope paths", "SMTPUTF8 profile", "command transaction"], ["header identity", "authenticated author", "mailbox occurrence"], ["A-SRC-149", "GAP-SRC-001"]),
    ("icalendar_rfc5545", "iCalendar RFC 5545", "candidate.shape.calendar_object", "serialization_profile", "conditional", ["components", "properties", "recurrence syntax"], ["resolved timezone future rules", "enterprise participant authority"], ["A-SRC-150"]),
    ("jscalendar", "JSCalendar RFC 8984", "candidate.shape.calendar_object", "semantic_representation_profile", "partial", ["calendar object fields", "typed JSON values"], ["all iCalendar extension round trips", "provider-specific scheduling state"], ["GAP-SRC-003"]),
    ("geoparquet", "GeoParquet 1.1", "candidate.shape.feature_table", "physical_layout_binding", "conditional", ["geometry columns", "CRS metadata", "bbox metadata"], ["feature identity", "validity time", "topology authority"], ["A-SRC-100"]),
    ("fits", "FITS 4.x", "candidate.shape.fits_hdu_list", "container_file_format", "conditional", ["HDU order", "card images", "image/table payloads"], ["vertical scientific meaning", "all time/coordinate conventions"], ["A-SRC-093"]),
    ("openexr", "OpenEXR 3", "candidate.shape.deep_image", "container_codec_layout", "conditional", ["parts", "channels", "deep samples", "tiles/scanlines"], ["scene object semantics", "compositing intent"], ["A-SRC-086"]),
    ("gltf", "glTF 2.0", "candidate.shape.scene_graph", "runtime_asset_binding", "conditional", ["nodes", "meshes", "materials", "animations"], ["CAD features", "BIM semantics", "manufacturing tolerance"], ["A-SRC-102"]),
    ("ifc", "IFC 4.3", "candidate.shape.bim_facility_model", "schema_and_exchange_profile", "conditional", ["typed objects", "relations", "geometry", "property sets"], ["model-view completeness", "asset truth", "authorization"], ["A-SRC-103"]),
    ("step_ap242", "STEP AP242", "candidate.shape.cad_product_model", "application_protocol_binding", "conditional", ["product structure", "geometry", "PMI", "configuration"], ["native feature history", "supplier/private semantics outside profile"], ["A-SRC-104", "GAP-SRC-008"]),
    ("cms", "Cryptographic Message Syntax", "candidate.shape.protected_content_envelope", "asn1_protection_binding", "conditional", ["signed/enveloped content", "certificates", "recipient info"], ["payload truth", "business authorization"], ["A-SRC-126"]),
    ("cose", "CBOR Object Signing and Encryption", "candidate.shape.protected_content_envelope", "cbor_protection_binding", "conditional", ["protected/unprotected headers", "signature/MAC/encryption structure"], ["payload truth", "business authorization"], ["A-SRC-127"]),
    ("cms_to_cose", "CMS to COSE", "candidate.shape.protected_content_envelope", "cross_representation_translation", "partial", ["selected algorithm/key/payload semantics under explicit profile"], ["all algorithm identifiers", "certificate/path semantics", "byte-identical signed content"], ["A-SRC-126", "A-SRC-127"]),
    ("vcf", "VCF 4.5", "candidate.shape.variant_set", "domain_file_binding", "conditional", ["loci", "alleles", "sample calls", "INFO/FORMAT fields"], ["normalized cross-assembly identity", "clinical interpretation"], ["A-SRC-111"]),
    ("vrs", "GA4GH VRS", "candidate.shape.variant_set", "semantic_identity_profile", "conditional", ["computed identifiers", "variation objects", "reference sequences"], ["sample observation", "clinical significance"], ["A-SRC-112"]),
    ("fhir", "FHIR R5", "candidate.shape.fhir_resource_graph", "clinical_exchange_binding", "conditional", ["resource graph", "version identity", "references"], ["profile conformance", "clinical validity", "consent"], ["A-SRC-114"]),
    ("fhir_genomics", "FHIR Genomics Reporting IG", "candidate.shape.genomic_report", "implementation_guide_profile", "conditional", ["report/finding/variant graph", "profiled terminologies"], ["laboratory authority", "causal conclusion", "jurisdictional policy"], ["A-SRC-115"]),
    ("iso20022", "ISO 20022 message catalogue", "candidate.shape.financial_business_message", "business_message_profile", "conditional", ["message components", "business identifiers", "transaction/status structure"], ["market-practice completion", "settlement finality"], ["A-SRC-117"]),
    ("fix", "FIX latest specification", "candidate.shape.fix_message_stream", "session_application_protocol", "conditional", ["session sequence", "tag/group structure", "order/execution lifecycle"], ["cross-venue total order", "market-state completeness"], ["A-SRC-118"]),
    ("citygml", "CityGML 3.0", "candidate.shape.city_model", "conceptual_model_binding", "conditional", ["city object semantics", "geometry/topology", "LoD"], ["render fidelity", "asset freshness"], ["A-SRC-097"]),
    ("stac", "STAC 1.x", "candidate.shape.stac_catalog", "catalog_profile", "conditional", ["catalog graph", "collection/item/assets", "extensions"], ["asset existence", "quality", "access authority"], ["A-SRC-099"]),
    ("hdf5", "HDF5", "candidate.shape.hdf5_group_graph", "container_model_binding", "conditional", ["groups", "links", "datasets", "attributes"], ["domain axes", "units", "time roles"], ["A-DSS-014"]),
    ("netcdf_cf", "netCDF plus CF", "candidate.shape.netcdf_dataset", "scientific_dataset_profile", "conditional", ["named dimensions", "coordinate systems", "units/calendars"], ["all vertical phenomenon meaning", "measurement authority"], ["A-DSS-015", "A-DSS-017"]),
    ("dicom", "DICOM", "candidate.shape.dicom_study_graph", "clinical_imaging_binding", "conditional", ["information entities", "instances/frames", "transfer syntax"], ["patient identity correctness", "diagnostic truth", "de-identification sufficiency"], ["A-DSS-041", "GAP-SRC-007"]),
]


LIBRARIES = [
    ("smtp-envelope", "pure SMTP transaction-envelope types and command-state validator"),
    ("internet-message-graph", "loss-aware RFC 5322/MIME graph parser and serializer contracts"),
    ("mailbox-occurrence", "mailbox occurrence identity, framing and dedup decision library"),
    ("calendar-object", "recurrence, override, timezone and scheduling-object algebra"),
    ("spectrum-contract", "frequency-grid, scaling, window and spectral-unit types"),
    ("deep-image", "deep pixel/sample topology and compositing contracts"),
    ("timed-text", "cue timeline, overlap and retiming laws"),
    ("musical-events", "tick/tempo/event pairing and symbolic music contracts"),
    ("city-model", "semantic city-object, geometry and LoD types"),
    ("stac-catalog", "linked catalog/item/asset contracts without network I/O"),
    ("feature-table", "feature grain, geometry-column and CRS binding contracts"),
    ("hdf5-graph", "group/link/dataset graph abstraction independent of one HDF5 provider"),
    ("netcdf-dataset", "named-dimension and coordinate-system contracts"),
    ("fits-hdu", "ordered heterogeneous HDU/card/payload algebra"),
    ("dicom-information-graph", "study/series/instance/frame identity and lifecycle contracts"),
    ("brep-topology", "exact solid topology, orientation and tolerance laws"),
    ("scene-graph", "node instancing, transform and animation contracts"),
    ("gltf-profile", "glTF representation/profile validator separated from scene semantics"),
    ("cad-product-model", "configuration/effectivity/product-definition contracts"),
    ("bim-facility-model", "facility object, system, containment and model-view contracts"),
    ("bio-sequence", "alphabet/reference/strand qualified sequence value objects"),
    ("sequence-read", "read/pair/group and quality-profile contracts"),
    ("sequence-alignment", "CIGAR/reference/sort and alignment-state contracts"),
    ("genomic-variation", "reference-qualified normalization and variation identity"),
    ("genotype-haplotype", "ploidy, phase and call-uncertainty contracts"),
    ("phenopacket", "phenotype-time/evidence/ontology-edition contracts"),
    ("genomic-report", "finding/interpretation/recommendation authority separation"),
    ("order-book", "event-to-state reconstruction and sequence-gap laws"),
    ("catalog-record", "asset/record/distribution identity and claim authority"),
    ("protected-envelope", "provider-neutral protected payload, key-purpose and verification outcomes"),
    ("fhir-resource-graph", "FHIR identity/reference/history plus explicit profile hooks"),
    ("financial-message", "ISO 20022 choreography and business-status contracts"),
    ("fix-stream", "FIX session/application identity, sequence and resend algebra"),
]


def build() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    (HERE / "schemas").mkdir(exist_ok=True)

    # Preserve source provenance while making this bundle independently inspectable.
    audit_sources = read_jsonl(AUDIT / "standards-sources.jsonl")
    sources = []
    for src in audit_sources:
        copy = dict(src)
        copy["adoption_status"] = "read_only_evidence_snapshot"
        copy["source_origin"] = "data_modality_gap_audit/standards-sources.jsonl"
        sources.append(copy)
    for sid, title, publisher, url, version, supports in EXTRA_SOURCES:
        sources.append({
            "source_id": sid, "title": title, "publisher": publisher, "url": url,
            "edition_or_version": version, "supports": [supports],
            "source_kind": "official_primary_specification", "authority": "normative_or_primary_official",
            "accessed_at": ACCESSED, "limitations": ["Representation conformance does not establish enterprise semantic correctness."],
            "adoption_status": "gap_closure_primary_source", "source_origin": "direct_gap_closure_research",
        })

    contexts, constructs, operations, inferences, adjudications, compiler_requirements = [], [], [], [], [], []
    for index, f in enumerate(FAMILIES, 1):
        (fid, label, cluster, relation, target, representation, evidence, identity, time, order,
         topology, change, uncertainty, security, op_names, invalid) = f
        context_id = f"candidate.bc.{fid}"
        shape_id = f"candidate.shape.{fid}"
        contexts.append({
            "context_id": context_id, "status": "candidate_not_canonical", "name": label,
            "cluster": cluster, "sovereign_question": f"What exact laws make {label.lower()} safe to identify, change, transform and analyze?",
            "inside": ["logical/observation shape", "semantic qualifiers", "identity/time/order/change laws", "representation binding preconditions"],
            "outside": ["vendor runtime implementation", "industry decision authority", "legal conclusion", "analytical result truth"],
            "owns": [fid, f"{fid}_identity", f"{fid}_validity", f"{fid}_representation_profile"],
            "invariants": [identity, time, order, topology, change, uncertainty, security],
            "evidence_refs": evidence,
        })
        aspects = [
            ("logical_shape", label, representation, topology),
            ("semantic_qualifier_set", f"{label} semantic qualifiers", "typed qualifier record", uncertainty),
            ("identity_contract", f"{label} identity contract", "scoped identity and edition relation", identity),
            ("representation_profile", f"{label} representation profile", representation, "representation is not semantic identity"),
        ]
        for kind, suffix_label, carrier, special_law in aspects:
            cid = shape_id if kind == "logical_shape" else f"candidate.{kind}.{fid}"
            constructs.append({
                "construct_id": cid, "construct_kind": kind, "status": "candidate_not_canonical",
                "name": suffix_label, "family_id": fid, "owner_context": context_id,
                "carrier_or_binding": carrier,
                "logical_shape": topology,
                "semantic_qualifiers": ["semantic role", "profile/edition", "authority", "validity", "units/code systems where applicable"],
                "identity_semantics": identity, "time_semantics": time, "order_semantics": order,
                "topology_semantics": topology, "change_semantics": change,
                "uncertainty_semantics": uncertainty, "security_semantics": security,
                "special_law": special_law, "evidence_refs": evidence,
            })
        for op_index, op_name in enumerate(op_names, 1):
            operations.append({
                "operation_cell_id": f"candidate.otm.{fid}.{op_index:02d}", "operation": op_name,
                "owner_context": context_id, "input_constructs": [shape_id],
                "totality": "partial" if op_index != 1 else "conditional_total",
                "determinism": "deterministic_under_named_profile",
                "preconditions": ["exact representation/profile edition is bound", "identity/time/order/topology qualifiers required by the operation are resolved", "resource and security policy permits processing"],
                "success_preserves": ["declared identity relation", "declared time/order relation", "provenance to input edition"],
                "loss_or_residual": "typed residual and loss certificate required when meaning is not preserved",
                "refusal_codes": [f"{fid.upper()}_UNRESOLVED_PROFILE", f"{fid.upper()}_UNSUPPORTED_SEMANTICS", f"{fid.upper()}_LOSS_NOT_ACCEPTED"],
                "evidence_refs": evidence,
            })
        inferences.append({
            "inference_id": f"candidate.invalid.{fid}", "source_assertion": f"A value parses as {representation}.",
            "invalid_conclusion": invalid, "why_invalid": "Syntax or carrier facts do not supply the missing semantic, authority, identity, time, order or topology evidence.",
            "required_evidence": ["named semantic/profile contract", "authority and identity scope", "explicit preservation/loss policy"],
            "compiler_behavior": "refuse_or_emit_typed_unresolved_semantic_gap", "owner_context": context_id,
            "affected_constructs": [shape_id], "evidence_refs": evidence,
        })
        adjudications.append({
            "adjudication_id": f"candidate.adjudication.{fid}", "candidate_id": shape_id,
            "canonical_registry": "san.domain-atlas.data-shapes", "proposed_relation": relation,
            "canonical_target_id": target, "name_equivalence_used": False,
            "comparison_dimensions": ["abstraction layer", "grain and identity", "time and order", "topology", "change", "uncertainty", "security", "operation/refusal surface"],
            "status": "open_manual_adjudication", "automatic_merge_allowed": False,
            "evidence_refs": evidence,
        })
        compiler_requirements.append({
            "requirement_id": f"candidate.compiler.{fid}", "owner_context": context_id,
            "intent_field": f"data_shape.{fid}",
            "required_inputs": ["semantic contract", "exact representation/profile edition", "identity/time/order/change qualifiers", "accepted loss budget", "security purpose"],
            "emitted_ir": ["shape_contract_ir", "representation_binding_ir", "conversion_proof_obligation", "provider_qualification_requirement"],
            "proof_obligations": ["semantic_shape_not_inferred_from_format", "round_trip_or_declared_loss", "profile_edition_exact", "unsupported_semantics_refuse", "provider_qualification_executed"],
            "refusal_when": [invalid, "provider supports bytes but not required semantic operations", "conversion has undeclared loss"],
            "evidence_refs": evidence,
        })

    crosswalks = []
    for cid, source_name, target, layer, roundtrip, preserved, lost, evidence in CROSSWALKS:
        crosswalks.append({
            "crosswalk_id": f"candidate.crosswalk.{cid}", "source_representation": source_name,
            "target_construct_id": target, "binding_layer": layer,
            "round_trip": roundtrip, "preserved": preserved, "not_preserved_or_not_proven": lost,
            "canonicalization": "profile-specific; never infer canonical bytes from semantic equality",
            "compiler_action": "bind exact profile and require fixtures for every preservation/refusal claim",
            "status": "candidate_unqualified_until_conformance_fixtures", "evidence_refs": evidence,
        })

    libraries = []
    for index, (name, purpose) in enumerate(LIBRARIES, 1):
        family = FAMILIES[min(index - 1, len(FAMILIES) - 1)][0]
        libraries.append({
            "library_id": f"candidate.lib.{name}", "status": "candidate_boundary",
            "semantic_owner_context": f"candidate.bc.{family}",
            "library_kind": "semantic_pure", "effect_boundary": "pure_no_io",
            "purpose": purpose, "purity": "domain library; no network, database, scheduler or UI ownership",
            "owns": ["semantic types", "validation/refusal laws", "pure transformations", "provider-neutral requirements"],
            "does_not_own": ["transport I/O", "storage lifecycle", "deployment", "business authorization", "vendor selection"],
            "decision_surfaces": ["profile edition", "identity/equality", "time/order", "loss policy", "unknown extension policy", "security qualifier policy"],
            "compiler_contract": {"requires": [f"candidate.shape.{family}"], "offers": [f"candidate.compiler.{family}"], "binding_phase": "semantic_and_representation_lowering"},
            "evidence_refs": FAMILIES[min(index - 1, len(FAMILIES) - 1)][6],
        })

    qualifications = []
    for cw in crosswalks:
        qualifications.append({
            "qualification_id": cw["crosswalk_id"].replace("crosswalk", "qualification"),
            "subject_kind": "implementation_or_provider_occurrence", "status": "unexecuted_requirement",
            "for_crosswalk": cw["crosswalk_id"],
            "required_fixtures": ["positive", "negative", "boundary", "malformed", "unknown-extension", "lossy-round-trip", "security-adversarial"],
            "must_measure": ["identity preservation", "time/order preservation", "topology preservation", "numeric/text fidelity", "unknown field handling", "resource bounds"],
            "passing_claim": "exact implementation version passes exact profile suite on declared target",
            "forbidden_claim": "provider or format name alone proves support",
            "evidence_refs": cw["evidence_refs"],
        })
    for family in FAMILIES:
        fid, label, *_ = family
        qualifications.append({
            "qualification_id": f"candidate.qualification.semantic_provider.{fid}",
            "subject_kind": "implementation_or_provider_occurrence", "status": "unexecuted_requirement",
            "for_crosswalk": None, "for_construct": f"candidate.shape.{fid}",
            "required_fixtures": ["positive", "negative", "boundary", "malformed", "unknown-extension", "lossy-round-trip", "security-adversarial"],
            "must_measure": ["semantic operation totality", "typed refusals", "identity preservation", "time/order preservation", "topology preservation", "resource bounds"],
            "passing_claim": f"exact implementation version qualifies the {label} semantic contract on an exact target",
            "forbidden_claim": "library import, provider documentation or format parse success alone proves semantic support",
            "evidence_refs": family[6],
        })

    audit_innovations = read_jsonl(AUDIT / "innovations-2021-2026.jsonl")
    wanted_families = {f"fam.{f[0]}" for f in FAMILIES}
    innovations = []
    for src in audit_innovations:
        if len(innovations) >= 22:
            break
        if set(src.get("family_ids", [])) & wanted_families or src["innovation_id"] in {"INNOV-006", "INNOV-008", "INNOV-009", "INNOV-010", "INNOV-011", "INNOV-013", "INNOV-016", "INNOV-018", "INNOV-019", "INNOV-021", "INNOV-022", "INNOV-023", "INNOV-028", "INNOV-029"}:
            rec = dict(src)
            rec["innovation_id"] = f"candidate.{src['innovation_id'].lower()}"
            rec["status"] = "candidate_change_signal_not_taxonomy"
            rec["compiler_effect"] = "re-qualify exact representation/profile and invalidate superseded assumptions; do not mint a semantic type from a release name"
            innovations.append(rec)
    # Ensure the required minimum is met using other audit-confirmed non-LLM changes.
    for src in audit_innovations:
        if len(innovations) >= 22:
            break
        if not any(i["innovation"] == src["innovation"] for i in innovations):
            rec = dict(src)
            rec["innovation_id"] = f"candidate.{src['innovation_id'].lower()}"
            rec["status"] = "candidate_change_signal_not_taxonomy"
            rec["compiler_effect"] = "re-qualify exact representation/profile and invalidate superseded assumptions; do not mint a semantic type from a release name"
            innovations.append(rec)

    gaps = [
        ("roundtrip_fixtures", "critical", "Crosswalk preservation claims lack executable positive/negative/boundary/lossy fixtures."),
        ("smtp_provider_occurrences", "high", "Provider mailbox exports and retry/dedup identities are not qualified."),
        ("calendar_tzdb_drift", "high", "Recurrence results across timezone database editions need executable oracles."),
        ("spectrum_scaling", "high", "FFT normalization, PSD conventions, windows and unit conversions need formal profiles."),
        ("media_accessibility", "high", "Caption completeness, reading order and accessibility are authoritative review claims, not parse results."),
        ("citygml_encodings", "medium", "CityGML conceptual model to GML/JSON/database encodings lacks complete loss matrices."),
        ("stac_extensions", "medium", "The open extension universe needs governed occurrence/version records."),
        ("scientific_conventions", "critical", "HDF5/netCDF/FITS carrier conformance does not cover discipline conventions."),
        ("dicom_private_tags", "critical", "Private tags, burned-in PHI and de-identification profiles require fixture-based qualification."),
        ("brep_tolerance", "critical", "Cross-kernel B-rep validity, tolerance and persistent naming need independent conformance."),
        ("cad_native_features", "high", "AP242 exchange does not prove complete native feature-history preservation."),
        ("ifc_model_views", "high", "IFC schema validity must not substitute for model-view and project information requirements."),
        ("genomic_reference_registry", "critical", "Assembly, sequence, transcript and ontology edition resolution needs a governed registry."),
        ("variant_normalization", "critical", "VCF/VRS/liftover equivalence requires executable reference-aware law oracles."),
        ("clinical_authority", "critical", "Genomic finding, interpretation, diagnosis and recommendation authority remain distinct and unbound."),
        ("order_book_venue_profiles", "critical", "Venue-specific sequencing, recovery and priority rules need exact profiles and replay corpora."),
        ("iso20022_market_practice", "high", "Message schema must be paired with jurisdiction/network market-practice constraints."),
        ("fix_dictionary_versions", "high", "FIX dictionaries, custom tags, session profiles and venue dialects require occurrence qualification."),
        ("crypto_algorithm_agility", "critical", "CMS/COSE translation and verification require dated algorithm/key-purpose policy."),
        ("canonical_adjudication", "critical", "Every proposed relation remains open until manual law comparison and two independent implementations."),
    ]
    gap_records = [{"gap_id": f"candidate.gap.{gid}", "severity": sev, "description": desc, "status": "open", "completion_effect": "prevents completeness claim"} for gid, sev, desc in gaps]

    dump_jsonl(HERE / "sources.jsonl", sources)
    dump_jsonl(HERE / "context-candidates.jsonl", contexts)
    dump_jsonl(HERE / "shape-type-candidates.jsonl", constructs)
    dump_jsonl(HERE / "operation-totality.jsonl", operations)
    dump_jsonl(HERE / "invalid-inferences.jsonl", inferences)
    dump_jsonl(HERE / "canonical-adjudications.jsonl", adjudications)
    dump_jsonl(HERE / "representation-crosswalks.jsonl", crosswalks)
    dump_jsonl(HERE / "compiler-requirements.jsonl", compiler_requirements)
    dump_jsonl(HERE / "library-boundaries.jsonl", libraries)
    dump_jsonl(HERE / "provider-qualifications.jsonl", qualifications)
    dump_jsonl(HERE / "innovations-2021-2026.jsonl", innovations)
    dump_jsonl(HERE / "gaps.jsonl", gap_records)

    # Lightweight schemas are complemented by semantic/refential checks in validate_candidate.py.
    schemas = {
        "context.schema.json": ("context_id", ["status", "name", "sovereign_question", "inside", "outside", "owns", "invariants", "evidence_refs"]),
        "construct.schema.json": ("construct_id", ["construct_kind", "owner_context", "carrier_or_binding", "identity_semantics", "time_semantics", "order_semantics", "topology_semantics", "change_semantics", "uncertainty_semantics", "security_semantics", "evidence_refs"]),
        "crosswalk.schema.json": ("crosswalk_id", ["source_representation", "target_construct_id", "binding_layer", "round_trip", "preserved", "not_preserved_or_not_proven", "evidence_refs"]),
        "operation.schema.json": ("operation_cell_id", ["operation", "owner_context", "totality", "preconditions", "refusal_codes", "evidence_refs"]),
        "compiler-library.schema.json": ("library_id", ["purpose", "purity", "decision_surfaces", "compiler_contract", "evidence_refs"]),
        "source.schema.json": ("source_id", ["title", "publisher", "url", "source_kind", "authority", "supports"]),
    }
    for filename, (id_field, required) in schemas.items():
        properties = {id_field: {"type": "string", "minLength": 1}}
        for field in required:
            properties[field] = {"type": ["string", "array", "object", "boolean", "null"]}
        dump_json(HERE / "schemas" / filename, {
            "$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
            "required": [id_field, *required], "properties": properties, "additionalProperties": True,
        })

    files = [p for p in HERE.glob("*.jsonl")]
    digest = hashlib.sha256("".join(p.read_text() for p in sorted(files)).encode()).hexdigest()
    coverage = {
        "status": "candidate_gap_closure_not_completeness_claim",
        "counts": {
            "primary_sources": len(sources), "bounded_context_candidates": len(contexts),
            "shape_type_constructs": len(constructs), "operation_totality_cells": len(operations),
            "invalid_inferences": len(inferences), "representation_crosswalks": len(crosswalks),
            "canonical_adjudications": len(adjudications), "compiler_requirements": len(compiler_requirements),
            "library_boundaries": len(libraries), "provider_qualification_requirements": len(qualifications),
            "innovations_2021_2026": len(innovations), "open_gaps": len(gap_records),
        },
        "required_exact_crosswalk_terms": ["GeoParquet", "FITS", "OpenEXR", "glTF", "IFC", "STEP AP242", "CMS", "COSE", "VCF", "FHIR", "ISO 20022", "FIX"],
        "forbidden_shortcuts": [
            "unstructured is not a data type", "format name is not semantic type identity",
            "parse success is not semantic validity", "provider name is not qualification",
            "schema validity is not business or clinical validity", "successful signature is not truth or authorization",
        ],
        "bundle_sha256_over_jsonl": digest,
    }
    dump_json(HERE / "coverage-report.json", coverage)
    dump_json(HERE / "manifest.json", {
        "bundle_id": "san.domain-atlas.data-shapes-gap-closure", "edition": 1,
        "status": "candidate_extension_and_adjudication_bundle", "generated_at": ACCESSED,
        "canonical_input": str(CANONICAL.relative_to(UNIVERSES.parent.parent)),
        "audit_input": str(AUDIT.relative_to(UNIVERSES.parent.parent)),
        "files": sorted([p.name for p in HERE.iterdir() if p.is_file() and p.name not in {"manifest.json"}]),
        "coverage": coverage["counts"], "completeness_claim": False,
    })


if __name__ == "__main__":
    build()
