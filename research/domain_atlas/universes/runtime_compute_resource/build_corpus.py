#!/usr/bin/env python3
"""Build the provider-neutral runtime, compute and resource-control research corpus.

This file is the reviewable source for the generated JSON/JSONL registries.  Records are
hypotheses unless their status says otherwise; references prove only the scoped claim stated
in the evidence record.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EDITION = "0.1.0"


def write_json(path: str, value: object) -> None:
    (ROOT / path).write_text(json.dumps(value, indent=2, sort_keys=False) + "\n")


def write_jsonl(path: str, values: list[dict]) -> None:
    (ROOT / path).write_text("".join(json.dumps(v, sort_keys=False) + "\n" for v in values))


def ctx(
    suffix: str,
    name: str,
    vision: str,
    owns: list[str],
    excludes: list[str],
    neighbors: list[str],
    invariants: list[str],
    evidence: list[str],
    classification: str = "supporting",
) -> dict:
    return {
        "record_kind": "bounded_context",
        "context_id": f"context.runtime-resource.{suffix}",
        "edition": EDITION,
        "status": "research_candidate",
        "name": name,
        "domain_vision": vision,
        "subdomain_classification": classification,
        "owns": owns,
        "explicitly_excludes": excludes,
        "neighbor_context_refs": neighbors,
        "core_invariants": invariants,
        "published_language": f"contract.runtime-resource.{suffix}.v1",
        "evidence_refs": evidence,
        "gaps": ["Aggregate ownership and two-implementation conformance remain to be adjudicated."],
    }


CONTEXTS = [
    ctx("execution-contract", "Execution contract", "What executable work may a runtime accept without inventing business or query meaning?", ["work-unit identity", "entry point", "declared inputs and outputs", "effect and side-effect envelope", "execution guarantee requirement"], ["business intent", "query semantics", "algorithm meaning", "provider placement"], ["context.runtime-resource.attempt-control", "context.runtime-resource.executable-artifact", "context.runtime-resource.resource-demand"], ["A work unit references an immutable executable artifact and exact entry point.", "Unknown effect or execution guarantee is a compiler gap."], ["evidence.posix-2024", "evidence.wasm-core"], "core"),
    ctx("executable-artifact", "Executable artifact and kernel dispatch", "Which immutable artifact, ABI, target and compute-kernel entry point can be loaded and invoked?", ["artifact digest", "ABI", "target triple", "kernel entry point", "runtime feature requirements", "load and dispatch receipt"], ["source-language algorithm", "query plan", "container image distribution product"], ["context.runtime-resource.execution-contract", "context.runtime-resource.target-profile", "context.runtime-resource.device-runtime"], ["Artifact identity includes bytes digest, ABI and target.", "A compute kernel is never confused with an operating-system kernel."], ["evidence.oci-image", "evidence.wasm-core", "evidence.sycl-2020", "evidence.opencl-3"], "core"),
    ctx("process-runtime", "Process runtime", "How is an isolated process created, signalled, waited for and terminated?", ["process identity and lifetime", "spawn/exec/wait", "signal delivery", "exit status", "process resource attachment"], ["thread scheduling policy", "container orchestration", "application workflow"], ["context.runtime-resource.thread-runtime", "context.runtime-resource.isolation-runtime", "context.runtime-resource.attempt-control"], ["A reused numeric PID is not the same process identity.", "Exit status and termination cause are retained separately."], ["evidence.posix-2024", "evidence.posix-spawn"]),
    ctx("thread-runtime", "Thread runtime", "How are address-space-sharing execution agents created, joined, synchronized and scheduled?", ["thread identity", "joinability", "synchronization", "contention scope", "thread-local state"], ["process lifetime", "async task semantics", "distributed worker"], ["context.runtime-resource.process-runtime", "context.runtime-resource.async-runtime", "context.runtime-resource.scheduling-policy"], ["Thread identity is scoped to its process lifetime.", "Join, detach and cancellation semantics are explicit."], ["evidence.posix-2024", "evidence.rust-thread"]),
    ctx("async-runtime", "Asynchronous task runtime", "How are cooperatively scheduled futures/tasks polled, awakened, cancelled and drained?", ["async task identity", "poll/wake contract", "executor membership", "cooperative cancellation", "structured task scope"], ["OS thread policy", "durable workflow semantics", "business timeout policy"], ["context.runtime-resource.thread-runtime", "context.runtime-resource.cancellation-deadline", "context.runtime-resource.executor-worker"], ["Dropping a future is not assumed to cancel its external effects.", "Blocking operations require an explicit blocking boundary."], ["evidence.rust-future", "evidence.tokio-task", "evidence.reactive-streams"]),
    ctx("actor-runtime", "Actor runtime", "How does an identity-bearing isolated actor serialize messages, supervise failures and recover state?", ["actor identity", "mailbox", "message ordering scope", "supervision", "restart identity"], ["business aggregate", "message broker", "durable workflow"], ["context.runtime-resource.executor-worker", "context.runtime-resource.attempt-control", "context.runtime-resource.backpressure"], ["Actor restart identity and state-recovery policy are explicit.", "Mailbox ordering is scoped, not called globally ordered."], ["evidence.erlang-supervision", "evidence.ray-actors"]),
    ctx("executor-worker", "Executor and worker pool", "How is runnable work assigned to reusable workers and execution slots?", ["worker identity", "executor identity", "slot capacity", "work queue", "worker drain", "worker health"], ["cluster admission", "provider machine lifecycle", "algorithm semantics"], ["context.runtime-resource.async-runtime", "context.runtime-resource.attempt-control", "context.runtime-resource.placement"], ["A worker is an execution occurrence, not a unit of requested CPU.", "Draining forbids new assignments while preserving declared completion policy."], ["evidence.dask-worker-state", "evidence.ray-actors", "evidence.spark-scheduling"]),
    ctx("device-runtime", "Heterogeneous device runtime", "How are CPU, GPU and accelerator devices discovered, selected, addressed and commanded?", ["device identity", "platform/context", "command queue", "memory accessibility", "kernel dispatch", "event synchronization"], ["kernel algorithm semantics", "device procurement", "cluster quota"], ["context.runtime-resource.executable-artifact", "context.runtime-resource.resource-topology", "context.runtime-resource.resource-reservation"], ["Device discovery and provider selection are separate.", "Memory accessibility and synchronization are explicit per context."], ["evidence.sycl-2020", "evidence.opencl-3", "evidence.cuda-guide", "evidence.openmp-6"], "core"),
    ctx("distributed-runtime", "Distributed task and collective runtime", "How are work and data coordinated across failure-prone execution members?", ["distributed task identity", "rank/member identity", "collective scope", "data dependency availability", "member failure outcome"], ["business saga", "query semantics", "network transport implementation"], ["context.runtime-resource.executor-worker", "context.runtime-resource.failure-domain", "context.runtime-resource.checkpoint-recovery"], ["Membership edition is part of collective identity.", "Remote failure is not represented as a local exception alone."], ["evidence.mpi-4.1", "evidence.dask-worker-state", "evidence.ray-placement"]),
    ctx("attempt-control", "Job, work-unit and attempt control", "What is the authoritative lifecycle of declared work, retries and individual attempts?", ["job identity", "work-unit identity", "attempt identity", "retry lineage", "outcome precedence", "attempt receipt"], ["workflow business state", "scheduler policy", "executable semantics"], ["context.runtime-resource.execution-contract", "context.runtime-resource.cancellation-deadline", "context.runtime-resource.checkpoint-recovery"], ["Retry creates a new AttemptId and never rewrites the previous attempt.", "Success, failure, cancellation, timeout and preemption remain distinct outcomes."], ["evidence.k8s-job", "evidence.slurm-job-state", "evidence.jobset"] , "core"),
    ctx("cancellation-deadline", "Cancellation, deadlines and timeouts", "How can execution be requested to stop, and what is known when its deadline or timeout expires?", ["deadline", "timeout scope", "cancellation request", "acknowledgement", "drain deadline", "forced termination"], ["business expiry", "SLA policy", "transaction rollback"], ["context.runtime-resource.attempt-control", "context.runtime-resource.async-runtime", "context.runtime-resource.backpressure"], ["Cancellation request is not completion.", "Deadline, elapsed timeout and observed wall-clock time are separate."], ["evidence.grpc-deadline", "evidence.tokio-cancellation", "evidence.temporal-timeouts"], "core"),
    ctx("backpressure", "Flow control and backpressure", "How is finite downstream demand signalled and overload propagated without unbounded queues?", ["demand credit", "buffer bound", "push/pull mode", "overflow policy", "load shedding", "backpressure receipt"], ["business priority", "network congestion-control protocol", "autoscaling decision"], ["context.runtime-resource.executor-worker", "context.runtime-resource.cancellation-deadline", "context.runtime-resource.autoscaling"], ["Unbounded buffering is refused unless explicitly waived.", "Dropped, rejected, delayed and cancelled work are distinct."], ["evidence.reactive-streams", "evidence.grpc-flow", "evidence.dask-worker-state"], "core"),
    ctx("checkpoint-recovery", "Checkpoint, resume and replay", "What execution state can be durably captured and safely resumed after interruption?", ["checkpoint identity", "compatibility", "resume point", "checkpoint lineage", "restore outcome", "replay determinism claim"], ["database backup", "business event sourcing", "artifact storage implementation"], ["context.runtime-resource.attempt-control", "context.runtime-resource.distributed-runtime", "context.runtime-resource.failure-domain"], ["A checkpoint is bound to artifact, state schema and runtime compatibility.", "Restore creates a new attempt even if logical work identity is preserved."], ["evidence.criu", "evidence.temporal-docs", "evidence.mpi-4.1"]),
    ctx("resource-topology", "Resource identity, capability and topology", "What resources exist, what can they do, and how are locality and failure relations represented?", ["resource identity", "capability facts", "topology graph", "locality", "sharing domain", "failure domain"], ["workload demand", "quota", "provider SKU", "allocation"], ["context.runtime-resource.resource-demand", "context.runtime-resource.provider-occurrence", "context.runtime-resource.failure-domain"], ["Resource identity is not inferred from a mutable name.", "Topology edges carry relation kind, validity and evidence."], ["evidence.hwloc", "evidence.redfish", "evidence.cxl-3.2", "evidence.sycl-2020"], "core"),
    ctx("resource-demand", "Workload resource demand", "What finite resource quantities, qualities and topology relations does work require?", ["minimum demand", "target demand", "maximum demand", "elastic range", "hard and soft constraints", "usage horizon"], ["available supply", "provider offer", "quota", "observed usage"], ["context.runtime-resource.execution-contract", "context.runtime-resource.resource-offer", "context.runtime-resource.admission-control"], ["Every blocking resource dimension is bounded or explicitly rejected as unbounded.", "Minimum, target and maximum are not interchangeable."], ["evidence.k8s-resources", "evidence.slurm-reservation", "evidence.ray-placement"], "core"),
    ctx("resource-offer", "Allocatable resource offer", "What time-bounded capacity and guarantees may an allocator truthfully offer?", ["offer identity", "capacity vector", "quality attributes", "validity window", "interruptibility", "price/energy rates", "evidence"], ["provider marketing SKU", "workload demand", "reservation", "actual allocation"], ["context.runtime-resource.resource-topology", "context.runtime-resource.resource-demand", "context.runtime-resource.provider-occurrence"], ["Offer validity and evidence freshness are explicit.", "An offer is not an allocation and makes no usage claim."], ["evidence.nist-cloud", "evidence.focus-1.2", "evidence.k8s-dra"], "core"),
    ctx("resource-pool", "Resource pool and inventory", "Which offers form a pool, and what capacity is free, held, allocated, unavailable or stale?", ["pool identity", "membership", "capacity ledger", "availability", "fragmentation", "inventory freshness"], ["tenant quota", "provider catalog", "individual allocation"], ["context.runtime-resource.resource-offer", "context.runtime-resource.resource-reservation", "context.runtime-resource.capacity-planning"], ["Pool totals reconcile with held, allocated, unavailable and free capacity within measurement error.", "Stale inventory is never silently treated as free."], ["evidence.k8s-dra", "evidence.slurm-reservation", "evidence.redfish"]),
    ctx("quota-budget", "Quota, finite budget and precharge", "What authority limits resource admission and spend before effects occur?", ["quota identity", "scope", "limit", "usage ledger", "budget", "precharge", "release/refund"], ["physical capacity", "billing invoice", "scheduler priority"], ["context.runtime-resource.admission-control", "context.runtime-resource.accounting-cost", "context.runtime-resource.resource-pool"], ["Quota availability does not prove physical feasibility.", "Effectful work consuming a hard budget is admitted only after atomic precharge or equivalent reservation."], ["evidence.k8s-quota", "evidence.kueue-clusterqueue", "evidence.focus-1.2"], "core"),
    ctx("admission-control", "Workload admission", "May this work enter contention given policy, authority, feasibility and finite budgets?", ["admission request", "admission decision", "reason catalog", "admission hold", "admission receipt"], ["exact placement", "runtime start", "business authorization"], ["context.runtime-resource.resource-demand", "context.runtime-resource.quota-budget", "context.runtime-resource.placement"], ["Admitted does not mean scheduled or running.", "Every refusal has a stable typed reason and evidence."], ["evidence.kueue-concepts", "evidence.k8s-scheduling-readiness", "evidence.slurm-qos"], "core"),
    ctx("resource-reservation", "Reservation and allocation", "How is capacity held, committed, assigned and released without double allocation?", ["reservation", "allocation", "hold expiry", "commit", "release", "capacity ledger mutation"], ["lease liveness", "actual usage", "provider provisioning"], ["context.runtime-resource.resource-pool", "context.runtime-resource.lease-fencing", "context.runtime-resource.placement"], ["Capacity is deducted exactly once at reservation commit.", "Expired holds cannot be committed without a new reservation."], ["evidence.slurm-reservation", "evidence.ray-placement", "evidence.k8s-dra"], "core"),
    ctx("lease-fencing", "Leases, heartbeats and fencing", "How is temporary authority kept alive and stale holders prevented from acting?", ["lease identity", "TTL", "renewal", "heartbeat", "fencing token", "expiry", "revocation"], ["business delegation", "resource capacity", "distributed transaction"], ["context.runtime-resource.resource-reservation", "context.runtime-resource.control-reconciliation", "context.runtime-resource.executor-worker"], ["A stale lease holder cannot pass a monotonic fencing check.", "Heartbeat receipt is evidence of observation, not proof of useful progress."], ["evidence.etcd-api", "evidence.etcd-concurrency", "evidence.zookeeper-recipes"], "core"),
    ctx("placement", "Placement constraints and assignment", "Where may an admitted work unit execute given hard constraints, preferences and topology?", ["candidate set", "affinity", "anti-affinity", "co-location", "spread", "assignment", "placement proof"], ["admission policy", "worker execution", "provider provisioning"], ["context.runtime-resource.resource-topology", "context.runtime-resource.scheduling-policy", "context.runtime-resource.resource-reservation"], ["Hard constraints are never traded for score.", "Assignment is versioned against inventory and demand editions."], ["evidence.k8s-scheduling", "evidence.k8s-topology", "evidence.kueue-topology", "evidence.ray-placement"], "core"),
    ctx("scheduling-policy", "Scheduling policy", "In what order and by which declared objective should eligible work receive feasible assignments?", ["policy identity", "priority", "fairness", "objective", "heuristic/exact method", "tie-break", "optimality/quality receipt"], ["capacity inventory", "workload semantics", "mechanism-specific dispatch"], ["context.runtime-resource.placement", "context.runtime-resource.preemption", "context.operations-research.optimization"], ["Policy, mechanism and observed decision are separate records.", "A heuristic result never claims optimality without a bound or proof."], ["evidence.drf", "evidence.firmament", "evidence.sparrow", "evidence.borg", "evidence.posix-2024"], "core"),
    ctx("preemption", "Priority, eviction and preemption", "When may running or reserved work be displaced, and what compensation is required?", ["preemption eligibility", "victim selection", "grace", "checkpoint opportunity", "resource reclaim", "preemption receipt"], ["business cancellation", "node failure", "autoscaling"], ["context.runtime-resource.scheduling-policy", "context.runtime-resource.attempt-control", "context.runtime-resource.checkpoint-recovery"], ["Preemption is not reported as application failure.", "Victim selection preserves protected-class and disruption constraints."], ["evidence.k8s-preemption", "evidence.slurm-qos", "evidence.kueue-concepts"]),
    ctx("autoscaling", "Autoscaling and elasticity", "When and how may replicas, allocations or provider capacity change in response to demand?", ["scaling target", "signal", "recommendation", "stabilization", "scale action", "hysteresis", "scale receipt"], ["business demand forecast", "provider billing", "scheduler placement"], ["context.runtime-resource.capacity-planning", "context.runtime-resource.control-reconciliation", "context.runtime-resource.resource-demand"], ["Scale recommendation, requested capacity and realized capacity are distinct.", "Every loop declares delay, hysteresis and maximum rate of change."], ["evidence.k8s-hpa", "evidence.k8s-node-autoscaling", "evidence.spark-scheduling"]),
    ctx("capacity-planning", "Capacity and feasibility planning", "Can forecast demand be served within topology, SLO, cost, energy and failure constraints?", ["capacity model", "demand scenario", "headroom", "fragmentation", "feasibility result", "sensitivity"], ["live scheduling", "business forecasting", "procurement decision"], ["context.runtime-resource.resource-pool", "context.runtime-resource.slo", "context.runtime-resource.accounting-cost"], ["Forecast uncertainty is retained.", "Aggregate free capacity does not prove a feasible placement."], ["evidence.k8s-node-autoscaling", "evidence.drf", "evidence.serverless-datacenter"]),
    ctx("failure-domain", "Failure domains, partitions and failover", "Which correlated failures can occur and which degraded or failover behaviors are permitted?", ["failure-domain identity", "partition model", "fault assumption", "redundancy", "failover", "degraded mode", "recovery evidence"], ["business continuity policy", "data durability semantics", "incident response"], ["context.runtime-resource.resource-topology", "context.runtime-resource.checkpoint-recovery", "context.runtime-resource.slo"], ["Redundancy claims name the failure domain they tolerate.", "Partition, crash, omission, corruption and operator action remain distinct."], ["evidence.k8s-topology", "evidence.mpi-4.1", "evidence.ray-placement"]),
    ctx("pressure-health", "Resource pressure and health", "What current evidence indicates saturation, degradation, unavailability or device health?", ["pressure observation", "health state", "capacity degradation", "taint", "measurement confidence", "health transition"], ["SLO judgment", "scheduler objective", "incident ownership"], ["context.runtime-resource.resource-topology", "context.runtime-resource.observability", "context.runtime-resource.control-reconciliation"], ["Health is time-scoped observation, not a permanent resource attribute.", "Pressure and utilization are not interchangeable."], ["evidence.linux-psi", "evidence.linux-cgroup-v2", "evidence.redfish", "evidence.k8s-dra"]),
    ctx("accounting-cost", "Usage accounting, cost and charge", "What was allocated and consumed, at what rate, by whom, and at what monetary cost?", ["allocation-time", "usage quantity", "rate", "cost attribution", "idle cost", "charge correction", "accounting receipt"], ["provider invoice authority", "budget approval", "business value"], ["context.runtime-resource.quota-budget", "context.runtime-resource.runtime-receipt", "context.runtime-resource.energy-carbon"], ["Requested, reserved, allocated, metered and billed quantities never collapse into one field.", "Corrections preserve the original charge lineage."], ["evidence.opencost", "evidence.focus-1.2", "evidence.nist-cloud"], "core"),
    ctx("energy-carbon", "Energy, power and carbon accounting", "What power, energy and carbon quantities are attributable to resource use and scheduling choices?", ["power envelope", "energy quantity", "operational carbon", "embodied carbon allocation", "carbon intensity", "attribution method"], ["sustainability strategy", "electricity market", "hardware lifecycle inventory authority"], ["context.runtime-resource.accounting-cost", "context.runtime-resource.scheduling-policy", "context.runtime-resource.observability"], ["Power, energy and carbon are dimensionally distinct.", "Estimated attribution names its model and uncertainty."], ["evidence.sci-iso", "evidence.sci-spec", "evidence.kepler"]),
    ctx("slo", "Runtime SLO and error budget", "Which service-level objectives constrain execution and how is compliance evaluated?", ["SLI contract", "objective", "window", "error budget", "burn", "violation", "evaluation receipt"], ["business outcome", "incident response", "raw telemetry collection"], ["context.runtime-resource.observability", "context.runtime-resource.capacity-planning", "context.runtime-resource.control-reconciliation"], ["An SLO names population, indicator, threshold and evaluation window.", "Missing telemetry cannot be silently interpreted as success."], ["evidence.opentelemetry-system", "evidence.openmetrics", "evidence.google-sre"]),
    ctx("observability", "Runtime observability", "Which signals identify an observed runtime entity and explain execution and resource behavior?", ["observed-resource identity", "metrics", "traces", "logs", "profiles", "correlation", "telemetry provenance"], ["SLO policy", "incident decision", "business analytics"], ["context.runtime-resource.runtime-receipt", "context.runtime-resource.pressure-health", "context.runtime-resource.slo"], ["Telemetry producer and observed entity are distinct.", "Sampling, aggregation and dropped-signal loss are explicit."], ["evidence.otel-resource", "evidence.opentelemetry-system", "evidence.openmetrics"]),
    ctx("runtime-receipt", "Execution and resource receipts", "What append-only evidence proves what the control plane requested and the runtime observed?", ["intent receipt", "admission receipt", "binding receipt", "start/stop receipt", "usage receipt", "outcome receipt", "causal chain"], ["business audit verdict", "provider invoice", "raw log storage"], ["context.runtime-resource.attempt-control", "context.runtime-resource.accounting-cost", "context.runtime-resource.control-reconciliation"], ["Receipts are append-only and content-addressed.", "A receipt proves only its issuer, scope, observation time and stated claim."], ["evidence.cloudevents", "evidence.otel-resource", "evidence.focus-1.2"], "core"),
    ctx("target-profile", "Execution target profile", "Which runtime, ABI, isolation, architecture and resource mechanisms can a target support?", ["target identity", "architecture", "runtime capabilities", "supported ABI", "resource controllers", "limits", "conformance evidence"], ["deployed resource occurrence", "workload demand", "provider commercial offer"], ["context.runtime-resource.executable-artifact", "context.runtime-resource.provider-occurrence", "context.runtime-resource.isolation-runtime"], ["Target profile is versioned and evidence-backed.", "Target compatibility is not inferred from architecture name alone."], ["evidence.oci-runtime", "evidence.wasm-core", "evidence.posix-2024"]),
    ctx("isolation-runtime", "Isolation and virtualization runtime", "Which process, container, VM or sandbox boundary constrains effects and resource access?", ["isolation kind", "namespace", "cgroup attachment", "VM boundary", "sandbox capability", "escape/failure contract"], ["application security policy", "image build", "orchestrator product"], ["context.runtime-resource.process-runtime", "context.runtime-resource.target-profile", "context.security.trust-boundary"], ["Isolation mechanism never implies a threat-model guarantee by name alone.", "Resource isolation and security isolation are evaluated separately."], ["evidence.oci-runtime", "evidence.linux-namespaces", "evidence.firecracker", "evidence.wasm-core"]),
    ctx("provider-occurrence", "Provider resource and deployment occurrence", "Which concrete provider-owned resource exists now, under what authority, edition and lifecycle?", ["provider resource identity", "deployment occurrence", "provisioning state", "region/zone", "offer binding", "decommission"], ["logical resource class", "product", "workload identity"], ["context.runtime-resource.resource-offer", "context.runtime-resource.target-profile", "context.runtime-resource.control-reconciliation"], ["A provider SKU, a purchased entitlement and a deployed occurrence are different identities.", "Occurrence state is reconciled from provider evidence."], ["evidence.nist-cloud", "evidence.redfish", "evidence.k8s-node-autoscaling"]),
    ctx("control-reconciliation", "Runtime control-plane reconciliation", "How is declared runtime state continuously compared with observed state and safely converged?", ["desired state", "observed state", "reconcile generation", "action", "backoff", "conflict", "reconciliation receipt"], ["product UI", "business workflow", "provider implementation"], ["context.runtime-resource.provider-occurrence", "context.runtime-resource.lease-fencing", "context.runtime-resource.runtime-receipt"], ["Reconciliation is generation- and fencing-aware.", "Repeated failure converges to a typed degraded or refused state, never infinite invisible retry."], ["evidence.kubernetes-controller", "evidence.etcd-api", "evidence.opentelemetry-system"], "core"),
    ctx("control-plane-product", "Runtime control-plane product boundary", "Which user outcome may package runtime contexts without becoming their semantic owner?", ["product promise", "supported personas", "operating obligations", "packaging boundary", "exit and portability"], ["resource semantics", "scheduler-policy ownership", "provider resource identity", "runtime libraries"], ["context.runtime-resource.control-reconciliation", "context.runtime-resource.provider-occurrence", "context.product.boundary"], ["A control-plane product packages contexts and libraries but owns no borrowed semantic type.", "Provider and library replacement seams are part of the product contract."], ["evidence.cncf-platforms", "evidence.nist-cloud"], "supporting"),
]


def typ(
    suffix: str,
    name: str,
    owner: str,
    category: str,
    definition: str,
    equality: str,
    invariants: list[str],
    confusions: list[str],
    evidence: list[str],
) -> dict:
    return {
        "record_kind": "runtime_resource_type",
        "type_id": f"type.runtime-resource.{suffix}",
        "edition": EDITION,
        "status": "research_candidate",
        "name": name,
        "owner_context_ref": f"context.runtime-resource.{owner}",
        "category": category,
        "definition": definition,
        "equality_semantics": equality,
        "canonical_form": "Canonical JSON with explicit edition, unit and scoped identifiers; no float quantities.",
        "invariants": invariants,
        "must_not_be_confused_with": confusions,
        "evidence_refs": evidence,
        "gaps": [],
    }


TYPE_SPECS = [
    ("work-unit-id", "WorkUnitId", "execution-contract", "identity", "Stable logical identity of one declared unit of executable work across attempts.", "Exact namespace, identifier and birth edition.", ["Never reused within its authority scope."], ["AttemptId", "JobId", "process ID"], ["evidence.k8s-job"]),
    ("job-id", "JobId", "attempt-control", "identity", "Identity of a finite collection of work units governed as one runtime job.", "Exact authority, namespace, identifier and generation.", ["A retry of a job may preserve JobId only when the job contract says so."], ["workflow ID", "scheduler queue ID"], ["evidence.slurm-job-state", "evidence.k8s-job"]),
    ("attempt-id", "AttemptId", "attempt-control", "identity", "Unique identity of one physical try to execute a work unit.", "Exact identifier; attempt ordinal is descriptive and insufficient alone.", ["Every retry creates a new AttemptId.", "An AttemptId has exactly one terminal outcome."], ["WorkUnitId", "process ID"], ["evidence.k8s-job", "evidence.temporal-timeouts"]),
    ("actor-id", "ActorId", "actor-runtime", "identity", "Logical actor identity scoped to an actor system and incarnation policy.", "System ID, logical ID and incarnation where restart semantics require it.", ["Incarnation change is observable when mailbox or state continuity is not preserved."], ["worker ID", "business entity ID"], ["evidence.ray-actors", "evidence.erlang-supervision"]),
    ("worker-id", "WorkerId", "executor-worker", "identity", "Identity of a concrete runtime worker occurrence.", "Executor scope, worker identifier and boot epoch.", ["Restart creates a new boot epoch."], ["resource slot", "actor", "provider instance"], ["evidence.dask-worker-state", "evidence.ray-actors"]),
    ("executor-id", "ExecutorId", "executor-worker", "identity", "Identity of a runtime component that assigns tasks to workers or slots.", "Authority, identifier and generation.", ["Executor identity is independent of host identity."], ["scheduler policy", "worker"], ["evidence.spark-scheduling"]),
    ("process-identity", "ProcessIdentity", "process-runtime", "identity", "Process identity robust to operating-system PID reuse.", "Boot identity, PID and process start identity.", ["PID alone never establishes equality across time."], ["numeric PID", "container ID"], ["evidence.posix-2024"]),
    ("thread-identity", "ThreadIdentity", "thread-runtime", "identity", "Thread identity scoped to a process incarnation.", "ProcessIdentity plus runtime thread identity and birth generation.", ["Thread ID reuse does not preserve identity."], ["async task", "CPU"], ["evidence.posix-2024", "evidence.rust-thread"]),
    ("async-task-id", "AsyncTaskId", "async-runtime", "identity", "Identity of a cooperatively scheduled asynchronous task.", "Runtime scope and task identity.", ["A task may migrate between worker threads without identity change."], ["thread ID", "future value"], ["evidence.tokio-task"]),
    ("resource-id", "ResourceId", "resource-topology", "identity", "Stable identity of a logical or physical allocatable resource.", "Owning authority, resource class, immutable identifier and incarnation where relevant.", ["Mutable hostname or provider display name is not sufficient."], ["ResourceClassId", "provider SKU", "offer"], ["evidence.redfish", "evidence.otel-resource"]),
    ("provider-resource-id", "ProviderResourceId", "provider-occurrence", "identity", "Provider-scoped identity of a provisioned or provisionable resource occurrence.", "Provider authority, account/project scope, provider resource identifier and incarnation.", ["Provider reuse must change incarnation or be detected by lifecycle evidence."], ["target profile", "SKU", "ResourceId"], ["evidence.otel-resource", "evidence.nist-cloud"]),
    ("deployment-occurrence-id", "DeploymentOccurrenceId", "provider-occurrence", "identity", "Identity of one realized deployment occurrence of a compiled runtime plan.", "Release ID, target ID and occurrence identifier.", ["Redeployment after destructive replacement creates a new occurrence."], ["product", "artifact", "provider resource"], ["evidence.oci-runtime"]),
    ("resource-class-id", "ResourceClassId", "resource-topology", "classifier", "Identity of a semantic resource dimension such as CPU time, exclusive GPU device or network bandwidth.", "Exact registry ID and edition.", ["Class identity includes units and sharing semantics."], ["resource instance", "provider SKU"], ["evidence.k8s-resources", "evidence.sycl-2020"]),
    ("resource-quantity", "ResourceQuantity", "resource-demand", "value_object", "Exact amount in one resource class and canonical unit.", "Dimension, rational magnitude, canonical unit and qualifier set.", ["Magnitude is finite and non-negative unless a delta type is explicitly used.", "Binary and decimal byte units never collapse."], ["capacity", "rate", "usage observation"], ["evidence.k8s-resources"]),
    ("resource-vector", "ResourceVector", "resource-demand", "value_object", "Finite map from resource class to exact quantity.", "Canonical ordered map after unit normalization.", ["No duplicate dimensions.", "Unknown dimensions are retained as typed gaps."], ["scalar slot count", "provider machine type"], ["evidence.drf", "evidence.k8s-resources"]),
    ("resource-demand", "ResourceDemand", "resource-demand", "aggregate", "Workload-owned minimum, target and maximum resource vectors with hard/soft topology constraints.", "Demand identity and edition; structural equality is not identity.", ["minimum <= target <= maximum under dimension partial order.", "Blocking dimensions are finite."], ["resource offer", "observed usage", "quota"], ["evidence.k8s-resources", "evidence.ray-placement"]),
    ("resource-offer", "ResourceOffer", "resource-offer", "aggregate", "Time-bounded promise of allocatable resource capacity and qualities backed by evidence.", "Offer ID and edition.", ["Offer names capacity, validity, interruptibility, topology and evidence freshness.", "Offer does not imply allocation."], ["SKU", "inventory observation", "allocation"], ["evidence.k8s-dra", "evidence.focus-1.2"]),
    ("resource-pool-id", "ResourcePoolId", "resource-pool", "identity", "Identity of a governed set of resource offers with a reconciled capacity ledger.", "Authority, pool ID and edition.", ["Membership changes increment pool edition."], ["scheduler queue", "quota"], ["evidence.kueue-clusterqueue"]),
    ("quota", "Quota", "quota-budget", "aggregate", "Authority-scoped maximum admitted or consumed quantity over a declared scope and window.", "Quota ID and edition.", ["Quota never claims physical availability.", "Usage and holds reconcile against limit."], ["capacity", "budget", "reservation"], ["evidence.k8s-quota", "evidence.kueue-clusterqueue"]),
    ("finite-budget", "FiniteBudget", "quota-budget", "aggregate", "Consumable bound over money, energy, carbon, attempts, time or another exact dimension.", "Budget ID and edition.", ["Currency/unit and accounting window are explicit.", "Hard effects require precharge or equivalent hold."], ["quota", "cost forecast", "invoice"], ["evidence.focus-1.2", "evidence.sci-iso"]),
    ("precharge", "Precharge", "quota-budget", "entity", "Atomic budget hold acquired before an effectful operation begins.", "Precharge ID.", ["At most one terminal commit, refund or expiry.", "Committed amount cannot exceed held amount without a new authorization."], ["reservation", "invoice charge"], ["evidence.focus-1.2"]),
    ("admission-decision", "AdmissionDecision", "admission-control", "event", "Accepted, held or refused result of evaluating work against policy, quota, evidence and coarse feasibility.", "Decision ID and immutable content digest.", ["Includes evaluated policy editions and typed reasons.", "Accepted is not scheduled."], ["placement assignment", "business approval"], ["evidence.kueue-concepts"]),
    ("reservation", "ResourceReservation", "resource-reservation", "entity", "Exclusive or shared capacity hold pending commit or expiry.", "Reservation ID.", ["Hold has owner, quantity, pool, validity and state.", "Expired reservation cannot commit."], ["allocation", "lease", "quota hold"], ["evidence.slurm-reservation", "evidence.ray-placement"]),
    ("allocation", "ResourceAllocation", "resource-reservation", "entity", "Committed assignment of resource capacity to a workload or occurrence.", "Allocation ID.", ["Allocation references committed reservation or atomic allocation proof.", "Release is idempotent and append-only evidenced."], ["usage", "offer", "lease"], ["evidence.k8s-dra", "evidence.slurm-reservation"]),
    ("lease", "Lease", "lease-fencing", "entity", "Time-limited authority to act on an allocation or coordination role, renewable under declared rules.", "Lease ID and generation.", ["Expiry is determined by lease authority time.", "Renewal never decreases fencing token."], ["reservation", "heartbeat", "business delegation"], ["evidence.etcd-api", "evidence.etcd-concurrency"]),
    ("fencing-token", "FencingToken", "lease-fencing", "value_object", "Monotonically ordered authority token used by protected resources to reject stale actors.", "Exact authority scope and monotonic ordinal.", ["Protected effects accept only a token newer than the last accepted token."], ["lease ID", "wall-clock timestamp", "lock ownership claim"], ["evidence.etcd-concurrency", "evidence.zookeeper-recipes"]),
    ("heartbeat", "Heartbeat", "lease-fencing", "observation", "Time-scoped signal that an identified actor was observable to an authority.", "Issuer, subject, sequence and observation time.", ["Does not prove useful progress.", "Missed heartbeat threshold is policy, not part of the observation."], ["lease renewal", "health verdict", "progress receipt"], ["evidence.temporal-timeouts", "evidence.etcd-api"]),
    ("topology-graph", "ResourceTopologyGraph", "resource-topology", "structure", "Versioned graph of resource containment, attachment, proximity, sharing and failure relations.", "Graph digest after canonical node and edge ordering.", ["Each edge names relation kind, validity and evidence.", "Containment and failure correlation are separate edges."], ["network graph", "organization hierarchy", "placement assignment"], ["evidence.hwloc", "evidence.cxl-3.2", "evidence.kueue-topology"]),
    ("placement-constraint", "PlacementConstraint", "placement", "value_object", "Hard predicate or soft scored preference over resource/topology candidates.", "Canonical predicate/score expression and owner edition.", ["Hardness is explicit.", "Soft preference declares weighting and tie-break interaction."], ["scheduler policy", "provider selector string"], ["evidence.k8s-scheduling", "evidence.k8s-topology"]),
    ("placement-assignment", "PlacementAssignment", "placement", "event", "Versioned selection of concrete resource candidates for admitted work.", "Assignment ID and immutable content digest.", ["References exact demand and inventory editions.", "Carries hard-constraint proof and score trace."], ["allocation", "reservation", "scheduler recommendation"], ["evidence.firmament", "evidence.k8s-scheduling"]),
    ("scheduler-policy", "SchedulerPolicy", "scheduling-policy", "specification", "Owned objective, eligibility, ordering, selection, tie-break and quality contract for scheduling.", "Policy ID and edition.", ["Mechanism and provider are not embedded in policy identity.", "Heuristic policies disclose lack of optimality proof."], ["scheduler implementation", "queue configuration", "OR method"], ["evidence.drf", "evidence.firmament", "evidence.sparrow"]),
    ("priority", "Priority", "scheduling-policy", "value_object", "Ordered urgency class within a declared authority and policy scope.", "Authority, policy edition and ordinal/class.", ["Priority has no cross-policy ordering without an explicit mapping."], ["business importance", "preemption permission", "deadline"], ["evidence.posix-2024", "evidence.k8s-preemption"]),
    ("preemption-policy", "PreemptionPolicy", "preemption", "specification", "Rules governing eligibility, victim selection, grace, checkpoint and compensation.", "Policy ID and edition.", ["Names protected classes and disruption limits.", "Preempted outcome remains distinct from failure."], ["cancellation policy", "eviction mechanism"], ["evidence.k8s-preemption", "evidence.slurm-qos"]),
    ("deadline", "Deadline", "cancellation-deadline", "value_object", "Absolute instant by which a scoped phase is expected to complete.", "Time scale, instant, uncertainty and scope.", ["Time scale and clock authority are explicit."], ["duration timeout", "SLA window", "lease expiry"], ["evidence.grpc-deadline"]),
    ("cancellation-request", "CancellationRequest", "cancellation-deadline", "command", "Idempotent request that identified execution stop under a declared mode and deadline.", "Request ID.", ["Acknowledgement and terminal stop are separate facts.", "Request names graceful, checkpoint, interrupt or force mode."], ["cancelled outcome", "kill signal"], ["evidence.tokio-cancellation", "evidence.grpc-deadline"]),
    ("backpressure-signal", "BackpressureSignal", "backpressure", "event", "Downstream capacity or demand signal constraining upstream emission.", "Channel scope, sequence and demand/credit value.", ["Credit never becomes negative.", "Overflow policy is separately declared."], ["autoscaling signal", "rate limit", "queue depth metric"], ["evidence.reactive-streams", "evidence.grpc-flow"]),
    ("checkpoint-ref", "CheckpointRef", "checkpoint-recovery", "identity", "Content-addressed checkpoint plus compatibility and lineage metadata.", "Digest, schema, artifact and runtime compatibility tuple.", ["Checkpoint bytes without compatibility metadata are not resumable proof."], ["snapshot name", "backup", "artifact"], ["evidence.criu", "evidence.temporal-docs"]),
    ("failure-domain", "FailureDomain", "failure-domain", "aggregate", "Set or relation of resources exposed to a correlated fault assumption.", "Authority, domain ID, failure-mode edition and membership edition.", ["Failure mode and correlation assumption are explicit."], ["availability zone label", "topology group", "blast-radius estimate"], ["evidence.k8s-topology", "evidence.redfish"]),
    ("pressure-observation", "ResourcePressureObservation", "pressure-health", "observation", "Measured time in which work was delayed due to CPU, memory or I/O contention.", "Subject, interval, metric edition and value.", ["Pressure is not inferred from utilization alone."], ["utilization", "health verdict", "SLO violation"], ["evidence.linux-psi"]),
    ("health-state", "ResourceHealthState", "pressure-health", "state", "Time-scoped assessed availability/degradation state of a resource.", "Subject, assessor, observation time and assessment generation.", ["Includes evidence and expiry/recheck trigger."], ["static capability", "provider status page"], ["evidence.redfish", "evidence.k8s-dra"]),
    ("cost-rate", "CostRate", "accounting-cost", "value_object", "Monetary amount per exact pricing unit and validity interval.", "Currency, rational amount, pricing unit, provider/authority and validity.", ["List, contracted, effective and billed rate kinds are distinct."], ["total cost", "resource quantity", "budget"], ["evidence.focus-1.2", "evidence.opencost"]),
    ("usage-receipt", "ResourceUsageReceipt", "accounting-cost", "receipt", "Signed or attributable observation of consumed or allocated quantity over an interval.", "Receipt digest.", ["Names measurement method, subject, interval, unit, uncertainty and issuer.", "Never overwrites prior corrected observations."], ["invoice line", "allocation", "telemetry sample"], ["evidence.focus-1.2", "evidence.opencost"]),
    ("power-envelope", "PowerEnvelope", "energy-carbon", "value_object", "Permitted or observed power range for a resource or workload.", "Subject, watts, interval and kind (limit/target/observed).", ["Power is a rate and never represented as energy."], ["energy quantity", "thermal design power"], ["evidence.sci-spec", "evidence.kepler"]),
    ("energy-receipt", "EnergyReceipt", "energy-carbon", "receipt", "Attributed energy quantity over a time interval with measurement/model provenance.", "Receipt digest.", ["Uses joules or canonically convertible energy unit.", "Estimated values include model identity and uncertainty."], ["power sample", "carbon amount", "electricity invoice"], ["evidence.sci-iso", "evidence.kepler"]),
    ("slo-contract", "RuntimeSloContract", "slo", "specification", "Population, indicator, objective, window and error-budget contract for runtime behavior.", "SLO ID and edition.", ["No objective without exact SLI and window.", "Missing data policy is explicit."], ["product promise", "alert threshold", "capacity target"], ["evidence.google-sre", "evidence.openmetrics"]),
    ("target-profile", "TargetProfile", "target-profile", "specification", "Evidence-backed execution target capabilities, ABIs, mechanisms and constraints.", "Target ID and edition.", ["Compatibility is proved against artifact and runtime requirements."], ["provider occurrence", "container image", "machine SKU"], ["evidence.oci-runtime", "evidence.wasm-core"]),
    ("runtime-receipt", "RuntimeReceipt", "runtime-receipt", "receipt", "Append-only typed evidence of one runtime/control-plane fact linked into a causal chain.", "Canonical content digest and issuer signature scope.", ["Includes subject, claim, event and recording time, issuer and evidence scope."], ["domain event", "raw log", "business audit verdict"], ["evidence.cloudevents", "evidence.otel-resource"]),
]

TYPES = [typ(*spec) for spec in TYPE_SPECS]


def state_machine(
    suffix: str,
    owner: str,
    subject_type: str,
    states: list[str],
    initial: str,
    terminal: list[str],
    transitions: list[tuple[str, str, str]],
    precedence: list[str],
    evidence: list[str],
) -> dict:
    return {
        "record_kind": "state_machine",
        "state_machine_id": f"state-machine.runtime-resource.{suffix}",
        "edition": EDITION,
        "status": "research_candidate",
        "owner_context_ref": f"context.runtime-resource.{owner}",
        "subject_type_ref": f"type.runtime-resource.{subject_type}",
        "states": states,
        "initial_state": initial,
        "terminal_states": terminal,
        "transitions": [{"from": a, "command_or_fact": b, "to": c} for a, b, c in transitions],
        "outcome_precedence": precedence,
        "illegal_transition_law": "Refuse with the current generation and allowed-next-state set; never coerce.",
        "concurrency": "Optimistic generation check or serialized aggregate command handling is required.",
        "idempotency": "Duplicate command identity returns the original transition receipt.",
        "time_model": "Every transition carries event time and recording time; timeout authority is explicit.",
        "evidence_refs": evidence,
    }


STATE_MACHINES = [
    state_machine("work-unit", "attempt-control", "work-unit-id", ["declared", "admission_pending", "admitted", "queued", "running", "succeeded", "failed", "cancelled", "timed_out", "preempted", "refused"], "declared", ["succeeded", "failed", "cancelled", "timed_out", "preempted", "refused"], [("declared", "request_admission", "admission_pending"), ("admission_pending", "admitted", "admitted"), ("admission_pending", "refused", "refused"), ("admitted", "enqueue", "queued"), ("queued", "attempt_started", "running"), ("running", "attempt_succeeded", "succeeded"), ("running", "attempt_failed", "failed"), ("running", "cancellation_completed", "cancelled"), ("running", "deadline_elapsed_and_stopped", "timed_out"), ("running", "preemption_completed", "preempted")], ["succeeded cannot be replaced", "forced termination outranks late success observation unless commit authority proves success before termination", "conflicts produce adjudication gap"], ["evidence.k8s-job", "evidence.slurm-job-state"]),
    state_machine("attempt", "attempt-control", "attempt-id", ["created", "assigned", "starting", "running", "checkpointing", "draining", "succeeded", "failed", "cancelled", "timed_out", "preempted", "lost"], "created", ["succeeded", "failed", "cancelled", "timed_out", "preempted", "lost"], [("created", "assignment_committed", "assigned"), ("assigned", "start_requested", "starting"), ("starting", "runtime_started", "running"), ("running", "checkpoint_requested", "checkpointing"), ("checkpointing", "checkpoint_written", "running"), ("running", "drain_requested", "draining"), ("draining", "completed", "succeeded"), ("running", "completed", "succeeded"), ("running", "failed", "failed"), ("running", "cancelled", "cancelled"), ("running", "timed_out", "timed_out"), ("running", "preempted", "preempted"), ("starting", "lease_lost", "lost"), ("running", "lease_lost", "lost")], ["one terminal outcome", "commit evidence precedes observer timeout when causally proven", "otherwise ambiguity is retained"], ["evidence.dask-worker-state", "evidence.temporal-timeouts"]),
    state_machine("reservation", "resource-reservation", "reservation", ["requested", "held", "committed", "released", "expired", "refused"], "requested", ["released", "expired", "refused"], [("requested", "capacity_held", "held"), ("requested", "refused", "refused"), ("held", "commit", "committed"), ("held", "hold_expired", "expired"), ("held", "release", "released"), ("committed", "release", "released")], ["expiry observed by authority forbids later commit", "duplicate release preserves first receipt"], ["evidence.slurm-reservation", "evidence.ray-placement"]),
    state_machine("allocation", "resource-reservation", "allocation", ["committed", "preparing", "ready", "active", "draining", "released", "revoked", "lost"], "committed", ["released", "revoked", "lost"], [("committed", "prepare", "preparing"), ("preparing", "prepared", "ready"), ("ready", "activate", "active"), ("active", "drain", "draining"), ("draining", "release", "released"), ("active", "release", "released"), ("active", "revoke", "revoked"), ("preparing", "resource_lost", "lost"), ("active", "resource_lost", "lost")], ["revocation/loss prevents new effects", "already committed external effects require separate compensation"], ["evidence.k8s-dra"]),
    state_machine("lease", "lease-fencing", "lease", ["issued", "active", "renewal_due", "expired", "revoked", "released"], "issued", ["expired", "revoked", "released"], [("issued", "acknowledged", "active"), ("active", "renewal_window_open", "renewal_due"), ("renewal_due", "renewed", "active"), ("renewal_due", "ttl_elapsed", "expired"), ("active", "revoked", "revoked"), ("active", "released", "released")], ["authority-observed expiry is terminal", "stale renewal cannot revive without a new lease generation"], ["evidence.etcd-api", "evidence.etcd-concurrency"]),
    state_machine("worker", "executor-worker", "worker-id", ["registered", "warming", "ready", "busy", "draining", "unreachable", "terminated"], "registered", ["terminated"], [("registered", "warmup_started", "warming"), ("warming", "ready", "ready"), ("ready", "assignment", "busy"), ("busy", "slot_available", "ready"), ("ready", "drain", "draining"), ("busy", "drain", "draining"), ("draining", "all_work_stopped", "terminated"), ("ready", "heartbeat_missed", "unreachable"), ("busy", "heartbeat_missed", "unreachable"), ("unreachable", "same_incarnation_recovered", "ready"), ("unreachable", "declared_dead", "terminated")], ["new boot epoch is a new WorkerId", "unreachable is not immediately dead"], ["evidence.dask-worker-state", "evidence.ray-actors"]),
    state_machine("checkpoint", "checkpoint-recovery", "checkpoint-ref", ["requested", "capturing", "sealed", "verified", "incompatible", "corrupt", "expired"], "requested", ["verified", "incompatible", "corrupt", "expired"], [("requested", "capture_started", "capturing"), ("capturing", "content_sealed", "sealed"), ("sealed", "compatibility_and_integrity_pass", "verified"), ("sealed", "compatibility_failed", "incompatible"), ("sealed", "integrity_failed", "corrupt"), ("verified", "retention_elapsed", "expired")], ["integrity failure outranks compatibility", "expired checkpoint cannot resume without explicit archival recovery"], ["evidence.criu", "evidence.temporal-docs"]),
    state_machine("provider-occurrence", "provider-occurrence", "provider-resource-id", ["declared", "provisioning", "available", "degraded", "draining", "deprovisioning", "gone", "provision_failed"], "declared", ["gone", "provision_failed"], [("declared", "provision", "provisioning"), ("provisioning", "provider_ready", "available"), ("provisioning", "provider_failed", "provision_failed"), ("available", "health_degraded", "degraded"), ("degraded", "health_restored", "available"), ("available", "drain", "draining"), ("degraded", "drain", "draining"), ("draining", "deprovision", "deprovisioning"), ("deprovisioning", "provider_absent", "gone")], ["provider-not-found is not gone without identity and consistency-window proof", "deprovision failure remains non-terminal"], ["evidence.nist-cloud", "evidence.redfish"]),
    state_machine("autoscaling-loop", "autoscaling", "resource-demand", ["observing", "recommending", "stabilizing", "requesting", "waiting_realization", "satisfied", "degraded", "stopped"], "observing", ["stopped"], [("observing", "signal_window_complete", "recommending"), ("recommending", "recommendation_stable", "stabilizing"), ("stabilizing", "action_allowed", "requesting"), ("requesting", "request_accepted", "waiting_realization"), ("waiting_realization", "capacity_realized", "satisfied"), ("waiting_realization", "deadline_or_refusal", "degraded"), ("satisfied", "next_window", "observing"), ("degraded", "next_window", "observing"), ("observing", "stop_requested", "stopped")], ["safety minimum overrides scale-down recommendation", "provider realization is authoritative for realized capacity"], ["evidence.k8s-hpa", "evidence.k8s-node-autoscaling"]),
    state_machine("cancellation", "cancellation-deadline", "cancellation-request", ["requested", "delivered", "acknowledged", "draining", "completed", "forced", "undeliverable"], "requested", ["completed", "forced", "undeliverable"], [("requested", "delivered", "delivered"), ("delivered", "acknowledged", "acknowledged"), ("acknowledged", "graceful_stop_started", "draining"), ("draining", "stopped", "completed"), ("delivered", "force_deadline_elapsed", "forced"), ("acknowledged", "force_deadline_elapsed", "forced"), ("requested", "delivery_impossible", "undeliverable")], ["completed success before delivery may supersede cancellation only with causal commit proof", "forced retains incomplete-cleanup risk"], ["evidence.grpc-deadline", "evidence.temporal-timeouts"]),
]


def resource_class(
    suffix: str,
    name: str,
    dimension: str,
    unit: str,
    consumability: str,
    shareability: str,
    divisibility: str,
    compressibility: str,
    topology: list[str],
    hazards: list[str],
    evidence: list[str],
) -> dict:
    return {
        "record_kind": "resource_class",
        "resource_class_id": f"resource-class.{suffix}",
        "edition": EDITION,
        "status": "research_candidate",
        "name": name,
        "dimension": dimension,
        "canonical_unit": unit,
        "consumability": consumability,
        "shareability": shareability,
        "divisibility": divisibility,
        "compressibility": compressibility,
        "overcommit_law": "Forbidden unless an offer explicitly states enforcement, degradation and failure semantics.",
        "topology_relations": topology,
        "reservation_semantics": "Resource-class-specific; must be declared by each offer.",
        "usage_measurement": "Method, interval, uncertainty and issuer are required.",
        "hazards": hazards,
        "evidence_refs": evidence,
    }


RESOURCE_CLASS_SPECS = [
    ("cpu-time", "CPU execution time", "time", "nanosecond", "renewable_rate", "time_shared", "continuous", "compressible", ["socket", "NUMA node", "core", "hardware thread"], ["throttling", "steal time", "priority inversion"], ["evidence.posix-2024", "evidence.linux-cgroup-v2"]),
    ("cpu-share", "CPU contention share", "dimensionless_weight", "ratio", "renewable_rate", "shared_weighted", "continuous", "compressible", ["cgroup hierarchy", "scheduler domain"], ["weight is not guaranteed CPU", "contention-dependent delivery"], ["evidence.linux-cgroup-v2", "evidence.k8s-resources"]),
    ("cpu-core-exclusive", "Exclusive CPU core", "count", "core", "reusable_capacity", "exclusive", "integer", "non_compressible", ["socket", "NUMA node", "cache domain"], ["SMT sibling interference", "frequency variability"], ["evidence.k8s-cpu-manager", "evidence.hwloc"]),
    ("cpu-affinity-slot", "CPU affinity placement", "set_membership", "cpu-set", "reusable_capacity", "exclusive_or_shared", "set", "non_compressible", ["CPU set", "NUMA node", "cache domain"], ["hotplug", "cpuset hierarchy conflict"], ["evidence.linux-cgroup-v2", "evidence.hwloc"]),
    ("gpu-device-exclusive", "Exclusive GPU device", "count", "device", "reusable_capacity", "exclusive", "integer", "non_compressible", ["PCIe root", "NUMA node", "fabric island"], ["device reset blast radius", "driver/ABI mismatch"], ["evidence.k8s-dra", "evidence.sycl-2020"]),
    ("gpu-partition", "Partitioned GPU resource", "count_or_capacity_vector", "partition", "reusable_capacity", "partitioned", "discrete", "non_compressible", ["parent device", "memory slice", "compute slice", "fabric island"], ["shared-engine interference", "partition profile incompatibility"], ["evidence.k8s-dra", "evidence.cuda-guide"]),
    ("accelerator-device", "Accelerator device", "count_and_capabilities", "device", "reusable_capacity", "exclusive_or_shared", "discrete", "non_compressible", ["host attachment", "fabric", "memory domain"], ["capability mismatch", "firmware/driver incompatibility"], ["evidence.k8s-dra", "evidence.opencl-3"]),
    ("accelerator-kernel-slot", "Accelerator kernel concurrency slot", "count", "slot", "renewable_rate", "shared_bounded", "integer", "partially_compressible", ["command queue", "compute unit", "device"], ["head-of-line blocking", "occupancy interference"], ["evidence.sycl-2020", "evidence.opencl-3"]),
    ("memory-capacity", "Volatile memory capacity", "information", "byte", "reusable_capacity", "shared_or_exclusive", "integer_bytes", "non_compressible", ["NUMA node", "memory tier", "device context", "CXL pool"], ["OOM termination", "paging latency", "remote-tier latency"], ["evidence.linux-cgroup-v2", "evidence.cxl-3.2"]),
    ("memory-bandwidth", "Memory bandwidth", "information_rate", "byte_per_second", "renewable_rate", "shared_contended", "continuous", "compressible", ["memory controller", "NUMA node", "interconnect"], ["contention", "read/write asymmetry", "measurement model error"], ["evidence.hwloc", "evidence.sycl-2020"]),
    ("memory-latency-class", "Memory latency class", "duration_distribution", "nanosecond_distribution", "quality_attribute", "shared_contended", "continuous", "non_compressible", ["NUMA node", "memory tier", "fabric hop"], ["tail latency", "migration instability"], ["evidence.cxl-3.2", "evidence.hwloc"]),
    ("memory-hugepage", "Huge page capacity", "information", "byte", "reusable_capacity", "reserved_pool", "integer_page", "non_compressible", ["NUMA node", "page size"], ["fragmentation", "allocation failure despite free base pages"], ["evidence.linux-cgroup-v2"]),
    ("ephemeral-storage-capacity", "Ephemeral storage capacity", "information", "byte", "reusable_capacity", "shared_or_quota", "integer_bytes", "non_compressible", ["node", "filesystem", "device"], ["eviction", "inode exhaustion", "write amplification"], ["evidence.k8s-resources"]),
    ("storage-iops", "Storage operations rate", "operation_rate", "operation_per_second", "renewable_rate", "shared_contended", "continuous", "compressible", ["volume", "device", "queue"], ["operation-size ambiguity", "burst-credit exhaustion"], ["evidence.redfish"]),
    ("storage-throughput", "Storage transfer throughput", "information_rate", "byte_per_second", "renewable_rate", "shared_contended", "continuous", "compressible", ["volume", "device", "path"], ["read/write asymmetry", "burst policy"], ["evidence.redfish"]),
    ("io-queue-depth", "I/O queue depth", "count", "in_flight_operation", "reusable_capacity", "shared_bounded", "integer", "non_compressible", ["device queue", "runtime ring"], ["latency amplification", "starvation"], ["evidence.io-uring"]),
    ("network-bandwidth-ingress", "Ingress network bandwidth", "information_rate", "bit_per_second", "renewable_rate", "shared_contended", "continuous", "compressible", ["NIC", "link", "fabric path", "zone"], ["oversubscription", "packet loss", "provider metering granularity"], ["evidence.opentelemetry-system"]),
    ("network-bandwidth-egress", "Egress network bandwidth", "information_rate", "bit_per_second", "renewable_rate", "shared_contended", "continuous", "compressible", ["NIC", "link", "fabric path", "billing boundary"], ["oversubscription", "cost boundary mismatch"], ["evidence.opentelemetry-system", "evidence.focus-1.2"]),
    ("network-packet-rate", "Network packet rate", "operation_rate", "packet_per_second", "renewable_rate", "shared_contended", "continuous", "compressible", ["NIC queue", "link", "virtual switch"], ["small-packet saturation", "interrupt pressure"], ["evidence.opentelemetry-system"]),
    ("rdma-endpoint", "RDMA endpoint and queue-pair capacity", "count", "endpoint", "reusable_capacity", "exclusive_or_partitioned", "integer", "non_compressible", ["HCA", "port", "fabric"], ["protection-domain mismatch", "fabric partition"], ["evidence.mpi-4.1"]),
    ("file-descriptor", "File descriptor slot", "count", "descriptor", "reusable_capacity", "process_scoped", "integer", "non_compressible", ["process", "user", "system"], ["exhaustion", "descriptor leak"], ["evidence.posix-2024"]),
    ("process-slot", "Process slot", "count", "process", "reusable_capacity", "quota_scoped", "integer", "non_compressible", ["user", "cgroup", "host"], ["fork failure", "PID exhaustion"], ["evidence.posix-spawn", "evidence.linux-cgroup-v2"]),
    ("worker-slot", "Runtime worker slot", "count", "slot", "reusable_capacity", "runtime_scoped", "integer", "non_compressible", ["executor", "worker pool", "host"], ["queue growth", "blocking work starvation"], ["evidence.dask-worker-state", "evidence.ray-actors"]),
    ("license-entitlement", "Concurrent license entitlement", "count", "seat", "reusable_capacity", "exclusive_or_shared", "integer", "non_compressible", ["license server", "organization", "region"], ["external authority outage", "lease expiry"], ["evidence.slurm-reservation"]),
    ("wall-clock-budget", "Wall-clock execution budget", "time", "second", "consumable", "work_scoped", "continuous", "non_compressible", ["attempt", "job", "queue"], ["clock discontinuity", "cleanup overrun"], ["evidence.slurm-job-state", "evidence.grpc-deadline"]),
    ("attempt-budget", "Attempt count budget", "count", "attempt", "consumable", "work_scoped", "integer", "non_compressible", ["work unit", "job"], ["retry storm", "duplicated side effects"], ["evidence.temporal-timeouts", "evidence.k8s-job"]),
    ("monetary-budget", "Monetary spend budget", "money", "currency_minor_unit", "consumable", "authority_scoped", "integer", "non_compressible", ["account", "cost center", "workload"], ["rate staleness", "currency mismatch", "late billing corrections"], ["evidence.focus-1.2", "evidence.opencost"]),
    ("power-limit", "Power limit", "power", "watt", "renewable_rate", "resource_scoped", "continuous", "non_compressible", ["device", "socket", "rack", "site"], ["thermal throttling", "shared attribution"], ["evidence.sci-spec", "evidence.kepler"]),
    ("energy-budget", "Energy budget", "energy", "joule", "consumable", "authority_scoped", "continuous", "non_compressible", ["workload", "host", "site"], ["model error", "double attribution"], ["evidence.sci-iso", "evidence.kepler"]),
    ("carbon-budget", "Carbon budget", "mass_co2e", "gram_co2e", "consumable", "authority_scoped", "continuous", "non_compressible", ["workload", "organization", "region-time"], ["marginal/average intensity mismatch", "embodied allocation uncertainty"], ["evidence.sci-iso", "evidence.sci-spec"]),
    ("control-plane-qps", "Control-plane request capacity", "operation_rate", "request_per_second", "renewable_rate", "shared_contended", "continuous", "compressible", ["API server", "tenant", "controller"], ["reconciliation storm", "throttling", "priority inversion"], ["evidence.kubernetes-controller"]),
]

RESOURCE_CLASSES = [resource_class(*spec) for spec in RESOURCE_CLASS_SPECS]


SCHEDULING_POLICIES = [
    {"policy_id": "scheduling-policy.fifo", "family": "ordering", "objective": "oldest eligible work first", "guarantee": "deterministic only under declared equal-priority tie-break and stable eligible set", "method_refs": [], "required_inputs": ["eligibility", "enqueue sequence", "priority"], "tradeoffs": ["head-of-line blocking", "ignores multidimensional fit"], "evidence_refs": ["evidence.posix-2024"]},
    {"policy_id": "scheduling-policy.round-robin", "family": "time_sharing", "objective": "bounded turn taking among runnable peers", "guarantee": "share/fairness depends on quantum and contention scope", "method_refs": [], "required_inputs": ["runnable set", "priority", "quantum"], "tradeoffs": ["context-switch overhead", "not deadline optimal"], "evidence_refs": ["evidence.posix-2024"]},
    {"policy_id": "scheduling-policy.bin-pack", "family": "placement_heuristic", "objective": "increase utilization or reduce active resources", "guarantee": "heuristic unless exact solver and bound are attached", "method_refs": ["method.operations-research.bin-packing"], "required_inputs": ["resource vectors", "candidate capacities", "hard constraints", "score weights"], "tradeoffs": ["fragmentation", "failure concentration", "tail contention"], "evidence_refs": ["evidence.k8s-binpacking"]},
    {"policy_id": "scheduling-policy.spread", "family": "placement_heuristic", "objective": "distribute work across topology or failure domains", "guarantee": "declared max skew or preference only", "method_refs": [], "required_inputs": ["topology graph", "domain cardinality", "skew", "hardness"], "tradeoffs": ["higher communication cost", "lower packing efficiency"], "evidence_refs": ["evidence.k8s-topology"]},
    {"policy_id": "scheduling-policy.gang", "family": "co_scheduling", "objective": "reserve all required members before any start", "guarantee": "all-or-nothing reservation within declared group and timeout", "method_refs": ["method.operations-research.resource-constrained-scheduling"], "required_inputs": ["bundle set", "topology constraints", "reservation timeout"], "tradeoffs": ["queue delay", "fragmentation", "deadlock without ordering"], "evidence_refs": ["evidence.ray-placement", "evidence.kueue-topology"]},
    {"policy_id": "scheduling-policy.backfill", "family": "queue_optimization", "objective": "use holes without delaying protected reservations", "guarantee": "depends on runtime estimate and reservation model", "method_refs": ["method.operations-research.scheduling"], "required_inputs": ["runtime estimate", "reservation horizon", "priority"], "tradeoffs": ["estimate error", "starvation without aging"], "evidence_refs": ["evidence.slurm-reservation"]},
    {"policy_id": "scheduling-policy.dominant-resource-fairness", "family": "multiresource_fairness", "objective": "maximize minimum dominant share", "guarantee": "strategy-proof, envy-free and Pareto efficient under the paper model", "method_refs": ["method.operations-research.max-min-fairness"], "required_inputs": ["tenant demands", "resource capacities", "weights"], "tradeoffs": ["model assumptions may not cover topology or indivisible devices"], "evidence_refs": ["evidence.drf"]},
    {"policy_id": "scheduling-policy.min-cost-flow", "family": "global_optimization", "objective": "minimize declared placement cost over a flow network", "guarantee": "optimal for encoded network and solver termination; model fidelity is separate", "method_refs": ["method.operations-research.min-cost-flow"], "required_inputs": ["task graph", "resource graph", "edge capacities", "cost model"], "tradeoffs": ["model/update cost", "central coordination"], "evidence_refs": ["evidence.firmament"]},
    {"policy_id": "scheduling-policy.power-of-two-sampling", "family": "distributed_heuristic", "objective": "low-latency placement without centralized state", "guarantee": "probabilistic performance under the paper model", "method_refs": ["method.operations-research.randomized-load-balancing"], "required_inputs": ["sample count", "queue estimates", "late binding policy"], "tradeoffs": ["stale local views", "quality variance"], "evidence_refs": ["evidence.sparrow"]},
    {"policy_id": "scheduling-policy.work-stealing", "family": "decentralized_balancing", "objective": "move ready work from busy to idle workers", "guarantee": "runtime-specific; no global optimality claim", "method_refs": [], "required_inputs": ["stealable task set", "victim selection", "locality cost"], "tradeoffs": ["data transfer", "cache loss", "duplicate races"], "evidence_refs": ["evidence.dask-worker-state"]},
    {"policy_id": "scheduling-policy.deadline-aware", "family": "real_time", "objective": "meet declared completion deadlines", "guarantee": "requires schedulability proof for hard real-time claim", "method_refs": ["method.operations-research.deadline-scheduling"], "required_inputs": ["deadline", "execution-time bounds", "preemption cost", "resource model"], "tradeoffs": ["requires reliable bounds", "may reduce throughput"], "evidence_refs": ["evidence.posix-2024"]},
    {"policy_id": "scheduling-policy.cost-aware", "family": "economic_optimization", "objective": "minimize expected cost subject to hard SLO and policy constraints", "guarantee": "quality depends on rate validity and demand uncertainty", "method_refs": ["method.operations-research.robust-optimization"], "required_inputs": ["cost rates", "resource demand", "interruptibility", "SLO"], "tradeoffs": ["rate staleness", "spot interruption", "transfer charges"], "evidence_refs": ["evidence.focus-1.2", "evidence.harvest-serverless"]},
    {"policy_id": "scheduling-policy.energy-carbon-aware", "family": "sustainability_optimization", "objective": "reduce energy or carbon subject to performance, locality and authority constraints", "guarantee": "must distinguish energy efficiency from carbon intensity and preserve temporal/region method", "method_refs": ["method.operations-research.multi-objective-optimization"], "required_inputs": ["energy model", "carbon intensity", "SLO", "data locality", "time flexibility"], "tradeoffs": ["delayed work", "migration energy", "model uncertainty"], "evidence_refs": ["evidence.sci-iso", "evidence.kepler"]},
]
for policy in SCHEDULING_POLICIES:
    policy.update({"record_kind": "scheduling_policy", "edition": EDITION, "status": "research_candidate", "owner_context_ref": "context.runtime-resource.scheduling-policy"})


def decision(
    suffix: str,
    owner: str,
    question: str,
    values: list[str],
    phase: str,
    default_law: str,
    default_value: str | None,
    constraints: list[str],
    implications: list[str],
    affects: list[str],
    evidence: list[str],
) -> dict:
    return {
        "decision_id": f"decision.runtime-resource.{suffix}",
        "edition": 1,
        "status": "hypothesis",
        "owner_context_ref": f"context.runtime-resource.{owner}",
        "question": question,
        "value_contract": f"value-contract.runtime-resource.{suffix}.v1",
        "allowed_values": values,
        "binding_phase": phase,
        "authority_ref": f"authority.runtime-resource.{owner}",
        "default_law": default_law,
        "default_value": default_value,
        "constraints": constraints,
        "conflicts": [],
        "implications": implications,
        "affects_contracts": affects,
        "evidence_required": evidence,
        "change_semantics": ["Changing after binding invalidates affected bindings and requires semantic diff plus runtime disposition."],
        "gaps": [],
    }


DECISION_SPECS = [
    ("execution-model", "execution-contract", "Which execution identity and isolation model is required?", ["process", "thread", "async_task", "actor", "distributed_task", "compute_kernel", "wasm_component", "serverless_invocation"], "logical_planning", "forbidden", None, ["Selected model must satisfy effect, isolation and target requirements."], ["Determines runtime state machine and backend offer family."], ["contract.runtime-resource.execution-contract.v1"], ["evidence.posix-2024", "evidence.wasm-core"]),
    ("completion-guarantee", "execution-contract", "Which completion/delivery guarantee may be claimed?", ["at_most_once_attempt", "at_least_once_attempt", "effectively_once_with_idempotency", "transactionally_once_in_named_boundary", "best_effort"], "semantic_closure", "forbidden", None, ["Exactly-once is forbidden without a named atomic boundary and proof."], ["Determines retry, idempotency and receipt obligations."], ["contract.runtime-resource.execution-contract.v1"], ["evidence.temporal-docs"]),
    ("artifact-format", "executable-artifact", "Which executable artifact and ABI contract is bound?", ["native_process", "oci_bundle", "wasm_module", "wasm_component", "device_binary", "jit_ir"], "physical_binding", "forbidden", None, ["Artifact format must be compatible with target profile and entry point."], ["Selects loader/backend and supply-chain evidence."], ["contract.runtime-resource.executable-artifact.v1"], ["evidence.oci-runtime", "evidence.wasm-core", "evidence.sycl-2020"]),
    ("blocking-boundary", "async-runtime", "How may blocking work execute within an async runtime?", ["forbidden", "dedicated_blocking_pool", "external_process", "runtime_native_nonblocking"], "physical_binding", "forbidden", None, ["Main cooperative executor cannot be blocked by undeclared operations."], ["Changes worker pool and capacity demand."], ["contract.runtime-resource.async-runtime.v1"], ["evidence.tokio-task"]),
    ("cancellation-mode", "cancellation-deadline", "What stop behavior applies when cancellation is requested?", ["cooperative", "graceful_then_force", "checkpoint_then_stop", "immediate_interrupt", "non_cancellable_commit_region"], "logical_planning", "forbidden", None, ["Non-cancellable regions must be bounded and evidenced."], ["Determines cleanup, deadline and compensation behavior."], ["contract.runtime-resource.cancellation-deadline.v1"], ["evidence.grpc-deadline", "evidence.temporal-timeouts"]),
    ("timeout-scope", "cancellation-deadline", "Which phase does a timeout bound?", ["queue_wait", "reservation", "startup", "attempt_run", "idle", "heartbeat", "drain", "end_to_end"], "analytical_design", "forbidden", None, ["One timeout cannot silently stand for all phases."], ["Determines clocks, state transitions and refusal causes."], ["contract.runtime-resource.cancellation-deadline.v1"], ["evidence.temporal-timeouts"]),
    ("backpressure-mode", "backpressure", "How does downstream capacity constrain upstream work?", ["demand_credit", "bounded_queue_block", "bounded_queue_reject", "drop_oldest", "drop_newest", "sample", "load_shed_by_priority"], "logical_planning", "forbidden", None, ["Lossy modes require loss approval and receipts."], ["Determines buffer resource demand and outcome catalog."], ["contract.runtime-resource.backpressure.v1"], ["evidence.reactive-streams"]),
    ("buffer-bound", "backpressure", "What finite bound applies to pending work or bytes?", ["count_bound", "byte_bound", "time_bound", "compound_bound"], "logical_planning", "forbidden", None, ["Bound magnitude and overflow policy are separate required decisions."], ["Controls overload behavior and capacity requirements."], ["contract.runtime-resource.backpressure.v1"], ["evidence.reactive-streams", "evidence.dask-worker-state"]),
    ("retry-policy", "attempt-control", "When may a new attempt be created?", ["never", "typed_transient_failures", "preemption_only", "lost_worker_only", "all_nonterminal_side_effect_safe_failures"], "logical_planning", "forbidden", None, ["Retry requires attempt budget and side-effect/idempotency proof."], ["Creates new AttemptIds and cost/time demand."], ["contract.runtime-resource.attempt-control.v1"], ["evidence.k8s-job", "evidence.temporal-timeouts"]),
    ("checkpoint-policy", "checkpoint-recovery", "When is execution state checkpointed?", ["none", "periodic", "before_preemption", "on_demand", "phase_boundary", "adaptive"], "physical_binding", "explicit_safe_constant", "none", ["Checkpoint compatibility, overhead and retention must close."], ["Changes storage, I/O, preemption and recovery requirements."], ["contract.runtime-resource.checkpoint-recovery.v1"], ["evidence.criu"]),
    ("resource-hardness", "resource-demand", "How are each demand dimension's minimum, target and maximum enforced?", ["hard_min_hard_max", "hard_min_elastic_max", "best_effort", "burstable", "exclusive"], "observation_planning", "forbidden", None, ["Applied per resource dimension; global label is insufficient."], ["Determines admission and overcommit compatibility."], ["contract.runtime-resource.resource-demand.v1"], ["evidence.k8s-resources"]),
    ("overcommit-policy", "resource-offer", "May offered capacity be overcommitted?", ["forbidden", "cpu_weighted", "memory_with_reclaim", "storage_thin", "provider_declared_other"], "deployment_binding", "forbidden", None, ["Each allowed mode names enforcement, pressure and terminal failure behavior."], ["Changes feasibility and failure model."], ["contract.runtime-resource.resource-offer.v1"], ["evidence.linux-cgroup-v2", "evidence.k8s-resources"]),
    ("topology-hardness", "placement", "Are locality/spread relations required or preferred?", ["required", "preferred", "unconstrained", "role_indexed_mixed"], "logical_planning", "forbidden", None, ["Role-indexed mixed mode gives each role an explicit value."], ["Changes candidate set and scoring."], ["contract.runtime-resource.placement.v1"], ["evidence.k8s-topology", "evidence.kueue-topology"]),
    ("gang-admission", "admission-control", "Must a group be admitted and reserved all-or-nothing?", ["none", "all_members", "minimum_members", "role_indexed"], "logical_planning", "explicit_safe_constant", "none", ["Minimum-members mode declares progress and shrink semantics."], ["Changes reservation atomicity and deadlock obligations."], ["contract.runtime-resource.admission-control.v1"], ["evidence.ray-placement", "evidence.kueue-concepts"]),
    ("scheduling-objective", "scheduling-policy", "Which governed scheduling objective and precedence are used?", ["fifo", "fair_share", "bin_pack", "spread", "deadline", "min_cost", "min_energy", "min_carbon", "min_makespan", "multi_objective_declared"], "physical_binding", "forbidden", None, ["Multi-objective mode requires weights or lexicographic precedence and sensitivity evidence."], ["Selects policy library, inputs and proof contract."], ["contract.runtime-resource.scheduling-policy.v1"], ["evidence.drf", "evidence.firmament"]),
    ("scheduler-quality", "scheduling-policy", "What solution-quality claim is required from scheduling?", ["optimal_with_proof", "bounded_gap", "feasible", "heuristic_best_at_budget", "probabilistic", "no_quality_claim"], "physical_binding", "forbidden", None, ["Claim must match algorithm receipt and time budget."], ["Controls method/provider eligibility."], ["contract.runtime-resource.scheduling-policy.v1"], ["evidence.firmament", "evidence.sparrow"]),
    ("fairness-law", "scheduling-policy", "Which fairness relation applies across tenants/classes?", ["none", "weighted_max_min", "dominant_resource_fairness", "proportional", "reserved_share_plus_borrow", "custom_with_oracle"], "semantic_closure", "forbidden", None, ["Scope, weights, protected classes and starvation bound are required."], ["Changes ordering and quota-borrowing behavior."], ["contract.runtime-resource.scheduling-policy.v1"], ["evidence.drf", "evidence.kueue-clusterqueue"]),
    ("preemption-mode", "preemption", "How may capacity be reclaimed from lower-precedence work?", ["forbidden", "suspend", "checkpoint_requeue", "graceful_terminate", "immediate_terminate", "provider_interruptible"], "physical_binding", "forbidden", None, ["Victim protection, grace and outcome mapping are explicit."], ["Changes checkpoint, cleanup and attempt policies."], ["contract.runtime-resource.preemption.v1"], ["evidence.k8s-preemption", "evidence.slurm-qos"]),
    ("autoscaling-signal", "autoscaling", "Which evidence drives scaling?", ["utilization", "queue_depth", "arrival_rate", "latency", "custom_sli", "schedule_infeasibility", "composite"], "deployment_binding", "forbidden", None, ["Signal freshness, lag and missing-data behavior are required."], ["Selects observation requirements and control law."], ["contract.runtime-resource.autoscaling.v1"], ["evidence.k8s-hpa", "evidence.k8s-node-autoscaling"]),
    ("autoscaling-axis", "autoscaling", "What changes when the system scales?", ["replica_count", "per_occurrence_resource", "worker_count", "node_capacity", "device_capacity", "multi_axis"], "deployment_binding", "forbidden", None, ["Multi-axis controllers declare precedence and loop interaction."], ["Changes provider and runtime bindings."], ["contract.runtime-resource.autoscaling.v1"], ["evidence.k8s-hpa", "evidence.k8s-resize", "evidence.k8s-node-autoscaling"]),
    ("scaling-stabilization", "autoscaling", "Which hysteresis and rate limits prevent unsafe oscillation?", ["fixed_window", "separate_up_down_windows", "rate_limited", "model_predictive", "manual"], "deployment_binding", "forbidden", None, ["Scale-down safety and cooldown are explicit."], ["Controls responsiveness and thrashing risk."], ["contract.runtime-resource.autoscaling.v1"], ["evidence.k8s-hpa"]),
    ("lease-expiry", "lease-fencing", "Which authority and clock determine lease expiry?", ["linearizable_store_ttl", "provider_lease", "runtime_supervisor", "hardware_watchdog"], "deployment_binding", "forbidden", None, ["Local client wall clock cannot unilaterally establish distributed expiry."], ["Determines fencing and failover behavior."], ["contract.runtime-resource.lease-fencing.v1"], ["evidence.etcd-api"]),
    ("fencing-mode", "lease-fencing", "How are stale actors prevented from effecting protected resources?", ["monotonic_token", "compare_revision", "single_writer_epoch", "provider_generation", "unavailable_gap"], "deployment_binding", "forbidden", None, ["Unavailable fencing is a blocking gap for unsafe duplicate-writer domains."], ["Changes provider qualification."], ["contract.runtime-resource.lease-fencing.v1"], ["evidence.etcd-concurrency", "evidence.zookeeper-recipes"]),
    ("failure-domain-level", "failure-domain", "Which correlated failure domains must the plan tolerate?", ["process", "host", "rack", "zone", "region", "provider", "custom_graph_cut"], "assurance_insertion", "forbidden", None, ["Each level names failure mode and independence assumptions."], ["Changes placement, redundancy and cost."], ["contract.runtime-resource.failure-domain.v1"], ["evidence.k8s-topology"]),
    ("degraded-mode", "failure-domain", "What service is permitted when a required failure domain is unavailable?", ["refuse", "read_only", "reduced_capacity", "reduced_durability", "stale_results", "manual_authority"], "assurance_insertion", "forbidden", None, ["Information loss, affected users and recovery path are explicit."], ["Changes SLO and acceptance evidence."], ["contract.runtime-resource.failure-domain.v1"], ["evidence.google-sre"]),
    ("cost-selection", "accounting-cost", "Which cost notion participates in planning?", ["list", "contracted", "effective_amortized", "marginal", "internal_transfer", "multi_scenario"], "physical_binding", "forbidden", None, ["Currency, pricing unit, validity and correction lag are explicit."], ["Changes cost-aware offer ranking."], ["contract.runtime-resource.accounting-cost.v1"], ["evidence.focus-1.2"]),
    ("energy-method", "energy-carbon", "How is energy attributable to a workload?", ["direct_meter", "hardware_counter", "process_attribution_model", "allocation_proportion", "provider_reported", "unavailable"], "evidence_verification", "forbidden", None, ["Model-based modes require model identity, uncertainty and reconciliation."], ["Changes evidence strength and optimization eligibility."], ["contract.runtime-resource.energy-carbon.v1"], ["evidence.kepler", "evidence.sci-spec"]),
    ("carbon-method", "energy-carbon", "Which carbon method is used?", ["location_average", "market_based", "marginal", "provider_reported", "scenario_set"], "evidence_verification", "forbidden", None, ["Temporal/spatial granularity and embodied-carbon treatment are explicit."], ["Changes carbon-aware scheduling objective."], ["contract.runtime-resource.energy-carbon.v1"], ["evidence.sci-iso"]),
    ("isolation-kind", "isolation-runtime", "Which runtime isolation boundary is required?", ["same_process", "process", "container", "microvm", "vm", "wasm_sandbox", "hardware_confidential"], "assurance_insertion", "forbidden", None, ["Threat-model requirements are evaluated separately from mechanism label."], ["Selects backend and affects startup/resource overhead."], ["contract.runtime-resource.isolation-runtime.v1"], ["evidence.oci-runtime", "evidence.firecracker", "evidence.wasm-core"]),
    ("target-portability", "target-profile", "What target portability class is required?", ["single_exact_target", "same_os_arch_family", "oci_portable", "wasi_component", "sycl_backend_portable", "provider_multi_target"], "physical_binding", "forbidden", None, ["Portability requires conformance evidence for every selected target."], ["Controls candidate backend set and artifact matrix."], ["contract.runtime-resource.target-profile.v1"], ["evidence.oci-runtime", "evidence.wasi-02", "evidence.sycl-2020"]),
    ("provider-binding", "provider-occurrence", "When is a concrete provider resource selected?", ["compile_time", "deployment_time", "admission_time", "schedule_time", "runtime_late_binding"], "physical_binding", "forbidden", None, ["Late binding retains all policy/evidence constraints and emits a binding receipt."], ["Determines IR residual choices and adapter obligations."], ["contract.runtime-resource.provider-occurrence.v1"], ["evidence.nist-cloud", "evidence.k8s-dra"]),
    ("receipt-assurance", "runtime-receipt", "What assurance protects runtime receipts?", ["unsigned_attributed", "content_addressed", "signed", "transparency_log", "hardware_attested"], "evidence_verification", "forbidden", None, ["Required strength follows claim and threat model."], ["Controls evidence acceptance and storage."], ["contract.runtime-resource.runtime-receipt.v1"], ["evidence.cloudevents", "evidence.otel-resource"]),
]

DECISIONS = [decision(*spec) for spec in DECISION_SPECS]


def library(
    suffix: str,
    kind: str,
    owner: str | None,
    contexts: list[str],
    effect: str,
    public_types: list[str],
    traits: list[str],
    decisions: list[str],
    laws: list[str],
    resources: list[str],
    forbidden: list[str],
    evidence: list[str],
) -> dict:
    library_id = f"library.runtime-resource.{suffix}"
    return {
        "library_id": library_id,
        "edition": 1,
        "status": "hypothesis",
        "library_kind": kind,
        "semantic_owner_refs": [] if owner is None else [f"context.runtime-resource.{owner}"],
        "contributes_to_context_refs": [f"context.runtime-resource.{c}" for c in contexts],
        "effect_boundary": effect,
        "public_types": public_types,
        "public_traits": traits,
        "operation_refs": [],
        "error_contracts": [f"error-contract.runtime-resource.{suffix}.v1"],
        "decision_refs": [f"decision.runtime-resource.{d}" for d in decisions],
        "requirement_refs": [],
        "offer_refs": [],
        "configuration_contracts": [f"configuration.runtime-resource.{suffix}.v1"],
        "effect_intents": [] if effect == "pure_no_io" else [f"effect-intent.runtime-resource.{suffix}.v1"],
        "runtime_receipts": [] if effect == "pure_no_io" else [f"receipt.runtime-resource.{suffix}.v1"],
        "laws": laws,
        "oracles": [f"oracle.runtime-resource.{suffix}.laws.v1"],
        "resource_contracts": resources,
        "concurrency": ["Public concurrency and Send/Sync/thread-affinity behavior is explicit."],
        "cancellation": ["Every blocking or asynchronous operation declares cancellation safety and completion ambiguity."],
        "unsafe_ffi_generated_policy": ["No unsafe/FFI/generated code unless isolated behind a reviewed target backend with conformance tests."],
        "dependencies": [],
        "targets": ["provider_neutral"],
        "compatibility": ["Semantic edition and wire/schema compatibility are independently versioned."],
        "removal_seams": [f"All calls cross public contract {library_id}.v1; no provider name appears in semantic APIs."],
        "forbidden_responsibilities": forbidden,
        "evidence_refs": evidence,
        "gaps": ["Independent implementation and benchmark evidence pending."],
    }


LIBRARY_SPECS = [
    ("identity-types", "semantic_pure", "execution-contract", ["execution-contract", "attempt-control", "executor-worker"], "pure_no_io", ["WorkUnitId", "JobId", "AttemptId", "WorkerId", "ExecutorId"], ["ScopedIdentity", "IncarnationAwareIdentity"], [], ["IDs are never inferred from provider display names."], [], ["provider discovery", "scheduling"], ["evidence.posix-2024"]),
    ("resource-quantity", "semantic_pure", "resource-demand", ["resource-demand", "resource-offer"], "pure_no_io", ["ResourceClassId", "ResourceQuantity", "ResourceVector"], ["ExactQuantity", "PartialOrder", "UnitNormalize"], ["resource-hardness"], ["Vector comparison is dimension-aware and partial.", "No float quantities."], ["resource-class.*"], ["provider rate lookup", "allocation"], ["evidence.k8s-resources", "evidence.drf"]),
    ("resource-topology", "semantic_pure", "resource-topology", ["resource-topology", "placement", "failure-domain"], "pure_no_io", ["ResourceId", "ResourceTopologyGraph", "FailureDomain"], ["TopologyQuery", "ConstraintPredicate"], ["topology-hardness", "failure-domain-level"], ["Graph editions are immutable.", "Containment, proximity and shared-failure edges stay distinct."], [], ["provider discovery", "scheduling objective"], ["evidence.hwloc", "evidence.k8s-topology"]),
    ("demand-offer-compatibility", "algorithm_pure", None, ["resource-demand", "resource-offer", "admission-control"], "pure_no_io", ["CompatibilityResult", "ResidualGap"], ["DemandOfferMatcher"], ["resource-hardness", "overcommit-policy"], ["Matching proves only declared dimensions and evidence freshness.", "Unknown dimensions return gaps."], ["resource-class.*"], ["provider ranking", "allocation mutation"], ["evidence.k8s-dra"]),
    ("quota-ledger", "semantic_pure", "quota-budget", ["quota-budget", "admission-control"], "pure_effect_intents", ["Quota", "QuotaHold", "QuotaReceipt"], ["QuotaLedger"], [], ["Holds plus committed usage never exceed hard quota.", "Release is idempotent."], [], ["physical capacity", "billing invoice"], ["evidence.k8s-quota", "evidence.kueue-clusterqueue"]),
    ("budget-precharge", "semantic_pure", "quota-budget", ["quota-budget", "accounting-cost"], "pure_effect_intents", ["FiniteBudget", "Precharge", "BudgetReceipt"], ["PrechargeLedger"], ["cost-selection"], ["Hard-budget effects require atomic precharge.", "Refund and commit preserve lineage."], [], ["currency conversion without authority", "provider billing"], ["evidence.focus-1.2"]),
    ("admission", "policy_pure", None, ["admission-control"], "pure_effect_intents", ["AdmissionRequest", "AdmissionDecision"], ["AdmissionPolicy", "AdmissionOracle"], ["gang-admission"], ["Every refusal is typed.", "Admission never claims placement."], ["resource-class.*"], ["resource provisioning", "scheduler dispatch"], ["evidence.kueue-concepts"]),
    ("reservation-ledger", "semantic_pure", "resource-reservation", ["resource-reservation", "resource-pool"], "pure_effect_intents", ["ResourceReservation", "ResourceAllocation", "CapacityLedger"], ["Reserve", "Commit", "Release"], [], ["No double allocation.", "Expired hold cannot commit."], ["resource-class.*"], ["provider provisioning", "lease liveness"], ["evidence.slurm-reservation", "evidence.ray-placement"]),
    ("lease-fencing", "semantic_pure", "lease-fencing", ["lease-fencing"], "pure_effect_intents", ["Lease", "FencingToken", "Heartbeat"], ["LeaseAuthority", "FencedEffect"], ["lease-expiry", "fencing-mode"], ["Fencing token is monotonic within scope.", "Expired lease cannot revive."], [], ["wall-clock-only distributed expiry", "protected effect implementation"], ["evidence.etcd-api", "evidence.etcd-concurrency"]),
    ("placement-constraints", "semantic_pure", "placement", ["placement", "resource-topology"], "pure_no_io", ["PlacementConstraint", "CandidateSet", "PlacementAssignment"], ["ConstraintEvaluator", "PlacementScorer"], ["topology-hardness"], ["Hard constraints filter before scoring.", "Assignment retains input editions."], ["resource-class.*"], ["scheduler policy", "provider selection"], ["evidence.k8s-scheduling"]),
    ("scheduler-policy-spi", "semantic_pure", "scheduling-policy", ["scheduling-policy", "placement"], "pure_no_io", ["SchedulerProblem", "SchedulerResult", "SchedulerQualityReceipt"], ["SchedulerPolicy", "ScheduleOracle"], ["scheduling-objective", "scheduler-quality", "fairness-law"], ["Result states feasible, infeasible, timeout-with-incumbent, timeout-without-incumbent or failed.", "Quality claim is explicit."], ["resource-class.*"], ["cluster state mutation", "provider calls"], ["evidence.firmament", "evidence.sparrow"]),
    ("scheduler-fifo", "algorithm_pure", None, ["scheduling-policy"], "pure_no_io", ["FifoPolicy"], ["SchedulerPolicy"], ["scheduling-objective"], ["Stable eligible ordering under declared tie-break."], [], ["capacity mutation", "global fairness claim"], ["evidence.posix-2024"]),
    ("scheduler-drf", "algorithm_pure", None, ["scheduling-policy"], "pure_no_io", ["DrfPolicy"], ["SchedulerPolicy"], ["fairness-law"], ["DRF properties hold only under encoded model assumptions."], ["resource-class.*"], ["topology invention", "provider calls"], ["evidence.drf"]),
    ("scheduler-binpack", "algorithm_pure", None, ["scheduling-policy"], "pure_no_io", ["BinPackPolicy"], ["SchedulerPolicy"], ["scheduling-objective", "scheduler-quality"], ["Never claims optimality without attached proof/bound."], ["resource-class.*"], ["hard-constraint relaxation"], ["evidence.k8s-binpacking"]),
    ("scheduler-min-cost-flow", "algorithm_pure", None, ["scheduling-policy"], "pure_no_io", ["MinCostFlowPolicy"], ["SchedulerPolicy"], ["scheduling-objective", "scheduler-quality"], ["Optimality is scoped to encoded flow problem and solver result."], ["resource-class.*"], ["cost-model ownership", "provider calls"], ["evidence.firmament"]),
    ("scheduler-gang", "algorithm_pure", None, ["scheduling-policy", "resource-reservation"], "pure_effect_intents", ["GangPolicy", "BundleSet"], ["SchedulerPolicy"], ["gang-admission"], ["No member starts before group reservation condition is met."], ["resource-class.*"], ["worker launch", "provider calls"], ["evidence.ray-placement", "evidence.kueue-topology"]),
    ("preemption-policy", "policy_pure", None, ["preemption"], "pure_effect_intents", ["PreemptionPolicy", "VictimSet", "PreemptionPlan"], ["VictimSelector", "DisruptionOracle"], ["preemption-mode"], ["Protected constraints are never violated for score.", "Preemption receipt names victims and reclaimed capacity."], ["resource-class.*"], ["force termination mechanism"], ["evidence.k8s-preemption", "evidence.slurm-qos"]),
    ("autoscaling-control", "policy_pure", None, ["autoscaling"], "pure_effect_intents", ["ScaleSignal", "ScaleRecommendation", "ScalePlan"], ["ScalingLaw", "StabilityOracle"], ["autoscaling-signal", "autoscaling-axis", "scaling-stabilization"], ["Scale plan is bounded and rate-limited.", "Recommendation is not realized capacity."], ["resource-class.*"], ["provider provisioning", "metric collection"], ["evidence.k8s-hpa", "evidence.k8s-node-autoscaling"]),
    ("backpressure", "semantic_pure", "backpressure", ["backpressure"], "pure_effect_intents", ["BackpressureSignal", "BufferBound", "OverflowOutcome"], ["DemandPublisher", "DemandSubscriber"], ["backpressure-mode", "buffer-bound"], ["Demand is non-negative and bounded.", "Loss is explicit."], ["resource-class.worker-slot"], ["unbounded queue", "autoscaling"], ["evidence.reactive-streams"]),
    ("deadline-cancellation", "semantic_pure", "cancellation-deadline", ["cancellation-deadline", "attempt-control"], "pure_effect_intents", ["Deadline", "CancellationRequest", "CancellationReceipt"], ["CancellationSource", "CancellationListener"], ["cancellation-mode", "timeout-scope"], ["Request, acknowledgement and completion are separate."], ["resource-class.wall-clock-budget"], ["business expiry", "OS force mechanism"], ["evidence.grpc-deadline", "evidence.temporal-timeouts"]),
    ("attempt-state", "semantic_pure", "attempt-control", ["attempt-control"], "pure_effect_intents", ["AttemptId", "AttemptState", "AttemptOutcome"], ["AttemptAggregate"], ["retry-policy"], ["Each retry is a new identity.", "Exactly one terminal outcome unless an explicit ambiguity record exists."], ["resource-class.attempt-budget"], ["work execution backend"], ["evidence.k8s-job", "evidence.slurm-job-state"]),
    ("checkpoint-contract", "semantic_pure", "checkpoint-recovery", ["checkpoint-recovery"], "pure_effect_intents", ["CheckpointRef", "CompatibilityResult", "RestorePlan"], ["CheckpointCodec", "CheckpointOracle"], ["checkpoint-policy"], ["Integrity and compatibility are independently checked.", "Restore creates a new attempt."], ["resource-class.storage-throughput"], ["storage provider", "runtime memory capture"], ["evidence.criu"]),
    ("process-backend", "runtime_mechanism", None, ["process-runtime", "attempt-control"], "effectful_runtime", ["ProcessSpec", "ProcessHandle", "ExitReceipt"], ["ProcessRuntime"], ["execution-model", "cancellation-mode"], ["PID reuse safe identity.", "Exit and signal cause preserved."], ["resource-class.process-slot", "resource-class.file-descriptor"], ["business retry policy", "container orchestration"], ["evidence.posix-spawn"]),
    ("async-executor", "runtime_mechanism", None, ["async-runtime", "executor-worker"], "effectful_runtime", ["AsyncTaskSpec", "TaskHandle"], ["AsyncExecutor"], ["blocking-boundary", "cancellation-mode"], ["Blocking effects cross declared boundary.", "Cancellation safety is explicit."], ["resource-class.worker-slot", "resource-class.cpu-time"], ["business timeout policy"], ["evidence.rust-future", "evidence.tokio-task"]),
    ("actor-runtime-spi", "runtime_mechanism", None, ["actor-runtime"], "effectful_runtime", ["ActorSpec", "ActorHandle", "MailboxSpec"], ["ActorRuntime"], ["execution-model", "backpressure-mode"], ["Mailbox order scope and restart identity are explicit."], ["resource-class.worker-slot", "resource-class.memory-capacity"], ["business aggregate semantics", "message broker ownership"], ["evidence.erlang-supervision", "evidence.ray-actors"]),
    ("device-runtime-spi", "runtime_mechanism", None, ["device-runtime", "executable-artifact"], "ffi_boundary", ["Device", "DeviceContext", "CommandQueue", "KernelHandle", "DeviceEvent"], ["DeviceRuntime"], ["artifact-format", "target-portability"], ["Capability query precedes use.", "Context and memory accessibility are enforced."], ["resource-class.gpu-device-exclusive", "resource-class.accelerator-device"], ["kernel algorithm", "cluster scheduling"], ["evidence.sycl-2020", "evidence.opencl-3"]),
    ("container-runtime-adapter", "target_backend", None, ["isolation-runtime", "target-profile"], "effectful_runtime", ["ContainerBundle", "ContainerHandle"], ["IsolationBackend", "TargetBackend"], ["isolation-kind", "artifact-format"], ["OCI lifecycle and configuration conformance is evidenced."], ["resource-class.cpu-time", "resource-class.memory-capacity"], ["image build", "cluster scheduling", "security guarantee invention"], ["evidence.oci-runtime"]),
    ("wasm-runtime-adapter", "target_backend", None, ["isolation-runtime", "target-profile", "executable-artifact"], "effectful_runtime", ["WasmComponent", "WitWorld", "WasiCapability"], ["IsolationBackend", "TargetBackend"], ["isolation-kind", "artifact-format", "target-portability"], ["Imported effects are capability-explicit.", "Component ABI edition is exact."], ["resource-class.cpu-time", "resource-class.memory-capacity"], ["ambient host access", "business semantics"], ["evidence.wasm-core", "evidence.wasi-02", "evidence.wasm-component"]),
    ("provider-adapter-spi", "provider_adapter", None, ["provider-occurrence", "resource-offer", "control-reconciliation"], "effectful_runtime", ["ProviderOffer", "ProviderOccurrence", "ProviderReceipt"], ["ProviderAdapter"], ["provider-binding"], ["Provider objects translate through an ACL.", "No provider enum in semantic types."], ["resource-class.*"], ["semantic ownership", "scheduler policy"], ["evidence.nist-cloud", "evidence.redfish"]),
    ("usage-accounting", "semantic_pure", "accounting-cost", ["accounting-cost", "runtime-receipt"], "pure_effect_intents", ["ResourceUsageReceipt", "CostRate", "CostReceipt"], ["UsageReconciler", "CostAllocator"], ["cost-selection"], ["Requested, allocated, used and billed remain separate.", "Corrections preserve lineage."], ["resource-class.*"], ["provider invoice authority", "currency guessing"], ["evidence.focus-1.2", "evidence.opencost"]),
    ("energy-accounting", "semantic_pure", "energy-carbon", ["energy-carbon"], "pure_effect_intents", ["PowerEnvelope", "EnergyReceipt", "CarbonReceipt"], ["EnergyAttributor", "CarbonMethod"], ["energy-method", "carbon-method"], ["Power, energy and carbon are dimensionally distinct.", "Model estimates retain uncertainty."], ["resource-class.power-limit", "resource-class.energy-budget", "resource-class.carbon-budget"], ["electricity market authority", "hidden attribution model"], ["evidence.sci-iso", "evidence.kepler"]),
    ("runtime-receipts", "semantic_pure", "runtime-receipt", ["runtime-receipt", "observability"], "pure_effect_intents", ["RuntimeReceipt", "ReceiptChain", "EvidenceScope"], ["ReceiptEmitter", "ReceiptVerifier"], ["receipt-assurance"], ["Append-only causal chain.", "Evidence scope never widens silently."], [], ["raw telemetry storage", "business verdict"], ["evidence.cloudevents", "evidence.otel-resource"]),
    ("conformance-oracles", "test_oracle", None, ["target-profile", "resource-offer", "runtime-receipt"], "pure_no_io", ["ConformanceClaim", "ProofResult"], ["TargetOracle", "OfferOracle", "LifecycleOracle"], [], ["A passing oracle proves only exact edition, target and tested scope."], [], ["production provider selection", "broad certification claim"], ["evidence.oci-conformance", "evidence.wasm-spec-tests"]),
]

LIBRARIES = [library(*spec) for spec in LIBRARY_SPECS]


COMPILER_CONTRACT = {
    "contract_id": "contract.runtime-resource.compiler-closure.v1",
    "edition": EDITION,
    "status": "active_research_contract",
    "scope": "Provider-neutral lowering from semantically closed executable work to finite runtime/resource plans and evidence; no query, business, storage-data or provider-product semantics.",
    "separation_invariants": [
        "semantic intent states what work means; runtime mechanism states how work executes",
        "resource class is not a resource occurrence, offer, quota, reservation, allocation or usage observation",
        "scheduler policy is not scheduler implementation or control-plane product",
        "target profile is not provider SKU or deployment occurrence",
        "a compute kernel is an executable entry point and is not an operating-system kernel",
        "requested, reserved, allocated, observed, rated and billed quantities remain separately typed",
        "logical completion and physical attempt outcome remain separately identified",
        "unknown resource dimensions, guarantees or effect semantics become typed gaps",
    ],
    "required_input_contracts": [
        "closed execution contract and immutable artifact reference",
        "work graph with explicit dependencies and side-effect regions",
        "minimum/target/maximum resource vectors",
        "hard and soft topology constraints",
        "completion, retry, timeout, cancellation and checkpoint semantics",
        "admission authority, quotas and finite budgets",
        "SLO, failure-domain and degraded-mode requirements",
        "cost, energy and carbon objectives only when their measurement methods close",
    ],
    "ir_stages": [
        {"stage": "runtime-ir.execution", "owns": ["work/job/attempt identities", "artifact and entry point", "effect envelope", "completion contract"], "exit_proofs": ["artifact identity exact", "effects closed", "attempt semantics total"]},
        {"stage": "runtime-ir.demand", "owns": ["resource dimensions", "minimum/target/maximum", "elasticity", "topology constraints"], "exit_proofs": ["units canonical", "all blocking dimensions finite", "hardness explicit"]},
        {"stage": "runtime-ir.assurance", "owns": ["isolation", "failure domains", "deadlines", "budgets", "SLOs"], "exit_proofs": ["authority resolved", "degraded/refusal paths total", "evidence gates attached"]},
        {"stage": "runtime-ir.feasibility", "owns": ["admission", "quota/precharge holds", "coarse capacity feasibility"], "exit_proofs": ["admission receipt", "budget hold", "no aggregate-capacity fallacy"]},
        {"stage": "runtime-ir.policy", "owns": ["eligible set", "scheduler policy", "quality contract", "preemption/autoscaling law"], "exit_proofs": ["policy owner and edition exact", "heuristic guarantee honest", "tie-break deterministic or explicitly nondeterministic"]},
        {"stage": "runtime-ir.physical", "owns": ["qualified offers", "target/backend", "placement", "reservation/allocation", "provider adapter"], "exit_proofs": ["hard constraints pass", "offer evidence fresh", "target conformance pass", "capacity reserved"]},
        {"stage": "runtime-ir.deployment", "owns": ["provider occurrences", "leases/fences", "worker/executor configuration", "reconciliation"], "exit_proofs": ["occurrence identities fixed", "fencing closes", "startup/health paths total"]},
        {"stage": "runtime-ir.evidence", "owns": ["attempt outcomes", "usage/cost/energy receipts", "SLO evaluation", "residual gaps"], "exit_proofs": ["receipt causal chain complete", "accounting reconciles", "no blocking runtime gap unwaived"]},
    ],
    "requirement_offer_binding_algorithm": [
        "resolve exact semantic owners, editions and target-independent requirements",
        "normalize every resource quantity to its registered dimension without losing qualifiers",
        "reject unbounded demand, unknown dimension or implicit overcommit",
        "evaluate admission, quota and hard-budget precharge independently of physical capacity",
        "enumerate offers structurally compatible with resource, topology, isolation, SLO and target requirements",
        "discard stale, unqualified, prohibited or policy-incompatible offers",
        "select declared scheduling method and retain solver/heuristic quality receipt",
        "atomically reserve then commit capacity; issue allocation, lease and fencing state",
        "lower to backend/provider only through typed adapters and explicit configuration decisions",
        "emit binding and rejected-alternative trace; invalidate on declared evidence, topology, rate, quota, target or health changes",
    ],
    "terminal_compile_results": ["bound", "bound_with_declared_degradation", "refused", "infeasible", "unknown_semantic_gap", "insufficient_evidence", "policy_conflict", "authority_missing"],
    "terminal_schedule_results": ["optimal_with_proof", "bounded_gap", "feasible", "heuristic_best_at_budget", "probabilistic_result", "infeasible", "timeout_with_incumbent", "timeout_without_incumbent", "mechanism_failure"],
    "runtime_receipt_chain": ["intent_accepted", "admission_decided", "budget_precharged", "offer_bound", "capacity_reserved", "allocation_committed", "occurrence_ready", "attempt_started", "checkpoint_or_progress", "attempt_terminal", "allocation_released", "usage_reconciled", "slo_evaluated"],
    "forbidden_shortcuts": [
        "dispatch by cloud vendor, crate, runtime or product name",
        "treat CPU request as observed CPU use",
        "treat quota as capacity",
        "treat a machine type as a resource vector without a qualified translation",
        "claim exactly-once from retry configuration",
        "claim cancellation after request delivery alone",
        "treat heartbeat as useful progress",
        "relax a hard placement constraint to get a result",
        "call a heuristic solution optimal",
        "infer isolation assurance from container/VM/Wasm label",
        "hide provider defaults or rate lookup inside a library",
        "compile an unknown resource dimension as zero",
    ],
}


def req(suffix: str, subject: str, kind: str, contracts: list[str], guarantees: list[str], criticality: str, evidence_gates: list[str], owner: str) -> dict:
    return {
        "record_kind": "capability_requirement",
        "requirement_id": f"requirement.runtime-resource.{suffix}",
        "edition": 1,
        "status": "hypothesis",
        "subject_ref": subject,
        "capability_kind": kind,
        "contract_refs": contracts,
        "operation_refs": [],
        "type_refs": [],
        "required_guarantees": guarantees,
        "applicability": {"when": ["subject is selected by runtime lowering"], "unless": [], "scope_refs": [subject]},
        "cardinality": "exactly_one",
        "binding_phase": "physical_binding",
        "criticality": criticality,
        "selection_laws": ["Select by exact contract, guarantees, target, limits and evidence; never by provider name."],
        "fallback_law": "refuse" if criticality == "blocking" else "typed_degradation",
        "prohibited_traits": ["implicit unbounded resource use", "hidden provider default", "unscoped exactly-once claim"],
        "evidence_gates": evidence_gates,
        "owner_ref": f"context.runtime-resource.{owner}",
        "gaps": [],
    }


REQUIREMENTS = [
    req("target", "intent.runtime-reference.example", "target", ["contract.runtime-resource.target-profile.v1"], ["exact ABI and artifact compatibility", "declared isolation mechanism"], "blocking", ["target conformance receipt for exact edition"], "target-profile"),
    req("runtime", "intent.runtime-reference.example", "runtime_mechanism", ["contract.runtime-resource.execution-contract.v1", "contract.runtime-resource.attempt-control.v1"], ["total attempt lifecycle", "typed cancellation outcome", "append-only receipt"], "blocking", ["two lifecycle conformance suites", "cancellation race tests"], "execution-contract"),
    req("finite-demand", "intent.runtime-reference.example", "resource", ["contract.runtime-resource.resource-demand.v1"], ["minimum target maximum vectors", "finite blocking dimensions"], "blocking", ["unit and partial-order oracle passes"], "resource-demand"),
    req("offer", "intent.runtime-reference.example", "resource", ["contract.runtime-resource.resource-offer.v1"], ["capacity and topology compatible", "valid evidence window", "overcommit semantics explicit"], "blocking", ["fresh inventory and capability probe"], "resource-offer"),
    req("admission", "intent.runtime-reference.example", "policy", ["contract.runtime-resource.admission-control.v1"], ["typed refusal", "quota checked independently", "coarse feasibility"], "blocking", ["admission decision receipt"], "admission-control"),
    req("scheduler", "intent.runtime-reference.example", "runtime_mechanism", ["contract.runtime-resource.scheduling-policy.v1"], ["hard constraints preserved", "declared quality result", "decision trace"], "blocking", ["policy law oracle", "adversarial infeasibility cases"], "scheduling-policy"),
    req("reservation", "intent.runtime-reference.example", "runtime_mechanism", ["contract.runtime-resource.resource-reservation.v1"], ["no double allocation", "idempotent release", "hold expiry"], "blocking", ["linearizability/model test", "capacity reconciliation"], "resource-reservation"),
    req("fencing", "intent.runtime-reference.example", "runtime_mechanism", ["contract.runtime-resource.lease-fencing.v1"], ["stale actor rejected", "authority-scoped lease expiry"], "blocking", ["partition and delayed-writer adversarial test"], "lease-fencing"),
    req("backpressure", "intent.runtime-reference.example", "runtime_mechanism", ["contract.runtime-resource.backpressure.v1"], ["finite buffer", "typed overload outcomes"], "blocking", ["overload and cancellation tests"], "backpressure"),
    req("failure", "intent.runtime-reference.example", "assurance", ["contract.runtime-resource.failure-domain.v1"], ["named tolerated failure domains", "degraded/refusal behavior"], "blocking", ["fault-injection receipts"], "failure-domain"),
    req("accounting", "intent.runtime-reference.example", "evidence", ["contract.runtime-resource.accounting-cost.v1"], ["requested reserved allocated used billed separated", "correction lineage"], "degradable", ["allocation-to-usage reconciliation"], "accounting-cost"),
    req("runtime-receipt", "intent.runtime-reference.example", "evidence", ["contract.runtime-resource.runtime-receipt.v1"], ["causal append-only receipt chain", "issuer and scope"], "blocking", ["receipt schema and chain verification"], "runtime-receipt"),
]


def offer(suffix: str, provider: str, kind: str, contracts: list[str], guarantees: list[str], decisions: list[str], targets: list[str], evidence: list[str], limits: list[str], exclusions: list[str]) -> dict:
    return {
        "record_kind": "capability_offer",
        "offer_id": f"offer.runtime-resource.{suffix}",
        "edition": 1,
        "status": "declared",
        "provider_ref": provider,
        "capability_kind": kind,
        "contract_refs": contracts,
        "operation_refs": [],
        "type_refs": [],
        "guarantees": guarantees,
        "limits": limits,
        "decision_refs": [f"decision.runtime-resource.{d}" for d in decisions],
        "target_refs": targets,
        "applicability": {"when": ["exact target and requirement editions match"], "unless": ["evidence expired"], "scope_refs": [provider]},
        "exclusions": exclusions,
        "conformance_receipts": [],
        "evidence_refs": evidence,
        "validity": {"from": None, "until": None, "recheck_triggers": ["provider/version change", "target change", "conformance failure", "evidence expiry"]},
        "gaps": ["Reference offer is illustrative and not provider-qualified."],
    }


OFFERS = [
    offer("posix-process", "provider.reference.posix-process", "runtime_mechanism", ["contract.runtime-resource.execution-contract.v1", "contract.runtime-resource.process-runtime.v1"], ["process spawn wait and typed exit", "signal-based force termination"], ["execution-model", "cancellation-mode"], ["target.reference.posix"], ["evidence.posix-2024", "evidence.posix-spawn"], ["no distributed failure guarantee", "platform-specific limits probed at deployment"], ["actor supervision", "device kernel dispatch"]),
    offer("oci-isolation", "provider.reference.oci-runtime", "target", ["contract.runtime-resource.isolation-runtime.v1", "contract.runtime-resource.target-profile.v1"], ["OCI lifecycle/configuration surface for exact runtime-spec edition"], ["isolation-kind", "artifact-format"], ["target.reference.oci"], ["evidence.oci-runtime"], ["security assurance requires separate threat-model proof"], ["cluster scheduler", "image build"]),
    offer("wasi-component", "provider.reference.wasi-component", "target", ["contract.runtime-resource.isolation-runtime.v1", "contract.runtime-resource.target-profile.v1"], ["typed component imports and WASI capability surface"], ["isolation-kind", "artifact-format", "target-portability"], ["target.reference.wasi02"], ["evidence.wasi-02", "evidence.wasm-component"], ["host effects limited to imported interfaces", "runtime conformance must be probed"], ["POSIX process parity", "ambient host access"]),
    offer("multiresource-scheduler", "provider.reference.scheduler-library", "runtime_mechanism", ["contract.runtime-resource.scheduling-policy.v1"], ["hard-constraint preservation", "explicit feasible/infeasible/timeout result", "quality receipt"], ["scheduling-objective", "scheduler-quality", "fairness-law"], ["target.reference.provider-neutral"], ["evidence.drf", "evidence.firmament"], ["model scale and solve-time budget declared per invocation"], ["capacity mutation", "provider provisioning"]),
    offer("lease-store", "provider.reference.linearizable-lease-store", "runtime_mechanism", ["contract.runtime-resource.lease-fencing.v1"], ["authority TTL", "monotonic revision/fencing input", "transactional compare"], ["lease-expiry", "fencing-mode"], ["target.reference.distributed-store"], ["evidence.etcd-api", "evidence.etcd-concurrency"], ["availability and partition behavior target-specific"], ["protected resource enforcement"]),
    offer("resource-observability", "provider.reference.otel", "evidence", ["contract.runtime-resource.observability.v1", "contract.runtime-resource.runtime-receipt.v1"], ["observed entity resource identity", "standard process/system attributes"], ["receipt-assurance"], ["target.reference.otel"], ["evidence.otel-resource", "evidence.opentelemetry-system"], ["semantic convention stability varies by attribute group"], ["SLO policy", "billing authority"]),
]


BINDINGS = [
    {
        "record_kind": "capability_binding", "binding_id": "binding.runtime-resource.reference-runtime", "edition": 1, "status": "candidate",
        "requirement_ref": "requirement.runtime-resource.runtime", "offer_refs": ["offer.runtime-resource.posix-process"], "binding_phase": "physical_binding",
        "cardinality_proof": "One illustrative runtime offer selected for one reference target; no production qualification claim.",
        "configuration": {"execution_model": "process", "completion_guarantee": "at_most_once_attempt"}, "adapter_refs": [],
        "proof_results": [{"proof_ref": "proof.runtime-resource.lifecycle-totality", "result": "inconclusive", "evidence_refs": ["evidence.posix-2024"]}],
        "evidence_refs": ["evidence.posix-2024"], "residual_gaps": ["gap.runtime-resource.reference-conformance"],
        "validity": {"from": None, "until": None, "invalidation_triggers": ["target change", "runtime edition change", "conformance evidence added or failed"]},
    },
    {
        "record_kind": "capability_binding", "binding_id": "binding.runtime-resource.reference-scheduler", "edition": 1, "status": "candidate",
        "requirement_ref": "requirement.runtime-resource.scheduler", "offer_refs": ["offer.runtime-resource.multiresource-scheduler"], "binding_phase": "physical_binding",
        "cardinality_proof": "One policy-SPI offer; algorithm policy remains a separately bound decision.",
        "configuration": {"objective": "multi_objective_declared", "quality": "heuristic_best_at_budget"}, "adapter_refs": [],
        "proof_results": [{"proof_ref": "proof.runtime-resource.hard-constraints", "result": "inconclusive", "evidence_refs": ["evidence.firmament"]}],
        "evidence_refs": ["evidence.firmament"], "residual_gaps": ["gap.runtime-resource.scheduler-scale"],
        "validity": {"from": None, "until": None, "invalidation_triggers": ["policy edition change", "resource dimension change", "solve budget change"]},
    },
]


def gap(suffix: str, subject: str, kind: str, blocking: bool, missing: list[str], resolution: str) -> dict:
    return {
        "record_kind": "compiler_gap", "gap_id": f"gap.runtime-resource.{suffix}", "edition": 1, "status": "open",
        "subject_ref": subject, "gap_kind": kind, "blocking": blocking, "missing_contracts": missing,
        "attempted_bindings": [], "observed_evidence": [], "owner_ref": "context.runtime-resource.control-reconciliation",
        "resolution_condition": resolution,
        "prohibited_fallbacks": ["guess a provider default", "coerce unknown to zero", "weaken a hard constraint", "claim a stronger guarantee"],
    }


GAPS = [
    gap("reference-conformance", "binding.runtime-resource.reference-runtime", "evidence_insufficient", True, ["contract.runtime-resource.process-runtime.v1"], "Two independent runtime implementations pass lifecycle, cancellation and resource-limit conformance on an exact target profile."),
    gap("scheduler-scale", "binding.runtime-resource.reference-scheduler", "evidence_insufficient", True, ["contract.runtime-resource.scheduling-policy.v1"], "Policy implementation passes adversarial feasibility and scale/latency gates for the declared problem envelope."),
    gap("unknown-resource", "intent.runtime-reference.example", "missing_type", True, ["contract.runtime-resource.resource-demand.v1"], "Every demand dimension resolves to a registered ResourceClass edition and qualified offer translation."),
    gap("fencing-enforcement", "requirement.runtime-resource.fencing", "missing_offer", True, ["contract.runtime-resource.lease-fencing.v1"], "Protected effect provider accepts and atomically enforces the selected fencing token."),
    gap("cancellation-race", "requirement.runtime-resource.runtime", "unsatisfied_law", True, ["contract.runtime-resource.cancellation-deadline.v1"], "Runtime proves outcome precedence for completion racing cancellation, timeout and force termination."),
    gap("device-partition-isolation", "requirement.runtime-resource.offer", "unqualified_provider", True, ["contract.runtime-resource.resource-offer.v1"], "Device driver proves partition capacity, sharing, reset blast radius and health behavior for exact firmware/driver editions."),
    gap("energy-attribution", "intent.runtime-reference.example", "evidence_insufficient", False, ["contract.runtime-resource.energy-carbon.v1"], "Attribution model is calibrated and reconciled against direct measurement with uncertainty bounds."),
    gap("provider-rate-staleness", "requirement.runtime-resource.accounting", "evidence_insufficient", False, ["contract.runtime-resource.accounting-cost.v1"], "Rate source publishes validity, correction and refresh evidence sufficient for planning horizon."),
    gap("checkpoint-portability", "intent.runtime-reference.example", "target_unsupported", False, ["contract.runtime-resource.checkpoint-recovery.v1"], "Checkpoint compatibility matrix passes restore tests across every selected target transition."),
    gap("correlated-failure", "requirement.runtime-resource.failure", "unsatisfied_law", True, ["contract.runtime-resource.failure-domain.v1"], "Topology/failure evidence establishes the independence assumptions used by redundancy placement."),
    gap("finite-buffer", "requirement.runtime-resource.backpressure", "missing_decision", True, ["contract.runtime-resource.backpressure.v1"], "Buffer bound and overflow outcome are supplied for every queue/channel."),
    gap("product-boundary", "context.runtime-resource.control-plane-product", "ambiguous_owner", False, ["contract.runtime-resource.control-plane-product.v1"], "Product adjudication proves user outcome, operating obligation and packaging boundary without stealing semantic ownership."),
]


def ev(suffix: str, title: str, publisher: str, kind: str, url: str, claims: list[str], limits: list[str], published: str | None = None) -> dict:
    return {
        "record_kind": "evidence_source",
        "evidence_id": f"evidence.{suffix}",
        "title": title,
        "publisher": publisher,
        "source_kind": kind,
        "url": url,
        "publication_date": published,
        "accessed_at": "2026-08-25",
        "primary_authority": True,
        "claims_supported": claims,
        "scope_limitations": limits,
    }


EVIDENCE = [
    ev("posix-2024", "The Open Group Base Specifications Issue 8, IEEE Std 1003.1-2024: General Information", "IEEE and The Open Group", "standard", "https://pubs.opengroup.org/onlinepubs/9799919799/functions/V2_chap02.html", ["process/thread model", "scheduling policies and priorities", "cancellation and asynchronous I/O foundations"], ["Conceptual portable interface; does not specify provider or cluster scheduler behavior."], "2024"),
    ev("posix-spawn", "posix_spawn", "IEEE and The Open Group", "standard", "https://pubs.opengroup.org/onlinepubs/9799919799/functions/posix_spawn.html", ["process creation attributes and failure surface"], ["POSIX targets only."], "2024"),
    ev("rust-thread", "std::thread", "Rust Project", "official_documentation", "https://doc.rust-lang.org/std/thread/", ["Rust native-thread lifecycle and join model"], ["Language/library contract; not distributed scheduling." ]),
    ev("rust-future", "std::future::Future", "Rust Project", "official_documentation", "https://doc.rust-lang.org/std/future/trait.Future.html", ["poll/wake future contract"], ["Does not define an executor or external-effect cancellation." ]),
    ev("tokio-task", "Tokio task module", "Tokio Project", "official_documentation", "https://docs.rs/tokio/latest/tokio/task/", ["cooperative async tasks, spawning and blocking boundary"], ["Tokio implementation, not universal async semantics." ]),
    ev("tokio-cancellation", "Graceful Shutdown", "Tokio Project", "official_documentation", "https://tokio.rs/tokio/topics/shutdown", ["cancellation-token and task-shutdown patterns"], ["Application patterns; force-termination semantics are outside scope." ]),
    ev("grpc-deadline", "Deadlines", "gRPC Project", "official_documentation", "https://grpc.io/docs/guides/deadlines/", ["deadline propagation and cancellation after expiry"], ["RPC-scoped; does not prove remote side effects stopped." ]),
    ev("grpc-flow", "Flow Control", "gRPC Project", "official_documentation", "https://grpc.io/docs/guides/flow-control/", ["stream flow-control behavior"], ["Transport/API-specific, not a whole-platform overload contract." ]),
    ev("reactive-streams", "Reactive Streams Specification", "Reactive Streams", "standard", "https://www.reactive-streams.org/", ["asynchronous streams with non-blocking backpressure"], ["Interface-level contract; buffering and workload policy still require decisions." ]),
    ev("erlang-supervision", "OTP Design Principles: Supervisor Behaviour", "Erlang/OTP", "official_documentation", "https://www.erlang.org/doc/system/sup_princ.html", ["supervision trees and restart strategies"], ["Erlang/OTP semantics; actor identity mapping remains implementation-specific." ]),
    ev("linux-cgroup-v2", "Control Group v2", "Linux Kernel Project", "official_documentation", "https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html", ["hierarchical CPU, memory, I/O and process resource control"], ["Linux-specific mechanisms; not a provider-neutral resource contract." ]),
    ev("linux-namespaces", "namespaces(7)", "Linux man-pages project", "official_documentation", "https://man7.org/linux/man-pages/man7/namespaces.7.html", ["Linux namespace isolation mechanisms"], ["Mechanism does not alone prove a security threat model." ]),
    ev("linux-psi", "PSI - Pressure Stall Information", "Linux Kernel Project", "official_documentation", "https://docs.kernel.org/accounting/psi.html", ["CPU, memory and I/O pressure-stall measurement"], ["Linux-specific observation; pressure is not end-to-end SLO." ]),
    ev("linux-sched-ext", "Extensible Scheduler Class", "Linux Kernel Project", "official_documentation", "https://docs.kernel.org/scheduler/sched-ext.html", ["BPF-defined CPU scheduler policy with fail-safe fallback"], ["Host CPU scheduler only; does not replace cluster scheduling." ]),
    ev("io-uring", "io_uring(7)", "Linux man-pages project", "official_documentation", "https://man7.org/linux/man-pages/man7/io_uring.7.html", ["Linux asynchronous I/O submission/completion rings"], ["Linux-specific and not a data-operation semantic contract." ]),
    ev("linux-damon", "DAMON: Data Access MONitoring and Access-aware System Operations", "Linux Kernel Project", "official_documentation", "https://docs.kernel.org/mm/damon/index.html", ["lightweight scalable access monitoring and access-aware memory operations"], ["Kernel memory mechanism; policy and workload meaning are separate." ]),
    ev("linux-mglru", "Multi-Gen LRU", "Linux Kernel Project", "official_documentation", "https://www.kernel.org/doc/html/v6.1/mm/multigen_lru.html", ["generational page-reclaim model and feedback loop"], ["Page-reclaim implementation, not application memory guarantee." ]),
    ev("hwloc", "Hardware Locality documentation", "Open MPI Project", "official_documentation", "https://www.open-mpi.org/projects/hwloc/doc/", ["portable hardware topology discovery and binding"], ["Observed topology needs freshness and provider identity reconciliation." ]),
    ev("oci-runtime", "OCI Runtime Specification", "Open Container Initiative", "standard", "https://specs.opencontainers.org/runtime-spec/", ["container runtime bundle, configuration and lifecycle contract"], ["Low-level runtime spec; not orchestration or security certification." ]),
    ev("oci-image", "OCI Image Specification", "Open Container Initiative", "standard", "https://specs.opencontainers.org/image-spec/", ["content-addressed image, configuration and platform metadata"], ["Artifact packaging does not define execution scheduling." ]),
    ev("oci-distribution", "OCI Distribution Specification", "Open Container Initiative", "standard", "https://specs.opencontainers.org/distribution-spec/", ["content distribution protocol"], ["Does not define runtime allocation." ]),
    ev("oci-conformance", "OCI-Conformant Products", "Open Container Initiative", "conformance_registry", "https://conformance.opencontainers.org/", ["scope-specific OCI conformance evidence model"], ["Conformance varies by specification and product/version." ]),
    ev("wasm-core", "WebAssembly Core Specification", "W3C WebAssembly Community Group", "standard", "https://www.w3.org/TR/wasm-core/", ["safe portable low-level code format and embedder-controlled effects"], ["Core Wasm does not itself provide system interfaces or resource scheduling." ], "2026-05-12"),
    ev("wasm-component", "WebAssembly Component Model design and specification", "W3C WebAssembly Community Group", "standard_draft", "https://github.com/WebAssembly/component-model", ["typed component interfaces, canonical ABI and resource handles"], ["Incrementally standardized; exact milestone/version must be bound." ]),
    ev("wasi-02", "WASI 0.2", "WASI Subgroup", "standard_release", "https://wasi.dev/releases/wasi-p2", ["WASI rebased on Component Model and WIT"], ["Runtime support and interface versions vary." ], "2024-01"),
    ev("wasm-spec-tests", "WebAssembly specification, reference interpreter and test suite", "W3C WebAssembly Community Group", "conformance_suite", "https://github.com/WebAssembly/spec", ["official reference interpreter and specification tests"], ["Core tests do not prove host/WASI/provider behavior." ]),
    ev("openmp-6", "OpenMP API Specification 6.0", "OpenMP Architecture Review Board", "standard", "https://www.openmp.org/specifications/", ["host parallelism, tasks, synchronization and target offload"], ["Compiler/runtime implementation coverage varies." ], "2024-11"),
    ev("mpi-4.1", "MPI 4.1 Standard", "MPI Forum", "standard", "https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report.pdf", ["distributed process groups, collectives, communication and sessions"], ["Portable failure-tolerance behavior remains limited and implementation-dependent." ], "2023-11-02"),
    ev("sycl-2020", "SYCL 2020 Specification", "Khronos Group", "standard", "https://registry.khronos.org/SYCL/specs/sycl-2020/html/sycl-2020.html", ["heterogeneous device, context, queue, event, kernel and USM model"], ["Optional capabilities and backend interop require target probes." ]),
    ev("opencl-3", "OpenCL 3.0 Specification", "Khronos Group", "standard", "https://registry.khronos.org/OpenCL/specs/3.0-unified/pdf/OpenCL_API.pdf", ["compute devices, contexts, command queues, kernels and memory objects"], ["Optional feature set requires device queries." ]),
    ev("cuda-guide", "CUDA C++ Programming Guide", "NVIDIA", "official_documentation", "https://docs.nvidia.com/cuda/cuda-c-programming-guide/", ["CUDA execution, device, memory and kernel model"], ["Vendor-specific implementation; cannot define provider-neutral semantics." ]),
    ev("k8s-resources", "Resource Management for Pods and Containers", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/", ["requests, limits and their scheduling/enforcement distinction"], ["Kubernetes/Linux behavior; provider target details vary." ]),
    ev("k8s-scheduling", "Scheduling, Preemption and Eviction", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/", ["Kubernetes scheduling constraint and extension surface"], ["Overview does not prove a particular plugin policy." ]),
    ev("k8s-binpacking", "Resource Bin Packing", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/resource-bin-packing/", ["MostAllocated and requested-to-capacity scoring"], ["Heuristic scoring, not global optimality." ]),
    ev("k8s-topology", "Pod Topology Spread Constraints", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/", ["max-skew topology spread constraints"], ["Quality depends on node labels and eligible-domain state." ]),
    ev("k8s-preemption", "Pod Priority and Preemption", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/", ["priority and preemption semantics"], ["Preemption does not guarantee immediate placement." ]),
    ev("k8s-quota", "Resource Quotas", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/policy/resource-quotas/", ["namespace-scoped aggregate resource limits"], ["Quota is not physical capacity or reservation." ]),
    ev("k8s-job", "Jobs", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/workloads/controllers/job/", ["finite task retries, completion and failure policies"], ["External side-effect idempotency remains application-owned." ]),
    ev("k8s-dra", "Dynamic Resource Allocation", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/", ["device classes, claims, slices, allocation, partitioning and consumable capacity"], ["Feature maturity varies by Kubernetes release/feature gate." ]),
    ev("k8s-hpa", "Horizontal Pod Autoscaling", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/", ["feedback autoscaling algorithm, multiple signals and stabilization"], ["Replica scaling only; observed metrics and provider capacity are separate." ]),
    ev("k8s-node-autoscaling", "Node Autoscaling", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/", ["node provisioning/consolidation from scheduling constraints"], ["Implementations and provider integration differ." ]),
    ev("k8s-resize", "Kubernetes v1.35: In-Place Pod Resize Graduates to Stable", "Kubernetes Project", "official_release", "https://kubernetes.io/blog/2025/12/19/kubernetes-v1-35-in-place-pod-resize-ga/", ["mutable CPU/memory requests and limits for running pods"], ["Only supported resource/runtime combinations; not arbitrary live resource rebinding." ], "2025-12-19"),
    ev("k8s-cpu-manager", "Control CPU Management Policies on the Node", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/", ["exclusive CPU assignment and policy behavior"], ["Kubelet/Linux scope." ]),
    ev("k8s-scheduling-readiness", "Pod Scheduling Readiness", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/scheduling-eviction/pod-scheduling-readiness/", ["explicit scheduling gates before scheduler consideration"], ["Gating does not reserve capacity." ]),
    ev("kubernetes-controller", "Controllers", "Kubernetes Project", "official_documentation", "https://kubernetes.io/docs/concepts/architecture/controller/", ["desired/observed state reconciliation control loops"], ["General controller pattern; domain-specific convergence requires separate laws." ]),
    ev("jobset", "JobSet Concepts", "Kubernetes SIG Apps", "official_documentation", "https://jobset.sigs.k8s.io/docs/concepts/", ["coordinated group of jobs with lifecycle and failure policy"], ["API maturity/version must be bound." ]),
    ev("kueue-concepts", "Kueue Concepts", "Kubernetes SIG Scheduling", "official_documentation", "https://kueue.sigs.k8s.io/docs/concepts/", ["workload admission, quota reservation, queues, cohorts, preemption and fair sharing"], ["Admission layer complements but does not replace pod placement." ]),
    ev("kueue-clusterqueue", "Cluster Queue", "Kubernetes SIG Scheduling", "official_documentation", "https://kueue.sigs.k8s.io/docs/concepts/cluster_queue/", ["resource flavors, quotas, borrowing and fair sharing"], ["Kueue-specific policies; exact release required." ]),
    ev("kueue-topology", "Topology-Aware Scheduling", "Kubernetes SIG Scheduling", "official_documentation", "https://kueue.sigs.k8s.io/docs/concepts/topology_aware_scheduling/", ["hierarchical topology-aware all-or-nothing workload placement"], ["Node-label topology depends on provider/admin correctness." ]),
    ev("slurm-job-state", "Slurm Job State Codes", "SchedMD", "official_documentation", "https://slurm.schedmd.com/job_state_codes.html", ["batch job lifecycle, preemption, timeout, staging and failure distinctions"], ["Slurm implementation semantics." ]),
    ev("slurm-reservation", "Slurm Advanced Resource Reservation Guide", "SchedMD", "official_documentation", "https://slurm.schedmd.com/reservations.html", ["time-scoped resource reservations for nodes, cores, licenses and burst buffers"], ["Slurm implementation semantics." ]),
    ev("slurm-qos", "Slurm Quality of Service", "SchedMD", "official_documentation", "https://slurm.schedmd.com/qos.html", ["priority, preemption and resource-limit controls"], ["Slurm policy/configuration-specific." ]),
    ev("ray-placement", "Ray Placement Groups", "Ray Project", "official_documentation", "https://docs.ray.io/en/latest/ray-core/scheduling/placement-group.html", ["atomic bundle reservations, gang scheduling, pack/spread and topology"], ["Ray logical resources are admission/accounting constructs, not physical-isolation guarantees." ]),
    ev("ray-actors", "Ray Actors", "Ray Project", "official_documentation", "https://docs.ray.io/en/latest/ray-core/actors.html", ["actor worker, scheduling and restart/retry model"], ["Ray-specific actor semantics." ]),
    ev("dask-worker-state", "Dask Worker State Machine", "Dask Project", "official_documentation", "https://distributed.dask.org/en/latest/worker-state.html", ["task, dependency transfer, cancellation and worker state-machine distinctions"], ["Dask implementation semantics." ]),
    ev("dask-memory", "Dask Managing Memory", "Dask Project", "official_documentation", "https://distributed.dask.org/en/latest/memory.html", ["distributed object lifetime, recomputation and memory management"], ["Dask data/task runtime, not general persistence." ]),
    ev("spark-scheduling", "Spark Job Scheduling", "Apache Spark", "official_documentation", "https://spark.apache.org/docs/latest/job-scheduling.html", ["executor allocation, FIFO/fair scheduling and dynamic allocation"], ["Spark-specific behavior and version." ]),
    ev("temporal-docs", "Temporal Platform Documentation", "Temporal Technologies", "official_documentation", "https://docs.temporal.io/", ["durable workflow replay, task queues, activities, retries and timers"], ["Workflow semantics are implementation-specific and business workflow ownership remains external." ]),
    ev("temporal-timeouts", "Temporal Activity Timeouts", "Temporal Technologies", "official_documentation", "https://docs.temporal.io/develop/typescript/failure-detection", ["activity timeout, retry, heartbeat and cancellation-delivery semantics"], ["SDK-specific page; exact SDK/version required." ]),
    ev("etcd-api", "etcd API", "etcd Project", "official_documentation", "https://etcd.io/docs/v3.7/learning/api/", ["leases, revisions, transactions and compare-and-swap"], ["Client protocols still require correct fencing at protected resource." ]),
    ev("etcd-concurrency", "etcd concurrency API reference", "etcd Project", "official_documentation", "https://etcd.io/docs/v3.8/dev-guide/api_concurrency_reference_v3/", ["locks/elections tied to leases and revisions"], ["Lock service alone cannot fence an external effect." ]),
    ev("zookeeper-recipes", "ZooKeeper Recipes and Solutions", "Apache ZooKeeper", "official_documentation", "https://zookeeper.apache.org/doc/current/recipes.html", ["locks, barriers, queues and leader election with ephemeral sequential nodes"], ["Recipes require client error handling and external fencing for protected effects." ]),
    ev("criu", "CRIU documentation", "CRIU Project", "official_documentation", "https://criu.org/Main_Page", ["Linux userspace process checkpoint/restore"], ["Kernel, workload and external-resource compatibility constraints apply." ]),
    ev("otel-resource", "OpenTelemetry Resource", "OpenTelemetry", "standard", "https://opentelemetry.io/docs/specs/otel/resource/", ["identity and location of observed telemetry entity"], ["Resource attributes do not establish provider control identity by themselves." ]),
    ev("opentelemetry-system", "OpenTelemetry System Semantic Conventions", "OpenTelemetry", "standard", "https://opentelemetry.io/docs/specs/semconv/system/", ["system, container, hardware, process and runtime metrics conventions"], ["Many conventions have mixed/development stability." ]),
    ev("openmetrics", "OpenMetrics Specification", "Prometheus Project / CNCF", "standard", "https://github.com/prometheus/OpenMetrics/blob/main/specification/OpenMetrics.md", ["metric family wire/model conventions"], ["Metric transport does not define SLO semantics." ]),
    ev("cloudevents", "CloudEvents Specification", "Cloud Native Computing Foundation", "standard", "https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md", ["portable event envelope identity, source, type and time"], ["Envelope does not define runtime receipt claim semantics." ]),
    ev("google-sre", "The Site Reliability Workbook", "Google", "official_book", "https://sre.google/workbook/table-of-contents/", ["SLO, error-budget, overload, monitoring and incident practices"], ["Operational guidance, not a normative machine-readable contract." ]),
    ev("focus-1.2", "FOCUS Specification v1.2", "FinOps Open Cost and Usage Specification", "standard", "https://focus.finops.org/focus-specification/v1-2/", ["provider-neutral cost and usage billing schema and vocabulary"], ["Billing truth is downstream of runtime metering and provider corrections." ], "2025-05-29"),
    ev("opencost", "OpenCost Specification", "OpenCost / CNCF", "standard", "https://opencost.io/docs/specification/", ["Kubernetes infrastructure allocation, usage and idle cost model"], ["Kubernetes-focused and not an invoice authority." ]),
    ev("sci-iso", "ISO/IEC 21031:2024 Software Carbon Intensity specification", "ISO/IEC", "standard", "https://www.iso.org/standard/86612.html", ["software carbon intensity calculation methodology"], ["Does not provide all input measurements or scheduling policy." ], "2024-03"),
    ev("sci-spec", "Software Carbon Intensity Specification 1.1", "Green Software Foundation", "standard", "https://sci.greensoftware.foundation/", ["operational/embodied carbon and functional-unit method"], ["Attribution input quality and marginal-vs-average decisions remain explicit." ]),
    ev("kepler", "Kepler", "Cloud Native Computing Foundation", "official_project", "https://www.cncf.io/projects/kepler/", ["eBPF-based energy-related system observation and Prometheus export"], ["Model accuracy, platform support and attribution uncertainty require validation." ]),
    ev("redfish", "Redfish Specification and Data Model", "DMTF", "standard", "https://www.dmtf.org/standards/redfish", ["hardware inventory, health, telemetry, jobs and management resources"], ["Provider implementation/profile conformance varies." ]),
    ev("nist-cloud", "NIST SP 800-145: The Definition of Cloud Computing", "NIST", "standard", "https://www.nist.gov/publications/nist-definition-cloud-computing", ["resource pooling, rapid elasticity and measured service"], ["Conceptual definition, not a binding/provider API." ], "2011-09-28"),
    ev("cxl-3.2", "Compute Express Link Specification 3.2", "CXL Consortium", "standard", "https://computeexpresslink.org/wp-content/uploads/2024/11/CXL-Specification_rev3p2_ver1p0_2024October2_evalcopy.pdf", ["coherent fabric, switching, memory pooling/sharing and device topology"], ["Hardware specification; deployable capabilities require inventory and conformance evidence." ], "2024-10-02"),
    ev("ucie-2", "UCIe 2.0 Specification: Manageability Architecture", "UCIe Consortium", "standard", "https://www.uciexpress.org/_files/ugd/0c1418_b6481ec611e24c6e91f1beb743b0c860.pdf", ["chiplet interconnect manageability, telemetry and virtual channels"], ["Package-level interface; not cluster resource scheduling." ], "2024"),
    ev("firecracker", "Firecracker: Lightweight Virtualization for Serverless Applications", "USENIX / Amazon Web Services", "research_paper", "https://www.usenix.org/conference/nsdi20/presentation/agache", ["microVM isolation/runtime design and startup/memory tradeoffs"], ["2020 design outside innovation window; implementation/version evidence still required." ], "2020"),
    ev("drf", "Dominant Resource Fairness: Fair Allocation of Multiple Resource Types", "UC Berkeley", "research_paper", "https://digicoll.lib.berkeley.edu/record/136796/files/EECS-2011-18.pdf", ["multiresource fairness properties and algorithm"], ["Properties hold under the paper model; topology and indivisible devices may require extensions." ], "2011"),
    ev("firmament", "Firmament: Fast, Centralized Cluster Scheduling at Scale", "USENIX / University of Cambridge", "research_paper", "https://research.google/pubs/firmament-fast-centralized-cluster-scheduling-at-scale/", ["incremental min-cost-flow cluster scheduling and quality/latency tradeoff"], ["Research system; production target/scale must be requalified." ], "2016"),
    ev("sparrow", "Sparrow: Distributed, Low Latency Scheduling", "ACM SOSP / UC Berkeley", "research_paper", "https://people.csail.mit.edu/matei/papers/2013/sosp_sparrow.pdf", ["decentralized sampling and late binding for low-latency scheduling"], ["Probabilistic research model; workload assumptions matter." ], "2013"),
    ev("borg", "Large-scale cluster management at Google with Borg", "Google Research", "research_paper", "https://research.google.com/pubs/archive/43438.pdf", ["production cluster admission, quota, priority, scheduling and task lifecycle design"], ["Historical proprietary environment; not a portable contract." ], "2015"),
    ev("serverless-datacenter", "The Serverless Datacenter: Hardware and Software Techniques for Resource Disaggregation", "UC Berkeley", "doctoral_thesis", "https://www2.eecs.berkeley.edu/Pubs/TechRpts/2022/EECS-2022-86.html", ["physical/logical disaggregation and demand-driven resource interfaces"], ["Research prototypes and selected workloads; not general production proof." ], "2022-05-13"),
    ev("harvest-serverless", "Faster and Cheaper Serverless Computing on Harvested Resources", "ACM SOSP / Microsoft Research", "research_paper", "https://doi.org/10.1145/3477132.3483580", ["eviction-aware serverless scheduling on variable spare resources"], ["Paper environment and workload scope; not universal provider guarantee." ], "2021-10-26"),
    ev("cncf-platforms", "Platforms White Paper", "CNCF TAG App Delivery", "whitepaper", "https://tag-app-delivery.cncf.io/whitepapers/platforms/", ["platform/product user experience and capability packaging distinctions"], ["Guidance, not runtime semantic standard." ]),
]


def innovation(suffix: str, name: str, year: int, family: str, change: str, compiler_impact: list[str], evidence: list[str], maturity: str, caveats: list[str]) -> dict:
    return {
        "record_kind": "innovation",
        "innovation_id": f"innovation.runtime-resource.{suffix}",
        "edition": EDITION,
        "status": "evidence_backed_candidate",
        "name": name,
        "first_material_year": year,
        "window": "2021-2026",
        "family": family,
        "core_change": change,
        "compiler_implications": compiler_impact,
        "maturity": maturity,
        "non_llm": True,
        "evidence_refs": evidence,
        "caveats": caveats,
    }


INNOVATIONS = [
    innovation("dra-structured", "Kubernetes Dynamic Resource Allocation with structured device claims", 2024, "device_resource_control", "Moves specialized-device requests from opaque plugin-era counts toward class/claim/slice APIs and scheduler-visible structured matching.", ["Represent device requests as capability predicates and alternatives.", "Bind ResourceClaim, allocation result and driver preparation as distinct phases.", "Probe exact Kubernetes/driver feature maturity."], ["evidence.k8s-dra"], "core API GA in Kubernetes 1.34; extensions vary", ["A DRA claim is still not a provider-neutral semantic resource class without ACL translation."]),
    innovation("dra-partition-capacity", "Partitionable devices and consumable device capacity", 2025, "device_resource_control", "Allows devices to expose partitions and capacity that multiple independent claims can consume rather than all-or-nothing device counts.", ["Resource classes need parent/partition identity and capacity counters.", "Allocation must prove no counter oversubscription and model shared-engine interference."], ["evidence.k8s-dra"], "feature maturity varies across Kubernetes 1.33-1.36", ["Capacity sharing does not establish performance isolation."]),
    innovation("in-place-resize", "In-place workload CPU and memory resize", 2023, "elasticity", "Separates resource-rights changes from destructive workload replacement for supported CPU/memory updates.", ["Add resize intent, proposed/accepted/realized resource vectors and transition receipts.", "Distinguish restart-required from in-place realizable changes."], ["evidence.k8s-resize"], "stable in Kubernetes 1.35", ["Not all resources or container/runtime combinations resize in place."]),
    innovation("kueue-admission", "Queueing and quota-reservation layer for batch workloads", 2022, "admission", "Makes workload admission, resource flavors, quota borrowing, fair sharing and preemption explicit above pod placement.", ["Compile admission separately from placement.", "Model LocalQueue, ClusterQueue, Cohort and ResourceFlavor through provider-neutral ACLs."], ["evidence.kueue-concepts", "evidence.kueue-clusterqueue"], "actively developed Kubernetes SIG project", ["Admission does not mean physical scheduling completion."]),
    innovation("topology-aware-batch", "Hierarchical topology-aware all-or-nothing batch scheduling", 2024, "placement", "Adds rack/block/host topology domains and group-level capacity checks for communication-sensitive jobs.", ["Topology graph must carry hierarchy and freshness.", "Support role/slice indexed gang constraints and placement receipts."], ["evidence.kueue-topology"], "beta in Kueue", ["Label accuracy and network-performance assumptions require evidence."]),
    innovation("jobset", "Coordinated JobSet lifecycle and failure policy", 2023, "distributed_jobs", "Models multiple replicated jobs as one coordinated runtime workload with dependency, success and failure policies.", ["Preserve logical JobSet, child job and attempt identities.", "Compile failure rules and restart scope rather than one generic retry count."], ["evidence.jobset"], "Kubernetes SIG project; API version evolving", ["Business workflow semantics remain outside runtime ownership."]),
    innovation("sched-ext", "Dynamically loadable safe-fallback Linux schedulers through sched_ext/eBPF", 2024, "host_scheduling", "Opens the host CPU-scheduler policy surface to BPF programs with runtime diagnostics and fail-safe fallback.", ["Treat host scheduler policy as a target capability/offer.", "Require fallback, watchdog, diagnostics and policy-version receipts."], ["evidence.linux-sched-ext"], "merged Linux facility with evolving scheduler ecosystem", ["Host CPU policy is not cluster scheduling and needs workload-specific validation."]),
    innovation("damon", "Production-oriented data-access monitoring and access-aware memory operations", 2021, "memory_control", "Provides lightweight scalable access-pattern observation and policy-driven memory actions.", ["Expose access-observation method and uncertainty.", "Bind memory-tier/reclaim policy independently from application semantics."], ["evidence.linux-damon"], "Linux kernel subsystem", ["Access frequency is not business value or safe eviction proof."]),
    innovation("mglru", "Multi-generational LRU page reclaim", 2022, "memory_control", "Uses access generations, tiers and feedback to improve page reclaim under pressure.", ["Target profile should report reclaim mechanism where it affects latency/capacity models.", "Do not encode kernel reclaim policy as application-level guarantee."], ["evidence.linux-mglru"], "Linux kernel implementation", ["Benefit is workload/kernel specific."]),
    innovation("cxl-fabric", "CXL 3.x fabric and memory pooling", 2022, "resource_disaggregation", "Extends coherent interconnect toward switched fabrics, pooled/shared memory and composable resource topologies.", ["Topology and resource identity can no longer assume memory belongs permanently to one host.", "Model attach/detach, pooling, latency tier, failure domain and fencing."], ["evidence.cxl-3.2"], "standard; hardware deployment support varies", ["Specification capability is not evidence that a deployed fabric supports every feature."]),
    innovation("ucie-manageability", "UCIe 2.0 chiplet manageability and telemetry architecture", 2024, "heterogeneous_hardware", "Adds standardized package-level management transport, discovery, telemetry/debug and QoS channels across chiplets.", ["Hardware-resource topology may include package/chiplet identities and manageability evidence.", "Keep package telemetry separate from cluster allocation."], ["evidence.ucie-2"], "industry specification", ["Package-level resource management is below the platform scheduler boundary."]),
    innovation("wasi-component", "WASI 0.2 on the WebAssembly Component Model", 2024, "portable_runtime", "Rebases WASI on typed WIT component interfaces and canonical ABI for cross-language composition.", ["Compile imported effects/capabilities as explicit requirements.", "Bind WIT world, component ABI and runtime conformance by exact edition."], ["evidence.wasi-02", "evidence.wasm-component"], "released interface milestone with uneven runtime coverage", ["Component portability does not automatically imply performance or host-capability parity."]),
    innovation("openmp6", "OpenMP 6.0 heterogeneous parallel runtime surface", 2024, "parallel_runtime", "Advances standardized host/task/target parallel programming and tooling interfaces.", ["Treat offload/task features as exact target capabilities.", "Emit implementation-coverage gaps rather than assuming compiler support."], ["evidence.openmp-6"], "published standard; implementation coverage partial", ["Specification publication is not target conformance evidence."]),
    innovation("mpi41", "MPI 4.1 standard refinement after MPI-4 sessions and persistent operations", 2023, "distributed_runtime", "Consolidates MPI-4 era interfaces and clarifications for scalable session-oriented distributed runtimes.", ["Model session/member-set edition separately from process rank.", "Target profile must enumerate supported MPI features and failure behavior."], ["evidence.mpi-4.1"], "ratified standard", ["Portable fault tolerance remains incomplete and implementation-dependent."]),
    innovation("oci-artifacts", "OCI Image/Distribution 1.1 artifact references and referrers API", 2024, "artifact_supply", "Standardizes linking metadata artifacts such as attestations and SBOM-like objects to content-addressed subjects.", ["Execution artifacts can require evidence artifacts by subject digest.", "Runtime binding validates artifact graph without treating it as resource allocation."], ["evidence.oci-image", "evidence.oci-distribution"], "released OCI specifications", ["Registry support and fallback behavior vary."]),
    innovation("focus-cost", "FOCUS provider-neutral cost and usage specification", 2023, "cost_accounting", "Creates a normalized cross-provider vocabulary/schema for billing and usage data.", ["Bind runtime usage receipts to billing records through explicit reconciliation.", "Preserve list/contracted/effective/billed cost distinctions and correction lineage."], ["evidence.focus-1.2"], "published specification with provider adoption", ["FOCUS data is billing evidence, not real-time scheduling truth."]),
    innovation("sci-standard", "Software Carbon Intensity becomes ISO/IEC 21031", 2024, "sustainability", "Standardizes a rate-based methodology combining operational and embodied emissions for a software boundary and functional unit.", ["Add energy/carbon measurement method, boundary and functional unit to resource plans.", "Reject carbon-aware ranking when comparable inputs do not close."], ["evidence.sci-iso", "evidence.sci-spec"], "international standard", ["Input attribution and carbon-intensity choices remain uncertain and context-dependent."]),
    innovation("kepler-energy", "eBPF-based workload energy attribution with Kepler", 2023, "energy_observability", "Exposes process/container-oriented energy estimates and hardware readings as observable metrics.", ["Treat attribution as versioned model evidence with uncertainty.", "Reconcile workload estimates to host measurements before optimization claims."], ["evidence.kepler"], "CNCF sandbox project", ["Accuracy and supported counters vary by platform/model."]),
    innovation("logical-physical-disaggregation", "Joint logical and physical resource disaggregation", 2022, "resource_disaggregation", "Research reframes resources as independently demanded and fabric-attached rather than fixed server-shaped slots.", ["Do not make machine type the primitive compiler demand.", "Represent resource vectors, topology costs and allocation horizons independently."], ["evidence.serverless-datacenter", "evidence.cxl-3.2"], "research plus emerging standards", ["Remote-resource latency/locality and failure behavior prevent transparent equivalence in general."]),
    innovation("harvested-resources", "Eviction-aware serverless execution on harvested resources", 2021, "interruptible_compute", "Demonstrates cost/throughput gains from scheduling functions on variable spare capacity using eviction-aware control.", ["Interruptibility, eviction rate and checkpoint/retry costs belong in offers.", "Cost-aware selection must retain risk and SLO constraints."], ["evidence.harvest-serverless"], "research prototype/evaluation", ["Results do not generalize without workload and provider revalidation."]),
]


BOUNDARY_MATRIX = {
    "matrix_id": "runtime-resource.semantic-boundary-matrix",
    "edition": EDITION,
    "rows": [
        {"concept": "semantic intent", "identity": "owned by business/data/analytical context", "answers": "what outcome/work means", "may_reference": ["execution requirement", "resource objective"], "must_not_own": ["provider SKU", "PID", "scheduler mechanism"]},
        {"concept": "runtime mechanism", "identity": "mechanism contract and edition", "answers": "how executable work progresses", "may_reference": ["work unit", "attempt", "allocation"], "must_not_own": ["business meaning", "query meaning", "provider product"]},
        {"concept": "resource class", "identity": "semantic dimension and edition", "answers": "what kind of finite capacity", "may_reference": ["unit", "topology relations"], "must_not_own": ["occurrence", "price", "quota"]},
        {"concept": "resource offer", "identity": "offer ID and edition", "answers": "what capacity/qualities may be allocated during validity", "may_reference": ["resource classes", "rates", "topology", "evidence"], "must_not_own": ["workload demand", "actual use"]},
        {"concept": "provider resource", "identity": "provider authority + provider ID + incarnation", "answers": "which provider-controlled resource", "may_reference": ["offers", "occurrences"], "must_not_own": ["logical resource semantics"]},
        {"concept": "deployment occurrence", "identity": "release + target + occurrence", "answers": "which realized deployment now exists", "may_reference": ["provider resources", "bindings"], "must_not_own": ["product or artifact identity"]},
        {"concept": "control-plane product", "identity": "user outcome and operating promise", "answers": "which experience packages capabilities", "may_reference": ["contexts", "libraries", "adapters"], "must_not_own": ["borrowed semantic types", "provider identity"]},
    ],
}


MANIFEST = {
    "corpus_id": "san.domain-atlas.runtime-compute-resource",
    "edition": EDITION,
    "status": "research_candidate",
    "completion_claim": False,
    "scope": "Runtime execution, compute and finite resource control independently of query/business semantics and provider products.",
    "exclusions": ["LLM/generative/agentic semantics", "query semantics", "storage data model", "business workflow meaning", "provider product catalog"],
    "generated_files": ["contexts.jsonl", "types.jsonl", "state-machines.jsonl", "resource-classes.jsonl", "scheduling-policies.jsonl", "decision-points.jsonl", "libraries.jsonl", "requirements-offers-bindings.jsonl", "evidence.jsonl", "innovations.jsonl", "gaps.jsonl", "compiler-contract.json", "boundary-matrix.json"],
    "minimum_gates": {"authoritative_primary_sources": 40, "recent_innovations": 15, "contexts": 25, "resource_classes": 20, "state_machines": 8},
}


def main() -> None:
    write_json("manifest.json", MANIFEST)
    write_json("compiler-contract.json", COMPILER_CONTRACT)
    write_json("boundary-matrix.json", BOUNDARY_MATRIX)
    write_jsonl("contexts.jsonl", CONTEXTS)
    write_jsonl("types.jsonl", TYPES)
    write_jsonl("state-machines.jsonl", STATE_MACHINES)
    write_jsonl("resource-classes.jsonl", RESOURCE_CLASSES)
    write_jsonl("scheduling-policies.jsonl", SCHEDULING_POLICIES)
    write_jsonl("decision-points.jsonl", DECISIONS)
    write_jsonl("libraries.jsonl", LIBRARIES)
    write_jsonl("requirements-offers-bindings.jsonl", REQUIREMENTS + OFFERS + BINDINGS)
    write_jsonl("evidence.jsonl", EVIDENCE)
    write_jsonl("innovations.jsonl", INNOVATIONS)
    write_jsonl("gaps.jsonl", GAPS)


if __name__ == "__main__":
    main()
