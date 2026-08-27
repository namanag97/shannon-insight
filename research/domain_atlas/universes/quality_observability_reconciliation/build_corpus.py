#!/usr/bin/env python3
"""Build the quality/observability/reconciliation candidate universe deterministically.

The records are provider-neutral research candidates.  Evidence establishes that a
concept or mechanism exists; it does not adjudicate the final bounded-context split.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
EDITION = 1
AS_OF = "2026-08-25"
CANDIDATE = "researched_candidate_not_adjudicated"


def source(
    source_id: str,
    title: str,
    publisher: str,
    url: str,
    evidence_role: str,
    source_kind: str,
    year: int,
    areas: list[str],
    claim: str,
    limitation: str = "Supports existence and vocabulary; does not establish a universal domain boundary.",
) -> dict[str, Any]:
    return {
        "source_id": f"qor.src.{source_id}",
        "edition": EDITION,
        "title": title,
        "publisher": publisher,
        "url": url,
        "evidence_role": evidence_role,
        "source_kind": source_kind,
        "publication_year": year,
        "areas": areas,
        "claims_supported": [claim],
        "primary_source": True,
        "authority_scope": {
            "normative_authority": "Normative within the issuing body's stated scope.",
            "open_specification": "Specification authority for conforming implementations of that specification.",
            "regulatory_authority": "Authoritative within the named regulatory or supervisory scope.",
            "original_research": "Primary evidence for the reported method or findings, not normative authority.",
            "implementation_evidence": "Official evidence that an implementation exposes the documented mechanism, not normative authority.",
        }[evidence_role],
        "limitations": limitation,
        "accessed_at": AS_OF,
    }


SOURCES = [
    source("iso25012", "ISO/IEC 25012:2008 Data quality model", "ISO/IEC", "https://www.iso.org/standard/35736.html", "normative_authority", "standard", 2008, ["quality-model", "fitness"], "Defines a general model of inherent and system-dependent data-quality characteristics."),
    source("iso25024", "ISO/IEC 25024:2015 Measurement of data quality", "ISO/IEC", "https://www.iso.org/standard/35749.html", "normative_authority", "standard", 2015, ["measurement", "evaluation"], "Defines data-quality measures used with the SQuaRE quality model."),
    source("iso8000-8", "ISO 8000-8:2015 Data quality: Information and data quality", "ISO", "https://www.iso.org/standard/60805.html", "normative_authority", "standard", 2015, ["quality-model", "governance"], "Describes fundamental concepts of information and data quality."),
    source("iso8000-61", "ISO 8000-61:2016 Data quality management: Process reference model", "ISO", "https://www.iso.org/standard/63086.html", "normative_authority", "standard", 2016, ["quality-management", "process"], "Defines a process reference model for data-quality management."),
    source("iso19157-1", "ISO 19157-1:2023 Geographic information — Data quality", "ISO", "https://www.iso.org/standard/78900.html", "normative_authority", "standard", 2023, ["quality-model", "industry-geospatial"], "Defines principles for describing and evaluating geographic-data quality."),
    source("iso2859-1", "ISO 2859-1:1999 Sampling procedures for inspection by attributes", "ISO", "https://www.iso.org/standard/1141.html", "normative_authority", "standard", 1999, ["sampling", "acceptance"], "Defines acceptance-sampling plans indexed by acceptance quality limit."),
    source("iso3951-1", "ISO 3951-1:2022 Sampling procedures for inspection by variables", "ISO", "https://www.iso.org/standard/71208.html", "normative_authority", "standard", 2022, ["sampling", "acceptance"], "Defines single sampling plans for inspection by variables."),
    source("jcgm-vim", "JCGM 200:2012 International vocabulary of metrology", "JCGM", "https://www.bipm.org/en/committees/jc/jcgm/publications", "normative_authority", "metrology_guide", 2012, ["measurement", "uncertainty"], "Defines measurement, measurand, measurement result, error and uncertainty terminology."),
    source("jcgm-gum", "JCGM 100:2008 Evaluation of measurement data — Guide to the expression of uncertainty", "JCGM", "https://www.bipm.org/en/committees/jc/jcgm/publications", "normative_authority", "metrology_guide", 2008, ["measurement", "uncertainty"], "Provides a general framework for evaluating and expressing measurement uncertainty."),
    source("w3c-dqv", "Data on the Web Best Practices: Data Quality Vocabulary", "W3C", "https://www.w3.org/TR/vocab-dqv/", "open_specification", "w3c_note", 2016, ["quality-metadata", "fitness", "certification"], "Separates dimensions, metrics, measurements, annotations, policies and certificates while leaving fitness judgments to consumers."),
    source("w3c-shacl", "Shapes Constraint Language (SHACL)", "W3C", "https://www.w3.org/TR/shacl/", "normative_authority", "recommendation", 2017, ["validation", "conformance"], "Defines shapes, constraint components and validation reports for RDF graphs."),
    source("w3c-shacl12", "SHACL 1.2 Core", "W3C", "https://www.w3.org/TR/shacl12-core/", "open_specification", "candidate_recommendation", 2026, ["validation", "innovation"], "Evolves the core graph-validation language and report model."),
    source("w3c-prov", "PROV-O: The PROV Ontology", "W3C", "https://www.w3.org/TR/prov-o/", "normative_authority", "recommendation", 2013, ["evidence", "lineage"], "Defines entities, activities, agents, derivation and attribution for provenance interchange."),
    source("w3c-dcat3", "Data Catalog Vocabulary (DCAT) Version 3", "W3C", "https://www.w3.org/TR/vocab-dcat-3/", "normative_authority", "recommendation", 2024, ["dataset-identity", "catalog"], "Defines interoperable dataset, distribution, service and catalog metadata."),
    source("w3c-csvw", "Model for Tabular Data and Metadata on the Web", "W3C", "https://www.w3.org/TR/tabular-data-model/", "normative_authority", "recommendation", 2015, ["schema", "validation"], "Defines annotated-table structure and metadata used for tabular parsing and validation."),
    source("json-schema", "JSON Schema Draft 2020-12", "JSON Schema", "https://json-schema.org/draft/2020-12/json-schema-core", "open_specification", "specification", 2022, ["schema", "validation"], "Defines vocabulary-driven structural constraints and evaluation for JSON instances."),
    source("xml-schema", "W3C XML Schema Definition Language 1.1", "W3C", "https://www.w3.org/TR/xmlschema11-1/", "normative_authority", "recommendation", 2012, ["schema", "validation"], "Defines XML structure, type assignment, constraints and validity assessment."),
    source("openapi31", "OpenAPI Specification 3.1.1", "OpenAPI Initiative", "https://spec.openapis.org/oas/v3.1.1.html", "open_specification", "specification", 2024, ["contract", "interface"], "Defines machine-readable HTTP API contracts aligned with JSON Schema semantics."),
    source("asyncapi30", "AsyncAPI Specification 3.0.0", "AsyncAPI Initiative", "https://www.asyncapi.com/docs/reference/specification/v3.0.0", "open_specification", "specification", 2023, ["contract", "event-interface"], "Defines machine-readable asynchronous API channels, operations and messages."),
    source("cloudevents", "CloudEvents Specification 1.0.2", "CNCF", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", "open_specification", "specification", 2022, ["event-evidence", "interoperability"], "Defines a common event envelope with source, identity, type and time attributes."),
    source("trace-context", "Trace Context Level 1", "W3C", "https://www.w3.org/TR/trace-context/", "normative_authority", "recommendation", 2021, ["observability", "correlation"], "Defines interoperable trace identifiers and propagation headers."),
    source("otel-spec", "OpenTelemetry Specification", "OpenTelemetry", "https://opentelemetry.io/docs/specs/otel/", "open_specification", "specification", 2025, ["observability", "telemetry"], "Defines APIs, SDKs and data concepts for traces, metrics and logs."),
    source("otel-semconv", "OpenTelemetry Semantic Conventions", "OpenTelemetry", "https://opentelemetry.io/docs/specs/semconv/", "open_specification", "specification", 2025, ["observability", "correlation"], "Defines shared names, types and meanings for telemetry attributes and signals."),
    source("openmetrics", "OpenMetrics Specification 1.0.0", "CNCF", "https://github.com/OpenObservability/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md", "open_specification", "specification", 2021, ["metrics", "observability"], "Defines a text exposition model for metric families, exemplars and metadata."),
    source("prometheus-rules", "Prometheus Alerting Rules", "Prometheus", "https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/", "implementation_evidence", "official_oss_docs", 2025, ["slo", "alerts"], "Documents rule evaluation, pending periods, labels and annotations."),
    source("openslo", "OpenSLO Specification", "OpenSLO", "https://github.com/OpenSLO/OpenSLO", "open_specification", "specification", 2021, ["slo", "quality-objective"], "Defines vendor-neutral services, SLIs, SLO objectives and alert policies."),
    source("openlineage", "OpenLineage Specification", "OpenLineage", "https://openlineage.io/docs/spec/", "open_specification", "specification", 2025, ["lineage", "observability"], "Defines runtime lineage events over jobs, runs, datasets and extensible facets."),
    source("openlineage-dq-metrics", "OpenLineage Data Quality Metrics Dataset Facet", "OpenLineage", "https://openlineage.io/docs/spec/facets/dataset-facets/data_quality_metrics/", "open_specification", "facet_specification", 2021, ["quality-metrics", "lineage"], "Defines version-bound dataset and column quality metric observations."),
    source("openlineage-dq-assertions", "OpenLineage Data Quality Assertions Facet", "OpenLineage", "https://openlineage.io/docs/spec/facets/dataset-facets/data_quality_assertions/", "open_specification", "facet_specification", 2025, ["validation", "lineage", "innovation"], "Separates assertion success from configured enforcement severity."),
    source("openlineage-column-lineage", "OpenLineage Column Lineage Dataset Facet", "OpenLineage", "https://openlineage.io/docs/spec/facets/dataset-facets/column_lineage_facet/", "open_specification", "facet_specification", 2022, ["lineage", "impact"], "Represents field-level input dependencies and transformation descriptions."),
    source("odcs31", "Open Data Contract Standard 3.1.0", "Bitol / LF AI & Data", "https://bitol-io.github.io/open-data-contract-standard/latest/", "open_specification", "specification", 2025, ["contract", "quality", "slo", "innovation"], "Defines a data contract structure spanning schema, quality, SLA, roles and servers."),
    source("odcs30-release", "Open Data Contract Standard 3.0.0 Release", "Bitol / LF AI & Data", "https://github.com/bitol-io/open-data-contract-standard/releases/tag/v3.0.0", "implementation_evidence", "release_record", 2024, ["contract", "quality", "innovation"], "Records the v3 restructuring of schema and data-quality declarations."),
    source("data-contract-spec", "Data Contract Specification", "Data Contract Specification", "https://datacontract.com/", "open_specification", "specification", 2024, ["contract", "schema", "quality"], "Defines a portable contract document and command-line validation surface."),
    source("dbt-data-tests", "Data tests", "dbt Labs", "https://docs.getdbt.com/docs/build/data-tests", "implementation_evidence", "official_oss_docs", 2025, ["testing", "validation"], "Documents generic and singular tests that return failing records."),
    source("dbt-unit-tests", "Unit tests", "dbt Labs", "https://docs.getdbt.com/docs/build/unit-tests", "implementation_evidence", "official_oss_docs", 2024, ["testing", "innovation"], "Documents testing SQL model logic against small static inputs before materialization."),
    source("dbt-contracts", "Model contracts", "dbt Labs", "https://docs.getdbt.com/docs/mesh/govern/model-contracts", "implementation_evidence", "official_oss_docs", 2023, ["contract", "conformance", "innovation"], "Documents enforced output column names and data types for models."),
    source("gx-expectations", "Expectations overview", "Great Expectations", "https://docs.greatexpectations.io/docs/core/define_expectations/", "implementation_evidence", "official_oss_docs", 2025, ["validation", "testing"], "Documents declarative, verifiable assertions over data."),
    source("gx-results", "ExpectationSuiteValidationResult", "Great Expectations", "https://docs.greatexpectations.io/docs/reference/api/core/expectationsuitevalidationresult_class/", "implementation_evidence", "official_oss_docs", 2026, ["validation", "evidence", "innovation"], "Documents detailed per-expectation results and aggregate validation statistics."),
    source("gx-checkpoint", "Checkpoint", "Great Expectations", "https://docs.greatexpectations.io/docs/reference/api/checkpoint_class/", "implementation_evidence", "official_oss_docs", 2026, ["validation", "gate"], "Documents production validation definitions, result formats and post-validation actions."),
    source("gx-unexpected-rows", "Retrieve all unexpected rows", "Great Expectations", "https://docs.greatexpectations.io/docs/core/run_validations/retrieve_all_failure_results/", "implementation_evidence", "official_oss_docs", 2025, ["validation", "correction"], "Documents retrieving the complete failing-row set separately from summary results."),
    source("sodacl", "SodaCL metrics and checks", "Soda", "https://docs.soda.io/sodacl-reference/metrics-and-checks", "implementation_evidence", "official_oss_docs", 2025, ["validation", "metrics"], "Documents metric, threshold, pass, fail, warn and error outcomes in a quality-check DSL."),
    source("deequ-docs", "Deequ — Unit Tests for Data", "Amazon Web Services", "https://github.com/awslabs/deequ", "implementation_evidence", "official_oss_docs", 2024, ["profiling", "verification", "anomaly"], "Documents analyzers, constraints, verification suites and metric repositories."),
    source("deequ-paper", "Automating Large-Scale Data Quality Verification", "PVLDB", "https://www.vldb.org/pvldb/vol11/p1781-schelter.pdf", "original_research", "research_paper", 2018, ["profiling", "verification"], "Introduces scalable analyzers, constraint verification and constraint suggestion for large datasets."),
    source("tfdv-paper", "Data Validation for Machine Learning", "SysML", "https://proceedings.mlsys.org/paper_files/paper/2019/file/928f1160e52192e3e0017fb63ab65391-Paper.pdf", "original_research", "research_paper", 2019, ["schema", "drift", "skew"], "Describes scalable statistics, schema inference, anomaly detection and training-serving skew checks."),
    source("pandera", "Pandera documentation", "Pandera", "https://pandera.readthedocs.io/en/stable/", "implementation_evidence", "official_oss_docs", 2025, ["schema", "validation", "types"], "Documents dataframe schemas, checks, type validation and multiple dataframe backends."),
    source("whylogs", "whylogs documentation", "whylogs", "https://whylogs.readthedocs.io/en/latest/", "implementation_evidence", "official_oss_docs", 2023, ["profiling", "sketches", "innovation"], "Documents mergeable statistical profiles used to monitor data without retaining raw values."),
    source("ydata-profiling", "ydata-profiling documentation", "YData", "https://docs.profiling.ydata.ai/", "implementation_evidence", "official_oss_docs", 2025, ["profiling", "comparison"], "Documents exploratory profiles and dataset comparison reports."),
    source("data-diff", "data-diff", "Datafold", "https://github.com/datafold/data-diff", "implementation_evidence", "official_oss_docs", 2022, ["reconciliation", "innovation"], "Documents cross-database row comparison and keyed difference workflows."),
    source("postgres-constraints", "PostgreSQL Constraints", "PostgreSQL Global Development Group", "https://www.postgresql.org/docs/current/ddl-constraints.html", "implementation_evidence", "official_oss_docs", 2025, ["conformance", "constraints"], "Documents check, not-null, unique, primary-key and foreign-key enforcement semantics."),
    source("delta-constraints", "Constraints on Databricks", "Databricks", "https://docs.databricks.com/aws/en/tables/constraints", "implementation_evidence", "official_product_docs", 2025, ["conformance", "constraints"], "Documents enforced and informational table constraints in a lakehouse implementation."),
    source("iceberg-evolution", "Apache Iceberg Evolution", "Apache Iceberg", "https://iceberg.apache.org/docs/latest/evolution/", "implementation_evidence", "official_oss_docs", 2025, ["schema", "change"], "Documents schema evolution by stable field identity without rewriting data files."),
    source("avro-spec", "Apache Avro Specification 1.12.0", "Apache Avro", "https://avro.apache.org/docs/1.12.0/specification/", "open_specification", "specification", 2024, ["schema", "compatibility"], "Defines writer/reader schema resolution and type promotion rules."),
    source("protobuf-updating", "Updating a Message Type", "Protocol Buffers", "https://protobuf.dev/programming-guides/proto3/#updating", "implementation_evidence", "official_oss_docs", 2025, ["schema", "compatibility"], "Documents compatibility rules for evolving field numbers, names and types."),
    source("parquet", "Apache Parquet Format", "Apache Parquet", "https://parquet.apache.org/docs/file-format/", "open_specification", "specification", 2025, ["profiling", "statistics"], "Defines column metadata and optional statistics that can support bounded profiling."),
    source("omg-cmmn", "Case Management Model and Notation 1.1", "Object Management Group", "https://www.omg.org/spec/CMMN/1.1/", "normative_authority", "standard", 2016, ["case-management", "adjudication"], "Defines case files, discretionary work, sentries, stages and case-task lifecycle."),
    source("omg-bpmn", "Business Process Model and Notation 2.0.2", "Object Management Group", "https://www.omg.org/spec/BPMN/2.0.2/", "normative_authority", "standard", 2014, ["workflow", "remediation"], "Defines process activities, events, gateways, compensation and escalation semantics."),
    source("vc-data-model", "Verifiable Credentials Data Model v2.0", "W3C", "https://www.w3.org/TR/vc-data-model-2.0/", "normative_authority", "recommendation", 2025, ["certification", "evidence", "innovation"], "Defines issuer, holder, subject, status and verifiable presentation semantics."),
    source("in-toto-attestation", "in-toto Attestation Framework", "in-toto", "https://github.com/in-toto/attestation", "open_specification", "specification", 2024, ["attestation", "evidence"], "Defines typed, signed statements whose subject is identified by digest."),
    source("slsa-provenance", "SLSA Provenance", "OpenSSF", "https://slsa.dev/spec/v1.0/provenance", "open_specification", "specification", 2023, ["attestation", "evidence", "innovation"], "Defines provenance attestations binding an artifact subject to a build process and inputs."),
    source("rfc9457", "RFC 9457 Problem Details for HTTP APIs", "IETF", "https://www.rfc-editor.org/rfc/rfc9457", "normative_authority", "internet_standard", 2023, ["failure", "interoperability"], "Defines a machine-readable problem-detail envelope with type, status and instance identity."),
    source("nist-control-charts", "NIST/SEMATECH e-Handbook: Control Charts", "NIST", "https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc3.htm", "regulatory_authority", "technical_handbook", 2013, ["anomaly", "change", "statistics"], "Documents statistical process monitoring and control-chart interpretation."),
    source("un-nqaf", "United Nations National Quality Assurance Frameworks Manual", "United Nations", "https://unstats.un.org/unsd/methodology/dataquality/un-nqaf-manual/", "normative_authority", "official_manual", 2019, ["quality-management", "statistics"], "Defines quality principles and assurance practices for official statistics."),
    source("bcbs239", "Principles for effective risk data aggregation and risk reporting", "Basel Committee on Banking Supervision", "https://www.bis.org/publ/bcbs239.htm", "regulatory_authority", "supervisory_standard", 2013, ["reconciliation", "control-truth", "finance"], "Requires accuracy, integrity, completeness, timeliness and adaptable risk-data aggregation with reconciliation to sources."),
    source("xbrl-formula", "XBRL Formula 1.0", "XBRL International", "https://specifications.xbrl.org/work-product-index-formula-formula-1.0.html", "open_specification", "specification", 2022, ["validation", "accounting", "reconciliation"], "Defines assertions, variables, filters and consistency checks for XBRL facts."),
    source("fhir-validation", "FHIR Validation", "HL7 International", "https://hl7.org/fhir/validation.html", "open_specification", "standard", 2023, ["validation", "healthcare"], "Defines validation against base resources, profiles, terminology bindings and invariants."),
    source("dicom-conformance", "DICOM Conformance", "DICOM Standards Committee", "https://www.dicomstandard.org/conformance", "normative_authority", "standard", 2025, ["conformance", "healthcare"], "Requires conformance statements that document supported application profiles and behavior."),
    source("fda-data-integrity", "Data Integrity and Compliance With Drug CGMP: Questions and Answers", "US FDA", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/data-integrity-and-compliance-drug-cgmp-questions-and-answers-guidance-industry", "regulatory_authority", "regulatory_guidance", 2018, ["evidence", "correction", "life-sciences"], "Explains attributable, legible, contemporaneous, original or true-copy and accurate record expectations."),
    source("gs1-dqf", "GS1 Data Quality Framework", "GS1", "https://www.gs1.org/standards/data-quality", "open_specification", "industry_framework", 2025, ["quality", "reference-data", "commerce"], "Provides an industry framework for assessing and improving master-data quality."),
    source("adwin", "Learning from Time-Changing Data with Adaptive Windowing", "SIAM", "https://doi.org/10.1137/1.9781611972771.42", "original_research", "research_paper", 2007, ["change-detection", "streaming"], "Introduces an adaptive-window method with statistical guarantees for change detection."),
    source("mmd", "A Kernel Two-Sample Test", "Journal of Machine Learning Research", "https://www.jmlr.org/papers/v13/gretton12a.html", "original_research", "research_paper", 2012, ["distribution-shift", "testing"], "Develops maximum mean discrepancy tests for determining whether samples share a distribution."),
    source("bocpd", "Bayesian Online Changepoint Detection", "arXiv", "https://arxiv.org/abs/0710.3742", "original_research", "research_paper", 2007, ["change-detection", "time-series"], "Introduces online posterior inference over time since the most recent change point."),
    source("rrcf", "Robust Random Cut Forest Based Anomaly Detection on Streams", "PMLR", "https://proceedings.mlr.press/v48/guha16.html", "original_research", "research_paper", 2016, ["anomaly", "streaming"], "Introduces a streaming anomaly score based on robust random cut forests."),
    source("metanome", "Profiling Relational Data: A Survey", "VLDB Journal", "https://hpi.de/fileadmin/user_upload/fachgebiete/naumann/publications/2018/Profiling_Survey.pdf", "original_research", "research_paper", 2018, ["profiling", "dependencies"], "Surveys discovery of metadata, dependencies, keys, inclusion dependencies and related profiles."),
    source("data-cascades", "Data Cascades in High-Stakes AI", "ACM CHI", "https://dl.acm.org/doi/10.1145/3411764.3445518", "original_research", "research_paper", 2021, ["fitness", "issue-management", "innovation"], "Reports compounding downstream effects of undervalued data work in high-stakes systems."),
    source("dagster-asset-checks", "Dagster Asset Checks", "Dagster", "https://docs.dagster.io/guides/test/asset-checks", "implementation_evidence", "official_oss_docs", 2023, ["validation", "gate", "innovation"], "Documents quality checks as first-class objects associated with data assets."),
    source("otel-logs", "OpenTelemetry Logs Data Model", "OpenTelemetry", "https://opentelemetry.io/docs/specs/otel/logs/data-model/", "open_specification", "specification", 2023, ["observability", "logs", "innovation"], "Defines a stable common log-record data model and trace correlation fields."),
]


def ctx(
    slug: str,
    name: str,
    purpose: str,
    aggregate: str,
    capabilities: list[str],
    operations: list[str],
    decision: str,
    invariants: list[str],
    refusals: list[str],
    distinctions: list[str],
    source_refs: list[str],
    planes: list[str],
    industries: list[str],
) -> dict[str, Any]:
    return {
        "slug": slug,
        "name": name,
        "purpose": purpose,
        "aggregate": aggregate,
        "capabilities": capabilities,
        "operations": operations,
        "decision": decision,
        "invariants": invariants,
        "refusals": refusals,
        "distinctions": distinctions,
        "sources": [f"qor.src.{item}" for item in source_refs],
        "planes": planes,
        "industries": industries,
    }


CONTEXTS = [
    ctx("quality_requirement", "Quality Requirement", "Own stakeholder-specific, testable quality needs before selecting measures or implementations.", "QualityRequirement", ["capture intended use", "bind quality dimension", "version acceptance criterion"], ["propose requirement", "scope requirement", "revise requirement", "retire requirement"], "Which stakeholder, use, data cut and consequence make the requirement meaningful?", ["A requirement names its consumer and intended use.", "Every threshold has a unit, comparison and evaluation scope."], ["stakeholder unknown", "usage context absent", "threshold unit ambiguous"], ["quality is not validity", "requirement is not observation"], ["iso25012", "iso25024", "w3c-dqv"], ["governance", "semantic", "type_shape"], ["finance", "healthcare", "public-statistics"]),
    ctx("fitness_for_use", "Fitness for Use", "Evaluate whether a data product is suitable for a particular decision under explicit risk and utility.", "FitnessAssessment", ["declare use profile", "evaluate suitability", "record conditional acceptance"], ["define use profile", "assess fitness", "compare alternatives", "issue fitness verdict"], "What loss, tolerance and decision horizon define acceptable fitness for this use?", ["Fitness is relative to a named use and consumer.", "A fitness verdict cannot be generalized beyond its assessed scope."], ["intended use absent", "loss model absent", "evidence not representative"], ["fitness is not intrinsic validity", "fitness verdict is not universal certification"], ["w3c-dqv", "iso25012", "data-cascades"], ["semantic", "governance", "industry"], ["clinical-research", "credit-risk", "transport-planning"]),
    ctx("quality_dimension_metric", "Quality Dimension and Metric", "Own dimension vocabulary, metric definitions, units, estimands and aggregation laws.", "QualityMetric", ["define dimension", "define metric procedure", "compose score"], ["register dimension", "define metric", "evaluate metric", "aggregate measurements"], "Is a proposed value a raw observation, a metric, a dimension score or a policy verdict?", ["A metric specifies procedure, unit and subject.", "Composite scores publish weighting and missing-component behavior."], ["metric procedure absent", "unit incompatible", "aggregation law undefined"], ["dimension is not metric", "measurement is not verdict"], ["w3c-dqv", "iso25024", "iso8000-8", "jcgm-vim"], ["semantic", "type_shape", "governance"], ["official-statistics", "manufacturing", "commerce"]),
    ctx("contract_declaration", "Declared Data Contract", "Own producer-consumer declarations for schema, semantics, quality, service and compatibility.", "DeclaredContract", ["author contract edition", "classify compatibility", "negotiate obligations"], ["draft contract", "validate contract document", "classify contract change", "activate contract edition"], "Which clauses are normative obligations and which are informative metadata?", ["A contract edition is immutable after activation.", "Every obligation names obligor, beneficiary and scope."], ["authority absent", "compatibility unresolved", "credential embedded in contract"], ["declared contract is not observed behavior", "schema is not whole contract"], ["odcs31", "data-contract-spec", "openapi31", "asyncapi30", "protobuf-updating"], ["governance", "semantic", "pipeline", "type_shape"], ["commerce", "telecom", "finance"]),
    ctx("contract_observation", "Observed Contract", "Infer and record actual structural, behavioral and service properties without silently rewriting declarations.", "ObservedContract", ["observe delivered shape", "measure behavior", "compare declaration to observation"], ["capture contract observation", "infer observed constraints", "compare contract states", "publish divergence"], "Which observations are strong enough to support an inferred constraint and for what horizon?", ["Observed properties retain sample window and provenance.", "Observation never mutates the declared contract."], ["sample horizon absent", "identity unresolved", "inference confidence insufficient"], ["observed contract is not declared contract", "absence of violation is not guarantee"], ["openlineage", "openlineage-dq-metrics", "deequ-paper", "iceberg-evolution"], ["runtime", "lineage", "governance"], ["payments", "retail", "logistics"]),
    ctx("schema_conformance", "Schema Conformance", "Evaluate data instances against structural and type declarations at explicit versions.", "SchemaConformanceRun", ["resolve schema edition", "validate structure", "report conformance"], ["compile schema", "validate instance", "validate batch", "emit conformance report"], "Which schema language, edition and validation mode govern the instance?", ["A report binds the exact schema and data identities.", "Validator failure is distinct from instance nonconformance."], ["schema edition missing", "schema ill formed", "validator capability unsupported"], ["conformance is not fitness", "validator error is not validation failure"], ["json-schema", "xml-schema", "w3c-shacl", "w3c-csvw", "postgres-constraints", "delta-constraints"], ["type_shape", "pipeline", "runtime"], ["healthcare", "public-data", "software-telemetry"]),
    ctx("rule_specification", "Quality Rule Specification", "Own executable assertions, target selection, parameters, severity and explanatory metadata.", "QualityRule", ["author rule", "type-check rule", "version rule library"], ["define rule", "bind rule target", "type check rule", "deprecate rule"], "Does the rule express a hard invariant, sampled test, heuristic detector or advisory policy?", ["Rules declare target grain and missingness semantics.", "Severity does not alter the observed outcome."], ["target path unresolved", "parameter type invalid", "predicate non-deterministic without declaration"], ["test predicate is not gate action", "heuristic is not invariant"], ["w3c-shacl", "sodacl", "gx-expectations", "xbrl-formula"], ["type_shape", "semantic", "governance"], ["banking", "life-sciences", "marketplaces"]),
    ctx("validation_execution", "Validation Execution", "Run a rule set on an identified data cut and retain scoped results.", "ValidationRun", ["plan validation", "execute validation", "summarize results"], ["plan validation run", "execute rule set", "collect violations", "finalize validation result"], "Full scan, partition scan, incremental evaluation or sample—which execution semantics apply?", ["Every result binds rule, engine, data cut and time.", "Skipped, errored, passed and failed remain distinct."], ["data cut unresolved", "rule engine unavailable", "evaluation incomplete"], ["execution failure is not failed assertion", "pass is not certification"], ["gx-results", "gx-checkpoint", "deequ-docs", "sodacl"], ["pipeline", "runtime", "lineage"], ["finance", "manufacturing", "education"]),
    ctx("test_case_management", "Data Test Case", "Own examples, fixtures, expected outcomes and regression suites for data transformations and rules.", "DataTestCase", ["author fixture", "assert expected output", "manage regression suite"], ["create test case", "generate fixture", "execute test case", "record regression result"], "Is the subject transformation logic, data conformance, or production-data behavior?", ["Fixtures are versioned and isolated from production truth.", "Expected outcomes are reviewed independently of actual results."], ["fixture leaks production secret", "expected result absent", "test oracle circular"], ["unit test is not production monitor", "fixture is not evidence of population quality"], ["dbt-unit-tests", "dbt-data-tests", "pandera"], ["pipeline", "type_shape", "governance"], ["software-analytics", "finance", "retail"]),
    ctx("data_profiling", "Data Profiling", "Compute descriptive summaries, dependencies and candidate constraints over bounded observations.", "DataProfile", ["profile columns", "discover dependencies", "merge profile sketches"], ["plan profile", "scan profile", "merge profiles", "compare profiles"], "Which statistics, precision, sampling and privacy budgets are allowed?", ["Profiles state population or sample scope.", "Approximate statistics disclose error or sketch parameters."], ["privacy budget absent", "scan cost exceeds budget", "unsupported carrier type"], ["profile is not contract", "candidate constraint is not accepted rule"], ["metanome", "deequ-paper", "whylogs", "ydata-profiling", "parquet"], ["type_shape", "runtime", "semantic"], ["commerce", "telecom", "scientific-data"]),
    ctx("statistical_baseline", "Statistical Baseline", "Own reference windows, stratification, seasonality and uncertainty used by detectors.", "StatisticalBaseline", ["select reference window", "fit baseline", "version baseline"], ["select baseline data", "fit baseline", "validate baseline", "publish baseline edition"], "Is the baseline fixed, rolling, seasonal, peer-group or externally controlled?", ["Baseline selection precedes current-window scoring.", "Baseline drift never silently changes a contractual threshold."], ["reference window contaminated", "sample insufficient", "seasonality unresolved"], ["baseline is not source truth", "model update is not anomaly resolution"], ["nist-control-charts", "jcgm-gum", "adwin"], ["semantic", "runtime", "governance"], ["manufacturing", "payments", "energy"]),
    ctx("anomaly_detection", "Quality Anomaly Detection", "Score surprising measurements or records against an explicit detector and baseline.", "AnomalyAssessment", ["score metric anomaly", "score record anomaly", "calibrate detector"], ["configure detector", "score observation", "rank anomaly", "explain detector signal"], "What false-positive, false-negative and detection-delay trade-off is authorized?", ["Anomaly scores retain detector and baseline editions.", "An anomaly is a signal requiring adjudication, not a defect verdict."], ["baseline absent", "detector uncalibrated", "score incomparable across editions"], ["detection is not adjudication", "surprise is not invalidity"], ["deequ-docs", "nist-control-charts", "rrcf"], ["runtime", "semantic", "lineage"], ["fraud-operations", "iot", "retail"]),
    ctx("distribution_shift", "Distribution Shift", "Test whether current and reference populations differ at declared features and strata.", "ShiftAssessment", ["select two-sample test", "quantify effect size", "localize shift"], ["define shift comparison", "execute two sample test", "estimate effect size", "localize changed strata"], "Which null hypothesis, multiplicity correction and practical-effect threshold apply?", ["Statistical significance and practical significance remain separate.", "Shift results identify both populations and feature mappings."], ["populations not comparable", "sample dependence unmodeled", "multiplicity policy absent"], ["distribution shift is not quality failure", "correlation shift is not causal explanation"], ["mmd", "tfdv-paper", "jcgm-gum"], ["semantic", "runtime", "industry"], ["clinical-trials", "credit-risk", "demand-forecasting"]),
    ctx("change_point_detection", "Change-Point Detection", "Identify time-localized changes in level, variance, rate or distribution under delay guarantees.", "ChangePointAssessment", ["detect sequential change", "estimate change point", "manage detector state"], ["configure sequential test", "ingest measurement", "detect change point", "reset detector state"], "Which change family, run-length prior or adaptive-window guarantee applies?", ["Event time and observation order are explicit.", "Detector reset is recorded as a state transition."], ["time order ambiguous", "state checkpoint missing", "minimum segment violated"], ["change point is not root cause", "reset is not correction"], ["adwin", "bocpd", "nist-control-charts"], ["runtime", "pipeline", "semantic"], ["network-operations", "manufacturing", "market-data"]),
    ctx("observability_instrumentation", "Quality Observability Instrumentation", "Define and emit telemetry about quality evaluations, pipeline behavior and data-product service.", "InstrumentationContract", ["define telemetry", "emit correlated signals", "bound telemetry cost"], ["register instrument", "emit quality metric", "emit validation event", "record evaluation span"], "Which signals and attributes are observable without exposing protected values or exploding cardinality?", ["Telemetry identities correlate to data cut, run and rule.", "Instrumentation does not become the authority for business correctness."], ["correlation identity absent", "cardinality budget exceeded", "sensitive attribute prohibited"], ["observability is not conformance", "telemetry is not source truth"], ["otel-spec", "otel-semconv", "openmetrics", "trace-context"], ["runtime", "pipeline", "lineage"], ["all-industries", "platform-operations"]),
    ctx("signal_correlation", "Quality Signal Correlation", "Correlate metrics, logs, traces, lineage, changes and validation evidence without collapsing identities.", "SignalCorrelation", ["join signals by identity", "construct causal candidate graph", "deduplicate alerts"], ["correlate signal", "link signal to lineage", "group related alerts", "rank causal candidates"], "Which identity links are observed, declared, probabilistic or manually asserted?", ["Correlation edges record method and confidence.", "Correlation never upgrades temporal association to causation."], ["identity namespace conflict", "clock uncertainty excessive", "join confidence below policy"], ["correlation is not causation", "alert grouping is not defect adjudication"], ["trace-context", "openlineage", "otel-logs"], ["runtime", "lineage", "pipeline"], ["telecom", "financial-services", "commerce"]),
    ctx("quality_slo", "Quality SLO", "Own service-level indicators, objectives, windows, budgets and burn semantics for quality outcomes.", "QualitySLO", ["define quality SLI", "evaluate objective window", "compute error budget"], ["define sli", "define slo", "evaluate slo", "compute budget burn"], "What event population, good-event predicate, window and target express the objective?", ["SLI numerator and denominator are typed and reproducible.", "SLO compliance is windowed and does not certify individual records."], ["denominator zero policy absent", "window unresolved", "target unit invalid"], ["SLO is not invariant", "error budget is not permission to corrupt"], ["openslo", "prometheus-rules", "openmetrics", "odcs31"], ["governance", "runtime", "semantic"], ["marketplaces", "payments", "telecom"]),
    ctx("quality_alerting", "Quality Alerting", "Translate evaluated signals into routed, deduplicated, stateful notifications under explicit policies.", "QualityAlert", ["evaluate alert policy", "deduplicate notification", "route alert"], ["evaluate alert condition", "open alert", "silence alert", "resolve alert"], "When does a signal become pending, firing, suppressed, acknowledged or resolved?", ["Alert lifecycle is distinct from incident lifecycle.", "Silence never changes the underlying measurement."], ["routing target absent", "deduplication key ambiguous", "silence unauthorized"], ["alert is not incident", "silence is not waiver"], ["prometheus-rules", "openslo", "rfc9457"], ["runtime", "governance", "pipeline"], ["all-industries", "platform-operations"]),
    ctx("quality_incident_case", "Quality Incident and Case", "Own the investigated lifecycle of a suspected quality impact, participants, evidence and work items.", "QualityCase", ["open quality case", "manage investigation", "coordinate remediation"], ["open case", "attach evidence", "assign work item", "close case"], "What scope and impact threshold promote signals or defects into a managed case?", ["Case state is independent from dataset publication state.", "Closure records resolution reason and residual risk."], ["case subject unresolved", "required evidence missing", "closure rationale absent"], ["incident is not defect", "case closure is not data correction"], ["omg-cmmn", "omg-bpmn", "data-cascades"], ["governance", "runtime", "industry"], ["healthcare", "banking", "public-administration"]),
    ctx("defect_adjudication", "Quality Defect Adjudication", "Determine whether a detected condition constitutes a defect relative to authoritative criteria.", "DefectDecision", ["assemble adjudication packet", "apply decision policy", "record defect verdict"], ["submit signal for adjudication", "request expert review", "decide defect status", "reopen decision"], "Who has authority to decide and which criteria and evidence meet the burden?", ["Verdicts retain decision authority and evidence.", "Unresolved cases remain unknown rather than defaulting to defect."], ["decision authority absent", "evidence conflict unresolved", "criteria edition missing"], ["detection is not adjudication", "adjudication is not correction"], ["omg-cmmn", "w3c-prov", "fda-data-integrity"], ["governance", "semantic", "industry"], ["life-sciences", "finance", "public-statistics"]),
    ctx("reconciliation_definition", "Reconciliation Definition", "Specify populations, keys, transformations, tolerances, directions and truth roles for comparison.", "ReconciliationDefinition", ["define comparison sides", "define matching keys", "define tolerance policy"], ["define reconciliation", "bind comparison population", "compile match strategy", "classify compatibility"], "Which side is source truth, accounting truth, control truth or merely a peer observation?", ["Each side has a named truth role; roles need not be symmetric.", "Tolerance includes unit, sign, rounding and aggregation grain."], ["truth role absent", "comparison grain incompatible", "tolerance dimension invalid"], ["reconciliation is not validation", "source truth is not automatically control truth"], ["bcbs239", "xbrl-formula", "data-diff"], ["semantic", "type_shape", "governance", "pipeline"], ["banking", "payments", "inventory"]),
    ctx("reconciliation_execution", "Reconciliation Execution", "Execute exact, tolerant, aggregate or probabilistic comparisons over identified cuts.", "ReconciliationRun", ["pair populations", "compute breaks", "summarize balance"], ["plan reconciliation run", "match records", "compute differences", "finalize reconciliation"], "Is comparison exact, tolerance-based, aggregate, temporal or probabilistic?", ["A run binds both data cuts and the definition edition.", "Matched, unmatched, ambiguous and incomparable remain separate."], ["data cuts misaligned", "matching non-deterministic", "comparison incomplete"], ["break is not defect", "balanced aggregate is not row-level equality"], ["data-diff", "bcbs239", "xbrl-formula"], ["pipeline", "runtime", "lineage"], ["finance", "logistics", "commerce"]),
    ctx("reconciliation_break", "Reconciliation Break and Exception", "Own discrepancy identity, classification, materiality and lifecycle after comparison.", "ReconciliationBreak", ["classify break", "assess materiality", "age exception"], ["open break", "classify break", "split break", "close break"], "Is the break timing, mapping, amount, reference, duplication, omission or unexplained?", ["Break history is append-only.", "Closure names resolution, evidence and any correcting entries."], ["break identity unstable", "materiality policy absent", "closure evidence missing"], ["break is not defect", "exception is not waiver"], ["bcbs239", "omg-cmmn", "w3c-prov"], ["governance", "runtime", "industry"], ["banking", "insurance", "supply-chain"]),
    ctx("correction_proposal", "Correction Proposal", "Design candidate repairs while preserving original observations and review authority.", "CorrectionProposal", ["propose patch", "estimate impact", "route approval"], ["draft correction", "simulate correction", "assess blast radius", "approve correction"], "Is the repair deterministic, inferred, manually asserted or a compensating entry?", ["Original values remain addressable.", "Proposal records derivation, scope and reversibility."], ["original unavailable", "repair confidence insufficient", "approval authority absent"], ["proposal is not correction", "imputation is not observed fact"], ["fda-data-integrity", "w3c-prov", "gx-unexpected-rows"], ["governance", "lineage", "pipeline"], ["life-sciences", "finance", "customer-master"]),
    ctx("correction_execution", "Correction Execution and Restatement", "Apply approved repair, compensating entry or restatement with immutable receipts.", "CorrectionRun", ["apply correction", "emit restatement", "verify repaired cut"], ["apply patch", "post compensating entry", "publish restatement", "rollback correction"], "Does the domain permit in-place edit, append-only correction, compensating transaction or new edition?", ["Correction never erases its source evidence.", "Every applied change references an approved proposal."], ["proposal not approved", "target edition changed", "rollback impossible"], ["correction is not deletion", "restatement is not original observation"], ["fda-data-integrity", "w3c-prov", "omg-bpmn"], ["pipeline", "lineage", "governance"], ["pharmaceuticals", "accounting", "public-statistics"]),
    ctx("quarantine_release", "Quarantine and Release Gate", "Isolate suspect cuts and govern publication, downstream use and controlled release.", "QuarantineLot", ["quarantine data cut", "evaluate release gate", "track downstream exposure"], ["place quarantine", "evaluate release criteria", "grant release", "revoke release"], "Does the gate block publication, consumption, propagation, or only a named use?", ["Quarantine scope is exact and does not imply defect verdict.", "Release requires current evidence for the same data cut."], ["scope unresolved", "release evidence stale", "authorized releaser absent"], ["quarantine is not deletion", "release is not universal certification"], ["dagster-asset-checks", "gx-checkpoint", "w3c-dqv"], ["pipeline", "governance", "runtime"], ["healthcare", "finance", "manufacturing"]),
    ctx("certification_attestation", "Quality Certification and Attestation", "Issue scoped claims about assessment under named criteria, issuer authority and validity period.", "QualityAttestation", ["define certification scheme", "issue attestation", "verify status"], ["request certification", "evaluate certification criteria", "issue certificate", "revoke certificate"], "Is the artifact a self-attestation, third-party certificate, signed measurement or policy label?", ["Attestations bind subject digest, criteria edition, issuer and validity.", "Revocation status is independently checkable."], ["issuer unauthorized", "subject digest absent", "status unavailable"], ["certificate is not measurement", "signature is not truth"], ["w3c-dqv", "vc-data-model", "in-toto-attestation"], ["governance", "lineage", "semantic"], ["regulated-data", "data-marketplaces", "public-data"]),
    ctx("evidence_receipt", "Quality Evidence and Receipt", "Own immutable evaluation evidence, provenance, identity, retention and disclosure scope.", "EvidenceReceipt", ["capture evaluation receipt", "hash evidence subject", "verify provenance chain"], ["create receipt", "attach provenance", "sign receipt", "verify receipt"], "What is directly observed, computed, asserted, signed or externally certified?", ["Evidence identifies subject, method, actor and time.", "Redaction preserves a verifiable statement of omitted scope."], ["subject identity absent", "provenance discontinuity", "signature verification failed"], ["evidence is not proof of all claims", "receipt is not verdict"], ["w3c-prov", "in-toto-attestation", "slsa-provenance", "cloudevents"], ["lineage", "governance", "runtime"], ["all-industries", "regulated-data"]),
    ctx("waiver_exception", "Quality Waiver and Policy Exception", "Authorize time-bounded deviations from enforcement without changing observations or requirements.", "QualityWaiver", ["request waiver", "evaluate compensating controls", "expire waiver"], ["submit waiver", "approve waiver", "revoke waiver", "expire waiver"], "Who may accept which residual risk for which use, cut and duration?", ["Waivers are scoped, expiring and attributable.", "Waiver changes disposition, never the measured result."], ["risk owner absent", "expiry absent", "scope broader than authority"], ["waiver is not pass", "silence is not waiver"], ["omg-cmmn", "w3c-prov", "openslo"], ["governance", "runtime", "industry"], ["banking", "healthcare", "telecom"]),
    ctx("reference_master_alignment", "Reference and Master Alignment", "Compare observations to governed identity, code and hierarchy references with effective-time semantics.", "ReferenceAlignment", ["resolve reference edition", "map codes", "measure alignment"], ["bind reference set", "validate reference value", "map deprecated code", "report unaligned value"], "Which reference authority and effective-time edition governs each observation?", ["Reference edition and effective time are explicit.", "Mapping preserves whether it was exact, deprecated, inferred or manual."], ["reference authority ambiguous", "effective time unknown", "many-to-many mapping unresolved"], ["reference truth is not observed source truth", "code mapping is not entity resolution"], ["gs1-dqf", "fhir-validation", "dicom-conformance", "iso19157-1"], ["semantic", "type_shape", "governance"], ["commerce", "healthcare", "geospatial"]),
    ctx("accounting_control_reconciliation", "Accounting and Control Reconciliation", "Reconcile operational records, subledgers, ledgers and independent controls without conflating authority roles.", "ControlReconciliation", ["bind book of record", "reconcile control total", "post adjustment trail"], ["select control population", "reconcile balances", "explain control variance", "certify control completion"], "Which system is operational source, accounting book, regulatory report or independent control?", ["Truth roles are declared for each assertion and period.", "An adjustment never rewrites the operational source observation."], ["period not closed", "control total unauthenticated", "material variance unexplained"], ["source truth is not accounting truth", "accounting truth is not control truth"], ["bcbs239", "xbrl-formula", "fda-data-integrity"], ["semantic", "governance", "industry", "lineage"], ["banking", "insurance", "payments"]),
    ctx("duplicate_entity_resolution", "Duplicate and Entity Resolution Quality", "Identify candidate duplicate records and adjudicate identity links separately from merge effects.", "EntityResolutionCase", ["generate duplicate candidates", "score identity link", "adjudicate merge"], ["block candidate pairs", "score match", "decide identity link", "propose entity merge"], "Which identifiers, similarity evidence and false-merge costs govern resolution?", ["Probabilistic links retain score and model edition.", "Merge is a separate authorized correction."], ["blocking recall unknown", "identity authority absent", "merge irreversible"], ["duplicate detection is not identity adjudication", "identity adjudication is not record merge"], ["gs1-dqf", "metanome", "data-cascades"], ["semantic", "type_shape", "governance"], ["customer-master", "patient-matching", "supplier-master"]),
    ctx("completeness_timeliness", "Completeness, Freshness and Timeliness", "Evaluate expected population coverage, arrivals, event-time lag and use-time availability.", "DeliveryQualityAssessment", ["define expected population", "measure completeness", "measure lateness"], ["define arrival expectation", "compute completeness", "compute freshness", "classify lateness"], "Is timeliness measured at event, ingestion, processing, publication or consumption time?", ["Completeness denominator and expected population are explicit.", "Freshness and event-time lateness remain distinct."], ["expected population unknown", "clock basis incompatible", "denominator unbounded"], ["missing is not late", "freshness is not correctness"], ["iso25024", "odcs31", "openlineage-dq-metrics"], ["pipeline", "runtime", "semantic"], ["market-data", "logistics", "public-health"]),
    ctx("sampling_measurement", "Sampling and Measurement Assurance", "Design samples, measurement procedures and uncertainty statements for economical assessment.", "MeasurementPlan", ["design sample", "estimate uncertainty", "decide acceptance"], ["define measurement plan", "draw sample", "estimate measurement uncertainty", "issue acceptance decision"], "What population, design, confidence and acceptance-risk bound apply?", ["Sample design is fixed before results are interpreted.", "Acceptance decision records producer and consumer risks."], ["sampling frame incomplete", "selection probability unknown", "uncertainty not estimable"], ["sample pass is not population proof", "measurement error is not data defect"], ["iso2859-1", "iso3951-1", "jcgm-gum"], ["semantic", "runtime", "governance"], ["manufacturing", "survey-statistics", "clinical-quality"]),
    ctx("lineage_quality_impact", "Lineage Quality Impact", "Propagate candidate impact, evidence and recovery obligations across declared and observed lineage.", "QualityImpactAnalysis", ["trace affected descendants", "scope blast radius", "plan revalidation"], ["attach quality facet", "traverse impacted lineage", "select revalidation scope", "issue impact report"], "Does impact follow declared dependency, observed read, field derivation or policy subscription?", ["Impact edges retain lineage kind and data version.", "Potential impact is distinct from observed corruption."], ["lineage version absent", "field mapping ambiguous", "traversal horizon unbounded"], ["lineage is not causation", "potential impact is not confirmed defect"], ["openlineage", "openlineage-column-lineage", "w3c-prov"], ["lineage", "pipeline", "governance"], ["all-industries", "data-platform"]),
    ctx("quality_policy", "Quality Policy and Control", "Own mandatory controls, applicability, authority, exceptions and enforcement consequences.", "QualityPolicy", ["author quality policy", "resolve applicability", "evaluate control"], ["define policy", "bind policy scope", "evaluate control", "supersede policy"], "Which authority owns the policy and what takes precedence when policies conflict?", ["Policy applicability is resolved before enforcement.", "Policy change does not rewrite historical evaluations."], ["authority chain absent", "policy conflict unresolved", "effective period missing"], ["policy is not metric", "control is not observation"], ["iso8000-61", "w3c-dqv", "un-nqaf"], ["governance", "semantic", "industry"], ["public-statistics", "banking", "healthcare"]),
    ctx("remediation_verification", "Remediation Verification", "Verify that approved actions corrected the target defect without unacceptable regression.", "RemediationVerification", ["define verification plan", "retest corrected cut", "assess regression"], ["plan remediation verification", "execute targeted retest", "execute regression suite", "accept remediation"], "Which original defect criteria, regression scope and observation horizon establish effective remediation?", ["Verification uses criteria independent of repair mechanics.", "Acceptance identifies residual exceptions and monitoring horizon."], ["corrected cut unidentified", "test oracle shared with repair", "regression scope insufficient"], ["correction execution is not remediation success", "retest pass is not broad certification"], ["omg-bpmn", "dbt-unit-tests", "gx-results"], ["pipeline", "governance", "runtime"], ["all-industries", "regulated-data"]),
]


SEMANTIC_DISTINCTIONS = [
    ("validity_vs_quality", "Validity", "satisfaction of a specified predicate or grammar", "Quality", "degree of suitability across named dimensions and use", "A valid record can still be untimely, biased, incomplete or unfit."),
    ("quality_vs_fitness", "Quality measurement", "an observed value under a metric", "Fitness verdict", "a use-specific decision under loss and tolerance", "No metric value implies fitness without a use policy."),
    ("conformance_vs_observability", "Conformance", "comparison to a declared specification", "Observability", "ability to infer internal behavior from emitted signals", "Rich telemetry cannot establish conformance when no rule was evaluated."),
    ("observability_vs_reconciliation", "Observability", "signals about operation and data behavior", "Reconciliation", "comparison of identified populations under matching and truth roles", "A dashboard discrepancy is not a reconciled break set."),
    ("detection_vs_adjudication", "Detection", "production of a signal by a rule or detector", "Adjudication", "authorized decision that a signal is a defect or acceptable condition", "A detector cannot silently decide business defect status."),
    ("adjudication_vs_correction", "Adjudication", "decision about condition and responsibility", "Correction", "authorized change, compensating entry or restatement", "A defect verdict does not authorize mutation."),
    ("declared_vs_observed_contract", "Declared contract", "normative producer-consumer agreement", "Observed contract", "sampled or measured behavior", "Observed regularity cannot silently amend an activated contract."),
    ("source_vs_accounting_truth", "Source truth", "authoritative record of the originating event or observation", "Accounting truth", "recognized, classified and periodized book of record", "Accounting adjustments may lawfully differ from operational events."),
    ("accounting_vs_control_truth", "Accounting truth", "booked financial representation", "Control truth", "independent total or assertion used to test the books", "A ledger cannot be its own independent control merely by relabeling it."),
    ("test_outcome_vs_gate", "Test outcome", "pass, fail, skip or execution error", "Gate disposition", "block, warn, quarantine, permit or waive", "Severity and policy determine disposition without changing outcome."),
    ("absence_vs_zero", "Absence", "no observed value or event", "Zero", "an observed numeric value equal to zero", "Coalescing absence to zero is information loss requiring authority."),
    ("freshness_vs_timeliness", "Freshness", "age since a relevant update or observation", "Timeliness", "availability within a use-specific deadline", "Fresh data can still arrive too late for a particular decision."),
    ("exact_vs_tolerant_reconciliation", "Exact equality", "identity after canonical representation", "Tolerant match", "acceptance within explicit rounding, time or amount bounds", "Tolerance must never be smuggled into equality."),
    ("evidence_vs_proof", "Evidence", "scoped observation, record or assertion", "Proof obligation", "claim whose required evidence and laws have been discharged", "A receipt alone does not prove every property of its subject."),
    ("correction_vs_restatement", "Correction", "repair of a value or relationship", "Restatement", "new authoritative edition superseding a published representation", "A restatement preserves the identity and auditability of the prior edition."),
    ("duplicate_vs_identity", "Duplicate candidate", "records similar enough to investigate", "Identity decision", "authorized assertion that records refer to the same entity", "Similarity score cannot authorize a merge."),
]


INNOVATIONS = [
    ("openmetrics_1", 2021, "OpenMetrics 1.0 standardized metric families, metadata and exemplars for portable signal exchange.", ["openmetrics"]),
    ("openlineage_quality_facets", 2021, "OpenLineage attached quality measurements to versioned dataset lineage rather than an unscoped dashboard.", ["openlineage-dq-metrics"]),
    ("openslo_v1", 2021, "OpenSLO introduced a vendor-neutral declarative object model for SLIs, objectives and alert policies.", ["openslo"]),
    ("mergeable_data_profiles", 2021, "whylogs popularized mergeable sketch-based profiles that reduce raw-data retention for monitoring.", ["whylogs"]),
    ("data_cascades", 2021, "Data-cascades research connected neglected data work to compounding downstream quality impact.", ["data-cascades"]),
    ("cloud_events_102", 2022, "CloudEvents 1.0.2 provided a stable interoperable envelope for evaluation and incident evidence events.", ["cloudevents"]),
    ("data_diff_cross_database", 2022, "data-diff exposed keyed row reconciliation across heterogeneous databases as an open implementation pattern.", ["data-diff"]),
    ("column_lineage_facet", 2022, "OpenLineage column-lineage facets made field-level impact scope portable across integrations.", ["openlineage-column-lineage"]),
    ("variable_acceptance_sampling", 2022, "ISO 3951-1:2022 refreshed standardized acceptance sampling by variables for bounded inspection cost.", ["iso3951-1"]),
    ("dbt_model_contracts", 2023, "dbt model contracts made selected output shape obligations enforceable at build time.", ["dbt-contracts"]),
    ("dagster_asset_checks", 2023, "Dagster asset checks made checks first-class objects linked to materialized assets.", ["dagster-asset-checks"]),
    ("otel_log_model_stable", 2023, "OpenTelemetry stabilized a common log data model with trace and resource correlation.", ["otel-logs"]),
    ("slsa_provenance_1", 2023, "SLSA 1.0 supplied a portable provenance predicate for digest-bound artifact evidence.", ["slsa-provenance"]),
    ("openlineage_1", 2023, "OpenLineage 1.0 stabilized a general runtime-lineage exchange contract.", ["openlineage"]),
    ("iso19157_revision", 2023, "ISO 19157-1:2023 revised geographic-data quality principles and evaluation vocabulary.", ["iso19157-1"]),
    ("odcs_3", 2024, "ODCS 3.0 broadened contract schema beyond tables and revised quality declarations for multiple engines.", ["odcs30-release"]),
    ("dbt_unit_tests", 2024, "dbt unit tests separated transformation-logic tests over fixtures from production-data tests.", ["dbt-unit-tests"]),
    ("dcat_3", 2024, "DCAT 3 expanded standardized dataset and data-service catalog metadata used to identify quality subjects.", ["w3c-dcat3"]),
    ("in_toto_attestation", 2024, "The in-toto attestation framework generalized typed digest-bound evidence statements.", ["in-toto-attestation"]),
    ("avro_112_resolution", 2024, "Avro 1.12 consolidated writer-reader schema resolution rules used in compatibility decisions.", ["avro-spec"]),
    ("vc_2", 2025, "Verifiable Credentials 2.0 standardized issuer, holder, subject, status and presentation semantics for portable certificates.", ["vc-data-model"]),
    ("odcs_31", 2025, "ODCS 3.1 refined a portable contract containing schema, quality, SLA, roles and server declarations.", ["odcs31"]),
    ("quality_assertions_facet", 2025, "OpenLineage data-quality assertions explicitly separated observed success from configured severity.", ["openlineage-dq-assertions"]),
    ("complete_unexpected_rows", 2025, "Great Expectations documented retrieval of complete failing-row sets separately from capped result summaries.", ["gx-unexpected-rows"]),
    ("shacl_12", 2026, "SHACL 1.2 evolved portable graph-constraint and validation-report semantics.", ["w3c-shacl12"]),
    ("validation_severity", 2026, "Great Expectations validation results exposed ordered failure severity independently from per-rule evidence.", ["gx-results"]),
]


GAPS = [
    ("metric_dimension_crosswalk", "No universal lossless crosswalk exists among ISO, DQV, industry and tool quality dimensions.", "semantic", "Adjudicate mappings as contextual, many-to-many claims with evidence."),
    ("fitness_loss_models", "Portable representations for use-specific loss, utility and risk tolerance remain immature.", "compiler", "Define a typed use-policy algebra and validate it in unrelated industries."),
    ("contract_observation_confidence", "There is no shared standard for confidence and expiry of observed-contract inferences.", "research", "Specify sampling horizon, confidence and invalidation laws."),
    ("rule_language_portability", "Quality DSLs disagree on nulls, three-valued logic, regex, sampling and failure rows.", "interoperability", "Build a semantic feature matrix and typed lowering refusals."),
    ("validator_failure_taxonomy", "Most tools incompletely distinguish ill-formed rule, unsupported feature, engine failure and failed assertion.", "operations", "Standardize a portable execution-outcome sum type."),
    ("stream_validation_finality", "Retractions, late data and changing windows complicate final validation outcomes in streams.", "research", "Model provisional and final evidence with progress frontiers."),
    ("profile_sketch_error", "Profile formats rarely exchange sketch algorithms, error bounds and merge compatibility.", "interoperability", "Define typed sketch metadata and merge proof obligations."),
    ("baseline_governance", "Baseline approval, contamination, seasonal editions and retirement lack a common contract.", "governance", "Define baseline lifecycle and independent validation receipts."),
    ("detector_calibration", "Cross-provider anomaly scores and sensitivity settings are not comparable.", "interoperability", "Require calibration curves, cost assumptions and editioned score semantics."),
    ("multiplicity_policy", "Quality monitoring frequently omits correction for many simultaneous statistical tests.", "assurance", "Make family definition and correction policy compiler decisions."),
    ("telemetry_cardinality_privacy", "Quality evidence can leak values or exceed telemetry cardinality budgets.", "assurance", "Qualify redaction, aggregation and exemplar policies."),
    ("quality_sli_denominators", "Denominator zero, missing expected events and late-arriving corrections lack portable SLI semantics.", "semantic", "Specify denominator completeness and revision policy."),
    ("case_exchange", "No broadly adopted interchange binds quality signals, breaks, evidence, decisions and corrective work.", "interoperability", "Prototype a CMMN-aligned quality-case envelope."),
    ("adjudication_authority", "Domain authority for declaring a defect is commonly implicit in workflow configuration.", "governance", "Represent authority, delegation and appeal as explicit policy."),
    ("truth_role_ontology", "Source, operational, accounting, regulatory and control truth roles lack a shared horizontal ontology.", "semantic", "Develop a role relation model that permits lawful disagreement."),
    ("probabilistic_reconciliation", "Probability-calibrated matching and unmatched-population guarantees are not standardized.", "research", "Define calibration, abstention and review obligations."),
    ("aggregate_masking", "Balanced totals can mask offsetting record-level breaks.", "assurance", "Require reconciliation coverage claims by grain and materiality."),
    ("correction_semantics", "Providers differ on update, merge, correction, compensating entry and restatement semantics.", "interoperability", "Compile only to providers that expose the required history law."),
    ("waiver_propagation", "Downstream propagation and expiry of quality waivers is weakly standardized.", "governance", "Bind waivers to exact subjects, uses and lineage edges."),
    ("certificate_revocation", "Quality certificates often lack online status and subject-version binding.", "assurance", "Require digest subject, validity and revocation mechanisms."),
    ("evidence_minimization", "Evidence retention and privacy minimization conflict when failing values are sensitive.", "assurance", "Define selective disclosure and reproducibility profiles."),
    ("reference_effective_time", "Reference-data validation often ignores bitemporal publication and effective dates.", "semantic", "Require reference edition, valid time and transaction time."),
    ("industry_materiality", "Materiality and fitness thresholds do not transfer safely across industries.", "industry", "Keep vertical policies outside the horizontal core and require explicit bindings."),
    ("independent_review", "The candidate context split has not received independent domain review.", "completeness", "Run split/merge adjudication with quality, observability and finance specialists."),
    ("enumeration_saturation", "No finite catalog can prove saturation of open-world methods, standards and provider behaviors.", "completeness", "Track search strategies, recurring freshness and typed unknowns."),
    ("provider_conformance", "No provider offer has been qualified against every candidate operation and refusal.", "implementation", "Build executable conformance suites per offer profile."),
    ("cost_models", "Portable cost and scan-budget models for validation and reconciliation are incomplete.", "compiler", "Add bounded resource estimates and refusal thresholds."),
    ("semantic_layer_contracts", "Metric-semantic-layer contracts rarely carry validation, fitness and evidence semantics end-to-end.", "cross-plane", "Define metric-definition to quality-requirement bindings."),
]


def camel(text: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[^a-zA-Z0-9]+", text) if part)


def ids_for_context(item: dict[str, Any]) -> dict[str, Any]:
    slug = item["slug"]
    context_id = f"qor.context.{slug}"
    capability_ids = [f"qor.capability.{slug}.{re.sub(r'[^a-z0-9]+', '_', cap.lower()).strip('_')}" for cap in item["capabilities"]]
    operation_ids = [f"qor.operation.{slug}.{re.sub(r'[^a-z0-9]+', '_', op.lower()).strip('_')}" for op in item["operations"]]
    return {"context_id": context_id, "capability_ids": capability_ids, "operation_ids": operation_ids}


def make_context_records() -> list[dict[str, Any]]:
    records = []
    for item in CONTEXTS:
        ids = ids_for_context(item)
        records.append({
            "context_id": ids["context_id"],
            "edition": EDITION,
            "status": CANDIDATE,
            "name": item["name"],
            "purpose": item["purpose"],
            "aggregate_candidates": [item["aggregate"]],
            "owns": item["capabilities"],
            "excludes": [f"final authority owned by adjacent contexts", f"provider-specific execution internals"],
            "sovereign_distinctions": item["distinctions"],
            "capability_refs": ids["capability_ids"],
            "operation_refs": ids["operation_ids"],
            "decision_refs": [f"qor.decision.{item['slug']}.primary"],
            "invariant_ref": f"qor.guard.{item['slug']}",
            "source_refs": item["sources"],
            "cross_plane_ref": f"qor.cross_plane.{item['slug']}",
            "candidate_note": "Boundary, name and ownership remain candidates pending split/merge adjudication.",
        })
    return records


def make_capability_records() -> list[dict[str, Any]]:
    records = []
    for item in CONTEXTS:
        ids = ids_for_context(item)
        for index, (name, capability_id) in enumerate(zip(item["capabilities"], ids["capability_ids"])):
            linked_ops = [op_id for pos, op_id in enumerate(ids["operation_ids"]) if pos % len(ids["capability_ids"]) == index]
            records.append({
                "capability_id": capability_id,
                "edition": EDITION,
                "status": CANDIDATE,
                "name": name.capitalize(),
                "owner_context": ids["context_id"],
                "definition": f"Provider-neutral capability to {name} within {item['name']}.",
                "input_kinds": [item["aggregate"], "Scope", "PolicyEdition"],
                "output_kinds": [f"{camel(name)}Result", "EvidenceReceipt"],
                "operation_refs": linked_ops,
                "quality_attributes": ["deterministic when method and inputs are fixed", "scope-preserving", "evidence-producing"],
                "source_refs": item["sources"],
                "candidate_note": "Capability grain and owner remain unadjudicated.",
            })
    return records


EFFECTFUL_PREFIXES = ("execute", "capture", "emit", "record", "open", "close", "apply", "post", "publish", "ingest", "attach", "sign", "verify", "revoke", "draw", "place", "request", "submit")


def make_operation_records() -> list[dict[str, Any]]:
    records = []
    for item in CONTEXTS:
        ids = ids_for_context(item)
        for index, (name, operation_id) in enumerate(zip(item["operations"], ids["operation_ids"])):
            effect = "effectful_evidence_io" if name.startswith(EFFECTFUL_PREFIXES) else "pure"
            records.append({
                "operation_id": operation_id,
                "edition": EDITION,
                "status": CANDIDATE,
                "name": name.capitalize(),
                "owner_context": ids["context_id"],
                "capability_ref": ids["capability_ids"][index % len(ids["capability_ids"])],
                "signature": {
                    "inputs": [{"name": "subject", "type": item["aggregate"]}, {"name": "scope", "type": "EvaluationScope"}, {"name": "policy", "type": "PolicyEdition"}],
                    "output": {"type": f"Result<{camel(name)}, QualityRefusal>"},
                },
                "preconditions": [item["invariants"][0], "All referenced editions and subject identities resolve."],
                "postconditions": [f"The {name} result is bound to its exact inputs and method edition.", "Any evidence receipt states observed versus asserted content."],
                "laws": ["identity preservation", "scope monotonicity", "no hidden default", "evidence attribution"],
                "effect_class": effect,
                "determinism": "deterministic_given_declared_clock_random_seed_and_provider_snapshot" if effect != "pure" else "deterministic",
                "idempotency": "idempotent_by_operation_key_or_explicitly_refused" if effect != "pure" else "referentially_transparent",
                "information_loss": "none unless an explicit approximation, redaction, aggregation or tolerance decision is bound",
                "refusal_codes": [f"QOR_{re.sub(r'[^A-Z0-9]+', '_', reason.upper())}" for reason in item["refusals"]],
                "source_refs": item["sources"],
                "candidate_note": "Signature and owner are research candidates; provider binding requires qualification.",
            })
    return records


def make_decision_records() -> list[dict[str, Any]]:
    records = []
    for item in CONTEXTS:
        ids = ids_for_context(item)
        records.append({
            "decision_id": f"qor.decision.{item['slug']}.primary",
            "edition": EDITION,
            "status": CANDIDATE,
            "owner_context": ids["context_id"],
            "question": item["decision"],
            "binding_phase": "intent_elaboration_before_provider_selection",
            "allowed_value_kinds": ["explicit_literal", "policy_reference", "typed_strategy_reference", "unresolved_gap"],
            "default_law": "Omission is a typed unresolved-decision gap; no provider default may silently supply semantics.",
            "evidence_required": ["decision authority", "scope", "rationale", "applicable source or policy"],
            "affects_operations": ids["operation_ids"],
            "source_refs": item["sources"],
        })
    return records


def make_guard_records() -> list[dict[str, Any]]:
    records = []
    for item in CONTEXTS:
        ids = ids_for_context(item)
        records.append({
            "guard_id": f"qor.guard.{item['slug']}",
            "edition": EDITION,
            "status": CANDIDATE,
            "owner_context": ids["context_id"],
            "invariants": item["invariants"],
            "refusals": [{"code": f"QOR_{re.sub(r'[^A-Z0-9]+', '_', reason.upper())}", "condition": reason, "phase": "pre_execution", "recoverability": "requires_explicit_resolution"} for reason in item["refusals"]],
            "must_not_collapse": item["distinctions"],
            "source_refs": item["sources"],
        })
    return records


def make_requirement_records() -> list[dict[str, Any]]:
    records = []
    for item in CONTEXTS:
        ids = ids_for_context(item)
        records.append({
            "requirement_id": f"qor.requirement.{item['slug']}.core",
            "edition": EDITION,
            "status": CANDIDATE,
            "intent_kind": item["slug"],
            "owner_context": ids["context_id"],
            "required_capabilities": ids["capability_ids"],
            "required_decisions": [f"qor.decision.{item['slug']}.primary"],
            "proof_obligations": item["invariants"],
            "acceptable_effects": ["pure", "effectful_evidence_io"],
            "unresolved_behavior": "refuse_with_typed_gap",
            "source_refs": item["sources"],
        })
    return records


def make_offer_records() -> list[dict[str, Any]]:
    records = []
    for item in CONTEXTS:
        ids = ids_for_context(item)
        records.append({
            "offer_id": f"qor.offer_template.{item['slug']}.provider_neutral",
            "edition": EDITION,
            "status": CANDIDATE,
            "provider_class": "unbound_provider_template",
            "owner_context": ids["context_id"],
            "offered_capabilities": ids["capability_ids"],
            "operation_profiles": [{"operation_ref": op_id, "support": "requires_provider_qualification"} for op_id in ids["operation_ids"]],
            "guarantees": item["invariants"],
            "unsupported_semantics": ["undeclared approximation", "implicit truth-role selection", "unscoped mutation"],
            "qualification_receipts_required": ["conformance test receipt", "versioned provider capability statement"],
            "source_refs": item["sources"],
        })
    return records


def make_compiler_mappings(operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "mapping_id": operation["operation_id"].replace("qor.operation.", "qor.compiler_mapping."),
        "edition": EDITION,
        "status": CANDIDATE,
        "operation_ref": operation["operation_id"],
        "requirement_ref": f"qor.requirement.{operation['owner_context'].removeprefix('qor.context.')}.core",
        "offer_template_ref": f"qor.offer_template.{operation['owner_context'].removeprefix('qor.context.')}.provider_neutral",
        "lowering_stages": ["normalize intent", "resolve semantic decisions", "type-check subject and scope", "match qualified offer", "emit plan plus proof obligations"],
        "must_refuse_when": ["required decision unresolved", "operation profile unqualified", "invariant proof absent", "effect authority absent"],
        "result_kind": "candidate_binding_or_typed_gap",
        "source_refs": operation["source_refs"],
    } for operation in operations]


def make_library_records() -> list[dict[str, Any]]:
    records = []
    for item in CONTEXTS:
        ids = ids_for_context(item)
        pure_ops = []
        effect_ports = []
        for name, op_id in zip(item["operations"], ids["operation_ids"]):
            (effect_ports if name.startswith(EFFECTFUL_PREFIXES) else pure_ops).append(op_id)
        records.append({
            "library_id": f"qor.library.{item['slug']}_kernel",
            "edition": EDITION,
            "status": CANDIDATE,
            "name": f"{item['name']} kernel",
            "owner_context": ids["context_id"],
            "boundary_kind": "pure_kernel_with_explicit_effect_ports",
            "pure_operation_refs": pure_ops,
            "effect_operation_refs": effect_ports,
            "input_types": [item["aggregate"], "EvaluationScope", "PolicyEdition"],
            "output_types": [f"Result<{item['aggregate']}, QualityRefusal>", "EvidenceReceipt"],
            "forbidden_dependencies": ["vendor SDK in pure kernel", "ambient clock", "ambient randomness", "mutable global state", "hidden network access"],
            "port_candidates": ["subject reader", "evidence sink", "policy resolver", "clock", "identity resolver"],
            "source_refs": item["sources"],
            "candidate_note": "Library split is proposed, not an implementation commitment.",
        })
    return records


def make_cross_plane_records() -> list[dict[str, Any]]:
    plane_laws = {
        "type_shape": "Bind carriers, schema editions, missingness and comparison semantics.",
        "pipeline": "Bind exact data cuts, execution points, gates, retries and correction effects.",
        "lineage": "Bind declared and observed dependencies, data versions and evidence provenance.",
        "governance": "Bind authority, policy, waiver, retention and certification scope.",
        "semantic": "Bind business meaning, metric definition, grain, truth role and intended use.",
        "runtime": "Bind telemetry, resource budgets, failure modes, state and operational identity.",
        "industry": "Bind vertical materiality, regulation, workflow and authoritative references outside the horizontal kernel.",
    }
    records = []
    for item in CONTEXTS:
        ids = ids_for_context(item)
        records.append({
            "mapping_id": f"qor.cross_plane.{item['slug']}",
            "edition": EDITION,
            "status": CANDIDATE,
            "context_ref": ids["context_id"],
            "plane_bindings": [{"plane": plane, "relationship": plane_laws[plane], "ownership": "partnership_or_customer_supplier_to_be_adjudicated"} for plane in ["type_shape", "pipeline", "lineage", "governance", "semantic", "runtime", "industry"]],
            "priority_planes": item["planes"],
            "industry_case_candidates": item["industries"],
            "non_collapse_laws": item["distinctions"],
            "source_refs": item["sources"],
        })
    return records


def make_distinction_records() -> list[dict[str, Any]]:
    return [{
        "distinction_id": f"qor.distinction.{slug}",
        "edition": EDITION,
        "status": CANDIDATE,
        "left": {"term": left_term, "definition": left_definition},
        "right": {"term": right_term, "definition": right_definition},
        "non_collapse_law": law,
        "compiler_consequence": "Preserve separate types and require an explicit, evidenced conversion or decision.",
    } for slug, left_term, left_definition, right_term, right_definition, law in SEMANTIC_DISTINCTIONS]


def make_innovation_records() -> list[dict[str, Any]]:
    return [{
        "innovation_id": f"qor.innovation.{slug}",
        "edition": EDITION,
        "status": CANDIDATE,
        "year": year,
        "description": description,
        "relevance": ["candidate capability expansion", "compiler or interoperability evidence"],
        "source_refs": [f"qor.src.{item}" for item in refs],
        "limitation": "Recent evidence of a mechanism or practice; not proof of universal adoption or final ownership.",
    } for slug, year, description, refs in INNOVATIONS]


def make_gap_records() -> list[dict[str, Any]]:
    return [{
        "gap_id": f"qor.gap.{slug}",
        "edition": EDITION,
        "status": "explicit_open_gap",
        "statement": statement,
        "gap_class": gap_class,
        "blocking": gap_class in {"semantic", "compiler", "completeness", "assurance"},
        "next_evidence_action": action,
        "compiler_behavior": "emit_typed_gap_and_refuse_semantic_guessing",
    } for slug, statement, gap_class, action in GAPS]


def obj_schema(title: str, id_field: str, required: list[str], properties: dict[str, Any]) -> dict[str, Any]:
    base = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://shannon-insight.local/schemas/qor/{id_field}.schema.json",
        "title": title,
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
    }
    return base


STR = {"type": "string", "minLength": 1}
STRINGS = {"type": "array", "items": STR, "minItems": 1, "uniqueItems": True}
SOURCE_REFS = {"type": "array", "items": {"type": "string", "pattern": "^qor\\.src\\."}, "minItems": 1, "uniqueItems": True}
STATUS = {"const": CANDIDATE}


def schemas() -> dict[str, dict[str, Any]]:
    source_schema = obj_schema("Quality evidence source", "source", ["source_id", "edition", "title", "publisher", "url", "evidence_role", "source_kind", "publication_year", "areas", "claims_supported", "primary_source", "authority_scope", "limitations", "accessed_at"], {
        "source_id": {"type": "string", "pattern": "^qor\\.src\\."}, "edition": {"type": "integer", "minimum": 1}, "title": STR, "publisher": STR, "url": {"type": "string", "pattern": "^https://"}, "evidence_role": {"enum": ["normative_authority", "open_specification", "regulatory_authority", "original_research", "implementation_evidence"]}, "source_kind": STR, "publication_year": {"type": "integer", "minimum": 1900, "maximum": 2026}, "areas": STRINGS, "claims_supported": STRINGS, "primary_source": {"const": True}, "authority_scope": STR, "limitations": STR, "accessed_at": {"const": AS_OF},
    })
    return {
        "source": source_schema,
        "bounded-context-candidate": obj_schema("Quality bounded-context candidate", "bounded-context-candidate", ["context_id", "edition", "status", "name", "purpose", "aggregate_candidates", "owns", "excludes", "sovereign_distinctions", "capability_refs", "operation_refs", "decision_refs", "invariant_ref", "source_refs", "cross_plane_ref", "candidate_note"], {"context_id": {"type": "string", "pattern": "^qor\\.context\\."}, "edition": {"type": "integer"}, "status": STATUS, "name": STR, "purpose": STR, "aggregate_candidates": STRINGS, "owns": STRINGS, "excludes": STRINGS, "sovereign_distinctions": STRINGS, "capability_refs": STRINGS, "operation_refs": STRINGS, "decision_refs": STRINGS, "invariant_ref": STR, "source_refs": SOURCE_REFS, "cross_plane_ref": STR, "candidate_note": STR}),
        "capability": obj_schema("Quality capability candidate", "capability", ["capability_id", "edition", "status", "name", "owner_context", "definition", "input_kinds", "output_kinds", "operation_refs", "quality_attributes", "source_refs", "candidate_note"], {"capability_id": {"type": "string", "pattern": "^qor\\.capability\\."}, "edition": {"type": "integer"}, "status": STATUS, "name": STR, "owner_context": STR, "definition": STR, "input_kinds": STRINGS, "output_kinds": STRINGS, "operation_refs": STRINGS, "quality_attributes": STRINGS, "source_refs": SOURCE_REFS, "candidate_note": STR}),
        "typed-operation": obj_schema("Typed quality operation candidate", "typed-operation", ["operation_id", "edition", "status", "name", "owner_context", "capability_ref", "signature", "preconditions", "postconditions", "laws", "effect_class", "determinism", "idempotency", "information_loss", "refusal_codes", "source_refs", "candidate_note"], {"operation_id": {"type": "string", "pattern": "^qor\\.operation\\."}, "edition": {"type": "integer"}, "status": STATUS, "name": STR, "owner_context": STR, "capability_ref": STR, "signature": {"type": "object"}, "preconditions": STRINGS, "postconditions": STRINGS, "laws": STRINGS, "effect_class": {"enum": ["pure", "effectful_evidence_io"]}, "determinism": STR, "idempotency": STR, "information_loss": STR, "refusal_codes": STRINGS, "source_refs": SOURCE_REFS, "candidate_note": STR}),
        "decision-point": obj_schema("Quality compiler decision point", "decision-point", ["decision_id", "edition", "status", "owner_context", "question", "binding_phase", "allowed_value_kinds", "default_law", "evidence_required", "affects_operations", "source_refs"], {"decision_id": {"type": "string", "pattern": "^qor\\.decision\\."}, "edition": {"type": "integer"}, "status": STATUS, "owner_context": STR, "question": STR, "binding_phase": STR, "allowed_value_kinds": STRINGS, "default_law": STR, "evidence_required": STRINGS, "affects_operations": STRINGS, "source_refs": SOURCE_REFS}),
        "invariant-refusal": obj_schema("Quality invariant and refusal candidate", "invariant-refusal", ["guard_id", "edition", "status", "owner_context", "invariants", "refusals", "must_not_collapse", "source_refs"], {"guard_id": {"type": "string", "pattern": "^qor\\.guard\\."}, "edition": {"type": "integer"}, "status": STATUS, "owner_context": STR, "invariants": STRINGS, "refusals": {"type": "array", "items": {"type": "object"}, "minItems": 1}, "must_not_collapse": STRINGS, "source_refs": SOURCE_REFS}),
        "requirement": obj_schema("Quality intent requirement candidate", "requirement", ["requirement_id", "edition", "status", "intent_kind", "owner_context", "required_capabilities", "required_decisions", "proof_obligations", "acceptable_effects", "unresolved_behavior", "source_refs"], {"requirement_id": {"type": "string", "pattern": "^qor\\.requirement\\."}, "edition": {"type": "integer"}, "status": STATUS, "intent_kind": STR, "owner_context": STR, "required_capabilities": STRINGS, "required_decisions": STRINGS, "proof_obligations": STRINGS, "acceptable_effects": STRINGS, "unresolved_behavior": {"const": "refuse_with_typed_gap"}, "source_refs": SOURCE_REFS}),
        "offer-template": obj_schema("Quality capability offer template", "offer-template", ["offer_id", "edition", "status", "provider_class", "owner_context", "offered_capabilities", "operation_profiles", "guarantees", "unsupported_semantics", "qualification_receipts_required", "source_refs"], {"offer_id": {"type": "string", "pattern": "^qor\\.offer_template\\."}, "edition": {"type": "integer"}, "status": STATUS, "provider_class": STR, "owner_context": STR, "offered_capabilities": STRINGS, "operation_profiles": {"type": "array", "items": {"type": "object"}, "minItems": 1}, "guarantees": STRINGS, "unsupported_semantics": STRINGS, "qualification_receipts_required": STRINGS, "source_refs": SOURCE_REFS}),
        "compiler-mapping": obj_schema("Quality compiler mapping candidate", "compiler-mapping", ["mapping_id", "edition", "status", "operation_ref", "requirement_ref", "offer_template_ref", "lowering_stages", "must_refuse_when", "result_kind", "source_refs"], {"mapping_id": {"type": "string", "pattern": "^qor\\.compiler_mapping\\."}, "edition": {"type": "integer"}, "status": STATUS, "operation_ref": STR, "requirement_ref": STR, "offer_template_ref": STR, "lowering_stages": STRINGS, "must_refuse_when": STRINGS, "result_kind": STR, "source_refs": SOURCE_REFS}),
        "library-boundary": obj_schema("Quality library boundary candidate", "library-boundary", ["library_id", "edition", "status", "name", "owner_context", "boundary_kind", "pure_operation_refs", "effect_operation_refs", "input_types", "output_types", "forbidden_dependencies", "port_candidates", "source_refs", "candidate_note"], {"library_id": {"type": "string", "pattern": "^qor\\.library\\."}, "edition": {"type": "integer"}, "status": STATUS, "name": STR, "owner_context": STR, "boundary_kind": STR, "pure_operation_refs": {"type": "array", "items": STR, "uniqueItems": True}, "effect_operation_refs": {"type": "array", "items": STR, "uniqueItems": True}, "input_types": STRINGS, "output_types": STRINGS, "forbidden_dependencies": STRINGS, "port_candidates": STRINGS, "source_refs": SOURCE_REFS, "candidate_note": STR}),
        "cross-plane-mapping": obj_schema("Quality cross-plane mapping candidate", "cross-plane-mapping", ["mapping_id", "edition", "status", "context_ref", "plane_bindings", "priority_planes", "industry_case_candidates", "non_collapse_laws", "source_refs"], {"mapping_id": {"type": "string", "pattern": "^qor\\.cross_plane\\."}, "edition": {"type": "integer"}, "status": STATUS, "context_ref": STR, "plane_bindings": {"type": "array", "items": {"type": "object"}, "minItems": 7}, "priority_planes": STRINGS, "industry_case_candidates": STRINGS, "non_collapse_laws": STRINGS, "source_refs": SOURCE_REFS}),
        "semantic-distinction": obj_schema("Quality semantic distinction", "semantic-distinction", ["distinction_id", "edition", "status", "left", "right", "non_collapse_law", "compiler_consequence"], {"distinction_id": {"type": "string", "pattern": "^qor\\.distinction\\."}, "edition": {"type": "integer"}, "status": STATUS, "left": {"type": "object"}, "right": {"type": "object"}, "non_collapse_law": STR, "compiler_consequence": STR}),
        "innovation": obj_schema("Recent quality innovation candidate", "innovation", ["innovation_id", "edition", "status", "year", "description", "relevance", "source_refs", "limitation"], {"innovation_id": {"type": "string", "pattern": "^qor\\.innovation\\."}, "edition": {"type": "integer"}, "status": STATUS, "year": {"type": "integer", "minimum": 2021, "maximum": 2026}, "description": STR, "relevance": STRINGS, "source_refs": SOURCE_REFS, "limitation": STR}),
        "gap": obj_schema("Explicit quality universe gap", "gap", ["gap_id", "edition", "status", "statement", "gap_class", "blocking", "next_evidence_action", "compiler_behavior"], {"gap_id": {"type": "string", "pattern": "^qor\\.gap\\."}, "edition": {"type": "integer"}, "status": {"const": "explicit_open_gap"}, "statement": STR, "gap_class": STR, "blocking": {"type": "boolean"}, "next_evidence_action": STR, "compiler_behavior": {"const": "emit_typed_gap_and_refuse_semantic_guessing"}}),
    }


def build_records() -> dict[str, list[dict[str, Any]]]:
    operations = make_operation_records()
    return {
        "sources.jsonl": SOURCES,
        "bounded-context-candidates.jsonl": make_context_records(),
        "capabilities.jsonl": make_capability_records(),
        "typed-operations.jsonl": operations,
        "decision-points.jsonl": make_decision_records(),
        "invariants-refusals.jsonl": make_guard_records(),
        "requirements.jsonl": make_requirement_records(),
        "offer-templates.jsonl": make_offer_records(),
        "compiler-mappings.jsonl": make_compiler_mappings(operations),
        "library-boundary-candidates.jsonl": make_library_records(),
        "cross-plane-mappings.jsonl": make_cross_plane_records(),
        "semantic-distinctions.jsonl": make_distinction_records(),
        "innovations.jsonl": make_innovation_records(),
        "gaps.jsonl": make_gap_records(),
    }


def serialize_jsonl(records: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n" for record in records)


def serialize_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def manifest(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    authority_counts = Counter(source["evidence_role"] for source in SOURCES)
    counts = {name.removesuffix(".jsonl").replace("-", "_"): len(values) for name, values in records.items()}
    counts["capability_operation_candidates"] = len(records["capabilities.jsonl"]) + len(records["typed-operations.jsonl"])
    return {
        "universe_id": "quality_observability_reconciliation",
        "edition": EDITION,
        "as_of": AS_OF,
        "status": CANDIDATE,
        "completion_claim": False,
        "counts": counts,
        "source_authority_counts": dict(sorted(authority_counts.items())),
        "required_cross_planes": ["type_shape", "pipeline", "lineage", "governance", "semantic", "runtime", "industry"],
        "forbidden_core_methods": ["large-language-model methods", "generative methods", "prompt-dependent adjudication"],
        "standing": "broad evidence-backed horizontal candidate corpus; independent review, provider qualification and enumeration saturation remain open",
    }


def render() -> dict[Path, str]:
    records = build_records()
    output = {ROOT / name: serialize_jsonl(values) for name, values in records.items()}
    for name, schema in schemas().items():
        output[ROOT / "schemas" / f"{name}.schema.json"] = serialize_json(schema)
    output[ROOT / "manifest.json"] = serialize_json(manifest(records))
    return output


def main() -> int:
    rendered = render()
    for path, content in sorted(rendered.items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    counts = manifest(build_records())["counts"]
    print(
        "WROTE quality/observability/reconciliation corpus: "
        f"{counts['bounded_context_candidates']} contexts, "
        f"{counts['capabilities']} capabilities, "
        f"{counts['typed_operations']} typed operations, "
        f"{counts['sources']} sources, {counts['innovations']} recent innovations, "
        f"{counts['gaps']} explicit gaps"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
