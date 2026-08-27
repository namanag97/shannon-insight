"""Constitutional boundary between compilation and broader solution synthesis."""

ARCHITECTURE = {
    "architecture_id": "architecture.solution_synthesis_assurance.v1",
    "kind": "ARCHITECTURE_PATTERN_NOT_PRODUCT",
    "status": "PROPOSED_UNRATIFIED",
    "sovereign_question": "For each enterprise requirement, which bounded mechanism may resolve it, which authority owns any remaining decision, and what exact blueprint or residual follows without pretending the whole world is mechanically compilable?",
    "compiler_promise": "Transform sufficiently explicit, ratified intent against frozen registries into a reproducible solution blueprint, or return a complete typed actionable account of why closure is impossible.",
    "non_promise": "Does not infer universal business meaning, manufacture authority or evidence, guarantee physical effects or outcomes, or treat open-world discovery as a closed-world compile.",
    "corpus_router_ref": "research/product_ontology/corpus_architecture_router/manifest.json",
    "corpus_routing_law": "Every governed research file has one explicit package route into a bounded mechanism, IR transition, resolution frontier, binding phase and authority; record occurrence routing does not confer semantic authority.",
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
    ("domain-context-ir", "DomainContextIR", "bounded contexts vocabulary identities aggregates workflows invariants refusals and neighboring authorities", "domain_and_context_owners"),
    ("semantic-intent-ir", "SemanticIntentIR", "exact vocabulary identities grain time authority partiality and evidence meanings", "semantic_owners"),
    ("source-estate-requirement-ir", "SourceEstateRequirementIR", "logical source systems records observations cuts cursors change modes completeness finality and acquisition obligations without selecting an occurrence", "source_and_data_contract_owners"),
    ("analytical-design-ir", "AnalyticalDesignIR", "question decision study population measures dimensions estimand method assumptions uncertainty alternatives and result semantics", "analytical_practice_and_method_owners"),
    ("product-composition-ir", "ProductCompositionIR", "operated lifecycle owners adoption units neighbor boundaries and product requirements", "product_boundary_authorities"),
    ("capability-requirement-ir", "CapabilityRequirementIR", "typed required behaviors guarantees resources and binding phases", "capability_contract_owners"),
    ("contract-graph-ir", "ContractGraphIR", "exact types operations decisions invariants refusals dependencies and substitution laws", "library_contract_owners"),
    ("application-behavior-ir", "ApplicationBehaviorIR", "actors commands queries aggregate transitions policies sagas human tasks and decision points", "application_domain_owners"),
    ("logical-dataflow-ir", "LogicalDataflowIR", "sources admissions transformations state analytics publications and delivery topology", "data_product_owners"),
    ("experience-delivery-ir", "ExperienceDeliveryIR", "audiences question and result kinds semantic presentation visual encodings interactions documents notifications accessibility disclosure and delivery contracts", "experience_presentation_and_disclosure_owners"),
    ("authority-effect-ir", "AuthorityEffectIR", "proposal decision authorization effect intent execution receipt outcome and revocation chain", "authority_and_effect_owners"),
    ("implementation-offer-ir", "ImplementationOfferIR", "exact implementation artifact provider offer target compatibility configuration exclusion and evidence-claim identities", "implementation_and_provider_offer_owners"),
    ("qualification-evidence-ir", "QualificationEvidenceIR", "exact-scope executable law operational portability security performance and independent-appraisal receipts needed before selection", "independent_implementation_qualifiers"),
    ("physical-binding-ir", "PhysicalBindingIR", "exact implementation provider occurrence estate region resource and qualification bindings", "platform_and_provider_qualifiers"),
    ("deployment-blueprint-ir", "DeploymentBlueprintIR", "immutable desired physical state rollout rollback migration recovery and decommission plan", "deployment_authority"),
    ("evidence-acceptance-ir", "EvidenceAcceptanceIR", "proof obligations receipts appraisal scopes invalidations and vertical acceptance gates", "independent_assurance_and_vertical_owners"),
]

TRANSFORMS = [
    ("business-to-domain", "business-intent-ir", "domain-context-ir", "bounded_context_elaboration", "domain_boundary_or_owner_missing"),
    ("domain-to-semantic", "domain-context-ir", "semantic-intent-ir", "semantic_elaboration", "semantic_owner_missing"),
    ("semantic-to-source-estate", "semantic-intent-ir", "source-estate-requirement-ir", "source_requirement_elaboration", "source_authority_or_cut_semantics_missing"),
    ("semantic-to-analytical-design", "semantic-intent-ir", "analytical-design-ir", "analytical_question_and_study_elaboration", "analytical_design_or_method_assumption_missing"),
    ("semantic-to-products", "semantic-intent-ir", "product-composition-ir", "product_boundary_resolution", "product_boundary_unresolved"),
    ("products-to-capabilities", "product-composition-ir", "capability-requirement-ir", "capability_projection", "capability_requirement_incomplete"),
    ("analytical-design-to-capabilities", "analytical-design-ir", "capability-requirement-ir", "analytical_capability_projection", "analytical_capability_requirement_incomplete"),
    ("capabilities-to-contracts", "capability-requirement-ir", "contract-graph-ir", "exact_contract_resolution", "exact_contract_unratified"),
    ("domain-to-application", "domain-context-ir", "application-behavior-ir", "domain_behavior_elaboration", "application_decision_unowned"),
    ("source-estate-to-dataflow", "source-estate-requirement-ir", "logical-dataflow-ir", "source_admission_and_cut_planning", "source_or_cut_closure_failed"),
    ("analytical-design-to-dataflow", "analytical-design-ir", "logical-dataflow-ir", "analytical_execution_topology", "analytical_execution_closure_failed"),
    ("contracts-to-dataflow", "contract-graph-ir", "logical-dataflow-ir", "logical_composition", "dataflow_closure_failed"),
    ("analytical-design-to-experience", "analytical-design-ir", "experience-delivery-ir", "result_presentation_elaboration", "result_or_presentation_semantics_missing"),
    ("application-to-experience", "application-behavior-ir", "experience-delivery-ir", "interaction_and_human_task_elaboration", "interaction_or_human_task_contract_missing"),
    ("application-to-authority-effect", "application-behavior-ir", "authority-effect-ir", "authority_effect_projection", "authority_or_effect_owner_missing"),
    ("contracts-to-implementation-offers", "contract-graph-ir", "implementation-offer-ir", "frozen_registry_candidate_enumeration", "exact_implementation_offer_missing"),
    ("offers-to-qualification-evidence", "implementation-offer-ir", "qualification-evidence-ir", "exact_scope_conformance_and_independent_appraisal", "qualification_evidence_missing_or_stale"),
    ("logical-to-physical", "logical-dataflow-ir", "physical-binding-ir", "qualified_binding", "qualified_offer_missing"),
    ("experience-to-physical", "experience-delivery-ir", "physical-binding-ir", "delivery_target_binding", "qualified_delivery_or_activation_target_missing"),
    ("authority-into-physical", "authority-effect-ir", "physical-binding-ir", "effect_port_binding", "effect_port_unauthorized"),
    ("qualification-into-physical", "qualification-evidence-ir", "physical-binding-ir", "qualification_gate", "qualification_scope_mismatch_or_missing"),
    ("physical-to-blueprint", "physical-binding-ir", "deployment-blueprint-ir", "desired_state_planning", "estate_or_resource_binding_missing"),
    ("blueprint-to-evidence", "deployment-blueprint-ir", "evidence-acceptance-ir", "acceptance_obligation_projection", "acceptance_evidence_missing"),
]

# A transform edge is not sufficient proof that an output IR is complete.  These
# are the explicit hypergraph joins required before the named IR may close.
IR_JOIN_RULES = [
    ("semantic-closure", "semantic-intent-ir", ["domain-context-ir"], "All reused terms, identities and rules resolve to one scoped authority or an explicit conflict."),
    ("analytical-design-closure", "analytical-design-ir", ["business-intent-ir", "semantic-intent-ir"], "The analytical question, study design, method assumptions, output status and decision use are jointly closed."),
    ("capability-closure", "capability-requirement-ir", ["product-composition-ir", "analytical-design-ir", "application-behavior-ir", "source-estate-requirement-ir"], "Capabilities cover operated product promises, analytics, application behavior and data acquisition without collapsing those owners."),
    ("contract-closure", "contract-graph-ir", ["semantic-intent-ir", "capability-requirement-ir"], "Every required behavior has exact types, laws, decisions, refusals, ports and substitution constraints."),
    ("logical-dataflow-closure", "logical-dataflow-ir", ["source-estate-requirement-ir", "analytical-design-ir", "contract-graph-ir"], "Source cuts, transformations, state, analytical execution and publication topology agree at grain, time and authority boundaries."),
    ("experience-closure", "experience-delivery-ir", ["semantic-intent-ir", "analytical-design-ir", "application-behavior-ir"], "Presentation preserves result semantics and exposes the correct human actions, uncertainty, disclosure and accessibility behavior."),
    ("qualification-closure", "qualification-evidence-ir", ["contract-graph-ir", "implementation-offer-ir"], "Qualification receipts bind the exact contract, artifact, target occurrence, configuration, test domain, checker and independence claim."),
    ("physical-binding-closure", "physical-binding-ir", ["logical-dataflow-ir", "experience-delivery-ir", "authority-effect-ir", "product-composition-ir", "implementation-offer-ir", "qualification-evidence-ir"], "Implementations, source occurrences, providers, targets and delivery channels are exact-scope qualified; authority remains separate."),
    ("blueprint-closure", "deployment-blueprint-ir", ["physical-binding-ir", "product-composition-ir"], "Desired state includes operations, rollout, recovery, migration, exit and acceptance obligations for every selected product promise."),
    ("acceptance-closure", "evidence-acceptance-ir", ["deployment-blueprint-ir", "qualification-evidence-ir", "product-composition-ir"], "Product and unrelated-vertical acceptance appraise the complete blueprint without being reused as pre-binding implementation qualification."),
]

# Orthogonal universes used to test whether the corpus covers an entire data and
# analytics solution.  A plane is a coverage coordinate, not automatically a
# product, bounded context, crate, compiler pass, or deployment unit.
DATA_ANALYTICS_PLANES = [
    ("business-domain", "Business and Vertical Domain Meaning", "Industry vocabulary, business lifecycles, decisions, authority and acceptance meaning.", ["research/domain_atlas/industries/"], ["domain-context-ir", "semantic-intent-ir"]),
    ("application-behavior", "Application Behavior and Human Work", "Commands, queries, aggregates, workflows, cases, policies, approvals, projections and effect handoffs.", ["research/domain_atlas/universes/application_behavior/", "research/domain_atlas/universes/human_work_review_adjudication/"], ["application-behavior-ir", "authority-effect-ir"]),
    ("source-acquisition", "Source Estate and Acquisition", "Source-system classes and occurrences, connectors, protocols, observations, instruments, cursors, cuts and finality.", ["research/domain_atlas/universes/source_systems/", "research/domain_atlas/universes/source_occurrence_catalog/", "research/domain_atlas/universes/connectors_protocols/", "research/domain_atlas/universes/measurement_acquisition_calibration/"], ["source-estate-requirement-ir", "logical-dataflow-ir"]),
    ("data-semantics-contracts", "Data Types, Semantics and Contracts", "Shapes, carriers, semantic values, identity, grain, time, units, schemas, mappings and data contracts.", ["research/domain_atlas/universes/data_shapes/", "research/domain_atlas/universes/core_semantic_primitives/", "research/domain_atlas/universes/schema_data_contract_governance/", "research/domain_atlas/universes/schema_mapping_translation/"], ["semantic-intent-ir", "contract-graph-ir"]),
    ("movement-transformation", "Movement, Dataflow and Transformation", "CDC, ingestion, messaging, pipelines, orchestration, transformation builds, incremental state and activation mapping.", ["research/domain_atlas/universes/pipeline_dataflow/", "research/domain_atlas/universes/transformation_build_semantics/", "research/domain_atlas/universes/messaging_channels/", "research/domain_atlas/universes/operational_activation_mapping/"], ["contract-graph-ir", "logical-dataflow-ir"]),
    ("persistence-representation", "Persistence, Lakehouse and Representation", "Storage state, tables, transactions, files, objects, indexes, layouts, formats, encodings, compression, protection and recovery.", ["research/domain_atlas/universes/persistence_lakehouse/", "research/domain_atlas/universes/encoding_compression/"], ["contract-graph-ir", "physical-binding-ir"]),
    ("compute-query-runtime", "Compute, Query and Runtime Control", "Query semantics, kernels, scheduling, jobs, resources, concurrency, backpressure, quotas, leases, failure and recovery.", ["research/domain_atlas/universes/query_compute_kernels/", "research/domain_atlas/universes/runtime_compute_resource/"], ["capability-requirement-ir", "physical-binding-ir"]),
    ("governance-trust", "Governance, Quality, Lineage, Security and Trust", "Metadata, vocabulary, master/reference data, policy, privacy, lineage, quality, reconciliation, evidence and assurance.", ["research/domain_atlas/universes/governance_metadata_ontology_mdm/", "research/domain_atlas/universes/quality_observability_reconciliation/", "research/domain_atlas/universes/lineage_provenance_evidence/", "research/domain_atlas/universes/security_privacy_trust/"], ["semantic-intent-ir", "evidence-acceptance-ir"]),
    ("analytics-methods", "Analytical Questions, Studies and Methods", "Descriptive, diagnostic, predictive, causal, process, graph, spatial, optimization, simulation, experimental and other formal methods.", ["research/domain_atlas/universes/analytics_types/", "research/domain_atlas/universes/method_kernels/", "research/domain_atlas/universes/operations_research/", "research/domain_atlas/universes/predictive_ml_models/"], ["analytical-design-ir", "logical-dataflow-ir"]),
    ("semantic-metrics", "Semantic Metrics and Formula Evaluation", "Measures, dimensions, metrics, formulas, targets, benchmarks, semantic queries and evaluation equivalence.", ["research/domain_atlas/universes/semantic_metrics_formulas/"], ["semantic-intent-ir", "analytical-design-ir"]),
    ("experience-presentation", "Analytical Experience and Presentation", "Question/result kinds, BI, visualization, interaction, documents, alerts, accessibility, disclosure, delivery and activation.", ["research/domain_atlas/universes/consumption_bi_visualization/", "research/domain_atlas/universes/addressable_content_rendition/"], ["experience-delivery-ir", "physical-binding-ir"]),
    ("decision-activation", "Decision, Authorization and Operational Activation", "Proposal, appraisal, approval, authorized decision, effect intent, execution receipt, outcome and feedback.", ["research/domain_atlas/universes/operational_activation_mapping/", "research/domain_atlas/universes/human_work_review_adjudication/"], ["authority-effect-ir", "evidence-acceptance-ir"]),
    ("product-operations", "Product, Estate and Commercial Operations", "Adoption promises, product lifecycles, composition, tenancy, administration, support, cost, exit and decommissioning.", ["research/product_ontology/", "research/domain_atlas/universes/product_composition_lifecycle/", "research/domain_atlas/universes/platform_commercial_support/"], ["product-composition-ir", "deployment-blueprint-ir"]),
    ("implementation-provider", "Implementations, Providers and Targets", "Library implementations, provider offers, target occurrences, ABI/layout/resource requirements and replaceability seams.", ["research/domain_atlas/compiler/provider_target_registry/", "research/domain_atlas/compiler/implementation_architecture/"], ["implementation-offer-ir", "qualification-evidence-ir", "physical-binding-ir"]),
    ("synthesis-assurance", "Synthesis, Qualification and Change", "Intent resolution, constraint planning, binding, code generation, conformance, vertical acceptance, rollout, drift, invalidation and research extension.", ["research/domain_atlas/compiler/", "research/product_ontology/qualification_program/"], ["deployment-blueprint-ir", "evidence-acceptance-ir"]),
]

# Python is the reproducible corpus workbench.  These roles prevent research
# generators from being mistaken for the eventual typed domain libraries or
# production runtime.
PYTHON_TOOLCHAIN_ROLES = [
    ("evidence-collector", "May access external sources and emit immutable, provenance-bound raw snapshots; it never writes canonical semantic decisions.", "network_isolated_from_canonical_build", ["raw_evidence_snapshot"]),
    ("authored-corpus-source", "Holds reviewable candidate facts and declarations. JSONL/YAML is preferred; Python source-model literals are transitional authoring, not runtime truth.", "schema_and_owner_review_required", ["authored_candidate_record"]),
    ("canonical-builder", "Purely projects declared inputs into normalized deterministic artifacts and manifests.", "no_network_clock_random_or_silent_defaults", ["derived_projection", "canonical_candidate_contract"]),
    ("validator", "Checks schemas, identities, references, invariants, negative twins, freshness and fail-closed gates without promoting authority.", "read_only_except_disposable_temp_output", ["validation_report"]),
    ("router-indexer", "Builds reverse indexes, support sets, corpus routes and gap/work queues; indexes never become semantic authority.", "derived_and_rebuildable", ["derived_index", "typed_gap_queue"]),
    ("execution-harness", "Executes exact oracles or reference implementations in a finite declared environment and retains occurrence-scoped receipts.", "effects_confined_to_declared_run_directory", ["execution_receipt"]),
    ("build-orchestrator", "Executes the declared package DAG, checks immutable snapshots versus live projections, and proves clean-build equivalence.", "cannot_infer_dependencies_from_names", ["build_receipt", "semantic_diff"]),
    ("prototype-solver", "Tests compiler, planner, binder or reconciliation semantics against fixtures; it is not a qualified production implementation.", "candidate_only_until_independently_qualified", ["prototype_plan", "typed_refusal"]),
    ("reference-runtime-implementation", "May implement an exact contract for conformance and portability campaigns, but remains separate from the corpus and from provider qualification.", "exact_contract_and_occurrence_evidence_required", ["implementation_artifact", "execution_receipt"]),
]

ARTIFACT_CLASSES = [
    ("raw-evidence-snapshot", "Observed external material with retrieval provenance and digest; immutable after capture.", "evidence-collector", "OBSERVED_NOT_AUTHORITY", "immutable"),
    ("authored-candidate-record", "Human/research-authored proposed fact, boundary, rule or vocabulary record.", "authored-corpus-source", "PROPOSED_UNRATIFIED", "editioned"),
    ("authority-decision", "Named owner decision with scope, precedence, evidence and invalidation triggers.", "authority-adjudication-workbench", "RATIFIED_FOR_EXACT_SCOPE", "append_only_supersession"),
    ("canonical-candidate-contract", "Exact contract projected from ratified inputs; validity does not imply implementation.", "canonical-builder", "CONTRACT_VALID_ONLY", "content_addressed_edition"),
    ("derived-projection", "Rebuildable normalization, matrix, route, index, queue or summary.", "canonical-builder", "NO_INDEPENDENT_AUTHORITY", "replaceable_rebuild"),
    ("implementation-artifact", "Code or binary claiming an exact contract and build identity.", "reference-runtime-implementation", "UNQUALIFIED_UNTIL_EVIDENCED", "content_addressed_edition"),
    ("execution-receipt", "Occurrence-scoped observation from an executable oracle or implementation run.", "execution-harness", "EVIDENCE_NOT_QUALIFICATION", "immutable"),
    ("qualification-appraisal-receipt", "Independent exact-scope verdict over implementation, target, configuration and test domain.", "assurance-appraisal-system", "QUALIFIED_ONLY_FOR_RECORDED_SCOPE", "append_only_with_revocation"),
    ("solution-blueprint", "Immutable synthesis result containing bindings, assumptions, decisions, residuals, operations and acceptance obligations.", "deterministic-compiler-kernel", "PLAN_NOT_EFFECT", "content_addressed_edition"),
    ("runtime-observation", "Observed application, data, resource, effect or outcome state used for reconciliation and invalidation.", "desired-state-reconciler", "OBSERVATION_NOT_DEFINITION", "append_only_corrections"),
    ("historical-snapshot", "Frozen prior-edition research or accounting baseline whose literal cardinalities are part of its identity.", "build-orchestrator", "HISTORICAL_NOT_LIVE_CANONICAL", "immutable"),
]

BUILD_POLICIES = [
    ("snapshot-vs-live", "Historical snapshots validate exact frozen counts and digests; live projections derive counts from declared current inputs."),
    ("source-vs-generated", "Every package declares authored inputs, generated outputs, builder, validator, authority status and regeneration boundary."),
    ("no-semantic-policy-in-plumbing", "Generic Python plumbing may canonicalize, route and validate; semantic defaults and ownership decisions must be explicit governed records."),
    ("declared-dependency-dag", "Build dependencies and input digests are declared; filesystem discovery may detect drift but cannot silently admit a semantic source."),
    ("clean-build-equivalence", "A topological rebuild from a clean checkout must be byte-identical to checked-in derived artifacts for the same snapshots."),
    ("support-set-invalidation", "Every derived decision, binding and receipt exposes the exact inputs whose change invalidates it."),
    ("effect-isolation", "Research generation is pure; collectors, execution harnesses and reconcilers have separate declared effect boundaries."),
    ("language-boundary", "JSONL/schema records are the interchange contract; Python is the research/build workbench and Rust may implement typed compiler and runtime libraries without becoming semantic authority."),
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
