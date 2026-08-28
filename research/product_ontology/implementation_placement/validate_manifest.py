#!/usr/bin/env python3
"""Validate the digest-bound Python implementation-placement manifest."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_manifest.py"
MANIFEST = HERE / "manifest.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def validate() -> dict[str, Any]:
    if not MANIFEST.is_file():
        fail("manifest missing")
    before = MANIFEST.read_bytes()
    manifest = json.loads(before)
    if manifest.get("manifest_id") != "shannon_python_implementation_placement":
        fail("manifest identity drift")
    if manifest.get("application_product_id") != (
        "application_product.software_engineering.codebase_intelligence"
    ):
        fail("application product identity drift")
    if manifest.get("implementation_id") != "implementation.shannon_python.codebase_insight":
        fail("implementation identity drift")

    paths: set[str] = set()
    role_counts: dict[str, int] = {}
    for record in manifest.get("files", []):
        relative = record.get("path")
        if not isinstance(relative, str) or relative in paths:
            fail(f"invalid or duplicate manifest path: {relative!r}")
        paths.add(relative)
        absolute = ROOT / relative
        if not absolute.is_file():
            fail(f"manifested file missing: {relative}")
        if record.get("sha256") != sha256(absolute):
            fail(f"manifested file digest drift: {relative}")
        if record.get("byte_count") != absolute.stat().st_size:
            fail(f"manifested file size drift: {relative}")
        role = record.get("role")
        role_counts[role] = role_counts.get(role, 0) + 1
    required_roles = {
        "source_model": 3,
        "validator": 4,
        "schema": 2,
        "generated_artifact": 7,
    }
    if role_counts != required_roles:
        fail(f"manifest role counts drift: {role_counts!r}")

    claims = manifest.get("claims", {})
    for allowed_true in (
        "application_boundary_structurally_modeled",
        "module_placement_total_for_current_source_tree",
        "extraction_candidates_exact_source_scoped",
    ):
        if claims.get(allowed_true) is not True:
            fail(f"structural claim missing: {allowed_true}")
    for forbidden in (
        "semantic_ratified",
        "implementation_qualified",
        "portable_offer",
        "executed_vertical_acceptance",
        "build_ready",
        "product_ratified",
        "overall_completion",
    ):
        if claims.get(forbidden) is not False:
            fail(f"manifest illegally promotes {forbidden}")

    stored_digest = manifest.get("manifest_digest")
    without_digest = dict(manifest)
    without_digest.pop("manifest_digest", None)
    if stored_digest != canonical_digest(without_digest):
        fail("manifest digest mismatch")

    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"manifest builder failed:\n{result.stdout}{result.stderr}")
    if MANIFEST.read_bytes() != before:
        fail("manifest is stale or nondeterministic")
    return {
        "manifest_id": manifest["manifest_id"],
        "file_count": len(paths),
        "manifest_digest": stored_digest,
        "status": "VALID",
        "completion_claim": False,
    }


def main() -> int:
    try:
        summary = validate()
    except Exception as exc:
        print(f"FAIL implementation_placement_manifest: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
