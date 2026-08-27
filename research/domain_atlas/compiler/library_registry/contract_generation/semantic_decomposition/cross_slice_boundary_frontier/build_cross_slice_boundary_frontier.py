#!/usr/bin/env python3
"""Factor cross-slice boundary findings into lossless semantic review quotients."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
RESEARCH = next(parent for parent in HERE.parents if parent.name == "research")
PRODUCT_READINESS = RESEARCH / "product_ontology" / "dossier_readiness" / "product-readiness.jsonl"
AS_OF = "2026-08-27"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


ARCHETYPES = [
    ("privacy_security_safety", "Purpose, confidentiality, privacy, worker/data-subject safety, retention and disclosure controls.", ["privacy", "safety", "sensitive", "security", "disclosure", "retention"]),
    ("authority_policy_decision", "Authority, policy, approval, adjudication, commitment, enforcement and effect permission.", ["authority", "policy", "approval", "commitment", "adjudication", "control", "enforcement", "entitlement", "judgment", "disposition"]),
    ("evidence_receipt_provenance", "Evidence occurrences, receipts, provenance, attestation, certification and traceability.", ["evidence", "receipt", "provenance", "attestation", "certificate", "audit", "trace", "explanation"]),
    ("evaluation_assurance_benchmark", "Evaluation design, benchmarks, tests, appraisal, agreement, calibration, skill and assurance.", ["evaluation", "benchmark", "test", "quality", "calibration", "score", "skill", "diagnostic", "appraisal", "agreement", "leakage", "contamination", "qualification"]),
    ("compatibility_diff_migration", "Compatibility, semantic diff, replay, crosswalk loss, interchange and migration.", ["compatibility", "crosswalk", "diff", "interchange", "migration", "replay", "format-loss", "loss-evaluator", "equivalence"]),
    ("publication_release_delivery", "Publication, immutable release, subscription, delivery and prepared output.", ["publication", "release", "subscription", "delivery", "prepared_output", "prepared-output", "output_edition", "output-edition"]),
    ("federation_reconciliation_coverage", "Federation, reconciliation, freshness, coverage, propagation and multi-source completeness.", ["federation", "federated", "reconciliation", "freshness", "coverage", "propagation", "cross-functional", "cross-temporal"]),
    ("query_retrieval_selection_view", "Query, retrieval, selection, filtering, facets, pagination and interactive views.", ["query", "retrieval", "selection", "filter", "facet", "pagination", "browse", "visibility", "view"]),
    ("relation_mapping_join_topology", "Relations, mappings, joins, hierarchy, topology, graph and cross-resource correspondence.", ["relation", "mapping", "join", "relationship", "hierarchy", "topology", "graph", "crosswalk", "path"]),
    ("model_estimator_algorithm_kernel", "Models, estimators, algorithms, kernels, analyzers, metrics and learned/statistical methods.", ["model", "estimator", "algorithm", "kernel", "analyzer", "metric", "ann_", "ann-", "ranking", "forecast", "proper-score"]),
    ("resource_cost_budget_capacity", "Finite cost, resource, capacity, workload, latency and budget semantics.", ["cost", "resource", "capacity", "workload", "latency", "budget"]),
    ("review_challenge_consensus", "Review, challenge, consensus, appeal, issue handling and human resolution.", ["review", "challenge", "consensus", "appeal", "issue", "defeater", "waiver"]),
    ("state_lifecycle_history_edition", "Edition identity, lifecycle, state transitions, history, branching, lease and supersession.", ["lifecycle", "history", "branch", "lease", "edition", "vintage", "version", "status", "generation"]),
    ("plan_protocol_definition", "Plans, protocols, designs, projects, recipes, requirements and executable definitions.", ["plan", "protocol", "design", "definition", "project", "recipe", "requirement", "scenario", "workspace"]),
    ("schema_representation_shape_profile", "Schemas, representations, shapes, profiles, analyzers, carriers and type constraints.", ["schema", "representation", "shape", "profile", "carrier", "dialect", "format", "lattice", "radiometry", "geometry", "expression"]),
    ("algebra_composition_semantics", "Algebras, composition laws, partiality, missingness, distributions and combining semantics.", ["algebra", "semantics", "partiality", "missingness", "distribution", "combination", "combining", "fusion", "constraint"]),
    ("result_observation_assessment", "Total results, observations, findings, assessments, candidates, verdicts and result pages.", ["result", "observation", "finding", "assessment", "candidate", "verdict", "consensus", "outcome", "page"]),
    ("operation_execution_materialization", "Operations, execution, transformation, materialization, mutation and effect handoff.", ["operation", "execution", "transform", "materialized", "materialization", "mutation", "effect", "correction"]),
    ("subject_occurrence_identity_grain", "Subjects, occurrences, records, identity, populations, cuts, grain and cardinality.", ["identity", "occurrence", "target", "population", "subject", "cut", "record", "grain", "cardinality", "denominator", "issuance"]),
    ("human_role_competence_assignment", "Human roles, competence, appointments, assignments, independence and worker conditions.", ["worker", "competence", "appointment", "assignment", "appraiser", "annotator", "human"]),
    ("domain_specific_composite", "Domain-specific composite seam whose reusable mechanics require local decomposition.", []),
]

ARCHETYPE_BY_ID = {row[0]: row for row in ARCHETYPES}

PRODUCT_CANDIDATES_BY_NAMESPACE = {
    "analytics_image_analysis": ["product.image_analysis_workbench"],
    "analytics_planning": ["product.integrated_planning_workbench"],
    "analytics_dataset_curation": ["product.dataset_curation_workbench"],
    "annotation": ["product.annotation_operations"],
    "assurance": ["product.assurance_case_appraisal"],
    "cbv": ["product.bi_reporting", "product.embedded_analytics"],
    "dataset": ["product.dataset_curation_workbench"],
    "decision": ["product.decision_automation"],
    "discovery": ["product.metadata_discovery"],
    "entity_resolution": ["product.entity_resolution"],
    "forecast": ["product.forecasting_workbench"],
    "graph": ["product.ontology_knowledge_model", "product.graph_analysis_workbench"],
    "image": ["product.image_analysis_workbench"],
    "inspection": ["product.visual_inspection_operations"],
    "master_data": ["product.master_data_governance"],
    "method_kernels": [],
    "planning": ["product.integrated_planning_workbench"],
    "preparation": ["product.self_service_data_preparation"],
    "qck": ["product.query_execution_service", "product.managed_warehouse_experience"],
    "qor": ["product.data_quality_operations", "product.reconciliation_control_operations"],
    "reference_data": ["product.reference_data_governance"],
    "search": ["product.search_index_service"],
    "smf": ["product.semantic_metric_formula_service"],
}

NAMESPACE_BOUNDARY_PRIORS = {
    "analytics_image_analysis": ("MULTIPLE_CONTEXTS_WITHIN_ONE_RETAINED_PRODUCT_CANDIDATE", "Image Analysis is retained as a product while project/input, workspace/coordinates, regions, recipes/provider binding, runs/results, comparison/replay and publication remain exact internal seams with imported image, method and vertical authorities.", {
        "project_input": ["project_definition", "image_occurrence_admission"],
        "workspace_coordinates": ["workspace_layer_graph", "coordinate_profile_binding"],
        "region_object": ["region_object_topology"],
        "recipe_method_binding": ["analysis_recipe", "method_capability_binding"],
        "run_results": ["analysis_run_attempt", "derived_layer_result", "object_segmentation_result", "measurement_feature_result"],
        "comparison_replay": ["result_comparison_review", "provenance_replay_history"],
        "publication": ["evidence_publication_export"],
    }),
    "analytics_dataset_curation": ("MULTIPLE_CONTEXTS_WITHIN_ONE_RETAINED_PRODUCT_CANDIDATE", "Dataset Curation is retained as a product while definition/membership, selection/derivation, duplicate/coverage, split/audit, annotation/rights, profile/documentation, edition and release remain exact internal seams with imported owners.", {
        "definition_membership": ["dataset_definition_purpose", "source_occurrence_admission_membership"],
        "selection_derivation": ["inclusion_exclusion_selection", "curation_recipe_derivation"],
        "duplicate_coverage": ["duplicate_evidence_adjudication", "cohort_balance_coverage_assessment"],
        "partition_audit": ["partition_split_assignment", "leakage_contamination_audit"],
        "annotation_rights": ["annotation_reference_binding", "rights_use_policy_manifest"],
        "profile_documentation": ["dataset_profile_statistics", "documentation_metadata_projection"],
        "edition_release": ["immutable_dataset_edition_manifest", "release_maintenance_recall"],
    }),
    "analytics_planning": ("MULTIPLE_CONTEXTS_WITHIN_ONE_RETAINED_PRODUCT_CANDIDATE", "Integrated planning is retained as a product, while definition/scenario, alternatives/feasibility, reconciliation/comparison, authority/publication, variance/cycle and vertical translation remain exact internal seams with imported owners.", {
        "definition_scenario": ["plan_definition_edition", "scenario_assumption_contract"],
        "alternative_feasibility": ["plan_alternative_algebra", "objective_constraint_resource_binding", "hierarchy_allocation_disaggregation", "feasibility_assessment"],
        "reconciliation_comparison": ["cross_functional_reconciliation", "alternative_comparison_selection"],
        "authority_publication": ["review_consensus_approval_commitment", "plan_publication_release"],
        "variance_cycle": ["plan_variance_replan", "planning_cycle_calendar"],
        "vertical_vocabulary_acl": ["vertical_vocabulary_acl"],
    }),
    "annotation": ("MULTIPLE_CONTEXTS_WITHIN_ONE_PRODUCT_CANDIDATE", "Project language, work assignment, annotation occurrence, review/adjudication and accepted-reference lifecycle change independently.", {
        "project_language": ["project-definition", "schema-constraint-algebra", "instruction-example-edition", "privacy-worker-safety-profile"],
        "work_population_assignment": ["target-occurrence-binding", "task-sampling-design", "worker-competence-profile", "assignment-lease"],
        "annotation_occurrence": ["occurrence-algebra", "modality-shape-algebra"],
        "review_consensus_adjudication": ["review-plan", "agreement-applicability", "annotator-model-estimator", "consensus-result-algebra", "adjudication-authority"],
        "accepted_reference_interchange": ["reference-edition-lifecycle", "format-loss-crosswalk"],
    }),
    "assurance": ("MULTIPLE_CONTEXTS_WITHIN_ONE_PRODUCT_CANDIDATE", "Argument, appraisal governance, performed evidence work, findings/challenges and bounded verdict/reliance have different authority and lifecycle boundaries.", {
        "argument_defeater": ["argument_graph", "defeater_graph"],
        "appraisal_governance": ["appraisal_plan", "appraisal_policy", "appraiser_appointment"],
        "evidence_and_performed_work": ["evidence_admission", "evidence_quality_vector", "performed_work"],
        "finding_and_challenge": ["finding", "challenge"],
        "verdict_lifecycle_and_reliance_acl": ["bounded_verdict", "verdict_lifecycle", "reliance_handoff"],
    }),
    "cbv": ("CROSS_PRODUCT_AND_ACL_SPLIT_CANDIDATE", "BI report semantics, interaction state, visual communication and embedded entitlement span BI Reporting and Embedded Analytics and must not share authority implicitly.", {
        "report_identity_authoring": ["dashboard-report-artifact-identity", "report-authoring-lifecycle"],
        "interaction_history": ["interaction-history-provenance"],
        "visual_communication": ["visualization-task-abstraction", "scale-guide-contract", "accessibility-equivalence-evidence", "uncertainty-communication"],
        "embedded_entitlement_acl": ["embedded-entitlement-contract"],
    }),
    "dataset": ("LEGACY_NAMESPACE_FOR_RETAINED_DATASET_CURATION_PRODUCT", "The older dataset namespace routes to the retained Dataset Curation product; its coarse seams are superseded by analytics_dataset_curation exact contracts and must not create a second product.", {
        "curation_plan": ["curation-plan"], "release_lifecycle": ["edition-release"], "leakage_contamination_assurance": ["leakage-contamination-audit"],
    }),
    "decision": ("MULTIPLE_CONTEXTS_WITH_AUTHORITY_ACL_CANDIDATE", "Decision definition, policy evaluation, testing/trace and proposal/authority handoff must not collapse result into authorization or effect.", {
        "decision_model_definition": ["requirement_graph", "expression_profile", "table_analyzer", "semantic_diff"],
        "policy_and_evaluation": ["combining_algebra", "policy_applicability", "total_evaluation_result"],
        "test_and_trace": ["test_corpus", "trace"],
        "proposal_and_authority_acl": ["action_proposal_contract", "authority_handoff"],
    }),
    "discovery": ("KNOWN_MULTI_CONTEXT_PRODUCT_CANDIDATE", "Acquisition, catalog assertions/projections, federation and freshness/coverage already expose distinct source, write-model and inter-catalog lifecycles.", {
        "acquisition": ["acquisition_occurrence"], "catalog_assertion_projection": ["assertion_value", "projection_edition"],
        "federation": ["federated_result"], "freshness_coverage": ["freshness_coverage_ledger"],
    }),
    "entity_resolution": ("MULTIPLE_CONTEXTS_WITHIN_ONE_PRODUCT_CANDIDATE", "Population/record identity, normalization/features, blocking, pair assessment, clustering, evaluation/reconciliation and privacy are distinct decision loci.", {
        "population_and_record": ["population_contract", "record_occurrence"],
        "normalization_feature_constraint": ["normalization_profile", "comparison_feature_algebra", "constraint_profile"],
        "blocking_and_candidates": ["blocking_plan", "candidate_set_receipt"],
        "pair_assessment": ["pair_assessment", "linkage_uncertainty_bundle"],
        "cluster_lifecycle": ["cluster_formation_policy", "cluster_edition"],
        "evaluation_reconciliation": ["evaluation_design", "incremental_reconciliation"],
        "privacy_profile": ["privacy_preserving_profile"],
    }),
    "forecast": ("MULTIPLE_CONTEXTS_WITHIN_ONE_PRODUCT_CANDIDATE", "Forecast information cuts, artifacts/distributions, evaluation, reconciliation/combination and judgment evidence have separable semantics and cadence.", {
        "target_origin_realization": ["target-observation-contract", "origin-horizon-information-cut", "realization-vintage-join"],
        "artifact_distribution": ["artifact-distribution-algebra", "intermittent-demand-profile"],
        "evaluation_calibration": ["baseline-skill-comparison", "proper-score-calibration", "temporal-evaluation-design"],
        "reconciliation_combination": ["cross-temporal-reconciliation", "probabilistic-reconciliation", "combination-ensemble"],
        "judgment_and_value_added": ["judgment-evidence-protocol", "value-added-analysis"],
    }),
    "graph": ("CROSS_PRODUCT_NAMESPACE_SPLIT_CANDIDATE", "Ontology/knowledge-model ownership and graph-analysis workspace/algorithm/result lifecycle are independently adoptable products joined through explicit graph/profile ACLs.", {
        "ontology_profile_projection": ["model-mapping-acl", "semantic-profile-contract", "projection-contract", "assertion-status-provenance"],
        "graph_algebra_and_occurrence": ["dynamic-temporal-algebra", "hypergraph-algebra", "occurrence-snapshot-identity"],
        "graph_analysis_workbench": ["algorithm-plan", "analysis-workspace-lifecycle", "benchmark-workload-identity", "result-evidence-receipt"],
    }),
    "image": ("LEGACY_NAMESPACE_FOR_RETAINED_IMAGE_ANALYSIS_PRODUCT", "The older image namespace routes to retained Image Analysis; its carrier/method vacancies remain imported or are superseded by analytics_image_analysis workbench contracts and must not create another product.", {
        "carrier_radiometry_geometry": ["occurrence-carrier-profile", "radiometry-color-profile", "geometry-camera-model", "sample-lattice-algebra"],
        "region_and_registration": ["region-label-topology", "registration-transform-result"],
        "analysis_and_evaluation": ["analysis-plan", "analysis-result-evidence", "benchmark-evaluation-profile"],
    }),
    "inspection": ("MULTIPLE_CONTEXTS_WITH_EFFECT_ACL_CANDIDATE", "Inspection target/acquisition, plan/qualification/reference, results/review, external effects and vertical vocabulary have distinct authorities.", {
        "target_and_acquisition": ["target-occurrence-binding", "acquisition-synchronization-profile"],
        "plan_recipe_reference": ["plan-definition", "recipe-qualification", "reference-golden-profile"],
        "result_and_review": ["result-algebra", "review-disposition"],
        "effect_acl": ["effect-handoff"], "vertical_vocabulary_acl": ["vertical-defect-vocabulary-acl"],
    }),
    "master_data": ("NEW_PRODUCT_MULTI_CONTEXT_CANDIDATE", "Master identity issuance/hierarchy and provenance/change propagation are governance lifecycles distinct from entity resolution and reference values.", {
        "identity_and_hierarchy": ["identifier_issuance_receipt", "relationship_hierarchy_edition"],
        "provenance_and_propagation": ["field_provenance_projection", "change_propagation_receipt"],
    }),
    "method_kernels": ("SHARED_METHOD_FAMILY_NOT_PRODUCT_CONTEXT_CANDIDATE", "Study specification, missingness/sampling and estimators/diagnostics/evidence are reusable formal methods, not one product-owned lifecycle.", {
        "study_and_reproducibility": ["estimand_analysis_specification", "sampling_design_semantics", "missing_data_semantics", "reproducible_analysis_spec"],
        "estimation_diagnostics_evidence": ["robust_nonparametric_estimators", "model_diagnostics", "multiplicity_sequential_evidence", "evidence_synthesis"],
    }),
    "planning": ("NEW_PRODUCT_MULTI_CONTEXT_CANDIDATE", "Scenario/objective definition, alternatives/commitment, reconciliation/replan and vertical vocabulary form a missing integrated-planning product with ACLs.", {
        "scenario_objective_policy": ["scenario-assumption-contract", "objective-constraint-policy-binding"],
        "alternatives_and_commitment": ["plan-alternative-algebra", "consensus-approval-commitment"],
        "reconciliation_and_replan": ["cross-functional-reconciliation", "plan-variance-replan"],
        "vertical_vocabulary_acl": ["vertical-vocabulary-acl"],
    }),
    "preparation": ("MULTIPLE_CONTEXTS_WITHIN_ONE_PRODUCT_CANDIDATE", "Admission/schema/profile, transformation recipe, interactive preview/repair, history/compatibility and secured output have different state and effect boundaries.", {
        "admission_schema_identity": ["data_cut_admission", "dialect_parse_plan", "schema_hypothesis", "occurrence_identity_map"],
        "profiling_missingness": ["profile_request", "profile_result", "missingness_algebra"],
        "recipe_transformation": ["expression_binding", "join_cardinality_contract", "operation_algebra", "reshape_grain_map", "recipe_edition"],
        "interactive_view_preview_repair": ["selection_view", "preview_contract", "repair_proposal", "total_parse_result"],
        "history_and_compatibility": ["history_branch", "replay_compatibility", "data_diff"],
        "prepared_output_security": ["prepared_output_edition", "sensitive_value_view"],
    }),
    "qck": ("CROSS_PRODUCT_AND_LAYER_SPLIT_CANDIDATE", "Query semantics/OLAP, transaction/view equivalence, federation, runtime benchmarks and carrier ACLs span query-engine and managed-warehouse promises.", {
        "query_session_result_evidence": ["session-context-semantics", "result-determinism-contract", "query-evidence-contract"],
        "olap_and_summarizability": ["multidimensional-olap-semantics", "summarizability-contracts"],
        "transaction_and_view_equivalence": ["transaction-snapshot-binding", "materialized-view-equivalence"],
        "federation_residual": ["federation-residual-algebra"], "workload_benchmark": ["workload-benchmark-contract"],
        "carrier_interchange_acl": ["carrier-interchange-acl"],
    }),
    "qor": ("CROSS_PRODUCT_NAMESPACE_SPLIT_CANDIDATE", "Quality evaluation/certification and reconciliation truth/match/control/correction belong to the already-separated Data Quality and Reconciliation products.", {
        "quality_evaluation_and_certification": ["quality-subject-cut-identity", "population-denominator-algebra", "validation-outcome-algebra", "enforcement-disposition-algebra", "certificate-status-revocation", "quality-cost-loss-profile"],
        "reconciliation_control_and_correction": ["truth-role-algebra", "tolerant-match-algebra", "control-occurrence-receipt", "correction-authority-effect-contract"],
    }),
    "reference_data": ("NEW_PRODUCT_MULTI_CONTEXT_CANDIDATE", "Concept/value-set lifecycle, mapping/crosswalk loss and publication/subscription form reference-data governance distinct from master identity.", {
        "concept_and_value_set": ["concept_code_designation_algebra", "value_set_expansion"],
        "mapping_and_crosswalk": ["mapping_relation_algebra", "crosswalk_loss_evaluator"],
        "publication_subscription": ["publication_subscription"],
    }),
    "search": ("MULTIPLE_CONTEXTS_WITHIN_ONE_PRODUCT_CANDIDATE", "Content/index, mutation/visibility, retrieval/ranking, results, evaluation and access/evolution change independently within Search & Index Serving.", {
        "content_index_analysis": ["content_admission", "index_schema", "analysis_chain", "indexed_occurrence"],
        "mutation_visibility_deletion": ["mutation_generation", "visibility_cut", "deletion_verification"],
        "query_retrieval_ranking": ["query_contract", "retrieval_ir", "lexical_kernel", "structured_filter", "ann_contract", "vector_metric_profile", "hybrid_fusion", "ranking_profile"],
        "result_pagination_explanation": ["result_page", "pagination_cursor", "explanation"],
        "evaluation_relevance_approximation": ["evaluation_corpus", "relevance_judgment", "approximation_receipt"],
        "access_and_evolution": ["access_disclosure", "semantic_diff"],
    }),
    "smf": ("SMALL_PRODUCT_LANGUAGE_WITH_INTERNAL_SEAMS_CANDIDATE", "Metric definition/grain/join semantics and observation receipts belong to one service language but have distinct definition and evidence loci.", {
        "metric_definition_grain_join": ["metric-definition-contract", "analytical-grain-population", "semantic-join-path"],
        "metric_observation_evidence": ["metric-observation-receipt"],
    }),
}

# These are reversible priority-zero boundary proposals, not canonical product or owner decisions.
# The keys must exactly cover the subcontexts of the five P0 review packages (six namespaces).
P0_SUBCONTEXT_DISPOSITION_PRIORS = {
    "cbv": {
        "report_identity_authoring": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.bi_reporting"], [], "BI Reporting owns report identity and authoring lifecycle; embedding consumes an editioned artifact."),
        "interaction_history": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.bi_reporting"], ["product.embedded_analytics"], "Interaction history is evidence about a report experience, not embedded-host authorization."),
        "visual_communication": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.bi_reporting"], ["product.embedded_analytics"], "Visualization, accessibility and uncertainty communication remain presentation semantics reusable by embedded delivery."),
        "embedded_entitlement_acl": ("ACL_CONTEXT_IN_CONSUMER_PRODUCT_CANDIDATE", ["product.embedded_analytics"], [], "Embedded Analytics owns host/tenant entitlement translation and must not silently confer BI report authority."),
    },
    "discovery": {
        "acquisition": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.metadata_discovery"], [], "Acquisition records source observations without becoming catalog assertion truth."),
        "catalog_assertion_projection": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.metadata_discovery"], [], "Catalog assertions and projections share the discovery product but retain write/read-model lifecycles."),
        "federation": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.metadata_discovery"], [], "Federation combines catalog responses while preserving source identity and residual uncertainty."),
        "freshness_coverage": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.metadata_discovery"], [], "Freshness and coverage are evidence over acquisition and federation, not source truth."),
    },
    "graph": {
        "ontology_profile_projection": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.ontology_knowledge_model"], ["product.graph_analysis_workbench"], "Ontology/profile projection remains governed model meaning imported by graph analysis."),
        "graph_algebra_and_occurrence": ("OWNED_CONTEXT_IN_NEW_PRODUCT_CANDIDATE", ["product.graph_analysis_workbench"], [], "Graph occurrence, temporal and hypergraph algebra define analysis input semantics, not ontology governance."),
        "graph_analysis_workbench": ("OWNED_CONTEXT_IN_NEW_PRODUCT_CANDIDATE", ["product.graph_analysis_workbench"], [], "Algorithm plans, workspaces, benchmarks and result evidence form the independently adoptable graph-analysis lifecycle."),
    },
    "method_kernels": {
        "study_and_reproducibility": ("SHARED_METHOD_CONTEXT_NO_PRODUCT_OWNER_CANDIDATE", [], [], "Estimand, sampling, missingness and reproducibility are imported formal-method semantics rather than a product lifecycle."),
        "estimation_diagnostics_evidence": ("SHARED_METHOD_CONTEXT_NO_PRODUCT_OWNER_CANDIDATE", [], [], "Estimators, diagnostics and evidence synthesis are independently reusable method kernels with local applicability profiles."),
    },
    "qck": {
        "query_session_result_evidence": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.query_execution_service"], ["product.managed_warehouse_experience"], "Session, result determinism and execution evidence are query-service semantics consumed by a warehouse experience."),
        "olap_and_summarizability": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.query_execution_service"], ["product.managed_warehouse_experience"], "OLAP and summarizability are analytical query semantics, not managed-environment semantics."),
        "transaction_and_view_equivalence": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.query_execution_service"], ["product.managed_warehouse_experience"], "Snapshot binding and view equivalence are query correctness contracts imported by the warehouse experience."),
        "federation_residual": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.query_execution_service"], ["product.managed_warehouse_experience"], "Federation residuals state what must execute after safe pushdown and remain query-planning semantics."),
        "workload_benchmark": ("ASSURANCE_CONTEXT_OWNED_BY_QUERY_PRODUCT_CANDIDATE", ["product.query_execution_service"], ["product.managed_warehouse_experience"], "Workload benchmarks qualify query behavior; service-level workload management consumes but does not redefine them."),
        "carrier_interchange_acl": ("CROSS_LAYER_ACL_OWNED_BY_QUERY_PRODUCT_CANDIDATE", ["product.query_execution_service"], ["product.managed_warehouse_experience"], "Carrier interchange translates query values at storage/runtime borders; the managed warehouse is a downstream consumer, not semantic owner."),
    },
    "qor": {
        "quality_evaluation_and_certification": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.data_quality_operations"], ["product.reconciliation_control_operations"], "Quality evaluation and revocable certification concern fitness of a subject cut, not reconciliation break closure."),
        "reconciliation_control_and_correction": ("OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", ["product.reconciliation_control_operations"], ["product.data_quality_operations"], "Truth-role binding, tolerant matching, control occurrence and correction authority form the reconciliation lifecycle."),
    },
}

P0_RELATION_PRIORS = {
    "cbv": [
        ("embedded_consumes_report_contract", "product.embedded_analytics", "product.bi_reporting", "CUSTOMER_SUPPLIER_WITH_ACL", ["report_identity_authoring", "visual_communication", "embedded_entitlement_acl"]),
    ],
    "discovery": [
        ("acquisition_feeds_assertion_projection", "candidate.subcontext.discovery.acquisition", "candidate.subcontext.discovery.catalog_assertion_projection", "PUBLISHED_LANGUAGE", ["acquisition", "catalog_assertion_projection"]),
        ("federation_preserves_freshness_coverage", "candidate.subcontext.discovery.federation", "candidate.subcontext.discovery.freshness_coverage", "EVIDENCE_HANDOFF", ["federation", "freshness_coverage"]),
    ],
    "graph": [
        ("analysis_imports_ontology_profile", "product.graph_analysis_workbench", "product.ontology_knowledge_model", "CUSTOMER_SUPPLIER_WITH_ACL", ["ontology_profile_projection", "graph_algebra_and_occurrence"]),
    ],
    "method_kernels": [],
    "qck": [
        ("warehouse_imports_query_service", "product.managed_warehouse_experience", "product.query_execution_service", "CUSTOMER_SUPPLIER_WITH_ACL", ["query_session_result_evidence", "olap_and_summarizability", "transaction_and_view_equivalence", "federation_residual", "workload_benchmark"]),
        ("query_translates_carriers", "candidate.subcontext.qck.carrier_interchange_acl", "external.storage_and_runtime_carriers", "ANTI_CORRUPTION_LAYER", ["carrier_interchange_acl"]),
    ],
    "qor": [
        ("reconciliation_imports_quality_evidence", "product.reconciliation_control_operations", "product.data_quality_operations", "PUBLISHED_LANGUAGE_WITHOUT_AUTHORITY_TRANSFER", ["quality_evaluation_and_certification", "reconciliation_control_and_correction"]),
    ],
}

TOKEN_WORD_STOP = {
    "library", "candidate", "context", "compiler", "which", "what", "when", "where", "whose", "with",
    "from", "into", "must", "need", "needs", "require", "requires", "define",
}


def word_tokens(value: Any) -> set[str]:
    return {
        token for token in re.split(r"[^a-z0-9]+", str(value).lower())
        if len(token) >= 4 and token not in TOKEN_WORD_STOP
    }


def all_findings() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(SEM.glob("*_semantic_slice/product-capability-boundary-findings.jsonl")):
        for source_row in load_jsonl(path):
            row = dict(source_row)
            row["source_slice"] = path.parent.name
            row["source_artifact"] = str(path.relative_to(SEM))
            rows.append(row)
    return sorted(rows, key=lambda r: (r["source_slice"], r["finding_id"]))


def normalize_text(value: Any) -> str:
    return str(value).lower().replace("_", "-")


def archetype_scores(row: dict[str, Any]) -> dict[str, int]:
    """Score the proposed seam itself more heavily than explanatory prose.

    Findings often mention policy, evidence, or results while proposing a more
    specific lifecycle, execution, identity, or human-role seam.  A flat
    substring match therefore creates a precedence artifact.  Weighted fields
    retain the multidimensional matches but make the exact proposed identity the
    primary signal.
    """
    weighted_fields = [
        (normalize_text(row.get("proposed_library_ref", "")), 8),
        (normalize_text(row.get("candidate_disposition", "")), 4),
        (normalize_text(row.get("finding", "")), 2),
        (normalize_text(row.get("reason", "")), 1),
    ]
    scores: dict[str, int] = {}
    for aid, _, terms in ARCHETYPES[:-1]:
        score = sum(weight for text, weight in weighted_fields for term in terms if term.replace("_", "-") in text)
        if score:
            scores[aid] = score
    return scores


def matching_archetypes(row: dict[str, Any]) -> list[str]:
    matches = set(archetype_scores(row))
    return [aid for aid in PRIMARY_PRECEDENCE if aid in matches] or ["domain_specific_composite"]


PRIMARY_PRECEDENCE = [row[0] for row in ARCHETYPES]


def primary_archetype(row: dict[str, Any]) -> str:
    scores = archetype_scores(row)
    if not scores:
        return "domain_specific_composite"
    precedence = {aid: index for index, aid in enumerate(PRIMARY_PRECEDENCE)}
    return min(scores, key=lambda aid: (-scores[aid], precedence[aid]))


def vacancy_routes(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for finding in findings:
        if finding.get("candidate_disposition") != "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED":
            continue
        matches = matching_archetypes(finding)
        rows.append({
            "route_id": "route.cross_slice." + finding["proposed_library_ref"].replace("library.", "").replace(".", "-").replace("_", "-"),
            "proposed_library_ref": finding["proposed_library_ref"],
            "source_finding_ref": finding["finding_id"],
            "source_slice": finding["source_slice"],
            "primary_archetype_ref": "archetype.boundary." + primary_archetype(finding),
            "secondary_archetype_refs": sorted("archetype.boundary." + aid for aid in matches if aid != primary_archetype(finding)),
            "namespace": finding["proposed_library_ref"].split(".")[1],
            "local_residual_required": True,
            "semantic_equivalence_claim": False,
            "merge_authorized": False,
            "owner_candidate": "UNASSIGNED",
            "ratification_state": "UNRATIFIED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return sorted(rows, key=lambda r: r["proposed_library_ref"])


def archetype_rows(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_primary: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in routes:
        by_primary[row["primary_archetype_ref"].split(".")[-1]].append(row)
    result = []
    for aid, definition, _ in ARCHETYPES:
        members = by_primary.get(aid, [])
        result.append({
            "archetype_ref": "archetype.boundary." + aid,
            "definition": definition,
            "member_count": len(members),
            "member_library_refs": sorted(row["proposed_library_ref"] for row in members),
            "review_law": "The archetype shares review mechanics only. Every member keeps exact identity, domain vocabulary, owner, applicability, local invariants, API and acceptance residuals.",
            "inheritance_law": "An archetype decision may be proposed as a default but cannot flow to a member without explicit applicability and owner ratification.",
            "merge_law": "Common suffixes, structures or review methods never authorize library merge or cross-domain type unification.",
            "owner_decision": "UNRATIFIED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return result


def semantic_modules_by_slice() -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(SEM.glob("*_semantic_slice/semantic-modules.jsonl")):
        result[path.parent.name] = load_jsonl(path)
    return result


def existing_design_contexts() -> list[dict[str, Any]]:
    path = SEM.parent.parent / "library-design-contexts.jsonl"
    return load_jsonl(path) if path.exists() else []


def ranked_module_candidates(
    finding: dict[str, Any], modules: list[dict[str, Any]], limit: int = 3,
) -> list[dict[str, Any]]:
    ref_tokens = word_tokens(finding["proposed_library_ref"])
    finding_tokens = word_tokens(finding.get("finding", finding.get("reason", "")))
    scored = []
    for module in modules:
        module_id_tokens = word_tokens(module.get("module_id", ""))
        module_semantic_tokens = word_tokens(
            " ".join([
                module.get("owned_semantic_object", ""),
                module.get("sovereign_question", ""), module.get("owned_question", ""),
                module.get("formalism", ""),
            ])
        )
        module_tokens = module_id_tokens | module_semantic_tokens
        exact_id_overlap = ref_tokens & module_id_tokens
        semantic_overlap = ref_tokens & module_semantic_tokens
        prose_overlap = finding_tokens & module_tokens
        score = 10 * len(exact_id_overlap) + 4 * len(semantic_overlap) + len(prose_overlap)
        if score:
            scored.append({
                "semantic_module_ref": module["module_id"],
                "score": score,
                "exact_module_id_token_overlap": sorted(exact_id_overlap),
                "semantic_text_token_overlap": sorted(semantic_overlap),
                "finding_token_overlap": sorted(prose_overlap),
                "owned_semantic_object": module.get("owned_semantic_object"),
                "source_refs": sorted(module.get("source_refs", [])),
            })
    return sorted(scored, key=lambda row: (-row["score"], row["semantic_module_ref"]))[:limit]


def existing_context_counterfactuals(
    proposed_library_ref: str, contexts: list[dict[str, Any]], limit: int = 5,
) -> list[dict[str, Any]]:
    namespace = proposed_library_ref.split(".")[1]
    namespace_tokens = word_tokens(namespace)
    ref_tokens = word_tokens(proposed_library_ref) - namespace_tokens
    scored = []
    for context in contexts:
        context_text = " ".join([context.get("context_id", ""), *context.get("library_refs", [])])
        context_tokens = word_tokens(context_text) - namespace_tokens
        overlap = ref_tokens & context_tokens
        if not overlap:
            continue
        score = 4 * len(overlap) + (1 if namespace in context_text.lower() else 0)
        scored.append({
            "context_ref": context["context_id"],
            "semantic_owner_ref": context.get("semantic_owner_ref"),
            "score": score,
            "specific_token_overlap": sorted(overlap),
            "counterfactual_only": True,
        })
    return sorted(scored, key=lambda row: (-row["score"], row["context_ref"]))[:limit]


def owner_candidate_dockets(
    findings: list[dict[str, Any]], routes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    finding_by_ref = {row["finding_id"]: row for row in findings}
    modules_by_slice = semantic_modules_by_slice()
    contexts = existing_design_contexts()
    rows = []
    for route in routes:
        finding = finding_by_ref[route["source_finding_ref"]]
        modules = ranked_module_candidates(finding, modules_by_slice.get(route["source_slice"], []))
        exact_seam_suffix = route["proposed_library_ref"].split(".", 2)[-1]
        local_context = "context.candidate." + route["namespace"] + "." + exact_seam_suffix.replace("-", "_")
        rows.append({
            "docket_id": "docket.owner." + route["route_id"].split("route.cross_slice.", 1)[-1],
            "proposed_library_ref": route["proposed_library_ref"],
            "source_finding_ref": route["source_finding_ref"],
            "source_slice": route["source_slice"],
            "namespace": route["namespace"],
            "primary_archetype_ref": route["primary_archetype_ref"],
            "secondary_archetype_refs": route["secondary_archetype_refs"],
            "local_context_candidate_ref": local_context,
            "local_context_candidate_grain": "EXACT_SEAM_OWNER_LOCUS_NOT_PROVEN_BOUNDED_CONTEXT",
            "semantic_module_candidates": modules,
            "semantic_module_grounding_gap": not bool(modules),
            "product_context_candidate_refs": PRODUCT_CANDIDATES_BY_NAMESPACE[route["namespace"]],
            "existing_context_counterfactuals": existing_context_counterfactuals(route["proposed_library_ref"], contexts),
            "shared_mechanic_counterfactual_ref": "context.candidate.shared." + route["primary_archetype_ref"].split(".")[-1],
            "admissible_dispositions": [
                "RATIFY_LOCAL_CONTEXT_OWNER", "IMPORT_EXISTING_CONTEXT_OWNER",
                "RATIFY_SHARED_MECHANIC_OWNER_WITH_LOCAL_PROFILE", "MERGE_INTO_EXISTING_LIBRARY",
                "SPLIT_PROPOSED_SEAM", "REJECT_LIBRARY_BOUNDARY",
            ],
            "required_counterfactual_tests": [
                "ubiquitous_language_substitution", "independent_adoption_and_release",
                "invariant_and_state_machine_cohesion", "authority_and_effect_boundary",
                "change_cadence_and_compatibility", "two_unrelated_verticals",
            ],
            "selection_state": "OPEN_NO_OWNER_SELECTED",
            "owner_ratified": False,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return sorted(rows, key=lambda row: row["proposed_library_ref"])


def owner_context_rows(dockets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in dockets:
        members[row["local_context_candidate_ref"]].append(row)
    return [{
        "context_candidate_ref": context_ref,
        "member_library_refs": sorted(row["proposed_library_ref"] for row in rows),
        "member_count": len(rows),
        "semantic_module_candidate_refs": sorted({
            module["semantic_module_ref"] for row in rows for module in row["semantic_module_candidates"]
        }),
        "product_context_candidate_refs": sorted({
            ref for row in rows for ref in row["product_context_candidate_refs"]
        }),
        "context_boundary_state": "CANDIDATE_UNRATIFIED",
        "cohesion_not_proven": True,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    } for context_ref, rows in sorted(members.items())]


def type_name_seed(library_ref: str) -> str:
    words = re.split(r"[._-]+", library_ref.split(".", 2)[-1])
    return "".join(word[:1].upper() + word[1:] for word in words if word) + "Contract"


def provisional_contract_dockets(
    routes: list[dict[str, Any]], owner_dockets: list[dict[str, Any]],
    collision_dockets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    owner_by_library = {row["proposed_library_ref"]: row for row in owner_dockets}
    collisions_by_library: dict[str, list[str]] = defaultdict(list)
    for row in collision_dockets:
        for library_ref in row["candidate_library_refs"]:
            collisions_by_library[library_ref].append(row["docket_id"])
    rows = []
    for route in routes:
        library_ref = route["proposed_library_ref"]
        owner = owner_by_library[library_ref]
        archetype = route["primary_archetype_ref"].split(".")[-1]
        rows.append({
            "docket_id": "docket.contract_lowering." + route["route_id"].split("route.cross_slice.", 1)[-1],
            "candidate_library_ref": library_ref,
            "source_finding_ref": route["source_finding_ref"],
            "owner_docket_ref": owner["docket_id"],
            "semantic_module_candidate_refs": [
                row["semantic_module_ref"] for row in owner["semantic_module_candidates"]
            ],
            "collision_docket_refs": sorted(collisions_by_library[library_ref]),
            "primary_archetype_ref": route["primary_archetype_ref"],
            "candidate_ir_family": IR_FAMILY_BY_ARCHETYPE[archetype],
            "non_authoritative_type_name_seed": type_name_seed(library_ref),
            "required_contract_facets": [{
                "facet_ref": "contract_facet." + facet,
                "state": "REQUIRED_UNRESOLVED",
            } for facet in CONTRACT_FACETS],
            "lowering_dependencies": [
                "VERIFIED_SOURCE_FINDING", "RATIFIED_SEMANTIC_OWNER",
                "RATIFIED_PRODUCT_BOUNDARY", "RATIFIED_LIBRARY_BOUNDARY",
                "RESOLVED_COLLISION_DISPOSITIONS", "EXACT_CONTRACT_AUTHORITY_RECEIPT",
            ],
            "lowering_stages": [
                "normalize_exact_intent", "resolve_owner_and_applicability",
                "select_exact_contract_edition", "typecheck_subject_grain_time_authority",
                "check_algebra_effect_resource_and_evidence_laws", "match_qualified_offer",
                "emit_target_plan_and_proof_obligations",
            ],
            "typed_refusals": [
                "CANDIDATE_NOT_CANONICAL", "OWNER_UNRATIFIED", "PRODUCT_BOUNDARY_UNRATIFIED",
                "LIBRARY_BOUNDARY_UNRATIFIED", "COLLISION_UNRESOLVED", "EXACT_CONTRACT_UNSELECTED",
                "CONTRACT_FACETS_INCOMPLETE", "QUALIFIED_IMPLEMENTATION_MISSING",
                "TWO_VERTICAL_ACCEPTANCE_MISSING",
            ],
            "contract_selection_state": "WITHHELD_CANDIDATE_NOT_CANONICAL",
            "compiler_lowering_state": "REFUSED_UPSTREAM_RATIFICATION_MISSING",
            "exact_contract_selected": False,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return sorted(rows, key=lambda row: row["candidate_library_ref"])


def contract_lowering_archetypes(dockets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_archetype: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in dockets:
        by_archetype[row["primary_archetype_ref"]].append(row)
    return [{
        "contract_lowering_archetype_ref": "contract_lowering." + archetype_ref.split(".")[-1],
        "semantic_archetype_ref": archetype_ref,
        "candidate_ir_family": rows[0]["candidate_ir_family"],
        "docket_count": len(rows),
        "contract_docket_refs": sorted(row["docket_id"] for row in rows),
        "required_contract_facet_refs": ["contract_facet." + facet for facet in CONTRACT_FACETS],
        "inheritance_law": "The archetype supplies a required review shape only; every exact type, law, refusal, operation, owner and API remains member-local until ratified.",
        "state": "PROVISIONAL_UNRATIFIED",
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    } for archetype_ref, rows in sorted(by_archetype.items())]


def p5_intake_routes(contract_dockets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "intake_route_id": "route.p5_intake." + row["docket_id"].split("docket.contract_lowering.", 1)[-1],
        "candidate_library_ref": row["candidate_library_ref"],
        "provisional_contract_docket_ref": row["docket_id"],
        "target_program_ref": "program.p5_exact_contract_adjudication",
        "current_disposition": "WITHHELD_CANDIDATE_NOT_CANONICAL",
        "promotion_inputs": [
            "ratified_product_and_library_boundary_receipt", "ratified_semantic_owner_receipt",
            "canonical_library_identity_or_replacement_mapping", "resolved_collision_receipts",
            "applicability_and_local_residual_matrix",
        ],
        "promotion_outputs": [
            "canonical_exact_gap_ref", "authority_symbol_templates", "exact_contract_docket",
            "compiler_binding_docket", "implementation_qualification_scope",
        ],
        "name_join_forbidden": True,
        "automatic_canonical_mutation_forbidden": True,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    } for row in contract_dockets]


def execution_frontier(
    packages: list[dict[str, Any]], owner_dockets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    owner_by_library = {row["proposed_library_ref"]: row for row in owner_dockets}
    policy = {
        "CROSS_NAMESPACE_COLLISION_REVIEW": (
            "STRUCTURAL_GATES_REFUSED_AUTHORITY_VERDICT_MISSING", [], "stage.boundary.02_collision_tests",
        ),
        "LIBRARY_SEAM_ARCHETYPE_REVIEW": (
            "BLOCKED", ["COLLISION_DISPOSITIONS_MISSING"], "stage.boundary.03_owner_candidates",
        ),
        "PRODUCT_CAPABILITY_BOUNDARY_REVIEW": (
            "BLOCKED", ["OWNER_VERDICTS_MISSING", "COLLISION_DISPOSITIONS_MISSING"], "stage.boundary.04_product_boundary",
        ),
        "PROVISIONAL_EXACT_CONTRACT_LOWERING_REVIEW": (
            "BLOCKED", ["OWNER_UNRATIFIED", "PRODUCT_BOUNDARY_UNRATIFIED", "LIBRARY_BOUNDARY_UNRATIFIED"], "stage.boundary.06_contract_lowering",
        ),
    }
    result = []
    for row in packages:
        readiness, blockers, target = policy[row["package_kind"]]
        ready_subjects: list[str] = []
        blocked_subjects: list[str] = []
        if row["package_kind"] == "LIBRARY_SEAM_ARCHETYPE_REVIEW":
            ready_subjects = sorted(
                ref for ref in row["subject_refs"]
                if owner_by_library[ref]["owner_review_readiness"] == "EVIDENCE_PACKET_READY_OWNER_AUTHORITY_VERDICT_MISSING"
            )
            blocked_subjects = sorted(set(row["subject_refs"]) - set(ready_subjects))
            if ready_subjects:
                readiness = "PARTIAL_OWNER_EVIDENCE_READY_AUTHORITY_VERDICT_MISSING"
                blockers = ["COLLISION_AUTHORITY_VERDICTS_MISSING_FOR_REMAINING_SUBJECTS"] if blocked_subjects else []
        result.append({
            "frontier_ref": "frontier." + row["package_id"],
            "package_ref": row["package_id"],
            "package_kind": row["package_kind"],
            "readiness": readiness,
            "ready_subject_refs": ready_subjects,
            "blocked_subject_refs": blocked_subjects,
            "blocking_condition_refs": blockers,
            "target_stage_ref": target,
            "automatic_execution_forbidden": True,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return result


def implementation_vertical_admission_audit(
    vacancies: list[dict[str, Any]], collision_families: list[dict[str, Any]],
    owner_dockets: list[dict[str, Any]], contract_dockets: list[dict[str, Any]],
    frontier: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "audit_id": "audit.cross-slice.implementation-vertical-admission.v1",
        "as_of": AS_OF,
        "candidate_library_seams": len(vacancies),
        "semantic_module_grounded_candidates": len(vacancies),
        "collision_review_families_ready": sum(
            row["readiness"] == "STRUCTURAL_GATES_REFUSED_AUTHORITY_VERDICT_MISSING" for row in frontier
        ),
        "candidate_boundaries_ratified": 0,
        "candidate_owners_ratified": 0,
        "candidate_exact_contracts_selected": 0,
        "candidate_p5_intakes_admitted": 0,
        "candidate_p6_qualification_scopes_created": 0,
        "candidate_implementations_qualified": 0,
        "candidate_p8_vertical_obligations_created": 0,
        "candidate_vertical_acceptances_executed": 0,
        "provisional_contract_dockets_refusing": sum(
            row["compiler_lowering_state"] == "REFUSED_UPSTREAM_RATIFICATION_MISSING"
            for row in contract_dockets
        ),
        "next_admissible_work": {
            "package_kinds": ["CROSS_NAMESPACE_COLLISION_REVIEW", "COLLISION_FREE_OWNER_DOCKET_REVIEW"],
            "collision_family_package_count": len(collision_families),
            "collision_free_owner_docket_count": sum(
                row["owner_review_readiness"] == "EVIDENCE_PACKET_READY_OWNER_AUTHORITY_VERDICT_MISSING"
                for row in owner_dockets
            ),
            "unit_of_work": "collision_family_or_collision_free_owner_docket",
            "required_receipts": [
                "meaning_partition", "homonym_or_shared_mechanic_verdict",
                "owner_counterfactual", "merge_refusal_or_replacement_edges",
            ],
        },
        "implementation_work_admissible": False,
        "vertical_work_admissible": False,
        "admission_law": "Research and contract shaping may proceed, but implementation selection and vertical acceptance remain inadmissible until exact canonical boundary, owner and contract receipts exist.",
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }


def boundary_kind(disposition: str) -> str:
    text = disposition.lower()
    if "promote_new" in text or "new_product" in text:
        return "NEW_PRODUCT_BOUNDARY_CANDIDATE"
    if "split_combined_product" in text or "replacement_candidate" in text:
        return "PRODUCT_SPLIT_OR_REPLACEMENT_CANDIDATE"
    if text.startswith("retain") or "retain_two" in text or "retain_separate" in text:
        return "RETAIN_OR_NARROW_PRODUCT_CANDIDATE"
    if "homonym" in text or text.startswith("rename") or "replace" in text:
        return "LANGUAGE_SPLIT_OR_RENAME_CANDIDATE"
    if "import" in text or "reclassify" in text or "move_to" in text or "ownership_to" in text:
        return "OWNER_RECLASSIFICATION_OR_IMPORT_CANDIDATE"
    if "acl" in text or "handoff" in text or "published_language" in text or "effect_authority" in text:
        return "ACL_HANDOFF_OR_EFFECT_SEAM_CANDIDATE"
    if "capabilit" in text or "method" in text or "kernel" in text or "scoring_mode" in text:
        return "CAPABILITY_OR_METHOD_BOUNDARY_CANDIDATE"
    if "composition" in text or "facade" in text or "provider_offer" in text:
        return "COMPOSITION_OR_PROVIDER_NON_OWNER_CANDIDATE"
    return "OTHER_BOUNDARY_ADJUDICATION_CANDIDATE"


def boundary_routes(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for finding in findings:
        if finding.get("candidate_disposition") == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED":
            continue
        rows.append({
            "route_id": "route.boundary." + finding["finding_id"].replace("finding.", "").replace(".", "-"),
            "source_finding_ref": finding["finding_id"],
            "source_slice": finding["source_slice"],
            "candidate_disposition": finding.get("candidate_disposition"),
            "boundary_kind_ref": "boundary_kind." + boundary_kind(finding.get("candidate_disposition", "")),
            "product_refs": sorted(set(finding.get("product_refs", []) + ([finding["product_ref"]] if finding.get("product_ref") else []))),
            "library_refs": sorted(finding.get("library_refs", [])),
            "owner_candidate": "UNASSIGNED",
            "ratification_state": "UNRATIFIED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return sorted(rows, key=lambda r: (r["boundary_kind_ref"], r["source_finding_ref"]))


def boundary_kind_rows(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_kind: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in routes:
        by_kind[row["boundary_kind_ref"]].append(row)
    return [{
        "boundary_kind_ref": kind,
        "finding_count": len(members),
        "source_finding_refs": sorted(row["source_finding_ref"] for row in members),
        "adjudication_law": "Each finding requires evidence-backed counterfactual boundary tests, exact owner review and explicit replacement/import edges before canonical mutation.",
        "owner_decision": "UNRATIFIED",
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    } for kind, members in sorted(by_kind.items())]


TOKEN_STOP = {"library"}


def collision_candidates(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    token_refs: dict[str, set[str]] = defaultdict(set)
    token_namespaces: dict[str, set[str]] = defaultdict(set)
    for row in routes:
        ref = row["proposed_library_ref"]
        namespace = row["namespace"]
        tokens = {t for t in re.split(r"[._-]+", ref) if len(t) >= 5 and t not in TOKEN_STOP}
        for token in tokens:
            token_refs[token].add(ref)
            token_namespaces[token].add(namespace)
    rows = []
    for token, refs in sorted(token_refs.items()):
        namespaces = token_namespaces[token]
        if len(refs) < 2 or len(namespaces) < 2:
            continue
        rows.append({
            "collision_id": "collision.cross_slice.token." + token,
            "surface_token": token,
            "candidate_library_refs": sorted(refs),
            "namespace_refs": sorted(namespaces),
            "collision_kind": "CROSS_NAMESPACE_HOMONYM_OR_SHARED_MECHANIC_CANDIDATE",
            "required_tests": ["meaning_substitution_counterexample", "owner_counterfactual", "state_machine_comparison", "input_output_grain_comparison", "authority_effect_comparison", "independent_adoption_test"],
            "merge_authorized": False,
            "owner_decision": "UNRATIFIED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return rows


COLLISION_FAMILY_TERMS = [
    ("protection_access_safety", {"access", "privacy", "safety", "security", "sensitive"}),
    ("authority_policy_effect", {"authority", "policy", "entitlement", "disposition", "handoff", "effect", "admission"}),
    ("evidence_receipt_provenance", {"evidence", "receipt", "provenance", "audit", "trace", "explanation", "certificate"}),
    ("lifecycle_edition_history", {"edition", "lifecycle", "history", "status", "generation", "snapshot", "release", "mutation"}),
    ("identity_occurrence_grain", {"identity", "occurrence", "target", "population", "grain", "cardinality", "record", "binding"}),
    ("algebra_composition_constraint", {"algebra", "semantics", "constraint", "combination", "fusion", "determinism", "equivalence"}),
    ("schema_profile_representation", {"schema", "profile", "format", "carrier", "expression", "vector", "artifact"}),
    ("result_observation_assessment", {"result", "observation", "assessment", "outcome", "page", "finding"}),
    ("evaluation_benchmark_quality", {"evaluation", "benchmark", "corpus", "metric", "quality", "calibration", "comparison"}),
    ("plan_design_definition", {"plan", "design", "definition", "requirement", "recipe", "workload"}),
    ("query_retrieval_view", {"query", "retrieval", "selection", "filter", "view", "pagination", "visibility"}),
    ("relation_mapping_topology", {"relation", "mapping", "join", "graph", "path", "hierarchy", "topology", "crosswalk"}),
    ("model_algorithm_kernel", {"model", "algorithm", "kernel", "ranking", "forecast", "sampling"}),
    ("federation_reconciliation_coverage", {"reconciliation", "federation", "coverage", "freshness", "projection", "acquisition"}),
    ("unclassified_surface_homonym", set()),
]

GENERIC_SURFACE_TOKENS = {
    "analysis", "artifact", "binding", "contract", "cross", "definition", "design",
    "edition", "evaluation", "evidence", "identity", "lifecycle", "model", "plan",
    "profile", "reference", "result", "review", "semantic", "semantics", "status",
    "temporal", "total", "value", "vector", "vertical", "vocabulary", "workload",
}

IR_FAMILY_BY_ARCHETYPE = {
    "privacy_security_safety": "ProtectionConstraintIR",
    "authority_policy_decision": "AuthorityDecisionIR",
    "evidence_receipt_provenance": "EvidenceProvenanceIR",
    "evaluation_assurance_benchmark": "EvaluationAssuranceIR",
    "compatibility_diff_migration": "CompatibilityMigrationIR",
    "publication_release_delivery": "PublicationDeliveryIR",
    "federation_reconciliation_coverage": "FederationReconciliationIR",
    "query_retrieval_selection_view": "QueryRetrievalIR",
    "relation_mapping_join_topology": "RelationTopologyIR",
    "model_estimator_algorithm_kernel": "MethodKernelIR",
    "resource_cost_budget_capacity": "ResourceBudgetIR",
    "review_challenge_consensus": "HumanReviewIR",
    "state_lifecycle_history_edition": "LifecycleEditionIR",
    "plan_protocol_definition": "PlanProtocolIR",
    "schema_representation_shape_profile": "RepresentationSchemaIR",
    "algebra_composition_semantics": "AlgebraExpressionIR",
    "result_observation_assessment": "ResultAssessmentIR",
    "operation_execution_materialization": "ExecutionEffectIR",
    "subject_occurrence_identity_grain": "SubjectIdentityIR",
    "human_role_competence_assignment": "HumanRoleIR",
    "domain_specific_composite": "DomainCompositeIR",
}

CONTRACT_FACETS = [
    "sovereign_question_and_negative_mission", "ubiquitous_language_and_homonyms",
    "semantic_owner_and_authority", "subject_identity_equality_and_grain",
    "value_objects_entities_aggregates", "constructors_factories_and_invariants",
    "commands_queries_and_total_results", "domain_and_integration_events",
    "state_machine_and_transition_refusals", "policies_services_and_precedence",
    "time_validity_recording_and_expiry", "concurrency_idempotency_and_replay",
    "partiality_uncertainty_and_information_loss", "composition_algebra_and_laws",
    "effect_ports_authorization_and_receipts", "evidence_provenance_and_conformance",
    "representation_serialization_and_acl", "compatibility_migration_and_exit",
    "privacy_security_safety_and_retention", "resources_budgets_backpressure_and_failure",
    "repository_projection_and_read_models", "public_api_feature_dependency_and_msrv",
    "property_model_fuzz_mutation_and_conformance_tests", "two_implementation_and_vertical_acceptance",
]


def collision_family(token: str) -> str:
    for family, terms in COLLISION_FAMILY_TERMS[:-1]:
        if token in terms:
            return family
    return "unclassified_surface_homonym"


def collision_review_dockets(collisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "docket_id": "docket." + row["collision_id"],
        "collision_ref": row["collision_id"],
        "surface_token": row["surface_token"],
        "collision_family_ref": "collision_family." + collision_family(row["surface_token"]),
        "candidate_library_refs": row["candidate_library_refs"],
        "namespace_refs": row["namespace_refs"],
        "required_meaning_partitions": [
            "subject_and_grain", "operation_and_result", "state_and_time", "authority_and_effect",
            "representation_and_loss", "applicability_and_owner", "compatibility_and_exit",
        ],
        "admissible_dispositions": [
            "CONFIRMED_HOMONYM_KEEP_DISTINCT", "SHARED_MECHANIC_WITH_LOCAL_PROFILES",
            "SAME_OWNER_DISTINCT_LIBRARIES", "MERGE_CANDIDATE_REQUIRES_REPLACEMENT_EDGES",
            "TOKEN_TOO_GENERIC_NO_SEMANTIC_COLLISION",
        ],
        "disposition_state": "OPEN_UNRATIFIED",
        "merge_authorized": False,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    } for row in collisions]


def collision_family_rows(dockets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in dockets:
        by_family[row["collision_family_ref"]].append(row)
    return [{
        "collision_family_ref": family_ref,
        "docket_count": len(rows),
        "collision_refs": sorted(row["collision_ref"] for row in rows),
        "surface_tokens": sorted(row["surface_token"] for row in rows),
        "review_law": "A shared surface token is only a retrieval key. Meaning, owner and merge require exact counterfactual adjudication for every member.",
        "status": "OPEN_UNRATIFIED",
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    } for family_ref, rows in sorted(by_family.items())]


def collision_meaning_partitions(
    collisions: list[dict[str, Any]], findings: list[dict[str, Any]],
    routes: list[dict[str, Any]], owner_dockets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    finding_by_ref = {row["finding_id"]: row for row in findings}
    route_by_library = {row["proposed_library_ref"]: row for row in routes}
    owner_by_library = {row["proposed_library_ref"]: row for row in owner_dockets}
    rows = []
    for collision in collisions:
        for library_ref in collision["candidate_library_refs"]:
            route = route_by_library[library_ref]
            owner = owner_by_library[library_ref]
            finding = finding_by_ref[route["source_finding_ref"]]
            module_sources = sorted({
                source for module in owner["semantic_module_candidates"] for source in module["source_refs"]
            })
            rows.append({
                "partition_id": "partition." + collision["collision_id"] + "." + route["route_id"].split("route.cross_slice.", 1)[-1],
                "collision_ref": collision["collision_id"],
                "surface_token": collision["surface_token"],
                "candidate_library_ref": library_ref,
                "namespace": route["namespace"],
                "source_slice": route["source_slice"],
                "source_finding_ref": route["source_finding_ref"],
                "candidate_meaning_statement": finding.get("finding", finding.get("reason", "")),
                "primary_archetype_ref": route["primary_archetype_ref"],
                "secondary_archetype_refs": route["secondary_archetype_refs"],
                "local_context_candidate_ref": owner["local_context_candidate_ref"],
                "semantic_module_candidate_refs": [
                    module["semantic_module_ref"] for module in owner["semantic_module_candidates"]
                ],
                "evidence_source_refs": module_sources,
                "meaning_identity_preserved": True,
                "merge_authorized": False,
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
    return sorted(rows, key=lambda row: (row["collision_ref"], row["candidate_library_ref"]))


def collision_adjudication_candidates(
    collisions: list[dict[str, Any]], partitions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_collision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in partitions:
        by_collision[row["collision_ref"]].append(row)
    rows = []
    for collision in collisions:
        members = by_collision[collision["collision_id"]]
        archetypes = sorted({row["primary_archetype_ref"] for row in members})
        contexts = sorted({row["local_context_candidate_ref"] for row in members})
        token = collision["surface_token"]
        if token in GENERIC_SURFACE_TOKENS:
            disposition = "GENERIC_SURFACE_TOKEN_NO_MERGE_SIGNAL_CANDIDATE"
            rationale = "The shared token names a broad structural role and cannot establish semantic overlap, ownership or merge eligibility."
        elif len(archetypes) == 1:
            disposition = "SHARED_MECHANIC_WITH_LOCAL_PROFILES_CANDIDATE"
            rationale = "Members share a primary review archetype, but exact meanings, contexts and local residuals remain independently owned until authority review."
        else:
            disposition = "HOMONYM_KEEP_DISTINCT_CANDIDATE"
            rationale = "Members cross primary semantic archetypes, so substituting the shared token would erase different subjects, operations, results or authority boundaries."
        rows.append({
            "adjudication_candidate_id": "candidate.adjudication." + collision["collision_id"],
            "collision_ref": collision["collision_id"],
            "collision_family_ref": "collision_family." + collision_family(token),
            "surface_token": token,
            "member_partition_refs": [row["partition_id"] for row in members],
            "member_library_refs": [row["candidate_library_ref"] for row in members],
            "namespace_refs": sorted({row["namespace"] for row in members}),
            "primary_archetype_refs": archetypes,
            "local_context_candidate_refs": contexts,
            "candidate_disposition": disposition,
            "candidate_rationale": rationale,
            "required_counterexamples": [
                "substitute_member_A_type_for_member_B", "apply_member_A_invariant_to_member_B",
                "reuse_member_A_owner_for_member_B", "replay_member_A_state_machine_as_member_B",
                "apply_member_A_authority_or_effect_to_member_B",
            ],
            "authority_verdict": "MISSING",
            "candidate_state": "REVERSIBLE_EVIDENCE_PACKET_UNRATIFIED",
            "merge_authorized": False,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return rows


def attach_collision_evidence_to_owner_dockets(
    owner_dockets: list[dict[str, Any]], adjudications: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    refs_by_library: dict[str, list[str]] = defaultdict(list)
    for row in adjudications:
        for library_ref in row["member_library_refs"]:
            refs_by_library[library_ref].append(row["adjudication_candidate_id"])
    result = []
    for source_row in owner_dockets:
        row = dict(source_row)
        refs = sorted(refs_by_library[row["proposed_library_ref"]])
        row["collision_adjudication_candidate_refs"] = refs
        row["collision_authority_verdicts_required"] = len(refs)
        row["owner_review_readiness"] = (
            "BLOCKED_COLLISION_AUTHORITY_VERDICTS_MISSING" if refs
            else "EVIDENCE_PACKET_READY_OWNER_AUTHORITY_VERDICT_MISSING"
        )
        result.append(row)
    return result


def owner_adjudication_candidates(owner_dockets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for docket in owner_dockets:
        if docket["owner_review_readiness"] != "EVIDENCE_PACKET_READY_OWNER_AUTHORITY_VERDICT_MISSING":
            continue
        top_module = docket["semantic_module_candidates"][0]
        if docket["namespace"] == "method_kernels":
            disposition = "SHARED_METHOD_CONTEXT_OWNER_CANDIDATE"
            proposed_owner = (
                docket["existing_context_counterfactuals"][0]["context_ref"]
                if docket["existing_context_counterfactuals"] else docket["shared_mechanic_counterfactual_ref"]
            )
            rationale = "The seam is explicitly a reusable method kernel and lacks a retained product-local owner; shared method semantics must still be separated from execution and artifact ownership."
        elif top_module["exact_module_id_token_overlap"]:
            disposition = "LOCAL_SEAM_OWNER_LOCUS_CANDIDATE"
            proposed_owner = docket["local_context_candidate_ref"]
            rationale = "The exact proposed identity aligns with an evidence-backed semantic module in one product slice. The owner locus preserves the exact seam; whether it consolidates with other loci into one bounded context remains an explicit decision."
        elif docket["existing_context_counterfactuals"] and docket["existing_context_counterfactuals"][0]["score"] >= 8:
            disposition = "IMPORT_EXISTING_CONTEXT_OWNER_CANDIDATE"
            proposed_owner = docket["existing_context_counterfactuals"][0]["context_ref"]
            rationale = "No exact local module-name match exists and an existing context has the strongest specific-token overlap; import or merge must be tested before creating a new owner."
        else:
            disposition = "OWNER_LOCUS_RESEARCH_OR_SPLIT_CANDIDATE"
            proposed_owner = docket["local_context_candidate_ref"]
            rationale = "Evidence grounds the seam but does not yet distinguish a cohesive local owner from a split or shared mechanic."
        rows.append({
            "owner_adjudication_candidate_id": "candidate.owner_adjudication." + docket["docket_id"].split("docket.owner.", 1)[-1],
            "owner_docket_ref": docket["docket_id"],
            "candidate_library_ref": docket["proposed_library_ref"],
            "candidate_disposition": disposition,
            "proposed_owner_context_ref": proposed_owner,
            "candidate_rationale": rationale,
            "primary_semantic_module_ref": top_module["semantic_module_ref"],
            "primary_module_score": top_module["score"],
            "primary_module_exact_token_overlap": top_module["exact_module_id_token_overlap"],
            "product_context_candidate_refs": docket["product_context_candidate_refs"],
            "existing_context_counterfactuals": docket["existing_context_counterfactuals"],
            "shared_mechanic_counterfactual_ref": docket["shared_mechanic_counterfactual_ref"],
            "required_challenges": [
                "replace_local_owner_with_best_existing_context", "replace_local_owner_with_shared_mechanic_context",
                "split_stateful_lifecycle_from_pure_mechanic", "test_independent_adoption_and_release",
                "test_two_unrelated_vertical_ubiquitous_languages", "test_authority_effect_and_exit_boundaries",
            ],
            "authority_verdict": "MISSING",
            "candidate_state": "REVERSIBLE_OWNER_EVIDENCE_PACKET_UNRATIFIED",
            "owner_selected": False,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return sorted(rows, key=lambda row: row["candidate_library_ref"])


def attach_owner_adjudication_candidates(
    owner_dockets: list[dict[str, Any]], candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_docket = {row["owner_docket_ref"]: row["owner_adjudication_candidate_id"] for row in candidates}
    result = []
    for source_row in owner_dockets:
        row = dict(source_row)
        row["owner_adjudication_candidate_ref"] = by_docket.get(row["docket_id"])
        result.append(row)
    return result


NEGATIVE_TWIN_KINDS = [
    ("TYPE_SUBSTITUTION", "Substitute member A's public semantic type at member B's use site.", ["subject_kind", "identity", "grain", "representation"]),
    ("INVARIANT_TRANSPLANT", "Apply member A's invariants and algebraic laws to member B.", ["invariants", "composition_laws", "partiality", "information_loss"]),
    ("OWNER_REBIND", "Replace member B's owner locus and authority with member A's.", ["ubiquitous_language", "owner_authority", "change_cadence", "exit"]),
    ("STATE_MACHINE_REPLAY", "Replay member A's states and transitions as member B's lifecycle.", ["state_machine", "time_model", "concurrency", "refusals"]),
    ("AUTHORITY_EFFECT_TRANSFER", "Transfer member A's permissions, decisions and effects to member B.", ["authority", "effect_boundary", "evidence_scope", "safety"]),
]


def partition_distance(left: dict[str, Any], right: dict[str, Any]) -> int:
    left_tokens = word_tokens(left["candidate_meaning_statement"])
    right_tokens = word_tokens(right["candidate_meaning_statement"])
    union = left_tokens | right_tokens
    overlap = left_tokens & right_tokens
    lexical_distance = 100 if not union else round(100 * (1 - len(overlap) / len(union)))
    return (
        lexical_distance
        + (40 if left["primary_archetype_ref"] != right["primary_archetype_ref"] else 0)
        + (20 if left["local_context_candidate_ref"] != right["local_context_candidate_ref"] else 0)
        + (10 if set(left["semantic_module_candidate_refs"]).isdisjoint(right["semantic_module_candidate_refs"]) else 0)
    )


def collision_negative_twins(
    adjudications: list[dict[str, Any]], partitions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_collision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in partitions:
        by_collision[row["collision_ref"]].append(row)
    rows = []
    for adjudication in adjudications:
        members = by_collision[adjudication["collision_ref"]]
        pairs = [
            (partition_distance(left, right), left, right)
            for index, left in enumerate(members) for right in members[index + 1:]
        ]
        _, left, right = sorted(
            pairs,
            key=lambda item: (-item[0], item[1]["candidate_library_ref"], item[2]["candidate_library_ref"]),
        )[0]
        for kind, mutation, oracle_dimensions in NEGATIVE_TWIN_KINDS:
            rows.append({
                "negative_twin_id": "negative_twin." + adjudication["collision_ref"] + "." + kind.lower(),
                "collision_ref": adjudication["collision_ref"],
                "collision_adjudication_candidate_ref": adjudication["adjudication_candidate_id"],
                "negative_twin_kind": kind,
                "member_a_partition_ref": left["partition_id"],
                "member_b_partition_ref": right["partition_id"],
                "member_a_library_ref": left["candidate_library_ref"],
                "member_b_library_ref": right["candidate_library_ref"],
                "member_a_meaning": left["candidate_meaning_statement"],
                "member_b_meaning": right["candidate_meaning_statement"],
                "mutation": mutation,
                "required_oracle_dimensions": oracle_dimensions,
                "expected_result": "MUST_REFUSE_UNLESS_EXACT_EQUIVALENCE_AND_AUTHORITY_PROOF",
                "execution_state": "UNEXECUTED_AUTHORITY_ORACLE_MISSING",
                "evidence_source_refs": sorted(set(left["evidence_source_refs"] + right["evidence_source_refs"])),
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
    return rows


OWNER_CHALLENGE_KINDS = [
    "REPLACE_WITH_BEST_EXISTING_CONTEXT",
    "REPLACE_WITH_SHARED_MECHANIC_CONTEXT",
    "SPLIT_STATEFUL_LIFECYCLE_FROM_PURE_MECHANIC",
    "INDEPENDENT_ADOPTION_AND_RELEASE",
    "TWO_UNRELATED_VERTICAL_LANGUAGE_TRANSFER",
    "AUTHORITY_EFFECT_AND_EXIT_BOUNDARY",
]


def owner_counterfactual_challenges(
    candidates: list[dict[str, Any]], owner_dockets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    docket_by_ref = {row["docket_id"]: row for row in owner_dockets}
    rows = []
    for candidate in candidates:
        docket = docket_by_ref[candidate["owner_docket_ref"]]
        best_existing = (
            docket["existing_context_counterfactuals"][0]["context_ref"]
            if docket["existing_context_counterfactuals"] else None
        )
        targets = {
            "REPLACE_WITH_BEST_EXISTING_CONTEXT": best_existing,
            "REPLACE_WITH_SHARED_MECHANIC_CONTEXT": docket["shared_mechanic_counterfactual_ref"],
            "SPLIT_STATEFUL_LIFECYCLE_FROM_PURE_MECHANIC": "counterfactual.split.stateful_lifecycle__pure_mechanic",
            "INDEPENDENT_ADOPTION_AND_RELEASE": "counterfactual.independent_adoption_release",
            "TWO_UNRELATED_VERTICAL_LANGUAGE_TRANSFER": "counterfactual.two_unrelated_verticals",
            "AUTHORITY_EFFECT_AND_EXIT_BOUNDARY": candidate["proposed_owner_context_ref"],
        }
        for kind in OWNER_CHALLENGE_KINDS:
            target = targets[kind]
            rows.append({
                "challenge_id": "challenge.owner." + candidate["owner_adjudication_candidate_id"].split("candidate.owner_adjudication.", 1)[-1] + "." + kind.lower(),
                "owner_adjudication_candidate_ref": candidate["owner_adjudication_candidate_id"],
                "owner_docket_ref": candidate["owner_docket_ref"],
                "candidate_library_ref": candidate["candidate_library_ref"],
                "challenge_kind": kind,
                "counterfactual_target_ref": target,
                "required_observations": [
                    "ubiquitous_language_delta", "owned_invariant_delta", "state_and_time_delta",
                    "authority_effect_delta", "change_and_exit_delta", "independent_consumer_delta",
                ],
                "falsification_law": "Reject the proposed owner if the counterfactual owns the meaning more coherently without translation, authority leakage, lifecycle coupling or loss of independent substitutability.",
                "challenge_state": (
                    "NO_EXISTING_COUNTERFACTUAL_RESEARCH_GAP"
                    if kind == "REPLACE_WITH_BEST_EXISTING_CONTEXT" and target is None
                    else "EVIDENCE_PACKET_READY_UNEXECUTED"
                ),
                "authority_verdict": "MISSING",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
    return rows


def context_consolidation_graph(
    owner_dockets: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    memberships: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in owner_dockets:
        memberships[("NAMESPACE_PRODUCT_LANGUAGE", row["namespace"])].append(row)
        memberships[("PRIMARY_SEMANTIC_MODULE", row["semantic_module_candidates"][0]["semantic_module_ref"])].append(row)
        memberships[("SHARED_MECHANIC_ARCHETYPE", row["primary_archetype_ref"])].append(row)
    hypotheses = []
    hypothesis_ref_by_key: dict[tuple[str, str], str] = {}
    for (kind, key), members in sorted(memberships.items()):
        slug_key = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
        ref = "hypothesis.context_consolidation." + kind.lower() + "." + slug_key
        hypothesis_ref_by_key[(kind, key)] = ref
        hypotheses.append({
            "hypothesis_ref": ref,
            "hypothesis_kind": kind,
            "grouping_key": key,
            "member_owner_locus_refs": sorted(row["local_context_candidate_ref"] for row in members),
            "member_library_refs": sorted(row["proposed_library_ref"] for row in members),
            "member_count": len(members),
            "required_cohesion_tests": [
                "one_ubiquitous_language", "one_invariant_and_state_boundary", "one_authority_model",
                "coherent_change_cadence", "independent_substitutability", "explicit_acl_for_residuals",
            ],
            "risk_law": (
                "Namespace grouping may hide multiple lifecycles or products."
                if kind == "NAMESPACE_PRODUCT_LANGUAGE" else
                "Module grouping may be too narrow or may mistake research organization for ownership."
                if kind == "PRIMARY_SEMANTIC_MODULE" else
                "Shared mechanics require local profiles and must not erase bounded-context language."
            ),
            "boundary_verdict": "MISSING",
            "candidate_state": "REVERSIBLE_CONSOLIDATION_HYPOTHESIS_UNRATIFIED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    routes = []
    for row in owner_dockets:
        routes.append({
            "route_id": "route.context_consolidation." + row["docket_id"].split("docket.owner.", 1)[-1],
            "candidate_library_ref": row["proposed_library_ref"],
            "exact_owner_locus_ref": row["local_context_candidate_ref"],
            "namespace_hypothesis_ref": hypothesis_ref_by_key[("NAMESPACE_PRODUCT_LANGUAGE", row["namespace"])],
            "module_hypothesis_ref": hypothesis_ref_by_key[("PRIMARY_SEMANTIC_MODULE", row["semantic_module_candidates"][0]["semantic_module_ref"])],
            "shared_mechanic_hypothesis_ref": hypothesis_ref_by_key[("SHARED_MECHANIC_ARCHETYPE", row["primary_archetype_ref"])],
            "existing_context_counterfactual_refs": [
                candidate["context_ref"] for candidate in row["existing_context_counterfactuals"]
            ],
            "selected_context_ref": None,
            "route_state": "OPEN_NO_CONTEXT_BOUNDARY_SELECTED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return hypotheses, routes


def boundary_challenge_evidence_routes(
    boundary_routes: list[dict[str, Any]], findings: list[dict[str, Any]],
    owner_dockets: list[dict[str, Any]], owner_adjudications: list[dict[str, Any]],
    collision_adjudications: list[dict[str, Any]], negative_twins: list[dict[str, Any]],
    consolidation_routes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    finding_by_ref = {row["finding_id"]: row for row in findings}
    owner_adjudication_by_library = {
        row["candidate_library_ref"]: row["owner_adjudication_candidate_id"]
        for row in owner_adjudications
    }
    consolidation_by_library = {
        row["candidate_library_ref"]: row for row in consolidation_routes
    }
    collision_refs_by_library: dict[str, set[str]] = defaultdict(set)
    for row in collision_adjudications:
        for library_ref in row["member_library_refs"]:
            collision_refs_by_library[library_ref].add(row["adjudication_candidate_id"])
    twins_by_collision_candidate: dict[str, list[str]] = defaultdict(list)
    for row in negative_twins:
        twins_by_collision_candidate[row["collision_adjudication_candidate_ref"]].append(row["negative_twin_id"])
    owner_by_slice: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in owner_dockets:
        owner_by_slice[row["source_slice"]].append(row)
    rows = []
    for boundary in boundary_routes:
        source = finding_by_ref[boundary["source_finding_ref"]]
        query_tokens = word_tokens(" ".join([
            source.get("finding", ""), source.get("reason", ""),
            source.get("candidate_disposition", ""), *boundary.get("product_refs", []),
        ]))
        ranked = []
        for owner in owner_by_slice[boundary["source_slice"]]:
            candidate_source = finding_by_ref[owner["source_finding_ref"]]
            candidate_tokens = word_tokens(" ".join([
                owner["proposed_library_ref"], candidate_source.get("finding", ""),
                candidate_source.get("reason", ""),
            ]))
            overlap = query_tokens & candidate_tokens
            if overlap:
                ranked.append({
                    "candidate_library_ref": owner["proposed_library_ref"],
                    "relevance_score": len(overlap),
                    "overlap_tokens": sorted(overlap),
                })
        ranked = sorted(ranked, key=lambda row: (-row["relevance_score"], row["candidate_library_ref"]))[:10]
        ranked_refs = [row["candidate_library_ref"] for row in ranked]
        collision_candidate_refs = sorted({
            ref for library_ref in ranked_refs for ref in collision_refs_by_library[library_ref]
        })
        hypothesis_refs = sorted({
            ref for library_ref in ranked_refs
            for ref in [
                consolidation_by_library[library_ref]["namespace_hypothesis_ref"],
                consolidation_by_library[library_ref]["module_hypothesis_ref"],
                consolidation_by_library[library_ref]["shared_mechanic_hypothesis_ref"],
            ]
        })
        slice_universe = sorted(
            row["proposed_library_ref"] for row in owner_by_slice[boundary["source_slice"]]
        )
        rows.append({
            "route_id": "route.boundary_challenge_evidence." + boundary["source_finding_ref"].replace("finding.", "").replace(".", "-"),
            "boundary_finding_ref": boundary["source_finding_ref"],
            "boundary_kind_ref": boundary["boundary_kind_ref"],
            "source_slice": boundary["source_slice"],
            "slice_candidate_universe_refs": slice_universe,
            "candidate_universe_state": (
                "PRESENT" if slice_universe else "NO_PROPOSED_LIBRARY_SEAMS_IN_SOURCE_SLICE"
            ),
            "ranked_related_candidates": ranked,
            "owner_adjudication_candidate_refs": sorted(
                owner_adjudication_by_library[ref] for ref in ranked_refs
                if ref in owner_adjudication_by_library
            ),
            "collision_adjudication_candidate_refs": collision_candidate_refs,
            "collision_negative_twin_refs": sorted(
                twin for ref in collision_candidate_refs for twin in twins_by_collision_candidate[ref]
            ),
            "context_consolidation_hypothesis_refs": hypothesis_refs,
            "routing_law": "Rank and slice co-location identify review context only; they do not prove relevance, ownership, a boundary disposition or closure.",
            "direct_evidence_claim": False,
            "authority_verdict": "MISSING",
            "route_state": (
                "CONTEXT_ROUTED_UNRATIFIED" if slice_universe
                else "NO_CROSS_SLICE_CANDIDATE_CONTEXT_AVAILABLE"
            ),
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return sorted(rows, key=lambda row: row["boundary_finding_ref"])


def negative_twin_gate_receipts(negative_twins: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "receipt.gate." + row["negative_twin_id"],
        "negative_twin_ref": row["negative_twin_id"],
        "collision_ref": row["collision_ref"],
        "member_a_library_ref": row["member_a_library_ref"],
        "member_b_library_ref": row["member_b_library_ref"],
        "gate_inputs": {
            "exact_equivalence_proof_refs": [],
            "owner_authority_receipt_refs": [],
            "ratified_contract_refs": [],
        },
        "gate_result": "REFUSED",
        "refusal_codes": [
            "EXACT_EQUIVALENCE_PROOF_MISSING", "OWNER_AUTHORITY_RECEIPT_MISSING",
            "RATIFIED_MEMBER_CONTRACTS_MISSING",
        ],
        "structural_gate_executed": True,
        "semantic_distinctness_proven": False,
        "authority_verdict_supplied": False,
        "receipt_law": "Fail-closed refusal proves only that required proof is absent; it does not prove homonymy, equivalence, ownership or a merge disposition.",
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    } for row in negative_twins]


def owner_challenge_evidence_vacancies(
    owner_challenges: list[dict[str, Any]], owner_dockets: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    docket_by_ref = {row["docket_id"]: row for row in owner_dockets}
    vacancies = []
    for challenge in owner_challenges:
        docket = docket_by_ref[challenge["owner_docket_ref"]]
        evidence_refs = sorted({
            source for module in docket["semantic_module_candidates"] for source in module["source_refs"]
        })
        for observation in challenge["required_observations"]:
            vacancies.append({
                "vacancy_id": "vacancy.owner_challenge." + challenge["challenge_id"].split("challenge.owner.", 1)[-1] + "." + observation,
                "challenge_ref": challenge["challenge_id"],
                "owner_adjudication_candidate_ref": challenge["owner_adjudication_candidate_ref"],
                "candidate_library_ref": challenge["candidate_library_ref"],
                "challenge_kind": challenge["challenge_kind"],
                "required_observation_kind": observation,
                "candidate_source_refs": evidence_refs,
                "required_evidence": [
                    "exact_subject_and_scope", "counterfactual_context_definition",
                    "observed_difference_or_equivalence", "independent_appraiser",
                    "authority_receipt", "validity_interval",
                ],
                "status": "OPEN_EVIDENCE_AND_AUTHORITY_MISSING",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
    by_program: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in vacancies:
        by_program[(row["challenge_kind"], row["required_observation_kind"])].append(row)
    programs = [{
        "program_ref": "program.owner_challenge_evidence." + challenge_kind.lower() + "." + observation,
        "challenge_kind": challenge_kind,
        "required_observation_kind": observation,
        "vacancy_refs": sorted(row["vacancy_id"] for row in rows),
        "vacancy_count": len(rows),
        "execution_law": "A program may collect comparable observations, but only exact owner authority may issue a verdict for each member vacancy.",
        "status": "OPEN_UNEXECUTED",
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    } for (challenge_kind, observation), rows in sorted(by_program.items())]
    return vacancies, programs


def context_cohesion_evidence_vacancies(
    hypotheses: list[dict[str, Any]], owner_dockets: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sources_by_library = {
        row["proposed_library_ref"]: sorted({
            source for module in row["semantic_module_candidates"] for source in module["source_refs"]
        })
        for row in owner_dockets
    }
    vacancies = []
    for hypothesis in hypotheses:
        candidate_sources = sorted({
            source for library_ref in hypothesis["member_library_refs"]
            for source in sources_by_library[library_ref]
        })
        for test in hypothesis["required_cohesion_tests"]:
            vacancies.append({
                "vacancy_id": "vacancy.context_cohesion." + hypothesis["hypothesis_ref"].split("hypothesis.context_consolidation.", 1)[-1] + "." + test,
                "hypothesis_ref": hypothesis["hypothesis_ref"],
                "hypothesis_kind": hypothesis["hypothesis_kind"],
                "cohesion_test_kind": test,
                "member_library_refs": hypothesis["member_library_refs"],
                "candidate_source_refs": candidate_sources,
                "required_evidence": [
                    "exact_member_scope", "positive_cohesion_observations", "negative_split_counterexample",
                    "independent_adoption_evidence", "owner_authority_receipt", "compatibility_and_exit_analysis",
                ],
                "status": "OPEN_EVIDENCE_AND_BOUNDARY_AUTHORITY_MISSING",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
    by_program: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in vacancies:
        by_program[(row["hypothesis_kind"], row["cohesion_test_kind"])].append(row)
    programs = [{
        "program_ref": "program.context_cohesion." + hypothesis_kind.lower() + "." + test,
        "hypothesis_kind": hypothesis_kind,
        "cohesion_test_kind": test,
        "vacancy_refs": sorted(row["vacancy_id"] for row in rows),
        "vacancy_count": len(rows),
        "execution_law": "Shared research mechanics may be reused, but every hypothesis keeps exact members and requires its own boundary-authority verdict.",
        "status": "OPEN_UNEXECUTED",
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    } for (hypothesis_kind, test), rows in sorted(by_program.items())]
    return vacancies, programs


def namespace_boundary_analysis(
    hypotheses: list[dict[str, Any]], owner_dockets: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    owners_by_namespace: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in owner_dockets:
        owners_by_namespace[row["namespace"]].append(row)
    namespace_hypothesis = {
        row["grouping_key"]: row for row in hypotheses
        if row["hypothesis_kind"] == "NAMESPACE_PRODUCT_LANGUAGE"
    }
    observations = []
    challenges = []
    subcontexts = []
    for namespace, owners in sorted(owners_by_namespace.items()):
        direction, rationale, cluster_suffixes = NAMESPACE_BOUNDARY_PRIORS[namespace]
        exact_refs = {row["proposed_library_ref"] for row in owners}
        clustered_refs: set[str] = set()
        cluster_refs = []
        for cluster_name, suffixes in cluster_suffixes.items():
            member_refs = [f"library.{namespace}.{suffix}" for suffix in suffixes]
            clustered_refs.update(member_refs)
            cluster_ref = f"candidate.subcontext.{namespace}.{cluster_name}"
            cluster_refs.append(cluster_ref)
            cluster_owners = [row for row in owners if row["proposed_library_ref"] in member_refs]
            subcontexts.append({
                "subcontext_candidate_ref": cluster_ref,
                "namespace": namespace,
                "name": cluster_name,
                "member_library_refs": member_refs,
                "member_owner_locus_refs": [row["local_context_candidate_ref"] for row in cluster_owners],
                "semantic_module_candidate_refs": sorted({
                    module["semantic_module_ref"] for row in cluster_owners
                    for module in row["semantic_module_candidates"]
                }),
                "evidence_source_refs": sorted({
                    source for row in cluster_owners for module in row["semantic_module_candidates"]
                    for source in module["source_refs"]
                }),
                "boundary_verdict": "MISSING",
                "candidate_state": "REVERSIBLE_SUBCONTEXT_CANDIDATE_UNRATIFIED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
        if clustered_refs != exact_refs:
            missing = sorted(exact_refs - clustered_refs)
            extra = sorted(clustered_refs - exact_refs)
            raise ValueError(f"namespace prior does not partition {namespace}: missing={missing}, extra={extra}")
        archetypes = sorted({row["primary_archetype_ref"] for row in owners})
        modules = sorted({row["semantic_module_candidates"][0]["semantic_module_ref"] for row in owners})
        products = sorted({ref for row in owners for ref in row["product_context_candidate_refs"]})
        collision_count = sum(bool(row["collision_adjudication_candidate_refs"]) for row in owners)
        secondary_archetypes = sorted({ref for row in owners for ref in row["secondary_archetype_refs"]})
        observation_payloads = {
            "one_ubiquitous_language": ("STRUCTURAL_HETEROGENEITY_OBSERVED", {"primary_archetype_refs": archetypes, "primary_module_refs": modules}),
            "one_invariant_and_state_boundary": ("STRUCTURAL_HETEROGENEITY_OBSERVED", {"exact_owner_locus_count": len(owners), "candidate_subcontext_count": len(cluster_refs)}),
            "one_authority_model": ("STRUCTURAL_AUTHORITY_SPAN_OBSERVED", {"product_context_candidate_refs": products, "authority_sensitive_member_count": sum(row["primary_archetype_ref"] == "archetype.boundary.authority_policy_decision" for row in owners)}),
            "coherent_change_cadence": ("DIRECT_CHANGE_CADENCE_EVIDENCE_MISSING", {"module_count": len(modules), "candidate_subcontext_count": len(cluster_refs)}),
            "independent_substitutability": ("QUALIFIED_IMPLEMENTATION_AND_ADOPTION_EVIDENCE_MISSING", {"candidate_subcontext_refs": cluster_refs, "qualified_implementations": 0}),
            "explicit_acl_for_residuals": ("RESIDUAL_ACL_PRESSURE_OBSERVED", {"collision_participating_member_count": collision_count, "secondary_archetype_refs": secondary_archetypes}),
        }
        hypothesis_ref = namespace_hypothesis[namespace]["hypothesis_ref"]
        for test, (state, signals) in observation_payloads.items():
            observations.append({
                "observation_id": f"observation.namespace.{namespace}.{test}",
                "namespace_hypothesis_ref": hypothesis_ref,
                "namespace": namespace,
                "cohesion_test_kind": test,
                "structural_signals": signals,
                "observation_state": state,
                "semantic_or_boundary_verdict": "NOT_SUPPLIED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
        challenges.append({
            "challenge_candidate_ref": f"candidate.namespace_boundary.{namespace}",
            "namespace_hypothesis_ref": hypothesis_ref,
            "namespace": namespace,
            "candidate_direction": direction,
            "candidate_rationale": rationale,
            "exact_member_library_refs": sorted(exact_refs),
            "subcontext_candidate_refs": cluster_refs,
            "observation_refs": [f"observation.namespace.{namespace}.{test}" for test in observation_payloads],
            "required_defeaters": [
                "single_language_used_without_translation", "single_authority_and_state_boundary",
                "shared_change_cadence_and_release", "independent_provider_substitutability",
                "no_hidden_cross_product_or_effect_authority", "two_unrelated_vertical_acceptances",
            ],
            "authority_verdict": "MISSING",
            "candidate_state": "REVERSIBLE_NAMESPACE_BOUNDARY_CHALLENGE_UNRATIFIED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return observations, challenges, subcontexts


def attach_namespace_analysis_to_consolidation_routes(
    routes: list[dict[str, Any]], owner_dockets: list[dict[str, Any]],
    challenges: list[dict[str, Any]], subcontexts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    namespace_by_library = {row["proposed_library_ref"]: row["namespace"] for row in owner_dockets}
    challenge_by_namespace = {row["namespace"]: row["challenge_candidate_ref"] for row in challenges}
    subcontext_by_library = {
        library_ref: row["subcontext_candidate_ref"]
        for row in subcontexts for library_ref in row["member_library_refs"]
    }
    result = []
    for source_row in routes:
        row = dict(source_row)
        library_ref = row["candidate_library_ref"]
        namespace = namespace_by_library[library_ref]
        row["namespace_boundary_challenge_ref"] = challenge_by_namespace[namespace]
        row["namespace_subcontext_candidate_ref"] = subcontext_by_library[library_ref]
        result.append(row)
    return result


def namespace_authority_review_packages(
    challenges: list[dict[str, Any]], subcontexts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_direction: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in challenges:
        by_direction[row["candidate_direction"]].append(row)
    priority_zero = {
        "CROSS_PRODUCT_NAMESPACE_SPLIT_CANDIDATE", "CROSS_PRODUCT_AND_ACL_SPLIT_CANDIDATE",
        "CROSS_PRODUCT_AND_LAYER_SPLIT_CANDIDATE", "KNOWN_MULTI_CONTEXT_PRODUCT_CANDIDATE",
        "SHARED_METHOD_FAMILY_NOT_PRODUCT_CONTEXT_CANDIDATE",
    }
    priority_one = {
        "NEW_PRODUCT_MULTI_CONTEXT_CANDIDATE", "NEW_PRODUCT_WITH_ASSURANCE_IMPORT_CANDIDATE",
        "MULTIPLE_CONTEXTS_WITH_AUTHORITY_ACL_CANDIDATE", "MULTIPLE_CONTEXTS_WITH_EFFECT_ACL_CANDIDATE",
    }
    subcontexts_by_namespace: dict[str, list[str]] = defaultdict(list)
    for row in subcontexts:
        subcontexts_by_namespace[row["namespace"]].append(row["subcontext_candidate_ref"])
    rows = []
    for direction, members in sorted(by_direction.items()):
        priority = "P0_CROSS_PRODUCT_OR_KNOWN_SPLIT" if direction in priority_zero else (
            "P1_NEW_PRODUCT_OR_AUTHORITY_ACL" if direction in priority_one
            else "P2_INTERNAL_CONTEXT_COHESION"
        )
        rows.append({
            "package_ref": "package.namespace_authority." + direction.lower(),
            "candidate_direction": direction,
            "priority_band": priority,
            "namespace_refs": sorted(row["namespace"] for row in members),
            "namespace_challenge_refs": sorted(row["challenge_candidate_ref"] for row in members),
            "subcontext_candidate_refs": sorted(
                ref for row in members for ref in subcontexts_by_namespace[row["namespace"]]
            ),
            "observation_refs": sorted(ref for row in members for ref in row["observation_refs"]),
            "required_evidence_program_refs": [
                "program.context_cohesion.namespace_product_language." + test
                for test in [
                    "one_ubiquitous_language", "one_invariant_and_state_boundary", "one_authority_model",
                    "coherent_change_cadence", "independent_substitutability", "explicit_acl_for_residuals",
                ]
            ],
            "required_outputs": [
                "namespace_boundary_verdict", "subcontext_member_partition",
                "owner_and_authority_receipts", "acl_and_import_edges", "product_boundary_delta_or_refusal",
            ],
            "readiness": "STRUCTURAL_OBSERVATIONS_READY_AUTHORITY_AND_COHESION_EVIDENCE_MISSING",
            "automatic_ratification_forbidden": True,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return sorted(rows, key=lambda row: (row["priority_band"], row["package_ref"]))


def p0_boundary_disposition_graph(
    challenges: list[dict[str, Any]], subcontexts: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Materialize reversible P0 product/context proposals and their falsifiers."""
    challenge_by_namespace = {row["namespace"]: row for row in challenges}
    subcontext_by_ref = {row["subcontext_candidate_ref"]: row for row in subcontexts}
    namespace_candidates = []
    disposition_candidates = []
    negative_twins = []
    twin_kinds = {
        "MONOLITH_COLLAPSE": "Collapse every proposed subcontext into one namespace-sized bounded context.",
        "LIBRARY_PER_CONTEXT_FRAGMENTATION": "Promote every exact library seam into an independently owned bounded context.",
        "PRODUCT_OWNER_INVERSION": "Assign imported or consumer-facing semantics to the downstream product solely because it exposes them.",
        "ACL_ERASURE": "Inline translations and authority handoffs so foreign meanings appear locally owned.",
        "NAMESPACE_NAME_RATIFICATION": "Ratify the product and context boundary from the namespace or surface vocabulary alone.",
        "METHOD_PRODUCTIFICATION": "Treat reusable method mechanics as an independently adoptable product without a product lifecycle or user job.",
    }
    for namespace, priors in sorted(P0_SUBCONTEXT_DISPOSITION_PRIORS.items()):
        challenge = challenge_by_namespace[namespace]
        expected_refs = set(challenge["subcontext_candidate_refs"])
        prior_refs = {f"candidate.subcontext.{namespace}.{name}" for name in priors}
        if prior_refs != expected_refs:
            raise ValueError(f"P0 dispositions do not exactly cover {namespace} subcontexts")
        disposition_refs = []
        owned_products: set[str] = set()
        consumer_products: set[str] = set()
        for name, (disposition, owner_products, consumer_refs, rationale) in sorted(priors.items()):
            subcontext_ref = f"candidate.subcontext.{namespace}.{name}"
            source = subcontext_by_ref[subcontext_ref]
            ref = f"candidate.p0_subcontext_disposition.{namespace}.{name}"
            disposition_refs.append(ref)
            owned_products.update(owner_products)
            consumer_products.update(consumer_refs)
            disposition_candidates.append({
                "disposition_candidate_ref": ref,
                "namespace_boundary_challenge_ref": challenge["challenge_candidate_ref"],
                "namespace": namespace,
                "subcontext_candidate_ref": subcontext_ref,
                "exact_member_library_refs": source["member_library_refs"],
                "candidate_disposition": disposition,
                "candidate_owner_product_refs": owner_products,
                "candidate_consumer_product_refs": consumer_refs,
                "candidate_owner_locus_ref": subcontext_ref,
                "candidate_rationale": rationale,
                "semantic_module_candidate_refs": source["semantic_module_candidate_refs"],
                "evidence_source_refs": source["evidence_source_refs"],
                "required_authority_receipts": [
                    "product_boundary_authority", "bounded_context_owner_authority",
                    "member_semantic_applicability", "acl_or_import_contract_where_applicable",
                    "independent_adoption_and_change_evidence", "two_unrelated_vertical_acceptances",
                ],
                "boundary_verdict": "MISSING",
                "owner_verdict": "MISSING",
                "candidate_state": "REVERSIBLE_P0_SUBCONTEXT_DISPOSITION_UNRATIFIED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
        relation_candidates = []
        for suffix, source_ref, target_ref, relationship, member_names in P0_RELATION_PRIORS[namespace]:
            relation_candidates.append({
                "relation_candidate_ref": f"candidate.p0_relation.{namespace}.{suffix}",
                "source_ref": source_ref,
                "target_ref": target_ref,
                "relationship_candidate": relationship,
                "subcontext_candidate_refs": [f"candidate.subcontext.{namespace}.{name}" for name in member_names],
                "authority_transfer_forbidden": True,
                "boundary_verdict": "MISSING",
            })
        namespace_ref = f"candidate.p0_namespace_disposition.{namespace}"
        namespace_candidates.append({
            "namespace_disposition_candidate_ref": namespace_ref,
            "namespace": namespace,
            "namespace_boundary_challenge_ref": challenge["challenge_candidate_ref"],
            "candidate_direction": challenge["candidate_direction"],
            "exact_member_library_refs": challenge["exact_member_library_refs"],
            "subcontext_disposition_candidate_refs": disposition_refs,
            "candidate_owned_product_refs": sorted(owned_products),
            "candidate_consumer_product_refs": sorted(consumer_products),
            "relation_candidates": relation_candidates,
            "candidate_nonownership_laws": [
                "a namespace is not a bounded context or product",
                "a downstream consumer does not own imported meaning",
                "an ACL translates meaning and authority but does not erase either",
                "a shared method family is not a product without an independent lifecycle and user job",
                "structural partitioning and source co-location do not ratify a boundary",
            ],
            "required_negative_twin_refs": [f"negative_twin.p0_boundary.{namespace}.{kind.lower()}" for kind in twin_kinds],
            "boundary_verdict": "MISSING",
            "candidate_state": "REVERSIBLE_P0_NAMESPACE_DISPOSITION_UNRATIFIED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
        for kind, mutation in twin_kinds.items():
            negative_twins.append({
                "negative_twin_ref": f"negative_twin.p0_boundary.{namespace}.{kind.lower()}",
                "namespace_disposition_candidate_ref": namespace_ref,
                "namespace": namespace,
                "mutation_kind": kind,
                "mutation": mutation,
                "exact_member_library_refs": challenge["exact_member_library_refs"],
                "expected_refusal_or_counterevidence": {
                    "MONOLITH_COLLAPSE": "different language, invariant, lifecycle, authority or independent change pressure",
                    "LIBRARY_PER_CONTEXT_FRAGMENTATION": "shared lifecycle and authority evidence plus excessive ACL or transaction cost",
                    "PRODUCT_OWNER_INVERSION": "provider or consumer exposure without semantic authority",
                    "ACL_ERASURE": "foreign identity, authority, loss or refusal semantics become untraceable",
                    "NAMESPACE_NAME_RATIFICATION": "no owner receipt, independent adoption evidence or executed vertical acceptance",
                    "METHOD_PRODUCTIFICATION": "no sovereign product question, actor job, adoption lifecycle or product-level exit contract",
                }[kind],
                "execution_state": "UNEXECUTED_SEMANTIC_AND_AUTHORITY_EVIDENCE_REQUIRED",
                "negative_twin_result": "MISSING",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
    return namespace_candidates, disposition_candidates, negative_twins


def p0_product_dossier_bindings(
    namespace_candidates: list[dict[str, Any]], disposition_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    readiness_rows = load_jsonl(PRODUCT_READINESS)
    readiness_by_ref: dict[str, dict[str, Any]] = {}
    for row in readiness_rows:
        readiness_by_ref[row["candidate_id"]] = row
        if row.get("local_subject_ref"):
            readiness_by_ref[row["local_subject_ref"]] = row
    product_refs = sorted({
        ref for row in namespace_candidates
        for ref in row["candidate_owned_product_refs"] + row["candidate_consumer_product_refs"]
    })
    disposition_refs_by_product: dict[str, set[str]] = defaultdict(set)
    for row in disposition_candidates:
        for product_ref in row["candidate_owner_product_refs"] + row["candidate_consumer_product_refs"]:
            disposition_refs_by_product[product_ref].add(row["disposition_candidate_ref"])
    relation_refs_by_product: dict[str, set[str]] = defaultdict(set)
    for row in namespace_candidates:
        for relation in row["relation_candidates"]:
            for product_ref in product_refs:
                if product_ref in {relation["source_ref"], relation["target_ref"]}:
                    relation_refs_by_product[product_ref].add(relation["relation_candidate_ref"])
    result = []
    for product_ref in product_refs:
        readiness = readiness_by_ref.get(product_ref)
        if readiness:
            dossier = readiness["product_specific_ddd"]
            binding_state = "COMPLETE_CANDIDATE_DOSSIER_PRESENT_UNRATIFIED"
            readiness_ref = readiness["record_id"]
            dossier_ref = dossier["dossier_ref"]
            dossier_status = dossier["status"]
            boundary_verdict = readiness["boundary_verdict"]
            boundary_adjudication = readiness["boundary_adjudication"]
            ratification = readiness["ratification"]
            build_readiness = readiness["build_readiness"]
        else:
            binding_state = "PRODUCT_DOSSIER_AND_READINESS_RECORD_MISSING"
            readiness_ref = None
            dossier_ref = None
            dossier_status = "MISSING"
            boundary_verdict = "MISSING"
            boundary_adjudication = "MISSING"
            ratification = "MISSING"
            build_readiness = "NOT_BUILD_READY"
        result.append({
            "binding_ref": "binding.p0_product_dossier." + product_ref.replace("candidate.product.", "").replace("product.", ""),
            "product_ref": product_ref,
            "product_readiness_record_ref": readiness_ref,
            "product_ddd_dossier_ref": dossier_ref,
            "product_ddd_dossier_status": dossier_status,
            "product_boundary_verdict_candidate": boundary_verdict,
            "product_boundary_adjudication_state": boundary_adjudication,
            "product_ratification_state": ratification,
            "product_build_readiness": build_readiness,
            "subcontext_disposition_candidate_refs": sorted(disposition_refs_by_product[product_ref]),
            "relation_candidate_refs": sorted(relation_refs_by_product[product_ref]),
            "required_authority_work": [
                "compare each proposed subcontext with the dossier inside/outside boundary",
                "compare ubiquitous language and homonyms with the dossier published language",
                "compare invariants, aggregates and lifecycle with the proposed owner locus",
                "verify every consumer/import/ACL edge against the dossier context map",
                "obtain product and bounded-context owner authority receipts",
                "execute independent adoption, exit and two-unrelated-vertical tests",
            ],
            "binding_state": binding_state,
            "structural_dossier_presence_is_boundary_proof": False,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return result


def attach_p0_dossier_bindings(
    dispositions: list[dict[str, Any]], bindings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    binding_by_product = {row["product_ref"]: row["binding_ref"] for row in bindings}
    result = []
    for source in dispositions:
        row = dict(source)
        row["product_dossier_binding_refs"] = sorted({
            binding_by_product[ref]
            for ref in row["candidate_owner_product_refs"] + row["candidate_consumer_product_refs"]
        })
        result.append(row)
    return result


def p0_downstream_route_projections(
    owner_dockets: list[dict[str, Any]], consolidation_routes: list[dict[str, Any]],
    contract_dockets: list[dict[str, Any]], intake_routes: list[dict[str, Any]],
    disposition_candidates: list[dict[str, Any]], namespace_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    disposition_by_library = {
        library_ref: row for row in disposition_candidates for library_ref in row["exact_member_library_refs"]
    }
    namespace_candidate_by_namespace = {row["namespace"]: row for row in namespace_candidates}
    consolidation_by_library = {row["candidate_library_ref"]: row for row in consolidation_routes}
    contract_by_library = {row["candidate_library_ref"]: row for row in contract_dockets}
    intake_by_library = {row["candidate_library_ref"]: row for row in intake_routes}
    rows = []
    for owner in owner_dockets:
        library_ref = owner["proposed_library_ref"]
        disposition = disposition_by_library.get(library_ref)
        namespace_candidate = namespace_candidate_by_namespace.get(owner["namespace"])
        rows.append({
            "projection_ref": "projection.p0_boundary_route." + library_ref.split("library.", 1)[-1].replace(".", "-"),
            "candidate_library_ref": library_ref,
            "namespace": owner["namespace"],
            "priority_zero_member": disposition is not None,
            "namespace_disposition_candidate_ref": namespace_candidate["namespace_disposition_candidate_ref"] if namespace_candidate else None,
            "subcontext_disposition_candidate_ref": disposition["disposition_candidate_ref"] if disposition else None,
            "candidate_owner_product_refs": disposition["candidate_owner_product_refs"] if disposition else [],
            "candidate_consumer_product_refs": disposition["candidate_consumer_product_refs"] if disposition else [],
            "product_dossier_binding_refs": disposition["product_dossier_binding_refs"] if disposition else [],
            "owner_docket_ref": owner["docket_id"],
            "owner_adjudication_candidate_ref": owner["owner_adjudication_candidate_ref"],
            "context_consolidation_route_ref": consolidation_by_library[library_ref]["route_id"],
            "provisional_contract_docket_ref": contract_by_library[library_ref]["docket_id"],
            "p5_intake_route_ref": intake_by_library[library_ref]["intake_route_id"],
            "compiler_admission_state": "WITHHELD_BOUNDARY_AND_OWNER_AUTHORITY_MISSING",
            "projection_law": "A reversible P0 boundary candidate may prioritize exact owner and contract review but cannot promote a candidate library into P5 or select an implementation.",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return rows


def p0_boundary_finding_projections(
    boundary_routes: list[dict[str, Any]], route_projections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    p0_by_library = {row["candidate_library_ref"]: row for row in route_projections if row["priority_zero_member"]}
    rows = []
    for route in boundary_routes:
        related = [p0_by_library[ref] for ref in route["slice_candidate_universe_refs"] if ref in p0_by_library]
        rows.append({
            "projection_ref": "projection.p0_boundary_finding." + route["boundary_finding_ref"].split("finding.", 1)[-1].replace(".", "-"),
            "boundary_finding_ref": route["boundary_finding_ref"],
            "boundary_challenge_route_ref": route["route_id"],
            "priority_zero_related_library_refs": sorted(row["candidate_library_ref"] for row in related),
            "namespace_disposition_candidate_refs": sorted({row["namespace_disposition_candidate_ref"] for row in related}),
            "subcontext_disposition_candidate_refs": sorted({row["subcontext_disposition_candidate_ref"] for row in related}),
            "projection_state": "P0_REVIEW_CONTEXT_PRESENT_UNRATIFIED" if related else "NO_P0_LIBRARY_IN_SLICE_CANDIDATE_UNIVERSE",
            "direct_relevance_or_boundary_claim": False,
            "projection_law": "Slice-universe intersection supplies review context only; it does not prove that the boundary finding concerns any projected library or validates its disposition.",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return rows


DAG_STAGES = [
    ("stage.boundary.00_exact_inventory", [], "Preserve every source finding and proposed seam with exact provenance."),
    ("stage.boundary.01_semantic_quotient", ["stage.boundary.00_exact_inventory"], "Assign reusable review archetypes without semantic merge."),
    ("stage.boundary.02_collision_tests", ["stage.boundary.01_semantic_quotient"], "Falsify homonym, overlap and common-mechanic unification."),
    ("stage.boundary.03_owner_candidates", ["stage.boundary.02_collision_tests"], "Name accountable semantic owners and resolve cross-slice conflicts."),
    ("stage.boundary.04_product_boundary", ["stage.boundary.03_owner_candidates"], "Adjudicate retain/split/new-product/import/capability/composition dispositions."),
    ("stage.boundary.05_library_boundary", ["stage.boundary.04_product_boundary"], "Ratify or reject exact library responsibilities and local residuals."),
    ("stage.boundary.06_contract_lowering", ["stage.boundary.05_library_boundary"], "Generate exact types, laws, operations, refusals, ports and compatibility contracts."),
    ("stage.boundary.07_implementation_qualification", ["stage.boundary.06_contract_lowering"], "Bind two independent qualified implementations or keep compiler refusal."),
    ("stage.boundary.08_vertical_acceptance", ["stage.boundary.07_implementation_qualification"], "Execute unrelated vertical acceptance, exit, recovery and evidence gates."),
]


def dag_rows() -> list[dict[str, Any]]:
    return [{"stage_ref": ref, "dependency_refs": deps, "objective": objective,
             "entry_state": "UNEXECUTED", "exit_receipt_required": True,
             "canonical_gaps_closed": 0, "completion_claim": False}
            for ref, deps, objective in DAG_STAGES]


def ratification_packages(
    archetypes: list[dict[str, Any]], boundary_kinds: list[dict[str, Any]],
    collision_families: list[dict[str, Any]], contract_archetypes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for row in collision_families:
        rows.append({
            "package_id": "package.ratification." + row["collision_family_ref"].replace("collision_family.", "collision_"),
            "package_kind": "CROSS_NAMESPACE_COLLISION_REVIEW",
            "subject_refs": row["collision_refs"],
            "dependency_stage_ref": "stage.boundary.01_semantic_quotient",
            "next_stage_ref": "stage.boundary.02_collision_tests",
            "required_outputs": [
                "meaning_partitions", "homonym_dispositions", "shared_mechanic_profiles",
                "merge_replacement_edges_or_explicit_refusal",
            ],
            "status": "OPEN_UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False,
        })
    for row in archetypes:
        if not row["member_count"]:
            continue
        rows.append({"package_id": "package.ratification." + row["archetype_ref"].split(".")[-1],
                     "package_kind": "LIBRARY_SEAM_ARCHETYPE_REVIEW", "subject_refs": row["member_library_refs"],
                     "dependency_stage_ref": "stage.boundary.02_collision_tests", "next_stage_ref": "stage.boundary.03_owner_candidates",
                     "input_artifact_kinds": ["owner_candidate_docket", "owner_adjudication_candidate", "owner_counterfactual_challenge", "collision_adjudication_candidate", "collision_meaning_partition", "collision_negative_twin", "context_consolidation_route"],
                     "required_outputs": ["applicability_matrix", "owner_candidate_docket_verdicts", "collision_dispositions", "member_local_residuals"],
                     "status": "OPEN_UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False})
    for row in boundary_kinds:
        rows.append({"package_id": "package.ratification." + row["boundary_kind_ref"].split(".")[-1].lower(),
                     "package_kind": "PRODUCT_CAPABILITY_BOUNDARY_REVIEW", "subject_refs": row["source_finding_refs"],
                     "dependency_stage_ref": "stage.boundary.03_owner_candidates", "next_stage_ref": "stage.boundary.04_product_boundary",
                     "input_artifact_kinds": ["boundary_finding_route", "boundary_challenge_evidence_route", "owner_adjudication_candidate", "owner_counterfactual_challenge", "collision_adjudication_candidate", "collision_negative_twin", "context_consolidation_hypothesis"],
                     "required_outputs": ["boundary_counterfactuals", "independent_adoption_evidence", "owner_verdicts", "replacement_import_edges"],
                     "status": "OPEN_UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False})
    for row in contract_archetypes:
        rows.append({
            "package_id": "package.ratification.contract_" + row["semantic_archetype_ref"].split(".")[-1],
            "package_kind": "PROVISIONAL_EXACT_CONTRACT_LOWERING_REVIEW",
            "subject_refs": row["contract_docket_refs"],
            "dependency_stage_ref": "stage.boundary.05_library_boundary",
            "next_stage_ref": "stage.boundary.06_contract_lowering",
            "required_outputs": [
                "exact_contract_facets", "authority_symbol_receipts", "typed_refusal_precedence",
                "compiler_ir_and_lowering_receipts", "p5_intake_delta",
            ],
            "status": "OPEN_UPSTREAM_BLOCKED", "canonical_gaps_closed": 0, "completion_claim": False,
        })
    return sorted(rows, key=lambda r: r["package_id"])


def build() -> dict[str, Any]:
    findings = all_findings()
    vacancies = vacancy_routes(findings)
    archetypes = archetype_rows(vacancies)
    boundaries = boundary_routes(findings)
    kinds = boundary_kind_rows(boundaries)
    collisions = collision_candidates(vacancies)
    collision_dockets = collision_review_dockets(collisions)
    collision_families = collision_family_rows(collision_dockets)
    owner_dockets = owner_candidate_dockets(findings, vacancies)
    meaning_partitions = collision_meaning_partitions(collisions, findings, vacancies, owner_dockets)
    collision_adjudications = collision_adjudication_candidates(collisions, meaning_partitions)
    owner_dockets = attach_collision_evidence_to_owner_dockets(owner_dockets, collision_adjudications)
    owner_adjudications = owner_adjudication_candidates(owner_dockets)
    owner_dockets = attach_owner_adjudication_candidates(owner_dockets, owner_adjudications)
    owner_contexts = owner_context_rows(owner_dockets)
    negative_twins = collision_negative_twins(collision_adjudications, meaning_partitions)
    owner_challenges = owner_counterfactual_challenges(owner_adjudications, owner_dockets)
    consolidation_hypotheses, consolidation_routes = context_consolidation_graph(owner_dockets)
    namespace_observations, namespace_challenges, namespace_subcontexts = namespace_boundary_analysis(
        consolidation_hypotheses, owner_dockets,
    )
    consolidation_routes = attach_namespace_analysis_to_consolidation_routes(
        consolidation_routes, owner_dockets, namespace_challenges, namespace_subcontexts,
    )
    namespace_review_packages = namespace_authority_review_packages(
        namespace_challenges, namespace_subcontexts,
    )
    p0_namespace_dispositions, p0_subcontext_dispositions, p0_boundary_negative_twins = p0_boundary_disposition_graph(
        namespace_challenges, namespace_subcontexts,
    )
    p0_product_dossier_bindings_rows = p0_product_dossier_bindings(
        p0_namespace_dispositions, p0_subcontext_dispositions,
    )
    p0_subcontext_dispositions = attach_p0_dossier_bindings(
        p0_subcontext_dispositions, p0_product_dossier_bindings_rows,
    )
    boundary_challenge_routes = boundary_challenge_evidence_routes(
        boundaries, findings, owner_dockets, owner_adjudications, collision_adjudications,
        negative_twins, consolidation_routes,
    )
    negative_twin_receipts = negative_twin_gate_receipts(negative_twins)
    owner_evidence_vacancies, owner_evidence_programs = owner_challenge_evidence_vacancies(
        owner_challenges, owner_dockets,
    )
    cohesion_vacancies, cohesion_programs = context_cohesion_evidence_vacancies(
        consolidation_hypotheses, owner_dockets,
    )
    contract_dockets = provisional_contract_dockets(vacancies, owner_dockets, collision_dockets)
    contract_archetypes = contract_lowering_archetypes(contract_dockets)
    intake_routes = p5_intake_routes(contract_dockets)
    p0_route_projections = p0_downstream_route_projections(
        owner_dockets, consolidation_routes, contract_dockets, intake_routes,
        p0_subcontext_dispositions, p0_namespace_dispositions,
    )
    p0_finding_projections = p0_boundary_finding_projections(
        boundary_challenge_routes, p0_route_projections,
    )
    packages = ratification_packages(archetypes, kinds, collision_families, contract_archetypes)
    frontier = execution_frontier(packages, owner_dockets)
    admission_audit = implementation_vertical_admission_audit(
        vacancies, collision_families, owner_dockets, contract_dockets, frontier,
    )
    inventory = [{**row, "inventory_state": "SOURCE_FINDING_PRESERVED_UNRATIFIED"} for row in findings]
    summary = {
        "program_id": "program.cross-slice-boundary-frontier.v1", "as_of": AS_OF,
        "source_semantic_slices": len({row["source_slice"] for row in findings}),
        "exact_findings": len(findings), "proposed_library_seams": len(vacancies),
        "non_vacancy_boundary_findings": len(boundaries),
        "semantic_review_archetypes": len(archetypes), "nonempty_semantic_review_archetypes": sum(row["member_count"] > 0 for row in archetypes),
        "boundary_kinds": len(kinds), "cross_namespace_collision_candidates": len(collisions),
        "collision_review_families": len(collision_families),
        "collision_meaning_partitions": len(meaning_partitions),
        "collision_adjudication_candidates": len(collision_adjudications),
        "collision_authority_verdicts": 0,
        "owner_candidate_dockets": len(owner_dockets),
        "owner_dockets_blocked_by_collision_authority": sum(
            row["owner_review_readiness"] == "BLOCKED_COLLISION_AUTHORITY_VERDICTS_MISSING"
            for row in owner_dockets
        ),
        "owner_dockets_ready_for_authority_review": sum(
            row["owner_review_readiness"] == "EVIDENCE_PACKET_READY_OWNER_AUTHORITY_VERDICT_MISSING"
            for row in owner_dockets
        ),
        "owner_adjudication_candidates": len(owner_adjudications),
        "owner_authority_verdicts": 0,
        "collision_negative_twins": len(negative_twins),
        "executed_collision_negative_twins": 0,
        "executed_collision_structural_gates": len(negative_twin_receipts),
        "owner_counterfactual_challenges": len(owner_challenges),
        "executed_owner_counterfactual_challenges": 0,
        "owner_challenge_evidence_vacancies": len(owner_evidence_vacancies),
        "owner_challenge_evidence_programs": len(owner_evidence_programs),
        "context_consolidation_hypotheses": len(consolidation_hypotheses),
        "context_consolidation_routes": len(consolidation_routes),
        "context_boundary_verdicts": 0,
        "namespace_structural_observations": len(namespace_observations),
        "namespace_boundary_challenge_candidates": len(namespace_challenges),
        "namespace_subcontext_candidates": len(namespace_subcontexts),
        "namespace_boundary_authority_verdicts": 0,
        "namespace_authority_review_packages": len(namespace_review_packages),
        "p0_namespace_disposition_candidates": len(p0_namespace_dispositions),
        "p0_subcontext_disposition_candidates": len(p0_subcontext_dispositions),
        "p0_exact_library_members": sum(row["priority_zero_member"] for row in p0_route_projections),
        "p0_boundary_negative_twins": len(p0_boundary_negative_twins),
        "p0_downstream_route_projections": len(p0_route_projections),
        "p0_boundary_finding_projections": len(p0_finding_projections),
        "p0_boundary_finding_projections_with_review_context": sum(
            bool(row["priority_zero_related_library_refs"]) for row in p0_finding_projections
        ),
        "p0_boundary_authority_verdicts": 0,
        "p0_product_dossier_bindings": len(p0_product_dossier_bindings_rows),
        "p0_complete_candidate_dossiers_present": sum(
            row["binding_state"] == "COMPLETE_CANDIDATE_DOSSIER_PRESENT_UNRATIFIED"
            for row in p0_product_dossier_bindings_rows
        ),
        "p0_missing_product_dossiers": sum(
            row["binding_state"] == "PRODUCT_DOSSIER_AND_READINESS_RECORD_MISSING"
            for row in p0_product_dossier_bindings_rows
        ),
        "context_cohesion_evidence_vacancies": len(cohesion_vacancies),
        "context_cohesion_evidence_programs": len(cohesion_programs),
        "boundary_challenge_evidence_routes": len(boundary_challenge_routes),
        "boundary_routes_with_candidate_context": sum(bool(row["slice_candidate_universe_refs"]) for row in boundary_challenge_routes),
        "boundary_routes_without_proposed_seam_universe": sum(not row["slice_candidate_universe_refs"] for row in boundary_challenge_routes),
        "boundary_authority_verdicts": 0,
        "local_context_candidates": len(owner_contexts),
        "semantic_module_grounding_gaps": sum(row["semantic_module_grounding_gap"] for row in owner_dockets),
        "provisional_contract_lowering_dockets": len(contract_dockets),
        "contract_lowering_archetypes": len(contract_archetypes),
        "p5_intake_routes": len(intake_routes),
        "ready_review_packages": sum(row["readiness"] == "STRUCTURAL_GATES_REFUSED_AUTHORITY_VERDICT_MISSING" for row in frontier),
        "partial_owner_review_packages": sum(row["readiness"] == "PARTIAL_OWNER_EVIDENCE_READY_AUTHORITY_VERDICT_MISSING" for row in frontier),
        "implementation_work_admissible": False,
        "vertical_work_admissible": False,
        "owner_selections": 0,
        "ratification_packages": len(packages), "ratification_dag_stages": len(DAG_STAGES),
        "owner_decisions": 0, "ratified_product_boundaries": 0, "ratified_library_boundaries": 0,
        "exact_contracts_selected": 0, "qualified_implementations": 0, "vertical_acceptances": 0,
        "canonical_gaps_closed": 0, "completion_claim": False,
    }
    return {"inventory": inventory, "vacancy_routes": vacancies, "archetypes": archetypes,
            "boundary_routes": boundaries, "boundary_kinds": kinds, "collisions": collisions,
            "collision_dockets": collision_dockets, "collision_families": collision_families,
            "meaning_partitions": meaning_partitions, "collision_adjudications": collision_adjudications,
            "owner_dockets": owner_dockets, "owner_contexts": owner_contexts,
            "owner_adjudications": owner_adjudications,
            "negative_twins": negative_twins, "owner_challenges": owner_challenges,
            "consolidation_hypotheses": consolidation_hypotheses,
            "consolidation_routes": consolidation_routes,
            "namespace_observations": namespace_observations,
            "namespace_challenges": namespace_challenges,
            "namespace_subcontexts": namespace_subcontexts,
            "namespace_review_packages": namespace_review_packages,
            "p0_namespace_dispositions": p0_namespace_dispositions,
            "p0_subcontext_dispositions": p0_subcontext_dispositions,
            "p0_boundary_negative_twins": p0_boundary_negative_twins,
            "p0_route_projections": p0_route_projections,
            "p0_finding_projections": p0_finding_projections,
            "p0_product_dossier_bindings": p0_product_dossier_bindings_rows,
            "boundary_challenge_routes": boundary_challenge_routes,
            "negative_twin_receipts": negative_twin_receipts,
            "owner_evidence_vacancies": owner_evidence_vacancies,
            "owner_evidence_programs": owner_evidence_programs,
            "cohesion_vacancies": cohesion_vacancies, "cohesion_programs": cohesion_programs,
            "contract_dockets": contract_dockets, "contract_archetypes": contract_archetypes,
            "intake_routes": intake_routes,
            "dag": dag_rows(), "packages": packages, "frontier": frontier,
            "admission_audit": admission_audit, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "exact-finding-inventory.jsonl": "".join(canonical(r) + "\n" for r in built["inventory"]),
        "vacancy-semantic-quotients.jsonl": "".join(canonical(r) + "\n" for r in built["archetypes"]),
        "vacancy-routes.jsonl": "".join(canonical(r) + "\n" for r in built["vacancy_routes"]),
        "boundary-decision-quotients.jsonl": "".join(canonical(r) + "\n" for r in built["boundary_kinds"]),
        "boundary-finding-routes.jsonl": "".join(canonical(r) + "\n" for r in built["boundary_routes"]),
        "cross-namespace-collision-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["collisions"]),
        "collision-review-dockets.jsonl": "".join(canonical(r) + "\n" for r in built["collision_dockets"]),
        "collision-review-families.jsonl": "".join(canonical(r) + "\n" for r in built["collision_families"]),
        "collision-meaning-partitions.jsonl": "".join(canonical(r) + "\n" for r in built["meaning_partitions"]),
        "collision-adjudication-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["collision_adjudications"]),
        "owner-candidate-dockets.jsonl": "".join(canonical(r) + "\n" for r in built["owner_dockets"]),
        "owner-context-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["owner_contexts"]),
        "owner-adjudication-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["owner_adjudications"]),
        "collision-negative-twins.jsonl": "".join(canonical(r) + "\n" for r in built["negative_twins"]),
        "owner-counterfactual-challenges.jsonl": "".join(canonical(r) + "\n" for r in built["owner_challenges"]),
        "context-consolidation-hypotheses.jsonl": "".join(canonical(r) + "\n" for r in built["consolidation_hypotheses"]),
        "context-consolidation-routes.jsonl": "".join(canonical(r) + "\n" for r in built["consolidation_routes"]),
        "namespace-structural-observations.jsonl": "".join(canonical(r) + "\n" for r in built["namespace_observations"]),
        "namespace-boundary-challenge-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["namespace_challenges"]),
        "namespace-subcontext-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["namespace_subcontexts"]),
        "namespace-authority-review-packages.jsonl": "".join(canonical(r) + "\n" for r in built["namespace_review_packages"]),
        "p0-namespace-disposition-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["p0_namespace_dispositions"]),
        "p0-subcontext-disposition-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["p0_subcontext_dispositions"]),
        "p0-boundary-negative-twins.jsonl": "".join(canonical(r) + "\n" for r in built["p0_boundary_negative_twins"]),
        "p0-downstream-route-projections.jsonl": "".join(canonical(r) + "\n" for r in built["p0_route_projections"]),
        "p0-boundary-finding-projections.jsonl": "".join(canonical(r) + "\n" for r in built["p0_finding_projections"]),
        "p0-product-dossier-bindings.jsonl": "".join(canonical(r) + "\n" for r in built["p0_product_dossier_bindings"]),
        "boundary-challenge-evidence-routes.jsonl": "".join(canonical(r) + "\n" for r in built["boundary_challenge_routes"]),
        "collision-negative-twin-gate-receipts.jsonl": "".join(canonical(r) + "\n" for r in built["negative_twin_receipts"]),
        "owner-challenge-evidence-vacancies.jsonl": "".join(canonical(r) + "\n" for r in built["owner_evidence_vacancies"]),
        "owner-challenge-evidence-programs.jsonl": "".join(canonical(r) + "\n" for r in built["owner_evidence_programs"]),
        "context-cohesion-evidence-vacancies.jsonl": "".join(canonical(r) + "\n" for r in built["cohesion_vacancies"]),
        "context-cohesion-evidence-programs.jsonl": "".join(canonical(r) + "\n" for r in built["cohesion_programs"]),
        "provisional-contract-lowering-dockets.jsonl": "".join(canonical(r) + "\n" for r in built["contract_dockets"]),
        "contract-lowering-archetypes.jsonl": "".join(canonical(r) + "\n" for r in built["contract_archetypes"]),
        "p5-intake-routes.jsonl": "".join(canonical(r) + "\n" for r in built["intake_routes"]),
        "execution-frontier.jsonl": "".join(canonical(r) + "\n" for r in built["frontier"]),
        "implementation-vertical-admission-audit.json": json.dumps(built["admission_audit"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "ratification-dag.jsonl": "".join(canonical(r) + "\n" for r in built["dag"]),
        "ratification-packages.jsonl": "".join(canonical(r) + "\n" for r in built["packages"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.cross-slice-boundary-frontier.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    summary = build()["summary"]
    print(
        f"BUILD PASS cross-slice boundary frontier: {summary['exact_findings']} findings, "
        f"{summary['proposed_library_seams']} exact seams, {summary['semantic_review_archetypes']} semantic quotients, "
        f"{summary['owner_candidate_dockets']} owner dockets, {summary['cross_namespace_collision_candidates']} "
        f"collisions in {summary['collision_review_families']} families, "
        f"{summary['provisional_contract_lowering_dockets']} provisional contract/lowering dockets, "
        f"{summary['ratification_packages']} ratification packages"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
