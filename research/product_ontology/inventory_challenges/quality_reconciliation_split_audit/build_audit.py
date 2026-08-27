#!/usr/bin/env python3
"""Build deterministic views of the quality/reconciliation product-boundary split audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"

PARTITIONS = {
    "replacement_hypotheses": ("replacement-hypotheses.jsonl", "product_split_hypothesis", "hypothesis_id"),
    "library_assignments": ("library-assignments.jsonl", "library_boundary_assignment", "library_ref"),
    "vertical_remaps": ("vertical-remap-proposals.jsonl", "vertical_product_remap", "composition_ref"),
    "negative_tests": ("negative-tests.jsonl", "negative_split_test", "test_id"),
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def payloads() -> dict[str, bytes]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    outputs: dict[str, bytes] = {}
    for section, (filename, record_kind, identity_key) in PARTITIONS.items():
        rows = [
            {"record_kind": record_kind, "edition": source["edition"], **row}
            for row in source[section]
        ]
        rows.sort(key=lambda row: row[identity_key])
        outputs[filename] = "".join(canonical(row) + "\n" for row in rows).encode()
    summary = {
        "audit_id": source["audit_id"],
        "edition": source["edition"],
        "status": source["status"],
        "ruling": source["ruling"],
        "existing_candidate_ref": source["existing_candidate_ref"],
        "replacement_candidate_refs": [row["candidate_id"] for row in source["replacement_hypotheses"]],
        "library_assignment_count": len(source["library_assignments"]),
        "vertical_remap_count": len(source["vertical_remaps"]),
        "negative_test_count": len(source["negative_tests"]),
        "open_gap_count": len(source["open_gaps"]),
        "non_completion_claim": source["non_completion_claim"],
    }
    outputs["summary.json"] = (json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    manifest = {
        "audit_id": source["audit_id"],
        "edition": source["edition"],
        "source_sha256": digest(SOURCE.read_bytes()),
        "files": {name: {"sha256": digest(data), "bytes": len(data)} for name, data in sorted(outputs.items())},
    }
    outputs["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = []
    for filename, content in payloads().items():
        path = HERE / filename
        if not path.exists() or path.read_bytes() != content:
            changed.append(filename)
            if not args.check:
                path.write_bytes(content)
    if args.check and changed:
        print("STALE split-audit files: " + ", ".join(changed))
        return 1
    print("PASS quality/reconciliation split-audit build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
