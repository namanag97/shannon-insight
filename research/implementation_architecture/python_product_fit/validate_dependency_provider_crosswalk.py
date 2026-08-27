#!/usr/bin/env python3
"""Fail-closed validation for declared Python provider dependencies."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENERATED = (
    "dependency-provider-crosswalk.jsonl",
    "dependency-provider-summary.json",
    "dependency-provider-manifest.json",
)


class Failure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise Failure(message)


def load_json(path: Path) -> Any:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            fail(f"non-object JSONL row at {path.relative_to(ROOT)}:{line_number}")
        rows.append(value)
    return rows


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict[str, Any]:
    rules = load_json(HERE / "dependency-provider-rules.json")
    rows = load_jsonl(HERE / "dependency-provider-crosswalk.jsonl")
    summary = load_json(HERE / "dependency-provider-summary.json")
    manifest = load_json(HERE / "dependency-provider-manifest.json")

    if rules.get("completion_claim") is not False:
        fail("dependency provider rules claim completion")
    if len(rules.get("laws", [])) < 8 or any("!=" not in law for law in rules["laws"]):
        fail("dependency/provider non-collapse laws are incomplete")
    if summary["unclassified_provider_packages"]:
        fail(f"unclassified provider packages: {summary['unclassified_provider_packages']}")
    if summary["unique_declared_provider_package_count"] != len(rows):
        fail("provider row count drift")
    if summary["classified_provider_package_count"] != len(rows):
        fail("classified provider count drift")
    if summary["abstract_contract_binding_count"] != 0:
        fail("declared dependencies were promoted to abstract contracts")
    if summary["qualified_implementation_binding_count"] != 0:
        fail("declared dependencies were promoted to qualified implementations")
    if summary["semantic_authority_count"] != 0:
        fail("declared dependencies were promoted to semantic authority")

    packages: set[str] = set()
    for row in rows:
        package = row["provider_package"]
        if package in packages:
            fail(f"duplicate provider package row: {package}")
        packages.add(package)
        if package not in rules["providers"]:
            fail(f"provider row lacks rule: {package}")
        if not row["declared_groups"] or not row["declared_requirements"]:
            fail(f"provider row lacks declaration evidence: {package}")
        if row["abstract_contract_ref"] is not None:
            fail(f"provider dependency bound to abstract contract without adjudication: {package}")
        if row["implementation_qualification_ref"] is not None:
            fail(f"provider dependency bound to qualification without evidence: {package}")
        if row["semantic_authority"] or row["qualification_claim"] or row["completion_claim"]:
            fail(f"provider dependency promotes authority/qualification: {package}")
        if row["status"] != "DECLARED_PROVIDER_UNQUALIFIED_AGAINST_ABSTRACT_CONTRACT":
            fail(f"unsafe provider status: {package}")
        if len(row["replacement_seam"]) < 30:
            fail(f"provider replacement seam is too weak: {package}")

    expected_inputs = {
        "pyproject.toml": sha256_file(ROOT / "pyproject.toml"),
        "dependency-provider-rules.json": sha256_file(HERE / "dependency-provider-rules.json"),
    }
    if manifest["input_sha256"] != expected_inputs:
        fail("provider manifest input digests are stale")
    expected_generated = {
        "dependency-provider-crosswalk.jsonl": sha256_file(
            HERE / "dependency-provider-crosswalk.jsonl"
        ),
        "dependency-provider-summary.json": sha256_file(HERE / "dependency-provider-summary.json"),
    }
    if manifest["generated_sha256"] != expected_generated:
        fail("provider manifest generated digests are stale")
    if manifest["completion_claim"] is not False or summary["completion_claim"] is not False:
        fail("provider manifest or summary claims completion")
    return summary


def validate_determinism() -> None:
    before = {name: (HERE / name).read_bytes() for name in GENERATED}
    result = subprocess.run(
        [sys.executable, str(HERE / "build_dependency_provider_crosswalk.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"provider builder failed: {result.stdout}{result.stderr}")
    after = {name: (HERE / name).read_bytes() for name in GENERATED}
    changed = sorted(name for name in GENERATED if before[name] != after[name])
    if changed:
        fail(f"provider crosswalk was stale or nondeterministic: {changed}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--determinism", action="store_true")
    args = parser.parse_args()
    try:
        summary = validate()
        if args.determinism:
            validate_determinism()
            summary = validate()
    except (Failure, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL python_dependency_provider_fit: {exc}", file=sys.stderr)
        return 1
    print(
        "PASS python_dependency_provider_fit "
        + json.dumps(
            {
                "unique_declared_provider_package_count": summary[
                    "unique_declared_provider_package_count"
                ],
                "unclassified_provider_packages": summary[
                    "unclassified_provider_packages"
                ],
                "qualified_implementation_binding_count": summary[
                    "qualified_implementation_binding_count"
                ],
                "completion_claim": summary["completion_claim"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
