#!/usr/bin/env python3
"""Validate the quality/reconciliation product-boundary split audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
QOR = ROOT / "research/domain_atlas/universes/quality_observability_reconciliation"
VERTICALS = ROOT / "research/product_ontology/composition_pilots/deterministic_verticals"
GLOBAL = ROOT / "research/product_ontology/global_boundary_research"


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check = subprocess.run([sys.executable, str(HERE / "build_audit.py"), "--check"], cwd=ROOT, text=True, capture_output=True)
    require(check.returncode == 0, check.stdout.strip() or check.stderr.strip())
    source = json.loads((HERE / "source.json").read_text(encoding="utf-8"))
    require(source["status"] == "canonical_split_promoted_unratified", "split audit promotion status drift")
    qor_sources = {row["source_id"] for row in jsonl(QOR / "sources.jsonl")}
    qor_libraries = {
        row["library_id"].replace("qor.library.", "library.qor.")
        for row in jsonl(QOR / "library-boundary-candidates.jsonl")
    }
    require(set(source["evidence_refs"]) <= qor_sources, "split audit has unresolved QOR evidence")
    assignments = source["library_assignments"]
    assignment_refs = [row["library_ref"] for row in assignments]
    require(len(assignments) == 37 and len(set(assignment_refs)) == 37, "all 37 QOR libraries must be assigned exactly once")
    require(set(assignment_refs) == qor_libraries, "split audit library assignment coverage drift")
    hypotheses = source["replacement_hypotheses"]
    require(len(hypotheses) == 2, "split audit must propose exactly two replacement products")
    for row in hypotheses:
        scores = row["split_scores"]
        require(set(scores) == {"user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"}, f"incomplete split scores: {row['hypothesis_id']}")
        require(17 <= sum(scores.values()) <= 20 and row["verdict"] == "strong_product_candidate", f"unsupported strong verdict: {row['hypothesis_id']}")
        require(row["owned_meanings"] and row["excluded_meanings"], f"hypothesis lacks positive/negative boundary: {row['hypothesis_id']}")
    compositions = {row["composition_id"]: row for row in jsonl(VERTICALS / "vertical-compositions.jsonl")}
    global_candidate_ids = {row["record_id"] for row in jsonl(GLOBAL / "product-archetypes.jsonl")}
    require("candidate.product.quality_reconciliation" not in global_candidate_ids, "retired combined candidate remains canonical")
    require({
        "candidate.product.data_quality_operations",
        "candidate.product.reconciliation_control_operations",
    } <= global_candidate_ids, "canonical replacement candidates are missing")
    remaps = source["vertical_remaps"]
    require(len(remaps) == 4 and {row["composition_ref"] for row in remaps} == set(compositions), "vertical remap set drift")
    reconciliation_prefixes = {
        "library.qor.reconciliation_definition_kernel",
        "library.qor.reconciliation_execution_kernel",
        "library.qor.reconciliation_break_kernel",
        "library.qor.accounting_control_reconciliation_kernel",
    }
    for row in remaps:
        composition = compositions[row["composition_ref"]]
        has_reconciliation = bool(reconciliation_prefixes & set(composition["required_library_refs"]))
        expects_reconciliation = "candidate.product.reconciliation_control_operations" in row["replacement_refs"]
        require(has_reconciliation == expects_reconciliation, f"vertical remap does not follow exact libraries: {row['composition_ref']}")
        require(set(row["replacement_refs"]) <= set(composition["product_refs"]), f"canonical product remap missing from vertical: {row['composition_ref']}")
        require(row["existing_ref"] not in composition["product_refs"], f"retired product remains in vertical: {row['composition_ref']}")
    require(len(source["negative_tests"]) >= 8, "negative split-test surface too small")
    require(any("model or agent" in row["prohibited_claim"] for row in source["negative_tests"]), "missing model/agent authority refusal")
    require(len(source["open_gaps"]) >= 3 and "neither replacement product is ratified" in source["non_completion_claim"], "audit overclaims completion")
    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1
    print("PASS quality/reconciliation split audit: 2 canonical unratified replacements; 37 library assignments; 4 exact promoted vertical remaps; 8 negative tests; old combined candidate removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
