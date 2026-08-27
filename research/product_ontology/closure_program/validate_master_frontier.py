#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
rows = [json.loads(x) for x in (HERE / "master-batches.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
summary = json.loads((HERE / "master-summary.json").read_text(encoding="utf-8"))
readiness = json.loads((ROOT / "research/product_ontology/dossier_readiness/summary.json").read_text(encoding="utf-8"))
qualification = json.loads((ROOT / "research/product_ontology/qualification_program/effective-summary.json").read_text(encoding="utf-8"))
industries = json.loads((ROOT / "research/domain_atlas/industries/integration-audit.json").read_text(encoding="utf-8"))
industry_effective = json.loads((ROOT / "research/domain_atlas/industries/canonical-reference-effective-summary.json").read_text(encoding="utf-8"))
industry_review = json.loads((ROOT / "research/domain_atlas/industries/canonical-reference-machine-review-summary.json").read_text(encoding="utf-8"))
context_map = json.loads((ROOT / "research/domain_atlas/context_map/manifest.json").read_text(encoding="utf-8"))
source_systems = json.loads((ROOT / "research/domain_atlas/universes/source_systems/coverage-report.json").read_text(encoding="utf-8"))
data_shapes = json.loads((ROOT / "research/domain_atlas/universes/data_shapes/coverage-report.json").read_text(encoding="utf-8"))
providers = json.loads((ROOT / "research/domain_atlas/compiler/provider_target_registry/manifest.json").read_text(encoding="utf-8"))

assert len(rows) == 16 == summary["batch_count"]
ids = [r["batch_id"] for r in rows]
assert ids == [f"B{i:02d}_" + ids[i].split("_", 1)[1] for i in range(16)]
assert len(set(ids)) == len(ids)
known = set(ids)
for row in rows:
    assert set(row["depends_on"]) <= known
    assert row["exit_condition"] and row["authority_refs"] and row["scope"]

cases = sum(p["cases"] for p in industries["packs"])
assert cases == 1613 == summary["industry_analytical_case_count"]
assert summary["retained_product_count"] == readiness["retained_product_count"] == 66
assert summary["library_subject_count"] == qualification["library_qualification_subject_count"] == 539
assert summary["effective_evidence_vacancy_count"] == qualification["effective_evidence_vacancy_count"] == 912
assert summary["industry_canonical_reference_raw_queue_count"] == industries["canonical_reference_review_queue_records"] == industry_effective["raw_queue_records"] == 4169
assert summary["industry_canonical_reference_queue_count"] == industry_effective["remaining_open_research_records"] == 4166
assert summary["industry_canonical_reference_research_resolved_count"] == industry_effective["research_resolved_candidate_records"] == 3
assert summary["industry_canonical_reference_machine_review_candidate_count"] == industry_review["source_candidate_records"] == 137
assert summary["context_count"] == context_map["counts"]["contexts"] == 144
assert summary["source_system_class_count"] == source_systems["class_records"] == 171
assert summary["data_shape_logical_count"] == data_shapes["counts"]["logical_shapes"] == 177
assert summary["provider_offer_seed_count"] == providers["counts"]["concrete_offers"] == 59
assert summary["completion_claim"] is False
assert rows[7]["current"]["unresolved_method_refs"] == industry_effective["method_reference_frontier"]["remaining_open_research_distinct"] == 2028
assert rows[7]["current"]["effective_open_review_records"] == industry_effective["remaining_open_research_records"]
assert rows[7]["current"]["machine_review_batches"] == industry_review["review_batch_count"] == 31
assert rows[7]["current"]["machine_exact_alias_candidate_occurrences"] == industry_review["source_candidate_occurrences"] == 644
assert rows[14]["current"]["nominal_gate_obligations"] == qualification["retained_product_count"] * 2 * 8 == 1056
print("PASS master closure frontier: 16 dependency-ordered batches; live counts agree with authority summaries")
