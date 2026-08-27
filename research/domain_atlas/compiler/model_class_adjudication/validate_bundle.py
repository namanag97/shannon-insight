#!/usr/bin/env python3
"""Validate model-class adjudication structure and executable trace semantics."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import build_bundle as build


ROOT = Path(__file__).resolve().parent


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ids(rows: list[dict], filename: str) -> set[str]:
    values = [row.get("id") for row in rows]
    if any(not value for value in values):
        fail(f"{filename}: missing id")
    if len(values) != len(set(values)):
        fail(f"{filename}: duplicate id")
    return set(values)


def main() -> None:
    manifest = load_json(ROOT / "manifest.json")
    metamodel = load_json(ROOT / "metamodel.json")
    catalogs = {filename: load_jsonl(ROOT / filename) for filename in build.CATALOGS}
    results = load_jsonl(ROOT / "adjudication-results.jsonl")

    if manifest["completion_claim"] is not False or metamodel["completion_claim"] is not False:
        fail("finite candidate made a completion claim")
    if manifest["qualified_provider_offers"] != 0 or manifest["vertical_acceptance_receipts"] != 0:
        fail("adjudication candidate fabricated provider qualification or vertical acceptance")

    for filename in manifest["generated_files"]:
        path = ROOT / filename
        if not path.exists():
            fail(f"manifest references missing file: {filename}")
        if manifest["file_sha256"][filename] != sha256(path):
            fail(f"digest mismatch: {filename}")

    for filename, expected in manifest["record_counts"].items():
        actual = len(results) if filename == "adjudication-results.jsonl" else len(catalogs[filename])
        if actual != expected:
            fail(f"{filename}: count {actual} != manifest {expected}")

    all_ids: dict[str, set[str]] = {filename: ids(rows, filename) for filename, rows in catalogs.items()}
    all_ids["adjudication-results.jsonl"] = ids(results, "adjudication-results.jsonl")
    flattened: list[str] = [record_id for id_set in all_ids.values() for record_id in id_set]
    if len(flattened) != len(set(flattened)):
        fail("record id collision across files")

    source_ids = all_ids["sources.jsonl"]
    axis_ids = all_ids["classification-axes.jsonl"]
    atom_rows = catalogs["feature-atoms.jsonl"]
    atom_symbols = {row["symbol"] for row in atom_rows}
    class_rows = catalogs["model-classes.jsonl"]
    class_ids = all_ids["model-classes.jsonl"]
    refusal_ids = all_ids["refusal-rules.jsonl"]
    trace_ids = all_ids["classification-traces.jsonl"]

    if len(catalogs["classification-axes.jsonl"]) < 9:
        fail("classification axes are too thin")
    if len(atom_rows) < 85:
        fail("feature atom coverage is too thin")
    if len(class_rows) < 35:
        fail("model class coverage is too thin")
    if len(catalogs["transformation-kinds.jsonl"]) < 20:
        fail("model transformation coverage is too thin")
    if len(catalogs["transformation-traces.jsonl"]) < 7:
        fail("model transformation falsification coverage is too thin")
    if len(catalogs["provider-requirements.jsonl"]) != len(class_rows):
        fail("class-to-provider requirement projection is not total")
    if len(catalogs["proof-obligations.jsonl"]) < 25:
        fail("proof obligation coverage is too thin")
    if len(catalogs["refusal-rules.jsonl"]) < 25:
        fail("refusal coverage is too thin")
    if len(catalogs["classification-traces.jsonl"]) < 10:
        fail("classification trace coverage is too thin")

    for row in atom_rows:
        if row["axis_ref"] not in axis_ids:
            fail(f"{row['id']}: unknown axis {row['axis_ref']}")
        if row["absence_semantics"] != "unknown_unless_an_exclusive_sibling_is_proved":
            fail(f"{row['id']}: unsafe absence semantics")

    for row in class_rows:
        if not set(row["evidence_refs"]).issubset(source_ids):
            fail(f"{row['id']}: unknown evidence ref")
        predicate = row["sound_sufficient_predicate"]
        predicate_atoms = set(predicate["all_of"]) | set(predicate["none_of"])
        predicate_atoms |= {value for group in predicate["any_of_groups"] for value in group}
        unknown = predicate_atoms - atom_symbols
        if unknown:
            fail(f"{row['id']}: unknown predicate atom(s) {sorted(unknown)}")
        if set(predicate["all_of"]) & set(predicate["none_of"]):
            fail(f"{row['id']}: contradictory class predicate")
        if "provider requirements" not in row["binding_law"]:
            fail(f"{row['id']}: class-to-provider non-collapse law missing")
        if row["id"].startswith("class.mca.ai"):
            fail(f"{row['id']}: ambient AI class is forbidden")

    for row in catalogs["classification-rules.jsonl"]:
        if row["record_kind"] == "classification_rule" and row["class_ref"] not in class_ids:
            fail(f"{row['id']}: unknown class ref")

    for row in catalogs["proof-obligations.jsonl"]:
        if row["failure_ref"] not in refusal_ids:
            fail(f"{row['id']}: unknown refusal ref")
        if row["discharge_states"] != ["proved", "refuted", "unknown", "not_applicable"]:
            fail(f"{row['id']}: proof truth algebra changed")

    proof_ids = all_ids["proof-obligations.jsonl"]
    transformation_ids = all_ids["transformation-kinds.jsonl"]
    allowed_relations = {
        "semantic_equivalence",
        "bijective_solution_mapping_if_nonzero_finite",
        "equisatisfiable_with_decoding",
        "semantic_equivalence_under_orientation_and_domain",
        "semantic_equivalence_under_exact_cone_representation",
        "equisatisfiable_with_total_encoder_decoder",
        "outer_relaxation_bound_producing",
        "semantic_equivalence_only_with_domain_certificate",
        "bounded_approximation",
        "numerical_approximation_with_error_contract",
        "equivalent_relative_to_scenario_and_information_contract",
        "equivalent_relative_to_uncertainty_set",
        "one_sided_or_statistical_approximation",
        "statistical_approximation",
        "empirical_approximation",
        "equivalent_only_when_master_subproblem_protocol_closes",
        "equisatisfiable_or_equivalent_with_recovery_map",
        "bound_producing_relaxation",
        "weak_duality_bound_or_equivalence_under_strong_duality",
        "candidate_solution_generation",
        "statistical_estimation_not_equivalence",
        "compositional_approximation_or_equivalence_per_sync_contract",
    }
    for row in catalogs["transformation-kinds.jsonl"]:
        if row["semantic_relation"] not in allowed_relations:
            fail(f"{row['id']}: unknown transformation relation")
        if not set(row["source_class_refs"] + row["possible_target_class_refs"]).issubset(class_ids):
            fail(f"{row['id']}: unknown source/target model class")
        if not set(row["required_proof_refs"]).issubset(proof_ids):
            fail(f"{row['id']}: unknown transformation proof obligation")
        if not set(row["evidence_refs"]).issubset(source_ids):
            fail(f"{row['id']}: unknown transformation evidence")
        if row["applicability_status"] != "candidate_rule_not_executed":
            fail(f"{row['id']}: transformation overclaims execution")

    transformation_trace_ids = all_ids["transformation-traces.jsonl"]
    for row in catalogs["transformation-traces.jsonl"]:
        if row["transformation_ref"] not in transformation_ids:
            fail(f"{row['id']}: unknown transformation")
        if not set(row["source_class_refs"] + row["target_class_refs"]).issubset(class_ids):
            fail(f"{row['id']}: unknown trace class")
        transformation_row = next(item for item in catalogs["transformation-kinds.jsonl"] if item["id"] == row["transformation_ref"])
        if row["expected_relation"] != transformation_row["semantic_relation"]:
            fail(f"{row['id']}: relation drifted from transformation contract")
        if row["proof_receipt_refs"]:
            fail(f"{row['id']}: candidate trace fabricated proof receipts")
    if "transform_trace.mca.agent_claims_exact_linearization" not in transformation_trace_ids:
        fail("agent-proposed transformation negative twin is missing")
    agent_transform = next(row for row in catalogs["transformation-traces.jsonl"] if row["id"] == "transform_trace.mca.agent_claims_exact_linearization")
    if agent_transform.get("proposal_refs") != ["extension.generative_proposal"] or agent_transform["expected_disposition"] != "refused_proposal_is_not_proof":
        fail("agent proposal was admitted as transformation proof")
    relaxation = next(row for row in catalogs["transformation-kinds.jsonl"] if row["id"] == "transform.mca.continuous_relaxation")
    if relaxation["semantic_relation"] != "outer_relaxation_bound_producing" or "original-model optimality" not in relaxation["forbidden_claims"]:
        fail("continuous relaxation can be confused with the original model")

    provider_requirement_classes = []
    for row in catalogs["provider-requirements.jsonl"]:
        if row["class_ref"] not in class_ids:
            fail(f"{row['id']}: unknown provider requirement class")
        provider_requirement_classes.append(row["class_ref"])
        all_requirement_atoms = set(row["required_feature_atoms"]) | set(row["prohibited_feature_atoms"])
        all_requirement_atoms |= {value for group in row["required_any_of_feature_groups"] for value in group}
        if not all_requirement_atoms.issubset(atom_symbols):
            fail(f"{row['id']}: unknown feature in provider projection")
        if row["binding_status"] != "unbound_no_qualified_offer_asserted":
            fail(f"{row['id']}: provider requirement fabricated a binding")
        fallback = row["fallback_law"].lower()
        if "agent plan" not in fallback or "vendor name" not in fallback:
            fail(f"{row['id']}: unsafe provider fallback law")
    if sorted(provider_requirement_classes) != sorted(class_ids):
        fail("model class to provider requirement projection is not one-to-one")

    for row in catalogs["classification-traces.jsonl"]:
        unknown_facts = set(row["facts"]) - atom_symbols
        if unknown_facts:
            fail(f"{row['id']}: unknown facts {sorted(unknown_facts)}")
        unknown_classes = (set(row["requested_class_refs"]) | set(row["expected_class_refs"])) - class_ids
        if unknown_classes:
            fail(f"{row['id']}: unknown class refs {sorted(unknown_classes)}")
        unknown_blockers = set(row["external_blockers"]) - refusal_ids
        if unknown_blockers:
            fail(f"{row['id']}: unknown blockers {sorted(unknown_blockers)}")
        if row["negative_twin_ref"] and row["negative_twin_ref"] not in trace_ids:
            fail(f"{row['id']}: unknown negative twin")

        actual = build.adjudicate(row)
        if actual["matched_class_refs"] != row["expected_class_refs"]:
            fail(f"{row['id']}: actual classes {actual['matched_class_refs']} != expected {row['expected_class_refs']}")
        if actual["disposition"] != row["expected_disposition"]:
            fail(f"{row['id']}: disposition {actual['disposition']} != expected {row['expected_disposition']}")
        if actual["provider_bindable"] is not False:
            fail(f"{row['id']}: classifier fabricated a bindable provider")

    result_by_trace = {row["trace_ref"]: row for row in results}
    if set(result_by_trace) != trace_ids:
        fail("adjudication result coverage differs from trace coverage")
    for trace_row in catalogs["classification-traces.jsonl"]:
        actual = build.adjudicate(trace_row)
        stored = result_by_trace[trace_row["id"]]
        for field in ["matched_class_refs", "missing_requested_class_refs", "external_blockers", "disposition", "provider_bindable"]:
            if stored[field] != actual[field]:
                fail(f"{trace_row['id']}: stored adjudication drift in {field}")

    # The optional generative/tool-agent facts must not change an LP's class.
    lp = result_by_trace["trace.mca.fixture.continuous_lp"]
    lp_agent = result_by_trace["trace.mca.fixture.lp_with_llm_proposal"]
    if lp["matched_class_refs"] != lp_agent["matched_class_refs"]:
        fail("optional model/agent extension changed deterministic model classification")

    # A modeled ABM entity is not an optional tool-agent dependency.
    ecology_trace = next(row for row in catalogs["classification-traces.jsonl"] if row["id"] == "trace.mca.ecology.agent_based")
    if "extension.modeled_entity_agent" not in ecology_trace["facts"]:
        fail("ABM modeled-agent semantics missing")
    if {"extension.generative_proposal", "extension.tool_agent"} & set(ecology_trace["facts"]):
        fail("ABM trace acquired ambient LLM/tool-agent semantics")

    # The broad pipeline problem must remain unclassified while the closed screen may be LP,
    # but still cannot be deployed through provider or vertical inference.
    broad = result_by_trace["trace.mca.pipeline.broad_unclosed"]
    screen = result_by_trace["trace.mca.pipeline.lp_screen"]
    if broad["matched_class_refs"]:
        fail("open pipeline problem was forced into a class")
    if screen["matched_class_refs"] != ["class.mca.continuous_lp"]:
        fail("closed pipeline screen did not classify exactly as continuous LP")
    if screen["disposition"] != "classified_but_vertical_unaccepted":
        fail("pipeline screen bypassed vertical acceptance")

    laws = " ".join(metamodel["constitutional_laws"]).lower()
    for required in [
        "classification is multi-axis",
        "predictive/statistical fitted models",
        "agent-based simulation entities",
        "generative models and tool agents may propose",
        "removing every generative/agent extension",
        "analytical result is a proposal",
    ]:
        if required not in laws:
            fail(f"constitutional law missing: {required}")

    for key, path in build.UPSTREAM_FILES.items():
        current = sha256(path)
        if metamodel["upstream_snapshot_digests"].get(key) != current:
            fail(f"upstream snapshot drift: {key}; rebuild and review")
        if manifest["upstream_snapshot_digests"].get(key) != current:
            fail(f"manifest upstream snapshot drift: {key}")

    print(
        "PASS model-class adjudication candidate: "
        f"{len(atom_rows)} feature atoms, {len(class_rows)} class facets, "
        f"{len(catalogs['transformation-kinds.jsonl'])} transformation relations, "
        f"{len(catalogs['proof-obligations.jsonl'])} proof obligations, "
        f"{len(catalogs['refusal-rules.jsonl'])} refusals, "
        f"{len(catalogs['classification-traces.jsonl'])} deterministic traces; "
        "optional LLM/agent extension is classification-invariant; no provider binding fabricated"
    )


if __name__ == "__main__":
    try:
        main()
    except (ValidationError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
