#!/usr/bin/env python3
"""Deterministically enrich the platform slice with the solution-compiler product model.

This module does not invent a compiler implementation.  It projects already researched compiler
subsystems into one product-specific DDD and library graph, while preserving external semantic
ownership, qualification, build execution, effect authority and vertical acceptance as separate
boundaries.
"""

from __future__ import annotations

from typing import Any


PRODUCT = "product.solution_compiler"
AUTOMATION = {
    "default": "DETERMINISTIC_CORE_ONLY",
    "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
    "law": "A model or agent may propose declarations, mappings, plans, diagnostics, rewrites or repair candidates only; deterministic parsers, typecheckers, semantic owners, solvers, proof checkers and authorities decide whether they enter a compilation.",
    "removal_law": "Removing every optional model or agent extension preserves parsing, resolution, lowering, constraint solving, proof checking, artifact planning, diagnostics and evidence production; explicitly requested assistance may instead yield capability_unavailable.",
    "hard_work_law": "Automation never substitutes for vocabulary, domain ownership, invariants, registry population, exact algorithms, proof obligations, qualification evidence, effect authority or vertical acceptance.",
}

CENTRAL_REGISTRY = "research/domain_atlas/compiler/library_registry/library-contributions.jsonl"
IMPLEMENTATION_REGISTRY = "research/domain_atlas/compiler/implementation_architecture/library-boundaries.jsonl"
IR_REGISTRY = "research/domain_atlas/compiler/ir_lowering/library-boundaries.jsonl"
MCA_REGISTRY = "research/domain_atlas/compiler/model_class_adjudication/library-boundaries.jsonl"
BINDER_REGISTRY = "research/domain_atlas/compiler/binder_solver/library-boundaries.jsonl"
CONFORMANCE_REGISTRY = "research/domain_atlas/compiler/conformance_evaluation/library-boundaries.jsonl"
CODEGEN_REGISTRY = "research/domain_atlas/compiler/codegen_build/library-toolchain-boundaries.jsonl"

COMPILER_LIBRARIES = {
    "library.platform.intent_contract",
    "library.platform.compiler_contract",
    "library.platform.binding_evidence",
    "library.platform.release_evidence",
    "library.platform.compiler.canonical_reference_resolution",
    "library.platform.compiler.semantic_ir_lowering",
    "library.platform.compiler.model_class_adjudication",
    "library.platform.compiler.conformance_coordination",
    "library.platform.compiler.target_artifact_generation",
    "library.platform.compiler.release_artifact_governance",
    "library.platform.compiler.incremental_trace",
}

DDD_FIELDS = {
    "domain_vision_statement", "subdomain_classification", "bounded_context_boundary",
    "ubiquitous_language_policy", "context_map", "anti_corruption_layers", "published_language",
    "value_objects", "entities", "aggregates", "aggregate_roots", "aggregate_invariants",
    "commands", "domain_events", "refusal_failure_catalog", "domain_services",
    "application_services", "repositories", "factories", "specifications", "state_machine",
    "policies_and_reactions", "sagas_and_process_managers", "read_models_and_projections",
    "integration_event_policy", "concurrency_and_idempotency", "time_model",
    "event_storming_swimlanes", "nonfunctional_laws",
}


def evidence(ident: str, title: str, publisher: str, uri: str, claim: str) -> dict[str, Any]:
    return {
        "source_id": ident,
        "source_class": "official_specification_or_documentation",
        "title": title,
        "publisher": publisher,
        "uri": uri,
        "retrieved_at": "2026-08-26",
        "claim": claim,
        "scope_limit": "Supports the named compiler mechanism or contract only; it does not establish this product boundary as universally complete or qualify an implementation.",
    }


def artifact(ident: str, kind: str, name: str, owner: str | None, definition: str, refs: list[str]) -> dict[str, Any]:
    return {
        "artifact_id": ident, "kind": kind, "name": name, "status": "candidate",
        "semantic_owner_ref": owner, "adoption_unit": False, "operated": False,
        "definition": definition, "evidence_refs": refs,
    }


def library(
    ident: str,
    owner: str,
    capability: str,
    types: list[str],
    operations: list[str],
    decisions: list[str],
    invariants: list[str],
    refusals: list[str],
    dependencies: list[str],
    effect_boundary: str,
    refs: list[str],
    class_: str = "semantic_pure",
) -> dict[str, Any]:
    return {
        "library_id": ident, "class": class_, "owner_ref": owner,
        "provides": [capability], "types": types, "operations": operations,
        "decisions": decisions, "invariants": invariants, "refusals": refusals,
        "dependencies": dependencies, "effect_boundary": effect_boundary,
        "evidence_refs": refs, "product_refs": [PRODUCT],
    }


def origin_map(refs: list[str], path: str) -> dict[str, str]:
    return {ref: path for ref in refs}


IR_REFS = [
    "library.ir.analytical_design", "library.ir.logical_ir", "library.ir.optimizer",
    "library.ir.policy", "library.ir.proof_ir", "library.ir.proof_runner", "library.ir.release",
    "library.ir.rewrite", "library.ir.serialization", "library.ir.syntax",
    "library.ir.target_backend", "library.ir.types_shapes",
]
MCA_REFS = [
    "library.mca.class_predicates", "library.mca.convexity_oracle", "library.mca.extension_acl",
    "library.mca.feature_ir", "library.mca.provider_requirement_projection",
    "library.mca.reformulation_proof", "library.mca.result_acl",
    "library.mca.simulation_contract", "library.mca.trace", "library.mca.uncertainty_ir",
]
BINDER_REFS = [
    "library.bind.admission", "library.bind.constraint_ir", "library.bind.enumerator",
    "library.bind.model", "library.bind.optimizer", "library.bind.qualification",
    "library.bind.semantic", "library.bind.snapshot", "library.bind.solver_adapters",
    "library.bind.solver_spi",
]
CONFORMANCE_REFS = [
    "library.ce.identity", "library.ce.digest", "library.ce.schema", "library.ce.typecheck",
    "library.ce.law", "library.ce.oracle_spi", "library.ce.generator", "library.ce.shrinker",
    "library.ce.corpus", "library.ce.property", "library.ce.model", "library.ce.metamorphic",
    "library.ce.differential", "library.ce.golden", "library.ce.conformance", "library.ce.fuzz",
    "library.ce.mutation", "library.ce.coverage", "library.ce.chaos", "library.ce.fault",
    "library.ce.scheduler", "library.ce.security", "library.ce.crypto_vector",
    "library.ce.benchmark", "library.ce.measurement", "library.ce.statistics",
    "library.ce.numerical", "library.ce.predictive", "library.ce.accessibility",
    "library.ce.compatibility", "library.ce.replay", "library.ce.migration",
    "library.ce.restore", "library.ce.environment", "library.ce.sandbox", "library.ce.receipt",
    "library.ce.evidence", "library.ce.counterexample", "library.ce.waiver",
    "library.ce.appraisal", "library.ce.composition", "library.ce.invalidation",
    "library.ce.qualification", "library.ce.report", "library.ce.ci_adapter",
    "library.ce.target_probe", "library.ce.artifact_attestation", "library.ce.vertical_oracle",
]
CODEGEN_GENERATION_REFS = [
    "cgb.boundary.target_contract.primary", "cgb.boundary.backend_selection.primary",
    "cgb.boundary.target_feature.primary", "cgb.boundary.ir_backend_translation.primary",
    "cgb.boundary.native_codegen.primary", "cgb.boundary.wasm_core_codegen.primary",
    "cgb.boundary.wasm_component_codegen.primary", "cgb.boundary.abi_ffi.primary",
    "cgb.boundary.source_ast.primary", "cgb.boundary.source_template.primary",
    "cgb.boundary.generated_source.primary", "cgb.boundary.deterministic_format.primary",
    "cgb.boundary.source_map_debug.primary", "cgb.boundary.build_graph.primary",
    "cgb.boundary.invalidation.primary", "cgb.boundary.dependency_resolution.primary",
    "cgb.boundary.feature_resolution.primary", "cgb.boundary.toolchain_resolution.primary",
    "cgb.boundary.cargo_workspace.primary", "cgb.boundary.cargo_build_script.primary",
    "cgb.boundary.polyglot.primary", "cgb.boundary.cross_compile.primary",
    "cgb.boundary.linking.primary", "cgb.boundary.package_assembly.primary",
    "cgb.boundary.package_metadata.primary", "cgb.boundary.schema_generation.primary",
    "cgb.boundary.client_generation.primary", "cgb.boundary.database_migration.primary",
    "cgb.boundary.pipeline_manifest.primary", "cgb.boundary.config_manifest.primary",
    "cgb.boundary.infra_manifest.primary", "cgb.boundary.deployment_manifest.primary",
    "cgb.boundary.test_generation.primary", "cgb.boundary.oracle_fixture.primary",
    "cgb.boundary.documentation.primary",
]
CODEGEN_RELEASE_REFS = [
    "cgb.boundary.license.primary", "cgb.boundary.advisory.primary", "cgb.boundary.sbom.primary",
    "cgb.boundary.provenance.primary", "cgb.boundary.signing_identity.primary",
    "cgb.boundary.hermetic_build.primary", "cgb.boundary.reproducible_build.primary",
    "cgb.boundary.cache.primary", "cgb.boundary.remote_execution.primary",
    "cgb.boundary.artifact_repository.primary", "cgb.boundary.release_channel.primary",
    "cgb.boundary.rollout.primary", "cgb.boundary.rollback_artifact.primary",
    "cgb.boundary.state_rollback.primary", "cgb.boundary.decommission.primary",
    "cgb.boundary.evidence_receipt.primary",
]


def compiler_dossier() -> dict[str, Any]:
    question = "Given editioned enterprise intent and frozen registries, what closed evidence-bearing solution plan or typed refusal follows without inventing domain meaning or executing unauthorized effects?"
    users = ["enterprise_architect", "solution_engineer", "domain_model_owner", "platform_engineer", "assurance_reviewer", "release_operator"]
    harmed = ["affected_business_actor", "data_subject", "domain_owner", "source_owner", "runtime_operator", "provider_owner"]
    outcomes = ["resolved_or_refused_intent", "typed_staged_ir", "closed_requirement_offer_graph", "retained_alternatives_and_gaps", "reproducible_solution_and_artifact_plan", "scoped_proof_and_release_evidence"]
    negative = "Does not own business or industry meaning, silently create defaults, qualify providers by documentation, execute builds or deployments, authorize effects, mutate enterprise data, approve business decisions or assert vertical acceptance."
    ddd = {
        "domain_vision_statement": "Compile one exact enterprise-intent occurrence against frozen semantic, library, provider and target registries into a reproducible evidence-bearing plan, partial plan, unknown result or typed refusal.",
        "subdomain_classification": "core_differentiating_horizontal_intent_to_solution_compilation_product",
        "bounded_context_boundary": {
            "inside": ["compilation request and run identity", "input and registry snapshot binding", "source anchoring and resolution occurrences", "staged semantic IR and legality", "pass profiles and lowering traces", "requirement/offer candidate and rejection graph", "hard constraints objectives and binding results", "proof-obligation and qualification-request coordination", "target artifact build and release planning", "typed gaps diagnostics incremental invalidation and deterministic replay", "solution-plan publication and supersession"],
            "outside": ["business and industry semantic ownership", "source-system observation and data movement", "library/provider implementation behavior", "provider qualification issuance", "resource admission allocation and execution", "build/deployment effects", "business decision and effect authority", "product operations and vertical acceptance"],
        },
        "ubiquitous_language_policy": "Intent, declaration, source occurrence, registry snapshot, canonical assertion, resolution, IR stage, pass, lowering, optimization, requirement, offer, candidate, binding, qualification, proof, gap, diagnostic, solution plan, artifact plan, effect intent, receipt and acceptance are distinct terms. Domain homonyms cross an explicit ACL and no provider or product name selects meaning.",
        "context_map": [
            {"neighbor_ref": "context.domain_and_vertical_registries", "relationship": "customer_supplier_published_language", "translation": "consume exact semantic owners, editions, invariants, methods and acceptance predicates"},
            {"neighbor_ref": "context.canonical_reference_adjudication", "relationship": "anti_corruption_layer", "translation": "consume authorized directional mappings; never infer aliases from spelling"},
            {"neighbor_ref": "context.library_registry", "relationship": "open_host_service", "translation": "consume exact capability requirements, offers, laws and exclusions"},
            {"neighbor_ref": "context.provider_target_registry", "relationship": "anti_corruption_layer", "translation": "consume occurrence-scoped offers without promoting provider claims"},
            {"neighbor_ref": "component.provider_qualification", "relationship": "customer_supplier", "translation": "request exact-scope assessments and consume retained receipts"},
            {"neighbor_ref": "product.runtime_resource_control", "relationship": "customer_supplier", "translation": "emit resource demands and consume admission/allocation receipts separately"},
            {"neighbor_ref": "context.codegen_build", "relationship": "effect_port", "translation": "emit artifact/build plans; execution remains separately authorized"},
            {"neighbor_ref": "context.release_and_deployment_authority", "relationship": "effect_port", "translation": "publish candidate release plans without authorizing apply"},
            {"neighbor_ref": "context.vertical_acceptance", "relationship": "customer_supplier", "translation": "submit plan and evidence for independent domain-owner acceptance"},
        ],
        "anti_corruption_layers": ["acl.authored_intent", "acl.domain_registry", "acl.canonical_reference", "acl.library_offer", "acl.provider_target", "acl.solver_backend", "acl.proof_checker", "acl.codegen_backend", "acl.runtime_receipt", "acl.vertical_acceptance"],
        "published_language": ["CompilationId", "CompilationRequest", "InputSnapshot", "RegistrySnapshotManifest", "SourceAnchor", "ResolvedReference", "IrStage", "PassProfile", "PassReceipt", "CapabilityRequirement", "CapabilityOffer", "CandidateEdge", "BindingDecision", "ProofObligation", "CompilerGap", "Diagnostic", "SolutionPlan", "ArtifactPlan", "ReleaseEvidencePlan", "InvalidationSet", "CompilationOutcome"],
        "value_objects": ["CompilationId", "IntentEdition", "SourceAnchor", "SnapshotDigest", "RegistrySnapshotRef", "StableSemanticRef", "IrStage", "PassId", "PassProfile", "ConstraintId", "ObjectivePolicyEdition", "RequirementRef", "OfferRef", "ProofObligationRef", "DiagnosticCode", "GapCode", "PlanDigest", "InvalidationKey", "AuthorityRef", "EvidenceRef"],
        "entities": ["CompilationRun", "PassAttempt", "ResolutionOccurrence", "CandidateSolution", "BindingDecision", "ProofEvaluation", "CompilerGap", "Diagnostic", "SolutionPlanEdition", "CompilationInvalidation"],
        "aggregates": [
            {"root": "CompilationRun", "members": ["request", "input_snapshots", "pass_profile", "attempts", "stage_outputs", "decisions", "gaps", "outcome"], "consistency": "one run binds immutable inputs, registry editions and pass implementations; retries receive new attempt identities"},
            {"root": "CandidateSolution", "members": ["requirements", "candidate_edges", "rejections", "constraints", "objectives", "proof_statuses", "binding"], "consistency": "hard requirements never become preferences and every rejected alternative remains attributable"},
            {"root": "SolutionPlanEdition", "members": ["logical_plan", "physical_bindings", "artifact_plan", "effect_intents", "proofs", "residual_gaps", "publication_state"], "consistency": "publication requires one digest-bound closure whose effects remain intents rather than completed facts"},
        ],
        "aggregate_roots": ["CompilationRun", "CandidateSolution", "SolutionPlanEdition"],
        "aggregate_invariants": ["same frozen inputs editions pass implementations and decisions produce the same canonical outcome", "stable identity is distinct from edition occurrence and content digest", "domain meaning is imported only from its named semantic owner", "unknown ambiguous incompatible or unauthorised meaning produces a typed gap", "semantic lowering is distinct from proved-equivalent optimization", "hard constraints are never weakened into objectives", "feasible selected and qualified are distinct states", "a plan is not an effect intent receipt ready service or accepted outcome", "every proof and receipt is scoped to exact subjects inputs checkers environments and time", "partial unknown unsat refused cancelled and failed remain distinct", "all alternatives diagnostics assumptions decisions and invalidation supports remain attributable", "provider identity and optional automation cannot change semantics"],
        "commands": ["open_compilation", "bind_input_snapshot", "bind_registry_snapshot", "parse_declaration", "resolve_reference", "elaborate_intent", "lower_ir_stage", "adjudicate_model_class", "derive_capability_requirements", "enumerate_candidate_offers", "solve_hard_constraints", "rank_feasible_candidates", "request_qualification", "evaluate_proof_receipt", "plan_target_artifacts", "assemble_release_evidence", "publish_solution_plan", "record_compiler_gap", "cancel_compilation", "invalidate_compilation", "replay_compilation", "supersede_solution_plan"],
        "domain_events": ["compilation_opened", "input_snapshot_bound", "registry_snapshot_bound", "declaration_parsed", "reference_resolved", "intent_elaborated", "ir_stage_lowered", "model_class_adjudicated", "capability_requirements_derived", "candidate_offers_enumerated", "hard_constraints_solved", "feasible_candidates_ranked", "qualification_requested", "proof_receipt_evaluated", "target_artifacts_planned", "release_evidence_assembled", "solution_plan_published", "compiler_gap_recorded", "compilation_cancelled", "compilation_invalidated", "compilation_replayed", "solution_plan_superseded"],
        "refusal_failure_catalog": ["invalid_syntax", "unsupported_language_edition", "import_cycle", "registry_snapshot_missing", "registry_digest_mismatch", "unresolved_reference", "ambiguous_canonical_mapping", "semantic_owner_missing", "type_or_shape_mismatch", "illegal_ir_stage", "unproved_lowering", "model_class_unknown", "constraint_theory_unsupported", "hard_constraints_unsat", "solver_result_unknown", "proof_check_failed", "qualification_missing_or_stale", "target_unsupported", "artifact_plan_incomplete", "authority_missing_or_conflicting", "resource_budget_exhausted", "cancellation_requested", "incremental_clean_rebuild_mismatch", "vertical_acceptance_absent"],
        "domain_services": ["SnapshotBindingService", "CanonicalResolutionService", "IntentElaborationService", "IrLoweringService", "ModelClassAdjudicationService", "RequirementProjectionService", "BindingSolverService", "ProofCoordinationService", "ArtifactPlanningService", "ReleaseEvidenceService", "IncrementalInvalidationService", "CompilationReplayService"],
        "application_services": ["SubmitCompilationUseCase", "CompileIntentUseCase", "ExplainCompilationUseCase", "ResumeCompilationUseCase", "CancelCompilationUseCase", "RebindAfterChangeUseCase", "ReplayCompilationUseCase", "PublishSolutionPlanUseCase", "DiffSolutionPlansUseCase", "ExportCompilationEvidenceUseCase"],
        "repositories": ["CompilationRunRepository", "CandidateSolutionRepository", "SolutionPlanRepository"],
        "factories": ["CompilationRunFactory", "RegistrySnapshotManifestFactory", "CandidateSolutionFactory", "SolutionPlanFactory", "CompilerGapFactory", "DiagnosticFactory"],
        "specifications": ["CompilationInputClosureSpecification", "RegistrySnapshotIntegritySpecification", "ReferenceResolutionSpecification", "IrStageLegalitySpecification", "LoweringPreservationSpecification", "HardConstraintIntegritySpecification", "BindingEvidenceSpecification", "ProofScopeSpecification", "ArtifactPlanCompletenessSpecification", "SolutionPlanPublicationSpecification", "IncrementalEquivalenceSpecification"],
        "state_machine": {
            "states": ["draft", "snapshots_bound", "parsed", "resolution_pending", "resolved", "elaborated", "lowering", "requirements_ready", "candidate_enumeration", "constraint_solving", "qualification_pending", "artifact_planning", "plan_ready", "published", "partially_bound", "gapped", "unknown", "unsat", "refused", "cancelled", "invalidated", "superseded"],
            "transition_policy": "Only named commands with exact input editions and passed stage invariants advance the run; terminal-looking provider timeouts remain unknown until reconciled, and invalidation never rewrites historical outcomes.",
        },
        "policies_and_reactions": ["when an import or registry digest changes invalidate its exact support closure", "when a reference has no unique authorized mapping emit a gap", "when lowering changes meaning refuse unless an authorized loss or equivalence proof exists", "when hard constraints are unsatisfied retain a sufficient conflict core", "when solver status is unknown preserve partial evidence without claiming unsat", "when evidence expires revoke affected qualifications and bindings", "when an optional proposal arrives taint it until the complete deterministic path revalidates it", "when a plan is published emit no effect without separate authority"],
        "sagas_and_process_managers": ["CompilationProcess", "ReferenceAdjudicationHandoff", "BindingAndQualificationProcess", "LongRunningProofProcess", "ArtifactPlanningProcess", "IncrementalRecompilationProcess", "SolutionPlanPublicationProcess", "ProviderRebindingProcess"],
        "read_models_and_projections": ["CompilationStatusView", "SourceToIrTraceView", "RequirementOfferGraphView", "CandidateAndRejectionView", "ConstraintAndUnsatCoreView", "ProofAndQualificationView", "CompilerGapQueueView", "SolutionPlanView", "PlanSemanticDiffView", "InvalidationImpactView", "ReproducibilityView"],
        "integration_event_policy": "Only editioned snapshot bindings, stage receipts, requirements, binding decisions, gaps, diagnostics, solution plans, proof references, invalidations and supersessions cross the boundary. Domain models, provider DTOs, raw secrets, mutable runtime state, effects and acceptance decisions remain external.",
        "concurrency_and_idempotency": ["compilation commands use idempotency keys scoped to immutable request and snapshot digests", "pass attempts are append-only and receive unique identities", "parallel passes declare dependency and commutativity laws", "publication uses optimistic edition and canonical plan digest", "unknown external completion is reconciled before retry", "incremental and clean compilation must agree for the same frozen inputs"],
        "time_model": ["intent and registry validity differ from recording and retrieval time", "each evidence receipt carries validity expiry and invalidation triggers", "compilation start snapshot and publication times are distinct", "provider target quota and vulnerability evidence may expire independently", "historical runs retain the original clock inputs", "replay time never rewrites the validity interval of source evidence"],
        "event_storming_swimlanes": users + ["domain_registry_owner", "library_registry_owner", "provider_qualification_subsystem", "solver_backend", "proof_checker", "codegen_backend", "runtime_authority", "vertical_acceptance_authority"],
        "nonfunctional_laws": ["deterministic canonical output for identical frozen inputs", "finite memory work output candidate and proof budgets", "cooperative cancellation with explicit partial outcomes", "no ambient network filesystem clock randomness environment or mutable registry lookup in semantic passes", "stable diagnostic codes and source anchors", "content-addressed artifacts plus stable semantic identities", "incremental result equals clean result", "provider and backend isolation behind versioned ports", "fail-closed authority and evidence", "complete decision rejection assumption and receipt trace", "removing optional model and agent extensions preserves the deterministic compiler core"],
    }
    assert set(ddd) == DDD_FIELDS
    return {
        "dossier_id": "ddd.platform.solution_compiler", "record_kind": "product_ddd_dossier",
        "edition": 1, "product_ref": PRODUCT, "status": "candidate_not_ratified",
        "product_truth": {"sovereign_question": question, "users": users, "harmed_parties": harmed, "jobs": ["Compile exact enterprise intent into a closed reproducible solution plan, partial plan, unknown result or typed refusal while retaining every decision and proof obligation."], "measurable_outcomes": outcomes, "negative_mission": negative},
        "strategic_and_tactical_ddd": ddd,
    }


def enrich(source: dict[str, Any]) -> dict[str, Any]:
    source["sources"].extend([
        evidence("evidence.compiler.mlir", "MLIR Language Reference and Pass Infrastructure", "LLVM Project", "https://mlir.llvm.org/docs/LangRef/", "Defines extensible staged IR constructs; companion official documentation defines pass legality, preservation and failure."),
        evidence("evidence.compiler.smtlib", "SMT-LIB Standard 2.7", "SMT-LIB Initiative", "https://smt-lib.org/language.shtml", "Defines typed theories and sat, unsat and unknown result vocabulary used by exact constraint-solving adapters."),
        evidence("evidence.compiler.skyframe", "Skyframe", "Bazel Project", "https://bazel.googlesource.com/bazel/+/master/site/en/reference/skyframe.md", "Documents dependency-tracked incremental evaluation and invalidation."),
        evidence("evidence.compiler.substrait", "Substrait Specification", "Substrait Project", "https://substrait.io/spec/specification/", "Defines a versioned cross-system logical-plan representation with typed extensions and compatibility rules."),
        evidence("evidence.compiler.moi", "MathOptInterface model and optimizer attributes", "JuMP / MathOptInterface Project", "https://jump.dev/MathOptInterface.jl/stable/manual/models/", "Separates mathematical model classes, functions, sets, attributes and solver support."),
        evidence("evidence.compiler.rust_incremental", "Incremental Compilation in Detail", "Rust Project", "https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation-in-detail.html", "Documents dependency tracking, fingerprints, invalidation and incremental recomputation in a production compiler."),
        evidence("evidence.compiler.rust_codegen", "The rustc book: Codegen options and targets", "Rust Project", "https://doc.rust-lang.org/rustc/codegen-options/", "Documents exact target and code-generation decisions that must be separated from semantic lowering."),
        evidence("evidence.compiler.iso29119", "ISO/IEC/IEEE 29119 software testing series", "ISO/IEC/IEEE", "https://www.iso.org/standard/81291.html", "Defines testing concepts and processes relevant to scoped conformance evidence."),
    ])

    product = next(row for row in source["artifacts"] if row["artifact_id"] == PRODUCT)
    product.update({
        "name": "Intent-to-Solution Compiler",
        "sovereign_question": "Given editioned enterprise intent and frozen registries, what closed evidence-bearing solution plan or typed refusal follows without inventing domain meaning or executing unauthorized effects?",
        "users": ["enterprise_architect", "solution_engineer", "domain_model_owner", "platform_engineer", "assurance_reviewer", "release_operator"],
        "harmed_parties": ["affected_business_actor", "data_subject", "domain_owner", "source_owner", "runtime_operator", "provider_owner"],
        "jobs": ["bind exact input and registry snapshots", "resolve and type authored intent", "lower through legal IR stages", "derive and bind exact capability requirements", "coordinate proofs and qualifications", "produce a reproducible solution and artifact plan or typed refusal"],
        "outcomes": ["resolved_or_refused_intent", "typed_staged_ir", "closed_requirement_offer_graph", "retained_alternatives_and_gaps", "reproducible_solution_and_artifact_plan", "scoped_proof_and_release_evidence"],
        "negative_mission": "Does not own business or industry meaning, silently create defaults, qualify providers by documentation, execute builds or deployments, authorize effects, mutate enterprise data, approve business decisions or assert vertical acceptance.",
        "lifecycle_states": ["draft", "snapshots_bound", "parsed", "resolved", "elaborated", "lowering", "requirements_ready", "candidate_enumeration", "constraint_solving", "qualification_pending", "artifact_planning", "plan_ready", "published", "partially_bound", "gapped", "unknown", "unsat", "refused", "cancelled", "invalidated", "superseded"],
        "commands": ["open_compilation", "bind_input_snapshot", "bind_registry_snapshot", "parse_declaration", "resolve_reference", "lower_ir_stage", "adjudicate_model_class", "derive_capability_requirements", "solve_hard_constraints", "plan_target_artifacts", "publish_solution_plan", "record_compiler_gap", "cancel_compilation", "invalidate_compilation", "replay_compilation"],
        "events": ["compilation_opened", "input_snapshot_bound", "registry_snapshot_bound", "declaration_parsed", "reference_resolved", "ir_stage_lowered", "model_class_adjudicated", "capability_requirements_derived", "hard_constraints_solved", "target_artifacts_planned", "solution_plan_published", "compiler_gap_recorded", "compilation_cancelled", "compilation_invalidated", "compilation_replayed"],
        "invariants": ["domain meaning comes only from its semantic owner", "same frozen inputs produce the same canonical outcome", "unknown ambiguity and incompatibility are typed gaps", "lowering and optimization remain distinct", "hard constraints never become preferences", "feasible selected and qualified remain distinct", "plan is not effect or acceptance", "all alternatives decisions assumptions and evidence remain attributable"],
        "refusals": ["invalid_syntax", "registry_snapshot_missing", "unresolved_or_ambiguous_reference", "semantic_owner_missing", "illegal_ir_stage", "unproved_lowering", "model_class_unknown", "hard_constraints_unsat", "solver_result_unknown", "proof_check_failed", "qualification_missing_or_stale", "artifact_plan_incomplete", "authority_missing", "incremental_clean_rebuild_mismatch"],
        "automation_modality": AUTOMATION,
    })

    semantic_specs = [
        ("semantic.canonical_resolution", "Canonical resolution", "One source occurrence, authorized directional mapping assertion and resolution result without alias inference.", ["evidence.compiler.mlir"]),
        ("semantic.semantic_ir_lowering", "Semantic IR lowering", "Stage legality, preservation obligations, lowering results and rejected transformations.", ["evidence.compiler.mlir", "evidence.compiler.substrait"]),
        ("semantic.model_class_adjudication", "Formal model-class adjudication", "Typed feature facts, sound class facets, unknowns, refusals and provider requirements.", ["evidence.compiler.moi"]),
        ("semantic.conformance_coordination", "Conformance coordination", "Proof obligations, oracle/test requests and exact-scope evidence references without self-qualification.", ["evidence.compiler.iso29119"]),
        ("semantic.target_artifact_plan", "Target artifact plan", "Target, codegen, dependency, build and generated-artifact plan identities without executed-effect claims.", ["evidence.compiler.rust_codegen"]),
        ("semantic.release_artifact_governance", "Release artifact governance", "Supply-chain, reproducibility, release, rollback, decommission and evidence-plan requirements.", ["evidence.slsa12", "evidence.in_toto"]),
        ("semantic.incremental_compilation", "Incremental compilation", "Dependency supports, fingerprints, invalidations, replay and clean-build equivalence.", ["evidence.compiler.skyframe", "evidence.compiler.rust_incremental"]),
    ]
    capability_specs = [
        ("capability.resolve_canonical_references", "Resolve canonical references", "semantic.canonical_resolution", ["evidence.compiler.mlir"]),
        ("capability.lower_semantic_ir", "Lower semantic IR", "semantic.semantic_ir_lowering", ["evidence.compiler.mlir", "evidence.compiler.substrait"]),
        ("capability.adjudicate_model_class", "Adjudicate formal model class", "semantic.model_class_adjudication", ["evidence.compiler.moi"]),
        ("capability.coordinate_conformance", "Coordinate conformance obligations", "semantic.conformance_coordination", ["evidence.compiler.iso29119"]),
        ("capability.plan_target_artifacts", "Plan target artifacts", "semantic.target_artifact_plan", ["evidence.compiler.rust_codegen"]),
        ("capability.govern_release_artifacts", "Govern release artifact plan", "semantic.release_artifact_governance", ["evidence.slsa12", "evidence.in_toto"]),
        ("capability.invalidate_replay_compilation", "Invalidate and replay compilation", "semantic.incremental_compilation", ["evidence.compiler.skyframe", "evidence.compiler.rust_incremental"]),
    ]
    for ident, name, definition, refs in semantic_specs:
        source["artifacts"].append(artifact(ident, "semantic_contract", name, None, definition, refs))
    for ident, name, owner, refs in capability_specs:
        source["artifacts"].append(artifact(ident, "capability", name, owner, f"Typed capability owned by {owner}.", refs))

    existing = {row["library_id"]: row for row in source["libraries"]}
    for ident in {"library.platform.intent_contract", "library.platform.compiler_contract", "library.platform.binding_evidence", "library.platform.release_evidence"}:
        existing[ident]["product_refs"] = [PRODUCT]
    existing["library.platform.binding_evidence"]["dependencies"] = ["library.platform.compiler_contract", "library.platform.compiler.model_class_adjudication", "library.platform.compiler.semantic_ir_lowering"]

    source["libraries"].extend([
        library("library.platform.compiler.canonical_reference_resolution", "semantic.canonical_resolution", "capability.resolve_canonical_references", ["SourceOccurrenceRef", "MappingAssertionRef", "CanonicalRef", "ResolutionOutcome"], ["resolve_occurrence", "apply_authorized_mapping", "record_resolution"], ["mapping_edition", "homonym_policy", "unknown_mapping_policy"], ["spelling_is_not_identity", "mapping_is_directional_and_authorized", "unresolved_or_ambiguous_never_defaults"], ["source_occurrence_missing", "mapping_ambiguous", "mapping_authority_missing"], ["library.platform.intent_contract"], "pure_no_io", ["evidence.compiler.mlir"]),
        library("library.platform.compiler.semantic_ir_lowering", "semantic.semantic_ir_lowering", "capability.lower_semantic_ir", ["ResolvedIntentIr", "IrStage", "PassProfile", "LoweringTrace", "ProofObligation"], ["verify_stage", "lower_stage", "optimize_equivalent", "emit_lowering_trace"], ["stage_profile", "rewrite_policy", "authorized_loss_policy"], ["lowering_preserves_or_declares_meaning_change", "optimization_requires_equivalence", "stage_illegality_is_refused"], ["illegal_stage", "unproved_lowering", "rewrite_nontermination", "semantic_loss_unauthorized"], ["library.platform.compiler.canonical_reference_resolution"], "pure_no_io", ["evidence.compiler.mlir", "evidence.compiler.substrait"]),
        library("library.platform.compiler.model_class_adjudication", "semantic.model_class_adjudication", "capability.adjudicate_model_class", ["FormalProblemIr", "FeatureFact", "ModelClassFacet", "ClassAdjudication", "ProviderRequirement"], ["extract_feature_facts", "evaluate_class_predicates", "adjudicate_facets", "project_provider_requirements"], ["classification_profile", "unknown_fact_policy", "reformulation_policy"], ["industry_label_is_not_model_class", "class_claims_require_sound_predicates", "unknown_facets_do_not_default"], ["problem_boundary_unclosed", "feature_fact_unknown", "class_predicate_unproved", "reformulation_loss_unknown"], ["library.platform.compiler.semantic_ir_lowering"], "pure_no_io", ["evidence.compiler.moi"]),
        library("library.platform.compiler.conformance_coordination", "semantic.conformance_coordination", "capability.coordinate_conformance", ["ProofObligation", "OracleRequirement", "TestPopulation", "AssessmentRequest", "EvidenceRef"], ["derive_proof_obligations", "plan_oracle_execution", "evaluate_receipt_scope", "retain_counterexample"], ["evidence_ladder", "independence_policy", "waiver_policy", "invalidation_policy"], ["schema_valid_is_not_qualified", "test_pass_is_exact_scope_only", "waiver_is_not_pass"], ["oracle_missing", "population_undefined", "receipt_scope_mismatch", "counterexample_unresolved"], ["library.platform.binding_evidence", "library.platform.compiler.model_class_adjudication"], "pure_effect_intents", ["evidence.compiler.iso29119"], "assurance_boundary"),
        library("library.platform.compiler.target_artifact_generation", "semantic.target_artifact_plan", "capability.plan_target_artifacts", ["TargetContract", "BackendRequirement", "BuildGraph", "DependencyLock", "ArtifactPlan"], ["select_backend_requirements", "plan_generation", "plan_build_graph", "plan_package_and_manifests"], ["target_profile", "toolchain_policy", "dependency_resolution_policy", "generation_profile"], ["semantic_lowering_is_not_codegen", "template_is_not_generated_artifact", "package_is_not_deployment"], ["target_unsupported", "backend_unqualified", "dependency_resolution_unknown", "artifact_plan_incomplete"], ["library.platform.compiler.semantic_ir_lowering", "library.platform.compiler.conformance_coordination"], "pure_effect_intents", ["evidence.compiler.rust_codegen"]),
        library("library.platform.compiler.release_artifact_governance", "semantic.release_artifact_governance", "capability.govern_release_artifacts", ["SupplyChainPlan", "SbomRequirement", "ProvenanceRequirement", "ReleasePlan", "RollbackPlan", "DecommissionPlan"], ["plan_supply_chain_evidence", "plan_release", "plan_rollback_or_rollforward", "plan_decommission"], ["license_policy", "advisory_policy", "reproducibility_policy", "release_authority_policy"], ["signature_is_not_truth", "reproducible_bits_are_not_semantic_conformance", "artifact_rollback_is_not_state_rollback"], ["supply_chain_evidence_incomplete", "release_authority_missing", "rollback_semantics_unknown", "decommission_obligations_unresolved"], ["library.platform.compiler.target_artifact_generation", "library.platform.release_evidence"], "pure_effect_intents", ["evidence.slsa12", "evidence.in_toto"], "assurance_boundary"),
        library("library.platform.compiler.incremental_trace", "semantic.incremental_compilation", "capability.invalidate_replay_compilation", ["QueryKey", "SupportSet", "Fingerprint", "InvalidationSet", "CompilationTrace"], ["record_support", "compute_dirty_closure", "invalidate", "replay", "compare_clean_result"], ["fingerprint_profile", "change_policy", "cache_trust_policy"], ["cache_hit_is_not_correctness", "historical_trace_is_append_only", "incremental_equals_clean_for_same_inputs"], ["support_set_incomplete", "fingerprint_mismatch", "cache_namespace_untrusted", "incremental_clean_mismatch"], ["library.platform.compiler.semantic_ir_lowering", "library.platform.binding_evidence"], "pure_no_io", ["evidence.compiler.skyframe", "evidence.compiler.rust_incremental"]),
    ])

    new_requirements = [
        ("resolve_canonical_references", "capability.resolve_canonical_references", "canonical_resolution_unbound"),
        ("lower_semantic_ir", "capability.lower_semantic_ir", "semantic_lowering_unbound"),
        ("adjudicate_model_class", "capability.adjudicate_model_class", "model_class_adjudication_unbound"),
        ("coordinate_conformance", "capability.coordinate_conformance", "conformance_coordination_unbound"),
        ("plan_target_artifacts", "capability.plan_target_artifacts", "target_artifact_planning_unbound"),
        ("govern_release_artifacts", "capability.govern_release_artifacts", "release_artifact_governance_unbound"),
        ("invalidate_replay_compilation", "capability.invalidate_replay_compilation", "incremental_compilation_unbound"),
    ]
    source["requirements"].extend({
        "requirement_id": f"requirement.platform.compiler.{key}", "consumer_ref": PRODUCT,
        "capability_ref": capability, "binding_phase": "compile_time",
        "minimum_qualified_offers": 1, "status": "unbound", "refusal": refusal,
    } for key, capability, refusal in new_requirements)

    central_origins = {ref: CENTRAL_REGISTRY for row in source["binding_maps"] for ref in row["concrete_library_refs"]}
    for row in source["binding_maps"]:
        row["concrete_library_origins"] = {ref: central_origins[ref] for ref in row["concrete_library_refs"]}
    map_by_lib = {row["abstract_library_ref"]: row for row in source["binding_maps"]}

    def replace_map(local: str, refs: list[str], origins: dict[str, str]) -> None:
        row = map_by_lib[local]
        row.update({"concrete_library_refs": refs, "concrete_library_origins": origins, "compiler_disposition": "structurally_projected_unqualified", "gap_ref": None, "product_refs": [PRODUCT]})

    replace_map("library.platform.intent_contract", ["library.csp.intent.intent-vocabulary", "library.csp.intent.intent-conformance"], origin_map(["library.csp.intent.intent-vocabulary", "library.csp.intent.intent-conformance"], CENTRAL_REGISTRY))
    compiler_refs = ["library.impl.san-compiler-api", "library.impl.san-ir-core", "library.impl.san-module-graph", "library.impl.san-pass-contract", "library.impl.san-pass-engine"]
    replace_map("library.platform.compiler_contract", compiler_refs, origin_map(compiler_refs, IMPLEMENTATION_REGISTRY))
    replace_map("library.platform.binding_evidence", BINDER_REFS, origin_map(BINDER_REFS, BINDER_REGISTRY))
    release_refs = ["library.lpe.evidence-bundle", "library.lpe.evidence-evaluation"]
    replace_map("library.platform.release_evidence", release_refs, origin_map(release_refs, CENTRAL_REGISTRY))

    new_maps = [
        ("canonical_reference_resolution", "library.platform.compiler.canonical_reference_resolution", ["library.impl.san-canonical-reference", "library.impl.san-declaration", "library.impl.san-identity", "library.impl.san-source-model", "library.impl.san-syntax", "library.impl.san-type-checker"], IMPLEMENTATION_REGISTRY),
        ("semantic_ir_lowering", "library.platform.compiler.semantic_ir_lowering", IR_REFS, IR_REGISTRY),
        ("model_class_adjudication", "library.platform.compiler.model_class_adjudication", MCA_REFS, MCA_REGISTRY),
        ("conformance_coordination", "library.platform.compiler.conformance_coordination", CONFORMANCE_REFS, CONFORMANCE_REGISTRY),
        ("target_artifact_generation", "library.platform.compiler.target_artifact_generation", CODEGEN_GENERATION_REFS, CODEGEN_REGISTRY),
        ("release_artifact_governance", "library.platform.compiler.release_artifact_governance", CODEGEN_RELEASE_REFS, CODEGEN_REGISTRY),
    ]
    for key, local, refs, registry in new_maps:
        source["binding_maps"].append({
            "binding_map_id": f"binding.platform.compiler.{key}",
            "abstract_library_ref": local, "concrete_library_refs": refs,
            "concrete_library_origins": origin_map(refs, registry),
            "compiler_disposition": "structurally_projected_unqualified",
            "gap_ref": None, "portable_offer": False, "product_refs": [PRODUCT],
        })
    incremental_refs = ["library.ir.incremental", "library.bind.invalidation", "library.bind.trace", "library.impl.san-diagnostics", "library.impl.san-incremental"]
    incremental_origins = {
        "library.ir.incremental": IR_REGISTRY,
        "library.bind.invalidation": BINDER_REGISTRY,
        "library.bind.trace": BINDER_REGISTRY,
        "library.impl.san-diagnostics": IMPLEMENTATION_REGISTRY,
        "library.impl.san-incremental": IMPLEMENTATION_REGISTRY,
    }
    source["binding_maps"].append({
        "binding_map_id": "binding.platform.compiler.incremental_trace",
        "abstract_library_ref": "library.platform.compiler.incremental_trace",
        "concrete_library_refs": incremental_refs,
        "concrete_library_origins": incremental_origins,
        "compiler_disposition": "structurally_projected_unqualified", "gap_ref": None,
        "portable_offer": False, "product_refs": [PRODUCT],
    })

    source["ddd_dossiers"] = [compiler_dossier()]
    source["non_collapse_laws"].extend([
        "declaration syntax != resolved domain meaning != staged IR != physical plan",
        "semantic lowering != proved-equivalent optimization != target code generation",
        "formal problem statement != model-class facet != algorithm requirement != provider offer",
        "structural candidate != semantic compatibility != feasibility != preference != qualification",
        "compiler gap != unsat != unknown != refusal != execution failure",
        "compiled solution plan != build execution != deployment effect != ready service != vertical acceptance",
        "incremental cache hit != clean-build equivalence proof",
    ])
    source["negative_tests"].extend([
        {"test_id": "negative.compiler.domain_owner", "prohibited_claim": "The compiler may define a missing business or industry meaning.", "expected_result": "emit semantic_owner_missing gap"},
        {"test_id": "negative.compiler.name_binding", "prohibited_claim": "A matching provider or library name proves compatibility.", "expected_result": "require directional semantic and evidence checks"},
        {"test_id": "negative.compiler.lowering_optimization", "prohibited_claim": "A cheaper physical form is a valid lowering without equivalence evidence.", "expected_result": "refuse unproved meaning change"},
        {"test_id": "negative.compiler.hard_soft", "prohibited_claim": "An infeasible hard requirement may become a weighted preference.", "expected_result": "retain hard constraint and emit unsat or unknown"},
        {"test_id": "negative.compiler.plan_acceptance", "prohibited_claim": "A published solution plan proves a deployed accepted solution.", "expected_result": "require separate effects receipts and vertical acceptance"},
        {"test_id": "negative.compiler.agent_completion", "prohibited_claim": "An agent-generated architecture closes missing DDD qualification or acceptance evidence.", "expected_result": "retain typed proposal taint and all missing deterministic obligations"},
    ])
    return source
