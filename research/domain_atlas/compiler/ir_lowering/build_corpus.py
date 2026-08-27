#!/usr/bin/env python3
"""Deterministically build the candidate intent-to-solution IR/lowering corpus.

This is a research-corpus generator, not a compiler implementation.  Every emitted
record is candidate status, sorted by stable identity, and contains no provider
binding inferred from a name.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHEMAS = ROOT / "schemas"
EDITION = 1
AS_OF = "2026-08-25"


def dump_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_jsonl(path: Path, records: list[dict]) -> None:
    ordered = sorted(records, key=record_identity)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in ordered), encoding="utf-8")


def record_identity(record: dict) -> str:
    for key in (
        "source_id", "context_id", "node_id", "edge_id", "pass_id", "invariant_id",
        "diagnostic_id", "proof_id", "rewrite_id", "decision_trace_id", "incremental_rule_id", "migration_id",
        "extension_id", "artifact_id", "library_id", "mapping_id", "innovation_id", "gap_id",
        "trace_id",
    ):
        if key in record:
            return str(record[key])
    raise ValueError(f"record has no stable identity: {record}")


def digest_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def slugify(value: str) -> str:
    result = []
    for char in value.lower():
        result.append(char if char.isalnum() else "_")
    return "".join(result).strip("_")


SOURCE_ROWS = [
    # Core compiler IR and pass infrastructure.
    ("llvm.langref", "LLVM Language Reference Manual", "LLVM Project", "official_specification", "https://llvm.org/docs/LangRef.html", 2026, ["ssa", "types", "effects", "target_ir"]),
    ("llvm.newpm", "Using the New Pass Manager", "LLVM Project", "official_documentation", "https://llvm.org/docs/NewPassManager.html", 2026, ["passes", "analysis_invalidation"]),
    ("llvm.remarks", "LLVM Remarks", "LLVM Project", "official_documentation", "https://llvm.org/docs/Remarks.html", 2026, ["decision_trace", "optimization_diagnostics"]),
    ("llvm.bitcode", "LLVM Bitcode File Format", "LLVM Project", "official_specification", "https://llvm.org/docs/BitCodeFormat.html", 2026, ["serialization", "versioning"]),
    ("llvm.reproducible", "LLVM Coding Standards: Reproducible Builds", "LLVM Project", "official_documentation", "https://llvm.org/docs/CodingStandards.html#reproducible-builds", 2026, ["reproducibility"]),
    ("mlir.langref", "MLIR Language Reference", "LLVM Project", "official_specification", "https://mlir.llvm.org/docs/LangRef/", 2026, ["multi_level_ir", "regions", "symbols"]),
    ("mlir.dialects", "Defining Dialects", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/DefiningDialects/", 2026, ["extensions", "verification"]),
    ("mlir.interfaces", "MLIR Interfaces", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/Interfaces/", 2026, ["open_extension", "semantic_interfaces"]),
    ("mlir.passes", "MLIR Pass Infrastructure", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/PassManagement/", 2026, ["passes", "analysis_preservation", "failure"]),
    ("mlir.conversion", "MLIR Dialect Conversion", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/DialectConversion/", 2026, ["lowering", "legality"]),
    ("mlir.rewriting", "MLIR Pattern Rewriting", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/PatternRewriter/", 2026, ["rewrite", "termination"]),
    ("mlir.symbols", "MLIR Symbols and Symbol Tables", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/SymbolsAndSymbolTables/", 2026, ["symbol_resolution"]),
    ("mlir.diagnostics", "MLIR Diagnostic Infrastructure", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/Diagnostics/", 2026, ["typed_diagnostics"]),
    ("mlir.bytecode", "MLIR Bytecode Format", "LLVM Project", "official_specification", "https://mlir.llvm.org/docs/BytecodeFormat/", 2026, ["serialization", "dialect_versioning", "migration"]),
    ("mlir.transform", "MLIR Transform Dialect", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/Dialects/Transform/", 2026, ["transform_ir", "failure_modes", "reproducible_sequences"]),
    ("mlir.irdl", "MLIR IRDL Dialect", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/Dialects/IRDL/", 2026, ["dynamic_ir_definition", "constraints"]),
    ("mlir.dataflow", "MLIR DataFlow Framework", "LLVM Project", "official_documentation", "https://mlir.llvm.org/docs/Tutorials/DataFlowAnalysis/", 2026, ["analysis", "fixpoint"]),
    # Rust compiler concepts and incremental computation.
    ("rust.reference", "The Rust Reference", "Rust Project", "language_specification", "https://doc.rust-lang.org/reference/", 2026, ["types", "traits", "unsafe", "abi"]),
    ("rust.hir", "rustc-dev-guide: High-level IR", "Rust Project", "official_documentation", "https://rustc-dev-guide.rust-lang.org/hir.html", 2026, ["ast_lowering", "stable_identity"]),
    ("rust.mir", "rustc-dev-guide: Mid-level IR", "Rust Project", "official_documentation", "https://rustc-dev-guide.rust-lang.org/mir/index.html", 2026, ["typed_ir", "control_flow"]),
    ("rust.queries", "rustc-dev-guide: Query System", "Rust Project", "official_documentation", "https://rustc-dev-guide.rust-lang.org/query.html", 2026, ["memoization", "dependency_tracking"]),
    ("rust.incremental", "rustc-dev-guide: Incremental Compilation", "Rust Project", "official_documentation", "https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation-in-detail.html", 2026, ["incremental_recompilation", "fingerprints"]),
    ("rust.stablehash", "rustc-dev-guide: Stable Hashing", "Rust Project", "official_documentation", "https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation-in-detail.html#checking-query-results-for-changes-hashstable-and-stable-hashing", 2026, ["canonical_hash", "identity"]),
    ("salsa.book", "Salsa Book", "Salsa Project", "official_documentation", "https://salsa-rs.github.io/salsa/", 2026, ["incremental_queries", "tracked_inputs"]),
    # Portable analytical and relational IRs.
    ("substrait.spec", "Substrait Specification", "Substrait Project", "official_specification", "https://substrait.io/spec/specification/", 2026, ["logical_plan", "portability"]),
    ("substrait.types", "Substrait Type System", "Substrait Project", "official_specification", "https://substrait.io/types/type_system/", 2026, ["strict_types", "explicit_casts", "variations"]),
    ("substrait.relations", "Substrait Relations", "Substrait Project", "official_specification", "https://substrait.io/relations/logical_relations/", 2026, ["relational_algebra", "logical_operations"]),
    ("substrait.extensions", "Substrait Extensions", "Substrait Project", "official_specification", "https://substrait.io/extensions/", 2026, ["extension_urn", "custom_relation", "semantic_boundary"]),
    ("substrait.versioning", "Substrait Versioning and Compatibility", "Substrait Project", "official_specification", "https://substrait.io/spec/versioning/", 2026, ["versioning", "compatibility"]),
    ("calcite.algebra", "Apache Calcite Algebra", "Apache Software Foundation", "official_documentation", "https://calcite.apache.org/docs/algebra.html", 2026, ["relational_algebra", "traits"]),
    ("postgres.planner", "PostgreSQL Planner/Optimizer", "PostgreSQL Global Development Group", "official_documentation", "https://www.postgresql.org/docs/current/planner-optimizer.html", 2026, ["logical_physical_separation", "costing"]),
    ("datafusion.optimizer", "Apache DataFusion Query Optimizer", "Apache Software Foundation", "official_documentation", "https://datafusion.apache.org/library-user-guide/query-optimizer.html", 2026, ["logical_rewrite", "physical_rewrite"]),
    ("dbsp.paper", "DBSP: Automatic Incremental View Maintenance for Rich Query Languages", "PVLDB", "primary_research", "https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf", 2023, ["incremental_dataflow", "algebraic_derivative"]),
    ("openivm.paper", "OpenIVM: a SQL-to-SQL Compiler for Incremental Computations", "OpenIVM Authors", "primary_research", "https://arxiv.org/abs/2404.16486", 2024, ["incremental_lowering", "view_maintenance"]),
    # Portable dataflow models.
    ("beam.model", "Apache Beam Programming Model", "Apache Software Foundation", "official_documentation", "https://beam.apache.org/documentation/programming-guide/", 2026, ["portable_dataflow", "windowing", "triggers"]),
    ("beam.portability", "Apache Beam Portability Framework", "Apache Software Foundation", "official_documentation", "https://beam.apache.org/roadmap/portability/", 2026, ["runner_portability", "environment_contract"]),
    ("beam.protocol", "Apache Beam Runner API Protocol", "Apache Software Foundation", "official_specification", "https://github.com/apache/beam/blob/master/model/pipeline/src/main/proto/org/apache/beam/model/pipeline/v1/beam_runner_api.proto", 2026, ["portable_plan", "capability_urn"]),
    ("flink.architecture", "Apache Flink Architecture", "Apache Software Foundation", "official_documentation", "https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/flink-architecture/", 2026, ["dataflow_runtime", "deployment"]),
    ("flink.tables", "Apache Flink Dynamic Tables", "Apache Software Foundation", "official_documentation", "https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/sql-table-concepts/dynamic_tables/", 2026, ["stream_relational_semantics", "changelog"]),
    ("flink.state", "Apache Flink Stateful Stream Processing", "Apache Software Foundation", "official_documentation", "https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/stateful-stream-processing/", 2026, ["state", "checkpoint", "recovery"]),
    # Configuration and total evaluation semantics.
    ("cue.spec", "The CUE Language Specification", "CUE Project", "language_specification", "https://cuelang.org/docs/reference/spec/", 2026, ["constraints", "unification", "explicit_defaults"]),
    ("dhall.standard", "Dhall Language Standard", "Dhall Project", "language_specification", "https://github.com/dhall-lang/dhall-lang/tree/master/standard", 2026, ["normalization", "imports", "types"]),
    ("dhall.safety", "Dhall Safety Guarantees", "Dhall Project", "official_documentation", "https://docs.dhall-lang.org/discussions/Safety-guarantees.html", 2026, ["totality", "normalization", "no_effects"]),
    ("nix.language", "Nix Language", "Nix Project", "language_specification", "https://nix.dev/manual/nix/latest/language/", 2026, ["lazy_evaluation", "configuration"]),
    ("nix.derivations", "Nix Derivations", "Nix Project", "official_specification", "https://nix.dev/manual/nix/latest/language/derivations", 2026, ["build_graph", "declared_inputs"]),
    ("nix.store", "Nix Store Object Model", "Nix Project", "official_specification", "https://nix.dev/manual/nix/latest/store/store-object.html", 2026, ["content_address", "artifact_identity"]),
    ("starlark.spec", "Starlark Language Specification", "Starlark Project", "language_specification", "https://github.com/bazelbuild/starlark/blob/master/spec.md", 2026, ["deterministic_evaluation", "modules"]),
    ("jsonschema.2020", "JSON Schema Draft 2020-12", "JSON Schema Project", "standard", "https://json-schema.org/draft/2020-12/json-schema-core", 2022, ["schema", "validation", "vocabulary"]),
    ("rfc8785", "RFC 8785 JSON Canonicalization Scheme", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8785", 2020, ["canonical_serialization", "digest"]),
    # Logic, constraints, and independently checkable proofs.
    ("souffle.language", "Souffle Language Documentation", "Souffle Project", "official_documentation", "https://souffle-lang.github.io/docs.html", 2026, ["datalog", "fixpoint", "stratification"]),
    ("souffle.provenance", "Souffle Provenance", "Souffle Project", "official_documentation", "https://souffle-lang.github.io/provenance", 2026, ["proof_tree", "explanation"]),
    ("datafrog.api", "Datafrog Rust API", "Rust Project Contributors", "official_documentation", "https://docs.rs/datafrog/latest/datafrog/", 2019, ["datalog", "monotone_iteration"]),
    ("smtlib.27", "SMT-LIB Standard Version 2.7", "SMT-LIB Initiative", "standard", "https://smt-lib.org/language.shtml", 2026, ["smt", "models", "theories"]),
    ("cvc5.proofs", "cvc5 Proof Production", "cvc5 Project", "official_documentation", "https://cvc5.github.io/docs/cvc5-1.3.1/proofs/proofs.html", 2026, ["smt_proofs", "proof_export"]),
    ("alethe.spec", "Alethe Proof Format", "Alethe Project", "official_specification", "https://verit.loria.fr/documentation/alethe-spec.pdf", 2022, ["smt_proof_exchange"]),
    ("drat.trim", "DRAT Format and DRAT-trim Checker", "DRAT-trim Authors", "reference_checker", "https://github.com/marijnheule/drat-trim", 2023, ["sat_certificate", "independent_checking"]),
    ("veripb", "VeriPB Proof Checker", "VeriPB Project", "reference_checker", "https://gitlab.com/MIAOresearch/software/VeriPB", 2026, ["pseudo_boolean_certificate", "optimization_proof"]),
    ("egg.paper", "egg: Fast and Extensible Equality Saturation", "ACM POPL", "primary_research", "https://dl.acm.org/doi/10.1145/3434304", 2021, ["e_graph", "rewrite_equivalence"]),
    ("egglog.paper", "Better Together: Unifying Datalog and Equality Saturation", "ACM PLDI", "primary_research", "https://dl.acm.org/doi/10.1145/3591239", 2023, ["e_graph", "datalog", "explanations"]),
    # Portable low-level component boundaries.
    ("wasm.core", "WebAssembly Core Specification", "W3C WebAssembly Community Group", "standard", "https://webassembly.github.io/spec/core/", 2026, ["portable_target", "validation"]),
    ("wasm.component", "WebAssembly Component Model", "W3C WebAssembly Community Group", "official_specification", "https://github.com/WebAssembly/component-model", 2026, ["component_interfaces", "composition"]),
    ("wasm.canonicalabi", "WebAssembly Component Model Canonical ABI", "W3C WebAssembly Community Group", "official_specification", "https://github.com/WebAssembly/component-model/blob/main/design/mvp/CanonicalABI.md", 2026, ["canonical_abi", "resource_types"]),
    ("wasi.preview2", "WASI Preview 2", "Bytecode Alliance", "official_specification", "https://github.com/WebAssembly/WASI/tree/main/wasip2", 2024, ["portable_effect_interfaces", "capabilities"]),
    ("wit.spec", "WebAssembly Interface Types (WIT)", "Bytecode Alliance", "official_specification", "https://component-model.bytecodealliance.org/design/wit.html", 2026, ["interface_types", "worlds"]),
    # Build graphs, reproducibility, and evidence envelopes.
    ("bazel.build", "Bazel Build Encyclopedia", "Bazel Project", "official_documentation", "https://bazel.build/reference/be/overview", 2026, ["build_graph", "actions"]),
    ("bazel.hermeticity", "Bazel Hermeticity", "Bazel Project", "official_documentation", "https://bazel.build/basics/hermeticity", 2026, ["hermetic_build", "declared_inputs"]),
    ("bazel.remote", "Bazel Remote Caching", "Bazel Project", "official_documentation", "https://bazel.build/remote/caching", 2026, ["action_digest", "cache"]),
    ("reprobuilds.definition", "Reproducible Builds Definition", "Reproducible Builds Project", "community_specification", "https://reproducible-builds.org/docs/definition/", 2026, ["reproducibility", "environment"]),
    ("slsa.12", "SLSA Specification 1.2", "OpenSSF", "standard", "https://slsa.dev/spec/v1.2/", 2025, ["build_provenance", "verification"]),
    ("intoto.spec", "in-toto Specification", "in-toto Project", "official_specification", "https://github.com/in-toto/docs/blob/master/in-toto-spec.md", 2026, ["supply_chain_layout", "link_metadata"]),
    ("spdx.30", "SPDX Specification 3.0", "Linux Foundation SPDX Project", "standard", "https://spdx.github.io/spdx-spec/v3.0/", 2024, ["artifact_identity", "provenance"]),
    ("oci.image", "OCI Image Format Specification", "Open Container Initiative", "standard", "https://github.com/opencontainers/image-spec", 2026, ["content_address", "manifest"]),
]


SOURCES = [
    {
        "source_id": f"source.ir.{sid}", "edition": EDITION, "status": "reviewed_candidate",
        "title": title, "publisher": publisher, "source_kind": kind, "url": url,
        "publication_or_live_year": year, "accessed_at": AS_OF, "supports_topics": topics,
        "authority_scope": "Authoritative only for the named specification, implementation, or reported research result.",
        "limitations": [
            "Does not establish this corpus as complete.",
            "Does not qualify any provider occurrence or prove cross-system conformance.",
        ],
    }
    for sid, title, publisher, kind, url, year, topics in SOURCE_ROWS
]


CONTEXT_ROWS = [
    ("source_text", "Source text and lexical structure", "UTF-8 source units, tokens, spans, comments, and recovery", "semantic interpretation"),
    ("declaration_ast", "Declaration AST", "Parsed declarations, expressions, constraints, non-goals, and explicit holes", "name resolution and domain truth"),
    ("module_graph", "Module and import graph", "Module identities, import edges, cycles, visibility, and digests", "semantic aliases"),
    ("symbol_resolution", "Symbol and scope resolution", "Namespaces, scopes, overload candidate sets, editions, and ambiguity", "provider discovery"),
    ("edition_resolution", "Edition and lifecycle resolution", "Exact edition selection, deprecation, compatibility, and migration need", "silent latest-version selection"),
    ("canonical_reference", "Canonical-reference adjudication", "Evidence-bearing equivalent/narrower/broader/overlap/disjoint/missing assertions", "spelling-based equivalence"),
    ("language_context", "Bounded-context language IR", "Owned meanings, homonyms, ACL translations, imports, exports, exclusions", "physical layouts"),
    ("authority_resolution", "Authority resolution", "Owners, approvers, delegations, precedence, waivers, and expiry", "authentication mechanisms"),
    ("default_resolution", "Default resolution", "Explicit value, authority, applicability, precedence, provenance, and invalidation", "implementation-language defaults"),
    ("constraint_normalization", "Constraint normalization", "Canonical forms, contradictions, implications, finite domains, and residual holes", "heuristic guessing"),
    ("analytical_case", "Analytical case IR", "Question, actors, population, unit, grain, time, outcome, action, and feedback", "metric-only declarations"),
    ("study_design", "Study and analytical design", "Design, estimand, assumptions, diagnostics, uncertainty, evaluation, refusal", "kernel selection"),
    ("method_selection", "Analytical method selection", "Applicability proofs and retained rejected methods", "library-name dispatch"),
    ("observation_contract", "Observation contract", "Fact authority, measurement, missingness, censoring, uncertainty, provenance", "wire encoding"),
    ("semantic_types", "Semantic type system", "Carrier/value/observation/structure meaning and valid operations", "storage layout"),
    ("shape_system", "Shape and grain system", "Keys, cardinality, nesting, order, topology, change semantics, and grain", "schema filename inference"),
    ("identity_time_units", "Identity, time, and units", "Namespaces, lifecycles, time axes, dimensions, conversions, and error", "provider clock behavior"),
    ("representation_ir", "Representation IR", "Carrier, encoding, framing, layout, container, codec, protection, and loss", "semantic type ownership"),
    ("logical_operations", "Typed logical operations", "Signatures, laws, failures, effects, determinism, and information loss", "algorithms"),
    ("logical_dataflow", "Logical dataflow hypergraph", "Typed ports, state, time, ordering, delivery, cycles, and finite bounds", "deployment topology"),
    ("incremental_semantics", "Incremental computation semantics", "Change algebra, frontiers, monotonicity, retractions, finality, and fixed points", "cache implementation"),
    ("policy_ir", "Policy and assurance IR", "Security, privacy, purpose, residency, retention, disclosure, and precedence", "provider IAM syntax"),
    ("quality_ir", "Quality and reconciliation IR", "Expectation, observation, disposition, correction, and authority", "monitoring product"),
    ("proof_obligations", "Proof-obligation graph", "Claims, assumptions, checkers, certificates, scopes, defeaters, and results", "solver trust by name"),
    ("rewrite_system", "Rewrite equivalence", "Pattern, replacement, theory, side conditions, termination, and witness", "cost-based selection"),
    ("optimization", "Semantics-preserving optimization", "Equivalent alternatives, costs, statistics, objectives, and rejected alternatives", "semantic lowering"),
    ("algorithm_binding", "Algorithm binding", "Applicability, pre/postconditions, complexity, guarantee, stopping, and randomness", "kernel binding"),
    ("kernel_binding", "Kernel binding", "Exact types/layouts, ABI, numeric behavior, target needs, effects, and qualification", "provider marketing claims"),
    ("provider_target_binding", "Provider and target binding", "Versioned occurrences, offers, configuration, observed limits, evidence, and expiry", "invented bindings"),
    ("resource_feasibility", "Finite resource feasibility", "Demand vectors, quotas, capacity, budgets, scheduling quality, and refusal", "unbounded execution"),
    ("physical_plan", "Physical plan IR", "Algorithms, kernels, representations, exchanges, state, budgets, and alternatives", "logical meaning"),
    ("deployment_ir", "Deployment IR", "Artifacts, occurrences, placement, secrets intents, leases, health, and ownership", "live credentials"),
    ("operations_ir", "Operations and recovery IR", "Schedules, retry, checkpoint, replay, backfill, migration, cancellation, and SLO", "business semantics"),
    ("effect_intents", "Effect intents and receipts", "Authorized external effects, idempotency, compensation, reconciliation, and receipts", "silent I/O"),
    ("evidence_ir", "Evidence and lineage IR", "Claims, provenance, custody, scope, validity, defeaters, and retractions", "green-check generalization"),
    ("artifact_ir", "Artifact and release IR", "Canonical identities, manifests, signatures, dependencies, compatibility, and release authority", "artifact contents by digest alone"),
    ("pass_management", "Pass contracts", "Inputs, outputs, prerequisites, preservation, invalidation, diagnostics, and determinism", "arbitrary mutation"),
    ("incremental_recompile", "Incremental recompilation", "Stable keys, dependency edges, fingerprints, invalidation, reuse proofs, and cache receipts", "mtime-only correctness"),
    ("version_migration", "Versioning and migrations", "Schema/dialect editions, upcasters, compatibility, historical replay, rollback, and decommission", "silent upgrade"),
    ("extension_boundary", "Plugin and extension boundary", "Namespaced schemas, declared semantics, capabilities, trust, isolation, and rejection", "plugin authority escalation"),
    ("diagnostics", "Typed diagnostics and gaps", "Stable code, severity, source span, phase, subjects, evidence, remediation, and refusal", "free-text-only failure"),
    ("conformance", "Conformance and evaluation", "Positive/negative fixtures, metamorphic laws, differential checks, certificates, and coverage", "self-asserted completeness"),
]


CONTEXTS = [
    {
        "context_id": f"context.ir.{slug}", "edition": EDITION, "status": "candidate",
        "name": name, "owns": owns, "excludes": excludes,
        "inbound_contracts": ["editioned typed records", "source and authority references"],
        "outbound_contracts": ["validated candidate records", "typed gaps on unresolved meaning"],
        "source_refs": ["source.ir.mlir.langref", "source.ir.rust.queries"],
        "gaps": ["Independent bounded-context adjudication remains open."],
    }
    for slug, name, owns, excludes in CONTEXT_ROWS
]


NODE_SURFACES = {
    "syntax_declaration": [
        "CompilationUnit", "ModuleDecl", "ImportDecl", "ExportDecl", "NamespaceDecl", "IntentDecl",
        "OutcomeDecl", "ConstraintDecl", "NonGoalDecl", "AuthorityDecl", "DefaultDecl", "PolicyDecl",
        "AnalyticalCaseDecl", "ObservationNeedDecl", "OperationDecl", "TargetRequirementDecl", "LiteralExpr",
        "ReferenceExpr", "RecordExpr", "ListExpr", "CallExpr", "BinaryConstraintExpr", "SourceSpan", "ExplicitHole",
    ],
    "resolution": [
        "ModuleIdentity", "SymbolIdentity", "EditionRef", "Scope", "Visibility", "ImportBinding",
        "ExportBinding", "OverloadSet", "ResolvedReference", "UnresolvedReference", "AmbiguousReference",
        "DeprecatedReference", "AuthorityBinding", "DefaultBinding", "ResolutionEnvironment",
    ],
    "canonical_reference": [
        "CanonicalIdentity", "CanonicalReferenceAssertion", "EquivalenceAssertion", "NarrowerAssertion",
        "BroaderAssertion", "OverlapAssertion", "DisjointAssertion", "MissingCanonicalConceptAssertion",
        "AssertionEvidence", "AssertionAdjudication",
    ],
    "language_context": [
        "BoundedContext", "OwnedTerm", "HomonymSet", "SynonymCandidate", "PublishedLanguage",
        "ContextImport", "ContextExport", "ContextExclusion", "NeighborRelation", "AclTranslation",
        "SemanticOwner", "AuthorityDelegation", "PrecedenceRule", "Waiver", "MeaningGap",
    ],
    "analytical_design": [
        "AnalyticalCase", "DecisionQuestion", "Actor", "Population", "UnitOfAnalysis", "Grain",
        "TimeHorizon", "InputNeed", "OutputContract", "DecisionAction", "FeedbackLoop", "PracticeRef",
        "MethodRequirement", "StudyDesign", "Estimand", "Assumption", "DiagnosticPlan", "UncertaintyContract",
        "EvaluationPlan", "AcceptanceCriterion", "MethodAlternative", "MethodRejection",
    ],
    "observation_type_shape": [
        "SourceNeed", "SourceAuthority", "SourceOccurrenceRef", "Observation", "MeasurementProcedure",
        "SemanticType", "CarrierType", "ValueDomain", "Missingness", "Censoring", "MeasurementError",
        "Shape", "Field", "Key", "Cardinality", "NestedShape", "Ordering", "Topology", "ChangeSemantics",
        "IdentityNamespace", "IdentityLifecycle", "EventTime", "ValidTime", "RecordingTime", "IngestionTime",
        "ProcessingTime", "UnitDimension", "UnitConversion", "ProvenanceRef", "QualityRequirement",
        "RepresentationStack", "EncodingLayer", "FramingLayer", "LayoutLayer", "ContainerLayer", "CodecLayer",
        "ProtectionEnvelope", "LossContract",
    ],
    "logical_operation_dataflow": [
        "LogicalPlan", "Operation", "InputPort", "OutputPort", "Parameter", "Precondition", "Postcondition",
        "AlgebraicLaw", "FailureContract", "EffectContract", "DeterminismContract", "IdempotencyContract",
        "InformationLoss", "ResourceEstimate", "DataflowNode", "DataflowEdge", "Hyperedge", "StateContract",
        "WindowContract", "WatermarkContract", "TriggerContract", "OrderingContract", "DeliveryContract",
        "CheckpointContract", "ResumeContract", "RetryContract", "ReplayContract", "BackfillContract",
        "CancellationContract", "FixedPoint", "ChangeAlgebra", "Retraction", "FinalityFrontier", "FiniteBound",
    ],
    "assurance_policy": [
        "AssurancePlan", "Policy", "PolicyApplicability", "PolicyPrecedence", "PurposeConstraint",
        "ConsentConstraint", "ResidencyConstraint", "RetentionConstraint", "DisclosureConstraint",
        "AccessConstraint", "PrivacyUnit", "PrivacyBudget", "ContributionBound", "QualityRule",
        "ReconciliationRule", "HumanApproval", "Override", "WaiverApproval", "ProofObligation",
        "ProofAssumption", "ProofResult", "ProofCertificate", "OracleBinding", "Defeater",
    ],
    "physical_binding": [
        "PhysicalPlan", "CapabilityRequirement", "CapabilityOffer", "CapabilityBinding", "BindingAlternative",
        "RejectedAlternative", "SelectionLaw", "AlgorithmRequirement", "AlgorithmCandidate", "AlgorithmBinding",
        "KernelRequirement", "KernelCandidate", "KernelBinding", "RepresentationRequirement",
        "RepresentationBinding", "LibraryContribution", "ProviderCapabilityClass", "ProviderOccurrence",
        "ProviderOffer", "TargetProfile", "TargetOccurrence", "TargetBinding", "AbiContract", "NumericPosture",
        "ApproximationContract", "RandomnessContract", "StoppingLaw", "ComplexityBound", "MemoryBound",
        "ResourceDemand", "ResourceOffer", "ResourceBinding", "Budget", "CostModel", "ConfigurationDecision",
        "QualificationEvidence", "PhysicalExchange", "PhysicalState", "PhysicalFallback",
    ],
    "deployment_operations": [
        "DeploymentPlan", "ArtifactRef", "EntryPoint", "OccurrenceSpec", "PlacementConstraint", "Schedule",
        "Job", "AttemptPolicy", "Lease", "Fence", "SecretIntent", "HealthCheck", "Slo", "Alert",
        "Runbook", "OwnerAssignment", "RecoveryPlan", "MigrationPlan", "RollbackPlan", "DecommissionPlan",
        "EffectIntent", "IdempotencyKeyContract", "CompensationPlan", "ReconciliationPlan",
    ],
    "evidence_release": [
        "EvidenceBundle", "Claim", "Evidence", "EvidenceScope", "CustodyRecord", "LineageGraph",
        "ProspectiveLineage", "RetrospectiveLineage", "DecisionTrace", "PassReceipt", "BindingReceipt",
        "InvocationReceipt", "EffectReceipt", "ResourceReceipt", "QualityReceipt", "AcceptanceResult",
        "ArtifactManifest", "DependencyLock", "BuildProvenance", "ReleaseCandidate", "ReleaseApproval",
        "ReleaseSignature", "ResidualGap", "RetractionNotice", "RecallNotice",
    ],
}


STAGE_BY_LAYER = {
    "syntax_declaration": "ir.declaration", "resolution": "ir.declaration",
    "canonical_reference": "ir.language", "language_context": "ir.language",
    "analytical_design": "ir.analytical_design", "observation_type_shape": "ir.observation",
    "logical_operation_dataflow": "ir.logical_operations", "assurance_policy": "ir.assurance",
    "physical_binding": "ir.physical", "deployment_operations": "ir.operations",
    "evidence_release": "ir.evidence_release",
}


SOURCES_BY_LAYER = {
    "syntax_declaration": ["source.ir.mlir.langref", "source.ir.starlark.spec"],
    "resolution": ["source.ir.mlir.symbols", "source.ir.rust.hir"],
    "canonical_reference": ["source.ir.souffle.provenance", "source.ir.smtlib.27"],
    "language_context": ["source.ir.cue.spec", "source.ir.dhall.standard"],
    "analytical_design": ["source.ir.substrait.spec", "source.ir.smtlib.27"],
    "observation_type_shape": ["source.ir.substrait.types", "source.ir.beam.model"],
    "logical_operation_dataflow": ["source.ir.substrait.relations", "source.ir.beam.protocol", "source.ir.flink.tables"],
    "assurance_policy": ["source.ir.smtlib.27", "source.ir.cvc5.proofs", "source.ir.souffle.provenance"],
    "physical_binding": ["source.ir.mlir.conversion", "source.ir.llvm.langref", "source.ir.wasm.canonicalabi"],
    "deployment_operations": ["source.ir.flink.state", "source.ir.wasi.preview2", "source.ir.nix.derivations"],
    "evidence_release": ["source.ir.slsa.12", "source.ir.intoto.spec", "source.ir.rfc8785"],
}


NODE_FIELD_CONTRACTS = {
    "syntax_declaration": ["stable_id", "source_span", "edition", "explicit_children", "source_digest"],
    "resolution": ["reference", "scope", "candidate_set", "selected_identity", "edition", "resolution_evidence"],
    "canonical_reference": ["source_identity", "target_identity", "relation", "scope", "authority", "evidence", "validity"],
    "language_context": ["owner_context", "meaning", "imports", "exports", "exclusions", "authority", "translations"],
    "analytical_design": ["question", "population", "unit", "grain", "time", "assumptions", "uncertainty", "evaluation", "action"],
    "observation_type_shape": ["semantic_owner", "type", "shape", "identity", "time", "unit", "quality", "provenance"],
    "logical_operation_dataflow": ["typed_ports", "laws", "failures", "effects", "state", "time", "loss", "finite_bounds"],
    "assurance_policy": ["subject", "applicability", "authority", "precedence", "obligation", "oracle", "evidence", "defeaters"],
    "physical_binding": ["requirement", "candidate", "preconditions", "guarantees", "configuration", "target", "resources", "evidence"],
    "deployment_operations": ["artifact", "occurrence", "authority", "effect_boundary", "recovery", "slo", "owner", "receipt"],
    "evidence_release": ["claim", "scope", "subject_digest", "producer", "method", "validity", "defeaters", "signature"],
}


IR_NODES = []
for layer, names in NODE_SURFACES.items():
    for name in names:
        slug = "".join(("_" + c.lower()) if c.isupper() else c for c in name).lstrip("_")
        IR_NODES.append({
            "record_kind": "ir_node_candidate", "node_id": f"ir.node.{layer}.{slug}",
            "edition": EDITION, "status": "candidate", "layer": layer, "stage": STAGE_BY_LAYER[layer],
            "name": name, "semantic_role": f"Candidate {name} record in the {layer.replace('_', ' ')} layer.",
            "field_contracts": NODE_FIELD_CONTRACTS[layer],
            "identity_law": "Identity includes namespace, stable local key, and explicit edition; content digest is evidence, not semantic identity.",
            "preservation_law": "Lowering must retain source anchors, authority, assumptions, rejected alternatives, and unresolved gaps.",
            "default_law": "No value is defaulted unless a DefaultBinding names value, authority, applicability, precedence, and evidence.",
            "refusal_conditions": ["unresolved meaning", "missing edition", "ambiguous owner", "implicit authority-bound default"],
            "source_refs": SOURCES_BY_LAYER[layer], "gaps": ["Field algebra and exhaustive variants require independent review."],
        })


EDGE_ROWS = [
    ("contains", "container", "member", "membership and source order remain explicit"),
    ("declares", "declaration", "declared_identity", "declaration span and edition survive resolution"),
    ("imports", "module", "imported_module", "import digest and visibility are retained"),
    ("resolves_to", "reference", "identity", "candidate set and resolution rule are retained"),
    ("asserts_canonical_relation", "assertion", "identities", "relation, scope, authority, and evidence are retained"),
    ("owned_by", "meaning", "semantic_owner", "exactly one in-scope owner or a blocking ambiguity"),
    ("translated_by", "foreign_meaning", "acl_translation", "loss and non-equivalence remain visible"),
    ("specializes", "specific_contract", "general_contract", "strengthening is proved and weakening prohibited"),
    ("requires", "subject", "capability_requirement", "criticality and fallback law remain explicit"),
    ("offers", "candidate", "capability_offer", "offer scope, limits, version, and evidence remain explicit"),
    ("binds", "requirement", "offer", "binding carries compatibility proofs and rejected alternatives"),
    ("realizes", "algorithm", "method_or_operation", "pre/postconditions and guarantee posture imply requirement"),
    ("executes_as", "algorithm_or_operation", "kernel", "exact type/layout/target qualification is required"),
    ("represented_as", "semantic_value", "representation_stack", "all representation layers and losses remain distinct"),
    ("consumes", "operation", "input_port", "type, shape, grain, time, and ordering constraints match"),
    ("produces", "operation", "output_port", "postconditions and information loss are attached"),
    ("flows_to", "output_port", "input_port", "port compatibility and delivery contract are proved"),
    ("depends_on", "dependent", "dependency", "dependency kind and invalidation law are explicit"),
    ("guarded_by", "subject", "policy", "precedence and enforcement point are retained"),
    ("approved_by", "decision_or_effect", "authority", "approval scope and expiry are retained"),
    ("defaults_from", "decision", "default_binding", "authority and provenance are retained"),
    ("optimized_to", "equivalent_plan", "selected_plan", "equivalence witness is separate from cost decision"),
    ("lowered_to", "source_ir", "target_ir", "pass receipt and preservation witness are mandatory"),
    ("invalidates", "change", "derived_record", "affected dependency path is reproducible"),
    ("migrates_to", "old_edition", "new_edition", "upcast witness and historical interpretation survive"),
    ("verified_by", "claim", "oracle", "checker identity, inputs, output, and trust assumptions are retained"),
    ("evidenced_by", "claim", "evidence", "scope and defeaters prevent overgeneralization"),
    ("emits", "activity", "receipt", "receipt links inputs, configuration, outcome, and time"),
    ("rejects", "decision", "alternative", "reason and evidence remain first-class"),
    ("supersedes", "new_record", "old_record", "compatibility and invalidation are explicit"),
    ("packages", "release", "artifact", "packaging never transfers semantic ownership"),
    ("retracts", "retraction", "evidence_or_release", "consumers and historical state remain traceable"),
]


IR_EDGES = [
    {
        "record_kind": "ir_edge_candidate", "edge_id": f"ir.edge.{slug}", "edition": EDITION,
        "status": "candidate", "name": slug, "source_role": source_role, "target_role": target_role,
        "cardinality": "typed_by_endpoint_contract", "preservation_law": law,
        "cycle_law": "Cycles are forbidden unless the owning context declares a monotone/fixed-point or recovery-cycle semantics.",
        "source_refs": ["source.ir.mlir.langref", "source.ir.souffle.language"],
    }
    for slug, source_role, target_role, law in EDGE_ROWS
]


PASS_ROWS = [
    ("parse_declarations", "semantic_lowering", "source.text", "ir.declaration", "syntax and source spans"),
    ("build_module_graph", "semantic_lowering", "ir.declaration", "ir.declaration", "module identity and import provenance"),
    ("resolve_editions", "semantic_lowering", "ir.declaration", "ir.declaration", "explicit referenced editions"),
    ("resolve_symbols", "semantic_lowering", "ir.declaration", "ir.declaration", "candidate sets and lexical scope"),
    ("adjudicate_canonical_references", "semantic_lowering", "ir.declaration", "ir.language", "asserted relations and contrary evidence"),
    ("construct_context_language", "semantic_lowering", "ir.declaration", "ir.language", "owned meaning and ACL translations"),
    ("resolve_authority", "semantic_lowering", "ir.language", "ir.language", "owner, delegation, precedence, and expiry"),
    ("materialize_defaults", "semantic_lowering", "ir.language", "ir.language", "default authority and provenance"),
    ("close_analytical_case", "semantic_lowering", "ir.language", "ir.analytical_design", "question-to-action case closure"),
    ("select_applicable_methods", "semantic_lowering", "ir.analytical_design", "ir.analytical_design", "method assumptions and rejected alternatives"),
    ("lower_observation_needs", "semantic_lowering", "ir.analytical_design", "ir.observation", "source authority and observation semantics"),
    ("infer_types_shapes", "analysis", "ir.observation", "ir.observation", "explicit constraints without inventing meaning"),
    ("separate_representation_layers", "semantic_lowering", "ir.observation", "ir.observation", "semantic/carrier/encoding/framing/layout/container/codec/protection separation"),
    ("build_logical_hypergraph", "semantic_lowering", "ir.observation", "ir.logical_operations", "typed ports, grains, time, state, and effects"),
    ("derive_incremental_semantics", "semantic_lowering", "ir.logical_operations", "ir.logical_operations", "change algebra, frontiers, retractions, and finality"),
    ("insert_assurance_obligations", "semantic_lowering", "ir.logical_operations", "ir.assurance", "policies, authority, and proof obligations"),
    ("solve_policy_precedence", "analysis", "ir.assurance", "ir.assurance", "all applicable policies and conflict evidence"),
    ("verify_logical_plan", "validation", "ir.assurance", "ir.assurance", "logical meaning and blocking proof results"),
    ("normalize_equivalent_operations", "optimization", "ir.assurance", "ir.assurance", "equivalence witness and original plan"),
    ("push_filters", "optimization", "ir.assurance", "ir.assurance", "three-valued logic, effects, and cardinality"),
    ("prune_fields", "optimization", "ir.assurance", "ir.assurance", "all observable outputs and evidence fields"),
    ("choose_join_order", "optimization", "ir.assurance", "ir.assurance", "join semantics and complete alternative trace"),
    ("bind_algorithms", "physical_binding", "ir.assurance", "ir.physical", "method/operation identity and guarantee requirements"),
    ("bind_representations", "physical_binding", "ir.physical", "ir.physical", "all layers and loss contracts"),
    ("bind_kernels", "physical_binding", "ir.physical", "ir.physical", "exact type/layout/ABI/target qualification"),
    ("bind_provider_targets", "physical_binding", "ir.physical", "ir.physical", "occurrence identity, observed limits, and evidence validity"),
    ("prove_resource_feasibility", "validation", "ir.physical", "ir.physical", "finite demand and budget envelopes"),
    ("lower_deployment", "semantic_lowering", "ir.physical", "ir.operations", "bound artifacts, effects, owners, and recovery semantics"),
    ("plan_migration_recovery", "semantic_lowering", "ir.operations", "ir.operations", "in-flight and historical interpretation"),
    ("emit_artifacts_receipts", "artifact_emission", "ir.operations", "ir.evidence_release", "decision, proof, binding, and lineage closure"),
    ("evaluate_acceptance", "validation", "ir.evidence_release", "ir.evidence_release", "vertical outcomes and negative twins"),
    ("sign_release_candidate", "artifact_emission", "ir.evidence_release", "ir.evidence_release", "artifact set, residual gaps, and release authority"),
]


PASSES = [
    {
        "pass_id": f"pass.ir.{slug}", "edition": EDITION, "status": "candidate", "pass_kind": kind,
        "input_stage": input_stage, "output_stage": output_stage,
        "requires": ["input schema valid", "all prerequisite proof results are pass or explicitly non-blocking"],
        "produces": ["canonical output IR", "pass receipt", "typed diagnostics", "dependency delta"],
        "preserves": [preserves, "source anchors", "authority bindings", "residual gaps", "rejected alternatives"],
        "may_change": ["representation only where declared by the pass kind", "stable content digest"],
        "must_not_change": ["semantic meaning without an authorized semantic-lowering contract", "guarantee posture", "blocking gap status"],
        "determinism_contract": "Same canonical input, registry snapshot, pass edition, options, and finite evidence snapshot produce byte-identical canonical output and receipt.",
        "failure_atomicity": "On failure no output stage is publishable; diagnostic references the unmodified input and any quarantined partial work.",
        "proof_artifacts": ["preservation witness", "pre/postcondition results"],
        "invalidation_outputs": ["changed stable keys", "transitive dependency invalidations"],
        "source_refs": ["source.ir.mlir.passes", "source.ir.llvm.newpm", "source.ir.llvm.remarks"],
    }
    for slug, kind, input_stage, output_stage, preserves in PASS_ROWS
]


INVARIANT_ROWS = [
    ("candidate_only", "Every record in this package remains candidate and makes no completeness claim."),
    ("no_generative_semantics", "LLM, generative, prompt, RAG, and agent-memory concepts cannot influence core semantics or dispatch."),
    ("explicit_edition", "Every semantic or executable reference resolves to an explicit edition."),
    ("stable_identity_not_digest", "A content digest proves bytes, not semantic identity; both are recorded separately."),
    ("one_owner_per_meaning", "Each in-scope meaning has exactly one owner or a blocking ambiguity."),
    ("canonical_relation_evidenced", "Canonical-reference relations carry authority, scope, evidence, validity, and contrary evidence."),
    ("unknown_means_gap", "Unknown or ambiguous meaning becomes a typed blocking gap and is never guessed."),
    ("defaults_authority_bound", "Every applied default names value, authority, applicability, precedence, source, and invalidation triggers."),
    ("case_not_metric", "A metric, KPI, chart, or formula cannot stand in for an analytical case."),
    ("method_not_algorithm", "Analytical method, algorithm, kernel, provider offer, and target occurrence retain separate identities."),
    ("type_layers_separate", "Semantic type, carrier, encoding, framing, layout, container, codec, and protection remain separate."),
    ("grain_safe", "Every operation preserves declared grain or carries an approved grain-change contract."),
    ("time_axes_separate", "Event, valid, recording, ingestion, and processing time are never collapsed implicitly."),
    ("unit_safe", "Unit conversion requires dimension compatibility, exact rule edition, and error/rounding contract."),
    ("loss_authorized", "Information loss is finite, quantified, scoped, authority-approved, and verified."),
    ("ports_typecheck", "Every logical edge typechecks across type, shape, grain, time, ordering, and delivery semantics."),
    ("state_finite_or_refused", "Every stateful operation has finite bounds or compilation refuses."),
    ("effects_explicit", "External work appears only as an authorized effect intent with receipt and reconciliation semantics."),
    ("policy_precedence_total", "Applicable policy precedence is deterministic; unresolved conflicts block compilation."),
    ("proof_scope_exact", "A proof or green check establishes only its exact claim, subject, inputs, edition, and environment."),
    ("optimization_separate", "Optimization may choose only among proved-equivalent plans and cannot perform semantic lowering."),
    ("rewrite_witnessed", "Every rewrite has a theory, side conditions, witness/checker, termination posture, and rejected-match trace."),
    ("binding_structural", "Bindings are selected by typed requirements/offers/evidence, never provider, library, or crate names."),
    ("provider_occurrence_required", "A provider capability class is never treated as a deployed occurrence."),
    ("no_fabricated_binding", "Absent current occurrence-scoped qualification evidence, provider/target binding remains unbound."),
    ("finite_resources", "Latency, memory, storage, network, work, cost, and energy requirements are finite or explicitly refused."),
    ("rejected_alternatives_retained", "Every selection trace records considered, rejected, and unexamined alternatives with reasons."),
    ("incremental_reuse_proved", "Cached output is reused only when stable dependency fingerprints and pass/config editions match."),
    ("historical_interpretation_survives", "Migration preserves the ability to interpret and verify historical IR and receipts."),
    ("extension_namespaced", "Extensions use collision-resistant identities and cannot overwrite core semantics."),
    ("extension_fail_closed", "Unknown required extension semantics block; ignorable annotations are explicitly marked non-semantic."),
    ("artifact_closure", "Published artifacts link exact inputs, registry snapshot, passes, decisions, proofs, builders, and digests."),
    ("release_gap_gate", "No release is approved with an unwaived blocking gap."),
    ("deterministic_ordering", "Canonical serialization and tie-breaking never depend on hash iteration, filesystem order, locale, or wall clock."),
    ("nondeterminism_typed", "Permitted runtime nondeterminism is explicit and cannot weaken semantic or acceptance guarantees."),
    ("source_anchors_preserved", "Every derived node is traceable to source spans or generated-source anchors."),
]


INVARIANTS = [
    {"invariant_id": f"invariant.ir.{slug}", "edition": EDITION, "status": "candidate", "statement": statement,
     "applies_to": ["all compiler stages"], "failure_effect": "emit typed diagnostic and refuse affected output",
     "source_refs": ["source.ir.mlir.langref", "source.ir.mlir.passes"]}
    for slug, statement in INVARIANT_ROWS
]


DIAGNOSTIC_ROWS = [
    ("E1001", "syntax_invalid", "ir.declaration", "error", "source cannot be parsed without recovery ambiguity"),
    ("E1002", "duplicate_identity", "ir.declaration", "error", "same identity and edition declared more than once"),
    ("E1003", "module_cycle_illegal", "ir.declaration", "error", "import cycle lacks declared fixed-point/module semantics"),
    ("E1101", "symbol_unresolved", "ir.declaration", "error", "reference has no in-scope identity"),
    ("E1102", "symbol_ambiguous", "ir.declaration", "error", "reference has multiple surviving candidates"),
    ("E1103", "edition_unresolved", "ir.declaration", "error", "reference omits or cannot resolve an edition"),
    ("E1201", "canonical_relation_missing", "ir.language", "error", "foreign reference lacks an adjudicated canonical relation"),
    ("E1202", "semantic_owner_ambiguous", "ir.language", "error", "meaning has multiple authoritative owners"),
    ("E1203", "default_authority_missing", "ir.language", "error", "default lacks authority or provenance"),
    ("E1204", "default_conflict", "ir.language", "error", "applicable defaults disagree after precedence"),
    ("E1301", "analytical_case_incomplete", "ir.analytical_design", "error", "question-to-action closure is incomplete"),
    ("E1302", "metric_substitutes_case", "ir.analytical_design", "error", "metric was supplied where an analytical case is required"),
    ("E1303", "method_inapplicable", "ir.analytical_design", "error", "method assumptions or evaluation do not match the case"),
    ("E1401", "source_authority_missing", "ir.observation", "error", "required fact lacks authoritative source and reconciliation"),
    ("E1402", "type_missing", "ir.observation", "error", "observation lacks semantic type"),
    ("E1403", "shape_missing", "ir.observation", "error", "keys, cardinality, nesting, or topology unresolved"),
    ("E1404", "grain_fanout_unapproved", "ir.observation", "error", "join or expansion changes grain without approval"),
    ("E1405", "time_axis_collapsed", "ir.observation", "error", "distinct applicable time axes were collapsed"),
    ("E1406", "unit_conversion_unproved", "ir.observation", "error", "unit conversion lacks exact rule or error contract"),
    ("E1501", "operation_signature_mismatch", "ir.logical_operations", "error", "logical ports do not typecheck"),
    ("E1502", "information_loss_unauthorized", "ir.logical_operations", "error", "loss lacks bound, scope, approval, or oracle"),
    ("E1503", "state_unbounded", "ir.logical_operations", "error", "stateful operation has no finite bound"),
    ("E1601", "policy_conflict", "ir.assurance", "error", "policy precedence cannot select a unique lawful outcome"),
    ("E1602", "proof_inconclusive", "ir.assurance", "error", "blocking obligation has no passing proof result"),
    ("E1701", "rewrite_unproved", "ir.physical", "error", "optimization lacks valid equivalence witness"),
    ("E1702", "offer_incompatible", "ir.physical", "error", "candidate offer violates a blocking requirement"),
    ("E1703", "provider_unqualified", "ir.physical", "error", "provider occurrence evidence is absent, stale, or out of scope"),
    ("E1704", "resource_infeasible", "ir.physical", "error", "no candidate fits finite resource and SLO budgets"),
    ("E1801", "recovery_semantics_incomplete", "ir.operations", "error", "retry/replay/backfill/compensation semantics are incomplete"),
    ("E1901", "release_evidence_incomplete", "ir.evidence_release", "error", "artifact, lineage, proof, or acceptance closure is incomplete"),
    ("W2001", "deprecated_reference", "ir.declaration", "warning", "resolved identity is deprecated and requires explicit migration posture"),
    ("W2002", "optimization_missed", "ir.physical", "warning", "equivalent optimization was considered but rejected"),
]


DIAGNOSTICS = [
    {
        "diagnostic_id": f"diagnostic.ir.{code.lower()}", "code": code, "edition": EDITION,
        "status": "candidate", "diagnostic_kind": kind, "stage": stage, "severity": severity,
        "trigger": trigger, "payload_fields": ["source_spans", "subject_refs", "evidence_refs", "candidate_set", "authority_ref"],
        "compile_effect": "refuse affected stage output" if severity == "error" else "continue with explicit trace",
        "remediation_contract": "Supply or adjudicate the missing typed contract; do not guess or select by name.",
        "source_refs": ["source.ir.mlir.diagnostics", "source.ir.llvm.remarks"],
    }
    for code, kind, stage, severity, trigger in DIAGNOSTIC_ROWS
]


PROOF_ROWS = [
    ("parse_total", "ir.declaration", "AST is total over accepted syntax and every node has a source anchor"),
    ("symbol_unique", "ir.declaration", "every reference resolves to exactly one identity or a typed failure"),
    ("edition_exact", "ir.declaration", "every referenced identity has an explicit compatible edition"),
    ("module_graph_closed", "ir.declaration", "all imports are resolved, digested, and cycle-safe"),
    ("canonical_adjudicated", "ir.language", "foreign identities have evidence-bearing canonical-reference assertions"),
    ("meaning_owner_unique", "ir.language", "every meaning has one owner in scope"),
    ("acl_translation_safe", "ir.language", "context translation declares equivalence or loss"),
    ("default_authorized", "ir.language", "each applied default is authority-bound and provenance-bearing"),
    ("case_closure", "ir.analytical_design", "question, population, grain, time, output, action, and feedback close"),
    ("case_not_metric", "ir.analytical_design", "no metric substitutes for an analytical case"),
    ("method_applicable", "ir.analytical_design", "selected method assumptions and evaluation match the case"),
    ("alternatives_retained", "ir.analytical_design", "method selection retains considered and rejected alternatives"),
    ("source_authoritative", "ir.observation", "each required fact has authority, replicas, and reconciliation"),
    ("type_sound", "ir.observation", "semantic types and explicit casts make all observation expressions type-correct"),
    ("shape_sound", "ir.observation", "keys, cardinalities, nesting, ordering, and topology are compatible"),
    ("grain_safe", "ir.observation", "fanout and aggregation preserve or explicitly change grain"),
    ("identity_safe", "ir.observation", "identity namespace, lifecycle, merge, split, and collisions are explicit"),
    ("time_safe", "ir.observation", "all applicable time axes and clock uncertainties remain distinct"),
    ("unit_safe", "ir.observation", "unit conversions preserve dimensions within declared numeric error"),
    ("representation_complete", "ir.observation", "all representation layers and losses are explicit"),
    ("operation_signature", "ir.logical_operations", "logical operation ports typecheck"),
    ("operation_laws", "ir.logical_operations", "preconditions, postconditions, laws, refusals, and failures are satisfiable"),
    ("loss_authorized", "ir.logical_operations", "all information loss is bounded and authorized"),
    ("incremental_equivalence", "ir.logical_operations", "incremental and batch results agree under declared finality"),
    ("state_bounded", "ir.logical_operations", "all state has finite retention/work bounds"),
    ("policy_precedence", "ir.assurance", "policy application and precedence yield one lawful result"),
    ("authority_complete", "ir.assurance", "approval, waiver, override, write, and effect authority is complete"),
    ("proof_checker_scoped", "ir.assurance", "proof checker, encoding, assumptions, and certificate scope are explicit"),
    ("rewrite_equivalent", "ir.physical", "rewrite preserves denotation under proved side conditions"),
    ("algorithm_realizes", "ir.physical", "algorithm pre/postconditions imply method or operation requirements"),
    ("kernel_qualified", "ir.physical", "kernel matches exact type, layout, ABI, target, numeric, effect, and resource contract"),
    ("provider_occurrence_qualified", "ir.physical", "provider binding uses current occurrence-scoped evidence"),
    ("resource_feasible", "ir.physical", "finite resources satisfy budgets and SLO constraints"),
    ("guarantee_not_strengthened", "ir.physical", "lowering never promotes approximation or nondeterminism to stronger guarantees"),
    ("deployment_effect_safe", "ir.operations", "external effects have authorization, idempotency, receipt, and reconciliation"),
    ("recovery_safe", "ir.operations", "retry, replay, backfill, cancellation, and compensation preserve declared semantics"),
    ("migration_safe", "ir.operations", "in-flight and historical work remains interpretable across migration"),
    ("incremental_cache_sound", "ir.operations", "reused results have matching stable fingerprints and dependency closure"),
    ("lineage_closed", "ir.evidence_release", "outputs link sources, passes, decisions, bindings, proofs, and receipts"),
    ("artifact_reproducible", "ir.evidence_release", "declared inputs and environment reproduce canonical artifacts or explain variance"),
    ("acceptance_vertical", "ir.evidence_release", "positive cases and negative twins meet declared outcomes"),
    ("release_authorized", "ir.evidence_release", "release authority approves exact artifact set and residual gaps"),
]


PROOFS = [
    {
        "proof_id": f"proof.ir.{slug}", "edition": EDITION, "status": "candidate", "stage": stage,
        "claim": claim, "assumption_contract": ["exact input digests", "registry snapshot", "pass and proof editions"],
        "acceptable_witnesses": ["structural checker receipt", "independently checkable SAT/SMT certificate", "bounded model counterexample absence", "metamorphic oracle receipt"],
        "unacceptable_witnesses": ["solver or vendor name", "unscoped green check", "unsigned prose claim"],
        "result_lattice": ["pass", "fail", "inconclusive", "not_applicable"],
        "failure_diagnostic": "diagnostic.ir.e1602", "source_refs": ["source.ir.smtlib.27", "source.ir.cvc5.proofs", "source.ir.drat.trim"],
    }
    for slug, stage, claim in PROOF_ROWS
]


REWRITE_ROWS = [
    ("filter_conjunction_commute", "filter(p and q, x)", "filter(q and p, x)", "two-valued/three-valued predicate conjunction commutativity", "p and q are pure and share the same error domain"),
    ("filter_fusion", "filter(p, filter(q, x))", "filter(p and q, x)", "selection fusion", "p and q are pure; error and short-circuit observability is declared equivalent"),
    ("projection_prune", "project(all, x)", "project(required, x)", "relational projection", "removed fields are unobserved by result, policies, quality, lineage, and receipts"),
    ("inner_join_commute", "join_inner(a,b,p)", "join_inner(b,a,swap(p))", "bag relational algebra", "output field order is explicitly permuted and effects absent"),
    ("join_associate", "join_inner(join_inner(a,b,p),c,q)", "join_inner(a,join_inner(b,c,q2),p2)", "bag relational algebra", "predicates are rewritten exactly; null/error semantics and multiplicities match"),
    ("aggregate_partial", "aggregate(g,f,x)", "finalize(combine(partial(g,f,x)))", "decomposable aggregate monoid", "f exposes identity, associative combine, and numeric reproducibility posture"),
    ("map_fusion", "map(f,map(g,x))", "map(compose(f,g),x)", "pure function composition", "f and g are total or preserve identical failure ordering"),
    ("window_coalesce", "adjacent_windows(x)", "coalesced_window(x)", "window algebra", "trigger, lateness, watermark, and output multiplicity are equivalent"),
    ("incrementalize_sum", "recompute(sum,x_plus_delta)", "sum(x)+sum(delta)", "commutative group", "retractions are signed and overflow/numeric policy matches"),
    ("predicate_push_join", "filter(p,join(a,b))", "join(filter(p,a),b)", "selection pushdown", "p references only a and outer/null semantics are unaffected"),
    ("constant_fold", "op(constant_args)", "constant_result", "operation denotation", "operation is pure, total for inputs, edition-fixed, and target-independent"),
    ("dead_branch", "if true then a else b", "a", "conditional semantics", "condition is literal true and b has no observable effect"),
    ("representation_roundtrip", "decode(encode(x))", "x", "representation inverse law", "codec profile is lossless and canonicalization equivalence is authorized"),
    ("unit_conversion_compose", "convert_b_c(convert_a_b(x))", "convert_a_c(x)", "dimension-preserving conversion", "rounding/error bound of composition satisfies requested bound"),
    ("identity_eliminate", "identity(x)", "x", "identity law", "identity carries no policy, evidence, timing, or receipt observation"),
    ("dedup_idempotent", "dedup(k,dedup(k,x))", "dedup(k,x)", "idempotence", "same key, horizon, ordering, and survivor selection"),
]


REWRITES = [
    {
        "rewrite_id": f"rewrite.ir.{slug}", "edition": EDITION, "status": "candidate",
        "pattern": pattern, "replacement": replacement, "equivalence_theory": theory,
        "side_conditions": [side], "witness_contract": "Emit a normalized proof obligation plus checker/certificate receipt or reject the rewrite.",
        "termination_posture": "Applied by an ordered finite phase; saturation requires explicit node/iteration budgets.",
        "on_unknown": "reject rewrite and retain candidate as missed optimization",
        "source_refs": ["source.ir.egg.paper", "source.ir.egglog.paper", "source.ir.mlir.rewriting"],
    }
    for slug, pattern, replacement, theory, side in REWRITE_ROWS
]


DECISION_TRACE_ROWS = [
    ("symbol_resolution", "Resolve a source reference to one exact identity and edition", "all in-scope symbols", "lexical scope, namespace, visibility, edition compatibility, then stable identity"),
    ("canonical_adjudication", "Adjudicate a foreign-to-canonical relation", "all asserted relation kinds plus missing concept", "authority and evidence strength; never spelling similarity"),
    ("authority_precedence", "Resolve controlling authority", "direct owners, valid delegations, and applicable precedence rules", "declared precedence then stable identity; conflict refuses"),
    ("default_materialization", "Apply an explicit default", "all applicable DefaultBinding records", "precedence then specificity then stable identity; disagreement refuses"),
    ("method_selection", "Select applicable analytical methods", "all registered methods matching the question class", "assumption/evaluation applicability before declared preference"),
    ("rewrite_selection", "Select an equivalent rewrite", "all pattern matches under finite search budget", "proved equivalence before cost; deterministic cost tie-break"),
    ("algorithm_binding", "Bind an algorithm candidate", "all structurally compatible algorithm offers", "guarantee/applicability/resource proof before preference"),
    ("kernel_binding", "Bind a kernel candidate", "all exact type/layout/ABI/target-compatible kernels", "qualification evidence and finite resources before preference"),
    ("provider_target_binding", "Bind provider and target occurrences", "all versioned occurrence offers visible in the fixed registry/evidence snapshot", "policy/evidence/limits/feasibility before declared selection law"),
    ("release_decision", "Approve or refuse a release candidate", "release plus all blocking proof, acceptance, artifact, and gap results", "no unwaived blocking failure; authority signature last"),
]


DECISION_TRACES = [
    {
        "decision_trace_id": f"decisiontrace.ir.{slug}", "edition": EDITION, "status": "candidate",
        "question": question, "enumeration_law": enumeration, "selection_law": selection,
        "required_inputs": ["subject identity and edition", "registry/evidence snapshot digest", "authority and policy snapshot", "compiler/pass editions", "finite search budget"],
        "required_candidate_fields": ["candidate identity", "eligibility result", "elimination reasons", "proof/evidence refs", "score components if applicable", "tie-break key"],
        "required_outcome_fields": ["selected candidate or typed refusal", "all rejected candidates", "unexamined candidates and budget reason", "residual gaps", "invalidation triggers"],
        "retention_law": "Retain the trace with downstream artifacts and migrations; never retain only the winner.",
        "source_refs": ["source.ir.llvm.remarks", "source.ir.mlir.transform", "source.ir.substrait.extensions"],
    }
    for slug, question, enumeration, selection in DECISION_TRACE_ROWS
]


INCREMENTAL_ROWS = [
    ("source_content", "source digest or normalized token stream changes", ["parse", "all source-derived nodes"]),
    ("source_span_only", "comments/formatting change with identical normalized AST", ["source maps", "diagnostic rendering", "evidence anchors"]),
    ("module_export", "exported symbol identity/type/edition changes", ["dependent resolution", "downstream semantic IR"]),
    ("private_symbol", "private declaration changes", ["owning module queries only"]),
    ("registry_snapshot", "referenced registry record digest changes", ["resolution", "bindings", "proofs", "release"]),
    ("authority", "authority, delegation, precedence, or expiry changes", ["defaults", "policies", "effects", "release"]),
    ("default", "default value/applicability/provenance changes", ["all consumers of decision"]),
    ("method", "method assumptions/evaluation edition changes", ["analytical design", "logical plan", "acceptance"]),
    ("semantic_type", "semantic type or operation laws change", ["observation", "logical", "physical", "artifacts"]),
    ("representation", "encoding/layout/codec profile changes", ["physical plan", "kernel qualification", "artifacts"]),
    ("policy", "policy rule or applicability changes", ["assurance", "physical", "deployment", "release"]),
    ("pass_edition", "pass code/edition/options change", ["that pass output", "transitive consumers"]),
    ("proof_checker", "checker or certificate format edition changes", ["proof result", "release evidence"]),
    ("provider_evidence", "offer, occurrence, limit, or qualification evidence changes", ["physical binding", "resource proof", "deployment"]),
    ("target_profile", "ABI/capability/resource profile changes", ["kernel binding", "artifact", "deployment"]),
    ("runtime_observation", "health/rate/quota/cost evidence changes", ["time-bounded deployment binding only"]),
]


INCREMENTAL_RULES = [
    {
        "incremental_rule_id": f"incremental.ir.{slug}", "edition": EDITION, "status": "candidate",
        "change_key": change, "invalidates": invalidates,
        "stable_key_contract": "namespace + semantic identity + edition; never memory address, traversal ordinal, mtime, or random hash seed",
        "fingerprint_contract": "RFC 8785 canonical JSON bytes plus declared external material digests and pass/config editions",
        "reuse_gate": "All direct and transitive dependency fingerprints match and prior proof/receipt validity has not expired.",
        "receipt": "record old/new fingerprints, reused/recomputed keys, invalidation path, pass edition, and decision",
        "source_refs": ["source.ir.rust.incremental", "source.ir.rust.stablehash", "source.ir.bazel.remote"],
    }
    for slug, change, invalidates in INCREMENTAL_ROWS
]


MIGRATION_ROWS = [
    ("schema_add_optional", "old readers ignore explicitly non-semantic optional field", "backward", "no semantic default is introduced"),
    ("schema_add_required", "required field added", "breaking", "provide authored/authority-bound upcaster or refuse"),
    ("enum_add_variant", "closed enum gains variant", "breaking_for_exhaustive_consumers", "capability negotiation and reject-unknown behavior required"),
    ("field_rename", "field identity preserved under renamed spelling", "transform", "explicit identity map and source-anchor migration"),
    ("field_split", "one field becomes multiple meanings", "semantic_transform", "owner-approved mapping; no invented values"),
    ("meaning_change", "same spelling acquires different semantics", "new_identity", "mint new identity; canonical-reference assertion may relate them"),
    ("pass_upgrade", "pass edition changes", "recompile", "invalidate its outputs and transitive proof receipts"),
    ("proof_format_upgrade", "certificate/checker format changes", "reverify", "retain original certificate and checker identity"),
    ("registry_record_upgrade", "open-universe record edition changes", "selective_rebind", "re-resolve only recorded dependents then re-run gates"),
    ("provider_occurrence_upgrade", "deployed provider version/configuration changes", "requalify", "invalidate occurrence-scoped bindings; never inherit class evidence"),
    ("state_upgrade", "runtime state shape/semantics change", "operational_transform", "upcaster, compatibility, checkpoint, rollback/roll-forward, and historical replay required"),
    ("artifact_decommission", "artifact edition retired", "decommission", "consumer inventory, export, retention, revocation, and tombstone receipt required"),
]


MIGRATIONS = [
    {
        "migration_id": f"migration.ir.{slug}", "edition": EDITION, "status": "candidate", "change": change,
        "compatibility": compatibility, "required_action": action,
        "preserves": ["historical interpretation", "source and decision trace", "old and new digests", "authority"],
        "failure_law": "refuse migration; keep old edition readable and emit typed gap",
        "source_refs": ["source.ir.mlir.bytecode", "source.ir.substrait.versioning", "source.ir.spdx.30"],
    }
    for slug, change, compatibility, action in MIGRATION_ROWS
]


EXTENSION_ROWS = [
    ("syntax", "new namespaced declaration forms", "parser extension emits core ExplicitHole when semantics unavailable"),
    ("dialect", "new namespaced IR nodes/types/attributes", "registered schema, verifier, serialization edition, and migration hooks"),
    ("semantic_type", "open semantic type registry", "owner, operations, invalid inferences, and compatibility required"),
    ("operation", "open typed operation registry", "signature, laws, failures, effects, determinism, and evidence required"),
    ("analytical_method", "open method registry", "applicability, assumptions, uncertainty, evaluation, refusals, and evidence required"),
    ("rewrite", "optimization rule pack", "equivalence theory, side conditions, proof adapter, budgets, and termination posture"),
    ("proof_checker", "external certificate checker", "content-addressed executable, sandbox, deterministic I/O, trust declaration, and checker receipt"),
    ("algorithm", "algorithm candidates", "realization proof, guarantees, complexity, randomness, stopping, and failure required"),
    ("kernel", "kernel candidates", "exact types/layouts/ABI/target/resources/effects and qualification receipts required"),
    ("provider_adapter", "provider/target occurrence adapter", "cannot define semantics; declares offers, limits, configuration, evidence, and expiry"),
    ("artifact_emitter", "new output artifact format", "canonical serialization, media type, schema edition, verification, and migration required"),
    ("diagnostic_renderer", "human-oriented rendering", "cannot change code, severity, payload, refusal result, or machine record"),
]


EXTENSIONS = [
    {
        "extension_id": f"extension.ir.{slug}", "edition": EDITION, "status": "candidate",
        "extension_kind": slug, "allowed_surface": surface, "admission_contract": admission,
        "namespace_law": "Reverse-domain or registered collision-resistant namespace; core namespace cannot be claimed.",
        "trust_boundary": "Extension declarations are untrusted data until schema, signature, capability, policy, resource, and conformance gates pass.",
        "semantic_limit": "Extensions may add registered meaning but may not weaken core invariants, auto-approve defaults, or acquire another context's authority.",
        "unknown_handling": "Unknown required semantics block; explicitly non-semantic ignorable annotations may round-trip unchanged.",
        "source_refs": ["source.ir.mlir.interfaces", "source.ir.substrait.extensions", "source.ir.wasm.component"],
    }
    for slug, surface, admission in EXTENSION_ROWS
]


ARTIFACT_ROWS = [
    ("source_snapshot", "artifact", "canonical source units, imports, registry snapshot, and digests"),
    ("declaration_ir", "artifact", "validated declaration AST with source map"),
    ("language_ir", "artifact", "resolved meanings, contexts, authority, defaults, and gaps"),
    ("analytical_design_ir", "artifact", "closed cases, methods, assumptions, alternatives, and evaluation"),
    ("observation_ir", "artifact", "source needs, observation/type/shape/time/unit/representation contracts"),
    ("logical_plan", "artifact", "typed logical operation/dataflow graph"),
    ("assurance_plan", "artifact", "policies, authority, proof obligations, and results"),
    ("physical_plan", "artifact", "algorithms/kernels/representations/provider-target bindings or explicit unbound gaps"),
    ("deployment_plan", "artifact", "occurrences, configuration, effects, recovery, SLOs, and ownership"),
    ("decision_trace", "artifact", "candidate set, eliminations, scores, selected and rejected alternatives"),
    ("dependency_graph", "artifact", "stable-key dependency and invalidation graph"),
    ("release_manifest", "artifact", "complete artifact set, compatibility, gaps, and authorities"),
    ("pass_receipt", "receipt", "pass input/output digests, edition/options, proofs, diagnostics, and invalidations"),
    ("proof_receipt", "receipt", "claim/encoding/checker/certificate/result/scope/trust assumptions"),
    ("binding_receipt", "receipt", "requirement, offers considered, elimination reasons, selected binding, evidence, and validity"),
    ("default_receipt", "receipt", "decision, applied value, authority, source, applicability, precedence, and invalidation"),
    ("migration_receipt", "receipt", "old/new editions and digests, upcaster, verification, rollback, and residual gaps"),
    ("build_provenance", "receipt", "builder, invocation, declared inputs, environment identity, outputs, and timestamps"),
    ("runtime_receipt", "receipt", "attempt, artifact, occurrence, configuration, effects, outcome, resources, and causal parents"),
    ("release_receipt", "receipt", "release candidate, evidence bundle, authority, signature, validity, and revocation endpoints"),
]


ARTIFACTS = [
    {
        "artifact_id": f"artifact.ir.{slug}", "edition": EDITION, "status": "candidate", "artifact_kind": kind,
        "contract": contract, "identity": "semantic identity + edition + canonical content digest + media type",
        "required_envelope": ["schema_id", "producer_id", "producer_edition", "input_refs", "registry_snapshot", "created_at_or_logical_epoch", "digest", "signatures", "validity", "gaps"],
        "canonicalization": "RFC 8785 for JSON records; JSONL order is stable identity lexical order and LF terminated.",
        "verification": ["schema validation", "digest verification", "reference closure", "authority/signature policy", "no unwaived blocking gaps"],
        "source_refs": ["source.ir.rfc8785", "source.ir.slsa.12", "source.ir.intoto.spec"],
    }
    for slug, kind, contract in ARTIFACT_ROWS
]


LIBRARY_ROWS = [
    ("syntax", "semantic_pure", "tokens, AST, source maps", "no symbol or domain resolution"),
    ("identity", "semantic_pure", "stable IDs, editions, canonical refs", "no filesystem/catalog I/O"),
    ("context", "semantic_pure", "bounded contexts, owners, ACL translations", "no provider concepts"),
    ("analytical_design", "semantic_pure", "case/method/applicability contracts", "no algorithm selection"),
    ("types_shapes", "semantic_pure", "semantic types, shapes, grain, time, units", "no layout/kernel selection"),
    ("logical_ir", "semantic_pure", "typed operations and dataflow", "no runtime scheduling"),
    ("policy", "policy_pure", "policy applicability/precedence/obligations", "no IAM or secret effects"),
    ("proof_ir", "semantic_pure", "claims, assumptions, witnesses, results", "no solver execution"),
    ("rewrite", "algorithm_pure", "pattern matching and equivalence obligations", "no cost/provider selection"),
    ("optimizer", "algorithm_pure", "equivalent alternatives, costing interfaces, traces", "no semantic lowering"),
    ("binding", "algorithm_pure", "requirement/offer compatibility and alternatives", "no discovery or live probes"),
    ("incremental", "algorithm_pure", "dependency graph, stable fingerprints, invalidation", "no hidden cache I/O"),
    ("serialization", "semantic_pure", "canonical JSON/JSONL encoding and schema IDs", "no signing keys"),
    ("artifact_store", "runtime_mechanism", "explicit put/get/list effect intents and receipts", "no semantic identity decisions"),
    ("registry_adapter", "provider_adapter", "explicit registry snapshot retrieval and receipts", "no fallback to latest"),
    ("proof_runner", "runtime_mechanism", "sandboxed checker invocation and receipts", "no proof truth by exit code alone"),
    ("target_backend", "target_backend", "lower qualified physical IR to target artifacts", "no target self-qualification"),
    ("release", "runtime_mechanism", "manifest/sign/verify/publish intents and receipts", "no release self-approval"),
]


LIBRARIES = [
    {
        "library_id": f"library.ir.{slug}", "edition": EDITION, "status": "candidate_model",
        "library_kind": kind, "owns": owns, "forbidden_responsibilities": [forbidden],
        "effect_boundary": "pure_no_io" if kind in {"semantic_pure", "policy_pure", "algorithm_pure"} else "explicit_effect_intents_and_receipts",
        "public_boundary": ["editioned model types", "typed Result diagnostics", "deterministic iterators sorted by stable identity"],
        "replacement_seam": "traits describe contract operations; conformance suite qualifies implementations without name dispatch",
        "source_refs": ["source.ir.rust.reference", "source.ir.mlir.interfaces", "source.ir.wasm.component"],
    }
    for slug, kind, owns, forbidden in LIBRARY_ROWS
]


RUST_ROWS = [
    ("StableId", "newtype", "identity", "prevents mixing identities; edition remains separate", "does not make identity globally unique"),
    ("Edition<T>", "generic_newtype", "versioning", "couples value with explicit edition at type boundary", "cannot decide compatibility"),
    ("SourceSpan", "value_type", "diagnostics", "preserves byte/line anchors without storing source meaning", "not semantic identity"),
    ("SymbolRef<Unresolved>", "typestate", "resolution", "prevents unresolved symbols entering closed IR", "dynamic registry absence still yields runtime diagnostic"),
    ("SymbolRef<Resolved>", "typestate", "resolution", "carries exact identity/edition and resolution receipt", "cannot prove owner authority alone"),
    ("Ir<S>", "typestate", "stages", "makes stage transitions explicit and prevents pass order confusion", "does not prove semantic preservation"),
    ("Pass<I,O>", "trait", "passes", "models typed input/output and pass metadata", "trait implementation is not conformance evidence"),
    ("PreservationWitness<I,O>", "sealed_value", "proof_preservation", "binds pass input/output digests to proved claims", "may still trust checker assumptions"),
    ("Diagnostic", "closed_enum_plus_payload", "diagnostics", "stable codes and exhaustive machine handling", "extension codes require namespace envelope"),
    ("Gap", "nonempty_struct", "refusal", "forces missing meaning/capability to remain data", "does not resolve the gap"),
    ("AuthorityRef", "newtype", "authority", "avoids stringly typed principals", "does not authenticate or authorize"),
    ("DefaultBinding<T>", "struct", "defaults", "requires value, authority, provenance, applicability, precedence", "cannot synthesize a safe default"),
    ("NonEmpty<T>", "collection_wrapper", "invariants", "represents proof/candidate/cardinality requirements", "runtime validation still needed at decode"),
    ("BTreeMap<StableId,_>", "standard_collection", "determinism", "stable traversal and serialization order", "semantic order must still be separately modeled"),
    ("IndexMap", "qualified_dependency", "source_order", "retains authored order where it is semantic", "hash configuration must not determine canonical output"),
    ("Result<T, DiagnosticSet>", "sum_type", "failure", "makes refusal explicit and typed", "warnings and partial evidence need separate channel"),
    ("TriState", "closed_enum", "logic", "distinguishes true/false/unknown", "not a replacement for richer null/missing/error semantics"),
    ("ProofResult", "closed_enum", "proofs", "pass/fail/inconclusive/not-applicable are non-collapsible", "pass remains scope-bound"),
    ("Requirement<T>", "generic_struct", "binding", "separates required contract from offers", "cannot dispatch by Rust type name"),
    ("Offer<T>", "generic_struct", "binding", "carries limits, evidence, version, applicability", "does not imply deployed occurrence"),
    ("Binding<T>", "typestate", "binding", "constructible only from checked compatibility receipt", "cannot freeze expiring evidence forever"),
    ("Unbound<T>", "typestate", "binding", "prevents accidental execution before qualification", "requires explicit gap on terminal refusal"),
    ("SemanticType", "enum_or_registry_key", "types", "closed core carriers plus namespaced extension references", "enum alone cannot express open-world semantics"),
    ("ShapeExpr", "recursive_adt", "shapes", "represents nested/relational/graph/stream shape constraints", "recursive depth must be budgeted"),
    ("Operation", "trait_object_or_enum", "logical_ops", "shared typed signature/law inspection", "dynamic dispatch cannot confer semantic trust"),
    ("EffectIntent", "sealed_enum", "effects", "domain libraries describe effects without performing I/O", "adapters remain effectful and fallible"),
    ("Receipt", "signed_struct", "evidence", "binds inputs/config/outcome/producer/digest", "signature does not prove claim truth"),
    ("CanonicalJson", "validated_bytes", "serialization", "prevents hashing noncanonical JSON", "cross-format equivalence needs separate proof"),
    ("Fingerprint", "digest_newtype", "incremental", "avoids accidental raw-string cache keys", "digest collision assumptions remain explicit"),
    ("DepGraph", "typed_graph", "incremental", "edge kinds drive precise invalidation", "cycles need fixed-point semantics"),
    ("PluginManifest", "validated_struct", "extensions", "declares namespace, capabilities, schemas, trust and versions", "manifest is not qualification"),
    ("WasmComponent", "opaque_artifact_ref", "plugins", "possible capability-contained extension ABI", "component label alone does not prove sandbox/isolation"),
    ("Arc<T>", "ownership_mechanism", "concurrency", "shares immutable IR safely", "does not make interior mutability deterministic"),
    ("Send+Sync", "auto_traits", "concurrency", "expresses thread transfer/sharing safety", "does not prove semantic determinism"),
    ("serde", "boundary_dependency", "serialization", "candidate implementation mechanism behind canonical envelope", "default serde JSON is not automatically RFC 8785"),
    ("petgraph_or_custom", "boundary_dependency", "graphs", "candidate internal graph mechanism behind typed façade", "library graph indices are not stable identities"),
]


RUST_MAPPINGS = [
    {
        "mapping_id": f"rust.ir.{slugify(slug)}",
        "edition": EDITION, "status": "candidate_model_not_application", "rust_construct": slug,
        "construct_kind": kind, "applies_to": applies, "benefit": benefit, "limit": limit,
        "library_posture": "Expose model-owned types/traits; keep serialization, solver, runtime, provider, FFI, and target dependencies behind adapters.",
        "unsafe_policy": "No unsafe code in semantic model; any FFI/unsafe target backend is isolated, qualified, and receipt-producing.",
        "source_refs": ["source.ir.rust.reference", "source.ir.rust.mir", "source.ir.salsa.book"],
    }
    for slug, kind, applies, benefit, limit in RUST_ROWS
]


INNOVATION_ROWS = [
    ("equality_saturation_egg", 2021, "Reusable e-graphs with explanation-capable equality saturation for bounded rewrite search", "source.ir.egg.paper"),
    ("mlir_dynamic_dialects", 2026, "Current extensible dialect definitions and interfaces decouple IR consumers from concrete operation classes", "source.ir.mlir.dialects"),
    ("alethe_exchange", 2022, "A solver-neutral proof format direction for independently checking SMT reasoning", "source.ir.alethe.spec"),
    ("substrait_portable_relational_ir", 2026, "Current portable, extension-aware relational plan interchange has strict types and explicit casts", "source.ir.substrait.spec"),
    ("cvc5_flexible_proofs", 2026, "Current cvc5 proof production supports scoped internal checking and external proof formats", "source.ir.cvc5.proofs"),
    ("wasm_component_interfaces", 2026, "Current typed components, worlds, and canonical ABI provide a language-neutral extension boundary", "source.ir.wasm.component"),
    ("json_schema_2020_vocabularies", 2022, "Composable JSON Schema vocabularies and dynamic references for editioned record contracts", "source.ir.jsonschema.2020"),
    ("nix_content_addressed_store_model", 2026, "Current content-addressed build/store object modeling supports reproducible artifact graphs", "source.ir.nix.store"),
    ("dbsp_incremental_algebra", 2023, "Algebraic automatic incrementalization for rich relational computations", "source.ir.dbsp.paper"),
    ("egglog", 2023, "Integration of Datalog-style rules and equality saturation with explanations", "source.ir.egglog.paper"),
    ("slsa_v12", 2025, "SLSA 1.2 build provenance separates external parameters, dependencies, builder, and run details", "source.ir.slsa.12"),
    ("mlir_versioned_bytecode", 2026, "Current stable bytecode includes dialect-owned version payloads and upgrade hooks", "source.ir.mlir.bytecode"),
    ("drat_trim_2023", 2023, "Practical independently checkable SAT proof traces with reference checking", "source.ir.drat.trim"),
    ("wasi_preview2", 2024, "Component-model-based portable capability interfaces for effectful host interaction", "source.ir.wasi.preview2"),
    ("spdx_3_model", 2024, "SPDX 3.0 modular artifact/provenance model for interoperable evidence graphs", "source.ir.spdx.30"),
    ("openivm", 2024, "Compiler lowering of SQL into incremental view-maintenance programs", "source.ir.openivm.paper"),
    ("beam_runner_protocol_growth", 2026, "Current URN/capability-based portable pipeline contracts support cross-language runner boundaries", "source.ir.beam.protocol"),
    ("mlir_transform_dialect_maturity", 2026, "Current transform sequences are represented as IR with explicit silenceable/definite failure modes", "source.ir.mlir.transform"),
    ("substrait_extension_namespaces", 2026, "Current owner-qualified extension identities distinguish semantic and optimization enhancement posture", "source.ir.substrait.extensions"),
    ("smtlib_27", 2026, "SMT-LIB 2.7 standard revision supports portable solver inputs/outputs and theory semantics", "source.ir.smtlib.27"),
    ("slsa_12_source_track", 2025, "SLSA 1.2 source provenance and verified-property expansion", "source.ir.slsa.12"),
    ("wasm_component_async_direction", 2026, "Current component-model async/concurrency work clarifies portable effect and resource boundaries", "source.ir.wasm.component"),
    ("mlir_irdl_runtime_definition", 2026, "Current runtime-declarable IR constraints form an extension mechanism with verifier boundaries", "source.ir.mlir.irdl"),
    ("souffle_lazy_provenance", 2026, "Mature explanation interfaces that recover proof trees for derived facts", "source.ir.souffle.provenance"),
]


INNOVATIONS = [
    {
        "innovation_id": f"innovation.ir.{slug}", "edition": EDITION, "status": "candidate",
        "year": year, "non_llm": True, "innovation": innovation, "source_refs": [source_ref],
        "compiler_relevance": "Informs a bounded mechanism or contract; it is not copied as the compiler architecture.",
        "adoption_gate": ["semantic fit", "deterministic behavior", "independent conformance", "finite resource bounds", "license/security review"],
        "limitations": ["Year marks publication/release/maturity evidence, not universal first invention.", "No provider binding follows from inclusion."],
    }
    for slug, year, innovation, source_ref in INNOVATION_ROWS
]


GAP_ROWS = [
    ("grammar_not_adjudicated", "syntax", True, "A normative source grammar and error-recovery policy are not yet adjudicated."),
    ("semantic_algebra_incomplete", "meaning", True, "A full formal denotational semantics for every open-universe record is absent."),
    ("canonical_registry_absent", "canonical_reference", True, "No authoritative global canonical-reference registry snapshot is supplied."),
    ("authority_model_unadjudicated", "authority", True, "Delegation, expiry, and cross-jurisdiction precedence need independent review."),
    ("default_precedence_unproved", "defaults", True, "Default conflict algebra is specified as fail-closed but not formally proved."),
    ("vertical_method_coverage", "analytical_design", True, "Two examples do not establish method coverage across industries."),
    ("type_system_formalization", "types", True, "Kinds, subtyping/coercion, refinements, effects, and extension soundness need formalization."),
    ("shape_solver_limits", "shape", True, "Decidable fragments and finite solver budgets need adjudication."),
    ("three_valued_semantics", "logical", True, "Null/missing/error/censoring semantics require operation-by-operation formalization."),
    ("rewrite_checker", "optimization", True, "No qualified checker exists for the candidate rewrite catalog."),
    ("proof_encoding_trust", "proof", True, "Translation from IR obligations to SAT/SMT may be larger than the checked proof kernel."),
    ("solver_resource_policy", "proof", False, "Timeout/memory/certificate-size budgets require deployment evidence."),
    ("cost_model_calibration", "optimization", False, "Provider-neutral estimates are not calibrated to live occurrences."),
    ("provider_bindings_absent", "physical", True, "No provider or target occurrence bindings are asserted in this corpus."),
    ("kernel_qualifications_absent", "physical", True, "No exact kernel/type/layout/target qualification receipts are supplied."),
    ("runtime_adapter_abi", "deployment", True, "A concrete effect/runtime ABI is outside this specification."),
    ("migration_checker_absent", "migration", True, "Historical replay and upcaster verification lack an independent checker."),
    ("plugin_isolation_unproved", "extensions", True, "Wasm/native/process isolation claims require target-specific qualification."),
    ("reproducibility_cross_target", "artifacts", False, "Cross-target bitwise reproducibility cannot be promised generically."),
    ("independent_review", "governance", True, "The candidate corpus has not received independent domain, compiler, security, or formal-methods review."),
]


GAPS = [
    {
        "gap_id": f"gap.ir.{slug}", "edition": EDITION, "status": "open_candidate", "gap_kind": kind,
        "blocking": blocking, "statement": statement, "owner_ref": "authority.ir.research_program",
        "resolution_condition": "Supply an adjudicated contract and scoped evidence, update the corpus, and rerun conformance/independent review.",
        "prohibited_fallbacks": ["guess from spelling", "select by provider/library name", "silently apply implementation default", "downgrade proof obligation"],
    }
    for slug, kind, blocking, statement in GAP_ROWS
]


TRACES = [
    {
        "trace_id": "trace.ir.microgrid_forecast.positive", "edition": EDITION, "status": "candidate",
        "case": "Day-ahead net-load forecast to support a human-authorized microgrid battery schedule",
        "vertical": "energy_operations", "expected_result": "lowered_to_unbound_physical_requirements",
        "source_intent": {
            "question": "What distribution of 15-minute net load is expected for the next local operating day?",
            "decision": "Operator reviews a separately optimized charge/discharge schedule.",
            "non_goal": "The forecast does not directly actuate the battery.",
        },
        "steps": [
            {"ordinal": 0, "pass_ref": "pass.ir.parse_declarations", "input": ["intent, horizon, decision, non-goal"], "output": ["IntentDecl", "TimeHorizon", "NonGoalDecl"], "preserved": ["human action boundary", "source spans"], "decision": "no default"},
            {"ordinal": 1, "pass_ref": "pass.ir.construct_context_language", "input": ["site net load, operating day"], "output": ["owned terms with energy-site and grid-calendar contexts"], "preserved": ["local-calendar authority"], "decision": "ACL translation required"},
            {"ordinal": 2, "pass_ref": "pass.ir.close_analytical_case", "input": ["forecast question"], "output": ["population=site intervals; grain=site×15-minute; horizon=next local day; probabilistic output; rolling-origin evaluation"], "preserved": ["decision and forecast uncertainty"], "decision": "forecast method requirement"},
            {"ordinal": 3, "pass_ref": "pass.ir.lower_observation_needs", "input": ["meter, weather, calendar needs"], "output": ["authority-bound interval energy observations, forecast issue time, valid time, unit dimensions, missingness"], "preserved": ["clock and unit uncertainty"], "decision": "no source occurrence selected"},
            {"ordinal": 4, "pass_ref": "pass.ir.build_logical_hypergraph", "input": ["typed observations"], "output": ["resample→quality gate→feature time-align→forecast distribution→rolling evaluation"], "preserved": ["15-minute grain", "information cutoff", "uncertainty"], "decision": "state bounded by explicit history window"},
            {"ordinal": 5, "pass_ref": "pass.ir.insert_assurance_obligations", "input": ["logical plan"], "output": ["no-future-information, unit safety, missingness, coverage, and human-approval obligations"], "preserved": ["non-actuation guarantee"], "decision": "blocking proof gates"},
            {"ordinal": 6, "pass_ref": "pass.ir.bind_algorithms", "input": ["method requirement"], "output": ["algorithm requirements with finite training/inference budgets and rejected alternatives"], "preserved": ["forecast semantics"], "decision": "no concrete algorithm selected without applicability evidence"},
            {"ordinal": 7, "pass_ref": "pass.ir.bind_provider_targets", "input": ["kernel/target/provider requirements"], "output": ["unbound physical requirements", "gap.ir.provider_bindings_absent"], "preserved": ["no fabricated provider binding"], "decision": "refuse deployment"},
        ],
        "rejected_alternatives": [
            {"alternative": "point forecast only", "reason": "fails required uncertainty contract"},
            {"alternative": "use latest weather observation beyond forecast issue time", "reason": "future-information leakage"},
            {"alternative": "automatic actuation", "reason": "contradicts declared human authority boundary"},
        ],
        "terminal_gaps": ["gap.ir.provider_bindings_absent", "gap.ir.kernel_qualifications_absent"],
        "source_refs": ["source.ir.beam.model", "source.ir.flink.tables", "source.ir.substrait.types"],
    },
    {
        "trace_id": "trace.ir.vaccine_safety.positive", "edition": EDITION, "status": "candidate",
        "case": "Observed adverse-event incidence by vaccine lot for epidemiologist review",
        "vertical": "public_health_surveillance", "expected_result": "lowered_to_unbound_physical_requirements",
        "source_intent": {
            "question": "What is the observed incidence rate and uncertainty by lot within an authority-defined risk window?",
            "decision": "Epidemiologist decides whether investigation is warranted.",
            "non_goal": "The result is not a causal safety claim and does not recall a lot automatically.",
        },
        "steps": [
            {"ordinal": 0, "pass_ref": "pass.ir.parse_declarations", "input": ["population, outcome, window, decision, non-goals"], "output": ["AnalyticalCaseDecl", "AuthorityDecl"], "preserved": ["observational/non-causal posture"], "decision": "no default"},
            {"ordinal": 1, "pass_ref": "pass.ir.adjudicate_canonical_references", "input": ["local event and lot vocabularies"], "output": ["scoped canonical-reference assertions"], "preserved": ["broader/narrower relations and evidence"], "decision": "spelling not used as equivalence"},
            {"ordinal": 2, "pass_ref": "pass.ir.close_analytical_case", "input": ["surveillance question"], "output": ["population, person-time unit, lot×risk-window grain, censoring, uncertainty, investigation action"], "preserved": ["not-causal claim", "human decision"], "decision": "descriptive incidence method requirement"},
            {"ordinal": 3, "pass_ref": "pass.ir.lower_observation_needs", "input": ["administration, lot, outcome, enrollment observations"], "output": ["authority, identity linkage, valid/event/recording time, censoring, provenance, privacy unit"], "preserved": ["identity uncertainty and late correction"], "decision": "no deployed source selected"},
            {"ordinal": 4, "pass_ref": "pass.ir.build_logical_hypergraph", "input": ["typed observations"], "output": ["authorized linkage→risk-window intervalization→person-time aggregation→incidence+interval→suppression"], "preserved": ["lot grain", "censoring", "late-data corrections"], "decision": "no causal estimator introduced"},
            {"ordinal": 5, "pass_ref": "pass.ir.insert_assurance_obligations", "input": ["logical plan"], "output": ["purpose, minimum-cell, access, retention, lineage, and correction obligations"], "preserved": ["privacy unit and investigation authority"], "decision": "release blocked until policy values are bound"},
            {"ordinal": 6, "pass_ref": "pass.ir.bind_algorithms", "input": ["exact rate/interval operation requirements"], "output": ["algorithm and numeric requirements; unselected candidates"], "preserved": ["coverage and empty-stratum semantics"], "decision": "provider-neutral requirement only"},
            {"ordinal": 7, "pass_ref": "pass.ir.bind_provider_targets", "input": ["binding requirements"], "output": ["unbound physical requirements", "gap.ir.provider_bindings_absent"], "preserved": ["no fabricated provider binding"], "decision": "refuse deployment"},
        ],
        "rejected_alternatives": [
            {"alternative": "raw event count by lot", "reason": "omits exposed population/person-time denominator"},
            {"alternative": "causal risk statement", "reason": "observational design lacks identification assumptions"},
            {"alternative": "unsuppressed small cells", "reason": "policy value and disclosure authority are unresolved"},
        ],
        "terminal_gaps": ["gap.ir.provider_bindings_absent", "gap.ir.kernel_qualifications_absent"],
        "source_refs": ["source.ir.substrait.relations", "source.ir.souffle.provenance", "source.ir.smtlib.27"],
    },
    {
        "trace_id": "trace.ir.microgrid_forecast.negative", "edition": EDITION, "status": "candidate",
        "case": "Negative twin: forecast request omits local-day timezone and meter unit authority",
        "vertical": "energy_operations", "expected_result": "refused_at_observation",
        "source_intent": {"question": "Forecast tomorrow's load.", "decision": "unspecified", "non_goal": "unspecified"},
        "steps": [
            {"ordinal": 0, "pass_ref": "pass.ir.close_analytical_case", "input": ["underspecified intent"], "output": ["diagnostic.ir.e1301"], "preserved": ["original text"], "decision": "refuse; tomorrow and action are unresolved"},
            {"ordinal": 1, "pass_ref": "pass.ir.lower_observation_needs", "input": ["meter values without unit/clock authority"], "output": ["diagnostic.ir.e1405", "diagnostic.ir.e1406"], "preserved": ["raw evidence"], "decision": "refuse; do not guess timezone or kW/kWh"},
        ],
        "rejected_alternatives": [
            {"alternative": "host timezone", "reason": "implicit environment default lacks authority"},
            {"alternative": "infer unit from column name", "reason": "spelling is not evidence"},
        ],
        "terminal_gaps": ["gap.ir.authority_model_unadjudicated", "gap.ir.type_system_formalization"],
        "source_refs": ["source.ir.cue.spec", "source.ir.substrait.types"],
    },
    {
        "trace_id": "trace.ir.vaccine_safety.negative", "edition": EDITION, "status": "candidate",
        "case": "Negative twin: a dashboard metric requests lot ranking without case, linkage authority, or disclosure policy",
        "vertical": "public_health_surveillance", "expected_result": "refused_at_analytical_design",
        "source_intent": {"question": "Rank worst lots by adverse-event rate.", "decision": "unspecified", "non_goal": "unspecified"},
        "steps": [
            {"ordinal": 0, "pass_ref": "pass.ir.close_analytical_case", "input": ["metric/ranking request"], "output": ["diagnostic.ir.e1302"], "preserved": ["original metric request"], "decision": "refuse metric substitution"},
            {"ordinal": 1, "pass_ref": "pass.ir.lower_observation_needs", "input": ["unowned cross-source identity linkage"], "output": ["diagnostic.ir.e1401"], "preserved": ["unresolved identities"], "decision": "refuse unauthorized linkage"},
            {"ordinal": 2, "pass_ref": "pass.ir.solve_policy_precedence", "input": ["missing disclosure/minimum-cell policies"], "output": ["diagnostic.ir.e1601"], "preserved": ["policy gaps"], "decision": "refuse release"},
        ],
        "rejected_alternatives": [
            {"alternative": "assume identical patient identifiers", "reason": "identity authority and reconciliation absent"},
            {"alternative": "provider default small-cell threshold", "reason": "provider cannot own disclosure policy"},
        ],
        "terminal_gaps": ["gap.ir.canonical_registry_absent", "gap.ir.authority_model_unadjudicated"],
        "source_refs": ["source.ir.souffle.provenance", "source.ir.cvc5.proofs"],
    },
]


SCHEMA_COMMON_DEFS = {
    "id": {"type": "string", "pattern": "^[a-z][a-z0-9]*(\\.[a-z0-9_:-]+)+$"},
    "refs": {"type": "array", "items": {"$ref": "#/$defs/id"}, "uniqueItems": True},
    "strings": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
}


def object_schema(title: str, required: list[str], properties: dict) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "title": title,
        "type": "object", "additionalProperties": False, "required": required,
        "properties": properties, "$defs": SCHEMA_COMMON_DEFS,
    }


SCHEMAS_CONTENT = {
    "context.schema.json": object_schema("IR bounded context candidate",
        ["context_id", "edition", "status", "name", "owns", "excludes", "inbound_contracts", "outbound_contracts", "source_refs", "gaps"],
        {"context_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer", "minimum": 1}, "status": {"const": "candidate"},
         "name": {"type": "string"}, "owns": {"type": "string"}, "excludes": {"type": "string"},
         "inbound_contracts": {"$ref": "#/$defs/strings"}, "outbound_contracts": {"$ref": "#/$defs/strings"},
         "source_refs": {"$ref": "#/$defs/refs"}, "gaps": {"$ref": "#/$defs/strings"}}),
    "source.schema.json": object_schema("Primary source record",
        ["source_id", "edition", "status", "title", "publisher", "source_kind", "url", "publication_or_live_year", "accessed_at", "supports_topics", "authority_scope", "limitations"],
        {"source_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "reviewed_candidate"},
         "title": {"type": "string"}, "publisher": {"type": "string"}, "source_kind": {"type": "string"}, "url": {"type": "string", "format": "uri"},
         "publication_or_live_year": {"type": "integer", "minimum": 1900}, "accessed_at": {"type": "string", "format": "date"},
         "supports_topics": {"$ref": "#/$defs/strings"}, "authority_scope": {"type": "string"}, "limitations": {"$ref": "#/$defs/strings"}}),
    "ir-node.schema.json": object_schema("IR node candidate",
        ["record_kind", "node_id", "edition", "status", "layer", "stage", "name", "semantic_role", "field_contracts", "identity_law", "preservation_law", "default_law", "refusal_conditions", "source_refs", "gaps"],
        {"record_kind": {"const": "ir_node_candidate"}, "node_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"},
         "layer": {"type": "string"}, "stage": {"type": "string"}, "name": {"type": "string"}, "semantic_role": {"type": "string"},
         "field_contracts": {"$ref": "#/$defs/strings"}, "identity_law": {"type": "string"}, "preservation_law": {"type": "string"},
         "default_law": {"type": "string"}, "refusal_conditions": {"$ref": "#/$defs/strings"}, "source_refs": {"$ref": "#/$defs/refs"}, "gaps": {"$ref": "#/$defs/strings"}}),
    "ir-edge.schema.json": object_schema("IR edge candidate",
        ["record_kind", "edge_id", "edition", "status", "name", "source_role", "target_role", "cardinality", "preservation_law", "cycle_law", "source_refs"],
        {"record_kind": {"const": "ir_edge_candidate"}, "edge_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"},
         "name": {"type": "string"}, "source_role": {"type": "string"}, "target_role": {"type": "string"}, "cardinality": {"type": "string"},
         "preservation_law": {"type": "string"}, "cycle_law": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "pass-contract.schema.json": object_schema("IR pass contract",
        ["pass_id", "edition", "status", "pass_kind", "input_stage", "output_stage", "requires", "produces", "preserves", "may_change", "must_not_change", "determinism_contract", "failure_atomicity", "proof_artifacts", "invalidation_outputs", "source_refs"],
        {"pass_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"},
         "pass_kind": {"enum": ["semantic_lowering", "optimization", "analysis", "validation", "physical_binding", "artifact_emission"]},
         "input_stage": {"type": "string"}, "output_stage": {"type": "string"}, "requires": {"$ref": "#/$defs/strings"},
         "produces": {"$ref": "#/$defs/strings"}, "preserves": {"$ref": "#/$defs/strings"}, "may_change": {"$ref": "#/$defs/strings"},
         "must_not_change": {"$ref": "#/$defs/strings"}, "determinism_contract": {"type": "string"}, "failure_atomicity": {"type": "string"},
         "proof_artifacts": {"$ref": "#/$defs/strings"}, "invalidation_outputs": {"$ref": "#/$defs/strings"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "diagnostic.schema.json": object_schema("Typed compiler diagnostic",
        ["diagnostic_id", "code", "edition", "status", "diagnostic_kind", "stage", "severity", "trigger", "payload_fields", "compile_effect", "remediation_contract", "source_refs"],
        {"diagnostic_id": {"$ref": "#/$defs/id"}, "code": {"type": "string", "pattern": "^[EWI][0-9]{4}$"}, "edition": {"type": "integer"}, "status": {"const": "candidate"},
         "diagnostic_kind": {"type": "string"}, "stage": {"type": "string"}, "severity": {"enum": ["error", "warning", "info"]},
         "trigger": {"type": "string"}, "payload_fields": {"$ref": "#/$defs/strings"}, "compile_effect": {"type": "string"},
         "remediation_contract": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "proof.schema.json": object_schema("Proof obligation candidate",
        ["proof_id", "edition", "status", "stage", "claim", "assumption_contract", "acceptable_witnesses", "unacceptable_witnesses", "result_lattice", "failure_diagnostic", "source_refs"],
        {"proof_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "stage": {"type": "string"},
         "claim": {"type": "string"}, "assumption_contract": {"$ref": "#/$defs/strings"}, "acceptable_witnesses": {"$ref": "#/$defs/strings"},
         "unacceptable_witnesses": {"$ref": "#/$defs/strings"}, "result_lattice": {"$ref": "#/$defs/strings"},
         "failure_diagnostic": {"$ref": "#/$defs/id"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "artifact-receipt.schema.json": object_schema("Artifact or receipt candidate",
        ["artifact_id", "edition", "status", "artifact_kind", "contract", "identity", "required_envelope", "canonicalization", "verification", "source_refs"],
        {"artifact_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "artifact_kind": {"enum": ["artifact", "receipt"]},
         "contract": {"type": "string"}, "identity": {"type": "string"}, "required_envelope": {"$ref": "#/$defs/strings"},
         "canonicalization": {"type": "string"}, "verification": {"$ref": "#/$defs/strings"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "lowering-trace.schema.json": object_schema("Miniature lowering trace",
        ["trace_id", "edition", "status", "case", "vertical", "expected_result", "source_intent", "steps", "rejected_alternatives", "terminal_gaps", "source_refs"],
        {"trace_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "case": {"type": "string"},
         "vertical": {"type": "string"}, "expected_result": {"type": "string"}, "source_intent": {"type": "object"},
         "steps": {"type": "array", "minItems": 1, "items": {"type": "object"}}, "rejected_alternatives": {"type": "array", "items": {"type": "object"}},
         "terminal_gaps": {"$ref": "#/$defs/refs"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "invariant.schema.json": object_schema("Compiler invariant candidate",
        ["invariant_id", "edition", "status", "statement", "applies_to", "failure_effect", "source_refs"],
        {"invariant_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"},
         "statement": {"type": "string"}, "applies_to": {"$ref": "#/$defs/strings"}, "failure_effect": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "rewrite-equivalence.schema.json": object_schema("Rewrite equivalence candidate",
        ["rewrite_id", "edition", "status", "pattern", "replacement", "equivalence_theory", "side_conditions", "witness_contract", "termination_posture", "on_unknown", "source_refs"],
        {"rewrite_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "pattern": {"type": "string"},
         "replacement": {"type": "string"}, "equivalence_theory": {"type": "string"}, "side_conditions": {"$ref": "#/$defs/strings"},
         "witness_contract": {"type": "string"}, "termination_posture": {"type": "string"}, "on_unknown": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "decision-trace.schema.json": object_schema("Decision trace contract candidate",
        ["decision_trace_id", "edition", "status", "question", "enumeration_law", "selection_law", "required_inputs", "required_candidate_fields", "required_outcome_fields", "retention_law", "source_refs"],
        {"decision_trace_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "question": {"type": "string"},
         "enumeration_law": {"type": "string"}, "selection_law": {"type": "string"}, "required_inputs": {"$ref": "#/$defs/strings"},
         "required_candidate_fields": {"$ref": "#/$defs/strings"}, "required_outcome_fields": {"$ref": "#/$defs/strings"},
         "retention_law": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "incremental-rule.schema.json": object_schema("Incremental recompilation rule",
        ["incremental_rule_id", "edition", "status", "change_key", "invalidates", "stable_key_contract", "fingerprint_contract", "reuse_gate", "receipt", "source_refs"],
        {"incremental_rule_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "change_key": {"type": "string"},
         "invalidates": {"$ref": "#/$defs/strings"}, "stable_key_contract": {"type": "string"}, "fingerprint_contract": {"type": "string"},
         "reuse_gate": {"type": "string"}, "receipt": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "migration.schema.json": object_schema("IR/version migration candidate",
        ["migration_id", "edition", "status", "change", "compatibility", "required_action", "preserves", "failure_law", "source_refs"],
        {"migration_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "change": {"type": "string"},
         "compatibility": {"type": "string"}, "required_action": {"type": "string"}, "preserves": {"$ref": "#/$defs/strings"},
         "failure_law": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "extension-boundary.schema.json": object_schema("Plugin/extension boundary candidate",
        ["extension_id", "edition", "status", "extension_kind", "allowed_surface", "admission_contract", "namespace_law", "trust_boundary", "semantic_limit", "unknown_handling", "source_refs"],
        {"extension_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "extension_kind": {"type": "string"},
         "allowed_surface": {"type": "string"}, "admission_contract": {"type": "string"}, "namespace_law": {"type": "string"},
         "trust_boundary": {"type": "string"}, "semantic_limit": {"type": "string"}, "unknown_handling": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "library-boundary.schema.json": object_schema("Library boundary candidate",
        ["library_id", "edition", "status", "library_kind", "owns", "forbidden_responsibilities", "effect_boundary", "public_boundary", "replacement_seam", "source_refs"],
        {"library_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate_model"}, "library_kind": {"type": "string"},
         "owns": {"type": "string"}, "forbidden_responsibilities": {"$ref": "#/$defs/strings"}, "effect_boundary": {"type": "string"},
         "public_boundary": {"$ref": "#/$defs/strings"}, "replacement_seam": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "rust-applicability.schema.json": object_schema("Rust type/trait/typestate applicability mapping",
        ["mapping_id", "edition", "status", "rust_construct", "construct_kind", "applies_to", "benefit", "limit", "library_posture", "unsafe_policy", "source_refs"],
        {"mapping_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate_model_not_application"}, "rust_construct": {"type": "string"},
         "construct_kind": {"type": "string"}, "applies_to": {"type": "string"}, "benefit": {"type": "string"}, "limit": {"type": "string"},
         "library_posture": {"type": "string"}, "unsafe_policy": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"}}),
    "innovation.schema.json": object_schema("Non-LLM recent innovation candidate",
        ["innovation_id", "edition", "status", "year", "non_llm", "innovation", "source_refs", "compiler_relevance", "adoption_gate", "limitations"],
        {"innovation_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "year": {"type": "integer", "minimum": 2021, "maximum": 2026},
         "non_llm": {"const": True}, "innovation": {"type": "string"}, "source_refs": {"$ref": "#/$defs/refs"},
         "compiler_relevance": {"type": "string"}, "adoption_gate": {"$ref": "#/$defs/strings"}, "limitations": {"$ref": "#/$defs/strings"}}),
    "gap.schema.json": object_schema("Honest compiler gap",
        ["gap_id", "edition", "status", "gap_kind", "blocking", "statement", "owner_ref", "resolution_condition", "prohibited_fallbacks"],
        {"gap_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "open_candidate"}, "gap_kind": {"type": "string"},
         "blocking": {"type": "boolean"}, "statement": {"type": "string"}, "owner_ref": {"$ref": "#/$defs/id"},
         "resolution_condition": {"type": "string"}, "prohibited_fallbacks": {"$ref": "#/$defs/strings"}}),
    "upstream-alignment.schema.json": object_schema("Upstream compiler/universe alignment",
        ["alignment_id", "edition", "status", "completion_claim", "read_only_inputs", "stage_alignment", "adopted_laws", "proof_posture", "universe_posture", "known_alignment_gaps"],
        {"alignment_id": {"$ref": "#/$defs/id"}, "edition": {"type": "integer"}, "status": {"const": "candidate"}, "completion_claim": {"const": False},
         "read_only_inputs": {"$ref": "#/$defs/strings"}, "stage_alignment": {"type": "array", "minItems": 9, "items": {"type": "object"}},
         "adopted_laws": {"$ref": "#/$defs/strings"}, "proof_posture": {"type": "string"}, "universe_posture": {"type": "string"},
         "known_alignment_gaps": {"$ref": "#/$defs/strings"}}),
}


CONFORMANCE_PLAN = {
    "plan_id": "conformance.ir.intent_to_solution.candidate", "edition": EDITION, "status": "candidate",
    "completion_claim": False,
    "levels": [
        {"level": "schema", "tests": ["all JSON and JSONL parse", "each family validates against its schema subset", "additional properties rejected by published schemas"]},
        {"level": "identity", "tests": ["IDs unique globally where namespaces overlap", "editions positive", "all source/pass/diagnostic/gap refs resolve"]},
        {"level": "determinism", "tests": ["generator rerun byte-identical", "JSONL stable lexical identity order", "canonical digests independent of locale/time/hash seed"]},
        {"level": "semantic", "tests": ["pass pre/postconditions", "meaning/default/authority refusal fixtures", "stage preservation witnesses", "no semantic change in optimization passes"]},
        {"level": "rewrite", "tests": ["positive equivalence fixtures", "side-condition negative twins", "SMT/SAT certificates where decidable", "property/metamorphic tests where not formalized"]},
        {"level": "incremental", "tests": ["clean build equals incremental build", "single-change invalidation fixtures", "cache-poison and expired-evidence negative tests"]},
        {"level": "extensions", "tests": ["unknown required extension rejects", "ignorable annotation round-trips", "namespace collision rejects", "capability/trust/resource budgets enforced"]},
        {"level": "vertical", "tests": ["two unrelated positive lowering traces", "negative twins refuse at declared stage", "no provider binding without occurrence evidence"]},
        {"level": "artifact", "tests": ["digest/reference/signature closure", "SLSA/in-toto mapping tests", "historical migration and retraction replay"]},
        {"level": "review", "tests": ["compiler expert review", "formal methods review", "security/privacy review", "two independent vertical-domain reviews"]},
    ],
    "differential_oracles": ["independent parser", "reference JSON canonicalizer", "two proof checkers when format permits", "batch versus incremental result", "clean versus cached compile"],
    "coverage_metrics": ["records by stage", "diagnostics with negative fixture", "passes with preservation test", "proofs with checker or explicit gap", "extensions with rejection test", "migration paths exercised"],
    "release_gate": "All structural gates pass; all declared blocking proofs pass; no unwaived blocking gap; independent review remains required for non-candidate status.",
}


UPSTREAM_ALIGNMENT = {
    "alignment_id": "alignment.ir.upstream_contracts", "edition": EDITION,
    "status": "candidate", "completion_claim": False,
    "read_only_inputs": [
        "research/domain_atlas/compiler/compiler-metamodel.json",
        "research/domain_atlas/compiler/proof-obligations.json",
        "research/domain_atlas/compiler/decision-point.schema.json",
        "research/domain_atlas/compiler/library-contribution.schema.json",
        "research/domain_atlas/compiler/requirement-offer-binding.schema.json",
        "research/domain_atlas/universes/universe-contract.json",
        "research/domain_atlas/universes/source_systems/compiler-contract.json",
        "research/domain_atlas/universes/runtime_compute_resource/compiler-contract.json",
        "research/domain_atlas/universes/pipeline_dataflow/schemas/delivery-contract.schema.json",
        "research/domain_atlas/universes/pipeline_dataflow/schemas/recovery-contract.schema.json",
        "research/domain_atlas/universes/pipeline_dataflow/schemas/state-contract.schema.json",
        "research/domain_atlas/universes/query_compute_kernels/schema/kernel-contract.schema.json",
    ],
    "stage_alignment": [
        {"upstream_stage": "ir.declaration", "local_layers": ["syntax_declaration", "resolution"]},
        {"upstream_stage": "ir.language", "local_layers": ["canonical_reference", "language_context"]},
        {"upstream_stage": "ir.analytical_design", "local_layers": ["analytical_design"]},
        {"upstream_stage": "ir.observation", "local_layers": ["observation_type_shape"]},
        {"upstream_stage": "ir.logical_operations", "local_layers": ["logical_operation_dataflow"]},
        {"upstream_stage": "ir.assurance", "local_layers": ["assurance_policy"]},
        {"upstream_stage": "ir.physical", "local_layers": ["physical_binding"]},
        {"upstream_stage": "ir.operations", "local_layers": ["deployment_operations"]},
        {"upstream_stage": "ir.evidence_release", "local_layers": ["evidence_release"]},
    ],
    "adopted_laws": [
        "unknown meaning is a typed gap and is never guessed",
        "requirements and offers bind only through exact contracts and evidence",
        "semantic operation, analytical method, algorithm, kernel, provider offer and target remain separate identities",
        "semantic type, carrier, encoding, framing, layout, container, codec and protection envelope remain separate identities",
        "effectful work uses explicit intents and runtime receipts",
        "all finite-resource and evidence scope claims remain exact",
    ],
    "proof_posture": "The upstream proof catalog remains mandatory. Local proof candidates refine pass preservation and do not replace, weaken, or claim discharge of upstream obligations.",
    "universe_posture": "Open-universe records enter only through exact identity/edition/schema/authority/evidence snapshots; missing required surfaces produce typed gaps and never compiler branches keyed by vendor names.",
    "known_alignment_gaps": [
        "No formal refinement mapping has been independently checked.",
        "Universe-specific schemas evolve independently and require edition-aware adapters.",
        "Provider and target occurrence evidence is intentionally absent.",
    ],
}


README = """# Candidate deterministic intent-to-solution IR and lowering universe

This package specifies a research candidate, not a working compiler and not a completeness claim.
It models deterministic compilation from authored intent to evidence-bearing artifacts while refusing
unresolved meaning. LLM, generative, prompt, RAG, and agent-memory semantics are excluded from the
compiler core. Provider and target bindings are deliberately absent unless occurrence-scoped
qualification evidence exists; the miniature traces therefore stop at unbound physical requirements.

```text
source text / imports / registry snapshot
              |
              v
 [declaration AST] --parse/resolution receipts--> [resolved declaration IR]
              |                                         |
              | unresolved symbol/edition               | canonical assertions
              +----------------> typed gap <-------------+
                                                        v
 [language + bounded contexts + authority + explicit defaults]
              |
              v
 [analytical design: case -> method requirements -> rejected alternatives]
              |
              v
 [observation + semantic type + shape + identity/time/unit + representation]
              |
              v
 [typed logical operation/dataflow IR] ----equivalence proof----+
              |                                                  |
              v                                                  v
 [assurance/policy/proof IR]       [optimization-only alternatives + trace]
              |                                                  |
              +---------------------- merge proved meaning ------+
                                         |
                                         v
 [algorithm requirements -> kernel/layout/ABI requirements -> finite resources]
                                         |
                         qualified occurrence evidence? --no--> typed binding gap
                                         | yes
                                         v
 [physical bindings] -> [deployment/operations IR] -> [evidence/release IR]
                                         |
                                         v
 artifacts + pass/proof/binding/runtime/release receipts + retained rejections
```

## Separation laws

- Semantic lowering refines authored meaning between stages. Optimization selects only among
  proved-equivalent forms. A cost argument is never an equivalence proof.
- Method, algorithm, kernel, provider offer, and target occurrence are distinct identities.
- Semantic type, carrier, encoding, framing, layout, container, codec, and protection are distinct.
- Every applied default is a record with authority, applicability, precedence, provenance, and
  invalidation triggers. Missing or conflicting authority-bound values stop compilation.
- Every pass preserves source anchors, authorities, assumptions, rejected alternatives, and gaps.
- A proof/check/receipt is scoped to exact subjects, editions, inputs, checker, and environment.
- Stable identity is not a content digest. Both are carried because they answer different questions.

## Files

`contexts.jsonl` holds bounded-context candidates. `ir-nodes.jsonl` and `ir-edges.jsonl` enumerate
the staged model. Passes, invariants, diagnostics, proofs, rewrites, incremental rules, migrations,
extensions, artifacts/receipts, libraries, and Rust applicability are separate JSONL registries.
`lowering-traces.jsonl` contains two unrelated positive traces and their negative twins.
`sources.jsonl` contains primary/official evidence; `innovations.jsonl` isolates non-LLM 2021-2026
developments. `conformance-plan.json` states evaluation gates. `schemas/` contains machine contracts.
`upstream-alignment.json` records the compiler metamodel, proof catalog, and universe contracts read
as immutable research inputs; the local proof catalog refines but never replaces those obligations.

## Deterministic build and validation

```text
python3 research/domain_atlas/compiler/ir_lowering/build_corpus.py
python3 research/domain_atlas/compiler/ir_lowering/validate_corpus.py
```

The generator sorts every JSONL file by stable identity, emits sorted-key JSON with LF endings, and
uses no clock, network, filesystem enumeration order, random value, locale, or provider discovery.
The validator checks schemas as JSON, record shapes, reference closure, pass separation, candidate
status, forbidden generative terms, trace refusals, thresholds, manifest digests, and a clean
regeneration byte-comparison.

## Honest limits

This is an enumerated candidate universe. It does not supply a normative grammar, formal semantics
for every node, qualified rewrite/proof/migration checker, provider catalog, live provider evidence,
kernel qualification, concrete runtime ABI, or independent review. Those are blocking gaps recorded
in `gaps.jsonl`; they must not be filled by inference.
"""


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    SCHEMAS.mkdir(parents=True, exist_ok=True)

    datasets = {
        "sources.jsonl": SOURCES,
        "contexts.jsonl": CONTEXTS,
        "ir-nodes.jsonl": IR_NODES,
        "ir-edges.jsonl": IR_EDGES,
        "pass-contracts.jsonl": PASSES,
        "invariants.jsonl": INVARIANTS,
        "diagnostics.jsonl": DIAGNOSTICS,
        "proof-obligations.jsonl": PROOFS,
        "rewrite-equivalences.jsonl": REWRITES,
        "decision-trace-contracts.jsonl": DECISION_TRACES,
        "incremental-rules.jsonl": INCREMENTAL_RULES,
        "migrations.jsonl": MIGRATIONS,
        "extension-boundaries.jsonl": EXTENSIONS,
        "artifact-receipt-contracts.jsonl": ARTIFACTS,
        "library-boundaries.jsonl": LIBRARIES,
        "rust-applicability.jsonl": RUST_MAPPINGS,
        "innovations.jsonl": INNOVATIONS,
        "gaps.jsonl": GAPS,
        "lowering-traces.jsonl": TRACES,
    }
    for name, records in datasets.items():
        dump_jsonl(ROOT / name, records)
    for name, schema in SCHEMAS_CONTENT.items():
        dump_json(SCHEMAS / name, schema)
    dump_json(ROOT / "conformance-plan.json", CONFORMANCE_PLAN)
    dump_json(ROOT / "upstream-alignment.json", UPSTREAM_ALIGNMENT)
    (ROOT / "README.md").write_text(README, encoding="utf-8")

    generated_files = sorted(list(datasets) + ["conformance-plan.json", "upstream-alignment.json", "README.md"] + [f"schemas/{name}" for name in SCHEMAS_CONTENT])
    counts = {
        "primary_or_official_sources": len(SOURCES),
        "bounded_context_candidates": len(CONTEXTS),
        "ir_node_candidates": len(IR_NODES),
        "ir_edge_candidates": len(IR_EDGES),
        "pass_candidates": len(PASSES),
        "invariant_candidates": len(INVARIANTS),
        "diagnostic_candidates": len(DIAGNOSTICS),
        "proof_candidates": len(PROOFS),
        "rewrite_equivalence_candidates": len(REWRITES),
        "decision_trace_contracts": len(DECISION_TRACES),
        "incremental_rules": len(INCREMENTAL_RULES),
        "migration_candidates": len(MIGRATIONS),
        "extension_boundaries": len(EXTENSIONS),
        "artifact_receipt_contracts": len(ARTIFACTS),
        "library_boundaries": len(LIBRARIES),
        "rust_type_trait_typestate_mappings": len(RUST_MAPPINGS),
        "innovations_2021_2026": len(INNOVATIONS),
        "honest_gaps": len(GAPS),
        "lowering_traces": len(TRACES),
    }
    counts["ir_node_edge_pass_diagnostic_proof_candidates"] = sum(
        counts[key] for key in ("ir_node_candidates", "ir_edge_candidates", "pass_candidates", "diagnostic_candidates", "proof_candidates")
    )
    manifest = {
        "corpus_id": "san.domain-atlas.compiler.ir-lowering", "edition": EDITION,
        "status": "candidate_research_specification", "completion_claim": False, "as_of": AS_OF,
        "scope": "Deterministic provider-neutral intent-to-solution IR, pass, proof, lowering, artifact, and receipt contracts; no compiler implementation.",
        "forbidden_core_dependencies": ["llm", "large_language_model", "generative_model", "prompt", "rag", "agent_memory"],
        "counts": counts,
        "generated_files": generated_files,
        "file_digests": {name: digest_file(ROOT / name) for name in generated_files},
    }
    dump_json(ROOT / "manifest.json", manifest)
    print(json.dumps(counts, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
