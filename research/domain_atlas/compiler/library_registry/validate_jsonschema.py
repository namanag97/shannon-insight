#!/usr/bin/env python3
"""Validate every unified-registry record with a standards-complete JSON Schema engine.

Run with: uv run --with jsonschema python validate_jsonschema.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema


HERE = Path(__file__).resolve().parent


def main() -> int:
    schema = json.loads((HERE / "library-registry.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    count = 0
    for line_number, line in enumerate((HERE / "registry.jsonl").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        count += 1
        record = json.loads(line)
        for error in validator.iter_errors(record):
            errors.append(f"registry.jsonl:{line_number}:{'/'.join(str(x) for x in error.path)}: {error.message}")
    if errors:
        print(f"FAIL: {len(errors)} JSON Schema error(s)")
        for error in errors[:100]:
            print(f"- {error}")
        return 1
    print(json.dumps({"status": "PASS", "draft": "2020-12", "records": count}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
