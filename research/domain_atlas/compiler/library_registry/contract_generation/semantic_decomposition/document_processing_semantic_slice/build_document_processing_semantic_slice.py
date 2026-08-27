#!/usr/bin/env python3
"""Build an evidence-backed semantic slice for document and text processing."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
AS_OF = "2026-08-27"
PRODUCT = "product.document_processing_review"
TEXT_NEIGHBOR = "library.method_kernels.text_semantics"
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def product_subject_rows() -> list[dict[str, Any]]:
    return load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")


def library_universe() -> list[str]:
    refs = {
        edge["concrete_library_ref"]
        for row in product_subject_rows()
        if row["product_ref"] == PRODUCT
        for edge in row["concrete_bindings"]
    }
    refs.add(TEXT_NEIGHBOR)
    return sorted(refs)


LIBRARIES = library_universe()


def sources() -> list[dict[str, Any]]:
    rows = [
        ("pdf2", "ISO 32000-2:2020 — Portable document format — PDF 2.0", ["ISO/TC 171/SC 2"], 2020, "normative_container_and_rendition_standard", "https://www.iso.org/standard/75839.html", "Defines the PDF object, page, graphics, text, structure, annotation, form, encryption and incremental-update carrier model.", "PDF conformance does not establish safety, accessibility, extraction correctness or business truth."),
        ("pdf-archive", "PDF Specification Archive", ["PDF Association"], 2026, "official_standards_index", "https://pdfa.org/resource/pdf-specification-archive/", "Provides public access paths, editions, errata and extensions for ISO PDF specifications.", "An index or erratum is not a document-processing semantic owner."),
        ("pdfua2", "ISO 14289-2:2024 — PDF/UA-2", ["ISO/TC 171/SC 2"], 2024, "accessibility_standard", "https://www.iso.org/standard/82278.html", "Constrains accessible use of PDF 2.0 structure and content.", "Technical accessibility conformance does not prove usability for every person or task."),
        ("pdfa4", "ISO 19005-4:2020 — PDF/A-4", ["ISO/TC 171/SC 2"], 2020, "preservation_profile_standard", "https://www.iso.org/standard/71832.html", "Constrains PDF 2.0 for long-term preservation and reproducible rendering.", "Archival-profile conformance is not semantic completeness or retention authority."),
        ("epub33", "EPUB 3.3", ["W3C Publishing Maintenance Working Group"], 2026, "web_recommendation", "https://www.w3.org/TR/epub-33/", "Defines an editioned container and publication model for structured web content, resources and reading order.", "Publication packaging does not establish extracted meaning or reading-system equivalence."),
        ("ecma376", "ECMA-376 Office Open XML File Formats", ["Ecma TC45"], 2021, "normative_office_document_standard", "https://ecma-international.org/publications-and-standards/standards/ecma-376/", "Defines OOXML vocabularies, relationships and Open Packaging Conventions.", "A valid package may contain external relationships, macros or application-specific behavior and is not automatically safe."),
        ("odf13", "OpenDocument Format 1.3", ["OASIS OpenDocument TC"], 2021, "normative_office_document_standard", "https://docs.oasis-open.org/office/OpenDocument/v1.3/os/", "Defines package, content, styles, metadata and schema for application-independent office documents.", "ODF conformance does not select a canonical rendition or extraction schema."),
        ("mime", "MIME Sniffing Living Standard", ["WHATWG"], 2026, "normative_detection_standard", "https://mimesniff.spec.whatwg.org/", "Defines parsing and byte-pattern sniffing for MIME types.", "A sniffed type is evidence about a representation, not semantic validity, safety or identity."),
        ("media-types", "RFC 6838 — Media Type Specifications and Registration Procedures", ["IETF"], 2013, "internet_standard", "https://www.rfc-editor.org/rfc/rfc6838", "Defines media-type registration, naming, parameters and security-consideration obligations.", "A declared media type can be absent, wrong or malicious."),
        ("zip", "APPNOTE.TXT — ZIP File Format Specification", ["PKWARE"], 2024, "official_container_specification", "https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT", "Defines ZIP records, compression, encryption and archive structure used by compound document formats.", "A syntactically valid archive may exhaust resources or contain unsafe paths and relationships."),
        ("unicode17", "The Unicode Standard, Version 17.0", ["Unicode Consortium"], 2025, "normative_text_standard", "https://www.unicode.org/versions/Unicode17.0.0/", "Defines Unicode characters, code points, properties and conformance.", "A code point is not necessarily a user-perceived character, glyph, token or semantic unit."),
        ("uax15", "UAX #15 — Unicode Normalization Forms", ["Unicode Consortium"], 2025, "normative_text_algorithm", "https://www.unicode.org/reports/tr15/", "Defines canonical and compatibility equivalence and NFC, NFD, NFKC and NFKD.", "Normalization may lose compatibility distinctions and does not preserve byte offsets without a mapping."),
        ("uax29", "UAX #29 — Unicode Text Segmentation", ["Unicode Consortium"], 2025, "normative_segmentation_algorithm", "https://www.unicode.org/reports/tr29/", "Defines default grapheme, word and sentence boundaries plus tailoring requirements.", "Default segmentation does not universally match language-, genre- or task-specific semantic units."),
        ("uax9", "UAX #9 — Unicode Bidirectional Algorithm", ["Unicode Consortium"], 2025, "normative_text_order_algorithm", "https://www.unicode.org/reports/tr9/", "Defines resolved display ordering for bidirectional text.", "Display order is not storage order, logical document order or OCR reading order."),
        ("encoding", "Encoding Living Standard", ["WHATWG"], 2026, "normative_character_encoding_standard", "https://encoding.spec.whatwg.org/", "Defines interoperable decoding behavior for legacy encodings and UTF encodings.", "Successful decoding does not prove the declared encoding, original characters or intended language."),
        ("html", "HTML Living Standard", ["WHATWG"], 2026, "normative_document_model", "https://html.spec.whatwg.org/", "Defines HTML parsing, DOM document semantics and rendering-related structures.", "DOM structure, accessibility tree and visual layout are different projections."),
        ("xml", "Extensible Markup Language (XML) 1.0", ["World Wide Web Consortium"], 2008, "web_recommendation", "https://www.w3.org/TR/xml/", "Defines XML documents, entities, markup and well-formedness.", "Well-formed XML is not schema validity, safe entity processing or semantic correctness."),
        ("c14n", "Canonical XML Version 1.1", ["World Wide Web Consortium"], 2008, "web_recommendation", "https://www.w3.org/TR/xml-c14n11/", "Defines a canonical byte representation for an XML information set.", "Canonical bytes do not imply semantic identity across schemas or transformations."),
        ("alto44", "ALTO XML Schema 4.4", ["Library of Congress ALTO Editorial Board"], 2023, "official_layout_text_schema", "https://www.loc.gov/standards/alto/", "Represents pages, blocks, lines, strings, coordinates, reading order, language and OCR confidence.", "ALTO coordinates and text are assertions tied to an image and processing edition, not source truth."),
        ("pagexml", "PAGE XML Schema", ["PRImA Research Lab", "OCR-D"], 2025, "official_layout_text_schema", "https://ocr-d.de/en/spec/page", "Represents page regions, reading order, alternatives, recognition text and confidence.", "PAGE structure does not make a layout label, order or transcription correct."),
        ("ocrd", "OCR-D Technical Specification", ["OCR-D"], 2026, "official_workflow_specification", "https://ocr-d.de/en/spec/", "Defines reproducible OCR workflow interfaces, workspace files, PAGE conventions and processing metadata.", "Workflow interoperability does not qualify every OCR, layout or correction method."),
        ("ocrd-eval", "Quality Assurance in OCR-D", ["OCR-D"], 2026, "official_evaluation_specification", "https://ocr-d.de/en/spec/ocrd_eval.html", "Requires representative ground truth and localized evaluation of segmentation and transcription.", "Aggregate error rates can hide script, class, page and region failures."),
        ("hocr", "The hOCR Embedded OCR Workflow and Output Format", ["Thomas Breuel and contributors"], 2010, "community_ocr_encoding", "https://kba.github.io/hocr-spec/1.2/", "Defines HTML-based OCR text, layout, coordinates and metadata conventions.", "A hOCR carrier is not a universal content graph or evaluation authority."),
        ("iiif", "IIIF Presentation API 3.0", ["IIIF Consortium"], 2020, "open_presentation_standard", "https://iiif.io/api/presentation/3.0/", "Defines compound-object manifests, canvases, ranges, content resources and annotation alignment.", "Presentation structure explicitly does not own discovery, search or all descriptive semantics."),
        ("mets2", "METS Version 2", ["Library of Congress", "METS Editorial Board"], 2025, "official_structural_metadata_schema", "https://www.loc.gov/standards/mets/mets2.html", "Defines simplified descriptive, administrative, file and structural metadata for compound digital objects.", "A METS package does not establish the intellectual work, extracted fact or provenance truth."),
        ("tei", "TEI P5 Guidelines 4.12.0", ["Text Encoding Initiative Consortium"], 2026, "official_text_encoding_guidelines", "https://www.tei-c.org/release/doc/tei-p5-doc/en/html/", "Defines customizable markup for textual structures, interpretations, variants, transcription and scholarly apparatus.", "A TEI encoding is an editioned interpretation, not a lossless mirror of every visual or material property."),
        ("jats", "ANSI/NISO Z39.96-2024 — JATS 1.4", ["NISO JATS Standing Committee"], 2024, "national_document_schema_standard", "https://www.niso.org/publications/z3996-2024-jats", "Defines XML structures for journal-article textual, graphical and metadata content.", "JATS applicability is genre-specific and does not prove article claims."),
        ("annotation", "Web Annotation Data Model", ["World Wide Web Consortium"], 2017, "web_recommendation", "https://www.w3.org/TR/annotation-model/", "Separates annotation, body, target, selector, state, purpose, agent and lifecycle.", "An annotation association is not acceptance, ground truth or source identity."),
        ("prov", "PROV-O — The PROV Ontology", ["World Wide Web Consortium"], 2013, "web_recommendation", "https://www.w3.org/TR/prov-o/", "Defines entities, activities, agents, generation, use, derivation, attribution, association and delegation.", "Provenance is not proof of truth, correctness, causation or authorization."),
        ("c2pa", "C2PA Specifications 2.2", ["Coalition for Content Provenance and Authenticity"], 2025, "content_provenance_standard", "https://spec.c2pa.org/specifications/specifications/2.2/index.html", "Defines signed manifests, assertions, actions, content bindings and validation for media provenance.", "Authenticity and chain-of-actions evidence do not establish semantic truth or extraction correctness."),
        ("doclaynet", "DocLayNet: A Large Human-Annotated Dataset for Document-Layout Segmentation", ["Birgit Pfitzmann", "Christoph Auer", "Michele Dolfi", "Ahmed S. Nassar", "Peter Staar"], 2022, "peer_reviewed_primary_dataset", "https://research.ibm.com/publications/doclaynet-a-large-human-annotated-dataset-for-document-layout-segmentation", "Provides diverse human-annotated page layouts, double/triple annotation and agreement baselines.", "Its 11 classes and sampled domains are not a universal document ontology."),
        ("pubtables", "PubTables-1M: Towards Comprehensive Table Extraction From Unstructured Documents", ["Brandon Smock", "Rohith Pesala", "Robin Abraham"], 2022, "peer_reviewed_primary_dataset", "https://arxiv.org/abs/2110.00061", "Provides large-scale table detection, structure and functional-analysis annotations with canonicalization.", "Scientific-article tables do not cover all enterprise forms, spreadsheets or visual table conventions."),
        ("grits", "GriTS: Grid Table Similarity Metric for Table Structure Recognition", ["Brandon Smock", "Rohith Pesala", "Robin Abraham"], 2022, "peer_reviewed_primary_metric", "https://www.microsoft.com/en-us/research/?p=835363", "Defines content, topology and location similarity for table grids using matrix alignment.", "A table-structure metric does not measure factual correctness or downstream fitness."),
        ("funsd", "FUNSD: A Dataset for Form Understanding in Noisy Scanned Documents", ["Guillaume Jaume", "Hazim Kemal Ekenel", "Jean-Philippe Thiran"], 2019, "peer_reviewed_primary_dataset", "https://guillaumejaume.github.io/FUNSD/", "Provides noisy scanned-form words, labels and semantic links for form understanding.", "One dataset's labels and forms are not a universal business-document schema."),
        ("tesseract", "Tesseract User Manual", ["Tesseract OCR contributors"], 2026, "official_provider_contract", "https://tesseract-ocr.github.io/tessdoc/", "Documents a widely adopted OCR provider, language data, segmentation modes and output formats.", "Provider behavior and confidence are not portable semantic ownership or calibrated correctness."),
        ("xforms", "XForms 2.0", ["World Wide Web Consortium XForms Users Community Group"], 2025, "community_form_model", "https://www.w3.org/community/xformsusers/wiki/XForms_2.0", "Separates form data model, controls, constraints, calculations and submissions.", "A control or field is not an answered, verified or authorized claim."),
        ("csvw", "Model for Tabular Data and Metadata on the Web", ["World Wide Web Consortium"], 2015, "web_recommendation", "https://www.w3.org/TR/tabular-data-model/", "Defines tables, rows, columns, schemas, annotations, datatypes and foreign-key relations.", "A rectangular table carrier does not recover visual spans, header scopes or domain meaning automatically."),
        ("owasp-upload", "File Upload Cheat Sheet", ["OWASP Foundation"], 2026, "operational_security_guidance", "https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html", "Catalogs extension, type, signature, naming, size, storage, parser and authorization controls for hostile uploads.", "Operational guidance is not a normative document ontology or proof that a file is safe."),
        ("pdf-redaction", "PDF Redaction — Addendum to the PDF Association Technical Note", ["PDF Association"], 2022, "industry_security_guidance", "https://pdfa.org/resource/pdf-redaction/", "Distinguishes redaction annotations, application and removal of underlying content.", "Visual covering or a redaction mark does not prove sensitive content was removed."),
        ("json", "RFC 8259 — The JavaScript Object Notation Data Interchange Format", ["IETF"], 2017, "internet_standard", "https://www.rfc-editor.org/rfc/rfc8259", "Defines JSON syntax, values, interoperability and parser considerations.", "JSON serialization does not define a document extraction schema or semantic equality."),
    ]
    return [{
        "source_id": f"source.document.{sid}", "title": title,
        "authors_or_publisher": authors, "year": year, "source_kind": kind, "url": url,
        "bounded_implication": implication, "authority_limit": limit,
    } for sid, title, authors, year, kind, url, implication, limit in rows]


def modules() -> list[dict[str, Any]]:
    rows = [
        ("document-occurrence", "What carrier occurrence, intellectual work, edition, revision and processing case are being discussed?", "identity/lifecycle model", ["mets2", "tei"], []),
        ("carrier-container", "Which byte carrier, media type, container members, relationships, encryption and embedded resources are present?", "representation/container model", ["pdf2", "ecma376", "odf13", "epub33"], ["document-occurrence"]),
        ("format-detection", "Which declared, sniffed, parsed and validated format hypotheses exist, with what evidence?", "evidence classification model", ["mime", "media-types"], ["carrier-container"]),
        ("admission-safety", "Which integrity, decompression, recursion, external-reference, encryption and parser budgets admit or refuse a carrier?", "resource-bounded admission protocol", ["zip", "owasp-upload", "pdf2"], ["carrier-container", "format-detection"]),
        ("text-decoding", "Which character encoding and error policy maps bytes to Unicode scalar values with offset provenance?", "partial decoding function", ["encoding", "unicode17"], ["carrier-container"]),
        ("text-normalization", "Which Unicode normalization/collation profile is applied and what distinctions and offsets are lost?", "text equivalence algebra", ["uax15", "unicode17"], ["text-decoding"]),
        ("text-segmentation", "Which grapheme, word, sentence, line or tailored linguistic boundaries are asserted?", "segmentation relation", ["uax29", "uax9"], ["text-normalization"]),
        ("logical-structure", "Which sections, headings, lists, figures, references and semantic elements form a logical document structure?", "ordered typed tree/graph", ["tei", "jats", "html"], ["document-occurrence"]),
        ("page-revision", "What makes a page/canvas and its revision, crop, rotation, dimensions and coordinate frame the same occurrence?", "versioned spatial identity model", ["iiif", "alto44", "pagexml"], ["document-occurrence"]),
        ("rendition-profile", "Which fonts, color, resources, conformance profile and renderer policy define a bounded rendition?", "rendition decision profile", ["pdf2", "pdfa4", "epub33"], ["carrier-container", "page-revision"]),
        ("rendition-evaluation", "How is a rendered result compared to an editioned reference without equating pixel equality with semantic equality?", "conformance/evaluation model", ["pdf2", "pdfa4", "iiif"], ["rendition-profile"]),
        ("accessibility", "Which tags, reading order, alternatives, language and navigation claims support accessible use?", "accessibility conformance model", ["pdfua2", "epub33", "alto44"], ["logical-structure", "rendition-profile"]),
        ("image-preprocessing", "Which crop, deskew, binarization, denoise and dewarp transformations create a derived page image and loss receipt?", "image transformation pipeline", ["ocrd", "pagexml"], ["page-revision"]),
        ("ocr-recognition", "Which image region, script/language, recognition model and decoding profile produce character/token alternatives?", "statistical recognition model", ["ocrd", "tesseract", "pagexml"], ["image-preprocessing", "text-decoding"]),
        ("ocr-alternatives-confidence", "How are recognition alternatives, scores, calibration scope and abstention represented?", "uncertainty/evidence model", ["alto44", "pagexml", "ocrd-eval"], ["ocr-recognition"]),
        ("layout-regions", "Which page regions and labels are detected at what taxonomy, geometry and annotation edition?", "spatial classification model", ["doclaynet", "alto44", "pagexml"], ["page-revision"]),
        ("reading-order", "Which partial or total order relates regions, lines and tokens, including columns and bidirectional text?", "order/topology model", ["alto44", "pagexml", "uax9"], ["layout-regions", "text-segmentation"]),
        ("content-graph", "How are pages, regions, lines, tokens, glyphs, logical elements, tables, figures and provenance edges represented?", "versioned attributed graph", ["mets2", "iiif", "annotation"], ["logical-structure", "layout-regions", "reading-order"]),
        ("anchors-selectors", "How does a stable selector address exact bytes, text, geometry or structure under a declared revision and rendition?", "addressing/selector model", ["annotation", "iiif"], ["content-graph", "page-revision"]),
        ("partitioning", "Which structural, visual, linguistic or bounded-size partition creates units while preserving overlap and provenance?", "partition algebra", ["uax29", "tei", "content-placeholder"], ["content-graph", "text-segmentation"]),
        ("parser-adapter", "How does a provider-specific parser map foreign objects, warnings and loss into the canonical content graph?", "anti-corruption adapter", ["pdf2", "ecma376", "odf13"], ["carrier-container", "content-graph"]),
        ("document-classification", "Which document/section/page label taxonomy, evidence and abstention policy produce a classification candidate?", "statistical classification model", ["doclaynet", "funsd"], ["content-graph"]),
        ("information-extraction", "Which mention, entity, relation, event or field candidates are extracted under an editioned schema?", "typed extraction relation", ["tei", "jats", "annotation"], ["content-graph", "anchors-selectors"]),
        ("schema-binding", "How are source candidates mapped to field types, multiplicity, constraints, authority and residual information?", "constraint/mapping model", ["jats", "csvw", "json"], ["information-extraction"]),
        ("table-extraction", "Which visual table, grid topology, spanning cells, header scopes, content and footnotes form a table candidate?", "table graph reconstruction model", ["pubtables", "grits", "csvw"], ["layout-regions", "content-graph"]),
        ("form-extraction", "Which prompts, controls, marks, answers, groups and semantic links form a form candidate?", "form relation model", ["funsd", "xforms", "pdf2"], ["layout-regions", "information-extraction"]),
        ("extraction-evaluation", "Which representative ground truth, matching relation and localized metrics evaluate extraction?", "evaluation/appraisal model", ["ocrd-eval", "grits", "doclaynet"], ["information-extraction", "table-extraction", "form-extraction"]),
        ("uncertainty-abstention", "Which ambiguity, missing support, score, calibrated uncertainty and review threshold prevent false certainty?", "partiality/decision model", ["ocrd-eval", "doclaynet"], ["ocr-alternatives-confidence", "extraction-evaluation"]),
        ("provenance-anchor", "Which source occurrence, activity, agent, method edition and selector support an extracted candidate?", "provenance/evidence graph", ["prov", "annotation", "c2pa"], ["anchors-selectors", "information-extraction"]),
        ("transformation-loss", "Which decoding, normalization, rendering, OCR, partition, schema and export losses weaken anchors or claims?", "information-loss algebra", ["prov", "uax15", "c14n"], ["provenance-anchor"]),
        ("case-review", "How are typed exceptions, evidence, assignments, judgments, corrections and disposition tracked without overwriting candidates?", "case/state-machine import", ["annotation", "prov"], ["uncertainty-abstention", "provenance-anchor"]),
        ("judgment-authority", "Who may review, correct, accept or reject which candidate under what policy and evidence?", "authority protocol import", ["annotation", "prov"], ["case-review"]),
        ("correction-versioning", "How do correction, supersession, reprocessing, recall and retraction preserve prior editions and blast radius?", "versioned lifecycle model", ["mets2", "prov", "annotation"], ["document-occurrence", "case-review"]),
        ("validation-import", "How is an editioned structured output validated without turning validation into factual acceptance?", "validation execution import", ["json", "csvw", "jats"], ["schema-binding"]),
        ("export-release-import", "How are accepted candidates planned, encoded, delivered and receipted without granting publication authority?", "export/effect-port import", ["json", "prov"], ["validation-import", "provenance-anchor"]),
        ("materialization-import", "How is one immutable output edition published with identity, idempotency and recall evidence?", "materialization effect import", ["prov", "c2pa"], ["export-release-import", "correction-versioning"]),
        ("search-handoff", "Which addressable text/content artifacts are supplied to search while ranking and index visibility remain external?", "published-language seam", ["annotation", "iiif"], ["content-graph", "text-segmentation"]),
        ("annotation-handoff", "Which candidates and anchors are supplied to annotation operations while label ontology and dataset lifecycle remain external?", "published-language seam", ["annotation", "doclaynet"], ["anchors-selectors", "extraction-evaluation"]),
    ]
    result = []
    for mid, question, formalism, refs, deps in rows:
        actual_refs = ["ocrd" if ref == "content-placeholder" else ref for ref in refs]
        result.append({
            "module_id": f"module.document.{mid}", "owned_question": question,
            "formalism": formalism, "source_refs": [f"source.document.{ref}" for ref in actual_refs],
            "dependency_refs": [f"module.document.{ref}" for ref in deps],
            "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED",
        })
    return result


MODULE_MAP = {
    "library.method_kernels.text_semantics": ["text-decoding", "text-normalization", "text-segmentation"],
    "library.method_kernels.document_container_semantics": ["document-occurrence", "carrier-container", "format-detection", "admission-safety"],
    "library.san_format_probe": ["format-detection"],
    "library.san_integrity": ["admission-safety"],
    "library.document.rendition.profile.compiler": ["rendition-profile", "accessibility"],
    "library.document.rendition.evaluator": ["rendition-evaluation"],
    "library.method_kernels.document_ocr_methods": ["image-preprocessing", "ocr-recognition", "ocr-alternatives-confidence"],
    "library.method_kernels.document_layout_methods": ["layout-regions", "reading-order"],
    "library.method_kernels.document_content_graph": ["logical-structure", "page-revision", "content-graph", "anchors-selectors"],
    "library.method_kernels.document_parser_adapters": ["parser-adapter", "partitioning"],
    "library.method_kernels.document_classification_methods": ["document-classification"],
    "library.method_kernels.document_information_extraction": ["information-extraction", "schema-binding", "uncertainty-abstention"],
    "library.method_kernels.document_table_extraction": ["table-extraction"],
    "library.method_kernels.document_form_extraction": ["form-extraction"],
    "library.method_kernels.document_extraction_evaluation": ["extraction-evaluation"],
    "library.method_kernels.document_provenance_loss": ["provenance-anchor", "transformation-loss"],
    "library.cbv.analytical_case_reducer": ["case-review"],
    "library.cbv.decision_handoff_algebra": ["case-review", "judgment-authority"],
    "library.csp.decision.judgment-port": ["judgment-authority"],
    "library.csp.decision.decision-ledger": ["case-review", "judgment-authority"],
    "library.csp.identity.version-identity": ["document-occurrence", "page-revision", "correction-versioning"],
    "library.lpe.prov-statement-algebra": ["provenance-anchor"],
    "library.lpe.provenance-assertion": ["provenance-anchor"],
    "library.qor.validation_execution_kernel": ["validation-import"],
    "library.cbv.export_plan": ["export-release-import"],
    "library.cbv.export_encoder": ["export-release-import"],
    "library.cbv.export_delivery_port": ["export-release-import"],
    "library.pipeline.materialization_publisher": ["materialization-import"],
}


def laws() -> list[dict[str, Any]]:
    texts = [
        "A carrier or file is not the intellectual document or its business meaning.",
        "A declared media type is not a detected format; a detected format is not semantic validity.",
        "Parseable is not safe; syntactic validity is not bounded-resource admission.",
        "Byte identity, container identity, rendition identity and document identity are distinct.",
        "A rendered page is not the document's logical structure.",
        "A visual glyph is not a Unicode character, code point or grapheme cluster.",
        "Character decoding success does not prove the original encoding or intended character.",
        "Canonical Unicode equivalence is not byte equality or compatibility equivalence.",
        "Normalization must preserve an offset/loss map when source anchoring is required.",
        "Storage order, display order, reading order and logical order are distinct.",
        "An OCR token is a recognition hypothesis, not a source glyph or accepted transcription.",
        "An OCR provider score is not a correctness probability unless calibrated for the declared population.",
        "A layout region is not a logical section and a bounding box is not content identity.",
        "Page coordinates are not stable anchors without page revision, coordinate frame and rendition identity.",
        "A chunk is not inherently a paragraph, section, sentence, evidence unit or semantic unit.",
        "A parser adapter maps foreign representations; it does not own canonical document meaning.",
        "A parser output is not a canonical content graph merely because it is structured.",
        "Agreement between parsers is not proof of correctness.",
        "A document classification is a candidate under a taxonomy edition, not source truth.",
        "A text span or mention is not an entity; an entity mention is not entity identity.",
        "A relation mention is not a world relation and a field candidate is not an adjudicated fact.",
        "A table image is not a logical table; a detected grid is not semantic header scope.",
        "A rectangular cell matrix does not capture every spanning, nested or presentational table.",
        "A form field or control is not an answered, verified or authorized claim.",
        "Schema validation is not factual acceptance or downstream decision fitness.",
        "Aggregate precision, recall or error rate does not establish per-class, per-page or per-domain reliability.",
        "Ground-truth annotation is an editioned judgment with authority and disagreement, not infallible truth.",
        "A provenance statement does not prove truth, causation, correctness or authority.",
        "Content authenticity does not establish extraction correctness or claim truth.",
        "A resolvable citation or selector does not establish that the source supports a claim.",
        "Transformation provenance must declare information and anchor loss; it cannot silently strengthen evidence.",
        "Human review is an authority-bound judgment, not an automatic truth oracle.",
        "A correction does not erase a prior candidate; supersession is not deletion.",
        "Reprocessing creates a new attempt and output edition; it does not rewrite historical evidence.",
        "A redaction appearance or annotation does not prove underlying content removal.",
        "Structured output does not replace preservation of the admitted source occurrence and evidence.",
        "Encoding and export do not authorize publication, disclosure or downstream use.",
        "Materialization success does not establish output fitness or business acceptance.",
        "Search relevance is not extraction correctness and embedding similarity is not semantic equivalence.",
        "Annotation operations own label/judgment lifecycle; document processing owns addressable candidates and evidence handoff.",
        "OCR, layout, classification and extraction methods are provider implementations, not product or semantic owners.",
        "Document findings and reviewed structured candidates do not grant business-decision authority.",
        "Accessibility conformance, archival conformance and visual fidelity are independent properties.",
        "Resource exhaustion must produce a typed refusal, never silent truncation presented as completeness.",
        "Unknown encryption, external references, active content or decompression expansion must fail closed by policy.",
        "Provider, model, parser, schema and Unicode editions are explicit inputs, never ambient defaults.",
        "No LLM or agent output is evidence authority, factual authority or approval authority by itself.",
    ]
    return [{"law_id": f"law.document.non-collapse.{i:02d}", "law": text, "status": "CANDIDATE_UNRATIFIED"} for i, text in enumerate(texts, 1)]


def methods() -> list[dict[str, Any]]:
    groups = {
        "admission": ["extension_and_declared_type_check", "magic_signature_sniffing", "container_inventory", "schema_validation", "integrity_digest_check", "encryption_detection", "archive_bomb_budgeting", "active_content_and_external_relationship_detection"],
        "rendition": ["profile_compilation", "font_and_resource_resolution", "reference_rendering", "pixel_difference", "perceptual_render_difference", "structure_tree_validation", "accessibility_conformance", "page_geometry_normalization"],
        "text": ["character_decoding", "unicode_normalization", "grapheme_segmentation", "word_segmentation", "sentence_segmentation", "bidirectional_resolution", "locale_collation", "offset_alignment"],
        "ocr_layout": ["deskew_dewarp_binarize", "script_language_identification", "line_and_word_recognition", "recognition_alternative_decoding", "confidence_calibration", "region_detection", "reading_order_inference", "logical_structure_recovery"],
        "extraction": ["document_classification", "section_classification", "named_entity_extraction", "relation_extraction", "event_extraction", "key_value_extraction", "schema_guided_extraction", "table_detection", "table_structure_recognition", "header_scope_inference", "form_field_detection", "form_semantic_linking"],
        "evaluation_review": ["character_error_rate", "word_error_rate", "layout_iou_and_map", "table_grits_content_topology_location", "span_exact_and_overlap_matching", "field_precision_recall_f1", "calibration_and_selective_risk", "double_annotation_agreement", "typed_exception_routing", "human_adjudication", "reprocessing_blast_radius"],
        "provenance_release": ["selector_resolution", "activity_derivation_graph", "transformation_loss_propagation", "signed_content_manifest_validation", "structured_output_validation", "editioned_export", "idempotent_materialization", "recall_and_supersession"],
    }
    return [
        {"method_id": f"method.document.{name.replace('_', '-')}", "method_family": family,
         "method_name": name, "semantic_preconditions_required": True,
         "provider_is_semantic_owner": False, "status": "METHOD_BOUNDARY_CANDIDATE"}
        for family, names in groups.items() for name in names
    ]


def experts() -> list[dict[str, Any]]:
    rows = [
        ("ken-whistler", "Ken Whistler", ["uax15", "unicode17"], ["Treat Unicode edition, normalization form and equivalence relation as explicit contract inputs.", "Preserve the distinction between character identity and rendered glyphs."]),
        ("mark-davis", "Mark Davis", ["unicode17", "uax29"], ["Build text processing from standardized properties and conformance data.", "Default boundaries remain tailorable rather than universal semantics."]),
        ("thomas-breuel", "Thomas Breuel", ["hocr"], ["Represent OCR output with layout, coordinates and method metadata.", "Keep OCR workflow carriers separate from recognition truth."]),
        ("ray-smith", "Ray Smith", ["tesseract"], ["Expose segmentation mode, language data and recognition configuration.", "Provider confidence and engine behavior require independent calibration and qualification."]),
        ("peter-staar", "Peter Staar", ["doclaynet"], ["Train and evaluate layout methods on diverse document domains.", "Compare model performance with human agreement instead of assuming labels are obvious."]),
        ("birgit-pfitzmann", "Birgit Pfitzmann", ["doclaynet"], ["Preserve dataset provenance, annotation taxonomy and disagreement.", "General-purpose layout coverage requires domain diversity."]),
        ("michele-dolfi", "Michele Dolfi", ["doclaynet"], ["Treat document conversion as a structured-content recovery problem.", "Layout detection is only one stage of a larger content graph."]),
        ("brandon-smock", "Brandon Smock", ["pubtables", "grits"], ["Separate table detection, structure, content, location and functional roles.", "Evaluate grid topology rather than using one bounding-box metric."]),
        ("robin-abraham", "Robin Abraham", ["pubtables", "grits"], ["Canonicalization rules materially affect table ground truth.", "A metric must match the table structure being claimed."]),
        ("robert-sanderson", "Robert Sanderson", ["annotation", "iiif"], ["Address exact resource segments through selector and state models.", "Keep annotations, targets, bodies, motivations and source versions distinct."]),
        ("paolo-ciccarese", "Paolo Ciccarese", ["annotation"], ["Model review and interpretation as explicit annotation graphs.", "An annotation is an association, not automatic acceptance."]),
        ("luc-moreau", "Luc Moreau", ["prov"], ["Represent entities, activities, agents and derivation as distinct provenance roles.", "Provenance supports bounded explanation but does not prove correctness."]),
        ("paul-groth", "Paul Groth", ["prov"], ["Use interoperable provenance relations and named evidence.", "Keep evidence authority separate from semantic and operational authority."]),
        ("matt-garrish", "Matt Garrish", ["epub33"], ["Treat publication container, reading order, resources and accessibility as editioned profiles.", "Reading-system behavior must not silently define document semantics."]),
        ("syd-bauman", "Syd Bauman", ["tei"], ["Use explicit customizable schemas for textual interpretation.", "Encoding choices are scholarly/domain decisions with declared loss and scope."]),
        ("guillaume-jaume", "Guillaume Jaume", ["funsd"], ["Model forms through words, semantic labels and relations rather than OCR text alone.", "Dataset-specific form labels require domain schema translation."]),
    ]
    return [{
        "expert_id": f"expert.document.{eid}", "name": name,
        "source_refs": [f"source.document.{ref}" for ref in refs],
        "lessons_for_composable_platform": lessons,
        "authority_limit": "Expert work constrains candidate semantics and methods; the expert is not the SAN semantic owner or qualification authority.",
        "status": "RESEARCHED_PROFILE",
    } for eid, name, refs, lessons in rows]


def innovations() -> list[dict[str, Any]]:
    rows = [
        ("doclaynet", 2022, "DocLayNet introduced a diverse, human-annotated layout corpus with agreement evidence rather than one scientific-publication layout distribution.", ["doclaynet"]),
        ("pubtables-grits", 2022, "PubTables-1M plus GriTS made table detection, grid structure, location and content separately representable and evaluable.", ["pubtables", "grits"]),
        ("alto44", 2023, "ALTO 4.4 added page language and rotation while recent ALTO editions added explicit reading order and bidirectional properties.", ["alto44"]),
        ("pdfua2", 2024, "PDF/UA-2 aligned accessible-document conformance with PDF 2.0 structure and semantics.", ["pdfua2", "pdf2"]),
        ("jats14", 2024, "JATS 1.4 advanced an editioned, continuously maintained semantic article carrier rather than ad hoc field extraction.", ["jats"]),
        ("mets2", 2025, "METS 2 simplified compound-object structural metadata and removed its XLink dependency while preserving migration concerns.", ["mets2"]),
        ("c2pa22", 2025, "C2PA 2.2 standardized content-bound provenance manifests, assertions and actions while retaining authenticity-versus-truth limits.", ["c2pa"]),
        ("unicode17", 2025, "Unicode 17 and current annexes provide editioned conformance data for normalization, segmentation and bidirectional text.", ["unicode17", "uax15", "uax29", "uax9"]),
        ("epub33", 2026, "EPUB 3.3 became a current W3C Recommendation with test-suite and reading-system contracts for structured publications.", ["epub33"]),
        ("ocrd-current", 2026, "Current OCR-D specifications integrate PAGE, repeatable workflow metadata and localized ground-truth evaluation.", ["ocrd", "ocrd-eval", "pagexml"]),
    ]
    return [{
        "innovation_id": f"innovation.document.{iid}", "year": year, "innovation": text,
        "source_refs": [f"source.document.{ref}" for ref in refs], "ai_or_llm_dependency": False,
        "boundary_implication": "Encode the change as an editioned carrier, method, evidence or conformance module; do not create an ambient AI product or transfer semantic authority to a provider.",
        "status": "EVIDENCE_BACKED_NON_LLM_INNOVATION",
    } for iid, year, text, refs in rows]


AXIS_QUESTIONS = {
    "semantic_object": "Which carrier occurrence, document/work edition, page, rendition, content element, OCR/layout/extraction candidate, table/form, review case, output edition or evidence object is owned?",
    "semantic_role": "Which roles are source owner, document subject, operator, parser/provider, schema owner, annotator, reviewer, evidence issuer, publisher and downstream accepting authority?",
    "identity_and_equality": "What distinguishes byte, container, work, edition, revision, page/canvas, region, selector, candidate, schema, attempt, output and provenance identities and equivalences?",
    "grain_and_cardinality": "Are operations per byte range, member, document, page, region, line, token, grapheme, field, cell, table, case, attempt or output edition, with what multiplicity and completeness?",
    "state_and_change": "What legal received, admitted, refused, rendered, parsed, extracted, validated, exception, reviewed, accepted, released, recalled, superseded and reprocessed transitions exist?",
    "time": "How are source creation/effective time, revision validity, processing time, recording time, review time, release time, retention time and reconstruction time separated?",
    "order_and_topology": "Which package relationships, page sequence, reading order, logical hierarchy, region graph, table grid, form links and provenance graph are asserted or derived?",
    "partiality_and_uncertainty": "How are unknown format, malformed/encrypted content, alternatives, missing text, ambiguous order, scores, calibration, extraction uncertainty, abstention and unresolved review represented?",
    "authority_and_trust": "Who may define schemas and profiles, admit carriers, accept correction, release output, disclose content, recall an edition and accept a downstream fact?",
    "effect_boundary": "How are pure detection/rendering/extraction/validation separated from file access, review assignment, publication, materialization, disclosure and business action?",
    "representation": "Which bytes, PDF/OOXML/ODF/EPUB, image, Unicode, ALTO/PAGE/hOCR, content graph, annotation, table/form, JSON and provenance carriers are used, at what edition and loss?",
    "composition_algebra": "How do admission, rendition, decoding, OCR, layout, graph, partition, extraction, validation, review, provenance and release compose and propagate refusals and loss?",
    "compatibility_and_evolution": "What changes to carrier, Unicode, parser, renderer, model, taxonomy, schema, selector, review policy and output edition preserve compatibility or force reprocessing?",
    "resources_and_failure": "What byte, expansion, recursion, page, pixel, token, graph, parser, model, memory, deadline, review and output budgets apply, and when must processing refuse?",
    "evidence_and_conformance": "Which standard fixtures, malformed corpora, Unicode tests, render references, representative ground truth, localized metrics, negative twins and independent providers support each claim?",
    "privacy_security_safety": "How are hostile files, active content, external references, decompression bombs, hidden/redacted data, sensitive text, reviewer exposure, retention, disclosure and unsafe downstream claims controlled?",
}


NATIVE = {
    "library.document.rendition.evaluator", "library.document.rendition.profile.compiler",
    "library.method_kernels.document_classification_methods", "library.method_kernels.document_container_semantics",
    "library.method_kernels.document_content_graph", "library.method_kernels.document_extraction_evaluation",
    "library.method_kernels.document_form_extraction", "library.method_kernels.document_information_extraction",
    "library.method_kernels.document_layout_methods", "library.method_kernels.document_ocr_methods",
    "library.method_kernels.document_parser_adapters", "library.method_kernels.document_provenance_loss",
    "library.method_kernels.document_table_extraction",
}


def boundary_findings(products_by_library: dict[str, set[str]]) -> list[dict[str, Any]]:
    shared = sorted(set(LIBRARIES) - NATIVE - {TEXT_NEIGHBOR})
    return [
        {"finding_id": "finding.document.product-retain.v1", "library_refs": sorted(NATIVE), "current_product_refs": [PRODUCT], "candidate_disposition": "RETAIN_DOCUMENT_PROCESSING_REVIEW_PRODUCT", "reason": "Carrier admission through bounded rendition, content recovery, extraction, exception review and structured-output release is one user-visible operational lifecycle with its own cases, attempts, evidence and recall.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.document.native-versus-imported.v1", "library_refs": shared, "current_product_refs": [PRODUCT], "candidate_disposition": "RETAIN_AS_EXPLICIT_SHARED_IMPORTS_NOT_PRODUCT_OWNED", "reason": "Case, judgment, version identity, provenance, validation, export, integrity and materialization responsibilities are reused across products and retain external semantic owners.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.document.text-foundation.v1", "library_refs": [TEXT_NEIGHBOR], "current_product_refs": [], "candidate_disposition": "BIND_AS_SHARED_TEXT_FOUNDATION_CANDIDATE", "reason": "Decoding, Unicode normalization, segmentation, collation and offset mapping are prerequisites for document, search and annotation semantics, but the captured graph declares no product consumer.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.document.search-seam.v1", "library_refs": ["library.method_kernels.document_content_graph", TEXT_NEIGHBOR], "current_product_refs": [PRODUCT, "product.search_index_service"], "candidate_disposition": "PUBLISHED_LANGUAGE_CONTENT_AND_ANCHORS_TO_SEARCH", "reason": "Document processing supplies versioned addressable content; search owns indexing, query interpretation, ranking and visibility.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.document.annotation-seam.v1", "library_refs": ["library.method_kernels.document_content_graph", "library.method_kernels.document_extraction_evaluation"], "current_product_refs": [PRODUCT, "product.annotation_operations"], "candidate_disposition": "PUBLISHED_LANGUAGE_CANDIDATES_AND_ANCHORS_TO_ANNOTATION", "reason": "Document processing may emit candidates and selectors; annotation operations own labeling tasks, ontology, adjudication and training/evaluation-dataset lifecycle.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.document.parser-provider-acl.v1", "library_refs": ["library.method_kernels.document_parser_adapters"], "current_product_refs": [PRODUCT], "candidate_disposition": "ANTI_CORRUPTION_ADAPTER_ONLY", "reason": "Parser providers map foreign carriers and diagnostics into canonical document objects with declared loss; provider object models do not own document semantics.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.document.provenance-loss-narrow.v1", "library_refs": ["library.method_kernels.document_provenance_loss", "library.lpe.prov-statement-algebra", "library.lpe.provenance-assertion"], "current_product_refs": [PRODUCT, "product.lineage_provenance"], "candidate_disposition": "DOCUMENT_LIBRARY_OWNS_TRANSFORMATION_AND_ANCHOR_LOSS_ONLY", "reason": "The document-specific library records decoding, rendering, OCR, partition and extraction loss; generic provenance entities, activities and assertions remain lineage/provenance-owned.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.document.judgment-authority.v1", "library_refs": ["library.csp.decision.judgment-port", "library.csp.decision.decision-ledger", "library.cbv.decision_handoff_algebra"], "current_product_refs": [PRODUCT], "candidate_disposition": "IMPORTED_JUDGMENT_AND_EVIDENCE_HANDOFF_AUTHORITY", "reason": "The product requests and records review but does not manufacture reviewer authority or turn accepted extraction into a business fact.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.document.format-integrity-sharing.v1", "library_refs": ["library.san_format_probe", "library.san_integrity"], "current_product_refs": [PRODUCT], "candidate_disposition": "SHARED_REPRESENTATION_ADMISSION_PRIMITIVES", "reason": "Format evidence and integrity/resource admission are reusable representation concerns even though the current declared product graph exposes only the document consumer.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.document.release-authority.v1", "library_refs": ["library.cbv.export_plan", "library.cbv.export_encoder", "library.cbv.export_delivery_port", "library.pipeline.materialization_publisher"], "current_product_refs": [PRODUCT], "candidate_disposition": "IMPORTED_RELEASE_MECHANICS_DISCLOSURE_AUTHORITY_EXTERNAL", "reason": "Encoding, delivery and materialization can execute a selected release plan but cannot authorize disclosure, retention, factual acceptance or downstream action.", "owner_decision": "UNRATIFIED"},
    ]


def build() -> dict[str, Any]:
    source_rows, module_rows, law_rows = sources(), modules(), laws()
    method_rows, expert_rows, innovation_rows = methods(), experts(), innovations()
    contributions = {row["library_id"]: row for row in load_jsonl(REGISTRY / "library-contributions.jsonl")}
    coordinate_dockets = {row["library_ref"]: row for row in load_jsonl(SEM / "library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact_dockets = {row["library_ref"]: row for row in load_jsonl(SEM / "p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    products_by_library = {ref: set() for ref in LIBRARIES}
    subjects_by_library = {ref: set() for ref in LIBRARIES}
    for subject in product_subject_rows():
        for edge in subject["concrete_bindings"]:
            ref = edge["concrete_library_ref"]
            if ref in products_by_library:
                products_by_library[ref].add(subject["product_ref"])
                subjects_by_library[ref].add(subject["subject_ref"])
    target_occurrences = {(row["axis"], row["library_ref"]): row for row in load_jsonl(SEM / "targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    module_by_id = {row["module_id"]: row for row in module_rows}
    library_rows, axis_rows = [], []
    for ref in LIBRARIES:
        mods = [f"module.document.{name}" for name in MODULE_MAP[ref]]
        evidence = sorted({src for mod in mods for src in module_by_id[mod]["source_refs"]})
        exact_docket = exact_dockets.get(ref)
        coordinate_docket = coordinate_dockets.get(ref)
        if ref == TEXT_NEIGHBOR:
            disposition = "BIND_AS_SHARED_TEXT_FOUNDATION_CANDIDATE"
        elif ref in NATIVE:
            disposition = "RETAIN_DOCUMENT_NATIVE_NARROW_MODULE_BOUNDARY"
        else:
            disposition = "RETAIN_SHARED_IMPORT_EXTERNAL_SEMANTIC_OWNER"
        library_rows.append({
            "record_kind": "document_processing_library_semantic_binding_candidate",
            "binding_id": f"binding.document-semantic-slice.{slug(ref)}.v1",
            "library_ref": ref, "library_name": contributions[ref]["name"],
            "semantic_module_refs": mods, "evidence_refs": evidence,
            "exact_contract_docket_ref": exact_docket["docket_id"] if exact_docket else None,
            "coordinate_binding_docket_ref": coordinate_docket["binding_docket_id"] if coordinate_docket else None,
            "downstream_contract_route": "ROUTED" if exact_docket and coordinate_docket else "MISSING_P5_AND_COORDINATE_DOCKET_TYPED_VACANCY",
            "downstream_subject_refs": sorted(subjects_by_library[ref]),
            "downstream_product_refs": sorted(products_by_library[ref]),
            "boundary_disposition_candidate": disposition,
            "compiler_binding": "REFUSED",
            "refusal_reasons": (["DOWNSTREAM_CONTRACT_ROUTE_MISSING"] if not exact_docket or not coordinate_docket else []) + ["OWNER_RATIFICATION_MISSING", "MEMBER_AXIS_APPLICABILITY_UNRATIFIED", "EXACT_CONTRACT_UNSELECTED", "IMPLEMENTATIONS_UNQUALIFIED"],
            "completion_claim": False,
        })
        for axis in AXES:
            targeted = target_occurrences.get((axis, ref))
            axis_rows.append({
                "record_kind": "document_processing_library_axis_decision_candidate",
                "decision_candidate_id": f"decision-candidate.document-axis.{slug(ref)}.{axis.replace('_', '-')}.v1",
                "library_ref": ref, "axis": axis, "semantic_module_refs": mods,
                "coordinate_question": AXIS_QUESTIONS[axis],
                "applicability_candidate": "REQUIRED_EXPLICIT_PROFILE", "evidence_refs": evidence,
                "targeted_member_adjudication_occurrence_ref": targeted["occurrence_id"] if targeted else None,
                "coordinate_answers": [], "member_applicability": "PROPOSED_OWNER_REVIEW_REQUIRED",
                "owner_decision": "UNRATIFIED", "status": "EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER",
                "canonical_gaps_closed": 0, "completion_claim": False,
            })
    findings = boundary_findings(products_by_library)
    context = {
        "record_kind": "bounded_context_candidate", "context_id": "context.document-processing-semantic-slice.v1",
        "as_of": AS_OF,
        "vision": "How can one admitted document occurrence be rendered, textually and structurally understood, extracted, evaluated, reviewed and released as provenance-linked structured candidates without collapsing carrier into document, OCR into truth, provenance into correctness or review into business authority?",
        "inside": ["carrier/container detection and bounded admission", "document/page/revision and rendition profiles", "Unicode decoding, normalization, segmentation and offset mapping", "OCR, layout, reading order and content graph", "partitioning and parser anti-corruption adapters", "classification, information, table and form extraction", "uncertainty, evaluation, provenance and transformation loss", "typed exception review, correction, reprocessing and structured-output release"],
        "outside": ["generic transport and object-store ownership", "records-retention and disclosure authority", "search index, query and ranking lifecycle", "annotation ontology and dataset lifecycle", "generic lineage/provenance ownership", "business-fact acceptance and downstream case disposition", "provider/model semantic ownership", "LLM or agent authority"],
        "neighbors": [
            {"context_ref": "context.representation-and-integrity", "relationship": "customer_supplier"},
            {"context_ref": "context.text-semantics", "relationship": "customer_supplier"},
            {"context_ref": "context.annotation-operations", "relationship": "published_language"},
            {"context_ref": "context.search-index-service", "relationship": "published_language"},
            {"context_ref": "context.lineage-provenance", "relationship": "anti_corruption_layer"},
            {"context_ref": "context.judgment-authority", "relationship": "anti_corruption_layer"},
            {"context_ref": "context.materialization-runtime", "relationship": "customer_supplier"},
        ],
        "published_language": ["DocumentOccurrence", "DocumentRevision", "CarrierEvidence", "AdmissionDecision", "PageRevision", "RenditionProfile", "ContentGraph", "ContentSelector", "RecognitionAlternative", "LayoutRegion", "ReadingOrder", "ExtractionSchemaEdition", "ExtractionCandidate", "TableCandidate", "FormCandidate", "ValidationFinding", "DocumentReviewCase", "CorrectionEdition", "TransformationLoss", "StructuredOutputEdition", "DocumentEvidenceHandoff"],
        "ratification": "WITHHELD", "completion_claim": False,
    }
    summary = {
        "program_id": "program.document-processing-semantic-slice.v1", "as_of": AS_OF,
        "primary_or_official_sources": len(source_rows), "semantic_modules": len(module_rows),
        "non_collapse_laws": len(law_rows), "method_types": len(method_rows),
        "expert_learning_profiles": len(expert_rows), "recent_non_llm_innovations": len(innovation_rows),
        "bound_libraries": len(library_rows), "document_native_libraries": len(NATIVE),
        "shared_import_libraries": len(set(LIBRARIES) - NATIVE - {TEXT_NEIGHBOR}),
        "unconsumed_shared_foundation_candidates": sum(not products_by_library[ref] for ref in LIBRARIES),
        "library_axis_decision_candidates": len(axis_rows), "product_capability_boundary_findings": len(findings),
        "downstream_products": len({p for values in products_by_library.values() for p in values}),
        "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0,
        "canonical_gaps_closed": 0, "completion_claim": False,
    }
    return {"context": context, "sources": source_rows, "modules": module_rows, "laws": law_rows,
            "methods": method_rows, "experts": expert_rows, "innovations": innovation_rows,
            "libraries": library_rows, "axes": axis_rows, "findings": findings, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "bounded-context.json": json.dumps(built["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "semantic-modules.jsonl": "".join(canonical(row) + "\n" for row in built["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(row) + "\n" for row in built["laws"]),
        "document-method-taxonomy.jsonl": "".join(canonical(row) + "\n" for row in built["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(row) + "\n" for row in built["experts"]),
        "innovation-records.jsonl": "".join(canonical(row) + "\n" for row in built["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(row) + "\n" for row in built["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(row) + "\n" for row in built["findings"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.document-processing-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    summary = build()["summary"]
    print(f"BUILD PASS document processing semantic slice: {summary['semantic_modules']} modules, {summary['method_types']} methods, {summary['bound_libraries']} libraries and {summary['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
