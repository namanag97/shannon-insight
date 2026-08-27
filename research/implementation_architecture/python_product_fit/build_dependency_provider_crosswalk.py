#!/usr/bin/env python3
"""Classify declared Python dependencies as provider implementations, never contracts."""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PYPROJECT = ROOT / "pyproject.toml"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_package_name(requirement: str) -> str:
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
    if not match:
        raise ValueError(f"cannot parse dependency requirement: {requirement!r}")
    return match.group(1).lower().replace("_", "-").replace(".", "-")


def parse_dependency_groups(text: str) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    section = ""
    active_group: str | None = None
    in_array = False

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1]
            active_group = None
            in_array = False
            continue

        if section == "project" and stripped.startswith("dependencies") and "[" in stripped:
            active_group = "runtime"
            in_array = True
            continue

        if section == "project.optional-dependencies" and not in_array:
            match = re.match(r"([A-Za-z0-9_.-]+)\s*=\s*\[", stripped)
            if match:
                active_group = match.group(1)
                in_array = True
                continue

        if not in_array or active_group is None:
            continue
        if stripped.startswith("]"):
            active_group = None
            in_array = False
            continue
        match = re.match(r'"([^"]+)"', stripped)
        if match:
            groups[active_group].append(match.group(1))

    if not groups.get("runtime"):
        raise ValueError("project runtime dependencies were not parsed")
    return dict(groups)


def main() -> int:
    rules = load_json(HERE / "dependency-provider-rules.json")
    providers = rules["providers"]
    groups = parse_dependency_groups(PYPROJECT.read_text(encoding="utf-8"))

    by_package: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: {"groups": [], "requirements": []}
    )
    for group, requirements in sorted(groups.items()):
        for requirement in requirements:
            package = normalize_package_name(requirement)
            by_package[package]["groups"].append(group)
            by_package[package]["requirements"].append(requirement)

    unknown = sorted(set(by_package) - set(providers))
    rows = []
    for package in sorted(by_package):
        rule = providers.get(package)
        if rule is None:
            continue
        rows.append(
            {
                "record_kind": "python_dependency_provider_crosswalk",
                "provider_package": package,
                "declared_groups": sorted(set(by_package[package]["groups"])),
                "declared_requirements": sorted(set(by_package[package]["requirements"])),
                "provider_role": rule["provider_role"],
                "effect_boundary": rule["effect_boundary"],
                "replacement_seam": rule["replacement_seam"],
                "abstract_contract_ref": None,
                "implementation_qualification_ref": None,
                "semantic_authority": False,
                "qualification_claim": False,
                "status": "DECLARED_PROVIDER_UNQUALIFIED_AGAINST_ABSTRACT_CONTRACT",
                "completion_claim": False,
            }
        )

    output = HERE / "dependency-provider-crosswalk.jsonl"
    output.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    runtime_packages = {
        package
        for package, values in by_package.items()
        if "runtime" in values["groups"]
    }
    optional_packages = set(by_package) - runtime_packages
    summary = {
        "report_id": "python_dependency_provider_crosswalk",
        "as_of": rules["as_of"],
        "declared_dependency_group_count": len(groups),
        "declared_dependency_occurrence_count": sum(len(v) for v in groups.values()),
        "unique_declared_provider_package_count": len(by_package),
        "classified_provider_package_count": len(rows),
        "runtime_provider_package_count": len(runtime_packages),
        "optional_or_engineering_provider_package_count": len(optional_packages),
        "unclassified_provider_packages": unknown,
        "abstract_contract_binding_count": 0,
        "qualified_implementation_binding_count": 0,
        "semantic_authority_count": 0,
        "status": "DECLARED_PROVIDER_DEPENDENCIES_CLASSIFIED_UNQUALIFIED",
        "completion_claim": False,
    }
    summary_path = HERE / "dependency-provider-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest = {
        "manifest_id": "python_dependency_provider_crosswalk",
        "schema_version": "1.0.0",
        "as_of": rules["as_of"],
        "input_sha256": {
            "pyproject.toml": sha256_file(PYPROJECT),
            "dependency-provider-rules.json": sha256_file(HERE / "dependency-provider-rules.json"),
        },
        "generated_sha256": {
            "dependency-provider-crosswalk.jsonl": sha256_file(output),
            "dependency-provider-summary.json": sha256_file(summary_path),
        },
        "completion_claim": False,
    }
    (HERE / "dependency-provider-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, sort_keys=True))
    return 1 if unknown else 0


if __name__ == "__main__":
    raise SystemExit(main())
