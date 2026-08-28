#!/usr/bin/env python3
"""Fail-closed validation for claim-bound Python placement evidence."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_python_placement_evidence.py"
EVIDENCE = HERE / "shannon-python-placement-evidence.jsonl"
SUMMARY = HERE / "shannon-python-placement-evidence-summary.json"

ALLOWED_ROLES = {
    "architecture",
    "standard",
    "product_boundary_evidence",
    "empirical_validation",
}
ALLOWED_SOURCE_KINDS = {
    "official_specification",
    "standard",
    "official_documentation",
    "official_product_documentation",
    "official_project_documentation",
    "official_research_guidance",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"evidence artifact missing: {path.relative_to(ROOT)}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate() -> dict[str, Any]:
    if not SUMMARY.is_file():
        fail("evidence summary missing")
    before = {path: path.read_bytes() for path in (EVIDENCE, SUMMARY)}
    rows = load_jsonl(EVIDENCE)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if len(rows) < 25:
        fail("primary-source evidence floor is below 25")
    source_ids = [row.get("source_id") for row in rows]
    urls = [row.get("url") for row in rows]
    if len(source_ids) != len(set(source_ids)):
        fail("duplicate evidence source identity")
    if len(urls) != len(set(urls)):
        fail("duplicate evidence URL")
    for row in rows:
        source_id = row.get("source_id")
        if row.get("evidence_role") not in ALLOWED_ROLES:
            fail(f"unknown evidence role for {source_id}")
        if row.get("source_kind") not in ALLOWED_SOURCE_KINDS:
            fail(f"unknown source kind for {source_id}")
        parsed = urlparse(str(row.get("url", "")))
        if parsed.scheme != "https" or not parsed.netloc:
            fail(f"evidence locator is not an absolute HTTPS URL: {source_id}")
        if len(str(row.get("bounded_claim", ""))) < 40:
            fail(f"bounded claim missing or too weak: {source_id}")
        if not isinstance(row.get("supports"), list) or len(row["supports"]) < 2:
            fail(f"support claims missing: {source_id}")
        if not isinstance(row.get("does_not_prove"), list) or len(row["does_not_prove"]) < 2:
            fail(f"explicit non-proof missing: {source_id}")
        if row.get("last_verified") != "2026-08-27":
            fail(f"verification date drift: {source_id}")
        for forbidden in (
            "semantic_authority",
            "implementation_qualification_claim",
            "product_ratification_claim",
            "completion_claim",
        ):
            if row.get(forbidden) is not False:
                fail(f"evidence row illegally promotes {forbidden}: {source_id}")
    if summary.get("source_count") != len(rows):
        fail("evidence summary count drift")
    if summary.get("sources_with_bounded_claim") != len(rows):
        fail("not every source has a bounded claim")
    if summary.get("sources_with_explicit_non_proof") != len(rows):
        fail("not every source has an explicit non-proof")
    for key in (
        "semantic_authority_claim_count",
        "qualification_claim_count",
    ):
        if summary.get(key) != 0:
            fail(f"evidence summary illegally promotes {key}")
    if summary.get("completion_claim") is not False:
        fail("evidence summary illegally claims completion")

    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"evidence builder failed:\n{result.stdout}{result.stderr}")
    after = {path: path.read_bytes() for path in (EVIDENCE, SUMMARY)}
    for path in before:
        if before[path] != after[path]:
            fail(f"evidence artifact is stale or nondeterministic: {path.relative_to(ROOT)}")
    return summary


def main() -> int:
    try:
        summary = validate()
    except Exception as exc:
        print(f"FAIL shannon_python_placement_evidence: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
