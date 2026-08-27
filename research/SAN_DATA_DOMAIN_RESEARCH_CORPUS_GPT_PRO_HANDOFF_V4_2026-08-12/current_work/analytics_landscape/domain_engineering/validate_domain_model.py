#!/usr/bin/env python3
"""Validate referential and minimum semantic integrity of the platform domain model."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "data_platform_domain_model.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_ids(items: list[dict], label: str) -> set[str]:
    ids = [item.get("id") for item in items]
    require(all(isinstance(item_id, str) and item_id for item_id in ids), f"{label}: missing id")
    require(len(ids) == len(set(ids)), f"{label}: duplicate id")
    return set(ids)


def validate() -> dict:
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))

    require(model.get("model_id") == "data-platform-domain-model", "unexpected model_id")
    require(bool(model.get("domain_vision")), "domain vision is required")
    require(bool(model.get("sovereign_question")), "sovereign question is required")
    require(bool(model.get("negative_charter")), "negative charter is required")

    subdomains = model.get("strategic_subdomains", [])
    contexts = model.get("bounded_contexts", [])
    relationships = model.get("context_relationships", [])
    laws = model.get("platform_constitution", [])

    subdomain_ids = unique_ids(subdomains, "strategic_subdomains")
    context_ids = unique_ids(contexts, "bounded_contexts")
    law_ids = unique_ids(laws, "platform_constitution")

    classifications = {item.get("classification") for item in subdomains}
    require(classifications == {"core", "supporting", "generic"}, "subdomain classifications incomplete")

    required_context_fields = (
        "name",
        "question",
        "owns",
        "excludes",
        "aggregate_roots",
        "commands",
        "events",
        "refusals",
        "laws",
    )
    for context in contexts:
        context_id = context["id"]
        require(context.get("subdomain") in subdomain_ids, f"{context_id}: unknown subdomain")
        for field in required_context_fields:
            require(bool(context.get(field)), f"{context_id}: {field} is required")
        require(set(context["owns"]).isdisjoint(context["excludes"]), f"{context_id}: owns/excludes overlap")

    relationship_keys: set[tuple[str, str, str]] = set()
    allowed_relationships = {
        "anti-corruption-layer",
        "conformist",
        "customer-supplier",
        "open-host-service",
        "partnership",
        "published-language",
        "separate-ways",
        "shared-kernel",
    }
    for relationship in relationships:
        upstream = relationship.get("upstream")
        downstream = relationship.get("downstream")
        relation = relationship.get("relationship")
        require(upstream in context_ids, f"relationship has unknown upstream: {upstream}")
        require(downstream in context_ids, f"relationship has unknown downstream: {downstream}")
        require(upstream != downstream, f"self relationship is invalid: {upstream}")
        require(relation in allowed_relationships, f"unknown relationship type: {relation}")
        require(bool(relationship.get("contract")), "relationship contract is required")
        key = (upstream, downstream, relationship["contract"])
        require(key not in relationship_keys, f"duplicate relationship contract: {key}")
        relationship_keys.add(key)

    require(len(model.get("canonical_flow", [])) >= 10, "canonical flow is incomplete")
    require(len(model.get("time_model", [])) >= 10, "time model is incomplete")
    require(len(law_ids) >= 15, "platform constitution is too small")

    rust_application = model.get("rust_application", {})
    for field in ("direct", "declarative_ir_required", "runtime_only", "evidence_only", "forbidden_equivalences"):
        require(bool(rust_application.get(field)), f"rust_application.{field} is required")

    return {
        "valid": True,
        "strategic_subdomains": len(subdomains),
        "bounded_contexts": len(contexts),
        "context_relationships": len(relationships),
        "platform_laws": len(laws),
        "time_axes": len(model["time_model"]),
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
