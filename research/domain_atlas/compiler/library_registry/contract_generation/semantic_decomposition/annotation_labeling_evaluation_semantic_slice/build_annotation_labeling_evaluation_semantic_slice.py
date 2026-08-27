#!/usr/bin/env python3
"""Build the evidence-backed annotation, labeling and reference-evaluation semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
PRODUCTS = {"product.annotation_operations", "product.dataset_curation_workbench"}
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

NEIGHBORS = {
    "library.analytical_workspace.definition.compiler",
    "library.analytical_workspace.lifecycle.reducer",
    "library.business_glossary.taxonomy_binding",
    "library.document.rendition.evaluator",
    "library.gmo.privacy_purpose_binding",
    "library.method_kernels.descriptive_statistics",
    "library.method_kernels.document_content_graph",
    "library.method_kernels.document_extraction_evaluation",
    "library.method_kernels.document_layout_methods",
    "library.method_kernels.document_ocr_methods",
    "library.method_kernels.document_provenance_loss",
    "library.method_kernels.image_methods",
    "library.method_kernels.inferential_tests_resampling",
    "library.method_kernels.provider_qualification",
    "library.method_kernels.raster_grid_methods",
    "library.method_kernels.spatial_reference_semantics",
    "library.method_kernels.statistical_estimators",
    "library.method_kernels.vector_geometry_topology",
    "library.ontology_model.axiom_profile",
    "library.ontology_model.identity_import_closure",
    "library.ontology_model.ontology_mapping",
    "library.ontology_model.shape_validation",
    "library.pipeline.data_cut_algebra",
    "library.pointcloud.3d.evaluator",
    "library.pointcloud.analysis.profile.compiler",
    "library.predictive.calibration",
    "library.predictive.classification_models",
    "library.predictive.conformal_prediction",
    "library.predictive.graph_sampling",
    "library.predictive.image_features",
    "library.predictive.metrics",
    "library.predictive.model_lifecycle",
    "library.predictive.neural_predictive_models",
    "library.predictive.robustness_evaluation",
    "library.spt.privacy_accountant",
    "library.spt.privacy_vocabulary",
}

VACANCIES = [
    ("library.annotation.project-definition", "Purpose, target population, schema, instructions, quality policy, roles, budgets and release intent need one editioned project contract."),
    ("library.annotation.target-occurrence-binding", "Source occurrence, immutable version, selector, state, rendition and resolvability evidence must be bound before work."),
    ("library.annotation.schema-constraint-algebra", "Label types, values, attributes, relations, cardinalities, dependencies, abstention and unknown states need a portable schema algebra."),
    ("library.annotation.instruction-example-edition", "Instructions, definitions, positive/negative/borderline examples, precedence and change impact require immutable editions."),
    ("library.annotation.task-sampling-design", "Population/frame, inclusion probabilities, strata, overlap, seed, weights and intended estimands require a sampling design."),
    ("library.annotation.worker-competence-profile", "Role, domain competence, training, calibration, language, conflicts, accessibility and validity require a scoped profile."),
    ("library.annotation.assignment-lease", "Task scope, worker, blinding, overlap group, lease, concurrency, expiry and submission authority need a lifecycle."),
    ("library.annotation.occurrence-algebra", "Human annotation, imported assertion, weak label, model suggestion, correction and adjudicated reference need distinct occurrence kinds."),
    ("library.annotation.modality-shape-algebra", "Text spans, regions, tracks, intervals, graphs, tables, audio, 3D and geospatial selectors need typed modality-specific shapes."),
    ("library.annotation.review-plan", "Review sampling, independence, issue taxonomy, severity, evidence, escalation and acceptance thresholds require a plan."),
    ("library.annotation.agreement-applicability", "Scale, unit, coder design, missingness, prevalence, distance function, uncertainty and interpretation must precede metric selection."),
    ("library.annotation.annotator-model-estimator", "Latent-label inference requires worker-error assumptions, identifiability, priors, uncertainty and abstention rather than silent majority truth."),
    ("library.annotation.consensus-result-algebra", "Votes, quorum, ties, abstentions, unresolved disagreement, weights and derived consensus need a total result algebra."),
    ("library.annotation.adjudication-authority", "Adjudicator competence, authority scope, evidence cut, defeaters, rationale, appeal and expiry need an append-only judgment protocol."),
    ("library.annotation.reference-edition-lifecycle", "Accepted reference scope, evidence, exclusions, quality claims, supersession, challenge, recall and consumer notification need one lifecycle."),
    ("library.annotation.format-loss-crosswalk", "Source/target schema editions, identity mapping, coordinate conversion, unsupported semantics and quantified loss require an explicit crosswalk."),
    ("library.annotation.privacy-worker-safety-profile", "Purpose, consent, sensitive content, minimization, worker exposure, redaction, residency and retention need a campaign profile."),
    ("library.analytics_dataset_curation.dataset_definition_purpose", "Dataset identity, purpose, intended/prohibited uses, population, observation unit and coverage target require an editioned definition."),
    ("library.analytics_dataset_curation.source_occurrence_admission_membership", "Source occurrence admission and evidence-bearing membership decisions must remain distinct from source truth and views."),
    ("library.analytics_dataset_curation.inclusion_exclusion_selection", "Inclusion/exclusion predicates, sampling frames, unknown handling, precedence and residuals require a total selection algebra."),
    ("library.analytics_dataset_curation.curation_recipe_derivation", "Curation derivations require typed ordered recipes, exact cuts, declared loss, replay and comparison without becoming production pipelines."),
    ("library.analytics_dataset_curation.duplicate_evidence_adjudication", "Exact/near duplicate evidence, representations, thresholds, components and representative decisions require explicit adjudication."),
    ("library.analytics_dataset_curation.cohort_balance_coverage_assessment", "Cohorts, reference population, distributions, balance, coverage gaps and uncertainty require purpose-scoped assessment."),
    ("library.analytics_dataset_curation.partition_split_assignment", "Split roles, assignment units, group/time isolation, stratification and reproducible randomness require one partition contract."),
    ("library.analytics_dataset_curation.leakage_contamination_audit", "Duplicate, target, subject, group, temporal and provenance leakage require evidence, defeaters, limitations and residual-risk verdicts."),
    ("library.analytics_dataset_curation.annotation_reference_binding", "A curated dataset may bind zero or many annotation/reference editions through exact target coverage and recall semantics."),
    ("library.analytics_dataset_curation.rights_use_policy_manifest", "Rights, licenses, permissions, prohibitions, duties, consent evidence, purposes, conflicts and revocation require a fail-closed manifest."),
    ("library.analytics_dataset_curation.dataset_profile_statistics", "Dataset profiles require exact membership/split cuts, statistic applicability, uncertainty, suppression and comparison semantics."),
    ("library.analytics_dataset_curation.documentation_metadata_projection", "Datasheets, data cards, Croissant, DCAT and DataCite are evidence-bearing projections with explicit omissions and loss."),
    ("library.analytics_dataset_curation.immutable_dataset_edition_manifest", "A sealed dataset edition requires complete membership, schema, split, annotation, rights, documentation, distribution and digest manifests."),
    ("library.analytics_dataset_curation.release_maintenance_recall", "Release, delivery, maintenance, change impact, successor editions, deprecation and recall require distinct receipt-bearing states."),
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
    ("w3c-model", "Web Annotation Data Model", "W3C", 2017, "web_standard", "https://www.w3.org/TR/annotation-model/", "Defines annotation body, target, motivation, selectors, states, agents and time.", "Interoperability does not establish annotation correctness or reference authority."),
    ("w3c-vocab", "Web Annotation Vocabulary", "W3C", 2017, "web_standard", "https://www.w3.org/TR/annotation-vocab/", "Provides machine-readable annotation terms and relations.", "Vocabulary terms do not define a campaign schema or adjudication policy."),
    ("w3c-protocol", "Web Annotation Protocol", "W3C", 2017, "web_standard", "https://www.w3.org/TR/annotation-protocol/", "Defines annotation container discovery and CRUD protocol.", "Protocol success is not durable publication, correctness or review."),
    ("w3c-prov", "PROV-O", "W3C", 2013, "web_standard", "https://www.w3.org/TR/prov-o/", "Defines entity, activity, agent and derivation provenance.", "Provenance assertion is evidence, not proof of annotation truth."),
    ("iiif3", "IIIF Presentation API 3.0", "IIIF Consortium", 2020, "official_specification", "https://iiif.io/api/presentation/3.0/", "Uses annotation pages, canvases and selectors for rich digital objects.", "IIIF presentation scope does not cover all enterprise carriers or label semantics."),
    ("iiif4", "IIIF Presentation API 4.0 Release Candidate", "IIIF Consortium", 2026, "official_release_candidate", "https://iiif.io/api/presentation/4.0/", "Extends interoperable presentation and selector models including complex regions.", "Release-candidate semantics may change and do not grant domain authority."),
    ("media-fragments", "Media Fragments URI 1.0", "W3C", 2012, "web_standard", "https://www.w3.org/TR/media-frags/", "Defines temporal and spatial media fragments.", "Fragment syntax does not bind immutable source editions or complex shapes."),
    ("rfc6902", "JSON Patch", "IETF", 2013, "internet_standard", "https://www.rfc-editor.org/rfc/rfc6902", "Defines ordered document patch operations useful for correction evidence.", "Patch application does not supply semantic validity or authorization."),
    ("iso-laf", "ISO 24612 Linguistic Annotation Framework", "ISO", 2012, "international_standard", "https://www.iso.org/standard/37326.html", "Defines an abstract graph model and pivot serialization for linguistic annotations.", "LAF is language-resource scoped and does not own every modality."),
    ("tei", "TEI P5 Guidelines: Linking, Segmentation and Alignment", "TEI Consortium", 2026, "community_standard", "https://tei-c.org/release/doc/tei-p5-doc/en/html/SA.html", "Defines spans, milestones, links, alignment and stand-off mechanisms for texts.", "TEI structures do not define project acceptance or ground truth."),
    ("uima", "UIMA Version 3 Specification", "Apache UIMA", 2026, "official_specification", "https://uima.apache.org/d/uimaj-current/references.html", "Defines typed feature structures, CAS views and annotation indexes.", "Framework type systems are implementation surfaces, not semantic owners."),
    ("webvtt", "WebVTT", "W3C", 2019, "web_standard", "https://www.w3.org/TR/webvtt1/", "Defines timed text cues and payloads over media timelines.", "Timed cue representation is not transcription or event-label correctness."),
    ("geojson", "RFC 7946 GeoJSON", "IETF", 2016, "internet_standard", "https://www.rfc-editor.org/rfc/rfc7946", "Defines geographic feature geometries and coordinate ordering.", "GeoJSON geometry is not observation identity, topology or domain classification."),
    ("dicom-seg", "DICOM Segmentation Information Object", "NEMA/MITA", 2026, "official_standard", "https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.51.html", "Defines binary, fractional and label-map segmentations linked to source images.", "DICOM encoding does not establish clinical truth or diagnostic authority."),
    ("dicom-sr", "DICOM Structured Reporting", "NEMA/MITA", 2026, "official_standard", "https://dicom.nema.org/medical/dicom/current/output/chtml/part03/chapter_A.html", "Defines coded observations, measurements and image-coordinate references.", "Structured report conformance is not clinical acceptance."),
    ("ome-ngff", "OME-NGFF 0.5", "Open Microscopy Environment", 2025, "community_specification", "https://ngff.openmicroscopy.org/0.5/index.html", "Defines multidimensional images, label images and coordinate transformations.", "Label-image association does not establish label meaning or validity."),
    ("coco", "Microsoft COCO: Common Objects in Context", "Lin et al.", 2014, "primary_paper_dataset", "https://arxiv.org/abs/1405.0312", "Defines large-scale category, instance segmentation and keypoint annotations.", "COCO task classes and formats are benchmark-specific, not universal annotation semantics."),
    ("coco-panoptic", "Panoptic Segmentation", "Kirillov et al.", 2019, "primary_paper_dataset", "https://arxiv.org/abs/1801.00868", "Unifies thing-instance and stuff-semantic segmentation evaluation.", "Panoptic segments do not cover all region or uncertainty semantics."),
    ("cvat-review", "CVAT Review Mode", "CVAT", 2026, "official_product_documentation", "https://docs.cvat.ai/docs/manual/advanced/review/", "Documents issues, comments, review and correction workflow.", "Vendor workflow is market evidence, not a portable contract."),
    ("cvat-consensus", "CVAT Consensus-based Annotation", "CVAT", 2026, "official_product_documentation", "https://docs.cvat.ai/docs/qa-analytics/consensus/", "Documents overlapping jobs, consensus replicas and quality reports.", "Consensus configuration does not make majority output truth."),
    ("labelstudio-quality", "Label Studio Annotation Quality and Review", "HumanSignal", 2026, "official_product_documentation", "https://labelstud.io/guide/quality", "Documents review, ground-truth tasks, agreement and quality workflows.", "Product behavior does not establish portable metric applicability."),
    ("cohen", "A Coefficient of Agreement for Nominal Scales", "Jacob Cohen", 1960, "primary_paper", "https://doi.org/10.1177/001316446002000104", "Defines chance-corrected agreement for two coders on nominal categories.", "Kappa is design/prevalence dependent and is not annotation accuracy."),
    ("weighted-kappa", "Weighted Kappa", "Jacob Cohen", 1968, "primary_paper", "https://doi.org/10.1037/h0026256", "Extends kappa with graded disagreement weights.", "Weights encode judgment and cannot be inferred from ordinal names alone."),
    ("fleiss", "Measuring Nominal Scale Agreement Among Many Raters", "Joseph Fleiss", 1971, "primary_paper", "https://doi.org/10.1037/h0031619", "Defines multi-rater nominal agreement under a specified rating design.", "Fleiss kappa is not interchangeable with pairwise Cohen kappa."),
    ("krippendorff", "Computing Krippendorff's Alpha-Reliability", "Klaus Krippendorff", 2011, "primary_method_paper", "https://repository.upenn.edu/entities/publication/cd5c0360-6d25-4c28-b458-944dd1984076", "Defines alpha using observed/expected disagreement and distance functions.", "Alpha interpretation depends on unitizing, scale, missingness and sampling."),
    ("icc", "Intraclass Correlations: Uses in Assessing Rater Reliability", "Shrout and Fleiss", 1979, "primary_paper", "https://doi.org/10.1037/0033-2909.86.2.420", "Distinguishes ICC forms by effects, unit and consistency/agreement target.", "Reporting ICC without its exact model and unit is incomplete."),
    ("dawid-skene", "Maximum Likelihood Estimation of Observer Error-Rates", "Dawid and Skene", 1979, "primary_paper", "https://doi.org/10.2307/2346806", "Jointly estimates latent class and observer confusion parameters.", "Latent-label estimates depend on identifiability and model assumptions."),
    ("glad", "Whose Vote Should Count More", "Whitehill et al.", 2009, "primary_paper", "https://proceedings.neurips.cc/paper/2009/hash/f899139df5e1059396431415e770c6dd-Abstract.html", "Models annotator expertise and item difficulty for label aggregation.", "A fitted competence model does not grant adjudication authority."),
    ("snorkel", "Snorkel: Rapid Training Data Creation with Weak Supervision", "Ratner et al.", 2017, "primary_system_paper", "https://doi.org/10.14778/3157794.3157797", "Combines noisy labeling functions through a generative label model.", "Weak labels are probabilistic program outputs, not human annotations or accepted reference truth."),
    ("active-learning", "Active Learning Literature Survey", "Burr Settles", 2009, "research_survey", "https://minds.wisconsin.edu/handle/1793/60660", "Organizes pool, stream and membership-query active learning strategies.", "Selection efficiency does not preserve population representativeness automatically."),
    ("core-set", "Active Learning for Convolutional Neural Networks: A Core-Set Approach", "Sener and Savarese", 2018, "primary_paper", "https://openreview.net/forum?id=H1aIuk-RW", "Frames batch active selection as core-set coverage.", "Representation/model dependence limits transfer and sampling inference."),
    ("datasheets", "Datasheets for Datasets", "Gebru et al.", 2021, "primary_paper", "https://arxiv.org/abs/1803.09010", "Defines documentation questions across dataset motivation, composition, collection and maintenance.", "Documentation is not machine-readable conformance or fitness proof."),
    ("data-cards", "Data Cards", "Pushkarna et al.", 2022, "primary_paper", "https://arxiv.org/abs/2204.01075", "Defines purposeful, structured dataset transparency across stakeholder needs.", "A data card is a scoped disclosure, not complete provenance or acceptance."),
    ("croissant", "Croissant: A Metadata Format for ML-Ready Datasets", "MLCommons", 2024, "primary_paper_standard", "https://arxiv.org/abs/2403.19546", "Defines machine-readable dataset metadata, resources, structure and ML semantics.", "Croissant describes datasets but does not own annotation adjudication or legal fitness."),
    ("croissant11", "Croissant Format 1.1", "MLCommons", 2026, "community_specification", "https://docs.mlcommons.org/croissant/docs/croissant-spec-1.1.html", "Adds extensibility and richer provenance/usage-policy modeling.", "Consumers still must interpret external vocabularies and enforce policy."),
    ("iso5259-1", "ISO/IEC 5259-1:2024 Data Quality for Analytics and ML", "ISO/IEC", 2024, "international_standard", "https://www.iso.org/standard/81088.html", "Defines data-quality terminology and examples for analytics and ML.", "General quality vocabulary does not define annotation-specific acceptance."),
    ("dcat3", "Data Catalog Vocabulary 3", "W3C", 2024, "web_standard", "https://www.w3.org/TR/vocab-dcat-3/", "Defines datasets, distributions, versions, series and data services.", "Catalog metadata does not establish membership, rights or annotation quality."),
    ("datacite", "DataCite Metadata Schema 4.6", "DataCite", 2024, "official_schema", "https://schema.datacite.org/meta/kernel-4.6/", "Defines persistent dataset citation, creators, versions, relations and rights.", "Persistent identifiers do not establish content equivalence or fitness."),
    ("nist-ai-rmf", "AI Risk Management Framework 1.0", "NIST", 2023, "official_framework", "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf", "Requires documented data, human oversight, validity and risk governance.", "Risk framework guidance does not define annotation schema or metric algorithms."),
    ("iso19011", "ISO 19011:2018 Guidelines for Auditing Management Systems", "ISO", 2018, "international_standard", "https://www.iso.org/standard/70017.html", "Defines audit principles, competence, evidence and findings.", "Audit guidance does not make a reviewer an annotation adjudicator."),
    ("iso5725", "ISO 5725-1:2023 Accuracy of Measurement Methods", "ISO", 2023, "international_standard", "https://www.iso.org/standard/69418.html", "Distinguishes trueness and precision in measurement-method evaluation.", "Measurement accuracy terminology cannot be copied blindly to subjective labels."),
]


def sources() -> list[dict[str, Any]]:
    return sorted(({
        "source_id": f"source.annotation.{key}", "title": title, "publisher": publisher,
        "year": year, "source_kind": kind, "url": url, "supported_claim": claim,
        "authority_limit": limit, "primary_or_official": True,
        "status": "INDEPENDENTLY_RESEARCHED_PRIMARY_OR_OFFICIAL",
    } for key, title, publisher, year, kind, url, claim, limit in SOURCE_ROWS), key=lambda row: row["source_id"])


MODULE_ROWS = [
    ("project-purpose", "What annotation question, use, population and prohibited interpretation define the project?", "project purpose", ["w3c-model", "datasheets"], []),
    ("source-occurrence", "Which immutable source occurrence and content edition may be viewed but not rewritten?", "source ACL", ["w3c-model", "w3c-prov"], ["project-purpose"]),
    ("target-selector", "Which resource/fragment/selector/state/rendition identifies the exact annotation target?", "selector algebra", ["w3c-model", "media-fragments", "iiif3"], ["source-occurrence"]),
    ("selector-resolution", "Can the selector resolve uniquely against the declared source edition, coordinate system and state?", "resolution result algebra", ["w3c-model", "iiif4"], ["target-selector"]),
    ("annotation-body", "Which textual, semantic, geometric, relational or external body is asserted about a target?", "annotation body algebra", ["w3c-model", "w3c-vocab"], ["target-selector"]),
    ("motivation-role", "Is the occurrence classifying, tagging, describing, correcting, linking, assessing or another declared act?", "annotation role", ["w3c-vocab"], ["annotation-body"]),
    ("schema-edition", "Which label types, values, attributes, relations, constraints and unknown/abstain states form the schema?", "schema algebra", ["iso-laf", "uima"], ["project-purpose"]),
    ("taxonomy-ontology-binding", "Which label value maps to which external concept edition, with what mapping relation?", "semantic ACL", ["w3c-vocab", "iso-laf"], ["schema-edition"]),
    ("instruction-edition", "Which definitions, examples, precedence, ambiguity and escalation guidance governed the work?", "instruction contract", ["cvat-review", "labelstudio-quality"], ["schema-edition"]),
    ("project-definition", "Which purpose, sources, schema, instructions, roles, quality policy, budgets and release intent identify a project edition?", "project aggregate", ["labelstudio-quality", "cvat-consensus"], ["source-occurrence", "schema-edition", "instruction-edition"]),
    ("population-frame", "Which eligible target occurrences, exclusions and coverage claims define the annotation population?", "population contract", ["active-learning", "iso5259-1"], ["project-definition"]),
    ("task-sampling", "Which sampling design, strata, probabilities, overlap, seed and weights select task units?", "sampling design", ["active-learning", "core-set"], ["population-frame"]),
    ("worker-profile", "Which identity, role, competence, training, language, conflict and accessibility evidence applies?", "competence profile", ["iso19011", "cvat-review"], ["project-definition"]),
    ("assignment-lease", "Which worker may act on which task under what blinding, overlap, concurrency and expiry?", "assignment lifecycle", ["cvat-consensus", "iso19011"], ["task-sampling", "worker-profile"]),
    ("annotation-occurrence", "Which actor/tool asserted which body about which target under which schema/instruction and time?", "annotation occurrence", ["w3c-model", "w3c-prov"], ["assignment-lease", "annotation-body"]),
    ("occurrence-kind", "Is this human label, imported assertion, weak label, model suggestion, correction, consensus or adjudication?", "truth-role algebra", ["snorkel", "cvat-consensus"], ["annotation-occurrence"]),
    ("text-span-structure", "Which character/token/span/segment/tree/relation/coreference semantics bind text annotations?", "text annotation algebra", ["iso-laf", "tei", "uima"], ["target-selector"]),
    ("document-layout-table", "Which page, block, line, token, field, cell, row, column and relation are annotated?", "document annotation algebra", ["iiif3", "uima"], ["target-selector"]),
    ("image-region-shape", "Which box, polygon, mask, polyline, keypoint, skeleton, instance or crowd semantics apply?", "2D shape algebra", ["coco", "coco-panoptic"], ["target-selector"]),
    ("video-track-event", "Which frame/time interval, track identity, interpolation, occlusion and event boundary apply?", "spatiotemporal annotation", ["media-fragments", "webvtt"], ["target-selector"]),
    ("audio-speech", "Which time span, transcript, speaker, sound event, confidence and overlap semantics apply?", "audio annotation algebra", ["webvtt", "iso-laf"], ["target-selector"]),
    ("geospatial", "Which feature geometry, CRS, topology, validity time and spatial relation apply?", "geospatial annotation algebra", ["geojson", "iiif4"], ["target-selector"]),
    ("medical-scientific", "Which source frame, segment, coded concept, measurement and reference coordinate apply?", "domain annotation ACL", ["dicom-seg", "dicom-sr", "ome-ngff"], ["target-selector"]),
    ("three-d-pointcloud", "Which point/voxel/surface/cuboid/track and coordinate frame identify a 3D label?", "3D annotation algebra", ["ome-ngff", "iiif4"], ["target-selector"]),
    ("graph-relation", "Which nodes, edges, hyperedges, roles, direction and evidence define relational annotations?", "graph annotation algebra", ["iso-laf", "w3c-model"], ["annotation-occurrence"]),
    ("preference-ranking", "Which alternatives, pairwise/ordinal/rating choice, tie, abstention and rationale define preference data?", "judgment algebra", ["weighted-kappa", "krippendorff"], ["annotation-occurrence"]),
    ("weak-programmatic-label", "Which labeling functions, dependencies and probabilistic aggregation produce a weak label?", "weak supervision", ["snorkel", "dawid-skene"], ["occurrence-kind"]),
    ("model-suggestion", "Which model/version/cut/score generated a suggestion and how was it accepted, edited or rejected?", "suggestion ACL", ["cvat-review", "nist-ai-rmf"], ["occurrence-kind"]),
    ("correction-supersession", "Which attributable correction creates a new occurrence without erasing its predecessor?", "append-only correction", ["rfc6902", "w3c-prov"], ["annotation-occurrence"]),
    ("review-plan", "Which sample, reviewer independence, issue taxonomy, severity, evidence and threshold govern review?", "review design", ["cvat-review", "iso19011"], ["project-definition"]),
    ("review-issue", "Which target/annotation, finding, evidence, comments, resolution and appeal identify an issue?", "review issue aggregate", ["cvat-review", "iso19011"], ["review-plan", "annotation-occurrence"]),
    ("agreement-design", "Which unit, coders, scale, missingness, distance, prevalence, population and uncertainty scope agreement?", "agreement applicability", ["cohen", "fleiss", "krippendorff", "icc"], ["task-sampling"]),
    ("categorical-agreement", "Which observed/expected agreement and coder design define nominal or ordinal kappa?", "agreement estimator", ["cohen", "weighted-kappa", "fleiss"], ["agreement-design"]),
    ("alpha-distance", "Which coincidence construction and distance function define Krippendorff alpha?", "agreement estimator", ["krippendorff"], ["agreement-design"]),
    ("continuous-reliability", "Which ICC model, raters, unit and consistency/absolute-agreement target apply?", "reliability estimator", ["icc", "iso5725"], ["agreement-design"]),
    ("agreement-uncertainty", "Which sampling distribution, interval, sensitivity and subgroup slices qualify the estimate?", "statistical appraisal", ["krippendorff", "iso5725"], ["categorical-agreement", "alpha-distance", "continuous-reliability"]),
    ("latent-label-estimation", "Which worker-error/item-difficulty model and assumptions estimate latent labels?", "latent variable inference", ["dawid-skene", "glad"], ["agreement-design"]),
    ("consensus-rule", "Which eligible votes, weights, quorum, threshold, tie, abstention and unresolved rules apply?", "consensus policy", ["cvat-consensus", "labelstudio-quality"], ["agreement-design"]),
    ("consensus-result", "Which derived result, support, dissent, uncertainty and unresolved residual follow from the rule?", "total consensus result", ["cvat-consensus", "dawid-skene"], ["consensus-rule", "latent-label-estimation"]),
    ("adjudication", "Which authorized expert reviews which evidence cut and issues which defeasible judgment?", "authority protocol", ["iso19011", "cvat-review"], ["review-issue", "consensus-result"]),
    ("reference-acceptance", "Which annotations, schema, population, evidence, exclusions and authority form an accepted reference edition?", "reference release aggregate", ["labelstudio-quality", "w3c-prov"], ["adjudication"]),
    ("reference-challenge-recall", "How can a reference edition be challenged, superseded, recalled and propagated to consumers?", "change/recall lifecycle", ["w3c-protocol", "datacite"], ["reference-acceptance"]),
    ("export-crosswalk", "Which identities, shapes, coordinates and meanings survive export, and what loss is declared?", "representation ACL", ["coco", "iso-laf", "croissant"], ["reference-acceptance"]),
    ("privacy-safety", "Which purpose, consent, minimization, worker exposure, redaction, residency and retention apply?", "privacy/safety profile", ["nist-ai-rmf", "datasheets"], ["project-definition"]),
    ("quality-dashboard", "Which throughput, rework, agreement, defect, drift, coverage and uncertainty observations are shown?", "operational projection", ["cvat-consensus", "iso5259-1"], ["agreement-uncertainty", "review-issue"]),
    ("annotation-product-boundary", "What project/task/annotation/review/adjudication/reference-release lifecycle belongs to Annotation Operations?", "product boundary", ["w3c-model", "cvat-review", "labelstudio-quality"], ["reference-challenge-recall", "quality-dashboard"]),
    ("dataset-purpose-sources", "Which purpose, source datasets, rights, population and prohibited uses define a curated corpus?", "dataset curation intent", ["datasheets", "data-cards"], []),
    ("dataset-membership-transform", "Which exact records/files, derivations, filters, deduplication and transformations form membership?", "dataset occurrence algebra", ["croissant", "w3c-prov"], ["dataset-purpose-sources"]),
    ("dataset-balance-split", "Which strata, weights, train/validation/test splits, leakage constraints and intended evaluations apply?", "dataset partition design", ["iso5259-1", "datasheets"], ["dataset-membership-transform"]),
    ("dataset-documentation-rights", "Which provenance, creators, license, consent, restrictions, statistics and maintenance disclosures apply?", "dataset disclosure", ["croissant11", "data-cards", "datacite"], ["dataset-purpose-sources"]),
    ("dataset-release", "Which immutable membership, annotation refs, splits, manifests, checksums and documentation form a release?", "dataset edition lifecycle", ["croissant", "dcat3", "datacite"], ["dataset-balance-split", "dataset-documentation-rights"]),
    ("dataset-product-boundary", "What independently adoptable corpus curation, partition, documentation, release and maintenance lifecycle is not annotation?", "product boundary", ["datasheets", "croissant", "dcat3"], ["dataset-release", "annotation-product-boundary"]),
]


def modules() -> list[dict[str, Any]]:
    return [{
        "module_id": f"module.annotation.{key}", "owned_question": question, "formalism": formalism,
        "source_refs": sorted(f"source.annotation.{source}" for source in refs),
        "dependency_refs": sorted(f"module.annotation.{dep}" for dep in deps),
        "authority_limit": "Annotation, agreement, consensus or model output does not by itself establish source truth, accepted reference authority, downstream fitness or a business effect.",
        "research_status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED",
    } for key, question, formalism, refs, deps in MODULE_ROWS]


LAW_STATEMENTS = [
    "Source occurrence is not annotation target, selector, body, annotation occurrence or reference edition.",
    "Annotation target identity requires a source edition and selector state; a floating offset is not stable identity.",
    "Resource identity is not content digest, rendition identity, fragment identity or semantic subject identity.",
    "Selector syntax equality is not resolved-target equality; resolved-target equality is not semantic equivalence.",
    "Body is not label meaning unless bound to an exact schema/taxonomy edition.",
    "Annotation motivation/role is not annotation value or authority.",
    "UI label text is not label identifier, taxonomy concept, model target or business class.",
    "Unknown, not-applicable, cannot-determine, abstain, missing and negative are distinct states.",
    "Schema validation is not annotation correctness or reference acceptance.",
    "Instruction edition is part of annotation evidence and cannot be inferred from project name.",
    "Example is not definition; borderline example is not precedence rule.",
    "Task is not target, assignment, annotation, review issue or dataset member.",
    "Population is not sampling frame, selected sample, completed work or released corpus.",
    "Active-learning selection is not probability sampling and does not support population inference by default.",
    "Sampling weight is not worker vote weight, class weight, training loss weight or business priority.",
    "Worker identity is not competence, role, authority, reliability or current assignment.",
    "Assignment is not completed work; lease is not ownership and expiry revokes submission authority.",
    "Human annotation, imported assertion, weak label, model suggestion, correction, consensus and adjudication are distinct occurrence kinds.",
    "Model suggestion accepted by a human remains traceably model-assisted; it is not independent human evidence.",
    "Weak label is not ground truth, manual annotation or model prediction.",
    "Correction creates a new attributable occurrence and never erases prior evidence.",
    "Text character offset is not token identity, grapheme identity, semantic span or stable target across revisions.",
    "Bounding box, polygon, mask, keypoint, skeleton and instance identity are not interchangeable.",
    "Semantic segmentation label is not instance segmentation, panoptic segment or physical object identity.",
    "Video frame index is not time; interpolated track state is not independently observed annotation.",
    "Transcript is not speaker diarization, translation, semantic interpretation or acoustic event label.",
    "GeoJSON geometry is not CRS-independent shape, topology, observation or domain class.",
    "Medical image segment is not diagnosis, clinical finding, measurement truth or treatment authority.",
    "Graph relation annotation is not observed real-world relationship or logical entailment.",
    "Preference choice is not factual label, utility function, policy or downstream decision.",
    "Review issue is not proven defect; issue resolution is not source mutation.",
    "Reviewer competence is not adjudicator authority; adjudication is not majority vote.",
    "Raw agreement is not chance-corrected agreement, reliability, accuracy, validity or truth.",
    "Cohen kappa, weighted kappa, Fleiss kappa, Krippendorff alpha and ICC require different designs and cannot be silently substituted.",
    "Agreement metric without scale, coder design, missingness and unit is semantically incomplete.",
    "High agreement can reflect shared bias; low agreement can expose genuine ambiguity or underspecified instructions.",
    "Agreement aggregate is population- and prevalence-dependent and can hide subgroup disagreement.",
    "Metric point estimate is not uncertainty interval or evidence of threshold satisfaction.",
    "Latent-label estimate is a model-dependent inference, not discovered truth.",
    "Annotator reliability estimate is task/population/time scoped and not permanent competence.",
    "Consensus rule is not consensus result; consensus result is not unanimity, correctness or authority.",
    "Majority vote does not erase dissent, abstention, minority expertise or unresolved ties.",
    "Adjudication judgment is defeasible and scoped; it does not rewrite source content or prior annotations.",
    "Accepted reference is a versioned authority claim, not metaphysical ground truth or future correctness guarantee.",
    "Reference edition identity includes schema, population, evidence cut, exclusions and accepting authority.",
    "Reference supersession is not recall; recall issuance is not completed propagation.",
    "Annotation export is not semantic preservation; format conversion requires explicit loss and identity crosswalks.",
    "COCO, DICOM, Web Annotation, LAF and vendor formats are not mutually lossless by default.",
    "Annotation project is not dataset curation, model training, model evaluation or source-content management.",
    "Dataset membership is not annotation occurrence; an unlabeled dataset can be curated and annotations can span multiple datasets.",
    "Dataset edition is not file path, repository snapshot, annotation release or model-training cut.",
    "Deduplication identity is not semantic equivalence and can remove meaningful repeated occurrences.",
    "Train/validation/test split is not random partition unless its subject, group, time and contamination laws are explicit.",
    "Dataset balance is not population representativeness, fairness, task relevance or downstream utility.",
    "Dataset documentation is not license, consent, provenance completeness or fitness proof.",
    "Annotation Operations should import generic human work, quality metrics, privacy and modality carriers rather than own them.",
    "Dataset Curation Workbench and Annotation Operations have independent users, lifecycles, outputs and authority boundaries.",
    "Models and agents may propose annotations, samples or review priorities but cannot acquire semantic, adjudication, reference-release or effect authority.",
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.annotation.{i:03d}", "statement": statement,
             "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0}
            for i, statement in enumerate(LAW_STATEMENTS, 1)]


METHOD_GROUPS = {
    "target_selection": ["whole-resource target", "fragment selector", "text-position selector", "text-quote selector", "XPath/CSS selector", "SVG shape selector", "media temporal fragment", "image region selector", "WKT/GeoJSON selector", "3D region selector", "selector refinement", "state/rendition binding", "selector reanchoring"],
    "classification_rating": ["binary label", "single-class label", "multi-label classification", "hierarchical classification", "ordinal rating", "continuous rating", "likert judgment", "pairwise preference", "ranking", "best-worst choice", "abstaining classification", "confidence-qualified label"],
    "text_language": ["tokenization", "span/entity annotation", "part-of-speech tagging", "morphosyntactic annotation", "dependency syntax", "constituency syntax", "semantic role labeling", "relation extraction annotation", "coreference annotation", "sentiment/emotion annotation", "intent/slot annotation", "question-answer annotation", "translation alignment", "transcription correction", "summary evaluation", "toxicity/safety classification"],
    "document": ["page classification", "layout-region annotation", "reading-order annotation", "OCR transcription", "key-value field annotation", "table detection", "cell/row/column annotation", "form relation annotation", "signature/stamp annotation", "document redaction annotation"],
    "image_video_3d": ["bounding-box annotation", "polygon annotation", "semantic mask", "instance mask", "panoptic segmentation", "keypoint annotation", "skeleton/pose annotation", "polyline annotation", "depth/surface annotation", "3D cuboid annotation", "point-cloud segmentation", "object track", "action/event interval", "frame attribute interpolation", "occlusion/visibility annotation", "captioning", "visual question-answer grounding"],
    "audio_signal": ["speech transcription", "speaker diarization", "speaker identification", "word timestamping", "sound-event interval", "music structure annotation", "prosody annotation", "signal event marker", "time-series interval label", "change-point annotation"],
    "geo_scientific": ["point feature annotation", "line/path annotation", "polygon feature annotation", "raster region label", "spatiotemporal trajectory label", "medical image segmentation", "coded clinical finding", "microscopy label image", "measurement annotation", "scientific specimen annotation"],
    "sampling_assignment": ["simple random sampling", "stratified sampling", "cluster sampling", "systematic sampling", "overlap/replicate sampling", "uncertainty sampling", "margin sampling", "entropy sampling", "query-by-committee", "diversity/core-set sampling", "rare-class enrichment", "error-driven resampling", "competence-based assignment", "blind assignment", "lease-based dispatch"],
    "aggregation_agreement": ["raw percent agreement", "Cohen kappa", "weighted kappa", "Fleiss kappa", "Krippendorff alpha", "intraclass correlation", "Dice/IoU spatial agreement", "boundary-distance agreement", "majority vote", "weighted vote", "Dawid-Skene estimation", "GLAD expertise/difficulty estimation", "weak-label model", "quorum consensus", "unresolved consensus"],
    "review_assurance": ["gold-task calibration", "peer review", "expert review", "random quality audit", "risk-based review", "issue/comment workflow", "correction/supersession", "conflict adjudication", "appeal/re-adjudication", "agreement confidence interval", "subgroup agreement analysis", "instruction A/B pilot", "cross-provider differential", "reference acceptance", "reference recall"],
    "dataset_curation": ["source acquisition", "inclusion/exclusion filtering", "record linkage", "exact/near deduplication", "normalization/transformation", "class/stratum balancing", "group-aware splitting", "temporal splitting", "contamination/leakage audit", "license/consent filtering", "dataset statistics", "datasheet/data-card production", "Croissant metadata", "manifest/checksum release", "dataset versioning", "dataset deprecation/recall"],
}


def methods() -> list[dict[str, Any]]:
    module_for = {"target_selection": "target-selector", "classification_rating": "schema-edition", "text_language": "text-span-structure", "document": "document-layout-table", "image_video_3d": "image-region-shape", "audio_signal": "audio-speech", "geo_scientific": "medical-scientific", "sampling_assignment": "task-sampling", "aggregation_agreement": "agreement-design", "review_assurance": "review-plan", "dataset_curation": "dataset-product-boundary"}
    source_for = {"target_selection": ["w3c-model", "iiif4"], "classification_rating": ["iso-laf", "krippendorff"], "text_language": ["iso-laf", "tei", "uima"], "document": ["iiif3", "uima"], "image_video_3d": ["coco", "coco-panoptic", "media-fragments"], "audio_signal": ["webvtt", "iso-laf"], "geo_scientific": ["geojson", "dicom-seg", "ome-ngff"], "sampling_assignment": ["active-learning", "core-set", "cvat-consensus"], "aggregation_agreement": ["cohen", "fleiss", "krippendorff", "dawid-skene"], "review_assurance": ["cvat-review", "iso19011"], "dataset_curation": ["datasheets", "data-cards", "croissant"]}
    rows = []
    for group, names in METHOD_GROUPS.items():
        for i, name in enumerate(names, 1):
            rows.append({
                "method_type_id": f"method.annotation.{group}.{i:02d}", "method_group": group,
                "name": name, "semantic_module_ref": f"module.annotation.{module_for[group]}",
                "source_refs": sorted(f"source.annotation.{ref}" for ref in source_for[group]),
                "result_law": "Every method returns a typed result with exact target/schema/instruction/population/provider identity, partiality and evidence; no output implies reference, adjudication or downstream effect authority.",
                "llm_dependency": "none", "status": "EVIDENCE_BACKED_METHOD_TYPE_CANDIDATE_UNRATIFIED",
            })
    return rows


EXPERT_ROWS = [
    ("sanderson", "Robert Sanderson", "Web Annotation and IIIF", "Separate body, target, selector, state, motivation and provenance so annotations remain addressable across systems.", ["w3c-model", "iiif3"]),
    ("ciccarese", "Paolo Ciccarese", "open annotation models", "Model annotations as first-class associations rather than fields pasted into source records.", ["w3c-model"]),
    ("ide", "Nancy Ide", "linguistic annotation frameworks", "Use graph-based stand-off annotation and pivot models to avoid carrier-specific semantic capture.", ["iso-laf"]),
    ("romary", "Laurent Romary", "language-resource standards", "Keep primary data, annotation structures and data-category vocabularies separable and mappable.", ["iso-laf", "tei"]),
    ("krippendorff", "Klaus Krippendorff", "content analysis reliability", "Choose units, scale and disagreement function before computing alpha; include missingness and sampling uncertainty.", ["krippendorff"]),
    ("cohen", "Jacob Cohen", "chance-corrected agreement", "Treat kappa as a scoped statistic for a coder design, not an accuracy or truth score.", ["cohen", "weighted-kappa"]),
    ("fleiss", "Joseph Fleiss", "multi-rater reliability", "Declare rater sampling and rating design before applying multi-rater kappa or ICC.", ["fleiss", "icc"]),
    ("dawid", "A. Philip Dawid", "observer-error latent models", "Preserve latent-class and observer-error assumptions rather than calling estimated labels ground truth.", ["dawid-skene"]),
    ("skene", "Allan Skene", "observer-error estimation", "Estimate rater confusion jointly with latent outcomes while exposing identifiability and convergence limits.", ["dawid-skene"]),
    ("whitehill", "Jacob Whitehill", "crowd label aggregation", "Separate annotator expertise and item difficulty and never convert fitted competence into authority.", ["glad"]),
    ("ratner", "Alexander Ratner", "weak supervision", "Represent labeling functions, conflicts, dependencies and probabilistic labels separately from manual reference data.", ["snorkel"]),
    ("settles", "Burr Settles", "active learning", "Expose query strategy and sampling bias; annotation efficiency is not population coverage.", ["active-learning"]),
    ("savarese", "Silvio Savarese", "core-set active learning", "Treat representation and coverage metric as explicit dependencies of diversity-based sampling.", ["core-set"]),
    ("lin", "Tsung-Yi Lin", "large-scale visual annotation", "Bind category, image, instance, geometry and evaluation identities to one dataset edition.", ["coco"]),
    ("kirillov", "Alexander Kirillov", "panoptic annotation", "Keep instance and semantic region identities distinct even when one benchmark unifies evaluation.", ["coco-panoptic"]),
    ("gebru", "Timnit Gebru", "dataset documentation", "Document motivation, composition, collection, preprocessing, uses, distribution and maintenance before reuse.", ["datasheets"]),
    ("pushkarna", "Mahima Pushkarna", "data cards", "Design dataset disclosures around stakeholder decisions and lifecycle stages, not one generic checklist.", ["data-cards"]),
    ("noy", "Natasha Noy", "dataset metadata and discovery", "Make dataset resources, structure, semantics and provenance machine-readable without treating metadata as fitness.", ["croissant"]),
    ("benjelloun", "Omar Benjelloun", "Croissant dataset interoperability", "Bind file resources, record sets, fields, transformations and versioned vocabulary explicitly.", ["croissant", "croissant11"]),
    ("clunie", "David Clunie", "DICOM structured annotations", "Preserve source frames, coded concepts, geometry and observation provenance rather than exporting pixels plus loose labels.", ["dicom-seg", "dicom-sr"]),
    ("goldberg", "Ignacio Goldberg", "medical imaging annotations", "Distinguish segmentations, measurements and clinical statements in interoperable imaging objects.", ["dicom-seg"]),
    ("swedlow", "Jason Swedlow", "bioimaging data standards", "Keep multidimensional image geometry and label-image associations explicit and versioned.", ["ome-ngff"]),
    ("snow", "Rion Snow", "crowdsourced NLP annotation", "Use multiple independent judgments and adjudication evidence rather than assuming one annotator is gold.", ["dawid-skene", "iso-laf"]),
    ("artstein", "Ron Artstein", "inter-coder agreement", "Match agreement coefficients to task structure and interpret disagreement as a diagnostic of representation and instructions.", ["krippendorff", "cohen"]),
    ("passonneau", "Rebecca Passonneau", "NLP annotation reliability", "Model unitizing and prevalence effects and preserve ambiguity instead of forcing categories prematurely.", ["krippendorff", "iso-laf"]),
    ("cvat-community", "CVAT maintainers", "annotation workflow operations", "Separate tasks, assignments, consensus replicas, review issues, corrections and quality reports operationally.", ["cvat-review", "cvat-consensus"]),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.annotation.{key}", "name": name, "specialism": specialism,
             "learning_for_corpus": learning, "source_refs": sorted(f"source.annotation.{ref}" for ref in refs),
             "authority_limit": "Expert work informs bounded propositions; no person, paper, vendor or standards body becomes the SAN semantic owner.",
             "status": "LEARNING_PROFILE_NOT_ENDORSEMENT"}
            for key, name, specialism, learning, refs in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("datasheets", 2021, "Datasheets for datasets", "Makes dataset formation, composition, use and maintenance disclosures a lifecycle artifact.", ["datasheets"], "none"),
    ("data-cards", 2022, "Stakeholder-centered data cards", "Adds purposeful, structured transparency views rather than one undifferentiated dataset description.", ["data-cards"], "none"),
    ("nist-rmf", 2023, "NIST AI RMF data and human-oversight governance", "Connects dataset/annotation evidence to risk, validity and accountable oversight without granting model authority.", ["nist-ai-rmf"], "none"),
    ("iso5725-2023", 2023, "ISO 5725:2023 measurement accuracy revision", "Refreshes trueness/precision distinctions used carefully at objective-measurement annotation seams.", ["iso5725"], "none"),
    ("iso-laf-confirmed", 2023, "ISO LAF confirmation", "Preserves a current pivot model for interoperable stand-off linguistic annotations.", ["iso-laf"], "none"),
    ("croissant10", 2024, "Croissant 1.0", "Standardizes machine-readable dataset metadata, resources, record structure and ML semantics.", ["croissant"], "none"),
    ("iso5259", 2024, "ISO/IEC 5259 data-quality series", "Creates a governed vocabulary and process family for analytics/ML data quality.", ["iso5259-1"], "none"),
    ("dcat3", 2024, "DCAT 3 dataset series and versioning", "Strengthens machine-readable dataset/distribution/version/change descriptions.", ["dcat3"], "none"),
    ("datacite46", 2024, "DataCite Metadata Schema 4.6", "Improves persistent citation, contributor roles, rights and relation metadata for released datasets.", ["datacite"], "none"),
    ("coconut", 2024, "Model-assisted relabeling of COCO-scale segmentation", "Shows model proposals can accelerate relabeling while retained human/reference evidence remains necessary.", ["coco", "cvat-review"], "model_assistance_not_llm"),
    ("ome-ngff05", 2025, "OME-NGFF 0.5 label-image associations", "Advances cloud-native multidimensional carrier and label metadata.", ["ome-ngff"], "none"),
    ("quality-consensus", 2025, "Operational consensus replicas and automated QA", "Makes overlap, gold tasks, quality reports and review routing configurable workflow objects.", ["cvat-consensus", "labelstudio-quality"], "optional_model_assistance_not_llm"),
    ("croissant11", 2026, "Croissant 1.1", "Adds extensibility, provenance, vocabulary interoperability and structured usage policies.", ["croissant11"], "none"),
    ("iiif4", 2026, "IIIF Presentation 4 release candidate", "Broadens standardized complex digital-object presentation and selector support.", ["iiif4"], "none"),
    ("agent-assisted-labeling", 2026, "Governed model/agent-assisted annotation", "Separates generated proposal identity, human acceptance/edit/rejection and reference-release authority.", ["nist-ai-rmf", "cvat-review"], "optional_ai_or_llm_proposal_only"),
]


def innovations() -> list[dict[str, Any]]:
    return [{"innovation_id": f"innovation.annotation.{key}", "year": year, "name": name,
             "compiler_relevance": relevance, "source_refs": sorted(f"source.annotation.{ref}" for ref in refs),
             "ai_or_llm_dependency": dependency, "status": "RECENT_INNOVATION_CANDIDATE_UNRATIFIED"}
            for key, year, name, relevance, refs, dependency in INNOVATION_ROWS]


def module_refs_for_library(ref: str) -> list[str]:
    text = ref.lower()
    keys = {"project-purpose", "annotation-occurrence", "occurrence-kind", "annotation-product-boundary"}
    if "selector" in text or "addressable" in text: keys |= {"source-occurrence", "target-selector", "selector-resolution"}
    if "taxonomy" in text or "ontology" in text or "label_contract" in text or "target_contract" in text: keys |= {"schema-edition", "taxonomy-ontology-binding", "annotation-body"}
    if "human_work" in text or "assignment" in text or "sampling" in text: keys |= {"population-frame", "task-sampling", "worker-profile", "assignment-lease"}
    if "agreement" in text or "statistic" in text or "metric" in text: keys |= {"agreement-design", "categorical-agreement", "alpha-distance", "continuous-reliability", "agreement-uncertainty"}
    if "consensus" in text: keys |= {"latent-label-estimation", "consensus-rule", "consensus-result"}
    if "review" in text or "correction" in text or "adjudication" in text: keys |= {"correction-supersession", "review-plan", "review-issue", "adjudication"}
    if "export" in text or "provenance" in text or "version" in text: keys |= {"reference-acceptance", "reference-challenge-recall", "export-crosswalk"}
    if "document" in text or "ocr" in text: keys |= {"text-span-structure", "document-layout-table"}
    if "image" in text or "raster" in text: keys |= {"image-region-shape"}
    if "spatial" in text or "geometry" in text or "pointcloud" in text: keys |= {"geospatial", "three-d-pointcloud"}
    if "predictive" in text or "model" in text or "calibration" in text: keys |= {"weak-programmatic-label", "model-suggestion"}
    if "privacy" in text: keys |= {"privacy-safety"}
    if "workspace" in text or "pipeline" in text: keys |= {"dataset-membership-transform", "dataset-release", "dataset-product-boundary"}
    return sorted(f"module.annotation.{key}" for key in keys)


def library_bindings(source_ids: set[str]) -> list[dict[str, Any]]:
    direct = declared_product_libraries()
    evidence = sorted(source_ids)[:6]
    return [{
        "library_ref": ref, "relationship_to_product": "DECLARED_CONCRETE_BINDING" if ref in direct else "JUSTIFIED_NEIGHBOR_IMPORT_OR_OWNER",
        "semantic_module_refs": module_refs_for_library(ref), "evidence_refs": evidence,
        "downstream_product_refs": sorted(PRODUCTS),
        "downstream_contract_route": "DECLARED_PRODUCT_BINDING_UNRATIFIED" if ref in direct else "NEIGHBOR_IMPORT_CANDIDATE_UNRATIFIED",
        "refusal_reasons": ["OWNER_RATIFICATION_MISSING", "EXACT_CONTRACT_UNSELECTED", "QUALIFIED_IMPLEMENTATION_MISSING", "TWO_VERTICAL_ACCEPTANCE_MISSING"],
        "compiler_binding": "REFUSED", "completion_claim": False,
    } for ref in LIBRARIES]


def findings() -> list[dict[str, Any]]:
    rows = [{
        "finding_id": "finding.annotation.product.v1", "candidate_disposition": "RETAIN_ANNOTATION_OPERATIONS_BUT_NARROW_IMPORTED_OWNERS",
        "product_ref": "product.annotation_operations", "library_refs": sorted(declared_product_libraries()),
        "finding": "Retain project/task/annotation/review/agreement/consensus/adjudication/reference-release lifecycle while importing source truth, generic human work, statistics, modality carriers, privacy and downstream model/effect authority.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }, {
        "finding_id": "finding.annotation.dataset-curation-product.v1", "candidate_disposition": "RETAIN_DATASET_CURATION_WORKBENCH_WITH_EXACT_IMPORTED_OWNERS",
        "product_ref": "product.dataset_curation_workbench",
        "library_refs": ["library.pipeline.data_cut_algebra", "library.analytical_workspace.definition.compiler", "library.analytical_workspace.lifecycle.reducer"],
        "finding": "Retain purpose/membership, split/audit evidence, immutable edition, release and maintenance as an independent lifecycle while importing preparation, annotation, quality methods, rights authority, storage, publication service and model lifecycle.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }, {
        "finding_id": "finding.annotation.ground-truth-rename.v1", "candidate_disposition": "RENAME_GROUND_TRUTH_TO_ACCEPTED_REFERENCE_EDITION",
        "library_refs": ["library.cbv.annotation_store", "library.review.adjudication.reducer"],
        "finding": "Ground truth falsely suggests absolute truth; the portable object is an accepted, scoped, versioned, challengeable and recallable reference edition with named authority and evidence.",
        "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0,
    }]
    for i, (ref, rationale) in enumerate(VACANCIES, 1):
        rows.append({"finding_id": f"finding.annotation.library-vacancy.{i:02d}", "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED", "proposed_library_ref": ref, "library_refs": [], "finding": rationale, "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0})
    return rows


def bounded_context() -> dict[str, Any]:
    return {
        "slice_id": "slice.annotation-labeling-evaluation.v1", "retained_products": sorted(PRODUCTS),
        "inside_annotation_operations": ["annotation project/schema/instructions", "target selection and task sampling", "assignment and annotation occurrence", "review/correction", "agreement/consensus", "adjudication", "accepted reference edition and recall"],
        "inside_dataset_curation_workbench": ["purpose and population", "source admission and membership", "curation recipe decisions", "duplicate adjudication", "cohort coverage and partition design", "leakage/contamination audit", "annotation/rights binding", "documentation and immutable edition", "release maintenance and recall"],
        "imported_owners": ["source truth/content", "generic human work", "statistical inference", "modality carriers and geometry", "privacy/safety", "model lifecycle", "downstream decision/effect"],
        "non_collapse_summary": "source != target/selector != annotation occurrence; agreement != correctness; consensus != adjudication; accepted reference != absolute truth; annotation release != dataset release",
        "product_boundary_candidates": [
            {"product_ref": "product.annotation_operations", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
            {"product_ref": "product.dataset_curation_workbench", "status": "RETAIN_WITH_EXACT_IMPORTS_UNRATIFIED"},
        ],
        "status": "CANDIDATE_UNRATIFIED", "completion_claim": False,
    }


def build() -> dict[str, Any]:
    src = sources(); source_ids = {row["source_id"] for row in src}; mods = modules(); bindings = library_bindings(source_ids)
    axes = [{"library_ref": b["library_ref"], "axis": axis, "semantic_module_refs": b["semantic_module_refs"], "evidence_refs": b["evidence_refs"], "decision_candidate": "UNRESOLVED_RESEARCHED_CANDIDATE", "coordinate_answers": [], "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False} for b in bindings for axis in AXES]
    result = {"sources": src, "modules": mods, "laws": laws(), "methods": methods(), "experts": experts(), "innovations": innovations(), "libraries": bindings, "axes": axes, "findings": findings(), "context": bounded_context()}
    result["summary"] = {"slice_id": "slice.annotation-labeling-evaluation.v1", "as_of": AS_OF, "primary_or_official_sources": len(src), "semantic_modules": len(mods), "non_collapse_laws": len(LAW_STATEMENTS), "method_types": sum(map(len, METHOD_GROUPS.values())), "expert_learning_profiles": len(EXPERT_ROWS), "recent_innovations": len(INNOVATION_ROWS), "declared_product_libraries": len(declared_product_libraries()), "justified_neighbor_libraries": len(NEIGHBORS), "bound_libraries": len(LIBRARIES), "library_axis_decision_candidates": len(axes), "retained_products": 2, "candidate_new_products": 0, "candidate_new_library_vacancies": len(VACANCIES), "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0, "canonical_gaps_closed": 0, "completion_claim": False}
    return result


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "primary-sources.jsonl": "".join(canonical(r) + "\n" for r in built["sources"]),
        "semantic-modules.jsonl": "".join(canonical(r) + "\n" for r in built["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(r) + "\n" for r in built["laws"]),
        "annotation-labeling-method-taxonomy.jsonl": "".join(canonical(r) + "\n" for r in built["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(r) + "\n" for r in built["experts"]),
        "innovation-records.jsonl": "".join(canonical(r) + "\n" for r in built["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(r) + "\n" for r in built["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(r) + "\n" for r in built["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(r) + "\n" for r in built["findings"]),
        "bounded-context.json": json.dumps(built["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.annotation-labeling-evaluation-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items(): (HERE / name).write_text(value)
    s = build()["summary"]
    print(f"BUILD PASS annotation/labeling/evaluation semantic slice: {s['semantic_modules']} modules, {s['method_types']} methods, {s['bound_libraries']} libraries, {s['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__": raise SystemExit(main())
