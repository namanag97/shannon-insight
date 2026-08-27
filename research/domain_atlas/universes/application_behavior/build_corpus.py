#!/usr/bin/env python3
"""Materialize the deterministic application-behavior candidate corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from source_model import AS_OF, EDITION, records

ROOT = Path(__file__).resolve().parent
GENERATED_JSONL = tuple(records().keys())


def record_key(row: dict[str, Any]) -> str:
    if "id" in row:
        return row["id"]
    keys = sorted(key for key in row if key.endswith("_id"))
    if not keys:
        raise ValueError("record has no deterministic identifier")
    return row[keys[0]]


def render(rows: Iterable[dict[str, Any]]) -> bytes:
    ordered = sorted(rows, key=record_key)
    return ("\n".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for row in ordered) + "\n").encode("utf-8")


def render_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def coverage(rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    libraries = rows["library-contracts.jsonl"]
    offers = rows["requirements-offers.jsonl"]
    tests = rows["conformance-tests.jsonl"]
    edges = rows["assembly-edges.jsonl"]
    return {
        "coverage_id": "coverage.application_behavior.v0_1_0",
        "universe_id": "application_behavior",
        "edition": EDITION,
        "as_of": AS_OF,
        "status": "specified_candidate_open_world",
        "completion_claim": False,
        "counts": {
            "sources": len(rows["sources.jsonl"]),
            "bounded_contexts": len(rows["bounded-contexts.jsonl"]),
            "semantic_contracts": len(rows["semantic-contracts.jsonl"]),
            "state_machines": len(rows["state-machines.jsonl"]),
            "state_transitions": len(rows["state-transitions.jsonl"]),
            "libraries": len(libraries),
            "operations": len(rows["operations.jsonl"]),
            "boundary_decisions": len(rows["boundary-decisions.jsonl"]),
            "crosswalks": len(rows["crosswalks.jsonl"]),
            "requirements": sum(1 for row in offers if row.get("requirement_id", "").startswith("requirement.")),
            "offers": sum(1 for row in offers if row.get("offer_id", "").startswith("offer.")),
            "conformance_tests": len(tests),
            "negative_twins": len(rows["negative-twins.jsonl"]),
            "assembly_edges": len(edges),
            "open_gaps": len(rows["gaps.jsonl"]),
        },
        "qualification": {
            "qualified_implementations": 0,
            "portable_offers": 0,
            "binding_eligible_offers": 0,
            "executed_conformance_tests": sum(1 for row in tests if row["execution_status"] == "executed"),
            "vertical_acceptance_receipts": 0,
        },
        "assembly_mechanisms": sorted({edge["resolution_mechanism"] for edge in edges}),
        "imports": [
            "universe.data_type",
            "universe.operation",
            "universe.pipeline_dataflow",
            "universe.persistence",
            "universe.security_privacy_trust",
            "universe.runtime_resource",
            "universe.lineage_provenance_evidence",
            "universe.consumption",
        ],
        "blocking_gaps": [row["gap_id"] for row in sorted(rows["gaps.jsonl"], key=record_key)],
        "claim_boundary": "This corpus specifies candidate contracts and evidence obligations. It is not a complete ontology, qualified implementation set, portable provider offer, product definition, solution pack, or executed application.",
    }


def expected_payloads() -> dict[str, bytes]:
    rows = records()
    payloads = {name: render(items) for name, items in rows.items()}
    payloads["coverage-report.json"] = render_json(coverage(rows))
    manifest_files = {
        name: {"records": len(rows[name]), "sha256": sha256(payload)}
        for name, payload in payloads.items()
        if name.endswith(".jsonl")
    }
    payloads["manifest.json"] = render_json({
        "manifest_id": "application_behavior_v0_1_0",
        "edition": EDITION,
        "as_of": AS_OF,
        "status": "specified_candidate_open_world",
        "completion_claim": False,
        "generator": "build_corpus.py + source_model.py",
        "files": manifest_files,
        "schema_refs": [
            "schemas/record.schema.json",
            "schemas/manifest.schema.json",
            "schemas/coverage-report.schema.json",
        ],
        "qualification": {"qualified_implementation_count": 0, "binding_eligible_offer_count": 0, "executed_test_count": 0},
    })
    return payloads


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files drift from source_model.py")
    args = parser.parse_args()
    payloads = expected_payloads()
    mismatches: list[str] = []
    for name, payload in payloads.items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_bytes() != payload:
                mismatches.append(name)
        else:
            path.write_bytes(payload)
    if args.check:
        if mismatches:
            print("DRIFT: " + ", ".join(sorted(mismatches)))
            return 1
        print(f"PASS application_behavior deterministic build: {len(payloads)} generated files")
        return 0
    print(f"WROTE application_behavior: {len(payloads)} generated files; completion_claim=false")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    raise SystemExit(main())
