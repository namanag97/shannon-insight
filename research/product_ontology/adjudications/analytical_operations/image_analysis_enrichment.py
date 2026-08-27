#!/usr/bin/env python3
"""Retain Image Analysis Workbench while importing image truth, methods and effects."""

from __future__ import annotations

from typing import Any


PRODUCT = "product.image_analysis_workbench"
PREFIX = "image_analysis"


def library(key: str) -> str:
    return f"library.analytics_image_analysis.{key}"


def owner(key: str) -> str:
    return f"semantic.image_analysis.{key}"


def capability(key: str) -> str:
    return f"capability.image_analysis.{key}"


SOURCES = [
    ("imagej_batch", "official_product_documentation", "Batch Processing", "ImageJ", "https://imagej.net/scripting/batch", "ImageJ documents reusable scripts and macros applied across image sets.", "Automation mechanics do not define scientific fitness, image identity or downstream authority."),
    ("imagej_roi", "official_product_documentation", "ROI Manager", "ImageJ", "https://imagej.net/ij/docs/guide/146-30.html", "ImageJ distinguishes reusable regions of interest and ROI-associated measurements.", "One tool's ROI representation is not a portable region/object algebra."),
    ("cellprofiler_project", "official_product_documentation", "Introduction to Projects", "CellProfiler", "https://cellprofiler-manual.s3.amazonaws.com/CellProfiler-4.2.3/help/projects_introduction.html", "A project binds an image file list, metadata, channel/group relations and an analysis pipeline.", "A project container does not prove input validity or result fitness."),
    ("cellprofiler_pipeline", "official_product_documentation", "How To Build A Pipeline", "CellProfiler", "https://cellprofiler-manual.s3.amazonaws.com/CellProfiler-4.2.8/help/pipelines_building.html", "Sequential modules, settings, test mode, batch execution and explicit output modules form a reproducible analysis workflow.", "Sequential provider modules are evidence for a lifecycle, not the universal recipe algebra."),
    ("cellprofiler_measurement", "official_product_documentation", "Measurement modules", "CellProfiler", "https://cellprofiler-manual.s3.amazonaws.com/CellProfiler-4.2.4/modules/measurement.html", "Measurements are attached to images or objects produced by prior modules and can be viewed or exported.", "A produced measurement is not accepted scientific truth or a business decision."),
    ("qupath_projects", "official_product_documentation", "Projects", "QuPath", "https://qupath.readthedocs.io/en/stable/docs/tutorials/projects.html", "QuPath projects manage collections of images and associated analysis data.", "A pathology-oriented implementation cannot own the cross-domain product semantics."),
    ("qupath_objects", "official_product_documentation", "Annotating images", "QuPath", "https://qupath.readthedocs.io/en/stable/docs/starting/annotating.html", "QuPath distinguishes annotations, detections and regions used for measurements and scoped analysis.", "Annotation and detection objects do not acquire reference, diagnosis or inspection authority."),
    ("qupath_workflows", "official_product_documentation", "Workflows", "QuPath", "https://qupath.readthedocs.io/en/stable/docs/scripting/workflows.html", "Recorded workflows can be converted into scripts and applied across projects.", "Recorded commands do not by themselves guarantee deterministic replay or semantic compatibility."),
    ("qupath_measurements", "official_product_documentation", "Commands and measurement export", "QuPath", "https://qupath.readthedocs.io/en/stable/docs/reference/commands.html", "QuPath exposes object measurement tables, maps and project-level exports.", "Exported tables do not prove units, uncertainty, validity or downstream acceptance."),
    ("napari_layers", "official_product_documentation", "Layers: bringing data into napari", "napari", "https://napari.org/stable/getting_started/layers.html", "Napari distinguishes Image, Labels, Points, Shapes, Surface, Tracks and Vectors layers over n-dimensional data.", "Viewer layer types do not establish source truth, reference acceptance or analytical correctness."),
    ("napari_units", "official_product_documentation", "Scale and unit-aware rendering", "napari", "https://napari.org/stable/guides/units.html", "Layer transforms, axis labels and units connect data coordinates to displayed world coordinates.", "Rendering transforms are not automatically calibrated physical-coordinate evidence."),
    ("ome_model", "official_data_model", "OME Data Model and File Formats", "Open Microscopy Environment", "https://ome-model.readthedocs.io/en/latest/", "OME separates projects, datasets, images, pixels, channels, planes, instruments, ROIs and structured annotations.", "Microscopy metadata does not define a universal analysis project or scientific conclusion."),
    ("ome_ngff", "community_specification", "OME-NGFF specification", "Open Microscopy Environment", "https://ngff.openmicroscopy.org/latest/", "OME-NGFF defines multidimensional arrays, axes, coordinate systems, transformations, multiscales and labels.", "Carrier/interchange semantics do not own workbench lifecycle, method fitness or result acceptance."),
]

EVIDENCE = [f"evidence.image_analysis.{row[0]}" for row in SOURCES]


LIBRARIES: dict[str, dict[str, Any]] = {
    "project_definition": {
        "types": ["ImageAnalysisProjectId", "AnalysisPurpose", "SubjectPopulation", "AnalysisQuestion", "ProjectEdition", "IntendedUse", "ProhibitedUse"],
        "operations": ["open_project", "bind_question_and_population", "declare_uses", "publish_project_edition"],
        "decisions": ["project identity", "question", "population", "unit of analysis", "intended and prohibited uses"],
        "invariants": ["project question image collection and analytical conclusion are distinct", "purpose and population are explicit and editioned", "project identity is provider neutral"],
        "refusals": ["question_missing", "population_ambiguous", "analysis_unit_unbound", "use_conflict", "project_edition_conflict"], "dependencies": [],
    },
    "image_occurrence_admission": {
        "types": ["ImageOccurrenceRef", "CarrierRef", "DecodedFieldRef", "ImageProfileRef", "AdmissionEvidence", "AdmissionDecision", "ExclusionReason"],
        "operations": ["propose_image_occurrence", "resolve_external_profile", "admit_or_exclude", "seal_input_cut"],
        "decisions": ["occurrence identity", "carrier/profile binding", "admissibility", "exclusion", "input cut"],
        "invariants": ["source image carrier decoded field rendition and admitted occurrence are distinct", "admission never mutates source truth", "unknown profile facts fail closed"],
        "refusals": ["occurrence_identity_unresolved", "carrier_unavailable", "profile_incompatible", "decode_evidence_missing", "admission_conflict"], "dependencies": ["project_definition"],
    },
    "workspace_layer_graph": {
        "types": ["WorkspaceId", "LayerId", "LayerKind", "LayerSource", "LayerOrder", "VisibilityState", "BlendProfile", "LayerGraphEdition"],
        "operations": ["create_workspace", "add_or_remove_layer", "order_layers", "bind_layer_source", "publish_layer_graph"],
        "decisions": ["layer identity and kind", "source binding", "order", "visibility", "display-only presentation"],
        "invariants": ["image label point shape surface track vector and measurement layers remain distinct", "display state never changes analytical data", "derived layers preserve source lineage"],
        "refusals": ["layer_kind_unsupported", "source_unresolved", "dimension_mismatch", "layer_cycle", "presentation_claims_data_change"], "dependencies": ["image_occurrence_admission"],
    },
    "coordinate_profile_binding": {
        "types": ["Axis", "AxisRole", "Unit", "DataFrameRef", "WorldFrameRef", "TransformRef", "ValidityDomain", "TransformUncertainty"],
        "operations": ["bind_axes_and_units", "bind_external_transform", "validate_frame_path", "project_coordinates", "report_residual"],
        "decisions": ["axis meaning", "units", "frame path", "transform edition", "validity and uncertainty"],
        "invariants": ["pixel index display coordinate and calibrated world coordinate are distinct", "binding a transform does not claim calibration authority", "all projections report validity domain and uncertainty"],
        "refusals": ["axis_ambiguous", "unit_missing", "frame_path_disconnected", "transform_out_of_domain", "uncertainty_unreported"], "dependencies": ["workspace_layer_graph"],
    },
    "region_object_topology": {
        "types": ["RegionId", "RegionKind", "Mask", "Contour", "LabelMap", "Component", "ObjectId", "Containment", "Adjacency", "TopologyEdition"],
        "operations": ["construct_region", "compose_regions", "derive_components", "bind_object", "compare_topology"],
        "decisions": ["region identity", "open/closed boundary", "connectivity", "overlap", "containment", "object binding"],
        "invariants": ["ROI mask contour label component and domain object are distinct", "region equality declares coordinate frame and tolerance", "region edits are append-only occurrences"],
        "refusals": ["frame_unbound", "invalid_geometry", "connectivity_undefined", "topology_inconsistent", "object_authority_missing"], "dependencies": ["coordinate_profile_binding"],
    },
    "analysis_recipe": {
        "types": ["AnalysisRecipeId", "RecipeStep", "MethodRequirement", "InputPort", "OutputPort", "ParameterBinding", "RandomnessPolicy", "ExpectedResultKind", "RecipeEdition"],
        "operations": ["define_recipe", "add_method_step", "bind_parameters", "typecheck_graph", "seal_recipe_edition"],
        "decisions": ["step graph", "ports", "parameters", "randomness", "partial-result policy", "expected outputs"],
        "invariants": ["recipe identity includes every behavior-affecting decision", "recipe validity is not scientific fitness", "undeclared randomness and provider defaults are forbidden"],
        "refusals": ["graph_cycle", "port_type_mismatch", "parameter_unresolved", "randomness_undeclared", "expected_result_unbound"], "dependencies": ["workspace_layer_graph", "region_object_topology"],
    },
    "method_capability_binding": {
        "types": ["MethodContractRef", "CapabilityRequirement", "ProviderOfferRef", "QualificationProfileRef", "CompatibilityRelation", "BindingDecision"],
        "operations": ["declare_method_requirement", "match_provider_offer", "check_qualification", "bind_method", "evaluate_substitution"],
        "decisions": ["method semantics", "capability", "provider qualification", "compatibility", "substitution posture"],
        "invariants": ["method contract provider implementation and fitted model are distinct", "provider binding never changes recipe semantics", "unqualified offers cannot satisfy compilation"],
        "refusals": ["method_owner_missing", "capability_unavailable", "provider_unqualified", "compatibility_unproven", "substitution_changes_semantics"], "dependencies": ["analysis_recipe"],
    },
    "analysis_run_attempt": {
        "types": ["AnalysisRunId", "AttemptId", "InputCut", "RecipeRef", "ProviderBindingSet", "ResourceBudget", "RunState", "CancellationReason", "RuntimeReceipt"],
        "operations": ["plan_run", "start_attempt", "record_progress", "cancel_attempt", "finish_attempt", "reconcile_unknown_terminal_state"],
        "decisions": ["exact cuts and bindings", "budgets", "retry", "cancellation", "partial validity", "terminal-state reconciliation"],
        "invariants": ["plan run attempt completion and valid result are distinct", "every attempt binds exact inputs recipe providers resources and time", "retry never overwrites prior evidence"],
        "refusals": ["input_cut_changed", "binding_unqualified", "budget_missing", "resource_exhausted", "cancelled", "terminal_state_unknown"], "dependencies": ["method_capability_binding"],
    },
    "derived_layer_result": {
        "types": ["DerivedLayerId", "ResultKind", "SourceLayerSet", "DerivationReceipt", "SampleFieldRef", "ResultState", "Limitation", "Uncertainty"],
        "operations": ["admit_derived_layer", "validate_shape_and_frame", "bind_derivation", "mark_partial_or_invalid", "compare_layer_editions"],
        "decisions": ["result kind", "source layers", "shape/frame", "partiality", "limitations", "uncertainty"],
        "invariants": ["derived layer is not source image or accepted reference", "completed execution is not valid result", "invalid unknown partial empty and zero are distinct"],
        "refusals": ["derivation_untraceable", "shape_mismatch", "frame_mismatch", "result_state_ambiguous", "limitation_missing"], "dependencies": ["analysis_run_attempt", "workspace_layer_graph"],
    },
    "object_segmentation_result": {
        "types": ["DetectionResult", "LocalizationResult", "SegmentationResult", "ObjectOccurrence", "RegionAssignment", "ClassCandidate", "Score", "Abstention"],
        "operations": ["admit_detection", "admit_segmentation", "construct_object_occurrences", "bind_class_candidates", "record_abstention"],
        "decisions": ["result grain", "region/object relation", "class vocabulary import", "score semantics", "abstention"],
        "invariants": ["detected region object class candidate and accepted domain entity are distinct", "scores never acquire label or decision authority", "result grain and evaluation unit are explicit"],
        "refusals": ["result_grain_missing", "vocabulary_unresolved", "score_semantics_unknown", "overlap_policy_missing", "abstention_collapsed"], "dependencies": ["derived_layer_result", "region_object_topology"],
    },
    "measurement_feature_result": {
        "types": ["MeasurementResult", "FeatureResult", "MeasuredSubjectRef", "MeasurandRef", "QuantityValue", "Unit", "Uncertainty", "ValidityDomain", "MethodReceipt"],
        "operations": ["admit_measurement", "admit_feature", "validate_unit_and_subject", "propagate_uncertainty", "publish_result_table"],
        "decisions": ["subject and grain", "measurand or feature", "unit", "uncertainty", "validity", "table schema"],
        "invariants": ["feature measurement indicator and conclusion are distinct", "measurement binds subject method unit uncertainty and validity", "undefined missing suppressed uncertain and zero are distinct"],
        "refusals": ["subject_unresolved", "measurand_undefined", "unit_incompatible", "uncertainty_missing", "validity_domain_exceeded"], "dependencies": ["object_segmentation_result"],
    },
    "result_comparison_review": {
        "types": ["ComparisonPlan", "ComparableCut", "MetricRef", "DifferenceResult", "ReviewIssue", "ReviewerJudgment", "Defeater", "ReviewVerdict"],
        "operations": ["define_comparison", "check_comparability", "calculate_difference", "open_review_issue", "record_judgment", "publish_review_verdict"],
        "decisions": ["comparison scope", "compatibility relation", "metric", "material difference", "issue disposition", "defeaters"],
        "invariants": ["difference is not defect diagnosis or inspection disposition", "review judgment never rewrites method results", "incomparable results refuse numerical comparison"],
        "refusals": ["cuts_incomparable", "metric_inapplicable", "difference_uncertain", "review_authority_missing", "defeater_unresolved"], "dependencies": ["derived_layer_result", "measurement_feature_result"],
    },
    "provenance_replay_history": {
        "types": ["HistoryEntry", "EditOccurrence", "RecipeRef", "RunReceiptRef", "ResultRef", "ProvenanceGraph", "ReplayPlan", "ReplayVerdict"],
        "operations": ["append_history", "construct_provenance", "plan_replay", "execute_replay_check", "compare_replay_results"],
        "decisions": ["history identity", "causal edges", "replay environment", "equivalence relation", "accepted residual"],
        "invariants": ["history records occurrences and never rewrites them", "replayability reproducibility and scientific validity are distinct", "equivalence and tolerances are declared"],
        "refusals": ["history_gap", "causal_edge_unresolved", "dependency_unavailable", "replay_non_deterministic", "equivalence_unbound"], "dependencies": ["analysis_run_attempt", "result_comparison_review"],
    },
    "evidence_publication_export": {
        "types": ["EvidencePackageId", "ProjectEditionRef", "InputManifest", "RecipeManifest", "RunReceiptSet", "ResultManifest", "LimitationStatement", "ExportProfile", "PublicationReceipt"],
        "operations": ["assemble_evidence_package", "validate_manifest", "project_export_format", "authorize_publication", "publish_package", "verify_package"],
        "decisions": ["included cuts", "evidence completeness", "projection loss", "disclosure", "publication authority", "verification"],
        "invariants": ["export publication and downstream acceptance are distinct", "publication preserves exact project input recipe run result and limitation identities", "lossy projection is declared and never silently canonical"],
        "refusals": ["manifest_incomplete", "result_invalid", "limitation_omitted", "projection_loss_unaccepted", "disclosure_denied", "publication_authority_missing"], "dependencies": ["provenance_replay_history"],
    },
}


def source_rows() -> list[dict[str, Any]]:
    return [{"source_id": f"evidence.image_analysis.{key}", "source_class": cls, "title": title, "publisher": publisher, "retrieved_at": "2026-08-27", "uri": uri, "claim": claim, "scope_limit": limit} for key, cls, title, publisher, uri, claim, limit in SOURCES]


def product_artifact() -> dict[str, Any]:
    states = ["project_draft", "inputs_pending", "workspace_open", "recipe_draft", "recipe_ready", "run_planned", "running", "results_pending", "review_open", "evidence_ready", "published", "superseded", "recalled"]
    commands = ["open_analysis_project", "admit_image_occurrences", "configure_workspace", "define_analysis_recipe", "bind_method_providers", "plan_analysis_run", "execute_analysis_run", "admit_results", "compare_and_review_results", "assemble_evidence_package", "authorize_publication", "publish_evidence_package", "supersede_project_edition", "recall_publication"]
    events = ["analysis_project_opened", "image_occurrences_admitted", "workspace_configured", "analysis_recipe_defined", "method_providers_bound", "analysis_run_planned", "analysis_run_executed", "results_admitted", "results_compared_and_reviewed", "evidence_package_assembled", "publication_authorized", "evidence_package_published", "project_edition_superseded", "publication_recalled"]
    return {
        "artifact_id": PRODUCT, "kind": "product", "name": "Image Analysis Workbench", "status": "candidate", "semantic_owner_ref": None, "adoption_unit": True, "operated": True,
        "definition": "How can an analyst turn admitted image occurrences into reproducible, inspectable and publishable analytical results without acquiring source, scientific, diagnostic, inspection or effect authority?",
        "sovereign_question": "How can an analyst turn admitted image occurrences into reproducible, inspectable and publishable analytical results without acquiring source, scientific, diagnostic, inspection or effect authority?",
        "users": ["image_analyst", "scientist", "research_engineer", "pathology_analyst", "materials_analyst", "assurance_reviewer"],
        "harmed_parties": ["data_subject", "patient", "sample_owner", "source_owner", "decision_subject", "downstream_consumer"],
        "jobs": ["Define an image-analysis project; bind images, layers, coordinates and regions; compose and run qualified methods; inspect, compare, replay and publish evidence-bearing results."],
        "outcomes": ["purpose_bound_project", "typed_image_workspace", "reproducible_analysis_recipe", "evidence_bearing_results", "reviewable_comparisons", "verifiable_publication"],
        "lifecycle_states": states, "commands": commands, "events": events,
        "invariants": ["image carrier decoded field layer region object measurement finding judgment and downstream decision are distinct", "project recipe run attempt result review and publication are distinct", "algorithms providers and models never own workbench semantics", "vertical vocabularies and authority are imported", "all results bind exact inputs recipe providers attempts limitations and time", "publication never implies diagnosis inspection disposition or scientific acceptance"],
        "refusals": ["question_or_population_unbound", "image_identity_or_profile_unresolved", "workspace_frames_incompatible", "recipe_invalid", "method_provider_unqualified", "runtime_budget_missing", "result_invalid_or_partiality_unknown", "comparison_inapplicable", "review_authority_missing", "evidence_manifest_incomplete", "publication_authority_missing"],
        "negative_mission": "Does not own acquisition devices, source bytes, image carrier formats, calibration truth, generic image algorithms, annotations or reference truth, model training, scientific-study conclusions, medical diagnosis, geospatial feature authority, inspection disposition, document extraction, storage, scheduling or downstream effects.",
        "automation_modality": {"default": "DETERMINISTIC_CORE_ONLY", "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"], "law": "Learned, generative and agentic methods may offer typed method results or proposals only through qualified ports.", "hard_work_law": "Automation never replaces vocabulary, boundary adjudication, invariants, state machines, evidence, law oracles, qualification or domain acceptance.", "removal_law": "Removing model and agent extensions preserves project, workspace, recipe, execution, result, review, replay and publication semantics."},
        "evidence_refs": EVIDENCE,
    }


def dossier(product: dict[str, Any]) -> dict[str, Any]:
    roots = ["AnalysisProject", "ImageWorkspace", "AnalysisRecipe", "AnalysisRun", "ResultSet", "ReviewCase", "EvidencePublication"]
    context_map = [
        {"neighbor_ref": "neighbor.image_source_truth", "relationship": "customer_supplier_acl", "translation": "admit immutable occurrences, carriers and profile evidence without owning them"},
        {"neighbor_ref": "neighbor.image_semantics", "relationship": "published_language", "translation": "import sample-lattice, radiometry, color, coordinate and carrier contracts"},
        {"neighbor_ref": "neighbor.method_kernels", "relationship": "open_host_service", "translation": "bind qualified deterministic, statistical or learned method contracts"},
        {"neighbor_ref": "product.annotation_operations", "relationship": "customer_supplier_acl", "translation": "import annotation and accepted-reference editions without creating ground truth"},
        {"neighbor_ref": "neighbor.model_lifecycle", "relationship": "customer_supplier_acl", "translation": "import released model artifacts while model lifecycle owns training and release"},
        {"neighbor_ref": "product.visual_inspection_operations", "relationship": "published_language", "translation": "supply method evidence while inspection owns plans, dispositions and effects"},
        {"neighbor_ref": "product.document_processing_review", "relationship": "separate_ways_published_language", "translation": "share image methods while document product owns content extraction and business-fact release"},
        {"neighbor_ref": "neighbor.geospatial_authority", "relationship": "anti_corruption_layer", "translation": "import CRS, feature and spatial-authority semantics"},
        {"neighbor_ref": "neighbor.scientific_medical_authority", "relationship": "anti_corruption_layer", "translation": "export evidence without claiming study conclusions or diagnosis"},
        {"neighbor_ref": "neighbor.versioned_storage", "relationship": "supplier", "translation": "persist bytes and objects without equating storage commits with project evidence editions"},
    ]
    ddd = {
        "domain_vision_statement": "Own the accountable lifecycle from an image-analysis question and admitted occurrences to reproducible, reviewable and publishable result evidence.",
        "subdomain_classification": "core_for_cross_domain_image_analysis_supporting_to_scientific_medical_industrial_and_geospatial_products",
        "bounded_context_boundary": {"inside": ["analysis project and purpose", "image occurrence admission", "workspace layer graph", "coordinate/profile binding", "regions and analytical objects", "recipe and method requirements", "run/attempt lifecycle", "derived layers detections segmentations measurements and features", "comparison review replay and evidence publication"], "outside": ["source bytes and acquisition", "carrier/radiometry/calibration truth", "generic algorithms", "annotation/reference authority", "model training and release", "scientific conclusions and medical diagnosis", "geospatial feature authority", "inspection disposition and machine effects", "document extraction", "generic runtime/storage"]},
        "ubiquitous_language_policy": "Project, source occurrence, carrier, layer, region, analytical object, recipe, run, attempt, result, finding, judgment, evidence package and downstream decision have one non-interchangeable meaning.",
        "context_map": context_map,
        "anti_corruption_layers": [f"acl.image_analysis.{row['neighbor_ref'].split('.')[-1]}" for row in context_map],
        "published_language": ["AnalysisProjectEdition", "InputCut", "LayerGraphEdition", "AnalysisRecipeEdition", "RunReceipt", "ResultSet", "ReviewVerdict", "EvidencePackage", "PublicationRecall", "typed refusals"],
        "value_objects": ["AnalysisPurpose", "ImageOccurrenceRef", "LayerId", "CoordinateProfile", "Region", "ObjectOccurrence", "AnalysisRecipe", "MethodRequirement", "InputCut", "ResultState", "MeasurementResult", "Uncertainty", "ReplayVerdict", "EvidenceDigest"],
        "entities": ["AnalysisProject", "ImageWorkspace", "Layer", "RegionOccurrence", "AnalysisRecipe", "AnalysisRun", "Attempt", "ResultSet", "ReviewIssue", "EvidencePublication"],
        "aggregates": [{"root": root, "members": [f"{root}Id", "edition", "state", "evidence_refs"], "consistency": f"{root} changes only through versioned commands preserving exact provenance and authority."} for root in roots],
        "aggregate_roots": roots,
        "aggregate_invariants": product["invariants"] + ["sealed recipes and published evidence packages are immutable", "every derived object or value has one exact result grain", "reviews append judgments and never rewrite prior method results"],
        "commands": product["commands"], "domain_events": product["events"],
        "refusal_failure_catalog": product["refusals"] + ["unsupported_capability", "resource_exhausted", "cancelled", "provider_terminal_state_unknown", "projection_loss_unaccepted"],
        "domain_services": ["ProjectDefinitionService", "ImageAdmissionService", "WorkspaceLayerService", "RecipeService", "MethodBindingService", "RunLifecycleService", "ResultAdmissionService", "ComparisonReviewService", "ReplayService", "EvidencePublicationService"],
        "application_services": ["OpenImageAnalysisProject", "ConfigureImageWorkspace", "ComposeAnalysisRecipe", "RunAnalysis", "ReviewResults", "ReplayAnalysis", "PublishEvidence", "SupersedeOrRecallPublication"],
        "repositories": [f"{root}Repository" for root in roots], "factories": [f"{root}Factory" for root in roots],
        "specifications": ["ProjectQuestionSpecification", "ImageAdmissionSpecification", "LayerCompatibilitySpecification", "CoordinateBindingSpecification", "RecipeTypeSpecification", "ProviderQualificationSpecification", "RunReadinessSpecification", "ResultValiditySpecification", "ComparisonApplicabilitySpecification", "ReplayEquivalenceSpecification", "EvidenceCompletenessSpecification"],
        "state_machine": {"project": product["lifecycle_states"], "recipe": ["draft", "type_invalid", "ready", "sealed", "superseded"], "run": ["planned", "starting", "running", "partial", "completed", "failed", "cancelled", "terminal_unknown", "reconciled"], "result": ["pending", "valid", "partial", "unknown", "invalid", "superseded"], "publication": ["draft", "review_pending", "authorized", "published", "superseded", "recalled"]},
        "policies_and_reactions": ["when source or profile validity changes open impact assessment", "when a recipe seals freeze behavior-affecting decisions", "when an attempt terminates unknown reconcile before retry", "when a result is partial preserve typed partiality", "when comparison inputs are incompatible refuse comparison", "when evidence is incomplete refuse publication", "when a dependency is recalled mark publications affected"],
        "sagas_and_process_managers": ["ProjectSetupProcess", "RecipeQualificationAndBindingProcess", "AnalysisRunProcess", "ResultReviewProcess", "ReplayVerificationProcess", "EvidencePublicationProcess", "DependencyRecallProcess"],
        "read_models_and_projections": ["ProjectOverview", "InputAndLayerView", "RecipeGraphView", "RunAttemptView", "ResultLayerView", "ObjectMeasurementTable", "ComparisonView", "ProvenanceGraphView", "EvidencePackageView"],
        "integration_event_policy": "Only editioned project, recipe, run, result, review, publication, supersession and recall facts cross the boundary; source truth, method internals, vertical judgments and downstream effects remain external.",
        "concurrency_and_idempotency": ["optimistic aggregate editions", "idempotency key per command", "immutable input and recipe cuts", "attempt identities survive retries", "layer edits are append-only occurrences", "publication uses compare-and-swap over exact evidence manifest", "unknown effects are reconciled before retry"],
        "time_model": ["source capture validity and recording time are imported", "admission edit recipe seal attempt result review publication supersession and recall times are distinct", "calibration and transform validity may be bitemporal", "published evidence remains historically immutable", "dependency recall creates impact events rather than retroactive mutation"],
        "event_storming_swimlanes": ["analyst", "source_owner", "image_semantics_owner", "method_provider", "runtime_provider", "annotation_owner", "reviewer", "scientific_or_vertical_authority", "publication_authority", "consumer"],
        "nonfunctional_laws": ["finite images pixels voxels layers regions objects methods attempts memory runtime output and cost", "cooperative cancellation with typed partial results", "determinism randomness approximation numeric tolerance and hardware sensitivity are explicit", "receipts bind semantic data recipe provider runtime authority and time cuts", "provider substitution preserves declared recipe and result semantics", "fail closed on missing identity profile qualification validity comparison applicability or publication authority", product["automation_modality"]["removal_law"]],
    }
    return {"dossier_id": "ddd.ao.image_analysis", "product_ref": PRODUCT, "status": "candidate_not_ratified", "product_truth": {"sovereign_question": product["sovereign_question"], "users": product["users"], "harmed_parties": product["harmed_parties"], "jobs": product["jobs"], "measurable_outcomes": product["outcomes"], "negative_mission": product["negative_mission"]}, "strategic_and_tactical_ddd": ddd}


def enrich_image_analysis(source: dict[str, Any]) -> dict[str, Any]:
    product = product_artifact()
    keys = sorted(LIBRARIES)
    lib_ids = {library(key) for key in keys}
    source["sources"] = [row for row in source["sources"] if row["source_id"] not in set(EVIDENCE)] + source_rows()

    neighbors = {
        "neighbor.image_source_truth": "Owns image acquisition occurrences, original bytes, device evidence and source corrections.",
        "neighbor.image_semantics": "Owns carrier, sample-lattice, radiometry, color, axes, coordinates and transform semantics.",
        "neighbor.method_kernels": "Owns reusable deterministic, statistical and predictive image-method contracts and conformance laws.",
        "neighbor.geospatial_authority": "Owns CRS, spatial feature, coverage and geospatial result authority.",
        "neighbor.scientific_medical_authority": "Owns study protocols, scientific conclusions, clinical interpretation and diagnosis.",
    }
    artifact_ids = {PRODUCT, *neighbors, *[owner(k) for k in keys], *[capability(k) for k in keys], "implementation.image_analysis.imagej", "implementation.image_analysis.cellprofiler", "implementation.image_analysis.qupath", "implementation.image_analysis.napari"}
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in artifact_ids]
    source["artifacts"].append(product)
    for key in keys:
        source["artifacts"].extend([
            {"artifact_id": owner(key), "kind": "semantic_contract", "name": key.replace("_", " ").title(), "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": False, "definition": f"Owns the provider-neutral {key.replace('_', ' ')} decision contract.", "evidence_refs": EVIDENCE},
            {"artifact_id": capability(key), "kind": "capability", "name": key.replace("_", " ").title(), "status": "candidate", "semantic_owner_ref": owner(key), "adoption_unit": False, "operated": False, "definition": f"Typed capability for {key.replace('_', ' ')}.", "evidence_refs": EVIDENCE},
        ])
    for ident, definition in neighbors.items():
        source["artifacts"].append({"artifact_id": ident, "kind": "neighbor", "name": ident.split(".")[-1].replace("_", " ").title(), "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": True, "definition": definition, "evidence_refs": EVIDENCE})
    implementations = [
        ("imagej", "ImageJ/Fiji", EVIDENCE[0:2], ["workspace_layer_graph", "region_object_topology", "analysis_recipe"]),
        ("cellprofiler", "CellProfiler", EVIDENCE[2:5], ["project_definition", "analysis_recipe", "analysis_run_attempt", "measurement_feature_result"]),
        ("qupath", "QuPath", EVIDENCE[5:9], ["project_definition", "region_object_topology", "result_comparison_review", "measurement_feature_result"]),
        ("napari", "napari", EVIDENCE[9:11], ["workspace_layer_graph", "coordinate_profile_binding", "region_object_topology"]),
    ]
    for key, name, evidence, _ in implementations:
        source["artifacts"].append({"artifact_id": f"implementation.image_analysis.{key}", "kind": "implementation", "name": name, "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": True, "definition": "Observed image-analysis implementation; no qualification or portability is claimed.", "evidence_refs": evidence})

    source["ownership"] = [row for row in source["ownership"] if not row["meaning_id"].startswith("meaning.image_analysis.")]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in lib_ids]
    source["requirements"] = [row for row in source["requirements"] if not row["requirement_id"].startswith("requirement.image_analysis.")]
    source["binding_maps"] = [row for row in source["binding_maps"] if not row["binding_map_id"].startswith("binding.image_analysis.")]
    source["binding_gaps"] = [row for row in source["binding_gaps"] if not row["gap_id"].startswith("gap.ao.binding.image_analysis.")]
    for key in keys:
        spec = LIBRARIES[key]
        source["ownership"].append({"meaning_id": f"meaning.image_analysis.{key}", "term": key.replace("_", " "), "owner_ref": owner(key), "invariant": spec["invariants"][0], "must_not_be_owned_by": ["component.ao.optional_model_agent_extension", "neighbor.image_source_truth", "neighbor.method_kernels", "neighbor.scientific_medical_authority"]})
        source["libraries"].append({"library_id": library(key), "class": "semantic_pure", "product_ref": PRODUCT, "owner_ref": owner(key), "provides": [capability(key)], "types": spec["types"], "operations": spec["operations"], "decisions": spec["decisions"], "invariants": spec["invariants"] + ["provider_identity_does_not_change_semantics", "partiality_uncertainty_and_abstention_are_explicit", "generated_or_agent_output_is_non_authoritative_until_typed_validated_and_accepted", "removing_model_and_agent_extensions_preserves_the_deterministic_core_contract"], "refusals": spec["refusals"] + ["unsupported_capability", "unresolved_authority", "resource_exhausted", "cancelled"], "dependencies": [library(dep) for dep in spec["dependencies"]], "effect_boundary": "pure_no_io", "evidence_refs": EVIDENCE})
        source["requirements"].append({"requirement_id": f"requirement.image_analysis.{key}", "consumer_ref": PRODUCT, "capability_ref": capability(key), "minimum_qualified_offers": 2, "binding_phase": "compile_time", "status": "unbound", "refusal": "refuse compilation when no exact compatible qualified offer exists"})
        gap = f"gap.ao.binding.image_analysis.{key}"
        source["binding_gaps"].append({"gap_id": gap, "product_ref": PRODUCT, "abstract_library_ref": library(key), "statement": f"No exact compiler registry contribution owns the complete {key.replace('_', ' ')} contract.", "blocking": True, "closure_evidence": "Add the exact pure contract with executable law oracles and independently qualify at least two substitutable implementations."})
        source["binding_maps"].append({"binding_map_id": f"binding.image_analysis.{key}", "product_ref": PRODUCT, "abstract_library_ref": library(key), "compiler_disposition": "missing_exact_compiler_library_contract", "concrete_library_refs": [], "gap_ref": gap, "portable_offer": False})

    source["offers"] = [row for row in source["offers"] if not row["offer_id"].startswith("offer.image_analysis.")]
    for key, _, evidence, capabilities in implementations:
        source["offers"].append({"offer_id": f"offer.image_analysis.{key}", "provider_ref": f"implementation.image_analysis.{key}", "capability_refs": [capability(item) for item in capabilities], "status": "observed_unqualified", "qualified_implementation_count": 0, "portable": False, "evidence_refs": evidence})

    source["boundary_decisions"] = [row for row in source["boundary_decisions"] if row["decision_id"] != "decision.ao.image_analysis.product"]
    source["boundary_decisions"].append({"decision_id": "decision.ao.image_analysis.product", "subject_ref": PRODUCT, "disposition": "strong_product_candidate", "rationale": "Project, workspace, recipe, run, typed result, comparison, replay and evidence-publication form an independently adopted lifecycle across scientific, medical, industrial and media contexts. Image truth, algorithms, annotations, vertical conclusions and effects remain imported.", "evidence_refs": EVIDENCE, "split_test": {axis: {"score": 2, "finding": f"Image Analysis Workbench has an independently falsifiable {axis} boundary; this does not ratify the product or qualify a provider.", "evidence_refs": EVIDENCE} for axis in ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]}})
    source["crosswalks"] = [row for row in source["crosswalks"] if row["legacy_ref"] != "candidate.product.image_analysis_workbench"]
    source["crosswalks"].append({"legacy_ref": "candidate.product.image_analysis_workbench", "canonical_refs": [PRODUCT, *sorted(lib_ids)], "disposition": "promote_independent_product_and_split_fourteen_workbench_contracts_while_importing_image_truth_methods_and_vertical_authority"})

    prefix = "relation.ao.image_analysis."
    source["relations"] = [row for row in source["relations"] if not row["relation_id"].startswith(prefix)]
    for index, target in enumerate([row["neighbor_ref"] for row in dossier(product)["strategic_and_tactical_ddd"]["context_map"]]):
        source["relations"].append({"relation_id": f"{prefix}{index:02d}", "from_ref": PRODUCT, "predicate": "requires", "to_ref": target, "binding_phase": "compile_time"})
    source["relations"].append({"relation_id": f"{prefix}optional_extension", "from_ref": "component.ao.optional_model_agent_extension", "predicate": "offers", "to_ref": PRODUCT, "binding_phase": "deployment_time"})

    source["negative_tests"] = [row for row in source["negative_tests"] if not row["test_id"].startswith("negative.image_analysis.")]
    negatives = {
        "carrier_identity": "encoded carrier is treated as the image occurrence or decoded sample field",
        "display_truth": "display appearance is treated as radiometric or measurement truth",
        "roi_object": "ROI or segmentation is treated as an accepted domain object",
        "score_label": "score or class candidate is treated as accepted reference truth",
        "completion_validity": "successful method completion is treated as a valid result",
        "recipe_fitness": "type-correct recipe is treated as scientifically fit",
        "comparison_decision": "difference is treated as diagnosis defect or disposition",
        "review_rewrite": "review overwrites source or method result history",
        "publication_acceptance": "publication is treated as downstream acceptance",
        "model_owner": "model or agent is treated as semantic or decision owner",
        "vertical_capture": "medical geospatial inspection or scientific vocabulary is hard-coded horizontally",
        "runtime_collapse": "run plan attempt result and effect receipt are collapsed",
    }
    for key, claim in negatives.items():
        source["negative_tests"].append({"test_id": f"negative.image_analysis.{key}", "prohibited_claim": claim, "expected_result": "REFUSE_WITH_TYPED_NON_COLLAPSE_ERROR"})

    source["semantic_gaps"] = [row for row in source["semantic_gaps"] if not row["gap_id"].startswith("gap.ao.semantic.image_analysis.")]
    for key, statement in {
        "image_profile": "Portable carrier, sample-lattice, radiometry, color and coordinate profile owners remain unratified.",
        "method_equivalence": "Cross-provider image-method semantic and numeric equivalence profiles remain unqualified.",
        "vertical_acceptance": "Two unrelated vertical compositions and domain-owner acceptance evidence are absent.",
    }.items():
        source["semantic_gaps"].append({"gap_id": f"gap.ao.semantic.image_analysis.{key}", "gap_class": "semantic_or_conformance", "statement": statement, "blocking": True, "closure_evidence": "Publish an exact owner/profile, executable law oracle and accepted independent evidence."})

    source["ddd_dossiers"] = [row for row in source["ddd_dossiers"] if row["product_ref"] != PRODUCT] + [dossier(product)]
    source["non_collapse_laws"] = [row for row in source["non_collapse_laws"] if not row.startswith("image occurrence !=")]
    source["non_collapse_laws"].append("image occurrence != carrier != decoded field != layer != region != object != measurement != finding != judgment != downstream decision or effect")
    source["scope"] = "Seven job-specific analytical-operation products, now including Dataset Curation Workbench and Image Analysis Workbench with exact boundaries."
    return source
