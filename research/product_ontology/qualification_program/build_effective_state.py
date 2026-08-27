#!/usr/bin/env python3
"""Derive the effective qualification state after canonical compiler-gap rebasing.

The original qualification snapshot is retained as trace evidence. This projection applies only
research rebase records that prove an exact abstract contract is already present. It never promotes
implementation, execution, appraisal, portability, physical binding, vertical acceptance or
ratification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
READINESS = ROOT / "research/product_ontology/dossier_readiness"
EXECUTIONS = ROOT / "research/domain_atlas/compiler/conformance_evaluation/executions"
AS_OF = "2026-08-27"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_execution_bindings() -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for path in sorted(EXECUTIONS.rglob("qualification-binding.json")):
        source = json.loads(path.read_text(encoding="utf-8"))
        if source.get("record_kind") != "qualification_execution_evidence_binding":
            raise ValueError(f"{path}: unexpected execution-binding record kind")
        subject_ref = source["qualification_subject_ref"]
        gate_ref = source["relevant_gate_ref"]
        bindings.append(
            {
                **source,
                "binding_id": f"binding.qp.{subject_ref.removeprefix('subject.qp.')}.{gate_ref.removeprefix('gate.qp.')}",
                "source_ref": path.relative_to(ROOT).as_posix(),
                "source_sha256": sha256(path),
            }
        )
    return bindings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    programs_path = HERE / "product-qualification-programs.jsonl"
    source_summary_path = HERE / "summary.json"
    vacancies_path = HERE / "evidence-vacancies.jsonl"
    subjects_path = HERE / "library-qualification-subjects.jsonl"
    gates_path = HERE / "gate-definitions.jsonl"
    readiness_summary_path = READINESS / "summary.json"
    rebase_path = READINESS / "compiler-gap-rebase.jsonl"

    programs = load_jsonl(programs_path)
    source_summary = json.loads(source_summary_path.read_text(encoding="utf-8"))
    readiness_summary = json.loads(readiness_summary_path.read_text(encoding="utf-8"))
    rebase_rows = load_jsonl(rebase_path)
    subjects = {row["subject_id"]: row for row in load_jsonl(subjects_path)}
    gate_ids = {row["gate_id"] for row in load_jsonl(gates_path)}
    execution_bindings = load_execution_bindings()

    if readiness_summary["open_structural_compiler_gap_count"] != 0:
        raise ValueError("readiness still has open structural compiler gaps; effective rebase is unsafe")
    if readiness_summary["research_resolved_compiler_gap_count"] != len(rebase_rows):
        raise ValueError("compiler-gap rebase count disagrees with readiness summary")

    by_product: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rebase_rows:
        if row["status"] != "RESEARCH_RESOLVED_DOWNSTREAM_GATED":
            raise ValueError(f"{row['record_id']}: rebase is not research-resolved downstream-gated")
        if row["research_disposition"] != "EXACT_ABSTRACT_CONTRACT_PRESENT":
            raise ValueError(f"{row['record_id']}: exact abstract contract is not proven")
        if row["remaining_gate"] != "CONCRETE_IMPLEMENTATION_AND_PROVIDER_QUALIFICATION":
            raise ValueError(f"{row['record_id']}: unexpected remaining gate")
        if row["implementation_state"] != "NO_BOUND_ARTIFACT" or row["qualified_implementation_refs"]:
            raise ValueError(f"{row['record_id']}: unsupported implementation promotion")
        by_product[row["product_ref"]].append(row)

    effective_rows: list[dict[str, Any]] = []
    source_states = Counter(source_summary["gate_state_counts"])
    blocked_programs = 0
    for program in programs:
        states = {row["gate_ref"]: row["state"] for row in program["gate_states"]}
        if states["gate.qp.contract_decomposition"] != "BLOCKED_MISSING_CONTRACT":
            continue
        blocked_programs += 1
        raw_gap_refs = sorted(program["compiler_gap_refs"])
        rebased = by_product.get(program["product_ref"], [])
        rebased_gap_refs = sorted(row["source_gap_ref"] for row in rebased)
        if raw_gap_refs != rebased_gap_refs:
            raise ValueError(
                f"{program['candidate_id']}: raw compiler gaps do not exactly match canonical rebase"
            )
        effective_rows.append(
            {
                "record_id": f"effective.qp.{program['candidate_id'].removeprefix('candidate.product.')}.contract_decomposition",
                "record_kind": "qualification_effective_gate_state_rebase",
                "candidate_id": program["candidate_id"],
                "product_ref": program["product_ref"],
                "source_state": "BLOCKED_MISSING_CONTRACT",
                "effective_state": "SATISFIED_STRUCTURAL",
                "source_gap_count": len(raw_gap_refs),
                "rebase_record_count": len(rebased),
                "remaining_gate": "CONCRETE_IMPLEMENTATION_AND_PROVIDER_QUALIFICATION",
                "completion_claim": False,
            }
        )

    program_by_candidate = {row["candidate_id"]: row for row in programs}
    for binding in execution_bindings:
        binding_id = binding["binding_id"]
        program = program_by_candidate.get(binding["candidate_id"])
        subject = subjects.get(binding["qualification_subject_ref"])
        gate_ref = binding["relevant_gate_ref"]
        if program is None or subject is None or gate_ref not in gate_ids:
            raise ValueError(f"{binding_id}: unknown candidate, qualification subject or gate")
        if subject["candidate_id"] != binding["candidate_id"] or subject["product_ref"] != binding["product_ref"]:
            raise ValueError(f"{binding_id}: subject scope mismatch")
        evidence_path = ROOT / binding["evidence_ref"]
        if not evidence_path.is_file():
            raise ValueError(f"{binding_id}: retained evidence does not exist")
        if binding["completion_claim"] or binding["qualified_implementation_count"] or binding["portable_offer"] or binding["build_ready"] or binding["ratified"]:
            raise ValueError(f"{binding_id}: unsupported promotion in execution evidence binding")
        source_state = next(row["state"] for row in program["gate_states"] if row["gate_ref"] == gate_ref)
        if source_state != "OPEN_NO_EVIDENCE":
            raise ValueError(f"{binding_id}: execution binding does not start from OPEN_NO_EVIDENCE")
        effective_rows.append(
            {
                "record_id": f"effective.qp.{binding['candidate_id'].removeprefix('candidate.product.')}.{gate_ref.removeprefix('gate.qp.')}",
                "record_kind": "qualification_effective_gate_state_rebase",
                "candidate_id": binding["candidate_id"],
                "product_ref": binding["product_ref"],
                "qualification_subject_ref": binding["qualification_subject_ref"],
                "execution_evidence_binding_ref": binding_id,
                "source_state": source_state,
                "effective_state": binding["gate_effect"],
                "remaining_gate": "PREREQUISITES_INDEPENDENT_APPRAISAL_AND_QUALIFICATION",
                "completion_claim": False,
            }
        )

    if blocked_programs != source_states["BLOCKED_MISSING_CONTRACT"]:
        raise ValueError("source summary blocked-contract count disagrees with product programs")
    if sum(row.get("source_gap_count", 0) for row in effective_rows) != len(rebase_rows):
        raise ValueError("not every canonical compiler-gap rebase is consumed exactly once")

    structural_rebase_count = len(by_product)
    effective_states = dict(source_states)
    effective_states["BLOCKED_MISSING_CONTRACT"] -= structural_rebase_count
    effective_states["SATISFIED_STRUCTURAL"] += structural_rebase_count
    effective_states["OPEN_NO_EVIDENCE"] -= len(execution_bindings)
    effective_states["EVIDENCE_PRESENT_PREREQUISITES_OPEN_NOT_A_PASS"] = len(execution_bindings)
    effective_states = {key: value for key, value in sorted(effective_states.items()) if value}
    effective_vacancies = source_summary["evidence_vacancy_count"] - structural_rebase_count

    summary = {
        "report_id": "product_qualification_effective_state_summary",
        "as_of": AS_OF,
        "retained_product_count": source_summary["retained_product_count"],
        "library_qualification_subject_count": source_summary["library_qualification_subject_count"],
        "source_snapshot_gate_state_counts": source_summary["gate_state_counts"],
        "effective_gate_state_counts": effective_states,
        "source_snapshot_evidence_vacancy_count": source_summary["evidence_vacancy_count"],
        "effective_evidence_vacancy_count": effective_vacancies,
        "rebase_product_count": structural_rebase_count,
        "rebase_source_gap_count": len(rebase_rows),
        "execution_evidence_binding_count": len(execution_bindings),
        "effective_evidence_present_open_gate_count": len(execution_bindings),
        "qualified_product_count": 0,
        "portable_product_count": 0,
        "executed_vertical_acceptance_product_count": 0,
        "build_ready_product_count": 0,
        "ratified_product_count": 0,
        "status": "EFFECTIVE_STRUCTURAL_REBASE_PARTIAL_EXECUTION_EVIDENCE_PRESENT",
    }

    rows_text = "".join(canonical(row) + "\n" for row in sorted(effective_rows, key=lambda r: r["record_id"]))
    summary_text = canonical(summary) + "\n"
    outputs = {
        "effective-gate-state-rebase.jsonl": rows_text,
        "effective-summary.json": summary_text,
        "execution-evidence-bindings.jsonl": "".join(canonical(row) + "\n" for row in sorted(execution_bindings, key=lambda row: row["binding_id"])),
    }
    manifest = {
        "manifest_id": "manifest.product_qualification_effective_state",
        "edition": 1,
        "as_of": AS_OF,
        "inputs": {
            str(programs_path.relative_to(ROOT)): {"sha256": sha256(programs_path), "bytes": programs_path.stat().st_size},
            str(source_summary_path.relative_to(ROOT)): {"sha256": sha256(source_summary_path), "bytes": source_summary_path.stat().st_size},
            str(vacancies_path.relative_to(ROOT)): {"sha256": sha256(vacancies_path), "bytes": vacancies_path.stat().st_size},
            str(subjects_path.relative_to(ROOT)): {"sha256": sha256(subjects_path), "bytes": subjects_path.stat().st_size},
            str(gates_path.relative_to(ROOT)): {"sha256": sha256(gates_path), "bytes": gates_path.stat().st_size},
            str(readiness_summary_path.relative_to(ROOT)): {"sha256": sha256(readiness_summary_path), "bytes": readiness_summary_path.stat().st_size},
            str(rebase_path.relative_to(ROOT)): {"sha256": sha256(rebase_path), "bytes": rebase_path.stat().st_size},
            **{
                row["source_ref"]: {"sha256": row["source_sha256"], "bytes": (ROOT / row["source_ref"]).stat().st_size}
                for row in execution_bindings
            },
            **{
                row["evidence_ref"]: {"sha256": sha256(ROOT / row["evidence_ref"]), "bytes": (ROOT / row["evidence_ref"]).stat().st_size}
                for row in execution_bindings
            },
        },
        "outputs": {
            name: {"sha256": hashlib.sha256(data.encode()).hexdigest(), "bytes": len(data.encode())}
            for name, data in sorted(outputs.items())
        },
        "counts": {
            "rebased_products": structural_rebase_count,
            "rebased_source_gaps": len(rebase_rows),
            "effective_evidence_vacancies": effective_vacancies,
            "execution_evidence_bindings": len(execution_bindings),
        },
    }
    outputs["effective-manifest.json"] = canonical(manifest) + "\n"

    stale: list[str] = []
    for name, data in outputs.items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != data:
                stale.append(name)
        else:
            path.write_text(data, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    print(
        f"{'CHECK' if args.check else 'BUILD'} PASS: {structural_rebase_count} products structurally rebased; "
        f"{len(rebase_rows)} source gaps resolved to implementation qualification; "
        f"{effective_vacancies} effective evidence vacancies"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
