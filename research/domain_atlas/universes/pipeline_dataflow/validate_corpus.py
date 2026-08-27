#!/usr/bin/env python3
"""Validate pipeline/dataflow corpus structure, references, coverage and examples."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"{path}: invalid JSON: {exc}")
        return None


def load_jsonl(path: Path) -> list[dict]:
    result = []
    try:
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except Exception as exc:
                fail(f"{path}:{number}: invalid JSON: {exc}")
                continue
            if not isinstance(value, dict):
                fail(f"{path}:{number}: record must be an object")
            else:
                result.append(value)
    except FileNotFoundError:
        fail(f"missing file: {path}")
    return result


def unique(records: list[dict], key: str, label: str) -> set[str]:
    values: list[str] = []
    for index, record in enumerate(records):
        value = record.get(key)
        if not isinstance(value, str) or not value:
            fail(f"{label}[{index}] missing non-empty {key}")
        else:
            values.append(value)
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        fail(f"{label}: duplicate {key}: {duplicates}")
    return set(values)


def type_matches(value, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, True)


def validate_instance(value, schema: dict, path: str) -> None:
    if "const" in schema and value != schema["const"]:
        fail(f"{path}: expected const {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        fail(f"{path}: {value!r} not in enum {schema['enum']}")
    expected = schema.get("type")
    if expected:
        expected_types = expected if isinstance(expected, list) else [expected]
        if not any(type_matches(value, candidate) for candidate in expected_types):
            fail(f"{path}: expected type {expected_types}, got {type(value).__name__}")
            return
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            fail(f"{path}: string shorter than minLength")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            fail(f"{path}: value {value!r} does not match {schema['pattern']!r}")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema and value < schema["minimum"]:
        fail(f"{path}: value below minimum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            fail(f"{path}: too few items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                fail(f"{path}: items are not unique")
        if isinstance(schema.get("items"), dict):
            for index, item in enumerate(value):
                validate_instance(item, schema["items"], f"{path}[{index}]")
    if isinstance(value, dict):
        required = schema.get("required", [])
        for name in required:
            if name not in value:
                fail(f"{path}: missing required property {name}")
        if len(value) < schema.get("minProperties", 0):
            fail(f"{path}: too few properties")
        props = schema.get("properties", {})
        for name, child in value.items():
            if name in props:
                validate_instance(child, props[name], f"{path}.{name}")
            elif isinstance(schema.get("additionalProperties"), dict):
                validate_instance(child, schema["additionalProperties"], f"{path}.{name}")
            elif schema.get("additionalProperties") is False:
                fail(f"{path}: unexpected property {name}")


def validate() -> dict:
    manifest = load_json(ROOT / "manifest.json") or {}
    sources = load_jsonl(ROOT / "sources.jsonl")
    contexts = load_jsonl(ROOT / "context-candidates.jsonl")
    decisions = load_jsonl(ROOT / "decision-catalog.jsonl")
    outcomes = load_jsonl(ROOT / "failure-refusal-catalog.jsonl")
    innovations = load_jsonl(ROOT / "innovations.jsonl")
    libraries = load_jsonl(ROOT / "library-boundary-candidates.jsonl")
    requirements = load_jsonl(ROOT / "compiler-requirements.jsonl")
    offers = load_jsonl(ROOT / "capability-offer-templates.jsonl")
    mappings = load_jsonl(ROOT / "operation-mappings.jsonl")
    gaps = load_jsonl(ROOT / "gaps.jsonl")
    lifecycles = load_jsonl(ROOT / "lifecycles.jsonl")
    artifact_kinds = load_jsonl(ROOT / "artifact-kinds.jsonl")

    source_ids = unique(sources, "source_id", "sources")
    context_ids = unique(contexts, "context_id", "contexts")
    decision_ids = unique(decisions, "decision_id", "decisions")
    outcome_ids = unique(outcomes, "outcome_id", "outcomes")
    innovation_ids = unique(innovations, "innovation_id", "innovations")
    library_ids = unique(libraries, "library_candidate_id", "libraries")
    requirement_ids = unique(requirements, "requirement_id", "requirements")
    offer_ids = unique(offers, "offer_template_id", "offers")
    mapping_ids = unique(mappings, "mapping_id", "operation mappings")
    gap_ids = unique(gaps, "gap_id", "gaps")
    lifecycle_ids = unique(lifecycles, "lifecycle_id", "lifecycles")
    artifact_kind_ids = unique(artifact_kinds, "artifact_kind_id", "artifact kinds")

    if len(sources) < 40:
        fail(f"need at least 40 primary sources, found {len(sources)}")
    allowed_source_kinds = {"official_documentation", "open_standard", "standard", "original_research", "official_implementation"}
    for record in sources:
        if record.get("source_kind") not in allowed_source_kinds:
            fail(f"{record.get('source_id')}: non-primary source kind {record.get('source_kind')}")
        url = record.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            fail(f"{record.get('source_id')}: source URL is not absolute HTTPS")
        if any(name in parsed.netloc for name in ("wikipedia.org", "reddit.com")):
            fail(f"{record.get('source_id')}: secondary/community source is forbidden")
        if not record.get("claims_supported"):
            fail(f"{record.get('source_id')}: no scoped claim")

    for record in contexts:
        for field in ("domain_vision", "boundary", "ubiquitous_language", "aggregate_roots", "invariants", "commands", "domain_events", "refusals", "state_machine", "decision_points", "context_relationships", "published_language", "anti_corruption_layers", "evidence_refs"):
            if field not in record or not record[field]:
                fail(f"{record.get('context_id')}: empty/missing DDD field {field}")
        if record.get("llm_dependency") != "none":
            fail(f"{record.get('context_id')}: LLM dependency is forbidden")
        for ref in record.get("evidence_refs", []):
            if ref not in source_ids:
                fail(f"{record.get('context_id')}: unknown evidence ref {ref}")
        for relation in record.get("context_relationships", []):
            neighbor = relation.get("neighbor", "")
            if neighbor.startswith("ppl.") and neighbor not in context_ids:
                fail(f"{record.get('context_id')}: unknown pipeline neighbor {neighbor}")

    for record in decisions:
        if record.get("owner_context", "").startswith("ppl.") and record["owner_context"] not in context_ids:
            fail(f"{record.get('decision_id')}: unknown owner context")
        if record.get("default_law", "").lower().find("hidden default") < 0:
            fail(f"{record.get('decision_id')}: default law must forbid hidden defaults")
        if not record.get("allowed_value_kinds"):
            fail(f"{record.get('decision_id')}: no allowed value kinds")

    must_have_decisions = {"decision.pipeline.compression", "decision.pipeline.checkpoint_mode", "decision.pipeline.watermark_strategy", "decision.pipeline.state_bound", "decision.pipeline.delivery_multiplicity", "decision.pipeline.backfill_reprocessing", "decision.pipeline.maintenance_retention"}
    missing = must_have_decisions - decision_ids
    if missing:
        fail(f"decision catalog misses critical decisions: {sorted(missing)}")

    for record in outcomes:
        if record.get("owner_context", "").startswith("ppl.") and record["owner_context"] not in context_ids:
            fail(f"{record.get('outcome_id')}: unknown owner context")
        if record.get("kind") not in {"refusal", "failure"}:
            fail(f"{record.get('outcome_id')}: invalid outcome kind")
        if not record.get("allowed_next_actions"):
            fail(f"{record.get('outcome_id')}: no next actions")

    for record in lifecycles:
        owner = record.get("owner_context", "")
        if owner.startswith("ppl.") and owner not in context_ids:
            fail(f"{record.get('lifecycle_id')}: unknown owner {owner}")
        states = set(record.get("states", []))
        if record.get("initial_state") not in states:
            fail(f"{record.get('lifecycle_id')}: initial state absent")
        if not set(record.get("terminal_states", [])).issubset(states):
            fail(f"{record.get('lifecycle_id')}: terminal state absent")
        for transition in record.get("transitions", []):
            if transition.get("from") not in states or transition.get("to") not in states:
                fail(f"{record.get('lifecycle_id')}: transition references unknown state")
        if record.get("invalid_transition_outcome") not in outcome_ids:
            fail(f"{record.get('lifecycle_id')}: unknown invalid-transition outcome")
        if not record.get("transitions") or not record.get("totality_law"):
            fail(f"{record.get('lifecycle_id')}: incomplete lifecycle")

    required_artifact_kinds = {"pipeline-artifact.definition", "pipeline-artifact.compiled_plan", "pipeline-artifact.deployment", "pipeline-artifact.run", "pipeline-artifact.task_attempt", "pipeline-artifact.data_cut", "pipeline-artifact.materialization", "pipeline-artifact.checkpoint"}
    if artifact_kind_ids != required_artifact_kinds:
        fail(f"artifact kind set mismatch: {sorted(required_artifact_kinds - artifact_kind_ids)}")
    for record in artifact_kinds:
        if record.get("lifecycle_ref") not in lifecycle_ids:
            fail(f"{record.get('artifact_kind_id')}: unknown lifecycle")
        if not record.get("cannot_substitute_for"):
            fail(f"{record.get('artifact_kind_id')}: missing non-substitution boundary")

    for record in innovations:
        for ref in record.get("evidence_refs", []):
            if ref not in source_ids:
                fail(f"{record.get('innovation_id')}: unknown evidence ref {ref}")
        if not re.search(r"202[1-6]", record.get("period", "")):
            fail(f"{record.get('innovation_id')}: outside 2021-2026 period")
        if record.get("llm_dependency") != "none":
            fail(f"{record.get('innovation_id')}: LLM innovation is forbidden")

    for record in libraries:
        owner = record.get("semantic_owner_context", "")
        if owner.startswith("ppl.") and owner not in context_ids:
            fail(f"{record.get('library_candidate_id')}: unknown owner {owner}")
        for ref in record.get("decision_refs", []):
            if ref not in decision_ids:
                fail(f"{record.get('library_candidate_id')}: unknown decision {ref}")
        if record.get("library_kind", "").startswith("pure") and "no I/O" not in record.get("effect_rule", ""):
            fail(f"{record.get('library_candidate_id')}: pure library does not forbid I/O")

    # The first risk-ranked pipeline closure item is retained only as a structural directed-
    # multigraph algebra.  Port compatibility, lawful-cycle policy, progress and execution remain
    # separate contracts.  Fail if the exact source API regresses to a generic request/outcome
    # placeholder or if the validator stops declaring its dependencies.
    library_by_id = {record["library_candidate_id"]: record for record in libraries}
    graph = library_by_id.get("library.pipeline.graph_algebra", {})
    required_graph_fields = {"public_types", "public_traits", "input_types", "output_types", "error_contracts", "operations", "laws", "oracles", "resource_contracts", "dependencies", "evidence_refs"}
    if not required_graph_fields <= set(graph):
        fail(f"library.pipeline.graph_algebra: missing exact contract fields {sorted(required_graph_fields - set(graph))}")
    if graph.get("semantic_owner_context") != "ppl.graph_topology" or graph.get("library_kind") != "pure_semantic":
        fail("library.pipeline.graph_algebra: owner or purity regressed")
    if graph.get("dependencies") != ["library.pipeline.identity_types"]:
        fail("library.pipeline.graph_algebra: identity dependency must remain exact")
    if len(graph.get("operations", [])) < 10 or not all(operation.get("purity") == "pure" for operation in graph.get("operations", [])):
        fail("library.pipeline.graph_algebra: exact pure operation surface regressed")
    if any(operation.get("effect_intent_type") is not None or operation.get("receipt_type") is not None for operation in graph.get("operations", [])):
        fail("library.pipeline.graph_algebra: pure algebra acquired effects")
    if not all(operation.get("refusal_types") == graph.get("error_contracts") for operation in graph.get("operations", [])):
        fail("library.pipeline.graph_algebra: operation refusal totality regressed")
    required_operations = {
        "operation.pipeline.graph-algebra.create", "operation.pipeline.graph-algebra.compose-subgraph",
        "operation.pipeline.graph-algebra.reachability", "operation.pipeline.graph-algebra.strong-components",
        "operation.pipeline.graph-algebra.condense", "operation.pipeline.graph-algebra.classify-feedback",
        "operation.pipeline.graph-algebra.canonicalize", "operation.pipeline.graph-algebra.diff",
    }
    if not required_operations <= {operation.get("operation_ref") for operation in graph.get("operations", [])}:
        fail("library.pipeline.graph_algebra: required structural operations missing")
    law_text = " ".join(graph.get("laws", [])).lower()
    for distinction in ("port compatibility", "progress", "termination", "scheduling", "runtime execution"):
        if distinction not in law_text:
            fail(f"library.pipeline.graph_algebra: missing non-ownership law for {distinction}")
    graph_validator = library_by_id.get("library.pipeline.graph_validator", {})
    validator_dependencies = set(graph_validator.get("dependencies", []))
    if validator_dependencies != {"library.pipeline.graph_algebra", "library.pipeline.port_typechecker"}:
        fail("library.pipeline.graph_validator: algebra/typechecker wiring regressed")
    required_validator_fields = {
        "public_types", "public_traits", "input_types", "output_types", "error_contracts",
        "refusal_precedence", "operations", "laws", "oracles", "resource_contracts",
        "configuration_contracts", "dependencies", "evidence_refs", "boundary_adjudication",
    }
    if not required_validator_fields <= set(graph_validator):
        fail(f"library.pipeline.graph_validator: missing exact contract fields {sorted(required_validator_fields - set(graph_validator))}")
    if graph_validator.get("semantic_owner_context") != "ppl.graph_topology" or graph_validator.get("library_kind") != "pure_algorithm":
        fail("library.pipeline.graph_validator: owner or purity regressed")
    if len(graph_validator.get("operations", [])) != 9 or not all(operation.get("purity") == "pure" for operation in graph_validator.get("operations", [])):
        fail("library.pipeline.graph_validator: exact nine-operation pure surface regressed")
    if any(operation.get("effect_intent_type") is not None or operation.get("receipt_type") is not None for operation in graph_validator.get("operations", [])):
        fail("library.pipeline.graph_validator: pure validator acquired effects")
    if not all(operation.get("refusal_types") == graph_validator.get("error_contracts") for operation in graph_validator.get("operations", [])):
        fail("library.pipeline.graph_validator: operation refusal totality regressed")
    validator_laws = " ".join(graph_validator.get("laws", [])).lower()
    for required_law in ("invalid graph", "coverage is complete", "does not authorize publication"):
        if required_law not in validator_laws:
            fail(f"library.pipeline.graph_validator: missing law covering {required_law}")
    adjudication = graph_validator.get("boundary_adjudication", {})
    if (
        adjudication.get("disposition") != "explicit_coexistence"
        or set(adjudication.get("subject_refs", [])) != {"library.pipeline.graph_algebra", "library.pipeline.graph_validator"}
        or adjudication.get("no_compatibility_alias") is not True
    ):
        fail("graph algebra/validator boundary lacks exact coexistence adjudication")
    if not {"src.tarjan.scc", "src.naiad.paper", "src.w3c.shacl", "src.beam.runner_guide"} <= source_ids:
        fail("graph algebra/validator: primary structural and validation evidence missing")

    exact_contract_fields = {
        "public_types", "public_traits", "input_types", "output_types", "error_contracts",
        "refusal_precedence", "operations", "laws", "oracles", "resource_contracts",
        "configuration_contracts", "dependencies", "evidence_refs",
    }
    port_typechecker = library_by_id.get("library.pipeline.port_typechecker", {})
    if not exact_contract_fields <= set(port_typechecker):
        fail(f"library.pipeline.port_typechecker: missing exact contract fields {sorted(exact_contract_fields - set(port_typechecker))}")
    if port_typechecker.get("semantic_owner_context") != "ppl.port_contract" or port_typechecker.get("library_kind") != "pure_algorithm":
        fail("library.pipeline.port_typechecker: owner or purity regressed")
    if set(port_typechecker.get("dependencies", [])) != {"library.pipeline.identity_types", "library.schema_registry.compatibility"}:
        fail("library.pipeline.port_typechecker: identity/schema-compatibility dependencies regressed")
    port_operations = port_typechecker.get("operations", [])
    if len(port_operations) != 12 or not all(operation.get("purity") == "pure" for operation in port_operations):
        fail("library.pipeline.port_typechecker: exact twelve-operation pure surface regressed")
    if any(operation.get("effect_intent_type") is not None or operation.get("receipt_type") is not None for operation in port_operations):
        fail("library.pipeline.port_typechecker: pure typechecker acquired effects")
    if not all(operation.get("refusal_types") == port_typechecker.get("error_contracts") for operation in port_operations):
        fail("library.pipeline.port_typechecker: operation refusal totality regressed")
    if any(len(operation.get("input_types", [])) != len(set(operation.get("input_types", []))) for operation in port_operations):
        fail("library.pipeline.port_typechecker: operation has ambiguous duplicate input carriers")
    port_laws = " ".join(port_typechecker.get("laws", [])).lower()
    for required_law in ("directional", "schema compatibility is consumed", "adapter obligation", "no arrival order", "proves no channel capacity"):
        if required_law not in port_laws:
            fail(f"library.pipeline.port_typechecker: missing law covering {required_law}")

    data_cut = library_by_id.get("library.pipeline.data_cut_algebra", {})
    if not exact_contract_fields <= set(data_cut):
        fail(f"library.pipeline.data_cut_algebra: missing exact contract fields {sorted(exact_contract_fields - set(data_cut))}")
    if data_cut.get("semantic_owner_context") != "ppl.data_cut" or data_cut.get("library_kind") != "pure_semantic":
        fail("library.pipeline.data_cut_algebra: owner or purity regressed")
    if set(data_cut.get("dependencies", [])) != {"library.pipeline.identity_types", "library.csp.time.interval-algebra"}:
        fail("library.pipeline.data_cut_algebra: identity/time dependencies regressed")
    cut_operations = data_cut.get("operations", [])
    if len(cut_operations) != 12 or not all(operation.get("purity") == "pure" for operation in cut_operations):
        fail("library.pipeline.data_cut_algebra: exact twelve-operation pure surface regressed")
    if any(operation.get("effect_intent_type") is not None or operation.get("receipt_type") is not None for operation in cut_operations):
        fail("library.pipeline.data_cut_algebra: pure algebra acquired effects")
    if not all(operation.get("refusal_types") == data_cut.get("error_contracts") for operation in cut_operations):
        fail("library.pipeline.data_cut_algebra: operation refusal totality regressed")
    if any(len(operation.get("input_types", [])) != len(set(operation.get("input_types", []))) for operation in cut_operations):
        fail("library.pipeline.data_cut_algebra: operation has ambiguous duplicate input carriers")
    cut_laws = " ".join(data_cut.get("laws", [])).lower()
    for required_law in ("opaque to this algebra", "minimal antichain", "timestamps alone never identify", "closed cut is immutable", "performs no source reads"):
        if required_law not in cut_laws:
            fail(f"library.pipeline.data_cut_algebra: missing law covering {required_law}")
    if not {
        "src.substrait.type_system", "src.flink.changelog_mode", "src.flink.source_sink_contract",
        "src.flink.execution_order", "src.postgresql.export_snapshot", "src.kafka.consumer_position",
        "src.timely.frontier",
    } <= source_ids:
        fail("port/data-cut exact contracts: primary compatibility and cut evidence missing")

    publication = library_by_id.get("library.pipeline.materialization_publisher", {})
    if not exact_contract_fields | {"effect_boundary", "boundary_adjudication"} <= set(publication):
        fail("library.pipeline.materialization_publisher: exact publication protocol fields missing")
    if publication.get("semantic_owner_context") != "ppl.materialization" or publication.get("library_kind") != "pure_semantic":
        fail("library.pipeline.materialization_publisher: owner or pure semantic boundary regressed")
    if publication.get("effect_boundary") != "pure_effect_intents":
        fail("library.pipeline.materialization_publisher: publication protocol must emit intents without performing effects")
    expected_publication_dependencies = {
        "library.pipeline.identity_types", "library.pipeline.data_cut_algebra",
        "library.pipeline.sink_committer", "library.pipeline.lineage_receipts",
        "library.qor.quarantine_release_kernel",
    }
    if set(publication.get("dependencies", [])) != expected_publication_dependencies:
        fail("library.pipeline.materialization_publisher: publication dependency boundary regressed")
    publication_operations = publication.get("operations", [])
    if len(publication_operations) != 10 or not all(operation.get("purity") == "pure" for operation in publication_operations):
        fail("library.pipeline.materialization_publisher: exact ten-operation pure protocol surface regressed")
    publication_intents = {
        operation.get("effect_intent_type")
        for operation in publication_operations
        if operation.get("effect_intent_type") is not None
    }
    if publication_intents != {"PublicationEffectIntent", "SupersessionEffectIntent", "RecallEffectIntent"}:
        fail("library.pipeline.materialization_publisher: typed publication intent surface regressed")
    if any(operation.get("receipt_type") is not None for operation in publication_operations):
        fail("library.pipeline.materialization_publisher: pure protocol acquired effect execution receipts")
    if not all(operation.get("refusal_types") == publication.get("error_contracts") for operation in publication_operations):
        fail("library.pipeline.materialization_publisher: operation refusal totality regressed")
    if any(len(operation.get("input_types", [])) != len(set(operation.get("input_types", []))) for operation in publication_operations):
        fail("library.pipeline.materialization_publisher: operation has ambiguous duplicate input carriers")
    publication_laws = " ".join(publication.get("laws", [])).lower()
    for required_law in (
        "candidate published materialization", "sink commit receipt", "quality assertion success severity gate verdict",
        "approval or eligibility never performs publication", "unknown timeout cancellation", "ratified and published commits",
        "recall changes declared visibility", "not physical deletion", "consumer acceptance", "never reads a clock",
    ):
        if required_law not in publication_laws:
            fail(f"library.pipeline.materialization_publisher: missing law covering {required_law}")
    publication_adjudication = publication.get("boundary_adjudication", {})
    if (
        publication_adjudication.get("disposition") != "retain_but_narrow"
        or publication_adjudication.get("subject_refs") != ["library.pipeline.materialization_publisher"]
        or publication_adjudication.get("no_compatibility_alias") is not True
    ):
        fail("library.pipeline.materialization_publisher: boundary narrowing adjudication missing")
    if not {
        "src.iceberg.spec", "src.iceberg.branching", "src.delta.protocol",
        "src.openlineage.object_model", "src.openlineage.quality_assertions",
        "src.openlineage.version_facet", "src.w3c.shacl",
    } <= source_ids:
        fail("library.pipeline.materialization_publisher: primary publication evidence missing")

    for record in requirements:
        owner = record.get("owner_context", "")
        if owner.startswith("ppl.") and owner not in context_ids:
            fail(f"{record.get('requirement_id')}: unknown owner {owner}")
        if not record.get("proof_obligations"):
            fail(f"{record.get('requirement_id')}: no proof obligations")
    for record in offers:
        if not record.get("required_claim_fields") or not record.get("required_receipts"):
            fail(f"{record.get('offer_template_id')}: incomplete offer template")

    central_path = ROOT.parent / "operations" / "operation-candidates.jsonl"
    central_operations = load_jsonl(central_path)
    central_ids = unique(central_operations, "operation_id", "central operations")
    for record in mappings:
        if record.get("central_operation_id") not in central_ids:
            fail(f"{record.get('mapping_id')}: unknown central operation {record.get('central_operation_id')}")
        owner = record.get("pipeline_context_id", "")
        if owner.startswith("ppl.") and owner not in context_ids:
            fail(f"{record.get('mapping_id')}: unknown pipeline context {owner}")

    schemas = {}
    for path in sorted((ROOT / "schemas").glob("*.schema.json")):
        schema = load_json(path)
        if schema:
            schemas[path.name] = schema
            if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                fail(f"{path}: not JSON Schema 2020-12")
            if schema.get("additionalProperties") is not False:
                fail(f"{path}: top-level additionalProperties must be false")
    expected_schema_files = {"pipeline-definition.schema.json", "node-definition.schema.json", "edge-definition.schema.json", "port-definition.schema.json", "state-contract.schema.json", "delivery-contract.schema.json", "recovery-contract.schema.json", "data-cut.schema.json", "compiled-plan.schema.json", "deployment.schema.json", "pipeline-run.schema.json", "task-attempt.schema.json", "materialization.schema.json"}
    if set(schemas) != expected_schema_files:
        fail(f"schema set mismatch: missing {sorted(expected_schema_files - set(schemas))}, extra {sorted(set(schemas) - expected_schema_files)}")

    examples = {
        "pipeline-definition.schema.json": [("pipeline", load_json(ROOT / "examples" / "cdc-snapshot-handoff.pipeline.json"))],
        "node-definition.schema.json": [("node", value) for value in load_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.nodes.jsonl")],
        "edge-definition.schema.json": [("edge", value) for value in load_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.edges.jsonl")],
        "port-definition.schema.json": [("port", value) for value in load_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.ports.jsonl")],
        "state-contract.schema.json": [("state", value) for value in load_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.states.jsonl")],
        "delivery-contract.schema.json": [("delivery", load_json(ROOT / "examples" / "cdc-snapshot-handoff.delivery.json"))],
        "recovery-contract.schema.json": [("recovery", load_json(ROOT / "examples" / "cdc-snapshot-handoff.recovery.json"))],
        "data-cut.schema.json": [("cut", load_json(ROOT / "examples" / "cdc-snapshot-handoff.data-cut.json"))],
        "compiled-plan.schema.json": [("plan", load_json(ROOT / "examples" / "cdc-snapshot-handoff.compiled-plan.json"))],
        "deployment.schema.json": [("deployment", load_json(ROOT / "examples" / "cdc-snapshot-handoff.deployment.json"))],
        "pipeline-run.schema.json": [("run", load_json(ROOT / "examples" / "cdc-snapshot-handoff.run.json"))],
        "task-attempt.schema.json": [("attempt", value) for value in load_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.attempts.jsonl")],
        "materialization.schema.json": [("materialization", load_json(ROOT / "examples" / "cdc-snapshot-handoff.materialization.json"))],
    }
    for schema_name, instances in examples.items():
        for index, (label, instance) in enumerate(instances):
            if instance is not None:
                validate_instance(instance, schemas[schema_name], f"example.{label}[{index}]")

    pipeline = examples["pipeline-definition.schema.json"][0][1] or {}
    nodes = [item[1] for item in examples["node-definition.schema.json"]]
    edges = [item[1] for item in examples["edge-definition.schema.json"]]
    ports = [item[1] for item in examples["port-definition.schema.json"]]
    states = [item[1] for item in examples["state-contract.schema.json"]]
    node_ids = unique(nodes, "node_id", "example nodes")
    edge_ids = unique(edges, "edge_id", "example edges")
    port_ids = unique(ports, "port_id", "example ports")
    state_ids = unique(states, "state_contract_id", "example states")
    if set(pipeline.get("node_refs", [])) != node_ids:
        fail("example pipeline node refs do not equal example node registry")
    if set(pipeline.get("edge_refs", [])) != edge_ids:
        fail("example pipeline edge refs do not equal example edge registry")
    if set(pipeline.get("state_contract_refs", [])) != state_ids:
        fail("example pipeline state refs do not equal example state registry")
    port_by_id = {port["port_id"]: port for port in ports}
    for node in nodes:
        for ref in node.get("input_port_refs", []) + node.get("output_port_refs", []):
            if ref not in port_ids:
                fail(f"{node['node_id']}: unknown port {ref}")
        for ref in node.get("state_contract_refs", []):
            if ref not in state_ids:
                fail(f"{node['node_id']}: unknown state {ref}")
        for ref in node.get("operation_refs", []):
            if ref not in central_ids:
                fail(f"{node['node_id']}: unknown operation {ref}")
    for edge in edges:
        source = port_by_id.get(edge.get("from_port_ref"))
        target = port_by_id.get(edge.get("to_port_ref"))
        if source is None or target is None:
            fail(f"{edge.get('edge_id')}: unresolved port")
        elif source["direction"] != "output" or target["direction"] != "input":
            fail(f"{edge.get('edge_id')}: edge direction invalid")

    artifacts = [
        pipeline.get("definition_id"),
        examples["compiled-plan.schema.json"][0][1].get("plan_id"),
        examples["deployment.schema.json"][0][1].get("deployment_id"),
        examples["pipeline-run.schema.json"][0][1].get("run_id"),
        examples["data-cut.schema.json"][0][1].get("data_cut_id"),
        examples["materialization.schema.json"][0][1].get("materialization_id"),
    ] + [attempt.get("attempt_id") for _, attempt in examples["task-attempt.schema.json"]]
    if len(artifacts) != len(set(artifacts)):
        fail("definition/plan/deployment/run/attempt/cut/materialization identities are not distinct")

    mode_matrix = load_json(ROOT / "execution-mode-matrix.json") or []
    required_modes = {"pipeline-mode.bounded_batch", "pipeline-mode.microbatch", "pipeline-mode.continuous_stream", "pipeline-mode.cdc", "pipeline-mode.incremental", "pipeline-mode.federated", "pipeline-mode.reverse_delivery"}
    found_modes = {item.get("mode_id") for item in mode_matrix}
    if found_modes != required_modes:
        fail(f"execution mode matrix mismatch: {sorted(required_modes - found_modes)}")
    topology_matrix = load_json(ROOT / "topology-matrix.json") or []
    if not {"pipeline-topology.dag", "pipeline-topology.feedback_fixed_point", "pipeline-topology.productive_cycle", "pipeline-topology.dynamic_map"}.issubset({item.get("topology_id") for item in topology_matrix}):
        fail("topology matrix misses DAG/cyclic/productive/dynamic patterns")

    expected_counts = manifest.get("counts", {})
    actual_counts = {"primary_sources": len(sources), "bounded_context_candidates": len(contexts), "decision_points": len(decisions), "failures_and_refusals": len(outcomes), "innovations_2021_2026": len(innovations), "library_boundaries": len(libraries), "compiler_requirements": len(requirements), "offer_templates": len(offers), "central_operation_mappings": len(mappings), "known_gaps": len(gaps), "schemas": len(schemas), "lifecycles": len(lifecycles), "artifact_kinds": len(artifact_kinds)}
    if expected_counts != actual_counts:
        fail(f"manifest counts differ: expected {expected_counts}, actual {actual_counts}")
    if manifest.get("completion_claim") is not False:
        fail("research corpus must not claim completeness")

    # Prevent accidental weakening of the core scope.
    if len(context_ids) < 35 or len(decision_ids) < 65 or len(library_ids) < 25 or len(mapping_ids) < 140 or len(innovation_ids) < 10 or len(gap_ids) < 10:
        fail("coverage floor regressed")
    readme = (ROOT / "README.md").read_text()
    for phrase in ("vendor DAG document", "Exactly once", "compression", "definition", "compiled physical plan", "task attempt", "data cut", "materialization"):
        if phrase.lower() not in readme.lower():
            fail(f"README misses required distinction phrase: {phrase}")

    return actual_counts


def main() -> int:
    counts = validate()
    if ERRORS:
        print("FAIL pipeline/dataflow corpus")
        for error in ERRORS:
            print(f"- {error}")
        return 1
    print("PASS pipeline/dataflow corpus")
    print(json.dumps(counts, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
