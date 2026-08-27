#!/usr/bin/env python3
"""Fail-closed structural and constitutional validator for the research bundle.

Passing validates the corpus contract only. It never qualifies an actual offer.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def fail(message: str) -> None:
    raise SystemExit(f"FAIL {message}")


def load_jsonl(name: str):
    rows = []
    for n, line in enumerate((ROOT / name).read_text().splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"{name}:{n}: invalid JSON: {exc}")
        if not isinstance(row, dict):
            fail(f"{name}:{n}: record is not object")
        for field in ("id", "kind", "edition", "status"):
            if field not in row:
                fail(f"{name}:{n}: missing {field}")
        rows.append(row)
    return rows


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    metamodel = json.loads((ROOT / "metamodel.json").read_text())
    if manifest.get("actual_offer_qualified") is not False or metamodel.get("completion_claim") is not False:
        fail("research corpus must never claim completion or actual qualification")

    all_rows = []
    by_file = {}
    for name, expected in manifest["counts"].items():
        if name == "oracle_test_decision_proof_records":
            continue
        rows = load_jsonl(name)
        by_file[name] = rows
        all_rows.extend(rows)
        if len(rows) != expected:
            fail(f"{name}: manifest count {expected}, observed {len(rows)}")
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if digest != manifest["sha256"][name]:
            fail(f"{name}: digest mismatch")

    identifiers = [row["id"] for row in all_rows]
    duplicate = [identifier for identifier, count in Counter(identifiers).items() if count > 1]
    if duplicate:
        fail(f"duplicate identifiers: {duplicate[:5]}")
    ids = set(identifiers)

    thresholds = manifest["thresholds"]
    checks = {
        "sources": len(by_file["sources.jsonl"]),
        "contexts": len(by_file["context-families.jsonl"]),
        "oracle_test_decision_proof_records": sum(len(by_file[name]) for name in
            ("oracle-contracts.jsonl", "test-techniques.jsonl", "decision-points.jsonl", "proof-obligations.jsonl")),
        "library_boundaries": len(by_file["library-boundaries.jsonl"]),
        "innovations_2021_2026": len(by_file["innovations-2021-2026.jsonl"]),
    }
    for key, floor in thresholds.items():
        if key == "unrelated_verticals":
            continue
        if checks[key] < floor:
            fail(f"threshold {key}: {checks[key]} < {floor}")
    if manifest["counts"]["oracle_test_decision_proof_records"] != checks["oracle_test_decision_proof_records"]:
        fail("derived assurance-record count mismatch")

    sources = {row["id"] for row in by_file["sources.jsonl"]}
    if not all(row.get("primary_or_official") is True and row.get("authority_scope") for row in by_file["sources.jsonl"]):
        fail("every source must be primary/official and scope-bound")
    for name in ("oracle-contracts.jsonl", "test-techniques.jsonl", "innovations-2021-2026.jsonl"):
        for row in by_file[name]:
            missing = set(row.get("source_refs", [])) - sources
            if missing:
                fail(f"{row['id']}: missing source refs {sorted(missing)}")
    if not all(row.get("non_llm") is True and 2021 <= row["year"] <= 2026
               for row in by_file["innovations-2021-2026.jsonl"]):
        fail("innovations must be dated 2021-2026 and non-LLM")

    contexts = {row["id"] for row in by_file["context-families.jsonl"]}
    for name in ("oracle-contracts.jsonl", "test-techniques.jsonl", "decision-points.jsonl",
                 "proof-obligations.jsonl", "coverage-matrix.jsonl", "requirements.jsonl", "offers.jsonl"):
        for row in by_file[name]:
            if row.get("context_ref") not in contexts:
                fail(f"{row['id']}: unresolved context_ref")

    oracle_ids = {row["id"] for row in by_file["oracle-contracts.jsonl"]}
    test_ids = {row["id"] for row in by_file["test-techniques.jsonl"]}
    for row in by_file["coverage-matrix.jsonl"]:
        if set(row["oracle_refs"]) - oracle_ids or set(row["test_refs"]) - test_ids:
            fail(f"{row['id']}: unresolved oracle/test coverage refs")
        if row.get("qualification_effect") != "none" or row.get("current_evidence") != "taxonomy_only":
            fail(f"{row['id']}: research coverage row cannot qualify")

    lib_ids = {row["id"] for row in by_file["library-boundaries.jsonl"]}
    req_ids = {row["id"] for row in by_file["requirements.jsonl"]}
    offer_ids = {row["id"] for row in by_file["offers.jsonl"]}
    for row in by_file["offers.jsonl"]:
        if row.get("bindable") is not False or row.get("evidence_receipt_refs"):
            fail(f"{row['id']}: candidate offer became bindable")
        if row.get("harness_boundary_ref") not in lib_ids:
            fail(f"{row['id']}: unresolved harness boundary")
    for row in by_file["requirement-offer-mappings.jsonl"]:
        if row["requirement_ref"] not in req_ids or row["offer_ref"] not in offer_ids:
            fail(f"{row['id']}: unresolved mapping")
        if row.get("binding_eligible") is not False or row.get("semantically_qualified") is not False:
            fail(f"{row['id']}: research mapping must be non-bindable")

    expected_layers = ["declaration", "schema_validation", "compile_type_check", "semantic_law_proof",
                       "executed_test", "benchmark", "deployed_observation", "independent_appraisal"]
    if metamodel.get("evidence_layers") != expected_layers:
        fail("evidence layers collapsed, missing, or reordered")
    laws = " ".join(metamodel.get("constitutional_laws", [])).lower()
    for phrase in ("schema validity is not compilation", "absence of a failure", "waiver is an expiring",
                   "two implementations", "component qualification", "passing this corpus validator never qualifies"):
        if phrase not in laws:
            fail(f"missing constitutional law: {phrase}")

    verdicts = {row["id"]: row for row in by_file["verdict-rules.jsonl"]}
    for key in ("verdict.ce.timeout", "verdict.ce.flaky", "verdict.ce.underpowered"):
        if verdicts[key]["result"] != "inconclusive":
            fail(f"{key}: must be inconclusive")
    if verdicts["verdict.ce.waived"]["result"] == "pass":
        fail("waiver cannot be pass")

    receipt_schema = json.loads((ROOT / "qualification-receipt-contract.schema.json").read_text())
    receipt_required = set(receipt_schema["required"])
    for field in ("artifact_digest", "dependency_lock_digest", "configuration_digest", "target_occurrence",
                  "oracle", "population", "execution", "verdict", "validity", "invalidation_triggers"):
        if field not in receipt_required:
            fail(f"receipt contract missing {field}")

    sm = by_file["qualification-state-machines.jsonl"]
    if len(sm) != 1:
        fail("exactly one qualification state-machine candidate required")
    forbidden = set(sm[0]["forbidden"])
    if "schema_valid -> qualified" not in forbidden or "benchmark_pass -> qualified" not in forbidden:
        fail("qualification state machine lacks forbidden shortcuts")

    positives = [row for row in by_file["examples.jsonl"] if row["kind"] == "vertical_example"]
    negatives = [row for row in by_file["examples.jsonl"] if row["kind"] == "negative_twin"]
    if len({row["vertical"] for row in positives}) < thresholds["unrelated_verticals"]:
        fail("fewer than two unrelated vertical examples")
    if len(negatives) < len(positives) or any(row.get("result") != "unqualified" for row in positives):
        fail("vertical examples require negative twins and must remain unqualified")

    required_context_slugs = {"algebraic_law", "property_based", "model_based", "metamorphic", "differential",
                              "conformance_suite", "golden", "fuzz_parser", "mutation", "chaos", "failure_injection",
                              "security_dynamic", "performance_latency", "numerical_accuracy", "statistical_power",
                              "reproducibility", "accessibility", "api_surface", "replay", "migration", "restore"}
    actual_slugs = {row["id"].removeprefix("context.ce.") for row in by_file["context-families.jsonl"]}
    if required_context_slugs - actual_slugs:
        fail(f"missing mandatory test families: {sorted(required_context_slugs - actual_slugs)}")

    before = {name: (ROOT / name).read_bytes() for name in manifest["sha256"]}
    subprocess.run([sys.executable, str(ROOT / "build_bundle.py")], check=True, cwd=ROOT)
    for name, data in before.items():
        if (ROOT / name).read_bytes() != data:
            fail(f"non-deterministic regeneration: {name}")

    execution_root = ROOT / "executions/lp_solver_exact_scope"
    retained_run = execution_root / "runs/run-20260826-macos-arm64-python3_14-001"
    execution_validator = execution_root / "validate_execution.py"
    completed = subprocess.run(
        [sys.executable, str(execution_validator), str(retained_run)],
        cwd=ROOT.parents[2],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        fail("retained exact-scope LP execution: " + (completed.stdout or completed.stderr).strip())
    if completed.stdout.strip():
        print(completed.stdout.strip())

    print("PASS conformance/evaluation candidate corpus: "
          f"{len(sources)} primary/official sources, {len(contexts)} context families, "
          f"{checks['oracle_test_decision_proof_records']} oracle/test/decision/proof records, "
          f"{len(lib_ids)} library boundaries, {len(by_file['innovations-2021-2026.jsonl'])} innovations; "
          "0 actual offers qualified")


if __name__ == "__main__":
    main()
