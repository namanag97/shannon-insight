#!/usr/bin/env python3
"""Build the evidence-backed search, retrieval and metadata-discovery semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
PRODUCTS = {"product.search_index_service", "product.metadata_discovery"}
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

NEIGHBORS = {
    "library.candidate.lib.catalog-record", "library.candidate.lib.stac-catalog",
    "library.cbv.query_gateway", "library.cbv.semantic_query_types",
    "library.data_marketplace.discovery_ranking", "library.data_use_policy.decision_evaluation",
    "library.data_use_policy.obligation_protocol", "library.data_use_policy.request_context",
    "library.document.rendition.evaluator", "library.gmo.catalog_listing_contract",
    "library.gmo.discovery_query", "library.gmo.metadata_acquisition",
    "library.gmo.metadata_assertions", "library.gmo.privacy_purpose_binding",
    "library.lineage_repository.port", "library.lpe.lineage-core", "library.lpe.lineage-query",
    "library.mae.retrieval_contract", "library.method_kernels.document_classification_methods",
    "library.method_kernels.document_content_graph", "library.method_kernels.document_information_extraction",
    "library.method_kernels.document_layout_methods", "library.method_kernels.document_ocr_methods",
    "library.method_kernels.document_table_extraction", "library.method_kernels.spatial_methods",
    "library.method_kernels.spatial_reference_semantics", "library.ontology_model.axiom_profile",
    "library.ontology_model.ontology_mapping", "library.ontology_model.reasoning_entailment",
    "library.ontology_model.shape_validation", "library.persistence.catalog_contract",
    "library.persistence.probabilistic_index", "library.qck.query-binding",
    "library.qck.query-receipts", "library.qck.query-syntax", "library.qck.query-types",
    "library.qck.spatial-kernels", "library.schema_registry.artifact_profile",
    "library.schema_registry.subject_identity", "library.schema_registry.version_registry",
    "library.selection.facet.evaluator", "library.smf.fanout_analyzer",
    "library.smf.semantic_query_canonicalizer", "library.smf.semantic_query_gateway",
    "library.spt.privacy_vocabulary",
}

VACANCIES = [
    ("library.search.content_admission", "Content occurrence, representation, language, policy, source version and extraction evidence need an admission result."),
    ("library.search.index_schema", "Fields, types, stored/indexed/doc-values/vector roles, multiplicity and compatibility need an editioned schema."),
    ("library.search.analysis_chain", "Character filters, tokenizer, token filters, locale, synonyms and index/query asymmetry need an edition."),
    ("library.search.indexed_occurrence", "Source occurrence, extracted unit, indexed document, field, passage and vector entries need separate identities."),
    ("library.search.mutation_generation", "Adds, updates, tombstones, sequence/generation, acknowledgement and idempotency need a total mutation result."),
    ("library.search.visibility_cut", "Refresh/searcher/replica generation and exact included mutations need an explicit searchable cut."),
    ("library.search.query_contract", "Information need, query AST, fields, filters, locale, time, policy, budgets and desired result grain need a contract."),
    ("library.search.retrieval_ir", "Lexical, structured, spatial, vector and hybrid stages need a provider-neutral typed plan."),
    ("library.search.lexical_kernel", "Term, phrase, proximity, Boolean, fuzzy and fielded retrieval need explicit scoring and partiality semantics."),
    ("library.search.structured_filter", "Predicate, null/missing, multivalue, nested, temporal and spatial filter semantics need a total contract."),
    ("library.search.vector_metric_profile", "Vector dimension/type, embedding edition, distance/similarity, normalization and comparability need one profile."),
    ("library.search.ann_contract", "Index family, build/search parameters, recall target, filters, updates, determinism and resource budgets need a contract."),
    ("library.search.hybrid_fusion", "Candidate depths, score normalization or rank fusion, weights, tie breaks and truncation need an algebra."),
    ("library.search.ranking_profile", "Features, stages, models, business rules, diversity, freshness and tie breaks need an editioned profile."),
    ("library.search.result_page", "Visibility cut, candidates, scores, ranks, snippets, facets, partiality, provenance and next cursor need a result."),
    ("library.search.pagination_cursor", "Stable sort keys, point-in-time cut, direction, expiry and duplicate/omission behavior need a cursor."),
    ("library.search.explanation", "Per-stage matches, feature values, score contributions, filters and omissions need a redacted explanation."),
    ("library.search.relevance_judgment", "Topic, assessor, scale, document/passage, context, time and uncertainty need a judgment occurrence."),
    ("library.search.evaluation_corpus", "Corpus, topics, qrels, pooling, metrics, slices, significance and leakage controls need an edition."),
    ("library.search.approximation_receipt", "Exact baseline, sample, recall/latency/memory distribution, filters and index edition need evidence."),
    ("library.search.deletion_verification", "Tombstone, generations, replicas, caches, snapshots and verified disappearance scope need a result."),
    ("library.discovery.acquisition_occurrence", "Source endpoint, protocol, cursor, coverage, permissions, time and failures need one acquisition occurrence."),
    ("library.discovery.assertion_value", "Claimed value, subject, predicate, source, extraction method, confidence, validity and conflict need an assertion."),
    ("library.discovery.projection_edition", "Accepted assertions, conflict policy, vocabulary mapping and index publication need a projection edition."),
    ("library.discovery.federated_result", "Per-source query/coverage/latency, normalization, deduplication, merge and partial failures need a result."),
    ("library.discovery.freshness_coverage_ledger", "Expected scope, last attempted/seen/changed/visible times and blind spots need a ledger."),
    ("library.search.access_disclosure", "Authorization filtering, count/facet/snippet leakage, purpose and audit evidence need a disclosure contract."),
    ("library.search.semantic_diff", "Schema/analyzer/corpus/ranking/visibility editions need directional behavioral and result-set differences."),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def declared_product_libraries() -> set[str]:
    rows = load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")
    return {edge["concrete_library_ref"] for row in rows if row["product_ref"] in PRODUCTS for edge in row["concrete_bindings"]}


LIBRARIES = sorted(declared_product_libraries() | NEIGHBORS)


SOURCE_ROWS = [
    ("ir-book", "Introduction to Information Retrieval", "Manning, Raghavan and Schütze", 2008, "primary_textbook", "https://nlp.stanford.edu/IR-book/", "Defines inverted indexes, scoring, evaluation, classification, clustering and Web retrieval foundations.", "A textbook taxonomy does not establish product ownership or relevance authority."),
    ("vector-space", "A Vector Space Model for Automatic Indexing", "Gerard Salton, Anita Wong and C. S. Yang", 1975, "primary_paper", "https://doi.org/10.1145/361219.361220", "Defines vector-space representation and similarity for documents and queries.", "Vector-space similarity is not semantic equivalence or business relevance."),
    ("bm25", "The Probabilistic Relevance Framework: BM25 and Beyond", "Stephen Robertson and Hugo Zaragoza", 2009, "primary_monograph", "https://doi.org/10.1561/1500000019", "Defines probabilistic relevance foundations, BM25/BM25F and assumptions.", "BM25 scores are query/index/profile scoped and are not probabilities of relevance."),
    ("lm-ir", "A Language Modeling Approach to Information Retrieval", "Ponte and Croft", 1998, "primary_paper", "https://doi.org/10.1145/290941.291008", "Defines query-likelihood retrieval from document language models.", "Language-model likelihood is not calibrated user relevance or truth."),
    ("pagerank", "The Anatomy of a Large-Scale Hypertextual Web Search Engine", "Brin and Page", 1998, "primary_paper", "https://doi.org/10.1016/S0169-7552(98)00110-X", "Combines link analysis with text retrieval in Web search.", "Link authority is graph/profile scoped and not domain authority."),
    ("wand", "Efficient Query Evaluation Using a Two-Level Retrieval Process", "Broder et al.", 2003, "primary_paper", "https://doi.org/10.1145/956863.956944", "Defines WAND-style safe or bounded top-k pruning.", "Pruning correctness depends on score upper bounds and query semantics."),
    ("lucene", "Apache Lucene Core", "Apache Lucene", 2026, "official_documentation", "https://lucene.apache.org/core/", "Documents indexing, analyzers, queries, scoring and search APIs.", "Lucene behavior is implementation evidence, not a universal retrieval contract."),
    ("lucene-index", "Lucene IndexWriter", "Apache Lucene", 2026, "official_api_documentation", "https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/index/IndexWriter.html", "Defines document mutation, commits, deletion and index-writer behavior.", "Writer acceptance or commit does not necessarily establish application search visibility."),
    ("lucene-analysis", "Lucene Analysis Package", "Apache Lucene", 2026, "official_api_documentation", "https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/analysis/package-summary.html", "Defines reusable character filters, tokenizers and token filters.", "Token streams depend on analyzer edition, field, locale and index/query position."),
    ("lucene-vector", "Lucene KNN Vector Format", "Apache Lucene", 2026, "official_api_documentation", "https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/codecs/lucene99/Lucene99HnswVectorsFormat.html", "Documents HNSW vector indexing/search parameters and limits.", "Implementation defaults do not define portable ANN recall, filtering or update semantics."),
    ("elastic-refresh", "Elasticsearch Refresh Parameter", "Elastic", 2026, "official_documentation", "https://www.elastic.co/docs/reference/elasticsearch/rest-apis/refresh-parameter", "Distinguishes mutation processing from when changes become visible to search.", "Refresh visibility is scoped to shards/searchers and is not source truth or replica deletion proof."),
    ("elastic-delete", "Elasticsearch Delete By Query", "Elastic", 2026, "official_documentation", "https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-delete-by-query.html", "Documents snapshot-based deletion, conflicts, throttling, tasks and refresh behavior.", "Accepted deletion is not verified disappearance from every generation, cache or snapshot."),
    ("opensearch-analyzers", "OpenSearch Analyzers", "OpenSearch", 2026, "official_documentation", "https://docs.opensearch.org/latest/analyzers/", "Defines character filters, tokenizers, token filters and analyzer use.", "Index/search analyzer mismatch and synonym changes require explicit compatibility semantics."),
    ("opensearch-rrf", "OpenSearch Reciprocal Rank Fusion", "OpenSearch", 2026, "official_documentation", "https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/rrf/", "Defines rank-based fusion, depth, weights, explanations and shard effects.", "RRF scores are not comparable to component scores or across queries."),
    ("solr-facets", "Apache Solr JSON Facet API", "Apache Solr", 2026, "official_documentation", "https://solr.apache.org/guide/solr/latest/query-guide/json-facet-api.html", "Defines nested facets, buckets, metrics, sorting and refinement.", "Facet counts depend on visibility, domain, approximation and distributed refinement."),
    ("trec-qrels", "TREC Relevance Judgments", "NIST", 2026, "government_benchmark", "https://trec.nist.gov/data/reljudge_eng.html", "Defines topic/corpus-bound relevance judgments and pooling assumptions.", "Judgments are assessor, topic, time and pool scoped rather than universal truth."),
    ("trec-eval", "trec_eval", "NIST", 2026, "official_evaluation_tool", "https://github.com/usnistgov/trec_eval", "Implements standard retrieval effectiveness measures over runs and qrels.", "Metric output depends on corpus, topics, judgments, cutoffs and unjudged policy."),
    ("ndcg", "Cumulated Gain-Based Evaluation of IR Techniques", "Järvelin and Kekäläinen", 2002, "primary_paper", "https://doi.org/10.1145/582415.582418", "Defines graded cumulative gain and normalized discounted cumulative gain.", "nDCG requires an explicit gain/discount profile and judgment set."),
    ("rrf", "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods", "Cormack, Clarke and Büttcher", 2009, "primary_paper", "https://doi.org/10.1145/1571941.1572114", "Defines rank-only fusion across retrieval runs.", "Fusion depth and rank constant affect results; scores lose component magnitudes."),
    ("ltr", "From RankNet to LambdaRank to LambdaMART", "Christopher Burges", 2010, "primary_technical_report", "https://www.microsoft.com/en-us/research/publication/from-ranknet-to-lambdarank-to-lambdamart-an-overview/", "Explains pairwise/listwise learning-to-rank and LambdaMART.", "A ranking model imports external training, feature, model and approval lifecycles."),
    ("hnsw", "Efficient and Robust Approximate Nearest Neighbor Search Using HNSW", "Malkov and Yashunin", 2018, "primary_paper", "https://arxiv.org/abs/1603.09320", "Defines hierarchical navigable small-world graph ANN.", "Approximation, random construction, data order and parameters affect recall and resources."),
    ("pq", "Product Quantization for Nearest Neighbor Search", "Jégou, Douze and Schmid", 2011, "primary_paper", "https://doi.org/10.1109/TPAMI.2010.57", "Defines compact vector codes and asymmetric distance computation.", "Quantization introduces profile-specific distortion and candidate loss."),
    ("faiss", "Billion-Scale Similarity Search with GPUs", "Johnson, Douze and Jégou", 2019, "primary_paper", "https://arxiv.org/abs/1702.08734", "Presents exact/approximate vector indexes, quantization and GPU execution.", "A toolkit does not establish metric fitness, embedding meaning or portable recall."),
    ("diskann", "DiskANN: Fast Accurate Billion-point Nearest Neighbor Search", "Subramanya et al.", 2019, "primary_paper", "https://papers.nips.cc/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html", "Defines SSD-oriented graph ANN for large vector collections.", "Hardware/layout assumptions and build/search parameters bound results."),
    ("fresh-diskann", "FreshDiskANN: A Fast and Accurate Graph-Based ANN Index for Streaming Similarity Search", "Singh et al.", 2021, "primary_paper", "https://arxiv.org/abs/2105.09613", "Adds concurrent updates and consolidation to disk-based ANN.", "Freshness and recall remain generation-, workload- and parameter-scoped."),
    ("filtered-ann", "Filtered-DiskANN: Graph Algorithms for Approximate Nearest Neighbor Search with Filters", "Gollapudi et al.", 2023, "primary_paper", "https://dl.acm.org/doi/10.1145/3580305.3599546", "Integrates structured filters into graph ANN candidate search.", "Filter selectivity and label distributions change recall/latency and must be qualified."),
    ("beir", "BEIR: A Heterogeneous Benchmark for Zero-Shot Evaluation of IR Models", "Thakur et al.", 2021, "primary_benchmark_paper", "https://arxiv.org/abs/2104.08663", "Evaluates lexical, sparse, dense, late-interaction and reranking across heterogeneous tasks.", "Benchmark averages do not prove fitness on a target corpus, language or information need."),
    ("mteb", "MTEB: Massive Text Embedding Benchmark", "Muennighoff et al.", 2022, "primary_benchmark_paper", "https://arxiv.org/abs/2210.07316", "Evaluates embeddings across tasks, domains, languages and metrics.", "Embedding benchmark rank does not define target retrieval relevance or policy fitness."),
    ("colbertv2", "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction", "Santhanam et al.", 2022, "primary_paper", "https://arxiv.org/abs/2112.01488", "Defines token-level late interaction with compressed residual representations.", "Late-interaction models import model/data lifecycle and add index/storage semantics."),
    ("splade", "SPLADE v2", "Formal et al.", 2021, "primary_paper", "https://arxiv.org/abs/2109.10086", "Defines learned sparse lexical expansion for inverted-index retrieval.", "Learned sparse weights are model-edition outputs, not human-readable semantic truth."),
    ("dcat3", "Data Catalog Vocabulary Version 3", "W3C", 2024, "web_standard", "https://www.w3.org/TR/vocab-dcat-3/", "Distinguishes catalog, resource, dataset, distribution, service, series and catalog record with versioning.", "A metadata record describes a resource; it is not the resource or source truth."),
    ("dublin-core", "DCMI Metadata Terms", "Dublin Core Metadata Initiative", 2020, "metadata_standard", "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/", "Defines reusable descriptive metadata terms and ranges.", "Term use does not establish assertion authority, completeness or profile conformance."),
    ("skos", "SKOS Simple Knowledge Organization System", "W3C", 2009, "web_standard", "https://www.w3.org/TR/skos-reference/", "Defines concepts, labels, schemes, semantic relations and mappings.", "A thesaurus mapping is not equivalence, ontology entailment or source truth."),
    ("dqv", "Data on the Web Best Practices: Data Quality Vocabulary", "W3C", 2016, "web_standard", "https://www.w3.org/TR/vocab-dqv/", "Defines quality measurements, metrics, annotations and policies for datasets.", "Quality metadata is scoped evidence, not discovery completeness or certification."),
    ("prov", "PROV-O", "W3C", 2013, "web_standard", "https://www.w3.org/TR/prov-o/", "Defines entity/activity/agent provenance and derivation.", "Provenance does not make acquired metadata current, correct or authoritative."),
    ("ogc-records", "OGC API Records Part 1 Core 1.0", "OGC", 2025, "international_standard", "https://docs.ogc.org/is/20-004r1/20-004r1.html", "Defines Web APIs for metadata-record discovery and retrieval.", "Record API conformance does not prove federated completeness or resource fitness."),
    ("stac", "SpatioTemporal Asset Catalog Specification", "STAC", 2025, "community_specification", "https://github.com/radiantearth/stac-spec", "Defines catalogs, collections, items and assets for spatiotemporal resources.", "STAC metadata is a domain profile and does not replace generic resource identity or truth."),
    ("opensearch-spec", "OpenSearch 1.1 Description Document", "OASIS", 2011, "standard", "https://docs.oasis-open.org/search-ws/searchRetrieve/v1.0/os/part3-opensearch.html", "Defines description and query templates for federated search endpoints.", "Endpoint description does not normalize relevance scores, identity or partial failure."),
    ("rfc9110", "RFC 9110 HTTP Semantics", "IETF", 2022, "internet_standard", "https://www.rfc-editor.org/rfc/rfc9110", "Defines validators, conditional requests, caching semantics and representation metadata.", "HTTP freshness is not source, acquisition, index or discovery freshness by itself."),
    ("elastic-dls", "Elasticsearch Document and Field Level Security", "Elastic", 2026, "official_documentation", "https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/controlling-access-at-document-field-level", "Documents document/field filtering during search.", "Filtering must also cover counts, facets, snippets, caches and explanations to avoid disclosure."),
    ("jsonpath", "RFC 9535 JSONPath", "IETF", 2024, "internet_standard", "https://www.rfc-editor.org/rfc/rfc9535", "Defines selectors, node lists and normalized paths over JSON.", "Selector order/duplicates and node identity differ from ranked retrieval semantics."),
    ("sparql", "SPARQL 1.1 Query Language", "W3C", 2013, "web_standard", "https://www.w3.org/TR/sparql11-query/", "Defines graph-pattern matching, solution sequences, filters, grouping and federation.", "Graph query matching and entailment are distinct from ranked relevance retrieval."),
]


def sources() -> list[dict[str, Any]]:
    return sorted(({"source_id": f"source.search.{k}", "title": t, "publisher": p, "year": y,
                    "source_kind": kind, "url": url, "supported_claim": claim,
                    "authority_limit": limit, "primary_or_official": True,
                    "status": "INDEPENDENTLY_REVIEWED_SOURCE_CANDIDATE"}
                   for k, t, p, y, kind, url, claim, limit in SOURCE_ROWS), key=lambda r: r["source_id"])


MODULE_ROWS = [
    ("content-scope", "Which source corpus, content types, occurrences, languages, purpose and policy define searchable scope?", "content scope", ["ir-book"], []),
    ("content-admission", "Which source/version/representation/extraction/policy evidence admits a content occurrence?", "admission result", ["prov", "dcat3"], ["content-scope"]),
    ("document-identity", "How do source object, rendition, extracted unit, indexed document, field, passage and vector entry identities relate?", "identity map", ["dcat3", "ir-book"], ["content-admission"]),
    ("index-schema", "Which fields, types, multiplicity, storage, indexing, doc-values and vector roles define an index edition?", "index schema", ["lucene", "dcat3"], ["document-identity"]),
    ("analysis-chain", "Which character/token filters, tokenizer, language, stemming, stopwords and synonyms define terms?", "analyzer edition", ["lucene-analysis", "opensearch-analyzers"], ["index-schema"]),
    ("index-structures", "Which postings, dictionaries, doc values, BKD, graph/vector and compression structures realize retrieval?", "physical index profile", ["ir-book", "lucene"], ["analysis-chain"]),
    ("mutation", "Which add/update/delete occurrence, generation, idempotency and acknowledgement modify the index?", "mutation result", ["lucene-index", "elastic-delete"], ["index-structures"]),
    ("visibility", "Which exact mutation generation is visible through which searcher, shard and replica cut?", "visibility cut", ["elastic-refresh", "lucene-index"], ["mutation"]),
    ("query-contract", "Which information need, query syntax/AST, fields, filters, locale, time, policy and budgets are declared?", "query contract", ["ir-book", "jsonpath"], ["visibility"]),
    ("lexical-retrieval", "Which terms, Boolean clauses, phrase/proximity, fuzzy and field semantics produce lexical candidates?", "lexical candidate set", ["ir-book", "bm25"], ["query-contract", "analysis-chain"]),
    ("structured-retrieval", "Which filters, null/missing, nested/multivalue, range, temporal and spatial semantics constrain candidates?", "structured candidate set", ["jsonpath", "sparql"], ["query-contract"]),
    ("facet-aggregation", "Which domain, buckets, counts, metrics, approximation and distributed refinement produce facets?", "facet result", ["solr-facets"], ["structured-retrieval"]),
    ("vector-profile", "Which embedding edition, dimension/type, metric, normalization and query vector define similarity?", "vector metric profile", ["vector-space", "mteb"], ["query-contract"]),
    ("exact-neighbor", "Which exact k-nearest or radius neighbors follow under one metric and tie policy?", "exact vector result", ["faiss"], ["vector-profile"]),
    ("ann-index", "Which HNSW/IVF/PQ/disk graph edition and parameters produce approximate candidates?", "ANN candidate set", ["hnsw", "pq", "diskann"], ["vector-profile"]),
    ("filtered-ann", "Which pre/post/in-graph filtering semantics and selectivity evidence bound ANN recall?", "filtered ANN result", ["filtered-ann"], ["ann-index", "structured-retrieval"]),
    ("hybrid-fusion", "Which candidate depths, normalization/rank fusion, weights, truncation and ties combine retrieval stages?", "hybrid result", ["rrf", "opensearch-rrf"], ["lexical-retrieval", "filtered-ann"]),
    ("ranking-profile", "Which scoring functions, features, models, rules, freshness/diversity and tie breaks order candidates?", "ranking profile", ["bm25", "ltr"], ["hybrid-fusion"]),
    ("ranking-model-acl", "Which externally governed learned model edition may score/rerank without moving lifecycle authority into search?", "model ACL", ["ltr", "beir"], ["ranking-profile"]),
    ("result-contract", "Which visibility cut, hits, scores, ranks, fields, snippets, facets and partiality define a result?", "search result", ["lucene", "opensearch-rrf"], ["ranking-profile"]),
    ("pagination", "Which point-in-time cut, stable sort/cursor and expiry prevent duplicates or omissions across pages?", "page cursor", ["elastic-refresh"], ["result-contract"]),
    ("explanation", "Which matches, features, score contributions, filters and omissions explain a rank under disclosure controls?", "explanation", ["opensearch-rrf", "bm25"], ["result-contract"]),
    ("relevance-judgment", "Which assessor/topic/document-or-passage/context/time/scale defines a relevance occurrence?", "relevance judgment", ["trec-qrels"], ["result-contract"]),
    ("evaluation-corpus", "Which corpus, topics, pools, qrels, slices and leakage boundaries define evaluation?", "evaluation edition", ["trec-qrels", "beir"], ["relevance-judgment"]),
    ("retrieval-metrics", "Which precision/recall/MAP/MRR/nDCG/ERR/cost/latency/resource metrics are applicable?", "metric result", ["trec-eval", "ndcg"], ["evaluation-corpus"]),
    ("approximation-evidence", "Which exact baseline, recall distribution, filters, latency/memory and workload qualify approximation?", "approximation receipt", ["hnsw", "filtered-ann"], ["retrieval-metrics"]),
    ("deletion-verification", "Which generations, replicas, caches and snapshots no longer expose a deleted occurrence?", "deletion proof", ["elastic-delete", "elastic-refresh"], ["visibility"]),
    ("access-disclosure", "Which authorization filter and purpose protect hits, counts, facets, snippets, explanations and logs?", "disclosure result", ["elastic-dls"], ["result-contract"]),
    ("index-evolution", "How do schema, analyzer, corpus, embedding, ANN and ranking editions migrate, rebuild and replay?", "index lifecycle", ["lucene-index", "fresh-diskann"], ["deletion-verification", "approximation-evidence"]),
    ("semantic-diff", "Which query regions, candidates, ranks, visibility, explanation and disclosure behavior change across editions?", "semantic diff", ["beir", "trec-eval"], ["index-evolution"]),
    ("search-product-boundary", "What index/mutation/visibility/retrieval/ranking/result/evaluation lifecycle belongs to Search and Index Serving?", "product boundary", ["lucene", "elastic-refresh", "trec-qrels"], ["semantic-diff", "access-disclosure"]),
    ("discovery-source", "Which source system, endpoint, protocol, scope, credentials and expected population may be discovered?", "source profile", ["dcat3", "ogc-records"], []),
    ("acquisition", "Which crawl/poll/event/manual/import occurrence, cursor, attempts and partial failures acquired metadata?", "acquisition occurrence", ["ogc-records", "rfc9110"], ["discovery-source"]),
    ("assertion", "Which source claims which value about which resource under which extraction method, confidence and validity?", "metadata assertion", ["prov", "dcat3"], ["acquisition"]),
    ("resource-record-split", "How do resource, dataset, distribution, service, catalog, record and discovery projection remain distinct?", "metadata object model", ["dcat3"], ["assertion"]),
    ("vocabulary-mapping", "Which labels, concepts, schemes, mappings and losses normalize assertions without inventing equivalence?", "vocabulary crosswalk", ["skos", "dublin-core"], ["assertion"]),
    ("assertion-conflict", "Which source precedence, freshness, confidence and steward verdict handles conflicting assertions?", "conflict set", ["prov", "dqv"], ["vocabulary-mapping"]),
    ("discovery-projection", "Which accepted assertions and conflicts form an editioned searchable/browsable projection?", "discovery projection", ["dcat3", "ogc-records"], ["assertion-conflict"]),
    ("browse-navigation", "Which taxonomies, facets, relationships and collections support navigation without claiming ranked relevance?", "browse state", ["skos", "dcat3"], ["discovery-projection"]),
    ("federation", "Which endpoint queries, coverage, score normalization, deduplication, merge and partial failures produce a federated result?", "federated result", ["opensearch-spec", "sparql"], ["browse-navigation"]),
    ("freshness-coverage", "Which expected sources/resources were attempted, seen, changed, projected and indexed at which times?", "coverage ledger", ["rfc9110", "dqv"], ["federation"]),
    ("discovery-quality", "Which completeness, freshness, provenance, conflict, accessibility and fitness evidence accompanies discovery?", "discovery evidence", ["dqv", "dcat3"], ["freshness-coverage"]),
    ("discovery-product-boundary", "What acquisition/assertion/federation/coverage/projection/browse lifecycle belongs to Metadata Discovery?", "product boundary", ["dcat3", "ogc-records"], ["discovery-quality"]),
    ("search-discovery-acl", "How does Metadata Discovery publish projections into Search without transferring assertion authority?", "product ACL", ["dcat3", "lucene"], ["search-product-boundary", "discovery-product-boundary"]),
    ("query-homonyms", "How do exact database query, graph query, ranked retrieval, browse navigation and discovery query remain distinct?", "language split", ["sparql", "ir-book", "ogc-records"], ["search-discovery-acl"]),
    ("vector-boundary", "Why are vectors/ANN retrieval methods rather than an AI product, feature store or embedding authority?", "method boundary", ["hnsw", "mteb"], ["search-product-boundary"]),
    ("recommendation-boundary", "How does user/item recommendation differ from query-conditioned corpus retrieval and ranking?", "neighbor ACL", ["ltr", "ir-book"], ["ranking-model-acl"]),
    ("automation-boundary", "How may models/agents expand queries, rerank or summarize while deterministic indexing/retrieval/evidence remains complete?", "automation seam", ["beir", "trec-qrels"], ["query-homonyms", "vector-boundary"]),
]


def modules() -> list[dict[str, Any]]:
    return [{"module_id": f"module.search.{k}", "sovereign_question": q,
             "owned_semantic_object": owned,
             "source_refs": sorted(f"source.search.{s}" for s in srcs),
             "dependency_refs": sorted(f"module.search.{d}" for d in deps),
             "authority_limit": "The module defines a candidate boundary; it does not ratify content, assertions, relevance, access, models, effects or implementations.",
             "status": "EVIDENCE_BACKED_SEMANTIC_MODULE_CANDIDATE_UNRATIFIED"}
            for k, q, owned, srcs, deps in MODULE_ROWS]


LAW_STATEMENTS = [
    "Source object, representation, extracted unit, indexed document, field, passage and vector entry are distinct occurrences.",
    "Index schema references content meaning but does not own source truth.",
    "Mutation acceptance, commit, refresh and query visibility are distinct events.",
    "Visibility is an exact index/searcher/replica generation cut, not a wall-clock adjective.",
    "Delete acceptance is not verified disappearance from all visible generations, caches, replicas or snapshots.",
    "Index document identity is not enterprise entity identity.",
    "Analyzer edition participates in both index and compatible query identity.",
    "Token is not word, concept, entity, source span or semantic meaning.",
    "Stemming, lemmatization, synonym expansion and ontology mapping are non-equivalent operations.",
    "Index-time and query-time analysis may differ only under an explicit compatibility contract.",
    "Query string is not query AST, information need, retrieval plan or result.",
    "Exact database query, graph query, ranked retrieval, browse navigation and discovery query remain distinct.",
    "Match is not relevance, correctness, truth, fitness, recommendation, decision or authorization.",
    "Retrieval candidate, score, rank, result page, clicked item and business outcome remain distinct.",
    "BM25, vector similarity, model score, normalized score and fusion score are not generally comparable.",
    "Retrieval score is not calibrated probability unless a separately qualified calibration contract says so.",
    "Rank is relative to candidate set, visibility cut, profile and tie policy.",
    "Top-k truncation is information loss and participates in downstream fusion semantics.",
    "RRF combines ranks and intentionally discards score magnitude.",
    "Score normalization requires a declared population and is not semantic unification.",
    "Hybrid retrieval is an explicit staged algebra, not ambient combination of lexical and vector outputs.",
    "Filter-before, filter-during and filter-after ANN have different recall and latency semantics.",
    "Exact nearest neighbor and approximate nearest neighbor results are distinct evidence classes.",
    "ANN recall is scoped to dataset, queries, metric, index edition, parameters, filters and baseline.",
    "Vector dimension, scalar type, embedding edition, distance metric and normalization are part of identity.",
    "Cosine similarity, dot product and Euclidean distance are not interchangeable without proven transforms.",
    "Embedding proximity is not semantic equivalence, identity, causal relation or business relevance.",
    "Vector search is a retrieval method family, not an AI product or feature-store responsibility.",
    "Embedding and ranking-model training/approval/retirement remain external model-lifecycle authority.",
    "Learned sparse, dense and late-interaction retrieval are distinct index/query structures.",
    "Reranking cannot recover candidates excluded by an earlier retrieval stage.",
    "Facet domain, filter domain, result domain and aggregation domain are explicit and may differ.",
    "Distributed facet count may be approximate until refinement and carries error/coverage evidence.",
    "Pagination without an exact point-in-time cut may duplicate or omit results under mutation.",
    "Explanation describes one evaluated profile and is not proof of relevance or fairness.",
    "Search access filtering covers hits, counts, facets, snippets, highlights, explanations, caches and logs.",
    "Authorization-filter success is not authorization to use, disclose or act on retrieved content.",
    "Relevance judgment is an assessor/topic/document-or-passage/context/time occurrence, not ground truth.",
    "Unjudged is not irrelevant unless the evaluation profile explicitly makes that assumption.",
    "Pooling depth and participating runs limit judgment completeness.",
    "Precision, recall, MAP, MRR, nDCG and ERR answer different questions and require applicability decisions.",
    "Offline relevance metric improvement is not proof of user, business, safety or fairness improvement.",
    "One benchmark average is not fitness across industries, languages, modalities or information needs.",
    "Latency, throughput, memory, build cost, update freshness and relevance are separate objectives.",
    "Source resource, metadata assertion, catalog record, discovery projection and search index document are distinct.",
    "A catalog record describes registration of a resource; it is not the resource itself.",
    "Dataset, distribution, data service, dataset series, catalog and catalog record remain distinct.",
    "Acquired metadata is an assertion from a source, not accepted catalog truth.",
    "Multiple conflicting assertions remain visible until an authorized rule or steward disposition.",
    "Vocabulary mapping is directional and does not imply equivalence or lossless round trip.",
    "Discovered is not acquired, acquired is not projected, projected is not indexed, and indexed is not visible.",
    "Freshness has source-event, acquisition, assertion, projection, mutation and search-visibility clocks.",
    "Coverage is relative to an expected population; an unknown population cannot silently become complete.",
    "Federated success may contain partial endpoint failures and non-comparable scores.",
    "Federated deduplication requires explicit resource/record identity and cannot use title equality as identity.",
    "Browse order, taxonomy order and relevance rank are different topologies.",
    "Metadata Discovery owns acquisition/assertion/federation/coverage/projection lifecycle, not generic index serving.",
    "Search and Index Serving owns index generations/visibility/retrieval/ranking/results, not metadata assertion authority.",
    "Marketplace discovery ranking and recommendation policy remain neighboring product concerns.",
    "Search result never becomes a business decision, approval, action or observed outcome.",
    "Models or agents may propose expansions, ranking features or summaries but cannot replace deterministic retrieval evidence.",
    "Optional generative assistance can be removed without removing indexing, lexical/structured/vector retrieval or evaluation.",
    "Every partial result, timeout, shard failure and approximation remains explicit rather than silently empty.",
    "Finite query, candidate, memory, latency, indexing, privacy and disclosure budgets are declared.",
    "No vendor, benchmark, expert, paper or model becomes the canonical semantic owner.",
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.search.noncollapse.{i:02d}", "statement": s,
             "law_kind": "NON_COLLAPSE_OR_AUTHORITY_SEAM",
             "compiler_consequence": "Type/refusal/ACL boundaries preserve this distinction before lowering or binding.",
             "status": "CANDIDATE_UNRATIFIED"} for i, s in enumerate(LAW_STATEMENTS, 1)]


METHOD_GROUPS = {
    "analysis": ["Unicode normalization", "language identification", "character filtering", "standard tokenization", "whitespace tokenization", "n-gram tokenization", "edge n-gram", "case folding", "diacritic folding", "stopword filtering", "stemming", "lemmatization", "shingling", "synonym expansion", "decompounding", "phonetic encoding", "transliteration", "entity-aware token annotation"],
    "index_structure": ["inverted index", "positional postings", "term dictionary FST", "skip postings", "block compression", "document values", "stored fields", "BKD tree", "prefix trie", "suffix/n-gram index", "phonetic index", "geospatial index", "temporal interval index", "bitmap index", "Bloom filter", "LSH index", "IVF index", "product-quantized index", "HNSW graph", "disk graph ANN"],
    "lexical": ["Boolean retrieval", "term frequency scoring", "TF-IDF", "BM25", "BM25F", "query likelihood", "divergence from randomness", "phrase query", "proximity query", "span query", "prefix query", "wildcard query", "regular-expression query", "fuzzy edit-distance query", "phonetic query", "field boosting", "function score", "relevance feedback", "pseudo-relevance feedback", "query expansion"],
    "structured_facet": ["exact term filter", "set membership", "numeric range", "date/time range", "exists/missing", "nested-object filter", "parent-child filter", "geo bounding box", "geo radius", "polygon intersection", "temporal overlap", "terms facet", "range facet", "date histogram", "nested facet", "pivot facet", "metric facet", "distributed facet refinement"],
    "vector_ann": ["exact brute-force kNN", "radius neighbor search", "cosine similarity", "dot-product similarity", "Euclidean distance", "Manhattan distance", "Mahalanobis distance", "locality-sensitive hashing", "IVF flat", "IVF product quantization", "optimized product quantization", "HNSW", "NSG", "DiskANN", "FreshDiskANN", "filtered graph ANN", "scalar quantization", "binary quantization", "multi-vector late interaction", "maximum inner-product search"],
    "fusion_ranking": ["linear score fusion", "min-max normalization", "z-score normalization", "L2 normalization", "reciprocal rank fusion", "Borda fusion", "CombSUM", "CombMNZ", "cascade ranking", "two-stage reranking", "LambdaMART", "pairwise learning to rank", "listwise learning to rank", "freshness boost", "diversity/MMR", "fairness-constrained reranking", "business-rule reranking", "stable tie breaking"],
    "query_understanding": ["query parsing", "field resolution", "spell correction", "completion/suggest", "synonym expansion", "abbreviation expansion", "entity linking", "intent classification", "query segmentation", "term weighting", "natural-language-to-query translation", "semantic query canonicalization", "filter extraction", "time expression resolution", "geo expression resolution", "query rewriting", "query routing", "federated source selection"],
    "evaluation": ["precision", "recall", "F1", "precision at k", "recall at k", "average precision", "mean average precision", "reciprocal rank", "mean reciprocal rank", "DCG", "nDCG", "expected reciprocal rank", "R-precision", "bpref", "success at k", "coverage", "judgment agreement", "pool completeness audit", "paired randomization test", "bootstrap confidence interval", "latency percentile", "throughput", "memory/index-size", "ANN recall at k"],
    "discovery_federation": ["scheduled crawl", "incremental cursor acquisition", "conditional HTTP acquisition", "event-driven acquisition", "manual assertion import", "schema extraction", "profile inference", "assertion provenance capture", "source-precedence merge", "conflict-preserving merge", "vocabulary crosswalk", "resource-record identity resolution", "federated fanout", "source timeout budget", "score/rank merge", "cross-source deduplication", "coverage estimation", "freshness lag analysis"],
    "lifecycle_assurance": ["generation acknowledgement", "refresh visibility check", "replica visibility check", "point-in-time pagination", "historical query replay", "schema compatibility check", "analyzer compatibility check", "ranking semantic diff", "cross-provider differential", "reindex/rebuild", "shadow index", "canary ranking", "tombstone verification", "cache invalidation verification", "snapshot disclosure", "privacy leakage test", "resource exhaustion test", "partial-shard failure test"],
}


def methods() -> list[dict[str, Any]]:
    module_for = {"analysis": "analysis-chain", "index_structure": "index-structures", "lexical": "lexical-retrieval", "structured_facet": "facet-aggregation", "vector_ann": "ann-index", "fusion_ranking": "ranking-profile", "query_understanding": "query-contract", "evaluation": "retrieval-metrics", "discovery_federation": "federation", "lifecycle_assurance": "index-evolution"}
    source_for = {"analysis": ["ir-book", "lucene-analysis"], "index_structure": ["ir-book", "hnsw"], "lexical": ["bm25", "lm-ir"], "structured_facet": ["solr-facets", "sparql"], "vector_ann": ["hnsw", "pq", "diskann"], "fusion_ranking": ["rrf", "ltr"], "query_understanding": ["ir-book", "ogc-records"], "evaluation": ["trec-eval", "ndcg"], "discovery_federation": ["dcat3", "ogc-records"], "lifecycle_assurance": ["elastic-refresh", "elastic-delete"]}
    rows = []
    for group, names in METHOD_GROUPS.items():
        for i, name in enumerate(names, 1):
            rows.append({"method_type_id": f"method.search.{group}.{i:02d}", "method_group": group,
                         "name": name, "semantic_module_ref": f"module.search.{module_for[group]}",
                         "source_refs": sorted(f"source.search.{s}" for s in source_for[group]),
                         "result_law": "Every method returns a typed, cut/profile/edition-bound result with partiality, approximation, provenance, resource and authority limits; it never silently claims truth, relevance authority, authorization or effects.",
                         "llm_dependency": "none", "status": "EVIDENCE_BACKED_METHOD_TYPE_CANDIDATE_UNRATIFIED"})
    return rows


EXPERT_ROWS = [
    ("salton", "Gerard Salton", "vector-space retrieval", "Represent query-document similarity explicitly while keeping it distinct from semantic equivalence.", ["vector-space"]),
    ("sparck-jones", "Karen Spärck Jones", "term weighting and IR evaluation", "Make collection statistics and relevance assumptions explicit in weighting and evaluation.", ["bm25", "ir-book"]),
    ("robertson", "Stephen Robertson", "probabilistic relevance and BM25", "Bind BM25 scores to corpus, fields, query and parameter profile rather than call them probabilities.", ["bm25"]),
    ("zaragoza", "Hugo Zaragoza", "probabilistic and fielded retrieval", "Expose BM25F field and parameter semantics and non-textual ranking features.", ["bm25"]),
    ("croft", "W. Bruce Croft", "language-model retrieval", "Separate document language likelihood from user relevance and evaluation judgments.", ["lm-ir"]),
    ("manning", "Christopher Manning", "information retrieval foundations", "Use a complete inverted-index/query/evaluation decomposition beneath product interfaces.", ["ir-book"]),
    ("raghavan", "Prabhakar Raghavan", "Web search and retrieval systems", "Treat retrieval effectiveness, index execution and Web-scale ranking as separate concerns.", ["ir-book"]),
    ("schuetze", "Hinrich Schütze", "text processing and IR", "Preserve language, tokenization and representation editions in search identity.", ["ir-book"]),
    ("voorhees", "Ellen Voorhees", "TREC evaluation", "Bind relevance judgments and metrics to exact topics, corpus, pools, assessors and time.", ["trec-qrels", "trec-eval"]),
    ("jarvelin", "Kalervo Järvelin", "graded relevance evaluation", "Use explicit gains and rank discounts rather than a universal relevance score.", ["ndcg"]),
    ("kekalainen", "Jaana Kekäläinen", "graded retrieval metrics", "Keep graded judgments, cutoffs and metric profiles visible and testable.", ["ndcg"]),
    ("baezayates", "Ricardo Baeza-Yates", "search algorithms and bias", "Analyze ranking, efficiency and bias as separate evidence dimensions.", ["ir-book", "trec-qrels"]),
    ("burges", "Christopher Burges", "learning to rank", "Keep features, labels, objective and model edition external to the search runtime contract.", ["ltr"]),
    ("malkov", "Yury Malkov", "graph ANN and HNSW", "Expose random graph construction, search breadth, recall and memory trade-offs.", ["hnsw"]),
    ("jegou", "Hervé Jégou", "vector quantization and similarity search", "Make quantization distortion, codes, metric and reranking part of the contract.", ["pq", "faiss"]),
    ("douze", "Matthijs Douze", "large-scale similarity search", "Separate index family, hardware execution and benchmark evidence from vector meaning.", ["pq", "faiss"]),
    ("johnson", "Jeff Johnson", "GPU similarity search", "Qualify exact/approximate vector kernels with resource and numerical evidence.", ["faiss"]),
    ("subramanya", "Suhas Jayaram Subramanya", "disk-based ANN", "Treat graph layout, disk access, build/search parameters and workload as indexed evidence.", ["diskann"]),
    ("gollapudi", "Siddharth Gollapudi", "filtered and streaming ANN", "Expose filter selectivity, update generations and recall/latency interactions.", ["fresh-diskann", "filtered-ann"]),
    ("khattab", "Omar Khattab", "late-interaction retrieval", "Keep token-level vector interaction and compressed index editions distinct from single-vector search.", ["colbertv2"]),
    ("gurevych", "Iryna Gurevych", "heterogeneous retrieval evaluation", "Require multi-domain evidence and preserve benchmark-to-target transfer gaps.", ["beir"]),
    ("reimers", "Nils Reimers", "dense retrieval and benchmarks", "Evaluate embeddings across heterogeneous tasks without making benchmark rank universal fitness.", ["beir", "mteb"]),
    ("cutting", "Doug Cutting", "Lucene and inverted-index systems", "Factor analyzers, index generations, query execution and scoring into replaceable contracts.", ["lucene"]),
    ("albertoni", "Riccardo Albertoni", "data-catalog interoperability", "Keep catalog resource, record, dataset, distribution and version identities separate.", ["dcat3"]),
    ("cox", "Simon J. D. Cox", "dataset metadata and DCAT", "Use standard resource/service/series relationships while preserving community profiles.", ["dcat3"]),
    ("gonzalez-beltran", "Alejandra Gonzalez-Beltran", "metadata standards and data discovery", "Represent provenance, quality and versions without treating catalog metadata as source truth.", ["dcat3", "dqv"]),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.search.{k}", "name": n, "specialism": s,
             "learning_for_corpus": learn, "source_refs": sorted(f"source.search.{r}" for r in refs),
             "authority_limit": "Expert work informs bounded propositions; no person, vendor, benchmark, standard or paper becomes the semantic owner.",
             "status": "LEARNING_PROFILE_NOT_ENDORSEMENT"} for k, n, s, learn, refs in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("fresh-diskann", 2021, "FreshDiskANN streaming updates", "Makes ANN mutation generations, consolidation, freshness and recall explicit together.", ["fresh-diskann"], "none"),
    ("beir", 2021, "BEIR heterogeneous retrieval benchmark", "Tests lexical, sparse, dense, late-interaction and reranking across unlike domains.", ["beir"], "none"),
    ("splade", 2021, "Learned sparse retrieval", "Preserves inverted-index execution while importing editioned learned term expansions.", ["splade"], "none"),
    ("colbertv2", 2022, "Compressed late-interaction retrieval", "Adds token-level multi-vector retrieval and residual compression as a distinct index profile.", ["colbertv2"], "none"),
    ("mteb", 2022, "Massive Text Embedding Benchmark", "Expands embedding evaluation beyond one retrieval dataset and exposes task transfer limits.", ["mteb"], "none"),
    ("rfc9110", 2022, "HTTP validator and freshness consolidation", "Clarifies conditional acquisition and representation validation for discovery connectors.", ["rfc9110"], "none"),
    ("filtered-ann", 2023, "Filter-aware graph ANN", "Moves structured filtering into ANN design and makes selectivity/recall trade-offs measurable.", ["filtered-ann"], "none"),
    ("dcat3", 2024, "DCAT 3", "Adds dataset series and version relationships while preserving catalog-record/resource separation.", ["dcat3"], "none"),
    ("jsonpath", 2024, "RFC 9535 JSONPath", "Standardizes nested selector semantics used by structured retrieval and metadata extraction.", ["jsonpath"], "none"),
    ("ogc-records", 2025, "OGC API Records 1.0", "Standardizes modern metadata-record discovery APIs and distributed catalog patterns.", ["ogc-records"], "none"),
    ("rrf", 2025, "Operational hybrid reciprocal-rank fusion", "Combines incomparable lexical/vector scores by ranks with explicit depth and shard effects.", ["opensearch-rrf", "rrf"], "none"),
    ("disk-vector", 2025, "Disk-oriented and quantized vector serving", "Treats memory, disk, compression, reranking and recall as one qualified profile.", ["diskann", "pq"], "none"),
    ("visibility", 2026, "Explicit refresh/search visibility contracts", "Separates mutation acknowledgement from searchable visibility and deletion completion.", ["elastic-refresh", "elastic-delete"], "none"),
    ("multi-stage", 2026, "Composable lexical/vector/filter/rerank pipelines", "Makes candidate depths, stage loss, score/rank fusion and explanations first-class.", ["opensearch-rrf", "beir"], "none"),
    ("assisted-retrieval", 2026, "Governed query expansion and result summarization proposals", "Allows models/agents to propose expansions or summaries while deterministic retrieval, citations, policy and relevance evidence remain authoritative.", ["beir", "trec-qrels"], "optional_ai_or_llm_proposal_only"),
]


def innovations() -> list[dict[str, Any]]:
    return [{"innovation_id": f"innovation.search.{k}", "year": y, "name": n,
             "compiler_relevance": rel, "source_refs": sorted(f"source.search.{r}" for r in refs),
             "ai_or_llm_dependency": dep, "status": "RECENT_INNOVATION_CANDIDATE_UNRATIFIED"}
            for k, y, n, rel, refs, dep in INNOVATION_ROWS]


def module_refs_for_library(ref: str) -> list[str]:
    text = ref.lower(); keys = {"search-discovery-acl", "query-homonyms", "automation-boundary"}
    if any(x in text for x in ("search", "query", "result", "retrieval")): keys |= {"query-contract", "lexical-retrieval", "structured-retrieval", "ranking-profile", "result-contract", "search-product-boundary"}
    if any(x in text for x in ("index", "persistence", "visibility")): keys |= {"index-schema", "index-structures", "mutation", "visibility", "index-evolution", "deletion-verification"}
    if any(x in text for x in ("neighbor", "ranking", "predictive", "probabilistic")): keys |= {"vector-profile", "ann-index", "hybrid-fusion", "ranking-model-acl", "vector-boundary"}
    if any(x in text for x in ("facet", "spatial")): keys |= {"structured-retrieval", "facet-aggregation"}
    if any(x in text for x in ("document", "rendition")): keys |= {"content-admission", "document-identity", "analysis-chain"}
    if any(x in text for x in ("metadata", "catalog", "discovery")): keys |= {"discovery-source", "acquisition", "assertion", "resource-record-split", "discovery-projection", "browse-navigation", "federation", "freshness-coverage", "discovery-product-boundary"}
    if any(x in text for x in ("ontology", "semantic")): keys |= {"vocabulary-mapping", "query-homonyms"}
    if any(x in text for x in ("lineage", "assertion")): keys |= {"assertion", "assertion-conflict", "discovery-quality"}
    if any(x in text for x in ("privacy", "policy", "obligation")): keys |= {"access-disclosure"}
    if any(x in text for x in ("schema_registry", "version")): keys |= {"index-schema", "index-evolution", "semantic-diff"}
    return sorted(f"module.search.{k}" for k in keys)


def library_bindings(source_ids: set[str]) -> list[dict[str, Any]]:
    direct = declared_product_libraries(); evidence = sorted(source_ids)[:8]
    return [{"library_ref": ref, "relationship_to_products": "DECLARED_CONCRETE_BINDING" if ref in direct else "JUSTIFIED_NEIGHBOR_IMPORT_OR_OWNER",
             "semantic_module_refs": module_refs_for_library(ref), "evidence_refs": evidence,
             "downstream_product_refs": sorted(PRODUCTS | {"product.catalog_service", "product.data_marketplace", "product.model_lifecycle"}),
             "downstream_contract_route": "DECLARED_PRODUCT_BINDING_UNRATIFIED" if ref in direct else "NEIGHBOR_IMPORT_CANDIDATE_UNRATIFIED",
             "refusal_reasons": ["OWNER_RATIFICATION_MISSING", "EXACT_CONTRACT_UNSELECTED", "QUALIFIED_IMPLEMENTATION_MISSING", "TWO_VERTICAL_ACCEPTANCE_MISSING"],
             "compiler_binding": "REFUSED", "completion_claim": False} for ref in LIBRARIES]


def findings() -> list[dict[str, Any]]:
    rows = [
        {"finding_id": "finding.search.products.retain-separate.v1", "candidate_disposition": "RETAIN_SEARCH_AND_METADATA_DISCOVERY_AS_INDEPENDENT_PRODUCTS", "product_refs": sorted(PRODUCTS), "library_refs": sorted(declared_product_libraries()), "finding": "Search and Index Serving owns index/mutation/visibility/retrieval/ranking/result/evaluation lifecycle. Metadata Discovery owns acquisition/assertion/federation/coverage/projection/browse lifecycle and imports search for serving.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.search.vector-method.v1", "candidate_disposition": "KEEP_VECTOR_AND_ANN_AS_METHOD_CAPABILITIES_NOT_AI_PRODUCT", "product_ref": "product.search_index_service", "library_refs": ["library.predictive.neighbor_search", "library.method_kernels.search_methods"], "finding": "Vector similarity and ANN are typed retrieval methods alongside lexical, structured, spatial and hybrid retrieval. Embedding/model lifecycle remains external and the ambient AI-search label is rejected.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.search.model-authority.v1", "candidate_disposition": "IMPORT_RANKING_AND_EMBEDDING_MODEL_LIFECYCLE", "product_ref": "product.search_index_service", "library_refs": ["library.predictive.ranking_models", "library.predictive.neighbor_search"], "finding": "Search binds exact ranking/embedding model editions but does not train, approve, promote, monitor or retire them implicitly.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.search.discovery-authority.v1", "candidate_disposition": "KEEP_ASSERTION_AUTHORITY_IN_METADATA_DISCOVERY_NOT_SEARCH_INDEX", "product_ref": "product.metadata_discovery", "library_refs": ["library.metadata_discovery.assertion_record", "library.metadata_discovery.discovery_projection", "library.persistence.index_mutation"], "finding": "Metadata assertions and conflict/freshness evidence are projected into an index; the index document is a serving representation and never becomes catalog/source truth.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.search.query-homonym.v1", "candidate_disposition": "SPLIT_QUERY_HOMONYM_INTO_EXACT_GRAPH_RANKED_BROWSE_AND_DISCOVERY_TYPES", "library_refs": ["library.qck.query-types", "library.metadata_discovery.search_browse", "library.method_kernels.search_methods"], "finding": "Exact database query, graph query, ranked retrieval, browse navigation and discovery query have different results, algebra, order and completeness semantics.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
    ]
    for i, (ref, rationale) in enumerate(VACANCIES, 1):
        rows.append({"finding_id": f"finding.search.library-vacancy.{i:02d}", "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED", "proposed_library_ref": ref, "library_refs": [], "finding": rationale, "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0})
    return rows


def bounded_context() -> dict[str, Any]:
    return {"slice_id": "slice.search-information-retrieval.v1", "retained_products": sorted(PRODUCTS),
            "search_inside": ["index schema and analysis chain", "mutation generations and visibility cuts", "lexical/structured/spatial/vector/hybrid retrieval", "ranking profiles and results", "relevance and approximation evidence", "deletion/rebuild lifecycle"],
            "metadata_discovery_inside": ["source acquisition", "metadata assertions and conflicts", "resource/record projection", "vocabulary mapping", "federation and browse", "freshness and coverage evidence"],
            "imported_owners": ["source content and catalog truth", "document extraction", "enterprise identity", "ontology and vertical vocabularies", "embedding/ranking model lifecycle", "data-use authorization", "recommendation/marketplace policy", "business decisions and effects"],
            "non_collapse_summary": "source != assertion != projection != index document; mutation ack != visibility; match != relevance; score != probability; rank != decision; exact != approximate neighbor; vector retrieval != AI product; discovery != completeness",
            "product_boundary_candidates": [{"product_ref": p, "status": "RETAIN_BUT_NARROW_UNRATIFIED"} for p in sorted(PRODUCTS)],
            "candidate_new_products": [], "status": "CANDIDATE_UNRATIFIED", "completion_claim": False}


def build() -> dict[str, Any]:
    src = sources(); source_ids = {r["source_id"] for r in src}; mods = modules(); bindings = library_bindings(source_ids)
    axes = [{"library_ref": b["library_ref"], "axis": axis, "semantic_module_refs": b["semantic_module_refs"], "evidence_refs": b["evidence_refs"], "decision_candidate": "UNRESOLVED_RESEARCHED_CANDIDATE", "coordinate_answers": [], "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False} for b in bindings for axis in AXES]
    result = {"sources": src, "modules": mods, "laws": laws(), "methods": methods(), "experts": experts(), "innovations": innovations(), "libraries": bindings, "axes": axes, "findings": findings(), "context": bounded_context()}
    result["summary"] = {"slice_id": "slice.search-information-retrieval.v1", "as_of": AS_OF,
        "primary_or_official_sources": len(src), "semantic_modules": len(mods), "non_collapse_laws": len(LAW_STATEMENTS),
        "method_types": sum(map(len, METHOD_GROUPS.values())), "expert_learning_profiles": len(EXPERT_ROWS), "recent_innovations": len(INNOVATION_ROWS),
        "declared_product_libraries": len(declared_product_libraries()), "justified_neighbor_libraries": len(NEIGHBORS), "bound_libraries": len(LIBRARIES),
        "library_axis_decision_candidates": len(axes), "candidate_new_products": 0, "candidate_new_library_vacancies": len(VACANCIES),
        "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0, "canonical_gaps_closed": 0, "completion_claim": False}
    return result


def outputs() -> dict[str, str]:
    b = build(); files = {
        "primary-sources.jsonl": "".join(canonical(r) + "\n" for r in b["sources"]),
        "semantic-modules.jsonl": "".join(canonical(r) + "\n" for r in b["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(r) + "\n" for r in b["laws"]),
        "search-information-retrieval-method-taxonomy.jsonl": "".join(canonical(r) + "\n" for r in b["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(r) + "\n" for r in b["experts"]),
        "innovation-records.jsonl": "".join(canonical(r) + "\n" for r in b["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(r) + "\n" for r in b["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(r) + "\n" for r in b["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(r) + "\n" for r in b["findings"]),
        "bounded-context.json": json.dumps(b["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(b["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n"}
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.search-information-retrieval-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    summary = build()["summary"]
    print(f"BUILD PASS search/information-retrieval semantic slice: {summary['semantic_modules']} modules, {summary['method_types']} methods, {summary['bound_libraries']} libraries, {summary['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
