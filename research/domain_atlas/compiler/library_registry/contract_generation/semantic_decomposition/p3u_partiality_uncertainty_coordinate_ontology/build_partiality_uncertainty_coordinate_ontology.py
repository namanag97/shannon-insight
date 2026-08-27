#!/usr/bin/env python3
"""Build a bearer-positioned partiality/uncertainty ontology and lossless P3U rebase."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
P3U_DOCKETS = SEM / "p3u_partiality_uncertainty_evidence/family-evidence-dockets.jsonl"
PRECLASSIFICATIONS = SEM / "applicability_matrices/member-preclassifications.jsonl"
sys.path.insert(0, str(SEM))

from member_axis_rebase import build_member_rebase  # noqa: E402


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


PRIMARY_SOURCES = [
    {
        "source_id": "source.uncertainty.substrait-types",
        "title": "Substrait Type System",
        "publisher": "Substrait",
        "url": "https://substrait.io/types/type_system/",
        "bounded_implication": "Nullability is separate from type class, parameters and variation; null is a special value of a nullable type, unbound is a placeholder for partial binding and casts are explicit.",
        "authority_limit": "Substrait does not make nullable, absent, unknown, invalid, unbound, stale and failed one semantic state or define application-domain missingness policy.",
    },
    {
        "source_id": "source.uncertainty.arrow-columnar",
        "title": "Apache Arrow Columnar Format",
        "publisher": "Apache Arrow",
        "url": "https://arrow.apache.org/docs/format/Columnar.html",
        "bounded_implication": "Array validity is carried separately from value buffers; null slots need not contain meaningful values and nested arrays have independently scoped validity.",
        "authority_limit": "A physical validity bitmap does not encode why a value is missing, whether it is unknown or inapplicable, or how it may be imputed, propagated or disclosed.",
    },
    {
        "source_id": "source.uncertainty.json-schema-2020-12",
        "title": "JSON Schema Core and Validation, Draft 2020-12",
        "publisher": "JSON Schema",
        "url": "https://json-schema.org/draft/2020-12/",
        "bounded_implication": "JSON null is an instance value while required governs property presence; type and applicator validation therefore distinguish missing members, present nulls and invalid values.",
        "authority_limit": "JSON Schema validation does not determine domain unknownness, defaulting, repair, observation completeness or statistical uncertainty.",
    },
    {
        "source_id": "source.uncertainty.kubernetes-api-conventions",
        "title": "Kubernetes API Conventions",
        "publisher": "Kubernetes",
        "url": "https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md",
        "bounded_implication": "Conditions use True, False and Unknown, absent known conditions default to Unknown, observedGeneration exposes staleness and polarity is condition-specific.",
        "authority_limit": "Condition aggregation cannot infer universal health, current completion, effect success or retry safety without condition-specific semantics.",
    },
    {
        "source_id": "source.uncertainty.nist-tn1297",
        "title": "NIST Technical Note 1297: Guidelines for Evaluating and Expressing Measurement Uncertainty",
        "publisher": "NIST",
        "url": "https://www.nist.gov/pml/nist-technical-note-1297",
        "bounded_implication": "Measurement results require identified uncertainty components, combined standard uncertainty and, when reported, an expanded uncertainty with coverage factor and assumptions.",
        "authority_limit": "Measurement uncertainty methods do not define forecast intervals, missing-data mechanisms, causal uncertainty, business risk tolerance or universal confidence semantics.",
    },
    {
        "source_id": "source.uncertainty.forecasting-fpp3",
        "title": "Forecasting: Principles and Practice, 3rd edition — Distributional forecasts and prediction intervals",
        "publisher": "OTexts",
        "url": "https://otexts.com/fpp3/distaccuracy.html",
        "bounded_implication": "Forecast uncertainty may be a distribution, quantile, prediction interval or sample path, depends on residual/model assumptions and generally changes with forecast horizon.",
        "authority_limit": "A point estimate plus generic confidence value does not fully characterize forecast uncertainty or make intervals comparable across models, horizons or populations.",
    },
    {
        "source_id": "source.uncertainty.postgresql-create-view",
        "title": "PostgreSQL 18 Documentation: CREATE VIEW",
        "publisher": "PostgreSQL Global Development Group",
        "url": "https://www.postgresql.org/docs/18/sql-createview.html",
        "bounded_implication": "Views are evaluated when referenced; replacement, updateability and local/cascaded checks are partial and operator-specific rather than proof of stored completeness.",
        "authority_limit": "A virtual relation and matching output shape do not establish stored completeness, semantic equivalence, total updateability or visibility.",
    },
    {
        "source_id": "source.uncertainty.ogc-moving-features-json",
        "title": "OGC Moving Features Encoding Extension — JSON 1.0",
        "publisher": "Open Geospatial Consortium",
        "url": "https://docs.ogc.org/is/19-045r3/19-045r3.html",
        "bounded_implication": "Discrete, step and continuous phenomena, temporal domains, lifespans and instant observations have different interpolation and existence semantics.",
        "authority_limit": "A missing position does not prove nonexistence and observed instants do not automatically define a total trajectory.",
    },
]


BEARER_ARCHETYPES = [
    ("nullable_or_optional_value", "One positioned value with explicit presence and validity carrier."),
    ("field_or_property_presence", "Presence, omission, default and explicit-null state of a named property."),
    ("typed_binding_or_placeholder", "Unbound, partially bound or resolved type/symbol position."),
    ("observation_or_measurement", "Observation of a measurand with method, unit, uncertainty and validity."),
    ("fact_assertion_or_claim", "Assertion whose truth, support, confidence, contradiction and disclosure may be partial."),
    ("collection_or_population_coverage", "Completeness of a collection relative to a declared population, cut or sampling frame."),
    ("runtime_condition_or_status", "Multi-valued, generation-scoped condition with polarity, reason and staleness."),
    ("state_or_transition_outcome", "Pending, unknown, failed, partial or completed lifecycle/effect outcome."),
    ("time_series_or_trajectory", "Partial function over time with observation support and interpolation/extrapolation policy."),
    ("point_estimate", "Estimated scalar/vector with estimator, population, sample and uncertainty context."),
    ("interval_or_bound", "Lower/upper or set-valued bound with open/closed endpoints and coverage interpretation."),
    ("probability_distribution", "Distribution over an explicit random variable, population and conditioning context."),
    ("quantile_or_sample_path", "Distributional functional or simulated path with horizon and dependence structure."),
    ("model_score_or_probability", "Score/probability with calibration population, threshold and drift scope."),
    ("optimization_or_solver_result", "Feasible, optimal, infeasible, invalid or unknown result with bounds and certificates."),
    ("quality_measurement_or_assertion", "Measured quality dimension, scope, threshold, evidence and fitness decision."),
    ("evidence_or_appraisal_result", "Evidence support, defeaters and appraisal state distinct from acceptance."),
    ("query_or_virtual_relation", "Potentially partial query result, virtual definition and updateability/completeness contract."),
    ("redacted_withheld_or_censored_value", "Intentionally obscured or observation-limited value with disclosure reason."),
    ("approximate_or_lossy_representation", "Approximation, rounding, compression or projection with error/loss bounds."),
]


def bearer_rows() -> list[dict[str, Any]]:
    return [
        {
            "record_kind": "partiality_uncertainty_bearer_archetype",
            "archetype_id": f"archetype.partiality-uncertainty.{name}.v1",
            "meaning": meaning,
            "required_coordinate_ref": "ontology.semantic-axis.partiality-uncertainty-coordinate.v1#uncertainty_coordinate",
            "applicability": "UNRESOLVED_PER_BEARER_POSITION_AND_USE_SITE",
            "completion_claim": False,
        }
        for name, meaning in BEARER_ARCHETYPES
    ]


ONTOLOGY = {
    "ontology_id": "ontology.semantic-axis.partiality-uncertainty-coordinate.v1",
    "edition": 1,
    "as_of": AS_OF,
    "axis": "partiality_and_uncertainty",
    "domain_question": "At each exact semantic position, what is absent, partial, unknown, invalid, stale, censored, approximate or uncertain; why; over which population/time/evidence scope; how is it represented, propagated, combined, compared and allowed to affect a decision?",
    "coordinate_key": [
        "bounded_context_ref", "bearer_ref", "property_operation_or_claim_ref",
        "semantic_position_ref", "uncertainty_profile_edition_ref", "use_site_ref",
    ],
    "uncertainty_coordinate": {
        "required_fields": [
            "bearer_archetype_ref", "carrier_and_semantic_state_lattice",
            "missingness_partiality_or_uncertainty_kind", "reason_and_mechanism",
            "subject_population_sample_and_completeness_scope", "time_horizon_freshness_and_validity",
            "point_set_interval_distribution_or_sample_path_representation", "unit_scale_and_support",
            "coverage_calibration_and_error_profile", "assumptions_dependence_and_model_edition",
            "propagation_defaulting_and_refusal_policy", "aggregation_composition_and_correlation_policy",
            "comparison_ordering_threshold_and_loss_policy", "imputation_interpolation_and_reconstruction_status",
            "authority_disclosure_and_human_judgment_boundary", "provenance_evidence_and_invalidators",
            "resource_budget_termination_and_approximation", "conformance_oracles_and_negative_twins",
        ],
        "partiality_kinds": [
            "absent_not_provided", "present_null", "not_applicable", "not_observed", "unknown",
            "unbound", "invalid", "failed", "pending", "stale", "incomplete", "out_of_scope",
            "withheld_or_redacted", "censored_or_truncated", "below_detection_limit", "tombstoned",
            "conflicting", "ambiguous", "resource_bounded", "non_convergent",
        ],
        "uncertainty_kinds": [
            "measurement", "sampling", "aleatoric", "epistemic", "model", "parameter",
            "forecast", "causal", "classification", "calibration", "interval_or_set_valued",
            "approximation_or_numerical", "data_quality", "lineage_or_coverage", "human_judgment",
        ],
        "outcomes": [
            "known_valid", "known_invalid", "present_null", "absent", "not_applicable", "unknown",
            "interval_or_set", "distributional", "approximate", "conflicting", "stale", "partial",
            "withheld", "failed", "indeterminate", "refused",
        ],
    },
    "dependency_axis_refs": [
        "semantic_object", "identity_and_equality", "grain_and_cardinality", "state_and_change",
        "time", "order_and_topology", "composition_algebra", "authority_and_trust",
        "effect_boundary", "resources_and_failure", "representation", "evidence_and_conformance",
    ],
    "discovery_projection_compatibility": {
        "existing_facets": ["optional_missing_null", "three_or_multi_valued", "interval_or_bound", "probabilistic", "approximate_or_lossy"],
        "status": "LOSSY_LEXICAL_DISCOVERY_PROJECTION_ONLY",
        "prohibition": "A facet cannot select missingness reason, state lattice, population, time/horizon, uncertainty representation, calibration, propagation, imputation, authority, decision threshold, applicability or exact contract.",
    },
    "non_collapse_laws": [
        "absent is not present-null unknown invalid failed withheld or not-applicable",
        "unknown is not false zero empty or retryable",
        "stale observation is not a current false condition",
        "unbound type or symbol is not a nullable runtime value",
        "invalid carrier is not a valid value with uncertainty",
        "point estimate is not a distribution quantile interval or sample path",
        "confidence interval prediction interval credible interval and tolerance interval are not interchangeable",
        "probability is meaningless without event population conditioning and calibration scope",
        "interval width is not comparable without units coverage method horizon and assumptions",
        "measurement uncertainty is not data quality model risk or business tolerance",
        "sampling uncertainty is not population incompleteness or selection bias",
        "aleatoric uncertainty is not epistemic uncertainty and neither is ordinary missingness",
        "imputation is a derived value with provenance not recovery of the unobserved truth",
        "interpolation is not observation and extrapolation is not interpolation",
        "censoring truncation redaction and absence have different mechanisms",
        "approximation error and probabilistic uncertainty require different composition laws",
        "partial effect is not failure before effect or successful completion",
        "solver unknown is not infeasible and feasible is not optimal",
        "quality score is not fitness acceptance or authorization",
        "more evidence need not monotonically reduce uncertainty when evidence conflicts",
        "defaulting or coalescing destroys missingness information unless residual provenance is retained",
    ],
    "primary_source_refs": [row["source_id"] for row in PRIMARY_SOURCES],
    "owner_decision": "UNRESOLVED",
    "member_applicability_decisions": 0,
    "canonical_gaps_closed": 0,
    "completion_claim": False,
}


KERNEL_DEFINITIONS = [
    ("lift_total_to_optional", "nullable_or_optional_value", "known value", "present optional value", "Lifting does not define why absence may later occur."),
    ("coalesce_or_default", "nullable_or_optional_value", "partial value and fallback policy", "chosen value plus residual provenance", "Defaulting without a residual erases absence and can create false certainty."),
    ("propagate_missing", "nullable_or_optional_value", "partial operands", "partial result", "Propagation depends on operator and missingness kind and is not universally strict."),
    ("mark_not_applicable", "field_or_property_presence", "subject and applicability rule", "explicit N/A state", "Not applicable is not unknown, absent or zero."),
    ("validate_present_value", "field_or_property_presence", "present carrier and schema/rule", "valid or invalid", "Invalid is not missing and should retain the offending carrier/evidence when safe."),
    ("bind_unbound_placeholder", "typed_binding_or_placeholder", "unbound position and binding environment", "bound type/symbol or refusal", "Unbound is a design-time partiality state, not runtime null."),
    ("kleene_three_valued_and", "runtime_condition_or_status", "True/False/Unknown conditions", "three-valued result", "Unknown cannot be collapsed to False and polarity/preconditions remain explicit."),
    ("kleene_three_valued_or", "runtime_condition_or_status", "True/False/Unknown conditions", "three-valued result", "Unknown cannot be collapsed to True or ordinary absence."),
    ("detect_stale_observation", "runtime_condition_or_status", "observation generation/time and desired generation", "current or stale", "Stale status cannot prove current health or failure."),
    ("aggregate_condition", "runtime_condition_or_status", "typed conditions and policy", "aggregate status", "Condition-specific polarity, severity and authority prevent generic Boolean folding."),
    ("record_pending_or_partial_effect", "state_or_transition_outcome", "execution observations and receipts", "pending/partial/completed outcome", "Partial effect is not atomic failure and requires recovery/compensation evidence."),
    ("classify_missingness_mechanism", "observation_or_measurement", "observation context and absence evidence", "mechanism hypothesis", "Missingness mechanism is an evidence-backed hypothesis, not readable from null alone."),
    ("impute_value", "observation_or_measurement", "partial observations and imputation model", "derived value plus uncertainty/provenance", "Imputed values are not observations and must not erase model assumptions."),
    ("interpolate_trajectory", "time_series_or_trajectory", "support points and interpolation model", "derived values inside support", "Interpolation depends on phenomenon semantics and is not observation."),
    ("extrapolate_trajectory", "time_series_or_trajectory", "support and extrapolation model", "derived values outside support", "Extrapolation carries stronger assumptions and distinct uncertainty from interpolation."),
    ("apply_censoring_or_truncation", "redacted_withheld_or_censored_value", "latent/observed process and limits", "censored/truncated observation", "Censoring and truncation change likelihood and population semantics differently."),
    ("redact_or_withhold", "redacted_withheld_or_censored_value", "value and disclosure authority", "withheld carrier plus reason", "Withheld is not unknown to the source and must preserve authority and disclosure status."),
    ("estimate_point", "point_estimate", "sample, estimator and population", "point estimate plus provenance", "A point estimate without uncertainty and estimand is not a complete analytical result."),
    ("construct_confidence_interval", "interval_or_bound", "sample estimator and confidence procedure", "frequentist interval", "Confidence is a procedure coverage property, not posterior probability of this fixed parameter."),
    ("construct_prediction_interval", "interval_or_bound", "forecast distribution and horizon", "future-observation interval", "Prediction intervals include future variability and are not parameter confidence intervals."),
    ("construct_credible_interval", "interval_or_bound", "posterior distribution and prior/model", "posterior probability interval", "Credible interval meaning depends on model/prior and is not frequentist coverage."),
    ("compute_lower_upper_bound", "interval_or_bound", "bounded computation or optimization state", "bound with proof/status", "A bound is not an estimate and open/closed, valid/heuristic status matters."),
    ("derive_quantile", "quantile_or_sample_path", "distribution and probability level", "quantile", "A quantile requires distribution, conditioning and level and is not a generic confidence score."),
    ("simulate_sample_paths", "quantile_or_sample_path", "stochastic model, horizon and random stream", "sample paths", "Sample paths are simulated realizations, not observed future trajectories."),
    ("combine_standard_uncertainty", "observation_or_measurement", "uncertainty components and dependence", "combined standard uncertainty", "Root-sum-of-squares is conditional on the measurement model and covariance assumptions."),
    ("propagate_distribution", "probability_distribution", "input distributions and transform", "output distribution/approximation", "Marginals alone are insufficient when inputs are dependent."),
    ("monte_carlo_propagate", "probability_distribution", "model, input distributions and random stream", "empirical output distribution", "Simulation error, model error and input uncertainty remain separate."),
    ("combine_probabilistic_evidence", "evidence_or_appraisal_result", "probabilistic evidence and dependence model", "updated support distribution", "Evidence combination is dependence/model sensitive and does not itself authorize acceptance."),
    ("calibrate_score", "model_score_or_probability", "scores, outcomes and calibration population", "calibrated mapping plus diagnostics", "Calibration is population/time scoped and can drift."),
    ("threshold_score", "model_score_or_probability", "score and decision/loss policy", "decision proposal", "Thresholding is a policy decision, not model truth or execution authority."),
    ("interval_arithmetic", "interval_or_bound", "interval operands and operator", "enclosure", "Dependency and wrapping can widen bounds; interval arithmetic is not a probability model."),
    ("combine_set_valued_results", "interval_or_bound", "sets and operator", "result set", "Set-valued possibility does not assign probabilities or preferences."),
    ("reconcile_conflicting_values", "fact_assertion_or_claim", "conflicting assertions and authority/evidence", "adjudicated or unresolved result", "Conflict cannot be erased by coalesce, timestamp or majority without policy and residuals."),
    ("measure_collection_completeness", "collection_or_population_coverage", "observed collection and declared population/cut", "coverage assertion", "Row count or end-of-stream alone does not prove population completeness."),
    ("aggregate_partial_collection", "collection_or_population_coverage", "partial collection and aggregate", "partial/bounded estimate", "Aggregates over incomplete data need explicit bias/bounds, not ordinary finality."),
    ("compute_quality_measure", "quality_measurement_or_assertion", "data, dimension, scope and method", "quality measurement", "Quality measurement is not fitness judgment, repair authority or acceptance."),
    ("appraise_evidence", "evidence_or_appraisal_result", "claims, evidence, defeaters and policy", "appraisal state", "Appraisal is not truth, relying-party acceptance or execution authority."),
    ("evaluate_virtual_relation", "query_or_virtual_relation", "definition, snapshot/context and parameters", "evaluation result", "A view is not stored complete data and same shape does not preserve meaning."),
    ("attempt_partial_update", "query_or_virtual_relation", "view mutation and updateability/check policy", "effect or refusal", "Readable rows do not imply total updateability or safe mutation."),
    ("quantize_or_round", "approximate_or_lossy_representation", "value and rounding/quantization profile", "approximation plus error bound", "Rounded equality is not value identity and may be non-invertible."),
    ("lossy_compress_or_project", "approximate_or_lossy_representation", "artifact and loss profile", "approximation plus residual metadata", "Decodability does not imply losslessness or preservation of analytical fitness."),
    ("interpret_solver_status", "optimization_or_solver_result", "solver outcome, bounds and certificates", "typed solve result", "Unknown is not infeasible; feasible is not optimal; equal objectives do not identify solutions."),
]


def kernel_rows() -> list[dict[str, Any]]:
    source_refs = [row["source_id"] for row in PRIMARY_SOURCES]
    return [
        {
            "record_kind": "partiality_uncertainty_kernel",
            "kernel_id": f"kernel.partiality-uncertainty.{name}.v1",
            "bearer_archetype_ref": f"archetype.partiality-uncertainty.{archetype}.v1",
            "input_contract": input_contract,
            "output_contract": output_contract,
            "required_coordinate_fields": ONTOLOGY["uncertainty_coordinate"]["required_fields"],
            "negative_twin": negative_twin,
            "bounded_primary_source_refs": source_refs,
            "applicability": "UNRESOLVED_PER_BEARER_POSITION_AND_USE_SITE",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for name, archetype, input_contract, output_contract, negative_twin in KERNEL_DEFINITIONS
    ]


def route_for_facets(facets: tuple[str, ...]) -> str:
    return (
        "LEXICAL_DISCOVERY_PROJECTION_ONLY_PARTIALITY_UNCERTAINTY_RESEARCH_REQUIRED"
        if facets
        else "NO_MEMBER_PARTIALITY_UNCERTAINTY_EVIDENCE_VACANCY"
    )


def build() -> dict[str, Any]:
    rebase = build_member_rebase(
        axis="partiality_and_uncertainty",
        dockets_path=P3U_DOCKETS,
        preclassifications_path=PRECLASSIFICATIONS,
        cluster_prefix="cluster.p3u.partiality-uncertainty-rebase",
        cluster_route=route_for_facets,
    )
    clusters = [
        {
            "record_kind": "partiality_uncertainty_member_research_cluster",
            **row,
            "required_next_evidence": [
                "authoritative bearer-position and state-lattice inventory",
                "missingness reason population completeness time and horizon contracts",
                "uncertainty representation calibration assumptions and dependence",
                "propagation aggregation imputation threshold and refusal policies",
                "authority disclosure resource evidence and conformance obligations",
            ],
            "member_applicability": "UNRESOLVED",
            "owner_decision": "UNRESOLVED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for row in rebase["clusters"]
    ]
    members = [
        {
            "record_kind": "partiality_uncertainty_member_research_route",
            "route_id": f"route.p3u.partiality-uncertainty.{row['library_ref'].removeprefix('library.').replace('.', '-').replace('_', '-')}",
            **row,
            "flat_projection_effect": "DISCOVERY_ROUTING_ONLY_NOT_APPLICABILITY",
            "required_bearer_and_state_lattice_inventory": "NOT_YET_SUPPLIED",
            "required_partiality_and_uncertainty_profiles": "NOT_YET_SUPPLIED",
            "required_propagation_imputation_and_decision_contracts": "NOT_YET_SUPPLIED",
            "required_authority_evidence_and_conformance_contracts": "NOT_YET_SUPPLIED",
            "member_applicability": "UNRESOLVED",
            "owner_decision": "UNRESOLVED",
            "canonical_gaps_closed": 0,
            "status": "LOSSLESSLY_ROUTED_RESEARCH_OPEN",
            "completion_claim": False,
        }
        for row in rebase["members"]
    ]
    extensions = []
    for family_ref, docket in sorted(rebase["docket_by_family"].items()):
        short = family_ref.removeprefix("constitution.family.")
        extensions.append(
            {
                "record_kind": "partiality_uncertainty_exact_contract_extension_candidate",
                "extension_id": f"extension.p3u.partiality-uncertainty-coordinate.{short}.v1",
                "family_ref": family_ref,
                "family_evidence_docket_ref": docket["docket_id"],
                "represented_library_refs": docket["library_refs"],
                "represented_library_count": docket["library_count"],
                "required_record_kinds": [
                    "partiality_bearer_inventory", "semantic_state_lattice",
                    "uncertainty_profile", "propagation_imputation_decision_contract",
                    "disclosure_authority_contract", "uncertainty_conformance_oracle",
                ],
                "owner_decision": "UNRESOLVED",
                "member_applicability_decisions": 0,
                "canonical_gaps_closed": 0,
                "status": "CANDIDATE_UNRATIFIED",
                "completion_claim": False,
            }
        )
    kernels = kernel_rows()
    summary = {
        "program_id": "program.p3u.partiality-uncertainty-coordinate-ontology-and-rebase.v1",
        "as_of": AS_OF,
        "axis": "partiality_and_uncertainty",
        "primary_sources": len(PRIMARY_SOURCES),
        "bearer_archetypes": len(BEARER_ARCHETYPES),
        "partiality_uncertainty_kernels": len(kernels),
        "family_extension_candidates": len(extensions),
        "research_clusters": len(clusters),
        "target_member_routes": len(members),
        "routes_with_lexical_discovery_projection": rebase["lexical_member_count"],
        "routes_with_no_member_partiality_uncertainty_evidence": rebase["vacancy_member_count"],
        "bearer_state_lattice_inventories_supplied": 0,
        "partiality_uncertainty_profiles_supplied": 0,
        "member_applicability_decisions": 0,
        "owner_decisions": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {
        "ontology": ONTOLOGY,
        "sources": PRIMARY_SOURCES,
        "archetypes": bearer_rows(),
        "kernels": kernels,
        "clusters": clusters,
        "members": members,
        "extensions": extensions,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "partiality-uncertainty-coordinate-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "bearer-archetypes.jsonl": "".join(canonical(row) + "\n" for row in built["archetypes"]),
        "partiality-uncertainty-kernels.jsonl": "".join(canonical(row) + "\n" for row in built["kernels"]),
        "member-research-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "member-partiality-uncertainty-routes.jsonl": "".join(canonical(row) + "\n" for row in built["members"]),
        "extension-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["extensions"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.p3u.partiality-uncertainty-coordinate-ontology-and-rebase.v1",
            "as_of": AS_OF,
            "files": claims,
            "completion_claim": False,
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(
        "BUILD PASS P3U partiality/uncertainty coordinate ontology: "
        f"{summary['bearer_archetypes']} bearer archetypes, {summary['partiality_uncertainty_kernels']} kernels, "
        f"{summary['research_clusters']} clusters and {summary['target_member_routes']} exact routes; "
        "decisions and gap closure remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
