#!/usr/bin/env python3
"""Factor conservative B07 alias candidates into domain-owner review batches."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ATLAS = HERE.parent
AUTO = HERE / "canonical-reference-auto-alias-candidates.jsonl"
AUTO_SUMMARY = HERE / "canonical-reference-auto-alias-summary.json"
PRACTICES = ATLAS / "universes/analytics_types/candidate-practices.jsonl"
OPERATIONS = ATLAS / "universes/operations/operation-candidates.jsonl"
SOURCES = ATLAS / "universes/source_systems/source-classes.jsonl"
INDUSTRIES = HERE / "foundation/isic-rev5.nodes.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def group_index() -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for row in load_jsonl(PRACTICES):
        result[("analytical_practice", row["practice_id"])] = row["family_id"]
    for row in load_jsonl(OPERATIONS):
        result[("typed_operation", row["operation_id"])] = row["family_id"]
    for row in load_jsonl(SOURCES):
        result[("source_system_class", row["class_id"])] = row["family_id"]
    industry_rows = load_jsonl(INDUSTRIES)
    by_id = {row["record_id"]: row for row in industry_rows}
    for row in industry_rows:
        section_ref = row["record_id"] if row["level"] == "section" else next(
            (ref for ref in row["ancestor_ids"] if by_id[ref]["level"] == "section"),
            row["scheme_edition_id"],
        )
        result[("industry_classification", row["record_id"])] = section_ref
    return result


def outputs() -> dict[str, str]:
    candidates = load_jsonl(AUTO)
    source_summary = json.loads(AUTO_SUMMARY.read_text(encoding="utf-8"))
    groups = group_index()
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        key = (candidate["reference_domain"], candidate["candidate_target_ref"])
        if key not in groups:
            raise ValueError(f"candidate target has no semantic review group: {key}")
        grouped[(candidate["reference_domain"], groups[key])].append(candidate)

    batches: list[dict[str, Any]] = []
    for (domain, group_ref), members in sorted(grouped.items()):
        identity = f"{domain}:{group_ref}"
        batches.append(
            {
                "record_kind": "canonical_reference_semantic_review_batch",
                "batch_id": f"refbatch.{hashlib.sha256(identity.encode()).hexdigest()[:16]}",
                "edition": 1,
                "reference_domain": domain,
                "semantic_review_group_ref": group_ref,
                "candidate_refs": sorted(row["candidate_id"] for row in members),
                "queue_refs": sorted(row["queue_id"] for row in members),
                "target_refs": sorted({row["candidate_target_ref"] for row in members}),
                "candidate_count": len(members),
                "occurrence_count": sum(row["occurrence_count"] for row in members),
                "origin_packs": sorted({pack for row in members for pack in row["origin_packs"]}),
                "review_protocol": [
                    "compare each vertical occurrence's intent, inputs, outputs, assumptions, state, time, authority and refusal laws to the proposed target",
                    "accept exact_alias only when normalization removed representation noise and no semantic qualifier",
                    "otherwise emit narrower_profile, broader_parent, split_required or no_match with a typed reason",
                    "retain canonical owner ratification and compiler substitution as separate downstream gates",
                ],
                "status": "OPEN_MACHINE_FACTORED_SEMANTIC_REVIEW",
                "completion_claim": False,
            }
        )

    domain_batch_counts: dict[str, int] = defaultdict(int)
    for batch in batches:
        domain_batch_counts[batch["reference_domain"]] += 1
    summary = {
        "report_id": "industry_canonical_reference_review_batch_summary",
        "as_of": "2026-08-27",
        "source_candidate_records": len(candidates),
        "source_candidate_occurrences": sum(row["occurrence_count"] for row in candidates),
        "review_batch_count": len(batches),
        "review_batches_by_domain": dict(sorted(domain_batch_counts.items())),
        "represented_candidate_records": sum(row["candidate_count"] for row in batches),
        "represented_candidate_occurrences": sum(row["occurrence_count"] for row in batches),
        "semantic_decisions_created": 0,
        "authority_receipts_created": 0,
        "completion_claim": False,
        "status": "MACHINE_FACTORED_REVIEW_FRONTIER_NOT_SEMANTIC_CLOSURE",
    }
    if summary["source_candidate_records"] != source_summary["machine_exact_alias_candidate_records"]:
        raise ValueError("auto-alias source summary count drift")
    rendered = {
        "canonical-reference-machine-review-batches.jsonl": "".join(canonical(row) + "\n" for row in sorted(batches, key=lambda row: row["batch_id"])),
        "canonical-reference-machine-review-summary.json": canonical(summary) + "\n",
    }
    inputs = (AUTO, AUTO_SUMMARY, PRACTICES, OPERATIONS, SOURCES, INDUSTRIES)
    manifest = {
        "manifest_id": "manifest.industry_canonical_reference_machine_review",
        "as_of": "2026-08-27",
        "inputs": {
            path.relative_to(ATLAS.parent).as_posix(): {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
            for path in inputs
        },
        "outputs": {
            name: {"sha256": hashlib.sha256(data.encode()).hexdigest(), "bytes": len(data.encode())}
            for name, data in sorted(rendered.items())
        },
        "completion_claim": False,
    }
    rendered["canonical-reference-machine-review-manifest.json"] = canonical(manifest) + "\n"
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale: list[str] = []
    generated = outputs()
    for name, data in generated.items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != data:
                stale.append(name)
        else:
            path.write_text(data, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = json.loads(generated["canonical-reference-machine-review-summary.json"])
    print(
        f"{'CHECK' if args.check else 'BUILD'} PASS B07 review batching: "
        f"{summary['source_candidate_records']} candidates / {summary['source_candidate_occurrences']} occurrences "
        f"factor into {summary['review_batch_count']} semantic-review batches; 0 decisions inferred"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
