#!/usr/bin/env python3
"""Generate the Python implementation-to-product fit projection.

This builder scans the committed Python package. It refuses an unknown top-level module, records
all internal dependency edges, and turns every disallowed cross-layer import into explicit
refactoring debt. It never promotes a module to semantic authority or qualification.
"""
from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC_ROOT = ROOT / "src" / "shannon_insight"
TEST_ROOT = ROOT / "tests"

GENERATED = (
    "module-allocation.jsonl",
    "dependency-boundary-findings.jsonl",
    "implementation-crosswalk.jsonl",
    "summary.json",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def relative_module_name(path: Path) -> tuple[str, bool]:
    rel = path.relative_to(ROOT / "src").with_suffix("")
    parts = list(rel.parts)
    is_package = parts[-1] == "__init__"
    if is_package:
        parts.pop()
    return ".".join(parts), is_package


def top_level_key_for_path(path: Path) -> str:
    rel = path.relative_to(SRC_ROOT)
    if len(rel.parts) == 1:
        return rel.name
    return rel.parts[0]


def imported_name_from_from_node(
    node: ast.ImportFrom,
    current_module: str,
    current_is_package: bool,
) -> str | None:
    if node.level == 0:
        return node.module
    package_parts = current_module.split(".") if current_is_package else current_module.split(".")[:-1]
    ascend = node.level - 1
    if ascend > len(package_parts):
        return None
    base = package_parts[: len(package_parts) - ascend]
    if node.module:
        base.extend(node.module.split("."))
    return ".".join(base)


def target_top_level_key(imported_name: str | None, known_keys: set[str]) -> str | None:
    if not imported_name or imported_name == "shannon_insight":
        return "__init__.py" if imported_name == "shannon_insight" else None
    if not imported_name.startswith("shannon_insight."):
        return None
    component = imported_name.split(".", 2)[1]
    file_key = f"{component}.py"
    if file_key in known_keys:
        return file_key
    if component in known_keys:
        return component
    return None


def parse_imports(path: Path, known_keys: set[str]) -> tuple[set[str], list[str]]:
    current_module, current_is_package = relative_module_name(path)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as exc:
        return set(), [f"{type(exc).__name__}: {exc}"]

    targets: set[str] = set()
    for node in ast.walk(tree):
        names: list[str | None] = []
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.append(imported_name_from_from_node(node, current_module, current_is_package))
        for name in names:
            key = target_top_level_key(name, known_keys)
            if key:
                targets.add(key)
    return targets, []


def test_import_coverage(known_keys: set[str]) -> tuple[dict[str, set[str]], list[dict[str, str]]]:
    coverage: dict[str, set[str]] = defaultdict(set)
    parse_errors: list[dict[str, str]] = []
    if not TEST_ROOT.exists():
        return coverage, parse_errors
    for path in sorted(TEST_ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        if "fixtures" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            parse_errors.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
            continue
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    key = target_top_level_key(alias.name, known_keys)
                    if key:
                        imported.add(key)
            elif isinstance(node, ast.ImportFrom):
                key = target_top_level_key(node.module, known_keys)
                if key:
                    imported.add(key)
        for key in imported:
            coverage[key].add(rel)
    return coverage, parse_errors


def source_tree_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        rel = path.relative_to(ROOT).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def main() -> int:
    if not SRC_ROOT.exists():
        raise SystemExit(f"missing Python package root: {SRC_ROOT}")

    rules = load_json(HERE / "module-allocation-rules.json")
    boundary = load_json(HERE / "application-boundary.json")
    allocations: dict[str, dict[str, Any]] = rules["allocations"]
    known_keys = set(allocations)
    layers: dict[str, dict[str, list[str]]] = rules["layers"]

    source_paths = sorted(
        path for path in SRC_ROOT.rglob("*.py") if "__pycache__" not in path.parts
    )
    observed_keys = {top_level_key_for_path(path) for path in source_paths}
    unknown_keys = sorted(observed_keys - known_keys)
    test_coverage, test_parse_errors = test_import_coverage(known_keys)

    module_rows: list[dict[str, Any]] = []
    source_parse_errors: list[dict[str, str]] = []
    edge_files: dict[tuple[str, str], set[str]] = defaultdict(set)

    for path in source_paths:
        rel = path.relative_to(ROOT).as_posix()
        key = top_level_key_for_path(path)
        allocation = allocations.get(key)
        if allocation is None:
            continue
        targets, errors = parse_imports(path, known_keys)
        for error in errors:
            source_parse_errors.append({"path": rel, "error": error})
        for target in targets:
            if target != key:
                edge_files[(key, target)].add(rel)
        module_rows.append(
            {
                "record_kind": "python_module_allocation",
                "module_path": rel,
                "top_level_owner_key": key,
                "ownership_layer": allocation["ownership_layer"],
                "application_id": boundary["application_id"],
                "allocation_basis": allocation["allocation_basis"],
                "local_application_semantic_owner": allocation[
                    "local_application_semantic_owner"
                ],
                "horizontal_semantic_authority": False,
                "implementation_posture": allocation["implementation_posture"],
                "coverage_coordinate_refs": sorted(allocation["coverage_coordinate_refs"]),
                "direct_test_file_count": len(test_coverage.get(key, set())),
                "source_sha256": sha256_file(path),
                "completion_claim": False,
            }
        )

    dependency_rows: list[dict[str, Any]] = []
    violation_count = 0
    for (source_key, target_key), files in sorted(edge_files.items()):
        source_layer = allocations[source_key]["ownership_layer"]
        target_layer = allocations[target_key]["ownership_layer"]
        permitted = target_layer in set(layers[source_layer]["may_import"])
        if not permitted:
            violation_count += 1
        dependency_rows.append(
            {
                "record_kind": "python_top_level_dependency_boundary",
                "source_owner_key": source_key,
                "source_layer": source_layer,
                "target_owner_key": target_key,
                "target_layer": target_layer,
                "observed_source_file_count": len(files),
                "observed_source_files": sorted(files),
                "verdict": "ALLOWED_BY_CURRENT_LAYER_POLICY"
                if permitted
                else "OBSERVED_REFACTOR_REQUIRED",
                "debt_reason": None
                if permitted
                else "The source ownership layer imports a layer outside its declared dependency allowance; retain as explicit architectural debt until the implementation is refactored or the boundary is re-adjudicated.",
                "semantic_authority": False,
                "qualification_claim": False,
                "completion_claim": False,
            }
        )

    crosswalk_rows = []
    for key in sorted(observed_keys & known_keys):
        allocation = allocations[key]
        crosswalk_rows.append(
            {
                "record_kind": "python_implementation_research_crosswalk",
                "top_level_owner_key": key,
                "application_id": boundary["application_id"],
                "product_plane": boundary["product_plane"],
                "ownership_layer": allocation["ownership_layer"],
                "coverage_coordinate_refs": sorted(allocation["coverage_coordinate_refs"]),
                "crosswalk_status": "EVIDENCE_ONLY_NO_PRODUCT_OR_CONTRACT_PROMOTION",
                "canonical_product_ref": None,
                "abstract_contract_scope_ref": None,
                "implementation_qualification_ref": None,
                "semantic_authority": False,
                "qualification_claim": False,
                "completion_claim": False,
            }
        )

    module_rows.sort(key=lambda row: row["module_path"])
    write_jsonl(HERE / "module-allocation.jsonl", module_rows)
    write_jsonl(HERE / "dependency-boundary-findings.jsonl", dependency_rows)
    write_jsonl(HERE / "implementation-crosswalk.jsonl", crosswalk_rows)

    layer_counts = Counter(row["ownership_layer"] for row in module_rows)
    posture_counts = Counter(row["implementation_posture"] for row in module_rows)
    directly_tested = sum(row["direct_test_file_count"] > 0 for row in module_rows)
    summary = {
        "report_id": "python_implementation_product_fit",
        "as_of": boundary["as_of"],
        "application_id": boundary["application_id"],
        "distribution_name": boundary["distribution_name"],
        "disposition": boundary["disposition"],
        "product_plane": boundary["product_plane"],
        "source_python_file_count": len(source_paths),
        "classified_python_file_count": len(module_rows),
        "observed_top_level_owner_count": len(observed_keys),
        "classified_top_level_owner_count": len(observed_keys & known_keys),
        "unknown_top_level_owner_keys": unknown_keys,
        "unused_compatibility_rule_keys": sorted(known_keys - observed_keys),
        "source_parse_error_count": len(source_parse_errors),
        "source_parse_errors": source_parse_errors,
        "test_parse_error_count": len(test_parse_errors),
        "test_parse_errors": test_parse_errors,
        "directly_tested_python_file_count": directly_tested,
        "ownership_layer_file_counts": dict(sorted(layer_counts.items())),
        "implementation_posture_file_counts": dict(sorted(posture_counts.items())),
        "top_level_dependency_edge_count": len(dependency_rows),
        "dependency_boundary_violation_count": violation_count,
        "coverage_coordinate_reference_count": len(
            {
                ref
                for row in crosswalk_rows
                for ref in row["coverage_coordinate_refs"]
            }
        ),
        "canonical_product_binding_count": 0,
        "abstract_contract_binding_count": 0,
        "qualified_implementation_binding_count": 0,
        "horizontal_semantic_authority_count": 0,
        "build_ready": False,
        "ratified": False,
        "status": "APPLICATION_BOUNDARY_CLASSIFIED_DEPENDENCY_DEBT_EXPLICIT_UNQUALIFIED",
        "completion_claim": False,
    }
    write_json(HERE / "summary.json", summary)

    generated_hashes = {name: sha256_file(HERE / name) for name in GENERATED}
    manifest = {
        "manifest_id": "python_implementation_product_fit",
        "schema_version": "1.0.0",
        "as_of": boundary["as_of"],
        "application_id": boundary["application_id"],
        "source_tree_sha256": source_tree_digest(source_paths),
        "input_sha256": {
            "application-boundary.json": sha256_file(HERE / "application-boundary.json"),
            "application-boundary.schema.json": sha256_file(
                HERE / "application-boundary.schema.json"
            ),
            "module-allocation-rules.json": sha256_file(HERE / "module-allocation-rules.json"),
            "module-allocation.schema.json": sha256_file(
                HERE / "module-allocation.schema.json"
            ),
        },
        "generated_sha256": generated_hashes,
        "completion_claim": False,
    }
    write_json(HERE / "manifest.json", manifest)

    print(json.dumps(summary, sort_keys=True))
    if unknown_keys or source_parse_errors or test_parse_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
