#!/usr/bin/env python3
"""Generate a broad hypothesis queue for typed data/analytics operations."""

from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent


FAMILIES = [
    ("discovery_metadata", "validator", "dat.source-discovery", [
        "enumerate source namespaces", "enumerate source objects", "describe source object",
        "discover endpoint capabilities", "discover protocol version", "discover schema",
        "discover partition layout", "discover change capability", "discover read limits",
        "discover write limits", "discover retention boundary", "discover consistency level",
        "discover ordering guarantee", "discover finality guarantee", "discover cost model",
        "discover security requirements", "discover data owner", "sample source metadata",
        "fingerprint source metadata", "diff source metadata", "validate discovery freshness"
    ]),
    ("connector_session", "effect_intent", "dat.connector-session", [
        "resolve connector binding", "negotiate protocol", "authenticate connector session",
        "authorize connector operation", "open connector session", "renew connector session",
        "rotate connector credential", "test connector health", "test source reachability",
        "reserve source quota", "throttle connector request", "close connector session",
        "resume connector session", "fail over connector endpoint", "select source replica",
        "resolve regional endpoint", "establish secure channel", "verify peer identity",
        "negotiate compression", "negotiate serialization"
    ]),
    ("snapshot_extract", "effectful_runtime", "dat.source-read", [
        "read source object", "scan source collection", "query source snapshot", "export source snapshot",
        "read source range", "read source partition", "read source page", "advance page cursor",
        "parallelize source scan", "sample source records", "read object metadata", "read object content",
        "list changed objects", "read database snapshot", "read consistent multi-object snapshot",
        "read point-in-time state", "read historical version", "read audit log", "read transaction log",
        "read external file", "read API resource", "read bulk export", "read federated source",
        "push down source predicate", "push down source projection", "push down source aggregation",
        "estimate extraction size", "preflight extraction", "cancel source read", "resume source read"
    ]),
    ("change_capture", "stateful_transform", "dat.change-capture", [
        "initialize change capture", "capture insert change", "capture update change", "capture delete change",
        "capture schema change", "read change log", "subscribe to change stream", "poll for changes",
        "decode change record", "normalize change envelope", "identify transaction boundary",
        "order change records", "deduplicate change delivery", "detect change gap", "repair change gap",
        "checkpoint change offset", "resume change offset", "seek change offset", "acknowledge change delivery",
        "retain change offset", "expire change offset", "bootstrap snapshot plus changes",
        "handoff snapshot to changes", "reconcile snapshot with changes", "capture tombstone",
        "propagate source correction", "detect source rewind", "handle log truncation",
        "validate change completeness", "measure change lag"
    ]),
    ("delivery_sink", "effectful_runtime", "dat.sink-delivery", [
        "create sink object", "append sink records", "upsert sink records", "merge sink records",
        "replace sink object", "delete sink records", "truncate sink object", "publish sink message",
        "send sink request", "write bulk load", "write object blob", "write table partition",
        "stage sink write", "validate staged write", "commit sink write", "abort sink write",
        "retry sink write", "deduplicate sink write", "acknowledge sink delivery", "verify sink visibility",
        "verify sink durability", "reconcile sink result", "compensate sink write", "quarantine failed delivery",
        "rate-limit sink delivery", "batch sink delivery", "flush sink buffer", "close sink writer",
        "emit delivery receipt", "redact sink payload"
    ]),
    ("framing_serialization", "pure_transform", "dat.encoding", [
        "detect media type", "detect character encoding", "decode bytes", "encode bytes",
        "parse delimited record", "serialize delimited record", "parse fixed-width record",
        "serialize fixed-width record", "parse JSON", "serialize JSON", "parse XML", "serialize XML",
        "parse Avro", "serialize Avro", "parse Protocol Buffers", "serialize Protocol Buffers",
        "parse Parquet page", "encode Parquet page", "parse ORC stripe", "encode ORC stripe",
        "frame message", "deframe message", "split record stream", "combine record fragments",
        "detect record boundary", "validate checksum frame", "normalize newline", "normalize Unicode",
        "transcode character set", "preserve unknown fields", "round-trip serialization"
    ]),
    ("compression_integrity", "pure_transform", "dat.encoding-integrity", [
        "compress payload", "decompress payload", "select compression codec", "detect compressed payload",
        "calculate digest", "verify digest", "calculate checksum", "verify checksum", "calculate content identity",
        "verify content identity", "sign payload", "verify payload signature", "encrypt payload",
        "decrypt payload", "wrap data key", "unwrap data key", "rotate envelope key",
        "chunk large payload", "reassemble payload chunks", "detect payload corruption",
        "repair erasure-coded payload", "verify canonical bytes", "attest payload provenance"
    ]),
    ("schema_type", "validator", "dat.schema-type", [
        "infer structural schema", "parse declared schema", "validate structural schema",
        "resolve schema reference", "register schema", "lookup schema edition", "compare schemas",
        "classify schema change", "check backward compatibility", "check forward compatibility",
        "check full compatibility", "project schema", "merge schemas", "intersect schemas",
        "widen physical type", "narrow physical type", "cast value", "safe cast value",
        "parse semantic value", "format semantic value", "validate semantic qualifier",
        "resolve union variant", "validate required field", "validate cardinality",
        "validate logical type", "preserve unknown schema field", "attach schema identity",
        "migrate schema edition", "generate schema fingerprint", "verify schema fingerprint"
    ]),
    ("quality_validation", "validator", "dat.quality", [
        "validate completeness", "validate validity", "validate uniqueness", "validate referential integrity",
        "validate cross-field consistency", "validate cross-record consistency", "validate timeliness",
        "validate freshness", "validate volume expectation", "validate distribution expectation",
        "validate range constraint", "validate enumeration constraint", "validate pattern constraint",
        "validate business rule", "validate data contract", "profile data quality", "score quality evidence",
        "localize quality violation", "explain quality failure", "quarantine invalid record",
        "accept record with warning", "reject invalid record", "repair validatable record",
        "compare quality baselines", "detect quality regression", "sample quality evidence",
        "aggregate quality results", "publish quality receipt", "waive quality violation",
        "expire quality waiver", "reconcile quality observation"
    ]),
    ("canonical_normalize", "pure_transform", "dat.canonical", [
        "canonicalize value", "canonicalize record", "canonicalize collection", "normalize whitespace",
        "normalize case", "normalize punctuation", "normalize identifier", "normalize address",
        "normalize telephone number", "normalize email address", "normalize unit", "convert unit",
        "normalize currency", "convert currency", "normalize timezone", "convert timestamp zone",
        "normalize locale", "normalize country code", "normalize language code", "normalize taxonomy code",
        "normalize missing value", "standardize category", "map reference value", "map code system",
        "apply controlled vocabulary", "sort canonically", "canonicalize floating-point value",
        "quantize numeric value", "round numeric value", "preserve normalization provenance"
    ]),
    ("relational_algebra", "pure_transform", "dat.relational-algebra", [
        "select rows", "project columns", "rename field", "derive field", "drop field", "reorder fields",
        "inner join", "left outer join", "right outer join", "full outer join", "semi join", "anti join",
        "cross join", "natural join", "theta join", "equi join", "as-of join", "interval join",
        "range join", "spatial join", "fuzzy join", "recursive join", "union all", "union distinct",
        "intersect collections", "subtract collections", "distinct records", "sort records", "limit records",
        "offset records", "top-k records", "rank records", "group records", "partition records",
        "unnest relation", "nest relation", "relational divide", "evaluate relational expression"
    ]),
    ("nested_shape", "pure_transform", "dat.shape", [
        "flatten nested record", "unflatten record", "explode array", "collect array", "zip arrays",
        "unzip arrays", "pivot relation", "unpivot relation", "transpose matrix", "reshape tensor",
        "stack arrays", "concatenate arrays", "split array", "slice array", "index array",
        "broadcast array", "sparsify array", "densify array", "encode sparse matrix",
        "decode sparse matrix", "pack struct", "unpack struct", "map nested field",
        "filter nested collection", "reduce nested collection", "preserve nested ordering",
        "validate rectangular shape", "align labeled axes", "rechunk multidimensional array"
    ]),
    ("identity_entity", "stateful_transform", "dat.identity-resolution", [
        "extract identity key", "validate identity key", "generate surrogate identity",
        "resolve natural identity", "resolve composite identity", "link records", "unlink records",
        "generate match candidates", "score record match", "classify record match", "merge entity records",
        "split entity record", "survive attribute value", "select golden record", "maintain source crosswalk",
        "resolve household identity", "resolve organization hierarchy", "resolve connected-party group",
        "resolve asset hierarchy", "detect duplicate entity", "detect identity collision",
        "record identity uncertainty", "approve entity merge", "reject entity merge", "reverse entity merge",
        "propagate identity correction", "version entity identity", "trace identity lineage",
        "measure linkage quality", "reconcile identity graph"
    ]),
    ("reconciliation", "reducer", "dat.reconciliation", [
        "compare source and target", "match reconciliation items", "calculate control total",
        "compare control totals", "reconcile balances", "reconcile counts", "reconcile quantities",
        "reconcile monetary amounts", "reconcile temporal state", "reconcile event sequences",
        "reconcile inventory movement", "reconcile transaction ledger", "identify unmatched item",
        "classify reconciliation break", "age reconciliation break", "allocate partial match",
        "net reconciliation items", "tolerate rounding difference", "apply reconciliation tolerance",
        "explain reconciliation difference", "assign break owner", "resolve reconciliation break",
        "waive reconciliation break", "reopen reconciliation break", "carry forward unresolved break",
        "attest reconciliation result", "compare reconciliation runs", "detect reconciliation regression"
    ]),
    ("temporal", "stateful_transform", "dat.temporal", [
        "assign event time", "assign processing time", "assign ingestion time", "assign valid time",
        "assign recording time", "construct valid-time interval", "construct recording-time interval",
        "close temporal interval", "coalesce temporal intervals", "split temporal interval",
        "normalize interval boundary", "compare instants", "compare intervals", "calculate duration",
        "shift time", "truncate time", "bucket time", "align calendar period", "apply business calendar",
        "apply timezone rule", "resolve daylight-saving ambiguity", "temporal as-of lookup",
        "temporal as-of join", "bitemporal lookup", "bitemporal correction", "detect temporal overlap",
        "detect temporal gap", "fill temporal gap", "interpolate temporal value", "resample time series",
        "align time series", "lag value", "lead value", "calculate rolling window",
        "calculate expanding window", "calculate period-over-period change", "expire temporal fact"
    ]),
    ("stream_window", "stateful_transform", "dat.stream", [
        "assign watermark", "advance watermark", "detect idle partition", "reorder event stream",
        "buffer out-of-order event", "classify late event", "drop late event", "side-output late event",
        "retract prior result", "upsert changed result", "emit changelog", "open tumbling window",
        "open sliding window", "open session window", "open global window", "trigger window early",
        "trigger window on time", "trigger window late", "accumulate window state", "evict window state",
        "close window", "merge session windows", "stream deduplicate", "stream join",
        "stream temporal join", "stream aggregate", "stream pattern match", "detect complex event",
        "checkpoint stream state", "restore stream state", "rescale stream state", "compact stream state",
        "apply backpressure", "measure event-time lag", "measure processing lag", "emit stream progress"
    ]),
    ("aggregation_measure", "reducer", "dat.measure", [
        "count observations", "count distinct values", "approximate distinct count", "sum values",
        "sum quantities", "average values", "weighted average", "minimum value", "maximum value",
        "product of values", "calculate variance", "calculate standard deviation", "calculate covariance",
        "calculate correlation", "calculate percentile", "calculate quantile", "calculate median",
        "calculate mode", "calculate ratio", "calculate rate", "calculate proportion", "calculate index",
        "calculate geometric mean", "calculate harmonic mean", "aggregate additive measure",
        "aggregate semi-additive measure", "reject non-additive aggregation", "roll up hierarchy",
        "drill across measures", "allocate measure", "restate measure", "reconcile metric",
        "evaluate formula", "bind formula input", "typecheck formula", "explain formula evaluation",
        "emit metric observation"
    ]),
    ("statistical_kernel", "pure_transform", "dat.statistical-kernel", [
        "calculate frequency table", "calculate contingency table", "estimate distribution",
        "fit parametric distribution", "calculate confidence interval", "calculate credible interval",
        "perform hypothesis test", "adjust multiple comparisons", "bootstrap sample", "permutation sample",
        "calculate effect size", "calculate statistical power", "determine sample size", "fit linear regression",
        "fit generalized linear model", "fit mixed-effects model", "fit survival model",
        "fit time-series model", "calculate residuals", "diagnose residuals", "calculate likelihood",
        "calculate posterior", "sample posterior", "calculate information criterion",
        "compare statistical models", "calibrate probability", "decompose variance",
        "propagate uncertainty", "perform sensitivity analysis", "summarize uncertainty"
    ]),
    ("sampling_partition", "pure_transform", "dat.sampling", [
        "simple random sample", "systematic sample", "stratified sample", "cluster sample",
        "multistage sample", "reservoir sample", "weighted sample", "importance sample",
        "oversample minority", "undersample majority", "sample by time", "sample by group",
        "sample by hash", "split train validation test", "split temporal holdout", "cross-validation split",
        "rolling-origin split", "bootstrap resample", "jackknife resample", "partition by key",
        "partition by range", "partition by time", "partition by hash", "repartition collection",
        "coalesce partitions", "balance partitions", "detect partition skew", "salt skewed key",
        "preserve sample weights", "calculate inclusion probability", "record sampling design"
    ]),
    ("graph", "pure_transform", "dat.graph", [
        "construct graph", "add graph vertex", "add graph edge", "remove graph vertex", "remove graph edge",
        "project graph", "filter graph", "traverse graph", "find graph path", "find shortest path",
        "calculate reachability", "calculate connected components", "calculate centrality",
        "detect communities", "match subgraph", "calculate graph cut", "calculate network flow",
        "detect graph cycle", "topologically sort graph", "calculate graph motif", "diff graphs",
        "merge graphs", "resolve temporal graph state", "propagate graph signal", "simulate graph diffusion",
        "validate graph constraint", "reconcile graph identity", "emit graph lineage"
    ]),
    ("spatial", "pure_transform", "dat.spatial", [
        "parse geometry", "validate geometry", "repair geometry", "transform coordinate reference system",
        "calculate spatial distance", "calculate geodesic distance", "calculate area", "calculate length",
        "calculate bearing", "buffer geometry", "intersect geometries", "union geometries",
        "subtract geometries", "clip geometry", "simplify geometry", "densify geometry",
        "spatially join records", "point-in-polygon test", "nearest-neighbor spatial search",
        "geocode address", "reverse geocode point", "map match trajectory", "interpolate spatial surface",
        "aggregate raster zones", "resample raster", "reproject raster", "tile raster",
        "calculate spatial autocorrelation", "detect spatial hotspot", "construct origin-destination matrix",
        "trace spatial route", "calculate catchment", "attach spatial provenance"
    ]),
    ("content_signal", "pure_transform", "dat.content-signal", [
        "tokenize text", "normalize text tokens", "calculate term frequency", "extract keyphrase",
        "match text pattern", "classify text by rules", "extract document field", "parse document layout",
        "calculate document similarity", "deduplicate documents", "detect language", "score readability",
        "transform signal spectrum", "filter signal", "smooth signal", "denoise signal", "detect peak",
        "calculate autocorrelation", "calculate cross-correlation", "calculate coherence", "extract waveform feature",
        "segment image", "detect image edge", "apply image morphology", "register images",
        "track image motion", "calculate image quality", "extract media metadata", "align media timeline",
        "preserve original content", "attach extraction lineage"
    ]),
    ("process_event", "stateful_transform", "dat.process-event", [
        "construct process event", "validate event-log minimums", "correlate event to case",
        "correlate event to object", "order case events", "construct event trace", "construct object-centric event graph",
        "discover process model", "replay event on process model", "align event log to model",
        "calculate conformance fitness", "calculate conformance precision", "calculate model generalization",
        "detect process deviation", "classify process variant", "compare process variants",
        "calculate process waiting time", "calculate process cycle time", "detect process rework",
        "localize process bottleneck", "analyze process handoff", "predict remaining process time",
        "predict next process activity", "simulate process execution", "detect process drift",
        "recommend process intervention", "record process intervention", "evaluate process intervention"
    ]),
    ("optimization_simulation", "planner", "dat.decision-model", [
        "formulate decision variables", "formulate objective", "formulate constraint", "validate decision model",
        "linearize decision model", "relax decision model", "decompose decision model", "select solver",
        "configure solver", "warm start solver", "solve exact model", "solve approximate model",
        "run heuristic", "run constructive heuristic", "run local search", "run metaheuristic", "run matheuristic",
        "simulate scenario", "run Monte Carlo simulation", "run discrete-event simulation",
        "run system-dynamics simulation", "run agent-based simulation", "run simulation optimization",
        "detect infeasible model", "extract infeasible subsystem", "detect unbounded model",
        "calculate optimality gap", "verify solution feasibility", "verify solution optimality",
        "analyze solution sensitivity", "enumerate alternative solutions", "explain constraint trade-off",
        "cancel solve", "checkpoint solve", "resume solve", "emit solution receipt",
        "evaluate realized decision outcome"
    ]),
    ("object_storage", "effectful_runtime", "dat.object-storage", [
        "put object", "get object", "head object", "delete object", "copy object", "move object",
        "list objects", "list object versions", "get object version", "restore object version",
        "begin multipart upload", "upload object part", "complete multipart upload", "abort multipart upload",
        "verify object ETag", "apply object retention", "apply legal hold", "transition object storage class",
        "expire object", "generate presigned access", "revoke object access", "replicate object",
        "verify object replication", "inventory object store", "detect orphan object", "garbage collect object",
        "emit object mutation receipt"
    ]),
    ("analytical_table", "effectful_runtime", "dat.analytical-table", [
        "create analytical table", "evolve analytical table schema", "append table data", "overwrite table data",
        "merge table data", "delete table data", "rewrite table files", "commit table snapshot",
        "abort table commit", "read table snapshot", "time travel table", "branch table state", "tag table state",
        "merge table branch", "expire table snapshot", "remove orphan table files", "compact table files",
        "cluster table data", "sort table data", "partition table data", "evolve partition specification",
        "collect table statistics", "rewrite table manifests", "register table", "rename table", "drop table",
        "restore table", "validate table metadata", "repair table metadata", "detect table conflict",
        "resolve table conflict", "emit table commit receipt"
    ]),
    ("index_search", "effectful_runtime", "dat.index-search", [
        "create index", "build index", "incrementally update index", "delete index entry", "compact index",
        "refresh index", "validate index consistency", "rebuild index", "search exact key",
        "search full text", "search faceted fields", "search fuzzy text", "search by similarity",
        "search temporal interval", "search spatial region", "rank search results", "filter search results",
        "highlight search match", "paginate search results", "explain search score", "evaluate retrieval relevance",
        "measure index coverage", "detect stale index", "switch index alias", "rollback index version",
        "snapshot index", "restore index", "emit index mutation receipt"
    ]),
    ("orchestration", "planner", "dat.orchestration", [
        "compile job graph", "validate job graph", "topologically order jobs", "plan job execution",
        "schedule job", "start job", "pause job", "resume job", "cancel job", "retry job",
        "skip job", "rerun job", "backfill job", "replay job", "branch job run", "join job branches",
        "wait for dependency", "wait for external signal", "emit job signal", "evaluate job condition",
        "apply retry policy", "apply timeout policy", "apply compensation policy", "record job heartbeat",
        "detect stalled job", "recover abandoned job", "deduplicate job request", "checkpoint job progress",
        "emit job outcome", "reconcile desired and actual job state", "calculate critical path",
        "enforce concurrency limit", "enforce execution window", "apply maintenance calendar"
    ]),
    ("runtime_resource", "effect_intent", "dat.resource-control", [
        "estimate resource requirement", "reserve compute resource", "allocate compute resource",
        "release compute resource", "scale compute resource", "place workload", "migrate workload",
        "preempt workload", "prioritize workload", "admit workload", "reject workload",
        "enforce CPU budget", "enforce memory budget", "enforce storage budget", "enforce network budget",
        "enforce I/O budget", "enforce cost budget", "precharge finite budget", "refund unused budget",
        "throttle workload", "apply backpressure", "spill intermediate state", "cancel resource usage",
        "detect resource exhaustion", "detect resource leak", "measure utilization", "attribute resource cost",
        "attribute energy use", "emit resource receipt", "degrade execution mode", "restore execution mode"
    ]),
    ("transaction_consistency", "state_transition", "dat.transaction", [
        "begin transaction", "read transaction state", "write transaction state", "prepare transaction",
        "commit transaction", "abort transaction", "compensate transaction", "retry transaction",
        "acquire lock", "renew lock", "release lock", "detect deadlock", "resolve deadlock",
        "compare version", "increment version", "detect write conflict", "resolve write conflict",
        "apply optimistic concurrency", "apply pessimistic concurrency", "establish snapshot isolation",
        "establish serializable isolation", "establish read consistency", "establish quorum",
        "replicate state", "detect replica lag", "fail over authority", "elect authority",
        "fence stale writer", "deduplicate command", "record idempotency key", "expire idempotency key",
        "emit transaction receipt"
    ]),
    ("lineage_provenance", "evidence_emitter", "dat.lineage-provenance", [
        "record data origin", "record derivation activity", "record responsible agent", "record source edition",
        "record operation invocation", "record input identity", "record output identity", "record parameter values",
        "record code identity", "record environment identity", "record provider identity", "record policy decision",
        "record human approval", "record uncertainty lineage", "construct lineage edge", "construct lineage graph",
        "query upstream lineage", "query downstream lineage", "calculate blast radius", "validate lineage completeness",
        "reconcile lineage evidence", "sign provenance record", "verify provenance signature",
        "redact provenance disclosure", "publish provenance subset", "retain provenance evidence",
        "expire provenance evidence", "recall provenance assertion", "emit execution receipt",
        "bind evidence to requirement"
    ]),
    ("security_privacy", "effect_intent", "dat.security-privacy", [
        "classify data sensitivity", "classify data purpose", "evaluate access policy", "authorize data access",
        "deny data access", "mask value", "redact field", "tokenize value", "detokenize value",
        "pseudonymize identity", "anonymize dataset", "generalize quasi-identifier", "suppress small cell",
        "add differential privacy noise", "account privacy budget", "enforce row policy", "enforce column policy",
        "filter by purpose", "filter by jurisdiction", "filter by residency", "enforce consent",
        "revoke consent", "propagate revocation", "apply retention policy", "apply deletion right",
        "export subject data", "audit data access", "detect policy conflict", "resolve policy precedence",
        "emit authorization receipt", "emit privacy receipt"
    ]),
    ("governance_lifecycle", "state_transition", "dat.governance", [
        "register data asset", "assign semantic owner", "assign operational owner", "classify data asset",
        "certify data asset", "decertify data asset", "publish data contract", "accept data contract",
        "reject data contract", "waive data requirement", "expire waiver", "open data issue",
        "assign data issue", "resolve data issue", "close data issue", "reopen data issue",
        "approve data change", "reject data change", "publish data product", "deprecate data product",
        "retire data product", "recall data product", "record data SLA", "evaluate data SLA",
        "declare data residency", "declare retention schedule", "hold data deletion", "release data hold",
        "qualify data provider", "disqualify data provider", "record governance decision"
    ]),
    ("version_migration", "planner", "dat.compatibility-migration", [
        "compare semantic editions", "classify semantic compatibility", "calculate semantic diff",
        "plan schema migration", "plan data migration", "plan contract migration", "generate upcaster",
        "generate downcaster", "transform historical record", "backfill derived field", "recompute historical result",
        "replay historical event", "dual write editions", "dual read editions", "parallel run editions",
        "canary new edition", "validate migrated state", "reconcile old and new results", "rollback edition",
        "roll forward edition", "decommission old edition", "dispose in-flight work", "translate integration event",
        "preserve historical interpretation", "detect migration loss", "record migration exception",
        "emit migration receipt", "calculate migration blast radius"
    ]),
    ("output_consumption", "pure_transform", "dat.output", [
        "construct analytical result", "attach uncertainty to result", "attach limitation to result",
        "attach evidence to result", "construct tabular projection", "construct chart specification",
        "construct map specification", "construct graph visualization", "construct alert",
        "construct report", "construct export", "construct decision recommendation",
        "construct explanation", "construct counterfactual explanation", "construct drill path",
        "construct case view", "construct audit view", "localize output", "format accessible output",
        "redact output", "watermark output", "sign output", "publish output", "retract output",
        "correct output", "version output", "record output consumption", "record decision action",
        "record outcome feedback"
    ])
]


DEFAULTS = {
    "predicate": ("pure", "deterministic", "not_applicable", "partial_typed_refusal", "not_applicable", "insensitive", "none", "stateless"),
    "pure_transform": ("pure", "deterministic", "not_applicable", "partial_typed_refusal", "unadjudicated", "unadjudicated", "unadjudicated", "stateless"),
    "reducer": ("pure", "deterministic", "not_applicable", "partial_typed_refusal", "lossy_declared", "unadjudicated", "unadjudicated", "bounded_state"),
    "stateful_transform": ("unadjudicated", "unadjudicated", "unadjudicated", "partial_typed_refusal", "unadjudicated", "order_required", "unadjudicated", "unadjudicated"),
    "planner": ("pure", "unadjudicated", "not_applicable", "partial_typed_refusal", "not_applicable", "unadjudicated", "unadjudicated", "unadjudicated"),
    "validator": ("pure", "deterministic", "not_applicable", "total", "not_applicable", "insensitive", "unadjudicated", "stateless"),
    "effect_intent": ("emits_intent", "deterministic", "by_key", "partial_typed_refusal", "not_applicable", "order_required", "unadjudicated", "external_state"),
    "effectful_runtime": ("read_write_external_state", "environment_dependent", "conditional", "partial_typed_failure", "unadjudicated", "order_required", "unadjudicated", "external_state"),
    "evidence_emitter": ("writes_external_state", "deterministic", "by_key", "partial_typed_failure", "not_applicable", "order_required", "recording_time", "external_state"),
    "state_transition": ("read_write_external_state", "deterministic", "by_key", "partial_typed_refusal", "not_applicable", "order_required", "recording_time", "external_state")
}


def slug(value: str) -> str:
    value = value.lower().replace("'", "").replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def main() -> int:
    records = []
    ids = set()
    labels = {}
    for family, kind, owner, names in FAMILIES:
        family_id = f"operation.{family}"
        for name in names:
            operation_id = f"{family_id}.{slug(name)}"
            if operation_id in ids:
                raise ValueError(f"duplicate operation id: {operation_id}")
            ids.add(operation_id)
            labels.setdefault(name.lower(), []).append(operation_id)
            effect, determinism, idempotency, totality, loss, order, time, state = DEFAULTS[kind]
            records.append({
                "operation_id": operation_id,
                "edition": 1,
                "status": "hypothesis",
                "family_id": family_id,
                "name": name,
                "operation_kind": kind,
                "semantic_owner_candidate": owner,
                "signature": {"type_parameters": [], "inputs": [], "outputs": [], "error_type": "UnadjudicatedOperationError"},
                "effect_class": effect,
                "determinism": determinism,
                "idempotency": idempotency,
                "totality": totality,
                "information_loss": loss,
                "order_sensitivity": order,
                "time_sensitivity": time,
                "statefulness": state,
                "execution_modes": [],
                "preconditions": [],
                "postconditions": [],
                "laws": [],
                "refusals": [],
                "failures": [],
                "resource_model": [],
                "provider_requirements": [],
                "evidence_refs": [],
                "llm_dependency": "none",
                "gaps": [
                    "candidate identity and semantic owner require adjudication",
                    "exact typed signature, laws and refusal precedence are unspecified",
                    "execution-mode and provider conformance are unspecified",
                    "primary evidence and compiler lowering are unspecified"
                ]
            })

    duplicates = {name: refs for name, refs in sorted(labels.items()) if len(refs) > 1}
    with (HERE / "operation-candidates.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    (HERE / "family-catalog.json").write_text(json.dumps({
        "edition": 1,
        "status": "hypothesis_queue",
        "family_count": len(FAMILIES),
        "candidate_count": len(records),
        "families": [
            {"family_id": f"operation.{family}", "operation_kind": kind, "semantic_owner_candidate": owner, "candidate_count": len(names)}
            for family, kind, owner, names in FAMILIES
        ],
        "duplicate_label_review_queue": duplicates,
        "completion_claim": False
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {len(records)} operation hypotheses across {len(FAMILIES)} families; {len(duplicates)} duplicate labels need review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
