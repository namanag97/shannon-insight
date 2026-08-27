#!/usr/bin/env python3
"""Regenerate an honest coverage baseline from the inherited research corpus."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / "SAN_DATA_ANALYTICS_GPT_PRO_HANDOFF_2026-08-12/current_work/analytics_landscape"
HERE = Path(__file__).resolve().parent


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def line_count(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def main() -> int:
    knowledge = load(LEGACY / "analytics_knowledge_base.json")
    taxonomy = load(LEGACY / "analytics_type_taxonomy.json")
    sources = load(LEGACY / "compiler/source_system_taxonomy.json")
    source_expanded_report = load(HERE / "source_systems/coverage-report.json")
    source_expanded_registry = HERE / "source_systems/source-classes.jsonl"
    ontology = load(LEGACY / "data_ontology.json")
    machine_map = load(LEGACY / "composition/analytics_type_machine_map.json")
    horizontal = load(LEGACY / "composition/horizontal_registry.json")

    analytics_ids = {item["id"] for item in knowledge["analytics_types"]}
    classified_ids = {item["analytics_type_id"] for item in taxonomy["classifications"]}
    mapped_ids = {item["analytics_type_id"] for item in machine_map["mappings"]}
    mapping_status = Counter(item["status"] for item in machine_map["mappings"])

    type_layers = {
        "carrier": len(ontology["carrier_types"]),
        "semantic_value": len(ontology["semantic_value_types"]),
        "observation": len(ontology["observation_types"]),
        "analytical_structure": len(ontology["analytical_structures"]),
        "composite": len(ontology["composite_types"]),
    }

    forbidden = ("llm", "large language", "prompt", "rag", "agent memory", "generative")
    forbidden_core_records = []
    for item in knowledge["analytics_types"]:
        searchable = " ".join([item["id"], item["name"], item["definition"], *item.get("aliases", [])]).lower()
        if any(term in searchable for term in forbidden):
            forbidden_core_records.append(item["id"])

    context_registry = ROOT / "domain_atlas/registry/context-candidates.jsonl"
    analytics_candidate_registry = HERE / "analytics_types/candidate-practices.jsonl"
    analytics_family_catalog = load(HERE / "analytics_types/family-catalog.json")
    operation_candidate_registry = HERE / "operations/operation-candidates.jsonl"
    operation_family_catalog = load(HERE / "operations/family-catalog.json")
    operation_deep_specs = load(HERE / "operations/deep-specifications.json")
    report = {
        "audit_id": "san.domain-atlas.universe-baseline",
        "edition": 1,
        "as_of": "2026-08-25",
        "status": "incomplete_baseline",
        "analytics_type_universe": {
            "inherited_adjudication_records": len(analytics_ids),
            "classified": len(classified_ids),
            "machine_mapped": len(mapped_ids),
            "mapping_status": dict(sorted(mapping_status.items())),
            "referentially_closed": analytics_ids == classified_ids == mapped_ids,
            "claim_300_supported": len(analytics_ids) >= 300,
            "expanded_hypothesis_candidates": line_count(analytics_candidate_registry),
            "expanded_candidate_families": analytics_family_catalog["family_count"],
            "expanded_candidate_completion_claim": analytics_family_catalog["completion_claim"],
            "standing": "seeded_incomplete"
        },
        "source_system_universe": {
            "inherited_seed_class_records": len(sources["source_classes"]),
            "researched_candidate_class_records": line_count(source_expanded_registry),
            "classification_axes": source_expanded_report["classification_axes"],
            "axis_values": source_expanded_report["axis_values"],
            "primary_evidence_records": source_expanded_report["primary_evidence_records"],
            "completion_claim": source_expanded_report["completion_claim"],
            "standing": source_expanded_report["standing"]
        },
        "data_type_universe": {
            "layers": type_layers,
            "total_records": sum(type_layers.values()),
            "classification_axes": len(ontology["classification_axes"]),
            "standing": "layered_seed_incomplete"
        },
        "operation_universe": {
            "normalized_operation_hypotheses": line_count(operation_candidate_registry),
            "operation_families": operation_family_catalog["family_count"],
            "deep_specification_overlays": len(operation_deep_specs["operations"]),
            "horizontal_machine_records": len(horizontal["machines"]),
            "horizontal_library_records": len(horizontal["libraries"]),
            "completion_claim": operation_family_catalog["completion_claim"],
            "standing": "enumerated_hypotheses_with_initial_deep_specs"
        },
        "bounded_context_universe": {
            "candidate_occurrences": line_count(context_registry),
            "standing": "enumerated_not_adjudicated"
        },
        "llm_quarantine": {
            "forbidden_core_analytics_records": forbidden_core_records,
            "passes": not forbidden_core_records
        },
        "blocking_gaps": [
            "inherited analytics registry contains 60 records rather than the previously claimed 300",
            "expanded analytical-practice records are hypotheses and require split/merge, evidence and compiler adjudication",
            "source-system universe is an open-world researched candidate and still lacks independent review and recurring saturation evidence",
            "data-type ontology lacks an operation-by-type totality matrix",
            "normalized operation records are hypotheses; most lack typed signatures, laws, evidence and lowering",
            "machine mappings are partial or gaps for 23 of 60 inherited analytics types",
            "559 distinct context candidates remain unadjudicated",
            "no universe has independent completeness evidence"
        ],
        "completion_claim": False
    }
    output = HERE / "universe-coverage-audit.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "WROTE universe baseline: "
        f"{len(analytics_ids)} inherited analytics, {line_count(source_expanded_registry)} researched source classes, "
        f"{sum(type_layers.values())} inherited data-type records, "
        f"{line_count(operation_candidate_registry)} operation hypotheses, "
        f"{line_count(context_registry)} context occurrences"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
