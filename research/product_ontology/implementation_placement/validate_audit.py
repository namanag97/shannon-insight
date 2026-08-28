#!/usr/bin/env python3
"""Fail-closed validation for the Python placement trace audit."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_audit.py"
AUDIT = HERE / "audit.json"

EXPECTED_REQUIREMENTS = {
    "placement.application_product_boundary",
    "placement.current_source_totality",
    "placement.sovereign_ddd",
    "placement.reusable_extraction_separation",
    "placement.primary_evidence",
    "placement.qualification_separation",
    "placement.deterministic_traceability",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def canonical_digest(value: Any) -> str:
    material = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(material).hexdigest()}"


def validate() -> dict[str, Any]:
    if not AUDIT.is_file():
        fail("placement audit missing")
    before = AUDIT.read_bytes()
    audit = json.loads(before)
    if audit.get("audit_id") != "shannon_python_implementation_placement_completion_audit":
        fail("audit identity drift")
    if audit.get("application_product_id") != (
        "application_product.software_engineering.codebase_intelligence"
    ):
        fail("application product identity drift")
    if audit.get("implementation_id") != "implementation.shannon_python.codebase_insight":
        fail("implementation identity drift")

    requirements = audit.get("requirements", [])
    requirement_ids = [row.get("requirement_id") for row in requirements]
    if set(requirement_ids) != EXPECTED_REQUIREMENTS or len(requirement_ids) != len(
        EXPECTED_REQUIREMENTS
    ):
        fail("audit requirement coverage is incomplete or duplicated")
    digest_paths = {
        row.get("path"): row.get("sha256") for row in audit.get("artifact_digests", [])
    }
    if len(digest_paths) != len(audit.get("artifact_digests", [])):
        fail("audit artifact digest paths are duplicated")
    for relative, stored in digest_paths.items():
        if not isinstance(relative, str):
            fail("audit artifact path is invalid")
        absolute = ROOT / relative
        if not absolute.is_file():
            fail(f"audited artifact missing: {relative}")
        if stored != sha256(absolute):
            fail(f"audited artifact digest drift: {relative}")

    for requirement in requirements:
        if not requirement.get("requirement") or not requirement.get("decision"):
            fail(f"requirement lacks statement or decision: {requirement.get('requirement_id')}")
        if not requirement.get("status") or not requirement.get("remaining_gate"):
            fail(f"requirement lacks status or remaining gate: {requirement.get('requirement_id')}")
        evidence_refs = requirement.get("evidence_refs", [])
        validator_refs = requirement.get("validator_refs", [])
        if not evidence_refs or not validator_refs:
            fail(f"requirement lacks evidence or validator refs: {requirement.get('requirement_id')}")
        for name in evidence_refs + validator_refs:
            relative = f"research/product_ontology/implementation_placement/{name}"
            if relative not in digest_paths:
                fail(f"requirement references unaudited artifact: {name}")

    counts = audit.get("computed_counts", {})
    if counts.get("module_count", 0) < 1 or counts.get("source_file_count", 0) < 1:
        fail("audit source/module counts are empty")
    if counts.get("bounded_context_count", 0) < 8:
        fail("audit DDD context count is too shallow")
    if counts.get("extraction_candidate_count", 0) < 1:
        fail("audit extraction frontier is empty")
    if counts.get("bound_exact_contract_count") != 0:
        fail("audit falsely reports bound exact contracts")
    if counts.get("qualified_extraction_candidate_count") != 0:
        fail("audit falsely reports qualified extraction candidates")
    if counts.get("claim_bound_primary_source_count", 0) < 25:
        fail("audit primary-evidence floor is below 25")

    frontier = audit.get("remaining_frontier", [])
    gates = [row.get("gate") for row in frontier]
    if len(gates) < 7 or len(gates) != len(set(gates)):
        fail("remaining frontier is incomplete or duplicated")
    for row in frontier:
        if not row.get("status") or row.get("count") is None:
            fail(f"remaining frontier row incomplete: {row!r}")

    if audit.get("verdict") != (
        "FOUNDATION_VALIDATED_DOWNSTREAM_AUTHORITY_AND_QUALIFICATION_GATES_OPEN"
    ):
        fail("audit verdict drift")
    for forbidden in (
        "semantic_ratified",
        "implementation_qualified",
        "build_ready",
        "product_ratified",
        "overall_completion_claim",
    ):
        if audit.get(forbidden) is not False:
            fail(f"audit illegally promotes {forbidden}")

    stored_digest = audit.get("audit_digest")
    without_digest = dict(audit)
    without_digest.pop("audit_digest", None)
    if stored_digest != canonical_digest(without_digest):
        fail("audit digest mismatch")

    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"audit builder failed:\n{result.stdout}{result.stderr}")
    if AUDIT.read_bytes() != before:
        fail("audit is stale or nondeterministic")
    return {
        "audit_id": audit["audit_id"],
        "requirement_count": len(requirements),
        "artifact_digest_count": len(digest_paths),
        "audit_digest": stored_digest,
        "status": "VALID",
        "completion_claim": False,
    }


def main() -> int:
    try:
        summary = validate()
    except Exception as exc:
        print(f"FAIL shannon_python_placement_audit: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
