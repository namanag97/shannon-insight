#!/usr/bin/env python3
"""Dependency-free integrity validator with optional Draft 2020-12 validation."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import build_corpus as build


ROOT = Path(__file__).resolve().parent
STATUS = "candidate_pending_review"

FILES = {
    "evidence-sources.jsonl": "evidence-source.schema.json",
    "bounded-context-candidates.jsonl": "bounded-context-candidate.schema.json",
    "ubiquitous-language-candidates.jsonl": "ubiquitous-language-candidate.schema.json",
    "capability-operation-candidates.jsonl": "capability-operation-candidate.schema.json",
    "decision-point-candidates.jsonl": "decision-point-candidate.schema.json",
    "invariants-refusals.jsonl": "invariant-refusal-candidate.schema.json",
    "context-relations-acls.jsonl": "context-relation-acl-candidate.schema.json",
    "compiler-mappings.jsonl": "compiler-mapping-candidate.schema.json",
    "library-boundaries.jsonl": "library-boundary-candidate.schema.json",
    "retired-compositions.jsonl": "library-replacement-candidate.schema.json",
    "external-universe-mappings.jsonl": "external-universe-mapping-candidate.schema.json",
    "vertical-cases.jsonl": "vertical-case-candidate.schema.json",
    "innovations-2021-2026.jsonl": "innovation-candidate.schema.json",
    "coverage-gaps.jsonl": "coverage-gap-candidate.schema.json",
}


def validate_manifest() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["completion_claim"] is False
    for name, claim in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name


def load_jsonl(path: Path) -> list[dict]:
    records = []
    for line_no, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            raise AssertionError(f"{path.name}:{line_no}: blank JSONL line")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise AssertionError(f"{path.name}:{line_no}: record is not an object")
        records.append(value)
    return records


def assert_unique(records: list[dict], key: str, filename: str) -> None:
    values = [r[key] for r in records]
    duplicates = [value for value, count in Counter(values).items() if count > 1]
    assert not duplicates, f"{filename}: duplicate {key}: {duplicates[:8]}"


def assert_acyclic(edges: dict[str, list[str]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            raise AssertionError("library dependency cycle: " + " -> ".join([*trail, node]))
        if node in visited:
            return
        visiting.add(node)
        for dep in edges.get(node, []):
            visit(dep, [*trail, node])
        visiting.remove(node)
        visited.add(node)

    for node in edges:
        visit(node, [])


def main() -> None:
    validate_manifest()
    # Rebuild once, then rebuild again and prove byte-for-byte deterministic JSONL/schema/report output.
    subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], check=True)
    generated = [ROOT / name for name in FILES] + sorted((ROOT / "schemas").glob("*.json")) + [ROOT / "coverage-report.json"]
    first = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in generated}
    subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], check=True)
    second = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in generated}
    assert first == second, "generator output is not deterministic"

    corpus = {name: load_jsonl(ROOT / name) for name in FILES}
    for filename, records in corpus.items():
        assert records, f"{filename}: empty registry"
        assert all(r.get("status") == STATUS for r in records), f"{filename}: non-candidate status"

    sources = corpus["evidence-sources.jsonl"]
    contexts = corpus["bounded-context-candidates.jsonl"]
    terms = corpus["ubiquitous-language-candidates.jsonl"]
    candidates = corpus["capability-operation-candidates.jsonl"]
    decisions = corpus["decision-point-candidates.jsonl"]
    invariants = corpus["invariants-refusals.jsonl"]
    relations = corpus["context-relations-acls.jsonl"]
    mappings = corpus["compiler-mappings.jsonl"]
    libraries = corpus["library-boundaries.jsonl"]
    replacements = corpus["retired-compositions.jsonl"]
    bridges = corpus["external-universe-mappings.jsonl"]
    verticals = corpus["vertical-cases.jsonl"]
    innovations = corpus["innovations-2021-2026.jsonl"]

    for filename, key in [
        ("evidence-sources.jsonl", "source_id"),
        ("bounded-context-candidates.jsonl", "context_id"),
        ("ubiquitous-language-candidates.jsonl", "term_id"),
        ("capability-operation-candidates.jsonl", "candidate_id"),
        ("decision-point-candidates.jsonl", "decision_id"),
        ("invariants-refusals.jsonl", "invariant_id"),
        ("context-relations-acls.jsonl", "relation_id"),
        ("compiler-mappings.jsonl", "mapping_id"),
        ("library-boundaries.jsonl", "library_id"),
        ("retired-compositions.jsonl", "replacement_id"),
        ("external-universe-mappings.jsonl", "mapping_id"),
        ("vertical-cases.jsonl", "case_id"),
        ("innovations-2021-2026.jsonl", "innovation_id"),
        ("coverage-gaps.jsonl", "gap_id"),
    ]:
        assert_unique(corpus[filename], key, filename)

    source_ids = {r["source_id"] for r in sources}
    context_ids = {r["context_id"] for r in contexts}
    candidate_ids = {r["candidate_id"] for r in candidates}
    capability_ids = {r["candidate_id"] for r in candidates if r["candidate_kind"] == "capability"}
    operation_ids = {r["candidate_id"] for r in candidates if r["candidate_kind"] == "typed_operation"}
    bridge_ids = {r["mapping_id"] for r in bridges}

    assert len(sources) >= 45
    assert len(contexts) >= 35
    assert len(candidates) + len(decisions) >= 150
    assert len(innovations) >= 20
    assert len(verticals) >= 2
    assert len(terms) >= 50

    # Required evidence diversity.
    assert sum(r["issuer"].startswith("W3C") or r["issuer"] == "W3C and OGC" for r in sources) >= 10
    assert sum("ISO" in r["issuer"] for r in sources) >= 8
    assert sum(r["issuer"] == "Object Management Group" or "OMG" in r["title"] for r in sources) >= 4
    assert sum(r["source_kind"] in {"industry_standard", "regulatory_standard", "intergovernmental_standard"} for r in sources) >= 10
    assert sum(r["source_kind"] == "official_oss_documentation" for r in sources) >= 10
    assert sum(r["source_kind"] == "research_article" for r in sources) >= 4

    for context in contexts:
        assert context["evidence_refs"], context["context_id"]
        assert set(context["evidence_refs"]) <= source_ids, context["context_id"]
        assert set(context["owns"]).isdisjoint(context["explicitly_excludes"]), context["context_id"]

    for term in terms:
        assert term["owning_context"] in context_ids, term["term_id"]
        assert set(term["evidence_refs"]) <= source_ids, term["term_id"]
        assert term["must_not_be_conflated_with"], term["term_id"]
    assert len({r["homonym_group"] for r in terms}) >= 20

    operations_by_context: dict[str, set[str]] = defaultdict(set)
    for candidate in candidates:
        assert candidate["owner_context"] in context_ids, candidate["candidate_id"]
        assert set(candidate["evidence_refs"]) <= source_ids, candidate["candidate_id"]
        if candidate["candidate_kind"] == "typed_operation":
            assert candidate["signature"]["inputs"] and candidate["signature"]["outputs"]
            assert candidate["refusals"]
            operations_by_context[candidate["owner_context"]].add(candidate["candidate_id"])
        else:
            assert set(candidate["provides_operations"]) <= operation_ids, candidate["candidate_id"]
    assert all(len(operations_by_context[c]) >= 4 for c in context_ids)

    for invariant in invariants:
        assert invariant["owner_context"] in context_ids, invariant["invariant_id"]
        assert invariant["compiler_refusal"], invariant["invariant_id"]
    for relation in relations:
        assert relation["source_context"] in context_ids, relation["relation_id"]
        assert relation["target_context"] in context_ids, relation["relation_id"]
        assert relation["write_default"] == "deny", relation["relation_id"]
    for bridge in bridges:
        assert set(bridge["source_contexts"]) <= context_ids, bridge["mapping_id"]
        assert bridge["on_no_unique_match"] == "emit gmo.context.compiler_gap"
    for mapping in mappings:
        assert mapping["offer"]["capability_id"] in capability_ids, mapping["mapping_id"]
        assert mapping["offer"]["owner_context"] in context_ids, mapping["mapping_id"]
        assert set(mapping["external_mapping_refs"]) <= bridge_ids, mapping["mapping_id"]
        assert mapping["typed_failures"], mapping["mapping_id"]

    library_ids = {r["library_id"] for r in libraries}
    central_library_path = ROOT.parent.parent / "compiler/library_registry/library-contributions.jsonl"
    external_library_ids = {r["library_id"] for r in load_jsonl(central_library_path)} if central_library_path.exists() else set()
    owned_contexts: list[str] = []
    covered_contexts: list[str] = []
    for library in libraries:
        slug = library["library_id"].removeprefix("gmo.library.")
        assert len(library["owns_contexts"]) == 1, library["library_id"]
        assert set(library["owns_contexts"]) <= context_ids, library["library_id"]
        assert set(library.get("contributes_to_context_refs", [])) <= context_ids, library["library_id"]
        assert set(library["allowed_dependencies"]) <= library_ids | external_library_ids, library["library_id"]
        owned_contexts.extend(library["owns_contexts"])
        covered_contexts.extend(library["owns_contexts"])
        covered_contexts.extend(library.get("contributes_to_context_refs", []))
        if slug in build.GMO_EXACT_SPLIT_APIS:
            assert library.get("public_types"), library["library_id"]
            assert library.get("public_traits"), library["library_id"]
            assert library.get("operations"), library["library_id"]
            for operation in library["operations"]:
                assert operation.get("operation_ref"), library["library_id"]
                assert operation.get("input_types"), library["library_id"]
                assert operation.get("output_type"), library["library_id"]
                assert operation.get("refusal_types"), library["library_id"]
                assert operation.get("purity") == "pure", library["library_id"]
    for replacement in replacements:
        retired_local_ref = "gmo.library." + replacement["retired_library_ref"].removeprefix("library.gmo.")
        assert retired_local_ref not in library_ids, replacement["replacement_id"]
        assert set(replacement["covered_context_refs"]) <= context_ids, replacement["replacement_id"]
        assert set(replacement["replacement_library_refs"]) <= external_library_ids, replacement["replacement_id"]
        assert replacement["compatibility_alias_permitted"] is False, replacement["replacement_id"]
        covered_contexts.extend(replacement["covered_context_refs"])
    # One context may publish several independently changeable libraries; the
    # invariant is one semantic owner per library, not one library per context.
    assert set(owned_contexts) <= context_ids
    assert set(covered_contexts) == context_ids, f"library context coverage mismatch: {sorted(context_ids - set(covered_contexts))}"
    assert_acyclic({r["library_id"]: [dep for dep in r["allowed_dependencies"] if dep in library_ids] for r in libraries})

    for vertical in verticals:
        assert set(vertical["required_contexts"]) <= context_ids, vertical["case_id"]
        assert set(vertical["evidence_refs"]) <= source_ids, vertical["case_id"]
    for innovation in innovations:
        assert 2021 <= innovation["year"] <= 2026
        assert innovation["source_ref"] in source_ids, innovation["innovation_id"]

    # Exact source-system IDs are validated when the neighboring registry exists. Selectors such
    # as shape.* remain explicit candidates and are refused until a registry edition is pinned.
    source_registry = ROOT.parent / "source_systems" / "source-classes.jsonl"
    if source_registry.exists():
        external_source_ids = {r["class_id"] for r in load_jsonl(source_registry)}
        referenced = set()
        for vertical in verticals:
            referenced.update(v for v in vertical["source_system_candidates"] if v.startswith("source."))
        for bridge in bridges:
            if bridge["target_universe"] == "source_system":
                referenced.update(v for v in bridge["target_candidates_or_selectors"] if v.startswith("source."))
        assert referenced <= external_source_ids, f"unknown source-system IDs: {sorted(referenced - external_source_ids)}"

    # The core may record an exclusion boundary, but core context/capability identities may not
    # adopt generative/LLM method vocabulary.
    forbidden = {"llm", "large_language_model", "prompt", "rag", "agent_memory", "generative_model"}
    core_identity_text = "\n".join(
        [r["context_id"] for r in contexts] + [r["candidate_id"] for r in candidates] + [r["library_id"] for r in libraries]
    ).lower()
    identity_tokens = set(re.split(r"[^a-z0-9]+", core_identity_text))
    assert not (identity_tokens & forbidden), sorted(identity_tokens & forbidden)

    schema_validation = "not installed"
    try:
        import jsonschema

        for filename, schema_name in FILES.items():
            schema = json.loads((ROOT / "schemas" / schema_name).read_text())
            jsonschema.Draft202012Validator.check_schema(schema)
            validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
            for line_no, record in enumerate(corpus[filename], start=1):
                errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
                assert not errors, f"{filename}:{line_no}: {errors[0].message}"
        schema_validation = "Draft 2020-12 passed"
    except ImportError:
        pass

    report = json.loads((ROOT / "coverage-report.json").read_text())
    assert all(report["minimum_checks"].values()), report["minimum_checks"]
    for filename, records in corpus.items():
        assert report["counts"][filename] == len(records), filename
        digest = "sha256:" + hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()
        assert report["registry_sha256"][filename] == digest, filename

    summary = report["summary"]
    print("governance/metadata/ontology/MDM corpus validation passed")
    print(f"sources={summary['sources']}")
    print(f"bounded_contexts={summary['bounded_contexts']}")
    print(f"capabilities={summary['capabilities']}")
    print(f"typed_operations={summary['typed_operations']}")
    print(f"decision_points={len(decisions)}")
    print(f"capability_operation_decision_total={summary['capability_operation_decision_total']}")
    print(f"terms={len(terms)}")
    print(f"invariants_refusals={len(invariants)}")
    print(f"context_relations_acls={len(relations)}")
    print(f"compiler_mappings={len(mappings)}")
    print(f"library_boundaries={len(libraries)}")
    print(f"retired_composite_libraries={len(replacements)}")
    print(f"external_universe_mappings={len(bridges)}")
    print(f"vertical_cases={summary['vertical_cases']}")
    print(f"recent_innovations={summary['recent_innovations']}")
    print(f"coverage_gaps={len(corpus['coverage-gaps.jsonl'])}")
    print(f"all_candidate_records={summary['all_candidate_records']}")
    print(f"schema_validation={schema_validation}")
    print("deterministic_rebuild=passed")


if __name__ == "__main__":
    main()
