#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATLAS = HERE.parent


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def norm(value: str, removable_prefixes: tuple[str, ...] = ()) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    for prefix in removable_prefixes:
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def method_forms(value: str) -> set[str]:
    base = norm(value, ("method.",))
    forms = {base}
    words = base.split()
    if words and words[-1] in {"analysis", "method", "methods", "study"}:
        forms.add(" ".join(words[:-1]))
    return {x for x in forms if x}


def strict_forms(value: str, prefixes: tuple[str, ...]) -> set[str]:
    base = norm(value, prefixes)
    return {base} if base else set()


queue = {row["queue_id"]: row for row in load_jsonl(HERE / "canonical-reference-review-queue.jsonl")}
manual_path = HERE / "canonical-reference-adjudications.jsonl"
manual = load_jsonl(manual_path) if manual_path.exists() else []
manual_ids = {row["queue_id"] for row in manual}
practices = load_jsonl(ATLAS / "universes/analytics_types/candidate-practices.jsonl")
operations = load_jsonl(ATLAS / "universes/operations/operation-candidates.jsonl")
sources = load_jsonl(ATLAS / "universes/source_systems/source-classes.jsonl")

targets: dict[str, set[str]] = {
    "analytical_practice": {row["practice_id"] for row in practices},
    "typed_operation": {row["operation_id"] for row in operations},
    "source_system_class": {row["class_id"] for row in sources},
}
indexes: dict[str, dict[str, set[str]]] = {
    "analytical_practice": defaultdict(set),
    "typed_operation": defaultdict(set),
    "source_system_class": defaultdict(set),
}
for row in practices:
    for value in [row["practice_id"], row["name"], *row.get("aliases", [])]:
        for form in method_forms(value):
            indexes["analytical_practice"][form].add(row["practice_id"])
for row in operations:
    for value in (row["operation_id"], row["name"]):
        for form in strict_forms(value, ("operation.", "op.")):
            indexes["typed_operation"][form].add(row["operation_id"])
for row in sources:
    for value in [row["class_id"], row["name"], *row.get("inherited_seed_refs", [])]:
        for form in strict_forms(value, ("source.",)):
            indexes["source_system_class"][form].add(row["class_id"])

rows = load_jsonl(HERE / "canonical-reference-auto-alias-candidates.jsonl")
summary = json.loads((HERE / "canonical-reference-auto-alias-summary.json").read_text(encoding="utf-8"))
assert summary["edition"] == 2
assert len(rows) == len({row["candidate_id"] for row in rows}) == len({row["queue_id"] for row in rows})
domain_counts = Counter()
domain_occurrences = Counter()
for row in rows:
    source = queue[row["queue_id"]]
    domain = row["reference_domain"]
    assert domain in indexes
    assert row["queue_id"] not in manual_ids
    assert source["reference_domain"] == domain
    assert source["raw_ref"] == row["raw_ref"]
    assert source["occurrence_count"] == row["occurrence_count"]
    assert row["candidate_target_ref"] in targets[domain]
    if domain == "analytical_practice":
        form = norm(row["raw_ref"], ("method.",))
    elif domain == "typed_operation":
        form = norm(row["raw_ref"], ("operation.", "op."))
    else:
        form = norm(row["raw_ref"], ("source.",))
    assert row["normalized_form"] == form
    assert indexes[domain][form] == {row["candidate_target_ref"]}, (domain, row["raw_ref"], indexes[domain][form])
    assert row["relation"] == "machine_exact_alias_candidate"
    assert row["status"] == "PROPOSED_NOT_RATIFIED"
    assert row["completion_claim"] is False
    assert row["prohibited_inferences"]
    domain_counts[domain] += 1
    domain_occurrences[domain] += row["occurrence_count"]
assert summary["machine_exact_alias_candidate_records"] == len(rows)
assert summary["machine_exact_alias_candidate_occurrences"] == sum(row["occurrence_count"] for row in rows)
assert summary["candidate_records_by_domain"] == dict(sorted(domain_counts.items()))
assert summary["candidate_occurrences_by_domain"] == dict(sorted(domain_occurrences.items()))
assert summary["raw_review_queue_records"] == len(queue)
assert summary["manual_research_resolutions"] == len(manual)
assert summary["remaining_without_manual_or_machine_exact_candidate"] == len(queue) - len(manual_ids) - len(rows)
assert summary["completion_claim"] is False
print(f"PASS exact canonical-reference candidates: {len(rows)} refs / {sum(r['occurrence_count'] for r in rows)} occurrences; all proposed-not-ratified; by-domain={dict(sorted(domain_counts.items()))}")
