#!/usr/bin/env python3
"""Validate structure, references, constitutional laws and useful scale."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


FILES = {
    "sources": ("sources.jsonl", "source_id"),
    "contexts": ("contexts.jsonl", "context_id"),
    "relations": ("relations.jsonl", "relation_id"),
    "acls": ("acl-decisions.jsonl", "acl_id"),
    "rules": ("loss-refusal-rules.jsonl", "rule_id"),
    "proofs": ("proof-obligations.jsonl", "proof_id"),
    "libraries": ("library-boundaries.jsonl", "library_id"),
    "requirements": ("requirements.jsonl", "requirement_id"),
    "offers": ("offers.jsonl", "offer_id"),
    "mappings": ("compiler-mappings.jsonl", "mapping_id"),
    "innovations": ("innovations-2021-2026.jsonl", "innovation_id"),
    "gaps": ("gaps.jsonl", "gap_id"),
    "paths": ("vertical-paths.jsonl", "path_id"),
    "alignments": ("input-alignments.jsonl", "alignment_id"),
}


MINIMUMS = {
    "sources": 60, "contexts": 80, "relations": 250, "acls": 250,
    "rules": 40, "proofs": 20, "libraries": 25, "requirements": 25,
    "offers": 25, "mappings": 25, "innovations": 15, "gaps": 20, "paths": 4,
    "alignments": 20,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_jsonl(filename: str, id_key: str) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    path = ROOT / filename
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"{filename}:{number}: invalid JSON: {exc}")
        if id_key not in record or not isinstance(record[id_key], str) or not record[id_key]:
            fail(f"{filename}:{number}: missing {id_key}")
        records.append(record)
    ids = [record[id_key] for record in records]
    if len(ids) != len(set(ids)):
        duplicates = [key for key, count in Counter(ids).items() if count > 1]
        fail(f"{filename}: duplicate identities: {duplicates[:5]}")
    if records != sorted(records, key=lambda record: record[id_key]):
        fail(f"{filename}: records are not in deterministic {id_key} order")
    return records, {record[id_key]: record for record in records}


def has_cycle(edges: list[tuple[str, str]]) -> bool:
    graph: dict[str, list[str]] = defaultdict(list)
    for left, right in edges:
        graph[left].append(right)
    done: set[str] = set()
    active: set[str] = set()

    def visit(node: str) -> bool:
        if node in active:
            return True
        if node in done:
            return False
        active.add(node)
        for target in graph.get(node, []):
            if visit(target):
                return True
        active.remove(node)
        done.add(node)
        return False

    return any(visit(node) for node in list(graph))


def validate_schema_required(records: dict[str, list[dict[str, Any]]]) -> None:
    schema_map = {
        "sources": "source", "contexts": "context", "relations": "relation", "acls": "acl",
        "rules": "rule", "proofs": "proof", "libraries": "library", "requirements": "requirement",
        "offers": "offer", "mappings": "compiler_mapping", "innovations": "innovation",
        "gaps": "gap", "paths": "vertical_path",
        "alignments": "input_alignment",
    }
    for key, schema_name in schema_map.items():
        schema = json.loads((ROOT / "schemas" / f"{schema_name}.schema.json").read_text(encoding="utf-8"))
        for idx, record in enumerate(records[key], 1):
            missing = [field for field in schema["required"] if field not in record]
            if missing:
                fail(f"{FILES[key][0]}:{idx}: schema-required fields absent: {missing}")


def validate() -> dict[str, Any]:
    records: dict[str, list[dict[str, Any]]] = {}
    indexes: dict[str, dict[str, dict[str, Any]]] = {}
    for key, (filename, id_key) in FILES.items():
        records[key], indexes[key] = load_jsonl(filename, id_key)
        if len(records[key]) < MINIMUMS[key]:
            fail(f"{key}: useful-scale gate {MINIMUMS[key]} not met; found {len(records[key])}")

    validate_schema_required(records)
    metamodel = json.loads((ROOT / "metamodel.json").read_text(encoding="utf-8"))
    allowed_relations = set(metamodel["relationship_types"])
    source_ids = set(indexes["sources"])
    context_ids = set(indexes["contexts"])
    acl_ids = set(indexes["acls"])
    proof_ids = set(indexes["proofs"])
    library_ids = set(indexes["libraries"])
    requirement_ids = set(indexes["requirements"])
    offer_ids = set(indexes["offers"])

    if len({source["url"] for source in records["sources"]}) != len(records["sources"]):
        fail("source URLs must be unique")
    for source in records["sources"]:
        if not source["url"].startswith("https://"):
            fail(f"non-HTTPS source URL: {source['source_id']}")
        if not source["authority_scope"] or not source["limitations"]:
            fail(f"source lacks authority scope or limitations: {source['source_id']}")

    languages: set[str] = set()
    import_contracts: set[str] = set()
    export_contracts: set[str] = set()
    planes: set[str] = set()
    for context in records["contexts"]:
        if context["status"] != "candidate_open_world" or context.get("completion_claim") is not False:
            fail(f"context makes non-candidate or completion claim: {context['context_id']}")
        owner = context["semantic_owner"]
        if owner.get("inferred_from_name") is not False:
            fail(f"owner must not be inferred from name: {context['context_id']}")
        if owner.get("owner_kind") in {"product", "suite", "provider", "deployment_occurrence"}:
            fail(f"packager/provider illegally owns semantics: {context['context_id']}")
        if str(owner.get("owner_id", "")).startswith(("product.", "provider.", "suite.")):
            fail(f"owner id illegally names packager/provider: {context['context_id']}")
        if not context["positive_charter"] or not context["negative_charter"]:
            fail(f"context lacks positive/negative charter: {context['context_id']}")
        planes.add(context["plane_id"])
        for language in context["published_languages"]:
            languages.add(language["language_id"])
        for item in context["imports"]:
            import_contracts.add(item["contract_id"])
            if item["from_context_id"] not in context_ids or item["acl_decision_id"] not in acl_ids:
                fail(f"unresolved context import: {context['context_id']}")
        for item in context["export_contracts"]:
            export_contracts.add(item["contract_id"])
            if item["to_context_id"] not in context_ids:
                fail(f"unresolved context export: {context['context_id']}")
        for source_id in context["evidence_refs"]:
            if source_id not in source_ids:
                fail(f"unresolved context evidence {source_id}: {context['context_id']}")
    if len(planes) < 20:
        fail(f"major-plane coverage too thin: {len(planes)}")

    relation_acl_pairs = set()
    totality_counts = Counter()
    preservation_counts = Counter()
    relation_type_counts = Counter()
    for relation in records["relations"]:
        source = relation["source"]["context_id"]
        target = relation["target"]["context_id"]
        if source not in context_ids or target not in context_ids or source == target:
            fail(f"invalid relation endpoints: {relation['relation_id']}")
        if relation["relationship_type"] not in allowed_relations:
            fail(f"unknown DDD relationship type: {relation['relation_id']}")
        if relation["semantic_owner_context_id"] != source:
            fail(f"relation silently transfers semantic ownership: {relation['relation_id']}")
        if relation.get("contributes_semantic_ownership_edge") is not False:
            fail(f"context-map crossing must not create a semantic ownership edge: {relation['relation_id']}")
        if relation["published_language_id"] not in languages:
            fail(f"unresolved published language: {relation['relation_id']}")
        if relation["import_contract_id"] not in import_contracts or relation["export_contract_id"] not in export_contracts:
            fail(f"unresolved import/export contract: {relation['relation_id']}")
        if relation["acl_decision_id"] not in acl_ids:
            fail(f"unresolved ACL: {relation['relation_id']}")
        for proof_id in relation["proof_obligation_ids"]:
            if proof_id not in proof_ids:
                fail(f"unresolved relation proof {proof_id}: {relation['relation_id']}")
        translation = relation["translation"]
        totality_counts[translation["totality"]] += 1
        preservation_counts[translation["information_preservation"]] += 1
        relation_type_counts[relation["relationship_type"]] += 1
        if translation["totality"] != "total" and "refuse_unhandled_foreign_value" not in relation["failure_refusals"]:
            fail(f"partial relation lacks refusal: {relation['relation_id']}")
        if translation["losses"] and "refuse_undeclared_information_loss" not in relation["failure_refusals"]:
            fail(f"lossy relation lacks refusal: {relation['relation_id']}")
        relation_acl_pairs.add((relation["relation_id"], relation["acl_decision_id"]))
    if len(relation_type_counts) < 10:
        fail(f"DDD relation vocabulary coverage too thin: {relation_type_counts}")
    if set(totality_counts) != {"total", "partial", "conditional"}:
        fail(f"translation totality axis incomplete: {totality_counts}")

    for acl in records["acls"]:
        pair = (acl["relation_id"], acl["acl_id"])
        if pair not in relation_acl_pairs:
            fail(f"orphan or mismatched ACL: {acl['acl_id']}")
        if acl["foreign_context_id"] not in context_ids or acl["local_context_id"] not in context_ids:
            fail(f"ACL endpoint missing: {acl['acl_id']}")
        if acl["totality"] != "total" and "refuse_unhandled_foreign_value" not in acl["refusals"]:
            fail(f"partial ACL lacks refusal: {acl['acl_id']}")
        if acl["declared_losses"] and not acl["information_preservation"].startswith(("loss", "evidence", "identity")):
            fail(f"ACL loss posture inconsistent: {acl['acl_id']}")

    for kind, projection in (("authority_delegation", "authority_delegation"), ("compiler_requirement", "compiler_dependency")):
        edges = [
            (r["source"]["context_id"], r["target"]["context_id"])
            for r in records["relations"] if r["cycle_projection"] == projection
        ]
        if has_cycle(edges):
            fail(f"forbidden {kind} cycle detected")

    if has_cycle([(lib["dependencies"][0], lib["library_id"]) for lib in records["libraries"] if lib["dependencies"]]):
        fail("library dependency cycle detected")
    for lib in records["libraries"]:
        for dependency in lib["dependencies"]:
            if dependency not in library_ids:
                fail(f"unresolved library dependency: {lib['library_id']} -> {dependency}")
        if any("provider" in owner for owner in lib["must_not_own"]) is False:
            fail(f"library boundary lacks provider non-ownership law: {lib['library_id']}")

    for offer in records["offers"]:
        if offer["library_id"] not in library_ids:
            fail(f"offer library missing: {offer['offer_id']}")
    for mapping in records["mappings"]:
        if mapping["requirement_id"] not in requirement_ids or mapping["offer_id"] not in offer_ids or mapping["library_id"] not in library_ids:
            fail(f"compiler mapping reference missing: {mapping['mapping_id']}")
        for proof_id in mapping["proof_obligation_ids"]:
            if proof_id not in proof_ids:
                fail(f"compiler mapping proof missing: {mapping['mapping_id']} -> {proof_id}")

    for innovation in records["innovations"]:
        if not 2021 <= innovation["year"] <= 2026 or innovation["non_llm"] is not True:
            fail(f"innovation window/non-LLM rule violated: {innovation['innovation_id']}")
        if innovation.get("source_id") not in source_ids:
            fail(f"innovation primary source not in source inventory: {innovation['innovation_id']}")

    inherited_candidates = {
        record["record_id"]
        for record in (
            json.loads(line) for line in (ROOT.parent / "registry/context-candidates.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()
        )
    }
    for alignment in records["alignments"]:
        if alignment["local_context_id"] not in context_ids or alignment["input_candidate_id"] not in inherited_candidates:
            fail(f"input alignment reference missing: {alignment['alignment_id']}")
        if alignment["synonymy_inferred"] is not False or alignment["owner_inherited"] is not False:
            fail(f"input alignment illegally infers synonymy/ownership: {alignment['alignment_id']}")

    vertical_polarities = defaultdict(set)
    for path in records["paths"]:
        for context_id in path["context_path"]:
            if context_id not in context_ids:
                fail(f"vertical path context missing: {path['path_id']} -> {context_id}")
        for proof_id in path["required_proofs"]:
            if proof_id not in proof_ids:
                fail(f"vertical path proof missing: {path['path_id']} -> {proof_id}")
        vertical_polarities[path["vertical"]].add(path["polarity"])
        if path["polarity"] == "negative_twin" and (not path.get("expected_refusal") or path.get("exact_boundary") not in context_ids):
            fail(f"negative twin lacks exact refusal boundary: {path['path_id']}")
    if len(vertical_polarities) < 2 or any(values != {"positive", "negative_twin"} for values in vertical_polarities.values()):
        fail(f"need unrelated positive paths and negative twins: {dict(vertical_polarities)}")

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    for filename, expected in manifest["artifacts"].items():
        actual = hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()
        if actual != expected:
            fail(f"manifest hash mismatch: {filename}")
    expected_counts = manifest["counts"]
    manifest_key = {
        "sources": "sources", "contexts": "contexts", "relations": "relations", "acls": "acl_decisions",
        "rules": "loss_refusal_rules", "proofs": "proof_obligations", "libraries": "library_boundaries",
        "requirements": "requirements", "offers": "offers", "mappings": "compiler_mappings",
        "innovations": "innovations", "gaps": "gaps", "paths": "vertical_paths",
        "alignments": "input_alignments",
    }
    for key, rows in records.items():
        if expected_counts[manifest_key[key]] != len(rows):
            fail(f"manifest count mismatch: {key}")

    return {
        "counts": {key: len(value) for key, value in records.items()},
        "planes": len(planes),
        "relation_types": dict(sorted(relation_type_counts.items())),
        "translation_totality": dict(sorted(totality_counts.items())),
        "information_preservation": dict(sorted(preservation_counts.items())),
        "verticals": sorted(vertical_polarities),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--determinism", action="store_true", help="also run the generator in stale-artifact check mode")
    args = parser.parse_args()
    report = validate()
    if args.determinism:
        subprocess.run([sys.executable, str(ROOT / "build_corpus.py"), "--check"], check=True)
    print("PASS candidate global context-map corpus")
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
