#!/usr/bin/env python3
"""Canonical declarative source for model, feature, inference and decision products."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"
AXES = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]


def ev(ident: str, title: str, publisher: str, uri: str, claim: str, limit: str, cls: str = "official_specification_or_documentation") -> dict[str, Any]:
    return {"source_id": ident, "source_class": cls, "title": title, "publisher": publisher, "uri": uri, "retrieved_at": "2026-08-26", "claim": claim, "scope_limit": limit}


def art(ident: str, kind: str, name: str, definition: str, refs: list[str], owner: str | None = None, adoption: bool = False, operated: bool = False, status: str = "candidate") -> dict[str, Any]:
    return {"artifact_id": ident, "kind": kind, "name": name, "status": status, "semantic_owner_ref": owner, "adoption_unit": adoption, "operated": operated, "definition": definition, "evidence_refs": refs}


def split(scores: list[int], refs: list[str], label: str) -> dict[str, Any]:
    return {axis: {"score": score, "finding": f"{label}: evidence for the {axis} boundary is scoped; scores below two preserve an unresolved independence or qualification gap.", "evidence_refs": refs} for axis, score in zip(AXES, scores, strict=True)}


def lib(ident: str, owner: str, capability: str, types: list[str], operations: list[str], decisions: list[str], laws: list[str], refusals: list[str], deps: list[str], effect: str, refs: list[str], cls: str = "semantic_pure") -> dict[str, Any]:
    return {"library_id": ident, "class": cls, "owner_ref": owner, "provides": [capability], "types": types, "operations": operations, "decisions": decisions, "invariants": laws, "refusals": refusals, "dependencies": deps, "effect_boundary": effect, "evidence_refs": refs}


def source() -> dict[str, Any]:
    sources = [
        ev("evidence.nist.ai_rmf", "Artificial Intelligence Risk Management Framework 1.0", "NIST", "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf", "Separates lifecycle actors and Govern, Map, Measure and Manage functions across design, build, validation, deployment and monitoring.", "A risk framework does not qualify a model, provider, decision or local control."),
        ev("evidence.nist.aria", "ARIA Program", "NIST", "https://ai-challenges.nist.gov/aria", "Treats testing, evaluation, verification and validation as contextual and empirical activities.", "Program material does not provide a universal evaluation oracle."),
        ev("evidence.mlflow.tracking", "MLflow Tracking", "MLflow", "https://mlflow.org/docs/latest/ml/tracking/", "Defines runs, experiments, parameters, code versions, datasets, metrics and artifacts.", "Tracking an occurrence does not establish reproducibility, validity or promotion authority."),
        ev("evidence.mlflow.registry", "MLflow Model Registry Workflows", "MLflow", "https://mlflow.org/docs/latest/ml/model-registry/workflow/", "Documents registered models, versions, aliases, tags, source runs and environment-oriented workflows.", "A registry alias or tag is not validation, approval, deployment or observed service state."),
        ev("evidence.mlflow.model", "MLflow Model", "MLflow", "https://mlflow.org/docs/latest/ml/model/", "Documents packaged model metadata, signatures, flavors and custom inference code.", "An MLflow flavor is one packaging contract and not universal model semantics or target qualification."),
        ev("evidence.mlflow.evaluation", "MLflow Model Evaluation", "MLflow", "https://mlflow.org/docs/latest/ml/evaluation", "Documents task-specific evaluation, custom metrics, artifacts and threshold validation.", "Generated metrics are scoped to the exact dataset, evaluator and configuration; they do not grant deployment authority."),
        ev("evidence.kubeflow.pipelines", "Kubeflow Pipelines Runs", "Kubeflow", "https://www.kubeflow.org/docs/components/pipelines/concepts/run/", "Defines immutable run logs, runtime graphs, artifacts, recurring runs and concurrency limits.", "Pipeline success does not prove model validity, business fitness or artifact qualification."),
        ev("evidence.kubeflow.trainer", "Kubeflow Trainer", "Kubeflow", "https://www.kubeflow.org/docs/components/trainer/overview/", "Documents TrainJob and runtime APIs for distributed model training.", "A training runtime owns execution mechanics, not target meaning, study validity or model approval."),
        ev("evidence.kserve.protocol", "Open Inference Protocol V2", "KServe", "https://kserve.github.io/website/docs/concepts/architecture/data-plane/v2-protocol", "Defines inference, model metadata, model readiness and server health APIs with version-addressed model endpoints.", "Protocol compatibility does not establish numerical equivalence, semantic fitness, SLOs or decision authority."),
        ev("evidence.kserve.control", "KServe Control Plane API", "KServe", "https://kserve.github.io/website/docs/reference/crd-api", "Defines InferenceService desired/status state, runtimes, transformers, explainers, batching, scaling and canary traffic.", "A reconciled resource or ready endpoint is not a validated prediction or accepted business outcome."),
        ev("evidence.kserve.canary", "KServe Canary Rollout", "KServe", "https://kserve.github.io/website/docs/model-serving/predictive-inference/rollout-strategies/canary-example", "Documents versioned rollout and traffic allocation between model revisions.", "Traffic exposure is not promotion approval and requires separately governed evaluation and rollback criteria."),
        ev("evidence.feast.feature_view", "Feast Feature View", "Feast", "https://docs.feast.dev/getting-started/concepts/feature-view", "Defines entity-bound time-series feature groups used for historical generation, materialization and online lookup.", "A feature schema does not own source-domain meaning and implementation-specific validation can be warning-only."),
        ev("evidence.feast.pit", "Feast Point-in-Time Joins", "Feast", "https://docs.feast.dev/getting-started/concepts/point-in-time-joins", "Documents reproduction of feature state at a historical event time.", "Project documentation does not prove correctness for every source, late-data rule or temporal convention."),
        ev("evidence.feast.online", "Feast Online Store", "Feast", "https://docs.feast.dev/getting-started/components/online-store", "Documents low-latency retrieval of latest materialized feature values per entity key.", "Latest-value storage is not historical truth, training parity or a vector-index contract."),
        ev("evidence.feast.architecture", "Feast Components Overview", "Feast", "https://docs.feast.dev/getting-started/components/overview", "Separates external feature transformation, registry apply, historical retrieval, materialization and online retrieval.", "One project architecture does not qualify providers or require these components to be one deployment."),
        ev("evidence.onnx.ir", "ONNX IR Specification", "ONNX", "https://onnx.ai/onnx/repo-docs/IR.html", "Defines versioned computation graphs, data types, operators and model metadata independently of runtime implementation.", "ONNX serialization does not prove transformation fidelity, runtime support, numerical equivalence or model fitness."),
        ev("evidence.onnx.versioning", "ONNX Versioning", "ONNX", "https://onnx.ai/onnx/repo-docs/Versioning.html", "Separates IR, operator-set and model versions and compatibility changes.", "Version compatibility is not semantic or predictive equivalence."),
        ev("evidence.pmml", "PMML 4.4.1", "Data Mining Group", "https://dmg.org/pmml/v4-4-1/GeneralStructure.html", "Defines a portable predictive-model interchange structure for named model families.", "PMML coverage and parser acceptance do not prove identical scoring or deployment fitness."),
        ev("evidence.model_cards", "Model Cards for Model Reporting", "Google Research", "https://research.google/pubs/model-cards-for-model-reporting/", "Proposes intended-use, limitation and slice-specific performance reporting for trained models.", "A model card is authored evidence, not an automatically true or sufficient qualification receipt.", "primary_research"),
        ev("evidence.data_cards", "Data Cards", "Google Research", "https://research.google/pubs/data-cards-purposeful-and-transparent-dataset-documentation-for-responsible-ai/", "Documents dataset provenance, collection, annotation, intended use and lifecycle reporting needs.", "Documentation cannot replace exact data cuts, lineage, rights or fitness evaluation.", "primary_research"),
        ev("evidence.evidently", "Evidently", "Evidently", "https://github.com/evidentlyai/evidently", "Documents offline evaluation and operated monitoring over quality, performance and drift measures.", "A tool's metrics and defaults are implementation claims and require task-, slice- and threshold-specific validation."),
        ev("evidence.omg.dmn", "Decision Model and Notation 1.5", "Object Management Group", "https://www.omg.org/spec/DMN/1.5/", "Defines decision requirements, decision logic, FEEL and decision-service interchange with normative machine-readable artifacts.", "DMN conformance does not authorize an external effect or prove that business inputs and policies are correct."),
        ev("evidence.omg.dmn_xsd", "DMN 1.5 XML Schema", "Object Management Group", "https://www.omg.org/spec/DMN/20230324/DMN15.xsd", "Provides the normative XML carrier for DMN 1.5 models.", "Schema validity is not semantic completeness, conflict freedom, execution correctness or business approval."),
        ev("evidence.kie.dmn", "Apache KIE DMN", "Apache KIE", "https://kie.apache.org/docs/components/drools/drools_dmn/", "Documents an executable DMN engine, decision graphs, decision tables, static analysis and TCK posture.", "Project conformance claims remain unqualified until exact edition, configuration and target receipts are executed."),
        ev("evidence.kie.runtime", "Drools DMN Runtime", "Apache KIE", "https://kie.apache.org/docs/10.1.x/drools/drools/DMN/index.html", "Documents FEEL, hit policies, strict-conformance and runtime type-check choices and decision-service execution.", "Extensions, defaults and configuration can change behavior; a returned decision is not an authorized effect."),
        ev("evidence.opa", "Open Policy Agent", "Open Policy Agent", "https://www.openpolicyagent.org/docs", "Separates policy decision from enforcement and evaluates structured input against policy and data.", "A general policy engine is not automatically a DMN business-decision service and a decision is not enforcement."),
        ev("evidence.opa.logs", "OPA Decision Logs", "Open Policy Agent", "https://www.openpolicyagent.org/docs/management-decision-logs", "Defines decision occurrence logging with decision identity, input and bundle metadata.", "Decision logs can contain sensitive data and are evidence of evaluation, not effect completion."),
        ev("evidence.kubernetes.jobs", "Kubernetes Jobs", "Kubernetes", "https://kubernetes.io/docs/concepts/workloads/controllers/job/", "Defines bounded batch execution, attempts, completion and failure policies.", "A batch execution primitive does not create a distinct batch-prediction product or model-validity claim."),
        ev("evidence.opentelemetry", "OpenTelemetry Specification", "OpenTelemetry", "https://opentelemetry.io/docs/specs/otel/", "Defines telemetry APIs, SDKs, data and transport for traces, metrics and logs.", "Telemetry records operational observations, not predictive validity, drift conclusions or causal diagnosis."),
        ev("evidence.openinference", "OpenInference Semantic Conventions", "OpenInference", "https://github.com/Arize-ai/openinference/tree/main/spec", "Defines trace attributes for model inference and related components.", "Trace-shape interoperability does not prove trace completeness, model quality or portability."),
        ev("evidence.mcp", "Model Context Protocol 2025-06-18", "Model Context Protocol", "https://modelcontextprotocol.io/specification/2025-06-18", "Defines versioned client/server capabilities for tools, resources, prompts and sampling.", "Protocol negotiation and tool visibility never create business authority or tool-effect permission."),
        ev("evidence.mcp.security", "MCP Security Best Practices", "Model Context Protocol", "https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices", "Documents confused-deputy, token passthrough, session and authorization risks.", "Guidance identifies controls but does not prove any implementation safe."),
        ev("evidence.a2a", "Agent2Agent Protocol", "A2A Project", "https://a2a-protocol.org/latest/specification/", "Defines task, message, artifact and agent-card exchange between independently operated components.", "A protocol peer is not trusted, qualified, authorized or semantically equivalent by discovery alone."),
        ev("evidence.jsonschema", "JSON Schema 2020-12", "JSON Schema", "https://json-schema.org/draft/2020-12", "Defines structural validation for JSON instances.", "Structural validity does not prove domain meaning, truth, authority or safety."),
        ev("evidence.slsa", "SLSA 1.2", "OpenSSF", "https://slsa.dev/spec/v1.2/", "Defines source and build provenance requirements.", "Provenance identifies production history but does not prove predictive or decision conformance."),
        ev("evidence.w3c.prov", "PROV-O", "W3C", "https://www.w3.org/TR/prov-o/", "Defines entities, activities, agents and derivation relationships.", "Provenance does not establish causality, correctness or authority."),
    ]

    kinds = [
        {"kind": "architecture_pattern", "definition": "A reusable arrangement without independent adoption or semantic ownership."},
        {"kind": "suite", "definition": "Packaging of products and capabilities without transferred meaning."},
        {"kind": "product", "definition": "An independently adopted and operated outcome promise."},
        {"kind": "control_component", "definition": "A subsystem that lacks its own complete adoption/support/exit promise."},
        {"kind": "capability", "definition": "Typed behavior required or offered by products and implementations."},
        {"kind": "semantic_contract", "definition": "Owner of a meaning, lifecycle, invariants and refusals."},
        {"kind": "standard", "definition": "An exact external edition specializing a contract."},
        {"kind": "library_contract", "definition": "A reusable pure or explicitly effect-bounded implementation seam."},
        {"kind": "implementation", "definition": "A provider artifact or adapter that may offer capabilities but owns no canonical meaning."},
        {"kind": "neighbor", "definition": "A separate bounded context imported through an explicit contract."},
    ]

    artifacts = [
        art("pattern.model_decision_stack", "architecture_pattern", "Composable model and decision stack", "A dependency arrangement; not an AI platform or product.", ["evidence.nist.ai_rmf"]),
        art("suite.model_decision_products", "suite", "Model and decision product suite", "Commercial or internal packaging of six separately governed products.", ["evidence.mlflow.tracking", "evidence.feast.architecture", "evidence.omg.dmn"]),
        art("product.model_lifecycle", "product", "Predictive Model Engineering and Lifecycle", "Experiment, training-specification, fitted-artifact, registry, promotion and retirement journey for predictive models.", ["evidence.mlflow.tracking", "evidence.mlflow.registry", "evidence.kubeflow.pipelines", "evidence.nist.ai_rmf"], adoption=True, operated=True),
        art("product.feature_platform", "product", "Feature Definition and Serving Platform", "Governed feature definitions, point-in-time retrieval, materialization and online retrieval without owning source facts.", ["evidence.feast.feature_view", "evidence.feast.pit", "evidence.feast.online", "evidence.feast.architecture"], adoption=True, operated=True),
        art("product.online_inference", "product", "Predictive Inference Serving", "Version-pinned predictive deployments and online inference occurrences under rollout and service contracts.", ["evidence.kserve.protocol", "evidence.kserve.control", "evidence.kserve.canary"], adoption=True, operated=True),
        art("product.model_assurance", "product", "Predictive Model Evaluation and Monitoring", "Independent pre-deployment and production evaluation, slice evidence, drift findings and review cases.", ["evidence.nist.ai_rmf", "evidence.mlflow.evaluation", "evidence.evidently", "evidence.model_cards"], adoption=True, operated=True),
        art("product.decision_automation", "product", "Decision Modeling and Execution", "Versioned deterministic decision models and traceable decision-service invocations that stop before effect authority.", ["evidence.omg.dmn", "evidence.omg.dmn_xsd", "evidence.kie.dmn", "evidence.opa"], adoption=True, operated=True),
        art("product.optional_model_extension", "product", "Optional Model and Agent Extension Runtime", "Explicitly requested generative/model task execution producing typed claims, plans and tool proposals without domain or effect authority.", ["evidence.mcp", "evidence.a2a", "evidence.jsonschema"], adoption=True, operated=True),
        art("component.model_registry", "control_component", "Model registry", "Version and alias registry inside the model lifecycle product.", ["evidence.mlflow.registry"]),
        art("component.training_runtime", "control_component", "Training runtime provider", "Effectful execution provider for a typed training job; it does not own study or model approval.", ["evidence.kubeflow.trainer"]),
        art("component.batch_scoring", "control_component", "Batch scoring composition", "A dataflow/job composition of feature retrieval, a scoring kernel and governed output publication.", ["evidence.kubernetes.jobs", "evidence.feast.architecture"]),
        art("component.vector_index", "control_component", "Vector index capability", "An indexed retrieval mechanism belonging to search/index serving, not feature semantics.", ["evidence.feast.online"]),
        art("standard.onnx", "standard", "ONNX IR", "Versioned model graph and operator-set interchange contract.", ["evidence.onnx.ir", "evidence.onnx.versioning"]),
        art("standard.dmn15", "standard", "DMN 1.5", "Versioned decision model, notation, FEEL and interchange contract.", ["evidence.omg.dmn", "evidence.omg.dmn_xsd"]),
        art("standard.kserve_v2", "standard", "Open Inference Protocol V2", "Versioned inference request, response, metadata and readiness interface.", ["evidence.kserve.protocol"]),
        art("standard.mcp_2025_06", "standard", "MCP 2025-06-18", "Versioned optional extension protocol for tools, resources, prompts and sampling.", ["evidence.mcp"]),
        art("implementation.mlflow", "implementation", "MLflow", "Observed lifecycle/tracking/evaluation implementation; unqualified for this corpus.", ["evidence.mlflow.tracking", "evidence.mlflow.registry", "evidence.mlflow.evaluation"]),
        art("implementation.kubeflow", "implementation", "Kubeflow", "Observed pipeline/training implementation; unqualified for this corpus.", ["evidence.kubeflow.pipelines", "evidence.kubeflow.trainer"]),
        art("implementation.feast", "implementation", "Feast", "Observed feature-platform implementation; unqualified for this corpus.", ["evidence.feast.architecture"]),
        art("implementation.kserve", "implementation", "KServe", "Observed inference-serving implementation; unqualified for this corpus.", ["evidence.kserve.protocol", "evidence.kserve.control"]),
        art("implementation.evidently", "implementation", "Evidently", "Observed evaluation/monitoring implementation; unqualified for this corpus.", ["evidence.evidently"]),
        art("implementation.drools", "implementation", "Apache KIE Drools DMN", "Observed decision runtime implementation; unqualified for this corpus.", ["evidence.kie.dmn", "evidence.kie.runtime"]),
        art("implementation.model_extension_adapter", "implementation", "Model extension adapter", "Provider-neutral placeholder for an exact optional model/agent adapter occurrence; no provider is qualified.", ["evidence.mcp", "evidence.a2a"]),
        art("neighbor.runtime_resource", "neighbor", "Runtime and resource control", "Owns execution admission, placement, scheduling, attempts, cancellation and resource receipts.", ["evidence.kubernetes.jobs"]),
        art("neighbor.dataflow", "neighbor", "Dataflow execution", "Owns batch/stream graph execution, checkpoints and output delivery.", ["evidence.kubeflow.pipelines"]),
        art("neighbor.search_index", "neighbor", "Search and index serving", "Owns indexed retrieval including vector retrieval and ranking profiles.", ["evidence.feast.online"]),
        art("neighbor.source_truth", "neighbor", "Source and analytical data truth", "Owns business facts, entity identity, valid/recorded time and corrections.", ["evidence.data_cards"]),
        art("neighbor.identity_policy", "neighbor", "Identity, authorization and delegation", "Owns principals, permissions, delegation, revocation and effect authorization.", ["evidence.opa"]),
        art("neighbor.effect_runtime", "neighbor", "Authorized effect runtime", "Owns external command execution, compensation and effect receipts.", ["evidence.opa.logs"]),
        art("neighbor.data_use_policy", "neighbor", "Data use and privacy policy", "Owns purpose, consent, disclosure, residency and retention authority.", ["evidence.nist.ai_rmf"]),
    ]

    semantics = [
        ("semantic.predictive_task", "Predictive task", "Target, population, grain, horizon, action proximity, loss and harmed-party contract.", ["evidence.nist.ai_rmf"]),
        ("semantic.experiment_run", "Model experiment run", "One immutable attempt with code, data, parameters, environment, metrics and artifacts.", ["evidence.mlflow.tracking"]),
        ("semantic.training_spec", "Training specification", "Resolved target/features/labels/splits/objective/estimator/runtime requirements before execution.", ["evidence.kubeflow.pipelines", "evidence.kubeflow.trainer"]),
        ("semantic.training_attempt", "Training attempt", "One runtime occurrence with exact inputs, target, seed posture, outputs and terminal receipt.", ["evidence.kubeflow.trainer"]),
        ("semantic.fitted_artifact", "Fitted model artifact", "Digest-bound learned parameters plus model structure, code, data cuts, configuration and environment evidence.", ["evidence.mlflow.model", "evidence.onnx.ir"]),
        ("semantic.model_edition", "Model edition", "Immutable released fitted-artifact identity with compatibility, intended-use and evidence references.", ["evidence.mlflow.registry", "evidence.model_cards"]),
        ("semantic.model_lifecycle_state", "Model lifecycle state", "Candidate, validated, approved, deployed, suspended and retired state under explicit authority.", ["evidence.mlflow.registry", "evidence.nist.ai_rmf"]),
        ("semantic.feature_definition", "Feature definition", "Entity key, value type, event/availability time, source, transformation and freshness contract.", ["evidence.feast.feature_view"]),
        ("semantic.feature_service", "Feature service", "Versioned selection of feature definitions bound to a consumer/model edition.", ["evidence.feast.architecture"]),
        ("semantic.historical_feature_cut", "Historical feature cut", "Point-in-time result over declared event, availability, recording, lateness and correction semantics.", ["evidence.feast.pit"]),
        ("semantic.feature_materialization", "Feature materialization", "Transfer occurrence from source/offline computation into an online store with cursor and receipt.", ["evidence.feast.online"]),
        ("semantic.online_feature_read", "Online feature read", "Entity-key lookup against an exact feature-service edition and observed freshness cut.", ["evidence.feast.online"]),
        ("semantic.inference_deployment", "Inference deployment", "Exact model edition, runtime, target, resource profile, endpoint revision and traffic policy.", ["evidence.kserve.control"]),
        ("semantic.inference_request", "Inference request", "Typed occurrence with request identity, model/revision binding, input schema and deadline.", ["evidence.kserve.protocol"]),
        ("semantic.prediction", "Prediction", "Model output bound to model edition, input occurrence, information cut and uncertainty semantics.", ["evidence.kserve.protocol", "evidence.nist.ai_rmf"]),
        ("semantic.inference_receipt", "Inference receipt", "Observed revision, target, timing, resource, completion/refusal and output digest evidence.", ["evidence.openinference", "evidence.opentelemetry"]),
        ("semantic.evaluation_plan", "Evaluation plan", "Task, dataset cut, slices, metrics, thresholds, comparators, multiplicity and reviewer contract.", ["evidence.mlflow.evaluation", "evidence.nist.ai_rmf"]),
        ("semantic.evaluation_result", "Evaluation result", "Metric and diagnostic evidence scoped to model, data cut, slice, evaluator and configuration.", ["evidence.mlflow.evaluation"]),
        ("semantic.model_validation", "Model validation verdict", "Policy evaluation over exact evidence with authority, expiry, residuals and defeaters.", ["evidence.nist.ai_rmf"]),
        ("semantic.model_monitor", "Model monitor", "Production observation plan for quality, drift, labels, slices, windows and missingness.", ["evidence.evidently"]),
        ("semantic.drift_finding", "Drift finding", "Scoped statistical or operational change result; never automatic proof of degradation or causality.", ["evidence.evidently"]),
        ("semantic.model_review_case", "Model review case", "Human-governed investigation, response, waiver, rollback, retraining or retirement record.", ["evidence.nist.ai_rmf"]),
        ("semantic.decision_model", "Decision model", "Versioned decision requirements, inputs, knowledge, logic, dependencies and output types.", ["evidence.omg.dmn"]),
        ("semantic.decision_table", "Decision table", "Rules, input/output clauses, allowed values and hit-policy semantics.", ["evidence.kie.runtime"]),
        ("semantic.decision_service", "Decision service", "Published subset of a decision model with exact input/output and edition contract.", ["evidence.omg.dmn"]),
        ("semantic.decision_invocation", "Decision invocation", "One decision-service evaluation with exact model edition, input, result and trace.", ["evidence.kie.runtime", "evidence.opa.logs"]),
        ("semantic.decision_result", "Decision result", "Deterministic evaluated output or typed refusal; not authorization or effect completion.", ["evidence.omg.dmn", "evidence.opa"]),
        ("semantic.extension_task", "Optional extension task", "Explicit model/agent use-site contract with fallback, budgets, schemas, tools and authority limits.", ["evidence.mcp", "evidence.a2a"]),
        ("semantic.extension_invocation", "Extension invocation", "Exact model/provider/target/context occurrence with nondeterminism and completion receipt.", ["evidence.mcp"]),
        ("semantic.generated_proposal", "Generated proposal", "Untrusted typed claim, plan or tool-call proposal awaiting deterministic validation.", ["evidence.mcp.security", "evidence.jsonschema"]),
    ]
    for ident, name, definition, refs in semantics:
        artifacts.append(art(ident, "semantic_contract", name, definition, refs))

    capability_specs = [
        ("capability.track_experiment", "Track model experiment", "semantic.experiment_run", ["evidence.mlflow.tracking"]),
        ("capability.compile_training", "Compile training specification", "semantic.training_spec", ["evidence.kubeflow.pipelines"]),
        ("capability.execute_training", "Execute training attempt", "semantic.training_attempt", ["evidence.kubeflow.trainer"]),
        ("capability.register_model", "Register immutable model edition", "semantic.model_edition", ["evidence.mlflow.registry"]),
        ("capability.transition_model", "Transition model lifecycle", "semantic.model_lifecycle_state", ["evidence.mlflow.registry", "evidence.nist.ai_rmf"]),
        ("capability.export_model", "Export model artifact and evidence", "semantic.fitted_artifact", ["evidence.onnx.ir", "evidence.mlflow.model"]),
        ("capability.define_feature", "Define governed feature", "semantic.feature_definition", ["evidence.feast.feature_view"]),
        ("capability.retrieve_historical_features", "Retrieve historical feature cut", "semantic.historical_feature_cut", ["evidence.feast.pit"]),
        ("capability.materialize_features", "Materialize online features", "semantic.feature_materialization", ["evidence.feast.online"]),
        ("capability.retrieve_online_features", "Retrieve online feature values", "semantic.online_feature_read", ["evidence.feast.online"]),
        ("capability.deploy_inference", "Deploy model revision", "semantic.inference_deployment", ["evidence.kserve.control"]),
        ("capability.route_inference", "Route model traffic", "semantic.inference_deployment", ["evidence.kserve.canary"]),
        ("capability.execute_inference", "Execute predictive inference", "semantic.inference_request", ["evidence.kserve.protocol"]),
        ("capability.record_inference", "Record inference receipt", "semantic.inference_receipt", ["evidence.openinference"]),
        ("capability.compose_batch_scoring", "Compose batch scoring", "semantic.prediction", ["evidence.kubernetes.jobs", "evidence.feast.architecture"]),
        ("capability.evaluate_model", "Evaluate model", "semantic.evaluation_result", ["evidence.mlflow.evaluation"]),
        ("capability.validate_model", "Validate evidence against policy", "semantic.model_validation", ["evidence.nist.ai_rmf"]),
        ("capability.monitor_model", "Monitor production model", "semantic.model_monitor", ["evidence.evidently"]),
        ("capability.open_model_review", "Open governed model review", "semantic.model_review_case", ["evidence.nist.ai_rmf"]),
        ("capability.publish_model_report", "Publish model evidence report", "semantic.model_edition", ["evidence.model_cards"]),
        ("capability.compile_decision_model", "Compile decision model", "semantic.decision_model", ["evidence.omg.dmn", "evidence.omg.dmn_xsd"]),
        ("capability.execute_decision", "Execute deterministic decision", "semantic.decision_invocation", ["evidence.kie.runtime"]),
        ("capability.record_decision", "Record decision trace", "semantic.decision_invocation", ["evidence.opa.logs"]),
        ("capability.bridge_decision_authority", "Submit decision result for authority", "semantic.decision_result", ["evidence.opa"]),
        ("capability.declare_extension_task", "Declare optional extension task", "semantic.extension_task", ["evidence.mcp"]),
        ("capability.invoke_extension", "Invoke optional model extension", "semantic.extension_invocation", ["evidence.mcp", "evidence.a2a"]),
        ("capability.validate_generated_proposal", "Validate generated proposal", "semantic.generated_proposal", ["evidence.jsonschema", "evidence.mcp.security"]),
    ]
    for ident, name, owner, refs in capability_specs:
        artifacts.append(art(ident, "capability", name, f"Typed capability owned by {owner}.", refs, owner=owner))

    products = ["product.model_lifecycle", "product.feature_platform", "product.online_inference", "product.model_assurance", "product.decision_automation", "product.optional_model_extension"]
    decisions = [
        {"decision_id": "decision.model.lifecycle", "subject_ref": "product.model_lifecycle", "disposition": "strong_product_candidate", "rationale": "Model builders and owners independently adopt experiment, artifact, registry, promotion and retirement workflows while importing compute, data and assurance.", "split_test": split([2] * 10, ["evidence.mlflow.tracking", "evidence.mlflow.registry", "evidence.kubeflow.pipelines", "evidence.nist.ai_rmf"], "predictive model engineering/lifecycle"), "evidence_refs": ["evidence.mlflow.tracking", "evidence.mlflow.registry", "evidence.kubeflow.pipelines", "evidence.nist.ai_rmf"]},
        {"decision_id": "decision.model.feature_platform", "subject_ref": "product.feature_platform", "disposition": "strong_product_candidate", "rationale": "Feature definitions, historical cuts, materialization, online freshness, support and exit form an independently operated promise distinct from vector search and source truth.", "split_test": split([2, 2, 2, 2, 2, 2, 2, 2, 2, 2], ["evidence.feast.feature_view", "evidence.feast.pit", "evidence.feast.online", "evidence.feast.architecture"], "feature platform"), "evidence_refs": ["evidence.feast.feature_view", "evidence.feast.pit", "evidence.feast.online", "evidence.feast.architecture"]},
        {"decision_id": "decision.model.online_inference", "subject_ref": "product.online_inference", "disposition": "strong_product_candidate", "rationale": "Applications independently consume an operated endpoint with revision, rollout, latency, resource and receipt contracts; serving cannot approve the model or authorize downstream actions.", "split_test": split([2] * 10, ["evidence.kserve.protocol", "evidence.kserve.control", "evidence.kserve.canary"], "predictive inference serving"), "evidence_refs": ["evidence.kserve.protocol", "evidence.kserve.control", "evidence.kserve.canary"]},
        {"decision_id": "decision.model.assurance", "subject_ref": "product.model_assurance", "disposition": "strong_product_candidate", "rationale": "Risk reviewers and model owners independently adopt evaluation, monitoring and investigation while promotion authority remains outside the evidence producer.", "split_test": split([2, 2, 2, 2, 1, 2, 2, 1, 2, 2], ["evidence.nist.ai_rmf", "evidence.mlflow.evaluation", "evidence.evidently", "evidence.model_cards"], "predictive model assurance"), "evidence_refs": ["evidence.nist.ai_rmf", "evidence.mlflow.evaluation", "evidence.evidently", "evidence.model_cards"]},
        {"decision_id": "decision.model.decision_automation", "subject_ref": "product.decision_automation", "disposition": "strong_product_candidate", "rationale": "Business analysts and application teams independently author, deploy, execute and migrate versioned decision services with standard interchange and runtime traces.", "split_test": split([2] * 10, ["evidence.omg.dmn", "evidence.omg.dmn_xsd", "evidence.kie.dmn", "evidence.opa"], "decision modeling and execution"), "evidence_refs": ["evidence.omg.dmn", "evidence.omg.dmn_xsd", "evidence.kie.dmn", "evidence.opa"]},
        {"decision_id": "decision.model.optional_extension", "subject_ref": "product.optional_model_extension", "disposition": "presumptive_product", "rationale": "An extension runtime can be separately adopted and operated, but portable semantic equivalence, reliable fallback and independent provider qualification remain unresolved; the core never depends on it.", "split_test": split([2, 2, 2, 2, 1, 2, 1, 1, 1, 1], ["evidence.mcp", "evidence.mcp.security", "evidence.a2a"], "optional model/agent extension runtime"), "evidence_refs": ["evidence.mcp", "evidence.mcp.security", "evidence.a2a"]},
        {"decision_id": "decision.model.vector_feature_split", "subject_ref": "pattern.model_decision_stack", "disposition": "split_vector_search_from_feature_platform", "rationale": "Embedding/vector indexing owns retrieval geometry and ranking, while a feature platform owns entity/time semantics, point-in-time cuts, materialization and training-serving parity.", "evidence_refs": ["evidence.feast.feature_view", "evidence.feast.pit", "evidence.feast.online"]},
        {"decision_id": "decision.model.registry_component", "subject_ref": "component.model_registry", "disposition": "reclassify_as_lifecycle_component", "rationale": "A registry version/alias API lacks the complete experiment, promotion, deployment-evidence, support and exit promise of the lifecycle product.", "evidence_refs": ["evidence.mlflow.registry"]},
        {"decision_id": "decision.model.training_runtime", "subject_ref": "component.training_runtime", "disposition": "reclassify_as_runtime_provider", "rationale": "Distributed training executes a resolved job but cannot own task validity, feature/label semantics, artifact approval or lifecycle state.", "evidence_refs": ["evidence.kubeflow.trainer"]},
        {"decision_id": "decision.model.batch_scoring", "subject_ref": "component.batch_scoring", "disposition": "reclassify_as_dataflow_composition", "rationale": "Batch scoring composes data cuts, feature retrieval, a scoring kernel, job execution and output publication; the schedule mode alone does not create a product.", "evidence_refs": ["evidence.kubernetes.jobs", "evidence.feast.architecture"]},
        {"decision_id": "decision.model.prediction_decision", "subject_ref": "semantic.prediction", "disposition": "retain_split", "rationale": "A score or probability is not a policy decision, authorization, command or observed outcome.", "evidence_refs": ["evidence.kserve.protocol", "evidence.omg.dmn", "evidence.opa"]},
        {"decision_id": "decision.model.evaluation_approval", "subject_ref": "semantic.model_validation", "disposition": "retain_split", "rationale": "Evaluation evidence and a validation verdict do not self-issue deployment approval; lifecycle authority consumes scoped evidence.", "evidence_refs": ["evidence.nist.ai_rmf", "evidence.mlflow.evaluation"]},
        {"decision_id": "decision.model.agent_authority", "subject_ref": "semantic.generated_proposal", "disposition": "reject_self_authorizing_extension", "rationale": "Generated claims, plans and tool calls are untrusted proposals until deterministic schema, semantics, policy, budget, qualification and effect checks pass.", "evidence_refs": ["evidence.mcp.security", "evidence.jsonschema", "evidence.opa"]},
    ]

    ownership = [{"meaning_id": f"meaning.{ident.removeprefix('semantic.')}", "term": name, "owner_ref": ident, "invariant": f"{name} identity and state cannot be inferred from a provider brand, registry alias, endpoint name, generated text or neighboring receipt.", "must_not_be_owned_by": ["neighbor.source_truth", "neighbor.identity_policy"]} for ident, name, _definition, _refs in semantics]

    libraries = [
        lib("library.model.experiment_ledger", "semantic.experiment_run", "capability.track_experiment", ["ExperimentId", "RunId", "RunManifest"], ["start_run", "close_run"], ["immutability", "late_metadata_policy"], ["run_identity_is_attempt_identity", "logged_is_not_reproducible"], ["duplicate_run", "mutable_closed_run"], [], "effect_intents_and_receipts", ["evidence.mlflow.tracking"], "runtime_boundary"),
        lib("library.model.training_contract", "semantic.training_spec", "capability.compile_training", ["TrainingSpec", "DataCutRef", "EstimatorRef"], ["type_training_spec", "close_training_spec"], ["split_policy", "seed_posture", "resource_requirement"], ["target_feature_label_and_split_are_explicit"], ["leakage_unknown", "unbound_runtime"], [], "pure_no_io", ["evidence.kubeflow.pipelines", "evidence.nist.ai_rmf"]),
        lib("library.model.training_attempt", "semantic.training_attempt", "capability.execute_training", ["TrainingAttempt", "TrainingIntent", "TrainingReceipt"], ["issue_training_intent", "ingest_training_receipt"], ["retry_policy", "checkpoint_policy"], ["retry_creates_new_attempt", "timeout_is_not_terminal_fact"], ["provider_unknown", "completion_unknown"], ["library.model.training_contract"], "effect_intents_and_receipts", ["evidence.kubeflow.trainer"], "runtime_boundary"),
        lib("library.model.artifact_contract", "semantic.fitted_artifact", "capability.export_model", ["FittedArtifact", "ArtifactManifest", "ModelDigest"], ["assemble_manifest", "verify_artifact"], ["serialization_profile", "external_data_policy"], ["weights_are_not_model_edition", "digest_covers_declared_parts"], ["missing_component", "unsupported_format"], ["library.model.training_attempt"], "pure_no_io", ["evidence.mlflow.model", "evidence.onnx.ir"]),
        lib("library.model.lifecycle_state", "semantic.model_lifecycle_state", "capability.transition_model", ["ModelEdition", "LifecycleState", "TransitionReceipt"], ["evaluate_transition", "retire"], ["approval_policy", "revocation_policy"], ["alias_is_not_state", "retirement_is_monotone_without_reinstatement_authority"], ["invalid_transition", "evidence_expired"], ["library.model.artifact_contract"], "effect_intents_and_receipts", ["evidence.mlflow.registry", "evidence.nist.ai_rmf"], "control_boundary"),
        lib("library.model.registry_port", "semantic.model_edition", "capability.register_model", ["RegisteredModel", "ModelEdition", "AliasBinding"], ["register_edition", "bind_alias", "export_registry"], ["alias_mutability", "retention_policy"], ["edition_is_immutable", "alias_is_mutable_reference"], ["digest_conflict", "unknown_edition"], ["library.model.artifact_contract"], "effect_intents_and_receipts", ["evidence.mlflow.registry"], "adapter_boundary"),
        lib("library.model.portability", "semantic.fitted_artifact", "capability.export_model", ["ModelCarrier", "OperatorSet", "ConversionReport"], ["validate_carrier", "convert_with_residuals"], ["ir_edition", "opset_policy", "numerical_tolerance"], ["parse_is_not_equivalence", "conversion_loss_is_explicit"], ["unsupported_operator", "equivalence_unproved"], ["library.model.artifact_contract"], "pure_no_io", ["evidence.onnx.ir", "evidence.onnx.versioning", "evidence.pmml"]),
        lib("library.model.feature_contract", "semantic.feature_definition", "capability.define_feature", ["FeatureDefinition", "FeatureService", "AvailabilityTime"], ["validate_definition", "bind_feature_service"], ["time_model", "freshness_policy", "unknown_source_policy"], ["feature_does_not_own_source_fact", "availability_time_precedes_use"], ["unknown_entity", "time_semantics_missing"], [], "pure_no_io", ["evidence.feast.feature_view"]),
        lib("library.model.feature_historical_retrieval", "semantic.historical_feature_cut", "capability.retrieve_historical_features", ["HistoricalFeatureRequest", "HistoricalFeatureCut", "JoinResidual"], ["plan_point_in_time_join", "validate_cut"], ["late_data_policy", "correction_policy", "tie_break"], ["no_future_information", "loss_is_reported"], ["availability_unknown", "ambiguous_order"], ["library.model.feature_contract"], "effect_intents_and_receipts", ["evidence.feast.pit"], "runtime_boundary"),
        lib("library.model.feature_materialization", "semantic.feature_materialization", "capability.materialize_features", ["MaterializationIntent", "MaterializationCursor", "MaterializationReceipt"], ["plan_materialization", "reconcile_materialization"], ["backfill_policy", "ttl_policy", "dedup_policy"], ["materialized_is_not_source_truth", "retry_preserves_occurrence_identity_rules"], ["source_gap", "completion_unknown"], ["library.model.feature_contract"], "effect_intents_and_receipts", ["evidence.feast.online"], "runtime_boundary"),
        lib("library.model.feature_online_retrieval", "semantic.online_feature_read", "capability.retrieve_online_features", ["OnlineFeatureRequest", "OnlineFeatureResult", "FreshnessReceipt"], ["lookup_features", "evaluate_freshness"], ["missing_feature_policy", "deadline_policy"], ["latest_is_not_point_in_time_historical", "freshness_is_observed"], ["stale_value", "partial_result"], ["library.model.feature_contract", "library.model.feature_materialization"], "effect_intents_and_receipts", ["evidence.feast.online"], "runtime_boundary"),
        lib("library.model.inference_contract", "semantic.inference_request", "capability.execute_inference", ["InferenceRequest", "InferenceResponse", "TensorValue"], ["validate_request", "validate_response"], ["protocol_edition", "shape_policy", "deadline_policy"], ["request_version_binding_is_explicit", "response_is_not_decision"], ["shape_mismatch", "model_not_ready"], ["library.model.artifact_contract"], "effect_intents_and_receipts", ["evidence.kserve.protocol"], "runtime_boundary"),
        lib("library.model.inference_routing", "semantic.inference_deployment", "capability.route_inference", ["DeploymentRevision", "TrafficPolicy", "RouteReceipt"], ["validate_route", "shift_traffic", "rollback_route"], ["canary_policy", "sticky_key_policy"], ["traffic_shift_is_not_promotion", "weights_are_versioned"], ["revision_unready", "policy_unsatisfied"], ["library.model.inference_contract", "library.model.lifecycle_state"], "effect_intents_and_receipts", ["evidence.kserve.control", "evidence.kserve.canary"], "runtime_boundary"),
        lib("library.model.inference_receipt", "semantic.inference_receipt", "capability.record_inference", ["InferenceReceipt", "TargetRef", "CompletionDisposition"], ["record_receipt", "correlate_prediction"], ["sampling_policy", "payload_retention"], ["telemetry_is_not_quality", "timeout_is_not_provider_completion"], ["receipt_gap", "correlation_unknown"], ["library.model.inference_contract"], "effect_intents_and_receipts", ["evidence.openinference", "evidence.opentelemetry"], "adapter_boundary"),
        lib("library.model.batch_scoring_composition", "semantic.prediction", "capability.compose_batch_scoring", ["BatchScoringPlan", "InputCut", "PredictionPublication"], ["compose_batch_scoring", "validate_publication"], ["partition_policy", "retry_policy", "output_commit_policy"], ["batch_is_execution_mode_not_model_semantics", "published_cut_is_explicit"], ["input_cut_unclosed", "partial_commit"], ["library.model.feature_historical_retrieval", "library.model.inference_contract"], "pure_effect_intents", ["evidence.kubernetes.jobs", "evidence.feast.architecture"]),
        lib("library.model.assurance_evaluation", "semantic.evaluation_result", "capability.evaluate_model", ["EvaluationPlan", "EvaluationResult", "SliceResult"], ["evaluate", "compare", "diagnose"], ["metric_profile", "slice_policy", "multiplicity_policy"], ["metric_is_scoped", "test_data_does_not_train"], ["label_missing", "sample_insufficient", "metric_undefined"], [], "pure_no_io", ["evidence.mlflow.evaluation", "evidence.nist.ai_rmf"]),
        lib("library.model.assurance_validation", "semantic.model_validation", "capability.validate_model", ["ValidationPolicy", "ValidationVerdict", "Defeater"], ["evaluate_validation", "invalidate_verdict"], ["threshold_policy", "expiry_policy", "review_authority"], ["evidence_producer_cannot_self_authorize", "unknown_fails_closed"], ["evidence_missing", "policy_unknown"], ["library.model.assurance_evaluation"], "pure_no_io", ["evidence.nist.ai_rmf"]),
        lib("library.model.assurance_monitoring", "semantic.model_monitor", "capability.monitor_model", ["MonitorPlan", "ObservationWindow", "DriftFinding"], ["evaluate_window", "detect_change"], ["baseline_policy", "label_delay", "missingness_policy"], ["drift_is_not_degradation", "correlation_is_not_cause"], ["baseline_invalid", "labels_immature"], ["library.model.assurance_evaluation", "library.model.inference_receipt"], "effect_intents_and_receipts", ["evidence.evidently"], "runtime_boundary"),
        lib("library.model.review_case", "semantic.model_review_case", "capability.open_model_review", ["ReviewCase", "Finding", "ResponseDecision"], ["open_case", "record_response", "close_case"], ["severity_policy", "waiver_policy"], ["alert_is_not_incident", "closure_requires_evidence"], ["owner_unknown", "closure_evidence_missing"], ["library.model.assurance_monitoring"], "effect_intents_and_receipts", ["evidence.nist.ai_rmf"], "case_boundary"),
        lib("library.model.evidence_report", "semantic.model_edition", "capability.publish_model_report", ["ModelReport", "IntendedUse", "Limitation"], ["assemble_report", "verify_evidence_links"], ["slice_disclosure", "redaction_policy"], ["report_is_not_qualification", "claims_link_to_evidence"], ["evidence_unbound", "audience_unknown"], ["library.model.assurance_validation"], "pure_effect_intents", ["evidence.model_cards", "evidence.w3c.prov"]),
        lib("library.model.decision_contract", "semantic.decision_model", "capability.compile_decision_model", ["DecisionModel", "DecisionRequirementGraph", "DecisionService"], ["parse_model", "type_model", "compile_model"], ["dmn_edition", "feel_profile", "extension_policy"], ["schema_valid_is_not_semantically_valid", "dependencies_are_closed"], ["type_error", "unsupported_profile"], [], "pure_no_io", ["evidence.omg.dmn", "evidence.omg.dmn_xsd"]),
        lib("library.model.decision_table", "semantic.decision_table", "capability.compile_decision_model", ["DecisionTable", "Rule", "HitPolicy"], ["analyze_gaps", "analyze_overlaps", "evaluate_table"], ["hit_policy", "priority_order", "null_policy"], ["rule_order_is_explicit", "overlap_behavior_is_declared"], ["gap_detected", "ambiguous_overlap"], ["library.model.decision_contract"], "pure_no_io", ["evidence.kie.dmn", "evidence.kie.runtime"]),
        lib("library.model.decision_runtime", "semantic.decision_invocation", "capability.execute_decision", ["DecisionInvocation", "DecisionResult", "DecisionTrace"], ["invoke_decision", "record_trace"], ["strict_conformance", "runtime_typecheck"], ["same_model_and_input_is_deterministic", "result_is_not_effect"], ["input_invalid", "decision_undefined"], ["library.model.decision_contract", "library.model.decision_table"], "effect_intents_and_receipts", ["evidence.kie.runtime", "evidence.opa.logs"], "runtime_boundary"),
        lib("library.model.decision_ledger", "semantic.decision_invocation", "capability.record_decision", ["DecisionLogEntry", "DecisionId", "BundleRef"], ["record_decision", "redact_log"], ["retention_policy", "sensitive_field_policy"], ["log_is_not_effect_receipt", "input_disclosure_is_minimized"], ["decision_id_missing", "redaction_unknown"], ["library.model.decision_runtime"], "effect_intents_and_receipts", ["evidence.opa.logs"], "adapter_boundary"),
        lib("library.model.decision_authority_bridge", "semantic.decision_result", "capability.bridge_decision_authority", ["DecisionResult", "ActionProposal", "AuthorityVerdict"], ["submit_proposal", "ingest_authority_verdict"], ["authority_context", "purpose_policy"], ["decision_is_not_authorization", "authorization_is_not_execution"], ["principal_unknown", "purpose_refused"], ["library.model.decision_runtime"], "pure_effect_intents", ["evidence.opa"]),
        lib("library.model.extension_contract", "semantic.extension_task", "capability.declare_extension_task", ["ExtensionTask", "FallbackPlan", "ToolRequirement"], ["type_extension_task", "remove_extension"], ["use_site_posture", "fallback_policy", "budget_policy"], ["extension_is_optional_or_intent_required", "removal_preserves_core"], ["fallback_missing", "authority_ambiguous"], [], "pure_no_io", ["evidence.mcp", "evidence.a2a"]),
        lib("library.model.extension_invocation", "semantic.extension_invocation", "capability.invoke_extension", ["ExtensionInvocation", "ProviderBinding", "InvocationReceipt"], ["invoke", "cancel", "record_completion"], ["model_edition", "sampling_policy", "retry_policy"], ["retry_has_new_identity", "seed_is_not_replay_proof"], ["provider_unqualified", "completion_unknown"], ["library.model.extension_contract"], "effect_intents_and_receipts", ["evidence.mcp", "evidence.a2a"], "runtime_boundary"),
        lib("library.model.generated_proposal", "semantic.generated_proposal", "capability.validate_generated_proposal", ["GeneratedClaim", "GeneratedPlan", "ToolCallProposal"], ["parse_proposal", "validate_proposal"], ["schema_profile", "taint_policy", "evidence_policy"], ["well_formed_is_not_true", "proposal_cannot_self_validate"], ["schema_invalid", "evidence_missing", "instruction_untrusted"], ["library.model.extension_contract"], "pure_no_io", ["evidence.jsonschema", "evidence.mcp.security"]),
    ]

    consumer_for = {
        "experiment_ledger": "product.model_lifecycle", "training_contract": "product.model_lifecycle", "training_attempt": "product.model_lifecycle", "artifact_contract": "product.model_lifecycle", "lifecycle_state": "product.model_lifecycle", "registry_port": "product.model_lifecycle", "portability": "product.model_lifecycle",
        "feature_contract": "product.feature_platform", "feature_historical_retrieval": "product.feature_platform", "feature_materialization": "product.feature_platform", "feature_online_retrieval": "product.feature_platform",
        "inference_contract": "product.online_inference", "inference_routing": "product.online_inference", "inference_receipt": "product.online_inference", "batch_scoring_composition": "component.batch_scoring",
        "assurance_evaluation": "product.model_assurance", "assurance_validation": "product.model_assurance", "assurance_monitoring": "product.model_assurance", "review_case": "product.model_assurance", "evidence_report": "product.model_assurance",
        "decision_contract": "product.decision_automation", "decision_table": "product.decision_automation", "decision_runtime": "product.decision_automation", "decision_ledger": "product.decision_automation", "decision_authority_bridge": "product.decision_automation",
        "extension_contract": "product.optional_model_extension", "extension_invocation": "product.optional_model_extension", "generated_proposal": "product.optional_model_extension",
    }
    requirements = []
    for row in libraries:
        tail = row["library_id"].split(".")[-1]
        requirements.append({"requirement_id": f"requirement.model.{tail}", "consumer_ref": consumer_for[tail], "capability_ref": row["provides"][0], "binding_phase": "runtime" if row["effect_boundary"] == "effect_intents_and_receipts" else "compile_time", "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{tail}_implementation"})

    offers = [
        {"offer_id": "offer.mlflow.lifecycle", "provider_ref": "implementation.mlflow", "capability_refs": ["capability.track_experiment", "capability.register_model", "capability.evaluate_model"], "qualified_implementation_count": 0, "portable": False, "status": "observed_unqualified", "evidence_refs": ["evidence.mlflow.tracking", "evidence.mlflow.registry", "evidence.mlflow.evaluation"]},
        {"offer_id": "offer.kubeflow.training", "provider_ref": "implementation.kubeflow", "capability_refs": ["capability.compile_training", "capability.execute_training"], "qualified_implementation_count": 0, "portable": False, "status": "observed_unqualified", "evidence_refs": ["evidence.kubeflow.pipelines", "evidence.kubeflow.trainer"]},
        {"offer_id": "offer.feast.feature", "provider_ref": "implementation.feast", "capability_refs": ["capability.define_feature", "capability.retrieve_historical_features", "capability.materialize_features", "capability.retrieve_online_features"], "qualified_implementation_count": 0, "portable": False, "status": "observed_unqualified", "evidence_refs": ["evidence.feast.feature_view", "evidence.feast.pit", "evidence.feast.online"]},
        {"offer_id": "offer.kserve.inference", "provider_ref": "implementation.kserve", "capability_refs": ["capability.deploy_inference", "capability.route_inference", "capability.execute_inference", "capability.record_inference"], "qualified_implementation_count": 0, "portable": False, "status": "observed_unqualified", "evidence_refs": ["evidence.kserve.protocol", "evidence.kserve.control", "evidence.kserve.canary"]},
        {"offer_id": "offer.evidently.assurance", "provider_ref": "implementation.evidently", "capability_refs": ["capability.evaluate_model", "capability.monitor_model"], "qualified_implementation_count": 0, "portable": False, "status": "observed_unqualified", "evidence_refs": ["evidence.evidently"]},
        {"offer_id": "offer.drools.decision", "provider_ref": "implementation.drools", "capability_refs": ["capability.compile_decision_model", "capability.execute_decision", "capability.record_decision"], "qualified_implementation_count": 0, "portable": False, "status": "observed_unqualified", "evidence_refs": ["evidence.kie.dmn", "evidence.kie.runtime"]},
        {"offer_id": "offer.extension.adapter", "provider_ref": "implementation.model_extension_adapter", "capability_refs": ["capability.invoke_extension"], "qualified_implementation_count": 0, "portable": False, "status": "declared_unqualified", "evidence_refs": ["evidence.mcp", "evidence.a2a"]},
    ]

    relations = [{"relation_id": f"relation.suite.packages.{p.split('.')[-1]}", "from_ref": "suite.model_decision_products", "predicate": "packages", "to_ref": p, "binding_phase": "authoring"} for p in products] + [
        {"relation_id": "relation.pattern.realizes.suite", "from_ref": "pattern.model_decision_stack", "predicate": "realizes", "to_ref": "suite.model_decision_products", "binding_phase": "authoring"},
        {"relation_id": "relation.lifecycle.requires.runtime", "from_ref": "product.model_lifecycle", "predicate": "requires", "to_ref": "neighbor.runtime_resource", "binding_phase": "runtime"},
        {"relation_id": "relation.lifecycle.requires.assurance", "from_ref": "product.model_lifecycle", "predicate": "requires", "to_ref": "product.model_assurance", "binding_phase": "qualification_time"},
        {"relation_id": "relation.feature.requires.source", "from_ref": "product.feature_platform", "predicate": "requires", "to_ref": "neighbor.source_truth", "binding_phase": "runtime"},
        {"relation_id": "relation.inference.requires.lifecycle", "from_ref": "product.online_inference", "predicate": "requires", "to_ref": "product.model_lifecycle", "binding_phase": "deployment_time"},
        {"relation_id": "relation.inference.requires.features", "from_ref": "product.online_inference", "predicate": "requires", "to_ref": "product.feature_platform", "binding_phase": "runtime"},
        {"relation_id": "relation.batch.requires.dataflow", "from_ref": "component.batch_scoring", "predicate": "requires", "to_ref": "neighbor.dataflow", "binding_phase": "runtime"},
        {"relation_id": "relation.vector.belongs.search", "from_ref": "component.vector_index", "predicate": "specializes", "to_ref": "neighbor.search_index", "binding_phase": "authoring"},
        {"relation_id": "relation.decision.requires.authority", "from_ref": "product.decision_automation", "predicate": "requires", "to_ref": "neighbor.identity_policy", "binding_phase": "runtime"},
        {"relation_id": "relation.extension.requires.authority", "from_ref": "product.optional_model_extension", "predicate": "requires", "to_ref": "neighbor.identity_policy", "binding_phase": "runtime"},
        {"relation_id": "relation.extension.requires.effects", "from_ref": "product.optional_model_extension", "predicate": "requires", "to_ref": "neighbor.effect_runtime", "binding_phase": "runtime"},
    ]

    crosswalks = [
        {"legacy_ref": "candidate.product.model_lifecycle", "canonical_refs": ["product.model_lifecycle"], "disposition": "replace_refined_boundary"},
        {"legacy_ref": "candidate.product.online_inference", "canonical_refs": ["product.online_inference"], "disposition": "replace_exact"},
        {"legacy_ref": "candidate.product.vector_feature_serving", "canonical_refs": ["product.feature_platform", "component.vector_index", "neighbor.search_index"], "disposition": "split"},
        {"legacy_ref": "candidate.product.feature_platform", "canonical_refs": ["product.feature_platform"], "disposition": "add_missing_product"},
        {"legacy_ref": "candidate.product.model_assurance", "canonical_refs": ["product.model_assurance"], "disposition": "add_missing_product"},
        {"legacy_ref": "candidate.product.decision_automation", "canonical_refs": ["product.decision_automation"], "disposition": "add_missing_product"},
        {"legacy_ref": "candidate.product.optional_model_extension", "canonical_refs": ["product.optional_model_extension"], "disposition": "add_optional_product"},
        {"legacy_ref": "candidate.product.batch_inference", "canonical_refs": ["component.batch_scoring", "neighbor.dataflow"], "disposition": "reclassify_composition"},
        {"legacy_ref": "candidate.product.model_registry", "canonical_refs": ["component.model_registry", "product.model_lifecycle"], "disposition": "reclassify_component"},
        {"legacy_ref": "candidate.product.training_platform", "canonical_refs": ["component.training_runtime", "product.model_lifecycle", "neighbor.runtime_resource"], "disposition": "split_product_from_provider"},
    ]

    negatives = [
        ("negative.model_family_artifact", "Model family is not fitted artifact or model edition.", "retain_distinct_identity"),
        ("negative.weights_model", "Weights alone are not a complete model artifact.", "require_manifest"),
        ("negative.run_reproducible", "Tracked run is not automatically reproducible.", "require_closed_inputs_environment_and_receipts"),
        ("negative.alias_approval", "Registry alias or tag is not approval.", "require_authority_transition"),
        ("negative.approval_deployment", "Approved model is not observed deployment.", "require_deployment_receipt"),
        ("negative.ready_valid", "Ready endpoint is not validated model behavior.", "require_assurance_evidence"),
        ("negative.protocol_equivalence", "Inference protocol compatibility is not numerical or semantic equivalence.", "require_differential_oracles"),
        ("negative.feature_source_truth", "Feature platform does not own source business facts.", "retain_source_authority"),
        ("negative.feature_vector", "Feature value is not embedding/vector-index entry.", "split_feature_and_search"),
        ("negative.latest_historical", "Latest online value is not point-in-time historical value.", "retain_time_contract"),
        ("negative.event_available", "Event time is not availability or recording time.", "require_time_axes"),
        ("negative.materialized_correct", "Materialized value is not automatically correct or fresh.", "require_receipt_and_freshness"),
        ("negative.batch_product", "Batch execution mode alone is not a prediction product.", "compose_dataflow"),
        ("negative.metric_verdict", "Evaluation metric is not validation verdict.", "apply_validation_policy"),
        ("negative.validation_approval", "Validation verdict is not deployment approval.", "invoke_lifecycle_authority"),
        ("negative.drift_degradation", "Drift is not automatic degradation.", "open_scoped_review"),
        ("negative.drift_cause", "Drift finding is not root cause.", "retain_hypothesis_status"),
        ("negative.telemetry_quality", "Inference telemetry is not model quality.", "join_outcomes_and_evaluate"),
        ("negative.report_truth", "Model card is not self-validating truth.", "verify_claim_evidence"),
        ("negative.prediction_decision", "Prediction is not business decision.", "execute_governed_decision_model"),
        ("negative.decision_authority", "Decision result is not authorization.", "apply_authority_gate"),
        ("negative.authorization_effect", "Authorization is not completed effect.", "require_effect_receipt"),
        ("negative.dmn_schema", "DMN XML validity is not model conformance.", "compile_and_test_semantics"),
        ("negative.hit_default", "Decision-table overlap cannot inherit an undeclared hit policy.", "refuse_ambiguous_model"),
        ("negative.agent_decision", "Generated plan is not decision or action.", "validate_then_authorize"),
        ("negative.tool_visibility", "Visible tool is not authorized tool call.", "check_per_effect_authority"),
        ("negative.agent_core", "Removing the extension cannot break deterministic core compilation.", "enforce_removal_test"),
        ("negative.ai_prefix", "A model-capable product is not renamed or duplicated as an AI product.", "classify_automation_modality"),
        ("negative.provider_docs", "Provider documentation is not qualification evidence.", "execute_conformance_profile"),
        ("negative.single_portable", "One implementation cannot establish portable semantics.", "require_two_independent_qualified_implementations"),
    ]
    negative_tests = [{"test_id": ident, "prohibited_claim": claim, "expected_result": expected} for ident, claim, expected in negatives]

    exact_maps = {
        "library.model.experiment_ledger": ["library.predictive.artifact_manifest"],
        "library.model.training_contract": ["library.predictive.target_contracts", "library.predictive.feature_contracts", "library.predictive.label_contracts", "library.predictive.split_planner", "library.predictive.objective_functions"],
        "library.model.training_attempt": ["library.predictive.optimizers", "library.predictive.artifact_manifest"],
        "library.model.artifact_contract": ["library.predictive.artifact_manifest", "library.predictive.model_serialization"],
        "library.model.lifecycle_state": ["library.predictive.model_lifecycle"],
        "library.model.registry_port": ["library.predictive.model_registry_port"],
        "library.model.portability": ["library.predictive.model_serialization", "library.predictive.provider_adapter_onnx"],
        "library.model.feature_contract": ["library.predictive.feature_contracts", "library.predictive.leakage_guard"],
        "library.model.feature_historical_retrieval": ["library.feature.historical_cut.planner", "library.feature.historical_cut.evaluator"],
        "library.model.feature_materialization": ["library.feature.materialization.planner", "library.feature.materialization.protocol"],
        "library.model.feature_online_retrieval": ["library.feature.online_read.protocol"],
        "library.model.inference_contract": ["library.predictive.online_scoring", "library.predictive.model_serialization"],
        "library.model.inference_routing": ["library.inference.revision_router", "library.inference.rollout_protocol"],
        "library.model.inference_receipt": ["library.predictive.online_scoring", "library.lpe.runtime-receipt-core"],
        "library.model.batch_scoring_composition": ["library.predictive.batch_scoring"],
        "library.model.assurance_evaluation": ["library.predictive.metrics", "library.predictive.calibration", "library.predictive.fairness_evaluation", "library.predictive.robustness_evaluation"],
        "library.model.assurance_validation": ["library.predictive.metrics", "library.lpe.evidence-evaluation"],
        "library.model.assurance_monitoring": ["library.predictive.monitoring", "library.predictive.drift_response"],
        "library.model.review_case": ["library.predictive.drift_response", "library.cbv.analytical_case_reducer", "library.cbv.decision_handoff_algebra"],
        "library.model.evidence_report": ["library.predictive.artifact_manifest", "library.lpe.evidence-bundle"],
        "library.model.decision_contract": ["library.csp.decision.decision-contract", "library.csp.decision.decision-conformance"],
        "library.model.decision_table": ["library.csp.decision.decision-table", "library.csp.decision.decision-conformance"],
        "library.model.decision_runtime": ["library.csp.decision.decision-contract", "library.csp.decision.decision-ledger", "library.csp.decision.decision-table"],
        "library.model.decision_ledger": ["library.csp.decision.decision-ledger"],
        "library.model.decision_authority_bridge": ["library.csp.decision.action-proposal", "library.csp.decision.action-authorizer", "library.csp.decision.effect-port"],
        "library.model.extension_contract": ["library.mae.contract_core", "library.mae.task_intent", "library.mae.schema_bridge"],
        "library.model.extension_invocation": ["library.mae.model_client_spi", "library.mae.retry_cancel_runtime"],
        "library.model.generated_proposal": ["library.mae.proposal_types", "library.mae.claim_validation_bridge", "library.mae.structured_output_oracle"],
    }
    gaps = {}
    binding_maps = []
    binding_gaps = []
    for row in libraries:
        local = row["library_id"]
        refs = exact_maps.get(local, [])
        gap = gaps.get(local)
        binding_maps.append({"binding_map_id": f"binding.model.{local.split('.')[-1]}", "abstract_library_ref": local, "concrete_library_refs": refs, "compiler_disposition": "structurally_projected_unqualified" if refs else "blocked_typed_gap", "gap_ref": gap[0] if gap else None, "portable_offer": False})
        if gap:
            binding_gaps.append({"gap_id": gap[0], "abstract_library_ref": local, "reason": gap[1], "resolution": "Adjudicate exact types, laws, failure states, fixtures and two independent implementations before binding."})

    return {
        "contract_id": "contract.product_adjudication.model_decision_serving.v0_1_0",
        "edition": 1,
        "status": "evidence_backed_adjudicated_candidate_not_ratified",
        "scope": "Predictive model engineering/lifecycle, feature definition and serving, predictive inference, model assurance, deterministic decision automation and optional model/agent extension product boundaries.",
        "negative_scope": "Does not create an ambient AI layer, treat prediction as decision, grant generated output authority, qualify providers, own source facts, or treat batch mode, registry, vector index or training runtime as products by implementation name.",
        "non_collapse_laws": [
            "predictive task != model family != estimator != training attempt != fitted artifact != model edition != deployment",
            "registry alias != lifecycle state != validation verdict != approval != deployment status",
            "feature definition != source fact != historical feature cut != materialization != online read",
            "event time != availability time != recording time != inference time != label maturity time",
            "vector index and embedding retrieval != feature definition and point-in-time serving",
            "inference request != prediction != calibrated risk != decision != authorization != effect != outcome",
            "evaluation metric != validation verdict != approval; drift != degradation != cause",
            "decision model != decision invocation != decision result != authority verdict != effect receipt",
            "batch scoring is a composition mode, not a product boundary by itself",
            "generated claim, plan or tool call is an untrusted proposal and cannot validate or authorize itself",
            "optional model/agent extension may be removed without changing deterministic core semantics",
            "suite packaging and provider brands never acquire semantic ownership",
        ],
        "sources": sources, "artifact_kinds": kinds, "artifacts": artifacts, "boundary_decisions": decisions,
        "ownership": ownership, "libraries": libraries, "requirements": requirements, "offers": offers,
        "relations": relations, "crosswalks": crosswalks, "negative_tests": negative_tests,
        "binding_maps": binding_maps, "binding_gaps": binding_gaps,
    }


def source_bytes() -> bytes:
    from product_enrichment import enrich

    return (json.dumps(enrich(source()), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


if __name__ == "__main__":
    SOURCE.write_bytes(source_bytes())
    print(f"WROTE {SOURCE}")
