#!/usr/bin/env python3
"""Deterministically build the governance/metadata/ontology/MDM candidate universe.

The seed tables are editorial hypotheses. Generation removes clerical repetition; it does not
promote any record beyond candidate status. The compiler consumes emitted JSONL, never product
names or free-text heuristics.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHEMAS = ROOT / "schemas"
AS_OF = "2026-08-25"
STATUS = "candidate_pending_review"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records))


def write_manifest() -> None:
    artifacts = sorted(p for p in ROOT.rglob("*.json*") if p.name != "manifest.json" and "__pycache__" not in p.parts)
    files = {str(p.relative_to(ROOT)): {"bytes": len(p.read_bytes()), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in artifacts}
    write_json(ROOT / "manifest.json", {"manifest_id": "manifest.governance-metadata-ontology-mdm.v1", "edition": 1, "files": files, "completion_claim": False})


def tokens(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


# Primary standards, official specifications/documentation, and research. A source supports only
# the surfaces named here. A URL is evidence metadata, not proof that every implementation conforms.
SOURCE_SEEDS = [
    ("E001", "Data Catalog Vocabulary (DCAT) Version 3", "W3C", "consortium_standard", 2024, "https://www.w3.org/TR/vocab-dcat-3/", "catalog;dataset;distribution;data service;versioning"),
    ("E002", "PROV-DM: The PROV Data Model", "W3C", "consortium_standard", 2013, "https://www.w3.org/TR/prov-dm/", "provenance;entity;activity;agent;derivation"),
    ("E003", "PROV-O: The PROV Ontology", "W3C", "consortium_standard", 2013, "https://www.w3.org/TR/prov-o/", "provenance ontology;qualified relations;interchange"),
    ("E004", "SKOS Simple Knowledge Organization System Reference", "W3C", "consortium_standard", 2009, "https://www.w3.org/TR/skos-reference/", "concept scheme;preferred label;alternative label;broader narrower;mapping"),
    ("E005", "OWL 2 Web Ontology Language Direct Semantics", "W3C", "consortium_standard", 2012, "https://www.w3.org/TR/owl2-direct-semantics/", "ontology;formal semantics;inference;consistency"),
    ("E006", "Shapes Constraint Language (SHACL)", "W3C", "consortium_standard", 2017, "https://www.w3.org/TR/shacl/", "graph shape;constraint;validation report;severity"),
    ("E007", "SHACL 1.2 Core Working Draft", "W3C", "working_draft", 2026, "https://www.w3.org/TR/shacl12-core/", "graph shape;constraint;rules;validation"),
    ("E008", "Data on the Web Best Practices: Data Quality Vocabulary", "W3C", "consortium_standard", 2016, "https://www.w3.org/TR/vocab-dqv/", "quality measurement;metric;annotation;certificate"),
    ("E009", "ODRL Information Model 2.2", "W3C", "consortium_standard", 2018, "https://www.w3.org/TR/odrl-model/", "policy statement;permission;prohibition;duty;assignee"),
    ("E010", "Data Privacy Vocabulary (DPV) 2.1", "W3C Data Privacy Vocabularies and Controls CG", "community_specification", 2024, "https://w3c.github.io/dpv/2.1/dpv/", "personal data;purpose;processing;legal basis;technical measure"),
    ("E011", "RDF 1.1 Concepts and Abstract Syntax", "W3C", "consortium_standard", 2014, "https://www.w3.org/TR/rdf11-concepts/", "RDF graph;IRI;literal;dataset;named graph"),
    ("E012", "RDF 1.2 Concepts and Abstract Data Model", "W3C", "working_draft", 2026, "https://www.w3.org/TR/rdf12-concepts/", "triple term;statement annotation;directional string;RDF dataset"),
    ("E013", "SPARQL 1.1 Query Language", "W3C", "consortium_standard", 2013, "https://www.w3.org/TR/sparql11-query/", "graph query;entailment;federation;result semantics"),
    ("E014", "SPARQL 1.2 Query Language Working Draft", "W3C", "working_draft", 2026, "https://www.w3.org/TR/sparql12-query/", "graph query;triple terms;versioned query semantics"),
    ("E015", "The RDF Data Cube Vocabulary", "W3C", "consortium_standard", 2014, "https://www.w3.org/TR/vocab-data-cube/", "dimension;measure;attribute;observation;integrity"),
    ("E016", "Metadata Vocabulary for Tabular Data", "W3C", "consortium_standard", 2015, "https://www.w3.org/TR/tabular-metadata/", "table metadata;column;foreign key;datatype;dialect"),
    ("E017", "JSON-LD 1.1", "W3C", "consortium_standard", 2020, "https://www.w3.org/TR/json-ld11/", "linked data;context;IRI expansion;graph serialization"),
    ("E018", "The Profiles Vocabulary", "W3C", "working_group_note", 2019, "https://www.w3.org/TR/dx-prof/", "profile;resource descriptor;constraint language;conformance"),
    ("E019", "Time Ontology in OWL", "W3C", "consortium_standard", 2022, "https://www.w3.org/TR/owl-time/", "temporal entity;instant;interval;reference system"),
    ("E020", "Semantic Sensor Network Ontology 2023 Edition", "W3C and OGC", "consortium_standard", 2023, "https://www.w3.org/TR/vocab-ssn-2023/", "observation;procedure;system;feature of interest;property"),
    ("E021", "DCMI Metadata Terms", "Dublin Core Metadata Initiative", "community_standard", 2020, "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/", "descriptive metadata;identifier;rights;provenance;application profile"),
    ("E022", "ISO/IEC 11179-3:2023 Metadata registries — Registry common facilities", "ISO/IEC", "international_standard", 2023, "https://www.iso.org/standard/78915.html", "registry item;identification;designation;definition;classification;mapping"),
    ("E023", "ISO 704:2022 Terminology work — Principles and methods", "ISO", "international_standard", 2022, "https://www.iso.org/standard/79077.html", "object;concept;definition;designation;term formation"),
    ("E024", "ISO 8000-110:2021 Master data exchange", "ISO", "international_standard", 2021, "https://www.iso.org/standard/78501.html", "master data;semantic encoding;data specification;conformance"),
    ("E025", "ISO 8000-114:2024 Portable data", "ISO", "international_standard", 2024, "https://www.iso.org/standard/83104.html", "portable data;semantic encoding;metadata;reference data"),
    ("E026", "ISO 8000-115:2024 Quality identifiers", "ISO", "international_standard", 2024, "https://www.iso.org/standard/88847.html", "identifier owner;resolution;quality identifier;master data"),
    ("E027", "ISO/IEC 38505-1:2017 Governance of data", "ISO/IEC", "international_standard", 2017, "https://www.iso.org/standard/56639.html", "governing body;evaluate;direct;monitor;accountability"),
    ("E028", "ISO/IEC TR 38505-2:2018 Implications for data management", "ISO/IEC", "technical_report", 2018, "https://www.iso.org/standard/70911.html", "data accountability map;management;governance evidence"),
    ("E029", "ISO 15489-1:2016 Records management", "ISO", "international_standard", 2016, "https://www.iso.org/standard/62542.html", "record;retention;disposition;authenticity;reliability"),
    ("E030", "ISO/IEC 25012:2008 Data quality model", "ISO/IEC", "international_standard", 2008, "https://www.iso.org/standard/35736.html", "data quality;accuracy;completeness;consistency;traceability"),
    ("E031", "ISO 3166 Country codes", "ISO", "international_standard", 2020, "https://www.iso.org/iso-3166-country-codes.html", "reference code;maintenance agency;country identifier;change"),
    ("E032", "Ontology Definition Metamodel 1.1", "Object Management Group", "industry_standard", 2014, "https://www.omg.org/spec/ODM/1.1", "ontology metamodel;RDF;OWL;logic;mappings"),
    ("E033", "Multiple Vocabulary Facility 1.0", "Object Management Group", "industry_standard", 2024, "https://www.omg.org/spec/MVF/1.0", "vocabulary;designation;multiple language;concept model"),
    ("E034", "Financial Industry Business Ontology", "Object Management Group and EDM Council", "industry_standard", 2024, "https://spec.edmcouncil.org/fibo/", "domain ontology;finance;legal entity;reference data"),
    ("E035", "Business Motivation Model 1.3", "Object Management Group", "industry_standard", 2015, "https://www.omg.org/spec/BMM/1.3", "policy;rule;directive;authority;governance motivation"),
    ("E036", "Structured Metrics Metamodel 1.2", "Object Management Group", "industry_standard", 2018, "https://www.omg.org/spec/SMM/1.2", "measure;measurement;metric;scope;library"),
    ("E037", "GS1 Global Data Synchronisation Network standards", "GS1", "industry_standard", 2025, "https://www.gs1.org/standards/gdsn", "product master data;data pool;synchronization;validation"),
    ("E038", "GS1 Global Data Model 2.14", "GS1", "industry_standard", 2025, "https://www.gs1.org/standards/gs1-global-data-model", "product attributes;harmonization;code list;governance"),
    ("E039", "GLEIF Common Data File formats", "Global Legal Entity Identifier Foundation", "industry_standard", 2021, "https://www.gleif.org/en/lei-data/access-and-use-lei-data/supporting-documents", "legal entity;relationship;golden copy;delta file;history"),
    ("E040", "Global LEI System policies", "LEI Regulatory Oversight Committee", "regulatory_standard", 2024, "https://www.leiroc.org/leiroc_gls/index.htm", "identifier authority;legal entity;relationship;validation"),
    ("E041", "SDMX 3.1 Specifications", "SDMX Sponsors", "industry_standard", 2025, "https://docs.sdmx.org/en/3.1.0/", "code list;concept scheme;data structure;constraint;statistics"),
    ("E042", "XBRL 2.1 Specification", "XBRL International", "industry_standard", 2013, "https://specifications.xbrl.org/spec-group-index-xbrl-2.1.html", "taxonomy;concept;fact;unit;context;validation"),
    ("E043", "ISO 20022 External Code Sets", "ISO 20022 Registration Authority", "industry_standard", 2025, "https://www.iso20022.org/catalogue-messages/additional-content-messages/external-code-sets", "reference code set;registration authority;version;finance"),
    ("E044", "HL7 FHIR R5 Terminology Module", "HL7 International", "industry_standard", 2023, "https://hl7.org/fhir/R5/terminology-module.html", "code system;value set;concept map;validation;version"),
    ("E045", "DICOM Current Standard", "DICOM Standards Committee and NEMA", "industry_standard", 2026, "https://www.dicomstandard.org/current/", "controlled terminology;identifier;schema;conformance;medical imaging"),
    ("E046", "ICD-11 Reference Guide", "World Health Organization", "intergovernmental_standard", 2024, "https://icdcdn.who.int/icd11referenceguide/en/html/index.html", "classification;code;foundation;linearization;health"),
    ("E047", "OpenLineage Specification", "OpenLineage / Linux Foundation", "open_specification", 2026, "https://openlineage.io/docs/spec/", "job;run;dataset;facet;lineage event"),
    ("E048", "Apache Atlas documentation", "Apache Software Foundation", "official_oss_documentation", 2025, "https://atlas.apache.org/", "type system;entity;classification;lineage;glossary"),
    ("E049", "DataHub metadata model and concepts", "DataHub Project", "official_oss_documentation", 2026, "https://docs.datahub.com/docs/what-is-datahub/datahub-concepts", "metadata aspect;URN;domain;glossary;assertion;ownership"),
    ("E050", "OpenMetadata schemas and API", "OpenMetadata Project", "official_oss_documentation", 2026, "https://docs.open-metadata.org/latest/main-concepts/metadata-standard/schemas", "entity schema;data product;contract;classification;workflow"),
    ("E051", "Egeria Open Metadata and Governance", "LF AI & Data / Egeria", "official_oss_documentation", 2025, "https://egeria-project.org/concepts/", "open metadata type;cohort;governance action;lineage;federation"),
    ("E052", "Amundsen architecture", "LF AI & Data / Amundsen", "official_oss_documentation", 2024, "https://www.amundsen.io/amundsen/architecture/", "catalog search;metadata ingestion;lineage;popularity"),
    ("E053", "JSON Schema Draft 2020-12", "JSON Schema", "open_specification", 2020, "https://json-schema.org/draft/2020-12", "runtime schema;vocabulary;validation;annotation;reference"),
    ("E054", "Apache Avro Specification", "Apache Software Foundation", "open_specification", 2025, "https://avro.apache.org/docs/current/specification/", "writer schema;reader schema;resolution;canonical form"),
    ("E055", "Protocol Buffers Language Guide", "Google", "open_specification", 2025, "https://protobuf.dev/programming-guides/proto3/", "field number;message schema;reserved field;evolution"),
    ("E056", "Schema Registry API and compatibility", "Confluent", "official_implementation_documentation", 2026, "https://docs.confluent.io/platform/current/schema-registry/develop/api.html", "subject;schema version;compatibility;registration;reference"),
    ("E057", "Apicurio Registry documentation", "Apicurio / Red Hat", "official_oss_documentation", 2026, "https://www.apicur.io/registry/docs/", "artifact;global ID;content rule;compatibility;schema registry"),
    ("E058", "OpenAPI Specification 3.1", "OpenAPI Initiative", "open_specification", 2024, "https://spec.openapis.org/oas/v3.1.1.html", "API contract;operation;schema;security;version"),
    ("E059", "AsyncAPI Specification 3.0", "AsyncAPI Initiative", "open_specification", 2024, "https://www.asyncapi.com/docs/reference/specification/v3.0.0", "event API;channel;message;operation;schema"),
    ("E060", "Open Policy Agent documentation", "Cloud Native Computing Foundation / OPA", "official_oss_documentation", 2026, "https://www.openpolicyagent.org/docs/latest/", "policy decision;input;data;bundle;enforcement point"),
    ("E061", "OpenFGA modeling language", "OpenFGA Project", "official_oss_documentation", 2026, "https://openfga.dev/docs/modeling/getting-started", "authorization model;relation;tuple;check;object"),
    ("E062", "Open Data Contract Standard 3.1", "Bitol / Linux Foundation", "open_specification", 2025, "https://bitol-io.github.io/open-data-contract-standard/latest/", "data contract;schema;quality;service level;team;terms"),
    ("E063", "Open Data Product Specification", "Bitol / Linux Foundation", "open_specification", 2025, "https://opendataproducts.org/", "data product;input;output;SLA;license;owner"),
    ("E064", "Apache Iceberg REST Catalog specification", "Apache Software Foundation", "open_specification", 2025, "https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml", "catalog protocol;namespace;table;view;commit;credential vending"),
    ("E065", "Project Nessie documentation", "Project Nessie", "official_oss_documentation", 2025, "https://projectnessie.org/nessie-latest/", "catalog version;branch;tag;commit;merge"),
    ("E066", "Apache Polaris documentation", "Apache Software Foundation", "official_oss_documentation", 2026, "https://polaris.apache.org/", "catalog;principal;role;privilege;table"),
    ("E067", "dbt Semantic Layer documentation", "dbt Labs", "official_implementation_documentation", 2026, "https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl", "semantic model;metric;entity;dimension;measure"),
    ("E068", "MetricFlow documentation", "dbt Labs / MetricFlow", "official_oss_documentation", 2026, "https://docs.getdbt.com/docs/build/about-metricflow", "metric formula;semantic join;time spine;query plan"),
    ("E069", "FIPS 199 Security Categorization", "NIST", "government_standard", 2004, "https://csrc.nist.gov/pubs/fips/199/final", "confidentiality;integrity;availability;impact;categorization"),
    ("E070", "NIST SP 800-60 Volume I Revision 1", "NIST", "government_guidance", 2008, "https://csrc.nist.gov/pubs/sp/800/60/v1/r1/final", "information type;security category;impact;mapping"),
    ("E071", "NIST Privacy Framework 1.0", "NIST", "government_framework", 2020, "https://www.nist.gov/privacy-framework/privacy-framework", "privacy risk;data processing;govern;control;communicate"),
    ("E072", "NIST Cybersecurity Framework 2.0", "NIST", "government_framework", 2024, "https://www.nist.gov/cyberframework", "govern;identify;protect;detect;respond;recover"),
    ("E073", "Records Management Lifecycle", "US National Archives and Records Administration", "government_guidance", 2025, "https://www.archives.gov/records-mgmt/policy", "record schedule;retention;disposition;legal hold;transfer"),
    ("E074", "A Theory for Record Linkage", "Journal of the American Statistical Association", "research_article", 1969, "https://doi.org/10.1080/01621459.1969.10501049", "record linkage;comparison vector;match;non-match;clerical review"),
    ("E075", "The FAIR Guiding Principles for scientific data management and stewardship", "Scientific Data", "research_article", 2016, "https://doi.org/10.1038/sdata.2016.18", "findable;accessible;interoperable;reusable;metadata;identifier"),
    ("E076", "Datasheets for Datasets", "Communications of the ACM", "research_article", 2021, "https://doi.org/10.1145/3458723", "dataset documentation;motivation;composition;collection;maintenance"),
    ("E077", "DeepMatcher: A Deep Learning Approach to Entity Matching", "ACM SIGMOD", "research_article", 2018, "https://doi.org/10.1145/3183713.3196926", "entity matching;pair classification;blocking;evaluation"),
    ("E078", "Dedupe documentation", "Dedupe.io / dedupe project", "official_oss_documentation", 2025, "https://docs.dedupe.io/", "entity resolution;active learning;blocking;clustering;gazetteer"),
    ("E079", "Splink documentation", "MoJ Analytical Services", "official_oss_documentation", 2026, "https://moj-analytical-services.github.io/splink/", "probabilistic linkage;Fellegi-Sunter;blocking;clustering;term frequency"),
    ("E080", "Zingg documentation", "ZinggAI", "official_oss_documentation", 2025, "https://docs.zingg.ai/", "entity resolution;training labels;blocking;matching;clusters"),
]


def evidence_records() -> list[dict]:
    result = []
    for sid, title, issuer, kind, year, url, supports in SOURCE_SEEDS:
        result.append({
            "record_kind": "evidence_source",
            "source_id": sid,
            "title": title,
            "issuer": issuer,
            "source_kind": kind,
            "publication_year": year,
            "url": url,
            "supports": tokens(supports),
            "does_not_establish": [
                "universal product conformance",
                "semantic equivalence outside the cited surface",
                "candidate acceptance without clause-level review",
            ],
            "retrieved_at": AS_OF,
            "status": STATUS,
        })
    return result


# slug, name, definition, owns, excludes, authority, evidence, four candidate actions
CONTEXT_SEEDS = [
    ("asset_identity", "Asset identity", "Stable identity and version identity for governable assets independent of display names.", "asset key;version key;alias binding;identity scope", "entity matching;business meaning;storage schema", "identity registrar", "E022;E021", "register identity;resolve alias;supersede identity;detect identity collision"),
    ("metadata_record", "Metadata record", "Assertions that describe an asset, with assertion source, scope, validity, and provenance.", "metadata assertion;statement provenance;validity;record version", "the described asset;domain ontology;runtime schema", "metadata publisher", "E021;E002", "publish assertion;retract assertion;query effective metadata;compare record versions"),
    ("metadata_ingestion", "Metadata ingestion", "Acquisition and normalization of metadata from source occurrences and connectors.", "harvest cursor;extraction receipt;normalization result;ingest failure", "source authority;catalog certification;business definitions", "ingestion operator", "E048;E049", "discover extractable metadata;ingest snapshot;ingest change;reconcile harvest"),
    ("technical_schema", "Technical schema", "Structural contract observed or declared for a payload, table, message, API, or file.", "field;carrier type;constraint;key;schema occurrence", "business concept;metric formula;ontology axiom", "schema publisher", "E053;E016", "register technical schema;diff technical schema;validate instance;bind field identity"),
    ("schema_registry", "Runtime schema registry", "Versioned serving and compatibility decisions for runtime serialization and interface schemas.", "subject;schema version;compatibility mode;schema reference", "business glossary;master authority;semantic metric", "schema registry authority", "E056;E057", "register schema version;check compatibility;resolve schema reference;deprecate schema subject"),
    ("semantic_model", "Semantic model", "Business-query semantics joining entities, dimensions, measures, and governed relationships.", "semantic entity;dimension;measure binding;join path;query grain", "runtime serialization;ontology inference;metric certification", "semantic model owner", "E067;E068", "define semantic entity;bind dimension;resolve join path;compile semantic query"),
    ("metric_definition", "Metric definition", "Versioned formula, grain, filters, time semantics, units, and aggregation laws for a semantic metric.", "metric formula;aggregation law;unit;grain;time window", "raw telemetry metric;catalog listing;quality score", "metric owner", "E036;E068", "define metric;typecheck formula;evaluate metric;compare metric versions"),
    ("business_glossary", "Business glossary", "Governed terms and definitions scoped to communities of practice.", "term;definition;synonym;scope;usage guidance", "formal ontology entailment;technical field type;tag membership", "glossary council", "E023;E004", "propose term;approve definition;link synonym;retire term"),
    ("terminology", "Terminology", "Concept-oriented designation work separating objects, concepts, definitions, and terms.", "concept;designation;definition;language;term status", "asset metadata;taxonomy navigation;ontology reasoning", "terminology authority", "E023;E033", "create concept entry;assign designation;validate definition;map terminologies"),
    ("taxonomy", "Taxonomy", "Controlled concept schemes and hierarchical or associative navigation relations.", "concept scheme;broader;narrower;related;notation", "necessary-and-sufficient axioms;asset ownership;record retention", "taxonomy maintainer", "E004;E041", "create concept scheme;place concept;validate hierarchy;publish taxonomy version"),
    ("ontology", "Domain ontology", "Formal domain classes, properties, individuals, and axioms under declared semantics.", "ontology IRI;axiom;import;entailment profile;consistency result", "runtime schema;glossary approval;semantic metric formula", "ontology owner", "E005;E032", "publish ontology;classify ontology;check consistency;compare entailments"),
    ("ontology_mapping", "Ontology and vocabulary mapping", "Qualified mappings between concepts or axioms without asserting unjustified equivalence.", "mapping assertion;mapping strength;direction;scope;evidence", "source concept definition;entity match;field transform", "mapping curator", "E004;E032", "propose concept mapping;validate mapping scope;publish crosswalk;retract mapping"),
    ("knowledge_graph", "Governed knowledge graph", "Materialized graph of identified assertions with provenance, shapes, and access boundaries.", "named graph;assertion identity;graph partition;graph release", "ontology semantics;master authority;policy decision", "graph custodian", "E011;E006", "ingest graph assertion;validate graph partition;publish graph release;query governed graph"),
    ("catalog_listing", "Catalog listing", "A discoverable description of an asset or service; listing does not imply endorsement.", "listing;distribution;endpoint;publisher;visibility", "certification;access grant;asset correctness", "catalog publisher", "E001;E021", "create listing;update distribution;federate listing;withdraw listing"),
    ("search_discovery", "Search and discovery", "Retrieval, browse, ranking, and recommendation signals over authorized metadata.", "index document;facet;ranking signal;query receipt", "authorization source;certification;business truth", "discovery operator", "E052;E075", "index authorized metadata;search catalog;browse facets;explain ranking"),
    ("data_product", "Data product", "A governed, consumable bundle with purpose, interfaces, owner, consumers, lifecycle, and service promises.", "product identity;purpose;ports;consumer contract;lifecycle", "individual source asset authority;access enforcement;metric formula", "data product owner", "E063;E050", "propose data product;publish product version;bind product output;retire data product"),
    ("data_contract", "Data contract", "Versioned expectations between producers and consumers for schema, semantics, quality, service, and use.", "contract version;expectation;compatibility;SLA;terms", "physical enforcement;data product identity;source schema observation", "contract parties", "E062;E050", "draft data contract;negotiate contract;validate contract;record contract breach"),
    ("ownership_accountability", "Ownership and accountability", "Decision rights and outcome accountability for data, metadata, product, policy, or meaning.", "owner assignment;accountability scope;decision right;delegation", "physical custody;steward task;access entitlement", "governing body", "E027;E028", "assign owner;delegate decision right;accept accountability;review ownership"),
    ("stewardship_work", "Stewardship work", "Operational responsibilities for definitions, quality follow-up, issue triage, and governed maintenance.", "steward assignment;work queue;attestation;escalation", "ultimate accountability;platform custody;policy authority", "stewardship lead", "E028;E049", "assign steward;attest metadata;triage governance task;escalate stewardship issue"),
    ("custody_operations", "Custody operations", "Operational possession and safekeeping of data or metadata stores.", "custodian assignment;backup duty;availability duty;operational boundary", "business ownership;policy approval;semantic definition", "platform operator", "E029;E072", "assign custodian;verify safekeeping;transfer custody;report custody failure"),
    ("policy_authority", "Policy authority", "Normative statements of permission, prohibition, duty, scope, issuer, and precedence.", "policy statement;issuer;scope;precedence;exception authority", "runtime decision execution;classification inference;legal interpretation", "policy authority", "E009;E035", "issue policy;resolve precedence;grant policy exception;retire policy"),
    ("policy_enforcement", "Policy enforcement", "Evaluation and execution of policy decisions at declared enforcement points.", "decision request;decision result;enforcement receipt;obligation result", "policy authorship;data classification;identity proofing", "enforcement operator", "E060;E061", "evaluate policy;enforce decision;execute obligation;record enforcement receipt"),
    ("classification", "Classification", "Assignment of assets or assertions to controlled classes with basis, scope, and confidence.", "classification scheme;assignment;basis;propagation rule;override", "access decision;taxonomy definition;quality certification", "classification authority", "E069;E048", "classify asset;review classification;propagate classification;remove classification"),
    ("privacy_purpose", "Privacy purpose and processing", "Purpose, processing, legal basis, data category, subject, and control metadata.", "purpose;processing category;personal-data category;legal basis;control", "legal adjudication;access enforcement;retention execution", "privacy authority", "E010;E071", "declare processing purpose;bind legal basis;assess purpose compatibility;record privacy control"),
    ("access_entitlement", "Access entitlement", "Grants and relationship tuples that authorize actions on resource scopes.", "principal;role;relation;resource scope;grant validity", "policy statement;identity proof;network enforcement", "entitlement administrator", "E061;E066", "grant entitlement;revoke entitlement;check entitlement;explain entitlement"),
    ("retention_disposition", "Retention and disposition", "Approved retention schedules, cutoff triggers, disposition actions, and execution receipts.", "record class;schedule;cutoff;retention period;disposition receipt", "legal hold authority;storage deletion mechanism;business lifecycle", "records authority", "E029;E073", "assign retention schedule;calculate disposition eligibility;authorize disposition;record disposition"),
    ("legal_hold", "Legal and investigation hold", "Suspension of otherwise eligible disposition for specified records and scope.", "hold;scope;issuer;start;release;conflict", "retention schedule;policy enforcement;legal advice", "hold authority", "E029;E073", "place hold;resolve hold scope;release hold;verify hold enforcement"),
    ("certification", "Certification", "Time-bounded attestation that explicit criteria and evidence were reviewed by an authority.", "certificate;criteria;evidence snapshot;issuer;expiry", "catalog listing;access grant;source truth", "certification authority", "E008;E018", "request certification;evaluate criteria;issue certificate;revoke certificate"),
    ("issue_workflow", "Governance issue workflow", "Typed issue, impact, assignment, remediation, verification, escalation, and closure.", "issue;state;severity;assignee;remediation;closure evidence", "quality metric definition;policy statement;asset ownership", "governance operations", "E050;E049", "open issue;triage issue;verify remediation;close issue"),
    ("change_governance", "Change governance", "Proposal, impact analysis, approval, migration, effective time, and rollback for governed assets.", "change proposal;impact;approval;migration;effective time", "artifact-specific diff semantics;deployment execution;business ownership", "change authority", "E022;E065", "propose change;analyze impact;approve change;activate change"),
    ("lineage", "Data lineage", "Declared or observed dependencies among jobs, runs, datasets, fields, and transformations.", "lineage edge;job;run;input;output;facet", "causal proof;semantic correctness;source authority", "lineage publisher", "E047;E002", "emit lineage event;resolve lineage graph;compute impact;reconcile lineage"),
    ("provenance", "Assertion provenance", "Origin, attribution, derivation, generation, and usage of entities and assertions.", "entity;activity;agent;generation;derivation;bundle", "workflow state;lineage completeness;truth", "provenance publisher", "E002;E003", "record generation;record derivation;bundle provenance;validate provenance reference"),
    ("data_quality", "Data quality", "Quality dimensions, measures, rules, observations, thresholds, and exceptions scoped to assets.", "quality rule;measure;observation;threshold;exception", "certification decision;business meaning;source correction", "quality rule owner", "E008;E030", "define quality rule;execute quality check;record observation;approve quality exception"),
    ("master_authority", "Authoritative master data", "Authority assignment and governed lifecycle for shared core business entities and attributes.", "master domain;authoritative attribute;source priority;effective version", "entity matching decision;golden projection;reference code set", "master data authority", "E024;E037", "define master domain;assign attribute authority;publish master version;reconcile authoritative source"),
    ("golden_record", "Golden record projection", "A reproducible consolidated representation selected from linked source records by survivorship rules.", "cluster projection;survivorship result;field provenance;golden version", "legal identity;source authority;match truth", "golden projection owner", "E039;E079", "build golden record;explain survivor;compare golden versions;invalidate golden projection"),
    ("reference_data", "Reference data", "Governed values used to classify or constrain other data, including versions and validity.", "reference set;value;validity;publisher;version", "master business entity;free-form tag;ontology class", "reference data authority", "E025;E041", "register reference set;publish reference version;validate reference value;retire reference value"),
    ("code_set", "Code set maintenance", "Codes, labels, meanings, statuses, and maintenance-agency change records.", "code;designation;definition;status;replacement", "entity identifier;taxonomy entailment;field encoding", "code maintenance agency", "E031;E043", "issue code;change code label;supersede code;map code versions"),
    ("entity_identity", "Entity identity", "Assertion that records refer to a real-world entity under a declared identity scope.", "entity key;identity claim;scope;identity evidence;status", "similarity score;golden representation;source record key", "identity authority", "E026;E040", "register entity identity;link identifier;split identity;retire identity"),
    ("entity_resolution", "Entity resolution", "Candidate generation and adjudication of whether records refer to the same entity.", "record pair;comparison;candidate cluster;decision;review", "authoritative identity;survivorship;source correction", "resolution service owner", "E074;E079", "generate candidates;compare records;classify pair;cluster matches"),
    ("match_policy", "Match policy", "Versioned deterministic, probabilistic, or supervised rules and thresholds for match decisions.", "blocking rule;comparison feature;threshold;model version;review band", "entity identity;merge execution;golden survivor", "match policy owner", "E074;E078", "define blocking rule;fit match parameters;set thresholds;evaluate match policy"),
    ("merge_survivorship", "Merge and survivorship", "Reversible source-record consolidation and field-level survivor selection.", "merge plan;survivorship rule;source precedence;undo receipt", "match likelihood;master authority;code-set maintenance", "survivorship authority", "E039;E079", "propose merge;select survivors;execute reversible merge;unmerge records"),
    ("hierarchy", "Hierarchy management", "Versioned parent-child, polyhierarchical, ordering, validity, and cycle constraints.", "node;edge;root;path;effective interval;closure", "taxonomy semantics;entity matching;organizational authority", "hierarchy owner", "E004;E041", "add hierarchy edge;move subtree;validate acyclicity;publish hierarchy version"),
    ("identifier_registry", "Identifier registry", "Namespaces, issuers, syntax, resolution, uniqueness, persistence, and lifecycle of identifiers.", "namespace;issuer;identifier;resolution rule;status", "entity matching;asset metadata;display label", "identifier registrar", "E022;E026", "register namespace;issue identifier;resolve identifier;reassign prohibited identifier"),
    ("crosswalk", "Crosswalk and mapping registry", "Qualified transformations and correspondences among schemas, code sets, terms, and identifiers.", "source version;target version;mapping kind;transform;loss profile", "source authority;ontology equivalence;match truth", "mapping authority", "E022;E004", "register crosswalk;validate mapping coverage;execute mapping;retire crosswalk"),
    ("metadata_federation", "Metadata federation", "Exchange, harvesting, precedence, deduplication, and provenance across catalogs and registries.", "peer;harvest token;federated assertion;precedence;conflict", "source catalog governance;asset authority;global truth", "federation operator", "E001;E051", "join federation;harvest peer;resolve assertion conflict;leave federation"),
    ("audit_evidence", "Governance audit evidence", "Immutable or append-oriented receipts for approvals, decisions, enforcement, changes, and reviews.", "receipt;evidence object;actor;time;scope;integrity proof", "policy decision logic;business truth;legal conclusion", "audit custodian", "E027;E072", "record governance receipt;verify evidence integrity;export audit package;apply evidence retention"),
    ("lifecycle_deprecation", "Lifecycle and deprecation", "Candidate, active, deprecated, superseded, retired, and tombstoned states with transition law.", "lifecycle state;transition;successor;notice;sunset", "retention disposition;business ownership;physical deletion", "lifecycle authority", "E001;E022", "activate asset;deprecate asset;name successor;retire asset"),
    ("access_request", "Catalog access request workflow", "Human request, justification, approval, provisioning handoff, expiry, and revocation evidence.", "request;purpose;approver;decision;provisioning receipt;expiry", "entitlement semantics;policy statement;identity proof", "access workflow owner", "E009;E061", "submit access request;approve access request;provision approved access;expire access request"),
    ("vertical_profile", "Vertical governance profile", "Industry-specific refinement that binds horizontal contexts to regulated identifiers, codes, evidence, and authority.", "profile;required context;external standard;vertical invariant;conformance test", "horizontal primitive redefinition;vendor product mapping;legal advice", "vertical standards owner", "E018;E044", "register vertical profile;validate profile dependency;bind vertical code;test vertical conformance"),
    ("compiler_gap", "Compiler gap and refusal", "Typed representation of unknown semantics, missing authority, unsupported mapping, or insufficient evidence.", "gap type;missing requirement;evidence;remediation;retry condition", "best-effort guess;silent default;product fallback", "compiler contract", "E022;E075", "emit typed gap;refuse unsafe compilation;accept remediation;close gap"),
]


def context_records() -> list[dict]:
    records = []
    for slug, name, definition, owns, excludes, authority, evidence, actions in CONTEXT_SEEDS:
        records.append({
            "record_kind": "bounded_context_candidate",
            "context_id": f"gmo.context.{slug}",
            "name": name,
            "definition": definition,
            "owns": tokens(owns),
            "explicitly_excludes": tokens(excludes),
            "authority_role": authority,
            "candidate_actions": tokens(actions),
            "evidence_refs": tokens(evidence),
            "status": STATUS,
        })
    return records


# Term records deliberately keep overloaded senses apart. A shared spelling is not an alias.
TERM_SEEDS = [
    ("metadata", "An assertion that describes another resource or assertion, with scope and provenance.", "metadata_record", "data value;domain axiom;runtime payload", "metadata", "E021;E002"),
    ("metadata record", "A versioned container of metadata assertions; it is not the described asset.", "metadata_record", "asset;data record", "record", "E021;E022"),
    ("metadata assertion", "A scoped proposition about an identified subject, predicate, value, source, and validity.", "metadata_record", "unqualified tag;data fact", "assertion", "E002;E011"),
    ("asset", "An identified governable resource such as a dataset, service, schema, term, policy, or product.", "asset_identity", "physical possession;accounting asset", "asset", "E001;E022"),
    ("dataset", "A collection of data published or curated as a unit, distinct from any distribution.", "catalog_listing", "file distribution;database instance;data product", "dataset", "E001;E075"),
    ("data product", "A lifecycle-managed consumable bundle with purpose, owner, interfaces, consumers, and promises.", "data_product", "dataset;catalog listing;dashboard", "product", "E063;E050"),
    ("catalog", "A governed collection of listings and services for discovery.", "catalog_listing", "storage namespace;schema registry;shopping catalog", "catalog", "E001;E052"),
    ("listing", "A discoverable description of a resource; publication alone is not endorsement.", "catalog_listing", "certificate;access grant", "catalog", "E001;E021"),
    ("certification", "A time-bounded attestation against explicit criteria and an evidence snapshot.", "certification", "listing;classification;validation pass", "certification", "E008;E018"),
    ("glossary", "A governed collection of scoped terms and definitions for a community.", "business_glossary", "taxonomy;ontology;dictionary of fields", "vocabulary", "E023;E049"),
    ("term", "A designation used to represent a concept in a language or community.", "terminology", "concept;identifier;field name", "term", "E023;E033"),
    ("concept", "A unit of knowledge distinguished from the term used to designate it.", "terminology", "class extension;tag;string", "concept", "E023;E004"),
    ("definition", "A statement representing a concept and distinguishing it from related concepts.", "terminology", "label;description;formula", "definition", "E023;E021"),
    ("designation", "A sign, term, appellation, symbol, or other representation of a concept.", "terminology", "definition;identifier assignment", "designation", "E023;E033"),
    ("synonym", "A designation accepted as having the same scoped concept referent, not merely similar text.", "business_glossary", "related term;mapping;alias of an asset", "synonym", "E004;E023"),
    ("taxonomy", "A controlled concept scheme organized for navigation by hierarchical or associative relations.", "taxonomy", "formal ontology;file-folder tree;classification assignment", "vocabulary", "E004;E041"),
    ("ontology", "A formal specification of domain classes, properties, individuals, axioms, and semantics.", "ontology", "glossary;taxonomy;runtime schema;knowledge graph data", "model", "E005;E032"),
    ("ontology class", "A class expression interpreted under an ontology semantics.", "ontology", "security classification;programming class;taxonomy concept", "class", "E005;E032"),
    ("tag", "A loosely governed label attached for retrieval or grouping.", "classification", "glossary term;ontology class;security classification", "class", "E049;E048"),
    ("classification", "A controlled scheme or an evidence-bearing assignment to a class, depending on qualified sense.", "classification", "taxonomy hierarchy;access decision", "class", "E069;E048"),
    ("technical schema", "A structural contract for carriers, fields, keys, constraints, and compatibility.", "technical_schema", "domain ontology;semantic model;metric formula", "schema", "E053;E016"),
    ("runtime schema", "A versioned schema resolved at serialization, interface, or message-processing time.", "schema_registry", "catalog metadata;ontology;database conceptual model", "schema", "E054;E056"),
    ("semantic model", "A query-oriented model of entities, dimensions, measures, joins, and grain.", "semantic_model", "ontology;runtime schema;statistical model", "model", "E067;E068"),
    ("metric", "A named semantic calculation with formula, grain, time behavior, unit, filters, and aggregation laws.", "metric_definition", "quality metric;telemetry series;physical measure", "metric", "E036;E068"),
    ("measure", "A quantified property or computation input whose aggregation semantics must be declared.", "semantic_model", "metric definition;measurement act;unit", "metric", "E015;E036"),
    ("quality metric", "A function and scale used to quantify a quality dimension for a scoped resource.", "data_quality", "business metric;certificate;quality rule", "metric", "E008;E030"),
    ("master data", "Shared core business entity data governed for reuse across processes or systems.", "master_authority", "transaction data;reference code set;golden projection", "master", "E024;E037"),
    ("authoritative master", "Master attributes published under explicit decision rights and source authority.", "master_authority", "golden record;replica;source-of-truth slogan", "master", "E024;E027"),
    ("golden record", "A reproducible consolidated projection from linked records and survivorship rules.", "golden_record", "authoritative master;legal identity;source row", "golden", "E039;E079"),
    ("golden copy", "A publisher-produced high-frequency complete file, possibly with delta files, for distribution.", "catalog_listing", "golden record;authoritative master", "golden", "E039;E040"),
    ("reference data", "Governed values used to classify, validate, or constrain other data.", "reference_data", "master entity;lookup cache;free text", "reference", "E025;E041"),
    ("reference code set", "A versioned set of codes and meanings maintained by an authority.", "code_set", "identifier namespace;taxonomy alone;enum carrier", "reference", "E031;E043"),
    ("entity", "A real-world or conceptual thing whose identity scope is declared.", "entity_identity", "source record;RDF entity in provenance;table row", "entity", "E040;E074"),
    ("identity", "The governed claim that an identifier or record denotes one entity in a scope.", "entity_identity", "similarity;authentication;record key", "identity", "E026;E040"),
    ("identifier", "A symbol issued within a namespace to identify a resource under declared lifecycle rules.", "identifier_registry", "display name;matching key;database surrogate alone", "identity", "E022;E026"),
    ("source key", "An identifier local to a source occurrence and namespace.", "asset_identity", "enterprise identity;match result;global identifier", "identity", "E022;E074"),
    ("match", "An adjudicated or scored assertion that two records may denote the same entity.", "entity_resolution", "string equality;identity;merge", "match", "E074;E079"),
    ("entity resolution", "Candidate generation, comparison, adjudication, and clustering for co-reference.", "entity_resolution", "identifier issuance;survivorship;search", "match", "E074;E078"),
    ("merge", "A governed and preferably reversible consolidation of records or identities.", "merge_survivorship", "match decision;union of schemas;overwrite", "merge", "E039;E079"),
    ("survivorship", "Field-level selection or derivation rules for a consolidated projection.", "merge_survivorship", "source authority;matching;retention", "golden", "E039;E079"),
    ("hierarchy", "A versioned parent-child relation with declared root, order, validity, and cycle laws.", "hierarchy", "taxonomy semantics;filesystem path;organizational chart instance", "hierarchy", "E004;E041"),
    ("lineage", "Dependencies among data, fields, jobs, and runs, whether declared or observed.", "lineage", "complete causality;provenance of every assertion;ownership", "lineage", "E047;E002"),
    ("provenance", "Information about entities, activities, agents, derivation, generation, and usage.", "provenance", "lineage completeness;truth;chain of custody alone", "lineage", "E002;E003"),
    ("owner", "A role accountable for decisions and outcomes in a declared scope.", "ownership_accountability", "custodian;steward;creator;IAM object owner", "owner", "E027;E028"),
    ("steward", "A role responsible for operational governance work within delegated authority.", "stewardship_work", "ultimate owner;custodian;approver by default", "owner", "E028;E049"),
    ("custodian", "A role responsible for operational possession, safekeeping, and availability.", "custody_operations", "business owner;steward;policy issuer", "owner", "E029;E072"),
    ("policy statement", "A normative permission, prohibition, duty, or rule issued under authority.", "policy_authority", "runtime decision;control implementation;free-form guideline", "policy", "E009;E035"),
    ("policy decision", "An evaluation result for supplied identity, resource, action, and context inputs.", "policy_enforcement", "policy statement;entitlement tuple;legal opinion", "policy", "E060;E061"),
    ("enforcement", "Execution of an allow, deny, redact, filter, transform, or obligation at an enforcement point.", "policy_enforcement", "policy authorship;certification;classification", "policy", "E060;E066"),
    ("entitlement", "A grant or relationship that contributes to authorization for an action on a resource.", "access_entitlement", "policy;authentication;catalog visibility", "policy", "E061;E066"),
    ("retention", "The period and conditions for keeping records before an authorized disposition.", "retention_disposition", "backup duration;business usefulness;legal hold", "retention", "E029;E073"),
    ("disposition", "An authorized records action such as destruction, transfer, or permanent preservation.", "retention_disposition", "soft delete;deprecation;storage compaction", "retention", "E029;E073"),
    ("legal hold", "A scoped suspension of disposition until explicitly released by the hold authority.", "legal_hold", "retention rule;classification;access deny", "retention", "E029;E073"),
    ("record", "Information created, received, and maintained as evidence and an asset of an activity.", "retention_disposition", "row;JSON object;metadata record", "record", "E029;E073"),
    ("data record", "A structured collection of fields in a dataset or message.", "technical_schema", "records-management record;metadata record;entity", "record", "E016;E054"),
    ("version", "An identified state intended to coexist or be addressed separately from other states.", "lifecycle_deprecation", "revision event;edition label;timestamp", "version", "E001;E022"),
    ("revision", "An event or change that produces, amends, or records a version.", "change_governance", "version identity;correction;release", "version", "E001;E065"),
    ("deprecation", "A lifecycle state warning against new use while preserving identity and migration guidance.", "lifecycle_deprecation", "deletion;revocation;retention expiry", "version", "E022;E053"),
    ("data contract", "A versioned agreement of producer and consumer expectations for a data interface.", "data_contract", "technical schema;policy;data product", "contract", "E062;E050"),
    ("service level", "A measurable service expectation with scope, method, window, threshold, and consequence.", "data_contract", "quality observation;business metric;support promise in prose", "contract", "E062;E063"),
    ("domain", "A bounded area of business meaning and accountability, not a DNS name or datatype set.", "ownership_accountability", "internet domain;value domain;ontology domain axiom", "domain", "E027;E049"),
    ("source", "An identified origin of an assertion or data occurrence with authority and observation limits.", "provenance", "connector;citation alone;source code", "source", "E002;E047"),
    ("authority", "A granted right to decide, publish, approve, or enforce within a scope.", "ownership_accountability", "popularity;technical access;custody", "authority", "E027;E028"),
    ("system of record", "A source occurrence granted authority for specified entities or attributes in a scope.", "master_authority", "single universal database;golden record;replica", "source", "E024;E027"),
    ("source of truth", "An unsafe slogan unless expanded to field, scope, time, decision right, and evidence.", "compiler_gap", "system of record;authoritative publication;latest replica", "source", "E027;E022"),
    ("quality", "Fitness characteristics measured for a declared object, use, method, and time.", "data_quality", "truth;certification;popularity", "quality", "E008;E030"),
    ("governance issue", "A typed deviation or uncertainty requiring accountable workflow and closure evidence.", "issue_workflow", "quality observation;incident alarm;discussion comment", "issue", "E049;E050"),
    ("distribution", "An accessible representation of a dataset, distinct from the dataset abstraction.", "catalog_listing", "dataset;source occurrence;data product", "dataset", "E001;E021"),
    ("crosswalk", "A versioned set of qualified correspondences or transformations between schemes.", "crosswalk", "equivalence;entity match;schema union", "mapping", "E004;E022"),
    ("mapping", "A directional, scoped correspondence or transform whose information loss is declared.", "crosswalk", "identity;equivalence;lineage edge", "mapping", "E004;E032"),
    ("equivalence", "A strong semantic assertion valid only under a declared formalism and scope.", "ontology_mapping", "similarity;close mapping;same label", "mapping", "E004;E005"),
    ("compatibility", "Ability of specified producer/consumer versions to interoperate under a named rule.", "schema_registry", "semantic equivalence;validation;non-breaking UI", "compatibility", "E054;E056"),
    ("validation", "Evaluation of an instance or artifact against explicit constraints producing a report.", "technical_schema", "truth;certification;compatibility", "validation", "E006;E053"),
    ("conformance", "Satisfaction of identified requirements in a specification or profile with evidence.", "certification", "validation pass alone;implementation claim;compatibility", "validation", "E018;E006"),
]


def term_records() -> list[dict]:
    return [{
        "record_kind": "ubiquitous_language_candidate",
        "term_id": f"gmo.term.{owner}.{term.lower().replace(' ', '_').replace('-', '_')}",
        "term": term,
        "definition": definition,
        "owning_context": f"gmo.context.{owner}",
        "must_not_be_conflated_with": tokens(contrasts),
        "homonym_group": homonym,
        "evidence_refs": tokens(evidence),
        "status": STATUS,
    } for term, definition, owner, contrasts, homonym, evidence in TERM_SEEDS]


def capability_operation_records(contexts: list[dict]) -> list[dict]:
    records: list[dict] = []
    for context in contexts:
        slug = context["context_id"].rsplit(".", 1)[-1]
        cap_id = f"gmo.capability.{slug}"
        op_ids = []
        for pos, action in enumerate(context["candidate_actions"], start=1):
            action_slug = action.replace(" ", "_").replace("/", "_")
            op_id = f"gmo.operation.{slug}.{action_slug}"
            op_ids.append(op_id)
            effect = "read_only" if action.split()[0] in {"query", "compare", "check", "resolve", "validate", "explain", "browse", "search", "compute", "calculate", "assess", "verify", "test", "evaluate", "discover"} else "governed_state_change"
            records.append({
                "record_kind": "capability_operation_candidate",
                "candidate_kind": "typed_operation",
                "candidate_id": op_id,
                "name": action,
                "owner_context": context["context_id"],
                "signature": {
                    "inputs": [f"{slug}.request", "actor_context", "evidence_context"],
                    "outputs": [f"{slug}.result", "decision_or_receipt"],
                },
                "preconditions": ["subject identities resolve uniquely", "actor is authorized for the requested scope", "required versions and effective time are explicit"],
                "postconditions": ["result identifies governing versions", "decision provenance is recorded", "unknown or ambiguous semantics are not silently defaulted"],
                "effect": effect,
                "determinism": "deterministic_given_versioned_inputs_and_policy",
                "idempotency": "required_by_idempotency_key" if effect == "governed_state_change" else "naturally_idempotent_read",
                "refusals": ["gmo.refusal.unknown_identity", "gmo.refusal.missing_authority", "gmo.refusal.ambiguous_version"],
                "evidence_refs": context["evidence_refs"],
                "status": STATUS,
            })
        records.append({
            "record_kind": "capability_operation_candidate",
            "candidate_kind": "capability",
            "candidate_id": cap_id,
            "name": f"Govern {context['name']}",
            "owner_context": context["context_id"],
            "provides_operations": op_ids,
            "requires": ["versioned identity", "scoped authority", "evidence provenance", "typed refusal channel"],
            "guarantees": ["candidate state is explicit", "owner context is unique", "writes are deny-by-default", "all decisions are replayable from versioned inputs"],
            "evidence_refs": context["evidence_refs"],
            "status": STATUS,
        })
    return sorted(records, key=lambda r: r["candidate_id"])


DECISION_SEEDS = [
    ("governed_object_kind", "What is the governed object?", "asset metadata;domain concept;runtime schema;semantic formula;master entity;reference set", "The owner context and valid operations differ.", "refuse ambiguous object kind"),
    ("asset_identity_scope", "Which namespace and version identify the asset?", "global persistent;publisher scoped;source occurrence scoped;content addressed;composite", "Aliases and versions cannot be resolved without scope.", "emit unknown identity scope"),
    ("assertion_authority", "Who may assert, approve, or retract this metadata?", "source publisher;domain council;owner;steward;automated observation", "Observation, proposal, and authoritative approval are distinct.", "keep assertion unapproved"),
    ("assertion_valid_time", "When is the assertion effective and when was it recorded?", "valid time only;recorded time only;bitemporal;timeless", "Latest recorded is not necessarily currently effective.", "require explicit temporal model"),
    ("glossary_taxonomy_ontology", "Which semantic artifact is required?", "glossary;taxonomy;ontology;semantic model;crosswalk", "Each has different laws and execution behavior.", "refuse label-driven substitution"),
    ("ontology_profile", "Which ontology semantics and reasoning profile apply?", "RDFS;OWL 2 EL;OWL 2 QL;OWL 2 RL;OWL 2 DL;custom declared", "Entailments and consistency costs vary.", "emit unsupported entailment profile"),
    ("shape_world_assumption", "Is constraint evaluation closed-world for the scoped graph?", "closed shape;open shape;mixed property closure", "OWL open-world inference and SHACL validation cannot be conflated.", "require declared validation scope"),
    ("catalog_endorsement", "Is the request for listing or certification?", "list only;list with quality signals;certify against criteria", "Discovery does not prove fitness or approval.", "never infer certification from listing"),
    ("search_authorization", "Which metadata may the requester discover?", "public listing;authorized metadata;field-redacted metadata;existence hidden", "Search indexes can leak sensitive existence and terms.", "deny indexing or result without visibility decision"),
    ("product_boundary", "What belongs to the data product and what remains an external dependency?", "owned output;input dependency;documentation;contract;policy reference", "Asset collection alone does not create product ownership.", "emit incomplete product boundary"),
    ("contract_scope", "At what interface and version does the data contract apply?", "dataset;table;topic;API;file distribution;product output", "A contract cannot govern an unidentified moving target.", "require interface identity and version"),
    ("contract_inheritance", "How do product and asset contracts combine?", "asset overrides;product defaults;intersection;explicit precedence", "Implicit inheritance can weaken obligations.", "refuse unresolved contract precedence"),
    ("owner_role", "Is this accountability, stewardship, custody, or approval?", "accountable owner;decision delegate;steward;custodian;approver", "One generic owner field destroys decision rights.", "require qualified role and scope"),
    ("policy_execution", "Is the artifact a policy statement or an enforcement implementation?", "statement;decision service;enforcement point;obligation worker", "A published policy is not evidence of enforcement.", "never claim enforcement without receipt"),
    ("classification_basis", "What evidence and scope support a classification assignment?", "manual attestation;rule;inherited;lineage propagated;source asserted", "Labels without basis cannot safely drive controls.", "keep assignment provisional"),
    ("classification_propagation", "May classification propagate through lineage?", "none;copy;join maximum;transform rule;manual review", "Propagation is not universally sound, especially for aggregation or de-identification.", "refuse undeclared propagation"),
    ("privacy_purpose_compatibility", "Is a proposed use compatible with the declared purpose and legal basis?", "compatible;requires new basis;prohibited;requires human/legal review", "Purpose metadata is not a legal decision by itself.", "route to qualified authority"),
    ("entitlement_semantics", "Which authorization model composes grants?", "RBAC;ABAC;ReBAC;ACL;capability token;hybrid", "Tuple presence alone may not imply allow.", "deny on unresolved model"),
    ("retention_trigger", "What event starts the retention clock?", "creation;case closure;contract termination;supersession;last activity;custom event", "A duration without cutoff is not executable.", "emit missing cutoff trigger"),
    ("hold_precedence", "Does a hold suspend disposition for this exact scope?", "no hold;direct hold;inherited hold;conflicting scope;released hold", "Deletion must not proceed through ambiguity.", "deny disposition"),
    ("certification_criteria", "Which criteria, evidence snapshot, issuer, and expiry define certification?", "schema;quality;security;semantic;combined profile", "A badge without criteria is not compiler-grade.", "refuse unscoped certification"),
    ("lineage_assertion_kind", "Is lineage declared, statically inferred, runtime observed, or manually asserted?", "declared;static;runtime;manual;reconciled composite", "Assurance and gaps differ by origin.", "preserve assertion kind"),
    ("field_lineage_assurance", "Is field-level lineage exact, partial, expression-derived, or unknown?", "exact;expression parsed;name mapped;partial;unknown", "Pretty graphs must not imply exact derivation.", "emit partial lineage gap"),
    ("schema_compatibility", "Which reader/writer direction and history depth are required?", "backward;forward;full;transitive variants;none", "The word compatible is incomplete without direction and versions.", "require named compatibility relation"),
    ("schema_semantic_change", "Can a structurally compatible change alter business meaning?", "no semantic change;definition change;unit change;code-set change;unknown", "Schema compatibility does not establish semantic compatibility.", "require semantic review"),
    ("metric_grain", "What population, entity, grain, time spine, and filters define the metric?", "event;entity snapshot;periodic aggregate;cohort;balance", "A formula without grain is ambiguous.", "emit missing grain"),
    ("metric_additivity", "Across which dimensions and time intervals is the measure additive?", "fully additive;semi-additive;non-additive;ratio;distinct count", "Blind summation produces invalid results.", "refuse invalid aggregation"),
    ("master_authority", "Which source or role is authoritative for each master attribute and time interval?", "single source;field authority;workflow approved;external registry;composite", "One source rarely owns every field.", "emit authority gap"),
    ("golden_vs_master", "Is the requested output an authoritative master or a golden projection?", "authoritative master;golden projection;source record;published golden copy", "Consolidation does not confer authority.", "preserve artifact kind"),
    ("reference_or_master", "Is the governed thing a reusable code/value set or a business entity?", "reference data;master entity;taxonomy concept;identifier namespace", "Different lifecycle, matching, and ownership laws apply.", "refuse ambiguous data class"),
    ("identity_or_match", "Is the request to issue identity or estimate co-reference?", "identity assertion;candidate match;confirmed match;merge;link only", "Similarity does not create identity.", "never auto-issue identity from score"),
    ("match_thresholds", "Which match, non-match, and clerical-review bands apply to a policy version?", "two-way threshold;three-way threshold;constraint-based;human-only", "Scores are not portable across populations or versions.", "require calibrated thresholds"),
    ("merge_reversibility", "Can merge effects be undone with original identifiers and field provenance?", "fully reversible;projection only;source mutation with audit;irreversible prohibited", "Irreversible merge risks identity corruption.", "deny destructive merge without authority"),
    ("survivorship_rule", "How is each golden field selected?", "source precedence;most recent valid;most complete;workflow approved;derived", "A cluster does not define survivor truth.", "emit missing survivorship rule"),
    ("hierarchy_laws", "Are multiple parents, cycles, ordering, and temporal overlap allowed?", "strict tree;DAG;polyhierarchy;general graph;temporal hierarchy", "Tree algorithms are invalid for general graphs.", "require declared hierarchy algebra"),
    ("identifier_persistence", "May identifiers be reassigned, recycled, aliased, or tombstoned?", "never reassign;persistent tombstone;controlled reassignment;ephemeral source key", "Identifier reuse can corrupt history.", "refuse undeclared reuse"),
    ("crosswalk_strength", "Is a mapping exact, broader, narrower, close, transform, or lossy?", "exact;broader;narrower;close;transform;unmapped", "Same label is not equivalence.", "preserve loss and direction"),
    ("federation_precedence", "When federated assertions conflict, which scoped precedence applies?", "source authority;newest approved;local override;quarantine;multi-valued", "Last write wins is not semantic governance.", "quarantine unresolved conflict"),
    ("change_breakingness", "Which consumers, contracts, mappings, and meanings make a change breaking?", "technical;semantic;policy;identifier;workflow;non-breaking", "A schema diff alone is incomplete impact analysis.", "block activation until impact resolved"),
    ("vertical_refinement", "Does a vertical profile refine horizontal laws without redefining them?", "valid refinement;conflicting redefinition;missing dependency;unsupported standard version", "Industry convenience must not collapse core distinctions.", "emit vertical profile conflict"),
]


def decision_records() -> list[dict]:
    return [{
        "record_kind": "decision_point_candidate",
        "decision_id": f"gmo.decision.{slug}",
        "question": question,
        "options": tokens(options),
        "why_material": why,
        "required_evidence": ["identified subject and scope", "versioned governing artifacts", "authorized decision role"],
        "default_on_unknown": refusal,
        "status": STATUS,
    } for slug, question, options, why, refusal in DECISION_SEEDS]


INVARIANT_SEEDS = [
    ("metadata_not_asset", "metadata_record", "A metadata record and the asset it describes have distinct identities.", "refuse a request that overwrites the asset when only metadata mutation is authorized"),
    ("ontology_not_schema", "ontology", "Ontology axioms do not substitute for a runtime payload schema.", "emit missing runtime schema"),
    ("schema_not_metric", "technical_schema", "A carrier type and field name do not determine a semantic metric formula.", "emit missing semantic formula"),
    ("metric_not_quality_score", "metric_definition", "Business metrics, telemetry metrics, and quality metrics remain typed separately.", "refuse untyped metric aggregation"),
    ("listing_not_certification", "catalog_listing", "Catalog publication never implies certification.", "omit certification and emit unmet assurance requirement"),
    ("certificate_expiry", "certification", "Certification identifies criteria, evidence snapshot, issuer, issue time, and expiry/review time.", "refuse badge-only certification"),
    ("policy_not_enforcement", "policy_authority", "Policy publication is not evidence that a decision was evaluated or enforced.", "require decision and enforcement receipts"),
    ("deny_default", "policy_enforcement", "Unknown, unavailable, or indeterminate authorization is not allow.", "deny with typed indeterminate reason"),
    ("owner_not_steward", "ownership_accountability", "Accountability, delegation, stewardship, custody, and approval are separately qualified roles.", "refuse generic owner mapping"),
    ("custody_not_authority", "custody_operations", "Operational custody does not grant business or policy decision rights.", "deny authority escalation from platform access"),
    ("identity_not_match", "entity_identity", "A similarity or match score cannot itself issue authoritative identity.", "emit candidate match requiring adjudication"),
    ("match_not_merge", "entity_resolution", "A match decision does not itself mutate or merge source records.", "require separately authorized merge plan"),
    ("merge_reversible", "merge_survivorship", "Original identifiers and field provenance remain recoverable for every governed merge.", "deny irreversible merge by default"),
    ("master_not_golden", "master_authority", "A golden projection does not become authoritative master data through consolidation alone.", "preserve projection status"),
    ("golden_copy_not_record", "golden_record", "A publisher golden-copy file and an MDM golden record are distinct artifacts.", "require artifact-kind qualification"),
    ("reference_not_master", "reference_data", "Reference values constrain other data; master entities participate in business identity and lifecycle.", "refuse ambiguous master/reference compilation"),
    ("code_no_reuse", "code_set", "A retired code is not reassigned unless the maintenance policy explicitly permits and versions the reuse.", "deny silent code recycling"),
    ("identifier_scope", "identifier_registry", "Identifier uniqueness and persistence claims are always scoped to namespace and issuer.", "emit unknown namespace"),
    ("hierarchy_cycle", "hierarchy", "Cycle checks use the declared hierarchy algebra and effective interval.", "reject prohibited cycle"),
    ("mapping_not_equivalence", "crosswalk", "A crosswalk mapping does not imply identity or logical equivalence.", "preserve mapping strength and loss"),
    ("skos_exact_not_owl_same", "ontology_mapping", "SKOS mapping relations are not silently upgraded to OWL equivalence.", "refuse entailment-strength escalation"),
    ("open_closed_world", "ontology", "Open-world inference and closed-world constraint validation remain distinct phases.", "require explicit phase and scope"),
    ("lineage_not_truth", "lineage", "A lineage edge does not prove source authority, transformation correctness, or completeness.", "report lineage assurance separately"),
    ("provenance_origin", "provenance", "Every authoritative assertion identifies its agent or source and derivation/generation basis.", "keep assertion untrusted or reject"),
    ("quality_scoped", "data_quality", "A quality observation identifies rule version, object, method, time, and population/sampling scope.", "reject context-free score"),
    ("classification_basis", "classification", "Every control-driving classification has a basis, scope, issuer, and review state.", "do not propagate ungrounded label"),
    ("purpose_not_permission", "privacy_purpose", "Declared purpose and legal basis metadata do not themselves grant technical access.", "require independent policy decision"),
    ("retention_cutoff", "retention_disposition", "A retention duration is not executable without record class and cutoff trigger.", "emit incomplete retention schedule"),
    ("hold_blocks_disposition", "legal_hold", "A matching active hold blocks destruction regardless of calculated disposition eligibility.", "deny disposition"),
    ("schema_direction", "schema_registry", "Compatibility identifies reader/writer direction, compared versions, history depth, and format rules.", "reject bare compatible claim"),
    ("contract_versioned", "data_contract", "Contract evaluation pins contract, interface, schema, policy, and code-set versions.", "emit ambiguous contract evaluation"),
    ("product_has_promise", "data_product", "A collection of assets without purpose, owner, consumers, ports, lifecycle, and promises is not compiled as a data product.", "emit incomplete product definition"),
    ("search_acl", "search_discovery", "Indexing and result rendering apply metadata visibility and existence-hiding rules.", "omit unauthorized document and facets"),
    ("federation_provenance", "metadata_federation", "Federation preserves source identity and never overwrites conflicting assertions without a precedence rule.", "quarantine conflict"),
    ("change_effective_time", "change_governance", "Approved change and activated effective version are separate states.", "do not activate on approval alone"),
    ("audit_append", "audit_evidence", "Governance receipts are append-oriented; correction creates a linked superseding receipt.", "reject in-place evidence rewrite"),
    ("candidate_only", "compiler_gap", "Every registry record remains a candidate until named review gates pass.", "refuse production conformance claim"),
    ("no_vendor_switch", "compiler_gap", "Compilation never selects semantics solely from a vendor/product name.", "emit missing capability evidence"),
    ("no_llm_core", "compiler_gap", "Prompt, RAG, agent-memory, and generative-model semantics are outside the horizontal core.", "route to a one-way extension namespace"),
]


def invariant_records() -> list[dict]:
    return [{
        "record_kind": "invariant_refusal_candidate",
        "invariant_id": f"gmo.invariant.{slug}",
        "owner_context": f"gmo.context.{context}",
        "statement": statement,
        "compiler_refusal": refusal,
        "severity": "hard",
        "status": STATUS,
    } for slug, context, statement, refusal in INVARIANT_SEEDS]


RELATION_SEEDS = [
    ("metadata_record", "asset_identity", "references", "read", "Metadata may reference identity but may not issue or reassign it."),
    ("metadata_ingestion", "metadata_record", "proposes", "create_provisional", "Ingestion writes observations, never approved business assertions."),
    ("metadata_ingestion", "technical_schema", "observes", "create_observed", "Observed schema stays distinct from declared schema."),
    ("schema_registry", "technical_schema", "serves_versions_of", "read_and_propose", "Registry may reject incompatible versions but does not define business meaning."),
    ("semantic_model", "technical_schema", "binds", "read", "Field bindings pin schema version and field identity."),
    ("metric_definition", "semantic_model", "compiles_against", "read", "Metric compilation cannot mutate the semantic model."),
    ("business_glossary", "terminology", "uses_concepts_from", "read_and_propose_mapping", "Glossary may adopt terms without owning terminology authority."),
    ("taxonomy", "terminology", "organizes", "read", "Hierarchy does not replace definitions."),
    ("ontology", "terminology", "formalizes", "read_and_propose_mapping", "Formalization needs explicit mapping approval."),
    ("ontology_mapping", "ontology", "maps", "read_and_propose_mapping", "Mapping curator cannot edit source ontologies."),
    ("knowledge_graph", "ontology", "conforms_to", "read", "Graph custodian does not own ontology axioms."),
    ("knowledge_graph", "provenance", "records_assertions_with", "append", "Every graph release preserves assertion provenance."),
    ("catalog_listing", "asset_identity", "lists", "read", "Catalog cannot mint source asset identity without registrar delegation."),
    ("search_discovery", "catalog_listing", "indexes", "read_authorized", "Visibility filters apply before ranking and facets."),
    ("search_discovery", "access_entitlement", "filters_by", "decision_only", "Search does not grant access."),
    ("data_product", "catalog_listing", "publishes_as", "create_listing", "Product listing is not product certification."),
    ("data_product", "data_contract", "offers_under", "read", "Contract approval remains with contract parties."),
    ("data_contract", "technical_schema", "constrains", "read", "Contract pins schema rather than rewriting it."),
    ("data_contract", "data_quality", "requires", "read", "Quality rules are referenced by version."),
    ("ownership_accountability", "stewardship_work", "delegates_work_to", "assign", "Delegation does not transfer accountability by default."),
    ("stewardship_work", "issue_workflow", "operates", "triage_and_update", "Stewards close only within delegated scope."),
    ("custody_operations", "audit_evidence", "publishes_receipts_to", "append", "Custodian cannot rewrite receipts."),
    ("policy_authority", "policy_enforcement", "supplies_policy_to", "publish_version", "Enforcer cannot silently modify policy."),
    ("policy_enforcement", "access_entitlement", "evaluates_with", "read", "Entitlement data is an input, not the whole policy."),
    ("classification", "policy_enforcement", "supplies_attribute_to", "read", "Classification does not itself allow or deny."),
    ("privacy_purpose", "policy_authority", "constrains", "read_and_review", "Legal interpretation stays outside automated core."),
    ("retention_disposition", "policy_enforcement", "requests_execution_from", "execute_authorized", "Disposition authority and physical enforcement are separate."),
    ("legal_hold", "retention_disposition", "overrides_eligibility", "deny_disposition", "Active matching hold wins."),
    ("certification", "catalog_listing", "annotates", "append_certificate", "Listing visibility does not imply certification."),
    ("certification", "data_quality", "uses_evidence_from", "read_snapshot", "Later observations do not rewrite old certificate evidence."),
    ("issue_workflow", "ownership_accountability", "escalates_to", "notify", "Issue workflow cannot reassign owner itself."),
    ("change_governance", "lifecycle_deprecation", "activates_transition_in", "request_transition", "Approval and activation are separate ACLs."),
    ("lineage", "technical_schema", "references_fields_in", "read", "Unresolved fields yield partial lineage."),
    ("lineage", "classification", "may_trigger_propagation_in", "request_review", "Lineage service cannot self-author classification policy."),
    ("provenance", "audit_evidence", "supports", "append", "Provenance record is not automatically an audit-grade receipt."),
    ("master_authority", "entity_identity", "governs_entities_from", "read_and_publish_attributes", "Master authority cannot infer identity from similarity."),
    ("golden_record", "entity_resolution", "projects_clusters_from", "read_confirmed", "Unreviewed match candidates are excluded unless policy explicitly permits."),
    ("golden_record", "merge_survivorship", "uses_rules_from", "read", "Projection does not mutate survivor rules."),
    ("reference_data", "code_set", "contains_versions_from", "read", "Reference set publisher respects code maintenance authority."),
    ("entity_resolution", "match_policy", "executes", "read_version", "Resolution pins population and policy version."),
    ("merge_survivorship", "entity_identity", "requests_identity_change_from", "propose", "Merge service cannot issue identity directly."),
    ("hierarchy", "entity_identity", "organizes", "read", "Hierarchy edge does not establish co-reference."),
    ("crosswalk", "reference_data", "maps_versions_of", "read", "Crosswalk does not modify source values."),
    ("metadata_federation", "metadata_record", "exchanges", "read_and_create_federated", "Source provenance is preserved."),
    ("audit_evidence", "retention_disposition", "is_scheduled_by", "read", "Audit store cannot self-author its schedule."),
    ("access_request", "policy_enforcement", "requests_decision_from", "decision_only", "Human approval cannot bypass policy deny."),
    ("access_request", "access_entitlement", "requests_provisioning_in", "propose_grant", "Provisioning is separately acknowledged."),
    ("vertical_profile", "compiler_gap", "emits_gap_through", "create", "Vertical conflict remains typed and visible."),
    ("compiler_gap", "audit_evidence", "records_refusal_in", "append", "A refusal is evidence, not an exception grant."),
]


def relation_records() -> list[dict]:
    return [{
        "record_kind": "context_relation_acl_candidate",
        "relation_id": f"gmo.relation.{src}.{kind}.{dst}",
        "source_context": f"gmo.context.{src}",
        "target_context": f"gmo.context.{dst}",
        "relation_kind": kind,
        "granted_access": access,
        "boundary_rule": rule,
        "write_default": "deny",
        "status": STATUS,
    } for src, dst, kind, access, rule in RELATION_SEEDS]


LIBRARY_SEEDS = [
    ("metadata_assertions", "metadata_record", "identity_kernel", "described asset mutation;source connector"),
    ("metadata_acquisition", "metadata_ingestion", "identity_kernel;metadata_assertions", "source-system semantics;approval"),
    ("terminology_core", "terminology;business_glossary", "identity_kernel;metadata_assertions", "taxonomy placement;formal entailment"),
    ("taxonomy_core", "taxonomy;hierarchy", "terminology_core;identity_kernel", "ontology reasoner;business hierarchy authority"),
    ("knowledge_graph", "knowledge_graph", "ontology_core;metadata_assertions;policy_client", "ontology ownership;policy authorship"),
    ("catalog_listing_contract", "catalog_listing", "identity_kernel;metadata_assertions;policy_client", "certification;access grant;ranking"),
    ("discovery_query", "search_discovery", "catalog_listing_contract;metadata_assertions;policy_client", "listing authority;access grant"),
    ("accountability", "ownership_accountability;stewardship_work;custody_operations", "identity_kernel;audit_receipts", "IAM entitlement;policy execution"),
    ("policy_model", "policy_authority", "identity_kernel;terminology_core", "runtime enforcement adapter"),
    ("policy_client", "policy_enforcement;access_entitlement", "policy_model;identity_kernel;audit_receipts", "policy authorship;identity proofing"),
    ("classification_assignment", "classification", "terminology_core;metadata_assertions", "privacy-purpose authority;legal advice;enforcement"),
    ("privacy_purpose_binding", "privacy_purpose", "terminology_core;policy_model;metadata_assertions", "classification authority;legal advice;enforcement"),
    ("records_governance", "retention_disposition;legal_hold", "policy_model;classification_assignment;privacy_purpose_binding;audit_receipts", "storage deletion;legal conclusion"),
    ("certification_lifecycle", "certification", "accountability;audit_receipts;quality_core", "issue remediation;change approval;artifact-specific diff engine"),
    ("assurance_appraisal_plan", "certification", "accountability;audit_receipts;quality_core", "certification issuance;appraisal execution;reliance decision"),
    ("governance_issue_workflow", "issue_workflow", "accountability;audit_receipts;quality_core", "certification issuance;change approval"),
    ("change_review_policy", "change_governance", "accountability;audit_receipts", "issue remediation;artifact-specific diff engine"),
    ("quality_core", "data_quality", "identity_kernel;schema_contracts;metadata_assertions", "certification decision;source remediation"),
    ("golden_record_edition", "golden_record", "entity_resolution;audit_receipts", "master authority;matching decision;source mutation"),
    ("match_policy", "match_policy", "identity_kernel;quality_core;audit_receipts", "identity issuance;merge execution;golden projection"),
    ("federation", "metadata_federation", "metadata_assertions;catalog_listing_contract;discovery_query;policy_client", "global last-write-wins;source approval"),
    ("audit_receipts", "audit_evidence", "identity_kernel", "domain decision logic;evidence deletion authority"),
    ("access_workflow", "access_request", "policy_client;accountability;audit_receipts", "authorization model;grant implementation"),
    ("vertical_profiles", "vertical_profile", "identity_kernel;reference_core;schema_contracts;policy_model", "horizontal primitive redefinition;vendor switch"),
    ("compiler_contract", "compiler_gap", "", "silent fallback;vendor-name dispatch;LLM or generative core"),
]

GMO_LIBRARY_CLASS = {
    "metadata_assertions": "semantic_pure",
    "metadata_acquisition": "effect_port_contract", "terminology_core": "semantic_pure",
    "taxonomy_core": "semantic_pure",
    "knowledge_graph": "semantic_pure", "catalog_listing_contract": "semantic_pure",
    "discovery_query": "algorithm_pure",
    "accountability": "policy_pure",
    "policy_model": "policy_pure", "policy_client": "effect_port_contract",
    "classification_assignment": "policy_pure", "privacy_purpose_binding": "policy_pure",
    "records_governance": "policy_pure", "certification_lifecycle": "policy_pure",
    "assurance_appraisal_plan": "policy_pure",
    "governance_issue_workflow": "policy_pure", "change_review_policy": "policy_pure",
    "quality_core": "semantic_pure", "golden_record_edition": "semantic_pure",
    "match_policy": "algorithm_pure",
    "federation": "algorithm_pure", "audit_receipts": "semantic_pure",
    "access_workflow": "policy_pure", "vertical_profiles": "policy_pure",
    "compiler_contract": "semantic_pure",
}

GMO_CLASS_EFFECT = {
    "semantic_pure": "pure_no_io", "algorithm_pure": "pure_no_io",
    "policy_pure": "pure_no_io", "effect_port_contract": "pure_effect_intents",
}

# These candidates passed the shared-owner collision review: one context owns the
# meaning and the other listed contexts are contributors/consumers.  Coarse
# candidates requiring split or replacement intentionally retain multiple owner
# candidates until their exact closure is published.
GMO_UNIQUE_OWNER = {
    "accountability": "ownership_accountability",
    "policy_client": "policy_enforcement",
    "records_governance": "retention_disposition",
    "taxonomy_core": "taxonomy",
    "terminology_core": "terminology",
}

GMO_REPLACED_LIBRARIES = {
    "assurance_workflow": ("certification;issue_workflow;change_governance", ["library.gmo.certification_lifecycle", "library.gmo.assurance_appraisal_plan", "library.gmo.governance_issue_workflow", "library.gmo.change_review_policy"], "Appraisal planning, certification, issue remediation and change review have separate authorities, lifecycles and evidence."),
    "catalog_discovery": ("catalog_listing;search_discovery", ["library.gmo.catalog_listing_contract", "library.gmo.discovery_query"], "Governed listing content and retrieval/ranking algorithms evolve independently."),
    "classification_privacy": ("classification;privacy_purpose", ["library.gmo.classification_assignment", "library.gmo.privacy_purpose_binding", "library.spt.privacy_vocabulary"], "Classification assertions and privacy-purpose bindings have different issuers, validity and policy consequences."),
    "entity_resolution": ("entity_identity;entity_resolution;match_policy;merge_survivorship", ["library.csp.identity.entity-resolution", "library.csp.identity.merge-split-ledger", "library.master_data.survivorship_projection", "library.gmo.match_policy"], "Entity identity, candidate resolution, match policy, merge/split history and survivorship remain separate decisions."),
    "identity_kernel": ("asset_identity;identifier_registry;lifecycle_deprecation", ["library.csp.identity.scoped-identifier", "library.csp.identity.namespace-registry", "library.csp.identity.version-identity", "library.san_content_identity"], "Identity is composed from sovereign identifier, namespace, version and content-identity contracts."),
    "schema_contracts": ("technical_schema;schema_registry", ["library.san_wire_schema", "library.schema_registry.subject_identity", "library.schema_registry.version_registry", "library.schema_registry.compatibility", "library.schema_registry.reference_closure"], "Technical schema and registry lifecycle/compatibility/reference closure remain separate contracts."),
    "semantic_query": ("semantic_model;metric_definition", ["library.cbv.semantic_query_types", "library.smf.semantic_query_canonicalizer", "library.smf.semantic_query_gateway"], "Semantic query carrier, canonicalization and dispatch remain independently substitutable."),
    "data_product_contracts": ("data_product;data_contract", ["library.data_contract.contract_identity", "library.data_contract.data_schema_binding", "library.data_product_publication.product_edition", "library.data_product_publication.accountability_binding"], "Product packaging does not own contract, schema, publication-edition or accountability meaning."),
    "ontology_core": ("ontology;ontology_mapping", ["library.ontology_model.axiom_profile", "library.ontology_model.ontology_mapping", "library.ontology_model.reasoning_entailment", "library.ontology_model.identity_import_closure"], "Axiom, mapping, entailment and import-closure contracts have independent evolution laws."),
    "lineage_core": ("lineage;provenance", ["library.lpe.lineage-core", "library.lpe.prov-statement-algebra","library.lpe.provenance-assertion", "library.lpe.provenance-bundle", "library.lpe.field-lineage", "library.lpe.formula-provenance"], "Lineage topology and provenance assertions are related but non-identical contracts."),
    "master_authority": ("master_authority;golden_record", ["library.master_data.domain_identity", "library.master_data.source_authority", "library.master_data.survivorship_projection", "library.gmo.golden_record_edition"], "Source authority is a decision right; a golden record is a reproducible projection edition rather than universal truth."),
    "reference_core": ("reference_data;code_set;crosswalk", ["library.reference_data.reference_set", "library.reference_data.code_set_lifecycle", "library.reference_data.crosswalk_mapping"], "Reference set, code-set lifecycle and crosswalk mapping have different identity and loss laws."),
}


GMO_EXACT_SPLIT_APIS = {
    "certification_lifecycle": {
        "types": ["CertificationCaseId", "CertificationCaseRevision", "CertificationProgramRef", "CertificationCriteriaEdition", "CertificationVerdict", "CertificationLifecyclePolicy", "CertificationRefusal"],
        "trait": "CertificationLifecycleAlgebra",
        "operations": [
            ("validate_certification_request", ["CertificationRequest", "CertificationProgramRef", "CertificationLifecyclePolicy"], "Result<ValidatedCertificationRequest,CertificationRefusal>"),
            ("reduce_certification_command", ["CertificationCaseRevision", "CertificationCommand", "CertificationLifecyclePolicy"], "Result<CertificationTransition,CertificationRefusal>"),
            ("evaluate_certificate_issuance", ["CertificationCaseRevision", "CertificationEvidenceCut", "CertificationCriteriaEdition"], "Result<CertificateIssuanceEligibility,CertificationRefusal>"),
        ],
        "errors": ["ProgramUnbound", "CriteriaEditionUnbound", "AssessorIndependenceUnproved", "EvidenceCutIncomplete", "CertificationTransitionInvalid", "IssuanceAuthorityMissing", "ResourceBudgetExceeded"],
        "laws": ["appraisal plan evidence verdict issuance and reliance decision are distinct", "a certificate binds exact subject program criteria evidence cut issuer and validity", "withdrawal and supersession never rewrite certification history"],
    },
    "assurance_appraisal_plan": {
        "types": ["AppraisalPlanId", "AppraisalPlanEdition", "AppraisalScope", "ProcedureSelection", "SamplingPlan", "AppraisalSchedule", "DeviationPolicy", "AppraisalPlanRefusal"],
        "trait": "AssuranceAppraisalPlanAlgebra",
        "operations": [
            ("validate_appraisal_plan", ["AppraisalPlanEdition", "AppraisalCriteriaEdition", "AppraisalPlanPolicy"], "Result<ValidatedAppraisalPlan,AppraisalPlanRefusal>"),
            ("compare_performed_work", ["ValidatedAppraisalPlan", "PerformedProcedureSet", "DeviationPolicy"], "Result<AppraisalPlanConformance,AppraisalPlanRefusal>"),
            ("derive_plan_amendment", ["ValidatedAppraisalPlan", "AppraisalPlanAmendment", "AppraisalPlanPolicy"], "Result<AppraisalPlanTransition,AppraisalPlanRefusal>"),
        ],
        "errors": ["ScopeUnbound", "ProcedureUnsupported", "SamplingBasisMissing", "ScheduleInvalid", "IndependenceRequirementMissing", "DeviationUnexplained", "ResourceBudgetExceeded"],
        "laws": ["an appraisal plan fixes scope criteria procedures sampling schedule competence and independence requirements", "performed work is never inferred from the approved plan", "every material deviation is recorded accepted under authority or refused"],
    },
    "governance_issue_workflow": {
        "types": ["GovernanceIssueId", "GovernanceIssueRevision", "GovernanceFindingRef", "RemediationPlan", "VerificationEvidenceSet", "GovernanceIssuePolicy", "GovernanceIssueRefusal"],
        "trait": "GovernanceIssueWorkflowAlgebra",
        "operations": [
            ("open_governance_issue", ["GovernanceFindingRef", "GovernanceIssuePolicy"], "Result<GovernanceIssueRevision,GovernanceIssueRefusal>"),
            ("reduce_issue_command", ["GovernanceIssueRevision", "GovernanceIssueCommand", "GovernanceIssuePolicy"], "Result<GovernanceIssueTransition,GovernanceIssueRefusal>"),
            ("evaluate_issue_closure", ["GovernanceIssueRevision", "VerificationEvidenceSet", "GovernanceIssuePolicy"], "Result<IssueClosureEligibility,GovernanceIssueRefusal>"),
        ],
        "errors": ["FindingUnbound", "IssueTransitionInvalid", "RemediationPlanMissing", "ClosureAuthorityMissing", "VerificationEvidenceMissing", "ResidualUnaccepted", "ResourceBudgetExceeded"],
        "laws": ["finding issue remediation action verification and closure are distinct", "closure preserves residual findings and correction evidence", "reopening appends a new revision and never erases the prior closure basis"],
    },
    "change_review_policy": {
        "types": ["GovernedChangeId", "GovernedChangeProposal", "SemanticDiffRef", "BlastRadiusAssessment", "ChangeReviewDecision", "ChangeReviewPolicy", "ChangeReviewRefusal"],
        "trait": "GovernedChangeReviewAlgebra",
        "operations": [
            ("classify_governed_change", ["GovernedChangeProposal", "SemanticDiffRef", "ChangeReviewPolicy"], "Result<ClassifiedGovernedChange,ChangeReviewRefusal>"),
            ("evaluate_change_impact", ["ClassifiedGovernedChange", "BlastRadiusAssessment", "ChangeReviewPolicy"], "Result<ChangeImpactAssessment,ChangeReviewRefusal>"),
            ("decide_change_review", ["ChangeImpactAssessment", "ChangeReviewEvidenceSet", "ChangeReviewPolicy"], "Result<ChangeReviewDecision,ChangeReviewRefusal>"),
        ],
        "errors": ["SemanticDiffMissing", "ChangeClassUnknown", "BlastRadiusIncomplete", "ReviewerAuthorityMissing", "MakerCheckerViolated", "MigrationEvidenceMissing", "ResourceBudgetExceeded"],
        "laws": ["change classification impact review approval release and migration completion are distinct", "approval binds one exact proposal and evidence cut", "unknown blast radius fails closed rather than becoming low impact"],
    },
    "catalog_listing_contract": {
        "types": ["CatalogListingId", "CatalogListingEdition", "MetadataAssertionRef", "VisibilityScope", "ListingProjection", "CatalogListingPolicy", "CatalogListingRefusal"],
        "trait": "CatalogListingAlgebra",
        "operations": [
            ("validate_listing_edition", ["CatalogListingEdition", "CatalogListingPolicy"], "Result<ValidatedCatalogListingEdition,CatalogListingRefusal>"),
            ("derive_listing_projection", ["ValidatedCatalogListingEdition", "CatalogProjectionCut", "CatalogListingPolicy"], "Result<ListingProjection,CatalogListingRefusal>"),
            ("compare_listing_editions", ["CatalogListingEdition", "CatalogListingEdition"], "Result<CatalogListingDiff,CatalogListingRefusal>"),
        ],
        "errors": ["ListingIssuerUnbound", "MetadataAssertionUnresolved", "VisibilityScopeInvalid", "ProjectionCutOpen", "ListingEditionConflict", "ResourceBudgetExceeded"],
        "laws": ["listing assertion source asset certification access grant and search rank are distinct", "a listing projection binds one immutable source and policy cut", "withdrawal preserves listing history and never deletes source assertions"],
    },
    "discovery_query": {
        "types": ["DiscoveryQuery", "CatalogCut", "CandidateListingSet", "RankingProfileRef", "DiscoveryResult", "CoverageStatement", "DiscoveryQueryPolicy", "DiscoveryQueryRefusal"],
        "trait": "DiscoveryQueryAlgebra",
        "operations": [
            ("normalize_discovery_query", ["DiscoveryQuery", "DiscoveryQueryPolicy"], "Result<NormalizedDiscoveryQuery,DiscoveryQueryRefusal>"),
            ("rank_discovery_candidates", ["NormalizedDiscoveryQuery", "CandidateListingSet", "RankingProfileRef"], "Result<DiscoveryResult,DiscoveryQueryRefusal>"),
            ("explain_discovery_result", ["DiscoveryResult", "CatalogCut", "DiscoveryQueryPolicy"], "Result<DiscoveryExplanation,DiscoveryQueryRefusal>"),
        ],
        "errors": ["QueryUnsupported", "CatalogCutOpen", "CandidateCoverageUnknown", "RankingProfileMissing", "ResultTruncated", "VisibilityIndeterminate", "ResourceBudgetExceeded"],
        "laws": ["visibility discoverability relevance rank suitability eligibility and endorsement are distinct", "empty result never proves absence without a coverage statement", "ranking binds exact query profile feature evidence candidate cut and policy edition"],
    },
    "classification_assignment": {
        "types": ["ClassificationAssignmentId", "ClassificationAssignmentEdition", "ClassifiedSubjectRef", "ClassificationSchemeEditionRef", "ClassRef", "AssignmentValidity", "ClassificationPolicy", "ClassificationRefusal"],
        "trait": "ClassificationAssignmentAlgebra",
        "operations": [
            ("validate_classification_assignment", ["ClassificationAssignmentEdition", "ClassificationPolicy"], "Result<ValidatedClassificationAssignment,ClassificationRefusal>"),
            ("compare_classification_assignments", ["ClassificationAssignmentEdition", "ClassificationAssignmentEdition"], "Result<ClassificationAssignmentDiff,ClassificationRefusal>"),
            ("plan_classification_retraction", ["ValidatedClassificationAssignment", "RetractionEvidenceSet", "ClassificationPolicy"], "Result<ClassificationRetractionIntent,ClassificationRefusal>"),
        ],
        "errors": ["ClassificationIssuerUnbound", "SubjectUnresolved", "SchemeEditionUnbound", "ClassUnresolved", "AssignmentValidityInvalid", "RetractionAuthorityMissing", "ResourceBudgetExceeded"],
        "laws": ["classification assignment label taxonomy placement ontology entailment privacy purpose and authorization are distinct", "an assignment binds issuer subject scheme edition class validity and evidence", "retraction preserves the historical assertion and reason"],
    },
    "privacy_purpose_binding": {
        "types": ["PrivacyPurposeBindingId", "PrivacyPurposeBindingEdition", "PurposeRef", "ProcessingActionRef", "DataCategoryRef", "PurposeAuthorityRef", "PurposeBindingPolicy", "PurposeBindingRefusal"],
        "trait": "PrivacyPurposeBindingAlgebra",
        "operations": [
            ("validate_purpose_binding", ["PrivacyPurposeBindingEdition", "PurposeBindingPolicy"], "Result<ValidatedPurposeBinding,PurposeBindingRefusal>"),
            ("evaluate_purpose_compatibility", ["ValidatedPurposeBinding", "ProposedProcessingContext", "PurposeBindingPolicy"], "Result<PurposeCompatibilityAssessment,PurposeBindingRefusal>"),
            ("supersede_purpose_binding", ["ValidatedPurposeBinding", "PrivacyPurposeBindingEdition", "PurposeBindingPolicy"], "Result<PurposeBindingTransition,PurposeBindingRefusal>"),
        ],
        "errors": ["PurposeAuthorityUnbound", "PurposeUnresolved", "ProcessingActionUnresolved", "DataCategoryUnresolved", "ValidityScopeInvalid", "CompatibilityIndeterminate", "ResourceBudgetExceeded"],
        "laws": ["purpose binding classification assignment consent legal basis policy decision and permission are distinct", "purpose compatibility is policy and authority scoped rather than inferred from labels", "supersession never rewrites the purpose applicable to historical processing"],
    },
    "match_policy": {
        "types": ["MatchPolicyId", "MatchPolicyEdition", "ResolutionPopulationRef", "CandidateGenerationRule", "ScoringMethodRef", "ThresholdPolicyRef", "MatchPolicyRefusal"],
        "trait": "EntityMatchPolicyAlgebra",
        "operations": [
            ("validate_match_policy", ["MatchPolicyEdition", "ResolutionPopulationRef"], "Result<ValidatedMatchPolicy,MatchPolicyRefusal>"),
            ("compile_match_policy", ["ValidatedMatchPolicy", "MatchMethodCapabilitySet"], "Result<CompiledMatchPolicy,MatchPolicyRefusal>"),
            ("compare_match_policy_editions", ["MatchPolicyEdition", "MatchPolicyEdition"], "Result<MatchPolicyDiff,MatchPolicyRefusal>"),
        ],
        "errors": ["PopulationUnbound", "CandidateRuleInvalid", "ScoringMethodUnqualified", "ThresholdPolicyMissing", "ReviewBandMissing", "ErrorCostUnbound", "ResourceBudgetExceeded"],
        "laws": ["candidate generation score threshold review decision link assertion merge and entity identity are distinct", "match policy binds one population feature method threshold error-cost and review profile", "a predictive score has no link or merge authority"],
    },
    "golden_record_edition": {
        "types": ["GoldenRecordEditionId", "GoldenRecordEdition", "MasterEntityRef", "AuthoritativeSourceCut", "FieldDecision", "ResidualConflictSet", "GoldenRecordPolicy", "GoldenRecordRefusal"],
        "trait": "GoldenRecordEditionAlgebra",
        "operations": [
            ("assemble_golden_record_edition", ["MasterEntityRef", "AuthoritativeSourceCut", "SurvivorshipPolicyEdition"], "Result<GoldenRecordEdition,GoldenRecordRefusal>"),
            ("validate_golden_record_edition", ["GoldenRecordEdition", "GoldenRecordPolicy"], "Result<ValidatedGoldenRecordEdition,GoldenRecordRefusal>"),
            ("compare_golden_record_editions", ["GoldenRecordEdition", "GoldenRecordEdition"], "Result<GoldenRecordEditionDiff,GoldenRecordRefusal>"),
        ],
        "errors": ["MasterEntityUnresolved", "SourceCutOpen", "AuthorityConflict", "SurvivorshipPolicyUnbound", "FieldProvenanceMissing", "ResidualConflictUnreported", "ResourceBudgetExceeded"],
        "laws": ["golden record is a reproducible editioned projection and not universal truth or source authority", "every field decision retains source authority provenance time and rule edition", "unresolved conflicts remain explicit and never disappear through tie breaking"],
    },
}


def expanded_dependency_refs(deps: str) -> list[str]:
    result: list[str] = []
    for dependency in tokens(deps):
        replacement = GMO_REPLACED_LIBRARIES.get(dependency)
        refs = replacement[1] if replacement else [f"gmo.library.{dependency}"]
        # Source-universe local identities use gmo.library.*; the normalized
        # central registry rewrites them to library.gmo.*.  External replacement
        # identities retain their canonical central form.
        result.extend(
            "gmo.library." + ref.removeprefix("library.gmo.")
            if ref.startswith("library.gmo.") else ref
            for ref in refs
        )
    return sorted(set(result))


def library_replacement_records() -> list[dict]:
    return [{
        "record_kind": "library_replacement_candidate",
        "replacement_id": f"gmo.replacement.{slug}",
        "retired_library_ref": f"library.gmo.{slug}",
        "covered_context_refs": [f"gmo.context.{context}" for context in tokens(contexts)],
        "replacement_library_refs": replacements,
        "compatibility_alias_permitted": False,
        "rationale": rationale,
        "closure_law": "Every former operation, law, refusal and migration path resolves to an exact replacement contract or is explicitly retired; product packaging cannot recreate the coarse boundary.",
        "status": STATUS,
    } for slug, (contexts, replacements, rationale) in sorted(GMO_REPLACED_LIBRARIES.items())]


def library_records() -> list[dict]:
    if {seed[0] for seed in LIBRARY_SEEDS} != set(GMO_LIBRARY_CLASS):
        raise ValueError("Every GMO library candidate must have exactly one explicit semantic class")
    rows = [{
        "record_kind": "library_boundary_candidate",
        "library_id": f"gmo.library.{slug}",
        "library_kind": GMO_LIBRARY_CLASS[slug],
        "effect_boundary": GMO_CLASS_EFFECT[GMO_LIBRARY_CLASS[slug]],
        "owns_contexts": [f"gmo.context.{GMO_UNIQUE_OWNER[slug]}"] if slug in GMO_UNIQUE_OWNER else [f"gmo.context.{c}" for c in tokens(contexts)],
        "contributes_to_context_refs": [f"gmo.context.{c}" for c in tokens(contexts)],
        "allowed_dependencies": expanded_dependency_refs(deps),
        "forbidden_responsibilities": tokens(forbidden),
        "public_contract": ["versioned request/response types", "typed gaps and refusals", "evidence references", "no provider-name semantic switch"],
        "status": STATUS,
    } for slug, contexts, deps, forbidden in LIBRARY_SEEDS]
    for row in rows:
        slug = row["library_id"].removeprefix("gmo.library.")
        exact_api = GMO_EXACT_SPLIT_APIS.get(slug)
        if exact_api:
            row.update({
                "public_types": exact_api["types"],
                "public_traits": [exact_api["trait"]],
                "input_types": sorted({value for _, inputs, _ in exact_api["operations"] for value in inputs}),
                "output_types": sorted({output for _, _, output in exact_api["operations"]}),
                "operations": [{
                    "operation_ref": f"operation.gmo.{slug}.{name}",
                    "name": name,
                    "input_types": inputs,
                    "output_type": output,
                    "purity": "pure",
                    "effect_intent_type": None,
                    "receipt_type": None,
                    "refusal_types": exact_api["errors"],
                } for name, inputs, output in exact_api["operations"]],
                "error_contracts": exact_api["errors"],
                "laws": exact_api["laws"],
                "oracles": ["constructor-and-invariant-properties", "identity-and-authority-negative-twins", "refusal-totality-fixtures", "cross-implementation-differential"],
            })
    return rows


BRIDGE_SEEDS = [
    ("ingest_catalog_sources", "metadata_ingestion", "source_system", "source.public_reference.open_data_catalog;source.analytical_repository.federated_query_catalog", "discovery, paging, change cursor, authority, security and limits must be bound to a deployed occurrence"),
    ("ingest_mdm_source", "metadata_ingestion;master_authority", "source_system", "source.enterprise_application.master_data_management", "product class does not prove entity domains, field authority or match behavior"),
    ("ingest_reference_registry", "metadata_ingestion;reference_data;code_set", "source_system", "source.public_reference.reference_code_registry", "registry version, issuer, validity and delta semantics are required"),
    ("ingest_semantic_metric_store", "metadata_ingestion;semantic_model;metric_definition", "source_system", "source.analytical_repository.semantic_metric_store", "formula, grain, unit, time spine and authorization must be observed separately"),
    ("ingest_identity_directory", "entity_identity;access_entitlement", "source_system", "source.security_identity.identity_directory;source.security_identity.identity_provider_authentication", "authentication identity is not automatically a business-party master identity"),
    ("ingest_government_register", "master_authority;identifier_registry", "source_system", "source.public_reference.government_administrative_register", "jurisdiction, legal effect, publication revision and correction semantics are required"),
    ("ingest_audit_security", "audit_evidence;policy_enforcement", "source_system", "source.security_identity.security_audit_log;source.security_identity.siem_detection_case", "telemetry occurrence is not itself governance approval evidence"),
    ("schema_shape_bridge", "technical_schema;schema_registry", "data_shape", "shape.*;dt.carrier.*;dt.semantic.schema_identifier", "compiler resolves exact carrier/type/shape IDs; unknown meaning remains a gap"),
    ("metadata_shape_bridge", "metadata_record;catalog_listing", "data_shape", "shape.graph.*;shape.document.*;dt.semantic.provenance_reference", "serialization shape does not own metadata meaning"),
    ("ontology_shape_bridge", "ontology;knowledge_graph", "data_shape", "shape.graph.rdf_graph;dt.semantic.identifier;dt.semantic.evidence_reference", "RDF carrier does not imply OWL entailment profile"),
    ("hierarchy_shape_bridge", "hierarchy;taxonomy", "data_shape", "shape.graph.directed_graph;shape.tree.*", "compiler chooses tree only after cycle and parent-cardinality laws are declared"),
    ("lineage_shape_bridge", "lineage;provenance", "data_shape", "shape.graph.directed_multigraph;shape.event_log.*;dt.semantic.provenance_reference", "edge shape does not establish lineage completeness"),
    ("golden_shape_bridge", "golden_record;entity_resolution", "data_shape", "shape.table.*;shape.graph.cluster_graph;dt.semantic.probability", "match score carrier does not establish identity"),
    ("reference_shape_bridge", "reference_data;code_set;crosswalk", "data_shape", "shape.table.*;shape.mapping.*;dt.semantic.identifier", "code meaning and version are qualifiers, not inferred from strings"),
    ("quality_shape_bridge", "data_quality;certification", "data_shape", "dt.semantic.probability;dt.semantic.ratio;dt.semantic.evidence_reference", "quality score requires scale, population, method and time"),
    ("schema_to_semantics", "technical_schema;semantic_model", "semantic_formula", "gmo.context.semantic_model", "field binding pins schema and semantic-model versions"),
    ("semantics_to_formula", "semantic_model;metric_definition", "semantic_formula", "gmo.context.metric_definition", "join path and query grain resolve before formula compilation"),
    ("terms_to_semantics", "business_glossary;semantic_model", "semantic_formula", "gmo.context.terminology;gmo.context.semantic_model", "term link is annotation unless an approved binding says otherwise"),
    ("quality_contract_bridge", "data_contract;data_quality", "quality", "gmo.context.data_quality", "contract references executable rule versions and acceptance windows"),
    ("lineage_pipeline_bridge", "lineage", "pipeline_dataflow", "pipeline.*;operation.*", "job/run/dataset identity and declared versus observed origin stay explicit"),
    ("lineage_quality_bridge", "lineage;data_quality", "quality", "gmo.context.data_quality", "impact traversal may select checks but cannot fabricate results"),
    ("classification_security_bridge", "classification;policy_enforcement", "privacy_security", "security.classification.*;security.policy_decision.*", "classification is an input; decision and enforcement receipts remain separate"),
    ("purpose_security_bridge", "privacy_purpose;policy_authority", "privacy_security", "privacy.purpose.*;privacy.processing.*;security.policy.*", "metadata does not replace legal review or access enforcement"),
    ("entitlement_security_bridge", "access_entitlement;access_request", "privacy_security", "security.identity.*;security.authorization.*", "identity proof and relationship model must be resolved at compile time"),
    ("retention_delete_bridge", "retention_disposition;legal_hold", "operation", "operation.delete.*;operation.redact.*;operation.transfer.*", "physical action compiles only with disposition authorization and negative hold check"),
    ("financial_vertical", "vertical_profile;entity_identity;reference_data;ontology", "vertical", "vertical.finance;E034;E039;E043", "bind LEI, FIBO and ISO 20022 versions without promoting close mappings to identity"),
    ("health_vertical", "vertical_profile;reference_data;code_set;technical_schema", "vertical", "vertical.healthcare;E044;E045;E046", "FHIR value-set membership, DICOM terms and ICD linearizations remain versioned authorities"),
    ("retail_vertical", "vertical_profile;master_authority;reference_data;hierarchy", "vertical", "vertical.retail;E037;E038", "GTIN/GLN identity, GDM attributes and GPC hierarchy have separate authority"),
    ("statistics_vertical", "vertical_profile;semantic_model;reference_data", "vertical", "vertical.official_statistics;E041;E015", "DSD dimensions and code lists bind observation grain and version"),
    ("records_vertical", "vertical_profile;retention_disposition;legal_hold", "vertical", "vertical.government_records;E029;E073", "schedule authority and hold precedence are mandatory"),
    ("research_vertical", "vertical_profile;catalog_listing;provenance", "vertical", "vertical.research;E075;E076", "FAIR signals and datasheets improve documentation but do not certify correctness"),
    ("software_vertical", "vertical_profile;schema_registry;lineage", "vertical", "vertical.software_delivery;E058;E059;E047", "API/message contracts and runtime lineage are separate evidence streams"),
]


def bridge_records() -> list[dict]:
    return [{
        "record_kind": "external_universe_mapping_candidate",
        "mapping_id": f"gmo.bridge.{slug}",
        "source_contexts": [f"gmo.context.{c}" for c in tokens(contexts)],
        "target_universe": target,
        "target_candidates_or_selectors": tokens(candidates),
        "compiler_rule": rule,
        "resolution": "exact_versioned_binding_required_at_compile_time",
        "on_no_unique_match": "emit gmo.context.compiler_gap",
        "status": STATUS,
    } for slug, contexts, target, candidates, rule in BRIDGE_SEEDS]


def compiler_mapping_records(contexts: list[dict], bridges: list[dict]) -> list[dict]:
    by_context: dict[str, list[str]] = {}
    for bridge in bridges:
        for context_id in bridge["source_contexts"]:
            by_context.setdefault(context_id, []).append(bridge["mapping_id"])
    result = []
    for context in contexts:
        slug = context["context_id"].rsplit(".", 1)[-1]
        result.append({
            "record_kind": "requirement_offer_compiler_mapping_candidate",
            "mapping_id": f"gmo.compiler_mapping.{slug}",
            "requirement": {
                "requirement_id": f"gmo.requirement.{slug}",
                "intent_examples": [f"govern {context['name'].lower()}", f"manage {context['name'].lower()}", context["candidate_actions"][0]],
                "required_semantics": context["owns"],
                "must_disambiguate_from": context["explicitly_excludes"],
            },
            "offer": {
                "capability_id": f"gmo.capability.{slug}",
                "owner_context": context["context_id"],
                "authority_role": context["authority_role"],
            },
            "compiler_steps": [
                "resolve governed object kind and identity scope",
                "pin versions, effective time, authority and policy context",
                "match required operations to capability offer",
                "resolve referenced external-universe mappings",
                "verify evidence and ACL obligations",
                "emit plan or typed gap/refusal without guessing",
            ],
            "external_mapping_refs": sorted(by_context.get(context["context_id"], [])),
            "proof_obligations": ["unique owner context", "authorized actor", "all referenced versions resolve", "hard invariants satisfied"],
            "typed_failures": ["unknown_identity", "ambiguous_context", "missing_authority", "unsupported_operation", "insufficient_evidence", "policy_denied"],
            "status": STATUS,
        })
    return result


VERTICAL_SEEDS = [
    ("financial_legal_entity", "Financial legal-entity mastering", "financial_services", "entity_identity;master_authority;golden_record;reference_data;ontology;change_governance", "source.regulated_vertical.core_banking;source.public_reference.government_administrative_register", "E034;E039;E040;E043", "LEI identity and relationship history remain distinct from probabilistic customer matching."),
    ("health_terminology", "Healthcare terminology and patient identity", "healthcare", "technical_schema;code_set;reference_data;entity_identity;entity_resolution;privacy_purpose", "source.regulated_vertical.electronic_health_record;source.regulated_vertical.medical_imaging_pacs", "E044;E045;E046", "Patient matching cannot infer clinical identity solely from demographic similarity; value sets are versioned."),
    ("retail_product", "Retail product and location master", "retail", "master_authority;golden_record;reference_data;hierarchy;identifier_registry;data_quality", "source.enterprise_application.master_data_management;source.enterprise_application.commerce_order_pos", "E037;E038", "GTIN, GLN, product attributes and classification hierarchy keep distinct authorities."),
    ("official_statistics", "Official statistics catalog and structures", "public_sector_statistics", "catalog_listing;semantic_model;reference_data;code_set;certification;provenance", "source.public_reference.official_statistics_exchange;source.public_reference.open_data_catalog", "E041;E015;E001", "A DSD fixes observation structure; publication and official-status certification remain separate."),
    ("government_records", "Government records retention", "public_administration", "classification;retention_disposition;legal_hold;policy_enforcement;audit_evidence", "source.public_reference.government_administrative_register;source.legacy_offline.manual_offline_register", "E029;E073", "Disposition compiles only after schedule, cutoff, authority and hold checks."),
    ("industrial_asset", "Industrial asset hierarchy and reference designation", "manufacturing", "master_authority;entity_identity;hierarchy;reference_data;lineage;custody_operations", "source.enterprise_application.manufacturing_execution;source.industrial_ot.industrial_historian", "E024;E020", "Equipment identity, hierarchy placement, telemetry source, and maintenance authority are independent."),
    ("software_event_api", "Software API and event-contract governance", "software_delivery", "schema_registry;technical_schema;data_contract;lineage;change_governance;certification", "source.code_devops.distributed_version_control;source.code_devops.ci_cd_orchestrator;source.event_messaging_cdc.partitioned_append_log", "E058;E059;E047", "Schema compatibility does not prove semantic compatibility or deployment conformance."),
    ("research_dataset", "Research dataset stewardship", "scientific_research", "catalog_listing;metadata_record;provenance;certification;data_quality;retention_disposition", "source.scientific_research.research_data_repository;source.scientific_research.laboratory_information_management", "E075;E076;E001", "FAIR assessment is scoped evidence, not a claim that results are scientifically correct."),
    ("energy_meter", "Utility meter and premises master", "utilities", "entity_identity;master_authority;reference_data;hierarchy;lineage;privacy_purpose", "source.regulated_vertical.utility_meter_billing;source.iot_edge.smart_meter_gateway", "E020;E026", "Meter device identity, premise identity, customer identity and readings must not be merged into one key."),
    ("telecom_product", "Telecom product and network inventory", "telecommunications", "master_authority;reference_data;hierarchy;technical_schema;issue_workflow;change_governance", "source.regulated_vertical.telecom_oss_bss;source.security_identity.network_security_telemetry", "E022;E027", "Commercial offer, service instance, resource and topology node have different identity and authority."),
    ("insurance_party", "Insurance party and policy master", "insurance", "entity_identity;entity_resolution;match_policy;golden_record;master_authority;privacy_purpose", "source.regulated_vertical.insurance_policy_claims;source.enterprise_application.customer_relationship_management", "E074;E079;E027", "Household, person, organization, role and policy-party records require explicit identity scopes."),
    ("logistics_location", "Logistics item, party, and location reference", "logistics", "identifier_registry;master_authority;reference_data;hierarchy;crosswalk;lineage", "source.enterprise_application.transportation_management;source.enterprise_application.warehouse_management", "E037;E038", "Location code crosswalks do not assert facility identity without authority and effective-time evidence."),
]


def vertical_records() -> list[dict]:
    return [{
        "record_kind": "vertical_case_candidate",
        "case_id": f"gmo.vertical_case.{slug}",
        "name": name,
        "vertical": vertical,
        "required_contexts": [f"gmo.context.{c}" for c in tokens(contexts)],
        "source_system_candidates": tokens(sources),
        "evidence_refs": tokens(evidence),
        "distinction_test": distinction,
        "compiler_outcome_on_missing_binding": "typed vertical_profile gap",
        "status": STATUS,
    } for slug, name, vertical, contexts, sources, evidence, distinction in VERTICAL_SEEDS]


INNOVATION_SEEDS = [
    ("iso11179_registry_common_2023", 2023, "E022", "Revised registry common facilities explicitly cover identification, designation/definition, registration, classification and mapping in one metamodel.", "adopt as candidate registry-item decomposition"),
    ("iso704_terminology_2022", 2022, "E023", "Updated terminology principles sharpen object/concept/definition/designation separation.", "use to keep terms distinct from concepts"),
    ("iso8000_master_exchange_2021", 2021, "E024", "Machine-checkable semantic encoding and data-specification conformance for exchanged characteristic master data.", "treat exchange conformance separately from internal MDM authority"),
    ("iso8000_portable_data_2024", 2024, "E025", "Portable data explicitly packages metadata and reference data with semantic encoding.", "candidate portable governance bundle"),
    ("iso8000_quality_identifiers_2024", 2024, "E026", "Quality identifiers add issuer semantics and resolution requirements.", "candidate identifier assurance profile"),
    ("dcat3_2024", 2024, "E001", "DCAT 3 adds dataset series and stronger versioning support while preserving dataset/distribution separation.", "adopt catalog version and series candidates"),
    ("rdf12_triple_terms", 2026, "E012", "RDF 1.2 drafts add triple terms and directional strings for richer statement annotation.", "experimental provenance binding; do not require in stable core"),
    ("sparql12_query", 2026, "E014", "SPARQL 1.2 draft aligns query behavior with RDF 1.2 additions.", "experimental query adapter"),
    ("shacl12_core", 2026, "E007", "SHACL 1.2 draft expands the graph constraint platform.", "track as draft; keep SHACL 1.0 baseline"),
    ("ssn_2023", 2023, "E020", "The 2023 SSN edition updates observation/system ontology patterns.", "use as vertical observation binding"),
    ("omg_mvf_2024", 2024, "E033", "OMG Multiple Vocabulary Facility formalizes multiple vocabularies and designations.", "candidate multilingual terminology interchange"),
    ("fibo_current_2024", 2024, "E034", "Continuously released FIBO modules provide versioned financial domain-ontology content.", "vertical profile only; no horizontal finance dependency"),
    ("gs1_gdm_2025", 2025, "E038", "GS1 Global Data Model 2.14 advances cross-market product-attribute harmonization.", "retail vertical attribute authority mapping"),
    ("gs1_gdsn_2025", 2025, "E037", "GDSN maintenance releases continue synchronized master-data validation and code-list evolution.", "version every pool and message binding"),
    ("gleif_cdf31", 2021, "E039", "LEI-CDF 3.1 and relationship/reporting formats add richer event and history handling in Golden Copy and delta files.", "distinguish publisher golden copy from MDM golden record"),
    ("fhir_r5_terminology", 2023, "E044", "FHIR R5 terminology resources strengthen versioned CodeSystem, ValueSet and ConceptMap exchange.", "health vertical reference-data binding"),
    ("sdmx31", 2025, "E041", "SDMX 3.1 evolves structural metadata, constraints and code-list exchange.", "official-statistics vertical binding"),
    ("odcs31", 2025, "E062", "ODCS 3.1 provides a vendor-neutral machine-readable contract spanning schema, semantics, quality, service levels and teams.", "candidate import/export adapter; preserve internal types"),
    ("open_data_product_spec", 2025, "E063", "An open data-product specification makes ports, ownership, service levels and licensing exchangeable.", "candidate product manifest adapter"),
    ("openlineage_facets", 2024, "E047", "OpenLineage facets enable extensible run, job and dataset metadata including field-level lineage patterns.", "ingest with assertion-kind and completeness qualifiers"),
    ("iceberg_rest_catalog", 2025, "E064", "The Iceberg REST Catalog protocol separates table metadata operations from a single catalog implementation.", "catalog occurrence adapter, not governance core"),
    ("nessie_versioned_catalog", 2023, "E065", "Nessie applies branch/tag/commit/merge semantics to catalog contents.", "candidate change-governance adapter"),
    ("apache_polaris", 2024, "E066", "Polaris emerged as an open catalog with principal, role and privilege surfaces.", "candidate catalog and entitlement occurrence"),
    ("openmetadata_contracts", 2025, "E050", "OpenMetadata added versioned data-contract, data-product, workflow and validation surfaces.", "official OSS evidence; no product-shaped core"),
    ("datahub_assertions_forms", 2024, "E049", "DataHub expanded assertions, forms, structured properties, domains and product governance metadata.", "evidence for separate assertion/workflow contexts"),
    ("nist_csf2_govern", 2024, "E072", "NIST CSF 2.0 adds GOVERN as a core function and strengthens governance evidence expectations.", "candidate governance assurance mapping"),
    ("datasheets_2021", 2021, "E076", "Datasheets for Datasets systematize dataset motivation, composition, collection and maintenance documentation.", "candidate documentation profile, not certification"),
    ("metricflow_semantic_compile", 2024, "E068", "MetricFlow operationalizes semantic entities, joins, time spines and metric query planning.", "evidence for formula context separated from schemas"),
]


def innovation_records() -> list[dict]:
    return [{
        "record_kind": "innovation_candidate",
        "innovation_id": f"gmo.innovation.{slug}",
        "year": year,
        "source_ref": source,
        "development": development,
        "candidate_impact": impact,
        "maturity": "working_draft" if source in {"E007", "E012", "E014"} else "published_or_official_release",
        "status": STATUS,
    } for slug, year, source, development, impact in INNOVATION_SEEDS]


GAP_SEEDS = [
    ("independent_review", "No candidate has yet passed independent domain, standards, security, and compiler review.", "all registries", "independent review receipts and adjudicated split/merge decisions"),
    ("clause_pinning", "Many evidence records point to whole specifications rather than exact clauses and immutable content digests.", "evidence-sources.jsonl", "clause locators, edition hashes and archival snapshots"),
    ("standard_access", "Some ISO/OMG normative details are paywalled or require licensed copies; catalog abstracts are insufficient for full conformance.", "ISO and OMG mappings", "licensed clause review by authorized reviewers"),
    ("ontology_consistency", "The corpus does not include executable OWL ontologies or reasoner conformance suites.", "ontology candidates", "profile-specific test ontologies and multiple reasoner receipts"),
    ("shacl_versions", "SHACL 1.2 remains draft and may change.", "innovation and shape mappings", "track W3C disposition and retain 1.0 baseline"),
    ("entity_resolution_benchmarks", "Match policies have no population-specific labeled benchmarks, fairness analysis, or drift receipts.", "entity resolution", "vertical benchmark packs with clerical review and subgroup error analysis"),
    ("merge_implementations", "Reversible merge/unmerge laws are not verified against multiple MDM implementations.", "merge and golden record", "two unrelated implementations and failure-injection tests"),
    ("retention_jurisdiction", "Horizontal retention semantics do not encode jurisdiction-specific legal schedules.", "retention and hold", "separate signed jurisdiction packs and legal review"),
    ("policy_formalism", "ODRL, Rego, ReBAC and enterprise policy languages do not share one proven semantic equivalence.", "policy mapping", "formal adapter contracts and non-equivalence tests"),
    ("classification_propagation", "Propagation through joins, aggregation, masking, tokenization and de-identification lacks universal sound rules.", "classification and lineage", "transformation-specific policies and counterexample suite"),
    ("semantic_metric_interop", "No single stable cross-vendor semantic-metric interchange standard covers every grain, join, time and additivity law.", "semantic model and metrics", "adapter profiles plus differential query tests"),
    ("catalog_federation", "Conflict resolution, deletion propagation, ACL intersection and identifier collision need multi-catalog conformance tests.", "metadata federation", "three-implementation federation harness"),
    ("vertical_coverage", "Twelve vertical cases demonstrate portability but do not saturate industries, jurisdictions, languages or code systems.", "vertical-cases.jsonl", "additional independently governed profile packs"),
    ("source_occurrences", "Mappings name provider-neutral source classes but no deployed occurrence capabilities or connector receipts are bound.", "external mappings", "occurrence records and connector verification"),
    ("external_ids", "Some type/shape and operation bridges use selectors because neighboring universe IDs remain candidates and may change.", "external-universe-mappings.jsonl", "pin accepted external registry editions and exact IDs"),
    ("freshness", "Standards and OSS documentation continue to evolve after the as-of date.", "entire corpus", "recurring primary-source freshness audit"),
    ("td_tooling", "Repository instructions require td session tracking, but the td executable was unavailable in this environment.", "research workflow", "install or expose td and reconstruct task receipt"),
]


def gap_records() -> list[dict]:
    return [{
        "record_kind": "coverage_gap_candidate",
        "gap_id": f"gmo.gap.{slug}",
        "description": description,
        "affected_surface": surface,
        "closure_evidence_required": closure,
        "compiler_behavior": "remain candidate and fail closed where the gap is material",
        "status": STATUS,
    } for slug, description, surface, closure in GAP_SEEDS]


def object_schema(title: str, kind: str, required: list[str], fields: dict[str, dict]) -> dict:
    properties = {
        "record_kind": {"const": kind},
        "status": {"const": STATUS},
    }
    properties.update(fields)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title,
        "type": "object",
        "required": ["record_kind", "status", *required],
        "properties": properties,
        "additionalProperties": True,
    }


def schemas() -> dict[str, dict]:
    s = {"type": "string", "minLength": 1}
    a = {"type": "array", "minItems": 1, "items": s, "uniqueItems": True}
    return {
        "evidence-source.schema.json": object_schema("Evidence source candidate", "evidence_source", ["source_id", "title", "issuer", "url", "supports"], {"source_id": s, "title": s, "issuer": s, "url": {"type": "string", "format": "uri"}, "supports": a}),
        "bounded-context-candidate.schema.json": object_schema("Bounded context candidate", "bounded_context_candidate", ["context_id", "name", "definition", "owns", "explicitly_excludes", "evidence_refs"], {"context_id": {"type": "string", "pattern": "^gmo\\.context\\."}, "name": s, "definition": s, "owns": a, "explicitly_excludes": a, "evidence_refs": a}),
        "ubiquitous-language-candidate.schema.json": object_schema("Ubiquitous language candidate", "ubiquitous_language_candidate", ["term_id", "term", "definition", "owning_context", "must_not_be_conflated_with"], {"term_id": s, "term": s, "definition": s, "owning_context": s, "must_not_be_conflated_with": a}),
        "capability-operation-candidate.schema.json": object_schema("Capability or operation candidate", "capability_operation_candidate", ["candidate_kind", "candidate_id", "name", "owner_context", "evidence_refs"], {"candidate_kind": {"enum": ["capability", "typed_operation"]}, "candidate_id": s, "name": s, "owner_context": s, "evidence_refs": a}),
        "decision-point-candidate.schema.json": object_schema("Decision point candidate", "decision_point_candidate", ["decision_id", "question", "options", "default_on_unknown"], {"decision_id": s, "question": s, "options": a, "default_on_unknown": s}),
        "invariant-refusal-candidate.schema.json": object_schema("Invariant and refusal candidate", "invariant_refusal_candidate", ["invariant_id", "owner_context", "statement", "compiler_refusal"], {"invariant_id": s, "owner_context": s, "statement": s, "compiler_refusal": s}),
        "context-relation-acl-candidate.schema.json": object_schema("Context relation and ACL candidate", "context_relation_acl_candidate", ["relation_id", "source_context", "target_context", "relation_kind", "granted_access", "boundary_rule"], {"relation_id": s, "source_context": s, "target_context": s, "relation_kind": s, "granted_access": s, "boundary_rule": s}),
        "compiler-mapping-candidate.schema.json": object_schema("Requirement, offer and compiler mapping candidate", "requirement_offer_compiler_mapping_candidate", ["mapping_id", "requirement", "offer", "compiler_steps", "typed_failures"], {"mapping_id": s, "requirement": {"type": "object"}, "offer": {"type": "object"}, "compiler_steps": a, "typed_failures": a}),
        "library-boundary-candidate.schema.json": object_schema("Library boundary candidate", "library_boundary_candidate", ["library_id", "owns_contexts", "forbidden_responsibilities", "public_contract"], {"library_id": s, "owns_contexts": a, "allowed_dependencies": {"type": "array", "items": s, "uniqueItems": True}, "forbidden_responsibilities": a, "public_contract": a}),
        "library-replacement-candidate.schema.json": object_schema("Library replacement candidate", "library_replacement_candidate", ["replacement_id", "retired_library_ref", "covered_context_refs", "replacement_library_refs", "rationale", "closure_law"], {"replacement_id": s, "retired_library_ref": s, "covered_context_refs": a, "replacement_library_refs": a, "rationale": s, "closure_law": s}),
        "external-universe-mapping-candidate.schema.json": object_schema("External universe mapping candidate", "external_universe_mapping_candidate", ["mapping_id", "source_contexts", "target_universe", "target_candidates_or_selectors", "compiler_rule"], {"mapping_id": s, "source_contexts": a, "target_universe": s, "target_candidates_or_selectors": a, "compiler_rule": s}),
        "vertical-case-candidate.schema.json": object_schema("Vertical case candidate", "vertical_case_candidate", ["case_id", "name", "vertical", "required_contexts", "source_system_candidates", "distinction_test"], {"case_id": s, "name": s, "vertical": s, "required_contexts": a, "source_system_candidates": a, "distinction_test": s}),
        "innovation-candidate.schema.json": object_schema("2021-2026 innovation candidate", "innovation_candidate", ["innovation_id", "year", "source_ref", "development", "candidate_impact"], {"innovation_id": s, "year": {"type": "integer", "minimum": 2021, "maximum": 2026}, "source_ref": s, "development": s, "candidate_impact": s}),
        "coverage-gap-candidate.schema.json": object_schema("Coverage gap candidate", "coverage_gap_candidate", ["gap_id", "description", "affected_surface", "closure_evidence_required"], {"gap_id": s, "description": s, "affected_surface": s, "closure_evidence_required": s}),
    }


def main() -> None:
    contexts = context_records()
    evidence = evidence_records()
    bridges = bridge_records()
    registries = {
        "evidence-sources.jsonl": evidence,
        "bounded-context-candidates.jsonl": contexts,
        "ubiquitous-language-candidates.jsonl": term_records(),
        "capability-operation-candidates.jsonl": capability_operation_records(contexts),
        "decision-point-candidates.jsonl": decision_records(),
        "invariants-refusals.jsonl": invariant_records(),
        "context-relations-acls.jsonl": relation_records(),
        "compiler-mappings.jsonl": compiler_mapping_records(contexts, bridges),
        "library-boundaries.jsonl": library_records(),
        "retired-compositions.jsonl": library_replacement_records(),
        "external-universe-mappings.jsonl": bridges,
        "vertical-cases.jsonl": vertical_records(),
        "innovations-2021-2026.jsonl": innovation_records(),
        "coverage-gaps.jsonl": gap_records(),
    }
    for filename, records in registries.items():
        write_jsonl(ROOT / filename, records)
    for filename, schema in schemas().items():
        write_json(SCHEMAS / filename, schema)

    all_ids: list[str] = []
    for records in registries.values():
        for record in records:
            for key, value in record.items():
                if key.endswith("_id") and isinstance(value, str):
                    all_ids.append(value)
                    break
    status_counts = Counter(r["status"] for records in registries.values() for r in records)
    digests = {}
    for filename in sorted(registries):
        digests[filename] = "sha256:" + hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()
    coverage = {
        "as_of": AS_OF,
        "edition": 1,
        "status": STATUS,
        "counts": {filename: len(records) for filename, records in sorted(registries.items())},
        "summary": {
            "sources": len(evidence),
            "bounded_contexts": len(contexts),
            "capabilities": sum(r["candidate_kind"] == "capability" for r in registries["capability-operation-candidates.jsonl"]),
            "typed_operations": sum(r["candidate_kind"] == "typed_operation" for r in registries["capability-operation-candidates.jsonl"]),
            "capability_operation_decision_total": len(registries["capability-operation-candidates.jsonl"]) + len(registries["decision-point-candidates.jsonl"]),
            "recent_innovations": len(registries["innovations-2021-2026.jsonl"]),
            "vertical_cases": len(registries["vertical-cases.jsonl"]),
            "all_candidate_records": sum(len(records) for records in registries.values()),
        },
        "minimum_checks": {
            "sources_at_least_45": len(evidence) >= 45,
            "bounded_contexts_at_least_35": len(contexts) >= 35,
            "capability_operation_decision_at_least_150": len(registries["capability-operation-candidates.jsonl"]) + len(registries["decision-point-candidates.jsonl"]) >= 150,
            "innovations_at_least_20": len(registries["innovations-2021-2026.jsonl"]) >= 20,
            "all_records_candidate": set(status_counts) == {STATUS},
            "ids_unique": len(all_ids) == len(set(all_ids)),
        },
        "status_counts": status_counts,
        "registry_sha256": digests,
    }
    write_json(ROOT / "coverage-report.json", coverage)
    write_manifest()


if __name__ == "__main__":
    main()
