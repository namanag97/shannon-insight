#!/usr/bin/env python3
"""Project exact library coordinate obligations into products and vertical assemblies."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
RESEARCH = SEM.parents[4]
PRODUCT = RESEARCH / "product_ontology"
AS_OF = "2026-08-27"

SUBJECTS = PRODUCT / "qualification_program/library-qualification-subjects.jsonl"
PROGRAMS = PRODUCT / "qualification_program/product-qualification-programs.jsonl"
READINESS = PRODUCT / "dossier_readiness/product-readiness.jsonl"
IMPORTS = PRODUCT / "global_boundary_research/capability-imports.jsonl"
PACKS = PRODUCT / "global_boundary_research/industry-solution-packs.jsonl"
VERTICALS = PRODUCT / "composition_pilots/deterministic_verticals/vertical-compositions.jsonl"
CAPABILITY_MIGRATIONS = PRODUCT / "boundary_migration_projection/capability-import-migration-dockets.jsonl"
SOLUTION_PACK_MIGRATIONS = PRODUCT / "boundary_migration_projection/solution-pack-boundary-migration-dockets.jsonl"
P6_SUBJECTS = SEM / "p6_implementation_qualification/subject-dockets.jsonl"
P6_PRODUCTS = SEM / "p6_implementation_qualification/product-qualification-dockets.jsonl"
P6_RESOLUTIONS = SEM / "p6_implementation_qualification/concrete-reference-resolutions.jsonl"
P8_PRODUCTS = SEM / "p8_vertical_acceptance_tensor/product-two-vertical-acceptance-gates.jsonl"
LIBRARY_DOCKETS = SEM / "library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def build() -> dict[str, Any]:
    subjects = load_jsonl(SUBJECTS)
    programs = load_jsonl(PROGRAMS)
    readiness = {row["local_subject_ref"]: row for row in load_jsonl(READINESS)}
    imports = load_jsonl(IMPORTS)
    packs = load_jsonl(PACKS)
    verticals = load_jsonl(VERTICALS)
    capability_migrations = {row["source_import_ref"]: row for row in load_jsonl(CAPABILITY_MIGRATIONS)}
    solution_pack_migrations = {
        (row["solution_pack_ref"], row["source_candidate_ref"]): row
        for row in load_jsonl(SOLUTION_PACK_MIGRATIONS)
    }
    p6_subjects = {row["subject_ref"]: row for row in load_jsonl(P6_SUBJECTS)}
    p6_products = {row["product_ref"]: row for row in load_jsonl(P6_PRODUCTS)}
    resolutions = {row["concrete_library_ref"]: row for row in load_jsonl(P6_RESOLUTIONS)}
    p8_products = {row["product_ref"]: row for row in load_jsonl(P8_PRODUCTS)}
    library_dockets = {row["library_ref"]: row for row in load_jsonl(LIBRARY_DOCKETS)}
    program_by_product = {row["product_ref"]: row for row in programs}
    product_by_candidate = {row["candidate_id"]: row["product_ref"] for row in programs}

    provider_subjects: dict[str, list[str]] = defaultdict(list)
    for subject in subjects:
        for capability in subject["provided_capability_refs"]:
            provider_subjects[capability].append(subject["subject_id"])

    subject_rows: list[dict[str, Any]] = []
    subject_projection_by_ref: dict[str, dict[str, Any]] = {}
    for subject in sorted(subjects, key=lambda row: row["subject_id"]):
        edges = []
        for concrete_ref in subject["compiler_projection"]["concrete_library_refs"]:
            resolution = resolutions[concrete_ref]
            coordinate = library_dockets.get(concrete_ref)
            edges.append(
                {
                    "concrete_library_ref": concrete_ref,
                    "resolution_ref": resolution["resolution_id"],
                    "resolution_class": resolution["resolution_class"],
                    "coordinate_binding_docket_ref": coordinate["binding_docket_id"] if coordinate else None,
                    "coordinate_axis_requirement_count": coordinate["axis_requirement_count"] if coordinate else 0,
                    "binding_status": "REFUSED_COORDINATE_AND_QUALIFICATION" if coordinate else "REFUSED_CONCRETE_REFERENCE_RESOLUTION",
                }
            )
        classes = Counter(edge["resolution_class"] for edge in edges)
        refusal_reasons = ["SUBJECT_IMPLEMENTATION_UNQUALIFIED", "EXACT_CONTRACT_UNSELECTED"]
        if any(edge["coordinate_binding_docket_ref"] for edge in edges):
            refusal_reasons.append("CANONICAL_LIBRARY_COORDINATES_UNRESOLVED")
        if any(not edge["coordinate_binding_docket_ref"] for edge in edges):
            refusal_reasons.append("NON_CANONICAL_REFERENCE_NOT_COORDINATE_BOUND")
        p6 = p6_subjects[subject["subject_id"]]
        row = {
            "record_kind": "product_subject_coordinate_binding_projection",
            "projection_id": f"projection.product-subject-coordinate.{slug(subject['subject_id'])}.v1",
            "subject_ref": subject["subject_id"],
            "product_ref": subject["product_ref"],
            "candidate_ref": subject["candidate_id"],
            "abstract_library_ref": subject["abstract_library_ref"],
            "source_binding_map_ref": subject["compiler_projection"]["mapping_ref"],
            "source_projection_disposition": subject["compiler_projection"]["disposition"],
            "p6_subject_docket_ref": p6["docket_id"],
            "concrete_bindings": edges,
            "concrete_reference_count": len(edges),
            "canonical_coordinate_binding_count": sum(bool(edge["coordinate_binding_docket_ref"]) for edge in edges),
            "noncanonical_resolution_count": sum(not edge["coordinate_binding_docket_ref"] for edge in edges),
            "resolution_class_counts": dict(sorted(classes.items())),
            "provided_capability_refs": subject["provided_capability_refs"],
            "compiler_binding": "REFUSED",
            "refusal_reasons": refusal_reasons,
            "completion_claim": False,
        }
        subject_rows.append(row)
        subject_projection_by_ref[subject["subject_id"]] = row

    capability_rows: list[dict[str, Any]] = []
    capability_refs_by_product: dict[str, list[str]] = defaultdict(list)
    for source in sorted(imports, key=lambda row: row["record_id"]):
        product_ref = product_by_candidate.get(source["candidate_id"])
        migration = capability_migrations.get(source["record_id"])
        obligation_id = f"obligation.capability-coordinate.{slug(source['record_id'])}.v1"
        if product_ref:
            capability_refs_by_product[product_ref].append(obligation_id)
        providers = sorted(provider_subjects.get(source["capability_id"], []))
        capability_rows.append(
            {
                "record_kind": "capability_import_coordinate_binding_obligation",
                "obligation_id": obligation_id,
                "source_import_ref": source["record_id"],
                "candidate_ref": source["candidate_id"],
                "retained_product_ref": product_ref,
                "target_boundary_class": "RETAINED_PRODUCT" if product_ref else "UNRETAINED_OR_LEGACY_CANDIDATE",
                "boundary_migration_docket_ref": migration["docket_id"] if migration else None,
                "migration_candidate_target_refs": migration["candidate_target_refs"] if migration else [],
                "capability_ref": source["capability_id"],
                "semantic_context_ref": source["semantic_context_ref"],
                "binding_phase": source["binding_phase"],
                "cardinality": source["cardinality"],
                "candidate_provider_subject_refs": providers,
                "selected_provider_subject_ref": None,
                "selected_qualified_offer_ref": None,
                "ownership_law": source["ownership_law"],
                "compiler_action": "REFUSE_CAPABILITY_IMPORT",
                "refusal_reasons": [
                    "NO_SELECTED_PROVIDER_SUBJECT",
                    "NO_QUALIFIED_PORTABLE_OFFER",
                    *([] if product_ref else ["TARGET_PRODUCT_BOUNDARY_NOT_RETAINED"]),
                ],
                "completion_claim": False,
            }
        )

    product_rows: list[dict[str, Any]] = []
    product_row_by_ref: dict[str, dict[str, Any]] = {}
    for program in sorted(programs, key=lambda row: row["product_ref"]):
        product_ref = program["product_ref"]
        projected_subjects = [subject_projection_by_ref[ref] for ref in program["library_subject_refs"]]
        concrete_refs = sorted({edge["concrete_library_ref"] for subject in projected_subjects for edge in subject["concrete_bindings"]})
        coordinate_refs = sorted({edge["coordinate_binding_docket_ref"] for subject in projected_subjects for edge in subject["concrete_bindings"] if edge["coordinate_binding_docket_ref"]})
        resolution_refs = sorted({edge["resolution_ref"] for subject in projected_subjects for edge in subject["concrete_bindings"] if not edge["coordinate_binding_docket_ref"]})
        ready = readiness[product_ref]
        p6 = p6_products[product_ref]
        p8 = p8_products[product_ref]
        row = {
            "record_kind": "product_coordinate_binding_docket",
            "binding_docket_id": f"docket.product-coordinate.{slug(product_ref)}.v1",
            "product_ref": product_ref,
            "candidate_ref": program["candidate_id"],
            "product_name": program["product_name"],
            "boundary_verdict": program["boundary_verdict"],
            "ddd_dossier_ref": program["ddd_dossier_ref"],
            "readiness_record_ref": ready["record_id"],
            "p6_product_qualification_docket_ref": p6["docket_id"],
            "p8_vertical_acceptance_gate_ref": p8["gate_id"],
            "subject_projection_refs": [subject["projection_id"] for subject in projected_subjects],
            "subject_count": len(projected_subjects),
            "concrete_library_refs": concrete_refs,
            "unique_concrete_reference_count": len(concrete_refs),
            "canonical_library_coordinate_docket_refs": coordinate_refs,
            "canonical_library_coordinate_docket_count": len(coordinate_refs),
            "noncanonical_concrete_resolution_refs": resolution_refs,
            "noncanonical_concrete_resolution_count": len(resolution_refs),
            "capability_import_obligation_refs": sorted(capability_refs_by_product.get(product_ref, [])),
            "capability_import_obligation_count": len(capability_refs_by_product.get(product_ref, [])),
            "compiler_assembly": "REFUSED",
            "refusal_reasons": [
                "ONE_OR_MORE_SUBJECT_BINDINGS_REFUSED",
                "COORDINATE_DECISIONS_UNRESOLVED",
                "NO_QUALIFIED_LIBRARY_IMPLEMENTATIONS",
                "NO_PORTABLE_PRODUCT_OFFER",
                "NO_EXECUTED_UNRELATED_VERTICAL_ACCEPTANCE",
                *(["CAPABILITY_IMPORTS_UNBOUND"] if capability_refs_by_product.get(product_ref) else []),
            ],
            "completion_claim": False,
        }
        product_rows.append(row)
        product_row_by_ref[product_ref] = row

    pack_rows: list[dict[str, Any]] = []
    for pack in sorted(packs, key=lambda row: row["record_id"]):
        bindings = []
        for candidate in pack["composes_candidate_ids"]:
            product_ref = product_by_candidate.get(candidate)
            migration = solution_pack_migrations.get((pack["record_id"], candidate))
            bindings.append(
                {
                    "candidate_ref": candidate,
                    "retained_product_ref": product_ref,
                    "product_coordinate_docket_ref": product_row_by_ref[product_ref]["binding_docket_id"] if product_ref else None,
                    "boundary_migration_docket_ref": migration["docket_id"] if migration else None,
                    "migration_candidate_target_refs": migration["candidate_target_refs"] if migration else [],
                    "binding_status": "REFUSED_PRODUCT_BINDING" if product_ref else "REFUSED_UNRETAINED_PRODUCT_BOUNDARY",
                }
            )
        pack_rows.append(
            {
                "record_kind": "industry_solution_pack_coordinate_binding_docket",
                "binding_docket_id": f"docket.solution-pack-coordinate.{slug(pack['record_id'])}.v1",
                "solution_pack_ref": pack["record_id"],
                "industry_ref": pack["industry_id"],
                "product_bindings": bindings,
                "product_binding_count": len(bindings),
                "unretained_product_boundary_count": sum(binding["retained_product_ref"] is None for binding in bindings),
                "vertical_ownership": pack["owns_vertical"],
                "horizontal_nonownership_law": pack["non_ownership_law"],
                "compiler_assembly": "REFUSED",
                "refusal_reasons": [
                    "ONE_OR_MORE_PRODUCT_BINDINGS_REFUSED",
                    "NO_QUALIFIED_PHYSICAL_BINDINGS",
                    "NO_EXECUTED_VERTICAL_ACCEPTANCE",
                    *(["UNRETAINED_PRODUCT_BOUNDARY"] if any(binding["retained_product_ref"] is None for binding in bindings) else []),
                ],
                "completion_claim": False,
            }
        )

    vertical_rows: list[dict[str, Any]] = []
    for vertical in sorted(verticals, key=lambda row: row["composition_id"]):
        product_bindings = []
        for candidate in vertical["product_refs"]:
            product_ref = product_by_candidate.get(candidate)
            product_bindings.append(
                {
                    "declared_product_ref": candidate,
                    "retained_product_ref": product_ref,
                    "product_coordinate_docket_ref": product_row_by_ref[product_ref]["binding_docket_id"] if product_ref else None,
                    "binding_status": "REFUSED_PRODUCT_BINDING" if product_ref else "REFUSED_UNRETAINED_PRODUCT_BOUNDARY",
                }
            )
        library_bindings = []
        for library_ref in vertical["required_library_refs"]:
            coordinate = library_dockets.get(library_ref)
            resolution = resolutions.get(library_ref)
            library_bindings.append(
                {
                    "library_ref": library_ref,
                    "coordinate_binding_docket_ref": coordinate["binding_docket_id"] if coordinate else None,
                    "concrete_resolution_ref": resolution["resolution_id"] if resolution else None,
                    "binding_status": "REFUSED_COORDINATE_BINDING" if coordinate else "REFUSED_NONCANONICAL_OR_UNREGISTERED_BINDING",
                }
            )
        vertical_rows.append(
            {
                "record_kind": "vertical_composition_coordinate_binding_docket",
                "binding_docket_id": f"docket.vertical-composition-coordinate.{slug(vertical['composition_id'])}.v1",
                "composition_ref": vertical["composition_id"],
                "vertical_case_ref": vertical["vertical_case_ref"],
                "industry_ref": vertical["industry_id"],
                "product_bindings": product_bindings,
                "product_binding_count": len(product_bindings),
                "library_bindings": library_bindings,
                "library_binding_count": len(library_bindings),
                "compiler_assembly": "REFUSED",
                "refusal_reasons": [
                    "PRODUCT_BINDINGS_REFUSED",
                    "LIBRARY_COORDINATE_BINDINGS_REFUSED",
                    "NO_QUALIFIED_PHYSICAL_BINDINGS",
                    "VERTICAL_ACCEPTANCE_NOT_EXECUTED",
                ],
                "completion_claim": False,
            }
        )

    gate_rows = []
    for kind, rows, ref_field in [
        ("PRODUCT", product_rows, "binding_docket_id"),
        ("INDUSTRY_SOLUTION_PACK", pack_rows, "binding_docket_id"),
        ("VERTICAL_COMPOSITION", vertical_rows, "binding_docket_id"),
    ]:
        for row in rows:
            gate_rows.append(
                {
                    "record_kind": "compiler_assembly_gate",
                    "gate_id": f"gate.compiler-assembly.{slug(row[ref_field])}.v1",
                    "assembly_kind": kind,
                    "binding_docket_ref": row[ref_field],
                    "verdict": "REFUSE_ASSEMBLY",
                    "refusal_reasons": row["refusal_reasons"],
                    "semantic_authority_receipt_refs": [],
                    "qualification_receipt_refs": [],
                    "vertical_acceptance_receipt_refs": [],
                    "completion_claim": False,
                }
            )

    all_concrete_edges = [edge for row in subject_rows for edge in row["concrete_bindings"]]
    summary = {
        "program_id": "program.product-coordinate-binding-projection.v1",
        "as_of": AS_OF,
        "qualification_subjects": len(subject_rows),
        "subject_concrete_reference_edges": len(all_concrete_edges),
        "unique_concrete_references": len({edge["concrete_library_ref"] for edge in all_concrete_edges}),
        "canonical_coordinate_bound_unique_references": len({edge["concrete_library_ref"] for edge in all_concrete_edges if edge["coordinate_binding_docket_ref"]}),
        "noncanonical_resolved_unique_references": len({edge["concrete_library_ref"] for edge in all_concrete_edges if not edge["coordinate_binding_docket_ref"]}),
        "retained_products": len(product_rows),
        "capability_import_obligations": len(capability_rows),
        "capability_imports_targeting_retained_products": sum(row["retained_product_ref"] is not None for row in capability_rows),
        "capability_imports_targeting_unretained_candidates": sum(row["retained_product_ref"] is None for row in capability_rows),
        "industry_solution_packs": len(pack_rows),
        "vertical_compositions": len(vertical_rows),
        "compiler_assembly_gates": len(gate_rows),
        "compiler_assemblies_permitted": 0,
        "semantic_authority_receipts": 0,
        "qualification_receipts": 0,
        "vertical_acceptance_receipts": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {
        "subjects": subject_rows,
        "products": product_rows,
        "capabilities": capability_rows,
        "packs": pack_rows,
        "verticals": vertical_rows,
        "gates": gate_rows,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "subject-coordinate-binding-projections.jsonl": "".join(canonical(row) + "\n" for row in built["subjects"]),
        "product-coordinate-binding-dockets.jsonl": "".join(canonical(row) + "\n" for row in built["products"]),
        "capability-import-coordinate-obligations.jsonl": "".join(canonical(row) + "\n" for row in built["capabilities"]),
        "industry-solution-pack-coordinate-dockets.jsonl": "".join(canonical(row) + "\n" for row in built["packs"]),
        "vertical-composition-coordinate-dockets.jsonl": "".join(canonical(row) + "\n" for row in built["verticals"]),
        "compiler-assembly-gates.jsonl": "".join(canonical(row) + "\n" for row in built["gates"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps(
        {"manifest_id": "manifest.product-coordinate-binding-projection.v1", "as_of": AS_OF, "files": claims, "completion_claim": False},
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(
        "BUILD PASS product coordinate binding projection: "
        f"{summary['qualification_subjects']} subjects -> {summary['retained_products']} products -> "
        f"{summary['industry_solution_packs']} packs + {summary['vertical_compositions']} verticals; all assemblies refuse"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
