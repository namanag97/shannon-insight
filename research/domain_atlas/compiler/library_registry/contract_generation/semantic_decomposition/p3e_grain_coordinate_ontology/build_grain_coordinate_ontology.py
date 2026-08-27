#!/usr/bin/env python3
"""Build the operation-positioned grain/cardinality ontology and lossless P3E rebase.

The existing semantic-axis facets are intentionally retained as discovery
projections.  They are not promoted into member applicability decisions.  An
exact grain contract is a tuple attached to a meaningful operation port, state,
event, evidence item or receipt, plus the transformation between such tuples.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"

P3E_DOCKETS = SEM / "p3e_grain_cardinality_evidence/family-evidence-dockets.jsonl"
PRECLASSIFICATIONS = SEM / "applicability_matrices/member-preclassifications.jsonl"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


PRIMARY_SOURCES = [
    {
        "source_id": "source.grain.substrait.logical-relations",
        "title": "Substrait Logical Relations",
        "publisher": "Substrait",
        "url": "https://substrait.io/relations/logical_relations/",
        "bounded_implication": "Relational operators have explicit input/output arity and operation-specific record behavior; filter, join, set, fetch and aggregate do not share one cardinality law.",
        "authority_limit": "Substrait establishes relational-plan semantics, not domain entity grain, source completeness, authority or business acceptance.",
    },
    {
        "source_id": "source.grain.arrow.introduction",
        "title": "Apache Arrow Format: Introduction and Terminology",
        "publisher": "Apache Arrow",
        "url": "https://arrow.apache.org/docs/format/Intro.html",
        "bounded_implication": "Array, chunked array, record batch, table, field and buffer occupy distinct logical and physical levels.",
        "authority_limit": "Arrow layout and length do not establish business observation grain, completeness or semantic identity.",
    },
    {
        "source_id": "source.grain.beam.model",
        "title": "Basics of the Apache Beam Model",
        "publisher": "Apache Beam",
        "url": "https://beam.apache.org/documentation/basics/",
        "bounded_implication": "Element, PCollection, window, pane and boundedness are distinct coordinates; aggregation completeness is window- and trigger-dependent.",
        "authority_limit": "Beam execution semantics do not establish source-system completeness, domain identity or accepted sink effects.",
    },
    {
        "source_id": "source.grain.iceberg.spec",
        "title": "Apache Iceberg Specification",
        "publisher": "Apache Iceberg",
        "url": "https://iceberg.apache.org/spec/",
        "bounded_implication": "Table, snapshot, manifest list, manifest, data/delete file, partition tuple and row are distinct levels with different completeness and concurrency boundaries.",
        "authority_limit": "Iceberg table metadata does not establish business grain, catalog authority or cross-format semantic equivalence.",
    },
    {
        "source_id": "source.grain.ocel.2",
        "title": "Object-Centric Event Log 2.0 Specification",
        "publisher": "OCEL Standard",
        "url": "https://ocel-standard.org/2.0/ocel20_specification.pdf",
        "bounded_implication": "Events, objects, event-object relations and object-object relations form a many-object event model; a single inherent case grain is not guaranteed.",
        "authority_limit": "OCEL defines an event-log interchange model, not a universal case projection, business entity or analytical acceptance boundary.",
    },
]


ONTOLOGY = {
    "ontology_id": "ontology.semantic-axis.grain-coordinate.v1",
    "edition": 1,
    "as_of": AS_OF,
    "axis": "grain_and_cardinality",
    "domain_question": "For each meaningful semantic position, what unit is observed or acted on, what contains it, what multiplicity is legal, what completeness boundary applies, and how does an operation transform those facts?",
    "scope": {
        "inside": [
            "operation-positioned units and containers",
            "cardinality intervals and multiplicity semantics",
            "boundedness and completeness scope",
            "grain-changing transformation kernels",
            "declared preservation and loss across a transformation",
            "dependencies on identity, order, time, state, uncertainty and authority",
        ],
        "outside": [
            "domain identity adjudication",
            "source-of-truth or ownership decisions",
            "business metric correctness",
            "physical performance or storage layout unless explicitly positioned as a physical carrier",
            "member applicability inferred from library names",
        ],
    },
    "coordinate_contract": {
        "coordinate_key": ["subject_ref", "operation_ref", "semantic_position", "port_ref"],
        "required_fields": [
            "semantic_position",
            "semantic_unit",
            "container_scope",
            "multiplicity_semantics",
            "cardinality_contract",
            "boundedness_and_completeness",
            "dependency_refs",
            "evidence_refs",
        ],
        "semantic_position": [
            "source",
            "input",
            "parameter",
            "configuration",
            "internal_state",
            "index",
            "event",
            "evidence",
            "output",
            "receipt",
            "sink_effect",
        ],
        "semantic_unit": [
            "scalar_value",
            "field_value",
            "record_or_tuple",
            "domain_entity",
            "domain_occurrence",
            "event_occurrence",
            "relation_edge",
            "path",
            "spatial_cell",
            "time_bucket",
            "optimization_variable",
            "model_artifact",
            "claim_or_evidence_item",
            "receipt",
            "explicit_extension",
        ],
        "container_scope": [
            "singleton",
            "optional",
            "set",
            "bag",
            "sequence",
            "map",
            "multimap",
            "table",
            "batch",
            "page",
            "partition",
            "shard",
            "window",
            "pane",
            "stream",
            "graph",
            "hierarchy",
            "model",
            "artifact_bundle",
            "explicit_extension",
        ],
        "multiplicity_semantics": [
            "single",
            "optional_zero_or_one",
            "set_distinct",
            "bag_duplicates_significant",
            "sequence_position_significant",
            "map_unique_key",
            "multimap_repeated_key",
            "graph_incidence",
            "unknown_must_be_declared",
        ],
        "cardinality_contract": {
            "lower_bound": "non_negative_integer_or_symbolic_expression",
            "upper_bound": "non_negative_integer_or_unbounded_or_unknown_or_symbolic_expression",
            "exactness": ["exact", "bounded", "estimated", "unknown"],
            "count_basis": [
                "physical_occurrence",
                "logical_occurrence",
                "distinct_by_equality_contract_ref",
                "weighted_occurrence",
                "unknown_must_be_declared",
            ],
            "empty_input_behavior": "required when it affects output cardinality",
            "duplicate_behavior": "required for set, bag, join, union, distinct and replay-sensitive operations",
        },
        "boundedness_and_completeness": {
            "boundedness": [
                "finite_known",
                "finite_unknown",
                "unbounded",
                "window_bounded",
                "snapshot_bounded",
                "unknown",
            ],
            "completeness_scope": [
                "element_local",
                "page_local",
                "batch_local",
                "partition_local",
                "window_local",
                "snapshot_local",
                "source_local",
                "global_claimed_with_proof",
                "partial",
                "unknown",
            ],
            "completion_proof_ref": "required for any non-local completeness claim",
        },
        "dependency_refs": [
            "identity_and_equality",
            "order_and_topology",
            "state_and_change",
            "time_and_temporality",
            "partiality_and_uncertainty",
            "authority_and_effect",
        ],
    },
    "discovery_projection_compatibility": {
        "existing_facets": [
            "scalar_or_single",
            "record_or_tuple",
            "collection_or_set",
            "partitioned",
            "stream_or_unbounded",
            "graph_or_network",
        ],
        "status": "LOSSY_LEXICAL_DISCOVERY_PROJECTION_ONLY",
        "prohibition": "Existing facets may route research. They cannot select a semantic position, operation, container, multiplicity, cardinality law, completeness boundary, applicability decision or exact contract.",
    },
    "non_collapse_laws": [
        "library is not operation",
        "operation is not port",
        "semantic unit is not container scope",
        "record is not domain entity",
        "page is not result set",
        "partition-local completeness is not global completeness",
        "physical chunk is not semantic batch",
        "window is not pane",
        "bounded is not complete",
        "count equality is not identity preservation",
        "set is not bag and bag is not sequence",
        "event-to-object relation is not an inherent single case",
        "snapshot is not table history",
        "evidence aggregation is not evidence acceptance",
    ],
    "required_negative_twins": [
        "zero inputs versus empty input container",
        "zero outputs versus refused or failed operation",
        "duplicate occurrence versus same semantic identity",
        "late record versus absent record",
        "page exhaustion versus source completeness",
        "partition completion versus global completion",
        "one-to-many expansion versus replay duplication",
        "aggregate row versus preserved source row",
    ],
    "primary_source_refs": [row["source_id"] for row in PRIMARY_SOURCES],
    "owner_decision": "UNRESOLVED",
    "member_applicability_decisions": 0,
    "canonical_gaps_closed": 0,
    "completion_claim": False,
}


KERNEL_DEFINITIONS = [
    ("identity", "one", "one", "|out| = |in|", ["subject identity", "multiplicity", "order when declared"], [], "Equal counts alone do not prove identity preservation."),
    ("filter", "one", "one", "0 <= |out| <= |in|", ["surviving occurrence identity", "relative order when declared"], ["cardinality", "completeness"], "A filtered result is not a complete source population."),
    ("one_to_one_map", "one", "one", "|out| = |in|", ["occurrence correspondence when evidenced"], ["semantic unit", "identity", "value equality"], "One output per input does not imply the output is the same entity."),
    ("project", "one", "one", "|out records| = |in records| unless projection also embeds a cardinality-changing expression", ["record occurrence count"], ["information", "keys", "identity evidence"], "Dropping fields can destroy identity or distinguishability without changing row count."),
    ("flat_map_or_explode", "one", "one", "|out| = sum(expansion_count(input_occurrence))", [], ["cardinality", "unit", "identity", "order"], "Expanded children are not automatically independent domain entities."),
    ("group_aggregate", "one", "one", "|out| = number_of_materialized_groups under declared empty-input and grouping-set rules", ["group key values when declared"], ["grain", "cardinality", "identity", "completeness", "uncertainty"], "An aggregate output row is not a preserved input row."),
    ("distinct_or_deduplicate", "one", "one", "|out| = number_of equivalence classes under equality_contract_ref", [], ["cardinality", "occurrence identity", "order", "evidence"], "Deduplication is undefined without an equality and survivor policy."),
    ("join", "many", "one", "|out| depends on join type and per-key match multiplicities", [], ["cardinality", "nullability", "identity", "order", "completeness"], "A join key is not automatically business identity and joins may multiply rows."),
    ("cross_product", "two", "one", "|out| = |left| * |right| for finite inputs", [], ["cardinality", "unit", "order"], "A cross-product row is a composite occurrence, not either input occurrence."),
    ("set_or_multiset_combine", "many", "one", "operation-specific set or bag law", [], ["duplicates", "cardinality", "order", "null equality"], "UNION ALL, UNION DISTINCT, INTERSECT and EXCEPT do not share one multiplicity law."),
    ("fetch_limit_or_page", "one", "one", "0 <= |out| <= requested_limit and |out| <= remaining_input", ["relative order when the input order is defined"], ["cardinality", "completeness"], "A full or final page does not by itself prove source completeness."),
    ("partition_or_shard", "one", "many_logical_outputs", "sum(partition occurrences) relates to input only under declared overlap and drop policy", [], ["scope", "order", "completeness", "duplication"], "Partition-local properties are not global properties."),
    ("window_assign", "one", "one_or_many_memberships", "an occurrence may belong to zero, one or multiple windows under the window function", ["source occurrence identity when evidenced"], ["multiplicity", "time scope", "completeness"], "Window membership duplication is not source replay duplication."),
    ("pane_emit", "one_window", "many_over_time", "zero or more panes per window under trigger and accumulation mode", [], ["temporal cardinality", "completeness", "retractions"], "A pane is not necessarily the final value for a window."),
    ("batch_or_chunk", "one", "many_physical_or_execution_units", "chunks cover the input only under an explicit coverage contract", [], ["physical boundaries", "retries", "order", "completeness"], "A physical buffer, execution bundle and semantic batch are not interchangeable."),
    ("nest_or_collect", "many", "one_or_many_containers", "output count depends on grouping scope; child multiplicity is retained only if declared", [], ["unit", "container", "order", "duplicates"], "One container output can represent many child occurrences without merging their identities."),
    ("unnest", "one", "one", "|out| = sum(nested_member_count(input_occurrence)) subject to null/empty rules", [], ["cardinality", "parent-child identity", "order"], "Empty, null and missing nested values can yield different cardinalities."),
    ("sample", "one", "one", "|out| is governed by the sampling design, frame and replacement policy", [], ["cardinality", "weights", "uncertainty", "population completeness"], "A sample is not the population and equal inclusion probability must not be assumed."),
    ("graph_traverse_or_expand", "graph_and_seed", "paths_nodes_or_edges", "output depends on traversal semantics, direction, revisit and path uniqueness policies", [], ["topology", "identity", "cycles", "cardinality", "order"], "Node, edge, path and reached-set grains are distinct."),
    ("snapshot_or_materialize", "state_or_stream", "snapshot", "snapshot membership is defined at a declared validity/recording/commit boundary", [], ["time", "state", "completeness", "concurrency"], "One snapshot is not the full history and storage files are not the snapshot identity."),
    ("update_retract_or_upsert", "changes", "state_or_changes", "occurrence count and state cardinality depend on key, operation kind and replay policy", [], ["identity", "state", "idempotency", "order", "time"], "Change-record count is not current-state entity count."),
    ("encode_decode_or_rechunk", "logical_or_physical_carrier", "physical_or_logical_carrier", "logical cardinality is preserved only if the codec round-trip contract says so", [], ["representation", "partiality", "loss", "chunking"], "Physical buffer or chunk count is not logical element count."),
    ("model_solve_or_infer", "model_and_observations", "assignments_predictions_or_distribution", "output unit and count follow the declared model/result contract", [], ["model version", "uncertainty", "feasibility", "acceptance authority"], "A solver assignment or prediction is not an authorized business action."),
    ("evidence_aggregate", "claims_or_evidence", "finding_or_receipt", "output count follows grouping and adjudication rules, not mere input count", [], ["provenance", "authority", "defeaters", "uncertainty"], "Collected evidence is not accepted proof and one receipt is not one source fact."),
]


def build_kernels() -> list[dict[str, Any]]:
    source_refs = [row["source_id"] for row in PRIMARY_SOURCES]
    return [
        {
            "record_kind": "grain_transformation_kernel",
            "kernel_id": f"kernel.grain.{name}.v1",
            "input_arity": input_arity,
            "output_arity": output_arity,
            "cardinality_relation": law,
            "candidate_preservations": preserves,
            "must_adjudicate": changes,
            "required_contract_fields": [
                "input_coordinate_refs",
                "output_coordinate_refs",
                "empty_input_behavior",
                "duplicate_behavior",
                "completeness_effect",
                "dependency_refs",
                "evidence_refs",
            ],
            "negative_twin": negative,
            "primary_source_pool_refs": source_refs,
            "applicability": "UNRESOLVED_PER_OPERATION",
            "status": "REUSABLE_KERNEL_CONTRACT_NOT_MEMBER_DECISION",
            "completion_claim": False,
        }
        for name, input_arity, output_arity, law, preserves, changes, negative in KERNEL_DEFINITIONS
    ]


def build() -> dict[str, Any]:
    dockets = load_jsonl(P3E_DOCKETS)
    preclass_rows = [
        row
        for row in load_jsonl(PRECLASSIFICATIONS)
        if row["axis"] == "grain_and_cardinality"
    ]
    preclass_by_library = {row["library_ref"]: row for row in preclass_rows}
    if len(preclass_by_library) != len(preclass_rows):
        raise ValueError("grain preclassifications contain duplicate library refs")

    target_members = {
        library_ref
        for docket in dockets
        for library_ref in docket["library_refs"]
    }
    if len(target_members) != sum(docket["library_count"] for docket in dockets):
        raise ValueError("P3E target dockets contain duplicate library occurrences")
    if not target_members <= set(preclass_by_library):
        raise ValueError("P3E target member is missing a flat discovery preclassification")

    cluster_members: dict[tuple[str, str, tuple[str, ...]], list[str]] = defaultdict(list)
    docket_by_family = {row["family_ref"]: row for row in dockets}
    member_routes: list[dict[str, Any]] = []
    for family_ref, docket in sorted(docket_by_family.items()):
        for library_ref in docket["library_refs"]:
            preclass = preclass_by_library[library_ref]
            facets = tuple(item["facet"] for item in preclass["candidate_facets"])
            cluster_key = (family_ref, preclass["preclassification"], facets)
            cluster_members[cluster_key].append(library_ref)

    cluster_ids: dict[tuple[str, str, tuple[str, ...]], str] = {}
    clusters: list[dict[str, Any]] = []
    family_ordinals: dict[str, int] = defaultdict(int)
    for key, library_refs in sorted(cluster_members.items()):
        family_ref, preclassification, facets = key
        family_ordinals[family_ref] += 1
        short = family_ref.removeprefix("constitution.family.")
        cluster_id = f"cluster.p3e.grain-rebase.{short}.{family_ordinals[family_ref]:02d}"
        cluster_ids[key] = cluster_id
        route = (
            "LEXICAL_DISCOVERY_PROJECTION_ONLY_OPERATION_RESEARCH_REQUIRED"
            if facets
            else "NO_MEMBER_OPERATION_EVIDENCE_VACANCY"
        )
        clusters.append(
            {
                "record_kind": "grain_member_research_cluster",
                "cluster_id": cluster_id,
                "family_ref": family_ref,
                "flat_preclassification": preclassification,
                "flat_candidate_facets": list(facets),
                "library_refs": sorted(library_refs),
                "library_count": len(library_refs),
                "research_route": route,
                "required_next_evidence": [
                    "authoritative operation inventory",
                    "externally meaningful port/state/event/evidence/receipt inventory",
                    "coordinate tuple per meaningful position",
                    "transformation-kernel composition per operation",
                    "negative twins and exception proof",
                ],
                "member_applicability": "UNRESOLVED",
                "owner_decision": "UNRESOLVED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )

    for family_ref, docket in sorted(docket_by_family.items()):
        for library_ref in docket["library_refs"]:
            preclass = preclass_by_library[library_ref]
            facets = tuple(item["facet"] for item in preclass["candidate_facets"])
            key = (family_ref, preclass["preclassification"], facets)
            member_routes.append(
                {
                    "record_kind": "grain_member_operation_research_route",
                    "route_id": f"route.p3e.grain-rebase.{library_ref.removeprefix('library.').replace('_', '-')}",
                    "library_ref": library_ref,
                    "family_ref": family_ref,
                    "source_gap_ref": preclass["source_gap_ref"],
                    "flat_preclassification_ref": preclass["preclassification_id"],
                    "flat_preclassification": preclass["preclassification"],
                    "flat_candidate_facets": [item["facet"] for item in preclass["candidate_facets"]],
                    "flat_projection_effect": "DISCOVERY_ROUTING_ONLY_NOT_APPLICABILITY",
                    "family_evidence_docket_ref": docket["docket_id"],
                    "family_evidence_candidate_refs": docket["evidence_candidate_refs"],
                    "research_cluster_ref": cluster_ids[key],
                    "required_coordinate_profile": "OPERATION_POSITIONED_PROFILE_NOT_YET_SUPPLIED",
                    "required_transformation_composition": "NOT_YET_SUPPLIED",
                    "research_route": (
                        "LEXICAL_DISCOVERY_PROJECTION_ONLY_OPERATION_RESEARCH_REQUIRED"
                        if facets
                        else "NO_MEMBER_OPERATION_EVIDENCE_VACANCY"
                    ),
                    "member_applicability": "UNRESOLVED",
                    "owner_decision": "UNRESOLVED",
                    "canonical_gaps_closed": 0,
                    "status": "LOSSLESSLY_ROUTED_RESEARCH_OPEN",
                    "completion_claim": False,
                }
            )

    family_extensions = []
    for family_ref, docket in sorted(docket_by_family.items()):
        short = family_ref.removeprefix("constitution.family.")
        family_extensions.append(
            {
                "record_kind": "grain_exact_contract_extension_candidate",
                "extension_id": f"extension.p3e.grain-coordinate.{short}.v1",
                "family_ref": family_ref,
                "family_evidence_docket_ref": docket["docket_id"],
                "represented_library_refs": docket["library_refs"],
                "represented_library_count": docket["library_count"],
                "required_record_kinds": [
                    "operation_contract",
                    "operation_port_grain_coordinate",
                    "grain_transformation_composition",
                    "grain_preservation_or_loss_claim",
                    "completeness_boundary_claim",
                    "negative_twin",
                    "member_exception",
                ],
                "required_owner_action": "ratify operation-positioned coordinates or explicitly preserve vacancy",
                "owner_decision": "UNRESOLVED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )

    kernels = build_kernels()
    summary = {
        "program_id": "program.p3e.grain-coordinate-ontology-and-rebase.v1",
        "as_of": AS_OF,
        "axis": "grain_and_cardinality",
        "primary_sources": len(PRIMARY_SOURCES),
        "transformation_kernels": len(kernels),
        "family_extension_candidates": len(family_extensions),
        "research_clusters": len(clusters),
        "target_member_routes": len(member_routes),
        "routes_with_lexical_discovery_projection": sum(bool(row["flat_candidate_facets"]) for row in member_routes),
        "routes_with_no_member_operation_evidence": sum(not row["flat_candidate_facets"] for row in member_routes),
        "operation_positioned_profiles_supplied": 0,
        "member_applicability_decisions": 0,
        "owner_decisions": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {
        "ontology": ONTOLOGY,
        "sources": PRIMARY_SOURCES,
        "kernels": kernels,
        "clusters": clusters,
        "member_routes": member_routes,
        "extensions": family_extensions,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "grain-coordinate-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "grain-transformation-kernels.jsonl": "".join(canonical(row) + "\n" for row in built["kernels"]),
        "member-research-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "member-operation-routes.jsonl": "".join(canonical(row) + "\n" for row in built["member_routes"]),
        "extension-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["extensions"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.p3e.grain-coordinate-ontology-and-rebase.v1",
            "as_of": AS_OF,
            "files": claims,
            "completion_claim": False,
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(
        "BUILD PASS P3E grain coordinate ontology: "
        f"{summary['transformation_kernels']} kernels, {summary['research_clusters']} lossless clusters, "
        f"{summary['target_member_routes']} member routes; applicability and gap closure remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
