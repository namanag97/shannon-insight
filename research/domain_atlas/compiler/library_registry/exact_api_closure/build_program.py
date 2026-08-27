#!/usr/bin/env python3
"""Build the deterministic exact-API closure queue for every placeholder library contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parent
WORKSPACE = HERE.parents[4]
QUALIFICATION = WORKSPACE / "research/product_ontology/qualification_program/library-qualification-subjects.jsonl"
VERTICALS = WORKSPACE / "research/product_ontology/composition_pilots/deterministic_verticals/vertical-compositions.jsonl"
AS_OF = "2026-08-26"


FAMILY_BY_NAMESPACE = {
    "csp": "shared_semantic_foundations",
    "method_kernels": "analytical_method_kernels",
    "operations_research": "operations_research",
    "predictive": "predictive_analytics",
    "persistence": "persistence_lakehouse",
    "qor": "quality_reconciliation",
    "runtime-resource": "runtime_resource_control",
    "candidate": "candidate_data_shapes",
    "lpe": "lineage_provenance_evidence",
    "qck": "query_compilation_execution",
    "mae": "optional_model_agent_extensions",
    "cbv": "consumption_bi_visualization",
    "pipeline": "pipeline_dataflow",
    "spt": "security_privacy_trust",
    "smf": "semantic_metrics_formulas",
    "platform-commercial-support": "platform_commercial_support",
    "msg": "messaging_coordination",
    "gmo": "governance_metadata_ontology",
    "forecast": "forecasting_lifecycle",
    "experiment": "experimentation_lifecycle",
    "cp": "connector_protocol",
    "application": "application_behavior",
}

GEOSPATIAL_NAMESPACES = {
    "geocode", "pointcloud", "spatial_layer", "spatial_network", "spatial_project",
    "spatial_result", "spatial_workflow", "terrain", "trajectory",
}

FAMILY_EVIDENCE_PROGRAM = {
    "shared_semantic_foundations": ["formal identity, time, quantity, authority and decision specifications", "algebraic laws and negative twins", "two independent semantic implementations"],
    "analytical_method_kernels": ["original method papers or standards", "reference algorithms and applicability domains", "benchmark, property and differential oracles"],
    "operations_research": ["formal optimization, simulation and queueing literature", "solver-independent model and result contracts", "independent solution and bound checkers"],
    "predictive_analytics": ["statistical learning and model-format specifications", "study, feature, target and evaluation contracts", "drift, calibration and lifecycle evidence"],
    "persistence_lakehouse": ["table-format, transaction and storage specifications", "failure, recovery and concurrency protocols", "format and engine interoperability suites"],
    "representation_codec": ["binary, columnar, compression and container specifications", "loss, canonicalization and integrity laws", "cross-implementation byte fixtures and fuzzing"],
    "quality_reconciliation": ["quality measurement and reconciliation standards", "evidence, sampling, correction and authority lifecycles", "negative twins separating detection, judgment and effect"],
    "runtime_resource_control": ["runtime, scheduling and resource-control specifications", "state, cancellation, quota and admission models", "race, overload and failure-injection oracles"],
    "candidate_data_shapes": ["domain standards for each data shape", "boundary and owner adjudication before signatures", "round-trip, loss and invalid-operation fixtures"],
    "lineage_provenance_evidence": ["PROV, OpenLineage, evidence and preservation standards", "claim, custody, disclosure and retention authority", "tamper, retraction and incomplete-coverage twins"],
    "query_compilation_execution": ["relational algebra and query IR specifications", "optimizer, execution and memory/spill contracts", "semantic differential and benchmark oracles"],
    "optional_model_agent_extensions": ["provider protocol specifications", "typed untrusted proposal boundaries", "removal, retry, budget and non-authority tests"],
    "consumption_bi_visualization": ["visualization, accessibility and internationalization standards", "presentation and interaction state models", "rendering, embedding and policy-projection tests"],
    "pipeline_dataflow": ["dataflow, streaming and orchestration specifications", "logical/effect/recovery contract separation", "replay, failure and end-to-end composition oracles"],
    "security_privacy_trust": ["security, privacy and attestation standards", "purpose, authority, revocation and retention models", "abuse, confused-deputy and fail-closed tests"],
    "semantic_metrics_formulas": ["measurement, dimensional and formula semantics", "grain, unit, uncertainty and temporal laws", "cross-engine calculation and aggregation oracles"],
    "platform_commercial_support": ["commercial, metering and service-management standards", "money, contract and support authority boundaries", "provider adapter and reconciliation tests"],
    "messaging_coordination": ["messaging protocol and delivery specifications", "ordering, idempotency, inbox/outbox and bridge contracts", "duplicate, loss, partition and recovery tests"],
    "governance_metadata_ontology": ["catalog, ontology, policy and governance standards", "ownership and published-language contracts", "federation, versioning and policy-evaluation tests"],
    "forecasting_lifecycle": ["forecasting method and evaluation literature", "edition, selection, override and publication lifecycles", "backtest, leakage and override-authority tests"],
    "experimentation_lifecycle": ["experimental-design and causal-inference standards", "assignment, integrity, analysis-binding and conclusion lifecycles", "randomization, interference and multiplicity tests"],
    "geospatial_analytics": ["OGC and geospatial format/service standards", "CRS, topology, accuracy and workflow contracts", "coordinate, topology and accuracy differential tests"],
    "connector_protocol": ["protocol and connector specifications", "codec, transport, adapter and conformance boundaries", "wire fixtures, fault injection and interoperability tests"],
    "application_behavior": ["application interaction, state, workflow, event, projection and effect-handoff specifications", "explicit authority, time, resource, refusal and receipt boundaries", "command/event, version conflict, retry/compensation, lag, effect-unknown and replay tests"],
}

# These are discovery seeds, not adopted semantic authority.  A batch owner must
# extract bounded claims, editions, conflicts and counterexamples before a seed
# may support an exact contract.
FAMILY_PRIMARY_EVIDENCE_SEEDS = {
    "pipeline_dataflow": [
        {
            "title": "OpenLineage Object Model 1.52.0",
            "uri": "https://openlineage.io/docs/spec/object-model/",
            "claim_scope": "separate design metadata, run observations, jobs, runs, datasets, versions and extensible facets",
        },
        {
            "title": "Apache Iceberg Branching and Tagging 1.11.0",
            "uri": "https://iceberg.apache.org/docs/latest/branching/",
            "claim_scope": "snapshot history and write-audit-publish through isolated audit branches, validation and explicit fast-forward publication",
        },
        {
            "title": "Apache Flink Checkpoints vs. Savepoints 2.3",
            "uri": "https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/checkpoints_vs_savepoints/",
            "claim_scope": "distinguish system-owned failure recovery checkpoints from user-owned portable operational savepoints",
        },
    ],
    "lineage_provenance_evidence": [
        {
            "title": "W3C PROV Data Model",
            "uri": "https://www.w3.org/TR/prov-dm/",
            "claim_scope": "domain-agnostic entities, activities, agents, derivations, responsibility, bundles, collections and extensibility",
        },
        {
            "title": "W3C Constraints of the PROV Data Model",
            "uri": "https://www.w3.org/TR/prov-constraints/",
            "claim_scope": "normalization, validity, equivalence, uniqueness, typing, impossibility and temporal ordering constraints",
        },
        {
            "title": "IETF RFC 9334 RATS Architecture",
            "uri": "https://www.rfc-editor.org/rfc/rfc9334.html",
            "claim_scope": "separate claims, evidence, endorsements, reference values, appraisal policies, appraisal results and relying-party authorization",
        },
    ],
    "quality_reconciliation": [
        {
            "title": "W3C Data Quality Vocabulary",
            "uri": "https://www.w3.org/TR/vocab-dqv/",
            "claim_scope": "separate quality dimensions, metrics, measurements, policies, annotations, certificates, feedback and derivations",
        },
        {
            "title": "OpenLineage Object Model 1.52.0",
            "uri": "https://openlineage.io/docs/spec/object-model/",
            "claim_scope": "runtime dataset quality metrics and assertions as facets rather than dataset identity or publication authority",
        },
        {
            "title": "W3C Constraints of the PROV Data Model",
            "uri": "https://www.w3.org/TR/prov-constraints/",
            "claim_scope": "terminating validation, normal forms, event-order consistency and implementation-independent equivalence",
        },
    ],
    "shared_semantic_foundations": [
        {
            "title": "IETF RFC 9562 UUIDs",
            "uri": "https://www.rfc-editor.org/rfc/rfc9562.html",
            "claim_scope": "UUID formats, versions, opacity, sorting, generation and global/local uniqueness tradeoffs",
        },
        {
            "title": "IETF RFC 3986 URI Generic Syntax",
            "uri": "https://www.rfc-editor.org/rfc/rfc3986.html",
            "claim_scope": "identifier syntax, resolution, normalization and equivalence boundaries",
        },
        {
            "title": "IETF RFC 3339 Date and Time on the Internet",
            "uri": "https://www.rfc-editor.org/rfc/rfc3339.html",
            "claim_scope": "timestamp representation, offsets, leap seconds, ordering and interoperability constraints",
        },
        {
            "title": "W3C JSON-LD 1.1",
            "uri": "https://www.w3.org/TR/json-ld11/",
            "claim_scope": "linked identifiers, contexts, expansion, compaction and graph representation without conflating syntax with domain equality",
        },
    ],
    "runtime_resource_control": [
        {
            "title": "Apache Flink Checkpoints vs. Savepoints 2.3",
            "uri": "https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/checkpoints_vs_savepoints/",
            "claim_scope": "ownership, lifecycle, portability, restore speed and compatibility differences among state snapshots",
        },
        {
            "title": "IETF RFC 9334 RATS Architecture",
            "uri": "https://www.rfc-editor.org/rfc/rfc9334.html",
            "claim_scope": "runtime evidence freshness, appraisal, trust roles and authorization separation",
        },
    ],
    "application_behavior": [
        {
            "title": "OpenAPI Specification 3.2.0",
            "uri": "https://spec.openapis.org/oas/v3.2.0.html",
            "claim_scope": "language-agnostic HTTP interface description; it does not establish domain command meaning or effect authority",
        },
        {
            "title": "CloudEvents Specification 1.0.x",
            "uri": "https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md",
            "claim_scope": "interoperable event context attributes and serialization envelope; it does not define event processing guarantees",
        },
        {
            "title": "W3C State Chart XML (SCXML) 1.0",
            "uri": "https://www.w3.org/TR/scxml/",
            "claim_scope": "event-driven state configuration and transition notation; it does not prove application ownership or persistence",
        },
        {
            "title": "Sagas",
            "uri": "https://doi.org/10.1145/38713.38742",
            "claim_scope": "long-lived transaction decomposition and explicit compensating transactions; it does not make compensation rollback",
        },
        {
            "title": "W3C PROV Data Model",
            "uri": "https://www.w3.org/TR/prov-dm/Overview.html",
            "claim_scope": "provenance relations among entities, activities and agents; it does not prove truth, authority or business acceptance",
        },
    ],
}


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def placeholder_dimensions(library: dict[str, Any]) -> list[str]:
    dimensions: list[str] = []
    api = library["api_contract"]
    if any(row["origin"] != "source_projection" for row in api["types"]):
        dimensions.append("types")
    if any(row["origin"] != "source_projection" for row in api["traits"]):
        dimensions.append("traits")
    if any(row["origin"] != "source_projection" for row in api["operations"]):
        dimensions.append("operations")
    return dimensions


def build_records() -> list[dict[str, Any]]:
    libraries = rows(REGISTRY / "library-contributions.jsonl")
    dependencies = rows(REGISTRY / "dependency-edges.jsonl")
    kernels = rows(REGISTRY / "kernel-to-library.jsonl")
    qualification = rows(QUALIFICATION)
    verticals = rows(VERTICALS)

    product_refs: dict[str, set[str]] = defaultdict(set)
    for subject in qualification:
        for ref in subject["compiler_projection"]["concrete_library_refs"]:
            product_refs[ref].add(subject["product_ref"])

    vertical_refs: dict[str, set[str]] = defaultdict(set)
    for vertical in verticals:
        for ref in vertical["required_library_refs"]:
            vertical_refs[ref].add(vertical["composition_id"])

    incoming: Counter[str] = Counter(edge["to_ref"] for edge in dependencies)
    outgoing: Counter[str] = Counter(edge["from_ref"] for edge in dependencies)
    kernel_counts: Counter[str] = Counter(link["library_ref"] for link in kernels)

    result: list[dict[str, Any]] = []
    for library in libraries:
        exact_gap = next((gap for gap in library["gaps"] if gap["gap_kind"] == "exact_api_contract_missing"), None)
        if exact_gap is None:
            continue
        ref = library["library_id"]
        products = sorted(product_refs[ref])
        vertical_uses = sorted(vertical_refs[ref])
        effect_boundary = library["effects"]["boundary"]
        effect_risk = effect_boundary != "pure_no_io"
        score = (
            100 * len(products)
            + 30 * len(vertical_uses)
            + 5 * incoming[ref]
            + 2 * outgoing[ref]
            + 3 * kernel_counts[ref]
            + (15 if effect_risk else 0)
        )
        if products and vertical_uses:
            band = "P0_PRODUCT_AND_VERTICAL"
        elif products:
            band = "P1_PRODUCT"
        elif vertical_uses or incoming[ref] or kernel_counts[ref]:
            band = "P2_SHARED_GRAPH"
        else:
            band = "P3_REMAINDER"
        result.append({
            "record_kind": "exact_api_closure_item",
            "closure_id": "closure.exact-api." + ref.removeprefix("library."),
            "edition": 1,
            "as_of": AS_OF,
            "library_ref": ref,
            "semantic_owner_refs": [owner["context_ref"] for owner in library["semantic_owners"]],
            "library_class": library["library_class"],
            "effect_boundary": effect_boundary,
            "priority_band": band,
            "priority_score": score,
            "product_refs": products,
            "vertical_composition_refs": vertical_uses,
            "incoming_dependency_count": incoming[ref],
            "outgoing_dependency_count": outgoing[ref],
            "kernel_count": kernel_counts[ref],
            "placeholder_dimensions": placeholder_dimensions(library),
            "source_gap_ref": exact_gap["gap_id"],
            "required_source_contract": [
                "exact public carrier types and equality/identity rules",
                "exact public traits and object-safety posture",
                "typed operation signatures with total outcomes",
                "typed refusal catalog and precedence",
                "purity or explicit effect-intent/receipt boundary",
                "configuration and decision editions with no hidden defaults",
                "laws, invariants, finite-resource contracts and negative twins",
                "compatibility, migration and evidence invalidation rules",
                "property, model, fuzz, fixture and differential conformance oracles",
                "bounded primary evidence supporting each semantic decision",
            ],
            "closure_law": "The gap closes only when every placeholder dimension is replaced by an owner-published source projection and the central normalizer emits no exact_api_contract_missing gap.",
            "prohibited_shortcuts": [
                "rename a generated placeholder",
                "copy a vendor SDK surface",
                "infer signatures from product marketing",
                "remove the gap without exact source fields",
                "use an LLM or agent output as semantic authority",
            ],
            "status": "OPEN_OWNER_CONTRACT_REQUIRED",
        })
    return sorted(result, key=lambda row: (-row["priority_score"], row["library_ref"]))


def research_family(library_ref: str) -> str:
    namespace = library_ref.split(".")[1]
    if namespace.startswith("san_") or namespace in {"san_wire_schema", "san_carrier"}:
        return "representation_codec"
    if namespace in GEOSPATIAL_NAMESPACES:
        return "geospatial_analytics"
    return FAMILY_BY_NAMESPACE.get(namespace, "unclassified_refuse")


def research_lane(row: dict[str, Any]) -> str:
    if research_family(row["library_ref"]) == "candidate_data_shapes":
        return "boundary_first"
    if row["library_class"] in {"semantic_pure", "policy_pure"} and row["effect_boundary"] == "pure_no_io":
        return "semantic_contract"
    if row["library_class"] in {"algorithm_pure", "test_oracle"} and row["effect_boundary"] == "pure_no_io":
        return "algorithm_conformance"
    return "effect_runtime_provider"


def build_batches(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        family = research_family(row["library_ref"])
        assert family != "unclassified_refuse", row["library_ref"]
        grouped[(family, research_lane(row))].append(row)
    batches = []
    for (family, lane), items in grouped.items():
        items = sorted(items, key=lambda row: (-row["priority_score"], row["library_ref"]))
        priorities = Counter(row["priority_band"] for row in items)
        missing = Counter(dimension for row in items for dimension in row["placeholder_dimensions"])
        batches.append({
            "record_kind": "exact_api_research_batch",
            "batch_id": f"batch.exact-api.{family}.{lane}",
            "edition": 1,
            "as_of": AS_OF,
            "research_family": family,
            "research_lane": lane,
            "status": "OPEN_RESEARCH_AND_OWNER_ADJUDICATION",
            "rank_score": max(row["priority_score"] for row in items),
            "item_count": len(items),
            "counts_by_priority_band": dict(sorted(priorities.items())),
            "counts_by_missing_dimension": dict(sorted(missing.items())),
            "library_refs": [row["library_ref"] for row in items],
            "closure_refs": [row["closure_id"] for row in items],
            "semantic_owner_refs": sorted({ref for row in items for ref in row["semantic_owner_refs"]}),
            "product_refs": sorted({ref for row in items for ref in row["product_refs"]}),
            "vertical_composition_refs": sorted({ref for row in items for ref in row["vertical_composition_refs"]}),
            "evidence_program": FAMILY_EVIDENCE_PROGRAM[family],
            "primary_evidence_seeds": FAMILY_PRIMARY_EVIDENCE_SEEDS.get(family, []),
            "evidence_seed_status": "DISCOVERY_ONLY_NOT_ADOPTED_AUTHORITY",
            "execution_strategy": [
                "adjudicate cohesion, owner, exclusions and dependencies for every library before signatures",
                "research primary standards, original papers and official project semantics on the internet as a reusable family evidence pack",
                "encode exact types, traits, operations, refusals, precedence, laws, bounds and oracles for a coherent sub-batch",
                "regenerate the central registry once per coherent sub-batch and run independent validators concurrently",
            ],
            "batch_closure_law": "Every listed closure item must either close through an owner-published exact contract or be replaced/retired through an explicit no-alias boundary adjudication; batch completion never implies implementation or qualification.",
            "prohibited_shortcuts": [
                "one generic API template across unlike semantics",
                "vendor-name or package-shape boundaries",
                "secondary summaries when primary specifications exist",
                "one passing implementation treated as portability",
                "LLM or agent proposal treated as semantic or approval authority",
            ],
        })
    return sorted(batches, key=lambda row: (-row["rank_score"], row["batch_id"]))


def outputs() -> dict[str, str]:
    records = build_records()
    batches = build_batches(records)
    queue = "".join(canonical(row) + "\n" for row in records)
    batch_plan = "".join(canonical(row) + "\n" for row in batches)
    bands = Counter(row["priority_band"] for row in records)
    families = Counter(research_family(row["library_ref"]) for row in records)
    lanes = Counter(research_lane(row) for row in records)
    summary = {
        "program_id": "program.exact-api-closure.v1",
        "edition": 1,
        "as_of": AS_OF,
        "status": "ACTIVE_INCOMPLETE",
        "completion_claim": False,
        "open_items": len(records),
        "research_batches": len(batches),
        "counts_by_priority_band": dict(sorted(bands.items())),
        "counts_by_research_family": dict(sorted(families.items())),
        "counts_by_research_lane": dict(sorted(lanes.items())),
        "laws": [
            "Every central exact_api_contract_missing gap appears exactly once in this queue.",
            "Priority changes work order and never weakens closure evidence.",
            "A source-level exact API is not implementation, qualification, portability or product acceptance.",
        ],
    }
    summary_text = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    manifest = {
        "manifest_id": "manifest.exact-api-closure.v1",
        "as_of": AS_OF,
        "counts": {"exact_api_closure_item": len(records), "exact_api_research_batch": len(batches)},
        "files": {
            "closure-queue.jsonl": {"sha256": hashlib.sha256(queue.encode()).hexdigest(), "bytes": len(queue.encode())},
            "research-batches.jsonl": {"sha256": hashlib.sha256(batch_plan.encode()).hexdigest(), "bytes": len(batch_plan.encode())},
            "summary.json": {"sha256": hashlib.sha256(summary_text.encode()).hexdigest(), "bytes": len(summary_text.encode())},
        },
    }
    return {
        "closure-queue.jsonl": queue,
        "research-batches.jsonl": batch_plan,
        "summary.json": summary_text,
        "manifest.json": json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale: list[str] = []
    for name, content in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            path.write_text(content, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    print(f"{'CHECK' if args.check else 'BUILD'} PASS exact-API closure queue: {len(build_records())} open items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
