#!/usr/bin/env python3
"""Build the lossless P2 owner and occurrence-adjudication docket.

P2 never infers or ratifies an owner. It converts the complete P1 research surface into
dependency-ordered, machine-readable decisions for named semantic and library owners.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
P1 = HERE.parent / "p1_authority_symbols"
REPO = HERE.parents[6]
LIBRARY_REGISTRY = P1.parents[2]
LIBRARY_CONTRIBUTIONS = LIBRARY_REGISTRY / "library-contributions.jsonl"
DEPENDENCY_EDGES = LIBRARY_REGISTRY / "dependency-edges.jsonl"
AS_OF = "2026-08-27"

CLASSIFICATION_FILES = (
    "analytical-result-classification-candidates.jsonl",
    "authority-contract-classification-candidates.jsonl",
    "capability-port-classification-candidates.jsonl",
    "evidence-contract-classification-candidates.jsonl",
    "failure-contract-classification-candidates.jsonl",
    "identity-contract-classification-candidates.jsonl",
    "measure-contract-classification-candidates.jsonl",
    "model-artifact-contract-classification-candidates.jsonl",
    "operation-contract-classification-candidates.jsonl",
    "policy-contract-classification-candidates.jsonl",
    "representation-contract-classification-candidates.jsonl",
    "resource-contract-classification-candidates.jsonl",
    "shape-contract-classification-candidates.jsonl",
    "time-contract-classification-candidates.jsonl",
)

INPUT_FILES = (
    "symbol-adjudication-packets.jsonl",
    "high-fanout-semantic-research.jsonl",
    "remaining-symbol-research-batches.jsonl",
    "archetype-research-programs.jsonl",
    "archetype-semantic-research.jsonl",
    "catchall-symbol-archetype-refinements.jsonl",
    "primary-sources.jsonl",
) + CLASSIFICATION_FILES

ROUTE_TO_WAVE = {
    "CROSS_FAMILY_SHARED_OWNER_HYPOTHESIS_RESEARCH": "wave.p2.owner.01-cross-family",
    "FAMILY_SHARED_OWNER_OR_LOCAL_IMPORT_RESEARCH": "wave.p2.owner.02-family",
    "HOMONYM_OR_DEFINITION_CONFLICT_RESEARCH": "wave.p2.owner.03-homonym",
}

DISPOSITION_ONTOLOGY = {
    "ontology_id": "ontology.p2-public-symbol-owner-disposition.v1",
    "edition": 1,
    "as_of": AS_OF,
    "question": "Who owns each repeated public symbol meaning, and how does every exact occurrence relate to that owner without losing local semantics?",
    "symbol_dispositions": [
        "CANONICAL_SHARED_OWNER_AND_IMPORTS",
        "FAMILY_SHARED_OWNER_AND_IMPORTS",
        "QUALIFY_LOCAL_SYMBOL_IDS",
        "HOMONYM_RENAME",
        "MERGE_DUPLICATE_LIBRARIES",
        "REJECT_DUPLICATE_DEFINITION",
        "UNRESOLVED",
    ],
    "occurrence_relations": [
        "OWNER_DECLARATION",
        "IMPORT_EXACT",
        "IMPORT_WITH_PROFILE",
        "QUALIFIED_LOCAL_HOMONYM",
        "RENAME_AND_MIGRATE",
        "RETIRE_DUPLICATE",
        "REJECT_OCCURRENCE",
        "UNRESOLVED",
    ],
    "required_decision_authorities": ["SEMANTIC_OWNER", "FAMILY_OWNER", "LIBRARY_OWNER"],
    "non_collapse_laws": [
        "bounded research is not owner ratification",
        "a shared carrier is not a shared bounded-context meaning",
        "equal spelling or definition digest is not semantic equality",
        "candidate owner is not canonical owner",
        "family default is not occurrence applicability",
        "qualified homonym is not an import",
        "import with profile is not exact import",
        "owner decision is not exact schema or implementation",
        "a ratification receipt authorizes only its exact input digest and edition",
        "canonical mutation is forbidden until every affected occurrence has a disposition",
    ],
    "ratification_receipt_required_fields": [
        "decision_id",
        "decision_authority_ref",
        "authority_scope",
        "input_snapshot_digest",
        "symbol_packet_ref",
        "selected_symbol_disposition",
        "semantic_owner_ref_or_local_owner_map",
        "definition_and_equality_contract_ref",
        "occurrence_disposition_refs",
        "migration_plan_ref",
        "effective_edition",
        "approved_at",
        "signature_or_attestation_ref",
    ],
    "completion_claim": False,
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace(".", "-").replace("_", "-").replace("/", "-")


def snapshot() -> dict[str, Any]:
    files = []
    paths = [P1 / name for name in INPUT_FILES] + [LIBRARY_CONTRIBUTIONS, DEPENDENCY_EDGES]
    for path in paths:
        data = path.read_bytes()
        files.append({
            "path": str(path.relative_to(REPO)),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "record_count": len(load_jsonl(path)),
        })
    digest = hashlib.sha256(canonical(files).encode()).hexdigest()
    return {"snapshot_id": f"snapshot.p2-input.{digest[:16]}", "aggregate_sha256": digest, "files": files}


def candidate_rows() -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    by_packet: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for name in CLASSIFICATION_FILES:
        for row in load_jsonl(P1 / name):
            enriched = dict(row)
            enriched["_source_file"] = name
            by_packet[row["symbol_packet_ref"]].append(enriched)
    for row in load_jsonl(P1 / "catchall-symbol-archetype-refinements.jsonl"):
        enriched = dict(row)
        enriched["_source_file"] = "catchall-symbol-archetype-refinements.jsonl"
        by_packet[row["symbol_packet_ref"]].append(enriched)
    high = {row["symbol_packet_ref"]: row for row in load_jsonl(P1 / "high-fanout-semantic-research.jsonl")}
    return by_packet, high


def union_strings(rows: list[dict[str, Any]], key: str) -> list[str]:
    return sorted({item for row in rows for item in row.get(key, []) if isinstance(item, str)})


def profile_by_library(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, set[str]] = collections.defaultdict(set)
    for row in rows:
        for profile in row.get("occurrence_profile_candidates", []):
            library_ref = profile.get("library_ref")
            if not library_ref:
                continue
            for key, value in profile.items():
                if key != "library_ref" and key.startswith("candidate_") and isinstance(value, str):
                    result[library_ref].add(value)
    return {key: sorted(value) for key, value in sorted(result.items())}


def semantic_role_candidates(rows: list[dict[str, Any]]) -> list[str]:
    values = set()
    for row in rows:
        for key, value in row.items():
            if key.startswith("candidate_") and (key.endswith("_role") or key == "candidate_semantic_role") and isinstance(value, str):
                values.add(value)
    return sorted(values)


def make_dockets() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    packets = load_jsonl(P1 / "symbol-adjudication-packets.jsonl")
    batches = load_jsonl(P1 / "remaining-symbol-research-batches.jsonl")
    archetype_research = {row["archetype_id"]: row for row in load_jsonl(P1 / "archetype-semantic-research.jsonl")}
    packet_to_batch = {packet_ref: batch for batch in batches for packet_ref in batch["packet_refs"]}
    candidate_by_packet, high_by_packet = candidate_rows()
    docket_rows = []
    occurrence_rows = []
    docket_by_packet: dict[str, dict[str, Any]] = {}

    for packet in sorted(packets, key=lambda row: row["priority_rank"]):
        packet_ref = packet["packet_id"]
        candidates = candidate_by_packet.get(packet_ref, [])
        high = high_by_packet.get(packet_ref)
        batch = packet_to_batch.get(packet_ref)
        archetype = batch["research_archetype"] if batch else "HIGH_FANOUT_DIRECT_RESEARCH"
        archetype_evidence = archetype_research.get(archetype, {})
        source_refs = set(archetype_evidence.get("source_refs", []))
        source_refs.update(union_strings(candidates, "source_refs"))
        if high:
            source_refs.update(high["source_refs"])
        research_basis_refs = []
        if high:
            research_basis_refs.append(high["research_id"])
        research_basis_refs.extend(row.get("candidate_id") or row.get("refinement_id") for row in candidates)
        research_basis_refs = sorted(ref for ref in research_basis_refs if ref)
        disposition_hypotheses = sorted({
            value
            for value in ([high.get("disposition_hypothesis")] if high else [])
            + [row.get("candidate_disposition_hypothesis") for row in candidates]
            if value
        })
        owner_hypotheses = sorted({row["candidate_owner_hypothesis"] for row in candidates if row.get("candidate_owner_hypothesis")})
        required_decisions = set(packet["required_questions"])
        required_decisions.update(union_strings(candidates, "required_owner_decisions"))
        if high:
            required_decisions.update(high["remaining_owner_decisions"])
        laws = set(archetype_evidence.get("non_collapse_laws", []))
        laws.update(union_strings(candidates, "non_collapse_laws"))
        if high:
            laws.update(high["non_collapse_laws"])
        authority_limits = sorted({
            value
            for value in ([high.get("authority_limit")] if high else [])
            + [row.get("authority_limit") for row in candidates]
            + [archetype_evidence.get("authority_limit")]
            if value
        })
        decision_unit_ref = (
            f"decision-unit.p2.direct.{slug(packet['symbol_ref'])}.v1"
            if high
            else f"decision-unit.p2.batch.{batch['batch_id'].removeprefix('batch.p1.remaining-symbols.').removesuffix('.v1')}.v1"
        )
        docket_id = f"docket.p2.symbol.{slug(packet['symbol_ref'])}.v1"
        docket = {
            "record_kind": "public_symbol_owner_adjudication_docket",
            "docket_id": docket_id,
            "edition": 1,
            "symbol_packet_ref": packet_ref,
            "symbol_kind": packet["symbol_kind"],
            "symbol_ref": packet["symbol_ref"],
            "priority_rank": packet["priority_rank"],
            "research_route": packet["research_route"],
            "research_archetype": archetype,
            "research_state": "BOUNDED_PRIMARY_RESEARCH_COMPLETE",
            "research_basis_refs": research_basis_refs,
            "source_refs": sorted(source_refs),
            "family_refs": packet["family_refs"],
            "occurrence_count": packet["library_count"],
            "definition_digests": packet["definition_digests"],
            "semantic_role_candidates": semantic_role_candidates(candidates),
            "disposition_hypotheses": disposition_hypotheses,
            "candidate_owner_refs": owner_hypotheses,
            "allowed_symbol_dispositions": packet["allowed_dispositions"],
            "selected_symbol_disposition": "UNRESOLVED",
            "selected_semantic_owner_ref": None,
            "definition_and_equality_contract_ref": None,
            "occurrence_disposition_complete": False,
            "required_owner_decisions": sorted(required_decisions),
            "non_collapse_laws": sorted(laws),
            "authority_limits": authority_limits,
            "decision_unit_ref": decision_unit_ref,
            "decision_wave_ref": ROUTE_TO_WAVE[packet["research_route"]],
            "ratification_receipt_ref": None,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "DECISION_READY_OWNER_UNRATIFIED",
            "completion_claim": False,
        }
        docket_rows.append(docket)
        docket_by_packet[packet_ref] = docket

        profiles = profile_by_library(candidates)
        for occurrence in sorted(packet["occurrences"], key=lambda row: (row["library_ref"], row["name"])):
            occurrence_id = f"occurrence.p2.{slug(packet['symbol_ref'])}.{slug(occurrence['library_ref'])}.v1"
            occurrence_rows.append({
                "record_kind": "public_symbol_occurrence_disposition_candidate",
                "occurrence_id": occurrence_id,
                "edition": 1,
                "docket_ref": docket_id,
                "symbol_packet_ref": packet_ref,
                "symbol_ref": packet["symbol_ref"],
                "family_ref": occurrence["family_id"],
                "library_ref": occurrence["library_ref"],
                "current_public_name": occurrence["name"],
                "current_definition_digest": occurrence["definition_digest"],
                "local_profile_candidates": profiles.get(occurrence["library_ref"], []),
                "allowed_occurrence_relations": DISPOSITION_ONTOLOGY["occurrence_relations"],
                "selected_occurrence_relation": "UNRESOLVED",
                "selected_owner_ref": None,
                "selected_public_name": None,
                "profile_contract_ref": None,
                "migration_obligation_refs": [],
                "required_authority_roles": ["SEMANTIC_OWNER", "LIBRARY_OWNER"],
                "ratification_receipt_ref": None,
                "canonical_mutation_allowed": False,
                "canonical_gaps_closed": 0,
                "status": "BLOCKED_PENDING_SYMBOL_OWNER_RATIFICATION",
                "completion_claim": False,
            })
    return docket_rows, occurrence_rows, docket_by_packet


def make_units(docket_by_packet: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    high = load_jsonl(P1 / "high-fanout-semantic-research.jsonl")
    batches = load_jsonl(P1 / "remaining-symbol-research-batches.jsonl")
    unit_specs: list[tuple[str, list[str], str, str, str]] = []
    for row in high:
        unit_specs.append((
            f"decision-unit.p2.direct.{slug(row['symbol_ref'])}.v1",
            [row["symbol_packet_ref"]],
            "DIRECT_HIGH_FANOUT_SYMBOL",
            "HIGH_FANOUT_DIRECT_RESEARCH",
            docket_by_packet[row["symbol_packet_ref"]]["research_route"],
        ))
    for batch in batches:
        unit_specs.append((
            f"decision-unit.p2.batch.{batch['batch_id'].removeprefix('batch.p1.remaining-symbols.').removesuffix('.v1')}.v1",
            batch["packet_refs"],
            "LOSSLESS_RESEARCH_BATCH_QUOTIENT",
            batch["research_archetype"],
            batch["research_route"],
        ))
    units = []
    for unit_id, packet_refs, unit_kind, archetype, route in unit_specs:
        dockets = [docket_by_packet[ref] for ref in packet_refs]
        units.append({
            "record_kind": "public_symbol_owner_decision_unit",
            "decision_unit_id": unit_id,
            "edition": 1,
            "unit_kind": unit_kind,
            "grouping_basis": "ONE_DIRECT_HIGH_FANOUT_RESEARCHED_SYMBOL" if unit_kind == "DIRECT_HIGH_FANOUT_SYMBOL" else "SHARED_RESEARCH_ARCHETYPE_ROUTE_AND_CLUSTER_WITH_PER_SYMBOL_DECISION_GRAIN",
            "research_archetype": archetype,
            "research_route": route,
            "decision_wave_ref": ROUTE_TO_WAVE[route],
            "symbol_docket_refs": [row["docket_id"] for row in dockets],
            "symbol_packet_refs": packet_refs,
            "symbol_count": len(packet_refs),
            "represented_occurrence_count": sum(row["occurrence_count"] for row in dockets),
            "family_refs": sorted({ref for row in dockets for ref in row["family_refs"]}),
            "source_refs": sorted({ref for row in dockets for ref in row["source_refs"]}),
            "decision_grain": "PER_SYMBOL_AND_PER_EXACT_OCCURRENCE",
            "coordination_law": "Share evidence and counterexample review inside this unit; never copy an owner, disposition or applicability decision between member symbols or occurrences.",
            "required_outputs": ["one ratified symbol disposition per docket", "one named semantic owner or complete local-owner map", "one exact definition/equality/lifecycle contract", "one disposition per exact occurrence", "one no-alias migration plan", "one content-addressed ratification receipt"],
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "DECISION_READY_OWNER_UNRATIFIED",
            "completion_claim": False,
        })
    return sorted(units, key=lambda row: (row["decision_wave_ref"], -row["represented_occurrence_count"], row["decision_unit_id"]))


def make_waves(units: list[dict[str, Any]], dockets: list[dict[str, Any]], occurrences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    specs = [
        ("wave.p2.owner.01-cross-family", 1, [], "CROSS_FAMILY_SHARED_OWNER_HYPOTHESIS_RESEARCH", "Ratify global or cross-family meanings before downstream family imports."),
        ("wave.p2.owner.02-family", 2, ["wave.p2.owner.01-cross-family"], "FAMILY_SHARED_OWNER_OR_LOCAL_IMPORT_RESEARCH", "Ratify family owners and profiled imports against already-decided cross-family primitives."),
        ("wave.p2.owner.03-homonym", 3, ["wave.p2.owner.01-cross-family"], "HOMONYM_OR_DEFINITION_CONFLICT_RESEARCH", "Split, qualify, rename, merge or reject collisions without using spelling as identity."),
    ]
    waves = []
    for wave_id, rank, dependencies, route, outcome in specs:
        members = [row for row in units if row["research_route"] == route]
        packets = [ref for row in members for ref in row["symbol_packet_refs"]]
        waves.append({
            "record_kind": "public_symbol_owner_decision_wave",
            "wave_id": wave_id,
            "edition": 1,
            "execution_rank": rank,
            "depends_on_wave_refs": dependencies,
            "research_route": route,
            "decision_unit_refs": [row["decision_unit_id"] for row in members],
            "symbol_packet_refs": packets,
            "symbol_count": len(packets),
            "represented_occurrence_count": sum(row["represented_occurrence_count"] for row in members),
            "exit_gate": outcome,
            "status": "READY_UNRATIFIED",
            "completion_claim": False,
        })
    waves.append({
        "record_kind": "public_symbol_owner_decision_wave",
        "wave_id": "wave.p2.owner.04-occurrences",
        "edition": 1,
        "execution_rank": 4,
        "depends_on_wave_refs": [row["wave_id"] for row in waves],
        "research_route": "EXACT_OCCURRENCE_DISPOSITION",
        "decision_unit_refs": [],
        "symbol_docket_refs": [row["docket_id"] for row in dockets],
        "symbol_packet_refs": [row["symbol_packet_ref"] for row in dockets],
        "symbol_count": len(dockets),
        "represented_occurrence_count": len(occurrences),
        "exit_gate": "Every occurrence is explicitly the owner declaration, an exact/profiled import, a qualified homonym, a renamed/migrated occurrence, a retired duplicate or a rejected occurrence.",
        "status": "BLOCKED_PENDING_OWNER_WAVES",
        "completion_claim": False,
    })
    return waves


CLASS_WEIGHTS = {
    "semantic_pure": 40,
    "policy_pure": 32,
    "algorithm_pure": 28,
    "effect_port_contract": 18,
    "runtime_mechanism": 10,
    "test_oracle": 5,
    "provider_adapter": -30,
    "target_backend": -30,
}

POSITIVE_NAME_TOKENS = {"core", "semantics", "identity", "algebra", "model", "types", "contract", "ledger", "catalog", "baseline", "estimator", "policy", "profile", "schema"}
NEGATIVE_NAME_WEIGHTS = {"adapter": -30, "provider": -20, "backend": -20, "client": -15, "sink": -15, "bridge": -15, "gateway": -10, "compiler": -8, "runtime": -8}
NAME_DERIVED_FEATURES = {
    "owner_shaped_name_tokens",
    "weak_symbol_name_overlap",
    "adapter_or_runtime_name_penalty",
}


def name_tokens(value: str) -> set[str]:
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value).lower()
    raw = re.findall(r"[a-z0-9]+", words)
    normalized = set(raw)
    for word in raw:
        if word.endswith("ers") and len(word) > 5:
            normalized.add(word[:-3])
        elif word.endswith("er") and len(word) > 4:
            normalized.add(word[:-2])
        elif word.endswith("s") and len(word) > 4:
            normalized.add(word[:-1])
    return normalized


def rank_owner_candidates(
    docket: dict[str, Any],
    docket_occurrences: list[dict[str, Any]],
    libraries: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    occurrence_libs = {row["library_ref"] for row in docket_occurrences}
    explicit = set(docket["candidate_owner_refs"])
    symbol_tokens = set()
    for row in docket_occurrences:
        symbol_tokens.update(name_tokens(row["current_public_name"]))
    rankings = []
    for library_ref in sorted(occurrence_libs):
        library = libraries[library_ref]
        library_class = library.get("library_class", "unknown")
        tokens = name_tokens(library_ref) | name_tokens(library.get("name", ""))
        features = []
        score = CLASS_WEIGHTS.get(library_class, 0)
        features.append({"feature": "library_class", "value": library_class, "score": CLASS_WEIGHTS.get(library_class, 0)})
        if library_ref in explicit:
            score += 100
            features.append({"feature": "p1_explicit_owner_hypothesis", "value": library_ref, "score": 100})
        positive = sorted(tokens & POSITIVE_NAME_TOKENS)
        if positive:
            value = min(18, 6 * len(positive))
            score += value
            features.append({"feature": "owner_shaped_name_tokens", "value": positive, "score": value})
        for token, weight in NEGATIVE_NAME_WEIGHTS.items():
            if token in tokens:
                score += weight
                features.append({"feature": "adapter_or_runtime_name_penalty", "value": token, "score": weight})
        overlap = sorted(tokens & symbol_tokens)
        if overlap:
            value = min(18, 6 * len(overlap))
            score += value
            features.append({"feature": "weak_symbol_name_overlap", "value": overlap, "score": value})
        incoming = sorted({edge["from_ref"] for edge in edges if edge["to_ref"] == library_ref and edge["from_ref"] in occurrence_libs})
        outgoing = sorted({edge["to_ref"] for edge in edges if edge["from_ref"] == library_ref and edge["to_ref"] in occurrence_libs})
        if incoming:
            value = min(60, 20 * len(incoming))
            score += value
            features.append({"feature": "explicit_owner_context_dependency_incoming", "value": incoming, "score": value})
        if outgoing:
            value = -min(45, 15 * len(outgoing))
            score += value
            features.append({"feature": "explicit_semantic_contract_dependency_outgoing", "value": outgoing, "score": value})
        source_status = library.get("source_projection", {}).get("source_status")
        if source_status in {"specified", "sourced_candidate"}:
            score += 3
            features.append({"feature": "source_projection_status", "value": source_status, "score": 3})
        contexts = sorted({row.get("context_ref") for row in library.get("semantic_owners", []) if row.get("role") == "meaning_owner" and row.get("context_ref")})
        rankings.append({
            "library_ref": library_ref,
            "library_class": library_class,
            "context_refs": contexts or library.get("context_refs", []),
            "score": score,
            "evidence_features": features,
            "counterevidence": [
                item
                for item in [
                    "provider_or_target_implementation_cannot_define_semantics" if library_class in {"provider_adapter", "target_backend"} else None,
                    "candidate_has_outgoing_semantic_contract_dependency" if outgoing else None,
                    "no_explicit_dependency_witness_from_peer_occurrences" if not incoming else None,
                ]
                if item
            ],
        })
    return sorted(rankings, key=lambda row: (-row["score"], row["library_ref"]))


def proposal_disposition(docket: dict[str, Any], rankings: list[dict[str, Any]]) -> str:
    exact = sorted(set(docket["disposition_hypotheses"]) & set(DISPOSITION_ONTOLOGY["symbol_dispositions"]))
    if len(exact) == 1:
        return exact[0]
    route = docket["research_route"]
    if route == "CROSS_FAMILY_SHARED_OWNER_HYPOTHESIS_RESEARCH":
        return "CANONICAL_SHARED_OWNER_AND_IMPORTS"
    if route == "FAMILY_SHARED_OWNER_OR_LOCAL_IMPORT_RESEARCH":
        return "FAMILY_SHARED_OWNER_AND_IMPORTS"
    contexts = {context for row in rankings for context in row["context_refs"]}
    if route == "HOMONYM_OR_DEFINITION_CONFLICT_RESEARCH" and len(contexts) > 1:
        return "QUALIFY_LOCAL_SYMBOL_IDS"
    return "UNRESOLVED"


def proposed_owners(disposition: str, rankings: list[dict[str, Any]]) -> tuple[list[str], str, list[str]]:
    if not rankings or disposition == "UNRESOLVED":
        return [], "UNRESOLVED", ["no disposition or owner can be proposed without stronger evidence"]
    if disposition in {"QUALIFY_LOCAL_SYMBOL_IDS", "HOMONYM_RENAME"}:
        by_context: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
        for row in rankings:
            for context in row["context_refs"] or ["UNSCOPED"]:
                by_context[context].append(row)
        owners = []
        for rows in by_context.values():
            ordered = sorted(rows, key=lambda row: (-row["score"], row["library_ref"]))
            if ordered[0]["score"] >= 20 and (len(ordered) == 1 or ordered[0]["score"] - ordered[1]["score"] >= 10):
                owners.append(ordered[0]["library_ref"])
        owners = sorted(set(owners))
        if owners and len(owners) == len(by_context):
            return owners, "MEDIUM", []
        return owners, "LOW", ["one or more bounded contexts lack a decisive local-owner margin"]
    top = rankings[0]
    margin = top["score"] - rankings[1]["score"] if len(rankings) > 1 else top["score"]
    if top["library_class"] in {"provider_adapter", "target_backend"}:
        return [], "UNRESOLVED", ["highest-ranked occurrence is an implementation/provider boundary"]
    if top["score"] >= 80 and margin >= 15:
        return [top["library_ref"]], "HIGH", []
    if top["score"] >= 25 and margin >= 10:
        return [top["library_ref"]], "MEDIUM", []
    return [], "LOW", ["candidate score or separation margin is insufficient for a single-owner proposal"]


def without_name_derived_evidence(rankings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counterfactual = []
    for ranking in rankings:
        row = dict(ranking)
        row["evidence_features"] = [
            feature for feature in ranking["evidence_features"]
            if feature["feature"] not in NAME_DERIVED_FEATURES
        ]
        row["score"] = sum(feature["score"] for feature in row["evidence_features"])
        counterfactual.append(row)
    return sorted(counterfactual, key=lambda row: (-row["score"], row["library_ref"]))


def make_proposals(dockets: list[dict[str, Any]], occurrences: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    libraries = {row["library_id"]: row for row in load_jsonl(LIBRARY_CONTRIBUTIONS)}
    edges = load_jsonl(DEPENDENCY_EDGES)
    occurrences_by_docket: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in occurrences:
        occurrences_by_docket[row["docket_ref"]].append(row)
    owner_rows = []
    relation_rows = []
    conflicts = []
    counterfactual_rows = []
    for docket in dockets:
        local_occurrences = occurrences_by_docket[docket["docket_id"]]
        rankings = rank_owner_candidates(docket, local_occurrences, libraries, edges)
        disposition = proposal_disposition(docket, rankings)
        baseline_owners, baseline_confidence, baseline_blockers = proposed_owners(disposition, rankings)
        name_free_rankings = without_name_derived_evidence(rankings)
        counterfactual_owners, counterfactual_confidence, counterfactual_blockers = proposed_owners(disposition, name_free_rankings)
        stable = baseline_owners == counterfactual_owners
        owners = baseline_owners if stable else []
        confidence = baseline_confidence if stable else "LOW"
        blockers = list(baseline_blockers)
        if not stable:
            blockers.append("owner proposal changes when all name-derived evidence is removed")
        proposal_id = f"proposal.p2.owner.{slug(docket['symbol_ref'])}.v1"
        counterfactual_rows.append({
            "record_kind": "owner_proposal_counterfactual",
            "counterfactual_id": f"counterfactual.p2.owner.{slug(docket['symbol_ref'])}.without-names.v1",
            "edition": 1,
            "proposal_ref": proposal_id,
            "docket_ref": docket["docket_id"],
            "symbol_ref": docket["symbol_ref"],
            "test": "REMOVE_ALL_NAME_DERIVED_SCORE_FEATURES",
            "removed_feature_kinds": sorted(NAME_DERIVED_FEATURES),
            "baseline_owner_refs": baseline_owners,
            "counterfactual_owner_refs": counterfactual_owners,
            "baseline_confidence": baseline_confidence,
            "counterfactual_confidence": counterfactual_confidence,
            "counterfactual_blockers": counterfactual_blockers,
            "stability": "STABLE" if stable else "UNSTABLE",
            "ratification_required": True,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        })
        proposal = {
            "record_kind": "public_symbol_owner_proposal",
            "proposal_id": proposal_id,
            "edition": 1,
            "docket_ref": docket["docket_id"],
            "symbol_packet_ref": docket["symbol_packet_ref"],
            "symbol_ref": docket["symbol_ref"],
            "proposed_symbol_disposition": disposition,
            "proposed_owner_refs": owners,
            "candidate_rankings": rankings,
            "confidence": confidence,
            "blockers": blockers,
            "proposal_basis": "P1_BOUNDED_RESEARCH_PLUS_EXPLICIT_CONTEXT_CLASS_AND_DEPENDENCY_EVIDENCE_WITH_WEAK_NAME_SUPPORT",
            "counterfactual_checks": ["remove name-token scores and preserve dependency/class evidence", "reject provider adapters and target backends as semantic owners", "preserve separate owners when bounded contexts differ", "keep unresolved when the score margin is insufficient"],
            "ratification_required": True,
            "ratification_receipt_ref": None,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "PROPOSED_UNRATIFIED" if disposition != "UNRESOLVED" and owners else "BLOCKED_NEEDS_OWNER_EVIDENCE",
            "completion_claim": False,
        }
        owner_rows.append(proposal)
        if blockers or disposition == "UNRESOLVED" or not owners:
            conflicts.append({
                "record_kind": "owner_proposal_conflict",
                "conflict_id": f"conflict.p2.owner.{slug(docket['symbol_ref'])}.v1",
                "edition": 1,
                "proposal_ref": proposal_id,
                "docket_ref": docket["docket_id"],
                "symbol_ref": docket["symbol_ref"],
                "conflict_kind": "NO_DECISIVE_OWNER" if not owners else "PARTIAL_LOCAL_OWNER_SET",
                "details": blockers or ["symbol disposition remains unresolved"],
                "top_candidate_refs": [row["library_ref"] for row in rankings[:3]],
                "required_evidence": ["named bounded-context owner decision", "exact meaning/equality/lifecycle contract", "counterexample review for losing candidates", "content-addressed ratification receipt"],
                "status": "OPEN",
                "completion_claim": False,
            })
        context_owner = {}
        for owner_ref in owners:
            owner_record = libraries[owner_ref]
            for context in [row.get("context_ref") for row in owner_record.get("semantic_owners", []) if row.get("context_ref")]:
                context_owner[context] = owner_ref
        for occurrence in local_occurrences:
            library_ref = occurrence["library_ref"]
            library_contexts = [row.get("context_ref") for row in libraries[library_ref].get("semantic_owners", []) if row.get("context_ref")]
            proposed_owner = library_ref if library_ref in owners else next((context_owner[ref] for ref in library_contexts if ref in context_owner), owners[0] if len(owners) == 1 else None)
            if not proposed_owner:
                relation = "UNRESOLVED"
            elif library_ref == proposed_owner:
                relation = "OWNER_DECLARATION"
            elif disposition in {"QUALIFY_LOCAL_SYMBOL_IDS", "HOMONYM_RENAME"} and not set(library_contexts) & set(libraries[proposed_owner].get("context_refs", [])):
                relation = "QUALIFIED_LOCAL_HOMONYM"
            elif occurrence["local_profile_candidates"]:
                relation = "IMPORT_WITH_PROFILE"
            else:
                relation = "IMPORT_EXACT"
            relation_rows.append({
                "record_kind": "public_symbol_occurrence_relation_proposal",
                "relation_proposal_id": f"proposal.p2.occurrence.{slug(docket['symbol_ref'])}.{slug(library_ref)}.v1",
                "edition": 1,
                "owner_proposal_ref": proposal_id,
                "occurrence_ref": occurrence["occurrence_id"],
                "docket_ref": docket["docket_id"],
                "symbol_ref": docket["symbol_ref"],
                "library_ref": library_ref,
                "proposed_occurrence_relation": relation,
                "proposed_owner_ref": proposed_owner,
                "profile_candidates": occurrence["local_profile_candidates"],
                "confidence": confidence if relation != "UNRESOLVED" else "UNRESOLVED",
                "ratification_required": True,
                "ratification_receipt_ref": None,
                "canonical_mutation_allowed": False,
                "canonical_gaps_closed": 0,
                "status": "PROPOSED_UNRATIFIED" if relation != "UNRESOLVED" else "BLOCKED_PENDING_OWNER_EVIDENCE",
                "completion_claim": False,
            })
    return owner_rows, relation_rows, conflicts, counterfactual_rows


CHALLENGE_ONTOLOGY = {
    "COUNTERFACTUAL_INSTABILITY": {
        "semantic_axis_refs": ["evidence_and_conformance", "identity_and_equality"],
        "questions": [
            "Which non-lexical primary or dependency evidence establishes the owner?",
            "Does the proposed owner survive removal of every spelling-derived feature?",
        ],
    },
    "INCOMPLETE_CONTEXT_OWNER_MAP": {
        "semantic_axis_refs": ["bounded_context_and_ownership", "identity_and_equality", "scope_and_grain"],
        "questions": [
            "Which bounded context owns each distinct local meaning?",
            "Are uncovered contexts exact imports, profiled imports or qualified homonyms?",
        ],
    },
    "UNRESOLVED_SYMBOL_DISPOSITION": {
        "semantic_axis_refs": ["identity_and_equality", "representation_and_canonicalization", "compatibility_and_evolution"],
        "questions": [
            "Is the repeated spelling one carrier, a family carrier, a qualified homonym or an invalid duplicate?",
            "What equality, canonicalization and migration laws distinguish the alternatives?",
        ],
    },
    "IMPLEMENTATION_LOCUS_REJECTED": {
        "semantic_axis_refs": ["bounded_context_and_ownership", "effect_and_external_interaction", "evidence_and_conformance"],
        "questions": [
            "Which semantic contract does the implementation/provider boundary depend on?",
            "Where is the provider-neutral meaning owner and conformance oracle?",
        ],
    },
    "INSUFFICIENT_OWNER_SEPARATION": {
        "semantic_axis_refs": ["bounded_context_and_ownership", "identity_and_equality", "evidence_and_conformance"],
        "questions": [
            "What positive authority evidence distinguishes the leading owner from its peers?",
            "What counterexample falsifies each losing owner candidate?",
        ],
    },
}


def challenge_class(conflict: dict[str, Any], proposal: dict[str, Any], counterfactual: dict[str, Any]) -> str:
    if counterfactual["stability"] == "UNSTABLE":
        return "COUNTERFACTUAL_INSTABILITY"
    if conflict["conflict_kind"] == "PARTIAL_LOCAL_OWNER_SET":
        return "INCOMPLETE_CONTEXT_OWNER_MAP"
    if proposal["proposed_symbol_disposition"] == "UNRESOLVED":
        return "UNRESOLVED_SYMBOL_DISPOSITION"
    if "highest-ranked occurrence is an implementation/provider boundary" in conflict["details"]:
        return "IMPLEMENTATION_LOCUS_REJECTED"
    return "INSUFFICIENT_OWNER_SEPARATION"


def make_challenge_packages(
    conflicts: list[dict[str, Any]],
    dockets: list[dict[str, Any]],
    proposals: list[dict[str, Any]],
    counterfactuals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    docket_by_id = {row["docket_id"]: row for row in dockets}
    proposal_by_id = {row["proposal_id"]: row for row in proposals}
    counterfactual_by_proposal = {row["proposal_ref"]: row for row in counterfactuals}
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for conflict in conflicts:
        proposal = proposal_by_id[conflict["proposal_ref"]]
        docket = docket_by_id[conflict["docket_ref"]]
        category = challenge_class(conflict, proposal, counterfactual_by_proposal[proposal["proposal_id"]])
        grouped[(category, docket["research_route"], docket["research_archetype"])].append(conflict)
    packages = []
    for (category, route, archetype), members in sorted(grouped.items()):
        ontology = CHALLENGE_ONTOLOGY[category]
        members = sorted(members, key=lambda row: row["symbol_ref"])
        packages.append({
            "record_kind": "owner_adjudication_challenge_package",
            "challenge_package_id": f"challenge-package.p2.{slug(category)}.{slug(route)}.{slug(archetype)}.v1",
            "edition": 1,
            "challenge_class": category,
            "research_route": route,
            "research_archetype": archetype,
            "semantic_axis_refs": ontology["semantic_axis_refs"],
            "challenge_questions": ontology["questions"],
            "conflict_refs": [row["conflict_id"] for row in members],
            "proposal_refs": [row["proposal_ref"] for row in members],
            "docket_refs": [row["docket_ref"] for row in members],
            "symbol_refs": [row["symbol_ref"] for row in members],
            "member_count": len(members),
            "required_evidence": sorted({item for row in members for item in row["required_evidence"]}),
            "decision_grain": "PER_SYMBOL_AND_PER_EXACT_OCCURRENCE",
            "propagation_law": "Evidence and counterexamples may be reviewed once per package; no member inherits another member's owner, equality or occurrence disposition.",
            "ratification_required": True,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "OPEN_REVIEW_QUOTIENT",
            "completion_claim": False,
        })
    return packages


RATIFICATION_CONTRACT = {
    "contract_id": "contract.p2-owner-ratification-receipt.v1",
    "edition": 1,
    "required_receipt_fields": [
        "receipt_id",
        "input_snapshot_ref",
        "input_snapshot_sha256",
        "docket_ref",
        "symbol_ref",
        "chosen_symbol_disposition",
        "semantic_owner_refs_or_complete_local_owner_map",
        "definition_equality_lifecycle_contract_digest",
        "public_name_and_edition",
        "complete_occurrence_dispositions",
        "counterexample_appraisal_digest",
        "migration_plan_digest",
        "effective_at",
        "authority_refs",
        "attestation_ref",
    ],
    "refusal_conditions": [
        "input snapshot mismatch",
        "missing or unauthorized authority",
        "counterfactual instability remains open",
        "incomplete bounded-context owner map",
        "incomplete exact-occurrence disposition map",
        "definition, equality or lifecycle contract missing",
        "provider adapter or target backend selected as semantic owner",
        "migration relies on a permanent compatibility alias",
        "attestation is absent, expired, revoked or unverifiable",
    ],
    "non_claims": [
        "A completed template is not a ratification receipt.",
        "A ratified owner does not prove implementation, qualification, portability, product acceptance or vertical fitness.",
        "A proposal score is not authority evidence.",
    ],
}


def make_ratification_packet_templates(
    snapshot_record: dict[str, Any],
    dockets: list[dict[str, Any]],
    proposals: list[dict[str, Any]],
    counterfactuals: list[dict[str, Any]],
    occurrence_proposals: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    challenge_packages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    proposal_by_docket = {row["docket_ref"]: row for row in proposals}
    counterfactual_by_proposal = {row["proposal_ref"]: row for row in counterfactuals}
    conflicts_by_proposal = {row["proposal_ref"]: row for row in conflicts}
    package_by_proposal = {
        proposal_ref: package["challenge_package_id"]
        for package in challenge_packages
        for proposal_ref in package["proposal_refs"]
    }
    occurrences_by_proposal: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in occurrence_proposals:
        occurrences_by_proposal[row["owner_proposal_ref"]].append(row)
    role_by_route = {
        "CROSS_FAMILY_SHARED_OWNER_HYPOTHESIS_RESEARCH": "CROSS_FAMILY_SEMANTIC_AUTHORITY",
        "FAMILY_SHARED_OWNER_OR_LOCAL_IMPORT_RESEARCH": "FAMILY_SEMANTIC_AUTHORITY",
        "HOMONYM_OR_DEFINITION_CONFLICT_RESEARCH": "BOUNDED_CONTEXT_SEMANTIC_AUTHORITIES",
    }
    rows = []
    for docket in dockets:
        proposal = proposal_by_docket[docket["docket_id"]]
        counterfactual = counterfactual_by_proposal[proposal["proposal_id"]]
        conflict = conflicts_by_proposal.get(proposal["proposal_id"])
        challenge_ref = package_by_proposal.get(proposal["proposal_id"])
        occurrence_rows = sorted(
            occurrences_by_proposal[proposal["proposal_id"]],
            key=lambda row: row["occurrence_ref"],
        )
        ready = conflict is None and bool(proposal["proposed_owner_refs"]) and counterfactual["stability"] == "STABLE"
        rows.append({
            "record_kind": "owner_ratification_packet_template",
            "ratification_packet_id": f"ratification-template.p2.owner.{slug(docket['symbol_ref'])}.v1",
            "edition": 1,
            "ratification_contract_ref": RATIFICATION_CONTRACT["contract_id"],
            "input_snapshot_ref": snapshot_record["snapshot_id"],
            "input_snapshot_sha256": snapshot_record["aggregate_sha256"],
            "docket_ref": docket["docket_id"],
            "symbol_packet_ref": docket["symbol_packet_ref"],
            "symbol_ref": docket["symbol_ref"],
            "family_refs": docket["family_refs"],
            "proposal_ref": proposal["proposal_id"],
            "counterfactual_ref": counterfactual["counterfactual_id"],
            "conflict_ref": conflict["conflict_id"] if conflict else None,
            "challenge_package_ref": challenge_ref,
            "candidate_symbol_disposition": proposal["proposed_symbol_disposition"],
            "candidate_owner_refs": proposal["proposed_owner_refs"],
            "candidate_confidence": proposal["confidence"],
            "occurrence_relation_proposal_refs": [row["relation_proposal_id"] for row in occurrence_rows],
            "occurrence_count": len(occurrence_rows),
            "unresolved_occurrence_count": sum(row["proposed_occurrence_relation"] == "UNRESOLVED" for row in occurrence_rows),
            "required_authority_roles": [role_by_route[docket["research_route"]], "AFFECTED_LIBRARY_OWNERS"],
            "required_receipt_fields": RATIFICATION_CONTRACT["required_receipt_fields"],
            "submission": {
                "chosen_symbol_disposition": None,
                "semantic_owner_refs_or_complete_local_owner_map": None,
                "definition_equality_lifecycle_contract_digest": None,
                "public_name_and_edition": None,
                "complete_occurrence_dispositions": None,
                "counterexample_appraisal_digest": None,
                "migration_plan_digest": None,
                "effective_at": None,
                "authority_refs": None,
                "attestation_ref": None,
            },
            "ratification_required": True,
            "ratification_receipt_ref": None,
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "READY_FOR_NAMED_AUTHORITY_REVIEW" if ready else "BLOCKED_BY_CHALLENGE_PACKAGE",
            "completion_claim": False,
        })
    return rows


def outputs() -> dict[str, str]:
    snap = snapshot()
    dockets, occurrences, docket_by_packet = make_dockets()
    units = make_units(docket_by_packet)
    waves = make_waves(units, dockets, occurrences)
    owner_proposals, occurrence_proposals, proposal_conflicts, proposal_counterfactuals = make_proposals(dockets, occurrences)
    challenge_packages = make_challenge_packages(proposal_conflicts, dockets, owner_proposals, proposal_counterfactuals)
    ratification_templates = make_ratification_packet_templates(snap, dockets, owner_proposals, proposal_counterfactuals, occurrence_proposals, proposal_conflicts, challenge_packages)
    route_counts = collections.Counter(row["research_route"] for row in dockets)
    summary = {
        "program_id": "program.p2-public-symbol-owner-adjudication.v1",
        "edition": 1,
        "as_of": AS_OF,
        "input_snapshot": snap,
        "symbol_dockets": len(dockets),
        "represented_occurrences": len(occurrences),
        "owner_decision_units": len(units),
        "owner_decision_waves": len(waves),
        "owner_proposals": len(owner_proposals),
        "occurrence_relation_proposals": len(occurrence_proposals),
        "owner_proposals_with_named_candidates": sum(bool(row["proposed_owner_refs"]) for row in owner_proposals),
        "owner_proposals_blocked": sum(row["status"].startswith("BLOCKED") for row in owner_proposals),
        "occurrence_relation_proposals_unresolved": sum(row["proposed_occurrence_relation"] == "UNRESOLVED" for row in occurrence_proposals),
        "proposal_conflicts": len(proposal_conflicts),
        "proposal_counterfactuals": len(proposal_counterfactuals),
        "counterfactually_stable_owner_proposals": sum(row["stability"] == "STABLE" for row in proposal_counterfactuals),
        "counterfactually_unstable_owner_proposals": sum(row["stability"] == "UNSTABLE" for row in proposal_counterfactuals),
        "owner_adjudication_challenge_packages": len(challenge_packages),
        "ratification_packet_templates": len(ratification_templates),
        "ratification_packet_templates_ready_for_authority_review": sum(row["status"] == "READY_FOR_NAMED_AUTHORITY_REVIEW" for row in ratification_templates),
        "ratification_packet_templates_blocked": sum(row["status"] == "BLOCKED_BY_CHALLENGE_PACKAGE" for row in ratification_templates),
        "symbol_route_counts": dict(sorted(route_counts.items())),
        "symbols_with_bounded_primary_research": sum(row["research_state"] == "BOUNDED_PRIMARY_RESEARCH_COMPLETE" for row in dockets),
        "symbols_with_explicit_owner_hypotheses": sum(bool(row["candidate_owner_refs"]) for row in dockets),
        "symbols_with_disposition_hypotheses": sum(bool(row["disposition_hypotheses"]) for row in dockets),
        "ratified_symbol_owners": 0,
        "ratified_occurrence_dispositions": 0,
        "canonical_mutations_allowed": 0,
        "canonical_exact_gaps_closed": 0,
        "next_gate": "NAMED_OWNER_RATIFICATION_OF_SYMBOL_DISPOSITIONS_THEN_EXACT_OCCURRENCE_DISPOSITIONS",
        "completion_claim": False,
    }
    files = {
        "disposition-ontology.json": json.dumps(DISPOSITION_ONTOLOGY, sort_keys=True, indent=2) + "\n",
        "owner-adjudication-dockets.jsonl": "".join(canonical(row) + "\n" for row in dockets),
        "occurrence-disposition-candidates.jsonl": "".join(canonical(row) + "\n" for row in occurrences),
        "owner-decision-units.jsonl": "".join(canonical(row) + "\n" for row in units),
        "owner-decision-waves.jsonl": "".join(canonical(row) + "\n" for row in waves),
        "owner-proposals.jsonl": "".join(canonical(row) + "\n" for row in owner_proposals),
        "occurrence-relation-proposals.jsonl": "".join(canonical(row) + "\n" for row in occurrence_proposals),
        "proposal-conflicts.jsonl": "".join(canonical(row) + "\n" for row in proposal_conflicts),
        "owner-proposal-counterfactuals.jsonl": "".join(canonical(row) + "\n" for row in proposal_counterfactuals),
        "challenge-ontology.json": json.dumps(CHALLENGE_ONTOLOGY, sort_keys=True, indent=2) + "\n",
        "owner-adjudication-challenge-packages.jsonl": "".join(canonical(row) + "\n" for row in challenge_packages),
        "ratification-contract.json": json.dumps(RATIFICATION_CONTRACT, sort_keys=True, indent=2) + "\n",
        "owner-ratification-packet-templates.jsonl": "".join(canonical(row) + "\n" for row in ratification_templates),
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.p2-owner-adjudication.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text() != text:
                stale.append(name)
        else:
            path.write_text(text)
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = json.loads(outputs()["summary.json"])
    print(
        f"{'CHECK' if args.check else 'BUILD'} PASS P2: {summary['symbol_dockets']} symbol dockets, "
        f"{summary['represented_occurrences']} occurrences, {summary['owner_decision_units']} decision units; "
        f"{summary['owner_proposals_with_named_candidates']} named proposals remain unratified, "
        "zero canonical mutations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
