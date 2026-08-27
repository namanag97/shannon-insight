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
        "0 qualified providers; 0 build-ready products"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
