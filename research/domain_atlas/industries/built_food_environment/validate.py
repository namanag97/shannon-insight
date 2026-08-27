#!/usr/bin/env python3
"""Validate the built/food/environment publication against its authored corpus."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_module():
    spec = importlib.util.spec_from_file_location("built_food_environment_corpus", HERE / "build_corpus.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def expected_jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for row in rows)


def main() -> int:
    module = load_module()
    summary = module.audit()
    publications = {
        "sources.jsonl": module.SOURCES,
        "data-shapes.jsonl": module.SHAPES,
        "source-systems.jsonl": module.SYSTEMS,
        "analytics-cases.jsonl": module.CASES,
    }
    for name, rows in publications.items():
        assert (HERE / name).read_text(encoding="utf-8") == expected_jsonl(rows), f"stale {name}"
    assert (HERE / "coverage-summary.json").read_text(encoding="utf-8") == json.dumps(summary, indent=2, sort_keys=True) + "\n"
    assert summary["primary_source_ratio"] == 1.0 and summary["llm_dependent_cases"] == 0
    print(
        "PASS built/food/environment industry corpus: "
        f"{summary['sources']} sources, {summary['data_shapes']} shapes, "
        f"{summary['source_system_needs']} source-system needs and {summary['analytical_cases']} cases; "
        "deterministic publication, no completeness or action-authority claim"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
