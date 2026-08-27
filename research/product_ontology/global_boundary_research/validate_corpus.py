#!/usr/bin/env python3
"""Dependency-free semantic and referential validation for boundary research."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load_jsonl(name: str, errors: list[str]) -> list[dict[str, Any]]:
    path = HERE / name
    rows = []
    if not path.exists():
        errors.append(f"missing dataset {name}")
        return rows
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            errors.append(f"{name}:{line_number}: blank lines are forbidden")
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{name}:{line_number}: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{name}:{line_number}: record is not an object")
        else:
            rows.append(value)
    return rows


def count_external_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def validate_required(rows: list[dict[str, Any]], required: list[str], name: str, errors: list[str]) -> None:
    for line_number, row in enumerate(rows, 1):
        missing = [key for key in required if key not in row]
        if missing:
            errors.append(f"{name}:{line_number}: missing {missing}")


def main() -> int:
    errors: list[str] = []
    report = json.loads((HERE / "coverage-report.json").read_text(encoding="utf-8"))
    datasets: dict[str, list[dict[str, Any]]] = {}
    for name in sorted(key for key in report["counts"] if key.endswith(".jsonl")):
        datasets[name] = load_jsonl(name, errors)
        expected = report["counts"][name]
        if len(datasets[name]) != expected:
            errors.append(f"{name}: expected {expected} records, found {len(datasets[name])}")

    # Every dataset has a declared schema and each record has the required shape.
    for name, rows in datasets.items():
        schema_path = HERE / "schemas" / name.replace(".jsonl", ".schema.json")
        if not schema_path.exists():
            errors.append(f"missing schema for {name}")
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validate_required(rows, schema.get("required", []), name, errors)
        kind = schema.get("properties", {}).get("record_kind", {}).get("const")
        for line_number, row in enumerate(rows, 1):
            if kind and row.get("record_kind") != kind:
                errors.append(f"{name}:{line_number}: record_kind {row.get('record_kind')!r} != {kind!r}")

    # Global record IDs are deterministic, nonempty and unique.
    ids: dict[str, str] = {}
    for name, rows in datasets.items():
        for row in rows:
            ident = row.get("record_id")
            if not isinstance(ident, str) or not re.fullmatch(r"[a-z][a-z0-9_.]*", ident):
                errors.append(f"{name}: invalid record_id {ident!r}")
            elif ident in ids:
                errors.append(f"duplicate record_id {ident} in {ids[ident]} and {name}")
            else:
                ids[ident] = name

    candidates = datasets["product-archetypes.jsonl"]
    candidate_ids = {row["record_id"] for row in candidates}
    if len(candidates) < 40:
        errors.append("fewer than 40 product archetype/boundary candidates")
    if any(row.get("ratification") != "withheld" for row in candidates):
        errors.append("all boundary candidates must explicitly withhold ratification")
    if any(row.get("status") == "ratified" for row in candidates):
        errors.append("research corpus must not contain ratified product candidates")
    for row in candidates:
        modality = row.get("automation_modality", {})
        if modality.get("default_posture") != "DETERMINISTIC_CORE_ONLY":
            errors.append(f"{row['record_id']}: model/agent modality is not deterministic-core-first")
        if set(modality.get("per_use_site_override", [])) != {
            "PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED",
        }:
            errors.append(f"{row['record_id']}: automation modality postures are incomplete")
        if not modality.get("law") or not modality.get("fallback"):
            errors.append(f"{row['record_id']}: automation modality lacks authority or fallback law")
        construction_law = modality.get("research_and_construction_law", "")
        if not all(term in construction_law for term in ("vocabulary enumeration", "invariant", "source evidence", "provider qualification", "acceptance")):
            errors.append(f"{row['record_id']}: automation can substitute for required research/construction work")
        analytical_law = modality.get("analytical_method_law", "")
        if not all(term in analytical_law for term in ("predictive", "heuristic", "simulation", "optimization", "stochasticity")):
            errors.append(f"{row['record_id']}: non-agent analytical methods are not preserved as first-class methods")
        if not all(term in modality.get("fallback", "") for term in ("deterministic parsing", "typing", "authorization", "qualification", "evidence")):
            errors.append(f"{row['record_id']}: removing model/agent extensions does not preserve the deterministic core")
    expected_ranges = {
        "merge": range(0, 7), "defer": range(7, 13),
        "presumptive_product": range(13, 17), "strong_product": range(17, 21),
    }
    for row in candidates:
        evaluation = row["boundary_evaluation"]
        scores = evaluation["scores"]
        if set(scores) != {"user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"}:
            errors.append(f"{row['record_id']}: incomplete split-test scores")
        if any(value not in {0, 1, 2} for value in scores.values()):
            errors.append(f"{row['record_id']}: split-test scores must be 0..2")
        if sum(scores.values()) != evaluation["total"]:
            errors.append(f"{row['record_id']}: score total mismatch")
        if evaluation["total"] not in expected_ranges[evaluation["verdict"]]:
            errors.append(f"{row['record_id']}: verdict/score range mismatch")
        for source_id in row["evidence_ids"]:
            if source_id not in ids or ids[source_id] != "evidence.jsonl":
                errors.append(f"{row['record_id']}: unresolved evidence {source_id}")

    # The detailed lakehouse adjudication is authoritative for its propagated slice.
    # Global rollups may add context, but may not silently drop a product boundary,
    # rescore an axis, or detach the score from its exact evidence.
    lakehouse_path = ROOT / "research/product_ontology/adjudications/lakehouse/source.json"
    lakehouse = json.loads(lakehouse_path.read_text(encoding="utf-8"))
    lakehouse_decisions = {row["decision_id"]: row for row in lakehouse["boundary_decisions"]}
    lakehouse_evidence = {row["source_id"] for row in lakehouse["sources"]}
    required_lakehouse_bindings = {
        "candidate.product.lakehouse_experience": "decision.lakehouse.managed_experience",
        "candidate.product.catalog_commit": "decision.lakehouse.catalog",
        "candidate.product.managed_table_maintenance": "decision.lakehouse.maintenance",
        "candidate.product.data_sharing": "decision.lakehouse.sharing",
    }
    candidates_by_id = {row["record_id"]: row for row in candidates}
    for candidate_id, decision_id in required_lakehouse_bindings.items():
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"global corpus dropped adjudicated lakehouse boundary {candidate_id}")
            continue
        decision = lakehouse_decisions[decision_id]
        evaluation = candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/lakehouse/"
            f"boundary-decisions.jsonl#{decision_id}"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append(f"{candidate_id}: stale or missing lakehouse adjudication_ref")
        split = decision["split_test"]
        expected_scores = {axis: value["score"] for axis, value in split.items()}
        expected_evidence = {axis: value["evidence_refs"] for axis, value in split.items()}
        if evaluation.get("scores") != expected_scores:
            errors.append(f"{candidate_id}: scores drift from lakehouse adjudication")
        if evaluation.get("axis_evidence") != expected_evidence:
            errors.append(f"{candidate_id}: axis evidence drifts from lakehouse adjudication")
        for axis, evidence_refs in expected_evidence.items():
            for evidence_ref in evidence_refs:
                if evidence_ref not in lakehouse_evidence:
                    errors.append(f"{candidate_id}: {axis} has unresolved local evidence {evidence_ref}")

    # The movement adjudication has the same no-drift authority. In particular,
    # reverse ETL/activation may not disappear back into a generic pipeline label.
    movement_path = ROOT / "research/product_ontology/adjudications/movement/source.json"
    movement = json.loads(movement_path.read_text(encoding="utf-8"))
    movement_decisions = {row["decision_id"]: row for row in movement["boundary_decisions"]}
    movement_evidence = {row["source_id"] for row in movement["sources"]}
    required_movement_bindings = {
        "candidate.product.source_connectivity_control": "decision.movement.connectivity",
        "candidate.product.source_replication_cdc": "decision.movement.cdc",
        "candidate.product.ingestion_delivery": "decision.movement.ingestion",
        "candidate.product.pipeline_orchestration": "decision.movement.orchestration",
        "candidate.product.dataflow_execution": "decision.movement.dataflow",
        "candidate.product.batch_transform_build": "decision.movement.transform_build",
        "candidate.product.event_streaming": "decision.movement.event_streaming",
        "candidate.product.operational_activation": "decision.movement.activation",
    }
    for candidate_id, decision_id in required_movement_bindings.items():
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"global corpus dropped adjudicated movement boundary {candidate_id}")
            continue
        decision = movement_decisions[decision_id]
        evaluation = candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/movement/"
            f"boundary-decisions.jsonl#{decision_id}"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append(f"{candidate_id}: stale or missing movement adjudication_ref")
        split = decision["split_test"]
        expected_scores = {axis: value["score"] for axis, value in split.items()}
        expected_evidence = {axis: value["evidence_refs"] for axis, value in split.items()}
        if evaluation.get("scores") != expected_scores:
            errors.append(f"{candidate_id}: scores drift from movement adjudication")
        if evaluation.get("axis_evidence") != expected_evidence:
            errors.append(f"{candidate_id}: axis evidence drifts from movement adjudication")
        for axis, evidence_refs in expected_evidence.items():
            for evidence_ref in evidence_refs:
                if evidence_ref not in movement_evidence:
                    errors.append(f"{candidate_id}: {axis} has unresolved local evidence {evidence_ref}")

    connector_candidate = candidates_by_id.get("candidate.product.connector_brand_sku")
    connector_decision = movement_decisions["decision.movement.connector_sku"]
    if connector_candidate is None:
        errors.append("global corpus dropped connector-SKU reclassification trace")
    else:
        connector_evaluation = connector_candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/movement/"
            "boundary-decisions.jsonl#decision.movement.connector_sku"
        )
        if connector_evaluation.get("adjudication_ref") != expected_ref:
            errors.append("connector-SKU candidate lacks exact movement adjudication_ref")
        if connector_evaluation.get("adjudication_disposition") != connector_decision["disposition"]:
            errors.append("connector-SKU candidate lost provider-offer disposition")
        if connector_evaluation.get("verdict") != "merge":
            errors.append("connector-SKU candidate must remain merge/reclassify")

    # Governance semantics is a third no-drift authority. The split of glossary
    # from ontology and schema registry from data-contract registry is constitutional,
    # not an optional presentation choice.
    governance_path = ROOT / "research/product_ontology/adjudications/governance_semantics/source.json"
    governance = json.loads(governance_path.read_text(encoding="utf-8"))
    governance_decisions = {row["decision_id"]: row for row in governance["boundary_decisions"]}
    governance_evidence = {row["source_id"] for row in governance["sources"]}
    required_governance_bindings = {
        "candidate.product.metadata_discovery": "decision.governance.metadata_discovery",
        "candidate.product.business_glossary": "decision.governance.business_glossary",
        "candidate.product.ontology_knowledge_model": "decision.governance.ontology",
        "candidate.product.schema_registry": "decision.governance.schema_registry",
        "candidate.product.data_contract_registry": "decision.governance.data_contract",
        "candidate.product.master_data_governance": "decision.governance.master_data",
        "candidate.product.reference_data_governance": "decision.governance.reference_data",
        "candidate.product.lineage_provenance": "decision.governance.lineage",
        "candidate.product.data_quality_operations": "decision.governance.data_quality_operations",
        "candidate.product.reconciliation_control_operations": "decision.governance.reconciliation_control_operations",
        "candidate.product.data_use_policy": "decision.governance.policy",
        "candidate.product.data_product_publication": "decision.governance.publication",
        "candidate.product.data_marketplace": "decision.governance.marketplace",
    }
    for candidate_id, decision_id in required_governance_bindings.items():
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"global corpus dropped adjudicated governance boundary {candidate_id}")
            continue
        decision = governance_decisions[decision_id]
        evaluation = candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/governance_semantics/"
            f"boundary-decisions.jsonl#{decision_id}"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append(f"{candidate_id}: stale or missing governance adjudication_ref")
        split = decision["split_test"]
        expected_scores = {axis: value["score"] for axis, value in split.items()}
        expected_evidence = {axis: value["evidence_refs"] for axis, value in split.items()}
        if evaluation.get("scores") != expected_scores:
            errors.append(f"{candidate_id}: scores drift from governance adjudication")
        if evaluation.get("axis_evidence") != expected_evidence:
            errors.append(f"{candidate_id}: axis evidence drifts from governance adjudication")
        for axis, evidence_refs in expected_evidence.items():
            for evidence_ref in evidence_refs:
                if evidence_ref not in governance_evidence:
                    errors.append(f"{candidate_id}: {axis} has unresolved local evidence {evidence_ref}")
    if "candidate.product.glossary_ontology" in candidate_ids:
        errors.append("business glossary and formal ontology may not re-collapse into one product candidate")
    if "candidate.product.analytical_table" in candidate_ids:
        errors.append("analytical table semantic state must not reappear as a product candidate")

    # Analytical-method adjudication is the fourth no-drift authority. Method
    # labels that failed product tests may not be resurrected as global products.
    analytical_path = ROOT / "research/product_ontology/adjudications/analytical_methods/source.json"
    analytical = json.loads(analytical_path.read_text(encoding="utf-8"))
    analytical_decisions = {row["decision_id"]: row for row in analytical["boundary_decisions"]}
    analytical_evidence = {row["source_id"] for row in analytical["sources"]}
    analytical_artifacts = {row["artifact_id"] for row in analytical["artifacts"]}
    required_analytical_bindings = {
        "candidate.product.experimentation_platform": "decision.methods.experimentation_platform",
        "candidate.product.forecasting_workbench": "decision.methods.forecasting_workbench",
        "candidate.product.optimization_solver": "decision.methods.optimization_solver",
        "candidate.product.process_mining_workbench": "decision.methods.process_mining_workbench",
        "candidate.product.geospatial_workbench": "decision.methods.geospatial_workbench",
        "candidate.product.simulation_environment": "decision.methods.simulation_environment",
    }
    for candidate_id, decision_id in required_analytical_bindings.items():
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"global corpus dropped adjudicated analytical boundary {candidate_id}")
            continue
        decision = analytical_decisions[decision_id]
        evaluation = candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/analytical_methods/"
            f"boundary-decisions.jsonl#{decision_id}"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append(f"{candidate_id}: stale or missing analytical adjudication_ref")
        split = decision["split_test"]
        expected_scores = {axis: value["score"] for axis, value in split.items()}
        expected_evidence = {axis: value["evidence_refs"] for axis, value in split.items()}
        if evaluation.get("scores") != expected_scores:
            errors.append(f"{candidate_id}: scores drift from analytical adjudication")
        if evaluation.get("axis_evidence") != expected_evidence:
            errors.append(f"{candidate_id}: axis evidence drifts from analytical adjudication")
        for axis, evidence_refs in expected_evidence.items():
            for evidence_ref in evidence_refs:
                if evidence_ref not in analytical_evidence:
                    errors.append(f"{candidate_id}: {axis} has unresolved local evidence {evidence_ref}")
    forbidden_method_products = {
        "candidate.product.statistical_analysis", "candidate.product.causal_experimentation",
        "candidate.product.forecasting", "candidate.product.optimization",
        "candidate.product.anomaly_detection", "candidate.product.process_mining",
        "candidate.product.graph_analytics", "candidate.product.geospatial_analytics",
        "candidate.product.text_document_analytics", "candidate.product.media_signal_analytics",
        "candidate.product.simulation_scenario",
    }
    for candidate_id in sorted(forbidden_method_products & candidate_ids):
        errors.append(f"method label reappeared as a product after adjudication: {candidate_id}")

    # Model/decision adjudication is the fifth no-drift authority. It prevents
    # vector/feature, prediction/decision, evidence/approval and agent/authority
    # collapses from reappearing during global regeneration.
    model_path = ROOT / "research/product_ontology/adjudications/model_decision_serving/source.json"
    model_adjudication = json.loads(model_path.read_text(encoding="utf-8"))
    model_decisions = {row["decision_id"]: row for row in model_adjudication["boundary_decisions"]}
    model_evidence = {row["source_id"] for row in model_adjudication["sources"]}
    required_model_bindings = {
        "candidate.product.model_lifecycle": "decision.model.lifecycle",
        "candidate.product.feature_platform": "decision.model.feature_platform",
        "candidate.product.online_inference": "decision.model.online_inference",
        "candidate.product.model_assurance": "decision.model.assurance",
        "candidate.product.decision_automation": "decision.model.decision_automation",
        "candidate.product.optional_model_extension": "decision.model.optional_extension",
    }
    for candidate_id, decision_id in required_model_bindings.items():
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"global corpus dropped adjudicated model/decision boundary {candidate_id}")
            continue
        decision = model_decisions[decision_id]
        evaluation = candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/model_decision_serving/"
            f"boundary-decisions.jsonl#{decision_id}"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append(f"{candidate_id}: stale or missing model/decision adjudication_ref")
        split = decision["split_test"]
        expected_scores = {axis: value["score"] for axis, value in split.items()}
        expected_evidence = {axis: value["evidence_refs"] for axis, value in split.items()}
        if evaluation.get("scores") != expected_scores:
            errors.append(f"{candidate_id}: scores drift from model/decision adjudication")
        if evaluation.get("axis_evidence") != expected_evidence:
            errors.append(f"{candidate_id}: axis evidence drifts from model/decision adjudication")
        for axis, evidence_refs in expected_evidence.items():
            for evidence_ref in evidence_refs:
                if evidence_ref not in model_evidence:
                    errors.append(f"{candidate_id}: {axis} has unresolved local evidence {evidence_ref}")
    vector_candidate = candidates_by_id.get("candidate.product.vector_feature_serving")
    vector_decision = model_decisions["decision.model.vector_feature_split"]
    if vector_candidate is None:
        errors.append("global corpus dropped legacy vector/feature split trace")
    else:
        evaluation = vector_candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/model_decision_serving/"
            "boundary-decisions.jsonl#decision.model.vector_feature_split"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append("vector/feature umbrella lacks exact split adjudication_ref")
        if evaluation.get("adjudication_disposition") != vector_decision["disposition"]:
            errors.append("vector/feature umbrella lost split disposition")
        if evaluation.get("verdict") != "defer":
            errors.append("vector/feature umbrella must remain deferred after split")
    forbidden_model_products = {
        "candidate.product.model_registry", "candidate.product.training_runtime",
        "candidate.product.batch_inference", "candidate.product.vector_feature_platform",
        "candidate.product.ai_model_lifecycle", "candidate.product.ai_decisioning",
    }
    for candidate_id in sorted(forbidden_model_products & candidate_ids):
        errors.append(f"component/mode/AI-prefixed label reappeared as product: {candidate_id}")

    # Query/warehouse/search/protection is the newest no-drift authority for
    # query execution, virtualization, search visibility and the recovery/archive split.
    qwsp_path = ROOT / "research/product_ontology/adjudications/query_warehouse_search_protection/source.json"
    qwsp = json.loads(qwsp_path.read_text(encoding="utf-8"))
    qwsp_decisions = {row["decision_id"]: row for row in qwsp["boundary_decisions"]}
    qwsp_evidence = {row["source_id"] for row in qwsp["sources"]}
    required_qwsp_bindings = {
        "candidate.product.distributed_query": "decision.product.query",
        "candidate.product.warehouse_experience": "decision.product.warehouse",
        "candidate.product.virtual_data_access": "decision.product.virtual",
        "candidate.product.search_index_serving": "decision.product.search",
        "candidate.product.data_protection_recovery": "decision.product.recovery",
        "candidate.product.digital_preservation_archive": "decision.product.archive",
    }
    for candidate_id, decision_id in required_qwsp_bindings.items():
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"global corpus dropped adjudicated query/warehouse/search/protection boundary {candidate_id}")
            continue
        decision = qwsp_decisions[decision_id]
        evaluation = candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/query_warehouse_search_protection/"
            f"boundary-decisions.jsonl#{decision_id}"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append(f"{candidate_id}: stale or missing query/warehouse/search/protection adjudication_ref")
        split = decision["split_test"]
        expected_scores = {axis: value["score"] for axis, value in split.items()}
        expected_evidence = {axis: value["evidence_refs"] for axis, value in split.items()}
        if evaluation.get("scores") != expected_scores:
            errors.append(f"{candidate_id}: scores drift from query/warehouse/search/protection adjudication")
        if evaluation.get("axis_evidence") != expected_evidence:
            errors.append(f"{candidate_id}: axis evidence drifts from query/warehouse/search/protection adjudication")
        for axis, evidence_refs in expected_evidence.items():
            for evidence_ref in evidence_refs:
                if evidence_ref not in qwsp_evidence:
                    errors.append(f"{candidate_id}: {axis} has unresolved local evidence {evidence_ref}")

    legacy_qwsp = {
        "candidate.product.federated_query": ("decision.federation.capability", "merge"),
        "candidate.product.backup_restore_archive": ("decision.protection.archive_split", "defer"),
    }
    for candidate_id, (decision_id, expected_verdict) in legacy_qwsp.items():
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"global corpus dropped required legacy split trace {candidate_id}")
            continue
        decision = qwsp_decisions[decision_id]
        evaluation = candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/query_warehouse_search_protection/"
            f"boundary-decisions.jsonl#{decision_id}"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append(f"{candidate_id}: legacy split trace lacks exact adjudication_ref")
        if evaluation.get("adjudication_disposition") != decision["disposition"]:
            errors.append(f"{candidate_id}: legacy split trace lost disposition")
        if evaluation.get("verdict") != expected_verdict:
            errors.append(f"{candidate_id}: legacy split trace must remain {expected_verdict}")

    forbidden_qwsp_products = {
        "candidate.product.federated_query_engine",
        "candidate.product.operational_analytics",
        "candidate.product.realtime_analytics",
        "candidate.product.batch_analytics",
        "candidate.product.query_cache",
        "candidate.product.cache_service",
        "candidate.product.vector_search_product",
        "candidate.product.ai_search",
        "candidate.product.snapshot_backup",
        "candidate.product.worm_archive",
    }
    for candidate_id in sorted(forbidden_qwsp_products & candidate_ids):
        errors.append(f"capability/profile/mechanism/AI-prefixed label reappeared as product: {candidate_id}")

    # Semantic metrics/formulas is the no-drift authority for the governed
    # meaning/evaluation product and the legacy metric-store/query bundle.
    smf_path = ROOT / "research/product_ontology/adjudications/semantic_metrics_formulas/source.json"
    smf = json.loads(smf_path.read_text(encoding="utf-8"))
    smf_decisions = {row["decision_id"]: row for row in smf["boundary_decisions"]}
    smf_evidence = {row["source_id"] for row in smf["sources"]}
    semantic_candidate = candidates_by_id.get("candidate.product.semantic_metric")
    semantic_decision = smf_decisions["decision.smf.product"]
    if semantic_candidate is None:
        errors.append("global corpus dropped adjudicated semantic metric/formula boundary")
    else:
        evaluation = semantic_candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/semantic_metrics_formulas/"
            "boundary-decisions.jsonl#decision.smf.product"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append("semantic metric/formula product lacks exact adjudication_ref")
        split = semantic_decision["split_test"]
        expected_scores = {axis: value["score"] for axis, value in split.items()}
        expected_evidence = {axis: value["evidence_refs"] for axis, value in split.items()}
        if evaluation.get("scores") != expected_scores:
            errors.append("semantic metric/formula scores drift from adjudication")
        if evaluation.get("axis_evidence") != expected_evidence:
            errors.append("semantic metric/formula axis evidence drifts from adjudication")
        for axis, evidence_refs in expected_evidence.items():
            for evidence_ref in evidence_refs:
                if evidence_ref not in smf_evidence:
                    errors.append(f"semantic metric/formula {axis} has unresolved local evidence {evidence_ref}")

    metric_bundle = candidates_by_id.get("candidate.product.metric_store_bundle")
    metric_bundle_decision = smf_decisions["decision.smf.metric_store_bundle"]
    if metric_bundle is None:
        errors.append("global corpus dropped legacy metric-store/query bundle trace")
    else:
        evaluation = metric_bundle["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/semantic_metrics_formulas/"
            "boundary-decisions.jsonl#decision.smf.metric_store_bundle"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append("metric-store/query bundle lacks exact adjudication_ref")
        if evaluation.get("adjudication_disposition") != metric_bundle_decision["disposition"]:
            errors.append("metric-store/query bundle lost reclassification disposition")
        if evaluation.get("verdict") != "merge":
            errors.append("metric-store/query bundle must remain merge/reclassify")

    forbidden_smf_products = {
        "candidate.product.formula_engine", "candidate.product.metric_registry",
        "candidate.product.metric_observation_store", "candidate.product.semantic_query_gateway",
        "candidate.product.semantic_cache", "candidate.product.headless_bi",
        "candidate.product.ai_semantic_layer", "candidate.product.ai_metrics",
        "candidate.product.telemetry_metric_business_service",
    }
    for candidate_id in sorted(forbidden_smf_products & candidate_ids):
        errors.append(f"semantic component/packaging/AI-prefixed label reappeared as product: {candidate_id}")

    # Controlled collaboration, privacy-rights/retention, entity resolution and
    # assurance-case appraisal are independent products.  Clean-room mechanisms,
    # match scores, appraiser independence and governance-suite packaging are not.
    cpra_path = ROOT / "research/product_ontology/adjudications/collaboration_privacy_resolution_assurance/source.json"
    cpra = json.loads(cpra_path.read_text(encoding="utf-8"))
    cpra_decisions = {row["decision_id"]: row for row in cpra["boundary_decisions"]}
    cpra_evidence = {row["source_id"] for row in cpra["sources"]}
    required_cpra_bindings = {
        "candidate.product.clean_room": "decision.cpra.collaboration.product",
        "candidate.product.privacy_rights_retention": "decision.cpra.privacy.product",
        "candidate.product.entity_resolution": "decision.cpra.resolution.product",
        "candidate.product.independent_assurance": "decision.cpra.assurance.product",
    }
    for candidate_id, decision_id in required_cpra_bindings.items():
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"global corpus dropped CPRA product boundary {candidate_id}")
            continue
        decision = cpra_decisions[decision_id]
        evaluation = candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/collaboration_privacy_resolution_assurance/"
            f"boundary-decisions.jsonl#{decision_id}"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append(f"{candidate_id}: stale or missing CPRA adjudication_ref")
        split = decision["split_test"]
        expected_scores = {axis: value["score"] for axis, value in split.items()}
        expected_evidence = {axis: value["evidence_refs"] for axis, value in split.items()}
        if evaluation.get("scores") != expected_scores:
            errors.append(f"{candidate_id}: scores drift from CPRA adjudication")
        if evaluation.get("axis_evidence") != expected_evidence:
            errors.append(f"{candidate_id}: axis evidence drifts from CPRA adjudication")
        for axis, evidence_refs in expected_evidence.items():
            for evidence_ref in evidence_refs:
                if evidence_ref not in cpra_evidence:
                    errors.append(f"{candidate_id}: {axis} has unresolved local evidence {evidence_ref}")

    governance_bundle = candidates_by_id.get("candidate.product.all_governance_bundle")
    governance_bundle_decision = cpra_decisions["decision.cpra.unified_governance"]
    if governance_bundle is None:
        errors.append("global corpus dropped unified-governance suite trace")
    else:
        evaluation = governance_bundle["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/collaboration_privacy_resolution_assurance/"
            "boundary-decisions.jsonl#decision.cpra.unified_governance"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append("unified-governance bundle lacks exact CPRA adjudication_ref")
        if evaluation.get("adjudication_disposition") != governance_bundle_decision["disposition"]:
            errors.append("unified-governance bundle lost suite disposition")
        if evaluation.get("verdict") != "merge":
            errors.append("unified-governance bundle must remain merge/reclassify")

    forbidden_cpra_products = {
        "candidate.product.tee_clean_room", "candidate.product.mpc_clean_room",
        "candidate.product.differential_privacy_clean_room", "candidate.product.clean_room_agent",
        "candidate.product.match_score", "candidate.product.entity_cluster",
        "candidate.product.golden_record_resolution", "candidate.product.ai_entity_resolution",
        "candidate.product.automated_independent_assurance", "candidate.product.ai_assurance",
    }
    for candidate_id in sorted(forbidden_cpra_products & candidate_ids):
        errors.append(f"CPRA mechanism/method/property/AI-prefixed label reappeared as product: {candidate_id}")

    # Encoding/decoding is a representation-library/runtime boundary, not a
    # freestanding product merely because it can be deployed behind a service API.
    rcb_path = ROOT / "research/product_ontology/adjudications/representation_codec_boundary/source.json"
    rcb = json.loads(rcb_path.read_text(encoding="utf-8"))
    rcb_decisions = {row["decision_id"]: row for row in rcb["boundary_decisions"]}
    codec_candidate = candidates_by_id.get("candidate.product.codec_service")
    codec_decision = rcb_decisions["decision.rcb.codec_service"]
    if codec_candidate is None:
        errors.append("global corpus dropped codec-service reclassification trace")
    else:
        evaluation = codec_candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/representation_codec_boundary/"
            "boundary-decisions.jsonl#decision.rcb.codec_service"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append("codec-service candidate lacks exact representation adjudication_ref")
        if evaluation.get("adjudication_disposition") != codec_decision["disposition"]:
            errors.append("codec-service candidate lost library/runtime disposition")
        if evaluation.get("verdict") != "merge":
            errors.append("codec-service candidate must remain merge/reclassify")

    # Five operational analytical lifecycles survived the open-world inventory
    # challenge and a full product/DDD/library/compiler adjudication.  Promote
    # only those exact products; methods, kernels, generated proposals and
    # physical effects remain separately owned.
    ao_path = ROOT / "research/product_ontology/adjudications/analytical_operations/source.json"
    ao = json.loads(ao_path.read_text(encoding="utf-8"))
    ao_decisions = {row["decision_id"]: row for row in ao["boundary_decisions"]}
    ao_evidence = {row["source_id"] for row in ao["sources"]}
    required_ao_bindings = {
        "candidate.product.self_service_data_preparation": "decision.ao.preparation.product",
        "candidate.product.annotation_operations": "decision.ao.annotation.product",
        "candidate.product.document_processing_review": "decision.ao.document.product",
        "candidate.product.visual_inspection_operations": "decision.ao.inspection.product",
        "candidate.product.signal_condition_diagnostics": "decision.ao.condition.product",
    }
    for candidate_id, decision_id in required_ao_bindings.items():
        candidate = candidates_by_id.get(candidate_id)
        if candidate is None:
            errors.append(f"global corpus dropped analytical-operations product boundary {candidate_id}")
            continue
        decision = ao_decisions[decision_id]
        evaluation = candidate["boundary_evaluation"]
        expected_ref = (
            "research/product_ontology/adjudications/analytical_operations/"
            f"boundary-decisions.jsonl#{decision_id}"
        )
        if evaluation.get("adjudication_ref") != expected_ref:
            errors.append(f"{candidate_id}: stale or missing analytical-operations adjudication_ref")
        if evaluation.get("verdict") != "strong_product":
            errors.append(f"{candidate_id}: analytical-operations product must retain strong verdict")
        split = decision["split_test"]
        expected_scores = {axis: value["score"] for axis, value in split.items()}
        expected_evidence = {axis: value["evidence_refs"] for axis, value in split.items()}
        if evaluation.get("scores") != expected_scores:
            errors.append(f"{candidate_id}: scores drift from analytical-operations adjudication")
        if evaluation.get("axis_evidence") != expected_evidence:
            errors.append(f"{candidate_id}: axis evidence drifts from analytical-operations adjudication")
        for axis, evidence_refs in expected_evidence.items():
            for evidence_ref in evidence_refs:
                if evidence_ref not in ao_evidence:
                    errors.append(f"{candidate_id}: {axis} has unresolved local evidence {evidence_ref}")

    ao_product_refs = {
        decision["subject_ref"]
        for decision in ao_decisions.values()
        if decision["disposition"] == "strong_product_candidate"
    }
    ao_dossiers = {row["product_ref"]: row for row in ao["ddd_dossiers"]}
    if set(ao_dossiers) != ao_product_refs:
        errors.append("analytical-operations products do not have exactly one full DDD dossier each")
    required_ddd_fields = {
        "domain_vision_statement", "subdomain_classification", "bounded_context_boundary",
        "ubiquitous_language_policy", "context_map", "anti_corruption_layers",
        "published_language", "value_objects", "entities", "aggregates", "aggregate_roots",
        "aggregate_invariants", "commands", "domain_events", "refusal_failure_catalog",
        "domain_services", "application_services", "repositories", "factories",
        "specifications", "state_machine", "policies_and_reactions",
        "sagas_and_process_managers", "read_models_and_projections",
        "integration_event_policy", "concurrency_and_idempotency", "time_model",
        "event_storming_swimlanes", "nonfunctional_laws",
    }
    for product_ref, dossier in ao_dossiers.items():
        actual_fields = set(dossier.get("strategic_and_tactical_ddd", {}))
        if not required_ddd_fields <= actual_fields:
            errors.append(f"{product_ref}: incomplete strategic/tactical DDD dossier")
    if len(ao["libraries"]) != 88 or len(ao["binding_maps"]) != 88:
        errors.append("analytical-operations decomposition must retain 88 libraries and 88 compiler maps")
    if len(ao["binding_gaps"]) != 28:
        errors.append("analytical-operations compiler must preserve fourteen Dataset Curation and fourteen Image Analysis exact-library gaps")
    if any(row.get("portable") or row.get("qualified_implementation_count") for row in ao["offers"]):
        errors.append("analytical-operations provider offer became portable or qualified without evidence")

    forbidden_ao_products = {
        "candidate.product.ai_data_preparation", "candidate.product.ai_annotation",
        "candidate.product.ai_document_processing", "candidate.product.ai_visual_inspection",
        "candidate.product.ai_condition_monitoring", "candidate.product.ocr_model",
        "candidate.product.signal_filter", "candidate.product.machine_reject_effect",
    }
    for candidate_id in sorted(forbidden_ao_products & candidate_ids):
        errors.append(f"analytical method/kernel/effect/AI-prefixed label reappeared as product: {candidate_id}")

    # The current finite inventory is now fully adjudicated.  This says nothing
    # about open-world completeness; it only prevents template verdicts from
    # silently surviving inside this edition.
    for candidate_id, candidate in candidates_by_id.items():
        if not candidate["boundary_evaluation"].get("adjudication_ref"):
            errors.append(f"{candidate_id}: global candidate remains template-only and unadjudicated")

    # One user/job, service blueprint and lifecycle contract per candidate.
    for name in ("user-jobs-outcomes.jsonl", "service-blueprints.jsonl", "lifecycle.jsonl"):
        refs = Counter(row["candidate_id"] for row in datasets[name])
        if set(refs) != candidate_ids:
            errors.append(f"{name}: candidate coverage mismatch")
        if any(count != 1 for count in refs.values()):
            errors.append(f"{name}: expected exactly one record per candidate")

    # Full applicability of the ordered 110 truths, with state-specific justification.
    truth = json.loads((ROOT / "research/product_ontology/truth-contract.json").read_text(encoding="utf-8"))
    truth_ids = [item["id"] for group in truth["groups"] for item in group["items"]]
    expected_truth = [f"T{n:03d}" for n in range(1, 111)]
    if truth_ids != expected_truth:
        errors.append("upstream truth contract is not exactly ordered T001..T110")
    profiles: dict[str, list[dict[str, Any]]] = defaultdict(list)
    allowed_states = {"REQUIRED", "CONDITIONAL", "PROHIBITED", "INAPPLICABLE", "UNDETERMINED"}
    for row in datasets["truth-applicability.jsonl"]:
        profiles[row["candidate_id"]].append(row)
        state = row["applicability"]
        if state not in allowed_states:
            errors.append(f"{row['record_id']}: invalid applicability {state}")
        required_key = {"REQUIRED": "evidence_needed", "CONDITIONAL": "condition", "PROHIBITED": "law", "INAPPLICABLE": "reason", "UNDETERMINED": "owner"}.get(state)
        if required_key and not row.get(required_key):
            errors.append(f"{row['record_id']}: {state} missing {required_key}")
    if set(profiles) != candidate_ids:
        errors.append("truth applicability candidate coverage mismatch")
    for candidate_id, rows in profiles.items():
        actual = [row["truth_id"] for row in rows]
        if actual != expected_truth:
            errors.append(f"{candidate_id}: truth profile must be exactly ordered T001..T110")
    if not any(row["applicability"] == "PROHIBITED" for row in datasets["truth-applicability.jsonl"]):
        errors.append("truth corpus must exercise PROHIBITED applicability")
    if not any(row["applicability"] == "INAPPLICABLE" for row in datasets["truth-applicability.jsonl"]):
        errors.append("truth corpus must exercise INAPPLICABLE applicability")

    obligations = datasets["obligations.jsonl"]
    if len(obligations) < 100:
        errors.append("fewer than 100 obligations/decision points")
    truth_obligations = {row.get("truth_id") for row in obligations if row.get("truth_id")}
    if truth_obligations != set(expected_truth):
        errors.append("obligations do not cover all truth dimensions")
    required_categories = {"adoption", "operation", "support", "slo", "security", "commercial", "exit"}
    actual_categories = {row["obligation_category"] for row in obligations}
    if not required_categories <= actual_categories:
        errors.append(f"missing obligation categories {sorted(required_categories - actual_categories)}")

    # Evidence and innovation floors.
    evidence = datasets["evidence.jsonl"]
    if len(evidence) < 50:
        errors.append("fewer than 50 evidence sources")
    if sum(row.get("authority") == "primary_or_authoritative" for row in evidence) < 50:
        errors.append("fewer than 50 primary/authoritative evidence sources")
    required_evidence_domains = {
        "product_service_lifecycle_and_assurance", "cloud_native_operator_contracts",
        "interoperability_and_portability", "data_product_and_platform_literature",
        "specialist_implementation_evidence", "enterprise_adoption_and_operations",
    }
    actual_evidence_domains = {domain for row in evidence for domain in row.get("evidence_domains", [])}
    if not required_evidence_domains <= actual_evidence_domains:
        errors.append(f"missing evidence domains {sorted(required_evidence_domains - actual_evidence_domains)}")
    if len({row["uri"] for row in evidence}) != len(evidence):
        errors.append("evidence URIs must be unique")
    for row in evidence:
        if not row["uri"].startswith("https://"):
            errors.append(f"{row['record_id']}: evidence URI must be HTTPS")
        if row["retrieved_at"] != "2026-08-26":
            errors.append(f"{row['record_id']}: retrieval date drift")
    innovations = datasets["innovations.jsonl"]
    if len(innovations) < 20:
        errors.append("fewer than 20 non-LLM innovations")
    for row in innovations:
        if not row.get("non_llm") or not 2021 <= row.get("year", 0) <= 2026:
            errors.append(f"{row['record_id']}: innovation must be non-LLM and dated 2021..2026")
        for source_id in row["source_ids"]:
            if source_id not in ids or ids[source_id] != "evidence.jsonl":
                errors.append(f"{row['record_id']}: unresolved source {source_id}")

    # Typed imports preserve context/library/provider separation.
    imports = datasets["capability-imports.jsonl"]
    import_counts = Counter(row["candidate_id"] for row in imports)
    if set(import_counts) != candidate_ids or any(count < 2 for count in import_counts.values()):
        errors.append("every candidate needs at least two typed capability imports")
    packaged = datasets["packaged-elements.jsonl"]
    packaged_kinds = Counter(row["element_kind"] for row in packaged)
    if not {"context", "library", "provider"} <= set(packaged_kinds):
        errors.append("packaged elements must include context, library and provider inputs")
    if any(row["product_status"] != "not_a_product_by_origin" for row in packaged):
        errors.append("context/library/provider origin must never imply product status")
    packaged_by_path = Counter(row["upstream_ref"].rsplit(":", 1)[0] for row in packaged)
    canonical_library_path = "research/domain_atlas/compiler/library_registry/library-contributions.jsonl"
    canonical_provider_path = "research/domain_atlas/compiler/provider_target_registry/concrete-offers.jsonl"
    if packaged_by_path[canonical_library_path] != count_external_jsonl(ROOT / canonical_library_path):
        errors.append("canonical compiler library registry is not fully represented as packaged library inputs")
    if packaged_by_path[canonical_provider_path] != count_external_jsonl(ROOT / canonical_provider_path):
        errors.append("canonical provider-target offers are not fully represented as packaged provider inputs")

    # Industry packs are vertical compositions, never horizontal candidates.
    packs = datasets["industry-solution-packs.jsonl"]
    if any(row.get("horizontal_product") is not False for row in packs):
        errors.append("industry packs must explicitly be non-horizontal products")
    for row in packs:
        for candidate_id in row["composes_candidate_ids"]:
            if candidate_id not in candidate_ids:
                errors.append(f"{row['record_id']}: unresolved composed candidate {candidate_id}")
        for method_ref in row.get("method_contract_refs", []):
            if method_ref not in analytical_artifacts:
                errors.append(f"{row['record_id']}: unresolved analytical method contract {method_ref}")
        if not row.get("method_contract_refs"):
            errors.append(f"{row['record_id']}: vertical pack lacks explicit analytical method contracts")
        if row.get("method_adjudication_ref") != "research/product_ontology/adjudications/analytical_methods/registry.jsonl":
            errors.append(f"{row['record_id']}: stale analytical method adjudication reference")
    if any("industry" in row["record_id"] for row in candidates):
        errors.append("horizontal candidate IDs must not branch by industry")

    # Cross-record references for substitution and incompatibility.
    for row in datasets["substitutions.jsonl"]:
        if row["candidate_id"] not in candidate_ids:
            errors.append(f"{row['record_id']}: unresolved candidate")
        if len(row["alternatives"]) < 2:
            errors.append(f"{row['record_id']}: needs at least two substitute implementations")
    for row in datasets["incompatibilities.jsonl"]:
        for field in ("left_candidate_id", "right_candidate_id"):
            if row[field] not in candidate_ids:
                errors.append(f"{row['record_id']}: unresolved {field}")

    # Upstream inventory must cover every universe output and remain hash-current.
    inventory = {row["path"]: row for row in datasets["upstream-inventory.jsonl"]}
    universe_files = sorted(
        p for p in (ROOT / "research/domain_atlas/universes").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )
    compiler_files = sorted(
        p for p in (ROOT / "research/domain_atlas/compiler").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )
    composition_files = sorted(
        p for p in (ROOT / "research/product_ontology/composition_pilots").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )
    for path in [*universe_files, *compiler_files, *composition_files]:
        rel = str(path.relative_to(ROOT))
        if rel not in inventory:
            errors.append(f"upstream inventory misses {rel}")
    for rel, row in inventory.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"inventory path missing {rel}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            errors.append(f"inventory hash stale {rel}")

    # Blocking list must be honest and tied to all four requested gap classes.
    gaps = datasets["gaps.jsonl"]
    gap_classes = {row["gap_class"] for row in gaps}
    if not {"context", "library", "provider", "compiler"} <= gap_classes:
        errors.append("cannot_ratify_until must include context, library, provider and compiler gaps")
    if report.get("completion_claim") is not False or report.get("status") != "research_candidate_not_ratified":
        errors.append("coverage report must withhold completion and ratification")

    # Generator check proves committed JSONL/schema/report files are deterministic and fresh.
    result = subprocess.run([sys.executable, str(HERE / "build_corpus.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        errors.append("deterministic generator check failed: " + (result.stdout + result.stderr).strip())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    verdicts = Counter(row["boundary_evaluation"]["verdict"] for row in candidates)
    states = Counter(row["applicability"] for row in datasets["truth-applicability.jsonl"])
    print(
        "PASS global product-boundary research: "
        f"{len(candidates)} boundary candidates; {len(obligations)} obligations/decisions; "
        f"{len(evidence)} sources; {len(innovations)} non-LLM innovations; "
        f"{len(datasets['truth-applicability.jsonl'])} truth applicability decisions; "
        f"{len(packaged)} packaged context/library/provider inputs; "
        f"{len(datasets['upstream-inventory.jsonl'])} upstream artifacts inventoried; "
        f"verdicts={dict(sorted(verdicts.items()))}; applicability={dict(sorted(states.items()))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
