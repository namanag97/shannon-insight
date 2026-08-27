#!/usr/bin/env python3
"""Build the evidence-backed entity-resolution, master-data and reference-data semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
PRODUCTS = {
    "product.entity_resolution",
    "product.master_data_governance",
    "product.reference_data_governance",
}
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

NEIGHBORS = {
    "library.business_glossary.term_identity",
    "library.cbv.uncertainty_contracts",
    "library.csp.identity.identifier-parser",
    "library.csp.identity.identity-conformance",
    "library.csp.identity.resolver-contract",
    "library.csp.identity.scoped-identifier",
    "library.csp.identity.version-identity",
    "library.data_contract.contract_identity",
    "library.geocode.match.profile.compiler",
    "library.gmo.change_review_policy",
    "library.gmo.privacy_purpose_binding",
    "library.gmo.quality_core",
    "library.lpe.canonical-json",
    "library.lpe.canonical-rdf",
    "library.lpe.provenance-assertion",
    "library.lpe.provenance-bundle",
    "library.method_kernels.data_quality_methods",
    "library.method_kernels.graph_community_methods",
    "library.method_kernels.graph_methods",
    "library.method_kernels.statistical_estimators",
    "library.ontology_model.identity_import_closure",
    "library.package.reference_closure",
    "library.persistence.clustering_planner",
    "library.pipeline.identity_types",
    "library.predictive.classification_models",
    "library.provider_offer.reference_closure",
    "library.qor.defect_adjudication_kernel",
    "library.qor.reference_master_alignment_kernel",
    "library.schema_registry.reference_closure",
    "library.smf.uncertainty_algebra",
    "library.spt.privacy_vocabulary",
    "library.spt.relationship_graph",
}

VACANCIES = [
    ("library.entity_resolution.population_contract", "Entity kind, source populations, namespaces, inclusion rules, duplicate model and allowed multiplicity need one editioned population contract."),
    ("library.entity_resolution.record_occurrence", "A source record occurrence needs immutable source, record, edition, ingestion and validity identity without pretending to be the represented entity."),
    ("library.entity_resolution.normalization_profile", "Parsing, transliteration, tokenization, missingness and lossy normalization require an editioned profile and retained raw values."),
    ("library.entity_resolution.blocking_plan", "Blocking predicates, passes, index cut, recall assumptions, budgets and deterministic union semantics require a plan."),
    ("library.entity_resolution.candidate_set_receipt", "Compared, excluded, blocked-out and unevaluated pairs require explicit candidate-set evidence."),
    ("library.entity_resolution.comparison_feature_algebra", "Field comparators, agreement levels, term frequencies, dependencies and missingness require typed features."),
    ("library.entity_resolution.pair_assessment", "Score, probability, calibrated risk, decision band, refusal and explanation need a total pair-assessment result."),
    ("library.entity_resolution.constraint_profile", "One-to-one, source uniqueness, cannot-link, must-link, temporal and domain constraints need an explicit profile."),
    ("library.entity_resolution.cluster_edition", "Cluster membership, method/policy/data cuts, uncertainty, conflicts and lineage require immutable editions."),
    ("library.entity_resolution.cluster_formation_policy", "Transitive closure, correlation clustering, collective inference and conflict resolution cannot be hidden behind merge."),
    ("library.entity_resolution.evaluation_design", "Pair-, cluster- and entity-centric estimands, sampling, labels, uncertainty and subgroup slices require one evaluation design."),
    ("library.entity_resolution.linkage_uncertainty_bundle", "Downstream analyses need alternative linkage structures, weights or posterior evidence rather than a silently hardened join."),
    ("library.entity_resolution.privacy_preserving_profile", "Threat model, parties, encodings, keys, leakage, attacks, linkage quality and deletion require a PPRL profile."),
    ("library.entity_resolution.incremental_reconciliation", "New evidence, late data, cluster drift, re-evaluation scope and stable external references require an incremental protocol."),
    ("library.master_data.identifier_issuance_receipt", "Issuance authority, domain, subject evidence, identifier, time, aliases and retirement conditions need a durable receipt."),
    ("library.master_data.field_provenance_projection", "Every golden field needs candidate occurrence, authority rule, transform, tie-break, override and evidence cut."),
    ("library.master_data.relationship_hierarchy_edition", "Master relationships and hierarchies need scoped identity, temporal validity, acyclicity/cardinality policy and editioning."),
    ("library.master_data.change_propagation_receipt", "Identity, merge/split, authority and golden-value changes need consumer impact, notification and acknowledgement evidence."),
    ("library.reference_data.concept_code_designation_algebra", "Concept, code, notation, designation, display, definition and language are distinct semantic carriers."),
    ("library.reference_data.value_set_expansion", "Definition, parameters, code-system editions, expansion time, included members and incompleteness need a reproducible result."),
    ("library.reference_data.mapping_relation_algebra", "Exact, close, broader, narrower, related, no-map and context-dependent relations need direction and edition identity."),
    ("library.reference_data.crosswalk_loss_evaluator", "Cardinality, direction, conditions, unmapped cases, ambiguity and round-trip loss need executable evaluation."),
    ("library.reference_data.publication_subscription", "Publisher authority, release, delta, consumer pinning, deprecation, recall and acknowledgement need a lifecycle."),
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
    ("newcombe", "Automatic Linkage of Vital Records", "Newcombe et al.", 1959, "primary_paper", "https://doi.org/10.1126/science.130.3381.954", "Introduces probabilistic ideas for linking person records without a universal identifier.", "Historical method evidence does not define current privacy, evaluation or identity authority."),
    ("fellegi-sunter", "A Theory for Record Linkage", "Fellegi and Sunter", 1969, "primary_paper", "https://doi.org/10.1080/01621459.1969.10501049", "Defines comparison evidence and link, non-link and possible-link decisions under error bounds.", "The model assumptions and pairwise decision problem do not establish clusters or master identities."),
    ("jaro", "Advances in Record-Linkage Methodology", "Matthew Jaro", 1989, "primary_paper", "https://doi.org/10.1080/01621459.1989.10478785", "Develops operational probabilistic linkage and string comparison for census matching.", "Application-specific calibration and clerical practice are not universal policy."),
    ("winkler", "String Comparator Metrics and Enhanced Decision Rules", "William Winkler", 1990, "primary_report", "https://www.census.gov/library/working-papers/1990/adrm/rr90-05.html", "Develops string comparators and decision enhancements used in record linkage.", "Similarity is field- and population-dependent and never proves entity identity alone."),
    ("levenshtein", "Binary Codes Capable of Correcting Deletions, Insertions and Reversals", "Vladimir Levenshtein", 1966, "primary_paper", "https://doi.org/10.1016/S0021-9800(65)80020-2", "Defines edit-distance foundations used for approximate string comparison.", "Edit distance measures representation difference, not semantic or entity equality."),
    ("monge-elkan", "The Field Matching Problem", "Monge and Elkan", 1996, "primary_paper", "https://www.aaai.org/Papers/KDD/1996/KDD96-044.pdf", "Studies field-level similarity for duplicate detection.", "Comparator performance does not define a decision threshold or cluster policy."),
    ("sorted-neighborhood", "The Merge/Purge Problem for Large Databases", "Hernandez and Stolfo", 1995, "primary_paper", "https://doi.org/10.1145/223784.223807", "Introduces sorted-neighborhood candidate generation for duplicate detection.", "Blocking efficiency can exclude true matches and requires measured recall."),
    ("canopy", "Efficient Clustering of High-Dimensional Data Sets with Application to Reference Matching", "McCallum, Nigam and Ungar", 2000, "primary_paper", "https://doi.org/10.1145/335191.335446", "Introduces cheap-distance canopies before expensive clustering.", "Canopy membership is candidate generation, not an identity assertion."),
    ("elmagarmid", "Duplicate Record Detection: A Survey", "Elmagarmid, Ipeirotis and Verykios", 2007, "research_survey", "https://doi.org/10.1109/TKDE.2007.250581", "Surveys duplicate detection stages, comparators and methods.", "Taxonomy coverage is not product ownership or method qualification."),
    ("christen", "Data Matching: Concepts and Techniques for Record Linkage", "Peter Christen", 2012, "research_monograph", "https://doi.org/10.1007/978-3-642-31164-2", "Systematizes preprocessing, indexing, comparison, classification and evaluation.", "A method catalog does not remove domain-specific decisions and error costs."),
    ("bhattacharya-getoor", "Collective Entity Resolution in Relational Data", "Bhattacharya and Getoor", 2007, "primary_paper", "https://doi.org/10.1145/1247480.1247597", "Uses relational evidence and collective decisions in entity resolution.", "Graph correlation is evidence, not authority, and can propagate errors."),
    ("dong-entity-resolution", "Big Data Integration", "Dong and Srivastava", 2015, "research_monograph", "https://doi.org/10.2200/S00578ED1V01Y201404DTM040", "Covers schema mapping, entity resolution and data fusion as distinct integration problems.", "Integration methods do not define master-data issuance or source truth."),
    ("binette-steorts", "(Almost) All of Entity Resolution", "Binette and Steorts", 2022, "peer_reviewed_survey", "https://doi.org/10.1126/sciadv.abi8021", "Reviews probabilistic, Bayesian, supervised, clustering and canonicalization approaches and open problems.", "A cross-disciplinary review is not a portable contract or authority decision."),
    ("sadinle", "Bayesian Estimation of Bipartite Matchings for Record Linkage", "Mauricio Sadinle", 2017, "primary_paper", "https://doi.org/10.1080/01621459.2016.1148612", "Models bipartite matching jointly and permits unresolved partial Bayes decisions with uncertainty.", "Bipartite constraints do not apply to every deduplication or multi-source population."),
    ("steorts", "Entity Resolution with Empirically Motivated Priors", "Rebecca Steorts", 2015, "primary_paper", "https://doi.org/10.1214/15-BA965SI", "Models latent entities and distorted records in Bayesian entity resolution.", "Posterior partitions depend on model, prior, sampler and convergence evidence."),
    ("papadakis-blocking", "Blocking and Filtering Techniques for Entity Resolution", "Papadakis et al.", 2020, "peer_reviewed_survey", "https://doi.org/10.1145/3377455", "Separates blocking, filtering and hybrid search-space reduction methods.", "Candidate pruning is not a non-match decision and must expose recall loss."),
    ("pprl-bloom", "Privacy-Preserving Record Linkage Using Bloom Filters", "Schnell, Bachteler and Reiher", 2009, "primary_paper", "https://doi.org/10.1186/1472-6947-9-41", "Introduces similarity-preserving Bloom-filter linkage for identifiers.", "Bloom encodings have attack and leakage risks and do not prove privacy by construction."),
    ("entity-evaluation", "How to Evaluate Entity Resolution Systems: An Entity-Centric Framework", "Binette et al.", 2024, "primary_paper", "https://arxiv.org/abs/2404.05622", "Adds reusable entity-centric labeling, pair/cluster metrics and root-cause analysis.", "One evaluation design does not make benchmark labels complete or representative by default."),
    ("convergence", "Convergence Diagnostics for Entity Resolution", "Aleshin-Guendel and Steorts", 2024, "peer_reviewed_review", "https://doi.org/10.1146/annurev-statistics-040522-114848", "Shows partition-valued Bayesian ER needs explicit convergence diagnostics.", "Convergence diagnostics do not establish model fit or real-world identity truth."),
    ("downstream-uncertainty", "Developing and Testing New Methods for Linking and Analyzing Multiple Data Sources", "PCORI", 2026, "official_research_report", "https://www.ncbi.nlm.nih.gov/books/NBK621301/", "Evaluates propagation of linkage uncertainty into downstream analyses.", "Study findings are scoped and do not select a universal propagation method."),
    ("splink", "Splink Record Linkage User Guide", "UK Ministry of Justice Analytical Services", 2026, "official_implementation_documentation", "https://moj-analytical-services.github.io/splink/topic_guides/topic_guides_index.html", "Documents SQL-scale Fellegi-Sunter linkage, blocking, comparison, training, clustering and evaluation.", "Implementation documentation is market evidence, not semantic authority or independent qualification."),
    ("dedupe", "Dedupe Documentation", "Dedupe.io", 2026, "official_implementation_documentation", "https://docs.dedupe.io/", "Documents active-learning-based entity matching and deduplication interfaces.", "Product behavior does not define universal sampling, threshold or review policy."),
    ("prov-o", "PROV-O", "W3C", 2013, "web_standard", "https://www.w3.org/TR/prov-o/", "Defines entity, activity, agent, derivation and attribution provenance.", "Provenance describes claims and derivations but does not establish their truth."),
    ("rfc3986", "Uniform Resource Identifier: Generic Syntax", "IETF", 2005, "internet_standard", "https://www.rfc-editor.org/rfc/rfc3986", "Defines URI syntax, resolution and normalization considerations.", "URI equivalence is scheme- and context-dependent and is not entity equality."),
    ("rfc9562", "Universally Unique IDentifiers", "IETF", 2024, "internet_standard", "https://www.rfc-editor.org/rfc/rfc9562", "Updates UUID formats, variants and generation algorithms.", "Statistical uniqueness does not establish subject identity, authority or non-reassignment policy."),
    ("iso8000-110", "ISO 8000-110:2021 Exchange of Characteristic Data", "ISO", 2021, "international_standard", "https://www.iso.org/standard/78503.html", "Specifies syntax, semantic encoding and requirements for exchanging characteristic master data.", "Exchange conformance does not issue identifiers or choose master values."),
    ("iso8000-115", "ISO 8000-115:2024 Quality Identifiers", "ISO", 2024, "international_standard", "https://www.iso.org/standard/88847.html", "Specifies identifier owner, restrictions, characteristics and resolution principles.", "Explicitly excludes identifier-creation and resolution-method ownership."),
    ("iso11179-1", "ISO/IEC 11179-1:2023 Metadata Registries — Framework", "ISO/IEC", 2023, "international_standard", "https://www.iso.org/standard/78914.html", "Defines metadata-registry framework and registry-item concepts.", "Metadata registration is not master-entity resolution or source-value authority."),
    ("iso11179-6", "ISO/IEC 11179-6:2023 Metadata Registries — Registration", "ISO/IEC", 2023, "international_standard", "https://www.iso.org/standard/78916.html", "Defines registration information, conditions and procedures for registry items.", "It excludes registry implementation and type-specific value-domain semantics."),
    ("gs1-keys", "GS1 Identification Keys", "GS1", 2026, "official_standard_registry", "https://www.gs1.org/standards/id-keys", "Defines authority-scoped identifiers for trade items, locations, assets, documents and other subject kinds.", "A syntactically valid key does not prove correct allocation, current status or cross-domain identity."),
    ("gleif-cdf", "LEI Common Data File Format 3.1", "GLEIF", 2022, "official_registry_specification", "https://www.gleif.org/en/lei-data/access-and-use-lei-data/supporting-documents", "Publishes legal-entity identifier, relationship, exception, history, golden-copy and delta formats.", "LEI scope is legal entities under GLEIS policy, not arbitrary enterprise entity mastering."),
    ("skos", "SKOS Simple Knowledge Organization System Reference", "W3C", 2009, "web_standard", "https://www.w3.org/TR/skos-reference/", "Distinguishes concepts, schemes, labels, notations and typed cross-scheme mapping relations.", "SKOS mapping properties target knowledge organization and do not imply operational code translation fitness."),
    ("genericode", "Code List Representation (genericode) 1.0", "OASIS", 2023, "oasis_standard", "https://docs.oasis-open.org/codelist/genericode/v1.0/genericode-v1.0.html", "Defines code-list metadata, entries, keys, column sets, code-list sets and serialization.", "Representation conformance does not define maintenance authority, business acceptance or mapping semantics."),
    ("fhir-codesystem", "FHIR R5 CodeSystem", "HL7", 2023, "official_standard", "https://hl7.org/fhir/R5/codesystem.html", "Separates code-system content, concepts, codes, displays, designations and publisher authority.", "FHIR CodeSystem publishes content; it does not own external code-system maintenance."),
    ("fhir-valueset", "FHIR R5 ValueSet", "HL7", 2023, "official_standard", "https://hl7.org/fhir/R5/valueset.html", "Defines intensional/extensional selections and expansions over code systems.", "A value-set definition is not its expansion and expansion depends on exact versions and parameters."),
    ("fhir-conceptmap", "FHIR R5 ConceptMap", "HL7", 2023, "official_standard", "https://hl7.org/fhir/R5/conceptmap.html", "Defines directional, contextual, versioned concept mappings including broader/narrower/no-map results.", "Reverse mapping and round-trip preservation cannot be assumed."),
    ("fhir-namingsystem", "FHIR R5 NamingSystem", "HL7", 2023, "official_standard", "https://hl7.org/fhir/R5/namingsystem.html", "Describes identifier/code-system names and preferred identifiers, including third-party registrations.", "Naming-system registration is distinct from code-system publisher authority."),
    ("sdmx", "SDMX Information Model", "SDMX", 2021, "official_standard", "https://sdmx.org/wp-content/uploads/SDMX_3-0-0_SECTION_2_FINAL.pdf", "Defines agency-scoped identifiers, concepts, codelists, data structures, constraints and versioning.", "Statistical exchange structures do not establish enterprise master identities."),
    ("unlocode", "United Nations Code for Trade and Transport Locations", "UNECE", 2026, "official_code_list", "https://unece.org/trade/cefact/unlocode-code-list-country-and-territory", "Publishes maintained location-code editions and change indicators.", "A code-list entry does not prove physical-location identity or operational suitability."),
    ("data-fusion", "Data Fusion: Resolving Conflicts from Multiple Sources", "Dong, Berti-Equille and Srivastava", 2013, "primary_paper", "https://research.google/pubs/data-fusion-resolving-conflicts-from-multiple-sources/", "Separates conflicting source claims, source accuracy/copying assumptions and selected values.", "Inferred truth is model- and snapshot-dependent and does not become source or legal authority."),
    ("reltio", "Reltio Match, Merge and Survivorship", "Reltio", 2026, "official_product_documentation", "https://docs.reltio.com/en/objectives/resolve-potential-matches/potential-matching-at-a-glance/potential-matching-navigation/reltio-match-merge-and-survivorship", "Shows match suggestions, merge, source crosswalks and field-level survivorship/golden views as distinct operations.", "Vendor terminology and behavior are market evidence, not a portable semantic contract."),
    ("semarchy-rdm", "Reference Data Management", "Semarchy", 2026, "official_product_documentation", "https://semarchy.com/domain/reference-data/", "Shows independently adoptable code, taxonomy, classification, hierarchy and distribution workflows.", "Commercial packaging does not prove the only valid product boundary."),
]


def sources() -> list[dict[str, Any]]:
    return sorted(({"source_id": f"source.entity.{key}", "title": title, "publisher": publisher,
                    "year": year, "source_kind": kind, "url": url, "supported_claim": claim,
                    "authority_limit": limit, "primary_or_official": True,
                    "status": "INDEPENDENTLY_RESEARCHED_PRIMARY_OR_OFFICIAL"}
                   for key, title, publisher, year, kind, url, claim, limit in SOURCE_ROWS), key=lambda r: r["source_id"])


MODULE_ROWS = [
    ("population", "Which entity kind, source populations, namespaces, duplicate model and multiplicity define the resolution universe?", "population contract", ["binette-steorts", "christen"], []),
    ("record-occurrence", "Which immutable source record occurrence supplies observed attributes without becoming the represented entity?", "occurrence identity", ["prov-o", "binette-steorts"], ["population"]),
    ("identifier-namespace", "Which issuer, namespace, subject kind, syntax, scope, validity and reuse policy qualify an identifier?", "identifier algebra", ["iso8000-115", "rfc9562", "gs1-keys"], ["population"]),
    ("identifier-resolution", "What typed result follows when an identifier is parsed, validated and resolved under one registry edition?", "resolution result algebra", ["rfc3986", "iso8000-115", "fhir-namingsystem"], ["identifier-namespace"]),
    ("raw-observation", "Which exact raw values, missing states and source times are retained before transformation?", "evidence preservation", ["prov-o", "christen"], ["record-occurrence"]),
    ("normalization", "Which parsing, case, punctuation, transliteration, abbreviation and token transformations apply with what loss?", "normalization profile", ["christen", "jaro"], ["raw-observation"]),
    ("comparison-feature", "Which fields, comparators, agreement levels, dependencies, term frequencies and missingness form comparison evidence?", "comparison vector", ["fellegi-sunter", "winkler", "monge-elkan"], ["normalization"]),
    ("blocking-plan", "Which deterministic passes and indices generate candidate pairs under declared recall and resource assumptions?", "candidate generation", ["sorted-neighborhood", "canopy", "papadakis-blocking"], ["normalization"]),
    ("candidate-set", "Which pairs were compared, excluded, blocked out or unevaluated and why?", "candidate receipt", ["papadakis-blocking", "splink"], ["blocking-plan"]),
    ("fellegi-sunter-score", "Which m/u probabilities, priors, weights and dependence assumptions produce a linkage score?", "probabilistic linkage", ["fellegi-sunter", "jaro", "splink"], ["comparison-feature", "candidate-set"]),
    ("supervised-pair-model", "Which labels, sampling design, features, loss, calibration and cut produce pair predictions?", "supervised classification", ["binette-steorts", "dedupe"], ["comparison-feature", "candidate-set"]),
    ("bayesian-linkage", "Which likelihood, prior, partition/matching constraints, sampler and convergence evidence produce posterior linkage structures?", "Bayesian inference", ["sadinle", "steorts", "convergence"], ["comparison-feature", "candidate-set"]),
    ("pair-assessment", "Which score/probability, calibrated error, decision band, explanation and refusal characterize a pair?", "total pair result", ["fellegi-sunter", "sadinle"], ["fellegi-sunter-score", "supervised-pair-model", "bayesian-linkage"]),
    ("pair-decision", "Which authorized policy turns pair evidence into link, non-link, possible-link or refused?", "decision policy", ["fellegi-sunter", "jaro"], ["pair-assessment"]),
    ("constraints", "Which source-uniqueness, one-to-one, cannot-link, must-link, temporal and business constraints apply?", "constraint profile", ["sadinle", "binette-steorts"], ["population"]),
    ("collective-evidence", "Which relational/graph evidence may affect decisions without circularly manufacturing identity?", "collective resolution", ["bhattacharya-getoor", "binette-steorts"], ["pair-assessment", "constraints"]),
    ("cluster-formation", "Which closure, clustering, optimization or collective policy constructs clusters from pair evidence and constraints?", "partition algebra", ["binette-steorts", "bhattacharya-getoor"], ["pair-decision", "collective-evidence"]),
    ("cluster-edition", "Which records, links, conflicts, data/method/policy cuts and uncertainty identify a cluster edition?", "cluster lifecycle", ["steorts", "entity-evaluation"], ["cluster-formation"]),
    ("incremental-resolution", "How do late records and changed evidence create a new cluster edition without silently rewriting history?", "incremental reconciliation", ["binette-steorts", "prov-o"], ["cluster-edition"]),
    ("privacy-preserving-linkage", "Which parties, threat model, encodings, leakage, attacks and quality evidence govern privacy-preserving linkage?", "PPRL protocol", ["pprl-bloom", "iso8000-115"], ["comparison-feature"]),
    ("review-sampling", "Which uncertain/risky pairs or clusters are selected for independent clerical review?", "review design", ["fellegi-sunter", "entity-evaluation"], ["pair-assessment", "cluster-edition"]),
    ("review-adjudication", "Which competent authority may issue a defeasible pair/cluster judgment from one evidence cut?", "adjudication protocol", ["jaro", "entity-evaluation"], ["review-sampling"]),
    ("merge-split-reversal", "Which accepted proposal changes cluster membership, preserves lineage and supports reversal/appeal?", "append-only change protocol", ["prov-o", "reltio"], ["review-adjudication", "cluster-edition"]),
    ("evaluation-design", "Which labeled population, sampling, estimands, metrics, uncertainty and slices evaluate the system?", "evaluation contract", ["entity-evaluation", "binette-steorts"], ["population", "cluster-edition"]),
    ("pair-evaluation", "Which pair precision/recall/error estimates and uncertainty apply under the evaluation sample?", "pair metrics", ["entity-evaluation", "fellegi-sunter"], ["evaluation-design"]),
    ("cluster-evaluation", "Which cluster/entity metrics detect overmerge, undermerge and error concentration?", "cluster metrics", ["entity-evaluation", "binette-steorts"], ["evaluation-design"]),
    ("downstream-uncertainty", "How are alternative links/partitions and their uncertainty propagated into downstream estimands?", "uncertainty propagation", ["downstream-uncertainty", "sadinle"], ["bayesian-linkage", "evaluation-design"]),
    ("entity-resolution-boundary", "What ends at resolution assertions and cluster editions before master-identity authority begins?", "product boundary", ["binette-steorts", "dong-entity-resolution"], ["merge-split-reversal", "evaluation-design"]),
    ("master-domain", "Which business subject kind, jurisdiction, issuing authority and lifecycle define a master domain?", "master domain contract", ["iso8000-110", "gs1-keys", "gleif-cdf"], []),
    ("master-identity-issuance", "Which accepted evidence authorizes issuance, aliasing, retirement and non-reuse of a master identity?", "identity issuance", ["iso8000-115", "gs1-keys", "gleif-cdf"], ["master-domain"]),
    ("source-registration", "Which source occurrence is registered for which master domain without becoming authoritative automatically?", "source registration", ["prov-o", "iso8000-110"], ["record-occurrence", "master-domain"]),
    ("source-attribute-authority", "Which source may supply which attribute for which context and valid-time interval under what precedence?", "authority relation", ["iso8000-110", "reltio"], ["source-registration"]),
    ("candidate-value", "Which raw/normalized value, source, transform, validity and confidence form a master attribute candidate?", "value occurrence", ["prov-o", "data-fusion"], ["source-attribute-authority", "normalization"]),
    ("survivorship-policy", "Which authority, recency, completeness, quality, tie-break and override rules select field values?", "survivorship algebra", ["reltio", "data-fusion"], ["candidate-value"]),
    ("golden-projection", "Which reproducible field-level view results at one evidence/policy/time cut with explanations?", "projection result", ["reltio", "prov-o"], ["survivorship-policy"]),
    ("master-relationships", "Which mastered relationships and hierarchy editions apply with cardinality, time and cycle policy?", "relationship lifecycle", ["gleif-cdf", "gs1-keys"], ["master-identity-issuance"]),
    ("master-stewardship", "How are identity, authority, survivorship and hierarchy conflicts assigned, decided, appealed and closed?", "stewardship case", ["reltio", "gleif-cdf"], ["golden-projection", "master-relationships"]),
    ("master-publication", "Which identity, golden projection, relationships, provenance and restrictions form a publishable master edition?", "master release", ["iso8000-110", "gleif-cdf"], ["master-stewardship"]),
    ("master-change-propagation", "Which consumers are affected by merge/split/retirement/value changes and what acknowledgement is required?", "change propagation", ["gleif-cdf", "prov-o"], ["master-publication"]),
    ("master-data-boundary", "What identity issuance, authority, survivorship, hierarchy, stewardship and publication lifecycle is independently adoptable?", "product boundary", ["iso8000-110", "reltio"], ["master-change-propagation", "entity-resolution-boundary"]),
    ("concept-scheme", "Which publisher-scoped concepts, definitions and semantic relations form a concept-scheme edition?", "concept system", ["skos", "fhir-codesystem"], []),
    ("code-system", "Which codes/notations designate which concepts under one publisher and edition?", "code system", ["fhir-codesystem", "genericode"], ["concept-scheme"]),
    ("designation-label", "Which language/use-scoped designation, display or synonym belongs to a concept without becoming its identity?", "designation algebra", ["skos", "fhir-codesystem"], ["concept-scheme"]),
    ("reference-set", "Which exact set edition contains which eligible reference values and statuses?", "reference set lifecycle", ["genericode", "sdmx"], ["code-system"]),
    ("value-set-definition", "Which inclusion/exclusion rules over exact code-system editions define an allowed-use set?", "intensional set", ["fhir-valueset", "sdmx"], ["code-system"]),
    ("value-set-expansion", "Which parameters, terminology cut and time produce which extensional members and incompleteness?", "expansion result", ["fhir-valueset", "fhir-codesystem"], ["value-set-definition"]),
    ("mapping-relation", "Which directional exact/close/broader/narrower/related/no-map assertion applies under what context?", "mapping algebra", ["skos", "fhir-conceptmap"], ["concept-scheme"]),
    ("crosswalk-edition", "Which source/target editions, mappings, conditions, cardinalities and unmapped policy define a crosswalk?", "crosswalk lifecycle", ["fhir-conceptmap", "skos"], ["mapping-relation", "reference-set"]),
    ("mapping-loss", "What ambiguity, narrowing/broadening, no-map and round-trip loss result for a translation direction?", "loss evaluator", ["fhir-conceptmap", "skos"], ["crosswalk-edition"]),
    ("code-lifecycle", "Which additions, deprecations, replacements, aliases and effective dates form a code-list change?", "code lifecycle", ["genericode", "unlocode"], ["code-system"]),
    ("reference-publication", "Which publisher, edition, artifacts, digests, deltas and effective dates form a reference release?", "reference release", ["genericode", "sdmx", "unlocode"], ["reference-set", "code-lifecycle", "crosswalk-edition"]),
    ("reference-subscription", "Which consumer pins, accepts, rejects or migrates to which release with what acknowledgement?", "subscription lifecycle", ["genericode", "fhir-valueset"], ["reference-publication"]),
    ("reference-data-boundary", "What code/concept/set/mapping/publication lifecycle is independently adoptable from master entities?", "product boundary", ["semarchy-rdm", "genericode", "fhir-conceptmap"], ["reference-subscription"]),
    ("canonicalization-seam", "How are byte canonicalization, identifier normalization, entity representative selection and golden projection kept distinct?", "homonym adjudication", ["rfc3986", "binette-steorts", "reltio"], ["normalization", "golden-projection"]),
    ("three-product-seam", "Which contracts cross Entity Resolution, Master Data Governance and Reference Data Governance without collapsing ownership?", "context map", ["dong-entity-resolution", "iso8000-110", "genericode"], ["entity-resolution-boundary", "master-data-boundary", "reference-data-boundary"]),
]


def modules() -> list[dict[str, Any]]:
    return [{"module_id": f"module.entity.{key}", "owned_question": q, "formalism": formalism,
             "source_refs": sorted(f"source.entity.{s}" for s in refs),
             "dependency_refs": sorted(f"module.entity.{d}" for d in deps),
             "authority_limit": "Resolution evidence, master projections and reference mappings remain scoped, versioned and defeasible; none silently mutates sources or acquires legal/business effect authority.",
             "research_status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED"}
            for key, q, formalism, refs, deps in MODULE_ROWS]


LAW_STATEMENTS = [
    "Source record occurrence is not represented entity, master identity, golden record or reference value.",
    "Record identifier is not entity identifier; identifier string is not namespace-scoped identifier.",
    "Identifier syntax validity is not correct allocation, current validity, resolvability or subject identity.",
    "UUID uniqueness is not identity authority, non-reassignment evidence or semantic equality.",
    "URI normalization is not resource equivalence; resource equivalence is not real-world entity equality.",
    "Raw value is not normalized value, comparison feature, candidate value or survived value.",
    "Normalization is a potentially lossy transform and must not erase the raw observation.",
    "String similarity is not semantic equivalence, entity sameness or a link decision.",
    "Comparator output without field, locale, representation and missingness policy is incomplete.",
    "Blocking membership is not match; blocked-out is not non-match; unevaluated is not negative.",
    "Candidate-set recall is distinct from matcher recall and cluster recall.",
    "Comparison vector is not linkage weight, probability, calibrated risk or decision.",
    "Fellegi-Sunter weight is a likelihood ratio under assumptions, not a universal match probability.",
    "Score is not threshold band; threshold band is not authorized decision; decision is not source truth.",
    "Link, non-link, possible-link, abstain, conflict and refused are distinct total-result states.",
    "Pairwise evidence does not automatically define a globally consistent partition.",
    "One-to-one bipartite matching is not unconstrained deduplication or multi-source clustering.",
    "Transitive closure can create unsupported links; pair link is not cluster co-membership proof.",
    "Graph proximity or shared relationships are evidence, not identity authority.",
    "Cluster is not entity, household, account, legal person, business party or master identity.",
    "Cluster identifier is not stable subject identifier unless an explicit authority issues it as such.",
    "Cluster edition identity includes population, source cuts, method, policy, constraints and time.",
    "Incremental update creates a new reconciliation edition and never silently rewrites prior evidence.",
    "Merge proposal is not accepted merge; accepted merge is not source mutation.",
    "Split is not deletion; reversal must preserve prior cluster and decision lineage.",
    "Clerical review is not ground truth; reviewer competence is not adjudication authority.",
    "Review judgment is scoped and defeasible and may remain possible-link or unresolved.",
    "Pair precision/recall, cluster metrics and entity-centric metrics answer different questions.",
    "Benchmark label is not population truth; evaluation requires sampling, uncertainty and coverage evidence.",
    "High pair accuracy can hide catastrophic overmerged clusters or concentrated entity-level errors.",
    "A hardened linkage table is not sufficient evidence for downstream uncertainty-sensitive analysis.",
    "Posterior convergence is not model fit, calibration, identity truth or downstream validity.",
    "Privacy-preserving encoding is not proof of privacy; threat model, leakage and attacks remain explicit.",
    "Bloom-filter similarity can leak identifiers and does not preserve every comparator semantic.",
    "Entity Resolution owns comparison and reconciliation assertions, not master identifier issuance.",
    "Resolution assertion is not master identity, golden projection or accepted business effect.",
    "Master identity is an authority-scoped lifecycle object, not the winning source record.",
    "Source registration is not source authority; source authority is attribute/context/time scoped.",
    "System of record, source of entry, source of truth and authoritative candidate are distinct roles.",
    "Latest is not most complete, most accurate, most authoritative or legally effective.",
    "Survivorship policy is not survivorship result; result is not source correction.",
    "Golden record is a reproducible projection at a cut, not metaphysical truth or the represented entity.",
    "Golden field provenance must identify candidate, source authority, transform, rule and override.",
    "Manual override is not permanent truth and requires scope, authority, expiry and appeal semantics.",
    "Master relationship is not entity-resolution link, source relationship or inferred graph edge.",
    "Master hierarchy edition is not taxonomy hierarchy or organizational/legal structure by default.",
    "Stewardship decision is not source mutation or downstream business approval outside delegation.",
    "Master merge/split propagation issuance is not completed consumer application or acknowledgement.",
    "Master data describes governed business entities; reference data constrains/classifies values and concepts.",
    "Reference value is not mastered business entity merely because it has an identifier and lifecycle.",
    "Concept is not code, notation, designation, display label, definition or code-list row.",
    "Code identity includes its code system and edition; the same lexical code across systems is not equal.",
    "CodeSystem is not ValueSet; ValueSet definition is not ValueSet expansion.",
    "Value-set expansion identity includes code-system editions, parameters, terminology cut and time.",
    "Naming-system registration is not code-system publisher authority.",
    "Reference set is not code system, value set, concept scheme, taxonomy or schema enumeration by default.",
    "Crosswalk mapping is a directional assertion, not equivalence, transform or guaranteed translation.",
    "Exact, close, broader, narrower, related and no-map relations are not interchangeable.",
    "Forward mapping does not imply reverse mapping; two mappings do not imply lossless round trip.",
    "Many-to-one mapping can destroy information even when every source code has a target.",
    "Reference-data publication is not consumer adoption; deprecation is not completed migration.",
    "Byte/document canonicalization, identifier normalization, canonical representative and golden projection are four different operations.",
    "One vendor may package entity resolution, MDM and RDM together; packaging does not prove one product boundary.",
    "Entity Resolution, Master Data Governance and Reference Data Governance have independent users, outputs, adoption paths and authority lifecycles.",
    "Models or agents may propose candidates, scores, mappings or priorities but cannot acquire identity, master, publisher or effect authority.",
]


def laws() -> list[dict[str, Any]]:
    return [{"law_id": f"law.entity.{i:03d}", "statement": s,
             "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0}
            for i, s in enumerate(LAW_STATEMENTS, 1)]


METHOD_GROUPS = {
    "normalization_comparison": ["case/punctuation normalization", "Unicode normalization", "transliteration", "phonetic encoding", "abbreviation expansion", "token sorting", "exact agreement", "Levenshtein distance", "Damerau-Levenshtein distance", "Jaro similarity", "Jaro-Winkler similarity", "q-gram similarity", "Jaccard similarity", "Dice similarity", "cosine token similarity", "Monge-Elkan similarity", "numeric tolerance", "date partial agreement", "geographic distance", "address standardization", "term-frequency adjustment"],
    "candidate_generation": ["full Cartesian comparison", "exact-key blocking", "multi-pass blocking", "standard blocking", "sorted neighborhood", "canopy clustering", "q-gram indexing", "suffix-array indexing", "LSH blocking", "MinHash blocking", "schema-agnostic token blocking", "attribute clustering blocking", "block purging", "block filtering", "meta-blocking", "nearest-neighbor retrieval", "learned blocking", "progressive blocking", "incremental blocking"],
    "pair_inference": ["deterministic exact rules", "Fellegi-Sunter linkage", "EM parameter estimation", "frequency-aware linkage", "logistic regression matcher", "decision tree matcher", "random forest matcher", "gradient boosted matcher", "support vector matcher", "active-learning matcher", "cost-sensitive classifier", "calibrated probability matcher", "Bayesian bipartite linkage", "Bayesian deduplication", "latent-entity distortion model", "neural pair matcher", "embedding-based matcher", "hybrid rule/statistical matcher", "abstaining classifier"],
    "clustering_collective": ["connected components", "transitive closure", "hierarchical agglomeration", "correlation clustering", "center/canopy clustering", "Markov clustering", "community detection", "collective relational resolution", "factor-graph inference", "bipartite assignment", "multi-partite matching", "source-aware clustering", "constraint-aware clustering", "cluster repair", "incremental clustering", "streaming entity coreference", "cluster representative selection", "canonical-record selection"],
    "review_adjudication": ["possible-link clerical review", "risk-ranked review", "uncertainty sampling", "cluster-centric review", "entity-centric labeling", "pair label adjudication", "cluster split review", "merge proposal review", "cannot-link assertion", "must-link assertion", "appeal/re-adjudication", "merge reversal", "split reversal", "negative-twin review", "cross-provider differential"],
    "evaluation": ["pair precision", "pair recall", "pair F-score", "false-match rate", "false-nonmatch rate", "reduction ratio", "pairs completeness", "pairs quality", "cluster B-cubed", "variation of information", "adjusted Rand index", "cluster edit distance", "overmerge rate", "undermerge rate", "entity-centric precision/recall", "cluster-size error profile", "subgroup error analysis", "calibration curve", "expected calibration error", "threshold sensitivity", "bootstrap uncertainty", "Bayesian posterior checking", "MCMC convergence diagnostics", "root-cause error analysis"],
    "privacy_preserving": ["Bloom-filter PPRL", "cryptographic long-term keys", "secure multiparty comparison", "private set intersection", "trusted linkage unit", "hash-based exact linkage", "phonetic encoding under encryption", "differentially private linkage statistics", "multi-party PPRL", "encoding frequency attack audit", "cryptanalysis/red-team audit"],
    "master_data": ["registry-issued identifier", "centralized registry mastering", "consolidation/coexistence mastering", "transaction-style mastering", "source registry", "field-level source authority", "most-trusted-source survivorship", "most-recent survivorship", "most-complete survivorship", "frequency survivorship", "quality-score survivorship", "conditional survivorship", "manual override", "golden projection", "master hierarchy management", "relationship mastering", "stewardship workflow", "merge/split lifecycle", "delta publication", "consumer reconciliation"],
    "reference_data": ["code-list registration", "concept-scheme management", "code-system publication", "designation/localization", "reference-set editioning", "intensional value set", "extensional value set", "value-set expansion", "code validation", "code lookup", "exact mapping", "close mapping", "broader/narrower mapping", "context-dependent mapping", "no-map assertion", "crosswalk publication", "round-trip loss test", "code deprecation/replacement", "reference hierarchy", "subscription/delta distribution"],
    "uncertainty_change": ["alternative linkage structures", "multiple-imputation linkage", "posterior partition samples", "linkage-weighted analysis", "sensitivity bounds", "incremental re-resolution", "late-record reconciliation", "policy-edition replay", "cluster drift audit", "consumer impact analysis", "change acknowledgement", "historical replay"],
}


def methods() -> list[dict[str, Any]]:
    module_for = {"normalization_comparison": "comparison-feature", "candidate_generation": "blocking-plan", "pair_inference": "pair-assessment", "clustering_collective": "cluster-formation", "review_adjudication": "review-adjudication", "evaluation": "evaluation-design", "privacy_preserving": "privacy-preserving-linkage", "master_data": "master-data-boundary", "reference_data": "reference-data-boundary", "uncertainty_change": "downstream-uncertainty"}
    source_for = {"normalization_comparison": ["jaro", "winkler", "christen"], "candidate_generation": ["sorted-neighborhood", "papadakis-blocking"], "pair_inference": ["fellegi-sunter", "sadinle", "binette-steorts"], "clustering_collective": ["bhattacharya-getoor", "binette-steorts"], "review_adjudication": ["fellegi-sunter", "entity-evaluation"], "evaluation": ["entity-evaluation", "convergence"], "privacy_preserving": ["pprl-bloom"], "master_data": ["iso8000-110", "reltio", "gleif-cdf"], "reference_data": ["genericode", "fhir-conceptmap", "skos"], "uncertainty_change": ["downstream-uncertainty", "prov-o"]}
    rows = []
    for group, names in METHOD_GROUPS.items():
        for i, name in enumerate(names, 1):
            rows.append({"method_type_id": f"method.entity.{group}.{i:02d}", "method_group": group,
                         "name": name, "semantic_module_ref": f"module.entity.{module_for[group]}",
                         "source_refs": sorted(f"source.entity.{s}" for s in source_for[group]),
                         "result_law": "Every method returns a typed, scoped and editioned result with partiality, uncertainty, evidence and refusal; no output silently becomes entity identity, source truth, master authority, reference authority or business effect.",
                         "llm_dependency": "none", "status": "EVIDENCE_BACKED_METHOD_TYPE_CANDIDATE_UNRATIFIED"})
    return rows


EXPERT_ROWS = [
    ("newcombe", "Howard Newcombe", "probabilistic record linkage", "Treat linkage as evidence under error rather than exact-key joining.", ["newcombe"]),
    ("fellegi", "Ivan Fellegi", "record-linkage decision theory", "Preserve link, non-link and possible-link decisions with explicit error trade-offs.", ["fellegi-sunter"]),
    ("sunter", "Alan Sunter", "record-linkage decision theory", "Make comparison evidence and decision thresholds explicit rather than burying them in matching code.", ["fellegi-sunter"]),
    ("jaro", "Matthew Jaro", "operational probabilistic linkage", "Treat preprocessing, comparison, weighting, blocking and clerical resolution as separately testable stages.", ["jaro"]),
    ("winkler", "William Winkler", "string comparison and linkage", "Calibrate comparators and frequency effects to the population instead of using universal fuzzy thresholds.", ["winkler"]),
    ("christen", "Peter Christen", "data matching systems", "Expose the full preprocessing-indexing-comparison-classification-evaluation pipeline and its domain choices.", ["christen"]),
    ("steorts", "Rebecca Steorts", "Bayesian entity resolution", "Represent latent entities, distorted records, partition uncertainty and sampler diagnostics explicitly.", ["steorts", "binette-steorts", "convergence"]),
    ("binette", "Olivier Binette", "entity-resolution evaluation", "Evaluate at pair, cluster and entity levels and build reusable representative benchmarks with root-cause analysis.", ["binette-steorts", "entity-evaluation"]),
    ("sadinle", "Mauricio Sadinle", "Bayesian bipartite linkage", "Enforce matching constraints jointly and permit unresolved decisions while propagating uncertainty downstream.", ["sadinle", "downstream-uncertainty"]),
    ("papadakis", "George Papadakis", "blocking and filtering", "Model candidate generation as its own recall/resource decision, never as a hidden non-match rule.", ["papadakis-blocking"]),
    ("palpanas", "Themis Palpanas", "scalable entity resolution", "Separate search-space reduction from pair decisions and compare schema-aware and schema-agnostic routes.", ["papadakis-blocking"]),
    ("getoor", "Lise Getoor", "collective entity resolution", "Use relational evidence while guarding against circularity and propagated linkage errors.", ["bhattacharya-getoor"]),
    ("bhattacharya", "Indrajit Bhattacharya", "collective entity resolution", "Treat interdependent entity decisions as a graph problem rather than independent pairs when justified.", ["bhattacharya-getoor"]),
    ("elmagarmid", "Ahmed Elmagarmid", "duplicate detection", "Decompose duplicate detection across representations, similarity, decisions and scalable search.", ["elmagarmid"]),
    ("ipeirotis", "Panagiotis Ipeirotis", "data integration and human review", "Preserve uncertainty and route high-value ambiguous cases to governed human decisions.", ["elmagarmid"]),
    ("dong", "Xin Luna Dong", "entity resolution and data fusion", "Keep reference reconciliation separate from conflicting-value fusion and source trust assumptions.", ["dong-entity-resolution", "data-fusion"]),
    ("srivastava", "Divesh Srivastava", "data integration and truth discovery", "Expose source copying, accuracy and conflict assumptions before selecting a consolidated value.", ["data-fusion"]),
    ("schnell", "Rainer Schnell", "privacy-preserving linkage", "Pair utility claims with an explicit attacker model, encoding leakage audit and quality comparison.", ["pprl-bloom"]),
    ("bachteler", "Tobias Bachteler", "privacy-preserving linkage", "Treat encoding construction and similarity computation as separate, attackable protocol decisions.", ["pprl-bloom"]),
    ("hernandez", "Mauricio Hernandez", "large-scale duplicate detection", "Use deterministic candidate windows to control cost while measuring missed-match consequences.", ["sorted-neighborhood"]),
    ("stolfo", "Salvatore Stolfo", "merge/purge systems", "Keep candidate generation and duplicate decisions modular so scaling choices remain replaceable.", ["sorted-neighborhood"]),
    ("otto", "Boris Otto", "master data governance", "Define master-data ownership, architecture and lifecycle independently of one implementation platform.", ["iso8000-110"]),
    ("holman", "G. Ken Holman", "code-list interchange", "Represent code-list keys, entries, versions and configurations explicitly and validate beyond syntax.", ["genericode"]),
    ("miles", "Alistair Miles", "SKOS knowledge organization", "Keep concept identity, labels, notations and mapping relations separate and typed.", ["skos"]),
    ("gleif", "GLEIF standards and data-quality teams", "legal-entity reference data", "Publish exact identifier, entity, relationship, exception, history, golden and delta editions under named authority.", ["gleif-cdf"]),
    ("hl7-terminology", "HL7 Terminology Infrastructure Work Group", "code systems and terminology services", "Separate code-system publisher authority, value-set selection/expansion and directional concept mapping.", ["fhir-codesystem", "fhir-valueset", "fhir-conceptmap"]),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.entity.{key}", "name": name, "specialism": specialism,
             "learning_for_corpus": learning, "source_refs": sorted(f"source.entity.{s}" for s in refs),
             "authority_limit": "Expert work informs bounded propositions; no person, paper, vendor or standards body becomes the SAN semantic owner.",
             "status": "LEARNING_PROFILE_NOT_ENDORSEMENT"}
            for key, name, specialism, learning, refs in EXPERT_ROWS]


INNOVATION_ROWS = [
    ("iso8000-110", 2021, "ISO 8000-110 characteristic-data exchange", "Strengthens portable semantic encoding and quality requirements for master-data exchange.", ["iso8000-110"], "none"),
    ("gleif31", 2022, "GLEIF LEI-CDF 3.1 and relationship/history editions", "Makes legal-entity events, relationship records, reporting exceptions, golden copies and deltas explicit.", ["gleif-cdf"], "none"),
    ("almost-all", 2022, "Cross-disciplinary entity-resolution synthesis", "Unifies probabilistic, supervised, clustering and canonicalization families while exposing evaluation and downstream gaps.", ["binette-steorts"], "none"),
    ("genericode10", 2023, "OASIS genericode 1.0 standard", "Standardizes code-list document, key, row, column-set and configured code-list-set semantics.", ["genericode"], "none"),
    ("fhir-r5", 2023, "FHIR R5 terminology resources", "Clarifies normative CodeSystem/ValueSet boundaries and directional contextual ConceptMap semantics.", ["fhir-codesystem", "fhir-valueset", "fhir-conceptmap"], "none"),
    ("iso11179", 2023, "ISO/IEC 11179 registry framework and registration revision", "Refreshes editioned registry-item naming, identification, definition and registration procedures.", ["iso11179-1", "iso11179-6"], "none"),
    ("er-evaluation", 2023, "ER-Evaluation open evaluation toolkit", "Operationalizes end-to-end pair, cluster and entity-centric analysis with reusable benchmark artifacts.", ["entity-evaluation"], "none"),
    ("entity-centric", 2024, "Entity-centric ER evaluation framework", "Adds representative entity labeling, monitoring, error metrics and root-cause analysis beyond pair benchmarks.", ["entity-evaluation"], "none"),
    ("convergence", 2024, "Partition-aware Bayesian ER convergence diagnostics", "Makes MCMC convergence a first-class qualification requirement for posterior linkage structures.", ["convergence"], "none"),
    ("rfc9562", 2024, "RFC 9562 UUID revision", "Adds modern UUID versions and sortable/time-ordered generation while preserving the identity/authority boundary.", ["rfc9562"], "none"),
    ("iso8000-115", 2024, "ISO 8000-115 quality-identifier revision", "Clarifies owner, restrictions, syntax, semantics and resolution characteristics while excluding identifier creation methods.", ["iso8000-115"], "none"),
    ("uncertainty-analysis", 2026, "Linked-data uncertainty propagation trials", "Compares multiple linkage structures and downstream analyses rather than treating one hard join as certain.", ["downstream-uncertainty"], "none"),
    ("real-time-survivorship", 2026, "Context-specific real-time survivorship views", "Shows golden fields can be policy/role-sensitive projections with source crosswalks rather than stored truth.", ["reltio"], "none"),
    ("independent-rdm", 2026, "Independently adoptable reference-data workbenches", "Market evidence reinforces separate code/taxonomy/classification governance and distribution lifecycles.", ["semarchy-rdm"], "none"),
    ("governed-assisted-er", 2026, "Governed assisted candidate and mapping proposals", "Allows models or agents to propose candidates and mappings while preserving deterministic policies, evidence and human/owner authority.", ["entity-evaluation", "fhir-conceptmap"], "optional_ai_or_llm_proposal_only"),
]


def innovations() -> list[dict[str, Any]]:
    return [{"innovation_id": f"innovation.entity.{key}", "year": year, "name": name,
             "compiler_relevance": relevance, "source_refs": sorted(f"source.entity.{s}" for s in refs),
             "ai_or_llm_dependency": dep, "status": "RECENT_INNOVATION_CANDIDATE_UNRATIFIED"}
            for key, year, name, relevance, refs, dep in INNOVATION_ROWS]


def module_refs_for_library(ref: str) -> list[str]:
    t = ref.lower()
    keys = {"population", "record-occurrence", "three-product-seam"}
    if any(x in t for x in ("identity", "identifier", "namespace", "canonical")): keys |= {"identifier-namespace", "identifier-resolution", "canonicalization-seam"}
    if any(x in t for x in ("entity-resolution", "duplicate", "match", "cluster", "classification")): keys |= {"normalization", "comparison-feature", "blocking-plan", "pair-assessment", "pair-decision", "cluster-formation", "cluster-edition", "entity-resolution-boundary"}
    if any(x in t for x in ("review", "adjudication", "issue", "evidence")): keys |= {"review-sampling", "review-adjudication", "merge-split-reversal", "evaluation-design"}
    if any(x in t for x in ("uncertainty", "statistical")): keys |= {"bayesian-linkage", "evaluation-design", "downstream-uncertainty"}
    if any(x in t for x in ("privacy", "purpose")): keys |= {"privacy-preserving-linkage"}
    if any(x in t for x in ("graph", "relationship")): keys |= {"collective-evidence", "cluster-formation", "master-relationships"}
    if any(x in t for x in ("master_data", "golden", "source_authority", "reference_master")): keys |= {"master-domain", "master-identity-issuance", "source-attribute-authority", "survivorship-policy", "golden-projection", "master-stewardship", "master-data-boundary"}
    if any(x in t for x in ("reference_data", "reference_closure", "ontology", "glossary")): keys |= {"concept-scheme", "code-system", "reference-set", "mapping-relation", "crosswalk-edition", "mapping-loss", "reference-data-boundary"}
    if "provenance" in t: keys |= {"record-occurrence", "cluster-edition", "golden-projection", "master-publication"}
    if "quality" in t: keys |= {"evaluation-design", "source-attribute-authority", "mapping-loss"}
    return sorted(f"module.entity.{k}" for k in keys)


def library_bindings(source_ids: set[str]) -> list[dict[str, Any]]:
    direct = declared_product_libraries(); evidence = sorted(source_ids)[:7]
    return [{"library_ref": ref, "relationship_to_product": "DECLARED_CONCRETE_BINDING" if ref in direct else "JUSTIFIED_NEIGHBOR_IMPORT_OR_OWNER",
             "semantic_module_refs": module_refs_for_library(ref), "evidence_refs": evidence,
             "downstream_product_refs": sorted(PRODUCTS),
             "downstream_contract_route": "DECLARED_PRODUCT_BINDING_UNRATIFIED" if ref in direct else "NEIGHBOR_IMPORT_CANDIDATE_UNRATIFIED",
             "refusal_reasons": ["OWNER_RATIFICATION_MISSING", "EXACT_CONTRACT_UNSELECTED", "QUALIFIED_IMPLEMENTATION_MISSING", "TWO_VERTICAL_ACCEPTANCE_MISSING"],
             "compiler_binding": "REFUSED", "completion_claim": False} for ref in LIBRARIES]


def findings() -> list[dict[str, Any]]:
    rows = [
        {"finding_id": "finding.entity.product.retain-narrow.v1", "candidate_disposition": "RETAIN_ENTITY_RESOLUTION_BUT_NARROW_MASTER_IMPORTS", "product_ref": "product.entity_resolution", "library_refs": sorted(declared_product_libraries()), "finding": "Retain population, occurrence, normalization, candidate, comparison, pair/cluster decision, review, reversal and evaluation lifecycles; master identities, source authority, survivorship and golden records are capability imports owned by Master Data Governance.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.entity.product.split-master-reference.v1", "candidate_disposition": "RETAIN_INDEPENDENT_PRODUCT_BOUNDARIES_AFTER_SPLIT", "legacy_product_ref": "product.master_reference_data", "product_refs": ["product.master_data_governance", "product.reference_data_governance"], "library_refs": ["library.master_data.domain_identity", "library.master_data.source_authority", "library.master_data.stewardship_case", "library.master_data.survivorship_projection", "library.reference_data.code_set_lifecycle", "library.reference_data.crosswalk_mapping", "library.reference_data.reference_set"], "finding": "Master entities and reference/code systems have independent sovereign questions, authorities, users, adoption paths, states, outputs and standards; the global corpus now retains them as separate product boundaries without a compatibility alias.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.entity.binding.reclassify-master.v1", "candidate_disposition": "RECLASSIFY_MASTER_LIBRARIES_FROM_ENTITY_PRODUCT_OWNERSHIP_TO_CAPABILITY_IMPORTS", "product_ref": "product.entity_resolution", "library_refs": ["library.gmo.golden_record_edition", "library.master_data.domain_identity", "library.master_data.source_authority", "library.master_data.stewardship_case", "library.master_data.survivorship_projection"], "finding": "Entity Resolution may offer resolution assertions and cluster editions to mastering, but it does not issue master identities or own field authority, survivorship, golden projection or stewardship effects.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
        {"finding_id": "finding.entity.canonicalization-homonym.v1", "candidate_disposition": "SPLIT_CANONICALIZATION_HOMONYM_INTO_TYPED_OPERATIONS", "library_refs": ["library.csp.identity.canonicalization", "library.lpe.canonical-json", "library.lpe.canonical-rdf", "library.gmo.golden_record_edition"], "finding": "Byte/document canonicalization, identifier normalization, entity representative selection and master golden projection have different equality, loss, authority and lifecycle semantics.", "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0},
    ]
    for i, (ref, rationale) in enumerate(VACANCIES, 1):
        rows.append({"finding_id": f"finding.entity.library-vacancy.{i:02d}", "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED", "proposed_library_ref": ref, "library_refs": [], "finding": rationale, "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0})
    return rows


def bounded_context() -> dict[str, Any]:
    return {"slice_id": "slice.entity-resolution-mastering.v1", "retained_products": sorted(PRODUCTS),
            "superseded_product": "product.master_reference_data",
            "split_replacement_products": ["product.master_data_governance", "product.reference_data_governance"],
            "inside_entity_resolution": ["source-record occurrence profiles", "normalization/comparison", "blocking/candidate evidence", "pair assessments and decisions", "constraints and cluster editions", "review/adjudication and reversible merge/split", "evaluation and uncertainty propagation"],
            "inside_master_data_governance": ["master domain and identity issuance", "source registration and field authority", "candidate values and survivorship", "golden projections", "master relationships/hierarchies", "stewardship and publication/change propagation"],
            "inside_reference_data_governance": ["concept/code/designation semantics", "reference sets and code-system lifecycle", "value-set definition/expansion", "directional crosswalks and mapping loss", "publication/subscription"],
            "imported_owners": ["source mutation", "legal/business identity authority", "generic statistical kernels", "generic review workflow", "privacy/security", "downstream decision and business effect"],
            "non_collapse_summary": "record != entity; score != decision; pair link != cluster; cluster != master identity; source authority != survivorship; golden projection != truth; master entity != reference value; code != concept; mapping != equivalence",
            "product_boundary_candidates": [
                {"product_ref": "product.entity_resolution", "status": "RETAIN_BUT_NARROW_UNRATIFIED"},
                {"product_ref": "product.master_data_governance", "status": "RETAINED_BOUNDARY_UNRATIFIED"},
                {"product_ref": "product.reference_data_governance", "status": "RETAINED_BOUNDARY_UNRATIFIED"}],
            "status": "CANDIDATE_UNRATIFIED", "completion_claim": False}


def build() -> dict[str, Any]:
    src = sources(); source_ids = {r["source_id"] for r in src}; mods = modules(); bindings = library_bindings(source_ids)
    axes = [{"library_ref": b["library_ref"], "axis": axis, "semantic_module_refs": b["semantic_module_refs"], "evidence_refs": b["evidence_refs"], "decision_candidate": "UNRESOLVED_RESEARCHED_CANDIDATE", "coordinate_answers": [], "owner_decision": "UNRATIFIED", "canonical_gaps_closed": 0, "completion_claim": False} for b in bindings for axis in AXES]
    result = {"sources": src, "modules": mods, "laws": laws(), "methods": methods(), "experts": experts(), "innovations": innovations(), "libraries": bindings, "axes": axes, "findings": findings(), "context": bounded_context()}
    result["summary"] = {"slice_id": "slice.entity-resolution-mastering.v1", "as_of": AS_OF,
        "primary_or_official_sources": len(src), "semantic_modules": len(mods), "non_collapse_laws": len(LAW_STATEMENTS),
        "method_types": sum(map(len, METHOD_GROUPS.values())), "expert_learning_profiles": len(EXPERT_ROWS), "recent_innovations": len(INNOVATION_ROWS),
        "declared_product_libraries": len(declared_product_libraries()), "justified_neighbor_libraries": len(NEIGHBORS), "bound_libraries": len(LIBRARIES),
        "library_axis_decision_candidates": len(axes), "retained_split_products": 2, "candidate_new_library_vacancies": len(VACANCIES),
        "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0, "canonical_gaps_closed": 0, "completion_claim": False}
    return result


def outputs() -> dict[str, str]:
    b = build()
    files = {
        "primary-sources.jsonl": "".join(canonical(r) + "\n" for r in b["sources"]),
        "semantic-modules.jsonl": "".join(canonical(r) + "\n" for r in b["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(r) + "\n" for r in b["laws"]),
        "entity-resolution-master-reference-method-taxonomy.jsonl": "".join(canonical(r) + "\n" for r in b["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(r) + "\n" for r in b["experts"]),
        "innovation-records.jsonl": "".join(canonical(r) + "\n" for r in b["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(r) + "\n" for r in b["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(r) + "\n" for r in b["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(r) + "\n" for r in b["findings"]),
        "bounded-context.json": json.dumps(b["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(b["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.entity-resolution-mastering-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    s = build()["summary"]
    print(f"BUILD PASS entity-resolution/master/reference semantic slice: {s['semantic_modules']} modules, {s['method_types']} methods, {s['bound_libraries']} libraries, {s['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
