#!/usr/bin/env python3
"""Build the evidence-backed forecasting and integrated-planning semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
AS_OF = "2026-08-27"
PRODUCTS = {"product.forecasting_workbench", "product.integrated_planning_workbench"}
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

NEIGHBORS = {
    "library.csp.intent.constraint-algebra",
    "library.csp.quantity.probability-core",
    "library.csp.time.business-calendar",
    "library.csp.time.calendar-period",
    "library.method_kernels.forecasting_methods",
    "library.method_kernels.probabilistic_inference",
    "library.method_kernels.probability_distribution_algebra",
    "library.method_kernels.semantic_metrics",
    "library.operations_research.constraint_policy_algebra",
    "library.operations_research.objective_preference_algebra",
    "library.operations_research.optimization_model_ir",
    "library.operations_research.optimization_result_algebra",
    "library.operations_research.optimization_solution_validation",
    "library.operations_research.optimization_solve_execution",
    "library.operations_research.simulation_execution",
    "library.operations_research.simulation_experiment_design",
    "library.operations_research.simulation_model_semantics",
    "library.operations_research.simulation_output_analysis",
    "library.operations_research.simulation_random_stream_control",
    "library.operations_research.simulation_verification_validation",
    "library.predictive.conformal_prediction",
    "library.predictive.forecast_models",
    "library.predictive.metrics",
    "library.predictive.objective_functions",
    "library.predictive.probabilistic_models",
    "library.qor.quality_dimension_metric_kernel",
    "library.runtime-resource.budget-precharge",
    "library.smf.calendar_algebra",
}

VACANCIES = [
    ("library.forecast.target-observation-contract", "Target meaning, unit/population/grain, observation occurrence, revision, vintage, availability and finality need one exact contract."),
    ("library.forecast.origin-horizon-information-cut", "Origin, horizon, issue time, information cut and covariate-availability cut require distinct typed identities."),
    ("library.forecast.artifact-distribution-algebra", "Point, mean, median, quantile set, interval, sample paths and joint distribution require non-interchangeable result forms."),
    ("library.forecast.temporal-evaluation-design", "Rolling origins, gaps, horizons, outcome vintages, leakage rules and aggregation need a reusable evaluation design."),
    ("library.forecast.proper-score-calibration", "Score orientation, propriety, calibration, sharpness, weighting and uncertainty of comparison require an explicit evaluation algebra."),
    ("library.forecast.baseline-skill-comparison", "Naive/seasonal/business baselines, skill scores, tests, slices and abstention need a governed comparison contract."),
    ("library.forecast.combination-ensemble", "Candidate identity, weights, information set, dependence, update and fallback semantics need a provider-neutral combination library."),
    ("library.forecast.intermittent-demand-profile", "Occurrence/size decomposition, zero semantics, obsolescence and inventory-loss orientation require a separate profile."),
    ("library.forecast.probabilistic-reconciliation", "Joint distribution, constraints, dependence preservation, sampling and probabilistic coherence are not covered by point reconciliation alone."),
    ("library.forecast.cross-temporal-reconciliation", "Cross-sectional, grouped, temporal and cross-temporal constraints require explicit summing structures and validity scopes."),
    ("library.forecast.realization-vintage-join", "A forecast can only be evaluated against an exact origin/horizon-compatible realized-outcome vintage with finality semantics."),
    ("library.forecast.judgment-evidence-protocol", "Structured judgment, private information, rationale, authority, conflict, expiry and evaluation need a protocol independent of raw replacement."),
    ("library.forecast.value-added-analysis", "Process-step and human-adjustment value requires base/applied/outcome identity, slice support, uncertainty and non-causal interpretation."),
    ("library.analytics_planning.plan_definition_edition", "Plan identity, edition, purpose, scope, horizon, grain and cadence require one portable lifecycle contract."),
    ("library.analytics_planning.scenario_assumption_contract", "A planning scenario needs editioned exogenous assumptions, controllable choices, inherited forecasts and incompatibility rules."),
    ("library.analytics_planning.plan_alternative_algebra", "Alternative identity, scope, horizon, decisions, resource assignments, outputs and residual infeasibility require a total algebra."),
    ("library.analytics_planning.objective_constraint_resource_binding", "Goals, preferences, hard/soft constraints, resources, policies and authority must remain distinct and be bound explicitly."),
    ("library.analytics_planning.hierarchy_allocation_disaggregation", "Aggregation, allocation, disaggregation, rounding, hierarchy reconciliation and residuals require explicit non-interchangeable semantics."),
    ("library.analytics_planning.feasibility_assessment", "Imported solver and simulation results require a plan-scoped assessment that preserves unknown, infeasible, risky and qualified states."),
    ("library.analytics_planning.cross_functional_reconciliation", "Demand, supply, capacity, inventory, workforce and financial plans require typed conflicts and accountable resolution, not numeric averaging."),
    ("library.analytics_planning.alternative_comparison_selection", "Alternative criteria, tradeoffs, dominance, robustness, selection proposals and evidence require a contract separate from approval."),
    ("library.analytics_planning.review_consensus_approval_commitment", "Proposal, review, consensus, approval, commitment, release and execution are separate authority states."),
    ("library.analytics_planning.plan_publication_release", "Publication, release intent, delivery, execution, recall and supersession require distinct receipt-bearing states."),
    ("library.analytics_planning.plan_variance_replan", "Plan-versus-actual variance, assumption invalidation, trigger, reforecast, replan, supersession and in-flight disposition need one lifecycle."),
    ("library.analytics_planning.planning_cycle_calendar", "Planning-cycle stages, business calendars, gates, deadlines, late-input policy and escalation need planning-specific semantics over generic workflow."),
    ("library.analytics_planning.vertical_vocabulary_acl", "Finance, demand, supply, capacity, inventory, workforce and project semantics must be imported as vertical profiles rather than owned by a generic planner."),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def declared_product_libraries() -> set[str]:
    rows = load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")
    return {edge["concrete_library_ref"] for row in rows if row["product_ref"] in PRODUCTS for edge in row["concrete_bindings"]}


LIBRARIES = sorted(declared_product_libraries() | NEIGHBORS)


SOURCE_ROWS = [
    ("fpp3", "Forecasting: Principles and Practice, third edition", "Hyndman and Athanasopoulos", 2021, "research_text", "https://otexts.com/fpp3/", "Defines forecast task, methods, distributions, temporal evaluation and hierarchical coherence.", "Regularly indexed time-series emphasis is not the whole forecasting universe."),
    ("gneiting-raftery", "Strictly Proper Scoring Rules, Prediction, and Estimation", "Gneiting and Raftery", 2007, "primary_paper", "https://doi.org/10.1198/016214506000001437", "Establishes proper scoring rules for probabilistic forecasts.", "A proper score does not choose business utility, acceptance or action."),
    ("hyndman-koehler", "Another Look at Measures of Forecast Accuracy", "Hyndman and Koehler", 2006, "primary_paper", "https://doi.org/10.1016/j.ijforecast.2006.03.001", "Analyzes accuracy measures and proposes scaled errors.", "No accuracy metric is universally appropriate across grains, losses and zero regimes."),
    ("tashman", "Out-of-sample Tests of Forecasting Accuracy", "Len Tashman", 2000, "primary_paper", "https://doi.org/10.1016/S0169-2070(00)00065-0", "Defines rolling-origin evaluation considerations.", "Backtest evidence is design-, horizon-, vintage- and regime-scoped."),
    ("diebold-mariano", "Comparing Predictive Accuracy", "Diebold and Mariano", 1995, "primary_paper", "https://doi.org/10.1080/07350015.1995.10524599", "Defines tests of equal predictive accuracy under loss differentials.", "A statistical comparison does not grant selection or deployment authority."),
    ("bates-granger", "The Combination of Forecasts", "Bates and Granger", 1969, "primary_paper", "https://doi.org/10.1057/jors.1969.103", "Shows forecast combinations can exploit differential error information.", "Combination value depends on information, covariance, estimation and evaluation scope."),
    ("clemen", "Combining Forecasts: A Review and Annotated Bibliography", "Robert Clemen", 1989, "primary_review", "https://doi.org/10.1016/0169-2070(89)90012-5", "Synthesizes forecast-combination evidence and methods.", "A review establishes a method family, not a universally winning rule."),
    ("hyndman-hierarchical", "Optimal Combination Forecasts for Hierarchical Time Series", "Hyndman et al.", 2011, "primary_paper", "https://doi.org/10.1016/j.csda.2011.03.006", "Frames coherent hierarchical forecasts through linear combination.", "Coherence is not accuracy, feasibility or organizational consensus."),
    ("mint", "Optimal Forecast Reconciliation for Hierarchical and Grouped Time Series", "Wickramasuriya, Athanasopoulos and Hyndman", 2019, "primary_paper", "https://doi.org/10.1080/01621459.2018.1448825", "Defines minimum-trace point forecast reconciliation.", "MinT assumptions and covariance estimation do not cover every constraint or distribution."),
    ("temporal-hierarchies", "Forecasting with Temporal Hierarchies", "Athanasopoulos et al.", 2017, "primary_paper", "https://doi.org/10.1016/j.ejor.2017.02.046", "Defines reconciliation across temporal aggregation levels.", "Temporal aggregation coherence is distinct from cross-functional plan agreement."),
    ("reconciliation-review", "Forecast Reconciliation: A Review", "Panagiotelis et al.", 2024, "primary_review", "https://doi.org/10.1016/j.ijforecast.2023.10.010", "Reviews point, probabilistic, Bayesian and ML reconciliation.", "The reviewed families retain different assumptions and conformance oracles."),
    ("prob-reconciliation", "Probabilistic Forecast Reconciliation under the Gaussian Framework", "Shanika Wickramasuriya", 2021, "primary_paper", "https://arxiv.org/abs/2103.11128", "Relates Gaussian probabilistic reconciliation and proper scores.", "Gaussian results do not establish general distributional equivalence."),
    ("cross-temporal-prob", "Cross-temporal Probabilistic Forecast Reconciliation", "Girolimetto et al.", 2023, "primary_paper", "https://arxiv.org/abs/2303.17277", "Extends probabilistic reconciliation across cross-sectional and temporal constraints.", "Method evidence remains dataset, estimator and constraint scoped."),
    ("croston", "Forecasting and Stock Control for Intermittent Demands", "J. D. Croston", 1972, "primary_paper", "https://doi.org/10.1057/jors.1972.50", "Separates nonzero demand size and occurrence interval for intermittent demand.", "The original estimator is biased and does not define inventory policy."),
    ("syntetos-boylan", "The Accuracy of Intermittent Demand Estimates", "Syntetos and Boylan", 2005, "primary_paper", "https://doi.org/10.1016/j.ijforecast.2004.10.001", "Analyzes bias and correction for intermittent-demand estimates.", "Accuracy results do not collapse occurrence, size, obsolescence and stocking loss."),
    ("tsb", "Forecasting Intermittent Demand: A Comparative Study", "Teunter, Syntetos and Babai", 2011, "primary_paper", "https://doi.org/10.1057/jors.2010.32", "Introduces an obsolescence-aware probability update for intermittent demand.", "A demand forecast remains distinct from an inventory order policy."),
    ("m4", "The M4 Competition", "Makridakis, Spiliotis and Assimakopoulos", 2018, "competition_paper", "https://doi.org/10.1016/j.ijforecast.2018.06.001", "Provides large-scale comparative evidence across forecasting methods.", "Competition rankings are dataset, metric, horizon and submission scoped."),
    ("m5-accuracy", "The M5 Accuracy Competition", "Makridakis et al.", 2022, "competition_paper", "https://doi.org/10.1016/j.ijforecast.2021.11.013", "Evaluates hierarchical retail point forecasts with weighted scaled error.", "Retail competition performance is not universal deployment fitness."),
    ("m5-uncertainty", "The M5 Uncertainty Competition", "Makridakis et al.", 2022, "competition_paper", "https://doi.org/10.1016/j.ijforecast.2021.10.005", "Evaluates multiple forecast quantiles across retail hierarchies.", "A quantile leaderboard does not prove calibrated joint distributions."),
    ("m6", "The M6 Financial Forecasting Competition", "Makridakis et al.", 2023, "competition_paper", "https://doi.org/10.1016/j.ijforecast.2023.04.014", "Separates forecast ranking performance from investment decision performance.", "Financial competition results are not general forecasting or portfolio authority."),
    ("aci", "Adaptive Conformal Predictions for Time Series", "Zaffran et al.", 2022, "primary_paper", "https://proceedings.mlr.press/v162/zaffran22a.html", "Studies adaptive prediction intervals under time dependence and shift.", "Coverage is procedure-, horizon-, dependence- and adaptation-regime scoped."),
    ("fva", "Forecast Value Added in Demand Planning", "Fildes, Goodwin and De Baets", 2025, "primary_paper", "https://doi.org/10.1016/j.ijforecast.2024.07.006", "Evaluates judgmental adjustments across about 147,000 forecasts in six studies.", "Observed FVA is associative evaluation, not causal proof of a person or process."),
    ("business-methods", "Business Forecasting Methods: Impressive Advances, Lagging Implementation", "Goodwin et al.", 2023, "primary_open_paper", "https://doi.org/10.1371/journal.pone.0295693", "Connects systematic forecasting, organizational practice, uncertainty and judgment.", "Survey and interview evidence does not define a universal workflow."),
    ("principles", "Principles of Forecasting", "International Institute of Forecasters", 2026, "professional_knowledge_base", "https://forecastingprinciples.com/", "Collects evidence-oriented forecasting principles and methods.", "Principles remain conditional on task, data, purpose and evidence."),
    ("alfred", "ALFRED: Archival Federal Reserve Economic Data", "Federal Reserve Bank of St. Louis", 2026, "official_data_documentation", "https://alfred.stlouisfed.org/", "Provides vintages of economic data available at historical dates.", "One archive demonstrates vintage semantics but does not own all outcome finality."),
    ("sdmx", "SDMX 3.0 Information Model", "SDMX Technical Working Group", 2021, "official_standard", "https://docs.sdmx.org/en/latest/2_0/information-model.html", "Defines structured statistical data, dimensions, attributes and time-series observations.", "SDMX representation does not define forecast truth, model or planning authority."),
    ("iso8601", "ISO 8601-1:2019 Date and Time", "ISO", 2019, "international_standard", "https://www.iso.org/standard/70907.html", "Defines date/time representations used by temporal contracts.", "Representation alone does not define event, availability, origin or horizon semantics."),
    ("rfc3339", "Date and Time on the Internet", "IETF", 2002, "internet_standard", "https://www.rfc-editor.org/rfc/rfc3339", "Defines an interoperable timestamp profile.", "Timestamp syntax does not establish clock, cut, period or business-calendar meaning."),
    ("ascm-sop", "Sales and Operations Planning", "ASCM", 2026, "professional_body_guidance", "https://www.ascm.org/topics/sales-and-operations-planning/", "Separates forecasting, demand planning, supply planning, executive approval and implementation.", "Guidance is supply-chain scoped and does not define a universal horizontal implementation."),
    ("ascm-dictionary", "ASCM Supply Chain Dictionary", "ASCM", 2024, "professional_dictionary", "https://learn.ascm.org/sfc/servlet.shepherd/document/download/069R3000006PlDHIA0?operationContext=S1", "Defines IBP as integration of strategic, operational and financial planning that balances demand, supply and resources.", "A professional definition does not settle software bounded contexts or authority."),
    ("scor", "SCOR Digital Standard", "ASCM", 2026, "professional_standard", "https://scor.ascm.org/processes/source", "Distinguishes planning practices including S&OP, network planning, scenario planning and IBP.", "SCOR process taxonomy is not a compiler contract."),
    ("afp-pbf", "Planning, Budgeting and Forecasting", "Association for Financial Professionals", 2026, "professional_body_guidance", "https://www.afponline.org/topics/fp-a-topics/planning-budgeting-and-forecasting", "Distinguishes budgeting, planning, resource allocation and forecasting in FP&A.", "Financial guidance does not own supply, workforce or operational planning semantics."),
    ("afp-fpa", "What is FP&A", "Association for Financial Professionals", 2026, "professional_body_definition", "https://fpacert.afponline.org/certification/what-is-fp-a", "Frames integrated planning, forecasting, performance management and analysis as decision support.", "Decision support is not decision authorization or execution."),
    ("dmn", "Decision Model and Notation 1.5", "Object Management Group", 2024, "official_specification", "https://www.omg.org/spec/DMN/1.5/About-DMN", "Defines decision requirements, expressions and services useful at planning-policy borders.", "A decision model does not supply forecasts, objectives, authority or effects."),
    ("prov", "PROV-O", "W3C", 2013, "web_standard", "https://www.w3.org/TR/prov-o/", "Defines provenance entities, activities and agents for editions and derivations.", "Provenance assertions require evidence and do not establish correctness."),
    ("cloudevents", "CloudEvents 1.0.2", "CNCF", 2022, "official_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", "Defines interoperable event-envelope metadata for lifecycle integration.", "Envelope conformance does not define domain-event meaning or delivery truth."),
    ("sktime", "sktime Forecasting API", "sktime project", 2026, "official_implementation_documentation", "https://www.sktime.net/en/stable/api_reference/forecasting.html", "Documents independent forecasting estimators, horizons, reduction and evaluation interfaces.", "API availability does not establish portable semantics or qualification."),
    ("statsforecast", "StatsForecast Models", "Nixtla", 2026, "official_implementation_documentation", "https://nixtlaverse.nixtla.io/statsforecast/src/core/models.html", "Documents scalable statistical forecast model implementations.", "Provider output is not a governed forecast edition or evidence of universal superiority."),
    ("statsmodels", "statsmodels Time Series Analysis", "statsmodels project", 2026, "official_implementation_documentation", "https://www.statsmodels.org/stable/tsa.html", "Documents independent ARIMA, state-space, VAR and related implementations.", "Implementation documentation is not provider-neutral model semantics."),
    ("gluonts", "GluonTS Probabilistic Time Series Modeling", "AWS Labs", 2026, "official_implementation_documentation", "https://ts.gluon.ai/", "Documents distribution and sample-path oriented forecast objects and evaluation.", "Framework abstractions do not establish business forecast governance."),
]


def sources() -> list[dict[str, Any]]:
    return sorted(({
        "source_id": f"source.foreplan.{key}", "title": title, "publisher": publisher,
        "year": year, "source_kind": kind, "url": url, "supported_claim": claim,
        "authority_limit": limit, "primary_or_official": True,
        "status": "INDEPENDENTLY_RESEARCHED_PRIMARY_OR_OFFICIAL",
    } for key, title, publisher, year, kind, url, claim, limit in SOURCE_ROWS), key=lambda row: row["source_id"])


MODULE_ROWS = [
    ("forecast-purpose", "Which future unknown is estimated, for whom, for what use and with which prohibited interpretations?", "purpose contract", ["fpp3", "business-methods"], []),
    ("target-semantics", "Which variable/event, unit, population, grain and transformation define the forecast target?", "target contract", ["fpp3", "sdmx"], ["forecast-purpose"]),
    ("observation-occurrence", "Which observed occurrence, source, event time and value support the series?", "observation algebra", ["sdmx", "prov"], ["target-semantics"]),
    ("revision-vintage-finality", "Which observation edition was available when, and may it still be revised?", "bitemporal vintage algebra", ["alfred", "prov"], ["observation-occurrence"]),
    ("calendar-frequency", "Which calendar, period, frequency, timezone, aggregation and irregularity semantics apply?", "temporal index algebra", ["iso8601", "rfc3339", "sdmx"], ["target-semantics"]),
    ("origin-horizon", "Which origin and target time/period define each horizon?", "forecast index algebra", ["fpp3", "sktime"], ["calendar-frequency"]),
    ("information-cut", "Which observations, covariates, revisions and external assumptions were knowable at issue time?", "information filtration", ["tashman", "alfred"], ["revision-vintage-finality", "origin-horizon"]),
    ("missing-censor-zero", "Which absent, censored, structural-zero, outlier and not-yet-available states exist?", "partial observation algebra", ["fpp3", "croston"], ["observation-occurrence"]),
    ("series-features-regime", "Which trend, seasonality, dependence, intermittency, breaks and forecastability evidence characterize the history?", "time-series diagnostics", ["fpp3", "syntetos-boylan"], ["information-cut"]),
    ("benchmark-baseline", "Which naive, seasonal, drift or business baseline establishes minimum skill?", "baseline contract", ["fpp3", "m4"], ["origin-horizon"]),
    ("estimator-family", "Which assumptions, state, covariates, fit/update procedure and output forms define an estimator?", "estimator contract", ["fpp3", "statsmodels", "statsforecast"], ["series-features-regime"]),
    ("judgmental-forecast", "Which structured elicitation and evidence produce a judgmental forecast when history is absent or disrupted?", "judgment protocol", ["fpp3", "principles"], ["forecast-purpose"]),
    ("combination", "Which candidates, weights, dependence assumptions and update policy form a combined forecast?", "combination algebra", ["bates-granger", "clemen"], ["estimator-family", "judgmental-forecast"]),
    ("point-forecast", "Is the point a mean, median, mode, quantile or decision-oriented functional?", "elicitable functional", ["gneiting-raftery", "fpp3"], ["estimator-family"]),
    ("quantile-interval", "Which quantile levels or interval construction, coverage target and conditioning apply?", "marginal uncertainty algebra", ["gneiting-raftery", "m5-uncertainty"], ["estimator-family"]),
    ("sample-path-joint", "Which joint distribution, path dependence, cross-series dependence and sampling identity apply?", "joint forecast distribution", ["gluonts", "prob-reconciliation"], ["quantile-interval"]),
    ("conformal-coverage", "Which conformity score, calibration window, dependence assumptions and adaptive coverage rule apply?", "distribution-free interval protocol", ["aci"], ["information-cut"]),
    ("intermittent-demand", "How are demand occurrence, positive size, zero stretches and obsolescence modeled?", "hurdle/renewal forecast", ["croston", "syntetos-boylan", "tsb"], ["missing-censor-zero"]),
    ("hierarchy-group-structure", "Which nested, grouped or general linear aggregation constraints define coherence?", "summing/constraint algebra", ["hyndman-hierarchical", "mint"], ["target-semantics"]),
    ("temporal-hierarchy", "Which multiple temporal aggregation levels and calendars must cohere?", "temporal summing algebra", ["temporal-hierarchies"], ["calendar-frequency"]),
    ("point-reconciliation", "Which base forecasts, mapping, covariance estimate and projection produce coherent point forecasts?", "linear reconciliation", ["mint", "reconciliation-review"], ["hierarchy-group-structure"]),
    ("probabilistic-reconciliation", "Which transformation conditions or samples preserve constraints and distributional meaning?", "distribution reconciliation", ["prob-reconciliation", "cross-temporal-prob"], ["sample-path-joint", "point-reconciliation"]),
    ("cross-temporal-reconciliation", "Which cross-sectional and temporal constraints are applied jointly and in what order?", "cross-temporal algebra", ["cross-temporal-prob", "reconciliation-review"], ["temporal-hierarchy", "probabilistic-reconciliation"]),
    ("evaluation-cut", "Which rolling origins, gaps, horizons, vintages, series and outcome-finality rules form the test design?", "temporal evaluation design", ["tashman", "alfred"], ["information-cut"]),
    ("metric-applicability", "Which loss/score is defined for the output form, zeros, scale, hierarchy and decision purpose?", "metric applicability", ["hyndman-koehler", "gneiting-raftery"], ["evaluation-cut"]),
    ("proper-score", "Which strictly/proper score evaluates the declared predictive functional or distribution?", "scoring-rule algebra", ["gneiting-raftery", "m5-uncertainty"], ["metric-applicability"]),
    ("calibration-sharpness", "Are probabilities/quantiles calibrated, and how sharp are they subject to calibration?", "probabilistic diagnostic", ["gneiting-raftery", "aci"], ["proper-score"]),
    ("aggregation-weighting", "Which series, horizon, scale, value or decision weights aggregate evaluation results?", "evaluation aggregation", ["m5-accuracy", "m5-uncertainty"], ["metric-applicability"]),
    ("skill-comparison", "What skill over baselines exists, with what sampling uncertainty and test multiplicity?", "comparative appraisal", ["diebold-mariano", "m4"], ["benchmark-baseline", "aggregation-weighting"]),
    ("robustness-shift", "How stable is performance across regimes, horizons, slices, revisions and distribution shift?", "robustness appraisal", ["aci", "business-methods"], ["skill-comparison"]),
    ("selection-profile", "Which candidates, baselines, evidence, costs, constraints and abstention rules govern recommendation?", "selection policy", ["m4", "business-methods"], ["robustness-shift"]),
    ("forecast-definition", "Which purpose, target, temporal, information, output and consumer contracts identify a definition edition?", "definition aggregate", ["fpp3", "prov"], ["forecast-purpose", "target-semantics", "origin-horizon", "information-cut"]),
    ("forecast-run", "Which definition, method, data cut, provider, randomness and resource attempt identify generation?", "run aggregate", ["sktime", "statsforecast", "prov"], ["forecast-definition", "estimator-family"]),
    ("forecast-edition", "Which immutable forecast artifact edition, supersession, approval, expiry and retraction state applies?", "forecast lifecycle", ["prov", "cloudevents"], ["forecast-run"]),
    ("publication-profile", "Which audience, representation, disclosure, effective time, subscription and recall rules publish an edition?", "publication policy", ["cloudevents", "prov"], ["forecast-edition"]),
    ("realization-join", "Which outcome vintage realizes each exact origin/horizon target without hindsight leakage?", "forecast-outcome join", ["alfred", "tashman"], ["forecast-edition", "revision-vintage-finality"]),
    ("override-policy", "Who may propose/approve which adjustment, for what evidence, magnitude, shape and expiry?", "authority policy", ["fva", "business-methods"], ["forecast-edition"]),
    ("override-lifecycle", "Which base-preserving proposal, review, approval, application, withdrawal and supersession states exist?", "override aggregate", ["fva", "prov"], ["override-policy"]),
    ("forecast-value-added", "Did a process step or adjustment improve bounded forecast performance relative to its base?", "ex-post process evaluation", ["fva", "diebold-mariano"], ["override-lifecycle", "realization-join"]),
    ("forecast-product-boundary", "What forecast definition/run/evaluation/governance lifecycle belongs to Forecasting Workbench?", "product boundary", ["business-methods", "fpp3"], ["publication-profile", "forecast-value-added"]),
    ("planning-purpose", "Which desired outcomes and choices must be coordinated, and who bears consequences?", "planning intent", ["ascm-dictionary", "afp-fpa"], []),
    ("planning-scenario", "Which inherited forecasts, assumptions, controllable choices and external conditions identify a scenario?", "scenario aggregate", ["ascm-dictionary", "scor"], ["planning-purpose", "forecast-product-boundary"]),
    ("objective-preference", "Which goals, priorities, tradeoffs and utility/loss orientation apply?", "objective/preference algebra", ["afp-fpa", "dmn"], ["planning-purpose"]),
    ("constraint-policy", "Which hard/soft constraints, business policies and exceptions limit alternatives?", "constraint/policy algebra", ["ascm-sop", "dmn"], ["planning-purpose"]),
    ("resource-capacity", "Which funds, people, materials, equipment, time and capacity are available at each grain?", "resource envelope", ["ascm-sop", "afp-pbf"], ["constraint-policy"]),
    ("plan-alternative", "Which choices, allocations, schedule, expected outcomes and residual risks form one alternative?", "plan algebra", ["ascm-dictionary", "afp-pbf"], ["planning-scenario", "objective-preference", "resource-capacity"]),
    ("feasibility-validation", "Does an alternative satisfy exact constraints and resource balances, and what remains infeasible?", "feasibility oracle", ["ascm-sop", "scor"], ["plan-alternative"]),
    ("cross-functional-reconciliation", "How are demand, supply, capacity, inventory, workforce and finance conflicts exposed and resolved?", "plan reconciliation protocol", ["ascm-sop", "ascm-dictionary"], ["feasibility-validation"]),
    ("consensus-approval", "Which proposal, review, consensus, approval and dissent states exist, with whose authority?", "human authority protocol", ["ascm-sop", "dmn"], ["cross-functional-reconciliation"]),
    ("commitment-release", "Which approved plan becomes a commitment or released execution instruction?", "effect handoff", ["ascm-sop", "afp-fpa"], ["consensus-approval"]),
    ("variance-replan", "Which actual/forecast/plan variance or assumption failure triggers reforecast, replan or supersession?", "adaptive plan lifecycle", ["afp-pbf", "ascm-sop"], ["commitment-release"]),
    ("vertical-plan-profile", "Which finance, demand, supply, capacity, workforce or project vocabulary specializes the horizontal planner?", "vertical ACL", ["scor", "afp-fpa"], ["planning-purpose"]),
    ("planning-product-boundary", "What scenario/alternative/reconciliation/approval/commitment lifecycle warrants an Integrated Planning Workbench?", "product boundary", ["ascm-dictionary", "afp-fpa"], ["variance-replan", "vertical-plan-profile"]),
]


def modules() -> list[dict[str, Any]]:
    return [{
        "module_id": f"module.foreplan.{key}", "owned_question": question, "formalism": formalism,
        "source_refs": sorted(f"source.foreplan.{source}" for source in source_refs),
        "dependency_refs": sorted(f"module.foreplan.{dep}" for dep in deps),
        "authority_limit": "Forecast evidence does not establish plan desirability, approval, commitment or effect; planning authority does not rewrite forecast or actual truth.",
        "research_status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED",
    } for key, question, formalism, source_refs, deps in MODULE_ROWS]


LAW_STATEMENTS = [
    "Forecast is not observation, actual, target, budget, plan, decision, commitment or effect.",
    "Forecast target variable is not a management target or desired outcome.",
    "Event time, availability time, recording time, revision time, forecast origin, target time and publication time are distinct.",
    "Observation identity is not value equality, source-row identity, vintage identity or final-outcome identity.",
    "Latest observation vintage is not the vintage available at a historical forecast origin.",
    "Missing, censored, suppressed, structural zero, sampled zero, outlier and not-yet-available are distinct.",
    "Calendar period identity is not duration equality or timestamp equality.",
    "Forecast horizon is origin-relative and is not merely an integer column name.",
    "Known future covariate is not forecast covariate; perfect-foresight evaluation is not deployable evidence.",
    "Backtest training cut is not evaluation cut, production cut or current data cut.",
    "Random split validation is not time-respecting forecast evaluation.",
    "Point forecast is not inherently mean, median, mode, quantile, target or most likely future.",
    "Quantile set is not prediction interval, sample path or coherent joint distribution.",
    "Marginal calibration is not joint calibration, path realism or decision fitness.",
    "Nominal coverage is not finite-sample, conditional or under-shift coverage without assumptions.",
    "Accuracy, bias, calibration, sharpness, stability, coherence, latency and cost are distinct qualities.",
    "MAE, RMSE, MAPE, sMAPE, MASE, pinball loss, WIS, CRPS and log score answer different questions.",
    "Undefined or unstable percentage error near zero cannot be silently coerced to zero.",
    "A proper score evaluates a declared predictive object; it does not encode all business utility.",
    "Aggregate score equality does not imply equal horizon, item, tail or subgroup performance.",
    "Statistical significance is not practical value, robustness, causality or deployment authority.",
    "Leaderboard rank is not universal superiority, portability or production qualification.",
    "Naive baseline is not optional; complex model performance without baseline skill is uninterpretable.",
    "Model selection recommendation is not owner approval or forecast publication.",
    "Estimator definition is not fit artifact, forecast run, forecast artifact or published edition.",
    "Method family identity is not provider implementation identity or semantic equivalence.",
    "Statistical, econometric, machine-learning, deep and foundation models share forecast laws but not assumptions.",
    "Forecast combination is not reconciliation; weighting candidates does not guarantee structural coherence.",
    "Point reconciliation is not probabilistic reconciliation.",
    "Cross-sectional, grouped, temporal and cross-temporal reconciliation are not interchangeable.",
    "Forecast coherence is not forecast accuracy, plan feasibility, accounting balance or stakeholder consensus.",
    "Statistical forecast reconciliation is not ledger reconciliation or cross-functional plan reconciliation.",
    "Demand occurrence probability is not positive demand size; intermittent demand needs both.",
    "Demand forecast is not inventory policy, replenishment order or service-level commitment.",
    "Judgmental forecast is not arbitrary override; it requires task, evidence, identity and feedback.",
    "Override proposal is not approval; approval is not application; application is not truth rewrite.",
    "Adjusted forecast preserves its base and rationale; it does not erase the algorithmic edition.",
    "Positive forecast value added is not causal proof that an adjustment policy or actor created value.",
    "Forecast publication is not consumption, plan adoption, action authorization or effect receipt.",
    "Retraction or recall issuance is not completed downstream propagation.",
    "Scenario is not forecast: it conditions on assumptions or choices and need not be judged by predictive probability.",
    "What-if simulation is not forecast, optimized plan or committed plan.",
    "Budget is not forecast: it formalizes an authorized financial plan or limit.",
    "Management target is not expected outcome; pressure to meet a target must not contaminate forecast truth.",
    "Plan alternative is not recommendation, approved plan, commitment, schedule, command or execution.",
    "Objective is not constraint, preference, policy, metric or authority.",
    "Hard constraint is not soft preference; infeasible is not merely low-scoring.",
    "Optimization solution is a candidate under a model, not automatically a feasible or authorized real-world plan.",
    "Consensus is not truth, unanimity, approval or authority.",
    "Cross-functional plan reconciliation must preserve disagreements and constraints, not manufacture one number by averaging.",
    "Approved plan is not executable instruction until exact effect authority and handoff are satisfied.",
    "Plan variance is not forecast error unless the compared objects, vintages and purposes align.",
    "Reforecast updates expected outcomes; replan changes intended choices or allocations.",
    "Actual outcome does not retroactively change the identity of the forecast or plan assessed against it.",
    "Finance, demand, supply, capacity and workforce planning are vertical profiles over shared planning mechanics, not synonyms.",
    "Forecasting Workbench does not own actual truth, generic model lifecycle, planning objectives, approval or execution.",
    "Integrated Planning Workbench imports forecasts, simulations and optimization proposals but owns their coordinated plan lifecycle.",
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.foreplan.{i:03d}", "statement": statement,
             "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0}
            for i, statement in enumerate(LAW_STATEMENTS, 1)]


METHOD_GROUPS = {
    "baseline_smoothing": ["mean forecast", "naive forecast", "seasonal naive", "drift", "moving average", "simple exponential smoothing", "Holt trend", "damped trend", "Holt-Winters additive", "Holt-Winters multiplicative", "ETS automatic selection"],
    "statistical_time_series": ["AR", "MA", "ARMA", "ARIMA", "seasonal ARIMA", "ARIMAX/dynamic regression", "structural time series", "local level/trend state space", "unobserved components", "dynamic harmonic regression", "Theta method", "TBATS/BATS", "VAR", "VECM", "dynamic factor model"],
    "special_series": ["Croston", "Syntetos-Boylan adjustment", "Teunter-Syntetos-Babai", "ADIDA", "IMAPA", "count forecast", "survival/time-to-event forecast", "functional time-series forecast", "spatio-temporal forecast", "nowcasting", "mixed-frequency forecast", "change-point/regime forecast"],
    "causal_exogenous_judgment": ["regression with forecast predictors", "intervention/event model", "transfer-function model", "leading-indicator model", "econometric structural model", "expert judgment", "Delphi", "prediction market", "structured analogy", "scenario-conditioned projection", "judgmental adjustment", "debiased adjustment"],
    "machine_predictive": ["tree ensemble forecast", "gradient-boosted forecast", "support-vector regression forecast", "nearest-neighbor forecast", "Gaussian-process forecast", "neural autoregression", "recurrent sequence forecast", "temporal convolution forecast", "transformer time-series forecast", "global pooled forecast", "hybrid statistical-predictive forecast", "foundation time-series forecast"],
    "combination_selection": ["simple average combination", "median combination", "variance-covariance weighting", "regression stacking", "Bayesian model averaging", "online expert aggregation", "ensemble pruning", "per-series model selection", "per-horizon model selection", "meta-learning selection", "selection abstention", "champion-challenger"],
    "probabilistic": ["parametric predictive distribution", "quantile regression forecast", "distributional regression", "bootstrap forecast interval", "simulation/sample-path forecast", "Bayesian posterior predictive", "conformal prediction interval", "adaptive conformal interval", "copula joint forecast", "ensemble distribution", "calibrated probability forecast", "extreme/tail forecast"],
    "reconciliation": ["bottom-up", "top-down proportions", "middle-out", "OLS reconciliation", "WLS reconciliation", "MinT reconciliation", "nonnegative reconciliation", "temporal hierarchy reconciliation", "cross-temporal reconciliation", "probabilistic projection reconciliation", "probabilistic conditioning reconciliation", "sample-path reconciliation", "general linear-constraint reconciliation"],
    "evaluation": ["fixed-origin holdout", "rolling-origin expanding window", "rolling-origin sliding window", "gap/embargo evaluation", "multi-horizon evaluation", "vintage-real-time evaluation", "MAE/RMSE evaluation", "MASE/RMSSE evaluation", "pinball-loss evaluation", "WIS/CRPS evaluation", "log-score evaluation", "calibration/reliability analysis", "sharpness analysis", "Diebold-Mariano comparison", "forecast value-added analysis", "slice/regime robustness", "rank uncertainty", "operational-cost evaluation"],
    "planning": ["driver-based planning", "rolling planning", "scenario planning", "budgeting", "demand planning", "supply planning", "capacity planning", "inventory planning", "workforce planning", "financial planning", "sales and operations planning", "integrated business planning", "constraint-based planning", "optimization-assisted planning", "simulation-assisted planning", "consensus planning", "exception-based planning", "plan-versus-actual variance", "replanning", "contingency planning"],
}


def methods() -> list[dict[str, Any]]:
    module_for = {
        "baseline_smoothing": "estimator-family", "statistical_time_series": "estimator-family",
        "special_series": "intermittent-demand", "causal_exogenous_judgment": "judgmental-forecast",
        "machine_predictive": "estimator-family", "combination_selection": "combination",
        "probabilistic": "sample-path-joint", "reconciliation": "cross-temporal-reconciliation",
        "evaluation": "evaluation-cut", "planning": "planning-product-boundary",
    }
    source_for = {
        "baseline_smoothing": ["fpp3", "m4"], "statistical_time_series": ["fpp3", "statsmodels"],
        "special_series": ["croston", "syntetos-boylan", "tsb"], "causal_exogenous_judgment": ["fpp3", "business-methods"],
        "machine_predictive": ["m5-accuracy", "business-methods"], "combination_selection": ["bates-granger", "clemen"],
        "probabilistic": ["gneiting-raftery", "aci", "m5-uncertainty"], "reconciliation": ["mint", "reconciliation-review"],
        "evaluation": ["tashman", "hyndman-koehler", "gneiting-raftery"], "planning": ["ascm-sop", "ascm-dictionary", "afp-pbf"],
    }
    rows = []
    for group, names in METHOD_GROUPS.items():
        for i, name in enumerate(names, 1):
            rows.append({
                "method_type_id": f"method.foreplan.{group}.{i:02d}", "method_group": group,
                "name": name, "semantic_module_ref": f"module.foreplan.{module_for[group]}",
                "source_refs": sorted(f"source.foreplan.{ref}" for ref in source_for[group]),
                "result_law": "Every method returns a typed result with exact target, origin/horizon, information cut, output form, assumptions, provider/plan identity, uncertainty and no implied planning or effect authority.",
                "llm_dependency": "none", "status": "EVIDENCE_BACKED_METHOD_TYPE_CANDIDATE_UNRATIFIED",
            })
    return rows


EXPERT_ROWS = [
    ("hyndman", "Rob J. Hyndman", "forecast methods, evaluation and reconciliation", "Make target, horizon, baseline, time-respecting evaluation and coherent hierarchy first-class contracts.", ["fpp3", "hyndman-koehler", "hyndman-hierarchical"]),
    ("athanasopoulos", "George Athanasopoulos", "hierarchical and temporal forecasting", "Represent grouped, cross-sectional and temporal structures explicitly before reconciliation.", ["fpp3", "temporal-hierarchies", "mint"]),
    ("gneiting", "Tilmann Gneiting", "probabilistic forecasting and scoring rules", "Match each predictive functional/distribution to a proper score and separate calibration from sharpness.", ["gneiting-raftery"]),
    ("raftery", "Adrian Raftery", "probabilistic prediction and calibration", "Preserve distributions and uncertainty rather than reducing every forecast to a point.", ["gneiting-raftery"]),
    ("makridakis", "Spyros Makridakis", "forecasting competitions and empirical comparison", "Require large, heterogeneous benchmarks and strong simple baselines; never universalize a leaderboard.", ["m4", "m5-accuracy", "m6"]),
    ("spiliotis", "Evangelos Spiliotis", "large-scale forecast evaluation", "Bind rankings to exact series, horizon, metric, weighting and submission rules.", ["m4", "m5-accuracy"]),
    ("assimakopoulos", "Vassilios Assimakopoulos", "forecast methods and competitions", "Treat hybrid and combination performance as empirical evidence, not method-family authority.", ["m4"]),
    ("wickramasuriya", "Shanika Wickramasuriya", "point and probabilistic reconciliation", "Keep constraint space, covariance estimate and distributional assumptions visible in reconciliation.", ["mint", "prob-reconciliation"]),
    ("tashman", "Len Tashman", "forecast evaluation design", "Use rolling origins and preserve horizon-specific out-of-sample evidence.", ["tashman", "business-methods"]),
    ("diebold", "Francis Diebold", "predictive accuracy comparison", "Compare loss differentials with dependence-aware uncertainty rather than ranks alone.", ["diebold-mariano"]),
    ("mariano", "Roberto Mariano", "forecast comparison", "Separate observed score differences from evidence that predictive accuracy truly differs.", ["diebold-mariano"]),
    ("goodwin", "Paul Goodwin", "judgmental forecasting and organizational practice", "Structure judgment, segregate forecasts from targets and evaluate adjustments ex post.", ["business-methods", "fva"]),
    ("fildes", "Robert Fildes", "business and demand forecasting", "Preserve base forecasts and measure when process steps and adjustments add or destroy value.", ["fva", "business-methods"]),
    ("de-baets", "Shari De Baets", "judgmental adjustment and FVA", "Treat direction, magnitude, evidence and SKU-level heterogeneity as explicit adjustment decisions.", ["fva"]),
    ("petropoulos", "Fotios Petropoulos", "forecasting practice and methods", "Connect methodological evidence to operational adoption without collapsing forecast into decision.", ["business-methods"]),
    ("syntetos", "Aris Syntetos", "intermittent demand", "Separate demand occurrence from positive size and bind metrics to inventory consequences.", ["syntetos-boylan", "tsb"]),
    ("boylan", "John Boylan", "intermittent demand and inventory forecasting", "Expose bias corrections and demand regimes rather than treating zeros as ordinary continuous observations.", ["syntetos-boylan"]),
    ("teunter", "Ruud Teunter", "intermittent demand and obsolescence", "Model declining occurrence probability explicitly when obsolescence makes classic Croston updates stale.", ["tsb"]),
    ("croston", "J. D. Croston", "intermittent demand decomposition", "Decompose arrival intervals and nonzero sizes while retaining later bias corrections and limits.", ["croston"]),
    ("clemen", "Robert Clemen", "forecast combination", "Prefer explicit combination assumptions and comparative evidence over winner-take-all selection.", ["clemen", "bates-granger"]),
    ("zafran", "Margaux Zaffran", "adaptive conformal time-series prediction", "State dependence and adaptation assumptions when claiming interval coverage under shift.", ["aci"]),
    ("feron", "Olivier Féron", "probabilistic energy forecasting", "Evaluate interval procedures in sequential operational settings, not exchangeable abstractions alone.", ["aci"]),
    ("lapide", "Larry Lapide", "sales and operations planning", "Keep forecasting as an input to cross-functional planning and executive decision, not the plan itself.", ["ascm-sop"]),
    ("wallace", "Thomas Wallace", "sales and operations planning", "Model the recurring review, ownership and single feasible plan process independently of forecast generation.", ["ascm-sop"]),
    ("oliver-wight", "Oliver Wight practitioners", "integrated business planning", "Connect strategic, operational and financial choices while preserving functional plans and disagreement.", ["ascm-dictionary"]),
    ("fp-and-a", "AFP FP&A practitioner body", "financial planning and analysis", "Separate plan, budget, forecast, performance analysis and resource-allocation decision support.", ["afp-pbf", "afp-fpa"]),
]


def experts() -> list[dict[str, Any]]:
    return [{
        "expert_id": f"expert.foreplan.{key}", "name": name, "specialism": specialism,
        "learning_for_corpus": learning, "source_refs": sorted(f"source.foreplan.{ref}" for ref in refs),
        "authority_limit": "Expert work informs bounded propositions; no person, paper, vendor or professional body becomes the SAN semantic owner.",
        "status": "LEARNING_PROFILE_NOT_ENDORSEMENT",
    } for key, name, specialism, learning, refs in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("prob-reconciliation", 2021, "Gaussian probabilistic reconciliation", "Extends coherence from point means toward reconciled predictive distributions under explicit Gaussian assumptions.", ["prob-reconciliation"], "none"),
    ("sdmx3", 2021, "SDMX 3.0 information model", "Strengthens machine-readable statistical series, dimensions and attributes used at the observation border.", ["sdmx"], "none"),
    ("aci", 2022, "Adaptive conformal prediction for time series", "Adds sequentially adaptive interval coverage machinery under dependence and distribution shift.", ["aci"], "predictive_model_agnostic_not_llm"),
    ("m5-uncertainty", 2022, "Large-scale hierarchical uncertainty competition", "Makes nine-quantile forecasts, weighted interval scoring and hierarchical retail evaluation first-class.", ["m5-uncertainty"], "none"),
    ("m5-accuracy", 2022, "Large-scale hierarchical retail accuracy competition", "Combines granular series, hierarchy/value weighting, exogenous events and scaled errors.", ["m5-accuracy"], "method_optional_not_llm"),
    ("m6-decision-separation", 2023, "M6 forecast-versus-decision evaluation", "Empirically separates return-ranking forecast skill from portfolio decision performance.", ["m6"], "none"),
    ("business-adoption", 2023, "Systematic forecasting adoption evidence", "Surfaces the compiler need for auditable judgment, uncertainty communication, monitoring and process feedback.", ["business-methods"], "none"),
    ("cross-temporal-prob", 2023, "Cross-temporal probabilistic reconciliation", "Unifies probabilistic coherence constraints across series and temporal aggregation levels.", ["cross-temporal-prob"], "none"),
    ("general-linear-reconciliation", 2023, "General linearly constrained reconciliation", "Moves beyond tree hierarchies toward free/constrained variable structures.", ["reconciliation-review"], "none"),
    ("reconciliation-review", 2024, "Unified reconciliation research map", "Clarifies point, probabilistic, Bayesian, temporal and machine-learning approaches and their non-equivalence.", ["reconciliation-review"], "method_optional_not_llm"),
    ("fva-meta", 2025, "Cross-study forecast value-added analysis", "Provides large multi-study evidence on when human adjustments add or destroy bounded value.", ["fva"], "none"),
    ("private-vintage-evaluation", 2025, "Vintage-aware real-time evaluation emphasis", "Elevates information-set reconstruction and revision-aware outcomes over hindsight backtests.", ["alfred", "fva"], "none"),
    ("rolling-integrated-planning", 2025, "Continuous integrated planning practice", "Moves planning from annual static budgets toward editioned scenarios, rolling forecasts and cross-functional replanning.", ["ascm-dictionary", "afp-pbf"], "none"),
    ("distribution-object-apis", 2026, "Distribution and sample-path forecast APIs", "Independent frameworks expose forecast objects richer than point tables, motivating portable result algebra.", ["gluonts", "sktime"], "model_optional_not_llm"),
    ("scor-digital-planning", 2026, "SCOR Digital Standard planning practices", "Provides machine-addressable process distinctions for network, scenario, S&OP and integrated business planning.", ["scor"], "none"),
]


def innovations() -> list[dict[str, Any]]:
    return [{
        "innovation_id": f"innovation.foreplan.{key}", "year": year, "name": name,
        "compiler_relevance": relevance, "source_refs": sorted(f"source.foreplan.{ref}" for ref in refs),
        "ai_or_llm_dependency": dependency, "status": "RECENT_INNOVATION_CANDIDATE_UNRATIFIED",
    } for key, year, name, relevance, refs, dependency in INNOVATION_ROWS]


def module_refs_for_library(library_ref: str) -> list[str]:
    text = library_ref.lower()
    keys = {"forecast-purpose", "target-semantics", "origin-horizon", "information-cut"}
    if "time" in text or "calendar" in text: keys |= {"calendar-frequency", "observation-occurrence", "revision-vintage-finality"}
    if "estim" in text or "model" in text or "forecasting_methods" in text: keys |= {"series-features-regime", "benchmark-baseline", "estimator-family", "intermittent-demand", "combination"}
    if "probab" in text or "conformal" in text: keys |= {"quantile-interval", "sample-path-joint", "conformal-coverage", "proper-score", "calibration-sharpness"}
    if "evaluation" in text or "metric" in text or "selection" in text: keys |= {"evaluation-cut", "metric-applicability", "aggregation-weighting", "skill-comparison", "robustness-shift", "selection-profile"}
    if "reconciliation" in text: keys |= {"hierarchy-group-structure", "temporal-hierarchy", "point-reconciliation", "probabilistic-reconciliation", "cross-temporal-reconciliation"}
    if "definition" in text: keys |= {"forecast-definition", "missing-censor-zero"}
    if "edition" in text or "publication" in text: keys |= {"forecast-run", "forecast-edition", "publication-profile", "realization-join"}
    if "override" in text: keys |= {"override-policy", "override-lifecycle", "forecast-value-added"}
    if "objective" in text or "constraint" in text or "optimization" in text: keys |= {"planning-purpose", "objective-preference", "constraint-policy", "feasibility-validation"}
    if "simulation" in text: keys |= {"planning-scenario", "plan-alternative"}
    if "budget" in text or "resource" in text: keys |= {"resource-capacity", "plan-alternative", "commitment-release"}
    return sorted(f"module.foreplan.{key}" for key in keys)


def library_bindings(source_ids: set[str]) -> list[dict[str, Any]]:
    direct = declared_product_libraries()
    default_sources = sorted(source_ids)[:6]
    rows = []
    for ref in LIBRARIES:
        rows.append({
            "library_ref": ref,
            "relationship_to_product": "DECLARED_CONCRETE_BINDING" if ref in direct else "JUSTIFIED_NEIGHBOR_IMPORT_OR_OWNER",
            "semantic_module_refs": module_refs_for_library(ref), "evidence_refs": default_sources,
            "downstream_product_refs": sorted(PRODUCTS),
            "downstream_contract_route": "DECLARED_PRODUCT_BINDING_UNRATIFIED" if ref in direct else "NEIGHBOR_IMPORT_CANDIDATE_UNRATIFIED",
            "refusal_reasons": ["OWNER_RATIFICATION_MISSING", "EXACT_CONTRACT_UNSELECTED", "QUALIFIED_IMPLEMENTATION_MISSING", "TWO_VERTICAL_ACCEPTANCE_MISSING"],
            "compiler_binding": "REFUSED", "completion_claim": False,
        })
    return rows


def axis_rows(bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "library_ref": binding["library_ref"], "axis": axis,
        "semantic_module_refs": binding["semantic_module_refs"], "evidence_refs": binding["evidence_refs"],
        "decision_candidate": "UNRESOLVED_RESEARCHED_CANDIDATE", "coordinate_answers": [],
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False,
    } for binding in bindings for axis in AXES]


def findings() -> list[dict[str, Any]]:
    rows = [{
        "finding_id": "finding.foreplan.forecasting-product.v1",
        "candidate_disposition": "RETAIN_FORECASTING_WORKBENCH_BUT_NARROW_IMPORTED_OWNERS",
        "product_ref": "product.forecasting_workbench", "library_refs": sorted(declared_product_libraries()),
        "finding": "Retain forecast definition, generation, temporal evaluation, selection, reconciliation, override and publication governance while importing observation truth, generic predictive model lifecycle, planning, decision and effects.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }, {
        "finding_id": "finding.foreplan.integrated-planning-product.v1",
        "candidate_disposition": "RETAIN_INTEGRATED_PLANNING_WORKBENCH_WITH_EXACT_IMPORTED_OWNERS",
        "product_ref": "product.integrated_planning_workbench",
        "library_refs": sorted(ref for ref, _ in VACANCIES if ref.startswith("library.analytics_planning.")),
        "finding": "ASCM plus independently replaceable SAP, Oracle and Pigment implementations prove a stable scenario, alternative, feasibility, reconciliation, review, approval, publication, variance and replanning lifecycle distinct from forecasting, method execution, generic workflow and operational effects.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }, {
        "finding_id": "finding.foreplan.frontier-cluster-split.v1",
        "candidate_disposition": "SPLIT_FORECASTING_AND_PLANNING_PRODUCT_FORMALISMS",
        "library_refs": sorted(declared_product_libraries()),
        "finding": "The current frontier label forecasting/planning hides two products: forecasting estimates uncertain futures; planning coordinates intended choices under objectives, constraints and authority.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }, {
        "finding_id": "finding.foreplan.forecast-estimators-split.v1",
        "candidate_disposition": "SPLIT_OVERBROAD_FORECAST_ESTIMATORS_LIBRARY",
        "library_refs": ["library.method_kernels.forecast_estimators"],
        "finding": "Baseline, statistical, intermittent, exogenous, learned, probabilistic and combination estimators have different assumptions, result forms and conformance oracles.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }]
    for i, (ref, rationale) in enumerate(VACANCIES, 1):
        rows.append({
            "finding_id": f"finding.foreplan.library-vacancy.{i:02d}",
            "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED",
            "proposed_library_ref": ref, "library_refs": [], "finding": rationale,
            "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
        })
    return rows


def bounded_context() -> dict[str, Any]:
    return {
        "slice_id": "slice.forecasting-planning.v1",
        "retained_product": "product.forecasting_workbench",
        "retained_products": sorted(PRODUCTS),
        "inside_forecasting_workbench": ["forecast definition", "origin/horizon and information cut", "generation run/edition", "temporal evaluation and selection", "forecast reconciliation", "base-preserving override", "publication and recall"],
        "inside_integrated_planning_workbench_candidate": ["planning scenario and assumptions", "plan alternatives", "objective/constraint/resource binding", "feasibility", "cross-functional reconciliation", "consensus/approval/commitment", "variance and replanning"],
        "imported_owners": ["observation and actual truth", "generic model lifecycle", "simulation", "optimization", "vertical business vocabulary", "authority and policy", "execution/effects"],
        "vertical_solution_pack_candidates": ["financial planning", "demand planning", "supply planning", "capacity planning", "inventory planning", "workforce planning", "project/portfolio planning"],
        "product_boundary_candidates": [
            {"product_ref": "product.forecasting_workbench", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
            {"product_ref": "product.integrated_planning_workbench", "status": "RETAIN_WITH_EXACT_IMPORTS_UNRATIFIED"},
        ],
        "non_collapse_summary": "observation/actual != forecast != scenario != target/budget != plan alternative != approved commitment != execution/effect",
        "status": "CANDIDATE_UNRATIFIED", "completion_claim": False,
    }


def build() -> dict[str, Any]:
    src = sources()
    source_ids = {row["source_id"] for row in src}
    mods = modules()
    bindings = library_bindings(source_ids)
    axes = axis_rows(bindings)
    result = {
        "sources": src, "modules": mods, "laws": laws(), "methods": methods(), "experts": experts(),
        "innovations": innovations(), "libraries": bindings, "axes": axes, "findings": findings(),
        "context": bounded_context(),
    }
    result["summary"] = {
        "slice_id": "slice.forecasting-planning.v1", "as_of": AS_OF,
        "primary_or_official_sources": len(src), "semantic_modules": len(mods),
        "non_collapse_laws": len(LAW_STATEMENTS), "method_types": sum(map(len, METHOD_GROUPS.values())),
        "expert_learning_profiles": len(EXPERT_ROWS), "recent_innovations": len(INNOVATION_ROWS),
        "declared_product_libraries": len(declared_product_libraries()), "justified_neighbor_libraries": len(NEIGHBORS),
        "bound_libraries": len(LIBRARIES), "library_axis_decision_candidates": len(axes),
        "retained_products": len(PRODUCTS), "candidate_new_products": 0, "candidate_new_library_vacancies": len(VACANCIES),
        "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0,
        "canonical_gaps_closed": 0, "completion_claim": False,
    }
    return result


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "semantic-modules.jsonl": "".join(canonical(row) + "\n" for row in built["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(row) + "\n" for row in built["laws"]),
        "forecasting-planning-method-taxonomy.jsonl": "".join(canonical(row) + "\n" for row in built["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(row) + "\n" for row in built["experts"]),
        "innovation-records.jsonl": "".join(canonical(row) + "\n" for row in built["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(row) + "\n" for row in built["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(row) + "\n" for row in built["findings"]),
        "bounded-context.json": json.dumps(built["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({
        "manifest_id": "manifest.forecasting-planning-semantic-slice.v1", "as_of": AS_OF,
        "files": claims, "completion_claim": False,
    }, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    summary = build()["summary"]
    print(f"BUILD PASS forecasting/planning semantic slice: {summary['semantic_modules']} modules, {summary['method_types']} methods, {summary['bound_libraries']} libraries, {summary['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
