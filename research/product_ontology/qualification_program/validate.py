#!/usr/bin/env python3
"""Validate the product qualification program and its fail-closed posture."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load_jsonl(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []
    check = subprocess.run([sys.executable, str(HERE / "build_program.py"), "--check"], cwd=ROOT, text=True, capture_output=True)
    if check.returncode:
        errors.append(check.stdout.strip() or check.stderr.strip())
    effective_check = subprocess.run(
        [sys.executable, str(HERE / "build_effective_state.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if effective_check.returncode:
        errors.append(effective_check.stdout.strip() or effective_check.stderr.strip())

    gates = load_jsonl("gate-definitions.jsonl")
    edges = load_jsonl("gate-dependencies.jsonl")
    programs = load_jsonl("product-qualification-programs.jsonl")
    subjects = load_jsonl("library-qualification-subjects.jsonl")
    bindings = load_jsonl("execution-evidence-bindings.jsonl")
    vacancies = load_jsonl("evidence-vacancies.jsonl")
    acceptance = load_jsonl("product-vertical-acceptance-programs.jsonl")
    summary = json.loads((HERE / "summary.json").read_text())
    manifest = json.loads((HERE / "manifest.json").read_text())
    effective_summary = json.loads((HERE / "effective-summary.json").read_text())
    effective_rows = load_jsonl("effective-gate-state-rebase.jsonl")

    gate_ids = {row["gate_id"] for row in gates}
    if len(gates) != 16 or len(gate_ids) != len(gates):
        errors.append("qualification DAG must contain exactly 16 unique gate definitions")
    indegree = Counter({gate_id: 0 for gate_id in gate_ids})
    graph: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        source, target = edge["from_gate_ref"], edge["to_gate_ref"]
        if source not in gate_ids or target not in gate_ids:
            errors.append(f"unknown gate dependency endpoint: {source} -> {target}")
        graph[source].append(target)
        indegree[target] += 1
    queue = deque(sorted(gate for gate, count in indegree.items() if count == 0))
    visited = 0
    while queue:
        gate = queue.popleft(); visited += 1
        for target in graph[gate]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if visited != len(gate_ids):
        errors.append("qualification gate graph contains a cycle")

    candidate_ids = {row["candidate_id"] for row in programs}
    retained_ids = {
        row["candidate_id"]
        for row in (
            json.loads(line)
            for line in (ROOT / "research/product_ontology/dossier_readiness/product-readiness.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    if len(candidate_ids) != len(programs) or candidate_ids != retained_ids:
        errors.append("qualification program must exactly cover every retained product")
    if len(acceptance) != len(programs) or {row["candidate_id"] for row in acceptance} != candidate_ids:
        errors.append("every product must have one vertical acceptance program")
    subject_ids = {row["subject_id"] for row in subjects}
    if len(subject_ids) != len(subjects):
        errors.append("duplicate library qualification subject")
    subjects_by_product = Counter(row["candidate_id"] for row in subjects)
    if set(subjects_by_product) != candidate_ids or min(subjects_by_product.values(), default=0) < 1:
        errors.append("every product must have at least one exact library qualification subject")
    binding_ids = {row["binding_id"] for row in bindings}
    if len(binding_ids) != len(bindings):
        errors.append("duplicate execution evidence binding")
    for binding in bindings:
        source_path = ROOT / binding["source_ref"]
        evidence_path = ROOT / binding["evidence_ref"]
        if not source_path.is_file() or hashlib.sha256(source_path.read_bytes()).hexdigest() != binding["source_sha256"]:
            errors.append(f"{binding['binding_id']}: source binding identity drift")
        if not evidence_path.is_file():
            errors.append(f"{binding['binding_id']}: missing retained evidence")
        if binding["qualification_subject_ref"] not in subject_ids or binding["relevant_gate_ref"] not in gate_ids:
            errors.append(f"{binding['binding_id']}: unknown subject or gate")
        if binding["completion_claim"] or binding["qualified_implementation_count"] or binding["portable_offer"] or binding["build_ready"] or binding["ratified"]:
            errors.append(f"{binding['binding_id']}: unsupported promotion")
    if any(row["implementation_state"] != "NO_BOUND_ARTIFACT" or row["qualified_implementation_refs"] or row["portable_offer"] for row in subjects):
        errors.append("an implementation was promoted without evidence")
    effective_by_binding = {
        row["execution_evidence_binding_ref"]: row
        for row in effective_rows
        if row.get("execution_evidence_binding_ref")
    }
    if set(effective_by_binding) != binding_ids:
        errors.append("effective state does not consume every execution evidence binding exactly once")
    for binding in bindings:
        effective = effective_by_binding.get(binding["binding_id"])
        if effective and (
            effective["effective_state"] != binding["gate_effect"]
            or effective["qualification_subject_ref"] != binding["qualification_subject_ref"]
        ):
            errors.append(f"{binding['binding_id']}: effective execution-evidence state mismatch")
    if any("Removing every model, LLM and agent" not in row["automation_extension"]["removal_law"] for row in programs):
        errors.append("optional automation removal law is missing")
    for program in programs:
        states = {row["gate_ref"]: row["state"] for row in program["gate_states"]}
        if set(states) != gate_ids:
            errors.append(f"{program['candidate_id']}: incomplete gate state vector")
        if states["gate.qp.boundary_ddd"] != "SATISFIED_STRUCTURAL":
            errors.append(f"{program['candidate_id']}: boundary/DDD structural gate drift")
        if program["current_verdict"] != "BLOCKED_NO_QUALIFIED_PORTABLE_ACCEPTED_IMPLEMENTATION":
            errors.append(f"{program['candidate_id']}: premature product verdict")
        for ref in program["library_subject_refs"]:
            if ref not in subject_ids:
                errors.append(f"{program['candidate_id']}: unknown library subject {ref}")
        program_bindings = [row for row in bindings if row["candidate_id"] == program["candidate_id"]]
        for binding in program_bindings:
            if states[binding["relevant_gate_ref"]] != "OPEN_NO_EVIDENCE":
                errors.append(f"{binding['binding_id']}: immutable base snapshot was rewritten")
    if any(row["current_verdict"] != "NOT_EXECUTED" or any(slot["executed_acceptance_ref"] for slot in row["vertical_slots"]) for row in acceptance):
        errors.append("vertical acceptance was promoted without execution evidence")
    if any(not row["blocking"] or row["status"] != "OPEN" for row in vacancies):
        errors.append("an evidence vacancy is not open and blocking")

    if any(summary[key] for key in ("qualified_product_count", "portable_product_count", "executed_vertical_acceptance_product_count", "build_ready_product_count", "ratified_product_count")):
        errors.append("summary contains an unsupported promotion")
    if any(effective_summary[key] for key in ("qualified_product_count", "portable_product_count", "executed_vertical_acceptance_product_count", "build_ready_product_count", "ratified_product_count")):
        errors.append("effective summary contains an unsupported promotion")
    if effective_summary["effective_gate_state_counts"].get("BLOCKED_MISSING_CONTRACT", 0):
        errors.append("effective qualification state resurrects a resolved structural compiler gap")

    if effective_summary.get("execution_evidence_binding_count") != len(bindings):
        errors.append("effective summary execution-binding count drift")
    expected_counts = {"products": len(programs), "subjects": len(subjects), "vacancies": len(vacancies), "acceptance_programs": len(acceptance), "gates": len(gates), "edges": len(edges)}
    if manifest["counts"] != expected_counts:
        errors.append("manifest counts drift")
    for name, metadata in manifest["files"].items():
        path = HERE / name
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != metadata["sha256"] or len(data) != metadata["bytes"]:
            errors.append(f"manifest digest drift: {name}")

    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1
    print(
        f"PASS product qualification program: {len(programs)} products; {len(subjects)} exact library subjects; "
        f"{len(gates)}-gate DAG; {effective_summary['effective_evidence_vacancy_count']} effective open evidence vacancies; "
        "0 qualified, portable, accepted, build-ready or ratified products"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
