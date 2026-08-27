#!/usr/bin/env python3
"""Validate the candidate consumption, BI and visualization universe."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema"


def load_jsonl(name: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{line_no}: invalid JSON: {exc}") from exc
        assert isinstance(value, dict), f"{name}:{line_no}: record must be an object"
        records.append(value)
    return records


def load_json(name: str) -> dict[str, Any]:
    value = json.loads((ROOT / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict), f"{name}: must be an object"
    return value


def require_unique(records: list[dict[str, Any]], field: str, label: str) -> set[str]:
    values = [record[field] for record in records]
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    assert not duplicates, f"{label}: duplicate {field}: {duplicates}"
    return set(values)


def evidence_refs(records: list[dict[str, Any]]) -> set[str]:
    result: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "evidence_refs":
                    assert isinstance(child, list)
                    result.update(child)
                else:
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(records)
    return result


def validate_schema(records: list[dict[str, Any]], schema_name: str, label: str) -> None:
    schema = load_json(f"schema/{schema_name}")
    required = set(schema["required"])
    allowed = set(schema["properties"])
    for index, record in enumerate(records, 1):
        missing = required - set(record)
        extra = set(record) - allowed
        assert not missing, f"{label}:{index}: missing fields {sorted(missing)}"
        assert not extra, f"{label}:{index}: extra fields {sorted(extra)}"
    try:
        import jsonschema
    except ImportError:
        return
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for index, record in enumerate(records, 1):
        errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
        if errors:
            details = "; ".join(f"{list(error.path)}: {error.message}" for error in errors[:5])
            raise AssertionError(f"{label}:{index}: {details}")


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("cbv_build_corpus", ROOT / "build_corpus.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = load_generator()
    registries: dict[str, list[dict[str, Any]]] = {}
    ids_by_file: dict[str, set[str]] = {}
    for name, (_, id_field, schema_name) in module.REGISTRIES.items():
        records = load_jsonl(name)
        validate_schema(records, schema_name, name)
        registries[name] = records
        ids_by_file[name] = require_unique(records, id_field, name)

    sources = registries["sources.jsonl"]
    contexts = registries["context-candidates.jsonl"]
    capabilities = registries["capabilities.jsonl"]
    presentations = registries["presentation-contracts.jsonl"]
    interactions = registries["interaction-contracts.jsonl"]
    decisions = registries["decision-points.jsonl"]
    bindings = registries["requirements-offers-bindings.jsonl"]
    mappings = registries["compiler-mappings.jsonl"]
    libraries = registries["library-boundaries.jsonl"]
    retired_compositions = registries["retired-library-compositions.jsonl"]
    cross_maps = registries["cross-domain-mappings.jsonl"]
    invariants = registries["invariants-refusals.jsonl"]
    innovations = registries["innovations.jsonl"]
    gaps = registries["gaps.jsonl"]

    source_ids = ids_by_file["sources.jsonl"]
    context_ids = ids_by_file["context-candidates.jsonl"]
    capability_ids = ids_by_file["capabilities.jsonl"]
    decision_ids = ids_by_file["decision-points.jsonl"]

    # Requested quantitative floors.  Capabilities and decisions are separately counted so a
    # context name cannot masquerade as an operation surface.
    assert len(sources) >= 45, "45+ authoritative primary sources required"
    assert len(contexts) >= 35, "35+ bounded contexts required"
    assert len(capabilities) + len(decisions) >= 150, "150+ capabilities/operations/decision points required"
    assert len(capabilities) >= 150, "150+ typed capabilities required independently"
    assert len(innovations) >= 20, "20+ recent innovations required"
    assert len({source["url"] for source in sources}) == len(sources), "source URLs must be unique"
    assert {source["source_kind"] for source in sources} >= {"standard", "official_spec", "official_docs", "official_implementation", "paper"}
    assert sum(source["source_kind"] == "paper" for source in sources) >= 10
    assert sum(source["source_kind"] == "standard" for source in sources) >= 25

    # Referential closure and evidence use.
    all_evidence = evidence_refs([record for name, records in registries.items() if name != "sources.jsonl" for record in records])
    assert not (all_evidence - source_ids), f"unknown evidence refs: {sorted(all_evidence - source_ids)}"
    assert len(all_evidence) >= 60, "at least 60 sources must materially support non-source records"
    assert all(
        record["status"] == ("retired_composition" if name == "retired-library-compositions.jsonl" else "candidate")
        for name, records in registries.items() if name != "sources.jsonl" for record in records
    )
    assert all(source["status"] == "candidate_evidence" for source in sources)

    assert all(set(context["capability_refs"]) <= capability_ids for context in contexts)
    assert all(set(context["decision_refs"]) <= decision_ids for context in contexts)
    assert all(capability["context_ref"] in context_ids for capability in capabilities)
    assert all(set(capability["decision_refs"]) <= decision_ids for capability in capabilities)
    assert all(contract["owner_context_ref"] in context_ids for contract in presentations + interactions)
    assert all(decision["context_ref"] in context_ids for decision in decisions)
    assert all(binding["context_ref"] in context_ids for binding in bindings)
    assert all(set(mapping["consulted_context_refs"]) <= context_ids for mapping in mappings)
    assert all(set(library["contributes_to_context_refs"]) <= context_ids for library in libraries)
    assert all(set(library["capability_refs"]) <= capability_ids for library in libraries)
    assert all(mapping["local_context_ref"] in context_ids for mapping in cross_maps)
    assert all(set(invariant["applies_to_context_refs"]) <= context_ids for invariant in invariants)
    assert all(gap["context_ref"] in context_ids for gap in gaps)

    # Every context has exactly one decision and four operations in this edition, but the open
    # universe may extend by adding records in a future edition.
    capabilities_by_context = Counter(capability["context_ref"] for capability in capabilities)
    decisions_by_context = Counter(decision["context_ref"] for decision in decisions)
    assert set(capabilities_by_context) == context_ids and all(count == 4 for count in capabilities_by_context.values())
    assert set(decisions_by_context) == context_ids and all(count == 1 for count in decisions_by_context.values())
    assert all(capability["refusals"] for capability in capabilities)
    assert all(capability["information_loss"] and capability["batch_live_posture"] for capability in capabilities)

    required_context_locals = {
        "semantic_query", "olap_model", "pivot_spec", "dashboard_definition", "dashboard_runtime",
        "report_definition", "report_snapshot", "visual_grammar", "visual_encoding", "notebook_document",
        "execution_kernel", "exploratory_session", "self_service", "alert_rule", "notification_delivery",
        "subscription", "embedded_analytics", "analytics_api", "export", "governed_sharing", "annotation",
        "story", "accessibility", "localization", "mobile_offline", "interaction_state",
        "session_reproducibility", "client_cache", "source_finality", "decision_handoff",
    }
    assert {f"context.cbv.{local}" for local in required_context_locals} <= context_ids

    # Required cross-plane exchanges.
    required_external_domains = {
        "semantic_formula", "query_kernel", "quality", "lineage", "governance", "security_privacy",
        "decisions_actions", "product_truth", "source_systems", "runtime_compute_resource",
        "persistence_lakehouse", "pipeline_dataflow", "encoding_compression", "data_shapes",
    }
    assert required_external_domains <= {mapping["external_domain"] for mapping in cross_maps}
    assert all(mapping["compiler_exchange"] == ["typed requirement", "qualified offer", "decision receipt", "gap on incompatibility"] for mapping in cross_maps)

    # The ten non-collapsible identities have executable refusals, not prose-only notes.
    required_invariants = {
        "invariant.cbv.semantic_visual_split", "invariant.cbv.result_state_split",
        "invariant.cbv.dashboard_case_split", "invariant.cbv.report_live_split",
        "invariant.cbv.alert_delivery_split", "invariant.cbv.export_share_split",
        "invariant.cbv.notebook_kernel_split", "invariant.cbv.access_style_split",
        "invariant.cbv.explanation_evidence_split", "invariant.cbv.cache_finality_split",
    }
    assert required_invariants <= ids_by_file["invariants-refusals.jsonl"]
    assert len({record["refusal_code"] for record in invariants}) == len(invariants)

    # Contract and library separation.
    assert all(contract["contract_kind"] == "presentation" and contract.get("distinction_preserved") for contract in presentations)
    assert all(contract["contract_kind"] == "interaction" and contract.get("meaning") and contract.get("state_transition") for contract in interactions)
    assert {library["layer"] for library in libraries} == {"pure", "runtime"}
    assert sum(library["layer"] == "pure" for library in libraries) >= 15
    assert sum(library["layer"] == "runtime" for library in libraries) >= 10
    assert all("provider names do not define canonical semantics" in library["forbidden_ownership"] for library in libraries)
    assert all(binding["offer_contract"]["provider_names_are_nonsemantic"] is True for binding in bindings)
    assert all("accessibility_posture" in binding["requirement"] for binding in bindings)

    # A risk-ranked closure item exposed a false boundary: export planning, encoding, delivery and
    # report-snapshot lifecycle have different owners/effects and must not survive as one facade.
    library_by_id = {library["library_id"]: library for library in libraries}
    split = next(item for item in retired_compositions if item["retired_library_id"] == "library.cbv.export_writer")
    assert split["no_compatibility_alias"] is True
    assert "library.cbv.export_writer" not in library_by_id
    assert set(split["replacement_library_refs"]) == {
        "library.cbv.export_plan", "library.cbv.export_encoder",
        "library.cbv.export_delivery_port", "library.cbv.report_snapshot_reducer",
    }
    assert set(split["replacement_library_refs"]) <= set(library_by_id)
    assert set(split["capability_partition"]) == set(split["replacement_library_refs"])
    assert set(split["delegated_capability_refs"]) == {"capability.cbv.export.sign_export"}
    assert all(library_by_id[ref].get("semantic_owner_ref") in {"context.cbv.export", "context.cbv.report_snapshot"} for ref in split["replacement_library_refs"])
    for ref in split["replacement_library_refs"]:
        library = library_by_id[ref]
        assert library.get("public_types") and library.get("public_traits") and library.get("operations")
        assert library.get("error_contracts") and library.get("laws") and library.get("oracles")
        assert all(operation["refusal_types"] for operation in library["operations"])

    # Case lifecycle, decision handoff, archive semantics/storage, client caching and analytical
    # content versioning are independently owned contracts.  The retired facades must never
    # return as aliases, and every replacement must expose an executable exact API.
    expected_splits = {
        "library.cbv.decision_case": {
            "library.cbv.analytical_case_reducer", "library.cbv.decision_handoff_algebra",
            "library.cbv.case_archive_manifest",
        },
        "library.cbv.case_archive_store": {
            "library.cbv.case_archive_manifest", "library.cbv.case_archive_store_port",
            "library.cbv.content_versioning_algebra",
        },
        "library.cbv.cache_identity": {
            "library.cbv.client_cache_algebra", "library.cbv.content_versioning_algebra",
        },
    }
    retired_by_id = {item["retired_library_id"]: item for item in retired_compositions}
    assert expected_splits.keys() <= retired_by_id.keys()
    for retired_id, replacements in expected_splits.items():
        decision = retired_by_id[retired_id]
        assert retired_id not in library_by_id
        assert decision["no_compatibility_alias"] is True
        assert set(decision["replacement_library_refs"]) == replacements
        assert set(decision["capability_partition"]) == replacements
        assert replacements <= set(library_by_id)
        for ref in replacements:
            library = library_by_id[ref]
            assert library.get("semantic_owner_ref") in library["contributes_to_context_refs"]
            assert library.get("public_types") and library.get("public_traits")
            assert library.get("operations") and library.get("error_contracts")
            assert library.get("laws") and library.get("oracles")
            assert all(operation["refusal_types"] for operation in library["operations"])
    handoff = library_by_id["library.cbv.decision_handoff_algebra"]
    assert handoff["effect_boundary"] == "pure_effect_intents"
    assert all(operation["purity"] == "pure" for operation in handoff["operations"])
    assert any(operation["effect_intent_type"] == "ActionRequestIntent" for operation in handoff["operations"])
    archive_store = library_by_id["library.cbv.case_archive_store_port"]
    assert archive_store["effect_boundary"] == "effectful_runtime"
    assert any(operation["purity"] == "effectful_explicit" for operation in archive_store["operations"])

    # Innovations are recent, source-backed and explicitly outside the excluded method family.
    assert all(2021 <= innovation["year"] <= 2026 for innovation in innovations)
    assert all(innovation["non_llm"] is True and innovation["evidence_refs"] for innovation in innovations)

    # No core dispatch or contract may acquire prompt/model/agentic semantics.  The innovation
    # boolean is intentionally excluded from this scan because its field name records quarantine.
    forbidden = re.compile(r"(?i)\b(prompt|retrieval.augmented|agentic|agent[_ -]?memory|large language|generative model)\b")
    for label, records in [
        ("contexts", contexts), ("capabilities", capabilities), ("presentations", presentations),
        ("interactions", interactions), ("decisions", decisions), ("bindings", bindings),
        ("mappings", mappings), ("libraries", libraries), ("cross_maps", cross_maps),
    ]:
        for index, record in enumerate(records, 1):
            assert not forbidden.search(json.dumps(record)), f"{label}:{index}: forbidden core method dependency"

    # The checked-in outputs must be the exact deterministic projection of build_corpus.py.
    for name, (expected, _, _) in module.REGISTRIES.items():
        assert registries[name] == expected, f"{name}: stale or nondeterministic generated output"
    assert load_json("metamodel.json") == module.METAMODEL, "metamodel.json is stale"

    manifest = load_json("manifest.json")
    actual_counts = {
        "sources": len(sources), "bounded_context_candidates": len(contexts),
        "capabilities_operations": len(capabilities), "presentation_contracts": len(presentations),
        "interaction_contracts": len(interactions), "decision_points": len(decisions),
        "requirements_offer_bindings": len(bindings), "compiler_mappings": len(mappings),
        "library_boundaries": len(libraries), "retired_library_compositions": len(retired_compositions),
        "cross_domain_mappings": len(cross_maps),
        "invariants_refusals": len(invariants), "innovations_2021_2026": len(innovations), "open_gaps": len(gaps),
    }
    assert manifest["counts"] == actual_counts, "manifest counts are stale"
    assert manifest["completion_claim"] is False and manifest["status"] == "candidate"
    coverage = load_json("coverage-report.json")
    assert coverage["counts"] == actual_counts and all(coverage["threshold_results"].values())

    print(
        "PASS consumption-bi-visualization universe: "
        f"{len(sources)} sources ({len(all_evidence)} used), {len(contexts)} contexts, "
        f"{len(capabilities)} capabilities, {len(decisions)} decisions, "
        f"{len(presentations)} presentation + {len(interactions)} interaction contracts, "
        f"{len(bindings)} bindings, {len(mappings)} compiler mappings, {len(libraries)} libraries, "
        f"{len(retired_compositions)} retired compositions, "
        f"{len(cross_maps)} cross-maps, {len(invariants)} invariants/refusals, "
        f"{len(innovations)} innovations, {len(gaps)} gaps"
    )


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
