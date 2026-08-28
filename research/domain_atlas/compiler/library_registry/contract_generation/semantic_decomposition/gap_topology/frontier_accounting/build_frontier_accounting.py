#!/usr/bin/env python3
"""Build lossless disposition accounting for every live semantic-gap atom.

This package does not close semantic, implementation, qualification, or acceptance
gaps. It proves that every gap cluster and every constituent atom in the current
gap-topology snapshot has exactly one reversible route to a reusable decision
kernel plus one explicit local residual.
"""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
GAP_ROOT = HERE.parent
SEM = GAP_ROOT.parent
RESEARCH = SEM.parents[4]
REPO_ROOT = RESEARCH.parent
QUALIFICATION = RESEARCH / "product_ontology/qualification_program"

SHARD_COUNT = 32
AS_OF = "2026-08-28"

IDENTITY_FIELDS = (
    "record_id",
    "artifact_id",
    "audit_id",
    "research_id",
    "batch_id",
    "work_package_id",
    "decision_cluster_id",
    "cluster_id",
    "candidate_id",
    "vacancy_id",
    "library_id",
    "library_ref",
    "symbol_ref",
    "family_id",
    "gate_ref",
    "source_id",
    "decision_id",
    "requirement_id",
    "offer_id",
    "binding_map_id",
    "gap_id",
    "dossier_id",
    "relation_id",
    "test_id",
    "contract_id",
    "node_id",
    "edge_id",
    "id",
)

DISPOSITION_TAXONOMY = [
    {
        "disposition_id": "CLOSED_BY_EXISTING_VALID_EVIDENCE",
        "meaning": "The exact atom has an admissible, scope-bound closure receipt already present in the governed corpus.",
        "required_proof": ["closure_receipt_ref", "receipt_scope_digest", "authority_ref", "invalidation_condition"],
        "current_snapshot_allowed_without_receipt": False,
    },
    {
        "disposition_id": "COVERED_BY_REUSABLE_KERNEL",
        "meaning": "A reusable decision protocol covers the atom, while the atom retains an exact residual decision or evidence obligation.",
        "required_proof": ["primary_kernel_ref", "local_residual", "closure_condition"],
        "current_snapshot_allowed_without_receipt": True,
    },
    {
        "disposition_id": "SPLIT_INTO_MULTIPLE_DECISIONS",
        "meaning": "The source quotient contained materially different questions and is split into independently owned exact decisions.",
        "required_proof": ["split_decision_refs", "lossless_source_projection"],
        "current_snapshot_allowed_without_receipt": True,
    },
    {
        "disposition_id": "MERGED_WITH_ANOTHER_QUOTIENT",
        "meaning": "Two or more quotients share the same question, owner, bearer, formalism, authority, refusal and oracle and may share one decision.",
        "required_proof": ["merged_quotient_refs", "identity_of_decision_signature"],
        "current_snapshot_allowed_without_receipt": True,
    },
    {
        "disposition_id": "RECLASSIFIED_OR_WRONGLY_FORMULATED",
        "meaning": "The source item is a real obligation but its prior gap kind, owner, grain or lifecycle was incorrect.",
        "required_proof": ["prior_classification", "replacement_classification", "responsibility_migration"],
        "current_snapshot_allowed_without_receipt": True,
    },
    {
        "disposition_id": "CONTRADICTED_OR_REOPENED",
        "meaning": "Existing evidence or a counterexample invalidates a prior decision or closure claim.",
        "required_proof": ["contradictory_evidence_refs", "reopen_scope", "invalidation_condition"],
        "current_snapshot_allowed_without_receipt": True,
    },
    {
        "disposition_id": "EVIDENCE_VACANCY",
        "meaning": "The semantic or authority question is known, but admissible evidence or a named authority decision is absent.",
        "required_proof": ["evidence_need", "owner_role", "closure_condition"],
        "current_snapshot_allowed_without_receipt": True,
    },
    {
        "disposition_id": "IMPLEMENTATION_ONLY",
        "meaning": "The remaining obligation requires an implementation occurrence and executable receipts, not additional semantic invention.",
        "required_proof": ["exact_contract_subject_ref", "implementation_evidence_need", "closure_condition"],
        "current_snapshot_allowed_without_receipt": True,
    },
    {
        "disposition_id": "QUALIFICATION_ONLY",
        "meaning": "The remaining obligation requires independent conformance, provider, product or vertical-acceptance evidence.",
        "required_proof": ["qualification_scope", "independent_evidence_need", "closure_condition"],
        "current_snapshot_allowed_without_receipt": True,
    },
    {
        "disposition_id": "OUTSIDE_RESEARCH_SCOPE",
        "meaning": "The item is intentionally outside this research corpus, with a named external owner and retained boundary contract.",
        "required_proof": ["external_owner", "boundary_contract_ref", "exit_or_handoff_condition"],
        "current_snapshot_allowed_without_receipt": True,
    },
]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def record_identity(row: dict[str, Any]) -> str:
    for field in IDENTITY_FIELDS:
        value = row.get(field)
        if value not in (None, "") and not isinstance(value, (dict, list)):
            return f"{field}:{value}"
    return f"row-sha256:{sha256_text(canonical(row))}"


def exact_cluster_ref(kind: str, key: str) -> str:
    return f"gap-cluster.{kind}.{key}"


def require_count(label: str, expected: int, values: Iterable[Any]) -> list[Any]:
    result = list(values)
    if len(result) != expected:
        raise ValueError(f"{label}: declared count {expected} != exact constituents {len(result)}")
    return result


QUESTION_BY_GAP_KIND = {
    "source-structure": "Which exact source control is missing or failed, and what executable receipt repairs it?",
    "source-authority": "Which authority may adopt, qualify, split or reject this source family for canonical semantic input?",
    "researched-symbol-owner": "Which context owns this researched public symbol and how must each occurrence import or refine it?",
    "symbol-owner-adjudication-batch": "Which exact owner and occurrence relationship follows for each researched symbol packet?",
    "symbol-research-batch": "What bounded primary research and owner adjudication are required for each unresolved symbol packet?",
    "family-axis-evidence": "What bounded evidence and negative twins govern this family-axis applicability question?",
    "applicability": "For each exact member, does the semantic axis apply, not apply, specialize or remain undecidable?",
    "exact-contract": "What exact public types, operations, invariants, refusals and oracles constitute this library contract?",
    "implementation": "Which concrete implementation occurrence realizes the exact contract and emits reproducible receipts?",
    "qualification": "Does an independent appraisal qualify the implementation for the exact declared scope?",
    "product-gate": "Which exact product or vertical gate receipt is still absent for this candidate?",
}

FORMALISM_BY_GAP_KIND = {
    "source-structure": "schema_validation_and_reproducible_build_receipts",
    "source-authority": "evidence_argumentation_and_authority_adjudication",
    "researched-symbol-owner": "type_identity_context_mapping_and_owner_adjudication",
    "symbol-owner-adjudication-batch": "type_identity_context_mapping_and_owner_adjudication",
    "symbol-research-batch": "open_world_research_and_counterexample_search",
    "family-axis-evidence": "family_axis_evidence_synthesis",
    "applicability": "typed_applicability_lattice_with_explicit_exceptions",
    "exact-contract": "type_theory_algebra_state_machine_and_executable_oracles",
    "implementation": "implementation_identity_build_reproducibility_and_conformance",
    "qualification": "independent_conformance_and_differential_testing",
    "product-gate": "assurance_case_product_and_vertical_acceptance",
}

NEGATIVE_TWINS_BY_GAP_KIND = {
    "source-structure": ["file exists != schema is valid", "validator passes != source authority is established"],
    "source-authority": ["structural readiness != canonical authority", "source evidence != owner ratification"],
    "researched-symbol-owner": ["same spelling != same semantic identity", "shared carrier != shared lifecycle owner"],
    "symbol-owner-adjudication-batch": ["batch adjacency != one owner", "research complete != owner ratified"],
    "symbol-research-batch": ["lexical cluster != semantic proposition", "one source != bounded authority"],
    "family-axis-evidence": ["evidence seed != family default", "family evidence != member applicability"],
    "applicability": ["modal majority != member decision", "applicable family axis != identical local contract"],
    "exact-contract": ["library name != exact contract", "schema shape != behavior and refusal laws"],
    "implementation": ["source code presence != conforming implementation", "one implementation != portability"],
    "qualification": ["self-test != independent qualification", "qualified scope != universal fitness"],
    "product-gate": ["structural pilot != executed acceptance", "product dossier != build-ready product"],
}

OWNER_BY_PROGRAM = {
    "P00": "CORPUS_MAINTAINER",
    "P01": "FAMILY_OWNER",
    "P02": "SEMANTIC_OWNER",
    "P03": "FAMILY_OWNER",
    "P04": "LIBRARY_OWNER",
    "P05": "LIBRARY_OWNER",
    "P06": "IMPLEMENTER",
    "P07": "INDEPENDENT_APPRAISER",
}

CLOSURE_CONDITION_BY_PROGRAM = {
    "P00": "The exact failed source control has a current digest-bound repair and executable validator receipt.",
    "P01": "A named authority records an adopt, qualify, split or reject decision for the exact source-family edition.",
    "P02": "A named semantic owner records the symbol identity and every occurrence disposition with exact migration consequences.",
    "P03": "Bounded primary evidence, authority limits, contradictory evidence and negative twins are recorded for the exact family-axis member.",
    "P04": "The library owner ratifies apply, prohibit, specialize or undecidable for the exact member occurrence.",
    "P05": "The library owner publishes an exact editioned contract with executable laws, refusals and conformance oracles.",
    "P06": "A concrete content-addressed implementation binds the exact contract and emits reproducible build and execution receipts.",
    "P07": "An independent authority issues an exact-scope qualification, product or vertical-acceptance receipt.",
}

RESIDUAL_BY_GAP_KIND = {
    "source-structure": "SOURCE_STRUCTURE_REPAIR_AND_RECEIPT",
    "source-authority": "SOURCE_AUTHORITY_DECISION",
    "researched-symbol-owner": "SYMBOL_OWNER_AND_OCCURRENCE_RATIFICATION",
    "symbol-owner-adjudication-batch": "SYMBOL_OWNER_AND_OCCURRENCE_RATIFICATION",
    "symbol-research-batch": "BOUNDED_PRIMARY_RESEARCH_THEN_OWNER_ADJUDICATION",
    "family-axis-evidence": "FAMILY_AXIS_EVIDENCE_AND_COUNTEREXAMPLES",
    "applicability": "EXACT_MEMBER_APPLICABILITY_DECISION",
    "exact-contract": "OWNER_RATIFIED_EXACT_CONTRACT",
    "implementation": "CONCRETE_IMPLEMENTATION_OCCURRENCE",
    "qualification": "INDEPENDENT_IMPLEMENTATION_QUALIFICATION",
    "product-gate": "PRODUCT_OR_VERTICAL_ACCEPTANCE_RECEIPT",
}


def cluster_disposition(cluster: dict[str, Any]) -> str:
    program = cluster["program_ref"]
    if program == "P06":
        return "IMPLEMENTATION_ONLY"
    if program == "P07":
        return "QUALIFICATION_ONLY"
    if cluster["gap_kind"] in {"source-structure", "source-authority", "symbol-research-batch", "family-axis-evidence"}:
        return "EVIDENCE_VACANCY"
    return "COVERED_BY_REUSABLE_KERNEL"


def atom_status(cluster: dict[str, Any]) -> str:
    if cluster["program_ref"] == "P06":
        return "IMPLEMENTATION_VACANCY"
    if cluster["program_ref"] == "P07":
        return "QUALIFICATION_VACANCY"
    return "EVIDENCE_VACANCY"


def add_atom(
    atoms: list[dict[str, Any]],
    cluster_ref: str,
    source_path: Path,
    source_row: dict[str, Any],
    constituent_kind: str,
    constituent_ref: str,
    *,
    affected_scope_refs: list[str],
    local_context: dict[str, Any] | None = None,
) -> None:
    source_record_ref = record_identity(source_row)
    source_record_sha256 = sha256_text(canonical(source_row))
    source_atom_key = canonical(
        {
            "cluster_ref": cluster_ref,
            "source_path": rel(source_path),
            "source_record_ref": source_record_ref,
            "constituent_kind": constituent_kind,
            "constituent_ref": constituent_ref,
        }
    )
    source_atom_digest = sha256_text(
        canonical(
            {
                "source_atom_key": source_atom_key,
                "source_record_sha256": source_record_sha256,
                "local_context": local_context or {},
            }
        )
    )
    atoms.append(
        {
            "atom_id": f"atom.semantic-gap.{sha256_text(source_atom_key)[:24]}",
            "record_kind": "semantic_gap_atom_disposition",
            "source_cluster_ref": cluster_ref,
            "source_path": rel(source_path),
            "source_record_ref": source_record_ref,
            "source_record_sha256": source_record_sha256,
            "constituent_kind": constituent_kind,
            "constituent_ref": constituent_ref,
            "affected_scope_refs": sorted(set(affected_scope_refs)),
            "source_atom_digest": source_atom_digest,
            "local_context": local_context or {},
            "completion_claim": False,
        }
    )


def exact_atoms() -> list[dict[str, Any]]:
    atoms: list[dict[str, Any]] = []

    authorities_path = SEM / "source_authority_audit/readiness-audits.jsonl"
    for row in load_jsonl(authorities_path):
        family_key = row["family_id"].split(".")[-1]
        missing = row["missing_or_failed_controls"]
        for control in missing:
            control_ref = control if isinstance(control, str) else canonical(control)
            add_atom(
                atoms,
                exact_cluster_ref("source-structure", family_key),
                authorities_path,
                row,
                "missing_or_failed_control",
                control_ref,
                affected_scope_refs=[row["family_id"]],
                local_context={"validator_receipt_ref": row.get("validator_receipt_ref")},
            )
        add_atom(
            atoms,
            exact_cluster_ref("source-authority", family_key),
            authorities_path,
            row,
            "source_authority_decision",
            row["family_id"],
            affected_scope_refs=[row["family_id"]],
            local_context={
                "authority_decision": row.get("authority_decision"),
                "source_file_sha256": row.get("source_file_sha256"),
                "tree_digest": row.get("tree_digest"),
            },
        )

    researched_path = SEM / "p1_authority_symbols/high-fanout-semantic-research.jsonl"
    for row in load_jsonl(researched_path):
        key = row["symbol_ref"].replace(".", "-")
        add_atom(
            atoms,
            exact_cluster_ref("researched-symbol-owner", key),
            researched_path,
            row,
            "researched_symbol_owner_decision",
            row["symbol_ref"],
            affected_scope_refs=[item["library_ref"] for item in row["affected_occurrences"]],
            local_context={
                "research_id": row.get("research_id"),
                "decision": row.get("decision"),
                "symbol_packet_ref": row.get("symbol_packet_ref"),
            },
        )

    remaining_path = SEM / "p1_authority_symbols/remaining-symbol-research-batches.jsonl"
    for row in load_jsonl(remaining_path):
        key = row["batch_id"].removeprefix("batch.p1.remaining-symbols.").removesuffix(".v1")
        primary_research_complete = row.get("research_state") == "BOUNDED_PRIMARY_RESEARCH_COMPLETE"
        kind = "symbol-owner-adjudication-batch" if primary_research_complete else "symbol-research-batch"
        packets = require_count(
            f"{row['batch_id']} packet refs",
            row["packet_count"],
            row["packet_refs"],
        )
        symbol_by_packet = dict(zip(packets, row.get("symbol_refs", []), strict=False))
        for packet_ref in packets:
            add_atom(
                atoms,
                exact_cluster_ref(kind, key),
                remaining_path,
                row,
                "symbol_packet",
                packet_ref,
                affected_scope_refs=[packet_ref],
                local_context={
                    "symbol_ref": symbol_by_packet.get(packet_ref),
                    "research_state": row.get("research_state"),
                    "research_archetype": row.get("research_archetype"),
                },
            )

    targeted_path = SEM / "structured_projection/targeted-evidence-work-packages.jsonl"
    for row in load_jsonl(targeted_path):
        key = f"{row['family_id'].split('.')[-1]}.{row['axis'].replace('_', '-')}"
        library_refs = require_count(
            f"{row['work_package_id']} library refs",
            row["library_count"],
            row["library_refs"],
        )
        for library_ref in library_refs:
            add_atom(
                atoms,
                exact_cluster_ref("family-axis-evidence", key),
                targeted_path,
                row,
                "family_axis_library_occurrence",
                library_ref,
                affected_scope_refs=[library_ref],
                local_context={
                    "family_id": row["family_id"],
                    "axis": row["axis"],
                    "work_package_id": row["work_package_id"],
                },
            )

    decisions_path = SEM / "applicability_matrices/family-axis-decision-clusters.jsonl"
    decision_groups: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for row in load_jsonl(decisions_path):
        decision_groups[(row["family_id"], row["axis"])].append(row)
    for (family, axis), rows in sorted(decision_groups.items()):
        key = f"{family.split('.')[-1]}.{axis.replace('_', '-')}"
        cluster_ref = exact_cluster_ref("applicability", key)
        for row in rows:
            members = require_count(
                f"{record_identity(row)} member refs",
                row["member_count"],
                row["member_preclassification_refs"],
            )
            for member_ref in members:
                add_atom(
                    atoms,
                    cluster_ref,
                    decisions_path,
                    row,
                    "member_applicability_decision",
                    member_ref,
                    affected_scope_refs=[member_ref],
                    local_context={
                        "family_id": family,
                        "axis": axis,
                        "preclassification": row.get("preclassification"),
                        "decision_status": row.get("status"),
                    },
                )

    exact_path = SEM / "structured_projection/exact-contract-input-candidates.jsonl"
    exact_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in load_jsonl(exact_path):
        exact_groups[row["family_id"]].append(row)
    for family, rows in sorted(exact_groups.items()):
        family_key = family.split(".")[-1]
        for row in rows:
            library_ref = row["library_ref"]
            common_context = {
                "family_id": family,
                "candidate_id": row.get("candidate_id"),
                "candidate_status": row.get("status"),
            }
            for kind, constituent_kind in (
                ("exact-contract", "exact_contract_subject"),
                ("implementation", "implementation_subject"),
                ("qualification", "qualification_subject"),
            ):
                add_atom(
                    atoms,
                    exact_cluster_ref(kind, family_key),
                    exact_path,
                    row,
                    constituent_kind,
                    library_ref,
                    affected_scope_refs=[library_ref],
                    local_context=common_context,
                )

    vacancies_path = QUALIFICATION / "evidence-vacancies.jsonl"
    vacancy_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in load_jsonl(vacancies_path):
        vacancy_groups[row["gate_ref"]].append(row)
    for gate_ref, rows in sorted(vacancy_groups.items()):
        gate_key = gate_ref.removeprefix("gate.qp.").replace("_", "-")
        cluster_ref = exact_cluster_ref("product-gate", gate_key)
        for row in rows:
            add_atom(
                atoms,
                cluster_ref,
                vacancies_path,
                row,
                "qualification_evidence_vacancy",
                row["vacancy_id"],
                affected_scope_refs=[row["candidate_id"]],
                local_context={
                    "candidate_id": row["candidate_id"],
                    "gate_ref": gate_ref,
                    "current_state": row.get("current_state"),
                    "evidence_needed": row.get("evidence_needed", []),
                },
            )

    atoms.sort(key=lambda row: row["atom_id"])
    if len({row["atom_id"] for row in atoms}) != len(atoms):
        raise ValueError("duplicate atom_id")
    if len({row["source_atom_digest"] for row in atoms}) != len(atoms):
        raise ValueError("duplicate source_atom_digest")
    return atoms


def build_decision_kernels(
    method_kernels: list[dict[str, Any]],
    clusters_by_id: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    kernels: list[dict[str, Any]] = []
    cluster_to_kernel: dict[str, str] = {}
    for method in sorted(method_kernels, key=lambda row: row["method_kernel_id"]):
        member_refs = method["member_cluster_refs"]
        first_cluster = clusters_by_id[member_refs[0]]
        gap_kind = first_cluster["gap_kind"]
        signature = method["signature"]
        kernel_signature = {
            "question": QUESTION_BY_GAP_KIND[gap_kind],
            "owner_candidate": method["closure_authority"],
            "formalism": FORMALISM_BY_GAP_KIND[gap_kind],
            "bearer_or_decision_locus": signature["locus"],
            "authority_requirement": method["closure_authority"],
            "law_and_refusal_family": {
                "law": "No atom inherits a semantic conclusion, authority, implementation verdict or acceptance merely because it shares this reusable method kernel.",
                "typed_refusal": f"{gap_kind.upper().replace('-', '_')}_RESIDUAL_OPEN",
                "oracle": sorted(signature["required_evidence_kinds"]),
            },
        }
        kernel_id = f"kernel.semantic-decision.{sha256_text(canonical(kernel_signature))[:20]}"
        for cluster_ref in member_refs:
            if cluster_ref in cluster_to_kernel:
                raise ValueError(f"cluster has multiple primary kernels: {cluster_ref}")
            cluster_to_kernel[cluster_ref] = kernel_id
        kernels.append(
            {
                "decision_kernel_id": kernel_id,
                "record_kind": "semantic_decision_kernel",
                "decision_signature": kernel_signature,
                "source_method_kernel_ref": method["method_kernel_id"],
                "question": QUESTION_BY_GAP_KIND[gap_kind],
                "owner_candidate": method["closure_authority"],
                "formalism": FORMALISM_BY_GAP_KIND[gap_kind],
                "bearer_or_decision_locus": signature["locus"],
                "authority_requirement": method["closure_authority"],
                "laws": [
                    "Reusable mechanics do not share semantic conclusions.",
                    "Every exact source atom retains one independently closable residual.",
                    "A missing authority or receipt refuses closure.",
                    "Implementation, qualification and acceptance cannot be inferred from structural coverage.",
                ],
                "typed_refusal": f"{gap_kind.upper().replace('-', '_')}_RESIDUAL_OPEN",
                "conformance_oracles": sorted(signature["required_evidence_kinds"]),
                "negative_twins": NEGATIVE_TWINS_BY_GAP_KIND[gap_kind],
                "member_cluster_refs": sorted(member_refs),
                "represented_atom_count": method["represented_atom_count"],
                "status": "PROPOSED_UNRATIFIED",
                "completion_claim": False,
            }
        )
    kernels.sort(key=lambda row: row["decision_kernel_id"])
    return kernels, cluster_to_kernel


def enrich_atoms(
    atoms: list[dict[str, Any]],
    clusters_by_id: dict[str, dict[str, Any]],
    cluster_to_kernel: dict[str, str],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for atom in atoms:
        cluster = clusters_by_id.get(atom["source_cluster_ref"])
        if cluster is None:
            raise ValueError(f"atom references unknown cluster {atom['source_cluster_ref']}")
        program = cluster["program_ref"]
        disposition = cluster_disposition(cluster)
        residual_kind = RESIDUAL_BY_GAP_KIND[cluster["gap_kind"]]
        local_residual = {
            "residual_kind": residual_kind,
            "subject_ref": atom["constituent_ref"],
            "owner_role": OWNER_BY_PROGRAM[program],
            "required_evidence_kinds": cluster["required_evidence_kinds"],
            "closure_condition": CLOSURE_CONDITION_BY_PROGRAM[program],
        }
        enriched.append(
            {
                **atom,
                "primary_kernel_ref": cluster_to_kernel[atom["source_cluster_ref"]],
                "disposition": disposition,
                "local_residual": local_residual,
                "closure_receipt_refs": [],
                "invalidation_condition": (
                    "Recompute this route when the source record digest, parent cluster edition, "
                    "authority decision, contract edition, implementation occurrence or evidence validity changes."
                ),
                "status": atom_status(cluster),
            }
        )
    enriched.sort(key=lambda row: row["atom_id"])
    return enriched


def build_cluster_dispositions(
    clusters: list[dict[str, Any]],
    atoms: list[dict[str, Any]],
    cluster_to_kernel: dict[str, str],
) -> list[dict[str, Any]]:
    atoms_by_cluster: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for atom in atoms:
        atoms_by_cluster[atom["source_cluster_ref"]].append(atom)

    rows: list[dict[str, Any]] = []
    for cluster in sorted(clusters, key=lambda row: row["cluster_id"]):
        member_atoms = sorted(atoms_by_cluster[cluster["cluster_id"]], key=lambda row: row["atom_id"])
        atom_set_sha256 = sha256_text(
            "".join(f"{row['atom_id']}:{row['source_atom_digest']}\n" for row in member_atoms)
        )
        disposition = cluster_disposition(cluster)
        rows.append(
            {
                "cluster_disposition_id": f"disposition.{cluster['cluster_id']}",
                "record_kind": "semantic_gap_cluster_disposition",
                "source_cluster_ref": cluster["cluster_id"],
                "source_cluster_sha256": sha256_text(canonical(cluster)),
                "source_atom_count": cluster["atom_count"],
                "projected_atom_count": len(member_atoms),
                "atom_set_sha256": atom_set_sha256,
                "primary_kernel_ref": cluster_to_kernel[cluster["cluster_id"]],
                "disposition": disposition,
                "disposition_reason": {
                    "COVERED_BY_REUSABLE_KERNEL": "The decision protocol is reusable, but each exact atom remains open until its local authority/evidence condition is met.",
                    "EVIDENCE_VACANCY": "The question is known and routed, but required semantic evidence or authority is absent.",
                    "IMPLEMENTATION_ONLY": "Semantic routing is explicit; closure now requires a concrete implementation occurrence and executable receipts.",
                    "QUALIFICATION_ONLY": "Closure now requires independent qualification, product acceptance or vertical-acceptance evidence.",
                }[disposition],
                "quotient_group_ref": cluster_to_kernel[cluster["cluster_id"]],
                "merged_quotient_refs": [],
                "split_decision_refs": [],
                "local_residual_kinds": sorted(
                    {row["local_residual"]["residual_kind"] for row in member_atoms}
                ),
                "closure_condition": CLOSURE_CONDITION_BY_PROGRAM[cluster["program_ref"]],
                "closure_receipt_refs": [],
                "invalidation_condition": (
                    "Any change to the source atom set, cluster signature, named owner, evidence edition, "
                    "implementation occurrence or acceptance scope invalidates this disposition."
                ),
                "status": atom_status(cluster),
                "completion_claim": False,
            }
        )
    return rows


def shard_atoms(atoms: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    shards = {f"atom-dispositions-{index:02d}.jsonl": [] for index in range(SHARD_COUNT)}
    for atom in atoms:
        index = int(hashlib.sha256(atom["atom_id"].encode()).hexdigest()[:8], 16) % SHARD_COUNT
        shards[f"atom-dispositions-{index:02d}.jsonl"].append(atom)
    for rows in shards.values():
        rows.sort(key=lambda row: row["atom_id"])
    return shards


def build_model() -> dict[str, Any]:
    clusters = load_jsonl(GAP_ROOT / "gap-clusters.jsonl")
    method_kernels = load_jsonl(GAP_ROOT / "closure-method-kernels.jsonl")
    parent_summary = load_json(GAP_ROOT / "summary.json")
    clusters_by_id = {row["cluster_id"]: row for row in clusters}
    if len(clusters_by_id) != len(clusters):
        raise ValueError("duplicate parent cluster IDs")

    raw_atoms = exact_atoms()
    kernels, cluster_to_kernel = build_decision_kernels(method_kernels, clusters_by_id)

    if set(cluster_to_kernel) != set(clusters_by_id):
        missing = sorted(set(clusters_by_id) - set(cluster_to_kernel))
        extra = sorted(set(cluster_to_kernel) - set(clusters_by_id))
        raise ValueError(f"method-kernel coverage mismatch missing={missing[:5]} extra={extra[:5]}")

    atoms = enrich_atoms(raw_atoms, clusters_by_id, cluster_to_kernel)
    counts = collections.Counter(row["source_cluster_ref"] for row in atoms)
    for cluster in clusters:
        if counts[cluster["cluster_id"]] != cluster["atom_count"]:
            raise ValueError(
                f"{cluster['cluster_id']}: source atom count {counts[cluster['cluster_id']]} "
                f"!= parent atom_count {cluster['atom_count']}"
            )
    if set(counts) != set(clusters_by_id):
        raise ValueError("not every parent cluster has an atom projection")
    if len(atoms) != parent_summary["represented_gap_atoms"]:
        raise ValueError(
            f"atom total {len(atoms)} != parent represented_gap_atoms "
            f"{parent_summary['represented_gap_atoms']}"
        )

    cluster_rows = build_cluster_dispositions(clusters, atoms, cluster_to_kernel)
    taxonomy = [
        {
            **row,
            "record_kind": "gap_disposition_taxonomy",
            "status": "CONSTITUTIONAL_CANDIDATE",
            "completion_claim": False,
        }
        for row in DISPOSITION_TAXONOMY
    ]
    disposition_counts = collections.Counter(row["disposition"] for row in atoms)
    residual_counts = collections.Counter(row["local_residual"]["residual_kind"] for row in atoms)
    status_counts = collections.Counter(row["status"] for row in atoms)
    summary = {
        "program_id": "program.semantic-gap-frontier-accounting.v1",
        "edition": 1,
        "as_of": AS_OF,
        "parent_gap_topology_program_ref": parent_summary["program_id"],
        "parent_gap_topology_sha256": sha256_text(
            (GAP_ROOT / "gap-clusters.jsonl").read_text(encoding="utf-8")
        ),
        "source_gap_clusters": len(clusters),
        "source_gap_atoms": parent_summary["represented_gap_atoms"],
        "projected_gap_clusters": len(cluster_rows),
        "projected_gap_atoms": len(atoms),
        "decision_kernels": len(kernels),
        "atom_shards": SHARD_COUNT,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "residual_counts": dict(sorted(residual_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "closed_by_existing_valid_evidence": disposition_counts["CLOSED_BY_EXISTING_VALID_EVIDENCE"],
        "implemented_atoms": 0,
        "qualified_atoms": 0,
        "accepted_atoms": 0,
        "unmapped_clusters": 0,
        "unmapped_atoms": 0,
        "multiply_mapped_atoms": 0,
        "reversibility": "PASS_BY_EXACT_SOURCE_OCCURRENCE_AND_CONSTITUENT_DIGEST",
        "completion_claim": False,
    }
    validation_report = {
        "report_id": "validation.semantic-gap-frontier-accounting.v1",
        "checks": {
            "jsonl_validity": "BUILDER_GUARANTEED_VALIDATOR_RECHECKS",
            "unique_ids": "BUILDER_GUARANTEED_VALIDATOR_RECHECKS",
            "parent_cluster_coverage": "PASS",
            "atom_count_conservation": "PASS",
            "exact_source_occurrence_projection": "PASS",
            "one_primary_kernel_per_atom": "PASS",
            "local_residual_preservation": "PASS",
            "no_silent_aliases": "PASS",
            "no_invented_implementation": "PASS",
            "no_invented_qualification": "PASS",
            "no_invented_acceptance": "PASS",
            "deterministic_ordering": "BUILDER_GUARANTEED_VALIDATOR_RECHECKS",
        },
        "counts": {
            "source_clusters": len(clusters),
            "source_atoms": parent_summary["represented_gap_atoms"],
            "projected_clusters": len(cluster_rows),
            "projected_atoms": len(atoms),
            "decision_kernels": len(kernels),
        },
        "completion_claim": False,
    }
    return {
        "taxonomy": sorted(taxonomy, key=lambda row: row["disposition_id"]),
        "kernels": kernels,
        "clusters": cluster_rows,
        "atoms": atoms,
        "shards": shard_atoms(atoms),
        "summary": summary,
        "validation_report": validation_report,
    }


def render_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(canonical(row) + "\n" for row in rows)


def write_jsonl(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    text = render_jsonl(rows)
    (HERE / name).write_text(text, encoding="utf-8")
    return {
        "path": name,
        "records": len(rows),
        "bytes": len(text.encode("utf-8")),
        "sha256": sha256_text(text),
    }


def write_json(name: str, value: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    (HERE / name).write_text(text, encoding="utf-8")
    return {
        "path": name,
        "records": 1,
        "bytes": len(text.encode("utf-8")),
        "sha256": sha256_text(text),
    }


def main() -> int:
    model = build_model()
    claims = [
        write_jsonl("disposition-taxonomy.jsonl", model["taxonomy"]),
        write_jsonl("decision-kernels.jsonl", model["kernels"]),
        write_jsonl("cluster-dispositions.jsonl", model["clusters"]),
    ]
    for name, rows in sorted(model["shards"].items()):
        claims.append(write_jsonl(name, rows))
    claims.append(write_json("summary.json", model["summary"]))
    claims.append(write_json("validation-report.json", model["validation_report"]))
    manifest = {
        "manifest_id": "manifest.semantic-gap-frontier-accounting.v1",
        "files": sorted(claims, key=lambda row: row["path"]),
        "summary": model["summary"],
        "completion_claim": False,
    }
    write_json("manifest.json", manifest)
    print(json.dumps(model["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
