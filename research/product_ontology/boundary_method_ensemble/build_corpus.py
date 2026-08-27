#!/usr/bin/env python3
"""Build a multi-method ensemble for discovering and falsifying product/domain seams."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"


def encode(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def S(ident: str, title: str, owner: str, uri: str, scope: str, limit: str) -> dict:
    return {"source_id":f"source.boundary-method.{ident}","title":title,"owner":owner,"uri":uri,"claim_scope":scope,"scope_limit":limit}


SOURCES = [
    S("evans-ddd","Domain-Driven Design Reference","Eric Evans","https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf","models, bounded contexts, context maps, aggregates, modules and conceptual contours","DDD does not by itself define product-market, operational, economic or physical boundaries."),
    S("eventstorming","EventStorming","Alberto Brandolini","https://www.eventstorming.com/","collaborative discovery of flows, events, policies, hotspots and candidate boundaries","Workshop clusters are hypotheses, not ratified boundaries."),
    S("domain-storytelling","Domain Storytelling Quick Start","Hofer and Schwentner","https://domainstorytelling.org/quick-start-guide","actor-work-object stories and important scenario variants","Stories reveal work and language but do not prove consistency, product or provider boundaries."),
    S("wardley","Wardley Mapping Introduction","Simon Wardley community","https://learnwardleymapping.com/introduction/","user-anchored value chains, dependency and evolution stages","Strategic position and market evolution do not establish semantic ownership."),
    S("bizbok","Business Architecture capability principles","Business Architecture Guild","https://www.businessarchitectureguild.org/resource/resmgr/baguild_gov_ref_model_worksh.pdf","capabilities as stable what-not-how views related to value streams, information, organization, products and policy","A capability map is not a process, bounded-context or deployable-product map."),
    S("togaf-archimate","TOGAF and ArchiMate","The Open Group","https://www.opengroup.org/togaf","enterprise architecture method and cross-layer business, application, data and technology representation","Architecture views classify and relate an estate but do not prove local domain semantics or transaction boundaries."),
    S("bpmn-cmmn-dmn","BPMN, CMMN and DMN","Object Management Group","https://www.omg.org/intro/TripleCrown.pdf","prescriptive process, adaptive case and decision/rule models","Notation conformance does not prove organizational adoption, product value or complete observed behavior."),
    S("process-mining","Process Mining Manifesto","IEEE Task Force on Process Mining","https://www.tf-pm.org/resources/manifesto","event-log discovery, conformance and enhancement of operational processes","An event log is observation-limited; discovered behavior does not by itself define policy or authority."),
    S("data-products","Designing Data Products","Thoughtworks","https://martinfowler.com/articles/designing-data-products.html","use-case-backward product discovery, independent value, ownership, SLOs and reuse across cases","Guidance concerns analytical data products and does not make every table, topic or application a product."),
    S("team-topologies","Organization Dynamics with Team Topologies","Skelton and Pais","https://teamtopologies.com/s/Organization-Dynamics-with-Team-Topologies-Mini-book-MB80.pdf","stream alignment, cognitive load, service interactions and thinnest viable platforms","Team feasibility and flow inform boundaries but cannot override language and authority."),
    S("service-blueprint","Service Blueprinting","Nielsen Norman Group","https://www.nngroup.com/courses/service-design/","customer actions, frontstage, backstage and support orchestration","Experience maps do not prove semantic or consistency boundaries."),
    S("foda","Feature-Oriented Domain Analysis Feasibility Study","Carnegie Mellon SEI","https://www.sei.cmu.edu/library/feature-oriented-domain-analysis-foda-feasibility-study/","domain commonality and variability for systematic reuse","A feature is not automatically a product, bounded context, runtime toggle or library."),
    S("sysml","SysML v2","Object Management Group","https://www.omg.org/sysml/sysmlv2/","requirements, behavior, structure, analysis, verification and traceability for complex systems","A system allocation is not automatically a DDD or commercial product boundary."),
    S("c4","C4 Model","Simon Brown","https://c4model.com/","software system, container, component, code and deployment views","C4 describes software structure and communication; it does not discover domain meaning or product value."),
    S("owl","OWL 2 Primer","W3C","https://www.w3.org/TR/owl-primer/","formal knowledge representation, axioms, entities, expressions and reasoning","Ontology entailment is not workflow, validation, source truth or product ownership."),
    S("shacl","Shapes Constraint Language","W3C","https://www.w3.org/TR/shacl/","graph-shape constraints and validation reports","SHACL conformance is not ontology consistency, completeness or real-world truth."),
    S("iso704","ISO 704:2022","ISO","https://www.iso.org/standard/79077.html","terminology work among objects, concepts, definitions and designations","The public abstract supports terminology scope only; it does not provide the paywalled normative details."),
    S("alloy","Alloy: A Language and Tool for Exploring Software Designs","MIT CSAIL","https://groups.csail.mit.edu/sdg/pubs/2019/alloy-cacm-18-feb-22-2019.pdf","finite relational structure, constraints, simulation and counterexample search","Bounded model checking cannot prove an unbounded domain or product-market fit."),
    S("tla","TLA+","TLA+ project","https://github.com/tlaplus","specification and verification of reactive and concurrent systems","Formal state behavior does not discover user value, vocabulary or evidence authority."),
    S("stpa","STPA Handbook","MIT Partnership for Systems Approaches to Safety and Security","https://psas.scripts.mit.edu/home/books-and-handbooks/","losses, hazards, control structures, unsafe control actions, scenarios and constraints","Safety analysis is one mandatory lens where harm exists; it does not replace domain or product discovery."),
    S("nist-sse","NIST SP 800-160 Vol. 1 Rev. 1","NIST","https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final","trustworthy secure systems engineering across the lifecycle","Security trust boundaries do not automatically coincide with products or bounded contexts."),
    S("sre-slo","Service Level Objectives","Google SRE","https://sre.google/sre-book/service-level-objectives/","user-relevant indicators, objectives and error budgets","SLOs demonstrate an operated promise but do not establish semantics or independent value."),
    S("arc42","arc42 Template Overview","arc42","https://docs.arc42.org/","architecture goals, constraints, context, building blocks, runtime, deployment, decisions, quality and risks","Documentation structure is not a boundary-discovery proof."),
    S("context-mapper","Context Mapper","Context Mapper","https://contextmapper.org/","DDD context maps and service decomposition as code","Tool syntax records a model but does not ratify its boundaries."),
]


def M(ident: str, family: str, name: str, question: str, outputs: list[str], evidence: list[str], blind: str, sources: list[str]) -> dict:
    return {"method_id":f"method.{ident}","family":family,"name":name,"primary_question":question,"outputs":outputs,"seam_evidence_for":evidence,"not_proof_of":blind,"source_refs":[f"source.boundary-method.{s}" for s in sources],"status":"applicable_lens"}


METHODS = [
    # Strategy and portfolio landscape
    M("strategy.wardley","strategy_landscape","Wardley Mapping","What user-anchored value chain exists, what depends on what, and how evolved is each component?",["value_chain","evolution_map","make_buy_partner_hypotheses"],["product","provider","capability","investment"],"semantic or consistency boundaries",["wardley"]),
    M("strategy.business_model_canvas","strategy_landscape","Business Model Canvas","How does an organization create, deliver and capture value?",["customer_segments","value_propositions","channels","partners","cost_revenue_model"],["product","suite","economics"],"domain invariants or runtime architecture",[]),
    M("strategy.value_chain","strategy_landscape","Porter Value Chain Analysis","Which primary and support activities create margin or strategic advantage?",["activity_system","cost_and_differentiation_hypotheses"],["subdomain","product","investment"],"bounded contexts or process truth",[]),
    M("strategy.capability_heatmap","strategy_landscape","Capability Heat Mapping","Where is strategic importance, maturity, pain, duplication or investment need concentrated?",["capability_scores","investment_map"],["capability","portfolio"],"product or semantic boundaries",["bizbok"]),
    M("strategy.application_estate","strategy_landscape","Application Estate / Portfolio Mapping","Which applications, owners, technologies, costs, lifecycle stages, integrations and redundancies exist?",["application_inventory","integration_map","TIME_or_6R_dispositions"],["migration","provider","physical_system"],"future domain ownership or product identity",["togaf-archimate"]),
    M("strategy.impact_mapping","strategy_landscape","Impact Mapping","Which actor behavior changes connect a goal to candidate deliverables?",["goal_actor_impact_deliverable_graph"],["product","outcome","experiment"],"domain model or implementation seam",[]),
    M("strategy.systems_thinking","strategy_landscape","Systems Thinking / Causal Loop Mapping","Which reinforcing, balancing, delayed and emergent feedback structures shape outcomes?",["causal_loop_model","leverage_points"],["policy","system_boundary","measurement"],"causal identification or software boundary",[]),
    M("strategy.soft_systems","strategy_landscape","Soft Systems Methodology","How do conflicting stakeholder worldviews define and transform a messy problem situation?",["rich_picture","root_definitions","conceptual_activity_models"],["domain","stakeholder","boundary_candidate"],"one objective true model",[]),
    M("strategy.cynefin","strategy_landscape","Cynefin Sense-Making","Is the situation clear, complicated, complex, chaotic or confused, and what decision posture fits?",["context_classification","action_posture"],["research_method","operating_posture"],"product or semantic seam",[]),

    # Business architecture, customer and product
    M("business.capability_map","business_product","Business Capability Mapping","What stable abilities must the enterprise possess, independent of how and who?",["capability_hierarchy","capability_definitions","cross_maps"],["capability","portfolio"],"process, product, bounded context or implementation",["bizbok"]),
    M("business.value_stream","business_product","Business Value Stream Mapping","What end-to-end stages create value for a stakeholder?",["value_stream","value_items","stakeholders"],["product","subdomain","handoff"],"detailed process control flow",["bizbok"]),
    M("business.jtbd","business_product","Jobs to Be Done","What progress is a user trying to make in a circumstance and what alternatives compete?",["job_statement","forces","outcome_expectations"],["product","user","outcome"],"domain semantics or technical architecture",[]),
    M("business.opportunity_tree","business_product","Opportunity Solution Tree","How do outcomes, opportunities, solutions and experiments relate?",["outcome_opportunity_solution_experiment_tree"],["product","experiment","roadmap"],"bounded context or stable library seam",[]),
    M("business.service_blueprint","business_product","Service Blueprinting","How do customer actions, frontstage, backstage, support processes and evidence deliver one service?",["service_blueprint","fail_points","handoffs"],["product","experience","operation"],"semantic ownership or atomic consistency",["service-blueprint"]),
    M("business.customer_journey","business_product","Customer Journey Mapping","What does a user do, think, feel and experience across touchpoints and time?",["journey","moments_of_truth","pain_points"],["experience","product","channel"],"backstage architecture or domain truth",["service-blueprint"]),
    M("business.data_product_backward","business_product","Use-case-backward Data Product Design","What smallest independently valuable analytical data promise serves a use case and generalizes across more cases?",["data_product_candidates","ports","owner","SLOs"],["data_product","adoption","interface"],"all platform products or semantic contexts",["data-products"]),
    M("business.product_split_merge","business_product","Evidence-carrying Product Split/Merge Adjudication","Does a candidate have distinct users, outcomes, adoption, semantics, authority, lifecycle, operation, economics, interfaces and alternatives?",["coordinate_evidence","bounded_verdict","residual_gaps"],["product","suite","capability"],"implementation qualification or market success",[]),

    # Domain knowledge discovery
    M("domain.ddd","domain_semantics","Domain-Driven Design","Which models express core domain rules in code and where is each model valid?",["ubiquitous_language","bounded_contexts","context_map","tactical_model"],["bounded_context","aggregate","semantic_owner","module"],"product, market, operation or physical deployment",["evans-ddd"]),
    M("domain.eventstorming","domain_semantics","EventStorming","What happened, why, by whose command, under which policy, using which read model and external system?",["event_timeline","commands","policies","actors","hotspots","boundary_candidates"],["process","aggregate_candidate","bounded_context_candidate"],"ratified boundary or complete exception behavior",["eventstorming"]),
    M("domain.storytelling","domain_semantics","Domain Storytelling","Who does what with which work objects in important concrete scenarios?",["actor_activity_work_object_stories","scenario_variants"],["language","workflow","context_candidate"],"formal state, product or consistency proof",["domain-storytelling"]),
    M("domain.example_mapping","domain_semantics","Example Mapping / Specification by Example","Which rules and concrete examples or open questions define a behavior?",["rules","examples","questions"],["invariant","refusal","acceptance_oracle"],"whole-domain or product completeness",[]),
    M("domain.context_mapping","domain_semantics","DDD Context Mapping","How do model owners influence, translate, conform, isolate or publish contracts to one another?",["context_relationships","ACLs","published_languages"],["bounded_context","translation","authority"],"runtime topology or product adoption",["evans-ddd","context-mapper"]),
    M("domain.conceptual_contours","domain_semantics","Conceptual Contours / Volatility Analysis","Which concepts form whole cohesive units and shear along observed axes of change and stability?",["cohesive_modules","change_axes","split_merge_hypotheses"],["library","module","bounded_context"],"independent product value",["evans-ddd"]),
    M("domain.terminology","domain_semantics","Terminology Work","Which objects, concepts, characteristics, definitions and designations exist in each scope and language?",["concept_system","definitions","designations","relations"],["vocabulary","semantic_identity","homonym_boundary"],"formal ontology entailment, process or product",["iso704"]),
    M("domain.ethnography","domain_semantics","Contextual Inquiry / Ethnography","What work actually occurs in context, including tacit practices, artifacts and workarounds?",["field_observations","task_models","breakdowns"],["domain","workflow","product","exception"],"statistical representativeness or formal correctness",[]),

    # Process, case and decision
    M("work.bpmn","work_behavior","BPMN","What prescriptive activities, actors, messages, events, gateways and compensation form a process?",["process_model","message_choreography"],["workflow","orchestration","handoff"],"adaptive case behavior or rule semantics",["bpmn-cmmn-dmn"]),
    M("work.cmmn","work_behavior","CMMN","How does knowledge work evolve around a case file under events, discretion and milestones?",["case_model","case_file","stages","sentries","milestones"],["case","human_judgment","lifecycle"],"fully ordered process or decision logic",["bpmn-cmmn-dmn"]),
    M("work.dmn","work_behavior","DMN","Which input data, knowledge sources and decisions form a decision requirements graph and executable logic?",["decision_requirements_graph","decision_tables","FEEL_logic"],["decision","rule","policy"],"workflow, authority to decide or business outcome",["bpmn-cmmn-dmn"]),
    M("work.value_stream_map","work_behavior","Lean Value Stream Mapping","Where do material/information flow, wait, work, inventory, rework and lead time occur?",["current_future_state_map","flow_metrics","waste_hypotheses"],["process","operation","bottleneck"],"semantic or product ownership",[]),
    M("work.process_mining","work_behavior","Process Mining","What behavior is observed in event/object data and how does it conform to or extend a model?",["discovered_model","conformance_result","performance_overlay"],["process","exception","bottleneck","boundary_falsifier"],"policy intent, complete population, causality or authority",["process-mining"]),
    M("work.petrii","work_behavior","Petri Nets / Workflow Nets","What concurrency, synchronization, choice, reachability, liveness and deadlock properties exist?",["formal_process_net","reachability_or_soundness_result"],["state_machine","concurrency","aggregate_or_saga"],"user value or domain vocabulary",[]),
    M("work.statecharts","work_behavior","Statecharts / State Machines","What legal states, transitions, guards, hierarchy and orthogonal regions govern an entity or process?",["state_machine","transition_table","illegal_transition_oracles"],["aggregate","lifecycle","protocol"],"product or context boundary by itself",[]),
    M("work.theory_constraints","work_behavior","Theory of Constraints","Which constraint limits system throughput and how should exploitation, subordination and elevation proceed?",["constraint_hypothesis","throughput_policy"],["operation","bottleneck","product_outcome"],"semantic model or persistent boundary",[]),

    # Information and semantic representation
    M("information.conceptual_data","information_semantics","Conceptual Data Modeling","What domain concepts, relationships, cardinalities and identities exist independent of technology?",["conceptual_schema","business_rules"],["semantic_type","identity","relationship"],"behavior, authority or product",[]),
    M("information.er","information_semantics","Entity-Relationship Modeling","What entity sets, attributes, relationships, keys and cardinalities structure data?",["ER_model","logical_schema"],["data_shape","identity_candidate"],"domain behavior, context or source truth",[]),
    M("information.orm","information_semantics","Object-Role / Fact-Oriented Modeling","Which elementary facts, roles, constraints and verbalizations describe the domain?",["fact_types","role_constraints","verbalizations"],["vocabulary","constraint","data_model"],"process, product or authority",[]),
    M("information.ontology","information_semantics","Ontology Engineering with RDF/OWL","Which classes, properties, individuals and axioms support exchange and formal entailment?",["ontology","axioms","import_closure","entailments"],["semantic_contract","published_language","mapping"],"closed-world validation, workflow, source truth or product",["owl"]),
    M("information.shacl","information_semantics","SHACL Shape Modeling","Which nodes in an exact graph cut conform to explicit structural constraints?",["shapes_graph","validation_report"],["data_contract","conformance_oracle"],"ontology consistency, completeness or truth",["shacl"]),
    M("information.dimensional","information_semantics","Dimensional Modeling","Which business process grain, facts, dimensions, conformed dimensions and slowly changing histories support analytics?",["bus_matrix","fact_dimensions","grain"],["analytical_data_product","measure","projection"],"source operational model or universal semantics",[]),
    M("information.data_vault","information_semantics","Data Vault Modeling","Which business keys, relationships and descriptive histories require auditable integration structures?",["hubs","links","satellites","load_rules"],["integration_storage","history","lineage"],"business truth, product or semantic context",[]),
    M("information.contract_schema","information_semantics","Data Contracts and Schema Evolution","What exact producer-consumer obligations, editions and compatibility relations govern exchange?",["schema","contract","compatibility_result","migration_policy"],["published_language","interface","lifecycle"],"observed attainment, semantic equivalence or product value",[]),

    # Architecture and sociotechnical decomposition
    M("architecture.c4","architecture_structure","C4 Modeling","How does a software system decompose into containers, components and code and interact with users/systems?",["context","container","component","deployment_views"],["software_system","module","runtime"],"domain or product seam",["c4"]),
    M("architecture.arc42","architecture_structure","arc42","What goals, constraints, context, building blocks, runtime, deployment, decisions, qualities and risks define an architecture?",["architecture_description","quality_scenarios","decisions","risks"],["documentation","quality","runtime"],"boundary discovery by itself",["arc42"]),
    M("architecture.team_topologies","architecture_structure","Team Topologies","What stream alignment, cognitive load and interaction mode enable fast independent flow?",["team_topology","team_API","interaction_modes"],["team","product_operation","platform"],"semantic ownership or aggregate consistency",["team-topologies"]),
    M("architecture.coupling","architecture_structure","Coupling, Cohesion and Connascence Analysis","Which elements share reasons to change and which dependencies amplify change?",["coupling_graph","cohesion_metrics","change_candidates"],["module","library","service"],"user value or domain authority",[]),
    M("architecture.hexagonal","architecture_structure","Ports and Adapters / Hexagonal Architecture","Which domain/application core ports isolate external actors, technologies and effects?",["ports","adapters","effect_boundaries"],["library","provider","ACL"],"product or bounded-context count",[]),
    M("architecture.event_driven","architecture_structure","Event-Driven Architecture / Event Sourcing / CQRS","Which facts, commands, state transitions and projections coordinate decoupled components?",["event_contracts","aggregate_streams","projections","sagas"],["aggregate","integration","read_model"],"business event truth or product independence",[]),
    M("architecture.archimate","architecture_structure","ArchiMate","How do motivation, strategy, business, application, data, technology and migration elements relate?",["cross_layer_enterprise_model","plateaus","gaps","work_packages"],["estate","dependency","migration"],"fine domain model or runtime conformance",["togaf-archimate"]),
    M("architecture.togaf","architecture_structure","TOGAF ADM","How is enterprise architecture developed, governed, migrated and changed across domains?",["baseline_target_architectures","roadmap","governance"],["enterprise_architecture","migration"],"specific domain or product seam",["togaf-archimate"]),

    # Reuse and variability
    M("variability.foda","reuse_variability","FODA Feature Modeling","What is mandatory, optional, alternative, common and variable across a family of systems?",["feature_model","commonality_variability","rationale"],["decision_point","product_line","configuration"],"semantic authority, runtime qualification or product",["foda"]),
    M("variability.product_line","reuse_variability","Software Product-Line Engineering","Which reusable assets, production plan and variation mechanisms generate a governed family?",["domain_assets","production_plan","application_engineering_model"],["library","compiler","solution_pack"],"individual domain meaning or adoption value",["foda"]),
    M("variability.decision_model","reuse_variability","Orthogonal Variability / Decision Modeling","Which decisions select variants under which constraints and binding phases?",["variation_points","variants","constraints","binding_times"],["compiler","configuration","library"],"that every option is valid or qualified",["foda"]),
    M("variability.algebraic_api","reuse_variability","Algebraic and Type-Driven API Design","What minimal types and closed operations preserve laws while exposing legitimate variation?",["type_algebra","traits","laws","total_error_types"],["semantic_library","compiler_IR"],"complete domain discovery or product-market fit",[]),
    M("variability.plugin","reuse_variability","Plugin / Provider Architecture","Which stable ports admit replaceable implementations with capability negotiation?",["provider_interface","extension_manifest","qualification_contract"],["provider","adapter","extension"],"semantic equivalence or portability without evidence",[]),

    # Formal and systems engineering
    M("formal.alloy","formal_verification","Alloy Relational Modeling","What finite structures satisfy or violate relational invariants?",["formal_model","instances","counterexamples"],["identity","cardinality","invariant","boundary_falsifier"],"unbounded correctness or product evidence",["alloy"]),
    M("formal.tla","formal_verification","TLA+","What safety and liveness properties hold over concurrent state transitions?",["temporal_specification","model_check_result","proof"],["protocol","concurrency","idempotency","saga"],"domain vocabulary or user value",["tla"]),
    M("formal.design_by_contract","formal_verification","Design by Contract","What preconditions, postconditions and invariants govern an operation and type?",["contracts","runtime_or_static_checks"],["operation","library","aggregate"],"system-level liveness or product boundary",[]),
    M("formal.property_testing","formal_verification","Property-Based / Model-Based Testing","Do generated executions satisfy algebraic, state and metamorphic properties?",["generators","properties","shrunk_counterexamples"],["library","state_machine","conformance"],"proof outside tested model and bounds",[]),
    M("formal.theorem_proving","formal_verification","Interactive Theorem Proving","Can selected mathematical laws be derived from explicit axioms?",["formal_theory","machine_checked_proofs"],["semantic_kernel","algorithm"],"axiom truth, usability or product fit",[]),
    M("systems.sysml","formal_verification","MBSE with SysML","How do requirements, structure, behavior, parametrics, allocation and verification trace across a system?",["requirements_model","system_structure","behavior","allocation","verification_links"],["system","requirement","hardware_software_seam"],"DDD or product boundary",["sysml"]),
    M("systems.stpa","formal_verification","STPA","Which losses, hazards, unsafe control actions and interaction scenarios require system constraints?",["control_structure","hazards","unsafe_actions","safety_constraints"],["authority","effect","safety_boundary"],"ordinary product value or complete probability estimate",["stpa"]),

    # Trust, operations and economics
    M("trust.threat_model","trust_operations","Threat Modeling / Attack Trees / STRIDE","What assets, actors, trust boundaries, attack paths and mitigations exist?",["threat_model","abuse_cases","security_requirements"],["trust_boundary","effect_port","provider"],"domain or product boundary",["nist-sse"]),
    M("trust.privacy_model","trust_operations","Privacy Threat Modeling / LINDDUN","Which linkability, identifiability, disclosure, unawareness and rights risks arise across data flows?",["privacy_threats","data_flow_map","mitigations"],["privacy_boundary","data_minimization","authority"],"legal conclusion or product identity",[]),
    M("trust.fmea_fta","trust_operations","FMEA / Fault-Tree Analysis","How can component failure modes or combinations cause effects and top events?",["failure_modes","fault_tree","controls"],["failure_domain","provider","operation"],"software interaction hazards or semantic seams",[]),
    M("operations.sre","trust_operations","SRE SLI/SLO/Error-Budget Modeling","Which user-visible behaviors matter, how are they measured, and what failure budget governs change?",["SLIs","SLOs","error_budget_policy"],["operated_product","provider","failure_domain"],"semantic ownership or independent user value",["sre-slo"]),
    M("operations.resilience","trust_operations","Resilience and Chaos Engineering","How does the system behave under dependency, network, resource, time and regional failure?",["steady_state_hypothesis","fault_experiments","recovery_evidence"],["failure_domain","provider","product_operation"],"normal-domain semantics or safety proof",[]),
    M("operations.capacity","trust_operations","Queueing, Capacity and Backpressure Modeling","What arrival, service, concurrency, buffer and overload dynamics determine performance?",["workload_model","capacity_plan","overload_policy"],["runtime","provider","product_SLO"],"product value or semantic model",[]),
    M("operations.finops","trust_operations","FinOps / Unit Economics","How are usage, allocation, unit cost, value and optimization decisions governed?",["cost_model","allocation","unit_economics","optimization_case"],["product","provider","economics"],"semantic or consistency boundary",[]),

    # Empirical discovery and validation
    M("evidence.systematic_review","empirical_evidence","Systematic Literature / Mapping Review","What evidence, concepts, methods, disagreements and gaps exist across a reproducible research corpus?",["protocol","study_corpus","evidence_synthesis","gap_map"],["domain","method","innovation"],"local applicability or implementation conformance",[]),
    M("evidence.grounded_theory","empirical_evidence","Grounded Theory","Which concepts and relationships emerge through coding, constant comparison and theoretical sampling?",["codes","categories","theory","saturation_claim"],["vocabulary","domain","boundary_candidate"],"formal semantics or statistical prevalence",[]),
    M("evidence.delphi","empirical_evidence","Delphi / Structured Expert Elicitation","Where do independently elicited expert judgments converge, disagree and remain uncertain?",["judgments","rationales","consensus_distribution"],["domain","priority","uncertainty"],"objective truth or implementation proof",[]),
    M("evidence.repository_mining","empirical_evidence","Repository and Change-History Mining","Which code, dependency and co-change structures reveal actual ownership and shearing forces?",["dependency_graph","cochange_clusters","ownership_map"],["module","library","migration"],"future semantic or product correctness",[]),
    M("evidence.runtime_tracing","empirical_evidence","Runtime Trace and Interaction Mining","Which actual calls, messages, latencies, failures and state paths occur?",["runtime_graph","critical_paths","failure_correlations"],["runtime","provider","operation"],"all possible behavior or semantic authority",[]),
    M("evidence.data_usage","empirical_evidence","Data Lineage and Usage Mining","Which sources, transformations, queries, consumers and impacts are observed?",["lineage_graph","usage_population","impact_candidates"],["data_product","pipeline","consumer"],"causality, completeness or source truth",[]),
    M("evidence.red_team","empirical_evidence","Adversarial / Red-Team Boundary Review","Which counterexamples collapse identities, cross authority, bypass refusals or make replacement impossible?",["negative_twins","attack_cases","boundary_falsifiers"],["all_boundary_kinds"],"positive completeness",[]),

    # Analytical problem formulation
    M("analytics.measurement","analytical_formulation","Measurement Theory and Metrology","What measurand, unit, scale, procedure, uncertainty and traceability make a number meaningful?",["measurement_model","uncertainty_budget","traceability"],["metric","data_type","analytical_result"],"causality or business decision",[]),
    M("analytics.statistics","analytical_formulation","Statistical Decision and Estimation Theory","Which population, estimand, sampling process, loss and uncertainty define an inference?",["estimand","estimator","uncertainty","decision_rule"],["analytical_method","data_requirement","result"],"causality, authority or product",[]),
    M("analytics.causal","analytical_formulation","Causal Graph / Structural Causal Modeling","Which interventions, counterfactuals, assumptions and identification conditions support a causal claim?",["causal_graph","estimand","identification_proof","sensitivity"],["analytical_method","source_requirement","claim"],"observed correlation or domain authority",[]),
    M("analytics.or","analytical_formulation","Operations Research Model Formulation","Which decisions, objectives, constraints, uncertainty and feasible sets define optimization or simulation?",["decision_model","objective","constraints","solution_concept"],["analytical_method","solver_library","data_requirement"],"business authorization or source truth",[]),
    M("analytics.simulation","analytical_formulation","Simulation Modeling","Which system boundary, state, events, resources, distributions and experiments represent behavior?",["conceptual_model","executable_model","experiment_design","validation_evidence"],["analytical_method","process","capacity"],"real-world identity or guaranteed forecast",[]),
]


LENSES = [
    ("value","A product requires user, job, outcome and harmed-party evidence.",["business_product","strategy_landscape"]),
    ("semantic","A bounded context requires a coherent local model, language and explicit translations.",["domain_semantics","information_semantics"]),
    ("behavior","Processes, cases, decisions, states and exceptions require fitting behavioral formalisms.",["work_behavior"]),
    ("authority","Decision rights, trust boundaries, approvals and effects must be independently modeled.",["domain_semantics","trust_operations","formal_verification"]),
    ("consistency","Aggregate and protocol seams require atomicity, concurrency, safety and liveness evidence.",["domain_semantics","formal_verification"]),
    ("variability","Composable libraries require commonality, variation points, constraints and binding phases.",["reuse_variability"]),
    ("software","Modules, containers, dependencies and ports require a separate implementation view.",["architecture_structure"]),
    ("operation","Operated products/providers require SLO, capacity, failure, recovery and support evidence.",["trust_operations"]),
    ("economics","Independent products/providers require usage, cost, value and exit evidence.",["strategy_landscape","trust_operations"]),
    ("empirical","Claimed boundaries must survive observed work, code, logs, data usage, incidents and adversarial cases.",["empirical_evidence"]),
    ("analytical","Analytical products require method, data, assumptions, uncertainty and result-authority boundaries.",["analytical_formulation"]),
    ("system","Hardware, software, people, procedures, requirements and safety constraints require end-to-end traceability.",["formal_verification","architecture_structure"]),
]

REQUIRED_LENSES = [{"lens_id":f"lens.{ident}","record_kind":"required_boundary_lens","law":law,"method_families":families,"default_if_missing":"UNDETERMINED_NOT_PASS"} for ident, law, families in LENSES]


TRIANGULATION = [
    {"record_id":"triangulation.metadata.product","record_kind":"multi_method_seam_verdict","subject_ref":"product.metadata_discovery","verdict":"retain_one_operated_product","supporting_methods":["method.business.jtbd","method.business.service_blueprint","method.business.product_split_merge","method.operations.sre","method.strategy.wardley"],"counterpressure":["Different semantic submodels and imported physical search do not require separate adoption promises."],"residual":"Executed user adoption, SLO and exit evidence remain absent."},
    {"record_id":"triangulation.metadata.acquisition","record_kind":"multi_method_seam_verdict","subject_ref":"library.metadata_discovery.acquisition_port","verdict":"separate_supporting_context_and_effect_library","supporting_methods":["method.domain.ddd","method.domain.context_mapping","method.architecture.hexagonal","method.work.statecharts","method.formal.tla"],"counterpressure":["It is not independently valuable enough to be a product inside this portfolio."],"residual":"Provider conformance and protocol-specific refinements remain unqualified."},
    {"record_id":"triangulation.metadata.catalog","record_kind":"multi_method_seam_verdict","subject_ref":"context.metadata_discovery.catalog","verdict":"one_core_context_with_multiple_aggregates_services_and_libraries","supporting_methods":["method.domain.ddd","method.domain.conceptual_contours","method.information.conceptual_data","method.information.ontology","method.business.service_blueprint"],"counterpressure":["Physical indexing/search is an imported provider boundary; it must not own catalog semantics."],"residual":"Domain-expert and implementation feedback may later expose a language split."},
    {"record_id":"triangulation.metadata.search","record_kind":"multi_method_seam_verdict","subject_ref":"library.metadata_discovery.search_browse","verdict":"catalog_service_and_effect_port_not_context_or_product","supporting_methods":["method.domain.conceptual_contours","method.architecture.hexagonal","method.architecture.c4","method.operations.sre"],"counterpressure":["Ranking and execution have distinct algorithms and SLOs, supporting replaceable provider seams."],"residual":"Search provider qualification and ranking evaluation remain open."},
    {"record_id":"triangulation.metadata.federation","record_kind":"multi_method_seam_verdict","subject_ref":"library.metadata_discovery.federation","verdict":"separate_supporting_context_and_library","supporting_methods":["method.domain.context_mapping","method.domain.ddd","method.architecture.event_driven","method.formal.tla","method.trust.threat_model"],"counterpressure":["Federation remains part of the catalog product until independent adoption/exit evidence appears."],"residual":"Peer trust, failure and conflict conformance fixtures remain unexecuted."},
    {"record_id":"triangulation.metadata.freshness","record_kind":"multi_method_seam_verdict","subject_ref":"library.metadata_discovery.freshness_coverage","verdict":"pure_measurement_library_with_catalog_semantic_owner","supporting_methods":["method.analytics.measurement","method.operations.sre","method.domain.conceptual_contours","method.information.contract_schema"],"counterpressure":["Generic measurement primitives should be imported rather than duplicated."],"residual":"Cross-product generic extraction is a future refactoring candidate, not a new product."},
]


FILES = {
    "sources.jsonl":SOURCES,
    "methods.jsonl":METHODS,
    "required-lenses.jsonl":REQUIRED_LENSES,
    "metadata-discovery-triangulation.jsonl":TRIANGULATION,
}


def main() -> None:
    files = {}
    for name, rows in FILES.items():
        payload = encode(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        files[name] = {"records":len(rows),"sha256":hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {"manifest_id":"boundary_method_ensemble_v0_1_0","as_of":AS_OF,"edition":1,"status":"researched_open_world","completion_claim":False,"method_count":len(METHODS),"family_count":len({row['family'] for row in METHODS}),"files":files}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS boundary method ensemble: {len(SOURCES)} sources, {len(METHODS)} methods, {len({row['family'] for row in METHODS})} families, {len(REQUIRED_LENSES)} required lenses")


if __name__ == "__main__":
    main()
