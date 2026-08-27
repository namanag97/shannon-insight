#!/usr/bin/env python3
"""Project the researched lineage/provenance universe into one governed product boundary.

The product owns derivation assertions, capture, graph qualification, query, possible-impact
analysis and correction propagation.  It explicitly does not absorb causal truth, audit,
independent appraisal, custody, retention, disclosure policy, runtime execution or source facts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LPE = ROOT / "research/domain_atlas/universes/lineage_provenance_evidence"
PRODUCT = "product.lineage_provenance"
OWNER = "semantic.lineage_provenance"

PRODUCT_FIELDS = {
    "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
    "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
}
DDD_FIELDS = {
    "domain_vision_statement", "subdomain_classification", "bounded_context_boundary",
    "ubiquitous_language_policy", "context_map", "anti_corruption_layers", "published_language",
    "value_objects", "entities", "aggregates", "aggregate_roots", "aggregate_invariants",
    "commands", "domain_events", "refusal_failure_catalog", "domain_services",
    "application_services", "repositories", "factories", "specifications", "state_machine",
    "policies_and_reactions", "sagas_and_process_managers", "read_models_and_projections",
    "integration_event_policy", "concurrency_and_idempotency", "time_model",
    "event_storming_swimlanes", "nonfunctional_laws",
}

AUTOMATION = {
    "default": "DETERMINISTIC_CORE_ONLY",
    "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
    "law": "Models or agents may propose mappings, missing-edge candidates, explanations, impact hypotheses or repair plans only; deterministic identity, constraint, coverage, policy and authority checks decide whether a proposal becomes an assertion.",
    "removal_law": "Removing every optional model or agent preserves capture, validation, graph storage, query, impact slicing, evidence packaging, correction, retraction and recall propagation; an intent that explicitly requires such assistance may instead yield capability_unavailable.",
    "hard_work_law": "Automation never replaces source attribution, vocabulary, relation semantics, identity resolution, temporal scope, coverage accounting, invariants, authority, evidence qualification, provider conformance or domain acceptance.",
}

SELECTED_SOURCE_REFS = {
    "source.lpe.fda.electronic.2024", "source.lpe.ietf.rfc8493", "source.lpe.oasis.csaf",
    "source.lpe.openlineage.column", "source.lpe.openlineage.facets",
    "source.lpe.openlineage.spec", "source.lpe.sdmx.30", "source.lpe.sigstore.bundle",
    "source.lpe.w3c.prov.aq", "source.lpe.w3c.prov.constraints",
    "source.lpe.w3c.prov.dm", "source.lpe.w3c.prov.links", "source.lpe.w3c.prov.n",
    "source.lpe.w3c.prov.o",
}


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


LIBRARY_SPECS = [
    {
        "library_id": "library.provenance_core",
        "capability_ref": "capability.record_lineage",
        "name": "Provenance and lineage assertion core",
        "definition": "Own typed entity/activity/agent and logical-lineage assertions without claiming causality or source truth.",
        "concrete": ["library.lpe.prov-statement-algebra","library.lpe.provenance-assertion", "library.lpe.provenance-bundle", "library.lpe.lineage-core"],
        "types": ["ProvenanceEntity", "ProvenanceActivity", "ProvenanceAgent", "QualifiedRelation", "LineageNode", "LineageEdge", "LineageLayer", "CoverageStatement"],
        "operations": ["validate_assertion", "record_logical_edge", "qualify_relation", "quarantine_ambiguous_assertion"],
        "decisions": ["relation_kind", "lineage_layer", "assertion_scope", "ambiguity_posture"],
        "invariants": ["derivation is not causation", "prospective lineage is not observed execution", "identity edition occurrence and digest remain distinct", "unknown coverage remains explicit"],
        "refusals": ["unresolved_subject", "unattributed_assertion", "relation_kind_unknown", "lineage_layer_collapsed"],
        "dependencies": [], "effect_boundary": "pure_effect_intents",
    },
    {
        "library_id": "library.governance_lineage.constraints",
        "capability_ref": "capability.governance_lineage.validate_constraints",
        "name": "Provenance constraint and inference oracle",
        "definition": "Validate relation-specific ordering and structural constraints while retaining an inference trace.",
        "concrete": ["library.lpe.prov-constraints"],
        "types": ["ProvConstraint", "ValidationFinding", "InferenceTrace", "ConstraintProfileEdition"],
        "operations": ["validate_graph_constraints", "infer_qualified_relation"],
        "decisions": ["constraint_profile", "inference_posture", "violation_severity"],
        "invariants": ["validation never turns integrity into truth", "inferred and observed assertions remain distinct", "a provenance graph is not assumed to be a universal DAG"],
        "refusals": ["constraint_profile_unknown", "ordering_violation", "unbounded_inference"],
        "dependencies": ["library.provenance_core"], "effect_boundary": "pure_no_io",
    },
    {
        "library_id": "library.governance_lineage.interchange",
        "capability_ref": "capability.governance_lineage.interchange_bundles",
        "name": "Provenance bundle interchange",
        "definition": "Import and export editioned provenance bundles with namespaces, profiles and explicit loss reports.",
        "concrete": ["library.lpe.prov-interchange"],
        "types": ["ProvenanceBundle", "ProvProfile", "NamespaceMap", "LossReport"],
        "operations": ["import_bundle", "export_bundle", "link_bundles"],
        "decisions": ["interchange_profile", "unknown_relation_posture", "namespace_collision_policy"],
        "invariants": ["interchange never silently loses required semantics", "bundle identity does not imply member truth"],
        "refusals": ["unsupported_profile", "namespace_collision", "undeclared_loss"],
        "dependencies": ["library.provenance_core", "library.governance_lineage.constraints"], "effect_boundary": "effectful_runtime",
    },
    {
        "library_id": "library.governance_lineage.runtime_capture",
        "capability_ref": "capability.governance_lineage.capture_runtime",
        "name": "Runtime lineage capture adapter",
        "definition": "Translate exact run/input/output occurrences into canonical assertions with deduplication and source attribution.",
        "concrete": ["library.lpe.openlineage-adapter"],
        "types": ["RunOccurrence", "RunEvent", "DatasetOccurrence", "FacetRegistry", "ProducerEdition", "CaptureReceipt"],
        "operations": ["observe_run_inputs", "observe_run_outputs", "deduplicate_event", "translate_facets"],
        "decisions": ["event_identity", "facet_profile", "late_event_posture", "deduplication_scope"],
        "invariants": ["declared inputs are not actual inputs", "capture time is not event time", "adapter identity cannot change canonical meaning"],
        "refusals": ["run_identity_missing", "producer_edition_missing", "facet_semantics_unknown", "conflicting_duplicate"],
        "dependencies": ["library.provenance_core"], "effect_boundary": "effectful_runtime",
    },
    {
        "library_id": "library.governance_lineage.field_derivation",
        "capability_ref": "capability.governance_lineage.capture_field_derivation",
        "name": "Field and column derivation",
        "definition": "Record field-level dependencies, transform kinds and extraction gaps over exact schema editions.",
        "concrete": ["library.lpe.field-lineage"],
        "types": ["SchemaEditionRef", "FieldPath", "FieldDependency", "TransformKind", "ExtractionGap"],
        "operations": ["capture_field_edge", "validate_field_identity", "record_extraction_gap"],
        "decisions": ["field_identity_profile", "transform_classification", "unknown_expression_posture"],
        "invariants": ["field lineage binds exact schema and expression editions", "parser failure cannot become no-dependency"],
        "refusals": ["field_identity_ambiguous", "schema_edition_missing", "transform_kind_unknown"],
        "dependencies": ["library.provenance_core"], "effect_boundary": "pure_no_io",
    },
    {
        "library_id": "library.governance_lineage.formula_derivation",
        "capability_ref": "capability.governance_lineage.capture_formula_derivation",
        "name": "Formula and semantic derivation",
        "definition": "Record formula-AST, operand-role, grain and unit dependencies without executing or governing the formula.",
        "concrete": ["library.lpe.formula-provenance"],
        "types": ["FormulaEditionRef", "FormulaAstDigest", "OperandRole", "SemanticGrain", "UnitContract"],
        "operations": ["capture_formula_dependency", "validate_operand_binding"],
        "decisions": ["formula_identity", "operand_role", "grain_binding", "unit_compatibility"],
        "invariants": ["formula lineage does not own formula meaning or execution", "unit and grain loss remain explicit"],
        "refusals": ["formula_edition_missing", "operand_role_ambiguous", "grain_or_unit_unbound"],
        "dependencies": ["library.provenance_core"], "effect_boundary": "pure_no_io",
    },
    {
        "library_id": "library.governance_lineage.graph_query",
        "capability_ref": "capability.governance_lineage.query_graph",
        "name": "Bounded lineage graph query",
        "definition": "Compute time-, layer-, purpose- and policy-scoped graph cuts with coverage and redaction gaps.",
        "concrete": ["library.lpe.lineage-query"],
        "types": ["TraversalRequest", "GraphCut", "PathKind", "TimeCut", "CoverageGap", "RedactionGap"],
        "operations": ["slice_graph", "compute_upstream_cut", "compute_downstream_cut", "explain_path"],
        "decisions": ["path_semantics", "traversal_budget", "time_cut", "redaction_posture"],
        "invariants": ["query result completeness is bounded by declared coverage", "redaction is not absence", "path existence is not causation"],
        "refusals": ["unbounded_traversal", "time_cut_missing", "policy_decision_missing", "coverage_unknown"],
        "dependencies": ["library.provenance_core", "library.governance_lineage.constraints"], "effect_boundary": "pure_no_io",
    },
    {
        "library_id": "library.governance_lineage.impact_invalidation",
        "capability_ref": "capability.governance_lineage.evaluate_impact",
        "name": "Lineage impact and invalidation",
        "definition": "Classify possible downstream impact, coordinate review and emit notification or invalidation intents.",
        "concrete": ["library.lpe.impact-analysis"],
        "types": ["ImpactPath", "ImpactState", "ReviewPriority", "InvalidationIntent", "NotificationIntent"],
        "operations": ["classify_impact_path", "prioritize_review", "confirm_external_impact", "propose_invalidation"],
        "decisions": ["possible_vs_confirmed", "priority_policy", "propagation_scope", "stop_condition"],
        "invariants": ["possible impact is not observed corruption or business harm", "notification and invalidation remain external effects"],
        "refusals": ["coverage_insufficient", "impact_policy_missing", "confirmation_authority_missing"],
        "dependencies": ["library.governance_lineage.graph_query"], "effect_boundary": "pure_effect_intents",
    },
    {
        "library_id": "library.governance_lineage.evidence_bundle",
        "capability_ref": "capability.governance_lineage.package_evidence",
        "name": "Lineage evidence bundle",
        "definition": "Package exact assertion, source, validation, coverage and redaction materials for a scoped reliance claim.",
        "concrete": ["library.lpe.evidence-bundle"],
        "types": ["EvidenceManifest", "EvidenceMember", "CoverageStatement", "RedactionDeclaration", "BundleValidation"],
        "operations": ["assemble_evidence_bundle", "validate_bundle", "declare_redaction"],
        "decisions": ["member_scope", "coverage_statement", "redaction_declaration", "bundle_profile"],
        "invariants": ["a provenance bundle is not automatically sufficient evidence", "bundle integrity does not prove member truth or authority"],
        "refusals": ["member_identity_missing", "coverage_undeclared", "redaction_unverifiable"],
        "dependencies": ["library.provenance_core", "library.governance_lineage.constraints"], "effect_boundary": "pure_no_io",
    },
    {
        "library_id": "library.governance_lineage.correction_recall",
        "capability_ref": "capability.governance_lineage.govern_correction",
        "name": "Lineage correction, retraction and recall propagation",
        "definition": "Preserve prior assertions while publishing corrected editions, retractions and downstream recall intents.",
        "concrete": ["library.lpe.record-lifecycle"],
        "types": ["RecordEdition", "CorrectionNotice", "RetractionNotice", "RecallNotice", "AffectedScope", "Acknowledgement"],
        "operations": ["publish_correction", "retract_assertion", "propagate_recall", "record_acknowledgement"],
        "decisions": ["lifecycle_kind", "affected_scope", "replacement_binding", "propagation_cut"],
        "invariants": ["correction is not deletion", "retraction is not recall", "history is preserved", "recall delivery is an external effect"],
        "refusals": ["correction_authority_missing", "affected_scope_unresolved", "history_preservation_impossible"],
        "dependencies": ["library.provenance_core", "library.governance_lineage.impact_invalidation"], "effect_boundary": "pure_effect_intents",
    },
    {
        "library_id": "library.governance_lineage.repository_port",
        "capability_ref": "capability.governance_lineage.persist_graph",
        "name": "Lineage repository persistence port",
        "definition": "Plan and reconcile assertion append, immutable graph-edition, cut-bound read, change-scan, verification and externally authorized disposition effects without acquiring lineage semantics, truth, completeness or retention authority.",
        "concrete": [],
        "types": ["LineageRepositoryPortEdition", "RepositoryOccurrenceRef", "AssertionAppendBatch", "AssertionAppendIntent", "RepositoryAppendReceipt", "GraphEditionManifest", "GraphEditionPublicationIntent", "GraphCutReadIntent", "RepositoryCursor", "ChangeScanIntent", "SnapshotVerificationResult", "ExternalDispositionDecisionRef", "RepositoryDispositionIntent", "RepositoryDispositionReceipt"],
        "operations": ["assemble_assertion_append_batch", "plan_assertion_append", "reconcile_append_receipt", "assemble_graph_edition_manifest", "plan_graph_edition_publication", "reconcile_graph_edition_receipt", "plan_graph_cut_load", "validate_loaded_graph_cut", "plan_change_scan", "validate_change_page", "verify_repository_snapshot", "plan_repository_disposition", "reconcile_disposition_receipt"],
        "decisions": ["repository_occurrence_identity", "assertion_identity_and_uniqueness", "append_batch_atomicity", "duplicate_and_conflict_posture", "consistency_and_read_isolation", "graph_edition_manifest", "cursor_scope_and_expiry", "bitemporal_cut", "coverage_and_redaction_gaps", "retention_hold_and_disposition_authority"],
        "invariants": ["assertion edition repository occurrence commit graph edition snapshot and representation identities remain distinct", "append acknowledgement is not semantic validation or acceptance", "commit order is not event validity or causal order", "not-found policy-hidden wrong-cut incomplete-coverage and proven absence remain distinct", "retention hold disclosure redaction and erasure authority remain external", "unknown completion reconciles before retry"],
        "refusals": ["repository_occurrence_unbound", "assertion_identity_conflict", "precondition_failed", "atomicity_unsupported", "consistency_profile_unsupported", "graph_edition_conflict", "temporal_cut_invalid", "coverage_unknown", "cursor_invalid", "cursor_expired", "disposition_authority_missing", "legal_hold_conflict", "effect_completion_unknown"],
        "dependencies": ["library.provenance_core"], "effect_boundary": "effect_port_contract",
    },
]


def _source_rows() -> list[dict[str, Any]]:
    result = []
    for row in jsonl(LPE / "sources.jsonl"):
        if row["source_id"] not in SELECTED_SOURCE_REFS:
            continue
        result.append({
            "source_id": row["source_id"],
            "source_class": "primary_research" if row["source_kind"] == "primary_research" else "official_specification_or_documentation",
            "title": row["title"], "publisher": row["publisher"], "uri": row["url"],
            "retrieved_at": row["accessed_on"], "claim": row["authority_scope"],
            "scope_limit": " ".join(row["limitations"]),
        })
    return result


def _capability(spec: dict[str, Any]) -> dict[str, Any]:
    refs = sorted({ref for concrete in spec["concrete"] for ref in UPSTREAM[concrete]["evidence_refs"]})
    if not refs:
        refs = ["source.lpe.w3c.prov.dm", "source.lpe.w3c.prov.aq"]
    return {
        "artifact_id": spec["capability_ref"], "kind": "capability", "name": spec["name"],
        "status": "specified_candidate", "semantic_owner_ref": OWNER,
        "adoption_unit": False, "operated": False, "definition": spec["definition"],
        "evidence_refs": refs,
    }


def _library(spec: dict[str, Any]) -> dict[str, Any]:
    refs = sorted({ref for concrete in spec["concrete"] for ref in UPSTREAM[concrete]["evidence_refs"]})
    if not refs:
        refs = ["source.lpe.w3c.prov.dm", "source.lpe.w3c.prov.aq"]
    return {
        "library_id": spec["library_id"], "class": "effect_port_contract" if not spec["concrete"] else "semantic_or_adapter",
        "owner_ref": OWNER, "provides": [spec["capability_ref"]], "types": spec["types"],
        "operations": spec["operations"], "decisions": spec["decisions"],
        "invariants": spec["invariants"], "refusals": spec["refusals"],
        "dependencies": spec["dependencies"], "effect_boundary": spec["effect_boundary"],
        "evidence_refs": refs, "product_refs": [PRODUCT],
    }


def _product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "What prospective and observed derivation assertions, coverage limits, evidence and lifecycle changes connect exact enterprise data, process, formula and result occurrences without promoting a path to causality or truth?",
        "users": ["data_engineer", "analytics_engineer", "data_steward", "data_product_owner", "impact_analyst", "assurance_reviewer", "incident_investigator"],
        "harmed_parties": ["data_subject", "source_owner", "downstream_consumer", "decision_subject", "runtime_operator", "evidence_relying_party"],
        "jobs": ["Capture, qualify, store, query and exchange prospective and retrospective lineage; expose coverage and ambiguity; evaluate possible downstream impact; and propagate corrections, retractions and recalls."],
        "outcomes": ["qualified_derivation_assertion_graph", "declared_capture_and_coverage_gaps", "bounded_upstream_downstream_cuts", "possible_impact_review", "scoped_lineage_evidence_bundle", "history_preserving_correction_and_recall"],
        "negative_mission": "Does not own source facts, causal inference, audit or security events, data-quality fitness, master identity, workflow/runtime execution, formula meaning, independent appraisal, custody, retention/erasure/disclosure authority, notification effects or vertical acceptance.",
        "lifecycle_states": ["draft", "capture_pending", "captured", "identity_pending", "quarantined_ambiguous", "validated", "published", "partially_covered", "impact_review", "correction_pending", "corrected", "retracted", "recall_open", "superseded", "archived_reference"],
        "commands": ["open_capture_batch", "record_prospective_assertion", "record_observed_assertion", "resolve_assertion_identity", "validate_provenance_constraints", "quarantine_ambiguous_assertion", "publish_graph_edition", "query_graph_cut", "classify_possible_impact", "confirm_external_impact", "assemble_lineage_evidence", "publish_correction", "retract_assertion", "open_recall", "record_recall_acknowledgement", "supersede_graph_edition"],
        "events": ["capture_batch_opened", "prospective_assertion_recorded", "observed_assertion_recorded", "assertion_identity_resolved", "provenance_constraints_validated", "ambiguous_assertion_quarantined", "graph_edition_published", "graph_cut_queried", "possible_impact_classified", "external_impact_confirmed", "lineage_evidence_assembled", "correction_published", "assertion_retracted", "recall_opened", "recall_acknowledgement_recorded", "graph_edition_superseded"],
        "invariants": ["prospective lineage is not observed execution", "logical physical runtime field and formula lineage remain distinct", "derivation and graph reachability are not causation", "audit log provenance graph and evidence bundle are not synonyms", "identity digest signature authority and truth remain distinct", "coverage redaction ambiguity and source gaps are explicit", "possible impact is not confirmed harm", "correction retraction recall and deletion remain distinct", "effect authority remains external"],
        "refusals": ["subject_identity_unresolved", "assertion_source_unattributed", "lineage_layer_unknown", "relation_semantics_unknown", "event_or_validity_time_missing", "conflicting_duplicate", "provenance_constraint_violation", "coverage_unknown", "query_budget_exceeded", "policy_decision_missing", "impact_confirmation_authority_missing", "correction_authority_missing", "repository_provider_unbound", "evidence_bundle_incomplete"],
        "automation_modality": AUTOMATION,
    }


def _dossier() -> dict[str, Any]:
    truth = _product_truth()
    ddd = {
        "domain_vision_statement": "Own qualified, time-scoped derivation assertions and their coverage, query, possible-impact and correction lifecycle without claiming causal or source truth.",
        "subdomain_classification": "core_horizontal_lineage_and_provenance_evidence_product",
        "bounded_context_boundary": {
            "inside": ["prospective and retrospective derivation assertions", "logical physical runtime field and formula lineage layers", "entity activity agent run dataset field formula and result occurrence references", "capture source attribution deduplication ambiguity and coverage", "provenance graph constraints editions bundles and interchange", "bounded lineage query and path explanation", "possible-impact classification and review coordination", "lineage evidence packaging", "history-preserving correction retraction recall and supersession", "repository port and persistence receipts"],
            "outside": ["source business-fact truth", "causal inference", "workflow runtime and effect execution", "audit/security event ownership", "data-quality fitness and reconciliation truth", "master or entity-link authority", "formula/model/method meaning", "attestation issuer and independent appraisal", "custody forensic preservation retention legal hold erasure and disclosure authority", "notification delivery and vertical acceptance"],
        },
        "ubiquitous_language_policy": "Entity, activity, agent, occurrence, assertion, derivation, influence, lineage layer, prospective, observed, graph edition, bundle, coverage, ambiguity, path, possible impact, confirmed impact, correction, retraction, recall and deletion each have one non-interchangeable meaning. A model-proposed edge remains a proposal until the same deterministic checks as any other source pass.",
        "context_map": [
            {"neighbor_ref": "product.solution_compiler", "relationship": "published_language", "translation": "consume prospective plans and compiler receipts without treating them as runtime facts"},
            {"neighbor_ref": "product.pipeline_orchestration", "relationship": "customer_supplier_acl", "translation": "translate run and I/O occurrences without acquiring execution semantics"},
            {"neighbor_ref": "product.semantic_metric_formula", "relationship": "customer_supplier_acl", "translation": "consume exact formula AST grain unit and binding editions"},
            {"neighbor_ref": "product.model_lifecycle", "relationship": "customer_supplier_acl", "translation": "consume model study feature data and evaluation occurrence references"},
            {"neighbor_ref": "product.data_quality_operations", "relationship": "open_host_service", "translation": "exchange scoped lineage evidence without converting paths into defects"},
            {"neighbor_ref": "product.schema_and_data_contract", "relationship": "anti_corruption_layer", "translation": "bind schema and contract editions without owning compatibility or acceptance"},
            {"neighbor_ref": "product.master_and_entity_resolution", "relationship": "anti_corruption_layer", "translation": "consume adjudicated identifiers without creating master truth"},
            {"neighbor_ref": "product.data_use_privacy_retention", "relationship": "customer_supplier", "translation": "obtain query disclosure retention and erasure decisions"},
            {"neighbor_ref": "product.independent_assurance", "relationship": "customer_supplier", "translation": "submit lineage evidence for separate appraisal"},
            {"neighbor_ref": "product.digital_preservation", "relationship": "customer_supplier", "translation": "export preservation packages while custody and long-term validity remain external"},
        ],
        "anti_corruption_layers": ["acl.compiler_plan_receipt", "acl.runtime_capture", "acl.schema_contract", "acl.semantic_formula", "acl.model_study", "acl.master_entity_identity", "acl.quality_reconciliation", "acl.policy_privacy_retention", "acl.assurance", "acl.preservation"],
        "published_language": ["LineageAssertionId", "LineageAssertionEdition", "SubjectOccurrenceRef", "ProvenanceEntity", "ProvenanceActivity", "ProvenanceAgent", "QualifiedRelation", "LineageLayer", "ProspectiveAssertion", "ObservedAssertion", "GraphEdition", "ProvenanceBundle", "CoverageStatement", "AmbiguityGap", "GraphCut", "ImpactState", "EvidenceManifest", "CorrectionNotice", "RetractionNotice", "RecallNotice", "TypedRefusal", "PersistenceReceipt"],
        "value_objects": ["LineageAssertionId", "AssertionEdition", "SubjectOccurrenceRef", "SourceOccurrenceRef", "EntityRef", "ActivityRef", "AgentRef", "RunRef", "DatasetCutRef", "FieldPath", "FormulaAstDigest", "LineageLayer", "RelationKind", "Direction", "TimeCut", "CoverageStatement", "AmbiguityGap", "EvidenceMemberRef", "ValidityInterval", "RecordingInstant"],
        "entities": ["LineageAssertion", "CaptureBatch", "ProvenanceBundle", "ProvenanceGraphEdition", "ImpactReview", "LineageEvidencePackage", "CorrectionNotice", "RetractionNotice", "RecallCampaign"],
        "aggregates": [
            {"root": "LineageAssertion", "members": ["subject_refs", "relation", "layer", "source", "times", "coverage", "validation", "lifecycle"], "consistency": "one immutable assertion edition binds exact subjects, occurrence, semantics, source and temporal scope"},
            {"root": "CaptureBatch", "members": ["producer", "source_cut", "events", "deduplication", "ambiguities", "coverage", "receipt"], "consistency": "capture never converts missing, conflicting or late observations into absence"},
            {"root": "ProvenanceGraphEdition", "members": ["assertion_refs", "constraint_profile", "validation", "coverage", "indexes", "publication"], "consistency": "publication binds one immutable assertion cut and validation profile"},
            {"root": "ImpactReview", "members": ["trigger", "graph_cut", "possible_paths", "coverage_gaps", "confirmations", "intents"], "consistency": "possible, reviewed, confirmed and externally acted impact remain separate"},
            {"root": "LineageLifecycleCase", "members": ["affected_assertions", "correction", "retraction", "recall", "acknowledgements", "state"], "consistency": "prior history is retained and each lifecycle action carries distinct authority"},
        ],
        "aggregate_roots": ["LineageAssertion", "CaptureBatch", "ProvenanceGraphEdition", "ImpactReview", "LineageLifecycleCase"],
        "aggregate_invariants": truth["invariants"] + ["same canonical inputs and profile produce the same validation and graph-cut result", "all published evidence binds exact assertion graph policy and time editions", "provider identity cannot alter relation semantics"],
        "commands": truth["commands"],
        "domain_events": truth["events"],
        "refusal_failure_catalog": truth["refusals"] + ["interchange_loss_undeclared", "redaction_scope_unverifiable", "recall_propagation_partial", "optional_assistance_unavailable"],
        "domain_services": ["AssertionQualificationService", "CaptureDeduplicationService", "ProvenanceConstraintService", "CoverageAccountingService", "GraphSliceService", "ImpactClassificationService", "EvidencePackagingService", "CorrectionPropagationService"],
        "application_services": ["RecordProspectiveLineageUseCase", "CaptureRuntimeLineageUseCase", "PublishGraphEditionUseCase", "QueryLineageUseCase", "ReviewImpactUseCase", "ExportEvidenceUseCase", "CorrectAssertionUseCase", "RetractAssertionUseCase", "RecallDownstreamUseCase"],
        "repositories": ["LineageAssertionRepository", "CaptureBatchRepository", "GraphEditionRepository", "ImpactReviewRepository", "LineageLifecycleCaseRepository"],
        "factories": ["LineageAssertionFactory", "CaptureBatchFactory", "GraphEditionFactory", "ImpactReviewFactory", "LineageLifecycleCaseFactory"],
        "specifications": ["AssertionIdentitySpecification", "RelationSemanticsSpecification", "TemporalScopeSpecification", "ProvenanceConstraintSpecification", "CaptureCoverageSpecification", "GraphQueryAuthorizationSpecification", "ImpactConfirmationSpecification", "EvidenceBundleCompletenessSpecification", "CorrectionAuthoritySpecification"],
        "state_machine": {
            "assertion": ["draft", "identity_pending", "quarantined_ambiguous", "validated", "published", "corrected", "retracted", "superseded"],
            "capture": ["open", "receiving", "partially_covered", "sealed", "reconciled", "failed"],
            "impact": ["possible", "review_pending", "reviewed", "confirmed", "refuted", "unknown", "intent_submitted", "closed"],
            "recall": ["draft", "authorized", "open", "partially_acknowledged", "closed", "cancelled"],
        },
        "policies_and_reactions": ["when identity or relation semantics are ambiguous quarantine rather than guess", "when a declared plan is observed retain prospective and retrospective assertions separately", "when coverage is partial attach gaps to every affected query and evidence result", "when an upstream correction is published compute possible downstream impact and open review", "when impact is externally confirmed emit notification or invalidation intents without executing them", "when an assertion is retracted preserve history and stop new reliance under the policy", "when a source event conflicts with an existing occurrence retain both and open reconciliation"],
        "sagas_and_process_managers": ["RuntimeCaptureProcess", "GraphPublicationProcess", "PossibleImpactReviewProcess", "CorrectionPropagationProcess", "DownstreamRecallProcess", "LineageEvidenceExportProcess"],
        "read_models_and_projections": ["AssertionDetailView", "CaptureCoverageView", "ProvenanceGraphView", "UpstreamGraphCut", "DownstreamGraphCut", "FieldAndFormulaLineageView", "ImpactReviewView", "CorrectionRetractionRecallView", "EvidenceBundleView"],
        "integration_event_policy": "Only editioned, minimized assertion, coverage, validation, graph-publication, possible-impact, correction, retraction, recall and evidence facts cross the boundary. Source facts, causal conclusions, policy decisions, effect outcomes and independent appraisal remain foreign facts.",
        "concurrency_and_idempotency": ["optimistic aggregate edition", "idempotency key binds producer occurrence and canonical event digest", "duplicate and conflicting duplicate remain distinct outcomes", "capture and graph publication are append-only", "graph queries bind immutable graph and policy cuts", "unknown external completion reconciles before retry", "correction and recall attempts never erase prior attempts"],
        "time_model": ["event observation recording transaction and publication times are distinct", "validity time and recording time are both retained", "prospective plan validity differs from execution occurrence time", "retrieval appraisal decision and disposition times remain external but referenceable", "correction retraction recall acknowledgement and supersession each carry event validity and recording times", "queries bind an explicit bitemporal graph cut"],
        "event_storming_swimlanes": ["source_system", "pipeline_or_runtime", "data_engineer", "data_steward", "data_product_owner", "impact_analyst", "policy_authority", "assurance_reviewer", "affected_consumer"],
        "nonfunctional_laws": ["deterministic identity constraint validation and bounded graph traversal", "finite graph depth nodes edges time memory and cost", "stream backpressure cooperative cancellation and resumable cursors", "typed partial unknown ambiguous and redacted outcomes", "encryption and policy enforcement do not create truth", "receipts bind source occurrence graph profile policy provider and time cuts", "provider identity cannot change semantic meaning", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {
        "dossier_id": "ddd.governance.lineage_provenance", "product_ref": PRODUCT,
        "status": "candidate_not_ratified", "product_truth": {
            "sovereign_question": truth["sovereign_question"], "users": truth["users"],
            "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"],
            "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"],
        }, "strategic_and_tactical_ddd": ddd,
    }


UPSTREAM = {row["library_id"]: row for row in jsonl(LPE / "library-boundaries.jsonl")}


def enrich_lineage(source: dict[str, Any]) -> dict[str, Any]:
    generated_artifacts = {spec["capability_ref"] for spec in LIBRARY_SPECS if spec["capability_ref"] != "capability.record_lineage"}
    generated_libraries = {spec["library_id"] for spec in LIBRARY_SPECS if spec["library_id"] != "library.provenance_core"}
    generated_requirements = {f"requirement.governance_lineage.{spec['library_id'].split('.')[-1]}" for spec in LIBRARY_SPECS if spec["capability_ref"] != "capability.record_lineage"}
    generated_relations = {
        "relation.governance_lineage.requires_schema", "relation.governance_lineage.requires_contract",
        "relation.governance_lineage.requires_policy", "relation.governance_lineage.exchanges_quality",
    }
    generated_negatives = {
        "negative.lineage.plan_actual", "negative.lineage.causality", "negative.lineage.coverage",
        "negative.lineage.audit", "negative.lineage.integrity_truth", "negative.lineage.impact",
        "negative.lineage.correction_delete", "negative.lineage.model_assertion",
        "negative.lineage.provider_qualification", "negative.lineage.persistence_retention",
    }

    source["sources"] = [row for row in source["sources"] if row["source_id"] not in SELECTED_SOURCE_REFS] + _source_rows()
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in generated_artifacts]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in generated_libraries]
    source["requirements"] = [row for row in source["requirements"] if row["requirement_id"] not in generated_requirements]
    source["relations"] = [row for row in source["relations"] if row["relation_id"] not in generated_relations]
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in generated_negatives]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if PRODUCT not in row.get("product_refs", [])]
    source["binding_gaps"] = [row for row in source.get("binding_gaps", []) if row.get("product_ref") != PRODUCT]
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT]

    product = next(row for row in source["artifacts"] if row["artifact_id"] == PRODUCT)
    product.update(_product_truth())

    provenance_core = next(row for row in source["libraries"] if row["library_id"] == "library.provenance_core")
    provenance_core.update(_library(LIBRARY_SPECS[0]))
    source["artifacts"].extend(_capability(spec) for spec in LIBRARY_SPECS[1:])
    source["libraries"].extend(_library(spec) for spec in LIBRARY_SPECS[1:])

    for spec in LIBRARY_SPECS[1:]:
        suffix = spec["library_id"].split(".")[-1]
        source["requirements"].append({
            "requirement_id": f"requirement.governance_lineage.{suffix}",
            "consumer_ref": PRODUCT, "capability_ref": spec["capability_ref"],
            "binding_phase": "runtime" if spec["effect_boundary"] in {"effectful_runtime", "effect_port_contract"} else "compile_time",
            "minimum_qualified_offers": 1, "status": "unbound",
            "refusal": f"no_qualified_{suffix}_implementation",
        })

    for spec in LIBRARY_SPECS:
        concrete = (["library.lineage_repository.port"]
                    if spec["library_id"] == "library.governance_lineage.repository_port"
                    else spec["concrete"])
        suffix = spec["library_id"].split(".")[-1]
        is_gap = not concrete
        source["binding_maps"].append({
            "binding_map_id": f"binding.governance_lineage.{suffix}",
            "product_refs": [PRODUCT], "abstract_library_ref": spec["library_id"],
            "concrete_library_refs": concrete,
            "required_requirement_refs": [f"requirement.{ref.removeprefix('library.')}.implementation" for ref in concrete],
            "portable_offer_refs": [f"offer.{ref.removeprefix('library.')}.portable" for ref in concrete],
            "compiler_disposition": "blocked_typed_gap" if is_gap else "structurally_projected_unqualified",
            "gap_ref": "gap.governance_lineage.repository_port" if is_gap else None,
            "portable_offer": False,
        })
    source["ddd_dossiers"].append(_dossier())

    source["relations"].extend([
        {"relation_id": "relation.governance_lineage.requires_schema", "from_ref": PRODUCT, "predicate": "requires", "to_ref": "product.schema_registry", "binding_phase": "compile_time", "authority_effect": "schema identity and compatibility authority remain external"},
        {"relation_id": "relation.governance_lineage.requires_contract", "from_ref": PRODUCT, "predicate": "requires", "to_ref": "product.data_contract_registry", "binding_phase": "compile_time", "authority_effect": "contract publication and acceptance remain external"},
        {"relation_id": "relation.governance_lineage.requires_policy", "from_ref": PRODUCT, "predicate": "requires", "to_ref": "product.data_use_policy", "binding_phase": "runtime", "authority_effect": "query and disclosure decisions remain external"},
        {"relation_id": "relation.governance_lineage.exchanges_quality", "from_ref": PRODUCT, "predicate": "requires", "to_ref": "product.data_quality_operations", "binding_phase": "runtime", "authority_effect": "lineage paths do not become quality defects or fitness verdicts"},
    ])
    source["negative_tests"].extend([
        {"test_id": "negative.lineage.plan_actual", "input_claim": "A prospective plan proves the runtime inputs and outputs occurred.", "expected_refusal": "retain prospective and observed assertions separately"},
        {"test_id": "negative.lineage.causality", "input_claim": "A derivation edge or reachable path proves causation.", "expected_refusal": "return derivation/path only and require a separate causal design"},
        {"test_id": "negative.lineage.coverage", "input_claim": "No returned path proves no dependency exists.", "expected_refusal": "attach capture and query coverage gaps"},
        {"test_id": "negative.lineage.audit", "input_claim": "An audit log is a complete provenance graph and evidence bundle.", "expected_refusal": "preserve audit provenance and evidence schemas separately"},
        {"test_id": "negative.lineage.integrity_truth", "input_claim": "Matching digest or valid signature proves the assertion true and authoritative.", "expected_refusal": "report scoped integrity only"},
        {"test_id": "negative.lineage.impact", "input_claim": "A downstream path proves observed corruption or business harm.", "expected_refusal": "open possible-impact review"},
        {"test_id": "negative.lineage.correction_delete", "input_claim": "Correcting an assertion deletes the prior history.", "expected_refusal": "publish a new edition linked to retained history"},
        {"test_id": "negative.lineage.model_assertion", "input_claim": "A model- or agent-inferred edge is an accepted lineage fact.", "expected_refusal": "retain proposal taint until deterministic identity semantics coverage and authority checks pass"},
        {"test_id": "negative.lineage.provider_qualification", "input_claim": "Successful event capture qualifies the adapter or graph provider.", "expected_refusal": "require scoped conformance and qualification evidence"},
        {"test_id": "negative.lineage.persistence_retention", "input_claim": "Persisting lineage grants retention disclosure or erasure authority.", "expected_refusal": "obtain an external policy-authority decision"},
    ])
    source["non_collapse_laws"].extend([
        "prospective lineage != observed runtime lineage",
        "logical lineage != physical lineage != runtime lineage != field lineage != formula lineage",
        "derivation or graph path != causation",
        "audit event/log/trail != provenance graph != evidence bundle",
        "identity or digest or signature != truth or authority",
        "possible impact != confirmed impact != executed response",
        "correction != retraction != recall != deletion",
        "model or agent proposal != accepted assertion",
    ])
    return source
