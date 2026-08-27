#!/usr/bin/env python3
"""Validate exact data-use-policy contracts and ownership boundaries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_corpus


ROOT = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    return [json.loads(x) for x in (ROOT / name).read_text(encoding="utf-8").splitlines() if x.strip()]


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    data = {name: load(name) for name in build_corpus.FILES}
    for name, rows in data.items():
        assert manifest["files"][name]["records"] == len(rows)
        assert manifest["files"][name]["sha256"] == hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert len(data["sources.jsonl"]) == 17 and all(x["url"].startswith("https://") for x in data["sources.jsonl"])
    contexts = {x["context_id"] for x in data["bounded-contexts.jsonl"]}
    assert contexts == {"context.data_use_policy.administration", "context.data_use_policy.decision", "context.data_use_policy.usage"}
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 36 and all(x["default"] is None and x["default_law"] == "forbidden" for x in decisions)
    libs = data["library-contracts.jsonl"]
    assert len(libs) == 6 and len({x["library_id"] for x in libs}) == 6
    decision_ids = {x["decision_id"] for x in decisions}
    for lib in libs:
        assert len(lib["public_types"]) >= 18 and len(lib["operations"]) == 4
        assert set(lib["operation_refs"]) == {o["operation_ref"] for o in lib["operations"]}
        assert set(lib["decision_refs"]) <= decision_ids and len(lib["decision_refs"]) == 6
        assert all(o["input_types"] and o["output_type"].startswith("Result<") and o["purity"] == "pure" for o in lib["operations"])
        assert not ({"principal identity or authentication", "resource, data-category, purpose, consent or legal-basis truth", "enforcement execution or business effect"} - set(lib["must_not_own"]))
    owners = {x["library_id"]: x["semantic_owner_context"] for x in libs}
    assert owners["library.data_use_policy.policy_edition"] == "context.data_use_policy.administration"
    assert owners["library.data_use_policy.rule_combination"] == "context.data_use_policy.administration"
    assert owners["library.data_use_policy.request_context"] == "context.data_use_policy.decision"
    assert owners["library.data_use_policy.decision_evaluation"] == "context.data_use_policy.decision"
    assert owners["library.data_use_policy.obligation_protocol"] == "context.data_use_policy.usage"
    assert owners["library.data_use_policy.decision_evidence"] == "context.data_use_policy.usage"
    boundaries = {x["library_id"]: x["effect_boundary"] for x in libs}
    assert boundaries["library.data_use_policy.request_context"] == "pure_no_io"
    assert boundaries["library.data_use_policy.rule_combination"] == "pure_no_io"
    assert boundaries["library.data_use_policy.decision_evaluation"] == "pure_no_io"
    for suffix in ["policy_edition", "obligation_protocol", "decision_evidence"]:
        assert boundaries[f"library.data_use_policy.{suffix}"] == "pure_effect_intents"
    laws = " ".join(l for lib in libs for l in lib["laws"]).lower()
    for phrase in ["syntax validity, schema validity", "consumes externally owned", "permit, deny, not-applicable and indeterminate", "decision is not authentication", "prior permit does not", "obligation expression, returned obligation", "decision occurrence, decision evidence record"]:
        assert phrase in laws, phrase
    compiler = data["compiler-contracts.jsonl"]
    offers = [x for x in compiler if x["record_kind"] == "capability_offer"]
    assert len(compiler) == 18 and len(offers) == 6
    assert all(not x["portable"] and not x["selectable"] and x["qualified_implementation_count"] == 0 for x in offers)
    assert len(data["negative-twins.jsonl"]) == 18 and manifest["completion_claim"] is False
    print("VALIDATION PASS data use policy: 1 product projection, 3 contexts, 6 exact libraries, 36 no-default decisions, 0 qualified offers")


if __name__ == "__main__":
    main()
