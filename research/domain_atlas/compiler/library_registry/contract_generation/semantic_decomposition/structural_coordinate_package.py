#!/usr/bin/env python3
"""Deterministic mechanics for structural, decision-open semantic-axis coordinate packages."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from member_axis_rebase import build_member_rebase, load_jsonl


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def structural_dockets(*, axis: str, preclassifications_path: Path, docket_prefix: str, record_kind: str) -> list[dict[str, Any]]:
    by_family: dict[str, list[str]] = defaultdict(list)
    for row in load_jsonl(preclassifications_path):
        if row["axis"] == axis:
            by_family[row["family_id"]].append(row["library_ref"])
    return [
        {
            "record_kind": record_kind,
            "docket_id": f"{docket_prefix}.{family.removeprefix('constitution.family.').replace('_', '-')}.v1",
            "family_ref": family,
            "library_refs": sorted(refs),
            "library_count": len(refs),
            "evidence_candidate_refs": [],
            "source_evidence_binding": "UNRESOLVED_PER_FAMILY_AND_USE_SITE",
            "authority_limit": "Mechanical all-axis preclassification supplies membership and lexical discovery only.",
        }
        for family, refs in sorted(by_family.items())
    ]


def build_package(
    *, axis: str, preclassifications_path: Path, docket_prefix: str, docket_record_kind: str,
    cluster_prefix: str, cluster_record_kind: str, member_record_kind: str, member_route_prefix: str,
    extension_record_kind: str, extension_prefix: str, route_for_facets: Callable[[tuple[str, ...]], str],
    cluster_next_evidence: list[str], member_open_fields: dict[str, str], extension_record_kinds: list[str],
    ontology: dict[str, Any], sources: list[dict[str, Any]], archetypes: list[dict[str, Any]], kernels: list[dict[str, Any]],
    summary_base: dict[str, Any], lexical_summary_key: str, vacancy_summary_key: str,
) -> dict[str, Any]:
    dockets = structural_dockets(axis=axis, preclassifications_path=preclassifications_path, docket_prefix=docket_prefix, record_kind=docket_record_kind)
    rebase = build_member_rebase(axis=axis, dockets=dockets, preclassifications_path=preclassifications_path, cluster_prefix=cluster_prefix, cluster_route=route_for_facets)
    clusters = [{"record_kind":cluster_record_kind, **row, "required_next_evidence":cluster_next_evidence, "family_source_evidence_binding":"UNRESOLVED", "member_applicability":"UNRESOLVED", "owner_decision":"UNRESOLVED", "canonical_gaps_closed":0, "completion_claim":False} for row in rebase["clusters"]]
    members = [{"record_kind":member_record_kind, "route_id":f"{member_route_prefix}.{row['library_ref'].removeprefix('library.').replace('.', '-').replace('_', '-')}", **row, "flat_projection_effect":"DISCOVERY_ROUTING_ONLY_NOT_APPLICABILITY", **member_open_fields, "family_source_evidence_binding":"UNRESOLVED", "member_applicability":"UNRESOLVED", "owner_decision":"UNRESOLVED", "canonical_gaps_closed":0, "status":"LOSSLESSLY_ROUTED_RESEARCH_OPEN", "completion_claim":False} for row in rebase["members"]]
    extensions = [{"record_kind":extension_record_kind, "extension_id":f"{extension_prefix}.{family.removeprefix('constitution.family.').replace('_', '-')}.v1", "family_ref":family, "structural_rebase_docket_ref":docket["docket_id"], "represented_library_refs":docket["library_refs"], "represented_library_count":docket["library_count"], "required_record_kinds":extension_record_kinds, "source_evidence_binding":"UNRESOLVED", "owner_decision":"UNRESOLVED", "member_applicability_decisions":0, "canonical_gaps_closed":0, "status":"CANDIDATE_UNRATIFIED", "completion_claim":False} for family,docket in sorted(rebase["docket_by_family"].items())]
    summary = {**summary_base, "primary_sources":len(sources), "structural_family_dockets":len(dockets), "family_extension_candidates":len(extensions), "research_clusters":len(clusters), "target_member_routes":len(members), lexical_summary_key:rebase["lexical_member_count"], vacancy_summary_key:rebase["vacancy_member_count"], "family_source_evidence_bindings_supplied":0, "member_applicability_decisions":0, "owner_decisions":0, "canonical_gaps_closed":0, "completion_claim":False}
    return {"ontology":ontology,"sources":sources,"archetypes":archetypes,"kernels":kernels,"dockets":dockets,"clusters":clusters,"members":members,"extensions":extensions,"summary":summary}


def render_outputs(*, built: dict[str, Any], ontology_filename: str, archetypes_filename: str, kernels_filename: str, members_filename: str, manifest_id: str, as_of: str) -> dict[str, str]:
    files = {
        ontology_filename: json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2)+"\n",
        "primary-sources.jsonl":"".join(canonical(row)+"\n" for row in built["sources"]),
        archetypes_filename:"".join(canonical(row)+"\n" for row in built["archetypes"]),
        kernels_filename:"".join(canonical(row)+"\n" for row in built["kernels"]),
        "structural-family-dockets.jsonl":"".join(canonical(row)+"\n" for row in built["dockets"]),
        "member-research-clusters.jsonl":"".join(canonical(row)+"\n" for row in built["clusters"]),
        members_filename:"".join(canonical(row)+"\n" for row in built["members"]),
        "extension-candidates.jsonl":"".join(canonical(row)+"\n" for row in built["extensions"]),
        "summary.json":json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2)+"\n",
    }
    claims={name:{"bytes":len(text.encode()),"sha256":hashlib.sha256(text.encode()).hexdigest()} for name,text in files.items()}
    files["manifest.json"]=json.dumps({"manifest_id":manifest_id,"as_of":as_of,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n"
    return files
