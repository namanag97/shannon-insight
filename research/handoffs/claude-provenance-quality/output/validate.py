#!/usr/bin/env python3
"""Deterministic validator for the provenance/quality research lane.

Matches research/handoffs/claude-provenance-quality/CLAUDE-PROMPT.md.
Does not weaken checks to obtain a pass.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent
REPO = Path("/Users/namanagarwal/Projects/shannon-insight")
FAMILIES = ("lineage_provenance_evidence", "quality_reconciliation")
CHANGED = {
    "RETAIN_BUT_NARROW",
    "SPLIT",
    "MERGE",
    "RENAME",
    "REPLACE",
    "RETIRE",
}
VERDICTS = CHANGED | {"RETAIN_AS_IS"}
NEIGHBOR_RELS = {
    "depends_on",
    "supplies_witness_to",
    "consumes_witness_from",
    "adapter_for",
    "effect_port_for",
    "oracle_for",
    "explicit_coexistence",
    "collision",
}
CONTRACT_STATUS = {"EVIDENCE_SUFFICIENT_FOR_DRAFT", "PARTIAL", "BLOCKED"}
MODULE_KINDS = {
    "GLOBAL_PRIMITIVE_CANDIDATE",
    "CROSS_FAMILY_MODULE_CANDIDATE",
    "FAMILY_AXIS_MODULE_CANDIDATE",
    "LOCAL_REFINEMENT_CANDIDATE",
}
MODULE_STATUS = {"CANDIDATE_UNRATIFIED", "BLOCKED"}
APPLY_DECISIONS = {
    "APPLIES_AS_IS",
    "APPLIES_WITH_REFINEMENT",
    "NOT_APPLICABLE",
    "UNRESOLVED",
}
GAP_RELATIONS = {"BLOCKS", "REFINES", "CAUSES", "DUPLICATES", "INVALIDATES"}
ADJ_FIELDS = (
    "library_ref",
    "owned_question",
    "semantic_owner",
    "inside",
    "outside",
    "neighbor_relations",
    "verdict",
    "reasoning",
    "falsification_attempts",
    "source_refs",
    "unresolved_questions",
    "confidence",
    "semantic_module_refs",
    "local_residual_refs",
    "decision_dependencies",
    "ratification_required_by",
)
SRC_FIELDS = (
    "source_id",
    "title",
    "authors_or_issuer",
    "source_class",
    "edition_or_version",
    "publication_date",
    "uri",
    "accessed_on",
    "bounded_claims_supported",
    "claims_not_supported",
    "limitations",
    "confidence",
    "source_authority_scope",
    "normative_status",
    "primary_or_secondary",
    "supersedes_source_refs",
    "contradicts_source_refs",
    "content_digest",
)
MOD_FIELDS = (
    "module_id",
    "module_kind",
    "owned_question",
    "semantic_axis",
    "owner_candidate",
    "terms",
    "non_collapse_laws",
    "carrier_requirements",
    "operations_or_relations",
    "invariants",
    "refusals",
    "applicability_preconditions",
    "counterexamples",
    "source_refs",
    "conflicts",
    "authority_limit",
    "status",
    "decision_points",
    "invalidators",
    "dependent_module_refs",
)
APP_FIELDS = (
    "library_ref",
    "module_ref",
    "decision_candidate",
    "reason",
    "local_refinements",
    "counterexamples_checked",
    "source_refs",
    "owner_decision_required",
    "status",
)
MIG_FIELDS = (
    "old_library_ref",
    "old_responsibility",
    "new_owner_ref",
    "migration_kind",
    "compatibility_alias_allowed",
    "reason",
    "source_refs",
)
CON_FIELDS = (
    "library_ref",
    "contract_status",
    "carrier_types",
    "identity_and_equality_rules",
    "canonicalization_rules",
    "traits_or_ports",
    "operations",
    "success_outcomes",
    "refusals",
    "refusal_precedence",
    "invariants_and_laws",
    "state_transitions",
    "time_concurrency_idempotency",
    "finite_resource_contracts",
    "effect_intents_and_receipts",
    "configuration_decisions",
    "compatibility_and_migration",
    "evidence_invalidators",
    "conformance_oracles",
    "negative_twins",
    "dependencies",
    "semantic_module_refs",
    "local_residuals",
    "source_refs",
    "evidence_vacancies",
)
GAP_NODE_FIELDS = (
    "gap_id",
    "gap_kind",
    "defect_kind",
    "locus",
    "scope_grain",
    "semantic_axes",
    "affected_library_refs",
    "affected_module_refs",
    "required_closure_operation",
    "required_authority_role",
    "required_evidence",
    "blocked_outputs",
    "fanout",
    "status",
)
GAP_EDGE_FIELDS = (
    "edge_id",
    "from_gap_ref",
    "to_gap_ref",
    "relation",
    "reason",
)
MERGE_FIELDS = (
    "candidate_id",
    "target_artifact_kind",
    "target_ref",
    "operation",
    "precondition_input_digest",
    "proposed_payload",
    "source_refs",
    "semantic_module_refs",
    "affected_library_refs",
    "decision_dependencies",
    "risk",
    "confidence",
    "status",
)
MERGE_OPS = {"ADD", "REPLACE", "SPLIT", "MERGE", "RENAME", "RETIRE", "RECORD_VACANCY"}
MERGE_STATUS = {"PROPOSED_UNRATIFIED", "BLOCKED"}
FORBIDDEN_OWNER_TOKENS = (
    "w3c",
    "ietf",
    "iso/",
    "openlineage",
    "in-toto",
    "sigstore",
    "great expectations",
    "dbt",
    "soda",
    "prometheus",
    "vendor",
)
SNAPSHOT_INPUTS = (
    "research/domain_atlas/compiler/library_registry/exact_api_closure/research-batches.jsonl",
    "research/domain_atlas/compiler/library_registry/exact_api_closure/closure-queue.jsonl",
    "research/domain_atlas/compiler/library_registry/exact_api_closure/README.md",
    "research/domain_atlas/compiler/library_registry/library-contributions.jsonl",
    "research/domain_atlas/compiler/library_registry/dependency-edges.jsonl",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/semantic-axis-ontology.json",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/semantic-axis-lanes.jsonl",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/gap-ontology.json",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/closure-programs.jsonl",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/gap-clusters.jsonl",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/structured_projection/structured-axis-evidence.jsonl",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/structured_projection/targeted-evidence-work-packages.jsonl",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/applicability_matrices/family-axis-decision-clusters.jsonl",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/source_authority_audit/readiness-audits.jsonl",
    "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p0_identity_grain/global-symbol-collisions.jsonl",
)
AUTHORITY_TOKENS = (
    "authorize",
    "authorise",
    "issue certificate",
    "issue attestation",
    "issue waiver",
    "place legal hold",
    "acquire forensic",
    "destroy",
    "disposition",
    "release gate",
    "quarantine",
    "certify",
    "waive",
    "adjudicat",
    "legal hold",
    "recall",
)
PRIMARY_CLASSES = {
    "w3c_recommendation",
    "w3c_note",
    "ietf_rfc",
    "iso_standard",
    "iso_landing_page",
    "official_specification",
    "community_standard",
    "original_research",
    "regulatory_guidance",
    "government_standard",
    "government_guidance",
    "ccsds_magenta_book",
    "omg_specification",
    "metrology_guide",
}


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    text = path.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        raise SystemExit(f"{path.name}: missing terminal newline")
    for i, line in enumerate(text.splitlines(), 1):
        if not line:
            raise SystemExit(f"{path.name}:{i}: empty line")
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path.name}:{i}: JSON parse failed: {exc}") from exc
        if not isinstance(rec, dict):
            raise SystemExit(f"{path.name}:{i}: expected object")
        rows.append(rec)
    return rows


def assigned_library_refs() -> list[str]:
    refs: list[str] = []
    path = (
        REPO
        / "research/domain_atlas/compiler/library_registry/exact_api_closure"
        / "research-batches.jsonl"
    )
    for rec in load_jsonl(path):
        if rec.get("research_family") in FAMILIES:
            refs.extend(rec["library_refs"])
    return refs


def require_fields(rec: dict, fields: tuple[str, ...], where: str) -> list[str]:
    missing = [f for f in fields if f not in rec]
    extra = [k for k in rec if k not in fields]
    failures = []
    if missing:
        failures.append(f"{where}: missing fields {missing}")
    if extra:
        failures.append(f"{where}: unexpected fields {extra}")
    return failures


def acyclic(edges: list[tuple[str, str]]) -> bool:
    graph: dict[str, list[str]] = defaultdict(list)
    nodes: set[str] = set()
    for a, b in edges:
        graph[a].append(b)
        nodes.add(a)
        nodes.add(b)
    visiting: set[str] = set()
    seen: set[str] = set()

    def dfs(n: str) -> bool:
        if n in visiting:
            return False
        if n in seen:
            return True
        visiting.add(n)
        for m in graph.get(n, []):
            if not dfs(m):
                return False
        visiting.remove(n)
        seen.add(n)
        return True

    return all(dfs(n) for n in nodes)


def main() -> int:
    failures: list[str] = []
    assigned = assigned_library_refs()
    assigned_set = set(assigned)
    if len(assigned) != len(assigned_set):
        failures.append("input research-batches contain duplicate family refs")

    required_files = (
        "source-register.jsonl",
        "boundary-adjudications.jsonl",
        "semantic-modules.jsonl",
        "library-applicability.jsonl",
        "responsibility-migrations.jsonl",
        "contract-requirements.jsonl",
        "conflicts-and-vacancies.jsonl",
        "gap-dependency-graph.jsonl",
        "merge-candidates.jsonl",
        "coverage-report.json",
        "README.md",
    )
    for name in required_files:
        if not (OUT / name).exists():
            failures.append(f"missing required artifact {name}")

    sources = load_jsonl(OUT / "source-register.jsonl") if (OUT / "source-register.jsonl").exists() else []
    adjs = load_jsonl(OUT / "boundary-adjudications.jsonl") if (OUT / "boundary-adjudications.jsonl").exists() else []
    mods = load_jsonl(OUT / "semantic-modules.jsonl") if (OUT / "semantic-modules.jsonl").exists() else []
    apps = load_jsonl(OUT / "library-applicability.jsonl") if (OUT / "library-applicability.jsonl").exists() else []
    migs = load_jsonl(OUT / "responsibility-migrations.jsonl") if (OUT / "responsibility-migrations.jsonl").exists() else []
    cons = load_jsonl(OUT / "contract-requirements.jsonl") if (OUT / "contract-requirements.jsonl").exists() else []
    vacs = load_jsonl(OUT / "conflicts-and-vacancies.jsonl") if (OUT / "conflicts-and-vacancies.jsonl").exists() else []
    gaps = load_jsonl(OUT / "gap-dependency-graph.jsonl") if (OUT / "gap-dependency-graph.jsonl").exists() else []

    source_ids = [r.get("source_id") for r in sources]
    if len(source_ids) != len(set(source_ids)):
        failures.append("source-register.jsonl: duplicate source_id")
    if source_ids != sorted(str(x) for x in source_ids):
        failures.append("source-register.jsonl: source_id order is not deterministic sorted")
    source_set = set(source_ids)
    for i, rec in enumerate(sources, 1):
        failures.extend(require_fields(rec, SRC_FIELDS, f"source-register.jsonl:{i}"))

    adj_refs = [r.get("library_ref") for r in adjs]
    if Counter(adj_refs) != Counter(assigned):
        missing = sorted(assigned_set - set(adj_refs))
        extra = sorted(set(adj_refs) - assigned_set)
        dups = sorted(r for r, n in Counter(adj_refs).items() if n != 1)
        if missing:
            failures.append(f"boundary-adjudications missing assigned refs: {missing}")
        if extra:
            failures.append(f"boundary-adjudications silently added unrelated refs: {extra}")
        if dups:
            failures.append(f"boundary-adjudications duplicate refs: {dups}")
    if adj_refs != sorted(str(x) for x in adj_refs):
        failures.append("boundary-adjudications.jsonl: library_ref order is not sorted")

    changed_refs: set[str] = set()
    for i, rec in enumerate(adjs, 1):
        where = f"boundary-adjudications.jsonl:{i}:{rec.get('library_ref')}"
        failures.extend(require_fields(rec, ADJ_FIELDS, where))
        if rec.get("verdict") not in VERDICTS:
            failures.append(f"{where}: illegal verdict {rec.get('verdict')}")
        if rec.get("verdict") in CHANGED:
            changed_refs.add(rec["library_ref"])
        if not rec.get("owned_question"):
            failures.append(f"{where}: empty owned_question")
        if not isinstance(rec.get("inside"), list) or not rec["inside"]:
            failures.append(f"{where}: inside must be a non-empty list")
        if not isinstance(rec.get("outside"), list) or not rec["outside"]:
            failures.append(f"{where}: outside must be a non-empty list")
        if not rec.get("falsification_attempts"):
            failures.append(f"{where}: falsification_attempts required")
        for rel in rec.get("neighbor_relations") or []:
            if rel.get("relation") not in NEIGHBOR_RELS:
                failures.append(f"{where}: illegal neighbor relation {rel}")
        srcs = rec.get("source_refs") or []
        unresolved = rec.get("unresolved_questions") or []
        nontrivial = rec.get("verdict") in CHANGED or rec.get("confidence") != "low"
        if nontrivial and not srcs and not unresolved:
            failures.append(
                f"{where}: nontrivial decision lacks primary evidence and explicit vacancy"
            )
        for sid in srcs:
            if sid not in source_set:
                failures.append(f"{where}: unresolved source_ref {sid}")

    mod_ids = [r.get("module_id") for r in mods]
    if mod_ids != sorted(str(x) for x in mod_ids):
        failures.append("semantic-modules.jsonl: module_id order is not sorted")
    if len(mod_ids) != len(set(mod_ids)):
        failures.append("semantic-modules.jsonl: duplicate module_id")
    module_set = set(mod_ids)
    for i, rec in enumerate(mods, 1):
        where = f"semantic-modules.jsonl:{i}:{rec.get('module_id')}"
        failures.extend(require_fields(rec, MOD_FIELDS, where))
        if rec.get("module_kind") not in MODULE_KINDS:
            failures.append(f"{where}: illegal module_kind")
        if rec.get("status") not in MODULE_STATUS:
            failures.append(f"{where}: status must remain CANDIDATE_UNRATIFIED or BLOCKED")
        if not rec.get("counterexamples"):
            failures.append(f"{where}: counterexamples required")
        if not rec.get("authority_limit"):
            failures.append(f"{where}: authority_limit required")
        if not rec.get("source_refs") and rec.get("status") != "BLOCKED":
            failures.append(f"{where}: module lacks sources and is not BLOCKED")
        for sid in rec.get("source_refs") or []:
            if sid not in source_set:
                failures.append(f"{where}: unresolved source_ref {sid}")

    app_keys = [(r.get("library_ref"), r.get("module_ref")) for r in apps]
    if app_keys != sorted(app_keys, key=lambda x: (str(x[0]), str(x[1]))):
        failures.append("library-applicability.jsonl: order is not deterministic")
    if len(app_keys) != len(set(app_keys)):
        failures.append("library-applicability.jsonl: duplicate library×module rows")
    covered_by_app = {k[0] for k in app_keys}
    if assigned_set - covered_by_app:
        failures.append(
            "libraries missing applicability coverage: "
            + str(sorted(assigned_set - covered_by_app))
        )
    libs_with_apply = defaultdict(list)
    for i, rec in enumerate(apps, 1):
        where = f"library-applicability.jsonl:{i}"
        failures.extend(require_fields(rec, APP_FIELDS, where))
        if rec.get("library_ref") not in assigned_set:
            failures.append(f"{where}: unrelated library_ref {rec.get('library_ref')}")
        if rec.get("module_ref") not in module_set:
            failures.append(f"{where}: unknown module_ref {rec.get('module_ref')}")
        if rec.get("decision_candidate") not in APPLY_DECISIONS:
            failures.append(f"{where}: illegal decision_candidate")
        if rec.get("owner_decision_required") is not True:
            failures.append(f"{where}: owner_decision_required must remain true")
        if rec.get("decision_candidate") == "APPLIES_WITH_REFINEMENT" and not rec.get(
            "local_refinements"
        ):
            failures.append(f"{where}: refinement decision lacks local_refinements")
        for sid in rec.get("source_refs") or []:
            if sid not in source_set:
                failures.append(f"{where}: unresolved source_ref {sid}")
        libs_with_apply[rec.get("library_ref")].append(rec)

    mig_keys = [(m.get("old_library_ref"), m.get("old_responsibility")) for m in migs]
    if mig_keys != sorted(mig_keys, key=lambda x: (str(x[0]), str(x[1]))):
        failures.append("responsibility-migrations.jsonl: order is not deterministic")
    if len(mig_keys) != len(set(mig_keys)):
        failures.append("responsibility-migrations.jsonl: duplicate old responsibility rows")
    migrated_olds = {m.get("old_library_ref") for m in migs}
    if changed_refs - migrated_olds:
        failures.append(
            "changed boundaries missing responsibility migration: "
            + str(sorted(changed_refs - migrated_olds))
        )
    adj_by_ref = {r["library_ref"]: r for r in adjs if "library_ref" in r}
    for i, rec in enumerate(migs, 1):
        where = f"responsibility-migrations.jsonl:{i}"
        failures.extend(require_fields(rec, MIG_FIELDS, where))
        if rec.get("compatibility_alias_allowed") is not False:
            failures.append(f"{where}: compatibility_alias_allowed must be false")
        if rec.get("old_library_ref") not in assigned_set:
            failures.append(f"{where}: old_library_ref not assigned")
        for sid in rec.get("source_refs") or []:
            if sid not in source_set:
                failures.append(f"{where}: unresolved source_ref {sid}")
        adj = adj_by_ref.get(rec.get("old_library_ref"))
        if adj and adj.get("verdict") == "SPLIT":
            if rec.get("old_responsibility") not in adj.get("inside", []):
                failures.append(
                    f"{where}: SPLIT migration responsibility not listed in old inside"
                )
        if adj and adj.get("verdict") == "RETAIN_BUT_NARROW":
            if rec.get("old_responsibility") in adj.get("inside", []):
                failures.append(
                    f"{where}: RETAIN_BUT_NARROW migrated a responsibility still marked inside"
                )

    split_or_rename_or_replace = {
        r["library_ref"]
        for r in adjs
        if r.get("verdict") in {"SPLIT", "RENAME", "REPLACE", "RETIRE"}
    }
    retained = [
        r["library_ref"]
        for r in adjs
        if r.get("verdict") in {"RETAIN_AS_IS", "RETAIN_BUT_NARROW"}
    ]
    con_refs = [c.get("library_ref") for c in cons]
    if con_refs != sorted(str(x) for x in con_refs):
        failures.append("contract-requirements.jsonl: library_ref order is not sorted")
    if len(con_refs) != len(set(con_refs)):
        failures.append("contract-requirements.jsonl: duplicate library_ref")
    proposed_from_mig = {
        m["new_owner_ref"]
        for m in migs
        if m.get("new_owner_ref")
        and (
            m["new_owner_ref"] not in assigned_set
            or adj_by_ref.get(m.get("old_library_ref"), {}).get("verdict")
            in {"SPLIT", "RENAME", "REPLACE"}
        )
    }
    for i, rec in enumerate(cons, 1):
        where = f"contract-requirements.jsonl:{i}:{rec.get('library_ref')}"
        failures.extend(require_fields(rec, CON_FIELDS, where))
        if rec.get("contract_status") not in CONTRACT_STATUS:
            failures.append(f"{where}: illegal contract_status")
        for sid in rec.get("source_refs") or []:
            if sid not in source_set:
                failures.append(f"{where}: unresolved source_ref {sid}")
        for mid in rec.get("semantic_module_refs") or []:
            if mid not in module_set:
                failures.append(f"{where}: unknown semantic_module_ref {mid}")
        if rec.get("contract_status") == "EVIDENCE_SUFFICIENT_FOR_DRAFT" and not rec.get(
            "source_refs"
        ):
            failures.append(f"{where}: draft contract without sources")
        if rec.get("contract_status") == "BLOCKED" and not rec.get("evidence_vacancies"):
            failures.append(f"{where}: BLOCKED contract without evidence_vacancies")
        ops = " ".join(rec.get("operations") or []).lower()
        effects = rec.get("effect_intents_and_receipts") or []
        pure_claimed = any("pure" in str(t).lower() for t in rec.get("traits_or_ports") or [])
        if pure_claimed:
            io_tokens = ("network fetch", "filesystem write", "ambient clock", "http call")
            if any(tok in ops for tok in io_tokens) and not effects:
                failures.append(f"{where}: pure contract performs I/O without effect port")
        if any(tok in ops for tok in AUTHORITY_TOKENS):
            cfg = " ".join(rec.get("configuration_decisions") or []).lower()
            deps = " ".join(rec.get("dependencies") or []).lower()
            blob = cfg + " " + deps + " " + " ".join(rec.get("refusals") or []).lower()
            if "authority" not in blob and "rfc" not in blob and "iso" not in blob:
                failures.append(
                    f"{where}: authority-bearing action does not name an external authority source"
                )
        if rec.get("library_ref") in split_or_rename_or_replace:
            failures.append(
                f"{where}: retired/renamed/split old ref must not keep a retained contract"
            )
    for ref in retained:
        if ref not in con_refs:
            failures.append(f"retained boundary missing contract: {ref}")
    for ref in proposed_from_mig:
        if str(ref).startswith(("library.lpe.", "library.qor.")) and ref not in con_refs:
            if ref not in assigned_set or adj_by_ref.get(ref, {}).get("verdict") in CHANGED - {
                "RETAIN_BUT_NARROW"
            }:
                if ref not in retained and ref not in con_refs:
                    failures.append(f"proposed boundary missing contract: {ref}")

    for i, rec in enumerate(vacs, 1):
        where = f"conflicts-and-vacancies.jsonl:{i}"
        needed = {
            "vacancy_id",
            "kind",
            "affected_library_refs",
            "statement",
            "required_evidence",
            "source_refs",
        }
        missing = sorted(needed - set(rec))
        extra = sorted(set(rec) - needed)
        if missing:
            failures.append(f"{where}: missing {missing}")
        if extra:
            failures.append(f"{where}: unexpected {extra}")
        for sid in rec.get("source_refs") or []:
            if sid not in source_set:
                failures.append(f"{where}: unresolved source_ref {sid}")
    vac_ids = [v.get("vacancy_id") for v in vacs]
    if vac_ids != sorted(str(x) for x in vac_ids):
        failures.append("conflicts-and-vacancies.jsonl: vacancy_id order is not sorted")

    nodes = [g for g in gaps if "gap_id" in g]
    edges = [g for g in gaps if "edge_id" in g]
    if any("gap_id" in g and "edge_id" in g for g in gaps):
        failures.append("gap-dependency-graph.jsonl: record mixes node and edge fields")
    node_ids = [n.get("gap_id") for n in nodes]
    edge_ids = [e.get("edge_id") for e in edges]
    if node_ids != sorted(str(x) for x in node_ids):
        failures.append("gap nodes are not sorted by gap_id")
    if edge_ids != sorted(str(x) for x in edge_ids):
        failures.append("gap edges are not sorted by edge_id")
    if len(node_ids) != len(set(node_ids)):
        failures.append("duplicate gap_id")
    node_set = set(node_ids)
    for i, rec in enumerate(nodes, 1):
        failures.extend(require_fields(rec, GAP_NODE_FIELDS, f"gap-node:{rec.get('gap_id')}"))
        if rec.get("status") in {"CLOSED", "DECIDED", "RATIFIED"}:
            failures.append(f"gap {rec.get('gap_id')}: must not mark canonical gap closed")
    for rec in edges:
        failures.extend(require_fields(rec, GAP_EDGE_FIELDS, f"gap-edge:{rec.get('edge_id')}"))
        if rec.get("relation") not in GAP_RELATIONS:
            failures.append(f"gap-edge {rec.get('edge_id')}: illegal relation")
        if rec.get("from_gap_ref") not in node_set or rec.get("to_gap_ref") not in node_set:
            failures.append(f"gap-edge {rec.get('edge_id')}: unresolved gap ref")
    cycle_edges = [
        (e["from_gap_ref"], e["to_gap_ref"])
        for e in edges
        if e.get("relation") != "DUPLICATES"
    ]
    if not acyclic(cycle_edges):
        failures.append("gap dependencies contain a cycle after ignoring DUPLICATES")

    # Homonym guard: same exact public symbol name must not be silently unified.
    symbol_owners: dict[str, set[str]] = defaultdict(set)
    for rec in cons:
        for carrier in rec.get("carrier_types") or []:
            name = carrier.split(":")[0].split("/")[0].strip()
            if name:
                symbol_owners[name].add(rec["library_ref"])
    for name, owners in symbol_owners.items():
        if len(owners) > 1 and name in {
            "Evidence",
            "Receipt",
            "Attestation",
            "Measurement",
            "Validation",
            "Lineage",
            "Impact",
            "Certificate",
        }:
            # Allowed only if a collision/homonym vacancy or module exists.
            has_note = any(
                name.lower() in json.dumps(v).lower() for v in vacs
            ) or any(
                name.lower() in json.dumps(m.get("terms", [])).lower()
                and m.get("module_kind") in {
                    "GLOBAL_PRIMITIVE_CANDIDATE",
                    "CROSS_FAMILY_MODULE_CANDIDATE",
                }
                for m in mods
            )
            if not has_note:
                failures.append(
                    f"public symbol {name} appears under {sorted(owners)} without homonym adjudication"
                )

    cov_path = OUT / "coverage-report.json"
    if cov_path.exists():
        cov = json.loads(cov_path.read_text(encoding="utf-8"))
        if cov.get("completion_claim") is not False:
            failures.append("coverage-report.json: completion_claim must be false")
        if cov.get("input_library_count") != len(assigned_set):
            failures.append("coverage-report.json: input_library_count mismatch")
        if set(cov.get("covered_library_refs") or []) != assigned_set:
            failures.append("coverage-report.json: covered_library_refs mismatch")
        for key in (
            "module_count",
            "applicability_row_count",
            "root_gap_count",
            "represented_downstream_gap_count",
            "reuse_ratio",
            "singleton_residual_count",
            "unresolved_public_symbol_collisions",
        ):
            if key not in cov:
                failures.append(f"coverage-report.json: missing {key}")
        if cov.get("module_count") != len(mods):
            failures.append("coverage-report.json: module_count mismatch")
        if cov.get("applicability_row_count") != len(apps):
            failures.append("coverage-report.json: applicability_row_count mismatch")
        snap = cov.get("input_snapshot")
        if not isinstance(snap, dict) or "files" not in snap or "aggregate_digest" not in snap:
            failures.append("coverage-report.json: missing input_snapshot")
        else:
            live = []
            for rel in SNAPSHOT_INPUTS:
                p = REPO / rel
                data = p.read_bytes() if p.exists() else b""
                digest = hashlib.sha256(data).hexdigest()
                nrec = None
                if rel.endswith(".jsonl") and p.exists():
                    nrec = sum(1 for line in data.splitlines() if line.strip())
                live.append({"path": rel, "sha256": digest, "bytes": len(data), "record_count": nrec})
            live_by_path = {x["path"]: x for x in live}
            reported = snap.get("files") or []
            reported_by_path = {x.get("path"): x for x in reported}
            if set(live_by_path) != set(reported_by_path):
                failures.append("coverage-report.json: input_snapshot path set mismatch")
            for path, expected in live_by_path.items():
                got = reported_by_path.get(path) or {}
                if got.get("sha256") != expected["sha256"]:
                    failures.append(f"coverage-report.json: digest mismatch for {path}")
                if got.get("record_count") != expected["record_count"]:
                    failures.append(f"coverage-report.json: record_count mismatch for {path}")
            concat = "".join(x["sha256"] for x in live)
            if snap.get("aggregate_digest") != hashlib.sha256(concat.encode("utf-8")).hexdigest():
                failures.append("coverage-report.json: aggregate_digest mismatch")
        for key in ("research_cutoff", "generated_at", "researched_proposition_count", "projection_count"):
            if key not in cov:
                failures.append(f"coverage-report.json: missing {key}")

    merge_path = OUT / "merge-candidates.jsonl"
    merges = load_jsonl(merge_path) if merge_path.exists() else []
    merge_ids = [m.get("candidate_id") for m in merges]
    if merge_ids != sorted(str(x) for x in merge_ids):
        failures.append("merge-candidates.jsonl: candidate_id order is not sorted")
    if len(merge_ids) != len(set(merge_ids)):
        failures.append("merge-candidates.jsonl: duplicate candidate_id")
    snap_digest = None
    cov_path = OUT / "coverage-report.json"
    if cov_path.exists():
        try:
            snap_digest = json.loads(cov_path.read_text(encoding="utf-8")).get("input_snapshot", {}).get(
                "aggregate_digest"
            )
        except json.JSONDecodeError:
            snap_digest = None
    for i, rec in enumerate(merges, 1):
        where = f"merge-candidates.jsonl:{i}:{rec.get('candidate_id')}"
        failures.extend(require_fields(rec, MERGE_FIELDS, where))
        if rec.get("operation") not in MERGE_OPS:
            failures.append(f"{where}: illegal operation")
        if rec.get("status") not in MERGE_STATUS:
            failures.append(f"{where}: status must be PROPOSED_UNRATIFIED or BLOCKED")
        if not rec.get("precondition_input_digest"):
            failures.append(f"{where}: missing precondition_input_digest")
        elif snap_digest and rec.get("precondition_input_digest") != snap_digest:
            failures.append(f"{where}: precondition_input_digest does not match live snapshot")
        for sid in rec.get("source_refs") or []:
            if sid not in source_set:
                failures.append(f"{where}: unresolved source_ref {sid}")
        for mid in rec.get("semantic_module_refs") or []:
            if mid not in module_set:
                failures.append(f"{where}: unknown semantic_module_ref {mid}")
        owner_blob = json.dumps(rec.get("proposed_payload") or {}).lower()
        if any(tok in owner_blob for tok in FORBIDDEN_OWNER_TOKENS) and "semantic_owner" in owner_blob:
            if any(
                f"semantic_owner\": \"{tok}" in owner_blob or f"owner_candidate\": \"{tok}" in owner_blob
                for tok in FORBIDDEN_OWNER_TOKENS
            ):
                failures.append(f"{where}: vendor/standard presented as SAN semantic owner")
        payload = rec.get("proposed_payload") or {}
        if not isinstance(payload, dict) or len(payload.keys()) > 8:
            failures.append(f"{where}: proposed_payload is not an atomic change")

    for rec in adjs + mods:
        owner = str(rec.get("semantic_owner") or rec.get("owner_candidate") or "").lower()
        if any(tok in owner for tok in FORBIDDEN_OWNER_TOKENS):
            failures.append(
                f"{rec.get('library_ref') or rec.get('module_id')}: vendor/standard presented as SAN semantic owner"
            )

    if failures:
        print("VALIDATOR FAILED")
        for item in failures:
            print(f"- {item}")
        return 1
    print("VALIDATOR PASSED")
    print(
        f"assigned={len(assigned_set)} adjudications={len(adjs)} "
        f"modules={len(mods)} applicability={len(apps)} sources={len(sources)}"
    )
    print("completion_claim=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
