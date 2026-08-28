#!/usr/bin/env python3
"""Build an additive primary-source macro-model challenge over the frozen 16-axis corpus.

The historical semantic-decomposition artifacts are inputs, never rewritten by this builder. Five
candidate axes are projected over the same 682 library contracts using the same deliberately weak
lexical-discovery posture as the base program: a pattern hit is a review candidate, while no hit is
UNRESOLVED rather than INAPPLICABLE.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from source_model import DEEP_EVIDENCE_CLAIMS, MACRO_CHALLENGES, PRIMARY_SOURCES, PROPOSED_AXES

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
GENERATION = SEM.parent
REGISTRY = GENERATION.parent
AS_OF = "2026-08-28"
EXPECTED_BASE_AXIS_COUNT = 16
EXPECTED_LIBRARY_COUNT = 682
EXPECTED_FAMILY_COUNT = 24


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def searchable_text(library: dict[str, Any]) -> str:
    # Match the base program's conservative discovery surface. Generic boilerplate, evidence refs,
    # refusal templates and vendor/provider names must not manufacture semantic applicability.
    parts = [library.get("name", "")]
    parts.extend(library.get("scope", {}).get("responsibilities", []))
    for operation in library.get("api_contract", {}).get("operations", []):
        parts.extend(
            [operation.get("name", ""), *operation.get("input_types", []), operation.get("output_type", "")]
        )
    for public_type in library.get("api_contract", {}).get("types", []):
        parts.append(public_type.get("name", ""))
    return " ".join(str(x) for x in parts).lower().replace("_", " ").replace("-", " ")


def matches_for_axis(axis: dict[str, Any], text: str) -> list[dict[str, Any]]:
    hits = []
    for facet in axis["facets"]:
        evidence = []
        for pattern in facet["patterns"]:
            if re.search(pattern, text, flags=re.IGNORECASE):
                evidence.append(pattern)
        if evidence:
            hits.append({"facet": facet["facet"], "matched_patterns": evidence})
    return hits


def build() -> dict[str, Any]:
    base_ontology_path = SEM / "semantic-axis-ontology.json"
    base_manifest = json.loads((SEM / "manifest.json").read_text(encoding="utf-8"))
    base_summary = json.loads((SEM / "summary.json").read_text(encoding="utf-8"))
    base_ontology = json.loads(base_ontology_path.read_text(encoding="utf-8"))
    proposals = rows(GENERATION / "library-instance-proposals.jsonl")
    libraries = {row["library_id"]: row for row in rows(REGISTRY / "library-contributions.jsonl")}

    if base_summary["axes"] != EXPECTED_BASE_AXIS_COUNT:
        raise ValueError(f"base axis drift: {base_summary['axes']}")
    if len(proposals) != EXPECTED_LIBRARY_COUNT:
        raise ValueError(f"library proposal drift: {len(proposals)}")
    if len({row['family_id'] for row in proposals}) != EXPECTED_FAMILY_COUNT:
        raise ValueError("family count drift")
    if sha256(base_ontology_path) != base_manifest["files"]["semantic-axis-ontology.json"]["sha256"]:
        raise ValueError("base ontology digest does not match its committed manifest")

    source_by_id = {row["source_id"]: row for row in PRIMARY_SOURCES}
    claim_by_axis: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in DEEP_EVIDENCE_CLAIMS:
        claim_by_axis[claim["supports_axis"]].append(claim)

    signatures = []
    family_axis: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    coverage: dict[str, Counter[str]] = {axis["axis"]: Counter() for axis in PROPOSED_AXES}
    family_hits: dict[str, Counter[str]] = {axis["axis"]: Counter() for axis in PROPOSED_AXES}

    for proposal in proposals:
        library = libraries[proposal["library_ref"]]
        text = searchable_text(library)
        selections = []
        for axis in PROPOSED_AXES:
            hits = matches_for_axis(axis, text)
            status = "EXPLICIT_CANDIDATE_SET_UNRATIFIED" if hits else "UNRESOLVED_OWNER_INPUT_REQUIRED"
            for hit in hits:
                coverage[axis["axis"]][hit["facet"]] += 1
            if hits:
                family_hits[axis["axis"]][proposal["family_id"]] += 1
            selection = {
                "axis": axis["axis"],
                "status": status,
                "candidate_facets": hits,
                "owner_must": "accept, reject, split or replace every candidate; no-hit remains unresolved, never inapplicable",
            }
            selections.append(selection)
            family_axis[(proposal["family_id"], axis["axis"])].append(
                {
                    "library_ref": proposal["library_ref"],
                    "signature_ref": "signature.macro." + proposal["library_ref"].removeprefix("library."),
                    "status": status,
                    "candidate_facets": [hit["facet"] for hit in hits],
                }
            )
        signatures.append(
            {
                "record_kind": "macro_model_new_axis_signature_candidate",
                "signature_id": "signature.macro." + proposal["library_ref"].removeprefix("library."),
                "library_ref": proposal["library_ref"],
                "family_id": proposal["family_id"],
                "source_gap_ref": proposal["source_gap_ref"],
                "axis_selections": selections,
                "status": "DISCOVERY_SIGNATURE_NOT_AUTHORITY",
                "canonical_mutation_allowed": False,
                "completion_claim": False,
            }
        )

    packages = []
    for ordinal, ((family_id, axis_id), members) in enumerate(sorted(family_axis.items()), start=1):
        facets = Counter(facet for member in members for facet in member["candidate_facets"])
        unresolved = [member["library_ref"] for member in members if member["status"].startswith("UNRESOLVED")]
        packages.append(
            {
                "record_kind": "macro_model_family_axis_review_package",
                "work_package_id": f"work.macro-axis.{ordinal:04d}",
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

    axis_deltas = []
    for axis in PROPOSED_AXES:
        selections = [
            selection
            for signature in signatures
            for selection in signature["axis_selections"]
            if selection["axis"] == axis["axis"]
        ]
        evidence_refs = set(axis["evidence_refs"])
        issuers = sorted({source_by_id[ref]["issuer"] for ref in evidence_refs})
        claims = claim_by_axis[axis["axis"]]
        axis_deltas.append(
            {
                "record_kind": "macro_model_axis_delta",
                "axis": axis["axis"],
                "question": axis["question"],
                "phase": axis["phase"],
                "facet_count": len(axis["facets"]),
                "non_collapse_laws": axis["non_collapse"],
                "deep_claim_refs": [claim["claim_id"] for claim in claims],
                "primary_source_refs": sorted(evidence_refs),
                "independent_issuer_count": len(issuers),
                "issuer_names": issuers,
                "candidate_cells": sum(bool(row["candidate_facets"]) for row in selections),
                "unresolved_cells": sum(not row["candidate_facets"] for row in selections),
                "candidate_facet_occurrences": sum(coverage[axis["axis"]].values()),
                "candidate_facet_counts": dict(sorted(coverage[axis["axis"]].items())),
                "families_with_candidate_hits": len(family_hits[axis["axis"]]),
                "model_verdict": axis["model_verdict"],
                "status": "EVIDENCE_BACKED_RESEARCH_AXIS_NOT_RATIFIED",
                "canonical_mutation_allowed": False,
                "completion_claim": False,
            }
        )

    effective_model = {
        "record_kind": "effective_macro_model_research_candidate",
        "model_id": "model.enterprise-data-analytics-semantic-axes.challenge-v1",
        "as_of": AS_OF,
        "base_model": {
            "ontology_id": base_ontology["ontology_id"],
            "axis_count": len(base_ontology["axes"]),
            "axis_ids": [row["axis"] for row in base_ontology["axes"]],
            "sha256": sha256(base_ontology_path),
        },
        "candidate_additions": PROPOSED_AXES,
        "effective_research_axis_count": len(base_ontology["axes"]) + len(PROPOSED_AXES),
        "laws": [
            "This overlay challenges but never rewrites the historical 16-axis candidate corpus.",
            "Source breadth is not authority; only bounded claims with authority limits and negative twins support model changes.",
            "Lexical discovery is a routing signal, never an applicability decision.",
            "A missing lexical signal remains UNRESOLVED rather than INAPPLICABLE.",
            "A proposed axis may be rejected or folded back into existing axes after counterexample review.",
            "No macro-model research result closes semantic-owner, exact-contract, implementation, qualification, provider, physical or vertical-acceptance gates.",
        ],
        "status": "RESEARCH_CHALLENGE_CANDIDATE_NOT_RATIFIED",
        "canonical_mutation_allowed": False,
        "completion_claim": False,
    }

    candidate_cells = sum(
        bool(selection["candidate_facets"])
        for signature in signatures
        for selection in signature["axis_selections"]
    )
    total_new_cells = len(signatures) * len(PROPOSED_AXES)
    summary = {
        "program_id": "program.macro-model-primary-source-challenge.v1",
        "as_of": AS_OF,
        "primary_source_count": len(PRIMARY_SOURCES),
        "primary_source_issuer_count": len({row["issuer"] for row in PRIMARY_SOURCES}),
        "deep_bounded_claim_count": len(DEEP_EVIDENCE_CLAIMS),
        "macro_challenge_count": len(MACRO_CHALLENGES),
        "proposed_axis_count": len(PROPOSED_AXES),
        "rejected_new_axis_challenge_count": sum(row["verdict"].startswith("REJECT") for row in MACRO_CHALLENGES),
        "base_axis_count": len(base_ontology["axes"]),
        "effective_research_axis_count": len(base_ontology["axes"]) + len(PROPOSED_AXES),
        "library_count": len(signatures),
        "family_count": len({row["family_id"] for row in proposals}),
        "base_axis_cells": base_summary["axis_cells"],
        "new_axis_cells": total_new_cells,
        "effective_research_axis_cells": base_summary["axis_cells"] + total_new_cells,
        "new_axis_candidate_cells": candidate_cells,
        "new_axis_unresolved_cells": total_new_cells - candidate_cells,
        "new_family_axis_review_packages": len(packages),
        "canonical_gaps_closed": 0,
        "owner_decisions": 0,
        "completion_claim": False,
        "status": "ITERATION_1_MODELED_RECOMPUTE_REQUIRED",
    }
    return {
        "primary_sources": PRIMARY_SOURCES,
        "deep_claims": DEEP_EVIDENCE_CLAIMS,
        "challenges": MACRO_CHALLENGES,
        "axis_deltas": axis_deltas,
        "signatures": signatures,
        "packages": packages,
        "effective_model": effective_model,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["primary_sources"]),
        "deep-evidence-claims.jsonl": "".join(canonical(row) + "\n" for row in built["deep_claims"]),
        "macro-challenges.jsonl": "".join(canonical(row) + "\n" for row in built["challenges"]),
        "proposed-axis-deltas.jsonl": "".join(canonical(row) + "\n" for row in built["axis_deltas"]),
        "effective-new-axis-signatures.jsonl": "".join(canonical(row) + "\n" for row in built["signatures"]),
        "family-axis-review-packages.jsonl": "".join(canonical(row) + "\n" for row in built["packages"]),
        "effective-macro-model.json": json.dumps(built["effective_model"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    manifest_files = {
        name: {"bytes": len(text.encode("utf-8")), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.macro-model-primary-source-challenge.v1",
            "as_of": AS_OF,
            "files": manifest_files,
            "completion_claim": False,
        },
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    built = outputs()
    for name, text in built.items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = json.loads(built["summary.json"])
    print(
        f"{'CHECK' if args.check else 'BUILD'} PASS macro challenge: "
        f"{summary['primary_source_count']} sources, {summary['library_count']} libraries, "
        f"{summary['base_axis_count']}+{summary['proposed_axis_count']} axes, "
        f"{summary['new_axis_cells']} new cells; zero authority/canonical promotions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
