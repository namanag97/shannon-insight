#!/usr/bin/env python3
"""Validate messaging/channel corpus structure, references, semantics and drift."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import build_corpus


ROOT = Path(__file__).resolve().parent
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def type_matches(expected: str, value: Any) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, True)


def validate_schema(schema: dict[str, Any], value: Any, location: str) -> None:
    if "const" in schema and value != schema["const"]:
        fail(f"{location}: expected {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        fail(f"{location}: {value!r} outside enum")
    expected = schema.get("type")
    if expected and not type_matches(expected, value):
        fail(f"{location}: expected {expected}, got {type(value).__name__}")
        return
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            fail(f"{location}: string below minLength")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            fail(f"{location}: does not match {schema['pattern']!r}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            fail(f"{location}: too few items")
        if schema.get("uniqueItems"):
            normalized = [json.dumps(item, sort_keys=True) for item in value]
            if len(normalized) != len(set(normalized)):
                fail(f"{location}: duplicate items")
        for index, item in enumerate(value):
            if isinstance(schema.get("items"), dict):
                validate_schema(schema["items"], item, f"{location}[{index}]")
    if isinstance(value, dict):
        if len(value) < schema.get("minProperties", 0):
            fail(f"{location}: too few properties")
        for required in schema.get("required", []):
            if required not in value:
                fail(f"{location}: missing {required}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = set(value) - set(props)
            if extras:
                fail(f"{location}: unexpected fields {sorted(extras)}")
        for key, child in props.items():
            if key in value:
                validate_schema(child, value[key], f"{location}.{key}")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    try:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except Exception as error:
                fail(f"{path.name}:{number}: invalid JSON: {error}")
                continue
            if not isinstance(value, dict):
                fail(f"{path.name}:{number}: expected object")
            else:
                records.append(value)
    except FileNotFoundError:
        fail(f"missing {path}")
    return records


def ids(records: list[dict[str, Any]], field: str, label: str) -> set[str]:
    values = [record.get(field) for record in records]
    if any(not isinstance(value, str) or not value for value in values):
        fail(f"{label}: missing {field}")
    valid = [value for value in values if isinstance(value, str)]
    if len(valid) != len(set(valid)):
        fail(f"{label}: duplicate {field}")
    return set(valid)


def refs_exist(refs: list[str], valid: set[str], location: str) -> None:
    missing = set(refs) - valid
    if missing:
        fail(f"{location}: unresolved references {sorted(missing)}")


def validate() -> dict[str, Any]:
    for path, expected in sorted(build_corpus.render().items()):
        if not path.exists():
            fail(f"missing generated file {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            fail(f"generated drift in {path.relative_to(ROOT)}; run build_corpus.py")

    schemas = build_corpus.schemas()
    loaded: dict[str, list[dict[str, Any]]] = {}
    id_sets: dict[str, set[str]] = {}
    for filename, (schema_name, _, id_field) in build_corpus.REGISTRIES.items():
        records = load_jsonl(ROOT / filename)
        loaded[filename] = records
        for number, record in enumerate(records, 1):
            validate_schema(schemas[schema_name], record, f"{filename}:{number}")
        id_sets[filename] = ids(records, id_field, filename)

    sources = loaded["sources.jsonl"]
    contexts = loaded["bounded-context-candidates.jsonl"]
    capabilities = loaded["capabilities.jsonl"]
    operations = loaded["typed-operations.jsonl"]
    decisions = loaded["decision-points.jsonl"]
    channels = loaded["channel-contracts.jsonl"]
    distinctions = loaded["semantic-distinctions.jsonl"]
    guards = loaded["invariants-refusals.jsonl"]
    laws = loaded["delivery-composition-laws.jsonl"]
    lifecycle_records = loaded["lifecycles.jsonl"]
    reqs = loaded["compiler-requirements.jsonl"]
    offers = loaded["capability-offers.jsonl"]
    mappings = loaded["compiler-mappings.jsonl"]
    libraries = loaded["library-adapter-boundaries.jsonl"]
    boundaries = loaded["implementation-boundaries.jsonl"]
    qualifications = loaded["provider-qualification-requirements.jsonl"]
    innovation_records = loaded["innovations.jsonl"]
    evidence_records = loaded["evidence.jsonl"]
    gap_records = loaded["gaps.jsonl"]

    if len(sources) < 60:
        fail(f"source minimum: {len(sources)} < 60")
    if len(contexts) < 40:
        fail(f"bounded-context minimum: {len(contexts)} < 40")
    combined = len(capabilities) + len(operations) + len(decisions) + len(channels)
    if combined < 180:
        fail(f"capability/operation/decision/channel minimum: {combined} < 180")
    if len(operations) < 180:
        fail(f"typed operation minimum: {len(operations)} < 180")
    if len(innovation_records) < 20:
        fail(f"innovation minimum: {len(innovation_records)} < 20")
    if len(gap_records) < 20:
        fail(f"gap minimum: {len(gap_records)} < 20")

    exact_library_ids = {
        "msg.library.envelope_kernel",
        "msg.library.retained_log_contract",
        "msg.library.consumer_progress_contract",
    }
    exact_libraries = {row["library_id"]: row for row in libraries if row["library_id"] in exact_library_ids}
    if set(exact_libraries) != exact_library_ids:
        fail("missing exact envelope/log/progress library split")
    for library_id, row in exact_libraries.items():
        if row.get("status") != "specified" or len(row.get("public_types", [])) < 12:
            fail(f"{library_id}: exact public type contract missing")
        if set(row.get("operation_refs", [])) != {op.get("operation_ref") for op in row.get("operations", [])}:
            fail(f"{library_id}: exact operation signatures do not cover operation_refs")
        if len(row.get("decision_refs", [])) < 6 or len(row.get("laws", [])) < 5:
            fail(f"{library_id}: decisions or laws are incomplete")
    envelope_laws = " ".join(exact_libraries["msg.library.envelope_kernel"].get("laws", [])).lower()
    log_laws = " ".join(exact_libraries["msg.library.retained_log_contract"].get("laws", [])).lower()
    progress_laws = " ".join(exact_libraries["msg.library.consumer_progress_contract"].get("laws", [])).lower()
    if "metadata is not payload" not in envelope_laws or "position is scoped" not in log_laws or "transport progress is not" not in progress_laws:
        fail("critical envelope/log/progress non-collapse laws missing")

    source_ids = id_sets["sources.jsonl"]
    context_ids = id_sets["bounded-context-candidates.jsonl"]
    capability_ids = id_sets["capabilities.jsonl"]
    operation_ids = id_sets["typed-operations.jsonl"]
    decision_ids = id_sets["decision-points.jsonl"]
    guard_ids = id_sets["invariants-refusals.jsonl"]
    requirement_ids = id_sets["compiler-requirements.jsonl"]
    offer_ids = id_sets["capability-offers.jsonl"]

    allowed_kinds = {"standard", "specification", "official_oss_docs", "provider_documentation", "research_paper"}
    allowed_roles = {"normative_authority", "open_specification", "implementation_evidence", "provider_evidence", "original_research"}
    for item in sources:
        if item["source_kind"] not in allowed_kinds:
            fail(f"{item['source_id']}: unacceptable source kind")
        if item["evidence_role"] not in allowed_roles:
            fail(f"{item['source_id']}: unacceptable evidence role")
        parsed = urlparse(item["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            fail(f"{item['source_id']}: source URL is not HTTPS")
        if any(host in parsed.netloc for host in ("wikipedia.org", "reddit.com")):
            fail(f"{item['source_id']}: secondary/community source is forbidden")
        if item["evidence_role"] in {"implementation_evidence", "provider_evidence", "original_research"} and item["canonical_semantics"]:
            fail(f"{item['source_id']}: evidence must not claim canonical provider-neutral semantics")
    roles = {item["evidence_role"] for item in sources}
    if roles != allowed_roles:
        fail(f"evidence role coverage mismatch: {sorted(roles)}")
    if sum(1 for item in sources if item["evidence_role"] in {"normative_authority", "open_specification"}) < 30:
        fail("fewer than 30 normative/open specification sources")
    if sum(1 for item in sources if item["evidence_role"] == "original_research") < 8:
        fail("fewer than 8 foundational primary papers")
    if sum(1 for item in sources if item["evidence_role"] == "implementation_evidence") < 25:
        fail("fewer than 25 official implementation sources")

    for item in contexts:
        refs_exist(item["source_refs"], source_ids, item["context_id"])
        refs_exist(item["capability_refs"], capability_ids, item["context_id"])
        refs_exist(item["operation_refs"], operation_ids, item["context_id"])
        refs_exist([item["decision_ref"]], decision_ids, item["context_id"])
        refs_exist([item["guard_ref"]], guard_ids, item["context_id"])
        if item["llm_dependency"] != "none" or item["status"] != "candidate_not_adjudicated":
            fail(f"{item['context_id']}: invalid status or LLM dependency")
        if len(item["operation_refs"]) != 4 or len(item["capability_refs"]) != 2:
            fail(f"{item['context_id']}: expected four operations and two capabilities")

    context_ops = {item["context_id"]: set(item["operation_refs"]) for item in contexts}
    context_caps = {item["context_id"]: set(item["capability_refs"]) for item in contexts}
    for item in capabilities:
        refs_exist([item["owner_context"]], context_ids, item["capability_id"])
        refs_exist(item["operation_refs"], operation_ids, item["capability_id"])
        refs_exist(item["source_refs"], source_ids, item["capability_id"])
        if not set(item["operation_refs"]).issubset(context_ops[item["owner_context"]]):
            fail(f"{item['capability_id']}: cross-context operation ownership")
    for item in operations:
        refs_exist([item["owner_context"]], context_ids, item["operation_id"])
        refs_exist([item["capability_ref"]], capability_ids, item["operation_id"])
        refs_exist(item["source_refs"], source_ids, item["operation_id"])
        if item["capability_ref"] not in context_caps[item["owner_context"]]:
            fail(f"{item['operation_id']}: cross-context capability")
        if set(item["delivery_stage_effects"]) != {"producer_effect", "publication", "transport", "consumption", "downstream_effect"}:
            fail(f"{item['operation_id']}: missing separated delivery stages")
        if set(item["signature"]) != {"inputs", "output"}:
            fail(f"{item['operation_id']}: malformed signature")
    for item in decisions:
        refs_exist([item["owner_context"]], context_ids, item["decision_id"])
        refs_exist(item["affects_operations"], operation_ids, item["decision_id"])
        refs_exist(item["source_refs"], source_ids, item["decision_id"])
        if "No hidden default" not in item["default_law"]:
            fail(f"{item['decision_id']}: hidden defaults not forbidden")
    for item in channels:
        refs_exist([item["owner_context"]], context_ids, item["channel_id"])
        if "component-level" not in item["delivery_claim_ceiling"] or "end-to-end exactly once" not in item["delivery_claim_ceiling"]:
            fail(f"{item['channel_id']}: exactly-once ceiling missing")
    for item in guards:
        refs_exist([item["owner_context"]], context_ids, item["guard_id"])
        refs_exist(item["source_refs"], source_ids, item["guard_id"])
        refusal_codes = [refusal["code"] for refusal in item["refusals"]]
        if len(refusal_codes) != len(set(refusal_codes)):
            fail(f"{item['guard_id']}: duplicate refusal codes")
    for item in laws:
        refs_exist(item["source_refs"], source_ids, item["law_id"])
        if not item["counterexample_required"]:
            fail(f"{item['law_id']}: counterexample requirement absent")

    required_laws = {
        "msg.law.stage_separation", "msg.law.exactly_once_non_inference", "msg.law.end_to_end_exactly_once",
        "msg.law.ack_scope", "msg.law.dedup_scope", "msg.law.order_scope", "msg.law.retry_identity",
        "msg.law.redelivery_identity", "msg.law.replay_identity", "msg.law.time_non_substitution",
        "msg.law.dlq_non_correction", "msg.law.transaction_boundary",
    }
    if not required_laws.issubset(id_sets["delivery-composition-laws.jsonl"]):
        fail("critical delivery laws missing")
    exact_text = " ".join(item["statement"].lower() for item in laws)
    if "component-level exactly once must not be used as proof of end-to-end exactly once" not in exact_text:
        fail("explicit component/end-to-end exactly-once prohibition missing")

    for item in lifecycle_records:
        states = set(item["states"])
        events = set(item["events"])
        if item["initial_state"] not in states or not set(item["terminal_states"]).issubset(states):
            fail(f"{item['lifecycle_id']}: invalid initial/terminal state")
        seen = set()
        for transition in item["transitions"]:
            key = (transition.get("from"), transition.get("event"))
            if key in seen:
                fail(f"{item['lifecycle_id']}: nondeterministic transition {key}")
            seen.add(key)
            if transition.get("from") not in states or transition.get("to") not in states or transition.get("event") not in events:
                fail(f"{item['lifecycle_id']}: invalid transition")
        if item["undefined_transition"] != "REF_INVALID_STATE_TRANSITION" or "For every declared state and event" not in item["totality_law"]:
            fail(f"{item['lifecycle_id']}: lifecycle is not total by refusal")

    for item in reqs:
        refs_exist([item["owner_context"]], context_ids, item["requirement_id"])
        refs_exist(item["required_capabilities"], capability_ids, item["requirement_id"])
        refs_exist(item["required_decisions"], decision_ids, item["requirement_id"])
        refs_exist(item["source_refs"], source_ids, item["requirement_id"])
    for item in offers:
        refs_exist([item["satisfies_requirement"]], requirement_ids, item["offer_id"])
        refs_exist(item["claimed_capabilities"], capability_ids, item["offer_id"])
        refs_exist(item["source_refs"], source_ids, item["offer_id"])
        if item["status"] != "template_not_provider_claim":
            fail(f"{item['offer_id']}: offer template masquerades as provider claim")
    for item in mappings:
        refs_exist([item["requirement_ref"]], requirement_ids, item["mapping_id"])
        refs_exist([item["offer_ref"]], offer_ids, item["mapping_id"])
        if item["refusal"] != "REF_NO_QUALIFIED_MESSAGING_TARGET":
            fail(f"{item['mapping_id']}: missing deterministic target refusal")
    for item in libraries:
        refs_exist([item["semantic_owner_context"]], context_ids, item["library_id"])
        if item["library_kind"] == "pure_semantic_kernel" and "no I/O" not in item["effect_boundary"]:
            fail(f"{item['library_id']}: pure kernel permits effects")
    layer_set = {item["artifact_kind"] for item in boundaries}
    expected_layers = {"logical", "protocol", "broker_engine", "client_library", "provider_offer", "deployed_occurrence"}
    if layer_set != expected_layers:
        fail(f"artifact layer separation mismatch: {sorted(layer_set)}")
    for item in boundaries:
        refs_exist([item["semantic_owner_context"]], context_ids, item["boundary_id"])
    for item in qualifications:
        refs_exist(item["evidence_refs"], source_ids, item["qualification_id"])
        if item["status"] != "qualification_required_not_executed" or len(item["required_tests"]) < 8:
            fail(f"{item['qualification_id']}: qualification posture incomplete")
    for item in innovation_records:
        refs_exist(item["evidence_refs"], source_ids, item["innovation_id"])
        if not re.search(r"202[1-6]", item["period"]) or item["llm_dependency"] != "none":
            fail(f"{item['innovation_id']}: invalid time window or forbidden dependency")
    for item in evidence_records:
        refs_exist([item["source_ref"]], source_ids, item["evidence_id"])
        source_item = next(source for source in sources if source["source_id"] == item["source_ref"])
        if item["canonical_scope"] != source_item["canonical_semantics"]:
            fail(f"{item['evidence_id']}: canonical-scope mismatch")

    required_distinctions = {
        "msg.distinction.logical_protocol", "msg.distinction.protocol_broker", "msg.distinction.broker_client",
        "msg.distinction.offer_occurrence", "msg.distinction.message_business_key", "msg.distinction.partition_global_order",
        "msg.distinction.receipt_acceptance", "msg.distinction.retry_redelivery", "msg.distinction.redelivery_replay",
        "msg.distinction.dlq_quarantine", "msg.distinction.event_broker_processing_time",
    }
    if not required_distinctions.issubset(id_sets["semantic-distinctions.jsonl"]):
        fail("critical non-substitution distinctions missing")

    examples = []
    for filename in sorted(build_corpus.EXAMPLES):
        path = ROOT / filename
        try:
            examples.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as error:
            fail(f"{filename}: invalid example: {error}")
    normal = [item for item in examples if "twin_of" not in item]
    twins = [item for item in examples if "twin_of" in item]
    if {item.get("vertical") for item in normal} != {"commerce_order_fulfillment", "industrial_turbine_condition_monitoring"}:
        fail("two unrelated vertical examples missing")
    if len(twins) != 2 or {item.get("twin_of") for item in twins} != {item.get("example_id") for item in normal}:
        fail("failure twins do not close over vertical examples")

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.glob("*.jsonl"))
    forbidden = [r"large[ _-]?language[ _-]?model", r"\brag\b", r"agent[ _-]?memory", r"generative[ _-]?model"]
    for pattern in forbidden:
        if re.search(pattern, all_text, flags=re.IGNORECASE):
            fail(f"forbidden core dependency appears in JSONL: {pattern}")

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    report = json.loads((ROOT / "coverage-report.json").read_text(encoding="utf-8"))
    if manifest["counts"] != build_corpus.counts() or report["counts"] != build_corpus.counts():
        fail("manifest/report counts drift")
    if manifest["completion_claim"] or report["completion_claim"] or not gap_records:
        fail("corpus makes a false completeness claim")
    if manifest["status"] != "researched_candidate_not_adjudicated":
        fail("candidate status missing")

    return {
        "counts": build_corpus.counts(),
        "sources_by_role": {role: sum(1 for item in sources if item["evidence_role"] == role) for role in sorted(allowed_roles)},
        "artifact_layers": sorted(layer_set),
        "status": "PASS" if not ERRORS else "FAIL",
        "errors": ERRORS,
    }


def main() -> int:
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True))
    if ERRORS:
        for error in ERRORS:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
