#!/usr/bin/env python3
"""Discover Python corpus packages and build the governed protocol registry."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from source_model import (
    AUTHORITY_CLASSES,
    CONTRACTS,
    PACKAGE_KINDS,
    PROTOCOL_VERSION,
    REBUILD_POLICIES,
    WRITE_POLICIES,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCAN_ROOTS = [ROOT / "research/domain_atlas", ROOT / "research/product_ontology", ROOT / "research/analytics_landscape"]
AS_OF = "2026-08-27"

MIGRATION_WAVES = {
    "M00_AUTHORED_VALIDATION_CLASSIFICATION": ([], "Separate authored sources, immutable snapshots and aggregate validators from regenerable projections."),
    "M01_UNIVERSE_AND_EVIDENCE_PRODUCERS": (["M00_AUTHORED_VALIDATION_CLASSIFICATION"], "Contract source, shape, operation, method, presentation and other universe producers before their consumers."),
    "M02_VERTICAL_CONTEXT_AND_REFERENCE_PRODUCERS": (["M00_AUTHORED_VALIDATION_CLASSIFICATION", "M01_UNIVERSE_AND_EVIDENCE_PRODUCERS"], "Contract industries, context maps, reference spines and vertical demand producers."),
    "M03_PRODUCT_BOUNDARY_AND_ADJUDICATION": (["M01_UNIVERSE_AND_EVIDENCE_PRODUCERS", "M02_VERTICAL_CONTEXT_AND_REFERENCE_PRODUCERS"], "Contract product research, boundary adjudication, dossier and migration projections."),
    "M04_SEMANTIC_CONTRACT_AND_COORDINATE_GRAPH": (["M01_UNIVERSE_AND_EVIDENCE_PRODUCERS", "M03_PRODUCT_BOUNDARY_AND_ADJUDICATION"], "Contract semantic axes, evidence campaigns, coordinate packages, exact-contract and owner-adjudication projections."),
    "M05_COMPILER_BINDING_AND_CODEGEN": (["M04_SEMANTIC_CONTRACT_AND_COORDINATE_GRAPH"], "Contract binder, mapper, IR, codegen, implementation architecture and conformance compiler packages."),
    "M06_QUALIFICATION_EXECUTION_AND_ACCEPTANCE": (["M03_PRODUCT_BOUNDARY_AND_ADJUDICATION", "M04_SEMANTIC_CONTRACT_AND_COORDINATE_GRAPH", "M05_COMPILER_BINDING_AND_CODEGEN"], "Separate test harnesses, execution campaigns, independent qualification and vertical/system acceptance evidence."),
    "M07_CLOSURE_FIXED_POINT_AND_GLOBAL_ROUTING": (["M02_VERTICAL_CONTEXT_AND_REFERENCE_PRODUCERS", "M03_PRODUCT_BOUNDARY_AND_ADJUDICATION", "M04_SEMANTIC_CONTRACT_AND_COORDINATE_GRAPH", "M05_COMPILER_BINDING_AND_CODEGEN", "M06_QUALIFICATION_EXECUTION_AND_ACCEPTANCE"], "Contract repository-wide inventories, closure projections, routers and aggregate validation as bounded fixed-point consumers."),
    "M08_RESIDUAL_PACKAGE_ADJUDICATION": (["M00_AUTHORED_VALIDATION_CLASSIFICATION"], "Adjudicate packages that do not yet map safely to a known build-system responsibility."),
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def discover() -> list[dict[str, Any]]:
    by_dir: dict[Path, dict[str, list[str]]] = defaultdict(lambda: {"build": [], "validate": []})
    for scan_root in SCAN_ROOTS:
        for path in scan_root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            name = path.name
            if name.startswith(("build", "generate")):
                by_dir[path.parent]["build"].append(relative(path))
            if name.startswith("validate"):
                by_dir[path.parent]["validate"].append(relative(path))

    contracts_by_root = {row["root"]: row["package_id"] for row in CONTRACTS}
    rows = []
    for directory, scripts in sorted(by_dir.items(), key=lambda item: relative(item[0])):
        # Self-hosting output would make discovery depend on whether this package
        # has already been generated.  The protocol package is validated directly
        # and is excluded from its legacy migration census.
        if directory == HERE:
            continue
        root = relative(directory)
        local_manifests = sorted(relative(p) for p in directory.glob("*manifest*.json"))
        local_schemas = sorted(
            relative(p)
            for pattern in ("*.schema.json", "schema/*.json", "schemas/*.json")
            for p in directory.glob(pattern)
            if p.is_file()
        )
        candidate_id = "candidate." + root.removeprefix("research/").replace("/", ".").replace("-", "_")
        rows.append(
            {
                "record_kind": "observed_python_corpus_package",
                "candidate_id": candidate_id,
                "root": root,
                "build_scripts": sorted(scripts["build"]),
                "validate_scripts": sorted(scripts["validate"]),
                "local_manifest_paths": local_manifests,
                "local_schema_paths": local_schemas,
                "readme_present": (directory / "README.md").is_file(),
                "declared_contract_ref": contracts_by_root.get(root),
                "contract_state": "EXPLICIT_CONTRACT" if root in contracts_by_root else "LEGACY_DISCOVERED_UNCONTRACTED",
                "schema_state": "LOCAL_SCHEMA_PRESENT" if local_schemas else "NO_LOCAL_SCHEMA_OBSERVED_NOT_PROOF_OF_ABSENCE",
                "completion_claim": False,
            }
        )
    return rows


def topo(contracts: list[dict[str, Any]]) -> list[str]:
    by_id = {row["package_id"]: row for row in contracts}
    indegree = {key: 0 for key in by_id}
    outgoing: dict[str, set[str]] = defaultdict(set)
    for row in contracts:
        for dep in row["dependency_refs"]:
            if dep not in by_id:
                raise ValueError(f"{row['package_id']}: unknown dependency {dep}")
            indegree[row["package_id"]] += 1
            outgoing[dep].add(row["package_id"])
    ready = sorted(key for key, value in indegree.items() if value == 0)
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for nxt in sorted(outgoing[node]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
                ready.sort()
    if len(order) != len(by_id):
        raise ValueError("declared package dependency graph contains a cycle")
    return order


def migration_wave(row: dict[str, Any]) -> str:
    root = row["root"]
    if not row["build_scripts"]:
        return "M00_AUTHORED_VALIDATION_CLASSIFICATION"
    if "/executions/" in root or "qualification" in root or "acceptance" in root or "composition_pilots" in root:
        return "M06_QUALIFICATION_EXECUTION_AND_ACCEPTANCE"
    if "/universes/" in root or "analytics_landscape" in root:
        return "M01_UNIVERSE_AND_EVIDENCE_PRODUCERS"
    if "/industries" in root or "/context_map" in root or "canonical_reference" in root:
        return "M02_VERTICAL_CONTEXT_AND_REFERENCE_PRODUCERS"
    if "/semantic_decomposition/" in root:
        return "M04_SEMANTIC_CONTRACT_AND_COORDINATE_GRAPH"
    if "/compiler/" in root:
        return "M05_COMPILER_BINDING_AND_CODEGEN"
    if any(token in root for token in ("/adjudications/", "/dossier_readiness", "/boundary_", "/inventory_challenges/", "/upstream_demand")):
        return "M03_PRODUCT_BOUNDARY_AND_ADJUDICATION"
    if any(token in root for token in ("/closure_program", "/global_boundary_research", "/corpus_architecture_router", "/semantic_fixed_point_campaign")):
        return "M07_CLOSURE_FIXED_POINT_AND_GLOBAL_ROUTING"
    return "M08_RESIDUAL_PACKAGE_ADJUDICATION"


def suggested_kind(row: dict[str, Any]) -> str:
    root = row["root"]
    if "/executions/" in root or "qualification" in root or "acceptance" in root:
        return "execution_campaign"
    if not row["build_scripts"] and row["validate_scripts"]:
        return "authored_source_or_aggregate_validator_UNRESOLVED"
    if row["build_scripts"]:
        return "deterministic_projection_CANDIDATE_UNPROVEN"
    return "package_kind_UNRESOLVED"


def outputs() -> dict[str, str]:
    observed = discover()
    order = topo(CONTRACTS)
    order_index = {package_id: index for index, package_id in enumerate(order, 1)}
    contracts = [
        {
            "record_kind": "corpus_build_package_contract",
            "protocol_version": PROTOCOL_VERSION,
            **row,
            "topological_order": order_index[row["package_id"]],
            "completion_claim": False,
        }
        for row in sorted(CONTRACTS, key=lambda row: order_index[row["package_id"]])
    ]
    edges = [
        {
            "record_kind": "corpus_build_dependency_edge",
            "edge_id": f"edge.{dep.removeprefix('package.')}.to.{row['package_id'].removeprefix('package.')}",
            "upstream_ref": dep,
            "downstream_ref": row["package_id"],
            "edge_semantics": "upstream_validation_required_before_downstream_build",
            "completion_claim": False,
        }
        for row in contracts
        for dep in row["dependency_refs"]
    ]
    gaps = []
    for row in observed:
        if row["declared_contract_ref"] is None:
            gaps.append(
                {
                    "record_kind": "corpus_build_protocol_migration_gap",
                    "gap_id": "gap.package-contract." + row["candidate_id"].removeprefix("candidate."),
                    "package_candidate_ref": row["candidate_id"],
                    "root": row["root"],
                    "gap_kind": "EXPLICIT_PACKAGE_CONTRACT_MISSING",
                    "required_evidence": ["input ownership", "output ownership", "dependency edges", "write boundary", "rebuild policy", "authority class"],
                    "compiler_or_orchestrator_action": "REFUSE_AUTOMATIC_EXECUTION",
                    "completion_claim": False,
                }
            )
        if not row["build_scripts"] and row["validate_scripts"]:
            gaps.append(
                {
                    "record_kind": "corpus_build_protocol_migration_gap",
                    "gap_id": "gap.build-classification." + row["candidate_id"].removeprefix("candidate."),
                    "package_candidate_ref": row["candidate_id"],
                    "root": row["root"],
                    "gap_kind": "VALIDATE_ONLY_OR_AUTHORED_PACKAGE_CLASSIFICATION_REQUIRED",
                    "required_evidence": ["authored_source, aggregate_validator or historical_snapshot disposition"],
                    "compiler_or_orchestrator_action": "REFUSE_REGENERATION",
                    "completion_claim": False,
                }
            )
        if row["build_scripts"] and not row["validate_scripts"]:
            gaps.append(
                {
                    "record_kind": "corpus_build_protocol_migration_gap",
                    "gap_id": "gap.validator." + row["candidate_id"].removeprefix("candidate."),
                    "package_candidate_ref": row["candidate_id"],
                    "root": row["root"],
                    "gap_kind": "VALIDATOR_NOT_OBSERVED_IN_PACKAGE_ROOT",
                    "required_evidence": ["bounded validator command or explicit parent-validator ownership"],
                    "compiler_or_orchestrator_action": "REFUSE_AUTOMATIC_EXECUTION",
                    "completion_claim": False,
                }
            )

    gaps_by_candidate: dict[str, list[str]] = defaultdict(list)
    for gap in gaps:
        gaps_by_candidate[gap["package_candidate_ref"]].append(gap["gap_id"])
    dockets = []
    for row in observed:
        if row["declared_contract_ref"] is not None:
            continue
        dockets.append(
            {
                "record_kind": "corpus_build_contract_candidate_docket",
                "docket_id": "docket.package-contract." + row["candidate_id"].removeprefix("candidate."),
                "package_candidate_ref": row["candidate_id"],
                "root": row["root"],
                "migration_wave_ref": migration_wave(row),
                "suggested_package_kind": suggested_kind(row),
                "observed_build_scripts": row["build_scripts"],
                "observed_validate_scripts": row["validate_scripts"],
                "observed_manifest_paths": row["local_manifest_paths"],
                "observed_schema_paths": row["local_schema_paths"],
                "decision_axes": {
                    "input_ownership": "UNRESOLVED",
                    "output_ownership": "UNRESOLVED",
                    "dependency_edges": "UNRESOLVED",
                    "package_kind": "UNRATIFIED_CANDIDATE",
                    "authority_class": "UNRESOLVED",
                    "determinism": "UNPROVEN",
                    "write_boundary": "UNRESOLVED",
                    "fixed_point_membership": "UNRESOLVED",
                    "execution_risk": "UNASSESSED",
                },
                "migration_gap_refs": sorted(gaps_by_candidate[row["candidate_id"]]),
                "orchestrator_action": "REFUSE_AUTOMATIC_EXECUTION",
                "completion_claim": False,
            }
        )

    dockets_by_wave: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for docket in dockets:
        dockets_by_wave[docket["migration_wave_ref"]].append(docket)
    migration_batches = []
    for wave_id, (depends_on, objective) in MIGRATION_WAVES.items():
        rows = dockets_by_wave[wave_id]
        migration_batches.append(
            {
                "record_kind": "corpus_build_protocol_migration_batch",
                "batch_id": wave_id,
                "depends_on": depends_on,
                "objective": objective,
                "package_candidate_count": len(rows),
                "package_candidate_refs": sorted(row["package_candidate_ref"] for row in rows),
                "build_and_validate_candidates": sum(bool(row["observed_build_scripts"] and row["observed_validate_scripts"]) for row in rows),
                "build_without_local_validator_candidates": sum(bool(row["observed_build_scripts"] and not row["observed_validate_scripts"]) for row in rows),
                "validate_without_local_builder_candidates": sum(bool(row["observed_validate_scripts"] and not row["observed_build_scripts"]) for row in rows),
                "exit_condition": "Every candidate has an explicit input/output/dependency/authority/write/rebuild contract or an authored, historical, aggregate, external, merged or retired disposition.",
                "automatic_execution_enabled": False,
                "completion_claim": False,
            }
        )
    vocabulary = [
        *({"record_kind": "package_kind_definition", "term": key, "definition": value} for key, value in sorted(PACKAGE_KINDS.items())),
        *({"record_kind": "authority_class_definition", "term": key} for key in sorted(AUTHORITY_CLASSES)),
        *({"record_kind": "rebuild_policy_definition", "term": key} for key in sorted(REBUILD_POLICIES)),
        *({"record_kind": "write_policy_definition", "term": key} for key in sorted(WRITE_POLICIES)),
    ]
    summary = {
        "protocol_id": "protocol.corpus-build.v1",
        "protocol_version": PROTOCOL_VERSION,
        "as_of": AS_OF,
        "observed_python_package_candidates": len(observed),
        "explicit_package_contracts": len(contracts),
        "executable_contracts": sum(row["execution_enabled"] for row in contracts),
        "fixed_point_packages": sum(row["package_kind"] == "fixed_point_projection" for row in contracts),
        "aggregate_validators": sum(row["package_kind"] == "aggregate_validator" for row in contracts),
        "uncontracted_observed_packages": sum(row["declared_contract_ref"] is None for row in observed),
        "migration_gap_records": len(gaps),
        "contract_candidate_dockets": len(dockets),
        "migration_batches": len(migration_batches),
        "dependency_edges": len(edges),
        "topological_nodes": len(order),
        "world_completion_claim": False,
        "completion_claim": False,
    }
    files = {
        "package-contracts.jsonl": "".join(canonical(row) + "\n" for row in contracts),
        "observed-package-candidates.jsonl": "".join(canonical(row) + "\n" for row in observed),
        "dependency-edges.jsonl": "".join(canonical(row) + "\n" for row in edges),
        "migration-gaps.jsonl": "".join(canonical(row) + "\n" for row in gaps),
        "contract-candidate-dockets.jsonl": "".join(canonical(row) + "\n" for row in dockets),
        "migration-batches.jsonl": "".join(canonical(row) + "\n" for row in migration_batches),
        "protocol-vocabulary.jsonl": "".join(canonical(row) + "\n" for row in vocabulary),
        "summary.json": json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(text.encode()), "sha256": digest_bytes(text.encode())} for name, text in files.items()}
    files["manifest.json"] = json.dumps(
        {"manifest_id": "manifest.corpus-build-protocol.v1", "as_of": AS_OF, "files": claims, "completion_claim": False},
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    built = outputs()
    for name, text in built.items():
        (HERE / name).write_text(text, encoding="utf-8")
    summary = json.loads(built["summary.json"])
    print(
        "BUILD PASS corpus build protocol: "
        f"{summary['explicit_package_contracts']} explicit contracts over "
        f"{summary['observed_python_package_candidates']} observed package candidates; "
        f"{summary['uncontracted_observed_packages']} migrations remain fail-closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
