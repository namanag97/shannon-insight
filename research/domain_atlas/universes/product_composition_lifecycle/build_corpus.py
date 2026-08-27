#!/usr/bin/env python3
"""Build the provider-neutral product-composition environment lifecycle corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


SOURCES = [
    {"source_id": "source.product_composition.kubernetes.controllers", "title": "Kubernetes Controllers", "publisher": "Kubernetes Project", "url": "https://kubernetes.io/docs/concepts/architecture/controller/", "source_kind": "official_documentation", "claim_scope": "desired/observed control-loop pattern and separation of controllers", "scope_limit": "Does not define product capability closure, business readiness, rollback safety or exit completeness."},
    {"source_id": "source.product_composition.kubernetes.objects", "title": "Objects in Kubernetes", "publisher": "Kubernetes Project", "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/", "source_kind": "official_documentation", "claim_scope": "declarative spec/status and versioned object identity", "scope_limit": "Kubernetes object behavior is implementation evidence, not universal product semantics."},
    {"source_id": "source.product_composition.crossplane.compositions", "title": "Crossplane Compositions", "publisher": "Crossplane Project", "url": "https://docs.crossplane.io/latest/composition/compositions/", "source_kind": "official_documentation", "claim_scope": "composite APIs, composed resources, observed/desired function pipelines and capability advertisement", "scope_limit": "Crossplane composition does not establish provider qualification or application acceptance."},
    {"source_id": "source.product_composition.crossplane.resources", "title": "Crossplane Composite Resources", "publisher": "Crossplane Project", "url": "https://docs.crossplane.io/latest/composition/composite-resources/", "source_kind": "official_documentation", "claim_scope": "composition selection and readiness conditions for composed resources", "scope_limit": "A Ready condition is framework-scoped and cannot prove arbitrary business or cross-component readiness."},
    {"source_id": "source.product_composition.opengitops.principles", "title": "OpenGitOps Principles v1.0.0", "publisher": "OpenGitOps / CNCF", "url": "https://opengitops.dev/", "source_kind": "open_specification", "claim_scope": "declarative, versioned/immutable, pulled and continuously reconciled desired state", "scope_limit": "GitOps principles do not define capability solving, migration safety or exit acceptance."},
    {"source_id": "source.product_composition.argo.rollouts", "title": "Argo Rollouts", "publisher": "Argo Project", "url": "https://argoproj.github.io/rollouts/", "source_kind": "official_documentation", "claim_scope": "blue-green/canary rollout, analysis, promotion and rollback mechanisms", "scope_limit": "Metrics-based mechanism does not own product readiness criteria or prove rollback reversibility."},
    {"source_id": "source.product_composition.cncf.platforms", "title": "CNCF Platforms White Paper", "publisher": "Cloud Native Computing Foundation", "url": "https://tag-app-delivery.cncf.io/whitepapers/platforms/", "source_kind": "official_whitepaper", "claim_scope": "platform capability composition, interfaces and product-like platform experience", "scope_limit": "Industry guidance is not a conformance standard or provider qualification receipt."},
]


CONTEXTS = [
    {"context_id": "context.product_composition.declaration", "name": "Product composition declaration", "sovereign_question": "Which editioned product profile and component requirements constitute one desired environment?", "inside": ["environment identity", "profile edition", "component slots", "required and optional capabilities", "constraints", "dependency graph"], "outside": ["component semantic definitions", "provider selection", "runtime reconciliation"], "owner": "authority.product_composition", "status": "specified_candidate"},
    {"context_id": "context.product_composition.capability_closure", "name": "Capability closure and binding", "sovereign_question": "Do exact qualified component offers close every required capability and compatibility obligation?", "inside": ["requirements", "offers", "binding precedence", "compatibility", "qualification validity", "closure residuals"], "outside": ["provider qualification execution", "component implementation", "commercial purchase"], "owner": "authority.product_composition", "status": "specified_candidate"},
    {"context_id": "context.product_composition.environment_reconciliation", "name": "Environment reconciliation and readiness", "sovereign_question": "How is desired composition compared with observed occurrences and classified as ready, drifting, degraded or refused?", "inside": ["desired cut", "observed cut", "generation", "drift", "readiness premises", "reconcile intents", "receipts"], "outside": ["provider API execution", "component-local health meaning", "business acceptance"], "owner": "authority.product_composition", "status": "specified_candidate"},
    {"context_id": "context.product_composition.change_exit", "name": "Composition rollout, rollback and exit", "sovereign_question": "How may an environment edition change or exit while dispositions, irreversible boundaries and evidence remain explicit?", "inside": ["semantic diff", "blast radius", "rollout", "rollback", "roll-forward", "in-flight disposition", "exit plan", "residual obligations"], "outside": ["effect authorization", "provider execution", "data migration semantics owned by components", "acceptance authority"], "owner": "authority.product_composition", "status": "specified_candidate"},
]


DECISIONS = [
    ("profile_selection", "Which product profile and edition define the environment?"),
    ("component_identity", "Which component identities and semantic editions are required?"),
    ("binding_precedence", "How are multiple structurally eligible offers ordered without provider-name semantics?"),
    ("capability_closure", "Must closure be exact, at-least, or explicitly residual-bearing?"),
    ("qualification_posture", "Which qualification scopes, freshness and independence gates are mandatory?"),
    ("desired_observed_comparison", "Which identity, grain, time and generation rules govern comparison?"),
    ("drift_policy", "Which differences are benign, actionable, blocking or unknown?"),
    ("readiness_policy", "Which component and cross-component premises constitute environment readiness?"),
    ("rollout_policy", "Which change strategy, stages, budgets and promotion gates apply?"),
    ("rollback_policy", "When is rollback eligible, impossible, or weaker than roll-forward?"),
    ("irreversibility_policy", "Which effects require precharge, authority, backup or compensation before change?"),
    ("exit_policy", "Which export, migration, decommission, destruction and residual-obligation evidence closes exit?"),
]


DECISION_ROWS = [
    {"decision_id": f"decision.product_composition.environment.{slug}", "owner_context": "context.product_composition.environment_reconciliation", "question": question, "default": None, "default_law": "forbidden", "status": "declared"}
    for slug, question in DECISIONS
]


ERRORS = ["InvalidDeclaration", "ProfileUnresolved", "CapabilityGap", "BindingAmbiguous", "SemanticEditionConflict", "OfferUnqualified", "EvidenceExpired", "ObservedGenerationStale", "DriftUnknown", "ReadinessUnproved", "RolloutUnsafe", "RollbackUnavailable", "IrreversibleBoundaryUnapproved", "ExitIncomplete", "ResidualObligationUnowned", "ResourceExhausted", "UnsupportedCapability"]


OPERATIONS = [
    {"operation_ref": "operation.product_composition.environment.type_environment", "input_types": ["EnvironmentDeclaration"], "output_type": "Result<TypedEnvironment,EnvironmentLifecycleRefusal>", "purity": "pure"},
    {"operation_ref": "operation.product_composition.environment.resolve_capability_closure", "input_types": ["CapabilityClosureInput"], "output_type": "Result<CapabilityClosure,EnvironmentLifecycleRefusal>", "purity": "pure"},
    {"operation_ref": "operation.product_composition.environment.compare_desired_observed", "input_types": ["EnvironmentComparisonInput"], "output_type": "Result<EnvironmentDiff,EnvironmentLifecycleRefusal>", "purity": "pure"},
    {"operation_ref": "operation.product_composition.environment.classify_drift", "input_types": ["DriftClassificationInput"], "output_type": "Result<DriftSet,EnvironmentLifecycleRefusal>", "purity": "pure"},
    {"operation_ref": "operation.product_composition.environment.evaluate_readiness", "input_types": ["ReadinessEvaluationInput"], "output_type": "Result<ReadinessVerdict,EnvironmentLifecycleRefusal>", "purity": "pure"},
    {"operation_ref": "operation.product_composition.environment.plan_rollout", "input_types": ["RolloutPlanningInput"], "output_type": "Result<RolloutPlan,EnvironmentLifecycleRefusal>", "purity": "pure", "effect_intent_type": "RolloutStageIntent"},
    {"operation_ref": "operation.product_composition.environment.plan_rollback", "input_types": ["RollbackPlanningInput"], "output_type": "Result<RollbackPlan,EnvironmentLifecycleRefusal>", "purity": "pure", "effect_intent_type": "RollbackStageIntent"},
    {"operation_ref": "operation.product_composition.environment.plan_exit", "input_types": ["ExitPlanningInput"], "output_type": "Result<ExitPlan,EnvironmentLifecycleRefusal>", "purity": "pure", "effect_intent_type": "ExitStageIntent"},
]


PUBLIC_TYPES = ["EnvironmentId", "EnvironmentEdition", "ProductProfileId", "ProductProfileEdition", "ComponentSlotId", "ComponentRequirement", "ComponentOfferRef", "BindingDecision", "CapabilityClosureInput", "CapabilityClosure", "ClosureResidual", "EnvironmentDeclaration", "TypedEnvironment", "DesiredEnvironmentState", "ObservedEnvironmentState", "ObservedGeneration", "EnvironmentComparisonInput", "EnvironmentDiff", "DriftClassificationInput", "DriftItem", "DriftSet", "ReadinessEvaluationInput", "ReadinessPremise", "ReadinessVerdict", "RolloutPlanningInput", "RolloutStage", "RolloutPlan", "RollbackPlanningInput", "RollbackEligibility", "RollbackPlan", "ExitPlanningInput", "ExitDisposition", "ExitPlan", "ResidualObligation", "EnvironmentLifecycleRefusal"]


LAWS = [
    "A product composition packages component contracts but never acquires their semantic ownership.",
    "Desired state, observed state, last-applied state and accepted state are distinct immutable cuts.",
    "A documented capability claim is not a qualified offer, and a set of offers is not capability closure until every exact requirement and compatibility edge is solved.",
    "Component readiness does not imply environment readiness; cross-component premises, dependencies and evidence freshness must close.",
    "Drift is a classified difference, not automatically a failure, repair instruction or authorization.",
    "Provider names, deployment topology and UI packaging cannot select product semantics or hidden defaults.",
    "A rollout plan is not execution, promotion, acceptance or evidence that the new edition is safe.",
    "Rollback is not assumed reversible; schema, data, authority and external effects may require roll-forward, compensation or refusal.",
    "Deletion is not exit completion; export, migration, in-flight work, decommission, destruction and residual obligations have separate dispositions.",
    "No model or agent may qualify an offer, waive a gap, approve an irreversible boundary, promote a rollout or accept exit evidence.",
]


LIBRARY = {
    "library_id": "library.product_composition.environment_lifecycle",
    "name": "Product Composition Environment Lifecycle",
    "library_kind": "policy_pure",
    "semantic_owner_context": "context.product_composition.environment_reconciliation",
    "status": "specified",
    "candidate_responsibility": "declarative product-profile composition, exact capability closure, desired/observed comparison, drift, readiness, rollout, rollback and exit planning without absorbing component semantics",
    "effect_boundary": "pure_effect_intents",
    "public_types": PUBLIC_TYPES,
    "public_traits": ["EnvironmentLifecycleAlgebra", "CapabilityClosureSolver", "EnvironmentChangePlanner"],
    "operation_refs": [row["operation_ref"] for row in OPERATIONS],
    "operations": OPERATIONS,
    "decision_refs": [row["decision_id"] for row in DECISION_ROWS],
    "configuration_contracts": ["EnvironmentLifecyclePolicy", "ReadinessPolicy", "RolloutPolicy", "RollbackPolicy", "ExitPolicy"],
    "laws": LAWS,
    "invariants": ["published environment editions are immutable", "every component binding names exact requirement, offer, semantic edition, target and qualification evidence", "observations bind occurrence, generation, observer and observation time", "every irreversible step has prior authority and a declared fallback", "every active occurrence and residual obligation receives exactly one exit disposition"],
    "error_contracts": ERRORS,
    "dependencies": ["library.runtime-resource.provider-adapter-spi", "library.runtime-resource.runtime-receipts", "library.cp.connector_lifecycle"],
    "evidence_refs": [row["source_id"] for row in SOURCES],
    "oracles": ["capability-closure model tests", "desired/observed generation and drift properties", "readiness negative twins", "rollout/rollback state-machine exploration", "irreversible-change counterexamples", "exit-disposition completeness", "two unrelated product profiles"],
    "gaps": ["No execution controller or provider adapter is qualified by this pure contract.", "Two independent implementations and executed acceptance in a lakehouse and an unrelated enterprise product remain required."],
    "must_not_own": ["component domain meaning", "provider qualification authority", "runtime execution", "business acceptance", "commercial contracting", "credential custody"],
    "qualification_required": False,
}


NEGATIVE_TWINS = [
    ("ready_components_ready_environment", "All components report ready, therefore the environment is ready.", "Require cross-component dependency, compatibility and evidence-freshness premises."),
    ("desired_is_observed", "The desired manifest proves the deployed state.", "Compare against occurrence-scoped observations and generations."),
    ("documented_is_qualified", "Provider documentation satisfies a capability requirement.", "Require an exact offer and current scoped qualification receipts."),
    ("drift_is_repair", "Any drift authorizes automatic reconciliation.", "Classify drift and require action authority and safety evidence."),
    ("rollback_is_reverse", "Reapplying the old declaration reverses every effect.", "Account for irreversible data, schema, authority and external effects."),
    ("delete_is_exit", "Deleting the control object completes supplier exit.", "Disposition exports, migrations, occurrences, in-flight work, destruction and residual obligations."),
    ("provider_selects_profile", "A provider name implies the product profile and defaults.", "Bind provider-neutral requirements before any offer selection."),
    ("composition_owns_components", "The product composition may redefine component semantics.", "Import published contracts through explicit ownership-preserving edges."),
]


NEGATIVE_ROWS = [{"negative_id": f"negative.product_composition.{slug}", "unsafe_inference": unsafe, "required_behavior": required, "status": "active"} for slug, unsafe, required in NEGATIVE_TWINS]


COMPILER_ROWS = [
    {"record_kind": "capability_requirement", "requirement_id": "requirement.product_composition.environment_lifecycle", "subject_ref": LIBRARY["library_id"], "required_operations": LIBRARY["operation_refs"], "required_decisions": LIBRARY["decision_refs"], "fallback_law": "refuse", "status": "declared"},
    {"record_kind": "capability_offer", "offer_id": "offer.product_composition.environment_lifecycle.reference", "subject_ref": LIBRARY["library_id"], "claimed_operations": LIBRARY["operation_refs"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
    {"record_kind": "binding_rule", "binding_rule_id": "binding.product_composition.environment_lifecycle", "requirement_ref": "requirement.product_composition.environment_lifecycle", "offer_ref": "offer.product_composition.environment_lifecycle.reference", "structural_match": True, "selection_law": "Structural match never promotes an unqualified or non-portable offer.", "selectable": False, "status": "declared"},
]


FILES = {
    "sources.jsonl": SOURCES,
    "bounded-contexts.jsonl": CONTEXTS,
    "decision-points.jsonl": DECISION_ROWS,
    "library-contracts.jsonl": [LIBRARY],
    "compiler-contracts.jsonl": COMPILER_ROWS,
    "negative-twins.jsonl": NEGATIVE_ROWS,
}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = lines(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {"manifest_id": "product_composition_lifecycle_v0_1_0", "as_of": AS_OF, "edition": EDITION, "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False, "qualified_implementation_count": 0}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS product composition lifecycle: {len(SOURCES)} sources, {len(CONTEXTS)} contexts, {len(DECISION_ROWS)} decisions, 1 exact library, {len(COMPILER_ROWS)} compiler contracts")


if __name__ == "__main__":
    main()
