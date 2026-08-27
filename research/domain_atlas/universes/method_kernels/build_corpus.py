#!/usr/bin/env python3
"""Build the provider-neutral method/algorithm/kernel research universe.

The Python structures are the reviewable authoring form. Generated JSONL files are
machine-consumable candidate records, never a completeness claim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EDITION = 1
ACCESSED = "2026-08-25"


def write_jsonl(name: str, rows: list[dict]) -> None:
    (ROOT / name).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def write_manifest() -> None:
    artifacts = sorted(p for p in ROOT.rglob("*.json*") if p.name != "manifest.json" and "__pycache__" not in p.parts)
    files = {str(p.relative_to(ROOT)): {"bytes": len(p.read_bytes()), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in artifacts}
    (ROOT / "manifest.json").write_text(json.dumps({"manifest_id": "manifest.method-kernels.v1", "edition": EDITION, "files": files, "completion_claim": False}, indent=2, sort_keys=True) + "\n")


SOURCE_ROWS = [
    # Statistics, inference, experiments, causality, forecasting and anomaly detection.
    ("nist_handbook", "NIST/SEMATECH Engineering Statistics Handbook", "NIST", "official_documentation", "https://www.itl.nist.gov/div898/handbook/", "engineering statistics, exploratory analysis, process control, experiment design and reliability"),
    ("asa_pvalue", "ASA Statement on Statistical Significance and P-Values", "American Statistical Association", "standard", "https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf", "interpretation limits of p-values and statistical significance"),
    ("scipy_stats", "Statistical functions (scipy.stats)", "SciPy", "official_documentation", "https://docs.scipy.org/doc/scipy/reference/stats.html", "probability distributions, tests, estimators and descriptive statistics"),
    ("statsmodels_guide", "statsmodels User Guide", "statsmodels", "official_documentation", "https://www.statsmodels.org/stable/user-guide.html", "regression, GLM, GEE, mixed, multivariate, duration and time-series methods"),
    ("statsmodels_tsa", "Time Series Analysis", "statsmodels", "official_documentation", "https://www.statsmodels.org/stable/tsa", "ARIMA, state-space, VAR, filters, tests and forecasting contracts"),
    ("statsmodels_survival", "Methods for Survival and Duration Analysis", "statsmodels", "official_documentation", "https://www.statsmodels.org/stable/duration.html", "right-censored survival estimation and proportional-hazards regression"),
    ("r_stats", "R stats package index", "R Core Team", "official_documentation", "https://stat.ethz.ch/R-manual/R-devel/library/stats/html/00Index.html", "reference implementation surface for classical statistical methods"),
    ("stan_reference", "Stan Reference Manual", "Stan Development Team", "official_documentation", "https://mc-stan.org/docs/reference-manual/", "Bayesian model, inference, diagnostics and generated-quantity semantics"),
    ("pymc_api", "PyMC API", "PyMC Developers", "official_documentation", "https://www.pymc.io/projects/docs/en/stable/api.html", "probabilistic modeling, sampling and posterior artifact interfaces"),
    ("sklearn_evaluation", "Model selection and evaluation", "scikit-learn", "official_documentation", "https://scikit-learn.org/stable/model_selection", "cross-validation, tuning, thresholding, scoring and evaluation"),
    ("sklearn_outlier", "Novelty and Outlier Detection", "scikit-learn", "official_documentation", "https://scikit-learn.org/stable/modules/outlier_detection.html", "outlier versus novelty semantics and representative algorithms"),
    ("river_anomaly", "River anomaly detection", "River", "official_documentation", "https://riverml.xyz/latest/api/overview/#anomaly-detection", "online anomaly scoring interfaces"),
    ("river_drift", "River concept drift detection", "River", "official_documentation", "https://riverml.xyz/latest/api/overview/#drift-detection", "stream drift detectors and update interfaces"),
    ("fda_adaptive", "Adaptive Designs for Clinical Trials Guidance", "US FDA", "regulatory_guidance", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/adaptive-design-clinical-trials-drugs-and-biologics-guidance-industry", "prospective adaptive study-design controls and simulation evidence"),
    ("consort", "CONSORT 2025 Statement", "CONSORT-SPIRIT Group", "standard", "https://www.consort-spirit.org/consort-2025", "randomized trial reporting and design transparency"),
    ("openfeature_spec", "OpenFeature Specification", "Cloud Native Computing Foundation", "standard", "https://openfeature.dev/specification/", "typed evaluation context, targeting identity, provider, hook, tracking and conformance requirements"),
    ("growthbook_ab", "Open Guide to A/B Testing", "GrowthBook", "official_documentation", "https://docs.growthbook.io/open-guide-to-ab-testing.v1.0.pdf", "experiment hypothesis, deterministic assignment, variation, exposure tracking and result workflow"),
    ("statsig_assignment", "Assignment Sources", "Statsig", "official_documentation", "https://docs.statsig.com/statsig-warehouse-native/configuration/assignment-sources", "unit, experiment, group and exposure-time assignment occurrence contracts"),
    ("statsig_lifecycle", "Stop Assignments", "Statsig", "official_documentation", "https://docs.statsig.com/experiments/ending/stop-assignments", "separation of new assignment closure, persistent prior assignment and continuing analysis"),
    ("dowhy_paper", "DoWhy: An End-to-End Library for Causal Inference", "DoWhy authors", "primary_paper", "https://arxiv.org/abs/2011.04216", "assumption-first causal identification, estimation and refutation workflow"),
    ("dowhy_docs", "DoWhy documentation", "PyWhy", "official_documentation", "https://www.pywhy.org/dowhy/", "causal graph, identification, estimation and refutation interfaces"),
    ("doubleml_docs", "DoubleML documentation", "DoubleML", "official_documentation", "https://docs.doubleml.org/", "orthogonal-score, cross-fitting and causal inference interfaces"),
    ("econml_docs", "EconML documentation", "Microsoft Research", "official_documentation", "https://econml.azurewebsites.net/", "conditional treatment-effect estimator interfaces and inference"),
    ("grf_reference", "Generalized Random Forests Reference", "grf authors", "official_documentation", "https://grf-labs.github.io/grf/REFERENCE.html", "forest-based heterogeneous effect and statistical inference contracts"),
    ("forecasting_book", "Forecasting: Principles and Practice, 3rd edition", "Hyndman and Athanasopoulos", "official_documentation", "https://otexts.com/fpp3/", "forecast workflow, models, accuracy, reconciliation and time-series cross-validation"),
    ("sktime_forecasting", "sktime forecasting API", "sktime", "official_documentation", "https://www.sktime.net/en/stable/api_reference/forecasting.html", "provider-neutral forecasting estimator and horizon interfaces"),
    ("statsforecast_docs", "StatsForecast documentation", "Nixtla", "official_documentation", "https://nixtlaverse.nixtla.io/statsforecast/", "statistical forecasting models, prediction intervals, cross-validation and distributed execution interfaces"),
    ("prophet_paper", "Forecasting at Scale", "Taylor and Letham", "primary_paper", "https://peerj.com/preprints/3190/", "decomposable forecasting and analyst-in-the-loop diagnostics"),

    # Process, quality and reliability.
    ("process_manifesto", "Process Mining Manifesto", "IEEE Task Force on Process Mining", "standard", "https://processmining.org/old-version/files/Process_Mining_Manifesto.pdf", "discovery, conformance, enhancement and operational-support scope"),
    ("ocel20", "Object-Centric Event Log 2.0 Specification", "OCEL Standard", "official_specification", "https://www.ocel-standard.org/2.0/ocel20_specification.pdf", "object-centric event, object, relationship and temporal-attribute semantics"),
    ("oced_core", "Towards a Simple and Extensible Standard for Object-Centric Event Data: Core Model, Design Space, and Lessons Learned", "Fahland et al.", "primary_paper", "https://arxiv.org/abs/2410.14495", "OCED core concepts, identity, qualifiers, extensions and explicit design choices distinct from OCEL exchange profiles"),
    ("state_aware_ocpm", "State-Aware Object-Centric Process Mining: Enhancing OCEL 2.0 with Explicit State Transitions", "Kretzschmann et al.", "primary_paper", "https://doi.org/10.1007/978-3-032-15140-7_6", "domain-conditioned object-state functions, generated state-transition events and State-Aware OCEL semantics"),
    ("temporal_ekg", "Transforming Object-Centric Event Logs to Temporal Event Knowledge Graphs", "Khayatbashi, Hartig and Jalali", "primary_paper", "https://arxiv.org/abs/2406.07596", "OCEL-to-temporal-event-knowledge-graph transformation with entity snapshots and temporal succession"),
    ("pm4py", "PM4Py documentation", "Fraunhofer FIT", "official_documentation", "https://processintelligence.solutions/pm4py/", "process discovery, conformance, event-data and object-centric implementations"),
    ("prom", "ProM Documentation", "ProM Tools", "official_documentation", "https://promtools.org/prom-documentation/", "plugin contracts for event logs, discovery, conformance and enhancement"),
    ("xes", "IEEE 1849-2016 XES Standard", "IEEE", "standard", "https://www.xes-standard.org/", "single-case event-log exchange semantics"),
    ("great_expectations", "Run Validations", "Great Expectations", "official_documentation", "https://docs.greatexpectations.io/docs/core/run_validations/", "expectation suites, batches, validations and result artifacts"),
    ("deequ", "Deequ", "AWS Labs", "reference_implementation", "https://github.com/awslabs/deequ", "large-scale dataset metrics, constraints and verification"),
    ("sodacl", "SodaCL metrics and checks", "Soda", "official_documentation", "https://docs.soda.io/sodacl-reference/metrics-and-checks", "data-quality metric, threshold, check and result states"),
    ("lifelines", "lifelines documentation", "lifelines Developers", "official_documentation", "https://lifelines.readthedocs.io/en/latest/", "survival analysis and censored-duration models"),

    # Graph and spatial.
    ("graphblas_c", "GraphBLAS C API 2.1.0", "GraphBLAS Forum", "standard", "https://graphblas.org/docs/GraphBLAS_API_C_v2.1.0.pdf", "semiring sparse matrix/vector building blocks for graph algorithms"),
    ("graphblas_cpp", "GraphBLAS C++ API Specification 1.0", "GraphBLAS Forum", "standard", "https://graphblas.org/graphblas-api-cpp/", "C++ graph linear-algebra containers, operators and algorithms"),
    ("suitesparse_graphblas", "SuiteSparse:GraphBLAS User Guide", "Texas A&M University", "reference_implementation", "https://github.com/DrTimothyAldenDavis/GraphBLAS", "reference GraphBLAS implementation, types, formats and execution controls"),
    ("lagraph_paper", "LAGraph: Linear Algebra, Network Analysis Libraries, and the Study of Graph Algorithms", "LAGraph authors", "primary_paper", "https://arxiv.org/abs/2104.01661", "separation between GraphBLAS primitives and graph-algorithm library"),
    ("networkx_algorithms", "NetworkX Algorithms", "NetworkX", "official_documentation", "https://networkx.org/documentation/stable/reference/algorithms/index.html", "graph algorithm taxonomy and Python reference interfaces"),
    ("igraph_manual", "igraph Reference Manual", "igraph", "official_documentation", "https://igraph.org/c/html/latest/", "graph representations and algorithm interfaces"),
    ("ogc_sfa", "Simple Features Access Part 1", "Open Geospatial Consortium", "standard", "https://www.ogc.org/standards/sfa/", "geometry, spatial-reference and topological semantics"),
    ("ogc_om", "Observations and Measurements", "Open Geospatial Consortium", "standard", "https://www.ogc.org/standards/om/", "observation, feature-of-interest, procedure and result semantics"),
    ("geos", "GEOS documentation", "OSGeo", "official_documentation", "https://libgeos.org/", "planar geometry predicates and constructive operations"),
    ("proj", "PROJ documentation", "OSGeo", "official_documentation", "https://proj.org/", "coordinate reference systems and transformations"),
    ("gdal", "GDAL documentation", "OSGeo", "official_documentation", "https://gdal.org/", "raster/vector translation, warping and geospatial data access"),
    ("postgis", "PostGIS Reference", "PostGIS Project", "official_documentation", "https://postgis.net/docs/reference.html", "database spatial predicates, measurement, transformation and indexing"),
    ("pysal_esda", "Exploratory Spatial Data Analysis", "PySAL", "official_documentation", "https://pysal.org/esda/", "spatial autocorrelation and exploratory spatial statistics"),
    ("pysal_spreg", "Spatial Regression Models", "PySAL", "official_documentation", "https://pysal.org/spreg/", "spatial regression estimator contracts"),

    # Text, search and semantic formulas.
    ("unicode_uax15", "Unicode Normalization Forms", "Unicode Consortium", "standard", "https://www.unicode.org/reports/tr15/", "canonical and compatibility normalization"),
    ("unicode_uax29", "Unicode Text Segmentation", "Unicode Consortium", "standard", "https://www.unicode.org/reports/tr29/", "grapheme, word and sentence boundary rules"),
    ("icu_boundary", "ICU Boundary Analysis", "Unicode Consortium", "official_documentation", "https://unicode-org.github.io/icu/userguide/boundaryanalysis/", "locale-aware text segmentation implementation"),
    ("icu_collation", "ICU Collation", "Unicode Consortium", "official_documentation", "https://unicode-org.github.io/icu/userguide/collation/", "locale-aware comparison, sort-key and tailoring semantics"),
    ("lucene_core", "Apache Lucene Core", "Apache Software Foundation", "official_documentation", "https://lucene.apache.org/core/", "inverted indexing, structured/full-text search and ranking library scope"),
    ("lucene_similarity", "Lucene Similarities", "Apache Software Foundation", "official_documentation", "https://lucene.apache.org/core/10_3_0/core/org/apache/lucene/search/similarities/package-summary.html", "BM25 and other retrieval scoring contracts"),
    ("tantivy", "Tantivy documentation", "Tantivy Project", "official_documentation", "https://docs.rs/tantivy/latest/tantivy/", "Rust full-text index, query, collector and schema interfaces"),
    ("openformula", "OpenDocument 1.3 Part 4: Recalculated Formula", "OASIS", "standard", "https://docs.oasis-open.org/office/OpenDocument/v1.3/csprd02/part4-formula/OpenDocument-v1.3-csprd02-part4-formula.html", "formula expression, function, error and evaluation semantics"),
    ("apache_ossie", "Apache Ossie Semantic Schema", "Apache Software Foundation", "official_specification", "https://github.com/apache/ossie/blob/main/core-spec/osi-schema.json", "open semantic-model entities, dimensions, measures and metrics schema"),
    ("dbt_semantic", "dbt Semantic Models", "dbt Labs", "official_documentation", "https://docs.getdbt.com/docs/build/semantic-models", "semantic graph, entity, dimension, time and simple-metric contracts"),
    ("dbt_metrics", "Creating metrics", "dbt Labs", "official_documentation", "https://docs.getdbt.com/docs/build/metrics-overview", "simple, ratio, derived, cumulative and conversion metric definitions"),
    ("sdmx", "SDMX Information Model", "SDMX", "standard", "https://docs.sdmx.org/en/i1-doc/Sections/Section1/SDMX_2-1_SECTION_1_Framework.html", "statistical data structure, concepts, dimensions and measures"),

    # Deterministic document containers, parsing, OCR, layout, tables and forms.
    ("pdf20", "PDF Specification Archive", "PDF Association", "standard", "https://pdfa.org/resource/pdf-specification-archive/", "ISO 32000-2:2020 PDF container, page, graphics, text, logical structure, form and embedded-file semantics"),
    ("ecma376", "ECMA-376 Office Open XML", "Ecma International", "standard", "https://ecma-international.org/publications-and-standards/standards/ecma-376/", "OOXML vocabularies, open packaging, relationships and compatibility semantics"),
    ("odf13", "OpenDocument Format 1.3", "OASIS", "standard", "https://docs.oasis-open.org/office/OpenDocument/v1.3/os/", "ODF package, document structure and content semantics"),
    ("html_standard", "HTML Living Standard", "WHATWG", "standard", "https://html.spec.whatwg.org/", "HTML parsing, DOM, document, form and embedded-content semantics"),
    ("rfc5322", "RFC 5322 Internet Message Format", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc5322", "email message header, body and address syntax"),
    ("rfc2045", "RFC 2045 Multipurpose Internet Mail Extensions", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc2045", "MIME media type, transfer encoding and multipart body semantics"),
    ("tika", "Apache Tika", "Apache Software Foundation", "official_documentation", "https://tika.apache.org/", "media detection and recursive metadata/text extraction across heterogeneous document formats"),
    ("pdfbox", "Apache PDFBox", "Apache Software Foundation", "official_documentation", "https://pdfbox.apache.org/", "PDF parsing, rendering, positioned text, metadata and AcroForm interfaces"),
    ("tesseract", "Tesseract User Manual", "Tesseract OCR", "official_documentation", "https://tesseract-ocr.github.io/tessdoc/", "OCR languages/scripts, page segmentation and text/TSV/hOCR/PAGE/ALTO output"),
    ("hocr", "hOCR Embedded OCR Workflow and Output Format", "hOCR Community", "official_specification", "https://kba.github.io/hocr-spec/1.2/", "OCR text hierarchy, coordinates, confidence and capabilities metadata"),
    ("alto", "ALTO XML Schema", "Library of Congress", "official_specification", "https://www.loc.gov/standards/alto/", "layout and text content with physical coordinates and confidence"),
    ("pubtables1m", "PubTables-1M: Towards Comprehensive Table Extraction From Unstructured Documents", "Microsoft Research", "primary_paper", "https://openaccess.thecvf.com/content/CVPR2022/html/Smock_PubTables-1M_Towards_Comprehensive_Table_Extraction_From_Unstructured_Documents_CVPR_2022_paper.html", "table detection, structure recognition, functional analysis, canonicalization and evaluation corpus"),
    ("spacy_pipeline", "spaCy Processing Pipelines", "Explosion", "official_documentation", "https://spacy.io/usage/processing-pipelines", "versioned text categorization, entity recognition and pipeline component interfaces"),
    ("opennlp_manual", "Apache OpenNLP Manual", "Apache Software Foundation", "official_documentation", "https://opennlp.apache.org/docs/2.5.7/manual/opennlp.html", "statistical text categorization, named-entity, chunking and document processing interfaces"),

    # Signal, image and numerical/scientific computing.
    ("scipy_signal", "Signal processing (scipy.signal)", "SciPy", "official_documentation", "https://docs.scipy.org/doc/scipy/reference/signal.html", "filtering, convolution, spectral, resampling and system operations"),
    ("scipy_fft", "Discrete Fourier transforms (scipy.fft)", "SciPy", "official_documentation", "https://docs.scipy.org/doc/scipy/reference/fft.html", "FFT/DCT/DST operations, normalization and backend control"),
    ("pywavelets", "PyWavelets documentation", "PyWavelets", "official_documentation", "https://pywavelets.readthedocs.io/en/latest/", "discrete/continuous wavelet transforms and thresholding"),
    ("fftw", "FFTW 3.3.11 Manual", "MIT FFTW Project", "official_documentation", "https://fftw.org/fftw3_doc/", "DFT planning, layouts, precision, threading and transform definitions"),
    ("opencv_imgproc", "OpenCV Image Processing", "OpenCV", "official_documentation", "https://docs.opencv.org/4.10.0/d7/da8/tutorial_table_of_content_imgproc.html", "classical image filtering, morphology, transforms, contours and segmentation"),
    ("scikit_image", "scikit-image API", "scikit-image", "official_documentation", "https://scikit-image.org/docs/stable/api/skimage", "classical image filtering, feature, morphology, registration and segmentation"),
    ("itk", "ITK documentation", "Insight Toolkit", "official_documentation", "https://docs.itk.org/en/latest/index.html", "N-dimensional scientific image segmentation and registration"),
    ("blas", "BLAS Technical Forum Standard", "Netlib", "standard", "https://www.netlib.org/blas/blast-forum/", "dense basic linear algebra operation semantics"),
    ("lapack", "LAPACK Users' Guide", "Netlib", "official_documentation", "https://www.netlib.org/lapack/lug/", "dense factorizations, solvers, eigen and singular-value routines"),
    ("onemkl", "oneMKL Specification", "Unified Acceleration Foundation", "standard", "https://oneapi-spec.uxlfoundation.org/specifications/oneapi/latest/elements/onemkl/source/", "portable dense/sparse algebra, FFT, RNG, statistics and vector-math APIs"),
    ("array_api", "Python Array API Standard 2025.12", "Consortium for Python Data API Standards", "standard", "https://data-apis.org/array-api/latest/", "common array/tensor API, semantics and conformance tests"),
    ("numpy_ufunc", "NumPy universal functions", "NumPy", "official_documentation", "https://numpy.org/doc/stable/reference/ufuncs.html", "typed vectorized elementwise, reduction and broadcasting semantics"),
    ("numpy_rng", "NumPy random sampling", "NumPy", "official_documentation", "https://numpy.org/doc/stable/reference/random/index.html", "separation of bit generator, distribution transform, seed and parallel stream"),
    ("scipy_guide", "SciPy User Guide", "SciPy", "official_documentation", "https://docs.scipy.org/doc/scipy/tutorial/", "scientific algorithms across statistics, algebra, signal, sparse and spatial domains"),
    ("faer", "faer documentation", "faer Project", "official_documentation", "https://docs.rs/faer/latest/faer/", "Rust dense and sparse linear algebra implementation surface"),
    ("ndarray", "ndarray documentation", "Rust ndarray Project", "official_documentation", "https://docs.rs/ndarray/latest/ndarray/", "Rust N-dimensional array representation and operations"),
    ("statrs", "statrs documentation", "statrs Project", "official_documentation", "https://docs.rs/statrs/latest/statrs/", "Rust probability distributions and statistical functions"),
    ("linfa", "linfa documentation", "linfa Project", "official_documentation", "https://docs.rs/linfa/latest/linfa/", "Rust fit/predict dataset and classical statistical-learning interfaces"),

    # Columnar execution, physical data kernels and codecs.
    ("arrow_columnar", "Arrow Columnar Format", "Apache Software Foundation", "standard", "https://arrow.apache.org/docs/format/Columnar.html", "language-neutral in-memory layout, types, validity and zero-copy interchange"),
    ("arrow_compute", "Arrow Compute Functions", "Apache Software Foundation", "official_documentation", "https://arrow.apache.org/docs/cpp/api/compute.html", "function registry and typed scalar/vector/aggregate kernels"),
    ("arrow_acero", "Acero streaming execution engine", "Apache Software Foundation", "official_documentation", "https://arrow.apache.org/docs/cpp/acero.html", "streaming execution over Arrow compute kernels"),
    ("parquet_encoding", "Parquet Encoding Definitions", "Apache Software Foundation", "official_specification", "https://parquet.apache.org/docs/file-format/data-pages/encodings/", "plain, dictionary, RLE, bit-pack, delta and byte-stream-split encodings"),
    ("parquet_compression", "Parquet Compression", "Apache Software Foundation", "official_specification", "https://parquet.apache.org/docs/file-format/data-pages/compression/", "page compression codec contract"),
    ("zstd", "Zstandard API Manual", "Meta Zstandard Project", "official_documentation", "https://facebook.github.io/zstd/doc/api_manual_latest.html", "lossless compression levels, dictionaries, streaming, memory and errors"),
    ("snappy_format", "Snappy compressed format description", "Google", "official_specification", "https://github.com/google/snappy/blob/main/format_description.txt", "Snappy LZ77-derived byte-stream format"),
]


SOURCES = [
    {
        "source_id": f"source.method_kernel.{sid}",
        "edition": EDITION,
        "title": title,
        "publisher": publisher,
        "kind": kind,
        "url": url,
        "primary_or_official": True,
        "authority_scope": scope,
        "limitations": "Authority is limited to the named standard, method, implementation or publisher-maintained interface; provider documentation is not independent deployment qualification.",
        "accessed_at": ACCESSED,
    }
    for sid, title, publisher, kind, url, scope in SOURCE_ROWS
]


DECISION_SPECS = [
    ("study_design", "Which observation, sampling, assignment or experimental design is authorized?", "StudyDesignId", ["census", "probability_sample", "randomized", "quasi_experimental", "observational", "simulation"], "analytical_design"),
    ("estimand", "What exact population/time/grain quantity or decision target is sought?", "EstimandRef", [], "analytical_design"),
    ("population_sampling", "What target population, sampling frame and weighting design apply?", "PopulationSamplingSpec", [], "analytical_design"),
    ("missingness", "How are missing, censored, truncated and structurally absent observations treated?", "MissingnessPolicy", ["reject", "complete_case", "pairwise", "impute", "model", "domain_specific"], "analytical_design"),
    ("identification", "Which identification assumptions and falsification checks are required?", "IdentificationContract", [], "analytical_design"),
    ("multiplicity", "How are multiple looks, hypotheses, outcomes or groups controlled?", "MultiplicityPolicy", ["none_justified", "familywise", "false_discovery", "hierarchical", "sequential_spending"], "analytical_design"),
    ("uncertainty", "Which uncertainty representation and coverage semantics are required?", "UncertaintyPolicy", ["none_justified", "standard_error", "confidence_interval", "credible_interval", "prediction_interval", "distribution", "scenario"], "analytical_design"),
    ("evaluation_split", "How are fit, tune, calibration and final evaluation observations separated?", "EvaluationPartitionPolicy", ["none_not_fitted", "holdout", "cross_validation", "rolling_origin", "blocked", "nested", "external"], "analytical_design"),
    ("evaluation_metric", "Which loss, score, residual or domain utility determines acceptance?", "EvaluationMeasureRef", [], "analytical_design"),
    ("forecast_horizon", "What forecast origin, horizon, frequency and update cadence apply?", "ForecastHorizonSpec", [], "analytical_design"),
    ("forecast_reconciliation", "How must hierarchical or grouped forecasts cohere?", "ForecastReconciliationPolicy", ["none", "bottom_up", "top_down", "middle_out", "optimal_combination"], "analytical_design"),
    ("anomaly_threshold", "How is an anomaly score converted to a case, alert or refusal?", "ThresholdPolicy", ["fixed", "quantile", "cost_sensitive", "adaptive", "human_review"], "analytical_design"),
    ("experiment_unit_identity", "What entity, cluster or device is randomized, assigned, exposed and analyzed, and how are identity changes handled?", "ExperimentUnitPolicy", [], "semantic_closure"),
    ("experiment_eligibility", "Which prospective rule and as-of time determine eligibility and enrollment?", "EligibilityPolicy", [], "analytical_design"),
    ("experiment_assignment", "Which randomization, allocation, stratification, clustering and salt/stream semantics assign eligible units?", "AssignmentMechanism", [], "analytical_design"),
    ("experiment_assignment_persistence", "When does an assignment remain stable, reset, migrate or stop accepting new units?", "AssignmentPersistencePolicy", ["ephemeral", "sticky_until_reset", "sticky_until_end", "epoch_versioned"], "deployment_binding"),
    ("experiment_interference", "Which mutual-exclusion, overlap, spillover and interference assumptions constrain simultaneous experiments?", "ExperimentInterferencePolicy", [], "analytical_design"),
    ("experiment_exposure", "What occurrence proves that an assigned unit actually received a treatment, and how are duplicates and noncompliance represented?", "ExposureOccurrencePolicy", [], "observation_planning"),
    ("experiment_analysis_cut", "Which assignment, exposure, metric and late-arrival cuts form one immutable analysis snapshot?", "ExperimentAnalysisCutPolicy", [], "analytical_design"),
    ("experiment_stopping", "Which prospective duration, information, error-spending or safety rule permits an interim look or stop?", "ExperimentStoppingPolicy", [], "analytical_design"),
    ("experiment_override", "Which authority may override assignment, for which purpose, and how is the unit excluded or retained in analysis?", "ExperimentOverridePolicy", ["forbidden", "test_only_excluded", "authorized_operational_excluded", "declared_analysis_specific"], "deployment_binding"),
    ("process_perspective", "Is the process representation case-centric or object-centric, and which identities are authoritative?", "ProcessPerspective", ["single_case", "multi_log_view", "object_centric"], "semantic_closure"),
    ("conformance_cost", "What deviation, alignment and incompleteness costs are semantically valid?", "ConformanceCostModel", [], "analytical_design"),
    ("graph_semantics", "What directedness, multiplicity, self-loop, weight, temporal and property semantics apply?", "GraphSemanticProfile", [], "semantic_closure"),
    ("spatial_reference", "Which CRS, axis order, datum, dimensionality and distance model apply?", "SpatialReferencePolicy", [], "semantic_closure"),
    ("text_locale", "Which Unicode version, normalization, locale, segmentation and collation rules apply?", "TextProcessingProfile", [], "semantic_closure"),
    ("retrieval_ranking", "Which query semantics, ranking formula, field weights and tie order apply?", "RetrievalRankingPolicy", [], "analytical_design"),
    ("document_profile", "Which exact media type, container/profile edition and conformance level govern parsing?", "DocumentProfile", [], "semantic_closure"),
    ("document_recursion", "How are package parts, attachments, embedded resources and recursion limits represented?", "DocumentRecursionPolicy", [], "observation_planning"),
    ("document_encryption", "How are encrypted, signed, password-protected or rights-constrained documents admitted or refused?", "DocumentProtectionPolicy", [], "assurance_insertion"),
    ("document_coordinates", "Which page, crop, rotation, origin, unit and transform define element coordinates?", "DocumentCoordinatePolicy", [], "semantic_closure"),
    ("document_reading_order", "Which tagged, source, geometric or explicitly uncertain reading order applies?", "ReadingOrderPolicy", ["source_declared", "tagged_structure", "geometric", "provider_inferred_with_confidence", "unordered"], "semantic_closure"),
    ("document_text_normalization", "How are glyph codes, Unicode mapping, whitespace, hyphenation and normalization represented without losing source text?", "DocumentTextPolicy", [], "semantic_closure"),
    ("ocr_language_script", "Which OCR languages, scripts, orientation and trained-data editions are allowed?", "OcrLanguageScriptPolicy", [], "analytical_design"),
    ("ocr_segmentation", "Which page segmentation, preprocessing, recognition and confidence semantics apply?", "OcrSegmentationPolicy", [], "analytical_design"),
    ("document_layout", "Which line, block, region, heading, list, figure and reading-order model applies?", "DocumentLayoutPolicy", [], "analytical_design"),
    ("document_table", "Which detection, row/column grid, spanning-cell, header and continuation semantics define a table?", "DocumentTablePolicy", [], "analytical_design"),
    ("document_form", "Which native field, widget, appearance, key/value and signature semantics define form extraction?", "DocumentFormPolicy", [], "semantic_closure"),
    ("document_provenance", "Which byte/part/page/coordinate, extractor edition, confidence and loss evidence accompanies every extracted element?", "DocumentProvenancePolicy", [], "evidence_verification"),
    ("document_resource_safety", "What size, page, nesting, expansion, image, timeout and cancellation limits constrain hostile documents?", "DocumentResourcePolicy", [], "deployment_binding"),
    ("document_label_taxonomy", "Which versioned single/multi-label taxonomy, hierarchy, thresholds and unknown label govern document classification?", "DocumentLabelTaxonomy", [], "analytical_design"),
    ("document_field_schema", "Which fields, spans, relations, cardinalities, types, normalization and evidence are extracted?", "DocumentExtractionSchema", [], "analytical_design"),
    ("document_extraction_match", "Which exact, normalized, span-overlap, relation, cell/grid or hierarchical matching rule defines correctness?", "DocumentExtractionMatchPolicy", [], "evidence_verification"),
    ("document_abstention", "When must classification or extraction abstain, defer or emit alternatives rather than invent a value?", "DocumentAbstentionPolicy", [], "analytical_design"),
    ("signal_sampling", "What sample rate, clock, anti-alias, boundary and resampling policy apply?", "SignalSamplingPolicy", [], "observation_planning"),
    ("image_coordinates", "What pixel/voxel spacing, origin, orientation, channel and intensity semantics apply?", "ImageCoordinatePolicy", [], "semantic_closure"),
    ("metric_grain", "At which entity grain, time spine and dimensions may the measure be evaluated?", "MetricGrainPolicy", [], "semantic_closure"),
    ("aggregation_algebra", "Which aggregation, decomposability and semi-additivity laws apply?", "AggregationAlgebraRef", [], "semantic_closure"),
    ("precision", "Which numeric dtype, accumulation precision, overflow and NaN laws apply?", "NumericPolicy", ["exact_integer", "decimal", "binary32", "binary64", "mixed", "arbitrary"], "physical_binding"),
    ("determinism", "What reproducibility level is required across calls, threads, targets and provider versions?", "DeterminismPolicy", ["same_call", "same_binary_target", "cross_thread", "cross_device", "cross_provider"], "physical_binding"),
    ("random_stream", "Which RNG family, seed, stream splitting and replay rules apply?", "RandomStreamPolicy", [], "physical_binding"),
    ("layout", "Which shape, strides, contiguity, sparsity and ownership layouts are accepted?", "ArrayLayoutPolicy", [], "physical_binding"),
    ("kernel_backend", "Which qualified kernel offer may implement each primitive on the target?", "KernelOfferRef", [], "physical_binding"),
    ("resource_budget", "What finite work, memory, wall-time, thread and device budgets apply?", "ResourceBudget", [], "physical_binding"),
    ("cancellation", "Where are cancellation safe points and what partial artifacts may survive?", "CancellationPolicy", [], "deployment_binding"),
    ("compression", "Which representation encoding, codec, level, dictionary, framing and integrity policy apply?", "CompressionBindingPolicy", [], "physical_binding"),
    ("artifact_persistence", "Which fitted/index/plan artifacts are serializable, compatible and invalidated by change?", "ArtifactPersistencePolicy", [], "deployment_binding"),
    ("ffi_safety", "May an FFI/device/provider boundary be used and which memory, panic and error contracts govern it?", "FfiSafetyPolicy", ["pure_rust_only", "ffi_allowed_qualified", "external_runtime_allowed"], "physical_binding"),
]


def decision_record(spec: tuple) -> dict:
    slug, question, value_contract, allowed_values, phase = spec
    return {
        "decision_id": f"decision.method_kernels.{slug}",
        "edition": EDITION,
        "status": "declared",
        "owner_context_ref": "context.method_kernel_binding",
        "question": question,
        "value_contract": value_contract,
        "allowed_values": allowed_values,
        "binding_phase": phase,
        "authority_ref": "authority.analytical_design_or_platform_policy",
        "default_law": "forbidden",
        "default_value": None,
        "constraints": ["The selected value must be valid for the resolved semantic and study contract."],
        "conflicts": ["Provider defaults cannot override an authored or authority-owned value."],
        "implications": ["Changing this decision invalidates dependent plans, artifacts, results and evidence."],
        "affects_contracts": ["contract.method_kernel.execution"],
        "evidence_required": ["decision authority", "resolved value", "applicability evidence"],
        "change_semantics": ["Recompile affected logical and physical plans and requalify invalidated artifacts."],
        "gaps": ["Domain-specific allowed values and precedence require vertical binding."],
    }


DECISIONS = [decision_record(spec) for spec in DECISION_SPECS]


DOMAIN_DEFAULTS = {
    "descriptive": {
        "owner": "context.descriptive_statistics",
        "practice": ["analytics.descriptive"],
        "study": ["Declare population, inclusion, grain, grouping, weights and missingness before computation."],
        "estimand": ["Define the exact sample or population functional, units and grouping domain."],
        "inputs": ["typed observations with population, grain, time, units and missingness qualifiers"],
        "assumptions": ["grouping and weights preserve the intended population", "missingness handling is explicit"],
        "formula": ["Function domain, equality, ordering, null/NaN and empty-input semantics are fixed."],
        "estimator": ["Distinguish an exact sample functional from an estimator of a population functional."],
        "outputs": ["typed statistic, population/grain key and computation receipt"],
        "uncertainty": ["Sampling uncertainty is emitted only when a sampling design and estimator justify it."],
        "evaluation": ["Compare against hand fixtures, algebraic laws and an independent implementation."],
        "artifact": ["definition", "compiled aggregation plan", "result receipt"],
        "algorithm": ["stable finite algorithm whose approximation and merge laws are declared"],
        "kernels": ["typed reductions", "ordering/selection", "group partitioning"],
        "decisions": ["population_sampling", "missingness", "metric_grain", "aggregation_algebra", "precision"],
    },
    "inferential": {
        "owner": "context.statistical_inference",
        "practice": ["analytics.inferential"],
        "study": ["Declare sampling, dependence, censoring, covariate and analysis plan before inference."],
        "estimand": ["Name the population parameter and conditioning/intervention set exactly."],
        "inputs": ["study observations", "sampling/cluster/weight metadata", "analysis design"],
        "assumptions": ["identifiability and regularity assumptions are explicit", "dependence structure is not silently ignored"],
        "formula": ["Likelihood, estimating equation, prior or test statistic is versioned and inspectable."],
        "estimator": ["Bias, consistency, variance and finite/asymptotic claim boundaries are declared."],
        "outputs": ["estimate or test result", "uncertainty", "diagnostics", "assumption and provenance receipt"],
        "uncertainty": ["Coverage semantics, approximation regime and multiplicity are explicit."],
        "evaluation": ["Simulation calibration, residual diagnostics and reference fixtures are required."],
        "artifact": ["analysis plan", "fitted parameters", "variance state", "diagnostics", "result"],
        "algorithm": ["convergence and numerical-failure states remain distinct from a valid estimate"],
        "kernels": ["linear algebra", "special functions", "optimization", "random variates"],
        "decisions": ["study_design", "estimand", "population_sampling", "missingness", "multiplicity", "uncertainty", "precision", "random_stream"],
    },
    "experimental": {
        "owner": "context.experimental_design",
        "practice": ["analytics.experimental"],
        "study": ["Assignment, blocking, stopping, exclusion and analysis rules are prospective and authority-approved."],
        "estimand": ["Treatment contrast, population and interference assumptions are fixed before outcomes are inspected."],
        "inputs": ["units", "treatments", "covariates/blocks", "outcomes", "assignment and exposure records"],
        "assumptions": ["assignment mechanism is preserved", "interference and noncompliance are addressed"],
        "formula": ["Design probabilities and analysis estimators are linked without post-hoc substitution."],
        "estimator": ["Estimator matches the randomization, clustering and repeated-look design."],
        "outputs": ["effect estimate", "uncertainty", "balance and protocol-deviation diagnostics"],
        "uncertainty": ["Randomization or model-based inference is labeled and multiplicity/stopping adjustments applied."],
        "evaluation": ["Allocation integrity, balance, attrition, protocol and sensitivity checks are required."],
        "artifact": ["protocol", "randomization plan", "analysis plan", "locked data", "result"],
        "algorithm": ["randomization, allocation and analysis are separately reproducible"],
        "kernels": ["RNG", "stratification", "regression", "resampling"],
        "decisions": ["study_design", "estimand", "population_sampling", "identification", "multiplicity", "evaluation_split", "random_stream"],
    },
    "causal": {
        "owner": "context.causal_analysis",
        "practice": ["analytics.causal"],
        "study": ["Represent treatment, outcome, timing, population, assignment and causal assumptions."],
        "estimand": ["Name potential-outcome or structural estimand, treatment version and target population."],
        "inputs": ["treatment/exposure", "outcome", "covariates", "time", "assignment/instrument/running-variable evidence"],
        "assumptions": ["identification assumptions are explicit and cannot be inferred from estimator choice", "post-treatment leakage is prohibited"],
        "formula": ["Identification formula is separated from the statistical estimator."],
        "estimator": ["Nuisance estimation, overlap, weighting and variance procedure are declared."],
        "outputs": ["identified estimand or not-identified result", "estimate", "uncertainty", "refutations/sensitivity"],
        "uncertainty": ["Sampling, nuisance and sensitivity uncertainty are not collapsed."],
        "evaluation": ["Placebo, balance, overlap, pre-trend, falsification and sensitivity checks are method-specific."],
        "artifact": ["causal graph/argument", "identification proof", "fitted nuisance artifacts", "effect result"],
        "algorithm": ["Cross-fitting, optimization and bootstrap partitions are reproducible and leakage-safe."],
        "kernels": ["regression/classification", "weighting", "matching/search", "resampling", "linear algebra"],
        "decisions": ["study_design", "estimand", "identification", "missingness", "evaluation_split", "uncertainty", "random_stream"],
    },
    "forecasting": {
        "owner": "context.forecasting",
        "practice": ["analytics.forecasting"],
        "study": ["Forecast origin, information set, horizon, frequency, revision and evaluation window are fixed."],
        "estimand": ["Target value/distribution and availability time are distinct from observed future revisions."],
        "inputs": ["ordered time-indexed observations", "calendar", "known-future regressors", "hierarchy and revision metadata"],
        "assumptions": ["training rows contain only information available at each origin", "time-zone and frequency semantics are stable"],
        "formula": ["Model dynamics, seasonal structure and transformation/inversion rules are explicit."],
        "estimator": ["Fit/update procedure and state initialization are versioned."],
        "outputs": ["point or distributional forecast by origin/horizon", "intervals/quantiles", "diagnostics"],
        "uncertainty": ["Forecast uncertainty is horizon-indexed and distinguishes parameter, innovation and scenario uncertainty."],
        "evaluation": ["Rolling-origin evaluation against declared baselines and horizon-specific scores is required."],
        "artifact": ["transformation", "fitted state", "forecast origin", "forecast", "actual/revision", "score"],
        "algorithm": ["Fit, filter, smooth, forecast and update transitions have distinct receipts."],
        "kernels": ["time alignment", "linear algebra", "optimization", "probability distribution", "reconciliation"],
        "decisions": ["forecast_horizon", "forecast_reconciliation", "missingness", "uncertainty", "evaluation_split", "evaluation_metric", "precision"],
    },
    "anomaly_change": {
        "owner": "context.anomaly_and_change",
        "practice": ["analytics.anomaly_detection", "analytics.change_detection"],
        "study": ["Define reference regime, contamination, update policy and consequences of alerts."],
        "estimand": ["Anomaly score, change time or process state is distinct from alert/case policy."],
        "inputs": ["observations or event stream", "reference window/model", "context and labels when available"],
        "assumptions": ["reference regime and exchangeability/stationarity limits are explicit", "feedback contamination is controlled"],
        "formula": ["Score/statistic and threshold policy are separate governed objects."],
        "estimator": ["Fit/calibration/update procedure declares contamination and forgetting."],
        "outputs": ["score or change evidence", "threshold decision", "case/alert receipt"],
        "uncertainty": ["False alarm, detection delay and calibration uncertainty are reported where estimable."],
        "evaluation": ["Time-aware labeled evaluation, synthetic injection or statistical false-alarm calibration is required."],
        "artifact": ["reference state", "scorer", "threshold", "alert", "adjudication feedback"],
        "algorithm": ["Online state, warm-up, reset and late/out-of-order handling are explicit."],
        "kernels": ["stream statistics", "distance", "tree traversal", "windowing"],
        "decisions": ["anomaly_threshold", "evaluation_split", "evaluation_metric", "resource_budget", "determinism"],
    },
    "process": {
        "owner": "context.process_mining",
        "practice": ["analytics.process_mining"],
        "study": ["Event/object identity, activity semantics, timestamps, lifecycle and case/object perspective are explicit."],
        "estimand": ["Discovered behavior, deviation, performance or organizational relation is scoped to an event-log view."],
        "inputs": ["qualified event or object-centric event log", "optional reference model", "calendar/resource semantics"],
        "assumptions": ["event extraction is evidenced", "flattening or case selection does not silently distort multiplicity"],
        "formula": ["Process-model and conformance semantics are versioned independently from visualization."],
        "estimator": ["Discovery/conformance parameters and noise thresholds are explicit."],
        "outputs": ["process model, conformance/performance result, variants and evidence links"],
        "uncertainty": ["Sampling, incompleteness and extraction uncertainty are retained when known."],
        "evaluation": ["Fitness, precision, simplicity, generalization and domain validation are distinct."],
        "artifact": ["event-log view", "process model", "alignment/replay", "performance result"],
        "algorithm": ["Algorithm input class, soundness/termination and approximation status are explicit."],
        "kernels": ["graph traversal", "search/alignment", "aggregation", "temporal ordering"],
        "decisions": ["process_perspective", "conformance_cost", "metric_grain", "resource_budget"],
    },
    "data_quality": {
        "owner": "context.data_quality",
        "practice": ["analytics.data_quality"],
        "study": ["Define the data product, population/snapshot, rule authority and acceptance consequence."],
        "estimand": ["A quality measure or assertion is scoped to exact data, rule edition and evaluation time."],
        "inputs": ["versioned data snapshot/stream", "quality rules/constraints", "reference data", "lineage"],
        "assumptions": ["rule scope and null semantics are explicit", "sampling does not masquerade as full validation"],
        "formula": ["Metric formula, threshold and assertion are three distinct objects."],
        "estimator": ["Approximate profiles declare error and confidence; exact checks declare scanned scope."],
        "outputs": ["measurements", "pass/warn/fail/error assertions", "failing evidence and coverage receipt"],
        "uncertainty": ["Sampling/sketch uncertainty and detection coverage are emitted."],
        "evaluation": ["Seeded defects, negative twins, reference reconciliation and rule mutation tests are required."],
        "artifact": ["rule suite", "scan plan", "measurement", "validation result", "evidence sample"],
        "algorithm": ["Pushdown and incremental evaluation must preserve rule semantics."],
        "kernels": ["aggregations", "distinct/sketch", "pattern/predicate", "join/reconciliation"],
        "decisions": ["metric_grain", "missingness", "aggregation_algebra", "evaluation_metric", "resource_budget"],
    },
    "reliability": {
        "owner": "context.reliability_analysis",
        "practice": ["analytics.reliability"],
        "study": ["Failure, censoring, repair, exposure, cohort and observation-window semantics are declared."],
        "estimand": ["Reliability, hazard, availability or degradation target is defined at a mission time and population."],
        "inputs": ["failure/repair/exposure records", "censoring/truncation", "covariates", "inspection/degradation observations"],
        "assumptions": ["censoring and recurrence assumptions are explicit", "asset identity and operating regime are stable"],
        "formula": ["Failure-time, repair or degradation model and mission profile are versioned."],
        "estimator": ["Censoring-aware estimator and variance procedure are required."],
        "outputs": ["survival/reliability/hazard/availability estimate", "uncertainty", "diagnostics"],
        "uncertainty": ["Censoring, parameter and extrapolation uncertainty are distinguished."],
        "evaluation": ["Calibration, residuals, held-out cohorts and engineering plausibility checks are required."],
        "artifact": ["cohort definition", "fitted life/degradation model", "reliability result"],
        "algorithm": ["Risk sets, ties, recurrent events and numerical convergence are explicit."],
        "kernels": ["sorting", "risk-set aggregation", "optimization", "integration"],
        "decisions": ["estimand", "missingness", "uncertainty", "evaluation_split", "precision"],
    },
    "queue_simulation": {
        "owner": "context.simulation_analysis",
        "practice": ["analytics.simulation", "analytics.queueing"],
        "study": ["System boundary, entities/resources, event/time semantics, experiment and replications are declared."],
        "estimand": ["Steady-state/transient performance functional and warm-up/horizon are explicit."],
        "inputs": ["system model", "arrival/service/transition inputs", "scenario and random streams"],
        "assumptions": ["input models and independence/dependence structure are justified", "simulation is not claimed as real-system truth"],
        "formula": ["State-transition and event-calendar semantics are inspectable."],
        "estimator": ["Replication, batching, warm-up and output-analysis procedure are explicit."],
        "outputs": ["simulation traces", "performance distributions", "confidence/error assessment"],
        "uncertainty": ["Input, stochastic, parameter and structural uncertainty are separated."],
        "evaluation": ["Verification, validation, sensitivity and independent replication are required."],
        "artifact": ["model", "experiment", "random streams", "run receipts", "output analysis"],
        "algorithm": ["Event ordering, simultaneous-event policy and cancellation preserve valid partial results."],
        "kernels": ["priority queue", "RNG", "distribution sampling", "aggregation"],
        "decisions": ["study_design", "estimand", "random_stream", "resource_budget", "cancellation", "uncertainty"],
    },
    "operations_research_bridge": {
        "owner": "context.or_method_bridge",
        "practice": ["analytics.operations_research"],
        "study": ["Delegate decision-problem, solver, heuristic and proof semantics to the dedicated OR corpus."],
        "estimand": ["Decision objective, feasibility and evidence target are referenced without duplication."],
        "inputs": ["DecisionProblemIR or OR qualification contract"],
        "assumptions": ["the OR record edition resolves", "this bridge does not strengthen solver claims"],
        "formula": ["Objective/constraint semantics remain owned by the OR corpus."],
        "estimator": ["Not applicable unless the referenced OR method contains statistical estimation."],
        "outputs": ["resolved OR requirement or typed unresolved-reference gap"],
        "uncertainty": ["Inherited exactly from the referenced OR contract."],
        "evaluation": ["OR qualification and post-solve validation receipts are mandatory."],
        "artifact": ["OR reference", "binding", "result mapping"],
        "algorithm": ["No local algorithm duplicates the OR method."],
        "kernels": ["Only kernel requirements exported by the resolved OR plan are bound here."],
        "decisions": ["resource_budget", "determinism", "precision", "kernel_backend"],
    },
    "graph": {
        "owner": "context.graph_analysis",
        "practice": ["analytics.graph"],
        "study": ["Graph entity/edge identity, directedness, multiplicity, weights, time and sampling are declared."],
        "estimand": ["Graph property or derived structure is tied to an exact graph snapshot/view."],
        "inputs": ["typed graph or sparse matrix", "weight/semiring", "source/target or query parameters"],
        "assumptions": ["graph projection and missing edges are not treated as true absence", "weight algebra is valid"],
        "formula": ["Graph definition and algebra/semiring are independent of storage representation."],
        "estimator": ["Approximate/sampled graph estimates declare error and sampling assumptions."],
        "outputs": ["typed graph property, path/community/subgraph or score", "algorithm receipt"],
        "uncertainty": ["Sampling/approximation uncertainty is emitted when applicable."],
        "evaluation": ["Small exact fixtures, invariants, reference algorithms and metamorphic graph tests are required."],
        "artifact": ["graph view", "algorithm plan", "result"],
        "algorithm": ["Complexity and behavior for directed, multi-edge, negative-weight and disconnected cases are explicit."],
        "kernels": ["sparse matrix/vector", "semiring operations", "priority queue", "sort/reduce"],
        "decisions": ["graph_semantics", "precision", "layout", "kernel_backend", "resource_budget"],
    },
    "spatial": {
        "owner": "context.spatial_analysis",
        "practice": ["analytics.spatial"],
        "study": ["Feature identity, geometry validity, CRS, axis order, scale and sampling support are declared."],
        "estimand": ["Spatial relation, field or statistic is scoped to coordinate/reference and support semantics."],
        "inputs": ["typed geometry/raster/feature observations", "CRS", "spatial weights or neighborhood"],
        "assumptions": ["coordinate transformations and distance models are valid", "support/change-of-support is addressed"],
        "formula": ["Topology and metric formulas preserve CRS and dimensionality preconditions."],
        "estimator": ["Spatial dependence and edge/boundary corrections are explicit."],
        "outputs": ["geometry, spatial relation/statistic/field or transformed feature", "precision/provenance receipt"],
        "uncertainty": ["Measurement, positional, interpolation and model uncertainty are distinct."],
        "evaluation": ["OGC fixtures, CRS round trips, topology validity and spatial cross-validation are required."],
        "artifact": ["spatial reference", "weights/index/model", "result"],
        "algorithm": ["Robust-predicate and tolerance semantics are provider-qualified."],
        "kernels": ["geometry predicate/overlay", "coordinate transform", "spatial index", "linear algebra"],
        "decisions": ["spatial_reference", "precision", "layout", "resource_budget"],
    },
    "text_search": {
        "owner": "context.text_and_search",
        "practice": ["analytics.text", "analytics.search"],
        "study": ["Corpus, locale, query intent, relevance judgments and update policy are declared."],
        "estimand": ["Text unit, lexical statistic or ranking/retrieval target is fixed."],
        "inputs": ["Unicode text/documents", "schema/fields", "locale/analyzer", "queries and judgments"],
        "assumptions": ["normalization/tokenization are appropriate for language and domain", "ranking labels represent the target users"],
        "formula": ["Analyzer pipeline and scoring formula are versioned separately from the index."],
        "estimator": ["Corpus statistics and tuned ranking parameters identify their snapshot."],
        "outputs": ["tokens/features/index/ranked results", "score explanation and analyzer/index receipt"],
        "uncertainty": ["Evaluation uncertainty and incomplete relevance judgments are retained."],
        "evaluation": ["Unicode conformance, analyzer golden tests and retrieval effectiveness/latency evaluation are required."],
        "artifact": ["analyzer", "lexicon/index", "ranking profile", "query result"],
        "algorithm": ["Index-time/search-time compatibility and deterministic tie ordering are explicit."],
        "kernels": ["Unicode transform", "automaton/FST", "postings intersection", "ranking", "top-k"],
        "decisions": ["text_locale", "retrieval_ranking", "evaluation_metric", "layout", "compression"],
    },
    "signal": {
        "owner": "context.signal_analysis",
        "practice": ["analytics.signal"],
        "study": ["Sampling clock/rate, sensor calibration, bandwidth, window and boundary conditions are declared."],
        "estimand": ["Time/frequency-domain component or event target names normalization and units."],
        "inputs": ["sampled signal", "sample times/rate", "units", "channel and calibration metadata"],
        "assumptions": ["anti-alias and sampling requirements are met", "stationarity/locality assumptions are explicit"],
        "formula": ["Transform/filter definition includes normalization, phase and boundary conventions."],
        "estimator": ["Spectral/signal estimator states windowing, overlap, detrending and variance behavior."],
        "outputs": ["filtered/transformed signal, spectrum/features/events", "frequency/time coordinates"],
        "uncertainty": ["Noise, spectral leakage, resolution and estimator variance are represented."],
        "evaluation": ["Synthetic tones/impulses, round trips, conservation laws and reference implementations are required."],
        "artifact": ["filter/transform plan", "state", "result"],
        "algorithm": ["Streaming state, latency, overlap and numerical precision are explicit."],
        "kernels": ["convolution", "FFT", "matrix/vector", "resampling"],
        "decisions": ["signal_sampling", "precision", "layout", "kernel_backend", "resource_budget"],
    },
    "image": {
        "owner": "context.image_analysis",
        "practice": ["analytics.image_classical"],
        "study": ["Pixel/voxel geometry, modality, calibration, annotation and evaluation unit are declared."],
        "estimand": ["Region, boundary, transform, registration or measurement target is exact."],
        "inputs": ["typed raster/image/volume", "spacing/orientation", "intensity/channel semantics", "optional markers/reference"],
        "assumptions": ["intensity and coordinate conventions are valid", "preprocessing does not erase target evidence"],
        "formula": ["Neighborhood, structuring element, interpolation and boundary semantics are explicit."],
        "estimator": ["Threshold/registration/segmentation parameter estimation is versioned."],
        "outputs": ["transformed image, labels/geometry/features/measurements", "quality metrics"],
        "uncertainty": ["Resolution, registration and segmentation uncertainty are retained where available."],
        "evaluation": ["Phantoms/golden images, geometric invariants and task-specific segmentation/registration metrics are required."],
        "artifact": ["transform/filter", "label map/registration", "measurement result"],
        "algorithm": ["Connectivity, interpolation, padding and tie semantics are explicit."],
        "kernels": ["convolution", "morphology", "connected components", "interpolation", "FFT"],
        "decisions": ["image_coordinates", "precision", "layout", "kernel_backend", "resource_budget"],
    },
    "semantic_metric": {
        "owner": "context.semantic_metric_evaluation",
        "practice": ["analytics.semantic_metric"],
        "study": ["Business entity, grain, population, valid time, dimensions and decision use are declared."],
        "estimand": ["Measure definition includes unit, aggregation algebra, filters, time and comparability."],
        "inputs": ["semantic entities/dimensions", "facts/observations", "formula", "time spine", "policy"],
        "assumptions": ["join paths preserve grain and cardinality", "units/currencies and validity times are compatible"],
        "formula": ["Formula AST is typed, totality-aware and separate from provider SQL."],
        "estimator": ["Approximate aggregations declare error; ordinary semantic metrics are evaluations, not statistical estimators."],
        "outputs": ["metric observation keyed by entity/dimensions/time", "lineage and formula edition"],
        "uncertainty": ["Source measurement and approximate-computation uncertainty propagate through supported formulas."],
        "evaluation": ["Algebraic laws, join-cardinality counterexamples, exact fixtures and cross-backend conformance are required."],
        "artifact": ["metric definition", "bound semantic graph", "lowered query", "metric observation"],
        "algorithm": ["Lowering must preserve grain, null, time, unit and aggregation laws."],
        "kernels": ["join/group/reduce", "formula evaluation", "time alignment", "unit conversion"],
        "decisions": ["metric_grain", "aggregation_algebra", "missingness", "precision", "kernel_backend"],
    },
}


METHOD_SPECS = {
    "descriptive": [
        ("univariate_summary", "Univariate summary statistics", "Compute governed count, center, dispersion, range and moments for one variable.", ["nist_handbook", "scipy_stats"]),
        ("grouped_summary", "Grouped descriptive statistics", "Evaluate descriptive functionals independently at an authorized grouping grain.", ["nist_handbook", "arrow_compute"]),
        ("empirical_distribution", "Empirical distribution estimation", "Represent the observed distribution through empirical CDF, histogram or density estimate.", ["scipy_stats", "r_stats"]),
        ("quantile_estimation", "Quantile and percentile estimation", "Estimate order-based population or sample cut points under a named quantile convention.", ["scipy_stats", "numpy_ufunc"]),
        ("contingency_analysis", "Contingency-table analysis", "Summarize joint categorical frequencies, margins and association measures.", ["scipy_stats", "statsmodels_guide"]),
        ("robust_summary", "Robust descriptive statistics", "Summarize center and spread with bounded or reduced sensitivity to extremes.", ["nist_handbook", "statsmodels_guide"]),
        ("exploratory_analysis", "Exploratory data analysis", "Reveal distributional, relational and structural features without converting exploration into confirmatory evidence.", ["nist_handbook"]),
        ("mergeable_sketch", "Mergeable approximate summaries", "Estimate count-distinct, quantile, frequency or moment summaries with declared merge and error laws.", ["arrow_compute", "deequ"]),
    ],
    "inferential": [
        ("point_estimation", "Point estimation", "Estimate a named population parameter from a declared sampling model.", ["scipy_stats", "r_stats"]),
        ("interval_estimation", "Confidence and uncertainty interval estimation", "Construct an interval with an explicit repeated-sampling or posterior interpretation.", ["scipy_stats", "stan_reference"]),
        ("hypothesis_testing", "Hypothesis testing", "Evaluate a predeclared null/alternative using a test statistic and controlled rejection rule.", ["asa_pvalue", "scipy_stats"]),
        ("linear_regression", "Linear regression", "Estimate a conditional linear mean relationship with declared error and covariance assumptions.", ["statsmodels_guide", "r_stats"]),
        ("generalized_linear_model", "Generalized linear modeling", "Relate a response distribution to predictors through a declared link and variance family.", ["statsmodels_guide"]),
        ("robust_regression", "Robust regression", "Fit regression under reduced sensitivity to outliers or misspecified error tails.", ["statsmodels_guide"]),
        ("quantile_regression", "Quantile regression", "Estimate conditional quantiles rather than a conditional mean.", ["statsmodels_guide"]),
        ("mixed_effects", "Hierarchical and mixed-effects modeling", "Estimate fixed and random effects for nested or crossed dependence structures.", ["statsmodels_guide", "r_stats"]),
        ("generalized_estimating_equations", "Generalized estimating equations", "Estimate marginal response relationships under repeated or clustered observations.", ["statsmodels_guide"]),
        ("bayesian_inference", "Bayesian inference", "Update a declared prior and likelihood into posterior quantities with diagnostic evidence.", ["stan_reference", "pymc_api"]),
        ("resampling_inference", "Bootstrap and resampling inference", "Approximate sampling behavior using a resampling scheme that preserves the design's dependence structure.", ["scipy_stats", "r_stats"]),
        ("permutation_randomization_test", "Permutation and randomization tests", "Evaluate a statistic under transformations justified by exchangeability or assignment.", ["scipy_stats", "sklearn_evaluation"]),
        ("multiple_comparison", "Multiplicity control", "Control family-wise, false-discovery or sequential error across related inferential claims.", ["asa_pvalue", "statsmodels_guide"]),
        ("meta_analysis", "Evidence synthesis and meta-analysis", "Combine compatible study effects while modeling heterogeneity and publication/selection limits.", ["statsmodels_guide"]),
    ],
    "experimental": [
        ("completely_randomized", "Completely randomized experiment", "Assign eligible units to treatments by a governed random mechanism.", ["consort", "nist_handbook"]),
        ("blocked_randomized", "Blocked or stratified randomized experiment", "Randomize within predeclared blocks to improve balance and precision.", ["nist_handbook", "consort"]),
        ("factorial_design", "Factorial experimental design", "Estimate main and interaction effects by jointly varying multiple factors.", ["nist_handbook"]),
        ("fractional_factorial", "Fractional-factorial and screening design", "Trade run count for a declared alias structure when screening factors.", ["nist_handbook"]),
        ("sequential_design", "Sequential experiment design", "Allow prospectively governed interim looks or allocation changes with error control.", ["fda_adaptive"]),
        ("adaptive_design", "Adaptive experiment design", "Modify declared design aspects using accumulating information under a prospective rule.", ["fda_adaptive"]),
        ("power_sample_size", "Power and sample-size design", "Choose enrollment or observation count from effect, variance, error and attrition assumptions.", ["nist_handbook", "fda_adaptive"]),
    ],
    "causal": [
        ("graph_identification", "Causal graph identification", "Derive whether and how a causal estimand is identified under a graph and assumptions.", ["dowhy_paper", "dowhy_docs"]),
        ("regression_adjustment", "Outcome-regression adjustment", "Estimate an intervention contrast by modeling conditional outcomes under exchangeability.", ["dowhy_docs", "statsmodels_guide"]),
        ("propensity_score", "Propensity-score modeling", "Estimate treatment-assignment propensity as an input to balance, matching or weighting.", ["dowhy_docs", "econml_docs"]),
        ("inverse_probability_weighting", "Inverse-probability weighting", "Reweight observations to represent a target intervention population under positivity.", ["dowhy_docs", "doubleml_docs"]),
        ("matching", "Causal matching", "Construct comparable treated and control sets under an explicit distance and overlap policy.", ["dowhy_docs"]),
        ("doubly_robust", "Doubly robust effect estimation", "Combine treatment and outcome nuisance models under a declared robustness theorem.", ["doubleml_docs", "econml_docs"]),
        ("instrumental_variables", "Instrumental-variable estimation", "Identify treatment effects using relevance, exclusion and independence assumptions.", ["doubleml_docs", "statsmodels_guide"]),
        ("difference_in_differences", "Difference-in-differences", "Estimate treatment effects from treated/control changes under parallel-trend assumptions.", ["doubleml_docs"]),
        ("regression_discontinuity", "Regression-discontinuity design", "Estimate a local treatment effect at an assignment threshold under continuity assumptions.", ["doubleml_docs"]),
        ("synthetic_control", "Synthetic-control design", "Construct a weighted donor counterfactual for an exposed unit or group.", ["dowhy_docs"]),
        ("heterogeneous_effects", "Heterogeneous treatment-effect estimation", "Estimate conditional or grouped causal effects without substituting prediction for identification.", ["grf_reference", "econml_docs"]),
        ("causal_sensitivity", "Causal sensitivity and refutation", "Quantify how causal conclusions change under unmeasured confounding or violated assumptions.", ["dowhy_docs", "doubleml_docs"]),
    ],
    "forecasting": [
        ("benchmark_forecast", "Forecast benchmarks", "Produce naive, seasonal-naive or drift baselines required to interpret skill.", ["forecasting_book"]),
        ("exponential_smoothing", "Exponential-smoothing forecasts", "Forecast level, trend and seasonality using recursively updated components.", ["forecasting_book", "statsmodels_tsa"]),
        ("arima", "ARIMA-family forecasting", "Model differenced serial dependence through autoregressive and moving-average structure.", ["forecasting_book", "statsmodels_tsa"]),
        ("state_space", "State-space forecasting", "Infer latent dynamic state and forecast observations through transition and observation equations.", ["statsmodels_tsa"]),
        ("multivariate_var", "Multivariate VAR/VECM forecasting", "Forecast jointly evolving series and optional long-run cointegration relations.", ["statsmodels_tsa"]),
        ("dynamic_regression", "Dynamic regression and exogenous forecasting", "Combine time-series errors with regressors whose future availability is governed.", ["forecasting_book", "statsmodels_tsa"]),
        ("intermittent_demand", "Intermittent-demand forecasting", "Forecast sparse demand occurrence and size without treating zeros as ordinary Gaussian noise.", ["forecasting_book", "sktime_forecasting"]),
        ("hierarchical_forecast", "Hierarchical and grouped forecast reconciliation", "Produce forecasts coherent across aggregation constraints.", ["forecasting_book"]),
        ("probabilistic_forecast", "Probabilistic forecasting", "Emit quantiles, intervals or full predictive distributions by horizon.", ["forecasting_book", "sktime_forecasting"]),
        ("forecast_combination", "Forecast combination", "Combine multiple forecast sources under an explicit weighting and evaluation rule.", ["forecasting_book"]),
        ("rolling_origin_evaluation", "Rolling-origin forecast evaluation", "Evaluate forecasts using only information available at each historical origin.", ["forecasting_book", "sktime_forecasting"]),
    ],
    "anomaly_change": [
        ("rule_threshold", "Rule and threshold anomaly detection", "Detect observations violating governed physical, business or statistical limits.", ["nist_handbook", "sodacl"]),
        ("robust_score", "Robust statistical anomaly scoring", "Score deviation using robust center, scale or tail models.", ["scipy_stats", "sklearn_outlier"]),
        ("isolation_forest", "Isolation-based anomaly detection", "Score anomalies by short random partition paths under a fitted reference sample.", ["sklearn_outlier"]),
        ("local_outlier_factor", "Local-density outlier detection", "Compare neighborhood density to identify local deviations.", ["sklearn_outlier"]),
        ("one_class_boundary", "One-class novelty detection", "Learn a support boundary from a reference regime and score later novelty.", ["sklearn_outlier"]),
        ("change_point", "Change-point detection", "Locate distribution or parameter regime changes in an ordered sequence.", ["river_drift", "scipy_stats"]),
        ("statistical_process_control", "Statistical process control", "Monitor process statistics against phase-I/phase-II control limits.", ["nist_handbook"]),
        ("stream_drift", "Streaming drift detection", "Detect changes online with explicit false-alarm, delay, reset and warm-up semantics.", ["river_drift"]),
    ],
    "process": [
        ("event_abstraction", "Event extraction and abstraction", "Construct canonical events/objects from source evidence with provenance and lifecycle semantics.", ["ocel20", "xes"]),
        ("case_discovery", "Case-centric process discovery", "Derive a process model from an event log under one explicit case notion.", ["process_manifesto", "prom"]),
        ("object_centric_discovery", "Object-centric process discovery", "Discover interacting object behavior without flattening to one case identifier.", ["ocel20", "pm4py"]),
        ("alignment_conformance", "Alignment-based conformance checking", "Find and cost model/log moves that reconcile observed traces with a reference model.", ["process_manifesto", "prom"]),
        ("token_replay", "Token-replay conformance checking", "Replay traces over token-based models and report missing/remaining/consumed/produced behavior.", ["pm4py", "prom"]),
        ("process_performance", "Process performance and bottleneck analysis", "Measure waiting, service, cycle, rework and congestion over process behavior.", ["process_manifesto", "pm4py"]),
        ("process_variant", "Process variant and deviation analysis", "Group and compare observed control-flow or object-centric behavioral variants.", ["pm4py"]),
        ("organizational_mining", "Organizational and handoff mining", "Analyze resource roles, collaboration, workload and handoff networks from events.", ["process_manifesto", "prom"]),
        ("predictive_monitoring", "Predictive process monitoring", "Estimate remaining time, next event or outcome for an in-flight case with prefix-safe evaluation.", ["process_manifesto", "pm4py"]),
    ],
    "data_quality": [
        ("profiling", "Data profiling", "Compute governed structural and statistical summaries for a dataset snapshot or stream.", ["deequ", "great_expectations"]),
        ("constraint_validation", "Data constraint validation", "Evaluate typed assertions against exact data scope and return pass/warn/fail/error evidence.", ["great_expectations", "deequ", "sodacl"]),
        ("schema_conformance", "Schema conformance analysis", "Detect absent, extra, reordered or incompatible fields against a versioned contract.", ["sodacl", "great_expectations"]),
        ("completeness", "Completeness and missingness analysis", "Measure presence under explicit null, sentinel and structural-absence semantics.", ["sodacl", "deequ"]),
        ("uniqueness", "Uniqueness and duplicate analysis", "Evaluate identity/key uniqueness at a declared grain.", ["sodacl", "deequ"]),
        ("referential_integrity", "Referential-integrity analysis", "Verify governed references against authoritative target keys and validity time.", ["sodacl"]),
        ("distribution_shift", "Distribution-shift quality analysis", "Compare current and reference distributions using typed distances or tests.", ["sodacl", "river_drift"]),
        ("reconciliation", "Cross-system data reconciliation", "Compare source/target records, aggregates and schemas with explicit tolerance and matching.", ["sodacl"]),
    ],
    "reliability": [
        ("kaplan_meier", "Nonparametric survival estimation", "Estimate a survival function from censored event times without a parametric lifetime family.", ["statsmodels_survival", "lifelines"]),
        ("proportional_hazards", "Proportional-hazards regression", "Relate covariates to hazard under a proportionality contract.", ["statsmodels_survival", "lifelines"]),
        ("parametric_lifetime", "Parametric lifetime modeling", "Fit a declared lifetime distribution and extrapolate within governed limits.", ["nist_handbook", "lifelines"]),
        ("competing_risks", "Competing-risks analysis", "Estimate cause-specific or cumulative-incidence quantities under mutually exclusive event causes.", ["lifelines"]),
        ("repairable_system", "Repairable-system analysis", "Model recurrent failures, repairs and exposure for a continuing asset/system.", ["nist_handbook"]),
        ("accelerated_life", "Accelerated-life testing", "Relate stressed-test lifetimes to use conditions through a declared acceleration model.", ["nist_handbook"]),
        ("degradation_model", "Degradation and remaining-life analysis", "Model observed degradation paths and threshold crossing under uncertainty.", ["nist_handbook"]),
    ],
    "queue_simulation": [
        ("queueing_analysis", "Analytical queueing models", "Estimate congestion and service performance under explicit arrival, service, discipline and network assumptions.", ["nist_handbook"]),
        ("monte_carlo", "Monte Carlo simulation", "Estimate a functional by reproducible random sampling with error analysis.", ["numpy_rng", "onemkl"]),
        ("discrete_event_simulation", "Discrete-event simulation", "Simulate timestamped state transitions of entities, resources and queues.", ["process_manifesto"]),
        ("system_dynamics", "System-dynamics simulation", "Simulate aggregate stocks, flows, delays and feedback equations.", ["nist_handbook"]),
        ("agent_based_simulation", "Agent-based simulation (non-LLM)", "Simulate explicitly programmed interacting entities; agent means modeled entity, not an LLM or agentic system.", ["nist_handbook"]),
        ("simulation_validation", "Simulation verification and validation", "Establish that implementation matches the model and assess fitness for the real-system use.", ["nist_handbook"]),
    ],
    "operations_research_bridge": [
        ("decision_problem_bridge", "Decision-problem bridge", "Resolve a DecisionProblemIR reference into the dedicated OR method and proof contracts.", ["nist_handbook"]),
        ("solver_result_bridge", "Solver-result bridge", "Preserve OR termination, feasibility, bound, incumbent and proof states in the common result algebra.", ["onemkl"]),
        ("heuristic_qualification_bridge", "Heuristic-qualification bridge", "Reference empirical OR heuristic qualification without implying a universal quality guarantee.", ["sklearn_evaluation"]),
    ],
    "graph": [
        ("traversal", "Graph traversal", "Visit reachable graph elements under declared directedness and visit-order semantics.", ["networkx_algorithms", "graphblas_c"]),
        ("shortest_path", "Shortest-path analysis", "Compute paths minimizing a compatible edge-weight algebra with negative-cycle handling.", ["networkx_algorithms", "graphblas_c"]),
        ("connectivity", "Connectivity and component analysis", "Identify connected, strongly connected, biconnected or cut structures.", ["networkx_algorithms"]),
        ("centrality", "Graph centrality analysis", "Compute declared degree, path, flow, spectral or random-walk importance scores.", ["networkx_algorithms", "igraph_manual"]),
        ("community", "Community and partition analysis", "Partition graph elements using an explicit objective, resolution and randomness policy.", ["networkx_algorithms", "igraph_manual"]),
        ("motif", "Motif and subgraph analysis", "Count or locate declared small subgraph patterns with exact or sampled guarantees.", ["networkx_algorithms"]),
        ("link_prediction", "Structural link prediction", "Score candidate links from graph structure under leakage-safe temporal evaluation.", ["networkx_algorithms"]),
        ("graph_similarity", "Graph similarity and isomorphism", "Compare graph structures or determine exact isomorphism under label semantics.", ["networkx_algorithms"]),
        ("temporal_graph", "Temporal graph analysis", "Analyze reachability, paths and structure with event/valid-time edge semantics.", ["igraph_manual", "graphblas_cpp"]),
    ],
    "spatial": [
        ("topology_predicates", "Spatial topology predicates", "Evaluate DE-9IM-like topological relations over valid geometries.", ["ogc_sfa", "geos"]),
        ("coordinate_transform", "Coordinate transformation", "Transform coordinates between declared reference systems with axis/datum evidence.", ["proj", "ogc_sfa"]),
        ("spatial_index_query", "Spatial indexing and query", "Prune and evaluate spatial candidates without changing exact predicate semantics.", ["postgis", "geos"]),
        ("spatial_autocorrelation", "Spatial autocorrelation analysis", "Measure global or local dependence under a declared spatial-weights graph.", ["pysal_esda"]),
        ("spatial_regression", "Spatial regression", "Estimate response relationships while representing spatial lag/error dependence.", ["pysal_spreg"]),
        ("spatial_interpolation", "Spatial interpolation and kriging", "Estimate a field at unobserved locations under a variogram/covariance model.", ["pysal_esda", "scipy_guide"]),
        ("point_pattern", "Point-pattern analysis", "Analyze intensity, interaction and clustering of spatial event locations.", ["pysal_esda"]),
        ("raster_zonal", "Raster and zonal analysis", "Aggregate or transform raster cells under geometry, resolution, nodata and resampling semantics.", ["gdal", "postgis"]),
        ("map_matching", "Map matching", "Infer network locations/paths corresponding to uncertain observed coordinates.", ["postgis", "networkx_algorithms"]),
    ],
    "text_search": [
        ("unicode_normalization", "Unicode normalization", "Map canonically or compatibly equivalent text to a declared Unicode normalization form.", ["unicode_uax15", "icu_collation"]),
        ("text_segmentation", "Text boundary segmentation", "Locate grapheme, word, sentence or line boundaries under Unicode and locale rules.", ["unicode_uax29", "icu_boundary"]),
        ("tokenization", "Search tokenization", "Convert text and field context into positioned tokens under a versioned analyzer.", ["lucene_core", "icu_boundary"]),
        ("stemming", "Stemming and lexical normalization", "Map inflected tokens to indexed forms under language-specific rules and known loss.", ["lucene_core"]),
        ("lexical_statistics", "Lexical and corpus statistics", "Compute term/document frequencies, co-occurrence and vocabulary summaries.", ["lucene_core"]),
        ("automata_matching", "Pattern, automaton and FST matching", "Compile and execute finite-state text/pattern operations.", ["lucene_core", "tantivy"]),
        ("inverted_index", "Inverted-index construction", "Build term-to-postings structures with positions, payloads and segment identity.", ["lucene_core", "tantivy"]),
        ("boolean_retrieval", "Boolean and filtered retrieval", "Evaluate logical, phrase, range and field constraints over an index.", ["lucene_core", "tantivy"]),
        ("bm25_ranking", "BM25 relevance ranking", "Rank matching documents using versioned BM25 corpus and field parameters.", ["lucene_similarity"]),
        ("faceting_grouping", "Faceting, grouping and top-k collection", "Aggregate and rank search results by governed fields and tie rules.", ["lucene_core", "tantivy"]),
        ("spell_suggest", "Spell correction and query suggestion", "Generate and rank lexical candidates under edit, frequency and language constraints.", ["lucene_core"]),
        ("classical_topic_model", "Classical probabilistic topic modeling", "Estimate document-topic and topic-term distributions without generative language-model semantics.", ["scipy_stats", "sklearn_evaluation"]),
    ],
    "signal": [
        ("sampling_resampling", "Signal sampling and resampling", "Change sample grids with explicit anti-alias, phase and reconstruction semantics.", ["scipy_signal"]),
        ("fir_filter", "Finite impulse-response filtering", "Apply a finite convolutional filter with declared coefficients and boundary policy.", ["scipy_signal"]),
        ("iir_filter", "Infinite impulse-response filtering", "Apply recursive filter state with stability, initialization and phase semantics.", ["scipy_signal"]),
        ("convolution", "Signal convolution", "Compute discrete convolution with direct/FFT/overlap strategy and exact output mode.", ["scipy_signal"]),
        ("correlation", "Signal cross-correlation", "Estimate lagged similarity with declared normalization and boundary conventions.", ["scipy_signal"]),
        ("spectral_estimation", "Fourier and spectral estimation", "Transform signals and estimate power/cross spectra under window and normalization rules.", ["scipy_fft", "fftw", "scipy_signal"]),
        ("time_frequency", "Short-time Fourier analysis", "Estimate local frequency content using a governed window, hop and invertibility contract.", ["scipy_signal", "scipy_fft"]),
        ("wavelet", "Wavelet analysis", "Decompose signals across time/space scales under a chosen wavelet and boundary mode.", ["pywavelets"]),
        ("peak_event", "Peak and signal-event detection", "Locate signal events by prominence, width, distance and threshold semantics.", ["scipy_signal"]),
    ],
    "image": [
        ("intensity_transform", "Image intensity and color transformation", "Transform calibrated intensities or color spaces with range and dtype semantics.", ["scikit_image", "opencv_imgproc"]),
        ("image_filtering", "Image filtering and restoration", "Smooth, sharpen, denoise or deconvolve images under a declared observation model.", ["scikit_image", "opencv_imgproc"]),
        ("mathematical_morphology", "Mathematical morphology", "Apply erosion, dilation, opening, closing and related lattice operations with a structuring element.", ["scikit_image", "opencv_imgproc"]),
        ("edge_contour", "Edge and contour extraction", "Detect and connect intensity boundaries into governed geometric evidence.", ["opencv_imgproc", "scikit_image"]),
        ("image_segmentation", "Classical image segmentation", "Partition pixels/voxels into meaningful regions using non-LLM classical methods.", ["scikit_image", "itk"]),
        ("connected_components", "Connected-component labeling", "Label components under exact neighborhood connectivity and background rules.", ["scikit_image", "opencv_imgproc"]),
        ("image_registration", "Image registration", "Estimate a spatial transform aligning moving and reference images under a similarity metric.", ["itk", "scikit_image"]),
        ("classical_features", "Classical image feature extraction", "Compute corners, blobs, texture, shape or local descriptors without learned generative models.", ["scikit_image", "opencv_imgproc"]),
        ("image_measurement", "Image region measurement", "Measure geometry, intensity and topology of labeled regions with coordinate units.", ["scikit_image", "itk"]),
    ],
    "semantic_metric": [
        ("base_measure", "Base semantic measure", "Bind a typed observation expression to an entity grain, unit and valid time.", ["apache_ossie", "dbt_semantic"]),
        ("distributive_aggregate", "Distributive aggregation", "Evaluate merge-preserving count, sum, minimum or maximum over a governed population.", ["dbt_metrics", "sdmx"]),
        ("algebraic_aggregate", "Algebraic aggregation", "Evaluate a fixed-size sufficient-state aggregate such as average from count and sum.", ["dbt_metrics", "openformula"]),
        ("holistic_aggregate", "Holistic aggregation", "Evaluate an aggregate such as exact median whose state is not fixed-size mergeable.", ["dbt_metrics", "openformula"]),
        ("ratio_metric", "Ratio metric", "Divide compatible numerator and denominator metrics under zero, unit and grain laws.", ["dbt_metrics", "openformula"]),
        ("derived_metric", "Derived metric formula", "Evaluate a typed formula over existing metrics while preserving dependency and error semantics.", ["dbt_metrics", "openformula"]),
        ("semiadditive_metric", "Semi-additive measure", "Aggregate across some dimensions but prohibit or specialize aggregation across others such as time.", ["apache_ossie", "dbt_semantic"]),
        ("cumulative_metric", "Cumulative and windowed metric", "Accumulate a measure over a defined time spine, window and reset policy.", ["dbt_metrics"]),
        ("conversion_metric", "Conversion and funnel metric", "Relate qualifying base and conversion events under entity, order, window and attribution rules.", ["dbt_metrics"]),
        ("cohort_retention", "Cohort and retention metric", "Measure later activity for entities assigned to cohorts by an exact entry event and calendar.", ["dbt_semantic", "dbt_metrics"]),
        ("unit_currency_conversion", "Unit and currency conversion", "Transform compatible quantities using versioned units, rates and validity times.", ["openformula", "sdmx"]),
        ("time_comparison", "Period and time-shift comparison", "Compare aligned metric observations across governed calendars, periods and revision states.", ["dbt_metrics", "sdmx"]),
    ],
}


RESULT_STATES = ["valid", "invalid_input", "assumptions_unmet", "unsupported", "not_converged", "numerically_suspect", "resource_exhausted", "cancelled", "inconclusive"]


def method_family(domain: str, spec: tuple) -> dict:
    slug, name, definition, evidence_slugs = spec
    base = DOMAIN_DEFAULTS[domain]
    or_refs = []
    if domain == "operations_research_bridge":
        or_refs = {
            "decision_problem_bridge": ["or.method.decision_framing"],
            "solver_result_bridge": ["or.method.solve_result_validation"],
            "heuristic_qualification_bridge": ["or.method.heuristic_empirical_qualification"],
        }.get(slug, [])
    elif domain == "queue_simulation" and slug in {"queueing_analysis", "discrete_event_simulation", "agent_based_simulation"}:
        or_refs = [f"or.method.{slug}"]
    return {
        "method_family_id": f"method_family.{domain}.{slug}",
        "edition": EDITION,
        "status": "sourced_candidate",
        "name": name,
        "domain_family": domain,
        "definition": definition,
        "owner_context_ref": base["owner"],
        "practice_refs": base["practice"],
        "study_design_contract": base["study"],
        "estimand_contract": base["estimand"] + [f"The distinct target of {name} must be resolved before provider binding."],
        "input_contracts": base["inputs"],
        "assumptions": base["assumptions"],
        "formula_model_contract": base["formula"],
        "estimator_contract": base["estimator"],
        "output_contracts": base["outputs"],
        "uncertainty_contract": base["uncertainty"],
        "evaluation_contract": base["evaluation"],
        "result_states": RESULT_STATES,
        "artifact_lifecycle": base["artifact"],
        "algorithm_requirements": base["algorithm"],
        "kernel_requirements": base["kernels"],
        "decision_refs": [f"decision.method_kernels.{decision}" for decision in base["decisions"]],
        "or_bridge_refs": or_refs,
        "evidence_refs": [f"source.method_kernel.{source}" for source in evidence_slugs],
        "llm_dependency": "none",
        "gaps": ["Theorem-level preconditions, provider conformance and two unrelated vertical bindings remain to be adjudicated for this candidate."],
    }


METHOD_FAMILIES = [
    method_family(domain, spec)
    for domain, specs in METHOD_SPECS.items()
    for spec in specs
]


def mf(domain: str, slug: str) -> str:
    return f"method_family.{domain}.{slug}"


IMPLEMENTATION_SPECS = [
    # Formulas: declarative meaning, not execution strategy.
    ("formula", "weighted_mean", "Weighted-mean formula", "Define sum(w*x)/sum(w) with exact zero-weight, unit, missingness and accumulation semantics.", [mf("descriptive", "grouped_summary"), mf("semantic_metric", "algebraic_aggregate")], ["weighted arithmetic mean"], ["nist_handbook", "openformula"], []),
    ("formula", "sample_variance", "Sample-variance formula", "Define centered second moment with a named denominator/degrees-of-freedom convention.", [mf("descriptive", "univariate_summary"), mf("inferential", "point_estimation")], ["sample variance"], ["nist_handbook", "scipy_stats"], []),
    ("formula", "rate_ratio", "Rate and ratio formula", "Define numerator, denominator, exposure, zero-domain, unit and compatibility laws.", [mf("semantic_metric", "ratio_metric")], ["ratio or exposure-normalized rate"], ["openformula", "dbt_metrics"], []),
    ("formula", "survival_hazard", "Survival and hazard formulas", "Relate survival, cumulative hazard and instantaneous hazard under declared continuous/discrete time.", [mf("reliability", "kaplan_meier"), mf("reliability", "proportional_hazards")], ["survival and hazard functionals"], ["statsmodels_survival", "lifelines"], []),
    ("formula", "log_likelihood", "Log-likelihood formula", "Evaluate a parameterized observation model with support, weighting and constant-term policy.", [mf("inferential", "point_estimation"), mf("forecasting", "arima")], ["log likelihood and score inputs"], ["statsmodels_guide", "stan_reference"], []),
    ("formula", "average_treatment_effect", "Average-treatment-effect estimand", "Define the target-population expectation of potential-outcome contrast with treatment versions and time.", [mf("causal", "graph_identification"), mf("causal", "doubly_robust")], ["ATE estimand"], ["dowhy_paper", "doubleml_docs"], []),
    ("formula", "bm25", "BM25 ranking formula", "Define document/query score from term frequency, document length and corpus statistics with fixed parameters.", [mf("text_search", "bm25_ranking")], ["BM25 relevance score"], ["lucene_similarity"], []),
    ("formula", "metric_expression", "Typed semantic-metric expression", "Represent formula AST, dependencies, units, grain, null/error and time semantics before SQL lowering.", [mf("semantic_metric", "derived_metric"), mf("semantic_metric", "ratio_metric")], ["semantic metric observation"], ["openformula", "apache_ossie", "dbt_metrics"], []),

    # Models: representations, not universal truths.
    ("model", "linear", "Linear statistical model", "Represent response as a linear predictor plus declared error structure.", [mf("inferential", "linear_regression")], ["conditional mean and covariance model"], ["statsmodels_guide", "r_stats"], []),
    ("model", "glm", "Generalized linear model", "Represent exponential-family response, linear predictor and link function.", [mf("inferential", "generalized_linear_model")], ["conditional response distribution"], ["statsmodels_guide"], []),
    ("model", "state_space", "State-space model", "Represent latent-state transition and observation equations with initialization and noise.", [mf("forecasting", "state_space")], ["latent dynamic state and observation distribution"], ["statsmodels_tsa"], []),
    ("model", "arima", "ARIMA model", "Represent differenced serial dependence through AR and MA lag polynomials.", [mf("forecasting", "arima")], ["serial process and forecast distribution"], ["forecasting_book", "statsmodels_tsa"], []),
    ("model", "causal_graph", "Causal graph and structural assumptions", "Represent causal variables, directed relations and identification assumptions independently from estimation.", [mf("causal", "graph_identification")], ["causal identification argument"], ["dowhy_paper", "dowhy_docs"], []),
    ("model", "cox_ph", "Cox proportional-hazards model", "Represent multiplicative covariate effects on an unspecified baseline hazard.", [mf("reliability", "proportional_hazards")], ["relative hazard and survival quantities"], ["statsmodels_survival", "lifelines"], []),
    ("model", "queueing", "Queueing network model", "Represent arrivals, service, routing, capacity, discipline and performance regime.", [mf("queue_simulation", "queueing_analysis")], ["queue length, waiting and utilization functionals"], ["nist_handbook"], []),
    ("model", "petri_process", "Petri-net/process-tree model", "Represent process control-flow behavior, concurrency and replay semantics.", [mf("process", "case_discovery"), mf("process", "alignment_conformance")], ["allowed process behavior"], ["process_manifesto", "prom"], []),
    ("model", "property_graph", "Typed graph model", "Represent vertices, edges, direction, multiplicity, weights, properties and time.", [mf("graph", "traversal"), mf("graph", "centrality")], ["graph topology and attributes"], ["graphblas_cpp", "networkx_algorithms"], []),
    ("model", "spatial_covariance", "Spatial covariance/variogram model", "Represent distance/direction-dependent covariance for interpolation and spatial inference.", [mf("spatial", "spatial_interpolation")], ["spatial dependence and prediction covariance"], ["pysal_esda", "pysal_spreg"], []),
    ("model", "lti_system", "Linear time-invariant signal model", "Represent convolutional input-output behavior and frequency response.", [mf("signal", "fir_filter"), mf("signal", "iir_filter")], ["signal system response"], ["scipy_signal"], []),
    ("model", "image_transform", "Parameterized image registration transform", "Represent rigid, affine or deformable coordinate mapping with interpolation semantics.", [mf("image", "image_registration")], ["moving-to-reference coordinate map"], ["itk", "scikit_image"], []),
    ("model", "semantic_graph", "Semantic entity-metric graph", "Represent entities, dimensions, measures, join relations, time and formula dependencies.", [mf("semantic_metric", "base_measure"), mf("semantic_metric", "derived_metric")], ["valid metric-query space"], ["apache_ossie", "dbt_semantic"], []),

    # Estimators: observations to estimates.
    ("estimator", "ols", "Ordinary least-squares estimator", "Estimate linear coefficients by minimizing squared residuals with covariance diagnostics.", [mf("inferential", "linear_regression")], ["linear coefficients and covariance"], ["statsmodels_guide", "lapack"], ["kernel.linalg.qr"]),
    ("estimator", "glm_mle", "GLM maximum-likelihood estimator", "Estimate GLM parameters under the declared family/link and convergence policy.", [mf("inferential", "generalized_linear_model")], ["GLM coefficients, covariance and diagnostics"], ["statsmodels_guide"], ["kernel.linalg.qr", "kernel.vector.elementwise"]),
    ("estimator", "m_estimator", "Robust M-estimator", "Estimate regression parameters by iteratively reweighted loss under a declared influence function.", [mf("inferential", "robust_regression")], ["robust coefficients and scale"], ["statsmodels_guide"], ["kernel.linalg.qr"]),
    ("estimator", "posterior", "Posterior inference estimator", "Approximate posterior expectations/quantiles from a declared probabilistic model and sampler.", [mf("inferential", "bayesian_inference")], ["posterior draws and summaries"], ["stan_reference", "pymc_api"], ["kernel.rng.counter_based"]),
    ("estimator", "bootstrap", "Bootstrap estimator", "Estimate a sampling distribution by a design-compatible resampling procedure.", [mf("inferential", "resampling_inference")], ["bootstrap distribution, bias and interval"], ["scipy_stats", "r_stats"], ["kernel.rng.counter_based", "kernel.aggregate.reduce"]),
    ("estimator", "kaplan_meier", "Kaplan-Meier estimator", "Estimate survival from ordered failures and risk sets under right censoring.", [mf("reliability", "kaplan_meier")], ["survival step function and confidence bands"], ["statsmodels_survival", "lifelines"], ["kernel.sort.stable", "kernel.aggregate.reduce"]),
    ("estimator", "cox_partial_likelihood", "Cox partial-likelihood estimator", "Estimate proportional-hazards coefficients from risk sets and tied-event policy.", [mf("reliability", "proportional_hazards")], ["hazard ratios and covariance"], ["statsmodels_survival", "lifelines"], ["kernel.sort.stable", "kernel.linalg.qr"]),
    ("estimator", "ipw", "Inverse-probability weighted estimator", "Estimate an intervention contrast by governed propensity-derived weights.", [mf("causal", "inverse_probability_weighting")], ["weighted causal effect and diagnostics"], ["dowhy_docs", "doubleml_docs"], ["kernel.aggregate.reduce"]),
    ("estimator", "aipw", "Augmented inverse-probability weighted estimator", "Combine outcome regression and treatment weighting under a doubly robust contract.", [mf("causal", "doubly_robust")], ["causal effect, influence values and uncertainty"], ["doubleml_docs", "econml_docs"], ["kernel.aggregate.reduce", "kernel.linalg.qr"]),
    ("estimator", "doubleml", "Cross-fitted orthogonal-score estimator", "Estimate a causal parameter using orthogonal scores and leakage-safe cross-fitting.", [mf("causal", "doubly_robust"), mf("causal", "heterogeneous_effects")], ["causal parameter and valid inference"], ["doubleml_docs"], ["kernel.aggregate.reduce"]),
    ("estimator", "did", "Difference-in-differences estimator", "Estimate treated-versus-control change with panel/repeated-cross-section and pre-trend contracts.", [mf("causal", "difference_in_differences")], ["ATT/ATE-like contrast and event-study diagnostics"], ["doubleml_docs"], ["kernel.linalg.qr"]),
    ("estimator", "rdd_local_polynomial", "Local-polynomial RDD estimator", "Estimate a discontinuity at a cutoff with governed bandwidth and running-variable diagnostics.", [mf("causal", "regression_discontinuity")], ["local treatment effect and uncertainty"], ["doubleml_docs"], ["kernel.linalg.qr"]),
    ("estimator", "synthetic_control", "Synthetic-control estimator", "Estimate a counterfactual trajectory from constrained donor weights.", [mf("causal", "synthetic_control")], ["counterfactual path, gap and placebo evidence"], ["dowhy_docs"], ["kernel.linalg.qr"]),
    ("estimator", "ets", "Exponential-smoothing state estimator", "Estimate recursively updated level/trend/seasonal state and forecast distribution.", [mf("forecasting", "exponential_smoothing")], ["fitted state and forecasts"], ["forecasting_book", "statsmodels_tsa"], ["kernel.vector.elementwise"]),
    ("estimator", "arima_mle", "ARIMA likelihood estimator", "Estimate ARIMA parameters with stationarity/invertibility and initialization policy.", [mf("forecasting", "arima")], ["ARIMA parameters, state and forecasts"], ["statsmodels_tsa"], ["kernel.linalg.cholesky"]),
    ("estimator", "kalman", "Kalman filter/smoother", "Estimate latent Gaussian linear state by recursive predict-update and optional smoothing.", [mf("forecasting", "state_space")], ["filtered/smoothed state and covariance"], ["statsmodels_tsa"], ["kernel.linalg.gemm", "kernel.linalg.cholesky"]),
    ("estimator", "isolation_forest", "Isolation-forest anomaly estimator", "Fit randomized partition trees and derive path-length anomaly scores.", [mf("anomaly_change", "isolation_forest")], ["fitted forest and anomaly scores"], ["sklearn_outlier"], ["kernel.rng.counter_based", "kernel.topk.select"]),
    ("estimator", "local_outlier_factor", "Local-outlier-factor estimator", "Estimate local reachability density and relative neighborhood anomaly score.", [mf("anomaly_change", "local_outlier_factor")], ["local outlier scores"], ["sklearn_outlier"], ["kernel.distance.pairwise", "kernel.topk.select"]),
    ("estimator", "spatial_lag", "Spatial-lag regression estimator", "Estimate response dependence through a declared spatial-weights operator.", [mf("spatial", "spatial_regression")], ["spatial coefficients and diagnostics"], ["pysal_spreg"], ["kernel.sparse.spmv", "kernel.linalg.qr"]),
    ("estimator", "kriging", "Kriging estimator", "Estimate an unobserved spatial field from covariance-weighted observations.", [mf("spatial", "spatial_interpolation")], ["spatial predictions and kriging variance"], ["pysal_esda", "scipy_guide"], ["kernel.linalg.cholesky"]),
    ("estimator", "welch_psd", "Welch power-spectral-density estimator", "Average windowed periodograms with declared overlap, detrending and scaling.", [mf("signal", "spectral_estimation")], ["frequency-indexed PSD estimate"], ["scipy_signal"], ["kernel.fft.dft", "kernel.aggregate.reduce"]),
    ("estimator", "probabilistic_topic", "Classical probabilistic topic estimator", "Fit document-topic and topic-term distributions under a declared finite latent-topic model.", [mf("text_search", "classical_topic_model")], ["topic distributions and diagnostics"], ["scipy_stats", "sklearn_evaluation"], ["kernel.rng.counter_based", "kernel.linalg.gemm"]),

    # Algorithms: finite procedures.
    ("algorithm", "welford", "Welford online moments", "Update count, mean and second central moment stably in one pass with a merge law.", [mf("descriptive", "univariate_summary"), mf("descriptive", "mergeable_sketch")], ["mean and variance sufficient state"], ["nist_handbook"], ["kernel.aggregate.reduce"]),
    ("algorithm", "quickselect", "Selection-based exact quantile", "Select order statistics without fully sorting while preserving the chosen quantile convention.", [mf("descriptive", "quantile_estimation")], ["exact sample quantile ingredients"], ["numpy_ufunc"], ["kernel.topk.select"]),
    ("algorithm", "qr_least_squares", "QR least-squares algorithm", "Solve least squares through orthogonal-triangular factorization with rank diagnostics.", [mf("inferential", "linear_regression")], ["least-squares solution and residuals"], ["lapack"], ["kernel.linalg.qr"]),
    ("algorithm", "irls", "Iteratively reweighted least squares", "Fit GLM or robust regression by repeated weighted least-squares updates.", [mf("inferential", "generalized_linear_model"), mf("inferential", "robust_regression")], ["coefficient iterate and convergence diagnostics"], ["statsmodels_guide"], ["kernel.linalg.qr"]),
    ("algorithm", "lbfgs", "Limited-memory quasi-Newton optimization", "Minimize a smooth objective from gradients with finite memory and line-search termination.", [mf("inferential", "point_estimation")], ["parameter optimum candidate and termination"], ["scipy_guide"], ["kernel.vector.elementwise", "kernel.linalg.dot"]),
    ("algorithm", "nuts_hmc", "NUTS/Hamiltonian Monte Carlo", "Generate posterior draws using Hamiltonian dynamics and adaptive trajectory length.", [mf("inferential", "bayesian_inference")], ["posterior draw stream and sampler diagnostics"], ["stan_reference", "pymc_api"], ["kernel.rng.counter_based", "kernel.vector.elementwise"]),
    ("algorithm", "bootstrap_resample", "Bootstrap resampling algorithm", "Generate resamples consistent with i.i.d., cluster, block or stratified design.", [mf("inferential", "resampling_inference")], ["replicate estimates"], ["scipy_stats"], ["kernel.rng.counter_based"]),
    ("algorithm", "cross_fitting", "Cross-fitting algorithm", "Partition observations, fit nuisance functions out-of-fold and combine orthogonal scores.", [mf("causal", "doubly_robust")], ["out-of-fold nuisance predictions and causal score"], ["doubleml_docs"], ["kernel.aggregate.reduce"]),
    ("algorithm", "rolling_origin", "Rolling-origin evaluation algorithm", "Generate chronological train/evaluate origins with horizon and revision safety.", [mf("forecasting", "rolling_origin_evaluation")], ["forecast-score tensor by origin and horizon"], ["forecasting_book", "sktime_forecasting"], ["kernel.sort.stable"]),
    ("algorithm", "mint_reconciliation", "Minimum-trace forecast reconciliation", "Project base forecasts into a coherent hierarchy using an estimated error covariance.", [mf("forecasting", "hierarchical_forecast")], ["coherent forecasts"], ["forecasting_book"], ["kernel.linalg.qr"]),
    ("algorithm", "cusum_change", "CUSUM change detector", "Accumulate directional evidence and signal/reset under a governed threshold.", [mf("anomaly_change", "change_point"), mf("anomaly_change", "statistical_process_control")], ["change statistic and alarm time"], ["nist_handbook"], ["kernel.vector.elementwise"]),
    ("algorithm", "inductive_miner", "Inductive process discovery", "Recursively derive a block-structured process model from event-log cuts and noise policy.", [mf("process", "case_discovery")], ["process tree/Petri net"], ["pm4py", "prom"], ["kernel.graph.traversal"]),
    ("algorithm", "alignment_astar", "A* process alignment", "Search synchronous/log/model moves for a least-cost trace-model alignment.", [mf("process", "alignment_conformance")], ["alignment and deviation cost"], ["prom", "pm4py"], ["kernel.topk.select", "kernel.graph.traversal"]),
    ("algorithm", "token_replay", "Token replay algorithm", "Replay events over a Petri net and account for missing, consumed, produced and remaining tokens.", [mf("process", "token_replay")], ["replay conformance state"], ["pm4py", "prom"], ["kernel.graph.traversal"]),
    ("algorithm", "constraint_scan", "Data constraint scan", "Evaluate a rule suite over exact or declared sampled scope and emit failing evidence.", [mf("data_quality", "constraint_validation")], ["measurements and assertion results"], ["great_expectations", "sodacl", "deequ"], ["kernel.aggregate.reduce", "kernel.join.hash"]),
    ("algorithm", "hash_reconciliation", "Partitioned hash reconciliation", "Match source/target records by governed identity and compare typed field/aggregate values.", [mf("data_quality", "reconciliation")], ["matched, missing and differing records"], ["sodacl"], ["kernel.join.hash", "kernel.aggregate.hash"]),
    ("algorithm", "bfs", "Breadth-first graph traversal", "Visit unweighted graph layers from a source under exact directedness and tie-order policy.", [mf("graph", "traversal")], ["reachability and hop distance"], ["networkx_algorithms", "graphblas_c"], ["kernel.graph.semiring_mxv"]),
    ("algorithm", "dijkstra", "Dijkstra shortest path", "Compute nonnegative-weight shortest paths with a priority queue and predecessor policy.", [mf("graph", "shortest_path")], ["distances and paths"], ["networkx_algorithms"], ["kernel.topk.select"]),
    ("algorithm", "pagerank", "PageRank power iteration", "Estimate stationary random-walk centrality under damping, dangling and convergence rules.", [mf("graph", "centrality")], ["node centrality vector"], ["networkx_algorithms", "graphblas_c"], ["kernel.graph.semiring_mxv"]),
    ("algorithm", "community_modularity", "Modularity community optimization", "Search a graph partition under a declared modularity objective, resolution and seed.", [mf("graph", "community")], ["partition and quality score"], ["igraph_manual", "networkx_algorithms"], ["kernel.graph.traversal", "kernel.rng.counter_based"]),
    ("algorithm", "rtree_query", "R-tree candidate filtering", "Use bounding boxes to prune spatial candidates before exact predicate evaluation.", [mf("spatial", "spatial_index_query")], ["candidate geometry pairs"], ["postgis", "geos"], ["kernel.geometry.predicate"]),
    ("algorithm", "proj_pipeline", "Coordinate-operation pipeline", "Select and execute a versioned CRS transformation with axis, grid and error policy.", [mf("spatial", "coordinate_transform")], ["transformed coordinates and operation receipt"], ["proj", "ogc_sfa"], ["kernel.spatial.transform"]),
    ("algorithm", "unicode_normalize", "Unicode normalization algorithm", "Apply the selected canonical/compatibility decomposition and composition form.", [mf("text_search", "unicode_normalization")], ["normalized Unicode string"], ["unicode_uax15", "icu_collation"], ["kernel.text.normalize"]),
    ("algorithm", "break_iterator", "Unicode boundary iteration", "Locate grapheme/word/sentence boundaries with Unicode and locale dictionary rules.", [mf("text_search", "text_segmentation")], ["boundary offsets and rule status"], ["unicode_uax29", "icu_boundary"], ["kernel.text.segmentation"]),
    ("algorithm", "inverted_index_build", "Segmented inverted-index construction", "Analyze fields, build postings/positions and commit immutable index segments.", [mf("text_search", "inverted_index")], ["versioned searchable index"], ["lucene_core", "tantivy"], ["kernel.search.postings", "kernel.data.dictionary_encode", "kernel.compression.zstd"]),
    ("algorithm", "bm25_topk", "BM25 top-k retrieval", "Score matching postings and maintain deterministic top-k results.", [mf("text_search", "bm25_ranking")], ["ranked documents and score explanations"], ["lucene_similarity", "tantivy"], ["kernel.search.postings", "kernel.topk.select"]),
    ("algorithm", "cooley_tukey", "Cooley-Tukey FFT", "Factor a DFT into smaller transforms with declared normalization, layout and planning.", [mf("signal", "spectral_estimation")], ["discrete Fourier transform"], ["fftw", "scipy_fft"], ["kernel.fft.dft"]),
    ("algorithm", "polyphase_resample", "Polyphase resampling", "Filter and rationally change sample rate while controlling aliasing and phase.", [mf("signal", "sampling_resampling")], ["resampled signal"], ["scipy_signal"], ["kernel.signal.convolution"]),
    ("algorithm", "canny_edge", "Canny edge detector", "Smooth, differentiate, suppress and hysteresis-threshold image edges.", [mf("image", "edge_contour")], ["edge mask"], ["opencv_imgproc", "scikit_image"], ["kernel.signal.convolution", "kernel.image.morphology"]),
    ("algorithm", "watershed", "Watershed segmentation", "Flood a marker/elevation representation into labeled catchment regions.", [mf("image", "image_segmentation")], ["label image"], ["scikit_image", "opencv_imgproc"], ["kernel.image.connected_components", "kernel.topk.select"]),
    ("algorithm", "phase_correlation", "Phase-correlation registration", "Estimate translation from normalized cross-power spectrum with subpixel refinement.", [mf("image", "image_registration")], ["image shift and registration quality"], ["scikit_image"], ["kernel.fft.dft", "kernel.signal.convolution"]),
    ("algorithm", "metric_lowering", "Grain-safe metric lowering", "Resolve semantic graph paths and lower a typed metric AST to a provider query without changing grain.", [mf("semantic_metric", "derived_metric"), mf("semantic_metric", "ratio_metric")], ["logical metric query plan"], ["apache_ossie", "dbt_semantic", "dbt_metrics"], ["kernel.join.hash", "kernel.aggregate.hash"]),

    # Kernels: executable primitives, including physical encoding/compression boundaries.
    ("numerical_kernel", "vector.elementwise", "Typed elementwise vector kernel", "Apply a scalar function over arrays under broadcast, cast, null/NaN and aliasing rules.", [], ["elementwise array operation"], ["numpy_ufunc", "array_api", "arrow_compute"], []),
    ("numerical_kernel", "aggregate.reduce", "Typed reduction kernel", "Reduce an array under identity, associativity/order, null/NaN and accumulation rules.", [], ["sum, count, min, max or custom reduction"], ["numpy_ufunc", "arrow_compute"], []),
    ("numerical_kernel", "aggregate.hash", "Hash aggregation kernel", "Partition typed keys and maintain aggregate states with deterministic merge/finalize semantics.", [], ["grouped aggregate state"], ["arrow_compute", "arrow_acero"], []),
    ("numerical_kernel", "topk.select", "Selection and top-k kernel", "Select order statistics or ranked candidates under stable tie and NaN rules.", [], ["selected values/indices"], ["numpy_ufunc", "lucene_core"], []),
    ("numerical_kernel", "sort.stable", "Stable typed sort kernel", "Sort values/records under total/partial ordering, locale and null placement policy.", [], ["permutation or sorted values"], ["numpy_ufunc", "arrow_compute"], []),
    ("numerical_kernel", "histogram", "Histogram and bin-count kernel", "Assign observations to governed bin edges and reduce counts/weights.", [], ["bin counts and edges"], ["scipy_stats", "numpy_ufunc"], []),
    ("numerical_kernel", "rng.counter_based", "Splittable random-stream kernel", "Generate reproducible pseudorandom bits/variates under algorithm, seed, stream and distribution policy.", [], ["random bit or variate stream"], ["numpy_rng", "onemkl"], []),
    ("numerical_kernel", "linalg.dot", "Vector dot-product kernel", "Compute a typed dot product with accumulation-precision and conjugation semantics.", [], ["scalar inner product"], ["blas", "onemkl"], []),
    ("numerical_kernel", "linalg.gemm", "Dense matrix multiplication kernel", "Compute typed matrix multiplication with layout, transpose, precision and accumulation rules.", [], ["dense matrix product"], ["blas", "onemkl", "faer"], []),
    ("numerical_kernel", "linalg.qr", "QR factorization kernel", "Factor a matrix with pivoting/rank/tolerance and overwrite semantics.", [], ["Q/R factors and rank information"], ["lapack", "faer"], []),
    ("numerical_kernel", "linalg.cholesky", "Cholesky factorization kernel", "Factor a positive-definite matrix with triangle, symmetry and failure semantics.", [], ["triangular factor"], ["lapack", "faer"], []),
    ("numerical_kernel", "linalg.svd", "Singular-value decomposition kernel", "Factor a matrix under full/thin/vector options and non-convergence semantics.", [], ["singular values and optional vectors"], ["lapack", "numpy_ufunc"], []),
    ("numerical_kernel", "sparse.spmv", "Sparse matrix-vector kernel", "Multiply a typed sparse matrix and vector under format, index and duplicate-entry rules.", [], ["dense or sparse output vector"], ["onemkl", "graphblas_c"], []),
    ("data_kernel", "graph.traversal", "Graph frontier-expansion kernel", "Expand and filter one graph frontier under explicit adjacency layout, direction, mask, duplicate and ordering rules; it does not choose a traversal or optimization policy.", [], ["next frontier and visited-state delta"], ["graphblas_c", "graphblas_cpp"], []),
    ("numerical_kernel", "graph.semiring_mxv", "Semiring sparse matrix-vector kernel", "Evaluate generalized sparse matrix-vector multiplication under an explicit semiring and mask.", [], ["graph frontier or algebraic vector"], ["graphblas_c", "graphblas_cpp"], []),
    ("numerical_kernel", "graph.semiring_mxm", "Semiring sparse matrix-matrix kernel", "Evaluate generalized sparse matrix multiplication under semiring, mask and sparsity rules.", [], ["sparse algebraic matrix"], ["graphblas_c", "suitesparse_graphblas"], []),
    ("numerical_kernel", "distance.pairwise", "Pairwise distance kernel", "Compute distances/similarities under metric, missingness, dtype and memory-block policy.", [], ["distance matrix or neighbor candidates"], ["scipy_guide", "sklearn_evaluation"], []),
    ("numerical_kernel", "fft.dft", "Discrete Fourier transform kernel", "Compute DFT/DCT/DST under direction, normalization, shape, strides, precision and plan semantics.", [], ["frequency-domain array"], ["fftw", "scipy_fft", "onemkl"], []),
    ("numerical_kernel", "signal.convolution", "Convolution/correlation kernel", "Compute direct, FFT or overlap convolution under mode, padding and precision semantics.", [], ["convolved/correlated signal or image"], ["scipy_signal"], []),
    ("numerical_kernel", "image.morphology", "Image morphology kernel", "Apply lattice neighborhood operations under connectivity, structuring element and border rules.", [], ["transformed image/mask"], ["scikit_image", "opencv_imgproc"], []),
    ("numerical_kernel", "image.connected_components", "Connected-component kernel", "Label image/graph components under exact connectivity and label-order policy.", [], ["component labels and count"], ["scikit_image", "opencv_imgproc"], []),
    ("data_kernel", "join.hash", "Typed hash-join kernel", "Match equality keys under cardinality, null, collation, memory and spill semantics.", [], ["joined record batches"], ["arrow_acero", "arrow_compute"], []),
    ("data_kernel", "text.normalize", "Unicode normalization kernel", "Normalize Unicode to a named version/form without inventing locale semantics.", [], ["normalized text"], ["unicode_uax15", "icu_collation"], []),
    ("data_kernel", "text.segmentation", "Unicode segmentation kernel", "Emit text boundaries under Unicode version, boundary kind, locale and dictionary rules.", [], ["boundary offsets"], ["unicode_uax29", "icu_boundary"], []),
    ("data_kernel", "search.postings", "Postings intersection and scoring kernel", "Traverse compressed postings/positions and expose matching statistics for query scoring.", [], ["matching document streams and scores"], ["lucene_core", "tantivy"], []),
    ("data_kernel", "text.fst", "Finite-state text kernel", "Compile/evaluate automata or transducers under Unicode/code-unit and determinization budgets.", [], ["matches or transformed symbols"], ["lucene_core", "tantivy"], []),
    ("data_kernel", "document.container_parse", "Bounded document-container parse kernel", "Parse one exact document/container profile into bounded parts and relationships under encryption, recursion and expansion limits.", [], ["typed package parts, relationships and parse receipt"], ["tika", "pdfbox", "ecma376"], []),
    ("data_kernel", "document.positioned_text", "Positioned-text extraction kernel", "Extract glyph/text spans with source encoding, Unicode mapping, page coordinate transforms and loss warnings.", [], ["positioned glyph and text-span stream"], ["pdf20", "pdfbox", "alto"], []),
    ("data_kernel", "document.layout_group", "Document layout-grouping kernel", "Group positioned content into lines, blocks and regions under explicit geometric and reading-order policies.", [], ["layout regions and ordering evidence"], ["hocr", "alto", "pdfbox"], []),
    ("data_kernel", "document.ocr_runtime", "OCR runtime kernel", "Execute one qualified OCR engine/profile over a bounded page image and emit positioned text, confidence and runtime evidence.", [], ["positioned OCR elements and receipt"], ["tesseract", "hocr", "alto"], []),
    ("data_kernel", "document.table_structure", "Document table-structure kernel", "Detect a table region and emit a row/column/spanning-cell graph without inventing business meaning.", [], ["table structure and cell geometry"], ["pubtables1m", "alto"], []),
    ("data_kernel", "document.form_tree", "Document form-tree kernel", "Traverse native document form fields/widgets and emit names, values, appearances, coordinates and unsupported-form warnings.", [], ["typed form tree and field occurrences"], ["pdf20", "pdfbox", "html_standard"], []),
    ("data_kernel", "document.classification_runtime", "Document classification runtime kernel", "Execute one qualified classifier over a typed document view and emit label scores, alternatives, abstention and runtime evidence.", [], ["typed classification result and receipt"], ["spacy_pipeline", "opennlp_manual"], []),
    ("data_kernel", "document.information_extraction_runtime", "Document information-extraction runtime kernel", "Execute one qualified schema-bound span/field/relation extractor and preserve source evidence, alternatives and abstention.", [], ["typed extraction result and receipt"], ["spacy_pipeline", "opennlp_manual", "hocr"], []),
    ("numerical_kernel", "geometry.predicate", "Robust geometry predicate kernel", "Evaluate topological predicates with validity, dimensionality and robustness semantics.", [], ["boolean/spatial relation"], ["ogc_sfa", "geos"], []),
    ("numerical_kernel", "spatial.transform", "Coordinate transformation kernel", "Transform coordinate tuples using a resolved CRS operation and error/accuracy receipt.", [], ["transformed coordinates"], ["proj", "ogc_sfa"], []),
    ("numerical_kernel", "spatial.interpolation", "Spatial interpolation kernel", "Evaluate weighted field interpolation under neighborhood and covariance parameters.", [], ["predicted field values"], ["pysal_esda", "scipy_guide"], []),
    ("data_kernel", "arrow.compute_dispatch", "Arrow compute-kernel dispatch", "Dispatch a logical function to a kernel by exact input signature and shape.", [], ["Arrow scalar/array/batch output"], ["arrow_compute", "arrow_columnar"], []),
    ("data_kernel", "data.dictionary_encode", "Dictionary-encoding kernel", "Map values to a dictionary and typed indices with fallback and ordering semantics.", [], ["dictionary plus index stream"], ["parquet_encoding", "arrow_columnar"], []),
    ("data_kernel", "data.rle_bitpack", "RLE/bit-pack encoding kernel", "Encode repeated or bounded-width integers under the Parquet hybrid grammar.", [], ["encoded byte stream"], ["parquet_encoding"], []),
    ("data_kernel", "data.delta_encode", "Delta and byte-stream-split encoding kernels", "Encode typed values using declared delta, prefix or byte-stream layout before compression.", [], ["encoded page values"], ["parquet_encoding"], []),
    ("data_kernel", "compression.zstd", "Zstandard codec kernel", "Compress/decompress framed bytes with level, dictionary, checksum, streaming and memory limits.", [], ["compressed or decompressed byte stream"], ["zstd", "parquet_compression"], []),
    ("data_kernel", "compression.snappy", "Snappy codec kernel", "Compress/decompress Snappy blocks/frames with size, checksum and corruption handling.", [], ["compressed or decompressed byte stream"], ["snappy_format", "parquet_compression"], []),
]


def implementation_record(spec: tuple) -> dict:
    kind, slug, name, definition, family_refs, computes, evidence_slugs, kernel_refs = spec
    prefix = "kernel" if kind in {"numerical_kernel", "data_kernel"} else kind
    if kind == "formula":
        state = ["immutable expression and semantic edition", "no fitted or hidden runtime state"]
        randomness = ["none"]
        numeric = ["totality, units, missingness and error propagation are explicit"]
        termination = ["finite expression evaluation or typed undefined/error result"]
        resource = ["expression DAG size and evaluation work are finite or rejected"]
    elif kind == "model":
        state = ["declared model structure is immutable", "fitted parameters, if any, are a separate artifact"]
        randomness = ["model stochasticity is distinct from implementation RNG"]
        numeric = ["parameter domains, support and conditioning are explicit"]
        termination = ["model construction validates or refuses; fitting uses a separate estimator"]
        resource = ["model size and state dimensions are declared"]
    elif kind == "estimator":
        state = ["fitted artifact records data, method, code, configuration and provider digests"]
        randomness = ["all random streams and sample partitions are explicit and replay-scoped"]
        numeric = ["convergence, covariance, residual and tolerance evidence are retained"]
        termination = ["valid convergence, not converged, cancelled and numerical failure are distinct"]
        resource = ["finite observations, iterations, memory, threads/devices and wall-time budgets"]
    elif kind == "algorithm":
        state = ["workspace and reusable plans are explicit; no ambient mutable state"]
        randomness = ["none unless a governed RNG/seed/stream is passed explicitly"]
        numeric = ["precision, ordering, tolerance and approximation semantics survive lowering"]
        termination = ["finite bound or explicit cancellation/iteration/work stopping contract"]
        resource = ["time/work, memory, concurrency and device use are budgeted"]
    else:
        state = ["kernel plan/workspace/stream state is explicit and versioned when reusable"]
        randomness = ["none unless RNG is the declared operation"]
        numeric = ["dtype, precision, overflow, NaN/null, rounding and error behavior are declared"]
        termination = ["returns typed success, unsupported, invalid, resource, cancellation or provider failure"]
        resource = ["shape-dependent work, memory, scratch, threads/devices and output bounds are declared"]
    return {
        "record_id": f"{prefix}.{slug}",
        "record_kind": kind,
        "edition": EDITION,
        "status": "sourced_candidate",
        "name": name,
        "definition": definition,
        "method_family_refs": family_refs,
        "computes": computes,
        "typed_inputs": ["exact typed input contract resolved from the referenced method or operation"],
        "typed_outputs": ["exact typed output contract plus execution receipt"],
        "preconditions": ["all semantic, shape, study and numeric preconditions are checked or refused"],
        "semantics": [definition, "Provider-specific names do not change this record's meaning."],
        "state_contract": state,
        "randomness_contract": randomness,
        "numeric_contract": numeric,
        "termination_contract": termination,
        "resource_contract": resource,
        "failure_states": ["invalid_input", "unsupported", "not_converged_or_incomplete", "numerical_failure", "resource_exhausted", "cancelled", "provider_failure"],
        "decision_refs": ["decision.method_kernels.precision", "decision.method_kernels.determinism", "decision.method_kernels.resource_budget", "decision.method_kernels.kernel_backend"],
        "kernel_refs": kernel_refs,
        "evidence_refs": [f"source.method_kernel.{source}" for source in evidence_slugs],
        "llm_dependency": "none",
        "gaps": ["Executable conformance fixtures, target qualification and unrelated-vertical validation remain open unless covered by a separate receipt."],
    }


IMPLEMENTATION_RECORDS = [implementation_record(spec) for spec in IMPLEMENTATION_SPECS]


LIBRARY_SPECS = [
    ("analysis_design", "semantic_pure", "context.analytical_design", ["StudyDesign", "Estimand", "Population", "AnalysisPlan"], ["ResolveAnalysisDesign"], ["method-family contracts"], ["study_design", "estimand", "population_sampling", "identification"], ["nist_handbook", "consort", "dowhy_paper"]),
    ("formula_algebra", "semantic_pure", "context.formula_semantics", ["FormulaAst", "TypedExpression", "DomainError", "EvaluationSemantics"], ["TypeFormula", "EvaluateFormula"], ["formula records"], ["metric_grain", "aggregation_algebra", "missingness", "precision"], ["openformula", "apache_ossie"]),
    ("method_contracts", "semantic_pure", "context.method_semantics", ["MethodFamily", "Assumption", "Applicability", "EvaluationContract"], ["ResolveMethod"], ["method-family records"], ["study_design", "estimand", "uncertainty", "evaluation_metric"], ["nist_handbook", "statsmodels_guide"]),
    ("result_algebra", "semantic_pure", "context.analytical_result", ["AnalyticalResult", "InvalidReason", "ConvergenceStatus", "Uncertainty"], ["InterpretResult"], ["result-state algebra"], ["uncertainty", "precision"], ["statsmodels_guide", "stan_reference"]),
    ("statistical_estimators", "algorithm_pure", "", ["EstimatorSpec", "FittedEstimator", "EstimateResult"], ["Fit", "Estimate", "Update"], ["inferential estimator records"], ["missingness", "uncertainty", "random_stream", "precision"], ["scipy_stats", "statsmodels_guide", "r_stats"]),
    ("probability_distribution_algebra", "semantic_pure", "context.probability_distribution", ["DistributionFamily", "Parameterization", "Support", "DensityOrMass", "Cdf", "Quantile"], ["ValidateDistribution", "EvaluateDensity", "EvaluateCdf", "EvaluateQuantile"], ["probability-distribution semantic contracts"], ["precision", "uncertainty", "random_stream"], ["scipy_stats", "r_stats", "stan_reference"]),
    ("descriptive_statistics", "algorithm_pure", "", ["SampleView", "SummaryProfile", "MomentResult", "QuantileResult", "RobustSummary"], ["Summarize", "ComputeMoments", "ComputeQuantiles", "ComputeRobustSummary"], ["descriptive-statistics algorithms"], ["missingness", "precision", "uncertainty"], ["nist_handbook", "scipy_stats", "r_stats"]),
    ("inferential_tests_resampling", "algorithm_pure", "", ["NullHypothesis", "Alternative", "TestProfile", "ResamplingPlan", "TestResult"], ["TestHypothesis", "Bootstrap", "Permute", "AdjustMultiplicity"], ["inferential test and resampling algorithms"], ["study_design", "population_sampling", "missingness", "random_stream", "uncertainty", "multiplicity"], ["nist_handbook", "asa_pvalue", "scipy_stats", "r_stats"]),
    ("regression_glm_estimators", "algorithm_pure", "", ["DesignMatrix", "RegressionFamily", "LinkFunction", "FittedRegression", "RegressionDiagnostics"], ["FitRegression", "PredictRegression", "DiagnoseRegression"], ["regression and GLM estimators"], ["missingness", "precision", "uncertainty", "evaluation_split"], ["statsmodels_guide", "r_stats", "scipy_stats"]),
    ("survival_event_history_estimators", "algorithm_pure", "", ["EventHistory", "CensoringProfile", "RiskSet", "FittedSurvivalModel", "SurvivalResult"], ["EstimateSurvival", "FitHazardModel", "EvaluateSurvival"], ["survival and event-history estimators"], ["missingness", "uncertainty", "evaluation_split"], ["statsmodels_survival", "lifelines", "nist_handbook"]),
    ("probabilistic_inference", "algorithm_pure", "", ["ProbabilisticModel", "InferencePlan", "PosteriorArtifact", "SamplerDiagnostics", "PosteriorPredictive"], ["CompileProbabilisticModel", "InferPosterior", "DiagnoseSampler", "GeneratePosteriorPredictive"], ["probabilistic inference algorithms"], ["random_stream", "precision", "uncertainty", "resource_budget", "cancellation"], ["stan_reference", "pymc_api"]),
    ("causal_methods", "algorithm_pure", "", ["CausalModel", "IdentificationResult", "EffectEstimate"], ["Identify", "FitNuisance", "EstimateEffect", "Refute"], ["causal method records"], ["identification", "evaluation_split", "random_stream"], ["dowhy_docs", "doubleml_docs"]),
    ("causal_graph_identification", "algorithm_pure", "", ["CausalGraph", "CausalQuery", "AssumptionSet", "IdentificationResult", "AdjustmentSet"], ["ValidateCausalGraph", "IdentifyEffect", "EnumerateAdjustmentSets"], ["causal graph and identification algorithms"], ["identification", "estimand", "missingness"], ["dowhy_paper", "dowhy_docs"]),
    ("causal_effect_estimators", "algorithm_pure", "", ["CausalEstimand", "NuisancePlan", "OverlapDiagnostic", "EffectEstimate", "EffectUncertainty"], ["FitNuisance", "EstimateCausalEffect", "DiagnoseOverlap"], ["causal effect-estimation algorithms"], ["identification", "evaluation_split", "random_stream", "uncertainty"], ["doubleml_docs", "econml_docs", "dowhy_docs"]),
    ("causal_refutation_sensitivity", "algorithm_pure", "", ["EffectEstimate", "RefutationPlan", "SensitivityModel", "RefutationResult", "RobustnessEnvelope"], ["RunRefutation", "AnalyzeSensitivity", "ComparePlacebo"], ["causal refutation and sensitivity algorithms"], ["identification", "random_stream", "uncertainty"], ["dowhy_paper", "dowhy_docs"]),
    ("experiment_protocol_semantics", "semantic_pure", "context.experimental_design", ["ExperimentProtocol", "ProtocolEdition", "ExperimentUnit", "UnitRegistry", "EligibilityRule", "TreatmentArm", "InterferenceProfile"], ["AuthorExperimentProtocol", "ValidateEligibility", "SealExperimentProtocol"], ["prospective experiment protocol and eligibility contracts"], ["study_design", "estimand", "experiment_unit_identity", "experiment_eligibility", "experiment_interference"], ["nist_handbook", "consort", "fda_adaptive"]),
    ("experiment_assignment_state", "policy_pure", "context.experiment_assignment", ["AssignmentIdentity", "AssignmentEpoch", "AssignmentState", "AssignmentDecision", "PersistentAssignment", "AssignmentOverride"], ["AssignEligibleUnit", "ReplayAssignment", "StopNewAssignments", "ApplyAuthorizedOverride"], ["total experiment-assignment state machine"], ["experiment_unit_identity", "experiment_assignment", "experiment_assignment_persistence", "experiment_override", "determinism"], ["openfeature_spec", "growthbook_ab", "statsig_lifecycle"]),
    ("experiment_randomization_methods", "algorithm_pure", "", ["RandomizationPlan", "AllocationRatio", "Stratum", "Block", "Cluster", "RandomizationReceipt"], ["RandomizeCompletely", "RandomizeWithinBlock", "RandomizeCluster", "CheckAllocationBalance"], ["reproducible randomization and allocation algorithms"], ["experiment_assignment", "random_stream", "determinism", "precision"], ["nist_handbook", "consort", "growthbook_ab"]),
    ("experiment_exposure_occurrence", "semantic_pure", "context.experiment_exposure", ["ExposureOccurrence", "AssignmentRef", "TreatmentDelivered", "ExposureTime", "ExposureDeduplicationKey", "NonCompliance"], ["RecordExposure", "DeduplicateExposure", "LinkExposureToAssignment", "ClassifyNonCompliance"], ["actual treatment-exposure occurrence contracts"], ["experiment_unit_identity", "experiment_exposure", "missingness"], ["openfeature_spec", "statsig_assignment", "growthbook_ab"]),
    ("experiment_analysis_cut_stopping", "policy_pure", "context.experiment_analysis_cut", ["InterimLook", "StoppingPolicy", "AssignmentCut", "ExposureCut", "MetricCut", "LateArrivalPolicy", "LockedAnalysisCut"], ["OpenInterimLook", "EvaluateStoppingRule", "LockAnalysisCut", "RejectPostCutMutation"], ["analysis-cut, repeated-look and stopping policy contracts"], ["experiment_analysis_cut", "experiment_stopping", "multiplicity", "evaluation_split"], ["fda_adaptive", "consort", "statsig_lifecycle"]),
    ("forecasting_methods", "algorithm_pure", "", ["ForecastHorizon", "ForecastOrigin", "FittedForecaster", "Forecast"], ["FitForecast", "UpdateForecast", "PredictHorizon", "Reconcile"], ["forecasting method records"], ["forecast_horizon", "forecast_reconciliation", "evaluation_split"], ["forecasting_book", "sktime_forecasting"]),
    ("time_series_semantics", "semantic_pure", "context.time_series_semantics", ["TimeSeriesIndex", "ObservationCut", "ForecastOrigin", "ForecastHorizon", "RevisionIdentity", "TemporalSplit"], ["ValidateTimeSeries", "ResolveInformationCut", "ResolveForecastHorizon", "BuildTemporalSplit"], ["time-series and forecast-index semantic contracts"], ["forecast_horizon", "evaluation_split", "missingness"], ["forecasting_book", "sktime_forecasting", "statsmodels_tsa"]),
    ("forecast_estimators", "algorithm_pure", "", ["ForecasterSpec", "FittedForecaster", "ForecastRequest", "ForecastDistribution", "FitDiagnostics"], ["FitForecaster", "UpdateForecaster", "ProduceForecast"], ["forecast estimator algorithms"], ["forecast_horizon", "evaluation_split", "random_stream", "uncertainty"], ["forecasting_book", "sktime_forecasting", "statsmodels_tsa", "statsforecast_docs"]),
    ("forecast_evaluation", "algorithm_pure", "", ["RollingOriginPlan", "ForecastObservationJoin", "ScoringRule", "CalibrationResult", "ForecastEvaluation"], ["BacktestForecast", "ScoreForecast", "EvaluateCalibration"], ["forecast evaluation algorithms"], ["forecast_horizon", "evaluation_metric", "evaluation_split", "uncertainty"], ["forecasting_book", "sktime_forecasting", "statsforecast_docs"]),
    ("forecast_reconciliation", "algorithm_pure", "", ["ForecastHierarchy", "CoherenceConstraint", "ReconciliationProfile", "ReconciledForecast", "CoherenceResidual"], ["ValidateHierarchy", "ReconcileForecast", "MeasureCoherence"], ["forecast reconciliation algorithms"], ["forecast_horizon", "forecast_reconciliation", "precision", "uncertainty"], ["forecasting_book", "sktime_forecasting"]),
    ("anomaly_baseline", "algorithm_pure", "", ["ReferenceWindow", "BaselineProfile", "BaselineArtifact", "RegimeDiagnostic"], ["FitBaseline", "UpdateBaseline", "DiagnoseRegime"], ["anomaly baseline algorithms"], ["anomaly_threshold", "evaluation_split", "missingness", "random_stream"], ["sklearn_outlier", "river_anomaly"]),
    ("anomaly_detectors", "algorithm_pure", "", ["BaselineArtifact", "DetectorProfile", "AnomalyScore", "ThresholdProfile", "AnomalyFinding"], ["ScoreObservation", "CalibrateThreshold", "DetectAnomaly"], ["anomaly detector algorithms"], ["anomaly_threshold", "evaluation_metric", "uncertainty"], ["sklearn_outlier", "river_anomaly"]),
    ("change_point_detectors", "algorithm_pure", "", ["OrderedObservationStream", "ChangeDetectorProfile", "ChangeScore", "ChangePoint", "DetectionDelay"], ["UpdateChangeDetector", "DetectChangePoint", "EvaluateDetectionDelay"], ["change-point and drift detector algorithms"], ["anomaly_threshold", "evaluation_metric", "resource_budget"], ["river_drift", "nist_handbook"]),
    ("analytical_finding_contract", "semantic_pure", "context.analytical_finding", ["FindingIdentity", "FindingScope", "EvidenceWindow", "ErrorProfile", "FindingStatus", "AdjudicationHandoff"], ["ConstructFinding", "AttachEvidenceWindow", "RequestAdjudication"], ["non-authoritative analytical finding contracts"], ["anomaly_threshold", "uncertainty"], ["sklearn_outlier", "river_anomaly", "nist_handbook"]),
    ("process_methods", "algorithm_pure", "", ["EventLogView", "ProcessModel", "ConformanceResult"], ["Discover", "Align", "Replay", "Enhance"], ["process method records"], ["process_perspective", "conformance_cost"], ["ocel20", "pm4py", "prom"]),
    ("process_event_projection", "semantic_pure", "context.process_event_projection", ["SourceEvent", "EventIdentity", "ObjectIdentity", "QualifiedRelation", "OcedView", "OcelView"], ["CorrelateEvents", "ProjectOced", "ProjectOcel"], ["event/object projection contracts"], ["process_perspective", "multiplicity", "missingness"], ["ocel20", "oced_core", "pm4py"]),
    ("process_case_projection", "semantic_pure", "context.process_case_projection", ["CaseDefinition", "LeadingObjectSelection", "CaseProjection", "ProjectionLoss"], ["DefineCase", "ProjectCases", "ExplainProjectionLoss"], ["case-projection contracts"], ["process_perspective", "multiplicity"], ["process_manifesto", "ocel20", "pm4py"]),
    ("process_state_aware_projection", "semantic_pure", "context.process_state_projection", ["ObjectStateDefinition", "ObjectStateAt", "StateTransition", "GeneratedStateEvent", "StateAwareOcel"], ["DeriveObjectState", "GenerateStateTransition", "ProjectStateAwareOcel"], ["state-aware projection contracts"], ["process_perspective", "multiplicity", "missingness"], ["state_aware_ocpm", "ocel20"]),
    ("process_temporal_graph_projection", "semantic_pure", "context.process_temporal_graph_projection", ["TemporalEntitySnapshot", "SnapshotSuccessor", "TemporalEventKnowledgeGraph", "GraphProjectionLoss"], ["SnapshotEntities", "ProjectTemporalEkg", "ExplainTemporalGraphLoss"], ["temporal event-graph projection contracts"], ["process_perspective", "multiplicity", "graph_semantics"], ["temporal_ekg", "ocel20"]),
    ("process_discovery_methods", "algorithm_pure", "", ["EventLogView", "DiscoveryProfile", "ProcessModel", "DiscoveryDiagnostics"], ["DiscoverProcessModel", "EvaluateDiscovery"], ["process-discovery method records"], ["process_perspective", "resource_budget", "random_stream"], ["process_manifesto", "pm4py", "prom"]),
    ("process_conformance_methods", "algorithm_pure", "", ["EventLogView", "ProcessModel", "AlignmentProfile", "ConformanceResult"], ["Align", "Replay", "CheckConformance"], ["process-conformance method records"], ["process_perspective", "conformance_cost", "resource_budget"], ["process_manifesto", "pm4py", "prom"]),
    ("process_performance_methods", "algorithm_pure", "", ["EventLogView", "ProcessModel", "PerformanceProfile", "ProcessPerformanceResult"], ["MeasurePerformance", "DetectBottleneck", "EnhanceModel"], ["process-performance method records"], ["process_perspective", "multiplicity", "uncertainty"], ["process_manifesto", "pm4py", "prom"]),
    ("data_quality_methods", "algorithm_pure", "", ["QualityRule", "Measurement", "AssertionResult"], ["Profile", "Measure", "Validate", "Reconcile"], ["data-quality method records"], ["metric_grain", "missingness", "resource_budget"], ["great_expectations", "deequ", "sodacl"]),
    ("graph_methods", "algorithm_pure", "", ["GraphView", "GraphAlgorithmSpec", "GraphResult"], ["Traverse", "ShortestPath", "Centrality", "Partition"], ["graph method records"], ["graph_semantics", "resource_budget"], ["graphblas_c", "networkx_algorithms"]),
    ("graph_semantics", "semantic_pure", "context.graph_semantics", ["GraphSchema", "VertexIdentity", "EdgeIdentity", "GraphView", "Directionality", "Multiplicity", "WeightAlgebra", "TemporalGraphCut"], ["ValidateGraph", "CreateGraphView", "ResolveGraphCut"], ["typed graph representation and view contracts"], ["graph_semantics", "multiplicity", "missingness"], ["graphblas_c", "networkx_algorithms", "igraph_manual"]),
    ("graph_traversal_path_methods", "algorithm_pure", "", ["GraphView", "TraversalProfile", "PathProfile", "TraversalResult", "PathResult"], ["TraverseGraph", "FindShortestPath", "EnumerateReachability"], ["graph traversal and path algorithms"], ["graph_semantics", "resource_budget", "determinism"], ["networkx_algorithms", "igraph_manual", "graphblas_c"]),
    ("graph_centrality_methods", "algorithm_pure", "", ["GraphView", "CentralityProfile", "CentralityScore", "CentralityResult"], ["ComputeCentrality", "RankVertices"], ["graph centrality algorithms"], ["graph_semantics", "precision", "resource_budget"], ["networkx_algorithms", "igraph_manual", "lagraph_paper"]),
    ("graph_community_methods", "algorithm_pure", "", ["GraphView", "CommunityProfile", "Partition", "CommunityDiagnostics"], ["DetectCommunities", "EvaluatePartition"], ["graph community and partition algorithms"], ["graph_semantics", "random_stream", "evaluation_metric", "resource_budget"], ["networkx_algorithms", "igraph_manual"]),
    ("graph_semiring_kernel_facade", "runtime_mechanism", "", ["GraphMatrixView", "SemiringSpec", "MaskSpec", "GraphKernelRequirement", "GraphKernelReceipt"], ["DispatchGraphMxv", "DispatchGraphMxm", "CancelGraphKernel"], ["GraphBLAS/semiring kernel contracts"], ["graph_semantics", "layout", "precision", "determinism", "resource_budget", "cancellation"], ["graphblas_c", "graphblas_cpp", "suitesparse_graphblas", "lagraph_paper"]),
    ("spatial_methods", "algorithm_pure", "", ["Geometry", "Crs", "SpatialWeights", "SpatialResult"], ["Predicate", "Transform", "Interpolate", "SpatialFit"], ["spatial method records"], ["spatial_reference", "precision"], ["ogc_sfa", "proj", "geos"]),
    ("spatial_reference_semantics", "semantic_pure", "context.spatial_reference_semantics", ["CoordinateReferenceSystem", "Datum", "AxisOrder", "CoordinateEpoch", "SpatialSupport", "AccuracyEnvelope"], ["ValidateSpatialReference", "ResolveAxisOrder", "CompareSpatialSupport"], ["spatial-reference semantic contracts"], ["spatial_reference", "precision"], ["ogc_sfa", "ogc_om", "proj"]),
    ("coordinate_transform_methods", "algorithm_pure", "", ["CoordinateTuple", "SourceCrs", "TargetCrs", "TransformPipeline", "TransformAccuracy", "TransformResult"], ["SelectTransformPipeline", "TransformCoordinates", "EvaluateTransformAccuracy"], ["coordinate transformation algorithms"], ["spatial_reference", "precision", "resource_budget"], ["proj", "gdal", "postgis"]),
    ("vector_geometry_topology", "algorithm_pure", "", ["Geometry", "TopologyModel", "PredicateProfile", "OverlayProfile", "GeometryResult"], ["ValidateGeometry", "EvaluateSpatialPredicate", "OverlayGeometry", "RepairGeometry"], ["vector geometry and topology algorithms"], ["spatial_reference", "precision", "resource_budget"], ["ogc_sfa", "geos", "postgis"]),
    ("raster_grid_methods", "algorithm_pure", "", ["RasterGrid", "GridGeometry", "NoDataProfile", "ResamplingProfile", "RasterResult"], ["WarpRaster", "ResampleRaster", "MapAlgebra", "ZonalAggregate"], ["raster and grid algorithms"], ["spatial_reference", "precision", "missingness", "resource_budget"], ["gdal", "ogc_om"]),
    ("spatial_statistics_methods", "algorithm_pure", "", ["SpatialObservation", "SpatialWeights", "SpatialStatisticProfile", "SpatialModel", "SpatialStatisticalResult"], ["BuildSpatialWeights", "MeasureSpatialAutocorrelation", "FitSpatialModel", "InterpolateSpatially"], ["spatial statistics algorithms"], ["spatial_reference", "precision", "uncertainty", "evaluation_split"], ["pysal_esda", "pysal_spreg", "ogc_om"]),
    ("text_semantics", "semantic_pure", "context.text_semantics", ["UnicodeProfile", "TextBoundary", "AnalyzerSpec"], ["NormalizeText", "SegmentText", "CollateText"], ["text method records"], ["text_locale"], ["unicode_uax15", "unicode_uax29", "icu_boundary"]),
    ("search_methods", "algorithm_pure", "", ["IndexSpec", "QuerySpec", "RankingProfile", "SearchResult"], ["BuildIndex", "Search", "ExplainScore"], ["search method records"], ["text_locale", "retrieval_ranking", "compression"], ["lucene_core", "lucene_similarity", "tantivy"]),
    ("document_container_semantics", "semantic_pure", "context.document_container", ["DocumentMediaType", "DocumentProfile", "PackagePart", "PartRelationship", "EmbeddedResource", "ProtectionStatus"], ["DetectDocumentProfile", "EnumeratePackageParts", "ResolveEmbeddedResources", "ValidateDocumentProtection"], ["document container/package contracts"], ["document_profile", "document_recursion", "document_encryption", "document_resource_safety"], ["pdf20", "ecma376", "odf13", "html_standard", "rfc5322", "rfc2045"]),
    ("document_content_graph", "semantic_pure", "context.document_content", ["DocumentIdentity", "Page", "CoordinateSpace", "Glyph", "TextSpan", "Block", "Region", "StructureNode", "ReadingOrderEdge"], ["ConstructContentGraph", "MapCoordinates", "ResolveReadingOrder", "PreserveSourceText"], ["document content and coordinate graph contracts"], ["document_coordinates", "document_reading_order", "document_text_normalization"], ["pdf20", "html_standard", "hocr", "alto"]),
    ("document_parser_adapters", "provider_adapter", "", ["DocumentBytes", "ParserProfile", "ParsedPart", "ParserWarning", "ParseReceipt"], ["ParseDocument", "ParseEmbeddedPart", "CancelDocumentParse"], ["format parser adapter contracts"], ["document_profile", "document_recursion", "document_encryption", "document_resource_safety"], ["tika", "pdfbox", "ecma376", "odf13"]),
    ("document_layout_methods", "algorithm_pure", "", ["PositionedContent", "LayoutProfile", "Line", "Block", "Region", "ReadingOrder", "LayoutResult"], ["SegmentLayout", "InferReadingOrder", "DetectRepeatedRegion", "ClassifyStructuralRole"], ["document layout-analysis algorithms"], ["document_coordinates", "document_reading_order", "document_layout"], ["pdf20", "pdfbox", "hocr", "alto"]),
    ("document_ocr_methods", "algorithm_pure", "", ["PageImage", "OcrProfile", "RecognizedGlyph", "RecognizedWord", "OcrConfidence", "OcrResult"], ["RecognizePage", "DetectOrientation", "SegmentOcrPage", "EmitPositionedOcr"], ["OCR recognition algorithms"], ["ocr_language_script", "ocr_segmentation", "document_coordinates", "document_resource_safety"], ["tesseract", "hocr", "alto"]),
    ("document_table_extraction", "algorithm_pure", "", ["TableRegion", "TableGrid", "TableRow", "TableColumn", "TableCell", "HeaderRole", "SpanningCell", "TableExtractionResult"], ["DetectTable", "RecognizeTableStructure", "AssignCellContent", "LinkContinuedTable"], ["document table-detection and structure-recognition algorithms"], ["document_coordinates", "document_reading_order", "document_table"], ["pubtables1m", "pdf20", "alto"]),
    ("document_form_extraction", "algorithm_pure", "", ["Form", "FormField", "Widget", "FieldName", "FieldValue", "Appearance", "SignatureField", "FormExtractionResult"], ["ExtractNativeForm", "AssociateFieldWidget", "ExtractFieldValue", "ValidateFormAppearance"], ["native and inferred document-form extraction algorithms"], ["document_coordinates", "document_form"], ["pdf20", "pdfbox", "html_standard"]),
    ("document_provenance_loss", "semantic_pure", "context.document_extraction_evidence", ["ExtractedElementIdentity", "SourceLocator", "BytePartPageRegionRef", "ExtractorIdentity", "Confidence", "InformationLoss", "ExtractionEvidence"], ["AttachExtractionEvidence", "CompareExtractionLoss", "RefuseUnsupportedClaim"], ["element-level extraction provenance, confidence and loss contracts"], ["document_provenance", "document_coordinates", "document_profile"], ["tika", "tesseract", "hocr", "alto"]),
    ("document_classification_methods", "algorithm_pure", "", ["DocumentView", "LabelTaxonomy", "ClassificationProfile", "LabelScore", "ClassificationResult", "Abstention"], ["ClassifyDocument", "CalibrateClassification", "AbstainClassification"], ["document classification algorithms"], ["document_label_taxonomy", "document_abstention", "evaluation_split", "uncertainty"], ["spacy_pipeline", "opennlp_manual", "sklearn_evaluation"]),
    ("document_information_extraction", "algorithm_pure", "", ["DocumentView", "ExtractionSchema", "ExtractedSpan", "ExtractedField", "ExtractedRelation", "ExtractionAlternative", "ExtractionResult"], ["ExtractSpans", "ExtractFields", "ExtractRelations", "NormalizeExtractedValue", "AbstainExtraction"], ["schema-bound document information-extraction algorithms"], ["document_field_schema", "document_abstention", "document_provenance", "missingness"], ["spacy_pipeline", "opennlp_manual", "hocr"]),
    ("document_extraction_evaluation", "test_oracle", "", ["ExtractionGoldCorpus", "MatchingPolicy", "ClassificationMetric", "SpanMetric", "RelationMetric", "TableMetric", "CalibrationMetric", "ExtractionEvaluationReceipt"], ["EvaluateDocumentClassification", "EvaluateInformationExtraction", "EvaluateTableExtraction", "EvaluateAbstention"], ["document extraction evaluation and qualification oracles"], ["document_extraction_match", "document_abstention", "evaluation_metric", "uncertainty"], ["pubtables1m", "sklearn_evaluation", "hocr"]),
    ("signal_methods", "algorithm_pure", "", ["SampledSignal", "FilterSpec", "TransformPlan", "Spectrum"], ["Filter", "Resample", "Transform", "DetectPeak"], ["signal method records"], ["signal_sampling", "precision"], ["scipy_signal", "scipy_fft", "fftw"]),
    ("image_methods", "algorithm_pure", "", ["ImageGeometry", "Image", "LabelMap", "Registration"], ["FilterImage", "Morphology", "Segment", "Register"], ["image method records"], ["image_coordinates", "precision"], ["scikit_image", "opencv_imgproc", "itk"]),
    ("semantic_metrics", "semantic_pure", "context.semantic_metric_evaluation", ["SemanticGraph", "MetricDefinition", "MetricQuery", "MetricObservation"], ["BindMetric", "LowerMetric", "EvaluateMetric"], ["semantic-metric method records"], ["metric_grain", "aggregation_algebra", "missingness"], ["apache_ossie", "dbt_semantic", "dbt_metrics"]),
    ("numerical_kernel_facade", "runtime_mechanism", "", ["ArrayView", "SparseView", "KernelRequirement", "KernelReceipt"], ["DispatchKernel", "CancelKernel"], ["numerical kernel records"], ["precision", "determinism", "layout", "kernel_backend", "resource_budget", "cancellation"], ["array_api", "blas", "lapack", "onemkl", "faer"]),
    ("columnar_kernel_facade", "runtime_mechanism", "", ["ColumnarBatch", "ComputeExpression", "ColumnarKernelReceipt"], ["DispatchCompute", "ExecuteBatch", "ExecuteStream"], ["Arrow/data kernel records"], ["layout", "precision", "resource_budget", "cancellation"], ["arrow_columnar", "arrow_compute", "arrow_acero"]),
    ("codec_adapter", "provider_adapter", "", ["EncodingSpec", "CodecSpec", "CodecReceipt"], ["Encode", "Decode", "Compress", "Decompress"], ["physical encoding and codec kernel records"], ["compression", "resource_budget", "ffi_safety"], ["parquet_encoding", "parquet_compression", "zstd", "snappy_format"]),
    ("provider_qualification", "test_oracle", "", ["QualificationProfile", "ConformanceReceipt", "BenchmarkReceipt"], ["QualifyOffer", "InvalidateReceipt"], ["qualification profiles and receipts"], ["kernel_backend", "determinism", "precision", "resource_budget"], ["array_api", "graphblas_c", "arrow_compute"]),
    ("artifact_envelope", "semantic_pure", "context.analytical_artifact", ["ArtifactIdentity", "MethodDigest", "DataDigest", "ProviderDigest", "Compatibility"], ["SealArtifact", "CheckCompatibility"], ["fitted/index/plan artifact contract"], ["artifact_persistence", "determinism"], ["stan_reference", "lucene_core", "fftw"]),
    ("operations_research_bridge", "semantic_pure", "context.or_method_bridge", ["OrMethodRef", "DecisionProblemRef", "OrResultRef"], ["ResolveOrReference", "MapOrResult"], ["dedicated OR corpus references"], ["resource_budget", "precision", "determinism"], ["nist_handbook"]),
]


def library_record(spec: tuple) -> dict:
    slug, kind, semantic_owner, public_types, public_traits, contributions, decision_slugs, evidence_slugs = spec
    pure = kind in {"semantic_pure", "algorithm_pure", "policy_pure", "test_oracle"}
    semantic_refs = [semantic_owner] if semantic_owner else []
    return {
        "library_id": f"library.method_kernels.{slug}",
        "edition": EDITION,
        "status": "specified",
        "library_kind": kind,
        "semantic_owner_refs": semantic_refs,
        "contributes_to_context_refs": [semantic_owner] if semantic_owner else ["context.method_kernel_execution"],
        "effect_boundary": "pure_no_io" if pure else ("ffi_boundary" if kind == "provider_adapter" else "effectful_runtime"),
        "public_types": public_types,
        "public_traits": public_traits,
        "operation_refs": [f"operation.method_kernels.{slug}.{trait.lower()}" for trait in public_traits],
        "error_contracts": ["InvalidInput", "UnsupportedCapability", "AssumptionUnmet", "NumericalFailure", "ResourceExhausted", "Cancelled", "ProviderFailure"],
        "decision_refs": [f"decision.method_kernels.{decision}" for decision in decision_slugs],
        "requirement_refs": [f"requirement.method_kernels.{slug}"],
        "offer_refs": [],
        "configuration_contracts": ["All semantic and runtime configuration is typed, explicit and digest-bound."],
        "effect_intents": [] if pure else ["ExecuteMethodKernel"],
        "runtime_receipts": [] if pure else ["MethodKernelExecutionReceipt"],
        "laws": [
            "Library names never own analytical meaning.",
            "A method cannot strengthen evidence supplied by its study design.",
            "Unknown or unsupported semantics produce a typed refusal.",
        ],
        "oracles": ["law fixtures", "negative twins", "reference comparison", "resource and cancellation tests"],
        "resource_contracts": ["All work, memory, concurrency and device use is finite or refused."],
        "concurrency": ["Thread safety and schedule-dependent results are declared by offer."],
        "cancellation": ["Long-running work accepts explicit cancellation and reports partial-artifact validity."],
        "unsafe_ffi_generated_policy": ["No unsafe/FFI in pure semantic libraries.", "Adapters isolate and qualify any FFI/provider boundary."],
        "dependencies": [],
        "targets": ["provider_neutral_contract"],
        "compatibility": ["Semantic edition compatibility is checked separately from serialization and ABI compatibility."],
        "removal_seams": ["Provider and target implementations bind behind requirement/offer contracts."],
        "forbidden_responsibilities": ["UI", "deployment ownership", "ambient configuration", "vendor-name dispatch", "product outcome promise"],
        "evidence_refs": [f"source.method_kernel.{source}" for source in evidence_slugs],
        "gaps": [f"Runtime implementation and two unrelated vertical qualifications remain open for {', '.join(contributions)}."],
    }


LIBRARIES = [library_record(spec) for spec in LIBRARY_SPECS]


def capability_kind(library_kind: str) -> str:
    if library_kind == "semantic_pure":
        return "semantic_contract"
    if library_kind == "algorithm_pure":
        return "analytical_practice"
    if library_kind == "test_oracle":
        return "evidence"
    return "runtime_mechanism"


REQUIREMENTS = [
    {
        "record_kind": "capability_requirement",
        "requirement_id": f"requirement.method_kernels.{row['library_id'].split('.')[-1]}",
        "edition": EDITION,
        "status": "declared",
        "subject_ref": row["library_id"],
        "capability_kind": capability_kind(row["library_kind"]),
        "contract_refs": [f"contract.method_kernel.{row['library_id'].split('.')[-1]}"],
        "operation_refs": row["operation_refs"],
        "type_refs": ["type.method_kernel.contract"],
        "required_guarantees": row["laws"] + ["All required configuration and finite budgets are resolved."],
        "applicability": {"when": ["The referenced analytical plan requires this contribution."], "unless": [], "scope_refs": [row["library_id"]]},
        "cardinality": "exactly_one",
        "binding_phase": "semantic_closure" if row["library_kind"] == "semantic_pure" else "physical_binding",
        "criticality": "blocking",
        "selection_laws": ["Select by exact contract, target, guarantees, limits and qualification evidence; never by provider name."],
        "fallback_law": "refuse",
        "prohibited_traits": ["hidden semantic defaults", "unbounded resources", "unqualified FFI", "LLM/generative dependency"],
        "evidence_gates": ["structural conformance", "semantic law tests", "target execution receipt", "version and dependency identity"],
        "owner_ref": row["contributes_to_context_refs"][0],
        "gaps": ["No provider is selected by this research corpus."],
    }
    for row in LIBRARIES
]


PROVIDER_SPECS = [
    ("numpy", "NumPy", ["numerical_kernel_facade"], ["vector.elementwise", "aggregate.reduce", "topk.select", "sort.stable", "rng.counter_based", "linalg.dot", "linalg.svd"], ["numpy_ufunc", "numpy_rng", "array_api"], ["target.cpu.python"]),
    ("scipy", "SciPy", ["statistical_estimators", "probability_distribution_algebra", "descriptive_statistics", "inferential_tests_resampling", "signal_methods", "numerical_kernel_facade"], ["fft.dft", "signal.convolution", "distance.pairwise", "histogram"], ["scipy_guide", "scipy_stats", "scipy_signal", "scipy_fft"], ["target.cpu.python"]),
    ("statsmodels", "statsmodels", ["statistical_estimators", "inferential_tests_resampling", "regression_glm_estimators", "survival_event_history_estimators", "forecasting_methods", "time_series_semantics", "forecast_estimators", "forecast_evaluation"], ["linalg.qr", "linalg.cholesky"], ["statsmodels_guide", "statsmodels_tsa", "statsmodels_survival"], ["target.cpu.python"]),
    ("r_stats", "R stats", ["statistical_estimators", "probability_distribution_algebra", "descriptive_statistics", "inferential_tests_resampling", "regression_glm_estimators", "forecasting_methods", "time_series_semantics", "forecast_estimators", "forecast_evaluation"], ["aggregate.reduce", "linalg.qr"], ["r_stats"], ["target.cpu.r"]),
    ("stan", "Stan", ["statistical_estimators", "probability_distribution_algebra", "probabilistic_inference", "artifact_envelope"], ["rng.counter_based", "vector.elementwise"], ["stan_reference"], ["target.cpu.external_runtime"]),
    ("pymc", "PyMC", ["statistical_estimators", "probability_distribution_algebra", "probabilistic_inference"], ["rng.counter_based", "vector.elementwise"], ["pymc_api"], ["target.cpu.python"]),
    ("scikit_learn", "scikit-learn", ["statistical_estimators", "anomaly_baseline", "anomaly_detectors"], ["distance.pairwise", "topk.select"], ["sklearn_evaluation", "sklearn_outlier"], ["target.cpu.python"]),
    ("doubleml", "DoubleML", ["causal_methods", "causal_effect_estimators"], ["aggregate.reduce", "linalg.qr"], ["doubleml_docs"], ["target.cpu.python"]),
    ("dowhy", "DoWhy", ["causal_methods", "causal_graph_identification", "causal_effect_estimators", "causal_refutation_sensitivity"], ["aggregate.reduce", "graph.traversal"], ["dowhy_docs", "dowhy_paper"], ["target.cpu.python"]),
    ("econml", "EconML", ["causal_effect_estimators"], ["aggregate.reduce", "linalg.qr"], ["econml_docs"], ["target.cpu.python"]),
    ("sktime", "sktime", ["forecasting_methods", "time_series_semantics", "forecast_estimators", "forecast_evaluation", "forecast_reconciliation"], ["aggregate.reduce", "linalg.qr", "sort.stable"], ["sktime_forecasting", "forecasting_book"], ["target.cpu.python"]),
    ("statsforecast", "StatsForecast", ["forecasting_methods", "time_series_semantics", "forecast_estimators", "forecast_evaluation"], ["aggregate.reduce", "linalg.qr", "sort.stable"], ["statsforecast_docs"], ["target.cpu.python"]),
    ("river", "River", ["anomaly_baseline", "anomaly_detectors", "change_point_detectors", "analytical_finding_contract"], ["aggregate.reduce", "histogram", "sort.stable"], ["river_anomaly", "river_drift"], ["target.cpu.python"]),
    ("growthbook", "GrowthBook", ["experiment_protocol_semantics", "experiment_assignment_state", "experiment_randomization_methods", "experiment_exposure_occurrence", "experiment_analysis_cut_stopping"], ["rng.counter_based", "aggregate.hash", "join.hash", "sort.stable"], ["growthbook_ab"], ["target.cpu.external_runtime"]),
    ("statsig", "Statsig", ["experiment_protocol_semantics", "experiment_assignment_state", "experiment_randomization_methods", "experiment_exposure_occurrence", "experiment_analysis_cut_stopping"], ["rng.counter_based", "aggregate.hash", "join.hash", "sort.stable"], ["statsig_assignment", "statsig_lifecycle"], ["target.cpu.external_runtime"]),
    ("pm4py", "PM4Py", ["process_methods", "process_event_projection", "process_case_projection", "process_discovery_methods", "process_conformance_methods", "process_performance_methods"], ["graph.traversal", "topk.select"], ["pm4py", "ocel20"], ["target.cpu.python"]),
    ("prom", "ProM", ["process_methods", "process_discovery_methods", "process_conformance_methods", "process_performance_methods"], ["graph.traversal", "topk.select"], ["prom", "process_manifesto"], ["target.jvm.external_runtime"]),
    ("great_expectations", "Great Expectations", ["data_quality_methods"], ["aggregate.reduce", "join.hash"], ["great_expectations"], ["target.cpu.python"]),
    ("deequ", "Deequ", ["data_quality_methods"], ["aggregate.reduce", "join.hash"], ["deequ"], ["target.jvm.spark"]),
    ("soda", "Soda", ["data_quality_methods"], ["aggregate.reduce", "join.hash"], ["sodacl"], ["target.cpu.python"]),
    ("suitesparse_graphblas", "SuiteSparse:GraphBLAS", ["graph_methods", "graph_semiring_kernel_facade", "numerical_kernel_facade"], ["graph.semiring_mxv", "graph.semiring_mxm", "sparse.spmv"], ["suitesparse_graphblas", "graphblas_c"], ["target.cpu.native"]),
    ("networkx", "NetworkX", ["graph_methods", "graph_semantics", "graph_traversal_path_methods", "graph_centrality_methods", "graph_community_methods"], ["graph.traversal", "topk.select"], ["networkx_algorithms"], ["target.cpu.python"]),
    ("igraph", "igraph", ["graph_methods", "graph_semantics", "graph_traversal_path_methods", "graph_centrality_methods", "graph_community_methods"], ["graph.traversal", "topk.select"], ["igraph_manual"], ["target.cpu.native"]),
    ("lagraph", "LAGraph", ["graph_traversal_path_methods", "graph_centrality_methods", "graph_semiring_kernel_facade"], ["graph.traversal", "graph.semiring_mxv", "graph.semiring_mxm"], ["lagraph_paper", "graphblas_c"], ["target.cpu.native"]),
    ("geos", "GEOS", ["spatial_methods", "vector_geometry_topology"], ["geometry.predicate"], ["geos", "ogc_sfa"], ["target.cpu.native"]),
    ("proj", "PROJ", ["spatial_methods", "spatial_reference_semantics", "coordinate_transform_methods"], ["spatial.transform"], ["proj", "ogc_sfa"], ["target.cpu.native"]),
    ("gdal", "GDAL", ["spatial_methods", "spatial_reference_semantics", "coordinate_transform_methods", "vector_geometry_topology", "raster_grid_methods"], ["spatial.transform", "aggregate.reduce"], ["gdal"], ["target.cpu.native"]),
    ("postgis", "PostGIS", ["spatial_methods", "spatial_reference_semantics", "coordinate_transform_methods", "vector_geometry_topology"], ["geometry.predicate", "spatial.transform", "join.hash"], ["postgis", "ogc_sfa"], ["target.database.postgresql"]),
    ("pysal", "PySAL", ["spatial_methods", "spatial_statistics_methods", "statistical_estimators"], ["sparse.spmv", "linalg.qr"], ["pysal_esda", "pysal_spreg"], ["target.cpu.python"]),
    ("icu", "ICU", ["text_semantics"], ["text.normalize", "text.segmentation", "text.fst"], ["icu_boundary", "icu_collation", "unicode_uax15", "unicode_uax29"], ["target.cpu.native"]),
    ("lucene", "Apache Lucene", ["search_methods"], ["search.postings", "text.fst", "topk.select"], ["lucene_core", "lucene_similarity"], ["target.jvm.embedded"]),
    ("tantivy", "Tantivy", ["search_methods"], ["search.postings", "text.fst", "topk.select"], ["tantivy"], ["target.rust.embedded"]),
    ("tika", "Apache Tika", ["document_container_semantics", "document_content_graph", "document_parser_adapters", "document_provenance_loss"], ["document.container_parse", "document.positioned_text", "document.layout_group"], ["tika"], ["target.jvm.external_runtime"]),
    ("pdfbox", "Apache PDFBox", ["document_container_semantics", "document_content_graph", "document_parser_adapters", "document_layout_methods", "document_form_extraction", "document_provenance_loss"], ["document.container_parse", "document.positioned_text", "document.layout_group", "document.form_tree"], ["pdfbox", "pdf20"], ["target.jvm.embedded"]),
    ("tesseract", "Tesseract OCR", ["document_ocr_methods", "document_provenance_loss"], ["document.ocr_runtime"], ["tesseract", "hocr", "alto"], ["target.cpu.external_runtime"]),
    ("table_transformer", "Microsoft Table Transformer", ["document_table_extraction"], ["document.table_structure"], ["pubtables1m"], ["target.cpu.python"]),
    ("spacy", "spaCy", ["document_classification_methods", "document_information_extraction"], ["document.classification_runtime", "document.information_extraction_runtime"], ["spacy_pipeline"], ["target.cpu.python"]),
    ("opennlp", "Apache OpenNLP", ["document_classification_methods", "document_information_extraction"], ["document.classification_runtime", "document.information_extraction_runtime"], ["opennlp_manual"], ["target.jvm.embedded"]),
    ("fftw", "FFTW", ["signal_methods", "numerical_kernel_facade"], ["fft.dft"], ["fftw"], ["target.cpu.native"]),
    ("opencv", "OpenCV", ["image_methods"], ["signal.convolution", "image.morphology", "image.connected_components"], ["opencv_imgproc"], ["target.cpu.native"]),
    ("scikit_image", "scikit-image", ["image_methods"], ["signal.convolution", "image.morphology", "image.connected_components"], ["scikit_image"], ["target.cpu.python"]),
    ("itk", "ITK", ["image_methods"], ["signal.convolution", "spatial.interpolation"], ["itk"], ["target.cpu.native"]),
    ("netlib_lapack", "Netlib BLAS/LAPACK", ["numerical_kernel_facade"], ["linalg.dot", "linalg.gemm", "linalg.qr", "linalg.cholesky", "linalg.svd"], ["blas", "lapack"], ["target.cpu.native"]),
    ("onemkl", "oneMKL", ["numerical_kernel_facade"], ["linalg.dot", "linalg.gemm", "linalg.qr", "linalg.cholesky", "sparse.spmv", "fft.dft", "rng.counter_based"], ["onemkl"], ["target.oneapi.devices"]),
    ("faer", "faer", ["numerical_kernel_facade"], ["linalg.gemm", "linalg.qr", "linalg.cholesky", "linalg.svd", "sparse.spmv"], ["faer"], ["target.rust.cpu"]),
    ("ndarray", "Rust ndarray", ["numerical_kernel_facade"], ["vector.elementwise", "aggregate.reduce", "linalg.dot"], ["ndarray"], ["target.rust.cpu"]),
    ("statrs", "statrs", ["statistical_estimators"], ["vector.elementwise"], ["statrs"], ["target.rust.cpu"]),
    ("linfa", "linfa", ["statistical_estimators"], ["linalg.qr", "distance.pairwise"], ["linfa"], ["target.rust.cpu"]),
    ("arrow_compute", "Apache Arrow Compute/Acero", ["columnar_kernel_facade"], ["arrow.compute_dispatch", "aggregate.hash", "join.hash", "sort.stable"], ["arrow_columnar", "arrow_compute", "arrow_acero"], ["target.cpu.native"]),
    ("zstd", "Zstandard", ["codec_adapter"], ["compression.zstd"], ["zstd"], ["target.cpu.native"]),
    ("snappy", "Snappy", ["codec_adapter"], ["compression.snappy"], ["snappy_format"], ["target.cpu.native"]),
    ("parquet", "Apache Parquet encodings", ["codec_adapter"], ["data.dictionary_encode", "data.rle_bitpack", "data.delta_encode"], ["parquet_encoding", "parquet_compression"], ["target.columnar.file"]),
    ("dbt_metricflow", "dbt MetricFlow", ["semantic_metrics"], ["aggregate.hash", "join.hash"], ["dbt_semantic", "dbt_metrics"], ["target.database.pushdown"]),
]


def provider_offer(spec: tuple) -> dict:
    provider_slug, name, library_slugs, kernel_slugs, evidence_slugs, targets = spec
    operations = [f"kernel.{slug}" for slug in kernel_slugs]
    contracts = [f"contract.method_kernel.{slug}" for slug in library_slugs]
    return {
        "record_kind": "capability_offer",
        "offer_id": f"offer.method_kernels.{provider_slug}",
        "edition": EDITION,
        "status": "declared",
        "provider_ref": f"provider.{provider_slug}",
        "capability_kind": "runtime_mechanism",
        "contract_refs": contracts,
        "operation_refs": operations,
        "type_refs": ["type.method_kernel.contract"],
        "guarantees": [f"Official documentation describes {name}'s named interfaces; no deployment qualification is implied."],
        "limits": ["Exact version, build features, dtype/layout, target, determinism, resource and error behavior require probing."],
        "decision_refs": ["decision.method_kernels.precision", "decision.method_kernels.determinism", "decision.method_kernels.layout", "decision.method_kernels.resource_budget"],
        "target_refs": targets,
        "applicability": {"when": ["Exact version and target are qualified against every required operation."], "unless": ["A semantic, policy, target or evidence gate fails."], "scope_refs": [f"provider.{provider_slug}"]},
        "exclusions": ["Provider name is not a semantic owner.", "No undocumented operation or guarantee is offered.", "No LLM/generative dependency is admitted."],
        "conformance_receipts": [],
        "evidence_refs": [f"source.method_kernel.{source}" for source in evidence_slugs],
        "validity": {"from": ACCESSED, "until": None, "recheck_triggers": ["provider release", "dependency/build change", "target change", "qualification expiry", "security advisory"]},
        "gaps": ["No executed SAN conformance receipt exists in this research edition."],
    }


OFFERS = [provider_offer(spec) for spec in PROVIDER_SPECS]


COMPILER_GAPS = [
    {
        "record_kind": "compiler_gap",
        "gap_id": f"gap.method_kernels.{slug}",
        "edition": EDITION,
        "status": "open",
        "subject_ref": subject,
        "gap_kind": kind,
        "blocking": True,
        "missing_contracts": contracts,
        "attempted_bindings": [],
        "observed_evidence": [],
        "owner_ref": "context.method_kernel_binding",
        "resolution_condition": resolution,
        "prohibited_fallbacks": ["select by provider name", "accept provider documentation as runtime qualification", "weaken method assumptions", "silently use a default"],
    }
    for slug, subject, kind, contracts, resolution in [
        ("unqualified_runtime", "library.method_kernels.numerical_kernel_facade", "unqualified_provider", ["contract.method_kernel.numerical_kernel_facade"], "Execute conformance, numerical, determinism, resource and cancellation profiles on the exact target."),
        ("unknown_method", "library.method_kernels.method_contracts", "missing_offer", ["contract.method_kernel.method_contracts"], "Add and adjudicate a provider-neutral method-family contract with authoritative evidence."),
        ("artifact_compatibility", "library.method_kernels.artifact_envelope", "evidence_insufficient", ["contract.method_kernel.artifact_envelope"], "Demonstrate version-change, replay, migration and invalidation behavior for fitted/index/plan artifacts."),
        ("codec_safety", "library.method_kernels.codec_adapter", "unqualified_provider", ["contract.method_kernel.codec_adapter"], "Qualify corrupt/truncated/adversarial inputs, output bounds, checksums, dictionaries and cancellation."),
        ("vertical_validity", "library.method_kernels.analysis_design", "missing_vertical_case", ["contract.method_kernel.analysis_design"], "Bind at least two unrelated vertical analytical cases and pass domain acceptance."),
    ]
]


COMPILER_RECORDS = REQUIREMENTS + OFFERS + COMPILER_GAPS


QUALIFICATION_SPECS = [
    ("analysis_design", "library.method_kernels.analysis_design", "Analysis-design implementation preserves population, estimand, authority, prospective protocol identity and refusal semantics.", ["randomized, observational and simulation designs", "missing estimand", "post-outcome protocol mutation", "unauthorized design twin"], ["schema/type oracle", "prospective-version oracle", "authority/refusal oracle"]),
    ("experiment_protocol", "library.method_kernels.experiment_protocol_semantics", "Experiment protocol preserves unit, eligibility, treatment, interference, estimand, authority and prospective edition semantics.", ["individual and cluster randomization", "eligibility boundary times", "overlapping experiment twin", "post-start protocol edit"], ["protocol identity oracle", "eligibility as-of oracle", "sealed-protocol mutation refusal"]),
    ("experiment_assignment_state", "library.method_kernels.experiment_assignment_state", "Assignment state is total, replayable and stable under exact unit, protocol, epoch, persistence, stop and override semantics.", ["same-unit replay", "epoch/salt change", "stop-new-assignment case", "authorized and unauthorized overrides"], ["state-transition oracle", "assignment replay oracle", "stop/override authority oracle"]),
    ("experiment_randomization", "library.method_kernels.experiment_randomization_methods", "Randomization preserves declared allocation, block/stratum/cluster, random-stream, determinism and balance semantics.", ["known seeded allocation", "unequal ratios", "small and incomplete blocks", "cluster and stratified assignments"], ["exact seeded replay", "allocation-count oracle", "Monte Carlo balance/distribution test"]),
    ("experiment_exposure", "library.method_kernels.experiment_exposure_occurrence", "Exposure occurrence preserves unit, assignment, delivered treatment, event time, deduplication, provenance and noncompliance without equating assignment with exposure.", ["assigned-not-exposed", "exposed-not-assigned", "duplicate/retried delivery", "cross-device identity change"], ["assignment/exposure non-equivalence oracle", "deduplication oracle", "event-time/provenance oracle"]),
    ("experiment_analysis_cut_stopping", "library.method_kernels.experiment_analysis_cut_stopping", "Analysis cut and stopping implementation freezes exact assignment, exposure, metric and as-of inputs and applies only prospective repeated-look/stopping rules.", ["late-arriving metric twin", "unplanned peek", "sequential-spending boundary", "safety stop and ordinary stop"], ["cut digest/replay oracle", "post-cut mutation refusal", "stopping/multiplicity reference"]),
    ("semantic_formula", "library.method_kernels.formula_algebra", "Formula typing and evaluation preserve units, grain, totality, null/error and dependency semantics.", ["typed formula fixtures", "zero/empty/null/NaN negative twins", "unit and grain counterexamples", "two backend lowerings"], ["schema validation", "typechecking oracle", "algebraic law oracle", "exact reference values"]),
    ("statistical_estimator", "library.method_kernels.statistical_estimators", "Estimator implementation preserves the method assumptions, estimand, convergence and uncertainty contract.", ["known analytic cases", "Monte Carlo coverage suite", "misspecified-assumption twins", "ill-conditioned numerical fixtures"], ["reference implementation", "bias/coverage oracle", "residual/convergence oracle"]),
    ("probability_distribution", "library.method_kernels.probability_distribution_algebra", "Distribution implementation preserves parameterization, support, normalization and density/mass/CDF/quantile identities.", ["analytic distribution identities", "boundary and tail cases", "invalid parameterizations", "sampling moment/quantile checks"], ["normalization and monotonicity laws", "CDF/quantile inversion", "cross-provider reference values"]),
    ("descriptive_statistics", "library.method_kernels.descriptive_statistics", "Summary implementation preserves population/sample, weighting, missingness, degrees-of-freedom, order-statistic and numerical-accumulation semantics.", ["empty/singleton/constant samples", "weighted and missingness twins", "large-offset cancellation cases", "known robust-statistic fixtures"], ["exact small-sample oracle", "metamorphic shift/scale laws", "high-precision reference"]),
    ("inferential_tests_resampling", "library.method_kernels.inferential_tests_resampling", "Test and resampling implementation preserves null/alternative, statistic, tail, exchangeability, multiplicity and random-stream semantics.", ["analytic null cases", "one/two-sided twins", "non-exchangeable permutation refusal", "seeded bootstrap and multiplicity suite"], ["type-I error simulation", "exact test reference", "random-stream replay"]),
    ("regression_glm", "library.method_kernels.regression_glm_estimators", "Regression implementation preserves design/rank, family/link, weighting, regularization, convergence, diagnostics and uncertainty semantics.", ["full-rank analytic model", "rank-deficient design", "separation and ill-conditioning", "family/link/weight twins"], ["coefficient and prediction residual", "rank/convergence oracle", "diagnostic and interval coverage"]),
    ("survival_event_history", "library.method_kernels.survival_event_history_estimators", "Survival implementation preserves origin, event/censoring/competing-risk, risk-set, tie and time-scale semantics.", ["right-censored reference data", "left truncation", "tied events", "all-censored and zero-risk twins"], ["risk-set oracle", "survival monotonicity", "reference hazard/interval comparison"]),
    ("probabilistic_inference", "library.method_kernels.probabilistic_inference", "Probabilistic inference preserves model density, conditioning, transformations, random streams, convergence diagnostics and posterior claim boundaries.", ["analytic conjugate models", "divergent/poor-mixing cases", "reparameterization twin", "posterior-predictive fixtures"], ["posterior moment reference", "sampler diagnostic oracle", "seed/replay and distributional comparison"]),
    ("causal_method", "library.method_kernels.causal_methods", "Causal workflow refuses non-identification and preserves cross-fitting, overlap and sensitivity semantics.", ["identified and non-identified DAGs", "positivity violation", "post-treatment leakage", "placebo and sensitivity cases"], ["identification oracle", "leakage oracle", "reference estimate intervals"]),
    ("causal_identification", "library.method_kernels.causal_graph_identification", "Causal identification returns the same estimand expression or refusal under exact graph, intervention and assumption semantics.", ["back-door/front-door DAGs", "non-identified graph", "latent-confounding twin", "post-treatment adjustment counterexample"], ["symbolic identification oracle", "d-separation checks", "adjustment-set comparison"]),
    ("causal_estimation", "library.method_kernels.causal_effect_estimators", "Effect estimation preserves estimand, nuisance split/cross-fitting, overlap, weighting, uncertainty and failure semantics.", ["known-effect simulations", "positivity failure", "nuisance leakage twin", "heterogeneous-effect slices"], ["bias/coverage oracle", "overlap/refusal oracle", "cross-provider interval comparison"]),
    ("causal_refutation", "library.method_kernels.causal_refutation_sensitivity", "Refutation and sensitivity preserve perturbation, placebo, unobserved-confounding and robustness-envelope meanings without promoting robustness to proof.", ["placebo treatment", "random common cause", "data subset", "parameterized unobserved confounding"], ["perturbation identity oracle", "expected-null behavior", "monotone sensitivity comparison"]),
    ("forecasting", "library.method_kernels.forecasting_methods", "Forecasting implementation is origin/horizon safe and reports distributional and reconciliation truth.", ["seasonal baseline corpus", "known future leakage twin", "hierarchical coherence fixture", "revision/as-of fixture"], ["rolling-origin oracle", "coherence residual", "baseline skill comparison"]),
    ("time_series_semantics", "library.method_kernels.time_series_semantics", "Time-series contracts preserve frequency/index, event versus availability time, revision/as-of identity, origin, horizon and temporal-split safety.", ["regular/irregular indexes", "duplicate and missing periods", "revision vintages", "future-availability leakage twin"], ["index/frequency oracle", "information-cut oracle", "temporal-split validation"]),
    ("forecast_estimators", "library.method_kernels.forecast_estimators", "Forecaster implementation preserves fit/update state, origin/horizon, exogenous availability, distributional output and convergence semantics.", ["seasonal analytic series", "short-history refusal", "exogenous leakage twin", "point/quantile/distribution outputs"], ["forecast index oracle", "baseline residual comparison", "distributional sanity laws"]),
    ("forecast_evaluation", "library.method_kernels.forecast_evaluation", "Forecast evaluation joins exact origins and outcomes, uses declared scoring laws, preserves rolling-origin independence and reports calibration uncertainty.", ["rolling-origin corpus", "revised actuals", "scale-zero metric twin", "probability-integral-transform fixture"], ["cut/join oracle", "score reference", "calibration and coverage oracle"]),
    ("forecast_reconciliation", "library.method_kernels.forecast_reconciliation", "Forecast reconciliation preserves hierarchy/summing constraints, base-forecast identity, covariance assumptions and coherence residuals.", ["two-level hierarchy", "incoherent base forecasts", "singular covariance", "nonnegative constraint case"], ["coherence oracle", "base/reconciled identity trace", "reference reconciliation residual"]),
    ("anomaly_baseline", "library.method_kernels.anomaly_baseline", "Baseline implementation preserves reference window, update mode, regime assumptions, fit data identity and invalidation semantics.", ["stationary baseline", "seasonal baseline", "regime-shift twin", "contaminated reference window"], ["baseline artifact identity", "update/replay oracle", "regime diagnostic"]),
    ("anomaly_detection", "library.method_kernels.anomaly_detectors", "Detector preserves score direction/range, threshold calibration, batch/stream update, error profile and finding partiality.", ["known outliers", "novelty/outlier mode twin", "threshold boundary cases", "online chunking equivalence"], ["score-order oracle", "false-positive/negative profile", "batch/stream comparison"]),
    ("change_point_detection", "library.method_kernels.change_point_detectors", "Change detector preserves ordering, update state, alarm/reset semantics, detection delay and false-alarm contract.", ["mean/variance change", "no-change stream", "gradual drift", "chunk-boundary and reset twins"], ["change-location tolerance", "false-alarm/delay oracle", "state replay"]),
    ("analytical_finding", "library.method_kernels.analytical_finding_contract", "Finding construction preserves subject/window, detector and threshold editions, evidence, uncertainty and non-authoritative adjudication handoff.", ["same score/different threshold twin", "expired baseline", "missing evidence window", "finding-to-incident escalation attempt"], ["identity/provenance oracle", "scope/expiry oracle", "authority refusal"]),
    ("process", "library.method_kernels.process_methods", "Process implementation preserves event/object identities and declared discovery/conformance semantics.", ["XES single-case log", "OCEL multi-object log", "flattening distortion twin", "known model/log alignment"], ["format conformance", "fitness/precision oracle", "alignment cost reference"]),
    ("process_event_projection", "library.method_kernels.process_event_projection", "Event/object projection preserves source identities, qualified relations, multiplicity, attribute histories, clocks and explicit loss across OCED/OCEL views.", ["OCEL 2.0 multi-object log", "OCED identity and qualifier fixtures", "shared-object multiplicity twin", "attribute-history and clock-conflict cases"], ["OCEL profile conformance", "identity/multiplicity oracle", "round-trip and loss receipt"]),
    ("process_case_projection", "library.method_kernels.process_case_projection", "Case projection declares its leading-object and execution-boundary policy and reports event duplication, omission and shared-object loss.", ["one-to-many leading-object cases", "shared-event duplication twin", "nested execution boundaries", "case-less object graph"], ["projection cardinality oracle", "source-attribution oracle", "declared-loss comparison"]),
    ("process_state_aware_projection", "library.method_kernels.process_state_aware_projection", "State-aware projection derives object state from an exact state definition and emits generated state-transition events without confusing them with source events.", ["object attribute histories", "simultaneous state-change twin", "missing-state input", "coalesced versus uncoalesced State-Aware OCEL"], ["state-function oracle", "generated-event provenance oracle", "temporal boundary comparison"]),
    ("process_temporal_graph_projection", "library.method_kernels.process_temporal_graph_projection", "Temporal EKG projection preserves entity identity, snapshot validity, temporal succession and declared OCEL-to-graph information loss.", ["OCEL entity history", "same-time snapshot twin", "relationship qualifier fixture", "directly-follows pruning case"], ["snapshot identity oracle", "temporal succession oracle", "graph transform loss receipt"]),
    ("process_discovery", "library.method_kernels.process_discovery_methods", "Process discovery returns a scoped model hypothesis with exact algorithm, noise, completeness and evaluation semantics.", ["known block-structured log", "noise and incompleteness twins", "object-centric projection variants", "empty and degenerate logs"], ["language/behavior comparison", "fitness/precision evaluation", "determinism and budget replay"]),
    ("process_conformance", "library.method_kernels.process_conformance_methods", "Conformance preserves model/log semantics, move/cost policy, partiality and work-budget behavior.", ["known optimal alignment", "move-cost counterexamples", "token-replay mismatch", "alignment timeout with incumbent"], ["alignment-cost reference", "fitness/precision oracle", "partial-result and resource receipt"]),
    ("process_performance", "library.method_kernels.process_performance_methods", "Process performance analysis preserves event/object time, concurrency, queue/service distinctions and uncertainty without promoting a bottleneck signal to root cause.", ["queue/service decomposition log", "concurrent object interactions", "censored duration case", "dynamic bottleneck cascade"], ["time decomposition oracle", "aggregation/multiplicity oracle", "uncertainty and causality refusal"]),
    ("data_quality", "library.method_kernels.data_quality_methods", "Quality checks report exact evaluated scope, measurement, result state and failing evidence.", ["clean dataset", "one-defect-per-rule mutants", "sampled versus full-scan twin", "source-target reconciliation"], ["mutation score", "scope receipt oracle", "reference mismatch set"]),
    ("graph", "library.method_kernels.graph_methods", "Graph algorithms preserve directedness, multiplicity, weight algebra, disconnected and negative-edge semantics.", ["directed/undirected twins", "multi-edge/self-loop graphs", "negative edge/cycle graphs", "small exact graphs"], ["graph invariant oracle", "reference algorithm", "semiring law tests"]),
    ("graph_semantics", "library.method_kernels.graph_semantics", "Graph representation preserves vertex/edge identity, direction, multiplicity, loops, weight algebra, properties and temporal-cut semantics.", ["directed/undirected twins", "simple/multigraph/self-loop cases", "typed property and missing-value cases", "temporal graph cuts"], ["graph schema oracle", "identity/multiplicity oracle", "view/cut round trip"]),
    ("graph_traversal_paths", "library.method_kernels.graph_traversal_path_methods", "Traversal/path implementation preserves reachability, direction, weight, negative-edge/cycle, path reconstruction, ordering and resource semantics.", ["small exact graphs", "disconnected graph", "negative edge and negative cycle", "equal-cost path ordering twin"], ["reference BFS/shortest path", "path cost/reconstruction oracle", "resource/cancellation receipt"]),
    ("graph_centrality", "library.method_kernels.graph_centrality_methods", "Centrality implementation preserves exact measure definition, normalization, direction/weight interpretation, convergence and undefined-node behavior.", ["star/path/cycle graphs", "weighted/directed twins", "disconnected graph", "convergence limit case"], ["analytic small-graph values", "normalization law", "residual/convergence oracle"]),
    ("graph_community", "library.method_kernels.graph_community_methods", "Community implementation preserves objective, resolution, random stream, overlap/hierarchy posture and partition evaluation semantics.", ["disconnected cliques", "resolution-limit graph", "seed replay", "overlapping-community refusal"], ["partition validity", "objective/modularity reference", "randomness and stability receipt"]),
    ("graph_semiring_kernels", "library.method_kernels.graph_semiring_kernel_facade", "Graph semiring kernels preserve domains, identities, annihilators, masks, transpose, sparsity/layout and deterministic/resource guarantees on an exact target.", ["built-in and user semirings", "structural/valued masks", "transpose and alias cases", "sparse empty/dense boundary cases"], ["semiring algebra laws", "GraphBLAS reference comparison", "layout/resource/determinism receipt"]),
    ("spatial", "library.method_kernels.spatial_methods", "Spatial operations preserve CRS, axis, topology, dimensionality and accuracy semantics.", ["OGC geometry fixtures", "invalid topology cases", "axis-order twin", "round-trip CRS cases"], ["OGC conformance", "topology oracle", "transform accuracy bound"]),
    ("spatial_reference", "library.method_kernels.spatial_reference_semantics", "Spatial references preserve CRS edition, datum, axis order, units, coordinate epoch, spatial support and accuracy envelope.", ["axis-order twins", "dynamic/static datum cases", "unknown CRS", "same coordinates/different CRS"], ["CRS identity oracle", "unit/axis oracle", "support/accuracy comparison"]),
    ("coordinate_transform", "library.method_kernels.coordinate_transform_methods", "Coordinate transformation preserves source/target CRS, selected operation/grid resources, dimensionality, epoch and declared accuracy.", ["known control points", "grid-present/grid-missing twins", "round-trip cases", "outside-area-of-use inputs"], ["control-point residual", "pipeline identity receipt", "area/accuracy refusal"]),
    ("vector_geometry_topology", "library.method_kernels.vector_geometry_topology", "Vector geometry implementation preserves topology model, dimension, boundary, validity, precision and predicate/overlay semantics.", ["OGC geometry corpus", "invalid rings and self-intersections", "boundary-touch twins", "precision-grid overlay"], ["OGC predicate oracle", "topology validity", "overlay area/boundary residual"]),
    ("raster_grid", "library.method_kernels.raster_grid_methods", "Raster/grid implementation preserves grid geometry, CRS, band/dtype, nodata/mask, resampling and support semantics.", ["aligned/misaligned grids", "nodata versus zero twin", "categorical/continuous resampling", "edge and partial-pixel cases"], ["grid geometry oracle", "pixel/nodata reference", "resampling conservation/error bound"]),
    ("spatial_statistics", "library.method_kernels.spatial_statistics_methods", "Spatial statistics preserve observation support, weights construction, neighborhood, dependence, estimator assumptions, uncertainty and evaluation semantics.", ["known lattice patterns", "island observations", "row-standardization twins", "spatial leakage split"], ["weights and neighborhood oracle", "reference autocorrelation/regression", "uncertainty/leakage oracle"]),
    ("text_search", "library.method_kernels.search_methods", "Text/search implementation preserves Unicode analyzer and index/query/ranking compatibility.", ["Unicode normalization corpus", "segmentation languages", "index/search analyzer mismatch twin", "ranked relevance judgments"], ["Unicode conformance", "golden token stream", "score explanation", "retrieval metric"]),
    ("document_container", "library.method_kernels.document_container_semantics", "Document-container semantics preserve exact media/profile edition, package parts/relationships, attachments, protection state and bounded recursion.", ["PDF/OOXML/ODF/HTML/MIME fixtures", "nested attachments", "encrypted/unsupported profile", "archive expansion limit"], ["format/profile oracle", "part/relationship graph", "resource/protection refusal"]),
    ("document_content_graph", "library.method_kernels.document_content_graph", "Content graph preserves document/page/element identity, coordinate transforms, source text, structural roles and uncertain reading order.", ["rotated/cropped pages", "tagged and untagged PDFs", "multi-column layout", "glyph-to-Unicode loss cases"], ["coordinate round trip", "source-span provenance", "reading-order partial-order oracle"]),
    ("document_parser", "library.method_kernels.document_parser_adapters", "Parser adapter preserves container/profile semantics, bounded recursion, warnings, cancellation and exact provider/version receipts.", ["valid/corrupt/truncated documents", "nested packages", "password-protected input", "decompression/page-count bomb"], ["reference parser differential", "parse-tree invariants", "resource/cancellation receipt"]),
    ("document_layout", "library.method_kernels.document_layout_methods", "Layout extraction preserves coordinates, line/block/region membership, role, repeated-region and reading-order uncertainty.", ["single/multi-column pages", "headers/footers", "sidebars/footnotes", "overlapping positioned text"], ["region overlap/coverage", "reading-order graph comparison", "layout mutation score"]),
    ("document_ocr", "library.method_kernels.document_ocr_methods", "OCR preserves page image identity, language/script/profile, positioned recognition, confidence, alternatives and failure/unsupported states.", ["multilingual/script corpus", "rotation/skew", "low contrast/noise", "blank and adversarial pages"], ["character/word error rate", "bbox/reading-order residual", "confidence calibration and runtime receipt"]),
    ("document_table", "library.method_kernels.document_table_extraction", "Table extraction preserves detection, grid, rows/columns, spanning cells, headers, coordinates, content provenance and continuation uncertainty.", ["ruled/unruled tables", "row/column spans", "empty cells", "multi-page continuation"], ["GriTS/structure reference", "cell geometry/content alignment", "canonical table graph comparison"]),
    ("document_form", "library.method_kernels.document_form_extraction", "Form extraction preserves native field tree, widget, type, name, value, appearance, coordinates and signature/XFA unsupported states.", ["AcroForm controls", "nested field names", "appearance/value mismatch", "XFA and scanned form twins"], ["native field-tree oracle", "widget/page geometry", "unsupported/inferred distinction"]),
    ("document_provenance", "library.method_kernels.document_provenance_loss", "Every extracted element preserves source locator, byte/part/page/region, extractor edition, confidence, transformation and explicit information loss.", ["same text from native/OCR paths", "embedded-document lineage", "coordinate transform", "provider disagreement"], ["element identity/digest", "lineage closure", "loss/confidence no-strengthening law"]),
    ("document_classification", "library.method_kernels.document_classification_methods", "Document classification preserves taxonomy edition, single/multi-label semantics, score calibration, thresholds, hierarchy and abstention.", ["known label corpus", "multi-label and hierarchical cases", "out-of-taxonomy documents", "class imbalance and threshold boundaries"], ["label/metric reference", "calibration curve", "abstention/unknown-label oracle"]),
    ("document_information_extraction", "library.method_kernels.document_information_extraction", "Information extraction preserves schema, span/field/relation type, cardinality, normalization, source evidence, confidence, alternatives and abstention.", ["exact/overlapping spans", "repeated fields", "missing/ambiguous values", "cross-page relation cases"], ["schema/type oracle", "source-span alignment", "cardinality/abstention oracle"]),
    ("document_extraction_evaluation", "library.method_kernels.document_extraction_evaluation", "Evaluation preserves gold-corpus edition, matching rules, task scope, aggregation, calibration, abstention and error slices.", ["classification, span, relation and table gold cases", "exact versus overlap twin", "empty prediction/gold", "provider disagreement"], ["independent metric implementation", "matching-policy differential", "mutation and error-slice coverage"]),
    ("signal", "library.method_kernels.signal_methods", "Signal transforms preserve sample/frequency coordinates, normalization, phase and boundary semantics.", ["impulse", "single and multi-tone signals", "non-power-of-two lengths", "streaming chunk-boundary twins"], ["round-trip residual", "spectral peak oracle", "energy/scaling law"]),
    ("image", "library.method_kernels.image_methods", "Image operations preserve geometry, connectivity, dtype, boundary and interpolation semantics.", ["binary morphology phantoms", "segmentation phantoms", "known rigid transform", "dtype/range twins"], ["pixel-exact fixture", "geometry residual", "segmentation metric"]),
    ("numerical_kernels", "library.method_kernels.numerical_kernel_facade", "Kernel offer satisfies exact signatures, numeric residuals, determinism, resource and cancellation requirements on one target.", ["well-conditioned fixtures", "ill-conditioned fixtures", "NaN/Inf/overflow", "strided/aliased/sparse layouts", "cancellation and memory limits"], ["reference residual", "metamorphic law", "determinism replay", "resource envelope"]),
    ("columnar_kernels", "library.method_kernels.columnar_kernel_facade", "Columnar kernels preserve Arrow types, validity, chunking and streaming semantics.", ["all supported Arrow types", "null and chunk-boundary twins", "dictionary/run-end inputs", "bounded streaming input"], ["Arrow integration fixtures", "batch/stream equivalence", "memory bound"]),
    ("codec", "library.method_kernels.codec_adapter", "Codec/encoding offer round-trips valid input and safely rejects corrupt, truncated or resource-hostile data.", ["empty/small/large/compressible/incompressible corpus", "dictionary mismatch", "truncated/corrupt frames", "decompression-bomb budget"], ["byte-exact round trip", "format conformance", "checksum/corruption oracle", "resource limit"]),
    ("rust_boundary", "library.method_kernels.numerical_kernel_facade", "Rust/native boundary exposes ownership, thread safety, panic/error, cancellation, feature and dependency truth.", ["safe Rust backend", "FFI backend", "feature-minimal build", "thread and cancellation stress"], ["Miri/sanitizer where applicable", "API conformance", "dependency and license audit"]),
]


QUALIFICATION_RECEIPTS = [
    {
        "receipt_id": f"receipt.method_kernel.{slug}",
        "edition": EDITION,
        "record_kind": "qualification_profile",
        "status": "template_not_executed",
        "subject_ref": subject,
        "claim": claim,
        "scope": ["exact provider version", "exact build/features", "exact target/hardware", "exact configuration and operation set"],
        "environment": {},
        "configuration": {},
        "fixtures": fixtures,
        "oracles": oracles,
        "results": [],
        "evidence_refs": [],
        "validity": {"from": None, "until": None},
        "invalidation_triggers": ["provider version/build change", "target/hardware change", "configuration change", "fixture/oracle edition change", "dependency or security change"],
        "limitations": ["This is an unexecuted qualification profile and proves no provider capability.", "Passing one profile would prove only its exact claim and scope."],
    }
    for slug, subject, claim, fixtures, oracles in QUALIFICATION_SPECS
]


ARTIFACT_RESULT_SPECS = [
    ("study_design", "study_design", "definition", "A frozen observation, sampling or assignment design whose authority and causal/statistical scope are explicit.", ["contract.method_kernel.analysis_design"], ["population", "units", "assignment_or_sampling", "time_window", "analysis_protocol"], ["study_design", "population_sampling", "identification"], ["nist_handbook", "consort"], "contract_portable"),
    ("estimand", "estimand", "definition", "A versioned target quantity with population, treatment/exposure, outcome, time, contrast, intercurrent-event and unit semantics.", ["contract.method_kernel.analysis_design", "contract.method_kernel.formula_algebra"], ["target_quantity", "population", "contrast", "time_semantics", "units"], ["estimand", "identification"], ["fda_adaptive", "dowhy_paper"], "semantic_only"),
    ("resolved_method_plan", "resolved_method_plan", "compiled_plan", "A compiler-resolved method/estimator/algorithm/kernel graph with every semantic and runtime decision digest-bound.", ["contract.method_kernel.method_contracts", "contract.method_kernel.artifact_envelope"], ["study_design_ref", "estimand_ref", "method_family_ref", "implementation_graph", "resolved_decisions", "evidence_gates"], ["study_design", "estimand", "kernel_backend", "resource_budget"], ["nist_handbook", "array_api"], "contract_portable"),
    ("fitted_model", "fitted_model", "fitted_state", "Learned parameters and diagnostics bound to the method, training data snapshot, provider build, configuration and random stream.", ["contract.method_kernel.statistical_estimators", "contract.method_kernel.artifact_envelope"], ["model_contract_ref", "parameter_state", "fit_diagnostics", "training_data_digest", "feature_schema"], ["precision", "random_stream", "artifact_persistence"], ["stan_reference", "sklearn_evaluation"], "provider_bound"),
    ("fitted_transform", "fitted_transform", "fitted_state", "Learned preprocessing state such as categories, scaling, imputation or projections, kept distinct from an unfitted transform definition.", ["contract.method_kernel.artifact_envelope"], ["transform_contract_ref", "learned_state", "input_schema", "output_schema", "fit_data_digest"], ["missingness", "precision", "artifact_persistence"], ["sklearn_evaluation", "arrow_columnar"], "provider_bound"),
    ("forecast", "forecast", "execution_result", "A point, interval, quantile or distribution forecast indexed by origin, target time, horizon, scenario and revision/as-of truth.", ["contract.method_kernel.forecasting_methods", "contract.method_kernel.result_algebra"], ["origin", "target_time", "horizon", "distribution_or_summary", "revision_identity"], ["forecast_horizon", "forecast_reconciliation", "uncertainty"], ["statsmodels_tsa", "forecasting_book"], "contract_portable"),
    ("simulation_run", "simulation_run", "execution_result", "A bounded simulation result with model edition, scenario, replication, seed/substream, warm-up and termination evidence.", ["contract.method_kernel.operations_research_bridge", "contract.method_kernel.result_algebra"], ["simulation_model_ref", "scenario", "replications", "random_streams", "outputs", "termination_receipt"], ["random_stream", "resource_budget", "cancellation"], ["nist_handbook", "numpy_rng"], "contract_portable"),
    ("search_index", "search_index", "fitted_state", "A materialized index bound to analyzer, Unicode, field schema, codec and ranking compatibility contracts.", ["contract.method_kernel.search_methods", "contract.method_kernel.artifact_envelope"], ["document_schema", "analyzer_digest", "segment_manifest", "codec_identity", "generation"], ["text_locale", "retrieval_ranking", "artifact_persistence"], ["lucene_core", "tantivy"], "provider_bound"),
    ("process_model", "process_model", "fitted_state", "A discovered or authored process model whose event/object perspective, discovery configuration and conformance semantics remain attached.", ["contract.method_kernel.process_methods", "contract.method_kernel.artifact_envelope"], ["model_notation", "model_payload", "event_object_perspective", "discovery_configuration", "source_log_digest"], ["process_perspective", "conformance_cost", "artifact_persistence"], ["pm4py", "ocel20", "xes"], "representation_portable"),
    ("analytical_result", "analytical_result", "execution_result", "A total result envelope that separates valid values from refusal, partiality, convergence, numerical and resource states.", ["contract.method_kernel.result_algebra"], ["result_state", "typed_value_or_failure", "method_plan_digest", "data_snapshot_digest", "numeric_receipt"], ["precision", "determinism", "resource_budget"], ["nist_handbook", "openformula"], "contract_portable"),
    ("evaluation_receipt", "evaluation_receipt", "evidence", "Evaluation evidence bound to the exact artifact, holdout/backtest protocol, metric definition, slices and uncertainty.", ["contract.method_kernel.provider_qualification", "contract.method_kernel.result_algebra"], ["subject_artifact_digest", "evaluation_design", "evaluation_data_digest", "metric_definitions", "slice_results", "uncertainty"], ["evaluation_split", "evaluation_metric", "uncertainty"], ["sklearn_evaluation", "forecasting_book"], "contract_portable"),
    ("evidence_bundle", "evidence_bundle", "evidence", "An immutable claim-evidence bundle linking source authority, assumptions, decisions, executions, diagnostics and invalidation triggers.", ["contract.method_kernel.artifact_envelope", "contract.method_kernel.provider_qualification"], ["claims", "evidence_edges", "decision_receipts", "execution_receipts", "limitations", "invalidation_triggers"], ["artifact_persistence", "determinism", "cancellation"], ["great_expectations", "deequ", "array_api"], "contract_portable"),
]


def artifact_result_contract(spec):
    slug, kind, phase, definition, producers, payload, decision_slugs, evidence_slugs, portability = spec
    terminal_states = ["valid", "invalid_input", "unsupported", "resource_exhausted", "cancelled", "inconclusive"]
    return {
        "artifact_contract_id": f"artifact_contract.method_kernel.{slug}",
        "edition": EDITION,
        "status": "sourced_candidate",
        "artifact_kind": kind,
        "state_phase": phase,
        "definition": definition,
        "producer_contracts": producers,
        "required_identity_fields": ["artifact_id", "contract_edition", "content_digest", "producer_identity", "created_at"],
        "required_payload_fields": payload,
        "provenance_requirements": ["input and upstream artifact digests", "resolved configuration digest", "provider/build/target identity where executable", "authority and evidence references"],
        "result_states": terminal_states,
        "validation_rules": ["Schema and semantic edition validate before use.", "Every referenced digest and identity is resolvable.", "A non-valid state cannot carry an unqualified success value."],
        "invalidation_triggers": ["semantic contract change", "input or upstream artifact change", "provider/build/target change", "configuration or random-stream change", "evidence expiry or revocation"],
        "replay_contract": ["Replay uses the exact method plan, data snapshot, provider build, target, configuration and random-stream identities.", "If exact replay is unsupported, the artifact declares the weaker reproducibility relation and evidence."],
        "portability": {"level": portability, "conditions": ["Compatible semantic edition and exact required types are available.", "Any representation/provider migration is explicit and receipt-backed."]},
        "decision_refs": [f"decision.method_kernels.{decision}" for decision in decision_slugs],
        "evidence_refs": [f"source.method_kernel.{source}" for source in evidence_slugs],
        "gaps": ["Instance serialization, migration and runtime qualification remain open until an exact provider and vertical are bound."],
    }


ARTIFACT_RESULT_CONTRACTS = [artifact_result_contract(spec) for spec in ARTIFACT_RESULT_SPECS]


INNOVATION_SPECS = [
    ("array_api_interchange", "Array API standardization and conformance", 2021, "standard_and_conformance", "A common array API began making method code less coupled to one array provider and created an executable conformance surface.", ["array_api"], "Common syntax does not prove identical floating-point, performance, device or determinism behavior."),
    ("graphblas_2", "GraphBLAS C API 2.x", 2021, "standard_release", "GraphBLAS 2.x matured semiring-based graph kernels as a provider-neutral primitive interface.", ["graphblas_c"], "API conformance does not qualify higher-level graph algorithms or target performance."),
    ("lagraph_layer", "LAGraph separation above GraphBLAS", 2021, "primary_research_and_reference_implementation", "LAGraph made the boundary between low-level GraphBLAS kernels and user-facing graph algorithms explicit.", ["lagraph_paper", "graphblas_c"], "The algorithm library remains only one graph-method provider."),
    ("doubleml_package", "Reusable DoubleML method workflow", 2021, "maintained_research_software", "DoubleML packaged orthogonal scores, cross-fitting and causal inference diagnostics behind reusable estimator interfaces.", ["doubleml_docs"], "The package does not make causal assumptions true and may use statistical-learning nuisance models."),
    ("arrow_acero", "Arrow Acero streaming execution over compute kernels", 2022, "official_implementation_milestone", "Acero exposed streaming physical plans above Arrow's typed compute-kernel registry.", ["arrow_compute", "arrow_acero"], "Its API and provider status must be version-qualified; it does not own analytical semantics."),
    ("ocel20", "OCEL 2.0 object-centric event semantics", 2023, "standard_release", "OCEL 2.0 standardized events linked to multiple typed objects, qualified relations and changing object attributes.", ["ocel20"], "Exchange semantics do not prove event extraction correctness or process-method validity."),
    ("graphblas_21", "GraphBLAS 2.1 conformance surface", 2023, "standard_release", "GraphBLAS 2.1 refined the standard primitive surface and reference implementation alignment.", ["graphblas_c", "suitesparse_graphblas"], "A standard edition still requires per-provider and per-target execution evidence."),
    ("semantic_metric_graph", "Open semantic-graph metric specifications", 2023, "productization_and_open_spec_direction", "MetricFlow-style semantic graphs moved entity, dimension, time and metric definitions outside individual BI tools.", ["dbt_semantic", "dbt_metrics"], "Vendor/product semantics remain incomplete as a universal formula and grain standard."),
    ("scipy_array_backends", "Scientific functions adopting array-backend dispatch", 2024, "official_implementation_direction", "Scientific Python increasingly exposed array-backend dispatch so method code can target multiple CPU/GPU array implementations.", ["scipy_guide", "array_api"], "Coverage varies by function/device and must be probed rather than inferred globally."),
    ("rust_faer", "Rust-native high-performance linear algebra maturation", 2024, "maintained_implementation_milestone", "faer expanded a Rust-native dense/sparse algebra option and a removable alternative to native BLAS/LAPACK FFI.", ["faer"], "The current docs establish surface, not universal numerical/performance superiority."),
    ("parquet_byte_stream_split", "Byte-stream-split analytical encoding adoption", 2024, "standardized_physical_encoding", "Parquet standardized byte-stream split for typed numeric values to improve downstream compression behavior.", ["parquet_encoding"], "Encoding alone does not reduce size and benefit depends on data and codec."),
    ("apache_ossie", "Apache Ossie open semantic schema", 2025, "open_specification_candidate", "Ossie exposed a machine-readable semantic schema for entities, dimensions, measures and metrics.", ["apache_ossie"], "The schema is evolving and does not yet constitute universal semantic-metric conformance."),
    ("parquet_variant", "Parquet analytical representation extensions", 2025, "standard_evolution", "Parquet's evolving type/encoding surface showed the need to bind logical meaning separately from physical shredding and codecs.", ["parquet_encoding"], "This record captures the architectural direction, not complete Variant or geospatial conformance."),
    ("unicode_search_modularity", "Versioned analyzer/ranking modularity in modern search libraries", 2025, "implementation_evolution", "Modern Lucene/Tantivy surfaces increasingly separate analyzer, index codec, ranking and collectors as replaceable decisions.", ["lucene_core", "lucene_similarity", "tantivy"], "These are implementation capabilities, not a neutral search-product standard."),
    ("ocel21_formats", "Scalable object-centric event-log serializations", 2026, "standard_evolution", "OCEL's current specification direction adds compact CSV and bundled Parquet serializations while preserving object-centric semantics.", ["ocel20", "parquet_encoding"], "Serialization scalability does not resolve event extraction, identity or conformance-method correctness."),
    ("array_api_2025", "Array API 2025.12 verification and benchmark surface", 2026, "standard_release", "The 2025.12 Array API publishes specification, verification and benchmark surfaces for portable array implementations.", ["array_api"], "Benchmarks and tests remain scoped; identical API does not guarantee bitwise equivalence."),
]


INNOVATIONS = [
    {
        "innovation_id": f"innovation.method_kernel.{slug}",
        "edition": EDITION,
        "name": name,
        "year": year,
        "evidence_posture": posture,
        "non_llm": True,
        "problem_and_innovation": description,
        "evidence_refs": [f"source.method_kernel.{source}" for source in evidence_slugs],
        "limits": [limits, "This may be a standardization, implementation or productization milestone rather than invention of the underlying mathematics."],
        "compiler_implications": ["Bind exact editions and capabilities rather than branching on product names.", "Retain provider and target qualification as a separate gate."],
    }
    for slug, name, year, posture, description, evidence_slugs, limits in INNOVATION_SPECS
]


GAPS = {
    "atlas_id": "san.domain-atlas.method-kernel.gaps",
    "edition": EDITION,
    "completion_claim": False,
    "open_gaps": [
        {"gap_id": "enumeration_open_world", "severity": "structural", "description": "The finite family list is a saturation checkpoint, not proof that every analytical method exists here.", "resolution": "Recurring literature/standard/vertical audits add governed records or explicit extension gaps."},
        {"gap_id": "theorem_preconditions", "severity": "blocking_for_claims", "description": "Most candidate methods still need theorem-level applicability and counterexample records.", "resolution": "Attach machine-readable preconditions, guarantees and falsification fixtures per adjudicated method."},
        {"gap_id": "exact_provider_versions", "severity": "blocking_for_binding", "description": "Provider seeds cite maintained docs but do not pin exact versions, features, builds and transitive dependencies.", "resolution": "Ingest signed provider manifests and generate exact offers."},
        {"gap_id": "executed_receipts", "severity": "blocking_for_binding", "description": "Qualification records are deliberately unexecuted templates.", "resolution": "Execute profiles on exact targets and persist immutable evidence receipts."},
        {"gap_id": "cross_provider_numerics", "severity": "high", "description": "Floating-point tolerance, order, mixed precision and parallel nondeterminism are not normalized across providers.", "resolution": "Define operation-specific numeric equivalence relations and qualify multiple implementations."},
        {"gap_id": "artifact_interchange", "severity": "high", "description": "No universal fitted-model/index/plan artifact format covers all method families.", "resolution": "Keep artifacts provider-bound unless an explicit portable semantic/serialization contract is proved."},
        {"gap_id": "rust_coverage", "severity": "high", "description": "Rust-native coverage is strong for arrays/algebra/search but incomplete for broad statistics, causal, process, spatial and image methods.", "resolution": "Use pure Rust contributions where qualified and narrow removable adapters to external runtimes elsewhere."},
        {"gap_id": "ffi_license_supply_chain", "severity": "high", "description": "ABI, allocator, panic, thread, license and supply-chain implications of native/provider libraries require separate qualification.", "resolution": "Bind feature/dependency/license manifests and run FFI safety profiles."},
        {"gap_id": "accelerator_targets", "severity": "high", "description": "GPU/accelerator coverage, device transfer, cancellation and reproducibility are sparsely evidenced.", "resolution": "Add target-specific offers and receipts without changing semantic method records."},
        {"gap_id": "codec_adversarial", "severity": "high", "description": "Compression ratios and speed are data-dependent; corrupt input and decompression expansion create hazards.", "resolution": "Qualify codecs on representative and adversarial corpora with hard output/memory/work limits."},
        {"gap_id": "or_crosswalk", "severity": "medium", "description": "OR is referenced, not copied; cross-references must be checked against every edition of the dedicated OR corpus.", "resolution": "Add an edition-aware cross-universe relation graph and validator."},
        {"gap_id": "vertical_method_packs", "severity": "high", "description": "Specialized econometric, epidemiological, psychometric, actuarial, chemometric, bioinformatic and engineering methods need vertical packs.", "resolution": "Extend through the closed metamodel; promote a method horizontally only after unrelated-domain evidence."},
        {"gap_id": "study_to_method_selection", "severity": "blocking_for_compiler", "description": "The compiler lacks an executable rule system that derives admissible methods from study/estimand/assumption contracts.", "resolution": "Encode admissibility as requirements, proofs and explicit ambiguity gaps—never a heuristic name lookup."},
        {"gap_id": "operation_crosswalk", "severity": "blocking_for_compiler", "description": "Method algorithms and kernels are not yet fully cross-referenced to the global typed-operation universe.", "resolution": "Adjudicate ownership and add exact operation/type/shape references."},
        {"gap_id": "two_verticals", "severity": "blocking_for_product_boundary", "description": "No method/library boundary here has yet passed two unrelated vertical applications.", "resolution": "Bind and validate against unrelated cases before productization."},
    ],
}


def main() -> None:
    write_jsonl("sources.jsonl", SOURCES)
    write_jsonl("decision-points.jsonl", DECISIONS)
    write_jsonl("method-families.jsonl", METHOD_FAMILIES)
    write_jsonl("implementation-records.jsonl", IMPLEMENTATION_RECORDS)
    write_jsonl("library-boundaries.jsonl", LIBRARIES)
    write_jsonl("compiler-requirements-offers.jsonl", COMPILER_RECORDS)
    write_jsonl("qualification-receipts.jsonl", QUALIFICATION_RECEIPTS)
    write_jsonl("artifact-result-contracts.jsonl", ARTIFACT_RESULT_CONTRACTS)
    write_jsonl("innovations.jsonl", INNOVATIONS)
    (ROOT / "gaps.json").write_text(json.dumps(GAPS, indent=2, sort_keys=True) + "\n")
    write_manifest()
    print(
        "WROTE method-kernel corpus: "
        f"{len(SOURCES)} sources, {len(METHOD_FAMILIES)} method families, "
        f"{len(IMPLEMENTATION_RECORDS)} implementation records, {len(LIBRARIES)} library boundaries, "
        f"{len(DECISIONS)} decisions, {len(OFFERS)} provider offers, "
        f"{len(QUALIFICATION_RECEIPTS)} qualification profiles, {len(ARTIFACT_RESULT_CONTRACTS)} artifact/result contracts, "
        f"{len(INNOVATIONS)} innovations"
    )


if __name__ == "__main__":
    main()
