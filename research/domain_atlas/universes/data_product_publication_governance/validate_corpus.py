#!/usr/bin/env python3
"""Validate exact data-product publication contracts and ownership boundaries."""

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
    assert len(data["sources.jsonl"]) == 19 and all(x["url"].startswith("https://") for x in data["sources.jsonl"])
    contexts = {x["context_id"] for x in data["bounded-contexts.jsonl"]}
    assert contexts == {"context.data_product_publication.definition", "context.data_product_publication.readiness", "context.data_product_publication.lifecycle"}
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 42 and all(x["default"] is None and x["default_law"] == "forbidden" for x in decisions)
    libs = data["library-contracts.jsonl"]
    assert len(libs) == 7 and len({x["library_id"] for x in libs}) == 7
    decision_ids = {x["decision_id"] for x in decisions}
    for lib in libs:
        assert len(lib["public_types"]) >= 19 and len(lib["operations"]) == 4
        assert set(lib["operation_refs"]) == {o["operation_ref"] for o in lib["operations"]}
        assert set(lib["decision_refs"]) <= decision_ids and len(lib["decision_refs"]) == 6
        assert all(o["input_types"] and o["output_type"].startswith("Result<") and o["purity"] == "pure" for o in lib["operations"])
        assert not ({"source facts, datasets, schemas, contracts or distributions", "independent assurance or universal fitness", "catalog ranking or marketplace offer", "access approval, provisioning or consumption"} - set(lib["must_not_own"]))
    owners = {x["library_id"]: x["semantic_owner_context"] for x in libs}
    for suffix in ["product_edition", "port_assembly", "accountability_binding"]:
        assert owners[f"library.data_product_publication.{suffix}"] == "context.data_product_publication.definition"
    assert owners["library.data_product_publication.readiness_evidence"] == "context.data_product_publication.readiness"
    for suffix in ["publication_protocol", "consumer_change", "recall_exit"]:
        assert owners[f"library.data_product_publication.{suffix}"] == "context.data_product_publication.lifecycle"
    boundaries = {x["library_id"]: x["effect_boundary"] for x in libs}
    assert boundaries["library.data_product_publication.port_assembly"] == "pure_no_io"
    assert boundaries["library.data_product_publication.readiness_evidence"] == "pure_no_io"
    for suffix in ["product_edition", "accountability_binding", "publication_protocol", "consumer_change", "recall_exit"]:
        assert boundaries[f"library.data_product_publication.{suffix}"] == "pure_effect_intents"
    laws = " ".join(l for lib in libs for l in lib["laws"]).lower()
    for phrase in ["data product, product series", "product port, contract, schema", "product owner, semantic owner", "cannot manufacture independent appraisal", "readiness, approval, publication intent", "delivered notification does not", "package completeness, byte integrity"]:
        assert phrase in laws, phrase
    compiler = data["compiler-contracts.jsonl"]
    offers = [x for x in compiler if x["record_kind"] == "capability_offer"]
    assert len(compiler) == 21 and len(offers) == 7
    assert all(not x["portable"] and not x["selectable"] and x["qualified_implementation_count"] == 0 for x in offers)
    assert len(data["negative-twins.jsonl"]) == 20 and manifest["completion_claim"] is False
    print("VALIDATION PASS data product publication: 1 product projection, 3 contexts, 7 exact libraries, 42 no-default decisions, 0 qualified offers")


if __name__ == "__main__":
    main()
