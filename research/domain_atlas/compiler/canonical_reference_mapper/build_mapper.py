#!/usr/bin/env python3
"""Build the loss-aware canonical-reference triage corpus.

The builder is deliberately deterministic and uses only the Python standard
library.  It never edits the industry queue, a vertical pack, or a universe.
Lexical retrieval is emitted as retrieval evidence only.  Semantic proposals
come exclusively from the checked-in manual proposal seeds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
ATLAS = ROOT.parent.parent
INDUSTRIES = ATLAS / "industries"
UNIVERSES = ATLAS / "universes"
QUEUE_PATH = INDUSTRIES / "canonical-reference-review-queue.jsonl"
AUTHORITY_EVIDENCE_PATH = ROOT / "authority-evidence.jsonl"
MANUAL_SEEDS_PATH = ROOT / "manual-proposal-seeds.json"

PACK_FOCUS = {
    "finance_insurance": "finance",
    "health_life_sciences": "healthcare",
    "manufacturing_industrial": "manufacturing",
    "transport_logistics": "logistics",
    "energy_resources": "energy",
    "public_education": "public",
    "commerce_services": "commerce",
    "telecom_media_tech": "telecom_media_tech",
    "built_food_environment": "built_food_environment",
}

RELATIONS = {
    "equivalent",
    "narrower",
    "broader",
    "overlap",
    "disjoint",
    "missing_canonical_concept",
}

CANONICAL_SPECS = [
    ("industry_classification", "industry_taxonomy_node", INDUSTRIES / "foundation/isic-rev5.nodes.jsonl", "record_id", "title"),
    ("analytical_practice", "analytical_practice", UNIVERSES / "analytics_types/candidate-practices.jsonl", "practice_id", "name"),
    ("analytical_practice", "method_family", UNIVERSES / "method_kernels/method-families.jsonl", "method_family_id", "name"),
    ("analytical_practice", "method_implementation", UNIVERSES / "method_kernels/implementation-records.jsonl", "record_id", "name"),
    ("analytical_practice", "operations_research_method", UNIVERSES / "operations_research/methods.jsonl", "method_id", "name"),
    ("typed_operation", "typed_operation", UNIVERSES / "operations/operation-candidates.jsonl", "operation_id", "name"),
    ("source_system_class", "source_system_class", UNIVERSES / "source_systems/source-classes.jsonl", "class_id", "name"),
    ("data_shape", "data_shape", UNIVERSES / "data_shapes/shape-records.jsonl", "shape_id", "name"),
    ("data_type", "data_type", UNIVERSES / "data_shapes/type-records.jsonl", "type_id", "name"),
]

IDENTITY_FIELDS = {
    "record_id", "practice_id", "method_family_id", "method_id", "operation_id",
    "class_id", "shape_id", "type_id", "context_id", "capability_id", "gap_id",
    "source_id", "evidence_id", "decision_id", "innovation_id", "family_id",
    "requirement_id", "offer_id", "binding_id", "contract_id", "entity_type_id",
    "relation_type_id", "library_id", "provider_id", "profile_id", "rule_id",
}

REFERENCE_FIELDS = {
    "refs", "ids", "parent", "parents", "owner", "source", "target", "evidence",
    "requires", "offers", "members", "contexts", "operations", "methods", "practices",
}

SCHEMAS: dict[str, dict[str, Any]] = {}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    if isinstance(value, bytes):
        payload = value
    elif isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def stable_id(prefix: str, *parts: str) -> str:
    return f"{prefix}.{digest(chr(31).join(parts))[:20]}"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: JSONL record is not an object")
            records.append(value)
    return records


def load_authority_evidence() -> list[dict[str, Any]]:
    """Load the checked-in primary/official evidence ledger used by proposals."""
    records = load_jsonl(AUTHORITY_EVIDENCE_PATH)
    seen: set[str] = set()
    for record in records:
        authority_id = record.get("authority_id")
        if not isinstance(authority_id, str) or not authority_id:
            raise ValueError("authority evidence requires a non-empty authority_id")
        if authority_id in seen:
            raise ValueError(f"duplicate authority evidence ID: {authority_id}")
        seen.add(authority_id)
    return sorted(records, key=lambda record: record["authority_id"])


def jsonl_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records).encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def normalize_label(value: str, strip_namespace: bool = True) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("_", " ").replace("-", " ").replace(".", " ")
    tokens = re.findall(r"[a-z0-9]+", value)
    if strip_namespace:
        while tokens and tokens[0] in {"method", "analytics", "operation", "op"}:
            tokens.pop(0)
    return " ".join(tokens)


def label_tokens(value: str) -> set[str]:
    stop = {"a", "an", "and", "for", "from", "in", "of", "or", "the", "to", "under", "with"}
    return {token for token in normalize_label(value).split() if token not in stop}


def target_contract(record: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "assumptions", "input_contracts", "output_contracts", "uncertainty_contract",
        "evaluation_contract", "distinctiveness_basis", "laws", "preconditions",
        "postconditions", "failures", "refusals", "totality", "information_loss",
        "authority", "order_finality", "temporality", "transactions", "hazards",
        "classification_rule", "constraints", "invalid_operations", "valid_operations",
        "time_semantics", "change_semantics", "topology", "guarantees", "runtime_budget",
        "scheme_code", "level", "parent_id", "assignment_basis",
    )
    return {field: record[field] for field in fields if field in record}


def canonical_candidates() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for domain, kind, path, id_field, name_field in CANONICAL_SPECS:
        for record in load_jsonl(path):
            candidate_id = record[id_field]
            if candidate_id in seen:
                raise ValueError(f"duplicate canonical ID {candidate_id} in {path} and {seen[candidate_id]}")
            seen[candidate_id] = str(path)
            evidence_refs = record.get("evidence_refs", record.get("source_refs", []))
            aliases = record.get("aliases", [])
            if not isinstance(aliases, list):
                aliases = []
            contract = target_contract(record)
            result.append({
                "record_kind": "canonical_candidate",
                "candidate_id": candidate_id,
                "canonical_domain": domain,
                "concept_kind": kind,
                "name": record[name_field],
                "definition": record.get("definition", record.get("assignment_basis", record[name_field])),
                "aliases": aliases,
                "status": record.get("status", "unspecified"),
                "semantic_contract": contract,
                "semantic_contract_sha256": digest(contract),
                "evidence_refs": sorted(set(evidence_refs)),
                "source_file": path.relative_to(ATLAS).as_posix(),
                "source_record_sha256": digest(record),
                "candidate_only_not_adjudicated": True,
            })
    return sorted(result, key=lambda r: r["candidate_id"])


def iter_json_values(path: Path) -> Iterable[tuple[str, Any]]:
    if path.suffix == ".jsonl":
        for number, record in enumerate(load_jsonl(path), 1):
            yield f"line[{number}]", record
    elif path.suffix == ".json":
        yield "$", json.loads(path.read_text(encoding="utf-8"))


def universe_id_census() -> list[dict[str, Any]]:
    occurrences: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"declaration_files": set(), "reference_files": set(), "field_names": set(), "count": 0}
    )
    id_pattern = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)+$")

    def walk(value: Any, key: str, location: str, path: Path) -> None:
        if isinstance(value, dict):
            for child_key, child in value.items():
                walk(child, child_key, f"{location}.{child_key}", path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, key, f"{location}[{index}]", path)
        elif isinstance(value, str) and id_pattern.match(value):
            key_lower = key.casefold()
            relevant = (
                key_lower in IDENTITY_FIELDS
                or key_lower.endswith(("_id", "_ids", "_ref", "_refs"))
                or any(token in key_lower.split("_") for token in REFERENCE_FIELDS)
            )
            if relevant:
                role = "identity_declaration" if key_lower in IDENTITY_FIELDS else "reference_occurrence"
                bucket = occurrences[value]
                source_file = path.relative_to(ATLAS).as_posix()
                bucket["declaration_files" if role == "identity_declaration" else "reference_files"].add(source_file)
                bucket["field_names"].add(key)
                bucket["count"] += 1

    for path in sorted(UNIVERSES.rglob("*")):
        if path.suffix not in {".json", ".jsonl"} or "__pycache__" in path.parts:
            continue
        for location, value in iter_json_values(path):
            walk(value, "", location, path)
    result = []
    for identifier, bucket in sorted(occurrences.items()):
        result.append({
            "record_kind": "universe_id_census",
            "identifier": identifier,
            "declaration_seen": bool(bucket["declaration_files"]),
            "declaration_files": sorted(bucket["declaration_files"]),
            "reference_files": sorted(bucket["reference_files"]),
            "field_names": sorted(bucket["field_names"]),
            "occurrence_count": bucket["count"],
        })
    return result


def pack_dirs() -> list[Path]:
    required = ("analytics-cases.jsonl", "source-systems.jsonl", "data-shapes.jsonl", "sources.jsonl")
    return sorted(path for path in INDUSTRIES.iterdir() if path.is_dir() and all((path / name).exists() for name in required))


def context_snapshot(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("record_kind") == "analytical_case":
        fields = (
            "name", "sovereign_question", "decision_or_action", "unit_of_analysis",
            "grain", "industry_id", "subindustry_ids", "evidence_refs", "llm_dependency",
        )
    else:
        fields = (
            "source_class", "objects", "read_change_modes", "time_order_finality", "schema_semantics",
            "authority", "hazards", "industry_id", "subindustry_ids", "evidence_refs",
        )
    return {field: record.get(field) for field in fields if field in record}


def source_occurrences() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add(domain: str, raw_ref: str, pack: str, source_file: Path, record: dict[str, Any], field: str, position: int) -> None:
        occurrence_id = stable_id("refocc", domain, raw_ref, pack, record["record_id"], field, str(position))
        rows.append({
            "record_kind": "canonical_reference_source_occurrence",
            "occurrence_id": occurrence_id,
            "reference_domain": domain,
            "raw_ref": raw_ref,
            "origin_pack": pack,
            "source_file": source_file.relative_to(ATLAS).as_posix(),
            "source_record_id": record["record_id"],
            "source_field": field,
            "source_position": position,
            "source_record_sha256": digest(record),
            "context": context_snapshot(record),
            "semantic_status": "source_context_only_not_adjudicated",
        })

    for pack_dir in pack_dirs():
        pack = pack_dir.name
        case_path = pack_dir / "analytics-cases.jsonl"
        for record in load_jsonl(case_path):
            for field, domain in (
                ("method_refs", "analytical_practice"),
                ("operation_refs", "typed_operation"),
                ("subindustry_ids", "industry_classification"),
            ):
                for position, raw_ref in enumerate(record.get(field, [])):
                    add(domain, raw_ref, pack, case_path, record, field, position)
            raw_industry = record.get("industry_id")
            if raw_industry:
                add("industry_classification", raw_industry, pack, case_path, record, "industry_id", 0)
        system_path = pack_dir / "source-systems.jsonl"
        for record in load_jsonl(system_path):
            raw_ref = record.get("source_class") or "<missing>"
            add("source_system_class", raw_ref, pack, system_path, record, "source_class", 0)
    return sorted(rows, key=lambda r: (r["reference_domain"], r["raw_ref"], r["origin_pack"], r["source_record_id"], r["source_position"]))


def source_definitions(queue: list[dict[str, Any]], occurrences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for occurrence in occurrences:
        by_key[(occurrence["reference_domain"], occurrence["raw_ref"])].append(occurrence)
    scope_notes = {
        "analytical_practice": "Meaning is bounded by the source cases' questions, decisions, populations, grains, assumptions and evidence; the label alone is not a portable practice definition.",
        "typed_operation": "Meaning is bounded by the source cases' input, result, invariant and failure contracts; the verb alone is not a typed operation.",
        "source_system_class": "Meaning is bounded by objects, authority, read/change, schema, time/finality and hazards; a product-shaped phrase is not itself a provider-neutral class.",
        "industry_classification": "Meaning is a vertical scope occurrence, not an edition-qualified economic-activity identity; an explicit crosswalk or extension registration is required.",
    }
    result = []
    for item in sorted(queue, key=lambda r: r["queue_id"]):
        source_rows = by_key[(item["reference_domain"], item["raw_ref"])]
        evidence_refs = sorted({ref for row in source_rows for ref in row["context"].get("evidence_refs", [])})
        context_digests = sorted({digest(row["context"]) for row in source_rows})
        result.append({
            "record_kind": "canonical_reference_source_definition",
            "source_definition_id": stable_id("refdef", item["queue_id"]),
            "queue_id": item["queue_id"],
            "reference_domain": item["reference_domain"],
            "raw_ref": item["raw_ref"],
            "occurrence_count": len(source_rows),
            "origin_packs": sorted({row["origin_pack"] for row in source_rows}),
            "source_record_ids": sorted({row["source_record_id"] for row in source_rows}),
            "context_sha256s": context_digests,
            "evidence_refs": evidence_refs,
            "scope_note": scope_notes[item["reference_domain"]],
            "definition_status": "contextual_evidence_extracted_not_semantically_adjudicated",
        })
    return result


def compatible_candidates(domain: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [candidate for candidate in candidates if candidate["canonical_domain"] == domain]


def retrieval_score(raw: str, candidate: dict[str, Any]) -> float:
    raw_tokens = label_tokens(raw)
    best = 0.0
    for label in [candidate["name"], *candidate["aliases"]]:
        target_tokens = label_tokens(label)
        if not raw_tokens or not target_tokens:
            continue
        overlap = len(raw_tokens & target_tokens)
        if not overlap:
            continue
        score = 0.65 * overlap / len(raw_tokens) + 0.35 * overlap / len(raw_tokens | target_tokens)
        if normalize_label(raw) == normalize_label(label):
            score = 1.0
        best = max(best, score)
    return round(best, 6)


def namespace_alignments(queue: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for item in queue:
        for candidate in compatible_candidates(item["reference_domain"], candidates):
            labels = [(candidate["name"], "canonical_name"), *((alias, "declared_alias") for alias in candidate["aliases"])]
            for label, basis in labels:
                if normalize_label(item["raw_ref"]) == normalize_label(label):
                    result.append({
                        "record_kind": "mechanical_namespace_alignment",
                        "alignment_id": stable_id("refalign", item["queue_id"], candidate["candidate_id"], basis, label),
                        "queue_id": item["queue_id"],
                        "raw_ref": item["raw_ref"],
                        "candidate_target_ref": candidate["candidate_id"],
                        "matched_label": label,
                        "basis": basis,
                        "normalization": "NFKC+casefold+separator-tokenization+leading-local-namespace-removal",
                        "semantic_effect": "none",
                        "proves_equivalence": False,
                        "status": "retrieval_only",
                    })
    return sorted(result, key=lambda r: r["alignment_id"])


def alias_assertions(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for candidate in candidates:
        for alias in candidate["aliases"]:
            result.append({
                "record_kind": "canonical_alias_assertion",
                "assertion_id": stable_id("refalias", candidate["candidate_id"], alias),
                "assertion_kind": "declared_alias",
                "alias": alias,
                "target_ref": candidate["candidate_id"],
                "declared_in": candidate["source_file"],
                "evidence_refs": candidate["evidence_refs"],
                "status": "inherited_declared_assertion_not_mapper_adjudication",
            })
    for crosswalk in load_jsonl(INDUSTRIES / "foundation/crosswalks.jsonl"):
        result.append({
            "record_kind": "canonical_alias_assertion",
            "assertion_id": stable_id("refalias", crosswalk["record_id"]),
            "assertion_kind": "official_crosswalk_not_alias",
            "crosswalk_ref": crosswalk["record_id"],
            "source_members": crosswalk["source_members"],
            "target_members": crosswalk["target_members"],
            "relation": crosswalk["relation"],
            "evidence_refs": crosswalk["evidence_refs"],
            "losses": crosswalk["losses"],
            "status": "inherited_official_crosswalk_not_mapper_adjudication",
        })
    return sorted(result, key=lambda r: r["assertion_id"])


def load_manual_seeds() -> list[dict[str, Any]]:
    value = json.loads((ROOT / "manual-proposal-seeds.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("manual-proposal-seeds.json must contain an object")
    seeds: list[dict[str, Any]] = []
    for domain, entries in sorted(value.get("contextual_exact", {}).items()):
        for raw_ref, target_ref in sorted(entries.items()):
            seeds.append({
                "reference_domain": domain,
                "raw_ref": raw_ref,
                "target_refs": [target_ref],
                "relation": "narrower",
                "confidence": "medium",
                "mapping_semantics": "reviewed_contextual_use_to_same_named_portable_contract",
            })
    seeds.extend(value.get("semantic_proposals", []))
    return seeds


def mapping_rationale(seed: dict[str, Any], source: dict[str, Any], targets: list[dict[str, Any]]) -> str:
    if seed.get("rationale"):
        return seed["rationale"]
    target_names = ", ".join(target["name"] for target in targets)
    return (
        f"The extracted vertical contexts use '{source['raw_ref']}' as a situated reference. "
        f"The reviewed target definition(s)—{target_names}—make the portable family reviewable, "
        "while the vertical question, actors, grain, policy and evidence remain owned by the source cases."
    )


def candidate_mappings(
    queue: list[dict[str, Any]],
    definitions: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    occurrences: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    queue_by_raw = defaultdict(list)
    for item in queue:
        queue_by_raw[(item["reference_domain"], item["raw_ref"])].append(item)
    def_by_queue = {record["queue_id"]: record for record in definitions}
    candidate_by_id = {record["candidate_id"]: record for record in candidates}
    occ_by_key = defaultdict(list)
    for occurrence in occurrences:
        occ_by_key[(occurrence["reference_domain"], occurrence["raw_ref"])].append(occurrence)
    authority_by_id = {record["authority_id"]: record for record in load_authority_evidence()}
    result = []
    seen_sources: set[tuple[str, tuple[str, ...]]] = set()
    for seed in load_manual_seeds():
        key = (seed["reference_domain"], seed["raw_ref"])
        items = queue_by_raw.get(key, [])
        if len(items) != 1:
            raise ValueError(f"manual seed must resolve to exactly one queue item: {key}, got {len(items)}")
        item = items[0]
        target_ids = tuple(seed["target_refs"])
        if (item["queue_id"], target_ids) in seen_sources:
            raise ValueError(f"duplicate manual proposal seed for {item['queue_id']} -> {target_ids}")
        seen_sources.add((item["queue_id"], target_ids))
        targets = []
        for target_id in target_ids:
            if target_id not in candidate_by_id:
                raise ValueError(f"manual seed target does not exist: {target_id}")
            target = candidate_by_id[target_id]
            if target["canonical_domain"] != item["reference_domain"]:
                raise ValueError(f"manual seed crosses incompatible domains: {item['queue_id']} -> {target_id}")
            targets.append(target)
        relation = seed.get("relation", "narrower")
        if relation not in RELATIONS - {"missing_canonical_concept"}:
            raise ValueError(f"invalid mapping relation {relation}")
        source_definition = def_by_queue[item["queue_id"]]
        source_rows = occ_by_key[key]
        source_evidence = source_definition["evidence_refs"]
        target_evidence = sorted({ref for target in targets for ref in target["evidence_refs"]})
        authority_evidence_refs = sorted(set(seed.get("authority_evidence_refs", [])))
        unknown_authority_refs = set(authority_evidence_refs) - set(authority_by_id)
        if unknown_authority_refs:
            raise ValueError(
                f"manual seed references unknown authority evidence: {item['raw_ref']} -> "
                f"{sorted(unknown_authority_refs)}"
            )
        focus = {PACK_FOCUS[pack] for pack in item["origin_packs"]}
        if any("banking.ccr" in row["context"].get("subindustry_ids", []) for row in source_rows):
            focus.add("finance_ccr")
        result.append({
            "record_kind": "canonical_candidate_mapping",
            "mapping_id": stable_id("refmap", item["queue_id"], *target_ids, relation),
            "queue_id": item["queue_id"],
            "source_definition_ref": source_definition["source_definition_id"],
            "reference_domain": item["reference_domain"],
            "raw_ref": item["raw_ref"],
            "target_refs": list(target_ids),
            "proposed_relation": relation,
            "cardinality": "one_to_many" if len(target_ids) > 1 else "one_to_one",
            "mapping_semantics": seed.get("mapping_semantics", "vertical_context_to_portable_family"),
            "rationale": mapping_rationale(seed, source_definition, targets),
            "information_loss": seed.get("information_loss", [
                "The canonical target does not replace vertical actors, decisions, grain, thresholds, policy or case evidence.",
                "Algorithm, parameterization, study design and runtime qualification remain separate bindings unless explicitly named.",
            ]),
            "uncertainties": seed.get("uncertainties", [
                "The target is itself a candidate record and has not been globally adjudicated.",
                "Independent domain review must confirm the relation against every materially distinct source context.",
            ]),
            "evidence": {
                "source_occurrence_refs": [row["occurrence_id"] for row in source_rows],
                "source_evidence_refs": source_evidence,
                "target_evidence_refs": target_evidence,
                "authority_evidence_refs": authority_evidence_refs,
                "target_source_files": sorted({target["source_file"] for target in targets}),
                "target_contract_sha256s": [target["semantic_contract_sha256"] for target in targets],
            },
            "confidence": seed.get("confidence", "medium"),
            "review_focus": sorted(focus),
            "review_status": "manual_evidence_reviewed_independent_review_pending",
            "status": "proposed",
            "adjudicated": False,
        })
    return sorted(result, key=lambda r: r["mapping_id"])


def missing_concepts(
    queue: list[dict[str, Any]],
    definitions: list[dict[str, Any]],
    alignments: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    def_by_queue = {record["queue_id"]: record for record in definitions}
    mapped_targets = defaultdict(list)
    for mapping in mappings:
        mapped_targets[mapping["queue_id"]].extend(mapping["target_refs"])
    alignment_targets = defaultdict(list)
    for alignment in alignments:
        alignment_targets[alignment["queue_id"]].append(alignment["candidate_target_ref"])
    explicit = set(json.loads((ROOT / "manual-missing-concept-seeds.json").read_text(encoding="utf-8")))
    result = []
    for item in queue:
        is_vertical_extension = item["reference_domain"] == "industry_classification"
        is_explicit = item["raw_ref"] in explicit
        if not (is_vertical_extension or is_explicit):
            continue
        definition = def_by_queue[item["queue_id"]]
        slug = re.sub(r"[^a-z0-9]+", "_", normalize_label(item["raw_ref"])).strip("_")[:80]
        result.append({
            "record_kind": "missing_canonical_concept_proposal",
            "proposal_id": stable_id("refgap", item["queue_id"]),
            "queue_id": item["queue_id"],
            "reference_domain": item["reference_domain"],
            "raw_ref": item["raw_ref"],
            "proposed_relation": "missing_canonical_concept",
            "provisional_concept_key": f"proposed.{item['reference_domain']}.{slug}",
            "proposal_kind": "vertical_extension_registration" if is_vertical_extension else "canonical_universe_gap",
            "why_not_silent_rewrite": "No exact edition-qualified canonical identity or evidence-bearing equivalence is asserted by this pass.",
            "preserved_broader_candidate_refs": sorted(set(mapped_targets[item["queue_id"]] + alignment_targets[item["queue_id"]])),
            "source_definition_ref": definition["source_definition_id"],
            "evidence_refs": definition["evidence_refs"],
            "uncertainties": [
                "The concept may ultimately be registered as a vertical extension, decomposed, mapped lossily, or rejected.",
                "A missing-concept proposal does not establish a new canonical identity.",
            ],
            "status": "open",
            "adjudicated": False,
        })
    return sorted(result, key=lambda r: r["proposal_id"])


def collisions(queue: list[dict[str, Any]], candidates: list[dict[str, Any]], alignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    raw_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in queue:
        raw_groups[(item["reference_domain"], normalize_label(item["raw_ref"]))].append(item)
    for (domain, normalized), items in sorted(raw_groups.items()):
        raw_forms = sorted({item["raw_ref"] for item in items})
        if len(raw_forms) > 1:
            result.append({
                "record_kind": "canonical_reference_collision",
                "collision_id": stable_id("refcollision", "raw_normalization", domain, normalized),
                "collision_kind": "raw_normalization_collision",
                "reference_domain": domain,
                "normalized_label": normalized,
                "raw_refs": raw_forms,
                "queue_ids": sorted(item["queue_id"] for item in items),
                "risk": "Normalization would silently merge distinct source spellings and possibly distinct meanings.",
                "required_action": "Review source definitions before any merge or alias assertion.",
                "status": "open",
            })
    candidate_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        candidate_groups[(candidate["canonical_domain"], normalize_label(candidate["name"]))].append(candidate)
    for (domain, normalized), items in sorted(candidate_groups.items()):
        if len(items) > 1:
            result.append({
                "record_kind": "canonical_reference_collision",
                "collision_id": stable_id("refcollision", "canonical_homonym", domain, normalized),
                "collision_kind": "canonical_homonym_or_layer_collision",
                "reference_domain": domain,
                "normalized_label": normalized,
                "candidate_target_refs": sorted(item["candidate_id"] for item in items),
                "concept_kinds": sorted({item["concept_kind"] for item in items}),
                "risk": "A shared label does not establish shared laws, ownership layer or equivalence.",
                "required_action": "Compare definitions, contracts and intended layer; keep false twins distinct.",
                "status": "open",
            })
    by_queue = defaultdict(set)
    for alignment in alignments:
        by_queue[alignment["queue_id"]].add(alignment["candidate_target_ref"])
    for queue_id, target_refs in sorted(by_queue.items()):
        if len(target_refs) > 1:
            item = next(record for record in queue if record["queue_id"] == queue_id)
            result.append({
                "record_kind": "canonical_reference_collision",
                "collision_id": stable_id("refcollision", "ambiguous_alignment", queue_id),
                "collision_kind": "ambiguous_mechanical_alignment",
                "reference_domain": item["reference_domain"],
                "normalized_label": normalize_label(item["raw_ref"]),
                "raw_refs": [item["raw_ref"]],
                "queue_ids": [queue_id],
                "candidate_target_refs": sorted(target_refs),
                "risk": "The same mechanically aligned label resolves to more than one canonical candidate.",
                "required_action": "Use source meaning and target laws; do not choose by string score.",
                "status": "open",
            })
    return sorted(result, key=lambda r: r["collision_id"])


def triage_records(
    queue: list[dict[str, Any]],
    definitions: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
    missing: list[dict[str, Any]],
    alignments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    def_by_queue = {record["queue_id"]: record for record in definitions}
    mappings_by_queue = defaultdict(list)
    for mapping in mappings:
        mappings_by_queue[mapping["queue_id"]].append(mapping)
    missing_by_queue = defaultdict(list)
    for proposal in missing:
        missing_by_queue[proposal["queue_id"]].append(proposal)
    aligns_by_queue = defaultdict(list)
    for alignment in alignments:
        aligns_by_queue[alignment["queue_id"]].append(alignment)
    compatible = {domain: compatible_candidates(domain, candidates) for domain in {q["reference_domain"] for q in queue}}
    result = []
    for item in sorted(queue, key=lambda r: r["queue_id"]):
        retrieved = []
        for candidate in compatible[item["reference_domain"]]:
            score = retrieval_score(item["raw_ref"], candidate)
            if score >= 0.15:
                retrieved.append((score, candidate["candidate_id"]))
        retrieved.sort(key=lambda row: (-row[0], row[1]))
        semantic_mappings = mappings_by_queue[item["queue_id"]]
        gaps = missing_by_queue[item["queue_id"]]
        disposition = "semantic_candidate_proposed" if semantic_mappings else "open_semantic_triage"
        if gaps and not semantic_mappings:
            disposition = "open_missing_concept_review"
        result.append({
            "record_kind": "canonical_reference_triage",
            "triage_id": stable_id("reftriage", item["queue_id"]),
            "queue_id": item["queue_id"],
            "queue_record_sha256": digest(item),
            "reference_domain": item["reference_domain"],
            "raw_ref": item["raw_ref"],
            "occurrence_count": item["occurrence_count"],
            "origin_packs": item["origin_packs"],
            "source_definition_ref": def_by_queue[item["queue_id"]]["source_definition_id"],
            "mechanical_alignment_refs": [row["alignment_id"] for row in aligns_by_queue[item["queue_id"]]],
            "lexical_retrieval": [
                {"candidate_target_ref": target_id, "score": score, "semantic_evidence": False}
                for score, target_id in retrieved[:5]
            ],
            "candidate_mapping_refs": [row["mapping_id"] for row in semantic_mappings],
            "missing_concept_proposal_refs": [row["proposal_id"] for row in gaps],
            "disposition": disposition,
            "relation": "unresolved",
            "status": "proposed" if semantic_mappings else "open",
            "adjudicated": False,
            "next_review": "independent semantic review" if semantic_mappings else "definition and law comparison",
        })
    return result


def review_batches(triage: list[dict[str, Any]], mappings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mapping_by_id = {record["mapping_id"]: record for record in mappings}
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in triage:
        primary_pack = sorted(record["origin_packs"])[0]
        lane = "proposal_review" if record["candidate_mapping_refs"] else "open_research"
        groups[(primary_pack, record["reference_domain"], lane)].append(record)
    result = []
    for (pack, domain, lane), members in sorted(groups.items()):
        mapping_ids = sorted({mapping_id for member in members for mapping_id in member["candidate_mapping_refs"]})
        focus = sorted({focus for mapping_id in mapping_ids for focus in mapping_by_id[mapping_id]["review_focus"]})
        result.append({
            "record_kind": "canonical_reference_review_batch",
            "batch_id": f"refbatch.{pack}.{domain}.{lane}",
            "primary_pack": pack,
            "reference_domain": domain,
            "lane": lane,
            "queue_ids": [member["queue_id"] for member in sorted(members, key=lambda r: (-r["occurrence_count"], r["queue_id"]))],
            "queue_item_count": len(members),
            "occurrence_count": sum(member["occurrence_count"] for member in members),
            "candidate_mapping_refs": mapping_ids,
            "review_focus": focus,
            "priority": "high" if lane == "proposal_review" or sum(member["occurrence_count"] for member in members) >= 100 else "normal",
            "review_protocol": "reviewer-protocol.md",
            "status": "open",
        })
    return result


def negative_tests() -> list[dict[str, Any]]:
    return [
        {"test_id": "negative.hospital_provider_vs_activity", "left": "SHA hospital provider type", "right": "industry.isic5.class.c8610", "forbidden_relation": "equivalent", "reason": "Provider classification and economic activity are orthogonal axes."},
        {"test_id": "negative.state_estimation_homonym", "left": "state estimation", "right": "analytics.signal_sensor.state_estimation|analytics.control_feedback.state_estimation", "forbidden_relation": "automatic_equivalent", "reason": "Signal-estimation and control-feedback ownership/laws require contextual review."},
        {"test_id": "negative.simulation_vs_optimization", "left": "simulation", "right": "optimization", "forbidden_relation": "equivalent", "reason": "Simulation evaluates a declared model; it does not prove an optimum."},
        {"test_id": "negative.business_limit_vs_row_limit", "left": "operation.evaluate-limit-authorize-and-receipt", "right": "operation.relational_algebra.limit_records", "forbidden_relation": "equivalent", "reason": "A policy/authority limit is not row truncation."},
        {"test_id": "negative_source_vs_shape", "left": "electronic health record", "right": "shape.longitudinal_cohort", "forbidden_relation": "equivalent", "reason": "A source capability is not a provider-neutral data shape."},
        {"test_id": "negative_vendor_vs_source_class", "left": "vendor product", "right": "source capability class", "forbidden_relation": "equivalent", "reason": "A deployment may expose multiple source-class surfaces."},
        {"test_id": "negative_table_vs_relational_source", "left": "table", "right": "source.operational_database.relational_transactional", "forbidden_relation": "equivalent", "reason": "A shape does not imply a transactional source authority."},
        {"test_id": "negative_kpi_vs_practice", "left": "KPI label", "right": "analytical practice", "forbidden_relation": "equivalent", "reason": "A metric cannot replace intent, study, uncertainty and evidence contracts."},
        {"test_id": "negative_string_only_equivalence", "left": "normalized equal label", "right": "canonical candidate", "forbidden_relation": "automatic_equivalent", "reason": "String equality is retrieval evidence only."},
        {"test_id": "negative_cross_edition_rewrite", "left": "unqualified industry code", "right": "industry.isic5.*", "forbidden_relation": "silent_rewrite", "reason": "Industry identities are edition-qualified and need a crosswalk."},
        {"test_id": "negative_verb_optimize", "left": "operation.optimize", "right": "any operation.optimization_simulation.*", "forbidden_relation": "automatic_equivalent", "reason": "An untyped verb does not establish inputs, result algebra, budgets or failure laws."},
        {"test_id": "negative_llm_column_generation", "left": "analytics.method.quarantined_llm_generation_with_tevv", "right": "or.method.column_generation", "forbidden_relation": "equivalent", "reason": "Shared word 'generation' is a false lexical twin; LLM semantics are outside the core."},
    ]


def coverage_report(
    queue: list[dict[str, Any]], occurrences: list[dict[str, Any]], definitions: list[dict[str, Any]],
    candidates: list[dict[str, Any]], census: list[dict[str, Any]], alignments: list[dict[str, Any]],
    aliases: list[dict[str, Any]], mappings: list[dict[str, Any]], missing: list[dict[str, Any]],
    collisions_rows: list[dict[str, Any]], triage: list[dict[str, Any]], batches: list[dict[str, Any]],
    authority_records: list[dict[str, Any]],
) -> dict[str, Any]:
    by_domain: dict[str, Any] = {}
    for domain in sorted({item["reference_domain"] for item in queue}):
        qids = {item["queue_id"] for item in queue if item["reference_domain"] == domain}
        domain_mappings = [row for row in mappings if row["queue_id"] in qids]
        domain_triage = [row for row in triage if row["queue_id"] in qids]
        by_domain[domain] = {
            "queue_items": len(qids),
            "occurrences": sum(item["occurrence_count"] for item in queue if item["queue_id"] in qids),
            "manual_reviewed_proposals": len(domain_mappings),
            "queue_items_with_proposals": len({row["queue_id"] for row in domain_mappings}),
            "open_triage_items": sum(row["status"] == "open" for row in domain_triage),
            "relation_counts": dict(sorted(Counter(row["proposed_relation"] for row in domain_mappings).items())),
            "confidence_counts": dict(sorted(Counter(row["confidence"] for row in domain_mappings).items())),
        }
    by_pack = {}
    for pack in sorted(PACK_FOCUS):
        qids = {item["queue_id"] for item in queue if pack in item["origin_packs"]}
        pack_mappings = [row for row in mappings if row["queue_id"] in qids]
        by_pack[pack] = {
            "queue_memberships": len(qids),
            "occurrences": sum(1 for row in occurrences if row["origin_pack"] == pack),
            "manual_reviewed_proposals": len(pack_mappings),
            "queue_items_with_proposals": len({row["queue_id"] for row in pack_mappings}),
            "open_queue_items": len(qids - {row["queue_id"] for row in pack_mappings}),
        }
    return {
        "record_kind": "canonical_reference_coverage_report",
        "report_id": "canonical-reference-mapper.coverage.edition1",
        "edition": 1,
        "status": "triage_complete_adjudication_open",
        "input_queue_sha256": hashlib.sha256(QUEUE_PATH.read_bytes()).hexdigest(),
        "queue_items": len(queue),
        "source_occurrences": len(occurrences),
        "source_definitions": len(definitions),
        "triage_records": len(triage),
        "canonical_candidates": len(candidates),
        "universe_id_census_records": len(census),
        "mechanical_namespace_alignments": len(alignments),
        "alias_and_official_crosswalk_assertions": len(aliases),
        "manual_evidence_reviewed_proposals": len(mappings),
        "queue_items_with_semantic_proposals": len({row["queue_id"] for row in mappings}),
        "unresolved_first_class_triage_items": sum(row["relation"] == "unresolved" for row in triage),
        "missing_concept_proposals": len(missing),
        "collision_homonym_records": len(collisions_rows),
        "review_batches": len(batches),
        "authority_evidence_records": len(authority_records),
        "mappings_with_authority_evidence": len({
            row["mapping_id"] for row in mappings if row["evidence"].get("authority_evidence_refs")
        }),
        "authority_evidence_ref_counts": dict(sorted(Counter(
            ref for row in mappings for ref in row["evidence"].get("authority_evidence_refs", [])
        ).items())),
        "adjudicated_status_count": 0,
        "silent_rewrite_count": 0,
        "by_domain": by_domain,
        "by_pack": by_pack,
        "by_relation": dict(sorted(Counter(row["proposed_relation"] for row in mappings).items())),
        "by_confidence": dict(sorted(Counter(row["confidence"] for row in mappings).items())),
        "by_review_focus": dict(sorted(Counter(focus for row in mappings for focus in row["review_focus"]).items())),
        "completion_claim": False,
        "blocking_posture": "All records remain candidates or open gaps pending independent review and adjudication outside this pass.",
    }


def make_schema(title: str, required: list[str], properties: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title,
        "type": "object",
        "required": required,
        "properties": properties or {},
        "additionalProperties": True,
    }


def schemas() -> dict[str, dict[str, Any]]:
    common_string = {"type": "string", "minLength": 1}
    candidate_mapping_schema = make_schema(
        "Semantic candidate mapping",
        ["record_kind", "mapping_id", "queue_id", "reference_domain", "raw_ref", "target_refs", "proposed_relation", "rationale", "information_loss", "uncertainties", "evidence", "confidence", "review_status", "status", "adjudicated"],
        properties={
            "evidence": {
                "type": "object",
                "required": ["source_occurrence_refs", "source_evidence_refs", "target_evidence_refs", "authority_evidence_refs", "target_source_files", "target_contract_sha256s"],
                "properties": {
                    "source_occurrence_refs": {"type": "array", "items": common_string},
                    "source_evidence_refs": {"type": "array", "items": common_string},
                    "target_evidence_refs": {"type": "array", "items": common_string},
                    "authority_evidence_refs": {"type": "array", "items": common_string},
                    "target_source_files": {"type": "array", "items": common_string},
                    "target_contract_sha256s": {"type": "array", "items": {"type": "string", "pattern": "^[0-9a-f]{64}$"}},
                },
                "additionalProperties": True,
            },
        },
    )
    return {
        "source-occurrence.schema.json": make_schema("Canonical-reference source occurrence", ["record_kind", "occurrence_id", "reference_domain", "raw_ref", "origin_pack", "source_record_id", "context"]),
        "source-definition.schema.json": make_schema("Canonical-reference source definition", ["record_kind", "source_definition_id", "queue_id", "reference_domain", "raw_ref", "occurrence_count", "definition_status"]),
        "canonical-candidate.schema.json": make_schema("Canonical candidate index record", ["record_kind", "candidate_id", "canonical_domain", "concept_kind", "name", "definition", "semantic_contract_sha256", "source_file"]),
        "universe-id-census.schema.json": make_schema("Universe identifier census record", ["record_kind", "identifier", "declaration_seen", "declaration_files", "reference_files", "field_names", "occurrence_count"]),
        "alias-assertion.schema.json": make_schema("Declared alias or official crosswalk assertion", ["record_kind", "assertion_id", "assertion_kind", "status"]),
        "namespace-alignment.schema.json": make_schema("Mechanical namespace alignment", ["record_kind", "alignment_id", "queue_id", "raw_ref", "candidate_target_ref", "semantic_effect", "proves_equivalence"]),
        "candidate-mapping.schema.json": candidate_mapping_schema,
        "authority-evidence.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Canonical-reference authority evidence",
            "type": "object",
            "additionalProperties": False,
            "required": [
                "record_kind", "authority_id", "title", "publisher_or_authors", "source_kind",
                "primary_url", "accessed_at", "authority_scope", "supports", "limitations", "status",
            ],
            "properties": {
                "record_kind": {"const": "canonical_reference_authority_evidence"},
                "authority_id": {"type": "string", "minLength": 1},
                "title": {"type": "string", "minLength": 1},
                "publisher_or_authors": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1},
                "source_kind": {"enum": ["official_method_body", "official_product_documentation", "primary_research_paper"]},
                "primary_url": {"type": "string", "format": "uri", "minLength": 1},
                "related_urls": {"type": "array", "items": {"type": "string", "format": "uri"}},
                "publication_year": {"type": "integer", "minimum": 1900, "maximum": 2100},
                "accessed_at": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
                "authority_scope": {"type": "string", "minLength": 1},
                "supports": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1},
                "limitations": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1},
                "status": {"const": "verified_primary_evidence"},
            },
        },
        "missing-concept.schema.json": make_schema("Missing canonical concept proposal", ["record_kind", "proposal_id", "queue_id", "reference_domain", "raw_ref", "proposed_relation", "status", "adjudicated"]),
        "collision.schema.json": make_schema("Collision or homonym record", ["record_kind", "collision_id", "collision_kind", "reference_domain", "risk", "required_action", "status"]),
        "triage-record.schema.json": make_schema("Canonical-reference triage record", ["record_kind", "triage_id", "queue_id", "queue_record_sha256", "reference_domain", "raw_ref", "occurrence_count", "relation", "status", "adjudicated"]),
        "review-batch.schema.json": make_schema("Canonical-reference review batch", ["record_kind", "batch_id", "primary_pack", "reference_domain", "lane", "queue_ids", "queue_item_count", "review_protocol", "status"]),
        "negative-test.schema.json": make_schema("False-twin refusal test", ["test_id", "left", "right", "forbidden_relation", "reason"]),
        "coverage-report.schema.json": make_schema("Canonical-reference coverage report", ["record_kind", "report_id", "queue_items", "source_occurrences", "triage_records", "manual_evidence_reviewed_proposals", "adjudicated_status_count", "silent_rewrite_count", "by_domain", "by_pack"]),
    }


def build_outputs() -> dict[str, bytes]:
    queue = load_jsonl(QUEUE_PATH)
    authority_records = load_authority_evidence()
    candidates = canonical_candidates()
    census = universe_id_census()
    occurrences = source_occurrences()
    definitions = source_definitions(queue, occurrences)
    alignments = namespace_alignments(queue, candidates)
    aliases = alias_assertions(candidates)
    mappings = candidate_mappings(queue, definitions, candidates, occurrences)
    missing = missing_concepts(queue, definitions, alignments, mappings)
    collision_rows = collisions(queue, candidates, alignments)
    triage = triage_records(queue, definitions, candidates, mappings, missing, alignments)
    batches = review_batches(triage, mappings)
    negatives = negative_tests()
    coverage = coverage_report(
        queue, occurrences, definitions, candidates, census, alignments, aliases,
        mappings, missing, collision_rows, triage, batches,
        authority_records,
    )
    artifacts: dict[str, bytes] = {
        "source-occurrences.jsonl": jsonl_bytes(occurrences),
        "source-definitions.jsonl": jsonl_bytes(definitions),
        "canonical-candidate-index.jsonl": jsonl_bytes(candidates),
        "universe-id-census.jsonl": jsonl_bytes(census),
        "alias-assertions.jsonl": jsonl_bytes(aliases),
        "namespace-alignments.jsonl": jsonl_bytes(alignments),
        "candidate-mappings.jsonl": jsonl_bytes(mappings),
        "missing-concept-proposals.jsonl": jsonl_bytes(missing),
        "collisions-homonyms.jsonl": jsonl_bytes(collision_rows),
        "triage-records.jsonl": jsonl_bytes(triage),
        "review-batches.jsonl": jsonl_bytes(batches),
        "negative-tests.jsonl": jsonl_bytes(negatives),
        "coverage-report.json": json_bytes(coverage),
        "coverage-report.jsonl": jsonl_bytes([coverage]),
    }
    for name, schema in schemas().items():
        artifacts[f"schemas/{name}"] = json_bytes(schema)
    manifest_artifacts = {
        name: {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload), "records": payload.count(b"\n") if name.endswith(".jsonl") else 1}
        for name, payload in sorted(artifacts.items())
    }
    manifest = {
        "record_kind": "canonical_reference_mapper_manifest",
        "edition": 1,
        "generator": "build_mapper.py",
        "input_queue": QUEUE_PATH.relative_to(ATLAS).as_posix(),
        "input_queue_sha256": hashlib.sha256(QUEUE_PATH.read_bytes()).hexdigest(),
        "input_queue_records": len(queue),
        "input_manual_proposal_seeds": MANUAL_SEEDS_PATH.relative_to(ATLAS).as_posix(),
        "input_manual_proposal_seeds_sha256": hashlib.sha256(MANUAL_SEEDS_PATH.read_bytes()).hexdigest(),
        "input_manual_proposal_seed_count": len(load_manual_seeds()),
        "input_authority_evidence": AUTHORITY_EVIDENCE_PATH.relative_to(ATLAS).as_posix(),
        "input_authority_evidence_sha256": hashlib.sha256(AUTHORITY_EVIDENCE_PATH.read_bytes()).hexdigest(),
        "input_authority_evidence_records": len(authority_records),
        "artifacts": manifest_artifacts,
        "adjudication_performed": False,
        "llm_runtime_dependency": "none",
    }
    artifacts["manifest.json"] = json_bytes(manifest)
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare generated bytes without writing")
    args = parser.parse_args()
    artifacts = build_outputs()
    mismatches = []
    for relative, payload in artifacts.items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_bytes() != payload:
                mismatches.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    if mismatches:
        for mismatch in mismatches:
            print(f"ERROR: generated artifact differs: {mismatch}")
        return 1
    action = "verified" if args.check else "wrote"
    report = json.loads(artifacts["coverage-report.json"])
    print(
        f"PASS {action} canonical-reference triage: {report['queue_items']} queue items, "
        f"{report['source_occurrences']} occurrences, {report['manual_evidence_reviewed_proposals']} "
        f"manual evidence-reviewed proposals, {report['adjudicated_status_count']} adjudicated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
