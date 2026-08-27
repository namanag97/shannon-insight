#!/usr/bin/env python3
"""Independently audit the preserved GPT Pro delta without promoting it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DELTA = HERE / "output-2026-08-27"

PRIMARY_IDS = {
    "applicability-resolutions.jsonl": "applicability_resolution_id",
    "capability-product-library-wiring-deltas.jsonl": "wiring_delta_id",
    "conflicts-vacancies-and-open-questions.jsonl": "vacancy_id",
    "convergence-dag.jsonl": "work_id",
    "exact-contract-research-dispositions.jsonl": "contract_disposition_id",
    "gap-dispositions.jsonl": "gap_disposition_id",
    "gap-frontier-disposition.jsonl": "gap_disposition_id",
    "library-boundary-deltas.jsonl": "library_delta_id",
    "lossless-quotient-projection.jsonl": "atom_ref",
    "member-axis-research-resolutions.jsonl": "member_axis_resolution_id",
    "product-boundary-deltas.jsonl": "delta_id",
    "product-dossier-deltas.jsonl": "dossier_delta_id",
    "semantic-decision-kernels.jsonl": "kernel_id",
    "source-authority-resolutions.jsonl": "source_authority_resolution_id",
    "source-register.jsonl": "source_id",
    "symbol-occurrence-migrations.jsonl": "input_occurrence_ref",
    "symbol-owner-resolutions.jsonl": "input_docket_ref",
    "vertical-falsification-cases.jsonl": "case_id",
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    report = json.loads((DELTA / "validation-report.json").read_text(encoding="utf-8"))
    expected_counts = report["jsonl_counts"]
    errors: list[str] = []

    for filename, id_field in PRIMARY_IDS.items():
        path = DELTA / filename
        if not path.is_file():
            errors.append(f"missing {filename}")
            continue
        rows = load_jsonl(path)
        if len(rows) != expected_counts.get(filename):
            errors.append(f"{filename}: count {len(rows)} != {expected_counts.get(filename)}")
        ids = [row.get(id_field) for row in rows]
        if any(value is None for value in ids):
            errors.append(f"{filename}: missing primary id {id_field}")
        if len(ids) != len(set(ids)):
            errors.append(f"{filename}: duplicate primary id {id_field}")
        if any(row.get("completion_claim") is not False for row in rows):
            errors.append(f"{filename}: completion claim is not uniformly false")

    inventory = json.loads((DELTA / "input-inventory.json").read_text(encoding="utf-8"))
    matched = changed = missing = 0
    for row in inventory["entries"]:
        path = REPO / row["path"]
        if not path.is_file():
            missing += 1
        elif hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]:
            matched += 1
        else:
            changed += 1

    counts = report["counts"]
    guarded_zeroes = [
        "invented_build_ready_products", "invented_implementations", "invented_portable_offers",
        "invented_qualified_providers", "invented_ratified_products", "invented_vertical_acceptances",
    ]
    if any(counts.get(field) != 0 for field in guarded_zeroes):
        errors.append("validation report claims invented downstream evidence")
    if counts.get("input_gap_quotients") != 686 or counts.get("input_represented_atoms") != 16687:
        errors.append("advertised frontier accounting drift")

    result = {
        "status": "FAIL" if errors else "ACCEPT_CANDIDATE_OVERLAY_REBASE_REQUIRED",
        "package_status": report.get("status"),
        "jsonl_files": len(PRIMARY_IDS),
        "input_inventory": {"total": len(inventory["entries"]), "matched": matched, "changed": changed, "missing": missing},
        "canonical_promotion": False,
        "errors": errors,
    }
    print(json.dumps(result, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
