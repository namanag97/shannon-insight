#!/usr/bin/env python3
"""Fail-closed validation for the Shannon Python implementation placement."""
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
BUILDER = HERE / "build_shannon_python_placement.py"
PLACEMENT = HERE / "shannon-python-placement.json"
CROSSWALK = HERE / "shannon-python-module-crosswalk.jsonl"
SUMMARY = HERE / "summary.json"

REQUIRED_NON_COLLAPSE_LAWS = {
    "shannon_python_package != universal_enterprise_data_platform",
    "codebase_analysis_application != horizontal_analytics_product_family",
    "implementation_module != semantic_authority",
    "algorithm_implementation != qualified_method_contract",
    "local_storage_or_query_support != storage_or_query_product",
    "application_kernel != solution_compiler_or_reconciler",
    "Git_or_source_code_observation != universal_source_system_contract",
    "renderer_or_dashboard != analytical_result_meaning",
    "same_campaign_tests != independent_qualification",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"required generated artifact missing: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"expected object in {path.relative_to(ROOT)}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        fail(f"required generated artifact missing: {path.relative_to(ROOT)}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            fail(f"expected object at {path.relative_to(ROOT)}:{line_number}")
        rows.append(value)
    return rows


def import_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("shannon_python_placement_builder", BUILDER)
    if spec is None or spec.loader is None:
        fail("unable to import placement builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_determinism() -> None:
    before = {
        path: path.read_bytes()
        for path in (PLACEMENT, CROSSWALK, SUMMARY)
        if path.exists()
    }
    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"builder failed:\n{result.stdout}{result.stderr}")
    after = {path: path.read_bytes() for path in (PLACEMENT, CROSSWALK, SUMMARY)}
    if set(before) != set(after):
        fail("generated placement artifact set changed during validation")
    for path, payload in before.items():
        if after[path] != payload:
            fail(f"nondeterministic or stale generated artifact: {path.relative_to(ROOT)}")


def validate() -> dict[str, Any]:
    builder = import_builder()
    placement = load_json(PLACEMENT)
    summary = load_json(SUMMARY)
    rows = load_jsonl(CROSSWALK)

    discovered = builder.discover_modules()
    expected_modules = {row["module"] for row in discovered}
    actual_modules = [row.get("module") for row in rows]
    if len(actual_modules) != len(set(actual_modules)):
        fail("module crosswalk contains duplicate module identities")
    if set(actual_modules) != expected_modules:
        fail(
            "module crosswalk is not total: "
            f"missing={sorted(expected_modules - set(actual_modules))}, "
            f"extra={sorted(set(actual_modules) - expected_modules)}"
        )

    family_ids = builder.existing_family_ids()
    observed_paths: set[str] = set()
    for row in rows:
        if row.get("record_kind") != "python_module_placement":
            fail(f"unexpected record kind for module {row.get('module')}")
        if row.get("application_product_id") != builder.APPLICATION_PRODUCT_ID:
            fail(f"module {row.get('module')} is bound to the wrong application product")
        if row.get("semantic_authority") is not False:
            fail(f"module {row.get('module')} illegally claims semantic authority")
        if row.get("implementation_qualified") is not False:
            fail(f"module {row.get('module')} illegally claims qualification")
        if row.get("product_ratified") is not False:
            fail(f"module {row.get('module')} illegally claims product ratification")
        unknown = set(row.get("horizontal_coverage_coordinates", [])) - family_ids
        if unknown:
            fail(f"module {row.get('module')} uses unknown horizontal coordinates: {sorted(unknown)}")
        files = row.get("source_files")
        if not isinstance(files, list) or not files:
            fail(f"module {row.get('module')} has no source-file evidence")
        if row.get("file_count") != len(files):
            fail(f"file count drift for module {row.get('module')}")
        computed_lines = 0
        for source in files:
            relative = source.get("path")
            if not isinstance(relative, str) or not relative.startswith("src/shannon_insight/"):
                fail(f"invalid source path for module {row.get('module')}: {relative!r}")
            if relative in observed_paths:
                fail(f"source file assigned to more than one module: {relative}")
            observed_paths.add(relative)
            absolute = ROOT / relative
            if not absolute.is_file():
                fail(f"source file missing: {relative}")
            if source.get("sha256") != sha256_file(absolute):
                fail(f"source digest drift: {relative}")
            lines = len(absolute.read_text(encoding="utf-8", errors="replace").splitlines())
            if source.get("line_count") != lines:
                fail(f"source line-count drift: {relative}")
            computed_lines += lines
        if row.get("line_count") != computed_lines:
            fail(f"module line-count drift for {row.get('module')}")

    if placement.get("implementation_id") != "implementation.shannon_python.codebase_insight":
        fail("unexpected implementation identity")
    if placement.get("placement_verdict") != (
        "RETAIN_AS_APPLICATION_PRODUCT_AND_QUALIFICATION_PROVING_IMPLEMENTATION"
    ):
        fail("unexpected Python placement verdict")
    product = placement.get("application_product", {})
    if product.get("product_id") != builder.APPLICATION_PRODUCT_ID:
        fail("application-product identity drift")
    if product.get("product_plane") != "application_domain_product_candidate":
        fail("Python application was not kept on the application-domain product plane")
    if placement.get("unknown_horizontal_coverage_coordinates") != []:
        fail("placement contains unknown horizontal coverage coordinates")
    if placement.get("completion_claim") is not False:
        fail("placement illegally claims completion")
    if placement.get("qualification_posture", {}).get("status") != (
        "UNQUALIFIED_IMPLEMENTATION_CANDIDATE"
    ):
        fail("placement qualification posture was promoted without evidence")
    laws = set(placement.get("non_collapse_laws", []))
    missing_laws = REQUIRED_NON_COLLAPSE_LAWS - laws
    if missing_laws:
        fail(f"required non-collapse laws missing: {sorted(missing_laws)}")

    if placement.get("module_count") != len(rows):
        fail("placement module count drift")
    if placement.get("source_file_count") != len(observed_paths):
        fail("placement source-file count drift")
    if placement.get("source_line_count") != sum(row["line_count"] for row in rows):
        fail("placement source-line count drift")

    if summary.get("module_count") != len(rows):
        fail("summary module count drift")
    if summary.get("source_file_count") != len(observed_paths):
        fail("summary source-file count drift")
    if summary.get("source_line_count") != placement.get("source_line_count"):
        fail("summary source-line count drift")
    if summary.get("projection_digest") != placement.get("projection_digest"):
        fail("summary/placement digest mismatch")
    for forbidden in ("implementation_qualified", "product_ratified", "completion_claim"):
        if summary.get(forbidden) is not False:
            fail(f"summary illegally promotes {forbidden}")

    validate_determinism()
    return summary


def main() -> int:
    try:
        summary = validate()
    except Exception as exc:
        print(f"FAIL shannon_python_placement: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
