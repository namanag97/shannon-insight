#!/usr/bin/env python3
"""Build exact metadata-discovery semantic and compiler contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for row in rows)


def S(ident: str, title: str, publisher: str, url: str, scope: str, limit: str, kind: str = "official_specification") -> dict:
    return {
        "source_id": f"source.metadata-discovery.{ident}",
        "title": title,
        "publisher": publisher,
        "url": url,
        "source_kind": kind,
        "claim_scope": scope,
        "scope_limit": limit,
    }


SOURCES = [
    S("w3c.dcat3", "Data Catalog Vocabulary (DCAT) Version 3", "W3C", "https://www.w3.org/TR/vocab-dcat-3/", "catalog, catalog record, resource, dataset, distribution, version and catalog-service distinctions", "DCAT interoperability terms do not prescribe storage, access policy, ranking, source authority or implementation architecture."),
    S("w3c.prov-o", "PROV-O: The PROV Ontology", "W3C", "https://www.w3.org/TR/prov-o/", "entity, activity, agent, attribution, derivation, collection and bundle provenance", "Provenance is evidence about origin and processing; it does not prove correctness, completeness or authority."),
    S("w3c.dqv", "Data on the Web Best Practices: Data Quality Vocabulary", "W3C", "https://www.w3.org/TR/vocab-dqv/", "quality measurements, annotations, certificates, metrics and provenance", "DQV deliberately does not define one universal objective notion of quality; fitness remains purpose- and policy-bound."),
    S("w3c.sparql11", "SPARQL 1.1 Query Language", "W3C", "https://www.w3.org/TR/sparql11-query/", "dataset selection, graph patterns, solution sequences, ordering, limits and result forms", "A query result is dataset-cut and regime bound; an empty result does not prove absence from a source population."),
    S("dublincore.terms", "DCMI Metadata Terms", "Dublin Core Metadata Initiative", "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/", "general resource-description properties and term status", "General metadata terms do not resolve domain identity, source precedence, catalog registration or access authority."),
    S("oai.pmh.2", "Open Archives Initiative Protocol for Metadata Harvesting 2.0", "Open Archives Initiative", "https://www.openarchives.org/OAI/openarchivesprotocol.html", "repository records, identifiers, datestamps, sets, deletion support and resumption tokens for incremental harvesting", "OAI record identifiers are not necessarily item identifiers; deletion and datestamp semantics are repository-protocol scoped."),
    S("ogc.api.records", "OGC API - Records", "Open Geospatial Consortium", "https://ogcapi.ogc.org/records/", "Web API building blocks for discovery and access to metadata records and collections", "Records API conformance does not establish domain truth, universal ranking semantics or unrestricted access to described resources."),
    S("rfc.9110", "RFC 9110: HTTP Semantics", "IETF", "https://www.rfc-editor.org/rfc/rfc9110.html", "representation metadata, validators, conditional requests and response semantics", "ETag and Last-Modified are protocol validators, not semantic asset identity, source completeness or business freshness."),
    S("rfc.8288", "RFC 8288: Web Linking", "IETF", "https://www.rfc-editor.org/rfc/rfc8288.html", "typed links, relation types, target attributes and link context", "A link relation is scoped to its context and registered or extension semantics; it does not prove equivalence or authority."),
    S("iso.19115.1", "ISO 19115-1:2014 Geographic Information — Metadata", "ISO", "https://www.iso.org/standard/53798.html", "metadata principles and requirements for geographic information and services", "The public catalog abstract supports boundary coverage only; paywalled clauses are not asserted here."),
    S("openmetadata.ingestion", "Metadata Ingestion Technical Architecture", "OpenMetadata", "https://docs.open-metadata.org/latest/developers/contribute/codebase-deep-dives/metadata-ingestion", "source-to-sink connector topology and extraction of external metadata into a catalog", "Implementation evidence illustrates connector boundaries; it is not a universal semantic standard or qualified SAN provider.", "official_implementation_documentation"),
    S("openmetadata.connectors", "Metadata Ingestion", "OpenMetadata", "https://docs.open-metadata.org/latest/connectors/ingestion", "scheduled workflows and connector coverage for database, dashboard, pipeline, messaging and storage metadata", "Connector availability and emitted fields are edition-specific implementation facts.", "official_implementation_documentation"),
    S("apache-atlas.overview", "Apache Atlas Overview", "Apache Software Foundation", "https://atlas.apache.org/", "metadata type and entity management, classifications, lineage, search and APIs", "Atlas entities and classifications demonstrate one implementation model and do not define universal catalog semantics.", "official_implementation_documentation"),
    S("apache-atlas.search", "Apache Atlas Advanced Search", "Apache Software Foundation", "https://atlas.apache.org/1.2.0/Search-Advanced.html", "typed metadata search, filters, ordering, pagination, active/deleted state and result envelopes", "Search behavior and state fields are Atlas-specific; retrieval and rank are not truth or certification.", "official_implementation_documentation"),
    S("ckan.api", "CKAN API Guide", "CKAN Association", "https://docs.ckan.org/en/2.11/api/", "versioned dataset, resource, activity, search, facets and pagination APIs", "CKAN package and search semantics are implementation evidence; result count and facets do not prove source-population completeness.", "official_implementation_documentation"),
]


def context(slug: str, name: str, question: str, outside: list[str]) -> dict:
    return {
        "context_id": f"context.metadata_discovery.{slug}",
        "name": name,
        "sovereign_question": question,
        "inside": ["exact identities", "editioned decisions", "typed operations", "laws", "refusals"],
        "outside": outside + ["provider qualification", "ambient persistence", "unauthorized external effects"],
        "owner": f"authority.metadata_discovery.{slug}",
        "status": "specified_candidate",
    }


CONTEXTS = [
    context("acquisition", "Metadata Acquisition", "For an exact source occurrence and extraction scope, what harvest work is requested, what was returned, what was rejected and when may its cursor advance?", ["source-system truth", "connector execution", "assertion publication", "asset mutation"]),
    context("catalog", "Catalog Assertion and Discovery", "For an exact catalog cut, which source-attributed assertion editions are valid and how are they projected, measured, searched and browsed without becoming source truth, certification or access authority?", ["described asset ownership", "universal source precedence", "physical search/index execution", "ontology glossary schema metric or policy approval"]),
    context("federation", "Catalog Federation", "Across exact peer catalog identities and editions, what records were harvested and how are identity alignment, conflicts, precedence, partial completion and provenance preserved?", ["global last-write-wins", "peer mutation", "global identity by shared label", "federation transport execution"]),
]


# DDD model boundaries and library seams are deliberately not one-to-one. Acquisition has a
# source-protocol/effect language; federation has a peer/conflict language; assertion lifecycle,
# derived projections, discovery queries and discovery measurements share the catalog model.
CONTEXT_BY_SEAM = {
    "acquisition_port": "acquisition",
    "assertion_record": "catalog",
    "discovery_projection": "catalog",
    "search_browse": "catalog",
    "federation": "federation",
    "freshness_coverage": "catalog",
}


DECISIONS: dict[str, list[str]] = {
    "acquisition_port": ["connector_profile", "source_occurrence_identity", "extraction_scope", "cursor_and_checkpoint", "deletion_semantics"],
    "assertion_record": ["assertion_identity", "observation_mode", "provenance_requirement", "temporal_model", "conflict_and_retraction"],
    "discovery_projection": ["projection_schema", "normalization_and_loss", "visibility_cut", "facet_and_browse_model", "projection_retirement"],
    "search_browse": ["query_language", "ranking_profile", "pagination_and_order", "freshness_requirement", "coverage_and_truncation"],
    "federation": ["peer_identity", "harvest_edition", "identity_alignment", "precedence_and_conflict", "partial_failure"],
    "freshness_coverage": ["observation_clock", "freshness_reference_event", "coverage_population", "unknown_and_late_posture", "slo_evaluation"],
}


DECISION_ROWS = [
    {
        "decision_id": f"decision.metadata_discovery.{ctx}.{decision}",
        "owner_context": f"context.metadata_discovery.{ctx}",
        "question": f"What exact {decision.replace('_', ' ')} applies?",
        "default": None,
        "default_law": "forbidden",
        "status": "declared",
    }
    for ctx, values in DECISIONS.items()
    for decision in values
]


def O(ctx: str, name: str, inputs: list[str], output: str, purity: str = "pure") -> dict:
    return {
        "operation_ref": f"operation.metadata_discovery.{ctx}.{name}",
        "input_types": inputs,
        "output_type": f"Result<{output},{''.join(part.title() for part in ctx.split('_'))}Refusal>",
        "purity": purity,
    }


SPECS = [
    {
        "id": "library.metadata_discovery.acquisition_port",
        "ctx": "acquisition_port",
        "name": "Metadata Acquisition Port",
        "kind": "effect_port",
        "types": ["SourceOccurrenceRef", "SourceEndpointRef", "ConnectorProfile", "ExtractionScope", "HarvestIntent", "HarvestAttemptId", "HarvestCursor", "CheckpointToken", "SourceRecordKey", "SourceRecordEnvelope", "DeletionSignal", "ExtractionReceipt", "NormalizationResidual", "CursorCommitIntent", "CursorCommitReceipt", "AcquisitionRefusal"],
        "ops": [
            O("acquisition_port", "plan_harvest", ["SourceOccurrenceRef", "ExtractionScope", "ConnectorProfile", "HarvestCursor"], "HarvestIntent"),
            O("acquisition_port", "interpret_extraction", ["HarvestIntent", "ExtractionReceipt", "DeletionPolicy", "NormalizationPolicy"], "InterpretedHarvest"),
            O("acquisition_port", "plan_cursor_commit", ["InterpretedHarvest", "CursorPolicy", "PriorCursorEvidence"], "CursorCommitIntent"),
            O("acquisition_port", "reconcile_cursor_receipt", ["CursorCommitIntent", "CursorCommitReceipt"], "ReconciledHarvestCursor"),
        ],
        "laws": [
            "Source occurrence, source item, protocol record, extracted envelope, metadata assertion and described asset are distinct identities.",
            "Harvest attempt, extraction receipt, accepted assertion edition and cursor commit are distinct lifecycle facts.",
            "A cursor advances only from an exact successful receipt under the selected checkpoint policy; completion unknown never advances it.",
            "Absence from one extraction is not deletion unless the source protocol supplies an exact deletion signal under declared semantics.",
            "Normalization preserves source payload reference, transformation profile and residual information loss.",
        ],
        "errors": ["SourceOccurrenceUnbound", "ConnectorProfileUnbound", "CursorConflict", "DeletionSemanticsUnknown", "NormalizationLossUnaccepted", "ExtractionCompletionUnknown"],
        "deps": [],
        "evidence": ["source.metadata-discovery.oai.pmh.2", "source.metadata-discovery.rfc.9110", "source.metadata-discovery.openmetadata.ingestion", "source.metadata-discovery.openmetadata.connectors"],
    },
    {
        "id": "library.metadata_discovery.assertion_record",
        "ctx": "assertion_record",
        "name": "Source-attributed Metadata Assertion",
        "kind": "effect_port",
        "types": ["MetadataAssertionId", "MetadataAssertionEdition", "DescribedSubjectRef", "MetadataPredicateRef", "MetadataValue", "ObservationMode", "StatementProvenance", "SourceRecordRef", "DerivationRef", "ValidityInterval", "RecordingInstant", "HarvestInstant", "ConfidenceStatement", "ConflictSet", "AssertionPublicationIntent", "AssertionPublicationReceipt", "AssertionRetractionIntent", "AssertionRefusal"],
        "ops": [
            O("assertion_record", "validate_assertion", ["MetadataAssertionDraft", "AssertionIdentityPolicy", "ProvenancePolicy", "TemporalPolicy"], "ValidatedMetadataAssertion"),
            O("assertion_record", "compare_editions", ["MetadataAssertionEdition", "MetadataAssertionEdition", "ComparisonPolicy"], "AssertionEditionDiff"),
            O("assertion_record", "plan_publication", ["ValidatedMetadataAssertion", "AssertionPublisherRef", "PublicationPolicy"], "AssertionPublicationIntent"),
            O("assertion_record", "plan_retraction", ["MetadataAssertionEdition", "RetractionEvidenceSet", "RetractionPolicy"], "AssertionRetractionIntent"),
        ],
        "laws": [
            "A metadata assertion describes a subject under exact provenance and time; it is not the described asset or source fact itself.",
            "Observed, declared, inferred, imported, proposed and corrected assertions remain distinct observation modes.",
            "Validity time, recording time, harvest time and publication time are separate clocks.",
            "Confidence does not establish truth, authority, identity or precedence.",
            "Correction, retraction, supersession and deletion are distinct and preserve prior editions and dependents.",
        ],
        "errors": ["SubjectUnresolved", "PredicateUnresolved", "ObservationModeUnknown", "ProvenanceMissing", "TemporalScopeAmbiguous", "ConflictUnresolved", "PublicationCompletionUnknown"],
        "deps": ["library.metadata_discovery.acquisition_port"],
        "evidence": ["source.metadata-discovery.w3c.dcat3", "source.metadata-discovery.w3c.prov-o", "source.metadata-discovery.dublincore.terms", "source.metadata-discovery.rfc.8288"],
    },
    {
        "id": "library.metadata_discovery.discovery_projection",
        "ctx": "discovery_projection",
        "name": "Discovery Projection",
        "kind": "effect_port",
        "types": ["DiscoveryProjectionId", "ProjectionEdition", "ProjectionCut", "DiscoveryDocumentId", "DiscoveryDocument", "CatalogRecordRef", "CatalogedResourceRef", "DatasetRef", "DistributionRef", "FacetDefinition", "FacetValue", "BrowseNodeId", "BrowseEdge", "VisibilityContext", "TransformationProfile", "ProjectionResidual", "ProjectionBuildIntent", "ProjectionBuildReceipt", "ProjectionRefusal"],
        "ops": [
            O("discovery_projection", "derive_document", ["MetadataAssertionEditionSet", "ProjectionSchema", "TransformationProfile", "ProjectionCut"], "DiscoveryDocument"),
            O("discovery_projection", "derive_facets", ["DiscoveryDocumentSet", "FacetPolicy", "ProjectionCut"], "FacetProjection"),
            O("discovery_projection", "derive_browse_graph", ["DiscoveryDocumentSet", "BrowsePolicy", "ProjectionCut"], "BrowseProjection"),
            O("discovery_projection", "plan_projection_build", ["DiscoveryDocumentSet", "FacetProjection", "BrowseProjection", "VisibilityContext"], "ProjectionBuildIntent"),
        ],
        "laws": [
            "Catalog record, cataloged resource, dataset, distribution, metadata assertion, discovery document and listing are distinct.",
            "A discovery projection is an immutable derived read model and never becomes its source assertions or described resources.",
            "Every projection binds an exact assertion cut, schema, transformation profile, visibility context and residual loss.",
            "Visibility in a projection is not access authorization, certification, endorsement, publication readiness or product eligibility.",
            "Removing a projection document does not retract its assertions or delete its described asset.",
        ],
        "errors": ["AssertionCutUnknown", "ProjectionSchemaUnbound", "TransformationLossUnaccepted", "VisibilityContextUnknown", "BrowseCycleForbidden", "ProjectionCompletionUnknown"],
        "deps": ["library.metadata_discovery.assertion_record"],
        "evidence": ["source.metadata-discovery.w3c.dcat3", "source.metadata-discovery.w3c.prov-o", "source.metadata-discovery.ogc.api.records", "source.metadata-discovery.ckan.api"],
    },
    {
        "id": "library.metadata_discovery.search_browse",
        "ctx": "search_browse",
        "name": "Search and Browse Semantics",
        "kind": "effect_port",
        "types": ["DiscoveryQueryId", "DiscoveryQuery", "QueryLanguageEdition", "FilterExpression", "FacetRequest", "BrowseRequest", "RankingProfile", "RankingSignal", "RankingEvidence", "PaginationCursor", "OrderingContract", "ResultWindow", "DiscoveryResult", "SearchExecutionIntent", "SearchExecutionReceipt", "ResultCoverageStatement", "QueryExplanation", "SearchBrowseRefusal"],
        "ops": [
            O("search_browse", "plan_search", ["DiscoveryQuery", "ProjectionCut", "VisibilityContext", "SearchBudget"], "SearchExecutionIntent"),
            O("search_browse", "plan_browse", ["BrowseRequest", "ProjectionCut", "VisibilityContext", "SearchBudget"], "SearchExecutionIntent"),
            O("search_browse", "interpret_result", ["SearchExecutionIntent", "SearchExecutionReceipt", "CoveragePolicy"], "DiscoveryResult"),
            O("search_browse", "explain_ranking", ["DiscoveryResult", "RankingProfile", "RankingEvidenceSet"], "QueryExplanation"),
        ],
        "laws": [
            "Search is an external read effect: the semantic library emits a cut-bound intent and interprets an exact receipt without hiding provider execution.",
            "Match, score, rank, relevance judgment, endorsement, certification and authorization are distinct.",
            "Ordering, pagination cursor, result window, truncation and total-hits relation are explicit; page stability is never assumed across cuts.",
            "An empty result proves only that the exact execution receipt returned no visible match under its query, cut, policy and budget.",
            "Model- or agent-generated query expansion remains attributed proposal input and cannot grant visibility or change deterministic filters.",
        ],
        "errors": ["QueryLanguageUnsupported", "ProjectionCutUnknown", "VisibilityContextUnknown", "RankingProfileUnbound", "FreshnessUnsatisfied", "ResultTruncated", "CoverageUnknown", "SearchCompletionUnknown"],
        "deps": ["library.metadata_discovery.discovery_projection"],
        "evidence": ["source.metadata-discovery.w3c.sparql11", "source.metadata-discovery.ogc.api.records", "source.metadata-discovery.apache-atlas.search", "source.metadata-discovery.ckan.api"],
    },
    {
        "id": "library.metadata_discovery.federation",
        "ctx": "federation",
        "name": "Catalog Federation",
        "kind": "effect_port",
        "types": ["CatalogPeerId", "CatalogPeerEdition", "PeerEndpointRef", "PeerTrustProfile", "FederationScope", "PeerHarvestToken", "PeerRecordEnvelope", "FederatedAssertion", "IdentityAlignment", "PrecedenceRule", "FederationConflict", "FederationConflictSet", "PartialPeerResult", "FederationHarvestIntent", "FederationHarvestReceipt", "FederationMergePlan", "FederationRefusal"],
        "ops": [
            O("federation", "plan_peer_harvest", ["CatalogPeerEdition", "FederationScope", "PeerHarvestToken", "FederationBudget"], "FederationHarvestIntent"),
            O("federation", "interpret_peer_receipt", ["FederationHarvestIntent", "FederationHarvestReceipt", "PeerProtocolPolicy"], "PeerHarvestResult"),
            O("federation", "align_peer_identities", ["PeerHarvestResultSet", "IdentityAlignmentPolicy"], "IdentityAlignmentSet"),
            O("federation", "derive_merge_plan", ["PeerHarvestResultSet", "IdentityAlignmentSet", "PrecedencePolicy", "ConflictPolicy"], "FederationMergePlan"),
        ],
        "laws": [
            "Peer catalog identity, peer record identity, described resource identity and local assertion identity remain distinct.",
            "Every federated assertion retains peer, record, edition, harvest and derivation provenance.",
            "Federation never invents ambient global last-write-wins, same-label identity, symmetric equivalence or transitive trust.",
            "Conflict preservation, precedence selection and identity alignment are separate decisions with separate evidence.",
            "Partial peer failure, token expiry, truncation and completion unknown remain visible in the merge plan.",
        ],
        "errors": ["PeerIdentityUnbound", "PeerProtocolUnsupported", "PeerTokenInvalid", "IdentityAlignmentAmbiguous", "PrecedenceUnbound", "ConflictUnresolved", "PartialCompletion"],
        "deps": ["library.metadata_discovery.acquisition_port", "library.metadata_discovery.assertion_record", "library.metadata_discovery.discovery_projection"],
        "evidence": ["source.metadata-discovery.w3c.dcat3", "source.metadata-discovery.oai.pmh.2", "source.metadata-discovery.ogc.api.records", "source.metadata-discovery.rfc.8288"],
    },
    {
        "id": "library.metadata_discovery.freshness_coverage",
        "ctx": "freshness_coverage",
        "name": "Discovery Freshness and Coverage",
        "kind": "algorithm_pure",
        "types": ["ObservationClock", "DiscoveryPopulation", "PopulationMemberRef", "CoverageScope", "PopulationCardinality", "FreshnessReferenceEvent", "FreshnessObservation", "FreshnessAge", "CoverageObservation", "CoverageNumerator", "CoverageDenominator", "UnknownMemberSet", "LateMemberSet", "DiscoverySlo", "DiscoverySloResult", "DiscoveryEvidenceReceipt", "MeasurementCompleteness", "FreshnessCoverageRefusal"],
        "ops": [
            O("freshness_coverage", "measure_freshness", ["FreshnessObservationSet", "ObservationClock", "FreshnessPolicy", "AsOfInstant"], "FreshnessMeasurement"),
            O("freshness_coverage", "measure_coverage", ["DiscoveryPopulation", "ObservedMemberSet", "CoveragePolicy", "AsOfInstant"], "CoverageMeasurement"),
            O("freshness_coverage", "evaluate_slo", ["FreshnessMeasurement", "CoverageMeasurement", "DiscoverySlo", "EvaluationPolicy"], "DiscoverySloResult"),
            O("freshness_coverage", "assemble_evidence", ["DiscoverySloResult", "MeasurementProvenance", "EvidencePolicy"], "DiscoveryEvidenceReceipt"),
        ],
        "laws": [
            "Freshness is measured from supplied observations and an explicit clock; a configured schedule is not an observed successful extraction.",
            "Coverage requires an explicit population, denominator, membership rule, scope, cut and as-of instant.",
            "Unknown population, zero population, no observations, late observations and zero covered members remain distinct.",
            "Freshness, coverage, content correctness, fitness for purpose, authority and availability are independent dimensions.",
            "An SLO pass is a policy-bound measurement result, not certification, source correctness or authorization.",
        ],
        "errors": ["ObservationClockUnbound", "ReferenceEventUnknown", "PopulationUnknown", "DenominatorInvalid", "ObservationMissing", "MeasurementIncomplete", "SloPolicyUnbound"],
        "deps": ["library.metadata_discovery.acquisition_port", "library.metadata_discovery.search_browse"],
        "evidence": ["source.metadata-discovery.w3c.dqv", "source.metadata-discovery.w3c.prov-o", "source.metadata-discovery.rfc.9110", "source.metadata-discovery.iso.19115.1"],
    },
]


def materialize(spec: dict) -> dict:
    ctx = spec["ctx"]
    return {
        "library_id": spec["id"],
        "name": spec["name"],
        "library_kind": spec["kind"],
        "semantic_owner_context": f"context.metadata_discovery.{CONTEXT_BY_SEAM[ctx]}",
        "status": "specified",
        "candidate_responsibility": spec["name"].lower(),
        "effect_boundary": "pure_effect_intents" if spec["kind"] == "effect_port" else "pure_no_io",
        "public_types": spec["types"],
        "public_traits": [spec["name"].replace(" ", "") + "Algebra"],
        "operation_refs": [op["operation_ref"] for op in spec["ops"]],
        "operations": spec["ops"],
        "decision_refs": [f"decision.metadata_discovery.{ctx}.{decision}" for decision in DECISIONS[ctx]],
        "configuration_contracts": [spec["name"].replace(" ", "") + "Policy"],
        "laws": spec["laws"],
        "invariants": [
            "published editions, projection cuts and effect receipts are immutable",
            "all identities, provenance, temporal scope, authority, visibility, coverage and results are explicit and edition bound",
            "unknown, absent, deleted, filtered, hidden, truncated, refused, partial and completion-unknown remain distinct",
        ],
        "error_contracts": spec["errors"] + ["UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
        "dependencies": spec["deps"],
        "evidence_refs": spec["evidence"],
        "oracles": ["canonical positive fixtures", "negative twins", "property and metamorphic laws", "state-machine model tests", "malformed and boundary corpus", "edition migration corpus", "two independent differential implementations"],
        "gaps": ["No implementation is qualified; two independent implementations and executed conformance remain required."],
        "must_not_own": ["described asset or source truth", "glossary ontology schema metric or policy authority", "access certification or marketplace fulfillment", "provider qualification", "unauthorized external effects"],
        "qualification_required": False,
    }


LIBRARIES = [materialize(spec) for spec in SPECS]


NEGATIVES = [
    ("record_asset", "A catalog record is the cataloged resource or dataset.", "Keep registration record, described resource, dataset and distribution identities distinct."),
    ("harvest_acceptance", "A successful extraction means every returned field is an accepted assertion.", "Validate, attribute and publish assertions separately from the extraction receipt."),
    ("absence_deletion", "A missing record in one harvest proves deletion.", "Require exact protocol deletion semantics or retain absence as unknown."),
    ("cursor_attempt", "Starting or scheduling a harvest permits cursor advancement.", "Advance only after an exact accepted cursor-commit receipt."),
    ("normalization_loss", "Normalized metadata is semantically identical to its source payload.", "Preserve transformation profile and residual information loss."),
    ("confidence_truth", "A high-confidence metadata assertion is true or authoritative.", "Keep confidence, provenance, authority and truth separate."),
    ("projection_source", "A discovery document is the source assertion or source record.", "Bind it as an immutable derived projection of exact assertion editions."),
    ("visibility_access", "Visibility in search grants access, certification or endorsement.", "Require independent policy, authority and effect decisions."),
    ("rank_truth", "Top-ranked result is the most relevant or correct asset in reality.", "Publish profile- and cut-bound ranking evidence only."),
    ("empty_absence", "Empty search results prove source-population absence.", "Report query cut, visibility, coverage, truncation and provider receipt."),
    ("federation_lww", "Federation may resolve every peer conflict with ambient latest-write-wins.", "Require explicit peer editions, precedence and conflict policy."),
    ("fresh_schedule", "A scheduled harvest proves fresh metadata.", "Measure freshness from supplied successful observations and an explicit clock."),
    ("slo_correctness", "Freshness and coverage SLO pass proves content correctness.", "Keep freshness, coverage, correctness, fitness and authority independent."),
    ("agent_authority", "A model or agent may establish identity, delete records, grant visibility or certify a result.", "Treat suggestions as attributed proposals subject to deterministic laws and named authority."),
]


NEGATIVE_ROWS = [
    {"negative_id": f"negative.metadata-discovery.{slug}", "unsafe_inference": unsafe, "required_behavior": behavior, "status": "active"}
    for slug, unsafe, behavior in NEGATIVES
]


COMPILER_ROWS = []
for lib in LIBRARIES:
    stem = lib["library_id"].removeprefix("library.")
    COMPILER_ROWS += [
        {"record_kind": "capability_requirement", "requirement_id": f"requirement.{stem}.implementation", "subject_ref": lib["library_id"], "required_operations": lib["operation_refs"], "required_decisions": lib["decision_refs"], "fallback_law": "refuse", "status": "declared"},
        {"record_kind": "capability_offer", "offer_id": f"offer.{stem}.reference", "subject_ref": lib["library_id"], "claimed_operations": lib["operation_refs"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
        {"record_kind": "binding_rule", "binding_rule_id": f"binding.{stem}", "requirement_ref": f"requirement.{stem}.implementation", "offer_ref": f"offer.{stem}.reference", "structural_match": True, "selection_law": "Structural match never promotes an unqualified or non-portable implementation.", "selectable": False, "status": "declared"},
    ]


FILES = {
    "sources.jsonl": SOURCES,
    "bounded-contexts.jsonl": CONTEXTS,
    "decision-points.jsonl": DECISION_ROWS,
    "library-contracts.jsonl": LIBRARIES,
    "compiler-contracts.jsonl": COMPILER_ROWS,
    "negative-twins.jsonl": NEGATIVE_ROWS,
}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = lines(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {
        "manifest_id": "metadata_discovery_governance_v0_1_0",
        "as_of": AS_OF,
        "edition": EDITION,
        "status": "specified_unimplemented_open_world",
        "files": digests,
        "completion_claim": False,
        "qualified_implementation_count": 0,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS metadata discovery: {len(SOURCES)} sources, {len(CONTEXTS)} contexts, {len(DECISION_ROWS)} decisions, {len(LIBRARIES)} exact libraries, {len(COMPILER_ROWS)} compiler contracts")


if __name__ == "__main__":
    main()
