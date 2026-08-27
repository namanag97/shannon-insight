#!/usr/bin/env python3
"""Generate conservative machine-exact canonical-reference candidates.

This does not ratify a mapping. It removes only reversible representation noise or uses
aliases explicitly declared by the canonical record, and it emits a candidate only when
exactly one target survives. No edit distance, embedding, ontology guess or semantic
broadening/narrowing is allowed.
"""
from __future__ import annotations

import hashlib
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


def add_form(index: dict[str, set[str]], form: str, target: str) -> None:
    if form:
        index[form].add(target)


def main() -> int:
    queue = load_jsonl(HERE / "canonical-reference-review-queue.jsonl")
    manual_path = HERE / "canonical-reference-adjudications.jsonl"
    manual = load_jsonl(manual_path) if manual_path.exists() else []
    manual_ids = {row["queue_id"] for row in manual}

    practices = load_jsonl(ATLAS / "universes/analytics_types/candidate-practices.jsonl")
    operations = load_jsonl(ATLAS / "universes/operations/operation-candidates.jsonl")
    source_classes = load_jsonl(ATLAS / "universes/source_systems/source-classes.jsonl")

    indexes: dict[str, dict[str, set[str]]] = {
        "analytical_practice": defaultdict(set),
        "typed_operation": defaultdict(set),
        "source_system_class": defaultdict(set),
    }

    for practice in practices:
        target = practice["practice_id"]
        for value in [practice["practice_id"], practice["name"], *practice.get("aliases", [])]:
            for form in method_forms(value):
                add_form(indexes["analytical_practice"], form, target)

    for operation in operations:
        target = operation["operation_id"]
        for value in (operation["operation_id"], operation["name"]):
            for form in strict_forms(value, ("operation.", "op.")):
                add_form(indexes["typed_operation"], form, target)

    for source_class in source_classes:
        target = source_class["class_id"]
        # `inherited_seed_refs` are explicit compatibility/lineage aliases published by the
        # source-system universe itself. They are stronger than a guessed textual synonym.
        values = [source_class["class_id"], source_class["name"], *source_class.get("inherited_seed_refs", [])]
        for value in values:
            for form in strict_forms(value, ("source.",)):
                add_form(indexes["source_system_class"], form, target)

    rows: list[dict] = []
    for source in queue:
        domain = source["reference_domain"]
        if domain not in indexes or source["queue_id"] in manual_ids:
            continue
        if domain == "analytical_practice":
            form = norm(source["raw_ref"], ("method.",))
        elif domain == "typed_operation":
            form = norm(source["raw_ref"], ("operation.", "op."))
        else:
            form = norm(source["raw_ref"], ("source.",))
        targets = sorted(indexes[domain].get(form, set()))
        if len(targets) != 1:
            continue
        basis = ["unique equality after NFKC/case/punctuation/underscore/whitespace normalization"]
        if domain == "analytical_practice":
            basis.append("method namespace removal and uniquely matching trailing generic method noun are permitted")
        elif domain == "typed_operation":
            basis.append("operation/op namespace removal is permitted; operation verb/noun tokens are otherwise preserved")
        else:
            basis.append("source namespace removal and canonical-record inherited_seed_refs are permitted explicit aliases")
        rows.append({
            "record_kind": "canonical_reference_machine_alias_candidate",
            "candidate_id": "autoalias." + hashlib.sha256(source["queue_id"].encode()).hexdigest()[:16],
            "edition": 2,
            "queue_id": source["queue_id"],
            "reference_domain": domain,
            "raw_ref": source["raw_ref"],
            "normalized_form": form,
            "candidate_target_ref": targets[0],
            "occurrence_count": source["occurrence_count"],
            "origin_packs": source["origin_packs"],
            "relation": "machine_exact_alias_candidate",
            "status": "PROPOSED_NOT_RATIFIED",
            "completion_claim": False,
            "decision_basis": basis,
            "prohibited_inferences": [
                "string similarity beyond exact normalized equality",
                "semantic broadening or narrowing",
                "provider or vertical vocabulary promoted to universal semantics",
                "authority promotion",
                "compiler substitution before ratification",
            ],
        })

    rows.sort(key=lambda row: (row["reference_domain"], row["queue_id"]))
    output = HERE / "canonical-reference-auto-alias-candidates.jsonl"
    output.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    domain_counts = Counter(row["reference_domain"] for row in rows)
    domain_occurrences = Counter()
    for row in rows:
        domain_occurrences[row["reference_domain"]] += row["occurrence_count"]
    summary = {
        "report_id": "industry_canonical_reference_auto_alias_candidates",
        "as_of": "2026-08-27",
        "edition": 2,
        "completion_claim": False,
        "raw_review_queue_records": len(queue),
        "manual_research_resolutions": len(manual),
        "machine_exact_alias_candidate_records": len(rows),
        "machine_exact_alias_candidate_occurrences": sum(row["occurrence_count"] for row in rows),
        "candidate_records_by_domain": dict(sorted(domain_counts.items())),
        "candidate_occurrences_by_domain": dict(sorted(domain_occurrences.items())),
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
