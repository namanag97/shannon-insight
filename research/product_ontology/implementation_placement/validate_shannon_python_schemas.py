#!/usr/bin/env python3
"""Validate generated Python placement artifacts against their JSON Schemas."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - fail-closed runtime guard
    print("FAIL shannon_python_schema: jsonschema is required", file=sys.stderr)
    raise SystemExit(1) from exc

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def main() -> int:
    try:
        placement_schema = json.loads(
            (HERE / "shannon-python-placement.schema.json").read_text(encoding="utf-8")
        )
        crosswalk_schema = json.loads(
            (HERE / "shannon-python-module-crosswalk.schema.json").read_text(
                encoding="utf-8"
            )
        )
        placement = json.loads(
            (HERE / "shannon-python-placement.json").read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator.check_schema(placement_schema)
        jsonschema.Draft202012Validator.check_schema(crosswalk_schema)
        jsonschema.validate(instance=placement, schema=placement_schema)
        row_count = 0
        for line_number, line in enumerate(
            (HERE / "shannon-python-module-crosswalk.jsonl")
            .read_text(encoding="utf-8")
            .splitlines(),
            1,
        ):
            if not line.strip():
                continue
            row_count += 1
            try:
                row = json.loads(line)
                jsonschema.validate(instance=row, schema=crosswalk_schema)
            except Exception as exc:
                raise AssertionError(
                    f"module crosswalk schema failure at line {line_number}: {exc}"
                ) from exc
        if row_count == 0:
            raise AssertionError("module crosswalk is empty")
    except Exception as exc:
        print(f"FAIL shannon_python_schema: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "report_id": "shannon_python_placement_schema_validation",
                "module_row_count": row_count,
                "status": "VALID",
                "completion_claim": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
