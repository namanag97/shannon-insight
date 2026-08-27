#!/usr/bin/env python3
"""Build a bearer-positioned time ontology and lossless all-member time rebase."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
PRECLASSIFICATIONS = SEM / "applicability_matrices/member-preclassifications.jsonl"
sys.path.insert(0, str(SEM))

from member_axis_rebase import build_member_rebase, load_jsonl  # noqa: E402


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


PRIMARY_SOURCES = [
    {
        "source_id": "source.time.owl-time",
        "title": "Time Ontology in OWL",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/owl-time/",
        "bounded_implication": "Instants, intervals, durations, temporal positions, topological relations, clocks, calendars and temporal reference systems are distinct temporal constructs.",
        "authority_limit": "OWL-Time does not select application time roles, clock authority, zone database edition, lateness/finality, correction or recording policy.",
    },
    {
        "source_id": "source.time.rfc3339",
        "title": "RFC 3339: Date and Time on the Internet: Timestamps",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc3339.html",
        "bounded_implication": "Internet timestamps encode date, time, numeric offset and optional fractional seconds with explicit leap-second and unknown-local-offset cases.",
        "authority_limit": "A textual timestamp and offset do not identify a time-zone rule set, application role, clock trust, causal order or semantic precision beyond the encoded value.",
    },
    {
        "source_id": "source.time.rfc9557",
        "title": "RFC 9557: Date and Time on the Internet: Timestamps with Additional Information",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc9557.html",
        "bounded_implication": "An Internet timestamp can carry a named time zone, calendar and criticality metadata separately from its numeric UTC offset.",
        "authority_limit": "Zone/calendar annotations do not choose application time role or guarantee future/past rule accuracy unless an edition and resolution policy are bound.",
    },
    {
        "source_id": "source.time.iana-tzdb-theory",
        "title": "Theory and pragmatics of the tz code and data",
        "publisher": "IANA Time Zone Database",
        "url": "https://www.iana.org/time-zones/theory",
        "bounded_implication": "Civil-time interpretation depends on editioned regional rules, historical/future scope, transitions, offsets and known accuracy limitations rather than a single permanent offset.",
        "authority_limit": "The tz database does not establish legal authority, perfect historical truth, clock error, application calendars or domain schedule policy.",
    },
    {
        "source_id": "source.time.rfc5545",
        "title": "RFC 5545: Internet Calendaring and Scheduling Core Object Specification",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc5545.html",
        "bounded_implication": "Calendar events, periods, durations, recurrence rules, exclusions, time zones and floating local times have distinct expansion and interpretation rules.",
        "authority_limit": "Recurrence syntax does not establish business-calendar acceptance, resource availability, execution, holiday authority or infinite expansion safety.",
    },
    {
        "source_id": "source.time.lamport-clocks",
        "title": "Time, Clocks, and the Ordering of Events in a Distributed System",
        "publisher": "ACM / Leslie Lamport",
        "url": "https://lamport.azurewebsites.net/pubs/time-clocks.pdf",
        "bounded_implication": "Happened-before is a partial order; logical clocks preserve its direction while total extensions and physical-clock readings do not create causal relations among concurrent events.",
        "authority_limit": "Logical clocks do not establish physical occurrence time, business causality, source truth or global simultaneous order.",
    },
    {
        "source_id": "source.time.apache-beam",
        "title": "Apache Beam Programming Guide",
        "publisher": "Apache Beam",
        "url": "https://beam.apache.org/documentation/programming-guide/",
        "bounded_implication": "Event timestamps, windows, watermarks, triggers, allowed lateness, state and timers are separate components; a watermark is an estimate of input progress.",
        "authority_limit": "Beam progress does not prove source completeness, business finality, clock truth or acceptance of external effects.",
    },
    {
        "source_id": "source.time.otel-metrics",
        "title": "OpenTelemetry Metrics Data Model",
        "publisher": "OpenTelemetry / CNCF",
        "url": "https://opentelemetry.io/docs/specs/otel/metrics/data-model/",
        "bounded_implication": "Metric streams distinguish observation timestamps, start timestamps, delta/cumulative temporality, reset detection, gaps and no-recorded-value markers.",
        "authority_limit": "Telemetry temporality does not establish domain validity time, business calendars, source finality or universal aggregation semantics.",
    },
    {
        "source_id": "source.time.w3c-prov-o",
        "title": "PROV-O: The PROV Ontology",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/prov-o/",
        "bounded_implication": "Generation, invalidation, activity start/end and qualified influence times attach to different provenance relations and subjects.",
        "authority_limit": "Provenance timestamps do not prove causal sufficiency, clock correctness, validity intervals, recording time or acceptance.",
    },
]


TEMPORAL_BEARER_ARCHETYPES = [
    ("instant", "Position on a declared time scale/reference system with precision and uncertainty."),
    ("local_date_time", "Calendar/clock fields without enough information to identify one instant."),
    ("offset_date_time", "Local calendar/clock fields plus numeric offset, distinct from a named zone."),
    ("zoned_date_time", "Local date-time resolved under a named, editioned time-zone rule set."),
    ("calendar_date_or_time_of_day", "Civil date or local time component not inherently an instant."),
    ("elapsed_duration", "Amount measured on an elapsed/monotonic scale."),
    ("calendar_period", "Calendar-relative amount whose realized duration depends on start and calendar rules."),
    ("time_interval", "Bounded or unbounded interval with endpoint and open/closed semantics."),
    ("occurrence_time", "Time at which a domain event or phenomenon occurs."),
    ("observation_time", "Time at which an occurrence or state is observed/measured."),
    ("validity_time", "Time over which a fact, rule, state or relationship is claimed valid in the modeled world."),
    ("recording_or_transaction_time", "Time over which a representation is recorded as current in a system of record."),
    ("ingestion_or_processing_time", "Time at which data enters or is processed by a computational system."),
    ("decision_time", "Time at which a proposal, judgment, approval or policy decision is made."),
    ("execution_or_effect_time", "Time at which an authorized effect starts, occurs or completes."),
    ("correction_or_supersession_time", "Time at which a prior assertion is corrected, retracted or superseded."),
    ("schedule_or_recurrence", "Rule generating intended temporal occurrences under calendar and zone semantics."),
    ("business_calendar", "Authority-scoped working/nonworking intervals, holidays and cutoffs."),
    ("deadline_or_timeout", "Constraint or elapsed budget relative to a declared origin and clock."),
    ("ttl_expiry_or_lease", "Age/expiry boundary with origin, renewal, grace and enforcement semantics."),
    ("window_pane_or_bucket", "Analytical grouping of occurrences over a temporal domain."),
    ("watermark_or_progress_frontier", "Estimate or proof frontier over which earlier events are not expected/accepted."),
    ("logical_or_causal_clock", "Logical counter/vector/hybrid carrier for order and concurrency, not ordinary civil time."),
    ("bitemporal_fact_or_history", "Fact/history with independently queryable validity and recording axes."),
    ("temporal_snapshot_or_as_of_cut", "View selected under an exact cut and one or more time roles."),
]


def temporal_bearer_rows() -> list[dict[str, Any]]:
    return [
        {
            "record_kind": "temporal_bearer_archetype",
            "archetype_id": f"archetype.time.{name}.v1",
            "meaning": meaning,
            "required_coordinate_ref": "ontology.semantic-axis.time-coordinate.v1#time_coordinate",
            "applicability": "UNRESOLVED_PER_TEMPORAL_BEARER_AND_USE_SITE",
            "completion_claim": False,
        }
        for name, meaning in TEMPORAL_BEARER_ARCHETYPES
    ]


ONTOLOGY = {
    "ontology_id": "ontology.semantic-axis.time-coordinate.v1",
    "edition": 1,
    "as_of": AS_OF,
    "axis": "time",
    "domain_question": "For each temporal bearer and use site, what time role, carrier, reference system, clock/calendar/zone authority, precision, interval/duration semantics, progress/finality, correction and evidence contract applies?",
    "coordinate_key": [
        "bounded_context_ref", "subject_ref", "temporal_bearer_ref", "time_role_ref",
        "time_profile_edition_ref", "use_site_ref",
    ],
    "time_coordinate": {
        "required_fields": [
            "temporal_bearer_archetype_ref", "time_role_ref", "carrier_and_serialization_ref",
            "time_scale_reference_system_and_epoch", "clock_source_authority_and_trust",
            "calendar_chronology_and_edition", "zone_identifier_rules_edition_and_resolution_policy",
            "precision_resolution_range_and_uncertainty", "instant_interval_endpoint_and_bound_semantics",
            "elapsed_duration_or_calendar_period_semantics", "subject_identity_grain_and_scope",
            "occurrence_observation_recording_processing_and_decision_relation",
            "comparison_order_causality_and_concurrency_policy", "local_time_gap_fold_leap_and_offset_policy",
            "recurrence_schedule_business_calendar_and_exception_policy", "window_lateness_watermark_trigger_and_finality_policy",
            "deadline_timeout_ttl_age_origin_renewal_and_grace", "validity_recording_bitemporal_and_as_of_policy",
            "correction_retraction_supersession_retention_and_replay_policy", "arithmetic_rounding_bucket_and_overflow_policy",
            "authority_provenance_evidence_and_invalidators", "conformance_oracles_and_negative_twins",
        ],
        "time_roles": [
            "occurrence", "observation", "validity", "recording", "transaction", "ingestion",
            "processing", "decision", "authorization", "execution_start", "effect_occurrence",
            "completion", "correction", "supersession", "retraction", "publication", "expiry",
            "schedule_intent", "deadline", "progress_frontier", "replay_virtual_time",
        ],
        "outcomes": [
            "exact", "precision_bounded", "interval_bounded", "uncertain", "ambiguous_fold",
            "nonexistent_gap", "role_unbound", "calendar_unbound", "zone_edition_unbound",
            "clock_untrusted", "causally_incomparable", "late", "expired", "out_of_range", "refused",
        ],
    },
    "dependency_axis_refs": [
        "semantic_object", "identity_and_equality", "grain_and_cardinality", "state_and_change",
        "order_and_topology", "partiality_and_uncertainty", "composition_algebra",
        "authority_and_trust", "effect_boundary", "resources_and_failure", "representation",
        "compatibility_and_evolution", "evidence_and_conformance",
    ],
    "discovery_projection_compatibility": {
        "existing_facets": ["event_time", "validity_time", "bitemporal", "interval_or_window", "schedule_or_calendar", "deadline_or_timeout", "ttl_or_expiry"],
        "status": "LOSSY_LEXICAL_DISCOVERY_PROJECTION_ONLY",
        "prohibition": "A time-looking field or lexical facet cannot select time role, clock, calendar, zone edition, precision, interval law, finality, correction, applicability, owner or exact contract.",
    },
    "non_collapse_laws": [
        "instant is not local date-time offset date-time or textual timestamp",
        "numeric offset is not a named time zone and zone rules are editioned",
        "calendar date and time-of-day do not identify an instant without a resolution context",
        "elapsed duration is not calendar period",
        "occurrence observation validity recording transaction ingestion processing decision authorization execution completion correction and publication are separate roles",
        "deadline is not occurrence time and timeout is not a civil timestamp",
        "TTL and lease expiry require an age origin clock renewal and grace policy",
        "wall-clock order is not causal order and equal clock readings do not prove simultaneity",
        "logical-clock order is not physical occurrence time",
        "event time is not processing or arrival time",
        "watermark is not proof of source completeness or business finality",
        "window close is not immutable finality when corrections or late data remain admissible",
        "bitemporality requires independently queryable validity and recording axes",
        "correction time does not erase prior recording history",
        "precision uncertainty and unknown time are not zero duration",
        "ambiguous local-time fold is not a unique instant and nonexistent local time is not an instant",
        "recurrence rule is not its finite expansion and expansion requires a bounded horizon",
        "business calendar is authority scoped and is not a universal Gregorian weekday rule",
        "snapshot/as-of cut must name its time role and consistency frontier",
        "same serialized timestamp under different calendar zone or scale editions need not denote the same temporal position",
        "retention age and domain validity are separate policies",
        "replay virtual time is not original wall-clock execution time",
    ],
    "primary_source_refs": [row["source_id"] for row in PRIMARY_SOURCES],
    "owner_decision": "UNRESOLVED",
    "member_applicability_decisions": 0,
    "canonical_gaps_closed": 0,
    "completion_claim": False,
}


KERNEL_DEFINITIONS = [
    ("parse_rfc3339_timestamp", "offset_date_time", "timestamp text and profile", "typed offset date-time or refusal", "Parsing does not bind application time role, named zone or clock trust."),
    ("format_timestamp", "offset_date_time", "typed temporal value and precision profile", "text representation", "Formatting can lose precision/zone metadata and is not semantic identity."),
    ("resolve_local_date_time", "zoned_date_time", "local date-time, zone and rule edition", "zero, one or two instant candidates", "DST gaps/folds require an explicit resolution policy."),
    ("convert_zone_preserving_instant", "zoned_date_time", "instant and target zone edition", "target local representation", "Preserving instant need not preserve local date, offset or schedule meaning."),
    ("convert_calendar", "calendar_date_or_time_of_day", "date and source/target chronology editions", "target date or refusal", "Calendar conversion is not zone resolution or instant conversion."),
    ("read_wall_clock", "instant", "clock source and trust context", "clock reading with precision/uncertainty", "Wall-clock reading can jump and does not prove elapsed duration or causality."),
    ("measure_monotonic_elapsed", "elapsed_duration", "monotonic start/end readings", "elapsed duration", "Monotonic duration is not a civil time position."),
    ("compare_instants", "instant", "two positions on compatible scales", "before/equal/after/indeterminate", "Comparison requires scale conversion, precision and uncertainty policy."),
    ("add_elapsed_duration", "elapsed_duration", "instant and elapsed amount", "instant or overflow/refusal", "Elapsed arithmetic does not apply civil-calendar rules."),
    ("add_calendar_period", "calendar_period", "civil date-time, period, calendar/zone policy", "resolved date-time candidate(s)", "Month/day arithmetic can be non-associative and zone transitions create gaps/folds."),
    ("convert_duration_units", "elapsed_duration", "duration and exact scale factor", "converted duration", "Calendar months/years cannot be converted to fixed seconds without context."),
    ("normalize_interval", "time_interval", "endpoints and bound kinds", "canonical interval or invalidity", "Empty, unbounded and uncertain intervals remain distinct."),
    ("evaluate_interval_relation", "time_interval", "two intervals", "topological temporal relation", "Interval topology is not causality, validity authority or containment ownership."),
    ("intersect_intervals", "time_interval", "interval operands", "intersection or empty", "Intersection does not reconcile different time roles or scales."),
    ("union_adjacent_intervals", "time_interval", "compatible intervals", "union or refusal", "Disjoint intervals and differing bound semantics cannot silently become one interval."),
    ("bucket_or_truncate", "window_pane_or_bucket", "instant, origin, width and rounding", "bucket identity", "Bucket identity depends on role, origin, zone/calendar and boundary policy."),
    ("assign_event_timestamp", "occurrence_time", "event and source timestamp evidence", "event-time assertion", "Source timestamp is an assertion and may be absent, corrected or untrusted."),
    ("record_observation_time", "observation_time", "observation act and clock", "observation-time assertion", "Observation time is not occurrence or validity time."),
    ("record_transaction_time", "recording_or_transaction_time", "record mutation and system clock", "recording interval/version", "System recording time is not domain validity time."),
    ("record_processing_time", "ingestion_or_processing_time", "processing step and runtime clock", "processing-time assertion", "Processing time is not arrival, occurrence or source time."),
    ("record_decision_time", "decision_time", "decision act and evidence", "decision-time assertion", "Decision time is not authorization or effect time."),
    ("record_effect_time", "execution_or_effect_time", "effect receipt and clock/source", "effect-time assertion", "Requested or acknowledged time does not necessarily prove effect occurrence."),
    ("advance_watermark", "watermark_or_progress_frontier", "input observations and progress policy", "new progress estimate", "Watermarks are monotone estimates within a model, not truth or finality."),
    ("classify_lateness", "watermark_or_progress_frontier", "event time, frontier and allowed lateness", "on-time/late/too-late", "Lateness is pipeline-policy relative and not invalidity."),
    ("fire_event_time_trigger", "window_pane_or_bucket", "window, frontier and trigger state", "pane emission", "Pane emission is not necessarily final or complete."),
    ("assign_fixed_window", "window_pane_or_bucket", "event instant, origin and width", "window membership", "Fixed windows depend on exact boundary/origin semantics."),
    ("assign_sliding_windows", "window_pane_or_bucket", "event instant, width and period", "one or more memberships", "One event may belong to multiple sliding windows."),
    ("merge_session_windows", "window_pane_or_bucket", "events and gap policy", "data-dependent sessions", "Session windows are not fixed intervals and late events can merge prior sessions."),
    ("expand_recurrence", "schedule_or_recurrence", "rule, start, zone/calendar edition and horizon", "bounded occurrence candidates", "A recurrence rule may be infinite and expansion is edition/horizon dependent."),
    ("apply_business_calendar", "business_calendar", "candidate time and authority-scoped calendar", "accepted/adjusted/refused time", "Weekends and holidays are jurisdiction, tenant and edition scoped."),
    ("compute_deadline", "deadline_or_timeout", "origin, duration/period and policy", "deadline", "Deadline arithmetic must choose elapsed versus calendar semantics."),
    ("enforce_timeout", "deadline_or_timeout", "start, elapsed clock and cancellation policy", "completed/timed-out/indeterminate", "Timeout does not prove cancellation or absence of late effects."),
    ("evaluate_ttl_expiry", "ttl_expiry_or_lease", "age origin, clock, TTL and grace", "live/expired/indeterminate", "TTL expiry differs from revocation, deletion and domain invalidity."),
    ("renew_lease", "ttl_expiry_or_lease", "lease identity, authority and renewal time", "new expiry or refusal", "Renewal races and stale holders require fencing/identity evidence."),
    ("assign_validity_interval", "validity_time", "fact/state and validity evidence", "valid-time interval", "Validity is a modeled claim, not recording or observation time."),
    ("bitemporal_insert", "bitemporal_fact_or_history", "fact, valid interval and recording event", "history segment", "Valid and recording axes must remain independently queryable."),
    ("bitemporal_correct", "bitemporal_fact_or_history", "prior history, correction and new assertion", "superseding history without erasure", "Correction must not rewrite prior recording truth by default."),
    ("query_as_of", "temporal_snapshot_or_as_of_cut", "history, named time role and cut", "as-of view", "An as-of timestamp without a role/consistency frontier is ambiguous."),
    ("temporal_join", "time_interval", "relations with time roles and overlap policy", "temporally matched rows", "Overlapping validity does not prove entity identity or causal relationship."),
    ("temporal_aggregate", "window_pane_or_bucket", "observations, time role, windows and completeness", "time-indexed aggregate", "Aggregation must preserve role, boundary, lateness and revision semantics."),
    ("compute_age_or_freshness", "observation_time", "origin, current clock and policy", "age/freshness verdict", "Freshness is role/source/policy scoped and not correctness."),
    ("logical_clock_tick", "logical_or_causal_clock", "local logical state and event", "advanced logical time", "Logical time orders events but is not physical time."),
    ("logical_clock_receive", "logical_or_causal_clock", "local and received logical values", "merged/advanced logical time", "Tie-broken total order does not create causal dependence."),
    ("vector_clock_compare", "logical_or_causal_clock", "vector timestamps", "before/after/equal/concurrent", "Concurrency is not simultaneity and vectors are membership-scope dependent."),
    ("estimate_clock_offset", "instant", "clock samples and synchronization model", "offset/error estimate", "Synchronization provides bounded estimates, not perfect clock truth."),
    ("record_correction_or_supersession", "correction_or_supersession_time", "prior assertion and correction act", "correction relation with times", "Correction occurrence and corrected fact validity are different roles."),
    ("compute_retention_cutoff", "recording_or_transaction_time", "retention policy, origin and clock", "eligible/not-eligible/indeterminate", "Retention eligibility is not erasure authority or domain invalidity."),
    ("replay_with_virtual_time", "temporal_snapshot_or_as_of_cut", "history, replay cut and virtual clock policy", "replayed execution trace", "Replay time is not original wall-clock time and effects must remain isolated."),
]


def temporal_kernel_rows() -> list[dict[str, Any]]:
    source_refs = [row["source_id"] for row in PRIMARY_SOURCES]
    return [
        {
            "record_kind": "temporal_operation_kernel",
            "kernel_id": f"kernel.time.{name}.v1",
            "temporal_bearer_archetype_ref": f"archetype.time.{archetype}.v1",
            "input_contract": input_contract,
            "output_contract": output_contract,
            "required_coordinate_fields": ONTOLOGY["time_coordinate"]["required_fields"],
            "negative_twin": negative_twin,
            "bounded_primary_source_refs": source_refs,
            "applicability": "UNRESOLVED_PER_TEMPORAL_BEARER_AND_USE_SITE",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for name, archetype, input_contract, output_contract, negative_twin in KERNEL_DEFINITIONS
    ]


def structural_time_dockets() -> list[dict[str, Any]]:
    by_family: dict[str, list[str]] = defaultdict(list)
    for row in load_jsonl(PRECLASSIFICATIONS):
        if row["axis"] == "time":
            by_family[row["family_id"]].append(row["library_ref"])
    return [
        {
            "record_kind": "time_structural_rebase_docket",
            "docket_id": f"docket.time-coordinate.{family_ref.removeprefix('constitution.family.').replace('_', '-')}.v1",
            "family_ref": family_ref,
            "library_refs": sorted(library_refs),
            "library_count": len(library_refs),
            "evidence_candidate_refs": [],
            "source_evidence_binding": "UNRESOLVED_PER_FAMILY_AND_USE_SITE",
            "authority_limit": "All-axis preclassification supplies membership only; it is not temporal evidence or applicability authority.",
        }
        for family_ref, library_refs in sorted(by_family.items())
    ]


def route_for_facets(facets: tuple[str, ...]) -> str:
    return (
        "LEXICAL_DISCOVERY_PROJECTION_ONLY_TEMPORAL_RESEARCH_REQUIRED"
        if facets
        else "NO_MEMBER_TEMPORAL_BEARER_EVIDENCE_VACANCY"
    )


def build() -> dict[str, Any]:
    dockets = structural_time_dockets()
    rebase = build_member_rebase(
        axis="time",
        dockets=dockets,
        preclassifications_path=PRECLASSIFICATIONS,
        cluster_prefix="cluster.time-coordinate-rebase",
        cluster_route=route_for_facets,
    )
    clusters = [
        {
            "record_kind": "time_member_research_cluster",
            **row,
            "required_next_evidence": [
                "authoritative per-use-site temporal bearer and time-role inventory",
                "clock scale calendar zone edition precision and uncertainty contract",
                "interval duration recurrence window deadline TTL and progress semantics",
                "validity recording correction retention replay and finality policy",
                "authority evidence counterexamples and conformance oracles",
            ],
            "family_source_evidence_binding": "UNRESOLVED",
            "member_applicability": "UNRESOLVED",
            "owner_decision": "UNRESOLVED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for row in rebase["clusters"]
    ]
    members = [
        {
            "record_kind": "time_member_research_route",
            "route_id": f"route.time-coordinate.{row['library_ref'].removeprefix('library.').replace('.', '-').replace('_', '-')}",
            **row,
            "flat_projection_effect": "DISCOVERY_ROUTING_ONLY_NOT_APPLICABILITY",
            "required_temporal_bearer_and_time_role_inventory": "NOT_YET_SUPPLIED",
            "required_time_coordinate_profiles": "NOT_YET_SUPPLIED",
            "required_progress_finality_correction_and_replay_contracts": "NOT_YET_SUPPLIED",
            "required_authority_evidence_and_conformance_contracts": "NOT_YET_SUPPLIED",
            "family_source_evidence_binding": "UNRESOLVED",
            "member_applicability": "UNRESOLVED",
            "owner_decision": "UNRESOLVED",
            "canonical_gaps_closed": 0,
            "status": "LOSSLESSLY_ROUTED_RESEARCH_OPEN",
            "completion_claim": False,
        }
        for row in rebase["members"]
    ]
    extensions = [
        {
            "record_kind": "time_exact_contract_extension_candidate",
            "extension_id": f"extension.time-coordinate.{family_ref.removeprefix('constitution.family.').replace('_', '-')}.v1",
            "family_ref": family_ref,
            "structural_rebase_docket_ref": docket["docket_id"],
            "represented_library_refs": docket["library_refs"],
            "represented_library_count": docket["library_count"],
            "required_record_kinds": [
                "temporal_bearer_inventory", "time_role_coordinate", "clock_calendar_zone_profile",
                "interval_duration_recurrence_contract", "progress_finality_contract",
                "bitemporal_correction_replay_contract", "time_conformance_oracle",
            ],
            "source_evidence_binding": "UNRESOLVED",
            "owner_decision": "UNRESOLVED",
            "member_applicability_decisions": 0,
            "canonical_gaps_closed": 0,
            "status": "CANDIDATE_UNRATIFIED",
            "completion_claim": False,
        }
        for family_ref, docket in sorted(rebase["docket_by_family"].items())
    ]
    kernels = temporal_kernel_rows()
    summary = {
        "program_id": "program.time-coordinate-ontology-and-rebase.v1",
        "as_of": AS_OF,
        "axis": "time",
        "primary_sources": len(PRIMARY_SOURCES),
        "temporal_bearer_archetypes": len(TEMPORAL_BEARER_ARCHETYPES),
        "temporal_operation_kernels": len(kernels),
        "structural_family_dockets": len(dockets),
        "family_extension_candidates": len(extensions),
        "research_clusters": len(clusters),
        "target_member_routes": len(members),
        "routes_with_lexical_discovery_projection": rebase["lexical_member_count"],
        "routes_with_no_member_temporal_bearer_evidence": rebase["vacancy_member_count"],
        "temporal_bearer_inventories_supplied": 0,
        "time_coordinate_profiles_supplied": 0,
        "family_source_evidence_bindings_supplied": 0,
        "member_applicability_decisions": 0,
        "owner_decisions": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {
        "ontology": ONTOLOGY,
        "sources": PRIMARY_SOURCES,
        "archetypes": temporal_bearer_rows(),
        "kernels": kernels,
        "dockets": dockets,
        "clusters": clusters,
        "members": members,
        "extensions": extensions,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "time-coordinate-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "temporal-bearer-archetypes.jsonl": "".join(canonical(row) + "\n" for row in built["archetypes"]),
        "temporal-operation-kernels.jsonl": "".join(canonical(row) + "\n" for row in built["kernels"]),
        "structural-family-dockets.jsonl": "".join(canonical(row) + "\n" for row in built["dockets"]),
        "member-research-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "member-time-routes.jsonl": "".join(canonical(row) + "\n" for row in built["members"]),
        "extension-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["extensions"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.time-coordinate-ontology-and-rebase.v1",
            "as_of": AS_OF,
            "files": claims,
            "completion_claim": False,
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(
        "BUILD PASS time coordinate ontology: "
        f"{summary['temporal_bearer_archetypes']} bearers, {summary['temporal_operation_kernels']} kernels, "
        f"{summary['research_clusters']} clusters and {summary['target_member_routes']} exact routes; "
        "evidence bindings, decisions and closures remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
