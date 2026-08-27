#!/usr/bin/env python3
"""Materialize the presentation SOTA atlas without inventing missing research records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
ATLAS = ROOT / "docs/research/SOTA-PRESENTATION-CAPABILITY-ATLAS-2026-08-27.md"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}\n"
    if marker not in text:
        raise ValueError(f"atlas missing section: {heading}")
    return text.split(marker, 1)[1].split("\n## ", 1)[0].strip()


def bullets(body: str) -> list[str]:
    return [line[2:].strip() for line in body.splitlines() if line.startswith("- ")]


def render_jsonl(rows: list[dict[str, Any]], identity: str) -> str:
    return "".join(canonical(row) + "\n" for row in sorted(rows, key=lambda row: row[identity]))


def parse_atlas() -> tuple[dict[str, str], dict[str, Any]]:
    text = ATLAS.read_text(encoding="utf-8")
    headline = re.search(
        r"Coverage: (\d+) products; (\d+) sources; (\d+) patterns; (\d+) intents; "
        r"(\d+) specialist families; (\d+) target seams\.",
        text,
    )
    if not headline:
        raise ValueError("atlas coverage declaration is missing")
    declared = {
        "products": int(headline.group(1)),
        "narrative_sources": int(headline.group(2)),
        "visual_patterns": int(headline.group(3)),
        "question_intents": int(headline.group(4)),
        "specialist_families": int(headline.group(5)),
        "target_seams": int(headline.group(6)),
    }

    products: list[dict[str, Any]] = []
    for item in bullets(section(text, "50 SOTA products and observed presentation surface")):
        owner_product, feature_text = item.split(":", 1)
        parts = [part.strip() for part in owner_product.split(" / ")]
        products.append(
            {
                "record_kind": "presentation_product_observation",
                "product_observation_id": f"presentation.product.{slug(owner_product)}",
                "organization": parts[0],
                "product_surface": " / ".join(parts[1:]),
                "observed_feature_labels": [value.strip() for value in feature_text.split(",")],
                "evidence_posture": "NARRATIVE_ATLAS_CLAIM_REQUIRES_SOURCE_LEVEL_BINDING",
                "semantic_authority": False,
                "qualified": False,
            }
        )

    patterns: list[dict[str, Any]] = []
    for item in bullets(section(text, "142 normalized patterns")):
        family, values = item.split(":", 1)
        for value in (part.strip() for part in values.split(",")):
            patterns.append(
                {
                    "record_kind": "presentation_visual_pattern_candidate",
                    "visual_pattern_id": f"presentation.pattern.{slug(value)}",
                    "pattern_name": value,
                    "pattern_family": family.strip(),
                    "status": "UPSTREAM_RESEARCH_CANDIDATE_UNRATIFIED",
                }
            )

    intents: list[dict[str, Any]] = []
    for item in bullets(section(text, "68 question-intent routes")):
        match = re.fullmatch(r"(.+?) -> (.+?) \[(.+)]", item)
        if not match:
            raise ValueError(f"invalid question-intent row: {item}")
        intent, pattern_text, family = match.groups()
        intents.append(
            {
                "record_kind": "presentation_question_intent_candidate",
                "question_intent_id": f"presentation.intent.{slug(intent)}",
                "intent": intent,
                "candidate_pattern_refs": [f"presentation.pattern.{slug(value.strip())}" for value in pattern_text.split("/")],
                "specialization_family": family,
                "binding_status": "CANDIDATE_REQUIRES_TYPED_RESULT_AND_FITNESS_ADJUDICATION",
            }
        )

    specialists: list[dict[str, Any]] = []
    for item in bullets(section(text, "17 typed specialist families")):
        family_id, name = item.split(":", 1)
        specialists.append(
            {
                "record_kind": "presentation_specialist_family_candidate",
                "specialist_family_id": f"presentation.specialist.{slug(family_id)}",
                "family_name": name.strip(),
                "status": "UPSTREAM_RESEARCH_CANDIDATE_UNRATIFIED",
            }
        )

    seam_names = [value.strip() for value in section(text, "50 target seams").split(",") if value.strip()]
    seams = [
        {
            "record_kind": "presentation_target_seam_candidate",
            "target_seam_id": f"presentation.seam.{slug(value)}",
            "seam_name": value,
            "canonical_contract_ref": None,
            "status": "UPSTREAM_RESEARCH_INPUT_REQUIRES_CANONICAL_ADJUDICATION",
            "qualified": False,
            "ratified": False,
        }
        for value in seam_names
    ]
    laws = [
        {
            "record_kind": "presentation_non_collapse_law_candidate",
            "law_id": f"presentation.law.{index:02d}",
            "statement": statement,
            "status": "UPSTREAM_RESEARCH_CANDIDATE_UNRATIFIED",
        }
        for index, statement in enumerate(bullets(section(text, "SOTA laws")), start=1)
    ]

    phases: list[dict[str, Any]] = []
    for item in bullets(section(text, "Adoption sequence")):
        phase_name, description = item.split(":", 1)
        phase_id, name = phase_name.split(" - ", 1)
        phases.append(
            {
                "record_kind": "presentation_adoption_phase_candidate",
                "adoption_phase_id": f"presentation.adoption.{slug(phase_id)}",
                "phase": phase_id,
                "name": name,
                "intent": description.strip(),
                "status": "PROPOSED_SEQUENCE_NOT_EXECUTION_EVIDENCE",
            }
        )

    architecture = re.search(r"## Architecture\n`([^`]+)`", text)
    if not architecture:
        raise ValueError("atlas architecture declaration is missing")
    source_claims = [
        {
            "record_kind": "presentation_atlas_source_claim",
            "source_claim_id": "presentation.claim.coverage",
            "claim": declared,
            "authority_limit": "Headline count from the supplied atlas; not independently source-bound by this projection.",
        },
        {
            "record_kind": "presentation_atlas_source_claim",
            "source_claim_id": "presentation.claim.evidence_anchors",
            "claim": section(text, "Evidence anchors"),
            "authority_limit": "Narrative list of organizations and research anchors; not 82 machine-readable evidence records.",
        },
    ]

    actual = {
        "products": len(products),
        "visual_patterns": len(patterns),
        "question_intents": len(intents),
        "specialist_families": len(specialists),
        "target_seams": len(seams),
    }
    for key, count in actual.items():
        if count != declared[key]:
            raise ValueError(f"atlas {key} count mismatch: declared {declared[key]}, parsed {count}")
    pattern_ids = {row["visual_pattern_id"] for row in patterns}
    unknown_patterns = sorted(
        ref for row in intents for ref in row["candidate_pattern_refs"] if ref not in pattern_ids
    )
    if unknown_patterns:
        raise ValueError(f"question intents reference unknown patterns: {unknown_patterns}")

    summary = {
        "record_kind": "presentation_sota_atlas_projection_summary",
        "as_of": "2026-08-27",
        "source_ref": ATLAS.relative_to(ROOT).as_posix(),
        "architecture_candidate": architecture.group(1),
        "declared_counts": declared,
        "machine_readable_counts": actual,
        "machine_readable_evidence_source_count": 0,
        "evidence_limitation": "The atlas declares 82 sources but does not contain 82 exact source records or URLs; source-level evidence remains open.",
        "integration_posture": "UPSTREAM_RESEARCH_INPUT_ONLY",
        "qualified_provider_count": 0,
        "ratified_contract_count": 0,
        "completion_claim": False,
    }
    outputs = {
        "products.jsonl": render_jsonl(products, "product_observation_id"),
        "visual-patterns.jsonl": render_jsonl(patterns, "visual_pattern_id"),
        "question-intents.jsonl": render_jsonl(intents, "question_intent_id"),
        "specialist-families.jsonl": render_jsonl(specialists, "specialist_family_id"),
        "target-seams.jsonl": render_jsonl(seams, "target_seam_id"),
        "non-collapse-laws.jsonl": render_jsonl(laws, "law_id"),
        "adoption-phases.jsonl": render_jsonl(phases, "adoption_phase_id"),
        "source-claims.jsonl": render_jsonl(source_claims, "source_claim_id"),
        "summary.json": canonical(summary) + "\n",
    }
    manifest = {
        "manifest_id": "manifest.presentation_sota_atlas_projection",
        "as_of": "2026-08-27",
        "source": {
            "path": ATLAS.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(ATLAS.read_bytes()).hexdigest(),
            "bytes": ATLAS.stat().st_size,
        },
        "outputs": {
            name: {"sha256": hashlib.sha256(data.encode()).hexdigest(), "bytes": len(data.encode())}
            for name, data in sorted(outputs.items())
        },
        "completion_claim": False,
    }
    outputs["manifest.json"] = canonical(manifest) + "\n"
    return outputs, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, summary = parse_atlas()
    stale: list[str] = []
    for name, data in outputs.items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != data:
                stale.append(name)
        else:
            path.write_text(data, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    counts = summary["machine_readable_counts"]
    print(
        f"{'CHECK' if args.check else 'BUILD'} PASS presentation SOTA atlas: "
        f"{counts['products']} product observations; {counts['visual_patterns']} patterns; "
        f"{counts['question_intents']} intents; {counts['target_seams']} upstream seams; "
        "0 fabricated evidence sources or authority promotions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
