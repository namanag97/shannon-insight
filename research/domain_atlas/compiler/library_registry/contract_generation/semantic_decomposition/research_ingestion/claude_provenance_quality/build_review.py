#!/usr/bin/env python3
"""Build a non-ratifying integration review of the Claude provenance/quality lane."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parents[1]
REGISTRY = SEM.parents[1]
ROOT = REGISTRY.parents[2]
HANDOFF = ROOT / "handoffs/claude-provenance-quality/output"
LPE_UNIVERSE = ROOT / "domain_atlas/universes/lineage_provenance_evidence/library-boundaries.jsonl"
QOR_UNIVERSE = ROOT / "domain_atlas/universes/quality_observability_reconciliation/library-boundary-candidates.jsonl"
LIBRARIES = REGISTRY / "library-contributions.jsonl"
CONTEXTS = REGISTRY / "library-design-contexts.jsonl"
CLOSURES = REGISTRY / "exact_api_closure/closure-queue.jsonl"
AS_OF = "2026-08-26"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


AXIS_TARGETS = {
    "semantic_object": ["module.semantic-axis.semantic-object.v1"],
    "identity_and_equality": ["module.semantic-axis.identity-equality.v1"],
    "grain_and_cardinality": ["module.semantic-axis.grain-cardinality.v1"],
    "state_and_change": ["module.semantic-axis.state-change.v1"],
    "time": ["module.semantic-axis.time.v1"],
    "order_and_topology": ["module.semantic-axis.order-topology.v1"],
    "partiality_and_uncertainty": ["module.semantic-axis.partiality-uncertainty.v1"],
    "authority_and_trust": ["module.semantic-axis.authority-trust.v1"],
    "effect_boundary": ["module.semantic-axis.effect-boundary.v1"],
    "privacy_security_safety": ["module.semantic-axis.privacy-security-safety.v1"],
    "semantic_role": ["module.semantic-axis.semantic-role.v1"],
    "composition_algebra": ["module.semantic-axis.composition-algebra.v1"],
    "representation": ["module.semantic-axis.representation.v1"],
    "compatibility_and_evolution": ["module.semantic-axis.compatibility-evolution.v1"],
    "evidence_and_conformance": ["module.semantic-axis.evidence-conformance.v1"],
}

GLOBAL_TARGETS = {
    "module.global.authority-external-source": ["module.semantic-axis.authority-trust.v1"],
    "module.global.data-vs-metadata": ["module.semantic-axis.semantic-object.v1", "module.semantic-axis.representation.v1"],
    "module.global.effect-vs-pure": ["module.semantic-axis.effect-boundary.v1", "module.semantic-axis.semantic-role.v1"],
    "module.global.event-assertion-evidence-proof-truth": ["module.semantic-axis.semantic-object.v1", "module.semantic-axis.evidence-conformance.v1"],
    "module.global.integrity-authenticity-correctness": ["module.semantic-axis.evidence-conformance.v1", "module.semantic-axis.authority-trust.v1"],
    "module.global.missing-negative-incomplete-evidence": ["module.semantic-axis.partiality-uncertainty.v1", "module.semantic-axis.evidence-conformance.v1"],
    "module.global.retraction-deletion-supersession": ["module.semantic-axis.state-change.v1", "module.semantic-axis.authority-trust.v1"],
}

CROSS_TARGETS = {
    "module.cross.attestation-vs-quality-certificate": ["module.semantic-axis.semantic-object.v1", "module.semantic-axis.evidence-conformance.v1"],
    "module.cross.derivation-vs-causation": ["module.semantic-axis.order-topology.v1"],
    "module.cross.design-vs-runtime-lineage": ["module.semantic-axis.time.v1", "module.semantic-axis.semantic-role.v1"],
    "module.cross.impact-graph-vs-quality-invalidation": ["module.semantic-axis.composition-algebra.v1", "module.semantic-axis.evidence-conformance.v1"],
    "module.cross.match-candidate-vs-identity-resolution": ["module.semantic-axis.identity-equality.v1", "module.semantic-axis.authority-trust.v1"],
    "module.cross.observation-vs-inference": ["module.semantic-axis.semantic-role.v1", "module.semantic-axis.evidence-conformance.v1"],
    "module.cross.receipt-vs-quality-evidence": ["module.semantic-axis.semantic-object.v1", "module.semantic-axis.evidence-conformance.v1"],
}

MERGE_REVIEWS = {
    "merge.rename.lpe.openlineage-adapter": ("REJECT_AND_RETAIN_PROVIDER_ADAPTER_BOUNDARY", "A provider-named ACL is a valid replaceable adapter seam. Renaming it to a generic runtime-lineage adapter would hide the OpenLineage-specific mapping and loss profile.", ["Retain or narrow the OpenLineage adapter as a provider adapter.", "If a provider-neutral runtime-lineage port is needed, model it separately and let this adapter implement it."]),
    "merge.rename.qor.certificate": ("ADMIT_TO_NEW_BOUNDARY_ADJUDICATION", "DQV supports separating a quality certificate annotation from attestation evidence, but the proposed replacement library and owner contract do not yet exist in the canonical registry.", ["Create an owner-authored quality-certificate boundary candidate.", "Migrate only after exact responsibility, context, API and no-alias cutover are ratified."]),
    "merge.replace.qor.observability": ("REQUIRE_TELEMETRY_OWNER_AND_PORT_ADJUDICATION", "Instrumentation is an adapter/evidence-emitter role, but the proposed replacement is not a current library and must import rather than own the telemetry data model.", ["Identify the provider-neutral telemetry emission port owner.", "Keep signal correlation and quality meaning outside the emit adapter."]),
    "merge.split.lpe.lineage-core": ("REWRITE_FROM_COMPLETE_LPE_INVENTORY", "The proposal assumes missing statement and bundle cores that already exist outside the assigned exact-API batches. The logical-lineage responsibility may still need narrowing, but not this stale split.", ["Re-evaluate lineage-core alongside the six omitted LPE universe libraries.", "Reuse existing prov-statement-algebra, provenance-assertion and provenance-bundle boundaries."]),
    "merge.split.lpe.record-lifecycle": ("ADMIT_TO_BOUNDARY_ADJUDICATION", "Amendment, retraction, recall and deletion have different subjects, authorities and effects; proposed replacement records remain unmaterialized.", ["Create four owner-context boundary candidates with exact authority and lifecycle contracts.", "Define coexistence and precedence with retention, legal hold and historical provenance."]),
    "merge.split.lpe.retention-policy": ("ADMIT_TO_AUTHORITY_BOUNDARY_ADJUDICATION", "Technical retention scheduling and externally authorized legal hold are non-collapsible, but neither replacement boundary is present and one SEC rule cannot establish global policy semantics.", ["Research jurisdiction-neutral retention schedule semantics and authority profiles.", "Create separate legal-hold authority and conflict-precedence contracts."]),
    "merge.split.qor.completeness-timeliness": ("BLOCKED_PENDING_CHARACTERISTIC_AUTHORITY", "The handoff correctly records that landing-page evidence is insufficient to settle completeness, freshness and timeliness terminology.", ["Obtain and review the authoritative characteristic definitions.", "Preserve the blocked status and do not generate replacement APIs."]),
    "merge.split.qor.dimension-metric": ("CONFIRMS_EXISTING_SPLIT_PROPOSAL", "The canonical source record already marks this split as researched but unadjudicated; DQV supports distinct dimension, metric and measurement roles.", ["Route to the existing QOR boundary adjudication rather than create a duplicate proposal.", "Materialize replacements only after owner and exact-contract decisions."]),
    "merge.split.qor.duplicate-entity": ("ADMIT_TO_IDENTITY_MDM_BOUNDARY_ADJUDICATION", "Match candidates and confidence are not approved co-reference or merge authority, but DQV alone does not establish identity-resolution semantics.", ["Bind the proposal to the identity/MDM owner and evidence corpus.", "Separate candidate generation, adjudicated decision and merge effect."]),
    "merge.split.qor.evidence-receipt": ("ADMIT_TO_CROSS_FAMILY_BOUNDARY_ADJUDICATION", "Quality evaluation evidence and transparency or inclusion receipts have different owners and equality/lifecycle laws; the new QOR evidence-record boundary is not yet materialized.", ["Define the QOR evidence-record boundary and its relation to LPE receipt storage.", "Keep receipt occurrence, stored receipt, evidence body and appraisal result distinct."]),
    "merge.vacancy.disclosure-core": ("REJECT_FALSE_VACANCY_USE_EXISTING_LIBRARY", "library.lpe.disclosure-core already exists in the LPE universe and central registry; it was merely outside the assigned exact-API batches.", ["Route disclosure research to the existing library gap.", "Do not add a duplicate closure vacancy."]),
    "merge.vacancy.missing-lpe-cores": ("REJECT_FALSE_VACANCY_USE_EXISTING_LIBRARIES", "prov-statement-algebra, provenance-assertion and provenance-bundle already exist in the LPE universe and central registry.", ["Add or prioritize exact-API closure for the existing libraries if needed.", "Do not treat batch omission as ontology absence."]),
}


def canonical_library_id(value: str) -> str:
    """Translate source-universe aliases at the ingestion border only."""
    if value.startswith("qor.library."):
        return "library.qor." + value.removeprefix("qor.library.")
    return value


def library_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {canonical_library_id(row["library_id"]) for row in rows}


def proposed_refs(payload: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for key, value in payload.items():
        if key.endswith("_ref") and isinstance(value, str):
            refs.append(value)
        elif key in {"new_refs", "missing_universe_libs"} and isinstance(value, list):
            refs.extend(item for item in value if isinstance(item, str))
    return sorted(set(refs))


def module_reviews(modules: list[dict[str, Any]], context_ids: set[str]) -> list[dict[str, Any]]:
    rows = []
    for module in modules:
        kind = module["module_kind"]
        if kind == "GLOBAL_PRIMITIVE_CANDIDATE":
            disposition = "REFINE_EXISTING_CONSTITUTION_CANDIDATE"
            targets = GLOBAL_TARGETS[module["module_id"]]
            owner_action = "Constitution owners decide whether the bounded laws refine existing modules; do not create a second global primitive."
        elif kind == "CROSS_FAMILY_MODULE_CANDIDATE":
            disposition = "REHOME_AS_JOINT_CROSS_FAMILY_REFINEMENT_CANDIDATE"
            targets = CROSS_TARGETS[module["module_id"]]
            owner_action = "Affected LPE, QOR and constitutional owners jointly adjudicate the seam; one family cannot own the cross-family distinction."
        elif kind == "LOCAL_REFINEMENT_CANDIDATE":
            disposition = "ROUTE_TO_BOUNDARY_ADJUDICATION_ONLY"
            targets = []
            owner_action = "Evaluate through its atomic boundary merge candidate; do not publish a local split/rename as a reusable semantic module."
        else:
            targets = AXIS_TARGETS.get(module["semantic_axis"], [])
            if module["status"] == "BLOCKED":
                disposition = "BLOCKED_FAMILY_REFINEMENT_EVIDENCE_REQUIRED"
            else:
                disposition = "RETAIN_AS_FAMILY_REFINEMENT_CANDIDATE"
            owner_action = "The named family owner adjudicates applicability, exact vocabulary and exceptions under the referenced constitutional module."
        rows.append({
            "record_kind": "external_research_module_integration_review",
            "review_id": f"review.claude-provenance-quality.{module['module_id']}",
            "module_ref": module["module_id"],
            "source_module_kind": kind,
            "source_status": module["status"],
            "source_semantic_axis": module["semantic_axis"],
            "source_owner_candidate": module["owner_candidate"],
            "source_owner_resolves": module["owner_candidate"] in context_ids,
            "integration_disposition": disposition,
            "constitutional_module_refs": targets,
            "semantic_axis_hint": module["semantic_axis"],
            "owner_action_required": owner_action,
            "source_refs": module["source_refs"],
            "authority_limit": "This review routes a bounded research proposition. It does not ratify the proposition, owner, public name, applicability, boundary change or exact contract.",
            "status": "INTEGRATION_CANDIDATE_UNRATIFIED" if "BLOCKED" not in disposition else "BLOCKED",
        })
    return rows


def merge_reviews(candidates: list[dict[str, Any]], libraries: list[dict[str, Any]], closures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    library_by_id = {row["library_id"]: row for row in libraries}
    closure_ids = {row["closure_id"] for row in closures}
    rows = []
    for candidate in candidates:
        disposition, reason, actions = MERGE_REVIEWS[candidate["candidate_id"]]
        refs = proposed_refs(candidate["proposed_payload"])
        target = candidate["target_ref"]
        target_record = library_by_id.get(target)
        target_exists = target in library_by_id or target in closure_ids
        rows.append({
            "record_kind": "external_research_merge_candidate_integration_review",
            "review_id": f"review.claude-provenance-quality.{candidate['candidate_id']}",
            "candidate_ref": candidate["candidate_id"],
            "operation": candidate["operation"],
            "target_ref": target,
            "target_exists": target_exists,
            "target_record_digest": digest_bytes(canonical(target_record).encode()) if target_record else None,
            "source_precondition_aggregate_digest": candidate["precondition_input_digest"],
            "precondition_assessment": "LIVE_AGGREGATE_SNAPSHOT_BUT_REBIND_TO_TARGET_RECORD_BEFORE_APPLY",
            "proposed_refs": refs,
            "existing_proposed_refs": [ref for ref in refs if ref in library_by_id or ref in closure_ids],
            "unmaterialized_proposed_refs": [ref for ref in refs if ref not in library_by_id and ref not in closure_ids],
            "integration_disposition": disposition,
            "reason": reason,
            "required_actions": actions,
            "source_refs": candidate["source_refs"],
            "semantic_module_refs": candidate["semantic_module_refs"],
            "source_status": candidate["status"],
            "authority_limit": "No canonical mutation is authorized. Any accepted boundary change requires a fresh target digest, owner adjudication, complete migrations and deterministic global validation.",
            "status": "BLOCKED" if disposition.startswith("BLOCKED") else "PROPOSED_UNRATIFIED",
        })
    return rows


def outputs() -> dict[str, str]:
    modules = load_jsonl(HANDOFF / "semantic-modules.jsonl")
    candidates = load_jsonl(HANDOFF / "merge-candidates.jsonl")
    adjudications = load_jsonl(HANDOFF / "boundary-adjudications.jsonl")
    lpe = load_jsonl(LPE_UNIVERSE); qor = load_jsonl(QOR_UNIVERSE)
    libraries = load_jsonl(LIBRARIES); contexts = load_jsonl(CONTEXTS); closures = load_jsonl(CLOSURES)
    assigned = {row["library_ref"] for row in adjudications}
    source_universe = library_ids(lpe) | library_ids(qor)
    omitted = sorted(source_universe - assigned)
    module_rows = module_reviews(modules, {row["context_id"] for row in contexts})
    merge_rows = merge_reviews(candidates, libraries, closures)
    false_vacancies = [row["candidate_ref"] for row in merge_rows if row["integration_disposition"].startswith("REJECT_FALSE_VACANCY")]
    unmaterialized = sorted({ref for row in merge_rows for ref in row["unmaterialized_proposed_refs"]})
    gaps = [
        {"record_kind": "external_research_integration_gap", "gap_id": "gap.integration.claude-provenance-quality.incomplete-family-scope", "gap_kind": "coverage_scope", "finding": "The handoff validated 68 exact-API-assigned libraries, while the two source universes contain 74 libraries.", "affected_refs": omitted, "required_action": "Research and integrate the six existing LPE libraries before any full-family conclusion or vacancy claim.", "status": "OPEN"},
        {"record_kind": "external_research_integration_gap", "gap_id": "gap.integration.claude-provenance-quality.false-vacancies", "gap_kind": "inventory_conflict", "finding": "Two merge candidates call existing LPE libraries missing because they were outside the assigned exact-API batches.", "affected_refs": false_vacancies, "required_action": "Reject duplicate vacancies and route work to the existing library records.", "status": "OPEN"},
        {"record_kind": "external_research_integration_gap", "gap_id": "gap.integration.claude-provenance-quality.unmaterialized-boundaries", "gap_kind": "boundary_materialization", "finding": "Several proposed replacements have no current owner-authored library record.", "affected_refs": unmaterialized, "required_action": "Create and adjudicate complete boundary records before migrations or exact contracts.", "status": "OPEN"},
        {"record_kind": "external_research_integration_gap", "gap_id": "gap.integration.claude-provenance-quality.aggregate-preconditions", "gap_kind": "merge_safety", "finding": "Every merge candidate uses the same live aggregate input digest rather than an exact target-record digest.", "affected_refs": [row["candidate_ref"] for row in merge_rows], "required_action": "Rebind an accepted candidate to the current target record digest and current canonical snapshot before application.", "status": "OPEN"},
        {"record_kind": "external_research_integration_gap", "gap_id": "gap.integration.claude-provenance-quality.cross-family-ownership", "gap_kind": "semantic_owner", "finding": "Cross-family modules name one source owner even when the proposition constrains LPE and QOR meanings jointly.", "affected_refs": [row["module_ref"] for row in module_rows if row["source_module_kind"] == "CROSS_FAMILY_MODULE_CANDIDATE"], "required_action": "Rehome under joint affected-family and constitutional adjudication; no single-family ratification.", "status": "OPEN"},
    ]
    snapshot_paths = [HANDOFF / name for name in ["source-register.jsonl", "semantic-modules.jsonl", "library-applicability.jsonl", "boundary-adjudications.jsonl", "responsibility-migrations.jsonl", "merge-candidates.jsonl", "coverage-report.json"]] + [LPE_UNIVERSE, QOR_UNIVERSE, LIBRARIES, CONTEXTS, CLOSURES]
    snapshot = [{"path": str(path.relative_to(ROOT)), "sha256": digest_bytes(path.read_bytes()), "bytes": path.stat().st_size, "record_count": len(load_jsonl(path)) if path.suffix == ".jsonl" else 1} for path in snapshot_paths]
    summary = {
        "program_id": "review.external-research.claude-provenance-quality.v1", "edition": 1, "as_of": AS_OF, "completion_claim": False,
        "handoff_validator_passed": True, "source_universe_library_count": len(source_universe), "handoff_assigned_library_count": len(assigned),
        "omitted_existing_library_count": len(omitted), "omitted_existing_library_refs": omitted,
        "module_review_count": len(module_rows), "merge_candidate_review_count": len(merge_rows), "integration_gap_count": len(gaps),
        "false_vacancy_candidate_count": len(false_vacancies), "unmaterialized_proposed_ref_count": len(unmaterialized),
        "canonical_mutations_authorized": 0, "ratified_modules": 0, "ratified_boundaries": 0,
        "finding": "The handoff supplies useful bounded research, but its full-family frame is incomplete and two vacancy proposals conflict with existing canonical inventory. Modules must refine constitutions or family profiles; boundary changes require separate owner adjudication.",
    }
    files = {
        "module-integration-review.jsonl": "".join(canonical(row) + "\n" for row in sorted(module_rows, key=lambda row: row["module_ref"])),
        "merge-candidate-integration-review.jsonl": "".join(canonical(row) + "\n" for row in sorted(merge_rows, key=lambda row: row["candidate_ref"])),
        "integration-gaps.jsonl": "".join(canonical(row) + "\n" for row in gaps),
        "input-snapshot.json": json.dumps({"snapshot_id": "snapshot.claude-provenance-quality.integration.v1", "as_of": AS_OF, "inputs": snapshot}, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"sha256": digest_bytes(text.encode()), "bytes": len(text.encode())} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.claude-provenance-quality.integration.v1", "completion_claim": False, "files": manifest}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text() != text: stale.append(name)
        else:
            path.write_text(text)
    if stale:
        print("STALE " + ", ".join(stale)); return 1
    summary = json.loads(outputs()["summary.json"])
    print(f"{'CHECK' if args.check else 'BUILD'} PASS Claude integration review: {summary['module_review_count']} modules, {summary['merge_candidate_review_count']} merge candidates, {summary['omitted_existing_library_count']} omitted existing libraries, {summary['false_vacancy_candidate_count']} false vacancies; zero ratification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
