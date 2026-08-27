#!/usr/bin/env python3
"""Validate the operations-research candidate corpus without third-party packages."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def validate_manifest() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["completion_claim"] is False
    for name, claim in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name


def load(name: str) -> list[dict]:
    rows: list[dict] = []
    for line_no, line in enumerate((ROOT / name).read_text().splitlines(), 1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{line_no}: invalid JSON: {exc}") from exc
        assert isinstance(value, dict), f"{name}:{line_no}: record must be an object"
        rows.append(value)
    return rows


def unique(rows: list[dict], field: str, name: str) -> set[str]:
    values = [row.get(field) for row in rows]
    assert all(isinstance(value, str) and value for value in values), f"{name}: missing {field}"
    repeated = [value for value, count in Counter(values).items() if count > 1]
    assert not repeated, f"{name}: duplicate {field}: {repeated}"
    return set(values)


def require_fields(rows: list[dict], fields: set[str], name: str) -> None:
    for index, row in enumerate(rows, 1):
        missing = fields - row.keys()
        assert not missing, f"{name}:{index}: missing fields {sorted(missing)}"
        for field in fields:
            assert row[field] not in (None, "", []), f"{name}:{index}: empty field {field}"


def validate_evidence(rows: list[dict], source_ids: set[str], name: str) -> None:
    for index, row in enumerate(rows, 1):
        refs = row.get("evidence_refs")
        assert isinstance(refs, list) and refs, f"{name}:{index}: evidence_refs must be nonempty"
        unknown = set(refs) - source_ids
        assert not unknown, f"{name}:{index}: unknown evidence refs {sorted(unknown)}"


def main() -> None:
    before_rebuild = {str(path.relative_to(ROOT)): path.read_bytes() for path in ROOT.rglob("*.json*")}
    rebuilt = subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], capture_output=True, text=True, check=False)
    after_rebuild = {str(path.relative_to(ROOT)): path.read_bytes() for path in ROOT.rglob("*.json*")}
    assert rebuilt.returncode == 0 and before_rebuild == after_rebuild, "deterministic rebuild drift or builder failure"
    validate_manifest()
    gap_schema = json.loads((ROOT / "gap.schema.json").read_text())
    gaps = load("gaps.jsonl")
    required_gap_fields = set(gap_schema["required"])
    allowed_gap_fields = set(gap_schema["properties"])
    allowed_gap_classes = set(gap_schema["properties"]["gap_class"]["enum"])
    assert len(gaps) == 5
    for gap in gaps:
        assert required_gap_fields <= set(gap) <= allowed_gap_fields
        assert gap["gap_class"] in allowed_gap_classes and gap["status"] == "OPEN"
        assert all(gap[field] for field in ("semantic_axes", "scope_refs", "closure_evidence", "blocked_outputs"))
    sources = load("sources.jsonl")
    methods = load("methods.jsonl")
    experts = load("experts.jsonl")
    companies = load("companies.jsonl")
    innovations = load("innovations.jsonl")
    contexts = load("bounded-context-candidates.jsonl")
    decisions = load("decision-points.jsonl")
    libraries = load("library-boundaries.jsonl")
    compiler_records = load("compiler-requirements-offers.jsonl")
    profiles = load("qualification-receipts.jsonl")

    source_ids = unique(sources, "source_id", "sources")
    method_ids = unique(methods, "method_id", "methods")
    unique(experts, "expert_id", "experts")
    unique(companies, "company_id", "companies")
    unique(innovations, "innovation_id", "innovations")
    unique(contexts, "context_id", "contexts")
    decision_ids = unique(decisions, "decision_id", "decisions")
    library_ids = unique(libraries, "library_id", "libraries")
    requirements = {
        row["requirement_id"]: row for row in compiler_records if row.get("record_kind") == "capability_requirement"
    }
    offers = {
        row["offer_id"]: row for row in compiler_records if row.get("record_kind") == "capability_offer"
    }
    assert len(requirements) + len(offers) == len(compiler_records), "unknown compiler record kind"
    assert len(requirements) == len(set(requirements)), "duplicate requirement id"
    assert len(offers) == len(set(offers)), "duplicate offer id"
    profile_ids = unique(profiles, "receipt_id", "qualification profiles")

    assert len(sources) >= 30, "at least 30 primary/official sources are required"
    assert len(methods) >= 250, "broad OR enumeration regressed below 250 practices"
    assert len(experts) >= 25, "representative expertise coverage regressed"
    assert len(companies) >= 15, "specialist-company pattern coverage regressed"
    assert len(innovations) >= 15, "five-year innovation coverage regressed"
    assert len(contexts) >= 30, "bounded-context candidate coverage regressed"
    assert len(decisions) >= 18, "compiler decision surface regressed"
    assert len(libraries) >= 16, "compiler library decomposition regressed"
    assert len(requirements) == len(libraries), "every OR library must expose one requirement"
    assert len(offers) >= 8, "provider observation and exact-artifact surface regressed"
    assert len(profiles) == len(libraries), "every OR library must have a qualification profile"
    assert sum(bool(row.get("primary_or_official")) for row in sources) >= 30

    require_fields(methods, {
        "method_id", "edition", "status", "family_id", "name", "intent", "inputs", "outputs",
        "assumptions", "guarantees", "failure_result_states", "runtime_budget", "evidence_refs",
        "compiler_implications", "gaps", "llm_dependency",
    }, "methods")
    require_fields(contexts, {
        "context_id", "edition", "status", "boundary_question", "inside", "outside", "intent",
        "inputs", "outputs", "assumptions", "guarantees", "failure_result_states", "runtime_budget",
        "evidence_refs", "compiler_implications", "gaps", "not_automatically_promoted_from",
        "llm_dependency",
    }, "contexts")
    require_fields(companies, {
        "company_id", "name", "claimed_capabilities", "verified_capabilities", "evidence_posture",
        "evidence_refs", "compiler_learnings", "limitations", "llm_core_dependency",
    }, "companies")
    require_fields(innovations, {
        "innovation_id", "name", "year", "evidence_posture", "non_llm", "problem_and_innovation",
        "evidence_refs", "limits", "compiler_implications",
    }, "innovations")
    require_fields(libraries, {
        "library_id", "edition", "status", "library_kind", "semantic_owner_refs",
        "contributes_to_context_refs", "effect_boundary", "public_types", "public_traits",
        "operation_refs", "error_contracts", "decision_refs", "requirement_refs", "laws",
        "oracles", "resource_contracts", "forbidden_responsibilities", "evidence_refs", "gaps",
    }, "libraries")
    require_fields(profiles, {
        "receipt_id", "edition", "record_kind", "status", "subject_ref", "claim", "scope",
        "fixtures", "oracles", "limitations", "invalidation_triggers",
    }, "qualification profiles")

    for rows, name in [
        (methods, "methods"), (experts, "experts"), (companies, "companies"),
        (innovations, "innovations"), (contexts, "contexts"),
    ]:
        validate_evidence(rows, source_ids, name)

    expected_families = {
        "or.family.framing", "or.family.mathematical_programming", "or.family.constraint_logic",
        "or.family.exact_algorithm", "or.family.decomposition", "or.family.approximation_online",
        "or.family.constructive_heuristic", "or.family.local_metaheuristic", "or.family.hybrid_search",
        "or.family.network_combinatorial", "or.family.routing", "or.family.scheduling",
        "or.family.inventory_planning", "or.family.queues_reliability", "or.family.simulation",
        "or.family.sequential_control", "or.family.markets_games_revenue", "or.family.human_decision",
        "or.family.postsolve_qualification",
    }
    actual_families = {row["family_id"] for row in methods}
    assert expected_families <= actual_families, f"missing method families: {sorted(expected_families - actual_families)}"

    required_methods = {
        "or.method.robust_optimization", "or.method.two_stage_stochastic_programming",
        "or.method.benders_decomposition", "or.method.constant_factor_approximation",
        "or.method.greedy_construction", "or.method.adaptive_large_neighborhood_search",
        "or.method.hyperheuristic", "or.method.matheuristic", "or.method.queueing_analysis",
        "or.method.discrete_event_simulation", "or.method.agent_based_simulation",
        "or.method.vehicle_routing_time_windows", "or.method.job_shop_scheduling",
        "or.method.infeasibility_diagnosis", "or.method.actual_vs_planned_reconciliation",
    }
    assert required_methods <= method_ids, f"missing anchor methods: {sorted(required_methods - method_ids)}"

    for row in methods:
        assert row["llm_dependency"] == "none", f"LLM dependency leaked into {row['method_id']}"
        assert row["runtime_budget"].get("cancellation_contract_required") is True
        states = set(row["failure_result_states"])
        assert {"invalid_model_or_data", "unsupported_capability", "resource_limit_with_incumbent", "resource_limit_without_incumbent"} <= states

    abm = next(row for row in methods if row["method_id"] == "or.method.agent_based_simulation")
    assert "not an LLM" in abm["intent"], "agent-based simulation must remain disambiguated from LLM agents"

    for row in contexts:
        assert row["status"] == "candidate_not_adjudicated"
        assert row["llm_dependency"] == "none"
        blockers = set(row["not_automatically_promoted_from"])
        assert {"algorithm name", "vendor feature"} <= blockers

    for row in companies:
        assert row["claimed_capabilities"] != row["verified_capabilities"], f"claims collapsed into verification for {row['company_id']}"
        assert row["llm_core_dependency"] == "not_required_for_the_classified_or_capabilities"

    for row in innovations:
        assert 2021 <= row["year"] <= 2026, f"innovation outside five-year window: {row['innovation_id']}"
        assert row["non_llm"] is True, f"LLM innovation leaked into core: {row['innovation_id']}"
        assert row["limits"], f"innovation has no limitations: {row['innovation_id']}"

    required_libraries = {
        "library.operations_research.decision_problem_semantics",
        "library.operations_research.objective_preference_algebra",
        "library.operations_research.constraint_policy_algebra",
        "library.operations_research.optimization_model_ir",
        "library.operations_research.solver_capability_contract",
        "library.operations_research.optimization_solve_execution",
        "library.operations_research.optimization_result_algebra",
        "library.operations_research.optimization_solution_validation",
        "library.operations_research.infeasibility_diagnosis",
        "library.operations_research.heuristic_search_contract",
        "library.operations_research.queue_model_semantics",
        "library.operations_research.queue_performance_methods",
        "library.operations_research.queue_network_methods",
        "library.operations_research.queue_inference_calibration",
        "library.operations_research.queue_model_validation",
        "library.operations_research.simulation_model_semantics",
        "library.operations_research.simulation_experiment_design",
        "library.operations_research.simulation_random_stream_control",
        "library.operations_research.simulation_execution",
        "library.operations_research.simulation_output_analysis",
        "library.operations_research.simulation_verification_validation",
    }
    assert required_libraries <= library_ids, f"missing OR compiler libraries: {sorted(required_libraries - library_ids)}"
    for row in libraries:
        assert row["status"] == "specified", f"premature library status: {row['library_id']}"
        assert len(row["semantic_owner_refs"]) == 1, f"library lacks a single semantic owner: {row['library_id']}"
        assert set(row["semantic_owner_refs"]) <= {item["context_id"] for item in contexts}
        assert set(row["decision_refs"]) <= decision_ids, f"unknown decision ref: {row['library_id']}"
        assert set(row["evidence_refs"]) <= source_ids, f"unknown library evidence: {row['library_id']}"
        expected_requirement = row["library_id"].replace("library.operations_research.", "requirement.operations_research.")
        assert row["requirement_refs"] == [expected_requirement]
        assert "LLM/generative dependency" in row["forbidden_responsibilities"]

    for requirement_id, row in requirements.items():
        assert row["status"] == "declared", f"premature requirement status: {requirement_id}"
        assert row["subject_ref"] in library_ids, f"unknown requirement subject: {requirement_id}"
        assert row["fallback_law"] == "refuse", f"unsafe fallback: {requirement_id}"
        assert row["evidence_gates"], f"missing evidence gates: {requirement_id}"

    for offer_id, row in offers.items():
        assert row["status"] in {
            "declared", "executed_not_appraised_not_qualified"
        }, f"premature provider qualification: {offer_id}"
        assert row.get("binding_eligible") is False, f"unqualified offer became bindable: {offer_id}"
        assert row["conformance_receipts"] == [], f"invented conformance receipt: {offer_id}"
        assert row["evidence_refs"] and set(row["evidence_refs"]) <= source_ids
        assert row["limits"] and row["exclusions"] and row["gaps"]

    exact_offers = {
        offer_id: row for offer_id, row in offers.items()
        if row.get("offer_kind") == "exact_adapter_artifact_offer"
    }
    assert set(exact_offers) == {
        "offer.operations_research.ortools.glop.mpsolver_python.9_15_6755",
        "offer.operations_research.highspy.highs.1_15_1",
        "offer.operations_research.ortools.cp_sat.python.9_15_6755",
    }
    workspace = ROOT.parents[3]
    for offer_id, row in exact_offers.items():
        assert row["status"] == "executed_not_appraised_not_qualified"
        assert row["executed_test_receipt_refs"]
        assert row["passed_contract_refs"]
        for receipt_ref in row["executed_test_receipt_refs"]:
            relative, receipt_id = receipt_ref.split("#", 1)
            receipt_path = workspace / relative
            assert receipt_path.is_file(), f"{offer_id}: unresolved execution evidence {relative}"
            receipts = {
                value["receipt_id"]: value
                for value in (json.loads(line) for line in receipt_path.read_text().splitlines())
            }
            assert receipt_id in receipts, f"{offer_id}: unresolved receipt {receipt_id}"
            assert receipts[receipt_id]["subject"] == offer_id
        assert row["conformance_receipts"] == [], "executed tests cannot impersonate qualification receipts"

    ortools_exact = exact_offers["offer.operations_research.ortools.glop.mpsolver_python.9_15_6755"]
    highs_exact = exact_offers["offer.operations_research.highspy.highs.1_15_1"]
    cp_sat_exact = exact_offers["offer.operations_research.ortools.cp_sat.python.9_15_6755"]
    assert ortools_exact["contract_refs"] == ["contract.operations_research.lp.safe_status_and_objective.v1"]
    assert ortools_exact["failed_contract_refs"] == ["contract.operations_research.lp.precise_terminal_classification.v1"]
    assert "contract.operations_research.lp.precise_terminal_classification.v1" in highs_exact["contract_refs"]
    assert highs_exact["failed_contract_refs"] == []
    assert {
        "contract.operations_research.cp_sat.core.v1",
        "contract.operations_research.cp_sat.global_constraints.v1",
        "contract.operations_research.cp_sat.fixed_interval_scheduling.v1",
        "contract.operations_research.cp_sat.complete_enumeration.v1",
        "contract.operations_research.cp_sat.unknown_limit_no_strengthening.v1",
    } == set(cp_sat_exact["contract_refs"])
    assert cp_sat_exact["failed_contract_refs"] == [
        "contract.operations_research.cp_sat.pre_parameter_complete_enumeration.v1"
    ]
    assert len(cp_sat_exact["executed_test_receipt_refs"]) == 6

    required_profiles = {
        library_id.replace("library.operations_research.", "receipt.operations_research.")
        for library_id in library_ids
    }
    assert required_profiles == profile_ids, f"qualification-profile coverage drift: {sorted(required_profiles ^ profile_ids)}"
    for row in profiles:
        assert row["record_kind"] == "qualification_profile"
        assert row["status"] == "template_not_executed"
        assert row["subject_ref"] in library_ids
        assert row["results"] == []
        assert row["fixtures"] and row["oracles"]
        assert any("proves no provider capability" in item for item in row["limitations"])

    urls = [row["url"] for row in sources]
    assert all(url.startswith("https://") for url in urls), "all evidence URLs must be HTTPS"

    print(
        "PASS operations-research universe: "
        f"{len(methods)} methods, {len(contexts)} contexts, {len(sources)} sources, "
        f"{len(experts)} experts, {len(companies)} companies, {len(innovations)} innovations; "
        f"{len(libraries)} compiler libraries, {len(decisions)} decisions, {len(offers)} unqualified offers"
    )


if __name__ == "__main__":
    main()
