#!/usr/bin/env python3
"""Fail-closed validator for the Python implementation/product boundary."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - intentional fail-closed dependency gate
    raise SystemExit("FAIL python_product_fit: jsonschema is required") from exc

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC_ROOT = ROOT / "src" / "shannon_insight"
GENERATED = (
    "module-allocation.jsonl",
    "dependency-boundary-findings.jsonl",
    "implementation-crosswalk.jsonl",
    "summary.json",
    "manifest.json",
)


class ValidationFailure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationFailure(message)


def load_json(path: Path) -> Any:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL {path.relative_to(ROOT)}:{line_number}: {exc}")
        if not isinstance(value, dict):
            fail(f"JSONL row is not an object: {path.relative_to(ROOT)}:{line_number}")
        rows.append(value)
    return rows


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def horizontal_family_ids() -> set[str]:
    ids: set[str] = set()
    base = ROOT / "research" / "analytics_landscape" / "product_families"
    for path in sorted(base.glob("families_*.json")):
        payload = load_json(path)
        for family in payload.get("families", []):
            ids.add(family["id"])
    if not ids:
        fail("horizontal coverage-family corpus is missing")
    return ids


def validate_no_runtime_research_imports() -> None:
    violations: list[str] = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            fail(f"source parse failure {path.relative_to(ROOT)}: {exc}")
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            if any(name == "research" or name.startswith("research.") for name in names):
                violations.append(path.relative_to(ROOT).as_posix())
    if violations:
        fail(f"runtime imports research authority corpus: {sorted(set(violations))}")


def validate_generated() -> dict[str, Any]:
    boundary_schema = load_json(HERE / "application-boundary.schema.json")
    boundary = load_json(HERE / "application-boundary.json")
    module_schema = load_json(HERE / "module-allocation.schema.json")
    rules = load_json(HERE / "module-allocation-rules.json")
    language_role = load_json(HERE / "language-role-and-packaging.json")
    module_rows = load_jsonl(HERE / "module-allocation.jsonl")
    dependency_rows = load_jsonl(HERE / "dependency-boundary-findings.jsonl")
    crosswalk_rows = load_jsonl(HERE / "implementation-crosswalk.jsonl")
    summary = load_json(HERE / "summary.json")
    manifest = load_json(HERE / "manifest.json")

    jsonschema.Draft202012Validator.check_schema(boundary_schema)
    jsonschema.Draft202012Validator(boundary_schema).validate(boundary)
    jsonschema.Draft202012Validator.check_schema(module_schema)
    module_validator = jsonschema.Draft202012Validator(module_schema)
    for index, row in enumerate(module_rows):
        errors = sorted(module_validator.iter_errors(row), key=lambda error: list(error.path))
        if errors:
            fail(f"module allocation row {index} failed schema: {errors[0].message}")

    if boundary["completion_claim"] is not False:
        fail("application boundary must not claim completion")
    if language_role.get("completion_claim") is not False:
        fail("language-role decision must not claim completion")
    if language_role.get("decision") != "RETAIN_PYTHON_AS_APPLICATION_RESEARCH_HARNESS_AND_OPTIONAL_PROVIDER_LANGUAGE_NOT_UNIVERSAL_SEMANTIC_AUTHORITY":
        fail("Python language-role decision drift")
    if len(language_role.get("forbidden_collapses", [])) < 8:
        fail("Python language-role non-collapse laws are incomplete")
    if boundary["product_plane"] != "APPLICATION_DOMAIN_PRODUCT":
        fail("Python package must remain on the application-domain product plane")
    if boundary["authority"]["horizontal_semantic_authority"] is not False:
        fail("Python package cannot claim horizontal semantic authority")
    posture = boundary["qualification_posture"]
    forbidden_posture = (
        posture["qualified_contract_scope_count"],
        posture["portable_offer_count"],
        posture["executed_vertical_acceptance_count"],
        posture["build_ready"],
        posture["ratified"],
    )
    if forbidden_posture != (0, 0, 0, False, False):
        fail("Python boundary fabricates qualification, portability, acceptance or ratification")

    source_paths = sorted(
        path.relative_to(ROOT).as_posix()
        for path in SRC_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    )
    allocated_paths = [row["module_path"] for row in module_rows]
    if len(allocated_paths) != len(set(allocated_paths)):
        fail("duplicate Python module allocation")
    if allocated_paths != sorted(allocated_paths):
        fail("module allocation JSONL is not deterministically sorted")
    if set(allocated_paths) != set(source_paths):
        missing = sorted(set(source_paths) - set(allocated_paths))
        extra = sorted(set(allocated_paths) - set(source_paths))
        fail(f"module allocation is not total; missing={missing}, extra={extra}")
    if summary["unknown_top_level_owner_keys"]:
        fail(f"unknown top-level owners remain: {summary['unknown_top_level_owner_keys']}")
    if summary["source_parse_error_count"] or summary["test_parse_error_count"]:
        fail("source/test parse errors remain in generated summary")
    if summary["classified_python_file_count"] != len(module_rows):
        fail("classified Python file count drift")
    if summary["source_python_file_count"] != len(source_paths):
        fail("source Python file count drift")
    if summary["horizontal_semantic_authority_count"] != 0:
        fail("generated summary promotes horizontal semantic authority")
    if any(row["horizontal_semantic_authority"] for row in module_rows):
        fail("module row promotes horizontal semantic authority")
    if any(row["completion_claim"] for row in module_rows):
        fail("module row claims completion")

    layer_names = set(rules["layers"])
    if {row["ownership_layer"] for row in module_rows} - layer_names:
        fail("module row references unknown ownership layer")

    seen_edges: set[tuple[str, str]] = set()
    violation_count = 0
    for row in dependency_rows:
        edge = (row["source_owner_key"], row["target_owner_key"])
        if edge in seen_edges:
            fail(f"duplicate dependency edge: {edge}")
        seen_edges.add(edge)
        if row["semantic_authority"] or row["qualification_claim"] or row["completion_claim"]:
            fail(f"dependency row promotes authority or qualification: {edge}")
        if row["verdict"] == "OBSERVED_REFACTOR_REQUIRED":
            violation_count += 1
            if not row["debt_reason"]:
                fail(f"dependency violation lacks explicit debt reason: {edge}")
        elif row["verdict"] != "ALLOWED_BY_CURRENT_LAYER_POLICY":
            fail(f"unknown dependency verdict: {row['verdict']}")
    if violation_count != summary["dependency_boundary_violation_count"]:
        fail("dependency violation count drift")
    if len(dependency_rows) != summary["top_level_dependency_edge_count"]:
        fail("dependency edge count drift")

    family_ids = horizontal_family_ids()
    crosswalk_keys: set[str] = set()
    for row in crosswalk_rows:
        key = row["top_level_owner_key"]
        if key in crosswalk_keys:
            fail(f"duplicate implementation crosswalk: {key}")
        crosswalk_keys.add(key)
        if set(row["coverage_coordinate_refs"]) - family_ids:
            fail(f"crosswalk references unknown evidence coordinate: {key}")
        if row["canonical_product_ref"] is not None:
            fail(f"unqualified Python module bound to canonical product: {key}")
        if row["abstract_contract_scope_ref"] is not None:
            fail(f"unqualified Python module bound to abstract contract scope: {key}")
        if row["implementation_qualification_ref"] is not None:
            fail(f"unqualified Python module bound to qualification: {key}")
        if row["semantic_authority"] or row["qualification_claim"] or row["completion_claim"]:
            fail(f"crosswalk promotes authority or qualification: {key}")
        if row["crosswalk_status"] != "EVIDENCE_ONLY_NO_PRODUCT_OR_CONTRACT_PROMOTION":
            fail(f"crosswalk has unsafe status: {key}")
    observed_keys = {row["top_level_owner_key"] for row in module_rows}
    if crosswalk_keys != observed_keys:
        fail("implementation crosswalk is not total over observed top-level owners")

    expected_inputs = {
        "application-boundary.json": sha256_file(HERE / "application-boundary.json"),
        "application-boundary.schema.json": sha256_file(HERE / "application-boundary.schema.json"),
        "module-allocation-rules.json": sha256_file(HERE / "module-allocation-rules.json"),
        "language-role-and-packaging.json": sha256_file(HERE / "language-role-and-packaging.json"),
        "module-allocation.schema.json": sha256_file(HERE / "module-allocation.schema.json"),
    }
    if manifest["input_sha256"] != expected_inputs:
        fail("manifest input digests are stale")
    expected_generated = {
        name: sha256_file(HERE / name)
        for name in (
            "module-allocation.jsonl",
            "dependency-boundary-findings.jsonl",
            "implementation-crosswalk.jsonl",
            "summary.json",
        )
    }
    if manifest["generated_sha256"] != expected_generated:
        fail("manifest generated digests are stale")
    if manifest["completion_claim"] is not False or summary["completion_claim"] is not False:
        fail("manifest or summary claims completion")

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if 'name = "shannon-codebase-insight"' not in pyproject:
        fail("distribution identity drifted from the bounded application")
    if "Multi-level codebase structural analysis" not in pyproject:
        fail("package description no longer states its bounded codebase-analysis purpose")
    validate_no_runtime_research_imports()

    return summary


def validate_determinism() -> None:
    before = {name: (HERE / name).read_bytes() for name in GENERATED}
    result = subprocess.run(
        [sys.executable, str(HERE / "build_module_allocation.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"builder failed during determinism check: {result.stdout}{result.stderr}")
    after = {name: (HERE / name).read_bytes() for name in GENERATED}
    changed = sorted(name for name in GENERATED if before[name] != after[name])
    if changed:
        fail(f"generated corpus was stale or nondeterministic: {changed}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--determinism", action="store_true")
    args = parser.parse_args()
    try:
        summary = validate_generated()
        if args.determinism:
            validate_determinism()
            summary = validate_generated()
    except (ValidationFailure, jsonschema.ValidationError, json.JSONDecodeError) as exc:
        print(f"FAIL python_product_fit: {exc}", file=sys.stderr)
        return 1
    print(
        "PASS python_product_fit "
        + json.dumps(
            {
                "source_python_file_count": summary["source_python_file_count"],
                "observed_top_level_owner_count": summary[
                    "observed_top_level_owner_count"
                ],
                "dependency_boundary_violation_count": summary[
                    "dependency_boundary_violation_count"
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
