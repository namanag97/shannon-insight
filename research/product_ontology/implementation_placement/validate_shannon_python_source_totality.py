#!/usr/bin/env python3
"""Fail-closed validation for Python source placement totality."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SRC = ROOT / "src" / "shannon_insight"
BUILDER = HERE / "build_shannon_python_source_totality.py"
OUTPUT = HERE / "shannon-python-source-totality.json"
CROSSWALK = HERE / "shannon-python-module-crosswalk.jsonl"


def fail(message: str) -> None:
    raise AssertionError(message)


def sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def validate() -> dict[str, Any]:
    if not OUTPUT.is_file() or not CROSSWALK.is_file():
        fail("source-totality dependencies are missing")
    before = OUTPUT.read_bytes()
    report = json.loads(before)
    actual = {
        str(path.relative_to(ROOT))
        for path in SRC.rglob("*.py")
        if "__pycache__" not in path.parts
    }
    rows = [
        json.loads(line)
        for line in CROSSWALK.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    represented = {
        source["path"] for row in rows for source in row.get("source_files", [])
    }
    exclusions = report.get("explicit_exclusions", [])
    exclusion_paths = [row.get("path") for row in exclusions]
    if len(exclusion_paths) != len(set(exclusion_paths)):
        fail("duplicate source exclusion")
    for row in exclusions:
        relative = row.get("path")
        if relative != "src/shannon_insight/__init__.py":
            fail(f"unapproved source exclusion: {relative}")
        absolute = ROOT / relative
        if not absolute.is_file() or row.get("sha256") != sha256(absolute):
            fail(f"source exclusion digest drift: {relative}")
        if row.get("disposition") != "PACKAGE_FACADE_OWNED_BY_APPLICATION_ROOT":
            fail("package façade exclusion disposition drift")
        if row.get("owner") != (
            "application_product.software_engineering.codebase_intelligence"
        ):
            fail("package façade owner drift")
        if row.get("semantic_authority") is not False:
            fail("package façade illegally claims semantic authority")
        if row.get("implementation_qualified") is not False:
            fail("package façade illegally claims qualification")
    classified = represented | set(exclusion_paths)
    if classified != actual:
        fail(
            f"source placement is not total: unclassified={sorted(actual - classified)}, "
            f"stale={sorted(classified - actual)}"
        )
    if report.get("unclassified_source_files") != []:
        fail("report retains unclassified source files")
    if report.get("stale_crosswalk_source_files") != []:
        fail("report retains stale crosswalk source files")
    if report.get("actual_python_source_file_count") != len(actual):
        fail("actual source count drift")
    if report.get("module_crosswalk_source_file_count") != len(represented):
        fail("represented source count drift")
    if report.get("explicit_exclusion_count") != len(exclusions):
        fail("source exclusion count drift")
    if report.get("status") != "TOTAL_WITH_EXPLICIT_PACKAGE_FACADE_EXCLUSION":
        fail("source totality status is not closed")
    if report.get("completion_claim") is not False:
        fail("source-totality report illegally claims overall completion")

    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"source-totality builder failed:\n{result.stdout}{result.stderr}")
    if OUTPUT.read_bytes() != before:
        fail("source-totality report is stale or nondeterministic")
    return report


def main() -> int:
    try:
        report = validate()
    except Exception as exc:
        print(f"FAIL shannon_python_source_totality: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
