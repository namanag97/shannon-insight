#!/usr/bin/env python3
"""Build the deterministic product qualification and vertical-acceptance program."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
READINESS = ROOT / "research/product_ontology/dossier_readiness"
ADJUDICATIONS = ROOT / "research/product_ontology/adjudications"
VERTICALS = ROOT / "research/product_ontology/composition_pilots/deterministic_verticals"
CE = ROOT / "research/domain_atlas/compiler/conformance_evaluation"
PTR = ROOT / "research/domain_atlas/compiler/provider_target_registry"
EXECUTIONS = ROOT / "research/domain_atlas/compiler/conformance_evaluation/executions"
AS_OF = "2026-08-26"


GATES = [
    ("gate.qp.boundary_ddd", "Exact product boundary and complete DDD", [], "structural"),
    ("gate.qp.contract_decomposition", "Exact product/library/compiler decomposition", ["gate.qp.boundary_ddd"], "structural"),
    ("gate.qp.law_authority", "Accountable semantic-law and oracle authority", ["gate.qp.contract_decomposition"], "semantic"),
    ("gate.qp.implementation_identity", "Digest-bound implementation subject identity", ["gate.qp.law_authority"], "implementation"),
    ("gate.qp.reproducible_build", "Reproducible build, dependency and supply-chain evidence", ["gate.qp.implementation_identity"], "implementation"),
    ("gate.qp.exact_scope_execution", "Executed exact-scope conformance suites", ["gate.qp.reproducible_build"], "execution"),
    ("gate.qp.independent_appraisal", "Independent appraisal of retained evidence", ["gate.qp.exact_scope_execution"], "appraisal"),
    ("gate.qp.first_qualified_implementation", "First qualified implementation for exact scope", ["gate.qp.independent_appraisal"], "qualification"),
    ("gate.qp.second_independent_implementation", "Second independently controlled qualified implementation", ["gate.qp.first_qualified_implementation"], "portability"),
    ("gate.qp.differential_exit", "Cross-implementation differential, migration and exit drill", ["gate.qp.second_independent_implementation"], "portability"),
    ("gate.qp.portable_offer", "Portable capability offer", ["gate.qp.differential_exit"], "portability"),
    ("gate.qp.physical_binding", "Exact target binding and operational envelope", ["gate.qp.first_qualified_implementation"], "physical"),
    ("gate.qp.two_vertical_structures", "Unchanged semantics in two unrelated vertical structures", ["gate.qp.contract_decomposition"], "generality"),
    ("gate.qp.executed_vertical_acceptance", "Executed domain-owner acceptance on a physical occurrence", ["gate.qp.physical_binding", "gate.qp.two_vertical_structures"], "acceptance"),
    ("gate.qp.build_ready", "Product build-readiness verdict", ["gate.qp.portable_offer", "gate.qp.executed_vertical_acceptance"], "product"),
    ("gate.qp.ratification", "Accountable product ratification", ["gate.qp.build_ready"], "product"),
]


EVIDENCE_NEEDED = {
    "gate.qp.contract_decomposition": ["exact compiler contract for every attributed library", "no unresolved blocking binding gap"],
    "gate.qp.law_authority": ["named semantic owner", "editioned executable laws and refusal oracles", "approved populations, tolerances and residual risks"],
    "gate.qp.implementation_identity": ["artifact digest", "source provenance", "implementation edition", "maintainer/control identity"],
    "gate.qp.reproducible_build": ["dependency-lock digest", "toolchain and target digest", "SBOM and provenance", "independent rebuild result"],
    "gate.qp.exact_scope_execution": ["configuration digest", "target occurrence", "population/corpus digest", "all attempts and counterexamples", "exact-scope receipts"],
    "gate.qp.independent_appraisal": ["appraiser identity and independence assessment", "scoped appraisal receipt", "limitations and invalidation triggers"],
    "gate.qp.first_qualified_implementation": ["current exact-scope qualification receipt for every required library", "composition-law evidence", "no active disqualifying counterexample"],
    "gate.qp.second_independent_implementation": ["second qualified artifact", "independent control and code/test/oracle lineage", "separate build and execution evidence"],
    "gate.qp.differential_exit": ["cross-implementation differential corpus", "semantic compatibility result", "state/data export-import drill", "loss and rollback receipts"],
    "gate.qp.portable_offer": ["two independent qualified implementations", "portable carrier/interface profile", "version and substitution envelope"],
    "gate.qp.physical_binding": ["exact target occurrence", "finite resource/time/cost budgets", "security/privacy/location evidence", "SLO, failure, cancellation and recovery receipts"],
    "gate.qp.two_vertical_structures": ["two unrelated vertical compositions", "unchanged horizontal contract editions", "semantic diffs and domain-owner criteria"],
    "gate.qp.executed_vertical_acceptance": ["accepted source occurrences and data cuts", "qualified physical binding", "runtime/effect receipts", "harm and outcome review", "domain-owner verdict"],
    "gate.qp.build_ready": ["all prerequisite gate receipts", "open-risk register", "operations, support, rollback and exit evidence"],
    "gate.qp.ratification": ["accountable ratifier", "bounded verdict", "validity interval", "residual owner and revocation conditions"],
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def render_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(canonical(row) + "\n" for row in sorted(rows, key=record_identity))


def record_identity(row: dict[str, Any]) -> str:
    for key in ("gate_id", "edge_id", "program_id", "subject_id", "binding_id", "vacancy_id", "acceptance_program_id"):
        if key in row:
            return str(row[key])
    raise ValueError(f"record has no identity: {row}")


def product_ref_matches(row: dict[str, Any], product_ref: str) -> bool:
    return row.get("product_ref") == product_ref or product_ref in row.get("product_refs", [])


def compiler_gap_refs(mapping: dict[str, Any]) -> list[str]:
    refs = list(mapping.get("blocking_gap_refs", []))
    if mapping.get("gap_ref"):
        refs.append(mapping["gap_ref"])
    return sorted(set(refs))


def oracle_contexts(library: dict[str, Any]) -> list[str]:
    text = " ".join(
        str(value)
        for value in (
            library.get("library_id"), library.get("class"), library.get("effect_boundary"),
            library.get("types"), library.get("operations"), library.get("invariants"),
            library.get("refusals"), library.get("decisions"),
        )
    ).lower()
    contexts = {
        "context.ce.structural_schema", "context.ce.static_type", "context.ce.api_surface",
        "context.ce.algebraic_law", "context.ce.domain_invariant", "context.ce.property_based",
        "context.ce.metamorphic", "context.ce.differential", "context.ce.coverage",
        "context.ce.supply_chain", "context.ce.reproducibility", "context.ce.deterministic_build",
    }
    effect = str(library.get("effect_boundary", ""))
    if effect != "pure_no_io":
        contexts |= {
            "context.ce.model_based", "context.ce.fuzz_stateful", "context.ce.failure_injection",
            "context.ce.replay", "context.ce.access_control", "context.ce.performance_latency",
            "context.ce.performance_throughput", "context.ce.resource_memory", "context.ce.cost",
        }
    keyword_contexts = {
        "serial": "context.ce.serialization", "canonical": "context.ce.canonicalization",
        "stream": "context.ce.streaming", "temporal": "context.ce.temporal",
        "time": "context.ce.temporal", "geo": "context.ce.geospatial",
        "spatial": "context.ce.geospatial", "document": "context.ce.document",
        "graph": "context.ce.graph", "process": "context.ce.process_mining",
        "optim": "context.ce.optimization", "forecast": "context.ce.predictive_validation",
        "predict": "context.ce.predictive_validation", "calibrat": "context.ce.calibration",
        "uncertainty": "context.ce.uncertainty", "statistic": "context.ce.statistical_power",
        "privacy": "context.ce.privacy", "reconcil": "context.ce.reconciliation",
        "lineage": "context.ce.lineage", "quality": "context.ce.data_quality",
        "recover": "context.ce.crash_recovery", "restore": "context.ce.restore",
        "migration": "context.ce.migration", "security": "context.ce.threat_abuse",
    }
    for keyword, context in keyword_contexts.items():
        if keyword in text:
            contexts.add(context)
    return sorted(contexts)


def load_execution_bindings() -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for path in sorted(EXECUTIONS.rglob("qualification-binding.json")):
        source = json.loads(path.read_text(encoding="utf-8"))
        if source.get("record_kind") != "qualification_execution_evidence_binding":
            raise ValueError(f"{path}: unexpected record_kind")
        relative = path.relative_to(ROOT).as_posix()
        subject_ref = source["qualification_subject_ref"]
        gate_ref = source["relevant_gate_ref"]
        bindings.append(
            {
                **source,
                "binding_id": f"binding.qp.{subject_ref.removeprefix('subject.qp.')}.{gate_ref.removeprefix('gate.qp.')}",
                "source_ref": relative,
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return bindings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    readiness = load_jsonl(READINESS / "product-readiness.jsonl")
    execution_bindings = load_execution_bindings()
    bindings_by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for binding in execution_bindings:
        bindings_by_subject[binding["qualification_subject_ref"]].append(binding)
    verticals = load_jsonl(VERTICALS / "vertical-compositions.jsonl")
    vertical_refs: dict[str, list[str]] = defaultdict(list)
    for vertical in verticals:
        for product_ref in vertical["product_refs"]:
            vertical_refs[product_ref].append(vertical["composition_id"])

    ce_context_ids = {row["id"] for row in load_jsonl(CE / "context-families.jsonl")}
    gate_rows = [
        {
            "gate_id": gate_id,
            "record_kind": "qualification_gate_definition",
            "edition": 1,
            "name": name,
            "plane": plane,
            "prerequisite_gate_refs": prereqs,
            "evidence_needed": EVIDENCE_NEEDED.get(gate_id, ["retained exact-scope evidence"]),
            "promotion_law": "Every prerequisite passes for the same immutable scope and all required evidence is valid; absence, waiver, model output or agent assertion is never a pass.",
            "failure_posture": "fail_closed_with_typed_open_or_refusal",
        }
        for gate_id, name, prereqs, plane in GATES
    ]
    edges = [
        {
            "edge_id": f"edge.qp.{source.removeprefix('gate.qp.')}__{target.removeprefix('gate.qp.')}",
            "record_kind": "qualification_gate_dependency",
            "from_gate_ref": source,
            "to_gate_ref": target,
            "relation": "must_pass_before",
        }
        for target, _name, prereqs, _plane in GATES
        for source in prereqs
    ]

    programs: list[dict[str, Any]] = []
    subjects: list[dict[str, Any]] = []
    vacancies: list[dict[str, Any]] = []
    acceptance: list[dict[str, Any]] = []

    for product in readiness:
        candidate_id = product["candidate_id"]
        ident = candidate_id.removeprefix("candidate.product.")
        bundle = product["adjudication_bundle"]
        product_ref = product["local_subject_ref"]
        source = json.loads((ADJUDICATIONS / bundle / "source.json").read_text(encoding="utf-8"))
        libraries = [row for row in source.get("libraries", []) if product_ref_matches(row, product_ref)]
        mappings = [row for row in source.get("binding_maps", source.get("compiler_library_bindings", [])) if product_ref_matches(row, product_ref)]
        mapping_by_library = {row.get("abstract_library_ref", row.get("local_library_ref")): row for row in mappings}
        binding_gaps = [row for row in source.get("binding_gaps", []) if product_ref_matches(row, product_ref)]
        gap_ids = sorted({row["gap_id"] for row in binding_gaps})
        subject_refs: list[str] = []
        for library in sorted(libraries, key=lambda row: row["library_id"]):
            library_id = library["library_id"]
            mapping = mapping_by_library.get(library_id, {})
            subject_id = f"subject.qp.{ident}.{library_id.removeprefix('library.')}"
            subject_refs.append(subject_id)
            contexts = oracle_contexts(library)
            missing_contexts = sorted(set(contexts) - ce_context_ids)
            if missing_contexts:
                raise ValueError(f"{library_id}: unknown conformance contexts {missing_contexts}")
            subjects.append(
                {
                    "subject_id": subject_id,
                    "record_kind": "library_qualification_subject",
                    "edition": 1,
                    "candidate_id": candidate_id,
                    "product_ref": product_ref,
                    "adjudication_bundle": bundle,
                    "abstract_library_ref": library_id,
                    "semantic_owner_ref": library.get("owner_ref"),
                    "library_class": library.get("class"),
                    "effect_boundary": library.get("effect_boundary"),
                    "provided_capability_refs": sorted(library.get("provides", [])),
                    "contract": {
                        "types": library.get("types", []),
                        "operations": library.get("operations", []),
                        "decisions": library.get("decisions", []),
                        "invariants": library.get("invariants", []),
                        "refusals": library.get("refusals", []),
                        "dependencies": library.get("dependencies", []),
                    },
                    "compiler_projection": {
                        "mapping_ref": mapping.get("binding_map_id", mapping.get("binding_id")),
                        "concrete_library_refs": sorted(mapping.get("concrete_library_refs", mapping.get("exact_library_refs", []))),
                        "gap_refs": compiler_gap_refs(mapping),
                        "disposition": mapping.get("compiler_disposition", mapping.get("bindability", mapping.get("status"))),
                    },
                    "required_conformance_context_refs": contexts,
                    "required_evidence_classes": ["law_authority_receipt", "artifact_and_build_identity", "executed_test_receipts", "independence_assessment", "exact_scope_qualification_receipt"],
                    "implementation_state": "EXECUTION_EVIDENCE_PRESENT_UNQUALIFIED" if bindings_by_subject.get(subject_id) else "NO_BOUND_ARTIFACT",
                    "execution_evidence_binding_refs": sorted(row["binding_id"] for row in bindings_by_subject.get(subject_id, [])),
                    "qualified_implementation_refs": [],
                    "portable_offer": False,
                    "source_evidence_refs": sorted(library.get("evidence_refs", [])),
                    "automation_law": "A model or agent may propose tests, counterexamples or diagnostics; deterministic checkers and accountable authorities alone can accept evidence or promote state.",
                }
            )

        structural_vertical_refs = sorted(vertical_refs.get(candidate_id, []))
        current_states: dict[str, str] = {
            "gate.qp.boundary_ddd": "SATISFIED_STRUCTURAL",
            "gate.qp.contract_decomposition": "BLOCKED_MISSING_CONTRACT" if gap_ids else "SATISFIED_STRUCTURAL",
            "gate.qp.two_vertical_structures": "SATISFIED_STRUCTURAL" if len(structural_vertical_refs) >= 2 else ("OPEN_PARTIAL_STRUCTURAL" if structural_vertical_refs else "OPEN_NO_EVIDENCE"),
        }
        for gate_id, _name, _prereqs, _plane in GATES:
            current_states.setdefault(gate_id, "OPEN_NO_EVIDENCE" if gate_id not in {"gate.qp.build_ready", "gate.qp.ratification"} else "WITHHELD_DOWNSTREAM")
        product_bindings = [row for ref in subject_refs for row in bindings_by_subject.get(ref, [])]
        for binding in product_bindings:
            gate_ref = binding["relevant_gate_ref"]
            if gate_ref not in current_states:
                raise ValueError(f"{binding['binding_id']}: unknown qualification gate {gate_ref}")
            if binding["candidate_id"] != candidate_id or binding["product_ref"] != product_ref:
                raise ValueError(f"{binding['binding_id']}: candidate/product scope mismatch")
            if binding["completion_claim"] or binding["qualified_implementation_count"] or binding["portable_offer"] or binding["build_ready"] or binding["ratified"]:
                raise ValueError(f"{binding['binding_id']}: unsupported promotion in execution evidence binding")
            current_states[gate_ref] = binding["gate_effect"]

        programs.append(
            {
                "program_id": f"program.qp.{ident}",
                "record_kind": "product_qualification_program",
                "edition": 1,
                "as_of": AS_OF,
                "candidate_id": candidate_id,
                "product_ref": product_ref,
                "product_name": product["name"],
                "boundary_verdict": product["boundary_verdict"],
                "ddd_dossier_ref": product["product_specific_ddd"]["dossier_ref"],
                "library_subject_refs": subject_refs,
                "compiler_gap_refs": gap_ids,
                "gate_states": [{"gate_ref": gate_id, "state": current_states[gate_id]} for gate_id, *_ in GATES],
                "qualification_scope_identity": [
                    "semantic requirement and law editions", "subject semantic identity", "artifact and source digests",
                    "dependency lock and configuration digests", "build/toolchain/environment digest", "provider offer snapshot",
                    "target occurrence", "population/corpus/generator and seed/schedule/fault plan", "validity interval and authority",
                ],
                "decision_points_without_defaults": [
                    "semantic and oracle authority", "subject implementation and version", "configuration and dependency graph",
                    "target occurrence and finite budgets", "population, exclusions, tolerances and residual risk",
                    "appraiser independence", "evidence maximum age", "promotion, waiver, expiry and revocation",
                    "portability equivalence and allowed loss", "vertical acceptance authority and effect boundary",
                ],
                "current_verdict": "BLOCKED_NO_QUALIFIED_PORTABLE_ACCEPTED_IMPLEMENTATION",
                "automation_extension": {
                    "default": "not_selected",
                    "allowed": ["propose typed test/profile", "generate candidate cases", "suggest counterexample", "summarize retained evidence", "emit non-authoritative diagnostic"],
                    "forbidden": ["invent vocabulary or facts", "approve laws", "waive refusal", "qualify implementation", "authorize effect", "accept vertical outcome", "ratify product"],
                    "removal_law": "Removing every model, LLM and agent leaves the qualification DAG, deterministic suites, evidence identities and promotion rules complete.",
                },
            }
        )

        for gate_id, _name, _prereqs, _plane in GATES:
            if current_states[gate_id] == "SATISFIED_STRUCTURAL":
                continue
            vacancies.append(
                {
                    "vacancy_id": f"vacancy.qp.{ident}.{gate_id.removeprefix('gate.qp.')}",
                    "record_kind": "qualification_evidence_vacancy",
                    "candidate_id": candidate_id,
                    "gate_ref": gate_id,
                    "current_state": current_states[gate_id],
                    "blocking": True,
                    "library_subject_refs": subject_refs if gate_id not in {"gate.qp.two_vertical_structures", "gate.qp.executed_vertical_acceptance", "gate.qp.build_ready", "gate.qp.ratification"} else [],
                    "compiler_gap_refs": gap_ids if gate_id == "gate.qp.contract_decomposition" else [],
                    "evidence_needed": EVIDENCE_NEEDED.get(gate_id, ["retained exact-scope evidence"]),
                    "owner": "UNASSIGNED_ACCOUNTABLE_AUTHORITY",
                    "status": "OPEN",
                }
            )

        slots = [
            {"slot": "unrelated_vertical_a", "composition_ref": structural_vertical_refs[0] if structural_vertical_refs else None, "structural_status": "PRESENT" if structural_vertical_refs else "MISSING", "executed_acceptance_ref": None},
            {"slot": "unrelated_vertical_b", "composition_ref": structural_vertical_refs[1] if len(structural_vertical_refs) > 1 else None, "structural_status": "PRESENT" if len(structural_vertical_refs) > 1 else "MISSING", "executed_acceptance_ref": None},
        ]
        acceptance.append(
            {
                "acceptance_program_id": f"acceptance.program.qp.{ident}",
                "record_kind": "product_vertical_acceptance_program",
                "edition": 1,
                "candidate_id": candidate_id,
                "required_unrelated_vertical_count": 2,
                "vertical_slots": slots,
                "required_gate_classes": ["source_and_cut_fitness", "semantic_and_policy_fitness", "method_and_model_validity", "physical_conformance", "operational_envelope", "authority_safety_and_effect", "outcome_monitoring_and_reconciliation", "change_rollback_and_exit"],
                "same_scope_law": "All gates bind the same immutable product/library editions, physical occurrence, evidence cut, authority and validity interval.",
                "current_verdict": "NOT_EXECUTED",
                "prohibited_shortcuts": ["structural composition as acceptance", "provider qualification as domain acceptance", "model or agent proposal as authority", "metric improvement without harm and population review"],
            }
        )

    metamodel = {
        "metamodel_id": "metamodel.product_qualification_program",
        "edition": 1,
        "as_of": AS_OF,
        "purpose": "Turn each retained product and attributed library into an explicit, fail-closed proof program without claiming an implementation exists.",
        "noncollapse_laws": [
            "specified != implemented != built != executed != appraised != qualified != portable != physically bound != vertically accepted != build-ready != ratified",
            "library qualification does not imply composition qualification",
            "provider documentation does not imply occurrence evidence",
            "one qualified implementation does not imply portability",
            "two component passes do not imply end-to-end acceptance",
            "waived, inconclusive and absent evidence are never pass",
            "model, LLM or agent output is a proposal occurrence, never evidence authority or promotion authority",
        ],
        "reused_authorities": {
            "conformance_context_registry": "research/domain_atlas/compiler/conformance_evaluation/context-families.jsonl",
            "qualification_receipt_schema": "research/domain_atlas/compiler/conformance_evaluation/qualification-receipt-contract.schema.json",
            "composition_laws": "research/domain_atlas/compiler/conformance_evaluation/composition-laws.jsonl",
            "provider_target_registry": "research/domain_atlas/compiler/provider_target_registry/",
            "vertical_acceptance_gate_pattern": "research/product_ontology/composition_pilots/deterministic_verticals/vertical-acceptance-gates.jsonl",
        },
        "evidence_verdicts": ["PASS_EXACT_SCOPE", "FAIL_WITH_COUNTEREXAMPLE", "INCONCLUSIVE", "INVALID", "WAIVED_NOT_PASS", "ABSENT"],
        "open_world": True,
    }

    state_counts = Counter(state["state"] for row in programs for state in row["gate_states"])
    summary = {
        "report_id": "product_qualification_program_summary",
        "as_of": AS_OF,
        "retained_product_count": len(programs),
        "gate_definition_count": len(gate_rows),
        "gate_dependency_count": len(edges),
        "library_qualification_subject_count": len(subjects),
        "evidence_vacancy_count": len(vacancies),
        "vertical_acceptance_program_count": len(acceptance),
        "gate_state_counts": dict(sorted(state_counts.items())),
        "qualified_product_count": 0,
        "portable_product_count": 0,
        "executed_vertical_acceptance_product_count": 0,
        "build_ready_product_count": 0,
        "ratified_product_count": 0,
        "status": "DETERMINISTIC_PROGRAM_GENERATED_EVIDENCE_WITHHELD",
    }

    outputs = {
        "metamodel.json": canonical(metamodel) + "\n",
        "gate-definitions.jsonl": render_jsonl(gate_rows),
        "gate-dependencies.jsonl": render_jsonl(edges),
        "product-qualification-programs.jsonl": render_jsonl(programs),
        "library-qualification-subjects.jsonl": render_jsonl(subjects),
        "evidence-vacancies.jsonl": render_jsonl(vacancies),
        "execution-evidence-bindings.jsonl": render_jsonl(execution_bindings),
        "product-vertical-acceptance-programs.jsonl": render_jsonl(acceptance),
        "summary.json": canonical(summary) + "\n",
    }
    manifest = {
        "manifest_id": "manifest.product_qualification_program",
        "edition": 1,
        "as_of": AS_OF,
        "files": {name: {"sha256": hashlib.sha256(data.encode()).hexdigest(), "bytes": len(data.encode())} for name, data in sorted(outputs.items())},
        "counts": {"products": len(programs), "subjects": len(subjects), "bindings": len(execution_bindings), "vacancies": len(vacancies), "acceptance_programs": len(acceptance), "gates": len(gate_rows), "edges": len(edges)},
    }
    outputs["manifest.json"] = canonical(manifest) + "\n"

    stale: list[str] = []
    for name, data in outputs.items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != data:
                stale.append(name)
        else:
            path.write_text(data, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    print(f"{'CHECK' if args.check else 'BUILD'} PASS: {len(programs)} products, {len(subjects)} library subjects, {len(vacancies)} evidence vacancies, {len(acceptance)} acceptance programs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
