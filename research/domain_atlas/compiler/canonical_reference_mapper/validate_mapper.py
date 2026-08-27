#!/usr/bin/env python3
"""Validate canonical-reference mapping artifacts and refusal gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
ATLAS = ROOT.parent.parent
INDUSTRIES = ATLAS / "industries"
QUEUE_PATH = INDUSTRIES / "canonical-reference-review-queue.jsonl"
sys.path.insert(0, str(ROOT))
import build_mapper as builder  # noqa: E402


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path}:{line_number}: record is not an object")
            records.append(record)
    return records


def duplicate_values(records: list[dict[str, Any]], field: str) -> list[str]:
    counts = Counter(record.get(field) for record in records)
    return sorted(str(value) for value, count in counts.items() if value is not None and count > 1)


def add_error(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def required_fields_validate(schema: dict[str, Any], record: dict[str, Any], label: str, errors: list[str]) -> None:
    for field in schema.get("required", []):
        if field not in record:
            errors.append(f"{label}: missing required field {field}")


def recursive_adjudicated(value: Any, location: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        if value.get("status") == "adjudicated":
            errors.append(f"{location}: prohibited adjudicated status")
        if value.get("adjudicated") is True:
            errors.append(f"{location}: prohibited adjudicated=true")
        for key, child in value.items():
            recursive_adjudicated(child, f"{location}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            recursive_adjudicated(child, f"{location}[{index}]", errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemas", action="store_true", help="also validate with jsonschema when installed")
    args = parser.parse_args()
    errors: list[str] = []

    files = {
        "occurrences": "source-occurrences.jsonl",
        "definitions": "source-definitions.jsonl",
        "candidates": "canonical-candidate-index.jsonl",
        "census": "universe-id-census.jsonl",
        "aliases": "alias-assertions.jsonl",
        "alignments": "namespace-alignments.jsonl",
        "mappings": "candidate-mappings.jsonl",
        "missing": "missing-concept-proposals.jsonl",
        "collisions": "collisions-homonyms.jsonl",
        "triage": "triage-records.jsonl",
        "batches": "review-batches.jsonl",
        "negatives": "negative-tests.jsonl",
    }
    data = {key: load_jsonl(ROOT / name) for key, name in files.items()}
    queue = load_jsonl(QUEUE_PATH)
    report = json.loads((ROOT / "coverage-report.json").read_text(encoding="utf-8"))
    report_jsonl = load_jsonl(ROOT / "coverage-report.jsonl")
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    # Basic identities and checked-in JSON Schemas.
    id_fields = {
        "occurrences": "occurrence_id", "definitions": "source_definition_id",
        "candidates": "candidate_id", "census": "identifier", "aliases": "assertion_id",
        "alignments": "alignment_id", "mappings": "mapping_id", "missing": "proposal_id",
        "collisions": "collision_id", "triage": "triage_id", "batches": "batch_id",
        "negatives": "test_id",
    }
    schema_names = {
        "occurrences": "source-occurrence.schema.json", "definitions": "source-definition.schema.json",
        "candidates": "canonical-candidate.schema.json", "census": "universe-id-census.schema.json",
        "aliases": "alias-assertion.schema.json", "alignments": "namespace-alignment.schema.json",
        "mappings": "candidate-mapping.schema.json", "missing": "missing-concept.schema.json",
        "collisions": "collision.schema.json", "triage": "triage-record.schema.json",
        "batches": "review-batch.schema.json", "negatives": "negative-test.schema.json",
    }
    jsonschema = None
    if args.schemas:
        try:
            import jsonschema as imported_jsonschema  # type: ignore
            jsonschema = imported_jsonschema
        except ImportError:
            errors.append("--schemas requested but jsonschema is not installed")
    for key, records in data.items():
        duplicates = duplicate_values(records, id_fields[key])
        add_error(errors, not duplicates, f"{files[key]} duplicate {id_fields[key]} values: {duplicates[:10]}")
        schema_path = ROOT / "schemas" / schema_names[key]
        add_error(errors, schema_path.exists(), f"missing schema {schema_path.name}")
        if not schema_path.exists():
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        for index, record in enumerate(records, 1):
            required_fields_validate(schema, record, f"{files[key]}:{index}", errors)
            if jsonschema:
                for error in jsonschema.Draft202012Validator(schema).iter_errors(record):
                    errors.append(f"{files[key]}:{index}: schema: {error.message}")
    coverage_schema = json.loads((ROOT / "schemas/coverage-report.schema.json").read_text())
    required_fields_validate(coverage_schema, report, "coverage-report.json", errors)
    if jsonschema:
        for error in jsonschema.Draft202012Validator(coverage_schema).iter_errors(report):
            errors.append(f"coverage-report.json: schema: {error.message}")

    # Queue preservation and exactly-once triage.
    queue_ids = [record["queue_id"] for record in queue]
    triage_queue_ids = [record["queue_id"] for record in data["triage"]]
    definition_queue_ids = [record["queue_id"] for record in data["definitions"]]
    add_error(errors, len(queue) == 4169, f"expected current queue size 4169, got {len(queue)}")
    add_error(errors, not duplicate_values(queue, "queue_id"), "input queue has duplicate queue IDs")
    add_error(errors, Counter(queue_ids) == Counter(triage_queue_ids), "triage does not represent every queue item exactly once")
    add_error(errors, Counter(queue_ids) == Counter(definition_queue_ids), "source definitions do not represent every queue item exactly once")
    queue_by_id = {record["queue_id"]: record for record in queue}
    for triage in data["triage"]:
        source = queue_by_id.get(triage["queue_id"])
        if not source:
            continue
        add_error(errors, triage["raw_ref"] == source["raw_ref"], f"{triage['queue_id']}: silent raw_ref rewrite")
        add_error(errors, triage["reference_domain"] == source["reference_domain"], f"{triage['queue_id']}: domain rewrite")
        add_error(errors, triage["queue_record_sha256"] == builder.digest(source), f"{triage['queue_id']}: queue digest mismatch")
        add_error(errors, triage["relation"] == "unresolved", f"{triage['queue_id']}: triage relation must remain unresolved")

    # Occurrences are re-derived from source files and checked without mutating them.
    occurrence_counts = Counter((row["reference_domain"], row["raw_ref"]) for row in data["occurrences"])
    expected_counts = {(row["reference_domain"], row["raw_ref"]): row["occurrence_count"] for row in queue}
    add_error(errors, occurrence_counts == expected_counts, "source-occurrence counts differ from the input queue")
    queue_by_key = {(row["reference_domain"], row["raw_ref"]): row for row in queue}
    source_file_cache: dict[str, dict[str, dict[str, Any]]] = {}
    for occurrence in data["occurrences"]:
        key = (occurrence["reference_domain"], occurrence["raw_ref"])
        add_error(errors, key in queue_by_key, f"{occurrence['occurrence_id']}: occurrence has no queue item")
        source_file = occurrence["source_file"]
        if source_file not in source_file_cache:
            source_file_cache[source_file] = {record["record_id"]: record for record in load_jsonl(ATLAS / source_file)}
        source_record = source_file_cache[source_file].get(occurrence["source_record_id"])
        if not source_record:
            errors.append(f"{occurrence['occurrence_id']}: source record missing")
            continue
        add_error(errors, builder.digest(source_record) == occurrence["source_record_sha256"], f"{occurrence['occurrence_id']}: source record digest mismatch")
        field = occurrence["source_field"]
        source_value = source_record.get(field)
        if isinstance(source_value, list):
            position = occurrence["source_position"]
            valid = position < len(source_value) and source_value[position] == occurrence["raw_ref"]
        else:
            valid = source_value == occurrence["raw_ref"]
        add_error(errors, valid, f"{occurrence['occurrence_id']}: source field no longer contains exact raw_ref")

    definition_counts = {record["queue_id"]: record["occurrence_count"] for record in data["definitions"]}
    for queue_id, source in queue_by_id.items():
        add_error(errors, definition_counts.get(queue_id) == source["occurrence_count"], f"{queue_id}: definition occurrence count mismatch")

    # Candidate existence, domain compatibility, evidence and review posture.
    candidate_by_id = {record["candidate_id"]: record for record in data["candidates"]}
    mapping_by_id = {record["mapping_id"]: record for record in data["mappings"]}
    occurrence_ids = {record["occurrence_id"] for record in data["occurrences"]}
    definition_ids = {record["source_definition_id"] for record in data["definitions"]}
    allowed_confidence = {"high", "medium", "low"}
    for mapping in data["mappings"]:
        source = queue_by_id.get(mapping["queue_id"])
        if not source:
            errors.append(f"{mapping['mapping_id']}: unknown queue ID")
            continue
        add_error(errors, mapping["raw_ref"] == source["raw_ref"], f"{mapping['mapping_id']}: raw_ref rewrite")
        add_error(errors, mapping["proposed_relation"] in builder.RELATIONS - {"missing_canonical_concept"}, f"{mapping['mapping_id']}: invalid relation")
        add_error(errors, mapping["confidence"] in allowed_confidence, f"{mapping['mapping_id']}: invalid confidence")
        add_error(errors, mapping["review_status"] == "manual_evidence_reviewed_independent_review_pending", f"{mapping['mapping_id']}: invalid review posture")
        add_error(errors, mapping["status"] == "proposed" and mapping["adjudicated"] is False, f"{mapping['mapping_id']}: proposal falsely adjudicated")
        add_error(errors, mapping["source_definition_ref"] in definition_ids, f"{mapping['mapping_id']}: missing source definition")
        target_evidence = []
        for target_ref in mapping["target_refs"]:
            target = candidate_by_id.get(target_ref)
            if not target:
                errors.append(f"{mapping['mapping_id']}: missing target {target_ref}")
                continue
            add_error(errors, target["canonical_domain"] == mapping["reference_domain"], f"{mapping['mapping_id']}: target crosses domain")
            target_evidence.extend(target["evidence_refs"])
        for occurrence_ref in mapping["evidence"]["source_occurrence_refs"]:
            add_error(errors, occurrence_ref in occurrence_ids, f"{mapping['mapping_id']}: missing evidence occurrence {occurrence_ref}")
        evidence_present = bool(mapping["evidence"]["source_evidence_refs"] or mapping["evidence"]["target_evidence_refs"] or target_evidence)
        add_error(errors, evidence_present, f"{mapping['mapping_id']}: mapping has no source or target evidence")

    # Manual seeds are the only semantic proposal authority.
    seed_pairs = set()
    for seed in builder.load_manual_seeds():
        key = (seed["reference_domain"], seed["raw_ref"])
        matching = [item for item in queue if (item["reference_domain"], item["raw_ref"]) == key]
        if len(matching) == 1:
            seed_pairs.add((matching[0]["queue_id"], tuple(seed["target_refs"])))
    output_pairs = {(row["queue_id"], tuple(row["target_refs"])) for row in data["mappings"]}
    add_error(errors, seed_pairs == output_pairs, "candidate mappings differ from checked-in manual seeds")

    # Mechanical namespace results cannot carry semantic force.
    for alignment in data["alignments"]:
        add_error(errors, alignment["candidate_target_ref"] in candidate_by_id, f"{alignment['alignment_id']}: unknown target")
        add_error(errors, alignment["semantic_effect"] == "none", f"{alignment['alignment_id']}: mechanical alignment has semantic effect")
        add_error(errors, alignment["proves_equivalence"] is False, f"{alignment['alignment_id']}: string match claims equivalence")
        source = queue_by_id.get(alignment["queue_id"])
        add_error(errors, bool(source) and source["raw_ref"] == alignment["raw_ref"], f"{alignment['alignment_id']}: alignment raw_ref rewrite")

    # Alias assertions must trace to an explicit alias field or a foundation crosswalk.
    crosswalk_by_id = {record["record_id"]: record for record in load_jsonl(INDUSTRIES / "foundation/crosswalks.jsonl")}
    for assertion in data["aliases"]:
        if assertion["assertion_kind"] == "declared_alias":
            target = candidate_by_id.get(assertion["target_ref"])
            add_error(errors, bool(target) and assertion["alias"] in target["aliases"], f"{assertion['assertion_id']}: alias was not explicitly declared")
        elif assertion["assertion_kind"] == "official_crosswalk_not_alias":
            crosswalk = crosswalk_by_id.get(assertion["crosswalk_ref"])
            add_error(errors, bool(crosswalk), f"{assertion['assertion_id']}: missing official crosswalk source")
            if crosswalk:
                add_error(errors, assertion["relation"] == crosswalk["relation"], f"{assertion['assertion_id']}: crosswalk relation changed")
        else:
            errors.append(f"{assertion['assertion_id']}: unrecognized alias assertion basis")

    # Missing concepts remain open, and every unresolved local industry identity is visible.
    missing_queue_ids = {record["queue_id"] for record in data["missing"]}
    industry_queue_ids = {record["queue_id"] for record in queue if record["reference_domain"] == "industry_classification"}
    add_error(errors, industry_queue_ids <= missing_queue_ids, "not every local industry identity has a visible missing/extension proposal")
    for proposal in data["missing"]:
        add_error(errors, proposal["proposed_relation"] == "missing_canonical_concept", f"{proposal['proposal_id']}: invalid missing relation")
        add_error(errors, proposal["status"] == "open" and proposal["adjudicated"] is False, f"{proposal['proposal_id']}: missing proposal not open")

    # Batches partition triage exactly once by primary pack.
    batched_queue_ids = [queue_id for batch in data["batches"] for queue_id in batch["queue_ids"]]
    add_error(errors, Counter(batched_queue_ids) == Counter(queue_ids), "review batches do not partition queue IDs exactly once")
    for batch in data["batches"]:
        add_error(errors, batch["queue_item_count"] == len(batch["queue_ids"]), f"{batch['batch_id']}: batch count mismatch")
        for mapping_id in batch["candidate_mapping_refs"]:
            add_error(errors, mapping_id in mapping_by_id, f"{batch['batch_id']}: unknown mapping {mapping_id}")

    # Universe census must contain every canonical candidate sourced from a universe.
    census_ids = {record["identifier"] for record in data["census"]}
    for candidate in data["candidates"]:
        if candidate["source_file"].startswith("universes/"):
            add_error(errors, candidate["candidate_id"] in census_ids, f"universe census misses canonical ID {candidate['candidate_id']}")

    # False-twin gates.  No equivalence is currently proposed, and named pairs remain refused.
    equivalent_pairs = {(row["raw_ref"], target) for row in data["mappings"] if row["proposed_relation"] == "equivalent" for target in row["target_refs"]}
    add_error(errors, not equivalent_pairs, "first pass must not assert equivalence")
    forbidden_pair = ("analytics.method.quarantined_llm_generation_with_tevv", "or.method.column_generation")
    all_pairs = {(row["raw_ref"], target) for row in data["mappings"] for target in row["target_refs"]}
    add_error(errors, forbidden_pair not in all_pairs, "false twin mapped: LLM generation -> column generation")
    required_negative_ids = {
        "negative.hospital_provider_vs_activity", "negative.state_estimation_homonym",
        "negative.simulation_vs_optimization", "negative.business_limit_vs_row_limit",
        "negative_source_vs_shape", "negative_vendor_vs_source_class", "negative_table_vs_relational_source",
        "negative_kpi_vs_practice", "negative_string_only_equivalence", "negative_cross_edition_rewrite",
        "negative_verb_optimize", "negative_llm_column_generation",
    }
    add_error(errors, required_negative_ids == {row["test_id"] for row in data["negatives"]}, "negative-test set is incomplete")

    # Coverage arithmetic and required vertical review focus.
    expected_by_domain = {}
    for domain in sorted({row["reference_domain"] for row in queue}):
        qids = {row["queue_id"] for row in queue if row["reference_domain"] == domain}
        mappings = [row for row in data["mappings"] if row["queue_id"] in qids]
        expected_by_domain[domain] = {
            "queue_items": len(qids),
            "occurrences": sum(row["occurrence_count"] for row in queue if row["queue_id"] in qids),
            "manual_reviewed_proposals": len(mappings),
            "queue_items_with_proposals": len({row["queue_id"] for row in mappings}),
            "open_triage_items": sum(row["status"] == "open" for row in data["triage"] if row["queue_id"] in qids),
            "relation_counts": dict(sorted(Counter(row["proposed_relation"] for row in mappings).items())),
            "confidence_counts": dict(sorted(Counter(row["confidence"] for row in mappings).items())),
        }
    add_error(errors, report["by_domain"] == expected_by_domain, "coverage by_domain arithmetic mismatch")
    expected_by_pack = {}
    for pack in sorted(builder.PACK_FOCUS):
        qids = {row["queue_id"] for row in queue if pack in row["origin_packs"]}
        mappings = [row for row in data["mappings"] if row["queue_id"] in qids]
        expected_by_pack[pack] = {
            "queue_memberships": len(qids),
            "occurrences": sum(row["origin_pack"] == pack for row in data["occurrences"]),
            "manual_reviewed_proposals": len(mappings),
            "queue_items_with_proposals": len({row["queue_id"] for row in mappings}),
            "open_queue_items": len(qids - {row["queue_id"] for row in mappings}),
        }
    add_error(errors, report["by_pack"] == expected_by_pack, "coverage by_pack arithmetic mismatch")
    required_focus = {"finance_ccr", "healthcare", "manufacturing", "logistics", "energy", "public", "commerce", "telecom_media_tech", "built_food_environment"}
    add_error(errors, required_focus <= set(report["by_review_focus"]), "manual proposals do not cover every required review focus")
    add_error(errors, len(data["mappings"]) >= 100, f"fewer than 100 manual evidence-reviewed proposals: {len(data['mappings'])}")
    add_error(errors, report["queue_items"] == len(queue) == len(data["triage"]), "coverage queue/triage count mismatch")
    add_error(errors, report["source_occurrences"] == len(data["occurrences"]), "coverage occurrence count mismatch")
    add_error(errors, report["manual_evidence_reviewed_proposals"] == len(data["mappings"]), "coverage proposal count mismatch")
    add_error(errors, report["adjudicated_status_count"] == 0, "coverage reports adjudicated records")
    add_error(errors, report["silent_rewrite_count"] == 0, "coverage reports silent rewrites")
    add_error(errors, report_jsonl == [report], "coverage JSON and JSONL differ")

    # No output record may claim adjudication.
    for key, records in data.items():
        recursive_adjudicated(records, files[key], errors)
    recursive_adjudicated(report, "coverage-report.json", errors)

    # Manifest integrity and input immutability receipt.
    queue_sha = hashlib.sha256(QUEUE_PATH.read_bytes()).hexdigest()
    add_error(errors, manifest["input_queue_sha256"] == queue_sha == report["input_queue_sha256"], "input queue digest mismatch")
    add_error(errors, manifest["input_queue_records"] == len(queue), "manifest queue count mismatch")
    add_error(errors, manifest["adjudication_performed"] is False, "manifest claims adjudication")
    add_error(errors, manifest["llm_runtime_dependency"] == "none", "manifest has an LLM runtime dependency")
    for relative, receipt in manifest["artifacts"].items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"manifest artifact missing: {relative}")
            continue
        payload = path.read_bytes()
        add_error(errors, hashlib.sha256(payload).hexdigest() == receipt["sha256"], f"manifest digest mismatch: {relative}")
        add_error(errors, len(payload) == receipt["bytes"], f"manifest byte count mismatch: {relative}")

    if errors:
        for error in errors[:100]:
            print(f"ERROR: {error}")
        if len(errors) > 100:
            print(f"ERROR: ... {len(errors) - 100} additional errors")
        return 1
    print(
        "PASS canonical-reference mapper: "
        f"{len(queue)} queue items exactly once; {len(data['occurrences'])} source occurrences; "
        f"{len(data['mappings'])} manual evidence-reviewed proposals; "
        f"{len(data['missing'])} first-class missing concepts; 0 silent rewrites; 0 adjudicated"
    )
    print("COUNTS by domain: " + json.dumps(report["by_domain"], sort_keys=True))
    print("COUNTS by pack: " + json.dumps(report["by_pack"], sort_keys=True))
    print("COUNTS by relation: " + json.dumps(report["by_relation"], sort_keys=True))
    print("COUNTS by confidence: " + json.dumps(report["by_confidence"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
