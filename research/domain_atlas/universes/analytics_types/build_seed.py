#!/usr/bin/env python3
"""Build a broad, honest hypothesis queue of named analytical practices."""

from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent


FAMILIES = [
    {
        "id": "descriptive_profile",
        "name": "Descriptive, comparative and profile analytics",
        "kind": "study",
        "intent": ["describe", "compare", "decompose"],
        "basis": ["intent", "output_contract"],
        "evidence": ["evidence.nist.eda"],
        "practices": [
            "univariate profiling", "distribution profiling", "frequency analysis", "cross-tabulation",
            "multidimensional slice and dice", "drill-down analysis", "roll-up analysis", "cohort analysis",
            "funnel analysis", "Pareto analysis", "concentration analysis", "diversity analysis",
            "inequality analysis", "benchmarking", "peer-group comparison", "variance-to-plan analysis",
            "contribution analysis", "mix-shift decomposition", "index-number analysis", "trend description"
        ]
    },
    {
        "id": "exploratory",
        "name": "Exploratory and structure-discovery analytics",
        "kind": "study",
        "intent": ["explore", "discover", "diagnose"],
        "basis": ["intent", "study_design"],
        "evidence": ["evidence.nist.eda"],
        "practices": [
            "exploratory data analysis", "missingness-pattern exploration", "outlier exploration",
            "leverage and influence exploration", "association exploration", "dependence exploration",
            "correlation structure exploration", "latent-structure exploration", "cluster-tendency assessment",
            "cluster analysis", "principal-component exploration", "factor analysis", "correspondence analysis",
            "multidimensional scaling", "manifold exploration", "projection-pursuit analysis",
            "robust exploratory analysis", "graphical residual exploration", "hypothesis-generation analysis"
        ]
    },
    {
        "id": "inferential",
        "name": "Statistical inference",
        "kind": "method",
        "intent": ["estimate", "test", "generalize"],
        "basis": ["study_design", "assumption", "uncertainty", "evidence"],
        "evidence": ["evidence.nist.statistics"],
        "practices": [
            "point estimation", "interval estimation", "Bayesian estimation", "hypothesis testing",
            "equivalence testing", "non-inferiority testing", "superiority testing", "goodness-of-fit testing",
            "distribution-free inference", "permutation inference", "bootstrap inference", "randomization inference",
            "multiple-comparison control", "false-discovery-rate control", "sequential inference",
            "variance-component analysis", "hierarchical inference", "meta-analysis", "small-area estimation",
            "empirical-Bayes estimation", "sensitivity analysis for statistical conclusions"
        ]
    },
    {
        "id": "measurement_uncertainty",
        "name": "Measurement, calibration and uncertainty analytics",
        "kind": "measurement",
        "intent": ["measure", "calibrate", "quantify uncertainty"],
        "basis": ["input_contract", "uncertainty", "evidence"],
        "evidence": ["evidence.nist.measurement"],
        "practices": [
            "measurement-system analysis", "gage repeatability and reproducibility", "instrument calibration analysis",
            "metrological traceability analysis", "uncertainty propagation", "error-budget analysis",
            "measurement-bias analysis", "precision analysis", "accuracy analysis", "resolution adequacy analysis",
            "detection-limit analysis", "quantitation-limit analysis", "inter-rater reliability analysis",
            "construct-validity analysis", "criterion-validity analysis", "measurement invariance analysis",
            "identifiability analysis", "observability analysis", "data-fusion uncertainty analysis"
        ]
    },
    {
        "id": "experimental_design",
        "name": "Experimental design and controlled comparison",
        "kind": "study",
        "intent": ["experiment", "compare", "estimate intervention effect"],
        "basis": ["study_design", "assumption", "evidence"],
        "evidence": ["evidence.nist.experiment_design"],
        "practices": [
            "randomized controlled experiment", "A/B experiment", "multivariate experiment",
            "full-factorial experiment", "fractional-factorial experiment", "blocked experiment",
            "stratified experiment", "cluster-randomized experiment", "crossover experiment",
            "split-plot experiment", "response-surface experiment", "adaptive experiment",
            "sequential experiment", "multi-armed-bandit experiment", "switchback experiment",
            "stepped-wedge experiment", "encouragement design", "placebo and negative-control analysis",
            "experiment power analysis", "experiment sample-size determination"
        ]
    },
    {
        "id": "causal",
        "name": "Causal inference and policy-effect analytics",
        "kind": "study",
        "intent": ["identify cause", "estimate effect", "evaluate policy"],
        "basis": ["intent", "study_design", "assumption", "evidence"],
        "evidence": ["evidence.causal.inference"],
        "practices": [
            "causal-question formulation", "causal-DAG specification", "identification analysis",
            "back-door adjustment", "front-door adjustment", "standardization and g-computation",
            "inverse-probability weighting", "propensity-score matching", "coarsened-exact matching",
            "doubly robust effect estimation", "instrumental-variable analysis", "regression-discontinuity analysis",
            "difference-in-differences analysis", "synthetic-control analysis", "interrupted-time-series analysis",
            "event-study causal analysis", "panel causal analysis", "mediation analysis", "moderation analysis",
            "heterogeneous-treatment-effect analysis", "uplift analysis", "causal-discovery analysis",
            "causal-transportability analysis", "policy evaluation", "causal sensitivity analysis",
            "unmeasured-confounding analysis", "negative-control causal analysis", "counterfactual explanation"
        ]
    },
    {
        "id": "forecasting",
        "name": "Forecasting, nowcasting and anticipatory analytics",
        "kind": "study",
        "intent": ["forecast", "nowcast", "anticipate"],
        "basis": ["intent", "time", "uncertainty", "evaluation"],
        "evidence": ["evidence.hyndman.fpp3"],
        "practices": [
            "naive forecasting", "seasonal-naive forecasting", "moving-average forecasting",
            "exponential-smoothing forecasting", "trend forecasting", "seasonal forecasting",
            "ARIMA forecasting", "dynamic-regression forecasting", "structural-time-series forecasting",
            "state-space forecasting", "vector-autoregression forecasting", "cointegrated-system forecasting",
            "hierarchical forecasting", "grouped forecasting", "temporal-hierarchy forecasting",
            "intermittent-demand forecasting", "new-product forecasting", "analog forecasting",
            "judgmental forecasting", "Delphi forecasting", "forecast combination", "scenario forecasting",
            "probabilistic forecasting", "quantile forecasting", "density forecasting", "interval forecasting",
            "nowcasting", "backcasting", "early-warning forecasting", "forecast reconciliation",
            "forecast-value assessment", "forecast-bias diagnosis", "forecast-accuracy backtesting"
        ]
    },
    {
        "id": "anomaly_change",
        "name": "Anomaly, change and regime analytics",
        "kind": "diagnostic",
        "intent": ["detect", "localize change", "characterize regime"],
        "basis": ["intent", "input_contract", "runtime", "evaluation"],
        "evidence": ["evidence.nist.monitoring"],
        "practices": [
            "point-anomaly detection", "contextual-anomaly detection", "collective-anomaly detection",
            "multivariate-anomaly detection", "sequence-anomaly detection", "seasonal-anomaly detection",
            "rare-event detection", "novelty detection", "out-of-distribution detection",
            "online-anomaly detection", "change-point detection", "structural-break detection",
            "distribution-shift detection", "concept-drift detection", "regime-shift detection",
            "regime-switching analysis", "scan-statistic detection", "emerging-pattern detection",
            "anomaly triage", "anomaly attribution", "alert-correlation analysis"
        ]
    },
    {
        "id": "process",
        "name": "Process, workflow and case analytics",
        "kind": "diagnostic",
        "intent": ["discover process", "check conformance", "improve flow"],
        "basis": ["intent", "input_contract", "output_contract", "evaluation"],
        "evidence": ["evidence.ieee.process_mining_manifesto"],
        "practices": [
            "process discovery", "procedural-process discovery", "declarative-process discovery",
            "object-centric process mining", "case-centric process mining", "case-level inspection",
            "process-variant analysis", "process conformance checking", "alignment-based conformance checking",
            "token-replay conformance checking", "rule and policy conformance checking",
            "process-model fitness assessment", "process-model precision assessment",
            "process-model generalization assessment", "process-model simplicity assessment",
            "process enhancement", "process performance analysis", "bottleneck localization",
            "waiting-time analysis", "cycle-time analysis", "rework-loop analysis", "handoff analysis",
            "organizational process mining", "social-network process analysis", "decision mining",
            "task mining", "process concept-drift analysis", "predictive process monitoring",
            "remaining-time prediction", "next-activity prediction", "process-outcome prediction",
            "process deviation root-cause analysis", "comparative process mining", "process simulation",
            "operational process detection", "operational process recommendation"
        ]
    },
    {
        "id": "diagnostic_rca",
        "name": "Diagnostic and root-cause analytics",
        "kind": "diagnostic",
        "intent": ["diagnose", "localize cause", "explain change"],
        "basis": ["intent", "evidence", "decision"],
        "evidence": ["evidence.nist.process_improvement"],
        "practices": [
            "root-cause analysis", "fault-tree analysis", "event-tree analysis",
            "failure-mode-and-effects analysis", "five-whys analysis", "Ishikawa cause analysis",
            "causal-tree diagnosis", "change attribution", "driver analysis", "variance-bridge analysis",
            "hierarchical drill-down diagnosis", "dependency-aware diagnosis", "topology-aware diagnosis",
            "incident-correlation diagnosis", "symptom-to-cause inference", "abductive diagnosis",
            "counterfactual diagnosis", "residual diagnosis", "failure-signature analysis",
            "comparative-case diagnosis", "defect Pareto diagnosis", "evidence triangulation"
        ]
    },
    {
        "id": "quality_spc",
        "name": "Statistical quality and process-control analytics",
        "kind": "operational_support",
        "intent": ["monitor quality", "control process", "improve process"],
        "basis": ["study_design", "runtime", "decision"],
        "evidence": ["evidence.nist.monitoring", "evidence.nist.process_improvement"],
        "practices": [
            "statistical process control", "individuals and moving-range control",
            "X-bar and range control", "X-bar and standard-deviation control", "attribute control-chart analysis",
            "EWMA control", "CUSUM control", "multivariate process control", "short-run process control",
            "process-capability analysis", "process-performance analysis", "acceptance-sampling analysis",
            "lot-quality assessment", "defect and nonconformance analysis", "yield analysis",
            "tolerance analysis", "designed process-improvement experiment", "robust-parameter design",
            "response-surface optimization", "control-plan effectiveness analysis", "quality escape analysis"
        ]
    },
    {
        "id": "reliability_survival",
        "name": "Reliability, survival and event-history analytics",
        "kind": "study",
        "intent": ["estimate survival", "assess reliability", "predict failure"],
        "basis": ["time", "censoring", "uncertainty", "decision"],
        "evidence": ["evidence.nist.reliability"],
        "practices": [
            "Kaplan-Meier survival analysis", "life-table analysis", "parametric survival analysis",
            "Cox proportional-hazards analysis", "accelerated-failure-time analysis",
            "competing-risks analysis", "multi-state event-history analysis", "recurrent-event analysis",
            "cure-model analysis", "frailty analysis", "time-varying-covariate survival analysis",
            "reliability distribution fitting", "Weibull reliability analysis", "accelerated-life testing",
            "degradation analysis", "remaining-useful-life estimation", "reliability-block analysis",
            "load-strength interference analysis", "repairable-system analysis", "reliability-growth analysis",
            "maintainability analysis", "availability analysis", "warranty and field-return analysis",
            "censored-data diagnosis", "truncation-aware event analysis", "hazard decomposition"
        ]
    },
    {
        "id": "queue_flow_capacity",
        "name": "Queue, flow, congestion and capacity analytics",
        "kind": "diagnostic",
        "intent": ["analyze flow", "locate bottleneck", "plan capacity"],
        "basis": ["input_contract", "method", "decision"],
        "evidence": ["evidence.informs.operations_research"],
        "practices": [
            "Little's-law analysis", "arrival-process analysis", "service-time analysis",
            "queue-performance analysis", "queueing-network analysis", "waiting-time analysis",
            "abandonment analysis", "congestion analysis", "bottleneck analysis", "constraint analysis",
            "capacity analysis", "utilization analysis", "work-in-process analysis", "throughput analysis",
            "flow-balance analysis", "staffing analysis", "appointment-capacity analysis",
            "service-level risk analysis", "finite-buffer analysis", "priority-queue analysis",
            "blocking and starvation analysis"
        ]
    },
    {
        "id": "simulation",
        "name": "Simulation and what-if analytics",
        "kind": "method",
        "intent": ["simulate", "stress", "compare scenarios"],
        "basis": ["input_contract", "output_contract", "uncertainty", "evaluation"],
        "evidence": ["evidence.informs.simulation"],
        "practices": [
            "Monte Carlo simulation", "discrete-event simulation", "agent-based simulation",
            "system-dynamics simulation", "microsimulation", "stochastic-process simulation",
            "hybrid simulation", "digital-twin simulation", "scenario simulation", "stress simulation",
            "counterfactual simulation", "historical replay simulation", "rare-event simulation",
            "uncertainty-propagation simulation", "simulation sensitivity analysis", "simulation calibration",
            "simulation validation", "surrogate-model simulation", "simulation optimization",
            "hardware-in-the-loop analysis", "policy microsimulation"
        ]
    },
    {
        "id": "optimization",
        "name": "Optimization and mathematical-programming analytics",
        "kind": "decision",
        "intent": ["optimize", "allocate", "schedule"],
        "basis": ["input_contract", "assumption", "decision", "evaluation"],
        "evidence": ["evidence.informs.operations_research"],
        "practices": [
            "linear optimization", "mixed-integer linear optimization", "nonlinear optimization",
            "convex optimization", "non-convex optimization", "combinatorial optimization",
            "constraint programming", "dynamic programming", "stochastic optimization",
            "robust optimization", "chance-constrained optimization", "distributionally robust optimization",
            "multi-objective optimization", "bilevel optimization", "network-flow optimization",
            "assignment optimization", "matching optimization", "routing optimization", "scheduling optimization",
            "packing optimization", "cutting-stock optimization", "inventory optimization", "portfolio optimization",
            "facility-location optimization", "location-allocation optimization", "optimal control",
            "model-predictive control", "simulation optimization", "decomposition optimization",
            "column-generation optimization", "heuristic optimization", "metaheuristic optimization",
            "global optimization", "feasibility and constraint diagnosis", "solution-sensitivity analysis",
            "shadow-price analysis", "optimality-gap analysis"
        ]
    },
    {
        "id": "heuristic_search",
        "name": "Heuristic, metaheuristic and hybrid optimization",
        "kind": "decision",
        "intent": ["find feasible solution", "improve solution", "search under budget"],
        "basis": ["method", "runtime", "evaluation", "decision"],
        "evidence": ["evidence.ortools.routing_search", "evidence.informs.operations_research"],
        "practices": [
            "constructive heuristic", "greedy heuristic", "best-insertion heuristic",
            "cheapest-insertion heuristic", "savings heuristic", "sweep heuristic",
            "first-fit heuristic", "best-fit heuristic", "priority-rule heuristic",
            "dispatching-rule heuristic", "relax-and-fix heuristic", "fix-and-optimize heuristic",
            "rounding heuristic", "diving heuristic", "feasibility-pump heuristic",
            "local search", "hill-climbing search", "steepest-descent search",
            "first-improvement search", "best-improvement search", "neighborhood search",
            "variable-neighborhood search", "large-neighborhood search", "ruin-and-recreate search",
            "iterated local search", "tabu search", "simulated annealing", "threshold-accepting search",
            "guided local search", "genetic algorithm", "evolutionary strategy",
            "differential-evolution search", "memetic algorithm", "ant-colony optimization",
            "particle-swarm optimization", "GRASP", "scatter search", "beam search",
            "random-restart search", "adaptive memory search", "hyper-heuristic search",
            "algorithm-portfolio selection", "automated heuristic configuration",
            "matheuristic optimization", "relaxation-guided heuristic", "decomposition-guided heuristic",
            "exact-and-heuristic hybrid search", "simulation-heuristic optimization",
            "anytime optimization", "budgeted search", "solution-pool analysis",
            "heuristic robustness evaluation", "heuristic optimality-gap estimation",
            "heuristic reproducibility analysis"
        ]
    },
    {
        "id": "or_modeling",
        "name": "Operations-research problem formulation and solution assurance",
        "kind": "decision",
        "intent": ["formulate decision problem", "select method", "assure solution"],
        "basis": ["input_contract", "assumption", "evidence", "runtime", "decision"],
        "evidence": ["evidence.informs.operations_research", "evidence.ortools.reference"],
        "practices": [
            "decision-variable formulation", "objective-function formulation", "constraint formulation",
            "hard-and-soft constraint analysis", "penalty-function design", "uncertainty-set formulation",
            "scenario-tree formulation", "multi-stage decision formulation", "recourse formulation",
            "state-action formulation", "Markov decision-process analysis", "partially observable decision analysis",
            "stochastic-process modeling", "queueing-model formulation", "inventory-model formulation",
            "network-model formulation", "scheduling-model formulation", "routing-model formulation",
            "market and mechanism model formulation", "game-theoretic equilibrium analysis",
            "bargaining analysis", "auction-design analysis", "revenue-management analysis",
            "model linearization", "model relaxation", "surrogate objective design",
            "model decomposition", "symmetry analysis", "presolve analysis", "scaling analysis",
            "solver-selection analysis", "algorithm-configuration analysis", "warm-start analysis",
            "feasibility diagnosis", "irreducible-infeasible-subsystem analysis", "unboundedness diagnosis",
            "solution verification", "constraint-slack analysis", "dual and reduced-cost analysis",
            "solution stability analysis", "solution explainability analysis", "post-optimality analysis",
            "implementation feasibility analysis", "decision-policy simulation", "optimization backtesting"
        ]
    },
    {
        "id": "decision_risk",
        "name": "Decision, risk and policy analytics",
        "kind": "decision",
        "intent": ["decide", "prioritize", "manage risk"],
        "basis": ["intent", "uncertainty", "decision", "evidence"],
        "evidence": ["evidence.informs.decision_analysis"],
        "practices": [
            "decision-tree analysis", "influence-diagram analysis", "expected-utility analysis",
            "Bayesian decision analysis", "multi-criteria decision analysis", "analytic-hierarchy analysis",
            "outranking analysis", "value-of-information analysis", "value-of-perfect-information analysis",
            "real-options analysis", "minimax decision analysis", "minimax-regret analysis",
            "robust decision making", "decision-threshold analysis", "risk aggregation", "risk decomposition",
            "scenario analysis", "stress testing", "reverse stress testing", "limit-utilization analysis",
            "policy-rule evaluation", "triage analysis", "prioritization analysis", "resource-allocation analysis",
            "treatment-selection analysis", "portfolio decision analysis", "decision audit",
            "decision-outcome feedback analysis"
        ]
    },
    {
        "id": "graph_network",
        "name": "Graph, network and relationship analytics",
        "kind": "study",
        "intent": ["analyze relationships", "trace paths", "diagnose networks"],
        "basis": ["input_contract", "method", "output_contract"],
        "evidence": ["evidence.network_science"],
        "practices": [
            "centrality analysis", "community detection", "link prediction", "graph matching",
            "subgraph matching", "motif analysis", "path analysis", "reachability analysis",
            "network-flow analysis", "cut-set analysis", "diffusion analysis", "contagion analysis",
            "cascade analysis", "k-core analysis", "structural-equivalence analysis", "role analysis",
            "bipartite-network analysis", "multiplex-network analysis", "temporal-graph analysis",
            "dynamic-network analysis", "network-resilience analysis", "dependency-graph analysis",
            "relationship-entity resolution", "fraud-ring analysis", "supply-network risk analysis",
            "lineage-graph impact analysis", "knowledge-graph consistency analysis",
            "graph-partition analysis", "network intervention analysis"
        ]
    },
    {
        "id": "spatial",
        "name": "Spatial and spatiotemporal analytics",
        "kind": "study",
        "intent": ["locate", "compare space", "analyze movement"],
        "basis": ["input_contract", "time", "method", "output_contract"],
        "evidence": ["evidence.ogc.spatial"],
        "practices": [
            "geocoding-quality analysis", "point-pattern analysis", "spatial-autocorrelation analysis",
            "hotspot analysis", "spatial-cluster analysis", "spatial-interpolation analysis",
            "kriging analysis", "spatial-regression analysis", "areal-data analysis", "raster zonal analysis",
            "terrain analysis", "viewshed analysis", "network-route analysis", "accessibility analysis",
            "catchment-area analysis", "location-allocation analysis", "spatiotemporal cluster analysis",
            "trajectory analysis", "origin-destination analysis", "mobility-flow analysis",
            "geofence event analysis", "exposure-surface analysis", "spatial change detection",
            "remote-sensing change analysis", "spatial coverage analysis", "map-matching analysis"
        ]
    },
    {
        "id": "text_content",
        "name": "Non-generative text, document and content analytics",
        "kind": "study",
        "intent": ["analyze text", "extract structure", "compare documents"],
        "basis": ["input_contract", "method", "output_contract"],
        "evidence": ["evidence.information_retrieval"],
        "practices": [
            "corpus profiling", "token-frequency analysis", "keyword analysis", "keyphrase extraction",
            "concordance analysis", "n-gram analysis", "collocation analysis", "lexicon-based sentiment analysis",
            "topic-model analysis", "document clustering", "document classification", "rule-based entity extraction",
            "statistical named-entity recognition", "relation extraction", "sequence labeling",
            "readability analysis", "document-similarity analysis", "near-duplicate document detection",
            "language identification", "stylometric analysis", "document-layout analysis", "OCR-quality analysis",
            "taxonomy classification", "bibliometric analysis", "citation-network analysis",
            "content-policy conformance analysis", "terminology consistency analysis"
        ]
    },
    {
        "id": "signal_sensor",
        "name": "Signal, waveform and sensor analytics",
        "kind": "method",
        "intent": ["analyze signal", "detect event", "estimate state"],
        "basis": ["input_contract", "time", "method", "runtime"],
        "evidence": ["evidence.signal_processing"],
        "practices": [
            "spectral analysis", "Fourier analysis", "wavelet analysis", "time-frequency analysis",
            "digital filtering", "signal smoothing", "signal denoising", "peak detection", "edge-event detection",
            "envelope analysis", "harmonic analysis", "coherence analysis", "cross-correlation analysis",
            "autocorrelation analysis", "phase analysis", "state estimation", "Kalman filtering",
            "sensor-fusion analysis", "sensor-drift analysis", "sensor-health diagnosis",
            "vibration analysis", "acoustic analysis", "modal analysis", "order-tracking analysis",
            "waveform-quality analysis", "signal change-point analysis", "event-trigger analysis"
        ]
    },
    {
        "id": "image_video",
        "name": "Classical image and video analytics",
        "kind": "method",
        "intent": ["measure image", "detect visual structure", "track change"],
        "basis": ["input_contract", "method", "output_contract"],
        "evidence": ["evidence.image_processing"],
        "practices": [
            "image-quality assessment", "image segmentation", "edge detection", "morphological image analysis",
            "connected-component analysis", "texture analysis", "shape analysis", "color-distribution analysis",
            "template matching", "feature-point extraction", "image registration", "change-image analysis",
            "motion estimation", "object tracking", "optical-flow analysis", "stereo-depth analysis",
            "photogrammetric measurement", "video event segmentation", "frame-quality analysis",
            "classical defect-vision analysis"
        ]
    },
    {
        "id": "data_mining",
        "name": "Classical data-mining and predictive analytics",
        "kind": "method",
        "intent": ["predict", "classify", "discover pattern"],
        "basis": ["intent", "method", "evaluation"],
        "evidence": ["evidence.data_mining"],
        "practices": [
            "supervised classification", "regression prediction", "ordinal prediction", "ranking analysis",
            "probability scoring", "calibrated risk scoring", "clustering", "density estimation",
            "association-rule mining", "frequent-itemset mining", "sequential-pattern mining",
            "episode mining", "subgroup discovery", "contrast-set mining", "rule induction",
            "dimensionality reduction", "feature selection", "feature-importance analysis",
            "partial-dependence analysis", "surrogate-model explanation", "nearest-neighbor analysis",
            "ensemble prediction", "cost-sensitive classification", "imbalanced-class analysis",
            "semi-supervised pattern analysis", "active-sampling analysis"
        ]
    },
    {
        "id": "econometric_longitudinal",
        "name": "Econometric, panel and longitudinal analytics",
        "kind": "study",
        "intent": ["estimate relationship", "analyze longitudinal change", "evaluate shock"],
        "basis": ["study_design", "time", "assumption", "uncertainty"],
        "evidence": ["evidence.econometrics"],
        "practices": [
            "cross-sectional regression", "panel fixed-effects analysis", "panel random-effects analysis",
            "longitudinal mixed-effects analysis", "generalized estimating equations", "simultaneous-equation analysis",
            "seemingly-unrelated regression", "cointegration analysis", "error-correction analysis",
            "Granger-predictive analysis", "local-projection analysis", "impulse-response analysis",
            "event-study analysis", "Oaxaca-Blinder decomposition", "productivity analysis",
            "production-frontier analysis", "input-output analysis", "elasticity estimation",
            "demand-system estimation", "hedonic analysis", "duration econometrics", "limited-dependent-variable analysis",
            "selection-model analysis", "microsimulation analysis"
        ]
    },
    {
        "id": "behavior_journey",
        "name": "Population behavior, journey and relationship analytics",
        "kind": "study",
        "intent": ["understand behavior", "analyze journey", "predict retention"],
        "basis": ["intent", "population", "time", "decision"],
        "evidence": ["evidence.behavior_analytics"],
        "practices": [
            "population segmentation", "behavioral segmentation", "cohort-retention analysis",
            "attrition analysis", "churn analysis", "lifetime-value analysis", "recency-frequency-value analysis",
            "journey-path analysis", "touchpoint analysis", "funnel conversion analysis",
            "drop-off diagnosis", "channel-switching analysis", "sequence-of-use analysis",
            "market-basket analysis", "cross-affinity analysis", "propensity analysis", "uplift targeting analysis",
            "next-best-action analysis", "recommendation evaluation", "attribution analysis",
            "incrementality analysis", "share-of-wallet analysis", "relationship-depth analysis",
            "complaint-theme analysis", "service-recovery analysis"
        ]
    },
    {
        "id": "data_quality_observability",
        "name": "Data quality, reconciliation and observability analytics",
        "kind": "validation",
        "intent": ["validate data", "reconcile", "diagnose data incident"],
        "basis": ["input_contract", "evidence", "runtime", "decision"],
        "evidence": ["evidence.data_quality"],
        "practices": [
            "data profiling", "completeness analysis", "validity analysis", "uniqueness analysis",
            "referential-integrity analysis", "cross-field consistency analysis", "cross-system consistency analysis",
            "timeliness analysis", "freshness analysis", "data-volume anomaly analysis",
            "schema-change analysis", "distribution-change analysis", "duplicate-entity analysis",
            "source-to-target reconciliation", "ledger-style reconciliation", "control-total reconciliation",
            "lineage-impact analysis", "data-incident root-cause analysis", "data-SLA analysis",
            "late-arrival analysis", "ordering and finality analysis", "correction and restatement analysis",
            "quality-rule effectiveness analysis", "data-contract conformance", "observability coverage analysis"
        ]
    },
    {
        "id": "semantic_metric",
        "name": "Semantic, metric and multidimensional evaluation analytics",
        "kind": "semantic_evaluation",
        "intent": ["evaluate measure", "aggregate correctly", "explain formula"],
        "basis": ["input_contract", "output_contract", "assumption", "evidence"],
        "evidence": ["evidence.sdmx", "evidence.openformula"],
        "practices": [
            "metric evaluation", "formula evaluation", "dimensional-consistency analysis",
            "unit-conversion analysis", "currency-normalization analysis", "aggregation-validity analysis",
            "semi-additive measure analysis", "non-additive measure analysis", "allocation analysis",
            "ratio-of-aggregates analysis", "weighted-average analysis", "distinct-count analysis",
            "approximate-distinct-count analysis", "percentile and quantile analysis", "windowed-measure analysis",
            "time-intelligence analysis", "period-over-period analysis", "same-period comparison",
            "cohort-semantic analysis", "hierarchy roll-up analysis", "many-to-many join-impact analysis",
            "metric decomposition", "metric reconciliation", "metric lineage analysis",
            "semantic-query validation", "calculation-change impact analysis"
        ]
    },
    {
        "id": "search_retrieval",
        "name": "Search, retrieval, matching and resolution analytics",
        "kind": "method",
        "intent": ["retrieve", "match", "resolve identity"],
        "basis": ["input_contract", "evaluation", "runtime"],
        "evidence": ["evidence.information_retrieval"],
        "practices": [
            "exact-match retrieval", "Boolean retrieval", "full-text retrieval", "faceted retrieval",
            "fielded retrieval", "fuzzy retrieval", "phonetic matching", "similarity retrieval",
            "temporal retrieval", "spatial retrieval", "entity-centric retrieval", "record linkage",
            "probabilistic record linkage", "deterministic entity resolution", "duplicate-record resolution",
            "candidate-pair generation", "match-score calibration", "retrieval relevance evaluation",
            "index-coverage analysis", "zero-result analysis", "query-log analysis"
        ]
    },
    {
        "id": "privacy_fairness",
        "name": "Privacy, disclosure, representativeness and fairness analytics",
        "kind": "validation",
        "intent": ["assess privacy", "assess bias", "validate fairness"],
        "basis": ["evidence", "uncertainty", "decision"],
        "evidence": ["evidence.nist.privacy", "evidence.nist.ai_rmf_measure"],
        "practices": [
            "re-identification-risk analysis", "statistical-disclosure-risk analysis", "k-anonymity assessment",
            "l-diversity assessment", "t-closeness assessment", "differential-privacy accounting",
            "privacy-utility analysis", "small-cell disclosure analysis", "linkage-attack analysis",
            "sampling-bias analysis", "coverage-bias analysis", "nonresponse-bias analysis",
            "missingness-bias analysis", "representation analysis", "subgroup-performance analysis",
            "disparate-impact analysis", "error-rate parity analysis", "calibration-by-group analysis",
            "counterfactual-fairness assessment", "intersectional fairness analysis",
            "fairness-threshold trade-off analysis", "consent-purpose conformance analysis",
            "data-residency conformance analysis"
        ]
    },
    {
        "id": "model_evaluation",
        "name": "Analytical model evaluation, validation and monitoring",
        "kind": "validation",
        "intent": ["validate model", "compare model", "monitor performance"],
        "basis": ["evaluation", "evidence", "runtime"],
        "evidence": ["evidence.model_risk_management"],
        "practices": [
            "holdout evaluation", "cross-validation", "time-series backtesting", "rolling-origin evaluation",
            "benchmark-model comparison", "champion-challenger analysis", "discrimination analysis",
            "calibration analysis", "probabilistic-score evaluation", "ranking evaluation",
            "residual analysis", "error decomposition", "stability analysis", "population-stability analysis",
            "parameter-stability analysis", "sensitivity analysis", "stress testing for models",
            "outcome analysis", "model-drift monitoring", "feature-drift monitoring",
            "model-performance monitoring", "threshold-performance analysis", "decision-curve analysis",
            "model-risk assessment", "independent model validation", "reproducibility assessment",
            "implementation-verification analysis", "model-limitation tracking"
        ]
    },
    {
        "id": "survey_official_statistics",
        "name": "Survey, census and official-statistics analytics",
        "kind": "study",
        "intent": ["estimate population", "adjust sample", "publish statistics"],
        "basis": ["study_design", "input_contract", "uncertainty", "evidence"],
        "evidence": ["evidence.un.official_statistics", "evidence.sdmx"],
        "practices": [
            "sample-design analysis", "stratified-sample estimation", "cluster-sample estimation",
            "survey-weighting analysis", "post-stratification", "raking and calibration weighting",
            "nonresponse adjustment", "design-effect analysis", "finite-population estimation",
            "capture-recapture analysis", "census coverage analysis", "small-area estimation",
            "seasonal adjustment", "benchmark revision analysis", "chain-linking analysis",
            "index compilation", "national-accounts balancing", "supply-use balancing",
            "confidentiality perturbation analysis", "statistical revision analysis",
            "official-statistics quality assessment", "time-series dissemination consistency"
        ]
    },
    {
        "id": "operations_supply",
        "name": "Operations, inventory and supply-network analytics",
        "kind": "decision",
        "intent": ["plan operations", "control inventory", "manage supply"],
        "basis": ["decision", "time", "input_contract"],
        "evidence": ["evidence.informs.operations_research"],
        "practices": [
            "demand-pattern segmentation", "ABC inventory analysis", "XYZ variability analysis",
            "inventory-policy analysis", "safety-stock analysis", "reorder-point analysis",
            "service-level inventory analysis", "multi-echelon inventory analysis", "stockout-risk analysis",
            "excess-and-obsolete analysis", "bullwhip-effect analysis", "supplier-performance analysis",
            "supplier-risk analysis", "supply-network exposure analysis", "order-allocation analysis",
            "available-to-promise analysis", "capable-to-promise analysis", "production-plan analysis",
            "schedule-adherence analysis", "yield-and-scrap flow analysis", "network-capacity analysis",
            "fulfillment-path analysis", "inventory-reconciliation analysis", "disruption-scenario analysis"
        ]
    },
    {
        "id": "cost_performance",
        "name": "Cost, resource and performance-efficiency analytics",
        "kind": "diagnostic",
        "intent": ["attribute cost", "analyze efficiency", "plan resources"],
        "basis": ["input_contract", "assumption", "decision"],
        "evidence": ["evidence.cost_accounting", "evidence.performance_engineering"],
        "practices": [
            "cost allocation", "activity-based costing", "unit-cost analysis", "marginal-cost analysis",
            "incremental-cost analysis", "cost-to-serve analysis", "total-cost-of-ownership analysis",
            "cost-driver analysis", "cost-variance analysis", "resource-consumption analysis",
            "capacity-cost analysis", "efficiency-frontier analysis", "data-envelopment analysis",
            "productivity analysis", "price-volume-mix analysis", "latency decomposition",
            "throughput-cost analysis", "cost-performance frontier analysis", "energy-intensity analysis",
            "resource-rightsizing analysis", "budget-burn analysis", "cost-anomaly analysis"
        ]
    },
    {
        "id": "control_feedback",
        "name": "Control, feedback and closed-loop operational analytics",
        "kind": "operational_support",
        "intent": ["monitor", "control", "adapt"],
        "basis": ["runtime", "decision", "evaluation"],
        "evidence": ["evidence.control_systems"],
        "practices": [
            "state estimation", "system identification", "stability analysis", "controllability analysis",
            "observability analysis", "feedback-loop analysis", "setpoint-tracking analysis",
            "disturbance-rejection analysis", "control-limit analysis", "constraint-violation prediction",
            "model-predictive control analysis", "adaptive-control analysis", "fault-detection-and-isolation",
            "fault-tolerant control analysis", "alarm-rationalization analysis", "alarm-flood analysis",
            "operator-response analysis", "intervention-effect monitoring", "policy-feedback evaluation",
            "closed-loop outcome monitoring", "safe-shutdown decision analysis"
        ]
    }
]


def slug(value: str) -> str:
    value = value.lower().replace("'", "").replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value


def main() -> int:
    records = []
    ids = set()
    labels = {}
    for family in FAMILIES:
        family_id = f"analytics.{family['id']}"
        for name in family["practices"]:
            practice_id = f"{family_id}.{slug(name)}"
            if practice_id in ids:
                raise ValueError(f"duplicate practice id: {practice_id}")
            ids.add(practice_id)
            labels.setdefault(name.lower(), []).append(practice_id)
            records.append({
                "practice_id": practice_id,
                "edition": 1,
                "status": "hypothesis",
                "family_id": family_id,
                "name": name,
                "aliases": [],
                "definition": (
                    f"Candidate practice in {family['name']}; exact intent, input/output, assumptions, "
                    "uncertainty, evaluation and evidence contract require adjudication."
                ),
                "practice_kind": family["kind"],
                "distinctiveness_basis": family["basis"],
                "intent_verbs": family["intent"],
                "input_contracts": [],
                "output_contracts": [],
                "assumptions": [],
                "uncertainty_contract": [],
                "evaluation_contract": [],
                "decision_proximity": "unadjudicated",
                "domain_portability": "unadjudicated",
                "evidence_refs": family["evidence"],
                "llm_dependency": "none",
                "gaps": [
                    "candidate identity not yet split/merge adjudicated",
                    "exact semantic and executable contracts not yet specified",
                    "primary evidence not yet verified at record level",
                    "compiler and machine mappings not yet established"
                ]
            })

    duplicate_labels = {name: refs for name, refs in labels.items() if len(refs) > 1}
    with (HERE / "candidate-practices.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    (HERE / "family-catalog.json").write_text(
        json.dumps({
            "edition": 1,
            "status": "hypothesis_queue",
            "family_count": len(FAMILIES),
            "candidate_count": len(records),
            "families": [{k: v for k, v in family.items() if k != "practices"} | {"candidate_count": len(family["practices"])} for family in FAMILIES],
            "duplicate_label_review_queue": duplicate_labels,
            "completion_claim": False
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )
    print(f"WROTE {len(records)} analytical-practice hypotheses across {len(FAMILIES)} families; {len(duplicate_labels)} duplicate labels need ownership review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
