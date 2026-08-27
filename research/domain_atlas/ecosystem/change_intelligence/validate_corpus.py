#!/usr/bin/env python3
"""Validate referential integrity and anti-overclaim laws for the corpus."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
ATLAS = ROOT.parents[1]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise AssertionError(f"{path.name}:{line_no}: invalid JSON: {error}") from error
        assert isinstance(value, dict), f"{path.name}:{line_no}: record must be an object"
        rows.append(value)
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = load_json(ROOT / "manifest.json")
    metamodel = load_json(ROOT / "metamodel.json")
    assert manifest["completion_claim"] is False
    assert metamodel["completion_claim"] is False
    assert "does not prove" in manifest["false_completeness_posture"].lower()

    datasets = {}
    for name, expected_count in manifest["counts"].items():
        path = ROOT / f"{name}.jsonl"
        rows = load_jsonl(path)
        datasets[name] = rows
        assert len(rows) == expected_count, f"{name}: count drift"
        schema = load_json(ROOT / "schemas" / f"{name}.schema.json")
        required = schema["required"]
        for index, row in enumerate(rows, 1):
            missing = [field for field in required if field not in row]
            assert not missing, f"{name}:{index}: missing {missing}"
            identity = next(field for field in required if field.endswith("_id") and field in row)
            assert isinstance(row[identity], str) and row[identity], f"{name}:{index}: invalid identity"

    extension_root = ROOT / "extensions" / "llm_agent"
    extension_datasets = {}
    for name, expected_count in manifest["optional_extension_counts"].items():
        rows = load_jsonl(extension_root / f"{name}.jsonl")
        extension_datasets[name] = rows
        assert len(rows) == expected_count, f"extension/{name}: count drift"
        schema = load_json(extension_root / "schemas" / f"{name}.schema.json")
        for index, row in enumerate(rows, 1):
            missing = [field for field in schema["required"] if field not in row]
            assert not missing, f"extension/{name}:{index}: missing {missing}"

    for relative, expected_digest in manifest["file_sha256"].items():
        assert sha256(ROOT / relative) == expected_digest, f"digest drift: {relative}"

    identity_fields = {
        "monitored-subjects": "subject_id", "sources": "source_id",
        "source-occurrences": "source_occurrence_id", "change-types": "change_type_id",
        "collection-runs": "collection_run_id", "collection-attempts": "collection_attempt_id",
        "candidate-signals": "signal_id", "verified-change-events": "change_event_id",
        "claims-evidence": "claim_id", "coverage-proof-mappings": "coverage_mapping_id",
        "impact-mappings": "impact_mapping_id", "review-decisions": "review_decision_id",
        "migration-invalidation-triggers": "trigger_id",
        "security-availability-tradeoffs": "tradeoff_id", "watchlist": "watch_id",
        "supersession": "supersession_id", "innovations": "innovation_id",
        "gaps": "gap_id", "offer-observations": "offer_observation_id",
        "recurring-schedules": "schedule_id",
    }
    for name, identity in identity_fields.items():
        values = [row[identity] for row in datasets[name]]
        assert len(values) == len(set(values)), f"{name}: duplicate {identity}"

    plane_ids = {row["plane_id"] for row in load_jsonl(ATLAS / "coverage-planes.jsonl")}
    proof_ids = {row["proof_id"] for row in load_json(ATLAS / "compiler" / "proof-obligations.json")["proofs"]}
    source_ids = {row["source_id"] for row in datasets["sources"]}
    subject_ids = {row["subject_id"] for row in datasets["monitored-subjects"]}
    occurrence_ids = {row["source_occurrence_id"] for row in datasets["source-occurrences"]}
    signal_ids = {row["signal_id"] for row in datasets["candidate-signals"]}
    event_ids = {row["change_event_id"] for row in datasets["verified-change-events"]}
    type_ids = {row["change_type_id"] for row in datasets["change-types"]}
    trigger_ids = {row["trigger_id"] for row in datasets["migration-invalidation-triggers"]}

    for name, rows in datasets.items():
        for index, row in enumerate(rows, 1):
            planes = set(row.get("coverage_plane_ids", []))
            if row.get("coverage_plane_id"):
                planes.add(row["coverage_plane_id"])
            proofs = set(row.get("proof_obligation_ids", []))
            assert planes <= plane_ids, f"{name}:{index}: unknown planes {planes - plane_ids}"
            assert proofs <= proof_ids, f"{name}:{index}: unknown proofs {proofs - proof_ids}"
            assert set(row.get("source_ids", [])) <= source_ids, f"{name}:{index}: unknown source"
            assert set(row.get("subject_ids", [])) <= subject_ids, f"{name}:{index}: unknown subject"
            if row.get("signal_id") is not None:
                assert row["signal_id"] in signal_ids, f"{name}:{index}: unknown signal"

    def all_strings(value: object):
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            for item in value:
                yield from all_strings(item)
        elif isinstance(value, dict):
            for item in value.values():
                yield from all_strings(item)

    assert not any(
        text.startswith(("extension_signal.", "extension_capability.", "effect_state."))
        for rows in datasets.values() for row in rows for text in all_strings(row)
    ), "deterministic core contains a reverse dependency on optional LLM/agent extension"

    for source in datasets["sources"]:
        parsed = urlparse(source["canonical_url"])
        assert parsed.scheme == "https" and parsed.netloc, f"invalid URL: {source['source_id']}"
        assert source["authority_tier"] == "primary"
        assert source["digest_posture"] != "verified_digest" or source["content_digest"]
        assert source["coverage_plane_ids"] and source["proof_obligation_ids"]

    for occurrence in datasets["source-occurrences"]:
        assert occurrence["source_id"] in source_ids
        assert occurrence["subject_id"] in subject_ids

    mapped_planes = {row["coverage_plane_id"] for row in datasets["coverage-proof-mappings"]}
    assert mapped_planes == plane_ids, f"plane coverage mismatch: missing={sorted(plane_ids-mapped_planes)} extra={sorted(mapped_planes-plane_ids)}"
    assert all(row["proof_obligation_ids"] for row in datasets["coverage-proof-mappings"])
    sources_by_id = {row["source_id"]: row for row in datasets["sources"]}
    for mapping in datasets["coverage-proof-mappings"]:
        assert any(
            mapping["coverage_plane_id"] in sources_by_id[source_id]["coverage_plane_ids"]
            for source_id in mapping["source_ids"]
        ), f"{mapping['coverage_mapping_id']}: source is not scoped to mapped plane"

    signals = {row["signal_id"]: row for row in datasets["candidate-signals"]}
    events_by_signal = {signal_id: row for row in datasets["verified-change-events"] for signal_id in row["signal_ids"]}
    impacts_by_signal = defaultdict(list)
    for row in datasets["impact-mappings"]:
        impacts_by_signal[row["signal_id"]].append(row)
    decisions_by_signal = defaultdict(list)
    for row in datasets["review-decisions"]:
        if row["signal_id"]:
            decisions_by_signal[row["signal_id"]].append(row)
        assert set(row["revisit_trigger_ids"]) <= trigger_ids

    for signal_id, signal in signals.items():
        assert signal["coverage_plane_ids"], f"{signal_id}: no coverage plane"
        assert signal["proof_obligation_ids"], f"{signal_id}: no proof obligation"
        assert set(signal["change_type_ids"]) <= type_ids
        assert signal["canonical_semantics_authority"] is False
        assert signal["release_vs_rollout"] == "release_or_documentation_observed_deployment_not_observed"
        assert impacts_by_signal[signal_id], f"{signal_id}: missing impact mapping"
        assert decisions_by_signal[signal_id], f"{signal_id}: missing review decision"
        if signal["admission_status"] not in {"watchlist", "quarantined_llm"}:
            assert signal_id in events_by_signal, f"{signal_id}: admitted without verified event"
        if signal["admission_status"] == "quarantined_llm":
            assert signal["llm_posture"] == "llm_specific"
            assert signal_id not in events_by_signal, f"{signal_id}: LLM wrapper leaked into verified core"
    assert all(signal["llm_posture"] != "llm_specific" for signal in signals.values())

    for event in datasets["verified-change-events"]:
        assert set(event["signal_ids"]) <= signal_ids
        assert event["canonical_semantics_authority"] is False
        assert event["deployed_rollout_status"] == "not_observed"
        assert event["verification_status"] == "primary_source_claim_verified"

    required_supplied = {
        "signal.google_spark_image_cutover", "signal.google_spark_cluster_recreation",
        "signal.openmetadata_dynamic_sampling", "signal.openmetadata_mcp_pagination",
        "signal.openmetadata_databricks_auth", "signal.snowflake_iceberg_v3_ingest",
        "signal.snowflake_iceberg_benchmark", "signal.fabric_runtime_2",
        "signal.snowflake_period", "signal.snowflake_sandbox_substrate",
        "signal.snowflake_automation_substrate",
        "signal.snowflake_restricted_stage_substrate", "signal.snowflake_dcr_iceberg",
        "signal.dbt_sqlparse_floor", "signal.dbt_azure_artifact_fix", "signal.sqlparse_cve",
        "signal.dagster_sensor_dry_run", "signal.cloudera_gpu_spark",
        "signal.redpanda_26_2_operator", "signal.redpanda_compaction_correctness",
        "signal.cube_tesseract_ga",
        "signal.typeorm_write_safety", "signal.typeorm_uuid_advisory",
    }
    assert required_supplied <= signal_ids, f"supplied signals missing: {required_supplied-signal_ids}"

    extension_metamodel = load_json(extension_root / "metamodel.json")
    assert extension_metamodel["optional"] is True
    assert extension_metamodel["dependency_direction"] == "extension_imports_deterministic_core"
    assert extension_metamodel["forbidden_reverse_dependency"] is True
    extension_signals = {row["extension_signal_id"]: row for row in extension_datasets["change-signals"]}
    required_extension_signals = {
        "extension_signal.snowflake_agent_code_wrapper",
        "extension_signal.snowflake_coco_wrapper",
        "extension_signal.snowflake_parse_wrapper",
        "extension_signal.cube_ai_wrappers",
        "extension_signal.openmetadata_mcp_wrapper",
    }
    assert required_extension_signals <= set(extension_signals)
    extension_capability_ids = {row["extension_capability_id"] for row in extension_datasets["capabilities"]}
    for row in extension_signals.values():
        assert row["extension_namespace"] == "llm_agent_optional"
        assert row["dependency_direction"] == "extension_imports_deterministic_core"
        assert row["canonical_semantics_authority"] is False
        assert row["release_vs_rollout"] == "release_or_documentation_observed_deployment_not_observed"
        assert row["documentation_vs_behavior"] == "behavior_requires_deployed_or_conformance_evidence"
        assert row["qualified_provider_offer"] is False
        assert set(row["source_ids"]) <= source_ids
        assert set(row["capability_ids"]) <= extension_capability_ids
        assert set(row["core_substrate_signal_ids"]) <= signal_ids
        assert set(row["coverage_plane_ids"]) <= plane_ids
        assert set(row["proof_obligation_ids"]) <= proof_ids
    for row in extension_datasets["substrate-mappings"]:
        assert row["extension_signal_id"] in extension_signals
        assert set(row["extension_capability_ids"]) <= extension_capability_ids
        assert set(row["core_substrate_signal_ids"]) <= signal_ids
        assert row["dependency_direction"] == "extension_imports_deterministic_core"
        assert row["forbidden_reverse_dependency"] is True
    effect_states = {row["effect_state_id"]: row for row in extension_datasets["effect-state-kinds"]}
    required_effect_states = {
        "effect_state.model_output", "effect_state.agent_plan", "effect_state.validated_claim",
        "effect_state.authorized_tool_intent", "effect_state.effect_receipt",
    }
    assert set(effect_states) == required_effect_states
    assert effect_states["effect_state.model_output"]["does_not_imply_state_ids"]
    assert effect_states["effect_state.authorized_tool_intent"]["does_not_imply_state_ids"] == ["effect_state.effect_receipt"]
    assert effect_states["effect_state.effect_receipt"]["receipt_required"] is True
    for row in extension_datasets["review-decisions"]:
        assert row["extension_signal_id"] in extension_signals
        assert set(row["required_effect_state_ids"]) == required_effect_states

    attempts_by_run = defaultdict(list)
    for attempt in datasets["collection-attempts"]:
        assert attempt["collection_run_id"] in {row["collection_run_id"] for row in datasets["collection-runs"]}
        assert attempt["source_occurrence_id"] in occurrence_ids
        attempts_by_run[attempt["collection_run_id"]].append(attempt)
        if attempt["outcome"] == "failure":
            assert attempt["failure_class"]
            assert attempt["interpretation"] == "observability_gap_not_evidence_of_no_change"
            assert attempt["content_changed"] is None
    for run in datasets["collection-runs"]:
        attempts = attempts_by_run[run["collection_run_id"]]
        feed = [row for row in attempts if ".feed." in row["collection_attempt_id"]]
        manual = [row for row in attempts if ".manual." in row["collection_attempt_id"]]
        assert len(feed) == run["feed_attempts"] == 40
        assert sum(row["failure_class"] == "dns_resolution" for row in feed) == run["dns_failures"] == 40
        assert sum(row["outcome"] == "success" for row in feed) == run["feed_successes"] == 0
        assert len(manual) == run["manual_pages_opened"] == 30
        assert run["no_news_claim"] is False

    assert any(row["decision_effect"] == "exploit_not_proven" for row in datasets["change-types"])
    assert any(row["decision_effect"] == "independent_confirmation_missing" for row in datasets["change-types"])
    assert any(row["decision_effect"] == "not_qualified_offer" for row in datasets["change-types"])
    assert all(row["qualified_offer"] is False and not row["qualification_receipt_ids"] for row in datasets["offer-observations"])
    assert all(row["prior_evidence_retained"] is True and row["automatic_semantic_replacement"] is False for row in datasets["supersession"])

    innovations = datasets["innovations"]
    recent_non_llm = [row for row in innovations if 2021 <= row["year"] <= 2026 and row["llm_dependency"] == "none"]
    assert len(recent_non_llm) >= 20
    assert all(row["canonical_semantics_authority"] is False for row in innovations)

    primary_count = sum(row["authority_tier"] == "primary" for row in datasets["sources"])
    source_subject_count = len(datasets["sources"]) + len(datasets["monitored-subjects"])
    decision_mapping_count = (
        len(datasets["change-types"]) + len(datasets["review-decisions"])
        + len(datasets["coverage-proof-mappings"]) + len(datasets["impact-mappings"])
    )
    assert primary_count >= manifest["quality_gates"]["authoritative_primary_sources_min"]
    assert source_subject_count >= manifest["quality_gates"]["source_subject_records_min"]
    assert decision_mapping_count >= manifest["quality_gates"]["change_type_decision_mapping_records_min"]
    assert len(mapped_planes) == manifest["quality_gates"]["coverage_planes_exact"]

    exact_counts = {name: len(rows) for name, rows in sorted(datasets.items())}
    summary = {
        "status": "PASS", "record_counts": exact_counts,
        "authoritative_primary_sources": primary_count,
        "source_subject_records": source_subject_count,
        "change_type_decision_mapping_records": decision_mapping_count,
        "coverage_planes_mapped": len(mapped_planes),
        "proof_obligations_referenced": len({p for rows in datasets.values() for row in rows for p in row.get("proof_obligation_ids", [])}),
        "innovations_2021_2026_non_llm": len(recent_non_llm),
        "dns_failures_preserved_as_gaps": sum(row["failure_class"] == "dns_resolution" for row in datasets["collection-attempts"]),
        "admitted_signals": sum(row["admission_status"].startswith("admitted") for row in datasets["candidate-signals"]),
        "core_llm_specific_signals": sum(row["llm_posture"] == "llm_specific" for row in datasets["candidate-signals"]),
        "optional_extension_signals": len(extension_signals),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
