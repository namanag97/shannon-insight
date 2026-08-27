#!/usr/bin/env python3
"""Build the deterministic presentation-experience boundary audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from source_model import (
    ARTIFACTS,
    AS_OF,
    AXES,
    HERE,
    LIBRARY_CANDIDATES,
    NON_COLLAPSE_LAWS,
    PRODUCT_HYPOTHESES,
    RESULT_KINDS,
    ROOT,
    SOURCES,
    SPECIALIZED_COMPATIBILITY,
)
from split_model import (
    LIBRARY_ALLOCATIONS,
    MIGRATION_STEPS,
    SPLIT_ADJUDICATIONS,
    SPLIT_DDD_DOSSIERS,
    SPLIT_SOURCES,
)
from frontier_model import FRONTIER_CROSSWALK, FRONTIER_LAWS, FRONTIER_SOURCES


INPUTS = {
    "retained_products": ROOT / "research/product_ontology/dossier_readiness/product-readiness.jsonl",
    "bi_bindings": ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/bi_visualization_metrics_semantic_slice/library-semantic-bindings.jsonl",
    "bi_findings": ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/bi_visualization_metrics_semantic_slice/product-capability-boundary-findings.jsonl",
    "bi_summary": ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/bi_visualization_metrics_semantic_slice/summary.json",
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(canonical(row) + "\n" for row in rows)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def evidence_refs(*idents: str) -> list[str]:
    return [f"evidence.presentation.{ident}" for ident in idents]


ARTIFACT_EVIDENCE = {
    "visual_grammar": evidence_refs("vegalite", "vegalite_spec", "observable_marks"),
    "interactive_exploration": evidence_refs("vegalite_selection", "tableau_sheets", "observable_marks"),
    "formal_reporting": evidence_refs("powerbi_paginated", "powerbi_paginated_docs", "grafana_reporting"),
    "operational_dashboard": evidence_refs("grafana_dashboard", "grafana_alert"),
    "narrative": evidence_refs("tableau_story", "tableau_sheets", "nbformat"),
    "regulatory_reporting": evidence_refs("xbrl", "powerbi_paginated_docs", "pdfua"),
    "publication": evidence_refs("grafana_share", "grafana_reporting", "prov"),
    "computational_document": evidence_refs("nbformat", "jupyter_mime", "prov"),
    "analytical_grid": evidence_refs("odf", "openformula", "tableau_sheets"),
    "specialized_view": evidence_refs("ogc_maps", "ogc_tiles", "ogc_styles", "cytoscape", "vtk"),
    "embedding": evidence_refs("powerbi_embed", "powerbi_embed_rls", "tableau_device"),
    "alerting": evidence_refs("grafana_alert", "grafana_share", "cloudevents"),
    "accessibility": evidence_refs("wcag22", "graphics_aria", "observable_accessibility", "pdfua"),
    "collaboration": evidence_refs("tableau_story", "prov"),
    "interaction": evidence_refs("vegalite_selection", "tableau_sheets"),
}


HYPOTHESIS_EVIDENCE = {
    "interactive_exploration": evidence_refs("vegalite", "vegalite_selection", "observable_marks", "tableau_sheets"),
    "formal_reporting": evidence_refs("powerbi_paginated", "powerbi_paginated_docs", "grafana_reporting", "xbrl"),
    "operational_dashboard": evidence_refs("grafana_dashboard", "grafana_alert", "grafana_share"),
    "analytical_application": evidence_refs("vegalite_selection", "powerbi_embed", "tableau_sheets"),
    "computational_document": evidence_refs("nbformat", "jupyter_mime", "prov"),
    "analytical_grid": evidence_refs("odf", "openformula", "tableau_sheets"),
    "embedding": evidence_refs("powerbi_embed", "powerbi_embed_rls", "tableau_device"),
    "specialized_view": evidence_refs("ogc_maps", "ogc_tiles", "ogc_styles", "cytoscape", "vtk"),
    "narrative": evidence_refs("tableau_story", "tableau_sheets", "nbformat"),
    "alerting": evidence_refs("grafana_alert", "grafana_share", "grafana_reporting", "cloudevents"),
    "external_publication": evidence_refs("grafana_share", "powerbi_embed", "xbrl", "pdfua"),
    "accessibility": evidence_refs("wcag22", "graphics_aria", "observable_accessibility", "tableau_accessibility", "pdfua"),
}


def input_snapshot() -> dict[str, Any]:
    files = []
    for role, path in INPUTS.items():
        data = path.read_bytes()
        files.append({
            "role": role,
            "path": str(path.relative_to(ROOT)),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return {
        "record_kind": "presentation_audit_input_snapshot",
        "as_of": AS_OF,
        "files": files,
        "completion_claim": False,
    }


def build() -> dict[str, list[dict[str, Any]] | dict[str, Any]]:
    all_sources = SOURCES + SPLIT_SOURCES + FRONTIER_SOURCES
    retained_rows = load_jsonl(INPUTS["retained_products"])
    retained_products = {row["local_subject_ref"] for row in retained_rows}
    bi_bindings = load_jsonl(INPUTS["bi_bindings"])
    existing_libraries = {row["library_ref"]: row for row in bi_bindings}

    axes = [
        {
            "axis_id": f"axis.presentation.{ident}",
            "record_kind": "presentation_semantic_axis",
            "name": ident,
            "adjudication_question": question,
            "required_outcome": "EXPLICIT_APPLICABILITY_AND_CONTRACT_OR_TYPED_REFUSAL",
            "status": "RESEARCH_AXIS_NOT_AUTHORITY",
            "completion_claim": False,
        }
        for ident, question in AXES
    ]
    artifacts = [
        {
            "artifact_id": f"artifact.presentation.{ident}",
            "record_kind": "presentation_artifact_kind",
            "name": ident,
            "family": family,
            "grain": grain,
            "lifecycle_candidate": lifecycle,
            "evidence_refs": ARTIFACT_EVIDENCE[family],
            "authority_law": "The artifact carries bounded claims and interactions; it does not acquire metric, source, decision, approval or effect authority.",
            "status": "PROPOSED_UNRATIFIED",
            "completion_claim": False,
        }
        for ident, family, grain, lifecycle in ARTIFACTS
    ]
    results = [
        {
            "result_kind_id": f"result-kind.presentation.{ident}",
            "record_kind": "analytical_result_kind_for_presentation",
            "name": ident,
            "semantic_tags": sorted(tags),
            "preservation_law": "Identity, grain, type, unit, time, uncertainty, missingness, provenance and authority survive every presentation target.",
            "status": "PROPOSED_UNRATIFIED",
            "completion_claim": False,
        }
        for ident, tags in RESULT_KINDS
    ]
    product_hypotheses = []
    for ident, name, disposition, neighbors, question in PRODUCT_HYPOTHESES:
        product_hypotheses.append({
            "hypothesis_id": f"hypothesis.presentation.{ident}",
            "record_kind": "presentation_product_boundary_hypothesis",
            "name": name,
            "sovereign_question": question,
            "preliminary_disposition": disposition,
            "nearest_retained_product_refs": neighbors,
            "evidence_refs": HYPOTHESIS_EVIDENCE[ident],
            "resolved_retained_product_refs": sorted(set(neighbors) & retained_products),
            "unresolved_retained_product_refs": sorted(set(neighbors) - retained_products),
            "split_test_axes": ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"],
            "promotion_gates": ["independent_lifecycle", "independent_adoption", "independent_support_and_exit", "two_independent_implementations", "two_unrelated_vertical_acceptances", "negative_twin_survives"],
            "ratification": "WITHHELD",
            "completion_claim": False,
        })

    libraries = []
    for ident, existing_ref, purpose in LIBRARY_CANDIDATES:
        exact_ref = None if existing_ref == "new" else existing_ref
        existing = existing_libraries.get(exact_ref) if exact_ref else None
        libraries.append({
            "library_hypothesis_id": f"library-hypothesis.presentation.{ident}",
            "record_kind": "presentation_library_boundary_hypothesis",
            "name": ident,
            "purpose": purpose,
            "evidence_refs": sorted({
                ref
                for hypothesis in product_hypotheses
                for ref in hypothesis["evidence_refs"]
                if (
                    ident.split("_")[0] in hypothesis["hypothesis_id"]
                    or ident in {"presentation_intent", "analytical_result_binding", "presentation_ir", "renderer_adapter", "semantic_equivalence_oracle", "presentation_resource_budget"}
                )
            }) or evidence_refs("vegalite", "wcag22", "prov"),
            "exact_existing_library_ref": exact_ref if existing else None,
            "unresolved_claimed_existing_ref": exact_ref if exact_ref and not existing else None,
            "current_route": existing["downstream_contract_route"] if existing else "NO_EXACT_CURRENT_LIBRARY",
            "compiler_binding": existing["compiler_binding"] if existing else "REFUSED_MISSING_EXACT_CONTRACT",
            "required_contract_surface": ["types", "value_objects", "operations", "state_machine", "invariants", "refusals", "events", "time", "resources", "laws", "oracles", "ports", "compatibility", "evidence"],
            "status": "EXISTING_UNRATIFIED" if existing else "CANDIDATE_VACANCY",
            "completion_claim": False,
        })

    laws = [
        {
            "law_id": f"law.presentation.{ident}",
            "record_kind": "presentation_noncollapse_law",
            "left": left,
            "right": right,
            "law": f"{left} != {right}",
            "falsification_test": f"Construct two cases with the same {left} but different {right}, and two with the same {right} but different {left}; a valid model must preserve both distinctions.",
            "status": "PROPOSED_UNRATIFIED",
            "completion_claim": False,
        }
        for ident, left, right in NON_COLLAPSE_LAWS
    ]

    axis_obligations = []
    for artifact in artifacts:
        for axis in axes:
            axis_obligations.append({
                "obligation_id": f"obligation.presentation.{slug(artifact['name'])}.{slug(axis['name'])}",
                "record_kind": "presentation_artifact_axis_obligation",
                "artifact_ref": artifact["artifact_id"],
                "axis_ref": axis["axis_id"],
                "applicability": "REQUIRED",
                "decision": "UNRATIFIED",
                "exact_contract_ref": None,
                "refusal": "OWNER_AND_EXACT_CONTRACT_MISSING",
                "completion_claim": False,
            })

    compatibility = []
    for artifact in artifacts:
        artifact_name = artifact["name"]
        required_tags = SPECIALIZED_COMPATIBILITY.get(artifact_name)
        for result in results:
            tags = set(result["semantic_tags"])
            if required_tags is None:
                disposition = "REQUIRED_TEST"
                reason = "General presentation artifact requires an explicit binding profile for this result kind."
            elif tags & required_tags:
                disposition = "NATIVE_CANDIDATE"
                reason = f"Result tags intersect specialized requirements {sorted(required_tags)}; semantic fitness remains unratified."
            else:
                disposition = "INAPPLICABLE_UNLESS_TRANSFORMED"
                reason = f"Specialized view requires one of {sorted(required_tags)}; any transformation must produce a separately identified result."
            compatibility.append({
                "cell_id": f"cell.presentation.{slug(artifact_name)}.{slug(result['name'])}",
                "record_kind": "presentation_result_compatibility_cell",
                "artifact_ref": artifact["artifact_id"],
                "result_kind_ref": result["result_kind_id"],
                "disposition": disposition,
                "reason": reason,
                "profile_ref": None,
                "status": "UNRATIFIED",
                "completion_claim": False,
            })

    gaps = []
    for library in libraries:
        if library["status"] == "CANDIDATE_VACANCY":
            gaps.append({
                "gap_id": f"gap.presentation.library.{slug(library['name'])}",
                "record_kind": "presentation_research_gap",
                "gap_class": "EXACT_LIBRARY_BOUNDARY_AND_CONTRACT",
                "subject_ref": library["library_hypothesis_id"],
                "evidence_needed": ["owner_adjudication", "exact_semantic_contract", "two_implementations", "conformance_oracles"],
                "blocking_for_promotion_or_compilation": True,
                "status": "OPEN",
                "completion_claim": False,
            })
    for hypothesis in product_hypotheses:
        gaps.append({
            "gap_id": f"gap.presentation.product.{slug(hypothesis['hypothesis_id'].split('.')[-1])}",
            "record_kind": "presentation_research_gap",
            "gap_class": "PRODUCT_BOUNDARY_ADJUDICATION",
            "subject_ref": hypothesis["hypothesis_id"],
            "evidence_needed": hypothesis["promotion_gates"],
            "blocking_for_promotion_or_compilation": True,
            "status": "OPEN",
            "completion_claim": False,
        })
    gaps.append({
        "gap_id": "gap.presentation.compatibility-profiles",
        "record_kind": "presentation_research_gap",
        "gap_class": "RESULT_ARTIFACT_COMPATIBILITY_PROFILES",
        "subject_ref": "tensor.presentation.result-artifact",
        "evidence_needed": ["encoding_fitness_rules", "uncertainty_and_missingness_profiles", "accessibility_equivalence", "resource_budgets", "vertical_acceptance"],
        "blocking_for_promotion_or_compilation": True,
        "status": "OPEN",
        "completion_claim": False,
    })

    summary = {
        "program_id": "program.presentation-experience-gap-audit.v1",
        "record_kind": "presentation_experience_gap_audit_summary",
        "as_of": AS_OF,
        "primary_or_official_sources": len(all_sources),
        "semantic_axes": len(axes),
        "artifact_kinds": len(artifacts),
        "analytical_result_kinds": len(results),
        "artifact_axis_obligations": len(axis_obligations),
        "result_artifact_compatibility_cells": len(compatibility),
        "product_boundary_hypotheses": len(product_hypotheses),
        "library_boundary_hypotheses": len(libraries),
        "existing_library_routes": sum(row["exact_existing_library_ref"] is not None for row in libraries),
        "candidate_library_vacancies": sum(row["status"] == "CANDIDATE_VACANCY" for row in libraries),
        "noncollapse_laws": len(laws),
        "boundary_split_adjudications": 1,
        "strong_candidate_products": 2,
        "candidate_complete_ddd_dossiers": len(SPLIT_DDD_DOSSIERS),
        "split_library_allocations": len(LIBRARY_ALLOCATIONS),
        "planned_hard_cut_migration_steps": len(MIGRATION_STEPS),
        "external_frontier_rows_adjudicated": len(FRONTIER_CROSSWALK),
        "frontier_level_noncollapse_laws": len(FRONTIER_LAWS),
        "frontier_genuine_research_vacancies": sum(row["disposition"] == "GENUINE_RESEARCH_VACANCY" for row in FRONTIER_CROSSWALK),
        "open_gaps": len(gaps),
        "ratified_products": 0,
        "ratified_contracts": 0,
        "qualified_implementations": 0,
        "completion_claim": False,
        "status": "RESEARCH_AUDIT_ACTIVE_INCOMPLETE",
    }
    return {
        "evidence": all_sources,
        "semantic_axes": axes,
        "artifact_kinds": artifacts,
        "result_kinds": results,
        "product_hypotheses": product_hypotheses,
        "library_hypotheses": libraries,
        "noncollapse_laws": laws,
        "artifact_axis_obligations": axis_obligations,
        "compatibility_cells": compatibility,
        "open_gaps": gaps,
        "split_adjudications": SPLIT_ADJUDICATIONS,
        "split_library_allocations": LIBRARY_ALLOCATIONS,
        "split_migration_steps": MIGRATION_STEPS,
        "split_ddd_dossiers": SPLIT_DDD_DOSSIERS,
        "frontier_crosswalk": FRONTIER_CROSSWALK,
        "frontier_laws": FRONTIER_LAWS,
        "input_snapshot": input_snapshot(),
        "summary": summary,
    }


FILES = {
    "evidence": "evidence.jsonl",
    "semantic_axes": "semantic-axes.jsonl",
    "artifact_kinds": "presentation-artifacts.jsonl",
    "result_kinds": "analytical-result-kinds.jsonl",
    "product_hypotheses": "product-boundary-hypotheses.jsonl",
    "library_hypotheses": "library-boundary-hypotheses.jsonl",
    "noncollapse_laws": "non-collapse-laws.jsonl",
    "artifact_axis_obligations": "artifact-axis-obligations.jsonl",
    "compatibility_cells": "result-artifact-compatibility.jsonl",
    "open_gaps": "open-gaps.jsonl",
    "split_adjudications": "bi-reporting-split-adjudications.jsonl",
    "split_library_allocations": "bi-reporting-split-library-allocations.jsonl",
    "split_migration_steps": "bi-reporting-split-migration-plan.jsonl",
    "split_ddd_dossiers": "bi-reporting-split-ddd-dossiers.jsonl",
    "frontier_crosswalk": "external-38-family-frontier-crosswalk.jsonl",
    "frontier_laws": "frontier-level-non-collapse-laws.jsonl",
}


def outputs() -> dict[str, str]:
    built = build()
    files = {name: jsonl(built[key]) for key, name in FILES.items()}
    files["input-snapshot.json"] = json.dumps(built["input_snapshot"], ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    files["summary.json"] = json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps({
        "manifest_id": "manifest.presentation-experience-gap-audit.v1",
        "as_of": AS_OF,
        "files": claims,
        "completion_claim": False,
    }, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text() != text:
                stale.append(name)
        else:
            path.write_text(text)
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = build()["summary"]
    print(
        f"{'CHECK' if args.check else 'BUILD'} PASS presentation experience audit: "
        f"{summary['artifact_kinds']} artifacts x {summary['analytical_result_kinds']} result kinds; "
        f"{summary['semantic_axes']} axes; {summary['product_boundary_hypotheses']} product hypotheses; "
        f"{summary['candidate_library_vacancies']} exact library vacancies"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
