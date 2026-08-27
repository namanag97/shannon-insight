#!/usr/bin/env python3
"""Build the evidence-backed graph, network, ontology and knowledge semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
ATLAS = REGISTRY.parents[1]
AS_OF = "2026-08-27"
PRODUCTS = {"product.ontology_knowledge_model", "product.graph_analysis_workbench"}
AXES = ["semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
        "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
        "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
        "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
        "privacy_security_safety"]

NEIGHBORS = {
    "library.method_kernels.graph_methods",
    "library.qck.graph-semantics",
    "library.qck.graph-kernels",
    "library.qck.query-types",
    "library.qck.query-receipts",
    "library.persistence.snapshot_graph",
    "library.predictive.graph_sampling",
    "library.predictive.graph_models",
    "library.predictive.graph_message_passing",
    "library.method_kernels.causal_graph_identification",
    "library.method_kernels.process_temporal_graph_projection",
    "library.method_kernels.document_content_graph",
    "library.spatial_network.profile.compiler",
    "library.spatial_network.route_accessibility.evaluator",
    "library.pipeline.graph_algebra",
    "library.pipeline.graph_validator",
    "library.lpe.canonical-rdf",
    "library.lpe.provenance-assertion",
    "library.telemetry.trace_graph",
    "library.spt.relationship_graph",
    "library.gmo.knowledge_graph",
    "library.cbv.visual_encoding",
    "library.cbv.interaction_reducer",
}

VACANCIES = [
    ("library.graph.semantic-profile-contract", "Directedness, multiplicity, self-loop, label/property, weight, temporal and uncertainty semantics need one explicit profile."),
    ("library.graph.occurrence-snapshot-identity", "Graph occurrence, logical graph, snapshot, edition, projection and view identity must be independently addressable."),
    ("library.graph.projection-contract", "Source entities/relations need an explicit loss-bearing projection into nodes, edges, properties and time."),
    ("library.graph.algorithm-plan", "A compiled graph analysis needs method, objective, parameters, randomness, approximation, backend and budget identity."),
    ("library.graph.result-evidence-receipt", "Graph results need input snapshot, semantic profile, plan, attempts, convergence and limitations bound into evidence."),
    ("library.graph.dynamic-temporal-algebra", "Event-time, valid-time, interval, evolving-edge and snapshot-sequence graph semantics need a shared algebra."),
    ("library.graph.hypergraph-algebra", "N-ary hyperedges and incidence structures cannot be silently reduced to ordinary binary edges."),
    ("library.graph.benchmark-workload-identity", "Benchmark dataset, generator, algorithm, scale, validation and environment editions need portable identity."),
    ("library.graph.assertion-status-provenance", "Asserted, quoted, inferred, hypothesized, retracted and source-observed knowledge statements need separate status/provenance."),
    ("library.graph.analysis-workspace-lifecycle", "Graph/network analysis requires an independently adoptable workspace, run, result, comparison and publication lifecycle."),
    ("library.graph.model-mapping-acl", "Property graph, RDF dataset, relational, document and vertical graph projections need explicit non-lossless translations."),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-").replace("/", "-")


def product_rows() -> list[dict[str, Any]]:
    return load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")


def declared_product_libraries() -> set[str]:
    return {edge["concrete_library_ref"] for row in product_rows() if row["product_ref"] in PRODUCTS for edge in row["concrete_bindings"]}


LIBRARIES = sorted(declared_product_libraries() | NEIGHBORS)


def catalogs() -> dict[str, dict[str, Any]]:
    rows = []
    rows += load_jsonl(ATLAS / "universes/semantic_vocabulary_ontology_governance/sources.jsonl")
    rows += load_jsonl(ATLAS / "universes/method_kernels/sources.jsonl")
    rows += load_jsonl(ATLAS / "universes/query_compute_kernels/sources.jsonl")
    rows += load_jsonl(ATLAS / "universes/pipeline_dataflow/sources.jsonl")
    return {row["source_id"]: row for row in rows}


SOURCE_SELECTION = [
    ("rdf-concepts", "source.semantic-vocabulary.w3c.rdf11.concepts", "Defines RDF graph/dataset terms, node kinds, graph equality foundations and carrier-independent abstract syntax.", "RDF graphs are one graph model and do not define enterprise identity, truth or all network algorithms."),
    ("rdf-semantics", "source.semantic-vocabulary.w3c.rdf11.semantics", "Defines model-theoretic RDF entailment and semantic conditions.", "Formal entailment under an interpretation is not observed truth, business acceptance or causal proof."),
    ("owl-syntax", "source.semantic-vocabulary.w3c.owl2.syntax", "Defines ontology, axiom, entity, annotation, import and structural syntax concepts.", "OWL syntax does not establish consistency, entailment, factual truth or governance approval."),
    ("owl-direct", "source.semantic-vocabulary.w3c.owl2.direct", "Defines direct model-theoretic semantics and entailment for OWL 2 DL.", "Logical consequences hold only under the selected semantics and asserted axioms."),
    ("owl-profiles", "source.semantic-vocabulary.w3c.owl2.profiles", "Defines distinct OWL 2 EL, QL and RL profiles with different expressivity/computational properties.", "Profile membership is not consistency, implementation fitness or truth."),
    ("owl-conformance", "source.semantic-vocabulary.w3c.owl2.conformance", "Separates document, parser and reasoner conformance requirements and tests.", "Passing a test suite cannot prove untested behavior or domain correctness."),
    ("shacl", "source.semantic-vocabulary.w3c.shacl", "Defines shapes graphs, data graphs, focus/value nodes, constraints and validation reports.", "SHACL conformance is not ontology consistency, completeness, truth or authorization."),
    ("rdf-canon", "source.semantic-vocabulary.w3c.rdf-canon", "Defines deterministic RDF dataset canonicalization and canonical identifiers.", "Canonical bytes/digests do not prove semantic equivalence, truth or authorization."),
    ("sparql", "source.semantic-vocabulary.w3c.sparql11", "Defines RDF graph-pattern matching, paths, solution mappings and result modifiers.", "SPARQL query results do not establish ontology entailment outside the selected regime or business truth."),
    ("prov", "source.semantic-vocabulary.w3c.prov-o", "Defines entity, activity, agent and derivation structures for provenance assertions.", "Provenance is not correctness, exhaustive lineage or causal proof."),
    ("skos", "source.semantic-vocabulary.w3c.skos", "Defines concept schemes and lexical/semantic relations distinct from formal OWL axioms.", "SKOS broader/narrower is not automatically class subsumption or identity."),
    ("graphblas-c", "source.method_kernel.graphblas_c", "Defines generalized sparse matrix/vector operations over semiring structures for graph kernels.", "Primitive API conformance does not qualify a higher-level graph algorithm, result or performance target."),
    ("graphblas-cpp", "source.method_kernel.graphblas_cpp", "Defines C++ concepts, matrices, vectors, views and operators for GraphBLAS-style algorithms.", "Language binding support does not establish cross-provider numerical or performance equivalence."),
    ("suitesparse", "source.method_kernel.suitesparse_graphblas", "Documents one reference implementation's formats, operations and execution controls.", "One implementation is not the provider-neutral semantic authority or portability proof."),
    ("lagraph", "source.method_kernel.lagraph_paper", "Separates low-level GraphBLAS primitives from user-facing graph algorithms and validation.", "One algorithm library does not cover all graph models, methods or target environments."),
    ("networkx", "source.method_kernel.networkx_algorithms", "Provides a broad official taxonomy and reference interfaces for graph algorithms.", "Provider documentation is not a formal universal method contract or performance qualification."),
    ("igraph", "source.method_kernel.igraph_manual", "Provides an independent graph/network analysis implementation and method surface.", "Independent implementation existence does not prove semantic equivalence for every method/configuration."),
    ("temporal-ekg", "source.method_kernel.temporal_ekg", "Defines a bounded transformation from object-centric event logs to temporal event knowledge graphs.", "One projection does not define universal temporal graph or process semantics and may lose information."),
    ("gql", "source.qck.gql.standard", "Defines standardized property-graph structures and a data/query language edition.", "GQL does not own graph analytics, ontology meaning, storage layout or provider performance."),
    ("tarjan", "src.tarjan.scc", "Defines depth-first algorithms for strongly connected components and biconnected components.", "Algorithmic correctness assumes the declared graph model and does not imply domain interpretation."),
]

EXTRA_SOURCES = [
    ("rdf12", "RDF 1.2 Concepts and Abstract Data Model", "W3C", 2026, "candidate_recommendation", "https://www.w3.org/TR/rdf12-concepts/", "Adds triple terms, directional language strings and explicit RDF version labels to the abstract model.", "Candidate Recommendation status and conformance levels must remain explicit; publication is not final Recommendation."),
    ("shacl12", "SHACL 1.2 Core", "W3C", 2026, "working_draft", "https://www.w3.org/TR/shacl12-core/", "Evolves graph constraint semantics and validation structures against RDF 1.2.", "A working draft can change and passing available tests is not complete conformance."),
    ("pagerank", "The PageRank Citation Ranking: Bringing Order to the Web", "Stanford InfoLab", 1999, "primary_paper", "http://dbpubs.stanford.edu:8090/pub/1999-66", "Defines a random-walk/eigenvector ranking method over a directed link graph.", "PageRank scores depend on graph construction, damping, dangling handling and interpretation and are not universal importance."),
    ("brandes", "A Faster Algorithm for Betweenness Centrality", "Journal of Mathematical Sociology", 2001, "primary_paper", "https://snap.stanford.edu/class/cs224w-readings/brandes01centrality.pdf", "Defines efficient exact betweenness computation through dependency accumulation over shortest paths.", "Betweenness meaning depends on path, weight, direction and normalization semantics."),
    ("louvain", "Fast Unfolding of Communities in Large Networks", "Journal of Statistical Mechanics", 2008, "primary_paper", "https://arxiv.org/abs/0803.0476", "Defines greedy multilevel modularity optimization for community candidates.", "Louvain is heuristic, resolution-dependent, order/randomness-sensitive and may return disconnected communities."),
    ("leiden", "From Louvain to Leiden: Guaranteeing Well-Connected Communities", "Scientific Reports", 2019, "primary_paper", "https://www.nature.com/articles/s41598-019-41695-z", "Adds refinement and guarantees connected communities under declared quality/resolution semantics.", "Connectivity guarantees do not establish ground-truth communities or unique optimal partitions."),
    ("graphalytics", "LDBC Graphalytics Benchmark Specification", "Linked Data Benchmark Council", 2026, "official_benchmark", "https://ldbcouncil.org/ldbc_graphalytics_docs/graphalytics_spec.pdf", "Defines graph analytics workloads, datasets, validation and benchmark reporting.", "Benchmark success is workload/environment scoped and not general implementation fitness."),
]


def sources() -> list[dict[str, Any]]:
    catalog = catalogs()
    result = []
    for alias, registry_ref, claim, limit in SOURCE_SELECTION:
        row = catalog[registry_ref]
        result.append({"source_id": f"source.graph.{alias}", "source_registry_ref": registry_ref,
                       "title": row["title"], "publisher": row.get("publisher", "UNKNOWN"),
                       "year": row.get("publication_year"), "source_kind": row.get("source_kind", row.get("kind", "primary_or_official")),
                       "url": row["url"], "supported_claim": claim, "authority_limit": limit,
                       "primary_or_official": True, "status": "INDEPENDENTLY_REBOUNDED_PRIMARY_OR_OFFICIAL"})
    result.extend({"source_id": f"source.graph.{alias}", "source_registry_ref": None, "title": title,
                   "publisher": publisher, "year": year, "source_kind": kind, "url": url,
                   "supported_claim": claim, "authority_limit": limit, "primary_or_official": True,
                   "status": "INDEPENDENTLY_RESEARCHED_PRIMARY_OR_OFFICIAL"}
                  for alias, title, publisher, year, kind, url, claim, limit in EXTRA_SOURCES)
    return sorted(result, key=lambda row: row["source_id"])


MODULE_ROWS = [
    ("graph-occurrence", "Which graph occurrence, snapshot, edition, projection and view is being analyzed?", "graph identity aggregate", ["rdf-concepts", "gql"], []),
    ("graph-semantic-profile", "Which directedness, multiplicity, self-loop, label/property, weight, time and uncertainty semantics apply?", "graph semantic profile", ["gql", "networkx"], ["graph-occurrence"]),
    ("node-edge-identity", "What identifies nodes, edges and properties, and which equality/canonicalization relations are legal?", "typed identity algebra", ["rdf-concepts", "rdf-canon", "gql"], ["graph-semantic-profile"]),
    ("property-graph", "Which labels, properties, paths and graph collections define a property-graph edition?", "property graph model", ["gql"], ["node-edge-identity"]),
    ("rdf-graph-dataset", "Which triples, terms, named/default graphs and dataset semantics define an RDF graph occurrence?", "RDF abstract model", ["rdf-concepts", "rdf-semantics"], ["node-edge-identity"]),
    ("hypergraph-incidence", "Which n-ary hyperedge/incidence semantics apply without lossy binary reification?", "hypergraph algebra", ["networkx"], ["node-edge-identity"]),
    ("multiplex-multilayer", "Which layer, edge-kind and inter-layer relation semantics distinguish multiplex graphs?", "layered graph profile", ["networkx", "igraph"], ["graph-semantic-profile"]),
    ("temporal-dynamic-graph", "Which event/valid time, interval, evolving edge and snapshot-sequence semantics apply?", "temporal graph algebra", ["temporal-ekg"], ["graph-occurrence"]),
    ("graph-projection", "How are source entities/relations projected into graph elements and what identity, cardinality and evidence are lost?", "loss-bearing ACL", ["prov", "temporal-ekg"], ["graph-semantic-profile"]),
    ("subgraph-view", "Which induced, edge-induced, filtered, sampled or materialized subgraph/view semantics apply?", "graph view algebra", ["networkx", "gql"], ["graph-occurrence"]),
    ("walk-trail-path", "Which repeated-node/edge, direction, label, length and weight rules distinguish walks, trails and paths?", "path algebra", ["gql", "networkx"], ["graph-semantic-profile"]),
    ("traversal-reachability", "Which start set, neighbor order, direction, depth, visit and termination semantics define traversal/reachability?", "traversal algebra", ["networkx", "graphblas-c"], ["walk-trail-path"]),
    ("shortest-path", "Which weight algebra, negative-edge/cycle and tie semantics define a shortest path result?", "path optimization algebra", ["networkx", "graphblas-c"], ["walk-trail-path"]),
    ("connectivity-components", "Which weak, strong, biconnected, articulation, bridge and component semantics apply?", "connectivity algebra", ["tarjan", "networkx"], ["traversal-reachability"]),
    ("centrality-ranking", "Which degree, path, spectral, flow or random-walk importance quantity is being estimated?", "centrality measure family", ["pagerank", "brandes", "networkx"], ["shortest-path"]),
    ("community-partition", "Which objective, resolution, overlap, hierarchy, randomness and connectivity guarantees define a community result?", "partition/objective algebra", ["louvain", "leiden"], ["graph-semantic-profile"]),
    ("cuts-flows-cores", "Which capacity, flow conservation, cut, conductance, k-core and decomposition laws apply?", "flow/cut/decomposition algebra", ["networkx", "igraph"], ["graph-semantic-profile"]),
    ("matching-assignment", "Which bipartite/general matching, cardinality/weight objective and unmatched semantics apply?", "matching algebra", ["networkx"], ["graph-semantic-profile"]),
    ("motif-subgraph", "Which pattern identity, inducedness, automorphism and exact/sampled counting semantics apply?", "motif/subgraph algebra", ["networkx", "igraph"], ["graph-semantic-profile"]),
    ("isomorphism-similarity", "Which exact isomorphism, edit, kernel or structural similarity relation applies?", "graph comparison algebra", ["networkx", "igraph"], ["node-edge-identity"]),
    ("structural-link-prediction", "Which candidate universe, structural score, temporal cut and leakage-safe evaluation define link prediction?", "non-authoritative scoring", ["networkx"], ["graph-occurrence"]),
    ("graph-sampling", "Which node/edge/walk/subgraph sampling design and inclusion probabilities define a sample?", "sampling design", ["networkx"], ["graph-occurrence"]),
    ("semiring-kernel", "Which carrier, additive/multiplicative operators, identities, masks and algebraic laws lower an algorithm?", "semiring sparse algebra", ["graphblas-c", "graphblas-cpp"], ["graph-semantic-profile"]),
    ("matrix-representation", "Which sparse matrix/vector representation preserves node/edge semantics and duplicate reduction?", "representation ACL", ["graphblas-c", "suitesparse"], ["semiring-kernel"]),
    ("algorithm-plan", "Which method, objective, parameters, randomness, approximation, backend and budget form an executable plan?", "compiled method plan", ["lagraph", "graphalytics"], ["semiring-kernel"]),
    ("algorithm-result", "Which result identity, convergence, approximation, residual, witness and limitation semantics apply?", "typed result aggregate", ["lagraph", "graphalytics"], ["algorithm-plan"]),
    ("graph-query", "Which graph pattern/path/query semantics are imported without owning physical execution or storage?", "query ACL", ["gql", "sparql"], ["property-graph", "rdf-graph-dataset"]),
    ("graph-storage-snapshot", "Which physical graph snapshot/index/storage identity is imported without defining logical graph meaning?", "storage ACL", ["gql", "rdf-concepts"], ["graph-occurrence"]),
    ("ontology-identity-imports", "Which ontology IRI, version IRI, document location, registry occurrence and import closure apply?", "ontology identity aggregate", ["owl-syntax"], ["rdf-graph-dataset"]),
    ("axiom-logic-profile", "Which annotations, axioms, logic/profile and expressivity restrictions apply?", "axiom/profile algebra", ["owl-syntax", "owl-profiles"], ["ontology-identity-imports"]),
    ("reasoning-entailment", "Which semantics, asserted axioms, import closure, entailment regime and resource bounds produce consequences?", "reasoning service", ["owl-direct", "owl-profiles"], ["axiom-logic-profile"]),
    ("consistency-classification-realization", "Which consistency, satisfiability, classification and realization questions and completeness guarantees apply?", "reasoner method family", ["owl-direct", "owl-conformance"], ["reasoning-entailment"]),
    ("shape-validation", "Which shapes/data graph, focus/value nodes, severity and validation-report semantics apply?", "constraint validation", ["shacl"], ["rdf-graph-dataset"]),
    ("ontology-mapping", "Which mapping relation—lexical, subsumption, equivalence, rule or transform—is asserted with what authority?", "mapping aggregate", ["owl-direct", "skos"], ["axiom-logic-profile"]),
    ("knowledge-assertion-status", "Which statements are asserted, quoted, inferred, hypothesized, retracted or source-observed?", "assertion status algebra", ["rdf12", "prov"], ["reasoning-entailment"]),
    ("knowledge-graph-release", "Which immutable graph cut, ontology editions, assertion statuses, provenance and policy form a release?", "knowledge release aggregate", ["rdf-canon", "prov"], ["knowledge-assertion-status"]),
    ("canonicalization-digest", "Which syntactic canonicalization/digest relation applies without claiming semantic equivalence?", "canonical carrier identity", ["rdf-canon"], ["rdf-graph-dataset"]),
    ("provenance-evidence", "Which sources, transformations, algorithm plans, attempts and claims support a graph result/release?", "evidence bundle", ["prov", "graphalytics"], ["algorithm-result"]),
    ("benchmark-conformance", "Which benchmark workload, dataset/generator, scale, validation and environment scope a performance claim?", "benchmark receipt", ["graphalytics", "owl-conformance"], ["algorithm-result"]),
    ("graph-visualization-interaction", "Which graph layout/visual interaction is imported without changing graph or analytical meaning?", "presentation ACL", ["networkx"], ["algorithm-result"]),
    ("predictive-graph-model-acl", "Which graph feature/model/message-passing prediction is imported without absorbing predictive lifecycle/assurance?", "predictive ACL", ["networkx"], ["graph-occurrence"]),
    ("causal-graph-acl", "Which causal DAG/SCM semantics are imported without treating ordinary graph paths as causal effects?", "causal ACL", ["networkx"], ["graph-occurrence"]),
    ("spatial-network-acl", "Which spatial topology, impedance, turn/access and routing semantics are imported?", "spatial-network ACL", ["networkx"], ["graph-occurrence"]),
    ("process-event-graph-acl", "Which event/object/process projection semantics and losses are imported?", "process graph ACL", ["temporal-ekg"], ["graph-projection"]),
    ("vertical-relationship-graph-acl", "Which domain relationship meanings and authority remain in a vertical/application context?", "vertical ACL", ["prov"], ["graph-projection"]),
    ("workspace-run-lifecycle", "Which analysis workspace, run, comparison, review and publication states form a product lifecycle?", "analysis lifecycle", ["networkx", "graphalytics"], ["algorithm-plan"]),
    ("decision-effect-handoff", "Which bounded finding/proposal is handed off without authorizing a decision, graph mutation or business effect?", "authority ACL", ["prov"], ["provenance-evidence"]),
    ("product-boundary-ontology", "What is owned by ontology/knowledge-model governance rather than graph analysis/query/storage?", "product boundary", ["owl-syntax", "shacl"], ["knowledge-graph-release"]),
    ("product-boundary-graph-analysis", "What independently adoptable graph/network analysis workspace and run lifecycle belongs to the retained workbench without transferring method meaning or external authority into the product?", "product boundary", ["networkx", "igraph", "graphalytics"], ["workspace-run-lifecycle"]),
]


def modules() -> list[dict[str, Any]]:
    return [{"module_id": f"module.graph.{key}", "owned_question": question, "formalism": formalism,
             "source_refs": sorted(f"source.graph.{ref}" for ref in source_refs),
             "dependency_refs": sorted(f"module.graph.{ref}" for ref in deps),
             "authority_limit": "A graph structure, algorithm result, entailment or conformance report does not establish domain truth, causality, identity, policy, product ownership or effect authority.",
             "research_status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED"}
            for key, question, formalism, source_refs, deps in MODULE_ROWS]


LAW_STATEMENTS = [
    "Graph carrier is not logical graph; serialization, storage layout and logical graph semantics remain distinct.",
    "Node identity is not label, property equality, row identity, RDF term equality or business-entity identity.",
    "Edge identity is not endpoint pair; parallel edges and edge occurrences may remain distinct.",
    "Walk, trail, simple path and shortest path are distinct result kinds.",
    "Reachability is not causality, authorization, dependency truth or business influence.",
    "A centrality score is not universal importance, authority, risk, influence or causal effect.",
    "A community is an objective/configuration-dependent partition candidate, not a natural or organizational truth.",
    "Modularity improvement does not prove globally optimal, stable or well-connected communities.",
    "A connected community is not a semantically coherent or authoritative group.",
    "Graph similarity is not identity, equivalence or substitutability.",
    "Structural link score is not a relationship assertion, fact or permission to create an edge.",
    "A sampled subgraph is not the population graph; inclusion and distortion evidence remain explicit.",
    "Matrix representation is not graph meaning; duplicate reduction and zero/absence semantics can lose information.",
    "Semiring selection changes algorithm meaning and cannot be inferred from numeric carrier types.",
    "Graph query result is not graph snapshot, analytical finding, knowledge assertion or source truth.",
    "Property graph, RDF dataset, hypergraph and relational projection are not losslessly interchangeable by default.",
    "Ontology IRI, version IRI, document location and registry occurrence are distinct identities.",
    "Annotation is not logical axiom, assertion, entailment or observed fact.",
    "Profile membership is not consistency, satisfiability, entailment, completeness or truth.",
    "Entailment is a consequence under explicit semantics and premises, not empirical or business truth.",
    "Ontology consistency is not SHACL conformance, dataset completeness or factual correctness.",
    "SHACL conformance is not ontology consistency, completeness or acceptance.",
    "Canonical RDF digest is not semantic equivalence, graph isomorphism under every model or truth.",
    "SKOS broader/narrower is not automatically OWL subclass/subsumption.",
    "Ontology mapping proposal is not identity, equivalence, accepted transform or authority transfer.",
    "Knowledge-graph assertion is not source observation; asserted, quoted, inferred, hypothesized and retracted statuses remain distinct.",
    "Knowledge-graph release is not graph database, graph query engine, graph analytics workspace or predictive model.",
    "Temporal graph snapshot is not event history; snapshot sequences may omit within-cut changes.",
    "Process graph, causal graph, spatial network, trace graph and vertical relationship graph are context specializations, not homonyms to merge.",
    "Graph layout and visualization do not change graph semantics or prove an analytical interpretation.",
    "Graph neural/message-passing output is a predictive result, not graph truth or ontology entailment.",
    "Benchmark conformance/performance is scoped to exact workload, data, environment and implementation.",
    "Algorithm completion is not convergence, correctness, determinism, portability or fitness.",
    "A model, heuristic or agent may propose a mapping, edge or interpretation but cannot acquire assertion or effect authority.",
    "Analytical finding is not decision, graph mutation or business effect authority.",
    "Ontology governance and graph/network analysis have distinct users, lifecycles, artifacts and operations and must not be one product by graph vocabulary alone.",
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.graph.{index:03d}", "statement": statement,
             "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0}
            for index, statement in enumerate(LAW_STATEMENTS, 1)]


METHOD_GROUPS = {
    "model_projection": ["directed_graph", "undirected_graph", "multigraph", "property_graph", "rdf_graph_dataset", "hypergraph", "multiplex_graph", "temporal_graph", "induced_subgraph", "edge_induced_subgraph", "graph_projection"],
    "traversal_reachability": ["breadth_first_search", "depth_first_search", "multi_source_traversal", "bounded_depth_traversal", "transitive_closure", "reachability_query", "topological_sort"],
    "paths": ["single_source_shortest_path", "all_pairs_shortest_path", "bidirectional_shortest_path", "k_shortest_paths", "all_simple_paths", "negative_cycle_detection", "widest_path", "minimum_mean_cycle"],
    "connectivity": ["weak_components", "strong_components", "biconnected_components", "articulation_points", "bridges", "condensation_graph", "minimum_vertex_cut", "minimum_edge_cut"],
    "centrality_ranking": ["degree_centrality", "closeness_centrality", "harmonic_centrality", "betweenness_centrality", "edge_betweenness", "eigenvector_centrality", "pagerank", "personalized_pagerank", "hits", "katz_centrality", "load_centrality"],
    "community_partition": ["modularity_evaluation", "louvain_partition", "leiden_partition", "label_propagation", "infomap_partition", "spectral_partition", "greedy_modularity", "overlapping_community", "community_comparison", "partition_stability"],
    "cuts_flows_cores": ["maximum_flow", "minimum_cut", "conductance", "k_core", "k_shell", "core_number", "densest_subgraph", "peeling_decomposition"],
    "matching_assignment": ["maximum_cardinality_matching", "maximum_weight_matching", "bipartite_matching", "minimum_weight_assignment", "edge_cover"],
    "motif_isomorphism": ["triangle_count", "clique_enumeration", "motif_count", "subgraph_isomorphism", "graph_isomorphism", "weisfeiler_leman_hash", "graph_edit_distance"],
    "link_similarity": ["common_neighbors", "jaccard_link_score", "adamic_adar", "preferential_attachment", "resource_allocation", "simrank", "structural_link_prediction"],
    "sampling_temporal": ["node_sampling", "edge_sampling", "random_walk_sampling", "snowball_sampling", "reservoir_edge_sampling", "temporal_reachability", "dynamic_components", "incremental_pagerank", "temporal_motif"],
    "ontology_reasoning": ["import_closure", "profile_check", "consistency_check", "satisfiability_check", "classification", "realization", "entailment_check", "explanation_justification", "shape_validation", "ontology_mapping", "knowledge_graph_release"],
    "algebra_execution": ["semiring_lowering", "masked_matrix_multiply", "sparse_matrix_vector", "graph_algorithm_plan", "cross_backend_conformance", "graphalytics_benchmark"],
}


def methods() -> list[dict[str, Any]]:
    source_by_group = {
        "model_projection": ["gql", "rdf-concepts", "networkx"], "traversal_reachability": ["networkx", "graphblas-c"],
        "paths": ["networkx", "graphblas-c"], "connectivity": ["tarjan", "networkx"],
        "centrality_ranking": ["pagerank", "brandes", "networkx"], "community_partition": ["louvain", "leiden", "igraph"],
        "cuts_flows_cores": ["networkx", "igraph"], "matching_assignment": ["networkx"],
        "motif_isomorphism": ["networkx", "igraph"], "link_similarity": ["networkx"],
        "sampling_temporal": ["networkx", "temporal-ekg"], "ontology_reasoning": ["owl-direct", "owl-conformance", "shacl"],
        "algebra_execution": ["graphblas-c", "lagraph", "graphalytics"],
    }
    return [{"method_type_id": f"method.graph.{group}.{name.replace('_', '-')}", "name": name.replace("_", " ").title(),
             "method_group": group, "source_refs": [f"source.graph.{ref}" for ref in source_by_group[group]],
             "selection_law": "Select only after binding the exact graph semantic profile, snapshot/projection, objective or question, parameters, randomness, approximation, resource budget and evidence obligations.",
             "status": "METHOD_CANDIDATE_UNRATIFIED"}
            for group, names in METHOD_GROUPS.items() for name in names]


EXPERT_ROWS = [
    ("tim-davis", "Timothy A. Davis", ["graphblas-c", "suitesparse", "lagraph"], ["Use semiring sparse algebra as a reusable kernel boundary.", "Separate primitive conformance from algorithm validation."], "Implementation leadership does not make one backend universally qualified."),
    ("jeremy-kepner", "Jeremy Kepner", ["graphblas-c"], ["Express graph algorithms over explicit algebraic structures.", "Make operator identities and zero/absence semantics visible."], "GraphBLAS mathematics does not select domain graph meaning."),
    ("aydın-buluc", "Aydın Buluç", ["graphblas-c", "lagraph"], ["Separate scalable sparse kernels from higher-level algorithms.", "Bind representation and parallel execution evidence independently."], "Parallel performance is target and workload scoped."),
    ("ulrik-brandes", "Ulrik Brandes", ["brandes"], ["Centrality names hide exact path/direction/normalization choices.", "Require witnesses and semantic profiles for rankings."], "Betweenness is one structural quantity, not universal importance."),
    ("mark-newman", "Mark Newman", ["louvain", "leiden"], ["Network measures and community objectives are model-dependent.", "Expose resolution and null-model choices."], "Network-science abstractions do not confer domain truth."),
    ("vincent-traag", "Vincent Traag", ["leiden"], ["Challenge popular heuristics with counterexamples and stronger guarantees.", "Keep quality function, resolution, randomness and connectivity explicit."], "Leiden communities are still objective-dependent candidates."),
    ("renaud-lambiotte", "Renaud Lambiotte", ["louvain"], ["Treat multilevel partitions and modularity as explicit optimization artifacts.", "Preserve hierarchy and resolution choices."], "Modularity heuristics do not yield unique ground truth."),
    ("lawrence-page", "Lawrence Page", ["pagerank"], ["Random-walk ranking requires graph construction, damping and dangling-node policy.", "Interpret scores only within the bounded model."], "PageRank does not measure every kind of importance or authority."),
    ("terry-winograd", "Terry Winograd", ["pagerank"], ["Link structure can support ranking when assumptions are explicit.", "Keep graph evidence separate from semantic endorsement."], "Citation/link ranking is not truth or general influence."),
    ("peter-patel-schneider", "Peter F. Patel-Schneider", ["owl-direct", "rdf-semantics"], ["Keep model-theoretic semantics and entailment regimes exact.", "Separate syntax, profiles, consistency and entailment."], "Logical consequence is conditional on premises and semantics."),
    ("ian-horrocks", "Ian Horrocks", ["owl-syntax", "owl-profiles"], ["Expose description-logic expressivity and computational profiles.", "Choose reasoning profiles deliberately rather than by ontology filename."], "OWL profile expertise does not establish domain factual truth."),
    ("boris-motik", "Boris Motik", ["owl-direct", "owl-profiles"], ["Compile inference only under named semantics and profile constraints.", "Make completeness/termination limits explicit."], "Reasoner results are scoped to exact ontology/import cuts."),
    ("deborah-mcguinness", "Deborah McGuinness", ["owl-syntax", "prov"], ["Represent provenance and explanation around knowledge claims.", "Keep ontology assertions distinct from source observations."], "Explanations do not automatically validate premises."),
    ("gregg-kellogg", "Gregg Kellogg", ["rdf-canon", "rdf12"], ["Version and canonicalization semantics are first-class compatibility decisions.", "Keep canonical carrier identity distinct from semantic equivalence."], "Draft/editor experience does not make RDF 1.2 final."),
    ("olaf-hartig", "Olaf Hartig", ["rdf12", "temporal-ekg"], ["Model statement-level relationships and temporal graph projections explicitly.", "Preserve projection losses and graph-version semantics."], "Temporal EKG results are bounded to the proposed transformation."),
    ("andy-seaborne", "Andy Seaborne", ["sparql", "rdf12"], ["Separate RDF graph model from graph-pattern query evaluation.", "Bind dataset and entailment regime for every query."], "SPARQL expertise does not define property-graph or network analytics semantics."),
    ("ldbc-graphalytics", "LDBC Graphalytics team", ["graphalytics"], ["Benchmark graph algorithms with exact datasets, scale factors, validation and environments.", "Keep workload performance evidence scoped and replayable."], "Benchmark-team specifications do not establish universal provider fitness."),
    ("network-library-maintainers", "NetworkX and igraph maintainer communities", ["networkx", "igraph"], ["Preserve a broad taxonomy of graph methods behind explicit graph semantics.", "Expose algorithm-specific parameters, result shapes and failure limits."], "Reference-library interfaces are not universal semantic or performance standards."),
    ("graphblas-forum", "GraphBLAS Forum", ["graphblas-c", "graphblas-cpp"], ["Standardize primitive operators and error behavior across implementations.", "Retain higher-level algorithm and target qualification gates."], "API conformance is not algorithm fitness or portability proof."),
    ("w3c-rdf-sparql", "W3C RDF and SPARQL Working Groups", ["rdf-concepts", "rdf12", "sparql", "shacl12"], ["Edition graph/data/query semantics explicitly.", "Distinguish Recommendation, Candidate Recommendation and Working Draft maturity."], "Working-group documents are authoritative only within their status and scope."),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.graph.{key}", "name": name,
             "source_refs": [f"source.graph.{ref}" for ref in refs],
             "lessons_for_composable_platform": lessons, "authority_limit": limit,
             "status": "LEARNING_PROFILE_NOT_AUTHORITY"}
            for key, name, refs, lessons, limit in EXPERT_ROWS]


INNOVATIONS = [
    ("graphblas-2", 2021, "GraphBLAS 2.x matured a provider-neutral semiring sparse-kernel interface.", ["graphblas-c"]),
    ("lagraph-layer", 2021, "LAGraph made the boundary between primitive GraphBLAS operations and user-facing graph algorithms explicit.", ["lagraph", "graphblas-c"]),
    ("rdf-canonicalization", 2024, "RDF Dataset Canonicalization standardized digestable canonical dataset representations.", ["rdf-canon"]),
    ("gql-2024", 2024, "ISO/IEC 39075 standardized property-graph structures and a portable graph query language.", ["gql"]),
    ("rdf12-triple-terms", 2026, "RDF 1.2 Candidate Recommendation introduced triple terms and explicit version/conformance labels.", ["rdf12"]),
    ("shacl12-family", 2026, "SHACL 1.2 drafts split core, SPARQL, rules, node expressions, UI and profiling surfaces.", ["shacl12"]),
    ("temporal-event-knowledge-graph", 2024, "Temporal EKG research made OCEL-to-temporal-graph projection and entity snapshots explicit.", ["temporal-ekg"]),
    ("graphblas-cpp-1", 2023, "GraphBLAS C++ 1.0 exposed language-level concepts, views and operators over the algebraic model.", ["graphblas-cpp"]),
    ("graphalytics-evolution", 2026, "The LDBC Graphalytics specification continued portable workload, validation and reporting contracts for graph analytics.", ["graphalytics"]),
    ("leiden-adoption-boundary", 2021, "Independent graph libraries increasingly exposed Leiden alongside Louvain, carrying stronger connectivity guarantees into practice.", ["leiden", "igraph"]),
]


def innovations() -> list[dict[str, Any]]:
    return [{"innovation_id": f"innovation.graph.{key}", "year": year, "summary": summary,
             "source_refs": [f"source.graph.{ref}" for ref in refs], "ai_or_llm_dependency": False,
             "authority_limit": "A recent standard, research result or implementation milestone does not prove universal adoption, semantic ownership, provider qualification or product readiness.",
             "status": "RECENT_MECHANISM_NOT_ADOPTION_OR_BOUNDARY_PROOF"}
            for key, year, summary, refs in INNOVATIONS]


AXIS_QUESTIONS = {
    "semantic_object": "Which logical graph, occurrence, snapshot, projection, ontology, algorithm plan, result or knowledge release may this library own?",
    "semantic_role": "Which node/edge/property, assertion/premise/consequence, input/output/witness and provider/evaluator role applies?",
    "identity_and_equality": "Which graph/node/edge/term/axiom/result identities and equality, isomorphism, canonicalization or mapping relations apply?",
    "grain_and_cardinality": "What node/edge multiplicity, path cardinality, match multiplicity, partition coverage and result grain apply?",
    "state_and_change": "Which graph snapshot, ontology edition, mapping, run, result, review and release transitions are legal?",
    "time": "Which event, valid, transaction, snapshot, interval, dynamic-update and recording times apply?",
    "order_and_topology": "Which direction, adjacency, incidence, reachability, path, hierarchy, import and derivation relations apply?",
    "partiality_and_uncertainty": "How are absent/zero edges, unknown properties, incomplete traversal, approximation, nondeterminism, nonconvergence and ambiguous mappings represented?",
    "authority_and_trust": "Who may assert/retract knowledge, approve ontologies/mappings/releases and interpret or act on graph findings?",
    "effect_boundary": "Which operations are pure queries/findings/proposals and which request graph mutation, publication, notification or business effects?",
    "representation": "Which property/RDF/hypergraph/matrix/query/result carrier editions apply and what translation losses are disclosed?",
    "composition_algebra": "Which path, semiring, traversal, partition, entailment, mapping and result-composition laws apply?",
    "compatibility_and_evolution": "Which graph/model/ontology/query/algorithm changes preserve replay and which require migration/revalidation?",
    "resources_and_failure": "Which memory, work, frontier, iteration, convergence, timeout, spill and cancellation budgets and total failures apply?",
    "evidence_and_conformance": "Which snapshot, profile, plan, witness, test, benchmark and provenance evidence supports each scoped result?",
    "privacy_security_safety": "Which relationship sensitivity, inference leakage, graph poisoning, traversal authorization, disclosure and harmful-action constraints apply?",
}


def binding_modules(ref: str) -> list[str]:
    result = set()
    suffix = ref.rsplit(".", 1)[-1].replace("_", "-")
    direct_map = {
        "axiom-profile": ["axiom-logic-profile"], "identity-import-closure": ["ontology-identity-imports"],
        "knowledge-graph-release": ["knowledge-graph-release"], "ontology-mapping": ["ontology-mapping"],
        "reasoning-entailment": ["reasoning-entailment", "consistency-classification-realization"],
        "shape-validation": ["shape-validation"],
    }
    result.update(direct_map.get(suffix, []))
    rules = [
        (("graph_semantics", "graph-semantics"), ["graph-semantic-profile", "node-edge-identity"]),
        (("graph_methods",), ["algorithm-plan", "algorithm-result"]),
        (("traversal_path",), ["traversal-reachability", "shortest-path", "walk-trail-path"]),
        (("centrality",), ["centrality-ranking"]), (("community",), ["community-partition"]),
        (("semiring", "graph-kernels"), ["semiring-kernel", "matrix-representation"]),
        (("query-types", "query-receipts"), ["graph-query", "algorithm-result"]),
        (("snapshot_graph",), ["graph-storage-snapshot", "graph-occurrence"]),
        (("graph_sampling",), ["graph-sampling"]),
        (("graph_models", "graph_message_passing"), ["predictive-graph-model-acl"]),
        (("causal_graph",), ["causal-graph-acl"]), (("process_temporal_graph",), ["process-event-graph-acl"]),
        (("document_content_graph",), ["vertical-relationship-graph-acl"]),
        (("spatial_network",), ["spatial-network-acl"]),
        (("pipeline.graph",), ["graph-projection"]),
        (("canonical-rdf",), ["canonicalization-digest", "rdf-graph-dataset"]),
        (("provenance-assertion",), ["provenance-evidence", "knowledge-assertion-status"]),
        (("trace_graph", "relationship_graph"), ["vertical-relationship-graph-acl"]),
        (("gmo.knowledge_graph",), ["knowledge-graph-release", "product-boundary-ontology"]),
        (("visual_encoding", "interaction_reducer"), ["graph-visualization-interaction"]),
    ]
    for needles, adds in rules:
        if any(needle in ref for needle in needles): result.update(adds)
    assert result, ref
    return sorted(f"module.graph.{name}" for name in result)


def boundary_findings() -> list[dict[str, Any]]:
    direct = declared_product_libraries()
    graph_workbench_refs = sorted(
        ref for ref in direct
        if ref.startswith("library.method_kernels.graph")
    )
    rows = [
        {"finding_id": "finding.graph.ontology-product.v1", "library_refs": sorted(direct), "current_product_refs": ["product.ontology_knowledge_model"], "candidate_disposition": "RETAIN_ONTOLOGY_KNOWLEDGE_MODEL_GOVERNANCE_PRODUCT_WITH_SIX_DECLARED_LIBRARIES", "reason": "Ontology identity/imports, axiom profiles, reasoning, shapes, mappings and governed knowledge releases share authority/lifecycle but do not own graph analytics/query/storage.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.graph.analysis-product-boundary.v1", "library_refs": graph_workbench_refs, "excluded_library_refs": ["library.method_kernels.graph_methods"], "current_product_refs": ["product.graph_analysis_workbench"], "candidate_disposition": "RETAIN_GRAPH_ANALYSIS_WORKBENCH_WITH_METHOD_IMPORTS_AND_EXPLICIT_OWNER_SEAMS", "reason": "Workspace, run, comparison, evidence, review, publication and exit form an independently adoptable analyst lifecycle distinct from ontology governance. Exact graph method libraries are imported without transferring method meaning into the product; the legacy graph-method facade remains excluded.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.graph.query-storage-seam.v1", "library_refs": sorted(ref for ref in NEIGHBORS if ref.startswith("library.qck.") or ref.startswith("library.persistence.")), "current_product_refs": [], "candidate_disposition": "IMPORT_GRAPH_QUERY_AND_STORAGE_WITHOUT_REOWNING_LOGICAL_ANALYSIS_OR_KNOWLEDGE_AUTHORITY", "reason": "GQL/SPARQL execution, graph kernels and physical snapshots are provider/runtime seams, not the analysis or ontology product.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.graph.predictive-seam.v1", "library_refs": sorted(ref for ref in NEIGHBORS if ref.startswith("library.predictive.")), "current_product_refs": [], "candidate_disposition": "KEEP_GRAPH_PREDICTIVE_MODELS_AND_MESSAGE_PASSING_IN_PREDICTIVE_MODEL_LIFECYCLE", "reason": "Graph features/models may consume graph contracts but training/scoring/assurance remain predictive-product ownership.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.graph.context-specializations.v1", "library_refs": sorted(ref for ref in NEIGHBORS if any(part in ref for part in ["causal_graph", "process_temporal_graph", "document_content_graph", "spatial_network", "trace_graph", "relationship_graph", "pipeline.graph"])), "current_product_refs": [], "candidate_disposition": "RETAIN_CAUSAL_PROCESS_DOCUMENT_SPATIAL_TRACE_PIPELINE_AND_VERTICAL_GRAPH_CONTEXT_SPECIALIZATIONS", "reason": "Shared graph vocabulary does not transfer domain identity, time, causality, policy or effect semantics.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.graph.knowledge-assertion-seam.v1", "library_refs": ["library.ontology_model.knowledge_graph_release", "library.lpe.provenance-assertion"], "current_product_refs": ["product.ontology_knowledge_model"], "candidate_disposition": "KNOWLEDGE_RELEASE_OWNS_ASSERTION_STATUS_PROVENANCE_AND_EDITION_NOT_SOURCE_TRUTH", "reason": "A release can govern asserted/inferred/quoted/retracted statements while preserving source and domain authority.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.graph.presentation-seam.v1", "library_refs": sorted(ref for ref in NEIGHBORS if ref.startswith("library.cbv.")), "current_product_refs": [], "candidate_disposition": "IMPORT_GRAPH_VISUALIZATION_AND_INTERACTION_WITHOUT_CHANGING_GRAPH_OR_RESULT_MEANING", "reason": "Layouts and interactions are presentation artifacts; analytical interpretation remains evidence-bound.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.graph.decision-effect-seam.v1", "library_refs": [], "current_product_refs": ["product.ontology_knowledge_model"], "candidate_disposition": "GRAPH_RESULT_ENTAILMENT_MAPPING_AND_ASSERTION_PROPOSALS_STOP_BEFORE_DECISION_AND_EFFECT_AUTHORITY", "reason": "Graph structure, algorithm scores and logical consequences cannot authorize identity merges, relationship assertions or business actions.", "owner_decision": "UNRATIFIED"},
    ]
    rows.extend({"finding_id": f"finding.graph.vacancy.{slug(ref)}.v1", "library_refs": [], "proposed_library_ref": ref,
                 "current_product_refs": [], "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED",
                 "reason": reason, "owner_decision": "UNRATIFIED"} for ref, reason in VACANCIES)
    return rows


def build() -> dict[str, Any]:
    ss, ms, ls, method_rows, expert_rows, innovation_rows = sources(), modules(), laws(), methods(), experts(), innovations()
    source_ids = {row["source_id"] for row in ss}; module_ids = {row["module_id"] for row in ms}
    assert all(set(row["source_refs"]) <= source_ids for row in ms + method_rows + expert_rows + innovation_rows)
    assert all(set(row["dependency_refs"]) <= module_ids for row in ms)
    contributions = {row["library_id"]: row for row in load_jsonl(REGISTRY / "library-contributions.jsonl")}
    assert set(LIBRARIES) <= contributions.keys()
    coord = {row["library_ref"]: row for row in load_jsonl(SEM / "library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact = {row["library_ref"]: row for row in load_jsonl(SEM / "p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    consumers = {ref: set() for ref in LIBRARIES}; subjects = {ref: set() for ref in LIBRARIES}
    for row in product_rows():
        for edge in row["concrete_bindings"]:
            ref = edge["concrete_library_ref"]
            if ref in consumers: consumers[ref].add(row["product_ref"]); subjects[ref].add(row["subject_ref"])
    targeted = {(row["axis"], row["library_ref"]): row for row in load_jsonl(SEM / "targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    module_by_id = {row["module_id"]: row for row in ms}; direct = declared_product_libraries()
    bindings, axes = [], []
    for ref in LIBRARIES:
        module_refs = binding_modules(ref)
        evidence_refs = sorted({source for mid in module_refs for source in module_by_id[mid]["source_refs"]})
        exact_row, coord_row = exact.get(ref), coord.get(ref); routed = bool(exact_row and coord_row)
        bindings.append({"record_kind": "graph_network_knowledge_library_semantic_binding_candidate",
                         "binding_id": f"binding.graph-semantic-slice.{slug(ref)}.v1", "library_ref": ref,
                         "library_name": contributions[ref]["name"], "semantic_module_refs": module_refs,
                         "evidence_refs": evidence_refs, "exact_contract_docket_ref": exact_row["docket_id"] if exact_row else None,
                         "coordinate_binding_docket_ref": coord_row["binding_docket_id"] if coord_row else None,
                         "downstream_contract_route": "ROUTED" if routed else "MISSING_P5_AND_COORDINATE_DOCKET_TYPED_VACANCY",
                         "downstream_subject_refs": sorted(subjects[ref]), "downstream_product_refs": sorted(consumers[ref]),
                         "boundary_disposition_candidate": "RETAIN_DECLARED_PRODUCT_DEPENDENCY_WITH_NARROW_OWNER" if ref in direct else "RETAIN_FORMALISM_OR_ACL_NEIGHBOR_WITH_EXPLICIT_OWNER_SEAM",
                         "compiler_binding": "REFUSED", "refusal_reasons": ([] if routed else ["DOWNSTREAM_CONTRACT_ROUTE_MISSING"]) + ["OWNER_RATIFICATION_MISSING", "MEMBER_AXIS_APPLICABILITY_UNRATIFIED", "EXACT_CONTRACT_UNSELECTED", "IMPLEMENTATIONS_UNQUALIFIED"], "completion_claim": False})
        for axis in AXES:
            target = targeted.get((axis, ref))
            axes.append({"record_kind": "graph_network_knowledge_library_axis_decision_candidate",
                         "decision_candidate_id": f"decision-candidate.graph-axis.{slug(ref)}.{axis.replace('_', '-')}.v1",
                         "library_ref": ref, "axis": axis, "semantic_module_refs": module_refs,
                         "coordinate_question": AXIS_QUESTIONS[axis], "applicability_candidate": "REQUIRED_EXPLICIT_PROFILE",
                         "evidence_refs": evidence_refs, "targeted_member_adjudication_occurrence_ref": target["occurrence_id"] if target else None,
                         "coordinate_answers": [], "member_applicability": "PROPOSED_OWNER_REVIEW_REQUIRED", "owner_decision": "UNRATIFIED",
                         "status": "EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER", "canonical_gaps_closed": 0, "completion_claim": False})
    findings = boundary_findings()
    context = {"record_kind": "bounded_context_candidate", "context_id": "context.graph-network-knowledge-semantic-slice.v1", "as_of": AS_OF,
               "vision": "How can exact graph structures, algorithms, ontology semantics and governed knowledge releases be composed without collapsing graph carrier, query/storage, network analysis, prediction, entailment, source truth or decision authority?",
               "inside": ["graph semantic profiles, identity, projection, paths, connectivity, centrality, communities, motifs, matching and comparison", "graph algorithm/algebra plans, results, benchmarks and evidence", "ontology identity/imports, axiom profiles, reasoning, shapes, mappings and knowledge releases", "typed ACLs to graph query/storage, prediction, specialized graphs, visualization and effects"],
               "outside": ["physical graph storage/query execution ownership", "predictive graph-model training/scoring/assurance", "causal, process, spatial, document, trace and vertical relationship truth", "source/entity identity and business relationship authority", "visualization ownership and business decisions/effects"],
               "product_boundary_candidates": [{"product_ref": "product.ontology_knowledge_model", "status": "RETAIN_UNRATIFIED"}, {"product_ref": "product.graph_analysis_workbench", "status": "RETAIN_SEPARATE_WORKBENCH_UNRATIFIED"}],
               "published_language": ["GraphSemanticProfile", "GraphOccurrence", "GraphSnapshot", "GraphProjection", "GraphAlgorithmPlan", "GraphResult", "GraphEvidenceReceipt", "OntologyEdition", "ImportClosure", "EntailmentResult", "ShapeValidationReport", "OntologyMapping", "KnowledgeAssertion", "KnowledgeGraphRelease"],
               "ratification": "WITHHELD", "completion_claim": False}
    summary = {"program_id": "program.graph-network-knowledge-semantic-slice.v1", "as_of": AS_OF,
               "primary_or_official_sources": len(ss), "semantic_modules": len(ms), "non_collapse_laws": len(ls),
               "method_types": len(method_rows), "expert_learning_profiles": len(expert_rows), "recent_non_llm_innovations": len(innovation_rows),
               "bound_libraries": len(bindings), "declared_product_libraries": len(direct), "formalism_and_acl_neighbor_libraries": len(NEIGHBORS),
               "candidate_new_products": 0, "candidate_new_library_vacancies": len(VACANCIES),
               "libraries_without_declared_product_consumer": sum(not consumers[ref] for ref in LIBRARIES),
               "missing_downstream_contract_routes": sum(row["downstream_contract_route"].startswith("MISSING") for row in bindings),
               "library_axis_decision_candidates": len(axes), "product_capability_boundary_findings": len(findings),
               "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0, "canonical_gaps_closed": 0, "completion_claim": False}
    return {"context": context, "sources": ss, "modules": ms, "laws": ls, "methods": method_rows, "experts": expert_rows,
            "innovations": innovation_rows, "libraries": bindings, "axes": axes, "findings": findings, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {"bounded-context.json": json.dumps(built["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
             "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
             "semantic-modules.jsonl": "".join(canonical(row) + "\n" for row in built["modules"]),
             "non-collapse-laws.jsonl": "".join(canonical(row) + "\n" for row in built["laws"]),
             "graph-method-taxonomy.jsonl": "".join(canonical(row) + "\n" for row in built["methods"]),
             "expert-learning-profiles.jsonl": "".join(canonical(row) + "\n" for row in built["experts"]),
             "innovation-records.jsonl": "".join(canonical(row) + "\n" for row in built["innovations"]),
             "library-semantic-bindings.jsonl": "".join(canonical(row) + "\n" for row in built["libraries"]),
             "library-axis-decision-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["axes"]),
             "product-capability-boundary-findings.jsonl": "".join(canonical(row) + "\n" for row in built["findings"]),
             "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n"}
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.graph-network-knowledge-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items(): (HERE / name).write_text(value)
    summary = build()["summary"]
    print(f"BUILD PASS graph/network/knowledge slice: {summary['semantic_modules']} modules, {summary['method_types']} methods, {summary['bound_libraries']} libraries and {summary['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__": raise SystemExit(main())
