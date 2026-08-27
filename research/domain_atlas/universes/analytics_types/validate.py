#!/usr/bin/env python3
"""Validate the analytical-practice hypothesis queue and deterministic seed."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    records = load_jsonl(HERE / "candidate-practices.jsonl")
    catalog = json.loads((HERE / "family-catalog.json").read_text(encoding="utf-8"))
    schema = json.loads((HERE / "analytics-practice.schema.json").read_text(encoding="utf-8"))
    evidence = {row["evidence_id"] for row in load_jsonl(HERE / "evidence.jsonl")}
    assert len(records) == len({row["practice_id"] for row in records}) == catalog["candidate_count"]
    assert len({row["family_id"] for row in records}) == catalog["family_count"]
    assert catalog["completion_claim"] is False and all(row["status"] == "hypothesis" for row in records)
    assert all(set(row["evidence_refs"]) <= evidence for row in records)
    validator = jsonschema.Draft202012Validator(schema)
    for row in records:
        validator.validate(row)

    spec = importlib.util.spec_from_file_location("analytics_types_seed", HERE / "build_seed.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="analytics-types-check-") as temp:
        module.HERE = Path(temp)
        with contextlib.redirect_stdout(io.StringIO()):
            assert module.main() == 0
        for name in ("candidate-practices.jsonl", "family-catalog.json"):
            assert (Path(temp) / name).read_bytes() == (HERE / name).read_bytes(), f"stale {name}"
    print(f"PASS analytical-practice universe: {len(records)} hypothesis records across {catalog['family_count']} families; deterministic; no identity or completeness claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

