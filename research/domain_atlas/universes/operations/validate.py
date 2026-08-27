#!/usr/bin/env python3
"""Validate the typed-operation hypothesis queue and deterministic seed."""
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
    records = load_jsonl(HERE / "operation-candidates.jsonl")
    catalog = json.loads((HERE / "family-catalog.json").read_text(encoding="utf-8"))
    schema = json.loads((HERE / "typed-operation.schema.json").read_text(encoding="utf-8"))
    assert len(records) == len({row["operation_id"] for row in records}) == catalog["candidate_count"]
    assert len({row["family_id"] for row in records}) == catalog["family_count"]
    assert catalog["completion_claim"] is False and all(row["status"] == "hypothesis" for row in records)
    validator = jsonschema.Draft202012Validator(schema)
    for row in records:
        validator.validate(row)

    spec = importlib.util.spec_from_file_location("operations_seed", HERE / "build_seed.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="operations-check-") as temp:
        module.HERE = Path(temp)
        with contextlib.redirect_stdout(io.StringIO()):
            assert module.main() == 0
        for name in ("operation-candidates.jsonl", "family-catalog.json"):
            assert (Path(temp) / name).read_bytes() == (HERE / name).read_bytes(), f"stale {name}"
    print(f"PASS typed-operation universe: {len(records)} hypothesis records across {catalog['family_count']} families; deterministic; no semantic-owner or compilability claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

