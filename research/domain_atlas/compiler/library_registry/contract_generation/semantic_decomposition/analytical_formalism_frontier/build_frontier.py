#!/usr/bin/env python3
"""Build a lossless retained-product x analytical-formalism research frontier."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
PRODUCT_ROOT = SEM.parents[4] / "product_ontology"
AS_OF = "2026-08-27"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slice_universes() -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for directory in sorted(SEM.glob("*_semantic_slice")):
        builders = sorted(directory.glob("build_*_semantic_slice.py"))
        if len(builders) != 1:
            continue
        spec = importlib.util.spec_from_file_location(f"frontier_{directory.name}", builders[0])
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result[directory.name] = set(module.LIBRARIES)
    return result


def product_refs() -> set[str]:
    return {row["product_ref"] for row in load_jsonl(PRODUCT_ROOT / "qualification_program/product-qualification-programs.jsonl")}


CLUSTERS = [
    ("process_object_centric", ["product.process_mining_workbench"], "process_analytics_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Event/OCED/case/object/state projections, discovery, conformance and performance."),
    ("optimization_simulation_queueing", ["product.optimization_solver", "product.simulation_environment"], "operations_research_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Decision models, optimization, heuristics, infeasibility, simulation/V&V and queueing seams."),
    ("predictive_modeling_scoring_assurance", ["product.feature_platform", "product.model_lifecycle", "product.online_inference", "product.model_assurance"], "predictive_analytics_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Study/target/feature, model families, training, scoring, assurance and lifecycle."),
    ("causal_experimentation", ["product.experimentation_platform"], "causal_inference_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Interventions, estimands, assignment/exposure, identification, estimation and sensitivity."),
    ("geospatial", ["product.geospatial_workbench"], "geospatial_analytics_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Features, observations, CRS, geometry/topology, coverages, networks, trajectories and spatial statistics."),
    ("document_text_extraction", ["product.document_processing_review"], "document_processing_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Carrier/rendition/text/OCR/layout/content graph/extraction/review/release."),
    ("signal_condition_event_history", ["product.signal_condition_diagnostics"], "signal_condition_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Measurement, signals, anomaly/change, survival, prognosis, diagnosis and evidence handoff."),
    ("forecasting_planning", ["product.forecasting_workbench", "product.integrated_planning_workbench"], "forecasting_planning_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Two non-collapsible products: forecasting owns uncertain future estimates and their evaluation/publication; integrated planning owns editioned scenarios, alternatives, reconciliation, approval, publication and replanning while importing methods, vertical meaning, authority and execution."),
    ("graph_network_knowledge", ["product.ontology_knowledge_model", "product.graph_analysis_workbench"], "graph_network_knowledge_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Graph identity, property/knowledge graphs, traversal, paths, centrality, communities, semirings, inference and release; ontology governance and the analysis workbench remain independent product lifecycles sharing only explicit formalism imports."),
    ("visual_image_inspection", ["product.image_analysis_workbench", "product.visual_inspection_operations"], "visual_image_inspection_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Image-analysis projects/workspaces/recipes/results and inspection plans/recipes/runs/review/disposition remain separate products while importing common image semantics and methods."),
    ("quality_reconciliation_controls", ["product.data_quality_operations", "product.reconciliation_control_operations"], "quality_reconciliation_controls_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Quality requirements/metrics/rules, profiling, anomaly, defects, repair, reconciliation, controls, waiver and certification."),
    ("search_information_retrieval", ["product.search_index_service", "product.metadata_discovery"], "search_information_retrieval_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Search index schemas/analyzers, mutation generations, visibility cuts, lexical/structured/spatial/vector/hybrid retrieval, ranking/results/evaluation remain separate from metadata acquisition, assertions/conflicts, federation, coverage, projections and browse lifecycle."),
    ("bi_visualization_metrics", ["product.bi_reporting", "product.embedded_analytics", "product.semantic_metric_formula_service"], "bi_visualization_metrics_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Measures/dimensions/formulas, semantic queries, visual encodings, interaction, dashboards, reports, subscriptions and exports."),
    ("entity_resolution_mastering", ["product.entity_resolution", "product.master_data_governance", "product.reference_data_governance"], "entity_resolution_mastering_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Source occurrences, identifiers, normalization, blocking, comparison, pair decisions, clusters, uncertainty, review and reversal; master identity/authority/survivorship and reference concept/code/set/mapping lifecycles remain three independent retained product boundaries sharing only explicit semantic imports."),
    ("annotation_labeling_evaluation", ["product.annotation_operations", "product.dataset_curation_workbench"], "annotation_labeling_evaluation_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Two non-collapsible products: Annotation Operations owns project/task/annotation/review/adjudication/reference editions; Dataset Curation owns purpose/membership, split/audit evidence, immutable editions, release and maintenance while importing preparation, annotation, quality methods, rights, storage, publication and model lifecycle."),
    ("general_statistical_inference", ["product.analytical_notebook"], "statistical_inference_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Population/sample, estimands, descriptive/inferential statistics, tests, resampling, multiplicity, uncertainty and reproducible study artifacts."),
    ("query_olap_warehouse", ["product.query_execution_service", "product.managed_warehouse_experience", "product.managed_lakehouse_experience", "product.virtual_data_access"], "query_olap_warehouse_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Relational/multidimensional semantics, planning, execution, transactions, materialization, federation and query evidence."),
    ("data_preparation_profiling", ["product.self_service_data_preparation"], "data_preparation_profiling_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Immutable data-cut admission, interactive project and view state, typed recipe authoring and reversible history, preview/replay/diff and prepared-output handoff; profiling remains reusable scoped evidence, while quality authority and deployed batch execution remain outside the product."),
    ("decision_automation_assurance", ["product.decision_automation", "product.assurance_case_appraisal"], "decision_automation_assurance_semantic_slice", "SLICE_ENCODED_UNRATIFIED", "Decision requirements/models/tables/policies, analysis, invocation, total results, traces and proposals remain distinct from authorization/effects; assurance claims, arguments, defeaters, evidence appraisal, bounded verdicts and reliance form a second independent product lifecycle."),
]


# Candidate semantic prerequisites between research quotients. These are not product runtime
# dependencies and do not ratify either endpoint. A mandatory foundation means the consumer's
# semantic slice would otherwise have to redefine the prerequisite question. A conditional import
# is required only when the named method/profile is selected by intent.
DEPENDENCIES = [
    ("general_statistical_inference", "forecasting_planning", "MANDATORY_SEMANTIC_FOUNDATION", "Forecast evaluation, intervals and model comparison require explicit sampling, estimand and uncertainty semantics."),
    ("signal_condition_event_history", "forecasting_planning", "MANDATORY_SEMANTIC_FOUNDATION", "Forecasting over indexed observations requires an explicit time-series cut, clock, support, gap and revision model."),
    ("general_statistical_inference", "quality_reconciliation_controls", "MANDATORY_SEMANTIC_FOUNDATION", "Sampling claims, baselines, distribution comparisons and control limits require statistical population and uncertainty semantics."),
    ("signal_condition_event_history", "quality_reconciliation_controls", "CONDITIONAL_METHOD_IMPORT", "Anomaly, change-point and temporal baseline controls import signal semantics only when those control methods are selected."),
    ("general_statistical_inference", "visual_image_inspection", "MANDATORY_SEMANTIC_FOUNDATION", "Inspection accuracy, sampling, uncertainty and acceptance evidence require explicit statistical claim semantics."),
    ("signal_condition_event_history", "visual_image_inspection", "CONDITIONAL_METHOD_IMPORT", "Image acquisition imports measurement and calibration semantics when pixel values are treated as observations."),
    ("geospatial", "visual_image_inspection", "CONDITIONAL_METHOD_IMPORT", "Inspection imports spatial reference, geometry or topology semantics only for spatially referenced imagery and results."),
    ("general_statistical_inference", "predictive_modeling_scoring_assurance", "MANDATORY_SEMANTIC_FOUNDATION", "Training/evaluation claims require population, sampling, estimation and uncertainty semantics distinct from model execution."),
    ("annotation_labeling_evaluation", "predictive_modeling_scoring_assurance", "CONDITIONAL_METHOD_IMPORT", "Supervised model work imports label-edition and adjudication semantics when labels are used."),
    ("general_statistical_inference", "causal_experimentation", "MANDATORY_SEMANTIC_FOUNDATION", "Causal estimation imports sampling, estimation and uncertainty while retaining separate identification semantics."),
    ("general_statistical_inference", "signal_condition_event_history", "MANDATORY_SEMANTIC_FOUNDATION", "Signal estimates, anomaly baselines and event-history estimators require explicit statistical claim and uncertainty semantics."),
    ("general_statistical_inference", "geospatial", "CONDITIONAL_METHOD_IMPORT", "Spatial statistics imports general statistical semantics but geometry, topology and reference systems do not."),
    ("general_statistical_inference", "process_object_centric", "CONDITIONAL_METHOD_IMPORT", "Process performance and inference import statistics; event/object semantics and conformance need not."),
    ("general_statistical_inference", "annotation_labeling_evaluation", "MANDATORY_SEMANTIC_FOUNDATION", "Agreement, sampling and evaluation claims require population, estimator and uncertainty semantics."),
    ("general_statistical_inference", "search_information_retrieval", "CONDITIONAL_METHOD_IMPORT", "Retrieval evaluation imports sampling, estimands and uncertainty; indexing and lexical semantics do not."),
    ("document_text_extraction", "search_information_retrieval", "CONDITIONAL_METHOD_IMPORT", "Document identity, extracted text and provenance are imported only for document-derived corpora."),
    ("graph_network_knowledge", "search_information_retrieval", "CONDITIONAL_METHOD_IMPORT", "Graph traversal or graph ranking is imported only for graph-backed retrieval."),
    ("query_olap_warehouse", "bi_visualization_metrics", "MANDATORY_SEMANTIC_FOUNDATION", "Semantic queries and report cuts require relation, grain, grouping, ordering and result semantics."),
    ("general_statistical_inference", "bi_visualization_metrics", "CONDITIONAL_METHOD_IMPORT", "Uncertainty displays and statistical measures import inference semantics; ordinary additive measures need not."),
    ("query_olap_warehouse", "data_preparation_profiling", "MANDATORY_SEMANTIC_FOUNDATION", "Join, projection, grouping, ordering and materialization recipes require relational and result semantics."),
    ("general_statistical_inference", "data_preparation_profiling", "CONDITIONAL_METHOD_IMPORT", "Sampling and statistical profiling import inference semantics; parsing and shaping need not."),
    ("entity_resolution_mastering", "graph_network_knowledge", "CONDITIONAL_METHOD_IMPORT", "Knowledge releases import mastered identity only when enterprise entities are reconciled across sources."),
    ("graph_network_knowledge", "entity_resolution_mastering", "CONDITIONAL_METHOD_IMPORT", "Graph clustering and link evidence are optional match methods, not identity authority."),
    ("causal_experimentation", "decision_automation_assurance", "CONDITIONAL_METHOD_IMPORT", "A decision may import a causal claim, but the claim does not authorize the decision or effect."),
    ("optimization_simulation_queueing", "decision_automation_assurance", "CONDITIONAL_METHOD_IMPORT", "A decision may import an optimization proposal, but feasibility or optimality does not authorize an effect."),
]


def dependency_rows(cluster_ids: set[str]) -> list[dict[str, Any]]:
    rows = []
    for prerequisite, consumer, kind, rationale in DEPENDENCIES:
        assert prerequisite in cluster_ids and consumer in cluster_ids
        rows.append({
            "record_kind": "analytical_formalism_dependency_candidate",
            "dependency_ref": f"dependency.formalism.{prerequisite}.to.{consumer}",
            "prerequisite_cluster_ref": f"formalism.{prerequisite}",
            "consumer_cluster_ref": f"formalism.{consumer}",
            "dependency_kind": kind,
            "rationale": rationale,
            "non_collapse_law": "Importing a prerequisite semantic proposition does not transfer ownership, authorize an effect, prove applicability or merge the bounded contexts.",
            "research_status": "CANDIDATE_UNRATIFIED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
    return sorted(rows, key=lambda row: row["dependency_ref"])


def mandatory_waves(cluster_ids: set[str], rows: list[dict[str, Any]]) -> dict[str, int]:
    incoming = {f"formalism.{cluster_id}": set() for cluster_id in cluster_ids}
    for row in rows:
        if row["dependency_kind"] == "MANDATORY_SEMANTIC_FOUNDATION":
            incoming[row["consumer_cluster_ref"]].add(row["prerequisite_cluster_ref"])
    waves: dict[str, int] = {}
    remaining = set(incoming)
    while remaining:
        ready = sorted(node for node in remaining if incoming[node] <= waves.keys())
        assert ready, "mandatory formalism dependency cycle"
        for node in ready:
            waves[node] = 0 if not incoming[node] else 1 + max(waves[parent] for parent in incoming[node])
            remaining.remove(node)
    return waves


def build() -> dict[str, Any]:
    slices = slice_universes()
    retained = product_refs()
    subject_rows = load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")
    refs_by_product = {ref: set() for ref in retained}
    subjects_by_product = {ref: set() for ref in retained}
    for row in subject_rows:
        if row["product_ref"] not in retained:
            continue
        subjects_by_product[row["product_ref"]].add(row["subject_ref"])
        refs_by_product[row["product_ref"]].update(edge["concrete_library_ref"] for edge in row["concrete_bindings"])

    products = []
    for product in sorted(retained):
        concrete = refs_by_product[product]
        overlaps = {name: sorted(concrete & universe) for name, universe in slices.items() if concrete & universe}
        covered = set().union(*(set(values) for values in overlaps.values())) if overlaps else set()
        products.append({
            "record_kind": "product_formalism_structural_coverage",
            "product_ref": product,
            "subject_refs": sorted(subjects_by_product[product]),
            "concrete_library_refs": sorted(concrete),
            "semantic_slice_overlaps": overlaps,
            "covered_concrete_library_refs": sorted(covered),
            "uncovered_concrete_library_refs": sorted(concrete - covered),
            "coverage_ratio_bps": (10000 * len(covered) // len(concrete)) if concrete else 0,
            "interpretation_limit": "Structural overlap does not prove product semantics, applicability, ownership, exact contracts, implementation qualification or product readiness.",
            "compiler_binding": "REFUSED",
            "completion_claim": False,
        })

    cluster_ids = {cluster_id for cluster_id, *_ in CLUSTERS}
    dependencies = dependency_rows(cluster_ids)
    waves = mandatory_waves(cluster_ids, dependencies)
    mandatory_in = {f"formalism.{cluster_id}": [] for cluster_id in cluster_ids}
    conditional_in = {f"formalism.{cluster_id}": [] for cluster_id in cluster_ids}
    mandatory_downstream = {f"formalism.{cluster_id}": [] for cluster_id in cluster_ids}
    conditional_downstream = {f"formalism.{cluster_id}": [] for cluster_id in cluster_ids}
    for edge in dependencies:
        target = mandatory_in if edge["dependency_kind"] == "MANDATORY_SEMANTIC_FOUNDATION" else conditional_in
        target[edge["consumer_cluster_ref"]].append(edge["prerequisite_cluster_ref"])
        downstream_target = mandatory_downstream if edge["dependency_kind"] == "MANDATORY_SEMANTIC_FOUNDATION" else conditional_downstream
        downstream_target[edge["prerequisite_cluster_ref"]].append(edge["consumer_cluster_ref"])

    cluster_rows = []
    clustered_products: set[str] = set()
    for cluster_id, product_list, package, status, question in CLUSTERS:
        assert set(product_list) <= retained
        clustered_products.update(product_list)
        members = sorted({ref for product in product_list for ref in refs_by_product[product]})
        covered = sorted(set().union(*(slices.get(package, set()) & refs_by_product[product] for product in product_list))) if package else []
        cluster_ref = f"formalism.{cluster_id}"
        visible_fanout = sum(len(refs_by_product[p]) for p in product_list)
        mandatory_dependents = sorted(set(mandatory_downstream[cluster_ref]))
        conditional_dependents = sorted(set(conditional_downstream[cluster_ref]))
        all_dependents = sorted(set(mandatory_dependents) | set(conditional_dependents))
        foundation_fanout = len(all_dependents)
        cluster_rows.append({
            "record_kind": "analytical_formalism_frontier_cluster",
            "cluster_id": cluster_ref, "product_refs": product_list,
            "declared_concrete_library_refs": members,
            "semantic_slice_package": package, "slice_covered_product_library_refs": covered,
            "research_status": status, "owned_question_scope": question,
            "next_operation": "CHALLENGE_EXISTING_SLICE_AND_ROUTE_OWNER_DECISIONS" if package else "DERIVE_EXACT_UNIVERSE_AND_EVIDENCE_BACKED_SEMANTIC_SLICE",
            "visible_product_library_fanout": visible_fanout,
            "mandatory_prerequisite_cluster_refs": sorted(mandatory_in[cluster_ref]),
            "conditional_import_cluster_refs": sorted(conditional_in[cluster_ref]),
            "mandatory_dependent_cluster_refs": mandatory_dependents,
            "conditional_dependent_cluster_refs": conditional_dependents,
            "dependent_cluster_refs": all_dependents,
            "foundation_fanout": foundation_fanout,
            "mandatory_research_wave": waves[cluster_ref],
            "priority_score": visible_fanout + 40 * len(mandatory_dependents) + 10 * len(conditional_dependents) + (100 if status == "OPEN_HIGH_PRIORITY" else 50 if status == "OPEN_MEDIUM_PRIORITY" else 0),
            "priority_interpretation": "Research heuristic combining visible product-library fanout, mandatory semantic dependents at weight 40 and conditional method dependents at weight 10; not readiness, authority or closure.",
            "canonical_gaps_closed": 0, "completion_claim": False,
        })

    summary = {
        "program_id": "program.analytical-formalism-frontier.v1", "as_of": AS_OF,
        "retained_products": len(retained), "live_semantic_slices": len(slices),
        "slice_library_union": len(set().union(*slices.values())),
        "product_formalism_coverage_rows": len(products), "frontier_clusters": len(cluster_rows),
        "formalism_dependency_candidates": len(dependencies),
        "mandatory_semantic_foundations": sum(row["dependency_kind"] == "MANDATORY_SEMANTIC_FOUNDATION" for row in dependencies),
        "conditional_method_imports": sum(row["dependency_kind"] == "CONDITIONAL_METHOD_IMPORT" for row in dependencies),
        "maximum_mandatory_research_wave": max(waves.values()),
        "highest_foundation_fanout_cluster_refs": sorted(
            (row["cluster_id"] for row in cluster_rows if row["foundation_fanout"] == max(item["foundation_fanout"] for item in cluster_rows))
        ),
        "encoded_unratified_clusters": sum(row["research_status"] == "SLICE_ENCODED_UNRATIFIED" for row in cluster_rows),
        "open_high_priority_clusters": sum(row["research_status"] == "OPEN_HIGH_PRIORITY" for row in cluster_rows),
        "open_medium_priority_clusters": sum(row["research_status"] == "OPEN_MEDIUM_PRIORITY" for row in cluster_rows),
        "products_represented_in_formalism_clusters": len(clustered_products),
        "products_not_yet_assigned_to_formalism_cluster": sorted(retained - clustered_products),
        "products_with_full_structural_slice_overlap": sum(bool(row["concrete_library_refs"]) and not row["uncovered_concrete_library_refs"] for row in products),
        "products_with_zero_structural_slice_overlap": sum(not row["covered_concrete_library_refs"] for row in products),
        "owner_decisions": 0, "canonical_gaps_closed": 0, "completion_claim": False,
    }
    return {
        "products": products,
        "clusters": sorted(cluster_rows, key=lambda row: (row["mandatory_research_wave"], -row["priority_score"], row["cluster_id"])),
        "dependencies": dependencies,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "product-formalism-coverage.jsonl": "".join(canonical(row) + "\n" for row in built["products"]),
        "formalism-frontier-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "formalism-dependency-graph.jsonl": "".join(canonical(row) + "\n" for row in built["dependencies"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.analytical-formalism-frontier.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    summary = build()["summary"]
    print(f"BUILD PASS analytical formalism frontier: {summary['retained_products']} products, {summary['live_semantic_slices']} slices and {summary['frontier_clusters']} quotient clusters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
