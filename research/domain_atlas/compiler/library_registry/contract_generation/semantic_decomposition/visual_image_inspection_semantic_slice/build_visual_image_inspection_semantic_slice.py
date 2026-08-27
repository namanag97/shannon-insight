#!/usr/bin/env python3
"""Build the evidence-backed visual/image analysis and inspection semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
AS_OF = "2026-08-27"
PRODUCTS = {"product.image_analysis_workbench", "product.visual_inspection_operations"}
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

NEIGHBORS = {
    "library.measurement.observation_result.constructor",
    "library.method_kernels.anomaly_baseline",
    "library.method_kernels.anomaly_detectors",
    "library.method_kernels.artifact_envelope",
    "library.method_kernels.codec_adapter",
    "library.method_kernels.descriptive_statistics",
    "library.method_kernels.inferential_tests_resampling",
    "library.method_kernels.method_contracts",
    "library.method_kernels.provider_qualification",
    "library.method_kernels.raster_grid_methods",
    "library.method_kernels.spatial_reference_semantics",
    "library.method_kernels.statistical_estimators",
    "library.method_kernels.vector_geometry_topology",
    "library.predictive.artifact_manifest",
    "library.predictive.calibration",
    "library.predictive.classification_models",
    "library.predictive.conformal_prediction",
    "library.predictive.image_features",
    "library.predictive.label_contracts",
    "library.predictive.model_lifecycle",
    "library.predictive.monitoring",
    "library.predictive.neural_predictive_models",
    "library.predictive.robustness_evaluation",
    "library.predictive.target_contracts",
    "library.agreement.measurement.evaluator",
    "library.consensus.evaluator",
    "library.consensus.rule.compiler",
    "library.review.adjudication.reducer",
    "library.review.issue.lifecycle",
    "library.pointcloud.3d.evaluator",
    "library.pointcloud.analysis.profile.compiler",
    "library.recipe.edit_history.algebra",
    "library.recipe.replay.evaluator",
    "library.recipe.replay.planner",
    "library.runtime-resource.attempt-state",
    "library.runtime-resource.conformance-oracles",
    "library.runtime-resource.deadline-cancellation",
    "library.runtime-resource.device-runtime-spi",
    "library.csp.decision.action-authorizer",
    "library.csp.decision.compensation",
    "library.csp.decision.decision-conformance",
    "library.csp.decision.decision-contract",
    "library.csp.decision.feedback-loop",
    "library.lpe.provenance-assertion",
    "library.lpe.reproduction-evaluator",
    "library.lpe.runtime-receipt-core",
}

VACANCIES = [
    ("library.analytics_image_analysis.project_definition", "Analysis question, population, unit, purpose and uses require an editioned project identity."),
    ("library.analytics_image_analysis.image_occurrence_admission", "Source occurrence, carrier, decoded field, rendition and admitted input cut require distinct identities and evidence."),
    ("library.analytics_image_analysis.workspace_layer_graph", "Image, label, point, shape, surface, track, vector and measurement layers require typed graph and presentation semantics."),
    ("library.analytics_image_analysis.coordinate_profile_binding", "Axes, units, data/world frames, imported transforms, validity and uncertainty require explicit binding semantics."),
    ("library.analytics_image_analysis.region_object_topology", "ROI, mask, contour, label map, component and analytical object require a carrier-independent topology contract."),
    ("library.analytics_image_analysis.analysis_recipe", "Method graph, ports, parameters, randomness and expected result kinds require compiled recipe identity."),
    ("library.analytics_image_analysis.method_capability_binding", "Method requirements, qualified offers, compatibility and provider substitution require a fail-closed binding contract."),
    ("library.analytics_image_analysis.analysis_run_attempt", "Plan, run, attempt, cancellation, retry, partiality and terminal-state reconciliation require total execution semantics."),
    ("library.analytics_image_analysis.derived_layer_result", "Derived fields and layers require exact sources, derivation receipts, frames, states, uncertainty and limitations."),
    ("library.analytics_image_analysis.object_segmentation_result", "Detection, localization, segmentation, object occurrence, score and abstention require explicit result-grain semantics."),
    ("library.analytics_image_analysis.measurement_feature_result", "Subject, measurand/feature, value, unit, uncertainty, validity and method receipt require one result contract."),
    ("library.analytics_image_analysis.result_comparison_review", "Comparability, metric applicability, differences, issues, judgments and defeaters require append-only review semantics."),
    ("library.analytics_image_analysis.provenance_replay_history", "Edits, causal provenance, replay environment, equivalence and residuals require evidence-bearing history."),
    ("library.analytics_image_analysis.evidence_publication_export", "Project, input, recipe, run, result and limitation manifests require loss-aware authorized publication."),
    ("library.inspection.target-occurrence-binding", "Physical item/area occurrence, trigger, view, capture set and evidence must be bound before evaluation."),
    ("library.inspection.acquisition-synchronization-profile", "Camera, lens, illumination, trigger, motion, multi-view synchronization and timing need a qualified profile."),
    ("library.inspection.reference-golden-profile", "Golden samples, templates, baselines and normality references need edition, population, validity and drift semantics."),
    ("library.inspection.plan-definition", "Purpose, population, characteristic, defect vocabulary import, costs, sampling and authority need an inspection-owned plan."),
    ("library.inspection.recipe-qualification", "Recipe testing, capability envelope, calibration scope, timing, provider portability and release need a qualification lifecycle."),
    ("library.inspection.result-algebra", "Not-inspected, incomplete, unknown, pass, fail, review-required and invalid states need total portable semantics."),
    ("library.inspection.review-disposition", "Method output, finding, reviewer judgment, disposition, waiver and appeal require an append-only authority boundary."),
    ("library.inspection.effect-handoff", "Disposition, action proposal, authorization, attempt and physical receipt need end-to-end non-collapse tests."),
    ("library.inspection.vertical-defect-vocabulary-acl", "Industry defect classes, severities, zones, tolerances and acceptance rules require explicit vertical imports."),
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
    ("opc-machine-vision", "OPC UA for Machine Vision Part 1", "OPC Foundation and VDMA", 2026, "official_specification", "https://reference.opcfoundation.org/specs/OPC-40100-1/full", "Defines machine-vision system state, configuration, recipe and result-management integration concepts.", "It deliberately leaves image acquisition/processing implementation and application-specific result meaning open."),
    ("genicam", "GenICam 2026.07 standards package", "EMVA", 2026, "official_standard_suite", "https://www.emva.org/standards-technology/genicam/genicam-downloads/", "Separates GenApi, GenTL, SFNC, PFNC, GenCP and GenDC device, transport, feature, pixel and data-container contracts.", "Interoperable device access does not prove evidence fitness, calibration validity or inspection correctness."),
    ("emva1288-linear", "EMVA 1288 Release 4.0 Linear", "EMVA", 2021, "official_standard", "https://www.emva.org/wp-content/uploads/EMVA1288Linear_4.0Release.pdf", "Defines measurement and presentation of linear camera/sensor characterization parameters.", "Camera characterization does not specify an application acquisition plan or acceptance decision."),
    ("emva1288-general", "EMVA 1288 Release 4.0 General", "EMVA", 2021, "official_standard", "https://www.emva.org/wp-content/uploads/EMVA1288General_4.0Release.pdf", "Extends objective characterization to broader camera response classes and processed output.", "Characterization evidence remains scoped to the tested device/configuration and method."),
    ("openvx", "OpenVX 1.3.2 Specification and Feature Sets", "Khronos Group", 2026, "official_specification", "https://registry.khronos.org/OpenVX/", "Defines portable image objects, vision kernels, verified graphs, execution and conformance feature sets.", "Kernel/API conformance does not define an inspection product, defect meaning or target performance."),
    ("gige-vision", "GigE Vision Standard", "Association for Advancing Automation", 2026, "official_standard", "https://www.automate.org/vision/vision-standards/gige-vision-standard", "Defines high-performance camera transport and control over Ethernet.", "Transport conformance does not establish pixel semantics, evidence quality or end-to-end timing fitness."),
    ("usb3-vision", "USB3 Vision Standard", "Association for Advancing Automation", 2026, "official_standard", "https://www.automate.org/vision/vision-standards/usb3-vision-standard", "Defines camera interoperability over USB3 transports.", "A compliant transport/device remains an unqualified acquisition source for a particular inspection."),
    ("vim", "JCGM 200:2012 International Vocabulary of Metrology", "BIPM/JCGM", 2012, "normative_guide", "https://www.bipm.org/en/doi/10.59161/jcgm200-2012", "Distinguishes measurand, measurement result, indication, calibration, traceability and uncertainty concepts.", "Metrology vocabulary does not define image algorithms, inspection policy or business authority."),
    ("gum", "JCGM 100:2008 Guide to the Expression of Uncertainty in Measurement", "BIPM/JCGM", 2008, "normative_guide", "https://www.bipm.org/en/doi/10.59161/jcgm100-2008e", "Defines general rules for evaluating and expressing measurement uncertainty.", "Uncertainty evaluation does not by itself establish conformity or acceptance."),
    ("gum1", "JCGM GUM-1:2023 Introduction", "BIPM/JCGM", 2023, "normative_guide", "https://www.bipm.org/documents/20126/2071204/JCGM_GUM-1.pdf", "Clarifies the measurement-model and uncertainty framework.", "A general measurement model needs application-specific calibration and validity evidence."),
    ("jcgm106", "JCGM 106:2012 Role of Measurement Uncertainty in Conformity Assessment", "BIPM/JCGM", 2012, "normative_guide", "https://www.bipm.org/documents/20126/2071204/JCGM_106_2012_E.pdf", "Separates measurement results, uncertainty, tolerance limits, decision rules and conformity decisions.", "A conformity decision is not necessarily a lot disposition or physical effect authorization."),
    ("iso2859", "ISO 2859-1:2026 Sampling Procedures for Inspection by Attributes", "ISO", 2026, "international_standard", "https://www.iso.org/standard/85464.html", "Defines AQL-indexed lot-by-lot attribute sampling schemes and switching rules.", "Sampling plans do not define how an image method detects or classifies a defect."),
    ("iso10360-7", "ISO 10360-7:2011 Imaging Probing Systems", "ISO", 2011, "international_standard", "https://www.iso.org/standard/43904.html", "Defines scoped acceptance and reverification tests for CMM imaging probing systems.", "The scope is discrete-point Cartesian CMM performance, not all machine vision inspection."),
    ("dicom", "DICOM Current Edition", "NEMA/MITA", 2026, "official_standard_suite", "https://www.dicomstandard.org/current/", "Separates information objects, pixel data, encoding, services, conformance and security profiles.", "DICOM conformance does not establish diagnosis, image quality or inspection result truth."),
    ("ome-ngff", "OME-NGFF 0.6 Release Candidate", "Open Microscopy Environment", 2026, "community_specification", "https://ngff.openmicroscopy.org/specifications/dev/index.html", "Defines multidimensional/multiscale images, axes, coordinate systems, transforms and label images over Zarr.", "A release candidate can change and carrier metadata does not establish label correctness."),
    ("icc", "ICC.1:2022 Colour Management", "International Color Consortium", 2022, "official_specification", "https://www.color.org/specification/ICC.1-2022-05.pdf", "Defines color profile architecture, device spaces, profile connection spaces and rendering intents.", "Profile conformance does not prove perceptual equality or inspection invariance."),
    ("tiff", "TIFF Revision 6.0", "Adobe / Library of Congress registry", 1992, "format_specification", "https://www.loc.gov/preservation/digital/formats/fdd/fdd000022.shtml", "Defines a tag-based raster container with multiple encodings and photometric interpretations.", "Container equivalence is not decoded sample, visual, radiometric or semantic equivalence."),
    ("opencv", "OpenCV Image Processing and Calibration Documentation", "OpenCV", 2026, "official_documentation", "https://docs.opencv.org/4.x/d7/da8/tutorial_table_of_content_imgproc.html", "Documents filtering, morphology, contours, transforms, segmentation and calibration implementation surfaces.", "Provider documentation is not provider-neutral semantics or deployment qualification."),
    ("scikit-image", "scikit-image API", "scikit-image project", 2026, "official_documentation", "https://scikit-image.org/docs/stable/api/skimage", "Documents an independent implementation of filtering, feature, morphology, measurement, registration and segmentation methods.", "Function availability does not establish method fitness or cross-provider equivalence."),
    ("itk", "Insight Toolkit Documentation", "ITK project", 2026, "official_documentation", "https://docs.itk.org/en/latest/index.html", "Documents N-dimensional image representations, filtering, registration and segmentation.", "Scientific/medical image operations do not own industrial inspection lifecycle semantics."),
    ("merlic", "MERLIC Process Integration and Tool Flow", "MVTec", 2026, "official_product_documentation", "https://www.mvtec.com/doc/merlic/26.03/manual/en-us/Content/Getting_started/getting_started.html", "Provides market evidence for image acquisition, tool-flow authoring, recipes, runtime states, results and controller integration as one operated job.", "One vendor product does not define portable semantics or qualify a SAN provider."),
    ("halcon-acquisition", "HALCON Image Acquisition Solution Guide", "MVTec", 2025, "official_product_documentation", "https://www.mvtec.com/fileadmin/Redaktion/mvtec.com/products/halcon/documentation/solution_guide/solution_guide_ii_a_image_acquisition.pdf", "Documents device interfaces, timing modes and acquisition configuration responsibilities.", "An acquisition API does not prove trigger-to-item binding or evidence sufficiency."),
    ("zhang-calibration", "A Flexible New Technique for Camera Calibration", "Zhengyou Zhang", 2000, "primary_paper", "https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr98-71.pdf", "Defines planar-target estimation of intrinsic/extrinsic camera parameters and distortion.", "Estimated calibration parameters remain model-, data- and validity-scope dependent."),
    ("canny", "A Computational Approach to Edge Detection", "John Canny", 1986, "primary_paper", "https://doi.org/10.1109/TPAMI.1986.4767851", "Derives an edge detector from detection, localization and single-response criteria.", "An image edge is not necessarily an object boundary or defect."),
    ("otsu", "A Threshold Selection Method from Gray-Level Histograms", "Nobuyuki Otsu", 1979, "primary_paper", "https://doi.org/10.1109/TSMC.1979.4310076", "Defines a histogram-based threshold criterion using between-class variance.", "A threshold partition has no intrinsic domain meaning or defect authority."),
    ("sift", "Distinctive Image Features from Scale-Invariant Keypoints", "David G. Lowe", 2004, "primary_paper", "https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf", "Defines scale/orientation invariant local features and matching stages.", "Feature matches are correspondence candidates, not identity or inspection conclusions."),
    ("ssim", "Image Quality Assessment: From Error Visibility to Structural Similarity", "Wang, Bovik, Sheikh and Simoncelli", 2004, "primary_paper", "https://ece.uwaterloo.ca/~z70wang/publications/ssim.pdf", "Defines structural-similarity comparison as an image-quality index.", "SSIM is not semantic fidelity, defect equivalence or universal perceptual truth."),
    ("mvtec-ad", "MVTec AD Industrial Anomaly Dataset", "Bergmann, Fauser, Sattlegger and Steger", 2019, "primary_paper_and_dataset", "https://openaccess.thecvf.com/content_CVPR_2019/html/Bergmann_MVTec_AD_--_A_Comprehensive_Real-World_Dataset_for_Unsupervised_Anomaly_CVPR_2019_paper.html", "Defines a multi-category industrial anomaly benchmark with image- and pixel-level ground truth.", "Benchmark performance is dataset/cut/metric scoped and not production acceptance evidence."),
    ("mvtec-ad2", "MVTec AD 2 Advanced Industrial Anomaly Dataset", "Heckler-Kram et al.", 2026, "primary_paper_and_dataset", "https://www.mvtec.com/research-teaching/datasets/mvtec-ad-2", "Adds high-resolution scenarios, lighting distribution shifts, private test labels and runtime/memory evaluation.", "Private-server scores and non-commercial data do not establish deployability or domain validity."),
    ("visa", "VisA: Visual Anomaly Dataset", "Zou et al.", 2022, "primary_paper_and_dataset", "https://www.ecva.net/papers/eccv_2022/papers_ECCV/html/2149_ECCV_2022_paper.php", "Defines a large industrial anomaly dataset with image- and pixel-level labels across 12 objects.", "One benchmark does not establish a universal normality or defect model."),
    ("mvtec-3d", "MVTec 3D-AD", "Bergmann et al.", 2022, "primary_paper_and_dataset", "https://arxiv.org/abs/2112.09045", "Extends industrial anomaly detection/localization to paired 3D scans and RGB information.", "3D benchmark representations and metrics do not define metrological traceability."),
    ("coco", "Microsoft COCO: Common Objects in Context", "Lin et al.", 2014, "primary_paper_and_dataset", "https://arxiv.org/abs/1405.0312", "Defines object detection/segmentation annotations and evaluation framing.", "COCO classes, IoU and AP are not industrial defect semantics or acceptance costs."),
    ("voc", "The PASCAL Visual Object Classes Challenge", "Everingham et al.", 2010, "primary_paper_and_dataset", "https://doi.org/10.1007/s11263-009-0275-4", "Defines detection/classification/segmentation tasks and evaluation protocols.", "Benchmark task definitions remain distinct from an enterprise inspection contract."),
    ("morphology", "Mathematical Morphology and Its Applications to Image Processing", "Jean Serra and Pierre Soille", 1994, "primary_research_monograph", "https://doi.org/10.1007/978-94-011-1040-2", "Grounds morphology in set/lattice operations and structuring elements.", "Morphological transformation does not assign domain meaning to resulting regions."),
    ("haralick", "Textural Features for Image Classification", "Haralick, Shanmugam and Dinstein", 1973, "primary_paper", "https://doi.org/10.1109/TSMC.1973.4309314", "Defines co-occurrence-based texture feature families.", "Texture features are representation-dependent measurements, not defect findings."),
    ("ransac", "Random Sample Consensus", "Fischler and Bolles", 1981, "primary_paper", "https://doi.org/10.1145/358669.358692", "Defines robust parameter estimation from data containing outliers.", "A consensus model is hypothesis/evidence scoped and not guaranteed truth."),
    ("pro", "The MVTec Anomaly Detection Dataset evaluation protocol", "MVTec", 2026, "official_benchmark_protocol", "https://benchmark.mvtec.com/", "Defines official server-side evaluation for withheld anomaly masks and named metrics.", "A leaderboard score is not a calibrated production risk or acceptance decision."),
    ("openexr", "OpenEXR Technical Introduction", "Academy Software Foundation", 2026, "official_format_documentation", "https://openexr.com/en/latest/TechnicalIntroduction.html", "Defines high-dynamic-range channels, parts, windows, sampling and metadata concepts.", "A high-dynamic-range carrier does not establish radiometric calibration or evidence fitness."),
]


def sources() -> list[dict[str, Any]]:
    return sorted(({
        "source_id": f"source.visual.{key}", "title": title, "publisher": publisher,
        "year": year, "source_kind": kind, "url": url, "supported_claim": claim,
        "authority_limit": limit, "primary_or_official": True,
        "status": "INDEPENDENTLY_RESEARCHED_PRIMARY_OR_OFFICIAL",
    } for key, title, publisher, year, kind, url, claim, limit in SOURCE_ROWS), key=lambda row: row["source_id"])


MODULE_ROWS = [
    ("image-occurrence", "Which physical capture, carrier bytes, decode, sample array, rendition and derived image occurrence is referenced?", "typed occurrence identity", ["genicam", "dicom", "ome-ngff"], []),
    ("image-carrier-codec", "Which container, codec, profile and decode contract produces the sample array?", "representation ACL", ["tiff", "openexr", "dicom"], ["image-occurrence"]),
    ("sample-lattice", "Which axes, extent, spacing, origin, orientation, channel, dtype, range, missingness and layout apply?", "sampled-field algebra", ["ome-ngff", "openvx", "itk"], ["image-occurrence"]),
    ("pixel-format", "Which packing, component order, bit depth, endianness and valid range define a pixel sample?", "representation profile", ["genicam", "openvx"], ["sample-lattice"]),
    ("radiometry", "Which exposure, gain, response, noise, saturation and photon/electrical quantities apply?", "measurement model", ["emva1288-linear", "emva1288-general", "gum"], ["sample-lattice"]),
    ("color-spectral", "Which color space/profile, rendering intent, spectral bands and illumination semantics apply?", "color/spectral profile", ["icc", "genicam"], ["radiometry"]),
    ("coordinate-frames", "Which pixel, sensor, camera, object, machine and world coordinate frames exist?", "frame graph", ["zhang-calibration", "ome-ngff", "iso10360-7"], ["sample-lattice"]),
    ("camera-model", "Which projection, intrinsic, extrinsic, distortion and uncertainty model maps frames?", "geometric measurement model", ["zhang-calibration", "gum"], ["coordinate-frames"]),
    ("region-roi-mask", "Which ROI, mask, support, zone and inclusion/boundary semantics select samples?", "region algebra", ["ome-ngff", "opencv"], ["sample-lattice"]),
    ("label-component-contour", "Which label-map, connectivity, component, contour and topology semantics apply?", "topological region algebra", ["opencv", "scikit-image", "morphology"], ["region-roi-mask"]),
    ("acquisition-device", "Which camera/device/stream capabilities and transport identities are bound?", "device capability contract", ["genicam", "gige-vision", "usb3-vision"], ["pixel-format"]),
    ("acquisition-profile", "Which camera, lens, illumination, exposure, trigger, motion, view and evidence-quality requirements apply?", "acquisition design", ["halcon-acquisition", "emva1288-general"], ["acquisition-device", "radiometry", "camera-model"]),
    ("capture-synchronization", "Which item occurrence, trigger, clock, motion, frame set and multi-sensor synchronization form one capture?", "temporal binding protocol", ["genicam", "opc-machine-vision"], ["acquisition-profile"]),
    ("calibration-record", "Which artifact, method, environment, validity interval, traceability chain and uncertainty identify calibration?", "calibration aggregate", ["vim", "gum", "zhang-calibration"], ["camera-model"]),
    ("calibration-validity", "Does calibration apply to this exact acquisition configuration, time and environment?", "validity predicate", ["vim", "iso10360-7"], ["calibration-record", "acquisition-profile"]),
    ("measurement-result", "Which measurand, indication, model, unit, value, uncertainty and metrological traceability form a result?", "measurement result algebra", ["vim", "gum"], ["calibration-validity"]),
    ("intensity-color-transform", "Which range, dtype, color/radiometric and information-loss rules govern an intensity transform?", "image transform algebra", ["icc", "opencv", "scikit-image"], ["color-spectral"]),
    ("filter-restoration", "Which observation/noise model, kernel, boundary, padding and precision govern filtering/restoration?", "signal/image operator", ["opencv", "scikit-image", "itk"], ["sample-lattice"]),
    ("morphology", "Which lattice, ordering, structuring element and boundary semantics govern morphology?", "lattice operator", ["morphology", "opencv"], ["region-roi-mask"]),
    ("edge-contour", "Which detection/localization, scale, threshold, connectivity and linking semantics produce edge/contour candidates?", "feature operator", ["canny", "opencv"], ["filter-restoration"]),
    ("segmentation", "Which partition/label semantics, markers, objective, stopping and uncertainty define segmentation?", "partition method family", ["scikit-image", "itk", "coco"], ["label-component-contour"]),
    ("registration", "Which reference/moving images, transform family, metric, optimizer, interpolation and validity domain define registration?", "transform estimation", ["itk", "ransac"], ["coordinate-frames"]),
    ("feature-descriptor", "Which keypoint/texture/shape descriptor, invariance and normalization semantics apply?", "feature algebra", ["sift", "haralick", "scikit-image"], ["sample-lattice"]),
    ("template-matching", "Which reference template, search domain, occlusion, score and candidate-selection rules apply?", "similarity search", ["opencv", "sift"], ["feature-descriptor"]),
    ("geometric-measurement", "Which region/feature geometry, unit, transform and uncertainty define an image-derived measurement?", "geometric metrology", ["iso10360-7", "vim", "gum"], ["measurement-result", "label-component-contour"]),
    ("object-detection", "Which target ontology, candidate geometry, score, suppression and matching semantics define detections?", "predictive result family", ["coco", "voc"], ["feature-descriptor"]),
    ("classification", "Which target label edition, population, score, calibration and abstention semantics define classification?", "predictive result family", ["coco", "visa"], ["feature-descriptor"]),
    ("visual-anomaly", "Which normality reference, target population, anomaly score/map, threshold and distribution-shift contract apply?", "novelty/anomaly inference", ["mvtec-ad", "mvtec-ad2", "visa"], ["classification"]),
    ("three-d-analysis", "Which point/depth/height carrier, registration, surface and 3D anomaly semantics apply?", "3D image/point-field analysis", ["mvtec-3d", "ome-ngff"], ["registration"]),
    ("multimodal-analysis", "Which visible, infrared, ultraviolet, X-ray, hyperspectral, depth and derived channels may be fused?", "multimodal observation algebra", ["opc-machine-vision", "genicam", "dicom"], ["capture-synchronization"]),
    ("method-plan", "Which method graph, parameters, artifacts, randomness, provider, target, budget and expected result kinds form a plan?", "compiled analytical plan", ["openvx", "merlic"], ["filter-restoration", "segmentation", "registration"]),
    ("method-result", "Which output, status, score, region, measurement, uncertainty, limitations and attempt evidence form a method result?", "total result algebra", ["openvx", "coco", "pro"], ["method-plan"]),
    ("benchmark-evaluation", "Which dataset/cut, annotation edition, unit, metric, threshold, aggregation and uncertainty scope an evaluation?", "evaluation design", ["mvtec-ad2", "coco", "pro"], ["method-result"]),
    ("inspection-target", "Which physical item/lot/area occurrence and characteristic is inspected by which capture set?", "inspection occurrence aggregate", ["opc-machine-vision", "iso2859"], ["capture-synchronization"]),
    ("defect-vocabulary-acl", "Which vertical defect, characteristic, severity, zone and tolerance vocabulary is imported?", "vertical semantic ACL", ["mvtec-ad", "iso2859"], ["inspection-target"]),
    ("inspection-plan", "Which purpose, population, sampling, costs, evidence, acceptance and authority define the inspection program?", "inspection design aggregate", ["iso2859", "jcgm106"], ["defect-vocabulary-acl"]),
    ("reference-golden-baseline", "Which golden sample, template or normality baseline edition, population and validity scope apply?", "reference aggregate", ["mvtec-ad2", "merlic"], ["inspection-plan"]),
    ("tool-flow-recipe", "Which typed tool graph, parameters, acquisition/calibration bindings and result ports form a recipe?", "recipe graph", ["merlic", "openvx"], ["method-plan", "inspection-plan"]),
    ("recipe-qualification", "Which test corpus, capability envelope, timing, provider and calibration scope qualify/release a recipe?", "qualification lifecycle", ["opc-machine-vision", "merlic", "openvx"], ["tool-flow-recipe", "benchmark-evaluation"]),
    ("inspection-execution", "Which item, capture set, recipe edition, attempt, runtime state and finite budget identify a run?", "runtime process", ["opc-machine-vision", "merlic"], ["recipe-qualification", "inspection-target"]),
    ("tolerance-decision-rule", "Which specification limits, guard bands, uncertainty, costs and decision rule evaluate a characteristic?", "conformity predicate", ["jcgm106", "gum"], ["measurement-result", "inspection-plan"]),
    ("inspection-result", "Which not-inspected, incomplete, invalid, unknown, pass, fail and review-required states form a total result?", "inspection result algebra", ["opc-machine-vision", "jcgm106"], ["inspection-execution", "method-result", "tolerance-decision-rule"]),
    ("review-judgment", "Which reviewer, evidence cut, finding, defeater, judgment and appeal state form an inspection review?", "human judgment protocol", ["jcgm106", "pro"], ["inspection-result"]),
    ("disposition-authority", "Which quality authority may accept, reject, waive, quarantine, rework or escalate an inspection result?", "authority protocol", ["iso2859", "jcgm106"], ["review-judgment"]),
    ("effect-handoff", "Which disposition becomes an action proposal, authorization, attempt and physical effect receipt?", "effect ACL", ["opc-machine-vision", "merlic"], ["disposition-authority"]),
    ("evidence-provenance-replay", "Which carriers, configurations, plans, providers, attempts, results and reviews support replay/challenge?", "evidence bundle", ["openvx", "opc-machine-vision", "pro"], ["inspection-result"]),
    ("change-drift-requalification", "Which device, illumination, environment, data, method or policy change invalidates calibration/recipe qualification?", "change impact protocol", ["mvtec-ad2", "emva1288-general"], ["recipe-qualification", "calibration-validity"]),
    ("product-boundary-inspection", "What operated inspection-plan/recipe/run/review lifecycle belongs to Visual Inspection Operations?", "product boundary", ["opc-machine-vision", "merlic"], ["effect-handoff"]),
    ("product-boundary-image-analysis", "What independently adoptable image-analysis workspace/run/result lifecycle is not an industrial inspection product?", "product boundary", ["itk", "scikit-image", "openvx"], ["method-result"]),
]


def modules() -> list[dict[str, Any]]:
    return [{
        "module_id": f"module.visual.{key}", "owned_question": question, "formalism": formalism,
        "source_refs": sorted(f"source.visual.{source}" for source in source_refs),
        "dependency_refs": sorted(f"module.visual.{dep}" for dep in deps),
        "authority_limit": "Image structure, measurement, method output or inspection result does not by itself establish defect truth, disposition authority or a physical effect.",
        "research_status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED",
    } for key, question, formalism, source_refs, deps in MODULE_ROWS]


LAW_STATEMENTS = [
    "Physical scene is not capture occurrence, carrier bytes, decoded image, rendition or derived image.",
    "Carrier-byte equality is not decoded-sample, visual, radiometric or semantic equality.",
    "Image occurrence identity is not content digest, filename, frame number, dataset row or physical-item identity.",
    "Pixel is a sample at an indexed support, not automatically a physical point, object or observation.",
    "Zero intensity is not missing, masked, saturated, clipped, transparent or outside support.",
    "Channel index is not color, wavelength, modality or measurand without a profile.",
    "Pixel coordinate is not sensor, camera, object, machine or world coordinate.",
    "Coordinate transform is not calibration evidence; estimated parameters require a method, data and validity scope.",
    "Camera interoperability is not camera characterization, calibration or acquisition fitness.",
    "Camera characterization is not application calibration or end-to-end measurement uncertainty.",
    "Calibration record is not current calibration validity for an altered device, lens, focus, temperature or geometry.",
    "Acquired frame is not an item-bound inspection observation until trigger, time, view and item occurrence resolve.",
    "Image quality is not evidence sufficiency, method fitness or inspection correctness.",
    "Color-profile conformance is not perceptual equality or defect invariance.",
    "ROI is not object, defect, label, mask, contour, component or acceptance zone.",
    "Label value is not label meaning; a label map requires ontology and source-image binding.",
    "Connected component depends on connectivity/background semantics and is not automatically a physical object.",
    "Edge is not contour, boundary, crack, scratch or defect.",
    "Segmentation partition is not ground truth, object identity or defect classification.",
    "Registration transform is not physical correspondence outside its declared validity domain.",
    "Feature match is not item identity, pose truth or authorized correspondence.",
    "Template score is not detection probability, calibrated confidence or acceptance decision.",
    "Detection box, mask, keypoint, score and class label are distinct result components.",
    "Classification score is not calibrated probability, uncertainty, correctness or authority.",
    "Anomaly score is not defect fact, defect class, severity, nonconformance or reject disposition.",
    "Normality reference is population, acquisition and time scoped; it is not universal good product.",
    "Learned model output and deterministic method output share result/evidence laws but not identical assumptions.",
    "Method completion is not valid result, convergence, determinism, reproducibility or fitness.",
    "Benchmark score is not production accuracy, calibrated risk, portability or deployment qualification.",
    "Image-level, region-level, pixel-level and item/lot-level evaluation units are not interchangeable.",
    "IoU, AP, AUROC, AUPR and PRO measure different questions and cannot be silently substituted.",
    "Golden sample is not specification, population truth or permanently valid baseline.",
    "Inspection plan is not executable recipe; recipe is not qualified recipe; qualified recipe is not released recipe.",
    "Tool-graph typechecking is not semantic correctness, timing fitness or provider portability.",
    "Recipe portability requires semantic, calibration, error, timing, resource and result equivalence evidence.",
    "Method result is not analytical finding, inspection result, review judgment or quality disposition.",
    "Pass, fail, unknown, invalid, incomplete, not-inspected and review-required are distinct total states.",
    "Tolerance conformance is decision-rule and uncertainty dependent, not raw numeric comparison alone.",
    "Inspection acceptance is not lot acceptance, shipment release, safety approval or legal conformity by default.",
    "Review judgment does not rewrite source image, method result or prior evidence.",
    "Disposition is not action authorization, machine command, attempted effect or physical receipt.",
    "PLC/controller communication success is not evidence that the intended physical reject occurred.",
    "A model or agent may propose regions, labels or dispositions but cannot acquire semantic, review or effect authority.",
    "Visual Inspection Operations does not own device drivers, generic image kernels, vertical defect vocabularies or plant control authority.",
    "Image Analysis Workbench and Visual Inspection Operations are retained separately because they have different users, lifecycles, outputs and authority boundaries.",
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.visual.{i:03d}", "statement": statement,
             "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0}
            for i, statement in enumerate(LAW_STATEMENTS, 1)]


METHOD_GROUPS = {
    "carrier_decode": ["lossless decode", "lossy decode with declared loss", "demosaicing", "bit-depth conversion", "channel extraction/combination", "tiling/chunking", "pyramid construction", "format/profile validation"],
    "radiometric_color": ["dark/flat-field correction", "gain/offset correction", "response linearization", "white balance", "color-space conversion", "spectral calibration", "HDR merge/tone mapping", "shading correction"],
    "geometry_calibration": ["intrinsic calibration", "extrinsic calibration", "lens-distortion correction", "stereo calibration", "hand-eye calibration", "pose estimation", "homography estimation", "coordinate rectification", "uncertainty propagation"],
    "filter_restoration": ["linear convolution", "Gaussian filtering", "median/rank filtering", "bilateral filtering", "non-local denoising", "deconvolution", "sharpening", "background estimation/subtraction", "frequency-domain filtering"],
    "morphology_topology": ["erosion/dilation", "opening/closing", "hit-or-miss", "distance transform", "watershed", "skeletonization", "connected components", "hole filling", "component-tree filtering"],
    "edge_feature": ["gradient/edge detection", "contour linking", "corner detection", "blob detection", "line/circle detection", "texture descriptors", "local invariant descriptors", "shape descriptors", "keypoint matching"],
    "segmentation": ["global/adaptive thresholding", "region growing", "graph-cut segmentation", "active contours", "clustering segmentation", "marker-controlled watershed", "semantic segmentation", "instance segmentation", "panoptic segmentation", "interactive segmentation"],
    "registration_matching": ["rigid registration", "affine registration", "deformable registration", "intensity registration", "feature registration", "template matching", "shape matching", "robust consensus fitting", "multi-view registration"],
    "measurement_metrology": ["region geometry measurement", "edge-based gauging", "caliper measurement", "surface/profile measurement", "roughness/texture measurement", "color measurement", "3D dimensional measurement", "uncertainty-aware conformity evaluation"],
    "recognition_prediction": ["image classification", "object detection", "keypoint/pose detection", "one-class classification", "novelty detection", "visual anomaly localization", "few-shot defect recognition", "calibrated selective prediction", "conformal prediction", "ensemble prediction"],
    "3d_multimodal": ["depth-map analysis", "height-map analysis", "point-cloud segmentation", "surface reconstruction", "3D anomaly localization", "stereo depth", "structured-light analysis", "thermal image analysis", "hyperspectral analysis", "X-ray/radiographic analysis", "multi-sensor fusion"],
    "inspection_operations": ["capture-item binding", "inspection sampling", "reference/golden comparison", "recipe compilation", "recipe qualification", "run execution", "tolerance evaluation", "abstention/review routing", "human adjudication", "disposition proposal", "machine-effect handoff", "reinspection/rework loop"],
    "evaluation_assurance": ["confusion-matrix evaluation", "precision/recall/AP evaluation", "IoU/Dice evaluation", "ROC/PR analysis", "PRO anomaly evaluation", "confidence calibration", "distribution-shift evaluation", "robustness/corruption testing", "runtime/memory benchmarking", "cross-provider differential testing", "metrological reverification"],
}


def methods() -> list[dict[str, Any]]:
    module_for = {
        "carrier_decode": "image-carrier-codec", "radiometric_color": "radiometry",
        "geometry_calibration": "camera-model", "filter_restoration": "filter-restoration",
        "morphology_topology": "morphology", "edge_feature": "edge-contour",
        "segmentation": "segmentation", "registration_matching": "registration",
        "measurement_metrology": "geometric-measurement", "recognition_prediction": "visual-anomaly",
        "3d_multimodal": "multimodal-analysis", "inspection_operations": "inspection-execution",
        "evaluation_assurance": "benchmark-evaluation",
    }
    source_for = {
        "carrier_decode": ["tiff", "openexr"], "radiometric_color": ["emva1288-general", "icc"],
        "geometry_calibration": ["zhang-calibration", "iso10360-7"], "filter_restoration": ["opencv", "scikit-image"],
        "morphology_topology": ["morphology", "opencv"], "edge_feature": ["canny", "sift", "haralick"],
        "segmentation": ["scikit-image", "itk", "coco"], "registration_matching": ["itk", "ransac"],
        "measurement_metrology": ["vim", "gum", "iso10360-7"], "recognition_prediction": ["mvtec-ad", "mvtec-ad2", "visa"],
        "3d_multimodal": ["mvtec-3d", "dicom", "genicam"], "inspection_operations": ["opc-machine-vision", "merlic", "jcgm106"],
        "evaluation_assurance": ["coco", "mvtec-ad2", "pro"],
    }
    rows = []
    for group, names in METHOD_GROUPS.items():
        for i, name in enumerate(names, 1):
            rows.append({
                "method_type_id": f"method.visual.{group}.{i:02d}", "method_group": group,
                "name": name, "semantic_module_ref": f"module.visual.{module_for[group]}",
                "source_refs": sorted(f"source.visual.{ref}" for ref in source_for[group]),
                "result_law": "Every method returns a typed total result with exact input/plan/provider identity, uncertainty or limitation, finite-resource outcome and no implied inspection authority.",
                "llm_dependency": "none", "status": "EVIDENCE_BACKED_METHOD_TYPE_CANDIDATE_UNRATIFIED",
            })
    return rows


EXPERT_ROWS = [
    ("zhang", "Zhengyou Zhang", "camera calibration", "Treat calibration as estimated model parameters tied to exact images, geometry and residual evidence.", ["zhang-calibration"]),
    ("canny", "John Canny", "edge detection", "Derive operators from explicit competing criteria; do not confuse detection and localization performance.", ["canny"]),
    ("otsu", "Nobuyuki Otsu", "threshold selection", "Expose the histogram objective and class assumptions rather than treating a threshold as domain truth.", ["otsu"]),
    ("serra", "Jean Serra", "mathematical morphology", "Model structuring elements and lattice operations algebraically so implementation optimizations preserve meaning.", ["morphology"]),
    ("soille", "Pierre Soille", "morphological image analysis", "Treat connectivity, watershed and region transforms as explicit topological decisions.", ["morphology"]),
    ("lowe", "David G. Lowe", "local invariant features", "Keep feature detection, description, matching and geometric verification as separate stages.", ["sift"]),
    ("haralick", "Robert Haralick", "texture and image features", "Bind texture features to quantization, offsets, directions and aggregation choices.", ["haralick"]),
    ("szeliski", "Richard Szeliski", "computer vision systems", "Decompose vision into image formation, features, alignment, recognition and reconstruction rather than one opaque method.", ["opencv", "zhang-calibration"]),
    ("steger", "Carsten Steger", "industrial machine vision and anomaly benchmarks", "Join algorithms to acquisition, calibration, recipe and evaluation evidence without collapsing results into decisions.", ["mvtec-ad", "mvtec-ad2", "merlic"]),
    ("bergmann", "Paul Bergmann", "industrial visual anomaly detection", "Evaluate image- and pixel-level anomaly outputs separately and preserve benchmark scope.", ["mvtec-ad", "mvtec-3d"]),
    ("bovik", "Alan Bovik", "image quality assessment", "Treat structural similarity as one scoped metric, not semantic or inspection equivalence.", ["ssim"]),
    ("wang", "Zhou Wang", "perceptual image quality", "Make reference image, scale and pooling choices explicit in quality comparisons.", ["ssim"]),
    ("fischler", "Martin Fischler", "robust geometric estimation", "Separate hypothesis generation, consensus scoring and final estimation with explicit inlier thresholds.", ["ransac"]),
    ("bolles", "Robert Bolles", "robust model fitting", "Preserve stochastic trials, support sets and failure probability in geometric results.", ["ransac"]),
    ("lin", "Tsung-Yi Lin", "object detection datasets/evaluation", "Bind labels, boxes/masks, matching thresholds and AP aggregation to an exact dataset edition.", ["coco"]),
    ("everingham", "Mark Everingham", "visual recognition evaluation", "Treat task definitions and evaluation protocols as first-class contracts.", ["voc"]),
    ("theuwissen", "Albert Theuwissen", "solid-state image sensor characterization", "Separate photon/electrical sensor behavior from downstream application semantics.", ["emva1288-linear"]),
    ("jaehne", "Bernd Jähne", "scientific image processing", "Preserve scale, sampling, physical units and uncertainty across image operations.", ["itk", "gum"]),
    ("ibanez", "Luis Ibáñez", "ITK and reproducible image analysis", "Use typed N-dimensional image geometry and pipeline metadata rather than bare arrays.", ["itk"]),
    ("van-der-walt", "Stefan van der Walt", "reproducible image algorithms", "Expose dtype/range conventions and reference implementations as conformance evidence.", ["scikit-image"]),
    ("epple", "Ulrich Epple", "OPC UA machine-vision information modeling", "Separate system integration/state/recipes/results from implementation-specific processing internals.", ["opc-machine-vision"]),
    ("volpe", "Chris Volpe", "GenICam interoperability", "Keep feature naming, transport and data-container layers separable and editioned.", ["genicam"]),
    ("heckler-kram", "Lars Heckler-Kram", "industrial anomaly evaluation under shift", "Test illumination shift, small defects and private labels rather than assuming saturated benchmarks generalize.", ["mvtec-ad2"]),
    ("zou", "Yang Zou", "visual anomaly datasets", "Distinguish normal/anomalous populations, image labels and pixel masks in few-shot evaluation.", ["visa"]),
]


def experts() -> list[dict[str, Any]]:
    return [{
        "expert_id": f"expert.visual.{key}", "name": name, "specialism": specialism,
        "learning_for_corpus": learning, "source_refs": sorted(f"source.visual.{ref}" for ref in refs),
        "authority_limit": "Expert work informs bounded propositions; no person, paper, vendor or standards body becomes the SAN semantic owner.",
        "status": "LEARNING_PROFILE_NOT_ENDORSEMENT",
    } for key, name, specialism, learning, refs in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("emva1288-r4", 2021, "EMVA 1288 Release 4", "General and linear camera characterization modules broaden objective sensor/camera evidence.", ["emva1288-linear", "emva1288-general"], "none"),
    ("openvx-feature-sets", 2021, "OpenVX feature sets", "Portable coherent capability subsets and conformance profiles make heterogeneous vision binding more explicit.", ["openvx"], "none"),
    ("mvtec-3d", 2022, "MVTec 3D-AD", "Pairs 3D scans and RGB for industrial anomaly detection/localization evaluation.", ["mvtec-3d"], "learned_or_classical_method_optional_not_llm"),
    ("icc44", 2022, "ICC profile version 4.4", "Updates governed color-management profiles and rendering semantics.", ["icc"], "none"),
    ("visa", 2022, "VisA industrial anomaly dataset", "Expands object domains, sample counts and pixel-level industrial anomaly labels.", ["visa"], "learned_or_classical_method_optional_not_llm"),
    ("ome-zarr-v3", 2024, "OME-NGFF over Zarr v3", "Moves multidimensional/multiscale image and label metadata toward cloud-native chunked representations.", ["ome-ngff"], "none"),
    ("mvtec-ad2", 2025, "MVTec AD 2", "Adds lighting shifts, tiny defects, high-resolution scenarios, private labels and resource measurement.", ["mvtec-ad2"], "learned_or_classical_method_optional_not_llm"),
    ("genicam-gendc12", 2026, "GenICam GenDC 1.2", "Editioned generic data containers broaden transport of heterogeneous sensor components.", ["genicam"], "none"),
    ("genicam-pfnc24", 2026, "GenICam PFNC 2.4", "Expands governed pixel-format names and values rather than relying on vendor strings.", ["genicam"], "none"),
    ("genicam-sfnc28", 2026, "GenICam SFNC 2.8", "Updates standardized camera feature naming and interoperability contracts.", ["genicam"], "none"),
    ("openvx132", 2026, "OpenVX 1.3.2", "Refreshes portable vision specifications, headers, feature sets and safety-critical deployment material.", ["openvx"], "none"),
    ("iso2859-2026", 2026, "ISO 2859-1 edition 3", "Updates attribute-sampling schemes and adds skip-lot procedures while retaining explicit switching logic.", ["iso2859"], "none"),
    ("gum-nonlinearity", 2026, "GUM Amendment 1 nonlinearity", "Makes nonlinearity in measurement models a first-class uncertainty concern.", ["gum1"], "none"),
    ("opc-machine-vision-current", 2026, "OPC UA Machine Vision current edition", "Provides machine-readable state, configuration, recipe and result integration semantics.", ["opc-machine-vision"], "none"),
    ("private-evaluation", 2025, "Withheld-label industrial evaluation servers", "Reduces direct ground-truth overfitting but introduces server, metric and submission identity obligations.", ["mvtec-ad2", "pro"], "none"),
]


def innovations() -> list[dict[str, Any]]:
    return [{
        "innovation_id": f"innovation.visual.{key}", "year": year, "name": name,
        "compiler_relevance": relevance, "source_refs": sorted(f"source.visual.{ref}" for ref in refs),
        "ai_or_llm_dependency": dependency, "status": "RECENT_INNOVATION_CANDIDATE_UNRATIFIED",
    } for key, year, name, relevance, refs, dependency in INNOVATION_ROWS]


def module_refs_for_library(library_ref: str) -> list[str]:
    text = library_ref.lower()
    keys = {"image-occurrence", "method-result", "evidence-provenance-replay"}
    if any(x in text for x in ["measurement", "calibration"]): keys |= {"radiometry", "calibration-record", "calibration-validity", "measurement-result"}
    if any(x in text for x in ["image", "raster", "spatial", "pointcloud", "codec"]): keys |= {"image-carrier-codec", "sample-lattice", "coordinate-frames", "region-roi-mask", "segmentation", "registration"}
    if any(x in text for x in ["predictive", "anomaly", "classification", "label", "agreement", "consensus"]): keys |= {"classification", "visual-anomaly", "benchmark-evaluation", "change-drift-requalification"}
    if any(x in text for x in ["recipe", "pipeline", "analysis_design"]): keys |= {"inspection-plan", "tool-flow-recipe", "recipe-qualification"}
    if any(x in text for x in ["runtime", "executor", "attempt", "receipt"]): keys |= {"inspection-execution", "capture-synchronization"}
    if any(x in text for x in ["decision", "review", "acceptance", "conformance", "quantity"]): keys |= {"tolerance-decision-rule", "inspection-result", "review-judgment", "disposition-authority", "effect-handoff"}
    if "acquisition" in text or "observation_binding" in text: keys |= {"acquisition-device", "acquisition-profile", "capture-synchronization"}
    if "coordinate_transform" in text: keys |= {"coordinate-frames", "camera-model", "registration"}
    if "image_methods" in text: keys |= {"filter-restoration", "morphology", "edge-contour", "segmentation", "registration", "feature-descriptor", "geometric-measurement"}
    if "analytical_finding" in text or "result_algebra" in text: keys |= {"method-plan", "method-result", "inspection-result"}
    if "effect" in text or "action" in text: keys |= {"disposition-authority", "effect-handoff"}
    if "provenance" in text or "evidence" in text: keys |= {"evidence-provenance-replay"}
    return sorted(f"module.visual.{key}" for key in keys)


def library_bindings(source_ids: set[str]) -> list[dict[str, Any]]:
    direct = declared_product_libraries()
    default_sources = sorted(source_ids)[:6]
    rows = []
    for ref in LIBRARIES:
        modules_for_ref = module_refs_for_library(ref)
        rows.append({
            "library_ref": ref, "relationship_to_product": "DECLARED_CONCRETE_BINDING" if ref in direct else "JUSTIFIED_NEIGHBOR_IMPORT_OR_OWNER",
            "semantic_module_refs": modules_for_ref,
            "evidence_refs": default_sources,
            "downstream_product_refs": sorted(PRODUCTS if ref in direct else PRODUCTS | {"product.image_analysis_workbench"}),
            "downstream_contract_route": "DECLARED_PRODUCT_BINDING_UNRATIFIED" if ref in direct else "NEIGHBOR_IMPORT_CANDIDATE_UNRATIFIED",
            "refusal_reasons": ["OWNER_RATIFICATION_MISSING", "EXACT_CONTRACT_UNSELECTED", "QUALIFIED_IMPLEMENTATION_MISSING", "TWO_VERTICAL_ACCEPTANCE_MISSING"],
            "compiler_binding": "REFUSED", "completion_claim": False,
        })
    return rows


def axis_rows(bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for binding in bindings:
        for axis in AXES:
            rows.append({
                "library_ref": binding["library_ref"], "axis": axis,
                "semantic_module_refs": binding["semantic_module_refs"], "evidence_refs": binding["evidence_refs"],
                "decision_candidate": "UNRESOLVED_RESEARCHED_CANDIDATE", "coordinate_answers": [],
                "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False,
            })
    return rows


def findings() -> list[dict[str, Any]]:
    direct = sorted(declared_product_libraries())
    rows = [{
        "finding_id": "finding.visual.inspection-product.v1", "candidate_disposition": "RETAIN_VISUAL_INSPECTION_OPERATIONS_BUT_NARROW_IMPORTED_OWNERS",
        "product_ref": "product.visual_inspection_operations", "library_refs": direct,
        "finding": "Retain the independently adoptable inspection plan/recipe/run/review lifecycle, while importing device, acquisition measurement, generic image methods, vertical defect vocabulary, predictive models and machine effects through explicit contracts.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }, {
        "finding_id": "finding.visual.image-analysis-product.v1", "candidate_disposition": "RETAIN_IMAGE_ANALYSIS_WORKBENCH_WITH_EXACT_IMPORTED_OWNERS",
        "product_ref": "product.image_analysis_workbench",
        "library_refs": [ref for ref, _ in VACANCIES if ref.startswith("library.analytics_image_analysis.")],
        "finding": "Retain the independently adopted project/workspace/recipe/run/result/review/publication lifecycle while importing carrier, lattice, radiometry, calibration, generic methods, vertical vocabularies and downstream authority.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }, {
        "finding_id": "finding.visual.image-methods-split.v1", "candidate_disposition": "SPLIT_OVERBROAD_IMAGE_METHODS_LIBRARY",
        "library_refs": ["library.method_kernels.image_methods"],
        "finding": "The current Image Methods library combines carrier/lattice semantics, transforms, filtering, morphology, segmentation, registration, features and measurement; these have different laws, configurations, results and qualification oracles.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }]
    for i, (ref, rationale) in enumerate(VACANCIES, 1):
        rows.append({
            "finding_id": f"finding.visual.library-vacancy.{i:02d}",
            "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED",
            "proposed_library_ref": ref, "library_refs": [], "finding": rationale,
            "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
        })
    return rows


def bounded_context() -> dict[str, Any]:
    return {
        "slice_id": "slice.visual-image-inspection.v1",
        "retained_product": "product.visual_inspection_operations",
        "retained_image_analysis_product": "product.image_analysis_workbench",
        "inside_visual_inspection_operations": ["inspection plan", "qualified recipe", "item-bound run", "inspection result", "review/disposition", "effect proposal"],
        "inside_image_analysis_workbench_candidate": ["image carrier/profile", "analysis workspace", "method plan/run", "result comparison", "evidence publication"],
        "imported_owners": ["device/transport", "measurement/calibration", "generic image kernels", "predictive model lifecycle", "annotation/ground truth", "vertical defect vocabulary", "quality authority", "machine control/effects"],
        "product_boundary_candidates": [
            {"product_ref": "product.visual_inspection_operations", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
            {"product_ref": "product.image_analysis_workbench", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
        ],
        "non_collapse_summary": "carrier != sample field != observation; feature/score/region != defect; method result != inspection result != judgment/disposition != authorized physical effect",
        "status": "CANDIDATE_UNRATIFIED", "completion_claim": False,
    }


def build() -> dict[str, Any]:
    src = sources()
    source_ids = {row["source_id"] for row in src}
    mods = modules()
    bindings = library_bindings(source_ids)
    axis = axis_rows(bindings)
    fs = findings()
    summary = {
        "slice_id": "slice.visual-image-inspection.v1", "as_of": AS_OF,
        "primary_or_official_sources": len(src), "semantic_modules": len(mods),
        "non_collapse_laws": len(LAW_STATEMENTS), "method_types": sum(map(len, METHOD_GROUPS.values())),
        "expert_learning_profiles": len(EXPERT_ROWS), "recent_innovations": len(INNOVATION_ROWS),
        "declared_product_libraries": len(declared_product_libraries()), "justified_neighbor_libraries": len(NEIGHBORS),
        "bound_libraries": len(LIBRARIES), "library_axis_decision_candidates": len(axis),
        "candidate_new_products": 0, "retained_products": 2, "candidate_new_library_vacancies": len(VACANCIES),
        "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0,
        "canonical_gaps_closed": 0, "completion_claim": False,
    }
    return {"sources": src, "modules": mods, "laws": laws(), "methods": methods(), "experts": experts(),
            "innovations": innovations(), "libraries": bindings, "axes": axis, "findings": fs,
            "context": bounded_context(), "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "semantic-modules.jsonl": "".join(canonical(row) + "\n" for row in built["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(row) + "\n" for row in built["laws"]),
        "visual-image-method-taxonomy.jsonl": "".join(canonical(row) + "\n" for row in built["methods"]),
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
        "manifest_id": "manifest.visual-image-inspection-semantic-slice.v1", "as_of": AS_OF,
        "files": claims, "completion_claim": False,
    }, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    summary = build()["summary"]
    print(f"BUILD PASS visual/image inspection semantic slice: {summary['semantic_modules']} modules, {summary['method_types']} methods, {summary['bound_libraries']} libraries, {summary['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
