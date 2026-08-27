#!/usr/bin/env python3
"""Validate the energy/resources research pack against schema and local semantics."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - exercised by the documented uv command
    raise SystemExit("jsonschema is required; run with: uv run --with jsonschema python validate_corpus.py") from exc


ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT.parent / "schema" / "industry-research-record.schema.json"
FILES = {
    "sources.jsonl": "source_evidence",
    "source-systems.jsonl": "source_system_need",
    "data-shapes.jsonl": "data_shape_need",
    "analytics-cases.jsonl": "analytical_case",
}
REQUIRED_MODES = {
    "bottleneck",
    "causal",
    "conformance",
    "diagnostic",
    "forecasting",
    "market",
    "material_balance",
    "optimization",
    "process_control",
    "reliability",
    "risk",
    "root_cause",
    "simulation",
    "spatial",
}


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{line_number}: {exc}") from exc
    return records


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    by_file = {name: load_jsonl(ROOT / name) for name in FILES}
    all_records = [record for records in by_file.values() for record in records]

    for name, expected_kind in FILES.items():
        for line_number, record in enumerate(by_file[name], 1):
            try:
                jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(record)
            except jsonschema.ValidationError as exc:
                location = ".".join(str(part) for part in exc.absolute_path)
                raise ValueError(f"{name}:{line_number}:{location}: {exc.message}") from exc
            require(record["record_kind"] == expected_kind, f"{name}:{line_number}: unexpected record kind")

    ids = [record["record_id"] for record in all_records]
    duplicate_ids = sorted(record_id for record_id, count in Counter(ids).items() if count > 1)
    require(not duplicate_ids, f"duplicate record ids: {duplicate_ids}")

    sources = by_file["sources.jsonl"]
    systems = by_file["source-systems.jsonl"]
    shapes = by_file["data-shapes.jsonl"]
    cases = by_file["analytics-cases.jsonl"]
    evidence_ids = {record["record_id"] for record in sources}
    system_ids = {record["record_id"] for record in systems}
    shape_ids = {record["record_id"] for record in shapes}

    require(len(sources) >= 25, "industry-family evidence gate requires at least 25 sources")
    require(len(systems) >= 25, "source-system coverage unexpectedly fell below 25 classes")
    require(len(shapes) >= 25, "data-shape coverage unexpectedly fell below 25 contracts")
    require(len(cases) >= 200, "analytical-case coverage unexpectedly fell below 200 cases")

    for record in systems + shapes + cases:
        unknown = sorted(set(record["evidence_refs"]) - evidence_ids)
        require(not unknown, f"{record['record_id']}: unknown evidence refs {unknown}")
    for record in cases:
        unknown_systems = sorted(set(record["source_system_refs"]) - system_ids)
        unknown_shapes = sorted(set(record["data_shape_refs"]) - shape_ids)
        require(not unknown_systems, f"{record['record_id']}: unknown system refs {unknown_systems}")
        require(not unknown_shapes, f"{record['record_id']}: unknown shape refs {unknown_shapes}")
        require(record.get("metric_only") is False, f"{record['record_id']}: metric-only record is forbidden")
        require(record["sovereign_question"].rstrip().endswith("?"), f"{record['record_id']}: sovereign question is not a question")
        require(bool(record["decision_or_action"].strip()), f"{record['record_id']}: missing decision/action")
        require(bool(record["actors"]), f"{record['record_id']}: missing accountable actors")
        require(len(record["outputs"]) >= 2, f"{record['record_id']}: missing output/run-receipt separation")
        require(record["llm_dependency"] == "prohibited_core", f"{record['record_id']}: unsafe LLM dependency")

    subindustries = {subindustry for record in cases for subindustry in record["subindustry_ids"]}
    modes = {mode for record in cases for mode in record["analytical_modes"]}
    require(len(subindustries) >= 25, "subindustry coverage unexpectedly fell below 25")
    require(REQUIRED_MODES <= modes, f"missing analytical modes: {sorted(REQUIRED_MODES - modes)}")

    print(json.dumps({
        "status": "PASS",
        "records": len(all_records),
        "sources": len(sources),
        "source_system_needs": len(systems),
        "data_shape_needs": len(shapes),
        "analytical_cases": len(cases),
        "subindustries": len(subindustries),
        "analytical_modes": dict(sorted(Counter(mode for record in cases for mode in record["analytical_modes"]).items())),
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
