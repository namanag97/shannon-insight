#!/usr/bin/env python3
"""Retain Dataset Curation Workbench without absorbing preparation, annotation, quality or ML."""

from __future__ import annotations

from typing import Any


PRODUCT = "product.dataset_curation_workbench"
PREFIX = "dataset_curation"
EVIDENCE = [
    "evidence.dataset_curation.datasheets",
    "evidence.dataset_curation.data_cards",
    "evidence.dataset_curation.croissant",
    "evidence.dataset_curation.dcat3",
    "evidence.dataset_curation.odrl",
    "evidence.dataset_curation.datacite",
    "evidence.dataset_curation.fiftyone_views",
    "evidence.dataset_curation.fiftyone_versioning",
    "evidence.dataset_curation.fiftyone_export",
    "evidence.dataset_curation.huggingface_repository",
    "evidence.dataset_curation.huggingface_cards",
    "evidence.dataset_curation.cleanlab_issues",
    "evidence.dataset_curation.deduplication_paper",
]

SOURCES = [
    {
        "source_id": "evidence.dataset_curation.datasheets", "source_class": "primary_research",
        "title": "Datasheets for Datasets", "publisher": "Gebru et al.", "retrieved_at": "2026-08-27",
        "uri": "https://www.microsoft.com/en-us/research/uploads/prod/2019/01/1803.09010.pdf",
        "claim": "Dataset documentation spans motivation, composition, collection, preprocessing, distribution, maintenance, and legal and ethical considerations.",
        "scope_limit": "A documentation proposal does not define storage, legal authority, executable curation semantics or provider qualification.",
    },
    {
        "source_id": "evidence.dataset_curation.data_cards", "source_class": "primary_research",
        "title": "Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI", "publisher": "Google Research / ACM", "retrieved_at": "2026-08-27",
        "uri": "https://research.google/pubs/data-cards-purposeful-and-transparent-dataset-documentation-for-responsible-ai/",
        "claim": "Data cards preserve origins, development, intent, uses, evolution, limitations and stakeholder-facing rationales across a dataset lifecycle.",
        "scope_limit": "The framework is evidence for documentation and maintenance, not a universal curation algorithm or business authority.",
    },
    {
        "source_id": "evidence.dataset_curation.croissant", "source_class": "open_standard",
        "title": "Croissant Format Specification 1.1", "publisher": "MLCommons", "retrieved_at": "2026-08-27",
        "uri": "https://docs.mlcommons.org/croissant/docs/croissant-spec-1.1.html",
        "claim": "Defines machine-readable dataset, record-set, file, field, provenance, use-policy and distribution metadata with stable references and checksums.",
        "scope_limit": "Metadata interchange does not decide membership, quality, split suitability, rights authority or release readiness.",
    },
    {
        "source_id": "evidence.dataset_curation.dcat3", "source_class": "w3c_recommendation",
        "title": "Data Catalog Vocabulary Version 3", "publisher": "W3C", "retrieved_at": "2026-08-27",
        "uri": "https://www.w3.org/TR/vocab-dcat-3/",
        "claim": "Separates dataset, distribution, data service, catalog record and dataset series, and specifies version, checksum, rights and lifecycle relations.",
        "scope_limit": "DCAT describes publication metadata; it does not prescribe internal curation, storage or acceptance decisions.",
    },
    {
        "source_id": "evidence.dataset_curation.odrl", "source_class": "w3c_recommendation",
        "title": "ODRL Information Model 2.2", "publisher": "W3C", "retrieved_at": "2026-08-27",
        "uri": "https://www.w3.org/TR/odrl-model/",
        "claim": "Distinguishes assets, parties, permissions, prohibitions, duties, constraints, policy profiles and conflict strategies for machine-readable use conditions.",
        "scope_limit": "A policy expression is not proof of legal validity, consent, entitlement, enforcement or fulfilled duty.",
    },
    {
        "source_id": "evidence.dataset_curation.datacite", "source_class": "community_standard",
        "title": "DataCite Metadata Schema 4.7", "publisher": "DataCite", "retrieved_at": "2026-08-27",
        "uri": "https://schema.datacite.org/",
        "claim": "Defines core identity, creators, publisher, dates, versions, resource types and typed related identifiers for citation and retrieval.",
        "scope_limit": "Citation metadata neither proves dataset contents nor replaces an immutable membership manifest.",
    },
    {
        "source_id": "evidence.dataset_curation.fiftyone_views", "source_class": "official_product_documentation",
        "title": "Dataset Views", "publisher": "Voxel51", "retrieved_at": "2026-08-27",
        "uri": "https://docs.voxel51.com/user_guide/using_views.html",
        "claim": "Documents composable dynamic filtering, slicing, matching, sorting, selection and saved views over heterogeneous dataset samples.",
        "scope_limit": "One provider's view API is not the portable membership algebra and a view is not a released dataset edition.",
    },
    {
        "source_id": "evidence.dataset_curation.fiftyone_versioning", "source_class": "official_product_documentation",
        "title": "Dataset Versioning", "publisher": "Voxel51", "retrieved_at": "2026-08-27",
        "uri": "https://docs.voxel51.com/enterprise/dataset_versioning.html",
        "claim": "Documents immutable read-only dataset snapshots, mutable HEAD, captured and excluded state, archival and restoration semantics.",
        "scope_limit": "Snapshot mechanics do not prove curation quality, external media immutability, rights or publication readiness.",
    },
    {
        "source_id": "evidence.dataset_curation.fiftyone_export", "source_class": "official_product_documentation",
        "title": "Exporting FiftyOne Datasets", "publisher": "Voxel51", "retrieved_at": "2026-08-27",
        "uri": "https://docs.voxel51.com/user_guide/export_datasets.html",
        "claim": "Documents export of whole datasets or selected views, media/labels independently, into multiple formats.",
        "scope_limit": "Serialization/export is a delivery mechanism, not proof of semantic equivalence or release authorization.",
    },
    {
        "source_id": "evidence.dataset_curation.huggingface_repository", "source_class": "official_product_documentation",
        "title": "Uploading datasets", "publisher": "Hugging Face", "retrieved_at": "2026-08-27",
        "uri": "https://huggingface.co/docs/hub/datasets-adding",
        "claim": "Dataset repositories carry files, revision history, public/private access, structured formats, viewers and documentation.",
        "scope_limit": "Repository packaging does not establish dataset fitness, rights, contamination freedom or independent product conformance.",
    },
    {
        "source_id": "evidence.dataset_curation.huggingface_cards", "source_class": "official_product_documentation",
        "title": "Dataset Cards", "publisher": "Hugging Face", "retrieved_at": "2026-08-27",
        "uri": "https://huggingface.co/docs/hub/main/datasets-cards",
        "claim": "Documents dataset content, context, responsible use, bias, license, language, modality, size, source and task metadata.",
        "scope_limit": "A card can be incomplete or inaccurate and is not a conformance or acceptance receipt.",
    },
    {
        "source_id": "evidence.dataset_curation.cleanlab_issues", "source_class": "official_technical_documentation",
        "title": "Datalab Issue Types", "publisher": "Cleanlab", "retrieved_at": "2026-08-27",
        "uri": "https://docs.cleanlab.ai/stable/cleanlab/datalab/guide/issue_type_description.html",
        "claim": "Separates dataset-level issues such as non-IID behavior and imbalance from occurrence-level issues such as labels, outliers, nulls and near duplicates, with explicit method inputs and limitations.",
        "scope_limit": "Scores are method results and candidate evidence; they do not themselves authorize removal, balancing or release.",
    },
    {
        "source_id": "evidence.dataset_curation.deduplication_paper", "source_class": "primary_research",
        "title": "Deduplicating Training Data Makes Language Models Better", "publisher": "Google Research", "retrieved_at": "2026-08-27",
        "uri": "https://research.google/pubs/deduplicating-training-data-makes-language-models-better/",
        "claim": "Shows that exact and near duplication and train-test overlap are separate measurable dataset risks with distribution and memorization consequences.",
        "scope_limit": "Text-corpus results do not universalize thresholds, similarity representations, removal policy or effects across modalities and uses.",
    },
]

LIBRARIES: dict[str, dict[str, Any]] = {
    "dataset_definition_purpose": {
        "types": ["DatasetDefinitionId", "DatasetPurpose", "IntendedUse", "ProhibitedUse", "PopulationDefinition", "UnitOfObservation", "TargetCoverage", "DefinitionEdition"],
        "operations": ["open_definition", "bind_purpose_and_population", "declare_uses", "publish_definition_edition"],
        "decisions": ["dataset identity", "purpose", "population", "unit of observation", "coverage target", "intended and prohibited uses"],
        "invariants": ["dataset purpose population and occurrence membership are distinct", "purpose and population are explicit and editioned", "a task label never becomes universal fitness"],
        "refusals": ["purpose_missing", "population_ambiguous", "observation_unit_unbound", "uses_conflict", "definition_edition_conflict"],
        "dependencies": [],
    },
    "source_occurrence_admission_membership": {
        "types": ["SourceOccurrenceRef", "SourceEditionRef", "AdmissionEvidence", "MembershipCandidate", "MembershipDecision", "ExclusionReason", "MembershipCut"],
        "operations": ["admit_source_occurrence", "propose_membership", "accept_or_reject_membership", "seal_membership_cut"],
        "decisions": ["source identity", "admissibility", "membership", "exclusion reason", "membership cut completeness"],
        "invariants": ["source occurrence is not dataset member until admitted", "membership decisions preserve source identity and rationale", "curation never mutates source truth"],
        "refusals": ["source_identity_unresolved", "source_edition_missing", "admission_evidence_missing", "membership_rule_unbound", "membership_conflict"],
        "dependencies": ["dataset_definition_purpose"],
    },
    "inclusion_exclusion_selection": {
        "types": ["SelectionPlan", "InclusionPredicate", "ExclusionPredicate", "SamplingFrame", "SelectionOccurrence", "SelectionResidual", "SelectionReceipt"],
        "operations": ["compile_selection_plan", "evaluate_selection", "explain_inclusion_or_exclusion", "record_residuals"],
        "decisions": ["predicate semantics", "sampling frame", "unknown handling", "precedence", "residual policy"],
        "invariants": ["selection view is not membership decision or dataset edition", "unknown and non-applicable remain distinct from false", "every exclusion has an attributable rule or judgment"],
        "refusals": ["predicate_invalid", "sampling_frame_unbound", "unknown_policy_missing", "selection_partial", "residual_unbounded"],
        "dependencies": ["source_occurrence_admission_membership"],
    },
    "curation_recipe_derivation": {
        "types": ["CurationRecipe", "RecipeStep", "DerivationRef", "InputCut", "OutputCut", "LossDeclaration", "ReplayReceipt"],
        "operations": ["define_curation_recipe", "bind_derivation", "typecheck_recipe", "replay_recipe", "compare_cuts"],
        "decisions": ["step order", "transform admission", "loss posture", "partial-result validity", "replay compatibility"],
        "invariants": ["recipe is not production pipeline or source mutation", "every derived occurrence binds exact inputs steps and outputs", "loss and partiality are explicit"],
        "refusals": ["recipe_type_error", "input_cut_incompatible", "derivation_untraceable", "loss_undeclared", "replay_non_determinism_unbounded"],
        "dependencies": ["inclusion_exclusion_selection"],
    },
    "duplicate_evidence_adjudication": {
        "types": ["DuplicateCandidate", "DuplicateKind", "SimilarityRepresentation", "ThresholdProfile", "DuplicateComponent", "DuplicateDecision", "RepresentativePolicy"],
        "operations": ["admit_duplicate_evidence", "classify_duplicate_relation", "adjudicate_component", "select_representative", "record_retained_duplicates"],
        "decisions": ["exact versus near", "representation and metric", "threshold", "equivalence scope", "representative and retention policy"],
        "invariants": ["similarity score is not duplicate identity or removal authority", "duplicate meaning is modality purpose and representation scoped", "retained and removed occurrences remain traceable"],
        "refusals": ["representation_unqualified", "threshold_unbound", "candidate_evidence_stale", "component_conflict", "representative_policy_missing"],
        "dependencies": ["curation_recipe_derivation"],
    },
    "cohort_balance_coverage_assessment": {
        "types": ["CohortDefinition", "StratumDefinition", "CoverageTarget", "DistributionMeasure", "BalanceAssessment", "CoverageGap", "SamplingWeightProposal"],
        "operations": ["define_cohorts", "measure_distribution", "assess_balance_and_coverage", "publish_gaps", "propose_sampling_adjustment"],
        "decisions": ["cohort semantics", "reference population", "measure", "coverage threshold", "adjustment proposal"],
        "invariants": ["imbalance is not defect and numerical balance is not representativeness", "cohort vocabulary comes from a vertical or purpose profile", "adjustment proposals never silently rewrite membership"],
        "refusals": ["cohort_definition_missing", "reference_population_unknown", "measure_inapplicable", "coverage_threshold_unbound", "small_cell_or_uncertainty_unreported"],
        "dependencies": ["source_occurrence_admission_membership"],
    },
    "partition_split_assignment": {
        "types": ["PartitionPlan", "SplitRole", "AssignmentUnit", "GroupingKey", "TemporalCut", "StratificationRule", "RandomnessReceipt", "SplitAssignment"],
        "operations": ["define_partition_plan", "bind_group_and_time_boundaries", "assign_occurrences", "freeze_split", "reproduce_assignment"],
        "decisions": ["split roles", "assignment unit", "group isolation", "temporal boundary", "stratification", "randomness and seed"],
        "invariants": ["dataset membership and split assignment are distinct", "one indivisible assignment unit cannot cross prohibited splits", "randomness algorithm seed input order and edition are recorded"],
        "refusals": ["split_roles_undefined", "assignment_unit_ambiguous", "group_key_missing", "temporal_cut_invalid", "stratification_infeasible", "randomness_unreproducible"],
        "dependencies": ["cohort_balance_coverage_assessment"],
    },
    "leakage_contamination_audit": {
        "types": ["AuditScope", "ProtectedBoundary", "ContaminationCandidate", "LeakagePath", "OverlapEvidence", "AuditFinding", "Defeater", "AuditVerdict"],
        "operations": ["define_audit_scope", "detect_overlap_and_paths", "admit_or_defeat_finding", "evaluate_partition_isolation", "publish_audit_verdict"],
        "decisions": ["protected boundary", "identity and similarity scope", "temporal and group reachability", "finding strength", "acceptable residual risk"],
        "invariants": ["duplicate contamination target leakage and temporal leakage are distinct", "absence of detected overlap is not proof of absence", "audit verdict binds methods cuts limitations and defeaters"],
        "refusals": ["protected_boundary_missing", "identity_resolution_insufficient", "method_coverage_unknown", "finding_unadjudicated", "residual_risk_unaccepted"],
        "dependencies": ["duplicate_evidence_adjudication", "partition_split_assignment"],
    },
    "annotation_reference_binding": {
        "types": ["AnnotationEditionRef", "ReferenceEditionRef", "TargetSelector", "CoverageMap", "AcceptanceStatus", "RecallLink", "UnlabeledOccurrencePolicy"],
        "operations": ["bind_annotation_edition", "resolve_target_coverage", "admit_reference_edition", "propagate_recall", "record_unlabeled_policy"],
        "decisions": ["annotation role", "target coverage", "reference acceptance", "missing-label treatment", "recall impact"],
        "invariants": ["source occurrence annotation prediction and accepted reference are distinct", "curation imports rather than creates annotations", "annotation recall can invalidate but never silently rewrite a dataset edition"],
        "refusals": ["annotation_edition_unresolved", "selector_mismatch", "schema_incompatible", "acceptance_status_missing", "recall_impact_unknown"],
        "dependencies": ["source_occurrence_admission_membership"],
    },
    "rights_use_policy_manifest": {
        "types": ["AssetRef", "RightsholderRef", "LicenseExpression", "Permission", "Prohibition", "Duty", "ConsentEvidenceRef", "PurposeConstraint", "TerritoryConstraint", "PolicyConflict"],
        "operations": ["bind_rights_evidence", "compile_use_manifest", "evaluate_declared_use", "detect_policy_conflict", "propagate_revocation"],
        "decisions": ["applicable asset and party", "license expression", "permission prohibition and duty", "purpose and territory", "conflict posture", "revocation impact"],
        "invariants": ["policy expression is not legal truth consent or entitlement", "rights remain distribution and occurrence scoped", "unknown or conflicting use authority refuses release"],
        "refusals": ["rightsholder_unknown", "license_incompatible", "permission_absent", "prohibition_applies", "duty_unfulfilled", "consent_or_purpose_unresolved", "revocation_not_propagated"],
        "dependencies": ["source_occurrence_admission_membership"],
    },
    "dataset_profile_statistics": {
        "types": ["ProfilePlan", "StatisticDefinition", "MeasureResult", "Uncertainty", "MissingnessProfile", "ModalityProfile", "CoverageMatrix", "ProfileEdition"],
        "operations": ["define_profile", "admit_measure_result", "assemble_profile_edition", "compare_profiles", "publish_limitations"],
        "decisions": ["profile scope", "statistic applicability", "measure admission", "uncertainty", "suppression and disclosure", "comparison compatibility"],
        "invariants": ["profile statistic is not quality verdict fitness or population truth", "statistics bind exact membership and split cuts", "undefined suppressed uncertain and zero are distinct"],
        "refusals": ["profile_scope_missing", "statistic_inapplicable", "measure_result_unqualified", "uncertainty_missing", "small_cell_disclosure_denied", "profile_cuts_incomparable"],
        "dependencies": ["cohort_balance_coverage_assessment", "partition_split_assignment"],
    },
    "documentation_metadata_projection": {
        "types": ["DocumentationProfile", "Audience", "DatasetStatement", "EvidenceLink", "Limitation", "MetadataProjection", "ConformanceClaim", "DocumentationEdition"],
        "operations": ["select_documentation_profile", "assemble_statements", "validate_required_fields", "project_metadata_format", "publish_documentation_edition"],
        "decisions": ["audience and purpose", "profile applicability", "statement evidence", "omission handling", "projection loss", "conformance claim"],
        "invariants": ["documentation statement is not dataset fact unless evidence supports it", "datasheet data card Croissant DCAT and DataCite are projections not one identity", "unknown and not applicable are explicit"],
        "refusals": ["audience_unbound", "required_statement_missing", "evidence_link_unresolved", "profile_incompatible", "projection_loss_unaccepted", "conformance_unproven"],
        "dependencies": ["dataset_definition_purpose", "rights_use_policy_manifest", "dataset_profile_statistics"],
    },
    "immutable_dataset_edition_manifest": {
        "types": ["DatasetEditionId", "MembershipManifest", "OccurrenceDigest", "SchemaRef", "SplitManifest", "AnnotationBinding", "RightsManifest", "DocumentationRef", "DistributionManifest", "EditionDigest"],
        "operations": ["assemble_edition_manifest", "validate_references", "calculate_edition_digest", "seal_dataset_edition", "verify_dataset_edition"],
        "decisions": ["edition identity", "manifest completeness", "digest profile", "external-content posture", "schema and distribution binding", "seal readiness"],
        "invariants": ["dataset definition working set view snapshot edition distribution and release are distinct", "sealed edition is immutable and content addressed under an explicit digest profile", "external mutable content cannot masquerade as captured state"],
        "refusals": ["membership_manifest_incomplete", "reference_unresolved", "digest_profile_missing", "external_content_mutable", "schema_or_split_mismatch", "edition_digest_conflict"],
        "dependencies": ["leakage_contamination_audit", "annotation_reference_binding", "rights_use_policy_manifest", "documentation_metadata_projection"],
    },
    "release_maintenance_recall": {
        "types": ["DatasetRelease", "ReleaseAudience", "DistributionRef", "MaintenancePlan", "ChangeProposal", "ImpactAssessment", "SupersessionLink", "DeprecationNotice", "RecallNotice", "ConsumerReceipt"],
        "operations": ["request_release", "authorize_release", "publish_release", "record_delivery", "assess_change", "supersede_or_deprecate", "recall_release"],
        "decisions": ["release authority", "audience and distribution", "maintenance ownership", "change compatibility", "consumer impact", "deprecation and recall scope"],
        "invariants": ["sealed edition release publication delivery use and outcome are distinct", "maintenance creates successor editions rather than rewriting history", "recall preserves evidence and propagates to known consumers"],
        "refusals": ["release_authority_missing", "distribution_unqualified", "documentation_or_rights_incomplete", "delivery_unknown", "change_impact_unassessed", "recall_scope_unknown", "consumer_notification_unproven"],
        "dependencies": ["immutable_dataset_edition_manifest"],
    },
}


def owner(key: str) -> str:
    return f"semantic.dataset_curation.{key}"


def capability(key: str) -> str:
    return f"capability.dataset_curation.{key}"


def library(key: str) -> str:
    return f"library.analytics_dataset_curation.{key}"


def product_artifact() -> dict[str, Any]:
    states = ["definition_draft", "sources_pending", "membership_working", "curation_in_progress", "split_design", "audit_pending", "review_ready", "edition_sealed", "release_pending", "released", "maintenance_open", "superseded", "deprecated", "recalled"]
    commands = ["open_dataset_definition", "admit_source_occurrence", "decide_membership", "apply_curation_recipe", "adjudicate_duplicates", "assess_coverage", "assign_partitions", "audit_leakage_and_contamination", "bind_annotations_and_rights", "assemble_documentation", "seal_dataset_edition", "authorize_release", "publish_release", "assess_change", "supersede_dataset_edition", "recall_dataset_release"]
    events = ["dataset_definition_opened", "source_occurrence_admitted", "membership_decided", "curation_recipe_applied", "duplicates_adjudicated", "coverage_assessed", "partitions_assigned", "leakage_and_contamination_audited", "annotations_and_rights_bound", "documentation_assembled", "dataset_edition_sealed", "release_authorized", "dataset_release_published", "change_assessed", "dataset_edition_superseded", "dataset_release_recalled"]
    return {
        "artifact_id": PRODUCT, "kind": "product", "name": "Dataset Curation Workbench", "status": "candidate",
        "semantic_owner_ref": None, "adoption_unit": True, "operated": True,
        "definition": "How can a dataset steward turn admitted source occurrences into a purpose-bound, evidence-bearing, immutable and maintainable dataset edition without acquiring source, annotation, legal, model or downstream-use authority?",
        "sovereign_question": "How can a dataset steward turn admitted source occurrences into a purpose-bound, evidence-bearing, immutable and maintainable dataset edition without acquiring source, annotation, legal, model or downstream-use authority?",
        "users": ["dataset_steward", "data_scientist", "research_data_manager", "benchmark_owner", "assurance_reviewer"],
        "harmed_parties": ["data_subject", "source_owner", "rightsholder", "underrepresented_population", "dataset_consumer", "downstream_decision_subject"],
        "jobs": ["Define, source, select, derive, deduplicate, balance, partition, audit, document, seal, release and maintain a reproducible dataset edition."],
        "outcomes": ["purpose_bound_membership", "reproducible_curation_decisions", "leakage_evidenced_splits", "machine_readable_documentation", "immutable_dataset_edition", "recallable_release"],
        "lifecycle_states": states, "commands": commands, "events": events,
        "invariants": ["source occurrence dataset member annotation and model example are distinct", "working view snapshot sealed edition distribution and release are distinct", "curation decisions bind exact evidence rules methods judgments and cuts", "sealed editions are immutable", "rights documentation and audit uncertainty fail closed", "release never proves downstream fitness use or outcome"],
        "refusals": ["purpose_or_population_unbound", "source_identity_unresolved", "membership_evidence_missing", "curation_recipe_invalid", "split_or_group_boundary_invalid", "leakage_audit_incomplete", "rights_or_consent_unresolved", "documentation_incomplete", "edition_manifest_inconsistent", "release_authority_missing", "recall_propagation_unknown"],
        "negative_mission": "Does not own source truth or storage, production transformation, annotation creation, generic quality methods, legal or consent authority, catalog subscriptions, model training/evaluation, or downstream use and effects.",
        "automation_modality": {
            "default": "DETERMINISTIC_CORE_ONLY", "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
            "law": "Statistical, learned, generative or agentic systems may propose membership, similarity, labels, profiles, documentation or risks only through typed evidence-bearing ports.",
            "hard_work_law": "Automation never replaces vocabulary, boundary adjudication, invariants, state machines, evidence, law oracles, qualification or domain acceptance.",
            "removal_law": "Removing optional models and agents preserves purpose, membership, split, audit, rights, documentation, edition and release semantics.",
        },
        "evidence_refs": EVIDENCE,
    }


def dossier(product: dict[str, Any]) -> dict[str, Any]:
    roots = ["DatasetDefinition", "MembershipPlan", "CurationCase", "PartitionPlan", "DatasetAudit", "DatasetEdition", "DatasetRelease"]
    context_map = [
        {"neighbor_ref": "neighbor.source_truth", "relationship": "customer_supplier_acl", "translation": "admit immutable source occurrences and correction/validity evidence"},
        {"neighbor_ref": "product.self_service_data_preparation", "relationship": "published_language", "translation": "import reviewable derivation recipes without transferring dataset membership authority"},
        {"neighbor_ref": "product.annotation_operations", "relationship": "customer_supplier_acl", "translation": "bind accepted annotation/reference editions and recall events"},
        {"neighbor_ref": "neighbor.quality", "relationship": "open_host_service", "translation": "import typed measurements and issue evidence without transferring curation decisions"},
        {"neighbor_ref": "neighbor.policy_privacy", "relationship": "customer_supplier_acl", "translation": "import rights consent purpose privacy and disclosure authority"},
        {"neighbor_ref": "neighbor.versioned_storage", "relationship": "supplier", "translation": "store and retrieve immutable objects without making storage commit equal dataset edition"},
        {"neighbor_ref": "neighbor.data_product_publication", "relationship": "published_language", "translation": "publish a sealed dataset as a distributable data product without absorbing contract subscription or SLO ownership"},
        {"neighbor_ref": "neighbor.model_lifecycle", "relationship": "published_language", "translation": "supply exact dataset editions while model lifecycle owns training evaluation and model release"},
    ]
    ddd = {
        "domain_vision_statement": "Own the accountable lifecycle from purpose and admitted source occurrences to immutable, documented, auditable and recallable dataset editions.",
        "subdomain_classification": "core_for_dataset_curation_supporting_to_analytical_scientific_and_model_products",
        "bounded_context_boundary": {"inside": ["purpose and population", "source admission and membership", "curation recipe decisions", "duplicate adjudication", "cohort coverage and balance", "partition design", "leakage and contamination audit", "annotation and rights binding", "dataset profiles and documentation", "edition sealing", "release maintenance supersession and recall"], "outside": ["source mutation and storage truth", "generic preparation and production transforms", "annotation creation", "statistical method ownership", "legal and consent authority", "generic catalog and data-product subscription", "model training evaluation and deployment", "downstream decision and effect"]},
        "ubiquitous_language_policy": "Dataset definition, source occurrence, member, working cut, view, split, audit finding, sealed edition, distribution and release each have one non-interchangeable meaning.",
        "context_map": context_map,
        "anti_corruption_layers": [f"acl.dataset_curation.{row['neighbor_ref'].split('.')[-1]}" for row in context_map],
        "published_language": ["DatasetDefinitionEdition", "MembershipDecision", "CurationRecipeReceipt", "SplitManifest", "DatasetAuditVerdict", "DatasetEditionManifest", "DatasetRelease", "DatasetRecallNotice", "typed refusals"],
        "value_objects": ["DatasetDefinitionId", "DatasetEditionId", "DatasetPurpose", "PopulationDefinition", "SourceOccurrenceRef", "MembershipDecision", "SelectionPredicate", "CurationRecipe", "DuplicateDecision", "CohortDefinition", "PartitionAssignment", "LeakageFinding", "RightsManifest", "DocumentationEdition", "EditionDigest", "ReleaseRef"],
        "entities": ["DatasetDefinition", "MembershipPlan", "MembershipOccurrence", "CurationCase", "DuplicateCase", "PartitionPlan", "DatasetAudit", "DatasetEdition", "DatasetRelease", "RecallOccurrence"],
        "aggregates": [{"root": root, "members": [f"{root}Id", "edition", "state", "evidence_refs"], "consistency": f"{root} changes only through versioned commands with exact evidence and authority."} for root in roots],
        "aggregate_roots": roots,
        "aggregate_invariants": product["invariants"] + ["every accepted membership change is attributable and reproducible", "every split binds group time randomness and stratification semantics", "every release binds one sealed edition and exact disclosure/use scope"],
        "commands": product["commands"], "domain_events": product["events"],
        "refusal_failure_catalog": product["refusals"] + ["method_capability_unavailable", "resource_budget_exhausted", "cancelled", "provider_terminal_state_unknown", "consumer_notification_unproven"],
        "domain_services": ["DatasetDefinitionService", "MembershipDecisionService", "CurationRecipeService", "DuplicateAdjudicationService", "CoverageAssessmentService", "PartitionDesignService", "LeakageAuditService", "RightsAndDocumentationBindingService", "DatasetEditionService", "DatasetReleaseService"],
        "application_services": ["OpenDatasetUseCase", "CurateMembershipUseCase", "DesignAndAuditSplitsUseCase", "ReviewDatasetUseCase", "SealDatasetEditionUseCase", "PublishDatasetReleaseUseCase", "MaintainOrRecallDatasetUseCase"],
        "repositories": [f"{root}Repository" for root in roots], "factories": [f"{root}Factory" for root in roots],
        "specifications": ["PurposePopulationSpecification", "SourceAdmissionSpecification", "MembershipEvidenceSpecification", "RecipeReplaySpecification", "DuplicateAdjudicationSpecification", "CoverageSpecification", "PartitionIsolationSpecification", "LeakageAuditSpecification", "RightsUseSpecification", "DocumentationCompletenessSpecification", "EditionManifestSpecification", "ReleaseReadinessSpecification"],
        "state_machine": {"dataset": product["lifecycle_states"], "membership": ["proposed", "evidence_pending", "accepted", "excluded", "challenged", "superseded"], "audit": ["scope_draft", "running", "finding_open", "defeated", "accepted_risk", "failed", "passed_with_limits", "superseded"], "release": ["not_requested", "review_pending", "authorized", "published", "delivered", "deprecated", "superseded", "recalled"]},
        "policies_and_reactions": ["when source validity changes open an impact assessment", "when annotation or consent is revoked mark dependent editions affected", "when split leakage is unresolved refuse sealing", "when edition seals freeze its manifest and digest", "when documentation or rights are incomplete refuse release", "when a release is recalled notify every known consumer while preserving history"],
        "sagas_and_process_managers": ["DatasetCurationProcess", "SplitDesignAndAuditProcess", "DatasetReviewAndSealProcess", "DatasetPublicationProcess", "DatasetChangeImpactProcess", "DatasetRecallProcess"],
        "read_models_and_projections": ["DatasetDefinitionView", "MembershipDecisionView", "DuplicateComponentView", "CohortCoverageView", "SplitIsolationView", "LeakageAuditView", "RightsUseView", "DocumentationCompletenessView", "EditionManifestView", "ReleaseAndConsumerView"],
        "integration_event_policy": "Only editioned purpose, membership, split, audit, sealed-edition, release, supersession and recall facts cross the boundary; source truth, method internals, legal judgments, annotations, model state and downstream effects remain external.",
        "concurrency_and_idempotency": ["optimistic aggregate editions", "idempotency key per command", "membership decisions use source occurrence and rule editions", "parallel method attempts have occurrence identities", "sealing uses compare-and-swap over exact manifests", "unknown publication delivery is reconciled before retry", "recall and supersession are append-only"],
        "time_model": ["source event validity and recording time are imported", "membership decision, method attempt, annotation acceptance, rights validity, split assignment, audit, seal, release, delivery, use and recall times are distinct", "purpose policies consent rights and source membership may be bitemporal", "sealed editions never acquire new members", "maintenance creates successor editions"],
        "event_storming_swimlanes": ["dataset_owner", "source_owner", "curator", "annotation_owner", "method_provider", "rights_privacy_authority", "reviewer", "release_authority", "consumer", "affected_party"],
        "nonfunctional_laws": ["finite sources occurrences candidates dimensions cohorts splits methods attempts runtime memory output cost and deadlines", "cooperative cancellation with typed partial evidence", "determinism randomness approximation and numeric tolerance are explicit", "receipts bind exact semantic data method provider authority and time cuts", "provider substitution preserves dataset identity and decisions", "fail closed on missing purpose source identity rights audit evidence or release authority", "recovery never duplicates publication effects or rewrites sealed editions", product["automation_modality"]["removal_law"]],
    }
    return {
        "dossier_id": "ddd.ao.dataset_curation", "product_ref": PRODUCT, "status": "candidate_not_ratified",
        "product_truth": {"sovereign_question": product["sovereign_question"], "users": product["users"], "harmed_parties": product["harmed_parties"], "jobs": product["jobs"], "measurable_outcomes": product["outcomes"], "negative_mission": product["negative_mission"]},
        "strategic_and_tactical_ddd": ddd,
    }


def enrich_dataset_curation(source: dict[str, Any]) -> dict[str, Any]:
    product = product_artifact()
    keys = sorted(LIBRARIES)
    lib_ids = {library(key) for key in keys}
    source["sources"] = [row for row in source["sources"] if row["source_id"] not in set(EVIDENCE)] + SOURCES

    artifact_ids = {PRODUCT, *[owner(key) for key in keys], *[capability(key) for key in keys]}
    neighbor_specs = {
        "neighbor.policy_privacy": "Owns legal, consent, purpose, privacy, residency and disclosure authority.",
        "neighbor.versioned_storage": "Owns durable bytes, objects, commits, snapshots and restoration mechanics.",
        "neighbor.data_product_publication": "Owns data-product contracts, subscriptions, access, serving SLOs and consumer delivery.",
        "neighbor.catalog": "Owns discovery registration, search and catalog-record lifecycle.",
    }
    artifact_ids.update(neighbor_specs)
    artifact_ids.update({"implementation.dataset_curation.fiftyone", "implementation.dataset_curation.huggingface", "standard.dataset_curation.croissant", "standard.dataset_curation.dcat3"})
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in artifact_ids]
    source["artifacts"].append(product)
    for key in keys:
        source["artifacts"].extend([
            {"artifact_id": owner(key), "kind": "semantic_contract", "name": key.replace("_", " ").title(), "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": False, "definition": f"Owns the exact provider-neutral {key.replace('_', ' ')} question, types, decisions, invariants and refusals.", "evidence_refs": EVIDENCE},
            {"artifact_id": capability(key), "kind": "capability", "name": key.replace("_", " ").title(), "status": "candidate", "semantic_owner_ref": owner(key), "adoption_unit": False, "operated": False, "definition": f"Typed capability for {key.replace('_', ' ')}.", "evidence_refs": EVIDENCE},
        ])
    for ident, definition in neighbor_specs.items():
        source["artifacts"].append({"artifact_id": ident, "kind": "neighbor", "name": ident.split(".")[-1].replace("_", " ").title(), "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": True, "definition": definition, "evidence_refs": EVIDENCE[:5]})
    source["artifacts"].extend([
        {"artifact_id": "implementation.dataset_curation.fiftyone", "kind": "implementation", "name": "FiftyOne", "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": True, "definition": "Observed dataset exploration, curation, export and snapshot implementation; unqualified here.", "evidence_refs": EVIDENCE[6:9]},
        {"artifact_id": "implementation.dataset_curation.huggingface", "kind": "implementation", "name": "Hugging Face Dataset Hub", "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": True, "definition": "Observed dataset repository, version, card and distribution implementation; unqualified here.", "evidence_refs": EVIDENCE[9:11]},
        {"artifact_id": "standard.dataset_curation.croissant", "kind": "standard", "name": "Croissant 1.1", "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": False, "definition": "Dataset metadata interchange profile, not the complete curation product.", "evidence_refs": [EVIDENCE[2]]},
        {"artifact_id": "standard.dataset_curation.dcat3", "kind": "standard", "name": "DCAT 3", "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": False, "definition": "Catalog publication vocabulary, not the complete curation product.", "evidence_refs": [EVIDENCE[3]]},
    ])

    source["ownership"] = [row for row in source["ownership"] if not row["meaning_id"].startswith("meaning.dataset_curation.")]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in lib_ids]
    source["requirements"] = [row for row in source["requirements"] if not row["requirement_id"].startswith("requirement.dataset_curation.")]
    source["binding_maps"] = [row for row in source["binding_maps"] if not row["binding_map_id"].startswith("binding.dataset_curation.")]
    source["binding_gaps"] = [row for row in source["binding_gaps"] if not row["gap_id"].startswith("gap.ao.binding.dataset_curation.")]
    for key in keys:
        spec = LIBRARIES[key]
        source["ownership"].append({"meaning_id": f"meaning.dataset_curation.{key}", "term": key.replace("_", " "), "owner_ref": owner(key), "invariant": spec["invariants"][0], "must_not_be_owned_by": ["component.ao.optional_model_agent_extension", "neighbor.source_truth", "product.annotation_operations", "neighbor.model_lifecycle"]})
        source["libraries"].append({
            "library_id": library(key), "class": "semantic_pure", "product_ref": PRODUCT, "owner_ref": owner(key), "provides": [capability(key)],
            "types": spec["types"], "operations": spec["operations"], "decisions": spec["decisions"],
            "invariants": spec["invariants"] + ["provider_identity_does_not_change_semantics", "partiality_uncertainty_and_abstention_are_explicit", "generated_or_agent_output_is_non_authoritative_until_typed_validated_and_accepted", "removing_model_and_agent_extensions_preserves_the_deterministic_core_contract"],
            "refusals": spec["refusals"] + ["unsupported_capability", "unresolved_authority", "resource_exhausted", "cancelled"],
            "dependencies": [library(dep) for dep in spec["dependencies"]], "effect_boundary": "pure_no_io", "evidence_refs": EVIDENCE,
        })
        source["requirements"].append({"requirement_id": f"requirement.dataset_curation.{key}", "consumer_ref": PRODUCT, "capability_ref": capability(key), "minimum_qualified_offers": 2, "binding_phase": "compile_time", "status": "unbound", "refusal": "refuse compilation when no exact compatible qualified offer exists"})
        gap = f"gap.ao.binding.dataset_curation.{key}"
        source["binding_gaps"].append({"gap_id": gap, "product_ref": PRODUCT, "abstract_library_ref": library(key), "statement": f"No exact compiler registry contribution owns the complete {key.replace('_', ' ')} contract.", "blocking": True, "closure_evidence": "Add the exact pure contract with executable law oracles and independently qualify at least two substitutable implementations."})
        source["binding_maps"].append({"binding_map_id": f"binding.dataset_curation.{key}", "product_ref": PRODUCT, "abstract_library_ref": library(key), "compiler_disposition": "missing_exact_compiler_library_contract", "concrete_library_refs": [], "gap_ref": gap, "portable_offer": False})

    source["boundary_decisions"] = [row for row in source["boundary_decisions"] if row["decision_id"] != "decision.ao.dataset_curation.product"]
    source["boundary_decisions"].append({
        "decision_id": "decision.ao.dataset_curation.product", "subject_ref": PRODUCT, "disposition": "strong_product_candidate",
        "rationale": "Purpose-bound corpus membership, split/audit evidence, immutable edition identity, release and maintenance form an independently adopted and replaceable lifecycle. Preparation, annotation, quality methods, rights authority, storage, publication service and model lifecycle remain imported owners.",
        "evidence_refs": EVIDENCE,
        "split_test": {axis: {"score": 2, "finding": f"Dataset Curation has an independently falsifiable {axis} boundary; this does not ratify the product or qualify a provider.", "evidence_refs": EVIDENCE} for axis in ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]},
    })
    source["crosswalks"] = [row for row in source["crosswalks"] if row["legacy_ref"] != "candidate.product.dataset_curation_workbench"]
    source["crosswalks"].append({"legacy_ref": "candidate.product.dataset_curation_workbench", "canonical_refs": [PRODUCT, *sorted(lib_ids)], "disposition": "promote_independent_product_and_split_fourteen_pure_contracts"})

    rel_prefix = "relation.ao.dataset_curation."
    source["relations"] = [row for row in source["relations"] if not row["relation_id"].startswith(rel_prefix)]
    for index, target in enumerate(["neighbor.source_truth", "product.self_service_data_preparation", "product.annotation_operations", "neighbor.quality", "neighbor.policy_privacy", "neighbor.versioned_storage", "neighbor.data_product_publication", "neighbor.model_lifecycle"]):
        source["relations"].append({"relation_id": f"{rel_prefix}{index:02d}", "from_ref": PRODUCT, "predicate": "requires", "to_ref": target, "binding_phase": "compile_time"})
    source["relations"].append({"relation_id": f"{rel_prefix}optional_extension", "from_ref": "component.ao.optional_model_agent_extension", "predicate": "offers", "to_ref": PRODUCT, "binding_phase": "deployment_time"})

    negative_rows = [
        ("source_member", "A source occurrence is automatically a dataset member.", "require explicit admission and membership decision"),
        ("view_edition", "A filter or saved view is a sealed dataset edition.", "require immutable complete manifest and digest"),
        ("snapshot_edition", "A storage snapshot proves dataset semantic completeness.", "separate captured bytes from curation edition identity"),
        ("score_removal", "A similarity or quality score authorizes removal.", "require typed curation decision and authority"),
        ("balanced_representative", "Numerical class balance proves population representativeness.", "preserve population coverage uncertainty and purpose"),
        ("random_split_safe", "A random split is leakage-free.", "test group temporal entity target and similarity boundaries"),
        ("no_detection_no_leakage", "No detected contamination proves absence of contamination.", "publish method coverage limitations and residual risk"),
        ("annotation_dataset", "An annotation release and a curated dataset edition are identical.", "bind zero or many annotation editions through explicit coverage"),
        ("policy_authority", "A license string or ODRL expression proves legal authority or consent.", "require authoritative evidence and conflict evaluation"),
        ("card_truth", "A dataset card or datasheet proves every statement and fitness claim.", "bind statements to evidence unknowns and review"),
        ("release_use", "Dataset publication proves lawful suitable downstream use.", "require consumer-specific fitness rights and decision authority"),
        ("agent_curation", "A model or agent may silently decide membership, rights, split safety or release.", "retain attributed proposals and deterministic acceptance gates"),
    ]
    ids = {f"negative.dataset_curation.{row[0]}" for row in negative_rows}
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in ids]
    source["negative_tests"].extend({"test_id": f"negative.dataset_curation.{ident}", "prohibited_claim": claim, "expected_result": result} for ident, claim, result in negative_rows)
    source["ddd_dossiers"] = [row for row in source["ddd_dossiers"] if row["product_ref"] != PRODUCT] + [dossier(product)]
    laws = [
        "source occurrence != admitted candidate != dataset member != annotation occurrence != model example",
        "working cut != view != snapshot != sealed dataset edition != distribution != release",
        "duplicate candidate != duplicate decision != removal authority",
        "balance != coverage != representativeness != fitness",
        "policy expression != legal authority != consent evidence != permitted use",
        "dataset release != downstream use != decision != effect != outcome",
    ]
    source["non_collapse_laws"] = [row for row in source["non_collapse_laws"] if row not in set(laws)] + laws
    source["scope"] = "Six job-specific analytical-operation products: self-service data preparation, annotation/ground-truth operations, dataset curation, document processing/review, visual inspection operations, and signal condition monitoring/diagnostics."
    return source
