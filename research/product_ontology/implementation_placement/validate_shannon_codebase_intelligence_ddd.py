#!/usr/bin/env python3
"""Fail-closed validation for the codebase-intelligence application DDD."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_shannon_codebase_intelligence_ddd.py"
DDD = HERE / "shannon-codebase-intelligence-ddd.json"
SUMMARY = HERE / "shannon-codebase-intelligence-ddd-summary.json"
PLACEMENT = HERE / "shannon-python-placement.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def validate_determinism() -> None:
    before = {path: path.read_bytes() for path in (DDD, SUMMARY)}
    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"DDD builder failed:\n{result.stdout}{result.stderr}")
    after = {path: path.read_bytes() for path in (DDD, SUMMARY)}
    for path in before:
        if before[path] != after[path]:
            fail(f"nondeterministic or stale DDD artifact: {path.relative_to(ROOT)}")


def validate() -> dict[str, Any]:
    if not DDD.exists() or not SUMMARY.exists() or not PLACEMENT.exists():
        fail("required generated placement/DDD artifacts are missing")
    model = json.loads(DDD.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    placement = json.loads(PLACEMENT.read_text(encoding="utf-8"))

    if model.get("product_id") != "application_product.software_engineering.codebase_intelligence":
        fail("application product identity drift")
    if model.get("portfolio_disposition") != "RETAIN_EXTERNAL_APPLICATION_PRODUCT_CANDIDATE":
        fail("application product was not kept outside the canonical horizontal platform portfolio")
    if model.get("product_plane") != "application_domain_product":
        fail("application product plane drift")
    if model.get("canonical_platform_product_id") is not None:
        fail("application product was silently collapsed into a platform product")

    contexts = model.get("bounded_contexts", [])
    context_ids = [row.get("context_id") for row in contexts]
    if len(context_ids) < 8 or len(context_ids) != len(set(context_ids)):
        fail("bounded contexts are missing or duplicated")
    context_set = set(context_ids)
    artifact_owners: dict[str, str] = {}
    for context in contexts:
        if not context.get("sovereign_responsibility") or not context.get("negative_charter"):
            fail(f"context boundary incomplete: {context.get('context_id')}")
        for artifact in context.get("owned_artifacts", []):
            previous = artifact_owners.get(artifact)
            if previous is not None and previous != context["context_id"]:
                fail(f"artifact has conflicting owners: {artifact}: {previous}, {context['context_id']}")
            artifact_owners[artifact] = context["context_id"]
    if len(artifact_owners) < 30:
        fail("durable artifact ownership surface is unexpectedly shallow")

    detailed_artifacts = model.get("owned_artifacts", [])
    detailed_names = [row.get("artifact") for row in detailed_artifacts]
    if len(detailed_names) != len(set(detailed_names)):
        fail("detailed artifact identities are duplicated")
    for artifact in detailed_artifacts:
        name = artifact.get("artifact")
        owner = artifact.get("owner_context")
        if owner not in context_set:
            fail(f"detailed artifact has unknown owner: {name}: {owner}")
        if artifact_owners.get(name) != owner:
            fail(f"detailed artifact owner conflicts with context ownership: {name}")
        for field in ("identity", "grain", "time", "equality"):
            if not artifact.get(field):
                fail(f"detailed artifact {name} omits {field}")

    for command in model.get("commands", []):
        if command.get("owner_context") not in context_set:
            fail(f"command has unknown owner: {command.get('command')}")
        if not command.get("outcomes"):
            fail(f"command omits outcomes: {command.get('command')}")
    command_names = [row.get("command") for row in model.get("commands", [])]
    if len(command_names) < 10 or len(command_names) != len(set(command_names)):
        fail("command catalog is missing or duplicated")

    for event in model.get("events", []):
        if event.get("owner_context") not in context_set:
            fail(f"event has unknown owner: {event.get('event')}")
    event_names = [row.get("event") for row in model.get("events", [])]
    if len(event_names) < 15 or len(event_names) != len(set(event_names)):
        fail("event catalog is missing or duplicated")

    state_machine = model.get("state_machine", {})
    if state_machine.get("owner_context") not in context_set:
        fail("state machine has unknown owner")
    states = set(state_machine.get("states", []))
    if not {"COMPLETE", "PARTIAL", "REFUSED", "CANCELLED", "STALE"} <= states:
        fail("state machine omits terminal partial/refusal/invalidation states")
    for source, command, target in state_machine.get("transitions", []):
        source_states = set(source.split("|"))
        if not source_states <= states or target not in states or not command:
            fail(f"invalid transition: {source!r}, {command!r}, {target!r}")

    refusals = model.get("refusals", [])
    precedences = [row.get("precedence") for row in refusals]
    if precedences != list(range(1, len(refusals) + 1)):
        fail("refusal precedence is not total and contiguous")
    refusal_codes = [row.get("code") for row in refusals]
    if len(refusal_codes) != len(set(refusal_codes)):
        fail("refusal codes are duplicated")

    if len(model.get("invariants", [])) < 10:
        fail("invariant surface is incomplete")
    if len(model.get("boundary_falsification_tests", [])) < 6:
        fail("boundary falsification evidence is incomplete")
    if len(model.get("non_collapse_laws", [])) < 10:
        fail("non-collapse law surface is incomplete")
    if not model.get("authority_model") or not model.get("time_model"):
        fail("authority or time model missing")
    if not model.get("concurrency_and_idempotency"):
        fail("concurrency/idempotency model missing")
    if not model.get("published_apis") or not model.get("dependencies"):
        fail("published APIs or dependency seams missing")
    if not model.get("economic_adoption_and_exit_seams"):
        fail("economic/adoption/exit seams missing")

    implementation = model.get("implementation_binding", {})
    if implementation.get("placement_projection_digest") != placement.get("projection_digest"):
        fail("DDD is not bound to the current Python placement projection")
    if implementation.get("status") != "UNQUALIFIED_IMPLEMENTATION_CANDIDATE":
        fail("implementation binding was promoted without qualification")
    compiler = model.get("compiler_and_solution_synthesis_binding", {})
    if compiler.get("global_solution_compiler_stage") is not None:
        fail("application was silently made a global compiler stage")

    readiness = model.get("evidence_and_readiness", {})
    if readiness.get("candidate_ddd_complete") is not True:
        fail("candidate DDD is not structurally complete")
    for forbidden in (
        "semantic_ratified",
        "implementation_qualified",
        "independently_appraised",
        "portable_offer",
        "executed_vertical_acceptance",
        "build_ready",
        "product_ratified",
    ):
        if readiness.get(forbidden) is not False:
            fail(f"DDD illegally promotes {forbidden}")
    if model.get("completion_claim") is not False:
        fail("DDD illegally claims completion")

    stored_digest = model.get("ddd_digest")
    without_digest = dict(model)
    without_digest.pop("ddd_digest", None)
    if stored_digest != canonical_digest(without_digest):
        fail("DDD digest mismatch")
    if summary.get("ddd_digest") != stored_digest:
        fail("DDD summary digest mismatch")
    if summary.get("bounded_context_count") != len(contexts):
        fail("DDD summary context count drift")
    if summary.get("owned_artifact_count") != len(detailed_artifacts):
        fail("DDD summary detailed-artifact count drift")
    for forbidden in (
        "semantic_ratified",
        "implementation_qualified",
        "build_ready",
        "product_ratified",
        "completion_claim",
    ):
        if summary.get(forbidden) is not False:
            fail(f"DDD summary illegally promotes {forbidden}")

    validate_determinism()
    return summary


def main() -> int:
    try:
        summary = validate()
    except Exception as exc:
        print(f"FAIL shannon_codebase_intelligence_ddd: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
