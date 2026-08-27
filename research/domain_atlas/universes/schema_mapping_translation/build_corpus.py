#!/usr/bin/env python3
"""Build the exact, provider-neutral schema-mapping compiler and executor corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for row in rows) + "\n"


def S(source_id: str, title: str, authority: str, url: str, supports: str, does_not_prove: str) -> dict:
    return {
        "source_id": f"source.schema-mapping.{source_id}", "title": title, "authority": authority,
        "url": url, "retrieved": AS_OF, "source_kind": "primary_or_official",
        "supports": supports, "does_not_prove": does_not_prove,
    }


SOURCES = [
    S("avro.current", "Apache Avro Specification", "Apache Avro", "https://avro.apache.org/docs/current/specification/", "directional writer/reader resolution, aliases, defaults, promotions, unions and logical types", "Avro resolution is not cross-format semantic equivalence, business conversion or consumer acceptance."),
    S("protobuf.proto3", "Protocol Buffers Language Guide: proto3", "Protocol Buffers", "https://protobuf.dev/programming-guides/proto3/", "field-number identity, unknown fields, presence, oneof and wire-safe/compatible/unsafe changes", "Wire compatibility does not prove source-code, JSON, application or semantic compatibility."),
    S("jsonschema.core.2020-12", "JSON Schema Core 2020-12", "JSON Schema", "https://json-schema.org/draft/2020-12/json-schema-core", "schema resources, references, dynamic scope, applicators, annotations and unevaluated locations", "Schema evaluation does not populate defaults or define a universal data transformation."),
    S("jsonschema.validation.2020-12", "JSON Schema Validation 2020-12", "JSON Schema", "https://json-schema.org/draft/2020-12/json-schema-validation", "validation vocabularies, assertions, annotations, formats and defaults", "A validation annotation is not an observed source value or an instruction to mutate an instance."),
    S("arrow.columnar.1.5", "Apache Arrow Columnar Format", "Apache Arrow", "https://arrow.apache.org/docs/format/Columnar.html", "physical layouts, parametric and nested types, nullability, unions, maps, dictionaries and extension types", "Layout compatibility does not establish application meaning or a lossless cross-carrier mapping."),
    S("parquet.logical-types", "Apache Parquet Logical Type Definitions", "Apache Parquet", "https://github.com/apache/parquet-format/blob/master/LogicalTypes.md", "physical/logical type annotations, decimals, temporal kinds, nested lists/maps and legacy compatibility", "A representable physical annotation does not preserve zone, ordering, precision or source semantics automatically."),
    S("iceberg.spec", "Apache Iceberg Specification", "Apache Iceberg", "https://iceberg.apache.org/spec/", "stable field identifiers, schema editions, allowed promotions and evolution restrictions", "Table-schema evolution is not a generic record translation plan or permission to rewrite source meaning."),
    S("orc.spec", "Apache ORC Specification", "Apache ORC", "https://orc.apache.org/specification/", "type trees, column identifiers, compound types, decimal and temporal encodings", "One ORC type tree does not prove equivalent identity or value domains in another carrier."),
    S("csvw.metadata", "Metadata Vocabulary for Tabular Data", "W3C", "https://www.w3.org/TR/tabular-metadata/", "tabular columns, datatypes, null/default/required annotations and transformations", "CSV metadata does not make ambiguous, malformed or lossy source text authoritative."),
    S("csvw.model", "Model for Tabular Data and Metadata on the Web", "W3C", "https://www.w3.org/TR/tabular-data-model/", "cell parsing, normalized values, defaults, nulls, separators and table structure", "Parsed cell values do not prove business identity, units or reference-data correspondence."),
    S("xsd.1.1.structures", "XML Schema Definition Language 1.1 Part 1: Structures", "W3C", "https://www.w3.org/TR/xmlschema11-1/", "XML component models, type alternatives, open content, substitution and structural validation", "XML validity does not establish a unique mapping into JSON, relational or columnar structures."),
    S("rfc8259", "RFC 8259: The JavaScript Object Notation Data Interchange Format", "IETF", "https://www.rfc-editor.org/rfc/rfc8259", "JSON value kinds, number interoperability, member-name behavior and encoding", "Successful JSON parsing does not resolve duplicate names, numeric range or target-type loss by itself."),
    S("rfc3339", "RFC 3339: Date and Time on the Internet", "IETF", "https://www.rfc-editor.org/rfc/rfc3339", "timestamp syntax, offsets, precision and leap-second considerations", "An offset timestamp is not a named-zone schedule and an absent zone is not UTC."),
    S("rfc9557", "RFC 9557: Date and Time on the Internet with Additional Information", "IETF", "https://www.rfc-editor.org/rfc/rfc9557", "named-zone and calendar annotations layered on RFC 3339 timestamps", "A zone annotation does not remove edition, ambiguity or future rule-change concerns."),
    S("unicode.uax15", "Unicode Standard Annex #15: Normalization Forms", "Unicode Consortium", "https://unicode.org/reports/tr15/", "canonical and compatibility normalization, stability and conformance tests", "Compatibility normalization may erase meaningful distinctions and is never a harmless hidden default."),
    S("odata.csdl-json.4.02", "OData CSDL JSON Representation 4.02", "OASIS", "https://docs.oasis-open.org/odata/odata-csdl-json/v4.02/odata-csdl-json-v4.02.html", "structured types, collections, nullability, defaults, precision, scale and spatial reference facets", "OData representation rules do not establish a universal carrier type lattice."),
    S("airbyte.protocol", "Airbyte Protocol", "Airbyte", "https://docs.airbyte.com/platform/understanding-airbyte/airbyte-protocol", "source/destination catalogs, JSON schemas, record envelopes, mismatch behavior and protocol editions", "A connector's best-effort loading posture is not an acceptable universal loss or unknown-field policy."),
    S("debezium.event-flattening", "Debezium New Record State Extraction", "Debezium", "https://debezium.io/documentation/reference/stable/transformations/event-flattening.html", "change envelopes, create/update/delete operations, tombstones and flattening trade-offs", "Flattening may erase operation and envelope evidence and therefore cannot be a silent mapping step."),
    S("cloudevents.1.0", "CloudEvents Specification 1.0", "CNCF CloudEvents", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", "event envelope attributes, payload schema reference and extension attributes", "An event envelope does not define payload translation, transport progress or delivery acceptance."),
    S("odcs.3.1", "Open Data Contract Standard 3.1", "Bitol", "https://bitol-io.github.io/open-data-contract-standard/v3.1.0/", "editioned data-contract schema and semantic bindings", "A data contract references schemas and policies but does not itself execute carrier translation."),
]


CONTEXT_ID = "context.schema_mapping.translation"
CONTEXTS = [{
    "context_id": CONTEXT_ID,
    "name": "Carrier Schema Mapping and Translation",
    "sovereign_question": "Given exact resolved source and target carrier-schema editions, what explicit structural mapping is valid, what information is lost or ambiguous, and how can that immutable plan be evaluated deterministically over records and change envelopes?",
    "inside": ["provider-neutral carrier type descriptors", "field/path matching policy", "structural mapping plans", "value-domain representability", "explicit residual and loss classification", "evolution invalidation", "deterministic record and change-envelope evaluation", "translation traces"],
    "outside": ["schema artifact registration or reference retrieval", "data-contract ownership", "ontology or business-concept equivalence", "master/reference crosswalks", "unit/currency/domain conversion authority", "source capture and cursor semantics", "physical delivery and target commits", "provider adapters and format parsers"],
    "owner": "authority.schema_mapping.translation",
    "status": "specified_candidate",
}]


COMPILER_DECISIONS = [
    "source_target_schema_closure_identity", "source_target_carrier_profile", "field_identity_and_path_matching",
    "name_alias_and_position_posture", "recursive_reference_and_cycle_posture", "mapping_cardinality",
    "logical_physical_and_extension_type_relation", "null_missing_empty_default_distinction", "unknown_field_posture",
    "unknown_enum_and_union_branch_posture", "union_discriminator_selection", "numeric_range_and_signedness",
    "decimal_precision_scale_and_rounding", "floating_special_values_and_total_order", "temporal_kind_unit_and_precision",
    "offset_zone_dst_and_leap_second", "text_encoding_and_unicode_normalization", "collation_and_case_posture",
    "binary_and_fixed_length_posture", "collection_order_and_duplicate_map_keys", "identity_and_key_field_preservation",
    "constraint_and_requiredness_preservation", "change_operation_delete_and_tombstone", "loss_taxonomy_and_acceptance",
    "schema_evolution_invalidation", "deterministic_rule_precedence", "compile_resource_budget",
]

EXECUTOR_DECISIONS = [
    "compiled_plan_identity", "input_conformance_posture", "runtime_value_error_posture", "residual_accumulation",
    "batch_failure_and_partial_result", "trace_granularity", "parallel_ordering_and_determinism", "execution_resource_budget",
]


def D(owner: str, name: str) -> dict:
    return {"decision_id": f"decision.schema_mapping.{owner}.{name}", "owner_context": CONTEXT_ID,
            "question": f"What exact {name.replace('_', ' ')} applies?", "default": None,
            "default_law": "forbidden", "status": "declared"}


DECISION_ROWS = [D("compiler", name) for name in COMPILER_DECISIONS] + [D("executor", name) for name in EXECUTOR_DECISIONS]


def O(owner: str, name: str, inputs: list[str], output: str) -> dict:
    return {"operation_ref": f"operation.schema_mapping.{owner}.{name}", "input_types": inputs,
            "output_type": f"Result<{output},SchemaMappingRefusal>", "purity": "pure"}


COMPILER_OPERATIONS = [
    O("compiler", "validate_mapping_context", ["SourceSchemaClosureRef", "TargetSchemaClosureRef", "CarrierProfilePair", "SchemaMappingPolicy"], "ValidatedMappingContext"),
    O("compiler", "derive_field_candidates", ["ValidatedMappingContext", "FieldMatchPolicy", "ResourceBudget"], "FieldCandidateSet"),
    O("compiler", "compile_mapping_plan", ["ValidatedMappingContext", "FieldMappingDeclarationSet", "SchemaMappingPolicy", "ResourceBudget"], "CompiledSchemaMapping"),
    O("compiler", "evaluate_mapping_totality", ["CompiledSchemaMapping", "SchemaDomainSummary", "TotalityPolicy"], "MappingTotalityReport"),
    O("compiler", "classify_mapping_residuals", ["CompiledSchemaMapping", "LossClassificationPolicy"], "MappingResidualSet"),
    O("compiler", "validate_loss_acceptance", ["MappingResidualSet", "ExternalLossDecisionRef", "LossAcceptancePolicy"], "AcceptedMappingPlan"),
    O("compiler", "compare_mapping_editions", ["CompiledSchemaMapping", "CompiledSchemaMapping", "MappingComparisonPolicy"], "SchemaMappingDiff"),
    O("compiler", "evaluate_schema_evolution_impact", ["CompiledSchemaMapping", "SchemaClosureDiff", "EvolutionImpactPolicy"], "MappingEvolutionImpact"),
    O("compiler", "explain_mapping_plan", ["CompiledSchemaMapping", "ExplanationScope", "ResourceBudget"], "MappingExplanation"),
]

EXECUTOR_OPERATIONS = [
    O("executor", "translate_record", ["AcceptedMappingPlan", "SourceRecord", "ExecutionPolicy", "ResourceBudget"], "RecordTranslationResult"),
    O("executor", "translate_record_batch", ["AcceptedMappingPlan", "SourceRecordBatch", "BatchExecutionPolicy", "ResourceBudget"], "BatchTranslationResult"),
    O("executor", "translate_change_envelope", ["AcceptedMappingPlan", "SourceChangeEnvelope", "ChangeEnvelopePolicy", "ResourceBudget"], "ChangeEnvelopeTranslationResult"),
    O("executor", "validate_translation_result", ["AcceptedMappingPlan", "TranslationResult", "TargetConformancePolicy"], "ValidatedTranslationResult"),
    O("executor", "explain_translation_trace", ["TranslationTrace", "ExplanationScope", "ResourceBudget"], "TranslationExplanation"),
]


COMPILER_TYPES = [
    "SchemaMappingCompilerEdition", "SchemaMappingId", "SchemaMappingEdition", "SourceSchemaClosureRef", "TargetSchemaClosureRef",
    "SchemaClosureDiff", "CarrierFormatRef", "CarrierProfileRef", "CarrierProfilePair", "ResolvedCarrierSchema", "ResolvedCarrierField",
    "StructuralPath", "FieldIdentity", "FieldName", "FieldAlias", "FieldPosition", "SourceFieldRef", "TargetFieldRef",
    "CarrierTypeDescriptor", "PhysicalTypeDescriptor", "LogicalTypeDescriptor", "ExtensionTypeRef", "TypeParameterSet",
    "Nullability", "PresenceKind", "MissingnessKind", "EmptyValueKind", "DefaultValueDeclaration", "DefaultProvenance",
    "NumericDomain", "Signedness", "BitWidth", "DecimalPrecision", "DecimalScale", "RoundingMode", "OverflowPosture",
    "FloatingSpecialValuePosture", "TemporalKind", "TemporalUnit", "TemporalPrecision", "OffsetKind", "ZoneRuleRef",
    "DstAmbiguityPosture", "LeapSecondPosture", "TextEncodingRef", "UnicodeVersionRef", "NormalizationForm",
    "CollationRef", "CasePosture", "BinaryLengthConstraint", "CollectionOrder", "MapKeyPolicy", "UnionDescriptor",
    "DiscriminatorPolicy", "EnumDomain", "ConstraintSet", "IdentityFieldRef", "KeySemanticsRef", "ChangeOperationKind",
    "TombstonePosture", "FieldMatchPolicy", "FieldCandidate", "FieldCandidateSet", "FieldMappingDeclaration",
    "FieldMappingDeclarationSet", "MappingCardinality", "MappingExpression", "MappingRule", "RulePrecedence",
    "ValidatedMappingContext", "CompiledFieldMapping", "CompiledSchemaMapping", "MappingPlanDigest", "MappingResidual",
    "MappingResidualKind", "InformationLossKind", "LossSeverity", "MappingResidualSet", "ExternalLossDecisionRef",
    "AcceptedMappingPlan", "SchemaDomainSummary", "MappingTotalityReport", "SchemaMappingDiff", "MappingEvolutionImpact",
    "MappingExplanation", "SchemaMappingPolicy", "LossClassificationPolicy", "LossAcceptancePolicy", "EvolutionImpactPolicy",
    "MappingComparisonPolicy", "TotalityPolicy", "ResourceBudget", "SchemaMappingRefusal",
]

EXECUTOR_TYPES = [
    "SchemaMappingExecutorEdition", "AcceptedMappingPlan", "MappingPlanDigest", "SourceRecord", "SourceRecordBatch",
    "SourceChangeEnvelope", "SourceValue", "TargetRecord", "TargetRecordBatch", "TargetChangeEnvelope", "TargetValue",
    "RecordOccurrenceRef", "ChangeOccurrenceRef", "ExecutionAttemptId", "TranslationResidual", "TranslationResidualSet",
    "TranslationTrace", "TranslationStepTrace", "RecordTranslationResult", "BatchTranslationResult",
    "ChangeEnvelopeTranslationResult", "TranslationResult", "ValidatedTranslationResult", "TranslationExplanation",
    "ExecutionPolicy", "BatchExecutionPolicy", "ChangeEnvelopePolicy", "TargetConformancePolicy", "ExplanationScope",
    "ResourceBudget", "SchemaMappingRefusal",
]


SHARED_LAWS = [
    "Schema mapping, schema compatibility, schema evolution, ontology mapping, reference crosswalk, formula transformation and business equivalence are distinct contracts.",
    "Schema artifact identity, resolved reference-closure identity, carrier profile, mapping edition, execution attempt and record occurrence are distinct.",
    "Source and target schemas are external immutable edition references; this context neither registers them nor makes one current.",
    "Field name, alias, ordinal position, carrier tag and stable field identity are distinct and no one is a hidden universal match key.",
    "Physical layout, carrier logical type, application value domain and business meaning remain distinct.",
    "Absent, missing, null, empty, defaulted, unknown, invalid, tombstone and deleted are never silently collapsed.",
    "A target default constructs a target value; it is not an observation from the source and retains default provenance.",
    "Unknown fields, enum symbols and union branches are preserved, residualized, quarantined or refused by explicit policy and never silently discarded.",
    "Every narrowing, rounding, truncation, overflow, underflow, precision change, zone loss, normalization or ordering change is classified and attributable.",
    "An unqualified local time is not UTC; local time, offset time, instant and named-zone civil time remain distinct.",
    "Canonical and compatibility Unicode normalization are distinct and bind an exact Unicode edition and form.",
    "Identity and key fields cannot be removed, synthesized or coerced without an explicit mapping declaration and externally accepted loss decision.",
    "Create, update, delete, snapshot-read, truncate, tombstone and envelope absence remain distinct change semantics.",
    "A schema-compatible change can invalidate a compiled mapping, and an unchanged field name does not prove unchanged identity or value domain.",
    "Structural translation may execute an externally bound exact conversion contract but cannot invent units, currencies, code mappings or business equivalence.",
    "Every result binds exact source and target schema closures, carrier profiles, mapping edition, policy digest and resource budget.",
    "A model or agent may propose attributed field candidates but cannot accept a match, choose hidden policy, waive residual loss or qualify an implementation.",
]


LIBRARIES = [
    {
        "library_id": "library.schema_mapping.compiler", "name": "Schema Mapping Compiler",
        "library_kind": "semantic_pure", "semantic_owner_context": CONTEXT_ID, "status": "specified",
        "candidate_responsibility": "compile exact source and target carrier-schema closures into an immutable loss-explicit structural mapping plan",
        "effect_boundary": "pure_no_io", "public_types": COMPILER_TYPES, "public_traits": ["SchemaMappingCompilerAlgebra"],
        "operation_refs": [op["operation_ref"] for op in COMPILER_OPERATIONS], "operations": COMPILER_OPERATIONS,
        "decision_refs": [row["decision_id"] for row in DECISION_ROWS if ".compiler." in row["decision_id"]],
        "configuration_contracts": ["SchemaMappingPolicy"], "laws": SHARED_LAWS + [
            "A derived field candidate is not an accepted mapping and always retains the rule and evidence that produced it.",
            "Mapping compilation is deterministic for the same closures, declarations, decision editions and budget; rule precedence is explicit.",
            "Loss acceptance is externally issued, exact-scope and revocable; the compiler validates it but cannot grant it.",
            "A compiled plan is immutable and dependency-digest bound; any affected schema, profile, rule or decision change requires impact evaluation.",
        ],
        "invariants": ["all mapping choices are explicit and no-default", "all information loss and ambiguity are typed residuals", "compilation performs no ambient I/O", "agent proposals never acquire authority"],
        "error_contracts": ["SourceSchemaClosureUnbound", "TargetSchemaClosureUnbound", "CarrierProfileUnbound", "SchemaReferenceUnresolved",
                            "FieldIdentityAmbiguous", "FieldMappingIncomplete", "MappingCardinalityUnsupported", "RecursiveMappingUnbounded",
                            "TypeRelationUnrepresentable", "NullMissingDefaultAmbiguous", "UnknownFieldPostureMissing", "UnionDiscriminatorAmbiguous",
                            "NumericPolicyMissing", "DecimalPolicyMissing", "TemporalPolicyMissing", "TextPolicyMissing", "KeyFieldLossUnaccepted",
                            "ChangeOperationLossUnaccepted", "ConstraintLossUnaccepted", "LossDecisionMissing", "LossDecisionScopeMismatch",
                            "EvolutionImpactUnknown", "RulePrecedenceAmbiguous", "UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
        "dependencies": ["library.schema_registry.reference_closure"], "evidence_refs": [row["source_id"] for row in SOURCES],
        "oracles": ["cross-carrier canonical mapping fixtures", "writer-reader direction negative twins", "numeric and decimal boundary corpus",
                    "temporal zone precision and leap-second corpus", "Unicode normalization conformance corpus", "nested union map and recursion corpus",
                    "missing-null-default-unknown truth table", "schema evolution invalidation metamorphic tests", "loss monotonicity properties",
                    "two independent compiler implementations and differential plans"],
        "gaps": ["No implementation is qualified; two independent compilers and executed conformance remain required."],
        "must_not_own": ["schema registration, current-version or compatibility authority", "ontology, term or business-concept mapping",
                         "master/reference value crosswalks", "unit, currency, formula or domain-conversion semantics", "source capture or cursor semantics",
                         "physical delivery, target commit or factual acceptance", "format parser/provider adapter implementation", "loss approval or provider qualification"],
        "qualification_required": False,
    },
    {
        "library_id": "library.schema_mapping.executor", "name": "Schema Mapping Executor",
        "library_kind": "algorithm_pure", "semantic_owner_context": CONTEXT_ID, "status": "specified",
        "candidate_responsibility": "evaluate an accepted immutable schema-mapping plan over records and change envelopes with deterministic residual and trace output",
        "effect_boundary": "pure_no_io", "public_types": EXECUTOR_TYPES, "public_traits": ["SchemaMappingExecutorAlgebra"],
        "operation_refs": [op["operation_ref"] for op in EXECUTOR_OPERATIONS], "operations": EXECUTOR_OPERATIONS,
        "decision_refs": [row["decision_id"] for row in DECISION_ROWS if ".executor." in row["decision_id"]],
        "configuration_contracts": ["SchemaMappingExecutionPolicy"], "laws": SHARED_LAWS + [
            "The executor evaluates only an accepted exact plan and cannot infer, extend, repair or approve mappings at runtime.",
            "One record failure, partial batch result, cancellation, resource exhaustion and total batch refusal remain distinct outcomes.",
            "Parallel execution may change physical schedule but not accepted record order or per-record result under the declared ordering profile.",
            "A translation trace proves the named evaluation steps and values only; it is not delivery acknowledgement or target acceptance.",
        ],
        "invariants": ["execution is deterministic for the same plan input and budget", "runtime loss is never omitted from the result", "execution performs no ambient I/O", "unknown completion cannot arise inside the pure boundary"],
        "error_contracts": ["MappingPlanUnaccepted", "MappingPlanDigestMismatch", "SourceRecordSchemaMismatch", "SourceValueInvalid",
                            "UnknownFieldEncountered", "UnknownEnumEncountered", "UnionBranchUnresolved", "NumericOverflow", "DecimalRoundingRefused",
                            "TemporalValueAmbiguous", "TextEncodingInvalid", "NormalizationLossRefused", "CollectionConstraintViolated",
                            "IdentityFieldUnavailable", "ChangeOperationUnsupported", "TargetConstraintViolated", "TraceBudgetExceeded",
                            "PartialBatchRefused", "UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
        "dependencies": ["library.schema_mapping.compiler"], "evidence_refs": [row["source_id"] for row in SOURCES],
        "oracles": ["accepted-plan execution fixtures", "value-domain boundary and malformed corpus", "record/batch equivalence property",
                    "serial/parallel determinism property", "residual accumulation monotonicity", "change-envelope and tombstone corpus",
                    "finite-budget and cancellation model tests", "cross-format round-trip tests where lossless is claimed",
                    "two independent executor implementations and differential results"],
        "gaps": ["No implementation is qualified; two independent executors and executed conformance remain required."],
        "must_not_own": ["mapping inference, plan acceptance or loss approval", "schema parsing, registration or reference retrieval",
                         "ontology, reference-data, unit, currency, formula or business conversion semantics", "source capture, checkpoint or replay",
                         "delivery acknowledgement, target commit or factual acceptance", "provider qualification or operational SLO"],
        "qualification_required": False,
    },
]


LENSES = [
    ("value", "Who needs this and what independent outcome exists?", "Delivery compilers need a reusable exact structural plan; runtimes need a separately optimizable plan evaluator.", "Retain two libraries inside one context; neither is a product."),
    ("semantic", "Which meanings are owned?", "The context owns carrier-shape correspondence, representability and residual loss only.", "Exclude ontology, reference, formula, unit, currency and business equivalence."),
    ("behavior", "Which decisions and transitions are owned?", "Compilation validates and seals plans; evaluation consumes accepted immutable plans and returns total typed outcomes.", "Executor cannot infer or mutate a mapping."),
    ("authority", "Who may assert, accept or waive?", "Schema owners issue closures; accountable external authorities accept loss; libraries only validate scoped references.", "No hidden approval and no agent authority."),
    ("consistency", "Which invariants require one boundary?", "One plan atomically binds both schema closures, all mapping rules, residuals, policies and digest.", "Keep plan integrity in compiler; evaluation is stateless per explicit input."),
    ("variability", "What must be configurable or replaceable?", "Format profiles, matching, numeric, temporal, text, unknown, constraint and loss policies vary independently.", "Every choice is an editioned no-default decision."),
    ("software", "What is independently testable and versionable?", "Cold-path plan compilation and hot-path evaluation have independent API, test and replacement seams.", "Split compiler from executor; keep format adapters outside."),
    ("operation", "Can it run, scale, fail and recover independently?", "Compilation is control-plane and bounded; execution is data-plane, batchable and parallelizable; both are pure.", "Separate resource envelopes and qualification suites."),
    ("economics", "Are cost, adoption and exit measurable?", "Compiler cost scales with schema complexity; executor cost scales with records/bytes and dominates throughput.", "Permit independent optimization and substitution, but do not promote either to product."),
    ("empirical", "What evidence supports the boundary?", "Avro, Protobuf, Iceberg, Arrow, Parquet, CSVW, Airbyte and Debezium expose recurring but non-identical resolution concerns.", "Use standards as evidence and conformance sources, never as universal equivalence proof."),
    ("analytical", "What mathematical or algorithmic problem is owned?", "Compilation is constrained correspondence plus partial/loss classification; execution is deterministic typed evaluation.", "Do not absorb probabilistic entity resolution or semantic inference."),
    ("system", "Which composition hazards appear?", "Silent defaulting, key loss, timezone coercion, envelope flattening and stale plans can corrupt downstream state while every adapter appears healthy.", "Fail closed, retain residuals, bind exact editions and invalidate affected plans."),
]

LENS_ROWS = [{"lens_id": f"lens.schema_mapping.{name}", "lens": name, "question": question,
              "finding": finding, "boundary_consequence": consequence,
              "method_refs": ["method.domain_driven_design", "method.feature_oriented_domain_analysis", "method.formal_conformance_testing"],
              "status": "applied"} for name, question, finding, consequence in LENSES]


BOUNDARY_VERDICTS = [{
    "verdict_id": "verdict.schema_mapping.compiler_executor_split",
    "subject_refs": ["library.schema_mapping.compiler", "library.schema_mapping.executor"],
    "disposition": "retain_split_with_shared_published_plan_contract",
    "rationale": "Compilation owns low-frequency semantic adjudication and immutable plan construction; execution owns high-frequency deterministic evaluation. They differ in volatility, resource economics, optimization, qualification and replacement while sharing only an editioned AcceptedMappingPlan published language.",
    "shared_contract_types": ["AcceptedMappingPlan", "MappingPlanDigest", "ResourceBudget", "SchemaMappingRefusal"],
    "split_proofs": ["different operations", "different decision sets", "different resource envelopes", "independent substitution", "one-way dependency from executor to compiler contract"],
    "merge_falsifier": "Merge only if independent implementations and change histories show that compilation and execution cannot be versioned, qualified or substituted independently without semantic duplication.",
    "further_split_falsifier": "Split carrier types or loss classification only if an independently owned language, operation set and replacement seam emerges rather than a shared DTO vocabulary.",
    "status": "candidate_boundary_adjudicated_not_ratified",
}]


NEGATIVES = [
    ("one_monolith", "Compilation and per-record execution are one indivisible library.", "Retain separate cold-path compiler and hot-path executor contracts."),
    ("compatibility_mapping", "Schema compatibility proves a usable mapping.", "Compile an explicit directional mapping and residual report."),
    ("name_identity", "Equal field names prove equal identity and meaning.", "Bind the declared identity/match policy and retain ambiguity."),
    ("position_identity", "Equal ordinal positions prove the same field.", "Treat position as one policy input, never universal identity."),
    ("alias_equivalence", "An alias proves business equivalence.", "Use aliases only under the exact carrier and schema resolution rules."),
    ("default_observed", "A target default is an observed source value.", "Mark target construction and retain default provenance."),
    ("null_missing", "Null and missing are interchangeable.", "Preserve presence and value state independently."),
    ("empty_null", "Empty string or collection means null.", "Require an explicit domain-external conversion or preserve the value."),
    ("unknown_drop", "Unknown fields may be dropped because the target cannot name them.", "Preserve, residualize, quarantine or refuse by explicit policy."),
    ("json_number", "Every JSON number round-trips through IEEE binary64.", "Check exact value domain and emit precision/range loss."),
    ("numeric_widen", "A syntactically wider numeric type is always behavior preserving.", "Check ranges, signedness, partition/hash use, special values and consumers."),
    ("decimal_round", "Decimal scale reduction is harmless.", "Bind rounding and overflow policy and classify changed values."),
    ("local_utc", "A timestamp without zone denotes UTC.", "Preserve local/offset/instant/named-zone kinds and refuse ambiguity."),
    ("offset_zone", "A numeric offset is a named timezone.", "Retain offset and named-zone identity separately."),
    ("precision_loss", "Millisecond and nanosecond timestamps are equivalent.", "Classify precision loss and validate accepted bounds."),
    ("unicode_harmless", "Any Unicode normalization is lossless.", "Bind exact form and Unicode edition; compatibility loss is explicit."),
    ("collation_encoding", "Valid UTF encoding preserves collation and comparison behavior.", "Keep encoding, normalization, collation and case posture separate."),
    ("map_order", "Map and object iteration order is always irrelevant.", "Bind ordering and duplicate-key policy."),
    ("union_guess", "A union branch can be selected from the runtime value without a policy.", "Require an exact discriminator or unambiguous branch rule."),
    ("key_synth", "A missing identity key may be silently synthesized.", "Require an explicit mapping and external authority or refuse."),
    ("flatten_delete", "Flattening a CDC envelope may discard operation and tombstone distinctions.", "Map envelope semantics explicitly and retain operation evidence."),
    ("wire_semantic", "Wire-safe evolution is semantically safe for every consumer.", "Evaluate mapping impact and downstream value domains separately."),
    ("stale_plan", "A compiled mapping remains valid after either schema changes.", "Bind closure digests and evaluate invalidation before execution."),
    ("roundtrip_claim", "One successful example proves lossless round-trip behavior.", "Prove the declared domain with property, boundary and differential tests."),
    ("trace_acceptance", "A successful translation trace is a delivery or factual-acceptance receipt.", "Keep translation, delivery commit and business acceptance distinct."),
    ("agent_acceptance", "A model may accept candidate matches or waive residuals.", "Allow attributed proposals only; deterministic rules and named authorities decide."),
]

NEGATIVE_ROWS = [{"negative_id": f"negative.schema-mapping.{slug}", "unsafe_inference": unsafe,
                  "required_behavior": required, "status": "active"} for slug, unsafe, required in NEGATIVES]


COMPILER_ROWS = []
for library in LIBRARIES:
    stem = library["library_id"].removeprefix("library.")
    requirement = f"requirement.{stem}.implementation"
    offer = f"offer.{stem}.reference"
    COMPILER_ROWS.extend([
        {"record_kind": "capability_requirement", "requirement_id": requirement, "subject_ref": library["library_id"],
         "required_operations": library["operation_refs"], "required_decisions": library["decision_refs"],
         "fallback_law": "refuse", "status": "declared"},
        {"record_kind": "capability_offer", "offer_id": offer, "subject_ref": library["library_id"],
         "claimed_operations": library["operation_refs"], "qualified_implementation_count": 0,
         "portable": False, "selectable": False, "status": "specified_unimplemented"},
        {"record_kind": "binding_rule", "binding_rule_id": f"binding.{stem}", "requirement_ref": requirement,
         "offer_ref": offer, "structural_match": True,
         "selection_law": "Structural match never promotes an unqualified or non-portable implementation.",
         "selectable": False, "status": "declared"},
    ])


FILES = {
    "sources.jsonl": SOURCES,
    "bounded-contexts.jsonl": CONTEXTS,
    "decision-points.jsonl": DECISION_ROWS,
    "boundary-lens-adjudication.jsonl": LENS_ROWS,
    "boundary-verdicts.jsonl": BOUNDARY_VERDICTS,
    "library-contracts.jsonl": LIBRARIES,
    "compiler-contracts.jsonl": COMPILER_ROWS,
    "negative-twins.jsonl": NEGATIVE_ROWS,
}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = lines(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {
        "manifest_id": "schema_mapping_translation_v0_1_0", "as_of": AS_OF, "edition": EDITION,
        "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False,
        "qualified_implementation_count": 0,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS schema mapping translation: {len(SOURCES)} sources, 1 context, {len(DECISION_ROWS)} decisions, 2 exact libraries, {len(COMPILER_OPERATIONS) + len(EXECUTOR_OPERATIONS)} operations, 12 lenses")


if __name__ == "__main__":
    main()
