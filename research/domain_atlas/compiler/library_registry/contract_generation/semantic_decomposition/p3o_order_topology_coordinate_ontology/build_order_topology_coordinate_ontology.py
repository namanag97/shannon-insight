#!/usr/bin/env python3
"""Build a relation-positioned order/topology ontology and lossless P3O rebase."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
P3O_DOCKETS = SEM / "p3o_order_topology_evidence/family-evidence-dockets.jsonl"
PRECLASSIFICATIONS = SEM / "applicability_matrices/member-preclassifications.jsonl"
sys.path.insert(0, str(SEM))

from member_axis_rebase import build_member_rebase  # noqa: E402


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


PRIMARY_SOURCES = [
    {
        "source_id": "source.order.rdf-concepts",
        "title": "RDF 1.1 Concepts and Abstract Syntax",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/rdf11-concepts/",
        "bounded_implication": "An RDF graph is a set of triples; semantic sequence must be represented explicitly rather than inferred from statement serialization order.",
        "authority_limit": "RDF does not choose domain hierarchy, traversal order, workflow precedence, causality or canonical serialization.",
    },
    {
        "source_id": "source.order.prov-constraints",
        "title": "Constraints of the PROV Data Model",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/prov-constraints/",
        "bounded_implication": "PROV defines preorder and strict-precedence constraints among generation, usage, invalidation, start and end without requiring a total physical-clock order.",
        "authority_limit": "A valid provenance relation does not prove record completeness, direct causality, truth or total comparability.",
    },
    {
        "source_id": "source.order.onnx-ir",
        "title": "ONNX Intermediate Representation Specification",
        "publisher": "ONNX",
        "url": "https://onnx.ai/onnx/repo-docs/IR.html",
        "bounded_implication": "An ONNX dataflow graph is acyclic and serialized in a topological order while some lists remain unordered or independently ordered.",
        "authority_limit": "One topological serialization is not the only execution schedule, business causality or order among independent results.",
    },
    {
        "source_id": "source.order.substrait-relations",
        "title": "Substrait Logical Relations",
        "publisher": "Substrait",
        "url": "https://substrait.io/relations/logical_relations/",
        "bounded_implication": "Relation-input topology, field ordinal order and row orderedness are distinct; operators explicitly preserve, clear, establish or remap orderedness.",
        "authority_limit": "Relational-plan orderedness does not define domain sequence, causal order, presentation order or cross-engine execution schedule.",
    },
    {
        "source_id": "source.order.beam-model",
        "title": "Basics of the Apache Beam model",
        "publisher": "Apache Beam",
        "url": "https://beam.apache.org/documentation/basics/",
        "bounded_implication": "Pipeline transforms form a dependency graph while a PCollection is unordered; timestamps, windows and watermarks add separately scoped temporal relations.",
        "authority_limit": "Construction order, runner execution, arrival order, event time and business causality are not interchangeable.",
    },
    {
        "source_id": "source.order.skos-primer",
        "title": "SKOS Simple Knowledge Organization System Primer",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/skos-primer/",
        "bounded_implication": "Broader/narrower, transitive ancestry, associative links, unordered collections and ordered collections are distinct; multiple broader concepts are allowed.",
        "authority_limit": "SKOS hierarchy is not automatically a tree, OWL subclassing, partonomy, ownership, display order or workflow precedence.",
    },
    {
        "source_id": "source.order.geosparql",
        "title": "OGC GeoSPARQL 1.1",
        "publisher": "Open Geospatial Consortium",
        "url": "https://docs.ogc.org/is/22-047r1/22-047r1.html",
        "bounded_implication": "GeoSPARQL defines parameterized spatial-relation families such as equals, disjoint, touches, crosses, within, contains and overlaps for features or geometries.",
        "authority_limit": "Spatial topology is not coordinate order, movement chronology, network connectivity, jurisdiction hierarchy or business containment.",
    },
]


RELATION_ARCHETYPES = [
    ("sequence_position", "Position in a finite or potentially unbounded sequence with explicit predecessor/successor semantics."),
    ("total_order", "A relation in which every admissible pair is comparable under a declared comparator and tie policy."),
    ("partial_order", "A reflexive antisymmetric transitive relation that admits incomparable elements."),
    ("strict_partial_order", "An irreflexive transitive relation, often precedence, that admits incomparability."),
    ("preorder", "A reflexive transitive relation whose mutually related elements need not be identical."),
    ("equivalence_partition", "An equivalence relation and its induced classes under an explicit equality contract."),
    ("causal_or_happens_before", "A witnessed causal or happens-before relation distinct from clock or arrival order."),
    ("dependency_dag", "Acyclic dependency relation with one or many valid topological extensions."),
    ("partition_local_log_order", "Total order scoped to one log partition, shard or journal, not a global order."),
    ("hierarchy_or_taxonomy", "Broader/narrower or parent/child relation that may be a tree, DAG or polyhierarchy."),
    ("partonomy_or_containment", "Part/whole, containment or nesting relation distinct from taxonomy and ownership."),
    ("directed_multigraph", "Directed nodes and edges with possible parallel edges, self-loops and typed incidence."),
    ("hypergraph_or_incidence", "Relations connecting more than two endpoints or explicit incidence structures."),
    ("spatial_topology", "Parameterized qualitative topology over spatial objects, geometries or regions."),
    ("temporal_interval_relation", "Before, after, overlap, meet, contain or other interval/instant relations under a time model."),
    ("rank_or_preference", "Rank, score order, dominance or preference, with explicit ties and incomparability."),
    ("render_or_layer_order", "Visual paint, z-layer, focus or reading order scoped to a presentation context."),
    ("join_or_reference_path", "A typed path through references, joins or semantic-model relations with path validity rules."),
    ("provenance_influence", "Qualified influence, derivation or lineage relation that does not by itself prove causality."),
    ("allocation_or_exclusion_topology", "Partition, overlap, mutual-exclusion or membership topology for allocation domains."),
]


def relation_archetype_rows() -> list[dict[str, Any]]:
    return [
        {
            "record_kind": "order_topology_relation_archetype",
            "archetype_id": f"archetype.order-topology.{name}.v1",
            "meaning": meaning,
            "required_coordinate_ref": "ontology.semantic-axis.order-topology-coordinate.v1#relation_coordinate",
            "applicability": "UNRESOLVED_PER_RELATION_AND_USE_SITE",
            "completion_claim": False,
        }
        for name, meaning in RELATION_ARCHETYPES
    ]


ONTOLOGY = {
    "ontology_id": "ontology.semantic-axis.order-topology-coordinate.v1",
    "edition": 1,
    "as_of": AS_OF,
    "axis": "order_and_topology",
    "domain_question": "Over which identified endpoint domain does which relation hold, with what algebraic properties, scope, witnesses, path semantics and representation boundary?",
    "coordinate_key": [
        "bounded_context_ref",
        "endpoint_domain_ref",
        "relation_ref",
        "relation_edition_ref",
        "scope_ref",
        "use_site_ref",
    ],
    "relation_coordinate": {
        "required_fields": [
            "endpoint_identity_and_type_refs",
            "relation_archetype_ref",
            "arity_direction_and_multiplicity",
            "algebraic_property_profile",
            "comparability_outcomes",
            "scope_and_partition_boundary",
            "tie_stability_and_null_policy",
            "path_and_cycle_policy",
            "witness_or_derivation_ref",
            "representation_versus_semantic_status",
            "authority_and_evidence_refs",
        ],
        "algebraic_properties": [
            "reflexive_or_irreflexive",
            "symmetric_asymmetric_or_antisymmetric",
            "transitive_or_nontransitive",
            "total_connected_or_partial",
            "acyclic_or_cycles_allowed",
            "well_founded_or_unbounded_descent_allowed",
            "stable_or_unstable_under_equal_keys",
            "single_edge_multiedge_or_hyperedge",
        ],
        "comparability_outcomes": [
            "before",
            "after",
            "equal_under_relation",
            "equivalent_not_identical",
            "concurrent",
            "incomparable",
            "disconnected",
            "cycle_detected",
            "relation_unbound",
            "indeterminate",
            "refused",
        ],
        "scope_kinds": [
            "global_claimed_with_proof",
            "partition_local",
            "window_local",
            "transaction_local",
            "case_or_object_local",
            "graph_component_local",
            "representation_local",
            "presentation_local",
            "unknown",
        ],
    },
    "path_contract": {
        "required_fields": [
            "start_and_end_domain_refs",
            "allowed_edge_relation_refs",
            "direction",
            "path_identity_and_equivalence",
            "simple_or_repeating_path",
            "cycle_policy",
            "cost_or_weight_algebra_ref",
            "closure_materialization_status",
            "witness_and_provenance",
        ]
    },
    "dependency_axis_refs": [
        "semantic_object",
        "identity_and_equality",
        "grain_and_cardinality",
        "state_and_change",
        "time",
        "partiality_and_uncertainty",
        "composition_algebra",
        "representation",
        "evidence_and_conformance",
    ],
    "discovery_projection_compatibility": {
        "existing_facets": [
            "total_order",
            "partial_order",
            "hierarchy",
            "graph_topology",
            "spatial_topology",
        ],
        "status": "LOSSY_LEXICAL_DISCOVERY_PROJECTION_ONLY",
        "prohibition": "A facet cannot select endpoint types, relation edition, algebraic laws, scope, path semantics, causality, member applicability or exact contract.",
    },
    "non_collapse_laws": [
        "serialization order is not semantic order",
        "arrival order is not source event time processing or causal order",
        "partition-local total order is not global order",
        "total order is not partial order and incomparability is a valid result",
        "a deterministic linear extension does not manufacture causality",
        "dependency is not causality and influence is not causal effect",
        "reachability is not adjacency",
        "hierarchy is not necessarily a tree",
        "taxonomy is not partonomy containment or ownership",
        "graph node edge path and connected component are distinct grains",
        "graph isomorphism is not subject identity or semantic equivalence",
        "sort key order is not field order row order render order or rank",
        "spatial topology is not coordinate order or network connectivity",
        "z-index is not accessibility reading order or business priority",
    ],
    "primary_source_refs": [row["source_id"] for row in PRIMARY_SOURCES],
    "owner_decision": "UNRESOLVED",
    "member_applicability_decisions": 0,
    "canonical_gaps_closed": 0,
    "completion_claim": False,
}


KERNEL_DEFINITIONS = [
    ("preserve_declared_order", "ordered input", "output with the same relation only when preservation preconditions hold", "Equal values or counts do not prove order preservation."),
    ("clear_order", "ordered or unordered input", "output with orderedness explicitly absent", "Unknown or cleared order must not be treated as arbitrary but stable order."),
    ("sort_total_extension", "collection plus comparator", "one deterministic total extension", "A sorted extension does not prove causal or intrinsic total order."),
    ("stable_sort", "sequence plus comparator", "ordered sequence preserving prior order among comparator-equivalent items", "Stability is scoped to the input sequence and equality/comparator profile."),
    ("rank_with_ties", "scored or preferred items", "rank classes and tie policy", "Rank equality is not subject equality and rank need not be a total order."),
    ("top_k_or_fetch", "ordered input", "bounded prefix or offset window", "A page or top-k result is not the complete ordered domain."),
    ("partition", "one endpoint domain", "several scoped domains", "Order within partitions does not create cross-partition comparability."),
    ("concatenate", "ordered sequences", "one sequence under declared operand order", "Concatenation order is not merge-by-key or event-time order."),
    ("merge_sorted", "multiple ordered inputs", "ordered output under one compatible comparator", "Local sortedness is insufficient when comparator or null policies differ."),
    ("shuffle_or_repartition", "collection with possible order", "repartitioned collection", "Execution determinism must not be inferred from incidental output order."),
    ("group_or_aggregate", "ordered or unordered occurrences", "groups and aggregates", "Group keys define equivalence classes, not presentation or causal order."),
    ("join_path", "typed endpoint domains and predicates", "matched composite occurrences", "Reachable join paths are not automatically semantically valid or unique."),
    ("set_or_bag_combine", "collections", "combined set/bag", "Set, bag and sequence operations have different duplicate and order laws."),
    ("dependency_edge_add", "dependency graph", "updated graph or cycle refusal", "Adding an edge can invalidate acyclicity and does not by itself prove causality."),
    ("topological_sort", "acyclic dependency graph", "one linear extension", "Many valid topological orders can denote the same dependency graph."),
    ("transitive_closure", "binary relation", "reachable-pair relation", "A closure edge is derived reachability, not a direct asserted edge."),
    ("transitive_reduction", "acyclic reachability relation", "minimal edge representation when defined", "Removing redundant edges changes representation, not reachability, under bounded preconditions."),
    ("graph_traverse", "graph plus seed and policy", "nodes edges or paths", "Traversal visitation order is not semantic graph order."),
    ("shortest_or_best_path", "weighted graph", "optimal path under declared algebra", "Optimality depends on weights, constraints and tie policy and does not imply authorization."),
    ("hierarchy_rollup", "polyhierarchy plus values", "ancestor aggregates", "Multiple parents can double count unless allocation semantics are explicit."),
    ("hierarchy_linearize", "tree or DAG", "display/traversal sequence", "Display order is not broader/narrower semantics."),
    ("containment_nest", "part/whole relation", "nested representation", "Nesting does not prove ownership, lifecycle dependence or taxonomy."),
    ("spatial_relation_evaluate", "spatial objects and relation family", "topological relation outcome", "Results depend on geometry, CRS, precision and boundary model."),
    ("temporal_relation_evaluate", "instants or intervals", "temporal relation outcome", "Clock ordering does not automatically establish causality."),
    ("causal_projection", "events plus causal witnesses", "partial happens-before relation", "Timestamp sort or correlation cannot supply missing causal witnesses."),
    ("log_append", "partition-local log", "new offset in that partition", "Offsets from different partitions are not globally comparable."),
    ("watermark_advance", "stream observations", "progress bound", "Watermark progress is not proof that all earlier events exist or effects completed."),
    ("window_assign", "timestamped occurrences", "one or more window memberships", "Window membership is not source, processing or causal order."),
    ("render_layer", "scene items", "paint/layer order", "Visual stacking does not define data rank, reading order or business priority."),
    ("reference_follow", "resource graph and reference", "resolved endpoint or refusal", "URI/path structure is not hierarchy or authority."),
    ("allocation_partition", "population and allocation rule", "exclusive or overlapping memberships", "Configuration order does not establish assignment precedence."),
    ("graph_encode_decode", "semantic graph and carrier", "carrier or reconstructed graph", "Statement/buffer order must not become semantic edge order."),
]


def relation_kernel_rows() -> list[dict[str, Any]]:
    source_refs = [row["source_id"] for row in PRIMARY_SOURCES]
    return [
        {
            "record_kind": "order_topology_relation_kernel",
            "kernel_id": f"kernel.order-topology.{name}.v1",
            "input_relation": input_relation,
            "output_relation": output_relation,
            "required_coordinate_fields": ONTOLOGY["relation_coordinate"]["required_fields"],
            "negative_twin": negative,
            "bounded_primary_source_refs": source_refs,
            "applicability": "UNRESOLVED_PER_OPERATION_AND_RELATION",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for name, input_relation, output_relation, negative in KERNEL_DEFINITIONS
    ]


def route_for_facets(facets: tuple[str, ...]) -> str:
    return (
        "LEXICAL_DISCOVERY_PROJECTION_ONLY_RELATION_RESEARCH_REQUIRED"
        if facets
        else "NO_MEMBER_RELATION_EVIDENCE_VACANCY"
    )


def build() -> dict[str, Any]:
    rebase = build_member_rebase(
        axis="order_and_topology",
        dockets_path=P3O_DOCKETS,
        preclassifications_path=PRECLASSIFICATIONS,
        cluster_prefix="cluster.p3o.order-topology-rebase",
        cluster_route=route_for_facets,
    )
    clusters = [
        {
            "record_kind": "order_topology_member_research_cluster",
            **row,
            "required_next_evidence": [
                "authoritative endpoint-domain and relation inventory",
                "relation family and algebraic-property profile",
                "scope partition tie null and cycle policies",
                "path witness causality and representation status",
                "negative twins and exception proof",
            ],
            "member_applicability": "UNRESOLVED",
            "owner_decision": "UNRESOLVED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for row in rebase["clusters"]
    ]
    members = [
        {
            "record_kind": "order_topology_member_research_route",
            "route_id": f"route.p3o.order-topology.{row['library_ref'].removeprefix('library.').replace('.', '-').replace('_', '-')}",
            **row,
            "flat_projection_effect": "DISCOVERY_ROUTING_ONLY_NOT_APPLICABILITY",
            "required_endpoint_and_relation_inventory": "NOT_YET_SUPPLIED",
            "required_relation_coordinate_profiles": "NOT_YET_SUPPLIED",
            "required_path_and_scope_contracts": "NOT_YET_SUPPLIED",
            "required_preservation_or_change_kernels": "NOT_YET_SUPPLIED",
            "member_applicability": "UNRESOLVED",
            "owner_decision": "UNRESOLVED",
            "canonical_gaps_closed": 0,
            "status": "LOSSLESSLY_ROUTED_RESEARCH_OPEN",
            "completion_claim": False,
        }
        for row in rebase["members"]
    ]
    extensions = []
    for family_ref, docket in sorted(rebase["docket_by_family"].items()):
        short = family_ref.removeprefix("constitution.family.")
        extensions.append(
            {
                "record_kind": "order_topology_exact_contract_extension_candidate",
                "extension_id": f"extension.p3o.order-topology-coordinate.{short}.v1",
                "family_ref": family_ref,
                "family_evidence_docket_ref": docket["docket_id"],
                "represented_library_refs": docket["library_refs"],
                "represented_library_count": docket["library_count"],
                "required_record_kinds": [
                    "endpoint_domain_contract",
                    "relation_coordinate",
                    "relation_property_profile",
                    "path_contract",
                    "scope_and_partition_contract",
                    "relation_transformation_composition",
                    "member_exception",
                ],
                "required_owner_action": "ratify relation-positioned order/topology contracts or preserve an explicit vacancy",
                "owner_decision": "UNRESOLVED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )
    kernels = relation_kernel_rows()
    summary = {
        "program_id": "program.p3o.order-topology-coordinate-ontology-and-rebase.v1",
        "as_of": AS_OF,
        "axis": "order_and_topology",
        "primary_sources": len(PRIMARY_SOURCES),
        "relation_archetypes": len(RELATION_ARCHETYPES),
        "relation_kernels": len(kernels),
        "family_extension_candidates": len(extensions),
        "research_clusters": len(clusters),
        "target_member_routes": len(members),
        "routes_with_lexical_discovery_projection": rebase["lexical_member_count"],
        "routes_with_no_member_relation_evidence": rebase["vacancy_member_count"],
        "relation_coordinate_profiles_supplied": 0,
        "member_applicability_decisions": 0,
        "owner_decisions": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {
        "ontology": ONTOLOGY,
        "sources": PRIMARY_SOURCES,
        "archetypes": relation_archetype_rows(),
        "kernels": kernels,
        "clusters": clusters,
        "members": members,
        "extensions": extensions,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "order-topology-coordinate-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "relation-archetypes.jsonl": "".join(canonical(row) + "\n" for row in built["archetypes"]),
        "relation-kernels.jsonl": "".join(canonical(row) + "\n" for row in built["kernels"]),
        "member-research-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "member-relation-routes.jsonl": "".join(canonical(row) + "\n" for row in built["members"]),
        "extension-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["extensions"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.p3o.order-topology-coordinate-ontology-and-rebase.v1",
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
        "BUILD PASS P3O order/topology coordinate ontology: "
        f"{summary['relation_archetypes']} relation archetypes, {summary['relation_kernels']} kernels, "
        f"{summary['research_clusters']} clusters and {summary['target_member_routes']} exact routes; "
        "decisions and gap closure remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
