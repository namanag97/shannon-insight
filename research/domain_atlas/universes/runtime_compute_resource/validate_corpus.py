#!/usr/bin/env python3
"""Dependency-free structural and semantic checks for the runtime/resource corpus."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parents[1] / "compiler"
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def load_json(name: str) -> object:
    try:
        return json.loads((ROOT / name).read_text())
    except Exception as exc:  # noqa: BLE001
        fail(f"{name}: invalid JSON: {exc}")
        return {}


def load_jsonl(name: str) -> list[dict]:
    rows: list[dict] = []
    for line_no, line in enumerate((ROOT / name).read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            fail(f"{name}:{line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            fail(f"{name}:{line_no}: record is not an object")
            continue
        rows.append(value)
    return rows


def require(row: dict, fields: list[str], source: str) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        fail(f"{source}: missing fields {missing}")


def unique(rows: list[dict], field: str, source: str) -> set[str]:
    values = [row.get(field) for row in rows]
    bad = [value for value, count in Counter(values).items() if value is None or count != 1]
    if bad:
        fail(f"{source}: null or duplicate {field}: {bad}")
    return {value for value in values if isinstance(value, str)}


def validate_schema_records(schema_name: str, rows: list[dict], source: str) -> None:
    schema = load_json(f"schemas/{schema_name}")
    if not isinstance(schema, dict) or not isinstance(schema.get("required"), list):
        fail(f"{schema_name}: invalid schema contract")
        return
    required = set(schema["required"])
    for line_number, row in enumerate(rows, 1):
        missing = required - set(row)
        if missing:
            fail(f"{source}:{line_number}: schema-required fields missing: {sorted(missing)}")


before_rebuild = {str(path.relative_to(ROOT)): path.read_bytes() for path in ROOT.rglob("*.json*")}
completed_rebuild = subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], capture_output=True, text=True, check=False)
after_rebuild = {str(path.relative_to(ROOT)): path.read_bytes() for path in ROOT.rglob("*.json*")}
if completed_rebuild.returncode != 0 or before_rebuild != after_rebuild:
    fail("deterministic rebuild drift or builder failure")


manifest = load_json("manifest.json")
compiler = load_json("compiler-contract.json")
boundary = load_json("boundary-matrix.json")
contexts = load_jsonl("contexts.jsonl")
types = load_jsonl("types.jsonl")
machines = load_jsonl("state-machines.jsonl")
resources = load_jsonl("resource-classes.jsonl")
policies = load_jsonl("scheduling-policies.jsonl")
decisions = load_jsonl("decision-points.jsonl")
libraries = load_jsonl("libraries.jsonl")
bindings = load_jsonl("requirements-offers-bindings.jsonl")
evidence = load_jsonl("evidence.jsonl")
innovations = load_jsonl("innovations.jsonl")
gaps = load_jsonl("gaps.jsonl")

validate_schema_records("context.schema.json", contexts, "contexts.jsonl")
validate_schema_records("runtime-type.schema.json", types, "types.jsonl")
validate_schema_records("state-machine.schema.json", machines, "state-machines.jsonl")
validate_schema_records("resource-class.schema.json", resources, "resource-classes.jsonl")

if not isinstance(manifest, dict) or manifest.get("completion_claim") is not False:
    fail("manifest must explicitly state completion_claim=false")
if not isinstance(compiler, dict) or len(compiler.get("ir_stages", [])) < 8:
    fail("compiler contract must define at least eight IR stages")
if not isinstance(boundary, dict) or len(boundary.get("rows", [])) < 7:
    fail("boundary matrix must separate at least seven semantic/physical layers")

context_ids = unique(contexts, "context_id", "contexts.jsonl")
type_ids = unique(types, "type_id", "types.jsonl")
machine_ids = unique(machines, "state_machine_id", "state-machines.jsonl")
resource_ids = unique(resources, "resource_class_id", "resource-classes.jsonl")
policy_ids = unique(policies, "policy_id", "scheduling-policies.jsonl")
decision_ids = unique(decisions, "decision_id", "decision-points.jsonl")
library_ids = unique(libraries, "library_id", "libraries.jsonl")
evidence_ids = unique(evidence, "evidence_id", "evidence.jsonl")
innovation_ids = unique(innovations, "innovation_id", "innovations.jsonl")
gap_ids = unique(gaps, "gap_id", "gaps.jsonl")

minimums = manifest.get("minimum_gates", {}) if isinstance(manifest, dict) else {}
for label, rows, key in [
    ("contexts", contexts, "contexts"),
    ("state machines", machines, "state_machines"),
    ("resource classes", resources, "resource_classes"),
    ("recent innovations", innovations, "recent_innovations"),
]:
    if len(rows) < int(minimums.get(key, 0)):
        fail(f"minimum gate failed for {label}: {len(rows)}")
primary_count = sum(row.get("primary_authority") is True for row in evidence)
if primary_count < int(minimums.get("authoritative_primary_sources", 40)):
    fail(f"primary-source gate failed: {primary_count}")

for row in contexts:
    source = row.get("context_id", "context.unknown")
    require(row, ["record_kind", "domain_vision", "owns", "explicitly_excludes", "core_invariants", "evidence_refs"], source)
    if not row.get("owns") or not row.get("explicitly_excludes") or not row.get("core_invariants"):
        fail(f"{source}: boundary, exclusions and invariants must be non-empty")
    for ref in row.get("neighbor_context_refs", []):
        if ref.startswith("context.runtime-resource.") and ref not in context_ids:
            fail(f"{source}: unknown internal neighbor {ref}")

for row in types:
    source = row.get("type_id", "type.unknown")
    require(row, ["owner_context_ref", "definition", "equality_semantics", "canonical_form", "invariants", "must_not_be_confused_with"], source)
    if row.get("owner_context_ref") not in context_ids:
        fail(f"{source}: unknown owner {row.get('owner_context_ref')}")

for row in machines:
    source = row.get("state_machine_id", "state-machine.unknown")
    states = set(row.get("states", []))
    initial = row.get("initial_state")
    terminals = set(row.get("terminal_states", []))
    if initial not in states or not terminals or not terminals <= states:
        fail(f"{source}: invalid initial/terminal state declarations")
    graph: dict[str, set[str]] = defaultdict(set)
    for transition in row.get("transitions", []):
        a, b = transition.get("from"), transition.get("to")
        if a not in states or b not in states:
            fail(f"{source}: transition references unknown state {a}->{b}")
        else:
            graph[a].add(b)
    seen: set[str] = set()
    queue = deque([initial])
    while queue:
        state = queue.popleft()
        if state in seen:
            continue
        seen.add(state)
        queue.extend(graph[state] - seen)
    unreachable = states - seen
    if unreachable:
        fail(f"{source}: unreachable states {sorted(unreachable)}")
    if row.get("owner_context_ref") not in context_ids or row.get("subject_type_ref") not in type_ids:
        fail(f"{source}: unresolved owner or subject type")

for row in resources:
    source = row.get("resource_class_id", "resource-class.unknown")
    require(row, ["dimension", "canonical_unit", "consumability", "shareability", "divisibility", "compressibility", "overcommit_law", "topology_relations", "usage_measurement", "hazards"], source)
    if not row.get("topology_relations") or not row.get("hazards"):
        fail(f"{source}: topology and hazards must be explicit")

for row in policies:
    source = row.get("policy_id", "scheduling-policy.unknown")
    require(row, ["objective", "guarantee", "required_inputs", "tradeoffs", "evidence_refs"], source)
    if not row.get("required_inputs") or not row.get("tradeoffs"):
        fail(f"{source}: inputs and tradeoffs must be non-empty")

shared_decision_required = ["decision_id", "edition", "status", "owner_context_ref", "question", "value_contract", "allowed_values", "binding_phase", "authority_ref", "default_law", "default_value", "constraints", "conflicts", "implications", "affects_contracts", "evidence_required", "change_semantics", "gaps"]
for row in decisions:
    source = row.get("decision_id", "decision.unknown")
    require(row, shared_decision_required, source)
    if row.get("owner_context_ref") not in context_ids:
        fail(f"{source}: unknown context owner")
    if not row.get("allowed_values") or len(row.get("allowed_values", [])) != len(set(row.get("allowed_values", []))):
        fail(f"{source}: allowed values must be non-empty and unique")
    if row.get("default_law") == "forbidden" and row.get("default_value") is not None:
        fail(f"{source}: forbidden default law must have null default")

shared_library_required = ["library_id", "edition", "status", "library_kind", "semantic_owner_refs", "contributes_to_context_refs", "effect_boundary", "public_types", "public_traits", "operation_refs", "error_contracts", "decision_refs", "requirement_refs", "offer_refs", "configuration_contracts", "effect_intents", "runtime_receipts", "laws", "oracles", "resource_contracts", "concurrency", "cancellation", "unsafe_ffi_generated_policy", "dependencies", "targets", "compatibility", "removal_seams", "forbidden_responsibilities", "evidence_refs", "gaps"]
for row in libraries:
    source = row.get("library_id", "library.unknown")
    require(row, shared_library_required, source)
    if row.get("library_kind") == "semantic_pure" and len(row.get("semantic_owner_refs", [])) != 1:
        fail(f"{source}: semantic_pure library needs exactly one owner")
    for ref in row.get("semantic_owner_refs", []) + row.get("contributes_to_context_refs", []):
        if ref not in context_ids:
            fail(f"{source}: unknown context ref {ref}")
    for ref in row.get("decision_refs", []):
        if ref not in decision_ids:
            fail(f"{source}: unknown decision ref {ref}")
    if row.get("library_kind") in {"semantic_pure", "algorithm_pure", "policy_pure", "test_oracle"} and row.get("effect_boundary") not in {"pure_no_io", "pure_effect_intents"}:
        fail(f"{source}: pure library has effectful boundary")
    if not row.get("forbidden_responsibilities") or not row.get("removal_seams"):
        fail(f"{source}: missing forbidden responsibility/removal seam")

record_id_fields = {"capability_requirement": "requirement_id", "capability_offer": "offer_id", "capability_binding": "binding_id"}
binding_ids: set[str] = set()
requirement_ids: set[str] = set()
offer_ids: set[str] = set()
for row in bindings:
    kind = row.get("record_kind")
    field = record_id_fields.get(kind)
    if not field:
        fail(f"requirements-offers-bindings.jsonl: unexpected kind {kind}")
        continue
    value = row.get(field)
    if not isinstance(value, str):
        fail(f"{kind}: missing {field}")
    ({"capability_requirement": requirement_ids, "capability_offer": offer_ids, "capability_binding": binding_ids}[kind]).add(value)
for row in bindings:
    if row.get("record_kind") == "capability_binding":
        if row.get("requirement_ref") not in requirement_ids:
            fail(f"{row.get('binding_id')}: unknown requirement")
        for ref in row.get("offer_refs", []):
            if ref not in offer_ids:
                fail(f"{row.get('binding_id')}: unknown offer {ref}")

for row in gaps:
    require(row, ["gap_id", "subject_ref", "gap_kind", "blocking", "resolution_condition", "prohibited_fallbacks"], row.get("gap_id", "gap.unknown"))
for row in bindings:
    if row.get("record_kind") == "capability_binding":
        for ref in row.get("residual_gaps", []):
            if ref not in gap_ids:
                fail(f"{row.get('binding_id')}: unknown residual gap {ref}")

for row in evidence:
    source = row.get("evidence_id", "evidence.unknown")
    require(row, ["title", "publisher", "source_kind", "url", "primary_authority", "claims_supported", "scope_limitations", "accessed_at"], source)
    if not str(row.get("url", "")).startswith("https://"):
        fail(f"{source}: URL must use https")
    if not row.get("claims_supported") or not row.get("scope_limitations"):
        fail(f"{source}: scoped claims and limitations required")

for row in innovations:
    source = row.get("innovation_id", "innovation.unknown")
    require(row, ["first_material_year", "core_change", "compiler_implications", "maturity", "non_llm", "evidence_refs", "caveats"], source)
    if not 2021 <= int(row.get("first_material_year", 0)) <= 2026:
        fail(f"{source}: outside 2021-2026 window")
    if row.get("non_llm") is not True:
        fail(f"{source}: must be explicitly non-LLM")

for source_name, rows in [
    ("contexts", contexts), ("types", types), ("state-machines", machines), ("resource-classes", resources),
    ("scheduling-policies", policies), ("innovations", innovations),
]:
    for row in rows:
        for ref in row.get("evidence_refs", []):
            if ref not in evidence_ids:
                fail(f"{source_name}:{next(iter(row.values()), '?')}: unknown evidence ref {ref}")

forbidden = re.compile(r"(^|[._-])(llm|large_language_model|rag|agent_memory|prompt)([._-]|$)", re.IGNORECASE)
for rows, id_field in [(contexts, "context_id"), (types, "type_id"), (policies, "policy_id"), (innovations, "innovation_id")]:
    for row in rows:
        if forbidden.search(str(row.get(id_field, ""))) or forbidden.search(str(row.get("name", ""))):
            fail(f"{row.get(id_field)}: forbidden LLM/generative semantic dependency")

all_ids: list[str] = []
for values in [context_ids, type_ids, machine_ids, resource_ids, policy_ids, decision_ids, library_ids, evidence_ids, innovation_ids, gap_ids, requirement_ids, offer_ids, binding_ids]:
    all_ids.extend(values)
dupes = [value for value, count in Counter(all_ids).items() if count > 1]
if dupes:
    fail(f"IDs collide across registries: {dupes}")

if ERRORS:
    print(f"FAIL runtime/compute/resource corpus: {len(ERRORS)} error(s)")
    for error in ERRORS:
        print(f"- {error}")
    sys.exit(1)

print(
    "PASS runtime/compute/resource corpus: "
    f"{len(contexts)} contexts, {len(types)} types, {len(machines)} state machines, "
    f"{len(resources)} resource classes, {len(policies)} scheduling policies, "
    f"{len(decisions)} decisions, {len(libraries)} library boundaries, "
    f"{len(requirement_ids)} requirements, {len(offer_ids)} offers, {len(binding_ids)} candidate bindings, "
    f"{len(evidence)} primary sources, {len(innovations)} 2021-2026 non-LLM innovations, {len(gaps)} explicit gaps"
)
