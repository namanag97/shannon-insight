#!/usr/bin/env python3
"""Build an evidence-backed semantic slice for causal inference and experimentation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
AS_OF = "2026-08-27"

AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def library_universe() -> list[str]:
    rows = load_jsonl(REGISTRY / "library-contributions.jsonl")
    prefixes = ("library.experiment.", "library.method_kernels.causal", "library.method_kernels.experiment")
    return sorted(row["library_id"] for row in rows if row["library_id"].startswith(prefixes) or row["library_id"] == "library.predictive.causal_effect_learners")


LIBRARIES = library_universe()


def sources() -> list[dict[str, Any]]:
    rows = [
        ("what-if", "Causal Inference: What If", ["Miguel A. Hernán", "James M. Robins"], 2024, "open_foundational_text", "https://www.hsph.harvard.edu/miguel-hernan/wp-content/uploads/sites/1268/2024/04/hernanrobins_WhatIf_26apr24.pdf", "Separates causal questions, potential outcomes, identification, estimation, target trials and longitudinal treatment strategies.", "The framework does not establish assumptions or fitness for a particular study."),
        ("pearl-causality", "Causality: Models, Reasoning, and Inference", ["Judea Pearl"], 2009, "foundational_formal_text", "https://bayes.cs.ucla.edu/BOOK-2K/", "Defines structural causal models, interventions, counterfactuals, graphical identification and do-calculus.", "A supplied graph encodes assumptions; it is not observational proof of its arrows."),
        ("pearl-diagrams", "Causal Diagrams for Empirical Research", ["Judea Pearl"], 1995, "peer_reviewed_foundational_research", "https://doi.org/10.1093/biomet/82.4.669", "Formalizes graphical criteria and intervention identification in causal diagrams.", "Graphical identifiability is conditional on the assumed graph and model class."),
        ("imbens-rubin", "Causal Inference for Statistics, Social, and Biomedical Sciences", ["Guido W. Imbens", "Donald B. Rubin"], 2015, "foundational_formal_text", "https://doi.org/10.1017/CBO9781139025751", "Develops potential-outcome estimands, assignment mechanisms, randomized experiments and observational designs.", "The text does not make every assignment mechanism known or every observational comparison unconfounded."),
        ("consort-2025", "CONSORT 2025 statement: updated guideline for reporting randomised trials", ["CONSORT Group"], 2025, "current_reporting_guideline", "https://www.bmj.com/content/389/bmj-2024-081123", "Requires transparent reporting of design, randomization, analysis, harms, participant flow, protocol and open-science artifacts.", "CONSORT is a reporting guideline, not proof of trial validity or a universal experimental-analysis contract."),
        ("strobe", "STROBE Statement", ["STROBE Initiative"], 2007, "reporting_guideline", "https://www.strobe-statement.org/", "Requires explicit observational design, variables, selection, bias, missingness, confounding control and sensitivity analyses.", "STROBE explicitly is not a prescription for study design and not a quality-assessment instrument."),
        ("target-2025", "Transparent reporting of observational studies emulating a target trial: the TARGET Statement", ["TARGET Working Group"], 2025, "current_reporting_guideline", "https://www.bmj.com/content/390/bmj-2025-087179", "Requires the causal question, target-trial protocol, estimand, identifying assumptions, data mapping, estimates and sensitivity analyses to remain explicit.", "Reporting target-trial emulation does not itself eliminate confounding or design bias."),
        ("ich-e9r1", "ICH E9(R1) Addendum on Estimands and Sensitivity Analysis", ["International Council for Harmonisation"], 2019, "international_regulatory_guideline", "https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf", "Separates treatment condition, population, variable, intercurrent-event strategy and population-level summary in an estimand.", "Regulatory clinical-trial estimands require adaptation before use in unrelated enterprise contexts."),
        ("propensity", "The central role of the propensity score in observational studies for causal effects", ["Paul R. Rosenbaum", "Donald B. Rubin"], 1983, "peer_reviewed_foundational_research", "https://doi.org/10.1093/biomet/70.1.41", "Defines the propensity score and balancing of observed covariates under treatment-assignment assumptions.", "Balance on observed covariates does not prove absence of unmeasured confounding."),
        ("msm", "Marginal structural models and causal inference in epidemiology", ["James M. Robins", "Miguel A. Hernán", "Babette Brumback"], 2000, "peer_reviewed_foundational_research", "https://pubmed.ncbi.nlm.nih.gov/10955408/", "Defines inverse-probability weighted marginal structural models for time-varying treatments with treatment-affected confounders.", "Weighting validity depends on longitudinal identification, positivity and model assumptions."),
        ("late", "Identification and Estimation of Local Average Treatment Effects", ["Joshua D. Angrist", "Guido W. Imbens"], 1994, "peer_reviewed_foundational_research", "https://www.nber.org/papers/t0118", "Shows that an instrument plus additional assumptions identifies a local effect for units whose treatment changes with the instrument.", "Instrument relevance alone does not identify an ATE or validate exclusion, independence or monotonicity."),
        ("rdd", "Regression Discontinuity Designs in Economics", ["David S. Lee", "Thomas Lemieux"], 2010, "peer_reviewed_methodological_guide", "https://doi.org/10.1257/jel.48.2.281", "Defines continuity-based regression-discontinuity identification, estimation, validation and local interpretation.", "A visible cutoff discontinuity does not establish a global treatment effect or exclude manipulation."),
        ("rdd-modern", "Regression Discontinuity Designs", ["Matias D. Cattaneo", "Nicolás Idrobo", "Rocío Titiunik"], 2022, "peer_reviewed_current_synthesis", "https://doi.org/10.1146/annurev-economics-051520-021409", "Separates continuity and local-randomization frameworks and current validation/falsification methods.", "The two frameworks have different assumptions and cannot be silently mixed."),
        ("did-multiple", "Difference-in-Differences with Multiple Time Periods", ["Brantly Callaway", "Pedro H. C. Sant'Anna"], 2021, "peer_reviewed_primary_research", "https://doi.org/10.1016/j.jeconom.2020.12.001", "Identifies group-time treatment effects under staggered timing and supports outcome-regression, weighting and doubly robust estimators.", "A pretrend plot or conventional two-way fixed-effect regression does not prove the needed parallel-trends assumptions."),
        ("did-continuous", "Difference-in-Differences with a Continuous Treatment", ["Brantly Callaway", "Andrew Goodman-Bacon", "Pedro H. C. Sant'Anna"], 2024, "primary_working_paper", "https://www.nber.org/papers/w32117", "Separates level-specific treatment effects from causal responses and exposes selection and TWFE interpretation problems for continuous doses.", "Generalized parallel trends alone may not identify comparisons across dose levels."),
        ("synthetic-control", "Synthetic Control Methods for Comparative Case Studies", ["Alberto Abadie", "Alexis Diamond", "Jens Hainmueller"], 2010, "peer_reviewed_primary_research", "https://doi.org/10.1198/jasa.2009.ap08746", "Constructs a weighted comparison unit for aggregate interventions with pre-treatment fit and placebo-style inference.", "Good pre-treatment fit is not by itself proof of causal validity or post-treatment counterfactual accuracy."),
        ("dml", "Double/debiased machine learning for treatment and structural parameters", ["Victor Chernozhukov", "Denis Chetverikov", "Mert Demirer", "Esther Duflo", "Christian Hansen", "Whitney Newey", "James Robins"], 2018, "peer_reviewed_primary_research", "https://doi.org/10.1111/ectj.12097", "Uses orthogonal scores and cross-fitting to reduce nuisance-estimation bias for declared low-dimensional causal parameters.", "Flexible nuisance prediction does not supply identification assumptions or turn prediction into causation."),
        ("auto-dml", "Automatic Debiased Machine Learning of Causal and Structural Effects", ["Victor Chernozhukov", "Whitney Newey", "Rahul Singh"], 2022, "peer_reviewed_primary_research", "https://doi.org/10.3982/ECTA18515", "Automates construction of debiased estimators for classes of linear functionals using learned Riesz representers.", "Automation is estimator construction under a model, not automatic causal-question or identification discovery."),
        ("causal-forest", "Generalized Random Forests", ["Susan Athey", "Julie Tibshirani", "Stefan Wager"], 2019, "peer_reviewed_primary_research", "https://doi.org/10.1214/18-AOS1709", "Defines forest-based local moment estimation including heterogeneous treatment-effect functionals.", "A conditional-effect estimator does not justify individual causation or a treatment policy."),
        ("mediation", "Explanation in Causal Inference: Methods for Mediation and Interaction", ["Tyler J. VanderWeele"], 2015, "foundational_formal_text", "https://doi.org/10.1093/acprof:oso/9780199325870.001.0001", "Separates total, direct, indirect, mediated and interaction effects with distinct assumptions.", "A measured intermediate variable is not automatically a mediator, and mediation is not feature attribution."),
        ("interference", "Toward Causal Inference With Interference", ["Michael G. Hudgens", "M. Elizabeth Halloran"], 2008, "peer_reviewed_primary_research", "https://doi.org/10.1198/016214508000000292", "Defines direct, indirect, total and overall effects when one unit's assignment can affect another's outcome.", "No-interference/SUTVA must not be assumed merely because data are row-shaped."),
        ("e-value", "Sensitivity Analysis in Observational Research: Introducing the E-Value", ["Tyler J. VanderWeele", "Peng Ding"], 2017, "peer_reviewed_primary_research", "https://doi.org/10.7326/M16-2607", "Quantifies the minimum risk-ratio-scale confounder associations needed to explain away an observed association.", "An E-value does not prove absence of unmeasured confounding or address every bias."),
        ("sensemakr", "Making Sense of Sensitivity", ["Carlos Cinelli", "Chad Hazlett"], 2020, "peer_reviewed_primary_research", "https://doi.org/10.1111/rssb.12348", "Defines partial-R-squared sensitivity analysis and robustness values for omitted-variable bias in linear regression.", "Robustness to a calibrated confounder envelope is not identification proof."),
        ("transport", "Transportability of Causal Effects: Completeness Results", ["Elias Bareinboim", "Judea Pearl"], 2012, "peer_reviewed_primary_research", "https://doi.org/10.1609/aaai.v26i1.8232", "Provides graphical conditions and an algorithm for transporting causal effects between source and target environments.", "Transportability requires explicit cross-population invariance assumptions and is not ordinary replication."),
        ("proximal", "Proximal Causal Learning of Conditional Average Treatment Effects", ["Erik Sverdrup", "Yifan Cui"], 2023, "peer_reviewed_primary_research", "https://proceedings.mlr.press/v202/sverdrup23a.html", "Uses treatment- and outcome-inducing proxies to estimate heterogeneous effects under proximal identification conditions.", "Proxy availability does not by itself establish bridge completeness, relevance or identification."),
        ("proximal-regression", "Regression-based proximal causal inference", ["Jiewen Liu", "Chan Park", "Kendrick Li", "Eric J. Tchetgen Tchetgen"], 2025, "peer_reviewed_primary_research", "https://doi.org/10.1093/aje/kwae370", "Provides regression-based proximal identification and estimation constructions for settings with unmeasured confounding proxies.", "Its structural and bridge assumptions remain domain-specific and unverified by fitting."),
        ("data-fusion", "Robust Direct Learning for Causal Data Fusion", ["Xinyu Li", "Yilin Li", "Qing Cui", "Longfei Li", "Jun Zhou"], 2023, "peer_reviewed_primary_research", "https://proceedings.mlr.press/v189/li23c.html", "Studies homogeneous and heterogeneous causal data fusion with source-specific covariates.", "Multiple sources do not automatically share treatment, outcome, population or causal mechanisms."),
        ("dagitty", "DAGitty: a graphical tool for analyzing causal diagrams", ["Johannes Textor", "Benito van der Zander", "Mark S. Gilthorpe", "Maciej Liśkiewicz", "George T. H. Ellison"], 2016, "peer_reviewed_tool_research", "https://doi.org/10.1093/ije/dyw341", "Supports graphical adjustment-set analysis and testable implications for declared DAGs.", "A tool can analyze a supplied graph but cannot validate its substantive causal assumptions."),
        ("dowhy", "DoWhy: An End-to-End Library for Causal Inference", ["Amit Sharma", "Emre Kiciman"], 2020, "official_open_source_methodology", "https://arxiv.org/abs/2011.04216", "Separates model, identify, estimate and refute stages in a causal-analysis workflow.", "A workflow implementation is a provider, not semantic authority, and refutation tests cannot prove a causal model true."),
        ("doubleml", "DoubleML: An Object-Oriented Implementation of Double Machine Learning", ["Philipp Bach", "Victor Chernozhukov", "Malte S. Kurz", "Martin Spindler"], 2022, "peer_reviewed_reference_implementation", "https://doi.org/10.18637/jss.v102.i03", "Implements sample splitting, cross-fitting and orthogonal-score estimators with explicit data and model objects.", "Package execution does not choose the estimand or verify identifying assumptions."),
    ]
    return [{"source_id": f"source.causal.{sid}", "title": title, "authors_or_publisher": authors, "year": year, "source_kind": kind, "url": url, "bounded_implication": implication, "authority_limit": limit} for sid, title, authors, year, kind, url, implication, limit in rows]


def modules() -> list[dict[str, Any]]:
    rows = [
        ("causal-question", "What intervention contrast, outcome, population, unit and time horizon is the causal question?", "causal question contract", ["what-if", "ich-e9r1"], []),
        ("estimand", "Which population-level or conditional functional is to be identified?", "estimand algebra", ["what-if", "ich-e9r1"], ["causal-question"]),
        ("intervention-semantics", "What treatment strategy or intervention is sufficiently well defined to support counterfactual comparison?", "intervention/strategy model", ["what-if", "pearl-causality"], ["causal-question"]),
        ("potential-outcomes", "Which potential outcomes and consistency relations define the contrast?", "potential-outcome model", ["what-if", "imbens-rubin"], ["estimand", "intervention-semantics"]),
        ("population-time-zero", "How are eligibility, assignment, intervention start, follow-up, censoring and outcome windows aligned?", "target-trial temporal contract", ["what-if", "target-2025"], ["causal-question"]),
        ("protocol", "Which prospective design, analysis, deviation and edition rules govern a study?", "experiment protocol lifecycle", ["consort-2025", "target-2025"], ["causal-question"]),
        ("randomization", "Which allocation mechanism and probabilities create randomized assignment evidence?", "randomization algebra", ["imbens-rubin", "consort-2025"], ["protocol"]),
        ("assignment-state", "What assignment was generated, offered, received and retained at each cut?", "assignment state machine", ["consort-2025", "imbens-rubin"], ["randomization"]),
        ("exposure-adherence", "What intervention exposure, receipt, adherence, contamination and crossover actually occurred?", "exposure occurrence model", ["consort-2025", "ich-e9r1"], ["assignment-state", "intervention-semantics"]),
        ("identification-assumptions", "Which consistency, exchangeability, positivity, interference and selection assumptions connect observed data to the estimand?", "identification obligation set", ["what-if", "interference"], ["potential-outcomes", "population-time-zero"]),
        ("causal-graph", "Which structural variables, arrows, latent common causes and interventions are asserted?", "structural causal graph", ["pearl-causality", "pearl-diagrams"], ["causal-question"]),
        ("graph-identification", "Is the requested causal distribution identifiable from declared graphs and available regimes?", "do-calculus/identification procedure", ["pearl-diagrams", "pearl-causality"], ["causal-graph", "estimand"]),
        ("adjustment-set", "Which pre-treatment covariates form an admissible adjustment set, and which are colliders, mediators or descendants?", "graph/potential-outcome adjustment contract", ["dagitty", "pearl-diagrams"], ["identification-assumptions", "causal-graph"]),
        ("target-trial-emulation", "How is a hypothetical trial protocol mapped to observational data without time-zero or eligibility misalignment?", "observational design mapping", ["what-if", "target-2025"], ["protocol", "population-time-zero", "identification-assumptions"]),
        ("matching-weighting", "How do matching, stratification and propensity weighting target a population while preserving overlap and weight diagnostics?", "design/weighting algebra", ["propensity", "what-if"], ["adjustment-set", "estimand"]),
        ("g-methods", "How are g-formula, IPW, doubly robust and longitudinal g-method estimators selected for the identified estimand?", "g-method estimator family", ["what-if", "msm"], ["identification-assumptions", "estimand"]),
        ("instrumental-variables", "Which instrument assumptions identify which complier-local effect?", "IV/LATE identification model", ["late"], ["estimand", "identification-assumptions"]),
        ("regression-discontinuity", "Which cutoff, running variable, assignment rule and local framework identify a discontinuity effect?", "RDD design model", ["rdd", "rdd-modern"], ["estimand", "identification-assumptions"]),
        ("difference-in-differences", "Which group-time or dose-specific effects are identified by which parallel-trends comparison?", "DiD design/aggregation algebra", ["did-multiple", "did-continuous"], ["estimand", "identification-assumptions"]),
        ("synthetic-control", "Which donor pool and pre-treatment weighting construct a scoped counterfactual trajectory?", "synthetic-control design", ["synthetic-control"], ["estimand", "identification-assumptions"]),
        ("mediation", "Which total, direct, indirect, mediated and interaction effects are requested under which assumptions?", "mediation effect algebra", ["mediation"], ["estimand", "causal-graph"]),
        ("interference", "Which exposure mapping and partial-interference structure allow one unit's assignment to affect another?", "network/spillover potential-outcome model", ["interference"], ["potential-outcomes", "identification-assumptions"]),
        ("heterogeneous-effects", "Which CATE, subgroup, dose-response or policy-relevant heterogeneity functional is being estimated?", "conditional effect model", ["causal-forest", "proximal"], ["estimand", "identification-assumptions"]),
        ("effect-estimation", "Which estimator, nuisance models and sample-splitting scheme compute an identified effect?", "effect estimator contract", ["dml", "doubleml"], ["estimand", "identification-assumptions"]),
        ("uncertainty-inference", "Which sampling design, variance, interval, simultaneous band or identified set bounds the estimate?", "causal uncertainty contract", ["what-if", "did-multiple"], ["effect-estimation"]),
        ("diagnostics-falsification", "Which balance, overlap, placebo, pretrend, manipulation and negative-control findings challenge design assumptions?", "diagnostic evidence algebra", ["dowhy", "rdd-modern", "strobe"], ["identification-assumptions"]),
        ("sensitivity-bounds", "How strong must unmeasured confounding, selection or model misspecification be to alter the conclusion?", "sensitivity/bounding model", ["e-value", "sensemakr"], ["effect-estimation", "identification-assumptions"]),
        ("proximal-identification", "Can treatment- and outcome-inducing proxies identify effects despite latent confounding?", "proximal bridge model", ["proximal", "proximal-regression"], ["identification-assumptions", "heterogeneous-effects"]),
        ("transportability", "Which causal information can move from source studies to a target population under declared invariances?", "selection-diagram transport algebra", ["transport", "data-fusion"], ["estimand", "causal-graph"]),
        ("analysis-cuts-stopping", "Which assignment, exposure, outcome, analysis and interim cuts govern multiplicity and stopping?", "analysis-cut/stopping policy", ["consort-2025", "ich-e9r1"], ["protocol", "assignment-state", "exposure-adherence"]),
        ("result-sealing", "Which estimand, estimator, cuts, assumptions, diagnostics and evidence identity bind a causal result?", "causal result manifest", ["target-2025", "consort-2025"], ["effect-estimation", "uncertainty-inference", "diagnostics-falsification"]),
        ("conclusion-appraisal", "What claim strength survives assumption, sensitivity, multiplicity and scope appraisal?", "claim-evidence appraisal", ["strobe", "target-2025"], ["result-sealing", "sensitivity-bounds"]),
        ("decision-handoff", "How does a scoped causal finding reach a separate accountable decision authority without authorizing action?", "evidence-to-decision ACL", ["what-if", "consort-2025"], ["conclusion-appraisal"]),
        ("causal-discovery-boundary", "How are data-derived graph hypotheses kept separate from assumed, identified and validated causal structures?", "hypothesis boundary", ["pearl-causality", "dagitty"], ["causal-graph"]),
        ("root-cause-boundary", "How are contribution, diagnosis and root-cause hypotheses kept separate from intervention-effect identification?", "diagnostic/causal ACL", ["pearl-causality", "what-if"], ["causal-question", "identification-assumptions"]),
        ("method-composition-facade", "How are identification, estimation, diagnostics and sensitivity kernels composed without acquiring semantic ownership?", "qualified method composition", ["dowhy", "doubleml"], ["graph-identification", "effect-estimation", "diagnostics-falsification", "sensitivity-bounds"]),
    ]
    return [{"module_id": f"module.causal.{mid}", "owned_question": q, "formalism": formalism, "source_refs": [f"source.causal.{s}" for s in refs], "dependency_refs": [f"module.causal.{d}" for d in deps], "status": "EVIDENCE_BACKED_CANDIDATE_OWNER_UNRATIFIED", "completion_claim": False} for mid, q, formalism, refs, deps in rows]


MODULE_MAP = {
    "library.experiment.analysis_binding.compiler": ["estimand", "analysis-cuts-stopping", "effect-estimation", "uncertainty-inference", "method-composition-facade"],
    "library.experiment.analysis_result.sealer": ["result-sealing", "conclusion-appraisal"],
    "library.experiment.conclusion.appraiser": ["conclusion-appraisal", "decision-handoff"],
    "library.experiment.conclusion.lifecycle": ["conclusion-appraisal", "decision-handoff", "result-sealing"],
    "library.experiment.integrity.evaluator": ["diagnostics-falsification", "assignment-state", "exposure-adherence"],
    "library.experiment.integrity.profile.compiler": ["protocol", "diagnostics-falsification"],
    "library.method_kernels.causal_effect_estimators": ["effect-estimation", "g-methods", "instrumental-variables", "regression-discontinuity", "difference-in-differences", "synthetic-control", "heterogeneous-effects", "uncertainty-inference"],
    "library.method_kernels.causal_graph_identification": ["causal-graph", "graph-identification", "adjustment-set", "causal-discovery-boundary"],
    "library.method_kernels.causal_methods": ["method-composition-facade"],
    "library.method_kernels.causal_refutation_sensitivity": ["diagnostics-falsification", "sensitivity-bounds", "root-cause-boundary"],
    "library.method_kernels.experiment_analysis_cut_stopping": ["analysis-cuts-stopping", "protocol"],
    "library.method_kernels.experiment_assignment_state": ["assignment-state", "randomization"],
    "library.method_kernels.experiment_exposure_occurrence": ["exposure-adherence", "intervention-semantics"],
    "library.method_kernels.experiment_protocol_semantics": ["causal-question", "estimand", "protocol", "population-time-zero", "intervention-semantics"],
    "library.method_kernels.experiment_randomization_methods": ["randomization", "assignment-state"],
    "library.predictive.causal_effect_learners": ["heterogeneous-effects", "effect-estimation", "identification-assumptions"],
}


def laws() -> list[dict[str, Any]]:
    rows = [
        ("association-not-causation", "An observed association is not an intervention effect."),
        ("prediction-not-causal-effect", "Predictive accuracy does not identify the effect of changing a treatment."),
        ("estimand-estimator-estimate", "Estimand, estimator and estimate retain separate identities."),
        ("treatment-label-not-intervention", "A column named treatment does not define a well-specified intervention strategy."),
        ("observed-not-potential", "An observed outcome is not the unit's complete set of potential outcomes."),
        ("assignment-not-exposure", "Randomized assignment, offered treatment, receipt, adherence and contamination are distinct."),
        ("randomization-not-analysis", "A valid randomization mechanism does not choose an estimand, estimator, missingness policy or conclusion."),
        ("randomization-not-adherence", "Randomized assignment does not imply treatment receipt or protocol adherence."),
        ("itt-not-per-protocol", "Intention-to-treat, per-protocol, as-treated and treatment-on-treated effects are not interchangeable."),
        ("consistency-not-label", "Consistency and treatment-version assumptions are not implied by equal treatment labels."),
        ("sutva-not-row-shape", "No interference and stable treatment versions must be declared; row-shaped data do not imply them."),
        ("dag-edge-not-mechanism-proof", "An arrow in a causal graph is an assumption or model statement, not observed proof of mechanism."),
        ("discovery-not-identified-graph", "A causal-discovery output is a graph hypothesis, not an identified true causal graph."),
        ("adjustment-not-all-features", "Causal adjustment is not control for every predictive feature."),
        ("post-treatment-control-risk", "Adjusting for a mediator, collider or treatment descendant can create bias."),
        ("balance-not-ignorability", "Observed covariate balance does not prove conditional exchangeability."),
        ("propensity-not-causation", "A propensity score is an assignment probability given observed covariates, not a probability of causation."),
        ("overlap-not-global-positivity", "Empirical overlap in a sample does not prove positivity for every target-population stratum."),
        ("identification-not-estimation", "An estimable numerical procedure cannot repair a nonidentified causal question."),
        ("ate-cate-ite", "ATE, ATT, CATE, local effects and individual effects are distinct functionals."),
        ("subgroup-not-heterogeneity", "Different subgroup point estimates do not by themselves establish treatment-effect heterogeneity."),
        ("iv-relevance-not-validity", "Instrument relevance does not prove exclusion, independence or monotonicity."),
        ("late-not-ate", "A local average treatment effect for compliers is not a population ATE."),
        ("pretrend-not-proof", "Failure to reject pretrend differences does not prove future parallel trends."),
        ("twfe-not-target", "A two-way fixed-effect coefficient need not equal the desired group-time or dose-specific effect."),
        ("rdd-local-not-global", "An RDD discontinuity is local to its cutoff and does not establish a global effect."),
        ("synthetic-fit-not-validity", "Pre-treatment synthetic-control fit does not by itself prove causal validity."),
        ("mediator-not-confounder", "Mediator, confounder, collider, proxy and effect modifier are distinct causal roles."),
        ("mediation-not-attribution", "Causal mediation effects are not predictive feature attribution or responsibility allocation."),
        ("point-not-uncertainty", "A point estimate is not its sampling distribution, interval, identified set or residual uncertainty."),
        ("significance-not-importance", "Statistical significance is not causal magnitude, practical importance, safety or utility."),
        ("absence-significance-not-zero", "Failure to reject a null does not prove zero effect."),
        ("placebo-not-proof", "A passed placebo, falsification or negative-control test does not prove all identifying assumptions."),
        ("sensitivity-not-confounding-absence", "Sensitivity robustness within a declared envelope does not prove absence of unmeasured confounding."),
        ("transport-not-replication", "Transporting an effect requires cross-population invariance assumptions and is not ordinary replication."),
        ("source-not-target-population", "An effect identified in a source population is not automatically the target-population effect."),
        ("root-cause-not-effect", "A diagnostic root-cause hypothesis is not an identified intervention effect."),
        ("attribution-not-responsibility", "Contribution or attribution is not causal responsibility, blame or operational authority."),
        ("causal-finding-not-decision", "A causal estimate or conclusion cannot authorize treatment, allocation, denial or remediation."),
        ("reporting-not-validity", "Compliance with a reporting checklist does not establish design validity or causal truth."),
        ("provider-not-owner", "A software package can implement a method without owning the estimand, assumptions or causal meaning."),
        ("automated-estimator-not-automatic-causality", "Automated nuisance fitting or estimator construction does not automate causal-question definition or identification."),
    ]
    return [{"law_id": f"law.causal.{lid}", "statement": statement, "source_refs": ["source.causal.what-if", "source.causal.pearl-causality"], "status": "EVIDENCE_BACKED_CANDIDATE_OWNER_UNRATIFIED", "completion_claim": False} for lid, statement in rows]


def methods() -> list[dict[str, Any]]:
    rows = [
        ("causal-question-specification", "study_design", "domain intervention question", "typed population/intervention/outcome/contrast/time contract", "requires domain semantic owner"),
        ("target-trial-specification", "study_design", "causal question", "eligibility/strategies/assignment/follow-up/outcome/contrast plan", "design is not execution"),
        ("simple-randomization", "experimental_design", "units and allocation probabilities", "assignment sequence", "randomization is not exposure"),
        ("blocked-randomization", "experimental_design", "units, blocks and ratios", "within-block assignment", "block definition must be pre-specified"),
        ("cluster-randomization", "experimental_design", "clusters and assignment probabilities", "cluster assignment", "cluster effect and interference explicit"),
        ("adaptive-randomization", "experimental_design", "history and adaptation rule", "history-dependent assignment", "adaptation and analysis laws explicit"),
        ("factorial-design", "experimental_design", "multiple intervention factors", "joint assignment design", "interactions and estimands explicit"),
        ("encouragement-design", "experimental_design", "randomized encouragement", "instrument-like assignment", "exclusion/monotonicity not automatic"),
        ("target-trial-emulation", "observational_design", "observational longitudinal data", "trial-aligned analysis cohort", "unmeasured confounding remains possible"),
        ("matching", "observational_design", "treated/control units and covariates", "matched comparison design", "balance not ignorability"),
        ("propensity-stratification", "observational_design", "assignment score and units", "stratified comparison", "score model and overlap explicit"),
        ("inverse-probability-weighting", "estimator", "treatment/censoring probabilities and outcomes", "weighted effect estimate", "positivity and weight stability explicit"),
        ("g-computation", "estimator", "outcome model and intervention distribution", "standardized counterfactual functional", "model and exchangeability assumptions explicit"),
        ("augmented-ipw", "estimator", "outcome and treatment nuisance models", "doubly robust estimate", "double robustness is not assumption-free"),
        ("tmle", "estimator", "initial nuisance estimates and target parameter", "targeted substitution estimate", "target and fluctuation model explicit"),
        ("marginal-structural-model", "longitudinal", "time-varying treatment/confounder history", "marginal regime effect", "sequential exchangeability/positivity explicit"),
        ("structural-nested-model", "longitudinal", "treatment/outcome histories", "blip-effect parameters", "model and identification assumptions explicit"),
        ("instrumental-variables", "quasi_experiment", "instrument/treatment/outcome", "instrument-identified local effect", "relevance is insufficient"),
        ("regression-discontinuity", "quasi_experiment", "running variable/cutoff/treatment/outcome", "local discontinuity effect", "manipulation/continuity tests explicit"),
        ("difference-in-differences", "quasi_experiment", "group-time outcomes/treatment timing", "group-time ATT", "parallel trends and comparison groups explicit"),
        ("continuous-dose-did", "quasi_experiment", "group-time continuous dose", "dose-specific effect/response", "dose comparisons need stronger assumptions"),
        ("event-study", "quasi_experiment", "relative-time panel", "dynamic effect path", "normalization and comparison weights explicit"),
        ("interrupted-time-series", "quasi_experiment", "ordered outcomes and interruption", "level/slope change estimate", "cointerventions/autocorrelation explicit"),
        ("synthetic-control", "quasi_experiment", "treated unit, donor pool, pre-period", "synthetic counterfactual path", "donor eligibility and placebo design explicit"),
        ("causal-graph-identification", "identification", "DAG/SCM and query", "identified functional or refusal", "graph is an assumption"),
        ("backdoor-adjustment", "identification", "causal graph and candidate covariates", "valid adjustment formula/set", "post-treatment/collider controls refused"),
        ("frontdoor-adjustment", "identification", "mediator structure and graph", "frontdoor functional", "all frontdoor conditions explicit"),
        ("do-calculus", "identification", "causal graph and interventional query", "reduced expression or nonidentification witness", "model-class scoped"),
        ("mediation-analysis", "causal_functional", "treatment/mediator/outcome/covariates", "direct/indirect effect", "cross-world or interventional assumptions explicit"),
        ("interference-analysis", "causal_functional", "network/cluster assignments and exposure mapping", "direct/indirect/overall effect", "exposure mapping explicit"),
        ("causal-forest", "heterogeneous_effect", "identified study and covariates", "CATE estimate", "not individual causation"),
        ("uplift-modeling", "heterogeneous_effect", "identified randomized/observational design", "conditional incremental outcome estimate", "predictive uplift still needs identification"),
        ("double-machine-learning", "estimator", "identified score and nuisance learners", "orthogonal cross-fitted estimate", "nuisance ML not identification"),
        ("automatic-debiased-learning", "estimator", "linear functional and nuisance class", "automatically debiased estimate", "automatic estimator not automatic causality"),
        ("proximal-causal-learning", "identification_estimation", "treatment/outcome proxies and bridge assumptions", "proximal effect estimate", "proxy completeness/relevance explicit"),
        ("balance-diagnostics", "diagnostic", "weighted/matched covariates", "balance findings", "not exchangeability proof"),
        ("overlap-diagnostics", "diagnostic", "propensity/weight distributions", "overlap/weight findings", "sample scoped"),
        ("placebo-test", "diagnostic", "placebo outcome/treatment/time", "falsification finding", "passing does not validate all assumptions"),
        ("negative-control", "diagnostic", "negative control exposure/outcome", "confounding/bias finding", "control validity is an assumption"),
        ("pretrend-assessment", "diagnostic", "pre-treatment group-time outcomes", "pretrend evidence", "low power and future trends explicit"),
        ("rdd-manipulation-test", "diagnostic", "running-variable density/covariates", "cutoff manipulation finding", "one test not global validity"),
        ("e-value", "sensitivity", "risk-ratio estimate/interval", "confounding-strength threshold", "does not cover all biases"),
        ("robustness-value", "sensitivity", "linear estimate and partial R2 calibration", "omitted-variable robustness threshold", "model/envelope scoped"),
        ("partial-identification", "sensitivity", "bounded assumptions/data", "identified set", "bounds not point truth"),
        ("transport-formula", "transport", "selection diagram and source/target data", "target-population causal functional", "invariance assumptions explicit"),
        ("causal-data-fusion", "transport", "multiple source regimes/populations", "fused effect estimate", "semantic and mechanism compatibility explicit"),
    ]
    return [{"method_id": f"method.causal.{mid}", "method_class": klass, "input_semantics": inp, "output_semantics": out, "authority_limit": limit, "status": "RESEARCHED_METHOD_BOUNDARY_CANDIDATE"} for mid, klass, inp, out, limit in rows]


def experts() -> list[dict[str, Any]]:
    rows = [
        ("miguel-hernan", "Miguel A. Hernán", ["what-if", "target-2025"], ["Specify the target trial and align eligibility, treatment assignment, time zero and follow-up.", "Treat many causal failures as design and time-alignment failures before estimator failures."]),
        ("james-robins", "James M. Robins", ["what-if", "msm", "dml"], ["Model longitudinal treatment and treatment-affected confounding explicitly.", "Keep g-method identification separate from nuisance prediction."]),
        ("judea-pearl", "Judea Pearl", ["pearl-causality", "pearl-diagrams"], ["Represent intervention and observation with different operators.", "Treat graphs as explicit assumptions and make nonidentification a first-class result."]),
        ("donald-rubin", "Donald B. Rubin", ["imbens-rubin", "propensity"], ["Define potential outcomes and assignment mechanisms before analysis.", "Use design-stage balance without confusing it with unmeasured-confounding proof."]),
        ("guido-imbens", "Guido W. Imbens", ["imbens-rubin", "late"], ["Name the population and local estimand actually identified.", "Use assignment/design credibility to constrain estimator interpretation."]),
        ("susan-athey", "Susan Athey", ["causal-forest"], ["Estimate heterogeneity as a conditional functional with honest inference.", "Do not convert CATE rankings into individual causal truth or policy authority."]),
        ("paul-rosenbaum", "Paul R. Rosenbaum", ["propensity"], ["Separate observational study design from outcome analysis.", "Assess sensitivity because observed balance cannot address hidden bias."]),
        ("tyler-vanderweele", "Tyler J. VanderWeele", ["mediation", "e-value"], ["Separate direct, indirect and interaction effects.", "Report calibrated sensitivity rather than claiming unmeasured confounding is absent."]),
        ("elias-bareinboim", "Elias Bareinboim", ["transport", "data-fusion"], ["Model why source and target populations differ.", "Make transportability an identified formula or refusal, not a vague generalization claim."]),
        ("victor-chernozhukov", "Victor Chernozhukov", ["dml", "auto-dml"], ["Use orthogonal scores and cross-fitting for high-dimensional nuisance estimation.", "Never let flexible prediction replace identification."]),
        ("pedro-santanna", "Pedro H. C. Sant'Anna", ["did-multiple", "did-continuous"], ["Represent staggered adoption as group-time effects before aggregation.", "Expose continuous-dose selection and TWFE interpretation limits."]),
        ("brantly-callaway", "Brantly Callaway", ["did-multiple", "did-continuous"], ["Choose valid comparison groups and explicit aggregation weights.", "Do not treat event-study plots as self-validating designs."]),
        ("alberto-abadie", "Alberto Abadie", ["synthetic-control"], ["Define donor eligibility and pre-treatment fit transparently.", "Use placebo and design evidence without promoting fit to proof."]),
        ("eric-tchetgen", "Eric J. Tchetgen Tchetgen", ["proximal", "proximal-regression"], ["Use proxy variables through explicit bridge and completeness conditions.", "Treat proximal identification as a distinct route, not ordinary covariate adjustment."]),
        ("carlos-cinelli", "Carlos Cinelli", ["sensemakr"], ["Calibrate omitted-variable sensitivity using interpretable partial-R2 scales.", "Report robustness within the chosen envelope rather than declaring causal certainty."]),
        ("elizabeth-halloran", "M. Elizabeth Halloran", ["interference"], ["Define direct, indirect, total and overall effects under interference.", "Do not assume units are isolated when networks, markets or clusters create spillovers."]),
    ]
    return [{"expert_id": f"expert.causal.{eid}", "name": name, "source_refs": [f"source.causal.{s}" for s in refs], "lessons_for_composable_platform": lessons, "authority_limit": "Expert work constrains candidate semantics and methods; the expert is not the SAN semantic owner or a qualification authority.", "status": "RESEARCHED_PROFILE"} for eid, name, refs, lessons in rows]


def innovations() -> list[dict[str, Any]]:
    rows = [
        ("target-reporting", 2025, "TARGET makes target-trial emulation reportable as a causal question, protocol, estimand, identification, data mapping, estimate and sensitivity bundle.", ["target-2025"]),
        ("consort-2025", 2025, "CONSORT 2025 adds updated randomized-trial reporting and open-science obligations while preserving design/analysis/result distinctions.", ["consort-2025"]),
        ("continuous-did", 2024, "Continuous-treatment DiD separates level effects, causal responses, selection across dose and problematic TWFE summaries.", ["did-continuous"]),
        ("proximal-regression", 2025, "Regression-based proximal causal inference makes bridge-based latent-confounding adjustment more operational while retaining its identification conditions.", ["proximal-regression"]),
        ("proximal-cate", 2023, "Proximal causal learning extends proxy-based identification to conditional effect estimation.", ["proximal"]),
        ("causal-data-fusion", 2023, "Direct causal data-fusion methods make heterogeneous source-specific covariates and mechanisms explicit.", ["data-fusion"]),
        ("automatic-dml", 2022, "Automatic debiased learning constructs orthogonal estimators for wider classes of causal/structural functionals without automating identification.", ["auto-dml"]),
        ("modern-rdd", 2022, "Current RDD practice explicitly separates continuity and local-randomization frameworks with distinct validation and falsification procedures.", ["rdd-modern"]),
    ]
    return [{"innovation_id": f"innovation.causal.{iid}", "year": year, "innovation": text, "source_refs": [f"source.causal.{s}" for s in refs], "ai_or_llm_dependency": False, "boundary_implication": "Encode as an optional method/design/evidence module with assumptions and refusals; do not create an ambient AI product or silently widen causal claims.", "status": "EVIDENCE_BACKED_NON_AI_INNOVATION"} for iid, year, text, refs in rows]


AXIS_QUESTIONS = {
    "semantic_object": "Which causal question, intervention, potential outcome, assignment, exposure, estimand, graph, estimate, diagnostic, sensitivity result, conclusion or handoff is this library about?",
    "semantic_role": "Which roles are treatment, outcome, confounder, mediator, collider, instrument, modifier, proxy, unit, population, source/target domain, estimator, appraiser and decision authority?",
    "identity_and_equality": "What makes protocol, intervention version, assignment, exposure, study cut, estimand, graph, estimator, estimate, evidence and conclusion editions equal or distinct?",
    "grain_and_cardinality": "Are effects defined per unit, cluster, edge, group-time, dose, population, intervention strategy, study or target domain, and what interference/cardinality applies?",
    "state_and_change": "What are the legal draft, specified, assigned, exposed, analyzed, sealed, appraised, published, superseded, retracted and invalidated transitions?",
    "time": "How are eligibility, assignment, time zero, exposure, follow-up, censoring, outcome, recording, analysis cut, decision and transport-validity time distinguished?",
    "order_and_topology": "Which causal DAG, temporal order, treatment history, network interference, donor pool, cutoff or group-time topology constrains identification?",
    "partiality_and_uncertainty": "How are nonidentification, missingness, censoring, positivity failure, latent confounding, model misspecification, intervals, bounds and unresolved assumptions represented?",
    "authority_and_trust": "Who defines the question, intervention, estimand, assumptions, protocol, stopping, claim strength, release, retraction and decision use?",
    "effect_boundary": "How are pure causal specification/identification/estimation/appraisal separated from random assignment, intervention delivery, publication and enterprise action?",
    "representation": "Which table, longitudinal panel, graph, protocol, assignment log, exposure record, model artifact, result manifest and evidence carrier is used, at what edition and mapping loss?",
    "composition_algebra": "How do question, design, identification, estimator, diagnostics, sensitivity, transport, result and decision-handoff modules compose and propagate refusals?",
    "compatibility_and_evolution": "What changes preserve protocol, treatment version, estimand, assumptions, graph, data mapping, estimator, result and conclusion comparability, and what forces reanalysis?",
    "resources_and_failure": "What finite randomization, optimization, resampling, graph search, bootstrap, simulation and sensitivity budgets apply, and when must analysis refuse?",
    "evidence_and_conformance": "Which design fixtures, randomization checks, overlap/balance tests, negative controls, placebos, sensitivity envelopes, simulations and independent implementations support each bounded claim?",
    "privacy_security_safety": "What participant/unit privacy, treatment leakage, manipulation, selective reporting, harmful subgroup claims and unauthorized interventions must be prevented?",
}


def boundary_findings(products_by_library: dict[str, set[str]]) -> list[dict[str, Any]]:
    unconsumed = sorted(ref for ref in LIBRARIES if not products_by_library[ref])
    return [
        {"finding_id": "finding.causal.experiment-product-retain.v1", "library_refs": sorted(ref for ref in LIBRARIES if products_by_library[ref]), "current_product_refs": ["product.experimentation_platform"], "candidate_disposition": "RETAIN_EXPERIMENTATION_PRODUCT_WITH_NARROW_CAUSAL_HANDOFF", "reason": "Protocol, assignment, exposure, integrity, cuts, result sealing and conclusion lifecycle form an operationally coherent experimentation product; imported causal estimators do not own that lifecycle.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.causal.causal-toolkit-not-yet-product.v1", "library_refs": ["library.method_kernels.causal_graph_identification", "library.method_kernels.causal_effect_estimators", "library.method_kernels.causal_refutation_sensitivity", "library.method_kernels.causal_methods"], "current_product_refs": [], "candidate_disposition": "RETAIN_AS_COMPOSABLE_CAUSAL_STUDY_LIBRARIES_PRODUCT_BOUNDARY_UNPROVEN", "reason": "The captured graph proves method/library seams but no independent users, operations, SLO, lifecycle, adoption or exit boundary for a standalone causal platform.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.causal.predictive-learner-migration.v1", "library_refs": ["library.predictive.causal_effect_learners"], "current_product_refs": [], "candidate_disposition": "MOVE_SEMANTIC_OWNERSHIP_FROM_PREDICTIVE_TO_CAUSAL_HETEROGENEOUS_EFFECTS", "reason": "A treatment-effect learner requires a causal estimand and identification contract; predictive model-family semantics may supply nuisance learners but cannot own the effect.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.causal.randomization-seam.v1", "library_refs": ["library.method_kernels.experiment_randomization_methods", "library.method_kernels.experiment_assignment_state", "library.method_kernels.experiment_exposure_occurrence"], "current_product_refs": ["product.experimentation_platform"], "candidate_disposition": "PUBLISHED_LANGUAGE_RANDOMIZATION_EVIDENCE_TO_CAUSAL_IDENTIFICATION", "reason": "Randomization supplies assignment-mechanism evidence, while exposure/adherence and estimand policy remain separately bound.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.causal.method-facade-narrow.v1", "library_refs": ["library.method_kernels.causal_methods"], "current_product_refs": [], "candidate_disposition": "COMPOSITION_FACADE_ONLY_NO_CAUSAL_SEMANTIC_OWNERSHIP", "reason": "A generic causal-method facade may route qualified identification, estimation and sensitivity kernels but must not choose the question, graph, assumptions or claim strength.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.causal.root-cause-acl.v1", "library_refs": ["library.method_kernels.causal_refutation_sensitivity"], "current_product_refs": [], "candidate_disposition": "KEEP_CAUSAL_REFUTATION_SEPARATE_FROM_DIAGNOSTIC_ROOT_CAUSE", "reason": "Causal sensitivity and falsification challenge a specified effect analysis; signal/process root-cause diagnostics generate different kinds of hypotheses and evidence.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.causal.decision-authority.v1", "library_refs": ["library.experiment.conclusion.appraiser", "library.experiment.conclusion.lifecycle"], "current_product_refs": ["product.experimentation_platform"], "candidate_disposition": "RETAIN_EVIDENCE_HANDOFF_EFFECT_AUTHORITY_OUTSIDE", "reason": "Conclusion appraisal may bound claim strength and publication state but cannot authorize treatment, rollout, denial, remediation or policy action.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.causal.unconsumed.v1", "library_refs": unconsumed, "current_product_refs": [], "candidate_disposition": "EXPLICIT_ASSEMBLY_OWNERSHIP_REVIEW_REQUIRED", "reason": "Five exact causal libraries have no declared product consumer in the captured graph; absence is recorded without inferring non-use or inventing a product.", "owner_decision": "UNRATIFIED"},
    ]


def build() -> dict[str, Any]:
    source_rows, module_rows, law_rows = sources(), modules(), laws()
    method_rows, expert_rows, innovation_rows = methods(), experts(), innovations()
    contributions = {row["library_id"]: row for row in load_jsonl(REGISTRY / "library-contributions.jsonl")}
    coordinate_dockets = {row["library_ref"]: row for row in load_jsonl(SEM / "library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact_dockets = {row["library_ref"]: row for row in load_jsonl(SEM / "p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    products_by_library = {ref: set() for ref in LIBRARIES}
    subjects_by_library = {ref: set() for ref in LIBRARIES}
    for subject in load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl"):
        for edge in subject["concrete_bindings"]:
            ref = edge["concrete_library_ref"]
            if ref in products_by_library:
                products_by_library[ref].add(subject["product_ref"])
                subjects_by_library[ref].add(subject["subject_ref"])
    target_occurrences = {(row["axis"], row["library_ref"]): row for row in load_jsonl(SEM / "targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    module_by_id = {row["module_id"]: row for row in module_rows}
    library_rows, axis_rows = [], []
    for ref in LIBRARIES:
        mods = [f"module.causal.{x}" for x in MODULE_MAP[ref]]
        evidence = sorted({src for mod in mods for src in module_by_id[mod]["source_refs"]})
        if ref == "library.predictive.causal_effect_learners": disposition = "MOVE_SEMANTIC_OWNERSHIP_TO_CAUSAL_HETEROGENEOUS_EFFECTS"
        elif ref == "library.method_kernels.causal_methods": disposition = "COMPOSITION_FACADE_ONLY_NO_SEMANTIC_OWNERSHIP"
        else: disposition = "RETAIN_NARROW_MODULE_BOUNDARY"
        library_rows.append({"record_kind": "causal_inference_library_semantic_binding_candidate", "binding_id": f"binding.causal-semantic-slice.{slug(ref)}.v1", "library_ref": ref, "library_name": contributions[ref]["name"], "semantic_module_refs": mods, "evidence_refs": evidence, "exact_contract_docket_ref": exact_dockets[ref]["docket_id"], "coordinate_binding_docket_ref": coordinate_dockets[ref]["binding_docket_id"], "downstream_subject_refs": sorted(subjects_by_library[ref]), "downstream_product_refs": sorted(products_by_library[ref]), "boundary_disposition_candidate": disposition, "compiler_binding": "REFUSED", "refusal_reasons": ["OWNER_RATIFICATION_MISSING", "MEMBER_AXIS_APPLICABILITY_UNRATIFIED", "EXACT_CONTRACT_UNSELECTED", "IMPLEMENTATIONS_UNQUALIFIED"], "completion_claim": False})
        for axis in AXES:
            targeted = target_occurrences.get((axis, ref))
            axis_rows.append({"record_kind": "causal_inference_library_axis_decision_candidate", "decision_candidate_id": f"decision-candidate.causal-axis.{slug(ref)}.{axis.replace('_', '-')}.v1", "library_ref": ref, "axis": axis, "semantic_module_refs": mods, "coordinate_question": AXIS_QUESTIONS[axis], "applicability_candidate": "REQUIRED_EXPLICIT_PROFILE", "evidence_refs": evidence, "targeted_member_adjudication_occurrence_ref": targeted["occurrence_id"] if targeted else None, "coordinate_answers": [], "member_applicability": "PROPOSED_OWNER_REVIEW_REQUIRED", "owner_decision": "UNRATIFIED", "status": "EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER", "canonical_gaps_closed": 0, "completion_claim": False})
    findings = boundary_findings(products_by_library)
    context = {"record_kind": "bounded_context_candidate", "context_id": "context.causal-inference-semantic-slice.v1", "as_of": AS_OF, "vision": "How can a declared intervention contrast be designed, identified, estimated, challenged and transported without collapsing association into causation, assignment into exposure, graph assumptions into truth, sensitivity into proof or a causal finding into a decision?", "inside": ["causal questions, interventions, potential outcomes and estimands", "randomized and observational study-design semantics", "assignment, exposure, adherence and analysis cuts", "graphical and potential-outcome identification", "effect estimators and uncertainty", "quasi-experimental and longitudinal designs", "diagnostics, falsification, sensitivity and partial identification", "heterogeneous effects, mediation, interference and transportability", "result sealing, conclusion appraisal and evidence handoff"], "outside": ["domain authority to choose interventions, outcomes and acceptable harms", "physical intervention delivery", "generic predictive model-family ownership", "causal discovery as truth generation", "signal/process root-cause diagnosis", "enterprise action or policy authorization", "generic storage, compute and orchestration", "LLM/agent orchestration"], "neighbors": [{"context_ref": "context.experiment-lifecycle", "relationship": "customer_supplier"}, {"context_ref": "context.predictive-analytics-semantic-slice", "relationship": "anti_corruption_layer"}, {"context_ref": "context.process-analytics-semantic-slice", "relationship": "anti_corruption_layer"}, {"context_ref": "context.domain-decision-authority", "relationship": "anti_corruption_layer"}, {"context_ref": "context.runtime-resource-control", "relationship": "customer_supplier"}], "published_language": ["CausalQuestion", "InterventionStrategy", "PotentialOutcomeModel", "Estimand", "AssignmentMechanism", "AssignmentOccurrence", "ExposureOccurrence", "IdentificationAssumption", "CausalGraph", "IdentifiedFunctional", "EffectEstimatorBinding", "CausalEstimate", "DiagnosticFinding", "SensitivityResult", "TransportFormula", "CausalResultManifest", "ConclusionAppraisal", "DecisionEvidenceHandoff"], "ratification": "WITHHELD", "completion_claim": False}
    summary = {"program_id": "program.causal-inference-semantic-slice.v1", "as_of": AS_OF, "primary_or_official_sources": len(source_rows), "semantic_modules": len(module_rows), "non_collapse_laws": len(law_rows), "method_types": len(method_rows), "expert_learning_profiles": len(expert_rows), "recent_non_llm_innovations": len(innovation_rows), "bound_libraries": len(library_rows), "library_axis_decision_candidates": len(axis_rows), "product_capability_boundary_findings": len(findings), "downstream_products": len({p for vals in products_by_library.values() for p in vals}), "libraries_without_declared_product_consumer": sum(not vals for vals in products_by_library.values()), "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0, "canonical_gaps_closed": 0, "completion_claim": False}
    return {"context": context, "sources": source_rows, "modules": module_rows, "laws": law_rows, "methods": method_rows, "experts": expert_rows, "innovations": innovation_rows, "libraries": library_rows, "axes": axis_rows, "findings": findings, "summary": summary}


def outputs() -> dict[str, str]:
    b = build()
    files = {
        "bounded-context.json": json.dumps(b["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(x) + "\n" for x in b["sources"]),
        "semantic-modules.jsonl": "".join(canonical(x) + "\n" for x in b["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(x) + "\n" for x in b["laws"]),
        "causal-method-taxonomy.jsonl": "".join(canonical(x) + "\n" for x in b["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(x) + "\n" for x in b["experts"]),
        "innovation-records.jsonl": "".join(canonical(x) + "\n" for x in b["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(x) + "\n" for x in b["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(x) + "\n" for x in b["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(x) + "\n" for x in b["findings"]),
        "summary.json": json.dumps(b["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.causal-inference-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    s = build()["summary"]
    print(f"BUILD PASS causal inference semantic slice: {s['semantic_modules']} modules, {s['method_types']} methods, {s['bound_libraries']} libraries and {s['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
