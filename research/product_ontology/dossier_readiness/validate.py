#!/usr/bin/env python3
"""Validate the retained-product DDD/compiler readiness matrix."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load_jsonl(name: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (HERE / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    errors: list[str] = []
    check = subprocess.run(
        [sys.executable, str(HERE / "build_matrix.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check.returncode:
        errors.append(check.stdout.strip() or check.stderr.strip())

    rows = load_jsonl("product-readiness.jsonl")
    work = load_jsonl("closure-work-items.jsonl")
    compiler_gap_rebase = load_jsonl("compiler-gap-rebase.jsonl")
    projections = load_jsonl("closure-workstream-projection.jsonl")
    campaigns = load_jsonl("reusable-closure-campaigns.jsonl")
    dag = load_jsonl("closure-execution-dag.jsonl")
    summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    ids = [row["candidate_id"] for row in rows]
    retained_ids = {
        row["record_id"]
        for row in (
            json.loads(line)
            for line in (ROOT / "research/product_ontology/global_boundary_research/product-archetypes.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        if row["boundary_evaluation"]["verdict"] in {"strong_product", "presumptive_product"}
    }
    if len(set(ids)) != len(ids) or set(ids) != retained_ids:
        errors.append("readiness matrix must exactly cover every unique retained product")
    if any(row["boundary_adjudication"] != "PASS_EXACT_TRACE" for row in rows):
        errors.append("a retained product lacks exact boundary adjudication")
    if any(row["global_truth_profile"]["truth_dimension_count"] != 110 for row in rows):
        errors.append("a retained product lacks exactly 110 truth-applicability decisions")
    complete = [row for row in rows if row["product_specific_ddd"]["status"] == "COMPLETE_CANDIDATE_DOSSIER"]
    if len(complete) != len(rows) or any(row["product_specific_ddd"]["present_count"] != 29 for row in complete):
        errors.append("every retained product must have a complete 29-field DDD dossier")
    uncovered = [row for row in rows if row["library_and_compiler"]["uncovered_required_capability_count"]]
    if uncovered:
        errors.append("no retained product may expose an uncovered internally owned capability")
    if any(row["provider_readiness"]["qualified_offer_count"] for row in rows):
        errors.append("a provider became qualified without new qualification evidence")
    if any(row["provider_readiness"]["portable_offer_count"] for row in rows):
        errors.append("a provider became portable without two independent qualified implementations")
    if len(compiler_gap_rebase) != 59:
        errors.append("the 59 source compiler gaps must rebase losslessly")
    if len({row["source_gap_ref"] for row in compiler_gap_rebase}) != len(compiler_gap_rebase):
        errors.append("compiler-gap rebase duplicates a source gap")
    if any(
        set(row["contract_surface_present"])
        < {"types", "operations", "decisions", "invariants", "refusals", "dependencies"}
        for row in compiler_gap_rebase
    ):
        errors.append("a rebased compiler gap lacks a complete abstract contract surface")
    if any(
        row["status"] != "RESEARCH_RESOLVED_DOWNSTREAM_GATED"
        or row["remaining_gate"] != "CONCRETE_IMPLEMENTATION_AND_PROVIDER_QUALIFICATION"
        or row["qualified_implementation_refs"]
        or not row["compiler_binding"].startswith("REFUSED")
        or row["completion_claim"] is not False
        for row in compiler_gap_rebase
    ):
        errors.append("compiler-gap rebase bypasses implementation or qualification gates")
    if any(row["library_and_compiler"]["open_structural_binding_gap_count"] for row in rows):
        errors.append("a research-addressable structural compiler gap remains open")
    if sum(row["library_and_compiler"]["research_resolved_binding_gap_count"] for row in rows) != 59:
        errors.append("product readiness loses a compiler-gap rebase")
    if any(row["build_readiness"] != "NOT_BUILD_READY" or row["ratification"] != "WITHHELD" for row in rows):
        errors.append("a product was prematurely marked build-ready or ratified")
    if any(not row["automation_law"]["deterministic_core_survives_removal"] for row in rows):
        errors.append("deterministic-core removal law drift")
    work_by_candidate = Counter(row["candidate_id"] for row in work)
    if set(work_by_candidate) != set(ids) or min(work_by_candidate.values(), default=0) < 2:
        errors.append("every retained product needs explicit closure work")
    if any(not row["blocking"] or row["status"] != "OPEN" for row in work):
        errors.append("closure work must remain open and blocking in this edition")
    if any(row["work_kind"] == "compiler_gap_closure" for row in work):
        errors.append("research-resolved compiler gaps are still double-counted as product work")
    work_ids = {row["record_id"] for row in work}
    if len(projections) != len(work) or {row["work_item_ref"] for row in projections} != work_ids:
        errors.append("closure workstream projection must cover every work item exactly once")
    if len({row["work_item_ref"] for row in projections}) != len(projections):
        errors.append("closure workstream projection duplicates a work item")
    if any(
        not row["shared_workstream_refs"]
        or not row["exact_execution_refs"]
        or not row["refusal_gate"].startswith("REFUSE")
        or row["status"] != "ROUTED_EXECUTION_OPEN"
        or row["completion_claim"] is not False
        for row in projections
    ):
        errors.append("a closure item lacks an exact fail-closed execution route")
    by_kind = Counter(row["work_kind"] for row in projections)
    if by_kind != Counter({"provider_qualification": 66, "executed_vertical_acceptance": 66, "unrelated_vertical_generality": 54}):
        errors.append("closure workstream projection kind counts drift")
    provider_projections = [row for row in projections if row["work_kind"] == "provider_qualification"]
    if any(not row["subject_refs"] or not row["qualification_profile_refs"] for row in provider_projections):
        errors.append("provider qualification route lacks exact subjects or profile kernels")
    acceptance_projections = [row for row in projections if row["work_kind"] == "executed_vertical_acceptance"]
    if any(len(row["shared_workstream_refs"]) != 8 or len(row["exact_execution_refs"]) != 16 for row in acceptance_projections):
        errors.append("vertical acceptance route must cover 2 slots x 8 gate classes")
    generality_projections = [row for row in projections if row["work_kind"] == "unrelated_vertical_generality"]
    if any(len(row["exact_execution_refs"]) != 2 for row in generality_projections):
        errors.append("unrelated-vertical route must preserve two exact slot dockets")
    campaign_classes = Counter(row["campaign_class"] for row in campaigns)
    if campaign_classes != Counter({"QUALIFICATION_CONFORMANCE_METHOD": 42, "VERTICAL_ACCEPTANCE_GATE_METHOD": 8, "UNRELATED_VERTICAL_SLOT_SELECTION": 1}):
        errors.append("reusable closure campaign factoring drift")
    if len(campaigns) != len({row["campaign_id"] for row in campaigns}) or any(row["completion_claim"] is not False for row in campaigns):
        errors.append("reusable campaign identity collision or completion overclaim")
    if any(not row["shared_verdict_forbidden"] for row in campaigns):
        errors.append("a reusable campaign permits shared verdicts")
    if [row["stage"] for row in dag] != [1, 2, 3, 4, 5] or any(row["completion_claim"] is not False for row in dag):
        errors.append("closure execution DAG is not total, ordered and fail closed")
    if summary["retained_product_count"] != len(rows) or summary["open_work_item_count"] != len(work):
        errors.append("summary counts drift")
    if summary["build_ready_product_count"] or summary["executed_vertical_acceptance_product_count"]:
        errors.append("summary prematurely claims build readiness or executed acceptance")
    if (
        summary["source_compiler_gap_count"] != 59
        or summary["research_resolved_compiler_gap_count"] != 59
        or summary["open_structural_compiler_gap_count"] != 0
        or summary["implementation_binding_vacancy_count"] != 59
    ):
        errors.append("compiler-gap rebase summary drift")
    if summary.get("closure_workstream_projection_count") != 186 or summary.get("reusable_campaign_count") != 51 or summary.get("campaign_stage_count") != 5:
        errors.append("closure campaign summary drift")

    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1
    print(
        "PASS retained-product readiness: "
        f"{len(rows)} retained products; {len(complete)} full DDD dossiers; "
        f"{summary['explicit_product_library_attribution_count']} explicit product-library decompositions; "
        f"{summary['explicit_product_compiler_map_count']} explicit product compiler maps; "
        f"{len(work)} physical/acceptance closure items; 59 source compiler gaps structurally rebased; "
        f"{len(campaigns)} reusable execution campaigns in {len(dag)} stages; "
        "0 qualified providers; 0 build-ready products"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
