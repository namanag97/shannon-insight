#!/usr/bin/env python3
"""Validate industry packs structurally and report compiler-integration gaps honestly."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ATLAS = ROOT.parent


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return records


def digest(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def declared_ids(records: list[dict], alias_fields: tuple[str, ...]) -> set[str]:
    """Return canonical IDs plus aliases explicitly declared by the records.

    Vertical packs were produced independently. Some deliberately retain a local
    human-facing identifier alongside ``record_id``. Accepting only declared
    aliases keeps the audit honest: this resolves representation differences but
    never guesses semantic equivalence.
    """
    identifiers: set[str] = set()
    for record in records:
        for field in ("record_id", *alias_fields):
            value = record.get(field)
            if isinstance(value, str) and value:
                identifiers.add(value)
    return identifiers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemas", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None
    if args.schemas and jsonschema is None:
        print("ERROR: jsonschema is required for --schemas")
        return 1
    schema = json.loads((ROOT / "schema/industry-research-record.schema.json").read_text())
    validator = jsonschema.Draft202012Validator(schema) if args.schemas else None

    source_classes = {
        record["class_id"]
        for record in load_jsonl(ATLAS / "universes/source_systems/source-classes.jsonl")
    }
    practice_candidates = {
        record["practice_id"]
        for record in load_jsonl(ATLAS / "universes/analytics_types/candidate-practices.jsonl")
    }
    operation_candidates = {
        record["operation_id"]
        for record in load_jsonl(ATLAS / "universes/operations/operation-candidates.jsonl")
    }
    industry_nodes = {
        record["record_id"]
        for record in load_jsonl(ROOT / "foundation/isic-rev5.nodes.jsonl")
    }

    packs = []
    global_ids: dict[str, list[tuple[str, str]]] = defaultdict(list)
    urls: dict[str, list[tuple[str, str]]] = defaultdict(list)
    all_method_refs: Counter[str] = Counter()
    all_operation_refs: Counter[str] = Counter()
    unresolved_source_classes: Counter[str] = Counter()
    unresolved_industry_refs: Counter[str] = Counter()
    reference_occurrences: dict[tuple[str, str], dict[str, object]] = defaultdict(
        lambda: {"packs": set(), "records": []}
    )

    def note_reference(domain: str, ref: str, pack: str, record_id: str) -> None:
        occurrence = reference_occurrences[(domain, ref)]
        occurrence["packs"].add(pack)  # type: ignore[union-attr]
        records = occurrence["records"]  # type: ignore[assignment]
        if len(records) < 25 and record_id not in records:  # type: ignore[arg-type]
            records.append(record_id)  # type: ignore[union-attr]

    for pack_dir in sorted(path for path in ROOT.iterdir() if path.is_dir()):
        required_files = {
            "cases": pack_dir / "analytics-cases.jsonl",
            "sources": pack_dir / "sources.jsonl",
            "systems": pack_dir / "source-systems.jsonl",
            "shapes": pack_dir / "data-shapes.jsonl",
        }
        if not all(path.exists() for path in required_files.values()):
            continue
        data = {kind: load_jsonl(path) for kind, path in required_files.items()}
        pack_errors = []
        records = [record for group in data.values() for record in group]
        for kind, group in data.items():
            for index, record in enumerate(group, 1):
                record_id = record.get("record_id")
                if not record_id:
                    pack_errors.append(f"{kind}:{index} lacks record_id")
                    continue
                global_ids[record_id].append((pack_dir.name, digest(record)))
                if validator:
                    schema_errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
                    for error in schema_errors:
                        pack_errors.append(f"{kind}:{record_id}: {error.message}")
                if record.get("record_kind") == "source_evidence":
                    urls[record.get("url", "")].append((record_id, pack_dir.name))

        evidence_ids = declared_ids(data["sources"], ("source_id", "evidence_id", "local_id", "legacy_id"))
        system_ids = declared_ids(
            data["systems"],
            ("source_system_need_id", "system_id", "source_system_id", "local_id", "legacy_id"),
        )
        shape_ids = declared_ids(data["shapes"], ("shape_id", "data_shape_id", "local_id", "legacy_id"))
        canonical_local_ids = {record["record_id"] for record in records if record.get("record_id")}
        if len(canonical_local_ids) != len(records):
            pack_errors.append("duplicate record IDs inside pack")
        for record in records:
            missing_evidence = sorted(set(record.get("evidence_refs", [])) - evidence_ids)
            if missing_evidence:
                pack_errors.append(f"{record['record_id']} unresolved evidence refs {missing_evidence}")
        for case in data["cases"]:
            missing_systems = sorted(set(case.get("source_system_refs", [])) - system_ids)
            missing_shapes = sorted(set(case.get("data_shape_refs", [])) - shape_ids)
            if missing_systems:
                pack_errors.append(f"{case['record_id']} unresolved source refs {missing_systems}")
            if missing_shapes:
                pack_errors.append(f"{case['record_id']} unresolved shape refs {missing_shapes}")
            all_method_refs.update(case.get("method_refs", []))
            all_operation_refs.update(case.get("operation_refs", []))
            for method_ref in case.get("method_refs", []):
                note_reference("analytical_practice", method_ref, pack_dir.name, case["record_id"])
            for operation_ref in case.get("operation_refs", []):
                note_reference("typed_operation", operation_ref, pack_dir.name, case["record_id"])
            for industry_ref in [case.get("industry_id"), *case.get("subindustry_ids", [])]:
                if industry_ref and industry_ref not in industry_nodes:
                    unresolved_industry_refs[industry_ref] += 1
                    note_reference("industry_classification", industry_ref, pack_dir.name, case["record_id"])
        for system in data["systems"]:
            source_class = system.get("source_class")
            if source_class not in source_classes:
                unresolved_source_classes[source_class or "<missing>"] += 1
                note_reference(
                    "source_system_class",
                    source_class or "<missing>",
                    pack_dir.name,
                    system["record_id"],
                )

        if len(data["sources"]) < 25:
            pack_errors.append("pack has fewer than 25 evidence sources")
        if not data["cases"]:
            pack_errors.append("pack has no analytical cases")
        packs.append({
            "pack_id": pack_dir.name,
            "cases": len(data["cases"]),
            "sources": len(data["sources"]),
            "source_system_needs": len(data["systems"]),
            "data_shape_needs": len(data["shapes"]),
            "structural_errors": pack_errors,
        })
        errors.extend(f"{pack_dir.name}: {error}" for error in pack_errors)

    id_collisions = {
        record_id: occurrences
        for record_id, occurrences in sorted(global_ids.items())
        if len(occurrences) > 1
    }
    conflicting_id_collisions = {
        record_id: occurrences
        for record_id, occurrences in id_collisions.items()
        if len({item[1] for item in occurrences}) > 1
    }
    duplicate_urls = {
        url: occurrences
        for url, occurrences in sorted(urls.items())
        if url and len(occurrences) > 1
    }
    exact_methods = {ref: count for ref, count in all_method_refs.items() if ref in practice_candidates}
    exact_operations = {ref: count for ref, count in all_operation_refs.items() if ref in operation_candidates}
    unresolved_methods = {ref: count for ref, count in all_method_refs.items() if ref not in practice_candidates}
    unresolved_operations = {ref: count for ref, count in all_operation_refs.items() if ref not in operation_candidates}

    unresolved_by_domain = {
        "analytical_practice": unresolved_methods,
        "typed_operation": unresolved_operations,
        "source_system_class": dict(unresolved_source_classes),
        "industry_classification": dict(unresolved_industry_refs),
    }
    queue_records = []
    for domain, unresolved in unresolved_by_domain.items():
        for raw_ref, count in sorted(unresolved.items()):
            occurrence = reference_occurrences[(domain, raw_ref)]
            queue_records.append({
                "record_kind": "canonical_reference_adjudication",
                "queue_id": f"refq.{domain}.{hashlib.sha256(raw_ref.encode()).hexdigest()[:16]}",
                "edition": 1,
                "status": "open",
                "reference_domain": domain,
                "raw_ref": raw_ref,
                "occurrence_count": count,
                "origin_packs": sorted(occurrence["packs"]),
                "example_origin_records": occurrence["records"],
                "candidate_target_refs": [],
                "relation": "unresolved",
                "decision_basis": [],
                "required_review": [
                    "compare definitions and laws, not labels alone",
                    "preserve vertical specificity when a horizontal canonical target is broader",
                    "split the canonical universe when the raw reference exposes a genuinely missing concept",
                ],
                "prohibited_shortcuts": [
                    "string similarity as proof of equivalence",
                    "silent namespace rewriting",
                    "mapping a case-specific method to a KPI label",
                ],
            })
    queue_path = ROOT / "canonical-reference-review-queue.jsonl"
    queue_path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in queue_records),
        encoding="utf-8",
    )
    if args.schemas:
        queue_schema = json.loads(
            (ROOT / "schema/canonical-reference-adjudication.schema.json").read_text()
        )
        queue_validator = jsonschema.Draft202012Validator(queue_schema)
        for record in queue_records:
            for error in queue_validator.iter_errors(record):
                errors.append(f"reference-queue:{record['queue_id']}: {error.message}")

    report = {
        "audit_id": "san.domain-atlas.industry-integration",
        "edition": 1,
        "status": "structurally_valid_research_not_compiler_ready" if not errors else "structural_errors",
        "pack_count": len(packs),
        "packs": packs,
        "totals": {
            "analytical_cases": sum(pack["cases"] for pack in packs),
            "sources": sum(pack["sources"] for pack in packs),
            "source_system_needs": sum(pack["source_system_needs"] for pack in packs),
            "data_shape_needs": sum(pack["data_shape_needs"] for pack in packs),
        },
        "canonical_reference_closure": {
            "distinct_method_refs": len(all_method_refs),
            "exact_canonical_method_refs": len(exact_methods),
            "unresolved_method_refs": len(unresolved_methods),
            "distinct_operation_refs": len(all_operation_refs),
            "exact_canonical_operation_refs": len(exact_operations),
            "unresolved_operation_refs": len(unresolved_operations),
            "unresolved_source_class_refs": len(unresolved_source_classes),
            "unresolved_industry_or_subindustry_refs": len(unresolved_industry_refs),
        },
        "collision_summary": {
            "record_id_collisions": len(id_collisions),
            "conflicting_record_id_collisions": len(conflicting_id_collisions),
            "duplicate_source_urls": len(duplicate_urls),
        },
        "review_queues": {
            "unresolved_method_refs": dict(sorted(unresolved_methods.items())),
            "unresolved_operation_refs": dict(sorted(unresolved_operations.items())),
            "unresolved_source_classes": dict(sorted(unresolved_source_classes.items())),
            "unresolved_industry_refs": dict(sorted(unresolved_industry_refs.items())),
            "record_id_collisions": id_collisions,
            "conflicting_record_id_collisions": conflicting_id_collisions,
            "duplicate_source_urls": duplicate_urls,
        },
        "compiler_ready": False,
        "canonical_reference_review_queue": queue_path.name,
        "canonical_reference_review_queue_records": len(queue_records),
        "blocking_reasons": [
            "vertical industry/subindustry references are not yet crosswalked to the classification foundation",
            "vertical method references are not yet bound to canonical analytical-practice identities",
            "vertical operation references are not yet bound to canonical typed-operation identities",
            "source-system needs are not yet fully bound to canonical source-system classes",
            "data-shape needs await the canonical data-type/shape universe",
            "cross-pack identity and evidence URL deduplication is not adjudicated",
            "no case has closed requirements/offers through libraries/providers to runtime evidence",
        ],
        "completion_claim": False,
    }
    (ROOT / "integration-audit.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if errors:
        error_limit = 50
        for error in errors[:error_limit]:
            print(f"ERROR: {error}")
        if len(errors) > error_limit:
            print(f"ERROR: ... {len(errors) - error_limit} additional structural errors are in integration-audit.json")
        return 1
    closure = report["canonical_reference_closure"]
    print(
        "PASS industry pack structure; compiler integration remains open: "
        f"{len(packs)} packs, {report['totals']['analytical_cases']} cases, "
        f"{closure['unresolved_method_refs']} method refs, "
        f"{closure['unresolved_operation_refs']} operation refs, "
        f"{closure['unresolved_source_class_refs']} source-class refs and "
        f"{closure['unresolved_industry_or_subindustry_refs']} industry refs need canonical binding"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
