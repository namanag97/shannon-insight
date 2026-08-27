#!/usr/bin/env python3
"""Lossless mechanics shared by bearer-aware member-axis rebases.

This module groups only by exact family, preclassification state and ordered
lexical-facet signature.  It never supplies semantics, applicability, owners or
contracts.  Axis-specific builders add their own coordinate requirements and
research obligations to the returned skeletons.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def build_member_rebase(
    *,
    axis: str,
    dockets_path: Path | None = None,
    dockets: list[dict[str, Any]] | None = None,
    preclassifications_path: Path,
    cluster_prefix: str,
    cluster_route: Callable[[tuple[str, ...]], str],
) -> dict[str, Any]:
    if (dockets_path is None) == (dockets is None):
        raise ValueError(f"{axis}: supply exactly one of dockets_path or dockets")
    docket_rows = load_jsonl(dockets_path) if dockets_path is not None else list(dockets or [])
    preclass_rows = [
        row for row in load_jsonl(preclassifications_path) if row["axis"] == axis
    ]
    preclass_by_library = {row["library_ref"]: row for row in preclass_rows}
    if len(preclass_by_library) != len(preclass_rows):
        raise ValueError(f"{axis}: duplicate library refs in preclassifications")

    target_members = [
        library_ref for docket in docket_rows for library_ref in docket["library_refs"]
    ]
    if len(target_members) != len(set(target_members)):
        raise ValueError(f"{axis}: target dockets contain duplicate library occurrences")
    if not set(target_members) <= set(preclass_by_library):
        raise ValueError(f"{axis}: target member lacks a discovery preclassification")

    cluster_members: dict[tuple[str, str, tuple[str, ...]], list[str]] = defaultdict(list)
    docket_by_family = {row["family_ref"]: row for row in docket_rows}
    if len(docket_by_family) != len(docket_rows):
        raise ValueError(f"{axis}: duplicate family docket")
    for family_ref, docket in sorted(docket_by_family.items()):
        for library_ref in docket["library_refs"]:
            preclass = preclass_by_library[library_ref]
            facets = tuple(item["facet"] for item in preclass["candidate_facets"])
            cluster_members[(family_ref, preclass["preclassification"], facets)].append(
                library_ref
            )

    cluster_ids: dict[tuple[str, str, tuple[str, ...]], str] = {}
    cluster_skeletons: list[dict[str, Any]] = []
    family_ordinals: dict[str, int] = defaultdict(int)
    for key, library_refs in sorted(cluster_members.items()):
        family_ref, preclassification, facets = key
        family_ordinals[family_ref] += 1
        short = family_ref.removeprefix("constitution.family.")
        cluster_id = f"{cluster_prefix}.{short}.{family_ordinals[family_ref]:02d}"
        cluster_ids[key] = cluster_id
        cluster_skeletons.append(
            {
                "cluster_id": cluster_id,
                "family_ref": family_ref,
                "flat_preclassification": preclassification,
                "flat_candidate_facets": list(facets),
                "library_refs": sorted(library_refs),
                "library_count": len(library_refs),
                "research_route": cluster_route(facets),
            }
        )

    member_skeletons: list[dict[str, Any]] = []
    for family_ref, docket in sorted(docket_by_family.items()):
        for library_ref in docket["library_refs"]:
            preclass = preclass_by_library[library_ref]
            facets = tuple(item["facet"] for item in preclass["candidate_facets"])
            key = (family_ref, preclass["preclassification"], facets)
            member_skeletons.append(
                {
                    "library_ref": library_ref,
                    "family_ref": family_ref,
                    "source_gap_ref": preclass["source_gap_ref"],
                    "flat_preclassification_ref": preclass["preclassification_id"],
                    "flat_preclassification": preclass["preclassification"],
                    "flat_candidate_facets": list(facets),
                    "family_evidence_docket_ref": docket["docket_id"],
                    "family_evidence_candidate_refs": docket["evidence_candidate_refs"],
                    "research_cluster_ref": cluster_ids[key],
                    "research_route": cluster_route(facets),
                }
            )

    return {
        "dockets": docket_rows,
        "docket_by_family": docket_by_family,
        "clusters": cluster_skeletons,
        "members": member_skeletons,
        "target_member_count": len(target_members),
        "lexical_member_count": sum(bool(row["flat_candidate_facets"]) for row in member_skeletons),
        "vacancy_member_count": sum(not row["flat_candidate_facets"] for row in member_skeletons),
    }
