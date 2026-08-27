#!/usr/bin/env python3
"""Validate closure, lifecycle totality, thresholds, and deterministic generation."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
import build_corpus as build


HERE = Path(__file__).resolve().parent
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def load_json(name: str) -> object:
    try:
        return json.loads((HERE / name).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{name}: invalid JSON: {exc}")
        return {}


def load_jsonl(name: str) -> list[dict]:
    rows: list[dict] = []
    try:
        lines = (HERE / name).read_text(encoding="utf-8").splitlines()
    except Exception as exc:  # noqa: BLE001
        fail(f"{name}: unreadable: {exc}")
        return rows
    for line_no, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            fail(f"{name}:{line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(row, dict):
            fail(f"{name}:{line_no}: record must be an object")
            continue
        rows.append(row)
    return rows


def unique(rows: list[dict], field: str, name: str) -> set[str]:
    values = [row.get(field) for row in rows]
    duplicates = [value for value, count in Counter(values).items() if value is None or count != 1]
    if duplicates:
        fail(f"{name}: null or duplicate {field}: {duplicates}")
    return {value for value in values if isinstance(value, str)}


def require(row: dict, required: list[str], subject: str) -> None:
    missing = [field for field in required if field not in row]
    if missing:
        fail(f"{subject}: missing fields {missing}")


def simple_schema_validate(row: dict, schema: dict, subject: str) -> None:
    require(row, schema.get("required", []), subject)
    for field, spec in schema.get("properties", {}).items():
        if field not in row:
            continue
        value = row[field]
        expected = spec.get("type")
        checks = {
            "string": isinstance(value, str),
            "array": isinstance(value, list),
            "object": isinstance(value, dict),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "boolean": isinstance(value, bool),
        }
        if expected in checks and not checks[expected]:
            fail(f"{subject}: {field} is not {expected}")
        if "const" in spec and value != spec["const"]:
            fail(f"{subject}: {field} must equal {spec['const']!r}")
        if "enum" in spec and value not in spec["enum"]:
            fail(f"{subject}: {field} is not in declared enum")
        if "pattern" in spec and isinstance(value, str) and re.search(spec["pattern"], value) is None:
            fail(f"{subject}: {field} does not match {spec['pattern']}")
        if isinstance(value, list) and value == [] and spec.get("minItems", 0) > 0:
            fail(f"{subject}: {field} must be non-empty")


FILES = {
    "bounded-context-candidates.jsonl": ("context_id", "context.schema.json"),
    "capabilities.jsonl": ("capability_id", "capability.schema.json"),
    "operations.jsonl": ("operation_id", "operation.schema.json"),
    "decisions.jsonl": ("decision_id", "decision.schema.json"),
    "state-machines.jsonl": ("state_machine_id", "state-machine.schema.json"),
    "contracts.jsonl": ("contract_id", "contract.schema.json"),
    "invariants-refusals.jsonl": ("rule_id", "invariant-refusal.schema.json"),
    "library-boundaries.jsonl": ("library_id", "library-boundary.schema.json"),
    "retired-compositions.jsonl": ("replacement_id", "library-replacement.schema.json"),
    "compiler-mappings.jsonl": ("mapping_id", "compiler-mapping.schema.json"),
    "product-truth-mappings.jsonl": ("mapping_id", "product-truth.schema.json"),
    "cross-domain-mappings.jsonl": ("mapping_id", "cross-domain-mapping.schema.json"),
    "sources.jsonl": ("source_id", "source.schema.json"),
    "evidence.jsonl": ("evidence_id", "evidence.schema.json"),
    "innovations-2021-2026.jsonl": ("innovation_id", "innovation.schema.json"),
    "gaps.jsonl": ("gap_id", "gap.schema.json"),
    "vertical-examples.jsonl": ("example_id", "vertical-example.schema.json"),
}


rows_by_file = {name: load_jsonl(name) for name in [*FILES, "requirements-offers-bindings.jsonl"]}
ids_by_file: dict[str, set[str]] = {}
for name, (id_field, schema_name) in FILES.items():
    rows = rows_by_file[name]
    ids_by_file[name] = unique(rows, id_field, name)
    schema = load_json(f"schemas/{schema_name}")
    if isinstance(schema, dict):
        for row in rows:
            simple_schema_validate(row, schema, str(row.get(id_field, name)))

manifest = load_json("manifest.json")
compiler = load_json("compiler-contract.json")
if not isinstance(manifest, dict) or manifest.get("completion_claim") is not False:
    fail("manifest.json: completion_claim must be false")
if not isinstance(compiler, dict) or compiler.get("completion_claim") is not False:
    fail("compiler-contract.json: completion_claim must be false")

contexts = rows_by_file["bounded-context-candidates.jsonl"]
capabilities = rows_by_file["capabilities.jsonl"]
operations = rows_by_file["operations.jsonl"]
decisions = rows_by_file["decisions.jsonl"]
machines = rows_by_file["state-machines.jsonl"]
contracts = rows_by_file["contracts.jsonl"]
rules = rows_by_file["invariants-refusals.jsonl"]
libraries = rows_by_file["library-boundaries.jsonl"]
replacements = rows_by_file["retired-compositions.jsonl"]
mappings = rows_by_file["compiler-mappings.jsonl"]
truths = rows_by_file["product-truth-mappings.jsonl"]
sources = rows_by_file["sources.jsonl"]
evidence = rows_by_file["evidence.jsonl"]
innovations = rows_by_file["innovations-2021-2026.jsonl"]
gaps = rows_by_file["gaps.jsonl"]
examples = rows_by_file["vertical-examples.jsonl"]
bindings = rows_by_file["requirements-offers-bindings.jsonl"]
cross = rows_by_file["cross-domain-mappings.jsonl"]

binding_schema = load_json("schemas/requirement-offer-binding.schema.json")
if isinstance(binding_schema, dict):
    for row in bindings:
        simple_schema_validate(row, binding_schema, str(row.get("record_kind", "requirement-offer-binding")))

context_ids = ids_by_file["bounded-context-candidates.jsonl"]
capability_ids = ids_by_file["capabilities.jsonl"]
operation_ids = ids_by_file["operations.jsonl"]
contract_ids = ids_by_file["contracts.jsonl"]
library_ids = ids_by_file["library-boundaries.jsonl"]
source_ids = ids_by_file["sources.jsonl"]
gap_ids = ids_by_file["gaps.jsonl"]

minimums = manifest.get("minimum_gates", {}) if isinstance(manifest, dict) else {}
candidate_total = len(capabilities) + len(operations) + len(decisions) + len(machines) + len(contracts)
gate_values = {
    "bounded-context-candidates": len(contexts),
    "candidate_record_total": candidate_total,
    "sources": len(sources),
    "innovations-2021-2026": len(innovations),
    "vertical-examples": len(examples),
}
for gate, actual in gate_values.items():
    if actual < int(minimums.get(gate, 0)):
        fail(f"minimum gate {gate}: {actual} < {minimums.get(gate)}")
if isinstance(manifest, dict) and manifest.get("candidate_record_total") != candidate_total:
    fail("manifest candidate_record_total does not reconcile")
for name, rows in rows_by_file.items():
    key = name.removesuffix(".jsonl")
    if isinstance(manifest, dict) and manifest.get("counts", {}).get(key) != len(rows):
        fail(f"manifest count mismatch for {name}")

for context in contexts:
    subject = context.get("context_id", "unknown-context")
    if not context.get("owns") or not context.get("explicitly_excludes"):
        fail(f"{subject}: positive and negative scope required")
    if not context.get("authority_invariants") or not context.get("tenant_isolation_invariants"):
        fail(f"{subject}: authority and isolation invariants required")

for row in capabilities:
    if row.get("owner_context_ref") not in context_ids:
        fail(f"{row.get('capability_id')}: unknown context")
for row in operations:
    if row.get("owner_context_ref") not in context_ids or row.get("capability_ref") not in capability_ids or row.get("input_contract_ref") not in contract_ids:
        fail(f"{row.get('operation_id')}: unresolved context, capability, or contract")
for row in decisions:
    if row.get("owner_context_ref") not in context_ids:
        fail(f"{row.get('decision_id')}: unknown context")
    if row.get("default_law") != "forbidden" or row.get("default_value") is not None:
        fail(f"{row.get('decision_id')}: implicit default is forbidden")
for row in contracts:
    if row.get("owner_context_ref") not in context_ids:
        fail(f"{row.get('contract_id')}: unknown context")

for row in machines:
    subject = row.get("state_machine_id", "unknown-machine")
    states = set(row.get("states", []))
    commands = set(row.get("commands", []))
    if row.get("owner_context_ref") not in context_ids:
        fail(f"{subject}: unknown context")
    if row.get("initial_state") not in states or not set(row.get("terminal_states", [])) <= states:
        fail(f"{subject}: bad initial or terminal state")
    outcomes: dict[tuple[str, str], int] = defaultdict(int)
    graph: dict[str, set[str]] = defaultdict(set)
    for transition in row.get("transitions", []):
        state, command, target = transition.get("from"), transition.get("command"), transition.get("to")
        if state not in states or target not in states or command not in commands:
            fail(f"{subject}: transition has unknown state or command")
        outcomes[(state, command)] += 1
        graph[state].add(target)
    for refusal in row.get("refusal_matrix", []):
        state, command = refusal.get("state"), refusal.get("command")
        if state not in states or command not in commands:
            fail(f"{subject}: refusal has unknown state or command")
        outcomes[(state, command)] += 1
    for state in states:
        for command in commands:
            if outcomes[(state, command)] != 1:
                fail(f"{subject}: ({state}, {command}) has {outcomes[(state, command)]} outcomes, expected exactly one")
    seen: set[str] = set()
    queue = deque([row.get("initial_state")])
    while queue:
        state = queue.popleft()
        if state in seen:
            continue
        seen.add(state)
        queue.extend(graph[state] - seen)
    if states - seen:
        fail(f"{subject}: unreachable states {sorted(states - seen)}")

for row in libraries:
    subject = row.get("library_id", "unknown-library")
    slug = subject.rsplit(".", 1)[-1]
    for ref in row.get("semantic_owner_refs", []) + row.get("contributes_to_context_refs", []):
        if ref not in context_ids:
            fail(f"{subject}: unknown context {ref}")
    for ref in row.get("public_contracts", []):
        if ref not in contract_ids:
            fail(f"{subject}: unknown contract {ref}")
    for ref in row.get("operation_refs", []):
        if ref not in operation_ids:
            fail(f"{subject}: unknown operation {ref}")
    if row.get("library_kind") in {"semantic_pure", "policy_pure", "algorithm_pure"} and not str(row.get("effect_boundary", "")).startswith("pure"):
        fail(f"{subject}: pure library has an effectful boundary")
    provider_source_ref = row.get("provider_source_ref")
    if provider_source_ref is not None and provider_source_ref not in source_ids:
        fail(f"{subject}: unknown provider source")
    if slug in build.EXACT_SPLIT_APIS:
        if not row.get("public_types") or not row.get("public_traits") or not row.get("operations"):
            fail(f"{subject}: exact split API regressed to placeholders")
        for operation in row.get("operations", []):
            if not operation.get("operation_ref") or not operation.get("input_types") or not operation.get("output_type"):
                fail(f"{subject}: incomplete exact operation")
            if not operation.get("refusal_types") or operation.get("purity") != "pure":
                fail(f"{subject}: refusal or purity contract incomplete")

central_path = HERE.parent.parent / "compiler/library_registry/library-contributions.jsonl"
central_library_ids = {
    json.loads(line)["library_id"]
    for line in central_path.read_text(encoding="utf-8").splitlines()
} if central_path.exists() else set()
for row in replacements:
    subject = row.get("replacement_id", "unknown-replacement")
    if row.get("retired_library_ref") in library_ids:
        fail(f"{subject}: retired library still emitted")
    if not set(row.get("covered_context_refs", [])) <= context_ids:
        fail(f"{subject}: unknown covered context")
    if not set(row.get("replacement_library_refs", [])) <= central_library_ids:
        fail(f"{subject}: unresolved replacement library")
    if row.get("compatibility_alias_permitted") is not False:
        fail(f"{subject}: compatibility alias must be forbidden")

requirement_ids = unique([row for row in bindings if row.get("record_kind") == "capability_requirement"], "requirement_id", "requirements")
offer_ids = unique([row for row in bindings if row.get("record_kind") == "capability_offer"], "offer_id", "offers")
binding_ids = unique([row for row in bindings if row.get("record_kind") == "capability_binding"], "binding_id", "bindings")
for row in bindings:
    if row.get("record_kind") == "capability_requirement":
        for ref in row.get("requester_context_refs", []):
            if ref not in context_ids:
                fail(f"{row.get('requirement_id')}: unknown requester {ref}")
    elif row.get("record_kind") == "capability_offer":
        if row.get("library_ref") not in library_ids:
            fail(f"{row.get('offer_id')}: unknown library")
    elif row.get("record_kind") == "capability_binding":
        if row.get("requirement_ref") not in requirement_ids:
            fail(f"{row.get('binding_id')}: unknown requirement")
        for ref in row.get("offer_refs", []):
            if ref not in offer_ids:
                fail(f"{row.get('binding_id')}: unknown offer {ref}")
        for ref in row.get("residual_gap_refs", []):
            if ref not in gap_ids:
                fail(f"{row.get('binding_id')}: unknown gap {ref}")

for row in mappings:
    if row.get("from_requirement_ref") not in requirement_ids or row.get("through_library_ref") not in library_ids:
        fail(f"{row.get('mapping_id')}: unresolved requirement or library")
for row in truths:
    if row.get("semantic_owner_ref") not in context_ids:
        fail(f"{row.get('mapping_id')}: unknown semantic owner")
for row in cross:
    for ref in row.get("local_context_refs", []):
        if ref not in context_ids:
            fail(f"{row.get('mapping_id')}: unknown local context {ref}")

for collection_name, collection in [
    ("contexts", contexts), ("capabilities", capabilities), ("operations", operations), ("decisions", decisions),
    ("machines", machines), ("contracts", contracts), ("rules", rules), ("innovations", innovations),
]:
    for row in collection:
        for ref in row.get("source_refs", []):
            if ref not in source_ids:
                fail(f"{collection_name}:{ref}: unknown source")
for row in evidence:
    if row.get("source_ref") not in source_ids:
        fail(f"{row.get('evidence_id')}: unknown source")

official_source_count = sum(row.get("primary_or_official") is True for row in sources)
if official_source_count < 70:
    fail(f"official source count below 70: {official_source_count}")
for row in innovations:
    if row.get("non_llm") is not True or not 2021 <= int(row.get("first_material_year", 0)) <= 2026:
        fail(f"{row.get('innovation_id')}: innovation must be non-LLM and dated 2021-2026")
    for ref in row.get("context_refs", []):
        if ref not in context_ids:
            fail(f"{row.get('innovation_id')}: unknown context {ref}")

core_text = json.dumps([contexts, capabilities, operations, decisions, machines, contracts], sort_keys=True).lower()
for forbidden in ["large language model", "generative ai", "agentic workflow", "prompt token"]:
    if forbidden in core_text:
        fail(f"LLM/generative core leakage: {forbidden}")

required_distinction_fragments = [
    "Tenant identity, product account", "Commercial entitlement", "Commercial entitlement, technical quota",
    "Meter event, accepted usage", "plan or catalog offer", "internal SLO evaluation",
    "Customer support case", "Approved maintenance", "Suspension, entitlement revocation",
    "Product or supplier exit",
]
laws = "\n".join(row.get("law", "") for row in rules)
for fragment in required_distinction_fragments:
    if fragment not in laws:
        fail(f"required distinction invariant missing: {fragment}")

expected = build.build_artifacts()
for name, value in expected.items():
    if name.endswith(".jsonl"):
        expected_text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in value)  # type: ignore[union-attr]
    else:
        expected_text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if (HERE / name).read_text(encoding="utf-8") != expected_text:
        fail(f"{name}: generated artifact drift; rerun build_corpus.py")
for name, schema in build.build_schemas().items():
    expected_text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    if (HERE / "schemas" / name).read_text(encoding="utf-8") != expected_text:
        fail(f"schemas/{name}: generated schema drift")

if ERRORS:
    print("VALIDATION FAILED", file=sys.stderr)
    for error in ERRORS:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

report = {
    "validation_id": "validation.platform-commercial-support.0.1.0",
    "validated_at_source_date": build.AS_OF,
    "status": "passed_candidate_gates",
    "completion_claim": False,
    "counts": {
        "bounded_contexts": len(contexts),
        "capabilities": len(capabilities),
        "operations": len(operations),
        "decisions": len(decisions),
        "state_machines": len(machines),
        "contracts": len(contracts),
        "capability_operation_decision_lifecycle_contract_total": candidate_total,
        "invariant_refusal_precedence_rules": len(rules),
        "library_effect_port_provider_adapter_boundaries": len(libraries),
        "requirements": len(requirement_ids),
        "offers": len(offer_ids),
        "bindings": len(binding_ids),
        "compiler_mappings": len(mappings),
        "product_truth_mappings": len(truths),
        "cross_domain_mappings": len(cross),
        "official_primary_sources": official_source_count,
        "evidence_claims": len(evidence),
        "non_llm_innovations_2021_2026": len(innovations),
        "gaps": len(gaps),
        "blocking_gaps": sum(row.get("blocking") is True for row in gaps),
        "vertical_examples": len(examples),
        "schemas": len(build.build_schemas()),
    },
    "checks": [
        "deterministic artifact equality", "JSON and schema-required fields", "identity uniqueness",
        "reference closure", "manifest count reconciliation", "lifecycle reachability and total command-state dispatch",
        "authority and tenant-isolation presence", "requirement-offer-binding closure", "official-source threshold",
        "non-LLM innovation window", "semantic distinction invariants", "candidate/completion honesty",
    ],
}
(HERE / "validation-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("VALID platform-commercial-support sourced candidate")
for key, value in report["counts"].items():
    print(f"{key}={value}")
