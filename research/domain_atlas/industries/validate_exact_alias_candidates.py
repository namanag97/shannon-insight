#!/usr/bin/env python3
from __future__ import annotations

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
    if words and words[-1] in {"analysis", "method", "methods", "study"}:
        forms.add(" ".join(words[:-1]))
    return {x for x in forms if x}


queue = {row["queue_id"]: row for row in load_jsonl(HERE / "canonical-reference-review-queue.jsonl")}
manual_path = HERE / "canonical-reference-adjudications.jsonl"
manual = load_jsonl(manual_path) if manual_path.exists() else []
manual_ids = {row["queue_id"] for row in manual}
practices = load_jsonl(ATLAS / "universes/analytics_types/candidate-practices.jsonl")
practice_by_id = {row["practice_id"]: row for row in practices}
by_form: dict[str, set[str]] = defaultdict(set)
for practice in practices:
    for form in safe_forms(practice["name"]):
        by_form[form].add(practice["practice_id"])
    for alias in practice.get("aliases", []):
        for form in safe_forms(alias):
            by_form[form].add(practice["practice_id"])

rows = load_jsonl(HERE / "canonical-reference-auto-alias-candidates.jsonl")
summary = json.loads((HERE / "canonical-reference-auto-alias-summary.json").read_text(encoding="utf-8"))
assert len(rows) == len({row["candidate_id"] for row in rows}) == len({row["queue_id"] for row in rows})
for row in rows:
    source = queue[row["queue_id"]]
    assert row["queue_id"] not in manual_ids
    assert source["reference_domain"] == row["reference_domain"] == "analytical_practice"
    assert source["raw_ref"] == row["raw_ref"]
    assert source["occurrence_count"] == row["occurrence_count"]
    assert row["candidate_target_ref"] in practice_by_id
    form = norm(row["raw_ref"])
    assert row["normalized_form"] == form
    assert by_form[form] == {row["candidate_target_ref"]}, (row["raw_ref"], by_form[form])
    assert row["relation"] == "machine_exact_alias_candidate"
    assert row["status"] == "PROPOSED_NOT_RATIFIED"
    assert row["completion_claim"] is False
    assert row["prohibited_inferences"]
assert summary["machine_exact_alias_candidate_records"] == len(rows)
assert summary["machine_exact_alias_candidate_occurrences"] == sum(row["occurrence_count"] for row in rows)
assert summary["raw_review_queue_records"] == len(queue)
assert summary["manual_research_resolutions"] == len(manual)
assert summary["remaining_without_manual_or_machine_exact_candidate"] == len(queue) - len(manual_ids) - len(rows)
assert summary["completion_claim"] is False
print(f"PASS exact alias candidates: {len(rows)} distinct refs / {sum(r['occurrence_count'] for r in rows)} occurrences; all remain proposed-not-ratified")
