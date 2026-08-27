#!/usr/bin/env python3
"""Build the exact transformation-definition, selection, materialization and evidence corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for row in rows) + "\n"


def S(ident: str, title: str, authority: str, url: str, supports: str, limitation: str) -> dict:
    return {
        "source_id": f"source.transform-build.{ident}", "title": title, "authority": authority,
        "url": url, "retrieved": AS_OF, "source_kind": "primary_or_official",
        "supports": supports, "does_not_prove": limitation,
    }


SOURCES = [
    S("dbt.manifest", "Manifest JSON", "dbt Labs", "https://docs.getdbt.com/reference/artifacts/manifest-json", "a complete editioned project resource graph distinct from executed-node compilation output", "A dbt artifact is not a universal transformation language or proof of reproducibility."),
    S("dbt.selection", "Node selection syntax", "dbt Labs", "https://docs.getdbt.com/reference/node-selection/syntax", "ordered selector-method, graph-operator and set-operator evaluation over project resources", "One vendor selection grammar does not define the provider-neutral selection algebra."),
    S("dbt.selection-methods", "Node selector methods", "dbt Labs", "https://docs.getdbt.com/reference/node-selection/methods", "property, state, result, configuration and resource selectors", "Selector convenience defaults are not safe universal compiler defaults."),
    S("dbt.defer-state", "Defer and state selection", "dbt Labs", "https://docs.getdbt.com/reference/node-selection/defer", "separation of logical selection from environment-specific relation resolution", "Deferral does not prove compatible schemas or safe target substitution."),
    S("dbt.incremental", "Incremental models", "dbt Labs", "https://docs.getdbt.com/docs/build/incremental-models", "incremental eligibility, full refresh, unique keys and schema-change posture", "Timestamp filtering and unique keys do not prove complete or equivalent incremental maintenance."),
    S("dbt.incremental-strategy", "Incremental strategies", "dbt Labs", "https://docs.getdbt.com/docs/build/incremental-strategy", "append, merge, delete-insert, overwrite and microbatch strategy variability", "Adapter support matrices do not grant target mutation authority or exactly-once behavior."),
    S("dbt.run-results", "Run results JSON", "dbt Labs", "https://docs.getdbt.com/reference/artifacts/run-results-json", "resource result identity, status, timing, compiled code and adapter response", "A vendor-interpreted success status is not publication, quality or factual acceptance."),
    S("dataform.compilation", "Configure compilations", "Google Cloud", "https://docs.cloud.google.com/dataform/docs/configure-compilation", "source commit/workspace identity, compilation overrides, immutable compilation result and invocation separation", "A retained cloud compilation result is not a complete hermetic build definition."),
    S("dataform.dependencies", "Declare dependencies between actions", "Google Cloud", "https://docs.cloud.google.com/dataform/docs/dependencies", "explicit references, dependencies, assertions and transitive action selection", "Dataform action semantics are not a general dependency or selection standard."),
    S("dataform.tables", "Create tables", "Google Cloud", "https://docs.cloud.google.com/dataform/docs/create-tables", "table, view and incremental actions with full-refresh behavior", "BigQuery-oriented materialization does not prove target-neutral mutation semantics."),
    S("dataform.assertions", "Test data quality", "Google Cloud", "https://docs.cloud.google.com/dataform/docs/assertions", "assertion declarations and execution artifacts as separate resources", "Assertion execution does not make the build system the owner of quality meaning or waiver authority."),
    S("dataform.invocation", "WorkflowInvocations REST resource", "Google Cloud", "https://docs.cloud.google.com/dataform/reference/rest/v1/projects.locations.repositories.workflowInvocations", "an invocation bound to a compilation result with explicit lifecycle states", "A cloud workflow resource does not define portable scheduling or execution semantics."),
    S("sqlmesh.models", "SQLMesh model overview", "SQLMesh", "https://sqlmesh.readthedocs.io/en/stable/concepts/models/overview/", "model identity, dependencies, dialect, kinds, audits, grain and physical properties", "SQLMesh syntax is evidence of decisions, not the canonical language for all engines."),
    S("sqlmesh.plans", "SQLMesh plans", "SQLMesh", "https://sqlmesh.readthedocs.io/en/stable/concepts/plans/", "change classification, affected graph, backfill ranges, restatement and environment plans", "Interactive plan approval does not transfer enterprise publication authority."),
    S("sqlmesh.environments", "SQLMesh environments", "SQLMesh", "https://sqlmesh.readthedocs.io/en/stable/concepts/environments/", "logical environment snapshots and physical table reuse", "Environment naming does not prove target isolation or access authority."),
    S("sqlmesh.model-kinds", "SQLMesh model kinds", "SQLMesh", "https://sqlmesh.readthedocs.io/en/stable/concepts/models/model_kinds/", "full, view, seed, incremental-by-time, incremental-by-key and managed materialization variability", "A catalog of strategies does not establish their equivalence domains."),
    S("iceberg.spec", "Apache Iceberg specification", "Apache Iceberg", "https://iceberg.apache.org/spec/", "snapshot identity, optimistic commit, append/replace/overwrite/delete and sequence semantics", "A table format protocol is a target capability contract, not the transformation planner."),
    S("delta.protocol", "Delta Transaction Protocol", "Delta Lake", "https://github.com/delta-io/delta/blob/master/PROTOCOL.md", "atomic add/remove actions, transaction identifiers, idempotent external progress and commit behavior", "The protocol does not define application-specific progress or transformation correctness."),
    S("openlineage.core", "OpenLineage core model", "OpenLineage", "https://openlineage.io/docs/", "distinct dataset, job and run identities for execution lineage", "Lineage events are evidence claims and do not prove causality, correctness or acceptance."),
    S("openlineage.facets", "OpenLineage facets", "OpenLineage", "https://openlineage.io/docs/spec/facets/", "editioned job, run, input and output evidence facets", "Extensibility does not make arbitrary facets complete or mutually consistent."),
    S("slsa.provenance", "SLSA Build Provenance 1.2", "SLSA", "https://slsa.dev/spec/v1.2/build-provenance", "build definition, parameters, resolved dependencies, builder identity and run details", "Software provenance fields require data-build-specific completeness rules and trusted producers."),
    S("intoto.statement", "in-toto Statement v1", "in-toto", "https://in-toto.io/Statement/v1", "digest-bound immutable subjects and typed predicates", "An attestation statement does not by itself establish truth or signer authority."),
    S("w3c.prov", "PROV-DM", "W3C", "https://www.w3.org/TR/prov-dm/", "entities, activities, usage, generation, derivation and invalidation", "Generic provenance relations require application-specific identity and completeness profiles."),
    S("bazel.query", "Bazel Query Reference", "Bazel", "https://bazel.build/reference/query", "selection as set and graph algebra over a dependency graph", "Software target semantics do not directly define transformation-resource semantics."),
    S("reproducible-builds", "Deterministic build systems", "Reproducible Builds", "https://reproducible-builds.org/docs/deterministic-build-systems/", "stable inputs, stable outputs and minimized ambient environment capture", "Byte reproducibility alone does not prove semantic or data-result equivalence."),
    S("dbsp", "DBSP: Automatic Incremental View Maintenance for Rich Query Languages", "PVLDB", "https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf", "a mathematical full-versus-incremental relation over rich query languages", "A general IVM construction does not determine target commit, late-data or operational policy."),
    S("differential", "Differential Dataflow", "CIDR", "https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf", "versioned changes and incremental iterative computation over partial orders", "A computational model is not a complete batch product or mutation protocol."),
]


CONTEXTS = [
    {
        "context_id": "context.transform_build.definition_selection", "name": "Transformation Definition and Selection",
        "sovereign_question": "Given exact project, package, language and configuration editions, what transformation resources exist, how are their references resolved, and what exact invocation-specific closure is selected?",
        "inside": ["project resource declarations", "configuration precedence", "resource identity", "reference graph", "test bindings", "target-independent compiled definitions", "selector algebra", "state comparison", "selected closure"],
        "outside": ["package retrieval", "SQL or expression-language ownership", "source catalog resolution", "scheduling", "physical execution", "quality waiver", "target mutation"],
        "owner": "authority.transform_build.definition_selection", "status": "specified_candidate",
    },
    {
        "context_id": "context.transform_build.materialization", "name": "Transformation Materialization Planning",
        "sovereign_question": "Given exact selected definitions, input cuts, target state and target capabilities, what full or incremental work and conditional target mutations are valid?",
        "inside": ["materialization kind", "incremental state", "coverage intervals", "late data", "restatement", "schema-change impact", "mutation plan", "preconditions", "effect intents", "receipt reconciliation"],
        "outside": ["query optimization and execution", "target catalog authority", "storage protocol implementation", "scheduling", "resource placement", "publication acceptance"],
        "owner": "authority.transform_build.materialization", "status": "specified_candidate",
    },
    {
        "context_id": "context.transform_build.evidence", "name": "Transformation Build Evidence",
        "sovereign_question": "What can be truthfully concluded about a transformation build from exact definitions, selections, attempts, provider receipts, tests and produced occurrences?",
        "inside": ["build identity", "attempt identity", "resource result classification", "partial and unknown outcomes", "receipt matching", "input-output derivation", "provenance envelope", "publication candidate"],
        "outside": ["runtime telemetry collection", "quality rule ownership", "lineage repository", "artifact signing", "publication authority", "business acceptance"],
        "owner": "authority.transform_build.evidence", "status": "specified_candidate",
    },
]


DECISIONS = {
    "definition": [
        "project_identity", "source_closure_identity", "package_closure_identity", "resource_namespace_and_identity",
        "resource_kind_vocabulary", "definition_language_edition", "query_language_and_dialect_binding",
        "macro_template_edition", "configuration_precedence", "variable_binding", "environment_capture",
        "reference_resolution", "external_source_binding", "disabled_resource_posture", "ephemeral_resource_posture",
        "test_and_assertion_binding", "hook_and_operation_posture", "target_independent_output",
        "nondeterminism_time_randomness_posture", "secret_reference_posture", "canonicalization_and_digest",
        "compile_resource_budget", "diagnostic_and_residual_posture",
    ],
    "selection": [
        "selector_language_edition", "selection_method_vocabulary", "graph_traversal_operators", "set_operator_precedence",
        "exclusion_precedence", "resource_kind_filter", "indirect_test_posture", "disabled_resource_posture",
        "state_comparison_basis", "previous_result_basis", "defer_and_fallback_posture", "empty_selection_posture",
        "selected_dependency_closure", "selection_order_and_digest", "selection_resource_budget",
    ],
    "incremental": [
        "materialization_kind", "input_cut_binding", "target_occurrence_and_snapshot", "full_refresh_posture",
        "incremental_eligibility", "incremental_strategy", "progress_frontier_and_cursor", "unique_key_and_grain",
        "append_merge_replace_overwrite_delete_semantics", "time_partition_and_microbatch", "coverage_interval_algebra",
        "lookback_and_late_data", "restatement_and_backfill", "change_impact_classification", "schema_change_posture",
        "deletion_and_retraction_posture", "target_capability_profile", "concurrency_preconditions", "atomicity_and_isolation",
        "idempotency_scope", "partial_failure_posture", "cost_and_resource_budget", "full_incremental_equivalence_domain",
        "strategy_selection_precedence", "plan_canonicalization_and_digest",
    ],
    "mutation": [
        "target_occurrence_and_provider_edition", "expected_target_state", "mutation_operation_vocabulary",
        "operation_order_and_dependencies", "staging_and_temporary_objects", "transaction_and_atomicity_scope",
        "swap_commit_and_visibility", "idempotency_key_and_fence", "retry_and_unknown_completion",
        "cancellation_boundary", "schema_mutation_posture", "cleanup_and_compensation", "receipt_evidence_profile",
        "reconciliation_precedence", "mutation_resource_budget",
    ],
    "evidence": [
        "build_and_invocation_identity", "attempt_identity", "exact_input_and_plan_binding", "builder_provider_identity",
        "resource_state_taxonomy", "result_precedence", "skipped_blocked_and_deferred", "test_result_import",
        "receipt_scope_and_matching", "partial_unknown_and_cancelled", "input_output_derivation", "provenance_profile",
        "publication_candidate_posture", "retention_redaction_and_disclosure", "reproducibility_claim_profile",
    ],
}


CONTEXT_FOR = {
    "definition": "context.transform_build.definition_selection", "selection": "context.transform_build.definition_selection",
    "incremental": "context.transform_build.materialization", "mutation": "context.transform_build.materialization",
    "evidence": "context.transform_build.evidence",
}


DECISION_ROWS = [
    {
        "decision_id": f"decision.transform_build.{owner}.{name}", "owner_context": CONTEXT_FOR[owner],
        "question": f"What exact {name.replace('_', ' ')} applies?", "default": None,
        "default_law": "forbidden", "status": "declared",
    }
    for owner, names in DECISIONS.items() for name in names
]


def O(owner: str, name: str, inputs: list[str], output: str, purity: str = "pure") -> dict:
    return {
        "operation_ref": f"operation.transform_build.{owner}.{name}", "input_types": inputs,
        "output_type": f"Result<{output},TransformBuildRefusal>", "purity": purity,
    }


OPS = {
    "definition": [
        O("definition", "validate_project_closure", ["ProjectSourceClosureRef", "PackageClosureRef", "DefinitionPolicy", "ResourceBudget"], "ValidatedProjectClosure"),
        O("definition", "parse_resource_declarations", ["ValidatedProjectClosure", "DefinitionLanguageProfile", "ResourceBudget"], "ParsedResourceSet"),
        O("definition", "resolve_configuration", ["ParsedResourceSet", "ConfigurationBindingSet", "ConfigurationPrecedencePolicy"], "ConfiguredResourceSet"),
        O("definition", "resolve_resource_references", ["ConfiguredResourceSet", "ReferenceResolutionPolicy", "ResourceBudget"], "ResolvedResourceGraph"),
        O("definition", "bind_test_declarations", ["ResolvedResourceGraph", "TestBindingPolicy"], "TestBoundResourceGraph"),
        O("definition", "compile_logical_definitions", ["TestBoundResourceGraph", "ExternalQueryCompilerRef", "DefinitionCompilePolicy", "ResourceBudget"], "CompiledTransformationManifest"),
        O("definition", "compare_manifest_editions", ["CompiledTransformationManifest", "CompiledTransformationManifest", "ManifestComparisonPolicy"], "ManifestSemanticDiff"),
        O("definition", "explain_manifest", ["CompiledTransformationManifest", "ExplanationScope", "ResourceBudget"], "ManifestExplanation"),
    ],
    "selection": [
        O("selection", "parse_selector", ["SelectorExpression", "SelectorLanguageProfile", "ResourceBudget"], "ParsedSelector"),
        O("selection", "evaluate_selection_methods", ["CompiledTransformationManifest", "ParsedSelector", "SelectionMethodPolicy"], "CandidateResourceSet"),
        O("selection", "apply_graph_operators", ["ResolvedResourceGraph", "CandidateResourceSet", "GraphSelectionPolicy", "ResourceBudget"], "GraphExpandedResourceSet"),
        O("selection", "apply_set_and_exclusion_operators", ["GraphExpandedResourceSet", "ParsedSelector", "SetSelectionPolicy"], "FilteredResourceSet"),
        O("selection", "resolve_indirect_tests", ["CompiledTransformationManifest", "FilteredResourceSet", "IndirectTestPolicy"], "TestClosedResourceSet"),
        O("selection", "form_selected_closure", ["CompiledTransformationManifest", "TestClosedResourceSet", "SelectionClosurePolicy"], "SelectedTransformationClosure"),
        O("selection", "explain_selection", ["SelectedTransformationClosure", "ExplanationScope", "ResourceBudget"], "SelectionExplanation"),
    ],
    "incremental": [
        O("incremental", "validate_materialization_context", ["SelectedTransformationClosure", "InputCutSet", "TargetStateRef", "TargetCapabilityProfile"], "ValidatedMaterializationContext"),
        O("incremental", "classify_definition_change", ["ManifestSemanticDiff", "ChangeImpactPolicy"], "TransformationChangeImpact"),
        O("incremental", "derive_incremental_eligibility", ["ValidatedMaterializationContext", "IncrementalPolicy"], "IncrementalEligibility"),
        O("incremental", "compute_coverage_delta", ["InputCutSet", "MaterializationState", "CoveragePolicy"], "CoverageDelta"),
        O("incremental", "plan_late_data_and_lookback", ["CoverageDelta", "LateDataPolicy", "ResourceBudget"], "LateDataPlan"),
        O("incremental", "plan_restatement", ["MaterializationState", "RestatementRequest", "RestatementPolicy"], "RestatementPlan"),
        O("incremental", "plan_schema_transition", ["TargetSchemaRef", "OutputSchemaRef", "SchemaTransitionPolicy"], "SchemaTransitionPlan"),
        O("incremental", "compile_materialization_plan", ["ValidatedMaterializationContext", "IncrementalEligibility", "CoverageDelta", "LateDataPlan", "SchemaTransitionPlan", "MaterializationPolicy", "ResourceBudget"], "MaterializationPlan"),
        O("incremental", "validate_incremental_equivalence_claim", ["MaterializationPlan", "EquivalenceDomain", "EquivalencePolicy"], "IncrementalEquivalenceClaim"),
        O("incremental", "explain_materialization_plan", ["MaterializationPlan", "ExplanationScope", "ResourceBudget"], "MaterializationExplanation"),
    ],
    "mutation": [
        O("mutation", "lower_plan_to_mutation_intents", ["MaterializationPlan", "TargetMutationProfile", "MutationPolicy", "ResourceBudget"], "TargetMutationIntentSet"),
        O("mutation", "validate_mutation_preconditions", ["TargetMutationIntentSet", "ExpectedTargetState", "PreconditionPolicy"], "PreconditionedMutationPlan"),
        O("mutation", "form_mutation_effect_request", ["PreconditionedMutationPlan", "ExecutionBindingRef", "EffectRequestPolicy"], "TargetMutationEffectRequest"),
        O("mutation", "classify_mutation_receipt", ["TargetMutationEffectRequest", "ProviderMutationReceipt", "ReceiptPolicy"], "MutationReceiptClassification"),
        O("mutation", "reconcile_unknown_mutation", ["TargetMutationEffectRequest", "TargetObservationSet", "ReconciliationPolicy"], "MutationReconciliationResult"),
        O("mutation", "plan_cleanup_or_compensation", ["MutationReceiptClassification", "TargetObservationSet", "CompensationPolicy"], "CleanupOrCompensationPlan"),
        O("mutation", "explain_mutation_protocol", ["TargetMutationIntentSet", "ProviderMutationReceiptSet", "ExplanationScope"], "MutationProtocolExplanation"),
    ],
    "evidence": [
        O("evidence", "open_build_evidence", ["CompiledTransformationManifest", "SelectedTransformationClosure", "MaterializationPlan", "BuildIdentityPolicy"], "OpenBuildEvidence"),
        O("evidence", "record_resource_attempt", ["OpenBuildEvidence", "ResourceAttemptReceipt", "AttemptEvidencePolicy"], "OpenBuildEvidence"),
        O("evidence", "classify_resource_result", ["ResourceAttemptSet", "ProviderExecutionReceiptSet", "ImportedTestReceiptSet", "ResultPolicy"], "ResourceBuildResult"),
        O("evidence", "assemble_derivation_claims", ["ResourceBuildResultSet", "InputOccurrenceSet", "OutputOccurrenceSet", "DerivationPolicy"], "BuildDerivationSet"),
        O("evidence", "assemble_build_provenance", ["OpenBuildEvidence", "ResourceBuildResultSet", "BuildDerivationSet", "ProvenancePolicy"], "TransformationBuildProvenance"),
        O("evidence", "form_publication_candidate", ["TransformationBuildProvenance", "PublicationCandidatePolicy"], "TransformationPublicationCandidate"),
        O("evidence", "verify_build_evidence_completeness", ["TransformationBuildProvenance", "EvidenceCompletenessPolicy"], "BuildEvidenceCompletenessReport"),
    ],
}


COMMON_TYPES = [
    "TransformBuildEdition", "ProjectId", "ProjectEdition", "ResourceId", "ResourceEdition", "ResourceKind",
    "ResourceNamespace", "SourceOccurrenceRef", "SchemaEditionRef", "QueryDialectRef", "PolicyDigest",
    "ConfigurationDigest", "ResourceBudget", "ExplanationScope", "TransformBuildRefusal",
]


TYPES = {
    "definition": COMMON_TYPES + [
        "ProjectSourceClosureRef", "PackageClosureRef", "PackageEditionRef", "DefinitionLanguageProfile", "DefinitionPolicy",
        "ValidatedProjectClosure", "ResourceDeclaration", "ParsedResource", "ParsedResourceSet", "ConfigurationBinding",
        "ConfigurationBindingSet", "ConfigurationPrecedencePolicy", "ConfiguredResource", "ConfiguredResourceSet",
        "ReferenceDeclaration", "ReferenceEdge", "ReferenceResolutionPolicy", "ResolvedResourceGraph", "GraphCycle",
        "ExternalSourceBindingRef", "MacroEditionRef", "TemplateExpansionTrace", "TestDeclaration", "TestBindingPolicy",
        "TestBoundResourceGraph", "ExternalQueryCompilerRef", "LogicalTransformationRef", "CompiledResourceDefinition",
        "CompiledTransformationManifest", "ManifestDigest", "ManifestComparisonPolicy", "ManifestSemanticDiff",
        "DefinitionCompilePolicy", "Diagnostic", "DiagnosticSet", "ManifestExplanation", "CanonicalizationProfile",
    ],
    "selection": COMMON_TYPES + [
        "CompiledTransformationManifest", "ManifestDigest", "ResolvedResourceGraph", "SelectorExpression", "SelectorLanguageProfile",
        "ParsedSelector", "SelectionMethod", "SelectionMethodPolicy", "CandidateResourceSet", "GraphOperator",
        "GraphSelectionPolicy", "GraphExpandedResourceSet", "SetOperator", "SetSelectionPolicy", "FilteredResourceSet",
        "IndirectTestPolicy", "TestClosedResourceSet", "StateComparisonRef", "PreviousResultRef", "DeferredResolutionRef",
        "SelectionClosurePolicy", "SelectedTransformationClosure", "SelectionDigest", "SelectionExplanation", "SelectionResidual",
        "ResourceOrder", "SelectionTrace", "EmptySelectionPosture", "ResourceKindFilter", "DependencyClosure",
    ],
    "incremental": COMMON_TYPES + [
        "SelectedTransformationClosure", "InputCutRef", "InputCutSet", "TargetOccurrenceRef", "TargetSnapshotRef",
        "TargetStateRef", "TargetCapabilityProfile", "ValidatedMaterializationContext", "MaterializationKind",
        "MaterializationState", "MaterializationStateEdition", "ProgressFrontier", "UniqueKey", "GrainRef",
        "IncrementalStrategy", "IncrementalPolicy", "IncrementalEligibility", "CoverageInterval", "CoverageSet",
        "CoverageDelta", "CoveragePolicy", "LateDataPolicy", "LateDataPlan", "LookbackWindow", "MicrobatchProfile",
        "RestatementRequest", "RestatementPolicy", "RestatementPlan", "BackfillRange", "ManifestSemanticDiff",
        "ChangeImpactPolicy", "TransformationChangeImpact", "TargetSchemaRef", "OutputSchemaRef", "SchemaTransitionPolicy",
        "SchemaTransitionPlan", "RetractionPosture", "DeletePosture", "MaterializationPolicy", "MaterializationPlan",
        "MaterializationPlanDigest", "EquivalenceDomain", "EquivalencePolicy", "IncrementalEquivalenceClaim",
        "MaterializationExplanation", "CostEstimate", "ConcurrencyPrecondition", "IsolationProfile",
    ],
    "mutation": COMMON_TYPES + [
        "MaterializationPlan", "MaterializationPlanDigest", "TargetOccurrenceRef", "TargetProviderEditionRef",
        "TargetMutationProfile", "MutationOperationKind", "MutationOperation", "MutationDependency", "MutationPolicy",
        "TargetMutationIntent", "TargetMutationIntentSet", "ExpectedTargetState", "PreconditionPolicy",
        "PreconditionedMutationPlan", "ExecutionBindingRef", "EffectRequestPolicy", "TargetMutationEffectRequest",
        "IdempotencyKey", "FenceToken", "TransactionScope", "AtomicityProfile", "VisibilityProfile", "CancellationBoundary",
        "ProviderMutationReceipt", "ProviderMutationReceiptSet", "ReceiptPolicy", "MutationReceiptClassification",
        "TargetObservation", "TargetObservationSet", "ReconciliationPolicy", "MutationReconciliationResult",
        "CompensationPolicy", "CleanupOrCompensationPlan", "MutationProtocolExplanation", "UnknownCompletion",
        "PartialCompletion", "CommitOccurrenceRef", "PublicationCandidateRef",
    ],
    "evidence": COMMON_TYPES + [
        "BuildId", "BuildInvocationId", "BuildAttemptId", "CompiledTransformationManifest", "SelectedTransformationClosure",
        "MaterializationPlan", "BuildIdentityPolicy", "OpenBuildEvidence", "ResourceAttemptId", "ResourceAttemptReceipt",
        "ResourceAttemptSet", "ProviderExecutionReceipt", "ProviderExecutionReceiptSet", "ProviderMutationReceipt",
        "ImportedTestReceipt", "ImportedTestReceiptSet", "ResourceResultState", "ResultPolicy", "ResourceBuildResult",
        "ResourceBuildResultSet", "InputOccurrenceRef", "InputOccurrenceSet", "OutputOccurrenceRef", "OutputOccurrenceSet",
        "DerivationClaim", "BuildDerivationSet", "DerivationPolicy", "BuilderIdentityRef", "BuildEnvironmentDigest",
        "ProvenancePolicy", "TransformationBuildProvenance", "ProvenanceDigest", "PublicationCandidatePolicy",
        "TransformationPublicationCandidate", "EvidenceCompletenessPolicy", "BuildEvidenceCompletenessReport",
        "PartialBuildOutcome", "UnknownBuildOutcome", "CancellationOutcome", "EvidenceResidual", "EvidenceResidualSet",
    ],
}


SHARED_LAWS = [
    "Project source closure, package closure, compiled manifest, selected closure, build invocation, attempt, target occurrence and publication occurrence are distinct identities.",
    "Definition compilation, invocation selection, query compilation, physical execution, materialization planning, target mutation and publication acceptance are distinct contracts.",
    "Every semantic input that may alter a compiled manifest or selected closure is explicit, editioned and digest bound; ambient time, filesystem order, environment, network and randomness are forbidden unless declared.",
    "A resource reference establishes a dependency or name binding, not schema compatibility, data availability, quality or authorization.",
    "Disabled, unselected, deferred, skipped, blocked, cancelled, failed, unknown, succeeded, tested and published remain distinct states.",
    "A successful provider execution receipt is not a successful materialization, passed test, complete build, publication approval or factual acceptance.",
    "Full refresh and incremental execution are equivalent only over an explicit transformation, input-change, target-state and tolerance domain with evidence.",
    "Late arrival, correction, deletion, retraction, schema change, logic change, restatement and backfill are distinct causes and retain distinct plans.",
    "Append, merge, delete-insert, partition overwrite, full replace, snapshot swap and publication are distinct mutation semantics.",
    "Unknown mutation completion requires reconciliation before retry; retry cannot convert ambiguity into success.",
    "Every plan and evidence result is finite-budgeted and returns a typed refusal or residual rather than silently truncating the graph, intervals, attempts or evidence.",
    "A model or agent may propose attributed selectors, configurations, change classifications or diagnostics but cannot resolve hidden defaults, waive refusals, authorize effects, accept results, publish or qualify an implementation.",
]


def lib(owner: str, library_id: str, name: str, kind: str, responsibility: str, effect: str,
        dependencies: list[str], extra_laws: list[str], refusals: list[str], exclusions: list[str], oracles: list[str]) -> dict:
    return {
        "library_id": library_id, "name": name, "library_kind": kind,
        "semantic_owner_context": CONTEXT_FOR[owner], "status": "specified",
        "candidate_responsibility": responsibility, "effect_boundary": effect,
        "public_types": TYPES[owner], "public_traits": ["".join(part.capitalize() for part in library_id.split(".")[1:]) + "Algebra"],
        "operation_refs": [row["operation_ref"] for row in OPS[owner]], "operations": OPS[owner],
        "decision_refs": [row["decision_id"] for row in DECISION_ROWS if f".{owner}." in row["decision_id"]],
        "configuration_contracts": [f"{owner.capitalize()}Policy"], "laws": SHARED_LAWS + extra_laws,
        "invariants": ["all decision points are explicit and no-default", "all identities and editions are digest bound", "no ambient I/O occurs inside the semantic boundary", "optional model or agent proposals never acquire authority"],
        "error_contracts": refusals + ["UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
        "dependencies": dependencies, "evidence_refs": [row["source_id"] for row in SOURCES],
        "oracles": oracles + ["two independent implementations and cross-provider differential results"],
        "gaps": ["No implementation is qualified; two independent implementations and executed exact-scope conformance remain required."],
        "must_not_own": exclusions, "qualification_required": False,
    }


LIBRARIES = [
    lib("definition", "library.transform_definition.compiler", "Transformation Definition Compiler", "semantic_pure",
        "compile an exact project and package closure into a deterministic target-independent transformation manifest",
        "pure_no_io", ["library.package.reference_closure", "library.qck.query-syntax", "library.qck.query-binding"],
        ["Package retrieval is complete before this compiler starts; only an exact immutable closure reference enters the boundary.",
         "Configuration precedence is total and explainable; no provider adapter may silently change resolved semantic configuration.",
         "Compiled query or expression payloads are imported typed outputs from a language compiler and do not transfer language ownership.",
         "Manifest digest changes whenever any meaning-affecting definition, dependency, compiler edition, configuration or external binding changes."],
        ["ProjectClosureUnbound", "PackageClosureUnbound", "ResourceIdentityCollision", "DefinitionSyntaxInvalid", "ConfigurationPrecedenceAmbiguous", "ReferenceUnresolved", "DependencyCycle", "MacroEditionUnbound", "EnvironmentCaptureForbidden", "SecretValueEmbedded", "QueryCompilerUnbound", "TestBindingInvalid", "ManifestNondeterministic"],
        ["package discovery, fetching or lock resolution", "SQL, expression or query-language parsing and optimization", "source catalog currency", "selection", "scheduling or execution", "quality verdict or waiver", "target mutation or publication"],
        ["golden project-to-manifest fixtures", "configuration precedence decision tables", "reference graph and cycle model tests", "ambient time environment randomness and filesystem-order metamorphic tests", "manifest digest reproducibility tests"]),
    lib("selection", "library.transform_selection.closure", "Transformation Selection Closure", "algorithm_pure",
        "evaluate an explicit selector over one exact compiled manifest and form a deterministic dependency- and test-closed invocation set",
        "pure_no_io", ["library.transform_definition.compiler"],
        ["Selection is evaluated over exactly one manifest edition; resource membership cannot be imported from ambient current project state.",
         "Selection methods, graph expansion, set operations, exclusion, kind filtering and indirect-test closure execute in declared precedence.",
         "A selection preview and execution selection with the same exact inputs have the same members, order and digest.",
         "Deferral changes external occurrence resolution, not logical resource identity or dependency edges."],
        ["ManifestUnbound", "SelectorSyntaxInvalid", "SelectorMethodUnknown", "GraphOperatorUnsupported", "SetOperatorPrecedenceAmbiguous", "SelectionResourceUnknown", "SelectionCycle", "StateComparisonUnbound", "DeferredResolutionAmbiguous", "IndirectTestPolicyMissing", "EmptySelectionRefused", "SelectionClosureIncomplete"],
        ["resource definition compilation", "state artifact retrieval", "target relation resolution", "scheduling", "physical execution", "test meaning or waiver", "materialization strategy"],
        ["selector algebra truth tables", "graph traversal and exclusion property tests", "indirect test closure fixtures", "state and defer negative twins", "selection order and digest determinism tests"]),
    lib("incremental", "library.materialization.incremental_planner", "Incremental Materialization Planner", "policy_pure",
        "derive a full-refresh, incremental, restatement or refusal plan from exact selected resources, input cuts, target state and capabilities",
        "pure_no_io", ["library.transform_definition.compiler", "library.transform_selection.closure", "library.schema_registry.reference_closure"],
        ["The planner consumes an observed immutable target-state reference and cannot query or mutate a target itself.",
         "Incremental eligibility is proved from declared semantics and target state; target existence alone is insufficient.",
         "Coverage is an explicit interval or change-domain algebra; maximum timestamps are not a universal progress model.",
         "A full-refresh fallback is a distinct plan with cost, authority and destructiveness requirements, never an automatic escape hatch.",
         "Strategy choice is constrained by key, deletion, schema, isolation and target capabilities before cost preference."],
        ["SelectedClosureUnbound", "InputCutUnbound", "TargetStateUnbound", "TargetCapabilityMissing", "MaterializationKindUnsupported", "IncrementalEligibilityUnproved", "UniqueKeyInvalid", "CoverageIncomparable", "LateDataPolicyMissing", "RestatementRangeInvalid", "SchemaChangeUnhandled", "RetractionUnsupported", "IsolationInsufficient", "FullRefreshAuthorityMissing", "IncrementalEquivalenceUnproved", "PlanNondeterministic"],
        ["input acquisition", "query optimization or physical execution", "target state observation", "table-format commit protocol", "resource scheduling", "quality acceptance", "publication authority"],
        ["full-versus-incremental differential corpus", "late-arrival correction deletion and retraction fixtures", "coverage interval algebra properties", "schema and logic change impact model tests", "strategy capability constraint solver tests", "restatement and backfill metamorphic tests"]),
    lib("mutation", "library.materialization.mutation_protocol", "Materialization Mutation Protocol", "policy_pure",
        "lower a materialization plan into conditional provider-neutral target effect requests and reconcile exact provider receipts",
        "pure_effect_intents", ["library.materialization.incremental_planner", "library.persistence.commit_protocol"],
        ["The library creates effect requests but performs no target I/O and cannot grant mutation or publication authority.",
         "Every request binds the expected target state, target occurrence, provider edition, plan digest, idempotency scope and fence.",
         "Provider acknowledgement, durable commit, reader visibility, catalog publication and consumer acceptance remain distinct receipts.",
         "Cancellation after an irreversible boundary yields an explicit completion-unknown or reconciliation-required state.",
         "Cleanup and compensation are planned only where target capabilities and observed receipts make them valid."],
        ["MaterializationPlanUnbound", "TargetProviderUnbound", "MutationProfileUnsupported", "ExpectedStateMissing", "PreconditionFailed", "AtomicityUnsupported", "IdempotencyScopeMissing", "FenceStale", "EffectAuthorityMissing", "ProviderReceiptInvalid", "ReceiptScopeMismatch", "CompletionUnknown", "ReconciliationEvidenceInsufficient", "CancellationTooLate", "CompensationUnsupported"],
        ["physical query or mutation execution", "target catalog or storage implementation", "credential custody", "commit authority", "publication acceptance", "orchestration retries", "provider qualification"],
        ["mutation state-machine model tests", "idempotency retry and fence properties", "unknown-completion reconciliation fixtures", "partial commit and cancellation fault injection", "provider receipt conformance corpus", "cleanup and compensation negative twins"]),
    lib("evidence", "library.transform_build.evidence", "Transformation Build Evidence Assembler", "semantic_pure",
        "classify resource outcomes and assemble digest-bound derivation, provenance and publication-candidate evidence without self-acceptance",
        "pure_no_io", ["library.transform_definition.compiler", "library.transform_selection.closure", "library.materialization.incremental_planner", "library.materialization.mutation_protocol", "library.lpe.prov-statement-algebra","library.lpe.provenance-assertion"],
        ["Build identity binds the exact manifest, selection, input cuts, target state, materialization plan and declared builder environment.",
         "Evidence assembly preserves every attempt and contradictory or partial receipt; later success does not erase earlier failure.",
         "Lineage is an attributed derivation claim scoped to observed inputs, outputs and activity, not universal causal proof.",
         "A publication candidate is evidence offered to an external authority; this library cannot approve, list or publish it.",
         "Reproducibility claims state the compared artifacts, equivalence relation, controlled inputs and observed rebuild evidence."],
        ["BuildIdentityIncomplete", "ManifestDigestMismatch", "SelectionDigestMismatch", "InputOccurrenceUnbound", "AttemptIdentityCollision", "ProviderReceiptUntrusted", "ReceiptScopeMismatch", "ResultPrecedenceAmbiguous", "PartialOutcomeUnclassified", "UnknownOutcomeUnreconciled", "DerivationClaimUnsupported", "ProvenanceIncomplete", "TestReceiptUnbound", "PublicationCandidateIncomplete", "ReproducibilityClaimUnsupported"],
        ["telemetry or receipt collection", "test or quality-rule ownership", "lineage repository or graph query", "attestation signing", "publication, listing or factual acceptance", "provider qualification", "business outcome attribution"],
        ["result-state precedence decision tables", "attempt and receipt matching properties", "partial unknown cancelled and blocked fixtures", "provenance completeness mutation tests", "derivation edge anti-Cartesian tests", "independent rebuild and artifact-equivalence corpus"]),
]


LENSES = [
    ("value", "Analytics engineers need one reproducible build outcome, but compilers, selectors, planners, mutation adapters and evidence consumers need separately reusable seams.", "Retain one product composition and five libraries; none of the libraries is independently the product."),
    ("semantic", "Definition, selection, incremental state, target mutation and evidence have different owned vocabularies and homonyms.", "Use three bounded contexts and explicit published contracts rather than one manifest/materialization context."),
    ("behavior", "Compilation and selection are deterministic graph transformations; planning is state calculus; mutation is an effect protocol; evidence is result adjudication.", "Do not merge operations merely because one build invokes them sequentially."),
    ("authority", "Project owners declare definitions, target authorities authorize effects, providers issue receipts, quality owners decide tests and publication authorities accept candidates.", "Libraries validate exact external authority references but never mint or waive them."),
    ("consistency", "A manifest and selected closure each require atomic digest integrity; materialization plans bind one target-state cut; evidence is append-only across attempts.", "Keep each aggregate-sized invariant in its owner library and link by immutable references."),
    ("variability", "Languages, selector algebra, incremental strategies, target protocols and evidence profiles vary on different axes and binding times.", "Expose all choices as editioned no-default decisions and substitute each provider independently."),
    ("software", "The five seams have distinct APIs, dependencies, tests and rates of change.", "Split the two coarse labels into five exact libraries; import package, query, quality, lineage-store and target protocols."),
    ("operation", "Compilation and planning are cold control-path work; mutation interacts with an effectful provider; evidence may outlive executions.", "Keep semantic libraries pure and represent effects as requests/receipts with separate resource envelopes."),
    ("economics", "Graph compilation cost, selector latency, recomputation volume, target mutation cost and evidence retention are independently measurable.", "Independent optimization and exit are boundary evidence, but not independent product evidence."),
    ("empirical", "dbt, Dataform and SQLMesh repeatedly separate resources, selections, compilation results, invocations and incremental plans; Iceberg and Delta expose distinct commit protocols.", "Generalize recurring decisions while preserving vendor differences and refusing universal defaults."),
    ("analytical", "Selection is set/graph algebra; incremental planning is change and interval calculus; IVM equivalence is a mathematical claim; result classification is evidence logic.", "State assumptions and equivalence domains explicitly; do not reduce materialization to timestamp filtering."),
    ("system", "Composition hazards include stale manifests, wrong defer targets, late-data loss, duplicate merges, unknown commits, false success and premature publication.", "Digest every boundary, fail closed, reconcile unknown effects and withhold authority from build success."),
]


LENS_METHODS = {
    "value": ["method.business.jtbd", "method.business.capability_map", "method.business.product_split_merge"],
    "semantic": ["method.domain.ddd", "method.domain.terminology", "method.information.conceptual_data"],
    "behavior": ["method.domain.eventstorming", "method.work.statecharts", "method.work.dmn"],
    "authority": ["method.trust.threat_model", "method.systems.stpa"],
    "consistency": ["method.domain.ddd", "method.formal.alloy", "method.formal.design_by_contract"],
    "variability": ["method.variability.foda", "method.variability.decision_model", "method.variability.product_line"],
    "software": ["method.architecture.coupling", "method.architecture.hexagonal", "method.variability.algebraic_api"],
    "operation": ["method.operations.resilience", "method.operations.capacity", "method.operations.sre"],
    "economics": ["method.operations.finops", "method.business.product_split_merge"],
    "empirical": ["method.evidence.systematic_review", "method.evidence.repository_mining", "method.evidence.red_team"],
    "analytical": ["method.analytics.or", "method.formal.property_testing", "method.formal.theorem_proving"],
    "system": ["method.systems.stpa", "method.trust.fmea_fta", "method.strategy.systems_thinking"],
}


LENS_ROWS = [
    {
        "lens_id": f"lens.transform-build.{name}", "lens": name,
        "question": "What does this lens require of the proposed transformation-build boundaries?",
        "finding": finding, "boundary_consequence": consequence,
        "method_refs": LENS_METHODS[name], "status": "applied",
    }
    for name, finding, consequence in LENSES
]


BOUNDARY_VERDICTS = [
    {
        "verdict_id": "verdict.transform-build.transform-manifest-split",
        "subject_refs": ["library.transform_definition.compiler", "library.transform_selection.closure"],
        "supersedes_abstract_ref": "library.transform_manifest", "disposition": "split_coarse_contract",
        "rationale": "A compiled manifest describes the complete resolved project; a selection is invocation-specific set/graph closure over one manifest. They have different inputs, variability, caches, callers and substitution seams.",
        "shared_contract_types": ["CompiledTransformationManifest", "ResolvedResourceGraph", "ResourceId", "ManifestDigest"],
        "merge_falsifier": "Merge only if independent implementations cannot version, cache, test or substitute manifest compilation and selection separately.",
        "status": "candidate_boundary_adjudicated_not_ratified",
    },
    {
        "verdict_id": "verdict.transform-build.materialization-split",
        "subject_refs": ["library.materialization.incremental_planner", "library.materialization.mutation_protocol", "library.transform_build.evidence"],
        "supersedes_abstract_ref": "library.materialization", "disposition": "split_coarse_contract",
        "rationale": "Incremental calculus decides valid work, mutation protocol forms and reconciles effects, and evidence classifies what occurred. Their authority, purity, failure states and consumers differ.",
        "shared_contract_types": ["MaterializationPlan", "MaterializationPlanDigest", "ProviderMutationReceipt", "TransformBuildRefusal"],
        "merge_falsifier": "Merge only if planning, provider effect protocol and evidence appraisal cannot be replaced or qualified independently without semantic duplication.",
        "status": "candidate_boundary_adjudicated_not_ratified",
    },
    {
        "verdict_id": "verdict.transform-build.imported-neighbors",
        "subject_refs": [row["library_id"] for row in LIBRARIES], "disposition": "retain_import_boundaries",
        "rationale": "Package closure, query compilation, source/target catalog state, physical execution, quality authority, lineage storage, scheduling and publication are separately owned contracts and must enter through exact references or requests/receipts.",
        "imported_contract_refs": ["library.package.reference_closure", "library.qck.query-syntax", "library.qck.query-binding", "library.schema_registry.reference_closure", "library.persistence.commit_protocol", "library.lpe.prov-statement-algebra","library.lpe.provenance-assertion"],
        "status": "candidate_boundary_adjudicated_not_ratified",
    },
]


NEGATIVES = [
    ("manifest_selection", "The manifest is only the selected resources.", "Compile the full resolved project and form a separately identified invocation selection."),
    ("package_network", "The compiler may fetch latest packages while compiling.", "Resolve and digest an immutable package closure before compilation."),
    ("config_last_write", "Configuration precedence may follow incidental file iteration order.", "Bind an explicit total precedence policy and explanation trace."),
    ("ambient_env", "Unrecorded environment variables may change compiled meaning.", "Forbid or explicitly bind every meaning-affecting environment value."),
    ("macro_latest", "Macros may resolve to the latest compatible edition.", "Bind exact macro and compiler editions in the manifest digest."),
    ("sql_owned", "The transformation manifest compiler owns every query language.", "Import an exact query-language compiler output through a typed contract."),
    ("ref_schema", "A resolved ref proves compatible schema and available data.", "Keep reference, schema, occurrence and availability evidence distinct."),
    ("select_default_all", "An empty or invalid selector may silently mean all resources.", "Apply the declared empty-selection posture or refuse."),
    ("selection_order", "Selector evaluation order is immaterial.", "Declare method, graph, set, exclusion and kind-filter precedence."),
    ("defer_identity", "Deferring to another environment changes logical resource identity.", "Retain logical identity and separately bind the external occurrence."),
    ("test_pass", "An indirectly selected test is already passed.", "Selection creates a test work item; only an exact imported receipt supports a result."),
    ("target_exists", "An existing target table proves incremental eligibility.", "Prove eligibility from semantics, state, strategy and capabilities."),
    ("max_timestamp", "The maximum target timestamp is a universal incremental cursor.", "Use an explicit coverage/change algebra and late-data policy."),
    ("unique_key", "Declaring a unique key proves source and target uniqueness.", "Require scoped grain evidence and define null/duplicate behavior."),
    ("append_merge", "Append and merge are interchangeable if queries succeed.", "Preserve distinct duplicate, update, delete and idempotency semantics."),
    ("schema_sync", "Automatic schema synchronization is always safe.", "Plan an explicit schema transition and external authority decision."),
    ("full_refresh_escape", "Any incremental uncertainty may silently trigger full refresh.", "Emit a distinct destructive/costed plan requiring capability and authority."),
    ("late_lookback", "A fixed lookback guarantees all late data is captured.", "State the bounded assumption and residual beyond the horizon."),
    ("logic_future", "Changed transformation logic need only apply to future rows.", "Classify historical impact and require restatement or an explicit discontinuity."),
    ("ivm_universal", "Any query can be incrementally maintained with identical behavior at lower cost.", "Bind the exact language fragment, change domain, target state and equivalence evidence."),
    ("provider_strategy", "A provider adapter may select any supported mutation strategy.", "The semantic planner selects within explicit capability and policy constraints."),
    ("effect_call", "A mutation plan directly performs target I/O.", "Lower to typed effect requests and keep physical execution outside."),
    ("ack_commit", "Provider acknowledgement proves durable commit and visibility.", "Classify acknowledgement, commit, visibility and publication receipts separately."),
    ("retry_unknown", "Retrying an unknown mutation is safe because an idempotency key was supplied.", "Reconcile exact target state and provider semantics before retry."),
    ("cancel_rollback", "Cancellation implies all target effects were rolled back.", "Respect the irreversible boundary and classify unknown or partial completion."),
    ("cleanup_compensation", "Cleanup and compensation are always possible.", "Require declared target capability and an observed compensable state."),
    ("success_publish", "All resources succeeded, therefore the result is published.", "Emit a publication candidate for an external authority."),
    ("later_success", "A later successful retry erases failed attempts.", "Retain append-only attempt evidence and result precedence."),
    ("lineage_causal", "Recorded input/output lineage proves causal completeness.", "Emit scoped attributed derivation claims and explicit completeness limits."),
    ("provenance_truth", "A signed provenance statement proves its predicate is true.", "Evaluate signer, builder, scope, completeness and evidence policy separately."),
    ("repro_semantic", "Byte-identical artifacts prove data-result correctness.", "State artifact and semantic equivalence relations independently."),
    ("agent_authority", "An agent may choose hidden defaults, approve a full refresh or accept build evidence.", "Limit agents to attributed proposals; deterministic rules and accountable authorities decide."),
]


NEGATIVE_ROWS = [
    {"negative_id": f"negative.transform-build.{ident}", "unsafe_inference": unsafe, "required_behavior": required, "status": "active"}
    for ident, unsafe, required in NEGATIVES
]


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
        "manifest_id": "transformation_build_semantics_v0_1_0", "as_of": AS_OF, "edition": EDITION,
        "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False,
        "qualified_implementation_count": 0,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS transformation build: {len(SOURCES)} sources, 3 contexts, {len(DECISION_ROWS)} decisions, 5 exact libraries, {sum(len(v) for v in OPS.values())} operations, 12 lenses")


if __name__ == "__main__":
    main()
