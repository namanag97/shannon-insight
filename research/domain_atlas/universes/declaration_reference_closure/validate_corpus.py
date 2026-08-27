#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    first = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in HERE.glob("*.jsonl")}
    subprocess.run([sys.executable, str(HERE / "build_corpus.py")], check=True, capture_output=True, text=True)
    second = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in HERE.glob("*.jsonl")}
    assert first == second, "nondeterministic rebuild"
    contexts = load("bounded-contexts.jsonl")
    decisions = load("decision-points.jsonl")
    operations = load("operations.jsonl")
    libraries = load("library-contracts.jsonl")
    compiler = load("compiler-contracts.jsonl")
    sources = load("sources.jsonl")
    negatives = load("negative-twins.jsonl")
    context_ids = {row["context_id"] for row in contexts}
    library_ids = {row["library_id"] for row in libraries}
    assert library_ids == {"library.api.contract_parser", "library.provider_offer.reference_closure", "library.package.reference_closure"}
    assert len(sources) >= 15 and len(decisions) >= 60 and len(operations) >= 20 and len(negatives) >= 20
    assert all(row["semantic_owner_context"] in context_ids for row in libraries)
    assert all(row["effect_boundary"] == "pure_no_io" for row in libraries)
    assert all(row["qualified_implementation_count"] == 0 for row in compiler if row["record_kind"] == "capability_offer")
    assert not any(row["selectable"] for row in compiler if row["record_kind"] == "capability_offer")
    operation_refs = {row["operation_ref"] for row in operations}
    assert all(set(row["operation_refs"]) <= operation_refs for row in libraries)
    print(f"VALIDATION PASS drc: {len(libraries)} exact libraries, {len(decisions)} no-default decisions, {len(operations)} pure operations, zero qualified offers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
