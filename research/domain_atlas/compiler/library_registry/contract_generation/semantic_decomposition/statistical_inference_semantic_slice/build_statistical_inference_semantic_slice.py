#!/usr/bin/env python3
"""Build the evidence-backed general statistical inference semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
AS_OF = "2026-08-27"
PRODUCT = "product.analytical_notebook"
AXES = ["semantic_object","semantic_role","identity_and_equality","grain_and_cardinality","state_and_change","time","order_and_topology","partiality_and_uncertainty","authority_and_trust","effect_boundary","representation","composition_algebra","compatibility_and_evolution","resources_and_failure","evidence_and_conformance","privacy_security_safety"]
NEIGHBORS = {
    "library.cbv.uncertainty_contracts",
    "library.csp.quantity.partial-information",
    "library.csp.quantity.probability-core",
    "library.csp.quantity.scale-types",
    "library.csp.quantity.uncertainty-propagation",
    "library.lpe.prov-statement-algebra",
    "library.lpe.provenance-assertion",
    "library.method_kernels.analysis_design",
    "library.method_kernels.analytical_finding_contract",
    "library.method_kernels.artifact_envelope",
    "library.method_kernels.descriptive_statistics",
    "library.method_kernels.inferential_tests_resampling",
    "library.method_kernels.method_contracts",
    "library.method_kernels.numerical_kernel_facade",
    "library.method_kernels.probabilistic_inference",
    "library.method_kernels.probability_distribution_algebra",
    "library.method_kernels.regression_glm_estimators",
    "library.method_kernels.result_algebra",
    "library.method_kernels.statistical_estimators",
    "library.pipeline.data_cut_algebra",
    "library.smf.missingness_algebra",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def product_rows() -> list[dict[str, Any]]:
    return load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")


def library_universe() -> list[str]:
    direct = {edge["concrete_library_ref"] for row in product_rows() if row["product_ref"] == PRODUCT for edge in row["concrete_bindings"]}
    return sorted(direct | NEIGHBORS)


LIBRARIES = library_universe()


def sources() -> list[dict[str, Any]]:
    rows = [
        ("nist-handbook", "NIST/SEMATECH e-Handbook of Statistical Methods", ["National Institute of Standards and Technology", "SEMATECH"], 2012, "official_statistical_handbook", "https://www.itl.nist.gov/div898/handbook/", "Provides a broad engineering-statistics frame spanning exploration, measurement, modeling, design, comparison, control and reliability.", "It is method guidance, not a universal analysis plan or domain decision authority."),
        ("nist-eda", "NIST/SEMATECH Exploratory Data Analysis", ["James J. Filliben", "Alan Heckert"], 2012, "official_statistical_guidance", "https://itl.nist.gov/div898/handbook/eda/eda.htm", "Separates exploratory inquiry and graphical assumption checking from passive summary reduction.", "Exploration can generate hypotheses but does not by itself support confirmatory error guarantees."),
        ("nist-model", "NIST/SEMATECH Process Modeling", ["William Guthrie", "James J. Filliben", "Alan Heckert"], 2012, "official_modeling_guidance", "https://www.itl.nist.gov/div898/handbook/pmd/pmd.htm", "Makes model design, fitting, diagnostics, validation, improvement and intended use separate steps.", "A fitted model is not automatically adequate, predictive, causal or fit for a decision."),
        ("asa-pvalue", "ASA Statement on Statistical Significance and P-Values", ["American Statistical Association"], 2016, "professional_society_statement", "https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf", "Bounds p-values as model-conditional incompatibility measures and separates them from effect size, importance and truth.", "The statement does not prescribe one universal inferential school or decision threshold."),
        ("asa-2021", "ASA President's Task Force Statement on Statistical Significance and Replicability", ["American Statistical Association President's Task Force"], 2021, "professional_society_statement", "https://doi.org/10.1214/21-AOAS1501", "Reaffirms that sound inference requires design, transparency, uncertainty, context and cumulative evidence rather than threshold ritual.", "It does not make a statistical result a replication, policy decision or operational authorization."),
        ("ich-e9", "ICH E9 — Statistical Principles for Clinical Trials", ["International Council for Harmonisation"], 1998, "international_regulatory_guideline", "https://database.ich.org/sites/default/files/E9_Guideline.pdf", "Separates trial objectives, design, analysis sets, statistical principles and reporting.", "Its regulatory scope does not make every enterprise analysis a clinical trial."),
        ("ich-e9r1", "ICH E9(R1) — Estimands and Sensitivity Analysis", ["International Council for Harmonisation"], 2019, "international_regulatory_guideline", "https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf", "Separates the clinical question/estimand, estimator, estimate, intercurrent-event strategy and sensitivity analysis.", "The five clinical estimand attributes require domain-specific generalization outside trials."),
        ("census-sample", "Census Statistical Quality Standard A3 — Sample Design", ["United States Census Bureau"], 2022, "official_statistical_standard", "https://www.census.gov/about/policies/quality/standards/standarda3.html", "Requires target population, frame, selection design, probabilities, strata, clusters, weights and variance artifacts to remain explicit.", "A probability sample does not remove coverage, nonresponse, measurement or processing error."),
        ("census-analyze", "Census Statistical Quality Standard E1 — Analyzing Data", ["United States Census Bureau"], 2022, "official_statistical_standard", "https://www.census.gov/about/policies/quality/standards/standarde1.html", "Requires analysis to account for the actual sample design and estimation methodology.", "Unweighted or independence assumptions cannot be inferred from a rectangular table."),
        ("census-report", "Census Statistical Quality Standard E2 — Reporting Results", ["United States Census Bureau"], 2022, "official_statistical_standard", "https://www.census.gov/about/policies/quality/standards/standarde2.html", "Requires weighted estimates and measures of statistical uncertainty for applicable releases.", "A reported margin of error does not cover every nonsampling bias or domain risk."),
        ("rubin-missing", "Inference and Missing Data", ["Donald B. Rubin"], 1976, "peer_reviewed_primary_method", "https://doi.org/10.1093/biomet/63.3.581", "Formalizes missing-data mechanisms and conditions under which the observation process may be ignored.", "A missingness label is an assumption about a joint data/response process, not an observable fact inferred from null cells."),
        ("efron-bootstrap", "Bootstrap Methods: Another Look at the Jackknife", ["Bradley Efron"], 1979, "peer_reviewed_primary_method", "https://doi.org/10.1214/aos/1176344552", "Defines bootstrap estimation of a statistic's sampling distribution from an empirical distribution.", "Bootstrap validity depends on the sampling structure, statistic and resampling scheme; rows are not always exchangeable."),
        ("huber-robust", "Robust Estimation of a Location Parameter", ["Peter J. Huber"], 1964, "peer_reviewed_primary_method", "https://doi.org/10.1214/aoms/1177703732", "Establishes robustness as performance under bounded model contamination rather than an informal synonym for stability.", "Robustness is relative to a contamination/neighborhood model, loss and target."),
        ("bh-fdr", "Controlling the False Discovery Rate", ["Yoav Benjamini", "Yosef Hochberg"], 1995, "peer_reviewed_primary_method", "https://doi.org/10.1111/j.2517-6161.1995.tb02031.x", "Defines false-discovery-rate control as distinct from family-wise error control under stated dependence conditions.", "An adjusted value does not define the hypothesis family, scientific importance or decision consequences."),
        ("fda-multiplicity", "Multiple Endpoints in Clinical Trials", ["United States Food and Drug Administration"], 2022, "official_regulatory_guidance", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/multiple-endpoints-clinical-trials", "Requires endpoint families, ordering and error-control strategy to be explicit when multiple claims are tested.", "Its acceptable strategies are context-specific and do not authorize automatic correction across unrelated questions."),
        ("nasem-repro", "Reproducibility and Replicability in Science", ["National Academies of Sciences, Engineering, and Medicine"], 2019, "consensus_study_report", "https://doi.org/10.17226/25303", "Separates computational reproducibility, replication with new data and generalizability to other populations or contexts.", "Re-execution success does not establish correctness, replication or generalization."),
        ("cochrane-meta", "Cochrane Handbook Chapter 10 — Meta-analysis", ["Jonathan Deeks", "Julian Higgins", "Douglas Altman", "Joanne McKenzie", "Areti Veroniki"], 2024, "authoritative_method_handbook", "https://training.cochrane.org/handbook/current/chapter-10", "Separates study estimates, effect measures, fixed/common-effect and random-effects targets, heterogeneity and sensitivity.", "Pooling can mislead when designs, estimands, bias or effect measures are incompatible."),
        ("cochrane-effects", "Cochrane Handbook Chapter 6 — Effect Measures", ["Julian Higgins", "Tianjing Li", "Jonathan Deeks"], 2023, "authoritative_method_handbook", "https://training.cochrane.org/handbook/current/chapter-06", "Separates outcome data types and non-equivalent effect measures such as risks, odds, differences and ratios.", "Numeric convertibility does not make effect measures or estimands semantically interchangeable."),
        ("gum", "JCGM 100:2008 — Evaluation of Measurement Data", ["Joint Committee for Guides in Metrology"], 2008, "measurement_uncertainty_guide", "https://doi.org/10.59161/JCGM100-2008E", "Defines model-based propagation of measurement uncertainty, covariance and coverage.", "Measurement uncertainty is not sampling error, posterior uncertainty or decision risk."),
        ("gum1", "JCGM GUM-1:2023 — Introduction", ["Joint Committee for Guides in Metrology"], 2023, "current_measurement_uncertainty_guide", "https://doi.org/10.59161/JCGMGUM-1-2023", "Refreshes the conceptual foundation for measurement uncertainty and models.", "It does not replace statistical design or domain-specific uncertainty models."),
        ("r-stats", "The R Stats Package", ["R Core Team"], 2026, "official_method_provider", "https://stat.ethz.ch/R-manual/R-devel/library/stats/html/stats-package.html", "Implements distributions, estimation, tests, regression, smoothing, time series and random generation under explicit functions.", "Function availability and defaults do not own estimands, assumptions or claim strength."),
        ("scipy-stats", "SciPy Statistical Functions", ["SciPy project"], 2026, "official_method_provider", "https://docs.scipy.org/doc/scipy/reference/stats.html", "Implements distributions, descriptive statistics, tests, resampling, confidence intervals, FDR and related methods.", "Tests grouped under one API are not interchangeable and stochastic methods require explicit RNG/budget semantics."),
        ("statsmodels", "Statsmodels User Guide", ["statsmodels project"], 2026, "official_method_provider", "https://www.statsmodels.org/stable/user-guide.html", "Implements statistical models, estimation, results, diagnostics and tests.", "A fitted provider result does not establish model adequacy or a valid scientific claim."),
        ("stan", "Stan Reference Manual 2.39", ["Stan Development Team"], 2025, "official_probabilistic_programming_specification", "https://mc-stan.org/docs/reference-manual/", "Specifies probability programs, transforms, inference algorithms, diagnostics and reproducibility controls.", "A posterior is conditional on the model, data, prior and computational adequacy; sampling completion is not convergence proof."),
        ("stan-ppc", "Stan User's Guide — Predictive Checks", ["Stan Development Team"], 2025, "official_model_checking_guidance", "https://mc-stan.org/docs/stan-users-guide/posterior-predictive-checks.html", "Uses replicated data to check whether a model captures selected aspects of observed data.", "Passing selected predictive checks does not prove the model true or adequate for every use."),
        ("vehtari-rhat", "Rank-Normalization, Folding, and Localization: An Improved R-hat", ["Aki Vehtari", "Andrew Gelman", "Daniel Simpson", "Bob Carpenter", "Paul-Christian Bürkner"], 2021, "peer_reviewed_primary_method", "https://doi.org/10.1214/20-BA1221", "Improves MCMC convergence diagnostics with rank normalization, folding and localized effective sample size.", "A diagnostic threshold is necessary evidence, not proof of posterior accuracy or model adequacy."),
        ("rap", "Reproducible Analytical Pipelines Strategy", ["United Kingdom Government Analysis Function"], 2022, "official_analysis_delivery_standard", "https://analysisfunction.civilservice.gov.uk/policy-store/reproducible-analytical-pipelines-strategy/", "Requires analysis-as-code, versioning, peer review, tests, dependency management, logging and minimized manual steps.", "Pipeline reproducibility does not establish inferential validity, source quality or replication."),
        ("asa-safe", "Game-Theoretic Statistics and Safe Anytime-Valid Inference", ["Aaditya Ramdas", "Peter Grünwald", "Vladimir Vovk", "Glenn Shafer"], 2023, "peer_reviewed_research_synthesis", "https://doi.org/10.1214/23-STS894", "Develops e-processes and confidence sequences whose guarantees survive optional stopping under stated protocols.", "Anytime-valid evidence remains model/protocol conditional and is not a generic authorization to monitor or act."),
        ("jupyter-format", "Jupyter Notebook Format", ["Jupyter project"], 2025, "official_interchange_specification", "https://nbformat.readthedocs.io/en/latest/format_description.html", "Defines notebook cells, outputs, metadata and serialization.", "Notebook order and stored output do not prove execution order, environment identity or reproducibility."),
        ("jupyter-security", "Jupyter Notebook Security", ["Jupyter project"], 2025, "official_security_specification", "https://jupyter-notebook.readthedocs.io/en/stable/security.html", "Separates trusted signatures from untrusted stored outputs and active content.", "A trusted notebook signature establishes a local trust decision, not statistical correctness."),
    ]
    return [{"source_id": f"source.statistics.{sid}", "title": title, "authors_or_publisher": authors, "year": year, "source_kind": kind, "url": url, "bounded_implication": implication, "authority_limit": limit} for sid, title, authors, year, kind, url, implication, limit in rows]


MODULE_ROWS = [
    ("question-purpose", "What bounded descriptive, predictive, inferential or decision-support question is being asked?", "analysis intent", ["nist-handbook", "nasem-repro"], []),
    ("target-population", "Which finite or conceptual population, domain and eligibility conditions are targeted?", "population specification", ["census-sample", "ich-e9r1"], ["question-purpose"]),
    ("observational-unit", "What unit is sampled, observed, measured, clustered, repeated or analyzed?", "unit/grain model", ["census-sample", "cochrane-effects"], ["target-population"]),
    ("sampling-frame", "Which frame occurrence covers the target population with what omissions and duplicates?", "sampling-frame relation", ["census-sample"], ["target-population", "observational-unit"]),
    ("sampling-design", "Which probability/nonprobability selection, strata, clusters and inclusion probabilities generated the sample?", "sample-design algebra", ["census-sample"], ["sampling-frame"]),
    ("analysis-population", "Which observed, eligible and analysis-set occurrences are included, excluded or weighted?", "analysis-set projection", ["ich-e9", "census-analyze"], ["sampling-design"]),
    ("estimand", "Which population-level quantity answers the question under explicit conditions and events?", "estimand contract", ["ich-e9r1", "cochrane-effects"], ["question-purpose", "target-population"]),
    ("analysis-specification", "Which design, estimator, assumptions, transformations, diagnostics, multiplicity and sensitivity analyses were fixed when?", "editioned analysis protocol", ["ich-e9r1", "nasem-repro"], ["estimand", "analysis-population"]),
    ("data-cut", "Which immutable data occurrence, validity/recording cut and exclusions feed the analysis?", "input-cut algebra", ["nasem-repro", "rap"], ["analysis-specification"]),
    ("variable-role", "Which variables are outcome, exposure/treatment, predictor, covariate, stratum, cluster, weight, offset, censoring or identifier roles?", "variable-role typing", ["nist-model", "ich-e9r1"], ["data-cut"]),
    ("measurement-scale", "Which categorical, ordinal, count, rate, continuous, bounded, compositional or event-time scale constrains operations?", "scale/type algebra", ["cochrane-effects", "nist-eda"], ["variable-role"]),
    ("missingness-mechanism", "Which values are structurally absent, unobserved, invalid or censored under what observation mechanism?", "missing-data model", ["rubin-missing"], ["data-cut", "variable-role"]),
    ("survey-weight", "Which base, nonresponse, calibration and replicate weights attach to which sample edition?", "weighting relation", ["census-sample", "census-analyze"], ["sampling-design"]),
    ("probability-space", "Which sample space, sigma-algebra and probability measure make random variables and events meaningful?", "probability algebra", ["r-stats", "stan"], ["question-purpose"]),
    ("distribution-family", "Which univariate/multivariate distribution, parameters, support and measure define probability operations?", "distribution algebra", ["r-stats", "scipy-stats"], ["probability-space"]),
    ("randomness-stream", "Which algorithm, seed/key, substream and consumption order govern simulation/resampling?", "random-stream contract", ["scipy-stats", "stan"], ["probability-space"]),
    ("descriptive-summary", "Which count, center, spread, quantile, shape, frequency or robust summary describes the captured occurrence?", "descriptive reducer", ["nist-eda", "scipy-stats"], ["measurement-scale"]),
    ("exploratory-analysis", "Which plots, transformations, stratifications and assumption probes were explored without confirmatory guarantees?", "exploration protocol", ["nist-eda", "asa-pvalue"], ["descriptive-summary"]),
    ("estimator", "Which rule maps the specified sample occurrence to an estimate of the estimand?", "estimator algebra", ["ich-e9r1", "nist-model"], ["estimand", "analysis-population"]),
    ("sampling-distribution", "Which repeated-sampling distribution and design/model assumptions support standard errors and coverage?", "sampling-distribution model", ["efron-bootstrap", "census-analyze"], ["sampling-design", "estimator"]),
    ("interval-estimate", "Which confidence, compatibility, credible, prediction or tolerance interval targets what quantity at what level?", "interval result algebra", ["asa-pvalue", "stan", "gum"], ["estimator"]),
    ("resampling", "Which bootstrap, jackknife, permutation or Monte Carlo resampling unit and scheme approximates which target distribution?", "resampling protocol", ["efron-bootstrap", "scipy-stats"], ["sampling-design", "randomness-stream"]),
    ("hypothesis-model", "Which null/alternative model family, test statistic and rejection/evidence rule define a test?", "test contract", ["asa-pvalue", "scipy-stats"], ["probability-space", "analysis-specification"]),
    ("p-value", "Which tail/event under the specified model defines incompatibility of data at least as extreme as observed?", "model-conditional result", ["asa-pvalue"], ["hypothesis-model"]),
    ("error-power", "Which type-I/type-II, power, severity or long-run decision guarantees apply under which alternatives?", "repeated-sampling operating characteristic", ["asa-2021", "ich-e9"], ["hypothesis-model"]),
    ("multiplicity-family", "Which hypotheses/looks/endpoints form one error-controlled family and why?", "claim-family contract", ["bh-fdr", "fda-multiplicity"], ["analysis-specification", "hypothesis-model"]),
    ("sequential-monitoring", "Which filtration, look schedule, stopping rule and anytime-valid evidence process govern accumulating data?", "sequential evidence protocol", ["asa-safe"], ["analysis-specification", "randomness-stream"]),
    ("regression-model", "Which response distribution, link, systematic component, offsets, interactions and dependence structure form a model?", "regression/GLM model", ["nist-model", "statsmodels"], ["variable-role", "distribution-family"]),
    ("model-fit", "Which optimization/estimating/inference method and convergence criteria produce a fitted occurrence?", "fit execution contract", ["statsmodels", "stan"], ["regression-model", "estimator"]),
    ("model-diagnostics", "Which residual, influence, calibration, posterior predictive and computational checks probe selected failure modes?", "diagnostic evidence", ["nist-model", "stan-ppc", "vehtari-rhat"], ["model-fit"]),
    ("model-selection", "Which candidate universe, loss/information criterion, validation scheme and selection correction choose a model?", "selection protocol", ["nist-model", "nasem-repro"], ["analysis-specification", "model-diagnostics"]),
    ("robustness", "Which contamination/neighborhood, perturbation or specification changes leave which estimand/result acceptably stable?", "robustness relation", ["huber-robust", "ich-e9r1"], ["estimator"]),
    ("sensitivity-analysis", "Which unverifiable assumptions or intercurrent/missing-data strategies are varied, with what result comparison?", "sensitivity protocol", ["ich-e9r1", "rubin-missing"], ["analysis-specification", "robustness"]),
    ("probabilistic-inference", "Which prior, likelihood, posterior target, approximation algorithm and diagnostics define Bayesian/probabilistic inference?", "probabilistic-program contract", ["stan", "stan-ppc"], ["probability-space", "estimand"]),
    ("meta-analysis", "Which study estimands/effect measures are commensurable and how are weights and heterogeneity modeled?", "evidence-synthesis model", ["cochrane-meta", "cochrane-effects"], ["estimand", "interval-estimate"]),
    ("finding-claim", "Which bounded claim follows from which estimate, assumptions, diagnostics and authority, with what caveats?", "analytical finding", ["asa-2021", "nasem-repro"], ["interval-estimate", "model-diagnostics", "sensitivity-analysis"]),
    ("reproducibility", "Which data, code, method, configuration, environment and randomness identities permit computational re-execution?", "reproducibility evidence", ["nasem-repro", "rap"], ["analysis-specification", "data-cut", "randomness-stream"]),
    ("replicability", "Which independent study with new data addresses the same question and how is consistency appraised?", "replication relation", ["nasem-repro"], ["question-purpose", "finding-claim"]),
    ("generalizability", "To which populations, settings, times or interventions may the finding transport under what evidence?", "transport/applicability claim", ["nasem-repro", "ich-e9r1"], ["target-population", "finding-claim"]),
    ("result-envelope", "Which estimate, uncertainty, diagnostics, assumptions, data/method editions and receipts form one result occurrence?", "result value/evidence object", ["nasem-repro", "rap"], ["finding-claim", "reproducibility"]),
    ("notebook-record", "Which cell/source/output occurrences, execution graph, trust state and environment manifest constitute a notebook record?", "notebook document model", ["jupyter-format", "jupyter-security"], ["result-envelope"]),
]


def modules() -> list[dict[str, Any]]:
    return [{"module_id": f"module.statistics.{mid}", "owned_question": question, "formalism": formalism, "source_refs": [f"source.statistics.{ref}" for ref in refs], "dependency_refs": [f"module.statistics.{ref}" for ref in deps], "research_status": "EVIDENCE_BACKED_UNRATIFIED", "authority_limit": "The module proposes bounded statistical semantics; it does not select an enterprise owner, authorize a decision, qualify an implementation or close a canonical gap."} for mid, question, formalism, refs, deps in MODULE_ROWS]


LAW_ROWS = [
    ("population-sample", "Target population and observed sample must not collapse."),
    ("frame-population", "Sampling frame coverage and target-population membership must not collapse."),
    ("unit-row", "Observational unit and storage row must not collapse."),
    ("selection-analysis", "Selection design and analysis procedure must not collapse."),
    ("estimand-estimator", "Estimand, estimator and realized estimate must remain distinct."),
    ("estimate-truth", "An estimate is not the unknown population truth."),
    ("standard-error-variability", "Standard error is estimator uncertainty under a design/model, not raw-data spread."),
    ("confidence-credible", "Confidence and credible intervals have different probability semantics."),
    ("prediction-confidence", "Prediction intervals and parameter confidence intervals target different objects."),
    ("measurement-sampling", "Measurement uncertainty and sampling uncertainty must not collapse."),
    ("missing-null-zero", "Missing, null, structural absence, censored and numerical zero must not collapse."),
    ("mar-observed", "MCAR, MAR or MNAR is not directly observed from a missing-value pattern."),
    ("weight-frequency", "Survey/design weight is not automatically a frequency, importance or loss weight."),
    ("description-inference", "Describing the captured data occurrence is not inference to a population."),
    ("exploratory-confirmatory", "Exploratory discovery and confirmatory error-controlled analysis must not collapse."),
    ("association-cause", "Association or regression coefficient is not a causal effect without identification."),
    ("fit-adequacy", "Numerical convergence or fit completion is not model adequacy."),
    ("diagnostic-proof", "Passing selected diagnostics does not prove a model true or fit for every use."),
    ("p-null-probability", "A p-value is not the posterior probability that the null hypothesis is true."),
    ("p-effect-size", "A p-value is not effect size or practical importance."),
    ("significance-decision", "Statistical significance is not an operational or policy authorization."),
    ("nonrejection-equivalence", "Failure to reject is not evidence of equivalence or no effect."),
    ("alpha-observed-fdp", "A nominal error rate is not the realized false-discovery proportion."),
    ("fwer-fdr", "Family-wise error rate and false-discovery rate must not collapse."),
    ("hypothesis-family-list", "A multiplicity family is a semantic claim family, not merely every p-value in one file."),
    ("bootstrap-row-resample", "Bootstrap does not universally mean resampling independent rows."),
    ("random-seed-repro", "Equal seed alone does not establish reproducibility across algorithms, versions or execution orders."),
    ("robust-reproducible", "Robustness to perturbation and computational reproducibility must not collapse."),
    ("reproducible-replicable", "Re-execution on the same inputs and replication with new data must not collapse."),
    ("replicable-generalizable", "Replication in another study and generalization to a target context must not collapse."),
    ("sensitivity-supplementary", "Sensitivity analysis of assumptions and supplementary analysis of another question must not collapse."),
    ("posterior-truth", "A posterior distribution is conditional on model, prior, data and computation, not a truth distribution."),
    ("mcmc-posterior", "A finite MCMC sample is not the posterior distribution."),
    ("rhat-correctness", "An acceptable convergence diagnostic does not prove correct implementation or model adequacy."),
    ("fixed-random-meta", "Common/fixed-effect and random-effects meta-analysis target different models."),
    ("heterogeneity-noise", "Between-study heterogeneity is not automatically sampling noise."),
    ("poolable-numeric", "Numerically convertible effect estimates are not automatically semantically poolable."),
    ("finding-decision", "An analytical finding is not a relying-party decision or effect authorization."),
    ("evidence-acceptance", "Statistical evidence and acceptance under a policy must not collapse."),
    ("notebook-execution", "Notebook cell order is not necessarily execution order."),
    ("stored-output-repro", "Stored notebook output is not proof that the recorded source/environment reproduces it."),
    ("provider-semantics", "A provider API, default or successful return does not own statistical meaning."),
    ("method-family-substitution", "Methods in the same catalog category are not interchangeable without equal assumptions, target and guarantees."),
    ("uncertainty-risk", "Statistical uncertainty and decision loss/risk must not collapse."),
    ("coverage-fitness", "Nominal coverage under a model is not fitness for a domain decision."),
    ("ai-authority", "An AI or agent may propose an analysis but cannot infer missing design facts, waive diagnostics or authorize a claim/effect."),
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.statistics.non-collapse.{lid}", "statement": statement, "status": "EVIDENCE_BACKED_UNRATIFIED", "canonical_gaps_closed": 0} for lid, statement in LAW_ROWS]


METHOD_GROUPS = {
    "study_and_sampling": ["question formulation", "target-population specification", "sampling-frame construction", "simple random sampling", "stratified sampling", "cluster/multistage sampling", "systematic sampling", "unequal-probability sampling", "survey weighting/calibration", "power/sample-size design", "preregistered analysis specification"],
    "data_and_description": ["frequency/tabulation", "location summaries", "dispersion summaries", "quantiles/order statistics", "shape/skewness/kurtosis", "robust descriptive summaries", "contingency tables", "correlation/association", "exploratory graphical analysis", "missing-data pattern analysis"],
    "probability_and_simulation": ["discrete distributions", "continuous distributions", "multivariate distributions", "conditional/joint probability", "random-variable transforms", "expectation/moments", "covariance/dependence", "random variate generation", "Monte Carlo integration", "importance sampling"],
    "estimation_and_intervals": ["method of moments", "maximum likelihood", "estimating equations", "least/weighted least squares", "shrinkage/regularization", "Bayesian posterior estimation", "confidence intervals", "credible intervals", "prediction intervals", "tolerance intervals", "delta method", "bootstrap", "jackknife"],
    "tests_and_error_control": ["one-sample tests", "two-sample tests", "paired/repeated tests", "contingency/exact tests", "goodness-of-fit tests", "permutation/randomization tests", "equivalence/noninferiority tests", "sequential/anytime-valid tests", "family-wise error control", "false-discovery-rate control", "power/operating characteristics"],
    "models_and_diagnostics": ["linear regression", "generalized linear models", "mixed/hierarchical models", "nonlinear regression", "nonparametric smoothing", "robust estimation", "dimension reduction", "latent-variable models", "model selection", "residual diagnostics", "influence diagnostics", "posterior predictive checks", "computational convergence diagnostics"],
    "synthesis_and_claims": ["fixed/common-effect meta-analysis", "random-effects meta-analysis", "heterogeneity analysis", "sensitivity analysis", "missing-data sensitivity", "effect-measure transformation", "analytical finding construction", "computational reproducibility", "replication appraisal", "generalizability appraisal"],
}


def methods() -> list[dict[str, Any]]:
    rows = []
    for group, names in METHOD_GROUPS.items():
        for name in names:
            rows.append({"method_type_id": f"method.statistics.{slug(group)}.{slug(name.replace(' ', '-').replace('/', '-'))}", "method_group": group, "name": name, "selection_law": "Selection requires an explicit question/estimand, design, data type, assumptions, loss/error guarantee, resource budget and conformance evidence; category membership is not substitutability.", "status": "TAXONOMY_CANDIDATE_UNRATIFIED"})
    return rows


EXPERT_ROWS = [
    ("fisher", "Ronald A. Fisher", ["asa-pvalue", "nist-handbook"], ["Keep likelihood, experimental design and data-generating assumptions explicit.", "Do not collapse evidence against a model into an automatic decision rule."]),
    ("neyman", "Jerzy Neyman", ["ich-e9", "census-sample"], ["Model procedures by repeated-sampling operating characteristics.", "Separate a confidence procedure from probability about the realized parameter."]),
    ("pearson", "Egon S. Pearson", ["asa-2021"], ["Treat tests as designed procedures with alternatives and error trade-offs.", "A rejection rule needs a declared decision context."]),
    ("tukey", "John W. Tukey", ["nist-eda"], ["Make exploration a first-class mode for discovering structure and checking assumptions.", "Keep exploratory hypotheses distinct from confirmatory claims."]),
    ("huber", "Peter J. Huber", ["huber-robust"], ["Define robustness against an explicit neighborhood/contamination model.", "Do not use robust as an untestable adjective."]),
    ("efron", "Bradley Efron", ["efron-bootstrap"], ["Make the resampling unit and target sampling distribution explicit.", "Bootstrap validity is method- and dependence-specific."]),
    ("rubin", "Donald B. Rubin", ["rubin-missing", "ich-e9r1"], ["Model the observation/missingness process and separate estimand from estimator.", "Unverifiable assumptions require sensitivity analysis, not silent defaults."]),
    ("cox", "David R. Cox", ["nist-model", "ich-e9"], ["Match statistical models to the scientific question and design.", "Preserve conditionality and nuisance structure rather than treating coefficients as universal facts."]),
    ("benjamini", "Yoav Benjamini", ["bh-fdr"], ["Choose error criteria to match a family of claims and discovery use.", "FDR control is not FWER control and depends on stated conditions."]),
    ("hochberg", "Yosef Hochberg", ["bh-fdr", "fda-multiplicity"], ["Treat multiplicity as a structured claim-family problem.", "An adjusted number does not select the family or decision policy."]),
    ("gelman", "Andrew Gelman", ["stan-ppc", "vehtari-rhat"], ["Use generative checking and multiple diagnostics to expose model/computation failures.", "Do not treat one convergence statistic or posterior interval as sufficient validation."]),
    ("vehtari", "Aki Vehtari", ["vehtari-rhat"], ["Make Monte Carlo error and tail/bulk effective sample size explicit.", "Inference algorithms require diagnostic evidence at the actual estimands of interest."]),
    ("altman", "Douglas G. Altman", ["cochrane-meta", "cochrane-effects"], ["Report effect estimates and uncertainty rather than threshold labels alone.", "Evidence synthesis must preserve compatible outcome/effect semantics and bias limits."]),
    ("higgins", "Julian P. T. Higgins", ["cochrane-meta", "cochrane-effects"], ["Model heterogeneity and sensitivity across studies explicitly.", "Pooling is a semantic decision before it is a numerical operation."]),
    ("wasserstein", "Ronald L. Wasserstein", ["asa-pvalue", "asa-2021"], ["Prevent p-value thresholds from replacing scientific context and transparency.", "Statistical evidence is one input to judgment, not its authority."]),
    ("ramdas", "Aaditya Ramdas", ["asa-safe"], ["Represent sequential evidence with protocols valid under optional stopping.", "Anytime validity remains conditional on the filtration and test-martingale assumptions."]),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.statistics.{eid}", "name": name, "source_refs": [f"source.statistics.{ref}" for ref in refs], "lessons_for_composable_platform": lessons, "authority_limit": "Expert work constrains candidate semantics and methods; the expert is not the SAN semantic owner or qualification authority.", "status": "RESEARCHED_PROFILE"} for eid, name, refs, lessons in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("asa-replicability", 2021, "The ASA task-force statement reframed significance practice around design, context, uncertainty, transparency and cumulative evidence.", ["asa-2021"]),
    ("rhat", 2021, "Rank-normalized and folded R-hat plus localized effective sample size improved diagnostics for heavy tails and scale failures.", ["vehtari-rhat"]),
    ("census-quality", 2022, "The revised Census statistical quality standards made sample-design, weighting, variance and uncertainty obligations operationally explicit.", ["census-sample", "census-analyze", "census-report"]),
    ("fda-multiplicity", 2022, "FDA's final multiple-endpoints guidance made claim families, endpoint ordering and multiplicity strategy explicit.", ["fda-multiplicity"]),
    ("rap-strategy", 2022, "The UK RAP strategy operationalized analysis-as-code, versioning, tests, peer review and dependency capture for official analytics.", ["rap"]),
    ("anytime-valid", 2023, "Safe anytime-valid inference consolidated e-process and confidence-sequence semantics for optional stopping and continuation.", ["asa-safe"]),
    ("gum1", 2023, "GUM-1 refreshed the conceptual separation of measurand/model inputs, uncertainty evaluation and downstream use.", ["gum1"]),
    ("cochrane-65", 2024, "Cochrane Handbook 6.5 refreshed effect-measure, heterogeneity, meta-analysis and sensitivity guidance for evidence synthesis.", ["cochrane-meta", "cochrane-effects"]),
    ("stan-239", 2025, "Stan 2.39 exposes a broader editioned inference and diagnostic surface while retaining model-conditional semantics.", ["stan"]),
    ("scipy-resampling", 2026, "SciPy's unified resampling and Monte Carlo method objects make stochastic test configuration, RNG and budgets more explicit.", ["scipy-stats"]),
]


def innovations() -> list[dict[str, Any]]:
    return [{"innovation_id": f"innovation.statistics.{iid}", "year": year, "innovation": text, "source_refs": [f"source.statistics.{ref}" for ref in refs], "ai_or_llm_dependency": False, "boundary_implication": "Encode as an editioned semantic method/protocol/evidence module; do not transfer authority to a provider or create an ambient AI product.", "status": "EVIDENCE_BACKED_NON_LLM_INNOVATION"} for iid, year, text, refs in INNOVATION_ROWS]


MODULE_MAP = {
    "library.cbv.notebook_document": ["notebook-record", "analysis-specification", "result-envelope", "reproducibility"],
    "library.cbv.uncertainty_contracts": ["interval-estimate", "finding-claim", "result-envelope"],
    "library.csp.quantity.partial-information": ["missingness-mechanism", "measurement-scale"],
    "library.csp.quantity.probability-core": ["probability-space", "distribution-family"],
    "library.csp.quantity.scale-types": ["measurement-scale", "variable-role"],
    "library.csp.quantity.uncertainty-propagation": ["interval-estimate", "result-envelope"],
    "library.lpe.prov-statement-algebra": ["reproducibility", "result-envelope"],
    "library.lpe.provenance-assertion": ["reproducibility", "result-envelope"],
    "library.method_kernels.analysis_design": ["question-purpose", "target-population", "sampling-design", "analysis-population", "estimand", "analysis-specification"],
    "library.method_kernels.analytical_finding_contract": ["finding-claim", "result-envelope", "generalizability"],
    "library.method_kernels.artifact_envelope": ["reproducibility", "result-envelope"],
    "library.method_kernels.descriptive_statistics": ["descriptive-summary", "exploratory-analysis", "measurement-scale"],
    "library.method_kernels.inferential_tests_resampling": ["hypothesis-model", "p-value", "error-power", "multiplicity-family", "sequential-monitoring", "resampling"],
    "library.method_kernels.method_contracts": ["analysis-specification", "result-envelope"],
    "library.method_kernels.numerical_kernel_facade": ["model-fit", "randomness-stream", "reproducibility"],
    "library.method_kernels.probabilistic_inference": ["probabilistic-inference", "model-diagnostics", "randomness-stream"],
    "library.method_kernels.probability_distribution_algebra": ["probability-space", "distribution-family", "randomness-stream"],
    "library.method_kernels.regression_glm_estimators": ["regression-model", "model-fit", "model-diagnostics", "model-selection"],
    "library.method_kernels.result_algebra": ["interval-estimate", "finding-claim", "result-envelope"],
    "library.method_kernels.statistical_estimators": ["estimator", "sampling-distribution", "interval-estimate", "robustness", "sensitivity-analysis", "meta-analysis"],
    "library.pipeline.data_cut_algebra": ["data-cut", "analysis-population", "reproducibility"],
    "library.smf.missingness_algebra": ["missingness-mechanism", "measurement-scale"],
}


AXIS_QUESTIONS = {
    "semantic_object": "Which question, population, frame, unit, sample, variable, estimand, estimator, estimate, model, test, interval, finding, analysis or notebook occurrence is owned?",
    "semantic_role": "Which roles are study designer, data producer, sampling authority, analyst, method provider, reviewer, claim issuer, relying party and decision/effect authority?",
    "identity_and_equality": "What makes population/frame/sample/data cut, analysis plan, variable, estimand, method, model, RNG, result, finding and notebook editions equal or distinct?",
    "grain_and_cardinality": "Are semantics per population, frame unit, sampled unit, observation, variable, cluster, stratum, hypothesis, endpoint, model, study, result or synthesis?",
    "state_and_change": "What legal proposed, prespecified, sampled, observed, frozen, fitted, diagnosed, appraised, reported, corrected, retracted and superseded transitions exist?",
    "time": "How are target period, observation, recording, data-cut, plan-freeze, analysis, interim look, publication, correction and replication times separated?",
    "order_and_topology": "Which selection hierarchy, cluster/stratum structure, repeated-measure order, hypothesis family, model graph, execution graph and evidence graph constrain analysis?",
    "partiality_and_uncertainty": "How are coverage error, nonresponse, missingness, censoring, measurement error, sampling error, model uncertainty, Monte Carlo error and decision uncertainty separated?",
    "authority_and_trust": "Who defines the question, population, estimand, sample design, analysis plan, multiplicity family, claim strength, review, acceptance, correction and retraction?",
    "effect_boundary": "How are pure statistical computation and claim construction separated from data acquisition, publication, policy judgment, authorization and operational effect?",
    "representation": "Which table, tensor, distribution, sample-design, model, analysis-plan, result, diagnostic, evidence, notebook and provenance carriers are used at what edition and loss?",
    "composition_algebra": "How do design, data cut, weights, estimand, estimator, diagnostics, sensitivity, multiplicity, finding and evidence compose and propagate refusals/uncertainty?",
    "compatibility_and_evolution": "What population, frame, variable, coding, weight, estimand, method, model, software and policy changes preserve comparability or require replay/reappraisal?",
    "resources_and_failure": "What data, memory, precision, resample, chain, iteration, diagnostic, review and deadline budgets apply, and when must computation refuse?",
    "evidence_and_conformance": "Which analytical fixtures, simulated calibration cases, coverage/error tests, negative twins, independent implementations and replay receipts support each bounded claim?",
    "privacy_security_safety": "How are confidential samples, disclosure, reidentification, poisoned data, p-hacking, unsafe claims, automation bias and unauthorized decisions controlled?",
}


VACANCIES = [
    ("library.method_kernels.sampling_design_semantics", "Own sampling frames, selection designs, inclusion probabilities, strata/clusters, weights and design-aware variance semantics."),
    ("library.method_kernels.estimand_analysis_specification", "Own question-to-estimand-to-analysis-plan identity, freeze time, deviations and sensitivity obligations."),
    ("library.method_kernels.missing_data_semantics", "Own missingness mechanisms, observation models, imputation estimands and sensitivity protocols without collapsing nulls."),
    ("library.method_kernels.multiplicity_sequential_evidence", "Own hypothesis-family identity, FWER/FDR/other error criteria, interim looks and anytime-valid evidence protocols."),
    ("library.method_kernels.model_diagnostics", "Own model/computation diagnostic claims, failure modes and bounded adequacy evidence independently of fitting."),
    ("library.method_kernels.robust_nonparametric_estimators", "Own robustness neighborhoods, influence/breakdown targets and nonparametric estimator assumptions."),
    ("library.method_kernels.evidence_synthesis", "Own study/effect compatibility, pooling targets, heterogeneity and meta-analysis result semantics."),
    ("library.method_kernels.reproducible_analysis_spec", "Own immutable analysis/data/method/environment/randomness identity and re-execution evidence."),
]


def boundary_findings(consumers: dict[str, set[str]]) -> list[dict[str, Any]]:
    direct = sorted(ref for ref in LIBRARIES if PRODUCT in consumers[ref])
    findings = [
        {"finding_id": "finding.statistics.notebook-boundary.v1", "library_refs": direct, "current_product_refs": [PRODUCT], "candidate_disposition": "RETAIN_NOTEBOOK_AS_REPRODUCIBLE_STUDY_ARTIFACT_NOT_STATISTICS_OWNER", "reason": "A notebook owns document/cell/output/trust and captured execution evidence; it may compose statistical methods but does not own populations, estimands, estimators or inferential validity.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.statistics.shared-foundation.v1", "library_refs": sorted(NEIGHBORS), "current_product_refs": sorted({product for ref in NEIGHBORS for product in consumers[ref]}), "candidate_disposition": "SHARED_STATISTICAL_FORMALISM_NOT_STANDALONE_PRODUCT_BY_DEFAULT", "reason": "The kernels are imported by many analytical products; method reuse does not imply one monolithic statistics product or notebook ownership.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.statistics.causal-seam.v1", "library_refs": ["library.method_kernels.analysis_design", "library.method_kernels.regression_glm_estimators", "library.method_kernels.statistical_estimators"], "current_product_refs": [], "candidate_disposition": "ASSOCIATIONAL_INFERENCE_SEPARATE_FROM_CAUSAL_IDENTIFICATION", "reason": "General estimators and regression may implement a causal estimator only after a causal context supplies intervention, identification and sensitivity semantics.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.statistics.predictive-seam.v1", "library_refs": ["library.method_kernels.regression_glm_estimators", "library.method_kernels.probabilistic_inference"], "current_product_refs": [], "candidate_disposition": "ESTIMATION_AND_MODEL_CHECKING_SEPARATE_FROM_PREDICTIVE_LIFECYCLE", "reason": "Model fitting is a reusable method; feature/target contracts, scoring, rollout, drift and operational assurance remain predictive-product responsibilities.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.statistics.measurement-seam.v1", "library_refs": ["library.csp.quantity.uncertainty-propagation", "library.cbv.uncertainty_contracts"], "current_product_refs": sorted({product for ref in ["library.csp.quantity.uncertainty-propagation", "library.cbv.uncertainty_contracts"] for product in consumers[ref]}), "candidate_disposition": "QUALIFIED_UNCERTAINTY_HOMONYMS_REQUIRE_TYPED_IMPORTS", "reason": "Measurement uncertainty, sampling uncertainty, posterior uncertainty, Monte Carlo error and displayed decision uncertainty have different owners and propagation laws.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.statistics.missingness-seam.v1", "library_refs": ["library.csp.quantity.partial-information", "library.smf.missingness_algebra"], "current_product_refs": sorted({product for ref in ["library.csp.quantity.partial-information", "library.smf.missingness_algebra"] for product in consumers[ref]}), "candidate_disposition": "SPLIT_CARRIER_MISSINGNESS_FROM_OBSERVATION_MECHANISM", "reason": "A carrier can encode absent/unknown/inapplicable values, while inferential missingness requires a joint response/data mechanism and sensitivity assumptions.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.statistics.facade-seam.v1", "library_refs": ["library.method_kernels.numerical_kernel_facade", "library.method_kernels.method_contracts"], "current_product_refs": [], "candidate_disposition": "COMPOSITION_ONLY_NO_STATISTICAL_DEFAULTS", "reason": "A method/provider facade may route a qualified implementation but cannot infer the population, estimand, design, hypothesis family, assumptions or claim strength.", "owner_decision": "UNRATIFIED"},
    ]
    findings.extend({"finding_id": f"finding.statistics.vacancy.{slug(ref)}.v1", "library_refs": [], "proposed_library_ref": ref, "current_product_refs": [], "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED", "reason": reason, "owner_decision": "UNRATIFIED"} for ref, reason in VACANCIES)
    return findings


def build() -> dict[str, Any]:
    ss, ms, ls, method_rows, expert_rows, innovation_rows = sources(), modules(), laws(), methods(), experts(), innovations()
    contributions = {row["library_id"]: row for row in load_jsonl(REGISTRY / "library-contributions.jsonl")}
    assert set(LIBRARIES) <= contributions.keys()
    coord = {row["library_ref"]: row for row in load_jsonl(SEM / "library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact = {row["library_ref"]: row for row in load_jsonl(SEM / "p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    consumers = {ref: set() for ref in LIBRARIES}
    subjects = {ref: set() for ref in LIBRARIES}
    for row in product_rows():
        for edge in row["concrete_bindings"]:
            ref = edge["concrete_library_ref"]
            if ref in consumers:
                consumers[ref].add(row["product_ref"])
                subjects[ref].add(row["subject_ref"])
    targeted = {(row["axis"], row["library_ref"]): row for row in load_jsonl(SEM / "targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    module_by_id = {row["module_id"]: row for row in ms}
    bindings, axes = [], []
    for ref in LIBRARIES:
        module_refs = [f"module.statistics.{mid}" for mid in MODULE_MAP[ref]]
        evidence_refs = sorted({source for module_ref in module_refs for source in module_by_id[module_ref]["source_refs"]})
        exact_row, coord_row = exact.get(ref), coord.get(ref)
        routed = bool(exact_row and coord_row)
        bindings.append({
            "record_kind": "statistical_inference_library_semantic_binding_candidate",
            "binding_id": f"binding.statistics-semantic-slice.{slug(ref)}.v1",
            "library_ref": ref,
            "library_name": contributions[ref]["name"],
            "semantic_module_refs": module_refs,
            "evidence_refs": evidence_refs,
            "exact_contract_docket_ref": exact_row["docket_id"] if exact_row else None,
            "coordinate_binding_docket_ref": coord_row["binding_docket_id"] if coord_row else None,
            "downstream_contract_route": "ROUTED" if routed else "MISSING_P5_AND_COORDINATE_DOCKET_TYPED_VACANCY",
            "downstream_subject_refs": sorted(subjects[ref]),
            "downstream_product_refs": sorted(consumers[ref]),
            "boundary_disposition_candidate": "RETAIN_DECLARED_NOTEBOOK_DEPENDENCY_WITH_NARROW_OWNER" if PRODUCT in consumers[ref] else "RETAIN_SHARED_FORMALISM_NEIGHBOR_WITH_EXPLICIT_ACL",
            "compiler_binding": "REFUSED",
            "refusal_reasons": ([] if routed else ["DOWNSTREAM_CONTRACT_ROUTE_MISSING"]) + ["OWNER_RATIFICATION_MISSING", "MEMBER_AXIS_APPLICABILITY_UNRATIFIED", "EXACT_CONTRACT_UNSELECTED", "IMPLEMENTATIONS_UNQUALIFIED"],
            "completion_claim": False,
        })
        for axis in AXES:
            targeted_row = targeted.get((axis, ref))
            axes.append({
                "record_kind": "statistical_inference_library_axis_decision_candidate",
                "decision_candidate_id": f"decision-candidate.statistics-axis.{slug(ref)}.{axis.replace('_', '-')}.v1",
                "library_ref": ref,
                "axis": axis,
                "semantic_module_refs": module_refs,
                "coordinate_question": AXIS_QUESTIONS[axis],
                "applicability_candidate": "REQUIRED_EXPLICIT_PROFILE",
                "evidence_refs": evidence_refs,
                "targeted_member_adjudication_occurrence_ref": targeted_row["occurrence_id"] if targeted_row else None,
                "coordinate_answers": [],
                "member_applicability": "PROPOSED_OWNER_REVIEW_REQUIRED",
                "owner_decision": "UNRATIFIED",
                "status": "EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            })
    findings = boundary_findings(consumers)
    context = {
        "record_kind": "bounded_context_candidate",
        "context_id": "context.statistical-inference-semantic-slice.v1",
        "as_of": AS_OF,
        "vision": "How can a declared question, population, design, data cut and assumptions be transformed into bounded estimates, uncertainty and findings without collapsing samples into populations, estimators into estimands, p-values into truth, reproducibility into replication or findings into decisions?",
        "inside": ["analysis question, target population, sampling frame/design and analysis population", "estimand and editioned analysis specification", "variable roles, data types, missingness and survey-weight semantics", "probability/distribution and randomness semantics", "descriptive/exploratory analysis", "estimators, sampling distributions, intervals and resampling", "tests, error/power, multiplicity and sequential evidence", "regression/GLM, probabilistic inference, diagnostics and robustness", "sensitivity, meta-analysis and bounded finding construction", "reproducibility, replication and generalizability distinctions"],
        "outside": ["domain-specific measurement ownership", "causal identification and intervention semantics", "predictive feature/scoring/model lifecycle", "time-series, survival, spatial, process and graph semantics", "data acquisition/storage/query execution", "publication authority and operational decision/effect", "LLM or agent authority"],
        "neighbors": [
            {"context_ref": "context.measurement-metrology", "relationship": "anti_corruption_layer"},
            {"context_ref": "context.causal-inference-semantic-slice", "relationship": "customer_supplier"},
            {"context_ref": "context.predictive-analytics-semantic-slice", "relationship": "customer_supplier"},
            {"context_ref": "context.signal-condition-semantic-slice", "relationship": "customer_supplier"},
            {"context_ref": "context.forecasting-workbench", "relationship": "customer_supplier"},
            {"context_ref": "context.quality-reconciliation", "relationship": "customer_supplier"},
            {"context_ref": "context.notebook-document", "relationship": "published_language"},
            {"context_ref": "context.decision-effect-authority", "relationship": "anti_corruption_layer"},
        ],
        "published_language": ["AnalysisQuestion", "TargetPopulation", "SamplingFrameEdition", "SamplingDesign", "AnalysisPopulation", "Estimand", "AnalysisSpecificationEdition", "DataCut", "VariableRole", "MissingnessAssumption", "SurveyWeightProfile", "ProbabilityModel", "EstimatorSpecification", "Estimate", "IntervalEstimate", "HypothesisFamily", "TestResult", "MultiplicityPolicy", "DiagnosticFinding", "SensitivityResult", "AnalyticalFinding", "ReproducibilityReceipt"],
        "ratification": "WITHHELD",
        "completion_claim": False,
    }
    summary = {
        "program_id": "program.statistical-inference-semantic-slice.v1",
        "as_of": AS_OF,
        "primary_or_official_sources": len(ss),
        "semantic_modules": len(ms),
        "non_collapse_laws": len(ls),
        "method_types": len(method_rows),
        "expert_learning_profiles": len(expert_rows),
        "recent_non_llm_innovations": len(innovation_rows),
        "bound_libraries": len(bindings),
        "declared_product_libraries": sum(PRODUCT in consumers[ref] for ref in LIBRARIES),
        "formalism_neighbor_libraries": len(NEIGHBORS),
        "candidate_new_library_vacancies": len(VACANCIES),
        "libraries_without_declared_product_consumer": sum(not consumers[ref] for ref in LIBRARIES),
        "missing_downstream_contract_routes": sum(row["downstream_contract_route"].startswith("MISSING") for row in bindings),
        "library_axis_decision_candidates": len(axes),
        "product_capability_boundary_findings": len(findings),
        "owner_decisions": 0,
        "exact_contracts_selected": 0,
        "qualified_implementations": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {"context": context, "sources": ss, "modules": ms, "laws": ls, "methods": method_rows, "experts": expert_rows, "innovations": innovation_rows, "libraries": bindings, "axes": axes, "findings": findings, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "bounded-context.json": json.dumps(built["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "semantic-modules.jsonl": "".join(canonical(row) + "\n" for row in built["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(row) + "\n" for row in built["laws"]),
        "statistical-method-taxonomy.jsonl": "".join(canonical(row) + "\n" for row in built["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(row) + "\n" for row in built["experts"]),
        "innovation-records.jsonl": "".join(canonical(row) + "\n" for row in built["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(row) + "\n" for row in built["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(row) + "\n" for row in built["findings"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.statistical-inference-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    summary = build()["summary"]
    print(f"BUILD PASS statistical inference semantic slice: {summary['semantic_modules']} modules, {summary['method_types']} methods, {summary['bound_libraries']} libraries and {summary['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
