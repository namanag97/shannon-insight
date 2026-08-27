"""Constitutional boundary between compilation and broader solution synthesis."""

ARCHITECTURE = {
    "architecture_id": "architecture.solution_synthesis_assurance.v1",
    "kind": "ARCHITECTURE_PATTERN_NOT_PRODUCT",
    "status": "PROPOSED_UNRATIFIED",
    "sovereign_question": "For each enterprise requirement, which bounded mechanism may resolve it, which authority owns any remaining decision, and what exact blueprint or residual follows without pretending the whole world is mechanically compilable?",
    "compiler_promise": "Transform sufficiently explicit, ratified intent against frozen registries into a reproducible solution blueprint, or return a complete typed actionable account of why closure is impossible.",
    "non_promise": "Does not infer universal business meaning, manufacture authority or evidence, guarantee physical effects or outcomes, or treat open-world discovery as a closed-world compile.",
}

COMPONENTS = [
    ("deterministic-compiler-kernel", "Deterministic Compiler Kernel", "Transforms exact declarations through typed IR stages; checks legality, closure and reproducibility; emits a blueprint or typed residuals.", ["compile", "typecheck", "lower", "prove_structural_closure"], ["business_meaning", "physical_effect", "provider_qualification"]),
    ("constraint-planner-synthesizer", "Constraint Planner and Synthesizer", "Enumerates and compares feasible candidates under declared hard constraints, objectives and finite budgets.", ["enumerate", "solve", "rank_declared_objectives", "retain_alternatives"], ["objective_authority", "risk_appetite", "business_approval"]),
    ("authority-adjudication-workbench", "Authority and Judgment Adjudication Workbench", "Routes unresolved choices, exceptions and semantic disputes to named owners and records decisions with scope and evidence.", ["request_decision", "record_decision", "challenge", "ratify_or_reject"], ["invent_authority", "silent_default", "effect_execution"]),
    ("desired-state-reconciler", "Desired-State Reconciler and Operators", "Interprets an authorized immutable blueprint, converges physical state, reconciles unknown effects and emits receipts.", ["plan_apply", "provision", "configure", "observe", "retry", "rollback", "decommission"], ["semantic_compilation", "business_approval", "outcome_claim"]),
    ("assurance-appraisal-system", "Assurance, Qualification and Appraisal System", "Evaluates exact-scope conformance, operational, security, performance, exit and vertical-acceptance evidence independently of compilation.", ["derive_obligation", "execute_oracle", "qualify", "appraise", "invalidate"], ["self_qualification", "unbounded_truth_claim", "effect_execution"]),
    ("ontology-research-extension", "Open-World Ontology Research Extension", "Detects unknown concepts or absent boundaries, creates falsifiable research/adjudication packages and resumes synthesis only after governed extension.", ["detect_unknown", "open_research_case", "propose_contract", "request_ratification"], ["automatic_ontology_mutation", "name_based_alias", "premature_product_promotion"]),
]

MODES = [
    ("closed-world-compilation", "All required meanings, contracts, policies, implementations and evidence are present and ratified.", "deterministic-compiler-kernel", "compiled_solution_or_typed_refusal"),
    ("interactive-synthesis", "Several legal alternatives exist or an owned judgment, tradeoff, exception or authorization is required.", "authority-adjudication-workbench", "partial_plan_plus_exact_decision_requests"),
    ("open-world-discovery", "A required concept, lifecycle, product seam, contract, provider fact or acceptance predicate is absent from governed registries.", "ontology-research-extension", "research_adjudication_package_plus_suspended_compilation"),
]

IR_STAGES = [
    ("business-intent-ir", "BusinessIntentIR", "outcomes users harms non-goals assumptions constraints SLOs budget and acceptance intent", "business_owner"),
    ("semantic-intent-ir", "SemanticIntentIR", "exact vocabulary identities grain time authority partiality and evidence meanings", "semantic_owners"),
    ("product-composition-ir", "ProductCompositionIR", "operated lifecycle owners adoption units neighbor boundaries and product requirements", "product_boundary_authorities"),
    ("capability-requirement-ir", "CapabilityRequirementIR", "typed required behaviors guarantees resources and binding phases", "capability_contract_owners"),
    ("contract-graph-ir", "ContractGraphIR", "exact types operations decisions invariants refusals dependencies and substitution laws", "library_contract_owners"),
    ("application-behavior-ir", "ApplicationBehaviorIR", "actors commands queries aggregate transitions policies sagas human tasks and decision points", "application_domain_owners"),
    ("logical-dataflow-ir", "LogicalDataflowIR", "sources admissions transformations state analytics publications and delivery topology", "data_product_owners"),
    ("authority-effect-ir", "AuthorityEffectIR", "proposal decision authorization effect intent execution receipt outcome and revocation chain", "authority_and_effect_owners"),
    ("physical-binding-ir", "PhysicalBindingIR", "exact implementation provider occurrence estate region resource and qualification bindings", "platform_and_provider_qualifiers"),
    ("deployment-blueprint-ir", "DeploymentBlueprintIR", "immutable desired physical state rollout rollback migration recovery and decommission plan", "deployment_authority"),
    ("evidence-acceptance-ir", "EvidenceAcceptanceIR", "proof obligations receipts appraisal scopes invalidations and vertical acceptance gates", "independent_assurance_and_vertical_owners"),
]

TRANSFORMS = [
    ("business-to-semantic", "business-intent-ir", "semantic-intent-ir", "semantic_elaboration", "semantic_owner_missing"),
    ("semantic-to-products", "semantic-intent-ir", "product-composition-ir", "product_boundary_resolution", "product_boundary_unresolved"),
    ("products-to-capabilities", "product-composition-ir", "capability-requirement-ir", "capability_projection", "capability_requirement_incomplete"),
    ("capabilities-to-contracts", "capability-requirement-ir", "contract-graph-ir", "exact_contract_resolution", "exact_contract_unratified"),
    ("semantic-to-application", "semantic-intent-ir", "application-behavior-ir", "domain_behavior_elaboration", "application_decision_unowned"),
    ("contracts-to-dataflow", "contract-graph-ir", "logical-dataflow-ir", "logical_composition", "dataflow_closure_failed"),
    ("application-to-authority-effect", "application-behavior-ir", "authority-effect-ir", "authority_effect_projection", "authority_or_effect_owner_missing"),
    ("logical-to-physical", "logical-dataflow-ir", "physical-binding-ir", "qualified_binding", "qualified_offer_missing"),
    ("authority-into-physical", "authority-effect-ir", "physical-binding-ir", "effect_port_binding", "effect_port_unauthorized"),
    ("physical-to-blueprint", "physical-binding-ir", "deployment-blueprint-ir", "desired_state_planning", "estate_or_resource_binding_missing"),
    ("blueprint-to-evidence", "deployment-blueprint-ir", "evidence-acceptance-ir", "acceptance_obligation_projection", "acceptance_evidence_missing"),
]

FRONTIER_CLASSES = [
    ("mechanically-compilable", "Exact deterministic transformation with complete inputs and executable laws.", "deterministic-compiler-kernel"),
    ("constraint-synthesizable", "Finite legal alternatives can be searched under supplied constraints and objectives.", "constraint-planner-synthesizer"),
    ("authority-or-judgment-required", "A choice changes meaning, risk, rights, tradeoffs or authorization and requires a named owner.", "authority-adjudication-workbench"),
    ("physical-or-evidence-required", "Closure depends on an implementation, provider occurrence, build, effect receipt, qualification or vertical acceptance.", "assurance-appraisal-system"),
    ("open-world-extension-required", "The governed ontology lacks the required concept, boundary, contract or decision vocabulary.", "ontology-research-extension"),
]

BINDING_PHASES = [
    ("authoring", ["outcome", "vertical_vocabulary", "non_goal", "acceptance_intent"]),
    ("compile", ["semantic_owner", "product_boundary", "contract", "policy", "logical_plan"]),
    ("qualification", ["implementation_occurrence", "provider_offer", "conformance_scope"]),
    ("deployment", ["estate", "tenant", "account", "region", "resource", "credential_reference"]),
    ("runtime", ["admission", "routing", "retry", "failover", "human_approval", "effect_attempt"]),
    ("post-runtime", ["reconciliation", "appraisal", "outcome_evaluation", "invalidation"]),
    ("change", ["migration", "requalification", "rollback", "retirement", "historical_replay"]),
]

LAWS = [
    ("compiler-not-universal-authority", "compiler output != business truth or authority"),
    ("compiler-not-reconciler", "compiled blueprint != applied physical state"),
    ("product-not-library-sum", "product lifecycle owner != sum of required libraries"),
    ("plan-not-effect", "solution plan != effect intent != execution receipt != outcome"),
    ("open-not-closed-world", "unknown concept != unsupported known construct != invalid declaration"),
    ("feasible-not-selected", "feasible candidate != selected candidate != qualified binding"),
    ("evidence-not-meaning", "conformance evidence != semantic ownership or universal fitness"),
    ("runtime-not-definition", "runtime observation may invalidate but never silently rewrite declared meaning"),
    ("partial-is-successful-outcome", "typed partial plan with exact residuals is a legitimate synthesis outcome"),
    ("no-hidden-binding-phase", "every exposed decision has one explicit earliest binding phase and later override law"),
    ("no-name-join", "spelling or provider name never selects semantic identity implementation or authority"),
    ("extension-is-governed", "ontology extension requires evidence challenge owner decision edition and invalidation scope"),
]

OUTCOMES = [
    ("compiled-solution", ["blueprint", "bindings", "assumptions", "decisions", "evidence", "acceptance_requirements"], "All required gates are closed for the exact scope; deployment remains separately authorized."),
    ("incomplete-solution", ["resolved_graph", "valid_partial_plan", "missing_decisions", "missing_authorities", "missing_contracts", "missing_implementations", "missing_evidence", "next_actions"], "At least one gate remains open; no silent default or effect is permitted."),
]
