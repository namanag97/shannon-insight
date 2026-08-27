#!/usr/bin/env python3
"""Validate schema/data-contract exact boundaries and non-collapse laws."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_corpus


ROOT = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT/name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8")); data={name:load(name) for name in build_corpus.FILES}
    for name,rows in data.items():
        assert manifest["files"][name]["records"]==len(rows)
        assert manifest["files"][name]["sha256"]==hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    assert len(data["sources.jsonl"])==16 and all(row["url"].startswith("https://") for row in data["sources.jsonl"])
    assert len(data["bounded-contexts.jsonl"])==13
    decisions=data["decision-points.jsonl"]; assert len(decisions)==65 and all(row["default"] is None and row["default_law"]=="forbidden" for row in decisions)
    libs=data["library-contracts.jsonl"]; assert len(libs)==13 and len({row["library_id"] for row in libs})==13
    assert sum(row["library_id"].startswith("library.schema_registry.") for row in libs)==6
    assert sum(row["library_id"].startswith("library.data_contract.") for row in libs)==7
    decision_ids={row["decision_id"] for row in decisions}
    for lib in libs:
        assert len(lib["public_types"])>=11 and len(lib["operations"])==4
        assert set(lib["operation_refs"])=={op["operation_ref"] for op in lib["operations"]}
        assert set(lib["decision_refs"])<=decision_ids and len(lib["decision_refs"])==5
        assert all(op["input_types"] and op["output_type"].startswith("Result<") for op in lib["operations"])
    acceptance=next(row for row in libs if row["library_id"]=="library.data_contract.compatibility_acceptance")
    assert acceptance["effect_boundary"]=="pure_effect_intents" and any(op["operation_ref"].endswith("plan_acceptance") for op in acceptance["operations"])
    laws=" ".join(law for lib in libs for law in lib["laws"]).lower()
    for phrase in ["not schema version", "directional", "not zero impact", "not accepted", "declared obligation, observation", "possible breach", "deprecation, sunset"]: assert phrase in laws, phrase
    offers=[row for row in data["compiler-contracts.jsonl"] if row["record_kind"]=="capability_offer"]
    assert len(data["compiler-contracts.jsonl"])==39 and len(offers)==13 and all(not row["portable"] and not row["selectable"] and row["qualified_implementation_count"]==0 for row in offers)
    assert len(data["negative-twins.jsonl"])==13 and manifest["completion_claim"] is False
    print("VALIDATION PASS schema/data-contract governance: 13 exact boundaries, 65 no-default decisions, 0 qualified offers")


if __name__ == "__main__": main()
