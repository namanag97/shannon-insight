#!/usr/bin/env python3
"""Quotient-based convergence of the remaining presentation research frontier."""

from __future__ import annotations

from typing import Any


PRODUCT_DECISION_ROWS = [
    ("hypothesis.presentation.operational_dashboard", "RETIRE_COMPOSITE_COMPOSE_EXISTING_OWNERS", ["product.interactive_analytics_exploration", "product.signal_condition_diagnostics", "product.integrated_planning_workbench"], "Dashboard composition belongs to exploration; live condition/incident evidence belongs to monitoring products; goals, targets and scorecards belong to planning or vertical performance semantics."),
    ("hypothesis.presentation.analytical_application", "COMPOSE_EXISTING_PRODUCTS_AND_DOMAIN_APP", ["product.embedded_analytics", "product.decision_automation"], "An analytical application is a host-domain application composition importing embedded analytics and decision services; presentation cannot own forms, cases, domain commands or effect authority."),
    ("hypothesis.presentation.computational_document", "RETAIN_EXISTING_PRODUCT", ["product.analytical_notebook"], "The retained analytical-notebook product already owns document, kernel binding, execution history and reproducibility state; presentation libraries are imports."),
    ("hypothesis.presentation.analytical_grid", "DEFER_PRODUCT_RETAIN_CONTRACTS_AND_EXTERNAL_APPLICATION", ["product.self_service_data_preparation", "product.integrated_planning_workbench"], "Grid, cell, formula and recalculation semantics are reusable; spreadsheet application adoption/economics remain external and planning writeback stays with planning authority."),
    ("hypothesis.presentation.embedding", "RETAIN_EXISTING_PRODUCT", ["product.embedded_analytics"], "The retained embedded-analytics product owns host/guest session, entitlement projection, event bridge, tenant isolation and exit contracts."),
    ("hypothesis.presentation.specialized_view", "NO_GENERIC_PRODUCT_ROUTE_TO_SPECIALIZED_PRODUCTS_AND_LIBRARIES", ["product.geospatial_workbench", "product.graph_analysis_workbench", "product.process_mining_workbench", "product.signal_condition_diagnostics", "product.image_analysis_workbench"], "Spatial, graph, process, signal, image and scientific views preserve different topology, coordinate, uncertainty and interaction semantics; a generic specialized-view product would erase those owners."),
    ("hypothesis.presentation.narrative", "AUTHORING_MODE_AND_ARTIFACT_NOT_PRODUCT", ["product.formal_reporting_publication", "product.analytical_notebook"], "Narrative ordering, annotation and claim linking are reusable authoring semantics inside reporting and notebooks; no independent operated promise or exit boundary is proven."),
    ("hypothesis.presentation.external_publication", "COMPOSE_PUBLICATION_EMBED_AND_DISCLOSURE_OWNERS", ["product.formal_reporting_publication", "product.embedded_analytics", "product.data_product_publication", "product.data_use_policy"], "An external portal composes formal artifact issuance, host delivery, data-product publication and disclosure policy; portal packaging does not transfer any of those authorities."),
    ("hypothesis.presentation.accessibility", "CONSTITUTIONAL_REQUIREMENT_AND_LIBRARY_FAMILY_NOT_PRODUCT", ["product.interactive_analytics_exploration", "product.formal_reporting_publication", "product.embedded_analytics", "product.analytical_notebook"], "Accessible task equivalence constrains every analytical experience and renderer; it has no independent business outcome or adoption boundary."),
]


PRODUCT_CONVERGENCE_DECISIONS = [
    {
        "decision_id": f"decision.presentation.convergence.{subject.split('.')[-1].replace('_', '-')}",
        "record_kind": "presentation_product_convergence_decision",
        "subject_ref": subject,
        "verdict": verdict,
        "target_product_refs": targets,
        "rationale": rationale,
        "canonical_mutation": "PENDING_DEPENDENCY_AWARE_MIGRATION" if "RETIRE" in verdict else "NONE_RESEARCH_CROSSWALK_ONLY",
        "ratification": "WITHHELD",
        "completion_claim": False,
    }
    for subject, verdict, targets, rationale in PRODUCT_DECISION_ROWS
]


FAMILY_ROWS = [
    ("presentation_core", "SHARED_PRESENTATION_SEMANTICS", ["presentation_intent", "analytical_result_binding"], ["intent is not execution", "result binding is not source or metric ownership"]),
    ("encoding_composition", "SHARED_PRESENTATION_SEMANTICS", ["visual_encoding_fitness", "composition_layout", "responsive_layout", "uncertainty_encoding", "missingness_encoding", "provenance_disclosure"], ["encoding is not analytical meaning", "layout change cannot silently change task, grain or claim", "absence of a mark is not missingness semantics"]),
    ("interaction_navigation", "INTERACTIVE_EXPLORATION_PRIMARY_SHARED", ["interaction_state", "selection_algebra", "drill_navigation", "bookmark_view_state"], ["selection is not domain command", "drill is not aggregation authority", "bookmark is not a sealed data cut"]),
    ("formal_reporting", "FORMAL_REPORTING_OWNED", ["report_definition", "report_run", "pagination_layout", "publication_lifecycle"], ["definition is not run", "run is not rendition", "publication is not delivery or regulator acceptance"]),
    ("boundary_adapters", "PRODUCT_OWNED_ADAPTER_CONTRACTS", ["notification_port", "embed_entitlement_projection"], ["attention intent is not notification delivery", "host identity is not guest entitlement"]),
    ("accessibility_equivalence", "CONSTITUTIONAL_SHARED_LIBRARY", ["accessible_task_equivalent"], ["pixel or ARIA emission is not task equivalence", "alternative representation must preserve supported task and claim semantics"]),
    ("specialized_portrayal", "SPECIALIZED_PRODUCT_OWNED_LIBRARIES", ["map_portrayal", "tile_delivery", "graph_layout_view", "signal_view", "volume_scene_view"], ["map is not generic chart", "graph layout is not graph topology", "tile is not source feature", "signal view is not sampled signal", "scene is not scientific model"]),
    ("assurance_operations", "SHARED_ASSURANCE_AND_RUNTIME_LIBRARIES", ["visual_regression_oracle", "semantic_equivalence_oracle", "presentation_resource_budget", "presentation_usage_evidence"], ["pixel similarity is not semantic equivalence", "usage event is not user intent", "resource exhaustion is typed partiality"]),
    ("content_collaboration", "SHARED_CONTENT_CONTROL_PLANE", ["annotation_collaboration"], ["annotation is not target artifact", "comment is not approval", "mention is not accountable assignment"]),
]


LIBRARY_CONSTITUTIONS = [
    {
        "constitution_id": f"constitution.presentation.{ident.replace('_', '-')}",
        "record_kind": "presentation_library_family_constitution",
        "name": ident,
        "owner_posture": owner,
        "member_names": members,
        "laws": laws,
        "required_axes": ["subject_identity_grain", "state_change", "time", "order_topology", "composition", "partiality_uncertainty", "authority_effect", "representation", "compatibility", "privacy_security_safety", "resources_failure", "evidence_conformance"],
        "inheritance_law": "A family law is inherited only when the exact member applicability docket says REQUIRED; silence never implies applicability.",
        "status": "CANDIDATE_UNRATIFIED",
        "completion_claim": False,
    }
    for ident, owner, members, laws in FAMILY_ROWS
]


# name, family, exact candidate ref, owner, types, operations, invariant, refusal
CONTRACT_ROWS = [
    ("presentation_intent", "presentation_core", "library.presentation.presentation_intent", "SHARED_PRESENTATION_SEMANTICS", ["PresentationIntent", "AudienceTask", "ClaimPosture", "ArtifactKindRef"], ["validate_intent", "canonicalize_intent", "specialize_intent"], "intent carries audience, task, claim and artifact posture without selecting a provider", "intent_incomplete"),
    ("analytical_result_binding", "presentation_core", "library.presentation.analytical_result_binding", "SHARED_PRESENTATION_SEMANTICS", ["ResultBinding", "ResultEditionRef", "SemanticEditionRef", "DataCutRef"], ["bind_result", "validate_binding", "mark_stale"], "binding preserves identity grain type unit time uncertainty missingness provenance and authority", "result_binding_unclosed"),
    ("visual_encoding_fitness", "encoding_composition", "library.presentation.visual_encoding_fitness", "SHARED_PRESENTATION_SEMANTICS", ["EncodingCandidate", "EncodingFitness", "TaskProfile", "LossDeclaration"], ["evaluate_fitness", "rank_encodings", "explain_refusal"], "fitness is task and semantic-profile relative, never chart-popularity authority", "no_fit_encoding"),
    ("composition_layout", "encoding_composition", "library.presentation.composition_layout", "SHARED_PRESENTATION_SEMANTICS", ["ViewNode", "CompositionGraph", "ScaleResolution", "LayoutConstraint"], ["compose_views", "resolve_scales", "validate_composition"], "shared and independent scales plus layering/faceting order are explicit", "composition_ambiguous"),
    ("responsive_layout", "encoding_composition", "library.presentation.responsive_layout", "SHARED_PRESENTATION_SEMANTICS", ["ViewportProfile", "ResponsiveRule", "LayoutVariant", "TaskPreservationResult"], ["select_variant", "reflow", "verify_task_preservation"], "responsive transformation cannot remove a required task or conceal a material claim", "responsive_equivalence_unproved"),
    ("interaction_state", "interaction_navigation", "library.presentation.interaction_state", "INTERACTIVE_EXPLORATION", ["InteractionState", "InteractionEvent", "StateReducer", "SessionEpoch"], ["reduce_event", "merge_state", "reset_state"], "state reduction is deterministic per declared ordering and scope", "interaction_order_ambiguous"),
    ("selection_algebra", "interaction_navigation", "library.presentation.selection_algebra", "INTERACTIVE_EXPLORATION", ["Selection", "SelectionPredicate", "SelectionScope", "SelectionProjection"], ["union", "intersect", "subtract", "project_selection"], "selection only affects declared analytical view scope", "selection_projection_invalid"),
    ("drill_navigation", "interaction_navigation", "library.presentation.drill_navigation", "INTERACTIVE_EXPLORATION", ["DrillPath", "HierarchyRef", "DrillStep", "NavigationReceipt"], ["validate_path", "drill_down", "drill_up", "drill_through"], "every step binds an exact semantic hierarchy or relation", "drill_relation_unproved"),
    ("report_definition", "formal_reporting", "library.presentation.report_definition", "FORMAL_REPORTING_PUBLICATION", ["ReportDefinition", "ReportSection", "ParameterDefinition", "RenditionProfile"], ["create_definition", "validate_definition", "revise_definition"], "definition is immutable by edition and contains no run outcome", "report_definition_invalid"),
    ("report_run", "formal_reporting", "library.presentation.report_run", "FORMAL_REPORTING_PUBLICATION", ["ReportRun", "RunAttempt", "ParameterBinding", "RunOutcome"], ["plan_run", "start_attempt", "record_outcome", "cancel_run"], "every attempt binds exact definition, parameters, data cut and runtime offer", "report_run_unclosed"),
    ("pagination_layout", "formal_reporting", "library.presentation.pagination_layout", "FORMAL_REPORTING_PUBLICATION", ["PageBox", "FlowRegion", "BreakRule", "PaginationResult"], ["paginate", "validate_totality", "explain_overflow"], "pagination declares overflow, orphan, widow and repeated-context behavior", "pagination_totality_failed"),
    ("publication_lifecycle", "formal_reporting", "library.presentation.publication_lifecycle", "FORMAL_REPORTING_PUBLICATION", ["Publication", "PublicationEdition", "AudienceGrant", "WithdrawalReceipt"], ["issue", "correct", "supersede", "withdraw", "expire"], "issued editions are never overwritten and issuance is distinct from delivery", "publication_authority_missing"),
    ("notification_port", "boundary_adapters", "library.attention.intent", "SHARED_PUBLISHED_LANGUAGE", ["AttentionIntent", "AudienceIntent", "Urgency", "PurposeRef"], ["construct_intent", "minimize_payload", "validate_handoff"], "port emits intent only; notification workflow and provider effects remain external", "attention_intent_invalid"),
    ("embed_entitlement_projection", "boundary_adapters", "library.presentation.embed_entitlement_projection", "EMBEDDED_ANALYTICS", ["HostPrincipalRef", "GuestGrant", "EntitlementProjection", "ProjectionExpiry"], ["project_entitlements", "validate_projection", "revoke_projection"], "host identity, guest grant, content access and data policy decisions remain distinct", "entitlement_projection_denied"),
    ("accessible_task_equivalent", "accessibility_equivalence", "library.presentation.accessible_task_equivalent", "CONSTITUTIONAL", ["AnalyticalTask", "InteractionPath", "EquivalentRepresentation", "EquivalenceEvidence"], ["derive_task_graph", "compare_task_paths", "verify_equivalence"], "every supported material task has a perceivable and operable equivalent with preserved claims", "accessible_equivalence_unproved"),
    ("uncertainty_encoding", "encoding_composition", "library.presentation.uncertainty_encoding", "SHARED_PRESENTATION_SEMANTICS", ["UncertaintyKind", "IntervalBinding", "DistributionBinding", "EncodingDeclaration"], ["bind_uncertainty", "validate_encoding", "detect_false_precision"], "confidence, credible, prediction and tolerance intervals never collapse", "uncertainty_kind_unsupported"),
    ("missingness_encoding", "encoding_composition", "library.presentation.missingness_encoding", "SHARED_PRESENTATION_SEMANTICS", ["MissingnessKind", "MissingMarker", "SuppressionReason", "MissingnessLegend"], ["bind_missingness", "render_marker", "validate_distinguishability"], "missing, zero, not applicable, suppressed and not observed remain distinct", "missingness_ambiguous"),
    ("provenance_disclosure", "encoding_composition", "library.presentation.provenance_disclosure", "SHARED_PRESENTATION_SEMANTICS", ["ClaimRef", "EvidenceRef", "ProvenanceSummary", "DisclosureProfile"], ["derive_disclosure", "minimize_provenance", "verify_trace"], "disclosure summarizes but never replaces the addressable evidence chain", "provenance_trace_unresolved"),
    ("annotation_collaboration", "content_collaboration", "library.content.annotation_anchor", "SHARED_CONTENT_CONTROL_PLANE", ["Annotation", "TargetSelector", "CommentThread", "ReviewRef"], ["anchor_annotation", "reply", "resolve_thread", "reanchor"], "annotation target edition and selector are explicit; collaboration cannot mutate target truth", "annotation_anchor_invalid"),
    ("bookmark_view_state", "interaction_navigation", "library.presentation.bookmark_view_state", "INTERACTIVE_EXPLORATION", ["Bookmark", "ViewStateSnapshot", "ScopeRef", "Expiry"], ["capture_bookmark", "restore_bookmark", "share_bookmark", "expire_bookmark"], "bookmark captures scoped view state, not source data or a formal report cut", "bookmark_scope_invalid"),
    ("map_portrayal", "specialized_portrayal", "library.presentation.map_portrayal", "GEOSPATIAL_WORKBENCH", ["MapView", "CRSRef", "LayerStack", "PortrayalRule"], ["compose_map", "project_view", "validate_portrayal"], "geometry, CRS, style, scale and topology remain explicit", "crs_or_portrayal_unresolved"),
    ("tile_delivery", "specialized_portrayal", "library.presentation.tile_delivery", "GEOSPATIAL_WORKBENCH", ["TileMatrixSet", "TileCoordinate", "TileContent", "TileCachePolicy"], ["plan_tiles", "request_tile", "validate_tile", "invalidate_tiles"], "tile occurrence is a portrayal/cache artifact, not source feature identity", "tile_matrix_unsupported"),
    ("graph_layout_view", "specialized_portrayal", "library.presentation.graph_layout_view", "GRAPH_ANALYSIS_WORKBENCH", ["GraphView", "NodeMark", "EdgeMark", "LayoutResult"], ["bind_graph", "compute_layout", "filter_scene", "validate_topology_preservation"], "layout position never becomes graph topology or relationship truth", "graph_binding_invalid"),
    ("signal_view", "specialized_portrayal", "library.presentation.signal_view", "SIGNAL_CONDITION_DIAGNOSTICS", ["SignalView", "ChannelBinding", "WindowBinding", "CursorState"], ["bind_channels", "select_window", "overlay_events", "validate_sampling_disclosure"], "display resampling never silently changes signal, event or calibration semantics", "signal_sampling_ambiguous"),
    ("volume_scene_view", "specialized_portrayal", "library.presentation.volume_scene_view", "SCIENTIFIC_OR_IMAGE_PRODUCT_IMPORT", ["Scene", "VolumeBinding", "TransferFunction", "CameraState"], ["bind_volume", "compose_scene", "slice_volume", "validate_scene"], "rendering transfer functions and camera state never mutate scientific values", "volume_representation_unsupported"),
    ("visual_regression_oracle", "assurance_operations", "library.presentation.visual_regression_oracle", "PRESENTATION_ASSURANCE", ["RenderFixture", "ImageDifference", "PerceptualThreshold", "RegressionVerdict"], ["capture_fixture", "compare_render", "classify_difference"], "visual similarity is scoped evidence and never proves semantic equivalence", "visual_baseline_untrusted"),
    ("semantic_equivalence_oracle", "assurance_operations", "library.presentation.semantic_equivalence_oracle", "PRESENTATION_ASSURANCE", ["TaskTrace", "ClaimTrace", "RepresentationPair", "EquivalenceVerdict"], ["compare_claims", "compare_tasks", "compare_interactions", "issue_verdict"], "equivalence is task, audience and claim scoped with explicit residual loss", "semantic_equivalence_unproved"),
    ("presentation_resource_budget", "assurance_operations", "library.presentation.presentation_resource_budget", "PRESENTATION_RUNTIME", ["MarkBudget", "RowBudget", "LatencyBudget", "MemoryBudget", "BandwidthBudget", "CancellationToken"], ["precharge", "consume", "cancel", "record_exhaustion"], "finite resources are declared before effectful work and exhaustion is typed", "presentation_budget_exhausted"),
    ("presentation_usage_evidence", "assurance_operations", "library.presentation.presentation_usage_evidence", "PRESENTATION_OPERATIONS", ["ViewOccurrence", "InteractionOccurrence", "DeliveryOccurrenceRef", "UsageEvidence"], ["record_occurrence", "aggregate_usage", "redact_usage", "expire_usage"], "usage occurrences never infer comprehension, intent, approval or outcome", "usage_evidence_disallowed"),
]


def build_contract_candidates(library_hypotheses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name = {row["name"]: row for row in library_hypotheses}
    rows = []
    for name, family, exact_ref, owner, types, operations, invariant, refusal in CONTRACT_ROWS:
        hypothesis = by_name[name]
        rows.append({
            "contract_id": f"contract-candidate.presentation.{name.replace('_', '-')}.v1",
            "record_kind": "presentation_exact_library_contract_candidate",
            "hypothesis_ref": hypothesis["library_hypothesis_id"],
            "family_constitution_ref": f"constitution.presentation.{family.replace('_', '-')}",
            "exact_library_ref": exact_ref,
            "owner_posture": owner,
            "types": types,
            "operations": operations,
            "invariants": [invariant],
            "refusals": [refusal, "authority_missing", "compatibility_unproved", "resource_budget_missing"],
            "time_model": ["artifact, interaction/run, publication/delivery and recording time remain distinct", "every imported edition and data cut is exact"],
            "compatibility": ["directional semantic compatibility", "provider representation compatibility", "migration residuals explicit"],
            "oracles": ["canonical_round_trip", "negative_twin", "provider_differential", "resource_boundary", "historical_replay"],
            "evidence_refs": hypothesis["evidence_refs"],
            "implementation_evidence_floor": 2,
            "implementation_qualification": "NOT_ATTEMPTED",
            "owner_ratification": "WITHHELD",
            "compiler_binding": "REFUSED_UNTIL_OWNER_RATIFICATION_AND_QUALIFIED_OFFER",
            "completion_claim": False,
        })
    return rows


COMPATIBILITY_PROFILE_METAMODEL = {
    "metamodel_id": "metamodel.presentation.result-artifact-compatibility-profile.v1",
    "record_kind": "presentation_compatibility_profile_metamodel",
    "identity": ["profile_id", "profile_edition", "result_kind_ref", "artifact_kind_ref", "task_profile_ref", "audience_profile_ref"],
    "semantic_preservation_axes": ["identity", "grain", "type", "unit", "time", "uncertainty", "missingness", "order_topology", "provenance", "authority", "claim_scope"],
    "representation_axes": ["encoding", "layout", "interaction", "rendition", "responsive_variant", "specialized_portrayal"],
    "assurance_axes": ["accessibility_task_equivalence", "semantic_equivalence", "visual_regression", "resource_budget", "privacy_disclosure", "vertical_fitness"],
    "dispositions": ["NATIVE", "SUPPORTED_WITH_DECLARED_LOSS", "REQUIRES_TRANSFORMATION", "INAPPLICABLE", "REFUSED_UNPROVED"],
    "required_evidence": ["exact_contract_editions", "oracle_receipts", "provider_qualification", "audience_task_review", "two_unrelated_vertical_acceptances"],
    "compiler_law": "No result-artifact pair lowers to a renderer until every required semantic, representation, assurance and resource coordinate has an explicit disposition and evidence route.",
    "status": "CANDIDATE_UNRATIFIED",
    "completion_claim": False,
}


def build_compatibility_quotients(artifacts: list[dict[str, Any]], results: list[dict[str, Any]], cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    artifact_by_id = {row["artifact_id"]: row for row in artifacts}
    result_by_id = {row["result_kind_id"]: row for row in results}
    groups: dict[tuple[str, tuple[str, ...], str], list[str]] = {}
    for cell in cells:
        artifact = artifact_by_id[cell["artifact_ref"]]
        result = result_by_id[cell["result_kind_ref"]]
        key = (artifact["family"], tuple(result["semantic_tags"]), cell["disposition"])
        groups.setdefault(key, []).append(cell["cell_id"])
    rows = []
    for index, ((artifact_family, tags, disposition), cell_ids) in enumerate(sorted(groups.items()), 1):
        rows.append({
            "quotient_id": f"quotient.presentation.compatibility.{index:03d}",
            "record_kind": "presentation_compatibility_research_quotient",
            "artifact_family": artifact_family,
            "result_semantic_tags": list(tags),
            "current_disposition": disposition,
            "cell_refs": sorted(cell_ids),
            "cell_count": len(cell_ids),
            "required_profile_metamodel_ref": COMPATIBILITY_PROFILE_METAMODEL["metamodel_id"],
            "research_status": "STRUCTURALLY_ROUTED",
            "ratification_status": "OPEN_PER_CELL",
            "completion_claim": False,
        })
    return rows

