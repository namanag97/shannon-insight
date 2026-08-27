#!/usr/bin/env python3
"""Build an evidence-backed semantic slice for predictive analytics and forecasting."""
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
    rows=load_jsonl(REGISTRY/"library-contributions.jsonl")
    return sorted(row["library_id"] for row in rows if row["library_id"].startswith("library.predictive.") or row["library_id"].startswith("library.method_kernels.forecast") or row["library_id"]=="library.method_kernels.regression_glm_estimators")


LIBRARIES = library_universe()


def sources() -> list[dict[str, Any]]:
    rows = [
        ("sklearn-pitfalls","Common pitfalls and recommended practices",["scikit-learn project"],2026,"official_reference_documentation","https://scikit-learn.org/stable/common_pitfalls.html","Defines inconsistent preprocessing and prediction-time data leakage with pipeline/split counterexamples.","Provider guidance does not define every domain feature or prove a study leakage-free."),
        ("sklearn-cv","Cross-validation: evaluating estimator performance",["scikit-learn project"],2026,"official_reference_documentation","https://scikit-learn.org/stable/modules/cross_validation.html","Separates random, grouped and time-ordered split regimes and states their dependence assumptions.","A splitter implementation does not select the population, grouping, horizon or deployment-valid study design."),
        ("sklearn-metrics","Metrics and scoring: quantifying prediction quality",["scikit-learn project"],2026,"official_reference_documentation","https://scikit-learn.org/stable/modules/model_evaluation.html","Separates point/distribution targets, consistent scoring functions, prediction and decision making, and multiple metric families.","Metric availability does not select utility, threshold, acceptance, materiality or affected-party trade-offs."),
        ("sklearn-calibration","Probability calibration",["scikit-learn project"],2026,"official_reference_documentation","https://scikit-learn.org/stable/modules/calibration.html","Defines reliability semantics and independent data requirements for calibrator fitting.","A calibration curve or aggregate score does not establish subgroup, temporal or decision calibration."),
        ("sklearn-estimator","Developing scikit-learn estimators",["scikit-learn project"],2026,"official_provider_contract","https://scikit-learn.org/stable/developers/develop.html","Separates estimator, predictor, transformer and fitted state while specifying fit/predict input contracts.","The provider API does not own portable model-family semantics or artifact identity."),
        ("onnx-ir","ONNX Intermediate Representation specification",["ONNX project"],2026,"normative_open_specification","https://onnx.ai/onnx/repo-docs/IR.html","Defines versioned computation graphs, types, operator sets, model metadata and runtime-agnostic serialization.","Syntactic validation and operator support do not prove semantic equivalence, accuracy, safety or deployment fitness."),
        ("onnx-versioning","ONNX versioning specification",["ONNX project"],2026,"normative_open_specification","https://onnx.ai/onnx/repo-docs/Versioning.html","Keeps IR, operator-set and model versions independent and defines breaking-change rules.","Compatibility under ONNX rules does not prove numerical parity across providers or preserve external preprocessing."),
        ("kserve-v2","Open Inference Protocol V2",["KServe project"],2026,"official_open_protocol","https://kserve.github.io/website/docs/concepts/architecture/data-plane/v2-protocol","Defines framework-neutral health, metadata and inference endpoints with versioned model requests and typed tensors.","A serving protocol does not define feature meaning, output interpretation, batch/stream guarantees or decision authority."),
        ("model-cards","Model Cards for Model Reporting",["Margaret Mitchell","Simone Wu","Andrew Zaldivar","Parker Barnes","Lucy Vasserman","Ben Hutchinson","Elena Spitzer","Inioluwa Deborah Raji","Timnit Gebru"],2019,"peer_reviewed_primary_research","https://doi.org/10.1145/3287560.3287596","Proposes intended-use, limitation and disaggregated performance reporting for trained models.","A model card is a scoped report, not the executable artifact, proof of claims or deployment authorization."),
        ("datasheets","Datasheets for Datasets",["Timnit Gebru","Jamie Morgenstern","Briana Vecchione","Jennifer Wortman Vaughan","Hanna Wallach","Hal Daumé III","Kate Crawford","and collaborators"],2021,"peer_reviewed_primary_research","https://doi.org/10.1145/3458723","Defines structured documentation questions for dataset motivation, composition, collection, preprocessing, uses and distribution.","Documentation does not make a dataset representative, lawful, correct or suitable for a particular target."),
        ("snorkel","Snorkel: Rapid Training Data Creation with Weak Supervision",["Alexander Ratner","Stephen H. Bach","Henry Ehrenberg","Jason Fries","Sen Wu","Christopher Ré"],2017,"peer_reviewed_primary_research","https://doi.org/10.14778/3157794.3157797","Separates labeling functions, their unknown accuracies/correlations and a generative label model from ground truth.","Weakly supervised labels remain probabilistic derived assertions and cannot be silently promoted to adjudicated truth."),
        ("conformal-regression","Distribution-Free Predictive Inference for Regression",["Jing Lei","Max G'Sell","Alessandro Rinaldo","Ryan J. Tibshirani","Larry Wasserman"],2018,"peer_reviewed_primary_research","https://doi.org/10.1080/01621459.2017.1307116","Provides finite-sample marginal coverage for conformal regression bands under exchangeability-related design conditions.","Marginal coverage is not conditional coverage, calibration, causal validity or an individual guarantee."),
        ("conformal-risk","Conformal Risk Control",["Anastasios N. Angelopoulos","Stephen Bates","Adam Fisch","Lihua Lei","Tal Schuster"],2024,"peer_reviewed_primary_research","https://research.google/pubs/conformal-risk-control/","Extends conformal procedures to expected monotone-loss control with finite-sample bounds.","Its guarantee is scoped to the loss, calibration sample and assumptions; it does not authorize decisions or cover arbitrary drift."),
        ("nist-bias","NIST SP 1270 — Towards a Standard for Identifying and Managing Bias in AI",["Reva Schwartz","Apostol Vassilev","Kristen Greene","Lori Perine","Andrew Burt","Patrick Hall"],2022,"government_primary_guidance","https://doi.org/10.6028/NIST.SP.1270","Separates computational, human and systemic sources of bias and frames bias management across lifecycle and context.","It does not select one mathematical fairness definition or make metric parity sufficient for absence of harm."),
        ("nist-airmf","NIST AI RMF 1.0",["National Institute of Standards and Technology"],2023,"government_risk_framework","https://doi.org/10.6028/NIST.AI.100-1","Requires contextual mapping, measurement, management, governance and ongoing monitoring of validity, reliability and impacts.","A risk framework does not certify any model, prescribe exact thresholds or replace domain authority."),
        ("iso-lifecycle","ISO/IEC 5338:2023 — AI system life cycle processes",["ISO/IEC JTC 1/SC 42"],2023,"international_standard","https://www.iso.org/standard/81118.html","Defines controlled lifecycle processes for machine-learning and heuristic systems, aligned with system/software lifecycle standards.","The standard does not define model-family mathematics, provider APIs or evidence that a particular lifecycle was executed."),
        ("interpretable-ml","Definitions, methods, and applications in interpretable machine learning",["W. James Murdoch","Chandan Singh","Karl Kumbier","Reza Abbasi-Asl","Bin Yu"],2019,"peer_reviewed_primary_framework","https://doi.org/10.1073/pnas.1900654116","Separates model-based and post-hoc interpretation and predictive accuracy, descriptive accuracy and relevance to an audience.","An interpretation is not automatically faithful, causal, useful to every audience or a reason for a decision."),
        ("shapley-limits","Problems with Shapley-value-based explanations as feature importance measures",["I. Elizabeth Kumar","Suresh Venkatasubramanian","Carlos Scheidegger","Sorelle Friedler"],2020,"peer_reviewed_counterevidence","https://proceedings.mlr.press/v119/kumar20e.html","Shows semantic and human-goal limits of treating Shapley allocations as feature explanations.","The critique does not invalidate every Shapley computation; it blocks universal explanation claims."),
        ("forecasting-book","Forecasting: Principles and Practice, third edition",["Rob J. Hyndman","George Athanasopoulos"],2021,"open_foundational_text","https://otexts.com/fpp3/","Separates time-series features, model families, temporal evaluation, accuracy, combinations and reconciliation.","A textbook taxonomy does not choose a domain horizon, loss, intervention or production acceptance policy."),
        ("mint","Optimal forecast reconciliation through trace minimization",["Shanika L. Wickramasuriya","George Athanasopoulos","Rob J. Hyndman"],2019,"peer_reviewed_primary_research","https://robjhyndman.com/publications/mint/","Defines coherent hierarchical/grouped forecast reconciliation as a projection with an estimated error-covariance structure.","Coherence is not accuracy, calibration or truth; reconciliation can change every base forecast."),
        ("m5","M5 accuracy competition: Results, findings, and conclusions",["Spyros Makridakis","Evangelos Spiliotis","Vassilios Assimakopoulos"],2022,"peer_reviewed_benchmark_evidence","https://doi.org/10.1016/j.ijforecast.2021.11.013","Evaluates methods on 42,840 hierarchical retail series with an explicit horizon, aggregation and scoring design.","Competition ranking is task-specific and cannot establish universal model superiority or deployment fitness."),
        ("proper-scoring","Strictly Proper Scoring Rules, Prediction, and Estimation",["Tilmann Gneiting","Adrian E. Raftery"],2007,"peer_reviewed_foundational_research","https://doi.org/10.1198/016214506000001437","Formalizes proper scoring rules that incentivize truthful probabilistic forecasts for a declared target functional/distribution.","A proper score does not choose business utility, threshold, population or causal action."),
        ("pytorch-export","torch.export",["PyTorch project"],2026,"official_provider_contract","https://docs.pytorch.org/docs/stable/export.html","Defines an export IR, captured shape constraints, state and serialization for PyTorch programs.","Provider export soundness is scoped to captured assumptions and is not portable semantic equivalence by itself."),
        ("xgboost-model-io","XGBoost model IO",["XGBoost project"],2025,"official_provider_contract","https://xgboost.readthedocs.io/en/stable/tutorials/saving_model.html","Separates stable model representation from memory snapshots and configuration with JSON/UBJSON formats.","Provider model IO does not preserve external feature semantics, study evidence or cross-provider numerical identity."),
        ("statsmodels-glm","Generalized Linear Models",["statsmodels project"],2026,"official_provider_contract","https://www.statsmodels.org/stable/glm.html","Exposes response-family, link, weights, offsets, fitting and result semantics for GLMs.","One implementation API does not define all regression/count/survival contracts or validate model assumptions."),
        ("cox","Regression Models and Life-Tables",["D. R. Cox"],1972,"peer_reviewed_foundational_research","https://doi.org/10.1111/j.2517-6161.1972.tb00899.x","Defines proportional-hazards regression using partial likelihood for censored time-to-event observations.","The model does not make censoring non-informative, establish causality or guarantee proportional hazards."),
        ("xgboost-paper","XGBoost: A Scalable Tree Boosting System",["Tianqi Chen","Carlos Guestrin"],2016,"peer_reviewed_primary_system_research","https://doi.org/10.1145/2939672.2939785","Defines regularized tree boosting and scalable sparsity/cache-aware training mechanisms.","A training system does not own tree-model semantics, feature meaning or universal performance claims."),
        ("gnn-message-passing","Neural Message Passing for Quantum Chemistry",["Justin Gilmer","Samuel S. Schoenholz","Patrick F. Riley","Oriol Vinyals","George E. Dahl"],2017,"peer_reviewed_primary_research","https://proceedings.mlr.press/v70/gilmer17a.html","Presents a common message-passing abstraction over graph neural models.","Message passing does not define graph identity, sampling correctness, causal edges or domain validity."),
        ("concept-drift","A survey on concept drift adaptation",["João Gama","Indrė Žliobaitė","Albert Bifet","Mykola Pechenizkiy","Abdelhamid Bouchachia"],2014,"peer_reviewed_synthesis","https://doi.org/10.1145/2523813","Separates drift detection, understanding and adaptation in evolving data streams.","A detected distribution change is not necessarily concept drift, harm, cause or authority to retrain/replace."),
        ("causal-whatif","Causal Inference: What If",["Miguel A. Hernán","James M. Robins"],2020,"open_foundational_text","https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/","Separates causal effects and interventions from associational prediction through explicit identification assumptions.","The book does not make a predictive model a causal learner or establish assumptions for a particular domain."),
    ]
    return [{"source_id":f"source.predictive.{sid}","title":title,"authors_or_publisher":authors,"year":year,"source_kind":kind,"url":url,"bounded_implication":imp,"authority_limit":limit} for sid,title,authors,year,kind,url,imp,limit in rows]


def modules() -> list[dict[str, Any]]:
    rows = [
        ("study-target","What world outcome, prediction time, horizon, population, unit and target functional define the predictive question?","study estimand/target contract",["datasheets","sklearn-metrics"],[]),
        ("label-semantics","What observed, adjudicated, proxy, delayed, censored or weakly derived assertion supplies a target value?","typed assertion/evidence model",["datasheets","snorkel"],["study-target"]),
        ("feature-semantics","Which prediction-time-available observations and transformations form each feature, at what grain and validity time?","temporal feature contract",["sklearn-pitfalls","datasheets"],["study-target"]),
        ("sampling-weighting","Which population, sample design, inclusion probability and analysis weight support the intended claim?","sampling/weighting algebra",["datasheets","sklearn-metrics"],["study-target"]),
        ("split-design","Which independent, grouped, temporal, spatial or nested partitions isolate training, tuning, calibration and final evaluation?","study partition topology",["sklearn-cv"],["sampling-weighting"]),
        ("leakage-control","Could any feature, transform, selection, label or split use information unavailable at the declared prediction time or evaluation boundary?","information-flow noninterference oracle",["sklearn-pitfalls"],["feature-semantics","split-design"]),
        ("weak-supervision","How do labeling functions, conflicts, abstentions, dependencies and derived label uncertainty remain traceable?","label-source generative/evidence algebra",["snorkel"],["label-semantics"]),
        ("model-family","What input/output carrier, fitted state, prediction functional and assumptions define a substitutable predictive model family?","typed estimator/predictor contract",["sklearn-estimator","sklearn-metrics"],["study-target","feature-semantics"]),
        ("class-regression-count","How do categorical, real-valued and count targets select distinct output domains, links, losses and validity conditions?","GLM/prediction family algebra",["statsmodels-glm","sklearn-metrics"],["model-family"]),
        ("survival-longitudinal","How are censoring, truncation, repeated measures, subject effects, hazard, survival and trajectory outputs represented?","event-history/longitudinal model",["cox","statsmodels-glm"],["model-family"]),
        ("forecast-model","How do origin, horizon, frequency, seasonality, covariates, update policy and point/quantile/distribution output define a forecast?","time-indexed predictive process",["forecasting-book","proper-scoring"],["model-family"]),
        ("forecast-reconciliation","How are base forecasts projected into a declared coherent hierarchy and which changes/losses result?","linear reconciliation projection",["mint","m5"],["forecast-model"]),
        ("probabilistic-conformal","How are predictive distributions, intervals or sets distinguished and which coverage/calibration guarantee applies?","probability/prediction-set contract",["proper-scoring","conformal-regression","conformal-risk"],["model-family"]),
        ("structured-model-families","What graph, spatial, sequence, process, ranking, recommendation and online-state structures alter identity, topology and evaluation?","structured predictor family",["gnn-message-passing","sklearn-estimator"],["model-family"]),
        ("tree-kernel-neural-families","Which model representation and inference semantics distinguish tree, kernel, linear, interpretable and neural predictors?","representation-indexed predictor family",["xgboost-paper","pytorch-export","interpretable-ml"],["model-family"]),
        ("training-objective","Which loss, regularizer, constraints, sample weights and aggregation define the training objective without becoming evaluation utility?","objective algebra",["sklearn-metrics","xgboost-paper"],["model-family"]),
        ("training-algorithm","How do optimizer, solver, initialization, stopping, randomness and numeric regime produce fitted state under finite resources?","bounded training transition system",["sklearn-estimator","pytorch-export","xgboost-paper"],["training-objective"]),
        ("computational-kernels","Which linear, tensor/autodiff, tree, kernel, neighbor, factorization, graph, sequence and modality operations are pure reusable mechanisms?","typed numerical/operator algebra",["onnx-ir","gnn-message-passing","xgboost-paper"],[]),
        ("model-selection","Which candidate set, tuning data, search budget, metric vector and selection/complexity rule choose a model without contaminating final evaluation?","selection policy",["sklearn-cv","sklearn-metrics"],["split-design","training-algorithm"]),
        ("metric-evaluation","What target functional, population, weights, threshold and uncertainty make a predictive score meaningful?","metric/estimate algebra",["sklearn-metrics","proper-scoring"],["split-design"]),
        ("calibration-evaluation","How is reliability measured and recalibrated on data independent of model fitting?","calibration relation and calibrator",["sklearn-calibration"],["split-design","metric-evaluation"]),
        ("conformal-evaluation","Which exchangeability, calibration-set and loss conditions support marginal coverage or risk-control claims?","finite-sample coverage/risk oracle",["conformal-regression","conformal-risk"],["split-design"]),
        ("fairness-evaluation","Which affected groups, harms, reference population and incompatible parity criteria define a bounded fairness assessment?","socio-technical disparity evidence",["nist-bias","nist-airmf"],["metric-evaluation"]),
        ("robustness-evaluation","Which perturbation, shift, adversary, numeric and operational envelopes define robustness?","adversarial/stress-test oracle",["nist-airmf","sklearn-pitfalls"],["metric-evaluation"]),
        ("explanation-evaluation","What object is explained, for which audience and purpose, with what fidelity, stability and relevance evidence?","audience-scoped explanation claim",["interpretable-ml","shapley-limits"],["model-family"]),
        ("artifact-identity","What digest-bound closure of code, fitted state, data refs, study, configuration, environment and evidence identifies a model artifact?","content-addressed artifact manifest",["model-cards","iso-lifecycle","pytorch-export"],["training-algorithm"]),
        ("model-serialization","Which carrier, graph/operator editions, external preprocessing and numeric semantics preserve executable meaning?","editioned model representation",["onnx-ir","onnx-versioning","xgboost-model-io","pytorch-export"],["artifact-identity"]),
        ("provider-binding","How does a provider-specific estimator, artifact or runtime bind to portable requirements without owning semantics?","requirement/offer ACL",["sklearn-estimator","onnx-ir","pytorch-export","xgboost-model-io"],["model-serialization"]),
        ("scoring-execution","How do batch, request/response and ordered-stream scoring bind exact artifact, feature, output, deadline and receipt semantics?","bounded scoring state machine",["kserve-v2","onnx-ir"],["feature-semantics","artifact-identity"]),
        ("lifecycle-governance","Which candidate, trained, reviewed, approved, deployed, shadowed, superseded, revoked and retired states are legal?","governed lifecycle state machine",["iso-lifecycle","nist-airmf","model-cards"],["artifact-identity"]),
        ("monitoring-drift","Which input, feature, prediction, label, performance, calibration and harm observations support drift findings?","time-indexed monitoring/evidence model",["concept-drift","nist-airmf"],["scoring-execution","metric-evaluation"]),
        ("drift-response","Who may investigate, recalibrate, retrain, rollback, restrict or retire after a drift finding?","authority-gated policy reaction",["concept-drift","nist-airmf","iso-lifecycle"],["monitoring-drift","lifecycle-governance"]),
        ("forecast-method-facade","How are forecast estimators, evaluation and reconciliation composed without granting a facade semantic ownership?","composition-only method facade",["forecasting-book","mint","m5"],["forecast-model","forecast-reconciliation","metric-evaluation"]),
        ("causal-boundary","Why must treatment-effect identification, potential outcomes and intervention assumptions remain outside associational prediction?","causal/predictive anti-corruption boundary",["causal-whatif"],["study-target"]),
        ("predictive-finding","How does a prediction, forecast, score, explanation or drift signal remain a scoped finding until external decision authority acts?","claim-evidence-residual envelope",["nist-airmf","model-cards"],["metric-evaluation","scoring-execution"]),
    ]
    return [{"module_id":f"module.predictive.{mid}","question":question,"formalism":formalism,"source_refs":[f"source.predictive.{x}" for x in srcs],"imports":[f"module.predictive.{x}" for x in imports],"status":"EVIDENCE_BACKED_CANDIDATE_OWNER_UNRATIFIED"} for mid,question,formalism,srcs,imports in rows]


STUDY_MAP={
    "artifact_manifest":["artifact-identity"],"feature_contracts":["feature-semantics"],"label_contracts":["label-semantics"],"leakage_guard":["leakage-control"],"sampling_weights":["sampling-weighting"],"split_planner":["split-design"],"target_contracts":["study-target"],"weak_supervision":["weak-supervision"],
}
MODEL_MAP={
    "classification_models":["class-regression-count"],"regression_models":["class-regression-count"],"count_models":["class-regression-count"],"survival_models":["survival-longitudinal"],"longitudinal_models":["survival-longitudinal"],"forecast_models":["forecast-model"],"probabilistic_models":["probabilistic-conformal"],"graph_models":["structured-model-families"],"spatial_models":["structured-model-families"],"process_prediction_models":["structured-model-families"],"ranking_models":["structured-model-families"],"recommender_models":["structured-model-families"],"online_models":["structured-model-families"],"tree_models":["tree-kernel-neural-families"],"kernel_models":["tree-kernel-neural-families"],"interpretable_models":["tree-kernel-neural-families"],"neural_predictive_models":["tree-kernel-neural-families"],
}
KERNEL_MAP={
    "objective_functions":["training-objective"],"optimizers":["training-algorithm"],"linear_solvers":["computational-kernels"],"tensor_autodiff":["computational-kernels"],"tree_training_kernels":["computational-kernels"],"tree_inference_kernels":["computational-kernels"],"kernel_matrix_ops":["computational-kernels"],"neighbor_search":["computational-kernels"],"factorization_kernels":["computational-kernels"],"graph_message_passing":["computational-kernels"],"graph_sampling":["computational-kernels"],"sequence_kernels":["computational-kernels"],"image_features":["computational-kernels"],"signal_features":["computational-kernels"],
}
ASSURANCE_MAP={
    "metrics":["metric-evaluation"],"calibration":["calibration-evaluation"],"conformal_prediction":["conformal-evaluation"],"fairness_evaluation":["fairness-evaluation"],"robustness_evaluation":["robustness-evaluation"],"explanation":["explanation-evaluation"],"model_selection":["model-selection"],
}
LIFECYCLE_MAP={
    "model_serialization":["model-serialization"],"model_registry_port":["artifact-identity","lifecycle-governance"],"model_lifecycle":["lifecycle-governance"],"monitoring":["monitoring-drift"],"drift_response":["drift-response"],"batch_scoring":["scoring-execution"],"online_scoring":["scoring-execution"],"stream_scoring":["scoring-execution"],
}
PROVIDER_MAP={
    "provider_adapter_onnx":["provider-binding"],"provider_adapter_sklearn":["provider-binding"],"provider_adapter_statsmodels":["provider-binding"],"provider_adapter_torch":["provider-binding"],"provider_adapter_xgboost":["provider-binding"],
}


def modules_for_library(ref: str) -> list[str]:
    if ref.startswith("library.method_kernels.forecast"):
        tail=ref.rsplit(".",1)[1]
        maps={"forecast_estimators":["forecast-model"],"forecast_evaluation":["metric-evaluation"],"forecast_reconciliation":["forecast-reconciliation"],"forecasting_methods":["forecast-method-facade"]}
        return [f"module.predictive.{x}" for x in maps[tail]]
    if ref=="library.method_kernels.regression_glm_estimators": return ["module.predictive.class-regression-count"]
    tail=ref.split("library.predictive.",1)[1]
    if tail=="causal_effect_learners": return ["module.predictive.causal-boundary"]
    for mapping in (STUDY_MAP,MODEL_MAP,KERNEL_MAP,ASSURANCE_MAP,LIFECYCLE_MAP,PROVIDER_MAP):
        if tail in mapping: return [f"module.predictive.{x}" for x in mapping[tail]]
    raise KeyError(ref)


def laws() -> list[dict[str, Any]]:
    rows = [
        ("world-outcome-is-not-label","A world outcome, recorded observation, adjudicated label, proxy label and weakly derived label are distinct.",["datasheets","snorkel"]),
        ("prediction-time-is-not-label-time","Information available after the declared prediction time cannot become a feature merely because it exists before label recording.",["sklearn-pitfalls"]),
        ("feature-value-is-not-feature-meaning","Equal arrays do not establish equal feature definitions, grains, validity times, populations or transformations.",["datasheets","sklearn-pitfalls"]),
        ("split-is-not-random-partition","A valid evaluation split may require group, subject, time, space or dependency separation rather than random rows.",["sklearn-cv"]),
        ("validation-is-not-test","Tuning/validation data and final untouched evaluation data have different roles and identities.",["sklearn-cv","sklearn-pitfalls"]),
        ("cross-validation-is-not-deployment-evidence","Cross-validation estimates performance under its resampling design; it is not evidence for an unmatched deployment population or horizon.",["sklearn-cv"]),
        ("weak-label-is-not-ground-truth","A labeling-function aggregate remains a derived uncertain assertion even when it improves predictive performance.",["snorkel"]),
        ("model-family-is-not-algorithm","Regression, classification, forecasting or survival output semantics are not identified by the optimizer or software used to fit them.",["sklearn-estimator","statsmodels-glm"]),
        ("training-loss-is-not-evaluation-utility","The optimized objective, reported metric, proper score, business utility and harm function are separate contracts.",["sklearn-metrics","proper-scoring"]),
        ("score-is-not-threshold","A probability or decision score is not a class/action until an authorized threshold and abstention policy are applied.",["sklearn-metrics"]),
        ("accuracy-is-not-calibration","Discrimination/correct-class performance and probability reliability are distinct.",["sklearn-calibration"]),
        ("calibration-is-not-sharpness","A calibrated predictive distribution may be uninformative; sharpness is separate and subordinate to calibration.",["proper-scoring"]),
        ("aggregate-metric-is-not-subgroup-performance","An overall metric can hide variation across groups, times, sites, classes and affected parties.",["model-cards","nist-bias"]),
        ("metric-parity-is-not-fairness","One mathematical parity relation cannot prove absence of computational, human or systemic bias and harm.",["nist-bias"]),
        ("fairness-metrics-are-not-mutually-equivalent","Different fairness criteria encode different reference populations, harms and trade-offs and may conflict.",["nist-bias"]),
        ("explanation-is-not-cause","Feature attribution, importance or a local surrogate does not establish that changing a feature would change the outcome.",["interpretable-ml","shapley-limits","causal-whatif"]),
        ("explanation-is-not-faithfulness","An explanation artifact requires descriptive-accuracy evidence and cannot be presumed faithful from plausibility.",["interpretable-ml","shapley-limits"]),
        ("marginal-coverage-is-not-conditional-guarantee","Conformal marginal coverage does not promise coverage for every individual or subgroup.",["conformal-regression"]),
        ("conformal-guarantee-is-not-drift-proof","Coverage/risk guarantees depend on calibration design and assumptions and do not silently survive arbitrary distribution change.",["conformal-risk","concept-drift"]),
        ("coherence-is-not-accuracy","Forecasts that satisfy hierarchy constraints can remain inaccurate or miscalibrated.",["mint"]),
        ("forecast-is-not-prediction-without-origin","Forecast identity includes origin, horizon, frequency, information set and revision/update policy.",["forecasting-book","m5"]),
        ("benchmark-winner-is-not-universal-best","A competition ranking is scoped to its data, horizon, aggregation and scoring rule.",["m5"]),
        ("fitted-object-is-not-artifact-closure","In-memory fitted state is not the complete digest-bound closure of code, preprocessing, configuration, data references and evidence.",["model-cards","pytorch-export"]),
        ("serialization-is-not-semantic-portability","A parseable ONNX, JSON, UBJSON or provider state file does not prove equivalent preprocessing, operators or numerical outputs.",["onnx-ir","onnx-versioning","xgboost-model-io"]),
        ("model-version-is-not-ir-version","Model, IR, operator-set, provider, feature-contract and evidence editions evolve independently.",["onnx-versioning"]),
        ("ready-is-not-fit","A serving endpoint reporting ready/live does not establish model validity, feature compatibility or fitness for use.",["kserve-v2"]),
        ("batch-online-stream-not-equivalent","Batch, request/response and ordered-stream scoring have distinct ordering, state, retry, lateness, idempotency and receipt semantics.",["kserve-v2"]),
        ("prediction-is-not-decision","A prediction, forecast or risk score cannot authorize an action, denial, allocation or accusation.",["nist-airmf","model-cards"]),
        ("monitoring-signal-is-not-drift","A changed input, prediction or performance statistic is an observation; drift classification requires a declared hypothesis and evidence.",["concept-drift"]),
        ("drift-is-not-cause","Detected drift does not identify its cause, harmfulness or correct response.",["concept-drift","nist-airmf"]),
        ("drift-response-is-not-automatic-authority","Retraining, recalibration, rollback, restriction and retirement require separate policy authority.",["nist-airmf","iso-lifecycle"]),
        ("provider-is-not-model-owner","scikit-learn, statsmodels, PyTorch, XGBoost and ONNX adapters implement or translate contracts; they do not own domain target/model meaning.",["sklearn-estimator","onnx-ir","pytorch-export","xgboost-model-io"]),
        ("deterministic-seed-is-not-reproducibility","A random seed cannot reproduce training without exact data, code, configuration, dependency, hardware/numeric and scheduling closure.",["pytorch-export","iso-lifecycle"]),
        ("associational-predictor-is-not-causal-effect-learner","Predictive association does not identify treatment/intervention effects without a causal estimand and identification assumptions.",["causal-whatif"]),
        ("model-card-is-not-proof","A model card reports bounded claims and intended uses; it is not executable conformance evidence or authorization.",["model-cards"]),
    ]
    return [{"law_id":f"law.predictive.{lid}","statement":statement,"source_refs":[f"source.predictive.{x}" for x in refs],"status":"EVIDENCE_BACKED_CANDIDATE_OWNER_UNRATIFIED","completion_claim":False} for lid,statement,refs in rows]


def methods() -> list[dict[str, Any]]:
    rows = [
        ("target-definition","study","world outcome and decision setting","editioned target/horizon/population contract","requires domain owner"),
        ("label-adjudication","study","observations and evidence","label assertion with provenance","label is not world truth"),
        ("weak-supervision","study","labeling functions and unlabeled examples","probabilistic derived labels","not adjudicated ground truth"),
        ("feature-definition","study","prediction-time observations","typed feature view","availability and grain explicit"),
        ("probability-sampling","study","population and inclusion design","sample plus weights","generalization scope explicit"),
        ("grouped-splitting","study","grouped observations","group-separated partitions","group identity explicit"),
        ("temporal-backtesting","study","time-indexed observations","ordered train/test origins","future information excluded"),
        ("nested-model-selection","study","candidate/tuning/evaluation design","selected configuration plus unbiased outer estimate","search budget explicit"),
        ("leakage-analysis","study_oracle","feature/label/split information flows","leakage findings","absence requires bounded proof"),
        ("linear-regression","model_family","real target and feature design","conditional-location prediction","linearity/error assumptions scoped"),
        ("generalized-linear-model","model_family","response family/link/design","conditional functional prediction","family/link/dispersion explicit"),
        ("classification","model_family","categorical target","score/probability/class output","output type and threshold distinct"),
        ("count-regression","model_family","nonnegative count/exposure","count distribution functional","overdispersion/zero process explicit"),
        ("survival-analysis","model_family","time/event/censoring observations","hazard/survival/risk output","censoring and proportionality explicit"),
        ("longitudinal-modeling","model_family","repeated subject observations","trajectory/effect prediction","within-subject dependence explicit"),
        ("point-forecasting","forecast","origin/horizon information set","point functional forecast","functional and loss aligned"),
        ("probabilistic-forecasting","forecast","origin/horizon information set","quantile/interval/distribution forecast","calibration and sharpness distinct"),
        ("hierarchical-reconciliation","forecast","base forecasts and summing constraints","coherent forecast projection","coherence not accuracy"),
        ("forecast-combination","forecast","multiple forecast candidates","combined forecast","weight estimation and leakage explicit"),
        ("tree-ensemble","model_family","typed features/target","tree/ensemble predictor","training and inference formats distinct"),
        ("kernel-method","model_family","kernel and examples","kernel predictor","kernel validity/scaling explicit"),
        ("neural-predictor","model_family","tensor inputs/graph/state","neural predictor","architecture/provider not semantic owner"),
        ("probabilistic-model","model_family","random variables/observations","predictive distribution","conditioning and approximation explicit"),
        ("ranking","model_family","query/item/context/relevance","ordered scores/items","position/exposure/evaluation explicit"),
        ("recommendation","model_family","user/item/context/interactions","recommendation scores/slate","feedback/exposure bias explicit"),
        ("graph-prediction","model_family","typed graph and sampling view","node/edge/graph prediction","graph identity and topology explicit"),
        ("spatial-prediction","model_family","locations/support/neighborhood","spatial prediction","support/CRS/dependence explicit"),
        ("process-prediction","model_family","event/object process prefix","remaining-time/next-event/outcome prediction","process projection explicit"),
        ("online-learning","model_family","ordered feature/label stream","stateful evolving predictor","update order and delayed labels explicit"),
        ("empirical-risk-training","training","study, objective and candidate family","fitted state plus trace","training loss not utility"),
        ("gradient-optimization","training","objective/parameters","optimized candidate state","stationarity not global optimum"),
        ("autodiff","kernel","tensor program","derivative values/graph","numeric and mutation semantics explicit"),
        ("tree-training","kernel","examples/objective","tree structure/state","histogram/sampling approximations explicit"),
        ("tree-inference","kernel","tree artifact and features","scores/predictions","missing/category traversal explicit"),
        ("neighbor-search","kernel","metric/index/query","neighbor candidates","approximation/recall explicit"),
        ("factorization","kernel","matrix/tensor observations","latent factors","nonidentifiability explicit"),
        ("graph-message-passing","kernel","typed graph/features","updated representations","edge meaning not causal"),
        ("sequence-kernel","kernel","ordered sequence/state","sequence representation/output","padding/mask/order explicit"),
        ("signal-feature-extraction","kernel","sampled signal","feature vector/series","sampling/window/filter explicit"),
        ("image-feature-extraction","kernel","image/raster and transform","feature tensor","geometry/color/preprocessing explicit"),
        ("proper-score-evaluation","assurance","probabilistic predictions and outcomes","proper score estimate","target functional/population explicit"),
        ("classification-evaluation","assurance","scores/classes/labels","confusion/ranking/probability metrics","threshold/prevalence explicit"),
        ("regression-evaluation","assurance","point predictions/targets","error/fit metrics","scale/functional explicit"),
        ("probability-calibration","assurance","probabilities and independent outcomes","reliability evidence/calibrator","not accuracy"),
        ("split-conformal","assurance","model and calibration sample","prediction set/interval","marginal coverage scope explicit"),
        ("conformal-risk-control","assurance","monotone loss/calibration sample","risk-control parameter/set","assumptions explicit"),
        ("subgroup-disparity-evaluation","assurance","predictions/outcomes/groups/harms","disaggregated evidence","not total fairness"),
        ("robustness-testing","assurance","model and perturbation/shift envelope","stress findings","envelope not world totality"),
        ("posthoc-explanation","assurance","model/input/output/audience","explanation artifact","faithfulness and relevance separate"),
        ("batch-scoring","execution","finite batch and artifact","ordered batch predictions/receipt","partial/retry semantics explicit"),
        ("online-scoring","execution","request and artifact","prediction/receipt","deadline/idempotency explicit"),
        ("stream-scoring","execution","ordered event stream and state","stream predictions/receipts","lateness/replay/state explicit"),
        ("artifact-export","artifact","fitted state and manifest","editioned serialized artifact","carrier not semantic portability"),
        ("provider-adaptation","integration","portable requirement and provider offer","mapped execution/result plus loss","provider not semantic owner"),
        ("model-monitoring","lifecycle","scoring/label/outcome observations","time-indexed monitoring evidence","signal not drift"),
        ("drift-detection","lifecycle","monitoring evidence and hypothesis","drift finding","not cause or authority"),
        ("drift-response","lifecycle","drift finding and policy authority","investigate/recalibrate/retrain/rollback intent","effect requires authority"),
    ]
    return [{"method_id":f"method.predictive.{mid}","method_class":klass,"input_semantics":inp,"output_semantics":out,"authority_limit":limit,"status":"RESEARCHED_METHOD_BOUNDARY_CANDIDATE"} for mid,klass,inp,out,limit in rows]


def experts() -> list[dict[str, Any]]:
    rows = [
        ("rob-hyndman","Rob J. Hyndman",["forecasting-book","mint"],["Make origin, horizon, frequency and temporal evaluation explicit.","Treat reconciliation as a projection that enforces coherence, not accuracy."]),
        ("tilmann-gneiting","Tilmann Gneiting",["proper-scoring","sklearn-metrics"],["Align scores to the predicted functional or distribution.","Separate calibration, sharpness and decision utility."]),
        ("ryan-tibshirani","Ryan J. Tibshirani",["conformal-regression"],["Expose marginal finite-sample coverage and its exchangeability scope.","Keep conformal wrappers independent of the base estimator family."]),
        ("anastasios-angelopoulos","Anastasios N. Angelopoulos",["conformal-risk"],["Represent the controlled loss and calibration sample in the guarantee.","Do not universalize coverage or risk control beyond assumptions."]),
        ("bin-yu","Bin Yu",["interpretable-ml"],["Distinguish predictive accuracy, descriptive accuracy and audience relevance.","Prefer interpretable claims with explicit objects and validation."]),
        ("sorelle-friedler","Sorelle Friedler",["shapley-limits","nist-bias"],["Challenge feature-importance explanations against their human purpose.","Treat fairness and explanation as socio-technical, not metric-only properties."]),
        ("timnit-gebru","Timnit Gebru",["datasheets","model-cards"],["Bind dataset/model documentation to intended use, collection and disaggregated evaluation.","Documentation remains evidence-bearing claims rather than truth."]),
        ("christopher-re","Christopher Ré",["snorkel"],["Model weak-label source accuracies and correlations instead of declaring heuristic labels true.","Keep labeling programs, derived labels and discriminative models separate."]),
        ("joao-gama","João Gama",["concept-drift"],["Separate drift detection, understanding and adaptation.","Do not make every distributional change an automatic retraining trigger."]),
        ("miguel-hernan","Miguel A. Hernán",["causal-whatif"],["Define the causal estimand and intervention before effect learning.","Do not substitute predictive association for identification assumptions."]),
        ("margaret-mitchell","Margaret Mitchell",["model-cards"],["Publish intended uses, limitations and disaggregated evidence with artifacts.","A report must stay editioned and scoped to the exact model."]),
        ("tianqi-chen","Tianqi Chen",["xgboost-paper","xgboost-model-io"],["Separate scalable training mechanisms from stable model IO.","Do not confuse provider snapshots with long-lived model contracts."]),
        ("scikit-learn-community","scikit-learn community",["sklearn-pitfalls","sklearn-cv","sklearn-metrics","sklearn-estimator"],["Make fit/transform/predict roles composable and testable.","Use pipelines and correct splits to prevent leakage and preprocessing drift."]),
        ("onnx-community","ONNX community",["onnx-ir","onnx-versioning"],["Version model, IR and operator semantics independently.","Require exact operator support and reject unsupported graphs rather than guessing."]),
    ]
    return [{"expert_id":f"expert.predictive.{eid}","name":name,"contribution_refs":[f"source.predictive.{x}" for x in refs],"learnable_design_laws":lessons,"authority_limit":"The expert or community supplies bounded evidence; it does not own SAN domain meaning or operational authority."} for eid,name,refs,lessons in rows]


def innovations() -> list[dict[str, Any]]:
    rows = [
        ("dataset-documentation-as-contract",2021,["datasheets"],"Dataset composition, collection, use and distribution assumptions become an editioned evidence surface rather than tribal knowledge."),
        ("hierarchical-retail-benchmark-at-scale",2022,["m5"],"M5 tests point forecasting on 42,840 hierarchical series with explicit reconciliation and scaled-error semantics, exposing task-specific method trade-offs."),
        ("bias-management-beyond-metrics",2022,["nist-bias"],"Bias assurance expands from algorithmic parity to computational, human and systemic sources across the lifecycle."),
        ("governed-model-lifecycle-processes",2023,["iso-lifecycle","nist-airmf"],"International and government frameworks make continuous lifecycle control, TEVV, monitoring, incident response and retirement explicit obligations."),
        ("conformal-risk-control",2024,["conformal-risk"],"Finite-sample conformal machinery extends from marginal miscoverage to expected monotone-loss control under declared assumptions."),
        ("portable-versioned-model-ir",2024,["onnx-ir","onnx-versioning"],"ONNX matures independent IR, operator-set and model version coordinates with stable operator semantics and runtime-neutral graphs."),
        ("sound-export-with-shape-constraints",2025,["pytorch-export"],"Provider export IR records graph, state and shape assumptions explicitly for ahead-of-time transformation and serialization."),
        ("open-inference-protocol-v2",2026,["kserve-v2"],"A framework-neutral inference data plane standardizes health, metadata and typed inference while leaving semantic feature/output contracts external."),
    ]
    return [{"innovation_id":f"innovation.predictive.{iid}","year":year,"source_refs":[f"source.predictive.{x}" for x in refs],"core_delta":delta,"ai_or_llm_dependency":False,"status":"EVIDENCE_BACKED_INNOVATION_CANDIDATE"} for iid,year,refs,delta in rows]


AXIS_QUESTIONS = {
    "semantic_object":"Which target, label, feature, study, model family, fitted artifact, scoring run, prediction, metric, explanation, drift finding and decision are distinct subjects?",
    "semantic_role":"Which objects are observations, proxies, derived assertions, assumptions, estimators, predictors, evidence, findings, policies, offers or authorized decisions?",
    "identity_and_equality":"What identifies study, dataset cut, feature/label edition, split, fitted artifact, model carrier, provider offer, run, prediction and assurance report, under which equivalence?",
    "grain_and_cardinality":"What are the population, unit, row, group, time, feature, target, output, horizon, class, replication and subgroup multiplicities?",
    "state_and_change":"Which unfitted/fitted/reviewed/deployed/superseded/revoked states and batch/request/stream/online-update transitions are legal?",
    "time":"Which event, feature-validity, prediction, label, split, training, scoring, horizon, monitoring and decision times govern every claim?",
    "order_and_topology":"Which temporal, group, graph, hierarchy, ranking, sequence, pipeline, lifecycle and provenance orders/relations are asserted?",
    "partiality_and_uncertainty":"How are missing/censored/weak labels, abstentions, unknown classes, intervals/sets/distributions, approximation, drift and incomplete evidence represented?",
    "authority_and_trust":"Who may define targets, labels, features, groups, losses, thresholds, fairness criteria, intended use, promotion and response actions?",
    "effect_boundary":"How are pure study/model/evaluation functions separated from training/scoring execution, registry mutation, deployment, alerting and enterprise decisions?",
    "representation":"Which table/tensor/graph/model/card/ONNX/provider/receipt carriers are used, with what edition and mapping/numeric loss?",
    "composition_algebra":"Which study, model, kernel, artifact, provider, scoring, assurance and lifecycle modules compose, and how do refusals/evidence propagate?",
    "compatibility_and_evolution":"What changes preserve target, feature, label, study, model, IR/opset, provider, scoring, metric and evidence compatibility, and what requires retraining/replay?",
    "resources_and_failure":"What finite training/scoring time, memory, devices, search, batch, queue, stream state and cancellation bounds apply, and which partial results remain valid?",
    "evidence_and_conformance":"Which leakage twins, split fixtures, baselines, uncertainty estimates, subgroup tests, parity checks, conversion tests, monitoring receipts and independent providers support claims?",
    "privacy_security_safety":"What sensitive features/labels, membership/model extraction, poisoned inputs, harmful errors, affected parties and unsafe automated actions must be constrained?",
}


def boundary_findings(products_by_library: dict[str,set[str]]) -> list[dict[str, Any]]:
    unconsumed=sorted(ref for ref in LIBRARIES if not products_by_library[ref])
    model_family=sorted(ref for ref in unconsumed if ref.startswith("library.predictive.") and (ref.endswith("_models") or ref.endswith("interpretable_models")))
    provider=sorted(ref for ref in LIBRARIES if ".provider_adapter_" in ref)
    return [
        {"finding_id":"finding.predictive.fragmented-product-assembly.v1","library_refs":sorted(ref for ref in LIBRARIES if products_by_library[ref]),"current_product_refs":sorted({p for vals in products_by_library.values() for p in vals}),"candidate_disposition":"RETAIN_SEPARATE_PRODUCTS_WITH_PUBLISHED_HANDOFFS","reason":"Annotation, feature, forecasting, assurance, lifecycle, inference, search and diagnostics have distinct user/SLO/lifecycle boundaries, but their target→artifact→scoring→assurance handoffs must be explicit.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.predictive.model-development-capability.v1","library_refs":model_family,"current_product_refs":[],"candidate_disposition":"MODEL_DEVELOPMENT_CAPABILITY_OR_WORKBENCH_BOUNDARY_RESEARCH_REQUIRED","reason":"Most model-family contracts have no declared consumer. Evidence supports a reusable development/training capability seam but does not yet prove a new independently adoptable product.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.predictive.forecasting-workbench-incomplete.v1","library_refs":["library.method_kernels.forecasting_methods","library.predictive.forecast_models"],"current_product_refs":["product.forecasting_workbench"],"candidate_disposition":"ADD_EXPLICIT_MODEL_AND_COMPOSITION_IMPORTS_OR_JUSTIFY_EXCLUSION","reason":"The workbench consumes estimators, evaluation and reconciliation but not the forecast-model contract or composition facade.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.predictive.assurance-scope-incomplete.v1","library_refs":["library.predictive.conformal_prediction","library.predictive.explanation","library.predictive.model_selection"],"current_product_refs":["product.model_assurance"],"candidate_disposition":"ASSESS_ASSURANCE_IMPORTS_WITH_NON_COLLAPSE_LAWS","reason":"The current assurance product consumes calibration, fairness, metrics, robustness, monitoring and drift response but omits conformal, explanation and model-selection boundaries.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.predictive.scoring-modes.v1","library_refs":["library.predictive.batch_scoring","library.predictive.online_scoring","library.predictive.stream_scoring"],"current_product_refs":["product.online_inference"],"candidate_disposition":"SEPARATE_SCORING_MODE_CAPABILITIES_NOT_AUTOMATIC_PRODUCTS","reason":"Only online scoring is consumed. Batch and stream scoring have distinct runtime guarantees and need explicit imports or independently proven products.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.predictive.provider-adapters.v1","library_refs":provider,"current_product_refs":["product.model_lifecycle"],"candidate_disposition":"PROVIDER_OFFERS_AND_ACLS_NOT_PRODUCTS","reason":"Only the ONNX adapter is currently consumed. All five adapters are provider bindings and must never acquire model-family ownership.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.predictive.causal-effect-split.v1","library_refs":["library.predictive.causal_effect_learners"],"current_product_refs":[],"candidate_disposition":"MOVE_SEMANTIC_OWNERSHIP_TO_CAUSAL_INFERENCE_SLICE","reason":"Treatment-effect learning owns causal estimands and identification assumptions that cannot be governed by predictive model-family semantics.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.predictive.unconsumed-coverage.v1","library_refs":unconsumed,"current_product_refs":[],"candidate_disposition":"EXPLICIT_ASSEMBLY_OWNERSHIP_REVIEW_REQUIRED","reason":"Thirty-nine exact libraries have no declared product consumer in the captured graph; absence is recorded without inferring non-use or inventing lexical joins.","owner_decision":"UNRATIFIED"},
    ]


def build() -> dict[str, Any]:
    source_rows=sources(); module_rows=modules(); law_rows=laws(); method_rows=methods(); expert_rows=experts(); innovation_rows=innovations()
    contributions={row["library_id"]:row for row in load_jsonl(REGISTRY/"library-contributions.jsonl")}
    coordinate_dockets={row["library_ref"]:row for row in load_jsonl(SEM/"library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact_dockets={row["library_ref"]:row for row in load_jsonl(SEM/"p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    products_by_library={ref:set() for ref in LIBRARIES}; subjects_by_library={ref:set() for ref in LIBRARIES}
    for subject in load_jsonl(SEM/"product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl"):
        for edge in subject["concrete_bindings"]:
            ref=edge["concrete_library_ref"]
            if ref in products_by_library:
                products_by_library[ref].add(subject["product_ref"]);subjects_by_library[ref].add(subject["subject_ref"])
    target_occurrences={(row["axis"],row["library_ref"]):row for row in load_jsonl(SEM/"targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    module_by_id={row["module_id"]:row for row in module_rows}
    library_rows=[]; axis_rows=[]
    for ref in LIBRARIES:
        mods=modules_for_library(ref)
        evidence=sorted({src for mod in mods for src in module_by_id[mod]["source_refs"]})
        if ref=="library.predictive.causal_effect_learners": disposition="MOVE_SEMANTIC_OWNERSHIP_TO_CAUSAL_INFERENCE_SLICE"
        elif ref=="library.method_kernels.forecasting_methods": disposition="COMPOSITION_ONLY_NO_SEMANTIC_OWNERSHIP"
        elif ".provider_adapter_" in ref: disposition="RETAIN_PROVIDER_ACL_NOT_SEMANTIC_OWNER"
        else: disposition="RETAIN_NARROW_MODULE_BOUNDARY"
        library_rows.append({"record_kind":"predictive_analytics_library_semantic_binding_candidate","binding_id":f"binding.predictive-semantic-slice.{slug(ref)}.v1","library_ref":ref,"library_name":contributions[ref]["name"],"semantic_module_refs":mods,"evidence_refs":evidence,"exact_contract_docket_ref":exact_dockets[ref]["docket_id"],"coordinate_binding_docket_ref":coordinate_dockets[ref]["binding_docket_id"],"downstream_subject_refs":sorted(subjects_by_library[ref]),"downstream_product_refs":sorted(products_by_library[ref]),"boundary_disposition_candidate":disposition,"compiler_binding":"REFUSED","refusal_reasons":["OWNER_RATIFICATION_MISSING","MEMBER_AXIS_APPLICABILITY_UNRATIFIED","EXACT_CONTRACT_UNSELECTED","IMPLEMENTATIONS_UNQUALIFIED"],"completion_claim":False})
        for axis in AXES:
            targeted=target_occurrences.get((axis,ref))
            axis_rows.append({"record_kind":"predictive_analytics_library_axis_decision_candidate","decision_candidate_id":f"decision-candidate.predictive-axis.{slug(ref)}.{axis.replace('_','-')}.v1","library_ref":ref,"axis":axis,"semantic_module_refs":mods,"coordinate_question":AXIS_QUESTIONS[axis],"applicability_candidate":"REQUIRED_EXPLICIT_PROFILE","evidence_refs":evidence,"targeted_member_adjudication_occurrence_ref":targeted["occurrence_id"] if targeted else None,"coordinate_answers":[],"member_applicability":"PROPOSED_OWNER_REVIEW_REQUIRED","owner_decision":"UNRATIFIED","status":"EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER","canonical_gaps_closed":0,"completion_claim":False})
    findings=boundary_findings(products_by_library)
    context={"record_kind":"bounded_context_candidate","context_id":"context.predictive-analytics-semantic-slice.v1","as_of":AS_OF,"vision":"How can a declared population and prediction-time information set yield reproducible, uncertainty-aware predictions and forecasts without collapsing labels into truth, evaluation into utility, artifacts into carriers, drift into cause or predictions into decisions?","inside":["target, label, feature, sampling, split and leakage contracts","predictive and forecasting model-family semantics","training objectives, algorithms and pure kernels","metric, calibration, conformal, fairness, robustness and explanation assurance","artifact identity and model serialization","provider ACLs","batch, online and stream scoring","lifecycle, monitoring and drift response","scoped predictive finding handoff"],"outside":["causal-effect identification and intervention semantics","source ingestion and generic feature computation infrastructure","domain ownership of labels, harms, utility and thresholds","operational decision authorization","generic compute scheduling","UI and case workflow","LLM/agent orchestration"],"neighbors":[{"context_ref":"context.feature-platform","relationship":"published_language"},{"context_ref":"context.annotation-operations","relationship":"customer_supplier"},{"context_ref":"context.causal-inference","relationship":"anti_corruption_layer"},{"context_ref":"context.runtime-resource-control","relationship":"customer_supplier"},{"context_ref":"context.domain-decision-authority","relationship":"anti_corruption_layer"}],"published_language":["PredictiveTarget","LabelAssertion","FeatureContract","StudySplit","LeakageFinding","ModelFamilyRequirement","FittedArtifactManifest","ModelRepresentation","ScoringRequest","PredictionEnvelope","AssuranceFinding","DriftFinding","DriftResponseIntent"],"ratification":"WITHHELD","completion_claim":False}
    summary={"program_id":"program.predictive-analytics-semantic-slice.v1","as_of":AS_OF,"primary_or_official_sources":len(source_rows),"semantic_modules":len(module_rows),"non_collapse_laws":len(law_rows),"method_types":len(method_rows),"expert_learning_profiles":len(expert_rows),"recent_non_llm_innovations":len(innovation_rows),"bound_libraries":len(library_rows),"library_axis_decision_candidates":len(axis_rows),"product_capability_boundary_findings":len(findings),"downstream_products":len({p for vals in products_by_library.values() for p in vals}),"libraries_without_declared_product_consumer":sum(not vals for vals in products_by_library.values()),"owner_decisions":0,"exact_contracts_selected":0,"qualified_implementations":0,"canonical_gaps_closed":0,"completion_claim":False}
    return {"context":context,"sources":source_rows,"modules":module_rows,"laws":law_rows,"methods":method_rows,"experts":expert_rows,"innovations":innovation_rows,"libraries":library_rows,"axes":axis_rows,"findings":findings,"summary":summary}


def outputs() -> dict[str,str]:
    b=build(); files={
        "bounded-context.json":json.dumps(b["context"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        "primary-sources.jsonl":"".join(canonical(x)+"\n" for x in b["sources"]),
        "semantic-modules.jsonl":"".join(canonical(x)+"\n" for x in b["modules"]),
        "non-collapse-laws.jsonl":"".join(canonical(x)+"\n" for x in b["laws"]),
        "predictive-method-taxonomy.jsonl":"".join(canonical(x)+"\n" for x in b["methods"]),
        "expert-learning-profiles.jsonl":"".join(canonical(x)+"\n" for x in b["experts"]),
        "innovation-records.jsonl":"".join(canonical(x)+"\n" for x in b["innovations"]),
        "library-semantic-bindings.jsonl":"".join(canonical(x)+"\n" for x in b["libraries"]),
        "library-axis-decision-candidates.jsonl":"".join(canonical(x)+"\n" for x in b["axes"]),
        "product-capability-boundary-findings.jsonl":"".join(canonical(x)+"\n" for x in b["findings"]),
        "summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
    }
    claims={name:{"bytes":len(value.encode()),"sha256":hashlib.sha256(value.encode()).hexdigest()} for name,value in files.items()}
    files["manifest.json"]=json.dumps({"manifest_id":"manifest.predictive-analytics-semantic-slice.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n"
    return files


def main() -> int:
    for name,value in outputs().items(): (HERE/name).write_text(value)
    s=build()["summary"]
    print(f"BUILD PASS predictive analytics semantic slice: {s['semantic_modules']} modules, {s['method_types']} methods, {s['bound_libraries']} libraries and {s['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__=="__main__": raise SystemExit(main())
