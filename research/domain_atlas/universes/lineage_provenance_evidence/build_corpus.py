#!/usr/bin/env python3
"""Deterministically build the lineage, provenance and evidence candidate universe.

This is an open-world research seed.  Records are candidates, not accepted domain truth.
Primary sources are authority-scoped: a signature specification can support an integrity
mechanism, for example, but cannot prove that the signed claim is true.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema"
EDITION = 1
ACCESSED = "2026-08-25"


def dump_json(name: str, value: Any) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_jsonl(name: str, rows: list[dict[str, Any]]) -> None:
    with (ROOT / name).open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def sid(short: str) -> str:
    return f"source.lpe.{short}"


# Primary standards, specifications, official guidance, official project documents, and primary
# research artifacts.  `authority_scope` deliberately limits what each reference can establish.
SOURCE_ROWS = [
    ("w3c.prov.dm", "PROV-DM: The PROV Data Model", "W3C", "standard", "https://www.w3.org/TR/prov-dm/", 2013, "PROV entities, activities, agents, relations and event-time constraints", ["provenance_model", "derivation", "responsibility"]),
    ("w3c.prov.o", "PROV-O: The PROV Ontology", "W3C", "standard", "https://www.w3.org/TR/prov-o/", 2013, "OWL encoding and qualified PROV relations", ["provenance_graph", "interchange"]),
    ("w3c.prov.n", "PROV-N: The Provenance Notation", "W3C", "standard", "https://www.w3.org/TR/prov-n/", 2013, "Human-readable PROV notation", ["serialization", "interchange"]),
    ("w3c.prov.constraints", "Constraints of the PROV Data Model", "W3C", "standard", "https://www.w3.org/TR/prov-constraints/", 2013, "PROV validity, ordering and inference constraints", ["validation", "temporal_constraints"]),
    ("w3c.prov.aq", "PROV-AQ: Provenance Access and Query", "W3C", "working_group_note", "https://www.w3.org/TR/prov-aq/", 2013, "Discovery and retrieval of provenance descriptions", ["provenance_access", "query"]),
    ("w3c.prov.links", "Linking Across Provenance Bundles", "W3C", "working_group_note", "https://www.w3.org/TR/prov-links/", 2013, "Cross-bundle provenance linking", ["bundle", "federation"]),
    ("w3c.prov.dictionary", "PROV Dictionary", "W3C", "working_group_note", "https://www.w3.org/TR/prov-dictionary/", 2013, "Provenance of dictionary-like collections", ["collection", "membership"]),
    ("w3c.prov.dc", "Dublin Core to PROV Mapping", "W3C", "working_group_note", "https://www.w3.org/TR/prov-dc/", 2013, "Mapping descriptive metadata to PROV", ["metadata_mapping", "provenance"]),
    ("w3c.dcat3", "Data Catalog Vocabulary (DCAT) Version 3", "W3C", "standard", "https://www.w3.org/TR/vocab-dcat-3/", 2024, "Catalog resources, distributions, versions, series and checksums", ["catalog", "version", "distribution"]),
    ("w3c.dqv", "Data on the Web Best Practices: Data Quality Vocabulary", "W3C", "working_group_note", "https://www.w3.org/TR/vocab-dqv/", 2016, "Quality measurements, annotations and provenance links", ["quality", "measurement", "annotation"]),
    ("w3c.webanno", "Web Annotation Data Model", "W3C", "standard", "https://www.w3.org/TR/annotation-model/", 2017, "Targeted annotations, motivations and bodies", ["annotation", "evidence_target"]),
    ("w3c.earl", "Evaluation and Report Language 1.0 Schema", "W3C", "working_group_note", "https://www.w3.org/TR/EARL10-Schema/", 2011, "Machine-readable conformance assertions and test results", ["conformance", "test_evidence"]),
    ("w3c.vc2", "Verifiable Credentials Data Model v2.0", "W3C", "standard", "https://www.w3.org/TR/vc-data-model-2.0/", 2025, "Issuer-subject claims, validity, status and verifier processing; verifiability is not truth", ["credential", "claim", "status"]),
    ("w3c.vc.integrity", "Verifiable Credential Data Integrity 1.0", "W3C", "standard", "https://www.w3.org/TR/vc-data-integrity/", 2025, "Tamper-evident securing and verification of credential data", ["integrity", "signature", "verification"]),
    ("w3c.vc.bbs", "Data Integrity BBS Cryptosuites v1.0", "W3C", "candidate_recommendation", "https://www.w3.org/TR/vc-di-bbs/", 2026, "Work-in-progress BBS proof derivation, mandatory reveal, selective disclosure, unlinkability and leakage considerations", ["selective_disclosure", "derived_proof", "privacy"]),
    ("w3c.vc.status", "Bitstring Status List v1.0", "W3C", "standard", "https://www.w3.org/TR/vc-bitstring-status-list/", 2025, "Privacy-preserving credential suspension and revocation status", ["revocation", "status", "freshness"]),
    ("w3c.odrl", "ODRL Information Model 2.2", "W3C", "standard", "https://www.w3.org/TR/odrl-model/", 2018, "Permissions, prohibitions, duties and constraints for policy-scoped use", ["policy", "permission", "prohibition", "duty"]),
    ("w3c.did", "Decentralized Identifiers (DIDs) v1.0", "W3C", "standard", "https://www.w3.org/TR/did-core/", 2022, "Identifier documents, verification methods and service endpoints", ["identity", "verification_method"]),
    ("w3c.rdf.canon", "RDF Dataset Canonicalization", "W3C", "standard", "https://www.w3.org/TR/rdf-canon/", 2024, "Deterministic RDF dataset canonicalization for comparison and securing", ["canonicalization", "digest_input"]),
    ("w3c.tracecontext", "Trace Context", "W3C", "standard", "https://www.w3.org/TR/trace-context/", 2021, "Distributed trace correlation identifiers and propagation", ["trace", "correlation"]),
    ("w3c.owl.time", "Time Ontology in OWL", "W3C", "standard", "https://www.w3.org/TR/owl-time/", 2022, "Instants, intervals, temporal reference systems and relations", ["time", "validity"]),
    ("w3c.data.cube", "The RDF Data Cube Vocabulary", "W3C", "standard", "https://www.w3.org/TR/vocab-data-cube/", 2014, "Multidimensional statistical observations and data structures", ["observation", "dataset"]),
    ("openlineage.spec", "OpenLineage Specification", "OpenLineage", "official_specification", "https://openlineage.io/docs/spec/", 2026, "Job, run, dataset and event model for runtime lineage emission", ["runtime_lineage", "job", "run", "dataset"]),
    ("openlineage.lifecycle", "OpenLineage Lifecycle", "OpenLineage", "official_specification", "https://openlineage.io/docs/spec/run-cycle", 2026, "Run-event lifecycle and transition meanings", ["run_event", "lifecycle"]),
    ("openlineage.facets", "OpenLineage Facets and Extensibility", "OpenLineage", "official_specification", "https://openlineage.io/docs/spec/facets/", 2026, "Facet extension and producer metadata rules", ["facet", "extension"]),
    ("openlineage.column", "OpenLineage Column Lineage Dataset Facet", "OpenLineage", "official_specification", "https://openlineage.io/docs/spec/facets/dataset-facets/column_lineage_facet", 2026, "Field dependencies and transformation descriptions", ["column_lineage", "transformation"]),
    ("openlineage.schema", "OpenLineage Schema Dataset Facet", "OpenLineage", "official_specification", "https://openlineage.io/docs/spec/facets/dataset-facets/schema_facet", 2026, "Dataset field schema observed for a lineage event", ["schema", "dataset"]),
    ("openlineage.sql", "OpenLineage SQL Job Facet", "OpenLineage", "official_specification", "https://openlineage.io/docs/spec/facets/job-facets/sql_job_facet", 2026, "SQL source attached to a job facet", ["prospective_lineage", "logical_plan"]),
    ("openlineage.parent", "OpenLineage Parent Run Facet", "OpenLineage", "official_specification", "https://openlineage.io/docs/spec/facets/run-facets/parent_run_facet", 2026, "Hierarchical run linkage", ["run_lineage", "orchestration"]),
    ("ietf.rfc3339", "RFC 3339: Date and Time on the Internet", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc3339.html", 2002, "Timestamp syntax and offsets", ["timestamp", "recording_time"]),
    ("ietf.rfc3161", "RFC 3161: Time-Stamp Protocol", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc3161.html", 2001, "Trusted timestamp tokens over message imprints", ["timestamp_authority", "temporal_evidence"]),
    ("ietf.rfc5424", "RFC 5424: The Syslog Protocol", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc5424.html", 2009, "Structured event transport and origin metadata", ["log", "transport"]),
    ("ietf.rfc8785", "RFC 8785: JSON Canonicalization Scheme", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8785.html", 2020, "Deterministic JSON serialization", ["canonicalization", "digest_input"]),
    ("ietf.rfc8949", "RFC 8949: Concise Binary Object Representation", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8949.html", 2020, "CBOR data model and deterministic encoding considerations", ["serialization", "canonicalization"]),
    ("ietf.rfc9052", "RFC 9052: COSE Structures and Process", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9052.html", 2022, "CBOR signature, MAC and encryption structures", ["signature", "integrity"]),
    ("ietf.rfc9162", "RFC 9162: Certificate Transparency Version 2.0", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9162.html", 2021, "Merkle transparency logs, inclusion and consistency proofs", ["transparency", "receipt"]),
    ("ietf.rfc9334", "RFC 9334: Remote ATtestation procedureS Architecture", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9334.html", 2023, "Attester, verifier, relying party, evidence and appraisal roles", ["attestation", "independent_appraisal"]),
    ("ietf.rfc9711", "RFC 9711: Entity Attestation Token", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9711.html", 2025, "Attestation claims token syntax and processing", ["attestation", "claims"]),
    ("ietf.rfc9942", "RFC 9942: COSE Receipts", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9942.html", 2026, "Cryptographic receipts for inclusion in verifiable data structures", ["receipt", "transparency"]),
    ("ietf.rfc9943", "RFC 9943: An Architecture for Trustworthy and Transparent Digital Supply Chains", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9943.html", 2026, "Signed statements, transparency registration and receipts", ["transparent_statement", "receipt"]),
    ("ietf.rfc9901", "RFC 9901: Selective Disclosure for JSON Web Tokens", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9901.html", 2026, "SD-JWT issuance, selective claim disclosure and verifier processing", ["selective_disclosure", "jwt", "presentation"]),
    ("ietf.rfc4998", "RFC 4998: Evidence Record Syntax", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc4998.html", 2007, "Long-term evidence records and archive timestamps", ["long_term_validation", "preservation"]),
    ("ietf.rfc6283", "RFC 6283: Extensible Markup Language Evidence Record Syntax", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc6283.html", 2011, "XML evidence record syntax for long-term validation", ["long_term_validation", "preservation"]),
    ("ietf.rfc8493", "RFC 8493: The BagIt File Packaging Format", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8493.html", 2018, "Manifested file packaging and payload validation", ["transfer_package", "manifest", "custody"]),
    ("cncf.cloudevents", "CloudEvents Specification 1.0.2", "Cloud Native Computing Foundation", "official_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", 2022, "Portable event envelope and context attributes", ["event_envelope", "interoperability"]),
    ("otel.logs", "OpenTelemetry Logs Data Model", "OpenTelemetry", "official_specification", "https://opentelemetry.io/docs/specs/otel/logs/data-model/", 2026, "Log record fields including event and observed timestamps", ["observability", "log"]),
    ("otel.trace", "OpenTelemetry Trace Semantic Conventions", "OpenTelemetry", "official_specification", "https://opentelemetry.io/docs/specs/semconv/general/trace/", 2026, "Trace span semantics and links", ["observability", "trace"]),
    ("otel.schemas", "OpenTelemetry Telemetry Schemas", "OpenTelemetry", "official_specification", "https://opentelemetry.io/docs/specs/otel/schemas/", 2026, "Versioned telemetry schema transformation", ["telemetry_schema", "compatibility"]),
    ("slsa.provenance", "SLSA Provenance", "OpenSSF SLSA", "official_specification", "https://slsa.dev/spec/v1.1/provenance", 2023, "Build provenance predicate and verification model", ["attestation", "build_provenance"]),
    ("slsa.build", "SLSA Build Track", "OpenSSF SLSA", "official_specification", "https://slsa.dev/spec/v1.1/levels", 2023, "Progressive build assurance requirements", ["assurance", "build"]),
    ("intoto.attestation", "in-toto Attestation Framework", "in-toto", "official_specification", "https://github.com/in-toto/attestation/tree/v1.0/spec", 2022, "Statement envelope and versioned predicate model", ["attestation", "predicate"]),
    ("intoto.layout", "in-toto Specification", "in-toto", "official_specification", "https://github.com/in-toto/docs/blob/master/in-toto-spec.md", 2023, "Supply-chain layout, link metadata and verification", ["plan", "execution", "verification"]),
    ("intoto.dsse", "Dead Simple Signing Envelope", "in-toto", "official_specification", "https://github.com/secure-systems-lab/dsse/blob/master/envelope.md", 2021, "Signature envelope with payload-type binding", ["signature", "envelope"]),
    ("sigstore.bundle", "Sigstore Bundle Format", "Sigstore", "official_specification", "https://docs.sigstore.dev/about/bundle/", 2026, "Portable verification material and transparency evidence bundle", ["evidence_bundle", "signature", "transparency"]),
    ("sigstore.rekor", "Rekor Transparency Log", "Sigstore", "official_documentation", "https://docs.sigstore.dev/logging/overview/", 2026, "Append-only transparency log and inclusion verification", ["transparency", "receipt"]),
    ("tuf.spec", "The Update Framework Specification", "The Update Framework", "official_specification", "https://theupdateframework.github.io/specification/latest/", 2026, "Signed metadata roles, expiry, rollback and freeze resistance", ["metadata", "expiry", "delegation"]),
    ("spdx.3", "SPDX Specification 3.0.1", "Linux Foundation SPDX", "official_specification", "https://spdx.github.io/spdx-spec/v3.0.1/", 2024, "Software, dataset and build metadata model with relationships", ["artifact_metadata", "relationship"]),
    ("cyclonedx.16", "CycloneDX Specification 1.6", "OWASP Foundation", "official_specification", "https://cyclonedx.org/docs/1.6/json/", 2024, "BOM, formulation, declarations, attestations and evidence structures", ["attestation", "artifact_metadata"]),
    ("rocrate.11", "RO-Crate Metadata Specification 1.1", "Research Object Crate Community", "community_standard", "https://www.researchobject.org/ro-crate/1.1/", 2022, "Packaged research objects with contextual metadata", ["reproducibility", "research_object"]),
    ("workflow.run.crate", "Workflow Run RO-Crate Profile", "Workflow Run Crate Community", "community_standard", "https://www.researchobject.org/workflow-run-crate/profiles/process_run_crate/", 2024, "Prospective and retrospective workflow-run provenance packaging", ["workflow", "runtime_provenance", "reproducibility"]),
    ("cwl.12", "Common Workflow Language v1.2", "Common Workflow Language Project", "community_standard", "https://www.commonwl.org/v1.2/", 2020, "Portable workflow and tool descriptions", ["prospective_lineage", "workflow_plan"]),
    ("cwlprov", "CWLProv Research Object", "Common Workflow Language Project", "primary_research", "https://www.researchobject.org/cwlprov/", 2018, "Workflow execution provenance profile and packaging", ["retrospective_provenance", "reproducibility"]),
    ("fair.principles", "The FAIR Guiding Principles for scientific data management and stewardship", "Scientific Data", "primary_research", "https://www.nature.com/articles/sdata201618", 2016, "Findability, accessibility, interoperability and reuse principles", ["reproducibility", "stewardship"]),
    ("datacite.46", "DataCite Metadata Schema 4.6", "DataCite", "official_specification", "https://schema.datacite.org/meta/kernel-4.6/", 2024, "Research resource identifiers, related identifiers, versions and dates", ["citation", "version", "identity"]),
    ("premis.30", "PREMIS Data Dictionary for Preservation Metadata 3.0", "Library of Congress PREMIS Editorial Committee", "community_standard", "https://www.loc.gov/standards/premis/v3/premis-3-0-final.pdf", 2015, "Preservation objects, events, agents and rights", ["digital_preservation", "event"]),
    ("ddi.cdi", "DDI Cross Domain Integration Specification 1.0", "DDI Alliance", "community_standard", "https://docs.ddialliance.org/CDI/1.0/", 2024, "Cross-domain data description, process and provenance integration", ["data_description", "process", "provenance"]),
    ("sdmx.30", "SDMX Information Model 3.0", "SDMX Sponsors", "international_standard", "https://docs.sdmx.org/en/3.0/information-model/", 2021, "Statistical structures, constraints, data and metadata", ["statistical_data", "structure"]),
    ("iso.19115.1", "ISO 19115-1:2014 Geographic information — Metadata", "ISO", "standard_landing_page", "https://www.iso.org/standard/53798.html", 2014, "Geospatial metadata including resource lineage concepts", ["geospatial", "lineage"]),
    ("iso.19115.2", "ISO 19115-2:2019 Geographic information — Metadata for acquisition and processing", "ISO", "standard_landing_page", "https://www.iso.org/standard/67039.html", 2019, "Acquisition and processing metadata for geospatial resources", ["acquisition", "processing", "lineage"]),
    ("omg.sacm", "Structured Assurance Case Metamodel 2.3", "Object Management Group", "standard", "https://www.omg.org/spec/SACM/2.3/About-SACM", 2024, "Claims, argumentation, artifacts, citations and assurance-case packaging", ["claim", "argument", "evidence"]),
    ("oasis.csaf", "Common Security Advisory Framework Version 2.0", "OASIS", "standard", "https://docs.oasis-open.org/csaf/csaf/v2.0/csaf-v2.0.html", 2022, "Machine-readable security advisories, product status and remediation", ["recall", "advisory", "status"]),
    ("niso.credit", "ANSI/NISO Z39.104-2022 CRediT", "NISO", "standard_landing_page", "https://www.niso.org/standards-committees/credit", 2022, "Contributor-role taxonomy for research outputs", ["agent_role", "attribution"]),
    ("nist.800.53", "NIST SP 800-53 Rev. 5 Security and Privacy Controls", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final", 2020, "Audit and accountability, integrity, retention and system controls", ["audit", "security", "retention"]),
    ("nist.800.92", "NIST SP 800-92 Guide to Computer Security Log Management", "NIST", "government_guidance", "https://www.nist.gov/publications/guide-computer-security-log-management", 2006, "Enterprise security-log management practices", ["log", "security"]),
    ("nist.800.86", "NIST SP 800-86 Guide to Integrating Forensic Techniques into Incident Response", "NIST", "government_guidance", "https://csrc.nist.gov/pubs/sp/800/86/final", 2006, "Forensic collection, examination, analysis and reporting", ["forensics", "collection", "analysis"]),
    ("nist.ir.8387", "NISTIR 8387 Digital Evidence Preservation: Considerations for Evidence Handlers", "NIST", "government_guidance", "https://www.nist.gov/publications/digital-evidence-preservation-considerations-evidence-handlers", 2022, "Digital evidence preservation and handler considerations", ["digital_evidence", "preservation", "custody"]),
    ("nist.ir.8354", "NISTIR 8354 Digital Investigation Techniques: A NIST Scientific Foundation Review", "NIST", "government_review", "https://www.nist.gov/publications/digital-investigation-techniques-nist-scientific-foundation-review", 2022, "Scientific foundations and limitations of digital investigation techniques", ["forensics", "method_validation"]),
    ("nist.fips180", "FIPS 180-4 Secure Hash Standard", "NIST", "government_standard", "https://csrc.nist.gov/pubs/fips/180-4/upd1/final", 2015, "Approved secure hash algorithms", ["digest", "integrity"]),
    ("iso.27037", "ISO/IEC 27037:2012 Guidelines for identification, collection, acquisition and preservation of digital evidence", "ISO", "standard_landing_page", "https://www.iso.org/standard/44381.html", 2012, "Digital evidence handling lifecycle", ["forensics", "custody", "preservation"]),
    ("iso.19011", "ISO 19011:2018 Guidelines for auditing management systems", "ISO", "standard_landing_page", "https://www.iso.org/standard/70017.html", 2018, "Audit-program and audit-conduct guidance", ["audit", "independent_appraisal"]),
    ("ecfr.part11", "21 CFR Part 11 Electronic Records; Electronic Signatures", "US Electronic Code of Federal Regulations", "regulation", "https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11", 2026, "US regulated electronic records, signatures and audit trails", ["regulated_record", "audit_trail", "signature"]),
    ("fda.electronic.2024", "Electronic Systems, Electronic Records, and Electronic Signatures in Clinical Investigations: Questions and Answers", "US Food and Drug Administration", "regulatory_guidance", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/electronic-systems-electronic-records-and-electronic-signatures-clinical-investigations-questions", 2024, "Trustworthy clinical electronic systems, records, signatures and audit trails", ["clinical_data", "audit_trail", "certified_copy"]),
    ("fda.data.integrity", "Data Integrity and Compliance With Drug CGMP: Questions and Answers", "US Food and Drug Administration", "regulatory_guidance", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/data-integrity-and-compliance-drug-cgmp-questions-and-answers-guidance-industry", 2018, "ALCOA-oriented regulated manufacturing data integrity", ["data_integrity", "audit_trail"]),
    ("ema.computerised", "Guideline on computerised systems and electronic data in clinical trials", "European Medicines Agency", "regulatory_guidance", "https://www.ema.europa.eu/en/documents/regulatory-procedural-guideline/guideline-computerised-systems-and-electronic-data-clinical-trials_en.pdf", 2023, "Clinical data origin, audit trail, transfer, review and archiving", ["clinical_data", "audit_trail", "origin"]),
    ("mhra.gxp", "GXP Data Integrity Guidance and Definitions", "UK Medicines and Healthcare products Regulatory Agency", "regulatory_guidance", "https://assets.publishing.service.gov.uk/media/5aa2ad0de5274a3e391e37f6/MHRA_GxP_data_integrity_guide_March_edited_Final.pdf", 2018, "Data lifecycle, metadata, audit trail and data-integrity expectations", ["data_integrity", "metadata", "audit_trail"]),
    ("sec.17a4", "SEC Rule 17a-4 Records to be preserved by certain exchange members, brokers and dealers", "US Securities and Exchange Commission", "regulation", "https://www.ecfr.gov/current/title-17/chapter-II/part-240/section-240.17a-4", 2026, "Broker-dealer record retention and electronic recordkeeping requirements", ["retention", "regulated_record"]),
    ("cftc.131", "CFTC Rule 1.31 Records; recordkeeping requirements", "US Commodity Futures Trading Commission", "regulation", "https://www.ecfr.gov/current/title-17/chapter-I/part-1/section-1.31", 2026, "Commodity regulated-record authenticity, retention and production", ["retention", "regulated_record", "disclosure"]),
]


SOURCES = [
    {
        "source_id": sid(short), "edition": EDITION, "status": "reference",
        "title": title, "publisher": publisher, "source_kind": kind, "url": url,
        "publication_year": year, "accessed_on": ACCESSED,
        "authority_scope": scope, "topics": topics,
        "limitations": ["Authority is limited to the stated scope; citation does not qualify an implementation or establish the truth of a claim."],
    }
    for short, title, publisher, kind, url, year, scope, topics in SOURCE_ROWS
]


# id, name, family, sovereign question, inside, outside, primary source shorts, neighbors
CONTEXT_ROWS = [
    ("prospective-lineage", "Prospective Lineage", "lineage", "What declared plan says may consume, transform and produce data before execution?", "Plans, declared dependencies, expected inputs/outputs and control structure.", "Observed execution and actual values.", ["w3c.prov.dm", "cwl.12"], ["retrospective-lineage", "pipeline-lineage"]),
    ("retrospective-lineage", "Retrospective Lineage", "lineage", "What actually consumed, executed and produced artifacts in a particular run?", "Observed run occurrences, actual inputs/outputs and run-scoped dependencies.", "Unexecuted plans and generalized possibility.", ["openlineage.spec", "workflow.run.crate"], ["prospective-lineage", "runtime-lineage"]),
    ("logical-lineage", "Logical Lineage", "lineage", "Which semantic datasets, fields and expressions depend on which logical predecessors?", "Provider-neutral semantic dependencies and derivation expressions.", "Files, partitions, processes and task attempts.", ["w3c.prov.dm", "openlineage.column"], ["physical-lineage", "formula-lineage"]),
    ("physical-lineage", "Physical Lineage", "lineage", "Which concrete objects, files, partitions and snapshots supplied or received bytes?", "Physical artifact identities, locations, versions and storage cuts.", "Logical meaning and causal truth inferred from co-location.", ["w3c.dcat3", "w3c.prov.dm"], ["logical-lineage", "runtime-lineage"]),
    ("runtime-lineage", "Runtime Lineage", "lineage", "Which run event connected actual jobs and datasets at runtime?", "Run states, attempts, actual IO and producer facets.", "Complete audit, observability or truth claims.", ["openlineage.spec", "openlineage.lifecycle"], ["retrospective-lineage", "runtime-receipts"]),
    ("source-lineage", "Source and Acquisition Lineage", "lineage", "From which authoritative source occurrence and acquisition act did a datum enter the analytical estate?", "Origin identity, acquisition method, source cut and handoff.", "Source-system business semantics and connector implementation.", ["iso.19115.2", "w3c.prov.dm"], ["custody", "physical-lineage"]),
    ("pipeline-lineage", "Pipeline and Workflow Lineage", "lineage", "How do orchestrated tasks, branches and retries relate across plan and execution?", "Workflow topology, task identity, attempt linkage and materialization boundaries.", "Scheduler resource allocation and transformation semantics.", ["cwl.12", "openlineage.parent"], ["prospective-lineage", "runtime-lineage"]),
    ("transformation-lineage", "Transformation Lineage", "lineage", "Which typed transform and parameters derived an output from inputs?", "Transform identity, version, parameters, input roles and information loss.", "Opaque co-occurrence or mere temporal succession.", ["w3c.prov.dm", "openlineage.column"], ["logical-lineage", "formula-lineage"]),
    ("field-lineage", "Field and Element Lineage", "lineage", "Which exact input elements influenced each output element under what transform?", "Column, field, cell, array-region and graph-element dependency.", "Dataset-only edges treated as field proof.", ["openlineage.column", "w3c.prov.dictionary"], ["transformation-lineage", "schema-lineage"]),
    ("formula-lineage", "Semantic Formula Lineage", "lineage", "Which governed formula edition and operand semantics produced a measure or feature?", "Formula AST identity, metric edition, operands, filters, units and aggregation grain.", "Textual SQL alone and model execution.", ["w3c.prov.dm", "sdmx.30"], ["logical-lineage", "model-study-lineage"]),
    ("schema-lineage", "Schema Evolution Lineage", "lineage", "How did field identities and constraints evolve across schema editions?", "Adds, drops, renames, type changes, mappings and compatibility evidence.", "Record-level value corrections.", ["openlineage.schema", "ddi.cdi"], ["field-lineage", "impact-analysis"]),
    ("model-study-lineage", "Model and Study Lineage", "lineage", "Which data, protocol, method, code, parameters and environment yielded a model or study result?", "Study plans, cohorts, model versions, evaluation sets and outputs.", "Business approval of the result.", ["rocrate.11", "workflow.run.crate"], ["reproducibility-package", "decision-action-lineage"]),
    ("decision-action-lineage", "Decision and Action Lineage", "lineage", "Which evidence and rules informed a decision, and which authorized actions followed?", "Decision occurrence, inputs considered, policy edition, authority and resulting action.", "Decision correctness inferred from provenance.", ["omg.sacm", "w3c.prov.dm"], ["claim-argument", "impact-analysis"]),
    ("security-lineage", "Security and Policy Lineage", "lineage", "Which policy, identity, key and control state governed an access or transformation?", "Policy/key editions, authorization decision references and security context.", "Security telemetry automatically elevated to proof.", ["nist.800.53", "w3c.did"], ["audit-event", "attestation"]),
    ("governance-lineage", "Governance Lineage", "lineage", "Which stewardship, classification, consent, retention and approval state applied to an asset cut?", "Governance policy and authority links over time.", "Execution mechanics and legal conclusions.", ["w3c.dcat3", "w3c.prov.dm"], ["disclosure", "retention-legal-hold"]),
    ("quality-lineage", "Quality and Validation Lineage", "lineage", "Which checks, measurements and exceptions support a quality assertion for an exact data cut?", "Quality rules, measurements, observations, scope and outcomes.", "Quality score as proof of correctness.", ["w3c.dqv", "w3c.earl"], ["claim-evidence", "runtime-receipts"]),
    ("cross-system-reconciliation", "Cross-System Lineage Reconciliation", "lineage", "When do heterogeneous identifiers and edges denote the same occurrence or relation?", "Identity crosswalks, edge reconciliation, conflicts and confidence.", "Silent graph union and source precedence by ingestion order.", ["w3c.prov.links", "openlineage.facets"], ["provenance-graph", "identity-digest"]),
    ("lineage-query", "Lineage Query and Slicing", "lineage", "Which sound bounded slice answers upstream, downstream, path and point-in-time questions?", "Traversal semantics, scope, cut, cycles, uncertainty and redaction.", "Completeness claims beyond captured coverage.", ["w3c.prov.aq", "w3c.prov.constraints"], ["impact-analysis", "provenance-graph"]),
    ("impact-analysis", "Impact Analysis", "lineage", "What may or did depend on a changing, invalidated or compromised subject?", "Prospective reachability, retrospective affected runs, semantic effect and uncertainty.", "A graph path automatically treated as business impact.", ["w3c.prov.dm", "oasis.csaf"], ["lineage-query", "recall"]),
    ("provenance-assertion", "Provenance Assertion", "provenance", "Who asserts which scoped provenance relation about which identified occurrences?", "Assertion content, asserter, basis, scope, time and qualification.", "The asserted relation automatically treated as fact.", ["w3c.prov.dm", "w3c.prov.o"], ["provenance-graph", "attestation"]),
    ("provenance-graph", "Provenance Graph", "provenance", "How are qualified entities, activities, agents and relations assembled without erasing assertion boundaries?", "Typed nodes/edges, bundles, qualifiers, conflicts and graph cuts.", "Audit log, causal proof or evidence bundle by default.", ["w3c.prov.o", "w3c.prov.constraints"], ["provenance-bundle", "lineage-query"]),
    ("provenance-bundle", "Provenance Bundle", "provenance", "Which named set of provenance descriptions is packaged, scoped and itself given provenance?", "Bundle identity, membership, issuer, encoding and bundle provenance.", "All evidence needed for a decision.", ["w3c.prov.links", "w3c.prov.o"], ["evidence-bundle", "provenance-graph"]),
    ("derivation", "Data Derivation", "provenance", "How did an entity's fixed aspects depend on another entity?", "Derivation kind, generation/use anchors, transform and qualification.", "Process execution merely because two artifacts occur in one run.", ["w3c.prov.dm", "w3c.prov.constraints"], ["activity-execution", "transformation-lineage"]),
    ("activity-execution", "Process Activity Execution", "provenance", "What activity occurrence started, ended, used, generated and associated with agents?", "Occurrence identity, interval, usage, generation, association and plan.", "Data derivation without entity-dependency evidence.", ["w3c.prov.dm", "openlineage.lifecycle"], ["derivation", "runtime-lineage"]),
    ("agent-responsibility", "Agent Responsibility and Attribution", "provenance", "Which agent bore what role or delegation for an activity or entity?", "Association, attribution, delegation, roles and authority scope.", "Moral, legal or causal blame inferred from a technical link.", ["w3c.prov.dm", "niso.credit"], ["authority", "decision-action-lineage"]),
    ("version-revision", "Version, Revision and Supersession", "provenance", "How do materially distinct editions relate without overwriting identity?", "Version identity, revision relation, supersession and effective interval.", "Correction, retraction, deletion or recall collapsed into versioning.", ["w3c.dcat3", "w3c.prov.o"], ["correction", "retraction"]),
    ("plan-execution-conformance", "Plan-to-Execution Conformance", "provenance", "Did an observed execution conform to a declared plan under explicit tolerances?", "Plan/run matching, permitted variance, violations and proof basis.", "Plan identity treated as execution evidence.", ["intoto.layout", "workflow.run.crate"], ["prospective-lineage", "runtime-receipts"]),
    ("claim", "Claim Assertion", "evidence", "What proposition is asserted, by whom, about which subject and validity interval?", "Proposition, subject, issuer, modality, scope, assertion time and validity.", "Supporting evidence or independent acceptance.", ["omg.sacm", "w3c.vc2"], ["claim-argument", "claim-evidence"]),
    ("claim-argument", "Claim-Argument Structure", "evidence", "How do explicit reasoning steps support, rebut or qualify a claim?", "Claims, reasoning, warrants, assumptions, counterclaims and argument links.", "Evidence integrity or truth supplied by graph shape.", ["omg.sacm"], ["claim", "claim-evidence"]),
    ("claim-evidence", "Claim-Evidence Binding", "evidence", "Why is an evidence item relevant to a precise claim under a declared inference rule?", "Relevance, directness, method, scope, limitations and counterevidence.", "Citation count as evidential strength.", ["omg.sacm", "w3c.webanno"], ["evidence-strength", "defeaters"]),
    ("evidence-bundle", "Evidence Bundle", "evidence", "Which immutable or versioned package supplies the materials required to assess a claim?", "Manifest, items, claims, methods, signatures, custody, validation and redaction map.", "A provenance bundle or arbitrary archive automatically treated as evidence.", ["sigstore.bundle", "ietf.rfc8493"], ["provenance-bundle", "custody"]),
    ("authority", "Evidence Authority", "evidence", "Was the issuer competent and authorized for this exact proposition, subject, time and jurisdiction?", "Issuer identity, role, mandate, competence, scope and conflicts.", "Cryptographic identity treated as authority or truth.", ["w3c.vc2", "ietf.rfc9334"], ["identity-digest", "independent-appraisal"]),
    ("evidence-strength", "Evidence Strength", "evidence", "How strong is support after directness, method, integrity, corroboration and uncertainty are assessed separately?", "Dimension scores, rationale, aggregation policy and residual uncertainty.", "One universal scalar or authority popularity.", ["omg.sacm", "nist.ir.8354"], ["claim-evidence", "defeaters"]),
    ("evidence-freshness", "Evidence Freshness and Validity", "evidence", "Is evidence current enough for this use, distinct from when it was recorded?", "Observed, recorded, valid-from/until, expires, recheck triggers and source staleness.", "Recording time equated with event or validity time.", ["w3c.owl.time", "tuf.spec"], ["credential-status", "defeaters"]),
    ("defeaters", "Defeaters and Counterevidence", "evidence", "What rebuts a claim or undercuts its evidence, authority, method or relevance?", "Rebutting and undercutting defeaters, conflicts, resolution and residual risk.", "Failed verification silently discarded.", ["omg.sacm", "w3c.earl"], ["evidence-strength", "retraction"]),
    ("attestation", "Attestation", "evidence", "Which issuer signs or otherwise binds a statement about evidence or a subject?", "Statement, predicate type, issuer, signing context, verification material and validity.", "Independent appraisal or truth of claims.", ["intoto.attestation", "ietf.rfc9334"], ["claim", "independent-appraisal"]),
    ("independent-appraisal", "Independent Appraisal", "evidence", "What verifier independently evaluated evidence against which policy for a relying party?", "Verifier identity, appraisal policy, evidence input, verdict, time and limitations.", "Self-assertion or signature verification alone.", ["ietf.rfc9334", "iso.19011"], ["attestation", "authority"]),
    ("runtime-receipts", "Runtime Receipts", "evidence", "What durable, scoped record proves a runtime mechanism accepted, executed or rejected an intent?", "Invocation identity, inputs, code/config cut, outcome, effects, resource cut and integrity.", "Transient telemetry or job-success flag alone.", ["openlineage.spec", "ietf.rfc9942"], ["compiler-receipts", "audit-event"]),
    ("compiler-receipts", "Compiler and Binding Receipts", "evidence", "Which requirements, offers, decisions and proof obligations produced an executable binding?", "Semantic input, chosen offers, proof results, degradations, refusals and artifact digest.", "Runtime execution evidence.", ["slsa.provenance", "w3c.earl"], ["runtime-receipts", "plan-execution-conformance"]),
    ("identity-digest", "Identity, Canonicalization and Digest", "evidence", "Do identifiers and digests bind the exact bytes or abstract graph claimed?", "Identity scheme, canonicalization, digest algorithm, scope and collision posture.", "Digest equality treated as semantic identity or truth.", ["w3c.rdf.canon", "nist.fips180"], ["signature-seal", "cross-system-reconciliation"]),
    ("signature-seal", "Signature and Seal", "evidence", "Who controlled the verification key when a canonical payload was signed, and under which policy?", "Envelope, payload type, key reference, algorithm, verification result and key status.", "Signer authority, claim truth or safe time inferred from a valid signature.", ["intoto.dsse", "w3c.vc.integrity"], ["identity-digest", "attestation"]),
    ("transparency-registration", "Transparency Registration", "evidence", "Was an identified statement included in an append-only verifiable structure at a witnessed tree state?", "Registration, inclusion/consistency proof, service identity, checkpoint and gossip evidence.", "Truth of the registered statement.", ["ietf.rfc9942", "ietf.rfc9943"], ["signature-seal", "evidence-freshness"]),
    ("credential-status", "Credential and Attestation Status", "evidence", "Is a credential suspended, revoked, expired or otherwise invalid for the relying use?", "Status mechanism, retrieval time, purpose, cache and fail-closed policy.", "Absence from one status list as universal validity.", ["w3c.vc.status", "tuf.spec"], ["evidence-freshness", "recall"]),
    ("audit-event", "Audit Event", "audit", "What security- or accountability-relevant action was recorded with actor, object, outcome and time?", "Typed event occurrence, actor, target, action, outcome and recording context.", "Provenance edge or legal evidence automatically.", ["nist.800.53", "ietf.rfc5424"], ["audit-log", "runtime-receipts"]),
    ("audit-log", "Audit Log", "audit", "How are audit events transported, stored, protected, retained and searched?", "Log sequence, source, collection, normalization, protection and retention.", "Complete provenance graph or admissible evidence.", ["nist.800.92", "otel.logs"], ["audit-event", "audit-trail"]),
    ("audit-trail", "Audit Trail Reconstruction", "audit", "Can the creation, modification and deletion history of a governed record be reconstructed?", "Prior/current value, actor, action, reason, timestamp and protected sequence.", "All operational logs or causal lineage.", ["ecfr.part11", "ema.computerised"], ["audit-log", "correction"]),
    ("custody", "Chain of Custody", "custody", "Who possessed or controlled evidence across each transfer, and was continuity verified?", "Custodian, transfer, seal/digest, time, purpose, condition and exception.", "Provenance responsibility or access log alone.", ["iso.27037", "nist.ir.8387"], ["forensic-acquisition", "evidence-bundle"]),
    ("forensic-acquisition", "Forensic Acquisition", "custody", "How was a source acquired without unrecorded alteration and with repeatable verification?", "Authority, source state, method/tool version, write protection, image, digest and exceptions.", "Ordinary ingestion or backup.", ["nist.800.86", "iso.27037"], ["custody", "forensic-preservation"]),
    ("forensic-preservation", "Forensic Preservation", "custody", "How is evidentiary material kept authentic, intelligible and verifiable over time?", "Preservation actions, fixity, format, media, migration, access and validation.", "Availability backup alone.", ["nist.ir.8387", "premis.30"], ["long-term-validation", "retention-legal-hold"]),
    ("long-term-validation", "Long-Term Evidence Validation", "custody", "How can signatures and digests remain assessable after algorithm, key or certificate expiry?", "Evidence records, archive timestamps, renewal chains and algorithm migration.", "Perpetual truth or authorization.", ["ietf.rfc4998", "ietf.rfc6283"], ["forensic-preservation", "signature-seal"]),
    ("retention-legal-hold", "Retention and Legal Hold", "governance", "Which records must be retained, frozen, disposed or exempted under scoped authority?", "Schedule, trigger, jurisdiction, hold, disposition review and destruction receipt.", "Business correction, retraction or privacy erasure automatically.", ["sec.17a4", "cftc.131"], ["deletion-erasure", "forensic-preservation"]),
    ("disclosure", "Evidence Disclosure and Redaction", "governance", "Which evidence may be disclosed to whom, with what minimization and verifiable omissions?", "Audience, purpose, authorization, redaction map, selective disclosure and disclosure receipt.", "Deletion of source evidence or implication that undisclosed material is absent.", ["w3c.vc2", "cftc.131"], ["evidence-bundle", "retention-legal-hold"]),
    ("reproducibility-package", "Reproducibility Package", "reproducibility", "Which data, code, workflow, environment, parameters and results permit a qualified rerun?", "Manifested research object, identifiers, licenses, dependencies and run instructions.", "Guarantee that rerun results will be identical.", ["rocrate.11", "ietf.rfc8493"], ["environment-capture", "reproduction-appraisal"]),
    ("environment-capture", "Environment and Dependency Capture", "reproducibility", "Which software, hardware, configuration and external-service cuts conditioned a result?", "Dependency graph, image/package identity, target, environment variables and service versions.", "Business method or data authority.", ["slsa.provenance", "workflow.run.crate"], ["reproducibility-package", "compiler-receipts"]),
    ("protocol-method", "Protocol and Method Provenance", "reproducibility", "Which preregistered or governed method edition, assumptions and deviations applied?", "Protocol, method steps, sampling, exclusions, deviations and approvals.", "Observed execution automatically conforms to the method.", ["rocrate.11", "omg.sacm"], ["plan-execution-conformance", "model-study-lineage"]),
    ("reproduction-appraisal", "Reproduction and Replication Appraisal", "reproducibility", "Did an independent rerun or new study reproduce a result under declared equivalence?", "Original claim, rerun inputs, environment, equivalence rule, result and divergence analysis.", "Same digest required for all scientifically equivalent results.", ["fair.principles", "nist.ir.8354"], ["reproducibility-package", "independent-appraisal"]),
    ("correction", "Correction", "lifecycle", "How is erroneous content amended while preserving original state and reason?", "Corrected edition, affected scope, authority, reason, effective time and links to prior state.", "Deletion, retraction or recall.", ["fda.electronic.2024", "w3c.dcat3"], ["version-revision", "audit-trail"]),
    ("retraction", "Retraction", "lifecycle", "How is a claim or publication withdrawn from reliance without erasing history?", "Retracted subject, notice, authority, reason, effective time and replacement if any.", "Physical deletion or product recall.", ["w3c.vc.status", "datacite.46"], ["claim", "recall"]),
    ("recall", "Recall and Downstream Notification", "lifecycle", "Which distributed artifacts, decisions or actions must stop being used after a defect or compromise?", "Affected identity/range, severity, action, notification, acknowledgement and closure.", "Retraction of a scholarly claim or deletion.", ["oasis.csaf", "w3c.prov.dm"], ["impact-analysis", "credential-status"]),
    ("deletion-erasure", "Deletion, Erasure and Tombstoning", "lifecycle", "What is removed, rendered inaccessible or tombstoned, under whose authority and with which retained proof?", "Deletion scope, physical/logical behavior, replicas, exceptions and minimal receipt.", "Correction, retraction, recall or assured physical destruction without proof.", ["nist.800.53", "sec.17a4"], ["retention-legal-hold", "correction"]),
]


CONTEXTS = []
for cid, name, family, question, inside, outside, evidence, neighbors in CONTEXT_ROWS:
    CONTEXTS.append({
        "context_id": f"context.lpe.{cid}", "edition": EDITION, "status": "candidate",
        "name": name, "family": family, "sovereign_question": question,
        "inside": [inside], "outside": [outside],
        "invariants": ["Unknown coverage, authority or semantics remains explicit.", "No record in this context is qualified merely by enumeration."],
        "neighbor_context_refs": [f"context.lpe.{ref}" for ref in neighbors],
        "evidence_refs": [sid(ref) for ref in evidence],
        "cross_plane_refs": [],
        "gaps": ["Candidate boundary requires strategic DDD adjudication and independent review."],
    })


# id, family, definition, identity rule, mutable?, primary context, source shorts
ENTITY_ROWS = [
    ("data-entity", "provenance", "An identifiable physical, digital or conceptual thing with fixed aspects for the described cut.", "Identifier plus version/cut; a material change creates a distinct entity state.", False, "provenance-graph", ["w3c.prov.dm"]),
    ("activity-occurrence", "provenance", "An occurrence that acts on or with entities over an interval.", "Occurrence identifier, not merely activity type or plan name.", False, "activity-execution", ["w3c.prov.dm"]),
    ("agent", "provenance", "A person, organization or software agent bearing scoped responsibility.", "Authority-scoped agent identifier and identity scheme.", True, "agent-responsibility", ["w3c.prov.dm"]),
    ("plan", "provenance", "An intended set of steps or actions used by an activity.", "Plan identifier plus immutable edition.", False, "prospective-lineage", ["w3c.prov.o"]),
    ("usage", "provenance", "Qualified use of an entity by an activity occurrence.", "Activity, entity, role and occurrence/time qualifier.", False, "activity-execution", ["w3c.prov.dm"]),
    ("generation", "provenance", "Qualified generation of an entity by an activity occurrence.", "Entity generation event; at most one generation for one PROV entity cut.", False, "activity-execution", ["w3c.prov.constraints"]),
    ("derivation-record", "provenance", "Qualified assertion that one entity was derived from another.", "Generated entity, used entity, kind, assertion issuer and bundle.", False, "derivation", ["w3c.prov.dm"]),
    ("association", "provenance", "Qualified responsibility link between activity, agent, plan and role.", "Activity occurrence, agent, role and plan.", False, "agent-responsibility", ["w3c.prov.dm"]),
    ("provenance-assertion", "provenance", "An issuer-scoped assertion of one or more provenance propositions.", "Assertion identifier, issuer, issuance time and immutable proposition payload.", False, "provenance-assertion", ["w3c.prov.dm"]),
    ("provenance-bundle", "provenance", "A named set of provenance descriptions that can itself have provenance.", "Bundle identifier and exact member-set edition.", False, "provenance-bundle", ["w3c.prov.o"]),
    ("lineage-edge", "lineage", "A typed, directed, qualified dependency candidate between identified subjects.", "Source, target, relation kind, scope, assertion and valid cut.", False, "logical-lineage", ["openlineage.spec"]),
    ("lineage-observation", "lineage", "An observation from a producer that an edge or node occurred in a run.", "Producer, event id, observed subject and recording time.", False, "runtime-lineage", ["openlineage.spec"]),
    ("dataset", "lineage", "A logical collection of data addressed in a lineage event.", "Namespace, name and optional version/facet cut.", True, "logical-lineage", ["openlineage.spec"]),
    ("dataset-version", "lineage", "An immutable or declared edition/cut of a dataset.", "Dataset identity plus version, snapshot, transaction or content cut.", False, "version-revision", ["w3c.dcat3"]),
    ("distribution", "lineage", "An accessible representation of a dataset in a format.", "Distribution identifier, media/format and versioned access cut.", True, "physical-lineage", ["w3c.dcat3"]),
    ("field", "lineage", "A schema-addressable element with stable identity within a dataset edition.", "Stable field id where available; otherwise qualified path plus schema edition.", True, "field-lineage", ["openlineage.schema"]),
    ("formula-edition", "lineage", "A governed, immutable semantic expression with operand roles and result contract.", "Formula identity plus AST digest and semantic edition.", False, "formula-lineage", ["sdmx.30"]),
    ("transform-edition", "lineage", "A typed transformation definition, independent of any one execution.", "Transform identifier, source/code edition, parameter schema and semantic contract.", False, "transformation-lineage", ["openlineage.column"]),
    ("workflow-edition", "lineage", "A prospective workflow graph and tool binding specification.", "Workflow identifier plus immutable definition digest/edition.", False, "pipeline-lineage", ["cwl.12"]),
    ("run", "lineage", "A single workflow, job, study or computation execution occurrence.", "Globally scoped run identifier distinct from retry/attempt identifiers.", False, "runtime-lineage", ["openlineage.spec"]),
    ("run-attempt", "lineage", "One attempt to perform a run or task, including failed and abandoned attempts.", "Run id plus attempt id/ordinal; never overwritten by retry.", False, "runtime-lineage", ["openlineage.lifecycle"]),
    ("run-event", "lineage", "A producer-emitted lifecycle observation about a run.", "Event id or canonical producer/run/event-time tuple with deduplication posture.", False, "runtime-lineage", ["openlineage.lifecycle"]),
    ("source-occurrence", "lineage", "An exact source-system occurrence or read cut used for acquisition.", "Source authority, object, version/offset/snapshot and occurrence time.", False, "source-lineage", ["iso.19115.2"]),
    ("schema-edition", "lineage", "An immutable schema definition at one semantic/compatibility cut.", "Schema identity plus edition or canonical digest.", False, "schema-lineage", ["openlineage.schema"]),
    ("study", "reproducibility", "A governed investigation with protocol, population, methods and outputs.", "Study registration/organizational identifier plus edition.", True, "model-study-lineage", ["rocrate.11"]),
    ("model-artifact", "reproducibility", "A fitted or otherwise produced analytical model artifact, excluding generative-model semantics from the core.", "Model family/name plus immutable artifact and training-run cut.", False, "model-study-lineage", ["rocrate.11"]),
    ("decision-occurrence", "lineage", "An occurrence in which an authorized actor selects a disposition using declared inputs.", "Decision id, authority, subject and occurrence time.", False, "decision-action-lineage", ["omg.sacm"]),
    ("action-occurrence", "lineage", "An authorized effect or intervention following a decision or rule.", "Action id, actor, target, command and occurrence/outcome.", False, "decision-action-lineage", ["w3c.prov.dm"]),
    ("claim", "evidence", "A proposition asserted about a subject with modality and scope.", "Claim identifier plus canonical proposition edition; issuer assertions remain separate.", True, "claim", ["omg.sacm"]),
    ("argument", "evidence", "An explicit reasoning structure linking claims, evidence and warrants.", "Argument identifier and immutable argument edition.", False, "claim-argument", ["omg.sacm"]),
    ("warrant", "evidence", "A declared inference rule explaining why evidence supports a claim.", "Warrant identity plus rule edition and applicability scope.", False, "claim-argument", ["omg.sacm"]),
    ("evidence-item", "evidence", "An identified item offered in support of or against a claim.", "Evidence identifier, exact content/record cut and custody reference.", False, "claim-evidence", ["omg.sacm"]),
    ("evidence-bundle", "evidence", "A manifested package of evidence items, claims, methods and verification material.", "Bundle manifest identity and member digests.", False, "evidence-bundle", ["sigstore.bundle"]),
    ("assertion", "evidence", "An agent's act of putting forward a proposition, independent of proof or signature.", "Issuer, proposition, assertion occurrence and scope.", False, "claim", ["w3c.vc2"]),
    ("attestation", "evidence", "An authenticated statement using a typed predicate about one or more subjects.", "Statement envelope, predicate type, subject identities and issuer.", False, "attestation", ["intoto.attestation"]),
    ("appraisal-policy", "evidence", "A versioned policy used by a verifier to appraise evidence.", "Policy identity, edition, trust anchors and rule set.", False, "independent-appraisal", ["ietf.rfc9334"]),
    ("appraisal-result", "evidence", "A verifier's scoped result after applying appraisal policy to evidence.", "Verifier, evidence cut, policy edition, result and appraisal time.", False, "independent-appraisal", ["ietf.rfc9334"]),
    ("defeater", "evidence", "A rebutting or undercutting reason that weakens or defeats reliance.", "Target claim/support edge, defeater kind, issuer and evidence basis.", True, "defeaters", ["omg.sacm"]),
    ("counterevidence", "evidence", "Evidence offered against a claim or its support relation.", "Evidence item identity plus targeted claim/support edge.", False, "defeaters", ["omg.sacm"]),
    ("runtime-receipt", "evidence", "A durable scoped outcome record emitted by a runtime mechanism.", "Invocation, mechanism edition, outcome, effect summary and immutable receipt id.", False, "runtime-receipts", ["ietf.rfc9942"]),
    ("compiler-receipt", "evidence", "A durable record of semantic closure, requirement/offer binding and proof outcomes.", "Compilation identity, input contract cut and output artifact identity.", False, "compiler-receipts", ["slsa.provenance"]),
    ("content-digest", "integrity", "A digest of exact bytes or a specifically canonicalized abstract value.", "Algorithm identifier, canonicalization identifier, scope and digest bytes.", False, "identity-digest", ["nist.fips180"]),
    ("signature", "integrity", "A cryptographic signature over a typed canonical payload.", "Signature value, algorithm, verification method and payload binding.", False, "signature-seal", ["w3c.vc.integrity"]),
    ("verification-method", "integrity", "A key or other method used to verify a proof at a point in time.", "Method identifier, controller, key material edition and valid interval.", True, "signature-seal", ["w3c.did"]),
    ("transparency-checkpoint", "integrity", "A signed commitment to the state of a verifiable data structure.", "Transparency service, tree size/root, signature and checkpoint time.", False, "transparency-registration", ["ietf.rfc9162"]),
    ("inclusion-receipt", "integrity", "Proof that an identified statement was registered in a verifiable structure.", "Statement digest, service, tree state and proof path.", False, "transparency-registration", ["ietf.rfc9942"]),
    ("status-entry", "evidence", "A time-sensitive status indication for a credential or attestation.", "Status list identity, index/purpose, list edition and retrieval time.", True, "credential-status", ["w3c.vc.status"]),
    ("audit-event", "audit", "A typed accountability event with actor, target, action, outcome and time.", "Origin, event identifier/sequence and occurrence time.", False, "audit-event", ["nist.800.53"]),
    ("audit-log", "audit", "A managed sequence or collection of audit events.", "Log source and epoch/stream identity, with explicit sequence coverage.", True, "audit-log", ["nist.800.92"]),
    ("audit-trail-entry", "audit", "A protected record of creation, modification or deletion of a governed value.", "Record/field, transition, actor and committed sequence/time.", False, "audit-trail", ["ecfr.part11"]),
    ("custody-event", "custody", "A transfer, receipt, access, seal, unseal or disposition occurrence affecting evidence custody.", "Evidence item, custodian transition, time and event id.", False, "custody", ["iso.27037"]),
    ("forensic-image", "custody", "A bit-preserving acquisition artifact produced under a documented method.", "Source occurrence, image identity, acquisition method and digests.", False, "forensic-acquisition", ["nist.800.86"]),
    ("preservation-event", "custody", "An action affecting long-term preservation, such as migration, fixity check or media refresh.", "Object, event type, tool/method, outcome and time.", False, "forensic-preservation", ["premis.30"]),
    ("evidence-record", "custody", "A long-term validation record containing archive timestamps and renewal chains.", "Protected object set, archive timestamp sequence and edition.", False, "long-term-validation", ["ietf.rfc4998"]),
    ("legal-hold", "governance", "An authority-scoped suspension of ordinary disposition for identified records.", "Matter/authority, scope, start, status and release event.", True, "retention-legal-hold", ["sec.17a4"]),
    ("disclosure-package", "governance", "A purpose- and audience-scoped evidence view with declared omissions and redactions.", "Request, authorization, exact disclosed artifacts and package digest.", False, "disclosure", ["w3c.vc2"]),
    ("redaction-map", "governance", "A map from source material to withheld, transformed or disclosed regions and reasons.", "Source edition, disclosure package, region selectors and authorization.", False, "disclosure", ["w3c.webanno"]),
    ("reproducibility-package", "reproducibility", "A packaged research or analytical object sufficient for a stated reproduction target.", "Manifest, subject result, package edition and content digests.", False, "reproducibility-package", ["rocrate.11"]),
    ("environment-snapshot", "reproducibility", "A recorded cut of software, hardware, configuration and dependency state.", "Environment id, capture time, dependency graph and target identity.", False, "environment-capture", ["slsa.provenance"]),
    ("reproduction-run", "reproducibility", "An independently identified rerun intended to test a prior result.", "Original target claim, run identity, equivalence policy and environment.", False, "reproduction-appraisal", ["workflow.run.crate"]),
    ("correction-notice", "lifecycle", "A notice that identified content was erroneous and has a corrected replacement or annotation.", "Issuer, subject edition, notice time and correction scope.", False, "correction", ["fda.electronic.2024"]),
    ("retraction-notice", "lifecycle", "A notice withdrawing a claim or resource from reliance while preserving history.", "Issuer authority, retracted subject, reason and effective time.", False, "retraction", ["datacite.46"]),
    ("recall-notice", "lifecycle", "A notice requiring downstream users to stop, replace, quarantine or review affected artifacts/actions.", "Issuer, affected identity/range, severity and notice edition.", True, "recall", ["oasis.csaf"]),
    ("deletion-receipt", "lifecycle", "A minimal record of an authorized deletion attempt and its verified scope/outcome.", "Request, authority, target cut, mechanism, outcome and exception set.", False, "deletion-erasure", ["nist.800.53"]),
]


ENTITIES = [
    {
        "entity_type_id": f"entity-type.lpe.{eid}", "edition": EDITION, "status": "candidate",
        "name": eid.replace("-", " ").title(), "family": family, "definition": definition,
        "identity_rule": identity_rule, "mutable_reference": mutable,
        "owner_context_ref": f"context.lpe.{context}", "evidence_refs": [sid(ref) for ref in evidence],
        "invalid_inferences": ["Presence or integrity of this entity type does not establish the truth, completeness or authority of its content."],
    }
    for eid, family, definition, identity_rule, mutable, context, evidence in ENTITY_ROWS
]


# id, source type, target type, meaning, invalid inference, owner, source shorts
RELATION_ROWS = [
    ("was-derived-from", "data-entity", "data-entity", "The source entity contributed to derivation of the target entity.", "Temporal precedence alone is insufficient.", "derivation", ["w3c.prov.dm"]),
    ("was-generated-by", "data-entity", "activity-occurrence", "The target occurrence generated the source entity.", "Generation does not imply correctness.", "activity-execution", ["w3c.prov.dm"]),
    ("used", "activity-occurrence", "data-entity", "The source occurrence used the target entity in a qualified role.", "Availability to a process is not use.", "activity-execution", ["w3c.prov.dm"]),
    ("was-associated-with", "activity-occurrence", "agent", "The activity had a scoped association with the agent.", "Association is not blame or sole causation.", "agent-responsibility", ["w3c.prov.dm"]),
    ("was-attributed-to", "data-entity", "agent", "The entity was attributed to the agent under a role.", "Attribution is not authorship or truth.", "agent-responsibility", ["w3c.prov.dm"]),
    ("acted-on-behalf-of", "agent", "agent", "One agent acted with scoped delegation from another.", "Delegation scope must not be generalized.", "agent-responsibility", ["w3c.prov.dm"]),
    ("had-plan", "activity-occurrence", "plan", "The activity occurrence was associated with a prospective plan.", "The occurrence need not have conformed.", "plan-execution-conformance", ["w3c.prov.dm"]),
    ("specialization-of", "data-entity", "data-entity", "The source presents more specific aspects of the target general entity.", "Specialization is not arbitrary version order.", "version-revision", ["w3c.prov.dm"]),
    ("alternate-of", "data-entity", "data-entity", "Two entities present aspects of the same thing.", "Alternates need not be byte- or value-equal.", "cross-system-reconciliation", ["w3c.prov.dm"]),
    ("was-revision-of", "data-entity", "data-entity", "The source is a substantial revised edition of the target.", "Revision does not state correction or validity.", "version-revision", ["w3c.prov.o"]),
    ("had-primary-source", "data-entity", "data-entity", "The source cites a preceding entity with direct experience or knowledge.", "Primary source status is scoped, not truth.", "source-lineage", ["w3c.prov.o"]),
    ("had-member", "provenance-bundle", "provenance-assertion", "The target assertion belongs to the source bundle edition.", "Membership does not endorse the assertion.", "provenance-bundle", ["w3c.prov.o"]),
    ("declared-input", "workflow-edition", "dataset", "The workflow plan declares the dataset role as an input.", "Declared input is not observed use.", "prospective-lineage", ["cwl.12"]),
    ("declared-output", "workflow-edition", "dataset", "The workflow plan declares the dataset role as an output.", "Declared output is not observed generation.", "prospective-lineage", ["cwl.12"]),
    ("observed-input", "run", "dataset-version", "The run event identifies this exact or qualified dataset cut as input.", "Producer observation can be incomplete or wrong.", "retrospective-lineage", ["openlineage.spec"]),
    ("observed-output", "run", "dataset-version", "The run event identifies this dataset cut as output.", "Output listing is not successful durable commit proof.", "retrospective-lineage", ["openlineage.spec"]),
    ("parent-run", "run", "run", "The source run is hierarchically nested under or launched by the target run.", "Parentage is not data derivation.", "pipeline-lineage", ["openlineage.parent"]),
    ("retry-of", "run-attempt", "run-attempt", "The source attempt retries the target attempt under the same run intent.", "Retries are not the same occurrence.", "runtime-lineage", ["openlineage.lifecycle"]),
    ("field-depends-on", "field", "field", "An output field semantically depends on an input field under a declared transform.", "Dataset co-occurrence cannot establish field dependency.", "field-lineage", ["openlineage.column"]),
    ("computed-by-formula", "field", "formula-edition", "The field value semantics are governed by the formula edition.", "Text equality is not semantic formula identity.", "formula-lineage", ["sdmx.30"]),
    ("conforms-to-schema", "dataset-version", "schema-edition", "The dataset cut was validated or declared against the schema edition.", "Declaration and validation must remain distinguishable.", "schema-lineage", ["openlineage.schema"]),
    ("materialized-as", "dataset-version", "distribution", "The logical dataset cut is represented by a physical distribution.", "One distribution is not necessarily complete.", "physical-lineage", ["w3c.dcat3"]),
    ("acquired-from", "dataset-version", "source-occurrence", "The dataset cut was acquired from the exact source occurrence.", "Source occurrence does not imply authoritative business truth.", "source-lineage", ["iso.19115.2"]),
    ("informed-decision", "evidence-item", "decision-occurrence", "The evidence item was considered in the decision occurrence.", "Consideration does not mean decisive support.", "decision-action-lineage", ["omg.sacm"]),
    ("authorized-action", "decision-occurrence", "action-occurrence", "The decision occurrence authorized the action occurrence.", "Authorization is not proof the action completed.", "decision-action-lineage", ["w3c.prov.dm"]),
    ("asserts-claim", "assertion", "claim", "The assertion puts forward the target claim.", "Assertion is neither attestation nor appraisal.", "claim", ["w3c.vc2"]),
    ("supports", "evidence-item", "claim", "The evidence item supports the claim under an explicit warrant and scope.", "Citation alone is insufficient support.", "claim-evidence", ["omg.sacm"]),
    ("rebuts", "counterevidence", "claim", "The counterevidence directly supports the negation or incompatibility of the claim.", "Conflict must not be silently resolved.", "defeaters", ["omg.sacm"]),
    ("undercuts", "defeater", "evidence-item", "The defeater weakens authority, method, relevance, integrity or custody of support.", "Undercutting evidence need not prove the claim false.", "defeaters", ["omg.sacm"]),
    ("has-warrant", "argument", "warrant", "The argument uses the warrant to connect evidence and claims.", "A warrant does not validate its premises.", "claim-argument", ["omg.sacm"]),
    ("packages-evidence", "evidence-bundle", "evidence-item", "The bundle manifest includes the exact evidence item.", "Packaging is not endorsement.", "evidence-bundle", ["sigstore.bundle"]),
    ("attests-to", "attestation", "claim", "The attestation issuer authenticates a typed statement containing the claim.", "Authentication is not independent appraisal or truth.", "attestation", ["intoto.attestation"]),
    ("appraises", "appraisal-result", "attestation", "The appraisal result evaluates the attestation/evidence under a versioned policy.", "Signature validity alone is not a positive appraisal.", "independent-appraisal", ["ietf.rfc9334"]),
    ("uses-appraisal-policy", "appraisal-result", "appraisal-policy", "The appraisal applied the exact policy edition.", "Policy identity is not policy suitability.", "independent-appraisal", ["ietf.rfc9334"]),
    ("secured-by", "attestation", "signature", "The attestation payload is bound by the signature envelope.", "Valid signature does not establish issuer authority.", "signature-seal", ["w3c.vc.integrity"]),
    ("digest-of", "content-digest", "data-entity", "The digest covers the exact declared representation of the entity.", "Digest equality is not truth or abstract semantic equality.", "identity-digest", ["nist.fips180"]),
    ("verified-with", "signature", "verification-method", "The signature was verified using the method at a declared time and status cut.", "Control of a key at another time is not implied.", "signature-seal", ["w3c.did"]),
    ("included-at", "inclusion-receipt", "transparency-checkpoint", "The receipt proves inclusion at the checkpoint tree state.", "Inclusion does not prove statement truth.", "transparency-registration", ["ietf.rfc9942"]),
    ("has-status", "attestation", "status-entry", "The attestation or credential refers to a status entry.", "Cached status is not indefinitely current.", "credential-status", ["w3c.vc.status"]),
    ("emitted-receipt", "activity-occurrence", "runtime-receipt", "The runtime activity emitted a durable scoped receipt.", "Receipt emission does not imply successful outcome.", "runtime-receipts", ["ietf.rfc9942"]),
    ("compiled-to", "compiler-receipt", "data-entity", "The compiler receipt identifies the produced executable/plan artifact.", "Artifact identity does not prove runtime use.", "compiler-receipts", ["slsa.provenance"]),
    ("records-audit-event", "audit-log", "audit-event", "The log includes the event within a declared sequence/coverage cut.", "Presence in a mutable log is not durable evidence.", "audit-log", ["nist.800.92"]),
    ("reconstructs-change", "audit-trail-entry", "data-entity", "The trail entry records a governed state transition for the entity/value.", "Audit trail reconstruction is not derivation lineage.", "audit-trail", ["ecfr.part11"]),
    ("transferred-custody", "custody-event", "evidence-item", "The custody event records a transfer or receipt of the item.", "A system access event alone is not custody transfer.", "custody", ["iso.27037"]),
    ("acquired-as", "source-occurrence", "forensic-image", "The exact source occurrence was acquired as the forensic image.", "Ordinary copy does not meet forensic acquisition requirements.", "forensic-acquisition", ["nist.800.86"]),
    ("preserved-by", "evidence-item", "preservation-event", "The preservation event acted on the evidence item with recorded outcome.", "Migration must not erase prior identity or validation history.", "forensic-preservation", ["premis.30"]),
    ("renews-validation", "evidence-record", "evidence-record", "A newer evidence record renews long-term validation for an earlier protected set.", "Renewal does not retroactively repair a compromised chain.", "long-term-validation", ["ietf.rfc4998"]),
    ("subject-to-hold", "data-entity", "legal-hold", "The entity falls within the legal-hold scope for the interval.", "Hold does not settle ownership or admissibility.", "retention-legal-hold", ["sec.17a4"]),
    ("discloses", "disclosure-package", "evidence-item", "The package discloses the exact item or a declared transformed view.", "Non-membership does not prove withholding or absence.", "disclosure", ["w3c.vc2"]),
    ("redacts", "redaction-map", "evidence-item", "The map identifies portions withheld or transformed for disclosure.", "Redaction must not be described as deletion of the source.", "disclosure", ["w3c.webanno"]),
    ("packages-environment", "reproducibility-package", "environment-snapshot", "The package includes or identifies the environment snapshot.", "Environment capture does not guarantee rerun availability.", "reproducibility-package", ["rocrate.11"]),
    ("reproduces", "reproduction-run", "claim", "The run tests the target claim under a declared equivalence policy.", "A successful execution is not automatically a successful reproduction.", "reproduction-appraisal", ["workflow.run.crate"]),
    ("corrects", "correction-notice", "data-entity", "The notice identifies erroneous scope and corrected replacement/annotation.", "Correction does not erase the original.", "correction", ["fda.electronic.2024"]),
    ("retracts", "retraction-notice", "claim", "The notice withdraws the claim from reliance.", "Retraction is not deletion or recall.", "retraction", ["datacite.46"]),
    ("recalls", "recall-notice", "data-entity", "The notice requires downstream disposition of affected artifact identities/ranges.", "Recall is not a statement that all copies were removed.", "recall", ["oasis.csaf"]),
    ("deleted-under", "deletion-receipt", "data-entity", "The receipt reports the result of an authorized deletion operation.", "A success flag without replica/scope proof is not assured erasure.", "deletion-erasure", ["nist.800.53"]),
    ("supersedes", "data-entity", "data-entity", "The source edition becomes preferred for future reliance over the target.", "Supersession does not state that the target was wrong.", "version-revision", ["w3c.dcat3"]),
    ("invalidates", "defeater", "appraisal-result", "The defeater invalidates or narrows a prior appraisal result.", "Invalidation must retain prior history.", "defeaters", ["ietf.rfc9334"]),
    ("affected-by", "data-entity", "recall-notice", "Impact analysis places the entity in the notice's candidate affected set.", "Reachability is not confirmed impact.", "impact-analysis", ["oasis.csaf"]),
]


RELATIONS = [
    {
        "relation_type_id": f"relation-type.lpe.{rid}", "edition": EDITION, "status": "candidate",
        "name": rid.replace("-", " ").title(),
        "source_entity_type_ref": f"entity-type.lpe.{source}",
        "target_entity_type_ref": f"entity-type.lpe.{target}",
        "meaning": meaning, "invalid_inference": invalid,
        "owner_context_ref": f"context.lpe.{owner}",
        "qualifiers": ["assertion_or_observation_ref", "role_or_kind", "valid_or_event_time", "scope", "confidence_or_gap"],
        "evidence_refs": [sid(ref) for ref in evidence],
    }
    for rid, source, target, meaning, invalid, owner, evidence in RELATION_ROWS
]


# Each family has a concrete operation surface.  Names are intentionally narrower than broad
# verbs such as "track" or "audit" so failure, time and evidence obligations can be attached.
OPERATION_FAMILIES = {
    "lineage-capture": [
        ("declare-plan-dependencies", "Record typed inputs, outputs and dependency roles from a versioned plan without claiming execution."),
        ("observe-run-inputs", "Record actual run-scoped input dataset cuts and producer observation metadata."),
        ("observe-run-outputs", "Record actual run-scoped output dataset cuts without inferring durable commit."),
        ("capture-logical-edge", "Create a provider-neutral semantic dependency edge with assertion scope."),
        ("capture-physical-edge", "Relate concrete objects, snapshots, files or partitions involved in an occurrence."),
        ("capture-field-edge", "Relate exact input and output elements with transformation kind and confidence."),
        ("capture-formula-dependency", "Bind a result field to formula edition, operand roles, filters, units and grain."),
        ("capture-schema-transition", "Record field-identity-aware schema change and compatibility posture."),
        ("capture-source-acquisition", "Bind an ingested cut to its exact source occurrence and acquisition act."),
        ("capture-policy-context", "Attach policy, consent, classification, key and authorization editions to a governed occurrence."),
        ("deduplicate-lineage-event", "Recognize duplicate producer events under an explicit idempotency key and conflict law."),
        ("quarantine-ambiguous-lineage", "Preserve an edge as unresolved when identity, direction, time or semantics are ambiguous."),
    ],
    "provenance-graph": [
        ("assert-provenance-relation", "Issue a scoped provenance assertion without elevating it to accepted fact."),
        ("qualify-provenance-relation", "Attach role, plan, event, activity and time qualifiers to a relation."),
        ("construct-provenance-bundle", "Package a named exact set of provenance assertions with bundle provenance."),
        ("link-provenance-bundles", "Create cross-bundle references while retaining the original assertion namespaces."),
        ("validate-prov-constraints", "Evaluate ordering, uniqueness and inference constraints against a graph cut."),
        ("normalize-provenance-graph", "Normalize a graph under declared identifier and serialization rules."),
        ("merge-provenance-graphs", "Merge graphs only after identity, authority and conflict rules are selected."),
        ("slice-provenance-graph", "Return a bounded, redaction-aware graph slice with capture-coverage caveats."),
        ("diff-provenance-cuts", "Compute node, edge, qualifier and assertion changes between exact graph cuts."),
        ("infer-qualified-relation", "Apply a named sound inference rule and retain the derivation of the inferred edge."),
        ("retract-provenance-assertion", "Mark an issuer assertion withdrawn while preserving its history and graph impact."),
        ("export-provenance-interchange", "Serialize a graph/bundle with namespace, profile and loss report."),
    ],
    "identity-integrity": [
        ("resolve-entity-identity", "Resolve an identifier under an explicit scheme, authority, time and version cut."),
        ("mint-occurrence-identity", "Mint an occurrence identifier distinct from type, plan and retry identifiers."),
        ("canonicalize-json", "Produce RFC 8785 canonical bytes or fail on unsupported input."),
        ("canonicalize-rdf", "Produce RDFC-1.0 canonical form with complexity limits and algorithm identifier."),
        ("compute-content-digest", "Compute a named-algorithm digest over explicitly scoped bytes or canonical form."),
        ("verify-content-digest", "Compare recomputed and expected digests with algorithm/status reporting."),
        ("create-signature-envelope", "Bind payload type and canonical payload to a signing operation."),
        ("verify-signature-envelope", "Verify integrity, payload type, algorithm and verification method at a time cut."),
        ("resolve-verification-method", "Resolve key/controller/status information at the relevant verification time."),
        ("rotate-integrity-algorithm", "Migrate protected objects to an approved algorithm without erasing prior validation history."),
        ("compare-semantic-identity", "Apply a declared equivalence relation distinct from byte/digest identity."),
        ("refuse-identity-collapse", "Reject merges based only on labels, locations, digests over different scopes or temporal proximity."),
    ],
    "attestation-transparency": [
        ("create-typed-attestation", "Create an issuer-authenticated statement with predicate type, subjects and validity."),
        ("verify-attestation-envelope", "Verify envelope integrity and syntax without asserting predicate truth."),
        ("appraise-attestation-evidence", "Apply a verifier policy to evidence and emit a scoped appraisal result."),
        ("register-transparent-statement", "Submit a signed statement to a transparency service and retain registration outcome."),
        ("verify-inclusion-receipt", "Verify statement inclusion against a signed transparency checkpoint."),
        ("verify-consistency-proof", "Verify append-only consistency between two transparency checkpoints."),
        ("gossip-transparency-checkpoint", "Compare witnessed checkpoints to detect split-view or equivocation evidence."),
        ("resolve-attestation-status", "Resolve suspension, revocation or expiry using a fresh status mechanism."),
        ("renew-attestation-evidence", "Add current validation material without modifying the original attestation."),
        ("select-trust-anchor", "Select issuer/verifier trust anchors by relying policy and scope, not key presence alone."),
        ("evaluate-issuer-authority", "Assess issuer mandate and competence for the exact claim and interval."),
        ("refuse-self-appraisal-collapse", "Reject treatment of a self-attestation as an independent appraisal."),
    ],
    "claim-evidence": [
        ("author-claim", "Create a canonical scoped proposition with subject, modality and validity interval."),
        ("issue-assertion", "Record who asserted a claim, when, with what basis and intended audience."),
        ("construct-argument", "Link claims, warrants, assumptions and evidence into an explicit argument structure."),
        ("bind-evidence-to-claim", "Record relevance, directness, method and scope of an evidence-to-claim support edge."),
        ("register-counterevidence", "Attach evidence that rebuts the claim or conflicts with supporting evidence."),
        ("register-defeater", "Attach an undercutting or rebutting defeater to a claim or support edge."),
        ("score-evidence-dimensions", "Evaluate authority, integrity, directness, relevance, method, corroboration and freshness separately."),
        ("aggregate-evidence-under-policy", "Aggregate dimensions only under a named decision-specific policy with rationale."),
        ("resolve-evidence-conflict", "Record conflict disposition without deleting losing evidence or uncertainty."),
        ("test-claim-falsifier", "Evaluate a declared falsification or counterexample condition and preserve the result."),
        ("mark-evidence-insufficient", "Emit a typed insufficiency when required dimensions, scope or corroboration are missing."),
        ("explain-reliance-decision", "Produce a trace from relying decision to claims, support, defeaters, policy and residual gaps."),
    ],
    "runtime-receipts": [
        ("open-invocation", "Allocate a durable invocation identity and bind intended inputs, mechanism and configuration."),
        ("record-input-acceptance", "Receipt whether each exact input was accepted, rejected, substituted or unavailable."),
        ("record-execution-start", "Record runtime start with host/target, code, configuration and clock context."),
        ("record-effect-intent", "Persist intended writes, messages or external effects before or with execution."),
        ("record-effect-outcome", "Persist committed, aborted, partial, unknown or compensated effect outcomes."),
        ("record-resource-cut", "Record relevant runtime resource and environment cut without treating telemetry as durable evidence by default."),
        ("record-execution-outcome", "Emit success, failure, cancellation or indeterminate outcome with typed cause."),
        ("seal-runtime-receipt", "Canonicalize and integrity-protect the finalized receipt and referenced artifacts."),
        ("reconcile-retry-receipts", "Relate attempts without collapsing their inputs, effects or outcomes."),
        ("verify-receipt-completeness", "Check required fields, referenced artifacts, effect closure and evidence coverage."),
        ("promote-telemetry-to-evidence", "Promote selected telemetry only after durability, identity, integrity, retention and custody qualification."),
        ("refuse-success-from-log-message", "Reject inference of successful durable effects from a success log or span status alone."),
    ],
    "compiler-receipts": [
        ("derive-evidence-requirements", "Derive evidence and lineage requirements from analytical intent, policy and risk."),
        ("discover-provider-offers", "Load versioned provider offers with limits, evidence and target scope."),
        ("match-requirement-to-offer", "Match semantic guarantees and evidence gates, not provider names."),
        ("insert-lineage-capture", "Insert prospective/runtime lineage capture at the semantic or physical boundary required."),
        ("insert-receipt-emission", "Insert durable receipt emission for compilation, runtime and effect boundaries."),
        ("insert-integrity-controls", "Bind canonicalization, digest, signing or transparency mechanisms required by policy."),
        ("prove-mapping-soundness", "Evaluate that a mapping preserves relation meaning, identity, time and authority distinctions."),
        ("record-binding-decision", "Record selected and rejected offers with proof outcomes and residual gaps."),
        ("record-typed-degradation", "Carry an explicitly authorized loss of granularity, freshness or assurance into outputs."),
        ("emit-compiler-receipt", "Seal semantic inputs, requirement/offer bindings, proof outcomes and output identity."),
        ("invalidate-stale-binding", "Invalidate bindings when sources, schemas, policies, keys, methods or providers change."),
        ("refuse-unqualified-provider", "Fail closed when an offer lacks required evidence, limits or semantic conformance."),
    ],
    "audit-accountability": [
        ("emit-audit-event", "Emit a typed actor/action/target/outcome event with source and time metadata."),
        ("sequence-audit-events", "Assign source/epoch sequence information and declare gaps or reorderings."),
        ("collect-audit-log", "Collect audit events with source authentication and loss accounting."),
        ("normalize-audit-event", "Map a source event to a canonical model while retaining raw evidence and loss report."),
        ("protect-audit-log", "Apply access, integrity, immutability and separation-of-duty controls."),
        ("detect-audit-gap", "Detect missing sequence ranges, disabled capture, clock anomalies or collection loss."),
        ("reconstruct-record-history", "Reconstruct governed value creation/change/deletion with prior and current values."),
        ("review-audit-trail", "Apply a risk-based review procedure and record reviewer findings and coverage."),
        ("correlate-audit-and-lineage", "Link audit events to provenance occurrences without merging their semantics."),
        ("export-audit-trail", "Produce human- and machine-readable trail data with scope and integrity metadata."),
        ("retain-audit-records", "Apply retention and legal-hold schedules to audit records and their verification material."),
        ("refuse-log-as-evidence", "Reject automatic evidentiary promotion of unqualified logs."),
    ],
    "custody-forensics": [
        ("authorize-forensic-acquisition", "Record legal/organizational authority, scope and method before acquisition."),
        ("capture-source-state", "Record device/object state, clock, connectivity and volatility before acquisition."),
        ("acquire-forensic-image", "Acquire a source using a documented, versioned method with alteration controls."),
        ("verify-acquisition-fixity", "Compute and independently verify digests across acquisition copies."),
        ("record-custody-transfer", "Record releasor, recipient, time, purpose, condition, seal and verification."),
        ("record-evidence-access", "Record scoped access to evidence without claiming custody transfer."),
        ("seal-evidence-container", "Bind container, manifest, items and seal identifier under a custody event."),
        ("verify-custody-continuity", "Check every expected custody interval, transfer and exception."),
        ("perform-fixity-check", "Recompute fixity under a preservation schedule and record outcome."),
        ("migrate-preserved-format", "Migrate format with source retention, tool/method record and equivalence validation."),
        ("renew-long-term-validation", "Add archive timestamps or algorithm renewal evidence before protection weakens."),
        ("quarantine-compromised-evidence", "Prevent ordinary reliance while preserving compromised material and incident history."),
    ],
    "reproducibility": [
        ("package-research-object", "Manifest data, code, method, workflow, environment, results and licenses."),
        ("capture-environment", "Capture software, hardware, configuration, external service and dependency cuts."),
        ("record-randomness-control", "Record seeds, generators, nondeterministic sources and parallelism posture."),
        ("record-data-selection", "Record population, sample, exclusions, filters and exact input cuts."),
        ("record-method-edition", "Bind a run to protocol/method edition, assumptions and deviations."),
        ("validate-package-manifest", "Verify members, digests, identifiers, media types and required metadata."),
        ("resolve-reproduction-target", "Define whether target is bitwise, value-tolerant, statistical, structural or inferential."),
        ("execute-reproduction-run", "Perform an independently identified run against the declared target and environment."),
        ("compare-reproduction-result", "Evaluate result equivalence under the selected comparison policy."),
        ("explain-reproduction-divergence", "Trace differences to data, code, environment, method, randomness or external state."),
        ("publish-reproduction-appraisal", "Issue a scoped appraisal with materials, result, limitations and independence."),
        ("refuse-reproducibility-overclaim", "Reject claims stronger than captured dependencies and comparison evidence support."),
    ],
    "correction-lifecycle": [
        ("issue-correction", "Publish corrected scope, reason, authority and replacement while preserving the original."),
        ("issue-retraction", "Withdraw a claim or publication from reliance without erasing history."),
        ("issue-recall", "Publish affected identities/ranges, severity and required downstream disposition."),
        ("request-deletion", "Create an authority-scoped deletion or erasure request with exceptions and deadline."),
        ("place-legal-hold", "Suspend ordinary disposition for exact records and replicas within hold scope."),
        ("release-legal-hold", "End or narrow a hold with authority, time and resulting disposition schedule."),
        ("execute-deletion", "Apply logical/physical deletion mechanisms to resolved targets and replicas."),
        ("verify-deletion-scope", "Assess target, replicas, indexes, caches, backups and exceptions after deletion."),
        ("emit-deletion-receipt", "Emit a minimal privacy-aware receipt of attempted and verified deletion outcomes."),
        ("propagate-invalidation", "Notify downstream custodians, catalogs, decisions and caches of changed reliance status."),
        ("acknowledge-recall", "Record recipient receipt, disposition, exceptions and closure state."),
        ("refuse-lifecycle-collapse", "Reject substitution among correction, deletion, retraction, recall and supersession."),
    ],
    "disclosure-retention": [
        ("classify-evidence", "Assign sensitivity, jurisdiction, purpose and handling rules to evidence items."),
        ("resolve-disclosure-authority", "Determine requester, purpose, authorization, subject and jurisdiction scope."),
        ("select-disclosure-view", "Choose exact evidence fields/items required under minimization and relevance rules."),
        ("apply-evidence-redaction", "Produce transformed views and a protected redaction map without altering sources."),
        ("create-selective-presentation", "Create a privacy-aware presentation revealing only authorized claims or attributes."),
        ("verify-disclosure-package", "Verify manifest, authorization, integrity, redactions and declared omissions."),
        ("record-disclosure-receipt", "Record who received which exact package, when, for what purpose and conditions."),
        ("apply-retention-schedule", "Compute disposition dates from record class, trigger, jurisdiction and holds."),
        ("review-disposition", "Require authorized review before destruction, transfer or archival."),
        ("preserve-minimal-proof", "Retain only the authorized minimal receipt when source material is deleted."),
        ("expire-access-grant", "End evidence access when purpose, role or validity expires."),
        ("refuse-overdisclosure", "Fail when requested disclosure exceeds authority, purpose or minimization limits."),
    ],
    "impact-analysis": [
        ("compute-upstream-slice", "Traverse a bounded upstream graph with edge kinds, time cut and coverage gaps."),
        ("compute-downstream-slice", "Traverse a bounded downstream graph without equating reachability with confirmed impact."),
        ("compare-plan-and-run-impact", "Separate possible plan impact from observed affected executions."),
        ("classify-impact-path", "Classify paths as semantic, physical, runtime, governance, security or decision/action."),
        ("evaluate-change-compatibility", "Apply schema, formula, policy or artifact compatibility rules at each path."),
        ("identify-affected-decisions", "Find decisions that considered affected evidence or derived outputs."),
        ("identify-affected-actions", "Find actions downstream of affected decisions and exact execution occurrences."),
        ("identify-affected-models-studies", "Find models, studies, evaluations and publications using affected cuts."),
        ("prioritize-impact-review", "Rank review candidates using criticality, exposure, uncertainty and authority."),
        ("confirm-impact", "Record human or automated confirmation with exact evidence and scope."),
        ("emit-impact-notification", "Notify owners with affected identities, paths, uncertainty and required action."),
        ("close-impact-case", "Record dispositions, residual unknowns and evidence of notification/repair."),
    ],
}


FAMILY_CONTEXT = {
    "lineage-capture": "runtime-lineage", "provenance-graph": "provenance-graph",
    "identity-integrity": "identity-digest", "attestation-transparency": "attestation",
    "claim-evidence": "claim-evidence", "runtime-receipts": "runtime-receipts",
    "compiler-receipts": "compiler-receipts", "audit-accountability": "audit-log",
    "custody-forensics": "custody", "reproducibility": "reproducibility-package",
    "correction-lifecycle": "correction", "disclosure-retention": "disclosure",
    "impact-analysis": "impact-analysis",
}


FAMILY_SOURCE = {
    "lineage-capture": ["w3c.prov.dm", "openlineage.spec"],
    "provenance-graph": ["w3c.prov.o", "w3c.prov.constraints"],
    "identity-integrity": ["w3c.rdf.canon", "nist.fips180"],
    "attestation-transparency": ["ietf.rfc9334", "ietf.rfc9943"],
    "claim-evidence": ["omg.sacm", "w3c.vc2"],
    "runtime-receipts": ["openlineage.spec", "ietf.rfc9942"],
    "compiler-receipts": ["slsa.provenance", "w3c.earl"],
    "audit-accountability": ["nist.800.92", "ecfr.part11"],
    "custody-forensics": ["iso.27037", "nist.ir.8387"],
    "reproducibility": ["rocrate.11", "workflow.run.crate"],
    "correction-lifecycle": ["fda.electronic.2024", "oasis.csaf"],
    "disclosure-retention": ["w3c.vc2", "sec.17a4"],
    "impact-analysis": ["w3c.prov.dm", "oasis.csaf"],
}


FAMILY_PLANES = {
    "lineage-capture": ["sources", "pipelines", "transformations", "semantic_formulas", "runtime"],
    "provenance-graph": ["sources", "pipelines", "transformations", "models_studies"],
    "identity-integrity": ["security", "governance", "runtime", "compiler"],
    "attestation-transparency": ["security", "governance", "runtime"],
    "claim-evidence": ["models_studies", "decisions_actions", "quality", "governance"],
    "runtime-receipts": ["pipelines", "runtime"],
    "compiler-receipts": ["compiler", "runtime", "transformations"],
    "audit-accountability": ["security", "governance", "runtime"],
    "custody-forensics": ["security", "governance", "sources"],
    "reproducibility": ["models_studies", "pipelines", "transformations"],
    "correction-lifecycle": ["governance", "quality", "decisions_actions"],
    "disclosure-retention": ["governance", "security"],
    "impact-analysis": ["sources", "pipelines", "transformations", "semantic_formulas", "models_studies", "decisions_actions", "security", "governance", "quality", "runtime", "compiler"],
}


CAPABILITIES = []
for family, operations in OPERATION_FAMILIES.items():
    context = FAMILY_CONTEXT[family]
    evidence = [sid(ref) for ref in FAMILY_SOURCE[family]]
    planes = FAMILY_PLANES[family]
    CAPABILITIES.append({
        "capability_id": f"capability.lpe.{family}", "edition": EDITION, "status": "candidate",
        "candidate_kind": "capability", "family": family,
        "name": family.replace("-", " ").title(),
        "definition": f"Provider-neutral capability family for {family.replace('-', ' ')} with explicit identity, time, authority, failure and evidence contracts.",
        "owner_context_ref": f"context.lpe.{context}", "input_types": [], "output_types": [],
        "preconditions": ["Subject identities, scopes and authority postures are explicit."],
        "postconditions": ["Outcome and residual gaps are typed and evidence-linked."],
        "failure_modes": ["unknown_identity", "insufficient_authority", "insufficient_evidence", "time_ambiguity", "coverage_gap"],
        "refusal_law": "Refuse silent inference, semantic collapse or assurance upgrade when required distinctions are unavailable.",
        "cross_plane_refs": planes, "evidence_refs": evidence,
    })
    for oid, description in operations:
        CAPABILITIES.append({
            "capability_id": f"operation.lpe.{family}.{oid}", "edition": EDITION, "status": "candidate",
            "candidate_kind": "operation", "family": family, "name": oid.replace("-", " ").title(),
            "definition": description, "owner_context_ref": f"context.lpe.{context}",
            "input_types": ["typed_subject_refs", "authority_scope", "time_scope", "policy_or_method_edition"],
            "output_types": ["typed_outcome", "receipt_or_assertion_refs", "residual_gaps"],
            "preconditions": ["Input identity and scope are explicit.", "Required authority and evidence gates are selected."],
            "postconditions": ["Recording, event and validity time remain distinguishable.", "Failures and partial outcomes are not represented as success."],
            "failure_modes": ["invalid_input", "authority_missing", "evidence_insufficient", "conflict", "partial_or_unknown_effect"],
            "refusal_law": "Refuse when performing the operation would erase issuer, scope, time, granularity, custody, defeater or assurance distinctions.",
            "cross_plane_refs": planes, "evidence_refs": evidence,
        })


DECISION_ROWS = [
    ("lineage-granularity", "Select dataset, field, record, cell, array-region or physical-object lineage granularity from the question and evidence budget.", "lineage-capture"),
    ("prospective-or-retrospective", "Select plan possibility, observed occurrence, or both; never substitute one for the other.", "lineage-capture"),
    ("logical-physical-runtime", "Select logical meaning, physical materialization and runtime occurrence layers independently.", "lineage-capture"),
    ("edge-direction", "Resolve dependency direction from typed relation semantics rather than UI arrow orientation.", "provenance-graph"),
    ("graph-merge-policy", "Choose identity, authority, conflict and duplicate policy before merging provenance graphs.", "provenance-graph"),
    ("canonicalization-algorithm", "Choose canonicalization for the exact abstract data model and resource limits.", "identity-integrity"),
    ("digest-algorithm", "Choose digest algorithm and scope with agility and collision posture.", "identity-integrity"),
    ("signature-verification-time", "Choose the relevant signing, recording, verification or relying time for key/status evaluation.", "identity-integrity"),
    ("issuer-authority", "Decide whether issuer mandate covers the exact claim, subject, jurisdiction and interval.", "attestation-transparency"),
    ("independence-level", "Classify self-assertion, second-party review and independent appraisal without collapsing them.", "attestation-transparency"),
    ("transparency-policy", "Choose required logs, witness/checkpoint and freshness policy for registration evidence.", "attestation-transparency"),
    ("evidence-aggregation", "Choose a claim-specific aggregation rule; never assume one universal evidence score.", "claim-evidence"),
    ("defeater-disposition", "Decide whether a defeater narrows, suspends, rejects or leaves a claim indeterminate.", "claim-evidence"),
    ("telemetry-promotion", "Decide whether observability telemetry meets durable evidence identity, integrity, retention and custody gates.", "runtime-receipts"),
    ("receipt-finality", "Choose when a receipt can be finalized given external effects, retries and uncertain outcomes.", "runtime-receipts"),
    ("compiler-binding", "Select an offer only after guarantee, limit, evidence and invalidation checks pass.", "compiler-receipts"),
    ("typed-degradation", "Decide whether an explicit loss of granularity/freshness/assurance is authorized or compilation must refuse.", "compiler-receipts"),
    ("audit-retention", "Choose audit log retention and protection from record class, threat, regulation and investigation needs.", "audit-accountability"),
    ("forensic-method", "Select acquisition and preservation method based on source volatility, authority and alteration risk.", "custody-forensics"),
    ("reproduction-equivalence", "Choose bitwise, value-tolerance, statistical, structural or inferential reproduction target.", "reproducibility"),
    ("correction-action", "Select correction, supersession, retraction, recall or deletion based on what must change in reliance and storage.", "correction-lifecycle"),
    ("hold-versus-erasure", "Resolve legal hold, retention and erasure conflicts under identified authority; do not guess.", "correction-lifecycle"),
    ("disclosure-scope", "Select minimal authorized evidence and redactions for audience and purpose.", "disclosure-retention"),
    ("impact-confirmation", "Decide which reachable subjects are possible, probable or confirmed impacts with evidence.", "impact-analysis"),
]


for did, description, family in DECISION_ROWS:
    CAPABILITIES.append({
        "capability_id": f"decision.lpe.{did}", "edition": EDITION, "status": "candidate",
        "candidate_kind": "decision", "family": family, "name": did.replace("-", " ").title(),
        "definition": description, "owner_context_ref": f"context.lpe.{FAMILY_CONTEXT[family]}",
        "input_types": ["typed_requirements", "candidate_offers", "evidence", "policy"],
        "output_types": ["selected_posture", "rationale", "rejected_alternatives", "residual_gaps"],
        "preconditions": ["Decision authority and policy edition are explicit."],
        "postconditions": ["The decision is reproducible from recorded inputs or is marked human-judgment-dependent."],
        "failure_modes": ["authority_missing", "policy_conflict", "evidence_insufficient", "no_safe_alternative"],
        "refusal_law": "Refuse selection when a required distinction or blocking evidence gate is unresolved.",
        "cross_plane_refs": FAMILY_PLANES[family], "evidence_refs": [sid(ref) for ref in FAMILY_SOURCE[family]],
    })


LAW_ROWS = [
    ("plan-is-not-run", "A prospective plan never proves that any activity executed or any entity was used or generated.", "lineage-capture"),
    ("logical-is-not-physical", "Logical dependency never identifies physical bytes or storage cuts without an explicit materialization link.", "lineage-capture"),
    ("runtime-is-occurrence-scoped", "Runtime lineage refers to exact runs/attempts and may not be generalized without an aggregation rule.", "lineage-capture"),
    ("derivation-is-not-execution", "Entity derivation and process execution are distinct relation families and neither is inferred from the other alone.", "provenance-graph"),
    ("assertion-boundary-preserved", "Issuer and assertion boundaries survive graph merge, inference, export and slicing.", "provenance-graph"),
    ("unknown-coverage-open", "Absence of an edge in an open-world graph never proves absence of dependency.", "provenance-graph"),
    ("digest-is-not-truth", "A matching digest establishes representation integrity under its scope, not truth, authority or semantic correctness.", "identity-integrity"),
    ("identity-is-scheme-scoped", "Identifier equality is evaluated only under its scheme, authority, version and time scope.", "identity-integrity"),
    ("signature-is-not-authority", "A valid signature proves control of verification material for a payload; issuer authority needs separate appraisal.", "attestation-transparency"),
    ("attestation-is-not-appraisal", "An issuer attestation and an independent verifier appraisal remain distinct artifacts and roles.", "attestation-transparency"),
    ("transparency-is-not-truth", "Transparency registration proves inclusion at a tree state, not correctness of the statement.", "attestation-transparency"),
    ("evidence-needs-warrant", "Evidence supports a claim only through an explicit relevance/directness/warrant relation.", "claim-evidence"),
    ("defeaters-retained", "Counterevidence and unresolved defeaters are retained and surfaced in every reliance view.", "claim-evidence"),
    ("strength-is-multidimensional", "Authority, integrity, method, directness, relevance, corroboration and freshness are not collapsed by default.", "claim-evidence"),
    ("recording-time-is-not-validity", "Event, observation, recording, signing, registration, validity and appraisal times remain distinct.", "runtime-receipts"),
    ("telemetry-is-not-evidence", "Telemetry becomes durable evidence only after explicit identity, integrity, retention, coverage and custody qualification.", "runtime-receipts"),
    ("receipt-reports-failure", "A receipt represents failure, cancellation, partial or indeterminate outcomes directly; it never fabricates success.", "runtime-receipts"),
    ("compiler-does-not-upgrade", "Compilation never strengthens semantics, assurance or evidence posture without a proven binding.", "compiler-receipts"),
    ("audit-is-not-provenance", "Audit events/logs/trails and provenance assertions/graphs have different semantics and must be linked, not collapsed.", "audit-accountability"),
    ("log-is-not-evidence", "A log record is not evidentiary solely because it is structured, timestamped or retained.", "audit-accountability"),
    ("custody-continuity-explicit", "Every custody gap or seal/fixity failure remains explicit; later possession cannot silently repair it.", "custody-forensics"),
    ("reproduction-target-explicit", "Reproducibility is judged only against an explicit target and equivalence rule.", "reproducibility"),
    ("lifecycle-actions-distinct", "Correction, deletion, retraction, recall and supersession have distinct effects and cannot substitute silently.", "correction-lifecycle"),
    ("redaction-is-not-deletion", "A disclosure redaction transforms a view and does not imply source deletion or nonexistence.", "disclosure-retention"),
]


for lid, description, family in LAW_ROWS:
    CAPABILITIES.append({
        "capability_id": f"law.lpe.{lid}", "edition": EDITION, "status": "candidate",
        "candidate_kind": "law", "family": family, "name": lid.replace("-", " ").title(),
        "definition": description, "owner_context_ref": f"context.lpe.{FAMILY_CONTEXT[family]}",
        "input_types": ["candidate_state"], "output_types": ["pass_fail_gap"],
        "preconditions": ["Applicable scope and subject cut are explicit."],
        "postconditions": ["Violation produces a typed refusal or gap."],
        "failure_modes": ["law_violation", "scope_unknown"],
        "refusal_law": "Refuse any binding or inference that violates this law.",
        "cross_plane_refs": FAMILY_PLANES[family], "evidence_refs": [sid(ref) for ref in FAMILY_SOURCE[family]],
    })


EVIDENCE_MODEL = {
    "model_id": "model.lpe.evidence-evaluation", "edition": EDITION, "status": "candidate",
    "completion_claim": False,
    "purpose": "Assess whether identified evidence can support a precise claim for a relying decision without confusing integrity, identity, authority or assertion with truth.",
    "unit_of_assessment": "claim-evidence-support edge under one relying policy, subject cut and decision time",
    "roles": [
        {"role": "claimant", "meaning": "issues an assertion", "not_equivalent_to": ["attester", "independent_appraiser"]},
        {"role": "attester", "meaning": "authenticates a typed statement", "not_equivalent_to": ["claim_truth_authority", "independent_appraiser"]},
        {"role": "evidence_producer", "meaning": "produces an evidence item under a method", "not_equivalent_to": ["custodian", "verifier"]},
        {"role": "custodian", "meaning": "maintains custody/preservation continuity", "not_equivalent_to": ["claimant", "appraiser"]},
        {"role": "verifier", "meaning": "checks integrity, syntax or cryptographic validity", "not_equivalent_to": ["independent_appraiser"]},
        {"role": "independent_appraiser", "meaning": "applies a declared appraisal policy for a relying party", "not_equivalent_to": ["issuer", "automatic_signature_checker"]},
        {"role": "relying_party", "meaning": "decides whether and how to rely under its policy", "not_equivalent_to": ["truth_oracle"]},
    ],
    "authority_dimensions": [
        {"dimension": "identity_resolution", "question": "Is the issuer/appraiser identity resolved under a qualified scheme at the relevant time?", "levels": ["unknown", "self_identified", "authenticated", "independently_bound"]},
        {"dimension": "mandate", "question": "Does the actor have authority for this exact subject, proposition, action, jurisdiction and interval?", "levels": ["none_or_unknown", "claimed", "documented_scoped", "externally_confirmed_scoped"]},
        {"dimension": "competence", "question": "Is the actor competent for the method and proposition?", "levels": ["unknown", "claimed", "evidenced", "independently_qualified"]},
        {"dimension": "independence", "question": "What organizational, financial and method independence exists?", "levels": ["self", "second_party", "independent_with_conflicts", "independent_conflicts_controlled"]},
        {"dimension": "method_authority", "question": "Is the evidence-generation/appraisal method governed and fit for use?", "levels": ["unknown", "documented", "validated_for_scope", "independently_reviewed_for_scope"]},
        {"dimension": "conflict_of_interest", "question": "Are relevant conflicts disclosed and controlled?", "levels": ["unknown", "disclosed", "mitigated", "independently_reviewed"]},
    ],
    "strength_dimensions": [
        {"dimension": "integrity", "question": "Is the exact assessed representation intact?", "levels": ["failed", "unknown", "weakly_checked", "verified", "independently_verified"]},
        {"dimension": "identity", "question": "Are subject and occurrence identities unambiguous for the claim?", "levels": ["conflicting", "unknown", "partially_resolved", "resolved_scoped", "cross-system-confirmed"]},
        {"dimension": "directness", "question": "How directly does the item observe or measure the proposition?", "levels": ["irrelevant", "remote_inference", "indirect", "direct", "direct_with_method_controls"]},
        {"dimension": "relevance", "question": "Does the evidence apply to the exact subject, interval, population and conditions?", "levels": ["mismatch", "unknown", "partial", "matched", "matched_with_boundary_tests"]},
        {"dimension": "method_quality", "question": "Are collection, computation and appraisal methods documented and validated?", "levels": ["invalid", "unknown", "documented", "validated", "independently_replicated"]},
        {"dimension": "custody", "question": "Is handling and preservation continuity sufficient for this reliance?", "levels": ["broken", "unknown", "documented_with_gaps", "continuous", "continuous_and_independently_checked"]},
        {"dimension": "corroboration", "question": "Do genuinely independent sources/methods agree?", "levels": ["contradicted", "none", "dependent_repeat", "independent_agreement", "multiple_independent_methods"]},
        {"dimension": "reproducibility", "question": "Can the generation/evaluation be rerun to a declared equivalence target?", "levels": ["failed", "not_assessed", "materials_partial", "reproduced", "independently_replicated"]},
        {"dimension": "completeness", "question": "Does the item cover all records/events required for the claim?", "levels": ["known_incomplete", "unknown", "bounded_partial", "coverage_accounted", "coverage_independently_checked"]},
    ],
    "freshness_model": {
        "time_fields": ["event_time", "observation_time", "recording_time", "signing_time", "registration_time", "valid_from", "valid_until", "retrieval_time", "appraisal_time", "decision_time"],
        "rule": "Freshness is evaluated at decision_time using source volatility, status mechanism, valid interval, maximum age and recheck triggers; recording_time never substitutes for event_time or validity.",
        "states": ["fresh_for_use", "stale_but_usable_by_exception", "expired", "status_unknown", "future_not_yet_valid", "temporally_conflicting"],
        "recheck_triggers": ["source_changed", "schema_or_method_changed", "credential_status_changed", "key_or_algorithm_changed", "new_counterevidence", "custody_gap", "policy_changed", "retention_or_hold_changed"],
    },
    "defeater_model": [
        {"kind": "rebutting", "effect": "supports an incompatible proposition or the negation of the claim"},
        {"kind": "authority_undercutter", "effect": "shows issuer mandate, competence or independence is absent/narrower"},
        {"kind": "integrity_undercutter", "effect": "shows payload, identity, signature, digest or canonicalization is compromised/mismatched"},
        {"kind": "method_undercutter", "effect": "shows collection, derivation, measurement or appraisal method is invalid for scope"},
        {"kind": "relevance_undercutter", "effect": "shows subject, population, condition, jurisdiction or interval mismatch"},
        {"kind": "custody_undercutter", "effect": "shows uncontrolled handling, missing transfer or preservation failure"},
        {"kind": "freshness_undercutter", "effect": "shows stale status, expired validity or changed source state"},
        {"kind": "coverage_undercutter", "effect": "shows missing events, blind spots, sampling gaps or selective disclosure"},
        {"kind": "conflict", "effect": "shows unresolved inconsistency among evidence items or appraisals"},
    ],
    "evaluation_output": {
        "required": ["claim_ref", "evidence_refs", "policy_ref", "decision_time", "dimension_results", "defeaters", "verdict", "rationale", "residual_uncertainty", "appraiser_ref"],
        "verdicts": ["support_sufficient_for_policy", "support_insufficient", "defeated", "conflicted", "indeterminate", "not_applicable"],
        "aggregation_law": "No global numeric score is canonical. A relying policy may define monotone gates or aggregation, but must expose dimension inputs and must not compensate for blocking integrity, authority, relevance or freshness failures unless the policy explicitly permits and records an exception.",
    },
    "non_inferences": [
        "valid signature => claim truth", "matching digest => semantic correctness", "trusted issuer => authority for every claim",
        "more citations => stronger evidence", "recent recording time => current validity", "no logged event => event did not occur",
        "successful runtime status => durable external effects", "provenance path => confirmed causation or impact",
    ],
    "evidence_refs": [sid(ref) for ref in ["omg.sacm", "w3c.vc2", "ietf.rfc9334", "nist.ir.8354", "w3c.vc.status"]],
}


REFUSAL_ROWS = [
    ("missing-identity", "refuse", "A subject, occurrence, issuer, artifact or scope lacks a resolvable identity."),
    ("ambiguous-occurrence", "quarantine", "Type, plan, run, retry and event identities cannot be separated."),
    ("missing-authority", "refuse", "No scoped authority exists for assertion, appraisal, disclosure, correction, hold or deletion."),
    ("invalid-integrity", "refuse", "Digest, signature, manifest, transparency proof or fixity verification fails."),
    ("unknown-integrity", "gap", "Required representation or verification material is missing."),
    ("stale-status", "refuse_or_exception", "Credential, key, attestation, method or source status is too stale for the relying policy."),
    ("time-collapse", "refuse", "Event, observation, recording, signing, registration, validity or appraisal time would be silently conflated."),
    ("lineage-layer-collapse", "refuse", "Prospective/retrospective or logical/physical/runtime lineage would be silently substituted."),
    ("audit-provenance-collapse", "refuse", "An audit log/trail would be represented as a provenance graph or vice versa without typed mapping."),
    ("log-evidence-upgrade", "refuse", "A log or span lacks durable evidence qualification for the proposed reliance."),
    ("assertion-appraisal-collapse", "refuse", "Self-assertion/attestation would be presented as independent appraisal."),
    ("digest-truth-upgrade", "refuse", "Representation integrity would be presented as claim truth or semantic correctness."),
    ("open-world-absence", "gap", "Missing lineage/audit/evidence record would be used as proof of non-occurrence or independence."),
    ("unknown-edge-semantics", "quarantine", "A source edge cannot be mapped to a canonical relation with sound direction and qualifiers."),
    ("incomplete-custody", "quarantine", "Custody continuity, seal/fixity or preservation history has a material gap."),
    ("unresolved-defeater", "refuse_or_indeterminate", "A blocking rebutting or undercutting defeater remains unresolved."),
    ("unsupported-degradation", "refuse", "A binding would reduce lineage granularity, evidence strength or receipt durability without authorization."),
    ("provider-by-name", "refuse", "A provider is selected by brand/name rather than a versioned qualified offer."),
    ("partial-effect-as-success", "refuse", "Partial, cancelled or externally indeterminate effects would be reported as success."),
    ("reproducibility-overclaim", "refuse", "The claimed reproduction guarantee exceeds captured data, method, environment or equivalence evidence."),
    ("lifecycle-substitution", "refuse", "Correction, deletion, retraction, recall or supersession would be silently substituted."),
    ("hold-erasure-conflict", "refuse", "Retention/legal-hold and deletion/erasure authorities conflict without adjudication."),
    ("overdisclosure", "refuse", "Requested evidence exceeds authorized purpose, audience, jurisdiction or minimization scope."),
    ("confirmed-impact-from-path", "refuse", "Graph reachability alone would be labeled confirmed business or safety impact."),
]


INVARIANTS_REFUSALS = [
    {
        "rule_id": f"law.lpe.{lid}", "edition": EDITION, "status": "candidate", "rule_kind": "invariant",
        "name": lid.replace("-", " ").title(), "statement": description,
        "disposition": "refuse_or_typed_gap", "family": family,
        "evidence_refs": [sid(ref) for ref in FAMILY_SOURCE[family]],
    }
    for lid, description, family in LAW_ROWS
] + [
    {
        "rule_id": f"refusal.lpe.{rid}", "edition": EDITION, "status": "candidate", "rule_kind": "refusal",
        "name": rid.replace("-", " ").title(), "statement": statement,
        "disposition": disposition, "family": "cross_cutting",
        "evidence_refs": [sid("w3c.prov.constraints"), sid("omg.sacm")],
    }
    for rid, disposition, statement in REFUSAL_ROWS
]


# id, context, operation family/op, required guarantees, provider-class offer guarantees
REQUIREMENT_ROWS = [
    ("run-actual-io", "runtime-lineage", "lineage-capture.observe-run-inputs", ["run_scoped", "actual_not_declared", "producer_identity", "event_deduplication"], "runtime-lineage-emitter", ["run_event_identity", "actual_dataset_facets", "producer_schema_version"]),
    ("field-derivation", "field-lineage", "lineage-capture.capture-field-edge", ["field_identity", "transform_kind", "direction", "unknowns_preserved"], "field-lineage-extractor", ["field_edges", "transform_description", "confidence_and_gaps"]),
    ("formula-provenance", "formula-lineage", "lineage-capture.capture-formula-dependency", ["formula_ast_identity", "operand_roles", "units", "grain"], "semantic-formula-registry", ["versioned_formula_ast", "operand_semantics", "approval_history"]),
    ("prov-validation", "provenance-graph", "provenance-graph.validate-prov-constraints", ["prov_constraints", "ordering_checks", "violation_report"], "provenance-validator", ["constraint_validation", "inference_trace", "typed_violations"]),
    ("graph-query", "lineage-query", "provenance-graph.slice-provenance-graph", ["bounded_traversal", "time_cut", "coverage_gaps", "redaction"], "provenance-query-engine", ["typed_traversal", "cycle_handling", "coverage_metadata"]),
    ("canonical-payload", "identity-digest", "identity-integrity.canonicalize-json", ["algorithm_identity", "determinism", "resource_limits"], "canonicalization-provider", ["rfc8785_conformance", "deterministic_bytes", "failure_reporting"]),
    ("signed-attestation", "attestation", "attestation-transparency.create-typed-attestation", ["predicate_type_binding", "subject_digest", "issuer_identity", "algorithm_agility"], "attestation-signer", ["typed_statement", "signature_envelope", "verification_material"]),
    ("independent-appraisal", "independent-appraisal", "attestation-transparency.appraise-attestation-evidence", ["separate_verifier", "policy_edition", "defeater_handling", "verdict_scope"], "attestation-verifier", ["evidence_appraisal", "policy_trace", "scoped_verdict"]),
    ("transparency-receipt", "transparency-registration", "attestation-transparency.verify-inclusion-receipt", ["service_identity", "inclusion_proof", "checkpoint_signature", "freshness"], "transparency-service", ["registration_receipt", "signed_checkpoint", "consistency_proof"]),
    ("claim-evidence-evaluation", "evidence-strength", "claim-evidence.score-evidence-dimensions", ["multidimensional", "defeaters", "authority_scope", "freshness"], "evidence-appraisal-engine", ["dimension_results", "rationale", "residual_uncertainty"]),
    ("durable-runtime-receipt", "runtime-receipts", "runtime-receipts.seal-runtime-receipt", ["invocation_identity", "effect_outcome", "integrity", "retention"], "runtime-receipt-emitter", ["sealed_receipt", "typed_outcome", "effect_summary"]),
    ("compiler-proof-receipt", "compiler-receipts", "compiler-receipts.emit-compiler-receipt", ["input_contract_cut", "binding_trace", "proof_results", "artifact_identity"], "compiler-receipt-emitter", ["binding_receipt", "proof_results", "output_digest"]),
    ("qualified-audit-trail", "audit-trail", "audit-accountability.reconstruct-record-history", ["prior_and_current_value", "actor", "reason", "protected_sequence"], "regulated-audit-trail", ["record_history", "tamper_protection", "human_export"]),
    ("forensic-acquisition", "forensic-acquisition", "custody-forensics.acquire-forensic-image", ["authorized_scope", "source_state", "write_protection", "fixity"], "forensic-acquisition-provider", ["method_record", "forensic_image", "verified_digests"]),
    ("custody-continuity", "custody", "custody-forensics.verify-custody-continuity", ["every_transfer", "seal_condition", "gap_reporting", "custodian_identity"], "evidence-custody-system", ["custody_events", "continuity_verdict", "exceptions"]),
    ("reproduction-package", "reproducibility-package", "reproducibility.validate-package-manifest", ["data_code_method_environment", "digests", "licenses", "equivalence_target"], "research-object-packager", ["manifested_package", "dependency_links", "validation_report"]),
    ("correction-propagation", "correction", "correction-lifecycle.propagate-invalidation", ["affected_identity", "lifecycle_kind", "downstream_ack", "history_preserved"], "lifecycle-notification-provider", ["typed_notice", "delivery_receipts", "acknowledgements"]),
    ("impact-assessment", "impact-analysis", "impact-analysis.classify-impact-path", ["layered_paths", "possible_vs_confirmed", "time_cut", "coverage_gaps"], "impact-analysis-engine", ["classified_paths", "uncertainty", "review_queue"]),
]


REQUIREMENTS = []
OFFERS = []
COMPILER_MAPPINGS = []
for rid, context, operation, guarantees, provider_class, offered in REQUIREMENT_ROWS:
    requirement_id = f"requirement.lpe.{rid}"
    offer_id = f"offer.lpe.{rid}"
    operation_ref = f"operation.lpe.{operation}"
    REQUIREMENTS.append({
        "requirement_id": requirement_id, "edition": EDITION, "status": "candidate",
        "subject_context_ref": f"context.lpe.{context}", "operation_ref": operation_ref,
        "required_guarantees": guarantees, "criticality": "blocking",
        "evidence_gates": ["primary_spec_or_conformance_evidence", "version_and_validity", "failure_and_limit_contract"],
        "fallback_law": "refuse_or_explicit_typed_degradation",
        "evidence_refs": [sid(ref) for ref in FAMILY_SOURCE[next(f for f in OPERATION_FAMILIES if operation.startswith(f + "."))]],
    })
    OFFERS.append({
        "offer_id": offer_id, "edition": EDITION, "status": "candidate",
        "provider_class": provider_class, "operation_ref": operation_ref,
        "offered_guarantees": offered,
        "limits": ["Offer is a provider-class hypothesis, not a qualification of any product.", "Deployment/version/target conformance evidence is required."],
        "validity": {"from": None, "until": None, "recheck_triggers": ["provider_version", "schema_version", "policy_or_key_change"]},
        "evidence_refs": [sid(ref) for ref in FAMILY_SOURCE[next(f for f in OPERATION_FAMILIES if operation.startswith(f + "."))]],
    })
    COMPILER_MAPPINGS.append({
        "mapping_id": f"mapping.lpe.{rid}", "edition": EDITION, "status": "candidate",
        "requirement_ref": requirement_id, "offer_ref": offer_id, "operation_ref": operation_ref,
        "binding_phase": "assurance_insertion" if "receipt" in rid or "attestation" in rid else "physical_binding",
        "match_rules": [f"Every required guarantee must be satisfied or explicitly proven equivalent: {', '.join(guarantees)}.", "Offer limits and invalidation triggers must be carried into the binding receipt."],
        "proof_obligations": ["semantic_scope_match", "identity_and_time_match", "authority_match", "failure_and_gap_preservation", "evidence_freshness"],
        "fallback": "refuse unless a named typed degradation is authorized",
        "receipt_fields": ["requirement_ref", "offer_ref", "proof_results", "configuration", "rejected_offers", "residual_gaps", "validity"],
        "evidence_refs": OFFERS[-1]["evidence_refs"],
    })


CROSS_PLANE_ROWS = [
    ("sources", "Source occurrences and acquisition authority", ["source-lineage", "custody"], ["source-occurrence", "dataset-version"], ["acquired-from"], ["lineage-capture.capture-source-acquisition", "custody-forensics.capture-source-state"], "source acquisition receipt"),
    ("pipelines", "Plans, workflow editions, task runs and retries", ["prospective-lineage", "pipeline-lineage", "runtime-lineage"], ["workflow-edition", "run", "run-attempt"], ["declared-input", "observed-input", "parent-run", "retry-of"], ["lineage-capture.declare-plan-dependencies", "runtime-receipts.reconcile-retry-receipts"], "run and attempt receipts"),
    ("transformations", "Typed operations, code/parameter editions and derivations", ["transformation-lineage", "derivation", "activity-execution"], ["transform-edition", "activity-occurrence", "derivation-record"], ["was-derived-from", "used", "was-generated-by"], ["lineage-capture.capture-logical-edge", "compiler-receipts.insert-lineage-capture"], "compiler plus runtime receipts"),
    ("semantic_formulas", "Formula ASTs, metric editions, operands, filters, units and grain", ["formula-lineage", "field-lineage"], ["formula-edition", "field"], ["computed-by-formula", "field-depends-on"], ["lineage-capture.capture-formula-dependency", "impact-analysis.evaluate-change-compatibility"], "formula compilation and evaluation receipts"),
    ("models_studies", "Studies, protocols, model artifacts, cohorts, evaluations and publications", ["model-study-lineage", "protocol-method", "reproducibility-package"], ["study", "model-artifact", "reproducibility-package"], ["packages-environment", "reproduces"], ["reproducibility.package-research-object", "impact-analysis.identify-affected-models-studies"], "study/run/reproduction appraisal receipts"),
    ("decisions_actions", "Claims and evidence considered by decisions and authorized actions", ["decision-action-lineage", "claim-evidence"], ["decision-occurrence", "action-occurrence", "claim"], ["informed-decision", "authorized-action"], ["claim-evidence.explain-reliance-decision", "impact-analysis.identify-affected-decisions"], "decision and action receipts"),
    ("security", "Identities, policies, keys, attestations, access and forensic events", ["security-lineage", "attestation", "audit-event"], ["verification-method", "attestation", "audit-event"], ["secured-by", "records-audit-event"], ["identity-integrity.verify-signature-envelope", "audit-accountability.correlate-audit-and-lineage"], "authorization, attestation and audit receipts"),
    ("governance", "Stewardship, classification, retention, hold, disclosure and lifecycle authority", ["governance-lineage", "retention-legal-hold", "disclosure"], ["legal-hold", "disclosure-package", "correction-notice"], ["subject-to-hold", "discloses", "corrects"], ["disclosure-retention.resolve-disclosure-authority", "correction-lifecycle.place-legal-hold"], "approval, disclosure and disposition receipts"),
    ("quality", "Rules, measurements, validation outcomes, exceptions and quality claims", ["quality-lineage", "claim-evidence", "defeaters"], ["claim", "evidence-item", "defeater"], ["supports", "undercuts"], ["claim-evidence.score-evidence-dimensions", "claim-evidence.register-defeater"], "quality-check and review receipts"),
    ("runtime", "Invocations, inputs, targets, outcomes, effects and resource cuts", ["runtime-lineage", "runtime-receipts", "audit-event"], ["run", "runtime-receipt", "audit-event"], ["emitted-receipt", "observed-output"], ["runtime-receipts.record-effect-outcome", "runtime-receipts.seal-runtime-receipt"], "durable invocation/effect receipt"),
    ("compiler", "Semantic closure, requirements, offers, proofs, degradations and output artifacts", ["compiler-receipts", "plan-execution-conformance"], ["compiler-receipt", "plan", "data-entity"], ["compiled-to", "had-plan"], ["compiler-receipts.match-requirement-to-offer", "compiler-receipts.emit-compiler-receipt"], "compiler binding receipt"),
]


CROSS_PLANE_MAPPINGS = [
    {
        "plane_id": plane, "edition": EDITION, "status": "candidate", "name": name,
        "context_refs": [f"context.lpe.{ref}" for ref in contexts],
        "entity_type_refs": [f"entity-type.lpe.{ref}" for ref in entities],
        "relation_type_refs": [f"relation-type.lpe.{ref}" for ref in relations],
        "operation_refs": [f"operation.lpe.{ref}" for ref in operations],
        "required_receipt": receipt,
        "non_inference": "Cross-plane correlation never erases each plane's identity, authority, time, granularity or evidence posture.",
    }
    for plane, name, contexts, entities, relations, operations, receipt in CROSS_PLANE_ROWS
]


# id, kind, owner context, effect boundary, public contracts, forbidden responsibilities,
# operation suffixes, source shorts
LIBRARY_ROWS = [
    ("prov-statement-algebra", "semantic_pure", "provenance-graph", "pure_no_io", ["ProvEntity", "ProvActivity", "ProvAgent", "ProvRelation", "QualifiedRelation", "ProvInstance"], ["assertion_issuer", "bundle_membership", "storage", "evidence_scoring"], ["provenance-graph.qualify-provenance-relation"], ["w3c.prov.dm", "w3c.prov.o"]),
    ("provenance-assertion", "semantic_pure", "provenance-assertion", "pure_no_io", ["ProvenanceAssertion", "AssertionIssuer", "AssertionBasis", "AssertionScope", "AssertionStatus"], ["proposition_semantics", "issuer_trust", "automatic_truth_acceptance", "storage"], ["provenance-graph.assert-provenance-relation", "provenance-graph.retract-provenance-assertion"], ["w3c.prov.dm", "w3c.prov.o"]),
    ("provenance-bundle", "semantic_pure", "provenance-bundle", "pure_no_io", ["ProvBundleId", "ProvBundleEdition", "ProvDescriptionRef", "ProvBundle", "CrossBundleMention"], ["statement_semantics", "assertion_acceptance", "interchange_encoding", "storage"], ["provenance-graph.construct-provenance-bundle", "provenance-graph.link-provenance-bundles"], ["w3c.prov.o", "w3c.prov.links", "w3c.prov.constraints"]),
    ("prov-constraints", "test_oracle", "provenance-graph", "pure_no_io", ["ProvConstraint", "ValidationFinding", "InferenceTrace"], ["graph_persistence", "automatic_truth_acceptance"], ["provenance-graph.validate-prov-constraints", "provenance-graph.infer-qualified-relation"], ["w3c.prov.constraints"]),
    ("prov-interchange", "provider_adapter", "provenance-bundle", "effectful_runtime", ["ProvProfile", "NamespaceMap", "LossReport"], ["semantic_ownership", "silent_loss", "bundle_membership"], ["provenance-graph.export-provenance-interchange"], ["w3c.prov.n", "w3c.prov.links"]),
    ("lineage-core", "semantic_pure", "logical-lineage", "pure_no_io", ["LineageNode", "LineageEdge", "LineageLayer", "Granularity", "Coverage"], ["capture_transport", "provider_identity", "impact_confirmation"], ["lineage-capture.capture-logical-edge", "lineage-capture.quarantine-ambiguous-lineage"], ["w3c.prov.dm", "openlineage.spec"]),
    ("openlineage-adapter", "provider_adapter", "runtime-lineage", "effectful_runtime", ["RunEventAdapter", "FacetRegistry", "ProducerVersion"], ["canonical_semantic_ownership", "event_delivery_guarantee"], ["lineage-capture.observe-run-inputs", "lineage-capture.observe-run-outputs"], ["openlineage.spec", "openlineage.facets"]),
    ("field-lineage", "algorithm_pure", "field-lineage", "pure_no_io", ["FieldPath", "FieldDependency", "TransformKind", "ExtractionGap"], ["sql_execution", "dataset_identity_authority"], ["lineage-capture.capture-field-edge", "impact-analysis.evaluate-change-compatibility"], ["openlineage.column"]),
    ("formula-provenance", "semantic_pure", "formula-lineage", "pure_no_io", ["FormulaAst", "OperandRole", "SemanticGrain", "UnitContract"], ["formula_execution", "metric_governance_approval"], ["lineage-capture.capture-formula-dependency", "impact-analysis.evaluate-change-compatibility"], ["sdmx.30"]),
    ("lineage-query", "algorithm_pure", "lineage-query", "pure_no_io", ["TraversalRequest", "GraphCut", "PathKind", "CoverageGap"], ["graph_storage", "confirmed_impact"], ["provenance-graph.slice-provenance-graph", "impact-analysis.compute-upstream-slice", "impact-analysis.compute-downstream-slice"], ["w3c.prov.aq"]),
    ("impact-analysis", "policy_pure", "impact-analysis", "pure_effect_intents", ["ImpactPath", "ImpactState", "ReviewPriority", "NotificationIntent"], ["notification_delivery", "business_impact_truth"], ["impact-analysis.classify-impact-path", "impact-analysis.prioritize-impact-review", "impact-analysis.confirm-impact"], ["w3c.prov.dm", "oasis.csaf"]),
    ("canonical-json", "algorithm_pure", "identity-digest", "pure_no_io", ["CanonicalJson", "CanonicalizationError"], ["claim_truth", "semantic_equivalence"], ["identity-integrity.canonicalize-json"], ["ietf.rfc8785"]),
    ("canonical-rdf", "algorithm_pure", "identity-digest", "pure_no_io", ["CanonicalRdf", "ComplexityBudget", "PoisonDatasetError"], ["claim_truth", "unbounded_execution"], ["identity-integrity.canonicalize-rdf"], ["w3c.rdf.canon"]),
    ("digest-core", "algorithm_pure", "identity-digest", "pure_no_io", ["DigestAlgorithm", "ContentDigest", "DigestScope"], ["semantic_identity", "truth", "key_management"], ["identity-integrity.compute-content-digest", "identity-integrity.verify-content-digest"], ["nist.fips180"]),
    ("signature-envelope", "algorithm_pure", "signature-seal", "pure_no_io", ["TypedPayload", "SignatureEnvelope", "VerificationResult"], ["key_custody", "issuer_authority", "claim_truth"], ["identity-integrity.create-signature-envelope", "identity-integrity.verify-signature-envelope"], ["intoto.dsse", "w3c.vc.integrity"]),
    ("verification-method-resolver", "provider_adapter", "signature-seal", "effectful_runtime", ["VerificationMethodQuery", "ResolvedMethod", "MethodStatus"], ["trust_policy", "claim_appraisal"], ["identity-integrity.resolve-verification-method"], ["w3c.did"]),
    ("attestation-core", "semantic_pure", "attestation", "pure_no_io", ["Statement", "PredicateType", "SubjectDescriptor", "Attestation"], ["signing", "independent_appraisal", "predicate_truth"], ["attestation-transparency.create-typed-attestation", "attestation-transparency.verify-attestation-envelope"], ["intoto.attestation"]),
    ("rats-appraisal", "policy_pure", "independent-appraisal", "pure_effect_intents", ["Evidence", "AppraisalPolicy", "AppraisalResult", "RelyingDecisionIntent"], ["evidence_collection", "relying_party_action"], ["attestation-transparency.appraise-attestation-evidence", "attestation-transparency.select-trust-anchor"], ["ietf.rfc9334"]),
    ("transparency-client", "provider_adapter", "transparency-registration", "effectful_runtime", ["SignedStatement", "RegistrationReceipt", "Checkpoint", "ConsistencyProof"], ["statement_truth", "transparency_service_operation"], ["attestation-transparency.register-transparent-statement", "attestation-transparency.verify-inclusion-receipt", "attestation-transparency.verify-consistency-proof"], ["ietf.rfc9942", "ietf.rfc9943"]),
    ("claim-argument-core", "semantic_pure", "claim-argument", "pure_no_io", ["Claim", "Argument", "Warrant", "SupportEdge", "Defeater"], ["evidence_collection", "automatic_adjudication"], ["claim-evidence.construct-argument", "claim-evidence.bind-evidence-to-claim", "claim-evidence.register-defeater"], ["omg.sacm"]),
    ("evidence-evaluation", "policy_pure", "evidence-strength", "pure_effect_intents", ["DimensionResult", "AuthorityAssessment", "FreshnessAssessment", "RelianceVerdict"], ["universal_scalar_score", "claim_truth", "policy_selection"], ["claim-evidence.score-evidence-dimensions", "claim-evidence.aggregate-evidence-under-policy"], ["omg.sacm", "ietf.rfc9334"]),
    ("evidence-bundle", "semantic_pure", "evidence-bundle", "pure_no_io", ["EvidenceManifest", "EvidenceMember", "BundleValidation", "BundleCoverageAssessment"], ["archive_storage", "member_truth", "disclosure_authorization", "redaction_or_selective_disclosure"], ["claim-evidence.bind-evidence-to-claim"], ["sigstore.bundle", "ietf.rfc8493"]),
    ("runtime-receipt-core", "semantic_pure", "runtime-receipts", "pure_effect_intents", ["Invocation", "EffectIntent", "EffectOutcome", "RuntimeReceipt"], ["effect_execution", "telemetry_collection"], ["runtime-receipts.open-invocation", "runtime-receipts.record-effect-outcome", "runtime-receipts.seal-runtime-receipt"], ["openlineage.spec", "ietf.rfc9942"]),
    ("receipt-store", "runtime_mechanism", "runtime-receipts", "effectful_runtime", ["ReceiptWriter", "ReceiptReader", "RetentionClass", "AppendOutcome"], ["semantic_success_inference", "receipt_schema_ownership"], ["runtime-receipts.seal-runtime-receipt", "runtime-receipts.verify-receipt-completeness"], ["ietf.rfc9942", "sec.17a4"]),
    ("compiler-evidence-binding", "policy_pure", "compiler-receipts", "pure_effect_intents", ["EvidenceRequirement", "CapabilityOffer", "BindingProof", "CompilerReceiptIntent"], ["provider_execution", "policy_authorship"], ["compiler-receipts.match-requirement-to-offer", "compiler-receipts.prove-mapping-soundness", "compiler-receipts.record-binding-decision"], ["slsa.provenance", "w3c.earl"]),
    ("audit-event-core", "semantic_pure", "audit-event", "pure_no_io", ["AuditEvent", "ActorRef", "ActionKind", "Outcome", "SequenceCoverage"], ["log_transport", "provenance_inference", "evidence_admissibility"], ["audit-accountability.emit-audit-event", "audit-accountability.normalize-audit-event"], ["nist.800.53", "ietf.rfc5424"]),
    ("audit-log-adapter", "provider_adapter", "audit-log", "effectful_runtime", ["LogSource", "RawEvent", "CanonicalAuditEvent", "LossReport"], ["raw_log_mutation", "automatic_evidence_promotion"], ["audit-accountability.collect-audit-log", "audit-accountability.detect-audit-gap"], ["nist.800.92", "otel.logs"]),
    ("audit-trail-reconstructor", "algorithm_pure", "audit-trail", "pure_no_io", ["RecordTransition", "TrailEntry", "Reconstruction", "TrailGap"], ["source_log_storage", "causal_lineage"], ["audit-accountability.reconstruct-record-history", "audit-accountability.review-audit-trail"], ["ecfr.part11", "ema.computerised"]),
    ("custody-core", "semantic_pure", "custody", "pure_effect_intents", ["CustodyEvent", "Custodian", "Seal", "Condition", "ContinuityVerdict"], ["physical_transfer", "legal_admissibility_determination"], ["custody-forensics.record-custody-transfer", "custody-forensics.verify-custody-continuity"], ["iso.27037"]),
    ("forensic-acquisition-adapter", "provider_adapter", "forensic-acquisition", "effectful_runtime", ["AcquisitionRequest", "SourceState", "ToolEdition", "ForensicImage", "AcquisitionReceipt"], ["authority_adjudication", "evidence_analysis"], ["custody-forensics.acquire-forensic-image", "custody-forensics.verify-acquisition-fixity"], ["nist.800.86", "iso.27037"]),
    ("preservation-core", "policy_pure", "forensic-preservation", "pure_effect_intents", ["PreservationObject", "PreservationEvent", "FixityPolicy", "MigrationIntent"], ["media_storage", "format_converter_implementation"], ["custody-forensics.perform-fixity-check", "custody-forensics.migrate-preserved-format"], ["premis.30", "nist.ir.8387"]),
    ("long-term-validation", "algorithm_pure", "long-term-validation", "pure_no_io", ["EvidenceRecord", "ArchiveTimestamp", "RenewalChain", "ValidationResult"], ["timestamp_authority", "perpetual_truth"], ["custody-forensics.renew-long-term-validation"], ["ietf.rfc4998", "ietf.rfc6283"]),
    ("research-object", "semantic_pure", "reproducibility-package", "pure_no_io", ["ResearchObject", "Manifest", "WorkflowRun", "EnvironmentSnapshot"], ["workflow_execution", "reproducibility_guarantee"], ["reproducibility.package-research-object", "reproducibility.validate-package-manifest"], ["rocrate.11", "workflow.run.crate"]),
    ("reproduction-evaluator", "test_oracle", "reproduction-appraisal", "pure_no_io", ["EquivalenceTarget", "ComparisonResult", "Divergence", "ReproductionAppraisal"], ["run_execution", "scientific_truth"], ["reproducibility.compare-reproduction-result", "reproducibility.explain-reproduction-divergence"], ["fair.principles", "nist.ir.8354"]),
    ("record-lifecycle", "semantic_pure", "correction", "pure_effect_intents", ["Correction", "Retraction", "Recall", "DeletionRequest", "Supersession"], ["storage_deletion", "legal_authority_selection"], ["correction-lifecycle.issue-correction", "correction-lifecycle.issue-retraction", "correction-lifecycle.issue-recall"], ["fda.electronic.2024", "oasis.csaf"]),
    ("retention-policy", "policy_pure", "retention-legal-hold", "pure_effect_intents", ["RecordClass", "RetentionSchedule", "LegalHold", "DispositionIntent"], ["legal_advice", "physical_destruction"], ["disclosure-retention.apply-retention-schedule", "correction-lifecycle.place-legal-hold"], ["sec.17a4", "cftc.131"]),
    ("disclosure-core", "policy_pure", "disclosure", "pure_effect_intents", ["DisclosureRequest", "DisclosureSelection", "OmissionMap", "DisclosurePackagePlan", "DisclosureDeliveryIntent", "DisclosureReceiptIntent"], ["authorization_issuance", "cryptographic_proof_generation", "delivery", "recipient_acceptance", "source_deletion"], ["disclosure-retention.select-disclosure-view", "disclosure-retention.apply-evidence-redaction", "disclosure-retention.verify-disclosure-package"], ["w3c.vc2", "w3c.odrl", "w3c.vc.bbs", "ietf.rfc9901"]),
]


LIBRARIES = [
    {
        "library_id": f"library.lpe.{lid}", "edition": EDITION, "status": "candidate",
        "library_kind": kind, "semantic_owner_ref": f"context.lpe.{owner}",
        "contributes_to_context_refs": [f"context.lpe.{owner}"], "effect_boundary": effect,
        "public_contracts": contracts, "operation_refs": [f"operation.lpe.{op}" for op in operations],
        "runtime_receipts": [f"{lid}_operation_receipt"] if effect != "pure_no_io" else [],
        "forbidden_responsibilities": forbidden,
        "removal_seams": ["All external formats/providers are behind typed adapters.", "Replacing this library cannot change owner-context semantics without a new contract edition."],
        "evidence_refs": [sid(ref) for ref in evidence],
        "gaps": ["Candidate library boundary; dependency and API qualification remain open."],
    }
    for lid, kind, owner, effect, contracts, forbidden, operations, evidence in LIBRARY_ROWS
]

PROV_STATEMENT_REFUSALS = [
    "StatementIdentityMissing", "SubjectIdentityMissing", "RelationKindUnknown",
    "RelationEndpointTypeMismatch", "QualificationRoleInvalid", "TimeConstraintInvalid",
    "AttributeConflict", "InstanceScopeMismatch", "UnsupportedProvProfile",
    "ResourceBudgetExceeded",
]
PROV_ASSERTION_REFUSALS = [
    "AssertionIdentityMissing", "IssuerIdentityMissing", "PropositionSetEmpty",
    "PropositionUnresolved", "AssertionScopeInvalid", "AssertionBasisInvalid",
    "AssertionRevisionConflict", "AssertionAlreadyRetracted", "SupersessionTargetInvalid",
    "CoverageUnknown", "ResourceBudgetExceeded",
]
PROV_BUNDLE_REFUSALS = [
    "BundleIdentityMissing", "BundleIdentifierConflict", "DescriptionSetEmpty",
    "DescriptionUnresolved", "DuplicateBundleIdentifier", "BundleEditionConflict",
    "MentionSourceUnresolved", "MentionTargetUnresolved", "CrossBundleScopeInvalid",
    "ExperimentalMentionNotPermitted", "ResourceBudgetExceeded",
]

PROV_STATEMENT_EXACT_API = {
    "public_types": [
        "ProvNodeId", "ProvEntityDescriptor", "ProvActivityDescriptor", "ProvAgentDescriptor",
        "ProvEntity", "ProvActivity", "ProvAgent", "ProvRelationKind", "ProvRelationDescriptor",
        "ProvRelation", "ProvRelationQualification", "QualifiedProvRelation", "ProvAttribute",
        "ProvTimeConstraint", "ProvStatement", "ProvInstance", "ProvProfileEdition",
        "ProvStatementRefusal",
    ],
    "public_traits": ["ProvStatementAlgebra"],
    "input_types": ["ProvEntityDescriptor", "ProvActivityDescriptor", "ProvAgentDescriptor", "ProvRelationDescriptor", "ProvRelationQualification", "ProvProfileEdition"],
    "output_types": ["ProvEntity", "ProvActivity", "ProvAgent", "ProvRelation", "QualifiedProvRelation", "ProvInstance"],
    "operations": [
        {"operation_ref": "operation.lpe.prov-statement.declare-entity", "name": "declare_entity", "input_types": ["ProvEntityDescriptor", "ProvProfileEdition"], "output_type": "Result<ProvEntity,ProvStatementRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.prov-statement.declare-activity", "name": "declare_activity", "input_types": ["ProvActivityDescriptor", "ProvProfileEdition"], "output_type": "Result<ProvActivity,ProvStatementRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.prov-statement.declare-agent", "name": "declare_agent", "input_types": ["ProvAgentDescriptor", "ProvProfileEdition"], "output_type": "Result<ProvAgent,ProvStatementRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.prov-statement.construct-relation", "name": "construct_prov_relation", "input_types": ["ProvRelationDescriptor", "ProvInstance", "ProvProfileEdition"], "output_type": "Result<ProvRelation,ProvStatementRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.provenance-graph.qualify-provenance-relation", "name": "qualify_prov_relation", "input_types": ["ProvRelation", "ProvRelationQualification", "ProvProfileEdition"], "output_type": "Result<QualifiedProvRelation,ProvStatementRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.prov-statement.assemble-instance", "name": "assemble_prov_instance", "input_types": ["ProvStatement", "ProvProfileEdition"], "output_type": "Result<ProvInstance,ProvStatementRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
    ],
    "error_contracts": PROV_STATEMENT_REFUSALS,
    "laws": [
        "entity activity agent relation statement instance assertion bundle document and serialization have distinct identities",
        "an entity description fixes the aspects asserted for its described cut and material change requires a distinct entity state",
        "activity start end usage generation invalidation and association times remain distinct constraints",
        "relation direction and endpoint types follow the declared PROV relation kind rather than display orientation",
        "qualification may add role plan activity event agent and time details but cannot change the underlying relation kind or endpoints",
        "derivation is not causation execution correctness attribution endorsement or truth",
        "the statement algebra constructs propositions and never supplies issuer authority acceptance bundle membership or persistence",
    ],
    "oracles": ["prov-dm-type-fixtures", "relation-direction-negative-twins", "qualification-equivalence-properties", "entity-fixed-aspect-model", "time-constraint-boundaries", "cross-implementation-differential"],
}

PROVENANCE_ASSERTION_EXACT_API = {
    "public_types": [
        "ProvenanceAssertionId", "ProvenanceAssertionEdition", "ProvStatementRef",
        "ProvPropositionSet", "AssertionIssuerRef", "AssertionBasis", "AssertionScope",
        "AssertionTime", "AssertionCoverage", "AssertionStatus", "ProvenanceAssertion",
        "AssertionTransition", "AssertionConflict", "ProvenanceAssertionPolicy",
        "ProvenanceAssertionRefusal",
    ],
    "public_traits": ["ProvenanceAssertionAlgebra"],
    "input_types": ["ProvPropositionSet", "AssertionIssuerRef", "AssertionBasis", "AssertionScope", "AssertionTime", "AssertionCoverage", "ProvenanceAssertionPolicy"],
    "output_types": ["ProvenanceAssertion", "AssertionTransition", "AssertionConflict"],
    "operations": [
        {"operation_ref": "operation.lpe.provenance-graph.assert-provenance-relation", "name": "issue_provenance_assertion", "input_types": ["ProvPropositionSet", "AssertionIssuerRef", "AssertionBasis", "AssertionScope", "AssertionTime", "AssertionCoverage", "ProvenanceAssertionPolicy"], "output_type": "Result<ProvenanceAssertion,ProvenanceAssertionRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.provenance-assertion.assess-conflict", "name": "assess_assertion_conflict", "input_types": ["ProvenanceAssertion", "ProvenanceAssertion", "ProvenanceAssertionPolicy"], "output_type": "Result<AssertionConflict,ProvenanceAssertionRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.provenance-graph.retract-provenance-assertion", "name": "retract_provenance_assertion", "input_types": ["ProvenanceAssertion", "AssertionIssuerRef", "AssertionBasis", "ProvenanceAssertionPolicy"], "output_type": "Result<AssertionTransition,ProvenanceAssertionRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.provenance-assertion.supersede", "name": "supersede_provenance_assertion", "input_types": ["ProvenanceAssertion", "ProvenanceAssertion", "AssertionIssuerRef", "ProvenanceAssertionPolicy"], "output_type": "Result<AssertionTransition,ProvenanceAssertionRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
    ],
    "error_contracts": PROV_ASSERTION_REFUSALS,
    "laws": [
        "a PROV statement proposition and an issuer-scoped provenance assertion are distinct identities",
        "an assertion binds exact propositions issuer basis scope issuance time coverage and policy edition",
        "recording integrity signature or bundle membership does not establish assertion truth authority sufficiency or acceptance",
        "conflicting assertions coexist unless an accountable policy and authority records an explicit adjudication outside this algebra",
        "retraction and supersession preserve the original immutable assertion and its history",
        "graph merge inference slicing normalization and export preserve assertion and issuer boundaries",
        "absence of an assertion or edge under open coverage never proves absence of dependency or occurrence",
    ],
    "oracles": ["assertion-identity-properties", "issuer-boundary-merge-negative-twins", "conflict-coexistence-model", "retraction-state-machine", "coverage-open-world-properties", "cross-implementation-differential"],
}

PROVENANCE_BUNDLE_EXACT_API = {
    "public_types": [
        "ProvBundleId", "ProvBundleEdition", "ProvDescriptionRef", "ProvDescriptionSet",
        "ProvBundleIdentity", "ProvBundle", "ProvBundleValidation", "ProvBundleMention",
        "CrossBundleMentionPolicy", "ProvBundlePolicy", "ProvBundleRefusal",
    ],
    "public_traits": ["ProvenanceBundleAlgebra"],
    "input_types": ["ProvBundleIdentity", "ProvDescriptionSet", "ProvBundlePolicy", "ProvBundle", "ProvDescriptionRef", "CrossBundleMentionPolicy"],
    "output_types": ["ProvBundle", "ProvBundleValidation", "ProvBundleMention"],
    "operations": [
        {"operation_ref": "operation.lpe.provenance-graph.construct-provenance-bundle", "name": "construct_provenance_bundle", "input_types": ["ProvBundleIdentity", "ProvDescriptionSet", "ProvBundlePolicy"], "output_type": "Result<ProvBundle,ProvBundleRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.provenance-bundle.validate", "name": "validate_provenance_bundle", "input_types": ["ProvBundle", "ProvBundlePolicy"], "output_type": "Result<ProvBundleValidation,ProvBundleRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.provenance-bundle.derive-edition", "name": "derive_provenance_bundle_edition", "input_types": ["ProvBundle", "ProvDescriptionSet", "ProvBundlePolicy"], "output_type": "Result<ProvBundle,ProvBundleRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.provenance-graph.link-provenance-bundles", "name": "link_provenance_bundles", "input_types": ["ProvBundle", "ProvDescriptionRef", "ProvBundle", "ProvDescriptionRef", "CrossBundleMentionPolicy"], "output_type": "Result<ProvBundleMention,ProvBundleRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
    ],
    "error_contracts": PROV_BUNDLE_REFUSALS,
    "laws": [
        "a provenance bundle is a named immutable set of provenance descriptions and can itself be described as an entity",
        "bundle identity and edition bind the exact description-member set",
        "each bundle is validated independently and no cross-bundle inference is implicit",
        "the same entity identifier described in different bundles does not by itself identify the same description occurrence",
        "cross-bundle mention is explicit profile-scoped and retains source target and bundle identities",
        "bundle membership does not imply issuer endorsement assertion truth evidence sufficiency or acceptance",
        "serialization namespace mapping storage and access are delegated to separate interchange repository and query contracts",
    ],
    "oracles": ["bundle-identity-properties", "independent-validation-fixtures", "duplicate-identifier-negative-twins", "cross-bundle-mention-model", "membership-nonendorsement-properties", "cross-implementation-differential"],
}

RETIRED_LIBRARY_COMPOSITIONS = [{
    "decision_id": "decision.lpe.retire-prov-core.v1",
    "retired_library_id": "library.lpe.prov-core",
    "edition": EDITION,
    "status": "retired_composition",
    "reason": "The candidate mixed PROV statement semantics, issuer-scoped assertion lifecycle and named bundle membership across three existing bounded-context authorities.",
    "replacement_library_refs": ["library.lpe.prov-statement-algebra", "library.lpe.provenance-assertion", "library.lpe.provenance-bundle"],
    "operation_partition": {
        "library.lpe.prov-statement-algebra": ["operation.lpe.provenance-graph.qualify-provenance-relation"],
        "library.lpe.provenance-assertion": ["operation.lpe.provenance-graph.assert-provenance-relation", "operation.lpe.provenance-graph.retract-provenance-assertion"],
        "library.lpe.provenance-bundle": ["operation.lpe.provenance-graph.construct-provenance-bundle", "operation.lpe.provenance-graph.link-provenance-bundles"],
    },
    "no_compatibility_alias": True,
    "evidence_refs": ["source.lpe.w3c.prov.dm", "source.lpe.w3c.prov.o", "source.lpe.w3c.prov.constraints", "source.lpe.w3c.prov.links"],
}]

EVIDENCE_BUNDLE_EXACT_API = {
    "public_types": [
        "EvidenceBundleId", "EvidenceBundleEdition", "EvidenceManifest", "EvidenceMember",
        "EvidenceMemberDescriptor", "ClaimRef", "ClaimEvidenceBinding", "EvidenceRequirementSet",
        "BundleCoverageAssessment", "BundleValidationPolicy", "ValidatedEvidenceBundle",
        "MemberValidation", "ClaimEvidenceBindingPolicy", "BundleCoveragePolicy",
        "EvidenceBundleRefusal",
    ],
    "public_traits": ["EvidenceBundleAlgebra"],
    "input_types": ["EvidenceBundleEdition", "BundleValidationPolicy", "EvidenceMember", "ClaimRef", "EvidenceRequirementSet", "ClaimEvidenceBindingPolicy", "BundleCoveragePolicy"],
    "output_types": ["ValidatedEvidenceBundle", "MemberValidation", "ClaimEvidenceBinding", "BundleCoverageAssessment"],
    "operations": [
        {"operation_ref": "operation.lpe.evidence-bundle.validate-manifest", "name": "validate_manifest", "input_types": ["EvidenceBundleEdition", "BundleValidationPolicy"], "output_type": "Result<ValidatedEvidenceBundle,EvidenceBundleRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.evidence-bundle.validate-member-integrity", "name": "validate_member_integrity", "input_types": ["ValidatedEvidenceBundle", "EvidenceMember", "BundleValidationPolicy"], "output_type": "Result<MemberValidation,EvidenceBundleRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.evidence-bundle.bind-evidence-to-claim", "name": "bind_evidence_to_claim", "input_types": ["ValidatedEvidenceBundle", "ClaimRef", "ClaimEvidenceBindingPolicy"], "output_type": "Result<ClaimEvidenceBinding,EvidenceBundleRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.evidence-bundle.evaluate-coverage", "name": "evaluate_bundle_coverage", "input_types": ["ValidatedEvidenceBundle", "EvidenceRequirementSet", "BundleCoveragePolicy"], "output_type": "Result<BundleCoverageAssessment,EvidenceBundleRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
    ],
    "error_contracts": ["BundleIdentityMissing", "BundleEditionInvalid", "ManifestInvalid", "MemberDescriptorInvalid", "MemberDigestMismatch", "MemberUnresolved", "ClaimUnresolved", "BindingScopeInvalid", "RequirementSetInvalid", "CoverageUnknown", "ResourceBudgetExceeded"],
    "laws": [
        "bundle identity binds an immutable manifest edition and exact member descriptors",
        "packaging membership integrity signature custody authority truth sufficiency and endorsement are distinct",
        "member digest verification establishes only scoped byte identity",
        "claim binding records role scope method time and residual gaps and never accepts the claim",
        "coverage is evaluated against one explicit requirement set and population",
        "authorization selection redaction selective disclosure delivery and receipt belong outside the evidence bundle algebra",
    ],
    "oracles": ["manifest-identity-properties", "member-digest-negative-twins", "claim-binding-scope-fixtures", "coverage-partiality-model", "disclosure-boundary-negative-twins", "cross-implementation-differential"],
}

DISCLOSURE_REFUSALS = [
    "DisclosureRequestIdentityMissing", "DisclosureRequestEditionInvalid", "RequesterUnresolved",
    "AudienceUnresolved", "RecipientUnresolved", "PurposeUnresolved", "SubjectScopeInvalid",
    "EvidenceScopeInvalid", "SourceBundleUnvalidated", "BundleCoverageUnknown",
    "AuthorizationDecisionMissing", "AuthorizationDecisionDenied", "AuthorizationScopeMismatch",
    "AuthorizationExpired", "AuthorizationRevoked", "PolicyEditionMissing", "PolicyConflict",
    "PermissionAbsent", "ProhibitionMatched", "DutyUnsatisfied", "ConstraintUnresolved",
    "MinimumNecessaryViewUnresolved", "MandatoryDisclosureConflict", "SelectionExceedsAuthority",
    "SelectionExceedsPurpose", "ForbiddenMemberSelected", "OmissionReasonMissing",
    "RedactionMappingIncomplete", "RedactionChangesSource", "SelectiveDisclosureMechanismMissing",
    "SelectiveDisclosureMechanismUnqualified", "MandatoryRevealUnsupported",
    "DerivedRepresentationLossUnresolved", "CorrelationRiskUnassessed", "LeakageRiskExceedsPolicy",
    "PackageManifestIncomplete", "PackageDigestMismatch", "PackagePolicyNonconformant",
    "DeliveryTargetUnresolved", "DeliveryConditionsIncomplete", "ReceiptScopeIncomplete",
    "ObservedReceiptUnbound", "UnknownDeliveryCompletion", "ResourceBudgetExceeded",
]

DISCLOSURE_EXACT_API = {
    "public_types": [
        "DisclosureRequestId", "DisclosureRequestEdition", "RequesterRef", "AudienceRef",
        "RecipientRef", "PurposeRef", "PurposeEdition", "SubjectScope", "EvidenceScope",
        "DisclosureRequest", "DisclosurePolicy", "DisclosurePolicyEdition", "DisclosurePermission",
        "DisclosureProhibition", "DisclosureDuty", "DisclosureConstraint", "ConstraintSatisfaction",
        "DisclosureAuthorizationDecisionRef", "AuthorizationValidity", "ValidatedEvidenceBundleRef",
        "BundleCoverageAssessmentRef", "EvidenceMemberRef", "DisclosurePartition",
        "MandatoryDisclosureSet", "PermittedDisclosureSet", "ForbiddenDisclosureSet",
        "DisclosureSelection", "OmissionReason", "OmissionEntry", "OmissionMap",
        "RedactionTransformRef", "RedactionPlan", "SelectiveDisclosureMechanismProfile",
        "MechanismCapabilityWitness", "DerivedRepresentationPlan", "CorrelationRiskFinding",
        "LeakageRiskFinding", "ResidualDisclosureRisk", "DisclosurePackageManifest",
        "DisclosurePackagePlan", "DisclosurePackageDigest", "DisclosureConformanceReport",
        "DisclosureDeliveryIntent", "DisclosureDeliveryObservation", "DisclosureReceiptIntent",
        "DisclosureReceiptObservation", "DisclosureResourceBudget", "DisclosureRefusal",
    ],
    "public_traits": ["DisclosurePolicyAlgebra", "DisclosureLifecycleReducer"],
    "input_types": [
        "DisclosureRequest", "DisclosurePolicy", "DisclosureAuthorizationDecisionRef",
        "ValidatedEvidenceBundleRef", "BundleCoverageAssessmentRef", "DisclosureSelection",
        "OmissionMap", "RedactionPlan", "SelectiveDisclosureMechanismProfile",
        "MechanismCapabilityWitness", "DisclosurePackagePlan", "DisclosureDeliveryObservation",
        "DisclosureReceiptObservation", "DisclosureResourceBudget",
    ],
    "output_types": [
        "DisclosurePartition", "DisclosureSelection", "RedactionPlan", "DerivedRepresentationPlan",
        "ResidualDisclosureRisk", "DisclosurePackagePlan", "DisclosureConformanceReport",
        "DisclosureDeliveryIntent", "DisclosureReceiptIntent", "DisclosureReceiptObservation",
    ],
    "operations": [
        {"operation_ref": "operation.lpe.disclosure-core.validate-request", "name": "validate_disclosure_request", "input_types": ["DisclosureRequest", "DisclosurePolicy", "DisclosureResourceBudget"], "output_type": "Result<DisclosureRequest,DisclosureRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.disclosure-core.bind-authorization", "name": "bind_authorization_decision", "input_types": ["DisclosureRequest", "DisclosureAuthorizationDecisionRef", "DisclosurePolicy"], "output_type": "Result<AuthorizationValidity,DisclosureRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.disclosure-core.partition-evidence", "name": "partition_evidence", "input_types": ["ValidatedEvidenceBundleRef", "BundleCoverageAssessmentRef", "DisclosureRequest", "AuthorizationValidity", "DisclosurePolicy"], "output_type": "Result<DisclosurePartition,DisclosureRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.disclosure-retention.select-disclosure-view", "name": "select_minimum_necessary_view", "input_types": ["DisclosurePartition", "DisclosureRequest", "DisclosurePolicy"], "output_type": "Result<DisclosureSelection,DisclosureRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.disclosure-retention.apply-evidence-redaction", "name": "plan_redaction", "input_types": ["DisclosureSelection", "OmissionMap", "RedactionTransformRef", "DisclosurePolicy"], "output_type": "Result<RedactionPlan,DisclosureRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.disclosure-core.plan-selective-disclosure", "name": "plan_selective_disclosure", "input_types": ["DisclosureSelection", "MandatoryDisclosureSet", "SelectiveDisclosureMechanismProfile", "MechanismCapabilityWitness"], "output_type": "Result<DerivedRepresentationPlan,DisclosureRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.disclosure-core.assess-residual-risk", "name": "assess_disclosure_residual_risk", "input_types": ["DisclosureSelection", "RedactionPlan", "DerivedRepresentationPlan", "DisclosurePolicy"], "output_type": "Result<ResidualDisclosureRisk,DisclosureRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.disclosure-retention.verify-disclosure-package", "name": "compose_and_verify_package_plan", "input_types": ["DisclosureRequest", "AuthorizationValidity", "DisclosureSelection", "OmissionMap", "RedactionPlan", "DerivedRepresentationPlan", "ResidualDisclosureRisk", "DisclosurePolicy"], "output_type": "Result<DisclosurePackagePlan,DisclosureRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.disclosure-core.form-delivery-intent", "name": "form_disclosure_delivery_intent", "input_types": ["DisclosurePackagePlan", "RecipientRef", "DisclosurePolicy"], "output_type": "Result<DisclosureDeliveryIntent,DisclosureRefusal>", "purity": "pure", "effect_intent_type": "DisclosureDeliveryIntent", "receipt_type": "DisclosureDeliveryObservation"},
        {"operation_ref": "operation.lpe.disclosure-core.reconcile-delivery", "name": "reconcile_disclosure_delivery", "input_types": ["DisclosureDeliveryIntent", "DisclosureDeliveryObservation", "DisclosurePolicy"], "output_type": "Result<DisclosureReceiptIntent,DisclosureRefusal>", "purity": "pure", "effect_intent_type": "DisclosureReceiptIntent", "receipt_type": "DisclosureReceiptObservation"},
    ],
    "error_contracts": DISCLOSURE_REFUSALS,
    "laws": [
        "request authorization selection package plan delivery intent provider observation receipt intent receipt observation and recipient acceptance are distinct identities",
        "authorization is imported from an accountable authority and is always scoped by requester audience recipient purpose subject evidence policy edition and validity",
        "permission prohibition duty and constraint remain distinct and unresolved conflicts refuse",
        "minimum necessary selection is policy-defined and absence from a disclosed view never proves absence falsehood or irrelevance in the source bundle",
        "mandatory permitted and forbidden evidence form an explicit partition before redaction or proof derivation",
        "redaction derives a new representation with an omission map and never mutates deletes or rewrites source evidence",
        "selective disclosure proof generation is performed by a qualified replaceable mechanism adapter and is not owned by this policy algebra",
        "selective disclosure does not imply unlinkability and structural metadata correlation and mandatory-reveal leakage remain explicit residual risks",
        "package integrity or cryptographic verification does not establish claim truth authority sufficiency fitness or recipient acceptance",
        "delivery intent does not establish delivery and provider acknowledgement does not establish recipient acceptance or business reliance",
        "unknown delivery completion remains explicit and must reconcile before a retry policy can authorize another attempt",
        "all results bind exact source bundle request authorization policy mechanism and transform editions",
        "time and authorization status are imported observations and this pure core reads no ambient clock identity policy or network state",
        "models agents and language models may propose selections but never issue authority suppress refusals or invent observations",
    ],
    "oracles": [
        "request-authorization-selection-negative-twins", "permission-prohibition-duty-precedence-model",
        "minimum-necessary-boundary-fixtures", "mandatory-permitted-forbidden-partition-properties",
        "omission-nonabsence-properties", "redaction-source-immutability-properties",
        "selective-disclosure-mechanism-conformance-fixtures", "mandatory-reveal-negative-twins",
        "correlation-and-leakage-adversarial-fixtures", "package-policy-conformance-model",
        "unknown-delivery-completion-state-machine", "intent-observation-acceptance-negative-twins",
        "resource-budget-boundaries", "cross-implementation-differential",
    ],
}

RUNTIME_RECEIPT_EXACT_API = {
    "public_types": [
        "InvocationId", "InvocationRevision", "InvocationRequest", "EffectIntentId", "EffectIntent",
        "EffectAttemptId", "EffectOutcome", "EffectCompletionState", "ExpectedEffectSet",
        "RuntimeReceipt", "SealedRuntimeReceipt", "RuntimeReceiptPolicy", "RuntimeReceiptRefusal",
    ],
    "public_traits": ["RuntimeReceiptAlgebra"],
    "input_types": ["InvocationRequest", "InvocationRevision", "EffectIntent", "EffectOutcome", "ExpectedEffectSet", "RuntimeReceiptPolicy"],
    "output_types": ["InvocationRevision", "EffectIntentTransition", "EffectOutcomeTransition", "SealedRuntimeReceipt", "ReceiptCompletenessAssessment"],
    "operations": [
        {"operation_ref": "operation.lpe.runtime-receipts.open-invocation", "name": "open_invocation", "input_types": ["InvocationRequest", "RuntimeReceiptPolicy"], "output_type": "Result<InvocationRevision,RuntimeReceiptRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.runtime-receipts.record-effect-intent", "name": "record_effect_intent", "input_types": ["InvocationRevision", "EffectIntent", "RuntimeReceiptPolicy"], "output_type": "Result<EffectIntentTransition,RuntimeReceiptRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.runtime-receipts.record-effect-outcome", "name": "record_effect_outcome", "input_types": ["InvocationRevision", "EffectOutcome", "RuntimeReceiptPolicy"], "output_type": "Result<EffectOutcomeTransition,RuntimeReceiptRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.runtime-receipts.seal-runtime-receipt", "name": "seal_runtime_receipt", "input_types": ["InvocationRevision", "RuntimeReceiptPolicy"], "output_type": "Result<SealedRuntimeReceipt,RuntimeReceiptRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
        {"operation_ref": "operation.lpe.runtime-receipts.verify-receipt-completeness", "name": "verify_receipt_completeness", "input_types": ["RuntimeReceipt", "ExpectedEffectSet", "RuntimeReceiptPolicy"], "output_type": "Result<ReceiptCompletenessAssessment,RuntimeReceiptRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None},
    ],
    "error_contracts": ["InvocationIdentityMissing", "InvocationVersionConflict", "EffectIntentDuplicate", "EffectAttemptUnbound", "OutcomeAttemptMismatch", "CompletionStateInvalid", "ExpectedEffectSetIncomplete", "UnknownCompletionUnreconciled", "ReceiptAlreadySealed", "ResourceBudgetExceeded"],
    "laws": [
        "invocation intent attempt provider acknowledgement observed outcome verified effect and accepted business outcome are distinct",
        "every retry creates a new effect-attempt identity under the same or a new intent according to policy",
        "unknown completion remains explicit and reconciles before retry",
        "a sealed receipt is immutable and binds exact input edition policy target attempts outcomes and residuals",
        "telemetry correlation does not manufacture a runtime receipt or effect truth",
        "receipt completeness is evaluated against one explicit expected-effect set",
    ],
    "oracles": ["invocation-state-model", "attempt-identity-properties", "unknown-completion-fault-fixtures", "receipt-sealing-properties", "expected-effect-coverage-model", "cross-implementation-differential"],
}

for library in LIBRARIES:
    exact_contract = {
        "library.lpe.prov-statement-algebra": PROV_STATEMENT_EXACT_API,
        "library.lpe.provenance-assertion": PROVENANCE_ASSERTION_EXACT_API,
        "library.lpe.provenance-bundle": PROVENANCE_BUNDLE_EXACT_API,
    }.get(library["library_id"])
    if exact_contract:
        library.update(exact_contract)
        for operation in library["operations"]:
            operation["refusal_types"] = exact_contract["error_contracts"]
    if library["library_id"] == "library.lpe.evidence-bundle":
        library.update(EVIDENCE_BUNDLE_EXACT_API)
        for operation in library["operations"]:
            operation["refusal_types"] = EVIDENCE_BUNDLE_EXACT_API["error_contracts"]
    if library["library_id"] == "library.lpe.disclosure-core":
        library.update(DISCLOSURE_EXACT_API)
        for operation in library["operations"]:
            operation["refusal_types"] = DISCLOSURE_EXACT_API["error_contracts"]
    if library["library_id"] == "library.lpe.runtime-receipt-core":
        library.update(RUNTIME_RECEIPT_EXACT_API)
        for operation in library["operations"]:
            operation["refusal_types"] = RUNTIME_RECEIPT_EXACT_API["error_contracts"]


# id, year, title, contribution, source shorts, boundary/limit
INNOVATION_ROWS = [
    ("trace-context-rec", 2021, "Trace Context Recommendation", "Standardized cross-service trace identifiers useful for correlation while remaining observability rather than evidence by default.", ["w3c.tracecontext"], "Correlation does not establish lineage or causality."),
    ("certificate-transparency-v2", 2021, "Certificate Transparency v2", "Updated append-only Merkle transparency and consistency proof model reusable as an evidence neighbor.", ["ietf.rfc9162"], "Log inclusion is not statement truth."),
    ("dsse-envelope", 2021, "Dead Simple Signing Envelope", "Bound payload type into a deliberately small signature envelope used by attestation ecosystems.", ["intoto.dsse"], "Signing still requires issuer-authority appraisal."),
    ("sdmx-3", 2021, "SDMX 3.0 information model", "Advanced versioned structural metadata for statistical data and metadata lineage.", ["sdmx.30"], "Statistical structure is not transformation execution evidence."),
    ("openlineage-ecosystem", 2021, "OpenLineage ecosystem maturation", "Made interoperable runtime job/run/dataset event lineage a shared ecosystem concern.", ["openlineage.spec"], "Producer coverage and correctness remain qualified."),
    ("did-core", 2022, "DID Core Recommendation", "Standardized identifier documents and verification-method relationships for portable issuer/key resolution.", ["w3c.did"], "Identifier control is not authority or truth."),
    ("rocrate-11", 2022, "RO-Crate 1.1", "Stabilized lightweight linked-data packaging for reproducible research objects.", ["rocrate.11"], "A package does not guarantee executable or scientific reproducibility."),
    ("intoto-attestation-v1", 2022, "in-toto Attestation Framework v1", "Separated a generic statement envelope from versioned predicate schemas and subjects.", ["intoto.attestation"], "Attestation is an authenticated assertion, not independent appraisal."),
    ("cose-structures", 2022, "COSE Structures RFC", "Standardized compact signed and authenticated structures for constrained evidence envelopes.", ["ietf.rfc9052"], "Cryptographic validity is only one evidence dimension."),
    ("csaf-20", 2022, "CSAF 2.0", "Standardized machine-readable advisory, affected-product status and remediation structures useful for recall propagation.", ["oasis.csaf"], "Product advisories are an explicit neighbor, not core data lineage."),
    ("digital-evidence-preservation", 2022, "NIST digital evidence preservation guidance", "Updated preservation considerations for cloud, digital objects and evidence-handler workflows.", ["nist.ir.8387"], "Guidance does not determine admissibility in a particular proceeding."),
    ("rats-architecture", 2023, "RATS architecture", "Separated attester, verifier and relying-party roles plus evidence, appraisal policy and appraisal results.", ["ietf.rfc9334"], "Remote-attestation terms must be profiled for enterprise analytics use."),
    ("slsa-v1", 2023, "SLSA v1 provenance and build track", "Stabilized build provenance predicates and progressive build assurance levels.", ["slsa.provenance", "slsa.build"], "Software build provenance is a neighbor and does not cover arbitrary data truth."),
    ("otel-logs-stable", 2023, "OpenTelemetry Logs stable data model", "Standardized event and observed timestamps plus trace correlation for portable logs.", ["otel.logs"], "Structured telemetry is not durable evidence without qualification."),
    ("ema-electronic-data", 2023, "EMA electronic clinical data guideline", "Required data-point audit trails, origin metadata, reviewability and protected change history in clinical trials.", ["ema.computerised"], "Regulatory applicability is jurisdiction and use-case scoped."),
    ("dcat3", 2024, "DCAT 3 Recommendation", "Added stronger version, dataset-series and checksum vocabulary for catalogs and preservation manifests.", ["w3c.dcat3"], "Catalog metadata is not runtime lineage evidence."),
    ("rdfc-10", 2024, "RDF Dataset Canonicalization 1.0", "Standardized deterministic graph canonicalization for signing, comparison and change sets.", ["w3c.rdf.canon"], "Canonicalization can be resource intensive and is not truth validation."),
    ("spdx3", 2024, "SPDX 3.0", "Expanded a graph-oriented artifact/build/dataset relationship model useful at the software/data provenance boundary.", ["spdx.3"], "SBOM relationships do not replace enterprise data derivation semantics."),
    ("cyclonedx16", 2024, "CycloneDX 1.6 attestations and declarations", "Added richer formulation, declarations and attestation structures around artifact supply chains.", ["cyclonedx.16"], "Artifact assertions require separate evidence appraisal."),
    ("ddi-cdi10", 2024, "DDI-CDI 1.0", "Provided cross-domain conceptual integration of data description, process and provenance.", ["ddi.cdi"], "Enterprise ownership and implementation bindings remain local."),
    ("workflow-run-crate", 2024, "Workflow Run RO-Crate profiles", "Unified prospective workflow descriptions with retrospective run provenance in portable research packages.", ["workflow.run.crate"], "Profile conformance does not prove complete dependency capture."),
    ("fda-electronic-records", 2024, "FDA electronic systems and records Q&A", "Updated expectations for trustworthy electronic records, certified copies, audit trails and signatures in clinical investigations.", ["fda.electronic.2024"], "Guidance is nonbinding and domain scoped."),
    ("vc20", 2025, "Verifiable Credentials 2.0", "Clarified claim, issuer, validity, status, evidence and verifier processing, including that verifiability does not imply truth.", ["w3c.vc2"], "Credential privacy and relying policy remain critical."),
    ("vc-data-integrity", 2025, "Verifiable Credential Data Integrity 1.0", "Standardized extensible integrity proofs over canonical credential data.", ["w3c.vc.integrity"], "Proof verification does not establish evidence relevance or truth."),
    ("eat-rfc", 2025, "Entity Attestation Token RFC", "Standardized compact typed claims for entity attestation evidence.", ["ietf.rfc9711"], "Claim profiles and verifier policy are deployment-specific."),
    ("cose-receipts", 2026, "COSE Receipts RFC", "Standardized portable cryptographic receipts for verifiable data structure inclusion.", ["ietf.rfc9942"], "Receipt verification says nothing about registered statement truth."),
    ("scitt-architecture", 2026, "SCITT architecture RFC", "Standardized signed-statement transparency roles, registration and receipts for trustworthy digital supply chains.", ["ietf.rfc9943"], "The architecture is an explicit neighbor; analytics evidence profiles are still required."),
]


INNOVATIONS = [
    {
        "innovation_id": f"innovation.lpe.{iid}", "edition": EDITION, "status": "candidate",
        "year": year, "name": title, "contribution": contribution, "limit": limit,
        "non_llm": True, "evidence_refs": [sid(ref) for ref in evidence],
    }
    for iid, year, title, contribution, evidence, limit in INNOVATION_ROWS
]


GAP_ROWS = [
    ("lineage-completeness", "No universal way exists to prove all relevant dependencies were captured across opaque providers and manual steps.", "research", ["openlineage.spec", "w3c.prov.dm"]),
    ("field-lineage-semantics", "Field-lineage extraction often lacks precise laws for predicates, aggregates, windows, UDFs, implicit casts and control dependencies.", "semantic", ["openlineage.column"]),
    ("record-cell-lineage-scale", "Exact record/cell lineage remains expensive and privacy-sensitive at enterprise scale.", "implementation", ["w3c.prov.dictionary"]),
    ("cross-system-identity", "Datasets, runs, fields, agents and policies lack universal stable cross-system identity.", "identity", ["w3c.prov.links", "w3c.did"]),
    ("edge-authority", "Many lineage formats record producer identity but not authority/competence to assert each edge.", "authority", ["openlineage.spec", "w3c.vc2"]),
    ("causality-vs-dependency", "Operational lineage graphs rarely distinguish data dependence, control dependence, correlation and causal effect rigorously.", "semantic", ["w3c.prov.dm"]),
    ("valid-time-provenance", "Event, recording, transaction and business-valid times are inconsistently captured across tools.", "time", ["w3c.owl.time", "otel.logs"]),
    ("stream-retraction-lineage", "Retractions, updates, late data, panes and state compaction complicate stable streaming lineage.", "semantic", ["openlineage.spec"]),
    ("privacy-preserving-lineage", "Useful impact paths can expose sensitive identities, formulas and dataset relationships.", "privacy", ["w3c.vc2"]),
    ("redacted-evidence-verifiability", "Portable, interoperable proof of authorized redaction and completeness remains immature.", "evidence", ["w3c.vc.integrity", "w3c.webanno"]),
    ("evidence-strength-calibration", "No provider-neutral universal evidence-strength scale is justified across scientific, operational, regulatory and forensic uses.", "evidence", ["omg.sacm", "nist.ir.8354"]),
    ("defeater-interchange", "Machine-readable defeaters and counterevidence lack widespread interoperable exchange profiles.", "evidence", ["omg.sacm"]),
    ("appraisal-policy-portability", "Attestation appraisal policies and results remain ecosystem- and verifier-specific.", "policy", ["ietf.rfc9334"]),
    ("receipt-finality", "External effects can remain indeterminate after timeout, crash or partition, preventing a clean final receipt.", "runtime", ["ietf.rfc9942"]),
    ("telemetry-qualification", "There is no universal threshold for promoting sampled/mutable observability telemetry to durable evidence.", "evidence", ["otel.logs", "nist.800.92"]),
    ("clock-trust", "Clock skew, backdating and uncertain trusted time complicate ordering and freshness claims.", "time", ["ietf.rfc3161", "ietf.rfc3339"]),
    ("algorithm-agility", "Long-lived evidence needs planned canonicalization, digest, signature and timestamp algorithm migration.", "preservation", ["ietf.rfc4998", "nist.fips180"]),
    ("cloud-forensic-custody", "Shared-responsibility cloud sources complicate acquisition authority, source state and custody continuity.", "forensics", ["nist.ir.8387", "iso.27037"]),
    ("reproducibility-external-services", "Mutable APIs, unavailable services, licensed data and hardware differences limit reruns.", "reproducibility", ["rocrate.11", "workflow.run.crate"]),
    ("semantic-result-equivalence", "Provider-neutral equivalence policies for statistical, approximate and nondeterministic analytical results remain domain-specific.", "reproducibility", ["fair.principles"]),
    ("correction-propagation", "Downstream copies, caches, extracts, decisions and publications rarely provide complete invalidation acknowledgement.", "lifecycle", ["oasis.csaf", "w3c.prov.dm"]),
    ("erasure-versus-evidence", "Privacy erasure can conflict with forensic preservation, audit retention and legal holds.", "governance", ["sec.17a4", "nist.ir.8387"]),
    ("impact-confirmation", "Graph reachability over-approximates confirmed semantic, regulatory, financial and safety impact.", "semantic", ["w3c.prov.dm"]),
    ("regulatory-jurisdiction", "Regulatory evidence, retention, signature and audit requirements vary by record class and jurisdiction.", "governance", ["ecfr.part11", "ema.computerised", "cftc.131"]),
    ("independent-review", "This finite research seed lacks independent domain, legal, scientific and forensic review.", "research", ["iso.19011"]),
]


GAPS = [
    {
        "gap_id": f"gap.lpe.{gid}", "edition": EDITION, "status": "candidate",
        "gap_kind": kind, "description": description, "blocking": False,
        "resolution_condition": "A scoped contract, primary evidence, conformance oracle and independent review resolve or narrow this gap.",
        "prohibited_fallback": "Do not silently infer completeness, truth, authority, causality or equivalence.",
        "evidence_refs": [sid(ref) for ref in evidence],
    }
    for gid, description, kind, evidence in GAP_ROWS
]


for context in CONTEXTS:
    context["cross_plane_refs"] = [
        row[0] for row in CROSS_PLANE_ROWS if context["context_id"] in {f"context.lpe.{ref}" for ref in row[2]}
    ]


METAMODEL = {
    "metamodel_id": "san.lineage-provenance-evidence-universe", "edition": EDITION,
    "status": "candidate", "completion_claim": False,
    "scope": "Provider-neutral lineage, provenance, derivation, evidence, audit trails, claim-argument-evidence, attestations, runtime/compiler receipts, impact, disclosure, custody, reproducibility, correction, retraction, recall and forensic preservation for enterprise data and analytics.",
    "core_exclusion": "LLM, generative and agentic semantics are excluded as core methods. Ordinary statistical/analytical model and study provenance remains in scope.",
    "open_world_law": "Enumeration is a candidate coverage position. Unknown nodes, edges, producers, authorities, evidence, semantics and affected subjects remain typed gaps.",
    "horizontal_decomposition": [
        "source and acquisition occurrence", "prospective plan", "runtime execution occurrence",
        "logical dependency", "physical materialization", "field/formula/schema dependency",
        "provenance assertion and bundle", "claim and argument", "evidence and defeaters",
        "attestation, verification and appraisal", "audit event/log/trail", "custody and preservation",
        "compiler/runtime receipts", "impact and invalidation", "correction/retraction/recall/deletion",
    ],
    "distinction_matrix": [
        {"left": "prospective_lineage", "right": "retrospective_lineage", "law": "declared possibility is not observed execution"},
        {"left": "logical_lineage", "right": "physical_lineage", "law": "semantic dependence is not byte/object movement"},
        {"left": "physical_lineage", "right": "runtime_lineage", "law": "artifact/materialization identity is not occurrence identity"},
        {"left": "data_derivation", "right": "process_execution", "law": "entity dependency is not inferred from shared execution, nor vice versa"},
        {"left": "audit_log", "right": "provenance_graph", "law": "accountability events and derivation/responsibility assertions retain distinct schemas"},
        {"left": "provenance_bundle", "right": "evidence_bundle", "law": "a named provenance set is not automatically sufficient evidence for a claim"},
        {"left": "assertion", "right": "attestation", "law": "an assertion need not be authenticated"},
        {"left": "attestation", "right": "independent_appraisal", "law": "issuer-authenticated statement is not independent evaluation"},
        {"left": "identity_or_digest", "right": "truth", "law": "representation identity/integrity does not prove proposition truth"},
        {"left": "recording_time", "right": "validity", "law": "capture time does not define when a proposition or credential applies"},
        {"left": "correction", "right": "deletion", "law": "amendment with preserved history is not removal"},
        {"left": "retraction", "right": "recall", "law": "withdrawal of reliance is not downstream product/artifact disposition"},
        {"left": "observability_telemetry", "right": "durable_evidence", "law": "telemetry needs explicit qualification for identity, integrity, retention, coverage and custody"},
    ],
    "time_axes": [
        "event_time", "observation_time", "recording_time", "transaction_time", "signing_time",
        "transparency_registration_time", "valid_from", "valid_until", "retrieval_time",
        "appraisal_time", "decision_time", "retention_start", "disposition_time",
    ],
    "assurance_postures": [
        "unverified_assertion", "integrity_verified", "issuer_authenticated", "authority_scoped",
        "method_validated", "corroborated", "independently_appraised", "adjudicated_for_policy",
    ],
    "forbidden_automatic_inferences": EVIDENCE_MODEL["non_inferences"],
    "compiler_law": "A semantic requirement binds only to versioned qualified offers whose guarantees, limits, evidence, validity and failure contracts pass explicit proof obligations; otherwise compilation refuses or records an authorized typed degradation.",
    "forbidden_core_dependencies": ["llm", "large_language_model", "prompt", "rag", "agent_memory", "generative_model"],
}


def array(items: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"type": "array", "items": items or {"type": "string"}, "uniqueItems": True}


STR = {"type": "string", "minLength": 1}
BOOL = {"type": "boolean"}
INT = {"type": "integer"}
STRINGS = array()

EXACT_OPERATION_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["operation_ref", "name", "input_types", "output_type", "purity", "effect_intent_type", "receipt_type", "refusal_types"],
    "properties": {
        "operation_ref": STR, "name": STR, "input_types": STRINGS, "output_type": STR,
        "purity": {"enum": ["pure", "effectful_explicit", "unresolved_refuse"]},
        "effect_intent_type": {"type": ["string", "null"]}, "receipt_type": {"type": ["string", "null"]},
        "refusal_types": STRINGS,
    },
}


def object_schema(title: str, required: list[str], properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "title": title,
        "type": "object", "additionalProperties": False, "required": required,
        "properties": properties,
    }


COMMON = {"edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"}}
REF_STATUS = {"edition": {"type": "integer", "minimum": 1}, "status": {"const": "reference"}}


SCHEMAS = {
    "source.schema.json": object_schema("LPE primary source", ["source_id", "edition", "status", "title", "publisher", "source_kind", "url", "publication_year", "accessed_on", "authority_scope", "topics", "limitations"], {
        "source_id": {"type": "string", "pattern": "^source\\.lpe\\."}, **REF_STATUS, "title": STR, "publisher": STR,
        "source_kind": STR, "url": {"type": "string", "format": "uri"}, "publication_year": INT,
        "accessed_on": {"type": "string", "format": "date"}, "authority_scope": STR, "topics": STRINGS, "limitations": STRINGS,
    }),
    "context.schema.json": object_schema("LPE bounded-context candidate", ["context_id", "edition", "status", "name", "family", "sovereign_question", "inside", "outside", "invariants", "neighbor_context_refs", "evidence_refs", "cross_plane_refs", "gaps"], {
        "context_id": {"type": "string", "pattern": "^context\\.lpe\\."}, **COMMON, "name": STR, "family": STR,
        "sovereign_question": STR, "inside": STRINGS, "outside": STRINGS, "invariants": STRINGS,
        "neighbor_context_refs": STRINGS, "evidence_refs": STRINGS, "cross_plane_refs": STRINGS, "gaps": STRINGS,
    }),
    "entity-type.schema.json": object_schema("LPE entity type candidate", ["entity_type_id", "edition", "status", "name", "family", "definition", "identity_rule", "mutable_reference", "owner_context_ref", "evidence_refs", "invalid_inferences"], {
        "entity_type_id": {"type": "string", "pattern": "^entity-type\\.lpe\\."}, **COMMON, "name": STR, "family": STR,
        "definition": STR, "identity_rule": STR, "mutable_reference": BOOL, "owner_context_ref": STR,
        "evidence_refs": STRINGS, "invalid_inferences": STRINGS,
    }),
    "relation-type.schema.json": object_schema("LPE relation type candidate", ["relation_type_id", "edition", "status", "name", "source_entity_type_ref", "target_entity_type_ref", "meaning", "invalid_inference", "owner_context_ref", "qualifiers", "evidence_refs"], {
        "relation_type_id": {"type": "string", "pattern": "^relation-type\\.lpe\\."}, **COMMON, "name": STR,
        "source_entity_type_ref": STR, "target_entity_type_ref": STR, "meaning": STR, "invalid_inference": STR,
        "owner_context_ref": STR, "qualifiers": STRINGS, "evidence_refs": STRINGS,
    }),
    "capability.schema.json": object_schema("LPE capability, operation, decision or law candidate", ["capability_id", "edition", "status", "candidate_kind", "family", "name", "definition", "owner_context_ref", "input_types", "output_types", "preconditions", "postconditions", "failure_modes", "refusal_law", "cross_plane_refs", "evidence_refs"], {
        "capability_id": {"type": "string", "pattern": "^(capability|operation|decision|law)\\.lpe\\."}, **COMMON,
        "candidate_kind": {"enum": ["capability", "operation", "decision", "law"]}, "family": STR, "name": STR,
        "definition": STR, "owner_context_ref": STR, "input_types": STRINGS, "output_types": STRINGS,
        "preconditions": STRINGS, "postconditions": STRINGS, "failure_modes": STRINGS, "refusal_law": STR,
        "cross_plane_refs": STRINGS, "evidence_refs": STRINGS,
    }),
    "rule.schema.json": object_schema("LPE invariant or refusal candidate", ["rule_id", "edition", "status", "rule_kind", "name", "statement", "disposition", "family", "evidence_refs"], {
        "rule_id": {"type": "string", "pattern": "^(law|refusal)\\.lpe\\."}, **COMMON,
        "rule_kind": {"enum": ["invariant", "refusal"]}, "name": STR, "statement": STR, "disposition": STR,
        "family": STR, "evidence_refs": STRINGS,
    }),
    "requirement.schema.json": object_schema("LPE capability requirement candidate", ["requirement_id", "edition", "status", "subject_context_ref", "operation_ref", "required_guarantees", "criticality", "evidence_gates", "fallback_law", "evidence_refs"], {
        "requirement_id": {"type": "string", "pattern": "^requirement\\.lpe\\."}, **COMMON,
        "subject_context_ref": STR, "operation_ref": STR, "required_guarantees": STRINGS,
        "criticality": {"enum": ["blocking", "degradable", "optional"]}, "evidence_gates": STRINGS,
        "fallback_law": STR, "evidence_refs": STRINGS,
    }),
    "offer.schema.json": object_schema("LPE provider-class offer candidate", ["offer_id", "edition", "status", "provider_class", "operation_ref", "offered_guarantees", "limits", "validity", "evidence_refs"], {
        "offer_id": {"type": "string", "pattern": "^offer\\.lpe\\."}, **COMMON, "provider_class": STR,
        "operation_ref": STR, "offered_guarantees": STRINGS, "limits": STRINGS,
        "validity": {"type": "object", "required": ["from", "until", "recheck_triggers"], "additionalProperties": False, "properties": {"from": {"type": ["string", "null"]}, "until": {"type": ["string", "null"]}, "recheck_triggers": STRINGS}},
        "evidence_refs": STRINGS,
    }),
    "compiler-mapping.schema.json": object_schema("LPE compiler mapping candidate", ["mapping_id", "edition", "status", "requirement_ref", "offer_ref", "operation_ref", "binding_phase", "match_rules", "proof_obligations", "fallback", "receipt_fields", "evidence_refs"], {
        "mapping_id": {"type": "string", "pattern": "^mapping\\.lpe\\."}, **COMMON, "requirement_ref": STR,
        "offer_ref": STR, "operation_ref": STR, "binding_phase": STR, "match_rules": STRINGS,
        "proof_obligations": STRINGS, "fallback": STR, "receipt_fields": STRINGS, "evidence_refs": STRINGS,
    }),
    "cross-plane.schema.json": object_schema("LPE cross-plane mapping candidate", ["plane_id", "edition", "status", "name", "context_refs", "entity_type_refs", "relation_type_refs", "operation_refs", "required_receipt", "non_inference"], {
        "plane_id": {"enum": [row[0] for row in CROSS_PLANE_ROWS]}, **COMMON, "name": STR, "context_refs": STRINGS,
        "entity_type_refs": STRINGS, "relation_type_refs": STRINGS, "operation_refs": STRINGS,
        "required_receipt": STR, "non_inference": STR,
    }),
    "library.schema.json": object_schema("LPE library boundary candidate", ["library_id", "edition", "status", "library_kind", "semantic_owner_ref", "contributes_to_context_refs", "effect_boundary", "public_contracts", "operation_refs", "runtime_receipts", "forbidden_responsibilities", "removal_seams", "evidence_refs", "gaps"], {
        "library_id": {"type": "string", "pattern": "^library\\.lpe\\."}, **COMMON, "library_kind": STR,
        "semantic_owner_ref": STR, "contributes_to_context_refs": STRINGS, "effect_boundary": STR,
        "public_contracts": STRINGS, "operation_refs": STRINGS, "runtime_receipts": STRINGS,
        "forbidden_responsibilities": STRINGS, "removal_seams": STRINGS, "evidence_refs": STRINGS, "gaps": STRINGS,
        "public_types": STRINGS, "public_traits": STRINGS, "input_types": STRINGS, "output_types": STRINGS,
        "operations": {"type": "array", "minItems": 1, "items": EXACT_OPERATION_SCHEMA},
        "error_contracts": STRINGS, "laws": STRINGS, "oracles": STRINGS,
    }),
    "retired-library-composition.schema.json": object_schema("LPE retired composite library boundary", ["decision_id", "retired_library_id", "edition", "status", "reason", "replacement_library_refs", "operation_partition", "no_compatibility_alias", "evidence_refs"], {
        "decision_id": {"type": "string", "pattern": "^decision\\.lpe\\."},
        "retired_library_id": {"type": "string", "pattern": "^library\\.lpe\\."},
        "edition": {"type": "integer", "minimum": 1}, "status": {"const": "retired_composition"},
        "reason": STR, "replacement_library_refs": STRINGS,
        "operation_partition": {"type": "object", "minProperties": 1, "additionalProperties": STRINGS},
        "no_compatibility_alias": {"const": True}, "evidence_refs": STRINGS,
    }),
    "innovation.schema.json": object_schema("LPE 2021-2026 innovation candidate", ["innovation_id", "edition", "status", "year", "name", "contribution", "limit", "non_llm", "evidence_refs"], {
        "innovation_id": {"type": "string", "pattern": "^innovation\\.lpe\\."}, **COMMON,
        "year": {"type": "integer", "minimum": 2021, "maximum": 2026}, "name": STR, "contribution": STR,
        "limit": STR, "non_llm": {"const": True}, "evidence_refs": STRINGS,
    }),
    "gap.schema.json": object_schema("LPE research gap candidate", ["gap_id", "edition", "status", "gap_kind", "description", "blocking", "resolution_condition", "prohibited_fallback", "evidence_refs"], {
        "gap_id": {"type": "string", "pattern": "^gap\\.lpe\\."}, **COMMON, "gap_kind": STR,
        "description": STR, "blocking": BOOL, "resolution_condition": STR, "prohibited_fallback": STR,
        "evidence_refs": STRINGS,
    }),
}


def main() -> None:
    SCHEMA.mkdir(exist_ok=True)
    for name, schema in SCHEMAS.items():
        dump_json(f"schema/{name}", schema)

    dump_json("metamodel.json", METAMODEL)
    dump_json("evidence-evaluation-model.json", EVIDENCE_MODEL)
    dump_jsonl("sources.jsonl", SOURCES)
    dump_jsonl("bounded-context-candidates.jsonl", CONTEXTS)
    dump_jsonl("entity-types.jsonl", ENTITIES)
    dump_jsonl("relation-types.jsonl", RELATIONS)
    dump_jsonl("capability-candidates.jsonl", CAPABILITIES)
    dump_jsonl("invariants-refusals.jsonl", INVARIANTS_REFUSALS)
    dump_jsonl("requirements.jsonl", REQUIREMENTS)
    dump_jsonl("offers.jsonl", OFFERS)
    dump_jsonl("compiler-mappings.jsonl", COMPILER_MAPPINGS)
    dump_jsonl("cross-plane-mappings.jsonl", CROSS_PLANE_MAPPINGS)
    dump_jsonl("library-boundaries.jsonl", LIBRARIES)
    dump_jsonl("retired-library-compositions.jsonl", RETIRED_LIBRARY_COMPOSITIONS)
    dump_jsonl("innovations.jsonl", INNOVATIONS)
    dump_jsonl("gaps.jsonl", GAPS)

    counts = {
        "authoritative_sources": len(SOURCES),
        "bounded_context_candidates": len(CONTEXTS),
        "entity_type_candidates": len(ENTITIES),
        "relation_type_candidates": len(RELATIONS),
        "capability_operation_decision_law_candidates": len(CAPABILITIES),
        "invariant_refusal_candidates": len(INVARIANTS_REFUSALS),
        "requirements": len(REQUIREMENTS),
        "offers": len(OFFERS),
        "compiler_mappings": len(COMPILER_MAPPINGS),
        "cross_plane_mappings": len(CROSS_PLANE_MAPPINGS),
        "library_boundaries": len(LIBRARIES),
        "retired_library_compositions": len(RETIRED_LIBRARY_COMPOSITIONS),
        "innovations_2021_2026": len(INNOVATIONS),
        "open_gaps": len(GAPS),
        "schemas": len(SCHEMAS),
    }
    dump_json("manifest.json", {
        "universe_id": "lineage_provenance_evidence", "edition": EDITION, "status": "candidate",
        "generated_on": ACCESSED, "completion_claim": False, "counts": counts,
        "generated_files": [
            "metamodel.json", "evidence-evaluation-model.json", "sources.jsonl",
            "bounded-context-candidates.jsonl", "entity-types.jsonl", "relation-types.jsonl",
            "capability-candidates.jsonl", "invariants-refusals.jsonl", "requirements.jsonl",
            "offers.jsonl", "compiler-mappings.jsonl", "cross-plane-mappings.jsonl",
            "library-boundaries.jsonl", "retired-library-compositions.jsonl", "innovations.jsonl", "gaps.jsonl",
        ] + [f"schema/{name}" for name in sorted(SCHEMAS)],
        "honest_limit": "Counts measure this finite candidate seed, not completeness, conformance or acceptance.",
    })


if __name__ == "__main__":
    main()
