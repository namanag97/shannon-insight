#!/usr/bin/env python3
"""Validate the public/education publication against its authored corpus."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_module():
    spec = importlib.util.spec_from_file_location("public_education_corpus", HERE / "build_corpus.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def expected_jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def main() -> int:
    module = load_module()
    module.validate_local()
    publications = {
        "sources.jsonl": module.SOURCES,
        "source-systems.jsonl": module.SYSTEMS,
        "data-shapes.jsonl": module.SHAPES,
        "analytics-cases.jsonl": module.CASES,
    }
    for name, rows in publications.items():
        assert (HERE / name).read_text(encoding="utf-8") == expected_jsonl(rows), f"stale {name}"
    sectors = {row["record_id"].split(".")[1] for row in module.CASES}
    assert all(row["llm_dependency"] == "none" for row in module.CASES)
    print(
        "PASS public/education industry corpus: "
        f"{len(module.SOURCES)} sources, {len(module.SHAPES)} shapes, "
        f"{len(module.SYSTEMS)} source-system needs and {len(module.CASES)} cases across {len(sectors)} sectors; "
        "deterministic publication, no completeness or decision-authority claim"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
