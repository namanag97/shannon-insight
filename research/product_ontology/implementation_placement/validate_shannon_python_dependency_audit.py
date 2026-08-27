#!/usr/bin/env python3
"""Fail-closed validation for the Python internal-dependency audit."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_shannon_python_dependency_audit.py"
PLACEMENT_BUILDER = HERE / "build_shannon_python_placement.py"
AUDIT = HERE / "shannon-python-dependency-audit.json"
EDGES = HERE / "shannon-python-dependency-edges.jsonl"


def fail(message: str) -> None:
    raise AssertionError(message)


def import_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"unable to import {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"dependency edge artifact missing: {path.relative_to(ROOT)}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate() -> dict[str, Any]:
    if not AUDIT.is_file():
        fail("dependency audit missing")
    before = {path: path.read_bytes() for path in (AUDIT, EDGES)}
    dependency_builder = import_module(BUILDER, "python_dependency_builder")
    placement_builder = import_module(PLACEMENT_BUILDER, "python_dependency_placement")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    edges = load_jsonl(EDGES)
    placement_rows = placement_builder.discover_modules()
    roles = {row["module"]: row["implementation_role"] for row in placement_rows}
    known_modules = set(roles)

    edge_ids = [row.get("edge_id") for row in edges]
    edge_pairs = [(row.get("source_module"), row.get("target_module")) for row in edges]
    if len(edge_ids) != len(set(edge_ids)) or len(edge_pairs) != len(set(edge_pairs)):
        fail("dependency edges are duplicated")
    for row in edges:
        source = row.get("source_module")
        target = row.get("target_module")
        if source not in known_modules or target not in known_modules:
            fail(f"dependency edge references unknown module: {source} -> {target}")
        if source == target:
            fail(f"self edge should remain internal to its module: {source}")
        if row.get("source_role") != roles[source] or row.get("target_role") != roles[target]:
            fail(f"dependency role drift: {source} -> {target}")
        expected_classification = dependency_builder.classify_edge(roles[source], roles[target])
        if row.get("classification") != expected_classification:
            fail(f"dependency classification drift: {source} -> {target}")
        observations = row.get("observations")
        if not isinstance(observations, list) or not observations:
            fail(f"dependency edge has no source observation: {source} -> {target}")
        for observation in observations:
            relative = observation.get("path")
            line = observation.get("line")
            if not isinstance(relative, str) or not (ROOT / relative).is_file():
                fail(f"dependency observation path missing: {relative}")
            if not isinstance(line, int) or line < 1:
                fail(f"dependency observation line invalid: {relative}:{line}")
        expected_digest = canonical_digest(
            {
                "source_module": source,
                "target_module": target,
                "observations": observations,
            }
        )
        if row.get("edge_digest") != expected_digest:
            fail(f"dependency edge digest drift: {source} -> {target}")
        for forbidden in (
            "semantic_authority",
            "qualification_claim",
            "completion_claim",
        ):
            if row.get(forbidden) is not False:
                fail(f"dependency edge illegally promotes {forbidden}: {source} -> {target}")

    classification_counts = Counter(row["classification"] for row in edges)
    if audit.get("module_count") != len(known_modules):
        fail("dependency audit module count drift")
    if audit.get("internal_dependency_edge_count") != len(edges):
        fail("dependency audit edge count drift")
    if audit.get("classification_counts") != dict(sorted(classification_counts.items())):
        fail("dependency classification counts drift")
    blocker_count = sum(
        row["classification"] != "APPLICATION_LOCAL_EDGE" for row in edges
    )
    if audit.get("extraction_blocking_or_contract_edge_count") != blocker_count:
        fail("dependency blocker count drift")
    if audit.get("unresolved_import_observations") != []:
        fail(
            "internal import resolution is incomplete: "
            f"{audit.get('unresolved_import_observations')[:5]!r}"
        )
    if len(audit.get("extraction_laws", [])) < 5:
        fail("dependency audit omits extraction laws")
    for scc in audit.get("nontrivial_sccs", []):
        modules = scc.get("modules", [])
        if len(modules) < 2 or any(module not in known_modules for module in modules):
            fail(f"invalid nontrivial SCC: {modules!r}")
        if scc.get("roles") != sorted({roles[module] for module in modules}):
            fail(f"SCC role drift: {modules!r}")
        if scc.get("disposition") != "REQUIRES_SEAM_ADJUDICATION_BEFORE_EXTRACTION":
            fail(f"SCC disposition drift: {modules!r}")
    if audit.get("nontrivial_scc_count") != len(audit.get("nontrivial_sccs", [])):
        fail("nontrivial SCC count drift")
    if audit.get("status") != "OBSERVED_DEPENDENCY_TOPOLOGY_EXTRACTION_SEAMS_UNADJUDICATED":
        fail("dependency audit status drift")
    for forbidden in (
        "semantic_ratified",
        "implementation_qualified",
        "completion_claim",
    ):
        if audit.get(forbidden) is not False:
            fail(f"dependency audit illegally promotes {forbidden}")
    stored_digest = audit.get("audit_digest")
    without_digest = dict(audit)
    without_digest.pop("audit_digest", None)
    if stored_digest != canonical_digest(without_digest):
        fail("dependency audit digest mismatch")

    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"dependency audit builder failed:\n{result.stdout}{result.stderr}")
    after = {path: path.read_bytes() for path in (AUDIT, EDGES)}
    for path in before:
        if before[path] != after[path]:
            fail(f"dependency artifact is stale or nondeterministic: {path.relative_to(ROOT)}")
    return {
        "report_id": audit["report_id"],
        "module_count": audit["module_count"],
        "edge_count": len(edges),
        "blocker_count": blocker_count,
        "nontrivial_scc_count": audit["nontrivial_scc_count"],
        "audit_digest": stored_digest,
        "status": "VALID",
        "completion_claim": False,
    }


def main() -> int:
    try:
        summary = validate()
    except Exception as exc:
        print(f"FAIL shannon_python_dependency_audit: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
