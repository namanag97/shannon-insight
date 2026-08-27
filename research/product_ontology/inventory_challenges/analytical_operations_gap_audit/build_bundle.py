#!/usr/bin/env python3
"""Build deterministic JSON and JSONL views for the analytical-operations gap audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from source_model import HERE, SOURCE, source_bytes


SECTIONS = {
    "sources": "evidence.jsonl",
    "hypotheses": "product-hypotheses.jsonl",
    "deferred_hypotheses": "deferred-hypotheses.jsonl",
    "library_hypotheses": "library-hypotheses.jsonl",
    "collision_tests": "boundary-collision-tests.jsonl",
    "negative_tests": "negative-tests.jsonl",
    "blocking_gaps": "blocking-gaps.jsonl",
}


def jsonl(rows: list[dict[str, Any]]) -> bytes:
    return b"".join((json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode() for row in rows)


def outputs() -> dict[Path, bytes]:
    source = json.loads(source_bytes())
    built = {SOURCE: source_bytes()}
    for section, filename in SECTIONS.items():
        built[HERE / filename] = jsonl(source[section])
    counts = {section: len(source[section]) for section in SECTIONS}
    manifest = {
        "contract_id": source["contract_id"],
        "edition": source["edition"],
        "as_of": source["as_of"],
        "status": source["status"],
        "counts": counts,
        "derived": {
            "promotion_hypotheses": sum(row["preliminary_disposition"] == "promote_for_full_adjudication" for row in source["hypotheses"]),
            "ratified_products": 0,
            "qualified_providers": 0,
            "source_families": sorted({row["family"] for row in source["sources"]}),
        },
    }
    manifest["file_sha256"] = {path.name: hashlib.sha256(content).hexdigest() for path, content in built.items()}
    built[HERE / "manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    return built


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, content in outputs().items():
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                stale.append(path.name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    if stale:
        for name in stale:
            print(f"STALE {name}")
        return 1
    print(f"{'CHECK' if args.check else 'BUILD'} PASS analytical-operations gap audit: {len(outputs())} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
