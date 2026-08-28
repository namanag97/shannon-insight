#!/usr/bin/env python3
"""Build iteration 2 of the macro-model challenge without rewriting iteration 1."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_macro_challenge import searchable_text
from iteration2_model import (
    CROSS_AXIS_INTERACTIONS,
    ITERATION1_AXIS_DELTA_SHA256,
    ITERATION1_SUMMARY_SHA256,
    ITERATION2_AXES,
    ITERATION2_CHALLENGES,
    ITERATION2_CORRECTIONS,
    ITERATION2_DEEP_CLAIMS,
    ITERATION2_PRIMARY_SOURCES,
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
        patterns = [pattern for pattern in facet["patterns"] if re.search(pattern, text, re.IGNORECASE)]
        if patterns:
            found.append({"facet": facet["facet"], "matched_patterns": patterns})
    return found


def build() -> dict[str, Any]:
    iteration1_summary_path = HERE / "summary.json"
    iteration1_deltas_path = HERE / "proposed-axis-deltas.jsonl"
    if git_blob_sha(iteration1_summary_path) != ITERATION1_SUMMARY_SHA256:
        raise ValueError("iteration-1 summary changed; iteration 2 must rebase explicitly")
    if git_blob_sha(iteration1_deltas_path) != ITERATION1_AXIS_DELTA_SHA256:
        raise ValueError("iteration-1 axis deltas changed; iteration 2 must rebase explicitly")

    iteration1_summary = json.loads(iteration1_summary_path.read_text(encoding="utf-8"))
    iteration1_deltas = {row["axis"]: row for row in rows(iteration1_deltas_path)}
    base_summary = json.loads((SEM / "summary.json").read_text(encoding="utf-8"))
    proposals = rows(GENERATION / "library-instance-proposals.jsonl")
    libraries = {row["library_id"]: row for row in rows(REGISTRY / "library-contributions.jsonl")}

    source_by_id = {row["source_id"]: row for row in ITERATION2_PRIMARY_SOURCES}
    claims_by_axis: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in ITERATION2_DEEP_CLAIMS:
        claims_by_axis[claim["supports_axis"]].append(claim)

    signatures = []
    family_axis_members: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    axis_facet_counts: dict[str, Counter[str]] = {axis["axis"]: Counter() for axis in ITERATION2_AXES}
    family_hit_counts: dict[str, Counter[str]] = {axis["axis"]: Counter() for axis in ITERATION2_AXES}

    for proposal in proposals:
        library = libraries[proposal["library_ref"]]
        text = searchable_text(library)
        axis_selections = []
        for axis in ITERATION2_AXES:
            hits = matches(axis, text)
            status = "EXPLICIT_CANDIDATE_SET_UNRATIFIED" if hits else "UNRESOLVED_OWNER_INPUT_REQUIRED"
            for hit in hits:
                axis_facet_counts[axis["axis"]][hit["facet"]] += 1
            if hits:
                family_hit_counts[axis["axis"]][proposal["family_id"]] += 1
            selection = {
                "axis": axis["axis"],
                "status": status,
                "candidate_facets": hits,
                "owner_must": "accept, reject, split or replace every candidate; no-hit remains unresolved rather than inapplicable",
            }
            axis_selections.append(selection)
            family_axis_members[(proposal["family_id"], axis["axis"])].append(
                {
                    "library_ref": proposal["library_ref"],
                    "status": status,
                    "candidate_facets": [hit["facet"] for hit in hits],
                }
            )
        signatures.append(
            {
                "record_kind": "macro_model_iteration2_signature_candidate",
                "signature_id": "signature.macro.iter2." + proposal["library_ref"].removeprefix("library."),
                "library_ref": proposal["library_ref"],
                "family_id": proposal["family_id"],
                "source_gap_ref": proposal["source_gap_ref"],
                "axis_selections": axis_selections,
                "status": "DISCOVERY_SIGNATURE_NOT_AUTHORITY",
                "canonical_mutation_allowed": False,
                "completion_claim": False,
            }
        )

    packages = []
    targeted = []
    for ordinal, ((family_id, axis_id), members) in enumerate(sorted(family_axis_members.items()), start=1):
        unresolved = sorted(member["library_ref"] for member in members if member["status"] == "UNRESOLVED_OWNER_INPUT_REQUIRED")
        facets = Counter(facet for member in members for facet in member["candidate_facets"])
        package_id = f"work.macro.iter2.{ordinal:04d}"
        packages.append(
            {
                "record_kind": "macro_model_iteration2_family_axis_review_package",
                "work_package_id": package_id,
                "family_id": family_id,
                "axis": axis_id,
                "library_count": len(members),
                "candidate_library_count": len(members) - len(unresolved),
                "unresolved_library_count": len(unresolved),
                "unresolved_library_refs": unresolved,
                "candidate_facet_counts": dict(sorted(facets.items())),
                "status": "OWNER_RESEARCH_AND_RATIFICATION_REQUIRED",
                "canonical_mutation_allowed": False,
                "completion_claim": False,
            }
        )
        if unresolved:
            axis = next(item for item in ITERATION2_AXES if item["axis"] == axis_id)
            targeted.append(
                {
                    "record_kind": "macro_model_iteration2_targeted_evidence_work_package",
                    "targeted_work_package_id": package_id.replace("work.macro", "targeted.macro"),
                    "review_package_ref": package_id,
                    "family_id": family_id,
                    "axis": axis_id,
                    "unresolved_library_count": len(unresolved),
                    "unresolved_library_refs": unresolved,
                    "primary_source_refs": sorted(axis["evidence_refs"]),
                    "deep_claim_refs": [claim["claim_id"] for claim in claims_by_axis[axis_id]],
                    "allowed_outcomes": ["REQUIRED", "CONDITIONAL", "INAPPLICABLE", "PROHIBITED", "SPLIT_REQUIRED", "MISSING_FACET", "UNRESOLVED"],
                    "research_law": "Evidence may route a member to review but cannot create applicability, owner or canonical-contract authority automatically.",
                    "status": "TARGETED_PRIMARY_SOURCE_REVIEW_REQUIRED",
                    "canonical_mutation_allowed": False,
                    "completion_claim": False,
                }
            )

    axis_deltas = []
    for axis in ITERATION2_AXES:
        axis_id = axis["axis"]
        selections = [selection for row in signatures for selection in row["axis_selections"] if selection["axis"] == axis_id]
        evidence_refs = set(axis["evidence_refs"])
        axis_deltas.append(
            {
                "record_kind": "macro_model_iteration2_axis_delta",
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
                "candidate_facet_occurrences": sum(axis_facet_counts[axis_id].values()),
                "candidate_facet_counts": dict(sorted(axis_facet_counts[axis_id].items())),
                "families_with_candidate_hits": len(family_hit_counts[axis_id]),
                "model_verdict": axis["model_verdict"],
                "status": "EVIDENCE_BACKED_RESEARCH_AXIS_NOT_RATIFIED",
                "canonical_mutation_allowed": False,
                "completion_claim": False,
            }
        )

    iter2_by_axis = {row["axis"]: row for row in axis_deltas}
    scope_before = iteration1_deltas["scope_population_and_eligibility"]
    scope_after = iter2_by_axis["scope_population_and_eligibility"]
    correction_receipts = []
    for correction in ITERATION2_CORRECTIONS:
        receipt = dict(correction)
        if correction["correction_id"].endswith("scope-generic-token-contamination"):
            receipt["iteration1_candidate_cells"] = scope_before["candidate_cells"]
            receipt["iteration2_candidate_cells"] = scope_after["candidate_cells"]
            receipt["candidate_cell_reduction"] = scope_before["candidate_cells"] - scope_after["candidate_cells"]
            receipt["iteration1_generic_context_occurrences"] = scope_before["candidate_facet_counts"].get("contextual_constraint", 0)
            receipt["iteration2_population_applicability_occurrences"] = scope_after["candidate_facet_counts"].get("population_applicability_predicate", 0)
            receipt["validation_result"] = "FALSE_POSITIVE_SURFACE_REDUCED" if scope_after["candidate_cells"] < scope_before["candidate_cells"] else "FAILED_TO_REDUCE"
        else:
            receipt["validation_result"] = "SEPARATE_CAUSAL_AXIS_PRESENT" if "causal_and_interventional_semantics" in iter2_by_axis else "MISSING_CAUSAL_AXIS"
        correction_receipts.append(receipt)

    challenge_delta = [row for row in ITERATION2_CHALLENGES if row not in __import__("source_model").MACRO_CHALLENGES]
    all_source_ids = {row["source_id"] for row in ITERATION2_PRIMARY_SOURCES}
    base_source_ids = {row["source_id"] for row in __import__("source_model").PRIMARY_SOURCES}
    new_sources = [row for row in ITERATION2_PRIMARY_SOURCES if row["source_id"] not in base_source_ids]
    new_claim_ids = {row["claim_id"] for row in ITERATION2_DEEP_CLAIMS} - {row["claim_id"] for row in __import__("source_model").DEEP_EVIDENCE_CLAIMS}
    new_claims = [row for row in ITERATION2_DEEP_CLAIMS if row["claim_id"] in new_claim_ids]

    effective_model = {
        "record_kind": "effective_macro_model_research_candidate_iteration2",
        "model_id": "model.enterprise-data-analytics-semantic-axes.challenge-v2",
        "as_of": AS_OF,
        "base_axis_count": base_summary["axes"],
        "candidate_axis_count": len(ITERATION2_AXES),
        "effective_research_axis_count": base_summary["axes"] + len(ITERATION2_AXES),
        "candidate_axis_ids": [axis["axis"] for axis in ITERATION2_AXES],
        "cross_axis_interaction_count": len(CROSS_AXIS_INTERACTIONS),
        "laws": [
            "Iteration 1 remains immutable and digest-bound; iteration 2 records corrections instead of rewriting history.",
            "Axis universality is a semantic-question claim, not a lexical-frequency claim.",
            "A lexical hit is only a review candidate; a lexical miss remains unresolved rather than inapplicable.",
            "Cross-axis dependency never authorizes collapsing one axis into another.",
            "Causal order and temporal/topological order are explicitly non-equivalent.",
            "Stochastic mechanism and probabilistic uncertainty are explicitly non-equivalent.",
            "No macro challenge closes owner, exact-contract, implementation, qualification, provider, physical or vertical-acceptance gates.",
        ],
        "status": "ITERATION_2_RESEARCH_CHALLENGE_CANDIDATE_NOT_RATIFIED",
        "canonical_mutation_allowed": False,
        "completion_claim": False,
    }

    total_new_cells = len(signatures) * len(ITERATION2_AXES)
    candidate_cells = sum(bool(selection["candidate_facets"]) for row in signatures for selection in row["axis_selections"])
    summary = {
        "program_id": "program.macro-model-primary-source-challenge.v2",
        "as_of": AS_OF,
        "iteration1_summary_blob_sha": ITERATION1_SUMMARY_SHA256,
        "iteration1_axis_delta_blob_sha": ITERATION1_AXIS_DELTA_SHA256,
        "primary_source_count": len(ITERATION2_PRIMARY_SOURCES),
        "new_primary_source_count": len(new_sources),
        "primary_source_issuer_count": len({row["issuer"] for row in ITERATION2_PRIMARY_SOURCES}),
        "deep_bounded_claim_count": len(ITERATION2_DEEP_CLAIMS),
        "new_deep_bounded_claim_count": len(new_claims),
        "macro_challenge_count": len(ITERATION2_CHALLENGES),
        "new_macro_challenge_count": len(challenge_delta),
        "base_axis_count": base_summary["axes"],
        "candidate_axis_count": len(ITERATION2_AXES),
        "effective_research_axis_count": base_summary["axes"] + len(ITERATION2_AXES),
        "library_count": len(signatures),
        "family_count": len({row["family_id"] for row in proposals}),
        "base_axis_cells": base_summary["axis_cells"],
        "iteration2_candidate_axis_cells": total_new_cells,
        "effective_research_axis_cells": base_summary["axis_cells"] + total_new_cells,
        "candidate_cells": candidate_cells,
        "unresolved_cells": total_new_cells - candidate_cells,
        "family_axis_review_packages": len(packages),
        "targeted_evidence_work_packages": len(targeted),
        "targeted_unresolved_library_occurrences": sum(row["unresolved_library_count"] for row in targeted),
        "scope_iteration1_candidate_cells": scope_before["candidate_cells"],
        "scope_iteration2_candidate_cells": scope_after["candidate_cells"],
        "scope_candidate_cell_reduction": scope_before["candidate_cells"] - scope_after["candidate_cells"],
        "causal_candidate_cells": iter2_by_axis["causal_and_interventional_semantics"]["candidate_cells"],
        "stochastic_candidate_cells": iter2_by_axis["stochastic_mechanism_and_assignment"]["candidate_cells"],
        "cross_axis_interactions": len(CROSS_AXIS_INTERACTIONS),
        "canonical_gaps_closed": 0,
        "owner_decisions": 0,
        "completion_claim": False,
        "status": "ITERATION_2_MODELED_RECOMPUTE_REQUIRED",
    }

    return {
        "sources": ITERATION2_PRIMARY_SOURCES,
        "new_sources": new_sources,
        "claims": ITERATION2_DEEP_CLAIMS,
        "new_claims": new_claims,
        "challenges": ITERATION2_CHALLENGES,
        "new_challenges": challenge_delta,
        "axis_deltas": axis_deltas,
        "signatures": signatures,
        "packages": packages,
        "targeted": targeted,
        "interactions": CROSS_AXIS_INTERACTIONS,
        "corrections": correction_receipts,
        "model": effective_model,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "iteration2-primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "iteration2-new-primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["new_sources"]),
        "iteration2-deep-evidence-claims.jsonl": "".join(canonical(row) + "\n" for row in built["claims"]),
        "iteration2-new-deep-claims.jsonl": "".join(canonical(row) + "\n" for row in built["new_claims"]),
        "iteration2-macro-challenges.jsonl": "".join(canonical(row) + "\n" for row in built["challenges"]),
        "iteration2-new-challenges.jsonl": "".join(canonical(row) + "\n" for row in built["new_challenges"]),
        "iteration2-axis-deltas.jsonl": "".join(canonical(row) + "\n" for row in built["axis_deltas"]),
        "iteration2-signatures.jsonl": "".join(canonical(row) + "\n" for row in built["signatures"]),
        "iteration2-family-axis-review-packages.jsonl": "".join(canonical(row) + "\n" for row in built["packages"]),
        "iteration2-targeted-evidence-work-packages.jsonl": "".join(canonical(row) + "\n" for row in built["targeted"]),
        "iteration2-cross-axis-interactions.jsonl": "".join(canonical(row) + "\n" for row in built["interactions"]),
        "iteration2-correction-receipts.jsonl": "".join(canonical(row) + "\n" for row in built["corrections"]),
        "iteration2-effective-macro-model.json": json.dumps(built["model"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "iteration2-summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    manifest = {
        name: {"bytes": len(text.encode("utf-8")), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
        for name, text in files.items()
    }
    files["iteration2-manifest.json"] = json.dumps(
        {"manifest_id": "manifest.macro-model-primary-source-challenge.v2", "as_of": AS_OF, "files": manifest, "completion_claim": False},
        sort_keys=True,
        indent=2,
    ) + "\n"
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
    summary = json.loads(generated["iteration2-summary.json"])
    print(
        f"{'CHECK' if args.check else 'BUILD'} PASS macro iteration 2: "
        f"{summary['primary_source_count']} sources; 16+{summary['candidate_axis_count']}={summary['effective_research_axis_count']} axes; "
        f"{summary['iteration2_candidate_axis_cells']} candidate-axis cells; scope false-positive reduction {summary['scope_candidate_cell_reduction']}; "
        "zero authority/canonical promotions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
