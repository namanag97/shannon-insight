#!/usr/bin/env python3
"""Canonical declarative source for platform/control product adjudication."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from platform_product_enrichment import enrich_platform_products
from solution_compiler_enrichment import enrich as enrich_solution_compiler


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"
AXES = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]


def ev(ident: str, title: str, publisher: str, uri: str, claim: str, limit: str, cls: str = "official_specification_or_documentation") -> dict[str, Any]:
    return {"source_id":ident,"source_class":cls,"title":title,"publisher":publisher,"uri":uri,"retrieved_at":"2026-08-26","claim":claim,"scope_limit":limit}


def art(ident: str, kind: str, name: str, status: str, definition: str, refs: list[str], owner: str | None = None, adoption: bool = False, operated: bool = False) -> dict[str, Any]:
    return {"artifact_id":ident,"kind":kind,"name":name,"status":status,"semantic_owner_ref":owner,"adoption_unit":adoption,"operated":operated,"definition":definition,"evidence_refs":refs}


def split(scores: list[int], refs: list[str], label: str) -> dict[str, Any]:
    return {
        axis: {
            "score": score,
            "finding": f"{label} has evidence scoped to its {axis} boundary; a score below two preserves an unresolved qualification or independence gap.",
            "evidence_refs": refs,
        }
        for axis, score in zip(AXES, scores, strict=True)
    }


def lib(ident: str, owner: str, provides: list[str], types: list[str], operations: list[str], decisions: list[str], laws: list[str], refusals: list[str], deps: list[str], effect: str, refs: list[str], cls: str = "semantic_pure") -> dict[str, Any]:
    return {"library_id":ident,"class":cls,"owner_ref":owner,"provides":provides,"types":types,"operations":operations,"decisions":decisions,"invariants":laws,"refusals":refusals,"dependencies":deps,"effect_boundary":effect,"evidence_refs":refs}


def source() -> dict[str, Any]:
    sources = [
        ev("evidence.cncf.platforms","Platforms White Paper","CNCF TAG App Delivery","https://tag-app-delivery.cncf.io/whitepapers/platforms/","Defines a platform as an integrated capability set offered to users through supported interfaces and recommends product thinking.","Does not determine this portfolio's semantic owners or prove adoption of a specific platform."),
        ev("evidence.cncf.operational_excellence","Cloud Native Operational Excellence Whitepaper","CNCF TAG App Delivery","https://tag-app-delivery.cncf.io/whitepapers/cloud-native-operational-excellence/","Separates reliability, observability, incident, continuity and operational practices.","A practice framework does not make one platform-operations product or qualify an implementation."),
        ev("evidence.backstage.catalog","Backstage Software Catalog","Backstage","https://backstage.io/docs/features/software-catalog/","Documents ownership/discovery metadata for software components, services, websites, libraries and pipelines.","A portal/catalog is an interface capability, not the entire developer platform or source of service truth."),
        ev("evidence.backstage.templates","Backstage Software Templates","Backstage","https://backstage.io/docs/features/software-templates/","Documents parameterized scaffolding actions, task authorization and dry-run surfaces.","A template execution does not prove resulting service conformance or runtime readiness."),
        ev("evidence.crossplane.composition","Crossplane Compositions","Crossplane","https://docs.crossplane.io/latest/composition/compositions/","Defines custom APIs that compose managed resources through versioned composition pipelines.","Composition rendering is not provider qualification, successful reconciliation or vertical acceptance."),
        ev("evidence.kubernetes.controllers","Kubernetes Controllers","Kubernetes","https://kubernetes.io/docs/concepts/architecture/controller/","Defines control loops that reconcile current state toward desired state.","Observed desired/actual convergence is scoped to controller and resource contracts; it is not business outcome proof."),
        ev("evidence.kubernetes.resources","Resource Management for Pods and Containers","Kubernetes","https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/","Defines requests, limits and scheduling/runtime resource behavior for CPU, memory and other resources.","Kubernetes resource semantics do not cover every compute target or financial budget."),
        ev("evidence.kubernetes.scheduling","Scheduling, Preemption and Eviction","Kubernetes","https://kubernetes.io/docs/concepts/scheduling-eviction/","Separates placement, preemption, eviction, topology, bin-packing and scheduling readiness concerns.","Documentation does not qualify a scheduler configuration or prove workload SLOs."),
        ev("evidence.kubernetes.quota","Resource Quotas","Kubernetes","https://kubernetes.io/docs/concepts/policy/resource-quotas/","Defines namespace-scoped aggregate consumption limits and admission refusal.","Quota is authority to consume, not physical capacity, budget or placement."),
        ev("evidence.kubernetes.dra","Dynamic Resource Allocation","Kubernetes","https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/","Defines ResourceClaims, device allocation, capacity and privileged admin-access semantics.","Feature-stage and target-specific behavior must remain exact; a claim is not a portable resource offer."),
        ev("evidence.kubernetes.conformance","Kubernetes Conformance","CNCF","https://www.cncf.io/training/certification/software-conformance/","Defines a conformance program for Kubernetes implementations against a scoped test suite.","One conformance program cannot establish a universal provider-qualification broker."),
        ev("evidence.oci.runtime","OCI Runtime Specification","Open Container Initiative","https://specs.opencontainers.org/runtime-spec/","Defines a filesystem bundle, configuration and lifecycle operations for containers.","Runtime-spec conformance does not prove scheduler, resource, security or service-level fitness."),
        ev("evidence.wasi.p2","WASI 0.2","WASI Subgroup","https://wasi.dev/releases/wasi-p2","Defines capability-oriented component interfaces for WebAssembly targets.","Interface availability does not qualify a host occurrence or grant effects."),
        ev("evidence.opentelemetry.spec","OpenTelemetry Specification","OpenTelemetry","https://opentelemetry.io/docs/specs/otel/","Defines APIs, SDKs, data and transport contracts for traces, metrics and logs.","Telemetry is observation, not product health, root cause, SLO satisfaction or effect authority."),
        ev("evidence.opentelemetry.semconv","OpenTelemetry Semantic Conventions","OpenTelemetry","https://opentelemetry.io/docs/specs/semconv/","Defines versioned names, types and valid values for observed operations and resources.","A semantic convention does not prove collection completeness or service correctness."),
        ev("evidence.openslo","OpenSLO Specification","OpenSLO","https://github.com/OpenSLO/OpenSLO","Defines machine-readable service, indicator and objective declarations.","An SLO declaration is not an evaluated result, contractual SLA or service-credit decision."),
        ev("evidence.google.sre","The Site Reliability Workbook","Google","https://sre.google/workbook/table-of-contents/","Documents SLOs, monitoring, alerting, incident response, overload and change practices.","Practice guidance does not make telemetry and incident semantics one product."),
        ev("evidence.focus12","FOCUS Specification 1.2","FinOps Foundation","https://focus.finops.org/focus-specification/v1-2/","Defines vendor-neutral billing-data columns, semantics and conformance requirements.","Billing normalization does not prove allocation policy, business value, invoice truth or runtime usage."),
        ev("evidence.finops.framework","FinOps Framework","FinOps Foundation","https://www.finops.org/framework/","Defines FinOps personas, capabilities and iterative operating domains.","A framework does not prescribe one allocation policy or qualify cost data."),
        ev("evidence.opencost.spec","OpenCost Specification","OpenCost","https://opencost.io/docs/specification/","Defines vendor-neutral Kubernetes cost measurement and allocation methodology.","Kubernetes infrastructure cost is not universal enterprise cost, price, invoice or business value."),
        ev("evidence.openmeter.events","OpenMeter Usage Events","OpenMeter","https://openmeter.io/docs/metering/events/overview","Documents ingestion of CloudEvents-based usage occurrences and idempotency behavior.","A metering implementation does not own source usage truth or establish billed charges."),
        ev("evidence.openmeter.meters","OpenMeter Meters","OpenMeter","https://openmeter.io/docs/metering/meters","Documents meter definitions, aggregation and value-property behavior.","Meter configuration is not an allocation rule, budget or invoice."),
        ev("evidence.tmf645","TMF645 Service Qualification API","TM Forum","https://github.com/tmforum-apis/TMF645_ServiceQualification","Defines requests and responses for checking whether a service can be supplied at a location.","Telecom service qualification is not general implementation conformance or provider binding."),
        ev("evidence.it4it3","IT4IT Standard Version 3","The Open Group","https://www.opengroup.org/it4it","Defines value streams and information objects for managing digital products and services.","Reference architecture does not decide this portfolio's product boundaries."),
        ev("evidence.iso20000","ISO/IEC 20000-1:2018","ISO/IEC","https://www.iso.org/standard/70636.html","Specifies service-management-system requirements.","Catalog-level evidence does not license inaccessible clauses or merge incident, support and observability products."),
        ev("evidence.iso19941","ISO/IEC 19941 Cloud Interoperability and Portability","ISO/IEC","https://www.iso.org/standard/66639.html","Provides cloud interoperability and portability concepts.","Series-level concepts do not prove a concrete exit or cross-provider migration."),
        ev("evidence.slsa12","SLSA Specification 1.2","OpenSSF SLSA","https://slsa.dev/spec/v1.2/","Defines provenance and source/build track requirements for software supply chains.","Provenance does not prove semantic conformance, product fitness or deployment qualification."),
        ev("evidence.in_toto","in-toto Attestation Framework","in-toto","https://github.com/in-toto/attestation/tree/main/spec","Defines signed statement/predicate envelopes for supply-chain attestations.","A signed assertion still requires issuer, subject, predicate and policy appraisal."),
        ev("evidence.cue","CUE Language Specification","CUE","https://cuelang.org/docs/reference/spec/","Defines a constraint-based data language for validation, configuration and generation.","Constraint satisfaction under a CUE schema is not business-domain validity or provider qualification."),
        ev("evidence.terraform.plan","Terraform Plan Command","HashiCorp","https://developer.hashicorp.com/terraform/cli/commands/plan","Documents speculative and saved execution plans and planning modes.","A provider-specific infrastructure plan is not a provider-neutral solution compiler result or applied effect receipt."),
        ev("evidence.nist.cloud","NIST SP 800-145 Cloud Computing Definition","NIST","https://www.nist.gov/publications/nist-definition-cloud-computing","Defines essential cloud characteristics, service models and deployment models.","A general definition does not establish analytical runtime capability or product identity."),
        ev("evidence.paper.drf","Dominant Resource Fairness","UC Berkeley","https://digicoll.lib.berkeley.edu/record/136796/files/EECS-2011-18.pdf","Defines a multi-resource fairness allocation mechanism and properties.","A scheduling policy result is scoped to its assumptions and does not prove product fitness.","primary_research"),
    ]

    kinds = [
        {"kind":"architecture_pattern","definition":"A reusable arrangement without adoption or semantic-owner identity."},
        {"kind":"suite","definition":"Packaging of independently governed products and capabilities."},
        {"kind":"product","definition":"An independently adopted and operated outcome promise."},
        {"kind":"control_component","definition":"A compiler or runtime subsystem without an independent product promise."},
        {"kind":"capability","definition":"Typed behavior required or offered by products and implementations."},
        {"kind":"semantic_contract","definition":"Owner of meaning, state, invariants and refusals."},
        {"kind":"standard","definition":"An exact external edition specializing a contract."},
        {"kind":"interface","definition":"A versioned interaction contract without an operated promise."},
        {"kind":"library_contract","definition":"A pure or effect-bounded reusable implementation boundary."},
        {"kind":"implementation","definition":"A concrete unqualified project or provider component."},
        {"kind":"provider_class","definition":"A class of operated offers, not a qualified occurrence."},
        {"kind":"neighboring_product","definition":"A product outside this slice whose authority is imported."},
        {"kind":"solution_pack","definition":"A vertical composition carrying industry language, rules and defaults."},
    ]

    artifacts: list[dict[str, Any]] = [
        art("pattern.composable_data_platform","architecture_pattern","Composable data-platform pattern","retain_as_composition_pattern","Arranges compiler, developer platform, runtime, qualification, operations and FinOps capabilities without one semantic owner.",["evidence.cncf.platforms","evidence.it4it3"]),
        art("suite.data_analytics_platform","suite","Data and analytics platform suite","suite_not_semantic_owner","Packages four products and imported operational capabilities.",["evidence.cncf.platforms","evidence.cncf.operational_excellence"]),
        art("product.solution_compiler","product","Intent-to-solution compiler","presumptive_product","Compiles typed enterprise intent into a closed candidate solution plan or typed refusal with evidence.",["evidence.cue","evidence.crossplane.composition","evidence.terraform.plan"],"semantic.compilation_run",True,True),
        art("product.data_product_developer_platform","product","Data-product developer platform","strong_product_candidate","Offers paved paths, blueprints, self-service interfaces, conformance and lifecycle evidence to data-product teams.",["evidence.cncf.platforms","evidence.backstage.catalog","evidence.backstage.templates"],"semantic.platform_blueprint",True,True),
        art("product.runtime_resource_control","product","Analytical runtime resource control plane","strong_product_candidate","Admits, places and controls finite executable work over qualified resource offers and produces runtime receipts.",["evidence.kubernetes.resources","evidence.kubernetes.scheduling","evidence.kubernetes.dra"],"semantic.resource_admission",True,True),
        art("product.finops_allocation","product","Usage, cost and FinOps allocation","strong_product_candidate","Normalizes cost/usage, meters consumption, allocates shared cost and governs budgets/showback with evidence.",["evidence.focus12","evidence.finops.framework","evidence.opencost.spec"],"semantic.cost_allocation",True,True),
        art("component.provider_qualification","control_component","Provider qualification subsystem","compiler_subsystem_not_product","Evaluates exact provider artifact/occurrence/target evidence against a qualification profile and issues scoped receipts or refusals.",["evidence.kubernetes.conformance","evidence.slsa12","evidence.in_toto"],"semantic.qualification_receipt"),
        art("pattern.platform_operations","architecture_pattern","Platform operations pattern","split_composition_not_product","Composes telemetry, SLO evaluation, incident/service management, support, continuity and each product's operating responsibility.",["evidence.opentelemetry.spec","evidence.openslo","evidence.cncf.operational_excellence"]),
        art("standard.oci_runtime","standard","OCI Runtime Specification","exact_edition_required","Container runtime bundle and lifecycle contract.",["evidence.oci.runtime"]),
        art("standard.wasi_p2","standard","WASI 0.2","exact_edition_required","WebAssembly component host-interface profile.",["evidence.wasi.p2"]),
        art("standard.focus12","standard","FOCUS 1.2","exact_edition_required","Cost and usage normalization contract.",["evidence.focus12"]),
        art("standard.opentelemetry","standard","OpenTelemetry","exact_edition_required","Telemetry APIs, SDK, data and protocol contract.",["evidence.opentelemetry.spec"]),
        art("implementation.crossplane","implementation","Crossplane","observed_unqualified","Observed API composition and reconciliation implementation.",["evidence.crossplane.composition"]),
        art("implementation.backstage","implementation","Backstage","observed_unqualified","Observed developer portal/catalog/template implementation.",["evidence.backstage.catalog","evidence.backstage.templates"]),
        art("implementation.kubernetes","implementation","Kubernetes","observed_unqualified","Observed scheduling, quota, controller and resource-allocation implementation.",["evidence.kubernetes.controllers","evidence.kubernetes.scheduling"]),
        art("implementation.opencost","implementation","OpenCost","observed_unqualified","Observed Kubernetes cost measurement and allocation implementation.",["evidence.opencost.spec"]),
        art("implementation.openmeter","implementation","OpenMeter","observed_unqualified","Observed usage-event and meter implementation.",["evidence.openmeter.events","evidence.openmeter.meters"]),
        art("implementation.opentelemetry","implementation","OpenTelemetry","observed_unqualified","Observed telemetry API/SDK/collector family.",["evidence.opentelemetry.spec","evidence.opentelemetry.semconv"]),
        art("provider.runtime_backend","provider_class","Runtime backend provider","unqualified_class","Offers target-specific runtime resources and effect execution.",["evidence.oci.runtime","evidence.wasi.p2"]),
        art("provider.platform_capability","provider_class","Platform capability provider","unqualified_class","Offers one replaceable platform capability behind a provider-neutral requirement.",["evidence.cncf.platforms"]),
        art("neighbor.identity_policy","neighboring_product","Identity and policy authority","import_only","Owns principals, authorization, purpose, policy and revocation.",["evidence.kubernetes.dra"]),
        art("neighbor.telemetry_observability","neighboring_product","Telemetry and observability platform","future_product_adjudication","Owns collection, storage and query of operational signals without owning service truth.",["evidence.opentelemetry.spec"]),
        art("neighbor.incident_service_management","neighboring_product","Incident and service management","future_product_adjudication","Owns incident case, escalation, problem/change and support workflows.",["evidence.iso20000","evidence.cncf.operational_excellence"]),
        art("neighbor.billing_finance","neighboring_product","Billing and finance ledger","import_only","Owns rated charges, invoices, payments and accounting—not FinOps allocation.",["evidence.focus12"]),
    ]

    semantics = [
        ("semantic.intent_ir","Intent IR","typed desired outcomes, constraints, authority, acceptance and unresolved variables",["evidence.cue"]),
        ("semantic.compilation_run","Compilation run","input editions, passes, decisions, diagnostics, output and reproducibility identity",["evidence.terraform.plan"]),
        ("semantic.solution_plan","Solution plan","closed logical/physical plan, residual gaps, bindings and proof obligations",["evidence.crossplane.composition"]),
        ("semantic.compiler_gap","Compiler gap","typed missing meaning, capability, evidence, authority or target requirement",["evidence.cue"]),
        ("semantic.binding_decision","Binding decision","requirement, candidate offers, rejected alternatives, solver result and evidence",["evidence.kubernetes.conformance"]),
        ("semantic.release_evidence","Release evidence","build, qualification, migration, rollback and acceptance evidence set",["evidence.slsa12","evidence.in_toto"]),
        ("semantic.platform_blueprint","Platform blueprint","versioned self-service product template and capability requirements",["evidence.cncf.platforms","evidence.backstage.templates"]),
        ("semantic.paved_path","Paved path","supported workflow, interfaces, guardrails, escape hatch and ownership",["evidence.cncf.platforms"]),
        ("semantic.platform_capability","Platform capability","user-visible requirement/offer, service level, lifecycle and removal seam",["evidence.cncf.platforms"]),
        ("semantic.platform_conformance","Platform conformance","blueprint/output checks and evidence without business-outcome promotion",["evidence.backstage.templates"]),
        ("semantic.work_unit","Work unit","executable artifact, entry point, attempt policy and completion contract",["evidence.oci.runtime","evidence.wasi.p2"]),
        ("semantic.resource_demand","Resource demand","minimum/target/maximum quantities and hard/soft constraints",["evidence.kubernetes.resources"]),
        ("semantic.resource_offer","Resource offer","validity-scoped allocatable capacity, topology, health, price and target profile",["evidence.kubernetes.dra"]),
        ("semantic.resource_admission","Resource admission","quota, budget, compatibility and finite-capacity admission verdict",["evidence.kubernetes.quota"]),
        ("semantic.placement","Placement","constraint-satisfying assignment and scheduler-assurance result",["evidence.kubernetes.scheduling","evidence.paper.drf"]),
        ("semantic.reservation_allocation","Reservation and allocation","temporary hold versus committed assignment",["evidence.kubernetes.dra"]),
        ("semantic.lease_fencing","Lease and fencing","time-bounded effect authority and stale-writer exclusion",["evidence.kubernetes.controllers"]),
        ("semantic.runtime_attempt","Runtime attempt","worker/executor incarnation, start, cancellation and terminal outcome",["evidence.oci.runtime"]),
        ("semantic.runtime_receipt","Runtime receipt","observed execution, resource use, target and effect outcome",["evidence.opentelemetry.semconv"]),
        ("semantic.usage_meter","Usage meter","event subject, measure, aggregation, window and correction contract",["evidence.openmeter.events","evidence.openmeter.meters"]),
        ("semantic.cost_normalization","Cost normalization","provider billing occurrence mapped to an exact FOCUS edition with residuals",["evidence.focus12"]),
        ("semantic.cost_allocation","Cost allocation","rule, basis, shared/idle/overhead treatment, target and reconciliation",["evidence.opencost.spec"]),
        ("semantic.budget_precharge","Budget and precharge","finite spend authority reserved before effect and reconciled after usage",["evidence.finops.framework"]),
        ("semantic.unit_cost","Unit cost","cost divided by a governed useful-output denominator and exact period",["evidence.finops.framework"]),
        ("semantic.provider_offer","Provider offer","exact artifact, occurrence, target, configuration, limits and validity",["evidence.kubernetes.conformance"]),
        ("semantic.qualification_profile","Qualification profile","scoped oracles, target, thresholds, independence and invalidators",["evidence.kubernetes.conformance"]),
        ("semantic.qualification_receipt","Qualification receipt","subject/profile/result/evidence/expiry/revocation-bound assessment",["evidence.slsa12","evidence.in_toto"]),
        ("semantic.service_health","Service health","evaluated SLI/SLO state and uncertainty, not raw telemetry",["evidence.openslo","evidence.google.sre"]),
        ("semantic.incident_case","Incident case","impact, timeline, coordination, mitigation, restoration and evidence",["evidence.cncf.operational_excellence","evidence.iso20000"]),
    ]
    for ident, name, definition, refs in semantics:
        artifacts.append(art(ident,"semantic_contract",name,"candidate",definition,refs))

    capabilities = [
        ("capability.parse_intent","Parse and type intent","semantic.intent_ir",["evidence.cue"]),
        ("capability.compile_solution","Compile candidate solution","semantic.compilation_run",["evidence.crossplane.composition","evidence.terraform.plan"]),
        ("capability.bind_offers","Bind capability offers","semantic.binding_decision",["evidence.kubernetes.conformance"]),
        ("capability.emit_release_evidence","Emit release evidence","semantic.release_evidence",["evidence.slsa12"]),
        ("capability.publish_blueprint","Publish platform blueprint","semantic.platform_blueprint",["evidence.backstage.templates"]),
        ("capability.instantiate_paved_path","Instantiate paved path","semantic.paved_path",["evidence.cncf.platforms","evidence.crossplane.composition"]),
        ("capability.evaluate_platform_conformance","Evaluate platform conformance","semantic.platform_conformance",["evidence.backstage.templates"]),
        ("capability.normalize_resource_vector","Normalize resource vector","semantic.resource_demand",["evidence.kubernetes.resources"]),
        ("capability.admit_work","Admit finite work","semantic.resource_admission",["evidence.kubernetes.quota"]),
        ("capability.place_work","Place admitted work","semantic.placement",["evidence.kubernetes.scheduling"]),
        ("capability.reserve_allocate","Reserve and allocate resources","semantic.reservation_allocation",["evidence.kubernetes.dra"]),
        ("capability.execute_attempt","Execute runtime attempt","semantic.runtime_attempt",["evidence.oci.runtime","evidence.wasi.p2"]),
        ("capability.record_runtime_receipt","Record runtime receipt","semantic.runtime_receipt",["evidence.opentelemetry.semconv"]),
        ("capability.meter_usage","Meter usage","semantic.usage_meter",["evidence.openmeter.events"]),
        ("capability.normalize_cost","Normalize provider cost","semantic.cost_normalization",["evidence.focus12"]),
        ("capability.allocate_cost","Allocate cost","semantic.cost_allocation",["evidence.opencost.spec"]),
        ("capability.precharge_budget","Precharge finite budget","semantic.budget_precharge",["evidence.finops.framework"]),
        ("capability.qualify_provider","Qualify provider occurrence","semantic.qualification_receipt",["evidence.kubernetes.conformance","evidence.slsa12"]),
        ("capability.evaluate_service_health","Evaluate service health","semantic.service_health",["evidence.openslo"]),
        ("capability.manage_incident","Manage incident case","semantic.incident_case",["evidence.cncf.operational_excellence"]),
    ]
    for ident, name, owner, refs in capabilities:
        artifacts.append(art(ident,"capability",name,"candidate",f"Typed capability owned by {owner}.",refs,owner))

    decisions = [
        {"decision_id":"decision.platform.solution_compiler","subject_ref":"product.solution_compiler","disposition":"presumptive_product","rationale":"The enterprise architect has a distinct compile/refuse job and reproducible plan lifecycle, but independent market and operational evidence for this exact universal promise remains limited.","split_test":split([2,2,1,2,2,2,1,1,2,1],["evidence.cue","evidence.crossplane.composition","evidence.terraform.plan"],"intent-to-solution compiler"),"evidence_refs":["evidence.cue","evidence.crossplane.composition","evidence.terraform.plan"]},
        {"decision_id":"decision.platform.developer_platform","subject_ref":"product.data_product_developer_platform","disposition":"strong_product_candidate","rationale":"Platform teams operate an adopted product for developer self-service, supported capabilities, paved paths, lifecycle and exit.","split_test":split([2,2,2,2,2,2,2,1,2,2],["evidence.cncf.platforms","evidence.backstage.catalog","evidence.backstage.templates"],"data-product developer platform"),"evidence_refs":["evidence.cncf.platforms","evidence.backstage.catalog","evidence.backstage.templates"]},
        {"decision_id":"decision.platform.runtime_resource","subject_ref":"product.runtime_resource_control","disposition":"strong_product_candidate","rationale":"Admission, placement, allocation, lease/cancellation and runtime receipt ownership form an independently operated control-plane promise.","split_test":split([2,2,2,2,2,2,2,2,2,2],["evidence.kubernetes.resources","evidence.kubernetes.scheduling","evidence.kubernetes.dra","evidence.oci.runtime"],"runtime resource control"),"evidence_refs":["evidence.kubernetes.resources","evidence.kubernetes.scheduling","evidence.kubernetes.dra","evidence.oci.runtime"]},
        {"decision_id":"decision.platform.finops","subject_ref":"product.finops_allocation","disposition":"strong_product_candidate","rationale":"FinOps practitioners and platform/finance owners independently adopt cost normalization, allocation, budget and unit-economics operations with their own data and lifecycle.","split_test":split([2,2,2,2,2,2,2,2,2,1],["evidence.focus12","evidence.finops.framework","evidence.opencost.spec"],"FinOps allocation"),"evidence_refs":["evidence.focus12","evidence.finops.framework","evidence.opencost.spec"]},
        {"decision_id":"decision.platform.provider_qualification","subject_ref":"component.provider_qualification","disposition":"reclassify_as_compiler_assurance_subsystem","rationale":"Qualification owns profiles and receipts but lacks an independent user outcome, economics and lifecycle distinct from compiler binding and conformance assurance.","evidence_refs":["evidence.kubernetes.conformance","evidence.slsa12","evidence.in_toto"]},
        {"decision_id":"decision.platform.operations","subject_ref":"pattern.platform_operations","disposition":"split_and_defer_product_boundaries","rationale":"Telemetry, SLO evaluation, incident/service management, support and per-product operational duty have different owners; packaging does not prove one product.","evidence_refs":["evidence.opentelemetry.spec","evidence.openslo","evidence.cncf.operational_excellence","evidence.iso20000"]},
        {"decision_id":"decision.platform.compiler_apply","subject_ref":"semantic.solution_plan","disposition":"retain_split","rationale":"A compiled or provider plan is not an authorized apply, successful reconciliation or accepted business outcome.","evidence_refs":["evidence.terraform.plan","evidence.crossplane.composition"]},
        {"decision_id":"decision.platform.quota_capacity_budget","subject_ref":"semantic.resource_admission","disposition":"retain_split","rationale":"Entitlement, authorization, quota, budget and physical capacity are independent gates.","evidence_refs":["evidence.kubernetes.quota","evidence.kubernetes.resources","evidence.finops.framework"]},
        {"decision_id":"decision.platform.telemetry_health","subject_ref":"semantic.service_health","disposition":"retain_split","rationale":"Telemetry observations require scoped SLI/SLO evaluation before any health claim.","evidence_refs":["evidence.opentelemetry.spec","evidence.openslo"]},
        {"decision_id":"decision.platform.usage_cost_invoice","subject_ref":"semantic.cost_allocation","disposition":"retain_split","rationale":"Requested, allocated and consumed resources; normalized costs; allocated costs; prices; charges and invoices are distinct.","evidence_refs":["evidence.focus12","evidence.opencost.spec"]},
        {"decision_id":"decision.platform.ai_prefix","subject_ref":"pattern.composable_data_platform","disposition":"reject_ambient_ai_boundary","rationale":"Agents may propose intent or diagnoses; deterministic typing, solving, qualification, authority, resource control, cost allocation and receipts remain authoritative.","evidence_refs":["evidence.cue","evidence.kubernetes.conformance","evidence.focus12"]},
    ]

    ownership = [
        {"meaning_id":f"meaning.{ident.removeprefix('semantic.')}","term":name,"owner_ref":ident,"invariant":f"{name} identity and state cannot be inferred from provider brand, suite packaging, generated prose or a neighboring receipt.","must_not_be_owned_by":["neighbor.identity_policy","neighbor.billing_finance"]}
        for ident, name, _definition, _refs in semantics
    ]

    libraries = [
        lib("library.platform.intent_contract","semantic.intent_ir",["capability.parse_intent"],["IntentDocument","TypedIntent","IntentDiagnostic"],["parse_intent","type_intent"],["language_edition","unknown_term_policy"],["parse_is_not_resolve","unknown_meaning_fails_closed"],["invalid_syntax","unknown_semantics"],[],"pure_no_io",["evidence.cue"]),
        lib("library.platform.compiler_contract","semantic.compilation_run",["capability.compile_solution"],["CompilationRequest","CompilationOutcome","CompilerGap"],["compile"],["pass_profile","partiality_policy"],["same_inputs_editions_and_receipts_are_reproducible"],["unsat","unknown","refused"],["library.platform.intent_contract"],"pure_effect_intents",["evidence.crossplane.composition","evidence.terraform.plan"]),
        lib("library.platform.binding_evidence","semantic.binding_decision",["capability.bind_offers"],["CapabilityRequirement","CapabilityOffer","BindingDecision"],["evaluate_offer","solve_binding"],["objective_order","unknown_compatibility_policy"],["feasible_is_not_qualified","brand_is_nonsemantic"],["no_candidate","unsat","unknown"],["library.platform.compiler_contract"],"pure_no_io",["evidence.kubernetes.conformance"]),
        lib("library.platform.release_evidence","semantic.release_evidence",["capability.emit_release_evidence"],["EvidenceBundle","AttestationRef","ReleaseVerdict"],["assemble_evidence","evaluate_release"],["evidence_policy","expiry_policy"],["signature_is_not_truth","qualification_is_scoped"],["missing_evidence","expired_evidence"],["library.platform.binding_evidence"],"pure_effect_intents",["evidence.slsa12","evidence.in_toto"]),
        lib("library.platform.blueprint","semantic.platform_blueprint",["capability.publish_blueprint"],["Blueprint","CapabilityRequirement","PavedPathRef"],["validate_blueprint","publish_intent"],["edition_policy","escape_hatch_policy"],["template_is_not_instance"],["unknown_capability","invalid_blueprint"],["library.platform.intent_contract"],"pure_effect_intents",["evidence.cncf.platforms","evidence.backstage.templates"]),
        lib("library.platform.paved_path_runtime","semantic.paved_path",["capability.instantiate_paved_path"],["InstantiationIntent","PlatformInstance","ConformanceReceipt"],["plan_instantiation","reconcile_instance"],["provider_binding","rollback_policy"],["rendered_resources_are_not_ready_service"],["unbound_provider","reconciliation_unknown"],["library.platform.blueprint","library.platform.release_evidence"],"effect_intents_and_receipts",["evidence.crossplane.composition","evidence.backstage.templates"],"runtime_boundary"),
        lib("library.platform.resource_vector","semantic.resource_demand",["capability.normalize_resource_vector"],["ResourceClass","ResourceQuantity","ResourceDemand","ResourceOffer"],["normalize_quantity","compare_vectors"],["unit_profile","hardness"],["resource_comparison_is_dimension_aware"],["unknown_unit","incomparable_offer"],[],"pure_no_io",["evidence.kubernetes.resources"]),
        lib("library.platform.admission","semantic.resource_admission",["capability.admit_work"],["AdmissionRequest","AdmissionDecision","Precharge"],["admit"],["quota_policy","budget_policy","capacity_policy"],["hard_constraints_never_weaken","quota_is_not_capacity"],["quota_exhausted","budget_exhausted","capacity_unknown"],["library.platform.resource_vector"],"pure_effect_intents",["evidence.kubernetes.quota","evidence.kubernetes.dra"]),
        lib("library.platform.placement","semantic.placement",["capability.place_work"],["PlacementProblem","PlacementCandidate","PlacementResult"],["place"],["scheduler_policy","assurance_level"],["feasible_is_not_optimal","hard_constraints_precede_scoring"],["infeasible","timeout_without_incumbent"],["library.platform.resource_vector","library.platform.admission"],"pure_no_io",["evidence.kubernetes.scheduling","evidence.paper.drf"]),
        lib("library.platform.allocation_lease","semantic.reservation_allocation",["capability.reserve_allocate"],["Reservation","Allocation","Lease","FencingToken"],["reserve","allocate","renew","release"],["lease_duration","fencing_policy"],["reservation_is_not_allocation","lease_without_effect_fencing_is_not_safe"],["stale_token","expired_lease","allocation_conflict"],["library.platform.admission","library.platform.placement"],"effect_intents_and_receipts",["evidence.kubernetes.dra","evidence.kubernetes.controllers"],"runtime_boundary"),
        lib("library.platform.runtime_attempt","semantic.runtime_attempt",["capability.execute_attempt","capability.record_runtime_receipt"],["WorkUnit","Attempt","CancellationState","RuntimeReceipt"],["start_attempt","request_cancel","record_terminal"],["target_profile","retry_policy"],["retry_creates_new_attempt","timeout_is_not_terminal_fact"],["unsupported_target","cancel_unknown","provider_unknown"],["library.platform.allocation_lease"],"effect_intents_and_receipts",["evidence.oci.runtime","evidence.wasi.p2","evidence.opentelemetry.semconv"],"runtime_boundary"),
        lib("library.platform.meter","semantic.usage_meter",["capability.meter_usage"],["UsageEvent","MeterDefinition","UsageAggregate"],["validate_event","aggregate_usage"],["dedup_scope","window","correction_policy"],["event_is_not_aggregate","usage_is_not_charge"],["duplicate_event","late_correction_unsupported"],[],"effect_intents_and_receipts",["evidence.openmeter.events","evidence.openmeter.meters"],"runtime_boundary"),
        lib("library.platform.cost_normalization","semantic.cost_normalization",["capability.normalize_cost"],["ProviderCostRecord","FocusRecord","NormalizationResidual"],["normalize_cost"],["focus_edition","unknown_column_policy"],["normalization_preserves_source_occurrence_and_residuals"],["unsupported_provider_field","semantic_loss_unknown"],[],"pure_no_io",["evidence.focus12"]),
        lib("library.platform.cost_allocation","semantic.cost_allocation",["capability.allocate_cost"],["AllocationRule","AllocationBasis","AllocatedCost"],["allocate_cost","reconcile_allocation"],["shared_cost_policy","idle_cost_policy"],["allocated_total_reconciles_or_reports_residual"],["missing_basis","unreconciled_total"],["library.platform.meter","library.platform.cost_normalization"],"pure_no_io",["evidence.opencost.spec","evidence.finops.framework"]),
        lib("library.platform.budget_precharge","semantic.budget_precharge",["capability.precharge_budget"],["Budget","Precharge","BudgetReceipt"],["reserve_budget","reconcile_spend"],["overrun_policy","expiry_policy"],["budget_is_not_capacity","precharge_is_not_final_cost"],["insufficient_budget","stale_precharge"],["library.platform.cost_allocation"],"effect_intents_and_receipts",["evidence.finops.framework"],"runtime_boundary"),
        lib("library.platform.qualification","semantic.qualification_receipt",["capability.qualify_provider"],["QualificationProfile","Assessment","QualificationReceipt"],["run_assessment","issue_verdict","revoke"],["independence","expiry","revocation"],["documentation_is_not_execution","one_profile_is_not_universal"],["subject_mismatch","profile_incomplete","evidence_stale"],["library.platform.binding_evidence","library.platform.release_evidence"],"effect_intents_and_receipts",["evidence.kubernetes.conformance","evidence.slsa12"],"assurance_boundary"),
        lib("library.platform.telemetry","semantic.runtime_receipt",["capability.record_runtime_receipt"],["TelemetryEnvelope","SignalIdentity","CollectionReceipt"],["record_signal","correlate_receipt"],["semconv_edition","sampling_policy"],["telemetry_is_observation","sampling_is_explicit"],["unknown_semantics","collection_gap"],[],"effect_intents_and_receipts",["evidence.opentelemetry.spec","evidence.opentelemetry.semconv"],"adapter_boundary"),
        lib("library.platform.service_level","semantic.service_health",["capability.evaluate_service_health"],["SliObservation","SloDefinition","HealthVerdict"],["evaluate_slo"],["window","missing_data_policy","error_budget_policy"],["slo_is_not_sla","telemetry_is_not_health"],["insufficient_observation","indeterminate_health"],["library.platform.telemetry"],"pure_no_io",["evidence.openslo","evidence.google.sre"]),
        lib("library.platform.incident_case","semantic.incident_case",["capability.manage_incident"],["IncidentId","Impact","Timeline","RecoveryEvidence"],["open_incident","record_mitigation","close_with_evidence"],["severity_policy","closure_policy"],["alert_is_not_incident","restoration_is_not_root_cause"],["unknown_impact","closure_evidence_missing"],["library.platform.service_level"],"effect_intents_and_receipts",["evidence.cncf.operational_excellence","evidence.iso20000"],"runtime_boundary"),
        lib("library.platform.exit_manifest","semantic.release_evidence",["capability.emit_release_evidence"],["ExitManifest","ActiveWorkDisposition","ResidualObligation"],["plan_exit","verify_export"],["cutover_policy","retention_policy"],["data_export_is_not_supplier_exit"],["dependency_unresolved","transfer_unverified"],["library.platform.release_evidence"],"effect_intents_and_receipts",["evidence.iso19941"],"runtime_boundary"),
    ]

    requirements = [
        {"requirement_id":f"requirement.platform.{cap.removeprefix('capability.').replace('.', '_')}","consumer_ref":consumer,"capability_ref":cap,"binding_phase":phase,"minimum_qualified_offers":1,"status":"unbound","refusal":refusal}
        for cap, consumer, phase, refusal in [
            ("capability.parse_intent","product.solution_compiler","compile_time","no_qualified_intent_core"),
            ("capability.compile_solution","product.solution_compiler","compile_time","no_qualified_compiler_core"),
            ("capability.bind_offers","product.solution_compiler","compile_time","no_qualified_binding_engine"),
            ("capability.qualify_provider","component.provider_qualification","qualification_time","qualification_subsystem_unbound"),
            ("capability.publish_blueprint","product.data_product_developer_platform","compile_time","no_qualified_blueprint_core"),
            ("capability.instantiate_paved_path","product.data_product_developer_platform","deployment_time","no_qualified_platform_runtime"),
            ("capability.evaluate_platform_conformance","product.data_product_developer_platform","qualification_time","platform_conformance_unbound"),
            ("capability.normalize_resource_vector","product.runtime_resource_control","compile_time","resource_algebra_unbound"),
            ("capability.admit_work","product.runtime_resource_control","runtime","admission_core_unbound"),
            ("capability.place_work","product.runtime_resource_control","runtime","scheduler_unbound"),
            ("capability.reserve_allocate","product.runtime_resource_control","runtime","allocator_unbound"),
            ("capability.execute_attempt","product.runtime_resource_control","runtime","runtime_backend_unbound"),
            ("capability.meter_usage","product.finops_allocation","runtime","meter_unbound"),
            ("capability.normalize_cost","product.finops_allocation","runtime","cost_normalizer_unbound"),
            ("capability.allocate_cost","product.finops_allocation","runtime","allocation_core_unbound"),
            ("capability.precharge_budget","product.finops_allocation","runtime","budget_core_unbound"),
            ("capability.evaluate_service_health","pattern.platform_operations","runtime","service_health_capability_unbound"),
            ("capability.manage_incident","pattern.platform_operations","runtime","incident_capability_unbound"),
        ]
    ]

    offers = [
        {"offer_id":"offer.crossplane.composition","provider_ref":"implementation.crossplane","capability_refs":["capability.compile_solution","capability.instantiate_paved_path"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.crossplane.composition"]},
        {"offer_id":"offer.backstage.platform","provider_ref":"implementation.backstage","capability_refs":["capability.publish_blueprint","capability.instantiate_paved_path"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.backstage.catalog","evidence.backstage.templates"]},
        {"offer_id":"offer.kubernetes.runtime","provider_ref":"implementation.kubernetes","capability_refs":["capability.normalize_resource_vector","capability.admit_work","capability.place_work","capability.reserve_allocate","capability.execute_attempt"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.kubernetes.resources","evidence.kubernetes.scheduling","evidence.kubernetes.dra"]},
        {"offer_id":"offer.opencost.allocation","provider_ref":"implementation.opencost","capability_refs":["capability.allocate_cost"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.opencost.spec"]},
        {"offer_id":"offer.openmeter.meter","provider_ref":"implementation.openmeter","capability_refs":["capability.meter_usage"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.openmeter.events","evidence.openmeter.meters"]},
        {"offer_id":"offer.opentelemetry.telemetry","provider_ref":"implementation.opentelemetry","capability_refs":["capability.record_runtime_receipt"],"qualified_implementation_count":0,"portable":False,"status":"observed_unqualified","evidence_refs":["evidence.opentelemetry.spec","evidence.opentelemetry.semconv"]},
    ]

    relations = [
        {"relation_id":f"relation.suite.packages.{ident.split('.')[-1]}","from_ref":"suite.data_analytics_platform","predicate":"packages","to_ref":ident,"binding_phase":"authoring"}
        for ident in ["product.solution_compiler","product.data_product_developer_platform","product.runtime_resource_control","product.finops_allocation"]
    ] + [
        {"relation_id":"relation.pattern.realizes.suite","from_ref":"pattern.composable_data_platform","predicate":"realizes","to_ref":"suite.data_analytics_platform","binding_phase":"authoring"},
        {"relation_id":"relation.compiler.requires.qualification","from_ref":"product.solution_compiler","predicate":"requires","to_ref":"component.provider_qualification","binding_phase":"qualification_time"},
        {"relation_id":"relation.platform.requires.runtime","from_ref":"product.data_product_developer_platform","predicate":"requires","to_ref":"product.runtime_resource_control","binding_phase":"deployment_time"},
        {"relation_id":"relation.runtime.requires.identity","from_ref":"product.runtime_resource_control","predicate":"requires","to_ref":"neighbor.identity_policy","binding_phase":"runtime"},
        {"relation_id":"relation.finops.requires.billing","from_ref":"product.finops_allocation","predicate":"requires","to_ref":"neighbor.billing_finance","binding_phase":"runtime"},
        {"relation_id":"relation.operations.requires.telemetry","from_ref":"pattern.platform_operations","predicate":"requires","to_ref":"neighbor.telemetry_observability","binding_phase":"runtime"},
        {"relation_id":"relation.operations.requires.incident","from_ref":"pattern.platform_operations","predicate":"requires","to_ref":"neighbor.incident_service_management","binding_phase":"runtime"},
    ]

    crosswalks = [
        {"legacy_ref":"candidate.product.solution_compiler","canonical_refs":["product.solution_compiler"],"disposition":"replace_exact"},
        {"legacy_ref":"candidate.product.data_product_developer_platform","canonical_refs":["product.data_product_developer_platform"],"disposition":"replace_exact"},
        {"legacy_ref":"candidate.product.runtime_resource_control","canonical_refs":["product.runtime_resource_control"],"disposition":"replace_exact"},
        {"legacy_ref":"candidate.product.finops_allocation","canonical_refs":["product.finops_allocation"],"disposition":"replace_exact"},
        {"legacy_ref":"candidate.product.provider_qualification_broker","canonical_refs":["component.provider_qualification","semantic.qualification_profile","semantic.qualification_receipt"],"disposition":"reclassify_compiler_subsystem"},
        {"legacy_ref":"candidate.product.platform_operations","canonical_refs":["pattern.platform_operations","neighbor.telemetry_observability","neighbor.incident_service_management"],"disposition":"split_composition_and_defer_products"},
    ]

    negative_rows = [
        ("negative.plan_effect","Compiled plan is not an authorized or completed effect.","require_effect_intent_and_receipt"),
        ("negative.render_ready","Rendered resources are not a ready service.","require_reconciliation_and_acceptance"),
        ("negative.platform_portal","Developer portal is not the whole platform.","refuse_interface_product_collapse"),
        ("negative.template_instance","Blueprint or template is not a deployed instance.","refuse_identity_collapse"),
        ("negative.qualification_product","Qualification subsystem is not a product by internal service name.","reclassify_compiler_subsystem"),
        ("negative.docs_qualification","Provider documentation is not a qualification receipt.","require_executed_assessment"),
        ("negative.conformance_universal","One conformance profile is not universal portability.","scope_receipt"),
        ("negative.quota_capacity","Quota availability is not physical capacity.","evaluate_capacity_separately"),
        ("negative.budget_capacity","Budget authority is not physical capacity.","evaluate_capacity_separately"),
        ("negative.admission_placement","Admission is not placement or allocation.","retain_state_boundaries"),
        ("negative.reservation_allocation","Reservation is not allocation.","retain_state_boundaries"),
        ("negative.timeout_terminal","Caller timeout is not a terminal provider fact.","reconcile_unknown_outcome"),
        ("negative.retry_attempt","Retry cannot reuse attempt identity.","create_new_attempt"),
        ("negative.usage_cost","Runtime usage is not provider cost or invoice.","require_cost_mapping"),
        ("negative.normalized_allocated","Normalized cost is not allocated cost.","apply_governed_allocation"),
        ("negative.telemetry_health","Telemetry signal is not service health.","evaluate_slo"),
        ("negative.alert_incident","Alert occurrence is not incident case.","require_incident_admission"),
        ("negative.operations_product","Telemetry, SLO and incident packaging is not one semantic owner.","split_composition"),
        ("negative.agent_authority","Generated plan or diagnosis has no qualification or effect authority.","require_deterministic_validation"),
        ("negative.ai_prefix","Platform capabilities do not become separate AI products by automation modality.","remove_optional_extension_and_retest"),
    ]
    negative_tests = [{"test_id":i,"prohibited_claim":c,"expected_result":r} for i,c,r in negative_rows]

    exact_maps: dict[str, list[str]] = {
        "library.platform.intent_contract":["library.csp.intent.intent-vocabulary","library.csp.intent.intent-conformance"],
        "library.platform.compiler_contract":["library.gmo.compiler_contract"],
        "library.platform.binding_evidence":["library.lpe.compiler-evidence-binding"],
        "library.platform.release_evidence":["library.lpe.evidence-bundle","library.lpe.evidence-evaluation"],
        "library.platform.blueprint":["library.platform-commercial-support.catalog-repository-port"],
        "library.platform.paved_path_runtime":["library.platform-commercial-support.exit-manifest"],
        "library.platform.resource_vector":["library.runtime-resource.resource-quantity","library.runtime-resource.resource-topology","library.runtime-resource.demand-offer-compatibility"],
        "library.platform.admission":["library.runtime-resource.admission","library.runtime-resource.quota-ledger","library.runtime-resource.budget-precharge"],
        "library.platform.placement":["library.runtime-resource.placement-constraints","library.runtime-resource.scheduler-policy-spi"],
        "library.platform.allocation_lease":["library.runtime-resource.reservation-ledger","library.runtime-resource.lease-fencing"],
        "library.platform.runtime_attempt":["library.runtime-resource.attempt-state","library.runtime-resource.deadline-cancellation","library.runtime-resource.runtime-receipts"],
        "library.platform.meter":["library.platform-commercial-support.meter_definition","library.platform-commercial-support.usage_event","library.platform-commercial-support.usage_aggregation","library.platform-commercial-support.usage-journal-port"],
        "library.platform.cost_allocation":["library.platform-commercial-support.allocation-core"],
        "library.platform.budget_precharge":["library.platform-commercial-support.commercial-credit-preauthorization"],
        "library.platform.qualification":["library.runtime-resource.conformance-oracles","library.lpe.evidence-evaluation"],
        "library.platform.telemetry":[
            "library.telemetry.attribution_core",
            "library.telemetry.schema_conventions",
            "library.telemetry.trace_graph",
            "library.telemetry.metric_stream",
            "library.telemetry.log_event",
            "library.telemetry.profile_sample",
            "library.telemetry.propagation_context",
            "library.telemetry.observation_reduction",
            "library.telemetry.cross_signal_correlation",
            "library.telemetry.export_delivery",
        ],
        "library.platform.service_level":["library.platform-commercial-support.slo_evaluator"],
        "library.platform.incident_case":["library.platform-commercial-support.incident-routing-port","library.platform-commercial-support.incident_lifecycle"],
        "library.platform.exit_manifest":["library.platform-commercial-support.exit-manifest","library.platform-commercial-support.export-transfer-port"],
    }
    gap_libs = {"library.platform.cost_normalization":"gap.platform.focus_normalization_library"}
    binding_maps = []
    for local in [row["library_id"] for row in libraries]:
        refs = exact_maps.get(local, [])
        binding_maps.append({
            "binding_map_id":f"binding.platform.{local.split('.')[-1]}",
            "abstract_library_ref":local,
            "concrete_library_refs":refs,
            "compiler_disposition":"structurally_projected_unqualified" if refs else "blocked_typed_gap",
            "gap_ref":gap_libs.get(local),
            "portable_offer":False,
        })
    binding_gaps = [
        {"gap_id":"gap.platform.focus_normalization_library","abstract_library_ref":"library.platform.cost_normalization","reason":"FOCUS semantics are researched but no exact reusable normalization contract appears in the compiler library registry.","resolution":"Adjudicate exact FOCUS types, residual/loss laws and two independent implementations before binding."},
    ]

    return enrich_platform_products(enrich_solution_compiler({
        "contract_id":"contract.product_adjudication.platform_control.v0_1_0",
        "edition":1,
        "status":"evidence_backed_adjudicated_candidate_not_ratified",
        "scope":"Horizontal intent compilation, data-product developer platform, runtime resource control, provider qualification, platform operations and FinOps allocation boundaries.",
        "negative_scope":"Does not ratify products, qualify providers, grant effect authority, own business/domain intent, collapse telemetry into health, or treat cost normalization as billing truth.",
        "non_collapse_laws":[
            "intent != compiled plan != effect intent != effect receipt != accepted outcome",
            "platform != portal != template != provider bundle",
            "provider offer != artifact != occurrence != target != qualification receipt",
            "entitlement != authorization != quota != budget != capacity",
            "admission != placement != reservation != allocation != lease != execution",
            "requested != reserved != allocated != consumed != normalized cost != allocated cost != charge != invoice",
            "telemetry != service health != incident != problem != support case",
            "conformance to one profile != universal portability",
            "suite packaging does not transfer semantic ownership",
            "optional model or agent proposal does not create meaning, proof, qualification, authority, effect or product identity",
        ],
        "sources":sources,"artifact_kinds":kinds,"artifacts":artifacts,"boundary_decisions":decisions,
        "ownership":ownership,"libraries":libraries,"requirements":requirements,"offers":offers,
        "relations":relations,"crosswalks":crosswalks,"negative_tests":negative_tests,
        "binding_maps":binding_maps,"binding_gaps":binding_gaps,
    }))


def source_bytes() -> bytes:
    return (json.dumps(source(),ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode()


if __name__ == "__main__":
    SOURCE.write_bytes(source_bytes())
    print(f"WROTE {SOURCE}")
