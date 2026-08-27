#!/usr/bin/env python3
"""Build the provider-neutral telemetry signal semantics corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def source(ident: str, title: str, url: str, scope: str, limit: str, status: str = "stable_or_mixed_as_marked") -> dict:
    return {
        "source_id": f"source.telemetry.{ident}", "title": title, "publisher": "OpenTelemetry / CNCF" if not ident.startswith("w3c") else "W3C",
        "url": url, "source_kind": "official_specification", "claim_scope": scope, "scope_limit": limit, "source_status": status,
    }


SOURCES = [
    source("otel.overview", "OpenTelemetry Specification Overview", "https://opentelemetry.io/docs/specs/otel/overview/", "signal families, resources, context and propagation", "A telemetry specification does not define service health, causality or business truth."),
    source("otel.common", "OpenTelemetry Common Specification", "https://opentelemetry.io/docs/specs/otel/common/", "attribute values and collections", "String rendering may lose numeric and type fidelity."),
    source("otel.resource", "OpenTelemetry Resource Data Model", "https://opentelemetry.io/docs/specs/otel/resource/data-model/", "observed-entity attribution, identity and resource merge", "Resource identity is telemetry attribution, not enterprise master-data identity.", "development"),
    source("otel.scope", "OpenTelemetry Instrumentation Scope", "https://opentelemetry.io/docs/specs/otel/common/instrumentation-scope/", "instrumentation producer scope and schema URL", "Instrumentation scope identifies emitting software, not necessarily the observed entity."),
    source("otel.schemas", "OpenTelemetry Telemetry Schemas", "https://opentelemetry.io/docs/specs/otel/schemas/", "schema URLs and telemetry schema transformations", "A schema transform cannot silently repair unknown domain meaning."),
    source("otel.semconv", "OpenTelemetry Semantic Conventions", "https://opentelemetry.io/docs/specs/semconv/", "versioned names, types and valid values", "Conventions do not prove collection completeness or correctness."),
    source("otel.trace", "OpenTelemetry Trace Specification", "https://opentelemetry.io/docs/specs/otel/trace/", "span, trace, parent, link, event and status semantics", "A trace graph is observed execution structure, not proof of business causality."),
    source("otel.trace_sdk", "OpenTelemetry Tracing SDK", "https://opentelemetry.io/docs/specs/otel/trace/sdk/", "recording, sampling, processing and exporting decisions", "SDK defaults are implementation defaults and must not become hidden compiler semantics."),
    source("otel.metrics", "OpenTelemetry Metrics Data Model", "https://opentelemetry.io/docs/specs/otel/metrics/data-model/", "metric stream identity, temporality, aggregation, resets and gaps", "Telemetry metrics are not business measures, SLO verdicts or source facts."),
    source("otel.metrics_sdk", "OpenTelemetry Metrics SDK", "https://opentelemetry.io/docs/specs/otel/metrics/sdk/", "instruments, views, aggregation and readers", "A view is a collection transformation, not a semantic-layer measure definition."),
    source("otel.logs", "OpenTelemetry Logs Data Model", "https://opentelemetry.io/docs/specs/otel/logs/data-model/", "event and observed timestamps, severity, body and trace fields", "Log severity and text do not establish incident, root cause or domain-event truth."),
    source("otel.profiles", "OpenTelemetry Profiles", "https://opentelemetry.io/docs/specs/otel/profiles/", "profile samples, stack dictionaries and signal links", "Profiles are alpha and cannot be silently treated as a stable portable contract.", "alpha"),
    source("otel.otlp", "OTLP Specification 1.11.0", "https://opentelemetry.io/docs/specs/otlp/", "encoding, transport, full/partial success, retry and duplicate limits", "Request acknowledgement does not prove durable storage, query visibility or downstream use."),
    source("w3c.trace_context", "W3C Trace Context", "https://www.w3.org/TR/trace-context/", "traceparent and tracestate propagation", "Propagation supports correlation; it neither guarantees recording nor proves causality."),
    source("w3c.baggage", "W3C Baggage", "https://www.w3.org/TR/baggage/", "application metadata propagation", "Baggage crosses trust boundaries and requires explicit privacy and size policy."),
]


CONTEXTS = [
    ("attribution", "Telemetry attribution", "Which observed entity and instrumentation scope does a signal claim, under which exact identity and merge rules?"),
    ("schema", "Telemetry schema and conventions", "Which editioned field vocabulary and directional transformation gives attributes their telemetry meaning?"),
    ("trace", "Trace graph", "What span occurrences, parentage, links, events and statuses form one observed distributed execution graph?"),
    ("metric", "Metric streams", "What exact stream identity, point kind, unit, temporality, aggregation and gap semantics apply to measurements?"),
    ("log", "Logs and event records", "What occurred or was observed, at which times, severity and body mapping, without promoting a record to domain fact?"),
    ("profile", "Execution profiles", "What sampled stacks and resource-consumption values were captured under which format, period and stability contract?"),
    ("propagation", "Telemetry context propagation", "How are correlation context and baggage parsed, forwarded, restarted or removed across a trust boundary?"),
    ("reduction", "Observation reduction and loss", "What selection, filtering, aggregation or truncation changed an observation population, and what loss remains?"),
    ("correlation", "Cross-signal correlation", "Which evidence-bearing edges relate distinct telemetry occurrences without asserting causality or completeness?"),
    ("export", "Telemetry export delivery", "What exact batch was offered to which destination, and what delivery outcome, retry obligation or uncertainty followed?"),
]

CONTEXT_ROWS = [{
    "context_id": f"context.telemetry.{slug}", "name": name, "sovereign_question": question,
    "inside": ["editioned semantic types", "typed operations", "decisions", "laws", "refusals"],
    "outside": ["service health", "incident and root-cause judgment", "business-domain truth", "provider qualification", "effect authority"],
    "owner": f"authority.telemetry.{slug}", "status": "specified_candidate",
} for slug, name, question in CONTEXTS]


DECISIONS: dict[str, list[tuple[str, str]]] = {
    "attribution": [("attribute_limits", "Which attribute types, count, size and truncation limits apply?"), ("resource_identity", "Which entity and raw-attribute fields identify the observed resource?"), ("resource_merge", "How are entity, attribute and schema conflicts merged or refused?"), ("scope_identity", "Which name, version, schema URL and attributes identify instrumentation scope?")],
    "schema": [("convention_edition", "Which semantic-convention edition and stability level apply?"), ("schema_url", "Which telemetry schema URL governs this payload?"), ("transform_direction", "Which source and target editions and directional transform are permitted?"), ("unknown_attribute", "Are unknown attributes preserved, quarantined or refused?"), ("loss_policy", "Which rename, coercion, split, merge or deletion losses are permitted?")],
    "trace": [("span_identity", "Which trace/span identity and uniqueness scope apply?"), ("parent_link", "When is an edge parentage versus a non-parent link?"), ("span_kind", "Which producer, consumer, client, server or internal kind applies?"), ("status", "How is unset, ok or error status derived without inferring domain success?"), ("event_limit", "Which span-event and link limits and truncation receipts apply?"), ("clock", "Which start/end clock, precision and skew policy applies?")],
    "metric": [("stream_identity", "Which resource, scope, name, point type, unit, temporality and monotonicity identify a stream?"), ("point_kind", "Which gauge, sum, histogram, exponential histogram or summary contract applies?"), ("temporality", "Is aggregation delta or cumulative, with which start-time semantics?"), ("aggregation", "Which aggregation and view transformation applies?"), ("reset_gap", "How are reset, unknown start, gap, overlap and multi-writer conflict classified?"), ("cardinality", "Which attribute cardinality budget and overflow behavior applies?"), ("exemplar", "Which exemplar reservoir and correlation policy applies?")],
    "log": [("timestamp", "Which occurrence timestamp and origin clock apply?"), ("observed_timestamp", "Which collection observation timestamp and observer apply?"), ("severity_mapping", "How is source severity mapped, including unknown values?"), ("body_mapping", "How is a structured or unstructured source body represented without hidden coercion?"), ("event_name", "When is a log record treated as an editioned event class?"), ("trace_fields", "Which trace/span fields are valid and how is absence preserved?")],
    "profile": [("profile_edition", "Which alpha/stable format edition is explicitly enabled?"), ("sample_type", "Which sampled values and units apply?"), ("period", "Which sampling period, clock and jitter semantics apply?"), ("stack_identity", "Which mapping, function, location and build identity rules apply?"), ("original_payload", "When must an original payload be retained to avoid conversion loss?"), ("signal_link", "Which resource or trace/span links may be asserted?")],
    "propagation": [("format", "Which propagation format and edition apply?"), ("trust_boundary", "Which inbound and outbound trust boundary policy applies?"), ("restart", "When is trace context forwarded, participated in, restarted or refused?"), ("baggage_allowlist", "Which baggage keys, metadata, sizes and purposes may cross?"), ("conflict", "Which extraction and injection conflict precedence applies?"), ("privacy", "Which values must be removed or redacted before propagation?")],
    "reduction": [("stage", "At which production, SDK, collector or backend stage is reduction applied?"), ("method", "Which sampling, filtering, aggregation, truncation or redaction method applies?"), ("population", "What target population and eligibility predicate are claimed?"), ("probability", "What inclusion probability or weight is known for each retained observation?"), ("loss_accounting", "Which counts, ranges, fields and relationships became unavailable?"), ("budget", "Which overhead, volume, cardinality and latency budget constrains reduction?")],
    "correlation": [("edge_kind", "Which exact identity, resource, scope, trace, exemplar, profile or temporal edge kind applies?"), ("multiplicity", "Which one-to-one, one-to-many or many-to-many relation is permitted?"), ("time_tolerance", "Which time basis, skew and tolerance constrain temporal correlation?"), ("confidence", "Which deterministic match, asserted link or scored hypothesis status applies?"), ("missing_edge", "How is an absent or broken correlation edge represented?"), ("causality", "Which authority, if any, may separately assert causality?")],
    "export": [("protocol", "Which OTLP or other protocol edition and encoding apply?"), ("destination", "Which occurrence-scoped destination and tenant/purpose binding apply?"), ("batch", "Which batch sizing, ordering and concurrency rules apply?"), ("compression", "Which compression and decompression limits apply?"), ("retry", "Which status classes, backoff, deadline and retry budget apply?"), ("partial_success", "How are accepted and rejected record counts and diagnostics represented?"), ("duplicate", "Which duplicate possibility and downstream deduplication contract apply?"), ("backpressure", "Which throttle, buffer, shedding and cancellation behavior applies?")],
}

DECISION_ROWS = [{
    "decision_id": f"decision.telemetry.{context}.{slug}", "owner_context": f"context.telemetry.{context}",
    "question": question, "default": None, "default_law": "forbidden", "status": "declared",
} for context, values in DECISIONS.items() for slug, question in values]


def op(library: str, name: str, inputs: list[str], output: str, purity: str = "pure", intent: str | None = None, receipt: str | None = None) -> dict:
    row = {"operation_ref": f"operation.telemetry.{library}.{name}", "input_types": inputs, "output_type": output, "purity": purity}
    if intent:
        row["effect_intent_type"] = intent
    if receipt:
        row["receipt_type"] = receipt
    return row


def library(slug: str, name: str, kind: str, types: list[str], operations: list[dict], laws: list[str], errors: list[str], dependencies: list[str], evidence: list[str], gaps: list[str] | None = None) -> dict:
    return {
        "library_id": f"library.telemetry.{slug}", "name": name, "library_kind": kind,
        "semantic_owner_context": f"context.telemetry.{slug if slug in DECISIONS else {'attribution_core':'attribution','schema_conventions':'schema','trace_graph':'trace','metric_stream':'metric','log_event':'log','profile_sample':'profile','propagation_context':'propagation','observation_reduction':'reduction','cross_signal_correlation':'correlation','export_delivery':'export'}[slug]}",
        "status": "specified", "candidate_responsibility": name.lower(),
        "effect_boundary": "pure_effect_intents" if kind == "effect_port" else "pure_no_io",
        "public_types": types, "public_traits": [name.replace(" ", "") + "Algebra"],
        "operation_refs": [row["operation_ref"] for row in operations], "operations": operations,
        "decision_refs": [row["decision_id"] for row in DECISION_ROWS if row["owner_context"] == f"context.telemetry.{slug if slug in DECISIONS else {'attribution_core':'attribution','schema_conventions':'schema','trace_graph':'trace','metric_stream':'metric','log_event':'log','profile_sample':'profile','propagation_context':'propagation','observation_reduction':'reduction','cross_signal_correlation':'correlation','export_delivery':'export'}[slug]}"],
        "configuration_contracts": [name.replace(" ", "") + "Policy"], "laws": laws,
        "invariants": ["every semantic edition is explicit", "source occurrence, observed entity, instrumentation producer and collector occurrence remain distinct", "unknown, absent, dropped, rejected and unsupported remain distinct"],
        "error_contracts": errors + ["UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
        "dependencies": dependencies, "evidence_refs": evidence,
        "oracles": ["canonical fixtures", "negative twins", "property laws", "malformed boundary corpus", "edition migration corpus", "two-provider differential corpus"],
        "gaps": (gaps or []) + ["No implementation is qualified or portable; two independent implementations and executed conformance remain required."],
        "must_not_own": ["service health", "SLO or incident verdict", "root cause or causality", "business-domain event truth", "provider qualification", "effect authority"],
        "qualification_required": False,
    }


LIBRARIES = [
    library("attribution_core", "Telemetry Attribution Core", "semantic_pure",
        ["AttributeKey", "AttributeValue", "AttributeSet", "AttributeLoss", "EntityId", "Entity", "ResourceIdentity", "Resource", "ResourceMergeInput", "ResourceMergeResult", "InstrumentationScopeId", "InstrumentationScope", "TelemetrySchemaUrl", "AttributionRefusal"],
        [op("attribution", "validate_attributes", ["AttributeSet", "AttributePolicy"], "Result<AttributeSet,AttributionRefusal>"), op("attribution", "identify_resource", ["EntitySet", "AttributeSet", "ResourceIdentityPolicy"], "Result<ResourceIdentity,AttributionRefusal>"), op("attribution", "merge_resources", ["ResourceMergeInput", "ResourceMergePolicy"], "Result<ResourceMergeResult,AttributionRefusal>"), op("attribution", "identify_scope", ["InstrumentationScope", "ScopeIdentityPolicy"], "Result<InstrumentationScopeId,AttributionRefusal>")],
        ["Observed resource identity is not enterprise entity identity.", "The observed entity is not necessarily the instrumentation producer or collector.", "Resource merge conflicts are retained or refused, never silently overwritten.", "Attribute truncation or coercion emits explicit loss."],
        ["InvalidAttribute", "AttributeLimitExceeded", "ResourceIdentityUnknown", "ResourceConflict", "ScopeIdentityInvalid"], [], ["source.telemetry.otel.common", "source.telemetry.otel.resource", "source.telemetry.otel.scope"]),
    library("schema_conventions", "Telemetry Schema Conventions", "semantic_pure",
        ["ConventionEdition", "ConventionStability", "TelemetryFieldId", "TelemetryFieldDefinition", "TelemetrySchema", "SchemaTransform", "TransformDirection", "TransformResult", "TransformLoss", "SchemaRefusal"],
        [op("schema", "validate_schema", ["TelemetrySchema", "ConventionEdition"], "Result<TelemetrySchema,SchemaRefusal>"), op("schema", "resolve_field", ["TelemetryFieldId", "ConventionEdition"], "Result<TelemetryFieldDefinition,SchemaRefusal>"), op("schema", "transform_schema", ["TelemetryPayload", "SchemaTransform"], "Result<TransformResult,SchemaRefusal>"), op("schema", "diff_editions", ["ConventionEdition", "ConventionEdition"], "Result<SchemaDiff,SchemaRefusal>")],
        ["A field name without an exact convention edition has no portable telemetry meaning.", "Schema transformation is directional and may be partial.", "Schema validity does not prove observation correctness or collection completeness.", "Provider aliases cannot select semantic-convention meaning."],
        ["ConventionEditionUnknown", "FieldAmbiguous", "TransformUnavailable", "TransformLossUnauthorized", "StabilityUnsupported"], ["library.telemetry.attribution_core"], ["source.telemetry.otel.schemas", "source.telemetry.otel.semconv"]),
    library("trace_graph", "Telemetry Trace Graph", "semantic_pure",
        ["TraceId", "SpanId", "TraceFlags", "TraceState", "SpanContext", "SpanOccurrence", "SpanKind", "SpanStatus", "ParentEdge", "SpanLink", "SpanEvent", "TraceGraph", "TraceGap", "TraceRefusal"],
        [op("trace", "validate_span", ["SpanOccurrence", "TracePolicy"], "Result<SpanOccurrence,TraceRefusal>"), op("trace", "assemble_trace", ["SpanSet", "TraceAssemblyPolicy"], "Result<TraceGraph,TraceRefusal>"), op("trace", "classify_edges", ["SpanSet", "EdgePolicy"], "Result<TraceEdgeSet,TraceRefusal>"), op("trace", "detect_trace_gaps", ["TraceGraph", "GapPolicy"], "Result<TraceGapSet,TraceRefusal>")],
        ["Parent edge, span link, temporal adjacency and inferred causality are distinct.", "Span status is not business success, service health or incident state.", "A sampled flag is not a guarantee that any complete trace is recorded or exported.", "Missing spans remain gaps and are never synthesized as facts."],
        ["TraceIdentityInvalid", "SpanIdentityConflict", "ParentCycle", "ClockOrderInvalid", "TraceIncomplete"], ["library.telemetry.attribution_core", "library.telemetry.schema_conventions"], ["source.telemetry.otel.trace", "source.telemetry.otel.trace_sdk", "source.telemetry.w3c.trace_context"]),
    library("metric_stream", "Telemetry Metric Stream", "semantic_pure",
        ["MetricStreamId", "MetricName", "MetricUnit", "PointKind", "AggregationTemporality", "MetricPoint", "GaugePoint", "SumPoint", "HistogramPoint", "ExponentialHistogramPoint", "Exemplar", "MetricStream", "StreamReset", "StreamGap", "AggregationPlan", "MetricRefusal"],
        [op("metric", "identify_stream", ["MetricDescriptor", "MetricIdentityPolicy"], "Result<MetricStreamId,MetricRefusal>"), op("metric", "validate_point", ["MetricPoint", "MetricStream"], "Result<MetricPoint,MetricRefusal>"), op("metric", "reaggregate", ["MetricStream", "AggregationPlan"], "Result<MetricStream,MetricRefusal>"), op("metric", "classify_resets_gaps", ["MetricStream", "GapPolicy"], "Result<MetricContinuity,MetricRefusal>")],
        ["Point type, unit, temporality and monotonicity are identifying semantics, not display metadata.", "Delta, cumulative, reset, gap, overlap and absent are distinct.", "Spatial or temporal reaggregation declares removed attributes, resolution and irrecoverable information.", "A telemetry metric is not a business measure, SLO result, invoice quantity or source-system fact."],
        ["MetricIdentityConflict", "UnitConflict", "TemporalityConflict", "AggregationInvalid", "ResetUnknown", "CardinalityExceeded"], ["library.telemetry.attribution_core", "library.telemetry.schema_conventions"], ["source.telemetry.otel.metrics", "source.telemetry.otel.metrics_sdk"]),
    library("log_event", "Telemetry Log and Event Record", "semantic_pure",
        ["LogRecordId", "OccurrenceTimestamp", "ObservedTimestamp", "SeverityNumber", "SeverityText", "LogBody", "EventName", "LogRecord", "TraceCorrelationFields", "LogMapping", "LogMappingLoss", "LogRefusal"],
        [op("log", "map_source_record", ["SourceLogRecord", "LogMapping"], "Result<LogRecord,LogRefusal>"), op("log", "validate_record", ["LogRecord", "LogPolicy"], "Result<LogRecord,LogRefusal>"), op("log", "map_severity", ["SourceSeverity", "SeverityMapping"], "Result<SeverityNumber,LogRefusal>"), op("log", "classify_event_record", ["LogRecord", "EventSchemaPolicy"], "Result<EventClassification,LogRefusal>")],
        ["Occurrence timestamp and observed timestamp are different clocks and may not be substituted silently.", "A log event is not automatically a domain event, audit fact, incident or root cause.", "Severity text and number mappings retain source value and mapping edition.", "Trace identifiers enable correlation but do not prove causal responsibility."],
        ["TimestampUnknown", "SeverityMappingUnknown", "BodyMappingLoss", "EventSchemaUnknown", "TraceFieldsInvalid"], ["library.telemetry.attribution_core", "library.telemetry.schema_conventions"], ["source.telemetry.otel.logs"]),
    library("profile_sample", "Telemetry Profile Sample", "semantic_pure",
        ["ProfileId", "ProfileFormatEdition", "SampleType", "SamplePeriod", "ProfileSample", "StackTrace", "MappingId", "FunctionId", "LocationId", "BuildId", "OriginalPayloadRef", "ProfileLink", "Profile", "ProfileRefusal"],
        [op("profile", "validate_profile", ["Profile", "ProfilePolicy"], "Result<Profile,ProfileRefusal>"), op("profile", "resolve_stack", ["ProfileSample", "ProfileDictionary"], "Result<StackTrace,ProfileRefusal>"), op("profile", "convert_profile", ["Profile", "ProfileConversion"], "Result<ProfileConversionResult,ProfileRefusal>"), op("profile", "link_sample", ["ProfileSample", "ProfileLinkPolicy"], "Result<ProfileLink,ProfileRefusal>")],
        ["Alpha profile semantics require explicit opt-in and cannot satisfy a stable-contract requirement.", "A sampled stack is an observation, not proof of complete execution or causal cost.", "Lossy conversion retains the original payload or an explicit irrecoverable-loss receipt.", "Build identity, mapping identity and function symbol are distinct."],
        ["ExperimentalEditionNotEnabled", "ProfileFormatUnsupported", "DictionaryReferenceInvalid", "BuildIdentityUnknown", "ConversionLossUnauthorized"], ["library.telemetry.attribution_core", "library.telemetry.schema_conventions"], ["source.telemetry.otel.profiles"], ["OpenTelemetry profiles are alpha; stable portable profile semantics remain unavailable."]),
    library("propagation_context", "Telemetry Propagation Context", "semantic_pure",
        ["TraceParent", "TraceStateEntry", "TraceState", "BaggageKey", "BaggageValue", "BaggageMetadata", "Baggage", "Carrier", "TrustBoundary", "PropagationPolicy", "PropagationResult", "PropagationLoss", "PropagationRefusal"],
        [op("propagation", "extract_context", ["Carrier", "PropagationPolicy"], "Result<PropagationResult,PropagationRefusal>"), op("propagation", "inject_context", ["PropagationContext", "Carrier", "PropagationPolicy"], "Result<Carrier,PropagationRefusal>"), op("propagation", "cross_trust_boundary", ["PropagationContext", "TrustBoundary", "PropagationPolicy"], "Result<PropagationResult,PropagationRefusal>"), op("propagation", "restart_trace_context", ["PropagationContext", "RestartPolicy"], "Result<PropagationResult,PropagationRefusal>")],
        ["Forwarding, participating in and restarting a trace are distinct operations.", "Propagation preserves correlation possibility but does not guarantee recording, export or end-to-end completeness.", "Baggage is not authorization, authentication, tenancy truth or trusted business context.", "Trust-boundary filtering records every removed or rewritten field."],
        ["TraceParentInvalid", "TraceStateInvalid", "CarrierUnsupported", "BaggageLimitExceeded", "TrustBoundaryPolicyMissing", "SensitiveValueForbidden"], [], ["source.telemetry.w3c.trace_context", "source.telemetry.w3c.baggage", "source.telemetry.otel.overview"]),
    library("observation_reduction", "Telemetry Observation Reduction", "policy_pure",
        ["ObservationPopulation", "EligibilityPredicate", "ReductionStage", "ReductionMethod", "InclusionProbability", "SamplingWeight", "AggregationDescriptor", "TruncationDescriptor", "ReductionPolicy", "ReductionDecision", "ReductionReceipt", "InformationLoss", "CoverageClaim", "ReductionRefusal"],
        [op("reduction", "plan_reduction", ["ObservationPopulation", "ReductionPolicy", "ResourceBudget"], "Result<ReductionPlan,ReductionRefusal>"), op("reduction", "evaluate_inclusion", ["ObservationRef", "ReductionPlan"], "Result<ReductionDecision,ReductionRefusal>"), op("reduction", "account_loss", ["ReductionInputSummary", "ReductionOutputSummary", "ReductionPlan"], "Result<ReductionReceipt,ReductionRefusal>"), op("reduction", "evaluate_coverage", ["ReductionReceiptSet", "CoveragePolicy"], "Result<CoverageClaim,ReductionRefusal>")],
        ["Recording, retaining, sampling, exporting and querying are separate selection stages.", "A retained sample without a known inclusion law cannot support an unbiased population claim.", "Filtering, aggregation, truncation, redaction and dropping are different losses.", "Reduction receipts describe observation coverage only; they do not prove source or service completeness."],
        ["PopulationUndefined", "InclusionProbabilityUnknown", "SamplingPolicyIncompatible", "LossUnaccounted", "CoverageUnsupported", "ReductionBudgetExceeded"], ["library.telemetry.trace_graph", "library.telemetry.metric_stream", "library.telemetry.log_event", "library.telemetry.profile_sample"], ["source.telemetry.otel.trace_sdk", "source.telemetry.otel.metrics", "source.telemetry.otel.logs", "source.telemetry.otel.profiles"]),
    library("cross_signal_correlation", "Telemetry Cross-Signal Correlation", "semantic_pure",
        ["SignalOccurrenceRef", "CorrelationEdgeId", "CorrelationEdgeKind", "CorrelationAssertion", "CorrelationEvidence", "CorrelationConfidence", "TemporalTolerance", "CorrelationGraph", "BrokenCorrelation", "CorrelationRefusal"],
        [op("correlation", "assert_edge", ["SignalOccurrenceRef", "SignalOccurrenceRef", "CorrelationEvidence", "CorrelationPolicy"], "Result<CorrelationAssertion,CorrelationRefusal>"), op("correlation", "validate_edge", ["CorrelationAssertion", "CorrelationPolicy"], "Result<CorrelationAssertion,CorrelationRefusal>"), op("correlation", "build_graph", ["CorrelationAssertionSet"], "Result<CorrelationGraph,CorrelationRefusal>"), op("correlation", "classify_broken_edges", ["CorrelationGraph", "ExpectedEdgePolicy"], "Result<BrokenCorrelationSet,CorrelationRefusal>")],
        ["Shared resource, scope, trace, time or attribute values are distinct correlation evidence kinds.", "Correlation does not imply causation, responsibility, root cause or domain identity.", "Missing correlation does not prove absence of a real-world relation.", "Scored hypotheses never become deterministic links without separate evidence and authority."],
        ["SignalOccurrenceUnknown", "EdgeKindUnsupported", "MultiplicityInvalid", "TimeBasisIncompatible", "CorrelationEvidenceInsufficient", "CausalityClaimForbidden"], ["library.telemetry.attribution_core", "library.telemetry.trace_graph", "library.telemetry.metric_stream", "library.telemetry.log_event", "library.telemetry.profile_sample"], ["source.telemetry.otel.overview", "source.telemetry.otel.logs", "source.telemetry.otel.profiles", "source.telemetry.w3c.trace_context"]),
    library("export_delivery", "Telemetry Export Delivery", "effect_port",
        ["TelemetryBatchId", "TelemetryBatch", "SignalCount", "ExportDestination", "ExportProtocolEdition", "ExportIntent", "ExportAttemptId", "ExportOutcome", "PartialSuccess", "RetryDirective", "ThrottleDirective", "DuplicatePossibility", "ExportReceipt", "ExportRefusal"],
        [op("export", "plan_export", ["TelemetryBatch", "ExportDestination", "ExportPolicy"], "Result<ExportIntent,ExportRefusal>"), op("export", "submit_export", ["ExportIntent"], "Result<ExportReceipt,ExportRefusal>", "effectful_explicit", "ExportIntent", "ExportReceipt"), op("export", "interpret_response", ["ExportIntent", "ProtocolResponse", "ExportProtocolEdition"], "Result<ExportReceipt,ExportRefusal>"), op("export", "plan_retry", ["ExportIntent", "ExportReceipt", "RetryPolicy"], "Result<RetryDirective,ExportRefusal>")],
        ["Export request, transport acceptance, partial success, durable storage, query visibility and downstream use are distinct facts.", "A retry creates a new attempt bound to the original batch and may create duplicates.", "Partial success retains accepted and rejected counts plus the server diagnostic.", "Timeout and connection loss preserve unknown completion; they are not converted to failure or success."],
        ["DestinationUnqualified", "ProtocolEditionUnsupported", "BatchInvalid", "CompressionLimitExceeded", "PartialSuccessUnaccounted", "RetryBudgetExhausted", "CompletionUnknown", "BackpressureUnsupported"], ["library.telemetry.observation_reduction"], ["source.telemetry.otel.otlp"]),
]


NEGATIVE_TWINS = [
    ("resource_is_entity", "A telemetry resource is the authoritative enterprise entity.", "Keep telemetry attribution separate from master-data identity and bind an ACL if needed."),
    ("scope_is_resource", "The instrumentation scope identifies the observed resource.", "Represent producer scope and observed resource independently."),
    ("schema_is_correct", "A convention-valid payload proves correct instrumentation.", "Require collection and domain-specific correctness evidence separately."),
    ("span_error_incident", "An error span proves an incident and its root cause.", "Treat status as a scoped observation; use separate incident and diagnostic models."),
    ("metric_is_measure", "A telemetry metric name is a governed business measure.", "Bind a semantic-layer measure definition separately."),
    ("zero_is_missing", "A missing metric interval means zero.", "Preserve absence, gap, reset, stale and measured zero distinctly."),
    ("log_is_domain_event", "A log record is an authoritative domain event or audit fact.", "Require the domain event or evidence owner to admit it through an ACL."),
    ("profile_stable", "An alpha profile payload satisfies a stable portable profile requirement.", "Refuse unless experimental semantics are explicitly requested."),
    ("baggage_authority", "Propagated baggage grants authorization or trusted tenant identity.", "Resolve authority through its owning security context."),
    ("sample_complete", "A sampled dataset represents the complete observation population.", "Require population, inclusion and loss receipts."),
    ("correlation_causation", "Shared trace or time correlation proves causal responsibility.", "Represent causality as a separately governed assertion."),
    ("export_stored", "An OTLP success response proves durable storage and query visibility.", "Retain only the protocol-scoped delivery receipt."),
    ("timeout_failed", "An export timeout proves the destination accepted nothing.", "Preserve unknown completion and reconcile before retry."),
    ("telemetry_health", "Available telemetry proves a healthy service.", "Evaluate an explicit health or SLO policy over qualified signals."),
]

NEGATIVE_ROWS = [{"negative_id": f"negative.telemetry.{slug}", "unsafe_inference": unsafe, "required_behavior": behavior, "status": "active"} for slug, unsafe, behavior in NEGATIVE_TWINS]


COMPILER_ROWS = []
for item in LIBRARIES:
    stem = item["library_id"].removeprefix("library.")
    req = f"requirement.{stem}.implementation"
    offer = f"offer.{stem}.reference"
    COMPILER_ROWS.extend([
        {"record_kind": "capability_requirement", "requirement_id": req, "subject_ref": item["library_id"], "required_operations": item["operation_refs"], "required_decisions": item["decision_refs"], "fallback_law": "refuse", "status": "declared"},
        {"record_kind": "capability_offer", "offer_id": offer, "subject_ref": item["library_id"], "claimed_operations": item["operation_refs"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
        {"record_kind": "binding_rule", "binding_rule_id": f"binding.{stem}", "requirement_ref": req, "offer_ref": offer, "structural_match": True, "selection_law": "Structural match never promotes an unqualified, unstable or non-portable offer.", "selectable": False, "status": "declared"},
    ])


FILES = {
    "sources.jsonl": SOURCES,
    "bounded-contexts.jsonl": CONTEXT_ROWS,
    "decision-points.jsonl": DECISION_ROWS,
    "library-contracts.jsonl": LIBRARIES,
    "compiler-contracts.jsonl": COMPILER_ROWS,
    "negative-twins.jsonl": NEGATIVE_ROWS,
}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = jsonl(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {
        "manifest_id": "telemetry_signal_semantics_v0_1_0", "as_of": AS_OF, "edition": EDITION,
        "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False,
        "qualified_implementation_count": 0, "stable_profile_contract_available": False,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS telemetry signals: {len(SOURCES)} sources, {len(CONTEXT_ROWS)} contexts, {len(DECISION_ROWS)} decisions, {len(LIBRARIES)} exact libraries, {len(COMPILER_ROWS)} compiler contracts")


if __name__ == "__main__":
    main()
