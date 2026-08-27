#!/usr/bin/env python3
"""Build an exact internal-import and extraction-blocker audit for the Python package."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SRC = ROOT / "src" / "shannon_insight"
PLACEMENT_BUILDER = HERE / "build_shannon_python_placement.py"
OUTPUT = HERE / "shannon-python-dependency-audit.json"
EDGES = HERE / "shannon-python-dependency-edges.jsonl"

CANDIDATE_ROLES = {
    "analytical_method_kernel_candidate",
    "domain_semantic_library_candidate",
    "domain_relation_construction",
    "domain_observation_and_identity",
}


def import_placement_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "shannon_python_placement_builder_dependency", PLACEMENT_BUILDER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import placement builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_module(path: Path) -> str:
    relative = path.relative_to(SRC)
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    suffix = ".".join(parts)
    return "shannon_insight" + (f".{suffix}" if suffix else "")


def resolve_from_import(current_module: str, node: ast.ImportFrom) -> str | None:
    module = node.module or ""
    if node.level == 0:
        return module or None
    package = current_module.rsplit(".", 1)[0] if "." in current_module else current_module
    relative = "." * node.level + module
    try:
        return importlib.util.resolve_name(relative, package)
    except (ImportError, ValueError):
        return None


def top_level_internal(module_name: str | None) -> str | None:
    if not module_name or not module_name.startswith("shannon_insight"):
        return None
    parts = module_name.split(".")
    return parts[1] if len(parts) > 1 else "__package_root__"


def classify_edge(source_role: str, target_role: str) -> str:
    if source_role not in CANDIDATE_ROLES:
        return "APPLICATION_LOCAL_EDGE"
    if target_role in CANDIDATE_ROLES:
        return "CANDIDATE_DEPENDENCY_REQUIRES_EXACT_CONTRACT"
    if target_role == "experience_delivery":
        return "PRESENTATION_DEPENDENCY_BLOCKS_EXTRACTION"
    if target_role in {
        "application_infrastructure",
        "application_runtime_support",
        "application_orchestration",
    }:
        return "EFFECTFUL_APPLICATION_DEPENDENCY_REQUIRES_PORT"
    if target_role in {
        "application_measurement_and_scoring",
        "application_diagnostic_analysis",
        "application_finding_lifecycle",
        "application_decision_support",
        "application_evidence_eventing",
        "application_acquisition",
    }:
        return "APPLICATION_SEMANTIC_DEPENDENCY_REQUIRES_REHOME_OR_REFUSAL"
    return "SHARED_SUPPORT_DEPENDENCY_REQUIRES_ADJUDICATION"


def strongly_connected_components(nodes: set[str], edges: set[tuple[str, str]]) -> list[list[str]]:
    graph: dict[str, list[str]] = {node: [] for node in nodes}
    for source, target in edges:
        graph.setdefault(source, []).append(target)
        graph.setdefault(target, [])
    for values in graph.values():
        values.sort()

    index = 0
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in graph[node]:
            if target not in indices:
                visit(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])
        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                item = stack.pop()
                on_stack.remove(item)
                component.append(item)
                if item == node:
                    break
            components.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return sorted(components, key=lambda component: (len(component), component))


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def main() -> int:
    placement_builder = import_placement_builder()
    placement_rows = placement_builder.discover_modules()
    roles = {row["module"]: row["implementation_role"] for row in placement_rows}
    known_modules = set(roles)
    observed: dict[tuple[str, str], dict[str, Any]] = {}
    unresolved_relative_imports: list[dict[str, Any]] = []

    for path in sorted(SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        current = source_module(path)
        source_top = top_level_internal(current)
        if source_top == "__package_root__":
            continue
        try:
            tree = ast.parse(
                path.read_text(encoding="utf-8", errors="replace"), filename=str(path)
            )
        except SyntaxError as exc:
            unresolved_relative_imports.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "line": exc.lineno,
                    "reason": "SOURCE_SYNTAX_REFUSED",
                    "detail": str(exc),
                }
            )
            continue
        for node in ast.walk(tree):
            targets: list[str] = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                resolved = resolve_from_import(current, node)
                if resolved is None and node.level:
                    unresolved_relative_imports.append(
                        {
                            "path": str(path.relative_to(ROOT)),
                            "line": node.lineno,
                            "reason": "RELATIVE_IMPORT_UNRESOLVED",
                            "detail": ast.get_source_segment(
                                path.read_text(encoding="utf-8", errors="replace"), node
                            ),
                        }
                    )
                    continue
                if resolved:
                    targets = [resolved]
            for target_name in targets:
                target_top = top_level_internal(target_name)
                if (
                    target_top is None
                    or target_top == "__package_root__"
                    or target_top == source_top
                ):
                    continue
                if target_top not in known_modules:
                    unresolved_relative_imports.append(
                        {
                            "path": str(path.relative_to(ROOT)),
                            "line": getattr(node, "lineno", None),
                            "reason": "INTERNAL_TARGET_TOP_LEVEL_UNKNOWN",
                            "detail": target_name,
                        }
                    )
                    continue
                key = (source_top, target_top)
                edge = observed.setdefault(
                    key,
                    {
                        "edge_id": f"python_dependency.{source_top}.{target_top}",
                        "record_kind": "python_internal_dependency_edge",
                        "source_module": source_top,
                        "target_module": target_top,
                        "source_role": roles[source_top],
                        "target_role": roles[target_top],
                        "classification": classify_edge(
                            roles[source_top], roles[target_top]
                        ),
                        "observations": [],
                        "semantic_authority": False,
                        "qualification_claim": False,
                        "completion_claim": False,
                    },
                )
                observation = {
                    "path": str(path.relative_to(ROOT)),
                    "line": getattr(node, "lineno", None),
                    "imported_module": target_name,
                }
                if observation not in edge["observations"]:
                    edge["observations"].append(observation)

    edge_rows = sorted(observed.values(), key=lambda row: row["edge_id"])
    for row in edge_rows:
        row["observations"].sort(
            key=lambda item: (item["path"], item.get("line") or -1, item["imported_module"])
        )
        row["edge_digest"] = canonical_digest(
            {
                "source_module": row["source_module"],
                "target_module": row["target_module"],
                "observations": row["observations"],
            }
        )
    EDGES.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in edge_rows),
        encoding="utf-8",
    )

    edge_pairs = {(row["source_module"], row["target_module"]) for row in edge_rows}
    components = strongly_connected_components(known_modules, edge_pairs)
    nontrivial = [component for component in components if len(component) > 1]
    candidate_blockers = [
        row for row in edge_rows if row["classification"] != "APPLICATION_LOCAL_EDGE"
    ]
    classification_counts = Counter(row["classification"] for row in edge_rows)
    audit = {
        "report_id": "shannon_python_dependency_and_extraction_audit",
        "implementation_id": "implementation.shannon_python.codebase_insight",
        "module_count": len(known_modules),
        "internal_dependency_edge_count": len(edge_rows),
        "classification_counts": dict(sorted(classification_counts.items())),
        "extraction_blocking_or_contract_edge_count": len(candidate_blockers),
        "strongly_connected_component_count": len(components),
        "nontrivial_scc_count": len(nontrivial),
        "nontrivial_sccs": [
            {
                "scc_id": f"python_scc.{index:03d}",
                "modules": component,
                "roles": sorted({roles[module] for module in component}),
                "contains_extraction_candidate": any(
                    roles[module] in CANDIDATE_ROLES for module in component
                ),
                "contains_non_candidate": any(
                    roles[module] not in CANDIDATE_ROLES for module in component
                ),
                "disposition": "REQUIRES_SEAM_ADJUDICATION_BEFORE_EXTRACTION",
            }
            for index, component in enumerate(nontrivial, 1)
        ],
        "unresolved_import_observations": sorted(
            unresolved_relative_imports,
            key=lambda row: (row["path"], row.get("line") or -1, row["reason"]),
        ),
        "extraction_laws": [
            "An observed import edge is evidence of implementation dependency, not semantic ownership.",
            "A candidate-to-candidate edge requires an exact abstract dependency contract before extraction.",
            "A candidate dependency on application, infrastructure or presentation code blocks pure-library promotion until ported, inverted, rehomed or explicitly refused.",
            "A strongly connected component spanning candidate and non-candidate roles cannot be marketed as an independently reusable library.",
            "Removing an import is insufficient when hidden data, configuration, runtime or semantic coupling remains.",
        ],
        "status": "OBSERVED_DEPENDENCY_TOPOLOGY_EXTRACTION_SEAMS_UNADJUDICATED",
        "semantic_ratified": False,
        "implementation_qualified": False,
        "completion_claim": False,
    }
    audit["audit_digest"] = canonical_digest(audit)
    OUTPUT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "report_id": audit["report_id"],
                "module_count": audit["module_count"],
                "edge_count": audit["internal_dependency_edge_count"],
                "extraction_blocking_or_contract_edge_count": audit[
                    "extraction_blocking_or_contract_edge_count"
                ],
                "nontrivial_scc_count": audit["nontrivial_scc_count"],
                "unresolved_import_observation_count": len(
                    audit["unresolved_import_observations"]
                ),
                "audit_digest": audit["audit_digest"],
                "completion_claim": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
