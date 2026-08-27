#!/usr/bin/env python3
"""Add the graph-analysis workbench without productifying graph methods."""

from __future__ import annotations

from typing import Any


PRODUCT = "product.graph_analysis_workbench"
SEMANTIC_OWNER = "semantic.graph_analysis_workbench"
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

SOURCE_ROWS = [
    {
        "source_id": "evidence.graph_workbench.gephi_srs",
        "source_class": "official_product_documentation",
        "title": "Gephi Software Requirements Specification",
        "publisher": "Gephi Consortium",
        "uri": "https://gephi.org/users/gephi_srs_document.pdf",
        "retrieved_at": "2026-08-27",
        "claim": "Defines an independently operated graph-analysis application with projects, multiple workspaces, import, algorithm/statistics execution, plugins and graph/result export.",
        "scope_limit": "One implementation does not prove universal graph semantics, enterprise suitability, portability or the proposed SAN product boundary.",
    },
    {
        "source_id": "evidence.graph_workbench.cytoscape_manual",
        "source_class": "official_product_documentation",
        "title": "Cytoscape User Manual",
        "publisher": "Cytoscape Consortium",
        "uri": "https://manual.cytoscape.org/en/stable/",
        "retrieved_at": "2026-08-27",
        "claim": "Documents a separately adopted network-analysis application with session, network/table import, analysis, visualization, app extension and export/share lifecycles.",
        "scope_limit": "Cytoscape's biomedical ecosystem and UI do not establish generic enterprise authority, exact method equivalence or a portable provider contract.",
    },
    {
        "source_id": "evidence.graph_workbench.neo4j_management",
        "source_class": "official_product_documentation",
        "title": "Neo4j Graph Data Science: Graph management",
        "publisher": "Neo4j",
        "uri": "https://neo4j.com/docs/graph-data-science/current/management-ops/",
        "retrieved_at": "2026-08-27",
        "claim": "Documents named analytical graph catalogs, projection, mutation, access control, backup/restore, write-back and export lifecycle in a commercial graph-analytics offering.",
        "scope_limit": "Provider documentation proves one product surface only; it does not transfer database, ontology, source-truth or business-decision authority to the workbench.",
    },
    {
        "source_id": "evidence.graph_workbench.neo4j_export",
        "source_class": "official_product_documentation",
        "title": "Neo4j Graph Data Science: Export to a new database",
        "publisher": "Neo4j",
        "uri": "https://neo4j.com/docs/graph-data-science/current/management-ops/graph-export/export-db/",
        "retrieved_at": "2026-08-27",
        "claim": "Defines explicit export of a projected graph and algorithm mutations for archiving, inspection and organizational sharing.",
        "scope_limit": "A provider-specific database export is not a complete portable exit contract and does not prove semantic equivalence across carriers.",
    },
    {
        "source_id": "evidence.graph_workbench.graphalytics",
        "source_class": "official_benchmark_specification",
        "title": "LDBC Graphalytics Benchmark Specification",
        "publisher": "Linked Data Benchmark Council",
        "uri": "https://ldbcouncil.org/ldbc_graphalytics_docs/graphalytics_spec.pdf",
        "retrieved_at": "2026-08-27",
        "claim": "Defines graph-analytics workloads, datasets, validation and benchmark reporting that separate workload identity from implementation claims.",
        "scope_limit": "Benchmark conformance is workload and environment scoped and does not prove a product lifecycle, all method semantics or production fitness.",
    },
]

KEYS = [
    "workspace_lifecycle", "graph_occurrence_profile", "algorithm_plan",
    "run_evidence", "benchmark_workload", "result_comparison", "publication_review",
]

CAPABILITIES = {
    "workspace_lifecycle": "Open, edition, branch, archive and exit a graph-analysis workspace without owning source or ontology truth.",
    "graph_occurrence_profile": "Bind an exact graph occurrence, projection loss, topology/property/time profile and input cut.",
    "algorithm_plan": "Compile selected graph methods, parameters, randomness, approximation, backend and finite budgets into an explicit plan.",
    "run_evidence": "Execute and reconcile a graph-analysis run while preserving attempts, cancellation, partiality, resource use and result evidence.",
    "benchmark_workload": "Identify benchmark workload, dataset, scale, validation and environment without generalizing the resulting qualification.",
    "result_comparison": "Compare graph results only under compatible graph cuts, method profiles, tolerances and evidence scope.",
    "publication_review": "Review, publish, retract, recall and export bounded graph-analysis results without conferring decision authority.",
}

CONCRETE = {
    "workspace_lifecycle": [],
    "graph_occurrence_profile": ["library.method_kernels.graph_semantics"],
    "algorithm_plan": [
        "library.method_kernels.graph_traversal_path_methods",
        "library.method_kernels.graph_centrality_methods",
        "library.method_kernels.graph_community_methods",
        "library.method_kernels.graph_semiring_kernel_facade",
    ],
    "run_evidence": [],
    "benchmark_workload": [],
    "result_comparison": [],
    "publication_review": [],
}

QUALIFICATION = {
    "graph_occurrence_profile": ["receipt.method_kernel.graph_semantics"],
    "algorithm_plan": [
        "receipt.method_kernel.graph_traversal_paths", "receipt.method_kernel.graph_centrality",
        "receipt.method_kernel.graph_community", "receipt.method_kernel.graph_semiring_kernels",
    ],
}


def local_library(key: str) -> str:
    return f"library.analytics_graph_workbench.{key}"


def local_capability(key: str) -> str:
    return f"capability.analytics_graph_workbench.{key}"


def product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "For an exact graph occurrence and declared analytical question, what reproducible plan, run, bounded result, comparison and publication can be managed without turning graph structure or algorithm output into ontology truth, causality, identity, policy or operational authority?",
        "users": ["graph_analyst", "data_scientist", "network_researcher", "graph_data_steward", "method_reviewer", "result_publisher", "assurance_reviewer", "downstream_decision_owner"],
        "harmed_parties": ["represented_person_or_organization", "misclassified_or_ranked_subject", "source_owner", "result_consumer", "operator", "affected_decision_subject"],
        "jobs": ["Create an editioned analysis workspace; bind graph projections and profiles; select and configure graph methods; execute reproducible bounded runs; compare and review results; publish or recall scoped evidence; export the complete workspace without absorbing ontology, storage, prediction, decision or effect authority."],
        "outcomes": ["editioned_workspace", "loss_explicit_graph_occurrence", "compiled_algorithm_plan", "reproducible_run_receipt", "scoped_benchmark_evidence", "compatible_result_comparison", "reviewed_publication", "portable_exit_manifest"],
        "negative_mission": "Does not own source entities or relations, identity resolution, ontology and knowledge-model truth, graph persistence/query service, generic graph algorithms, predictive graph models, causal claims, vertical vocabulary, visualization semantics, business decisions or operational effects.",
        "lifecycle_states": ["draft", "graph_bound", "plan_compiled", "ready", "running", "partial", "completed", "review_pending", "accepted", "published", "retracted", "recalled", "archived", "exported", "failed"],
        "commands": ["open_workspace", "bind_graph_occurrence", "compile_algorithm_plan", "start_run", "cancel_run", "reconcile_run", "seal_result", "compare_results", "review_result", "publish_result", "retract_or_recall_result", "export_workspace", "archive_workspace"],
        "events": ["workspace_opened", "graph_occurrence_bound", "algorithm_plan_compiled", "run_started", "run_cancel_requested", "run_reconciled", "result_sealed", "results_compared", "result_reviewed", "result_published", "result_retracted_or_recalled", "workspace_exported", "workspace_archived"],
        "invariants": ["source relation, graph projection, graph occurrence, workspace, plan, run, result, publication and decision are distinct", "graph method semantics remain imported and replaceable", "ontology profile imports do not transfer ontology authority", "every result binds exact graph cut, profile, plan, provider, resources and evidence", "path is not cause, centrality is not importance or authority, and community is not a real-world group", "partial, cancelled, failed and unknown runs remain explicit", "publication never authorizes an external action"],
        "refusals": ["graph_occurrence_unbound", "projection_loss_undeclared", "semantic_profile_missing", "algorithm_plan_invalid", "method_or_provider_unqualified", "resource_budget_exceeded", "run_completion_unknown", "result_incompatible", "evidence_scope_missing", "publication_authority_missing", "exit_manifest_incomplete", "decision_or_effect_authority_requested"],
        "automation_modality": {"default": "DETERMINISTIC_CORE_ONLY", "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"], "law": "Learned models, LLMs and agents may propose projections, algorithms, parameters, interpretations or narratives, but graph identity/profile, plan, execution, evidence, review and authority remain typed and deterministic where selected.", "removal_law": "Removing every optional model, LLM or agent preserves workspace lifecycle, graph/profile binding, explicit classical algorithm planning and execution, result comparison, evidence, publication, recall and exit; required unavailable assistance yields capability_unavailable.", "hard_work_law": "Automation never supplies missing graph identity, projection loss, ontology authority, algorithm assumptions, resource bounds, benchmark scope, evidence, publication authority or vertical acceptance."},
    }


def dossier() -> dict[str, Any]:
    truth = product_truth()
    commands = truth["commands"]
    events = truth["events"]
    ddd = {
        "domain_vision_statement": "Own the provider-neutral graph-analysis workspace lifecycle from exact graph occurrence through reproducible run and bounded publication while graph methods, ontology truth, source authority and external effects remain imported.",
        "subdomain_classification": "core_horizontal_graph_analysis_workbench_candidate",
        "bounded_context_boundary": {"inside": ["workspace identity, edition, branch, archive and exit", "graph occurrence/projection/profile binding", "algorithm-plan compilation and method binding", "run attempts, cancellation, reconciliation and finite budgets", "result identity, comparison and benchmark evidence", "review, publication, retraction and recall"], "outside": ["source entity/relation truth and identity resolution", "ontology and knowledge-model governance", "graph database, query and storage", "generic graph method definitions and provider qualification", "predictive, causal and vertical graph semantics", "visualization meaning", "business decision and operational effect authority"]},
        "ubiquitous_language_policy": "Source relation, graph projection, graph occurrence, profile, workspace, algorithm plan, run attempt, result, comparison, benchmark, finding, publication, decision and effect are non-interchangeable; foreign ontology and vertical terms cross named ACLs.",
        "context_map": [
            {"neighbor_ref": "product.ontology_knowledge_model", "relationship": "customer_supplier_acl", "translation": "import ontology editions, semantic profiles, mappings and assertion status without acquiring ontology authority"},
            {"neighbor_ref": "product.query_execution_service", "relationship": "customer_supplier", "translation": "import exact graph/query cuts without acquiring persistence or query semantics"},
            {"neighbor_ref": "context.graph_method_kernels", "relationship": "customer_supplier_acl", "translation": "bind replaceable graph methods, assumptions, failures and qualification evidence"},
            {"neighbor_ref": "product.lineage_provenance", "relationship": "published_language", "translation": "publish immutable projection, plan, run, comparison and publication receipts"},
            {"neighbor_ref": "context.vertical_graph_semantics", "relationship": "anti_corruption_layer", "translation": "import domain vocabulary, populations and truth roles without renaming horizontal contracts"},
            {"neighbor_ref": "context.decision_and_effect_authority", "relationship": "effect_port", "translation": "handoff bounded results only; decisions and actions remain external"},
        ],
        "anti_corruption_layers": ["acl.graph_workbench.ontology_profile", "acl.graph_workbench.source_graph", "acl.graph_workbench.method_provider", "acl.graph_workbench.vertical_semantics", "acl.graph_workbench.decision_effect"],
        "published_language": ["GraphWorkspaceId", "GraphWorkspaceEdition", "GraphOccurrenceRef", "GraphSemanticProfileRef", "AlgorithmPlanEdition", "GraphRunId", "RunAttempt", "GraphResultEdition", "ResultComparison", "BenchmarkEvidence", "GraphPublicationEdition", "GraphRecallNotice", "WorkspaceExitManifest", "TypedRefusal"],
        "value_objects": ["WorkspaceId", "WorkspaceEdition", "GraphCutDigest", "ProjectionLossProfile", "AlgorithmProfileRef", "RandomnessProfile", "ApproximationProfile", "ResourceBudget", "ResultDigest", "EvidenceRef", "PublicationScope", "ExitDigest"],
        "entities": ["GraphWorkspace", "GraphOccurrenceBinding", "AlgorithmPlan", "GraphRun", "GraphResult", "ResultReview", "GraphPublication", "WorkspaceExit"],
        "aggregates": [
            {"root": "GraphWorkspace", "members": ["identity", "editions", "graph_bindings", "plans", "runs", "publications", "state"], "consistency": "published editions are immutable and branch/supersession is explicit"},
            {"root": "AlgorithmPlan", "members": ["graph_profile", "methods", "parameters", "randomness", "approximation", "backend", "budget"], "consistency": "a plan is complete and immutable before execution"},
            {"root": "GraphRun", "members": ["plan_ref", "input_cut", "attempts", "provider", "resources", "completion", "receipt"], "consistency": "unknown completion reconciles before retry and partial validity is explicit"},
            {"root": "GraphResult", "members": ["run_ref", "payload", "witnesses", "limitations", "review", "publication"], "consistency": "claim strength cannot exceed graph/profile/method/evidence scope"},
        ],
        "aggregate_roots": ["GraphWorkspace", "AlgorithmPlan", "GraphRun", "GraphResult"],
        "aggregate_invariants": truth["invariants"],
        "commands": commands,
        "domain_events": events,
        "refusal_failure_catalog": truth["refusals"] + ["capability_unavailable", "provider_failure", "cancelled", "partial_result_only"],
        "domain_services": ["GraphOccurrenceBindingService", "AlgorithmPlanCompiler", "GraphRunService", "ResultComparisonService", "BenchmarkEvidenceService", "PublicationReviewService", "WorkspaceExitService"],
        "application_services": ["OpenGraphWorkspaceUseCase", "BindGraphOccurrenceUseCase", "CompileAlgorithmPlanUseCase", "ExecuteGraphRunUseCase", "CompareAndReviewResultsUseCase", "PublishOrRecallResultUseCase", "ExportAndArchiveWorkspaceUseCase"],
        "repositories": ["GraphWorkspaceRepository", "AlgorithmPlanRepository", "GraphRunRepository", "GraphResultRepository", "GraphPublicationRepository"],
        "factories": ["GraphWorkspaceFactory", "GraphOccurrenceBindingFactory", "AlgorithmPlanFactory", "GraphRunFactory", "GraphResultFactory", "WorkspaceExitManifestFactory"],
        "specifications": ["GraphOccurrenceCompletenessSpecification", "ProjectionLossSpecification", "AlgorithmPlanSpecification", "MethodQualificationSpecification", "RunBudgetSpecification", "ResultCompatibilitySpecification", "BenchmarkScopeSpecification", "PublicationEligibilitySpecification", "ExitCompletenessSpecification"],
        "state_machine": {"workspace": truth["lifecycle_states"], "run": ["created", "admitted", "running", "cancel_requested", "partial", "completed", "failed", "unknown", "reconciled", "sealed"], "publication": ["draft", "review_pending", "accepted", "published", "retracted", "recalled", "superseded"]},
        "policies_and_reactions": ["when graph/profile identity is incomplete refuse planning", "when method assumptions or qualification are missing refuse execution", "when a run is unknown reconcile before retry", "when a result comparison is incompatible retain both results without ranking", "when a result implies causality identity policy or authority narrow or refuse the claim", "when publication evidence expires retract or recall the exact edition", "when a consumer requests action require external decision/effect authority"],
        "sagas_and_process_managers": ["WorkspaceLifecycleProcess", "GraphProjectionAdmissionProcess", "GraphRunExecutionProcess", "UnknownCompletionReconciliationProcess", "ResultReviewPublicationProcess", "RetractionRecallProcess", "WorkspaceExitProcess", "CrossProviderDifferentialProcess"],
        "read_models_and_projections": ["WorkspacePortfolioView", "GraphBindingAndLossView", "AlgorithmPlanView", "RunProgressAndBudgetView", "ResultEvidenceView", "ComparisonView", "PublicationRecallView", "ExitCompletenessView"],
        "integration_event_policy": "Only editioned workspace, graph-binding, plan, run, result, comparison, publication, recall and exit facts cross the boundary; source/ontology truth, provider internals, vertical interpretations, decisions and effects remain external.",
        "concurrency_and_idempotency": ["optimistic workspace, plan, result and publication editions", "sealed plans and results are immutable", "run idempotency binds plan, graph cut, provider, configuration and attempt", "unknown effects reconcile before retry", "publication, recall and exit are monotone receipt-bearing operations"],
        "time_model": ["source event, graph validity, observation, recording, projection cut, plan, run, result, publication and decision times are distinct", "dynamic graphs retain interval/instant semantics and snapshot derivation", "evidence and publication have validity and expiry", "recall and supersession preserve history"],
        "event_storming_swimlanes": ["graph_analyst", "source_graph_owner", "ontology_owner", "method_provider", "runtime_operator", "benchmark_reviewer", "result_reviewer", "publication_authority", "vertical_consumer", "decision_owner", "affected_party"],
        "nonfunctional_laws": ["finite vertices edges properties work memory threads external cost result size and publication volume", "cooperative cancellation with typed partial validity", "determinism randomness approximation ordering convergence and numeric tolerance are explicit", "small-graph exact and metamorphic oracles plus cross-provider differential tests", "receipts bind graph cut profile plan provider resources result evidence and authority", "provider identity cannot change semantics", truth["automation_modality"]["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.analytics.graph_analysis_workbench", "product_ref": PRODUCT, "status": "candidate_not_ratified", "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]}, "strategic_and_tactical_ddd": ddd}


def enrich_graph_workbench(source: dict[str, Any]) -> dict[str, Any]:
    source_ids = {row["source_id"] for row in SOURCE_ROWS}
    capability_ids = {local_capability(key) for key in KEYS}
    library_ids = {local_library(key) for key in KEYS}
    requirement_ids = {f"requirement.analytics_graph_workbench.{key}" for key in KEYS}
    binding_ids = {f"binding.analytics_graph_workbench.{key}" for key in KEYS}
    gap_ids = {f"gap.analytics_graph_workbench.{key}" for key in KEYS if not CONCRETE[key]}
    negative_ids = {f"negative.graph_workbench.{key}" for key in ["method_product", "ontology_truth", "projection_truth", "path_cause", "centrality_authority", "community_identity", "run_success", "benchmark_universal", "publication_action", "agent_authority"]}

    source["sources"] = [row for row in source["sources"] if row["source_id"] not in source_ids] + SOURCE_ROWS
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in capability_ids | {PRODUCT, SEMANTIC_OWNER}]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in library_ids]
    source["requirements"] = [row for row in source["requirements"] if row["requirement_id"] not in requirement_ids]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if row["binding_map_id"] not in binding_ids]
    source["binding_gaps"] = [row for row in source.get("binding_gaps", []) if row["gap_id"] not in gap_ids]
    source["boundary_decisions"] = [row for row in source["boundary_decisions"] if row["decision_id"] != "decision.methods.graph_analysis_workbench"]
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT]
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in negative_ids]
    source["crosswalks"] = [row for row in source["crosswalks"] if row["legacy_ref"] != "candidate.product.graph_analysis_workbench"]

    truth = product_truth()
    source["artifacts"].extend([
        {"artifact_id": PRODUCT, "kind": "product", "name": "Graph and network analysis workbench", "definition": "Governs graph-analysis workspaces, graph occurrence/profile bindings, algorithm plans, runs, result comparison, evidence, publication and exit while importing graph methods and ontology authority.", "status": "strong_product_candidate", "semantic_owner_ref": None, "adoption_unit": True, "operated": True, "evidence_refs": [row["source_id"] for row in SOURCE_ROWS], **truth},
        {"artifact_id": SEMANTIC_OWNER, "kind": "semantic_contract", "name": "Graph analysis workspace lifecycle semantics", "definition": "Owns workspace, graph-binding, plan, run, result-comparison, publication and exit meanings, not graph algorithm or ontology truth.", "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": False, "evidence_refs": ["evidence.graph_workbench.gephi_srs", "evidence.graph_workbench.cytoscape_manual", "evidence.graph_workbench.neo4j_management"]},
    ])
    for key in KEYS:
        source["artifacts"].append({"artifact_id": local_capability(key), "kind": "capability", "name": key.replace("_", " ").title(), "definition": CAPABILITIES[key], "status": "specified_candidate", "semantic_owner_ref": SEMANTIC_OWNER, "adoption_unit": False, "operated": False, "evidence_refs": [row["source_id"] for row in SOURCE_ROWS]})

    source["boundary_decisions"].append({
        "decision_id": "decision.methods.graph_analysis_workbench", "subject_ref": PRODUCT,
        "disposition": "strong_product_candidate_distinct_from_graph_method_family",
        "evidence_refs": [row["source_id"] for row in SOURCE_ROWS],
        "rationale": "Graph algorithms remain method/library contracts, but independent project/session/workspace, run, review, publication and exit lifecycles are adopted and operated as a workbench product.",
        "supersedes": ["candidate.product.graph_analysis_workbench"],
        "split_test": {
            "user": {"score": 2, "evidence_refs": ["evidence.graph_workbench.gephi_srs", "evidence.graph_workbench.cytoscape_manual"]},
            "job": {"score": 2, "evidence_refs": ["evidence.graph_workbench.gephi_srs", "evidence.graph_workbench.neo4j_management"]},
            "adoption": {"score": 2, "evidence_refs": ["evidence.graph_workbench.gephi_srs", "evidence.graph_workbench.cytoscape_manual"]},
            "semantics": {"score": 2, "evidence_refs": ["evidence.graph_workbench.graphalytics", "evidence.graph_workbench.neo4j_management"]},
            "authority": {"score": 1, "evidence_refs": ["evidence.graph_workbench.neo4j_management"]},
            "lifecycle": {"score": 2, "evidence_refs": ["evidence.graph_workbench.gephi_srs", "evidence.graph_workbench.neo4j_export"]},
            "operation": {"score": 2, "evidence_refs": ["evidence.graph_workbench.neo4j_management"]},
            "economics": {"score": 1, "evidence_refs": ["evidence.graph_workbench.neo4j_management"]},
            "interface": {"score": 2, "evidence_refs": ["evidence.graph_workbench.cytoscape_manual", "evidence.graph_workbench.neo4j_export"]},
            "market_evidence": {"score": 2, "evidence_refs": ["evidence.graph_workbench.gephi_srs", "evidence.graph_workbench.cytoscape_manual", "evidence.graph_workbench.neo4j_management"]},
        },
    })
    old_graph_decision = next(row for row in source["boundary_decisions"] if row["decision_id"] == "decision.methods.graph_not_product")
    old_graph_decision["rationale"] = "Graph analysis as a method label remains a semantic/library family; the separately adjudicated Graph Analysis Workbench product owns workspace/run/publication lifecycle and does not absorb graph methods, persistence or vertical applications."

    source["ddd_dossiers"].append(dossier())
    evidence_refs = [row["source_id"] for row in SOURCE_ROWS]
    for key in KEYS:
        deps = {
            "workspace_lifecycle": [], "graph_occurrence_profile": ["workspace_lifecycle"],
            "algorithm_plan": ["graph_occurrence_profile"], "run_evidence": ["algorithm_plan"],
            "benchmark_workload": ["algorithm_plan"], "result_comparison": ["run_evidence"],
            "publication_review": ["result_comparison"],
        }[key]
        source["libraries"].append({
            "library_id": local_library(key), "class": "semantic_policy_pure", "owner_ref": SEMANTIC_OWNER,
            "provides": [local_capability(key)],
            "types": [key.title().replace("_", ""), f"{key.title().replace('_', '')}Edition", f"{key.title().replace('_', '')}Refusal"],
            "operations": [f"define_{key}", f"validate_{key}"],
            "decisions": [f"{key}_identity", f"{key}_admission", f"{key}_compatibility"],
            "invariants": [CAPABILITIES[key], "provider identity does not change meaning", "authority and evidence remain explicit"],
            "refusals": [f"{key}_missing", f"{key}_invalid", f"{key}_incompatible", "resource_exhausted"],
            "dependencies": [local_library(dep) for dep in deps], "effect_boundary": "pure_effect_intents_only" if key == "publication_review" else "pure_no_io",
            "evidence_refs": evidence_refs, "product_refs": [PRODUCT],
        })
        source["requirements"].append({"requirement_id": f"requirement.analytics_graph_workbench.{key}", "consumer_ref": PRODUCT, "capability_ref": local_capability(key), "binding_phase": "runtime" if key in {"run_evidence", "publication_review"} else "compile_time", "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{key}_implementation"})
        concrete = CONCRETE[key]
        gap_ref = f"gap.analytics_graph_workbench.{key}"
        source["binding_maps"].append({"binding_map_id": f"binding.analytics_graph_workbench.{key}", "abstract_library_ref": local_library(key), "concrete_library_refs": concrete, "concrete_requirement_refs": [], "composition_law": "Workspace lifecycle composes exact graph occurrence/profile and imported method contracts; ontology, source, storage, prediction, vertical and effect authority remain outside.", "bindability": "structurally_bindable_unqualified" if concrete else "structurally_partial_blocking_gap", "blocking_gap_refs": [] if concrete else [gap_ref], "modality_posture": "deterministic_core", "minimum_qualified_implementations_per_required_contract": 1, "portable_claim_minimum_independent_implementations": 2, "qualification_profile_refs": QUALIFICATION.get(key, []), "substitution_law": "Workspace, graph cut/profile, plan, randomness, approximation, run, evidence, comparison, publication, exit and failure semantics survive substitution.", "cross_provider_differential_required": True, "fallback_law": "refuse", "status": "candidate_not_bound", "product_refs": [PRODUCT]})
        if not concrete:
            source["binding_gaps"].append({"gap_id": gap_ref, "status": "open", "product_refs": [PRODUCT], "abstract_library_refs": [local_library(key)], "missing_contracts": [key], "statement": f"The current exact compiler universe lacks a ratified provider-neutral {key.replace('_', ' ')} contract for the graph-analysis workbench.", "compiler_disposition": f"Add an exact {key.replace('_', ' ')} library with typed identity, operations, laws, refusals, finite bounds, evidence, portability tests and two qualified implementations."})

    source["crosswalks"].append({"legacy_ref": "candidate.product.graph_analysis_workbench", "canonical_refs": [PRODUCT, SEMANTIC_OWNER, *[local_library(key) for key in KEYS]], "disposition": "promote_distinct_workbench_candidate_without_productifying_graph_methods"})
    negatives = {
        "method_product": ("A graph algorithm or method library is itself the graph-analysis workbench product.", "retain method/library and product lifecycle identities"),
        "ontology_truth": ("A workbench graph or result establishes ontology or knowledge truth.", "require ontology-owner evidence and ACL"),
        "projection_truth": ("A projected graph is the source relation universe without loss.", "bind source cut and projection-loss profile"),
        "path_cause": ("A path or reachability result proves causality.", "publish structural reachability only"),
        "centrality_authority": ("A centrality score establishes importance, priority or authority.", "require external interpretation and decision authority"),
        "community_identity": ("A detected community is a real-world group or identity decision.", "retain algorithm/profile/uncertainty and external identity authority"),
        "run_success": ("Provider success proves a complete valid analytical result.", "require result and evidence validation"),
        "benchmark_universal": ("One benchmark result proves universal performance or portability.", "scope evidence to workload, dataset and environment"),
        "publication_action": ("A published graph result authorizes an operational effect.", "require external decision/effect authority"),
        "agent_authority": ("An agent fills missing graph, ontology, method, evidence or authority contracts.", "retain proposal taint and deterministic obligations"),
    }
    source["negative_tests"].extend({"test_id": f"negative.graph_workbench.{key}", "prohibited_claim": claim, "expected_result": expected} for key, (claim, expected) in negatives.items())
    source["non_collapse_laws"].extend(law for law in [
        "graph analysis method family != graph analysis workbench product",
        "source relation != graph projection != graph occurrence != workspace",
        "ontology profile import != ontology authority",
        "algorithm plan != run != result != publication",
        "path != cause; centrality != authority; community != real-world identity",
        "benchmark conformance != universal qualification or portability",
        "published graph result != decision or effect",
    ] if law not in source["non_collapse_laws"])
    return source
