#!/usr/bin/env python3
"""Generate conservative machine-exact analytical-practice alias candidates.

This does not ratify a mapping. It only removes reversible representation noise and
emits uniquely matching candidates for semantic-authority review.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATLAS = HERE.parent


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    if value.startswith("method."):
        value = value[len("method."):]
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def safe_forms(name: str) -> set[str]:
    base = norm(name)
    forms = {base}
    words = base.split()
    # A trailing generic noun does not change method identity when its removal is
    # unique across the canonical registry. Uniqueness is enforced below.
    if words and words[-1] in {"analysis", "method", "methods", "study"}:
        forms.add(" ".join(words[:-1]))
    return {x for x in forms if x}


def main() -> int:
    queue = load_jsonl(HERE / "canonical-reference-review-queue.jsonl")
    manual_path = HERE / "canonical-reference-adjudications.jsonl"
    manual = load_jsonl(manual_path) if manual_path.exists() else []
    manual_ids = {row["queue_id"] for row in manual}
    practices = load_jsonl(ATLAS / "universes/analytics_types/candidate-practices.jsonl")

    by_form: dict[str, set[str]] = defaultdict(set)
    for practice in practices:
        pid = practice["practice_id"]
        for form in safe_forms(practice["name"]):
            by_form[form].add(pid)
        for alias in practice.get("aliases", []):
            for form in safe_forms(alias):
                by_form[form].add(pid)

    rows: list[dict] = []
    for source in queue:
        if source["reference_domain"] != "analytical_practice" or source["queue_id"] in manual_ids:
            continue
        form = norm(source["raw_ref"])
        targets = sorted(by_form.get(form, set()))
        if len(targets) != 1:
            continue
        rows.append({
            "record_kind": "canonical_reference_machine_alias_candidate",
            "candidate_id": "autoalias." + hashlib.sha256(source["queue_id"].encode()).hexdigest()[:16],
            "edition": 1,
            "queue_id": source["queue_id"],
            "reference_domain": "analytical_practice",
            "raw_ref": source["raw_ref"],
            "normalized_form": form,
            "candidate_target_ref": targets[0],
            "occurrence_count": source["occurrence_count"],
            "origin_packs": source["origin_packs"],
            "relation": "machine_exact_alias_candidate",
            "status": "PROPOSED_NOT_RATIFIED",
            "completion_claim": False,
            "decision_basis": [
                "unique equality after NFKC/case/punctuation/whitespace normalization",
                "optional removal of a uniquely matching trailing generic noun only",
            ],
            "prohibited_inferences": [
                "string similarity beyond exact normalized equality",
                "semantic broadening or narrowing",
                "authority promotion",
                "compiler substitution before ratification",
            ],
        })

    rows.sort(key=lambda row: row["queue_id"])
    output = HERE / "canonical-reference-auto-alias-candidates.jsonl"
    output.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    summary = {
        "report_id": "industry_canonical_reference_auto_alias_candidates",
        "as_of": "2026-08-27",
        "completion_claim": False,
        "raw_review_queue_records": len(queue),
        "manual_research_resolutions": len(manual),
        "machine_exact_alias_candidate_records": len(rows),
        "machine_exact_alias_candidate_occurrences": sum(row["occurrence_count"] for row in rows),
        "remaining_without_manual_or_machine_exact_candidate": len(queue) - len(manual_ids) - len(rows),
        "status": "CANDIDATES_ONLY_AUTHORITY_WITHHELD",
    }
    (HERE / "canonical-reference-auto-alias-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
