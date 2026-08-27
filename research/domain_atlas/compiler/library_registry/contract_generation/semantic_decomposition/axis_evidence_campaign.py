#!/usr/bin/env python3
"""Reusable deterministic mechanics for semantic-axis evidence campaigns.

Only selection, coverage, record shape, manifests and residual-state checks are
shared. Evidence claims and all semantic or authority decisions stay local to
the campaign that supplies them.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode()).hexdigest()


def build_campaign(
    *,
    axis: str,
    campaign_key: str,
    program_id: str,
    claims: dict[str, dict[str, Any]],
    targets_path: Path,
    as_of: str,
) -> dict[str, Any]:
    packages = sorted(
        (row for row in load_jsonl(targets_path) if row["axis"] == axis),
        key=lambda row: row["family_id"],
    )
    target_families = {row["family_id"] for row in packages}
    claim_families = set(claims)
    if target_families != claim_families:
        raise ValueError(
            "claim coverage differs from target families: "
            f"missing={sorted(target_families - claim_families)}, "
            f"extra={sorted(claim_families - target_families)}"
        )

    axis_slug = axis.replace("_", "-")
    candidates: list[dict[str, Any]] = []
    dockets: list[dict[str, Any]] = []
    for package in packages:
        family = package["family_id"]
        claim = claims[family]
        short = family.removeprefix("constitution.family.")
        candidate_id = f"evidence.{campaign_key}.{axis_slug}.{short}.001"
        candidates.append(
            {
                "record_kind": "family_axis_primary_evidence_candidate",
                "evidence_candidate_id": candidate_id,
                "family_ref": family,
                "axis": axis,
                "work_package_ref": package["work_package_id"],
                "source": {
                    "title": claim["title"],
                    "publisher": claim["publisher"],
                    "url": claim["url"],
                    "source_kind": "primary_specification_or_official_documentation",
                    "retrieved_on": as_of,
                },
                "bounded_claim": claim["claim"],
                "candidate_coordinate_implications": claim["coordinates"],
                "authority_limit": claim["limit"],
                "negative_twin": claim["negative"],
                "applicability_scope": "family_coordinate_candidate; member and exception applicability unresolved",
                "evidence_effect": "candidate evidence only; does not choose a family default, owner, exact contract, implementation or acceptance verdict",
                "status": "BOUNDED_PRIMARY_EVIDENCE_CANDIDATE_UNRATIFIED",
                "completion_claim": False,
            }
        )
        dockets.append(
            {
                "record_kind": "family_axis_evidence_docket",
                "docket_id": f"docket.{campaign_key}.{axis_slug}.{short}",
                "family_ref": family,
                "axis": axis,
                "work_package_ref": package["work_package_id"],
                "work_package_digest": digest(package),
                "library_refs": package["library_refs"],
                "library_count": package["library_count"],
                "evidence_candidate_refs": [candidate_id],
                "required_outputs": package["required_outputs"],
                "owner_decision": "UNRESOLVED",
                "member_applicability": "UNRESOLVED",
                "exception_clusters": [],
                "canonical_gaps_closed": 0,
                "status": "EVIDENCE_SEED_PRESENT_RESEARCH_AND_ADJUDICATION_OPEN",
                "completion_claim": False,
            }
        )

    return {
        "candidates": candidates,
        "dockets": dockets,
        "summary": {
            "program_id": program_id,
            "as_of": as_of,
            "axis": axis,
            "family_dockets": len(dockets),
            "primary_evidence_candidates": len(candidates),
            "represented_library_occurrences": sum(row["library_count"] for row in dockets),
            "owner_decisions": 0,
            "member_applicability_decisions": 0,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        },
    }


def campaign_outputs(
    *, built: dict[str, Any], manifest_id: str, as_of: str
) -> dict[str, str]:
    files = {
        "evidence-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["candidates"]),
        "family-evidence-dockets.jsonl": "".join(canonical(row) + "\n" for row in built["dockets"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": manifest_id,
            "as_of": as_of,
            "files": claims,
            "completion_claim": False,
        },
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def write_outputs(output_dir: Path, outputs: dict[str, str]) -> None:
    for name, text in outputs.items():
        (output_dir / name).write_text(text)


def validate_common(
    *,
    output_dir: Path,
    targets_path: Path,
    claims: dict[str, dict[str, Any]],
    axis: str,
    built: dict[str, Any],
    outputs: dict[str, str],
    expected_family_count: int | None = None,
    expected_library_occurrences: int | None = None,
) -> None:
    for name, text in outputs.items():
        assert (output_dir / name).is_file(), f"missing {name}"
        assert (output_dir / name).read_text() == text, f"stale {name}"

    targets = [row for row in load_jsonl(targets_path) if row["axis"] == axis]
    target_by_family = {row["family_id"]: row for row in targets}
    if expected_family_count is None:
        expected_family_count = len(target_by_family)
    if expected_library_occurrences is None:
        expected_library_occurrences = sum(row["library_count"] for row in targets)
    candidates = built["candidates"]
    dockets = built["dockets"]
    assert len(target_by_family) == len(claims) == len(candidates) == len(dockets) == expected_family_count
    assert {row["family_ref"] for row in candidates} == set(claims) == set(target_by_family)
    assert len({row["evidence_candidate_id"] for row in candidates}) == expected_family_count
    assert len({row["source"]["url"] for row in candidates}) == expected_family_count
    assert all(
        row["source"]["url"].startswith("https://")
        and row["bounded_claim"]
        and row["authority_limit"]
        and row["negative_twin"]
        and row["candidate_coordinate_implications"]
        for row in candidates
    )
    assert all(
        not row["completion_claim"]
        and row["status"] == "BOUNDED_PRIMARY_EVIDENCE_CANDIDATE_UNRATIFIED"
        for row in candidates
    )

    candidate_by_family = {row["family_ref"]: row for row in candidates}
    for docket in dockets:
        target = target_by_family[docket["family_ref"]]
        candidate = candidate_by_family[docket["family_ref"]]
        assert docket["work_package_ref"] == target["work_package_id"] == candidate["work_package_ref"]
        assert docket["work_package_digest"] == digest(target)
        assert docket["library_refs"] == target["library_refs"]
        assert docket["library_count"] == len(target["library_refs"])
        assert docket["evidence_candidate_refs"] == [candidate["evidence_candidate_id"]]
        assert docket["owner_decision"] == docket["member_applicability"] == "UNRESOLVED"
        assert docket["exception_clusters"] == []
        assert docket["canonical_gaps_closed"] == 0
        assert not docket["completion_claim"]

    summary = built["summary"]
    assert summary["represented_library_occurrences"] == expected_library_occurrences
    assert summary["owner_decisions"] == 0
    assert summary["member_applicability_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
