#!/usr/bin/env python3
"""Build exact, provider-neutral data-product definition and publication contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "".join(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for r in rows)


def S(ident: str, title: str, publisher: str, url: str, scope: str, limit: str, kind: str = "official_specification") -> dict:
    return {"source_id": f"source.data-product-publication.{ident}", "title": title, "publisher": publisher,
            "url": url, "source_kind": kind, "claim_scope": scope, "scope_limit": limit}


SOURCES = [
    S("w3c.dcat3", "Data Catalog Vocabulary Version 3", "W3C", "https://www.w3.org/TR/vocab-dcat-3/", "catalog resource, record, dataset, distribution, data service, version and dataset-series distinctions", "DCAT describes catalog resources; it does not define a complete data product, readiness process, access grant or operated product boundary."),
    S("w3c.dwbp", "Data on the Web Best Practices", "W3C", "https://www.w3.org/TR/dwbp/", "metadata, identifiers, versioning, provenance, quality, access, preservation, feedback and republication", "Web publication guidance does not establish enterprise ownership, contractual acceptance or provider qualification."),
    S("w3c.dqv", "Data Quality Vocabulary", "W3C", "https://www.w3.org/TR/vocab-dqv/", "quality metrics, measurements, annotations, policies and certificates with provenance", "DQV intentionally does not define universal quality or make publisher self-assessment independent certification."),
    S("w3c.prov-o", "PROV-O: The PROV Ontology", "W3C", "https://www.w3.org/TR/prov-o/", "entity, activity, agent, attribution, derivation, generation, use and invalidation", "Provenance supports evidence and responsibility descriptions but does not prove correctness, authority or product readiness."),
    S("thoughtworks.designing-data-products", "Designing Data Products", "Thoughtworks", "https://martinfowler.com/articles/designing-data-products.html", "use-case-backward product identification, cohesive value and single domain ownership", "The design method supplies product hypotheses, not a normative exchange schema, runtime proof or universal boundary verdict.", "primary_practitioner_method"),
    S("lf.odps4.1", "Open Data Product Specification 4.1", "Linux Foundation", "https://opendataproducts.org/v4.1/", "machine-readable product details, use cases, holder, access, quality, SLA, contract, license and lifecycle metadata", "ODPS is an interoperability profile; optional fields and lifecycle labels do not establish semantic completeness, readiness or effect completion."),
    S("lf.odcs3.1", "Open Data Contract Standard 3.1", "Linux Foundation AI & Data", "https://bitol-io.github.io/open-data-contract-standard/v3.1.0/", "editioned data-contract identity, purpose, schema, quality, SLA, roles and server references", "A product references exact contracts; neither ODCS conformance nor an embedded contract proves observed attainment or acceptance."),
    S("datacite.kernel4.4", "DataCite Metadata Schema 4.4", "DataCite", "https://schema.datacite.org/meta/kernel-4.4/doc/DataCite-MetadataKernel_v4.4.pdf", "persistent identifiers and typed version, part, derivation, documentation, review and obsolescence relations", "Citation metadata does not define product semantics, access, publication authority or dependency closure."),
    S("cncf.cloudevents1", "CloudEvents Specification 1.0", "CNCF", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", "event occurrence identity, source, type, subject, time, content type and data-schema references", "CloudEvents specifies an envelope, not delivery guarantees, subscriber acceptance or business event semantics."),
    S("w3c.websub", "WebSub", "W3C", "https://www.w3.org/TR/websub/", "publisher, hub, subscriber, subscription verification, leases and authenticated content distribution", "Subscription and transport receipts do not prove that every consumer received, understood or migrated from a change."),
    S("ietf.rfc9745", "RFC 9745: Deprecation HTTP Response Header", "IETF", "https://www.rfc-editor.org/rfc/rfc9745.html", "deprecation instant, deprecation link and distinction from changed resource behavior", "HTTP deprecation applies to identified resources and is not a complete product migration, recall or decommission protocol."),
    S("ietf.rfc8594", "RFC 8594: The Sunset HTTP Header Field", "IETF", "https://www.rfc-editor.org/rfc/rfc8594.html", "declared time after which a URI is expected to become unresponsive", "Sunset is not deprecation, consumer migration, safe decommission or deletion evidence."),
    S("ietf.rfc9110", "RFC 9110: HTTP Semantics", "IETF", "https://www.rfc-editor.org/rfc/rfc9110.html", "resource representations, validators, conditional requests, status and caching semantics", "Protocol success and validators do not establish semantic identity, publication approval or consumer acceptance."),
    S("ietf.rfc8493", "RFC 8493: BagIt File Packaging Format", "IETF", "https://www.rfc-editor.org/info/rfc8493/", "portable arbitrary-content package, payload/tag manifests, completeness and checksum validity", "A complete valid bag proves package structure and byte integrity, not semantic completeness, safety or product substitutability."),
    S("ro-crate.1.1", "RO-Crate Metadata Specification 1.1", "Research Object Crate", "https://www.researchobject.org/ro-crate/specification/1.1/", "self-describing aggregate of data, metadata, contextual entities and external references", "RO-Crate is one packaging profile and does not define enterprise product ports, policy, readiness or exit obligations."),
    S("oci.descriptor1.1", "OCI Image Descriptor Specification", "Open Container Initiative", "https://specs.opencontainers.org/image-spec/descriptor/?v=v1.1.0", "media type, digest, size, artifact type, annotations and content verification", "OCI descriptors are content-addressing evidence and do not turn a data product into a container image or prove semantic equivalence."),
    S("rda.fair-maturity1", "FAIR Data Maturity Model 1.0", "Research Data Alliance", "https://www.rd-alliance.org/groups/fair-data-maturity-model-wg/outputs/?output=94549", "prioritized indicators for findability, accessibility, interoperability and reuse", "FAIR indicators are scoped assessment criteria, not universal product readiness, quality or certification."),
    S("google.sre-slo", "Service Level Objectives", "Google SRE", "https://sre.google/sre-book/service-level-objectives/", "SLIs, SLOs and user-visible service expectations", "SLO attainment is operational evidence, not data correctness, semantic compatibility or publication authority."),
    S("team-topologies.organization", "Organization Dynamics with Team Topologies", "Team Topologies", "https://teamtopologies.com/s/Organization-Dynamics-with-Team-Topologies-Mini-book-MB80.pdf", "team ownership, interaction modes, cognitive load and architecture-team boundaries", "Team assignment informs operability but does not itself define product identity, semantic ownership or accountability authority."),
]


def C(slug: str, name: str, question: str, outside: list[str]) -> dict:
    return {"context_id": f"context.data_product_publication.{slug}", "name": name, "sovereign_question": question,
            "inside": ["exact product identities", "immutable editions", "typed decisions", "laws and refusals"],
            "outside": outside + ["provider qualification", "ambient persistence", "unauthorized external effects"],
            "owner": f"authority.data_product_publication.{slug}", "status": "specified_candidate"}


CONTEXTS = [
    C("definition", "Data Product Definition", "For one independently owned product promise, what stable identity, immutable edition, ports, external contracts, distributions, dependencies, accountability and support bindings constitute it?", ["dataset, source, schema, contract, distribution or organizational identity ownership", "physical pipeline, serving or access execution", "marketplace offers"]),
    C("readiness", "Data Product Readiness", "Against an exact criteria edition and product cut, what evidence satisfies which readiness requirements, what remains residual, and whose assessment or certificate is being referenced?", ["independent assurance authority", "universal fitness or quality", "publication approval", "provider self-qualification"]),
    C("lifecycle", "Data Product Publication Lifecycle", "For an exact ready product edition, what publication, visibility, change, deprecation, recall, export and decommission intents and receipts preserve consumers, dependencies and history?", ["catalog search projection", "marketplace listing", "subscription eligibility", "access provisioning", "physical data deletion"]),
]


CONTEXT_BY_SEAM = {
    "product_edition": "definition", "port_assembly": "definition", "accountability_binding": "definition",
    "readiness_evidence": "readiness", "publication_protocol": "lifecycle", "consumer_change": "lifecycle", "recall_exit": "lifecycle",
}


DECISIONS = {
    "product_edition": ["identity_authority", "identity_scheme", "edition_semantics", "product_kind_and_scope", "purpose_value_and_job_refs", "supersession_relation"],
    "port_assembly": ["port_taxonomy", "input_output_role", "binding_exactness", "compatibility_requirement", "dependency_closure", "distribution_and_location_posture"],
    "accountability_binding": ["role_vocabulary", "responsibility_scope", "authority_evidence", "segregation_of_duties", "support_model", "delegation_and_revocation"],
    "readiness_evidence": ["criteria_profile", "evidence_cut_and_freshness", "satisfaction_relation", "assessor_independence", "residual_and_exception_posture", "verdict_expiry"],
    "publication_protocol": ["publication_authority", "visibility_scope", "effective_time", "target_registry", "idempotency_and_reconciliation", "unpublish_posture"],
    "consumer_change": ["change_classification", "compatibility_relation", "subscriber_population_and_cut", "notice_window", "in_flight_disposition", "delivery_and_reconciliation"],
    "recall_exit": ["recall_authority_and_scope", "dependency_blast_radius", "propagation_posture", "exit_package_profile", "consumer_and_in_flight_obligations", "decommission_gate"],
}


DECISION_ROWS = [{"decision_id": f"decision.data_product_publication.{seam}.{d}",
                  "owner_context": f"context.data_product_publication.{CONTEXT_BY_SEAM[seam]}",
                  "question": f"What exact {d.replace('_', ' ')} applies?", "default": None,
                  "default_law": "forbidden", "status": "declared"}
                 for seam, values in DECISIONS.items() for d in values]


def O(seam: str, name: str, inputs: list[str], output: str) -> dict:
    return {"operation_ref": f"operation.data_product_publication.{seam}.{name}", "input_types": inputs,
            "output_type": f"Result<{output},{''.join(x.title() for x in seam.split('_'))}Refusal>", "purity": "pure"}


SPECS = [
    {"id": "library.data_product_publication.product_edition", "seam": "product_edition", "name": "Data Product Identity and Edition", "kind": "effect_port",
     "types": ["DataProductId", "DataProductSeriesRef", "DataProductEditionId", "ProductIdentityAuthorityRef", "ProductKind", "ProductScope", "DomainRef", "JobRef", "OutcomeRef", "ValuePropositionRef", "PurposeRef", "ProductStatus", "ValidityInterval", "RecordingInstant", "EditionDigest", "EditionRelation", "ProductEditionDraft", "ValidatedProductEdition", "ProductRegistrationIntent", "ProductRegistrationReceipt", "ProductSupersessionIntent", "ProductEditionRefusal"],
     "ops": [O("product_edition", "validate_product_edition", ["ProductEditionDraft", "IdentityPolicy", "EditionPolicy", "ProductIdentityAuthorityRef"], "ValidatedProductEdition"), O("product_edition", "compare_product_editions", ["DataProductEdition", "DataProductEdition", "ComparisonPolicy"], "ProductEditionDiff"), O("product_edition", "plan_product_registration", ["ValidatedProductEdition", "ProductRegistryRef", "RegistrationAuthority"], "ProductRegistrationIntent"), O("product_edition", "plan_product_supersession", ["DataProductEditionId", "DataProductEditionId", "SupersessionEvidence", "SupersessionPolicy"], "ProductSupersessionIntent")],
     "laws": ["Data product, product series, immutable product edition, dataset, table, API, model, report, application, marketplace offer and deployment are distinct identities.", "Product identifier, human name, registry occurrence, catalog record and provider package digest are distinct.", "A product edition binds a scoped promise, intended jobs and outcomes; it does not acquire source-fact, dataset, purpose-taxonomy or consumer-outcome truth.", "Draft, validated, registered, ready, approved, published, deprecated, recalled and decommissioned remain distinct states.", "Supersession, replacement, compatibility, deprecation and obsolescence are explicit directional relations and never inferred from a larger version string.", "Registration and supersession are effect intents reconciled from exact receipts; no pure operation mutates a registry."],
     "errors": ["IdentityAuthorityMissing", "ProductIdentityCollision", "ProductScopeAmbiguous", "EditionConflict", "PurposeRefUnresolved", "OutcomeRefUnresolved", "SupersessionInvalid", "RegistrationCompletionUnknown"], "deps": [],
     "evidence": ["source.data-product-publication.w3c.dcat3", "source.data-product-publication.w3c.dwbp", "source.data-product-publication.datacite.kernel4.4", "source.data-product-publication.lf.odps4.1", "source.data-product-publication.thoughtworks.designing-data-products"]},
    {"id": "library.data_product_publication.port_assembly", "seam": "port_assembly", "name": "Data Product Port and Dependency Assembly", "kind": "algorithm_pure",
     "types": ["ProductPortId", "ProductPortEdition", "PortDirection", "InputPort", "OutputPort", "ManagementPort", "ContractEditionRef", "SchemaEditionRef", "DatasetEditionRef", "DistributionEditionRef", "DataServiceRef", "PolicyEditionRef", "QualityProfileRef", "SloProfileRef", "LineageCutRef", "DependencyEdge", "DependencyGraph", "CompatibilityRequirement", "BindingResidual", "ClosedPortAssembly", "PortAssemblyRefusal"],
     "ops": [O("port_assembly", "bind_product_port", ["DataProductEditionId", "ProductPortDraft", "ExternalEditionBindings", "PortPolicy"], "BoundProductPort"), O("port_assembly", "assemble_dependency_graph", ["BoundProductPortSet", "DependencyEdgeSet", "DependencyPolicy"], "DependencyGraph"), O("port_assembly", "validate_port_closure", ["DependencyGraph", "CompatibilityEvidenceSet", "ClosurePolicy"], "ClosedPortAssembly"), O("port_assembly", "derive_dependency_impact", ["ClosedPortAssembly", "ExternalEditionChangeSet", "ImpactPolicy"], "DependencyImpact")],
     "laws": ["Product port, contract, schema, dataset, distribution, data service, endpoint, credential and physical location are distinct.", "The product binds exact externally owned editions and never copies their semantic or effect authority.", "Input, output and management ports remain distinct; direction is relative to the product boundary and never inferred from a connector name.", "A distribution is one representation or availability form and is not the dataset, product or delivered occurrence.", "Dependency closure includes semantic, policy, data, runtime, evidence and support dependencies with explicit compatibility requirements.", "A closed structural graph is not runtime availability, contract acceptance, observed quality or consumer fitness."],
     "errors": ["PortIdentityCollision", "DirectionAmbiguous", "ExternalEditionUnbound", "CompatibilityUnknown", "DependencyCycleForbidden", "DependencyGraphOpen", "BindingResidualUnaccepted", "LocationMistakenForIdentity"], "deps": ["library.data_product_publication.product_edition"],
     "evidence": ["source.data-product-publication.w3c.dcat3", "source.data-product-publication.lf.odps4.1", "source.data-product-publication.lf.odcs3.1", "source.data-product-publication.w3c.prov-o"]},
    {"id": "library.data_product_publication.accountability_binding", "seam": "accountability_binding", "name": "Data Product Accountability and Support Binding", "kind": "effect_port",
     "types": ["AccountabilityBindingId", "ProductOwnerRef", "StewardRef", "CustodianRef", "PublisherRef", "SupportOwnerRef", "DecisionRightRef", "ResponsibilityScope", "AuthorityEvidenceRef", "DelegationRef", "SegregationRuleRef", "SupportChannelRef", "SupportWindow", "EscalationPolicyRef", "AccountabilityAssignmentIntent", "AccountabilityAssignmentReceipt", "AccountabilityRevocationIntent", "SupportCoverage", "AccountabilityBindingRefusal"],
     "ops": [O("accountability_binding", "validate_accountability_binding", ["DataProductEditionId", "AccountabilityDraft", "AuthorityEvidenceSet", "RolePolicy"], "ValidatedAccountabilityBinding"), O("accountability_binding", "plan_accountability_assignment", ["ValidatedAccountabilityBinding", "AuthorityServiceRef", "AssignmentPolicy"], "AccountabilityAssignmentIntent"), O("accountability_binding", "plan_accountability_revocation", ["AccountabilityBindingId", "RevocationEvidence", "RevocationPolicy"], "AccountabilityRevocationIntent"), O("accountability_binding", "derive_support_coverage", ["AccountabilityBindingSet", "SupportObjectiveSet", "CalendarCut"], "SupportCoverage")],
     "laws": ["Product owner, semantic owner, data owner, steward, custodian, publisher, operator and support owner are distinct roles.", "A product binds externally issued organizational identities, decision rights, delegations and revocations; it does not create persons, teams or ambient authority.", "Accountability, responsibility, authority, custody, execution and support duty are distinct relations.", "One product edition has one unambiguous accountable scope, while responsibilities and support duties may be plural and explicitly partitioned.", "Delegation is scope- and time-bound, does not transfer ultimate accountability, and revocation propagates to dependent assignments.", "Team proximity, repository ownership, authorship or on-call participation never implies publication or semantic authority."],
     "errors": ["AccountableOwnerMissing", "RoleIdentityUnresolved", "AuthorityEvidenceMissing", "ResponsibilityOverlap", "SegregationViolated", "DelegationOverbroad", "SupportGap", "AssignmentCompletionUnknown"], "deps": ["library.data_product_publication.product_edition"],
     "evidence": ["source.data-product-publication.w3c.prov-o", "source.data-product-publication.thoughtworks.designing-data-products", "source.data-product-publication.team-topologies.organization", "source.data-product-publication.lf.odps4.1"]},
    {"id": "library.data_product_publication.readiness_evidence", "seam": "readiness_evidence", "name": "Data Product Readiness Evidence", "kind": "algorithm_pure",
     "types": ["ReadinessCaseId", "ReadinessCriteriaEdition", "ReadinessRequirementId", "RequirementApplicability", "EvidenceCut", "EvidenceItemRef", "EvidenceFreshness", "EvidenceAuthorityRef", "RequirementSatisfaction", "UnsatisfiedRequirement", "ResidualRisk", "ExceptionRequestRef", "ExceptionDecisionRef", "AssessorRef", "AssessorIndependence", "ExternalCertificateRef", "ReadinessVerdict", "VerdictScope", "VerdictExpiry", "ReadinessTrace", "ReadinessEvidenceRefusal"],
     "ops": [O("readiness_evidence", "validate_readiness_criteria", ["ReadinessCriteriaEdition", "CriteriaAuthorityRef", "ApplicabilityContext"], "ValidatedReadinessCriteria"), O("readiness_evidence", "assemble_readiness_evidence", ["DataProductEditionId", "ClosedPortAssembly", "AccountabilityBinding", "EvidenceItemSet", "EvidenceCut"], "ReadinessEvidenceSet"), O("readiness_evidence", "evaluate_readiness", ["ValidatedReadinessCriteria", "ReadinessEvidenceSet", "EvaluationPolicy"], "ReadinessVerdict"), O("readiness_evidence", "explain_readiness", ["ReadinessVerdict", "ReadinessTrace", "DisclosurePolicy"], "ReadinessExplanation")],
     "laws": ["Readiness criteria, supplied evidence, satisfaction result, readiness verdict, publication approval and external certificate are distinct.", "The product evaluates declared criteria but cannot manufacture independent appraisal or certify itself.", "Every verdict binds exact product, port assembly, accountability, criteria, evidence and clock cuts plus residuals and expiry.", "Unknown, inapplicable, unsatisfied, conditionally satisfied, satisfied, waived and expired remain distinct; waiver requires an external scoped authority decision.", "Quality measurement, SLO attainment, FAIR indicator, security test and contract conformance are separate evidence dimensions and none alone proves readiness.", "A readiness pass is not publication, listing, access, delivery, consumer acceptance or fitness for every purpose."],
     "errors": ["CriteriaAuthorityMissing", "CriteriaIncomplete", "ApplicabilityUnknown", "EvidenceCutOpen", "EvidenceStale", "EvidenceAuthorityUnbound", "IndependenceUnproved", "ResidualUnaccepted", "ReadinessUndetermined"], "deps": ["library.data_product_publication.port_assembly", "library.data_product_publication.accountability_binding"],
     "evidence": ["source.data-product-publication.w3c.dqv", "source.data-product-publication.rda.fair-maturity1", "source.data-product-publication.google.sre-slo", "source.data-product-publication.w3c.prov-o"]},
    {"id": "library.data_product_publication.publication_protocol", "seam": "publication_protocol", "name": "Data Product Publication Protocol", "kind": "effect_port",
     "types": ["PublicationId", "PublicationEdition", "PublicationAuthorityRef", "PublicationApprovalRef", "PublicationTargetRef", "VisibilityScope", "EffectiveInstant", "PublicationCut", "PublicationManifest", "PublicationDigest", "PublicationIntent", "PublicationAttemptId", "PublicationReceipt", "VisibilityChangeIntent", "VisibilityChangeReceipt", "UnpublishIntent", "UnpublishReceipt", "PublicationState", "PublicationProtocolRefusal"],
     "ops": [O("publication_protocol", "plan_publication", ["DataProductEdition", "ClosedPortAssembly", "ReadinessVerdict", "PublicationApprovalRef", "PublicationPolicy"], "PublicationIntent"), O("publication_protocol", "reconcile_publication_receipt", ["PublicationIntent", "PublicationReceipt"], "PublicationState"), O("publication_protocol", "plan_visibility_change", ["PublicationEdition", "VisibilityScope", "VisibilityAuthorityRef", "VisibilityPolicy"], "VisibilityChangeIntent"), O("publication_protocol", "plan_unpublication", ["PublicationEdition", "UnpublicationEvidence", "UnpublicationPolicy"], "UnpublishIntent")],
     "laws": ["Readiness, approval, publication intent, publication attempt, publication receipt, catalog projection, marketplace listing and consumption are distinct.", "Publication binds an exact immutable product edition, port assembly, readiness verdict, approval, visibility scope, target and effective time.", "A successful target receipt proves registration or visibility effect only under that target contract; it does not prove discovery, access, delivery or consumer acceptance.", "Unknown publication completion is reconciled before retry and every intent has an explicit idempotency and target identity.", "Visibility change, unpublication, deprecation, recall and decommission are distinct and preserve historical receipts.", "Publication never mutates referenced contracts, schemas, datasets, distributions, policies or assurance evidence."],
     "errors": ["ProductEditionNotReady", "ApprovalMissing", "PublicationAuthorityMissing", "VisibilityScopeInvalid", "TargetUnsupported", "EffectiveTimeInvalid", "PublicationCompletionUnknown", "ReceiptMismatch"], "deps": ["library.data_product_publication.readiness_evidence"],
     "evidence": ["source.data-product-publication.w3c.dcat3", "source.data-product-publication.w3c.dwbp", "source.data-product-publication.lf.odps4.1", "source.data-product-publication.ietf.rfc9110"]},
    {"id": "library.data_product_publication.consumer_change", "seam": "consumer_change", "name": "Data Product Consumer Change Protocol", "kind": "effect_port",
     "types": ["ProductChangeId", "ChangeSet", "SemanticDiffRef", "CompatibilityResultRef", "ChangeClass", "AffectedEditionRef", "SubscriberPopulation", "SubscriberCut", "ConsumerDependencyRef", "ImpactStatement", "MigrationPathRef", "InFlightDisposition", "NoticeWindow", "ChangeNotice", "ChangeNoticeIntent", "NoticeDeliveryReceipt", "ConsumerAcknowledgementRef", "MigrationWindow", "ChangeClosureResult", "ConsumerChangeRefusal"],
     "ops": [O("consumer_change", "classify_product_change", ["ProductEditionDiff", "SemanticDiffSet", "CompatibilityEvidenceSet", "ChangePolicy"], "ClassifiedProductChange"), O("consumer_change", "plan_change_notice", ["ClassifiedProductChange", "SubscriberPopulation", "ImpactStatement", "NoticePolicy"], "ChangeNoticePlan"), O("consumer_change", "reconcile_notice_delivery", ["ChangeNoticePlan", "NoticeDeliveryReceiptSet", "DeliveryPolicy"], "NoticeDeliveryStatus"), O("consumer_change", "evaluate_migration_window", ["ClassifiedProductChange", "SubscriberCut", "ConsumerAcknowledgementSet", "MigrationEvidenceSet", "MigrationPolicy"], "ChangeClosureResult")],
     "laws": ["Change occurrence, semantic diff, compatibility result, impact statement, notice intent, transport delivery and consumer acknowledgement are distinct.", "Subscriber population, subscriber cut, affected dependency and notice scope are explicit; catalog views or access logs never silently become a complete consumer census.", "Breaking, additive, corrective, operational, policy, security, deprecation and recall changes remain typed and may require different reactions.", "A delivered notification does not prove receipt by every consumer, understanding, migration, acceptance or safe in-flight disposition.", "Notice window starts and closes under an explicit clock and policy; elapsed time alone never proves migration completion.", "Event envelopes and HTTP headers carry notices but do not define product-change semantics or delivery guarantees."],
     "errors": ["ChangeClassUnknown", "SemanticDiffMissing", "CompatibilityUnknown", "SubscriberPopulationUnknown", "ImpactUnproved", "NoticeWindowInvalid", "DeliveryPartial", "MigrationIncomplete", "InFlightDispositionOpen"], "deps": ["library.data_product_publication.publication_protocol"],
     "evidence": ["source.data-product-publication.cncf.cloudevents1", "source.data-product-publication.w3c.websub", "source.data-product-publication.ietf.rfc9745", "source.data-product-publication.ietf.rfc8594"]},
    {"id": "library.data_product_publication.recall_exit", "seam": "recall_exit", "name": "Data Product Recall, Exit and Decommission", "kind": "effect_port",
     "types": ["RecallCaseId", "RecallAuthorityRef", "RecallReason", "RecallScope", "AffectedProductEditionSet", "DependencyBlastRadius", "RecallNotice", "RecallPropagationIntent", "RecallPropagationReceipt", "ConsumerRemedyRef", "ExitProfile", "ExitManifest", "ExitArtifactRef", "ExitPackage", "ExitPackageDigest", "ExitValidationResult", "DecommissionCriteria", "DecommissionIntent", "DecommissionReceipt", "ResidualDependencySet", "RecallExitRefusal"],
     "ops": [O("recall_exit", "open_recall_case", ["AffectedProductEditionSet", "RecallEvidence", "RecallAuthorityRef", "RecallPolicy"], "RecallCase"), O("recall_exit", "plan_recall_propagation", ["RecallCase", "DependencyBlastRadius", "SubscriberPopulation", "PropagationPolicy"], "RecallPropagationPlan"), O("recall_exit", "assemble_exit_package", ["DataProductEdition", "ExitArtifactSet", "ExitProfile", "PackagingPolicy"], "ExitPackage"), O("recall_exit", "evaluate_decommission", ["RecallCase", "RecallPropagationStatus", "ExitValidationResult", "ResidualDependencySet", "DecommissionCriteria"], "DecommissionDecision")],
     "laws": ["Deprecation, sunset, recall, access revocation, unpublication, retirement, decommission, physical deletion and completed exit are distinct.", "Recall preserves the affected edition, reason, authority, scope, evidence, dependents, notices, remedies and propagation receipts.", "The product emits propagation, unpublication, access-revocation, compensation and decommission intents to owning runtimes; it never self-attests those effects.", "An exit package contains exact semantic, contract, schema, metadata, policy, provenance, evidence, configuration and dependency references required by its selected profile.", "Package completeness, byte integrity, semantic completeness, migration executability, provider independence and business substitutability are separate verdicts.", "Decommission is refused while live dependencies, consumer obligations, in-flight work, retention/hold duties, unresolved recalls or unverified exit artifacts remain."],
     "errors": ["RecallAuthorityMissing", "RecallScopeAmbiguous", "BlastRadiusUnknown", "PropagationIncomplete", "ExitProfileUnbound", "ExitPackageIncomplete", "ExitIntegrityFailed", "ResidualDependencyPresent", "ConsumerObligationOpen", "DecommissionUnsafe"], "deps": ["library.data_product_publication.consumer_change", "library.data_product_publication.port_assembly"],
     "evidence": ["source.data-product-publication.ietf.rfc9745", "source.data-product-publication.ietf.rfc8594", "source.data-product-publication.ietf.rfc8493", "source.data-product-publication.ro-crate.1.1", "source.data-product-publication.oci.descriptor1.1"]},
]


def materialize(s: dict) -> dict:
    seam = s["seam"]
    return {"library_id": s["id"], "name": s["name"], "library_kind": s["kind"],
            "semantic_owner_context": f"context.data_product_publication.{CONTEXT_BY_SEAM[seam]}", "status": "specified",
            "candidate_responsibility": s["name"].lower(), "effect_boundary": "pure_effect_intents" if s["kind"] == "effect_port" else "pure_no_io",
            "public_types": s["types"], "public_traits": [s["name"].replace(" ", "") + "Algebra"],
            "operation_refs": [o["operation_ref"] for o in s["ops"]], "operations": s["ops"],
            "decision_refs": [f"decision.data_product_publication.{seam}.{d}" for d in DECISIONS[seam]],
            "configuration_contracts": [s["name"].replace(" ", "") + "Policy"], "laws": s["laws"],
            "invariants": ["every identity, edition, cut, authority, compatibility relation, time, dependency, intent and receipt is explicit",
                           "unknown, absent, inapplicable, unready, unapproved, unpublished, hidden, deprecated, recalled, retired and decommissioned remain distinct",
                           "no model or agent may issue identity, establish accountability, waive criteria, approve, publish, recall, accept evidence, certify or decommission"],
            "error_contracts": s["errors"] + ["UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
            "dependencies": s["deps"], "evidence_refs": s["evidence"],
            "oracles": ["canonical positive fixtures", "negative twins", "property and metamorphic laws", "lifecycle model tests", "semantic-diff and dependency corpus", "package integrity and exit corpus", "two independent differential implementations"],
            "gaps": ["No implementation is qualified; two independent implementations and executed conformance remain required."],
            "must_not_own": ["source facts, datasets, schemas, contracts or distributions", "organizational identity or ambient authority", "independent assurance or universal fitness", "catalog ranking or marketplace offer", "access approval, provisioning or consumption", "physical data mutation or deletion", "provider qualification"],
            "qualification_required": False}


LIBRARIES = [materialize(s) for s in SPECS]


NEGATIVES = [
    ("product_dataset", "A data product is its dataset, table, API or distribution.", "Keep product promise, editions, ports and externally owned resources distinct."),
    ("name_identity", "Matching product names establish identity or equivalence.", "Require scoped identity authority and explicit mappings."),
    ("version_order", "A larger version string proves replacement, compatibility or currentness.", "Use explicit directional edition relations and compatibility evidence."),
    ("registry_product", "A catalog or registry record is the product edition.", "Treat registration as a separate effect occurrence describing the product."),
    ("port_endpoint", "A port is just a URL, table location, topic or credential.", "Bind semantic role, exact contracts and provider locations separately."),
    ("closed_ready", "A structurally closed port graph proves readiness.", "Evaluate exact multidimensional readiness criteria and evidence."),
    ("owner_author", "Repository author, team proximity or on-call role implies product authority.", "Require externally issued scoped authority and accountability bindings."),
    ("self_certificate", "A product's readiness verdict is independent certification.", "Keep self-assessment, external appraisal and certificate identities separate."),
    ("quality_ready", "One quality, FAIR or SLO score proves product readiness.", "Retain independent evidence dimensions and applicable criteria."),
    ("ready_publish", "Readiness automatically publishes a product.", "Require separate scoped approval and publication effect receipt."),
    ("publish_listing", "Publication creates a marketplace listing or endorsement.", "Marketplace offer and ranking remain independently owned."),
    ("publish_access", "Publication grants access or provisions data.", "Require policy, entitlement and fulfillment decisions from their owners."),
    ("receipt_discovery", "Publication receipt proves consumers can discover or consume the product.", "Limit the claim to the exact target registration effect."),
    ("notice_received", "A delivered notice proves every consumer understood and migrated.", "Track population, delivery, acknowledgement and migration separately."),
    ("logs_census", "Usage logs are a complete subscriber/dependency census.", "Require explicit population definition, cuts and coverage evidence."),
    ("deprecated_dead", "Deprecation means behavior changed, access ended or the product was deleted.", "Keep deprecation, sunset, recall, revocation and deletion distinct."),
    ("recall_deleted", "Recall deletes the product and all downstream copies.", "Preserve history and issue explicit effects to owning contexts with receipts."),
    ("valid_package_portable", "A complete checksum-valid exit package proves semantic portability.", "Evaluate integrity, semantics, migration, provider independence and substitutability separately."),
    ("time_decommission", "An elapsed sunset or notice window proves safe decommission.", "Require closed dependencies, obligations, in-flight work, recalls and exit evidence."),
    ("agent_authority", "A model or agent may establish identity, waive readiness, approve publication, recall or decommission.", "Allow attributed proposals only; named authorities and deterministic laws retain every consequential decision."),
]


NEGATIVE_ROWS = [{"negative_id": f"negative.data-product-publication.{s}", "unsafe_inference": u, "required_behavior": b, "status": "active"} for s, u, b in NEGATIVES]


COMPILER_ROWS = []
for lib in LIBRARIES:
    stem = lib["library_id"].removeprefix("library.")
    COMPILER_ROWS += [
        {"record_kind": "capability_requirement", "requirement_id": f"requirement.{stem}.implementation", "subject_ref": lib["library_id"], "required_operations": lib["operation_refs"], "required_decisions": lib["decision_refs"], "fallback_law": "refuse", "status": "declared"},
        {"record_kind": "capability_offer", "offer_id": f"offer.{stem}.reference", "subject_ref": lib["library_id"], "claimed_operations": lib["operation_refs"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
        {"record_kind": "binding_rule", "binding_rule_id": f"binding.{stem}", "requirement_ref": f"requirement.{stem}.implementation", "offer_ref": f"offer.{stem}.reference", "structural_match": True, "selection_law": "Structural match never promotes an unqualified or non-portable implementation.", "selectable": False, "status": "declared"},
    ]


FILES = {"sources.jsonl": SOURCES, "bounded-contexts.jsonl": CONTEXTS, "decision-points.jsonl": DECISION_ROWS,
         "library-contracts.jsonl": LIBRARIES, "compiler-contracts.jsonl": COMPILER_ROWS, "negative-twins.jsonl": NEGATIVE_ROWS}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = lines(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {"manifest_id": "data_product_publication_governance_v0_1_0", "as_of": AS_OF, "edition": EDITION,
                "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False,
                "qualified_implementation_count": 0}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS data product publication: {len(SOURCES)} sources, {len(CONTEXTS)} contexts, {len(DECISION_ROWS)} decisions, {len(LIBRARIES)} exact libraries, {len(COMPILER_ROWS)} compiler contracts")


if __name__ == "__main__":
    main()
