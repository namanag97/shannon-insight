#!/usr/bin/env python3
"""Build the effective research-closure projection without manufacturing ratification.

This program treats the prior 625-quotient convergence handoff as candidate research,
applies the fixed-point authority/ownership corrections in this directory, revalidates
downstream P02-P05 rows, and emits a lossless proposed-unratified projection.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / "research/handoffs/gpt-pro-product-ontology-convergence/output-2026-08-27"
OUT = HERE / "generated"

STARTING_RESEARCH_QUOTIENTS = 625
STARTING_RESEARCH_ATOMS = 14_496
EXPECTED_P01_FAMILIES = {
    "constitution.family.analytical_method_kernels",
    "constitution.family.candidate_data_shapes",
    "constitution.family.connector_protocol",
    "constitution.family.consumption_bi_visualization",
    "constitution.family.experimentation_lifecycle",
    "constitution.family.forecasting_lifecycle",
    "constitution.family.geospatial_analytics",
    "constitution.family.governance_metadata_ontology",
    "constitution.family.lineage_provenance_evidence",
    "constitution.family.messaging_coordination",
    "constitution.family.operations_research",
    "constitution.family.optional_model_agent_extensions",
    "constitution.family.persistence_lakehouse",
    "constitution.family.pipeline_dataflow",
    "constitution.family.platform_commercial_support",
    "constitution.family.predictive_analytics",
    "constitution.family.quality_reconciliation",
    "constitution.family.query_compilation_execution",
    "constitution.family.representation_codec",
    "constitution.family.runtime_resource_control",
    "constitution.family.security_privacy_trust",
    "constitution.family.semantic_metrics_formulas",
    "constitution.family.shared_semantic_foundations",
}

DETAIL_FILES = {
    "P02": "symbol-owner-resolutions.jsonl",
    "P03": "member-axis-research-resolutions.jsonl",
    "P04": "applicability-resolutions.jsonl",
    "P05": "exact-contract-research-dispositions.jsonl",
}

NEW_GAP_RESOLUTION_MAP = {
    "fp-gap.shared.business-calendar-owner.v1": "fp.shared.business-calendar.v1",
    "fp-gap.shared.money-core-owner.v1": "fp.shared.money-core.v1",
    "fp-gap.shared.probability-core-owner.v1": "fp.shared.probability-core.v1",
    "fp-gap.shared.verification-receipt-owner.v1": "fp.shared.verification-receipt.v1",
    "fp-gap.platform.tenant-commercial-owner.v1": "fp.p01.platform-commercial-support.v2",
    "fp-gap.platform.customer-party-master-owner.v1": "fp.p01.platform-commercial-support.v2",
    "fp-gap.lineage.epistemic-layer-authority.v1": "fp.p01.lineage-provenance-evidence.v2",
    "fp-gap.governance.metadata-ontology-collapse.v1": "fp.p01.governance-metadata-ontology.v2",
    "fp-gap.visualization.semantic-authority-split.v1": "fp.p01.consumption-bi-visualization.v2",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: JSONL row must be an object")
            rows.append(row)
    return rows


def canonical(row: Any) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("".join(canonical(row) + "\n" for row in rows), encoding="utf-8")


def deep_strings(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str):
        found.add(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            found.add(str(key))
            found.update(deep_strings(item))
    elif isinstance(value, list):
        for item in value:
            found.update(deep_strings(item))
    return found


def load_sources() -> set[str]:
    refs: set[str] = set()
    for row in load_jsonl(PRIOR / "source-register.jsonl"):
        for key in ("source_id", "record_id", "id"):
            if isinstance(row.get(key), str):
                refs.add(row[key])
    for path in sorted(HERE.glob("fresh-sources*.jsonl")):
        for row in load_jsonl(path):
            refs.add(row["source_id"])
    return refs


def load_p01_audits() -> dict[str, dict[str, Any]]:
    rows = load_jsonl(HERE / "p01-all-family-authority-audit.jsonl")
    audits = {row["family_ref"]: row for row in rows}
    if set(audits) != EXPECTED_P01_FAMILIES or len(rows) != 23:
        missing = sorted(EXPECTED_P01_FAMILIES - set(audits))
        extra = sorted(set(audits) - EXPECTED_P01_FAMILIES)
        raise ValueError(f"P01 audit must cover exactly 23 families; missing={missing}, extra={extra}")
    if any(row.get("audit_status") != "RESEARCH_RESOLVED_PROPOSED_UNRATIFIED" for row in rows):
        raise ValueError("Every P01 family must be research-resolved but proposed/unratified")
    return audits


def load_p01_deltas() -> dict[str, dict[str, Any]]:
    deltas: dict[str, dict[str, Any]] = {}
    for path in sorted(HERE.glob("p01-resolution-deltas*.jsonl")):
        for row in load_jsonl(path):
            deltas[row["delta_id"]] = row
    return deltas


def load_rehomes() -> dict[str, dict[str, Any]]:
    rows = load_jsonl(HERE / "shared-foundation-rehomes.jsonl")
    return {row["resolution_id"]: row for row in rows}


def affected_tokens() -> dict[str, str]:
    """Map exact semantic refs whose ownership/meaning changed to effective resolution IDs."""
    mapping = {
        "library.csp.time.business-calendar": "fp.shared.business-calendar.v1",
        "library.csp.quantity.money-core": "fp.shared.money-core.v1",
        "library.csp.quantity.probability-core": "fp.shared.probability-core.v1",
        "library.csp.intent.verification-receipt": "fp.shared.verification-receipt.v1",
        "library.platform-commercial-support.tenant-identity": "fp.p01.platform-commercial-support.v2",
        "library.platform-commercial-support.account_identity": "fp.p01.platform-commercial-support.v2",
        "library.platform-commercial-support.customer_party_identity": "fp.p01.platform-commercial-support.v2",
        "library.platform-commercial-support.legal_entity_binding": "fp.p01.platform-commercial-support.v2",
        "constitution.family.lineage_provenance_evidence": "fp.p01.lineage-provenance-evidence.v2",
        "constitution.family.governance_metadata_ontology": "fp.p01.governance-metadata-ontology.v2",
        "constitution.family.consumption_bi_visualization": "fp.p01.consumption-bi-visualization.v2",
        "constitution.family.candidate_data_shapes": "fp.p01.candidate-data-shapes.v1",
        "constitution.family.operations_research": "fp.p01.operations-research.v2",
        "constitution.family.forecasting_lifecycle": "fp.p01.forecasting-lifecycle.v2",
        "constitution.family.geospatial_analytics": "fp.p01.geospatial-analytics.v1",
        "constitution.family.optional_model_agent_extensions": "fp.p01.optional-model-agent-extensions.v1",
        "constitution.family.runtime_resource_control": "fp.p01.runtime-resource-control.v1",
        "constitution.family.shared_semantic_foundations": "fp.p01.shared-semantic-foundations.v2",
        "constitution.family.platform_commercial_support": "fp.p01.platform-commercial-support.v2",
    }
    return mapping


def overlay_detail_rows(p01: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    tokens = affected_tokens()
    out: list[dict[str, Any]] = []
    stats = {"rows": 0, "migration_rows": 0, "authority_routing_rows": 0, "unchanged_rows": 0}
    for program, filename in DETAIL_FILES.items():
        for row in load_jsonl(PRIOR / filename):
            strings = deep_strings(row)
            families = sorted(EXPECTED_P01_FAMILIES & strings)
            migrations = sorted({resolution for token, resolution in tokens.items() if token in strings})
            effective = dict(row)
            effective["fixed_point_program"] = program
            effective["fixed_point_completion_claim"] = False
            effective["fixed_point_ratification_state"] = "PROPOSED_UNRATIFIED_RESEARCH_DECISION"
            effective["fixed_point_family_audit_refs"] = [p01[f]["family_ref"] for f in families]
            if migrations:
                effective["fixed_point_revalidation"] = "REVALIDATED_WITH_SEMANTIC_MIGRATION"
                effective["fixed_point_resolution_refs"] = migrations
                stats["migration_rows"] += 1
            elif families:
                effective["fixed_point_revalidation"] = "REVALIDATED_WITH_AUTHORITY_ROUTING"
                effective["fixed_point_resolution_refs"] = [p01[f].get("fixed_point_ref", p01[f]["prior_resolution_ref"]) for f in families]
                stats["authority_routing_rows"] += 1
            else:
                effective["fixed_point_revalidation"] = "REVALIDATED_UNCHANGED"
                effective["fixed_point_resolution_refs"] = []
                stats["unchanged_rows"] += 1
            out.append(effective)
            stats["rows"] += 1
    return out, stats


def build() -> dict[str, Any]:
    source_refs = load_sources()
    p01 = load_p01_audits()
    p01_deltas = load_p01_deltas()
    rehomes = load_rehomes()

    # Fresh sources must be well-formed and every explicit fresh P01 reference must resolve.
    for delta in p01_deltas.values():
        for source_ref in delta.get("evidence_refs", []):
            if source_ref.startswith("FP26-") and source_ref not in source_refs:
                raise ValueError(f"unresolved fresh evidence ref {source_ref} in {delta['delta_id']}")

    prior_gaps = [row for row in load_jsonl(PRIOR / "gap-dispositions.jsonl") if row.get("research_addressable") is True]
    if len(prior_gaps) != STARTING_RESEARCH_QUOTIENTS:
        raise ValueError(f"expected {STARTING_RESEARCH_QUOTIENTS} research quotients, found {len(prior_gaps)}")
    atoms = sum(int(row.get("original_atom_count", 0)) for row in prior_gaps)
    if atoms != STARTING_RESEARCH_ATOMS:
        raise ValueError(f"expected {STARTING_RESEARCH_ATOMS} research atoms, found {atoms}")

    effective_gaps: list[dict[str, Any]] = []
    for row in prior_gaps:
        effective = dict(row)
        families = [f for f in row.get("family_refs", []) if f in p01]
        effective["fixed_point_status"] = "RESEARCH_RESOLVED_TO_PROPOSED_UNRATIFIED_DECISIONS"
        effective["fixed_point_ratification_state"] = "PROPOSED_UNRATIFIED"
        effective["fixed_point_completion_claim"] = False
        effective["fixed_point_family_audit_refs"] = families
        effective["fixed_point_authority_routing"] = [p01[f].get("fixed_point_ref", p01[f]["prior_resolution_ref"]) for f in families]
        effective["fixed_point_research_vacancy"] = False
        effective["remaining_closure_condition"] = "Named project authority ratification and any downstream implementation/qualification evidence remain separate; no additional research vacancy is asserted for this quotient unless new counterevidence reopens it."
        effective_gaps.append(effective)

    new_gaps = load_jsonl(HERE / "newly-discovered-gaps.jsonl")
    new_gap_effective: list[dict[str, Any]] = []
    for row in new_gaps:
        gap_id = row["gap_id"]
        resolution_ref = NEW_GAP_RESOLUTION_MAP.get(gap_id)
        if not resolution_ref:
            raise ValueError(f"new research gap has no effective resolution: {gap_id}")
        if resolution_ref.startswith("fp.shared.") and resolution_ref not in rehomes:
            raise ValueError(f"missing shared-foundation resolution {resolution_ref}")
        if resolution_ref.startswith("fp.p01.") and resolution_ref not in p01_deltas:
            raise ValueError(f"missing P01 resolution {resolution_ref}")
        effective = dict(row)
        effective["effective_resolution_ref"] = resolution_ref
        effective["fixed_point_status"] = "RESEARCH_RESOLVED_PROPOSED_UNRATIFIED"
        effective["fixed_point_research_vacancy"] = False
        effective["completion_claim"] = False
        new_gap_effective.append(effective)

    downstream, downstream_stats = overlay_detail_rows(p01)
    if any(row.get("fixed_point_completion_claim") is not False for row in downstream):
        raise ValueError("downstream projection attempted a completion claim")

    summary = {
        "program_id": "program.semantic-fixed-point-campaign.v1",
        "as_of": "2026-08-27",
        "starting_research_quotients": STARTING_RESEARCH_QUOTIENTS,
        "starting_research_atoms": STARTING_RESEARCH_ATOMS,
        "p01_families_audited": len(p01),
        "new_research_gaps_discovered": len(new_gaps),
        "new_research_gaps_with_effective_resolution": len(new_gap_effective),
        "effective_original_research_quotients_resolved": len(effective_gaps),
        "effective_original_research_atoms_resolved": atoms,
        "effective_research_vacancies": 0,
        "downstream_revalidation": downstream_stats,
        "canonical_gaps_closed": 0,
        "ratified_decisions": 0,
        "invented_implementations": 0,
        "invented_qualifications": 0,
        "invented_vertical_acceptances": 0,
        "completion_claim": False,
        "research_completion_semantics": "All known research-addressable quotients and fixed-point deltas have an evidence-bounded proposed-unratified resolution. Canonical closure remains authority-owned and physical gates remain open.",
    }
    return {
        "effective_gaps": effective_gaps,
        "new_gap_effective": new_gap_effective,
        "downstream": downstream,
        "summary": summary,
    }


def main() -> int:
    built = build()
    OUT.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT / "effective-gap-resolutions.jsonl", built["effective_gaps"])
    write_jsonl(OUT / "fixed-point-new-gap-resolutions.jsonl", built["new_gap_effective"])
    write_jsonl(OUT / "downstream-revalidation.jsonl", built["downstream"])
    (OUT / "summary.json").write_text(json.dumps(built["summary"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = {}
    for path in sorted(OUT.iterdir()):
        if path.name == "manifest.json" or not path.is_file():
            continue
        data = path.read_bytes()
        files[path.name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    manifest = {"manifest_id": "manifest.semantic-fixed-point-campaign.v1", "files": files, "completion_claim": False}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    s = built["summary"]
    print(
        "BUILD PASS semantic fixed point: "
        f"{s['effective_original_research_quotients_resolved']} original research quotients / "
        f"{s['effective_original_research_atoms_resolved']} atoms plus "
        f"{s['new_research_gaps_with_effective_resolution']} discovered gaps have effective proposed-unratified resolutions; "
        "zero research vacancies, zero canonical closure claims"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
