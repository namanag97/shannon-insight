#!/usr/bin/env python3
"""Project a complete geospatial-analysis workbench boundary into the analytical corpus."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
METHOD_ROOT = ROOT / "research/domain_atlas/universes/method_kernels"
GSW_ROOT = ROOT / "research/domain_atlas/universes/geospatial_specialized_workbench"
PRODUCT = "product.geospatial_workbench"
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
    "law": "Learned vision/geocoding methods, LLMs or agents may propose classifications, matches, workflows, parameters or explanations only. CRS/datum/epoch/axis semantics, geometry/topology, raster support, accuracy, transformations, workflow execution, evidence and operational authority remain deterministic and reviewable.",
    "removal_law": "Removing every optional learned model, LLM or agent preserves spatial-reference validation, coordinate transformation, vector/raster operations, spatial statistics, project/layer lifecycle, explicit classical geocoding/routing/terrain/trajectory/3D methods when selected, workflow history and accuracy evidence; an explicitly required unavailable method yields capability_unavailable.",
    "hard_work_law": "Automation never replaces feature identity, CRS/datum/epoch/axis order, dimensionality, topology model, grid geometry/nodata/resampling, spatial-temporal support, gazetteer/network/terrain authority, uncertainty and positional accuracy, provider qualification, publication/disclosure authority or vertical acceptance.",
}

EXACT = [
    "library.method_kernels.spatial_reference_semantics",
    "library.method_kernels.coordinate_transform_methods",
    "library.method_kernels.vector_geometry_topology",
    "library.method_kernels.raster_grid_methods",
    "library.method_kernels.spatial_statistics_methods",
]
GAP_KEYS = [
    "geospatial_project_layer_lifecycle",
    "geospatial_workflow_execution_history",
    "geocoding_gazetteer_methods",
    "network_routing_accessibility_methods",
    "trajectory_mobility_methods",
    "terrain_surface_hydrology_methods",
    "point_cloud_3d_methods",
    "spatial_result_accuracy_publication",
]
EXACT_COMPILER_OVERRIDES = {
    "geospatial_project_layer_lifecycle": ["library.spatial_project.definition.compiler", "library.spatial_layer.occurrence.lifecycle"],
    "geospatial_workflow_execution_history": ["library.spatial_workflow.definition.compiler", "library.spatial_workflow.execution.planner", "library.spatial_workflow.run.evidence"],
    "geocoding_gazetteer_methods": ["library.geocode.match.profile.compiler", "library.geocode.gazetteer.resolver", "library.geocode.accuracy.evaluator"],
    "network_routing_accessibility_methods": ["library.spatial_network.profile.compiler", "library.spatial_network.route_accessibility.evaluator"],
    "trajectory_mobility_methods": ["library.trajectory.construction.profile.compiler", "library.trajectory.mobility.evaluator"],
    "terrain_surface_hydrology_methods": ["library.terrain.analysis.profile.compiler", "library.terrain.hydrology.evaluator"],
    "point_cloud_3d_methods": ["library.pointcloud.analysis.profile.compiler", "library.pointcloud.3d.evaluator"],
    "spatial_result_accuracy_publication": ["library.spatial_result.accuracy.appraiser", "library.spatial_result.publication.profile.compiler"],
}
ALL_KEYS = [ref.rsplit(".", 1)[-1] for ref in EXACT] + GAP_KEYS
DEPENDENCIES = {
    "spatial_reference_semantics": [],
    "coordinate_transform_methods": ["spatial_reference_semantics"],
    "vector_geometry_topology": ["spatial_reference_semantics", "coordinate_transform_methods"],
    "raster_grid_methods": ["spatial_reference_semantics", "coordinate_transform_methods"],
    "spatial_statistics_methods": ["spatial_reference_semantics", "vector_geometry_topology", "raster_grid_methods"],
    "geospatial_project_layer_lifecycle": ["spatial_reference_semantics"],
    "geospatial_workflow_execution_history": ["geospatial_project_layer_lifecycle"],
    "geocoding_gazetteer_methods": ["spatial_reference_semantics", "vector_geometry_topology"],
    "network_routing_accessibility_methods": ["spatial_reference_semantics", "vector_geometry_topology"],
    "trajectory_mobility_methods": ["spatial_reference_semantics", "vector_geometry_topology"],
    "terrain_surface_hydrology_methods": ["spatial_reference_semantics", "raster_grid_methods", "vector_geometry_topology"],
    "point_cloud_3d_methods": ["spatial_reference_semantics", "coordinate_transform_methods"],
    "spatial_result_accuracy_publication": ["geospatial_workflow_execution_history", "spatial_statistics_methods"],
}
GAP_DETAILS = {
    "geospatial_project_layer_lifecycle": {
        "types": ["SpatialProjectId", "SpatialProjectEdition", "LayerOccurrence", "LayerRole", "LayerSourceCut", "LayerCrsBinding", "LayerStyleRef", "LayerSupersession"],
        "operations": ["open_spatial_project", "register_layer_occurrence", "bind_layer_crs_and_role", "version_layer", "supersede_project_or_layer"],
        "decisions": ["project_edition", "layer_identity", "layer_role", "source_cut", "style_separation", "supersession"],
        "invariants": ["dataset layer occurrence style and rendered map are distinct", "every layer binds exact source cut CRS support and accuracy", "published layer editions are immutable"],
        "refusals": ["project_scope_missing", "layer_identity_ambiguous", "source_cut_unbound", "crs_binding_missing", "layer_role_invalid", "supersession_conflict"],
        "statement": "No current compiler contribution owns geospatial project/layer occurrence identity, source cuts, CRS/support/accuracy bindings, role, edition and supersession without absorbing storage or visualization.",
    },
    "geospatial_workflow_execution_history": {
        "types": ["SpatialWorkflowEdition", "SpatialOperatorBinding", "LayerPort", "SpatialExecutionPlan", "SpatialRunId", "SpatialRunReceipt", "SpatialWorkflowHistory"],
        "operations": ["author_spatial_workflow", "typecheck_layer_ports", "bind_spatial_operators", "execute_spatial_workflow", "replay_or_compare_run"],
        "decisions": ["operator_admission", "crs_alignment", "materialization_cut", "resource_budget", "replay_equivalence"],
        "invariants": ["workflow edition plan run and result are distinct", "every edge preserves or declares CRS support grain dimensionality loss and accuracy", "provider substitutions preserve run semantics"],
        "refusals": ["layer_port_incompatible", "operator_unqualified", "crs_alignment_unproved", "loss_undeclared", "resource_budget_exceeded", "replay_not_equivalent"],
        "statement": "No current compiler contribution owns typed geospatial workflow/layer ports, operator binding, execution history, spatial loss and replay evidence as one exact contract.",
    },
    "geocoding_gazetteer_methods": {
        "types": ["AddressOrPlaceQuery", "GazetteerEdition", "CandidatePlace", "MatchProfile", "GeocodeResult", "ReverseGeocodeResult", "MatchUncertainty"],
        "operations": ["normalize_place_query", "geocode", "reverse_geocode", "rank_place_candidates", "evaluate_geocode_accuracy"],
        "decisions": ["gazetteer_authority", "locale_and_language", "candidate_generation", "match_threshold", "ambiguity_policy", "privacy_policy"],
        "invariants": ["address text place identity coordinate and administrative area are distinct", "match score is not identity decision", "gazetteer edition and positional uncertainty are retained"],
        "refusals": ["gazetteer_unbound", "query_locale_ambiguous", "no_candidate", "ambiguous_candidates", "threshold_unmet", "disclosure_denied"],
        "statement": "No current compiler contribution owns provider-neutral geocoding/reverse-geocoding over editioned gazetteers with ambiguity, locale, authority, uncertainty and privacy contracts.",
    },
    "network_routing_accessibility_methods": {
        "types": ["SpatialNetwork", "NetworkTopology", "ImpedanceProfile", "TurnRestriction", "RouteRequest", "RouteResult", "Isochrone", "AccessibilityMeasure"],
        "operations": ["build_spatial_network", "validate_network_topology", "route", "compute_isochrone", "measure_accessibility"],
        "decisions": ["network_edition", "mode_and_impedance", "turn_and_access_rules", "time_dependence", "path_tie_break", "unreachable_policy"],
        "invariants": ["geometric proximity is not network reachability", "route is not authorized itinerary or dispatch", "network/rule/time editions bind every result"],
        "refusals": ["network_unbound", "topology_invalid", "mode_unsupported", "restriction_ambiguous", "destination_unreachable", "budget_exhausted"],
        "statement": "No current compiler contribution owns spatial-network topology, routing, isochrone and accessibility methods with mode, impedance, restriction, time and unreachable semantics.",
    },
    "trajectory_mobility_methods": {
        "types": ["MovingObjectRef", "Trajectory", "TrajectorySample", "TemporalInterpolationProfile", "StopMoveSegmentation", "MapMatchResult", "MobilityPattern"],
        "operations": ["construct_trajectory", "interpolate_trajectory", "segment_stops_and_moves", "map_match", "compare_trajectories"],
        "decisions": ["object_identity", "sampling_and_order", "interpolation", "map_matching", "gap_policy", "privacy_aggregation"],
        "invariants": ["sample sequence trajectory inferred path and actual movement are distinct", "gaps and interpolation are explicit", "map match is a hypothesis with uncertainty"],
        "refusals": ["object_identity_missing", "time_order_invalid", "sampling_insufficient", "gap_too_large", "network_unbound", "map_match_ambiguous", "privacy_scope_denied"],
        "statement": "No current compiler contribution owns moving-object trajectory construction, interpolation, segmentation, map matching and mobility comparison with sampling, gaps, uncertainty and privacy contracts.",
    },
    "terrain_surface_hydrology_methods": {
        "types": ["ElevationSurface", "TerrainProfile", "SlopeAspectResult", "Watershed", "FlowNetwork", "VisibilityResult", "SurfaceUncertainty"],
        "operations": ["derive_slope_aspect", "delineate_watershed", "route_surface_flow", "compute_viewshed", "evaluate_surface_accuracy"],
        "decisions": ["elevation_datum", "surface_interpolation", "sink_fill_policy", "flow_algorithm", "visibility_model", "uncertainty_propagation"],
        "invariants": ["elevation datum and vertical CRS are mandatory", "filled surface is derived and never source truth", "terrain resolution and uncertainty bound claims"],
        "refusals": ["vertical_crs_missing", "surface_invalid", "resolution_insufficient", "sink_policy_missing", "flow_algorithm_unsupported", "uncertainty_unbounded"],
        "statement": "No current compiler contribution owns terrain/surface/hydrology methods with vertical CRS, resolution, derivation, algorithm and uncertainty semantics.",
    },
    "point_cloud_3d_methods": {
        "types": ["PointCloud", "PointAttributeSchema", "ThreeDimensionalCrs", "SpatialIndex3D", "SegmentationResult3D", "SurfaceOrMesh", "Accuracy3D"],
        "operations": ["validate_point_cloud", "index_point_cloud", "segment_or_classify_points", "derive_surface_or_mesh", "measure_3d_accuracy"],
        "decisions": ["3d_reference_frame", "attribute_schema", "lod_and_tiling", "classification_profile", "surface_reconstruction", "accuracy_model"],
        "invariants": ["2D footprint 2.5D surface 3D point cloud mesh and solid are distinct", "classification is not physical-object identity", "LOD and tiling never silently change accuracy claims"],
        "refusals": ["3d_crs_missing", "attribute_schema_invalid", "point_budget_exceeded", "lod_unsupported", "classification_unqualified", "surface_reconstruction_failed"],
        "statement": "No current compiler contribution owns point-cloud/3D validation, indexing, segmentation/classification and surface/mesh derivation with reference-frame, LOD, attributes and accuracy contracts.",
    },
    "spatial_result_accuracy_publication": {
        "types": ["SpatialResultEdition", "SpatialAccuracyStatement", "SupportAndScaleStatement", "SpatialLineageBundle", "SpatialPublicationProfile", "SpatialRecallNotice"],
        "operations": ["seal_spatial_result", "appraise_spatial_accuracy", "publish_spatial_result", "retract_or_recall_spatial_result", "propagate_spatial_supersession"],
        "decisions": ["result_identity", "accuracy_claim", "support_scale_and_resolution", "audience_disclosure", "publication_authority", "recall_scope"],
        "invariants": ["algorithm output accepted result publication map decision and effect are distinct", "accuracy/support/scale/CRS travel with every published result", "recall preserves history and propagates"],
        "refusals": ["result_unsealed", "accuracy_evidence_missing", "support_or_scale_ambiguous", "publication_authority_missing", "disclosure_denied", "recall_scope_ambiguous"],
        "statement": "No current compiler contribution owns geospatial result identity, accuracy/support/scale appraisal, publication, supersession, retraction and recall without collapsing into generic artifact storage or map rendering.",
    },
}
RECEIPTS = {
    "spatial_reference_semantics": "receipt.method_kernel.spatial_reference",
    "coordinate_transform_methods": "receipt.method_kernel.coordinate_transform",
    "vector_geometry_topology": "receipt.method_kernel.vector_geometry_topology",
    "raster_grid_methods": "receipt.method_kernel.raster_grid",
    "spatial_statistics_methods": "receipt.method_kernel.spatial_statistics",
}


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


UPSTREAM = {row["library_id"]: row for row in jsonl(METHOD_ROOT / "library-boundaries.jsonl")}
SOURCE_ROWS = {row["source_id"]: row for row in jsonl(METHOD_ROOT / "sources.jsonl")}
SELECTED_SOURCE_REFS = sorted({ref for ident in EXACT for ref in UPSTREAM[ident]["evidence_refs"]})
GSW_SOURCES = jsonl(GSW_ROOT / "sources.jsonl")
GSW_LIBRARIES = {row["library_id"]: row for row in jsonl(GSW_ROOT / "library-contracts.jsonl")}
GSW_COMPILER = jsonl(GSW_ROOT / "compiler-contracts.jsonl")
GSW_REQUIREMENTS = {row["subject_ref"]: row["requirement_id"] for row in GSW_COMPILER if row.get("record_kind") == "capability_requirement"}
GSW_PROFILES = {row["subject_ref"]: row["receipt_id"] for row in jsonl(GSW_ROOT / "qualification-profiles.jsonl")}
GSW_EVIDENCE_REFS = [row["source_id"] for row in GSW_SOURCES]


def key_of(ref: str) -> str:
    return ref.rsplit(".", 1)[-1]


def local_library(key: str) -> str:
    return f"library.analytics_geospatial.{key}"


def local_capability(key: str) -> str:
    return f"capability.analytics_geospatial.{key}"


def source_rows() -> list[dict[str, Any]]:
    result = []
    for ref in SELECTED_SOURCE_REFS:
        row = SOURCE_ROWS[ref]
        result.append({"source_id": ref, "source_class": "primary_research" if row["kind"] == "primary_research" else "official_specification_or_documentation", "title": row["title"], "publisher": row["publisher"], "uri": row["url"], "retrieved_at": row["accessed_at"], "claim": row["authority_scope"], "scope_limit": row["limitations"]})
    result.extend({"source_id": row["source_id"], "source_class": "primary_research" if any(token in row["authority"] for token in ("Tarboton", "Jenson", "Newson")) else "official_specification_or_documentation", "title": row["title"], "publisher": row["authority"], "uri": row["url"], "retrieved_at": row["retrieved"], "claim": row["supports"], "scope_limit": row["does_not_prove"]} for row in GSW_SOURCES)
    return result


def capability(key: str) -> dict[str, Any]:
    exact = next((ref for ref in EXACT if key_of(ref) == key), None)
    evidence = UPSTREAM[exact]["evidence_refs"] if exact else GSW_EVIDENCE_REFS
    return {"artifact_id": local_capability(key), "kind": "capability", "name": key.replace("_", " ").title(), "status": "specified_candidate", "semantic_owner_ref": "semantic.geospatial_analysis" if exact else "semantic.geospatial_project", "adoption_unit": False, "operated": False, "definition": f"Expose geospatial {key.replace('_', ' ')} with exact reference, support, accuracy, loss, authority, refusal and evidence contracts.", "evidence_refs": evidence}


def exact_library(ref: str) -> dict[str, Any]:
    row = UPSTREAM[ref]
    key = key_of(ref)
    laws = list(row["laws"])
    laws.extend({
        "spatial_reference_semantics": ["CRS, datum, coordinate epoch, axis order, dimensionality, spatial support and accuracy are non-interchangeable."],
        "coordinate_transform_methods": ["A coordinate transform binds an exact operation pipeline and resources; coordinate conversion never silently becomes datum transformation."],
        "vector_geometry_topology": ["Geometry validity, topology model, precision and repair loss are explicit; repaired geometry is a new derived occurrence."],
        "raster_grid_methods": ["Grid geometry, cell support, nodata, resampling and extent determine result identity; resampling never invents source resolution."],
        "spatial_statistics_methods": ["Spatial weights/support, sampling design, model assumptions and uncertainty bind every estimate; clustering or correlation is not cause."],
    }[key])
    provides = [local_capability(key)]
    if key == "vector_geometry_topology":
        provides.append("capability.analyze_geospatial")
    return {"library_id": local_library(key), "class": row["library_kind"], "owner_ref": "semantic.geospatial_analysis", "provides": provides, "types": row["public_types"], "operations": row["operation_refs"], "decisions": row["decision_refs"], "invariants": laws, "refusals": row["error_contracts"], "dependencies": [local_library(dep) for dep in DEPENDENCIES[key]], "effect_boundary": row["effect_boundary"], "evidence_refs": row["evidence_refs"], "product_refs": [PRODUCT]}


def gap_library(key: str) -> dict[str, Any]:
    spec = GAP_DETAILS[key]
    return {"library_id": local_library(key), "class": "semantic_algorithm_pure" if key not in {"geospatial_project_layer_lifecycle", "geospatial_workflow_execution_history", "spatial_result_accuracy_publication"} else "semantic_policy_pure", "owner_ref": "semantic.geospatial_project", "provides": [local_capability(key)], "types": spec["types"], "operations": spec["operations"], "decisions": spec["decisions"], "invariants": spec["invariants"], "refusals": spec["refusals"], "dependencies": [local_library(dep) for dep in DEPENDENCIES[key]], "effect_boundary": "pure_effect_intents_only" if key == "spatial_result_accuracy_publication" else "pure_no_io", "evidence_refs": GSW_EVIDENCE_REFS, "product_refs": [PRODUCT]}


def product_truth() -> dict[str, Any]:
    return {
        "sovereign_question": "For exact editioned spatial layers, reference systems, supports, scales, accuracy and workflow definitions, what transformed, topological, raster, statistical, network, trajectory, terrain, 3D or geocoded result can be established and published without mistaking representation for territory, proximity for reachability, correlation for cause, or analysis for operational authority?",
        "users": ["gis_analyst", "geospatial_data_engineer", "cartographer_or_visual_analyst", "remote_sensing_or_terrain_analyst", "network_or_mobility_analyst", "domain_planner", "spatial_service_operator", "accuracy_or_assurance_reviewer"],
        "harmed_parties": ["mapped_person_or_household", "land_or_asset_owner", "traveler_or_worker", "community", "indigenous_or_sensitive_location_group", "decision_affected_party", "environment_or_ecosystem"],
        "jobs": ["Create editioned spatial projects and layers; validate reference/support/accuracy; transform coordinates; analyze vector/raster/spatial statistics; run geocoding, network, trajectory, terrain and 3D methods; retain workflow histories; and publish scoped spatial results with loss and uncertainty evidence."],
        "outcomes": ["crs_datum_epoch_axis_safe_layers", "validated_vector_and_raster_occurrences", "operation_specific_transform_accuracy", "topology_and_nodata_preserving_analysis", "support_and_uncertainty_bound_spatial_estimates", "typed_geocode_route_trajectory_terrain_or_3d_result", "replayable_spatial_workflow_receipt", "published_result_with_crs_scale_support_accuracy_and_recall"],
        "negative_mission": "Does not own source feature/place/asset identity, territory or legal boundary truth, base-map/gazetteer/network authority, storage/index/query engines, generic image/ML methods, cartographic UI/rendering, routing dispatch, planning/optimization decisions, operational location effects, disclosure authority or vertical acceptance.",
        "lifecycle_states": ["draft", "project_open", "layers_registering", "reference_validation", "ready", "workflow_draft", "workflow_typechecked", "provider_unbound", "queued", "running", "partial", "completed", "accuracy_review", "accepted_as_spatial_result", "publication_pending", "published", "retracted", "recalled", "superseded", "failed"],
        "commands": ["open_spatial_project", "register_layer_occurrence", "bind_spatial_reference_support_and_accuracy", "validate_geometry_or_grid", "author_spatial_workflow", "bind_spatial_methods", "execute_coordinate_transform", "execute_vector_or_raster_analysis", "execute_spatial_statistics", "execute_geocode_route_trajectory_terrain_or_3d_method", "record_spatial_run", "appraise_spatial_accuracy", "publish_spatial_result", "retract_or_recall_spatial_result", "supersede_project_or_layer"],
        "events": ["spatial_project_opened", "layer_occurrence_registered", "spatial_reference_support_and_accuracy_bound", "geometry_or_grid_validated", "spatial_workflow_authored", "spatial_methods_bound", "coordinate_transform_executed", "vector_or_raster_analysis_executed", "spatial_statistics_executed", "specialized_spatial_method_executed", "spatial_run_recorded", "spatial_accuracy_appraised", "spatial_result_published", "spatial_result_retracted_or_recalled", "project_or_layer_superseded"],
        "invariants": ["territory feature identity geometry layer map analysis result decision and effect are distinct", "CRS datum epoch axis order dimensionality support scale resolution and accuracy are explicit", "source and transformed coordinates/geometry/raster are separately identified", "geometry repair resampling interpolation classification and map matching create derived occurrences with loss", "geometric proximity is not network reachability", "address or place match score is not identity or jurisdiction truth", "spatial association or hotspot is not cause", "2D 2.5D 3D point cloud mesh and solid are distinct", "workflow edition plan run result and publication remain separately traceable", "spatial result never authorizes routing dispatch land-use emergency or other external effect"],
        "refusals": ["source_layer_or_identity_unbound", "crs_or_axis_ambiguous", "datum_or_epoch_missing", "transform_pipeline_unavailable", "accuracy_grid_resource_missing", "invalid_geometry_or_topology", "grid_geometry_or_nodata_ambiguous", "support_scale_or_resolution_mismatch", "spatial_method_assumption_unmet", "gazetteer_or_network_unbound", "trajectory_sampling_insufficient", "vertical_crs_missing", "3d_schema_unsupported", "provider_unqualified", "publication_or_disclosure_authority_missing", "operational_effect_requested"],
        "automation_modality": AUTOMATION,
    }


def dossier() -> dict[str, Any]:
    truth = product_truth()
    ddd = {
        "domain_vision_statement": "Own provider-neutral geospatial project and analytical-workflow lifecycles that preserve reference, support, topology, scale, accuracy, loss and evidence without claiming territory truth or operational authority.",
        "subdomain_classification": "core_horizontal_geospatial_analysis_workbench_product",
        "bounded_context_boundary": {"inside": ["spatial project/layer occurrence editions and roles", "CRS datum coordinate epoch axis order dimensionality support scale resolution and accuracy", "coordinate-operation pipeline selection and transformation evidence", "vector geometry validity topology predicates overlay and repair", "raster/grid warping resampling nodata map algebra and zonal aggregation", "spatial weights autocorrelation models interpolation and uncertainty", "gazetteer geocoding and reverse geocoding results", "spatial networks routing isochrones and accessibility", "moving-object trajectories interpolation segmentation and map matching", "terrain surface hydrology and visibility methods", "point-cloud/3D indexing classification segmentation and surface derivation", "typed spatial workflows execution histories result appraisal publication retraction and recall"], "outside": ["source feature place asset and legal boundary identity/truth", "base-map gazetteer network terrain and observation-source authority", "generic storage index query/tiling resources", "generic image/remote-sensing classification and learned-model lifecycle", "cartographic styling rendering and UI consumption", "optimization planning routing dispatch and operational action", "privacy/disclosure/legal authority", "vertical acceptance"]},
        "ubiquitous_language_policy": "Territory, feature, place, address, asset, geometry, topology, coordinate, CRS, datum, epoch, axis, support, scale, resolution, accuracy, layer, project, map, raster, coverage, point cloud, trajectory, network, route, terrain, workflow, run, spatial result, publication, decision and effect are non-interchangeable. Learned spatial methods are qualified algorithms, not an AI truth class.",
        "context_map": [
            {"neighbor_ref": "context.vertical_spatial_identity", "relationship": "customer_supplier_acl", "translation": "consume feature/place/asset/boundary meaning and authority without owning it"},
            {"neighbor_ref": "context.source_data_and_quality", "relationship": "customer_supplier", "translation": "consume layer cuts completeness lineage and purpose-scoped quality evidence"},
            {"neighbor_ref": "context.spatial_standards_and_registries", "relationship": "conformist_acl", "translation": "resolve exact CRS datum operation units schema and standard editions"},
            {"neighbor_ref": "product.query_and_storage", "relationship": "customer_supplier", "translation": "consume indexed spatial/raster/point-cloud occurrences without owning persistence"},
            {"neighbor_ref": "context.image_remote_sensing_methods", "relationship": "customer_supplier_acl", "translation": "import classified/derived imagery with method and accuracy evidence"},
            {"neighbor_ref": "product.optimization_solver", "relationship": "anti_corruption_layer", "translation": "location-allocation and routing decisions remain optimization/decision problems"},
            {"neighbor_ref": "product.visualization_consumption", "relationship": "published_language", "translation": "publish layer/result contracts; styling/rendering and interaction remain external"},
            {"neighbor_ref": "product.lineage_provenance", "relationship": "published_language", "translation": "publish source transform resource workflow result and accuracy receipts"},
            {"neighbor_ref": "context.operational_location_effects", "relationship": "effect_port", "translation": "publish spatial evidence only; dispatch control land-use or emergency effects remain external"},
        ],
        "anti_corruption_layers": ["acl.vertical_feature_place_identity", "acl.source_layer", "acl.crs_datum_registry", "acl.spatial_provider", "acl.remote_sensing_model", "acl.storage_query", "acl.visualization_rendering", "acl.optimization_decision", "acl.operational_location_effect"],
        "published_language": ["SpatialProjectId", "SpatialProjectEdition", "LayerOccurrenceRef", "LayerSourceCut", "SpatialReferenceBinding", "SpatialSupport", "AccuracyEnvelope", "SpatialWorkflowEdition", "SpatialRunId", "SpatialResultEdition", "SpatialAccuracyStatement", "SpatialPublicationEdition", "SpatialRecallNotice", "TypedRefusal"],
        "value_objects": ["SpatialProjectId", "LayerOccurrenceId", "CrsRef", "DatumRef", "CoordinateEpoch", "AxisOrder", "DimensionProfile", "SpatialSupport", "ScaleOrResolution", "AccuracyEnvelope", "TopologyModel", "GridGeometry", "NoDataProfile", "GazetteerEditionRef", "NetworkEditionRef", "WorkflowDigest", "SpatialResultDigest"],
        "entities": ["SpatialProject", "LayerOccurrence", "SpatialWorkflowEdition", "SpatialRun", "SpatialResultEdition", "SpatialAccuracyAppraisal", "SpatialPublication"],
        "aggregates": [
            {"root": "SpatialProject", "members": ["scope", "layers", "workflow_refs", "result_refs", "authority_refs", "state"], "consistency": "project and layer changes create immutable editions and explicit supersession"},
            {"root": "LayerOccurrence", "members": ["source_cut", "feature_or_grid_schema", "reference", "support", "scale", "accuracy", "role", "lineage"], "consistency": "layer identity binds exact source and every interpretation-relevant spatial decision"},
            {"root": "SpatialWorkflowEdition", "members": ["layer_ports", "operators", "parameters", "reference_alignment", "loss_policy", "budgets", "digest"], "consistency": "each edge declares CRS/support/grain/dimensionality/accuracy preservation or loss"},
            {"root": "SpatialRun", "members": ["workflow_ref", "input_layers", "provider_occurrences", "resources", "progress", "outputs", "receipt"], "consistency": "run identity binds exact inputs providers resources and configuration"},
            {"root": "SpatialResultEdition", "members": ["run_ref", "carrier_ref", "reference", "support", "scale", "accuracy", "limitations", "publication", "recall"], "consistency": "claims cannot exceed input/method evidence and publication never mutates result"},
        ],
        "aggregate_roots": ["SpatialProject", "LayerOccurrence", "SpatialWorkflowEdition", "SpatialRun", "SpatialResultEdition"],
        "aggregate_invariants": truth["invariants"] + ["all transform resources and grid files participate in run identity", "dynamic-datum transforms bind coordinate epoch", "mixed CRS/support layers never combine without an explicit operation", "partial outputs declare valid extent/support and cancellation state", "provider identity cannot change spatial semantics"],
        "commands": truth["commands"], "domain_events": truth["events"],
        "refusal_failure_catalog": truth["refusals"] + ["resource_exhausted", "cancelled", "numerical_failure", "provider_failure", "partial_extent_only", "optional_assistance_unavailable"],
        "domain_services": ["SpatialReferenceBindingService", "CoordinateOperationService", "GeometryTopologyService", "RasterGridService", "SpatialStatisticsService", "GeocodingService", "NetworkAnalysisService", "TrajectoryAnalysisService", "TerrainAnd3DService", "SpatialWorkflowService", "SpatialAccuracyAppraisalService"],
        "application_services": ["OpenSpatialProjectUseCase", "RegisterLayerUseCase", "AuthorSpatialWorkflowUseCase", "ExecuteSpatialWorkflowUseCase", "AnalyzeNetworkOrTrajectoryUseCase", "AnalyzeTerrainOr3DUseCase", "AppraiseSpatialResultUseCase", "PublishSpatialResultUseCase", "RecallOrSupersedeSpatialResultUseCase"],
        "repositories": ["SpatialProjectRepository", "LayerOccurrenceRepository", "SpatialWorkflowRepository", "SpatialRunRepository", "SpatialResultRepository"],
        "factories": ["SpatialProjectFactory", "LayerOccurrenceFactory", "SpatialWorkflowFactory", "SpatialRunFactory", "SpatialResultFactory"],
        "specifications": ["SpatialReferenceSpecification", "CoordinateEpochSpecification", "GeometryTopologySpecification", "GridNoDataSpecification", "SupportScaleAccuracySpecification", "GazetteerMatchSpecification", "NetworkTopologySpecification", "TrajectorySamplingSpecification", "VerticalCrsTerrainSpecification", "PointCloudSchemaSpecification", "WorkflowLossSpecification", "SpatialPublicationSpecification"],
        "state_machine": {"project": truth["lifecycle_states"], "layer": ["registered", "reference_pending", "validated", "invalid", "active", "superseded", "withdrawn"], "workflow": ["draft", "typecheck_pending", "typechecked", "provider_unbound", "ready", "running", "completed", "partial", "failed", "superseded"], "result": ["raw", "accuracy_review", "accepted", "publication_pending", "published", "retracted", "recalled", "superseded"]},
        "policies_and_reactions": ["when CRS datum epoch or axis is ambiguous refuse", "when operation resources or grids are missing refuse or narrow accuracy", "when geometry is repaired retain source and derived identity plus loss", "when rasters resample publish new grid geometry and accuracy", "when geocode/map-match candidates are ambiguous retain alternatives", "when network and Euclidean conclusions differ preserve both semantics", "when spatial association is found prohibit causal wording", "when privacy or sensitive-location policy denies disclosure suppress publication without rewriting result", "when a material source/transform defect is discovered recall affected result editions", "when a result is proposed for action require external planning and operational authority"],
        "sagas_and_process_managers": ["LayerAdmissionProcess", "CoordinateResourceResolutionProcess", "SpatialWorkflowExecutionProcess", "PartialRunReconciliationProcess", "SpatialAccuracyAppraisalProcess", "SpatialPublicationProcess", "SpatialRecallProcess", "CrossProviderDifferentialProcess"],
        "read_models_and_projections": ["SpatialProjectView", "LayerReferenceAndAccuracyView", "WorkflowGraphView", "SpatialRunProgressView", "TransformPipelineView", "GeometryAndGridValidityView", "NetworkTrajectoryTerrain3DResultView", "SpatialAccuracyEvidenceView", "PublicationAndRecallView"],
        "integration_event_policy": "Only editioned project/layer/reference/workflow/run/result/accuracy/publication/recall facts cross the boundary. Source identity truth, provider internals, rendering interactions, planning decisions, location effects and outcomes remain external.",
        "concurrency_and_idempotency": ["optimistic project/layer/workflow/result editions", "registered layers workflows and accepted results are immutable", "idempotency binds workflow input cuts providers resources configuration and run identity", "parallel tiling/partitioning declares merge/order equivalence", "partial/cancelled output has typed extent validity", "unknown provider completion reconciles before retry", "publication and recall are monotone receipt-bearing operations"],
        "time_model": ["feature event time observation time recording time validity time coordinate epoch source cut run time publication time and decision time are distinct", "moving-object trajectories retain sampling times and gaps", "time-dependent networks bind rule/traffic cut", "dynamic CRS and deformation models bind epoch", "layers/results have validity and supersession", "accuracy evidence has applicability and expiry"],
        "event_storming_swimlanes": ["vertical_feature_place_owner", "spatial_data_steward", "gis_analyst", "geodesy_or_crs_authority", "method_provider", "workflow_runtime", "accuracy_reviewer", "privacy_disclosure_authority", "map_or_api_consumer", "planning_decision_owner", "affected_party"],
        "nonfunctional_laws": ["finite features cells points edges trajectories work memory concurrency external cost and result volume", "cooperative cancellation with typed spatial extent validity", "numeric precision robustness topology and tolerance are explicit", "axis-order datum-epoch antimeridian polar nodata invalid-geometry and singular-network negative twins", "OGC/EPSG/reference and cross-provider differential fixtures", "accuracy and uncertainty propagate monotonically or are explicitly recomputed", "unsafe FFI native providers and generated bindings remain isolated", "receipts bind source cuts references operation resources workflow provider configuration result and authority", "provider identity cannot change semantics", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {"dossier_id": "ddd.analytics.geospatial_workbench", "product_ref": PRODUCT, "status": "candidate_not_ratified", "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]}, "strategic_and_tactical_ddd": ddd}


def enrich_geospatial(source: dict[str, Any]) -> dict[str, Any]:
    caps = {local_capability(key) for key in ALL_KEYS}
    libs = {local_library(key) for key in ALL_KEYS}
    reqs = {f"requirement.analytics_geospatial.{key}" for key in ALL_KEYS}
    maps = {f"binding.analytics_geospatial.{key}" for key in ALL_KEYS}
    gaps = {f"gap.analytics_geospatial.{key}" for key in GAP_KEYS}
    negatives = {f"negative.geospatial.{key}" for key in ["territory_geometry", "crs_drop", "axis_epoch", "repair_truth", "raster_resolution", "proximity_reachability", "match_identity", "association_cause", "map_action", "agent_authority"]}
    laws = {"territory != feature identity != geometry != layer != map != analytical result", "CRS != datum != coordinate epoch != axis order != dimensionality != support != accuracy", "source geometry or raster != repaired transformed resampled interpolated or classified derivative", "geometric proximity != network reachability", "address or place match score != identity or jurisdiction truth", "spatial association or hotspot != causal effect", "map or published result != decision != operational location effect", "model or agent proposal != accepted spatial semantics evidence or authority"}

    source["sources"] = [row for row in source["sources"] if row["source_id"] not in set(SELECTED_SOURCE_REFS) | set(GSW_EVIDENCE_REFS)] + source_rows()
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in caps]
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in libs | {"library.geospatial_core"}]
    source["requirements"] = [row for row in source["requirements"] if row["requirement_id"] not in reqs]
    source["binding_maps"] = [row for row in source.get("binding_maps", []) if row["binding_map_id"] not in maps | {"binding.analytics.geospatial"}]
    source["binding_gaps"] = [row for row in source.get("binding_gaps", []) if row["gap_id"] not in gaps]
    source["negative_tests"] = [row for row in source["negative_tests"] if row["test_id"] not in negatives]
    source["non_collapse_laws"] = [law for law in source["non_collapse_laws"] if law not in laws]
    source["ddd_dossiers"] = [row for row in source.get("ddd_dossiers", []) if row.get("product_ref") != PRODUCT]

    next(row for row in source["artifacts"] if row["artifact_id"] == PRODUCT).update(product_truth())
    source["artifacts"].extend(capability(key) for key in ALL_KEYS)
    source["libraries"].extend(exact_library(ref) for ref in EXACT)
    source["libraries"].extend(gap_library(key) for key in GAP_KEYS)
    exact_by_key = {key_of(ref): ref for ref in EXACT}
    for key in ALL_KEYS:
        concrete_refs = [exact_by_key[key]] if key in exact_by_key else EXACT_COMPILER_OVERRIDES.get(key, [])
        concrete_requirement_refs = (list(UPSTREAM[exact_by_key[key]]["requirement_refs"]) if key in exact_by_key else [GSW_REQUIREMENTS[ref] for ref in concrete_refs])
        qualification_profile_refs = ([RECEIPTS[key]] if key in exact_by_key else [GSW_PROFILES[ref] for ref in concrete_refs])
        gap_id = f"gap.analytics_geospatial.{key}"
        source["requirements"].append({"requirement_id": f"requirement.analytics_geospatial.{key}", "consumer_ref": PRODUCT, "capability_ref": local_capability(key), "binding_phase": "runtime" if key in {"geospatial_workflow_execution_history", "spatial_result_accuracy_publication"} else "compile_time", "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{key}_implementation"})
        source["binding_maps"].append({"binding_map_id": f"binding.analytics_geospatial.{key}", "abstract_library_ref": local_library(key), "concrete_library_refs": concrete_refs, "concrete_requirement_refs": concrete_requirement_refs, "composition_law": "Exact geospatial contribution; source identity, storage/query, visualization, generic image/model methods, decision authority and operational effects remain imported.", "bindability": "structurally_bindable_unqualified" if concrete_refs else "structurally_partial_blocking_gap", "blocking_gap_refs": [] if concrete_refs else [gap_id], "modality_posture": "deterministic_core", "minimum_qualified_implementations_per_required_contract": 1, "portable_claim_minimum_independent_implementations": 2, "qualification_profile_refs": qualification_profile_refs, "substitution_law": "Reference datum epoch axis dimensionality support scale topology grid nodata time accuracy loss resource result and failure semantics survive substitution.", "cross_provider_differential_required": True, "fallback_law": "refuse", "status": "candidate_not_bound", "product_refs": [PRODUCT]})
        if not concrete_refs:
            source["binding_gaps"].append({"gap_id": gap_id, "status": "open", "product_refs": [PRODUCT], "abstract_library_refs": [local_library(key)], "missing_contracts": [key], "statement": GAP_DETAILS[key]["statement"], "compiler_disposition": f"Add an editioned compiler library contribution for {key} with exact types, operations, decisions, laws, refusals, finite bounds, removal seams, official/reference fixtures and two independently qualified implementations."})
    source["ddd_dossiers"].append(dossier())
    source["negative_tests"].extend([
        {"test_id": "negative.geospatial.territory_geometry", "prohibited_claim": "A geometry, layer or map is the territory, legal boundary or authoritative feature identity.", "expected_result": "retain external identity/authority and representation scope"},
        {"test_id": "negative.geospatial.crs_drop", "prohibited_claim": "Coordinates remain meaningful after dropping CRS, datum, epoch or axis order.", "expected_result": "refuse the unreferenced coordinates"},
        {"test_id": "negative.geospatial.axis_epoch", "prohibited_claim": "Axis order and coordinate epoch can be inferred from provider defaults.", "expected_result": "require exact editioned bindings"},
        {"test_id": "negative.geospatial.repair_truth", "prohibited_claim": "Geometry repair preserves source identity and truth without loss.", "expected_result": "create a derived occurrence and loss receipt"},
        {"test_id": "negative.geospatial.raster_resolution", "prohibited_claim": "Resampling increases source resolution or removes uncertainty.", "expected_result": "retain source support and derived grid/accuracy"},
        {"test_id": "negative.geospatial.proximity_reachability", "prohibited_claim": "Euclidean proximity proves network reachability or travel time.", "expected_result": "bind exact network mode impedance and restrictions"},
        {"test_id": "negative.geospatial.match_identity", "prohibited_claim": "A geocode or map-match score proves place/object identity.", "expected_result": "retain candidates uncertainty and external identity authority"},
        {"test_id": "negative.geospatial.association_cause", "prohibited_claim": "A hotspot or spatial association proves a causal mechanism.", "expected_result": "publish association with support and uncertainty only"},
        {"test_id": "negative.geospatial.map_action", "prohibited_claim": "A spatial result or map authorizes dispatch, boundary change or other effect.", "expected_result": "require external decision and effect authority"},
        {"test_id": "negative.geospatial.agent_authority", "prohibited_claim": "An agent fills missing reference, topology, gazetteer, accuracy, disclosure or authority evidence.", "expected_result": "retain proposal taint and deterministic obligations"},
    ])
    source["non_collapse_laws"].extend(sorted(laws))
    crosswalk = next(row for row in source["crosswalks"] if row["legacy_ref"] == "candidate.product.geospatial_analytics")
    crosswalk["canonical_refs"] = [PRODUCT, "semantic.geospatial_project", "semantic.geospatial_analysis", *[local_library(key) for key in ALL_KEYS], "standard.ogc_api_features"]
    crosswalk["disposition"] = "split_workbench_exact_foundation_and_specialized_libraries_from_standard"
    return source
