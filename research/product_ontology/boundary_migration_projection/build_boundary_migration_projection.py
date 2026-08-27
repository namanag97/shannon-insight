#!/usr/bin/env python3
"""Project merge/defer product adjudications into exact responsibility-migration work."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parent
REPO = PRODUCT.parents[1]
AS_OF = "2026-08-27"

ARCHETYPES = PRODUCT / "global_boundary_research/product-archetypes.jsonl"
IMPORTS = PRODUCT / "global_boundary_research/capability-imports.jsonl"
PACKS = PRODUCT / "global_boundary_research/industry-solution-packs.jsonl"
PROGRAMS = PRODUCT / "qualification_program/product-qualification-programs.jsonl"
ADJUDICATIONS = PRODUCT / "adjudications"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def target_kind(ref: str) -> str:
    prefix = ref.split(".", 1)[0]
    return {
        "artifact": "PRESENTATION_OR_DOMAIN_ARTIFACT",
        "capability": "CAPABILITY",
        "component": "COMPONENT",
        "interface": "INTERFACE",
        "library": "LIBRARY",
        "neighbor": "NEIGHBOR_BOUNDED_CONTEXT",
        "pattern": "ARCHITECTURE_OR_COMPOSITION_PATTERN",
        "product": "PRODUCT",
        "provider": "PROVIDER_OFFER_BOUNDARY",
        "semantic": "SEMANTIC_OWNER_OR_CONTRACT",
        "standard": "EXTERNAL_STANDARD_BOUNDARY",
        "suite": "COMMERCIAL_OR_EXPERIENCE_SUITE",
    }.get(prefix, "UNCLASSIFIED_BOUNDARY_REF")


def build() -> dict[str, Any]:
    archetypes = load_jsonl(ARCHETYPES)
    imports = load_jsonl(IMPORTS)
    packs = load_jsonl(PACKS)
    programs = load_jsonl(PROGRAMS)
    retained_products = {row["product_ref"] for row in programs}
    retained_candidates = {row["candidate_id"] for row in programs}
    nonretained = {
        row["record_id"]: row
        for row in archetypes
        if row["record_id"] not in retained_candidates
    }

    crosswalks_by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in sorted(ADJUDICATIONS.glob("*/legacy-crosswalks.jsonl")):
        for row in load_jsonl(path):
            if row["legacy_ref"] not in nonretained:
                continue
            relative = path.relative_to(REPO).as_posix()
            crosswalks_by_candidate[row["legacy_ref"]].append(
                {
                    "crosswalk_ref": f"{relative}#{slug(row['legacy_ref'])}-{slug('-'.join(row['canonical_refs']))}",
                    "source_path": relative,
                    "disposition": row["disposition"],
                    "target_refs": row["canonical_refs"],
                }
            )

    boundary_rows = []
    boundary_by_candidate = {}
    for candidate_ref, source in sorted(nonretained.items()):
        crosswalks = sorted(crosswalks_by_candidate[candidate_ref], key=lambda row: row["crosswalk_ref"])
        target_refs = sorted({ref for row in crosswalks for ref in row["target_refs"]})
        targets = [
            {
                "target_ref": ref,
                "target_kind": target_kind(ref),
                "retained_product_resolution": ref if ref in retained_products else None,
                "resolution_class": "RETAINED_PRODUCT_BOUNDARY" if ref in retained_products else "NONPRODUCT_ADJUDICATION_TARGET",
                "target_ratification": "WITHHELD",
            }
            for ref in target_refs
        ]
        verdict = source["boundary_evaluation"]["verdict"]
        docket_id = f"docket.product-boundary-migration.{slug(candidate_ref)}.v1"
        row = {
            "record_kind": "nonretained_product_boundary_migration_docket",
            "docket_id": docket_id,
            "candidate_ref": candidate_ref,
            "candidate_name": source["name"],
            "family": source["family"],
            "boundary_verdict": verdict,
            "adjudication_disposition": source["boundary_evaluation"]["adjudication_disposition"],
            "adjudication_ref": source["boundary_evaluation"]["adjudication_ref"],
            "owned_meanings": source["owned_meanings"],
            "crosswalks": crosswalks,
            "crosswalk_count": len(crosswalks),
            "target_boundaries": targets,
            "target_boundary_count": len(targets),
            "cross_context_reconciliation_required": len(crosswalks) > 1,
            "migration_semantics": "SPLIT_OR_RECLASSIFY_NO_COMPATIBILITY_ALIAS",
            "status": "DEFERRED_BOUNDARY_RESEARCH" if verdict == "defer" else "RECLASSIFICATION_UNRATIFIED",
            "refusal_reasons": [
                "RESPONSIBILITY_LEVEL_MIGRATION_UNRATIFIED",
                "TARGET_SEMANTIC_OWNERS_UNRATIFIED",
                *(["CROSS_CONTEXT_CROSSWALKS_UNRECONCILED"] if len(crosswalks) > 1 else []),
            ],
            "completion_claim": False,
        }
        boundary_rows.append(row)
        boundary_by_candidate[candidate_ref] = row

    capability_rows = []
    capability_by_import = {}
    for source in sorted(imports, key=lambda row: row["record_id"]):
        if source["candidate_id"] not in nonretained:
            continue
        boundary = boundary_by_candidate[source["candidate_id"]]
        docket_id = f"docket.capability-import-migration.{slug(source['record_id'])}.v1"
        row = {
            "record_kind": "capability_import_boundary_migration_docket",
            "docket_id": docket_id,
            "source_import_ref": source["record_id"],
            "source_candidate_ref": source["candidate_id"],
            "source_boundary_docket_ref": boundary["docket_id"],
            "capability_ref": source["capability_id"],
            "semantic_context_ref": source["semantic_context_ref"],
            "candidate_target_refs": [target["target_ref"] for target in boundary["target_boundaries"]],
            "selected_target_ref": None,
            "responsibility_assignment": "UNRESOLVED",
            "compatibility_alias_allowed": False,
            "compiler_action": "REFUSE_MIGRATED_CAPABILITY_IMPORT",
            "refusal_reasons": [
                "PER_CAPABILITY_RESPONSIBILITY_NOT_ASSIGNED",
                "TARGET_CONTRACT_AND_OWNER_UNRATIFIED",
                *(["CROSS_CONTEXT_CROSSWALKS_UNRECONCILED"] if boundary["cross_context_reconciliation_required"] else []),
            ],
            "completion_claim": False,
        }
        capability_rows.append(row)
        capability_by_import[source["record_id"]] = row

    solution_rows = []
    for pack in sorted(packs, key=lambda row: row["record_id"]):
        for candidate_ref in pack["composes_candidate_ids"]:
            if candidate_ref not in nonretained:
                continue
            boundary = boundary_by_candidate[candidate_ref]
            solution_rows.append(
                {
                    "record_kind": "solution_pack_product_boundary_migration_docket",
                    "docket_id": f"docket.solution-pack-boundary-migration.{slug(pack['record_id'])}.{slug(candidate_ref)}.v1",
                    "solution_pack_ref": pack["record_id"],
                    "industry_ref": pack["industry_id"],
                    "source_candidate_ref": candidate_ref,
                    "source_boundary_docket_ref": boundary["docket_id"],
                    "candidate_target_refs": [target["target_ref"] for target in boundary["target_boundaries"]],
                    "selected_composition_target_refs": [],
                    "composition_rewrite": "UNRESOLVED",
                    "compatibility_alias_allowed": False,
                    "compiler_action": "REFUSE_SOLUTION_PACK_BOUNDARY_MIGRATION",
                    "refusal_reasons": [
                        "DEFERRED_OR_RECLASSIFIED_PRODUCT_EDGE",
                        "COMPOSITION_RESPONSIBILITIES_NOT_REWRITTEN",
                        "TARGET_BOUNDARIES_UNRATIFIED",
                    ],
                    "completion_claim": False,
                }
            )

    reconciliation_rows = []
    for boundary in boundary_rows:
        if not boundary["cross_context_reconciliation_required"]:
            continue
        reconciliation_rows.append(
            {
                "record_kind": "cross_context_legacy_crosswalk_reconciliation_docket",
                "docket_id": f"docket.cross-context-crosswalk.{slug(boundary['candidate_ref'])}.v1",
                "candidate_ref": boundary["candidate_ref"],
                "boundary_docket_ref": boundary["docket_id"],
                "crosswalk_refs": [row["crosswalk_ref"] for row in boundary["crosswalks"]],
                "union_target_refs": [row["target_ref"] for row in boundary["target_boundaries"]],
                "required_decisions": [
                    "classify each target as complementary, overlapping or contradictory",
                    "assign every source meaning and imported capability to exactly one primary target",
                    "retain secondary dependency edges without creating an alias",
                    "ratify the responsible bounded-context owners",
                ],
                "status": "OPEN_CROSS_CONTEXT_RECONCILIATION",
                "completion_claim": False,
            }
        )

    work_rows = []
    imports_by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in capability_rows:
        imports_by_candidate[row["source_candidate_ref"]].append(row)
    solutions_by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in solution_rows:
        solutions_by_candidate[row["source_candidate_ref"]].append(row)
    for boundary in boundary_rows:
        work_rows.append(
            {
                "record_kind": "product_boundary_migration_work_package",
                "work_package_id": f"work.product-boundary-migration.{slug(boundary['candidate_ref'])}.v1",
                "candidate_ref": boundary["candidate_ref"],
                "boundary_docket_ref": boundary["docket_id"],
                "represented_owned_meanings": boundary["owned_meanings"],
                "capability_import_migration_docket_refs": [row["docket_id"] for row in imports_by_candidate[boundary["candidate_ref"]]],
                "solution_pack_migration_docket_refs": [row["docket_id"] for row in solutions_by_candidate[boundary["candidate_ref"]]],
                "target_boundary_refs": [row["target_ref"] for row in boundary["target_boundaries"]],
                "required_closure": [
                    "lossless responsibility migration",
                    "one primary semantic owner per responsibility within a bounded context",
                    "explicit dependency edges for non-owning targets",
                    "capability import contract rewrite",
                    "negative test proving the former product alias is unnecessary",
                    "owner ratification receipt",
                ],
                "status": "BLOCKED_OWNER_RATIFICATION_AND_RESPONSIBILITY_MAPPING",
                "completion_claim": False,
            }
        )

    summary = {
        "program_id": "program.product-boundary-migration-projection.v1",
        "as_of": AS_OF,
        "global_product_candidates": len(archetypes),
        "retained_product_candidates": len(retained_candidates),
        "nonretained_product_candidates": len(boundary_rows),
        "merge_candidates": sum(row["boundary_verdict"] == "merge" for row in boundary_rows),
        "deferred_candidates": sum(row["boundary_verdict"] == "defer" for row in boundary_rows),
        "legacy_crosswalks": sum(row["crosswalk_count"] for row in boundary_rows),
        "cross_context_reconciliations": len(reconciliation_rows),
        "capability_import_migrations": len(capability_rows),
        "solution_pack_product_edge_migrations": len(solution_rows),
        "migration_work_packages": len(work_rows),
        "responsibility_assignments_ratified": 0,
        "compiler_migrations_permitted": 0,
        "compatibility_aliases_allowed": 0,
        "completion_claim": False,
    }
    return {
        "boundaries": boundary_rows,
        "capabilities": capability_rows,
        "solutions": solution_rows,
        "reconciliations": reconciliation_rows,
        "work": work_rows,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "nonretained-product-boundary-dockets.jsonl": "".join(canonical(row) + "\n" for row in built["boundaries"]),
        "capability-import-migration-dockets.jsonl": "".join(canonical(row) + "\n" for row in built["capabilities"]),
        "solution-pack-boundary-migration-dockets.jsonl": "".join(canonical(row) + "\n" for row in built["solutions"]),
        "cross-context-crosswalk-reconciliation-dockets.jsonl": "".join(canonical(row) + "\n" for row in built["reconciliations"]),
        "boundary-migration-work-packages.jsonl": "".join(canonical(row) + "\n" for row in built["work"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps(
        {"manifest_id": "manifest.product-boundary-migration-projection.v1", "as_of": AS_OF, "files": claims, "completion_claim": False},
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(
        "BUILD PASS product boundary migration projection: "
        f"{summary['nonretained_product_candidates']} quotient work packages cover "
        f"{summary['capability_import_migrations']} capability imports and "
        f"{summary['solution_pack_product_edge_migrations']} solution-pack edge; all migrations refuse"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
