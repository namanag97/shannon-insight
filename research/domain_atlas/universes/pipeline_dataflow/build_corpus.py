#!/usr/bin/env python3
"""Build the provider-neutral pipeline/dataflow research corpus deterministically."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EDITION = 1
ACCESSED = "2026-08-25"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for value in values:
            handle.write(json.dumps(value, sort_keys=True) + "\n")


def source(
    source_id: str,
    title: str,
    publisher: str,
    url: str,
    areas: list[str],
    claims: list[str],
    *,
    source_kind: str = "official_documentation",
    publication_date: str | None = None,
    limitations: str = "Implementation evidence; not a universal semantic contract.",
) -> dict:
    return {
        "source_id": source_id,
        "edition": EDITION,
        "title": title,
        "publisher": publisher,
        "source_kind": source_kind,
        "url": url,
        "areas": areas,
        "claims_supported": claims,
        "publication_date": publication_date,
        "accessed_at": ACCESSED,
        "authority_scope": "Primary specification, project documentation, release record or original paper.",
        "limitations": limitations,
    }


SOURCES = [
    source("src.beam.basics", "Basics of the Beam model", "Apache Beam", "https://beam.apache.org/documentation/basics/", ["logical-dataflow", "time-progress", "state"], ["PCollections, transforms, windows, watermarks, triggers, state and timers are distinct model elements."]),
    source("src.beam.programming", "Beam Programming Guide", "Apache Beam", "https://beam.apache.org/documentation/programming-guide/", ["logical-dataflow", "window-trigger", "state"], ["A portable dataflow model covers bounded and unbounded collections with explicit windowing and triggers."]),
    source("src.beam.execution", "Beam Execution Model", "Apache Beam", "https://beam.apache.org/documentation/runtime/model/", ["execution-plan", "retry", "fusion"], ["Runner execution, bundles, retries and transform semantics are separate concerns."]),
    source("src.beam.runner_guide", "Runner Authoring Guide", "Apache Beam", "https://beam.apache.org/contribute/runner-guide/", ["validation", "runner-capability", "rejection"], ["A runner rejects a pipeline when required semantics or capabilities cannot be executed rather than silently weakening the pipeline."], source_kind="official_documentation"),
    source("src.beam.yaml", "Apache Beam YAML", "Apache Beam", "https://beam.apache.org/documentation/sdks/yaml/", ["declarative-definition", "portable-plan"], ["A declarative pipeline surface can target runners and serve as an intermediate representation."], publication_date="2024"),
    source("src.flink.architecture", "Flink Architecture", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/flink-architecture/", ["runtime", "deployment"], ["Client, job manager and task managers separate compilation, coordination and execution."]),
    source("src.flink.checkpointing", "Checkpointing", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-master/docs/dev/datastream/fault-tolerance/checkpointing/", ["checkpoint", "delivery"], ["Checkpoint mode, interval, alignment and externalization are independent decisions."]),
    source("src.flink.fault_tolerance", "Fault Tolerance", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/", ["checkpoint", "recovery", "delivery"], ["End-to-end exactly-once requires replayable sources and transactional or idempotent sinks."]),
    source("src.flink.savepoints", "Savepoints", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/savepoints/", ["state", "migration", "deployment"], ["Operational savepoints differ from recovery checkpoints and require stable operator identities."]),
    source("src.flink.watermarks", "Generating Watermarks", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/event-time/generating_watermarks/", ["time-progress"], ["Watermark generation, idleness and alignment are explicit progress decisions."]),
    source("src.flink.changelog", "Changelog Mode", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-master/docs/sql/reference/queries/changelog/", ["incremental", "update-model"], ["Insert, update-before, update-after and delete changes form explicit changelog modes."]),
    source("src.flink.backpressure", "Tuning Checkpoints and Large State", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/large_state_tuning/", ["backpressure", "checkpoint"], ["Barrier alignment, backpressure and unaligned checkpoints create measurable runtime trade-offs."]),
    source("src.flink.async_state_2", "Apache Flink 2.0.0: A New Era of Real-Time Data Processing", "Apache Flink", "https://flink.apache.org/2025/03/24/apache-flink-2.0.0-a-new-era-of-real-time-data-processing/", ["state", "innovation"], ["Asynchronous state access and disaggregated state preserve event-time semantics while changing physical execution."], publication_date="2025-03-24"),
    source("src.flink.cdc", "Flink CDC documentation", "Apache Flink", "https://flink.apache.org/documentation/flink-cdc-stable/", ["cdc", "pipeline-definition"], ["CDC pipelines expose source, transform, route and sink configuration as a distinct surface."]),
    source("src.kafka.introduction", "Apache Kafka Documentation", "Apache Kafka", "https://kafka.apache.org/documentation/", ["transport", "partition", "delivery"], ["Ordering is scoped to a topic partition and consumer position is offset-based."]),
    source("src.kafka.design", "Kafka Design", "Apache Kafka", "https://kafka.apache.org/documentation/#design", ["transport", "transactions"], ["Replication, retention, consumer groups, idempotent production and transactions have separate guarantees."]),
    source("src.kafka.connect", "Kafka Connect User Guide", "Apache Kafka", "https://kafka.apache.org/35/kafka-connect/user-guide/", ["connector-runtime", "offset", "delivery"], ["Connector definitions, tasks, offsets and exactly-once support are separate runtime elements."]),
    source("src.kafka.connector_dev", "Kafka Connect Connector Development Guide", "Apache Kafka", "https://kafka.apache.org/36/kafka-connect/connector-development-guide/", ["connector-runtime", "offset"], ["Source offsets and task partitioning are required recovery contracts for connectors."]),
    source("src.debezium.postgres", "Debezium PostgreSQL Connector", "Debezium", "https://debezium.io/documentation/reference/stable/connectors/postgresql.html", ["cdc", "snapshot-change-handoff"], ["Snapshots, log streaming, transaction metadata and incremental snapshot windows have distinct semantics."]),
    source("src.debezium.incremental_snapshot", "Incremental Snapshots in Debezium", "Debezium", "https://debezium.io/blog/2021/10/07/incremental-snapshots/", ["cdc", "innovation", "snapshot-change-handoff"], ["Chunked watermark windows reconcile snapshot rows with concurrent log changes and survive restarts."], publication_date="2021-10-07"),
    source("src.spark.structured_streaming", "Structured Streaming Programming Guide", "Apache Spark", "https://spark.apache.org/docs/latest/streaming/getting-started.html", ["microbatch", "streaming", "checkpoint"], ["A streaming table model runs incremental queries with offsets, checkpointing and write-ahead logs."]),
    source("src.spark.stateful", "Arbitrary Stateful Processing", "Apache Spark", "https://spark.apache.org/docs/latest/streaming/structured-streaming-transform-with-state.html", ["state", "innovation"], ["Stateful processors expose state variables, timers, TTL and lifecycle callbacks."], publication_date="2025"),
    source("src.airflow.dag", "Dags", "Apache Airflow", "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html", ["orchestration", "schedule", "run"], ["A DAG definition, DAG run, data interval and task instance are distinct concepts."]),
    source("src.airflow.tasks", "Tasks", "Apache Airflow", "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html", ["task-attempt", "retry"], ["Tasks instantiate into stateful task instances with explicit lifecycles."]),
    source("src.airflow.backfill", "Backfill", "Apache Airflow", "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/backfill.html", ["backfill", "data-cut"], ["Backfill range, reprocessing behavior, ordering and concurrency are independent decisions."]),
    source("src.airflow.data_aware", "Data-aware scheduling", "Apache Airflow", "https://airflow.apache.org/docs/apache-airflow/2.10.4/authoring-and-scheduling/datasets.html", ["materialization-trigger", "innovation"], ["Dataset update events can trigger downstream DAGs independently of time schedules."], publication_date="2022"),
    source("src.dagster.assets", "Dagster documentation", "Dagster", "https://docs.dagster.io/", ["asset-orchestration", "lineage"], ["Software-defined assets make materializations and asset dependencies first-class orchestration concepts."]),
    source("src.dagster.partitions", "Partitioned assets and jobs", "Dagster", "https://docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets", ["partition", "backfill"], ["Asset partitions and run partitions are related but distinct, and mappings connect partition spaces."]),
    source("src.dagster.backfills", "Backfills", "Dagster", "https://docs.dagster.io/guides/build/partitions-and-backfills/backfilling-data", ["backfill"], ["A backfill selects partition subsets and coordinates multiple materialization runs."]),
    source("src.dagster.asset_checks", "Introducing Dagster Asset Checks", "Dagster", "https://dagster.io/blog/dagster-asset-checks", ["quality-gate", "innovation"], ["Asset checks can gate propagation and execute with or separately from materialization."], publication_date="2023-10-09"),
    source("src.prefect.flows", "Flows", "Prefect", "https://docs.prefect.io/v3/concepts/flows", ["orchestration", "run"], ["Flow definitions, nested flow runs, retries and parameters are distinct runtime concepts."]),
    source("src.prefect.tasks", "Tasks", "Prefect", "https://docs.prefect.io/v3/concepts/tasks", ["task-attempt", "cache", "retry"], ["Tasks have run identities, caching, retries, timeouts and concurrent execution."]),
    source("src.prefect.deployments", "Deployments", "Prefect", "https://docs.prefect.io/v3/concepts/deployments", ["deployment", "schedule"], ["Deployments bind flow definitions to remote triggers, infrastructure and concurrency controls."]),
    source("src.temporal.platform", "Temporal Platform Documentation", "Temporal", "https://docs.temporal.io/", ["durable-execution", "replay"], ["Durable workflow state can resume from event history after process or infrastructure failure."]),
    source("src.temporal.retry", "Retry Policies", "Temporal", "https://docs.temporal.io/encyclopedia/retry-policies", ["retry", "idempotency"], ["Workflow and activity retries differ; activities must tolerate re-execution."]),
    source("src.temporal.cancellation", "Cancellation", "Temporal", "https://docs.temporal.io/develop/java/cancellation", ["cancellation"], ["Cancellation propagation and cancellation type are explicit policy choices."]),
    source("src.argo.dag", "DAG", "Argo Workflows", "https://argo-workflows.readthedocs.io/en/latest/walk-through/dag/", ["orchestration", "graph"], ["DAG tasks encode dependencies and enhanced depends expressions."]),
    source("src.argo.retry", "Retrying Failed or Errored Steps", "Argo Workflows", "https://argo-workflows.readthedocs.io/en/latest/walk-through/retrying-failed-or-errored-steps/", ["retry"], ["Retry limit, policy, expression and backoff are separate decisions."]),
    source("src.dbt.incremental", "Incremental models", "dbt Labs", "https://docs.getdbt.com/docs/build/incremental-models", ["incremental", "materialization"], ["Incremental selection, unique key and update strategy determine materialization semantics."]),
    source("src.dbt.snapshots", "Snapshots", "dbt Labs", "https://docs.getdbt.com/docs/build/snapshots", ["snapshot", "bitemporal"], ["Snapshot strategies record changing source rows over time and require stable keys."]),
    source("src.openlineage.spec", "OpenLineage Specification", "OpenLineage", "https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md", ["lineage", "receipt", "run"], ["Jobs, runs, datasets and run events are distinct, extensible lineage entities."], source_kind="open_standard"),
    source("src.openlineage.1_0", "Announcing OpenLineage 1.0", "OpenLineage", "https://openlineage.io/blog/1.0-release/", ["lineage", "innovation"], ["OpenLineage 1.0 added static events alongside observed runtime lineage."], publication_date="2023-08-04"),
    source("src.w3c.prov_o", "PROV-O: The PROV Ontology", "W3C", "https://www.w3.org/TR/prov-o/", ["provenance"], ["Entities, activities, agents, generation, usage, derivation and invalidation form a provenance model."], source_kind="standard"),
    source("src.w3c.shacl", "Shapes Constraint Language (SHACL)", "W3C", "https://www.w3.org/TR/shacl/", ["validation", "conformance", "finding-report"], ["Validation distinguishes processor failure from a complete conformance report whose results identify focus, constraint and severity."], source_kind="standard", publication_date="2017"),
    source("src.cloudevents.spec", "CloudEvents Specification", "CNCF", "https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md", ["events", "deduplication"], ["Source plus ID identifies an event; type, time, subject and data schema have distinct roles."], source_kind="open_standard"),
    source("src.opentelemetry.trace", "Tracing API", "OpenTelemetry", "https://opentelemetry.io/docs/specs/otel/trace/api/", ["observability", "attempt"], ["Spans, links, events, attributes and status provide scoped execution telemetry."], source_kind="open_standard"),
    source("src.asyncapi.spec", "AsyncAPI Specification", "AsyncAPI Initiative", "https://github.com/asyncapi/spec/blob/master/spec/asyncapi.md", ["channel", "message", "binding"], ["Applications, channels, operations, messages and protocol bindings are distinct contracts."], source_kind="open_standard"),
    source("src.reactive_streams.spec", "Reactive Streams Specification", "Reactive Streams", "https://github.com/reactive-streams/reactive-streams-jvm", ["backpressure", "flow-control"], ["Asynchronous boundaries require non-blocking demand signaling and bounded flow control."], source_kind="open_standard"),
    source("src.serverless_workflow.spec", "Serverless Workflow Specification", "CNCF Serverless Workflow", "https://github.com/serverlessworkflow/specification", ["workflow", "retry", "timeout"], ["Declarative workflows model tasks, waits, events, errors, retries and timeouts as typed constructs."], source_kind="open_standard"),
    source("src.substrait.basics", "Substrait Relations Basics", "Substrait", "https://substrait.io/relations/basics/", ["logical-plan", "physical-plan"], ["Portable relational plans compose relations and references but do not define all orchestration semantics."], source_kind="open_standard"),
    source("src.tarjan.scc", "Depth-First Search and Linear Graph Algorithms", "Robert Tarjan / SIAM", "https://doi.org/10.1137/0201010", ["graph", "strong-components", "complexity"], ["Depth-first search can compute strongly connected components of a directed graph in linear vertex-plus-edge time."], source_kind="original_research", publication_date="1972"),
    source("src.naiad.paper", "Naiad: A Timely Dataflow System", "Microsoft Research / ACM", "https://www.microsoft.com/en-us/research/publication/naiad-a-timely-dataflow-system-2/", ["dataflow", "cyclic-graph", "progress"], ["Cyclic dataflow structure and logical progress semantics are separate but composable contracts; lawful cycles require structured feedback and progress information."], source_kind="original_research", publication_date="2013"),
    source("src.arrow.c_stream", "Arrow C Stream Interface", "Apache Arrow", "https://arrow.apache.org/docs/format/CStreamInterface.html", ["port", "carrier"], ["A stream interface separates schema acquisition, batches, release and error reporting."], source_kind="open_standard"),
    source("src.substrait.type_system", "Substrait Type System", "Substrait", "https://substrait.io/types/type_system/", ["port", "type", "nullability", "carrier"], ["Type class, nullability, variation and parameters are separate dimensions and coercions are explicit rather than ambient."], source_kind="open_standard"),
    source("src.flink.changelog_mode", "ChangelogMode", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-stable/api/java/org/apache/flink/table/connector/ChangelogMode.html", ["port", "update-model", "compatibility"], ["Insert-only, upsert and full changelog modes expose different admitted change sets."], source_kind="official_documentation"),
    source("src.flink.source_sink_contract", "User-defined Sources and Sinks", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sourcessinks/", ["port", "boundedness", "update-model", "sink-acceptance"], ["A source produces and a sink accepts explicit boundedness and changelog capabilities; unsupported change kinds require planning or rejection."], source_kind="official_documentation"),
    source("src.flink.execution_order", "Execution Mode: Order of Processing", "Apache Flink", "https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/execution_mode/", ["port", "ordering", "event-time"], ["Streaming consumers cannot assume arrival order; keyed, batch and event-time order require separately stated guarantees."], source_kind="official_documentation"),
    source("src.postgresql.export_snapshot", "Snapshot Synchronization Functions", "PostgreSQL Global Development Group", "https://www.postgresql.org/docs/18/functions-admin.html#FUNCTIONS-SNAPSHOT-SYNCHRONIZATION", ["data-cut", "snapshot", "validity"], ["An exported transaction snapshot identifies one visibility view and has a bounded import lifetime tied to the exporting transaction."], source_kind="official_documentation"),
    source("src.kafka.consumer_position", "Kafka Consumer Position and Offsets", "Apache Kafka", "https://kafka.apache.org/documentation/#consumerconfigs", ["data-cut", "partition", "offset", "retention"], ["Consumer position is partition-scoped and denotes the next offset; positions may move and retained history constrains replay."], source_kind="official_documentation"),
    source("src.timely.frontier", "Timely Dataflow Progress Tracking", "Timely Dataflow", "https://timelydataflow.github.io/timely-dataflow/chapter_5/chapter_5_2.html", ["data-cut", "frontier", "partial-order", "completion"], ["Logical progress uses timestamp capabilities and minimal antichain frontiers to constrain possible future times."], source_kind="official_documentation"),
    source("src.iceberg.spec", "Apache Iceberg Table Specification", "Apache Iceberg", "https://iceberg.apache.org/spec/", ["snapshot", "commit", "incremental"], ["Snapshots, sequence numbers, manifests and optimistic commits define table state transitions."], source_kind="open_standard"),
    source("src.iceberg.branching", "Branching and Tagging", "Apache Iceberg", "https://iceberg.apache.org/docs/latest/branching/", ["pipeline-change", "materialization", "innovation"], ["Named snapshot branches enable audit, testing and write-audit-publish workflows."]),
    source("src.delta.protocol", "Delta Transaction Log Protocol", "Delta Lake", "https://github.com/delta-io/delta/blob/master/PROTOCOL.md", ["materialization", "commit", "ratification", "publication", "visibility"], ["Proposed, staged, ratified and published commits are distinct; catalog-managed publication may occur after successful ratification and must preserve version order."], source_kind="open_standard"),
    source("src.openlineage.object_model", "OpenLineage Object Model 1.52.0", "OpenLineage", "https://openlineage.io/docs/spec/object-model/", ["materialization", "dataset", "run", "version", "observation"], ["Design metadata, runtime observations, jobs, runs, datasets and provider-defined dataset versions are distinct."], source_kind="open_standard"),
    source("src.openlineage.quality_assertions", "OpenLineage Data Quality Assertions Facet 1.52.0", "OpenLineage", "https://openlineage.io/docs/spec/facets/dataset-facets/data_quality_assertions/", ["quality-gate", "assertion", "severity", "publication"], ["Assertion success and configured severity are independent; a failed warning need not block execution while an error may block."], source_kind="open_standard"),
    source("src.openlineage.version_facet", "OpenLineage Dataset Version Facet 1.52.0", "OpenLineage", "https://openlineage.io/docs/spec/facets/dataset-facets/version_facet/", ["materialization", "dataset-version", "identity"], ["A dataset occurrence may carry a provider-defined dataset version without standardizing the provider's version domain."], source_kind="open_standard"),
    source("src.delta.cdf", "Change Data Feed", "Delta Lake", "https://docs.delta.io/delta-change-data-feed/", ["incremental", "cdc", "innovation"], ["Row-level changes carry operation, commit version and commit timestamp with retention limits."]),
    source("src.delta.streaming", "Table streaming reads and writes", "Delta Lake", "https://docs.delta.io/delta-streaming/", ["streaming", "idempotency", "delivery"], ["Streaming checkpoints and application/version keys support idempotent table writes."]),
    source("src.hudi.timeline", "Timeline", "Apache Hudi", "https://hudi.apache.org/docs/next/timeline/", ["transaction", "materialization", "maintenance"], ["Requested and completed instants record writes and table-service actions in a timeline."]),
    source("src.hudi.spec", "Apache Hudi Technical Specification 1.0", "Apache Hudi", "https://hudi.apache.org/learn/tech-specs/", ["incremental", "cdc", "maintenance"], ["Snapshot, incremental and CDC queries expose different views of timeline changes."], source_kind="open_standard"),
    source("src.materialize.arrangements", "Arrangements", "Materialize", "https://materialize.com/docs/get-started/arrangements/", ["incremental", "dataflow", "state"], ["Differential collections represent updates as data, logical time and multiplicity difference."]),
    source("src.timely.progress", "Creating Operators", "Timely Dataflow", "https://timelydataflow.github.io/timely-dataflow/chapter_2/chapter_2_4.html", ["progress", "iterative-dataflow"], ["Capabilities and antichain frontiers track when logical times can still receive data."]),
    source("src.differential.repo", "Differential Dataflow", "Timely Dataflow", "https://github.com/TimelyDataflow/differential-dataflow", ["incremental", "iteration"], ["Collections of timestamped differences support incremental and iterative computation."], source_kind="official_implementation"),
    source("src.dbsp.paper", "DBSP: Automatic Incremental View Maintenance for Rich Query Languages", "VLDB Endowment", "https://www.vldb.org/pvldb/vol16/p1601-budiu.pdf", ["incremental", "innovation"], ["Algebraic differentiation can compile batch queries into incremental circuits."], source_kind="original_research", publication_date="2023"),
    source("src.chandy_lamport.paper", "Distributed Snapshots: Determining Global States of Distributed Systems", "Leslie Lamport / ACM", "https://lamport.azurewebsites.net/pubs/chandy.pdf", ["checkpoint", "barrier"], ["Marker-based snapshots capture a consistent distributed state without stopping computation."], source_kind="original_research", publication_date="1985"),
    source("src.sagas.paper", "Sagas", "ACM", "https://dl.acm.org/doi/10.1145/38713.38742", ["compensation", "long-running-transaction"], ["Long-lived transactions can be decomposed into subtransactions with compensating actions."], source_kind="original_research", publication_date="1987"),
    source("src.rfc5545", "RFC 5545: Internet Calendaring and Scheduling Core Object Specification", "IETF", "https://www.rfc-editor.org/rfc/rfc5545", ["schedule", "calendar"], ["Recurrence rules, exclusions, time zones and duration are distinct schedule semantics."], source_kind="standard"),
    source("src.kubernetes.job", "Jobs", "Kubernetes", "https://kubernetes.io/docs/concepts/workloads/controllers/job/", ["deployment", "attempt", "completion"], ["Jobs manage pods to completion with indexed, parallel and failure-policy choices."]),
    source("src.kubernetes.cronjob", "CronJob", "Kubernetes", "https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/", ["schedule", "concurrency"], ["Missed schedules, concurrency policies and starting deadlines are separate operational decisions."]),
    source("src.oci.image_spec", "OCI Image Format Specification", "Open Container Initiative", "https://github.com/opencontainers/image-spec", ["artifact", "deployment"], ["Content-addressed manifests and configurations identify executable image artifacts."], source_kind="open_standard"),
    source("src.calcite.algebra", "Relational Algebra", "Apache Calcite", "https://calcite.apache.org/docs/algebra.html", ["logical-plan", "optimization"], ["Relational expressions form trees that planners transform using equivalence-preserving rules."]),
    source("src.datafusion.architecture", "DataFusion Architecture", "Apache DataFusion", "https://datafusion.apache.org/contributor-guide/architecture.html", ["logical-plan", "physical-plan", "execution"], ["Logical optimization, physical planning and partitioned execution are distinct phases."]),
    source("src.open_data_contract", "Open Data Contract Standard", "BITOL", "https://docs.datacontract.com/open-data-contract-standard", ["port", "data-contract"], ["Schema, quality, SLA, roles and pricing can be expressed as versioned data contracts."], source_kind="open_standard"),
    source("src.paimon.overview", "Apache Paimon Documentation", "Apache Paimon", "https://paimon.apache.org/docs/master/", ["batch-stream", "changelog", "innovation"], ["An LSM-backed table can expose batch snapshots and streaming changelogs with selectable merge engines."]),
]


def context(
    slug: str,
    name: str,
    question: str,
    inside: list[str],
    outside: list[str],
    terms: list[str],
    roots: list[str],
    invariants: list[str],
    commands: list[str],
    events: list[str],
    refusals: list[str],
    decisions: list[str],
    neighbors: list[tuple[str, str]],
    evidence: list[str],
) -> dict:
    return {
        "context_id": f"ppl.{slug}",
        "edition": EDITION,
        "status": "sourced_candidate",
        "subdomain_classification": "core",
        "name": name,
        "domain_vision": question,
        "boundary": {"inside": inside, "outside": outside},
        "ubiquitous_language": [{"term": term, "meaning": f"Meaning owned by {name}; requires glossary adjudication before publication."} for term in terms],
        "aggregate_roots": roots,
        "invariants": invariants,
        "commands": commands,
        "domain_events": events,
        "refusals": refusals,
        "state_machine": {"states": ["draft", "validated", "active", "superseded", "retired"], "terminal_states": ["retired"], "transition_law": "Every transition is editioned, authorized and receipt-bearing."},
        "decision_points": decisions,
        "context_relationships": [{"neighbor": n, "relationship": r} for n, r in neighbors],
        "published_language": [f"{name}Definition", f"{name}Decision", f"{name}Receipt", f"{name}Refusal"],
        "anti_corruption_layers": ["Vendor workflow, stream processor and connector models translate at provider adapters; their defaults do not enter the canonical model."],
        "evidence_refs": evidence,
        "llm_dependency": "none",
        "gaps": ["Aggregate and term ownership remain candidate until global context-map adjudication.", "Conformance needs two independent implementations."],
    }


CONTEXTS = [
    context("pipeline_definition", "Pipeline Definition", "What reusable data-processing intent exists independently of any runner or execution?", ["definition identity and edition", "parameters", "declared inputs and outputs", "logical policy references"], ["physical operator placement", "run state", "provider credentials"], ["definition", "edition", "parameter", "entrypoint", "exitpoint"], ["PipelineDefinition"], ["A published edition is immutable.", "Every referenced semantic owner and contract edition resolves."], ["create definition", "revise definition", "publish definition", "retire definition"], ["pipeline definition created", "pipeline definition published", "pipeline definition retired"], ["unresolved semantic reference", "breaking revision without new edition", "ambiguous parameter binding"], ["parameter mutability", "publication authority", "compatibility relation"], [("ppl.graph_topology", "customer_supplier"), ("ppl.execution_plan", "customer_supplier")], ["src.beam.programming", "src.airflow.dag", "src.beam.yaml"]),
    context("graph_topology", "Dataflow Graph Topology", "Which typed nodes and edges compose the logical computation, including structurally identified feedback?", ["node and edge membership", "reachability", "fan-in and fan-out", "subgraph composition", "strong-component and feedback classification"], ["operator algorithm semantics", "port compatibility", "cycle progress or termination law", "runtime placement", "message protocol"], ["node", "edge", "path", "component", "feedback edge", "strongly connected component", "condensation graph"], ["LogicalGraph"], ["Every edge endpoint resolves inside the graph edition.", "Structural cycle classification never establishes progress, termination or productive continuation.", "No unreachable required output is publishable after policy validation."], ["add node", "connect endpoints", "compose subgraph", "classify components", "canonicalize topology"], ["node added", "endpoints connected", "components classified", "topology canonicalized"], ["edge endpoint unresolved", "subgraph identity collision", "feedback declaration unresolved", "duplicate node identity"], ["topology kind", "dynamic expansion law", "cycle policy", "canonical order policy"], [("ppl.port_contract", "customer_supplier"), ("ppl.iterative_dataflow", "partnership")], ["src.substrait.basics", "src.beam.programming", "src.tarjan.scc", "src.naiad.paper"]),
    context("port_contract", "Port Contract", "What may enter or leave a node, with which carrier, update, time and cardinality semantics?", ["direction", "carrier and schema", "boundedness", "update model", "time domain", "cardinality", "compatibility"], ["physical channel", "buffer allocation", "business schema ownership"], ["input port", "output port", "carrier", "update model", "cardinality", "compatibility witness"], ["PortContract"], ["Only output ports connect to input ports.", "Compatibility includes more than structural schema equality."], ["declare port", "revise port", "prove compatibility"], ["port declared", "port compatibility proven"], ["carrier mismatch", "unsafe schema coercion", "time-domain mismatch", "unsupported retractions"], ["schema evolution", "null and missing policy", "ordering requirement", "boundedness"], [("ppl.channel_contract", "customer_supplier"), ("dat.data-contract", "conformist")], ["src.arrow.c_stream", "src.open_data_contract", "src.asyncapi.spec"]),
    context("channel_contract", "Channel Contract", "How are typed elements exchanged without assigning transformation meaning to transport?", ["channel identity", "buffer and capacity", "partition lanes", "ordering scope", "flow-control protocol", "serialization binding"], ["record transformation", "schedule readiness", "business event meaning"], ["channel", "lane", "capacity", "demand", "acknowledgement", "end-of-input"], ["ChannelContract"], ["Capacity is finite or explicitly rejected as unbounded.", "Channel ordering claims are scoped."], ["open channel", "request demand", "send element", "acknowledge element", "close channel"], ["channel opened", "demand requested", "element acknowledged", "channel closed"], ["capacity unsupported", "ordering unsupported", "protocol binding incompatible"], ["push or pull", "buffer bound", "overflow action", "serialization", "compression"], [("ppl.flow_control", "partnership"), ("msg.messaging", "anti_corruption_layer")], ["src.reactive_streams.spec", "src.asyncapi.spec", "src.kafka.introduction"]),
    context("data_cut", "Data Cut", "Exactly which source versions, offsets, partitions or time interval constitute one input selection?", ["source positions", "snapshot identities", "partition selections", "event/valid/recording intervals", "closure proof"], ["execution start and end time", "source extraction mechanics", "downstream materialization"], ["data cut", "frontier", "offset range", "snapshot", "partition subset", "closed cut"], ["DataCut"], ["A closed cut is immutable.", "Every selected boundary uses the source's authoritative position domain."], ["propose cut", "close cut", "extend open cut", "invalidate cut"], ["data cut proposed", "data cut closed", "data cut invalidated"], ["source position expired", "incomparable frontiers", "cut not closed", "mixed snapshot authority"], ["cut closure", "inclusive boundaries", "late-data horizon", "source consistency"], [("ppl.ingestion_contract", "customer_supplier"), ("ppl.pipeline_run", "supplier")], ["src.airflow.dag", "src.iceberg.spec", "src.timely.progress"]),
    context("ingestion_contract", "Ingestion Contract", "How is an authoritative source observed and converted into canonical input without silently changing meaning?", ["source read intent", "snapshot/page/range strategy", "source position", "extraction receipts", "source throttling"], ["transport after extraction", "semantic transformation", "credential ownership"], ["extraction", "source cursor", "read consistency", "source quota", "observation receipt"], ["IngestionDefinition", "ExtractionRun"], ["Source authority and read consistency are explicit.", "Extraction cannot advance a durable cursor before acceptance."], ["preflight extraction", "read source", "advance cursor", "pause extraction", "close extraction"], ["extraction started", "source range observed", "cursor advanced", "extraction completed"], ["source unavailable", "retention gap", "quota denied", "read consistency unsupported"], ["poll or push", "snapshot or change", "page size", "rate limit", "read replica"], [("ppl.data_cut", "customer_supplier"), ("src.source-connector", "anti_corruption_layer")], ["src.kafka.connector_dev", "src.debezium.postgres", "src.beam.basics"]),
    context("transport_contract", "Data Transport", "How are observations moved between boundaries while preserving declared identity, order and integrity?", ["send and receive intents", "routing", "ack boundary", "integrity", "compression and framing binding"], ["data meaning", "business event ownership", "transform algorithms"], ["transport", "route", "frame", "ack boundary", "integrity digest"], ["TransportDefinition", "DeliveryAttempt"], ["Transport never claims semantic equivalence it cannot prove.", "Acknowledgement meaning is protocol-qualified."], ["bind route", "send batch", "send stream element", "acknowledge receipt", "close route"], ["route bound", "payload sent", "payload acknowledged", "route closed"], ["route unavailable", "payload too large", "integrity mismatch", "ack ambiguity"], ["protocol", "compression", "encryption", "batching", "acknowledgement"], [("ppl.channel_contract", "partnership"), ("ppl.delivery_guarantee", "customer_supplier")], ["src.kafka.design", "src.asyncapi.spec", "src.arrow.c_stream"]),
    context("transformation_composition", "Transformation Composition", "How are typed operations composed without confusing logical meaning with physical execution?", ["operation invocation", "typed parameters", "composition", "purity and effect boundary", "information-loss declaration"], ["operation's internal algorithm", "runner selection", "schedule"], ["invocation", "pure transform", "effect intent", "composition", "loss witness"], ["TransformationGraph"], ["Every invocation resolves an exact operation edition.", "Lossy transformations require explicit approval."], ["invoke operation", "compose operations", "approve loss", "validate laws"], ["operation bound", "loss approved", "composition validated"], ["operation unresolved", "law unsatisfied", "loss unapproved", "type mismatch"], ["algorithm variant", "parameter binding", "effect isolation", "error propagation"], [("operation.registry", "conformist"), ("ppl.execution_plan", "customer_supplier")], ["src.substrait.basics", "src.calcite.algebra", "src.beam.execution"]),
    context("incremental_computation", "Incremental Computation", "How is a result updated from changes rather than recomputed, with equivalent observable semantics?", ["change algebra", "differentiation", "incremental state", "consolidation", "equivalence oracle"], ["source CDC transport", "physical state backend", "business interpretation of corrections"], ["change", "difference", "multiplicity", "increment", "consolidation", "fixed point"], ["IncrementalPlan"], ["Incremental result is observationally equivalent to declared batch semantics within its assumptions.", "Negative multiplicities and retractions are not silently discarded."], ["derive incremental plan", "apply change", "consolidate changes", "verify equivalence"], ["incremental plan derived", "change applied", "equivalence verified"], ["unsupported non-monotone operation", "history unavailable", "unbounded differential state"], ["change representation", "maintenance strategy", "arrangement selection", "compaction frontier"], [("ppl.operator_state", "partnership"), ("ppl.transformation_composition", "customer_supplier")], ["src.materialize.arrangements", "src.differential.repo", "src.dbsp.paper"]),
    context("change_capture_coordination", "Change Capture Coordination", "How are source changes positioned, normalized and made resumable without owning source-specific log semantics?", ["normalized change envelope", "transaction boundary", "change offset", "gap detection", "resume"], ["database log decoding internals", "target merge semantics", "initial snapshot selection"], ["change envelope", "source offset", "transaction boundary", "tombstone", "change gap"], ["ChangeSubscription"], ["Offsets advance only after the declared acknowledgement boundary.", "Schema and data changes remain distinguishable."], ["start capture", "checkpoint offset", "seek offset", "detect gap", "resume capture"], ["capture started", "offset checkpointed", "change gap detected", "capture resumed"], ["offset expired", "log truncated", "transaction boundary unknown", "schema history missing"], ["envelope format", "transaction metadata", "tombstone policy", "offset retention"], [("ppl.snapshot_change_handoff", "partnership"), ("src.source-connector", "anti_corruption_layer")], ["src.debezium.postgres", "src.kafka.connector_dev", "src.delta.cdf"]),
    context("snapshot_change_handoff", "Snapshot and Change Handoff", "How does a baseline snapshot join a concurrent change stream without gaps or unjustified ordering claims?", ["handoff strategy", "snapshot windows", "overlap deduplication", "completeness proof", "restart context"], ["snapshot query planning", "source log decoding", "target merge"], ["baseline", "snapshot window", "low watermark", "high watermark", "overlap", "handoff"], ["SnapshotChangeSession"], ["Completion covers every qualifying source row or an explicit gap.", "Overlap resolution preserves authoritative log changes."], ["begin baseline", "open snapshot window", "close snapshot window", "reconcile overlap", "complete handoff"], ["baseline started", "snapshot window opened", "overlap reconciled", "handoff completed"], ["missing stable key", "watermark lost", "log retention crossed", "overlap ambiguous"], ["chunk key", "chunk size", "watermark strategy", "read-only signaling", "restart behavior"], [("ppl.change_capture_coordination", "partnership"), ("ppl.data_cut", "customer_supplier")], ["src.debezium.incremental_snapshot", "src.debezium.postgres", "src.flink.cdc"]),
    context("federated_flow", "Federated Flow", "Which operations may execute at remote sources while preserving semantics, policy and evidence?", ["pushdown eligibility", "remote plan fragment", "capability proof", "result reconciliation"], ["remote engine internals", "connector credential custody", "global query semantics"], ["federation", "pushdown", "remote fragment", "residual", "capability proof"], ["FederatedPlan"], ["Pushdown is equivalence-proven under remote semantics.", "Residual operations remain explicit."], ["propose pushdown", "qualify remote capability", "execute fragment", "reconcile result"], ["pushdown proposed", "remote capability qualified", "fragment completed"], ["semantic mismatch", "policy forbids movement", "remote capability stale", "residual unbound"], ["pushdown boundary", "data movement", "remote snapshot", "fallback"], [("ppl.execution_plan", "partnership"), ("src.federated-query", "anti_corruption_layer")], ["src.substrait.basics", "src.datafusion.architecture", "src.calcite.algebra"]),
    context("reverse_delivery", "Reverse Delivery", "How are governed analytical outputs applied back to operational destinations?", ["audience selection", "activation payload", "destination effect", "suppression", "delivery receipt"], ["analytical result creation", "destination business workflow", "identity resolution"], ["activation", "audience", "suppression", "destination effect", "delivery receipt"], ["ReverseDelivery"], ["No activation occurs without purpose and destination authority.", "Retries preserve effect idempotency or require compensation."], ["prepare activation", "approve activation", "deliver activation", "recall activation"], ["activation prepared", "activation delivered", "activation recalled"], ["purpose denied", "identity unresolved", "destination effect non-idempotent", "suppression active"], ["delivery cadence", "write mode", "suppression precedence", "recall behavior"], [("ppl.delivery_guarantee", "customer_supplier"), ("gov.policy", "conformist")], ["src.asyncapi.spec", "src.cloudevents.spec", "src.delta.streaming"]),
    context("partition_exchange", "Partition and Exchange", "How is data divided, routed, shuffled, coalesced and rebalanced across parallel execution?", ["partition function", "key/range/hash semantics", "exchange kind", "skew policy", "rescaling mapping"], ["business segmentation", "storage table partition specification", "resource allocation"], ["partition", "exchange", "shuffle", "lane", "skew", "rescale"], ["PartitionPlan"], ["Equal keys route together when required.", "Rescaling declares state and ordering consequences."], ["partition stream", "repartition stream", "coalesce partitions", "rebalance partitions", "rescale mapping"], ["stream partitioned", "exchange completed", "partition skew detected", "mapping rescaled"], ["partitioner nondeterministic", "key unavailable", "skew budget exceeded", "ordering cannot survive exchange"], ["partition function", "parallelism", "exchange mode", "skew mitigation", "rescale strategy"], [("ppl.execution_plan", "customer_supplier"), ("ppl.operator_state", "partnership")], ["src.kafka.introduction", "src.beam.execution", "src.datafusion.architecture"]),
    context("event_time_progress", "Event-Time Progress", "How is completeness progress represented across out-of-order and idle inputs?", ["event-time extraction", "watermark/frontier", "idleness", "alignment", "late classification"], ["valid-time business meaning", "window aggregation", "wall-clock scheduling"], ["event time", "processing time", "watermark", "frontier", "idle input", "late element"], ["ProgressContract"], ["A watermark is a scoped progress assertion, not proof that no earlier event exists.", "Combined progress respects every non-idle input."], ["assign event time", "advance progress", "mark idle", "align inputs", "classify late element"], ["progress advanced", "input marked idle", "late element classified"], ["timestamp absent", "progress regression", "alignment buffer exceeded", "idleness unsafe"], ["timestamp source", "watermark strategy", "idle timeout", "alignment drift", "late horizon"], [("ppl.window_trigger", "supplier"), ("ppl.channel_contract", "customer_supplier")], ["src.beam.basics", "src.flink.watermarks", "src.timely.progress"]),
    context("window_trigger", "Window and Trigger", "How are unbounded observations grouped and when are provisional or final results emitted?", ["window assignment", "merge", "trigger", "pane", "accumulation", "allowed lateness"], ["event-time generation", "sink update support", "business calendar ownership"], ["window", "pane", "trigger", "accumulation", "allowed lateness", "final pane"], ["WindowingPolicy"], ["Trigger output semantics match downstream update capabilities.", "Window state has an explicit cleanup horizon."], ["assign window", "fire trigger", "merge windows", "emit pane", "close window"], ["window assigned", "trigger fired", "pane emitted", "window closed"], ["unsupported retraction", "unbounded lateness", "merge conflict", "timer domain unavailable"], ["window kind", "trigger kind", "accumulation mode", "late-data action", "cleanup time"], [("ppl.event_time_progress", "customer_supplier"), ("ppl.operator_state", "partnership")], ["src.beam.programming", "src.spark.structured_streaming", "src.flink.watermarks"]),
    context("operator_state", "Operator State", "What durable or ephemeral state does an operator own and how may it evolve?", ["state scope", "key/window association", "schema", "bound", "TTL", "checkpoint participation", "migration"], ["backend physical implementation", "source system state", "materialized output"], ["operator state", "keyed state", "operator state", "TTL", "state schema", "state migration"], ["StateContract"], ["State is bounded or rejected as unbounded.", "State restore uses compatible operator and schema identities."], ["declare state", "update state", "expire state", "snapshot state", "migrate state"], ["state declared", "state updated", "state expired", "state migrated"], ["state bound absent", "schema incompatible", "TTL violates correctness", "restore owner mismatch"], ["scope", "durability", "TTL", "backend capability", "migration", "compaction"], [("ppl.checkpoint_coordination", "customer_supplier"), ("runtime.persistence", "anti_corruption_layer")], ["src.beam.basics", "src.flink.savepoints", "src.spark.stateful"]),
    context("iterative_dataflow", "Iterative Dataflow", "How may feedback cycles execute while proving progress, termination or productive continuation?", ["feedback edge", "iteration epoch", "fixed-point criterion", "delay", "convergence", "iteration budget"], ["domain algorithm correctness", "generic graph topology", "physical scheduling"], ["feedback", "iteration", "epoch", "fixed point", "convergence", "productive cycle"], ["IterationPlan"], ["Every feedback cycle contains a progress-enabling delay or epoch boundary.", "Non-terminating flows declare productive continuation and state bounds."], ["start iteration", "feed back change", "advance epoch", "test fixed point", "terminate iteration"], ["iteration started", "epoch advanced", "fixed point reached", "iteration terminated"], ["instantaneous cycle", "non-monotone unbounded feedback", "iteration budget exhausted", "convergence unknown"], ["termination law", "maximum iterations", "tolerance", "feedback partitioning", "checkpoint epoch"], [("ppl.graph_topology", "partnership"), ("ppl.incremental_computation", "partnership")], ["src.timely.progress", "src.differential.repo", "src.dbsp.paper"]),
    context("flow_control", "Flow Control", "How does demand and capacity propagate so fast producers cannot exhaust finite consumers?", ["demand", "credits", "backpressure propagation", "buffer bound", "overflow action", "load shedding"], ["resource admission policy", "business prioritization", "transport protocol internals"], ["demand", "credit", "backpressure", "buffer", "overflow", "load shed"], ["FlowControlPolicy"], ["No component assumes infinite buffer capacity.", "Loss under overload is explicit and evidenced."], ["request capacity", "grant credit", "throttle producer", "shed load", "resume flow"], ["credit granted", "producer throttled", "load shed", "flow resumed"], ["demand protocol absent", "buffer exhausted", "loss unapproved", "deadlock risk"], ["credit unit", "buffer size", "overflow action", "fairness", "feedback latency"], [("ppl.channel_contract", "partnership"), ("runtime.resource-control", "customer_supplier")], ["src.reactive_streams.spec", "src.flink.backpressure", "src.kafka.design"]),
    context("checkpoint_coordination", "Checkpoint Coordination", "How is a recoverable cut of distributed operator and channel state established?", ["checkpoint identity", "barriers", "alignment", "state handles", "source positions", "completion", "retention"], ["state backend encoding", "business transaction", "operational savepoint migration"], ["checkpoint", "barrier", "alignment", "channel state", "state handle", "completed checkpoint"], ["Checkpoint"], ["A completed checkpoint contains a mutually consistent state and source position set.", "Only durable completion may advance recovery authority."], ["trigger checkpoint", "acknowledge barrier", "persist state", "complete checkpoint", "abort checkpoint"], ["checkpoint triggered", "barrier acknowledged", "checkpoint completed", "checkpoint aborted"], ["barrier timeout", "state persistence failed", "concurrent checkpoint forbidden", "source position unavailable"], ["aligned or unaligned", "interval", "timeout", "concurrency", "retention", "incremental state"], [("ppl.operator_state", "customer_supplier"), ("ppl.delivery_guarantee", "partnership")], ["src.chandy_lamport.paper", "src.flink.checkpointing", "src.flink.backpressure"]),
    context("delivery_guarantee", "Delivery Guarantee", "What end-to-end multiplicity, ordering, visibility and durability can be proven for observable effects?", ["guarantee claim", "source replay premise", "state recovery premise", "sink effect premise", "proof composition"], ["transport marketing label", "business correctness", "sink implementation"], ["at-most-once", "at-least-once", "effectively-once", "exactly-once effect", "visibility", "finality"], ["DeliveryGuarantee"], ["No component-local guarantee is promoted to end-to-end.", "Guarantee scope names failure model and observation boundary."], ["declare guarantee", "compose guarantee", "verify premise", "publish guarantee"], ["guarantee declared", "premise verified", "guarantee published"], ["source not replayable", "sink neither transactional nor idempotent", "failure model unspecified", "ack boundary ambiguous"], ["multiplicity", "ordering scope", "visibility", "durability", "atomicity", "failure model"], [("ppl.sink_commit", "partnership"), ("ppl.checkpoint_coordination", "partnership")], ["src.flink.fault_tolerance", "src.spark.structured_streaming", "src.kafka.design"]),
    context("sink_commit", "Sink Commit", "How are staged outputs validated, atomically made visible, aborted or compensated?", ["write staging", "prepare", "validation", "commit", "abort", "visibility and durability receipt"], ["upstream computation", "sink storage internals", "business approval"], ["staged write", "prepare", "commit token", "abort", "visibility", "durability"], ["SinkTransaction"], ["A commit token is single-use within its idempotency scope.", "Visibility is not claimed before the sink confirms it."], ["stage write", "validate staged write", "prepare commit", "commit write", "abort write"], ["write staged", "commit prepared", "write committed", "write aborted"], ["commit conflict", "validation failed", "indeterminate commit", "durability unconfirmed"], ["commit protocol", "atomicity scope", "idempotency key", "visibility check", "abort cleanup"], [("ppl.delivery_guarantee", "partnership"), ("storage.transaction", "anti_corruption_layer")], ["src.delta.streaming", "src.iceberg.spec", "src.hudi.timeline"]),
    context("orchestration_control", "Orchestration Control", "When are units of work ready, admitted and coordinated across dependency and policy boundaries?", ["readiness", "dependency outcomes", "branching", "join rules", "external waits", "run coordination"], ["record-level data exchange", "task implementation", "resource scheduler internals"], ["readiness", "dependency", "trigger rule", "wait", "branch", "join"], ["OrchestrationRun"], ["A task starts only after all declared readiness predicates resolve.", "Skipped, failed and absent dependencies are distinct."], ["evaluate readiness", "admit task", "wait for signal", "branch run", "join branches"], ["task became ready", "task admitted", "external signal observed", "branches joined"], ["dependency unresolved", "trigger rule ambiguous", "external signal expired", "join impossible"], ["trigger rule", "branch predicate", "join predicate", "priority", "concurrency"], [("ppl.schedule_trigger", "partnership"), ("ppl.task_attempt", "customer_supplier")], ["src.airflow.dag", "src.serverless_workflow.spec", "src.argo.dag"]),
    context("schedule_trigger", "Schedule and Trigger", "Which temporal, event, materialization or manual condition requests a run for a declared data cut?", ["cron/recurrence", "calendar", "time zone", "event trigger", "materialization trigger", "misfire", "debounce"], ["run admission", "data-cut closure", "business calendar definition"], ["schedule", "trigger", "misfire", "catch-up", "debounce", "logical time"], ["TriggerDefinition"], ["A trigger request identifies intended logical time separately from observation time.", "Time-zone and daylight-saving behavior is explicit."], ["register trigger", "evaluate trigger", "emit run request", "suppress duplicate trigger"], ["trigger registered", "trigger matched", "run requested", "duplicate suppressed"], ["calendar unresolved", "misfire policy absent", "event identity missing", "trigger storm budget exceeded"], ["trigger kind", "time zone", "misfire", "catch-up", "debounce", "event coalescing"], [("ppl.data_cut", "customer_supplier"), ("ppl.orchestration_control", "supplier")], ["src.rfc5545", "src.airflow.data_aware", "src.kubernetes.cronjob"]),
    context("execution_plan", "Compiled Execution Plan", "How is a valid logical graph lowered into a target-qualified executable graph without changing meaning?", ["physical operators", "exchange", "fusion", "placement requirements", "artifacts", "decision trace"], ["logical semantic ownership", "actual deployment", "run state"], ["compiled plan", "physical operator", "stage", "exchange", "fusion", "lowering witness"], ["CompiledPlan"], ["Every physical fragment traces to logical meaning.", "Every semantics-changing optimization is refused."], ["lower logical graph", "select physical operator", "fuse stages", "insert exchange", "publish plan"], ["logical graph lowered", "operator selected", "plan published"], ["no compatible operator", "unsafe rewrite", "target capability missing", "resource estimate infeasible"], ["operator implementation", "fusion", "exchange", "parallelism", "state backend", "codegen"], [("ppl.deployment_binding", "customer_supplier"), ("runtime.compute", "anti_corruption_layer")], ["src.substrait.basics", "src.datafusion.architecture", "src.beam.execution"]),
    context("deployment_binding", "Deployment Binding", "Which immutable plan and artifacts are bound to which qualified runtime targets and operating configuration?", ["plan edition", "artifact digests", "target profile", "provider binding", "secrets references", "rollout policy"], ["secret values", "plan semantics", "runtime attempts"], ["deployment", "target", "artifact", "binding", "rollout", "qualification"], ["PipelineDeployment"], ["A deployment pins exact plan and artifact identities.", "Secrets are referenced, never embedded in the definition."], ["create deployment", "qualify target", "bind artifact", "activate deployment", "retire deployment"], ["deployment created", "target qualified", "deployment activated", "deployment retired"], ["target unqualified", "artifact digest mismatch", "secret reference unresolved", "rollout unsafe"], ["target", "artifact", "secret binding", "rollout strategy", "placement", "autoscaling"], [("ppl.pipeline_run", "supplier"), ("runtime.deployment", "anti_corruption_layer")], ["src.prefect.deployments", "src.kubernetes.job", "src.oci.image_spec"]),
    context("pipeline_run", "Pipeline Run", "What happened during one admitted execution of one deployment over one data cut?", ["run identity", "deployment reference", "data cut", "run lifecycle", "task set", "outcome"], ["reusable definition", "individual task-attempt internals", "output semantic ownership"], ["run", "run request", "admission", "start", "outcome", "logical time"], ["PipelineRun"], ["One run pins one deployment edition and one data cut.", "Terminal outcome cannot be rewritten; correction creates a new event or run."], ["request run", "admit run", "start run", "pause run", "complete run", "abort run"], ["run requested", "run admitted", "run started", "run paused", "run completed", "run aborted"], ["deployment inactive", "data cut invalid", "admission denied", "terminal run mutation"], ["run reason", "priority", "parameter binding", "deadline", "failure aggregation"], [("ppl.task_attempt", "customer_supplier"), ("ppl.materialization", "customer_supplier")], ["src.openlineage.spec", "src.airflow.dag", "src.prefect.flows"]),
    context("task_attempt", "Task Attempt", "What happened during one attempt to execute one physical task within one run?", ["attempt number", "worker lease", "heartbeat", "input bindings", "effect boundary", "outcome"], ["logical node", "global retry decision", "worker implementation"], ["task", "attempt", "lease", "heartbeat", "outcome", "orphan"], ["TaskAttempt"], ["Attempt identity never changes across heartbeat updates.", "Late completion from a revoked lease cannot commit effects."], ["lease task", "start attempt", "heartbeat attempt", "complete attempt", "revoke lease"], ["task leased", "attempt started", "heartbeat recorded", "attempt completed", "lease revoked"], ["lease expired", "stale worker", "input unavailable", "effect commit indeterminate"], ["lease duration", "heartbeat interval", "attempt timeout", "speculation", "worker isolation"], [("ppl.retry", "customer_supplier"), ("runtime.worker", "anti_corruption_layer")], ["src.airflow.tasks", "src.kubernetes.job", "src.opentelemetry.trace"]),
    context("materialization", "Materialization", "Which named output state was produced, committed, qualified and made visible?", ["materialization identity", "asset/object identity", "data cut", "content/version identity", "commit and quality receipts"], ["logical transformation", "storage format implementation", "consumer use"], ["materialization", "version", "content identity", "publication", "freshness", "qualification"], ["Materialization"], ["A published materialization references a successful commit and applicable gates.", "Overwrite does not erase prior lineage evidence."], ["register materialization", "qualify materialization", "publish materialization", "supersede materialization", "recall materialization"], ["materialization registered", "materialization qualified", "materialization published", "materialization recalled"], ["commit absent", "quality gate failed", "content identity unavailable", "publication unauthorized"], ["identity scheme", "version semantics", "publication gate", "freshness", "retention"], [("ppl.quality_gate", "customer_supplier"), ("ppl.lineage_receipt", "partnership")], ["src.openlineage.spec", "src.iceberg.spec", "src.dagster.assets"]),
    context("replay", "Replay", "How is retained input re-consumed from a declared position while preserving or intentionally revising semantics?", ["replay request", "position range", "definition/plan edition", "duplicate disposition", "comparison"], ["source retention", "backfill selection", "incident policy"], ["replay", "replay range", "historical plan", "duplicate disposition", "comparison run"], ["ReplayProcess"], ["Replay declares whether historical or current semantics apply.", "Original evidence remains immutable."], ["request replay", "validate retention", "start replay", "compare replay", "complete replay"], ["replay requested", "retention validated", "replay completed"], ["input expired", "historical artifact unavailable", "duplicate effect unsafe", "semantic edition ambiguous"], ["semantic edition", "output namespace", "duplicate handling", "rate", "comparison"], [("ppl.backfill", "partnership"), ("ppl.data_cut", "customer_supplier")], ["src.kafka.introduction", "src.temporal.platform", "src.openlineage.spec"]),
    context("backfill", "Backfill", "How is missing or revised historical coverage planned, ordered and reconciled across data cuts?", ["target coverage", "cut enumeration", "reprocessing rule", "run ordering", "concurrency", "reconciliation"], ["single replay execution", "calendar ownership", "transformation definition"], ["backfill", "coverage", "missing cut", "reprocessing", "run ordering", "catch-up"], ["BackfillCampaign"], ["Every target cut has an explicit existing-materialization disposition.", "Backfill cannot silently mix incompatible definition editions."], ["plan backfill", "approve backfill", "launch cut", "pause campaign", "reconcile campaign"], ["backfill planned", "cut launched", "campaign reconciled"], ["coverage ambiguous", "existing output disposition absent", "resource budget exceeded", "source retention gap"], ["reprocessing rule", "ordering", "concurrency", "edition pin", "publish strategy"], [("ppl.replay", "partnership"), ("ppl.schedule_trigger", "customer_supplier")], ["src.airflow.backfill", "src.dagster.backfills", "src.dbt.incremental"]),
    context("retry", "Retry", "When may a failed or uncertain attempt be repeated without violating effect and budget laws?", ["retry classification", "attempt budget", "delay/backoff", "jitter", "effect safety", "exhaustion"], ["domain-specific failure meaning", "compensation implementation", "worker scheduling"], ["retry", "attempt budget", "backoff", "jitter", "retryable failure", "exhaustion"], ["RetryPolicy"], ["Non-retryable failures are never retried.", "Effectful retry requires idempotency, transaction fencing or compensation."], ["classify failure", "schedule retry", "consume attempt", "exhaust retry"], ["failure classified", "retry scheduled", "attempt consumed", "retry exhausted"], ["failure unclassified", "attempt budget exhausted", "effect safety unproven", "deadline exceeded"], ["retry set", "max attempts", "backoff", "jitter", "deadline", "budget"], [("ppl.task_attempt", "supplier"), ("ppl.compensation", "customer_supplier")], ["src.temporal.retry", "src.argo.retry", "src.prefect.tasks"]),
    context("compensation", "Compensation", "How are committed effects semantically counteracted when atomic rollback is impossible?", ["compensation registration", "dependency order", "eligibility", "execution", "residual harm"], ["database rollback", "business remedy ownership", "retry classification"], ["compensation", "forward action", "counteraction", "irreversible effect", "residual"], ["CompensationProcess"], ["Compensation never claims erasure of a historical effect.", "Reverse order is used only when dependency semantics require it."], ["register compensation", "request compensation", "execute compensation", "record residual"], ["compensation registered", "compensation executed", "residual recorded"], ["effect irreversible", "compensation precondition absent", "counteraction failed", "authority denied"], ["trigger", "ordering", "best-effort or required", "retry", "human escalation"], [("ppl.retry", "partnership"), ("domain.remedy", "customer_supplier")], ["src.sagas.paper", "src.serverless_workflow.spec", "src.temporal.platform"]),
    context("cancellation", "Cancellation and Timeout", "How does stop intent propagate and what happens to in-flight work, state and effects?", ["cancel scope", "propagation", "cooperation", "force termination", "cleanup", "partial output disposition"], ["operating-system signal mechanics", "compensation semantics", "business authorization"], ["cancellation", "timeout", "deadline", "propagation", "cleanup", "abandonment"], ["CancellationProcess"], ["Cancellation has a terminal disposition for every admitted effect.", "Timeout and explicit cancellation remain distinguishable."], ["request cancellation", "propagate cancellation", "force terminate", "clean up", "complete cancellation"], ["cancellation requested", "cancellation propagated", "work terminated", "cleanup completed"], ["cancellation forbidden", "worker unresponsive", "effect indeterminate", "cleanup failed"], ["scope", "grace period", "propagation", "force policy", "partial output", "compensation"], [("ppl.task_attempt", "customer_supplier"), ("ppl.compensation", "partnership")], ["src.temporal.cancellation", "src.serverless_workflow.spec", "src.beam.execution"]),
    context("pipeline_change", "Pipeline Change and Rollout", "How do definition, plan, state and output editions coexist and migrate safely?", ["semantic diff", "state compatibility", "dual run", "canary", "cutover", "rollback/roll-forward", "in-flight disposition"], ["source schema ownership", "generic software delivery", "business approval"], ["semantic diff", "state migration", "dual run", "canary", "cutover", "in-flight work"], ["PipelineChange"], ["A change cannot reuse an identity when compatibility is false.", "In-flight work disposition is explicit before activation."], ["propose change", "classify compatibility", "migrate state", "start canary", "cut over", "retire edition"], ["change proposed", "compatibility classified", "canary started", "cutover completed"], ["state incompatible", "historical artifact missing", "canary divergence", "rollback impossible"], ["compatibility", "migration", "rollout", "comparison", "in-flight disposition", "decommission"], [("ppl.deployment_binding", "customer_supplier"), ("ppl.operator_state", "partnership")], ["src.flink.savepoints", "src.iceberg.branching", "src.oci.image_spec"]),
    context("maintenance", "Pipeline Maintenance", "Which recurring operations preserve pipeline, state, checkpoint and materialization health?", ["checkpoint cleanup", "state compaction", "offset retention", "small-file/table service trigger", "orphan cleanup", "maintenance receipts"], ["storage engine internal maintenance", "business retention policy", "incident response"], ["maintenance", "compaction", "vacuum", "checkpoint cleanup", "orphan", "retention horizon"], ["MaintenancePlan"], ["Maintenance never removes data or state still required for replay, recovery or audit.", "Every destructive action has a resolved retention proof."], ["plan maintenance", "qualify deletion", "compact state", "expire checkpoint", "clean orphan"], ["maintenance planned", "deletion qualified", "state compacted", "orphan cleaned"], ["retention proof absent", "active reference exists", "maintenance conflicts with run", "cleanup incomplete"], ["cadence", "retention", "compaction threshold", "conflict policy", "budget"], [("ppl.replay", "customer_supplier"), ("storage.maintenance", "anti_corruption_layer")], ["src.flink.savepoints", "src.hudi.timeline", "src.iceberg.branching"]),
    context("lineage_receipt", "Pipeline Lineage and Receipts", "What prospective and observed evidence connects inputs, activities, agents, attempts and outputs?", ["declared lineage", "observed lineage", "input/output identities", "activity and agent", "receipt scope", "signing"], ["general provenance ontology", "telemetry storage", "business evidence evaluation"], ["declared lineage", "observed lineage", "derivation", "activity", "agent", "receipt"], ["LineageReceipt"], ["Observed lineage never fabricates unobserved inputs.", "Receipt scope states exactly what was measured or asserted."], ["declare lineage", "observe lineage", "emit receipt", "sign receipt", "recall assertion"], ["lineage declared", "lineage observed", "receipt emitted", "assertion recalled"], ["identity unresolved", "observation incomplete", "signature invalid", "prospective and observed conflict"], ["granularity", "column lineage", "receipt signing", "redaction", "retention"], [("ppl.materialization", "partnership"), ("prov.provenance", "conformist")], ["src.openlineage.spec", "src.w3c.prov_o", "src.cloudevents.spec"]),
    context("observability", "Pipeline Observability", "Which runtime signals make progress, health, cost and failure diagnosable without becoming semantic truth?", ["metrics", "logs", "traces", "progress", "lag", "correlation", "alert evidence"], ["business correctness", "lineage ownership", "incident process"], ["metric", "log", "span", "link", "lag", "health", "alert"], ["ObservabilityContract"], ["Telemetry identity correlates to run and attempt identities.", "Absence of an alert is not proof of correctness."], ["emit metric", "record span", "record log", "measure lag", "raise alert"], ["metric emitted", "span recorded", "lag measured", "alert raised"], ["correlation absent", "cardinality budget exceeded", "clock uncertainty excessive", "signal dropped"], ["sampling", "retention", "cardinality", "redaction", "alert threshold", "clock"], [("ppl.lineage_receipt", "partnership"), ("ops.observability", "conformist")], ["src.opentelemetry.trace", "src.openlineage.spec", "src.flink.backpressure"]),
    context("quality_gate", "Pipeline Quality Gate", "Which validations block, quarantine, warn or permit a materialization or downstream run?", ["check definition", "scope", "severity", "evaluation", "gate action", "waiver"], ["quality rule business ownership", "profiling algorithm internals", "materialization storage"], ["check", "assertion", "severity", "gate", "quarantine", "waiver"], ["QualityGate"], ["A blocking failure cannot publish without an authorized, scoped waiver.", "Check evidence binds to the exact data cut and materialization."], ["define check", "evaluate check", "apply gate", "grant waiver", "quarantine output"], ["check evaluated", "gate blocked", "waiver granted", "output quarantined"], ["check unavailable", "evidence stale", "waiver unauthorized", "scope mismatch"], ["severity", "blocking policy", "sampling", "waiver", "quarantine", "downstream propagation"], [("ppl.materialization", "supplier"), ("quality.data-quality", "customer_supplier")], ["src.dagster.asset_checks", "src.openlineage.spec", "src.open_data_contract"]),
]


def decision(decision_id: str, owner: str, question: str, phase: str, values: list[str], consequences: list[str]) -> dict:
    return {
        "decision_id": f"decision.pipeline.{decision_id}",
        "edition": EDITION,
        "status": "sourced_candidate",
        "owner_context": owner,
        "question": question,
        "binding_phase": phase,
        "allowed_value_kinds": values,
        "default_law": "No hidden default. Omission is a typed unresolved-decision gap unless an applicable policy supplies a recorded value.",
        "authority_required": "pipeline design authority or policy named by the intent",
        "consequences": consequences,
        "evidence_required": ["decision trace", "compatibility proof", "applicable provider capability evidence"],
    }


DECISION_SEEDS = [
    ("topology_kind", "ppl.graph_topology", "Which topology class is intended?", "logical", ["dag", "feedback_cycle", "dynamic_graph", "nested_graph"], ["Changes validation and scheduling laws."]),
    ("execution_mode", "ppl.pipeline_definition", "How is input admitted over time?", "logical", ["bounded_batch", "microbatch", "continuous_stream", "incremental_triggered", "interactive"], ["Changes progress, latency, recovery and state requirements."]),
    ("cycle_law", "ppl.iterative_dataflow", "What makes each cycle lawful?", "logical", ["fixed_point", "finite_iteration", "productive_continuation", "eventual_quiescence"], ["Determines termination and resource proof obligations."]),
    ("dynamic_expansion", "ppl.graph_topology", "May runtime data create new task instances or graph nodes?", "logical", ["forbidden", "finite_static_map", "bounded_dynamic_map", "provider_dynamic"], ["Changes reproducibility and scheduling bounds."]),
    ("port_update_model", "ppl.port_contract", "Which updates may a port carry?", "logical", ["snapshot", "append", "upsert", "retract", "full_changelog"], ["Constrains compatible operators and sinks."]),
    ("port_boundedness", "ppl.port_contract", "Is the collection bounded?", "logical", ["bounded", "unbounded", "bounded_per_cut", "unknown_refused"], ["Determines need for progress and state cleanup."]),
    ("schema_compatibility", "ppl.port_contract", "Which schema evolution relation is accepted?", "logical", ["exact", "backward", "forward", "full", "explicit_transform"], ["Controls plan validity across editions."]),
    ("null_missing", "ppl.port_contract", "How do null, missing and absent differ?", "logical", ["distinct", "coalesced_with_loss", "forbidden"], ["Affects equality, filters and joins."]),
    ("ordering_scope", "ppl.channel_contract", "What ordering must be preserved?", "logical", ["none", "per_key", "per_partition", "total", "causal"], ["May require serialization or constrain repartitioning."]),
    ("channel_capacity", "ppl.channel_contract", "What is the maximum in-flight channel capacity?", "physical", ["bytes", "records", "both", "provider_bound"], ["Controls overload and checkpoint channel state."]),
    ("push_pull", "ppl.channel_contract", "Who controls demand?", "physical", ["push", "pull", "credit_based", "hybrid"], ["Selects flow-control protocol."]),
    ("overflow_action", "ppl.flow_control", "What happens when capacity is exhausted?", "operations", ["block", "backpressure", "spill", "drop_new", "drop_old", "sample", "fail"], ["May cause information loss or latency."]),
    ("ingestion_mode", "ppl.ingestion_contract", "How is the source observed?", "logical", ["snapshot", "incremental_poll", "log_cdc", "event_subscription", "bulk_export", "federated_query"], ["Changes cut and recovery semantics."]),
    ("read_consistency", "ppl.ingestion_contract", "Which source read consistency is required?", "logical", ["linearizable", "serializable", "snapshot", "repeatable_read", "read_committed", "eventual", "best_effort"], ["Determines whether a closed data cut can be proven."]),
    ("cursor_commit_boundary", "ppl.ingestion_contract", "When may a durable source cursor advance?", "physical", ["after_read", "after_transform", "after_sink_prepare", "after_sink_commit", "external_transaction"], ["Controls duplicates and loss after recovery."]),
    ("snapshot_change_strategy", "ppl.snapshot_change_handoff", "How is baseline plus concurrent change reconciled?", "logical", ["locked_snapshot", "consistent_log_position", "watermark_windows", "dual_read_compare", "provider_native"], ["Determines gap and overlap proof."]),
    ("snapshot_chunk_key", "ppl.snapshot_change_handoff", "Which total ordering divides snapshot chunks?", "physical", ["primary_key", "unique_key", "synthetic_range", "provider_partition"], ["Controls resumability and overlap resolution."]),
    ("transport_protocol", "ppl.transport_contract", "Which protocol transports the carrier?", "physical", ["message_log", "queue", "rpc", "file_object", "shared_memory", "database_protocol"], ["Changes acknowledgement, ordering and failure behavior."]),
    ("serialization", "ppl.transport_contract", "Which exact encoding and schema edition crosses the boundary?", "physical", ["arrow", "avro", "protobuf", "json", "parquet", "orc", "opaque_registered"], ["Controls interoperability and evolution."]),
    ("compression", "ppl.transport_contract", "Where and how is data compressed?", "physical", ["none", "frame", "batch", "file", "column", "adaptive"], ["Trades CPU, latency, memory, network and splittability."]),
    ("encryption", "ppl.transport_contract", "Which boundary applies encryption?", "assurance", ["transport", "payload", "field", "storage", "multiple"], ["Changes pushdown and inspection capability."]),
    ("batching", "ppl.transport_contract", "How are elements coalesced for transport or execution?", "physical", ["count", "bytes", "time", "adaptive", "none"], ["Trades latency, throughput and retry granularity."]),
    ("partition_function", "ppl.partition_exchange", "How is data assigned to parallel lanes?", "logical", ["hash", "range", "round_robin", "broadcast", "singleton", "custom_proven"], ["Affects ordering, skew and keyed state."]),
    ("parallelism", "ppl.partition_exchange", "What parallelism and rescaling range apply?", "physical", ["fixed", "bounded_auto", "data_dependent_bounded"], ["Controls cost, throughput and state redistribution."]),
    ("exchange_mode", "ppl.partition_exchange", "How does an exchange materialize or pipeline data?", "physical", ["pipelined", "blocking", "hybrid", "remote_shuffle"], ["Changes latency, recovery and storage."]),
    ("skew_mitigation", "ppl.partition_exchange", "How are hot partitions handled?", "physical", ["none", "salting", "adaptive_split", "broadcast_small_side", "custom"], ["May change aggregation and join plan."]),
    ("event_timestamp", "ppl.event_time_progress", "Which field or function owns event time?", "logical", ["source_field", "metadata", "derived", "processing_time"], ["Determines window and lateness semantics."]),
    ("watermark_strategy", "ppl.event_time_progress", "How is event-time progress estimated?", "logical", ["monotonic", "bounded_out_of_order", "source_supplied", "punctuated", "manual_frontier"], ["Controls result timing and state cleanup."]),
    ("idle_input", "ppl.event_time_progress", "When may an input stop constraining progress?", "operations", ["never", "timeout", "source_signal", "partition_lease"], ["Unsafe idleness can omit late records."]),
    ("watermark_alignment", "ppl.event_time_progress", "May fast inputs be throttled to slow input progress?", "physical", ["none", "max_drift", "strict_barrier"], ["Trades buffer size and throughput."]),
    ("late_data", "ppl.window_trigger", "What happens after event-time progress passes an element?", "logical", ["drop_with_receipt", "side_output", "update", "retract_and_update", "reopen_window", "fail"], ["Changes correctness and downstream update requirements."]),
    ("window_kind", "ppl.window_trigger", "How are unbounded observations grouped?", "logical", ["tumbling", "sliding", "session", "global", "calendar", "custom"], ["Determines state keys and merge laws."]),
    ("trigger_kind", "ppl.window_trigger", "When are panes emitted?", "logical", ["event_time", "processing_time", "count", "data_driven", "composite"], ["Controls provisional/final result behavior."]),
    ("accumulation_mode", "ppl.window_trigger", "How do successive panes relate?", "logical", ["discarding", "accumulating", "accumulating_and_retracting"], ["Constrains downstream effect model."]),
    ("state_scope", "ppl.operator_state", "To what identity is state scoped?", "logical", ["key", "key_window", "operator", "partition", "run", "global"], ["Determines access and redistribution laws."]),
    ("state_bound", "ppl.operator_state", "What proves state remains finite?", "logical", ["ttl", "window_close", "key_cardinality_budget", "compaction_frontier", "finite_input", "explicit_unbounded_refusal"], ["Required for resource feasibility."]),
    ("state_durability", "ppl.operator_state", "Which state must survive which failures?", "assurance", ["ephemeral", "attempt", "worker", "run", "deployment", "cross_region"], ["Selects backend and checkpoint obligations."]),
    ("state_backend", "ppl.operator_state", "Which qualified backend offer stores state?", "physical", ["memory", "local_embedded", "remote_disaggregated", "database", "custom_offer"], ["Changes latency, restore and cost."]),
    ("state_ttl", "ppl.operator_state", "When may state expire?", "logical", ["event_time", "processing_time", "valid_time", "explicit_signal", "never_with_bound"], ["May change results if chosen incorrectly."]),
    ("state_migration", "ppl.pipeline_change", "How does state cross plan editions?", "operations", ["compatible_reuse", "upcast", "offline_transform", "dual_state", "discard_with_approval"], ["Controls upgrade safety and history."]),
    ("checkpoint_mode", "ppl.checkpoint_coordination", "How are channel and operator state coordinated?", "physical", ["aligned", "unaligned", "at_least_once", "provider_atomic"], ["Trades checkpoint latency, channel state and ordering behavior."]),
    ("checkpoint_cadence", "ppl.checkpoint_coordination", "When are recovery points attempted?", "operations", ["interval", "record_count", "data_volume", "adaptive", "external_barrier"], ["Trades recovery loss window and overhead."]),
    ("checkpoint_retention", "ppl.checkpoint_coordination", "Which completed recovery points remain authoritative?", "operations", ["last_n", "age", "milestone", "externalized", "policy_composite"], ["Controls restore options and cost."]),
    ("delivery_multiplicity", "ppl.delivery_guarantee", "What observable effect multiplicity is required?", "assurance", ["at_most_once", "at_least_once", "effectively_once", "exactly_once_effect"], ["Determines source, checkpoint and sink requirements."]),
    ("delivery_order", "ppl.delivery_guarantee", "Within what scope must effects be ordered?", "assurance", ["none", "per_key", "per_partition", "transaction", "total"], ["May limit parallelism and retry."]),
    ("atomicity_scope", "ppl.sink_commit", "Which writes become visible atomically?", "logical", ["record", "batch", "partition", "table", "multi_table", "custom_transaction"], ["Determines commit coordinator requirements."]),
    ("sink_idempotency", "ppl.sink_commit", "How are repeated effect attempts recognized?", "logical", ["natural_key", "idempotency_key", "transaction_token", "commutative_effect", "not_idempotent"], ["Controls retry safety."]),
    ("visibility_check", "ppl.sink_commit", "How is committed output visibility confirmed?", "operations", ["commit_ack", "read_after_write", "catalog_snapshot", "external_receipt"], ["Separates acceptance from durable visibility."]),
    ("retry_classification", "ppl.retry", "Which outcomes may be retried?", "logical", ["explicit_allowlist", "explicit_denylist_with_default_retry", "policy_expression"], ["Prevents retrying permanent or unsafe failures."]),
    ("retry_backoff", "ppl.retry", "How are retries delayed?", "operations", ["constant", "linear", "exponential", "server_advised", "adaptive"], ["Changes load and recovery latency."]),
    ("retry_budget", "ppl.retry", "What finite retry budget applies?", "operations", ["attempts", "elapsed_time", "cost", "composite"], ["Prevents infinite work and cascading overload."]),
    ("timeout", "ppl.cancellation", "Which deadline terminates or escalates work?", "operations", ["attempt", "task", "run", "external_call", "idle"], ["Determines cancellation scope and retry classification."]),
    ("cancellation", "ppl.cancellation", "How is cancellation propagated and enforced?", "operations", ["cooperative", "wait_for_completion", "abandon", "force_after_grace"], ["Controls partial effects and cleanup."]),
    ("compensation", "ppl.compensation", "Which committed effects require counteractions?", "logical", ["none_atomic", "registered_reverse", "registered_dependency_order", "human_remedy"], ["Determines recovery for non-atomic workflows."]),
    ("trigger_type", "ppl.schedule_trigger", "What requests a run?", "logical", ["manual", "recurrence", "event", "materialization", "condition", "continuous"], ["Changes logical-time and deduplication rules."]),
    ("misfire", "ppl.schedule_trigger", "What happens to a missed temporal trigger?", "operations", ["skip", "fire_once", "catch_up_all", "bounded_catch_up", "fail"], ["Controls historical coverage and bursts."]),
    ("trigger_coalescing", "ppl.schedule_trigger", "How are multiple triggering observations combined?", "logical", ["none", "debounce", "window", "all_of", "any_of", "latest_only"], ["Defines run count and data cut."]),
    ("run_concurrency", "ppl.orchestration_control", "How many overlapping runs or tasks are admitted?", "operations", ["forbid_overlap", "bounded", "replace_previous", "queue", "unbounded_refused"], ["Controls races, freshness and cost."]),
    ("dependency_outcome", "ppl.orchestration_control", "Which upstream outcomes satisfy readiness?", "logical", ["all_success", "all_done", "any_success", "none_failed", "custom_total_predicate"], ["Controls branching and failure aggregation."]),
    ("data_cut_closure", "ppl.data_cut", "How does an input selection become closed?", "logical", ["snapshot_id", "offset_range", "event_time_frontier", "partition_set", "manifest", "external_attestation"], ["Required for reproducibility."]),
    ("replay_semantics", "ppl.replay", "Which semantic edition interprets historical input?", "logical", ["historical", "current", "both_compare", "explicit_edition"], ["Determines whether output is correction or reproduction."]),
    ("backfill_reprocessing", "ppl.backfill", "How are existing runs/materializations treated?", "operations", ["missing_only", "failed_only", "all", "compare_only", "supersede_after_gate"], ["Prevents silent duplicate publication."]),
    ("backfill_order", "ppl.backfill", "In what order are cuts processed?", "operations", ["oldest_first", "newest_first", "dependency_order", "priority", "parallel_bounded"], ["Affects incremental dependencies and freshness."]),
    ("artifact_binding", "ppl.deployment_binding", "How are executable artifacts identified?", "physical", ["content_digest", "signed_digest", "reproducible_build_record"], ["Controls deployment reproducibility and supply-chain assurance."]),
    ("target_placement", "ppl.deployment_binding", "Which qualified target receives each physical stage?", "physical", ["fixed", "constraint_based", "cost_optimized", "data_locality", "policy_selected"], ["Changes latency, residency and cost."]),
    ("rollout", "ppl.pipeline_change", "How does a new deployment edition become active?", "operations", ["replace", "canary", "blue_green", "parallel_compare", "partitioned_rollout"], ["Controls blast radius and in-flight work."]),
    ("materialization_publication", "ppl.materialization", "When is an output visible to consumers?", "assurance", ["on_commit", "after_quality", "after_approval", "scheduled_release", "branch_fast_forward"], ["Separates production from publication."]),
    ("quality_gate_action", "ppl.quality_gate", "What follows each check severity and outcome?", "assurance", ["observe", "warn", "quarantine", "block", "rollback", "require_waiver"], ["Controls bad-data propagation."]),
    ("lineage_granularity", "ppl.lineage_receipt", "At what granularity is derivation observed?", "assurance", ["pipeline", "run", "task", "dataset", "partition", "column", "record_sample"], ["Trades evidence coverage, cost and privacy."]),
    ("telemetry_sampling", "ppl.observability", "Which runtime signals are retained?", "operations", ["all", "head", "tail", "probabilistic", "adaptive", "policy_filtered"], ["Controls cost and diagnostic completeness."]),
    ("maintenance_retention", "ppl.maintenance", "When may checkpoints, offsets, state and artifacts be removed?", "operations", ["age", "count", "reference_reachability", "legal_policy", "composite"], ["May destroy replay or recovery ability."]),
]

DECISIONS = [decision(*seed) for seed in DECISION_SEEDS]


def failure(code: str, owner: str, phase: str, kind: str, meaning: str, next_actions: list[str]) -> dict:
    return {
        "outcome_id": f"pipeline.outcome.{code}",
        "edition": EDITION,
        "owner_context": owner,
        "phase": phase,
        "kind": kind,
        "meaning": meaning,
        "retry_class": "unclassified_until_policy",
        "effect_disposition_required": kind == "failure",
        "allowed_next_actions": next_actions,
        "llm_dependency": "none",
    }


FAILURES = [
    failure("invalid_state_transition", "ppl.orchestration_control", "any", "refusal", "The requested command is not legal in the aggregate's current state.", ["inspect lifecycle", "issue a legal command", "create a new aggregate when history is immutable"]),
    failure("definition_reference_unresolved", "ppl.pipeline_definition", "compile", "refusal", "A referenced semantic or contract edition does not resolve.", ["supply exact edition", "declare compiler gap"]),
    failure("graph_cycle_unlawful", "ppl.graph_topology", "compile", "refusal", "A cycle lacks delay, progress or termination/productivity law.", ["declare cycle law", "break cycle"]),
    failure("port_incompatible", "ppl.port_contract", "compile", "refusal", "Connected ports differ in an unadapted carrier, update, time, order or cardinality dimension.", ["bind proved adapter", "revise port"]),
    failure("state_unbounded", "ppl.operator_state", "compile", "refusal", "State has neither a finite bound nor an explicit approved unbounded posture.", ["supply bound", "reject design"]),
    failure("progress_undefined", "ppl.event_time_progress", "compile", "refusal", "An unbounded computation lacks progress semantics.", ["define frontier/watermark", "change to bounded cut"]),
    failure("retractions_unsupported", "ppl.port_contract", "compile", "refusal", "Downstream port or sink cannot represent required corrections.", ["bind retract-capable sink", "select approved loss policy"]),
    failure("source_not_replayable", "ppl.delivery_guarantee", "bind", "refusal", "Required recovery guarantee assumes replay that the source cannot provide.", ["weaken guarantee", "add durable ingress log"]),
    failure("sink_effect_unsafe", "ppl.sink_commit", "bind", "refusal", "Retryable execution targets a sink without transaction, idempotency or compensation.", ["bind safer sink", "provide idempotency key", "disable retry"]),
    failure("exactly_once_unproven", "ppl.delivery_guarantee", "bind", "refusal", "One or more end-to-end delivery premises are absent.", ["complete proof chain", "publish narrower guarantee"]),
    failure("target_unqualified", "ppl.deployment_binding", "bind", "refusal", "Target capability or current conformance evidence is insufficient.", ["qualify target", "select another offer"]),
    failure("resource_plan_infeasible", "ppl.execution_plan", "bind", "refusal", "Finite resource, SLO or cost constraints cannot be met.", ["revise plan", "increase authorized budget"]),
    failure("source_retention_gap", "ppl.data_cut", "pre_run", "refusal", "Requested offset, snapshot or history has expired.", ["record permanent gap", "use alternate authoritative source"]),
    failure("cut_not_closed", "ppl.data_cut", "pre_run", "refusal", "Input boundaries do not form a reproducible closed cut.", ["wait for closure", "supply explicit open-ended semantics"]),
    failure("schedule_ambiguous", "ppl.schedule_trigger", "pre_run", "refusal", "Time zone, recurrence, exclusion or misfire behavior is unresolved.", ["resolve calendar semantics"]),
    failure("duplicate_run_request", "ppl.pipeline_run", "admission", "refusal", "The request duplicates an existing idempotency scope.", ["return existing run identity", "use new authorized request key"]),
    failure("concurrency_denied", "ppl.orchestration_control", "admission", "refusal", "Run or task concurrency policy denies admission.", ["queue", "cancel predecessor", "request override"]),
    failure("budget_denied", "ppl.orchestration_control", "admission", "refusal", "No finite compute, I/O or cost budget is authorized.", ["wait for capacity", "obtain budget authority"]),
    failure("source_unavailable", "ppl.ingestion_contract", "runtime", "failure", "The qualified source endpoint cannot serve the admitted read.", ["retry if classified transient", "fail cut", "switch prequalified replica"]),
    failure("source_rewound", "ppl.change_capture_coordination", "runtime", "failure", "Observed source position regressed or changed lineage.", ["stop capture", "re-bootstrap with explicit lineage"]),
    failure("change_gap_detected", "ppl.change_capture_coordination", "runtime", "failure", "A discontinuity exists between durable change positions.", ["repair from retained log", "re-snapshot", "record permanent gap"]),
    failure("snapshot_overlap_ambiguous", "ppl.snapshot_change_handoff", "runtime", "failure", "Concurrent snapshot and log observations cannot be reconciled deterministically.", ["restart handoff", "quarantine affected keys"]),
    failure("backpressure_timeout", "ppl.flow_control", "runtime", "failure", "Demand remained below production beyond the declared bound.", ["scale consumer", "spill if allowed", "cancel run"]),
    failure("buffer_exhausted", "ppl.flow_control", "runtime", "failure", "A finite channel exhausted capacity before an allowed overflow action completed.", ["apply overflow policy", "fail run"]),
    failure("checkpoint_timeout", "ppl.checkpoint_coordination", "runtime", "failure", "Checkpoint barriers or state persistence did not complete within policy.", ["abort checkpoint", "retry checkpoint", "switch prequalified mode"]),
    failure("checkpoint_corrupt", "ppl.checkpoint_coordination", "restore", "failure", "Checkpoint identity, digest or state handles fail validation.", ["try earlier checkpoint", "fail recovery"]),
    failure("state_schema_incompatible", "ppl.operator_state", "restore", "refusal", "Persisted state cannot be interpreted by the selected operator edition.", ["run migration", "restore compatible edition"]),
    failure("worker_lease_lost", "ppl.task_attempt", "runtime", "failure", "The worker no longer owns authority to complete the attempt.", ["fence late effects", "schedule new attempt"]),
    failure("attempt_heartbeat_lost", "ppl.task_attempt", "runtime", "failure", "Attempt liveness evidence expired.", ["revoke lease", "inspect worker", "retry if safe"]),
    failure("attempt_timed_out", "ppl.cancellation", "runtime", "failure", "Attempt exceeded its declared deadline.", ["propagate cancellation", "retry if safe", "compensate effects"]),
    failure("cancellation_uncooperative", "ppl.cancellation", "runtime", "failure", "Work did not acknowledge cancellation within its grace period.", ["force terminate if allowed", "mark abandoned", "fence effects"]),
    failure("commit_conflict", "ppl.sink_commit", "commit", "failure", "Sink rejected the commit because its expected base state changed.", ["rebase and revalidate", "retry transaction if safe"]),
    failure("commit_indeterminate", "ppl.sink_commit", "commit", "failure", "The caller cannot determine whether an external effect committed.", ["reconcile by idempotency key", "query sink", "escalate"]),
    failure("visibility_unconfirmed", "ppl.sink_commit", "publish", "failure", "A commit acknowledgement exists but required visibility/durability evidence does not.", ["recheck", "quarantine", "fail publication"]),
    failure("quality_gate_blocked", "ppl.quality_gate", "publish", "refusal", "A blocking quality assertion failed for the exact materialization.", ["quarantine", "repair and rerun", "request scoped waiver"]),
    failure("lineage_incomplete", "ppl.lineage_receipt", "publish", "refusal", "Required input, activity, agent or output evidence is missing.", ["collect evidence", "publish with explicit gap only if allowed"]),
    failure("materialization_identity_missing", "ppl.materialization", "publish", "refusal", "Content, snapshot or version identity cannot be fixed.", ["obtain identity", "refuse publication"]),
    failure("retry_exhausted", "ppl.retry", "runtime", "failure", "The finite retry budget has been consumed.", ["fail task", "compensate", "human escalation"]),
    failure("compensation_failed", "ppl.compensation", "recovery", "failure", "A required counteraction did not reach its acceptance condition.", ["retry compensation if safe", "human remedy", "record residual harm"]),
    failure("backfill_divergence", "ppl.backfill", "validation", "failure", "Recomputed and expected historical outputs diverge outside tolerance.", ["hold publication", "diagnose semantic drift"]),
    failure("canary_divergence", "ppl.pipeline_change", "rollout", "failure", "New and reference editions disagree outside the declared comparison law.", ["stop rollout", "retain old edition", "investigate"]),
    failure("maintenance_reference_live", "ppl.maintenance", "maintenance", "refusal", "A checkpoint, artifact, offset or state object remains reachable by an active obligation.", ["defer deletion", "prove reference retired"]),
    failure("receipt_signature_invalid", "ppl.lineage_receipt", "evidence", "failure", "Receipt signature or digest chain does not verify.", ["reject receipt", "recollect evidence"]),
]


INNOVATIONS = [
    {"innovation_id": "innovation.pipeline.incremental_snapshot_handoff", "edition": 1, "name": "Online resumable incremental snapshots concurrent with CDC", "period": "2021-2022", "domain_change": "Makes baseline acquisition a chunked, resumable protocol with overlap windows rather than a one-time blocking prelude.", "compiler_implications": ["represent snapshot window and chunk cursor", "prove overlap deduplication", "retain restart context", "expose source write/read-only signaling"], "evidence_refs": ["src.debezium.incremental_snapshot", "src.debezium.postgres"], "limits": ["requires a stable chunk ordering", "does not imply total ordering of snapshot reads and changes"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.data_aware_orchestration", "edition": 1, "name": "Data/materialization-aware scheduling", "period": "2022-2026", "domain_change": "Promotes data update observations from incidental sensors to first-class run triggers.", "compiler_implications": ["separate materialization identity from URI", "deduplicate trigger observations", "derive a data cut from update events", "model all-of/any-of/coalescing"], "evidence_refs": ["src.airflow.data_aware", "src.dagster.assets"], "limits": ["an update event alone does not prove data quality or completeness"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.asset_quality_gates", "edition": 1, "name": "Quality checks integrated with materialization orchestration", "period": "2023-2024", "domain_change": "Makes quality assertions addressable work that can block downstream propagation.", "compiler_implications": ["bind checks to exact cuts and materializations", "represent block/warn/quarantine precedence", "require scoped waiver authority"], "evidence_refs": ["src.dagster.asset_checks", "src.openlineage.spec"], "limits": ["check execution is not proof of check adequacy"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.open_runtime_lineage_1", "edition": 1, "name": "Open runtime and static lineage contracts", "period": "2021-2024", "domain_change": "Standardizes job/run/dataset events and later prospective static lineage across heterogeneous tools.", "compiler_implications": ["emit declared and observed lineage separately", "carry exact run and dataset identities", "version facets without vendor branches"], "evidence_refs": ["src.openlineage.spec", "src.openlineage.1_0"], "limits": ["instrumentation coverage remains implementation-dependent"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.portable_relational_plans", "edition": 1, "name": "Cross-language portable relational plan interchange", "period": "2021-2026", "domain_change": "Creates an engine-neutral representation for structured compute operations and extensions.", "compiler_implications": ["lower semantic operations to portable plan fragments", "qualify extension functions", "retain orchestration and runtime concerns outside the relational plan"], "evidence_refs": ["src.substrait.basics", "src.substrait.basics"], "limits": ["does not specify scheduling, complete streaming progress, deployment or end-to-end effects"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.declarative_portable_dataflow", "edition": 1, "name": "Declarative runner-portable batch/stream pipeline surfaces", "period": "2024-2026", "domain_change": "Allows a provider-neutral pipeline graph to be authored as data and consumed by tooling.", "compiler_implications": ["separate surface syntax from canonical IR", "type provider transforms", "quarantine templating from semantic identity", "preserve runner selection as a binding decision"], "evidence_refs": ["src.beam.yaml", "src.beam.programming"], "limits": ["current transform catalog and portability are implementation-specific"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.disaggregated_async_state", "edition": 1, "name": "Disaggregated state with asynchronous operator access", "period": "2025-2026", "domain_change": "Decouples state durability from task-local disks while using asynchronous access to mask remote latency.", "compiler_implications": ["qualify async-state-compatible operators", "preserve per-key order, timers and watermarks", "model remote I/O and cache budgets", "bind state backend independently from logical state"], "evidence_refs": ["src.flink.async_state_2", "src.flink.savepoints"], "limits": ["operator coverage and performance depend on workload and implementation"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.algebraic_incrementalization", "edition": 1, "name": "Compiler-derived incremental dataflow from batch semantics", "period": "2023-2026", "domain_change": "Uses algebraic differentiation/circuit transformation to derive incremental maintenance rather than hand-authoring change logic.", "compiler_implications": ["record batch-equivalence oracle", "represent signed differences and integration", "bound state and compaction", "refuse unsupported operations"], "evidence_refs": ["src.dbsp.paper", "src.materialize.arrangements"], "limits": ["supported language and operator algebra are finite", "external effects are outside pure incremental equivalence"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.table_change_feeds", "edition": 1, "name": "Table-native row-level change feeds", "period": "2021-2026", "domain_change": "Makes a committed analytical table both a materialization and an incremental pipeline source.", "compiler_implications": ["bind commit-version ranges", "honor retention", "model before/after/change operation", "track schema across change ranges"], "evidence_refs": ["src.delta.cdf", "src.hudi.spec", "src.paimon.overview"], "limits": ["history retention and schema-change support vary", "change feed completeness begins only when enabled in some formats"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.branch_publish_workflows", "edition": 1, "name": "Snapshot branches for write-audit-publish and pipeline testing", "period": "2021-2026", "domain_change": "Uses isolated table lineages as a publication gate and reproducible test boundary.", "compiler_implications": ["model branch and snapshot identities", "separate commit from publication", "prove fast-forward or merge preconditions", "retain branch lifecycle"], "evidence_refs": ["src.iceberg.branching", "src.iceberg.spec"], "limits": ["branch semantics are table-scoped and do not provide multi-system atomicity"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.unaligned_checkpointing", "edition": 1, "name": "Production unaligned checkpoints under backpressure", "period": "2021-2026", "domain_change": "Captures in-flight channel data so checkpoint barriers need not wait behind congested buffers.", "compiler_implications": ["model channel state in checkpoint", "qualify topology limitations", "record watermark/recovery consequences", "trade checkpoint storage I/O against alignment delay"], "evidence_refs": ["src.flink.backpressure", "src.flink.checkpointing"], "limits": ["does not remove underlying backpressure", "can change recovery-time watermark behavior"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.unified_batch_stream_tables", "edition": 1, "name": "Tables as batch snapshots and streaming sources/sinks", "period": "2021-2026", "domain_change": "Collapses separate batch and streaming storage products into multiple temporal views of one committed table history.", "compiler_implications": ["select snapshot/incremental/CDC view", "bind starting and ending versions", "model merge engine and compaction", "avoid claiming identical latency or update semantics"], "evidence_refs": ["src.delta.streaming", "src.hudi.spec", "src.paimon.overview"], "limits": ["engine connectors and guarantees differ"], "llm_dependency": "none"},
    {"innovation_id": "innovation.pipeline.first_class_stateful_processors", "edition": 1, "name": "Typed state variables, timers and TTL in high-level streaming APIs", "period": "2024-2026", "domain_change": "Exposes state lifecycle and timers as structured definitions instead of opaque user-managed blobs.", "compiler_implications": ["type state variables", "validate TTL against semantics", "map timers to time domains", "derive migration obligations"], "evidence_refs": ["src.spark.stateful", "src.beam.basics"], "limits": ["backend portability and exact semantics remain engine-specific"], "llm_dependency": "none"},
]


def library(lib_id: str, name: str, kind: str, owner: str, responsibilities: list[str], excludes: list[str], decisions: list[str]) -> dict:
    return {
        "library_candidate_id": f"library.pipeline.{lib_id}",
        "edition": EDITION,
        "status": "boundary_candidate",
        "name": name,
        "library_kind": kind,
        "semantic_owner_context": owner,
        "responsibilities": responsibilities,
        "explicit_exclusions": excludes,
        "public_contracts": [f"{name.replace(' ', '')}Request", f"{name.replace(' ', '')}Outcome", f"{name.replace(' ', '')}Decision"],
        "decision_refs": [f"decision.pipeline.{item}" for item in decisions],
        "effect_rule": "Pure libraries perform no I/O. Runtime libraries accept explicit effect intents and emit typed receipts.",
        "composition_rule": "Depends on published contracts or ports, never on a product or vendor identity.",
        "qualification": ["law tests", "failure/refusal totality", "two independent implementation target"],
        "llm_dependency": "none",
    }


LIBRARIES = [
    library("identity_types", "Pipeline Identity Types", "pure_semantic", "ppl.pipeline_definition", ["definition, plan, deployment, run, attempt, cut and materialization IDs", "edition and compatibility relations"], ["storage", "scheduling"], ["schema_compatibility"]),
    library("graph_algebra", "Dataflow Graph Algebra", "pure_semantic", "ppl.graph_topology", ["typed graph construction", "reachability", "components", "feedback classification"], ["operator execution", "visualization UI"], ["topology_kind", "cycle_law", "dynamic_expansion"]),
    library("graph_validator", "Dataflow Graph Validator", "pure_algorithm", "ppl.graph_topology", ["compose structural, port, required-endpoint, cycle-law and dynamic-expansion validation results", "emit a complete finding report and identity-bound validated-graph certificate"], ["graph construction or traversal algorithms", "port compatibility decisions", "progress or termination proof generation", "provider plan optimization", "execution or publication authority"], ["topology_kind", "cycle_law"]),
    library("port_typechecker", "Port Compatibility Typechecker", "pure_algorithm", "ppl.port_contract", ["carrier/schema/update/time/order/cardinality compatibility", "adapter obligation derivation"], ["business schema ownership", "serialization I/O"], ["port_update_model", "port_boundedness", "schema_compatibility", "null_missing", "ordering_scope"]),
    library("data_cut_algebra", "Data Cut Algebra", "pure_semantic", "ppl.data_cut", ["offset ranges", "snapshot sets", "partition cuts", "frontier comparison", "cut closure"], ["source reads"], ["data_cut_closure"]),
    library("change_envelope", "Canonical Change Envelope", "pure_semantic", "ppl.change_capture_coordination", ["insert/update/delete/tombstone/schema/transaction representation", "source-position identity"], ["source log decoding", "target merge"], ["port_update_model"]),
    library("snapshot_handoff", "Snapshot Change Handoff", "runtime_protocol", "ppl.snapshot_change_handoff", ["chunk state machine", "watermark windows", "overlap reconciliation", "restart context"], ["source-specific SQL", "sink delivery"], ["snapshot_change_strategy", "snapshot_chunk_key"]),
    library("progress_algebra", "Progress Frontier Algebra", "pure_semantic", "ppl.event_time_progress", ["partial-order frontiers", "watermark combination", "idleness qualification"], ["wall-clock scheduling", "window aggregation"], ["event_timestamp", "watermark_strategy", "idle_input", "watermark_alignment"]),
    library("window_trigger", "Window Trigger Semantics", "pure_semantic", "ppl.window_trigger", ["window assignment/merge", "trigger state machine", "pane accumulation and lateness"], ["timer service runtime", "sink update implementation"], ["window_kind", "trigger_kind", "accumulation_mode", "late_data"]),
    library("differential_algebra", "Differential Change Algebra", "pure_algorithm", "ppl.incremental_computation", ["timestamped differences", "integration", "consolidation", "incremental equivalence laws"], ["state backend", "external effects"], ["port_update_model", "state_bound"]),
    library("partition_algebra", "Partition Exchange Algebra", "pure_algorithm", "ppl.partition_exchange", ["partition functions", "partition mapping", "rescale mapping", "skew diagnostics"], ["network shuffle", "worker allocation"], ["partition_function", "parallelism", "exchange_mode", "skew_mitigation"]),
    library("state_contracts", "Operator State Contracts", "pure_semantic", "ppl.operator_state", ["state type/scope/bound/TTL/durability/migration contracts"], ["backend reads and writes"], ["state_scope", "state_bound", "state_durability", "state_ttl", "state_migration"]),
    library("delivery_proof", "End to End Delivery Proof", "pure_algorithm", "ppl.delivery_guarantee", ["compose source, execution, checkpoint and sink premises", "scope failure models"], ["execute delivery", "claim business correctness"], ["delivery_multiplicity", "delivery_order", "atomicity_scope", "sink_idempotency"]),
    library("schedule_calculus", "Schedule and Trigger Calculus", "pure_algorithm", "ppl.schedule_trigger", ["recurrence expansion", "time zones", "misfires", "event coalescing", "logical time"], ["clock service", "event subscription"], ["trigger_type", "misfire", "trigger_coalescing"]),
    library("retry_policy", "Retry Policy Algebra", "pure_algorithm", "ppl.retry", ["failure classification", "finite budgets", "backoff and jitter", "deadline composition"], ["sleep/timer effects", "task execution"], ["retry_classification", "retry_backoff", "retry_budget"]),
    library("recovery_planner", "Pipeline Recovery Planner", "pure_algorithm", "ppl.replay", ["restore/replay/backfill/compensation plan selection", "effect disposition"], ["perform recovery effects"], ["replay_semantics", "backfill_reprocessing", "compensation"]),
    library("lineage_receipts", "Pipeline Lineage Receipts", "pure_semantic", "ppl.lineage_receipt", ["prospective and observed lineage records", "receipt scopes", "digest/signature inputs"], ["telemetry transport", "signature key custody"], ["lineage_granularity"]),
    library("logical_planner", "Logical Dataflow Planner", "pure_algorithm", "ppl.execution_plan", ["logical rewrites", "operation composition", "proof witnesses"], ["provider operator selection", "deployment"], ["topology_kind", "execution_mode"]),
    library("physical_planner", "Physical Dataflow Planner", "pure_algorithm", "ppl.execution_plan", ["offer matching", "operator selection", "fusion/exchange", "resource estimate"], ["target deployment", "runtime execution"], ["exchange_mode", "parallelism", "state_backend", "target_placement"]),
    library("connector_spi", "Pipeline Connector SPI", "effect_port", "ppl.ingestion_contract", ["discovery/read/change/write intents", "offset and acknowledgement contracts", "capability offers"], ["any specific source implementation"], ["ingestion_mode", "read_consistency", "cursor_commit_boundary"]),
    library("channel_runtime", "Bounded Channel Runtime", "runtime_effect", "ppl.channel_contract", ["finite buffers", "demand/credits", "close/error propagation", "channel receipts"], ["record transformation semantics", "global resource scheduling"], ["channel_capacity", "push_pull", "overflow_action"]),
    library("checkpoint_coordinator", "Checkpoint Coordinator", "runtime_protocol", "ppl.checkpoint_coordination", ["barrier injection", "operator acknowledgements", "completion/abort", "recovery-point publication"], ["state backend encoding", "sink business semantics"], ["checkpoint_mode", "checkpoint_cadence", "checkpoint_retention"]),
    library("state_backend_spi", "State Backend SPI", "effect_port", "ppl.operator_state", ["state get/put/snapshot/restore/migrate intents", "capability and cost offers"], ["operator state meaning", "specific backend"], ["state_backend", "state_durability"]),
    library("sink_committer", "Sink Commit Protocol", "runtime_protocol", "ppl.sink_commit", ["stage/validate/prepare/commit/abort/reconcile", "fencing and idempotency"], ["specific sink client", "transformation"], ["atomicity_scope", "sink_idempotency", "visibility_check"]),
    library("orchestration_kernel", "Orchestration State Machine", "runtime_protocol", "ppl.orchestration_control", ["readiness", "task admission", "branch/join", "run state transitions"], ["worker implementation", "record exchange"], ["dependency_outcome", "run_concurrency"]),
    library("task_lease", "Task Lease and Attempt Protocol", "runtime_protocol", "ppl.task_attempt", ["lease/fence/heartbeat/outcome", "late completion rejection"], ["task computation", "resource manager"], ["timeout", "cancellation"]),
    library("deployment_adapter_spi", "Deployment Target SPI", "effect_port", "ppl.deployment_binding", ["target qualification", "artifact deployment", "activate/deactivate", "deployment receipts"], ["specific scheduler/cloud", "plan semantics"], ["artifact_binding", "target_placement", "rollout"]),
    library("materialization_publisher", "Materialization Publication Protocol", "pure_semantic", "ppl.materialization", ["identity-bound candidate and publication lifecycle", "compose commit, quality, lineage, policy and authority witnesses", "form publication, supersession and recall effect intents", "classify receipts and reconcile unknown completion"], ["storage or catalog commit", "quality algorithm or gate authority", "publication authority issuance", "effect execution", "consumer acceptance", "product catalog publication"], ["materialization_publication", "quality_gate_action"]),
    library("telemetry_adapter", "Pipeline Telemetry Adapter", "effect_port", "ppl.observability", ["run/attempt correlated metrics, logs and spans", "bounded telemetry buffering"], ["telemetry backend", "semantic correctness"], ["telemetry_sampling"]),
    library("maintenance_planner", "Pipeline Maintenance Planner", "pure_algorithm", "ppl.maintenance", ["reachability-based retention", "compaction/cleanup scheduling", "conflict detection"], ["destructive storage effects"], ["maintenance_retention"]),
]


GRAPH_ALGEBRA_REFUSALS = [
    "GraphIdentityMissing", "GraphRevisionConflict", "GraphPolicyEditionUnknown",
    "NodeIdentityDuplicate", "NodeUnresolved", "PortEndpointUnresolved", "EdgeIdentityDuplicate",
    "EdgeEndpointInvalid", "IncidentEdgeDispositionRequired", "SubgraphIdentityCollision",
    "IdentityMappingNonInjective", "ComponentPartitionInvalid", "FeedbackDeclarationUnresolved",
    "DynamicExpansionUnresolved", "CanonicalOrderUnavailable", "GraphResourceBudgetExceeded",
]

GRAPH_ALGEBRA_CONTRACT = {
    "public_contracts": [],
    "public_types": [
        "DataflowGraphId", "DataflowGraphRevision", "GraphPolicyEdition", "GraphConstructionProfile",
        "GraphTopologyKind", "DynamicExpansionDeclarationRef", "GraphNodeId", "GraphEdgeId",
        "GraphNodeRef", "GraphPortEndpoint", "DirectedPortEdge", "IncidentEdgeDisposition",
        "DataflowGraph", "GraphNodeSelection", "GraphIdentityMap", "ReachabilityQuery",
        "ReachabilitySet", "StrongComponent", "StrongComponentPartition", "CondensationDag",
        "FeedbackDeclarationSet", "StructuralFeedbackClassification", "CanonicalDataflowGraph",
        "DataflowGraphComparison", "DataflowGraphDiff", "GraphResourceBudget", "GraphRefusal",
    ],
    "public_traits": ["DataflowGraphAlgebra"],
    "input_types": [
        "DataflowGraphRevision", "GraphConstructionProfile", "GraphPolicyEdition", "GraphNodeRef",
        "DirectedPortEdge", "IncidentEdgeDisposition", "DataflowGraph", "GraphNodeSelection",
        "GraphIdentityMap", "ReachabilityQuery", "StrongComponentPartition",
        "FeedbackDeclarationSet", "GraphResourceBudget",
    ],
    "output_types": [
        "DataflowGraphRevision", "DataflowGraph", "ReachabilitySet", "StrongComponentPartition",
        "CondensationDag", "StructuralFeedbackClassification", "CanonicalDataflowGraph",
        "DataflowGraphDiff",
    ],
    "error_contracts": GRAPH_ALGEBRA_REFUSALS,
    "operations": [
        {"operation_ref": "operation.pipeline.graph-algebra.create", "name": "create_dataflow_graph", "input_types": ["DataflowGraphId", "GraphConstructionProfile", "GraphPolicyEdition"], "output_type": "Result<DataflowGraphRevision,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.insert-node", "name": "insert_graph_node", "input_types": ["DataflowGraphRevision", "GraphNodeRef", "GraphPolicyEdition"], "output_type": "Result<DataflowGraphRevision,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.connect-edge", "name": "connect_graph_edge", "input_types": ["DataflowGraphRevision", "DirectedPortEdge", "GraphPolicyEdition"], "output_type": "Result<DataflowGraphRevision,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.remove-edge", "name": "remove_graph_edge", "input_types": ["DataflowGraphRevision", "GraphEdgeId", "GraphPolicyEdition"], "output_type": "Result<DataflowGraphRevision,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.remove-node", "name": "remove_graph_node", "input_types": ["DataflowGraphRevision", "GraphNodeId", "IncidentEdgeDisposition", "GraphPolicyEdition"], "output_type": "Result<DataflowGraphRevision,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.compose-subgraph", "name": "compose_dataflow_subgraph", "input_types": ["DataflowGraphRevision", "DataflowGraph", "GraphIdentityMap", "GraphPolicyEdition"], "output_type": "Result<DataflowGraphRevision,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.project-subgraph", "name": "project_induced_subgraph", "input_types": ["DataflowGraph", "GraphNodeSelection", "GraphPolicyEdition"], "output_type": "Result<DataflowGraph,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.reachability", "name": "evaluate_graph_reachability", "input_types": ["DataflowGraph", "ReachabilityQuery", "GraphResourceBudget"], "output_type": "Result<ReachabilitySet,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.strong-components", "name": "partition_strong_components", "input_types": ["DataflowGraph", "GraphResourceBudget"], "output_type": "Result<StrongComponentPartition,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.condense", "name": "build_condensation_dag", "input_types": ["DataflowGraph", "StrongComponentPartition", "GraphResourceBudget"], "output_type": "Result<CondensationDag,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.classify-feedback", "name": "classify_structural_feedback", "input_types": ["DataflowGraph", "StrongComponentPartition", "FeedbackDeclarationSet", "GraphResourceBudget"], "output_type": "Result<StructuralFeedbackClassification,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.canonicalize", "name": "canonicalize_dataflow_graph", "input_types": ["DataflowGraph", "GraphPolicyEdition", "GraphResourceBudget"], "output_type": "Result<CanonicalDataflowGraph,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-algebra.diff", "name": "compare_dataflow_graphs", "input_types": ["DataflowGraphComparison", "GraphResourceBudget"], "output_type": "Result<DataflowGraphDiff,GraphRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_ALGEBRA_REFUSALS},
    ],
    "laws": [
        "graph node edge and edition identities are immutable and unique within one graph revision",
        "parallel edges and self loops are preserved when their edge identities differ and are never silently deduplicated",
        "node insertion order adjacency iteration order and map implementation are not semantic graph properties",
        "subgraph composition resolves every collision through an explicit injective identity map and never silently renames",
        "reachability includes a zero-length path only when the query explicitly selects reflexive closure",
        "strong components form an exact disjoint partition of all graph nodes and the condensation quotient is acyclic",
        "condensation preserves reachability between distinct strong components",
        "structural feedback classification identifies cycles and declared feedback edges but proves neither progress termination convergence productivity nor state boundedness",
        "exact graph equality graph diff and graph isomorphism are distinct; this contract provides identity-bound equality and diff but no semantic isomorphism claim",
        "dynamic expansion is never ambient mutation; an unresolved or unbounded expansion declaration is refused",
        "the algebra owns no operator meaning port compatibility scheduling placement runtime execution or business outcome",
    ],
    "oracles": [
        "directed-multigraph-positive-fixtures", "duplicate-and-dangling-endpoint-negative-twins",
        "tarjan-kosaraju-gabow-strong-component-differential", "condensation-acyclicity-properties",
        "reachability-quotient-properties", "subgraph-composition-alpha-mapping-properties",
        "permutation-invariant-canonicalization", "deep-graph-stack-budget-fuzz",
        "cyclic-progress-nonclaim-negative-twins", "cross-implementation-differential",
    ],
    "resource_contracts": [
        "reachability strong-component and condensation work are O(nodes plus edges)",
        "canonicalization and diff declare finite node edge and output budgets",
        "deep graphs use a bounded explicit work stack or refuse before stack exhaustion",
        "no filesystem network clock randomness process environment or hidden durable state",
    ],
    "dependencies": ["library.pipeline.identity_types"],
    "evidence_refs": ["src.tarjan.scc", "src.naiad.paper", "src.beam.basics", "src.substrait.basics"],
}

GRAPH_VALIDATOR_REFUSALS = [
    "ValidationInputUnresolved", "ValidationProfileUnresolved", "ValidationProfileInvalid",
    "ValidationProfileAuthorityUnresolved", "GraphReferenceUnresolved", "GraphDigestMismatch",
    "GraphAlgebraEditionUnsupported", "PortTypecheckerEditionUnsupported",
    "StructuralFactsIncomplete", "StructuralFactsDigestMismatch", "PortWitnessSetMalformed",
    "CyclePolicyUnresolved", "CycleWitnessSetMalformed", "DynamicExpansionPolicyUnresolved",
    "DynamicExpansionWitnessMalformed", "FindingIdentityCollision", "ComponentResultIncomplete",
    "ValidationCoverageIncomplete", "ValidationReportNonconforming", "ValidationReportIncomplete",
    "ValidationReportDigestMismatch", "GraphValidationResourceBudgetExceeded",
]

GRAPH_VALIDATOR_CONTRACT = {
    "public_contracts": [],
    "public_types": [
        "GraphValidationProfileId", "GraphValidationProfileEdition", "GraphValidationProfile",
        "GraphValidationProfileAuthorityRef", "GraphValidationInput", "CanonicalDataflowGraphRef",
        "GraphStructuralFacts", "RequiredEndpointSet", "PortCompatibilityWitnessSet",
        "CycleLawWitnessSet", "DynamicExpansionWitnessSet", "GraphConstraintId",
        "GraphValidationFindingId", "GraphValidationSeverity", "GraphValidationFinding",
        "GraphValidationCoverage", "GraphValidationPlan", "StructuralValidationResult",
        "PortValidationResult", "ReachabilityValidationResult", "CycleValidationResult",
        "DynamicExpansionValidationResult", "GraphValidationComponentSet", "GraphValidationReport",
        "ValidatedDataflowGraph", "GraphValidationReportComparison", "GraphValidationReportDiff",
        "GraphValidationResourceBudget", "GraphValidationRefusal",
    ],
    "public_traits": ["DataflowGraphValidator"],
    "input_types": [
        "GraphValidationInput", "GraphValidationProfile", "GraphValidationResourceBudget",
        "GraphValidationPlan", "GraphStructuralFacts", "PortCompatibilityWitnessSet",
        "RequiredEndpointSet", "CycleLawWitnessSet", "DynamicExpansionWitnessSet",
        "GraphValidationComponentSet", "GraphValidationReport", "GraphValidationReportComparison",
    ],
    "output_types": [
        "GraphValidationPlan", "StructuralValidationResult", "PortValidationResult",
        "ReachabilityValidationResult", "CycleValidationResult", "DynamicExpansionValidationResult",
        "GraphValidationReport", "ValidatedDataflowGraph", "GraphValidationReportDiff",
    ],
    "error_contracts": GRAPH_VALIDATOR_REFUSALS,
    "refusal_precedence": [
        "unresolved identity edition digest or profile authority refuses before any constraint result",
        "malformed or mismatched dependency evidence refuses before coverage evaluation",
        "resource exhaustion refuses the validation operation and never produces a partial conformance claim",
        "a complete nonconforming report is a normal value until certification is requested",
        "certification of an incomplete report refuses before certification of a nonconforming report",
    ],
    "operations": [
        {"operation_ref": "operation.pipeline.graph-validator.prepare", "name": "prepare_graph_validation", "input_types": ["GraphValidationInput", "GraphValidationProfile", "GraphValidationResourceBudget"], "output_type": "Result<GraphValidationPlan,GraphValidationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_VALIDATOR_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-validator.structural-coverage", "name": "evaluate_structural_fact_coverage", "input_types": ["GraphValidationPlan", "GraphStructuralFacts"], "output_type": "Result<StructuralValidationResult,GraphValidationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_VALIDATOR_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-validator.port-witnesses", "name": "evaluate_port_witness_coverage", "input_types": ["GraphValidationPlan", "PortCompatibilityWitnessSet"], "output_type": "Result<PortValidationResult,GraphValidationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_VALIDATOR_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-validator.required-reachability", "name": "evaluate_required_endpoint_reachability", "input_types": ["GraphValidationPlan", "GraphStructuralFacts", "RequiredEndpointSet"], "output_type": "Result<ReachabilityValidationResult,GraphValidationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_VALIDATOR_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-validator.cycle-coverage", "name": "evaluate_cycle_law_coverage", "input_types": ["GraphValidationPlan", "GraphStructuralFacts", "CycleLawWitnessSet"], "output_type": "Result<CycleValidationResult,GraphValidationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_VALIDATOR_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-validator.dynamic-expansion", "name": "evaluate_dynamic_expansion_coverage", "input_types": ["GraphValidationPlan", "DynamicExpansionWitnessSet"], "output_type": "Result<DynamicExpansionValidationResult,GraphValidationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_VALIDATOR_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-validator.compose-report", "name": "compose_graph_validation_report", "input_types": ["GraphValidationPlan", "GraphValidationComponentSet"], "output_type": "Result<GraphValidationReport,GraphValidationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_VALIDATOR_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-validator.certify", "name": "certify_validated_dataflow_graph", "input_types": ["GraphValidationInput", "GraphValidationReport"], "output_type": "Result<ValidatedDataflowGraph,GraphValidationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_VALIDATOR_REFUSALS},
        {"operation_ref": "operation.pipeline.graph-validator.diff-reports", "name": "compare_graph_validation_reports", "input_types": ["GraphValidationReportComparison", "GraphValidationResourceBudget"], "output_type": "Result<GraphValidationReportDiff,GraphValidationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": GRAPH_VALIDATOR_REFUSALS},
    ],
    "laws": [
        "a graph validation profile is immutable editioned authority scoped and explicitly classifies every admitted constraint and severity",
        "validation findings bind stable finding identity constraint identity focus node edge or path severity source evidence and validation-profile edition",
        "a report conforms if and only if coverage is complete and it contains no finding disallowed by the exact validation profile",
        "an invalid graph produces a complete nonconforming report; inability to complete validation produces a refusal and never a partial conformance claim",
        "every graph edge has exactly one compatible rejected or missing port-witness disposition bound to the endpoint contract editions",
        "every required output is reachable from an admitted input or explicitly declared exogenous source under the profile reachability law",
        "every cyclic strong component and self loop has exactly one cycle-policy disposition and all required external progress termination productivity and state-bound witnesses",
        "structural cycle classification is not itself a cycle-law witness and the validator does not generate progress termination convergence or productivity proof",
        "dynamic expansion is accepted only with an exact finite expansion declaration bound and replay identity; ambient runtime graph mutation is refused",
        "finding severity and conformance-disallow policy are supplied by the authorized profile and cannot be weakened by provider model or validator implementation identity",
        "a validated graph certificate binds graph digest validation profile edition graph-algebra edition port-typechecker edition witness digests report digest and validation coverage",
        "any change to graph profile dependency edition evidence cut or finding set invalidates the prior validated-graph certificate",
        "validation does not authorize publication deployment execution waiver or business acceptance",
        "finding and report ordering is canonical and independent of hash-map traversal parallel evaluation and provider identity",
    ],
    "oracles": [
        "shacl-style-complete-report-fixtures", "beam-dag-positive-and-cycle-negative-fixtures",
        "naiad-structured-cycle-positive-fixtures", "missing-port-witness-negative-twins",
        "required-output-reachability-negative-twins", "cycle-witness-coverage-properties",
        "dynamic-expansion-bound-negative-twins", "invalid-versus-refused-state-model",
        "severity-profile-authority-negative-twins", "permutation-invariant-finding-order",
        "dependency-edition-invalidation-properties", "cross-implementation-differential",
    ],
    "resource_contracts": [
        "validation work is bounded by declared nodes edges constraints witnesses findings and output bytes",
        "constraint evaluation may short-circuit internally but a conformance report is emitted only with complete declared coverage",
        "finding accumulation exceeding its finite budget refuses instead of truncating",
        "no filesystem network clock randomness process environment or hidden durable state",
    ],
    "configuration_contracts": ["GraphValidationProfile", "GraphValidationResourceBudget"],
    "dependencies": ["library.pipeline.graph_algebra", "library.pipeline.port_typechecker"],
    "evidence_refs": ["src.w3c.shacl", "src.beam.basics", "src.beam.runner_guide", "src.naiad.paper", "src.tarjan.scc"],
    "boundary_adjudication": {
        "decision_id": "decision.pipeline.graph-algebra-validator-coexistence.v1",
        "disposition": "explicit_coexistence",
        "subject_refs": ["library.pipeline.graph_algebra", "library.pipeline.graph_validator"],
        "rationale": "The algebra owns immutable graph structure and derived structural facts; the validator consumes those facts plus external port and cycle witnesses to decide conformance under an editioned profile.",
        "no_compatibility_alias": True,
    },
}

PORT_TYPECHECKER_REFUSALS = [
    "PortPairUnresolved", "PortIdentityMismatch", "PortEditionUnsupported",
    "PortDirectionInvalid", "PortProfileUnresolved", "PortProfileAuthorityUnresolved",
    "DimensionPolicyIncomplete", "CarrierWitnessMissing", "CarrierWitnessMalformed",
    "SchemaWitnessMissing", "SchemaWitnessMalformed", "SchemaCompatibilityIndeterminate",
    "UpdateModelUnresolved", "UpdateModelIncompatible", "BoundednessUnresolved",
    "BoundednessIncompatible", "TimeDomainUnresolved", "TimeDomainIncompatible",
    "OrderingScopeUnresolved", "OrderingIncompatible", "CardinalityUnresolved",
    "CardinalityIncompatible", "NullMissingPolicyUnresolved", "NullMissingPolicyIncompatible",
    "AdapterObligationUnresolved", "AdapterWitnessMissing", "AdapterWitnessMalformed",
    "InformationLossUnauthorized", "CompatibilityCoverageIncomplete",
    "CompatibilityWitnessDigestMismatch", "PortCompatibilityResourceBudgetExceeded",
]

PORT_TYPECHECKER_CONTRACT = {
    "public_contracts": [],
    "public_types": [
        "PortContractId", "PortContractEdition", "PortDirection", "PortContractRef",
        "PortContract", "ProducerConsumerPortPair", "PortCompatibilityProfileId",
        "PortCompatibilityProfileEdition", "PortCompatibilityProfileAuthorityRef",
        "PortCompatibilityProfile", "PortCompatibilityDimension", "PortDimensionRelation",
        "CarrierContractRef", "CarrierCompatibilityWitness", "SchemaCompatibilityWitness",
        "PortUpdateModel", "UpdateModelCompatibilityWitness", "PortBoundedness",
        "BoundednessCompatibilityWitness", "PortTimeDomain", "TimeDomainCompatibilityWitness",
        "PortOrderingScope", "OrderingCompatibilityWitness", "PortCardinality",
        "CardinalityCompatibilityWitness", "NullMissingPolicy", "NullMissingCompatibilityWitness",
        "InformationLossClass", "AdapterObligationId", "AdapterObligation",
        "AdapterObligationSet", "AdapterChainWitness", "PortDimensionFinding",
        "PortCompatibilityComponentSet", "PortCompatibilityVerdict",
        "PortCompatibilityWitness", "PortCompatibilityComparison", "PortCompatibilityDiff",
        "PortCompatibilityResourceBudget", "PortCompatibilityRefusal",
    ],
    "public_traits": ["PortCompatibilityTypechecker"],
    "input_types": [
        "ProducerConsumerPortPair", "PortCompatibilityProfile", "PortCompatibilityResourceBudget",
        "CarrierCompatibilityWitness", "SchemaCompatibilityWitness", "PortContract",
        "AdapterObligationSet", "AdapterChainWitness", "PortCompatibilityComponentSet",
        "PortCompatibilityVerdict", "PortCompatibilityComparison",
    ],
    "output_types": [
        "PortContract", "PortDimensionRelation", "AdapterObligationSet",
        "PortCompatibilityVerdict", "PortCompatibilityWitness", "PortCompatibilityDiff",
    ],
    "error_contracts": PORT_TYPECHECKER_REFUSALS,
    "refusal_precedence": [
        "unresolved port identity edition direction profile or profile authority refuses before dimension evaluation",
        "missing malformed or digest-mismatched imported witnesses refuse before compatibility composition",
        "incomplete dimension coverage refuses before any compatible or adapter-closed verdict",
        "unauthorized information loss refuses before adapter-witness evaluation",
        "resource exhaustion refuses and never truncates findings or promotes indeterminate to compatible",
    ],
    "operations": [
        {"operation_ref": "operation.pipeline.port-typechecker.validate-contract", "name": "validate_port_contract", "input_types": ["PortContract", "PortCompatibilityProfile", "PortCompatibilityResourceBudget"], "output_type": "Result<PortContract,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.carrier", "name": "evaluate_carrier_compatibility", "input_types": ["ProducerConsumerPortPair", "CarrierCompatibilityWitness", "PortCompatibilityProfile"], "output_type": "Result<PortDimensionRelation,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.schema", "name": "evaluate_schema_compatibility_witness", "input_types": ["ProducerConsumerPortPair", "SchemaCompatibilityWitness", "PortCompatibilityProfile"], "output_type": "Result<PortDimensionRelation,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.update-model", "name": "evaluate_update_model_compatibility", "input_types": ["ProducerConsumerPortPair", "PortCompatibilityProfile"], "output_type": "Result<PortDimensionRelation,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.boundedness", "name": "evaluate_boundedness_compatibility", "input_types": ["ProducerConsumerPortPair", "PortCompatibilityProfile"], "output_type": "Result<PortDimensionRelation,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.time", "name": "evaluate_time_domain_compatibility", "input_types": ["ProducerConsumerPortPair", "PortCompatibilityProfile"], "output_type": "Result<PortDimensionRelation,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.ordering", "name": "evaluate_ordering_compatibility", "input_types": ["ProducerConsumerPortPair", "PortCompatibilityProfile"], "output_type": "Result<PortDimensionRelation,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.cardinality-null", "name": "evaluate_cardinality_and_absence_compatibility", "input_types": ["ProducerConsumerPortPair", "PortCompatibilityProfile"], "output_type": "Result<PortDimensionRelation,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.derive-adapters", "name": "derive_adapter_obligations", "input_types": ["ProducerConsumerPortPair", "PortCompatibilityComponentSet", "PortCompatibilityProfile"], "output_type": "Result<AdapterObligationSet,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.compose", "name": "compose_port_compatibility_verdict", "input_types": ["ProducerConsumerPortPair", "PortCompatibilityComponentSet", "AdapterObligationSet", "PortCompatibilityProfile", "PortCompatibilityResourceBudget"], "output_type": "Result<PortCompatibilityVerdict,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.close-adapters", "name": "verify_adapter_chain_closure", "input_types": ["PortCompatibilityVerdict", "AdapterChainWitness", "PortCompatibilityProfile"], "output_type": "Result<PortCompatibilityWitness,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
        {"operation_ref": "operation.pipeline.port-typechecker.diff", "name": "compare_port_compatibility", "input_types": ["PortCompatibilityComparison", "PortCompatibilityResourceBudget"], "output_type": "Result<PortCompatibilityDiff,PortCompatibilityRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": PORT_TYPECHECKER_REFUSALS},
    ],
    "laws": [
        "compatibility is directional from one exact output-port edition to one exact input-port edition under one authority-scoped profile",
        "only an output port may supply an input port; same-direction connection is invalid rather than adaptable",
        "carrier schema update boundedness time ordering cardinality and null-missing dimensions are independently total and none is inferred from another",
        "schema compatibility is consumed as an editioned external witness from the schema-compatibility owner and is never recomputed or weakened here",
        "wire-safe source-compatible value-preserving business-substitutable and port-compatible remain distinct relations",
        "Substrait-style type class nullability variation and parameters remain separate and every coercion is an explicit adapter obligation",
        "an output update-kind set directly satisfies an input only when every producible kind is accepted with required keys and before-images",
        "bounded input capability cannot silently satisfy an unbounded requirement and unbounded output cannot satisfy a bounded-only consumer without an explicit finite-cut adapter",
        "event processing ingestion recording and valid time are distinct; timestamp field presence does not establish a progress or watermark contract",
        "no arrival order is assumed; total per-key per-partition event-time and causal order are different requirements",
        "cardinality compatibility compares possible producer multiplicity against accepted consumer multiplicity and never treats zero one and many as interchangeable",
        "null missing absent tombstone and delete are distinct unless an authority-scoped lossy adapter explicitly declares the collapse",
        "the direct verdict is compatible iff all required dimensions are directly satisfied; adapter-required incompatible and indeterminate are never promoted to compatible",
        "an adapter obligation names source and target contracts transformation identity information loss proof requirements and responsible authority but does not select or execute an adapter",
        "adapter closure requires an exact ordered chain whose output contract equals the next input contract and whose composed losses are authorized",
        "port compatibility proves no channel capacity backpressure delivery guarantee source truth business acceptance deployment or runtime execution",
        "findings obligations verdicts and witnesses have canonical order independent of provider identity evaluation order and map iteration",
    ],
    "oracles": [
        "arrow-carrier-schema-positive-fixtures", "substrait-nullability-variation-negative-twins",
        "flink-changelog-mode-subset-properties", "bounded-unbounded-asymmetry-negative-twins",
        "event-processing-recording-valid-time-distinction-fixtures", "streaming-order-nonclaim-negative-twins",
        "zero-one-many-cardinality-lattice-properties", "null-missing-tombstone-delete-negative-twins",
        "schema-witness-edition-mismatch-fuzz", "adapter-chain-composition-properties",
        "dimension-permutation-invariant-verdicts", "cross-implementation-differential",
    ],
    "resource_contracts": [
        "work is bounded by declared dimensions schema-witness findings adapter obligations chain length and output bytes",
        "adapter-chain verification is linear in chain length plus imported witness sizes and refuses cyclic chains",
        "finding or obligation budget exhaustion refuses instead of returning partial compatibility",
        "no filesystem network clock randomness process environment or hidden durable state",
    ],
    "configuration_contracts": ["PortCompatibilityProfile", "PortCompatibilityResourceBudget"],
    "dependencies": ["library.pipeline.identity_types", "library.schema_registry.compatibility"],
    "evidence_refs": [
        "src.arrow.c_stream", "src.substrait.type_system", "src.flink.changelog_mode",
        "src.flink.source_sink_contract", "src.flink.execution_order", "src.beam.basics",
        "src.asyncapi.spec",
    ],
}

DATA_CUT_REFUSALS = [
    "DataCutIdentityUnresolved", "DataCutEditionUnsupported", "DataCutStateInvalid",
    "DataCutAuthorityUnresolved", "SourceIdentityUnresolved", "SourceEditionUnresolved",
    "PositionDomainUnresolved", "PositionDomainMismatch", "PositionComparatorWitnessMissing",
    "PositionComparatorWitnessMalformed", "PositionIncomparable", "PositionIntervalInvalid",
    "BoundaryInclusionUnresolved", "PartitionIdentityUnresolved", "PartitionCensusUnknown",
    "PartitionSelectionOverlap", "PartitionSelectionIncomplete", "SnapshotIdentityUnresolved",
    "SnapshotAuthorityMixed", "SnapshotValidityUnproven", "FrontierMalformed",
    "FrontierIncomparable", "TimeIntervalInvalid", "ClosureLawUnresolved",
    "ClosureEvidenceIncomplete", "ClosureWitnessMalformed", "ClosureWitnessDigestMismatch",
    "SourceRetentionExpired", "ClosedCutMutation", "CutComparisonIncomparable",
    "DataCutResourceBudgetExceeded",
]

DATA_CUT_CONTRACT = {
    "public_contracts": [],
    "public_types": [
        "DataCutId", "DataCutEdition", "DataCutState", "DataCutAuthorityRef", "SourceOccurrenceRef",
        "SourceEditionRef", "PositionDomainId", "PositionDomainEdition", "SourcePosition",
        "PositionOrderWitness", "BoundaryInclusion", "SourcePositionInterval", "PartitionId",
        "PartitionCensus", "PartitionSelection", "SnapshotOccurrenceRef", "SnapshotValidityWitness",
        "FrontierPoint", "CutFrontier", "CutFrontierComparison", "DataCutTimeIntervals", "DataCutSelection",
        "DataCutSelectionSet", "ClosureLawId", "ClosureLawEdition", "DataCutClosurePolicy",
        "DataCutClosureEvidence", "DataCutClosureWitness", "OpenDataCut", "ClosedDataCut",
        "InvalidatedDataCut", "DataCut", "DataCutProposal", "DataCutExtension",
        "DataCutInvalidation", "DataCutRelation", "DataCutComparison", "DataCutDiff",
        "DataCutResourceBudget", "DataCutRefusal",
    ],
    "public_traits": ["SourcePositionDomainAlgebra", "DataCutAlgebra"],
    "input_types": [
        "DataCutProposal", "DataCutExtension", "DataCut", "OpenDataCut", "ClosedDataCut",
        "DataCutSelection", "DataCutSelectionSet", "PositionOrderWitness", "CutFrontier", "CutFrontierComparison",
        "DataCutClosurePolicy", "DataCutClosureEvidence", "DataCutInvalidation",
        "DataCutComparison", "DataCutResourceBudget",
    ],
    "output_types": [
        "OpenDataCut", "ClosedDataCut", "InvalidatedDataCut", "DataCutSelection",
        "DataCutSelectionSet", "CutFrontier", "DataCutClosureWitness", "DataCutRelation", "DataCutDiff",
    ],
    "error_contracts": DATA_CUT_REFUSALS,
    "refusal_precedence": [
        "unresolved cut source partition snapshot position-domain edition or authority identity refuses before algebraic comparison",
        "malformed comparator snapshot-validity or closure evidence refuses before frontier or closure evaluation",
        "mixed or incomparable position domains refuse before set composition",
        "closed-cut mutation refuses before extension content is inspected",
        "resource exhaustion refuses without returning a partial frontier cut or closure witness",
    ],
    "operations": [
        {"operation_ref": "operation.pipeline.data-cut.propose", "name": "propose_open_data_cut", "input_types": ["DataCutProposal", "DataCutResourceBudget"], "output_type": "Result<OpenDataCut,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.normalize-selection", "name": "normalize_data_cut_selection", "input_types": ["DataCutSelection", "PositionOrderWitness", "DataCutResourceBudget"], "output_type": "Result<DataCutSelection,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.union-selections", "name": "union_data_cut_selections", "input_types": ["DataCutSelectionSet", "PositionOrderWitness", "DataCutResourceBudget"], "output_type": "Result<DataCutSelectionSet,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.intersect-selections", "name": "intersect_data_cut_selections", "input_types": ["DataCutSelectionSet", "PositionOrderWitness", "DataCutResourceBudget"], "output_type": "Result<DataCutSelectionSet,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.canonical-frontier", "name": "canonicalize_cut_frontier", "input_types": ["CutFrontier", "PositionOrderWitness", "DataCutResourceBudget"], "output_type": "Result<CutFrontier,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.compare-frontiers", "name": "compare_cut_frontiers", "input_types": ["CutFrontierComparison", "PositionOrderWitness", "DataCutResourceBudget"], "output_type": "Result<DataCutRelation,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.extend-open", "name": "extend_open_data_cut", "input_types": ["OpenDataCut", "DataCutExtension", "PositionOrderWitness", "DataCutResourceBudget"], "output_type": "Result<OpenDataCut,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.evaluate-closure", "name": "evaluate_data_cut_closure", "input_types": ["OpenDataCut", "DataCutClosurePolicy", "DataCutClosureEvidence", "PositionOrderWitness", "DataCutResourceBudget"], "output_type": "Result<DataCutClosureWitness,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.close", "name": "close_data_cut", "input_types": ["OpenDataCut", "DataCutClosureWitness", "DataCutAuthorityRef"], "output_type": "Result<ClosedDataCut,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.invalidate", "name": "invalidate_data_cut", "input_types": ["DataCut", "DataCutInvalidation", "DataCutAuthorityRef"], "output_type": "Result<InvalidatedDataCut,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.compare", "name": "compare_data_cuts", "input_types": ["DataCutComparison", "PositionOrderWitness", "DataCutResourceBudget"], "output_type": "Result<DataCutRelation,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
        {"operation_ref": "operation.pipeline.data-cut.diff", "name": "diff_data_cuts", "input_types": ["DataCutComparison", "PositionOrderWitness", "DataCutResourceBudget"], "output_type": "Result<DataCutDiff,DataCutRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": DATA_CUT_REFUSALS},
    ],
    "laws": [
        "a source position is meaningful only within one exact source occurrence partition position-domain identity and edition",
        "source positions are opaque to this algebra and are ordered only by an exact supplied position-domain witness; lexical or numeric guessing is forbidden",
        "a position interval records explicit lower and upper inclusivity and an upper next-position cursor is not silently reinterpreted as the last included record",
        "partition selections are identity-disjoint after normalization and closure over all partitions requires an exact partition census",
        "snapshot identity source identity schema or table edition and validity evidence are distinct and a mutable branch name is not a snapshot identity",
        "Iceberg-style snapshot content closure PostgreSQL transaction visibility and Kafka partition-offset cuts are different position domains and never share inferred comparison",
        "a cut frontier is the minimal antichain of mutually incomparable frontier points under the supplied partial order and has canonical order independent of insertion",
        "frontier advancement constrains possible future positions but proves neither source truth retention physical availability nor business finality",
        "event valid recording and ingestion intervals are separate filters and timestamps alone never identify the selected records",
        "union intersection containment and difference are defined only for compatible source and position domains with explicit boundary laws",
        "an open cut may extend monotonically under its policy; a closed cut is immutable and any revision creates a new cut identity and edition",
        "closure is law-specific and requires complete evidence for every selected source and partition; one snapshot or frontier cannot close unrelated sources",
        "a closure witness binds the exact selection digest closure-policy edition evidence cut comparator editions and authority reference",
        "source retention or snapshot expiry invalidates future reproducibility evidence without rewriting the historical closed-cut fact",
        "a data cut is not a schedule interval checkpoint savepoint transaction commit materialization lineage receipt or proof of data quality",
        "the algebra performs no source reads offset commits snapshot exports retention extension restoration or materialization effects",
        "canonical cut identity and diff are independent of input ordering map iteration provider name and evidence presentation order",
    ],
    "oracles": [
        "kafka-next-offset-boundary-fixtures", "iceberg-snapshot-versus-branch-negative-twins",
        "postgres-exported-snapshot-lifetime-negative-twins", "timely-antichain-minimality-properties",
        "incomparable-partition-frontier-fixtures", "inclusive-exclusive-range-boundary-tests",
        "unknown-partition-census-closure-refusals", "mixed-position-domain-negative-twins",
        "open-extend-close-invalidate-state-model", "union-intersection-difference-set-properties",
        "permutation-invariant-canonicalization", "cross-implementation-differential",
    ],
    "resource_contracts": [
        "selection and frontier work is bounded by sources partitions intervals frontier points evidence items and output bytes",
        "normalization comparison union intersection and diff declare finite comparison and allocation budgets",
        "antichain reduction refuses when the supplied comparison budget cannot establish minimality",
        "no filesystem network clock randomness process environment or hidden durable state",
    ],
    "configuration_contracts": ["DataCutClosurePolicy", "DataCutResourceBudget"],
    "dependencies": ["library.pipeline.identity_types", "library.csp.time.interval-algebra"],
    "evidence_refs": [
        "src.kafka.consumer_position", "src.iceberg.spec", "src.postgresql.export_snapshot",
        "src.timely.frontier", "src.timely.progress", "src.beam.basics",
    ],
}

MATERIALIZATION_PUBLICATION_REFUSALS = [
    "MaterializationIdentityUnresolved", "MaterializationEditionUnsupported",
    "MaterializationStateInvalid", "MaterializationRevisionConflict",
    "RunIdentityUnresolved", "ProducerOutputUnresolved", "DataCutUnresolved",
    "TargetOccurrenceUnresolved", "TargetVersionIdentityUnresolved",
    "TargetVersionDomainUnresolved", "ContentIdentityRequired",
    "CommitReceiptMissing", "CommitReceiptMalformed", "CommitReceiptScopeMismatch",
    "CommitDurabilityUnproven", "CommitVisibilityUnproven", "CommitCompletionUnknown",
    "QualityGateVerdictMissing", "QualityGateVerdictStale", "QualityGateScopeMismatch",
    "QualityGateBlocked", "QualityWaiverMissing", "QualityWaiverUnauthorized",
    "LineageReceiptMissing", "LineageReceiptScopeMismatch",
    "PublicationPolicyUnresolved", "PublicationMechanismUnsupported",
    "PublicationAuthorityMissing", "PublicationAuthorityScopeMismatch",
    "PublicationAuthorityExpired", "ReleaseTimeObservationMissing",
    "ReleaseConditionUnsatisfied", "ExpectedPublicationHeadConflict",
    "IdempotencyScopeConflict", "FenceTokenStale", "EffectReceiptMalformed",
    "EffectReceiptIntentMismatch", "PublicationCompletionUnknown",
    "PublicationObservationIncomplete", "SupersessionTargetInvalid",
    "RecallReasonMissing", "RecallAuthorityMissing", "TransitionNotAllowed",
    "ProviderCapabilityMissing", "ProviderQualificationMissing",
    "PublicationResourceBudgetExceeded",
]

MATERIALIZATION_PUBLICATION_CONTRACT = {
    "effect_boundary": "pure_effect_intents",
    "effect_rule": "This library performs no I/O. It deterministically evaluates evidence and emits typed effect intents; qualified adapters execute intents and external receipts are imported for classification and reconciliation.",
    "public_contracts": [],
    "public_types": [
        "MaterializationId", "MaterializationEdition", "MaterializationRevision",
        "MaterializationState", "PipelineRunRef", "ProducerNodeRef", "OutputPortRef",
        "ClosedDataCutRef", "TargetOccurrenceRef", "TargetVersionDomainId",
        "TargetVersionDomainEdition", "TargetVersionIdentity", "ContentIdentity",
        "MaterializationCandidate", "MaterializationCandidateDigest",
        "SinkCommitReceiptRef", "CommitEvidence", "QualityGateVerdictRef",
        "QualityGateEvidence", "QualityWaiverRef", "LineageReceiptRef",
        "LineageEvidence", "PublicationEvidenceSet", "PublicationEvidenceDigest",
        "PublicationPolicy", "PublicationPolicyEdition", "PublicationMechanism",
        "PublicationVisibilityScope", "PublicationEligibility",
        "PublicationEligibilityFinding", "PublicationEligibilityReport",
        "PublicationAuthorityRef", "PublicationAuthorityGrant", "ReleaseTimeObservation",
        "ExpectedPublicationHead", "PublicationCommandContext", "IdempotencyKey",
        "FenceToken", "PublicationEffectIntent", "SupersessionEffectIntent",
        "RecallEffectIntent", "PublicationEffectReceipt", "PublicationEffectOutcome",
        "PublicationEffectClassification", "PublicationTargetObservation",
        "PublicationObservationSet", "PublicationReconciliationPolicy",
        "PublicationReconciliationResult", "MaterializationPublicationEvent",
        "PublishedMaterialization", "SupersededMaterialization", "RecalledMaterialization",
        "MaterializationPublication", "MaterializationPublicationComparison",
        "MaterializationPublicationDiff", "PublicationResourceBudget",
        "MaterializationPublicationRefusal",
    ],
    "public_traits": ["MaterializationPublicationAlgebra", "MaterializationPublicationEffectPort"],
    "input_types": [
        "MaterializationCandidate", "PublicationEvidenceSet", "PublicationPolicy",
        "PublicationEligibilityReport", "PublicationAuthorityGrant", "ReleaseTimeObservation",
        "ExpectedPublicationHead", "PublicationCommandContext", "MaterializationPublication",
        "PublicationEffectIntent", "SupersessionEffectIntent", "RecallEffectIntent",
        "PublicationEffectReceipt", "PublicationObservationSet",
        "PublicationReconciliationPolicy", "MaterializationPublicationEvent",
        "MaterializationPublicationComparison", "PublicationResourceBudget",
    ],
    "output_types": [
        "MaterializationCandidate", "PublicationEvidenceSet", "PublicationEligibilityReport",
        "PublicationEffectIntent", "SupersessionEffectIntent", "RecallEffectIntent",
        "PublicationEffectClassification", "PublicationReconciliationResult",
        "MaterializationPublication", "MaterializationPublicationDiff",
    ],
    "error_contracts": MATERIALIZATION_PUBLICATION_REFUSALS,
    "refusal_precedence": [
        "unresolved materialization run producer output data-cut target version-domain edition or authority identity refuses before evidence or lifecycle evaluation",
        "malformed mismatched stale or incomplete commit quality lineage authority and effect receipts refuse before an adverse completed eligibility report is formed",
        "a valid complete blocking quality verdict returns an ineligible report unless a separately authorized applicable waiver is bound; it is not disguised as processor failure",
        "invalid current lifecycle state expected-head conflict stale fence or idempotency conflict refuses before an effect intent is formed",
        "unknown effect completion returns reconciliation required and refuses any blind retry or success transition",
        "resource exhaustion refuses without partial eligibility publication or reconciliation claims",
    ],
    "operations": [
        {"operation_ref": "operation.pipeline.materialization-publication.create-candidate", "name": "create_materialization_candidate", "input_types": ["MaterializationCandidate", "PublicationResourceBudget"], "output_type": "Result<MaterializationCandidate,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
        {"operation_ref": "operation.pipeline.materialization-publication.bind-evidence", "name": "bind_publication_evidence", "input_types": ["MaterializationCandidate", "PublicationEvidenceSet", "PublicationPolicy", "PublicationResourceBudget"], "output_type": "Result<PublicationEvidenceSet,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
        {"operation_ref": "operation.pipeline.materialization-publication.evaluate-eligibility", "name": "evaluate_publication_eligibility", "input_types": ["MaterializationCandidate", "PublicationEvidenceSet", "PublicationPolicy", "ReleaseTimeObservation", "PublicationResourceBudget"], "output_type": "Result<PublicationEligibilityReport,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
        {"operation_ref": "operation.pipeline.materialization-publication.form-publish-intent", "name": "form_materialization_publication_intent", "input_types": ["MaterializationCandidate", "PublicationEligibilityReport", "PublicationAuthorityGrant", "ExpectedPublicationHead", "PublicationCommandContext"], "output_type": "Result<PublicationEffectIntent,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": "PublicationEffectIntent", "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
        {"operation_ref": "operation.pipeline.materialization-publication.form-supersede-intent", "name": "form_materialization_supersession_intent", "input_types": ["MaterializationPublication", "MaterializationCandidate", "PublicationEligibilityReport", "PublicationAuthorityGrant", "ExpectedPublicationHead", "PublicationCommandContext"], "output_type": "Result<SupersessionEffectIntent,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": "SupersessionEffectIntent", "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
        {"operation_ref": "operation.pipeline.materialization-publication.form-recall-intent", "name": "form_materialization_recall_intent", "input_types": ["MaterializationPublication", "PublicationAuthorityGrant", "PublicationCommandContext"], "output_type": "Result<RecallEffectIntent,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": "RecallEffectIntent", "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
        {"operation_ref": "operation.pipeline.materialization-publication.classify-receipt", "name": "classify_publication_effect_receipt", "input_types": ["PublicationEffectIntent", "PublicationEffectReceipt", "PublicationPolicy"], "output_type": "Result<PublicationEffectClassification,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
        {"operation_ref": "operation.pipeline.materialization-publication.reconcile", "name": "reconcile_unknown_publication", "input_types": ["PublicationEffectIntent", "PublicationObservationSet", "PublicationReconciliationPolicy", "PublicationResourceBudget"], "output_type": "Result<PublicationReconciliationResult,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
        {"operation_ref": "operation.pipeline.materialization-publication.reduce", "name": "reduce_materialization_publication", "input_types": ["MaterializationPublication", "MaterializationPublicationEvent", "PublicationPolicy"], "output_type": "Result<MaterializationPublication,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
        {"operation_ref": "operation.pipeline.materialization-publication.diff", "name": "compare_materialization_publications", "input_types": ["MaterializationPublicationComparison", "PublicationResourceBudget"], "output_type": "Result<MaterializationPublicationDiff,MaterializationPublicationRefusal>", "purity": "pure", "effect_intent_type": None, "receipt_type": None, "refusal_types": MATERIALIZATION_PUBLICATION_REFUSALS},
    ],
    "laws": [
        "a materialization candidate published materialization target object target version and consumer-visible alias are distinct identities",
        "candidate creation records an immutable proposed output occurrence and never registers publishes qualifies or accepts it",
        "target version identity is opaque outside one exact provider version-domain identity and edition; numeric lexical or timestamp comparison is never inferred",
        "content identity is optional only when policy says provider version identity and commit evidence are sufficient; absence is explicit and never replaced by object name",
        "a sink commit receipt proves only its declared atomicity durability and visibility scope and is not by itself publication eligibility publication authority publication completion or consumer acceptance",
        "quality assertion success severity gate verdict and waiver are distinct; this protocol consumes a gate verdict and never executes a quality algorithm or issues a waiver",
        "a complete blocking quality verdict yields an ineligible completed report; malformed stale missing or scope-mismatched quality evidence is a refusal",
        "lineage evidence is bound to the exact candidate and cut when required but lineage completeness proves neither quality truth nor business fitness",
        "publication policy and publication authority are distinct; policy determines required evidence while an external scoped grant authorizes one transition",
        "approval or eligibility never performs publication and a publication intent is not a publication fact",
        "a provider receipt is accepted only when it binds the exact intent digest idempotency scope fence target version and expected publication head",
        "unknown timeout cancellation or lost acknowledgement never becomes success; reconciliation precedes retry or transition",
        "on-commit visibility catalog ratification catalog publication branch fast-forward alias swap and registry listing are different mechanisms with explicit provider capability witnesses",
        "Delta-style ratified and published commits remain distinct even when an implementation performs both atomically",
        "Iceberg-style audit-branch validation and fast-forward publication never imply atomic publication across unrelated tables targets or systems",
        "publication supersession and recall are append-only lifecycle facts; they do not mutate or erase prior materializations receipts lineage or consumer observations",
        "supersession establishes a declared successor relation and never proves semantic equivalence or safe migration",
        "recall changes declared visibility or fitness posture but is not physical deletion rollback compensation or proof that prior consumers did not observe the output",
        "scheduled release uses an imported time observation bound to the policy edition; this pure protocol never reads a clock",
        "publication does not establish source truth data quality adequacy business fitness product-catalog acceptance deployment success or downstream outcome",
        "the protocol performs no storage catalog registry network clock signing credential or destructive effect and optional models or agents have no policy evidence waiver authority or effect authority",
    ],
    "oracles": [
        "candidate-commit-publication-negative-twins", "quality-success-severity-gate-waiver-decision-table",
        "delta-proposed-staged-ratified-published-state-fixtures", "iceberg-audit-branch-fast-forward-fixtures",
        "target-version-domain-opacity-properties", "authority-scope-expiry-and-revocation-tests",
        "expected-head-race-and-fence-model-checks", "idempotent-retry-and-intent-receipt-binding-properties",
        "unknown-completion-reconciliation-fault-injection", "supersede-recall-append-only-state-model",
        "multi-target-atomicity-nonclaim-negative-twins", "permutation-invariant-evidence-canonicalization",
        "two-independent-adapter-conformance", "cross-implementation-semantic-differential",
    ],
    "resource_contracts": [
        "eligibility and reconciliation are bounded by declared evidence findings target observations lifecycle events and output bytes",
        "evidence canonicalization and diff declare finite comparison allocation and digest-input budgets",
        "provider observation exhaustion returns reconciliation required or a typed refusal and never a partial publication fact",
        "no filesystem network clock randomness process environment credential store or hidden durable state",
    ],
    "configuration_contracts": [
        "PublicationPolicy", "PublicationPolicyEdition", "PublicationReconciliationPolicy",
        "PublicationResourceBudget",
    ],
    "dependencies": [
        "library.pipeline.identity_types", "library.pipeline.data_cut_algebra",
        "library.pipeline.sink_committer", "library.pipeline.lineage_receipts",
        "library.qor.quarantine_release_kernel",
    ],
    "evidence_refs": [
        "src.iceberg.spec", "src.iceberg.branching", "src.delta.protocol",
        "src.openlineage.object_model", "src.openlineage.quality_assertions",
        "src.openlineage.version_facet", "src.w3c.shacl",
    ],
    "boundary_adjudication": {
        "decision_id": "boundary.pipeline.materialization-publication.v1",
        "disposition": "retain_but_narrow",
        "subject_refs": ["library.pipeline.materialization_publisher"],
        "rationale": "Retain one pure lifecycle/effect-intent protocol, but remove storage commit, quality evaluation, waiver issuance, authority issuance, effect execution, consumer acceptance and product-catalog publication.",
        "no_compatibility_alias": True,
    },
}

for candidate in LIBRARIES:
    if candidate["library_candidate_id"] == "library.pipeline.graph_algebra":
        candidate.update(GRAPH_ALGEBRA_CONTRACT)
    elif candidate["library_candidate_id"] == "library.pipeline.graph_validator":
        candidate.update(GRAPH_VALIDATOR_CONTRACT)
    elif candidate["library_candidate_id"] == "library.pipeline.port_typechecker":
        candidate.update(PORT_TYPECHECKER_CONTRACT)
    elif candidate["library_candidate_id"] == "library.pipeline.data_cut_algebra":
        candidate.update(DATA_CUT_CONTRACT)
    elif candidate["library_candidate_id"] == "library.pipeline.materialization_publisher":
        candidate.update(MATERIALIZATION_PUBLICATION_CONTRACT)


def requirement(req_id: str, owner: str, phase: str, statement: str, required_fields: list[str], evidence: list[str]) -> dict:
    return {"requirement_id": f"requirement.pipeline.{req_id}", "edition": 1, "owner_context": owner, "binding_phase": phase, "statement": statement, "required_contract_fields": required_fields, "prohibited_shortcuts": ["vendor-name dispatch", "hidden default", "capability inferred from marketing label"], "proof_obligations": evidence, "blocking": True, "llm_dependency": "none"}


REQUIREMENTS = [
    requirement("graph_lawful", "ppl.graph_topology", "logical", "The graph is well-formed and every cycle is lawful.", ["nodes", "edges", "ports", "cycle policy"], ["graph validation receipt"]),
    requirement("ports_compatible", "ppl.port_contract", "logical", "Every connected port is compatible across all semantic dimensions.", ["carrier", "schema", "update model", "time", "ordering", "cardinality"], ["port compatibility witnesses"]),
    requirement("unbounded_progress", "ppl.event_time_progress", "logical", "Every unbounded path has explicit progress and late-data behavior.", ["progress contract", "idleness", "late horizon"], ["progress law tests"]),
    requirement("state_bounded", "ppl.operator_state", "logical", "Every stateful node declares scope, bound, TTL, durability and migration.", ["state contracts"], ["state-bound proof"]),
    requirement("incremental_equivalence", "ppl.incremental_computation", "logical", "Incremental lowering preserves declared batch observable semantics.", ["change algebra", "equivalence scope"], ["property oracle", "recompute comparison"]),
    requirement("source_cut", "ppl.data_cut", "observation", "Input positions form a reproducible authoritative data cut.", ["source positions", "closure law"], ["source metadata receipt", "cut closure witness"]),
    requirement("snapshot_change_complete", "ppl.snapshot_change_handoff", "observation", "Baseline and change stream have no unaccounted gap or overlap.", ["handoff strategy", "restart context"], ["handoff completeness receipt"]),
    requirement("source_replay", "ppl.delivery_guarantee", "assurance", "Source replay capability covers the declared failure window.", ["position domain", "retention", "seek semantics"], ["connector capability test"]),
    requirement("channel_finite", "ppl.flow_control", "physical", "Every channel has a finite capacity and overload action.", ["capacity", "demand protocol", "overflow"], ["load test", "flow-control conformance"]),
    requirement("partition_laws", "ppl.partition_exchange", "physical", "Partitioning preserves required key colocation and ordering.", ["partition function", "exchange", "rescaling"], ["partition law tests"]),
    requirement("checkpoint_recovery", "ppl.checkpoint_coordination", "physical", "A qualified checkpoint path can restore state and positions under the declared failure model.", ["checkpoint mode", "state backend", "source positions"], ["failure injection restore test"]),
    requirement("sink_effect", "ppl.sink_commit", "physical", "Sink effects meet atomicity, idempotency, visibility and durability contracts.", ["commit protocol", "idempotency", "visibility"], ["sink conformance receipts"]),
    requirement("end_to_end_delivery", "ppl.delivery_guarantee", "assurance", "The requested delivery guarantee is proven end to end.", ["source", "execution", "checkpoint", "sink", "failure model"], ["composed guarantee proof"]),
    requirement("retry_safe", "ppl.retry", "operations", "Every retry site has finite budget, total classification and effect safety.", ["retry policy", "effect boundary"], ["failure matrix", "idempotency/transaction proof"]),
    requirement("cancel_total", "ppl.cancellation", "operations", "Cancellation defines every in-flight and external-effect disposition.", ["scope", "propagation", "cleanup", "partial output"], ["cancellation conformance test"]),
    requirement("backfill_explicit", "ppl.backfill", "operations", "Backfill fixes data cuts, edition, existing-output disposition and finite concurrency.", ["coverage", "edition", "reprocessing", "concurrency"], ["dry-run plan", "reconciliation receipt"]),
    requirement("deployment_pinned", "ppl.deployment_binding", "physical", "Deployment pins plan, artifact digests, target qualifications and secret references.", ["plan id", "artifacts", "target", "secret refs"], ["deployment manifest signature"]),
    requirement("resources_feasible", "ppl.execution_plan", "physical", "Plan fits finite compute, memory, state, network, I/O, latency and cost budgets.", ["resource estimates", "budgets", "SLO"], ["capacity proof", "benchmark evidence"]),
    requirement("quality_gated", "ppl.quality_gate", "evidence", "Required quality gates bind to exact outputs and control publication.", ["checks", "materialization", "gate precedence"], ["quality receipts"]),
    requirement("lineage_complete", "ppl.lineage_receipt", "evidence", "Required declared and observed lineage is identity-complete.", ["inputs", "activities", "agents", "outputs"], ["lineage coverage report"]),
    requirement("telemetry_correlated", "ppl.observability", "operations", "Runtime telemetry correlates to run, attempt, plan and deployment identities.", ["correlation keys", "sampling", "clock"], ["telemetry conformance"]),
    requirement("upgrade_safe", "ppl.pipeline_change", "operations", "Plan changes classify semantic/state compatibility and in-flight disposition.", ["semantic diff", "state migration", "rollout"], ["canary/parallel comparison"]),
    requirement("maintenance_safe", "ppl.maintenance", "operations", "Maintenance cannot destroy live replay, restore, audit or rollback obligations.", ["reference graph", "retention policy"], ["reachability proof", "deletion receipt"]),
]


OFFER_TEMPLATES = [
    {"offer_template_id": f"offer-template.pipeline.{kind}", "edition": 1, "capability_kind": kind, "required_claim_fields": fields, "required_limit_fields": ["max throughput", "max state or buffer", "supported targets", "unsupported combinations", "edition compatibility"], "required_receipts": receipts, "binding_rule": "An instance is matchable only after exact semantic, operational, resource and evidence fields are populated; a template is not itself an offer.", "llm_dependency": "none"}
    for kind, fields, receipts in [
        ("source_reader", ["position domain", "snapshot consistency", "resume", "retention"], ["read conformance", "failure recovery"]),
        ("cdc_reader", ["change envelope", "transaction metadata", "schema changes", "gap detection"], ["snapshot/change handoff test"]),
        ("transport_channel", ["ordering", "ack boundary", "capacity", "flow control"], ["backpressure test", "failure redelivery test"]),
        ("logical_operator", ["typed signature", "laws", "update support", "determinism"], ["law tests"]),
        ("incremental_operator", ["change algebra", "state", "retractions", "equivalence scope"], ["batch equivalence test"]),
        ("stream_time", ["watermarks/frontiers", "idleness", "alignment", "late handling"], ["out-of-order conformance"]),
        ("state_backend", ["state forms", "durability", "snapshot", "restore", "migration"], ["failure restore test"]),
        ("checkpoint_runtime", ["alignment modes", "channel state", "completion", "retention"], ["failure injection test"]),
        ("sink_committer", ["atomicity", "idempotency", "abort", "visibility", "durability"], ["indeterminate commit reconciliation"]),
        ("scheduler", ["triggers", "misfires", "dependencies", "concurrency", "leases"], ["state-machine conformance"]),
        ("task_executor", ["artifact types", "isolation", "cancellation", "heartbeats", "fencing"], ["lease-loss test"]),
        ("deployment_target", ["artifact binding", "placement", "resources", "rollout"], ["qualification receipt"]),
        ("lineage_emitter", ["job/run/dataset identity", "facets", "delivery", "signing"], ["schema conformance", "coverage test"]),
        ("telemetry_emitter", ["traces", "metrics", "logs", "correlation", "sampling"], ["telemetry conformance"]),
        ("materialization_store", ["version identity", "commit", "time travel", "change view", "retention"], ["commit and read visibility test"]),
    ]
]


CENTRAL_OPERATION_IDS = [
    "operation.discovery_metadata.discover_partition_layout",
    "operation.discovery_metadata.discover_change_capability",
    "operation.discovery_metadata.discover_retention_boundary",
    "operation.discovery_metadata.discover_consistency_level",
    "operation.discovery_metadata.discover_ordering_guarantee",
    "operation.discovery_metadata.discover_finality_guarantee",
    "operation.snapshot_extract.query_source_snapshot",
    "operation.snapshot_extract.read_source_range",
    "operation.snapshot_extract.read_source_partition",
    "operation.snapshot_extract.advance_page_cursor",
    "operation.snapshot_extract.parallelize_source_scan",
    "operation.snapshot_extract.read_database_snapshot",
    "operation.snapshot_extract.read_consistent_multi_object_snapshot",
    "operation.snapshot_extract.read_point_in_time_state",
    "operation.snapshot_extract.read_transaction_log",
    "operation.snapshot_extract.read_bulk_export",
    "operation.snapshot_extract.read_federated_source",
    "operation.snapshot_extract.preflight_extraction",
    "operation.snapshot_extract.cancel_source_read",
    "operation.snapshot_extract.resume_source_read",
    "operation.change_capture.initialize_change_capture",
    "operation.change_capture.capture_insert_change",
    "operation.change_capture.capture_update_change",
    "operation.change_capture.capture_delete_change",
    "operation.change_capture.capture_schema_change",
    "operation.change_capture.normalize_change_envelope",
    "operation.change_capture.identify_transaction_boundary",
    "operation.change_capture.order_change_records",
    "operation.change_capture.deduplicate_change_delivery",
    "operation.change_capture.detect_change_gap",
    "operation.change_capture.repair_change_gap",
    "operation.change_capture.checkpoint_change_offset",
    "operation.change_capture.resume_change_offset",
    "operation.change_capture.seek_change_offset",
    "operation.change_capture.acknowledge_change_delivery",
    "operation.change_capture.bootstrap_snapshot_plus_changes",
    "operation.change_capture.handoff_snapshot_to_changes",
    "operation.change_capture.reconcile_snapshot_with_changes",
    "operation.change_capture.detect_source_rewind",
    "operation.change_capture.handle_log_truncation",
    "operation.change_capture.validate_change_completeness",
    "operation.change_capture.measure_change_lag",
    "operation.delivery_sink.stage_sink_write",
    "operation.delivery_sink.validate_staged_write",
    "operation.delivery_sink.commit_sink_write",
    "operation.delivery_sink.abort_sink_write",
    "operation.delivery_sink.retry_sink_write",
    "operation.delivery_sink.deduplicate_sink_write",
    "operation.delivery_sink.acknowledge_sink_delivery",
    "operation.delivery_sink.verify_sink_visibility",
    "operation.delivery_sink.verify_sink_durability",
    "operation.delivery_sink.reconcile_sink_result",
    "operation.delivery_sink.compensate_sink_write",
    "operation.delivery_sink.quarantine_failed_delivery",
    "operation.delivery_sink.rate_limit_sink_delivery",
    "operation.delivery_sink.batch_sink_delivery",
    "operation.delivery_sink.flush_sink_buffer",
    "operation.delivery_sink.emit_delivery_receipt",
    "operation.stream_window.assign_watermark",
    "operation.stream_window.advance_watermark",
    "operation.stream_window.detect_idle_partition",
    "operation.stream_window.reorder_event_stream",
    "operation.stream_window.classify_late_event",
    "operation.stream_window.drop_late_event",
    "operation.stream_window.side_output_late_event",
    "operation.stream_window.retract_prior_result",
    "operation.stream_window.upsert_changed_result",
    "operation.stream_window.emit_changelog",
    "operation.stream_window.open_tumbling_window",
    "operation.stream_window.open_sliding_window",
    "operation.stream_window.open_session_window",
    "operation.stream_window.trigger_window_early",
    "operation.stream_window.trigger_window_on_time",
    "operation.stream_window.trigger_window_late",
    "operation.stream_window.accumulate_window_state",
    "operation.stream_window.evict_window_state",
    "operation.stream_window.close_window",
    "operation.stream_window.merge_session_windows",
    "operation.stream_window.checkpoint_stream_state",
    "operation.stream_window.restore_stream_state",
    "operation.stream_window.rescale_stream_state",
    "operation.stream_window.compact_stream_state",
    "operation.stream_window.apply_backpressure",
    "operation.stream_window.emit_stream_progress",
    "operation.sampling_partition.partition_by_key",
    "operation.sampling_partition.partition_by_range",
    "operation.sampling_partition.partition_by_time",
    "operation.sampling_partition.partition_by_hash",
    "operation.sampling_partition.repartition_collection",
    "operation.sampling_partition.coalesce_partitions",
    "operation.sampling_partition.balance_partitions",
    "operation.sampling_partition.detect_partition_skew",
    "operation.orchestration.compile_job_graph",
    "operation.orchestration.validate_job_graph",
    "operation.orchestration.topologically_order_jobs",
    "operation.orchestration.plan_job_execution",
    "operation.orchestration.schedule_job",
    "operation.orchestration.start_job",
    "operation.orchestration.pause_job",
    "operation.orchestration.resume_job",
    "operation.orchestration.cancel_job",
    "operation.orchestration.retry_job",
    "operation.orchestration.skip_job",
    "operation.orchestration.rerun_job",
    "operation.orchestration.backfill_job",
    "operation.orchestration.replay_job",
    "operation.orchestration.branch_job_run",
    "operation.orchestration.join_job_branches",
    "operation.orchestration.wait_for_dependency",
    "operation.orchestration.wait_for_external_signal",
    "operation.orchestration.emit_job_signal",
    "operation.orchestration.evaluate_job_condition",
    "operation.orchestration.apply_retry_policy",
    "operation.orchestration.apply_timeout_policy",
    "operation.orchestration.apply_compensation_policy",
    "operation.orchestration.record_job_heartbeat",
    "operation.orchestration.detect_stalled_job",
    "operation.orchestration.recover_abandoned_job",
    "operation.orchestration.deduplicate_job_request",
    "operation.orchestration.checkpoint_job_progress",
    "operation.orchestration.emit_job_outcome",
    "operation.orchestration.reconcile_desired_and_actual_job_state",
    "operation.orchestration.enforce_concurrency_limit",
    "operation.orchestration.enforce_execution_window",
    "operation.orchestration.apply_maintenance_calendar",
    "operation.runtime_resource.estimate_resource_requirement",
    "operation.runtime_resource.reserve_compute_resource",
    "operation.runtime_resource.release_compute_resource",
    "operation.runtime_resource.scale_compute_resource",
    "operation.runtime_resource.place_workload",
    "operation.runtime_resource.preempt_workload",
    "operation.runtime_resource.admit_workload",
    "operation.runtime_resource.enforce_cpu_budget",
    "operation.runtime_resource.enforce_memory_budget",
    "operation.runtime_resource.enforce_storage_budget",
    "operation.runtime_resource.enforce_network_budget",
    "operation.runtime_resource.enforce_i_o_budget",
    "operation.runtime_resource.enforce_cost_budget",
    "operation.runtime_resource.precharge_finite_budget",
    "operation.runtime_resource.throttle_workload",
    "operation.runtime_resource.spill_intermediate_state",
    "operation.runtime_resource.cancel_resource_usage",
    "operation.runtime_resource.emit_resource_receipt",
    "operation.transaction_consistency.compensate_transaction",
    "operation.transaction_consistency.retry_transaction",
    "operation.transaction_consistency.emit_transaction_receipt",
    "operation.lineage_provenance.record_data_origin",
    "operation.lineage_provenance.record_derivation_activity",
    "operation.lineage_provenance.record_responsible_agent",
    "operation.lineage_provenance.record_operation_invocation",
    "operation.lineage_provenance.record_input_identity",
    "operation.lineage_provenance.record_output_identity",
    "operation.lineage_provenance.record_parameter_values",
    "operation.lineage_provenance.record_code_identity",
    "operation.lineage_provenance.record_environment_identity",
    "operation.lineage_provenance.record_provider_identity",
    "operation.lineage_provenance.construct_lineage_edge",
    "operation.lineage_provenance.validate_lineage_completeness",
    "operation.lineage_provenance.reconcile_lineage_evidence",
    "operation.lineage_provenance.emit_execution_receipt",
    "operation.lineage_provenance.bind_evidence_to_requirement",
    "operation.version_migration.replay_historical_event",
    "operation.version_migration.validate_migrated_state",
    "operation.version_migration.emit_migration_receipt",
]


def owner_for_operation(operation_id: str) -> str:
    family = operation_id.split(".")[1]
    return {
        "discovery_metadata": "ppl.ingestion_contract",
        "snapshot_extract": "ppl.ingestion_contract",
        "change_capture": "ppl.change_capture_coordination",
        "delivery_sink": "ppl.sink_commit",
        "stream_window": "ppl.window_trigger",
        "sampling_partition": "ppl.partition_exchange",
        "orchestration": "ppl.orchestration_control",
        "runtime_resource": "runtime.resource-control",
        "transaction_consistency": "ppl.compensation",
        "lineage_provenance": "ppl.lineage_receipt",
        "version_migration": "ppl.pipeline_change",
    }[family]


OPERATION_MAPPINGS = [
    {
        "mapping_id": f"pipeline-map.{operation_id.removeprefix('operation.')}",
        "edition": 1,
        "pipeline_context_id": owner_for_operation(operation_id),
        "central_operation_id": operation_id,
        "mapping_role": "owned" if owner_for_operation(operation_id).startswith("ppl.") else "neighbor_requirement",
        "coverage": "direct_candidate",
        "notes": "The central operation identity is reused; the pipeline context supplies lifecycle and composition constraints, not a duplicate operation.",
    }
    for operation_id in CENTRAL_OPERATION_IDS
]


GAPS = [
    {"gap_id": "gap.pipeline.central_operations_progress_frontier", "edition": 1, "severity": "blocking_for_compilation", "area": "operation_registry", "statement": "The central operation registry has watermark operations but no adjudicated partially ordered frontier/capability algebra.", "needed_evidence": ["Timely-style frontier laws", "two implementation mappings"], "owner_candidate": "ppl.event_time_progress"},
    {"gap_id": "gap.pipeline.central_operations_cycle", "edition": 1, "severity": "blocking_for_compilation", "area": "operation_registry", "statement": "Iteration epoch, feedback delay, fixed-point test and productive-cycle operations are not explicit central operation identities.", "needed_evidence": ["iterative dataflow semantics", "termination/property tests"], "owner_candidate": "ppl.iterative_dataflow"},
    {"gap_id": "gap.pipeline.channel_protocol", "edition": 1, "severity": "blocking_for_binding", "area": "runtime", "statement": "No universal channel offer contract yet composes ordering, capacity, acknowledgement, backpressure and barrier behavior.", "needed_evidence": ["Reactive Streams mapping", "message-log mapping", "in-process channel mapping"], "owner_candidate": "ppl.channel_contract"},
    {"gap_id": "gap.pipeline.exactly_once_scope", "edition": 1, "severity": "blocking_for_claim", "area": "assurance", "statement": "A machine-checkable end-to-end guarantee proof calculus remains candidate and must distinguish processing from observable effects.", "needed_evidence": ["source replay tests", "checkpoint failure tests", "sink transaction/idempotency tests"], "owner_candidate": "ppl.delivery_guarantee"},
    {"gap_id": "gap.pipeline.snapshot_change_generality", "edition": 1, "severity": "research", "area": "cdc", "statement": "Snapshot/change handoff laws require adjudication across relational logs, document databases, APIs and object manifests.", "needed_evidence": ["at least four source-family mappings", "gap/overlap adversarial tests"], "owner_candidate": "ppl.snapshot_change_handoff"},
    {"gap_id": "gap.pipeline.materialization_identity", "edition": 1, "severity": "blocking_for_publication", "area": "identity", "statement": "A universal materialization identity must compose table snapshots, files/manifests, indexes, API destinations and message ranges without collapsing them.", "needed_evidence": ["identity profiles per carrier", "cross-version rules"], "owner_candidate": "ppl.materialization"},
    {"gap_id": "gap.pipeline.dynamic_graph", "edition": 1, "severity": "research", "area": "topology", "statement": "Dynamic task expansion and truly dynamic graph mutation need separate boundedness and replay semantics.", "needed_evidence": ["Airflow dynamic mapping", "Beam splitting", "workflow child execution"], "owner_candidate": "ppl.graph_topology"},
    {"gap_id": "gap.pipeline.federated_equivalence", "edition": 1, "severity": "blocking_for_pushdown", "area": "federation", "statement": "Pushdown compatibility requires exact remote null, collation, time, numeric and error semantics, not operator-name equality.", "needed_evidence": ["provider semantic profiles", "differential conformance suite"], "owner_candidate": "ppl.federated_flow"},
    {"gap_id": "gap.pipeline.cross_sink_atomicity", "edition": 1, "severity": "blocking_for_guarantee", "area": "transactions", "statement": "Atomic publication across heterogeneous sinks is not generally available and must lower to transactions, idempotency plus reconciliation, or compensation.", "needed_evidence": ["multi-sink failure matrix", "indeterminate commit protocol"], "owner_candidate": "ppl.sink_commit"},
    {"gap_id": "gap.pipeline.state_migration", "edition": 1, "severity": "blocking_for_upgrade", "area": "state", "statement": "Portable state schema and migration contracts across independent stream engines are not standardized.", "needed_evidence": ["Flink savepoint mapping", "Spark state mapping", "independent backend mapping"], "owner_candidate": "ppl.pipeline_change"},
    {"gap_id": "gap.pipeline.backfill_incremental", "edition": 1, "severity": "research", "area": "backfill", "statement": "Correct backfill in pipelines with downstream incremental state needs dependency-aware cut and publication planning.", "needed_evidence": ["partition mapping laws", "mixed live/backfill adversarial scenarios"], "owner_candidate": "ppl.backfill"},
    {"gap_id": "gap.pipeline.compression_boundary", "edition": 1, "severity": "binding", "area": "transport", "statement": "Compression is currently only a decision placeholder; codecs need offers for ratio, CPU, memory, seekability, splittability, dictionaries and corruption behavior.", "needed_evidence": ["codec capability registry", "representative benchmarks", "format compatibility tests"], "owner_candidate": "ppl.transport_contract"},
    {"gap_id": "gap.pipeline.receipt_signing", "edition": 1, "severity": "assurance", "area": "evidence", "statement": "Receipt signing, key authority, redaction and long-term verification profiles are not yet bound.", "needed_evidence": ["signature profile", "key rotation and revocation laws"], "owner_candidate": "ppl.lineage_receipt"},
    {"gap_id": "gap.pipeline.two_implementations", "edition": 1, "severity": "validation", "area": "generality", "statement": "Every core semantic and runtime contract still needs conformance against two independent implementations.", "needed_evidence": ["implementation A", "implementation B", "negative twins"], "owner_candidate": "pipeline_dataflow_universe"},
]


SCHEMA_URI = "https://san.example/spec/pipeline-dataflow"


def object_schema(title: str, required: list[str], properties: dict, *, schema_id: str) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SCHEMA_URI}/{schema_id}.schema.json",
        "title": title,
        "type": "object",
        "required": required,
        "properties": properties,
        "additionalProperties": False,
    }


STR = {"type": "string", "minLength": 1}
STRINGS = {"type": "array", "items": STR, "uniqueItems": True}
ID = {"type": "string", "pattern": "^[a-z][a-z0-9_.:-]+$"}
EDITION_PROP = {"type": "integer", "minimum": 1}


PORT_SCHEMA = object_schema(
    "Pipeline port definition",
    ["port_id", "edition", "direction", "carrier_ref", "shape_ref", "boundedness", "update_model", "cardinality", "time_contract", "ordering", "partitioning", "null_missing", "schema_evolution", "decision_bindings"],
    {
        "port_id": ID,
        "edition": EDITION_PROP,
        "direction": {"enum": ["input", "output"]},
        "carrier_ref": STR,
        "shape_ref": STR,
        "boundedness": {"enum": ["bounded", "unbounded", "bounded_per_cut"]},
        "update_model": {"enum": ["snapshot", "append", "upsert", "retract", "full_changelog", "control_only"]},
        "cardinality": {"enum": ["zero_or_one", "exactly_one", "zero_or_more", "one_or_more"]},
        "time_contract": {"type": "object", "required": ["domains", "progress_ref"], "properties": {"domains": {"type": "array", "items": {"enum": ["event_time", "processing_time", "valid_time", "recording_time", "commit_time"]}, "uniqueItems": True}, "progress_ref": {"type": ["string", "null"]}}, "additionalProperties": False},
        "ordering": {"enum": ["none", "per_key", "per_partition", "total", "causal"]},
        "partitioning": {"type": "object", "required": ["kind", "key_refs"], "properties": {"kind": {"enum": ["none", "hash", "range", "round_robin", "broadcast", "singleton", "provider"]}, "key_refs": STRINGS}, "additionalProperties": False},
        "null_missing": {"enum": ["distinct", "coalesced_with_declared_loss", "forbidden"]},
        "schema_evolution": {"enum": ["exact", "backward", "forward", "full", "explicit_transform"]},
        "decision_bindings": {"type": "object", "additionalProperties": {"type": ["string", "number", "integer", "boolean", "object", "array", "null"]}},
    },
    schema_id="port-definition-v0.1.0",
)


NODE_SCHEMA = object_schema(
    "Pipeline node definition",
    ["node_id", "edition", "node_kind", "operation_refs", "input_port_refs", "output_port_refs", "effect_class", "determinism", "idempotency", "state_contract_refs", "retry_policy_ref", "resource_requirements", "decision_bindings"],
    {
        "node_id": ID,
        "edition": EDITION_PROP,
        "node_kind": {"enum": ["source", "transform", "router", "union", "exchange", "barrier", "delay", "loop_head", "loop_tail", "subflow", "quality_gate", "materializer", "sink", "control"]},
        "operation_refs": STRINGS,
        "input_port_refs": STRINGS,
        "output_port_refs": STRINGS,
        "effect_class": {"enum": ["pure", "reads_external", "writes_external", "read_write_external", "control_effect"]},
        "determinism": {"enum": ["deterministic", "seeded", "environment_dependent", "nondeterministic_refused"]},
        "idempotency": {"enum": ["always", "by_key", "conditional", "never", "not_applicable"]},
        "state_contract_refs": STRINGS,
        "retry_policy_ref": {"type": ["string", "null"]},
        "resource_requirements": {"type": "object", "required": ["bounded"], "properties": {"bounded": {"type": "boolean"}, "expressions": STRINGS}, "additionalProperties": False},
        "decision_bindings": {"type": "object", "additionalProperties": True},
    },
    schema_id="node-definition-v0.1.0",
)


EDGE_SCHEMA = object_schema(
    "Pipeline edge definition",
    ["edge_id", "edition", "from_port_ref", "to_port_ref", "edge_kind", "channel", "barrier_behavior", "failure_propagation", "decision_bindings"],
    {
        "edge_id": ID,
        "edition": EDITION_PROP,
        "from_port_ref": STR,
        "to_port_ref": STR,
        "edge_kind": {"enum": ["data", "control", "progress", "barrier", "error", "compensation", "feedback"]},
        "channel": {"type": "object", "required": ["mode", "capacity", "flow_control", "delivery", "serialization", "compression"], "properties": {"mode": {"enum": ["in_process", "network", "durable_log", "object_manifest", "database", "provider"]}, "capacity": {"type": "object", "required": ["unit", "maximum"], "properties": {"unit": {"enum": ["records", "bytes", "batches"]}, "maximum": {"type": "integer", "minimum": 1}}, "additionalProperties": False}, "flow_control": {"enum": ["pull", "credit", "backpressure", "bounded_push"]}, "delivery": {"enum": ["at_most_once", "at_least_once", "transactional"]}, "serialization": STR, "compression": STR}, "additionalProperties": False},
        "barrier_behavior": {"enum": ["forward", "align", "snapshot_in_flight", "not_applicable"]},
        "failure_propagation": {"enum": ["fail_downstream", "fail_component", "side_output", "supervise", "compensate"]},
        "decision_bindings": {"type": "object", "additionalProperties": True},
    },
    schema_id="edge-definition-v0.1.0",
)


STATE_SCHEMA = object_schema(
    "Operator state contract",
    ["state_contract_id", "edition", "state_kind", "scope", "key_shape_ref", "value_shape_ref", "bound", "durability", "ttl", "checkpoint", "migration", "concurrency", "decision_bindings"],
    {
        "state_contract_id": ID,
        "edition": EDITION_PROP,
        "state_kind": {"enum": ["value", "list", "map", "reducing", "aggregating", "broadcast", "timer", "frontier", "dedup_index", "transaction"]},
        "scope": {"enum": ["key", "key_window", "operator", "partition", "run", "global"]},
        "key_shape_ref": {"type": ["string", "null"]},
        "value_shape_ref": STR,
        "bound": {"type": "object", "required": ["kind", "expression"], "properties": {"kind": {"enum": ["ttl", "window_close", "cardinality", "compaction_frontier", "finite_input", "explicit_unbounded"]}, "expression": STR}, "additionalProperties": False},
        "durability": {"enum": ["ephemeral", "attempt", "worker", "run", "deployment", "cross_region"]},
        "ttl": {"type": "object", "required": ["time_domain", "duration", "expiry_visibility"], "properties": {"time_domain": {"enum": ["event_time", "processing_time", "valid_time", "explicit_signal", "none"]}, "duration": {"type": ["string", "null"]}, "expiry_visibility": {"enum": ["silent", "tombstone", "receipt", "not_applicable"]}}, "additionalProperties": False},
        "checkpoint": {"type": "object", "required": ["participates", "consistency"], "properties": {"participates": {"type": "boolean"}, "consistency": {"enum": ["none", "local", "barrier_consistent", "transactional"]}}, "additionalProperties": False},
        "migration": {"type": "object", "required": ["compatibility", "upcaster_refs"], "properties": {"compatibility": {"enum": ["exact", "backward", "requires_transform", "discardable_with_approval"]}, "upcaster_refs": STRINGS}, "additionalProperties": False},
        "concurrency": {"enum": ["single_writer", "partition_confined", "optimistic", "serialized", "commutative"]},
        "decision_bindings": {"type": "object", "additionalProperties": True},
    },
    schema_id="state-contract-v0.1.0",
)


DELIVERY_SCHEMA = object_schema(
    "End-to-end delivery contract",
    ["delivery_contract_id", "edition", "observation_boundary", "multiplicity", "ordering_scope", "atomicity_scope", "source_replay", "execution_recovery", "sink_effect", "acknowledgement_boundary", "deduplication", "visibility", "failure_model", "proof_obligations", "decision_bindings"],
    {
        "delivery_contract_id": ID,
        "edition": EDITION_PROP,
        "observation_boundary": STR,
        "multiplicity": {"enum": ["at_most_once", "at_least_once", "effectively_once", "exactly_once_effect"]},
        "ordering_scope": {"enum": ["none", "per_key", "per_partition", "transaction", "total"]},
        "atomicity_scope": {"enum": ["record", "batch", "partition", "table", "multi_table", "external_workflow"]},
        "source_replay": {"type": "object", "required": ["required", "position_domain", "minimum_retention"], "properties": {"required": {"type": "boolean"}, "position_domain": STR, "minimum_retention": STR}, "additionalProperties": False},
        "execution_recovery": {"type": "object", "required": ["checkpoint_ref", "determinism_scope"], "properties": {"checkpoint_ref": {"type": ["string", "null"]}, "determinism_scope": STR}, "additionalProperties": False},
        "sink_effect": {"type": "object", "required": ["mechanism", "idempotency_scope", "reconciliation"], "properties": {"mechanism": {"enum": ["transaction", "idempotency_key", "commutative", "compensation", "none"]}, "idempotency_scope": {"type": ["string", "null"]}, "reconciliation": STR}, "additionalProperties": False},
        "acknowledgement_boundary": STR,
        "deduplication": {"type": "object", "required": ["key", "horizon"], "properties": {"key": {"type": ["string", "null"]}, "horizon": {"type": ["string", "null"]}}, "additionalProperties": False},
        "visibility": {"enum": ["on_ack", "read_after_write", "snapshot_commit", "external_receipt"]},
        "failure_model": STRINGS,
        "proof_obligations": STRINGS,
        "decision_bindings": {"type": "object", "additionalProperties": True},
    },
    schema_id="delivery-contract-v0.1.0",
)


RECOVERY_SCHEMA = object_schema(
    "Pipeline recovery contract",
    ["recovery_contract_id", "edition", "failure_domains", "checkpoint_policy", "retry_policy", "replay_policy", "backfill_policy", "compensation_policy", "cancellation_policy", "partial_output_policy", "orphan_policy", "liveness", "decision_bindings"],
    {
        "recovery_contract_id": ID,
        "edition": EDITION_PROP,
        "failure_domains": {"type": "array", "items": {"enum": ["record", "operator", "task", "worker", "stage", "run", "coordinator", "zone", "region", "source", "sink"]}, "uniqueItems": True},
        "checkpoint_policy": STR,
        "retry_policy": STR,
        "replay_policy": STR,
        "backfill_policy": STR,
        "compensation_policy": STR,
        "cancellation_policy": STR,
        "partial_output_policy": {"enum": ["discard", "quarantine", "retain_unpublished", "compensate", "provider_transaction"]},
        "orphan_policy": {"enum": ["fence_and_reclaim", "wait", "human_reconcile"]},
        "liveness": {"type": "object", "required": ["heartbeat", "lease", "stall"], "properties": {"heartbeat": STR, "lease": STR, "stall": STR}, "additionalProperties": False},
        "decision_bindings": {"type": "object", "additionalProperties": True},
    },
    schema_id="recovery-contract-v0.1.0",
)


PIPELINE_SCHEMA = object_schema(
    "Pipeline definition",
    ["definition_id", "edition", "status", "name", "execution_mode", "topology_kind", "parameter_schema_ref", "node_refs", "edge_refs", "entry_port_refs", "exit_port_refs", "state_contract_refs", "delivery_contract_ref", "recovery_contract_ref", "trigger", "policy_refs", "decision_bindings", "evidence_refs", "llm_dependency"],
    {
        "definition_id": ID,
        "edition": EDITION_PROP,
        "status": {"enum": ["draft", "validated", "published", "superseded", "retired"]},
        "name": STR,
        "execution_mode": {"enum": ["bounded_batch", "microbatch", "continuous_stream", "incremental_triggered", "interactive"]},
        "topology_kind": {"enum": ["dag", "feedback_cycle", "dynamic_graph", "nested_graph"]},
        "parameter_schema_ref": STR,
        "node_refs": STRINGS,
        "edge_refs": STRINGS,
        "entry_port_refs": STRINGS,
        "exit_port_refs": STRINGS,
        "state_contract_refs": STRINGS,
        "delivery_contract_ref": STR,
        "recovery_contract_ref": STR,
        "trigger": {"type": "object", "required": ["kind", "definition"], "properties": {"kind": {"enum": ["manual", "recurrence", "event", "materialization", "condition", "continuous"]}, "definition": {"type": "object"}}, "additionalProperties": False},
        "policy_refs": STRINGS,
        "decision_bindings": {"type": "object", "additionalProperties": True},
        "evidence_refs": STRINGS,
        "llm_dependency": {"const": "none"},
    },
    schema_id="pipeline-definition-v0.1.0",
)


DATA_CUT_SCHEMA = object_schema(
    "Data cut",
    ["data_cut_id", "edition", "status", "source_selections", "event_time_interval", "valid_time_interval", "recording_time_interval", "closure", "created_at", "evidence_refs"],
    {"data_cut_id": ID, "edition": EDITION_PROP, "status": {"enum": ["open", "closed", "invalidated"]}, "source_selections": {"type": "array", "minItems": 1, "items": {"type": "object", "required": ["source_ref", "position_domain", "start", "end", "snapshot_ref", "partitions"], "properties": {"source_ref": STR, "position_domain": STR, "start": {"type": ["string", "null"]}, "end": {"type": ["string", "null"]}, "snapshot_ref": {"type": ["string", "null"]}, "partitions": STRINGS}, "additionalProperties": False}}, "event_time_interval": {"type": ["object", "null"]}, "valid_time_interval": {"type": ["object", "null"]}, "recording_time_interval": {"type": ["object", "null"]}, "closure": {"type": "object", "required": ["law", "witness"], "properties": {"law": STR, "witness": STR}, "additionalProperties": False}, "created_at": STR, "evidence_refs": STRINGS},
    schema_id="data-cut-v0.1.0",
)


COMPILED_PLAN_SCHEMA = object_schema(
    "Compiled pipeline plan",
    ["plan_id", "edition", "definition_ref", "definition_edition", "logical_graph_digest", "physical_stages", "bindings", "decision_trace_refs", "proof_results", "resource_estimate", "artifact_refs", "status"],
    {"plan_id": ID, "edition": EDITION_PROP, "definition_ref": STR, "definition_edition": EDITION_PROP, "logical_graph_digest": STR, "physical_stages": {"type": "array", "minItems": 1, "items": {"type": "object", "required": ["stage_id", "node_refs", "operator_offer_refs", "parallelism", "exchange_refs"], "properties": {"stage_id": ID, "node_refs": STRINGS, "operator_offer_refs": STRINGS, "parallelism": {"type": "integer", "minimum": 1}, "exchange_refs": STRINGS}, "additionalProperties": False}}, "bindings": STRINGS, "decision_trace_refs": STRINGS, "proof_results": {"type": "array", "items": {"type": "object", "required": ["requirement_ref", "result", "evidence_refs"], "properties": {"requirement_ref": STR, "result": {"enum": ["proven", "refused", "waived"]}, "evidence_refs": STRINGS}, "additionalProperties": False}}, "resource_estimate": {"type": "object"}, "artifact_refs": STRINGS, "status": {"enum": ["candidate", "validated", "published", "invalidated"]}},
    schema_id="compiled-plan-v0.1.0",
)


DEPLOYMENT_SCHEMA = object_schema(
    "Pipeline deployment",
    ["deployment_id", "edition", "plan_ref", "plan_edition", "target_bindings", "artifact_digests", "secret_refs", "rollout", "operating_policies", "qualification_evidence_refs", "status"],
    {"deployment_id": ID, "edition": EDITION_PROP, "plan_ref": STR, "plan_edition": EDITION_PROP, "target_bindings": {"type": "array", "minItems": 1, "items": {"type": "object", "required": ["stage_ref", "target_profile_ref", "provider_offer_ref"], "properties": {"stage_ref": STR, "target_profile_ref": STR, "provider_offer_ref": STR}, "additionalProperties": False}}, "artifact_digests": {"type": "object", "minProperties": 1, "additionalProperties": STR}, "secret_refs": STRINGS, "rollout": {"enum": ["replace", "canary", "blue_green", "parallel_compare", "partitioned"]}, "operating_policies": STRINGS, "qualification_evidence_refs": STRINGS, "status": {"enum": ["draft", "qualified", "active", "draining", "retired"]}},
    schema_id="deployment-v0.1.0",
)


RUN_SCHEMA = object_schema(
    "Pipeline run",
    ["run_id", "edition", "deployment_ref", "deployment_edition", "plan_ref", "data_cut_ref", "trigger_observation_ref", "parameters_digest", "logical_time", "requested_at", "started_at", "ended_at", "state", "task_attempt_refs", "materialization_refs", "outcome_ref", "receipt_refs"],
    {"run_id": ID, "edition": EDITION_PROP, "deployment_ref": STR, "deployment_edition": EDITION_PROP, "plan_ref": STR, "data_cut_ref": STR, "trigger_observation_ref": STR, "parameters_digest": STR, "logical_time": STR, "requested_at": STR, "started_at": {"type": ["string", "null"]}, "ended_at": {"type": ["string", "null"]}, "state": {"enum": ["requested", "admitted", "running", "paused", "cancelling", "succeeded", "failed", "cancelled", "indeterminate"]}, "task_attempt_refs": STRINGS, "materialization_refs": STRINGS, "outcome_ref": {"type": ["string", "null"]}, "receipt_refs": STRINGS},
    schema_id="pipeline-run-v0.1.0",
)


ATTEMPT_SCHEMA = object_schema(
    "Task attempt",
    ["attempt_id", "edition", "run_ref", "stage_ref", "task_ref", "attempt_number", "worker_lease", "input_bindings", "state_restore_ref", "started_at", "heartbeat_at", "ended_at", "state", "effect_receipt_refs", "outcome_ref"],
    {"attempt_id": ID, "edition": EDITION_PROP, "run_ref": STR, "stage_ref": STR, "task_ref": STR, "attempt_number": {"type": "integer", "minimum": 1}, "worker_lease": {"type": "object", "required": ["lease_id", "worker_ref", "fence_token", "expires_at"], "properties": {"lease_id": STR, "worker_ref": STR, "fence_token": STR, "expires_at": STR}, "additionalProperties": False}, "input_bindings": STRINGS, "state_restore_ref": {"type": ["string", "null"]}, "started_at": {"type": ["string", "null"]}, "heartbeat_at": {"type": ["string", "null"]}, "ended_at": {"type": ["string", "null"]}, "state": {"enum": ["leased", "starting", "running", "checkpointing", "committing", "succeeded", "failed", "cancelled", "revoked", "indeterminate"]}, "effect_receipt_refs": STRINGS, "outcome_ref": {"type": ["string", "null"]}},
    schema_id="task-attempt-v0.1.0",
)


MATERIALIZATION_SCHEMA = object_schema(
    "Pipeline materialization",
    ["materialization_id", "edition", "run_ref", "producer_node_ref", "output_port_ref", "data_cut_ref", "object_ref", "version_identity", "content_identity", "commit_receipt_ref", "quality_receipt_refs", "lineage_receipt_ref", "visibility", "recorded_at", "status"],
    {"materialization_id": ID, "edition": EDITION_PROP, "run_ref": STR, "producer_node_ref": STR, "output_port_ref": STR, "data_cut_ref": STR, "object_ref": STR, "version_identity": STR, "content_identity": {"type": ["string", "null"]}, "commit_receipt_ref": STR, "quality_receipt_refs": STRINGS, "lineage_receipt_ref": STR, "visibility": {"enum": ["staged", "committed_unpublished", "published", "quarantined", "recalled", "superseded"]}, "recorded_at": STR, "status": {"enum": ["candidate", "qualified", "published", "recalled", "superseded"]}},
    schema_id="materialization-v0.1.0",
)


SCHEMAS = {
    "pipeline-definition.schema.json": PIPELINE_SCHEMA,
    "node-definition.schema.json": NODE_SCHEMA,
    "edge-definition.schema.json": EDGE_SCHEMA,
    "port-definition.schema.json": PORT_SCHEMA,
    "state-contract.schema.json": STATE_SCHEMA,
    "delivery-contract.schema.json": DELIVERY_SCHEMA,
    "recovery-contract.schema.json": RECOVERY_SCHEMA,
    "data-cut.schema.json": DATA_CUT_SCHEMA,
    "compiled-plan.schema.json": COMPILED_PLAN_SCHEMA,
    "deployment.schema.json": DEPLOYMENT_SCHEMA,
    "pipeline-run.schema.json": RUN_SCHEMA,
    "task-attempt.schema.json": ATTEMPT_SCHEMA,
    "materialization.schema.json": MATERIALIZATION_SCHEMA,
}


def port(port_id: str, direction: str, boundedness: str, update_model: str, *, progress: str | None = None, partition_key: list[str] | None = None) -> dict:
    return {
        "port_id": port_id,
        "edition": 1,
        "direction": direction,
        "carrier_ref": "carrier.structured.record_stream",
        "shape_ref": "shape.example.customer_change_v1",
        "boundedness": boundedness,
        "update_model": update_model,
        "cardinality": "zero_or_more",
        "time_contract": {"domains": ["event_time", "recording_time"], "progress_ref": progress},
        "ordering": "per_key",
        "partitioning": {"kind": "hash", "key_refs": partition_key or ["customer_id"]},
        "null_missing": "distinct",
        "schema_evolution": "backward",
        "decision_bindings": {"decision.pipeline.port_update_model": update_model, "decision.pipeline.ordering_scope": "per_key"},
    }


EXAMPLE_PORTS = [
    port("port.example.snapshot.rows", "output", "bounded_per_cut", "snapshot"),
    port("port.example.cdc.changes", "output", "unbounded", "full_changelog", progress="progress.example.source_lsn"),
    port("port.example.handoff.snapshot_in", "input", "bounded_per_cut", "snapshot"),
    port("port.example.handoff.changes_in", "input", "unbounded", "full_changelog", progress="progress.example.source_lsn"),
    port("port.example.handoff.out", "output", "unbounded", "full_changelog", progress="progress.example.source_lsn"),
    port("port.example.normalize.in", "input", "unbounded", "full_changelog", progress="progress.example.source_lsn"),
    port("port.example.normalize.out", "output", "unbounded", "full_changelog", progress="progress.example.source_lsn"),
    port("port.example.sink.in", "input", "unbounded", "full_changelog", progress="progress.example.source_lsn"),
    {**port("port.example.sink.receipt", "output", "bounded_per_cut", "control_only", partition_key=[]), "carrier_ref": "carrier.control.receipt", "shape_ref": "shape.pipeline.delivery_receipt_v1", "ordering": "none", "partitioning": {"kind": "none", "key_refs": []}, "time_contract": {"domains": ["recording_time"], "progress_ref": None}},
]


EXAMPLE_STATES = [
    {"state_contract_id": "state.example.snapshot_cursor", "edition": 1, "state_kind": "value", "scope": "run", "key_shape_ref": None, "value_shape_ref": "shape.source.chunk_cursor", "bound": {"kind": "finite_input", "expression": "one cursor per source table in the closed baseline cut"}, "durability": "run", "ttl": {"time_domain": "none", "duration": None, "expiry_visibility": "not_applicable"}, "checkpoint": {"participates": True, "consistency": "barrier_consistent"}, "migration": {"compatibility": "backward", "upcaster_refs": []}, "concurrency": "single_writer", "decision_bindings": {"decision.pipeline.snapshot_chunk_key": "primary_key"}},
    {"state_contract_id": "state.example.cdc_offset", "edition": 1, "state_kind": "frontier", "scope": "partition", "key_shape_ref": "shape.source.partition", "value_shape_ref": "shape.source.lsn", "bound": {"kind": "cardinality", "expression": "one durable offset per captured source partition"}, "durability": "deployment", "ttl": {"time_domain": "none", "duration": None, "expiry_visibility": "not_applicable"}, "checkpoint": {"participates": True, "consistency": "barrier_consistent"}, "migration": {"compatibility": "exact", "upcaster_refs": []}, "concurrency": "partition_confined", "decision_bindings": {"decision.pipeline.cursor_commit_boundary": "after_sink_commit"}},
    {"state_contract_id": "state.example.overlap_buffer", "edition": 1, "state_kind": "map", "scope": "key", "key_shape_ref": "shape.example.customer_key", "value_shape_ref": "shape.example.customer_change_v1", "bound": {"kind": "cardinality", "expression": "at most one snapshot chunk plus concurrent log changes inside the open snapshot window"}, "durability": "run", "ttl": {"time_domain": "explicit_signal", "duration": None, "expiry_visibility": "receipt"}, "checkpoint": {"participates": True, "consistency": "barrier_consistent"}, "migration": {"compatibility": "requires_transform", "upcaster_refs": []}, "concurrency": "partition_confined", "decision_bindings": {"decision.pipeline.snapshot_change_strategy": "watermark_windows"}},
    {"state_contract_id": "state.example.sink_transaction", "edition": 1, "state_kind": "transaction", "scope": "partition", "key_shape_ref": "shape.pipeline.partition_id", "value_shape_ref": "shape.pipeline.commit_token", "bound": {"kind": "cardinality", "expression": "one in-flight transaction per sink partition and checkpoint epoch"}, "durability": "run", "ttl": {"time_domain": "processing_time", "duration": "PT30M", "expiry_visibility": "receipt"}, "checkpoint": {"participates": True, "consistency": "transactional"}, "migration": {"compatibility": "exact", "upcaster_refs": []}, "concurrency": "single_writer", "decision_bindings": {"decision.pipeline.atomicity_scope": "table"}},
]


def node(node_id: str, node_kind: str, ops: list[str], inputs: list[str], outputs: list[str], effect: str, states: list[str]) -> dict:
    return {"node_id": node_id, "edition": 1, "node_kind": node_kind, "operation_refs": ops, "input_port_refs": inputs, "output_port_refs": outputs, "effect_class": effect, "determinism": "deterministic", "idempotency": "conditional" if effect != "pure" else "not_applicable", "state_contract_refs": states, "retry_policy_ref": "policy.example.bounded_retry" if effect != "pure" else None, "resource_requirements": {"bounded": True, "expressions": ["memory <= declared chunk plus overlap buffer", "network and state I/O <= deployment budget"]}, "decision_bindings": {}}


EXAMPLE_NODES = [
    node("node.example.snapshot", "source", ["operation.snapshot_extract.read_database_snapshot", "operation.snapshot_extract.read_source_range"], [], ["port.example.snapshot.rows"], "reads_external", ["state.example.snapshot_cursor"]),
    node("node.example.cdc", "source", ["operation.change_capture.initialize_change_capture", "operation.change_capture.normalize_change_envelope", "operation.change_capture.checkpoint_change_offset"], [], ["port.example.cdc.changes"], "reads_external", ["state.example.cdc_offset"]),
    node("node.example.handoff", "transform", ["operation.change_capture.handoff_snapshot_to_changes", "operation.change_capture.reconcile_snapshot_with_changes"], ["port.example.handoff.snapshot_in", "port.example.handoff.changes_in"], ["port.example.handoff.out"], "pure", ["state.example.overlap_buffer"]),
    node("node.example.normalize", "transform", ["operation.change_capture.deduplicate_change_delivery", "operation.change_capture.order_change_records"], ["port.example.normalize.in"], ["port.example.normalize.out"], "pure", []),
    node("node.example.sink", "materializer", ["operation.delivery_sink.stage_sink_write", "operation.delivery_sink.validate_staged_write", "operation.delivery_sink.commit_sink_write", "operation.delivery_sink.emit_delivery_receipt"], ["port.example.sink.in"], ["port.example.sink.receipt"], "writes_external", ["state.example.sink_transaction"]),
]


def edge(edge_id: str, source: str, target: str, *, channel_mode: str = "durable_log", barrier: str = "align") -> dict:
    return {"edge_id": edge_id, "edition": 1, "from_port_ref": source, "to_port_ref": target, "edge_kind": "data", "channel": {"mode": channel_mode, "capacity": {"unit": "records", "maximum": 10000}, "flow_control": "backpressure", "delivery": "at_least_once", "serialization": "schema.example.customer_change_v1", "compression": "codec.zstd.frame.explicit_offer"}, "barrier_behavior": barrier, "failure_propagation": "fail_component", "decision_bindings": {"decision.pipeline.channel_capacity": {"records": 10000}, "decision.pipeline.compression": "frame"}}


EXAMPLE_EDGES = [
    edge("edge.example.snapshot_handoff", "port.example.snapshot.rows", "port.example.handoff.snapshot_in", channel_mode="object_manifest"),
    edge("edge.example.cdc_handoff", "port.example.cdc.changes", "port.example.handoff.changes_in"),
    edge("edge.example.handoff_normalize", "port.example.handoff.out", "port.example.normalize.in"),
    edge("edge.example.normalize_sink", "port.example.normalize.out", "port.example.sink.in"),
]


EXAMPLE_DELIVERY = {
    "delivery_contract_id": "delivery.example.customer_table",
    "edition": 1,
    "observation_boundary": "published analytical table snapshot",
    "multiplicity": "exactly_once_effect",
    "ordering_scope": "per_key",
    "atomicity_scope": "table",
    "source_replay": {"required": True, "position_domain": "database LSN per source partition", "minimum_retention": "greater than maximum restore plus outage duration"},
    "execution_recovery": {"checkpoint_ref": "policy.example.barrier_checkpoint", "determinism_scope": "canonical changes affect keyed state once after restore"},
    "sink_effect": {"mechanism": "transaction", "idempotency_scope": "pipeline run plus checkpoint epoch", "reconciliation": "query table commit token after indeterminate acknowledgement"},
    "acknowledgement_boundary": "source offsets advance only after checkpoint-coordinated sink commit",
    "deduplication": {"key": "source transaction plus partition plus position plus row identity", "horizon": "source replay retention"},
    "visibility": "snapshot_commit",
    "failure_model": ["worker crash", "coordinator crash", "duplicate delivery", "network partition", "indeterminate sink acknowledgement"],
    "proof_obligations": ["source seek conformance", "checkpoint restore failure injection", "sink commit fencing", "visibility readback"],
    "decision_bindings": {"decision.pipeline.delivery_multiplicity": "exactly_once_effect", "decision.pipeline.atomicity_scope": "table"},
}


EXAMPLE_RECOVERY = {
    "recovery_contract_id": "recovery.example.customer_pipeline",
    "edition": 1,
    "failure_domains": ["record", "task", "worker", "coordinator", "source", "sink"],
    "checkpoint_policy": "policy.example.barrier_checkpoint",
    "retry_policy": "policy.example.bounded_retry",
    "replay_policy": "policy.example.replay_from_last_completed_checkpoint",
    "backfill_policy": "policy.example.closed_cut_backfill",
    "compensation_policy": "policy.example.abort_uncommitted_and_reconcile_indeterminate",
    "cancellation_policy": "policy.example.cooperative_then_fence",
    "partial_output_policy": "retain_unpublished",
    "orphan_policy": "fence_and_reclaim",
    "liveness": {"heartbeat": "PT15S", "lease": "PT60S", "stall": "three missed heartbeats then reconcile before retry"},
    "decision_bindings": {"decision.pipeline.retry_budget": {"attempts": 5, "elapsed": "PT30M"}, "decision.pipeline.cancellation": "force_after_grace"},
}


EXAMPLE_PIPELINE = {
    "definition_id": "pipeline.example.customer_cdc",
    "edition": 1,
    "status": "validated",
    "name": "Customer baseline and continuous change materialization",
    "execution_mode": "continuous_stream",
    "topology_kind": "dag",
    "parameter_schema_ref": "schema.example.customer_cdc_parameters_v1",
    "node_refs": [node["node_id"] for node in EXAMPLE_NODES],
    "edge_refs": [edge["edge_id"] for edge in EXAMPLE_EDGES],
    "entry_port_refs": ["port.example.snapshot.rows", "port.example.cdc.changes"],
    "exit_port_refs": ["port.example.sink.receipt"],
    "state_contract_refs": [state["state_contract_id"] for state in EXAMPLE_STATES],
    "delivery_contract_ref": EXAMPLE_DELIVERY["delivery_contract_id"],
    "recovery_contract_ref": EXAMPLE_RECOVERY["recovery_contract_id"],
    "trigger": {"kind": "continuous", "definition": {"bootstrap": "manual authorized baseline", "then": "resume durable change position"}},
    "policy_refs": ["policy.example.source_authority", "policy.example.quality_before_publish", "policy.example.finite_budget"],
    "decision_bindings": {"decision.pipeline.execution_mode": "continuous_stream", "decision.pipeline.snapshot_change_strategy": "watermark_windows", "decision.pipeline.compression": "frame"},
    "evidence_refs": ["src.debezium.incremental_snapshot", "src.flink.fault_tolerance", "src.openlineage.spec"],
    "llm_dependency": "none",
}


EXAMPLE_CUT = {
    "data_cut_id": "cut.example.customer_bootstrap_2026_08_25",
    "edition": 1,
    "status": "closed",
    "source_selections": [{"source_ref": "source.example.customer_db", "position_domain": "postgres_lsn", "start": None, "end": "0/16B6C50", "snapshot_ref": "snapshot.example.customer_at_0_16b6c50", "partitions": ["public.customer"]}],
    "event_time_interval": None,
    "valid_time_interval": None,
    "recording_time_interval": {"start": "2026-08-25T00:00:00Z", "end": "2026-08-25T01:00:00Z", "bounds": "closed_open"},
    "closure": {"law": "snapshot is reconciled through the recorded end LSN", "witness": "receipt.example.handoff_complete"},
    "created_at": "2026-08-25T01:00:01Z",
    "evidence_refs": ["receipt.example.source_snapshot", "receipt.example.change_position"],
}


EXAMPLE_PLAN = {
    "plan_id": "plan.example.customer_cdc.generic_stream_v1",
    "edition": 1,
    "definition_ref": EXAMPLE_PIPELINE["definition_id"],
    "definition_edition": 1,
    "logical_graph_digest": "sha256:example-logical-graph-digest-not-a-real-artifact",
    "physical_stages": [
        {"stage_id": "stage.example.ingress", "node_refs": ["node.example.snapshot", "node.example.cdc"], "operator_offer_refs": ["offer.example.source_connector"], "parallelism": 2, "exchange_refs": ["edge.example.snapshot_handoff", "edge.example.cdc_handoff"]},
        {"stage_id": "stage.example.compute", "node_refs": ["node.example.handoff", "node.example.normalize"], "operator_offer_refs": ["offer.example.stateful_stream_runtime"], "parallelism": 4, "exchange_refs": ["edge.example.handoff_normalize"]},
        {"stage_id": "stage.example.commit", "node_refs": ["node.example.sink"], "operator_offer_refs": ["offer.example.transactional_table_sink"], "parallelism": 4, "exchange_refs": ["edge.example.normalize_sink"]},
    ],
    "bindings": ["binding.example.source", "binding.example.runtime", "binding.example.sink"],
    "decision_trace_refs": ["trace.example.plan_decisions"],
    "proof_results": [{"requirement_ref": req["requirement_id"], "result": "proven", "evidence_refs": [f"evidence.example.{req['requirement_id'].split('.')[-1]}"]} for req in REQUIREMENTS[:13]],
    "resource_estimate": {"state_bytes_upper": 10737418240, "network_bytes_per_second_upper": 104857600, "parallelism": 4},
    "artifact_refs": ["artifact.example.pipeline_bundle"],
    "status": "validated",
}


EXAMPLE_DEPLOYMENT = {
    "deployment_id": "deployment.example.customer_cdc.prod",
    "edition": 1,
    "plan_ref": EXAMPLE_PLAN["plan_id"],
    "plan_edition": 1,
    "target_bindings": [{"stage_ref": stage["stage_id"], "target_profile_ref": "target.example.stream_cluster", "provider_offer_ref": stage["operator_offer_refs"][0]} for stage in EXAMPLE_PLAN["physical_stages"]],
    "artifact_digests": {"artifact.example.pipeline_bundle": "sha256:example-artifact-digest-not-a-real-artifact"},
    "secret_refs": ["secret-ref.example.customer_source", "secret-ref.example.table_sink"],
    "rollout": "parallel_compare",
    "operating_policies": ["policy.example.checkpoint", "policy.example.retry", "policy.example.alerting"],
    "qualification_evidence_refs": ["evidence.example.target_qualification", "evidence.example.failure_injection"],
    "status": "qualified",
}


EXAMPLE_ATTEMPTS = [
    {"attempt_id": f"attempt.example.customer.{index}", "edition": 1, "run_ref": "run.example.customer.bootstrap", "stage_ref": stage["stage_id"], "task_ref": stage["node_refs"][0], "attempt_number": 1, "worker_lease": {"lease_id": f"lease.example.{index}", "worker_ref": f"worker.example.{index}", "fence_token": f"fence-example-{index}", "expires_at": "2026-08-25T01:30:00Z"}, "input_bindings": [EXAMPLE_CUT["data_cut_id"]], "state_restore_ref": None, "started_at": "2026-08-25T01:00:10Z", "heartbeat_at": "2026-08-25T01:10:00Z", "ended_at": "2026-08-25T01:12:00Z", "state": "succeeded", "effect_receipt_refs": [f"receipt.example.attempt.{index}"], "outcome_ref": "pipeline.outcome.success"}
    for index, stage in enumerate(EXAMPLE_PLAN["physical_stages"], start=1)
]


EXAMPLE_MATERIALIZATION = {
    "materialization_id": "materialization.example.customer_table.snapshot_42",
    "edition": 1,
    "run_ref": "run.example.customer.bootstrap",
    "producer_node_ref": "node.example.sink",
    "output_port_ref": "port.example.sink.receipt",
    "data_cut_ref": EXAMPLE_CUT["data_cut_id"],
    "object_ref": "table.example.analytics.customer",
    "version_identity": "snapshot:42",
    "content_identity": "sha256:example-content-digest-not-a-real-artifact",
    "commit_receipt_ref": "receipt.example.table_commit_42",
    "quality_receipt_refs": ["receipt.example.customer_quality_42"],
    "lineage_receipt_ref": "receipt.example.customer_lineage_42",
    "visibility": "published",
    "recorded_at": "2026-08-25T01:12:01Z",
    "status": "published",
}


EXAMPLE_RUN = {
    "run_id": "run.example.customer.bootstrap",
    "edition": 1,
    "deployment_ref": EXAMPLE_DEPLOYMENT["deployment_id"],
    "deployment_edition": 1,
    "plan_ref": EXAMPLE_PLAN["plan_id"],
    "data_cut_ref": EXAMPLE_CUT["data_cut_id"],
    "trigger_observation_ref": "trigger-observation.example.manual_bootstrap",
    "parameters_digest": "sha256:example-parameter-digest-not-a-real-artifact",
    "logical_time": "2026-08-25T00:00:00Z",
    "requested_at": "2026-08-25T01:00:02Z",
    "started_at": "2026-08-25T01:00:10Z",
    "ended_at": "2026-08-25T01:12:01Z",
    "state": "succeeded",
    "task_attempt_refs": [attempt["attempt_id"] for attempt in EXAMPLE_ATTEMPTS],
    "materialization_refs": [EXAMPLE_MATERIALIZATION["materialization_id"]],
    "outcome_ref": "pipeline.outcome.success",
    "receipt_refs": ["receipt.example.run_complete", "receipt.example.customer_lineage_42"],
}


EXECUTION_MODE_MATRIX = [
    {"mode_id": "pipeline-mode.bounded_batch", "input_extent": "closed before run", "progress": "end of input", "state": "bounded by cut", "recovery": "task/stage retry or checkpoint", "required_decisions": ["data_cut_closure", "backfill_reprocessing", "delivery_multiplicity"]},
    {"mode_id": "pipeline-mode.microbatch", "input_extent": "sequence of closed small cuts", "progress": "batch/cut completion", "state": "cross-batch state optional", "recovery": "batch replay plus idempotent/transactional commit", "required_decisions": ["batching", "checkpoint_cadence", "sink_idempotency"]},
    {"mode_id": "pipeline-mode.continuous_stream", "input_extent": "unbounded", "progress": "watermark/frontier", "state": "must declare cleanup bound", "recovery": "checkpoint plus source replay", "required_decisions": ["watermark_strategy", "late_data", "state_bound", "checkpoint_mode"]},
    {"mode_id": "pipeline-mode.cdc", "input_extent": "transaction/change log", "progress": "source positions and transactions", "state": "offsets, schema history and optional dedup", "recovery": "seek durable position; handle log truncation", "required_decisions": ["ingestion_mode", "cursor_commit_boundary", "port_update_model"]},
    {"mode_id": "pipeline-mode.incremental", "input_extent": "signed changes or changed cuts", "progress": "change frontier or commit version", "state": "arrangements/materialized intermediates", "recovery": "restore or recompute from authoritative changes", "required_decisions": ["state_bound", "state_ttl", "delivery_multiplicity"]},
    {"mode_id": "pipeline-mode.federated", "input_extent": "remote snapshot/query", "progress": "remote result/cursor", "state": "local residual optional", "recovery": "repeat under pinned remote consistency or refuse", "required_decisions": ["read_consistency", "target_placement", "schema_compatibility"]},
    {"mode_id": "pipeline-mode.reverse_delivery", "input_extent": "analytical materialization/audience cut", "progress": "destination acknowledgement/receipt", "state": "suppression, idempotency and delivery status", "recovery": "retry, reconcile or compensate effects", "required_decisions": ["sink_idempotency", "atomicity_scope", "compensation"]},
]


TOPOLOGY_MATRIX = [
    {"topology_id": "pipeline-topology.dag", "law": "acyclic after subgraph expansion", "progress_requirement": "topological readiness", "refusal": "cycle detected"},
    {"topology_id": "pipeline-topology.feedback_fixed_point", "law": "feedback has epoch/delay and monotone or explicitly convergent fixed-point test", "progress_requirement": "iteration frontier", "refusal": "termination/convergence not proven"},
    {"topology_id": "pipeline-topology.productive_cycle", "law": "cycle intentionally continues but each epoch advances progress and state remains bounded", "progress_requirement": "productive-continuation witness", "refusal": "livelock or unbounded accumulation possible"},
    {"topology_id": "pipeline-topology.dynamic_map", "law": "expansion source and maximum cardinality are declared", "progress_requirement": "expansion closure", "refusal": "unbounded dynamic expansion"},
    {"topology_id": "pipeline-topology.nested_subflow", "law": "input/output ports and cancellation/failure propagation are total", "progress_requirement": "child-run outcome", "refusal": "implicit child effects or unresolved outputs"},
]


def lifecycle(lifecycle_id: str, owner: str, states: list[str], transitions: list[tuple[str, str, str]], terminal: list[str]) -> dict:
    return {
        "lifecycle_id": f"lifecycle.pipeline.{lifecycle_id}",
        "edition": 1,
        "owner_context": owner,
        "states": states,
        "initial_state": states[0],
        "terminal_states": terminal,
        "transitions": [{"from": source, "to": target, "cause": cause} for source, target, cause in transitions],
        "invalid_transition_outcome": "pipeline.outcome.invalid_state_transition",
        "totality_law": "For each command and current state, exactly one legal transition or typed refusal must result.",
    }


LIFECYCLES = [
    lifecycle("definition", "ppl.pipeline_definition", ["draft", "validated", "published", "superseded", "retired"], [("draft", "validated", "validation passed"), ("validated", "published", "publication authorized"), ("published", "superseded", "new compatible or breaking edition published"), ("published", "retired", "retirement authorized"), ("superseded", "retired", "retention obligations satisfied")], ["retired"]),
    lifecycle("compiled_plan", "ppl.execution_plan", ["candidate", "validated", "published", "invalidated"], [("candidate", "validated", "all blocking requirements proven"), ("validated", "published", "plan identity fixed"), ("candidate", "invalidated", "binding or proof failed"), ("validated", "invalidated", "dependency evidence changed"), ("published", "invalidated", "pinned offer or policy invalidated")], ["invalidated"]),
    lifecycle("deployment", "ppl.deployment_binding", ["draft", "qualified", "active", "draining", "retired", "failed"], [("draft", "qualified", "targets and artifacts qualified"), ("qualified", "active", "activation authorized"), ("active", "draining", "replacement or retirement requested"), ("draining", "retired", "in-flight work disposed"), ("draft", "failed", "deployment effect failed"), ("qualified", "failed", "activation failed")], ["retired", "failed"]),
    lifecycle("run", "ppl.pipeline_run", ["requested", "admitted", "running", "paused", "cancelling", "succeeded", "failed", "cancelled", "indeterminate"], [("requested", "admitted", "admission passed"), ("admitted", "running", "execution started"), ("running", "paused", "pause acknowledged"), ("paused", "running", "resume acknowledged"), ("running", "cancelling", "cancellation requested"), ("paused", "cancelling", "cancellation requested"), ("running", "succeeded", "all required outcomes and commits accepted"), ("running", "failed", "terminal failure aggregated"), ("cancelling", "cancelled", "disposition completed"), ("cancelling", "indeterminate", "effect disposition unresolved")], ["succeeded", "failed", "cancelled", "indeterminate"]),
    lifecycle("task_attempt", "ppl.task_attempt", ["leased", "starting", "running", "checkpointing", "committing", "succeeded", "failed", "cancelled", "revoked", "indeterminate"], [("leased", "starting", "worker accepted lease"), ("starting", "running", "task initialized"), ("running", "checkpointing", "barrier received"), ("checkpointing", "running", "checkpoint acknowledged"), ("running", "committing", "effects prepared"), ("committing", "succeeded", "commit accepted"), ("running", "failed", "failure classified terminal"), ("running", "cancelled", "cooperative cancellation completed"), ("leased", "revoked", "lease expired"), ("running", "revoked", "lease fenced"), ("committing", "indeterminate", "commit outcome unknown")], ["succeeded", "failed", "cancelled", "revoked", "indeterminate"]),
    lifecycle("data_cut", "ppl.data_cut", ["open", "closed", "invalidated"], [("open", "closed", "closure witness accepted"), ("open", "invalidated", "source boundary lost"), ("closed", "invalidated", "authority or identity revoked")], ["invalidated"]),
    lifecycle("checkpoint", "ppl.checkpoint_coordination", ["requested", "barriers_injected", "collecting", "persisting", "completed", "aborted", "expired", "corrupt"], [("requested", "barriers_injected", "coordinator triggered"), ("barriers_injected", "collecting", "first acknowledgement received"), ("collecting", "persisting", "all required state captured"), ("persisting", "completed", "durable completion accepted"), ("requested", "aborted", "checkpoint cancelled"), ("collecting", "aborted", "timeout or participant failure"), ("persisting", "aborted", "persistence failed"), ("completed", "expired", "retention proof authorized deletion"), ("completed", "corrupt", "integrity verification failed")], ["aborted", "expired", "corrupt"]),
    lifecycle("sink_transaction", "ppl.sink_commit", ["open", "staged", "validated", "prepared", "committed", "aborted", "indeterminate", "reconciled"], [("open", "staged", "writes staged"), ("staged", "validated", "staged checks passed"), ("validated", "prepared", "sink prepared commit"), ("prepared", "committed", "commit acknowledged and fenced"), ("open", "aborted", "abort accepted"), ("staged", "aborted", "abort accepted"), ("prepared", "indeterminate", "acknowledgement lost"), ("indeterminate", "reconciled", "sink state observed")], ["committed", "aborted", "reconciled"]),
    lifecycle("materialization", "ppl.materialization", ["registered", "committed_unpublished", "qualified", "published", "quarantined", "superseded", "recalled"], [("registered", "committed_unpublished", "commit receipt accepted"), ("committed_unpublished", "qualified", "required gates passed"), ("committed_unpublished", "quarantined", "blocking gate failed"), ("qualified", "published", "publication authorized"), ("published", "superseded", "new materialization published"), ("published", "recalled", "recall authority acted"), ("quarantined", "qualified", "repair and requalification passed")], ["superseded", "recalled"]),
    lifecycle("backfill_campaign", "ppl.backfill", ["draft", "planned", "approved", "running", "paused", "reconciling", "completed", "failed", "cancelled"], [("draft", "planned", "cuts enumerated"), ("planned", "approved", "resources and publication disposition authorized"), ("approved", "running", "first cut admitted"), ("running", "paused", "pause requested"), ("paused", "running", "resume requested"), ("running", "reconciling", "all cuts terminal"), ("reconciling", "completed", "coverage and outputs accepted"), ("running", "failed", "campaign failure threshold crossed"), ("running", "cancelled", "cancellation disposition completed")], ["completed", "failed", "cancelled"]),
    lifecycle("retry", "ppl.retry", ["eligible", "scheduled", "waiting", "attempting", "satisfied", "exhausted", "cancelled"], [("eligible", "scheduled", "policy selected delay"), ("scheduled", "waiting", "timer registered"), ("waiting", "attempting", "delay elapsed and admission passed"), ("attempting", "satisfied", "attempt succeeded"), ("attempting", "eligible", "retryable failure with budget remains"), ("eligible", "exhausted", "budget consumed"), ("scheduled", "cancelled", "parent cancelled"), ("waiting", "cancelled", "parent cancelled")], ["satisfied", "exhausted", "cancelled"]),
    lifecycle("cancellation", "ppl.cancellation", ["requested", "propagating", "waiting_grace", "forcing", "cleaning", "completed", "failed", "indeterminate"], [("requested", "propagating", "scope resolved"), ("propagating", "waiting_grace", "cancel intents delivered"), ("waiting_grace", "cleaning", "work stopped cooperatively"), ("waiting_grace", "forcing", "grace expired"), ("forcing", "cleaning", "work fenced or terminated"), ("cleaning", "completed", "all dispositions accepted"), ("cleaning", "failed", "required cleanup failed"), ("forcing", "indeterminate", "effect state unresolved")], ["completed", "failed", "indeterminate"]),
    lifecycle("compensation", "ppl.compensation", ["registered", "requested", "eligible", "executing", "compensated", "failed", "residual_recorded"], [("registered", "requested", "recovery selected compensation"), ("requested", "eligible", "preconditions and authority passed"), ("eligible", "executing", "counteraction admitted"), ("executing", "compensated", "acceptance condition observed"), ("executing", "failed", "counteraction failed"), ("failed", "residual_recorded", "unreversed effect documented")], ["compensated", "residual_recorded"]),
    lifecycle("snapshot_change_handoff", "ppl.snapshot_change_handoff", ["initialized", "baseline_running", "window_open", "reconciling", "caught_up", "continuous", "completed", "failed"], [("initialized", "baseline_running", "snapshot cursor fixed"), ("baseline_running", "window_open", "chunk window opened"), ("window_open", "reconciling", "chunk read and close marker observed"), ("reconciling", "baseline_running", "more chunks remain"), ("reconciling", "caught_up", "last chunk reconciled through high watermark"), ("caught_up", "continuous", "change stream owns progress"), ("continuous", "completed", "bounded capture intentionally closed"), ("baseline_running", "failed", "retention, key or read failure"), ("reconciling", "failed", "overlap ambiguous")], ["completed", "failed"]),
    lifecycle("maintenance", "ppl.maintenance", ["proposed", "qualified", "scheduled", "running", "completed", "failed", "cancelled"], [("proposed", "qualified", "retention and reference proof passed"), ("qualified", "scheduled", "maintenance window assigned"), ("scheduled", "running", "conflict and budget checks passed"), ("running", "completed", "effects and receipts accepted"), ("running", "failed", "maintenance effect failed"), ("scheduled", "cancelled", "window revoked")], ["completed", "failed", "cancelled"]),
]


ARTIFACT_KINDS = [
    {"artifact_kind_id": "pipeline-artifact.definition", "identity_scope": "reusable authored intent edition", "created_by": "pipeline authoring and publication", "pins": ["logical contracts", "parameters", "graph references"], "may_reference": [], "cannot_substitute_for": ["compiled_plan", "deployment", "run", "task_attempt", "data_cut", "materialization"], "lifecycle_ref": "lifecycle.pipeline.definition"},
    {"artifact_kind_id": "pipeline-artifact.compiled_plan", "identity_scope": "one lowering of one definition edition under decisions and offers", "created_by": "compiler physical-planning pass", "pins": ["physical stages", "bindings", "proof results", "artifacts"], "may_reference": ["definition"], "cannot_substitute_for": ["definition", "deployment", "run", "task_attempt", "data_cut", "materialization"], "lifecycle_ref": "lifecycle.pipeline.compiled_plan"},
    {"artifact_kind_id": "pipeline-artifact.deployment", "identity_scope": "one plan edition bound to qualified targets and artifacts", "created_by": "deployment binding", "pins": ["plan", "target offers", "artifact digests", "secret references", "operating policies"], "may_reference": ["compiled_plan"], "cannot_substitute_for": ["definition", "compiled_plan", "run", "task_attempt", "data_cut", "materialization"], "lifecycle_ref": "lifecycle.pipeline.deployment"},
    {"artifact_kind_id": "pipeline-artifact.run", "identity_scope": "one admitted execution of one deployment over one data cut", "created_by": "orchestration admission", "pins": ["deployment", "plan", "data cut", "parameters", "logical time"], "may_reference": ["deployment", "compiled_plan", "data_cut"], "cannot_substitute_for": ["definition", "compiled_plan", "deployment", "task_attempt", "data_cut", "materialization"], "lifecycle_ref": "lifecycle.pipeline.run"},
    {"artifact_kind_id": "pipeline-artifact.task_attempt", "identity_scope": "one numbered attempt of one task in one run under one worker lease", "created_by": "task leasing", "pins": ["run", "physical task", "attempt number", "fence token"], "may_reference": ["run", "compiled_plan"], "cannot_substitute_for": ["logical node", "definition", "run", "data_cut", "materialization"], "lifecycle_ref": "lifecycle.pipeline.task_attempt"},
    {"artifact_kind_id": "pipeline-artifact.data_cut", "identity_scope": "one exact source selection and closure witness", "created_by": "cut planning and closure", "pins": ["source positions", "snapshots", "partitions", "time intervals"], "may_reference": [], "cannot_substitute_for": ["schedule interval", "run", "materialization"], "lifecycle_ref": "lifecycle.pipeline.data_cut"},
    {"artifact_kind_id": "pipeline-artifact.materialization", "identity_scope": "one named output version produced from one run and cut", "created_by": "sink commit and publication", "pins": ["object", "version/content identity", "commit", "quality", "lineage"], "may_reference": ["run", "data_cut", "task_attempt"], "cannot_substitute_for": ["dataset definition", "run", "commit receipt", "quality proof"], "lifecycle_ref": "lifecycle.pipeline.materialization"},
    {"artifact_kind_id": "pipeline-artifact.checkpoint", "identity_scope": "one completed distributed recovery cut", "created_by": "checkpoint coordination", "pins": ["operator state handles", "channel state", "source positions", "plan/operator identities"], "may_reference": ["deployment", "compiled_plan", "run"], "cannot_substitute_for": ["savepoint", "data_cut", "materialization", "commit"], "lifecycle_ref": "lifecycle.pipeline.checkpoint"},
]


def main() -> None:
    for name, schema in SCHEMAS.items():
        write_json(ROOT / "schemas" / name, schema)
    write_jsonl(ROOT / "sources.jsonl", SOURCES)
    write_jsonl(ROOT / "context-candidates.jsonl", CONTEXTS)
    write_jsonl(ROOT / "decision-catalog.jsonl", DECISIONS)
    write_jsonl(ROOT / "failure-refusal-catalog.jsonl", FAILURES)
    write_jsonl(ROOT / "innovations.jsonl", INNOVATIONS)
    write_jsonl(ROOT / "library-boundary-candidates.jsonl", LIBRARIES)
    write_jsonl(ROOT / "compiler-requirements.jsonl", REQUIREMENTS)
    write_jsonl(ROOT / "capability-offer-templates.jsonl", OFFER_TEMPLATES)
    write_jsonl(ROOT / "operation-mappings.jsonl", OPERATION_MAPPINGS)
    write_jsonl(ROOT / "gaps.jsonl", GAPS)
    write_json(ROOT / "execution-mode-matrix.json", EXECUTION_MODE_MATRIX)
    write_json(ROOT / "topology-matrix.json", TOPOLOGY_MATRIX)
    write_jsonl(ROOT / "lifecycles.jsonl", LIFECYCLES)
    write_jsonl(ROOT / "artifact-kinds.jsonl", ARTIFACT_KINDS)
    write_json(ROOT / "examples" / "cdc-snapshot-handoff.pipeline.json", EXAMPLE_PIPELINE)
    write_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.nodes.jsonl", EXAMPLE_NODES)
    write_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.ports.jsonl", EXAMPLE_PORTS)
    write_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.edges.jsonl", EXAMPLE_EDGES)
    write_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.states.jsonl", EXAMPLE_STATES)
    write_json(ROOT / "examples" / "cdc-snapshot-handoff.delivery.json", EXAMPLE_DELIVERY)
    write_json(ROOT / "examples" / "cdc-snapshot-handoff.recovery.json", EXAMPLE_RECOVERY)
    write_json(ROOT / "examples" / "cdc-snapshot-handoff.data-cut.json", EXAMPLE_CUT)
    write_json(ROOT / "examples" / "cdc-snapshot-handoff.compiled-plan.json", EXAMPLE_PLAN)
    write_json(ROOT / "examples" / "cdc-snapshot-handoff.deployment.json", EXAMPLE_DEPLOYMENT)
    write_jsonl(ROOT / "examples" / "cdc-snapshot-handoff.attempts.jsonl", EXAMPLE_ATTEMPTS)
    write_json(ROOT / "examples" / "cdc-snapshot-handoff.materialization.json", EXAMPLE_MATERIALIZATION)
    write_json(ROOT / "examples" / "cdc-snapshot-handoff.run.json", EXAMPLE_RUN)
    manifest = {
        "corpus_id": "san.domain-atlas.pipeline-dataflow",
        "edition": 1,
        "status": "active_research_candidate",
        "completion_claim": False,
        "generated_by": "build_corpus.py",
        "counts": {
            "primary_sources": len(SOURCES),
            "bounded_context_candidates": len(CONTEXTS),
            "decision_points": len(DECISIONS),
            "failures_and_refusals": len(FAILURES),
            "innovations_2021_2026": len(INNOVATIONS),
            "library_boundaries": len(LIBRARIES),
            "compiler_requirements": len(REQUIREMENTS),
            "offer_templates": len(OFFER_TEMPLATES),
            "central_operation_mappings": len(OPERATION_MAPPINGS),
            "known_gaps": len(GAPS),
            "schemas": len(SCHEMAS),
            "lifecycles": len(LIFECYCLES),
            "artifact_kinds": len(ARTIFACT_KINDS),
        },
        "coverage": ["ingestion", "transport", "transformation", "orchestration", "bounded batch", "microbatch", "continuous streaming", "CDC", "incremental computation", "federation", "reverse delivery", "DAG", "cyclic/iterative dataflow", "ports/channels/partitions", "barriers/watermarks/windows/triggers", "state/checkpoints", "delivery/retry/replay/backfill", "compensation/cancellation", "scheduling/maintenance/deployment", "lineage/receipts"],
        "exclusions": ["LLM, generative or agentic semantics", "vendor product selection", "business-domain transformation meaning", "storage engine implementation internals"],
    }
    write_json(ROOT / "manifest.json", manifest)
    print(json.dumps(manifest["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
