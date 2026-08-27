#!/usr/bin/env python3
"""Build the evidence-backed signal, condition and event-history semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
AS_OF = "2026-08-27"
PRODUCT = "product.signal_condition_diagnostics"
AXES = ["semantic_object","semantic_role","identity_and_equality","grain_and_cardinality","state_and_change","time","order_and_topology","partiality_and_uncertainty","authority_and_trust","effect_boundary","representation","composition_algebra","compatibility_and_evolution","resources_and_failure","evidence_and_conformance","privacy_security_safety"]
NEIGHBORS = {
    "library.method_kernels.time_series_semantics", "library.method_kernels.descriptive_statistics",
    "library.method_kernels.statistical_estimators", "library.method_kernels.forecasting_methods",
    "library.qor.anomaly_detection_kernel", "library.qor.change_point_detection_kernel",
    "library.qor.signal_correlation_kernel", "library.qor.statistical_baseline_kernel",
    "library.telemetry.cross_signal_correlation",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def product_subject_rows() -> list[dict[str, Any]]:
    return load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")


def library_universe() -> list[str]:
    refs = {edge["concrete_library_ref"] for row in product_subject_rows() if row["product_ref"] == PRODUCT for edge in row["concrete_bindings"]}
    return sorted(refs | NEIGHBORS)


LIBRARIES = library_universe()


def sources() -> list[dict[str, Any]]:
    rows = [
        ("vim", "JCGM 200:2012 — International Vocabulary of Metrology", ["Joint Committee for Guides in Metrology"], 2012, "international_metrology_vocabulary", "https://www.bipm.org/documents/20126/2071204/JCGM_200_2012.pdf/f0e1ad45-d337-bbeb-53a6-15fe649d0ff1", "Separates quantity, measurand, indication, measurement result, calibration and metrological traceability.", "A measured value is not a true value, and traceability does not establish fitness or absence of mistakes."),
        ("gum", "JCGM 100:2008 — Guide to the Expression of Uncertainty in Measurement", ["Joint Committee for Guides in Metrology"], 2008, "measurement_uncertainty_guide", "https://doi.org/10.59161/JCGM100-2008E", "Defines measurement models, input quantities, standard uncertainty, covariance and combined/expanded uncertainty.", "A GUM uncertainty statement is conditional on the measurement model and input knowledge."),
        ("gum1", "JCGM GUM-1:2023 — Guide to the Expression of Uncertainty in Measurement — Introduction", ["Joint Committee for Guides in Metrology"], 2023, "current_measurement_uncertainty_guide", "https://doi.org/10.59161/JCGMGUM-1-2023", "Updates the conceptual introduction to measurement uncertainty and its applications.", "Uncertainty evaluation does not authorize a conformity or operational decision."),
        ("gum6", "JCGM GUM-6:2020 — Developing and Using Measurement Models", ["Joint Committee for Guides in Metrology"], 2020, "measurement_model_guide", "https://doi.org/10.59161/JCGMGUM-6-2020", "Makes the measurement model and model construction/evaluation explicit.", "A measurement model is not the physical system or a diagnostic mechanism."),
        ("nist-traceability", "Metrological Traceability: Frequently Asked Questions and NIST Policy", ["National Institute of Standards and Technology"], 2026, "official_metrology_guidance", "https://www.nist.gov/metrology/metrological-traceability", "Clarifies that traceability is a property of a measurement result through a documented calibration chain with uncertainty.", "A calibrated instrument alone does not make every result traceable or fit for purpose."),
        ("sensorthings", "OGC SensorThings API Part 1: Sensing 1.1", ["Open Geospatial Consortium"], 2021, "normative_observation_api", "https://docs.ogc.org/is/18-088/18-088.html", "Separates Thing, Sensor, ObservedProperty, Datastream, Observation, FeatureOfInterest and result/phenomenon times.", "A sensor observation is not the observed phenomenon or a diagnosis."),
        ("om", "OGC/ISO Observations, Measurements and Samples", ["Open Geospatial Consortium", "ISO/TC 211"], 2023, "normative_observation_model", "https://www.ogc.org/standards/om/", "Separates observation, procedure, feature of interest, observed property, result and temporal context.", "Observation provenance and result do not prove source accuracy or causal mechanism."),
        ("timeseriesml", "OGC TimeseriesML 1.3", ["Open Geospatial Consortium"], 2024, "normative_time_series_encoding", "https://www.ogc.org/standards/tsml/", "Defines an interoperable observation time-series profile and encoding.", "A time-series encoding does not select sampling, interpolation, missingness or analytical semantics."),
        ("iso8601", "ISO 8601-1:2019 — Date and Time", ["ISO/TC 154"], 2019, "international_time_standard", "https://www.iso.org/standard/70907.html", "Defines date/time representations and intervals.", "A timestamp representation does not identify clock, uncertainty, event meaning or ordering under concurrency."),
        ("ucum", "The Unified Code for Units of Measure", ["Regenstrief Institute"], 2024, "unit_code_system", "https://ucum.org/ucum", "Defines composable machine-readable unit expressions and conversion semantics.", "Convertible units do not make quantities, supports, calibration or results semantically equal."),
        ("ieee1057", "IEEE 1057 — Standard for Digitizing Waveform Recorders", ["IEEE Instrumentation and Measurement Society"], 2017, "waveform_acquisition_standard", "https://standards.ieee.org/ieee/1057/5362/", "Defines terminology and performance tests for digitizing waveform recorders.", "Digitizer conformance does not establish sensor fitness, correct installation or diagnostic validity."),
        ("iso13374-1", "ISO 13374-1:2003 — Condition Monitoring Data Processing — General Guidelines", ["ISO/TC 108/SC 5"], 2003, "condition_monitoring_architecture_standard", "https://www.iso.org/standard/21832.html", "Establishes software guidance for condition-monitoring data processing, communication and presentation.", "A reference architecture does not define every method or domain failure mode."),
        ("iso13374-2", "ISO 13374-2:2007 — Condition Monitoring Data Processing", ["ISO/TC 108/SC 5"], 2007, "condition_monitoring_information_model", "https://www.iso.org/standard/36645.html", "Defines reference information and processing models for open condition-monitoring systems.", "Processing-stage interoperability does not make findings equivalent across methods or assets."),
        ("iso17359", "ISO 17359:2018 — Condition Monitoring and Diagnostics — General Guidelines", ["ISO/TC 108/SC 5"], 2018, "condition_monitoring_program_standard", "https://www.iso.org/standard/71194.html", "Defines general procedures for establishing a machine condition-monitoring programme.", "A monitoring programme does not prove a detected condition, diagnosis or maintenance decision."),
        ("iso13379", "ISO 13379-1:2025 — Data Interpretation and Diagnostics Techniques", ["ISO/TC 108/SC 5"], 2025, "diagnostics_standard", "https://www.iso.org/standard/88027.html", "Defines common diagnostic concepts and guidance for selecting and developing diagnostic approaches.", "A diagnostic hypothesis is not a demonstrated cause or authorization to intervene."),
        ("iso13381", "ISO 13381-1:2025 — Prognostics — General Guidelines and Requirements", ["ISO/TC 108/SC 5"], 2025, "prognostics_standard", "https://www.iso.org/standard/88029.html", "Defines prognostic concepts, data, characteristics, processes and application requirements.", "A prognostic distribution is not a guaranteed failure time or maintenance authority."),
        ("mimosa", "OSA-CBM Information Architecture", ["MIMOSA"], 2010, "industry_condition_monitoring_model", "https://www.mimosa.org/mimosa-osa-cbm/", "Separates data acquisition, manipulation, state detection, health assessment, prognostics and advisory generation.", "Layer names are an integration model, not universal semantic ownership or method qualification."),
        ("scipy-signal", "SciPy Signal Processing Reference", ["SciPy project"], 2026, "official_method_provider", "https://docs.scipy.org/doc/scipy/reference/signal.html", "Implements filtering, resampling, spectral analysis, transforms, convolution and peak finding under explicit parameters.", "Provider defaults and numerical behavior do not own signal meaning or assure domain fitness."),
        ("fftw", "FFTW 3.3.11 User Manual", ["Matteo Frigo", "Steven G. Johnson"], 2025, "official_transform_provider", "https://fftw.org/fftw3_doc/", "Defines implemented DFT families, normalization conventions, layouts and execution planning.", "An FFT algorithm/provider is not a sampling theorem, spectral interpretation or diagnostic owner."),
        ("welch", "The Use of Fast Fourier Transform for the Estimation of Power Spectra", ["Peter D. Welch"], 1967, "peer_reviewed_primary_method", "https://doi.org/10.1109/TAU.1967.1161901", "Defines averaged modified periodograms for power spectral density estimation.", "A spectral estimate depends on stationarity, segmentation, windowing, overlap and normalization choices."),
        ("harris", "On the Use of Windows for Harmonic Analysis with the Discrete Fourier Transform", ["Fredric J. Harris"], 1978, "peer_reviewed_primary_method", "https://doi.org/10.1109/PROC.1978.10837", "Characterizes window functions and spectral leakage trade-offs.", "Window choice changes resolution, leakage and amplitude estimates and cannot remain ambient."),
        ("page-cusum", "Continuous Inspection Schemes", ["E. S. Page"], 1954, "peer_reviewed_primary_method", "https://doi.org/10.1093/biomet/41.1-2.100", "Defines sequential cumulative-sum change detection and run-length reasoning.", "A threshold crossing is procedure-scoped evidence, not a root-cause diagnosis."),
        ("pelt", "Optimal Detection of Changepoints With a Linear Computational Cost", ["Rebecca Killick", "Paul Fearnhead", "Idris Eckley"], 2012, "peer_reviewed_primary_method", "https://doi.org/10.1080/01621459.2012.737745", "Defines exact penalized multiple-changepoint optimization with pruning under conditions.", "A changepoint depends on cost, penalty and segment model and is not automatically an anomaly or cause."),
        ("bocpd", "Bayesian Online Changepoint Detection", ["Ryan Prescott Adams", "David J. C. MacKay"], 2007, "peer_reviewed_primary_method", "https://arxiv.org/abs/0710.3742", "Defines online posterior inference over run length under a hazard and segment predictive model.", "Posterior change probability is conditional on hazard, observation model and prior assumptions."),
        ("ucr-anomaly", "Current Time Series Anomaly Detection Benchmarks Are Flawed", ["Renjie Wu", "Eamonn Keogh"], 2021, "peer_reviewed_benchmark_audit", "https://doi.org/10.1109/TKDE.2021.3112126", "Documents benchmark defects and introduces the UCR Time Series Anomaly Archive.", "A benchmark rank does not establish production detection quality, root cause or intervention fitness."),
        ("sklearn-outlier", "Novelty and Outlier Detection", ["scikit-learn project"], 2026, "official_method_provider", "https://scikit-learn.org/stable/modules/outlier_detection.html", "Distinguishes outlier detection from novelty detection and documents estimator score/decision behavior.", "A provider's sign convention or contamination default is not a portable anomaly meaning."),
        ("river-anomaly", "River Anomaly Detection", ["River project"], 2026, "official_online_method_provider", "https://riverml.xyz/latest/api/anomaly/", "Implements online anomaly scoring, filtering and threshold-related components.", "Online update order and adaptation policy materially change the baseline and evidence."),
        ("kaplan-meier", "Nonparametric Estimation from Incomplete Observations", ["E. L. Kaplan", "Paul Meier"], 1958, "peer_reviewed_primary_method", "https://doi.org/10.1080/01621459.1958.10501452", "Defines product-limit survival estimation under censored observations.", "The estimator relies on censoring assumptions and does not identify cause or individual failure time."),
        ("cox", "Regression Models and Life-Tables", ["David R. Cox"], 1972, "peer_reviewed_primary_method", "https://doi.org/10.1111/j.2517-6161.1972.tb00899.x", "Defines proportional-hazards regression with partial likelihood.", "Hazard ratios are not survival probabilities, causal effects or constant risk differences."),
        ("fine-gray", "A Proportional Hazards Model for the Subdistribution of a Competing Risk", ["Jason Fine", "Robert Gray"], 1999, "peer_reviewed_primary_method", "https://doi.org/10.1080/01621459.1999.10474144", "Defines a subdistribution-hazard model for cumulative incidence under competing risks.", "Cause-specific and subdistribution hazards target different quantities and are not interchangeable."),
        ("aalen-johansen", "Aalen-Johansen Estimator and Multi-State Counting-Process Framework", ["Odd Aalen", "Søren Johansen"], 1978, "peer_reviewed_primary_method", "https://doi.org/10.1111/j.2517-6161.1978.tb01682.x", "Defines product-integral estimation of transition probabilities for multi-state event histories.", "State-transition estimates depend on observation and Markov/intensity assumptions."),
        ("forecasting-book", "Forecasting: Principles and Practice, 3rd edition", ["Rob J. Hyndman", "George Athanasopoulos"], 2021, "authoritative_open_text", "https://otexts.com/fpp3/", "Separates time-series structure, forecast distributions, evaluation, reconciliation and judgmental adjustment.", "A forecast is conditional, horizon- and information-cut-specific and not a prognosis or decision."),
        ("statsmodels-tsa", "Statsmodels Time Series Analysis", ["statsmodels project"], 2026, "official_method_provider", "https://www.statsmodels.org/stable/tsa.html", "Implements time-series models, filters, decomposition, statistics and forecasting.", "Provider class names and defaults do not define portable estimands or study validity."),
        ("sktime", "sktime Forecasting API", ["sktime project"], 2026, "official_method_provider", "https://www.sktime.net/en/stable/api_reference/forecasting.html", "Provides a unified forecasting interface with horizon, cutoff, update and probabilistic prediction concepts.", "API uniformity does not make all forecasting methods semantically substitutable."),
        ("prov", "PROV-O — The PROV Ontology", ["World Wide Web Consortium"], 2013, "web_recommendation", "https://www.w3.org/TR/prov-o/", "Defines entity, activity, agent, generation, use, derivation, attribution and delegation.", "Provenance does not prove signal accuracy, diagnostic correctness, causation or authority."),
        ("spc", "NIST/SEMATECH e-Handbook — Process Monitoring", ["National Institute of Standards and Technology"], 2012, "official_statistical_guidance", "https://www.itl.nist.gov/div898/handbook/pmc/pmc.htm", "Documents control charts, process monitoring and statistical assumptions.", "Statistical control is not conformance, specification fitness, fault diagnosis or absence of rare hazards."),
        ("iso5725", "ISO 5725-1:2023 — Accuracy (Trueness and Precision) of Measurement Methods", ["ISO/TC 69/SC 6"], 2023, "measurement_accuracy_standard", "https://www.iso.org/standard/69418.html", "Defines general principles and terminology for trueness and precision of measurement methods and results.", "Precision is not trueness, accuracy is not traceability and method validation is scope-specific."),
        ("opentelemetry-metrics", "OpenTelemetry Metrics Data Model", ["OpenTelemetry project"], 2026, "official_telemetry_specification", "https://opentelemetry.io/docs/specs/otel/metrics/data-model/", "Defines metric streams, points, temporality, aggregation and identity for telemetry interchange.", "Telemetry aggregation and correlation do not establish physical measurement semantics or diagnosis."),
    ]
    return [{"source_id":f"source.signal.{sid}","title":title,"authors_or_publisher":authors,"year":year,"source_kind":kind,"url":url,"bounded_implication":imp,"authority_limit":limit} for sid,title,authors,year,kind,url,imp,limit in rows]


def modules() -> list[dict[str, Any]]:
    rows = [
        ("phenomenon-measurand","What phenomenon, feature/system, quantity kind and measurand is intended?","measurement concept model",["vim","om"],[]),
        ("quantity-unit","Which quantity kind, unit, scale, reference and conversion rules give values meaning?","quantity/unit algebra",["vim","ucum"],["phenomenon-measurand"]),
        ("acquisition-profile","Which sensor, transducer, channel, range, sampling, synchronization and installation profile acquires indications?","acquisition contract",["ieee1057","sensorthings"],["phenomenon-measurand","quantity-unit"]),
        ("calibration-record","Which calibration operation, standard, conditions, validity and uncertainty relate indication to a result?","calibration relation",["vim","nist-traceability"],["acquisition-profile"]),
        ("traceability-chain","Which unbroken calibration chain and uncertainty contributions support a result?","evidence/provenance chain",["nist-traceability","gum"],["calibration-record"]),
        ("measurement-result","Which measured value, unit, uncertainty, coverage and conditions form one result?","measurement-result value object",["vim","gum","iso5725"],["quantity-unit","calibration-record"]),
        ("observation-binding","Which procedure, feature of interest, observed property, result and phenomenon/result time bind an observation?","observation relation",["om","sensorthings"],["measurement-result"]),
        ("sampled-signal","Which channel, samples, values, timestamps, clock, sampling law, units and gaps form one signal occurrence?","indexed signal model",["ieee1057","timeseriesml"],["observation-binding"]),
        ("time-index-cut","Which event/phenomenon, recording, processing, arrival, analysis-cut and decision times are distinguished?","temporal index model",["timeseriesml","iso8601"],["sampled-signal"]),
        ("missingness-irregularity","How are gaps, duplicates, jitter, late/out-of-order values, censoring and irregular sampling represented?","partial sequence model",["timeseriesml","forecasting-book"],["sampled-signal","time-index-cut"]),
        ("window-trigger","Which time/count/session/condition window and trigger create a bounded analysis occurrence?","window state machine",["timeseriesml","opentelemetry-metrics"],["time-index-cut"]),
        ("preprocessing","Which detrend, de-mean, normalization, clipping, denoise and artifact-rejection transformations occur with loss?","signal transformation pipeline",["scipy-signal","iso13374-2"],["sampled-signal"]),
        ("filtering","Which FIR/IIR/nonlinear filter, phase, state, initialization and boundary policy produces a derived signal?","linear/nonlinear operator",["scipy-signal","harris"],["preprocessing"]),
        ("resampling","Which target grid, antialias filter, interpolation and extrapolation assumptions map samples?","sampling transformation",["scipy-signal","ieee1057"],["filtering","missingness-irregularity"]),
        ("spectrum-transform","Which DFT/STFT/wavelet/analytic-signal transform, normalization, window and support create a representation?","transform algebra",["fftw","welch","harris"],["sampled-signal"]),
        ("signal-feature","Which peak, event, envelope, band power, phase, frequency, duration or morphology feature is extracted?","feature functional",["scipy-signal","welch"],["filtering","spectrum-transform"]),
        ("population-sample","Which observational unit, population, sampling frame, inclusion and dependence structure support statistics?","statistical study model",["gum","spc"],["observation-binding"]),
        ("descriptive-summary","Which location, dispersion, quantile, distribution, autocorrelation or robust summary describes a bounded sample?","statistical functional",["spc","iso5725"],["population-sample"]),
        ("baseline","Which reference population, regime, time cut, season/context, estimator, update and validity define expected behavior?","versioned baseline model",["spc","river-anomaly"],["descriptive-summary","time-index-cut"]),
        ("cross-signal-relation","Which alignment, lag, support, correlation/coherence measure and uncertainty relate two signals?","statistical relation",["welch","spc"],["sampled-signal","population-sample"]),
        ("anomaly-concept","Which point, contextual, collective, subsequence, event or regime deviation counts as anomalous for a declared task?","bounded anomaly taxonomy",["ucr-anomaly","sklearn-outlier"],["baseline"]),
        ("anomaly-score","Which detector, training/reference cut and direction produces a score with what scale and comparability?","scoring functional",["sklearn-outlier","river-anomaly"],["anomaly-concept"]),
        ("threshold-decision","Which false-alarm/miss costs, prevalence, calibration and review policy map scores to candidates?","decision rule",["page-cusum","ucr-anomaly"],["anomaly-score"]),
        ("offline-changepoint","Which segment model, cost, penalty and constraints yield retrospective changepoints?","penalized segmentation",["pelt"],["time-index-cut","baseline"]),
        ("online-change-detection","Which pre/post models, hazard, run length, threshold and detection-delay criterion define online change evidence?","sequential inference",["page-cusum","bocpd"],["time-index-cut","baseline"]),
        ("anomaly-evaluation","Which labeled events/intervals, tolerances, lead/lag, false alarms, delays and cost functional evaluate detection?","event/interval appraisal",["ucr-anomaly","page-cusum"],["anomaly-concept","threshold-decision"]),
        ("event-history","Which subject/item, origin, event types, state transitions, recurrence and risk sets form an event history?","counting-process/multi-state model",["kaplan-meier","aalen-johansen"],["time-index-cut"]),
        ("censoring-truncation","Which right/left/interval censoring, truncation, competing event and observation process make histories partial?","coarsening/observation model",["kaplan-meier","fine-gray"],["event-history"]),
        ("survival-hazard","Which survival, hazard, cumulative hazard, covariate model and estimand are computed under which assumptions?","event-history statistical model",["kaplan-meier","cox"],["event-history","censoring-truncation"]),
        ("competing-risks-multistate","Which cause-specific hazard, subdistribution hazard, cumulative incidence and transition probability is targeted?","competing-risk/multi-state model",["fine-gray","aalen-johansen"],["survival-hazard"]),
        ("forecast-handoff","Which information cut, origin, horizon, target, distribution and evaluation contract supply a forecast to diagnostics?","forecasting ACL",["forecasting-book","sktime"],["time-index-cut","sampled-signal"]),
        ("prognostics","Which degradation state, failure definition, usage profile and uncertainty support remaining-life or failure-time prognosis?","prognostic model",["iso13381","forecasting-book"],["event-history","forecast-handoff"]),
        ("condition-assessment","Which measurements, features, baselines and operating regimes support a scoped condition finding?","condition state appraisal",["iso17359","iso13374-2"],["signal-feature","baseline","anomaly-evaluation"]),
        ("diagnostic-hypothesis","Which observed symptoms, failure-mode model, alternatives and evidence support a diagnostic hypothesis?","diagnostic evidence model",["iso13379","iso17359"],["condition-assessment","cross-signal-relation"]),
        ("causal-boundary","How is fault diagnosis separated from causal identification and intervention-effect estimation?","causal anti-corruption layer",["iso13379","bocpd"],["diagnostic-hypothesis"]),
        ("analytical-finding","Which observation, method, assumptions, uncertainty, evidence, defeaters and validity scope form a finding?","claim/evidence contract",["prov","iso13379"],["condition-assessment","diagnostic-hypothesis"]),
        ("evidence-receipt","Which exact inputs, editions, parameters, runtime and outputs make an analysis occurrence reproducible?","provenance/receipt model",["prov","iso13374-2"],["analytical-finding"]),
        ("uncertainty-contract","How are measurement, sampling, model, forecast, detection and diagnostic uncertainty kept distinct and propagated?","uncertainty composition model",["gum","gum6"],["measurement-result","analytical-finding"]),
        ("case-judgment-import","How are findings, conflicts, assignments, human judgments and case state tracked without rewriting evidence?","case/judgment import",["prov","iso13379"],["analytical-finding","evidence-receipt"]),
        ("action-proposal-handoff","How is a bounded proposed action separated from authorization, execution, completion and acceptance?","decision/effect ACL",["iso13381","prov"],["case-judgment-import"]),
        ("quality-monitoring-acl","How do data-quality baselines/anomalies remain distinct from physical or business condition diagnostics?","bounded-context ACL",["spc","iso13379"],["baseline","anomaly-concept"]),
        ("telemetry-correlation-acl","How do service telemetry metric streams and trace correlation map into general signals without acquiring physical-measurement semantics?","representation/semantic ACL",["opentelemetry-metrics","vim"],["cross-signal-relation"]),
        ("method-provider-facade","How are numerical and method providers selected without selecting the study question, baseline, threshold or claim strength?","provider composition facade",["scipy-signal","statsmodels-tsa","fftw"],["evidence-receipt"]),
    ]
    return [{"module_id":f"module.signal.{mid}","owned_question":q,"formalism":f,"source_refs":[f"source.signal.{s}" for s in refs],"dependency_refs":[f"module.signal.{d}" for d in deps],"status":"EVIDENCE_BACKED_CANDIDATE_UNRATIFIED"} for mid,q,f,refs,deps in rows]


MODULE_MAP = {
    "library.measurement.calibration_record.compiler":["calibration-record"],
    "library.measurement.calibration.evaluator":["calibration-record","traceability-chain","measurement-result"],
    "library.measurement.observation_binding.compiler":["phenomenon-measurand","quantity-unit","observation-binding"],
    "library.method_kernels.time_series_semantics":["sampled-signal","time-index-cut","missingness-irregularity","window-trigger"],
    "library.pipeline.window_trigger":["window-trigger"],
    "library.method_kernels.signal_methods":["preprocessing","filtering","resampling","spectrum-transform","signal-feature"],
    "library.method_kernels.descriptive_statistics":["population-sample","descriptive-summary"],
    "library.method_kernels.statistical_estimators":["population-sample","descriptive-summary","uncertainty-contract"],
    "library.method_kernels.anomaly_baseline":["baseline"],
    "library.method_kernels.anomaly_detectors":["anomaly-concept","anomaly-score","threshold-decision","anomaly-evaluation"],
    "library.method_kernels.change_point_detectors":["offline-changepoint","online-change-detection","anomaly-evaluation"],
    "library.method_kernels.survival_event_history_estimators":["event-history","censoring-truncation","survival-hazard","competing-risks-multistate"],
    "library.predictive.survival_models":["survival-hazard","competing-risks-multistate"],
    "library.method_kernels.forecast_estimators":["forecast-handoff"],
    "library.method_kernels.forecasting_methods":["forecast-handoff","method-provider-facade"],
    "library.method_kernels.analysis_design":["population-sample","time-index-cut","anomaly-evaluation"],
    "library.method_kernels.analytical_finding_contract":["analytical-finding"],
    "library.cbv.uncertainty_contracts":["uncertainty-contract"],
    "library.method_kernels.numerical_kernel_facade":["method-provider-facade"],
    "library.lpe.evidence-bundle":["evidence-receipt"],
    "library.lpe.prov-statement-algebra":["evidence-receipt"],
    "library.lpe.provenance-assertion":["evidence-receipt"],
    "library.lpe.provenance-bundle":["evidence-receipt"],
    "library.lpe.runtime-receipt-core":["evidence-receipt"],
    "library.cbv.analytical_case_reducer":["case-judgment-import"],
    "library.cbv.decision_handoff_algebra":["case-judgment-import","action-proposal-handoff"],
    "library.csp.decision.decision-ledger":["case-judgment-import"],
    "library.csp.decision.judgment-port":["case-judgment-import"],
    "library.csp.decision.action-proposal":["action-proposal-handoff"],
    "library.qor.sampling_measurement_kernel":["population-sample","measurement-result"],
    "library.qor.statistical_baseline_kernel":["quality-monitoring-acl","baseline"],
    "library.qor.anomaly_detection_kernel":["quality-monitoring-acl","anomaly-concept","threshold-decision"],
    "library.qor.change_point_detection_kernel":["quality-monitoring-acl","offline-changepoint","online-change-detection"],
    "library.qor.signal_correlation_kernel":["quality-monitoring-acl","cross-signal-relation"],
    "library.telemetry.cross_signal_correlation":["telemetry-correlation-acl","cross-signal-relation"],
}


def laws() -> list[dict[str, Any]]:
    texts = [
        "A phenomenon, feature of interest, observed property, measurand, indication and measurement result are distinct.",
        "A sensor or instrument is not an observation, measurement result or traceability claim.",
        "Calibration is not adjustment, verification, validation or proof of fitness.",
        "Metrological traceability belongs to a result and declared chain, not merely to an instrument or laboratory.",
        "A measured value without unit, uncertainty, conditions and measurand is not a complete measurement result.",
        "Precision is not trueness; repeatability is not reproducibility; either is not universal accuracy.",
        "A timestamp is not event identity, clock identity, temporal uncertainty or causal order.",
        "Event time, observation time, recording time, arrival time, processing time, analysis cut and decision time are distinct.",
        "A time series is not merely an ordered vector; index, clock, support, gaps, revisions and units are semantic inputs.",
        "Missing, not observed, censored, below detection, invalid, late and zero are distinct states.",
        "Resampling is not observation and interpolation does not create measured evidence.",
        "Filtering changes signal content and phase unless preservation laws say otherwise.",
        "A DFT or FFT output is not a spectrum interpretation without sampling, normalization, window and support.",
        "Spectral leakage, resolution and amplitude bias depend on explicit window and segment choices.",
        "A peak is an algorithmic feature under declared prominence, width and boundary rules, not a physical event.",
        "A descriptive summary does not identify a population mechanism or future distribution.",
        "A baseline is an editioned reference population/regime, not timeless normality.",
        "Online baseline adaptation can absorb faults and must be a governed state transition.",
        "Correlation, cross-correlation, coherence and coincident timing do not prove causation or common mechanism.",
        "Lag maximizing correlation is not necessarily physical delay or causal direction.",
        "An outlier, novelty, anomaly, change point, drift, defect, fault and incident are distinct.",
        "An anomaly score has no portable direction or probability meaning without a declared contract.",
        "A threshold is a decision rule with false-alarm/miss costs and authority, not a property of the observation.",
        "A changepoint is conditional on segment model, cost, penalty or hazard and is not automatically an anomaly.",
        "Retrospective segmentation and online quickest detection target different evidence and latency trade-offs.",
        "Detection delay, point precision/recall, interval overlap and event utility are different evaluation objectives.",
        "Point-adjusted anomaly metrics can overstate performance and require explicit justification.",
        "A benchmark score does not establish production fitness or domain validity.",
        "Censoring is not event absence; truncation is not censoring; competing events are not ordinary missingness.",
        "Survival probability, hazard, cumulative hazard, cumulative incidence and subdistribution hazard are distinct estimands.",
        "A hazard ratio is not a risk ratio, survival probability, expected lifetime or causal effect.",
        "Cause-specific and subdistribution hazard models are not interchangeable.",
        "A forecast is not a prognosis; a prognosis is not a guaranteed event time.",
        "Forecast origin, information cut, horizon, target edition and evaluation window are explicit identities.",
        "Remaining useful life depends on failure definition, usage regime, censoring and model validity.",
        "Condition assessment is not diagnosis; diagnosis is not causal proof; prognosis is not authorization.",
        "A diagnostic hypothesis must preserve alternatives, defeaters and evidence scope.",
        "Root-cause language in diagnostics does not substitute for a causal identification contract.",
        "An analytical finding is not a business fact, policy decision or authority to act.",
        "Human judgment records an authority-scoped appraisal; it is not automatic truth.",
        "An action proposal is not authorization, execution, completion or acceptance.",
        "Data-quality anomalies and physical-condition anomalies may share methods but not bounded-context meaning.",
        "Telemetry metric identity and aggregation do not imply physical quantity or calibration semantics.",
        "Provenance is not correctness, traceability, diagnosis, cause or decision authority.",
        "Provider or model identity is not semantic ownership; a facade cannot choose hidden baselines or thresholds.",
        "Runtime success does not establish analytical validity and analytical validity does not establish action fitness.",
        "Resource exhaustion must refuse explicitly rather than shorten a window or weaken guarantees silently.",
        "Late and out-of-order data must follow an explicit revision/retraction policy.",
        "Model, method, calibration, sensor, baseline, threshold and study editions are digest-bound inputs.",
        "No LLM or agent output is measurement, diagnostic, causal, approval or effect authority by itself.",
    ]
    return [{"law_id":f"law.signal.non-collapse.{i:02d}","law":text,"status":"CANDIDATE_UNRATIFIED"} for i,text in enumerate(texts,1)]


def methods() -> list[dict[str, Any]]:
    groups = {
        "measurement":["sensor_acquisition","calibration_curve_evaluation","traceability_chain_appraisal","uncertainty_propagation","unit_conversion","observation_binding","sampling_plan","synchronization_and_clock_correction"],
        "signal_processing":["detrend_and_demean","fir_filter","iir_filter","zero_phase_filter","resample_polyphase","interpolate_irregular","fft_dft","welch_psd","stft","wavelet_transform","hilbert_envelope","cross_correlation","coherence","peak_detection","event_segmentation"],
        "statistics_baselines":["robust_descriptive_statistics","autocorrelation","seasonal_decomposition","control_chart","static_reference_baseline","rolling_baseline","contextual_baseline","cross_signal_lag_analysis"],
        "anomaly_change":["point_anomaly_score","contextual_anomaly_score","collective_subsequence_anomaly","novelty_detection","threshold_calibration","cusum","ewma_change_detection","pelt","binary_segmentation","bayesian_online_changepoint","change_interval_consolidation","detection_delay_evaluation"],
        "event_history":["kaplan_meier","nelson_aalen","cox_proportional_hazards","accelerated_failure_time","competing_risk_cumulative_incidence","fine_gray","aalen_johansen","recurrent_event_model","multi_state_model"],
        "forecast_prognostics":["point_forecast","quantile_forecast","distribution_forecast","forecast_backtest","remaining_useful_life","failure_probability_horizon","degradation_trend"],
        "diagnosis_review":["condition_indicator_appraisal","symptom_fault_mapping","diagnostic_hypothesis_ranking","alternative_hypothesis_preservation","finding_sealing","human_adjudication","action_proposal_handoff","reprocessing_and_retraction"],
    }
    return [{"method_id":f"method.signal.{name.replace('_','-')}","method_family":family,"method_name":name,"semantic_preconditions_required":True,"provider_is_semantic_owner":False,"status":"METHOD_BOUNDARY_CANDIDATE"} for family,names in groups.items() for name in names]


def experts() -> list[dict[str, Any]]:
    rows = [
        ("charles-ehrlich","Charles D. Ehrlich",["vim","nist-traceability"],["Treat traceability as a property of a result through a declared chain.","Keep calibration, uncertainty and fitness separate."]),
        ("walter-bich","Walter Bich",["gum","gum1"],["Make the measurement model and uncertainty contributors explicit.","Do not turn uncertainty calculation into conformity authority."]),
        ("steve-liang","Steve Liang",["sensorthings"],["Separate sensors, observed properties, datastreams, observations and features of interest.","Preserve phenomenon time and result time."]),
        ("alan-oppenheim","Alan V. Oppenheim",["scipy-signal","fftw"],["Model signals and systems through explicit transforms and operators.","Sampling, phase and boundary assumptions belong in contracts."]),
        ("fredric-harris","Fredric J. Harris",["harris"],["Window selection determines leakage and resolution trade-offs.","Never leave spectral normalization and window semantics ambient."]),
        ("peter-welch","Peter D. Welch",["welch"],["Expose segment, overlap, window and averaging choices in spectral estimates.","A PSD estimate remains an estimator with finite-sample uncertainty."]),
        ("rebecca-killick","Rebecca Killick",["pelt"],["Separate segment cost, penalty and search algorithm.","Exact optimization under assumptions does not make the segment model true."]),
        ("paul-fearnhead","Paul Fearnhead",["pelt","bocpd"],["Distinguish retrospective multiple-change segmentation from online detection.","Represent model and computational approximations explicitly."]),
        ("idris-eckley","Idris Eckley",["pelt"],["Evaluate change methods against the exact change object and tolerance.","Keep domain interpretation outside mathematical segmentation."]),
        ("ryan-adams","Ryan Prescott Adams",["bocpd"],["Model run length, hazard and predictive distribution explicitly.","Posterior change probability is conditional evidence."]),
        ("david-mackay","David J. C. MacKay",["bocpd"],["Use probabilistic models to expose assumptions and uncertainty.","Bayesian coherence does not eliminate model misspecification."]),
        ("eamonn-keogh","Eamonn Keogh",["ucr-anomaly"],["Audit anomaly benchmarks for leakage, triviality, mislabels and unrealistic evaluation.","Do not infer progress from flawed benchmark scores."]),
        ("edward-kaplan","E. L. Kaplan",["kaplan-meier"],["Treat censoring as an observation-process assumption.","Product-limit estimates describe populations, not individual event times."]),
        ("paul-meier","Paul Meier",["kaplan-meier"],["Preserve risk-set changes and incomplete follow-up.","Missing follow-up is not failure absence."]),
        ("david-cox","David R. Cox",["cox"],["Separate baseline hazard, covariate effect and partial likelihood.","Hazard ratios require careful estimand interpretation."]),
        ("odd-aalen","Odd Aalen",["aalen-johansen"],["Model event histories through counting processes and state transitions.","Multi-state transition probabilities differ from single-event survival."]),
    ]
    return [{"expert_id":f"expert.signal.{eid}","name":name,"source_refs":[f"source.signal.{s}" for s in refs],"lessons_for_composable_platform":lessons,"authority_limit":"Expert work constrains candidate semantics and methods; the expert is not the SAN semantic owner or qualification authority.","status":"RESEARCHED_PROFILE"} for eid,name,refs,lessons in rows]


def innovations() -> list[dict[str, Any]]:
    rows = [
        ("sensor-things-11",2021,"SensorThings 1.1 standardized observation streams while preserving sensor, property, feature and temporal roles.",["sensorthings"]),
        ("ucr-anomaly-audit",2021,"The UCR anomaly benchmark audit showed that flawed datasets and metrics can create an illusion of method progress.",["ucr-anomaly"]),
        ("gum1",2023,"GUM-1 refreshed the conceptual foundation for expressing measurement uncertainty across scientific and enterprise use.",["gum1"]),
        ("iso5725-2023",2023,"ISO 5725-1:2023 refreshed trueness/precision terminology for measurement methods and results.",["iso5725"]),
        ("timeseriesml-13",2024,"TimeseriesML 1.3 advanced interoperable observation-series encoding without prescribing analytical defaults.",["timeseriesml"]),
        ("iso13379-2025",2025,"ISO 13379-1:2025 updated common diagnostic concepts and method-selection guidance for machine systems.",["iso13379"]),
        ("iso13381-2025",2025,"ISO 13381-1:2025 updated prognostics requirements and the data/process concepts needed for bounded prognosis.",["iso13381"]),
        ("gum-nonlinearity-2026",2026,"The GUM amendment on nonlinearity makes measurement-model limitations and propagation choices more explicit.",["gum","gum1"]),
    ]
    return [{"innovation_id":f"innovation.signal.{iid}","year":year,"innovation":text,"source_refs":[f"source.signal.{s}" for s in refs],"ai_or_llm_dependency":False,"boundary_implication":"Encode as an editioned measurement, method, evaluation or evidence module; do not create an ambient AI product or transfer authority to a provider.","status":"EVIDENCE_BACKED_NON_LLM_INNOVATION"} for iid,year,text,refs in rows]


AXIS_QUESTIONS = {
    "semantic_object":"Which phenomenon, measurand, observation, measurement result, signal, window, baseline, feature, anomaly, changepoint, event history, forecast, prognosis, diagnostic hypothesis, finding or action proposal is owned?",
    "semantic_role":"Which roles are asset/subject, sensor, calibration authority, observation producer, analyst, method provider, baseline owner, diagnostician, reviewer, decision authority and effect executor?",
    "identity_and_equality":"What makes sensor/channel, calibration, observation, sample, series, clock, window, baseline, model, threshold, finding, event history and case editions equal or distinct?",
    "grain_and_cardinality":"Are semantics per indication, result, sample, channel, window, event, interval, regime, subject, risk set, population, asset, case or run, with what multiplicity and completeness?",
    "state_and_change":"What legal acquired, calibrated, bound, windowed, scored, detected, appraised, diagnosed, reviewed, proposed, retracted and superseded transitions exist?",
    "time":"How are phenomenon/event, acquisition, recording, arrival, processing, analysis-cut, detection, decision, calibration-validity and prognosis-horizon times separated?",
    "order_and_topology":"Which sample sequence, partial order, channel alignment, lag relation, segment partition, event history, risk set, state-transition graph and evidence graph constrain analysis?",
    "partiality_and_uncertainty":"How are missing/late/invalid samples, censoring, truncation, measurement uncertainty, score ambiguity, false-alarm risk, forecast distributions and unresolved diagnosis represented?",
    "authority_and_trust":"Who defines measurands, calibration validity, baselines, thresholds, failure modes, claim strength, review, action proposals, authorization, retraction and acceptance?",
    "effect_boundary":"How are pure measurement binding, transforms, estimation, detection and appraisal separated from acquisition I/O, alerting, case mutation, action authorization and physical effect?",
    "representation":"Which observation, time-series, tensor, window, spectrum, feature, event-history, model, finding, provenance and receipt carriers are used at what edition and loss?",
    "composition_algebra":"How do observation, calibration, windows, transforms, baselines, detectors, evaluation, diagnosis, evidence and decision handoff compose and propagate uncertainty/refusals?",
    "compatibility_and_evolution":"What sensor, clock, calibration, unit, sampling, window, model, baseline, threshold, taxonomy and policy changes preserve comparability or force replay/reappraisal?",
    "resources_and_failure":"What sample, channel, memory, state, latency, transform, search, bootstrap, model, review and retention budgets apply, and when must work refuse?",
    "evidence_and_conformance":"Which calibration chains, synthetic signals, invariance fixtures, benchmark audits, labeled event intervals, simulations, negative twins and independent providers support each bounded claim?",
    "privacy_security_safety":"How are sensitive signals, occupancy/health inference, sensor spoofing, tampering, alert fatigue, missed hazards, unsafe prognosis and unauthorized interventions controlled?",
}


def boundary_findings(products: dict[str,set[str]]) -> list[dict[str,Any]]:
    return [
        {"finding_id":"finding.signal.product-retain.v1","library_refs":sorted(ref for ref in LIBRARIES if PRODUCT in products[ref]),"current_product_refs":[PRODUCT],"candidate_disposition":"RETAIN_SIGNAL_CONDITION_DIAGNOSTICS_PRODUCT","reason":"Observation binding through signal analysis, anomaly/change/event-history findings, diagnosis, exception case and action-proposal handoff forms one operational diagnostic lifecycle while effect authority remains outside.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.signal.time-series-foundation.v1","library_refs":["library.method_kernels.time_series_semantics"],"current_product_refs":["product.forecasting_workbench"],"candidate_disposition":"IMPORT_SHARED_TIME_SERIES_FOUNDATION","reason":"Signal diagnostics requires index, cut, gaps, revisions and temporal split semantics but currently omits the shared library from its declared bindings.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.signal.statistics-foundation.v1","library_refs":["library.method_kernels.descriptive_statistics","library.method_kernels.statistical_estimators"],"current_product_refs":[],"candidate_disposition":"SHARED_STATISTICAL_PRIMITIVES_PRODUCT_BOUNDARY_UNPROVEN","reason":"Statistics support baselines, uncertainty and evaluation across products; no standalone product lifecycle is established by the captured graph.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.signal.forecast-acl.v1","library_refs":["library.method_kernels.forecast_estimators","library.method_kernels.forecasting_methods"],"current_product_refs":[PRODUCT,"product.forecasting_workbench"],"candidate_disposition":"FORECAST_INFORMATION_HANDOFF_NOT_DIAGNOSTIC_OWNERSHIP","reason":"A forecast is origin/horizon/target-specific predictive output; diagnostics may consume it but does not own forecast selection, evaluation, reconciliation or publication lifecycle.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.signal.survival-acl.v1","library_refs":["library.method_kernels.survival_event_history_estimators","library.predictive.survival_models"],"current_product_refs":[PRODUCT],"candidate_disposition":"EVENT_HISTORY_SEMANTICS_WITH_PREDICTIVE_MODEL_IMPORT","reason":"Event/censoring/risk-set estimands belong to event-history semantics; predictive model families may implement conditional models without owning event meaning.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.signal.quality-homonyms.v1","library_refs":["library.qor.statistical_baseline_kernel","library.qor.anomaly_detection_kernel","library.qor.change_point_detection_kernel","library.qor.signal_correlation_kernel"],"current_product_refs":["product.data_quality_operations"],"candidate_disposition":"KEEP_QUALITY_CONTEXT_SPECIALIZATIONS_SEPARATE_IMPORT_SHARED_METHODS","reason":"Quality baselines and anomalies concern data-contract observations and remediation policy; physical/business signal condition findings have different subjects, authorities and effects.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.signal.telemetry-acl.v1","library_refs":["library.telemetry.cross_signal_correlation"],"current_product_refs":[],"candidate_disposition":"TELEMETRY_SPECIALIZATION_IMPORTS_GENERAL_SIGNAL_RELATIONS","reason":"Service metric-stream identity, aggregation and trace context remain telemetry-owned and cannot inherit physical measurand/calibration semantics.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.signal.causal-seam.v1","library_refs":["library.method_kernels.analytical_finding_contract","library.cbv.decision_handoff_algebra"],"current_product_refs":[PRODUCT],"candidate_disposition":"DIAGNOSTIC_HYPOTHESIS_TO_CAUSAL_STUDY_ACL","reason":"Correlation, change timing and fault-pattern diagnosis can rank hypotheses but do not identify intervention effects or prove root cause.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.signal.action-authority.v1","library_refs":["library.csp.decision.action-proposal","library.csp.decision.decision-ledger","library.csp.decision.judgment-port"],"current_product_refs":[PRODUCT],"candidate_disposition":"EVIDENCE_AND_PROPOSAL_HANDOFF_ONLY","reason":"Diagnostics may propose and record review; authorization, execution, completion and acceptance remain decision/effect-context responsibilities.","owner_decision":"UNRATIFIED"},
        {"finding_id":"finding.signal.method-facades.v1","library_refs":["library.method_kernels.numerical_kernel_facade","library.method_kernels.forecasting_methods"],"current_product_refs":[PRODUCT],"candidate_disposition":"COMPOSITION_ONLY_NO_SEMANTIC_OWNERSHIP","reason":"Facades route qualified numerical/method providers and cannot choose hidden measurands, baselines, thresholds, estimands or claim strength.","owner_decision":"UNRATIFIED"},
    ]


def build() -> dict[str,Any]:
    ss,ms,ls,methods_rows,es,ins=sources(),modules(),laws(),methods(),experts(),innovations()
    contributions={r["library_id"]:r for r in load_jsonl(REGISTRY/"library-contributions.jsonl")}
    coord={r["library_ref"]:r for r in load_jsonl(SEM/"library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact={r["library_ref"]:r for r in load_jsonl(SEM/"p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    products={ref:set() for ref in LIBRARIES}; subjects={ref:set() for ref in LIBRARIES}
    for row in product_subject_rows():
        for edge in row["concrete_bindings"]:
            ref=edge["concrete_library_ref"]
            if ref in products: products[ref].add(row["product_ref"]);subjects[ref].add(row["subject_ref"])
    targeted={(r["axis"],r["library_ref"]):r for r in load_jsonl(SEM/"targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    modby={r["module_id"]:r for r in ms}; libs=[]; axes=[]
    for ref in LIBRARIES:
        mods=[f"module.signal.{x}" for x in MODULE_MAP[ref]]; evidence=sorted({s for m in mods for s in modby[m]["source_refs"]})
        ed=exact.get(ref);cd=coord.get(ref)
        if ref in {"library.method_kernels.numerical_kernel_facade","library.method_kernels.forecasting_methods"}: disposition="COMPOSITION_FACADE_ONLY_NO_SEMANTIC_OWNERSHIP"
        elif ref in NEIGHBORS: disposition="RETAIN_FORMALISM_NEIGHBOR_WITH_EXPLICIT_ACL"
        else: disposition="RETAIN_DECLARED_PRODUCT_DEPENDENCY_WITH_NARROW_OWNER"
        libs.append({"record_kind":"signal_condition_library_semantic_binding_candidate","binding_id":f"binding.signal-semantic-slice.{slug(ref)}.v1","library_ref":ref,"library_name":contributions[ref]["name"],"semantic_module_refs":mods,"evidence_refs":evidence,"exact_contract_docket_ref":ed["docket_id"] if ed else None,"coordinate_binding_docket_ref":cd["binding_docket_id"] if cd else None,"downstream_contract_route":"ROUTED" if ed and cd else "MISSING_P5_AND_COORDINATE_DOCKET_TYPED_VACANCY","downstream_subject_refs":sorted(subjects[ref]),"downstream_product_refs":sorted(products[ref]),"boundary_disposition_candidate":disposition,"compiler_binding":"REFUSED","refusal_reasons":(["DOWNSTREAM_CONTRACT_ROUTE_MISSING"] if not ed or not cd else [])+["OWNER_RATIFICATION_MISSING","MEMBER_AXIS_APPLICABILITY_UNRATIFIED","EXACT_CONTRACT_UNSELECTED","IMPLEMENTATIONS_UNQUALIFIED"],"completion_claim":False})
        for axis in AXES:
            t=targeted.get((axis,ref)); axes.append({"record_kind":"signal_condition_library_axis_decision_candidate","decision_candidate_id":f"decision-candidate.signal-axis.{slug(ref)}.{axis.replace('_','-')}.v1","library_ref":ref,"axis":axis,"semantic_module_refs":mods,"coordinate_question":AXIS_QUESTIONS[axis],"applicability_candidate":"REQUIRED_EXPLICIT_PROFILE","evidence_refs":evidence,"targeted_member_adjudication_occurrence_ref":t["occurrence_id"] if t else None,"coordinate_answers":[],"member_applicability":"PROPOSED_OWNER_REVIEW_REQUIRED","owner_decision":"UNRATIFIED","status":"EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER","canonical_gaps_closed":0,"completion_claim":False})
    findings=boundary_findings(products)
    context={"record_kind":"bounded_context_candidate","context_id":"context.signal-condition-semantic-slice.v1","as_of":AS_OF,"vision":"How can calibrated observations and event histories be transformed into bounded signal, anomaly, change, prognosis and diagnostic findings without collapsing measurement into truth, correlation into cause, anomaly into fault, prognosis into certainty or a proposed action into authority?","inside":["measurand, observation, calibration and uncertainty binding","sampled-signal and time-index semantics","windows, filters, resampling, transforms and signal features","statistical summaries, baselines and cross-signal relations","anomaly scoring, thresholds and change detection","event-history, censoring, survival, hazards and competing risks","forecast/prognostic information handoff","condition assessment, diagnostic hypotheses and evidence","case review and non-authoritative action proposal"],"outside":["sensor/device actuation and acquisition runtime ownership","generic telemetry and data-quality semantic ownership","forecasting workbench lifecycle","causal-effect identification and root-cause proof","maintenance/action authorization and physical effect","generic compute/storage/orchestration","LLM or agent authority"],"neighbors":[{"context_ref":"context.measurement-metrology","relationship":"customer_supplier"},{"context_ref":"context.forecasting-workbench","relationship":"anti_corruption_layer"},{"context_ref":"context.predictive-analytics-semantic-slice","relationship":"anti_corruption_layer"},{"context_ref":"context.causal-inference-semantic-slice","relationship":"anti_corruption_layer"},{"context_ref":"context.data-quality-operations","relationship":"anti_corruption_layer"},{"context_ref":"context.telemetry","relationship":"anti_corruption_layer"},{"context_ref":"context.decision-effect-authority","relationship":"published_language"}],"published_language":["MeasurementResult","ObservationBinding","SampledSignal","InformationCut","SignalWindow","BaselineEdition","SignalFeature","AnomalyScore","ThresholdProfile","AnomalyFinding","ChangePointFinding","EventHistory","CensoringProfile","SurvivalEstimate","HazardEstimate","CompetingRiskEstimate","ForecastHandoff","PrognosticFinding","DiagnosticHypothesis","ConditionFinding","AnalysisReceipt","ActionProposalHandoff"],"ratification":"WITHHELD","completion_claim":False}
    summary={"program_id":"program.signal-condition-semantic-slice.v1","as_of":AS_OF,"primary_or_official_sources":len(ss),"semantic_modules":len(ms),"non_collapse_laws":len(ls),"method_types":len(methods_rows),"expert_learning_profiles":len(es),"recent_non_llm_innovations":len(ins),"bound_libraries":len(libs),"declared_product_libraries":sum(PRODUCT in products[r] for r in LIBRARIES),"formalism_neighbor_libraries":len(NEIGHBORS),"libraries_without_declared_product_consumer":sum(not products[r] for r in LIBRARIES),"missing_downstream_contract_routes":sum(r["downstream_contract_route"].startswith("MISSING") for r in libs),"library_axis_decision_candidates":len(axes),"product_capability_boundary_findings":len(findings),"owner_decisions":0,"exact_contracts_selected":0,"qualified_implementations":0,"canonical_gaps_closed":0,"completion_claim":False}
    return {"context":context,"sources":ss,"modules":ms,"laws":ls,"methods":methods_rows,"experts":es,"innovations":ins,"libraries":libs,"axes":axes,"findings":findings,"summary":summary}


def outputs() -> dict[str,str]:
    b=build(); files={"bounded-context.json":json.dumps(b["context"],ensure_ascii=False,sort_keys=True,indent=2)+"\n","primary-sources.jsonl":"".join(canonical(x)+"\n" for x in b["sources"]),"semantic-modules.jsonl":"".join(canonical(x)+"\n" for x in b["modules"]),"non-collapse-laws.jsonl":"".join(canonical(x)+"\n" for x in b["laws"]),"signal-method-taxonomy.jsonl":"".join(canonical(x)+"\n" for x in b["methods"]),"expert-learning-profiles.jsonl":"".join(canonical(x)+"\n" for x in b["experts"]),"innovation-records.jsonl":"".join(canonical(x)+"\n" for x in b["innovations"]),"library-semantic-bindings.jsonl":"".join(canonical(x)+"\n" for x in b["libraries"]),"library-axis-decision-candidates.jsonl":"".join(canonical(x)+"\n" for x in b["axes"]),"product-capability-boundary-findings.jsonl":"".join(canonical(x)+"\n" for x in b["findings"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"}
    claims={n:{"bytes":len(v.encode()),"sha256":hashlib.sha256(v.encode()).hexdigest()} for n,v in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.signal-condition-semantic-slice.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n";return files


def main() -> int:
    for n,v in outputs().items():(HERE/n).write_text(v)
    s=build()["summary"];print(f"BUILD PASS signal condition semantic slice: {s['semantic_modules']} modules, {s['method_types']} methods, {s['bound_libraries']} libraries and {s['library_axis_decision_candidates']} unresolved axis decisions");return 0


if __name__=="__main__":raise SystemExit(main())
