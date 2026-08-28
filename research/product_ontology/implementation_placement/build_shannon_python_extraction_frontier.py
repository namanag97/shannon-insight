#!/usr/bin/env python3
"""Build exact-source extraction candidates from the Python application.

This projection does not decide that a module is a reusable universal library.
It identifies candidate implementation scopes and keeps exact abstract-contract,
semantic-authority, purity and qualification gates open.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PLACEMENT_BUILDER = HERE / "build_shannon_python_placement.py"

ELIGIBLE_ROLES = {
    "analytical_method_kernel_candidate": "EXACT_SCOPE_METHOD_KERNEL_CANDIDATE",
    "domain_semantic_library_candidate": "APPLICATION_DOMAIN_SEMANTIC_LIBRARY_CANDIDATE",
    "domain_relation_construction": "APPLICATION_DOMAIN_RELATION_LIBRARY_CANDIDATE",
    "domain_observation_and_identity": "APPLICATION_DOMAIN_OBSERVATION_LIBRARY_CANDIDATE",
}

EFFECTFUL_IMPORT_ROOTS = {
    "asyncio",
    "concurrent",
    "contextlib",
    "diskcache",
    "duckdb",
    "http",
    "multiprocessing",
    "os",
    "pathlib",
    "requests",
    "shutil",
    "signal",
    "socket",
    "sqlite3",
    "subprocess",
    "tempfile",
    "threading",
    "time",
    "urllib",
    "watchfiles",
}

EFFECTFUL_CALL_SUFFIXES = {
    "open",
    "read_bytes",
    "read_text",
    "write_bytes",
    "write_text",
    "mkdir",
    "unlink",
    "rename",
    "replace",
    "run",
    "Popen",
    "connect",
    "execute",
    "executemany",
    "commit",
    "rollback",
    "sleep",
}

REQUIRED_GATES = [
    "exact sovereign semantic owner",
    "editioned abstract contract identity",
    "constructor, observer, operation, decision, invariant and refusal closure",
    "declared dependency and effect boundary",
    "reproducible source, artifact, dependency, toolchain and configuration identity",
    "deterministic, property, metamorphic, adversarial and exact-scope execution",
    "independent appraisal",
    "second independently controlled implementation for portability claims",
    "differential, export/import, migration, rollback and exit evidence where applicable",
    "executed unrelated-vertical acceptance for any promoted horizontal contract",
]


def import_placement_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "shannon_python_placement_builder", PLACEMENT_BUILDER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Python placement builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def inspect_source(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return {
            "parse_status": "SYNTAX_REFUSED",
            "parse_refusal": str(exc),
            "public_symbols": [],
            "internal_import_roots": [],
            "external_import_roots": [],
            "effect_signals": ["syntax_refusal"],
        }

    public_symbols: list[dict[str, Any]] = []
    import_roots: set[str] = set()
    effect_signals: set[str] = set()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                public_symbols.append(
                    {
                        "name": node.name,
                        "kind": (
                            "class"
                            if isinstance(node, ast.ClassDef)
                            else "async_function"
                            if isinstance(node, ast.AsyncFunctionDef)
                            else "function"
                        ),
                        "line": node.lineno,
                    }
                )
        elif isinstance(node, ast.Import):
            import_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_roots.add(node.module.split(".", 1)[0])

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = dotted_name(node.func)
            if name and name.rsplit(".", 1)[-1] in EFFECTFUL_CALL_SUFFIXES:
                effect_signals.add(f"call:{name}")

    for root in import_roots & EFFECTFUL_IMPORT_ROOTS:
        effect_signals.add(f"import:{root}")

    return {
        "parse_status": "PARSED",
        "parse_refusal": None,
        "public_symbols": sorted(
            public_symbols, key=lambda item: (item["line"], item["kind"], item["name"])
        ),
        "internal_import_roots": sorted(import_roots & {"shannon_insight"}),
        "external_import_roots": sorted(import_roots - {"shannon_insight"}),
        "effect_signals": sorted(effect_signals),
    }


def scope_digest(source_files: list[dict[str, Any]]) -> str:
    material = "\n".join(
        f"{row['path']}\0{row['sha256']}" for row in sorted(source_files, key=lambda r: r["path"])
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(material).hexdigest()}"


def main() -> int:
    placement_builder = import_placement_builder()
    placement_rows = placement_builder.discover_modules()
    candidates: list[dict[str, Any]] = []

    for module in placement_rows:
        role = module["implementation_role"]
        disposition = ELIGIBLE_ROLES.get(role)
        if disposition is None:
            continue
        inspected_files: list[dict[str, Any]] = []
        all_effects: set[str] = set()
        all_external_imports: set[str] = set()
        all_internal_imports: set[str] = set()
        public_api_count = 0
        parse_refusals: list[dict[str, str]] = []
        for source in module["source_files"]:
            inspection = inspect_source(ROOT / source["path"])
            public_api_count += len(inspection["public_symbols"])
            all_effects.update(inspection["effect_signals"])
            all_external_imports.update(inspection["external_import_roots"])
            all_internal_imports.update(inspection["internal_import_roots"])
            if inspection["parse_status"] != "PARSED":
                parse_refusals.append(
                    {
                        "path": source["path"],
                        "refusal": inspection["parse_refusal"] or "unknown syntax refusal",
                    }
                )
            inspected_files.append({**source, **inspection})

        purity_posture = (
            "EFFECTFUL_OR_PURITY_UNPROVEN"
            if all_effects or parse_refusals
            else "PURE_CANDIDATE_UNPROVEN"
        )
        api_posture = (
            "PUBLIC_API_OBSERVED_CONTRACT_UNBOUND"
            if public_api_count
            else "NO_PUBLIC_API_OBSERVED_EXTRACTION_REVIEW_REQUIRED"
        )
        candidates.append(
            {
                "candidate_id": f"python_extraction.{module['module']}",
                "record_kind": "python_library_extraction_candidate",
                "implementation_id": "implementation.shannon_python.codebase_insight",
                "application_product_id": placement_builder.APPLICATION_PRODUCT_ID,
                "module": module["module"],
                "implementation_role": role,
                "candidate_disposition": disposition,
                "horizontal_coverage_coordinates": module[
                    "horizontal_coverage_coordinates"
                ],
                "semantic_scope_statement": module["rationale"],
                "source_scope_digest": scope_digest(module["source_files"]),
                "source_files": inspected_files,
                "public_api_symbol_count": public_api_count,
                "api_posture": api_posture,
                "internal_import_roots": sorted(all_internal_imports),
                "external_import_roots": sorted(all_external_imports),
                "static_effect_signals": sorted(all_effects),
                "purity_posture": purity_posture,
                "parse_refusals": parse_refusals,
                "exact_abstract_contract_id": None,
                "semantic_owner_id": None,
                "contract_binding_status": "UNBOUND_EXACT_CONTRACT_REQUIRED",
                "library_extraction_allowed": False,
                "implementation_qualified": False,
                "portable_offer": False,
                "product_promotion": False,
                "required_gates": REQUIRED_GATES,
                "refusal_laws": [
                    "Refuse extraction when exact public behavior, effects, dependencies, invariants or refusals remain implicit.",
                    "Refuse horizontal promotion when behavior is specific to source code, Git, repositories or developer workflows.",
                    "Refuse pure-library classification when static effect signals exist or purity has not been proved.",
                    "Refuse qualification when evidence is same-campaign, digest-unbound, stale or outside the declared source scope.",
                ],
                "completion_claim": False,
            }
        )

    candidates.sort(key=lambda row: row["candidate_id"])
    output = HERE / "shannon-python-extraction-candidates.jsonl"
    output.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in candidates),
        encoding="utf-8",
    )
    role_counts = Counter(row["implementation_role"] for row in candidates)
    purity_counts = Counter(row["purity_posture"] for row in candidates)
    summary = {
        "report_id": "shannon_python_extraction_frontier",
        "implementation_id": "implementation.shannon_python.codebase_insight",
        "candidate_count": len(candidates),
        "candidate_role_counts": dict(sorted(role_counts.items())),
        "purity_posture_counts": dict(sorted(purity_counts.items())),
        "candidates_with_bound_exact_contract": sum(
            row["exact_abstract_contract_id"] is not None for row in candidates
        ),
        "candidates_allowed_for_extraction": sum(
            row["library_extraction_allowed"] for row in candidates
        ),
        "qualified_candidate_count": sum(
            row["implementation_qualified"] for row in candidates
        ),
        "portable_offer_count": sum(row["portable_offer"] for row in candidates),
        "status": "EXACT_SOURCE_SCOPES_IDENTIFIED_CONTRACT_AND_QUALIFICATION_GATES_OPEN",
        "completion_claim": False,
    }
    (HERE / "shannon-python-extraction-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
