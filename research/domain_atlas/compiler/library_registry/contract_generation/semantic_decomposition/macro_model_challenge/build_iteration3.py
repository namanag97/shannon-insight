#!/usr/bin/env python3
"""Build iteration 3: split quantitative-value semantics from observation/metrology."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_macro_challenge import searchable_text
from iteration3_model import (
    ITERATION2_AXIS_DELTA_BLOB_SHA,
    ITERATION2_SUMMARY_BLOB_SHA,
    ITERATION3_AXES,
    ITERATION3_CHALLENGES,
    ITERATION3_CORRECTIONS,
    ITERATION3_DEEP_CLAIMS,
    ITERATION3_INTERACTIONS,
    ITERATION3_PRIMARY_SOURCES,
)

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
GENERATION = SEM.parent
REGISTRY = GENERATION.parent
AS_OF = "2026-08-28"


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def matches(axis: dict[str, Any], text: str) -> list[dict[str, Any]]:
    found = []
    for facet in axis["facets"]:
        local = [pattern for pattern in facet["patterns"] if re.search(pattern, text, flags=re.IGNORECASE)]
        if local:
            found.append({"facet": facet["facet"], "matched_patterns": local})
    return found


def build() -> dict[str, Any]:
    if git_blob_sha(HERE / "iteration2-summary.json") != ITERATION2_SUMMARY_BLOB_SHA:
        raise ValueError("iteration-2 summary changed; iteration 3 must explicitly rebase")
    if git_blob_sha(HERE / "iteration2-axis-deltas.jsonl") != ITERATION2_AXIS_DELTA_BLOB_SHA:
        raise ValueError("iteration-2 axis deltas changed; iteration 3 must explicitly rebase")

    iteration2_summary = json.loads((HERE / "iteration2-summary.json").read_text(encoding="utf-8"))
    iteration2_deltas = {row["axis"]: row for row in rows(HERE / "iteration2-axis-deltas.jsonl")}
    base_summary = json.loads((SEM / "summary.json").read_text(encoding="utf-8"))
    proposals = rows(GENERATION / "library-instance-proposals.jsonl")
    libraries = {row["library_id"]: row for row in rows(REGISTRY / "library-contributions.jsonl")}
    source_by_id = {row["source_id"]: row for row in ITERATION3_PRIMARY_SOURCES}
    claims_by_axis: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in ITERATION3_DEEP_CLAIMS:
        claims_by_axis[claim["supports_axis"]].append(claim)

    signatures = []
    family_axis: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    facet_counts: dict[str, Counter[str]] = {axis["axis"]: Counter() for axis in ITERATION3_AXES}
    family_hits: dict[str, set[str]] = {axis["axis"]: set() for axis in ITERATION3_AXES}

    for proposal in proposals:
        text = searchable_text(libraries[proposal["library_ref"]])
        selections = []
        for axis in ITERATION3_AXES:
            hits = matches(axis, text)
            status = "EXPLICIT_CANDIDATE_SET_UNRATIFIED" if hits else "UNRESOLVED_OWNER_INPUT_REQUIRED"
            for hit in hits:
                facet_counts[axis["axis"]][hit["facet"]] += 1
            if hits:
                family_hits[axis["axis"]].add(proposal["family_id"])
            selections.append({"axis": axis["axis"], "status": status, "candidate_facets": hits})
            family_axis[(proposal["family_id"], axis["axis"])].append(
                {"library_ref": proposal["library_ref"], "status": status, "candidate_facets": [hit["facet"] for hit in hits]}
            )
        signatures.append(
            {
                "record_kind": "macro_model_iteration3_signature_candidate",
                "signature_id": "signature.macro.iter3." + proposal["library_ref"].removeprefix("library."),
                "library_ref": proposal["library_ref"],
                "family_id": proposal["family_id"],
                "source_gap_ref": proposal["source_gap_ref"],
                "axis_selections": selections,
                "status": "DISCOVERY_SIGNATURE_NOT_AUTHORITY",
                "canonical_mutation_allowed": False,
                "completion_claim": False,
            }
        )

    axis_deltas = []
    for axis in ITERATION3_AXES:
        axis_id = axis["axis"]
        selections = [selection for row in signatures for selection in row["axis_selections"] if selection["axis"] == axis_id]
        evidence_refs = set(axis["evidence_refs"])
        axis_deltas.append(
            {
                "record_kind": "macro_model_iteration3_axis_delta",
                "axis": axis_id,
                "question": axis["question"],
                "phase": axis["phase"],
                "facet_count": len(axis["facets"]),
                "non_collapse_laws": axis["non_collapse"],
                "primary_source_refs": sorted(evidence_refs),
                "independent_issuer_count": len({source_by_id[ref]["issuer"] for ref in evidence_refs}),
                "deep_claim_refs": [claim["claim_id"] for claim in claims_by_axis[axis_id]],
                "candidate_cells": sum(bool(selection["candidate_facets"]) for selection in selections),
                "unresolved_cells": sum(not selection["candidate_facets"] for selection in selections),
                "candidate_facet_occurrences": sum(facet_counts[axis_id].values()),
                "candidate_facet_counts": dict(sorted(facet_counts[axis_id].items())),
                "families_with_candidate_hits": len(family_hits[axis_id]),
                "model_verdict": axis["model_verdict"],
                "status": "EVIDENCE_BACKED_RESEARCH_AXIS_NOT_RATIFIED",
                "canonical_mutation_allowed": False,
                "completion_claim": False,
            }
        )
    delta_by_axis = {row["axis"]: row for row in axis_deltas}

    packages = []
    targeted = []
    for ordinal, ((family_id, axis_id), members) in enumerate(sorted(family_axis.items()), start=1):
        unresolved = sorted(member["library_ref"] for member in members if member["status"] == "UNRESOLVED_OWNER_INPUT_REQUIRED")
        counts = Counter(facet for member in members for facet in member["candidate_facets"])
        work_id = f"work.macro.iter3.{ordinal:04d}"
        packages.append(
            {
                "record_kind": "macro_model_iteration3_family_axis_review_package",
                "work_package_id": work_id,
                "family_id": family_id,
                "axis": axis_id,
                "library_count": len(members),
                "candidate_library_count": len(members) - len(unresolved),
                "unresolved_library_count": len(unresolved),
                "unresolved_library_refs": unresolved,
                "candidate_facet_counts": dict(sorted(counts.items())),
                "status": "OWNER_RESEARCH_AND_RATIFICATION_REQUIRED",
                "canonical_mutation_allowed": False,
                "completion_claim": False,
            }
        )
        if unresolved:
            axis = next(item for item in ITERATION3_AXES if item["axis"] == axis_id)
            targeted.append(
                {
                    "record_kind": "macro_model_iteration3_targeted_evidence_work_package",
                    "targeted_work_package_id": work_id.replace("work.macro", "targeted.macro"),
                    "review_package_ref": work_id,
                    "family_id": family_id,
                    "axis": axis_id,
                    "unresolved_library_count": len(unresolved),
                    "unresolved_library_refs": unresolved,
                    "primary_source_refs": sorted(axis["evidence_refs"]),
                    "deep_claim_refs": [claim["claim_id"] for claim in claims_by_axis[axis_id]],
                    "allowed_outcomes": ["REQUIRED", "CONDITIONAL", "INAPPLICABLE", "PROHIBITED", "SPLIT_REQUIRED", "MISSING_FACET", "UNRESOLVED"],
                    "status": "TARGETED_PRIMARY_SOURCE_REVIEW_REQUIRED",
                    "canonical_mutation_allowed": False,
                    "completion_claim": False,
                }
            )

    iteration2_source_ids = {row["source_id"] for row in rows(HERE / "iteration2-primary-sources.jsonl")}
    new_sources = [row for row in ITERATION3_PRIMARY_SOURCES if row["source_id"] not in iteration2_source_ids]
    iteration2_claim_ids = {row["claim_id"] for row in rows(HERE / "iteration2-deep-evidence-claims.jsonl")}
    new_claims = [row for row in ITERATION3_DEEP_CLAIMS if row["claim_id"] not in iteration2_claim_ids]
    iteration2_challenge_ids = {row["challenge_id"] for row in rows(HERE / "iteration2-macro-challenges.jsonl")}
    new_challenges = [row for row in ITERATION3_CHALLENGES if row["challenge_id"] not in iteration2_challenge_ids]

    old_measurement = iteration2_deltas["measurement_and_observation"]
    quantity = delta_by_axis["quantity_and_value_semantics"]
    observation = delta_by_axis["observation_measurement_and_metrology"]
    correction_receipts = [
        {
            **ITERATION3_CORRECTIONS[0],
            "iteration2_combined_axis_candidate_cells": old_measurement["candidate_cells"],
            "iteration3_quantity_candidate_cells": quantity["candidate_cells"],
            "iteration3_observation_candidate_cells": observation["candidate_cells"],
            "iteration3_distinct_candidate_cell_union_upper_bound": quantity["candidate_cells"] + observation["candidate_cells"],
            "validation_result": "SPLIT_EFFECTIVE" if quantity["candidate_cells"] > 0 and observation["candidate_cells"] > 0 else "SPLIT_FAILED",
        }
    ]

    total_candidate_axis_cells = len(signatures) * len(ITERATION3_AXES)
    candidate_cells = sum(bool(selection["candidate_facets"]) for row in signatures for selection in row["axis_selections"])
    summary = {
        "program_id": "program.macro-model-primary-source-challenge.v3",
        "as_of": AS_OF,
        "iteration2_summary_blob_sha": ITERATION2_SUMMARY_BLOB_SHA,
        "iteration2_axis_delta_blob_sha": ITERATION2_AXIS_DELTA_BLOB_SHA,
        "primary_source_count": len(ITERATION3_PRIMARY_SOURCES),
        "new_primary_source_count": len(new_sources),
        "primary_source_issuer_count": len({row["issuer"] for row in ITERATION3_PRIMARY_SOURCES}),
        "deep_bounded_claim_count": len(ITERATION3_DEEP_CLAIMS),
        "new_deep_bounded_claim_count": len(new_claims),
        "macro_challenge_count": len(ITERATION3_CHALLENGES),
        "new_macro_challenge_count": len(new_challenges),
        "base_axis_count": base_summary["axes"],
        "candidate_axis_count": len(ITERATION3_AXES),
        "effective_research_axis_count": base_summary["axes"] + len(ITERATION3_AXES),
        "library_count": len(signatures),
        "family_count": len({row["family_id"] for row in proposals}),
        "base_axis_cells": base_summary["axis_cells"],
        "iteration3_candidate_axis_cells": total_candidate_axis_cells,
        "effective_research_axis_cells": base_summary["axis_cells"] + total_candidate_axis_cells,
        "candidate_cells": candidate_cells,
        "unresolved_cells": total_candidate_axis_cells - candidate_cells,
        "family_axis_review_packages": len(packages),
        "targeted_evidence_work_packages": len(targeted),
        "targeted_unresolved_library_occurrences": sum(row["unresolved_library_count"] for row in targeted),
        "replaced_iteration2_axis": "measurement_and_observation",
        "replacement_axes": ["quantity_and_value_semantics", "observation_measurement_and_metrology"],
        "iteration2_measurement_candidate_cells": old_measurement["candidate_cells"],
        "quantity_candidate_cells": quantity["candidate_cells"],
        "observation_candidate_cells": observation["candidate_cells"],
        "cross_axis_interactions": len(ITERATION3_INTERACTIONS),
        "canonical_gaps_closed": 0,
        "owner_decisions": 0,
        "completion_claim": False,
        "status": "ITERATION_3_MODELED_RECOMPUTE_REQUIRED",
    }
    model = {
        "record_kind": "effective_macro_model_research_candidate_iteration3",
        "model_id": "model.enterprise-data-analytics-semantic-axes.challenge-v3",
        "as_of": AS_OF,
        "base_axis_count": base_summary["axes"],
        "candidate_axis_ids": [axis["axis"] for axis in ITERATION3_AXES],
        "candidate_axis_count": len(ITERATION3_AXES),
        "effective_research_axis_count": base_summary["axes"] + len(ITERATION3_AXES),
        "split_lineage": {"measurement_and_observation": ["quantity_and_value_semantics", "observation_measurement_and_metrology"]},
        "laws": [
            "Iteration 2 is immutable and digest-bound; the old measurement axis is superseded only in this research candidate.",
            "Quantitative value semantics and observation/metrology are independent questions linked only when an observation result is quantitative.",
            "Currency is unit-like for monetary interpretation but is not an SI physical unit and cannot inherit physical conversion/calibration laws.",
            "A numeric or monetary value need not be an observation; targets, prices, notionals and declared amounts preserve epistemic status separately.",
            "No research-axis split closes semantic-owner, exact-contract, implementation, qualification, provider, physical or vertical-acceptance gates.",
        ],
        "status": "ITERATION_3_RESEARCH_CHALLENGE_CANDIDATE_NOT_RATIFIED",
        "canonical_mutation_allowed": False,
        "completion_claim": False,
    }
    return {
        "sources": ITERATION3_PRIMARY_SOURCES,
        "new_sources": new_sources,
        "claims": ITERATION3_DEEP_CLAIMS,
        "new_claims": new_claims,
        "challenges": ITERATION3_CHALLENGES,
        "new_challenges": new_challenges,
        "axis_deltas": axis_deltas,
        "signatures": signatures,
        "packages": packages,
        "targeted": targeted,
        "interactions": ITERATION3_INTERACTIONS,
        "corrections": correction_receipts,
        "model": model,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "iteration3-primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "iteration3-new-primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["new_sources"]),
        "iteration3-deep-evidence-claims.jsonl": "".join(canonical(row) + "\n" for row in built["claims"]),
        "iteration3-new-deep-claims.jsonl": "".join(canonical(row) + "\n" for row in built["new_claims"]),
        "iteration3-macro-challenges.jsonl": "".join(canonical(row) + "\n" for row in built["challenges"]),
        "iteration3-new-challenges.jsonl": "".join(canonical(row) + "\n" for row in built["new_challenges"]),
        "iteration3-axis-deltas.jsonl": "".join(canonical(row) + "\n" for row in built["axis_deltas"]),
        "iteration3-signatures.jsonl": "".join(canonical(row) + "\n" for row in built["signatures"]),
        "iteration3-family-axis-review-packages.jsonl": "".join(canonical(row) + "\n" for row in built["packages"]),
        "iteration3-targeted-evidence-work-packages.jsonl": "".join(canonical(row) + "\n" for row in built["targeted"]),
        "iteration3-cross-axis-interactions.jsonl": "".join(canonical(row) + "\n" for row in built["interactions"]),
        "iteration3-correction-receipts.jsonl": "".join(canonical(row) + "\n" for row in built["corrections"]),
        "iteration3-effective-macro-model.json": json.dumps(built["model"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "iteration3-summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode("utf-8")), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()} for name, text in files.items()}
    files["iteration3-manifest.json"] = json.dumps({"manifest_id":"manifest.macro-model-primary-source-challenge.v3","as_of":AS_OF,"files":manifest,"completion_claim":False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = outputs()
    stale = []
    for name, text in generated.items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = json.loads(generated["iteration3-summary.json"])
    print(
        f"{'CHECK' if args.check else 'BUILD'} PASS macro iteration 3: {summary['primary_source_count']} sources; "
        f"16+{summary['candidate_axis_count']}={summary['effective_research_axis_count']} axes; "
        f"quantity={summary['quantity_candidate_cells']} observation={summary['observation_candidate_cells']}; "
        "zero authority/canonical promotions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
