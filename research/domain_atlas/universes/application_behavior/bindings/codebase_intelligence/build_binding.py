#!/usr/bin/env python3
"""Build the deterministic code-intelligence application binding."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from source_model import AS_OF, COMPONENT_ROLE, EVIDENCE, LIBRARIES, PRODUCT, ROLE_DEFINITIONS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
OUTPUTS = (
    "product-binding.json",
    "component-bindings.jsonl",
    "library-bindings.jsonl",
    "research-python-roles.jsonl",
    "evidence.jsonl",
    "summary.json",
    "manifest.json",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def canonical_jsonl(rows: list[dict[str, Any]], key: str) -> str:
    return "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in sorted(rows, key=lambda item: item[key]))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def classify_research_python(path: Path) -> tuple[str, str]:
    relative = path.relative_to(ROOT).as_posix()
    name = path.name
    parts = set(path.parts)
    if "executions" in parts or name in {"run_execution.py", "validate_execution.py", "provider_adapter.py", "execute.py"}:
        return "qualification_execution_harness", "Exact execution/provider path rule"
    if name == "source_model.py":
        return "research_authoring_model", "Exact source_model.py rule"
    if name.startswith(("validate_", "verify_")) or name in {"validate.py", "validator.py", "verifier.py"}:
        return "research_validator", "Exact validator filename rule"
    if name.startswith(("build_", "generate_", "materialize_", "compile_", "derive_", "project_")):
        return "research_corpus_builder", "Exact deterministic builder filename rule"
    if any(token in name for token in ("migrate", "migration", "rebase", "reconcile", "repair", "backfill")):
        return "research_migration_or_reconciliation", "Explicit migration/reconciliation filename rule"
    if name.startswith("test_") or "tests" in parts:
        return "research_conformance_test", "Research test path rule"
    if name in {"__init__.py", "conftest.py"}:
        return "research_package_support", "Python package support rule"
    return "research_analysis_or_support", f"No stronger execution, builder, validator, migration or test rule matched {relative}"


def build() -> dict[str, str]:
    src_root = ROOT / "src" / "shannon_insight"
    actual_components = sorted(path.name for path in src_root.iterdir() if path.name != "__pycache__")
    configured_components = sorted(COMPONENT_ROLE)
    unknown = sorted(set(actual_components) - set(configured_components))
    stale = sorted(set(configured_components) - set(actual_components))
    if unknown or stale:
        raise SystemExit(f"component classification drift: unknown={unknown}, stale={stale}")

    component_rows: list[dict[str, Any]] = []
    for name in actual_components:
        role = COMPONENT_ROLE[name]
        definition = ROLE_DEFINITIONS[role]
        component_rows.append(
            {
                "component_id": f"component.code_intelligence.{name.replace('.', '_')}",
                "path": f"src/shannon_insight/{name}",
                "role": role,
                "ownership_kind": definition["ownership_kind"],
                "semantic_owner": PRODUCT["product_id"] if definition["ownership_kind"] in {"product_library", "application_experience"} else "imported_or_implementation_scope",
                "imports": definition["imports"],
                "cannot_own": definition["cannot_own"],
                "implementation_language": "python",
                "status": "implementation_present_unqualified",
                "qualification_claim": False,
                "completion_claim": False,
            }
        )

    library_rows: list[dict[str, Any]] = []
    for library in LIBRARIES:
        row = dict(library)
        row.update(
            {
                "edition": 1,
                "semantic_owner": PRODUCT["product_id"],
                "implementation_language": "python",
                "compatibility_rule": "A compatible replacement preserves declared types, operations, decisions, invariants, refusals and export behavior for the exact edition.",
                "evolution_rule": "Breaking semantic or artifact-identity change requires a new edition plus migration/refusal rules.",
                "resource_failure_rule": "Finite inputs, time, memory and cancellation must be declared by the execution occurrence; exhaustion is a typed refusal.",
                "qualification_status": "specified_binding_implementation_unqualified",
                "completion_claim": False,
            }
        )
        library_rows.append(row)

    research_rows: list[dict[str, Any]] = []
    for path in sorted((ROOT / "research").rglob("*.py")):
        role, basis = classify_research_python(path)
        relative = path.relative_to(ROOT).as_posix()
        research_rows.append(
            {
                "python_file_id": "research_python." + relative.replace("/", ".").replace("_", "-").removesuffix(".py"),
                "path": relative,
                "role": role,
                "classification_basis": basis,
                "authority": "research_workbench_only",
                "production_runtime": False,
                "semantic_authority": False,
                "provider_qualification": False,
                "build_ready_claim": False,
                "completion_claim": False,
            }
        )

    summary = {
        "report_id": "code_intelligence_python_product_boundary",
        "as_of": AS_OF,
        "product_id": PRODUCT["product_id"],
        "product_kind": PRODUCT["product_kind"],
        "top_level_component_count": len(component_rows),
        "classified_top_level_component_count": len(component_rows),
        "unclassified_top_level_component_count": 0,
        "library_binding_count": len(library_rows),
        "research_python_file_count": len(research_rows),
        "research_python_role_counts": {role: sum(row["role"] == role for row in research_rows) for role in sorted({row["role"] for row in research_rows})},
        "python_semantic_authority_count": 0,
        "qualified_implementation_count": 0,
        "build_ready_product_count": 0,
        "ratified_product_count": 0,
        "status": "APPLICATION_PRODUCT_BOUNDARY_EXPLICIT_IMPLEMENTATION_AND_RESEARCH_ROLES_UNQUALIFIED",
        "completion_claim": False,
    }

    rendered = {
        "product-binding.json": canonical_json(PRODUCT),
        "component-bindings.jsonl": canonical_jsonl(component_rows, "component_id"),
        "library-bindings.jsonl": canonical_jsonl(library_rows, "library_id"),
        "research-python-roles.jsonl": canonical_jsonl(research_rows, "path"),
        "evidence.jsonl": canonical_jsonl(EVIDENCE, "evidence_id"),
        "summary.json": canonical_json(summary),
    }
    manifest = {
        "manifest_id": "code_intelligence_python_product_boundary_v1",
        "as_of": AS_OF,
        "edition": 1,
        "parent_authority": PRODUCT["parent_semantic_authority"],
        "inputs": {
            "source_model.py": sha256_file(HERE / "source_model.py"),
            "parent_manifest.json": sha256_file(ROOT / PRODUCT["parent_semantic_authority"] / "manifest.json"),
            "pyproject.toml": sha256_file(ROOT / "pyproject.toml"),
        },
        "files": {name: {"sha256": sha256_bytes(content.encode("utf-8")), "records": content.count("\n") if name.endswith(".jsonl") else 1} for name, content in sorted(rendered.items())},
        "qualification": PRODUCT["qualification"],
        "completion_claim": False,
    }
    rendered["manifest.json"] = canonical_json(manifest)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = build()
    mismatches: list[str] = []
    for name in OUTPUTS:
        expected = rendered[name]
        path = HERE / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                mismatches.append(name)
        else:
            path.write_text(expected, encoding="utf-8")
    if mismatches:
        raise SystemExit("generated binding is stale or absent: " + ", ".join(mismatches))
    print(rendered["summary.json"].strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
