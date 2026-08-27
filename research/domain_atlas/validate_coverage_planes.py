#!/usr/bin/env python3
"""Validate the governed coverage-plane map and its dependency references."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ALLOWED = {"researched_candidate", "active_research", "partial", "seed_only", "schema_only", "specified_seed", "pilot_only", "missing", "derived_later"}


def main() -> int:
    errors: list[str] = []
    records: list[dict] = []
    with (ROOT / "coverage-planes.jsonl").open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: {exc}")
    ids = {record.get("plane_id") for record in records}
    if None in ids or len(ids) != len(records):
        errors.append("coverage plane IDs are missing or duplicated")
    for record in records:
        plane_id = record.get("plane_id", "<missing>")
        required = {"plane_id", "layer", "name", "status", "depends_on", "artifact_refs", "missing", "compiler_role"}
        absent = sorted(required - set(record))
        if absent:
            errors.append(f"{plane_id} missing {absent}")
        if record.get("status") not in ALLOWED:
            errors.append(f"{plane_id} has invalid status {record.get('status')!r}")
        unknown = sorted(set(record.get("depends_on", [])) - ids)
        if unknown:
            errors.append(f"{plane_id} has unknown dependencies {unknown}")
        if record.get("status") != "researched_candidate" and not record.get("missing"):
            errors.append(f"{plane_id} lacks explicit gaps")
    if len(records) < 60:
        errors.append("coverage map has fewer than 60 independently governed planes")
    if not any(record.get("status") == "missing" for record in records):
        errors.append("coverage map implausibly declares no missing planes")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    print(f"PASS coverage planes: {len(records)} planes; {json.dumps(counts, sort_keys=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

