#!/usr/bin/env python3
"""Fail-closed validation for Python reusable-extraction candidates."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_shannon_python_extraction_frontier.py"
PLACEMENT_BUILDER = HERE / "build_shannon_python_placement.py"
CANDIDATES = HERE / "shannon-python-extraction-candidates.jsonl"
SUMMARY = HERE / "shannon-python-extraction-summary.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def import_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"unable to import {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        fail(f"generated artifact missing: {path.relative_to(ROOT)}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_determinism() -> None:
    before = {path: path.read_bytes() for path in (CANDIDATES, SUMMARY)}
    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"extraction builder failed:\n{result.stdout}{result.stderr}")
    after = {path: path.read_bytes() for path in (CANDIDATES, SUMMARY)}
    for path in before:
        if before[path] != after[path]:
            fail(f"nondeterministic or stale extraction artifact: {path.relative_to(ROOT)}")


def validate() -> dict[str, Any]:
    extraction_builder = import_module(BUILDER, "python_extraction_builder")
    placement_builder = import_module(PLACEMENT_BUILDER, "python_placement_builder_for_extraction")
    rows = load_jsonl(CANDIDATES)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    placement_rows = placement_builder.discover_modules()
    expected = {
        row["module"]
        for row in placement_rows
        if row["implementation_role"] in extraction_builder.ELIGIBLE_ROLES
    }
    modules = [row.get("module") for row in rows]
    if len(modules) != len(set(modules)):
        fail("duplicate extraction candidate module")
    if set(modules) != expected:
        fail(
            "extraction frontier is not total over eligible roles: "
            f"missing={sorted(expected - set(modules))}, extra={sorted(set(modules) - expected)}"
        )

    family_ids = placement_builder.existing_family_ids()
    for row in rows:
        module = row.get("module")
        if row.get("record_kind") != "python_library_extraction_candidate":
            fail(f"unexpected record kind for {module}")
        if row.get("implementation_id") != "implementation.shannon_python.codebase_insight":
            fail(f"implementation identity drift for {module}")
        if row.get("application_product_id") != placement_builder.APPLICATION_PRODUCT_ID:
            fail(f"application-product identity drift for {module}")
        expected_disposition = extraction_builder.ELIGIBLE_ROLES.get(
            row.get("implementation_role")
        )
        if row.get("candidate_disposition") != expected_disposition:
            fail(f"candidate disposition drift for {module}")
        unknown = set(row.get("horizontal_coverage_coordinates", [])) - family_ids
        if unknown:
            fail(f"unknown horizontal coverage coordinates for {module}: {sorted(unknown)}")
        if row.get("exact_abstract_contract_id") is not None:
            fail(f"{module} claims an exact abstract contract without adjudication")
        if row.get("semantic_owner_id") is not None:
            fail(f"{module} claims a semantic owner without authority")
        if row.get("contract_binding_status") != "UNBOUND_EXACT_CONTRACT_REQUIRED":
            fail(f"{module} contract binding was promoted")
        for flag in (
            "library_extraction_allowed",
            "implementation_qualified",
            "portable_offer",
            "product_promotion",
            "completion_claim",
        ):
            if row.get(flag) is not False:
                fail(f"{module} illegally promotes {flag}")
        if len(row.get("required_gates", [])) < 10:
            fail(f"{module} omits required qualification gates")
        if len(row.get("refusal_laws", [])) < 4:
            fail(f"{module} omits extraction refusal laws")
        source_files = row.get("source_files")
        if not isinstance(source_files, list) or not source_files:
            fail(f"{module} has no exact source scope")
        digest_material: list[str] = []
        public_count = 0
        observed_effects: set[str] = set()
        for source in source_files:
            relative = source.get("path")
            if not isinstance(relative, str) or not relative.startswith("src/shannon_insight/"):
                fail(f"invalid source path for {module}: {relative!r}")
            absolute = ROOT / relative
            if not absolute.is_file():
                fail(f"source missing for {module}: {relative}")
            digest = sha256_file(absolute)
            if source.get("sha256") != digest:
                fail(f"source digest drift for {module}: {relative}")
            digest_material.append(f"{relative}\0{digest}")
            public_count += len(source.get("public_symbols", []))
            observed_effects.update(source.get("effect_signals", []))
            if source.get("parse_status") not in {"PARSED", "SYNTAX_REFUSED"}:
                fail(f"invalid parse status for {module}: {relative}")
        expected_digest = "sha256:" + hashlib.sha256(
            "\n".join(sorted(digest_material)).encode("utf-8")
        ).hexdigest()
        if row.get("source_scope_digest") != expected_digest:
            fail(f"source-scope digest drift for {module}")
        if row.get("public_api_symbol_count") != public_count:
            fail(f"public API count drift for {module}")
        if sorted(row.get("static_effect_signals", [])) != sorted(observed_effects):
            fail(f"effect-signal aggregation drift for {module}")
        expected_purity = (
            "EFFECTFUL_OR_PURITY_UNPROVEN"
            if observed_effects or row.get("parse_refusals")
            else "PURE_CANDIDATE_UNPROVEN"
        )
        if row.get("purity_posture") != expected_purity:
            fail(f"purity posture drift for {module}")

    if summary.get("candidate_count") != len(rows):
        fail("extraction summary candidate count drift")
    for key in (
        "candidates_with_bound_exact_contract",
        "candidates_allowed_for_extraction",
        "qualified_candidate_count",
        "portable_offer_count",
    ):
        if summary.get(key) != 0:
            fail(f"extraction summary illegally promotes {key}")
    if summary.get("completion_claim") is not False:
        fail("extraction summary illegally claims completion")

    validate_determinism()
    return summary


def main() -> int:
    try:
        summary = validate()
    except Exception as exc:
        print(f"FAIL shannon_python_extraction_frontier: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
